from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"
CANON_SHA = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"
TMP = Path("/tmp/pb4_pft_coverage")
RUN_LOG = Path("/tmp/pb4_pft_coverage_21ka.log")
OUTDST = BASE / "results" / "pft_coverage_audit_20261005"


def sh(args, cwd=None, env=None, stdout=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True, stdout=stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct() -> Path:
    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    z = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got = sha256(z)
    if got != CANON_SHA:
        raise SystemExit(f"canonical SHA mismatch: {got} != {CANON_SHA}")
    return z


def patch_runner(z: Path) -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        zz.extractall(TMP)
    root = TMP / ROOT_NAME
    runner = root / "pb4studio" / "runner.py"
    s = runner.read_text(encoding="utf-8")

    anchor = """        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })
"""
    if anchor not in s:
        raise SystemExit("runner summary-row anchor not found")

    add = anchor + """        # 2026-10-05 PFT-coverage audit only. These diagnostics do not
        # feed vegetation, EEMT, AGB, validation, or geomorphology.
        _optpft_audit = np.asarray(
            veg.get("optpft_node", np.full(igrid.shape, np.nan)), dtype="float64"
        )
        _full_biome_audit = np.asarray(
            veg.get("biome4_full_id_node", np.full(igrid.shape, np.nan)), dtype="float64"
        )
        _opt_valid = igrid.land & np.isfinite(_optpft_audit)
        _biome_valid = igrid.land & np.isfinite(_full_biome_audit)
        _opt_round = np.rint(_optpft_audit).astype("int16")
        _biome_round = np.rint(_full_biome_audit).astype("int16")
        for _p in range(0, 15):
            _pmask = _opt_valid & (_opt_round == _p)
            _n = int(np.count_nonzero(_pmask))
            row[f"audit_optpft_{_p:02d}_count"] = _n
            if _n:
                _nv = np.asarray(npp, dtype="float64")[_pmask]
                _nv = _nv[np.isfinite(_nv)]
                row[f"audit_optpft_{_p:02d}_npp_sum_gC_m2_yr"] = float(np.sum(_nv)) if _nv.size else 0.0
                row[f"audit_optpft_{_p:02d}_npp_mean_gC_m2_yr"] = float(np.mean(_nv)) if _nv.size else float("nan")
            else:
                row[f"audit_optpft_{_p:02d}_npp_sum_gC_m2_yr"] = 0.0
                row[f"audit_optpft_{_p:02d}_npp_mean_gC_m2_yr"] = float("nan")
        for _b in range(1, 29):
            row[f"audit_biome_{_b:02d}_count"] = int(
                np.count_nonzero(_biome_valid & (_biome_round == _b))
            )
"""
    runner.write_text(s.replace(anchor, add, 1), encoding="utf-8")
    return root


def run_full(root: Path) -> Path:
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "4")
    with RUN_LOG.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        rc = p.wait()
        if rc != 0:
            raise SystemExit(f"full 21 ka coverage audit failed: exit {rc}")
    return root / "outputs_CHELSA21K"


def find_summary(out: Path, mode: str) -> tuple[Path, pd.DataFrame]:
    found = []
    for p in (out / f"model_{mode}").rglob("*.csv"):
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
        except Exception:
            continue
        if "audit_optpft_04_count" in df.columns:
            found.append((p, df))
    if not found:
        raise SystemExit(f"no PFT-audit summary CSV found for {mode}")
    p, df = max(found, key=lambda x: len(x[1]))
    if len(df) != 211:
        raise SystemExit(f"expected 211 rows for {mode}; found {len(df)} in {p}")
    return p, df


def age_column(df: pd.DataFrame) -> str | None:
    for c in ("ka_bp", "model_ka_bp", "time_ka_bp", "time_ka", "age_ka", "age_ka_bp"):
        if c in df.columns:
            return c
    return None


