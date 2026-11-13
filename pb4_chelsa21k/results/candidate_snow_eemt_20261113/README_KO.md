# EEMT 적설 반영 후보 검토 (2026-11-13)

`final` 브랜치의 최종 모델(FABDEM 30 m, 656격자, 59.0 ha, Sc 0.7)은 그대로 두고, EEMT의 유효강수 계산만 바꾼 세 경우를 같은 조건에서 비교하였다. 이 폴더와 후보 패키지는 `candidate-snow-eemt` 브랜치에만 있다.

| 기호 | 규칙 | 식 |
|---|---|---|
| A | 음수 포함(U008 이전 식) | Σ c_w T_m (P_m − AET_m) |
| B | 영하 월 0(최종 모델) | Σ c_w max(T_m,0) max(P_m − AET_m,0) |
| C | BIOME4 적설 반영 | Σ c_w max(T_m,0) max(L_m − AET_m,0) |

L_m은 BIOME4 v4.2b2의 `daily`와 `snow` 서브루틴이 만든 일별 dprec+dmelt를 달력월(31, 28, 31, …일)로 합한 값이다. 후보 패키지에서는 두 서브루틴을 단정밀도로 그대로 옮겨 쓰며, 원 Fortran(gfortran -O0)과 4,244개 기후 조합에서 비교한 월 L의 최대 차이는 1.7×10⁻⁵ mm였다(출력 자릿수 차이).

## 1. 적설 수렴

- 용늪 211시점: 1년차 말과 2년차 말 적설이 모든 시점에서 같다(21 ka 126.5 mm, 5 ka 88.0 mm, 0 ka 75.6 mm). 12월 적설이 0이 되지는 않지만 연 순환은 두 번의 반복으로 주기해에 도달한다. 연 적설량 = 연 융설량, 물수지 오차는 4×10⁻⁴ mm 이하.
- 전지구 52지점 × 72시점(3,744경우): 1,348경우에서 연말 적설이 남고, 196경우(그린란드 내륙, 히말라야, 레이캬비크, 밴쿠버, 뉴욕, 앵커리지)는 해마다 적설이 늘어나 수렴하지 않는다. 야쿠츠크는 모든 시점에서 수렴하였다.
- 수렴하지 않는 196경우에서도 2회 반복과 10회 반복의 월 L 차이는 0.0000 mm였다. 적설이 융설 상한에 걸리지 않을 만큼 남아 있으면 해마다 같은 날 같은 양이 녹기 때문이다. 따라서 2회 반복은 월 액체수 계산에 충분하다.

`snow_check/yongneup_snow_balance.csv`, `snow_check/global_snow_convergence.csv`

## 2. 월 액체수와 물수지 (유역 평균 기후)

| ka | 연강수 P | BIOME4 일보간 강수 | 비 | 융설(=강설) | 12월 적설 |
|---|---|---|---|---|---|
| 21 | 1,786 | 1,794.7 | 1,515.0 | 279.8 | 126.5 |
| 5 | 1,960 | 1,969.4 | 1,739.7 | 229.7 | 88.0 |
| 0 | 1,838 | 1,846.7 | 1,634.9 | 211.7 | 75.6 |

연 L은 일보간 강수 합과 같다. BIOME4의 `daily`는 월 중앙일 사이를 선형 보간하므로 월합이 보존되지 않으며(0 ka 7월 P 384 mm, 보간 합 368.6 mm), 연합도 P보다 약 9 mm 크다. C와 B의 차이에는 적설 효과와 이 보간 효과가 함께 들어 있다. 0 ka 월별 값은 `snow_check/item2_monthly_0ka.csv`.

## 3. 평균기온 0 °C 이하이면서 액체수가 있는 달

