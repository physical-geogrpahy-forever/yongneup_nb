# LPJ-GUESS 13-PFT explicit AGB coupling audit

Date: 2026-10-05

## 0. Hard acceptance criteria

A production AGB route must satisfy all three conditions simultaneously.

1. The state/output must be explicitly aboveground biomass / aboveground carbon, not generic vegetation carbon.
2. It must respond to NPP and climate. A fixed biome lookup is not acceptable.
3. It must cover all 13 BIOME4 PFTs without silently substituting a nearest class.

## 1. Why LPJ-GUESS is now the primary fallback architecture

Published LPJ-GUESS applications provide direct precedent for climate-responsive aboveground biomass/carbon.

Huntley et al. (2023, Journal of Biogeography, DOI 10.1111/jbi.14619):
- carbon-only LPJ-GUESS
- PFT-specific output described as cmass = above-ground vascular plant biomass
- 20 PFTs
- palaeoclimate, atmospheric CO2 and climate forcing
- 500 yr spin-up plus 90 yr simulation/averaging
- repeated climate states through the late Quaternary

Layritz et al. (2026, JGR Biogeosciences, DOI 10.1029/2025JG009176):
- LPJ-GUESS v4.1.1
- uses above-ground carbon (AGC) explicitly as the vegetation state for recovery and PFT dominance
- validates order of magnitude against NASA ABoVE aboveground biomass/carbon data
- uses Arctic LPJ-GUESS PFTs including tundra functional groups

However, generic LPJ-GUESS cmass cannot be accepted blindly as anatomical AGB. Source-code audit shows generic living C includes root biomass. Therefore this project will add an explicit AGB diagnostic rather than reuse Total cmass.

## 2. Source-code anatomy of the explicit AGB diagnostic

Public LPJ-GUESS source audit shows:

Individual::ccont():
    cmass_leaf + cmass_root + cmass_sap + cmass_heart - cmass_debt

Therefore Total cmass includes belowground root C and is rejected as AGB.

The same source defines:
- cmass_leaf
- cmass_root
- cmass_wood() = cmass_sap + cmass_heart - cmass_debt

GCP output comments explicitly note:
- cWood includes sapwood, heartwood and coarse roots
- cRoot excludes coarse roots

The management implementation defines:
- stem_frac = fraction of wood cmass belonging to stems
- twig_frac = fraction of wood cmass belonging to twigs
- coarse_root_frac = 1 - stem_frac - twig_frac

with default tree values:
- stem_frac = 0.65
- twig_frac = 0.13
- coarse_root_frac = 0.22

Therefore the project can define an anatomically explicit aboveground-carbon diagnostic without generic total C:

For woody PFT i:

C_AGB,i =
C_leaf,i
+
(stem_frac_i + twig_frac_i) C_wood,i

For default tree partition:

C_AGB,i =
C_leaf,i + 0.78 C_wood,i

This explicitly excludes:
- fine-root pool C_root
- coarse-root fraction of C_wood

For nonwoody PFTs with no wood pool:

C_AGB,i = C_leaf,i

This diagnostic is calculated from LPJ-GUESS climate-responsive carbon pools. It is not an empirical NPP x constant bridge.

## 3. Carbon -> dry AGB

LPJ-GUESS pools are kg C m-2. Pelletier requires dry aboveground biomass.

Primary common conversion:

AGB_dry = C_AGB / f_C

Use f_C only after anatomical aboveground C has been isolated.

IPCC supports a default aboveground biomass carbon fraction of 0.47 t C per t dry matter for forest biomass, and 0.47 for herbaceous grassland biomass. A single 0.47 conversion can therefore be used as the conservative common baseline for the 13-PFT experiment, with broadleaf/conifer fractions as sensitivity rather than mixing carbon conversion with the AGB definition.

Thus:

AGB_dry [kg dry m-2] = C_AGB [kg C m-2] / 0.47

This conversion changes units only and does not perform aboveground/belowground partitioning.

## 4. Exact BIOME4 v4.2b2 PFT list

Direct original source jedokaplan/BIOME4 biome4.f:

1 Tropical Evergreen Trees
2 Tropical Drought-deciduous Trees
3 Temperate Broadleaved Evergreen Trees
4 Temperate Deciduous / Summergreen Trees
5 Cool / Temperate Evergreen Conifer Trees
6 Boreal Evergreen Trees
7 Boreal Deciduous Trees
8 temperate grass, C3 in exact v4.2b2 growth code
9 tropical/warm-temperate grass, C4
10 woody desert plant, C4 in exact v4.2b2 growth code
11 tundra shrub
12 cold herbaceous
13 lichen/forb

