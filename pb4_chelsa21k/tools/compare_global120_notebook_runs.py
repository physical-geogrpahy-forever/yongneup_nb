from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio


def load_run(runs_root: Path, label: str):
    root = runs_root / label / "yongneup_biome4_teaching"
    exp = root / "teaching_experiments_global120"
    metadata_path = exp / "github_run_metadata.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return root, exp, metadata


def scenario_summary(exp: Path, scenario: str) -> pd.DataFrame:
    path = exp / scenario / "output" / "model_dynamic" / "summary_timeseries.csv"
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    if "ka_bp" not in frame:
        raise ValueError(f"Missing ka_bp in {path}")
    frame["ka_bp"] = pd.to_numeric(frame["ka_bp"], errors="raise").astype(float)
    return frame.sort_values("ka_bp", ascending=False).reset_index(drop=True)


def metric_row(label, scenario, variable, basis, a, b):
    av = np.asarray(a, dtype=np.float64)
    bv = np.asarray(b, dtype=np.float64)
    valid = np.isfinite(av) & np.isfinite(bv)
    av = av[valid]
    bv = bv[valid]
    if not av.size:
        return {
            "run_comparison": label, "scenario": scenario, "variable": variable,
            "basis": basis, "n": 0, "mae": np.nan, "rmse": np.nan,
            "bias_second_minus_first": np.nan, "max_abs_difference": np.nan,
            "correlation": np.nan, "exact_agreement_pct": np.nan,
        }
    d = bv - av
    corr = np.nan
    if av.size > 1 and np.std(av) > 0 and np.std(bv) > 0:
        corr = float(np.corrcoef(av, bv)[0, 1])
    return {
        "run_comparison": label,
        "scenario": scenario,
        "variable": variable,
        "basis": basis,
        "n": int(av.size),
        "mae": float(np.mean(np.abs(d))),
        "rmse": float(np.sqrt(np.mean(d * d))),
        "bias_second_minus_first": float(np.mean(d)),
        "max_abs_difference": float(np.max(np.abs(d))),
        "correlation": corr,
        "exact_agreement_pct": float(100.0 * np.mean(np.isclose(av, bv, rtol=0.0, atol=1e-9))),
    }


