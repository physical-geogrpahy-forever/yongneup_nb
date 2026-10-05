> 최신 정정(Section 21): 역사적 평형 생체량 모델은 존재하며 BIOME-BGC는 줄기와 굵은뿌리를 분리한다. 모델의 존재와 BIOME4용 최종 변환계수의 검증을 구분한다.

> **2026-10-05 최종 적용 판정 업데이트(Section 20): JULES 기본계수의 용늪 최종 채택 안 함.** 정적 LAI→AGB 구조는 확인됐지만 BIOME4 LAI로 전이한 정확도는 미검증이며 원 모델도 온대/한대 탄소량 편향을 보고한다.

> **2026-10-05 LAI 경로 추가 확인(Section 18): JULES/TRIFFID에 정적 LAI→목질부 생체량 식이 존재함.** 굵은뿌리 분리와 full-leaf 정의를 명시한 전이식은 구성 가능하지만, 용늪 최종 계수의 검증/채택은 아직 아니다.

> **2026-10-05 최신 적용 판정(Section 17): Ise 원계수 채택 보류.** 식 재현은 확인했지만 관측연도 중첩 성숙림의 예측/관측 AGB 중앙값은 PFT5=0.489(n=15), PFT6=2.247(n=8), PFT7=1.810(n=1)이다. Section 16의 코드와 숫자는 진단 후보이며 검증된 최종 bridge가 아니다. 아래의 이전 상태 기록보다 이 판정을 우선한다.

> 2026-10-05 최신 판정: Section 16에서 Ise et al. (2010)의 VISIT 식과 공통 계수로 실행 가능한 총 NPP→평형 dry AGB 2군 모델을 제공한다. PFT4/5는 온대, PFT6/7은 아한대의 같은 계수이며, 네 PFT 독립 보정이나 native BIOME4 출력이 아니다. 이전의 모든 정적 모델이 없다는 표현은 철회한다.

# BIOME4-only AGB/vegetation-carbon 문헌 감사

작성일: 2026-10-05

> **첨부 원문 직접 검증: Section 15.** Figure S8의 NPP→지상부 목질 생산량 식을 확인했다. 관측 AGB/생산량 비율과 IBIS wood-pool 체류시간은 구분한다. PFT7의 Larix 대응 및 IBIS generic wood의 coarse-root 처리가 미검증이므로 이전 네 개 선형 AGB 계수를 확정값으로 사용하지 않는다.

> **정적 모델 존재 여부 정정: Section 14.** PFT별 NPP로 AGB를 계산하는 IBIS 탄소풀 방정식의 정적 평형해는 존재한다. BIOME4 자체 AGB 출력의 부재와 정적 모델의 부재를 혼동하지 않는다. Section 13의 관측비율과 Section 14의 모델 유도계수는 서로 다른 계산이다.

> **최신 판정(2026-10-05): Section 13을 우선한다.** Xia×Xue 조합은 정의 불일치로 철회했다. 실제 ForC/Luyssaert 관측비율을 계산했지만 검증된 최종 BIOME4→dry AGB 계수는 아직 확정하지 못했다. Section 10–11의 lookup은 실험 후보 기록이다.

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


# 13. Xia–Xue 후보 철회 및 Luyssaert 유래 실제 관측자료 계산 (2026-10-05)

## 13.1 이번 판정의 지위

**PFT4/5/6/7의 검증된 최종 NPP→dry AGB 계수는 아직 확정하지 못했다.**

이 절의 수치는 실제 공개 관측자료에서 새로 계산한 **진단용 stock/NPP 비율**이다. 논문에 발표된 BIOME4 고유 계수도, 평형 AGB를 검증한 회귀계수도 아니다. 이전 절의 후보를 production 식으로 승격하는 근거로 사용하지 않는다.

모델 입력 조건은 그대로 NPP와 PFT 두 개다. 관측 임령은 아래 자료 선별에만 사용했으며 모델에 임령/코호트를 추가하지 않았다. 이번 작업은 자료·문헌 검증이며 모델 실행이나 production AGB lookup 변경을 포함하지 않는다.

## 13.2 Xia (2019) × Xue (2017)을 최종식으로 사용할 수 없는 이유

- Xia의 관측 NPPwood는 stem + branch + **coarse root**다. Allocation의 분모는 leaf + wood + fine-root NPP의 합이다. 그 값을 aboveground wood allocation이라고 부르면 안 된다.
- Xue의 관측 residence-time 계산은 **지상부량 / 지상부 목질 생산량(stem + branch)**이다. NPP 전체로 나눈 값이 아니다. AGB numerator는 total aboveground biomass로 제시되며, leaf-free wood-only stock이라고 재정의하지 않는다.
- 따라서 Xia의 a_wood를 Xue의 residence time과 바로 곱하면 coarse-root 생산을 지상부량에 포함하는 오류가 생긴다.
- 두 논문의 boreal broadleaf deciduous 범주를 BIOME4 PFT7 전체와 같은 범주라고 단정할 수 없다. 특히 boreal deciduous needleleaf(Larix)가 같은 범주에 포함됐다고 주장할 근거가 없다.

Xue Table 2의 TeB 82.9, TeC 74.7, BoC 80.9, BoB 55.5 yr 자체는 확인했다. 그러나 그 값을 total NPP→AGB 계수나 BIOME4 PFT7 전체의 확정값으로 사용하지 않는다.