Important exact source check:
growth() sets C4 only when PFT == 9 or PFT == 10.
Therefore PFT8 is C3 and PFT10 is explicitly a C4 woody desert PFT.

## 5. 13-PFT LPJ-GUESS mapping audit

Status meanings:
- DIRECT = published LPJ/LPJ-GUESS PFT already provides this functional group
- ARCTIC-DIRECT = published Arctic LPJ-GUESS configuration provides the group
- CUSTOM-REQUIRED = no exact published default PFT found, must be explicitly parameterized

| BIOME4 PFT | BIOME4 definition | LPJ-GUESS target | status | explicit AGB diagnostic |
|---:|---|---|---|---|
|1|Tropical evergreen tree|TrBE, with TrIBE only if strategy ensemble is desired|DIRECT|leaf + aboveground wood|
|2|Tropical drought-deciduous / raingreen tree|TrBR|DIRECT|leaf + aboveground wood|
|3|Temperate broadleaf evergreen tree|TeBE|DIRECT|leaf + aboveground wood|
|4|Temperate summergreen broadleaf tree|TeBS; TeIBS optional strategy ensemble|DIRECT|leaf + aboveground wood|
|5|Temperate evergreen conifer|TeNE|DIRECT|leaf + aboveground wood|
|6|Boreal evergreen tree|BNE; BINE optional strategy ensemble|DIRECT|leaf + aboveground wood|
|7|Boreal deciduous tree, bst|BIBS boreal broadleaf summergreen|DIRECT|leaf + aboveground wood|
|8|Temperate C3 grass|C3G|DIRECT|leaf/shoot C|
|9|Tropical/warm C4 grass|C4G|DIRECT|leaf/shoot C|
|10|C4 woody desert plant|new C4 evergreen/semi-evergreen dryland shrub PFT|CUSTOM-REQUIRED|leaf + aboveground woody C|
|11|Tundra shrub|Arctic shrub PFT set HSE/HSS/LSE/LSS/EPDS/SPDS or a locked aggregate TUS|ARCTIC-DIRECT|leaf + aboveground woody C|
|12|Cold herbaceous|GRT, graminoid and forb tundra|ARCTIC-DIRECT|leaf/shoot C|
|13|Lichen/forb|CLM, cushion forb, lichen and moss tundra|ARCTIC-DIRECT|aboveground shoot/leaf C|

Direct coverage is therefore 12/13 functional types.

The only non-default blocker is PFT10.

## 6. PFT7 resolved

Do not map BIOME4 PFT7 to Larix/BNS automatically.

The BIOME4 source label is bst = Boreal Deciduous Trees. Independent Arctic/LPJ taxonomies distinguish:
- BIBS = boreal broad-leaved summergreen
- BNS = boreal needle-leaved summergreen

The BIOME4 bst lineage corresponds to the broadleaf cold-deciduous / Populus-type strategy, so the production mapping is:

BIOME4 PFT7 -> LPJ BIBS

This removes the earlier Xue PFT7 ambiguity.

## 7. PFT11-13 resolved from published Arctic LPJ-GUESS

The public Arctic instruction set contains:
- HSE high shrub evergreen
- HSS high shrub summergreen
- LSE low shrub evergreen
- LSS low shrub summergreen
- EPDS prostrate dwarf shrub evergreen
- SPDS prostrate dwarf shrub summergreen
- GRT graminoid and forb tundra
- CLM cushion forb, lichen and moss tundra
- C3G

Layritz et al. aggregate these as tundra PFTs in their analysis.

Therefore BIOME4:
- PFT11 -> tundra shrub set
- PFT12 -> GRT
- PFT13 -> CLM

does not require inventing a generic nonvascular proxy.

## 8. PFT10 scientific construction

No exact published LPJ-GUESS default C4 woody shrub PFT has been identified after targeted search.

Published dryland LPJ-GUESS configurations provide:
- C4 grass
- tropical evergreen trees
- tropical raingreen trees
- semi-deciduous shrubs such as Guiera senegalensis

but the shrub component is not an explicit C4 woody shrub.

Therefore pretending that an existing shrub PFT is BIOME4 PFT10 is prohibited.

### 8.1 Biological template

