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


## 5. 식생피복률과 NPP의 구조적/기능적 차이: 직접 인용 근거

### Li et al. (2017)

직접 인용:
> “FVC provides a basic structural index for assessing vegetation condition and NPP is a functional indicator for vegetation production”

사용 가능한 본문:
> 식생피복률은 식생 상태를 나타내는 구조적 지표인 반면, NPP는 식생 생산성을 나타내는 기능적 지표이다(Li et al., 2017).

### Ding et al. (2020)

직접 인용:
> “45.6% of global vegetated area experienced inconsistent trends in vegetation greenness, cover and productivity.”

또한 식생유형별 차이에 대해:
> “vegetation growth was immensely disparate in different vegetation types”

사용 가능한 본문:
> 식생피복과 생산성의 변화는 반드시 일치하지 않으며, 이러한 식생 생장 양상은 식생유형에 따라 다르게 나타날 수 있다(Ding et al., 2020).

주의: “동일한 식생피복률을 갖더라도 식생유형별 생산성이 다르다”는 표현은 위 두 논문에서 그대로 제시한 문장은 아니다. 직접 근거만 사용할 경우 위 두 문장 수준으로 제한한다.

## 6. APA 참고문헌

Ding, Z., Peng, J., Qiu, S., & Zhao, Y. (2020). Nearly half of global vegetated area experienced inconsistent vegetation growth in terms of greenness, cover, and productivity. *Earth's Future, 8*(10), e2020EF001618. https://doi.org/10.1029/2020EF001618

Li, T., Lü, Y., Fu, B., Comber, A. J., Harris, P., & Wu, L. (2017). Gauging policy-driven large-scale vegetation restoration programmes under a changing environment: Their effectiveness and socio-economic relationships. *Science of the Total Environment, 607-608*, 911-919. https://doi.org/10.1016/j.scitotenv.2017.07.044