Primary sources:
- Xia et al. (2019), DOI [10.1029/2018JG004777](https://doi.org/10.1029/2018JG004777), [저자 기관 PDF](https://climatehomes.unibe.ch/~joos/papers/xia19jgrbg.pdf), Methods 2.1.
- Xue et al. (2017), DOI [10.1002/2016GB005557](https://doi.org/10.1002/2016GB005557), observation method and Table 2.

## 13.3 원자료 확보 경로와 버전

NASA/ORNL DAAC의 Luyssaert 배포본 DOI [10.3334/ORNLDAAC/949](https://doi.org/10.3334/ORNLDAAC/949)는 자료설명서를 확인했다. CSV/DB archive 직접 다운로드는 Earthdata 로그인에 막혀 원 archive 자체를 읽지는 못했다. 설명서의 변수 정의 확인과 실제 archive 확인을 혼동하지 않는다.

이번 실제 계산은 공개 [ForC 저장소](https://github.com/forc-db/ForC)의 아래 고정 snapshot에서 수행했다.

- Commit: 407c520e6350917bca42e6bf7d5031dbcc551362
- Commit date: 2024-08-08
- 파일: data/ForC_measurements.csv, data/ForC_sites.csv, data/ForC_variables.csv, data/ForC_pft.csv 및 metadata/
- 재사용: CC BY 4.0. ForC 출처를 표시하며 원 논문 citation ID도 결과 CSV에 보존했다.
- NPP와 AGB **양쪽**의 loaded.from에 Luyssaert_2007_cbob가 포함된 기록만 선택했다. _v3.3 표기와 복수 source chain을 포함하며 원문 그대로 CSV에 남겼다.
- citation.ID는 원 연구 논문으로 지정될 수 있으므로 citation.ID == Luyssaert만 요구하면 해당 database에서 유래한 자료를 잘못 누락한다.
- 이는 ForC에 공개 재수록된 Luyssaert 유래 자료다. ORNL 배포본 v3.1 전체 또는 Xia가 사용한 v3.3.1 전체를 직접 확보했다는 뜻이 아니다.

ForC 원 dictionary:
- [변수 정의](https://github.com/forc-db/ForC/blob/407c520e6350917bca42e6bf7d5031dbcc551362/data/ForC_variables.csv)
- [PFT 정의](https://github.com/forc-db/ForC/blob/407c520e6350917bca42e6bf7d5031dbcc551362/data/ForC_pft.csv)
- [관측 필드 정의](https://github.com/forc-db/ForC/blob/407c520e6350917bca42e6bf7d5031dbcc551362/metadata/measurements_metadata.csv)

## 13.4 동일하게 적용한 변수·자료 선별

| 필드 | 이번에 사용한 정의 | 단위 |
|---|---|---|
| NPP_1_C | foliage + branch + stem + coarse root + fine root 연간 생산량 | Mg C ha^-1 yr^-1 |
| biomass_ag_C | 전체 live aboveground biomass의 carbon stock | Mg C ha^-1 |

NPP_2~5의 understory, reproductive production, herbivory, VOC/exudates 등 추가 항을 NPP_1과 섞지 않았다. NPP_1은 구조적 생산량의 합이며 BIOME4 계산 NPP의 모든 탄소 유출 항과 동일함을 검증한 것은 아니다.

모든 PFT에 적용한 기준:

1. 같은 sites.sitename와 같은 명시적 plot.name로 연결한다. NI/NRA/NA/NAC 및 빈 관측구 이름은 제외한다.
2. NPP와 AGB 양쪽의 dominant.veg code가 같아야 한다.
3. 양쪽 mean > 0. flag.suspicious=1 및 D.precedence=0은 제외한다. 중복 지정이 없는 빈 precedence는 유지한다.
4. 양쪽 기록 임령 ≥100을 선택한다. 999는 실제 999년이 아니라 primary/old-growth/mature/intact designation이다. 이 선별은 평형을 입증하지 않으며 관리림·교란 이력을 자동 배제하지 않는다.
5. ForC의 biogeog는 생물지리 구역이지 boreal/temperate 기후 분류가 아니다. FAO.ecozone의 Temperate / Boreal prefix를 사용한다.
6. 동일 PFT의 관측구별 stock/NPP 비율 중앙값을 먼저 구한 뒤, 관측구들 사이의 중앙값을 구한다. 하나의 관측구에 여러 stock/flux 기록이 있다는 이유로 그 관측구를 여러 독립 표본처럼 세지 않는다.
7. 주 계산에서는 관측연도 일치 또는 동일 기록 임령을 추가로 요구하지 않았다. 시점이 다른/불명확한 같은 관측구 조합도 포함하므로 **동시 측정 계수라고 주장하지 않는다.** 연도 겹침 및 동일 기록 임령은 별도 diagnostic field로 제공한다.

| BIOME4에 대응시킨 관측 analogue | ForC 조건 |
|---|---|
| PFT4 | Temperate + 2TDB |
| PFT5 | Temperate + 2TEN |
| PFT6 | Boreal + 2TEN |
| PFT7 | Boreal + 2TDB / 2TDN / 2TD |

2TD는 broadleaf/needleleaf 혼합 또는 leaf type 불명인 deciduous group이다. 이번 ≥100년 paired subset에는 2TD가 없고 PFT7은 2TDB 1곳, 2TDN 1곳이다. Habit가 불명인 2TN·2TB, 혼합/불명인 2TM·2TREE는 이 네 그룹에 임의 할당하지 않았다.

이 표는 관측 분류를 BIOME4 PFT에 대응시킨 명시적 calibration 방법이며 ForC에 BIOME4 PFT 번호가 직접 기록되어 있는 것은 아니다.

## 13.5 실제 계산값과 단위

관측구 j에서

\[
T_j=\frac{AGB_{C,j}}{NPP_{1,C,j}}
\]

를 구했다. 두 원 변수의 Mg C ha^-1 단위가 약분되므로 T_j의 단위는 yr이다. **T_j는 aboveground carbon / total structural NPP의 유효 비율이며 woody residence time이 아니다.**

입력 NPP가 g C m^-2 yr^-1이면,

\[
AGB_C\ [{\rm kg\ C\ m^{-2}}]=\frac{T_i}{1000}NPP
\]

이고, 건조량 내 탄소질량 비율을 f_C라고 하면

\[
AGB_{\rm dry}\ [{\rm kg\ dry\ m^{-2}}]
=\frac{T_i}{1000f_C}NPP
=c_iNPP.
\]

아래 dry 계수는 **f_C=0.5라고 가정했을 때만** 성립한다. 새로운 독립 탄소함량 검증값으로 0.5를 주장하지 않는다.

| PFT | 관측구 n | T_i 중앙값 (yr) | 진단용 c_i (f_C=0.5) | 관측구 c_i 최소–최대 | 기록 연도가 겹치는 관측구 |
|---|---:|---:|---:|---:|---:|
| 4 | 8 | 25.23374 | 0.0504675 | 0.0231614–0.0698840 | 7 |
| 5 | 17 | 40.45765 | 0.0809153 | 0.0336043–0.2435928 | 15 |
| 6 | 8 | 19.66431 | 0.0393286 | 0.0179529–0.0715187 | 8 |
| 7 | 2 | 14.97645 | 0.0299529 | 0.0105370–0.0493688 | 1 |

전체 35 관측구, candidate stock/flux 조합 44행이다. 최소–최대는 신뢰구간이 아니다. NPP가 변할 때 AGB가 변하는 단일 NPP×PFT 형태의 관측 기반 계수는 **계산 가능했지만**, 이 값의 평형성·대표성·독립 예측 성능은 아직 검증되지 않았다.

연도 diagnostic은 point date의 calendar year와 알려진 start/end year를 비교했다. 예를 들어 1994와 1994.580822는 같은 calendar year로 처리한다. 다른 연도가 기록된 경우와 날짜가 미상인 경우를 CSV에서 구별한다. 연도 겹침 자체도 완전한 동시성 또는 평형의 증거는 아니다.

## 13.6 PFT7의 실제 두 관측구

| 관측구 | 식생 | NPP_1_C | AGB_C | 기록 임령 | 관측 시점 | 진단용 c (f_C=0.5) |
|---|---|---:|---:|---:|---|---:|
| Aheden / unmanaged | 2TDB (deciduous broadleaf) | 3.01 Mg C ha^-1 yr^-1 | 74.30 Mg C ha^-1 | 둘 다 180 | 둘 다 1995 | 0.0493688 |
| Tura / natural regeneration after fire.Larix gmelinii forest | 2TDN (deciduous needleleaf) | 2.16 Mg C ha^-1 yr^-1 | 11.38 Mg C ha^-1 | 둘 다 105 | NPP 2000–2004; AGB 날짜 NI | 0.0105370 |

Measurement IDs: Aheden NPP=99, AGB=87; Tura NPP=15318, AGB=15314.

Tura는 같은 관측구로 연결되는 자료이며 stock timing이 미상이다. 날짜 미상을 날짜 불일치 또는 비평형의 증거로 바꾸지 않는다. 다만 시간 대응을 검증했다고 말할 수도 없다.

두 관측구의 비율은 약 4.69배 다르다. n=2의 중앙값을 boreal deciduous forest 전체, 특히 Larix 중심 식생의 검증된 대표계수라고 확정하지 않는다. 따라서 “Xia/BoBD를 PFT7에 놓으면 해결된다”는 종전 주장도 철회한다.

## 13.7 재현 파일과 최종 상태

이 절의 숫자는 아래 파일로 재현할 수 있다.

- [관측 stock/flux 조합과 출처](BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_PAIRS_20261005.csv)
- [관측구별 비율](BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_PLOT_RATIOS_20261005.csv)
- [PFT별 요약](BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_SUMMARY_20261005.csv)
- [재현 스크립트](BIOME4_LUYSSAERT_FORC_REPRODUCE_20261005.py)

재현 명령:

    python BIOME4_LUYSSAERT_FORC_REPRODUCE_20261005.py /path/to/ForC/data /path/to/output

Python pandas가 필요하다. 입력 ForC revision을 위 commit에 고정해야 한다.

확인된 것은 **하나의 공개 관측 자료체계에 들어 있는 Luyssaert 유래 NPP와 AGB 자료로 네 forest PFT analogue의 비율을 동일한 방식으로 계산할 수 있다는 것**이다. 요청된 검증된 최종 dry-AGB 계수 네 개를 완성했다고 주장하지 않는다. 종별 논문을 PFT마다 새로 붙이는 방법은 사용하지 않았다.


# 14. 정적 NPP×PFT→AGB 모델 존재 여부 정정 (2026-10-05)

## 14.1 존재 여부와 적용 검증을 구분한다

**PFT별 NPP로 평형 AGB를 계산하는 정적 탄소풀 모델을 구성할 수 있으며, 기존 IBIS 탄소풀 방정식에 그 근거가 명시돼 있다. “그런 모델이 하나도 없다”는 판정은 하지 않는다.**

BIOME4 자체가 standing AGB를 출력하지 않는다는 사실, BIOME4 전용으로 발표된 직접 변환식을 아직 확인하지 못했다는 사실, 다른 모델의 동일한 PFT 체계에서 정적 평형해를 얻을 수 있다는 사실은 서로 다르다.

관측 NPP/AGB paired sample의 부족 역시 이 모델 구조의 부재를 뜻하지 않는다.

## 14.2 확인한 published equation과 정적 해

[Xue et al. (2017), Global Biogeochemical Cycles, DOI 10.1002/2016GB005557](https://doi.org/10.1002/2016GB005557), Section 2.4, Eq. (2)는 IBIS의 PFT i, biomass pool j에 대해

\[
\frac{dC_{i,j}}{dt}
=a_{i,j}NPP_i-\frac{C_{i,j}}{\tau_{i,j}}
\]

를 제시한다. 본문은 NPP를 leaves, stems, roots로 배분하며 IBIS의 a가 고정값이라고 설명한다. Wood residence-time 항은 stems and branches의 pool에 대응한다.

IBIS 전체 모델은 동적이다. 아래 식은 그 pool equation에서 dC/dt=0을 놓아 얻은 **정적 평형해**이지 IBIS 전체가 정적 모델이라는 주장이 아니다.

\[
C_{i,j}^{*}=a_{i,j}\tau_{i,j}NPP_i.
\]

지상부를 leaf와 stem/branch로 정의하고 뿌리 pool을 제외하면

\[
AGB_{C,i}^{*}
=NPP_i(a_{L,i}\tau_{L,i}+a_{W,i}\tau_{W,i}).
\]

NPP 입력 g C m^-2 yr^-1, dry AGB 출력 kg dry m^-2, dry-matter carbon fraction f_C라면

\[
AGB_{{\rm dry},i}^{*}
=\frac{NPP_i}{1000f_C}
(a_{L,i}\tau_{L,i}+a_{W,i}\tau_{W,i}).
\]

이는 기존 방정식에서 이번에 전개한 평형 유도식이다. Eq. (2) 자체가 BIOME4의 published equation은 아니다. 고정된 공통 parameter set을 선택하면 실행시 입력은 NPP와 PFT뿐이며 임령/코호트 이력은 필요하지 않다.

## 14.3 PFT 공통 parameter set이 제시된 자료와 그 지위

Xue et al.의 2016 discussion manuscript
[Evaluation of modeled global carbon dynamics: analysis based on global carbon flux and above-ground biomass data](https://bg.copernicus.org/preprints/bg-2016-142/bg-2016-142.pdf),
DOI 10.5194/bg-2016-142, Table 1 (PDF page 27)은 IBIS의 모든 12 PFT에 allocation 및 residence-time parameters를 한 표로 제시한다.

Section 10의 수치 출처는 이 **2016 preprint Table 1**이다. 위 2017 Global Biogeochemical Cycles 논문의 Table 1은 mixed-effect model comparison이며 이 parameter table이 아니다. 두 문헌의 제목·자료 규모·표를 구분하며 2016 manuscript를 확인 없이 “2017 final”로 표현하지 않는다. 2017 논문은 pool equation의 published 근거로 사용할 수 있지만 2016 Table 1의 모든 수치가 같은 논문의 확정 parameter라는 주장은 하지 않는다.

| 관측 analogue / BIOME4 대응 | IBIS PFT | a_L | tau_L yr | a_W | tau_W yr | f_C=0.5 가정의 평형 dry 계수 |
|---|---:|---:|---:|---:|---:|---:|
| Temperate deciduous / 4 | 5 | 0.30 | 1 | 0.40 | 35 | 0.0286 |
| Temperate evergreen conifer / 5 | 4 | 0.30 | 2 | 0.30 | 35 | 0.0222 |
| Boreal evergreen conifer / 6 | 6 | 0.30 | 2.5 | 0.30 | 52 | 0.0327 |
| Boreal deciduous broadleaf / 7 | 7 | 0.30 | 1 | 0.40 | 52 | 0.0422 |
| Boreal deciduous conifer / 7 | 8 | 0.30 | 1 | 0.40 | 52 | 0.0422 |

이 표는 동일 자료의 동일 parameter framework를 이용한 정적 계산이 실제 가능하다는 재현 예시다. 종별 관측논문을 PFT마다 붙인 결과가 아니다. Boreal deciduous broadleaf와 needleleaf 두 범주는 이 parameter set에서 동일한 AGB 계수를 갖는다.

다만 이 대응은 여전히 **BIOME4→IBIS의 명시적인 기능형 대응**이다. BIOME4 고유 계수라고 부르지 않으며, 이 절을 이유로 기존 production lookup이나 canonical 실행 결과를 변경하지 않았다. 관측자료에서 계산한 Section 13의 계수와 이 모델 parameter에서 유도한 계수를 혼합하지 않는다.

## 14.4 정정된 결론

목표인 AGB=f(NPP,PFT)의 정적 계산 구조는 존재한다. IBIS 탄소풀 모델의 평형 축약은 확인된 구체적 사례다. 남은 선택은 같은 framework의 parameter set을 사용한 외부 정적 AGB 모듈을 어떤 근거와 한계로 BIOME4에 적용할 것인지이며, “그런 모델이 존재하지 않는다”는 문제가 아니다.


# 15. 사용자가 첨부한 2017 본문 및 보충자료 직접 검증 (2026-10-05)

## 15.1 판정

**NPP→지상부 목질 생산량→AGB의 정적 계산식은 유도할 수 있다. 실제로 보충자료 Figure S8에 첫 단계의 수치 식이 있다. 그러나 이 두 파일만으로 BIOME4 PFT4/5/6/7 전체의 검증된 계수를 확정했다고 주장하지 않는다.**

중요한 새로운 확인은 Xia의 coarse-root 포함 a_wood 없이도 Xue (2017) 안에서 NPP→aboveground woody production 변환을 얻을 수 있다는 것이다.

또한 이전 절에서 IBIS의 generic wood를 항상 aboveground wood로 취급한 부분은 미검증이므로 적용을 보류한다. Section 10–11과 14의 네 개 선형 계수를 검증된 total dry AGB로 사용하지 않는다.

이번에는 첨부 파일을 직접 읽고 그림을 렌더해 확인했다. 보충자료를 “접근하지 못했음”으로 남긴 이전 상태를 대체한다. 새로운 BIOME4/PB4 실행과 production lookup 변경은 없다.

## 15.2 확인한 파일과 위치

본문:
Global Biogeochemical Cycles - 2017 - Xue - Global patterns of woody residence time and its influence on model simulation (1).pdf

- DOI: 10.1002/2016GB005557
- SHA256: bd1be6017423620ef12a516b930bc0281e1869de60328931a6fae2b3919ac888
- PDF page 2 / journal p.822: Eq. (1), AGB 및 aboveground woody productivity 정의
- PDF page 4 / journal p.824: Eq. (2), IBIS carbon-pool equation
- PDF page 12 / journal p.832: Figure S8을 통한 MODIS NPP→aboveground NPP 변환 사용 설명
- PDF page 13 / journal p.833: Table 2, model default 및 meta-analysis residence times

보충자료:
gbc20541-sup-0001-supplementary.docx

- SHA256: ff5596ca353a77d8054631ec447dd9916828679b753b4105f119e26b4c9fbbd4
- 원 OOXML에서 Table 1개 및 embedded image 8개 확인
- 렌더 page 2: Table S1 (Fluxnet site 목록)
- 렌더 page 6: Figure S4 (BoCe, BoB, BoCd를 별도 표기)
- 렌더 page 10: Figure S8 (총 NPP와 aboveground woody NPP의 관계)
- 원 Contents에는 S1–S7이라고 쓰였지만 실제 파일에 S8도 있다.

DOCX의 vector 그림을 PDF로 렌더하고, 그림 안의 수치·축·caption을 시각적으로 확인했다. 원 첨부 파일은 수정하지 않았다.

## 15.3 실제 Figure S8 식

총 NPP를 x라고 하면 Figure S8은

\[
P_{\rm AGwood,C}=F(x)
=0.0001x^2+0.3515x-14.828
\]

를 제시하며 R^2=0.7538이다.

- x: Total NPP, g C m^-2 yr^-1
- y: ANPP, g C m^-2 yr^-1
- Caption에서 y를 above ground woody NPP라고 정의한다.
- 원 관측자료는 Luyssaert et al. (2007)이다.
- 잎을 포함한 전체 ANPP가 아니라 여기서는 **지상부 목질 생산량**으로 읽어야 한다.
- 따라서 Xia의 stem + branch + coarse-root wood allocation을 지상부라고 바꾸어 사용하는 오류를 피할 수 있다.
- R^2=0.7538은 NPP→aboveground woody NPP 관계의 값이며, 네 PFT의 최종 AGB 예측 R^2가 아니다.

본문 p.832는 이 회귀로 MODIS NPP에서 aboveground NPP를 추정해 residence-time 비교에 사용했다고 명시한다. 저자도 이 과정이 추가 불확실성을 만든다고 설명한다.

이 식은 이차식이며 고정 allocation fraction이 아니다. 현재 주 목적을 “AGB=c_PFT NPP인 선형식만”으로 불필요하게 제한하지 않는다. 사용자 목표는 정적 AGB=f(NPP,PFT)다.

## 15.4 본문 Eq. (1)을 이용한 정적 유도식

원문 Eq. (1):

\[
\tau_w=\frac{\overline{AGB_{\rm dry}}}{\overline{P_{\rm AGwood,dry}}}.
\]

따라서 같은 정의의 생산량과 체류시간을 사용하면

\[
AGB_{{\rm dry},i}=\tau_{w,i}P_{\rm AGwood,dry}.
\]

S8의 carbon production을 dry production으로 바꾸기 위해 목질 생산량의 dry-matter carbon fraction f_C를 명시하면

\[
\boxed{
AGB_{{\rm dry},i}
=\frac{\tau_{w,i}}{1000f_C}
(0.0001NPP^2+0.3515NPP-14.828).
}
\]

NPP 입력은 g C m^-2 yr^-1, 출력은 kg dry m^-2다. 여기서 f_C=0.5는 **별도로 명시한 carbon→dry 변환 가정**이며, 첨부 논문이 이 유도식에 필요한 f_C를 새로 추정했다고 주장하지 않는다.

f_C=0.5이면:

\[
AGB_{{\rm dry},i}=0.002\tau_{w,i}F(NPP).
\]

이 식은 본문 Eq. (1)과 supplementary S8을 결합해 이번에 전개한 정적 식이다. 논문에 그대로 발표된 BIOME4 전용 회귀식은 아니다. 실행시에는 NPP와 PFT로 tau를 선택할 수 있으며 임령/코호트 입력은 추가하지 않는다.

Eq. (1)의 numerator가 이미 AGB이므로 이 관측 기반 effective residence-time 경로에 별도의 leaf stock을 다시 더하지 않는다. 한편 Eq. (2)의 wood-pool residence time을 사용할 때는 같은 해석을 자동 적용할 수 없다.

## 15.5 관측 tau의 범주와 실제 숫자 확인

| 대응을 검토한 BIOME4 PFT | Table 2 관측 범주 | Meta-analysis tau_w (yr) | 0.002 tau_w | NPP=500일 때 위 유도식의 dry AGB kg m^-2 |
|---|---|---:|---:|---:|
| 4 | TeB, temperate broadleaf | 82.9 | 0.1658 | 30.8258676 |
| 5 | TeC, temperate coniferous | 74.7 | 0.1494 | 27.7767468 |
| 6 | BoC, boreal coniferous | 80.9 | 0.1618 | 30.0821796 |
| 7의 broadleaf analogue만 | BoB, boreal broadleaf | 55.5 | 0.1110 | 20.6373420 |

NPP=500일 때 S8 production은 185.922 g C m^-2 yr^-1이다. 각 수치는 f_C=0.5 가정에서 실제로 산술 재현했다. 독립 AGB 검증 결과는 아니다. Table 2의 coarse vegetation category를 BIOME4 기능형에 대응시키는 가정도 명시적으로 남긴다.

**마지막 행을 BIOME4 PFT7 전체의 확정식으로 사용하지 않는다.** BoB는 broadleaf이고, supplementary S4는 BoB와 boreal conifer cold-deciduous (BoCd)를 명시적으로 분리한다. Figure S4에 BoCd가 있다는 사실만으로 BoB의 55.5 yr가 Larix에도 적용됨을 입증할 수 없다. BoC의 pooled value를 deciduous conifer의 별도 관측 tau로 표현하지도 않는다.

## 15.6 이 첨부 파일에서 없는 것

Table S1은 10개 Fluxnet 관측소 목록이다. a_leaf, a_wood, tau_leaf의 PFT parameter table이 아니다.

따라서 첨부한 2017 본문 및 SI에 Section 10의 2016 preprint Table 1 allocation values가 모두 들어 있다고 주장하지 않는다. Eq. (2)의 algebraic equilibrium은 확인되지만, 숫자 parameter와 pool의 지상부/지하부 범위는 별도로 검증해야 한다.

본문 Table 2의 IBIS default tau는 TeB=50, TeC=50, BoB=100, BoC=100 yr다. 이것은 2016 preprint parameter table의 temperate=35, boreal=52 yr와 다른 parameter set이다. 둘을 같은 설정으로 혼합하지 않는다.

또한 이 default wood-pool tau를 S8 production에 곱한 뒤 Eq. (1)의 total AGB와 동일하다고 자동 선언하지 않는다. Default pool residence time과 관측 AGB/woody-production의 유효 비율은 구분해야 한다.

## 15.7 IBIS generic wood의 지상부 범위 재검증

앞서 Section 14에서 a_W를 지상부 배분율로 곧바로 사용할 수 있다고 설명한 것은 검증이 부족했다.

Castanho et al.의 IBIS 연구에 대한 **저자 답변**은 IBIS의 generic woody biomass pool이 aboveground wood와 coarse roots를 포함한다고 명시한다:
[공식 Copernicus author response](https://bg.copernicus.org/preprints/9/C5858/2012/bgd-9-C5858-2012.pdf), PDF page 8, journal discussion p.C5865.

이는 해당 IBIS 기술에서의 직접 근거다. 첨부 Xue (2017)는 stems and branches라고 기술하므로, Xue가 실제로 사용한 구현과 그 output 변환을 확인하지 않은 채 모든 IBIS version의 wood pool이 aboveground-only라고 단정하면 안 된다.

generic wood에 coarse root가 포함되는 경우의 올바른 일반형은:

\[
AGB_{{\rm dry},i}^{*}
=\frac{NPP_i}{1000f_C}
\left[
a_{L,i}\tau_{L,i}
+g_{{\rm AGwood},i}a_{W,i}\tau_{W,i}
\right],
\]

여기서 g_AGwood는 generic wood stock 중 aboveground wood의 비율이다. 단순히 fine-root 항을 제외하는 것만으로 generic wood 내부의 coarse-root가 제거되는 것은 아니다.

**0.0286/0.0222/0.0327/0.0422를 total dry AGB로 확정한 종전 주장은 보류한다.** 수식의 평형해 존재 자체와, 실제 목질 pool을 지상부로 변환하는 문제가 별개임을 기록한다. 임의의 g_AGwood를 새로 넣지 않았다.

## 15.8 적용 범위와 현재 상태

- 정적 계산 구조: 확인.
- S8을 이용한 total NPP→aboveground woody production 변환의 수치 식: 확인.
- Eq. (1)에서 total AGB로 연결하는 유도: 정의와 f_C를 명시하면 가능.
- 전체 PFT7, 특히 deciduous conifer의 관측 residence-time 대응: 이 두 파일만으로 확인하지 못함.
- 기존 IBIS 계수 네 개를 그대로 total dry AGB라고 사용하는 것: 미검증.
- 모델 실행 또는 production 수정: 수행하지 않음.

S8 원 식은 NPP=0에서 -14.828을 주며, 약 41.69044 g C m^-2 yr^-1 미만에서 음수가 된다. 전체 격자에 적용한다면 비산림/무생산 및 저생산 셀의 처리 규칙이 별도로 필요하다. max(0,F(NPP))는 가능한 비음수 처리 방식이지만 **원 논문의 회귀식 자체가 아니라 구현자가 추가하는 규칙**이다. 이번 검증에서는 원 식을 바꾸지 않았다.

Figure S8 축은 0–2500까지 표시되지만 이를 명시된 정확한 calibration data range로 주장하지 않는다. 원자료 범위 밖의 extrapolation이나 PFT별 독립 정확도는 별도 확인 대상이다.


# 16. Ise et al. (2010): 총 NPP만으로 실행 가능한 VISIT 2군 평형 AGB 계산

2026-10-05 원문 Table 1(PDF p.3), Eq. (7)-(12)(p.4), Appendix A Eq. (A10)-(A15)(p.10)를 확인했다. DOI: https://doi.org/10.1029/2010JG001326 . 공저자 대학 사이트의 PDF: https://gms.ctahr.hawaii.edu/gs/handler/getmedia.ashx?dt=3&g=12&moid=6541 .

정적 NPP→생체량 모델이 없다는 종전 표현은 틀렸다. 이 논문은 성분별 NPP에서 평형 stock을 실제 계산한다. VISIT의 EPP 배분과 성장 호흡 계수를 이용하면 총 NPP의 성분별 배분율을 대수적으로 구할 수 있으므로 추가 GPP/기온/나이 입력 없이 leaf+aboveground stem 평형량을 계산할 수 있다.

**정확한 해상도:** Table 1은 temperate와 boreal forest의 pooled parameter set이다. BIOME4 PFT4/5→temperate, PFT6/7→boreal로 이식한다. 따라서 PFT4=5, PFT6=7의 계수가 같다. 네 PFT 각각을 보정한 관측식 또는 native BIOME4 출력으로 표현하지 않는다. Boreal broadleaf만 PFT7에 대입하지 않고 PFT6/7 모두 넓은 boreal model class로 취급하는 명시적 연결 가정이다. Larix를 별도 문헌에서 붙이지 않는다.

정의:
q_f=f_f(1-k_gf)
q_s=(1-f_f)f_s(1-k_gs)
q_r=(1-f_f)(1-f_s)(1-k_gr)
a_j=q_j/(q_f+q_s+q_r)
AGBdry=NPP*(a_f/k_f+a_s/k_s)/(1000*f_C)

ff와 fs는 총 NPP의 배분율이 아니므로 위 normalization이 필요하다. stem과 root의 sapwood/heartwood를 구분하는 원문의 pool framework를 사용한다. root carbon은 AGB에서 제외하며 generic IBIS wood에 임의 보정값을 넣지 않는다. 출력 AGB는 해당 3-pool 모델의 살아 있는 지상부 leaf+stem 합이다.

f_C=0.5를 명시적 공통 변환 가정으로 놓으면 c_temperate=0.039538209325339524, c_boreal=0.08935146961601986이다. NPP 단위 g C m^-2 yr^-1, AGB 단위 kg dry m^-2. NPP=500일 때 19.769104663과 44.675734808이다. 이 수치는 새 산술 계산이며 실제 용늪 예측/검증 결과가 아니다.

독립 Decimal 원문 식 재현, NPP budget, pool equilibrium, zero/scaling, carbon-fraction scaling, invalid-input checks를 새로 실행해 모두 확인했다. 생태학적 정확도는 새로 검증하지 않았다. 어린 산림/최근 교란 이후 실제 AGB 대신 equilibrium stock으로 해석한다.

상세 유도/원문 계수/범위: `BIOME4_ISE2010_STATIC_AGB_20261005_KO.md`.
실행 코드: `ise2010_static_agb.py`.

이번 결과는 **실행 가능한 2군 정적 모델**이다. PFT4/5/6/7마다 서로 다른 독립계수가 필요하다는 추가 조건까지 충족했다고 표현하지 않는다. 이전 Sections 13-15의 네 PFT 세분 검증 부족은 그대로 남지만, 그것을 모든 정적 모델의 부재로 확대하지 않는다. Production BIOME4/Pelletier code와 기존 기후/지형 실험은 변경하지 않았다.

# 17. Ise 원계수 적용성 검증: 현 프로젝트 최종값으로 채택하지 않음

2026-10-05 Section 16의 계산 후보에 대해 사용자가 실제 적용 가능성을 검증하라고 요청했다. 산술 재현과 프로젝트 적용 판정을 구분하여 다음 추가 검증을 새로 실행했다.

## 17.1 canonical BIOME4 코드 확인

PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip을 읽었고 SHA-256=eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d로 기존 canonical과 일치했다. 실행/수정하지 않았다.

원 Fortran은 npp=gpp-stemresp-leafresp-finerootresp-growthresp로 연간 순탄소생산량을 계산한다. 이것은 ANPP나 woody NPP가 아니다. findnpp는 LAI별 생산량을 비교하여 최대 NPP를 찾는다. output(3)의 연간 NPP가 Python out[2], npp_node로 전달된다. 서로 경쟁하는 PFT별 잠재 NPP를 합친 tree_npp_total_node/total_pft_npp_node를 forest total NPP라고 보고 사용하면 안 된다. NPP와 실제 선택한 PFT가 대응하는 입력을 써야 한다.

## 17.2 원계수와 관측 stock 대조

기존 ForC/Luyssaert-origin NPP_1_C/biomass_ag_C 연결자료 44행, 35개 site/plot을 사용했다. ForC commit=407c520e6350917bca42e6bf7d5031dbcc551362. 두 reported ages >=100 조건(999는 성숙림 표식)이 적용되어 있다. 계수를 이 관측자료에 fit하지 않았다.

Mg C ha^-1 yr^-1 NPP를 100배하여 g C m^-2 yr^-1, Mg C ha^-1 AGB를 0.1/f_C배하여 kg dry m^-2로 바꿨다. 예측/관측 양쪽의 f_C=0.5는 비율에서 소거된다. plot별 여러 pair ratio를 중앙값으로 먼저 요약하고, PFT 내 plot들은 동일 가중치로 요약했다.

| 관측연도 중첩 자료 | 관측구 n | 예측/관측 AGB 중앙값 | plot 비율 평균 절대백분율오차 |
|---|---:|---:|---:|
| PFT4 | 7 | 0.7839745355 | 27.02567382% |
| PFT5 | 15 | 0.4886370497 | 48.30593038% |
| PFT6 | 8 | 2.2473047317 | 157.09026144% |
| PFT7 | 1 | 1.8098783549 | 80.98783549% |

시간 중첩+동일 reported age 조건의 n은 6/14/8/1이며 중앙값 0.7834397225/0.4808876354/2.2473047317/1.8098783549이다. 주요 불일치는 유지된다.

PFT7 strict sample은 Aheden broadleaf 1곳이다. Tura/Larix는 AGB 관측연도가 불명이라 strict sample에서 제외했다. 전체 진단에 포함하면 Tura 예측/관측=8.479752828이지만 이것을 동시점 검증값이라고 제시하지 않는다. PFT7/Larix 적용성이 검증됐다고 표현하지 않는다.

## 17.3 판정

원계수 c_temperate=0.0395382093, c_boreal=0.0893514696의 산술과 조건부 평형식은 맞다. 그러나 이 계수를 현 프로젝트의 검증된 최종 AGB 계수로 사용하지 않는다. PFT5/6 관측 불일치가 크고, PFT7 동시점 검증 표본은 1곳이다. 이 표본이 교란 없는 수학적 평형만으로 구성되었다는 근거도 없어 원 논문 이론 자체를 기각하는 검증이라고 주장하지 않는다.

Section 16은 실행 가능한 **계산 후보의 존재**를 증명한 것이며, 실제 적용 검증 통과 선언이 아니다. 원계수 계산기는 진단용으로 보존하고 출력에 project application status를 명시했다. 새 적용성 검사 및 관측별 provenance를 audit_ise2010_applicability.py와 BIOME4_ISE2010_APPLICABILITY_20261005.json으로 기록한다. 상세 문서의 첫머리에도 이 적용 보류 판정을 반영했다.

Production의 기존 NPP→AGB proxy를 이 후보로 교체하지 않았다. 기존 0.010 proxy가 이 후보보다 검증되었다는 뜻도 아니며, 최종 NPP/PFT→AGB bridge 확보 과제는 미완료다.


## 18. LAI 기반 모델 경로: JULES/TRIFFID allometry 확인 (2026-10-05)

**판정: LAI와 PFT를 이용한 정적 생체량 진단식은 실제 식생모델에 존재한다. BIOME4에 옮겨 쓰는 것은 모델 간 allometry 전이이며, 용늪의 검증된 최종 AGB 모형이라는 뜻은 아니다.**

### 18.1 원문에서 확인한 식과 입력

Harper et al. (2018), JULES4.6/JULES-C2, DOI 10.5194/gmd-11-2857-2018, Section 2.3.1 Eq. (4):
Cwood = awl * Lbal^(5/3), 단위 kg C m^-2.
Lbal은 계절 최대/잠재 LAI이다. 수고는 Eq. (5)로 이 탄소량에서 다시 계산되므로, 이 진단식을 이용할 때 수고나 임령을 독립 입력으로 요구하지 않는다. JULES 전체 시뮬레이션은 동적 탄소수지 모형이다. 여기서 추출하는 것은 그 안의 정적 allometry이며 JULES 전체를 실행한 결과와 동일하다고 주장하지 않는다.

Wiltshire et al. (2021), JULES-CN, DOI 10.5194/gmd-14-2161-2021, Section 3.1.1 Eq. (2)-(4), Section 3.1.2 Eq. (9)도 같은 구조를 명시한다:
- Cleaf = sigma_l * Lbal
- Cfine_root = Cleaf
- W = awl * Lbal^bwl
- 실제 계절 LAI = p * Lbal
- W는 지상 stem과 굵은뿌리를 합친 풀이다. 이를 AGB로 그대로 쓰지 않는다.
- full leaf out에서는 labile leaf reserve가 0이다. 따라서 잎 항을 더한 아래 식은 full-leaf AGB를 뜻한다.

### 18.2 지상부와 건물량으로의 명시적 변환

Wolf et al. (2011), DOI 10.1029/2010GB003917, paragraph [14]는 Luyssaert 자료의 coarse-root/wood 관계(n=40, r=0.972)를 조사하고, TRIFFID 등 모델 비교에서 stem:coarse-root = 75:25를 적용했다. Table 1의 stem은 trunk + branch이며 질량은 건물량이다.
이는 TRIFFID 원모형이 굵은뿌리를 별도 예측한다는 뜻이 아니라, 통합 woody pool을 관측 정의에 맞추는 공통 분리 가정이다. 모든 PFT에 같은 가정을 적용하며 PFT별로 다른 수종 논문을 붙이지 않는다. 지상과 지하 목질부의 탄소분율이 같다는 가정하에 탄소 풀에도 0.75를 적용할 수 있다.

조건부 변환식:
AGB_full_leaf_dry = LMA * Lbal + 0.75 * awl * Lbal^(5/3) / fC_wood
단위 kg dry matter m^-2.

LMA는 잎 건물량/잎면적, fC_wood는 목질부 건물량의 탄소분율이다. 잎 건물량을 LMA로 직접 계산하므로 잎 탄소분율과 목질부 탄소분율을 혼동하지 않는다. fC_wood=0.5를 쓴 수치 예시는 별도 명시 가정이며 2018 논문의 목질부 탄소분율로 확인된 값이라고 하지 않는다. 2016 논문은 잎 Cmass=0.5, 2018 논문은 Cm=0.4를 명시하므로 버전 사이의 탄소 변환 설정을 조용히 섞지 않는다.

Harper2016 Table2의 잎 trait과 Harper2018 Table2의 수정된 allometry는 같은 JULES 9PFT 계열의 공통 매개변수 체계이다. 2018 Section2.3은 2016 구성과 달라지는 항목을 명시한다. 아래는 모델 간 대응 후보이며 BIOME4가 공식 제공한 대응표가 아니다.

| BIOME4 PFT | JULES 기능형 대응 | LMA (kg dry leaf m^-2 leaf) | awl, 2018 (kg C m^-2) |
|---|---|---:|---:|
|4 온대 낙엽수|BDT 낙엽활엽수|0.0823|0.78|
|5 온대 상록침엽수|NET 상록침엽수|0.2263|0.65|
|6 한대 상록수|침엽 상록수로 해석할 때 NET|0.2263|0.65|
|7 한대 낙엽수|활엽 성분 BDT / 침엽 성분 NDT 두 시나리오|0.0823 / 0.1006|0.78 / 0.80|

PFT5와6은 동일 NET 매개변수를 사용한다. 따라서 네 PFT별 독립 보정 계수라고 표현하지 않는다.
BIOME4의 boreal deciduous 범주는 broadleaf와 needleleaf를 함께 포함할 수 있다(Bigelow et al. 2003, DOI 10.1029/2002JD002558, cold deciduous forest 정의). PFT7을 무조건 Larix 또는 무조건 BDT로 고정하지 않는다. 추가 구성 정보가 없다면 같은 JULES 매개변수 체계의 BDT/NDT 시나리오를 함께 계산할 수 있다. 이 두 결과는 선택한 기능형에 따른 시나리오 차이이지 통계적 신뢰구간이나 모든 실제 산림의 AGB 상하한이 아니다.

fC_wood=0.5 공통 가정에서 LAI=3일 때 산술 예시는 BDT 7.5479942189, NET 6.7631451824, NDT 7.7901017630 kg dry matter m^-2이다. 이 계산은 산술 확인이며 관측 검증이 아니다.

### 18.3 BIOME4 LAI 정의를 소스에서 확인

검사 파일: PB4Studio_v6.6.3_CHELSA21K/fortran_src/biome4_original_4_2b2.f.
ZIP SHA256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d.
- findnpp: LAI를 바꾸며 NPP가 최대인 optlai를 선택한다.
- growth: maxfvc = 1 - exp(-k * maxlai).
- hydrology: evergreen은 fvc=maxfvc, cold-deciduous는 fvc=maxfvc*dphen.
- 계절 monthlylai는 월별 fPAR에서 별도로 환산한다.
- output(2)는 dominant PFT의 optlai*100을 출력한다.
- backend는 out[1]/100을 lai_node로 읽으며, PFT별 optlai는 pftXX_raw_lai_node/mod_lai_node로 제공한다.

따라서 optlai는 연평균 계절 LAI가 아니라 phenology 적용 전의 최적 최대 canopy LAI이다. JULES Lbal과 계절 의미가 가까운 입력 후보이나, BIOME4의 생산 최적화가 JULES의 탄소수지로 결정된 상태와 동등함을 증명한 것은 아니다. 반드시 선택한 같은 PFT의 optlai를 사용한다. 여러 잠재 PFT의 LAI를 합산하지 않는다. 추가 피복률 자료가 없는 단일 PFT 계산은 해당 canopy의 면적 기준이며, 서로 다른 실제 피복률을 가진 grid-cell 평균과 자동으로 같다고 하지 않는다.

### 18.4 적용성 검증 범위와 남은 제한

Harper2018은 Carvalhais2014 및 Ruesch/Gibbs2008 자료와 vegetation carbon/biomass를 전지구 및 biome 수준에서 비교했다(Section2.4,4.2). 그러나 온대/한대 산림의 vegetation carbon 과대추정을 보고했고, allometric parameters의 추가 평가와 감소 가능성도 논의했다(Section5). 이는 원 JULES 전체 구성의 평가이며, BIOME4 optlai만 대입한 전이식의 독립 검증이 아니다.

ForC 동일 snapshot의 LAI와 biomass_ag_C를 탐색했다. 양의 값, suspicious!=1, precedence!=0, 알려진 site/plot, dominant.veg 일치, FAO Temperate/Boreal 및 대응 식생형 필터에서 84 pair rows/69 plots를 찾았다. 그러나 LAI 주석에 maximum/peak/full-leaf가 명시된 paired 행은 0이고, 날짜 미상도 포함한다. 연평균/순간값/최대값과 침엽 LAI의 면적 관례를 확인하지 않은 채 이 자료로 전이식을 검증했다고 선언하지 않는다. 이 탐색은 raw database의 LAI 관측을 가리키며 BIOME4 optlai와 동일 정의라는 뜻은 아니다. 수치 적합도나 새 계수는 산출하지 않았다.

현재 확보한 것은 **PFT 공통 체계에서 LAI로 잎+지상목질 생체량을 정적으로 진단할 수 있는 출판된 모델 구조와 명시적 변환 절차**다. 최종 채택에는 PFT7 처리, LAI 정의/단위, 공간 면적 기준, 목질 탄소분율, 용늪 또는 적합한 같은 정의의 관측 비교가 필요하다. 이 연구 확인으로 production AGB proxy를 바꾸거나 용늪 예측을 실행하지 않았다.

원문:
- https://gmd.copernicus.org/articles/9/2415/2016/
- https://gmd.copernicus.org/articles/11/2857/2018/
- https://gmd.copernicus.org/articles/14/2161/2021/
- https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010GB003917
- https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2002JD002558
- https://jules-lsm.github.io/vn4.4/namelists/pft_params.nml.html


## 19. 초본 LAI 기반 AGB 경로 확인 (2026-10-05)

**판정: 같은 JULES 계열의 generic C3/C4 grass 계수로 full-leaf living AGB 진단식을 구성할 수 있다. 모든 한랭 초본/지의류/이끼 또는 용늪 습지 초본에 대해 검증된 식이라는 뜻은 아니다.**

### 원문 정의와 공통 계수

Clark et al. (2011), DOI 10.5194/gmd-4-701-2011, Table7 및 Section5.2:
- generic C3/C4 grass의 awl=0.005 kg C m^-2.
- aws=1: 초본 stem carbon은 전부 respiring stem으로 표현된다.
- 기존 표의 bwl=1.667. Harper2018 Eq4는 5/3를 명시한다.

Harper2016 Table2의 공통 trait 체계:
- C3 grass LMA=0.0495 kg leaf dry matter m^-2 leaf.
- C4 grass LMA=0.1370 kg leaf dry matter m^-2 leaf.
Harper2018 Table2에서도 C3/C4의 awl=0.005, aws=1이다. 교목과 초본에 같은 JULES9 functional-type 체계를 사용한다. 억새 단일 종의 bioenergy 보정 계수로 자연 초본을 대체하지 않는다.

Littleton et al. (2020), JULES-BE, DOI 10.5194/gmd-13-1123-2020, Section2.2.2 Eq3-4는 위 모델 풀을 이용해 above-ground carbon을 leafC+woodC로 계산하며 rootC는 별도로 below-ground로 처리한다. 초본의 woodC 항은 지상 구조/줄기 풀로 해석하는 진단식이다. 교목 통합 woody pool에 적용한 Wolf2011의 stem:coarse-root=75:25 분리비율을 generic grass에 그대로 적용하지 않는다. 2020 논문의 AGB 보정/검증은 Miscanthus PFT에 대한 것이므로 generic grass 또는 용늪 습지 초본의 AGB 검증 근거로 확대하지 않는다.

### 유도식과 단위

full-leaf living herb AGB_dry = LMA * Lbal + awl * Lbal^(5/3) / fC_stem.
단위 kg dry matter m^-2. Lbal은 최대/잠재 LAI이다. rootC는 합산하지 않는다.
fC_stem=0.5는 명시적인 건물량 변환 가정이며 해당 2018 논문의 초본 줄기 탄소분율로 확인한 수치라고 하지 않는다. 잎 건물량은 LMA로 직접 계산해 버전별 잎 Cmass 차이와 섞지 않는다.

조건부 수치식:
C3: AGB = 0.0495*Lbal + 0.010*Lbal^(5/3).
C4: AGB = 0.1370*Lbal + 0.010*Lbal^(5/3).
LAI=3의 산술 확인: C3=0.2109025147 kg dry m^-2 (210.9025 g m^-2); C4=0.4734025147 kg dry m^-2 (473.4025 g m^-2).
이는 새 용늪 시뮬레이션 또는 현장 검증 결과가 아닌 공통 가정 아래 식 계산 예시이다. 죽은 standing biomass, litter 및 뿌리 생체량은 포함하지 않는다.

### BIOME4 대응과 하층식생의 제한

검사한 native source의 PFT8은 temperate grass, PFT9은 tropical C4 grass, PFT12는 cold herbaceous, PFT13은 lichen/forb로 표기된다. 실제 source의 photosynthetic-path 선택은 PFT9를 C4로 실행하고 PFT8은 C3로 실행한다. 이 source에서 월별 C3/C4 재선택 분기는 PFT10에만 활성화되어 있다. 주석에 C3/C4라고 쓰인 것만으로 PFT8의 실제 C4 비율을 만들어 내지 않는다. 최종 production 버전이 native source와 다른 경우 해당 코드의 pathway를 다시 확인해야 한다.

- 일반 초본의 C3/C4 기능형에는 같은 JULES generic grass 체계를 대응 후보로 사용한다.
- PFT12 cold herbaceous를 C3 grass 계수로 처리하는 것은 기능형 통합이라는 추가 가정이다. cold-herb 전용 검증 계수라고 표현하지 않는다.
- PFT13의 lichen/forb 전체에 generic grass 계수를 검증된 값처럼 적용하지 않는다. 특히 지의류/이끼를 grass의 잎+줄기 allometry로 처리할 근거는 이번 검토에서 확보하지 않았다.
- 산림 하층의 실제 초본 AGB를 요구한다면 초본 층 자체의 LAI/피복률이 필요하다. 총 canopy LAI만으로 교목과 초본의 실제 생체량을 분해하지 않는다.
- BIOME4 output(6)은 grasspft의 optlai, output(7)은 그 PFT의 optnpp이다. 이는 대안 초본 PFT의 potential output이며, 산림 밑에서 실현되는 하층 LAI/AGB라는 뜻이 아니다. 교목 potential AGB와 초본 potential AGB를 그대로 더하지 않는다.

초본 경로와 계수 존재 확인은 끝났지만, 용늪 현장 정확도와 모든 13PFT의 공통 변환은 아직 완료되지 않았다. production 코드는 변경하지 않았다.

원문:
- https://gmd.copernicus.org/articles/4/701/2011/
- https://gmd.copernicus.org/articles/9/2415/2016/
- https://gmd.copernicus.org/articles/11/2857/2018/
- https://gmd.copernicus.org/articles/13/1123/2020/


## 20. JULES 기본계수의 용늪 최종 적용 판정 (2026-10-05)

**현재 판정: Section18-19의 정적 구조 및 산술 재현은 확인했으나, 제시한 JULES 기본계수를 BIOME4-LAI 기반 용늪 최종 AGB 모형에 그대로 채택하지 않는다.** 식/계수의 존재 확인을 현장 적용 검증 완료로 표현하지 않는다. 새 production 실행이나 계수 보정은 하지 않았다.

JULES는 온대 전용이 아니라 전지구 land-surface/DGVM이다. 그렇더라도 용늪에 필요한 온대/한대의 AGB 성능은 별도로 판단해야 한다.

Harper2018 Section4.2:
- JULES-C2의 vegetation carbon high bias가 boreal/temperate forests 및 tropical savannah에서 발생한다.
- 이 지역의 수목 피복률을 과대추정하는 점을 원인으로 지적한다.
Section5:
- NPP와 Cveg가 대부분 biome에서 과대추정되므로 NPP가 너무 높을 가능성을 논의한다.
- awl/aws의 추가 평가와 하향 조정 필요 가능성도 명시한다.
따라서 vegetation carbon bias를 단독 LAI→AGB 함수의 bias와 동일시하지 않는다. 반대로, 외부 BIOME4 LAI를 대입하면 bias가 제거된다고 주장하지 않는다. 원 연구는 자체 동적 식생, LAI, NPP, coverage를 포함한 전체 구성의 평가이며, BIOME4 optlai를 대입한 진단식의 검증은 아니다.

Wolf2011은 초기 TRIFFID를 포함한 LSM의 organ allometry와 관측 산림을 비교했고 잎/줄기 배분의 상당한 불일치, 특히 낮은 생체량 산림의 문제를 보고했다. 이는 biomass allometry를 별도 검증할 필요가 있다는 근거다. 2011 연구를 2018 매개변수의 직접 검증/반증이라고 하지 않는다.

### 현재 결정

| 항목 | 상태 |
|---|---|
|같은 JULES 체계로 tree+generic grass 정적 식 구성|확인|
|기본 awl/LMA 계수의 BIOME4 optlai 전이 정확도|미검증|
|온대/한대 현장 AGB 또는 같은 LAI 정의의 독립 관측 검증|이번 전이식에는 없음|
|JULES 기본계수 그대로 용늪 최종 결과에 사용|현재 채택하지 않음|
|awl 임의 축소나 계수 변경을 통한 숫자 맞추기|수행하지 않음|
|LAI 기반 경로 자체|계속 검토 가능한 모델 구조이며 폐기 근거는 아님|

채택을 다시 판단하려면 공통 자료체계에서 정의와 면적 기준을 맞춘 LAI–living dry AGB 대조, 교목 기능형과 generic herb에 대한 성능 확인, PFT7 및 한랭 초본의 명시적 대응이 필요하다. local validation만이 유일한 길이라고 요구하는 것은 아니며, 적합한 온대/한대 독립자료도 검증 근거가 될 수 있다. 현재 미검증 상태를 모델 전체가 무가치하다는 결론으로 확대하지 않는다.

원문:
- https://gmd.copernicus.org/articles/11/2857/2018/gmd-11-2857-2018.html (Section4.2,5)
- https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010GB003917 (Section3-5, 초기 모델 비교)


## 21. 역사적 평형 생체량 모델의 존재와 AGB 출력 확인

**판정 정정:** “정적 또는 평형 생체량 모델이 없다”는 결론은 근거가 없으며 철회한다. 생체량을 계산하는 역사적 모델의 존재, 지상부와 지하부 구분, BIOME4 출력에 바로 붙일 수 있는 폐쇄식, 그 전이의 성능은 별도로 판정해야 한다. 동적 모델의 평형 운전 또는 평형식을 순수 정적 식생지리 모델과 혼동해서도 안 된다.

### 확인된 원문 근거

1. **FBM, Lüdeke et al. (1994), Kohlmaier et al. (1997):** 1997년 논문은 transient 및 steady-state 모드를 명시하며, 동일한 기본 구조를 32개 식생 유형에 적용한다. GC는 잎, 세근, 저장물질을 포함하고 RC는 줄기, 가지, 굵은뿌리를 포함한다. 따라서 평형 생체량 모델의 존재는 확인되지만 GC+RC를 AGB로 그대로 사용할 수는 없다. 식생 유형에 따라 풀 크기가 기후 및 토양 조건에 반응하므로 단순 고정 생체량 표만을 적용하는 방식과도 다르다. 출처: https://www.mkb-l.de/lit/fbm97.pdf (pp. 62–64, Table 2). 1994년 논문의 전문은 이번 확인에서 확보하지 못했으므로 그 논문의 세부 식이나 성능을 새로 검증했다고 주장하지 않는다.

2. **BIOME-BGC 4.1.1 공식 설명서:** 잎, 줄기, 세근, 굵은뿌리 생산을 분리한다. EPC line 15는 new stem C:new leaf C이며 line 17은 new coarse-root C:new stem C이다. 따라서 줄기 생산에 굵은뿌리를 합쳐야만 계산되는 구조가 아니다. 특히 livewood와 deadwood는 respiring/non-respiring 조직 구분이다. deadwood에는 살아 있는 나무의 심재, 목부, 수피 등이 포함되므로 AGB 계산에서 dead stem pool을 고사목으로 오인하여 제외하면 안 된다. CWD와 litter는 별도 풀이다. 공식 설명서 spinup은 기후 반복으로 soil C/N의 steady-state를 얻는 절차이며, 이것만으로 임의의 시점에 모든 식물 풀이 정확히 평형이라고 단정하지 않는다. 원래 모델은 일별 기상, 토양, 질소 조건을 요구하는 과정 모델이다. 출처: https://daac.ornl.gov/MODELS/guides/biome-bgc_guide.html (설명서 pp. 4, 11–12).

3. **White et al. (2000), BIOME-BGC 공통 파라미터 체계:** ENF, DBF, DNF, shrub, C3 grass, C4 grass를 동일 모델 안에서 다룬다. 별도 온대/한대 ENF 계수가 있는 것처럼 표현하면 안 된다. DNF의 일부 파라미터는 문헌 부족으로 ENF 값을 사용하며, 이는 논문 자체의 명시적 가정이다. BIOME4 PFT7에는 침엽/활엽 낙엽 성격의 선택 문제가 남아 있어 DNF 하나로 자동 매핑할 수 없다. 이 논문의 검증 중심은 NPP 민감도와 파라미터화이며, BIOME4 NPP/LAI를 투입한 AGB 외부 검증을 한 것으로 간주하지 않는다. 출처: https://journals.ametsoc.org/view/journals/eint/4/3/1087-3562_2000_004_0003_pasaot_2.0.co_2.xml ; DOI 10.1175/1087-3562(2000)004<0003:PASAOT>2.0.CO;2. 전문 페이지는 직접 열기에서 403이었으나 검색 색인의 원문 Section 2.2, Appendix A를 확인했다. 공식 파라미터 자료 DOI: 10.3334/ORNLDAAC/652.

4. **CENTURY, Parton et al. (1993), Gilmanov et al. (1997):** 초본 생체량 모델의 존재를 확인한다. 1993 연구는 11개 온대/열대 초지에서 peak live biomass 및 생산량을 관측과 비교했다. 1997 연구 초록은 구소련 8개 초지의 live/dead aboveground phytomass 모의를 명시하며 live phytomass 관측 비교 r²=0.41–0.98을 보고한다. 이는 동적 과정 모델의 검증이지 NPP+PFT만 받는 정적 식의 직접 검증은 아니다. 출처: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/93GB02042 ; https://www.sciencedirect.com/science/article/pii/S0304380096000671 ; DOI 10.1016/S0304-3800(96)00067-1.

5. **VECODE, Brovkin et al. (2002):** tree/grass 각각 green 및 structural biomass를 계산하며 NPP에 따른 allocation 및 turnover 함수를 northern Eurasia 약 500개 site 데이터로 보정했다. 그러나 structural pool에 stems+roots가 함께 포함된다. total biomass와 AGB를 동일시하지 않는다. 출처: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2001GB001662 (Section 2.3, Appendix A).

### 실용적 함의

BIOME4에 추가할 식을 찾는 방향은 “모델이 없으므로 관측 논문별 계수를 조각낸다”가 아니다. 공통 모델의 지상부/지하부 풀 구조와 파라미터를 유지한 평형 진단식을 검토해야 한다. 고정된 연간 allocation과 유효 손실률을 가정하는 단순 풀 수지에서 C*=a·NPP/λ는 대수적으로 도출되지만, 해당 단순화를 원래 BIOME-BGC 실행 또는 이미 검증된 BIOME4 변환식으로 소개해서는 안 된다. 계절 낙엽, 저장/전이 풀, 화재의 조직별 영향, stem 내부 live→dead 전이는 원래 식 확인 후 처리해야 한다.

이번 확인은 **역사적 생체량 모델과 AGB 분리 구조의 존재를 확정**한다. 새 BIOME4 최종 변환계수는 아직 제시하거나 채택하지 않았으며 production AGB 계산은 변경하지 않았다. JULES 전체 모형 편향이 있다는 이유만으로 모든 정적 생체량 진단식의 존재 또는 적용 가능성을 부정하는 논리는 사용하지 않는다.
