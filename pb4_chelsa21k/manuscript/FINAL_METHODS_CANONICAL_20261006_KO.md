# 용늪 PB4 최종 방법론 기준문서

작성일: 2026-10-06  
상태: **최종 Methods 기준문서**

이 문서는 용늪 PB4 연구의 최종 방법론, 수식, 변수 기호, 구현 범위와 검증 절차를 하나로 통일한 기준문서이다. 이후 논문 Methods, 그림 설명, 보충자료에서 같은 물리량에 다른 기호를 사용하지 않는다.

최종 검증자료는 Jang et al. (2011)만 사용한다. Park et al. (2021)은 최종 정량 검증에서 제외하며 본 연구의 배경 또는 해석 문헌으로만 사용할 수 있다.

## 1. 실행 provenance

- 기후자료: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 기간: 21.0-0.0 ka BP
- 간격: 0.1 kyr, 211 시점
- 식생모형: BIOME4 v4.2b2
- production configuration: PB4-McKenzie-nativeClimate + BIOME4-derived AGB*
- 최종 모델 버전: `6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB`
- 최종 package SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- 검증자료: Jang et al. (2011)
- 검증 항목 수: 62개 100년 output-time

## 2. 전체 계산 구조

최종 dynamic 계산 흐름은 다음과 같다.

```text
기후
-> 현재 지표고도와 토심
-> 토심에 따른 available-water storage
-> PFT별 finite-depth root accessibility
-> BIOME4
-> NPP, AET, LAI, PFT
-> EEMT와 AGB*
-> Pelletier 지형발달
-> 새로운 지표고도, 기반암고도, 토심
-> 다음 100년 시점의 BIOME4
```

static 계산에서는 초기 지표고도와 토심을 고정하고 동일한 기후시계열에 대해 BIOME4를 반복 실행한다. dynamic 계산에서는 매 100년 coupling interval 후 지표고도와 토심을 갱신하여 다음 BIOME4 계산에 다시 입력한다.

지형모형 내부에서는 수치안정성을 위해 adaptive substep을 사용할 수 있다. 그러나 하나의 100년 coupling interval 안에서는 새로운 기후시점을 읽거나 BIOME4를 다시 실행하지 않는다.

## 3. 최종 변수 표기 원칙

같은 기호를 서로 다른 물리량에 중복 사용하지 않는다.

| 기호 | 의미 | 단위 |
|---|---|---|
| (t_{BP}) | 연대 좌표 | ka BP |
| (	au) | 정방향 모델 적분시간 | kyr |
| (z) | 지표고도 | m |
| (z_b) | 기반암 또는 풍화전선 고도 | m |
| (H) | 토심 또는 레골리스 두께, (H=z-z_b) | m |
| (zeta) | 토양 프로파일 깊이 좌표 | m |
| (T_m) | 월평균기온 | degC |
| (R_m) | 월강수량 | mm month^-1 |
| (AET_m) | 월 실제증발산 | mm month^-1 |
| (W_{top},W_{bot}) | BIOME4 상층, 하층 available-water store | mm |
| (r_{30,p}) | PFT p의 상부 30 cm 누적 뿌리분율 | - |
| (X_p) | PFT p의 특성 뿌리깊이 | m |
| (D) | BIOME4에서 사용하는 유효 토심 | m |
| (R_{top,p},R_{bot,p}) | 실제 토심에서 접근 가능한 뿌리분율 | - |
| (omega_{top},omega_{bot},omega_{r,p}) | 상층, 하층, root-zone wetness | - |
| (NPP_C) | BIOME4 carbon NPP | g C m^-2 yr^-1 |
| (LAI_p) | PFT p의 BIOME4 optimal LAI | - |
| (p^*) | 해당 셀에서 선택된 dominant PFT | - |
| (L_{m,p}) | BIOME4 PFT별 expected leaf longevity | month |
| (I_{sap,p}) | AGB*에서 sapwood 항을 포함하는 indicator | 0 또는 1 |
| (AGB^*) | BIOME4-derived aboveground living biomass proxy | kg dry biomass m^-2 |
| (P_s) | 토양생산률 | m kyr^-1 |
| (P_{s,0}) | 잠재 토양생산률 | m kyr^-1 |
| (H_0) | 토양생산 특성깊이 | m |
| (kappa_d) | 토심의존 사면수송계수 | m kyr^-1 |
| (S_c) | 임계경사 | - |
| (A_c) | 기여면적 | m^2 |
| (w_c) | 유효 유로폭 | m |
| (S_f) | 유로방향 경사 | - |
| (E_{f,pot}) | 잠재 유수침식률 | m kyr^-1 |
| (E_{f,reg}) | 공급제약 후 레골리스 유수침식률 | m kyr^-1 |
| (ho_b,ho_s) | 기반암, 토양 또는 레골리스 밀도 | 동일 단위 |

