from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
OUT_DIR = Path(__file__).resolve().parent

PNG_PATH = OUT_DIR / "CHELSA_TraCE21k_Yongneup_temperature_precipitation.png"
SVG_PATH = OUT_DIR / "CHELSA_TraCE21k_Yongneup_temperature_precipitation.svg"


def build_annual_climate(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate annual mean temperature and annual precipitation from monthly CHELSA-TraCE21k fields."""
    monthly_temp = []
    monthly_precip = []

    for month in range(1, 13):
        mm = f"{month:02d}"
        tmin = df[f"tasmin_raw_{mm}"]
        tmax = df[f"tasmax_raw_{mm}"]
        pr = df[f"pr_raw_{mm}"]

        monthly_temp.append(((tmin + tmax) / 2.0) - 273.15)
        monthly_precip.append(pr)

    return pd.DataFrame(
        {
            "ka_BP": df["ka_bp"],
            "temperature_C": pd.concat(monthly_temp, axis=1).mean(axis=1),
            "precipitation_mm": pd.concat(monthly_precip, axis=1).sum(axis=1),
        }
    )


def set_korean_font() -> None:
    candidates = ["Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    raw = pd.read_csv(DATA_PATH)
    climate = build_annual_climate(raw)
    set_korean_font()

    fig, ax1 = plt.subplots(figsize=(8.2, 4.8))

    temp_line, = ax1.plot(
        climate["ka_BP"], climate["temperature_C"],
        color="firebrick", linewidth=1.6, linestyle="-", label="기온"
    )
    ax1.set_xlabel("연대 (ka BP)")
    ax1.set_ylabel("연평균 기온 (°C)")
    ax1.set_xlim(21, 0)
    ax1.set_xticks(np.arange(21, -0.1, -3))

    ax2 = ax1.twinx()
    precip_line, = ax2.plot(
        climate["ka_BP"], climate["precipitation_mm"],
        color="royalblue", linewidth=1.4, linestyle="-", label="강수량"
    )
    ax2.set_ylabel("연강수량 (mm)")

    # No figure title by design.
    ax1.legend(
        [temp_line, precip_line],
        ["기온", "강수량"],
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
