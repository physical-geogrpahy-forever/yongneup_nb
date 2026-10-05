# Effective AGB residence-time audit for the Xue/IBIS bridge

Date: 2026-10-05

The equilibrium dry-AGB bridge

AGBdry [kg m-2] = c_i * NPP_C [g C m-2 yr-1]

implies an aboveground-carbon stock/productivity ratio

T_i = c_i * 1000 * fC_i

in years.

Using IPCC carbon fractions gives:

| PFT | Xue dry coefficient | fC | implied T (yr) | ForC >=100 yr median T (yr) | Xue / ForC |
|---|---:|---:|---:|---:|---:|
|4 temperate deciduous|0.0286|0.48|13.728|25.234|0.544|
|5 temperate evergreen conifer|0.0222|0.51|11.322|40.458|0.280|
|6 boreal evergreen|0.0327|0.51|16.677|19.664|0.848|
|7 boreal deciduous, BDT carbon fraction|0.0422|0.48|20.256|14.976|1.353|
|7 boreal deciduous, NDT carbon fraction|0.0422|0.51|21.522|14.976|1.437|

## PFT4 local check

Mt. Worak Quercus mongolica:
- aboveground C = 81.94 t C ha-1
- annual NPP C fixation = 6.74 t C ha-1 yr-1
- observed effective ratio = 81.94 / 6.74 = 12.16 yr

This is very close to the Xue-implied 13.73 yr.

The older ForC temperate deciduous median is much higher at 25.23 yr. That discrepancy is consistent with the fact that standing stock/NPP ratio changes strongly with stand age and structure.

## PFT6 check

ForC >=100 yr boreal-evergreen analogue:
- n = 8 plots
- median AGB_C/NPP_C = 19.66 yr

Xue-implied PFT6:
- 16.68 yr

Ratio = 0.85, which is close for a cross-model equilibrium transfer.

The Korean magnitude checks span low-biomass Halla Abies koreana and much larger mature Korean pine stands, so a single stock value is not expected. The stock/NPP comparison is more informative than stock alone.

## PFT5 warning

PFT5 is a poor match to the mature ForC diagnostic: 11.3 vs 40.5 yr. This would be a serious limitation in a domain where PFT5 is common.

However, PFT5 has zero dominant-cell occurrences in the current 21-0 ka Yongneup run. It therefore does not affect this experiment's AGB feedback.

## PFT7 warning

The ForC PFT7 diagnostic has only two plots and mixes deciduous broadleaf and deciduous needleleaf analogues. The combined median is not a strong target for BIOME4 PFT7.

PFT7 also contributes relatively few cells, so it is retained as an uncertainty rather than used to reject the bridge.

## Current interpretation

For the PFTs that actually dominate this Yongneup 21-ka experiment:

- PFT4: local Korean stock/NPP ratio supports Xue.
- PFT6: mature ForC stock/NPP ratio supports Xue reasonably well.
- PFT7: unresolved but low contribution.
- PFT10: unresolved and negligible contribution.
- PFT5: substantial mismatch but absent from the realized dominant-PFT trajectory.

Therefore the Xue/IBIS bridge is currently the strongest equilibrium AGB candidate for this specific domain, while the JULES-LAI bridge remains an independent low-biomass sensitivity case.

This is a domain-specific promotion argument, not evidence that the Xue coefficients are universally valid for all BIOME4 PFTs.
