# 서론 및 이론적 배경 문헌 감사: 식생모델 시간규모와 LPJ-GUESS 계산비용

작성일: 2026-10-06  
대상: VeSLEM 논문의 식생모델 발전 및 전지구 동적 식생모델 설명 부분  
원칙: 본문 내주는 출판연도 기준으로 통일하고, 참고문헌은 APA 형식으로 기록한다.

## 1. 현재 권장 문장

> 이러한 전지구 동적 식생모델은 짧게는 수십 년부터 길게는 수십만 년까지의 시간적 스케일에 적용되어 왔다(Allen et al., 2020; Foley et al., 1996). 전지구 동적 식생모델은 탄소와 물 순환뿐만 아니라 식생의 경쟁 및 사망을 함께 고려할 수 있다는 점에서 의의가 있으나(Garreta et al., 2010), LPJ-GUESS와 같이 연령 기반 cohort와 복제 패치(replicate patches)를 이용하는 모델은 높은 계산량을 요구하며, 이러한 계산비용은 광범위하거나 고해상도의 모의에서 제약이 될 수 있다(Scherstjanoi et al., 2013).

## 2. 근거 확인

### Allen et al. (2020)

- LPJ-GUESS를 이용하여 140 ka부터 현재까지 전지구 biome 패턴을 모의하였다.
- 따라서 DGVM이 수십만 년 규모의 고식생 연구에 적용된 사례로 사용한다.
- 본문 내주: `Allen et al. (2020)`.

### Foley et al. (1996)

- IBIS는 land-surface biophysics, terrestrial carbon fluxes, global vegetation dynamics를 하나의 체계에서 결합한다.
- 시간규모가 짧은 생물물리 과정부터 장기 생태계 동역학까지 함께 모의할 수 있음을 제시한다.
- 본문 내주: `Foley et al. (1996)`.

### Garreta et al. (2010)

- LPJ-GUESS를 사용하면 climate change와 vegetation change 사이의 지연을 growth, mortality, competition을 통해 고려할 수 있다고 명시한다.
- 논문은 2009년에 온라인 출판되었지만 정식 권호의 출판연도는 2010이므로 APA 내주는 `Garreta et al. (2010)`으로 쓴다.
- `Garreta et al. (2009)`로 쓰지 않는다.

### Scherstjanoi et al. (2013)

- LPJ-GUESS를 second-generation DGVM의 사례로 직접 설명한다.
- LPJ-GUESS의 높은 계산비용의 원인으로 5-50개의 age-based cohorts와 많은 replicate patches의 동시 모의를 제시한다.
- 이 요구는 first-generation DGVM보다 계산 요구량을 2-3 orders of magnitude 증가시킨다고 보고한다.
- 계산비용 때문에 고해상도 전지구 LPJ-GUESS 모의는 슈퍼컴퓨터 없이는 현실적으로 어렵다고 명시한다.
- 주의: 이 논문은 BIOME4와 LPJ-GUESS의 계산시간을 직접 비교한 연구가 아니다.

## 3. APA 참고문헌

Allen, J. R. M., Forrest, M., Hickler, T., Singarayer, J. S., Valdes, P. J., & Huntley, B. (2020). Global vegetation patterns of the past 140,000 years. *Journal of Biogeography, 47*(10), 2073-2090. https://doi.org/10.1111/jbi.13930

Foley, J. A., Prentice, I. C., Ramankutty, N., Levis, S., Pollard, D., Sitch, S., & Haxeltine, A. (1996). An integrated biosphere model of land surface processes, terrestrial carbon balance, and vegetation dynamics. *Global Biogeochemical Cycles, 10*(4), 603-628. https://doi.org/10.1029/96GB02692

Garreta, V., Miller, P. A., Guiot, J., Hély, C., Brewer, S., Sykes, M. T., & Litt, T. (2010). A method for climate and vegetation reconstruction through the inversion of a dynamic vegetation model. *Climate Dynamics, 35*, 371-389. https://doi.org/10.1007/s00382-009-0629-1

Scherstjanoi, M., Kaplan, J. O., Thürig, E., & Lischke, H. (2013). GAPPARD: A computationally efficient method of approximating gap-scale disturbance in vegetation models. *Geoscientific Model Development, 6*, 1517-1542. https://doi.org/10.5194/gmd-6-1517-2013

