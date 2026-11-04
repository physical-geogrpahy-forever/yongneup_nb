"""Reproduce the FAO–UNESCO (1974) 3-class soil texture triangle.

Classes 1–3 match BIOME4 v4.2b2 soildata.
The Yongneup production raster uses class 2 in every valid cell.
No unmeasured sand/silt/clay composition point is invented.

Usage: python pb4_chelsa21k/plots/plot_fao_soil_texture_triangle.py
Outputs: PB4_FAO_soil_texture_classes_1_2_3.{png,svg} beside the script.
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

OUT = Path(__file__).resolve().parent
NAME = "PB4_FAO_soil_texture_classes_1_2_3"
H = sqrt(3.0) / 2.0
COLORS = {1: "#F3D6B4", 2: "#CAE2D5", 3: "#C6D2EE"}


def fao_class(sand: float, silt: float, clay: float) -> int:
    """FAO–UNESCO (1974), Legend p. 5; exact boundary assigned to medium."""
    if any(x < 0 or x > 100 for x in (sand, silt, clay)):
        raise ValueError("Sand, silt and clay must each be in [0, 100].")
    if abs(sand + silt + clay - 100) > 1e-6:
        raise ValueError("Sand + silt + clay must equal 100%.")
    if clay > 35:
        return 3
    if sand > 65 and clay < 18:
        return 1
    return 2


def xy(sand: float, silt: float, clay: float) -> tuple[float, float]:
    """Ternary point: sand at left, silt at right, clay at apex."""
    return ((silt + clay / 2.0) / 100.0, H * clay / 100.0)


def point(sand: float, clay: float) -> tuple[float, float]:
    return xy(sand, 100.0 - sand - clay, clay)


def set_korean_font() -> None:
    names = {font.name for font in fm.fontManager.ttflist}
    for name in ("Noto Sans CJK KR", "NanumGothic", "Noto Sans KR",
                 "Malgun Gothic", "AppleGothic"):
        if name in names:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams.update({
        "axes.unicode_minus": False, "svg.fonttype": "none", "pdf.fonttype": 42
    })


def main() -> None:
    assert fao_class(80, 10, 10) == 1
    assert fao_class(40, 40, 20) == 2
    assert fao_class(15, 40, 45) == 3
    assert fao_class(82, 0, 18) == 2

    set_korean_font()
    fig = plt.figure(figsize=(12.8, 7.4), facecolor="white")
    gs = fig.add_gridspec(
        1, 2, width_ratios=[1.58, 0.91], wspace=0.06,
        left=0.045, right=0.97, top=0.89, bottom=0.105
    )
    ax = fig.add_subplot(gs[0, 0])
    ax.set_aspect("equal")
    ax.set_xlim(-0.18, 1.15)
    ax.set_ylim(-0.18, 0.98)
    ax.axis("off")

    polygons = {
        1: [(100, 0), (82, 18), (65, 18), (65, 0)],
        2: [(65, 0), (65, 18), (82, 18), (65, 35), (0, 35), (0, 0)],
        3: [(65, 35), (0, 100), (0, 35)],
    }
    for cls in (2, 3, 1):
        ax.add_patch(Polygon(
            [point(sand, clay) for sand, clay in polygons[cls]],
            closed=True, facecolor=COLORS[cls], edgecolor="none", zorder=1
        ))

    # Draw the 10%-step ternary grid.
    for k in range(10, 100, 10):
        for endpoints in (
            (point(100-k, k), point(0, k)),          # constant clay
            (point(k, 0), point(k, 100-k)),          # constant sand
            (xy(0, k, 100-k), xy(100-k, k, 0)),     # constant silt
        ):
            (x0, y0), (x1, y1) = endpoints
            ax.plot(
                [x0, x1], [y0, y1], lw=0.46,
                color="#FFFFFF", alpha=0.80, zorder=2
            )

    # FAO's exact class boundaries: clay 35, clay 18 (partial), sand 65 (partial).
    for endpoints in (
        (point(65, 35), point(0, 35)),
        (point(82, 18), point(65, 18)),
        (point(65, 0), point(65, 18)),
    ):
        a, b = endpoints
        ax.plot((a[0], b[0]), (a[1], b[1]), color="#181818", lw=2.2, zorder=4)

    outline = [point(100, 0), point(0, 100), point(0, 0), point(100, 0)]
    ax.plot(
        [p[0] for p in outline], [p[1] for p in outline],
        color="#141414", lw=1.75, zorder=5
    )

    for k in range(0, 101, 20):
        px, py = point(100-k, k)
        ax.text(px-0.035, py+0.004, str(k), ha="right", va="center",
                fontsize=9, color="#4E4E4E")
        px, py = point(k, 0)
        ax.text(px, py-0.043, str(k), ha="center", va="top",
                fontsize=9, color="#4E4E4E")
        px, py = xy(0, k, 100-k)
        ax.text(px+0.035, py+0.004, str(k), ha="left", va="center",
                fontsize=9, color="#4E4E4E")

    ax.text(-0.135, 0.43, "점토 (Clay, %)", rotation=60,
            ha="center", va="center", fontsize=12)
    ax.text(0.50, -0.126, "모래 (Sand, %)",
            ha="center", va="center", fontsize=12)
    ax.text(1.107, 0.43, "미사 (Silt, %)", rotation=-60,
            ha="center", va="center", fontsize=12)
    ax.text(*point(79, 8), "1  조립질\nCoarse",
            ha="center", va="center", fontsize=12, weight="bold", zorder=6)
    ax.text(*point(39, 15), "2  중립질\nMedium",
            ha="center", va="center", fontsize=14, weight="bold", zorder=6)
    ax.text(*point(25, 57), "3  세립질\nFine",
            ha="center", va="center", fontsize=14, weight="bold", zorder=6)

    info = fig.add_subplot(gs[0, 1])
    info.axis("off")
    info.set_xlim(0, 1)
    info.set_ylim(0, 1)
    info.text(0.06, 0.92, "BIOME4 토성 구분",
              size=17, weight="bold", va="top")
    items = (
        (1, 0.78, "조립질  /  Coarse", "모래 > 65%, 점토 < 18%", "Ksat = 5.0 mm/h"),
        (2, 0.57, "중립질  /  Medium", "점토 < 35%, 1번 등급 제외", "Ksat = 4.0 mm/h"),
        (3, 0.36, "세립질  /  Fine", "점토 > 35%", "Ksat = 3.0 mm/h"),
    )
    for cls, yy, heading, rule, hydraulic in items:
        info.add_patch(Rectangle(
            (0.06, yy-0.095), 0.058, 0.145,
            facecolor=COLORS[cls], edgecolor="#555555", lw=0.7
        ))
        info.text(0.15, yy+0.025, heading, size=12.5, weight="bold", va="center")
        info.text(0.15, yy-0.034, rule, size=10.7, va="center")
        info.text(0.15, yy-0.078, hydraulic,
                  size=10.3, color="#545454", va="center")
    info.plot([0.06, 0.96], [0.175, 0.175], color="#A1A1A1", lw=0.8)
    info.text(0.06, 0.143, "용늪 PB4 최종 입력: 유효 격자 모두 2번",
              fontsize=10.8, weight="bold")
    info.text(0.06, 0.083, "입도 관측값의 위치는 표시하지 않음",
              fontsize=10.1, color="#555555")

    fig.text(
        0.5, 0.958, "FAO 토성 삼각도 — PB4Studio / BIOME4 등급 1·2·3",
        ha="center", va="center", fontsize=18, weight="bold"
    )
    fig.text(
        0.5, 0.035,
        "자료: FAO–UNESCO (1974), Soil Map of the World, Vol. I, p. 5; "
        "BIOME4 v4.2b2 soildata (Ksat).  |  경계선의 정확한 임계값은 중립질로 표기",
        ha="center", fontsize=9.2, color="#555555"
    )
    for extension in ("png", "svg"):
        dest = OUT / f"{NAME}.{extension}"
        fig.savefig(
            dest, dpi=250 if extension == "png" else None,
            bbox_inches="tight", facecolor="white"
        )
        print(dest)
    plt.close(fig)


if __name__ == "__main__":
    main()
