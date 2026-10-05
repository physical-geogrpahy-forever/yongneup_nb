# AGB bridge final decision

Date: 2026-10-05  
Status: **FINAL**

## Final selection

The production AGB treatment for the Yongneup PB4 model is fixed to the BIOME4-derived aboveground living biomass proxy \(AGB^*\):

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
LAI_p
\left[
S_p
+
0.03630780547701014\,L_{m,p}^{0.43}
\right]
}
\]

where \(LAI_p\) is BIOME4 optimal LAI, \(L_{m,p}\) is BIOME4 v4.2b2 pftpar(pft,7) in months, and

\[
S_p=
\begin{cases}
1, & pftpar(p,10)=1\\
0, & pftpar(p,10)=2
\end{cases}
\]

is a project-defined indicator for whether the BIOME4 source code includes the sapwood-respiration term for that PFT.

The leaf term is derived from Reich et al. (1992):

\[
\log_{10}(SLA)
=
2.44
-
0.43\log_{10}(\mathrm{life\mbox{-}span})
\]

with \(SLA\) in \(\mathrm{cm^2\,g^{-1}}\) and life-span in months, giving

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
0.03630780547701014\,LAI_p L_{m,p}^{0.43}
}
\]

in \(\mathrm{kg\ dry\ biomass\ m^{-2}}\).

The sapwood relation follows Haxeltine and Prentice (1996), BIOME3 Eq. (34):

\[
C_s=LAI\,C_n
\]

combined with BIOME4 v4.2b2 source code stemcarbon=0.5 kg C per unit LAI. With the explicit project conversion assumption \(f_C=0.50\),

\[
\boxed{
B_{\mathrm{sapwood,dry},p}=S_p\,LAI_p
}
\]

and therefore the final equation above follows directly.

## Pelletier coupling

The Pelletier et al. (2013) geomorphic coupling structure is retained:

\[
\boxed{
k_d=cEEMT+dAGB^*
}
\]

with

\[
c=0.033,\qquad d=0.05.
\]

Pelletier Eq. (5),

\[
AGB=e\exp(fEEMT),
\]

is not used for Yongneup because the Yongneup EEMT range substantially exceeds the source experiment range and direct exponential extrapolation produces physically unusable AGB values.

## Rejected or sensitivity-only alternatives

Legacy \(AGB=0.010NPP\) is retained only as a historical comparator. Xue/IBIS and JULES-derived bridges remain sensitivity experiments and are not the production AGB method. The direct Pelletier EEMT-to-AGB exponential relation is rejected for Yongneup.

## Full 21-0 ka test

The selected AGB* bridge was implemented from the same PB4-McKenzie-nativeClimate baseline and the full 21.0-0.0 ka trajectory was newly rerun at 0.1 kyr intervals.

Results:

| metric | static | dynamic |
|---|---:|---:|
| steps | 211 | 211 |
| time-mean basin AGB* kg m-2 | 3.19979 | 3.11600 |
| 0 ka basin AGB* kg m-2 | 3.48349 | 3.46620 |
| 0 ka basin AGB* t ha-1 | 34.8349 | 34.6620 |
| Jang correct / 62 | 24 | 55 |
| Jang accuracy | 38.71% | 88.71% |

The Jang et al. (2011) corrected reduced-class validation is unchanged from the nativeClimate baseline.

## Interpretation

\(AGB^*\) is not total anatomical aboveground biomass. It is the BIOME4-derived living aboveground proxy that can be defended from explicit published equations and BIOME4 source parameters, comprising foliage and sapwood only.

Manuscript wording at first use:

> BIOME4-derived aboveground living biomass proxy (AGB*), comprising foliage and sapwood.

## Authoritative method document

pb4_chelsa21k/manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md

## References

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365-392. https://doi.org/10.2307/2937116

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

BIOME4 v4.2b2 source code, Jed O. Kaplan: https://github.com/jedokaplan/BIOME4
