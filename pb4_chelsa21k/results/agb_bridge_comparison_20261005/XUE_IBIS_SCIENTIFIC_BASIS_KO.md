# Xue/IBIS AGB bridge scientific basis for Yongneup

Date: 2026-10-05

## 1. Domain scope: PFT5 is not part of the realized Yongneup problem

The canonical PB4-McKenzie-nativeClimate 21-0 ka PFT coverage audit was a fresh full run with:
- canonical SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
- climate: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 21.0-0.0 ka BP
- 0.1 kyr interval
- static 211 + dynamic 211
- no scientific model change; only PFT-count diagnostics added

Dynamic dominant-PFT occurrences:
- PFT4: 47/211 timesteps, 11,099 cell-observations
- PFT5: **0/211 timesteps, 0 cell-observations**
- PFT6: 186/211 timesteps, 48,107 cell-observations
- PFT7: 201/211 timesteps, 2,241 cell-observations
- PFT10: 90/211 timesteps, 200 cell-observations

Static PFT5 is also 0/211 and 0 cell-observations.

Earlier hotfix diagnostics contain cases where relaxed climate constraints allowed PFT5 to obtain positive NPP, but the strongest conifer/taiga competitor was PFT6 and no retained diagnostic shows PFT5 becoming the selected dominant optPFT.

Therefore PFT5 is removed from the scientific justification of the Yongneup AGB bridge. Its coefficient is not needed to reproduce the current experiment. A future production implementation should fail closed if PFT5 newly appears rather than claiming that its coefficient has been validated for this domain.

## 2. Why an NPP-turnover bridge is compatible with BIOME4 itself

BIOME4 is an equilibrium potential-natural-vegetation model. It directly predicts PFT-specific optimal NPP and LAI but not a prognostic standing AGB pool.

Wang, Ni & Prentice (2011) already solved the analogous BIOME4 carbon-storage problem by using the steady-state relation

[
C_{veg}=NPP,	au_{veg}
]

They state explicitly that this is consistent with BIOME4's steady-state assumption and that vegetation carbon turnover depends primarily on vegetation type.

This is important because it means the conceptual bridge

[
BIOME4 NPP ightarrow turnover ightarrow standing vegetation carbon
]

is already present in published BIOME4 methodology. The Xue/IBIS bridge does not invent the stock-from-productivity concept. It refines it from a mega-biome turnover time into PFT-specific aboveground leaf and wood pools.

Hoogakker et al. subsequently reused the Wang method for BIOME4 glacial-cycle carbon storage, again assuming BIOME4-modelled NPP is in balance with vegetation carbon through vegetation-type turnover times.

Wu et al. (2009) independently coupled BIOME4 to the process-based DEMETER carbon model and successfully used corresponding BIOME4 outputs to estimate terrestrial carbon storage. This provides a second precedent for attaching a carbon-allocation/storage module to BIOME4 rather than forcing BIOME4 itself to contain carbon pools it does not prognose.

## 3. The Xue/IBIS process equation

Xue et al. (2016 preprint; final article 2017) describe IBIS annual NPP allocation among leaves, stems for trees, and roots. For PFT (i), biomass pool (j):

[
rac{partial C_{i,j}}{partial t}
=
a_{i,j}NPP_i
-
rac{C_{i,j}}{	au_{i,j}}
]

where:
- (a_{i,j}) is the fraction of annual NPP allocated to the pool
- (	au_{i,j}) is its carbon residence time

For an equilibrium vegetation model, set

[
rac{partial C_{i,j}}{partial t}=0
]

giving

[
C_{i,j}=a_{i,j}	au_{i,j}NPP_i
]

For aboveground carbon, use leaf + wood:

[
oxed{
AGB_{C,i}
=
NPP_i
(a_{L,i}	au_{L,i}+a_{W,i}	au_{W,i})
}
]

Xue converts modeled carbon density to dry AGB by multiplying by 2.0. With BIOME4 NPP in g C m^-2 yr^-1:

[
oxed{
AGB_{dry,i}
=
rac{2}{1000}
NPP_i
(a_{L,i}	au_{L,i}+a_{W,i}	au_{W,i})
}
]

This is not an empirical regression fitted to the Yongneup pollen result. It is the analytic steady-state solution of a published carbon-pool mass balance.

## 4. Exact realized-PFT mapping