- 시점마다 1~2개월(주로 3월과 11월). 0 ka 3월은 평균 −1.2 °C이지만 −1 °C를 넘는 날의 비와 융설로 L 56.4 mm(융설 17.6 mm).
- 이런 달의 액체수 합은 7.7~98.8 mm이다. 월 평균기온 기준으로는 EPPT가 0이고, 일 단위로 c_w max(T_d,0)(L_d − AET_d)를 계산해도 이 달들의 EPPT는 최대 0.42 MJ m⁻² yr⁻¹이다. 해당 날의 기온이 0 °C를 겨우 넘기 때문이다.
- C를 월 단위로 계산한 값과 일 단위로 계산한 값의 차이는 0.12~0.89 MJ m⁻² yr⁻¹이다(일 AET는 출력되지 않으므로 월 AET를 일수로 나눠 배분).
- 계산법은 바꾸지 않았다. `snow_check/item3_eppt_basinmean.csv`

## 4. BIOME4 AET의 내용

- `hydrology`에서 aet = alfa × deq(평형증발량), 공급 한계 emax × wr로 제한. 잎이 없으면(fvc = 0) 0.25 × deq, 일평균기온 −10 °C 이하이면 0.
- 토양수분 수지의 별도 증발항은 `evap = 0.0`(원 코드에서 `evap = 0.10*deq(d)`는 주석 처리). AET 자체는 잎이 있는 날 식생 증산, 잎이 없는 날 평형증발량의 25%이다. wetphytomass와 waste(각 aet의 1%)는 수요 계산에만 쓰인다.
- meanaet(month)는 mm/day 평균이며, 패키지 계측 코드는 nint(meanaet × days × 100)로 내보내고 100으로 나눠 mm/month(0.01 mm 단위)로 읽는다.
- 출력 PFT는 최종 선택 PFT(optpft)의 최적 LAI에서의 AET이다. PFT 14이면 목본 PFT(wdom)의 값이며 섞지 않는다. 노출 기반암 격자는 AET = 0, NPP = 0.
- 이 내용을 연구방법 식 (9) 설명 뒤에 추가하였다(이 브랜치의 `manuscript/METHODS_VeSLEM_FINAL_20261113_KO.md`).

## 5. EEMT 규모 비교 (a, b 재보정 없음)

| 출처 | 용늪 유역 평균 (21~0 ka) |
|---|---|
| R&T 2007 가우스식(MAT, MAP) | 14~33 MJ m⁻² yr⁻¹ |
| R&T 2007 월별식(Thornthwaite PET, Lieth NPP) | 58~93 |
| 최종 모델 B | 61~100 |
| 후보 C | 70~103 |

Pelletier et al.(2013) 식 (3)은 수증기압 부족량이 필요하고(CHELSA-TraCE21k에 없음), 결과 단위와 음수 처리가 논문에 적혀 있지 않아 그대로 적용하지 않았다. 같은 회귀식으로 계산한 Santa Catalina의 EEMT는 0~35 MJ(Pelletier et al., 2013), 5 미만~37 MJ(Rasmussen et al., 2015)로, 반건조 산지의 값이다. P&R 2009의 a = 0.037 m/kyr, b = 0.03 (MJ)⁻¹은 가우스식 EEMT로 맞춘 값이므로, 같은 a, b에 월별 EEMT를 넣으면 P0가 커진다(EEMT 33 MJ에서 0.10 m/kyr, 98 MJ에서 0.70 m/kyr). C는 B보다 EEMT가 5.2~9.9 MJ 크다. `comparison/item5_RT_scale_fab30.csv`

## 6. 세 경우 비교 (FAB30, Sc 0.7, 211시점)

