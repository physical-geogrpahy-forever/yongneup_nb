"""Park et al. (2021) 자료의 기간 단위 판정(3.2~0.5 ka).

시점별 판정은 유효표본수가 작아(BDE 약 8, TBD 약 5) 정밀도가 낮으므로,
72개 시료를 합쳐 그룹마다 '이 기간에 있었는가'를 한 번만 판정한다.
관측: 합산 계수의 95% 신뢰구간(Clopper-Pearson) 하한이 그룹 기준 이상이면 출현,
상한이 0.5% 미만이면 비출현, 그 밖은 판정 불가.
모델: 28개 시점 중 유역 격자 1% 이상(7격자)을 차지한 시점 수와 평균 점유율.
사용법: python park_period_level.py [reference_run 폴더] [출력 폴더]
"""
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "reference_run"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
N_CELLS = 656
MIN_CELLS = math.ceil(0.01 * N_CELLS)
GROUPS = ("TBD", "BDE", "CON", "TBE", "GRS", "DWD")


def ci95(k: int, n: int) -> tuple[float, float]:
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return 100 * lo, 100 * hi


def main() -> None:
    data = {}
    for m in ("static", "dynamic"):
        o = pd.read_csv(RUN / f"model_{m}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
        o["grains"] = np.rint(o.obs_pct * o.terrestrial_sum / 100).astype(int)
        data[m] = o
    rows = []
    for g in GROUPS:
        d = data["dynamic"][data["dynamic"].pft_group == g]
        k, n, thr = int(d.grains.sum()), int(d.terrestrial_sum.sum()), float(d.threshold_pct.iloc[0])
        lo, hi = ci95(k, n)
        obs = "present" if lo >= thr else ("absent" if hi < 0.5 else "uncertain")
        row = {"group": g, "grains": k, "pollen_sum": n, "pct": 100 * k / n, "ci_lo": lo, "ci_hi": hi,
               "threshold_pct": thr, "observed": obs}
        for m, o in data.items():
            dm = o[o.pft_group == g]
            row[f"{m}_windows_present"] = int((dm.model_cells >= MIN_CELLS).sum())
            row[f"{m}_mean_share_pct"] = 100 * dm.model_cells.mean() / N_CELLS
            pres = row[f"{m}_windows_present"] > 0
            row[f"{m}_match"] = "n/a" if obs == "uncertain" else ("yes" if pres == (obs == "present") else "no")
        rows.append(row)
    res = pd.DataFrame(rows)
    res.round(3).to_csv(OUT / "park_period_level.csv", index=False, encoding="utf-8-sig")
    print(res.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
