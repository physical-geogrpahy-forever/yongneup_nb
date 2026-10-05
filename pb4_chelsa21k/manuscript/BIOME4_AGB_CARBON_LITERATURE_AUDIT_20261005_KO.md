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


# 9. 추가 검색으로 확인한 BIOME4→biomass→AGB 직접 경로

이전 판정인 "BIOME4-only 문헌에서 AGB로 갈 수 있는 경로를 찾지 못했다"는 검색이 불충분했다. 추가 검색에서 **BIOME4 biome을 실제 biomass density에 연결한 직접 선행연구**를 확인했다.

## 9.1 Ragon et al. (2024): BIOME4 biome → ecosystem biomass density

Ragon et al. (2024), *Alternative climatic steady states near the Permian–Triassic Boundary*, Scientific Reports 14:26136,
DOI 10.1038/s41598-024-76432-8.

이 연구는 BIOME4의 28 biome을 ecosystem type에 대응시키고, Houghton et al. (2009)의 mean living biomass density를 할당해 terrestrial biomass를 계산했다. 여러 값이 있을 때는 Saugier et al. (2001)을 사용했다.

관련 매핑:

| BIOME4 biome | ecosystem group | total living biomass |
|---|---|---:|
| 4 Temperate deciduous broadleaf forest | Temperate forests | 270 Mg ha^-1 |
| 5 Temperate evergreen needleleaf forest | Temperate forests | 270 |
| 6 Warm-temperate evergreen broadleaf and mixed forest | Temperate forests | 270 |
| 7 Cool mixed forest | Temperate + boreal forests | 160 |
| 9 Cool-temperate evergreen needleleaf and mixed forest | Temperate + boreal forests | 160 |
| 8 Cool evergreen needleleaf forest | Boreal forests | 83 |
| 10 Cold evergreen needleleaf forest | Boreal forests | 83 |
| 11 Cold deciduous forest | Boreal forests | 83 |
| 17 Temperate evergreen needleleaf open woodland | Boreal forests | 83 |

즉 **BIOME4의 biome 결과를 biomass density로 후처리하는 방법은 실제 문헌에 존재한다.**

## 9.2 Saugier et al. (2001): total biomass가 아니라 shoot biomass까지 분리

Ragon이 biomass source로 우선 사용한 Saugier et al. (2001), *Estimations of Global Terrestrial Productivity: Converging Toward a Single Number?*는 주요 biome별 biomass를 shoot와 root로 분리한다.

dry mass 기준:

| biome | shoot biomass g m^-2 | root biomass g m^-2 | total g m^-2 |
|---|---:|---:|---:|
| Tropical forest | 30,400 | 8,400 | 38,800 |
| Temperate forest | 21,000 | 5,700 | 26,700 |
| Boreal forest | 6,100 | 2,200 | 8,300 |
| Mediterranean shrubland | 6,000 | 6,000 | 12,000 |
| Tropical savanna/grassland | 4,000 | 1,700 | 5,700 |
| Temperate grassland | 250 | 500 | 750 |
| Desert | 350 | 350 | 700 |
| Arctic tundra | 250 | 400 | 650 |

여기서 **shoot biomass는 dry aboveground biomass에 해당한다.**

따라서 Ragon의 BIOME4 biome→ecosystem mapping에 Saugier의 shoot biomass를 사용하면, 별도의 NPP→AGB 회귀식 없이 직접 AGB를 줄 수 있다.

용늪에 중요한 forest biome의 direct AGB lookup:

[
AGB_{temperate}=21.0 {m kg dry m^{-2}}
]

[
AGB_{boreal}=6.1 {m kg dry m^{-2}}
]

BIOME4 7/9의 "temperate + boreal forests"는 Saugier의 두 forest biome을 합친 Ragon/Houghton group이다. Saugier가 제시한 면적을 이용한 area-weighted shoot biomass는

[
AGB_{temp+boreal}
=
rac{21.0	imes10.4+6.1	imes13.7}{10.4+13.7}
approx12.53 {m kg dry m^{-2}}
]

이다.

따라서 forest biome mapping은:

- BIOME4 4/5/6 → 21.0 kg dry m^-2
- BIOME4 7/9 → 12.53 kg dry m^-2
- BIOME4 8/10/11/17 → 6.1 kg dry m^-2

## 9.3 이 경로의 장점

