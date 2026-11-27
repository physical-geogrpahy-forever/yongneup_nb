"""FAO-UNESCO (1974)의 세 토성 구분(BIOME4 토성 등급 1, 2, 3).

사용법: python plot_fao_soil_texture_triangle.py
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import thesis_style as ts

OUT = Path(__file__).resolve().parent
NAME = "fig_soil_texture_triangle"
H = sqrt(3.0) / 2.0
COLORS = {1: "#f2f2f2", 2: "#d9d9d9", 3: "#bfbfbf"}


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


def main() -> None:
    assert fao_class(80, 10, 10) == 1
    assert fao_class(40, 40, 20) == 2
    assert fao_class(15, 40, 45) == 3
    assert fao_class(82, 0, 18) == 2

    ts.setup()
    fig, ax = plt.subplots(figsize=(0.62 * ts.WIDTH, 0.56 * ts.WIDTH))
    ax.set_aspect("equal")
    ax.set_xlim(-0.16, 1.16)
    ax.set_ylim(-0.17, 0.92)
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
                color="#ffffff", alpha=0.9, zorder=2
            )

    # FAO's exact class boundaries: clay 35, clay 18 (partial), sand 65 (partial).
    for endpoints in (
        (point(65, 35), point(0, 35)),
        (point(82, 18), point(65, 18)),
        (point(65, 0), point(65, 18)),
    ):
        a, b = endpoints
        ax.plot((a[0], b[0]), (a[1], b[1]), color="#000000", lw=1.0, zorder=4)

    outline = [point(100, 0), point(0, 100), point(0, 0), point(100, 0)]
    ax.plot(
        [p[0] for p in outline], [p[1] for p in outline],
        color="#000000", lw=0.8, zorder=5
    )

    for k in range(0, 101, 20):
        px, py = point(100-k, k)
        ax.text(px-0.035, py+0.004, str(k), ha="right", va="center",
                fontsize=7)
        px, py = point(k, 0)
        ax.text(px, py-0.043, str(k), ha="center", va="top",
                fontsize=7)
        px, py = xy(0, k, 100-k)
        ax.text(px+0.035, py+0.004, str(k), ha="left", va="center",
                fontsize=7)

    ax.text(-0.12, 0.45, "점토 (%)", rotation=60, ha="center", va="center")
    ax.text(0.50, -0.135, "모래 (%)", ha="center", va="center")
    ax.text(1.12, 0.45, "미사 (%)", rotation=-60, ha="center", va="center")
    ax.text(*point(80, 7), "조립질", ha="center", va="center", zorder=6)
    ax.text(*point(38, 16), "중립질", ha="center", va="center", zorder=6)
    ax.text(*point(25, 58), "세립질", ha="center", va="center", zorder=6)
    ts.save(fig, OUT, NAME)


if __name__ == "__main__":
    main()