다음 표기는 최종 Methods에서 사용하지 않는다.

- 토심을 (h)와 (H)로 혼용
- 기반암고도와 경험계수를 모두 (b)로 표기
- 강수와 토양생산을 모두 (P)로 표기
- soil wetness와 channel width를 모두 (w)로 표기
- 실제 AGB와 본 연구의 biomass proxy를 모두 AGB로 표기

## 4. 기후입력

CHELSA-TraCE21k/EnviCloud의 월별 Tmin, Tmax, 강수를 사용한다. 원자료 기온은 Kelvin이므로 월평균기온은

[
T_m=rac{T_{min,m}+T_{max,m}}{2}-273.15
]

로 변환한다.

CHELSA 자료에는 추가 고도감률 보정을 적용하지 않는다.

BIOME4 absolute minimum temperature는 원 BIOME4 회귀식을 사용한다.

[
T_{absmin}=0.006T_{cold}^2+1.316T_{cold}-21.9
]

CHELSA-TraCE21k Centennial 자료에 cloud 변수가 없으므로 BIOME4 광입력에 필요한 cloud만 Beyer 계열 자료에서 시간 보간한다. Beyer의 기온과 강수는 사용하지 않는다.

CO2는 PB4Studio에 포함된 Bereiter 계열 기록을 사용한다.

## 5. BIOME4

식생 코어는 BIOME4 v4.2b2로 고정한다. 최종 production에서는 BIOME4 v4.2b2의 native PFT climate limits를 유지한다.

BIOME4는 각 PFT에 대해 기후, CO2, 토양수분 조건에서 NPP와 optimal LAI를 계산하고, PFT 경쟁을 통해 dominant PFT와 biome을 판정한다.

토심에 따른 NPP 또는 LAI의 직접적인 경험 보정은 적용하지 않는다. 즉 다음과 같은 별도 multiplier는 사용하지 않는다.

[
NPPleftarrow NPP f(H)
]

[
LAIleftarrow LAI f(H)
]

토심의 식생효과는 available-water storage와 PFT별 root accessibility를 통해 BIOME4 수문과 수분스트레스에 전달된다.

## 6. 토심과 available-water storage

토심은 전 과정에서

[
oxed{H=z-z_b}
]

로 정의한다.

McKenzie et al. (2003)의 profile available water capacity 개념을 용늪 SoilGrids 수분특성에 적용한다. 깊이별 available-water density는

[
a_W(zeta)
=
1000
left[
	heta_{-10}(zeta)
-
	heta_{-1500}(zeta)
ight]
]

로 정의한다.

BIOME4의 native 2층 수문구조를 유지하여 상층과 하층 저장량을 각각

[
oxed{
W_{top}(H)
=
int_0^{min(H,0.30)}
a_W(zeta),dzeta
}
]

[
oxed{
W_{bot}(H)
=
int_{0.30}^{min[max(H,0.30),1.50]}
a_W(zeta),dzeta
}
]

로 계산한다.

전체 available-water storage는

[
W(H)=W_{top}(H)+W_{bot}(H)
]

이다.

현재 production code에 사용된 용늪 SoilGrids profile의 available-water density는 다음과 같다.

| 깊이 구간 m | available-water density mm m^-1 |
|---|---:|
| 0.00-0.05 | 237 |
| 0.05-0.15 | 232 |
| 0.15-0.30 | 218 |
| 0.30-0.60 | 207 |
| 0.60-1.00 | 198 |
| 1.00-2.00 | 179 |

BIOME4의 구조적 수문깊이 상한 때문에 실제 적분은 1.50 m까지만 사용한다.

