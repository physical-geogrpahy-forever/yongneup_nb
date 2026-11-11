#!/usr/bin/env python3
"""Build BIOME4 and selected-PFT area-ratio comparisons from two existing run artifacts."""
from pathlib import Path
import argparse
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def locate(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one {filename} under {root}; found {len(matches)}")
    return matches[0]


def read_ratio(root: Path, filename: str) -> pd.DataFrame:
    df = pd.read_csv(locate(root, filename))
    return df[(df["scenario"] == "baseline") & (df["model"] == "동적")].copy()


def integer_age_rows(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    rounded = np.rint(d["ka_bp"].to_numpy()).astype(int)
    keep = np.isclose(d["ka_bp"].to_numpy(), rounded, atol=1e-8)
    d = d.loc[keep].copy()
    d["ka_bp"] = rounded[keep]
    return d


def pivot_ratio(df, code_col, value_col, codes, ages):
    p = df.pivot_table(index="ka_bp", columns=code_col, values=value_col,
                       aggfunc="sum", fill_value=0)
    return p.reindex(index=ages, columns=codes, fill_value=0)


def assert_scenarios_identical(root: Path, filename: str, code_col: str, value_col: str):
    df = pd.read_csv(locate(root, filename))
    a = df[df["scenario"] == "baseline"].sort_values(["ka_bp", code_col])[value_col].to_numpy()
    b = df[df["scenario"] == "scenario2"].sort_values(["ka_bp", code_col])[value_col].to_numpy()
    if not np.array_equal(a, b):
        raise AssertionError(f"baseline and scenario2 differ in {filename}")


def save_stacked(data_1, data_01, ages, labels, title, outdir, stem, ncol):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8.3), sharex=True)
    handles = None
    panels = [
        (data_1, "1 kyr 시간간격"),
        (data_01, "0.1 kyr 시간간격 — 정수 ka 시점만 추출")
    ]
    for ax, (data, panel_title) in zip(axes, panels):
        values = [data.iloc[:, i].to_numpy() for i in range(data.shape[1])]
        h = ax.stackplot(ages, *values, labels=labels, alpha=0.9)
        if handles is None:
            handles = h
        ax.set_xlim(120, 0)
        ax.set_ylim(0, 100)
        ax.set_yticks(np.arange(0, 101, 20))
        ax.set_ylabel("면적 비율 (%)")
        ax.set_title(panel_title, loc="left")
        ax.grid(axis="y", alpha=0.25)
    axes[-1].set_xticks(np.arange(120, -1, -20))
    axes[-1].set_xlabel("시기 (ka BP)")
    fig.suptitle(
        title + "\n공통 정수 ka 시점 121개 · baseline (scenario2와 비율 시계열 완전 일치)",
        y=0.99, fontsize=14
    )
    fig.legend(handles, labels, loc="lower center", ncol=ncol,
               bbox_to_anchor=(0.5, 0.005), frameon=False)
    fig.tight_layout(rect=[0.02, 0.10, 0.98, 0.94])
    fig.savefig(outdir / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--one-kyr-dir", type=Path, required=True)
    parser.add_argument("--sub-kyr-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = ["Noto Sans", "Noto Sans CJK JP"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 8.5
    plt.rcParams["svg.fonttype"] = "none"

    biome_1 = read_ratio(args.one_kyr_dir, "biome4_biome_ratio_all_times.csv")
    biome_01 = read_ratio(args.sub_kyr_dir, "biome4_biome_ratio_all_times.csv")
    pft_1 = read_ratio(args.one_kyr_dir, "selected_pft_grid_ratio_all_times.csv")
    pft_01 = read_ratio(args.sub_kyr_dir, "selected_pft_grid_ratio_all_times.csv")

    for root, fname, code, value in [
        (args.one_kyr_dir, "biome4_biome_ratio_all_times.csv", "biome_id", "area_percent"),
        (args.one_kyr_dir, "selected_pft_grid_ratio_all_times.csv", "pft_id", "chosen_cells_percent"),
        (args.sub_kyr_dir, "biome4_biome_ratio_all_times.csv", "biome_id", "area_percent"),
        (args.sub_kyr_dir, "selected_pft_grid_ratio_all_times.csv", "pft_id", "chosen_cells_percent")
    ]:
        assert_scenarios_identical(root, fname, code, value)

    ages = np.arange(120, -1, -1, dtype=int)
    biome_01_i = integer_age_rows(biome_01)
    pft_01_i = integer_age_rows(pft_01)
    if not all(x["ka_bp"].nunique() == 121 for x in [biome_1, biome_01_i, pft_1, pft_01_i]):
        raise AssertionError("The comparison does not contain 121 common integer-ka ages")

    biome_codes = sorted(set(biome_1["biome_id"].astype(int)) |
                         set(biome_01_i["biome_id"].astype(int)))
    B1 = pivot_ratio(biome_1, "biome_id", "area_percent", biome_codes, ages)
    B01 = pivot_ratio(biome_01_i, "biome_id", "area_percent", biome_codes, ages)
    B1["미분류/미기록"] = (100.0 - B1.sum(axis=1)).clip(lower=0)
    B01["미분류/미기록"] = (100.0 - B01.sum(axis=1)).clip(lower=0)

    pft_codes = sorted(set(pft_1["pft_id"].astype(int)) |
                       set(pft_01_i["pft_id"].astype(int)))
    P1 = pivot_ratio(pft_1, "pft_id", "chosen_cells_percent", pft_codes, ages)
    P01 = pivot_ratio(pft_01_i, "pft_id", "chosen_cells_percent", pft_codes, ages)

    biome_names = (biome_1[["biome_id", "biome_name_ko"]]
                   .drop_duplicates().set_index("biome_id")["biome_name_ko"].to_dict())
    biome_plot_codes = [c for c in biome_codes if max(B1[c].max(), B01[c].max()) > 0]
    biome_cols = biome_plot_codes + ["미분류/미기록"]
    biome_labels = [f"{c}. {biome_names[c]}" for c in biome_plot_codes] + ["미분류/미기록"]
    B1_plot, B01_plot = B1[biome_cols], B01[biome_cols]

    pft_names = (pft_1[["pft_id", "pft_name"]]
                 .drop_duplicates().set_index("pft_id")["pft_name"].to_dict())
    pft_plot_codes = [c for c in pft_codes if max(P1[c].max(), P01[c].max()) > 0]
    pft_labels = []
    for c in pft_plot_codes:
        if c == 14:
            pft_labels.append("PFT 14. 목본·초본 공우점 판정 (별도 PFT 아님)")
        elif c == 0:
            pft_labels.append("PFT 0. 미선택")
        else:
            pft_labels.append(f"PFT {c}. {pft_names[c]}")
    P1_plot, P01_plot = P1[pft_plot_codes], P01[pft_plot_codes]

    save_stacked(
        B1_plot, B01_plot, ages, biome_labels,
        "BIOME4 생물군계별 면적 비율 — 시간간격 비교",
        outdir, "biome4_area_ratio_timestep_comparison", 3
    )
    save_stacked(
        P1_plot, P01_plot, ages, pft_labels,
        "선택 PFT별 격자 면적 비율 — 시간간격 비교",
        outdir, "selected_pft_area_ratio_timestep_comparison", 2
    )

    Bdiff = B1[biome_cols] - B01[biome_cols]
    Pdiff = P1[pft_plot_codes] - P01[pft_plot_codes]
    biome_l1 = Bdiff.abs().sum(axis=1)
    pft_l1 = Pdiff.abs().sum(axis=1)

    fig, axes = plt.subplots(3, 1, figsize=(14, 11.5), sharex=True)
    for col, label in zip(biome_cols, biome_labels):
        axes[0].plot(ages, Bdiff[col].to_numpy(), label=label, linewidth=1.35)
    axes[0].axhline(0, linewidth=0.8)
    axes[0].set_ylim(-1.0, 1.0)
    axes[0].set_ylabel("차이 (%p)")
    axes[0].set_title("BIOME4 생물군계별 비율 차이", loc="left")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(ncol=3, frameon=False, loc="upper right")

    for col, label in zip(pft_plot_codes, pft_labels):
        axes[1].plot(ages, Pdiff[col].to_numpy(), label=label, linewidth=1.35)
    axes[1].axhline(0, linewidth=0.8)
    axes[1].set_ylim(-1.0, 1.0)
    axes[1].set_ylabel("차이 (%p)")
    axes[1].set_title("선택 PFT별 격자 비율 차이", loc="left")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(ncol=2, frameon=False, loc="upper right")

    axes[2].plot(ages, biome_l1.to_numpy(), label="BIOME4 범주별 절대차 합계")
    axes[2].plot(ages, pft_l1.to_numpy(), label="선택 PFT 범주별 절대차 합계", linestyle="--")
    axes[2].set_ylabel("절대차 합계 (%p)")
    axes[2].set_xlabel("시기 (ka BP)")
    axes[2].set_title("시점별 전체 구성 차이 (범주별 절대차 합계)", loc="left")
    axes[2].grid(axis="y", alpha=0.25)
    axes[2].legend(frameon=False, loc="upper right")
    axes[2].set_xlim(120, 0)
    axes[2].set_xticks(np.arange(120, -1, -20))
    fig.suptitle("식생 비율 차이: 1 kyr − 0.1 kyr\n공통 정수 ka 시점 121개", y=0.995, fontsize=14)
    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
    fig.savefig(outdir / "vegetation_ratio_difference.png", dpi=220, bbox_inches="tight")
    fig.savefig(outdir / "vegetation_ratio_difference.svg", bbox_inches="tight")
    plt.close(fig)

    rows = []
    for age in ages:
        for code, label in zip(biome_cols, biome_labels):
            rows.append({
                "ratio_type": "BIOME4_area_percent",
                "code": "unclassified" if code == "미분류/미기록" else int(code),
                "category": label,
                "ka_bp": int(age),
                "share_1kyr_percent": float(B1.loc[age, code]),
                "share_0p1kyr_percent": float(B01.loc[age, code]),
                "difference_1kyr_minus_0p1kyr_pp": float(Bdiff.loc[age, code])
            })
        for code, label in zip(pft_plot_codes, pft_labels):
            rows.append({
                "ratio_type": "selected_PFT_grid_percent",
                "code": int(code),
                "category": label,
                "ka_bp": int(age),
                "share_1kyr_percent": float(P1.loc[age, code]),
                "share_0p1kyr_percent": float(P01.loc[age, code]),
                "difference_1kyr_minus_0p1kyr_pp": float(Pdiff.loc[age, code])
            })
    ratio_df = pd.DataFrame(rows)
    ratio_df.to_csv(outdir / "vegetation_ratio_comparison_integer_ka.csv",
                    index=False, encoding="utf-8-sig")

    different_ages = [int(x) for x in ages[~np.isclose(biome_l1.to_numpy(), 0)]]
    max_category_diff = float(max(Bdiff.abs().to_numpy().max(), Pdiff.abs().to_numpy().max()))
    max_total_diff = float(biome_l1.max())
    max_total_age = int(biome_l1.idxmax())
    readme = f"""# 120 ka BIOME4–Pelletier 시간간격 비교: 식생 비율

## 산출물
- biome4_area_ratio_timestep_comparison.png / .svg: BIOME4 생물군계별 면적 비율
- selected_pft_area_ratio_timestep_comparison.png / .svg: 선택 PFT별 격자 면적 비율
- vegetation_ratio_difference.png / .svg: 1 kyr와 0.1 kyr의 범주별 차이 및 시점별 전체 구성 차이
- vegetation_ratio_comparison_integer_ka.csv: 공통 정수 ka 시점별 범주 비율과 차이

## 비교 기준
- 120–0 ka BP의 공통 정수 시점 121개를 비교함.
- 0.1 kyr 실행 자료에서 정수 ka 시점만 추출했으며, 원래 0.1 kyr 자료는 변경하지 않음.
- 각 실행의 baseline을 대표로 사용함. scenario2는 BIOME4 및 선택 PFT 비율 시계열이 baseline과 모든 행에서 완전히 일치함.
- 유효 격자 236개, 20 m 격자 기준으로 각 셀의 면적 비율을 계산함.
- BIOME4에서 1 kyr 실행의 34 ka 시점은 한 셀의 생물군계 값이 미기록되어 면적 비율 합계가 99.5763%임. 이를 미분류/미기록 잔여 비율 0.4237%로 표시함.
- 선택 PFT 비율은 각 격자에서 선택된 optPFT 코드의 셀 점유율임. PFT 14는 별도 PFT가 아니라 목본·초본 공우점 판정 코드이며, PFT 0은 미선택 코드임.

## 요약
- BIOME4 및 선택 PFT 구성은 121개 시점 중 {121-len(different_ages)}개 시점에서 두 실행이 완전히 일치함.
- 차이가 발생한 시점: {", ".join(map(str, different_ages))} ka.
- 범주별 최대 절대차: {max_category_diff:.4f}%p.
- 시점별 범주 절대차 합계의 최대값: {max_total_diff:.4f}%p ({max_total_age} ka).
- 이 값은 면적 비율이며 식생 피복률이나 LAI 비율을 뜻하지 않음.
"""
    (outdir / "README_vegetation_ratio.md").write_text(readme, encoding="utf-8")

    zip_path = outdir / "global120_vegetation_ratio_comparison.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for path in sorted(outdir.iterdir()):
            if path.is_file() and path != zip_path:
                z.write(path, arcname=path.name)

    if not np.allclose(B1.sum(axis=1), 100.0, atol=1e-8):
        raise AssertionError("BIOME4 ratios including the unclassified residual do not sum to 100%")
    if not np.allclose(P1.sum(axis=1), 100.0, atol=1e-8):
        raise AssertionError("1-kyr selected PFT ratios do not sum to 100%")
    if not np.allclose(P01.sum(axis=1), 100.0, atol=1e-8):
        raise AssertionError("0.1-kyr selected PFT ratios do not sum to 100%")

    print({
        "integer_ka_points": len(ages),
        "exact_match_ages": 121-len(different_ages),
        "different_ages": different_ages,
        "max_category_difference_pp": max_category_diff,
        "max_total_absolute_difference_pp": max_total_diff,
        "max_difference_age_ka": max_total_age,
        "csv_rows": len(ratio_df),
        "output_files": sorted(p.name for p in outdir.iterdir())
    })


if __name__ == "__main__":
    main()
