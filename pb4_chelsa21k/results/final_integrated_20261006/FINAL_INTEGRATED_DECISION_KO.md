# PB4 final integrated production result

Final SHA-256: a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34

## Scientific configuration

- BIOME4 v4.2b2 native PFT climate limits
- McKenzie AWC and finite-depth root coupling
- BIOME4-derived AGB*
- Pelletier geomorphic coupling with kd=0.033 EEMT + 0.05 AGB*
- Pelletier direct exponential EEMT-to-AGB equation not used

## Primary Jang validation

| model                             | mode    |   n |   correct_n |   accuracy_pct |   threshold_fraction |
|:----------------------------------|:--------|----:|------------:|---------------:|---------------------:|
| PB4-FINAL-nativeClimate-BIOME4AGB | static  |  62 |          24 |        38.7097 |                 0.01 |
| PB4-FINAL-nativeClimate-BIOME4AGB | dynamic |  62 |          55 |        88.7097 |                 0.01 |

## AGB

| mode    |   n_timesteps |   time_mean_agb_kg_m2 |   min_time_mean_agb_kg_m2 |   max_time_mean_agb_kg_m2 |   absolute_max_agb_kg_m2 |   modern_0ka_agb_kg_m2 |   modern_0ka_agb_t_ha |
|:--------|--------------:|----------------------:|--------------------------:|--------------------------:|-------------------------:|-----------------------:|----------------------:|
| dynamic |           211 |               3.116   |                   2.52364 |                   3.5319  |                  4.26113 |                3.4662  |               34.662  |
| static  |           211 |               3.19979 |                   2.63126 |                   3.53755 |                  3.59854 |                3.48349 |               34.8349 |

## Park et al. (2021)

Park is an independent holdout evaluation. It is not included in the Jang 62-item accuracy and is not used for parameter tuning. Sample-level Supplementary pollen composition will be evaluated in 100-year windows without interpolation after the raw Supplementary table is archived.
