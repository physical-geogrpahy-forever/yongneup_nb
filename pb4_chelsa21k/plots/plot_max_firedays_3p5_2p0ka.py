from pathlib import Path
import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 사용법: python plot_max_firedays_3p5_2p0ka.py [STATE_CUBE.npz] [기후 CSV] [출력폴더]
_HERE = Path(__file__).resolve().parent
CUBE_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "results" / "final_fab30_20261113" / "FINAL_STATE_CUBE.npz"
CLIMATE_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else _HERE.parent / "data" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
OUT_DIR = Path(sys.argv[3]) if len(sys.argv) > 3 else _HERE

PNG_PATH = OUT_DIR / "YONGNEUP_FINAL_max_firedays_3p5_2p0ka.png"
SVG_PATH = OUT_DIR / "YONGNEUP_FINAL_max_firedays_3p5_2p0ka.svg"
CSV_PATH = OUT_DIR / "YONGNEUP_FINAL_max_firedays_3p5_2p0ka.csv"

KA_OLD, KA_YOUNG = 3.5, 2.0
# Park et al. (2021)의 대형 목탄 기반 주요 산불 시기 (ka BP)
FIRE_EPISODES = [(2.9, 2.7), (2.4, 2.3)]


def set_korean_font() -> None:
    candidates = ["Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def max_firedays(cube: np.lib.npyio.NpzFile, mode: str) -> np.ndarray:
    """각 시점에서 식생 격자의 우점 PFT 기준 산불잠재일수 중 최대값."""
    land = cube[f"{mode}__land"].astype(bool)
    fire = np.where(land, cube[f"{mode}__firedays_node"], np.nan)
    return np.nanmax(fire, axis=(1, 2))


def annual_precipitation(df: pd.DataFrame) -> pd.DataFrame:
    pr = sum(df[f"pr_raw_{m:02d}"] for m in range(1, 13))
    return pd.DataFrame({"ka_BP": df["ka_bp"].round(1), "precipitation_mm": pr})


def main() -> None:
    cube = np.load(CUBE_PATH)
    ka = np.round(cube["times_ka"].astype(float), 1)
    fire = pd.DataFrame({
        "ka_BP": ka,
        "dynamic_max_firedays": max_firedays(cube, "dynamic"),
        "static_max_firedays": max_firedays(cube, "static"),
    })
    climate = annual_precipitation(pd.read_csv(CLIMATE_PATH))
    data = fire.merge(climate, on="ka_BP", how="left")
    data = data[(data["ka_BP"] <= KA_OLD) & (data["ka_BP"] >= KA_YOUNG)].sort_values("ka_BP", ascending=False)
    data.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

    set_korean_font()
    fig, ax1 = plt.subplots(figsize=(8.2, 4.8))

    for old, young in FIRE_EPISODES:
        ax1.axvspan(old, young, color="lightsteelblue", alpha=0.45, linewidth=0, zorder=0)

    dynamic_line, = ax1.plot(
        data["ka_BP"], data["dynamic_max_firedays"],
        color="firebrick", linewidth=1.6, linestyle="-", marker="o", markersize=3, label="동적모델"
    )
    static_line, = ax1.plot(
        data["ka_BP"], data["static_max_firedays"],
        color="royalblue", linewidth=1.4, linestyle="-", marker="o", markersize=3, label="정적모델"
    )
    ax1.set_xlabel("연대 (ka BP)")
    ax1.set_ylabel("최대 산불잠재일수 (일)")
    ax1.set_xlim(KA_OLD, KA_YOUNG)
    ax1.set_xticks(np.arange(KA_OLD, KA_YOUNG - 0.01, -0.5))
    ax1.set_xticks(np.arange(KA_OLD, KA_YOUNG - 0.01, -0.1), minor=True)
    ymax = float(np.nanmax(data["dynamic_max_firedays"]))
    ax1.set_ylim(0, max(10.0, np.ceil(ymax * 1.15 / 10.0) * 10.0))

    ax2 = ax1.twinx()
    precip_line, = ax2.plot(
        data["ka_BP"], data["precipitation_mm"],
        color="dimgray", linewidth=1.2, linestyle="--", label="강수량"
    )
    ax2.set_ylabel("연강수량 (mm)")

    # No figure title by design, matching plot_chelsa_climate.py.
    ax1.legend(
        [dynamic_line, static_line, precip_line],
        ["동적모델", "정적모델", "강수량"],
        loc="upper left", frameon=False
    )

    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=600, bbox_inches="tight")
    fig.savefig(SVG_PATH, bbox_inches="tight")
    plt.close(fig)

    print(PNG_PATH)
    print(SVG_PATH)
    print(CSV_PATH)


if __name__ == "__main__":
    main()
