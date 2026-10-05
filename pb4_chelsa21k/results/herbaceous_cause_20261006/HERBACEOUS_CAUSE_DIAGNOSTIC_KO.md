# Herbaceous PFT disappearance diagnostic

Controlled model checks using the PB4 depth-sensitivity runner.

Scenarios:
- historical Beyer sensitivity table preserved inside the final package
- CHELSA with the earlier tuned PFT5/PFT6 climate sieve package from commit 9afe8ce
- CHELSA with the final native BIOME4 PFT climate limits

## Summary

| scenario         |   age_ka |   n_depths |   min_depth_m |   max_depth_m |   n_herb_open_opt_depths |   herb_open_opt_pfts |   herb_open_opt_depth_min_m |   herb_open_opt_depth_max_m |   n_pft8_positive_depths |   pft8_max_npp |   pft4_max_npp |   pft6_max_npp |
|:-----------------|---------:|-----------:|--------------:|--------------:|-------------------------:|---------------------:|----------------------------:|----------------------------:|-------------------------:|---------------:|---------------:|---------------:|
| CHELSA_native    |      2   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        415.409 |        528.75  |        516.586 |
| CHELSA_native    |      2.2 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        415.12  |        528.371 |        516.106 |
| CHELSA_native    |      2.3 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        418.961 |        532.046 |        515.911 |
| CHELSA_native    |      2.5 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        412.93  |        524.76  |        509.716 |
| CHELSA_native    |      2.7 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        419.918 |        531.729 |        512.969 |
| CHELSA_native    |      3   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        416.68  |        528.214 |        508.471 |
| CHELSA_native    |      4   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        405.498 |        515.995 |        495.547 |
| CHELSA_native    |      5   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        383.926 |        494.003 |        472.414 |
| CHELSA_tuned     |      2   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        415.409 |        528.75  |        516.586 |
| CHELSA_tuned     |      2.2 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        415.12  |        528.371 |        516.106 |
| CHELSA_tuned     |      2.3 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        418.961 |        532.046 |        515.911 |
| CHELSA_tuned     |      2.5 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        412.93  |        524.76  |        509.716 |
| CHELSA_tuned     |      2.7 |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        419.918 |        531.729 |        512.969 |
| CHELSA_tuned     |      3   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        416.68  |        528.214 |        508.471 |
| CHELSA_tuned     |      4   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        405.498 |        515.995 |        495.547 |
| CHELSA_tuned     |      5   |         14 |          0.01 |          1.5  |                        0 |                      |                      nan    |                      nan    |                       11 |        383.926 |        494.003 |        472.414 |
| historical_Beyer |      0   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        607.442 |        724.979 |        641.46  |
| historical_Beyer |      1   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        543.073 |        657.626 |        584.542 |
| historical_Beyer |      2   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        521.461 |        634.369 |          0     |
| historical_Beyer |      3   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        502.059 |        610.94  |        555.249 |
| historical_Beyer |      4   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        495.729 |        603.826 |          0     |
| historical_Beyer |      5   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        454.817 |        550.871 |          0     |
| historical_Beyer |      6   |         11 |          0.05 |          1.94 |                        1 |                    8 |                        0.05 |                        0.05 |                       11 |        468.246 |        570.897 |          0     |

## Common-grid direct comparison

