# Effective AGB residence-time audit for the Xue/IBIS bridge

Date: 2026-10-05

## Correction of the residence-time definition

The Xue/IBIS equilibrium bridge is derived from the carbon-pool equation itself:

[
C_{i,j}=a_{i,j}	au_{i,j}NPP_i
]

Therefore the model-native aboveground carbon stock/productivity ratio is

[
T_i=a_{L,i}	au_{L,i}+a_{W,i}	au_{W,i}
]

and must **not** be reconstructed by multiplying the dry-AGB coefficient by a new IPCC carbon fraction.

Xue et al. separately converts modeled carbon density to dry AGB by a factor of 2.0. The earlier audit mixed these two steps by applying 0.48/0.51 after the Xue dry conversion. That was unnecessary and is corrected here.

## Realized Yongneup forest PFTs

| BIOME4 PFT | Xue/IBIS analogue | model-native AGB_C/NPP_C (yr) | Xue dry coefficient | independent check |
|---|---|---:|---:|---|
|4|temperate broadleaf cold-deciduous|14.30|0.0286|Worak Q. mongolica 12.16 yr|
|6|boreal conifer evergreen|16.35|0.0327|ForC >=100 yr boreal-evergreen median 19.66 yr|
|7|boreal cold-deciduous tree|21.10|0.0422|ForC analogue n too small/heterogeneous for decisive test|
|10|evergreen shrub structural analogue|1.425|0.00285|negligible domain contribution|

PFT5 is excluded from the Yongneup scientific validation because it has 0 dominant-PFT occurrences in the retained canonical 21-0 ka run and no retained historical diagnostic shows it becoming selected dominant optPFT.

## PFT4 local check

Mt. Worak Quercus mongolica:
- aboveground C = 81.94 t C ha-1
- annual NPP C fixation = 6.74 t C ha-1 yr-1
- observed effective ratio = 81.94 / 6.74 = 12.16 yr

Xue/IBIS PFT4 equilibrium factor:
- 14.30 yr

Difference:
- Xue / observed = 1.18
- about 18% higher than the local mature-forest ratio

This is close for a cross-model PFT transfer and directly tests the stock/NPP quantity represented by the equilibrium equation.

## PFT6 check

ForC/Luyssaert >=100 yr boreal-evergreen analogue:
- n = 8 plots
- median AGB_C/NPP_C = 19.66 yr

Xue/IBIS PFT6:
- 16.35 yr

Difference:
- Xue / observed median = 0.83
- about 17% lower than the mature-plot median

Again, this is close relative to the very large stand-age and site variation in forest standing biomass.

## PFT7 and PFT10

PFT7:
- Xue equilibrium factor = 21.10 yr
- dynamic contribution is minor relative to PFT6
- available ForC analogue count and functional-type correspondence are insufficient for a decisive residence-time validation
- retain as uncertainty, not as a reason to reject the whole domain bridge

PFT10:
- Xue evergreen-shrub structural analogue = 1.425 yr
- only 200 cell-observations in the whole dynamic 21-ka run
- cell-weighted mean NPP only 6.08 g C m-2 yr-1
- basin-scale effect is negligible

## Interpretation

For the PFTs that control the Yongneup experiment:
- PFT4 local Korean stock/NPP ratio agrees with Xue within about 18%
- PFT6 mature ForC stock/NPP ratio agrees with Xue within about 17%

This is stronger evidence than matching AGB magnitude alone because it tests the exact slow-process quantity used by the equilibrium allocation-turnover formulation.

The result does not imply universal residence times. It supports the Xue parameter set as a defensible **equilibrium potential-vegetation bridge for this domain**.

See also:
- `XUE_IBIS_SCIENTIFIC_BASIS_KO.md`
- `XUE_IBIS_REALIZED_PFT_SCIENTIFIC_BASIS.csv`
