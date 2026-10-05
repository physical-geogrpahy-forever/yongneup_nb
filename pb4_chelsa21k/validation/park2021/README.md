# Park et al. (2021) independent holdout validation

이 폴더는 최종 PB4의 Park et al. (2021) 독립 보조검증용이다.

주 검증과 모델선택은 Jang et al. (2011), n=62, 유역 1% 출현 기준으로 이미 고정한다. Park 자료는 모델을 다시 보정하지 않는 holdout으로만 사용한다.

확보 원자료:

- 사용자가 제공한 Supplementary Excel: `1-s2.0-S0031018221004909-mmc1(1).xlsx`
- 파생 100년 window: `PARK2021_YNC_100YR_WINDOWS.csv`
- taxon mapping: `PARK2021_TAXON_MAPPING.csv`

Park et al. (2021) Supplementary의 sample-level pollen composition을 원자료로 사용하며, Fig. 3을 수작업 digitize하여 정량자료를 만들지 않는다.

시간처리:

- 원 sample age 유지
- 100년 window 집계
- 보간 없음
- sample이 없는 window는 결측
- 주 정량 비교구간은 69-16 cm, 약 2.072-0.515 ka BP

우선 비교:

- arboreal conifer vs deciduous broadleaf의 상대조성
- arboreal vs non-arboreal 변화방향
- 2738-2206 cal yr BP arboreal 감소, Poaceae/Artemisia 증가 사건의 재현 여부

local wetland taxa인 Cyperaceae, Apiaceae, Sphagnum은 regional vegetation 면적비 점수에 직접 포함하지 않는다.

주 통계는 Spearman rank correlation과 변화방향 일치도를 사용한다. pollen percentage와 model area fraction은 동일한 물리량으로 간주하지 않는다.

세부 정책:
pb4_chelsa21k/manuscript/PARK2021_INDEPENDENT_VALIDATION_POLICY_20261006_KO.md