이 식은 McKenzie의 profile AWC 개념과 BIOME4의 2층 수문구조를 결합한 본 연구의 구현식이며, McKenzie et al. (2003)의 BIOME4 확장식으로 기술하지 않는다.

## 7. PFT별 finite-depth root accessibility

BIOME4 v4.2b2의 PFT별 상부 30 cm 뿌리분율 (r_{30,p})을 McKenzie 계열 지수형 깊이감쇠와 연결한다.

특성깊이는

[
oxed{
X_p=-rac{0.30}{ln(1-r_{30,p})}
}
]

로 계산한다.

BIOME4 수문에서 실제 사용하는 유효 토심은

[
oxed{
D=min[max(H,0),1.50]
}
]

이다.

상층 접근 뿌리분율은

[
oxed{
R_{top,p}
=
1-exp
left[
-rac{min(D,0.30)}{X_p}
ight]
}
]

이고, 하층 접근 뿌리분율은

[
oxed{
R_{bot,p}
=
egin{cases}
0, & Dle0.30\
exp(-0.30/X_p)-exp(-D/X_p), & D>0.30
end{cases}
}
]

이다.

BIOME4 root-zone wetness는

[
oxed{
omega_{r,p}
=
R_{top,p}omega_{top}
+
R_{bot,p}omega_{bot}
}
]

으로 계산한다.

얕은 토양에서 (R_{top,p}+R_{bot,p}<1)이어도 두 값의 합을 1로 재정규화하지 않는다. 실제 토심 아래에 존재했을 뿌리를 얕은 층으로 인위적으로 재배치하지 않기 위한 것이다.

(r_{30,p})은 BIOME4/Jackson 계열 값이고, 지수형 깊이감쇠는 McKenzie 계열 개념이며, (X_p=-0.30/ln(1-r_{30,p}))은 두 구조를 연결하기 위한 본 연구의 분석적 변환이다.

## 8. EEMT

Pelletier et al. (2013)의 유효강수 에너지와 생물생산 에너지 개념을 사용하되, 현재 PB4에서 실제 계산되는 월별 형태로 산정한다.

[
oxed{
EEMT
=
rac{C_w}{10^6}
sum_{m=1}^{12}
T_m(R_m-AET_m)
+
rac{h_{BIO}}{10^6}
rac{max(NPP_C,0)}
{1000f_C}
}
]

사용값은

[
C_w=4186 {m J,kg^{-1},K^{-1}}
]

[
h_{BIO}=22	imes10^6 {m J,kg^{-1}}
]

[
f_C=0.50
]

이다.

(NPP_C)는 BIOME4의 탄소 기준 NPP이다. (f_C=0.50)은 carbon NPP를 dry biomass로 변환하기 위한 본 연구의 명시적 가정이다.

코드에서는 (R_m-AET_m)을 0으로 강제하지 않으며, EEMT에 별도의 1-80 MJ m^-2 yr^-1 clipping을 적용하지 않는다.

## 9. BIOME4-derived AGB*

본 연구의 지형 coupling에는 total anatomical AGB 대신 BIOME4-derived aboveground living biomass proxy인 (AGB^*)를 사용한다. (AGB^*)는 잎과 살아 있는 변재를 포함하며, BIOME4가 독립 standing stock으로 제공하지 않는 심재와 장기 목질부는 포함하지 않는다.

### 9.1 잎 건조생체량

Reich et al. (1992)의 전체 LEAVES 회귀식은

[
log_{10}(SLA)
=
2.44
-
0.43log_{10}(L_{m,p})
]

이다. (L_{m,p})의 단위는 month, SLA의 원 단위는 cm^2 g^-1이다.

m^2 kg^-1로 변환하면

[
SLA_p
=
27.542287L_{m,p}^{-0.43}
]

이므로

[
oxed{
B_{leaf,p}
=
0.0363078055
LAI_pL_{m,p}^{0.43}
}
]

가 된다.

### 9.2 변재 건조생체량

Haxeltine and Prentice (1996) Eq. (34)의 sapwood-LAI 관계는

[
C_s=LAI,C_n
]

이다.

