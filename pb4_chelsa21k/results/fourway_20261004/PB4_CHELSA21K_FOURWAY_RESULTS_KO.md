# PB4Studio CHELSA21K 4-way 새 실행 결과

업데이트: 2026-10-04

## 연구 범위

본 작업은 대암산 용늪의 습지생태학, 고생태학, 고기후학, 생물지형학 연구이다. CHELSA-TraCE21k 기후자료와 BIOME4-Pelletier 결합모형을 이용해 식생, 토심, 수문, 지형의 장기 상호작용을 평가한다. 병원체, 독소, 감염성 실험, 생물무기 또는 위해성 실험과 관계가 없다.

## 1. 이번 결과의 지위

이 문서의 수치는 **2026-10-04에 새로 실행한 결과**이다. 과거 Beyer forcing, hotfix7, hotfix10n5의 정확도를 재사용하지 않았다.

- 기후: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 기후 SHA-256: `3f5d249bb59f4163bb0f78f5cb4759972575931bf977b8b2791db497805b0ec9`
- 기준 패키지: `PB4Studio_v6.6.3_CHELSA21K.zip`
- 패키지 SHA-256: `bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09`
- 공간해상도: 20 m
- 동적모형: 21.0-0.0 ka BP, 0.1 kyr 간격
- 정적모형: 상태 누적이 없으므로 Jang 검증에 필요한 5.9-0.0 ka BP를 0.1 kyr 간격으로 계산
- Jang 평가항목: 62개 record x output-time
- 주 판정기준: 유역에서 기대 식생이 **1% 이상** 존재

## 2. 원본 BIOME4 대조군 수정

CHELSA21K 패키지를 점검한 결과 기존 `original` 선택에도 hotfix10n10의 PFT5/PFT6 기후제약 수정이 적용되고 있었다. 이것은 진짜 BIOME4 v4.2b2 원본 대조군이 아니므로 이번 실험에서는 다음과 같이 분리했다.

- 원본 BIOME4: native PFT5/PFT6 기후한계를 그대로 유지
- 수정형: hotfix10n10의 PFT5/PFT6 기후제약과 McKenzie/Jackson finite-depth root adapter 유지
- 원본 reduced mapping: native BIOME4 mixed biome 6/7/9를 mixed로 그대로 보존
- 수정형 reduced mapping: hotfix10n10의 51% dominance 규칙 유지
- exact restart는 `z`, `b`, `H`만 저장/복원하며 연속 실행과 분할 실행의 최종 배열이 `array_equal=True`, 최대 절대차 0.0으로 검증됨

패치는 `TRUE_ORIGINAL_AND_EXACT_RESTART.patch`에 보존한다.

## 3. Jang 식생대 분류 교정

기존 PB4 축약 검증표에는 Jang 원문과 다른 라벨이 포함돼 있었다. 이번 주 결과는 Jang et al. (2011)의 원문 식생대 서술을 4개 reduced class에 직접 대응시켜 다시 집계한다.

| 기록 | 기간 (ka BP) | 기존 PB4 라벨 | Jang 원문 기준 reduced class |
|---|---:|---|---|
| 95_01 | 5.9-4.8 | 혼효림 | 낙엽활엽수림 |
| 95_02 | 4.8-3.4 | 침엽수림 | 혼효림 |
| 95_03 | 3.4-0.39 | 낙엽활엽수림 | 낙엽활엽수림 |
| 95_04 | 0.39-0 | 침엽수림 | 혼효림 |

기존 라벨 결과도 비교를 위해 별도 보존하지만 주 결과로 쓰지 않는다.

## 4. 주 결과: Jang 원문 기준 + 1% 유역 출현

| BIOME4 | 지형 | 정확도 |
|---|---|---:|
| 원본 v4.2b2 | static | **19/62 = 30.65%** |
| 원본 v4.2b2 | dynamic | **19/62 = 30.65%** |
| hotfix10n10 수정형 | static | **24/62 = 38.71%** |
| hotfix10n10 수정형 | dynamic | **55/62 = 88.71%** |

