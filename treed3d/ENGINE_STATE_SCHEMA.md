# Engine state schema (v0)

The first live refactor will expose the existing production state without changing ecological equations.

Per-cell live state fields:
- row, col
- z_m
- soil_depth_m
- NPP_gC_m2_yr
- AET_mm_yr
- EEMT_MJ_m2_yr
- AGB_C_g_m2_component_sum
- Pelletier_AGB_dry_kg_m2
- LAI
- trait_H_m
- a_ll_yr
- C_leaf_gC_individual
- pathology/maladaptation flags when present

The state object also carries model time, scenario, and provenance. 3D rendering consumes this state read-only.