BIOME4 v4.2b2 source code는 `stemcarbon=0.5` kg C m^-2 per LAI를 사용한다. 탄소분율 (f_C=0.50)을 적용하면 sapwood 항이 활성인 PFT의 변재 건조생체량은 (LAI_p)와 같다.

본 연구에서는 BIOME4 source의 sapwood respiration flag를 바탕으로

[
I_{sap,p}
=
egin{cases}
1, & pftpar(p,10)=1\
0, & pftpar(p,10)=2
end{cases}
]

를 정의한다.

(I_{sap,p})는 BIOME4 원 변수명이 아니라 AGB* 계산을 위한 본 연구의 indicator이다.

### 9.3 셀 단위 최종 AGB*

BIOME4 경쟁 후 해당 셀에서 선택된 dominant PFT를 (p^*)라 하면 최종 AGB*는

[
oxed{
AGB^*
=
LAI_{p^*}
left[
I_{sap,p^*}
+
0.0363078055
L_{m,p^*}^{0.43}
ight]
}
]

이다.

단위는 kg dry biomass m^-2이다.

기존 `AGB=0.010 x NPP`, Xue/IBIS, JULES 방식은 production 식으로 사용하지 않는다. Pelletier et al. (2013)의 직접적인 EEMT-to-AGB 지수식도 용늪 production에서는 사용하지 않는다.

식생모형 자체는 BIOME4 v4.2b2이다. Haxeltine and Prentice (1996)는 별도의 BIOME3 식생모형을 결합하기 위해 사용하는 것이 아니라, BIOME4에 계승된 sapwood-LAI 관계의 문헌적 원전으로 인용한다.

## 10. 토양생산과 사면수송

잠재 토양생산률은

[
oxed{
P_{s,0}
=
a_Pexp(b_P EEMT)
}
]

로 계산한다.

토심에 따른 실제 토양생산률은

[
oxed{
P_s
=
P_{s,0}
exp
left(
-rac{Hcos	heta}{H_0}
ight)
}
]

이다.

식생과 EEMT에 따른 사면수송계수는

[
oxed{
kappa_d
=
c_EEEMT+c_BAGB^*
}
]

이며 현재 production은 Pelletier et al. (2013)의 계수

[
c_E=0.033,qquad c_B=0.05
]

를 사용한다.

비선형 토심의존 사면수송은

[
oxed{
mathbf q
=
-
rac{
kappa_dHcos	heta
abla z
}{
1-(|
abla z|/S_c)^2
}
}
]

로 계산한다.

논문에서는 위와 같이 토양생산, 사면수송계수, 사면수송을 별도의 식으로 제시한다. 하나의 거대한 통합식으로 전개하여 (cos	heta), 부호 또는 계수 정의가 누락되지 않도록 한다.

## 11. 유수침식

EEMT 의존 유수침식계수는

[
K_f=rac{K_0}{EEMT}
]

이다.

유효 유로폭은

[
oxed{
w_c=g_wA_c^{i_w}
}
]

로 계산한다.

잠재 유수침식률은

[
oxed{
E_{f,pot}
=
K_f
rac{A_c}{w_c}
S_f
}
]

이다.

한 수치 step에서 레골리스 제거가 가용 토심을 초과하지 않도록

[
oxed{
E_{f,reg}
=
min
left(
E_{f,pot},
rac{H_{avail}}{Delta	au}
ight)
}
]

의 공급제약을 적용한다.

이 공급제약은 Pelletier et al. (2013)의 원 Eq. (16) 자체가 아니라 PB4의 수치적 확장으로 기술한다.

## 12. 상태변수와 coupling

기본 상태변수는

[
z,qquad z_b,qquad H=z-z_b
]

이다.

토심 질량수지의 개념적 형태는

[
oxed{
rac{partial H}{partial	au}
=
rac{ho_b}{ho_s}
rac{P_s}{cos	heta}
-

ablacdotmathbf q
-
E_{f,reg}
}
]

로 정리한다.

기반암고도는 융기와 토양생산에 따라 갱신되고, 지표고도는 기반암고도와 토심의 합으로 일관되게 계산한다. 세부 수치해석에서는 adaptive substep, face flux, positivity constraint와 경계조건을 적용한다.

논문 본문에서는 위 과정식을 중심으로 기술하고, 세부 finite-volume update와 adaptive timestep 조건은 보충자료에 둔다.