BIOME4 v4.2b2 source defines:
- PFT4 = Temperate Deciduous Trees / Temperate Summergreen
- PFT6 = Boreal Evergreen Trees
- PFT7 = Boreal Deciduous Trees
- PFT10 = C3/C4 woody desert plant type

Xue Table 1 defines:
- IBIS PFT5 = temperate broadleaf cold-deciduous tree
- IBIS PFT6 = boreal conifer evergreen tree
- IBIS PFT7 = boreal broadleaf cold-deciduous tree
- IBIS PFT8 = boreal conifer cold-deciduous tree
- IBIS PFT9 = evergreen shrub

The mappings used here are based on growth form, climatic group and phenology:
- BIOME4 PFT4 -> IBIS PFT5
- BIOME4 PFT6 -> IBIS PFT6
- BIOME4 PFT7 -> IBIS PFT7 or 8
- BIOME4 PFT10 -> IBIS PFT9 structural analogue

PFT7's broadleaf-vs-deciduous-conifer ambiguity does not affect the AGB coefficient because Xue's PFT7 and PFT8 have the same AGB-relevant allocation and residence parameters.

## 5. Exact coefficients for the realized forest PFTs

### PFT4

Xue/IBIS PFT5:
- (a_L=0.30)
- (	au_L=1) yr
- (a_W=0.40)
- (	au_W=35) yr

[
a_L	au_L+a_W	au_W
=0.30(1)+0.40(35)=14.30
]

[
oxed{AGB_{dry}=0.0286,NPP}
]

### PFT6

Xue/IBIS PFT6:
- (a_L=0.30)
- (	au_L=2.5) yr
- (a_W=0.30)
- (	au_W=52) yr

[
0.30(2.5)+0.30(52)=16.35
]

[
oxed{AGB_{dry}=0.0327,NPP}
]

### PFT7

Xue/IBIS PFT7 and PFT8:
- (a_L=0.30)
- (	au_L=1) yr
- (a_W=0.40)
- (	au_W=52) yr

[
0.30(1)+0.40(52)=21.10
]

[
oxed{AGB_{dry}=0.0422,NPP}
]

### PFT10

Evergreen-shrub structural analogue:
- (a_L=0.45)
- (	au_L=1.5) yr
- (a_W=0.15)
- (	au_W=5) yr

[
0.45(1.5)+0.15(5)=1.425
]

[
AGB_{dry}=0.00285,NPP
]

PFT10 is not treated as a fully validated correspondence. It contributes only 200 dynamic cell-observations across the entire 21-ka run, with cell-weighted mean NPP 6.08 g C m^-2 yr^-1, so it is retained as an explicitly labelled negligible-contribution structural analogue.

## 6. Xue is an AGB-tested model, not only a theoretical pool equation

The Xue study did not merely report IBIS parameters. It evaluated potential AGB using a global plot dataset.

The 2016 methodological paper states that 2,101 plot-level AGB observations were collected and used to constrain the model. The final 2017 Ecological Modelling article reports that IBIS reproduced global total AGB on a comparable scale to other estimates, while also identifying important spatial biases caused largely by using one parameter set for a PFT across the globe.

This gives the bridge a useful but bounded validation status:
- strong enough to use as a physically based potential-AGB candidate
- not strong enough to call the PFT coefficients universal constants

## 7. Domain-specific stock/NPP check

A cleaner validation of the equilibrium bridge is to compare carbon stock divided by carbon NPP, because that is the quantity the equilibrium equation actually predicts.

### PFT4

Xue model-native equilibrium factor:

[
AGB_C/NPP_C=14.30 {m yr}
]

Mt. Worak Quercus mongolica:
- aboveground carbon = 81.94 t C ha^-1
- NPP carbon fixation = 6.74 t C ha^-1 yr^-1

[
81.94/6.74=12.16 {m yr}
]

Xue/observation ratio:

[
14.30/12.16=1.18
]

Thus the model-native turnover factor is about 18% above this Korean mature-forest observation, which is close for a cross-model PFT transfer.

### PFT6

Xue model-native equilibrium factor:

[
AGB_C/NPP_C=16.35 {m yr}
]

ForC/Luyssaert >=100-yr boreal-evergreen analogue plots:
- n=8
- median (AGB_C/NPP_C=19.66) yr

[
16.35/19.66=0.83
]

Thus Xue is about 17% below the mature-plot median.

These comparisons are more directly relevant to the Xue formulation than comparing AGB alone, because they isolate the stock accumulation timescale from site productivity.

