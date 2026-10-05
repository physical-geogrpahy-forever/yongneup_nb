# 용늪 PB4 논문 수식 및 AGB coupling 문헌감사 작업기록

작성일: 2026-10-05

## 0. 문서 목적

이 문서는 2026-10-05까지 진행한 용늪 PB4-McKenzie-nativeClimate 논문작성용 수식 정리, Pelletier 및 McKenzie 원문 대조, BIOME4의 NPP/LAI/biomass 처리 감사, AGB coupling 대안 검토를 다음 작업자에게 정확히 인계하기 위한 기록이다.

현재 연구 범위는 대암산 용늪의 습지생태학, 고생태학, 고기후학, 생물지형학 모델링이다. 병원체, 독소, 위해성 생물학 또는 생물무기 연구와 무관하다.

가장 중요한 원칙은 다음과 같다.

1. 원문 수식, PB4 결합식, 현재 코드 구현식을 섞지 않는다.
2. 기존 결과를 새 결과처럼 보고하지 않는다.
3. AGB 변환식을 변경하면 dynamic 21-0 ka 결과를 반드시 다시 실행하고 Jang 검증을 다시 해야 한다.
4. 발표 PPT는 참고용일 뿐, 수식의 근거는 원문 논문 및 실제 코드로 확인한다.
5. BIOME4가 직접 산출하지 않는 변수를 BIOME4 원식이라고 부르지 않는다.
6. **최종 식생 코어는 BIOME4 v4.2b2이다. BIOME3는 최종 모델, 후보식, 파라미터 출처에서 제외한다.** BIOME3를 검토했던 내용은 과거 검토 이력일 뿐이며, 최종 Methods나 AGB bridge의 근거로 사용하지 않는다.

---

# 1. 현재 잠정적 최종 production baseline 및 위치

AGB coupling provenance가 아직 미해결이므로 아래 모델을 **현재 잠정적 최종 baseline**으로 고정한다. AGB bridge가 최종 확정되고 21-0 ka 재검증을 통과하면 그때 새 최종판으로 승격한다.

현재 잠정적 최종 모델은 **PB4-McKenzie-nativeClimate**이다.

## 1.1 GitHub 위치

저장소:

`physical-geogrpahy-forever/yongneup_nb`

잠정적 최종 canonical package:

`pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K.zip`

명시적 final alias:

`pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`

두 ZIP의 SHA-256:

`eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

이 baseline을 확정한 production commit:

`cfd220b2be2b9d166aa0d5e220c3dc1d9c78634a`

최종 baseline 결과 및 provenance:

`pb4_chelsa21k/results/native_climate_final_20261005/`

재구성 자료:

- `pb4_chelsa21k/payload/`
- `pb4_chelsa21k/reconstruct_pb4.py`
- `pb4_chelsa21k/SHA256SUMS.txt`

**중요:** 이후 AGB식을 변경하는 실험은 이 ZIP을 덮어쓰지 않고 별도 candidate로 실행한다. 새 candidate가 물리적 타당성과 Jang 재검증을 모두 통과하기 전까지 위 ZIP이 비교 기준이다.

## 1.2 모델 기준

- 기후: CHELSA-TraCE21k / EnviCloud, 21-0 ka BP, 100년 간격
- 기후 원자료: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- BIOME4: v4.2b2 native PFT 기후제약
- 토심-AWC: McKenzie 계열 profile water capacity coupling
- 뿌리: BIOME4/Jackson top-30-cm root fraction을 finite-depth root accessibility로 확장
- reduced-class rule: native mixed biome 6/7/9에 대해 대칭 51% 과반 판정
- 지형: Pelletier 식생-토양-지형 coupling
- 최종 ZIP:
  - `pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K.zip`
  - `pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`
- SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

최종 21-0 ka 새 실행, Jang et al. (2011) 원문 식생대, n=62, 유역 1% 출현기준:

- static: 24/62 = 38.709677%
- dynamic: 55/62 = 88.709677%
- dynamic 95_03: 31/31
- dynamic 95_03 broadleaf fraction: 약 1.3423-3.3557%

이 결과는 현재 AGB proxy를 포함한 production 결과이며, AGB coupling을 변경하면 다시 실행해야 한다.

---

# 2. 논문용 HWP 수식 정리 현황

기존 정리본:

- `pb4_chelsa21k/manuscript/VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md`
- `pb4_chelsa21k/manuscript/VESLEM_PB4_HWP_EQUATION_INPUT.txt`

정리 방식:

- Pelletier et al. (2013) 원문 Eq. (1)-(22)를 원문 번호 그대로 유지
- 각 식에 HWP 수식편집기 입력형식을 병기
- Pelletier 원식과 PB4 구현 확장을 구분
- McKenzie (2003)의 profile AWC 및 root scaling 원식과 PB4/BIOME4 결합식을 구분
- PPT에 적힌 식은 현재 실제 코드와 차이가 있는지 반드시 코드로 검증

## 2.1 Pelletier 핵심식

현재 PB4와 직접 연결되는 핵심 원식:

[
E_{PPT}=\Delta T C_w P_{eff}
]

[
E_{BIO}=NPP h_{BIO}
]

[
z=b+h
]

[
\frac{\partial b}{\partial t}=U-\frac{P}{\cos\theta}
]

[
\frac{\partial h}{\partial t}
=\frac{\rho_b}{\rho_s}\frac{P}{\cos\theta}-E
]

[
P=P_0\exp\left(-\frac{h\cos\theta}{h_0}\right)
]

[
P_0=a\exp(bEEMT)
]

[
\mathbf q=
-\frac{k_d h\cos\theta\nabla z}
{1-(|\nabla z|/S_c)^2}
]

[
k_d=cEEMT+dAGB
]

[
E_f=K\frac{A}{w}|\nabla z|
]

[
w=gA^i
]

[
K=\frac{K_0}{EEMT}
]

현재 PB4는 이 구조를 유지하면서 finite regolith supply constraint, adaptive timestep, fixed/open boundary, flow-direction slope 등의 수치구현 확장을 사용한다.

## 2.2 EEMT 구현 차이

Pelletier의 개념은 effective precipitation energy + biological production energy이다.

현재 PB4는 BIOME4 NPP가 탄소질량이므로 dry biomass로 변환하여 생물생산 에너지를 계산한다.

[
EEMT=
\frac{C_w}{10^6}\sum_{m=1}^{12}T_m(P_m-AET_m)
+
\frac{h_{BIO}}{10^6}
\frac{\max(NPP_C,0)}{1000f_C}
]

현재 코드의 (f_C=0.50)은 별도 문헌 또는 모델 가정의 출처를 최종 논문에서 명시해야 한다.

---

# 3. McKenzie 원문 및 PB4 결합식

McKenzie, Gallant, & Gregory (2003), *Estimating Water Storage Capacities in Soil at Catchment Scales*는 학술지 논문이 아니라 CRC for Catchment Hydrology Technical Report 03/3이다.

원문에서 확인한 핵심:

## 3.1 profile available water capacity

[
AWC_{profile}(H)
=
1000\int_0^H
[\theta_{-10}(\xi)-\theta_{-1500}(\xi)]d\xi
]

PB4는 이를 BIOME4 native 수문층에 맞춰 0-0.30 m와 0.30-1.50 m로 분할한다.

## 3.2 root-depth scaling

McKenzie 원식:

[
f(x)=\exp(-x/X_i)
]

A horizon:

[
A_{Total}
=
AAWC X_i(1-e^{-d_A/X_i})
]

B horizon:

[
B_{Total}
=
BAWC X_i(e^{-d_A/X_i}-e^{-d_i/X_i})
]

PB4는 BIOME4/Jackson의 상부 30 cm 누적 뿌리분율 (r_{30,p})을 이용해

[
X_p=-\frac{0.30}{\ln(1-r_{30,p})}
]

로 특성깊이를 역산한다. 이 식은 McKenzie 원문식이 아니라 McKenzie 지수분포와 BIOME4 root fraction을 연결한 PB4 분석적 결합식이다.

---

# 4. AGB coupling 문제의 발견

현재 PB4는 BIOME4가 standing AGB를 직접 prognose하지 않기 때문에 다음 proxy를 사용한다.

[
AGB=s_{AGB}\max(NPP_C,0)
]

현재:

[
s_{AGB}=0.010
]

이 식은 Pelletier et al. (2013)의 원식이 아니다.

Pelletier 원문은 현장 AGB와 EEMT 관계로

[
AGB=e\exp(fEEMT)
]

을 사용한다.

따라서 현재 production의 `AGB=0.010 NPP`는 독립적인 coupling bridge이며, 논문 제출 전에 provenance를 해결해야 한다.

AGB가 (k_d=cEEMT+dAGB)에 직접 들어가므로 AGB 식을 바꾸면 dynamic 지형진화, 토심, AWC, BIOME4 식생이 연쇄적으로 바뀔 수 있다. static 식생은 AGB의 지형 feedback이 없으므로 영향이 훨씬 제한적일 것으로 예상되지만, 최종 판정은 새 실행으로 확인해야 한다.

---

# 5. Xue et al. (2017) 검토

Xue et al. (2017)은 woody biomass residence time과 DGVM biomass pool 식을 직접 제공한다.

핵심 관계:

[
\tau_w=\frac{M_w}{W_p}
]

즉,

[
M_w=W_p\tau_w
]

또한 DGVM biomass pool을

[
\frac{\partial C_{i,j}}{\partial t}
=
a_{i,j}NPP_i
-
\frac{C_{i,j}}{\tau_{i,j}}
]

로 나타낸다.

정상상태에서는

[
C_{i,j}=a_{i,j}\tau_{i,j}NPP_i
]

가 된다.

Xue meta-analysis의 woody residence time:

- warm temperate broadleaf: 104.1 yr
- warm temperate conifer: 72.0 yr
- temperate broadleaf: 82.9 yr
- temperate conifer: 74.7 yr
- boreal broadleaf: 55.5 yr
- boreal conifer: 80.9 yr

BIOME4 PFT4-7의 잠정 대응:

- PFT4 Temperate deciduous -> temperate broadleaf -> 82.9 yr
- PFT5 Cool conifer -> temperate conifer -> 74.7 yr
- PFT6 Boreal evergreen -> boreal conifer -> 80.9 yr
- PFT7 Boreal deciduous -> boreal broadleaf -> 55.5 yr

중요: Xue 본문은 (a_{i,j}), 즉 PFT별 NPP allocation fraction의 수치표를 제공하지 않는다. Xue만으로 (AGB=a\tau NPP) 전체를 완성할 수 없다.

---

# 6. Malhi et al. (2017) 검토

Malhi et al.은 NPP 중 aboveground coarse woody production으로 가는 비율과 woody residence time을 이용한다.

[
NPP_{ACW}
=
NPP\frac{NPP_{ACW}}{NPP}
]

성숙림 equilibrium에서

[
AGB
=
GPP
\frac{NPP}{GPP}
\frac{NPP_{ACW}}{NPP}
\tau_w
]

따라서

[
AGB=NPP f_{wood}\tau_w
]

구조가 직접 성립한다.

Malhi의 자료에서는 wood allocation이 지역별로 변하며 전체 평균이 대략 0.29 수준이다.

하지만 열대 산지림 자료이므로 용늪의 temperate/boreal BIOME4 PFT4-7에 0.29를 일괄 적용하는 것은 최종 논문용으로는 약하다.

---

# 7. Sitch et al. (2003), LPJ allocation 검토

Sitch et al.은 고정 (a_{wood})를 주는 방식이 아니라 NPP를 leaf, fine root, sapwood로 동적으로 배분한다.

주요 allometric constraints:

[
LA=k_{la:sa}SA
]

[
C_{leaf}=l_{r,max}\omega C_{root}
]

[
H=k_{allom2}D^{k_{allom3}}
]

[
CA=k_{allom1}D^{k_{rp}}
]

연간 biomass increment:

[
\Delta C
=
\Delta C_{leaf}
+
\Delta C_{sapwood}
+
\Delta C_{root}
]

LPJ는 이 조건을 동시에 만족하도록 annual allocation을 수치적으로 계산한다.

따라서 Sitch + Xue를 결합하면

[
NPP
\rightarrow
\Delta C_{sapwood}
\rightarrow
AGB_C=\tau_w\Delta C_{sapwood}
]

로 만들 수 있다.

그러나 이는 BIOME4에 LPJ식 carbon-pool state를 새로 도입하는 것이므로, 현재 equilibrium BIOME4의 철학과 구현을 크게 변경한다. 그래서 BIOME4 자체에서 더 직접적인 biomass bridge가 있는지 우선 확인하기로 했다.

---

# 8. BIOME3 검토 이력 — 최종 모델에서는 폐기

BIOME3 원문은 BIOME4의 계보를 확인하는 과정에서 일시적으로 검토하였다. 그러나 본 연구의 식생 코어는 **BIOME4 v4.2b2**이며, 사용자는 BIOME3를 최종 방법론에서 제외하기로 결정했다.

따라서 앞으로의 원칙은 다음과 같다.

- BIOME3의 biomass 식 또는 파라미터를 PB4 AGB bridge에 사용하지 않는다.
- BIOME3의 (C_s=LAI C_n), (C_n=1.0) 값은 최종 모델의 근거가 아니다.
- BIOME3와 BIOME4의 파라미터 차이를 맞추거나 보정하려고 하지 않는다.
- 최종 Methods의 식생모델 설명과 AGB 해결은 **BIOME4 v4.2b2 원 코드와 BIOME4 관련 문헌만**을 기준으로 한다.
- 이 절은 과거 검토가 있었음을 남기는 감사기록일 뿐이다.

---

# 9. BIOME4 v4.2b2 실제 소스 재검토

Jed Kaplan의 공개 BIOME4 v4.2b2 `biome4.f`를 직접 확인했다.

BIOME4는 각 PFT에 대해 `findnpp`에서 LAI를 반복 탐색하고, `growth`를 호출하여 최적 NPP와 최적 LAI를 결정한다.

최종적으로:

- `output(300+pft)=optnpp(pft)`
- `output(300+numofpfts+pft)=optlai(pft)`

를 출력한다.

## 9.1 respiration()의 biomass-related constants

원본 BIOME4 v4.2b2:

```fortran
parameter(Ln=50.,y=0.8,m10=1.6,p1=0.25,stemcarbon=0.5)
```

주석에서 `stemcarbon`은

> sapwood mass as KgC.m-2(leaf area).m-2(ground area)

로 정의되어 있다.

stem respiration은

```fortran
mstemresp(m)=lai*stemcarbon*respfact(pft)*...
```

이므로 BIOME4 내부에서 sapwood carbon은 사실상

[
C_{sap}=0.5\,LAI
quad [kg\;C\;m^{-2}]
]

으로 진단된다.

이 값은 BIOME3 Haxeltine & Prentice (1996)의 (C_n=1.0)보다 절반이다.

**아직 해결되지 않은 핵심 질문:** BIOME4에서 왜 (C_n) 상당값이 1.0에서 0.5로 변경되었는지, Kaplan/BIOME4 문헌에서 그 변경 근거를 찾아야 한다.

## 9.2 BIOME4 leaf allocation/litterfall

BIOME4는

```fortran
litterfall=lai*Ln*allocfact(pft)
```

를 사용한다.

PFT4-7에서 `allocfact=1.2`이므로

[
L_f=60\,LAI
quad [g\;C\;m^{-2}\;yr^{-1}]
]

이다.

최소 allocation requirement:

[
NPP\ge L_f
]

을 만족하지 못하면 해당 LAI는 지속 불가능한 것으로 처리한다.

## 9.3 PFT4-7 leaf longevity

`pftdata()`의 expected leaf longevity, months:

- PFT4 Temperate Deciduous Trees: 7 months
- PFT5 Cool Conifer Trees: 30 months
- PFT6 Boreal Evergreen Trees: 24 months
- PFT7 Boreal Deciduous Trees: 24 months

그러나 이 leaf longevity를 (L_f)에 곱해 standing leaf C를 계산하는 것은 BIOME4가 직접 출력하는 pool이 아니므로 별도 유도식으로 명시해야 한다.

---

# 10. BIOME4-native biomass bridge의 현재 판정

현재 가장 직접적으로 **BIOME4 v4.2b2 코드 자체에 근거하는 값**은 sapwood carbon이다.

BIOME4 v4.2b2:

[
C_{sap}=0.5\,LAI
]

따라서 BIOME4-native bridge 후보는

[
B_{sap,dry}
=
\frac{0.5\,LAI}{f_C}
]

이다.

예를 들어 (f_C=0.5)를 가정하면

[
B_{sap,dry}=LAI
]

가 된다.

LAI=5이면:

- sapwood carbon = 2.5 kg C m(^{-2})
- sapwood dry biomass = 5 kg m(^{-2}), (f_C=0.5) 가정

이 값은 기존 proxy (AGB=0.010NPP)에서 NPP=500 g C m(^{-2}) yr(^{-1})일 때의 5 kg m(^{-2})와 우연히 동일하지만, 두 식의 물리적 의미는 다르다.

중요: **sapwood biomass는 total AGB와 동일하지 않다.** Pelletier의 AGB는 aboveground live dry biomass에 해당하므로 leaf, branches, heartwood 등의 포함범위를 반드시 대조해야 한다.

따라서 현재 시점에는 다음 표현만 확정 가능하다.

> BIOME4는 total AGB를 직접 prognose하지 않지만 equilibrium LAI와 sapwood maintenance respiration의 구조에서 sapwood carbon을 (C_{sap}=0.5LAI)로 진단할 수 있다.

다음 표현은 아직 금지한다.

> “BIOME4에서 AGB는 (0.5LAI)로 계산된다.”

이는 total AGB가 아니라 sapwood C이므로 틀린 표현이다.

---

# 11. 현재 AGB 대안 후보 비교

| 방법 | 식 | 장점 | 문제 |
|---|---|---|---|
| 현 production | (AGB=0.010NPP) | 구현 단순, 기존 88.71% 결과 보존 | 계수 provenance 미해결 |
| Pelletier Eq.5 | (AGB=e\exp(fEEMT)) | Pelletier 원문과 직접 일치 | 용늪/BIOME4에 그대로 적용할 타당성 검토 필요 |
| Xue + fixed allocation | (AGB=a_{wood}\tau_wNPP) | residence time 관측 기반 | (a_{wood}) 별도 출처 필요 |
| Sitch + Xue | LPJ allocation -> woody production -> (	au_w) | 과정 기반 | BIOME4에 LPJ carbon-pool 모듈을 새로 붙이는 큰 변경 |
| BIOME4 sapwood | (C_{sap}=0.5LAI) | BIOME4 실제 코드에 직접 존재 | total AGB가 아님 |
| BIOME4 sapwood + total-wood conversion | (AGB\propto C_{sap}/f_{sap}) | BIOME4 structure 유지 | (f_{sap}) 외부 문헌 필요 |

현재 우선순위는 **BIOME4 문헌에서 total AGB 또는 vegetation carbon/biomass를 직접 진단한 선행연구가 있는지 확인하는 것**이다. 이 검토가 끝나기 전 production AGB bridge를 교체하지 않는다.

---

# 12. 다음 작업: 반드시 이어서 확인할 항목

## A. BIOME4 문헌의 AGB/biomass 사용 여부

다음 키워드로 BIOME4 및 BIOME3/4 파생 연구를 철저히 확인한다.

- BIOME4 aboveground biomass
- BIOME4 vegetation carbon
- BIOME4 biomass carbon
- BIOME4 LAI biomass
- BIOME4 sapwood carbon
- BIOME4 carbon stocks
- Kaplan BIOME4 biomass
- BIOME4 NPP biomass conversion
- BIOME4 equilibrium biomass

목표:

1. BIOME4를 사용해 AGB 또는 vegetation carbon을 실제 추정한 논문 확인
2. total AGB 계산식이 있으면 원문식과 파라미터 추출
3. sapwood-only 진단인지 total vegetation carbon인지 구분
4. BIOME4 v4.2b2의 `stemcarbon=0.5` 자체의 BIOME4 문헌적 근거 추적

## B. carbon fraction (f_C)

현재 EEMT 및 dry-biomass conversion에 (f_C=0.5)가 사용된다.

논문용으로 다음을 확보해야 한다.

- IPCC 또는 식물 biomass carbon fraction의 표준 문헌
- 가능하면 temperate/boreal woody vegetation에 맞는 값
- dry biomass와 carbon mass의 단위관계 명시

## C. production AGB ablation

새 AGB식을 채택하기 전에 최소 다음 2개를 비교한다.

Control:

[
AGB=0.010NPP
]

Candidate:

[
AGB=F(LAI,NPP,PFT)
]

동일 조건:

- CHELSA-TraCE21k/EnviCloud 21-0 ka
- PB4-McKenzie-nativeClimate
- native BIOME4 PFT climate limits
- 동일 McKenzie/Jackson soil-root coupling
- 동일 51% reduced-class rule
- 동일 Pelletier 지형 파라미터
- 동일 initial DEM, soil depth, boundary
- Jang n=62, 1% basin-presence criterion

반드시 비교할 출력:

- static Jang accuracy
- dynamic Jang accuracy
- 95_03 broadleaf fraction
- mean/min/max soil depth
- shallow-soil pockets
- EEMT
- AGB
- (k_d)
- hillslope flux
- final elevation
- AWC
- PFT4-7 NPP and LAI

기존 55/62 = 88.71%는 새 AGB식의 결과로 재사용하면 안 된다.

---

# 13. 이미 확인한 중요한 수치와 코드 사실

## 13.1 기존 dynamic 핵심 진단

3 ka 부근 McKenzie dynamic의 얕은 토양셀 예:

- H ≈ 0.04545 m
- WHC ≈ 10.77 mm
- PFT4 NPP ≈ 344.35
- PFT6 NPP ≈ 284.37
- PFT7 NPP ≈ 389.47
- native biome = 4 Temperate deciduous forest

이와 같은 ultra-shallow pocket이 95_03 broadleaf 1% 출현을 유지하는 핵심 기작으로 확인되었다.

따라서 AGB가 (k_d)를 바꾸면 얕은 토양포켓 자체가 바뀔 수 있고, 최종 검증도 달라질 수 있다.

## 13.2 BIOME4 출력 계측

원본 BIOME4 v4.2b2는 현재 계측된 소스에서 PFT별:

- optimal NPP
- optimal LAI

를 모두 출력할 수 있다.

따라서 다음 실험에서는 별도 LPJ를 붙이지 않고도 21-0 ka 전체 PFT별 LAI를 추출하여

[
0.010NPP
]

와

[
\frac{0.5LAI}{f_C}
]

를 먼저 **지형을 다시 돌리지 않고 진단 비교**할 수 있다. 이 비교 후 full dynamic ablation으로 넘어가는 것이 효율적이다.

---

# 14. 논문 Methods에 현재 쓸 수 있는 문장과 아직 쓰면 안 되는 문장

## 현재 써도 되는 내용

- BIOME4는 각 PFT에 대해 NPP를 최대화하는 equilibrium LAI를 탐색한다.
- BIOME4 v4.2b2의 respiration routine은 sapwood carbon에 비례하는 stem maintenance respiration을 사용한다.
- 현재 source constant는 `stemcarbon=0.5` kg C m(^{-2}) LAI(^{-1})이다.
- McKenzie AWC와 root-depth scaling은 BIOME4 native 2-layer hydrology와 결합되었다.
- Pelletier 사면수송계수는 (k_d=cEEMT+dAGB) 구조를 사용한다.
- 현재 production AGB는 `0.010 NPP` proxy이며 provenance 재검토 중이다.

## 아직 쓰면 안 되는 내용

- “BIOME4가 total AGB를 계산한다.”
- “BIOME4의 AGB는 (0.5LAI)이다.”
- “Xue가 BIOME4 PFT별 wood allocation fraction을 제공한다.”
- “Sitch의 LPJ allocation은 현재 PB4에 구현되었다.”
- “새 AGB식을 적용해도 88.71%가 유지된다.”
- “Pelletier Eq.5가 현재 PB4에 구현되어 있다.”

---

# 15. 핵심 참고문헌

## Pelletier

Pelletier, J. D., et al. (2013). *Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona.* Journal of Geophysical Research: Earth Surface, 118, 741-758. DOI: 10.1002/jgrf.20046.

## McKenzie

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating Water Storage Capacities in Soil at Catchment Scales.* CRC for Catchment Hydrology Technical Report 03/3.

## BIOME3 — 검토 후 최종 모델 근거에서 제외

Haxeltine, A., & Prentice, I. C. (1996). *BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types.* Global Biogeochemical Cycles, 10(4), 693-709. DOI: 10.1029/96GB02344.

이 문헌은 계보 확인 과정의 감사기록으로만 남기며, 최종 PB4의 AGB 식, 파라미터, 식생코어 근거로 사용하지 않는다.

## LPJ

Sitch, S., et al. (2003). *Evaluation of ecosystem dynamics, plant geography and terrestrial carbon cycling in the LPJ dynamic global vegetation model.* Global Change Biology, 9, 161-185. DOI: 10.1046/j.1365-2486.2003.00569.x.

## Xue

Xue et al. (2017). Global Biogeochemical Cycles. DOI: 10.1002/2016GB005557.

## Malhi

Malhi et al. (2017). New Phytologist. DOI: 10.1111/nph.14189.

---

# 16. 작업상 최종 판정

현재 production을 바로 수정하지 않는다.

현재까지 가장 중요한 발견은 다음과 같다.

1. 기존 `AGB=0.010NPP`는 Pelletier 원식이 아니며 provenance가 약하다.
2. Xue는 woody residence time을 강하게 지지하지만 allocation fraction을 직접 완성해주지 않는다.
3. Sitch는 allocation을 해결하지만 LPJ 구조를 BIOME4에 새로 이식하는 큰 변경이다.
4. BIOME3는 최종 모델과 AGB 해결 경로에서 폐기한다.
5. BIOME4 v4.2b2 source는 사실상 (C_{sap}=0.5LAI)의 sapwood-carbon 구조를 사용한다.
6. 그러나 sapwood carbon은 total AGB가 아니다.
7. 따라서 다음 최우선 과제는 **BIOME4 문헌에서 total AGB/vegetation carbon을 계산한 사례를 찾고, BIOME4의 `stemcarbon=0.5` 근거를 추적하는 것**이다.
8. 그 뒤 BIOME4 기반 후보 AGB bridge를 정하고, full 21-0 ka dynamic ablation을 새로 실행해야 한다.

이 문서는 이 지점의 인계 기준이다.


# 17. Pelletier Eq. (5) AGB 원식 후보 실험 — 완료 및 기각

현재 잠정적 최종 baseline은 변경하지 않고 별도 candidate로 AGB bridge만 교체하여 21-0 ka 전체를 새로 실행한다.

Baseline:

[
AGB=0.010max(NPP_C,0)
]

Candidate:

[
AGB=eexp(fEEMT)
]

Pelletier et al. (2013)의 원식 및 원 계수:

[
e=1 {m kg,m^{-2}},qquad
f=0.1 {m yr,m^2,MJ^{-1}}
]

따라서 candidate 구현은

[
AGB=exp(0.1EEMT)
]

이다.

## 17.1 고정 조건

AGB bridge 이외에는 잠정적 최종 production baseline을 유지한다.

- CHELSA-TraCE21k/EnviCloud 21-0 ka BP, 100년 간격
- BIOME4 v4.2b2 native climate limits
- McKenzie AWC
- finite-depth PFT root accessibility
- 51% reduced-class majority rule
- 기존 EEMT 계산
- 기존 Pelletier (c,d,K_0) 및 지형수식
- Jang et al. (2011) corrected mapping, n=62, basin presence >=1%

## 17.2 Wang 비교

Wang et al. (2011)의

[
C_{mathrm{veg}}=NPP	au_{mathrm{veg}}
]

는 **독립 진단값으로만 계산**하며 지형 forcing에는 사용하지 않는다.

현재 forest mega-biome mapping:

- BIOME4 biome 4, warm-temperate forest: (	au=15) yr
- BIOME4 biome 5-8, temperate forest: (	au=10) yr
- BIOME4 biome 9-11, boreal forest: (	au=26) yr

Pelletier AGB는 live dry biomass, Wang (C_{mathrm{veg}})는 carbon mass이므로 둘을 동일 변수로 간주하지 않고 별도 단위로 기록한다. 탄소분율을 임의 적용해 맞추지 않는다.

## 17.3 GitHub 구현 및 실행 위치

실행 스크립트:

`pb4_chelsa21k/tools/run_pelletier_agb_candidate.py`

Workflow:

`.github/workflows/pb4-chelsa21k-pelletier-agb-candidate.yml`

결과 예정 위치:

`pb4_chelsa21k/results/pelletier_agb_candidate_20261005/`

GitHub Actions run:

`37261891795`

새 21-0 ka 전체 실행 결과를 복구해 확인했다.

- 성공 실행: GitHub Actions run `37261755927`, job `111610259666`
- 모델 실행 자체는 성공
- 마지막 원격 push만 non-fast-forward 충돌로 실패했으며, Actions 로그의 실제 출력값을 복구해 원격 저장소에 기록함
- recovered 결과:
  - `pb4_chelsa21k/results/pelletier_agb_candidate_20261005/PELLETIER_AGB_EQ5_JANG1PCT_SUMMARY_RECOVERED.csv`
  - `pb4_chelsa21k/results/pelletier_agb_candidate_20261005/PELLETIER_AGB_EQ5_VS_WANG_SUMMARY_RECOVERED.csv`
  - `pb4_chelsa21k/results/pelletier_agb_candidate_20261005/PELLETIER_AGB_EQ5_RUN_RECOVERED_KO.md`

예정 핵심 출력:

- `PELLETIER_AGB_JANG1PCT_SUMMARY.csv`
- `PELLETIER_AGB_JANG1PCT_BY_ZONE.csv`
- `PELLETIER_AGB_static_JANG1PCT_ROWS.csv`
- `PELLETIER_AGB_dynamic_JANG1PCT_ROWS.csv`
- `PELLETIER_AGB_WANG_TIMESERIES_DIAGNOSTIC.csv`
- `PELLETIER_AGB_WANG_TIMESERIES_COMPACT.csv`
- `PELLETIER_AGB_PROVENANCE.json`
- `PELLETIER_AGB_CANDIDATE.patch`
- `PELLETIER_AGB_21KA_RUN.log`

## 17.4 새 실행 결과

Jang 1% 검증:

- static: 24/62 = 38.709677%
- dynamic: 54/62 = 87.096774%

즉 static은 baseline과 동일하지만 dynamic은 baseline 55/62 = 88.709677%보다 1개 시점 낮아졌다.

Pelletier Eq. (5) AGB 규모:

- static, 211시점 유역평균의 시간평균: 3414.11 kg m^-2
- static, 시간별 유역평균 범위: 172.94-12836.98 kg m^-2
- static, 전체 셀 절대최대: 13567.40 kg m^-2
- dynamic, 211시점 유역평균의 시간평균: 3487.47 kg m^-2
- dynamic, 시간별 유역평균 범위: 153.43-13007.80 kg m^-2
- dynamic, 전체 셀 절대최대: 23991.11 kg m^-2

Wang et al. (2011) 독립 BIOME4 vegetation-carbon 진단:

- static, 시간별 유역평균의 평균: 4.142 kg C m^-2
- static 범위: 2.655-6.266 kg C m^-2
- dynamic, 시간별 유역평균의 평균: 3.780 kg C m^-2
- dynamic 범위: 2.372-6.171 kg C m^-2

공간비교 진단:

- static, 211시점 평균 cellwise Pearson r = 0.7200
- dynamic, 211시점 평균 cellwise Pearson r = -0.9054
- dynamic 범위 = -0.9979에서 0.9998

이 결과는 단순한 절대규모 문제뿐 아니라, dynamic McKenzie 토심-수문 feedback이 작동할 때 Pelletier Eq. (5)의 EEMT 기반 AGB 공간패턴이 BIOME4 NPP 기반 Wang vegetation-carbon 패턴과 대체로 반대로 움직였음을 보여준다. 따라서 Eq. (5) 원 계수의 무보정 적용을 더 강하게 기각한다.

단위와 정의가 다르므로 Pelletier AGB와 Wang Cveg를 직접 같은 값으로 보지는 않는다. 다만 Pelletier Eq. (5)의 Arizona 계수를 현재 PB4 EEMT에 무보정 적용하면 용늪에서 AGB가 수백에서 수만 kg m^-2까지 폭증하므로 물리적으로 사용할 수 없다.

## 17.5 판정

**Pelletier Eq. (5) 원 계수의 용늪 무보정 이식은 기각한다.**

이유:

1. AGB 크기가 비현실적이다.
2. Wang BIOME4 vegetation-carbon 진단과 규모가 극단적으로 다르다.
3. Jang dynamic 검증도 88.71%에서 87.10%로 소폭 악화된다.
4. Pelletier의 (e,f)를 용늪에 맞춰 다시 적합하면 결국 지역 경험보정이 되므로 현재 목표인 누더기 없는 모델과 맞지 않는다.

따라서 기존 canonical baseline은 유지한다. 다음 해결은 BIOME4 자체의 biomass/carbon 체계에서 하나의 일관된 식생상태변수를 정의할 수 있는지 문헌적으로 확인한 뒤 진행한다.


# 18. 용늪 현지 AGB 검증/보정 자료 후보

Pelletier Eq. (5) 원 계수의 무보정 이식이 물리적으로 기각된 뒤, 누더기식 추가 모듈을 피하기 위한 가장 깔끔한 다음 자료원으로 **대한민국 전국 30 m 산림 AGB 지도**를 확인했다.

자료:

Kim, Seunguk, Shin, Joong Hoon, Han, Hee, & Choe, Hyeyeong (2026).
*Nationwide 30 m maps of forest composition, biomass, and diversity in South Korea (2021–2025) from direct prediction and plot-index imputation.*
Zenodo. DOI: 10.5281/zenodo.21701424.

핵심 특성:

- 제8차 국가산림자원조사(2021-2025) 기반
- Sentinel-2, 기후, 지형 예측자 사용
- 대한민국 전국 30 m 해상도
- CRS EPSG:5179
- aboveground biomass 직접 예측 지도 제공
- direct-prediction AGB와 cell-level uncertainty 지도 제공
- forest-type map을 추가한 FTM 버전도 제공
- spatial-block cross-validation 및 별도 공간독립 test set 사용

주요 파일:

- `base_biomass_30m.tif`
- `base_biomass_sd_30m.tif`
- `ftm_biomass_30m.tif`
- `ftm_biomass_sd_30m.tif`

이 자료는 BIOME4 또는 Pelletier에 다른 DGVM을 붙이지 않고, **현재 용늪 및 주변 산림의 실제 AGB 규모를 독립적으로 검증하는 자료**로 사용할 수 있다.

잠정적으로 가장 일관된 다음 전략:

1. 현재 canonical baseline은 그대로 보존
2. 용늪 20 m 모델영역과 이 30 m AGB 지도를 EPSG:5179에서 정합
3. 산림셀만 추출하여 현대 AGB의 평균, 범위, 공간패턴, 불확실성 확인
4. baseline `0.010NPP`, Pelletier Eq. (5), Wang (C_{veg})와 현대시점 규모 비교
5. Pelletier Eq. (5)의 형태를 유지할 경우, Arizona의 (e,f)를 그대로 쓰지 않고 **독립적인 한국 AGB 관측자료를 이용한 지역 검증 또는 보정 가능성**을 평가

아직 이 자료로 (e,f)를 적합하지 않았으며, 적합 여부도 확정하지 않았다. 데이터 확인 전 임의 보정은 금지한다.
