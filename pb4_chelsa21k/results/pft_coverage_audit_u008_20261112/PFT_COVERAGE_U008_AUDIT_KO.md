# PB4Studio U008 CHELSA21K 21-0 ka PFT coverage audit

## 실행 지위

- 새 전체 실행: yes
- 모델: 6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008
- canonical SHA-256: 0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- steps: static 211 + dynamic 211
- scientific model change: none
- production: U=0.08 m/kyr; BIOME4-derived AGB* (Reich 1992; Haxeltine & Prentice 1996 Eq.34)
- audit-only change: optpft_node and full BIOME4 biome counts written into per-step summaries

## 실제 사용 PFT

| mode    |   pft |   timesteps_present |   total_cell_observations |   max_cells_in_timestep |   mean_cells_all_211_steps |   cell_weighted_mean_npp_gC_m2_yr |   oldest_age_ka_present |   youngest_age_ka_present | xue_forest_bridge_supported   |
|:--------|------:|--------------------:|--------------------------:|------------------------:|---------------------------:|----------------------------------:|------------------------:|--------------------------:|:------------------------------|
| static  |     4 |                  47 |                     11241 |                     298 |                  53.2749   |                         535.603   |                     4.8 |                       0   | True                          |
| static  |     6 |                 186 |                     51637 |                     298 |                 244.725    |                         385.528   |                    21   |                       0.2 | True                          |
| dynamic |     0 |                 145 |                      1225 |                      26 |                   5.80569  |                           0       |                    20.2 |                       5.7 | False                         |
| dynamic |     4 |                  47 |                     11071 |                     295 |                  52.4692   |                         535.635   |                     4.8 |                       0   | True                          |
| dynamic |     6 |                 186 |                     48154 |                     298 |                 228.218    |                         386.244   |                    21   |                       0.2 | True                          |
| dynamic |     7 |                 201 |                      2226 |                      31 |                  10.5498   |                         307.2     |                    20.3 |                       0   | True                          |
| dynamic |    10 |                  91 |                       202 |                       8 |                   0.957346 |                           6.01485 |                    19.8 |                       6.2 | False                         |

## Xue forest bridge 밖의 실제 PFT

| mode    |   pft |   timesteps_present |   total_cell_observations |   max_cells_in_timestep |   mean_cells_all_211_steps |   cell_weighted_mean_npp_gC_m2_yr |   oldest_age_ka_present |   youngest_age_ka_present | xue_forest_bridge_supported   |
|:--------|------:|--------------------:|--------------------------:|------------------------:|---------------------------:|----------------------------------:|------------------------:|--------------------------:|:------------------------------|
| dynamic |    10 |                  91 |                       202 |                       8 |                   0.957346 |                           6.01485 |                    19.8 |                       6.2 | False                         |

## 판정 원칙

- PFT4-7만 사용되면 현재 Xue/IBIS forest NPP+PFT -> AGB candidate를 바로 전체 실행할 수 있다.
- PFT1-3 또는 PFT8-14가 실제로 선택되면 임의 대응하지 않고 해당 PFT의 문헌 경로를 먼저 확정한다.
- PFT0은 비식생/무효 상태로 AGB=0 처리 가능한 별도 상태이며 unsupported vegetation PFT로 세지 않는다.
