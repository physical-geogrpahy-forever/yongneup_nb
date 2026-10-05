# BIOME4-only AGB/vegetation-carbon 문헌 감사

작성일: 2026-10-05

## 목적

용늪 PB4-McKenzie-nativeClimate에서 Pelletier 지형식의 식생량 항을 처리하기 위해,
BIOME3, LPJ, Xue, Malhi, 외부 AGB 회귀식을 결합하지 않고 **BIOME4 자체 및 BIOME4를 직접 사용한 문헌만으로**
AGB 또는 이에 가장 가까운 식생량 상태변수를 해결할 수 있는지 검토했다.

## 1. BIOME4 원 모델에서 직접 계산되는 것

BIOME4 v4.2b2의 핵심 직접 산출은 PFT별 최적 NPP와 최적 LAI, 그리고 최종 biome이다.
Kaplan et al. (2003)은 BIOME4가 PFT별 최대 sustainable LAI와 associated NPP를 계산하고,
NPP, LAI, 토양수분 등의 biogeochemical variables를 이용해 biome을 결정한다고 설명한다.

**BIOME4 원 코어에는 total standing AGB를 직접 출력하는 독립 pool이 없다.**

따라서 `BIOME4 -> total AGB`를 원 모델 내부식이라고 부를 수 없다.

## 2. Wang et al. (2011): BIOME4에서 vegetation carbon을 만드는 직접 선행례

Wang, Ni & Prentice (2011), Regional Environmental Change 11:715-727,
DOI 10.1007/s10113-011-0204-2.

이 논문은 BIOME4의 steady-state assumption과 BIOME4 NPP를 이용해 vegetation carbon pool과 soil carbon pool을 계산한다.

[
C_{veg}=NPP,	au_{veg}
]

[
C_{soil}=NPP,	au_{soil}
]

여기서 (C_{veg})는 **vegetation carbon storage**, 단위 kg C m^-2이다.
이는 AGB가 아니라 vegetation 전체 carbon pool이다.

Wang et al.은 최근 기후/CO2에서 발표된 field carbon-storage 자료를 mega-biome별 대표값으로 합성하고,
BIOME4가 계산한 mega-biome 평균 NPP로부터 (	au_{veg}=C_{veg}/NPP)를 역산했다.

Table 1:

| mega-biome | Cveg kg C m^-2 | NPP kg C m^-2 yr^-1 | tau_veg yr |
|---|---:|---:|---:|
| Tropical forest | 34 | 1.40 | 24 |
| Warm-temperate forest | 18 | 1.22 | 15 |
| Temperate forest | 9 | 0.88 | 10 |
| Boreal forest | 12 | 0.46 | 26 |
| Grassland/dry shrubland | 2 | 0.52 | 4 |
| Savanna/dry woodland | 4 | 0.98 | 4 |
| Desert | 1 | 0.11 | 9 |
| Dry tundra | 4 | 0.20 | 20 |
| Tundra | 4 | 0.35 | 11 |

따라서 BIOME4 문헌 내부에서 가장 명확한 biomass-like state variable은 AGB가 아니라
[
oxed{C_{veg}=NPP,	au_{veg}}
]
이다.

## 3. Ji et al. (2016): Wang 방법의 BIOME4 재사용 사례

Ji et al. (2016), *Current forest carbon stocks and carbon sequestration potential in Anhui Province, China*,
Chinese Journal of Plant Ecology 40(4):395-404,
DOI 10.17521/cjpe.2015.0147.

이 연구는 BIOME4가 산출한 NPP를 Wang et al. (2011)의 개선된 carbon-storage 방법으로 변환하여
climax forest vegetation carbon density와 soil carbon density를 계산했다.

논문이 보고한 BIOME4-derived climax-forest vegetation carbon density:

| forest type | vegetation C density t C ha^-1 | kg C m^-2 |
|---|---:|---:|
| Temperate deciduous broadleaf forest | 126 | 12.6 |
| Temperate needleleaf forest | 100 | 10.0 |
| Subtropical deciduous broadleaf forest | 132 | 13.2 |
| Mixed evergreen-deciduous broadleaf forest | 150 | 15.0 |
| Subtropical evergreen broadleaf forest | 163 | 16.3 |
| Subtropical needleleaf forest | 154 | 15.4 |

즉 Wang의 (NPP	au_{veg}) 접근은 일회성 제안이 아니라 이후 BIOME4 forest-carbon 연구에서도 실제로 사용되었다.

## 4. AGB 분리 여부

이번 BIOME4 문헌 검색에서 **BIOME4 NPP로부터 total vegetation carbon을 계산한 연구는 확인되었지만,
그 (C_{veg})를 aboveground와 belowground로 내부적으로 분리하는 BIOME4-native 공식은 확인하지 못했다.**

