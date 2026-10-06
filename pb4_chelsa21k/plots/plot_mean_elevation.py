from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "final_integrated_20261006" / "FINAL_AGB_21KA_TIMESERIES.csv"
OUT_DIR = Path(__file__).resolve().parent

PNG_PATH = OUT_DIR / "YONGNEUP_U008_mean_elevation_CHELSA_style.png"
SVG_PATH = OUT_DIR / "YONGNEUP_U008_mean_elevation_CHELSA_style.svg"


def set_korean_font() -> None:
    candidates = ["Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    set_korean_font()

    dynamic = df[df["mode"] == "dynamic"].sort_values("ka_bp", ascending=False)
    static = df[df["mode"] == "static"].sort_values("ka_bp", ascending=False)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    dyn_line, = ax.plot(
        dynamic["ka_bp"], dynamic["mean_elevation_m"],
        color="firebrick", linewidth=1.6, linestyle="-", label="동적모델"
    )
    sta_line, = ax.plot(
        static["ka_bp"], static["mean_elevation_m"],
        color="royalblue", linewidth=1.4, linestyle="-", label="정적모델"
    )

    ax.set_xlabel("연대 (ka BP)")
    ax.set_ylabel("평균 고도 (m)")
    ax.set_xlim(21, 0)
    ax.set_xticks(np.arange(21, -0.1, -3))

    formatter = ScalarFormatter(useOffset=False)
    formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(formatter)

    values = pd.concat(
        [dynamic["mean_elevation_m"], static["mean_elevation_m"]]
    ).dropna()
    margin = max((values.max() - values.min()) * 0.08, 0.03)
    ax.set_ylim(values.min() - margin, values.max() + margin)

    # No title, matching plot_chelsa_climate.py.
    ax.legend(
        [dyn_line, sta_line],
        ["동적모델", "정적모델"],
        loc="upper left", frameon=False
    )

    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=600, bbox_inches="tight")
    fig.savefig(SVG_PATH, bbox_inches="tight")
    plt.close(fig)

    print(PNG_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()
