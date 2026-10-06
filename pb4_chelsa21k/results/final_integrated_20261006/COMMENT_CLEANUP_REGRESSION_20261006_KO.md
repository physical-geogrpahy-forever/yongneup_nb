# PB4 stale-comment cleanup regression

- baseline SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- cleaned SHA-256: `796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86`
- 변경 범위: `biome4_backend.py`의 폐기된 PFT5/PFT6 climate-sieve 설명 주석 및 docstring만 정리
- 과학 계산식, 파라미터, 입력자료, 실행경로 변경 없음
- 21.0-0.0 ka BP, 0.1 kyr 간격 static/dynamic 전체 재실행 완료
- Jang 1% 검증: static 24/62, dynamic 55/62로 동일
- Jang 124개 검증행의 정수 및 범주값은 동일하고, 실수 최대 절대차는 `1.1102230246251565e-16`
- `FINAL_AGB_21KA_TIMESERIES.csv` 대응 422행 × 88열 전체 비교
- 고도, 토심, 경사, NPP, EEMT, 식생분류, AGB*, PFT 진단, geomorph substep 진단을 포함한 실수 최대 절대차는 `2.842170943040401e-14`이며 해당 열은 `mean_npp`
- NaN 패턴과 범주형 값은 exact 동일
- 허용 절대오차 `1e-12`보다 35배 이상 작음
- 판정: **PASS_STRICT_NUMERIC**