def summarize(out: Path):
    OUTDST.mkdir(parents=True, exist_ok=True)
    full_frames = []
    pft_rows = []
    biome_rows = []

    for mode in ("static", "dynamic"):
        p, df = find_summary(out, mode)
        age_col = age_column(df)

        # Preserve the full 211-step canonical summary, including geomorphic
        # state, NPP and EEMT, so later AGB candidates can be compared against
        # the exact canonical trajectory without another hidden reference run.
        sub = df.copy()
        sub.insert(0, "mode", mode)
        sub.insert(1, "source_csv", str(p.relative_to(out)))
        full_frames.append(sub)

        for pft in range(0, 15):
            c_count = f"audit_optpft_{pft:02d}_count"
            c_sum = f"audit_optpft_{pft:02d}_npp_sum_gC_m2_yr"
            counts = pd.to_numeric(df[c_count], errors="coerce").fillna(0.0)
            sums = pd.to_numeric(df[c_sum], errors="coerce").fillna(0.0)
            present = counts > 0
            total_n = int(round(float(counts.sum())))
            total_npp = float(sums.sum())
            ages = []
            if age_col and present.any():
                ages = pd.to_numeric(df.loc[present, age_col], errors="coerce").dropna().tolist()
            pft_rows.append({
                "mode": mode,
                "pft": pft,
                "timesteps_present": int(present.sum()),
                "total_cell_observations": total_n,
                "max_cells_in_timestep": int(round(float(counts.max()))),
                "mean_cells_all_211_steps": float(counts.mean()),
                "cell_weighted_mean_npp_gC_m2_yr": (total_npp / total_n) if total_n else np.nan,
                "oldest_age_ka_present": max(ages) if ages else np.nan,
                "youngest_age_ka_present": min(ages) if ages else np.nan,
                "xue_forest_bridge_supported": pft in {4, 5, 6, 7},
            })

        for biome in range(1, 29):
            c = f"audit_biome_{biome:02d}_count"
            counts = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
            present = counts > 0
            biome_rows.append({
                "mode": mode,
                "biome": biome,
                "timesteps_present": int(present.sum()),
                "total_cell_observations": int(round(float(counts.sum()))),
                "max_cells_in_timestep": int(round(float(counts.max()))),
            })

    ts = pd.concat(full_frames, ignore_index=True)
    pfts = pd.DataFrame(pft_rows)
    biomes = pd.DataFrame(biome_rows)

    ts.to_csv(OUTDST / "PFT_COVERAGE_21KA_TIMESERIES.csv", index=False, encoding="utf-8-sig")
    pfts.to_csv(OUTDST / "PFT_COVERAGE_21KA_SUMMARY.csv", index=False, encoding="utf-8-sig")
    biomes.to_csv(OUTDST / "BIOME_COVERAGE_21KA_SUMMARY.csv", index=False, encoding="utf-8-sig")

    unsupported = pfts[
        (pfts["total_cell_observations"] > 0)
        & (~pfts["xue_forest_bridge_supported"])
        & (pfts["pft"] != 0)
    ].copy()
    unsupported.to_csv(OUTDST / "UNSUPPORTED_PFT_OCCURRENCES.csv", index=False, encoding="utf-8-sig")

    provenance = {
        "execution_status": "new_full_21ka_pft_coverage_audit",
        "canonical_model": "PB4-McKenzie-nativeClimate",
        "canonical_sha256": CANON_SHA,
        "climate": "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp": "21.0-0.0",
        "interval_kyr": 0.1,
        "n_timesteps_per_mode": 211,
        "modes": ["static", "dynamic"],
        "scientific_model_changes": "none; runner patched only to record optpft/biome diagnostics",
        "primary_question": "Are all selected PFTs covered by the Xue/IBIS forest bridge for BIOME4 PFT4-7?",
        "supported_forest_pfts": [4, 5, 6, 7],
    }
    (OUTDST / "PFT_COVERAGE_PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    shutil.copy2(RUN_LOG, OUTDST / "PFT_COVERAGE_21KA_RUN.log")

    used = pfts[pfts["total_cell_observations"] > 0].copy()
    md = """# PB4-McKenzie-nativeClimate 21-0 ka PFT coverage audit

## 실행 지위

- 새 전체 실행: yes
- 모델: PB4-McKenzie-nativeClimate
- canonical SHA-256: {sha}
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- steps: static 211 + dynamic 211
- scientific model change: none
- audit-only change: optpft_node and full BIOME4 biome counts written into per-step summaries

## 실제 사용 PFT

{used}

## Xue forest bridge 밖의 실제 PFT

{unsupported}

## 판정 원칙

- PFT4-7만 사용되면 현재 Xue/IBIS forest NPP+PFT -> AGB candidate를 바로 전체 실행할 수 있다.
- PFT1-3 또는 PFT8-14가 실제로 선택되면 임의 대응하지 않고 해당 PFT의 문헌 경로를 먼저 확정한다.
- PFT0은 비식생/무효 상태로 AGB=0 처리 가능한 별도 상태이며 unsupported vegetation PFT로 세지 않는다.
""".format(
        sha=CANON_SHA,
        used=used.to_markdown(index=False),
        unsupported=(unsupported.to_markdown(index=False) if len(unsupported) else "없음"),
    )
    (OUTDST / "PFT_COVERAGE_AUDIT_KO.md").write_text(md, encoding="utf-8")

    print("=== USED PFTS ===")
    print(used.to_string(index=False))
    print("=== UNSUPPORTED PFTS ===")
    print(unsupported.to_string(index=False) if len(unsupported) else "none")


def main():
    z = reconstruct()
    root = patch_runner(z)
    out = run_full(root)
    summarize(out)


if __name__ == "__main__":
    main()
