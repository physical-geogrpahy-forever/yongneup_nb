# PB4 U008 B vs E fire wetness experiment — final summary

- B and E both completed static 211 + dynamic 211 steps with exit code 0.
- Jang: B static 24/62, dynamic 55/62; E static 24/62, dynamic 55/62.
- PFT validation group summaries are identical between B and E.
- B vs E optPFT/biome changed cell-times: 0.
- E differs only in fire wetness input: B uses wr_n; E uses w(1).
- Native fire thresholds, +0.05 transition interval, and NPP<1000 fuel scaling are unchanged.
- raw_drydays is the pre-fuel-scaling fire-day diagnostic.

## Key fire result
Dynamic <0.3 m cells are exactly consistent between B and E. Deeper cells differ because w(1) is not the normalized full root-zone wetness.

| variant   | model_mode   | depth_bin   |   cell_time_n |   firedays_mean |   firedays_max |   raw_drydays_mean |   raw_drydays_max |
|:----------|:-------------|:------------|--------------:|----------------:|---------------:|-------------------:|------------------:|
| B         | static       | <0.05       |             0 |      nan        |            nan |          nan       |               nan |
| B         | static       | 0.05-0.10   |             0 |      nan        |            nan |          nan       |               nan |
| B         | static       | 0.10-0.30   |             0 |      nan        |            nan |          nan       |               nan |
| B         | static       | 0.30-1.00   |             0 |      nan        |            nan |          nan       |               nan |
| B         | static       | >=1.00      |         62878 |        0        |              0 |            0       |                 0 |
| B         | dynamic      | <0.05       |          1493 |       31.3697   |             49 |          135.242   |               162 |
| B         | dynamic      | 0.05-0.10   |           609 |       46.2562   |             57 |          129.337   |               149 |
| B         | dynamic      | 0.10-0.30   |          2280 |       26.3969   |             58 |           65.3346  |               142 |
| B         | dynamic      | 0.30-1.00   |         13056 |        0.979626 |             31 |            2.05499 |                57 |
| B         | dynamic      | >=1.00      |         44248 |        0        |              0 |            0       |                 0 |
| E         | static       | <0.05       |             0 |      nan        |            nan |          nan       |               nan |
| E         | static       | 0.05-0.10   |             0 |      nan        |            nan |          nan       |               nan |
| E         | static       | 0.10-0.30   |             0 |      nan        |            nan |          nan       |               nan |
| E         | static       | 0.30-1.00   |             0 |      nan        |            nan |          nan       |               nan |
| E         | static       | >=1.00      |         62878 |       10.5333   |             27 |           22.9595  |                45 |
| E         | dynamic      | <0.05       |          1493 |       31.3697   |             49 |          135.242   |               162 |
| E         | dynamic      | 0.05-0.10   |           609 |       46.2562   |             57 |          129.337   |               149 |
| E         | dynamic      | 0.10-0.30   |          2280 |       26.3969   |             58 |           65.3346  |               142 |
| E         | dynamic      | 0.30-1.00   |         13056 |       13.513    |             36 |           28.3024  |                60 |
| E         | dynamic      | >=1.00      |         44248 |       10.2302   |             28 |           22.4216  |                45 |

## Shallow consistency
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
