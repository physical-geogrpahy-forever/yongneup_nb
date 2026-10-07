# 다음 채팅 인계문: 용늪 VeSLEM / PB4Studio U008 결과 작성 및 셀 단위 식생 원인 분석

작성일: 2026-10-07

## 1. 저장소와 우선 확인 위치

저장소:
`physical-geogrpahy-forever/yongneup_nb`

작업 브랜치:
`main`

이 인계문 작성 직전 확인한 main HEAD:
`e943ac6e0eaf3df1e38afda5455b48159aee0bb6`

다른 채팅이 동시에 방법론을 갱신할 수 있으므로 다음 채팅에서는 반드시 main HEAD를 다시 확인한다. 위 SHA를 최신으로 고정해서 사용하지 않는다.

가장 먼저 읽을 파일:
1. `pb4_chelsa21k/manuscript/NEXT_CHAT_HANDOFF_20261007_KO.md`
2. `diagnostics/vegetation_cellwise/PB4_VEGETATION_CELLWISE_HANDOFF.md`
3. `pb4_chelsa21k/manuscript/FINAL_METHODS_MANUSCRIPT_FIRST_PRINCIPLES_20261007_KO.md`

방법론 원문 대조용:
- `pb4_chelsa21k/manuscript/FINAL_METHODS_CANONICAL_20261006_KO.md`
- `pb4_chelsa21k/manuscript/FINAL_METHODS_SOURCE_AUDIT_20261006_KO.md`
- `pb4_chelsa21k/PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md`

최종 모델 패키지:
- `pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K.zip`
- 해시 목록: `pb4_chelsa21k/SHA256SUMS.txt`

## 2. 최종 모델 기준

최종 분석 기준 버전:
`PB4Studio v6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`

공간해상도 20 m, 유효 셀 298개, 21.0 ka부터 0.0 ka까지 0.1 kyr 간격 211시점이다.

지역 융기율:
`U = 0.08 m/kyr = 80 mm/kyr`

21 kyr 동안 단순 누적 융기량은 1.68 m이다.

CHELSA-TraCE21k 기후를 사용하며 BIOME4 식생과 Pelletier 계열 지형발달이 결합되어 있다. 방법론 세부식은 위 FIRST_PRINCIPLES 문서를 우선한다.

## 3. 현재 논문 작성 단계

현재는 결과 절을 작성 중이다. 평균 고도, 평균 토심, 식생유형의 시간 및 공간 변화 문장을 최신 U008 결과로 교체하고 있다.

작성 규칙:
- 그래프를 눈대중으로 읽지 않는다.
- 수치는 CSV 또는 실제 재실행 결과를 직접 확인한다.
- 결과와 해석을 분리한다.
- 결과 문단에서는 관측된 수치와 공간패턴만 쓴다.
- 해석 문단에서는 그 원인을 모델 내부 변수와 과정으로 확인한 뒤 쓴다.
- 이전 120 ka 버전, 0.2 mm/yr 융기율, 100/50/10/1 ka 지도 서술은 폐기한다.
- 현재 지도 비교 시점은 21, 15, 10, 5, 0 ka이다.
- 연구문체에서 가운뎃점 사용을 피한다.
- 메타 문장, 예를 들어 "이전 버전과 달리", "재보정하지 않았다" 등은 논문 본문에 넣지 않는다.

## 4. 최종 U008 핵심 수치

### 평균 고도
동적모델:
- 21 ka: 1163.077482 m
- 약 19 ka 부근까지 소폭 하강
- 0 ka: 1163.845503 m
- 순증가: +0.768020 m

정적모델 평균 고도는 약 1163.077482 m로 일정하다.

해석 시 1.68 m의 누적 융기와 0.77 m의 순고도 증가 차이를 곧바로 "침식량"으로 등치하지 않는다. 사면 물질이동, 하천 침식, 지형 재분배가 융기 효과를 상당 부분 상쇄했다고만 해석한다.

### 평균 토심
동적모델:
- 21 ka: 1.940388 m
- 최저: 16.4 ka, 1.64762 m
- 15 ka: 1.68781 m
- 12 ka: 1.80656 m
- 10 ka: 1.90910 m
- 9 ka: 1.96274 m
- 6 ka: 2.15388 m
- 3 ka: 2.35579 m
- 0 ka: 2.499603 m
- 21 ka 대비 0 ka 순증가: +0.55922 m