| 항목 | A 음수 포함 | B 최종 | C 적설 |
|---|---|---|---|
| 유역 평균 EEMT, 동적 (21 ka → 0 ka) | 54.4 → 93.5 | 63.2 → 98.1 | 70.4 → 103.3 |
| 전 시점 평균 EEMT, 동적 | 75.8 | 83.2 | 90.1 |
| 0 ka 토심 평균 / 최소 / 최대 (m) | 1.78 / 0 / 3.78 | 1.86 / 0 / 3.99 | 1.94 / 0 / 4.19 |
| Jang 정적 / 동적 (/62) | 24 / 55 | 24 / 55 | 24 / 54 |
| Park PFT TSS 정적 / 동적 | 0.522 / 0.316 | 0.522 / 0.473 | 0.522 / 0.588 |
| DWD 제외 TSS 정적 / 동적 | 0.503 / 0.483 | 0.503 / 0.483 | 0.503 / 0.483 |
| DWD(PFT10, 사막 목본) 오탐 시점 (동적, /28) | 19 | 8 | 0 |
| PFT7(한대 낙엽수) 격자 수 (동적, 전 시점 평균 / 최대) | 19.1 / 38 | 19.5 / 38 | 15.5 / 35 |
| 2.7 ka PFT7 격자 | 33 | 19 | 4 |
| 3.5~2.0 ka 최대 산불일수, 동적 / 정적 | 56 / 0 | 56 / 0 | 55 / 0 |
| 3.5~2.0 ka 산불 격자 최대 | 54 | 50 | 35 |

- 검증군과 BIOME4 PFT의 대응은 `pb4studio/embedded_data/pft_groups_yongneup.csv`를 따른다: TBD = PFT4, BDE = PFT7(한대 낙엽수, Betula와 Salix), CON = PFT5와 6, TBE = PFT3, GRS = PFT8, DWD = PFT10(사막 목본, Ephedra).
- 동적 TSS 차이는 모두 DWD 한 군에서 나온다. 화분 기록에는 Ephedra가 없으므로, 유역의 1% 이상에 PFT10이 나타난 검증 시점 수가 그대로 오탐이 된다. DWD를 빼면 세 경우의 TSS는 같다. 나머지 군의 TP/FP/FN/TN은 세 경우가 같다(TBD 28/0/0/0, BDE 19/9/0/0, CON 26/2/0/0, TBE 0/0/0/28, GRS 0/0/25/3).
- PFT7(한대 낙엽수) 격자 수는 경우마다 다르지만 BDE 판정은 세 경우 모두 같다.
- 식생 변화의 순서(21 ka PFT6 전역 → 4 ka 무렵 PFT4 확장 → 1~0 ka PFT4 우점)는 세 경우가 같다. 차이는 얇은 토양 격자의 PFT7 수와 시점에 있다.
- C에서는 EEMT가 커져 토양이 두꺼워지고, 얇은 토양 격자의 PFT7과 PFT10이 줄어든다. TSS 상승은 PFT10 오탐이 사라진 결과이며, 이것만으로 식생 재현성이 나아졌다고 보지 않는다.

`comparison/summary.csv`, `comparison/eemt_soil_by_ka.csv`, `comparison/pft_counts_by_ka.csv`, `comparison/eemt_components_by_ka.csv`, `comparison/fire_3p5_2p0ka.csv`

## 파일

- `runs/negative_included/`, `runs/biome4_snow/`: 실행 요약 CSV와 상태 큐브. B는 `final_fab30_20261113/reference_run/`.
- `PACKAGE_FINAL_to_CANDIDATE.diff`: 최종 패키지 대비 변경(climate.py, config.py, 실행 스크립트). 기본값 `eemt_rule="freeze_zero"`로 다시 돌린 결과는 최종 실행과 모든 격자, 모든 시점에서 차이가 0이었다.
- `../../model/candidates/PB4Studio_v6.6.3_CHELSA21K_EEMTRULE_CANDIDATE.zip`: 후보 패키지. `PB4_EEMT_RULE`(freeze_zero, negative_included, biome4_snow)와 `PB4_OUT_DIR` 환경변수로 실행한다.
- `snow_check/`: BIOME4 원 서브루틴 추출본(subs.f), 검증 드라이버(drv.f, drv10.f), 계산 스크립트와 결과.
