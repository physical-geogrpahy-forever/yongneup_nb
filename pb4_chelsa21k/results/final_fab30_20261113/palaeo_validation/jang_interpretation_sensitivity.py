"""Jang et al. (2011) 검증의 해석과 연대 민감도.

입력: reference_run/validation_per_output_time_static_dynamic.csv (최종 실행의 Jang 시점별 판정)
1) 3대(3,400-390 cal yr BP, 95_03)의 기대 식생: 활엽수림(Jang 대 구분), 3,400-1,300 혼효림 후 활엽수림(Jang 고찰),
   전체 혼효림(정상부 해석), 활엽수림 또는 혼효림
2) 화분대 경계(5.9, 4.8, 3.4, 0.39 ka) 전후 0.1-0.3 kyr 제외
판정은 모두 유역 식생 격자의 1% 이상(본 검증과 같음).
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "reference_run" / "validation_per_output_time_static_dynamic.csv"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
COL = {"broadleaf": "basin_count_broadleaf", "mixed": "basin_count_mixed"}


def present(rows: pd.DataFrame, cls: str) -> pd.Series:
    return rows[COL[cls]] >= 0.01 * rows.valid_basin_cell_count


def main() -> None:
    v = pd.read_csv(SRC, encoding="utf-8-sig")
    rows = []
    for case in ("정적모델", "동적모델"):
        x = v[v.case_label == case]
        z3 = x.record_id == "95_03"
        early = z3 & (x.model_ka_bp >= 1.3)
        late = z3 & (x.model_ka_bp < 1.3)
        base = int(x[~z3].correct.sum())
        res = {
            "3대 활엽수림 (Jang 대 구분, 본 검증)": base + int(x[z3].correct.sum()),
            "3,400-1,300 혼효림, 이후 활엽수림 (Jang 고찰)": base + int(present(x[early], "mixed").sum()) + int(x[late].correct.sum()),
            "3대 혼효림 (정상부 해석)": base + int(present(x[z3], "mixed").sum()),
            "3대 활엽수림 또는 혼효림": base + int((present(x[z3], "broadleaf") | present(x[z3], "mixed")).sum()),
        }
        bounds = np.array([5.9, 4.8, 3.4, 0.39])
        dist = np.min(np.abs(x.model_ka_bp.values[:, None] - bounds[None, :]), axis=1)
        for buf in (0.1, 0.2, 0.3):
            keep = dist > buf + 1e-9
            res[f"경계 ±{buf} kyr 제외 (n={int(keep.sum())})"] = int(x[keep].correct.sum())
        for k, val in res.items():
            rows.append({"case": case, "scenario": k, "correct": val})
    out = pd.DataFrame(rows).pivot(index="scenario", columns="case", values="correct")[["정적모델", "동적모델"]]
    out.to_csv(OUT / "jang_interpretation_sensitivity.csv", encoding="utf-8-sig")
    print(out.to_string())


if __name__ == "__main__":
    main()
