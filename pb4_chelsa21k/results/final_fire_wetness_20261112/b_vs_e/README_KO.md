# PB4 U008 wetness normalization B vs E fire experiment — 2026-11-12

## Definition
- B: root-normalized daily fire wetness `wr_n = wr/max(rtop_eff+rbot_eff,1e-6)`; all other B settings unchanged.
- E: identical to B except daily fire wetness is top-layer relative soil water `w(1)`.
- Native fire thresholds, +0.05 partial-burn interval, and NPP<1000 fuel scaling are unchanged.
- `raw_drydays` is diagnostic-only fire days before the NPP/1000 scaling.

## Run status
- B static+dynamic: 211+211 steps, exit code 0
- E static+dynamic: 211+211 steps, exit code 0

## Jang
| variant   | model_mode   |   correct_n |   n |   accuracy_pct |
|:----------|:-------------|------------:|----:|---------------:|
| B         | static       |          24 |  62 |        38.7097 |
| B         | dynamic      |          55 |  62 |        88.7097 |
| E         | static       |          24 |  62 |        38.7097 |
| E         | dynamic      |          55 |  62 |        88.7097 |

## Changed optPFT/biome cell-times
- total: 0

- static: 0
- dynamic: 0

## Shallow (<0.3 m in both B and E) equality
| model_mode   | criterion                   | variable            |   n_cell_times |   n_equal |   n_different |   max_abs_diff |
|:-------------|:----------------------------|:--------------------|---------------:|----------:|--------------:|---------------:|
| static       | B_depth<0.3 AND E_depth<0.3 | firedays_node       |              0 |         0 |             0 |            nan |
| static       | B_depth<0.3 AND E_depth<0.3 | raw_firedays_node   |              0 |         0 |             0 |            nan |
| static       | B_depth<0.3 AND E_depth<0.3 | optpft_node         |              0 |         0 |             0 |            nan |
| static       | B_depth<0.3 AND E_depth<0.3 | biome4_full_id_node |              0 |         0 |             0 |            nan |
| dynamic      | B_depth<0.3 AND E_depth<0.3 | firedays_node       |           4382 |      4382 |             0 |              0 |
| dynamic      | B_depth<0.3 AND E_depth<0.3 | raw_firedays_node   |           4382 |      4382 |             0 |              0 |
| dynamic      | B_depth<0.3 AND E_depth<0.3 | optpft_node         |           4382 |      4382 |             0 |              0 |
| dynamic      | B_depth<0.3 AND E_depth<0.3 | biome4_full_id_node |           4382 |      4382 |             0 |              0 |
