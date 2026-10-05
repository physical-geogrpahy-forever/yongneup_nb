# BIOME4 optLAI + Reich leaf + BIOME4 sapwood AGB proxy: full 21-0 ka test

## Status

This is a new full candidate execution. The canonical PB4-McKenzie-nativeClimate package is not overwritten.

- baseline SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- candidate SHA-256: 1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c
- candidate ZIP: pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- static and dynamic: 211 steps each

## Candidate bridge

B_leaf,dry = 0.03630780547701014 * optLAI * L_m^0.43.

B_sapwood,dry = optLAI where BIOME4 pftpar(pft,10)=1, otherwise 0.

AGB*_dry = B_leaf,dry + B_sapwood,dry. Exact PFT parameters are recorded in provenance.

Only this AGB bridge changes the geomorphic coupling. EEMT and all other production settings are unchanged. Legacy 0.010*NPP is retained only as a diagnostic comparator. References: Reich et al. (1992), Ecological Monographs 62:365-392; Haxeltine & Prentice (1996), Global Biogeochemical Cycles 10:693-709; BIOME4 v4.2b2 source pftdata/respiration.

## Jang corrected 1% validation

| model                                            | mode    |   n |   correct_n |   accuracy_pct |   threshold_fraction |
|:-------------------------------------------------|:--------|----:|------------:|---------------:|---------------------:|
| PB4-McKenzie-nativeClimate-REICH-LAI-SAPWOOD-AGB | static  |  62 |          24 |        38.7097 |                 0.01 |
| PB4-McKenzie-nativeClimate-REICH-LAI-SAPWOOD-AGB | dynamic |  62 |          55 |        88.7097 |                 0.01 |

## AGB comparison with legacy 0.010*NPP

| mode    |   n_timesteps |   candidate_time_mean_of_cell_means_kg_m2 |   candidate_min_time_mean_kg_m2 |   candidate_max_time_mean_kg_m2 |   candidate_absolute_max_kg_m2 |   legacy_time_mean_of_cell_means_kg_m2 |   legacy_min_time_mean_kg_m2 |   legacy_max_time_mean_kg_m2 |   mean_candidate_to_legacy_ratio |   median_candidate_to_legacy_ratio_across_steps |
|:--------|--------------:|------------------------------------------:|--------------------------------:|--------------------------------:|-------------------------------:|---------------------------------------:|-----------------------------:|-----------------------------:|---------------------------------:|------------------------------------------------:|
| dynamic |           211 |                                   3.116   |                         2.52364 |                         3.5319  |                        4.26113 |                                4.00976 |                      2.35128 |                      6.10805 |                         0.809652 |                                        0.768519 |
| static  |           211 |                                   3.19979 |                         2.63126 |                         3.53755 |                        3.59854 |                                4.12358 |                      2.41    |                      6.1498  |                         0.803978 |                                        0.768519 |

## PFT contributions

| mode    |   pft |   total_cell_observations |   sum_agb_over_cell_observations_kg_m2 |   timesteps_present |
|:--------|------:|--------------------------:|---------------------------------------:|--------------------:|
| dynamic |     0 |                      1227 |                                 0      |                 145 |
| dynamic |     1 |                         0 |                                 0      |                   0 |
| dynamic |     2 |                         0 |                                 0      |                   0 |
| dynamic |     3 |                         0 |                                 0      |                   0 |
| dynamic |     4 |                     11102 |                             36715.4    |                  47 |
| dynamic |     5 |                         0 |                                 0      |                   0 |
| dynamic |     6 |                     48115 |                            152801      |                 187 |
| dynamic |     7 |                      2234 |                              6396.13   |                 201 |
| dynamic |     8 |                         0 |                                 0      |                   0 |
| dynamic |     9 |                         0 |                                 0      |                   0 |
| dynamic |    10 |                       200 |                                15.1038 |                  89 |
| dynamic |    11 |                         0 |                                 0      |                   0 |
| dynamic |    12 |                         0 |                                 0      |                   0 |
| dynamic |    13 |                         0 |                                 0      |                   0 |
| static  |     0 |                         0 |                                 0      |                   0 |
| static  |     1 |                         0 |                                 0      |                   0 |
| static  |     2 |                         0 |                                 0      |                   0 |
| static  |     3 |                         0 |                                 0      |                   0 |
| static  |     4 |                     11242 |                             37187.2    |                  47 |
| static  |     5 |                         0 |                                 0      |                   0 |
| static  |     6 |                     51636 |                            164009      |                 186 |
| static  |     7 |                         0 |                                 0      |                   0 |
| static  |     8 |                         0 |                                 0      |                   0 |
| static  |     9 |                         0 |                                 0      |                   0 |
| static  |    10 |                         0 |                                 0      |                   0 |
| static  |    11 |                         0 |                                 0      |                   0 |
| static  |    12 |                         0 |                                 0      |                   0 |
| static  |    13 |                         0 |                                 0      |                   0 |

## Promotion status

Candidate only. Promotion requires checking physical AGB magnitude, dynamic geomorphic response, and validation relative to the canonical baseline.