## 13. 시간축과 operator splitting

연대값과 모델 적분시간을 구분한다.

- (t_{BP}): 21.0 ka BP에서 0.0 ka BP로 감소하는 연대 좌표
- (	au): simulation 시작 이후 증가하는 정방향 적분시간

한 coupling interval은

[
Delta	au=0.1 {m kyr}
]

이다.

dynamic 계산에서 한 시점의 순서는 다음과 같다.

```text
현재 z, z_b, H
-> 해당 t_BP의 기후
-> W_top, W_bot
-> PFT별 root accessibility
-> BIOME4
-> NPP, AET, LAI, dominant PFT
-> EEMT, AGB*
-> 100년 지형발달
-> 새로운 z, z_b, H
-> 다음 t_BP
```

## 14. static과 dynamic

static 실험에서는 초기 지표고도와 토심을 고정하고 기후만 시간에 따라 변화시킨다.

dynamic 실험에서는 BIOME4 산출에서 계산한 EEMT와 AGB*가 지형발달에 입력되고, 변화한 지표고도와 토심이 다음 시점의 available-water storage와 root accessibility를 통해 BIOME4에 다시 입력된다.

따라서 dynamic은

```text
토심과 지형
-> 토양수분과 뿌리 접근성
-> 식생
-> EEMT와 AGB*
-> 지형변화
-> 새로운 토심과 지형
```

의 연속적인 양방향 coupling을 구현한다.

## 15. 검증

최종 정량 검증에는 Jang et al. (2011)의 네 record, `95_01`, `95_02`, `95_03`, `95_04`만 사용하며 총 62개 100년 output-time을 평가한다.

BIOME4의 mixed biome을 검증용 reduced class로 변환할 때는 침엽수와 활엽수 잠재 NPP의 상대비를 사용한다. 어느 한쪽이 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 분류한다. 이는 BIOME4 내부 생리계산이나 경쟁식이 아니라 검증을 위한 출력 재분류이다.

각 Jang 검증 시점에서는 관측 식생군이 모의 유역 내 유효 격자의 1% 이상에서 출현한 경우 일치한 것으로 판정한다. 1%는 검증 판정기준이며 식생모형의 파라미터나 내부 임계값이 아니다.

최종 production 결과는 static 24/62 = 38.71%, dynamic 55/62 = 88.71%이다.

Park et al. (2021)의 pollen holdout, PC2 상관, Herbs 비교는 최종 Methods와 최종 정량 검증에서 사용하지 않는다.

## 16. Methods 본문 권장 순서

실제 논문 Methods는 다음 순서로 작성한다.

1. 연구지역과 초기 지형자료
2. 기후자료와 21 ka forcing
3. BIOME4
4. 토심과 available-water storage
5. PFT별 finite-depth root accessibility
6. EEMT
7. BIOME4-derived AGB*
8. Pelletier 토양생산, 사면수송, 유수침식
9. static과 dynamic 실험설계
10. Jang et al. (2011) 검증
11. 수치구현과 시간간격

검증의 51% 재분류와 1% 출현 기준은 해당 절에서 문장으로 설명하며 별도의 수식으로 만들지 않는다.

## 17. 문서 권위순위

최종 Methods의 우선순위는 다음과 같다.

1. 이 문서 `FINAL_METHODS_CANONICAL_20261006_KO.md`
2. 최종 production package와 `results/final_integrated_20261006/FINAL_PROVENANCE.json`
3. AGB* 세부 근거 `BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md`
4. 원문 수식 확인용 `VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md`

과거 문서에 이 문서와 다른 변수명, 폐기된 AGB 식, Park 정량검증, 또는 중복 기호가 남아 있는 경우 이 문서를 따른다.

## 18. 핵심 참고문헌

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. Journal of Geophysical Research: Atmospheres, 108(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. Global Biogeochemical Cycles, 10(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. Ecological Monographs, 62(3), 365-392. https://doi.org/10.2307/2937116

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). Estimating water storage capacities in soil at catchment scales. CRC for Catchment Hydrology.

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. Journal of Geophysical Research: Earth Surface, 118, 741-758. https://doi.org/10.1002/jgrf.20046
