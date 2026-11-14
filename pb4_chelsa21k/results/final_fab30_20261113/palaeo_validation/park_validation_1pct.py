"""Park et al. (2021) PFT 검증: 유역 1% 출현 기준과 민감도.

입력: reference_run/model_{static,dynamic}/pft_validation_per_output_time.csv
      (패키지 pft_validation.py가 쓴 시점별 화분 비율, 그룹 기준 판정, 모델 격자 수)
본 판정: 화분은 그룹별 기준(표 4), 모델은 유역 656격자의 1%(7격자) 이상.
민감도: 모델 기준 1개 격자, 1-5%; 화분 기준 0.5-10%를 모든 그룹에 동일 적용.
사용법: python park_validation_1pct.py [reference_run 폴더] [출력 폴더]
"""
from pathlib import Path
import math
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "reference_run"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
N_CELLS = 656
GROUPS = ["TBD", "BDE", "CON", "TBE", "GRS", "DWD"]


def scores(v: pd.DataFrame, min_cells: int, obs_thr=None) -> dict:
    obs = (v.obs_pct >= obs_thr) if obs_thr is not None else (v.obs_present == 1)
    mod = v.model_cells >= min_cells
    tp, fp = int((mod & obs).sum()), int((mod & ~obs).sum())
    fn, tn = int((~mod & obs).sum()), int((~mod & ~obs).sum())
    sens = tp / (tp + fn) if tp + fn else float("nan")
    spec = tn / (tn + fp) if tn + fp else float("nan")
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "accuracy": (tp + tn) / len(v),
            "sensitivity": sens, "specificity": spec, "TSS": sens + spec - 1}


def main() -> None:
    data = {m: pd.read_csv(RUN / f"model_{m}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
            for m in ("static", "dynamic")}
    one_pct = math.ceil(0.01 * N_CELLS)

    rows = []
    for m, v in data.items():
        for g in GROUPS + ["ALL"]:
            sub = v if g == "ALL" else v[v.pft_group == g]
            rows.append({"model": m, "group": g, **scores(sub, one_pct)})
    main_tab = pd.DataFrame(rows)
    main_tab.round(3).to_csv(OUT / "park_validation_1pct.csv", index=False, encoding="utf-8-sig")

    sens = []
    for rule, mc in [("1 cell", 1)] + [(f"{p}%", math.ceil(p / 100 * N_CELLS)) for p in (1, 2, 3, 4, 5)]:
        for m, v in data.items():
            sens.append({"model_rule": rule, "model_min_cells": mc, "pollen_rule": "group (table 4)", "model": m,
                         **scores(v, mc)})
    for thr in (0.5, 1, 2, 5, 10):
        for m, v in data.items():
            sens.append({"model_rule": "1%", "model_min_cells": one_pct, "pollen_rule": f"{thr}% all groups",
                         "model": m, **scores(v, one_pct, thr)})
    pd.DataFrame(sens).round(3).to_csv(OUT / "park_validation_sensitivity.csv", index=False, encoding="utf-8-sig")
    print(main_tab[main_tab.group == "ALL"].round(3).to_string(index=False))
    print(pd.DataFrame(sens)[["model_rule", "pollen_rule", "model", "accuracy", "TSS"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