|   age_ka |   depth_m |   beyer_optpft |   chelsa_tuned_optpft |   chelsa_native_optpft |   beyer_pft8_npp |   chelsa_tuned_pft8_npp |   chelsa_native_pft8_npp |
|---------:|----------:|---------------:|----------------------:|-----------------------:|-----------------:|------------------------:|-------------------------:|
|        2 |      0.05 |              8 |                     7 |                      7 |          377.775 |                 343.583 |                  343.583 |
|        2 |      0.1  |              4 |                     7 |                      7 |          508.462 |                 415.409 |                  415.409 |
|        2 |      0.2  |              4 |                     4 |                      4 |          521.461 |                 415.24  |                  415.24  |
|        2 |      0.3  |              4 |                     4 |                      4 |          519.169 |                 413.966 |                  413.966 |
|        2 |      0.5  |              4 |                     4 |                      4 |          518.624 |                 412.401 |                  412.401 |
|        2 |      1.5  |              4 |                     4 |                      4 |          518.624 |                 412.401 |                  412.401 |
|        3 |      0.05 |              8 |                     7 |                      7 |          355.586 |                 343.601 |                  343.601 |
|        3 |      0.1  |              6 |                     7 |                      7 |          490.33  |                 416.68  |                  416.68  |
|        3 |      0.2  |              4 |                     4 |                      4 |          502.059 |                 416.552 |                  416.552 |
|        3 |      0.3  |              4 |                     4 |                      4 |          499.664 |                 415.095 |                  415.095 |
|        3 |      0.5  |              4 |                     4 |                      4 |          499.528 |                 413.791 |                  413.791 |
|        3 |      1.5  |              4 |                     4 |                      4 |          499.528 |                 413.791 |                  413.791 |
|        4 |      0.05 |              8 |                     7 |                      7 |          369.542 |                 338.538 |                  338.538 |
|        4 |      0.1  |              4 |                     7 |                      7 |          488.387 |                 405.498 |                  405.498 |
|        4 |      0.2  |              4 |                     6 |                      6 |          495.729 |                 405.375 |                  405.375 |
|        4 |      0.3  |              4 |                     6 |                      6 |          493.177 |                 403.87  |                  403.87  |
|        4 |      0.5  |              4 |                     6 |                      6 |          493.044 |                 402.579 |                  402.579 |
|        4 |      1.5  |              4 |                     6 |                      6 |          493.044 |                 402.579 |                  402.579 |
|        5 |      0.05 |              8 |                     7 |                      7 |          342.326 |                 322.395 |                  322.395 |
|        5 |      0.1  |              4 |                     7 |                      7 |          443.763 |                 383.926 |                  383.926 |
|        5 |      0.2  |              4 |                     6 |                      6 |          454.817 |                 383.807 |                  383.807 |
|        5 |      0.3  |              4 |                     6 |                      6 |          452.607 |                 382.073 |                  382.073 |
|        5 |      0.5  |              4 |                     6 |                      6 |          452.049 |                 381.155 |                  381.155 |
|        5 |      1.5  |              4 |                     6 |                      6 |          452.049 |                 381.155 |                  381.155 |


## 해석

이번 진단에서 가장 명확한 결과는 다음과 같다.

1. CHELSA forcing을 사용할 경우, PFT5/PFT6 climate sieve를 이전 tuned 설정으로 두어도 최종 native BIOME4 설정으로 되돌려도 결과가 동일했다.
2. 따라서 최종 production에서 침엽수 온도보정을 제거한 것이 후기 홀로세 초본 우점 소실의 원인은 아니다.
3. historical Beyer sensitivity에서는 0, 1, 2, 3, 4, 5, 6 ka 모두 토심 0.05 m에서 PFT8이 optPFT였다.
4. 같은 공통 age-depth grid에서 CHELSA tuned와 CHELSA native는 모두 0.05 m에서 PFT7이 optPFT였다.
5. CHELSA에서 PFT8 자체가 사라진 것은 아니다. 시험한 각 시점에서 PFT8 NPP는 여러 토심에서 양수였으나 경쟁에서 우점하지 못했다.

대표적인 0.05 m 결과:

| age | historical Beyer optPFT | CHELSA tuned optPFT | CHELSA native optPFT |
|---:|---:|---:|---:|
| 5 ka | 8 | 7 | 7 |
| 4 ka | 8 | 7 | 7 |
| 3 ka | 8 | 7 | 7 |
| 2 ka | 8 | 7 | 7 |

4 ka, 0.05 m의 raw NPP:

