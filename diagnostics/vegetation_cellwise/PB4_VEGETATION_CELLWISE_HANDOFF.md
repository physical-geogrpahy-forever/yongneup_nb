# PB4 U008 vegetation cellwise diagnostics handoff

## Scope
Final model: `PB4Studio v6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`.

This directory preserves cellwise diagnostics used to explain static-vs-dynamic vegetation differences in the Yongneup VeSLEM results. Continue from these files rather than re-deriving values from figures.

## Current writing rule
Separate **results** from **interpretation**. Do not infer values by eye from plots. Read the CSVs directly.

## Broadleaf vs mixed-forest transition around 4 ka
At 4.3 ka, static = 298/298 mixed forest. Dynamic = 8 broadleaf + 290 mixed forest.

For the 8 dynamic broadleaf cells at 4.3 ka:
- mean dynamic soil depth = 0.162 m
- mean dynamic WHC = 37.11 mm
- mean dynamic wetness = 70.81
- mean dynamic firedays = 93.25 d
- corresponding static cells have soil depth 1.94 m, WHC 298.55 mm, wetness 78.7, firedays 0 d
- 4 cells change native BIOME4 from Cool mixed forest to Temperate deciduous forest
- 4 cells retain native Cool mixed forest but cross the reduced-class 51% broadleaf-vs-conifer competition threshold
- detailed per-cell values and PFT competition values are stored below

Mismatch counts in 4.3-3.9 ka:
- 4.3 ka: 8 cells
- 4.2 ka: 6 cells
- 4.1 ka: 6 cells
- 4.0 ka: 0 cells
- 3.9 ka: 8 cells

The 298-cell 4.3 ka PFT diagnostic table is split into three CSVs only for GitHub transfer size. Each part repeats the same header. To reconstruct the original table, keep the header of part 1 and append data rows from parts 2 and 3.

## Early conifer-related differences
The early mismatch CSV contains mismatches at:
- 19.8 ka: 4 cells total = 1 herb/open + 3 bare in dynamic, all conifer in static
- 18.4 ka: 19 cells total = 1 herb/open + 18 bare in dynamic, all conifer in static
- 18.3 ka: 19 cells total = 19 bare in dynamic, all conifer in static

At 17.2 ka, direct process diagnostics were additionally generated:
- dynamic groups: 271 conifer, 1 herb/open, 26 bare
- conifer cells: mean soil depth 1.8194 m, mean WHC 260.764 mm, mean wetness 76.906, mean firedays 1.646 d, mean NPP 275.705
- herb/open cell: soil depth 0.00930 m, WHC 2.203 mm, wetness 56.7, firedays 34 d, NPP 6
- bare cells: essentially zero soil depth; 26 cells, many in valley/channel positions
- corresponding static cells use soil depth 1.94 m and are conifer forest

## 17.2 ka conifer mechanism analysis: completed 2026-10-07
Read first:
- `PB4_17p2_CONIFER_MECHANISM_COMPLETION_20261007_KO.md`
- `PB4_17p2_PFT_DEPTH_THRESHOLD_SUMMARY.csv`

Key completed findings:
- bare cells: 23/26 valley, versus 53/271 among conifer cells
- bare-cell median contributing area = 5,311.6 m2 versus 816.4 m2 in conifer cells
- bare-cell median A/w = 14,486.2 versus 43.77 in conifer cells
- all 26 bare cells show positive fluvial bedrock erosion, while only one retains positive regolith erosion
- current hillslope dz is positive in 23/26 bare cells, so the present bare state must not be attributed to current hillslope stripping
- 19.8 ka mismatch 4 cells and 18.4-18.3 ka mismatch 19 cells all persist inside the 17.2 ka bare set
- tracked herb/open cells become bare after their residual soil reaches zero
- direct 17.2 ka BIOME4-SD soil-depth sweep locates the conifer/open transition near H=0.01401 m and the native barren/open transition near H=0.000201 m under that fixed climate/soil setting
- the actual 17.2 ka herb/open cell has H=0.009295 m, WHC=2.203 mm, optPFT=10 and NPP=6
- at that cell PFT6 NPP falls from 276.006 to 56.717 and PFT7 from 260.564 to 92.366 relative to the 1.94 m reference
- BIOME4 source logic explains the transition: PFT7 below 120 moves to the open branch, after which low grass LAI with PFT10 present selects optPFT10

The remaining task is manuscript integration, not additional mechanism discovery unless a reviewer requires another sensitivity test.

## Files
- `PB4_EARLY_CONIFER_MISMATCH_CELL_DIAGNOSTICS.csv`
- `PB4_EARLY_CONIFER_MISMATCH_GROUP_SUMMARY.csv`
- `PB4_17p2_CONIFER_MISMATCH_CELL_PROCESS_DIAGNOSTICS.csv`
- `PB4_17p2_CONIFER_PROCESS_GROUP_DIAGNOSTICS.csv`
- `PB4_17p2_CONIFER_MECHANISM_COMPLETION_20261007_KO.md`
- `PB4_17p2_PFT_DEPTH_THRESHOLD_SUMMARY.csv`
- `PB4_4p3ka_broadleaf_cells_static_dynamic_full_diagnostics.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part1.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part2.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics_part3.csv`
- `PB4_4p3_3p9_mismatch_only.csv`
