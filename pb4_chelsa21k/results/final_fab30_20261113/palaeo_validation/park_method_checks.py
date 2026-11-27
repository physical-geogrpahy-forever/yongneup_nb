"""Park 검증 처리 점검: 화분합과 분류군 배정을 하나씩 바꾸었을 때의 결과.

사용법: python park_method_checks.py <패키지 embedded_data 폴더>
"""
import sys, math
from pathlib import Path
import numpy as np, pandas as pd

E = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; R = HERE.parent / "reference_run"
G = ["TBD", "BDE", "CON", "TBE", "GRS", "DWD"]
T = np.round(np.arange(0.5, 3.21, 0.1), 1)
NI = {
    "Pin": ["CON"], "Abi": ["CON"], "Pic": ["CON"], "Tsu": ["CON"], "Cup": ["CON"],
    "Pla": ["TBD"], "Car": ["TBD"], "Ace": ["TBD"], "QueL": ["TBD"], "Fra": ["TBD"], "Jug": ["TBD"],
    "Til": ["TBD"], "Cas": ["TBD"], "Ulm": ["TBD"], "Cel": ["TBD"], "Fag": ["TBD"], "Cor": ["TBD"],
    "Mor": ["TBD"], "Carya": ["TBD"], "Rhu": ["TBD"], "Lon": ["TBD"], "Sam": ["TBD"], "Ros": ["TBD"],
    "Euo": ["TBD", "TBE"], "Rha": ["TBD", "TBE"], "Myr": ["TBD", "TBE"],
    "Bet": ["BDE", "TBD"], "Sal": ["BDE", "TBD"], "Aln": ["BDE", "TBD"],
    "QueC": ["TBE"], "Ile": ["TBE"], "Bux": ["TBE"], "Cam": ["TBE"],
    "Poa": ["GRS"], "Poa37": ["GRS"], "Eph": ["DWD"],
}
cnt = pd.read_csv(E / "yongneup_park2021_ync_pollen_counts.csv", encoding="utf-8-sig")
tmap = pd.read_csv(E / "pft_taxon_map_yongneup.csv", encoding="utf-8-sig")[["taxon_code", "pft_group"]]
cnt = cnt.merge(tmap, on="taxon_code"); cnt["ka"] = cnt.age_cal_bp / 1000
N = int(pd.read_csv(R / "model_static" / "pft_model_cells_per_output_time.csv", encoding="utf-8-sig").n_cells.max())
MC = math.ceil(0.01 * N)
model = {m: pd.read_csv(R / f"model_{m}" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
         .set_index(["ka_bp", "pft_group"]).model_cells for m in ("static", "dynamic")}


def obs(groups=("A", "B"), drop=("Aln", "Api", "San"), assign=NI):
    c = cnt[cnt.park2021_group.isin(groups) & ~cnt.taxon_code.isin(drop)]
    rows = []
    for t in T:
        w = c[(c.ka >= t - 0.05) & (c.ka < t + 0.05)]
        s = w["count"].sum(); bt = w.groupby("taxon_code")["count"].sum()
        rows.append({"ka": t, "sum": s, **{g: 100 * sum(n for tx, n in bt.items() if g in assign.get(tx, [])) / s for g in G}})
    return pd.DataFrame(rows).set_index("ka")


def score(p, thr=0.5):
    out = {}
    for m, mc in model.items():
        k = dict(TP=0, FP=0, FN=0, TN=0); per = {}
        for g in G:
            o = (p[g] >= thr).values; mo = np.array([mc[(t, g)] >= MC for t in p.index])
            d = dict(TP=int((o & mo).sum()), FP=int((~o & mo).sum()), FN=int((o & ~mo).sum()), TN=int((~o & ~mo).sum()))
            per[g] = "{TP}/{FP}/{FN}/{TN}".format(**d)
            for a in k: k[a] += d[a]
        se, sp = k["TP"] / (k["TP"] + k["FN"]), k["TN"] / (k["TN"] + k["FP"])
        out[m] = dict(acc=round((k["TP"] + k["TN"]) / 168, 3), TSS=round(se + sp - 1, 3), BDE=per["BDE"], GRS=per["GRS"], TBE=per["TBE"])
    return out


nb = {k: (["TBD"] if k in ("Bet", "Sal", "Aln") else v) for k, v in NI.items()}
bet_only = {k: (["TBD"] if k == "Sal" else v) for k, v in NI.items()}
spore_groups = ("A", "B", "F")
cases = {
    "기준(문헌 체계)": obs(),
    "포자를 화분합에 포함": obs(groups=spore_groups),
    "터리풀속도 제외": obs(drop=("Aln", "Api", "San", "Fil")),
    "산형과, 오이풀속 포함": obs(drop=("Aln",)),
    "버드나무속을 온대 낙엽수에만 배정": obs(assign=bet_only),
    "자작나무속, 버드나무속을 온대 낙엽수에만 배정": obs(assign=nb),
}
rows = []
for name, p in cases.items():
    for m, v in score(p).items():
        rows.append({"case": name, "model": m, **v})
df = pd.DataFrame(rows)
df.to_csv(HERE / "park_method_checks.csv", index=False, encoding="utf-8-sig")
pd.set_option("display.width", 200)
print(df.to_string(index=False))
p = obs()
low = p[p["sum"] < 300]
print("\n화분합 300 미만 시점:", ", ".join(f"{k} ka({int(v)})" for k, v in low["sum"].items()))
print("BDE 화분 수(자작나무속+버드나무속) 최소:", int(min(cnt[(cnt.ka >= t - .05) & (cnt.ka < t + .05) & cnt.taxon_code.isin(['Bet', 'Sal'])]['count'].sum() for t in T)))
