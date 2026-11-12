# PB4 U008 PFT validation — 2026-11-12

- Model: 6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008
- Period: 21.0–0.0 ka BP, 0.1 kyr, static 211 + dynamic 211
- PFT validation package SHA-256: 7b0b29bc658420feb0b09e246a2141e44d9fee4134c445de7e9ac095b8039256
- Patch SHA-256: 963f5f56d1fac2504031d8cc1b117908a13d03775922ff4aa5e82f92815dcae0
- Clean rerun exit code: 0
- Scientific model change: none; validation diagnostics only

## Primary Jang validation regression
- static: 24/62 = 38.709677%
- dynamic: 55/62 = 88.709677%

## Default PFT validation (72 samples; CON=potential, others=optpft)

Static pooled: accuracy 0.7261904762, sensitivity 0.5510204082, specificity 0.9714285714, TSS 0.5224489796.
Dynamic pooled: accuracy 0.7857142857, sensitivity 0.7448979592, specificity 0.8428571429, TSS 0.5877551020.

Group outcomes (static / dynamic):
- TBD: 28/0/0/0 / 28/0/0/0 (TP/FP/FN/TN)
- BDE: 0/0/19/9 / 19/9/0/0
- CON: 26/2/0/0 / 26/2/0/0
- TBE: 0/0/0/28 / 0/0/0/28
- GRS: 0/0/25/3 / 0/0/25/3
- DWD: 0/0/0/28 / 0/0/0/28

## U008 optpft distribution differences vs PRE-AGB audit
Static PFT4/PFT6 are identical to PRE-AGB. Dynamic total cell-observations changed slightly:
- PFT0: 1231 -> 1225 (-6)
- PFT4: 11099 -> 11071 (-28)
- PFT6: 48107 -> 48154 (+47)
- PFT7: 2241 -> 2226 (-15)
- PFT10: 200 -> 202 (+2); presence timesteps 90 -> 91

The two independent executions in this session produced byte-identical PFT CSVs and summary_timeseries.csv files.