이 방법은 다음을 사용하지 않는다.

- BIOME3
- LPJ allocation
- Xue residence time
- Malhi wood allocation
- 임의의 NPP→AGB 계수
- Pelletier Arizona EEMT→AGB 경험식

구조는 단순하다.

[
BIOME4 biome
ightarrow
Ragon ecosystem mapping
ightarrow
Saugier shoot biomass
ightarrow
AGB
]

즉 **BIOME4 결과에서 AGB를 얻는 published post-processing lineage**가 존재한다.

## 9.4 한계

이 방식은 standing biomass가 biome별 대표값이므로 같은 biome 안의 NPP 차이에 따른 연속적인 AGB variation은 표현하지 않는다.
따라서 spatial/temporal AGB는 BIOME4 biome이 바뀔 때 단계적으로 바뀐다.

그러나 현재 `AGB=0.010 NPP`처럼 출처 없는 연속 proxy를 쓰는 것보다 문헌적 provenance가 훨씬 명확하고,
Pelletier의 필요한 단위인 kg dry m^-2와 직접 일치한다.

## 9.5 다음 candidate

다음 AGB candidate는 우선 이 **BIOME4-biome/Saugier-shoot AGB lookup**으로 정의한다.

Pelletier의 다른 식은 그대로 유지:

[
k_d=cEEMT+dAGB
]

AGB만 위 biome-based dry shoot biomass로 교체한다.

새 candidate는 기존 canonical baseline을 덮어쓰지 않고 별도 21–0 ka ablation으로 검증한다.


# 10. 목표 정정 및 우선 후보: BIOME4 NPP + PFT → dry AGB

## 10.1 실제 필요한 상태변수

본 연구에서 필요한 것은 biome별 고정 AGB가 아니라 다음과 같은 셀별, 시점별 함수이다.

[
\boxed{AGB_{dry}=f(NPP, PFT)}
]

즉 BIOME4가 각 셀과 시점에서 계산한 NPP 변화가 AGB에 연속적으로 반영되어야 하고, 같은 NPP라도 PFT의 탄소배분과 조직 체류시간 차이에 따라 AGB가 달라져야 한다.

따라서 9절의 Ragon-Saugier biome lookup은 문헌적 참고 및 독립 sensitivity candidate로만 남기며, **주 AGB bridge 후보로 채택하지 않는다.** 이 절의 판정이 9.5의 우선 candidate 판정을 대체한다.

## 10.2 BIOME4 자체에서 확보되는 입력

BIOME4 v4.2b2는 각 PFT에 대해 최적 NPP와 LAI를 계산하고 경쟁 후 dominant PFT를 출력한다. 원본 코드에서 PFT별 최적 NPP는 `optnpp(pft)`, 최적 LAI는 `optlai(pft)`이며, 최종 출력에는 dominant PFT와 PFT별 NPP가 포함된다.

용늪 PB4 패키지에서는 이를 이미 다음 배열로 전달한다.

- `npp_node`
- `optpft_node`
- `biome4_full_id_node`
- `pftXX_mod_npp_node`

따라서 새로운 외부 식생모델을 실제로 동적으로 결합하지 않아도, BIOME4의 직접 산출인 `NPP + PFT`를 AGB bridge의 입력으로 사용할 수 있다.

## 10.3 IBIS의 PFT별 NPP allocation-turnover 식

Foley et al. (1996)과 Kucharik et al. (2000)의 IBIS 계열은 annual NPP를 PFT별 leaf, wood, fine-root carbon pool에 할당하고 각 pool의 residence time으로 탄소 stock을 계산한다.

Xue et al. (2016 preprint; 2017 final)은 IBIS로 potential AGB를 계산하고 전지구 2,101개 plot-level AGB 자료와 비교했다. 이 연구에서 PFT (i), biomass pool (j)의 변화는 다음과 같다.

[
\frac{\partial C_{i,j}}{\partial t}
=
a_{i,j}NPP_i
-
\frac{C_{i,j}}{\tau_{i,j}}
]

여기서 (a_{i,j})는 annual NPP의 해당 pool 배분비율이고, (	au_{i,j})는 해당 pool의 carbon residence time이다.

BIOME4는 equilibrium potential vegetation model이므로 AGB bridge에서도 평형상태를 취하면

[
\frac{\partial C_{i,j}}{\partial t}=0
]

이고 따라서

