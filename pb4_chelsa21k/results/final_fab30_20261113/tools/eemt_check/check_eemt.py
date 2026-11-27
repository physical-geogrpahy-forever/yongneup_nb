"""EEMT 점검: 부호, 범위, 월 기후로 다시 계산한 값과의 차이, 영하인 달을 0으로 두지 않았을 때의 기여.

사용법: python check_eemt.py   (results/final_fab30_20261113 기준 상대 경로)
"""
from pathlib import Path
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[2]
CW = 4186.0
d = np.load(R / "FINAL_STATE_CUBE.npz")
for m in ("static", "dynamic"):
    e = np.where(d[f"{m}__land"], d[f"{m}__eemt_node"], np.nan)
    print(m, "EEMT 최소", round(float(np.nanmin(e)), 2), "최대", round(float(np.nanmax(e)), 2),
          "0 이하 격자", int(np.nansum(e <= 0)))
rows = []
for m in ("static", "dynamic"):
    f = pd.read_csv(R / f"reference_run/model_{m}/monthly_forcing_timeseries.csv", encoding="utf-8-sig")
    s = pd.read_csv(R / f"reference_run/model_{m}/summary_timeseries.csv", encoding="utf-8-sig").set_index("ka_bp")
    for ka, g in f.groupby("ka_bp"):
        g = g.sort_values("month")
        t, p, a = g.temperature_C_mean.values, g.precipitation_mm_mean.values, g.aet_mm_mean.values
        peff = np.maximum(p - a, 0.0)
        eppt = np.sum(np.maximum(t, 0.0) * CW * peff) / 1e6
        cold = np.sum(np.where(t < 0, t * CW * peff, 0.0)) / 1e6
        ebio = s.loc[ka, "mean_npp"] / 1000 / 0.5 * 22.0
        rows.append(dict(model=m, ka_bp=ka, eppt=eppt, ebio=ebio, recalc=eppt + ebio,
                         model_mean_eemt=s.loc[ka, "mean_eemt"], cold_months_unclipped=cold,
                         n_months_T_le_0=int((t <= 0).sum()), n_months_peff_neg=int((p - a < 0).sum())))
out = pd.DataFrame(rows)
out["diff"] = out.model_mean_eemt - out.recalc
out.to_csv(Path(__file__).with_name("eemt_check.csv"), index=False, encoding="utf-8-sig")
print(out.groupby("model")[["diff", "cold_months_unclipped"]].agg(["min", "max"]).round(2))
