"""모델 식생을 Betula 화분 비율로 바꿔 Park et al. (2021) 관측과 직접 비교(화분 순방향 모의).

분산 모형: Prentice (1985), Sugita (1993, 1994)의 Prentice-Sugita 모형.
  b = 4 vg / (n u sqrt(pi) Cz), gamma = n/2, n = 0.25, Cz = 0.12, u = 3 m/s(2, 4 민감도)
  거리 z 밖에서 오는 화분 비율 = exp(-b z^gamma)
  격자(900 m2) 가중치 = A b gamma z^(gamma-1) exp(-b z^gamma) / (2 pi z)
습지 반경 R = 48.8 m(면적 7,490 m2)보다 가까운 격자는 습지 표면으로 보고 뺀다.
유역 밖(배경) 기여 = exp(-b R^gamma) - 유역 격자 가중치 합.
BIOME4 우점 PFT가 격자 전체를 덮는다고 가정: PFT7 -> Betula(BDE), PFT4 -> 온대 낙엽활엽수(TBD).
RPP와 낙하속도(vg): Mazier et al. (2012) Betula 2.42(0.024 m/s), Quercus 5.83(0.035), Carpinus 2.106(0.042);
Li et al. (2018) 중국 Betula 12.5. TBD 화분은 Quercus 65%, Carpinus 21%로 구성되어 Quercus를 기본값으로 쓴다.
관측 비율 = BDE 알 수 / (BDE + TBD 알 수), 95% 신뢰구간은 Clopper-Pearson.
시나리오: 배경 0(유역 식생만), 배경 = 유역 평균 조성, 관측을 맞추는 데 필요한 배경 Betula 피도(Betula + TBD = 90% 가정).
사용법: python park_betula_forward.py <스냅숏이 있는 모의 결과 폴더> [출력 폴더]
"""
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd
from scipy.stats import beta, spearmanr

HERE = Path(__file__).resolve().parent
RUN = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE
CORE = (123245.19, 624269.79)
R_BOG = math.sqrt(7490 / math.pi)
N_EXP, CZ = 0.25, 0.12
GAM = N_EXP / 2
VG_B = 0.024
RPP_SETS = {"EU_Quercus": (2.42, 5.83, 0.035), "EU_Carpinus": (2.42, 2.106, 0.042), "CN_Betula_EU_Quercus": (12.5, 5.83, 0.035)}
BG_TOTAL = 0.9


def b_coef(vg: float, u: float) -> float:
    return 4 * vg / (N_EXP * u * math.sqrt(math.pi) * CZ)


def loading(d: np.ndarray, vg: float, u: float) -> tuple[np.ndarray, float]:
    bb = b_coef(vg, u)
    w = np.where(d > R_BOG, 900 * bb * GAM * d ** (GAM - 1) * np.exp(-bb * d ** GAM) / (2 * np.pi * d), 0.0)
    return w, math.exp(-bb * R_BOG ** GAM)


def main() -> None:
    o = pd.read_csv(RUN / "model_dynamic" / "pft_validation_per_output_time.csv", encoding="utf-8-sig")
    o["k"] = np.rint(o.obs_pct * o.terrestrial_sum / 100).astype(int)
    kB = o[o.pft_group == "BDE"].set_index("ka_bp").k
    kT = o[o.pft_group == "TBD"].set_index("ka_bp").k
    rows, summ = [], []
    for u in (2.0, 3.0, 4.0):
        for name, (rB, rT, vgT) in RPP_SETS.items():
            for m in ("static", "dynamic"):
                for ka in sorted(kB.index):
                    cc = pd.read_csv(RUN / f"model_{m}" / f"snapshot_{ka:g}ka" / "cell_values.csv", encoding="utf-8-sig")
                    d = np.hypot(cc.x - CORE[0], cc.y - CORE[1]).values
                    opt = np.rint(cc.optpft.fillna(-1)).astype(int).values
                    wB, tB = loading(d, VG_B, u)
                    wT, tT = loading(d, vgT, u)
                    LB, LT = wB[opt == 7].sum(), wT[opt == 4].sum()
                    OB, OT = tB - wB.sum(), tT - wT.sum()
                    sB, sT = (opt == 7).mean(), (opt == 4).mean()
                    b_, t_ = int(kB[ka]), int(kT[ka])
                    obs = b_ / (b_ + t_)
                    q = obs / (1 - obs)
                    f_req = (q * rT * (LT + BG_TOTAL * OT) - rB * LB) / (rB * OB + q * rT * OT)

                    def ratio(fB: float, fT: float) -> float:
                        pb, pt = rB * (LB + fB * OB), rT * (LT + fT * OT)
                        return pb / (pb + pt)

                    rows.append({"wind_ms": u, "rpp_set": name, "model": m, "ka_bp": ka, "betula_cells": int((opt == 7).sum()),
                                 "basin_share_of_betula_loading": wB.sum() / tB,
                                 "obs_ratio": obs, "obs_lo": beta.ppf(0.025, b_, t_ + 1), "obs_hi": beta.ppf(0.975, b_ + 1, t_),
                                 "pred_local_only": ratio(0, 0), "pred_bg_basin": ratio(sB, sT),
                                 "required_bg_betula_cover": f_req})
            w = pd.DataFrame([r for r in rows if r["wind_ms"] == u and r["rpp_set"] == name])
            for m in ("static", "dynamic"):
                x = w[w.model == m]
                ins = lambda p: int(((p >= x.obs_lo) & (p <= x.obs_hi)).sum())
                rho = spearmanr(x.pred_local_only, x.obs_ratio).statistic if x.betula_cells.std() > 0 else float("nan")
                summ.append({"wind_ms": u, "rpp_set": name, "model": m, "windows": len(x),
                             "basin_share_of_betula_loading": x.basin_share_of_betula_loading.mean(),
                             "obs_ratio_mean": x.obs_ratio.mean(),
                             "pred_local_only_mean": x.pred_local_only.mean(), "local_only_in_ci": ins(x.pred_local_only),
                             "pred_bg_basin_mean": x.pred_bg_basin.mean(), "bg_basin_in_ci": ins(x.pred_bg_basin),
                             "share_of_obs_explained_by_basin": x.pred_local_only.mean() / x.obs_ratio.mean(),
                             "required_bg_betula_mean": x.required_bg_betula_cover.mean(),
                             "required_bg_betula_min": x.required_bg_betula_cover.min(),
                             "required_bg_betula_max": x.required_bg_betula_cover.max(),
                             "spearman_local_vs_obs": rho})
    pd.DataFrame(rows).round(4).to_csv(OUT / "park_betula_forward_windows.csv", index=False, encoding="utf-8-sig")
    s = pd.DataFrame(summ)
    s.round(4).to_csv(OUT / "park_betula_forward_summary.csv", index=False, encoding="utf-8-sig")
    print(s.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
