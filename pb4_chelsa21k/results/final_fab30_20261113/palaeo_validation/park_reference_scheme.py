"""Park et al. (2021) 검증: 문헌 체계를 그대로 따른 처리.

분류군 배정: Ni et al. (2010, Palaeogeogr. Palaeoclimatol. Palaeoecol. 289: 44-61) 표 1의 다중 배정.
  자작나무속, 버드나무속 -> 아한대(BDE)와 온대(TBD) 냉량 낙엽 활엽교목 양쪽
  소나무속(아속 미분류) -> eurythermic evergreen needle-leaved tree -> 상록 침엽수(CON)
  나머지는 기존 대응표와 같음(전나무속 CON, 상록 참나무속과 감탕나무속 TBE, 벼과 GRS, 마황속 DWD).
화분 기준: 모든 그룹 0.5%(Prentice et al., 1996; Ni et al., 2010).
국지 분류군: 오리나무속(Jang et al., 2011: A. japonica가 습원과 주변에 서식), 산형과와 오이풀속
  (Jang et al., 2011; Park et al., 2021), 터리풀속은 기존대로 제외. 오리나무속을 Ni et al.(2010)처럼
  넣은 경우를 민감도로 함께 계산한다.
모델: 기존과 같음(유역 1%, 7격자; CON은 potential).
사용법: python park_reference_scheme.py <패키지 embedded_data 폴더>
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

E = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
R = HERE.parent / "reference_run"
G = ["TBD", "BDE", "CON", "TBE", "GRS", "DWD"]
T = np.round(np.arange(0.5, 3.21, 0.1), 1)
EXTRA = {"Bet": ["BDE", "TBD"], "Sal": ["BDE", "TBD"], "Pin": ["CON"], "Aln": ["BDE", "TBD"]}

cnt = pd.read_csv(E / "yongneup_park2021_ync_pollen_counts.csv", encoding="utf-8-sig")
tmap = pd.read_csv(E / "pft_taxon_map_yongneup.csv", encoding="utf-8-sig")[["taxon_code", "pft_group"]]
cnt = cnt.merge(tmap, on="taxon_code")
cnt["ka"] = cnt.age_cal_bp / 1000
model = {m: pd.read_csv(R / f"model_{m}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
         .set_index(["ka_bp", "pft_group"]).model_cells for m in ("static", "dynamic")}


def obs_pct(include_alnus: bool, scheme: str) -> pd.DataFrame:
    excl = {"EXCLUDE_LOCAL", "EXCLUDE_NONTERRESTRIAL"}
    c = cnt[cnt.park2021_group.isin(["A", "B"])].copy()
    keep = ~c.pft_group.isin(excl)
    if include_alnus:
        keep |= c.taxon_code == "Aln"
    c = c[keep]
    rows = []
    for t in T:
        w = c[(c.ka >= t - 0.05) & (c.ka < t + 0.05)]
        s = w["count"].sum()
        pct = {}
        for g in G:
            if scheme == "reference":
                own = w[(w.pft_group == g) & ~w.taxon_code.isin(EXTRA)]["count"].sum()
                extra = sum(w[w.taxon_code == k]["count"].sum() for k, gs in EXTRA.items() if g in gs)
                pct[g] = 100 * (own + extra) / s
            else:
                pct[g] = 100 * w[w.pft_group == g]["count"].sum() / s
        rows.append({"ka": t, "pollen_sum": int(s), **pct})
    return pd.DataFrame(rows).set_index("ka")


def score(p: pd.DataFrame, thr: dict) -> dict:
    out = {}
    for m, mc in model.items():
        tot = dict(TP=0, FP=0, FN=0, TN=0)
        per = {}
        for g in G:
            o = (p[g] >= thr[g]).values
            mo = np.array([mc[(t, g)] >= 7 for t in p.index])
            k = dict(TP=int((o & mo).sum()), FP=int((~o & mo).sum()), FN=int((o & ~mo).sum()), TN=int((~o & ~mo).sum()))
            per[g] = "{TP}/{FP}/{FN}/{TN}".format(**k)
            for a in tot:
                tot[a] += k[a]
        se, sp = tot["TP"] / (tot["TP"] + tot["FN"]), tot["TN"] / (tot["TN"] + tot["FP"])
        out[m] = {"accuracy": (tot["TP"] + tot["TN"]) / 168, "TSS": se + sp - 1, **tot, **per}
    return out


cur = {"TBD": 2, "BDE": 2, "CON": 1, "TBE": 5, "GRS": 2, "DWD": 5}
half = {g: 0.5 for g in G}
cases = {
    "현행 처리": (False, "current", cur),
    "문헌 체계(오리나무속 제외)": (False, "reference", half),
    "문헌 체계(오리나무속 포함)": (True, "reference", half),
}
rows = []
for name, (aln, sch, thr) in cases.items():
    for m, v in score(obs_pct(aln, sch), thr).items():
        rows.append({"case": name, "model": m, **v})
res = pd.DataFrame(rows)
res.round(3).to_csv(HERE / "park_reference_scheme.csv", index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250)
print(res.round(3).to_string(index=False))
p = obs_pct(False, "reference")
print(p.round(2).to_string())