def align_integer_ages(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rounded = np.rint(out["ka_bp"].to_numpy(dtype=float))
    keep = np.isclose(out["ka_bp"].to_numpy(dtype=float), rounded, atol=1e-7, rtol=0)
    out = out.loc[keep].copy()
    out["ka_bp"] = rounded[keep].astype(float)
    return out


def aggregate_0p1_interval_metrics(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.loc[df["ka_bp"] > 1e-9].copy()
    out["interval_start_ka"] = np.floor(out["ka_bp"].to_numpy(dtype=float) + 1e-7).astype(int)
    rows = []
    for age, group in out.groupby("interval_start_ka"):
        row = {"ka_bp": float(age)}
        for col in columns:
            if col not in group:
                continue
            if (
                "volume_m3_to_next" in col
                or "mean_depth_mm_to_next" in col
                or "substeps_to_next" in col
                or "trials_to_next" in col
                or "events_to_next" in col
            ):
                row[col] = float(pd.to_numeric(group[col], errors="coerce").sum(min_count=1))
            elif "min_dt_kyr" in col:
                row[col] = float(pd.to_numeric(group[col], errors="coerce").min())
            elif "max_dt_kyr" in col or "max_accepted" in col or "max_trial" in col:
                row[col] = float(pd.to_numeric(group[col], errors="coerce").max())
            else:
                row[col] = float(pd.to_numeric(group[col], errors="coerce").mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("ka_bp", ascending=False).reset_index(drop=True)


def compare_timeseries(df1: pd.DataFrame, df01: pd.DataFrame, scenario: str):
    state1 = align_integer_ages(df1)
    state01 = align_integer_ages(df01)
    merged = state1.merge(state01, on="ka_bp", suffixes=("_1kyr", "_0p1kyr"), validate="one_to_one")
    if len(merged) != 121:
        raise RuntimeError(f"{scenario}: expected 121 common integer ages, found {len(merged)}")

    rows = []
    geomorph_cols = [
        c for c in df1.columns
        if c.startswith("geomorph_") and c in df01.columns and c.endswith("_to_next")
    ]
    for col in sorted(set(df1.columns) & set(df01.columns)):
        if col == "ka_bp" or col.startswith("geomorph_"):
            continue
        if not pd.api.types.is_numeric_dtype(df1[col]) or not pd.api.types.is_numeric_dtype(df01[col]):
            continue
        a = merged[f"{col}_1kyr"].to_numpy(dtype=float)
        b = merged[f"{col}_0p1kyr"].to_numpy(dtype=float)
        rows.append(metric_row("1kyr_vs_0.1kyr", scenario, col, "integer-ka states", a, b))

    if geomorph_cols:
        proc1 = df1[["ka_bp"] + geomorph_cols].copy()
        proc1 = proc1.loc[proc1["ka_bp"] > 1e-9].copy()
        proc1["ka_bp"] = np.rint(proc1["ka_bp"]).astype(float)
        proc01 = aggregate_0p1_interval_metrics(df01, geomorph_cols)
        pmerge = proc1.merge(proc01, on="ka_bp", suffixes=("_1kyr", "_0p1kyr"), validate="one_to_one")
        for col in geomorph_cols:
            left = col + "_1kyr"
            right = col + "_0p1kyr"
            if left not in pmerge or right not in pmerge:
                continue
            rows.append(metric_row(
                "1kyr_vs_0.1kyr", scenario, col,
                "aggregated over matched 1-kyr intervals",
                pmerge[left].to_numpy(dtype=float),
                pmerge[right].to_numpy(dtype=float),
            ))
    return rows, merged, geomorph_cols


def snapshot_directories(model_dir: Path) -> dict[float, Path]:
    result = {}
    for path in model_dir.glob("snapshot_*ka"):
        m = re.match(r"^snapshot_([+-]?(?:\d+(?:\.\d*)?|\.\d+))ka$", path.name)
        if m:
            result[round(float(m.group(1)), 8)] = path
    return result


def read_tif(path: Path):
    with rasterio.open(path) as ds:
        arr = ds.read(1, masked=True)
        profile = ds.profile.copy()
        transform = ds.transform
        crs = ds.crs
    return arr, profile, transform, crs


def compare_rasters(root1: Path, root01: Path, scenario: str, out_dir: Path):
    model1 = root1 / scenario / "output" / "model_dynamic"
    model01 = root01 / scenario / "output" / "model_dynamic"
    snaps1 = snapshot_directories(model1)
    snaps01 = snapshot_directories(model01)
    common_ages = sorted(set(snaps1) & set(snaps01), reverse=True)
    if len(common_ages) != 25:
        raise RuntimeError(f"{scenario}: expected 25 common 5-kyr snapshots, found {len(common_ages)}")

    rows = []
    map_vars = ("elevation_m", "soil_depth_m", "npp", "eemt", "biome4_full_id")
    map_deltas = {name: [] for name in map_vars}
    for age in common_ages:
        d1 = snaps1[age]
        d01 = snaps01[age]
        common_files = sorted(
            set(p.name for p in d1.glob("*.tif")) &
            set(p.name for p in d01.glob("*.tif"))
        )
        for filename in common_files:
            name = filename[:-4]
            a, p1, t1, c1 = read_tif(d1 / filename)
            b, p01, t01, c01 = read_tif(d01 / filename)
            if a.shape != b.shape or t1 != t01 or c1 != c01:
                rows.append({
                    "scenario": scenario, "age_ka": age, "variable": name,
                    "status": "grid_mismatch", "n": 0,
                })
                continue
            av = np.asarray(a.filled(np.nan), dtype=np.float64)
            bv = np.asarray(b.filled(np.nan), dtype=np.float64)
            valid = np.isfinite(av) & np.isfinite(bv)
            if not np.any(valid):
                continue
            aa, bb = av[valid], bv[valid]
            categorical = (
                name in {"biome4_full_id", "vegetation_code", "soil_texture_class",
                         "bare_bedrock", "valley_mask", "hillslope_mask"}
                or name.endswith("_mask")
            )
            if categorical:
                agree = float(100.0 * np.mean(np.isclose(aa, bb, rtol=0.0, atol=1e-9)))
                rows.append({
                    "scenario": scenario, "age_ka": age, "variable": name,
                    "status": "categorical", "n": int(valid.sum()),
                    "agreement_pct": agree,
                    "mismatch_cells": int(np.count_nonzero(~np.isclose(aa, bb, rtol=0.0, atol=1e-9))),
                })
            else:
                delta = bv - av
                d = delta[valid]
                rows.append({
                    "scenario": scenario, "age_ka": age, "variable": name,
                    "status": "continuous", "n": int(valid.sum()),
                    "mae": float(np.mean(np.abs(d))),
                    "rmse": float(np.sqrt(np.mean(d * d))),
                    "bias_0p1_minus_1kyr": float(np.mean(d)),
                    "max_abs_difference": float(np.max(np.abs(d))),
                })
            if name in map_deltas:
                delta_map = (
                    np.where(valid, (av != bv).astype(float), np.nan)
                    if categorical else np.where(valid, bv - av, np.nan)
                )
                map_deltas[name].append((age, delta_map, p1))

    out_dir.mkdir(parents=True, exist_ok=True)
    for variable, entries in map_deltas.items():
        if len(entries) != 25:
            continue
        fig, axes = plt.subplots(5, 5, figsize=(15, 14), constrained_layout=True)
        arrays = [item[1] for item in entries]
        finite = np.concatenate([x[np.isfinite(x)] for x in arrays if np.isfinite(x).any()])
        if not finite.size:
            plt.close(fig)
            continue
        if variable == "biome4_full_id":
            vmin, vmax, cmap = 0.0, 1.0, "magma"
            label = "BIOME4 mismatch (1 = different)"
        else:
            vmax = float(np.nanpercentile(np.abs(finite), 98))
            if not np.isfinite(vmax) or vmax <= 0:
                vmax = 1e-9
            vmin, vmax, cmap = -vmax, vmax, "coolwarm"
            label = f"{variable}: 0.1-kyr minus 1-kyr"
        im = None
        for ax, (age, delta, _profile) in zip(axes.ravel(), entries):
            im = ax.imshow(delta, origin="upper", cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_title(f"{age:g} ka", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
        fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.78, label=label)
        fig.suptitle(f"{scenario}: {label}", fontsize=12)
        fig.savefig(out_dir / f"{scenario}_{variable}_difference_5k.png", dpi=160)
        plt.close(fig)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    runs_root = Path(args.runs_root).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    root1, exp1, meta1 = load_run(runs_root, "1kyr")
    root01, exp01, meta01 = load_run(runs_root, "0.1kyr")

    if meta1["model_zip_sha256"] != meta01["model_zip_sha256"]:
        raise RuntimeError("The two runs used different PB4Studio ZIP files.")
    if meta1["climate_lzma_sha256"] != meta01["climate_lzma_sha256"]:
        raise RuntimeError("The two runs used different Beyer climate archives.")
    if meta1["scenarios"] != meta01["scenarios"]:
        raise RuntimeError("Scenario settings differ between the two notebook runs.")
    if meta1["virtual_basin"] != meta01["virtual_basin"]:
        raise RuntimeError("The two notebooks generated different virtual basins.")
    if float(meta1["interval_kyr"]) != 1.0 or float(meta01["interval_kyr"]) != 0.1:
        raise RuntimeError("Notebook timestep metadata does not match the intended comparison.")

    scenarios = [x["name"] for x in meta1["scenarios"]]
    ts_rows, process_rows, raster_rows, duplicate_rows = [], [], [], []
    for scenario in scenarios:
        df1 = scenario_summary(exp1, scenario)
        df01 = scenario_summary(exp01, scenario)
        rows, aligned, geomorph_cols = compare_timeseries(df1, df01, scenario)
        ts_rows.extend(rows)

        if geomorph_cols:
            proc1 = df1.loc[df1["ka_bp"] > 1e-9, ["ka_bp"] + geomorph_cols].copy()
            proc1["ka_bp"] = np.rint(proc1["ka_bp"]).astype(float)
            proc01 = aggregate_0p1_interval_metrics(df01, geomorph_cols)
            pmerge = proc1.merge(proc01, on="ka_bp", suffixes=("_1kyr", "_0p1kyr"), validate="one_to_one")
            for col in geomorph_cols:
                left, right = col + "_1kyr", col + "_0p1kyr"
                if left in pmerge and right in pmerge:
                    process_rows.append({
                        "scenario": scenario,
                        "variable": col,
                        "one_kyr_interval_count": int(len(pmerge)),
                        "one_kyr_total": float(pd.to_numeric(pmerge[left], errors="coerce").sum()),
                        "ten_0p1_kyr_steps_aggregated_total": float(pd.to_numeric(pmerge[right], errors="coerce").sum()),
                        "mean_1kyr_interval": float(pd.to_numeric(pmerge[left], errors="coerce").mean()),
                        "mean_aggregated_0p1kyr_interval": float(pd.to_numeric(pmerge[right], errors="coerce").mean()),
                    })

        raster_rows.extend(compare_rasters(root1, root01, scenario, out_dir / "spatial_difference_maps"))

    # The two scenario controls were intentionally configured identically.
    for label, exp in (("1kyr", exp1), ("0.1kyr", exp01)):
        base = scenario_summary(exp, "baseline")
        second = scenario_summary(exp, "scenario2")
        for col in sorted(set(base.columns) & set(second.columns)):
            if col == "ka_bp" or not pd.api.types.is_numeric_dtype(base[col]) or not pd.api.types.is_numeric_dtype(second[col]):
                continue
            if len(base) == len(second):
                duplicate_rows.append(metric_row(
                    f"within_{label}_duplicate_scenarios",
                    "baseline_vs_scenario2", col, "same notebook",
                    base[col].to_numpy(dtype=float),
                    second[col].to_numpy(dtype=float),
                ))

    pd.DataFrame(ts_rows).to_csv(out_dir / "timeseries_comparison.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(process_rows).to_csv(out_dir / "geomorphic_process_budget_comparison.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(raster_rows).to_csv(out_dir / "spatial_raster_comparison_5k.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(duplicate_rows).to_csv(out_dir / "duplicate_scenario_check.csv", index=False, encoding="utf-8-sig")

    runtime_rows = []
    for label, metadata in (("1kyr", meta1), ("0.1kyr", meta01)):
        for row in metadata["scenario_runtime"]:
            runtime_rows.append({
                "notebook": label,
                "interval_kyr": metadata["interval_kyr"],
                "scenario": row["scenario"],
                "model": row["model"],
                "elapsed_seconds": row["elapsed_s"],
                "elapsed_minutes": row["elapsed_s"] / 60.0,
            })
    pd.DataFrame(runtime_rows).to_csv(out_dir / "runtime_comparison.csv", index=False, encoding="utf-8-sig")

    report = f"""# Global 120-ka notebook comparison

- 1-kyr notebook: ECO_GEOGRAPHY_LAB4_GLOBAL_120KA_FIXED_20261106.ipynb
- 0.1-kyr notebook: ECO_GEOGRAPHY_LAB4_GLOBAL_120KA_FIXED_20261106_0.1kyr.ipynb
- Model archive SHA-256: {meta1['model_zip_sha256']}
- Beyer climate archive SHA-256: {meta1['climate_lzma_sha256']}
- Original BIOME4 Fortran SHA-256: {meta1['original_biome4_fortran_sha256']}
- Period: 120–0 ka BP
- Coupling intervals: 1.0 kyr and 0.1 kyr
- Scenarios: two identical dynamic Dwa / KR_SEOUL scenarios
- Uplift: 0.08 m/kyr
- Common virtual basin: {meta1['virtual_basin']['actual_basin_area_km2']:.6f} km², {meta1['virtual_basin']['cell_size_m']:.1f} m grid
- Initial soil depth: {meta1['virtual_basin']['base_soil_depth_m']:.2f} m

The time-series comparison aligns model states at integer ka ages. Geomorphic interval diagnostics are compared after aggregating the ten 0.1-kyr intervals into each matching 1-kyr interval. Spatial rasters are compared at all common 5-kyr snapshots. The process-budget diagnostics sum accepted-substep hillslope and fluvial fluxes and do not alter the model state equations.
"""
    (out_dir / "README_comparison.md").write_text(report, encoding="utf-8")

    zip_path = out_dir / "global120_notebook_comparison.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob("*")):
            if path.is_file() and path != zip_path:
                archive.write(path, path.relative_to(out_dir))
    print("Comparison outputs:", out_dir)
    print("Comparison ZIP:", zip_path)


if __name__ == "__main__":
    main()