Atriplex canescens is a strong biological analogue because published work explicitly describes it as:
- C4
- perennial woody shrub
- evergreen to semi-evergreen depending on climate
- strongly drought-adapted
- distributed in arid and semi-arid environments

There are also direct Atriplex canescens biomass/allometric observations and drought-response biomass partitioning measurements.

### 8.2 Model construction rule

Create a new LPJ-GUESS PFT, working name:

C4DS = C4 Dryland Shrub

Mandatory properties:
- lifeform = woody shrub
- pathway = C4
- phenology = evergreen/semi-evergreen consistent with BIOME4 PFT10
- climate envelope anchored to BIOME4 PFT10 rather than silently borrowing a C3 shrub climate niche
- dryland shrub morphology/allometry from published LPJ-GUESS dryland shrub parameterization where pathway-independent
- C4 photosynthetic pathway parameters from LPJ-GUESS C4 vegetation
- Atriplex observations used to check SLA, biomass allocation and rooting-depth plausibility
- no parameter may be labelled 'published PFT10 parameter' unless it actually is one

This is a transparent custom cross-model PFT, not a claimed native LPJ-GUESS type.

## 9. Climate/NPP responsiveness

Do not calculate AGB from a static PFT coefficient.

Each climate state must be simulated with LPJ-GUESS so that:
climate + CO2 -> photosynthesis/GPP -> respiration -> NPP -> allocation -> tissue pools -> AGB

Therefore condition 2 is structurally satisfied.

Because the target BIOME4 model represents equilibrium potential vegetation, preferred coupling is independent equilibrium simulation for each 0.1-kyr climate slice rather than a 21-kyr age-history transient.

Published palaeoclimate LPJ-GUESS precedent used a long spin-up and terminal averaging. Initial proposed Yongneup protocol:
- forcing: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- 211 climate states
- one constrained PFT experiment per BIOME4 PFT / climate state as required
- spin-up length to be convergence-tested, starting from 500 yr precedent
- final averaging window starting from 90 yr precedent
- atmospheric CO2 matched to time slice if the PB4 climate stack supplies/reconstructs it
- no fire/land use if target is potential equilibrium vegetation unless a sensitivity experiment is explicitly requested

## 10. Why TREED is useful but not a replacement yet

TREED v1.0 (Rogger et al. 2026) is useful for resolving the anatomical AGB bookkeeping problem:
- stem biomass is explicitly heartwood + sapwood
- coarse root C is a separate pool
- coarse root C = 0.25(stem C)
- allometric constants were calibrated against observed aboveground biomass density
- NPP is process-calculated from climate/CO2-driven photosynthesis and respiration

This confirms that separating structural aboveground stem from coarse roots is a defensible LPJ-family architecture.

But TREED does not currently provide a one-to-one published 13 BIOME4 PFT parameter table. Therefore it is supporting architecture/reference, not the present 13-PFT production model.

## 11. Current decision

There is now a concrete route satisfying the three hard conditions in model architecture:

1. EXPLICIT AGB:
   implement and output a named AGB/AGC diagnostic that excludes fine and coarse roots explicitly.

2. NPP/CLIMATE RESPONSIVE:
   AGB is generated by LPJ-GUESS carbon allocation under each climate/CO2 state, not by a fixed lookup.

3. ALL 13 PFTS:
   12/13 have direct published global or Arctic LPJ-GUESS functional counterparts.
   PFT10 requires one explicitly documented custom C4 dryland shrub PFT.

Therefore the remaining work is no longer 'find an AGB equation'. It is:
A. finalize PFT10 C4DS parameters;
B. implement the explicit AGB diagnostic;
C. build the 13-PFT instruction file;
D. test one current-climate slice;
E. only then run 211 time slices.

## 12. Fail-closed rules

Production run must stop if:
- any of the 13 PFT definitions is absent
- generic Total cmass is substituted for AGB
- root C is included in AGB
- PFT10 is silently mapped to a C3 shrub
- an unsupported nearest-class mapping is introduced
- an AGB value is constant merely because the biome/PFT class is unchanged

## 13. Next concrete build target

Create a dedicated LPJ-GUESS branch/config for Yongneup with:
- exact 13 BIOME4-labelled PFTs
- explicit AGC and AGB_dry output fields
- output audit fields: NPP, leaf C, wood C, stem fraction, twig fraction, excluded coarse-root C, fine-root C, AGC, AGB_dry
- one-row provenance per PFT

Do not modify canonical PB4 until this test passes all 13 rows.
