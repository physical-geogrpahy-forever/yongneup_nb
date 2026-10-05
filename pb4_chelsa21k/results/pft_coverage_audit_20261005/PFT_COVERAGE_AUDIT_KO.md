# PB4-McKenzie-nativeClimate 21-0 ka PFT coverage audit

## 실행 지위

- 새 전체 실행: yes
- 모델: PB4-McKenzie-nativeClimate
- canonical SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- steps: static 211 + dynamic 211
- scientific model change: none
- audit-only change: optpft_node and full BIOME4 biome counts written into per-step summaries

## 실제 사용 PFT

| mode    |   pft |   timesteps_present |   total_cell_observations |   max_cells_in_timestep |   mean_cells_all_211_steps |   cell_weighted_mean_npp_gC_m2_yr |   oldest_age_ka_present |   youngest_age_ka_present | xue_forest_bridge_supported   |
|:--------|------:|--------------------:|--------------------------:|------------------------:|---------------------------:|----------------------------------:|------------------------:|--------------------------:|:------------------------------|
| static  |     4 |                  47 |                     11242 |                     298 |                  53.2796   |                           535.601 |                     4.8 |                       0   | True                          |
| static  |     6 |                 186 |                     51636 |                     298 |                 244.72     |                           385.526 |                    21   |                       0.2 | True                          |
| dynamic |     0 |                 145 |                      1231 |                      26 |                   5.83412  |                             0     |                    20.2 |                       5.7 | False                         |
| dynamic |     4 |                  47 |                     11099 |                     295 |                  52.6019   |                           535.535 |                     4.8 |                       0   | True                          |
| dynamic |     6 |                 186 |                     48107 |                     298 |                 227.995    |                           386.141 |                    21   |                       0.2 | True                          |
| dynamic |     7 |                 201 |                      2241 |                      31 |                  10.6209   |                           307.942 |                    20.3 |                       0   | True                          |
| dynamic |    10 |                  90 |                       200 |                       8 |                   0.947867 |                             6.08  |                    19.8 |                       6.2 | False                         |

## Xue forest bridge 밖의 실제 PFT

| mode    |   pft |   timesteps_present |   total_cell_observations |   max_cells_in_timestep |   mean_cells_all_211_steps |   cell_weighted_mean_npp_gC_m2_yr |   oldest_age_ka_present |   youngest_age_ka_present | xue_forest_bridge_supported   |
|:--------|------:|--------------------:|--------------------------:|------------------------:|---------------------------:|----------------------------------:|------------------------:|--------------------------:|:------------------------------|
| dynamic |    10 |                  90 |                       200 |                       8 |                   0.947867 |                              6.08 |                    19.8 |                       6.2 | False                         |

## 판정 원칙

- PFT4-7만 사용되면 현재 Xue/IBIS forest NPP+PFT -> AGB candidate를 바로 전체 실행할 수 있다.
- PFT1-3 또는 PFT8-14가 실제로 선택되면 임의 대응하지 않고 해당 PFT의 문헌 경로를 먼저 확정한다.
- PFT0은 비식생/무효 상태로 AGB=0 처리 가능한 별도 상태이며 unsupported vegetation PFT로 세지 않는다.
