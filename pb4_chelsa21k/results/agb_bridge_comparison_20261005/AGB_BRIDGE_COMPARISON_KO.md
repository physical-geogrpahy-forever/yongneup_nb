# AGB bridge 21–0 ka comparison — 2026-10-05

## 실행 범위

모델은 PB4-McKenzie-nativeClimate, 기후는 `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`, 21.0–0.0 ka BP, 0.1 kyr 간격, static 211 + dynamic 211 시점이다.

canonical package SHA-256:
`eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

비교한 AGB bridge:
1. production baseline: `AGB = 0.010*NPP`
2. JULES/TRIFFID optLAI allometry, PFT7=BDT
3. JULES/TRIFFID optLAI allometry, PFT7=NDT
4. Xue/IBIS PFT-specific equilibrium NPP-allocation-turnover candidate

## JULES 식

[
AGB_{dry} = LMA(PFT)L + {0.75,a_{wl}(PFT)L^{5/3} over 0.50}
]

여기서 (L)은 BIOME4 dominant PFT의 `optLAI`를 전달하는 `lai_node`이다.

PFT mapping:
- BIOME4 PFT4 -> JULES BDT: LMA 0.0823, awl 0.78
- PFT5 -> NET: 0.2263, 0.65
- PFT6 -> NET: 0.2263, 0.65
- PFT7 -> BDT 또는 NDT 두 sensitivity 실행
- PFT10 -> ESH: 0.1515, 0.13

PFT10에 integrated woody pool의 75:25 aboveground:coarse-root 분할을 적용한 것은 명시적 sensitivity extrapolation이다. 최종 검증된 shrub AGB 식으로 취급하지 않는다.

## 핵심 결과

| 방법 | dynamic 21 ka 평균 AGB kg m^-2 | dynamic 0 ka 평균 AGB kg m^-2 | dynamic absolute max kg m^-2 | Jang dynamic | Jang static |
|---|---:|---:|---:|---:|---:|
| legacy 0.010 NPP | 4.009 | 6.110 | - | 55/62 = 88.71% | 24/62 = 38.71% |
| JULES BDT | 6.178 | 8.399 | 10.803 | 55/62 = 88.71% | 24/62 = 38.71% |
| JULES NDT | 6.185 | 8.402 | 11.141 | 55/62 = 88.71% | 24/62 = 38.71% |
| Xue/IBIS | 12.836 | 17.564 | 20.720 | 55/62 = 88.71% | 24/62 = 38.71% |

JULES dynamic time-mean AGB는 Xue/IBIS보다 약 51.9% 낮다.

## 0 ka geomorphic response

canonical dynamic 0 ka:
- mean elevation 1166.3393235 m
- mean soil depth 2.4959888 m
- mean slope 0.2940822
- relief 68.2347752 m

JULES BDT minus canonical:
- mean elevation +0.01657 m
- mean soil depth +0.03025 m
- mean slope -0.003080
- relief -0.21060 m

JULES NDT minus canonical:
- mean elevation +0.01652 m
- mean soil depth +0.03032 m
- mean slope -0.003082
- relief -0.21452 m

Xue/IBIS minus canonical:
- mean elevation +0.06173 m
- mean soil depth +0.11751 m
- mean slope -0.011949
- relief -0.78984 m

따라서 AGB bridge는 실제 지형 feedback을 바꾼다. Jang corrected 1% 검증이 동일한 것은 지형이 동일해서가 아니라, 현재 범주형 1% presence 판정이 이 수준의 geomorphic 차이에 둔감하기 때문이다.

## PFT7 sensitivity

BDT와 NDT의 0 ka dynamic 차이는 매우 작다.
- mean AGB: 0.00360 kg m^-2
- mean elevation: 0.000052 m
- mean soil depth: 0.000071 m
- relief: 0.00392 m

따라서 현재 용늪 21 ka 도메인에서는 PFT7을 BDT/NDT 중 어느 쪽으로 해석하는지가 전체 결과의 주요 불확실성은 아니다.

## 판정

현재 수치 결과만 보면 JULES optLAI 경로가 Xue/IBIS보다 보수적인 AGB를 만들며, BIOME4가 직접 계산한 optLAI를 사용한다는 구조적 장점이 있다. 그러나 JULES 계수를 BIOME4 optLAI에 전이한 독립 검증은 아직 부족하고, fC_wood=0.50 및 PFT10 shrub woody-pool 분할 가정이 남아 있으므로 production으로 즉시 승격하지 않는다.

다음 판정 작업은 새로운 AGB 수식을 더 찾는 것이 아니라, 동일 정의의 LAI–living dry AGB 자료에서 JULES 전이식의 magnitude를 검증하는 것이다.

## 재현 파일

- BDT candidate ZIP: `pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_JULES_LAI_BDT_AGB.zip`
- NDT candidate ZIP: `pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_JULES_LAI_NDT_AGB.zip`
- BDT results: `pb4_chelsa21k/results/jules_lai_bdt_agb_candidate_20261005/`
- NDT results: `pb4_chelsa21k/results/jules_lai_ndt_agb_candidate_20261005/`
- IBIS reference: `pb4_chelsa21k/results/pft_ibis_agb_candidate_20261005/`

JULES BDT candidate SHA-256:
`2d0d38620904a7f40d6f1009a1787ec0657a2f001fe9309be683fb8c356d2fe0`

JULES NDT candidate SHA-256:
`1a369d9db3092e90473e696c909939a4968daa14de1ce2628b248dfa78781745`

Result commit:
`31a4c9fca8dedd52a64db92380012ae1370c317b`

## 문헌

- Harper et al. (2016), JULES-vn4.3 parameterization, GMD 9:2415–2440.
- Harper et al. (2018), JULES-C2 allometry, GMD 11:2857–2873.
- Wolf et al. (2011), forest biomass allometry in global land-surface models, Global Biogeochemical Cycles 25, GB2009.
- Xue et al. (2017), IBIS vegetation carbon / AGB evaluation, Ecological Modelling 355:84–96.
