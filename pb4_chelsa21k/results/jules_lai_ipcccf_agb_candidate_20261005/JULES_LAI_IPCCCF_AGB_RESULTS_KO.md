# BIOME4 optLAI -> JULES/TRIFFID dry AGB candidate with IPCC carbon fractions

## 실행 상태
- 새 21-0 ka 전체 실행
- static 211 + dynamic 211, PFT7 BDT/NDT 두 시나리오
- canonical baseline은 변경하지 않음
- AGB bridge만 교체

## 식
AGBdry = LMA * LAI + 0.75 * [awl * LAI^(5/3)] / fCwood(PFT)

BIOME4 dominant PFT의 optLAI(lai_node)를 JULES balanced/full-leaf seasonal maximum LAI의 analogue로 사용한다.

## PFT mapping
- PFT4 -> BDT: LMA 0.0823, awl 0.78
- PFT5 -> NET: LMA 0.2263, awl 0.65
- PFT6 -> NET: LMA 0.2263, awl 0.65
- PFT7 -> BDT and NDT both executed
- PFT10 -> evergreen shrub: LMA 0.1515, awl 0.13
- wood carbon fractions: BDT 0.48, NET/NDT 0.51, PFT10 fallback 0.47 (IPCC 2006 Table 4.3)

PFT10의 75:25 above/below woody split은 forest-derived Wolf et al. 관계를 shrub에 확장한 sensitivity 가정이며 최종 채택 근거로 간주하지 않는다.

## AGB summary
| scenario   | mode    |   n_timesteps |   candidate_time_mean_of_cell_means_kg_m2 |   candidate_min_time_mean_kg_m2 |   candidate_max_time_mean_kg_m2 |   candidate_absolute_max_kg_m2 |   fc04_time_mean_of_cell_means_kg_m2 |   legacy_time_mean_of_cell_means_kg_m2 |   mean_lai |   max_lai |
|:-----------|:--------|--------------:|------------------------------------------:|--------------------------------:|--------------------------------:|-------------------------------:|-------------------------------------:|---------------------------------------:|-----------:|----------:|
| BDT        | dynamic |           211 |                                   6.1619  |                         4.27101 |                         8.73897 |                       11.2406  |                              7.58942 |                                4.0088  |    2.80515 |      3.73 |
| BDT        | static  |           211 |                                   6.29094 |                         4.36116 |                         8.79571 |                        8.86755 |                              7.76154 |                                4.12358 |    2.82893 |      3.23 |
| NDT        | dynamic |           211 |                                   6.15534 |                         4.26992 |                         8.74528 |                       10.9295  |                              7.59764 |                                4.00869 |    2.80493 |      3.73 |
| NDT        | static  |           211 |                                   6.29094 |                         4.36116 |                         8.79571 |                        8.86755 |                              7.76154 |                                4.12358 |    2.82893 |      3.23 |

## Jang 2011 corrected 1% validation
| model                                                    | mode    |   n |   correct_n |   accuracy_pct |   threshold_fraction | scenario   |
|:---------------------------------------------------------|:--------|----:|------------:|---------------:|---------------------:|:-----------|
| PB4-McKenzie-nativeClimate-JULES-LAI-IPCCCF-AGB-PFT7-BDT | static  |  62 |          24 |        38.7097 |                 0.01 | BDT        |
| PB4-McKenzie-nativeClimate-JULES-LAI-IPCCCF-AGB-PFT7-BDT | dynamic |  62 |          55 |        88.7097 |                 0.01 | BDT        |
| PB4-McKenzie-nativeClimate-JULES-LAI-IPCCCF-AGB-PFT7-NDT | static  |  62 |          24 |        38.7097 |                 0.01 | NDT        |
| PB4-McKenzie-nativeClimate-JULES-LAI-IPCCCF-AGB-PFT7-NDT | dynamic |  62 |          55 |        88.7097 |                 0.01 | NDT        |

## PFT contribution
| scenario   | mode    |   pft |   total_cell_observations |   sum_agb_over_cell_observations_kg_m2 |   cell_weighted_mean_agb_kg_m2 |   cell_weighted_mean_lai |
|:-----------|:--------|------:|--------------------------:|---------------------------------------:|-------------------------------:|-------------------------:|
| BDT        | dynamic |     0 |                      1245 |                                0       |                      0         |                0         |
| BDT        | dynamic |     4 |                     11100 |                            89633       |                      8.07505   |                3.05131   |
| BDT        | dynamic |     5 |                         0 |                                0       |                    nan         |              nan         |
| BDT        | dynamic |     6 |                     47964 |                           282997       |                      5.9002    |                2.77978   |
| BDT        | dynamic |     7 |                      2388 |                            14815.6     |                      6.20418   |                2.53867   |
| BDT        | dynamic |    10 |                       181 |                                2.36288 |                      0.0130546 |                0.0692265 |
| BDT        | static  |     0 |                         0 |                                0       |                    nan         |              nan         |
| BDT        | static  |     4 |                     11242 |                            90815.4     |                      8.07823   |                3.05204   |
| BDT        | static  |     5 |                         0 |                                0       |                    nan         |              nan         |
| BDT        | static  |     6 |                     51636 |                           304746       |                      5.90181   |                2.78036   |
| BDT        | static  |     7 |                         0 |                                0       |                    nan         |              nan         |
| BDT        | static  |    10 |                         0 |                                0       |                    nan         |              nan         |
| NDT        | dynamic |     0 |                      1244 |                                0       |                      0         |                0         |
| NDT        | dynamic |     4 |                     11100 |                            89632.9     |                      8.07503   |                3.05131   |
| NDT        | dynamic |     5 |                         0 |                                0       |                    nan         |              nan         |
| NDT        | dynamic |     6 |                     47966 |                           283010       |                      5.90023   |                2.77978   |
| NDT        | dynamic |     7 |                      2384 |                            14389.9     |                      6.03603   |                2.53697   |
| NDT        | dynamic |    10 |                       184 |                                2.38329 |                      0.0129526 |                0.06875   |
| NDT        | static  |     0 |                         0 |                                0       |                    nan         |              nan         |
| NDT        | static  |     4 |                     11242 |                            90815.4     |                      8.07823   |                3.05204   |
| NDT        | static  |     5 |                         0 |                                0       |                    nan         |              nan         |
| NDT        | static  |     6 |                     51636 |                           304746       |                      5.90181   |                2.78036   |
| NDT        | static  |     7 |                         0 |                                0       |                    nan         |              nan         |
| NDT        | static  |    10 |                         0 |                                0       |                    nan         |              nan         |

## 판정
이 실행은 JULES 기본 allometry를 BIOME4 optLAI에 전이한 sensitivity candidate이다. production 채택은 독립 LAI-AGB 검증과 PFT10 처리 검토 뒤 별도 판단한다.
