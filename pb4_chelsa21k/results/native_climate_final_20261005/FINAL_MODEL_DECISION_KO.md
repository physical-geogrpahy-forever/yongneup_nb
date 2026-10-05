# PB4 CHELSA21K final production decision — 2026-10-05

## 결정

최종 production 모델은 **PB4-McKenzie-nativeClimate**로 채택한다.

- BIOME4 v4.2b2의 PFT5/PFT6 기후제약을 원본 그대로 유지
- McKenzie 토심별 AWC coupling 유지
- Jackson 계열 PFT별 finite-depth root accessibility 유지
- native mixed biome의 broadleaf/conifer reduced classification은 대칭적 **51% 과반 규칙** 유지
- dynamic Pelletier 식생-지형 coupling 유지

## 근거

동일 CHELSA-TraCE21k/EnviCloud 21-0 ka forcing으로 PFT5/PFT6 기후튜닝만 제거하여 21-0 ka 전체를 새로 실행했다.

Jang et al. (2011) 원문 식생대 reduced mapping, n=62, 유역 1% 출현 기준:

| 모델 | static | dynamic |
|---|---:|---:|
| 이전 tunedClimate | 24/62 = 38.71% | 55/62 = 88.71% |
| 최종 nativeClimate | 24/62 = 38.71% | 55/62 = 88.71% |

따라서 PFT5/PFT6 기후튜닝은 검증 정확도 향상에 필요하지 않았다. 최종 모델에서는 불필요한 기후 niche 조정을 제거한다.

95_03 dynamic의 broadleaf 비율은 31개 시점 모두 1%를 넘으며 범위는 약 1.3423-3.3557%이다.

## 무결성

이 결정 이전 tuned-climate canonical ZIP SHA-256:
`bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09`

최종 native-climate canonical ZIP SHA-256:
`eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

과거 tuned-climate 패키지는 Git 이력으로 복구 가능하지만 더 이상 production 기준본이 아니다.
