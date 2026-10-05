# Park et al. (2021) 독립 보조검증 정책

작성일: 2026-10-06  
상태: 최종 통합 PB4의 보조검증 설계

## 1. 역할 분리

최종 PB4의 주 검증과 모델 선택은 Jang et al. (2011)만으로 수행한다.

- 주 검증: Jang et al. (2011)
- record: 95_01, 95_02, 95_03, 95_04
- 평가항목: 62개 100년 output-time
- 판정기준: corrected reduced mapping, 유역 내 목표 식생군 1% 이상 출현
- 최종 dynamic 기준: 55/62 = 88.71%

Park et al. (2021)은 이 62개 총점에 합치지 않는다. 과거의 92_01, 92_02, 92_03을 Jang record와 같은 categorical score로 합산하는 방식은 폐기한다.

Park et al. (2021)은 최종모형이 확정된 뒤 수행하는 **독립 보조검증(holdout validation)**으로만 사용한다. Park 자료를 이용해 BIOME4 또는 지형모형의 파라미터를 다시 조정하지 않는다.

## 2. Park 자료의 성격

Park et al. (2021)의 YN-C core pollen 분석은 16-88 cm 깊이에서 50 cm를 제외한 72개 시료를 대상으로 수행되었고, 평균 시간해상도는 약 36.8년이다. pollen percentage는 total non-aquatic pollen and spore counts를 기준으로 계산되었다.

논문은 69-16 cm 구간을 완전히 발달한 peatland 이후의 구간으로 구분하며, 이 구간에서 PCA를 수행했다. 또한 Cyperaceae, Apiaceae, Sphagnum은 용늪 내부 수분상태에 민감한 local wetland taxa로 판단하여 temperature reconstruction에서 제외했다.

따라서 PB4의 지역 식생과 직접 비교하는 주 Park 보조검증은 69-16 cm, 약 2.072-0.515 ka BP 구간을 우선한다.

88-69 cm, 약 3.181-2.072 ka BP 구간은 peatland 발달 초기 단계이며 별도 descriptive comparison으로 남긴다. 이 구간은 최종 Park quantitative score에 포함하지 않는다.

## 3. 원자료 원칙

Park 검증은 논문 본문의 세 구간을 다시 범주화하여 사용하지 않는다.

사용 자료는 Park et al. (2021)의 Supplementary에 제시된 sample-level pollen composition이어야 한다.

현재 저장소에는 Supplementary의 machine-readable raw table이 아직 보존되어 있지 않다. 논문은 DOI에서 Supplementary data가 제공된다고 명시한다.

원자료 확보 후 다음 파일로 고정한다.

    pb4_chelsa21k/validation/park2021/PARK2021_YNC_POLLEN_RAW.csv

원자료를 수작업으로 그림에서 역산하지 않는다. Supplementary의 원 수치만 사용한다.

## 4. 시간 정렬

PB4 출력은 100년 간격이므로 Park sample age를 100년 window에 집계한다.

원칙:

- 보간하지 않음
- 각 pollen sample의 원 연대를 유지
- 동일한 100년 window에 여러 sample이 있으면 그 window 내 평균 조성을 계산
- pollen sample이 없는 100년 window는 결측으로 유지
- model output을 pollen sample age에 선형보간하지 않음

따라서 Park 검증의 유효 n은 Supplementary 원자료가 확보된 뒤 실제 100년 window 수로 결정한다.

## 5. 지역 식생 비교용 pollen group

Park의 raw pollen taxa를 PB4와 비교할 때는 mapping 파일을 별도로 보존한다.

    pb4_chelsa21k/validation/park2021/PARK2021_TAXON_MAPPING.csv

최소 비교축은 다음과 같다.

1. conifer arboreal pollen
2. deciduous broadleaf arboreal pollen
3. non-aquatic herbaceous pollen

Cyperaceae, Apiaceae, Sphagnum은 지역 식생 조성 점수에서 제외한다. 이들은 Park et al. (2021)이 local water availability에 민감한 taxa로 해석했으므로, 필요하면 별도의 local wetness diagnostic으로만 사용한다.

taxon mapping은 Supplementary의 실제 열 이름을 확인한 뒤 명시적으로 기록한다. 이름이 불명확한 taxon을 임의로 어느 군에 넣지 않는다.

## 6. PB4 model-side 비교값

각 100년 output에서 유역의 reduced vegetation class를 이용한다.

- conifer fraction
- broadleaf fraction
- mixed fraction
- herbaceous fraction

conifer와 broadleaf의 상대비를 비교할 때 mixed cell을 임의로 50:50으로 나누지 않는다.

tree-only model conifer fraction은 다음과 같이 정의한다.

    F_{conifer,model}={N_{conifer} OVER N_{conifer}+N_{broadleaf}}

tree-only model broadleaf fraction은

    F_{broadleaf,model}={N_{broadleaf} OVER N_{conifer}+N_{broadleaf}}

로 계산한다.

mixed fraction은 별도 변수로 함께 보고한다.

Park pollen에서도 arboreal conifer와 deciduous broadleaf를 같은 방식으로 closure한 비율을 산정한다.

    F_{conifer,pollen}={P_{conifer} OVER P_{conifer}+P_{broadleaf}}

    F_{broadleaf,pollen}={P_{broadleaf} OVER P_{conifer}+P_{broadleaf}}

## 7. 평가통계

Park 자료는 pollen percentage와 model area fraction이 동일한 물리량이 아니므로, Jang과 같은 binary accuracy를 주 통계로 사용하지 않는다.

주 통계:

- conifer fraction의 Spearman rho
- broadleaf fraction의 Spearman rho
- herbaceous signal의 Spearman rho
- mixed fraction을 포함한 model-side 변화의 descriptive comparison

보조 결과:

- 각 100년 window의 observed pollen composition과 model class fraction
- cold/warm 또는 open/wooded 변화방향의 일치 여부
- 69-16 cm 구간 시계열 그림

직접적인 RMSE나 percentage-point error는 보조값으로도 신중하게 사용한다. pollen productivity와 dispersal 차이 때문에 pollen percentage를 vegetation area percentage와 동일하게 취급하지 않는다.

## 8. 사용 금지

다음 방식은 최종 Park 검증에서 사용하지 않는다.

- Park의 92_01, 92_02, 92_03을 Jang 62개 score에 합산
- 세 Park 구간을 혼효림, 초본, 혼효림으로 단순 범주화하여 주 정확도로 사용
- Supplementary 원수치 없이 Fig. 3을 눈대중으로 digitize
- pollen sample 사이를 선형보간해 가상의 100년 자료 생성
- Park 결과를 보고 BIOME4 PFT 기후제약이나 51% 규칙을 재조정

## 9. 최종 보고 구조

본문의 주 검증 결과:

    Jang et al. (2011), n=62, 1% basin-presence criterion

Supplementary 또는 별도 Results subsection:

    Park et al. (2021) sample-level pollen composition, independent holdout evaluation

따라서 Park은 최종모형의 선택기준이 아니라, 이미 Jang으로 고정된 최종 PB4가 Late Holocene의 세부 식생변동을 독립적으로 재현하는지 확인하는 외부 검증자료로 사용한다.

## 10. 참고문헌

Park, J., Jin, Q., Choi, J., Bahk, J., & Park, J. (2021). Late Holocene climate variability in central Korea indicated by vegetation, geochemistry, and fire records of the Yongneup moor. Palaeogeography, Palaeoclimatology, Palaeoecology, 584, 110705. https://doi.org/10.1016/j.palaeo.2021.110705