따라서 사용자가 지정한 1% 기준에서는 **수정형 dynamic이 가장 높은 Jang categorical 일치도를 보이며, static 24/62에서 dynamic 55/62로 크게 증가한다.** 이 차이는 주로 3.4-0.39 ka의 낙엽활엽수림이 dynamic에서 유역의 약 1.34-3.36%로 지속되어 1% 기준을 통과하기 때문에 발생한다.

5%와 10%는 주 기준이 아니라 **임계값 민감도 분석**으로만 제시한다.

## 5. 구간별 1% 결과

### original_static

| 기록 | 기대 식생 | 정답/전체 | 정확도 |
|---|---|---:|---:|
| 95_01 | 낙엽활엽수림 | 0/12 | 0.00% |
| 95_02 | 혼효림 | 15/15 | 100.00% |
| 95_03 | 낙엽활엽수림 | 0/31 | 0.00% |
| 95_04 | 혼효림 | 4/4 | 100.00% |

### original_dynamic

| 기록 | 기대 식생 | 정답/전체 | 정확도 |
|---|---|---:|---:|
| 95_01 | 낙엽활엽수림 | 0/12 | 0.00% |
| 95_02 | 혼효림 | 15/15 | 100.00% |
| 95_03 | 낙엽활엽수림 | 0/31 | 0.00% |
| 95_04 | 혼효림 | 4/4 | 100.00% |

### mckenzie2003_static

| 기록 | 기대 식생 | 정답/전체 | 정확도 |
|---|---|---:|---:|
| 95_01 | 낙엽활엽수림 | 12/12 | 100.00% |
| 95_02 | 혼효림 | 9/15 | 60.00% |
| 95_03 | 낙엽활엽수림 | 0/31 | 0.00% |
| 95_04 | 혼효림 | 3/4 | 75.00% |

### mckenzie2003_dynamic

| 기록 | 기대 식생 | 정답/전체 | 정확도 |
|---|---|---:|---:|
| 95_01 | 낙엽활엽수림 | 12/12 | 100.00% |
| 95_02 | 혼효림 | 9/15 | 60.00% |
| 95_03 | 낙엽활엽수림 | 31/31 | 100.00% |
| 95_04 | 혼효림 | 3/4 | 75.00% |

## 6. 임계값 민감도

Jang 원문 기준에서 유역 출현 임계값을 1%, 5%, 10%로 바꾸면 다음과 같다.

| case | 1% | 5% | 10% |
|---|---:|---:|---:|
| original_static | 19/62 = 30.65% | 19/62 = 30.65% | 19/62 = 30.65% |
| original_dynamic | 19/62 = 30.65% | 19/62 = 30.65% | 19/62 = 30.65% |
| mckenzie2003_static | 24/62 = 38.71% | 23/62 = 37.10% | 23/62 = 37.10% |
| mckenzie2003_dynamic | 55/62 = 88.71% | 23/62 = 37.10% | 23/62 = 37.10% |

주 기준은 1%이므로 수정형 dynamic의 **55/62 = 88.71%**를 주 결과로 사용한다. 5%와 10%에서는 각각 23/62 = 37.10%로 낮아지며, 이는 임계값 선택에 대한 민감도로 함께 보고한다.

## 7. 기존 PB4 축약 라벨을 그대로 썼을 때

1% 기준 비교용 감사값은 다음과 같다.

| case | 기존 축약 라벨 1% |
|---|---:|
| original_static | 12/62 = 19.35% |
| original_dynamic | 12/62 = 19.35% |
| mckenzie2003_static | 0/62 = 0.00% |
| mckenzie2003_dynamic | 31/62 = 50.00% |

이 표는 과거 결과와의 추적성을 위해 남긴 것이며, Jang 원문 식생대와 불일치하는 라벨을 포함하므로 주 과학적 결론에는 사용하지 않는다.

## 8. 해석

