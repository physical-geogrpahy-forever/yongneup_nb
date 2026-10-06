# PB4 stale-comment cleanup regression

- baseline SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- cleaned SHA-256: `796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86`
- 변경 범위: `biome4_backend.py`의 폐기된 PFT5/PFT6 climate-sieve 설명 주석 및 docstring만 정리
- 과학 계산식, 파라미터, 입력자료, 실행경로 변경 없음
- Jang 1% 검증: static 24/62, dynamic 55/62로 동일
- Jang 검증 124행의 범주값 및 NaN 패턴 동일, 수치 최대 절대차 (1.11\times10^{-16})
- 21 ka static/dynamic 시계열 422행 × 88열 비교: 범주값 및 NaN 패턴 동일
- 시계열 수치 최대 절대차 (2.84\times10^{-14}), 최악 열은 `mean_npp`
- 허용 절대오차 (1\times10^{-12})보다 충분히 작으며 과학적으로 동일한 결과
- 판정: **PASS_STRICT_NUMERIC**
