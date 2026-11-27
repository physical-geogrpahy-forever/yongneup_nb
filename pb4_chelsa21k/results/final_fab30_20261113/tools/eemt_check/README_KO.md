# EEMT 점검 (2026-11-27)

구현(`pb4studio/climate.py`, `compute_eemt_and_agb`)

- EPPT = Σ c_w max(T_m, 0) max(P_m − AET_m, 0), c_w = 4,186 J/kg/K, P와 AET는 mm(= kg/m²), MJ로 환산.
- EBIO = max(NPP, 0)[gC/m²/yr] / 1000 / 0.5 × 22 MJ/kg.
- 근거: Pelletier et al. (2013) 식 1, 2(EPPT = ΔT c_w Peff, Peff = PPT − ET, EBIO = NPP h_BIO). Rasmussen & Tabor (2007): 유효강수는 0 °C에서 그 달 평균기온까지 데워지고, 유효강수가 음수인 달은 0. Pelletier & Rasmussen (2009): 월 단위 EEMT에서는 영하에 내린 강수가 풍화에 기여하지 않는다.

결과 (`check_eemt.py`, `eemt_check.csv`)

- 격자 EEMT: 정적 60.7~100.6, 동적 60.3~107.1 MJ/m²/yr. 0 이하인 격자 없음.
- 월 기후와 유역 평균 AET, NPP로 다시 계산한 값: 정적 모델은 모든 시점에서 일치(차 0.00). 동적 모델의 0~1.6 MJ 차이는 기반암 노출 격자 때문이다. 12 ka(노출 격자 41개)에서 식생 격자 평균 EEMT 75.39는 월 기후와 식생 격자 평균 AET, NPP로 다시 계산한 75.39와 같고, 노출 격자 EEMT 83.93은 AET 0으로 계산한 EPPT 83.93과 같다.
- 기반암 노출 격자는 AET가 0이라 강수 전체가 유효강수가 되어 EEMT가 식생 격자보다 약 8.5 MJ 높다(P0 약 1.3배).
- 유효강수가 음수인 달은 없다. 영하인 달은 시점마다 4~5개(11-3월).
- 영하인 달을 0으로 두지 않으면 EPPT가 4.7~10.5 MJ 줄어든다(유역 평균 EEMT 최소 51.5로 여전히 양수). 지금 구현은 이 음의 기여를 넣지 않는다.
- 물수지 결빙 기준을 0 °C로 바꾼 재실행(`../../sensitivity/frozen_soil_0C/`)에서도 EEMT는 소수 셋째 자리까지 같다.
