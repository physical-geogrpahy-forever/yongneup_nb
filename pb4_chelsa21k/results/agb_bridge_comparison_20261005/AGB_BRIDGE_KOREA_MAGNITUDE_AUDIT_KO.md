# BIOME4 AGB bridge: Korean magnitude audit and current decision

Date: 2026-10-05

## Scope

This audit compares the two fully executed 21-0 ka AGB bridges against Korean forest observations and the already-reconstructed ForC/Luyssaert diagnostics.

Models:
1. JULES/TRIFFID optLAI allometry with IPCC carbon fractions
2. Xue/IBIS equilibrium NPP allocation-turnover bridge

Canonical PB4 production package is not overwritten.

## Executed model results

### JULES-LAI-IPCCCF

Formula:

AGBdry = LMA(PFT) * optLAI + 0.75 * awl(PFT) * optLAI^(5/3) / fCwood(PFT)

Carbon fractions:
- broadleaf/BDT: 0.48
- conifer/NET/NDT: 0.51
- PFT10 shrub fallback: 0.47

Full run result:
- dynamic time-mean AGB: 6.16 kg dry m-2
- PFT4 cell-weighted AGB: 8.08 kg m-2
- PFT6 cell-weighted AGB: 5.90 kg m-2
- PFT7 cell-weighted AGB: about 6.0-6.2 kg m-2
- dynamic Jang 1%: 55/62 = 88.71%

### Xue/IBIS equilibrium

Formula:

AGBdry = coefficient(PFT) * NPP

Important coefficients:
- PFT4 0.0286
- PFT6 0.0327
- PFT7 0.0422

Full run result:
- dynamic time-mean AGB: 12.84 kg dry m-2
- PFT4 cell-weighted AGB: about 15.3 kg m-2
- PFT6 cell-weighted AGB: about 12.6 kg m-2
- PFT7 cell-weighted AGB: about 13.2 kg m-2
- dynamic Jang 1%: 55/62 = 88.71%

Therefore the Jang categorical validation does not discriminate the AGB bridges.

## Area-definition audit

BIOME4 v4.2b2 source was re-checked.

- findnpp searches the LAI that maximizes NPP.
- growth computes maxfvc = 1 - exp(-k*maxlai).
- fPAR is calculated directly from maxlai.
- monthly LAI is recovered from monthly fPAR.
- output(2) is the selected ecosystem/dominant-PFT LAI.
- no extra crown-cover multiplication is applied to optLAI before photosynthesis.

The BIOME3 model description also describes its state as total ecosystem LAI and NPP.

JULES defines LAI per vegetated surface tile and stores PFT fractional cover separately. In PB4 each 20-m cell is assigned a dominant PFT, so applying the PFT allometry to that cell without an additional FVC multiplier is internally consistent. Multiplying JULES AGB by BIOME4 FVC again would likely double-count coverage.

## Korean PFT4 check

PB4 modern PFT4:
- BIOME4 NPP about 612-615 g C m-2 yr-1
- BIOME4 optLAI about 3.2
- JULES-IPCCCF AGB about 87.8 Mg ha-1 at 0 ka
- IBIS equilibrium AGB about 175.9 Mg ha-1

Korean observations:
- Mt. Worak Quercus mongolica: aboveground C = 81.94 t C ha-1; using fC=0.48 gives about 170.7 Mg dry ha-1.
- Mt. Gariwang Quercus mongolica: mean aboveground C = 103.52 t C ha-1; the study used fC=0.47, corresponding to about 220.3 Mg dry ha-1.
- Mt. Gariwang direct litterfall LAI was about 4.06 +/- 0.42; Mt. Nam Quercus mongolica peak LAI reports are about 4.6-5.8.
- Mt. Worak NPP C fixation was about 6.74 t C ha-1 yr-1 = 674 g C m-2 yr-1, close to PB4 modern NPP.

Interpretation:
PB4 NPP magnitude is locally plausible, while PB4 optLAI is low relative to several Korean mature Quercus forests. This explains why the JULES transfer can underpredict standing wood even when the allometric equation itself is valid.

## Korean and mature-forest PFT6 check

PB4 PFT6:
- mean NPP about 386 g C m-2 yr-1
- JULES-IPCCCF AGB about 59 Mg ha-1
- IBIS equilibrium AGB about 126 Mg ha-1