정적모델은 약 1.94039 m로 일정하다.

초기 토심 감소는 토양생성보다 제거가 우세한 시기, 이후 증가는 토양생성과 사면 내 물질 재분배가 누적된 결과로 해석한다. 모델 출력이 직접 보장하지 않는 "퇴적"을 과도하게 단정하지 않는다.

### NPP
대표값:
- 18 ka: dynamic 280.3, static 299.1
- 15 ka: 333.8 vs 351.0
- 12 ka: 361.3 vs 393.0
- 9 ka: 434.1 vs 444.2
- 6 ka: 464.4 vs 468.0
- 3 ka: 526.4 vs 528.0
- 0 ka: 611.2 vs 615.0

약 12.1 ka에서 dynamic 355.8, static 388.6, 차이 약 -32.9가 확인됐다. 정확한 문장 작성 시 반드시 원자료를 다시 읽는다.

## 5. 현재 식생 결과의 큰 흐름

우점식생 변화는 정적모델과 동적모델에서 전반적으로 비슷하게 나타나지만 세부 전환시점과 국지적 구성은 다르다.

현재 확인된 주요 우점 구간:
- 21.0-18.3 ka: 침엽수림 우점
- 전환기를 거쳐 17.9-16.0 ka: 다시 침엽수림 우점
- 15.9-15.3 ka: 혼효림 우점
- 15.2-4.4 ka: 활엽수림 우점
- 3.9-0.1 ka: 혼효림 우점
- 0 ka: 활엽수림

이 구간은 최종 결과 문장 작성 전에 211시점 자료로 다시 검산한다. "거의 동일"이라는 표현보다 "전반적으로 비슷하게 나타났다"를 사용한다.

핵심은 우점식생 자체보다 동적모델에서 지형발달 때문에 생기는 국지적 차이를 설명하는 것이다.

## 6. 4 ka 부근 활엽수림과 혼효림 차이: 셀 단위 검증 완료

진단자료 위치:
`diagnostics/vegetation_cellwise/`

핵심 파일:
- `PB4_4p3ka_broadleaf_cells_static_dynamic_full_diagnostics.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part1.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part2.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part3.csv`
- `PB4_4p3_3p9_mismatch_only.csv`

298셀 전체 PFT 표는 GitHub 전송 크기 때문에 part1, part2, part3으로 나눴다. part1의 헤더를 유지하고 part2와 part3의 데이터 행을 이어 붙이면 원래 전체표가 된다.

4.3 ka:
- static: 298/298 혼효림
- dynamic: 활엽수림 8셀, 혼효림 290셀

동적 활엽수림 8셀:
- 평균 토심 0.162 m
- 평균 WHC 37.11 mm
- 평균 wetness 70.81
- 평균 firedays 93.25 d
- 토심 범위 0.046-0.276 m
- WHC 범위 10.99-62.55 mm
- firedays 범위 62-148 d

동적 혼효림 290셀:
- 평균 토심 약 2.336 m
- 평균 WHC 약 241.93 mm
- 평균 wetness 약 78.50
- 평균 firedays 약 3.19 d

동일 8셀의 static:
- 토심 1.94 m
- WHC 298.55 mm
- wetness 78.7
- firedays 0 d

4.3 ka에서는 기후와 토성은 셀 사이에 동일하므로 공간적 식생 차이는 기후 공간차로 설명할 수 없다.

8개 활엽수림 셀 중:
- 4셀은 BIOME4 native biome 자체가 Cool mixed forest에서 Temperate deciduous forest로 변함
- 나머지 4셀은 native biome은 Cool mixed forest로 유지되지만 reduced classification에서 활엽수와 침엽수 경쟁비가 51% 기준을 넘어서 활엽수림으로 바뀜

51% 경계 사례에서 정적모델의 활엽수 비율은 약 50.97%, 동적모델은 약 51.05-51.16%였다. 대표적으로 PFT4는 상대적으로 유지되지만 PFT6가 조금 더 감소하여 경계를 넘는다.

4.3-3.9 ka mismatch:
- 4.3 ka: 8셀
- 4.2 ka: 6셀
- 4.1 ka: 6셀
- 4.0 ka: 0셀
- 3.9 ka: 8셀

