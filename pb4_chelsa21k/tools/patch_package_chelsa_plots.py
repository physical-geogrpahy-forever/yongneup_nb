from __future__ import annotations

import argparse
from pathlib import Path


def patch_figures(root: Path) -> Path:
    p = root / "pb4studio" / "figures.py"
    s = p.read_text(encoding="utf-8")

    anchor = 'ts["yr_bp"] = ts["ka_bp"].astype(float) * 1000.0'
    start = s.index("    specs = [", s.index(anchor))
    end = s.index("    # 식생유형 비율 시계열", start)

    body = r'''# Main PB4 time-series figures use the exact visual conventions of
# plots/plot_chelsa_climate.py: 8.2 x 4.8 inch canvas, firebrick 1.6
# and royalblue 1.4 lines, 21 -> 0 ka BP, 3-kyr ticks, no title,
# no grid, upper-left frameless legend, 600 dpi.
specs = [
    ("mean_elevation_m", "평균 고도 (m)", "timeseries_mean_elevation.png"),
    ("mean_soil_depth_m", "평균 토심 (m)", "timeseries_mean_soil_depth.png"),
    ("mean_npp", r"평균 NPP (g C m$^{-2}$ yr$^{-1}$)", "timeseries_mean_npp.png"),
]
for col, ylabel, fname in specs:
    if col not in ts.columns:
        continue

    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    dynamic = ts[ts["case_label"] == dynamic_label].sort_values("ka_bp", ascending=False)
    static = ts[ts["case_label"] == static_label].sort_values("ka_bp", ascending=False)

    dynamic_line, = ax.plot(
        dynamic["ka_bp"], dynamic[col],
        color="firebrick", linewidth=1.6, linestyle="-", label=dynamic_label
    )
    static_line, = ax.plot(
        static["ka_bp"], static[col],
        color="royalblue", linewidth=1.4, linestyle="-", label=static_label
    )

    ax.set_xlabel("연대 (ka BP)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(21, 0)
    ax.set_xticks(np.arange(21, -0.1, -3))

    if col == "mean_elevation_m":
        from matplotlib.ticker import ScalarFormatter
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(formatter)

    ax.legend(
        [dynamic_line, static_line],
        [dynamic_label, static_label],
        loc="upper left", frameon=False
    )

    fig.tight_layout()
    out_path = fig_dir / fname
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.close(fig)
    written.append(out_path)
'''
    new = "\n".join(("    " + line if line else "") for line in body.splitlines()) + "\n\n"
    p.write_text(s[:start] + new + s[end:], encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ns = ap.parse_args()
    root = Path(ns.root).resolve()
    p = patch_figures(root)
    print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
