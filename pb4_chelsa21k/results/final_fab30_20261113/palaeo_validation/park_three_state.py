"""Park et al. (2021) PFT 검증의 세 범주 판정과 계수 오차.

화분만으로 비출현을 증명할 수 없으므로(Prentice et al., 1996; Hicks, 2006; Ammann et al., 2014)
관측을 출현(그룹 기준 이상), 비출현(0.5% 미만 또는 0알), 판정 불가(그 사이)로 나누고
판정 가능한 시점만으로 민감도, 특이도, TSS를 계산한다. 모델 출현은 유역 1%.
계수 오차는 이항분포 95% 신뢰구간(Clopper-Pearson; Maher, 1972의 신뢰한계와 같은 취지).
사용법: python park_three_state.py [reference_run 폴더] [출력 폴더]
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


def ci95(k: int, n: int) -> tuple[float, float]:
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return 100 * lo, 100 * hi


def load(model: str) -> pd.DataFrame:
    o = pd.read_csv(RUN / f"model_{model}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
    o["grains"] = np.rint(o.obs_pct * o.terrestrial_sum / 100).astype(int)
    ci = np.array([ci95(k, n) for k, n in zip(o.grains, o.terrestrial_sum)])
    o["ci_lo"], o["ci_hi"] = ci[:, 0], ci[:, 1]
    return o


def score(o: pd.DataFrame, presence_thr, absence: str) -> dict:
    thr = o.threshold_pct if presence_thr == "group" else float(presence_thr)
    absent = (o.grains == 0) if absence == "0 grains" else (o.obs_pct < 0.5)
    state = np.where(o.obs_pct >= thr, "P", np.where(absent, "A", "U"))
    pres = (o.model_cells >= math.ceil(0.01 * N_CELLS)).values
    tp = int(((state == "P") & pres).sum()); fn = int(((state == "P") & ~pres).sum())
    fp = int(((state == "A") & pres).sum()); tn = int(((state == "A") & ~pres).sum())
    se = tp / (tp + fn) if tp + fn else float("nan"); sp = tn / (tn + fp) if tn + fp else float("nan")
    return {"n_scored": tp + fn + fp + tn, "n_uncertain": int((state == "U").sum()), "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "sensitivity": se, "specificity": sp, "TSS": se + sp - 1}


def main() -> None:
    data = {m: load(m) for m in ("static", "dynamic")}
    rows = []
    for absence in ("<0.5%", "0 grains"):
        for thr in ("group", 1, 2, 5, 10):
            for m, o in data.items():
                rows.append({"absence_rule": absence, "presence_rule": f"{thr}" if thr == "group" else f"{thr}%",
                             "model": m, **score(o, thr, absence)})
    res = pd.DataFrame(rows)
    res.round(3).to_csv(OUT / "park_three_state.csv", index=False, encoding="utf-8-sig")

    o = data["dynamic"]
    rows = []
    for g in ("TBD", "BDE", "CON", "TBE", "GRS", "DWD"):
        d = o[o.pft_group == g]
        thr = d.threshold_pct.iloc[0]
        st = np.where(d.obs_pct >= thr, "P", np.where(d.obs_pct < 0.5, "A", "U"))
        rows.append({"group": g, "present": int((st == "P").sum()), "absent": int((st == "A").sum()),
                     "uncertain": int((st == "U").sum()),
                     "static_model_present_in_uncertain": int((data["static"].loc[d.index[st == "U"], "model_cells"] >= 7).sum()),
                     "dynamic_model_present_in_uncertain": int((d.model_cells[st == "U"] >= 7).sum())})
    pd.DataFrame(rows).to_csv(OUT / "park_three_state_by_group.csv", index=False, encoding="utf-8-sig")

    b = o[(o.pft_group == "BDE") & (o.obs_present == 0)][["ka_bp", "grains", "terrestrial_sum", "obs_pct", "ci_lo", "ci_hi", "n_pollen_samples"]]
    b.round(2).to_csv(OUT / "park_betula_below_threshold_ci.csv", index=False, encoding="utf-8-sig")
    print(res.round(3).to_string(index=False)); print(pd.DataFrame(rows).to_string(index=False)); print(b.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
