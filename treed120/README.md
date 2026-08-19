# Yongneup TREED–Pelletier 120 ka comparison

This branch runs two otherwise identical 120–0 ka, 1 kyr-coupled simulations on the 298-cell Yongneup grid.

- `dynamic`: TREED re-optimizes H, leaf longevity and leaf carbon at every age/cell within the audited soil-water fixed point.
- `frozen`: each cell's fully coupled 120 ka optimized traits and climate-niche traits are frozen for the remainder of the run.

Both use the same Beyer forcing, Korean monthly lapse correction, McKenzie-profile AWC, external TREED Esupply bucket, R2h EEMT equations, legacy NPP×0.010 AGB bridge, and unchanged Pelletier geomorphology. The comparison therefore isolates temporal trait/niche adaptation without introducing a new geomorphic trait multiplier.
