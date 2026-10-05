# PFT-specific BIOME4 NPP to dry AGB candidate: full 21-0 ka test

## Status

This is a new full candidate execution. The canonical PB4-McKenzie-nativeClimate package is not overwritten.

- baseline SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- candidate SHA-256: e263789ba8a41e274e001c778295dd1b1b47ae96148be37b077c526a7b72d216
- candidate ZIP: pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_PFT_IBIS_AGB.zip
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- static and dynamic: 211 steps each

## Candidate bridge

AGB_dry [kg m-2] = coefficient(PFT) * NPP [g C m-2 yr-1]

PFT0=0; PFT4=0.0286; PFT5=0.0222; PFT6=0.0327; PFT7=0.0422; PFT10=0.00285.

Only this AGB bridge changes the geomorphic coupling. EEMT and all other production settings are unchanged. Legacy 0.010*NPP is calculated only as a diagnostic.

## Jang corrected 1% validation

| model                                   | mode    |   n |   correct_n |   accuracy_pct |   threshold_fraction |
|:----------------------------------------|:--------|----:|------------:|---------------:|---------------------:|
| PB4-McKenzie-nativeClimate-PFT-IBIS-AGB | static  |  62 |          24 |        38.7097 |                 0.01 |
| PB4-McKenzie-nativeClimate-PFT-IBIS-AGB | dynamic |  62 |          55 |        88.7097 |                 0.01 |

## AGB comparison with legacy 0.010*NPP

| mode    |   n_timesteps |   candidate_time_mean_of_cell_means_kg_m2 |   candidate_min_time_mean_kg_m2 |   candidate_max_time_mean_kg_m2 |   candidate_absolute_max_kg_m2 |   legacy_time_mean_of_cell_means_kg_m2 |   legacy_min_time_mean_kg_m2 |   legacy_max_time_mean_kg_m2 |   mean_candidate_to_legacy_ratio |   median_candidate_to_legacy_ratio_across_steps |
|:--------|--------------:|------------------------------------------:|--------------------------------:|--------------------------------:|-------------------------------:|---------------------------------------:|-----------------------------:|-----------------------------:|---------------------------------:|------------------------------------------------:|
| dynamic |           211 |                                   12.8357 |                         7.70585 |                         17.564  |                        20.7202 |                                4.00357 |                      2.35218 |                       6.1107 |                          3.23083 |                                            3.27 |
| static  |           211 |                                   13.0915 |                         7.8807  |                         17.5884 |                        17.589  |                                4.12358 |                      2.41    |                       6.1498 |                          3.1967  |                                            3.27 |

## PFT contributions

| mode    |   pft |   total_cell_observations |   sum_agb_over_cell_observations_kg_m2 |   timesteps_present |
|:--------|------:|--------------------------:|---------------------------------------:|--------------------:|
| dynamic |     0 |                      1257 |                                0       |                 136 |
| dynamic |     4 |                     11088 |                           169826       |                  47 |
| dynamic |     5 |                         0 |                                0       |                   0 |
| dynamic |     6 |                     47557 |                           600454       |                 186 |
| dynamic |     7 |                      2779 |                            36797.4     |                 201 |
| dynamic |    10 |                       197 |                                3.46275 |                  85 |
| static  |     0 |                         0 |                                0       |                   0 |
| static  |     4 |                     11242 |                           172207       |                  47 |
| static  |     5 |                         0 |                                0       |                   0 |
| static  |     6 |                     51636 |                           650960       |                 186 |
| static  |     7 |                         0 |                                0       |                   0 |
| static  |    10 |                         0 |                                0       |                   0 |

## Promotion status

Candidate only. Promotion requires checking physical AGB magnitude, dynamic geomorphic response, and validation relative to the canonical baseline.
