# 120 ka BIOME4–Pelletier 시간간격 비교: 식생 비율

## 산출물
- biome4_area_ratio_timestep_comparison.png / .svg: BIOME4 생물군계별 면적 비율
- selected_pft_area_ratio_timestep_comparison.png / .svg: 선택 PFT별 격자 면적 비율
- vegetation_ratio_difference.png / .svg: 1 kyr와 0.1 kyr의 범주별 차이 및 시점별 전체 구성 차이
- vegetation_ratio_comparison_integer_ka.csv: 공통 정수 ka 시점별 범주 비율과 차이

## 비교 기준
- 120–0 ka BP의 공통 정수 시점 121개를 비교함.
- 0.1 kyr 실행 자료에서 정수 ka 시점만 추출했으며, 원래 0.1 kyr 자료는 변경하지 않음.
- 각 실행의 baseline을 대표로 사용함. scenario2는 BIOME4 및 선택 PFT 비율 시계열이 baseline과 모든 행에서 완전히 일치함.
- 유효 격자 236개, 20 m 격자 기준으로 각 셀의 면적 비율을 계산함.
- BIOME4에서 1 kyr 실행의 34 ka 시점은 한 셀의 생물군계 값이 미기록되어 면적 비율 합계가 99.5763%임. 이를 미분류/미기록 잔여 비율 0.4237%로 표시함.
- 선택 PFT 비율은 각 격자에서 선택된 optPFT 코드의 셀 점유율임. PFT 14는 별도 PFT가 아니라 목본·초본 공우점 판정 코드이며, PFT 0은 미선택 코드임.

## 요약
- BIOME4 및 선택 PFT 구성은 121개 시점 중 112개 시점에서 두 실행이 완전히 일치함.
- 차이가 발생한 시점: 119, 118, 117, 116, 115, 114, 34, 33, 21 ka.
- 범주별 최대 절대차: 0.8475%p.
- 시점별 범주 절대차 합계의 최대값: 3.3898%p (117 ka).
- 이 값은 면적 비율이며 식생 피복률이나 LAI 비율을 뜻하지 않음.