[
C_{i,j}=a_{i,j}\tau_{i,j}NPP_i
]

이다.

aboveground carbon은 leaf + wood만 포함하므로

[
\boxed{
AGB_{C,i}
=
NPP_i
\left(
a_{leaf,i}\tau_{leaf,i}
+
a_{wood,i}\tau_{wood,i}
\right)
}
]

가 된다.

Xue et al.은 IBIS가 계산한 carbon density를 dry AGB로 비교할 때 IPCC (2003)에 따라 2.0을 곱했다. 따라서 BIOME4 NPP 단위가 ({\rm g\ C\ m^{-2}\ yr^{-1}})일 때 dry AGB 단위 ({\rm kg\ dry\ biomass\ m^{-2}})로의 식은

[
\boxed{
AGB_{dry,i}
=
\frac{2}{1000}
NPP_i
\left(
a_{leaf,i}\tau_{leaf,i}
+
a_{wood,i}\tau_{wood,i}
\right)
}
]

이다.

중요하게도 이 식 전체가 Xue 논문에 한 줄의 BIOME4 회귀식으로 제시된 것은 아니다. **IBIS의 published pool equation과 PFT parameter table을 BIOME4의 equilibrium 성격에 맞추어 평형해로 축약한 문헌 기반 유도식**이다.

## 10.4 Xue et al. PFT parameter set

Xue et al. (2016) Table 1에서 용늪 forest PFT에 필요한 값은 다음과 같다.

| IBIS PFT | 식생형 | tau_leaf yr | tau_wood yr | a_leaf | a_wood |
|---:|---|---:|---:|---:|---:|
| 4 | Temperate conifer evergreen | 2.0 | 35 | 0.30 | 0.30 |
| 5 | Temperate broadleaf cold-deciduous | 1.0 | 35 | 0.30 | 0.40 |
| 6 | Boreal conifer evergreen | 2.5 | 52 | 0.30 | 0.30 |
| 7 | Boreal broadleaf cold-deciduous | 1.0 | 52 | 0.30 | 0.40 |
| 8 | Boreal conifer cold-deciduous | 1.0 | 52 | 0.30 | 0.40 |

## 10.5 BIOME4 PFT ↔ IBIS PFT 구조 대응

BIOME4 v4.2b2의 forest PFT 정의와 Xue/IBIS PFT 정의를 구조 및 잎 phenology 기준으로 대응시키면 다음과 같다.

| BIOME4 PFT | BIOME4 정의 | 대응 IBIS PFT | 대응 근거 |
|---:|---|---:|---|
| 4 | Temperate Deciduous Trees / Temperate Summergreen | 5 | temperate broadleaf cold-deciduous |
| 5 | Cool Conifer Trees / Temperate Evergreen Conifer | 4 | temperate conifer evergreen |
| 6 | Boreal Evergreen Trees | 6 | boreal conifer evergreen |
| 7 | Boreal Deciduous Trees | 7 또는 8 | boreal cold-deciduous tree |

BIOME4 PFT7은 boreal deciduous tree라는 넓은 기능형이므로 broadleaf deciduous와 deciduous conifer를 완전히 구별하지 않는다. 그러나 Xue Table 1에서 IBIS PFT7과 PFT8은 AGB 계산에 필요한 (	au_{leaf}, 	au_{wood}, a_{leaf}, a_{wood}) 값이 모두 동일하므로, **이번 AGB 계산에서는 이 구조적 모호성이 수치 결과에 영향을 주지 않는다.**

## 10.6 용늪 forest PFT별 직접 계산식

위 식과 Xue Table 1을 결합하면 다음과 같다.

### BIOME4 PFT4: temperate deciduous tree

[
a_L\tau_L+a_W\tau_W
=
0.30(1)+0.40(35)
=
14.30
]

[
\boxed{AGB_{dry}=0.0286\,NPP}
]

### BIOME4 PFT5: temperate evergreen conifer

[
0.30(2)+0.30(35)=11.10
]

[
\boxed{AGB_{dry}=0.0222\,NPP}
]

### BIOME4 PFT6: boreal evergreen conifer

[
0.30(2.5)+0.30(52)=16.35
]

[
\boxed{AGB_{dry}=0.0327\,NPP}
]

### BIOME4 PFT7: boreal deciduous tree

[
0.30(1)+0.40(52)=21.10
]