이 시기는 기후에 의해 활엽수림과 혼효림 전환 임계 부근에 놓인 상태에서, 동적 지형의 토심과 수분조건 차이가 일부 셀을 다른 쪽으로 이동시키는 것으로 해석한다.

## 7. 초기 침엽수림 차이: 현재까지 확인된 내용

핵심 파일:
- `diagnostics/vegetation_cellwise/PB4_EARLY_CONIFER_MISMATCH_CELL_DIAGNOSTICS.csv`
- `diagnostics/vegetation_cellwise/PB4_EARLY_CONIFER_MISMATCH_GROUP_SUMMARY.csv`
- `diagnostics/vegetation_cellwise/PB4_17p2_CONIFER_MISMATCH_CELL_PROCESS_DIAGNOSTICS.csv`
- `diagnostics/vegetation_cellwise/PB4_17p2_CONIFER_PROCESS_GROUP_DIAGNOSTICS.csv`

현재 직접 확인된 mismatch:
- 19.8 ka: dynamic에서 초본/개방식생 1셀 + 무식생 3셀, static은 해당 셀 모두 침엽수림
- 18.4 ka: dynamic에서 초본/개방식생 1셀 + 무식생 18셀, static은 모두 침엽수림
- 18.3 ka: dynamic에서 무식생 19셀, static은 모두 침엽수림

19.8 ka 초본/개방식생 1셀:
- 토심 0.003958 m
- WHC 0.938 mm
- wetness 61.7
- firedays 21 d
- NPP 4

18.4 ka 초본/개방식생 1셀:
- 토심 0.001297 m
- WHC 0.307 mm
- wetness 56.0
- firedays 15 d
- NPP 4

해당 시기의 무식생 셀은 사실상 토심 0에 가깝다. 반면 static 동일 위치는 토심 1.94 m, WHC 298.55 mm이고 침엽수림이다.

### 17.2 ka 과정 진단
dynamic 전체 298셀:
- 침엽수림 271셀
- 초본/개방식생 1셀
- 무식생 26셀

침엽수림 271셀 평균:
- 토심 1.8194 m
- WHC 260.764 mm
- wetness 76.906
- firedays 1.646 d
- NPP 275.705

초본/개방식생 1셀:
- 토심 0.009295 m
- WHC 2.203 mm
- wetness 56.7
- firedays 34 d
- NPP 6
- valley = 1
- contributing area 약 2355 m2

무식생 26셀:
- 토심은 사실상 0
- valley fraction = 0.8846, 즉 26셀 중 대부분이 valley/channel 위치
- 평균 contributing area 약 10856 m2
- 평균 unit-area contributing area 약 16991
- 평균 bedrock fluvial erosion 지표 약 0.0992 m/kyr
- regolith fluvial erosion은 토양이 이미 거의 소진된 셀에서 매우 작게 나타남

이 결과는 초기 침엽수림 차이가 단순한 PFT 경쟁 변화만이 아니라, 일부 수렴부와 하도 위치에서 토심이 거의 소실되어 초본 또는 무식생으로 바뀌는 별도의 경로가 있음을 보여준다.

### 17.2 ka 과정 진단 완결
추가 직접 계산과 셀 추적으로 다음이 확인되었다.
- 무식생 26셀 중 23셀(88.46%)이 valley이며, 침엽수림 271셀에서는 53셀(19.56%)이다.
- 무식생군 contributing area 중앙값은 5,311.6 m2로 침엽수림군 816.4 m2보다 약 6.5배 크다.
- 무식생군 A/w 중앙값은 14,486.2로 침엽수림군 43.77보다 약 331배 크다.
- 무식생 26셀 모두에서 fluvial bedrock erosion이 양수이며, fluvial regolith erosion이 양수인 셀은 1셀뿐이다.
- 현재 hillslope dz는 23/26셀에서 양수이고 음수인 무식생 셀은 없다. 따라서 현재의 무식생 상태를 현재 사면침식으로 직접 설명하지 않는다.
- 19.8 ka의 불일치 4셀과 18.4-18.3 ka의 불일치 19셀은 모두 17.2 ka의 무식생 셀에 포함된다.
- 19.8 ka cell (5,12)는 토심 0.003958 m의 개방식생에서 18.4 ka 토심 0 m 무식생으로, 18.4 ka cell (9,13)는 토심 0.001297 m의 개방식생에서 18.3 ka 토심 0 m 무식생으로 전환된다.
- 17.2 ka 실제 초본 셀 (14,9)은 토심 0.009295 m, WHC 2.203 mm, NPP 6, optPFT 10이다.
- 동일 17.2 ka 기후에서 토심만 바꾼 BIOME4-SD 민감도 계산에서 침엽수림-개방식생 전환은 약 H=0.01401 m, native barren-open 전환은 약 H=0.000201 m에서 나타났다.
- 실제 초본 셀에서 PFT6 NPP는 276.006에서 56.717로 약 79.45%, PFT7 NPP는 260.564에서 92.366으로 약 64.55% 감소한다.
- BIOME4 원 코드에서 PFT7 NPP가 120 미만이면 open branch로 이동하고, 이후 낮은 grass LAI와 PFT10 존재 조건에서 optPFT10이 선택된다.

