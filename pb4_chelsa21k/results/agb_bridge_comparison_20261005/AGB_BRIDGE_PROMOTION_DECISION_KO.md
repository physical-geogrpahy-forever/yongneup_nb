# AGB bridge promotion decision — RETRACTED

Date: 2026-10-05

> **최종 정정:** 이 문서의 기존 Xue/IBIS primary-promotion 결론은 철회한다. Xue et al. (2017)의 Eq. (3)에서 \(C_{i,j}\)는 leaf, stem, root biomass pool의 **carbon stock**이며 AGB 자체가 아니다. 같은 논문은 IBIS가 global AGB를 직접 계산하지 않고 carbon density를 계산한다고 명시하고, Table 3에서 model-derived carbon density를 above- and below-ground biomass를 포함한 forest carbon density와 비교한다. 따라서 \(0.0286/0.0327/0.0422\times NPP\)를 해부학적으로 검증된 dry AGB로 승격한 기존 판단은 근거가 부족하다. candidate 실행 결과는 sensitivity 기록으로만 유지한다.

## Current decision

- **Xue/IBIS NPP-turnover bridge: production AGB로 기각/보류.** carbon-pool equilibrium diagnostic으로는 유효하지만 AGB 분리가 입증되지 않았다.
- **JULES-LAI bridge: sensitivity only.** 별도 cross-model allometry이며 production 확정식 아님.
- **canonical legacy 0.010×NPP: historical comparator only.** 출처가 충분하지 않으므로 production 과학식으로 승격하지 않는다.
- **다음 AGB 해결 경로:** aboveground를 정의 자체에 포함하는 자료만 사용한다. 우선 Xue et al. (2017, GBC)의 observed \(\tau_w=AGB/aboveground\ woody\ productivity\) 및 supplementary NPP→aboveground woody NPP 관계를 검토하되, PFT별 residence-time 대응과 leaf 포함 여부를 별도 해결해야 한다.

## PFT5 domain status

The retained Yongneup evidence distinguishes potential PFT5 activity from actual dominance.

- canonical 21-0 ka static: 0/211 timesteps, 0 dominant cell-observations
- canonical 21-0 ka dynamic: 0/211 timesteps, 0 dominant cell-observations
- earlier hotfix diagnostics: relaxed climate constraints sometimes gave PFT5 positive NPP, but PFT6 remained the stronger conifer/taiga competitor
- no retained Yongneup diagnostic currently shows PFT5 becoming selected dominant optPFT

Therefore PFT5 is not used to argue for or against the Xue/IBIS bridge in this domain.

## Evidence hierarchy

### 1. Model lineage and required state

BIOME4 is an equilibrium potential-vegetation model and directly provides PFT, NPP, and optLAI but no standing AGB stock.

Xue/IBIS provides an explicit carbon-pool mass balance:

dC/dt = a*NPP - C/tau

At equilibrium:

C = a*tau*NPP

For aboveground carbon, the leaf and wood pools give:

AGB_C = NPP * (a_leaf*tau_leaf + a_wood*tau_wood)

Xue then converts modeled carbon density to dry AGB by multiplying by 2.0. This is a cross-model PFT-parameter transfer, but the equilibrium stock-from-NPP structure is not foreign to BIOME4: Wang et al. (2011) independently used Cveg=NPP*tau_veg specifically because BIOME4 assumes steady state. Hoogakker et al. later reused that BIOME4 turnover formulation over a glacial cycle, and Wu et al. (2009) provides an independent precedent for coupling BIOME4 output to a process-based carbon-storage model.

JULES provides a published LAI-to-wood allometry:

Cwood = awl * Lbal^(5/3)

This is also a cross-model transfer. It is useful, but a BIOME4 optLAI of about 3.2 produces much less standing wood than observed in several mature Korean forests.

### 2. Full 21-ka execution, not post-hoc arithmetic

All candidates were executed from the same canonical model:

- canonical model: PB4-McKenzie-nativeClimate
- canonical SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- modes: static 211 steps, dynamic 211 steps
- validation: corrected Jang et al. (2011), n=62, 1% basin-presence threshold

Results:

| bridge | dynamic mean AGB kg m-2 | 0 ka mean soil depth m | 0 ka relief m | Jang dynamic |
|---|---:|---:|---:|---:|
|legacy 0.010*NPP|about 4.01|2.496|68.235|55/62|
|JULES-LAI-IPCCCF|about 6.16|2.526|68.02|55/62|
|Xue/IBIS|12.84|2.614|67.445|55/62|

The categorical pollen validation therefore does not discriminate among AGB bridges. AGB selection must be based on biomass provenance and physical magnitude.

### 3. PFT4: Korean local stock/NPP evidence

At 0 ka the model is almost entirely PFT4.

PB4:
- NPP about 611-615 g C m-2 yr-1
- optLAI about 3.2
- JULES-IPCCCF AGB about 88 Mg dry ha-1
- Xue/IBIS AGB about 176 Mg dry ha-1

Korean observations:
- Mt. Worak Quercus mongolica aboveground C = 81.94 t C ha-1, equivalent to about 171 Mg dry ha-1 at fC=0.48.
- Mt. Worak annual NPP C fixation = 6.74 t C ha-1 yr-1 = 674 g C m-2 yr-1.
- observed AGB_C/NPP_C ratio = 12.16 yr.
- Xue/IBIS model-native equilibrium factor = 14.30 yr.
- Xue/observed ratio = 1.18.
- Mt. Gariwang mature Q. mongolica gives still larger AGB.
- observed Korean Q. mongolica peak/maximum LAI values are commonly above the BIOME4 modern optLAI.