[
\boxed{AGB_{dry}=0.0422\,NPP}
]

따라서 forest PFT에 대한 우선 candidate는

[
\boxed{
AGB_{dry}(NPP,PFT)=
\begin{cases}
0.0286NPP & PFT=4\\
0.0222NPP & PFT=5\\
0.0327NPP & PFT=6\\
0.0422NPP & PFT=7
\end{cases}
}
]

이다.

예를 들어 (NPP=500\ {\rm g\ C\ m^{-2}\ yr^{-1}})이면 각각 14.30, 11.10, 16.35, 21.10 kg dry biomass m^-2가 된다.

## 10.7 왜 Xue/IBIS를 첫 candidate로 쓰는가

이 경로는 현재 목표에 대해 다음 장점이 있다.

1. NPP가 변하면 AGB가 연속적으로 변한다.
2. 같은 NPP라도 PFT별 allocation과 residence time 차이가 AGB에 반영된다.
3. Xue et al.은 IBIS를 이용해 실제 potential AGB를 계산하고 2,101개 plot-level AGB 자료로 평가했다.
4. carbon stock을 dry AGB로 변환하는 2.0 factor도 해당 연구에 명시되어 있다.
5. BIOME4와 IBIS 모두 PFT 기반 potential vegetation framework이므로 biome 평균 고정 lookup보다 기능형 대응이 직접적이다.
6. BIOME4 → DEMETER 결합의 Wu et al. (2009)도 BIOME4의 NPP/vegetation 출력을 외부 carbon-allocation 모듈로 전달해 carbon stock을 계산한 직접 선행례이므로, BIOME4 NPP에 별도 allocation/turnover 모듈을 붙이는 설계 자체는 선행연구와 부합한다.

## 10.8 중요한 불확실성과 sensitivity

PFT별 wood allocation과 wood residence time은 고정된 자연상수가 아니다.

Ma et al. (2024)은 IBIS의 biomass가 특히 `awood`, `tauwood0`, `tauroot`, `rgrowth`에 민감함을 보였고, forest age를 무시한 steady-state assumption이 젊은 산림의 biomass를 과대평가할 수 있음을 지적했다. 또한 Ma et al.의 prior/default `tauwood0`는 temperate forest 50 yr, boreal forest 100 yr 등으로 Xue의 35/52 yr와 상당히 다르다.

따라서 Xue parameter set을 보편적 정답으로 취급하지 않는다. 다만 본 용늪 모델의 BIOME4가 **equilibrium potential vegetation**을 계산하고, Xue 연구가 **potential AGB**를 직접 평가했다는 점 때문에 첫 번째 candidate로 Xue set을 사용한다. Ma et al. parameterization은 이후 sensitivity 범위로 사용한다.

## 10.9 비산림 PFT 처리

현재 forest PFT4-7은 직접 대응이 가능하지만, BIOME4 PFT8-13 전부를 Xue의 IBIS PFT에 자동 대응시키면 일부는 구조적 추정이 된다.

특히:

- BIOME4 PFT8은 C3/C4 temperate grass 혼합형
- PFT10은 C3/C4 woody desert
- PFT11은 tundra shrub
- PFT13은 lichen/forb

이므로, 이들을 임의로 Xue PFT에 강제 대응시키지 않는다.

**다음 실행 전 먼저 최종 PB4-McKenzie-nativeClimate 21-0 ka 전체 211시점에서 실제 `optpft_node` 분포를 감사한다.**

- 실제 사용 PFT가 4-7에 한정되면 forest candidate를 그대로 실행한다.
- 그 밖의 PFT가 존재하면 빈도, 면적, 시점부터 기록하고 각 PFT에 대한 별도 문헌 대응을 검토한다.
- unsupported PFT를 단일 계수나 가장 가까운 PFT로 조용히 대체하지 않는다.

## 10.10 현재 판정

현재 우선순위는 다음과 같다.

[
\boxed{
BIOME4\ NPP + BIOME4\ dominant\ PFT
\rightarrow
Xue/IBIS\ PFT\ allocation+turnover
\rightarrow
dry\ AGB
}
]

이는 기존 `AGB=0.010*NPP`를 PFT별 문헌 기반 계수로 대체하며, Ragon-Saugier의 biome-fixed AGB lookup보다 본 연구가 요구하는 시간 및 공간 연속성을 보존한다.

