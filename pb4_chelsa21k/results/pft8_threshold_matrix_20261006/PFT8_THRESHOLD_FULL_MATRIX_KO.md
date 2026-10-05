# PFT8 temperate grass competition threshold full-run matrix

작성일: 2026-10-06  
기준 package SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`

## 실험 목적

최종 CHELSA 기반 PB4에서 PFT8 temperate grass는 양의 NPP를 계산하지만 PFT7 boreal deciduous tree가 우점하여 최종 optPFT로 거의 선택되지 않는다.

원 BIOME4 v4.2b2의 PFT7 경쟁 규칙은 PFT7 NPP가 120 gC m^-2 yr^-1 미만이거나 매우 건조하고 grass NPP가 더 클 때만 grass로 전환한다. PFT4 등 일부 다른 woody PFT에 존재하는 LAI 기반 canopy-opening 규칙은 PFT7에는 없다.

따라서 다음 규칙을 production 변경이 아닌 sensitivity candidate로 시험하였다.

    if grasspft == PFT8
    and grass NPP > 0
    and grass LAI >= 2.0
    and PFT7 woody LAI < threshold:
        optPFT = PFT8

시험 threshold는 2.65-2.95이며 모든 경우 21.0-0.0 ka static/dynamic 전체 실행을 다시 수행하였다.

## 전체 결과

| PFT7 LAI threshold | Jang static | Jang dynamic | dynamic Jang herb sum | PFT8 positive timesteps, 21 ka | PFT8 최대 cell 수 | 최대 유역비율 | 2.2-2.7 ka PFT8 시점수 | 2.2-2.7 ka PFT8 cell 합 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2.65 | 24/62 | **55/62** | 10 | 90 | 9 | 3.02% | 0 | 0 |
| 2.70 | 24/62 | **55/62** | 17 | 101 | 8 | 2.68% | 1 | 1 |
| 2.75 | 24/62 | 54/62 | 23 | 111 | 9 | 3.02% | 2 | 2 |
| 2.80 | 24/62 | 53/62 | 31 | 136 | 7 | 2.35% | 1 | 1 |
| 2.85 | 24/62 | 54/62 | 34 | 147 | 8 | 2.68% | 1 | 2 |
| 2.90 | 24/62 | 53/62 | 42 | 154 | 8 | 2.68% | 1 | 2 |
| 2.95 | 24/62 | 52/62 | 47 | 163 | 8 | 2.68% | 3 | 3 |

## 해석

1. PFT8을 다시 출현시키는 것 자체는 가능하다. 모든 threshold에서 21 ka 전체 dynamic 실행 중 PFT8이 실제 optPFT로 선택되는 시점이 발생하였다.
2. threshold가 커질수록 PFT8 출현 시점은 증가하지만 Jang dynamic 정확도가 악화되는 경향이 있다.
3. Jang 55/62를 그대로 유지하는 후보는 2.65와 2.70이다.
4. 2.65는 21 ka 전체에서는 PFT8을 생성하지만 2.2-2.7 ka 구간에는 PFT8이 없다.
5. 2.70은 Jang 55/62를 유지하면서 2.2-2.7 ka에도 PFT8이 최소 1 cell, 1시점 출현한다.
6. 2.75 이상은 PFT8을 더 늘리지만 이미 Jang 주 검증을 손상시키므로 현 단계에서 production 후보로 승격하지 않는다.

## 과학적 주의

2.65-2.95 값 자체는 BIOME4 출판 파라미터가 아니다. 이 실험은 PFT7의 원 competition block에 없는 canopy-opening rule을 PB4 extension으로 추가했을 때의 민감도 분석이다.

Park et al. (2021)은 independent holdout이므로 Park 적합도를 기준으로 threshold를 최적화해서는 안 된다. 따라서 2.70이 Park 구간에서 PFT8을 생성한다는 사실은 사후 진단으로만 기록하며, threshold 선택의 calibration criterion으로 사용하지 않는다.

현재 가장 보수적인 후보는 Jang 성능을 보존하는 2.65 또는 2.70이다. 최종 선택은 현재 최종 코드에서 forcing만 Beyer로 바꾸는 A/B 실험과 함께 판단한다.