완결문:
- `diagnostics/vegetation_cellwise/PB4_17p2_CONIFER_MECHANISM_COMPLETION_20261007_KO.md`
- `diagnostics/vegetation_cellwise/PB4_17p2_PFT_DEPTH_THRESHOLD_SUMMARY.csv`

## 8. 식생 결과 문장의 현재 방향

결과 문장은 다음 구조를 사용한다.

첫 문장:
"식생유형은 시기에 따라 뚜렷하게 변화하였으며, 정적 지형 모델과 동적 지형 모델의 우점식생 변화 양상은 전반적으로 비슷하게 나타났다."

그 다음:
1. 두 모델의 주요 우점식생 시간변화
2. 초기 침엽수림 시기의 동적모델 국지적 초본/무식생 출현
3. 4 ka 부근 혼효림-활엽수림 전환기의 국지적 차이

해석에서는:
- 큰 시간적 천이는 공통 기후변화가 주도
- 국지적 차이는 동적 지형발달에 따른 토심, WHC, wetness, firedays, PFT NPP 변화로 설명
- 초기 침엽수림 차이와 4 ka 활엽수림 차이는 원인이 같다고 단순화하지 않는다
- 초기에는 매우 얕은 토심 또는 토양 소실에 따른 초본/무식생 전환이 핵심
- 4 ka 부근에는 식생 경쟁 임계 부근에서 수분조건 변화가 PFT 상대생산성을 미세하게 바꾸는 것이 핵심

## 9. Jang 2011 최종 검증

Park 2021의 과거 24개 범주형 평가를 Jang primary score 분모에 넣지 않는다.

최종 Jang primary n = 62:
- static: 24/62 = 38.709677%
- dynamic: 55/62 = 88.709677%

최종 mapping:
- 95_01 = 활엽수림
- 95_02 = 혼효림
- 95_03 = 활엽수림
- 95_04 = 혼효림

record별:
- 95_01, 5.9-4.8 ka: static 12/12, dynamic 12/12
- 95_02, 4.8-3.4 ka: static 9/15, dynamic 9/15
- 95_03, 3.4-0.4 ka: static 0/31, dynamic 31/31
- 95_04, 0.3-0 ka: static 3/4, dynamic 3/4

관련 GitHub:
- `pb4_chelsa21k/results/final_integrated_20261006/FINAL_JANG1PCT_ROWS.csv`
- `pb4_chelsa21k/results/final_integrated_20261006/FINAL_JANG1PCT_SUMMARY.csv`
- `pb4_chelsa21k/results/fourway_20261004/JANG2011_CORRECTED_REDUCED_MAPPING.csv`

Jang 원자료는 61개 pollen sample이고, 62는 네 LPZ에 대응하는 반복 시간평가 단위이다. 이를 "62개 독립 화분시료"라고 쓰지 않는다.

## 10. Park 2021 독립 holdout

Park는 primary Jang categorical score와 분리한다.

현재 최종 참고 통계:
- PC2 vs dynamic cold-tree fraction: rho = 0.754, p = 0.00047466
- static: rho = -0.255, p = 0.32296
- broadleaf pollen vs dynamic temperate-deciduous: rho = 0.427, p = 0.087253

