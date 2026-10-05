# PB4 CHELSA21K native-climate ablation

업데이트: 2026-10-05

## 실험 목적

PB4-McKenzie의 토심별 AWC, PFT별 finite-depth root coupling, 51% 과반 reduced-class 판정, dynamic Pelletier coupling은 그대로 유지하고, PFT5/PFT6 기후제약 조정만 제거하여 BIOME4 v4.2b2 원본 기후제약으로 복원했다.

## 실행 조건

- 기후: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- 기간: 21.0-0.0 ka BP
- 간격: 0.1 kyr
- 기반 패키지 SHA-256: bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09
- 실행 상태: 2026-10-05 새 full 21 ka 실행
- 검증: Jang et al. (2011) 원문 식생대 reduced mapping, n=62, 유역 1% 출현 기준

## 결과

| 모델 | 지형 | 정답 | 정확도 |
|---|---|---:|---:|
| PB4-McKenzie-nativeClimate | static | 24/62 | 38.71% |
| PB4-McKenzie-nativeClimate | dynamic | 55/62 | 88.71% |

기존 PFT5/PFT6 tunedClimate PB4-McKenzie 결과와 총점뿐 아니라 Jang 구간별 결과도 동일했다.

| record | static | dynamic |
|---|---:|---:|
| 95_01 | 12/12 | 12/12 |
| 95_02 | 9/15 | 9/15 |
| 95_03 | 0/31 | 31/31 |
| 95_04 | 3/4 | 3/4 |

95_03 dynamic의 broadleaf fraction 범위도 기존 결과와 동일하게 0.0134228-0.0335570이다.

## 판정

PFT5/PFT6 기후제약 튜닝은 CHELSA21K + Jang 1% 검증 성능 향상에 필요하지 않다.

따라서 생산 모델 후보는 다음 구조가 더 단순하고 방어하기 쉽다.

1. BIOME4 v4.2b2 원본 PFT 기후제약 유지
2. McKenzie 기반 토심별 AWC 유지
3. Jackson finite-depth root coupling 유지
4. 51% 과반 broadleaf/conifer reduced-class 판정 유지
5. dynamic Pelletier coupling 유지

즉 모델 성능 향상은 PFT 온도한계 튜닝이 아니라 토심-수문-뿌리-지형 결합에서 나온 것으로 해석하는 것이 타당하다.
