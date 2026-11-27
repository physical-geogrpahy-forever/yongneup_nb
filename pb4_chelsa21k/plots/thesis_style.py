"""논문 그림 공통 형식."""
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

CM = 1 / 2.54
WIDTH = 16 * CM          # 본문 폭
INK = "#000000"
GRAY = "#808080"
LIGHT = "#d9d9d9"
DYN = dict(color=INK, lw=1.0, ls="-")
STA = dict(color=GRAY, lw=1.0, ls="--")


def setup() -> None:
    for name in ("Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic"):
        if name in {f.name for f in fm.fontManager.ttflist}:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.5,
        "ytick.minor.width": 0.5,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 1.8,
        "ytick.minor.size": 1.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })


def panel(ax, letter: str) -> None:
    ax.annotate(f"({letter})", xy=(0, 1), xycoords="axes fraction", xytext=(-2, 7),
                textcoords="offset points", ha="right", va="bottom", fontsize=8.5)


def save(fig, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(out_dir / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(out_dir / f"{stem}.png")