단, **아직 production에 반영하지 않는다.** 먼저 21-0 ka PFT coverage audit을 수행한 뒤 별도 candidate로 전체 실행하고 기존 canonical baseline과 비교한다.

## 10.11 핵심 문헌

- Foley, J. A., Prentice, I. C., Ramankutty, N., Levis, S., Pollard, D., Sitch, S., & Haxeltine, A. (1996). An integrated biosphere model of land surface processes, terrestrial carbon balance, and vegetation dynamics. Global Biogeochemical Cycles, 10, 603-628. https://doi.org/10.1029/96GB02692
- Kucharik, C. J., Foley, J. A., Delire, C., Fisher, V. A., Coe, M. T., Lenters, J. D., Young-Molling, C., Ramankutty, N., Norman, J. M., & Gower, S. T. (2000). Testing the performance of a dynamic global ecosystem model: Water balance, carbon balance, and vegetation structure. Global Biogeochemical Cycles, 14(3), 795-825. https://doi.org/10.1029/1999GB001138
- Xue, B.-L. et al. (2016). Evaluation of modeled global vegetation carbon dynamics: Analysis based on global carbon flux and above-ground biomass data. Biogeosciences Discussions. https://doi.org/10.5194/bg-2016-142
- Xue, B.-L. et al. (2017). Evaluation of modeled global vegetation carbon dynamics: Analysis based on global carbon flux and above-ground biomass data. Ecological Modelling, 355, 84-96. https://doi.org/10.1016/j.ecolmodel.2017.04.012
- Wu, H., Guiot, J., Peng, C., & Guo, Z. (2009). New coupled model used inversely for reconstructing past terrestrial carbon storage from pollen data: validation of model using modern data. Global Change Biology, 15, 82-96. https://doi.org/10.1111/j.1365-2486.2008.01712.x
- Ma, R. et al. (2024). Stepwise Calibration of Age-Dependent Biomass in the Integrated Biosphere Simulator (IBIS) Model. Journal of Advances in Modeling Earth Systems. https://doi.org/10.1029/2023MS004048


# 11. 21–0 ka 전체 PFT coverage audit와 PFT10 처리

## 11.1 실행 정보

Section 10의 PFT-specific AGB bridge를 실제 candidate로 실행하기 전에 최종 production 모델의 PFT coverage를 추측하지 않고 전수 확인했다.

- 실행일: 2026-10-05
- 실행 상태: 새 전체 실행
- 모델: PB4-McKenzie-nativeClimate
- canonical SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
- 기후: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 기간: 21.0-0.0 ka BP
- 간격: 0.1 kyr
- 시점 수: static 211 + dynamic 211
- 과학모델 수정: 없음
- 추가 사항: `optpft_node`와 full BIOME4 biome의 셀별 count만 기록

결과 파일:
`pb4_chelsa21k/results/pft_coverage_audit_20261005/`

결과 커밋:
`be862634bbc7040f3d4fa76b9869645d43a8d672`

## 11.2 실제 선택된 PFT

| mode | BIOME4 PFT | 출현 시점/211 | 누적 cell-observations | 시점 최대 셀 | cell-weighted mean NPP g C m^-2 yr^-1 |
|---|---:|---:|---:|---:|---:|
| static | 4 | 47 | 11,242 | 298 | 535.60 |
| static | 6 | 186 | 51,636 | 298 | 385.53 |
| dynamic | 0 | 145 | 1,231 | 26 | 0 |
| dynamic | 4 | 47 | 11,099 | 295 | 535.53 |
| dynamic | 6 | 186 | 48,107 | 298 | 386.14 |
| dynamic | 7 | 201 | 2,241 | 31 | 307.94 |
| dynamic | 10 | 90 | 200 | 8 | 6.08 |

따라서 식생이 실제로 선택된 PFT는 **4, 6, 7, 10**뿐이다. PFT5는 forest bridge에는 정의해 두지만 이번 canonical 21-0 ka 실행에서는 실제 dominant PFT로 선택되지 않았다.

PFT0은 dynamic 지형에서 BIOME4 식생이 없는 셀로, NPP=0이므로 AGB=0으로 처리한다.

## 11.3 PFT10의 문헌 대응

BIOME4 v4.2b2 원 코드에서 PFT10은 `C3/C4 woody desert plant type`이며 `pftdata`에서 phenological type=1, 즉 evergreen으로 정의된다.