| scenario | PFT4 | PFT6 | PFT7 | PFT8 | optPFT |
|---|---:|---:|---:|---:|---:|
| historical Beyer | 377.68 | 0.00 | 0.00 | 369.54 | 8 |
| CHELSA tuned | 361.94 | 297.81 | 394.60 | 338.54 | 7 |
| CHELSA native | 361.94 | 297.81 | 394.60 | 338.54 | 7 |

5 ka, 0.05 m에서도 historical Beyer는 PFT8이 우점하지만 CHELSA에서는 PFT7이 우점한다.

따라서 현재 결과는 다음과 같이 판정한다.

**초본류가 생리적으로 제거된 것이 아니라, CHELSA forcing 하에서 tree PFT, 특히 PFT7이 얕은 토양에서도 더 경쟁력 있게 남아 PFT8의 우점을 차단한다.**

PFT climate tuning 제거 여부는 동일 CHELSA 조건에서 결과가 정확히 동일하므로 원인에서 제외할 수 있다.

다만 historical Beyer 표는 과거 실행 산출물이며, 현재 최종 코드에 원 Beyer NetCDF를 다시 넣어 같은 코드와 같은 설정에서 climate forcing만 단독 교체한 신규 A/B 실행은 아니다. 따라서 가장 강한 원인은 Beyer -> CHELSA forcing 변경으로 판단되지만, 엄밀한 단일요인 인과확정에는 원 Beyer forcing을 현재 최종 코드에 재입력하는 추가 실험이 필요하다.


## 2026-10-06 current-final-code Beyer 재실행에 따른 정정

이전 진단에서 historical Beyer sensitivity table의 PFT8 출현을 climate-forcing 차이의 직접 증거로 해석했으나, current final PB4 code에 동일 packaged Beyer forcing을 다시 넣어 실행한 결과 이 해석은 수정해야 한다.

current final code + Beyer의 동일 depth sweep에서 0-6 ka, 토심 0.01-1.50 m의 모든 시험점에서 PFT8 optPFT는 0회였다.

대표 4 ka, 0.05 m:

- PFT4 NPP = 297.15
- PFT6 NPP = 265.14
- PFT7 NPP = 335.32
- PFT8 NPP = 265.00
- optPFT = 7

2.2-2.7 ka, 0.05 m에서도 PFT7 NPP는 약 339.7-351.4로 PFT8의 약 265.9-277.2보다 높았고 모두 optPFT 7이었다.

또한 current final code + Beyer full 21 ka spatial run에서도 PFT8은 static/dynamic 모두 0개 시점에서 우점했다. 따라서 **Beyer로 forcing만 되돌리는 것으로 temperate grass는 복구되지 않는다.**

historical Beyer sensitivity와 current-final Beyer의 차이는 old sensitivity의 climate treatment까지 포함한 implementation history에서 발생한다. current final code는 Beyer 0.5-degree panel을 reference elevation 590.4 m로 해석하고 월별 lapse rate를 이용해 실제 DEM elevation으로 하향보정한다. 패널 590.4 m에서 Yongneup 약 1162 m로의 여름 보정량은 대략 -3.1~-3.3°C이므로, 과거 raw Beyer TWM 약 22°C를 그대로 사용한 경우와 달리 PFT7의 native upper TWM 21°C constraint를 통과시킬 수 있다.

따라서 과거 5 cm PFT8은 현재 증거상 **Beyer 자체의 본질적 효과라기보다, 당시 raw panel climate를 site elevation으로 충분히 하향보정하지 않았던 설정과 결부된 결과**로 보는 것이 가장 타당하다.

current final code에서는 CHELSA와 lapse-corrected Beyer 모두 PFT7이 활성화되고 PFT8을 경쟁에서 억제한다. 그러므로 현재 temperate grass 문제는 forcing 선택보다 PFT7-PFT8 competition 및 지역 peatland/open-habitat process의 표현 문제로 재정의한다.

근거 결과:
- `pb4_chelsa21k/results/beyer_current_final_depth_20261006/`
- `pb4_chelsa21k/results/herbaceous_cause_20261006/BEYER_FINAL_CODE_FULL_RUN_SUMMARY_KO.md`
