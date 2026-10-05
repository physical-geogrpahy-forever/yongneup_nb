# BIOME4-derived AGB* final method

작성일: 2026-10-05  
상태: **최종 채택**  
2026-10-06 표기 갱신: 논문 Methods에서는 문헌 원식과 BIOME4 source parameter를 직접 사용하며, 계산 편의를 위한 파생 indicator와 전개 소수계수는 본문 수식에서 제외한다.

## 1. 최종 변수 정의

본 연구에서 Pelletier 식생-지형 결합식의 AGB 항에는 BIOME4 산출과 BIOME 계보의 출판식으로 계산한 **BIOME4-derived aboveground living biomass proxy**를 사용한다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

여기서 \(AGB^*\)는 잎과 살아 있는 변재(sapwood)를 포함한다. BIOME4가 독립적인 standing stock으로 제공하지 않는 심재(heartwood), 굵은 가지 등의 장기 목질부는 포함하지 않는다. 따라서 본문에서 최초 정의 시 total anatomical AGB와 구분하여 \(AGB^*\)로 표기한다.

## 2. BIOME4 입력

BIOME4의 모델 계보와 PFT 기반 최적 LAI/NPP 계산은 Kaplan et al. (2003)을 따른다. 실제 계산 파라미터는 공개 BIOME4 v4.2b2 source code의 biome4.f를 기준으로 한다.

본 AGB* 계산에 사용하는 BIOME4 변수는 다음과 같다.

- \(LAI_p\): dominant PFT의 BIOME4 optimal LAI
- \(L_{m,p}\): expected leaf longevity in months, BIOME4 v4.2b2 pftpar(pft,7)
- pftpar(pft,10): presence of sapwood respiration
- stemcarbon = 0.5: BIOME4 v4.2b2 respiration subroutine의 sapwood carbon parameter

표준 BIOME4 v4.2b2는 13개의 PFT parameter slot을 가지며 PFT1은 표준 실행에서 비활성화된다. 본 식은 13개 slot 모두에 대해 파라미터를 정의하되 실제 용늪 21-0 ka 실행에서 선택된 dominant PFT만 사용한다.

## 3. 잎 건조생체량

Reich et al. (1992), Table 1의 전체 LEAVES 자료에 제시된 회귀식을 원식 그대로 사용한다.

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

여기서 \(L_{m,p}\)의 단위는 month이고 \(SLA_p\)의 단위는 \(\mathrm{cm^2\,g^{-1}}\)이다. Reich et al. (1992)은 SLA를 leaf area / leaf dry mass로 정의한다.

LAI는 leaf area / ground area이므로 standing leaf dry biomass는

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 계산한다. 실제 구현에서는 SLA 단위를 \(\mathrm{m^2\,kg^{-1}}\)로 변환하여 동일 계산을 수행한다.

논문 Methods에서는 원식과 위 관계를 제시하며, 이를 전개해서 얻는 소수계수는 독립적인 경험계수처럼 제시하지 않는다.

## 4. 변재 건조생체량

Haxeltine and Prentice (1996), BIOME3 Eq. (34)의 원식은

\[
\boxed{
C_s
=
LAI\,C_n
}
\]

이다. 여기서 \(C_s\)는 total sapwood carbon content이고 \(C_n\)은 sapwood carbon content per unit LAI이다.

