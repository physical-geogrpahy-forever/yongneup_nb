# PB4 U008 McKenzie root-zone wetness normalization A/B/C/D

Source package SHA-256: `7b0b29bc658420feb0b09e246a2141e44d9fee4134c445de7e9ac095b8039256`

Normalization: `wr_n = wr/max(rtop_eff+rbot_eff,1.0e-6)`.

A is the current U008 path and is the default. A generated Fortran is byte-identical to the original U008 generated Fortran.

All A/B/C/D static and dynamic 21–0 ka runs finished with exit code 0.

## Jang overall

| variant   | model_mode   |   correct_n |   n |   accuracy_pct |
|:----------|:-------------|------------:|----:|---------------:|
| A         | static       |          24 |  62 |        38.7097 |
| A         | dynamic      |          55 |  62 |        88.7097 |
| B         | static       |          24 |  62 |        38.7097 |
| B         | dynamic      |          55 |  62 |        88.7097 |
| C         | static       |          24 |  62 |        38.7097 |
| C         | dynamic      |          55 |  62 |        88.7097 |
| D         | static       |          24 |  62 |        38.7097 |
| D         | dynamic      |          24 |  62 |        38.7097 |

## Files

- 01_JANG_OVERALL.csv
- 02_JANG_BY_RECORD.csv
- 03_PFT_VALIDATION_GROUP_SUMMARY.csv
- 04_SELECTED_8CELLS_211STEP_TIMESERIES.csv
- 05_FIREDAYS_DEPTHBIN_PER_OUTPUT_TIME.csv
- 06_FIREDAYS_DEPTHBIN_AGGREGATE.csv
- 07_DEEP_GE1P5_EQUALITY_BY_VARIABLE.csv
- 08_DEEP_GE1P5_EQUALITY_SUMMARY.csv
- 09_DEEP_GE1P5_DIFFERENCE_LOCATIONS.csv (only if differences exist)
- A_to_B.diff, B_to_C.diff, C_to_D.diff
- A/B/C/D_generated_fortran.f
- RUN_PROVENANCE.json