## 4. 서술상 주의

- `Scherstjanoi et al. (2013)`의 2-3 orders of magnitude 비교 대상은 BIOME4가 아니라 first-generation DGVM이다.
- 따라서 본문에서 `LPJ-GUESS는 BIOME4보다 계산량이 2-3 orders of magnitude 크다`라고 쓰지 않는다.
- 계산비용에 관한 문장은 LPJ-GUESS 자체의 cohort 및 replicate-patch 구조와 광범위, 고해상도 적용의 제약으로 한정한다.

## 5. 식생피복률과 NPP의 기능적 차이

### 권장 서술

> 기존의 식생피복률은 주로 식생의 공간적 피복 정도를 나타내는 구조적 지표인 반면, NPP는 식생의 생산성과 생물학적 에너지 투입을 나타내는 기능적 지표라는 장점이 있다(Pelletier et al., 2013). 특히 NPP를 식생 유형을 명시적으로 모의하는 식생모델과 연계할 경우, 동일한 식생피복률을 갖더라도 식생 유형에 따라 서로 다른 생산성을 지형 과정에 반영할 수 있다(Istanbulluoglu & Bras, 2005; Pelletier et al., 2013; Quijano-Baron et al., 2022; Schmid et al., 2018).

### 근거 범위

- Pelletier et al. (2013): EEMT에서 생물학적 에너지 항을 NPP로 정의하며, NPP를 biomass production과 연결한다. 또한 AGB, NPP, LAI, below-ground biomass가 서로 다른 식생 지표가 될 수 있음을 논의한다. 따라서 NPP를 생산성 및 생물학적 에너지 투입의 기능적 지표로 서술하는 핵심 근거이다.
- Istanbulluoglu and Bras (2005): vegetation cover를 균일한 지표피복 변수로 사용하면서, 뿌리 보강 효과가 식물 종, functional type 및 root depth에 따라 달라질 수 있음을 명시한다. 따라서 동일한 피복 변수만으로 식생 기능 차이를 모두 표현하기 어렵다는 근거로 사용할 수 있다.
- Quijano-Baron et al. (2022): leaves, roots, litter 및 soil carbon이 서로 다른 기작으로 erosion을 조절한다고 명시한다. 단일 vegetation-cover 변수보다 식생 생체량과 구성요소를 세분화할 필요성을 뒷받침한다.
- Schmid et al. (2018): vegetation cover를 이용해 hillslope diffusion, Manning roughness 및 fluvial erosion 관련 계수를 조절하며, vegetation cover와 roughness의 직접 대응이 단순화라고 명시한다. 식생피복률 기반 결합의 한계를 설명하는 근거로 사용한다.
- 주의: 위 문헌들이 “동일한 식생피복률에서 서로 다른 PFT의 NPP가 다르다”라는 문장을 그대로 제시하는 것은 아니다. 이 부분은 식생피복률 기반 접근의 단순화와 NPP/biomass의 기능적 의미를 종합한 본 연구의 해석이다. 보다 보수적으로 쓰려면 “동일한 피복률에서도 식생 유형별 생산성 차이를 반영할 수 있다”보다 “식생 유형별 생산성 차이를 추가로 반영할 수 있다”가 안전하다.

## 6. 추가 APA 참고문헌

Istanbulluoglu, E., & Bras, R. L. (2005). Vegetation-modulated landscape evolution: Effects of vegetation on landscape processes, drainage density, and topography. *Journal of Geophysical Research: Earth Surface, 110*(F2), F02012. https://doi.org/10.1029/2004JF000249

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

Quijano-Baron, J., Saco, P. M., & Rodríguez, J. F. (2022). Modelling the effects of above and belowground biomass pools on erosion dynamics. *Catena, 213*, 106123. https://doi.org/10.1016/j.catena.2022.106123

Schmid, M., Ehlers, T. A., Werner, C., Hickler, T., & Fuentes-Espoz, J.-P. (2018). Effect of changing vegetation and precipitation on denudation – Part 2: Predicted landscape response to transient climate and vegetation cover over millennial to million-year timescales. *Earth Surface Dynamics, 6*, 859-881. https://doi.org/10.5194/esurf-6-859-2018
