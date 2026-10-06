# PB4 stale-comment cleanup regression

- baseline SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- cleaned SHA-256: `796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86`
- 변경 범위: `biome4_backend.py`의 폐기된 PFT5/PFT6 climate-sieve 설명 주석 및 docstring만 정리
- 과학 계산식, 파라미터, 입력자료, 실행경로 변경 없음
- Jang 1% 검증: static 24/62, dynamic 55/62로 동일
- `FINAL_JANG1PCT_ROWS.csv` 전체 행 exact 동일
- `FINAL_AGB_21KA_TIMESERIES.csv` 대응 422행 전체, 모든 열 exact 동일
- 판정: **PASS_EXACT**
