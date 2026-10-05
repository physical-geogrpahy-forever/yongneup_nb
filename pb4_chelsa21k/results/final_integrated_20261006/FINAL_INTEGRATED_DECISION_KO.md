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

Park et al. (2021)은 independent holdout으로 완료하였다. 사용자가 제공한 Supplementary Excel의 sample-level pollen, PCA, temperature reconstruction을 직접 사용했고, 주 정량구간 16-69 cm의 53 samples를 17개 100년 window로 집계하였다. Park PC2와 dynamic PB4 cold-tree PFT fraction은 Spearman rho=0.632, p=0.00644로 유의한 같은 방향의 관계를 보였으나 static은 rho=-0.255, p=0.323이었다. pollen broadleaf fraction과 dynamic model fraction은 rho=0.448, p=0.0713으로 양의 경향이나 0.05 기준에서 유의하지 않았다. 2738-2206 cal yr BP open-vegetation event는 open PFT로 재현되지 않았다. Park 결과는 모델 재보정에 사용하지 않는다.

상세: `PARK2021_HOLDOUT_RESULT_20261006_KO.md`
