# 용늪 PB4 최종 방법론 기준문서

작성일: 2026-10-06  
상태: **최종 Methods 기준문서, 원식 대조 완료**

이 문서는 용늪 PB4 연구의 논문 Methods에서 사용할 수식, 변수, 구현식과 검증 절차를 통일한 기준문서이다.

핵심 원칙은 다음과 같다.

- 출판문헌에서 가져온 수식은 가능한 한 원식과 원 기호를 그대로 제시한다.
- 본 연구에서 문헌들을 연결하여 새로 만든 식은 반드시 "본 연구 구현식"으로 구분한다.
- 단순한 대수 전개나 단위변환으로 생긴 소수계수를 독립 파라미터처럼 제시하지 않는다.
- 코드의 수치안정화 장치와 물리적 또는 생태적 파라미터를 구분한다.
- 최종 정량 검증은 Jang et al. (2011)만 사용한다.

## 1. 실행 provenance

- 기후자료: \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`
- 기간: 21.0-0.0 ka BP
- 간격: 0.1 kyr, 총 211 시점
- 식생모형: BIOME4 v4.2b2
- production configuration: PB4-McKenzie-nativeClimate + BIOME4-derived AGB*
- 모델 버전: \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`
- 최종 package SHA-256: \`796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86\`
- 검증자료: Jang et al. (2011)
- 검증 표본: 62개 100년 output-time

## 2. 표기 원칙과 원문 기호의 대응

논문 전체에서 상태변수는 다음처럼 통일한다.

| 본문 기호 | 의미 | 단위 |
|---|---|---|
| \(t_{\mathrm{BP}}\) | 연대 좌표 | ka BP |
| \(\tau\) | 정방향 모델 적분시간 | kyr |
| \(z\) | 지표고도 | m |
| \(z_b\) | 기반암 또는 풍화전선 고도 | m |
| \(H\) | 토심 또는 레골리스 두께 | m |
| \(T_m\) | 월평균기온 | °C |
| \(R_m\) | 월강수량 | mm month\(^{-1}\) |
| \(AET_m\) | 월 실제증발산 | mm month\(^{-1}\) |
| \(NPP_C\) | BIOME4 carbon NPP | g C m\(^{-2}\) yr\(^{-1}\) |
| \(LAI_p\) | PFT \(p\)의 optimal LAI | 무차원 |
| \(AGB^*\) | BIOME4-derived aboveground living biomass proxy | kg dry biomass m\(^{-2}\) |

Pelletier et al. (2013)의 원 논문에서는 기반암고도 \(b\), 토심 \(h\), 시간 \(t\)를 사용하지만, 본 논문에서는 전체 방법론의 변수 일원화를 위해 상태변수를 \(z_b\), \(H\), \(\tau\)로 통일한다. 식의 구조와 각 계수는 Pelletier의 원식을 유지하고, 기호만 다음과 같이 대응시킨다.

\[
b_{\mathrm{source}}\rightarrow z_b,\qquad
h\rightarrow H,\qquad
t\rightarrow\tau
\]

여기서 \(b_{\mathrm{source}}\)는 Pelletier 원문의 기반암고도 기호를 뜻한다. 토양생산 경험계수 \(b\)는 Pelletier의 계수명 그대로 유지한다.

중요하게, 각 Pelletier 식은 서로 대입하여 하나의 통합식으로 만들지 않는다. \(P_0\), \(P\), \(k_d\), \(\mathbf q\), \(K\), \(w\), \(E_f\)를 각각 독립식으로 제시한다.

## 3. 기후입력과 BIOME4

CHELSA-TraCE21k/EnviCloud의 월별 Tmin, Tmax, 강수를 사용한다. 원자료의 Tmin과 Tmax는 Kelvin이므로 월평균기온은

\[
T_m=
\frac{T_{\min,m}+T_{\max,m}}{2}
-273.15
\]

로 변환한다.

CHELSA 자료에는 추가 고도감률 보정을 적용하지 않는다.

BIOME4 v4.2b2의 absolute minimum temperature 회귀식은 원 코드 그대로 사용한다.

\[
T_{\mathrm{absmin}}
=
0.006T_{\mathrm{cold}}^2
+
1.316T_{\mathrm{cold}}
-
21.9
\]

CHELSA-TraCE21k Centennial 자료에 cloud가 없으므로 BIOME4 광입력에 필요한 cloud만 Beyer 계열 자료에서 시간 보간한다. Beyer의 기온과 강수는 사용하지 않는다. CO2는 PB4Studio에 포함된 Bereiter 계열 기록을 사용한다.

식생 코어는 BIOME4 v4.2b2이다. production에서는 native PFT climate limits를 사용한다. 토심에 따른 NPP, LAI 또는 FVC의 직접적인 경험 multiplier는 사용하지 않는다.

## 4. 토심과 available-water storage

토심은

\[
\boxed{
H=z-z_b
}
\]

로 정의한다.

### 4.1 McKenzie et al. (2003)의 원 개념

McKenzie et al. (2003)은 profile available water capacity를 \(-10\) kPa와 \(-1.5\) MPa에서의 체적수분함량 차이에 기반하여 정의한다.

\[
AWC(\zeta)
=
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\]

또한 뿌리밀도의 깊이 가중함수는

\[
\boxed{
f(x)=\exp\left(-\frac{x}{X_i}\right)
}
\]

로 제시한다.

이 두 관계가 McKenzie에서 직접 가져온 부분이다. McKenzie et al. (2003)이 BIOME4용 2층 토심모형을 제시한 것은 아니다.

### 4.2 본 연구의 BIOME4 2층 구현

PB4는 McKenzie의 available-water 개념을 용늪 SoilGrids profile에 적용하면서 BIOME4의 기존 0-0.30 m와 0.30-1.50 m 수문층을 유지한다.

\[
W_{\mathrm{top}}(H)
=
1000
\int_0^{\min(H,0.30)}
\left[
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\right]
d\zeta
\]

\[
W_{\mathrm{bottom}}(H)
=
1000
\int_{0.30}^{\min[\max(H,0.30),1.50]}
\left[
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\right]
d\zeta
\]

이는 **본 연구 구현식**이다.

production code에 사용된 깊이별 available-water density는 다음과 같다.

| 깊이 m | mm m\(^{-1}\) |
|---|---:|
| 0.00-0.05 | 237 |
| 0.05-0.15 | 232 |
| 0.15-0.30 | 218 |
| 0.30-0.60 | 207 |
| 0.60-1.00 | 198 |
| 1.00-2.00 | 179 |

BIOME4의 구조적 수문깊이 상한 때문에 실제 적분은 1.50 m까지만 수행한다.

## 5. PFT별 finite-depth root accessibility

BIOME4 v4.2b2의 \`pftpar(pft,6)\`은 Jackson et al. 계열의 상부 30 cm 누적 뿌리분율이다. 이를 \(r_{30,p}\)로 쓴다.

Jackson 계열의 누적 뿌리분포는

\[
Y(d)=1-\beta^d
\]

의 지수형 구조를 갖는다.

PB4에서는 이를 McKenzie의

\[
f(x)=\exp(-x/X_i)
\]

와 연결한다. 따라서 다음 특성깊이는 문헌 원식이 아니라 **본 연구의 분석적 변환**이다.

\[
\boxed{
X_p
=
-\frac{0.30}
{\ln(1-r_{30,p})}
}
\]

BIOME4에서 사용할 유효 토심은

\[
D=\min[\max(H,0),1.50]
\]

으로 두며, 접근 가능한 상층과 하층 뿌리분율은

\[
R_{\mathrm{top},p}
=
1-
\exp
\left[
-\frac{\min(D,0.30)}{X_p}
\right]
\]

\[
R_{\mathrm{bottom},p}
=
\begin{cases}
0, & D\le0.30\\
\exp(-0.30/X_p)-\exp(-D/X_p), & D>0.30
\end{cases}
\]

로 계산한다.

BIOME4 hydrology의 root-zone wetness는

\[
\omega_{r,p}
=
R_{\mathrm{top},p}\omega_{\mathrm{top}}
+
R_{\mathrm{bottom},p}\omega_{\mathrm{bottom}}
\]

으로 계산한다.

위 네 식은 McKenzie와 Jackson의 관계를 BIOME4 2층 수문구조에 연결한 **본 연구 구현식**이다. 얕은 토양에서 \(R_{\mathrm{top},p}+R_{\mathrm{bottom},p}<1\)이어도 1로 재정규화하지 않는다.

## 6. EEMT

### 6.1 Pelletier et al. (2013)의 원식

유효강수 에너지와 생물생산 에너지는 원문 Eq. (1)과 Eq. (2)를 그대로 사용한다.

\[
\boxed{
E_{\mathrm{PPT}}
=
\Delta T\,C_wP_{\mathrm{eff}}
}
\]

\[
\boxed{
E_{\mathrm{BIO}}
=
NPP\,h_{\mathrm{BIO}}
}
\]

따라서

\[
EEMT
=
E_{\mathrm{PPT}}
+
E_{\mathrm{BIO}}
\]

이며 \(P_{\mathrm{eff}}=PPT-ET\)이다.

### 6.2 PB4의 월별 구현

BIOME4가 월별 AET와 탄소 기준 NPP를 제공하므로 PB4에서는 위 원식을 다음과 같이 구현한다.

\[
EEMT
=
\frac{C_w}{10^6}
\sum_{m=1}^{12}
T_m
\left(
R_m-AET_m
\right)
+
\frac{h_{\mathrm{BIO}}}{10^6}
\frac{\max(NPP_C,0)}
{1000f_C}
\]

여기서

\[
C_w=4186\ {\rm J\,kg^{-1}\,K^{-1}},
\qquad
h_{\mathrm{BIO}}=22\times10^6\ {\rm J\,kg^{-1}}
\]

이고 \(f_C=0.50\)은 carbon NPP를 dry biomass로 변환하기 위한 본 연구의 명시적 가정이다.

이 월별 합산식은 Pelletier 원문의 별도 번호식이 아니라 **원 Eq. (1)-(2)를 BIOME4 출력에 적용한 본 연구 구현식**이다.

코드에서는 \(R_m-AET_m\)을 0으로 clip하지 않으며, EEMT 자체에도 과거 PB4의 1-80 MJ m\(^{-2}\) yr\(^{-1}\) clipping을 적용하지 않는다.

## 7. BIOME4-derived AGB*

본 연구에서 Pelletier의 AGB 항은 total anatomical AGB가 아니라 BIOME4-derived aboveground living biomass proxy \(AGB^*\)로 대체한다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

### 7.1 잎

Reich et al. (1992)의 원 회귀식을 그대로 사용한다.

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

\(L_{m,p}\)의 단위는 month, \(SLA_p\)의 원 단위는 cm\(^2\) g\(^{-1}\)이다.

SLA의 정의에 따라

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 계산하며, 계산 시 SLA 단위만 m\(^2\) kg\(^{-1}\)로 변환한다.

논문 본문에서는 이를 전개해 얻는 \`0.0363078055...\`를 별도의 계수로 제시하지 않는다.

### 7.2 변재

Haxeltine and Prentice (1996) Eq. (34)의 원식은

\[
\boxed{
C_s=LAI\,C_n
}
\]

이다.

BIOME4 v4.2b2 source code에서 \`stemcarbon=0.5\`는 sapwood carbon per unit LAI로 사용된다. 따라서 BIOME4에서 sapwood respiration이 활성인 PFT는 \(C_n=0.5\)를 적용하며,

\[
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
\]

로 dry biomass로 변환한다. \(f_C=0.50\)은 본 연구의 명시적 변환 가정이다.

BIOME4 source에서 sapwood respiration을 제거하는 PFT에는 sapwood term을 적용하지 않는다. 이를 위해 코드에서 indicator를 사용할 수 있지만, 논문 원식에 새로운 생태 파라미터처럼 제시하지 않는다.

## 8. Pelletier 지형발달

Pelletier et al. (2013)의 식 구조를 그대로 사용하되, 본 논문의 상태변수는 전체 방법론과 일치하도록 \(z_b\), \(H\), \(\tau\)로 통일한다. 각 과정식은 서로 대입해 합치지 않고 독립적으로 제시한다.

### 8.1 상태변수

Pelletier Eq. (6)의 구조를 본 연구 표기로 쓰면

\[
\boxed{
z=z_b+H
}
\]

이다.

Pelletier Eq. (7)은

\[
\boxed{
\frac{\partial z_b}{\partial \tau}
=
U
-
\frac{P}{\cos\theta}
}
\]

로 쓴다.

Pelletier Eq. (8)은

\[
\boxed{
\frac{\partial H}{\partial \tau}
=
\frac{\rho_b}{\rho_s}
\frac{P}{\cos\theta}
-
E
}
\]

로 쓴다.

이 세 식은 상태변수 관계와 질량수지만 나타내며, 아래 과정식을 여기에 대입해 하나의 전개식으로 만들지 않는다.

### 8.2 토양생산

Pelletier Eq. (9)의 구조는

\[
\boxed{
P
=
P_0
\exp
\left(
-\frac{H\cos\theta}{H_0}
\right)
}
\]

로 쓴다.

Pelletier Eq. (10)은 별도 식으로

\[
\boxed{
P_0
=
a\exp(b\,EEMT)
}
\]

를 제시한다.

즉 \(P_0\)를 Eq. (9)에 대입하여 하나의 토양생산식으로 합치지 않는다.

### 8.3 사면수송

Pelletier Eq. (11)의 침식 또는 퇴적항은

\[
\boxed{
E_c
=
\nabla\cdot\mathbf q
}
\]

로 둔다.

본 연구에서 사용하는 depth-dependent nonlinear transport는 Pelletier Eq. (14)의 구조를 그대로 사용한다.

\[
\boxed{
\mathbf q
=
-
\frac{
k_dH\cos\theta\,\nabla z
}{
1-(|\nabla z|/S_c)^2
}
}
\]

기후와 식생에 따른 transport coefficient는 Pelletier Eq. (15)를 별도 식으로 둔다.

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

여기서 Pelletier 원식의 \(AGB\) 입력만 본 연구의 BIOME4-derived \(AGB^*\)로 대체한다.

\(k_d\)를 \(\mathbf q\) 식에 대입하여 전개하지 않는다.

### 8.4 유수침식

Pelletier et al. (2013)의 slope-wash 및 fluvial incision 식은

\[
\boxed{
E_f
=
K
\frac{A}{w}
|\nabla z|
}
\]

로 유지한다.

여기서 유효 유로폭 \(w\)는 모든 셀에서 동일한 식으로 계산하지 않는다. Pelletier et al. (2013)의 원 구조에 따라 hillslope sheet-flow 셀에서는 grid-cell width를 사용하고,

\[
\boxed{
w=\Delta x
}
\]

tributary-valley 셀에서는 valley-bottom width 관계를 사용한다.

\[
\boxed{
w=gA^i
}
\]

원 연구는 \(g=0.005\), \(i=0.5\)를 사용하였다.

regolith에 대한 erodibility는 Pelletier Eq. (18)을 별도 식으로

\[
\boxed{
K_{\mathrm{reg}}
=
\frac{K_0}{EEMT}
}
\]

로 둔다.

Pelletier et al. (2013)은 bedrock의 fluvial erodibility를 regolith보다 작게 두었으며 Table 1의 비율 \(F=10\)을 사용하였다. 이를 본 연구 표기로 쓰면

\[
\boxed{
K_{\mathrm{bed}}
=
\frac{K_{\mathrm{reg}}}{F}
}
\]

이다.

따라서 \(w\), \(K_{\mathrm{reg}}\), \(K_{\mathrm{bed}}\)을 \(E_f\) 식 안에 대입하여 하나의 전개식으로 만들지 않는다.

PB4는 hillslope와 valley를 구분하기 위해 Pelletier et al. (2013)이 기술한 grid-resolution-dependent \(A/w\) 분류논리를 유지한다. 실제 raster 구현에서는 \(|\nabla z|\)을 flow-routing 방향 경사로 평가하고, 한 substep에서 실제 가용 레골리스보다 많은 물질을 제거하지 못하도록 finite-supply constraint를 적용한다. 이 공급제약은 Pelletier의 원 과정식이 아니라 PB4의 수치구현 확장이다.

## 9. Pelletier 원 연구값과 용늪 production 값의 구분

최종 package의 지형모형 코드와 보존된 source audit를 대조하면 다음과 같다.

| 항목 | Pelletier et al. (2013) | 용늪 production |
|---|---:|---:|
| \(a\) | 0.037 m kyr\(^{-1}\) | 0.037 |
| \(b\) | 0.030 m\(^2\) yr MJ\(^{-1}\) | 0.030 |
| \(h_0\) | 0.50 m | 0.50 m |
| \(\rho_b/\rho_s\) | 1.8 | 1.8 |
| \(c\) | 0.033 | 0.033 |
| \(d\) | 0.050 | 0.050 |
| \(K_0\) | 0.020 m\(^2\) MJ\(^{-1}\) | 0.020 |
| \(g\) | 0.005 | 원 구조 유지 |
| \(i\) | 0.5 | 원 구조 유지 |
| \(F\) | 10 | 원 구조 유지 |
| \(S_c\) | 0.7, 0.9 sensitivity | **1.50** |
| \(U\) | 0.05 m kyr\(^{-1}\) | **0.20 m kyr\(^{-1}\)** |

따라서 \(S_c=1.50\)과 \(U=0.20\)은 Pelletier et al. (2013)의 원 연구값이라고 쓰면 안 된다. \(S_c=1.50\)은 용늪 20 m real-DEM 수치수렴시험을 거쳐 채택된 모델별 수치설정이다. \(U=0.20\ {\rm m\,kyr^{-1}}\)은 Park et al. (2017)이 고성-삼척의 동해안 중부 해안단구에서 제시한 약 0.16-0.28 m kyr\(^{-1}\)의 후기 제4기 융기율 범위 안에 놓이므로 지역 참고값으로 사용할 수 있다. 다만 이 값은 용늪 자체에서 직접 측정한 융기율이 아니므로, 본 연구에서는 동해안 중부의 장기 지각융기를 대표하는 일정한 regional forcing으로 취급한다.

또한 Pelletier의 모델실험 EEMT 범위는 대략 5-45 MJ m\(^{-2}\) yr\(^{-1}\)였으나 용늪 PB4에서는 이 범위를 넘는 EEMT가 발생한다. 따라서 EEMT 관련 계수의 외삽은 한계로 명시한다.

## 10. 수치해석과 source equation의 구분

Pelletier et al. (2013)의 물리식과 별개로 PB4에는 다음 수치 구현이 있다.

- 100년 coupling interval 내부의 adaptive geomorphic substep
- finite-volume donor-supply positivity constraint
- 실제 DEM의 초임계 경사를 처리하는 threshold-slope adjustment
- open outlet의 fixed base-level boundary
- accepted state를 float64로 유지
- 최대 허용 변화량 0.025 m를 기준으로 한 adaptive trial rejection

0.025 m는 물리 파라미터가 아니다. Pelletier et al. (2013)은 timestep을 동적으로 줄여 안정성을 확보했지만 이 프로젝트의 0.025 m 값 자체는 PB4 convergence audit에서 정한 **수치오차 허용기준**이다.

기본 explicit timestep 추정은 Pelletier의 형태를 따라

\[
\Delta t
=
0.01
\frac{\Delta x^2}
{2k_{d,\max}}
\]

를 사용하고, 필요할 경우 더 작은 substep으로 줄인다.

## 11. dynamic coupling

한 100년 coupling interval의 계산순서는 다음과 같다.

\`\`\`text
현재 z, z_b, H
-> 해당 t_BP의 CHELSA 기후
-> available-water storage
-> PFT별 root accessibility
-> BIOME4
-> NPP, AET, LAI, dominant PFT
-> EEMT, AGB*
-> Pelletier 지형발달
-> 새로운 z, z_b, H
-> 다음 t_BP
\`\`\`

각 100년 구간에서 BIOME4를 한 번 계산하고, 그 구간의 geomorphic adaptive substep 동안 동일한 EEMT와 AGB* forcing을 사용한다.

static 실험에서는 초기 지형과 토심을 고정한다. dynamic 실험에서는 변화한 지형과 토심이 다음 시점의 수문과 BIOME4 계산으로 다시 들어간다.

## 12. 검증

최종 정량 검증에는 Jang et al. (2011)의 \`95_01\`, \`95_02\`, \`95_03\`, \`95_04\`만 사용하며 총 62개 100년 output-time을 평가한다.

BIOME4 mixed biome의 검증용 reduced classification에서는 가장 강한 활엽수 PFT의 잠재 NPP와 가장 강한 침엽수 PFT의 잠재 NPP를 비교한다. 한쪽 비율이 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 둔다. 이는 BIOME4 내부 PFT 경쟁식이 아니라 검증용 후처리이다.

각 Jang 검증 시점에서 관측 식생군이 모의 유역 내 유효 격자의 1% 이상에서 출현하면 일치한 것으로 판정한다. 1% 기준은 별도의 모델 수식으로 만들지 않는다.

최종 production 결과는 static 24/62 = 38.71%, dynamic 55/62 = 88.71%이다.

Park et al. (2021)의 holdout, PC2 상관, Herbs 비교는 최종 Methods와 최종 정량검증에서 사용하지 않는다.

## 13. Methods 본문에서 제시할 핵심 수식

본문에서는 다음 원식과 핵심 구현식만 제시한다.

1. McKenzie root-depth 원식 \(f(x)=\exp(-x/X_i)\)과 PB4 2층 water-store 구현
2. Jackson/BIOME4 \(r_{30,p}\)에서 \(X_p\)로 가는 본 연구 변환
3. Pelletier EEMT Eq. (1)-(2)와 PB4 월별 구현
4. Reich SLA-life-span 원식과 \(B_{\mathrm{leaf}}=LAI/SLA\)
5. Haxeltine and Prentice \(C_s=LAI\,C_n\)
6. \(AGB^*=B_{\mathrm{leaf}}+B_{\mathrm{sapwood}}\)
7. Pelletier Eq. (6)-(10), Eq. (14)-(18)을 각각 독립식으로 제시하고 상호 대입하지 않음. 유수침식에서는 hillslope의 \(w=\Delta x\)와 valley의 \(w=gA^i\), regolith/bedrock erodibility를 구분함
8. 수치구현은 별도 서술하고 Eq. (20)-(22)는 보충자료에 제시

검증의 51% 재분류와 1% 출현 기준은 검증 절에서 문장으로 설명한다.

## 14. 문서 권위순위

1. 이 문서 \`FINAL_METHODS_CANONICAL_20261006_KO.md\`
2. 최종 production package와 \`results/final_integrated_20261006/FINAL_PROVENANCE.json\`
3. AGB 세부근거 \`BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md\`
4. 원문 대조용 \`VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md\`

과거 문서에 이 문서와 다른 변수명, 전개 소수계수, 폐기된 AGB 식 또는 Park 정량검증이 남아 있으면 이 문서를 따른다.

## 15. 핵심 참고문헌

Kaplan, J. O. (2001). Geophysical Applications of Vegetation Modeling. Doctoral dissertation, Lund University. ISBN 91-7874-089-4.

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. Journal of Geophysical Research: Atmospheres, 108(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. Global Biogeochemical Cycles, 10(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. Ecological Monographs, 62(3), 365-392. https://doi.org/10.2307/2937116

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). Estimating water storage capacities in soil at catchment scales. CRC for Catchment Hydrology.

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. Journal of Geophysical Research: Earth Surface, 118, 741-758. https://doi.org/10.1002/jgrf.20046


Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces and uplift rate in the East Coast of South Korea. Journal of the Korean Geomorphological Association, 24(4), 43-55.

Karger, D. N., et al. (2023). Climatologies at high resolution for the Earth's land surface areas. Climate of the Past, 19, 439-456.

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. Scientific Data, 7, 236.

Bereiter, B., et al. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. Geophysical Research Letters, 42, 542-549.

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. Canadian Journal of Forest Research, 17, 829-834.

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. Oecologia, 108, 389-411.

Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., & Rossiter, D. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. SOIL, 7, 217-240.