Xue et al. (2016/2017)의 IBIS PFT 중 가장 직접적인 구조 analogue는 **PFT9 evergreen shrub**이다.

Xue Table 1의 IBIS evergreen shrub 값:

[
\tau_L=1.5,quad
\tau_W=5,quad
a_L=0.45,quad
a_W=0.15
]

따라서 Section 10과 동일한 equilibrium dry-AGB 식을 사용하면

[
a_L\tau_L+a_W\tau_W
=
0.45(1.5)+0.15(5)
=
1.425
]

[
\boxed{
AGB_{dry,PFT10}
=
\frac{2}{1000}(1.425)NPP
=
0.00285NPP
}
]

이다.

이것은 BIOME4 PFT10과 IBIS PFT9가 같은 모델 PFT라는 뜻이 아니라, **woody shrub physiognomy와 evergreen leaf habit을 기준으로 한 명시적 cross-model PFT correspondence**이다.

이번 canonical coverage에서 PFT10의 mean NPP는 6.08 g C m^-2 yr^-1이므로 대표적인 AGB는

[
0.00285\times6.08
\approx0.0173 {m kg dry m^{-2}}
]

수준이다. 또한 전체 211시점에서 누적 200 cell-observations, 한 시점 최대 8셀에 불과하므로 전체 용늪 AGB 및 지형계수에 대한 기여는 매우 작을 것으로 예상된다. 단, 이 영향은 candidate 실행 결과로 확인한다.

## 11.4 실제 candidate에 사용할 lookup

[
\boxed{
AGB_{dry}(NPP,PFT)=
\begin{cases}
0 & PFT=0\\
0.0286NPP & PFT=4\\
0.0222NPP & PFT=5\\
0.0327NPP & PFT=6\\
0.0422NPP & PFT=7\\
0.00285NPP & PFT=10
\end{cases}
}
]

단위:

- 입력 NPP: g C m^-2 yr^-1
- 출력 AGB: kg dry biomass m^-2

PFT5는 현재 전기간 audit에서 선택되지 않았지만 temperate evergreen conifer에 대한 완전한 forest lookup을 위해 유지한다.

## 11.5 candidate 안전장치

새 candidate는 다음 원칙으로 실행한다.

1. 기존 canonical ZIP은 덮어쓰지 않는다.
2. AGB bridge 이외의 production 설정은 변경하지 않는다.
3. `optpft_node`와 `npp_node`를 직접 사용한다.
4. PFT0은 AGB=0.
5. PFT4/5/6/7/10은 위 문헌 기반 식 사용.
6. candidate의 지형 feedback 때문에 실행 도중 **새로운 PFT1-3, 8-9, 11-14가 실제 출현하면 조용히 근사하지 않고 즉시 실패시킨다.**
7. 새 PFT가 나오면 해당 PFT의 문헌 대응을 별도로 확정한 뒤 다시 실행한다.
8. 기존 `0.010*NPP` baseline AGB도 같은 실행에서 diagnostic으로 계산하여 새 AGB의 규모와 비율을 비교한다.

## 11.6 현재 판정

전기간 coverage audit 결과, 용늪 canonical 상태에서 필요한 실질적인 AGB bridge는 다음 네 식으로 거의 완결된다.

[
PFT4: 0.0286NPP
]

[
PFT6: 0.0327NPP
]

[
PFT7: 0.0422NPP
]

[
PFT10: 0.00285NPP
]

따라서 이제 문헌 검색 단계에서 실제 **21-0 ka PFT-specific NPP-to-AGB candidate 실행 단계**로 진행한다.


# 12. BIOME4 PFT + NPP → AGB 직접식 재검색 판정

## 12.1 검색 질문

이번 재검색의 질문은 하나로 제한했다.

[
AGB=f(BIOME4 NPP, BIOME4 PFT)
]

형태의 total aboveground biomass를 BIOME4 자체 PFT와 NPP에서 직접 산출하는 published 식 또는 published post-processing method가 존재하는가?

BIOME3, IBIS, LPJ 등의 PFT를 BIOME4 PFT에 임의 대응시키는 방법은 직접식으로 인정하지 않았다.

## 12.2 결론

