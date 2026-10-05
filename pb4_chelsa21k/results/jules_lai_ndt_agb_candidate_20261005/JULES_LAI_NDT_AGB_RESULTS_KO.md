# BIOME4 optLAI to JULES/TRIFFID dry AGB candidate (NDT PFT7): full 21-0 ka test

## Status

This is a new full candidate execution. The canonical PB4-McKenzie-nativeClimate package is not overwritten.

- baseline SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- candidate SHA-256: 1a369d9db3092e90473e696c909939a4968daa14de1ce2628b248dfa78781745
- candidate ZIP: pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_JULES_LAI_NDT_AGB.zip
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- static and dynamic: 211 steps each

## Candidate bridge

AGB_dry [kg dry m-2] = LMA(PFT)*optLAI + 0.75*awl(PFT)*optLAI^(5/3)/0.5

PFT4=BDT; PFT5/6=NET; PFT7=NDT; PFT10=ESH. Exact parameters are recorded in provenance.

Only this AGB bridge changes the geomorphic coupling. EEMT and all other production settings are unchanged. Legacy 0.010*NPP is retained only as a diagnostic comparator.

## Jang corrected 1% validation

| model                                        | mode    |   n |   correct_n |   accuracy_pct |   threshold_fraction |
|:---------------------------------------------|:--------|----:|------------:|---------------:|---------------------:|
| PB4-McKenzie-nativeClimate-JULES-LAI-NDT-AGB | static  |  62 |          24 |        38.7097 |                 0.01 |
| PB4-McKenzie-nativeClimate-JULES-LAI-NDT-AGB | dynamic |  62 |          55 |        88.7097 |                 0.01 |

## AGB comparison with legacy 0.010*NPP

| mode    |   n_timesteps |   candidate_time_mean_of_cell_means_kg_m2 |   candidate_min_time_mean_kg_m2 |   candidate_max_time_mean_kg_m2 |   candidate_absolute_max_kg_m2 |   legacy_time_mean_of_cell_means_kg_m2 |   legacy_min_time_mean_kg_m2 |   legacy_max_time_mean_kg_m2 |   mean_candidate_to_legacy_ratio |   median_candidate_to_legacy_ratio_across_steps |
|:--------|--------------:|------------------------------------------:|--------------------------------:|--------------------------------:|-------------------------------:|---------------------------------------:|-----------------------------:|-----------------------------:|---------------------------------:|------------------------------------------------:|
| dynamic |           211 |                                   6.18522 |                         4.34518 |                         8.40246 |                       11.1406  |                                4.00849 |                      2.35218 |                      6.11319 |                          1.56729 |                                         1.49932 |
| static  |           211 |                                   6.32156 |                         4.43796 |                         8.45446 |                        8.52348 |                                4.12358 |                      2.41    |                      6.1498  |                          1.55854 |                                         1.49972 |

## PFT contributions

| mode    |   pft |   total_cell_observations |   sum_agb_over_cell_observations_kg_m2 |   timesteps_present |
|:--------|------:|--------------------------:|---------------------------------------:|--------------------:|
| dynamic |     0 |                      1247 |                                0       |                 143 |
| dynamic |     4 |                     11101 |                            86166.8     |                  47 |
| dynamic |     5 |                         0 |                                0       |                   0 |
| dynamic |     6 |                     47950 |                           287972       |                 188 |
| dynamic |     7 |                      2394 |                            14773.4     |                 200 |
| dynamic |    10 |                       186 |                                2.41171 |                  83 |
| static  |     0 |                         0 |                                0       |                   0 |
| static  |     4 |                     11242 |                            87295.8     |                  47 |
| static  |     5 |                         0 |                                0       |                   0 |
| static  |     6 |                     51636 |                           310191       |                 186 |
| static  |     7 |                         0 |                                0       |                   0 |
| static  |    10 |                         0 |                                0       |                   0 |

## Promotion status

Candidate only. Promotion requires checking physical AGB magnitude, dynamic geomorphic response, and validation relative to the canonical baseline.
