"""Park et al. (2021) 검증: 문헌 체계를 그대로 따른 처리.

분류군 배정: Ni et al. (2010, Palaeogeogr. Palaeoclimatol. Palaeoecol. 289: 44-61) 표 1.
  한 분류군이 여러 PFT에 배정되면 그 화분을 해당 그룹 모두에 더한다(생물군계 판정의 다중 배정과 같음).
  BIOME4 PFT와의 대응(교목 PFT만 사용):
    TBD(PFT4) <- te-ft.cd.mb.t, te-fa.cd.mb.t, te-fi.cd.mb.t, wt.cd.mb.t
    BDE(PFT7) <- bo.cd.mb.t
    CON(PFT5, 6) <- bo.e.n.t, c-te.e.n.t, te.e.n.t, eu.e.n.t, wt.e.n.t
    TBE(PFT3) <- wt.e.sb.t, wt.e.mb.t
    GRS(PFT8) <- g
    DWD(PFT10) <- ft.ml.lhs (마황속)
  교목 PFT가 없고 벼과와 마황속도 아닌 분류군(진달래과, 가막살나무속, 포도속, 쑥속 등)은 채점하는 여섯 그룹에 해당하지 않는다.
화분 기준: 모든 그룹 0.5%(Prentice et al., 1996; Ni et al., 2010).
화분합: Park의 목본(A)+초본(B). 습원 국지 분류군(오리나무속: Jang et al., 2011; 산형과, 오이풀속:
  Jang et al., 2011, Park et al., 2021)과 수생, 사초과, 포자(Ni et al., 2010)는 뺀다. 터리풀속은 제외 근거가
  없어 화분합에 넣는다. 오리나무속을 넣은 경우와 모델, 화분 기준을 바꾼 경우를 민감도로 계산한다.
모델: 유역 식생 격자의 1%(7격자) 이상. CON은 생육 가능(potential), 나머지는 우점 PFT(optpft).
사용법: python park_reference_scheme.py <패키지 embedded_data 폴더> [모의 결과 폴더(기본 ../reference_run)] [출력 접미사]
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

E = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
R = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "reference_run"
SUFFIX = sys.argv[3] if len(sys.argv) > 3 else ""
import math
N_CELLS = int(pd.read_csv(R / "model_static" / "pft_model_cells_per_output_time.csv", encoding="utf-8-sig").n_cells.max())
PCT = lambda f: math.ceil(f / 100 * N_CELLS)
G = ["TBD", "BDE", "CON", "TBE", "GRS", "DWD"]
T = np.round(np.arange(0.5, 3.21, 0.1), 1)

# Ni et al. (2010) 표 1의 교목 PFT 배정을 채점 그룹으로 옮긴 것
NI2010 = {
    "Pin": ["CON"], "Abi": ["CON"], "Pic": ["CON"], "Tsu": ["CON"], "Cup": ["CON"],
    "Pla": ["TBD"], "Car": ["TBD"], "Ace": ["TBD"], "QueL": ["TBD"], "Fra": ["TBD"], "Jug": ["TBD"],
    "Til": ["TBD"], "Cas": ["TBD"], "Ulm": ["TBD"], "Cel": ["TBD"], "Fag": ["TBD"], "Cor": ["TBD"],
    "Mor": ["TBD"], "Carya": ["TBD"], "Rhu": ["TBD"], "Lon": ["TBD"], "Sam": ["TBD"], "Ros": ["TBD"],
    "Euo": ["TBD", "TBE"], "Rha": ["TBD", "TBE"], "Myr": ["TBD", "TBE"],
    "Bet": ["BDE", "TBD"], "Sal": ["BDE", "TBD"], "Aln": ["BDE", "TBD"],
    "QueC": ["TBE"], "Ile": ["TBE"], "Bux": ["TBE"], "Cam": ["TBE"],
    "Poa": ["GRS"], "Poa37": ["GRS"], "Eph": ["DWD"],
    # 교목 PFT가 없는 분류군: Vit(덩굴), Vib, Eri(관목), 초본
}

cnt = pd.read_csv(E / "yongneup_park2021_ync_pollen_counts.csv", encoding="utf-8-sig")
tmap = pd.read_csv(E / "pft_taxon_map_yongneup.csv", encoding="utf-8-sig")[["taxon_code", "pft_group"]]
cnt = cnt.merge(tmap, on="taxon_code")
cnt["ka"] = cnt.age_cal_bp / 1000
model = {m: pd.read_csv(R / f"model_{m}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
         .set_index(["ka_bp", "pft_group"]).model_cells for m in ("static", "dynamic")}


def obs_pct(include_alnus: bool, scheme: str) -> pd.DataFrame:
    c = cnt[cnt.park2021_group.isin(["A", "B"])].copy()
    keep = ~c.pft_group.isin(["EXCLUDE_LOCAL", "EXCLUDE_NONTERRESTRIAL"])
    if scheme == "reference":
        keep |= c.taxon_code == "Fil"
    if include_alnus:
        keep |= c.taxon_code == "Aln"
    c = c[keep]
    rows = []
    for t in T:
        w = c[(c.ka >= t - 0.05) & (c.ka < t + 0.05)]
        s = w["count"].sum()
        by_taxon = w.groupby("taxon_code")["count"].sum()
        pct = {}
        for g in G:
            if scheme == "reference":
                k = sum(n for tx, n in by_taxon.items() if g in NI2010.get(tx, []))
            else:
                k = w[w.pft_group == g]["count"].sum()
            pct[g] = 100 * k / s
        rows.append({"ka": t, "pollen_sum": int(s), **pct})
    return pd.DataFrame(rows).set_index("ka")


def score(p: pd.DataFrame, thr: dict, min_cells: int = None) -> dict:
    min_cells = PCT(1) if min_cells is None else min_cells
    out = {}
    for m, mc in model.items():
        tot = dict(TP=0, FP=0, FN=0, TN=0)
        per = {}
        for g in G:
            o = (p[g] >= thr[g]).values
            mo = np.array([mc[(t, g)] >= min_cells for t in p.index])
            k = dict(TP=int((o & mo).sum()), FP=int((~o & mo).sum()), FN=int((o & ~mo).sum()), TN=int((~o & ~mo).sum()))
            per[g] = "{TP}/{FP}/{FN}/{TN}".format(**k)
            for a in tot:
                tot[a] += k[a]
        se, sp = tot["TP"] / (tot["TP"] + tot["FN"]), tot["TN"] / (tot["TN"] + tot["FP"])
        out[m] = {"accuracy": (tot["TP"] + tot["TN"]) / 168, "sensitivity": se, "specificity": sp,
                  "TSS": se + sp - 1, **tot, **per}
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
res.round(3).to_csv(HERE / f"park_reference_scheme{SUFFIX}.csv", index=False, encoding="utf-8-sig")
p = obs_pct(False, "reference")
p.round(3).to_csv(HERE / f"park_reference_scheme_obs_pct{SUFFIX}.csv", encoding="utf-8-sig")
sens = []
for rule, mc in [("1개 격자", 1)] + [(f"{k}%", PCT(k)) for k in (1, 2, 3, 4, 5)]:
    for m, v in score(p, half, mc).items():
        sens.append({"model_rule": rule, "pollen_rule": "0.5%", "model": m, **v})
for thr in (0.5, 1, 2, 5, 10):
    for m, v in score(p, {g: thr for g in G}).items():
        sens.append({"model_rule": "1%", "pollen_rule": f"{thr}%", "model": m, **v})
sens = pd.DataFrame(sens)
sens.round(3).to_csv(HERE / f"park_reference_scheme_sensitivity{SUFFIX}.csv", index=False, encoding="utf-8-sig")
print(sens[["model_rule", "pollen_rule", "model", "accuracy", "TSS", "BDE", "TBE", "GRS", "CON"]].round(3).to_string(index=False))
pd.set_option("display.width", 250)
print(res.round(3).to_string(index=False))
print(p.round(2).to_string())