특히 확인한 BIOME4 문헌에서 다음은 찾지 못했다.

- BIOME4 PFT별 aboveground allocation fraction
- BIOME4 PFT별 root:shoot ratio를 이용한 Cveg -> AGB 공식
- BIOME4 내부 carbon-pool state에서 stem/branch/root를 분리하는 식
- Wang et al. (C_{veg})를 AGB로 직접 변환하는 공식

따라서
[
AGB=C_{veg}
]
라고 둘 수 없고,
[
AGB=f(C_{veg})
]
를 외부 allocation 문헌으로 새로 만드는 것도 이번 BIOME4-only 원칙에서는 하지 않는다.

## 5. Pelletier Eq. (5) 실험과의 연결

Pelletier et al. (2013)의
[
AGB=eexp(fEEMT)
]
원 계수를 현재 용늪 PB4에 무보정 적용한 21-0 ka 새 실행은 물리적으로 실패했다.

복구된 결과:

- static Jang: 24/62 = 38.71%
- dynamic Jang: 54/62 = 87.10%
- baseline dynamic: 55/62 = 88.71%
- Pelletier AGB time-mean basin mean:
  - static 3414.11 kg m^-2
  - dynamic 3487.47 kg m^-2
- Wang Cveg time-mean basin mean:
  - static 4.142 kg C m^-2
  - dynamic 3.780 kg C m^-2
- mean cellwise Pelletier-AGB vs Wang-Cveg correlation:
  - static r = 0.720
  - dynamic r = -0.905

따라서 Pelletier Arizona AGB proxy를 그대로 쓰는 안은 기각한다.

## 6. 현재 과학적 판정

BIOME4-only 원칙을 지키면 정직한 선택지는 두 개뿐이다.

### 선택 A: AGB라는 변수를 유지

현재까지 확인한 BIOME4 문헌만으로는 **AGB를 완결적으로 계산할 수 없다.**
따라서 추가 외부 allocation/root:shoot/allometry 문헌을 넣지 않는다면 AGB 사용을 포기해야 한다.

### 선택 B: geomorphic vegetation state를 BIOME4 vegetation carbon으로 재정의

BIOME4 문헌 안에서 직접 방어 가능한 식생량은

[
oxed{C_{veg}=NPP,	au_{veg}}
]

이다.

따라서 Pelletier의 지형수송계수

[
k_d=cEEMT+dAGB
]

를 PB4의 새 모델식으로

[
oxed{k_d=c_EEEMT+d_CC_{veg}}
]

처럼 **명시적으로 재정의**하는 것이 BIOME4-only 관점에서는 가장 일관적이다.

그러나 이 경우 (d_C)는 Pelletier의 기존 (d=0.05)를 그대로 쓸 수 없다.
단위와 state-variable 정의가 바뀌므로 (d_C)의 독립적인 결정방법이 필요하다.

이 점을 해결하지 않고 (C_{veg})를 AGB 자리에 그냥 대입하는 것은 금지한다.

## 7. 누더기 없는 다음 단계

다음 실험은 여러 모델을 섞지 않고 두 단순 ablation만 비교한다.

1. **EEMT-only**
[
k_d=c_EEEMT
]
AGB 항을 제거한다. BIOME4 NPP는 EEMT의 biological-energy term을 통해 이미 반영된다.

2. **BIOME4-Cveg**
[
C_{veg}=NPP	au_{veg}
]
[
k_d=c_EEEMT+d_CC_{veg}
]
Wang/Ji의 BIOME4 carbon-storage lineage만 사용한다.

두 경우 모두 기존 baseline, Pelletier Eq.(5) 후보와 별도 candidate로 유지하며,
(c_E,d_C)를 검증 정확도에 맞춰 임의 튜닝하지 않는다.

## 8. 최종 요약

- BIOME4 자체: NPP/LAI/biome은 직접 계산, total AGB pool은 없음.
- Wang et al. (2011): BIOME4 NPP -> vegetation carbon (C_{veg}=NPP	au_{veg}).
- Ji et al. (2016): 같은 방법을 실제 forest carbon-density simulation에 재사용.
- BIOME4-only literature에서 Cveg -> AGB 분할식은 현재 확인되지 않음.
- 따라서 BIOME4-only 원칙 아래에서는 **AGB를 억지로 만들지 말고 Cveg를 명시적인 새 geomorphic vegetation state로 쓰거나, AGB term 자체를 제거하는 것이 정직하다.**
- BIOME3, LPJ, Xue, Malhi, 한국 AGB 지도 회귀는 이 bridge에 사용하지 않는다.
