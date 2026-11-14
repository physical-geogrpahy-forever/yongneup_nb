"""Park et al. (2021) PFT 그룹별 일치 표와 민감도(TSS).

입력: reference_run/model_{static,dynamic}/pft_validation_per_output_time.csv
  (화분 비율과 출현 판정, 모델 격자 수가 시점별로 들어 있다)
판정: 모델 출현 = 유역 격자의 1% 이상(Jang et al., 2011 비교와 같음). 1개 격자 기준은 민감도로 제시.
비교 그룹: TBD, BDE, CON, TBE. 참고 그룹: GRS(습원 영향), DWD(장거리 화분).
사용법: python park_group_agreement.py [reference_run 폴더] [출력 폴더]
"""
from pathlib import Path
import math
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "reference_run"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
N_CELLS = 656
MAIN = ["TBD", "BDE", "CON", "TBE"]
REF = ["GRS", "DWD"]
LABEL = {"TBD": "온대 낙엽활엽수", "BDE": "아한대 낙엽수", "CON": "상록 침엽수", "TBE": "온대 상록활엽수",
         "GRS": "초본(참고)", "DWD": "건조지 목본(참고)"}


def load(model: str) -> pd.DataFrame:
    return pd.read_csv(RUN / f"model_{model}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")


def counts(v: pd.DataFrame, min_cells: int) -> tuple[int, int, int, int]:
    p = v.model_cells >= min_cells
    o = v.obs_present == 1
    return int((p & o).sum()), int((p & ~o).sum()), int((~p & o).sum()), int((~p & ~o).sum())


def tss(tp, fp, fn, tn):
    return tp / (tp + fn) + tn / (tn + fp) - 1 if (tp + fn) and (tn + fp) else float("nan")


def main() -> None:
    one_pct = math.ceil(0.01 * N_CELLS)
    data = {m: load(m) for m in ("static", "dynamic")}
    rows = []
    for g in MAIN + REF:
        r = {"group": g, "label": LABEL[g]}
        for m, v in data.items():
            tp, fp, fn, tn = counts(v[v.pft_group == g], one_pct)
            r.update({f"{m}_agree": tp + tn, f"{m}_TP": tp, f"{m}_FP": fp, f"{m}_FN": fn, f"{m}_TN": tn})
        r["n"] = int((data["static"].pft_group == g).sum())
        rows.append(r)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "park_group_agreement_1pct.csv", index=False, encoding="utf-8-sig")

    sens = []
    for name, groups in [("비교 4그룹", MAIN), ("4그룹+초본", MAIN + ["GRS"]), ("4그룹+건조지 목본", MAIN + ["DWD"]),
                         ("6그룹", MAIN + REF)]:
        for rule, mc in [("1%", one_pct), ("1개 격자", 1)]:
            r = {"groups": name, "presence_rule": rule}
            for m, v in data.items():
                r[f"{m}_TSS"] = round(tss(*counts(v[v.pft_group.isin(groups)], mc)), 3)
            sens.append(r)
    pd.DataFrame(sens).to_csv(OUT / "park_tss_sensitivity.csv", index=False, encoding="utf-8-sig")
    print(table[["label", "n", "static_agree", "dynamic_agree"]].to_string(index=False))
    print(pd.DataFrame(sens).to_string(index=False))


if __name__ == "__main__":
    main()