## 8. Why the JULES-LAI candidate is kept as sensitivity instead

The JULES/TRIFFID allometric route is published and useful, but when BIOME4 optLAI is inserted into it:
- PFT4 is around 81-88 Mg dry ha^-1
- PFT6 is around 59 Mg dry ha^-1

Those magnitudes agree with some present-day, young, disturbed, or low-biomass forests and with the independent current-landscape biomass reference.

However, standing woody biomass can keep accumulating after canopy LAI approaches saturation. BIOME4 is not an age-explicit current-stand model; it represents equilibrium potential vegetation. The NPP-turnover formulation therefore matches the intended vegetation state more directly.

Ma et al. (2024) strengthens this interpretation from the opposite direction: steady-state IBIS can overestimate young forests precisely because young stands have not yet accumulated equilibrium woody stock. That is a limitation for current-age biomass but is not a conceptual flaw when the target itself is equilibrium potential vegetation.

## 9. Known uncertainty: wood residence time

The major scientific uncertainty is not the algebra but (	au_W).

Xue notes that invariant PFT parameters create regional AGB bias. Ma et al. further shows that wood allocation and wood residence parameters are among the parameters to which biomass is especially sensitive, and that forest age matters strongly in transient stands.

Therefore:
- do not call 35 or 52 yr a universal biological constant
- do not interpret the resulting AGB as actual historical stand age
- interpret it as the equilibrium/potential standing AGB associated with BIOME4's simulated PFT and NPP
- preserve lower-biomass sensitivity cases

## 10. Pelletier coupling consistency

The full Xue/IBIS candidate has:
- dynamic mean AGB about 12.84 kg m^-2
- absolute maximum about 20.72 kg m^-2

Pelletier et al. (2013) source observations extend to roughly 60-75 kg m^-2 AGB at high elevation, so the Xue candidate does not exceed the source AGB magnitude.

The larger source-domain extrapolation in Yongneup is EEMT, not AGB.

## 11. Final scientific status

For this specific Yongneup BIOME4-Pelletier experiment:

[
oxed{
BIOME4 NPP + realized dominant PFT
ightarrow
IBIS allocation/residence mass balance
ightarrow
equilibrium AGB_C
ightarrow
Xue dry AGB
}
]

is the strongest current primary bridge because it has four independent layers of support:

1. **mass-balance basis**: allocation minus turnover equation
2. **model-state compatibility**: equilibrium solution for an equilibrium BIOME4 target
3. **BIOME4 methodological precedent**: published BIOME4 studies already use NPP x turnover to recover steady-state vegetation carbon
4. **independent magnitude check**: realized PFT4 and PFT6 stock/NPP ratios are close to Korean/ForC mature-forest observations

PFT5 is not used as supporting evidence because it has no retained dominant-PFT occurrence in Yongneup.

This remains a domain-specific equilibrium-AGB bridge, not a universal conversion for every BIOME4 application.

## References

- Foley, J. A. et al. (1996). An integrated biosphere model of land surface processes, terrestrial carbon balance, and vegetation dynamics. Global Biogeochemical Cycles, 10, 603-628. DOI 10.1029/96GB02692.
- Kucharik, C. J. et al. (2000). Testing the performance of a dynamic global ecosystem model: Water balance, carbon balance, and vegetation structure. Global Biogeochemical Cycles, 14, 795-825. DOI 10.1029/1999GB001138.
- Xue, B.-L. et al. (2017). Evaluation of modeled global vegetation carbon dynamics: Analysis based on global carbon flux and above-ground biomass data. Ecological Modelling, 355, 84-96. DOI 10.1016/j.ecolmodel.2017.04.012.
- Wang, H., Ni, J., & Prentice, I. C. (2011). Sensitivity of potential natural vegetation in China to projected changes in temperature, precipitation and atmospheric CO2. Regional Environmental Change, 11, 715-727. DOI 10.1007/s10113-011-0204-2.
- Wu, H., Guiot, J., Peng, C., & Guo, Z. (2009). New coupled model used inversely for reconstructing past terrestrial carbon storage from pollen data: validation of model using modern data. Global Change Biology, 15, 82-96. DOI 10.1111/j.1365-2486.2008.01712.x.
- Ma, R. et al. (2024). Stepwise Calibration of Age-Dependent Biomass in the Integrated Biosphere Simulator (IBIS) Model. Journal of Advances in Modeling Earth Systems, 16. DOI 10.1029/2023MS004048.
