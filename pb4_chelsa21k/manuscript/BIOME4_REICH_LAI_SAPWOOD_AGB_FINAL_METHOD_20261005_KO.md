# BIOME4-derived AGB* method — Reich LAI + sapwood route

작성일: 2026-10-05

## 1. 최종 산정 대상

본 연구에서 지형모형에 전달하는 식생량은 **BIOME4-derived aboveground living biomass proxy** (mathrm{AGB}^*)로 정의한다.

[
mathrm{AGB}^*_{mathrm{dry}}
=
B_{mathrm{leaf,dry}}
+
B_{mathrm{sapwood,dry}}
]

이는 잎과 살아 있는 변재(sapwood)를 포함하며, 심재(heartwood), 굵은 가지 등 BIOME4가 독립 상태변수로 계산하지 않는 장기 목질부는 포함하지 않는다.

## 2. 잎 건조생체량

Reich et al. (1992), Table 1의 LEAVES 자료 회귀식:

[
log_{10}(SLA)
=
2.44
-
0.43log_{10}(mathrm{life	ext{-}span})
]

여기서 life-span은 month, (SLA)는 cm2 g-1이다.

따라서

[
SLA
=
10^{2.44}L_m^{-0.43}
]

이고, (1 mathrm{cm^2,g^{-1}}=0.1 mathrm{m^2,kg^{-1}})이므로

[
SLA
=
27.542287 L_m^{-0.43}
quad [mathrm{m^2,kg^{-1}}].
]

BIOME4의 LAI 정의와 (SLA=mathrm{leaf area}/mathrm{leaf dry mass})를 결합하면

[
oxed{
B_{mathrm{leaf,dry}}
=
0.03630780547701014,
LAI,L_m^{0.43}
}
]

단위는 kg dry biomass m-2이다.

(L_m)은 BIOME4 v4.2b2의 `pftpar(pft,7)`, 즉 expected leaf longevity in months를 사용한다.

## 3. 변재 건조생체량

Haxeltine and Prentice (1996), BIOME3 Eq. (34):

[
oxed{
C_s=LAI,C_n
}
]

여기서 (C_s)는 total sapwood carbon content이다.

BIOME4 v4.2b2 source code의 `respiration` subroutine은

`stemcarbon=0.5`

를 사용하며 이를 sapwood mass in kg C per unit leaf area per unit ground area로 정의한다. 따라서

[
C_s=0.5,LAI
quad [mathrm{kg,C,m^{-2}}].
]

건조생체량 탄소분율을 (f_C=0.50)으로 두면

[
B_{mathrm{sapwood,dry}}
=
rac{0.5LAI}{0.5}
=
LAI.
]

단, BIOME4 `pftpar(pft,10)`이 2인 PFT는 source code에서 sapwood respiration이 제거되므로 변재 항을 0으로 둔다.

계산 편의를 위해 다음 indicator를 정의한다.

[
S_p=
egin{cases}
1,& pftpar(p,10)=1\
0,& pftpar(p,10)=2
end{cases}
]

## 4. 최종식

[
oxed{
mathrm{AGB}^*_{mathrm{dry},p}
=
LAI_p
left[
S_p
+
0.03630780547701014 L_{m,p}^{0.43}
ight]
}
]

단위:

[
mathrm{kg dry biomass m^{-2}}
]

(S_p)는 본 연구가 계산용으로 정의한 indicator이며 BIOME4 원 변수명이 아니다.

## 5. BIOME4 v4.2b2 13 PFT 파라미터

| PFT | BIOME4 source-code type | (L_m) month | pftpar(10) | (S_p) | AGB*/LAI |
|---:|---|---:|---:|---:|---:|
|1|Tropical Evergreen Trees|18|1|1|1.125825|
|2|Tropical Drought-deciduous Trees|9|1|1|1.093395|
|3|Temperate Broadleaved Evergreen Trees|18|1|1|1.125825|
|4|Temperate Deciduous Trees|7|1|1|1.083829|
|5|Cool Conifer Trees|30|1|1|1.156734|
|6|Boreal Evergreen Trees|24|1|1|1.142394|
|7|Boreal Deciduous Trees|24|1|1|1.142394|
|8|C3/C4 temperate grass|8|2|0|0.088783|
|9|C4 tropical grass|10|2|0|0.097724|
|10|C3/C4 woody desert|12|1|1|1.105693|
|11|Tundra shrub|8|1|1|1.088783|
|12|Cold herbaceous|8|2|0|0.088783|
|13|Lichen/forb|8|1|1|1.088783|

PFT13은 생물학적 명칭만 보면 변재가 어색하지만, 본 계산에서는 BIOME4 v4.2b2 source code의 `pftpar(13,10)=1`을 수정하지 않고 그대로 따른다.

## 6. 21–0 ka 전체 실행

모델:
- PB4-McKenzie-nativeClimate
- baseline SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
- 새 candidate SHA-256: `1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c`
- climate: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 21.0–0.0 ka BP, 0.1 kyr interval, static/dynamic 각각 211 steps

AGB* basin mean의 시계열 평균:
- static: 3.19979 kg m-2
- dynamic: 3.11600 kg m-2

legacy (0.010	imes NPP):
- static: 4.12358 kg m-2
- dynamic: 4.00976 kg m-2

따라서 새 식은 평균적으로 legacy의 약 80% 수준이다.

0 ka:
- static AGB*: 3.48349 kg m-2
- dynamic AGB*: 3.46620 kg m-2
- legacy static: 6.14980 kg m-2
- legacy dynamic: 6.10805 kg m-2

Jang et al. (2011) corrected reduced mapping, basin 1% presence:
- static: 24/62 = 38.71%
- dynamic: 55/62 = 88.71%

즉 vegetation-class validation은 기존 canonical과 동일하며 AGB bridge 교체로 악화되지 않았다.

## 7. 실제 용늪 21 ka에서 출현한 PFT

새 candidate의 dominant PFT:
- static: PFT4, PFT6
- dynamic: PFT4, PFT6, PFT7, PFT10
- 그 외 PFT는 dominant로 출현하지 않음
- PFT0은 dynamic bare/nonvegetated cells이며 AGB*=0

## 8. 해석상 제한

이 값은 total anatomical AGB가 아니다. BIOME4가 직접 제공하거나 published BIOME3/BIOME4 lineage에서 명시적으로 연결 가능한 **foliage + sapwood**만 사용한 (mathrm{AGB}^*)이다.

따라서 원고에서는 최초 정의 시 다음과 같이 명시한다.

> BIOME4-derived aboveground living biomass proxy (AGB*), comprising foliage and sapwood.

이후 기호는 (mathrm{AGB}^*)로 통일한다.

## 9. 핵심 레퍼런스

- Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. Journal of Geophysical Research: Atmospheres, 108(D19). https://doi.org/10.1029/2002JD002559
- Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. Global Biogeochemical Cycles, 10, 693-709. https://doi.org/10.1029/96GB02344
- Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. Ecological Monographs, 62(3), 365-392. https://doi.org/10.2307/2937116
- BIOME4 v4.2b2 source code: https://github.com/jedokaplan/BIOME4

## 10. 실행 파일

- candidate package: `pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip`
- runner: `pb4_chelsa21k/tools/run_reich_lai_sapwood_agb_candidate.py`
- results: `pb4_chelsa21k/results/reich_lai_sapwood_agb_candidate_20261005/`