1. **원본 BIOME4**는 Jang 시기 대부분을 native mixed forest로 분류했다. 그래서 원문 기준 혼효림인 95_02와 95_04는 맞지만 낙엽활엽수림인 95_01과 95_03은 맞지 않는다. static과 dynamic의 categorical 결과도 동일하다.
2. **수정형 BIOME4**는 5.9-4.8 ka의 낙엽활엽수림을 잘 재현하고 4.8-3.4 ka와 0.39-0 ka의 혼효림 일부를 재현한다. 그러나 3.4-0.39 ka의 낙엽활엽수림은 dynamic에서 유역의 약 1-3% 수준으로만 남아 5% 문턱을 넘지 못한다.
3. 현재 수정형 결과에서 Jang 검증기간의 reduced conifer-forest class는 사실상 나타나지 않는다. 따라서 hotfix10n10 침엽수 기후범위 확장을 넣었다고 해서 유역이 침엽수림으로 지배되는 것은 아니다.
4. 과거 Beyer/hotfix 결과의 높은 정확도는 최신 CHELSA 결과로 이전할 수 없다. 특히 기후 forcing, Jang 라벨, presence threshold를 동시에 명시해야 하며, 이 프로젝트의 주 기준은 1%이다.

## 9. 산출물

- `PRIMARY_JANG2011_1PCT_FOURWAY.csv`: 주 1% 결과
- `FOURWAY_JANG_ACCURACY_1_5_10PCT.csv`: 임계값 민감도
- `FOURWAY_JANG_ZONE_BREAKDOWN.csv`: 구간별 상세 결과
- `JANG2011_CORRECTED_REDUCED_MAPPING.csv`: Jang 원문 기반 분류 교정
- `EXECUTION_PROVENANCE.json`: 입력, 버전, SHA, 실행지위
- `TRUE_ORIGINAL_AND_EXACT_RESTART.patch`: 진짜 원본 대조군 및 exact restart 패치

Park et al. (2021)은 이 62개 categorical 정확도에 넣지 않는다. Supplementary 실측 화분자료를 별도 평가한다.


## 10. 수정형 성능 향상 원인 진단

추가 PFT/토심 진단 결과, 성능 향상은 두 단계로 구분된다.

- 원본 static 19/62 -> 수정형 static 24/62: 주로 native mixed forest에 대한 hotfix10n10의 51% reduced-class dominance 판정 효과
- 수정형 static 24/62 -> 수정형 dynamic 55/62: 동적 지형발달이 만든 극천부 토양 포켓과 McKenzie/Jackson finite-depth root-water coupling의 결합 효과

특히 3.4-0.4 ka에는 native BIOME4 broadleaf cell 자체가 매 시점 3-4/298셀, 즉 1.0067-1.3423% 존재하므로 1% 기준을 31/31 통과한다. 이 부분은 51% post-classification만으로 생긴 것이 아니다.

상세 진단은 `cause_diagnostics/CAUSE_DIAGNOSIS_KO.md`와 동 디렉터리의 CSV를 참조한다.


## 11. Native-climate ablation

2026-10-05에 PB4-McKenzie의 McKenzie AWC, Jackson finite-depth roots, 51% 과반 판정, dynamic Pelletier coupling은 유지하고 PFT5/PFT6 기후제약 튜닝만 제거한 full 21-0 ka ablation을 새로 실행했다.

결과는 tunedClimate와 완전히 동일했다.

- static: 24/62 = 38.71%
- dynamic: 55/62 = 88.71%
- 95_01: 12/12
- 95_02: 9/15
- 95_03: static 0/31, dynamic 31/31
- 95_04: 3/4

따라서 PFT5/PFT6 온도보정은 현재 검증 정확도 향상에 필요하지 않으며, BIOME4 v4.2b2 원본 기후제약을 유지하는 nativeClimate 구성이 더 단순한 생산 후보이다.

상세 결과: `../native_climate_ablation_20261005/NATIVE_CLIMATE_ABLATION_RESULTS_KO.md`
