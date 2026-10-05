# AGB strict explicit-only filter

Date: 2026-10-05

## Fixed rule

From this point onward, a literature route is allowed into the AGB candidate set only if the source itself explicitly defines or predicts one of the following:

- AGB
- aboveground biomass
- aboveground woody biomass

The following are NOT accepted as AGB without a separately published aboveground partition:

- vegetation carbon
- total biomass carbon
- generic biomass pool
- generic wood pool
- Cveg
- leaf/stem/root carbon pools
- total ecosystem carbon

## 1. Xue et al. (2017), Global Biogeochemical Cycles — PASS

Paper:
Xue et al. (2017), Global patterns of woody residence time and its influence on model simulation of aboveground biomass. DOI 10.1002/2016GB005557.

The source explicitly defines:

tau_w = M_w / W_p

where:
- M_w = mean AGB, Mg ha-1
- W_p = mean aboveground woody productivity including stem and branch, Mg ha-1 yr-1

Therefore:

AGB = tau_w * W_p

is a direct algebraic rearrangement of an explicit AGB equation.

The study compiled 1,319 forest sites restricted to mature/old-growth forests and no major disturbance for at least 100 years.

Meta-analysis tau_w values in Table 2:
- temperate broadleaf (TeB): 82.9 yr
- temperate coniferous (TeC): 74.7 yr
- boreal broadleaf (BoB): 55.5 yr
- boreal coniferous (BoC): 80.9 yr

This route PASSES the strict AGB filter.

Important:
- it predicts woody AGB, not leaf biomass plus wood by assumption
- BIOME4 total NPP cannot be inserted directly; an explicit aboveground woody productivity conversion is required
- PFT7 mapping remains ambiguous between BoB and BoC
- PFT10 has no directly supported category in this table

## 2. Xue et al. (2017) supplementary Figure S8 — supporting flux relation only

The supplementary material gives a direct empirical relation between total NPP and aboveground woody NPP:

P_AGwood,C = 0.0001*NPP^2 + 0.3515*NPP - 14.828

R2 = 0.7538.

This is NOT itself an AGB equation.

It may be connected to the explicit AGB equation above because its dependent variable is explicitly aboveground woody productivity.

When NPP is in g C m-2 yr-1, this produces aboveground woody productivity in g C m-2 yr-1.

To obtain dry-mass AGB from carbon productivity, a separately explicit carbon-to-dry-mass conversion is required.

## 3. Combined Xue explicit-AGB route

Using only definitions that are explicit about aboveground terms:

AGB = tau_w * W_p

and the Figure S8 relation,

AGB_C = tau_w * [0.0001*NPP^2 + 0.3515*NPP - 14.828] / 1000

in kg C m-2.

If a carbon-to-dry-mass factor of 2.0 is explicitly adopted from Xue et al. (2017, Ecological Modelling) / IPCC conversion:

AGB_dry =
0.002 * tau_w *
[0.0001*NPP^2 + 0.3515*NPP - 14.828]

with NPP in g C m-2 yr-1 and AGBdry in kg dry m-2.

This is the first currently retained Yongneup candidate whose final state variable is explicitly AGB in the source definition.

At NPP = 500 g C m-2 yr-1:
- TeB tau=82.9 -> 30.826 kg dry m-2
- TeC tau=74.7 -> 27.777
- BoB tau=55.5 -> 20.637
- BoC tau=80.9 -> 30.082

These are arithmetic illustrations, not Yongneup validation results.

## 4. Malhi et al. (2017), New Phytologist — PASS, structural corroboration

The paper explicitly states for mature forest that aboveground biomass can be expressed from aboveground coarse woody NPP and woody residence time:

AGB = NPP_ACW * tau_W

It therefore passes the strict AGB filter.

However, the dataset is tropical Amazon-Andean forest. It is useful as independent structural corroboration, not as the primary temperate/boreal parameter source for Yongneup.

## 5. Muller-Landau et al. (2021), New Phytologist — PASS, definition/review

The review explicitly defines aboveground woody residence time:

AWRT = AGB / AWP

where AGB is aboveground woody biomass density and AWP is aboveground woody productivity.

This passes the strict AGB filter but is not itself a Yongneup PFT parameterization.

## 6. Explicitly excluded previous routes

The following are excluded from the AGB candidate set unless an independently published aboveground partition is supplied:

- Xue Ecological Modelling Eq. (3) leaf/stem/root carbon-pool equilibrium coefficients 0.0286, 0.0327, 0.0422
- Wang BIOME4 Cveg = NPP*tauveg
- generic IBIS carbon density
- generic wood-pool carbon
- total vegetation carbon
- Ise total living biomass unless a source-explicit aboveground partition is used
- any inferred AGB obtained solely by dropping roots from a generic model carbon pool

## Current status

Strict primary route retained for further Yongneup testing:

Xue 2017 GBC explicit AGB definition
+
Xue supplementary explicit aboveground woody productivity relation

No other candidate is promoted unless the paper itself explicitly defines the target as AGB/aboveground biomass.