BIOME4 v4.2b2 source code의 respiration subroutine은 \`stemcarbon=0.5\`를 사용하며, source comment는 이를 sapwood mass in kg C per unit leaf area per unit ground area로 정의한다. 따라서 본 연구에서는 BIOME4 source parameter를

\[
C_n=0.5
\]

로 적용한다.

dry biomass 변환은

\[
\boxed{
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
}
\]

로 수행하며, \(f_C=0.50\)은 본 연구의 명시적 carbon-fraction 가정이다.

BIOME4 v4.2b2에서 \`pftpar(pft,10)=2\`인 PFT는 source code가 sapwood respiration을 제거하므로 해당 PFT의 AGB* 계산에서도 sapwood 항을 0으로 둔다. 이 처리는 BIOME4 source flag를 그대로 따른 것이며, 논문 Methods에서는 별도의 새로운 생태계수로 정의하지 않는다.

## 5. 최종 AGB* 식

위 두 항을 결합하면 최종 AGB*는 원 구성식을 유지하여 다음과 같이 쓴다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

여기서 잎 항은 Reich et al. (1992)의 원 회귀식과

\[
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
\]

로 계산하며, 변재 항은 Haxeltine and Prentice (1996) Eq. (34)와 BIOME4 v4.2b2의 sapwood 구현을 따른다.

단위는

\[
\boxed{
\mathrm{kg\ dry\ biomass\ m^{-2}}
}
\]

이다.

본 연구에서 이후의 AGB 표기는 특별한 설명이 없는 한 이 \(AGB^*\)를 뜻하며, 최초 Methods 정의에서는 반드시 BIOME4-derived aboveground living biomass proxy (AGB*)라고 명시한다.

## 6. BIOME4 v4.2b2 PFT별 source parameter

논문에는 파생된 \(AGB^*/LAI\) 소수계수를 제시하지 않고, 실제 계산에 들어가는 BIOME4 source parameter만 제시한다.

| PFT | BIOME4 source-code type | \(L_m\) month | pftpar(10) | sapwood 항 |
|---:|---|---:|---:|---|
| 1 | Tropical Evergreen Trees | 18 | 1 | 사용 |
| 2 | Tropical Drought-deciduous Trees | 9 | 1 | 사용 |
| 3 | Temperate Broadleaved Evergreen Trees | 18 | 1 | 사용 |
| 4 | Temperate Deciduous Trees | 7 | 1 | 사용 |
| 5 | Cool Conifer Trees | 30 | 1 | 사용 |
| 6 | Boreal Evergreen Trees | 24 | 1 | 사용 |
| 7 | Boreal Deciduous Trees | 24 | 1 | 사용 |
| 8 | C3/C4 temperate grass | 8 | 2 | 미사용 |
| 9 | C4 tropical grass | 10 | 2 | 미사용 |
| 10 | C3/C4 woody desert | 12 | 1 | 사용 |
| 11 | Tundra shrub | 8 | 1 | 사용 |
| 12 | Cold herbaceous | 8 | 2 | 미사용 |
| 13 | Lichen/forb | 8 | 1 | 사용 |

PFT13은 식생형 명칭상 sapwood 해석에 주의가 필요하지만, 본 연구에서는 BIOME4 v4.2b2 source code의 \`pftpar(13,10)=1\`을 임의 수정하지 않고 그대로 따른다.

## 7. Pelletier 지형식과의 결합

Pelletier et al. (2013)의 colluvial transport coupling 구조는 유지한다.

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

사용 계수는 Pelletier et al. (2013)의

\[
c=0.033,\qquad d=0.05
\]

를 유지한다.

반면 Pelletier et al. (2013)의 대상지 경험식

\[
AGB=e\exp(fEEMT)
\]

은 용늪에 사용하지 않는다. 원 연구의 EEMT 실험 범위보다 용늪 EEMT가 훨씬 높아 지수 외삽이 폭주하기 때문이다. 따라서 **Pelletier의 지형수송 결합식은 유지하고 AGB 상태변수만 BIOME4-derived \(AGB^*\)로 대체**한다.

## 8. 21-0 ka 전체 재실행 결과

실행 조건:

- model: PB4-McKenzie-nativeClimate
- baseline canonical SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- AGB* candidate SHA-256: 1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- static: 211 steps
- dynamic: 211 steps
- 새로 실행한 결과이며 과거 참고값이 아님

21 ka 전체 basin-mean AGB*의 시계열 평균:

\[
\mathrm{static}=3.19979\ \mathrm{kg\,m^{-2}}
\]

\[
\mathrm{dynamic}=3.11600\ \mathrm{kg\,m^{-2}}
\]

0 ka:

\[
\mathrm{static}=3.48349\ \mathrm{kg\,m^{-2}}
\]

\[
\mathrm{dynamic}=3.46620\ \mathrm{kg\,m^{-2}}
\]

즉 0 ka dynamic은 약 \(34.66\ \mathrm{t\,ha^{-1}}\)이다.

기존 0.010 x NPP bridge와 비교하면 21 ka 평균은 약 22% 감소하고, 0 ka에서는 약 43% 감소한다.

Jang et al. (2011) corrected reduced mapping, basin 1% presence criterion:

\[
\mathrm{static}=24/62=38.71\%
\]

\[
\mathrm{dynamic}=55/62=88.71\%
\]

로 기존 nativeClimate production baseline과 동일하다.

## 9. 최종 채택 판정

본 연구의 AGB 처리 방식은 다음으로 고정한다.

\[
\boxed{
BIOME4\ optLAI
+
BIOME4\ PFT\ leaf\ longevity
+
Reich\ SLA\mbox{-}life\mbox{-}span
+
BIOME4\ sapwood
\rightarrow
AGB^*
}
\]

다음 방식은 production AGB 산정식으로 사용하지 않는다.

- legacy AGB = 0.010 x NPP: 출처 없는 historical comparator
- Pelletier Eq. (5) AGB = e exp(f EEMT): 용늪 EEMT에서 지수 외삽 폭주
- Xue/IBIS bridge: PFT 대응과 aboveground 해석 불확실성
- JULES bridge: 별도 모델의 allometry를 BIOME4에 전이하는 cross-model sensitivity

## 10. 참고문헌

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365-392. https://doi.org/10.2307/2937116

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

BIOME4 v4.2b2 source code. Jed O. Kaplan. https://github.com/jedokaplan/BIOME4

## 11. 구현 및 결과 파일

- runner: pb4_chelsa21k/tools/run_reich_lai_sapwood_agb_candidate.py
- candidate package: pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip
- results: pb4_chelsa21k/results/reich_lai_sapwood_agb_candidate_20261005/
- comparison: pb4_chelsa21k/results/agb_bridge_comparison_20261005/AGB_BRIDGE_COMPARISON.csv