현재까지 확인한 BIOME4 원 논문, Kaplan (2001) 박사논문, BIOME4 v4.2b2 원 코드, BIOME4 응용 논문과 BIOME4-탄소 결합 문헌에서 **BIOME4 PFT별 NPP를 total AGB로 변환하는 직접 published 식은 확인되지 않았다.**

Kaplan et al. (2003)과 후속 BIOME4 설명에서 모델의 직접 식생 산출은 PFT별 최적 NPP와 최적 LAI, dominant/subdominant PFT 및 biome이며, standing total AGB pool은 없다.

Peng et al. (2011)의 Wu et al. (2009) PCM 검토는 BIOME4의 equilibrium design 때문에 terrestrial carbon stocks를 직접 계산할 수 없다고 명시하며, 이를 해결하기 위해 BIOME4의 **NPP + biome type**을 DEMETER에 입력한다.

2026 Scientific Reports PCM-weathering 연구도 동일하게 BIOME4 부분에서 biome과 NPP를 얻고, annual NPP의 leaf/stem/root allocation은 DEMETER scheme을 사용한다.

## 12.3 BIOME4 내부의 Alloc은 AGB allocation fraction이 아님

Kaplan (2001) Table 1.4의 PFT별 `Alloc`은 "relative minimum allocation" 또는 "modifier to the minimum allocation"이다.

BIOME4 v4.2b2 원 코드에서도:

`litterfall = lai * Ln * allocfact(pft)`

`minallocation = litterfall`

로 사용되어, 현재 LAI가 지속가능하려면 NPP가 충족해야 하는 최소 allocation requirement를 조정한다.

따라서 `Alloc=1.2` 등을 leaf/stem/root NPP allocation fraction으로 해석할 수 없고, PFT별 AGB 계수로 사용할 수 없다.

## 12.4 BIOME4 내부 sapwood carbon도 total AGB가 아님

BIOME4 원 코드에는 sapwood maintenance respiration을 계산하기 위한

`stemcarbon = 0.5`

가 있으며, LAI와 결합해 sapwood respiration cost를 계산한다. 이 값은 active sapwood carbon requirement에 해당하는 내부 구조 parameter이지, heartwood, branch 및 전체 woody biomass를 포함하는 standing total AGB pool이 아니다.

따라서 BIOME4 내부 LAI/leaf/sapwood 항을 합해 total AGB라고 부르는 것도 허용하지 않는다.

## 12.5 가장 가까운 published BIOME4 coupling

현재 가장 가까운 직접 선행례는 Wu et al. (2009)의 BIOME4 + DEMETER PCM이다.

구조:

[
BIOME4 ightarrow (NPP, biome) ightarrow DEMETER ightarrow
leaf, stem, root, litter, soil carbon
]

이는 BIOME4 결과를 실제 carbon-allocation model에 연결한 published lineage라는 장점이 있지만, **BIOME4 PFT-specific bridge가 아니라 biome-specific bridge**이다.

따라서 이것을 BIOME4 PFT식이라고 표현해서는 안 된다.

## 12.6 이전 Xue/IBIS candidate의 지위 정정

Section 10-11에서 만든

[
AGB_{dry}=coefficient(PFT)	imes NPP
]

candidate는 published BIOME4 equation이 아니다.

이는 IBIS/Xue의 PFT별 allocation/residence-time parameters를 BIOME4 PFT에 cross-model mapping하여 만든 **실험적 cross-model candidate**이다. 따라서 문헌 우선 후보 또는 production 식으로 승격하지 않는다.

해당 실행 결과는 sensitivity experiment로 보존하되, direct BIOME4-compatible 문헌식이 확인되었다고 인용해서는 안 된다.

## 12.7 현재 과학적 선택지

직접 BIOME4 PFT + NPP → total AGB 식이 확인되지 않았으므로, 다음 선택지는 명확히 구분한다.

1. BIOME4 lineage를 최우선할 경우: Wu et al. (2009)의 BIOME4 NPP + biome → DEMETER allocation을 재현한다.
2. PFT-specific을 최우선할 경우: 관측 기반 또는 독립 PFT-specific NPP/ANPP → AGB 관계를 찾아 BIOME4 PFT 정의와 직접 비교 가능한 경우에만 사용한다.
3. IBIS/Xue cross-model mapping은 sensitivity candidate로만 유지한다.
4. BIOME4 내부 Alloc 또는 sapwood respiration parameter를 total AGB로 오해해 사용하지 않는다.
