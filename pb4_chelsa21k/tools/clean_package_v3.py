#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

VERSION = "6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008"


def replace_block(text: str, start_token: str, end_token: str, replacement: str) -> str:
    start = text.index(start_token)
    end = text.index(end_token, start)
    return text[:start] + replacement + text[end:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--repo-root", required=True)
    ns = ap.parse_args()

    root = Path(ns.root).resolve()
    repo_root = Path(ns.repo_root).resolve()

    # 1. GUI/engine version must be identical.
    p = root / "pb4studio" / "__init__.py"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"__version__\s*=\s*['\"].*?['\"]", f"__version__ = '{VERSION}'", s)
    p.write_text(s, encoding="utf-8")

    p = root / "gui" / "main.py"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'EXPECTED_VERSION\s*=\s*["\'].*?["\']', f'EXPECTED_VERSION = "{VERSION}"', s, count=1)
    p.write_text(s, encoding="utf-8")

    # 2. Package time-series figures: exact visual template of plot_chelsa_climate.py.
    p = root / "pb4studio" / "figures.py"
    s = p.read_text(encoding="utf-8")
    replacement = r'''def make_timeseries_figures(
    static_dir: Path,
    dynamic_dir: Path,
    fig_dir: Path,
    static_label: str = "정적모델",
    dynamic_label: str = "동적모델",
) -> List[Path]:
    """Save PB4 time-series figures using the CHELSA climate-figure style."""
    setup_korean_matplotlib()
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter

    fig_dir = Path(fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    frames = []
    for case_dir, label in [(dynamic_dir, dynamic_label), (static_dir, static_label)]:
        path = Path(case_dir) / "summary_timeseries.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["case_label"] = label
        frames.append(df)
    if not frames:
        return written
    ts = pd.concat(frames, ignore_index=True)
    ts["yr_bp"] = ts["ka_bp"].astype(float) * 1000.0

    specs = [
        ("mean_elevation_m", "평균 고도 (m)", "timeseries_mean_elevation.png", True),
        ("mean_soil_depth_m", "평균 토심 (m)", "timeseries_mean_soil_depth.png", False),
        ("mean_npp", r"평균 NPP (g C m$^{-2}$ yr$^{-1}$)", "timeseries_mean_npp.png", False),
    ]
    for col, ylabel, fname, disable_offset in specs:
        if col not in ts.columns:
            continue
        dynamic = ts[ts["case_label"] == dynamic_label].sort_values("ka_bp", ascending=False)
        static = ts[ts["case_label"] == static_label].sort_values("ka_bp", ascending=False)

        fig, ax1 = plt.subplots(figsize=(8.2, 4.8))
        dynamic_line, = ax1.plot(
            dynamic["ka_bp"], dynamic[col],
            color="firebrick", linewidth=1.6, linestyle="-", label=dynamic_label
        )
        ax1.set_xlabel("연대 (ka BP)")
        ax1.set_ylabel(ylabel)
        ax1.set_xlim(21, 0)
        ax1.set_xticks(np.arange(21, -0.1, -3))

        static_line, = ax1.plot(
            static["ka_bp"], static[col],
            color="royalblue", linewidth=1.4, linestyle="-", label=static_label
        )
        if disable_offset:
            formatter = ScalarFormatter(useOffset=False)
            formatter.set_scientific(False)
            ax1.yaxis.set_major_formatter(formatter)

        ax1.legend(
            [dynamic_line, static_line],
            [dynamic_label, static_label],
            loc="upper left", frameon=False
        )
        fig.tight_layout()
        out_path = fig_dir / fname
        fig.savefig(out_path, dpi=600, bbox_inches="tight")
        plt.close(fig)
        written.append(out_path)

    if "vegetation_class_counts" in ts.columns and "n_cells" in ts.columns:
        ratio = parse_vegetation_ratio_long(ts)
        if not ratio.empty:
            class_order = [0, 1, 2, 3, 4]
            colors = ["#1f78b4", "#33a02c", "#b2df8a", "#fdbf6f", "#bdbdbd"]
            case_order = list(dict.fromkeys(ratio["case_label"].tolist()))
            fig, axes = plt.subplots(nrows=len(case_order), ncols=1, figsize=(9, 3.1 * len(case_order)),
                                      sharex=True, squeeze=False)
            for ax, case_label in zip(axes[:, 0], case_order):
                sub_case = ratio[ratio["case_label"] == case_label]
                pivot = sub_case.pivot_table(index="yr_bp", columns="vegetation_code", values="ratio_pct",
                                              aggfunc="mean").sort_index(ascending=False)
                for cls in class_order:
                    if cls not in pivot.columns:
                        pivot[cls] = 0.0
                pivot = pivot[class_order].fillna(0.0)
                ax.stackplot(pivot.index.values, [pivot[cls].values for cls in class_order],
                             labels=[VEG_CODE_LABEL_KO[cls] for cls in class_order], colors=colors, alpha=0.85)
                ax.set_title(str(case_label))
                ax.set_ylabel("면적 비율 (%)")
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.25)
                ax.invert_xaxis()
            axes[-1, 0].set_xlabel("시간 (yr BP, 1000년 간격)")
            handles, labels = axes[0, 0].get_legend_handles_labels()
            fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=9, frameon=True)
            fig.suptitle("시간에 따른 식생유형 비율", fontsize=14)
            fig.tight_layout(rect=(0, 0.08, 1, 0.96))
            out_path = fig_dir / "timeseries_vegetation_ratio.png"
            fig.savefig(out_path, dpi=300)
            plt.close(fig)
            written.append(out_path)

    return written
'''
    start = s.index("def make_timeseries_figures(")
    end = s.index("\n    return written", start) + len("\n    return written")
    s = s[:start] + replacement + s[end:]
    p.write_text(s, encoding="utf-8")

    # 3. Standard-report mean plots use the same template.
    p = root / "pb4studio" / "standard_report.py"
    s = p.read_text(encoding="utf-8")
    replacement = r'''def _make_mean_series(ts: pd.DataFrame, col: str, title: str, ylabel: str, out: Path) -> Path:
    setup_korean_matplotlib()
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter

    dynamic = ts[ts["case_label"] == "동적모델"].sort_values("ka_bp", ascending=False)
    static = ts[ts["case_label"] == "정적모델"].sort_values("ka_bp", ascending=False)

    fig, ax1 = plt.subplots(figsize=(8.2, 4.8))
    dynamic_line, = ax1.plot(
        dynamic["ka_bp"], dynamic[col],
        color="firebrick", linewidth=1.6, linestyle="-", label="동적모델"
    )
    ax1.set_xlabel("연대 (ka BP)")
    ax1.set_ylabel(ylabel)
    ax1.set_xlim(21, 0)
    ax1.set_xticks(np.arange(21, -0.1, -3))

    static_line, = ax1.plot(
        static["ka_bp"], static[col],
        color="royalblue", linewidth=1.4, linestyle="-", label="정적모델"
    )
    if col == "mean_elevation_m":
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        ax1.yaxis.set_major_formatter(formatter)

    ax1.legend(
        [dynamic_line, static_line], ["동적모델", "정적모델"],
        loc="upper left", frameon=False
    )
    fig.tight_layout()
    fig.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    return out
'''
    s = replace_block(s, "def _make_mean_series(", "\ndef _parse_class_counts", replacement + "\n")
    p.write_text(s, encoding="utf-8")

    # 4. FULL_EXPORT plots use identical visual rules.
    p = root / "tools" / "export_all_outputs.py"
    s = p.read_text(encoding="utf-8")
    replacement = r'''def make_plots(all_ts: pd.DataFrame, export_dir: Path) -> None:
    from matplotlib.ticker import ScalarFormatter

    specs = [
        ("mean_elevation_m", "평균 고도 (m)", "mean_elevation_211times.png", True),
        ("mean_soil_depth_m", "평균 토심 (m)", "mean_soil_depth_211times.png", False),
        ("mean_npp", r"평균 NPP (g C m$^{-2}$ yr$^{-1}$)", "mean_npp_211times.png", False),
        ("mean_eemt", r"평균 EEMT (MJ m$^{-2}$ yr$^{-1}$)", "mean_eemt_211times.png", False),
        ("reich_lai_sapwood_agb_mean_kg_m2", r"평균 AGB* (kg m$^{-2}$)", "mean_agb_star_211times.png", False),
    ]
    for col, ylabel, name, disable_offset in specs:
        if col not in all_ts.columns:
            continue
        dynamic = all_ts[all_ts["mode"] == "dynamic"].sort_values("ka_bp", ascending=False)
        static = all_ts[all_ts["mode"] == "static"].sort_values("ka_bp", ascending=False)

        fig, ax1 = plt.subplots(figsize=(8.2, 4.8))
        dynamic_line, = ax1.plot(
            dynamic["ka_bp"], dynamic[col],
            color="firebrick", linewidth=1.6, linestyle="-", label="동적모델"
        )
        ax1.set_xlabel("연대 (ka BP)")
        ax1.set_ylabel(ylabel)
        ax1.set_xlim(21, 0)
        ax1.set_xticks(np.arange(21, -0.1, -3))

        static_line, = ax1.plot(
            static["ka_bp"], static[col],
            color="royalblue", linewidth=1.4, linestyle="-", label="정적모델"
        )
        if disable_offset:
            formatter = ScalarFormatter(useOffset=False)
            formatter.set_scientific(False)
            ax1.yaxis.set_major_formatter(formatter)

        ax1.legend(
            [dynamic_line, static_line], ["동적모델", "정적모델"],
            loc="upper left", frameon=False
        )
        fig.tight_layout()
        fig.savefig(export_dir / name, dpi=600, bbox_inches="tight")
        plt.close(fig)
'''
    s = replace_block(s, "def make_plots(", "\ndef style_excel", replacement + "\n")
    p.write_text(s, encoding="utf-8")

    # 5. Keep the GitHub plot scripts in the package; one plotting source of truth.
    plots_dst = root / "plots"
    plots_dst.mkdir(exist_ok=True)
    plots_src = repo_root / "pb4_chelsa21k" / "plots"
    for name in ("plot_chelsa_climate.py", "plot_mean_elevation.py", "plot_mean_soil_depth.py", "plot_mean_npp.py"):
        shutil.copy2(plots_src / name, plots_dst / name)

    # 6. Remove old audits/debug/reference output from end-user ZIP.
    for name in ("diagnostics", "embedded_reference_results", "REFERENCE_FINAL_EXPORT_U008"):
        q = root / name
        if q.exists():
            shutil.rmtree(q)
    for q in root.rglob("__pycache__"):
        shutil.rmtree(q, ignore_errors=True)

    keep_top = {
        "CHECK_CHELSA21K_CONTRACT.bat",
        "FIRST_RUN_SETUP.bat",
        "MAKE_STANDARD_RESULT_FIGURES.bat",
        "README_CHELSA21K.txt",
        "README_FULL_EXPORT_KO.txt",
        "RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat",
        "RUN_YONGNEUP_21KA_CHELSA_SELFCONTAINED.bat",
        "START_PB4Studio.bat",
        "requirements.txt",
    }
    for q in list(root.iterdir()):
        if q.is_file() and q.name not in keep_top:
            q.unlink()

    keep_tools = {
        "run_yongneup_21ka_chelsa_selfcontained.py",
        "export_all_outputs.py",
        "make_standard_result_figures.py",
    }
    for q in (root / "tools").iterdir():
        if q.is_file() and q.name not in keep_tools:
            q.unlink()

    outputs = root / "outputs_CHELSA21K"
    if outputs.exists():
        shutil.rmtree(outputs)
    outputs.mkdir()
    (outputs / "README_RUN_TO_GENERATE.txt").write_text(
        "실행 결과는 이 폴더에 생성됩니다.\nRUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat을 실행하십시오.\n",
        encoding="utf-8",
    )

    (root / "README_FULL_EXPORT_KO.txt").write_text(
        f"""PB4Studio CHELSA21K U008 CLEAN FULL EXPORT
=============================================

버전
- {VERSION}
- regional uplift U = 0.08 m/kyr

실행
1. FIRST_RUN_SETUP.bat 최초 1회
2. START_PB4Studio.bat: GUI
3. RUN_YONGNEUP_21KA_AND_EXPORT_ALL.bat: 21 ka 전체 실행 및 전체 출력

시간축
- 21.0 ka BP에서 시작
- 0.0 ka BP까지
- 0.1 kyr 간격
- 총 211 시점

고도, 토심, NPP 시계열 그림
- pb4_chelsa21k/plots/plot_chelsa_climate.py와 동일한 시각 형식
- figsize 8.2 x 4.8
- x축 21 -> 0 ka BP
- x 눈금 21, 18, 15, 12, 9, 6, 3, 0
- 동적모델 firebrick, linewidth 1.6
- 정적모델 royalblue, linewidth 1.4
- 제목 없음, grid 없음, 범례 좌상단 frame 없음
- PNG 600 dpi
- 고도 matplotlib offset 표기 비활성화

불필요한 과거 audit, diagnostics, reference output, bytecode, 테스트 스크립트는 배포 ZIP에서 제거합니다.
""",
        encoding="utf-8",
    )

    if "6.6.3-CHELSA21K-envicloud-nolapse" in "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".py", ".txt", ".md", ".bat"}
    ):
        raise RuntimeError("stale EXPECTED_VERSION remains")

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