Observations and diagnostics:
- Halla Abies koreana: aboveground C 33.2-39.46 t C ha-1, equivalent to about 65-77 Mg dry ha-1 at fC=0.51.
- 27-yr Pinus koraiensis plantation: 59.9 Mg ha-1 aboveground dry biomass.
- natural mixed Korean pine component: 118 Mg ha-1.
- Taewha class-V Pinus koraiensis: 126.53 Mg ha-1.
- 71-80 yr Korean pine plantation: 317.9 Mg ha-1.
- ForC/Luyssaert >=100 yr boreal-evergreen analogue plots: median AGB_C/NPP_C ratio = 19.664 yr. With fC=0.51 and PB4 PFT6 NPP=386.1, diagnostic AGB is about 149 Mg ha-1.

Interpretation:
PFT6 observations span a very wide age/disturbance range. JULES is plausible for young or low-biomass subalpine stands, but is low for mature/equilibrium forest inventory. IBIS is closer to the natural/mature central tendency and to the ForC old-plot diagnostic.

## PFT7 check

Central Korean Larix kaempferi age-class V:
- total tree biomass = 193.4 Mg ha-1
- root fraction = 22.4%
- implied aboveground biomass about 150 Mg ha-1

PB4 candidates:
- JULES PFT7 about 60-62 Mg ha-1
- IBIS PFT7 about 132 Mg ha-1

PFT7 has a small domain contribution, so this does not control the full result, but again mature-stand magnitude favors the NPP-turnover candidate.

## Why the two bridges diverge

The difference is not carbon fraction.

The core difference is structural:
- JULES transfer makes standing wood a deterministic function of optLAI.
- IBIS transfer makes standing wood depend on NPP allocation and a long woody residence time.

Observed forest AGB can increase several-fold with stand age while LAI changes much less after canopy closure. Therefore a transferred LAI-only relation can represent canopy-supported allometry but does not necessarily reproduce long-term woody stock when the input LAI comes from another equilibrium model.

Wolf et al. (2011) also showed that biomass-pool allometry in several land-surface models, including TRIFFID and IBIS, deviates from inventory allometry, especially in young/low-biomass stands. Neither bridge should be described as independently validated simply because it comes from a published DGVM.

## Current decision

Do not promote JULES-LAI-IPCCCF to production.

Current evidence favors keeping:
- **IBIS/Xue NPP-turnover bridge as the leading equilibrium/potential-vegetation candidate**
- **JULES-LAI-IPCCCF as an independent lower-biomass sensitivity candidate**

Reason:
1. BIOME4 is an equilibrium potential-vegetation model, not an age-explicit young-stand model.
2. PB4 NPP is close to measured Korean forest NPP for PFT4.
3. Mature Korean PFT4, PFT6 and PFT7 biomass and the ForC >=100 yr diagnostic generally sit much closer to IBIS than to the transferred BIOME4-LAI/JULES estimate.
4. JULES remains informative for low-biomass or disturbed stands, including Halla Abies koreana and young Korean pine.
5. PFT10 remains unresolved but has negligible contribution in this 21-ka domain.

This is still a candidate ranking, not a final production promotion. The next decisive check should quantify whether Xue/IBIS residence-time coefficients are consistent with mature observational stock/NPP ratios for each required PFT without using stand age as a model input.

## Primary references

- Haxeltine & Prentice (1996), BIOME3, Global Biogeochemical Cycles 10:693-709.
- Kaplan et al. (2003), BIOME4 application, JGR Atmospheres 108(D19).
- Wolf et al. (2011), Forest biomass allometry in global land surface models, Global Biogeochemical Cycles 25, GB2009. DOI 10.1029/2010GB003917.
- Harper et al. (2016), JULES-vn4.3 parameterization, GMD 9:2415-2440.
- Harper et al. (2018), JULES-C2, GMD 11:2857-2873.
- Xue et al. (2017), Evaluation of modeled global vegetation carbon dynamics, Ecological Modelling 355:84-96.
- Son et al. (2001), Allometry and biomass of Korean pine in central Korea, Bioresource Technology 78:251-255. DOI 10.1016/S0960-8524(01)00012-8.
- Halla Abies koreana KNLTER annual biomass/carbon study, 2009-2013.
- Jo et al. (2026), Disentangling variation patterns and partitioning strategies of NPP, Ecological Processes 15:11.