Thus PB4 NPP is locally credible while transferred JULES standing biomass is low; Xue is close to the local stock/productivity ratio.

### 4. PFT6: mature evergreen evidence

PFT6 dominates a large fraction of the 21-ka trajectory.

PB4 mean PFT6:
- NPP about 386 g C m-2 yr-1
- JULES-IPCCCF AGB about 59 Mg ha-1
- Xue/IBIS AGB about 126 Mg ha-1

Observations and diagnostics:
- Halla Abies koreana represents a lower-biomass disturbed/subalpine case, about 65-77 Mg dry aboveground ha-1.
- 27-yr Pinus koraiensis plantation: 59.9 Mg ha-1.
- natural mixed Korean pine component: 118 Mg ha-1.
- Taewha class-V Korean pine: 126.53 Mg ha-1.
- older Korean pine stands can exceed 300 Mg ha-1.
- ForC >=100 yr boreal-evergreen analogue plots: median AGB_C/NPP_C = 19.66 yr.
- Xue/IBIS model-native equilibrium factor = 16.35 yr.
- Xue/observed-median ratio = 0.83.

JULES is reasonable for young/low-biomass stands, while Xue is more representative of mature/equilibrium stock.

### 5. PFT7 and PFT10

PFT7:
- small domain contribution
- Korean Larix age-class V implies approximately 150 Mg ha-1 aboveground
- Xue gives about 132 Mg ha-1
- JULES gives about 60-62 Mg ha-1
- BIOME4 PFT7 combines broadleaf and needleleaf deciduous forms, so uncertainty remains.

PFT10:
- extremely small contribution
- shrub above/below woody partition is poorly constrained for JULES
- Xue uses an evergreen-shrub structural analogue
- retain explicit uncertainty; it does not control the basin result.

### 6. Independent current-landscape reference

A current-landscape biomass reference based on Thurner et al. and IPCC conversion gives values close to the JULES sensitivity case.

This does not contradict the Xue choice. It indicates that:
- JULES approximates lower/current landscape biomass reasonably,
- Xue targets an equilibrium/mature potential vegetation stock.

Because the parent vegetation model is BIOME4 equilibrium potential vegetation, the latter interpretation is the one used for the primary candidate.

### 7. Pelletier source range

Pelletier et al. (2013):
- observed AGB in the source sky-island gradient spans from a few to approximately 60-75 kg m-2.
- Xue/IBIS candidate absolute maximum is about 20.7 kg m-2.

Therefore the Xue AGB magnitude remains inside the source AGB range used to motivate the Pelletier vegetation-transport term.

A separate limitation exists for EEMT:
- Pelletier experiments: 5-45 MJ m-2 yr-1
- Yongneup 0 ka: about 93 MJ m-2 yr-1

The major source-domain extrapolation is therefore EEMT, not AGB. This limitation applies to all AGB bridges.

## Promotion status by component

| component | status |
|---|---|
|PFT4 Xue coefficient|supported for this domain|
|PFT6 Xue coefficient|supported for this domain|
|PFT7 Xue coefficient|usable with uncertainty|
|PFT10 Xue coefficient|usable only as negligible-contribution structural analogue|
|PFT5|excluded from Yongneup domain justification: 0 retained dominant-PFT occurrences|
|JULES-LAI-IPCCCF|retain as sensitivity|
|legacy 0.010*NPP|superseded scientifically; retain only as historical reference|
|canonical package replacement|not performed in this decision commit|

## Recommended production rule

If the AGB bridge is promoted to the production package, the only scientific change should be the standing-AGB calculation. NPP, EEMT, BIOME4 competition, climate, soil-depth response, geomorphic equations, and validation mapping must remain unchanged.

Safety rule for a future production promotion:
- PFT0 -> AGB=0
- PFT4/6/7 -> Xue/IBIS coefficients supported above
- PFT10 -> explicitly labelled negligible-contribution evergreen-shrub structural analogue
- PFT5 -> abort and require a new review if it ever becomes a realized dominant PFT
- any other newly realized positive-NPP dominant PFT -> abort rather than silently approximate

The already executed 21-ka candidate included a dormant PFT5 lookup, but PFT5 occurred zero times, so removing that dormant branch would not change any value in the completed trajectory.

## Files supporting this decision

- results/pft_ibis_agb_candidate_20261005/
- results/jules_lai_bdt_agb_candidate_20261005/
- results/jules_lai_ndt_agb_candidate_20261005/
- results/jules_lai_ipcccf_agb_candidate_20261005/
- results/agb_bridge_comparison_20261005/XUE_IBIS_SCIENTIFIC_BASIS_KO.md
- results/agb_bridge_comparison_20261005/XUE_IBIS_REALIZED_PFT_SCIENTIFIC_BASIS.csv
- results/agb_bridge_comparison_20261005/AGB_BRIDGE_KOREA_MAGNITUDE_AUDIT_KO.md
- results/agb_bridge_comparison_20261005/AGB_BRIDGE_EFFECTIVE_RESIDENCE_AUDIT_KO.md
- results/agb_bridge_comparison_20261005/PELLETIER_AGB_RANGE_AUDIT_KO.md
- manuscript/AGB_BRIDGE_FINAL_COMPARISON_20261005.csv
