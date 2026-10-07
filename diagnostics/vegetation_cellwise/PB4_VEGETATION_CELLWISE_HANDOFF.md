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
- the detailed per-cell values and PFT competition values are in the 4.3 ka diagnostic CSVs

Mismatch counts in 4.3-3.9 ka:
- 4.3 ka: 8 cells
- 4.2 ka: 6 cells
- 4.1 ka: 6 cells
- 4.0 ka: 0 cells
- 3.9 ka: 8 cells

## Early conifer-related differences
The early mismatch CSV currently contains mismatches at:
- 19.8 ka: 4 cells total = 1 herb/open + 3 bare in dynamic, all conifer in static
- 18.4 ka: 19 cells total = 1 herb/open + 18 bare in dynamic, all conifer in static
- 18.3 ka: 19 cells total = 19 bare in dynamic, all conifer in static

At 17.2 ka, direct process diagnostics were additionally generated for all 298 cells:
- dynamic groups: 271 conifer, 1 herb/open, 26 bare
- conifer cells: mean soil depth 1.8194 m, mean WHC 260.764 mm, mean wetness 76.906, mean firedays 1.646 d, mean NPP 275.705
- herb/open cell: soil depth 0.00930 m, WHC 2.203 mm, wetness 56.7, firedays 34 d, NPP 6
- bare cells: essentially zero soil depth; 26 cells, many in valley/channel positions
- corresponding static cells use soil depth 1.94 m and are conifer forest

The next analysis task is to quantify, cell by cell and by process group, exactly how geomorphic soil stripping/channel incision lowers soil depth and WHC, changes wetness/firedays/PFT NPP, and produces the conifer -> herb/open or conifer -> bare differences. Distinguish:
1. true vegetation competition shifts with residual soil,
2. near-zero-soil/bare-bedrock outcomes caused by geomorphic stripping,
3. any role of valley/channel position, fluvial erosion, hillslope transport, and elevation difference.

Do not compress these into a generic “soil moisture effect”; identify the mechanism and magnitude from the CSVs.

## Files
- `PB4_EARLY_CONIFER_MISMATCH_CELL_DIAGNOSTICS.csv`
- `PB4_EARLY_CONIFER_MISMATCH_GROUP_SUMMARY.csv`
- `PB4_17p2_CONIFER_MISMATCH_CELL_PROCESS_DIAGNOSTICS.csv`
- `PB4_17p2_CONIFER_PROCESS_GROUP_DIAGNOSTICS.csv`
- `PB4_4p3ka_broadleaf_cells_static_dynamic_full_diagnostics.csv`
- `PB4_4p3ka_all_cells_PFT_diagnostics.csv`
- `PB4_4p3_3p9_mismatch_only.csv`
