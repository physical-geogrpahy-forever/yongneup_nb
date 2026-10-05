# Temperate grass recovery decision

작성일: 2026-10-06  
상태: production 승격 전 후보 비교

## 1. 문제

최종 canonical PB4에서는 PFT8 temperate grass가 후기 홀로세에서 사실상 사라졌다. PFT8 NPP 자체가 0인 것은 아니며, PFT7 boreal deciduous tree가 얕은 토양에서도 경쟁에서 우점하는 것이 직접 원인이었다.

## 2. Beyer forcing 재실행

현재 final PB4 code를 그대로 유지하고 forcing만 packaged Beyer 월별 기후로 교체한 21.0-0.0 ka 전체 실행을 새로 수행했다.

결과:

- static Jang: 19/62
- dynamic Jang: 62/62
- dynamic PFT8 positive timesteps: 0/211
- static PFT8 positive timesteps: 0/211

동일 final code의 Beyer depth sweep에서도 0-6 ka, 시험한 모든 토심에서 PFT8이 optPFT가 되지 않았다.

따라서 현재 모델의 PFT8 소실은 CHELSA forcing 하나만으로 설명되지 않는다. 과거 Beyer + 5 cm sensitivity에서 PFT8이 나타났던 것은 과거 implementation state와 현재 final implementation의 차이도 포함한다.

## 3. 경험적 PFT7 canopy-opening 후보

PFT7 woody LAI가 일정 threshold보다 작을 때 PFT8을 선택하는 PB4 extension을 별도로 시험했다.

2.70 후보:

- Jang static: 24/62
- Jang dynamic: 55/62
- dynamic PFT8 positive timesteps: 101/211
- 최대 PFT8 cell: 8
- 최대 유역비율: 2.68%
- 2.2-2.7 ka PFT8: 1 timestep, 1 cell

하지만 LAI 2.70은 출판된 BIOME4 또는 Jackson 파라미터가 아니며 project threshold이다. 따라서 production의 우선 후보로 삼지 않는다.

## 4. Jackson life-form sub-30 cm root-profile 후보

보다 과정 기반의 수정으로, BIOME4의 native top-30-cm cumulative root fraction은 그대로 보존하고 0-30 cm 내부의 root profile shape만 Jackson et al. (1996)의 life-form beta로 구분했다.

사용 beta:

- grass/herb: 0.952
- shrub: 0.978
- tree: 0.970

H <= 0.30 m에서 본 연구의 normalized bridge는 다음과 같다.

    R_top,p(H)=r30,p [1-beta_p^(100H)]/[1-beta_p^30]

H는 m이다.

이 식은 Jackson et al. (1996)의 원식을 BIOME4의 r30에 맞춰 정규화한 project-derived bridge이며 Jackson 원 논문에 그대로 제시된 식이 아니다.

H > 0.30 m에서는 기존 PB4 McKenzie/BIOME4 tail을 유지한다.

## 5. Jackson 후보 결과

Focused depth sweep:

- 5 ka: PFT8 opt at H=0.05 m
- 4 ka: PFT8 opt at H=0.05 m
- 3.0-2.0 ka 시험시점: focused single-point sweep에서는 PFT8 opt 없음

Full 21.0-0.0 ka dynamic:

- Jang static: 24/62
- Jang dynamic: 55/62
- PFT8 positive timesteps: 114/211
- 최대 PFT8 cell: 13
- 0.5-3.2 ka PFT8 positive timesteps: 8
- 0.5-3.2 ka 최대 PFT8 cell: 1

Park Zone 2에 해당하는 0.5-2.1 ka model windows에서는 dynamic PFT8이 2.0, 1.9, 1.8, 1.0 ka에 각각 1 cell 나타났다. static에서는 PFT8이 나타나지 않았다.

즉 이 후보는 Jang 55/62를 손상시키지 않으면서 dynamic model에 temperate grass를 다시 출현시킨다.

## 6. 해석

현재 가장 과학적으로 방어하기 쉬운 temperate-grass 복원 후보는 Jackson life-form sub-30 cm root-profile refinement이다.

이유:

1. PFT8 출현을 특정 Park 시기나 Jang score에 맞추는 임의 threshold를 사용하지 않는다.
2. PFT7과 PFT8이 BIOME4에서 동일한 r30=0.83을 갖는다는 이유만으로 0-30 cm 내부 root shape까지 동일하게 취급하던 기존 PB4 bridge를 개선한다.
3. native BIOME4 r30 값은 30 cm에서 정확히 보존한다.
4. Jang primary validation 55/62가 유지된다.
5. PFT8이 full dynamic model에서 실제로 다시 나타난다.

그러나 Park의 2738-2206 cal yr BP open-vegetation event를 충분한 크기로 재현했다고 볼 수는 없다. 후기 홀로세에서 PFT8은 최대 1 cell 수준으로 매우 제한적이다.

따라서 이 후보는 "temperate grass가 전혀 없는 구조적 문제"를 수정하는 과정 기반 후보로는 적합하지만, Park open-vegetation event를 맞추기 위한 보정으로 해석하지 않는다.

## 7. 현재 결정

canonical production package는 아직 변경하지 않는다.

현 단계 우선순위:

1. Jackson root-profile candidate를 primary mechanistic candidate로 유지
2. 후보의 PFT8 공간위치와 해당 cell의 토심을 확인
3. Park 53 sample -> 17 window holdout을 이 후보 결과로 다시 계산
4. Kendall tau-b, Spearman effect size, moving-block bootstrap CI, 변화방향 일치율로 재평가
5. 결과가 baseline보다 과학적으로 개선되는지 확인한 뒤 production 승격 여부를 결정

Candidate package:

    pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_JACKSON_LIFEFORM_SUB30_GRASS_CANDIDATE.zip

Candidate SHA-256:

    b2a0f79a078c286275fcbc4a4355a416fd6212343b70a601469bf4ca16eaa30e

Canonical SHA-256 remains:

    a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34