관련 파일:
- `pb4_chelsa21k/results/final_integrated_20261006/PARK2021_HOLDOUT_RESULT_20261006_KO.md`
- `pb4_chelsa21k/manuscript/PARK2021_HOLDOUT_STATISTICAL_PLAN_20261006_KO.md`
- `pb4_chelsa21k/manuscript/PARK2021_INDEPENDENT_VALIDATION_POLICY_20261006_KO.md`
- `pb4_chelsa21k/validation/park2021/`

## 11. 플롯과 지도 기준

GitHub 시계열 플롯 기준:
- `pb4_chelsa21k/plots/plot_chelsa_climate.py`
- `pb4_chelsa21k/plots/plot_mean_elevation.py`
- `pb4_chelsa21k/plots/plot_mean_soil_depth.py`
- `pb4_chelsa21k/plots/plot_mean_npp.py`

스타일:
- figsize 8.2 x 4.8
- x축 21 -> 0 ka
- tick 21,18,15,12,9,6,3,0
- 제목 없음
- 기본 흰 배경, grid 없음
- dynamic firebrick, static royalblue
- legend upper left, frame 없음
- PNG 600 dpi
- 새 그림을 만들 때 임의 스타일을 만들지 말고 이 코드를 따른다.

지도 최종 구성:
- 열: 21,15,10,5,0 ka
- 1행 dynamic
- 2행 static
- 3행 dynamic-static difference
- vegetation은 3행이 match/mismatch
- 경계는 외부 polygon이 아니라 정확한 raster pixel-edge outline
- elevation/soil map에는 outlet을 빨간 별로 표시

현재 outlet:
- grid row,col = (2,16)
- CRS EPSG:5187
- 좌표 약 (123252.94851086957, 624338.9488)

## 12. 현재 채팅의 로컬 산출물

아래는 현재 세션의 `/mnt/data`에 존재했던 파일이다. 새 채팅에서는 /mnt/data 지속성이 보장되지 않으므로 GitHub 자료를 우선하고, 필요한 경우 다시 생성한다.

핵심:
- `/mnt/data/PB4_ALL_TIMESTEPS_ALL_VARIABLES_U008_REFERENCE.csv`
  - 423행, 헤더 + static/dynamic 각 211시점
  - 평균 고도, 토심, NPP, EEMT, 식생 count, LAI, AET, wetness, runoff, firedays, PFT별 NPP 등 포함
- `/mnt/data/PB4_FULL_EXPORT_v2_ACTION_ARTIFACT.zip`
- `/mnt/data/PB4Studio_v6.6.3(3).zip`
- `/mnt/data/BIOME4-main (1)(1).zip`

셀 진단 원본:
- `/mnt/data/PB4_EARLY_CONIFER_MISMATCH_CELL_DIAGNOSTICS.csv`
- `/mnt/data/PB4_EARLY_CONIFER_MISMATCH_GROUP_SUMMARY.csv`
- `/mnt/data/PB4_17p2_CONIFER_MISMATCH_CELL_PROCESS_DIAGNOSTICS.csv`
- `/mnt/data/PB4_17p2_CONIFER_PROCESS_GROUP_DIAGNOSTICS.csv`
- `/mnt/data/PB4_4p3ka_broadleaf_cells_static_dynamic_full_diagnostics.csv`
- `/mnt/data/PB4_4p3ka_all_cells_PFT_diagnostics.csv`
- `/mnt/data/PB4_4p3_3p9_cellwise_dynamic_static_vegetation.csv`
- `/mnt/data/PB4_4p3_3p9_mismatch_only.csv`

지도 로컬 산출물:
- `/mnt/data/PB4_MAP5x3_elevation_outlet_star.png`
- `/mnt/data/PB4_MAP5x3_soil_depth_outlet_star.png`
- `/mnt/data/PB4_MAP5x3_OUTLET_STAR_OUTPUTS.zip`
- `/mnt/data/PB4Studio_v6.6.3_CHELSA21K_U008_MAP5x3_OUTLET_STAR.zip`

위 outlet-star package는 로컬 개선본이며 GitHub canonical package라고 자동 간주하지 않는다.

## 13. GitHub Actions full export

확인된 workflow run:
`37410207510`

artifact:
- id `11388859819`
- name `PB4Studio_v6.6.3_CHELSA21K_U008_FULL_EXPORT_v2`
- artifact SHA256 `f0b36fb8328431118d46c5ceba4d8210fd5b711f74b928e9751db7bc5bd0df9b`
- 당시 head SHA `df13eb79c3abcbcb8ac699e3d40bc6ec40cbf215`

