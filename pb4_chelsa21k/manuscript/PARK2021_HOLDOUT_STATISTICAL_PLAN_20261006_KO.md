# Park et al. (2021) holdout 통계계획 재정리

작성일: 2026-10-06  
상태: **최종 통계분석 전 사전 규칙**

## 1. 시간 정렬표를 먼저 고정

Park Zone 2의 53개 실제 pollen sample을 통계분석 전에 PB4 100년 시점에 고정한다.

source:
- `1-s2.0-S0031018221004909-mmc1(1).xlsx`
- sheet: `2. Pollen (percents)`
- depth: 16-69 cm, 50 cm 제외
- age: 515-2072 cal yr BP

assignment:

[
t_{PB4}=100leftlfloorrac{t_{pollen}+50}{100}ightfloor
]

즉 가장 가까운 100년 시점으로 배정하고 정확히 50년 경계인 경우 오래된 쪽 100년 시점으로 배정한다.

예:
- 515 BP -> 0.5 ka
- 554 BP -> 0.6 ka
- 1050 BP -> 1.1 ka
- 1250 BP -> 1.3 ka
- 2072 BP -> 2.1 ka

53 samples는 17개 100년 window로 집계된다.

고정표:
`PARK2021_SAMPLE_TO_PB4_ALIGNMENT.csv`

이 표를 만든 뒤 통계를 선택한다. 통계 결과를 보고 시간배정 규칙을 바꾸지 않는다.

## 2. Park holdout의 주 비교변수

Park 검증의 주 목적은 실제 식생유형 조성을 비교하는 것이다. 따라서 주 분석은 임의의 한랭지수나 임의의 혼효림 지수를 만들지 않는다.

Park Supplementary에서 직접 계산하는 주 변수:
1. 침엽수 비율
2. 낙엽활엽수 비율
3. 초본 비율
4. 총 목본 비율

PB4에서도 이에 대응하는 PFT 또는 reduced-class 비율을 사용한다.

PC2는 Park et al. (2021)이 실제 PCA로 산출한 독립적인 관측축이므로 보조 분석에는 사용할 수 있으나, 직접 식생유형 비율을 대신하는 주 검증지표로 사용하지 않는다.

## 3. 일반 Spearman 검정의 문제

17개 100년 window에 대해 일반적인 Spearman rho와 표준 p-value만 사용하는 것은 최종 주 검정으로 충분하지 않다.

이유:
- 자료가 시간순서 자료라 인접 100년 window가 독립이라는 보장이 없음
- pollen과 모델 모두 시간적 자기상관이 있을 수 있음
- n=17로 작음
- 모델 비율에 동일값이 반복되는 ties가 많음
- window별 pollen sample 수가 1-10개로 다름
- pollen percentage와 model cell fraction은 동일한 관측과정이 아님

따라서 기존 `Spearman rho=0.632, p=0.00644`는 현 단계에서는 **보조적인 효과크기/탐색 결과**로 취급하고, 표준 p-value를 최종 유의성 근거로 단독 사용하지 않는다.

## 4. 권장 최종 통계구조

### 4.1 주 효과크기

각 직접 식생유형 비율에 대해 다음을 함께 보고한다.

- Spearman rho
- Kendall tau-b

Spearman은 단조관계의 크기를 보여주고, Kendall tau-b는 작은 n과 ties가 많은 모델 비율에 더 안정적이다.

### 4.2 시간 자기상관 보정

표준 독립표본 p-value는 최종 추론에 사용하지 않는다. 17개 window는 시간순서 자료이며 자기상관 가능성이 있기 때문이다.

주 불확실성 평가는 **moving-block bootstrap**으로 한다.

- block length 2 windows = 200 yr
- block length 3 windows = 300 yr
- 두 block length에서 Spearman rho와 Kendall tau-b의 95% bootstrap CI를 계산
- 결론이 block length에 따라 바뀌면 유의성보다 불확실성을 보고

blocked permutation은 보조 sensitivity로 사용한다.

circular shift는 시계열 자기상관을 잘 보존하지만 n=17에서는 가능한 고유 shift 수가 매우 적어 p-value 해상도가 낮으므로 주 유의성 검정으로 사용하지 않는다.

따라서 최종 보고는 단일 p-value보다 effect size와 autocorrelation-preserving CI를 중심으로 한다.

### 4.3 변화방향 검증

절대 비율 외에 인접 window의 변화방향을 비교한다.

[
Delta X_t=X_t-X_{t-1}
]

관측과 모델의 (Delta) 부호가 같은 비율을 계산하여, 모델이 증가/감소 방향을 재현하는지 별도로 평가한다.

### 4.4 chronology sensitivity

nearest-100-year 배정에 대한 민감도를 확인한다.

- primary: nearest 100 yr
- sensitivity: model series를 -0.1 kyr, +0.1 kyr 이동하여 동일 통계 재계산

이는 Bacon posterior chronology uncertainty의 정식 대체물이 아니라, 100년 모델 시간해상도에 대한 alignment sensitivity이다.

## 5. 사용하지 않을 주 통계

다음은 Park 주 holdout 지표로 사용하지 않는다.

- pollen percentage와 model area fraction의 직접 RMSE만으로 적합도 판정
- 일반 Pearson correlation 단독
- PC2 vs 임의의 cold-tree index만으로 모델 검증
- 53개 sample을 독립 n=53으로 취급하여 동일 model window를 반복 복제
- 여러 sample이 같은 PB4 시점에 배정된 상태에서 sample-level 일반 p-value 계산

## 6. 최종 보고 방식

주 표:
- 53 sample -> PB4 window alignment 표
- 17-window 관측/모델 비교표

주 통계:
- 직접 식생유형별 Kendall tau-b
- 직접 식생유형별 Spearman rho
- moving-block bootstrap 95% CI, block length 2와 3
- blocked-permutation sensitivity
- 변화방향 일치율
- ±0.1 kyr alignment sensitivity

모델 값이 전 구간에서 동일하여 분산이 0인 경우 correlation을 강제로 계산하지 않는다. 이 경우에는 "not estimable due to zero model variance"로 보고하고, 해당 식생유형의 시간변동을 모델이 재현하지 못한 구조적 한계로 판정한다.

보조:
- Park PC1/PC2
- reconstructed temperature
- 2738-2206 cal yr BP open-vegetation event

Park 결과는 Jang 55/62 accuracy에 합산하지 않고 독립 holdout으로 유지한다.
