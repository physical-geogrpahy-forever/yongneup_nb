# AGB resolution: explicit aboveground biomass via BIOME4 biome classes

Date: 2026-10-05

## Decision

Stop searching for a PFT-carbon-pool conversion.

Use the final BIOME4 biome output directly, because a published BIOME4 application already maps all BIOME4 biomes to broad ecosystem types, and Saugier-derived tables provide explicit oven-dry aboveground vegetation mass for those ecosystem types.

This route avoids:
- generic carbon pools
- inferred leaf+wood = AGB
- missing PFT7 mappings
- coarse-root ambiguity

## Published lineage

Ragon et al. (2024), Scientific Reports:
- uses BIOME4
- maps the 28 BIOME4 biomes to ecosystem types and biomass density
- Table S3 / preprint Table C1 gives the exact BIOME4-biome -> ecosystem-type mapping
- biomass source is Houghton et al. (2009), with Saugier et al. (2001) chosen where several values exist

Saugier-derived explicit aboveground dry biomass:
- tropical forest: 30.4 kg dry m-2
- temperate forest: 21.0
- boreal forest: 6.1
- Mediterranean shrubland: 6.0
- tropical savanna/grassland: 4.0
- temperate grassland: 0.25
- desert: 0.35
- tundra: 0.25

These are explicit oven-dry aboveground vegetation masses, not total vegetation carbon.

## Yongneup realized BIOME4 biome coverage

Canonical 21-0 ka audit:

Dynamic:
- biome 4: 2,072 cell-observations
- biome 7: 45,810
- biome 8: 13,107
- biome 9: 167
- biome 10: 289
- biome 11: 2
- biome 21: 200
- biome 27: 37

Static:
- biome 7: 48,574
- biome 8: 14,006
- biome 10: 298

Therefore a biome-level mapping covers every realized output, including the states containing BIOME4 PFT7.

## Explicit AGB mapping for realized Yongneup biomes

Following Ragon's biome grouping:

| BIOME4 biome | name | ecosystem class | explicit dry AGB kg m-2 |
|---:|---|---|---:|
|4|Temperate deciduous broadleaf forest|temperate forest|21.0|
|7|Cool mixed forest|temperate + boreal forest|12.53*|
|8|Cool evergreen needleleaf forest|boreal forest|6.1|
|9|Cool-temperate evergreen needleleaf and mixed forest|temperate + boreal forest|12.53*|
|10|Cold evergreen needleleaf forest|boreal forest|6.1|
|11|Cold deciduous forest|boreal forest|6.1|
|21|Desert|desert|0.35|
|27|Barren|desert in Ragon mapping|0.35; 0.0 sensitivity|

*For Ragon's combined temperate+boreal class, the explicit aboveground mass is area-weighted from Saugier:
(10.4*21.0 + 13.7*6.1)/(10.4+13.7) = 12.53 kg dry m-2.
This weighting reproduces the same broad combined ecosystem logic used by Ragon/Houghton but uses explicit aboveground mass rather than total biomass.

## Diagnostic magnitude only, not a new PB4 run

Applying the mapping only to the existing biome-frequency audit gives:
- dynamic cell-observation-weighted mean AGB ≈ 11.37 kg dry m-2
- static cell-observation-weighted mean AGB ≈ 11.07 kg dry m-2

These are audit-weighted diagnostics, not spatial/time-step PB4 outputs and not yet geomorphic reruns.

## Why this solves the PFT7 problem

PFT7 no longer needs an external PFT analogue.

The model already converts PFT competition into a final BIOME4 biome. For example, BIOME4 biome 11 is explicitly Cold deciduous forest and is mapped by the published BIOME4 biomass workflow to boreal forest. AGB is then taken from an explicit aboveground biomass table.

Thus there is no:
PFT7 -> IBIS PFT7/8
or
PFT7 -> BoB/BoC
guess.

The bridge is:
BIOME4 final biome -> published BIOME4 biome ecosystem class -> explicit aboveground dry biomass.

## Limitation

The main limitation is that AGB is stepwise by biome rather than continuously varying with NPP within a biome.

Therefore:
1. use this fixed explicit-AGB lookup as the primary defensible baseline;
2. only after that, test an NPP-scaled within-biome sensitivity using paired explicit AGB and NPP references;
3. do not let the sensitivity replace the fixed published mapping unless independently validated.

## Next executable step

Patch a copy of PB4-McKenzie-nativeClimate so the Pelletier AGB term is driven by BIOME4 final biome ID and the table above, with:
- no PFT-carbon-pool bridge
- no Xue/IBIS coefficients
- barren = 0.35 primary following Ragon, 0.0 sensitivity
- all other model settings unchanged

Then run full 21-0 ka static + dynamic and report:
- AGB distribution by biome and time
- 0 ka geomorphology
- difference from canonical legacy
- Jang n=62 only as vegetation validation, not AGB validation
- explicit provenance for every AGB number