GitHub Actions artifact는 만료될 수 있으므로 장기 근거는 저장소의 CSV와 문서를 우선한다.

## 14. 17.2 ka 초기 침엽수림 원인 분석 완료

기존의 첫 작업이었던 17.2 ka 침엽수림 셀 단위 원인 분석은 2026-10-07에 완료하였다.

새 핵심 파일:
- `diagnostics/vegetation_cellwise/PB4_17p2_CONIFER_MECHANISM_ANALYSIS_20261007_KO.md`
- `diagnostics/vegetation_cellwise/PB4_17p2_CUMULATIVE_PROCESS_GROUP_SUMMARY.csv`
- `diagnostics/vegetation_cellwise/PB4_17p2_HERB_OPEN_PFT_DIAGNOSTICS.csv`

완료된 핵심 결론:
- 17.2 ka dynamic = 침엽수림 271셀, 초본/개방식생 1셀, 무식생 26셀.
- 비침엽수 27셀 중 24셀이 valley에 있으며, valley 셀의 비침엽수 비율은 24/77 = 31.17%, 비-valley는 3/221 = 1.36%이다.
- 무식생 26셀 중 23셀은 valley 경로이다. 21.0-17.2 ka 누적 하천 토양침식 평균은 3.245 m, 누적 토양생성 평균은 1.171 m였고 최종 토심은 0 m이다.
- 비-valley 무식생 3셀은 별도 사면수송 경로이다. 누적 사면 토심변화는 -2.586~-3.196 m이고 누적 하천 토양침식은 0.021-0.030 m에 불과하다.
- 초본/개방식생 1셀(row 14, col 9)은 초기 1.94 m 토심에서 누적 토양생성 +0.547 m, 사면 토심변화 +0.005 m, 하천 토양침식 -2.483 m를 거쳐 최종 0.0093 m의 잔존토양이 남았다.
- 이 셀의 WHC는 2.203 mm, NPP는 6, optPFT는 10이다. PFT 6 NPP는 56.72, PFT 7 NPP는 92.37로 BIOME4의 각각 140, 120 경쟁기준 아래로 떨어졌다. PFT 8도 0으로 감소하여 PFT 10이 남고 native biome 21 Desert가 된다. PB4 축약분류에서 이것이 code 3 초본/개방식생 범주로 들어간다.
- 따라서 해당 1셀은 실제 초본 PFT 우점이라고 쓰지 말고 "초본/개방식생 범주" 또는 "개방식생"으로 표현한다.
- 침엽수림 유지 셀 중 최저 토심은 0.0461 m, WHC 10.93 mm, firedays 83 d, PFT 7 NPP 226.37이었다. 초본/개방식생 셀의 firedays는 34 d이므로 firedays 단독으로 전환을 설명할 수 없다.
- 17.2 ka의 메커니즘은 4.3 ka 활엽수림/혼효림 차이와 다르다. 17.2 ka는 토양 고갈 또는 극얕은 잔존토양 경로이고, 4.3 ka는 산림 PFT가 유지된 상태에서 native biome 또는 51% 상대생산성 경계를 넘는 경쟁 경로이다.

다음 작업은 이 완료된 진단을 이용해 식생 결과 및 해석 문단을 최종 원고 문체에 통합하고, 211개 시점의 우점식생 구간을 최종 검산하는 것이다.

## 15. 금지할 오류

- 120 ka 결과를 현재 21 ka 결과와 섞지 말 것.
- 과거 uplift 0.2 mm/yr를 사용하지 말 것.
- 그래프 눈대중 값을 실제 값처럼 쓰지 말 것.
- static/dynamic 전체 평균만 보고 셀 단위 원인을 단정하지 말 것.
- 무식생을 단순한 경쟁 실패로 해석하지 말 것. 토심 0 여부를 먼저 확인할 것.
- 4 ka의 활엽수 전환과 17-19 ka의 무식생/초본 출현을 같은 메커니즘으로 뭉뚱그리지 말 것.
- Park 2021을 Jang primary n=62 분모에 다시 넣지 말 것.
- 결과와 해석을 한 문단에서 뒤섞지 말 것.
