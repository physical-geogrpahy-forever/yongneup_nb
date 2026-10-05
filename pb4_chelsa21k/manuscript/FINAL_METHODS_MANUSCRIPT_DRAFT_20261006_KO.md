# 용늪 BIOME4-Pelletier 결합모형 Methods 본문 초안

작성일: 2026-10-06  
상태: **원문 및 production code 대조 반영본**  
수식 기준: \`FINAL_METHODS_CANONICAL_20261006_KO.md\`  
출처 감사: \`FINAL_METHODS_SOURCE_AUDIT_20261006_KO.md\`

이 문서는 실제 논문 Methods 본문에 사용할 서술형 초안이다. 문헌에서 가져온 과정식은 원 논문의 구조를 유지하고, 결합모형 전체의 상태변수만 \(z\), \(z_b\), \(H\), \(\tau\)로 통일하였다. Pelletier et al. (2013)의 과정식은 서로 대입하여 하나의 통합식으로 만들지 않고 각각 독립적으로 제시하였다.

## 2.1 연구 설계와 결합모형

본 연구는 대암산 용늪에서 후기 빙기 이후의 기후변화가 식생과 토심, 지형발달의 상호작용을 통해 장기적인 식생사에 미치는 영향을 평가하기 위해 BIOME4 v4.2b2와 식생-토양-지형 상호작용을 모의하는 Pelletier et al. (2013)의 경관발달식을 결합하였다. BIOME4는 기후, 대기 CO2, 토양수분조건에 따라 PFT별 NPP와 NPP를 최대화하는 LAI를 계산하고 PFT 경쟁을 통해 잠재 식생을 판정하는 평형 식생모형이다(Kaplan, 2001). 본 연구에서는 원 BIOME4 v4.2b2의 13개 PFT와 native climate limits를 유지하였다.

모의기간은 21.0 ka BP부터 현재까지이며 결합 간격은 0.1 kyr로 설정하였다. 따라서 기후와 식생은 총 211개 시점에서 계산하였다. 정적 실험에서는 초기 지표고도와 토심을 전체 기간 동안 고정한 채 기후 forcing만 변화시켰다. 동적 실험에서는 각 시점의 BIOME4 결과로부터 EEMT와 \(AGB^*\)를 산정한 뒤 지형발달모형을 100년 동안 적분하고, 갱신된 지표고도와 토심을 다음 시점의 BIOME4 계산에 다시 입력하였다.

연대 좌표는 \(t_{\mathrm{BP}}\), 정방향 모델 적분시간은 \(\tau\)로 구분하였다. 지표고도는 \(z\), 기반암 또는 풍화전선 고도는 \(z_b\), 토심 또는 레골리스 두께는 \(H\)로 표기하고,

\[
\boxed{
H=z-z_b
}
\]

로 정의하였다.

## 2.2 기후 forcing과 BIOME4 입력

기온과 강수 forcing에는 CHELSA-TraCE21k의 월별 자료를 사용하였다. CHELSA-TraCE21k는 LGM 이후의 월별 기온과 강수량을 1 km 공간해상도로 하향화한 기후자료이다(Karger et al., 2023). 본 연구의 production 입력파일은 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`이며, 용늪 위치에 대해 추출한 월별 최저기온, 최고기온 및 강수량을 21.0-0.0 ka BP 범위에서 사용하였다. 원자료의 최저기온과 최고기온은 Kelvin 단위이므로 월평균기온은

\[
T_m
=
\frac{T_{\min,m}+T_{\max,m}}{2}
-
273.15
\]

로 변환하였다. CHELSA-TraCE21k 자체가 지형효과를 고려해 하향화된 자료이므로 PB4에서는 별도의 고도감률 보정을 추가하지 않았다.

BIOME4는 월별 cloudiness 또는 sunshine을 요구하지만 원 CHELSA-TraCE21k Centennial forcing에는 cloud cover가 포함되지 않는다. 따라서 cloudiness만 Beyer et al. (2020)의 후기 제4기 기후자료에서 가져와 월별로 시간보간하였으며, Beyer 자료의 기온과 강수량은 사용하지 않았다. 즉 기온과 강수량은 CHELSA-TraCE21k, cloudiness는 Beyer et al. (2020)의 보조 forcing으로 분리하였다.

대기 CO2 forcing에는 Bereiter et al. (2015)의 revised Antarctic composite를 사용하였다. PB4 package에 포함된 NOAA/NCEI 기록을 각 \(t_{\mathrm{BP}}\)에 대해 선형보간하였으며, 원자료의 시간범위를 벗어난 외삽은 허용하지 않았다.

BIOME4의 absolute minimum temperature는 v4.2b2 원 코드의 회귀식을 그대로 사용하였다.

\[
T_{\mathrm{absmin}}
=
0.006T_{\mathrm{cold}}^2
+
1.316T_{\mathrm{cold}}
-
21.9
\]

여기서 \(T_{\mathrm{cold}}\)는 가장 추운 달의 월평균기온이다. 본 연구에서는 토심에 따라 NPP, LAI 또는 FVC에 직접 곱해지는 별도의 경험계수를 사용하지 않았다. 토심의 영향은 아래에서 설명하는 available-water storage와 PFT별 finite-depth root accessibility를 통해 BIOME4 수문계산으로 전달하였다.

## 2.3 토심에 따른 available-water storage

토심이 BIOME4 수문상태에 미치는 영향은 McKenzie et al. (2003)의 profile available water capacity 개념을 이용하여 구현하였다. McKenzie et al. (2003)은 profile available water capacity를 명목상 field capacity와 wilting point에 해당하는 matric potential \(-10\) kPa와 \(-1.5\) MPa 사이의 체적수분함량 차이를 토양깊이에 대해 적분한 값으로 정의하였다. 따라서 깊이 \(\zeta\)에서의 available-water density는

\[
AWC(\zeta)
=
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\]

로 두었다(McKenzie et al., 2003).

용늪의 깊이별 수분특성은 SoilGrids 기반 point profile을 사용하였다. SoilGrids 2.0은 전지구 토양특성을 250 m 격자로 제공하는 디지털 토양지도 체계이다(Poggio et al., 2021). 다만 본 연구의 \(\theta_{-10}\)과 \(\theta_{-1500}\) profile 및 그 차이는 용늪 위치에서 확보한 project-specific 입력이며, Poggio et al. (2021)이 해당 용늪 수분특성값 자체를 제시한 것은 아니다.

BIOME4 v4.2b2의 기존 수문구조에 맞추어 상층은 0-0.30 m, 하층은 0.30-1.50 m로 구분하였다. 실제 토심 \(H\)에 따른 각 층의 available-water storage는

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

및

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

로 계산하였다. 이 두 식은 McKenzie et al. (2003)의 profile available-water 개념을 BIOME4 v4.2b2의 2층 수문구조에 연결한 본 연구의 구현식이다. BIOME4의 구조적 수문깊이 때문에 1.50 m보다 깊은 토양은 추가 water store로 사용하지 않았다.

Production code에 사용된 available-water density는 0-0.05 m에서 237 mm m\(^{-1}\), 0.05-0.15 m에서 232 mm m\(^{-1}\), 0.15-0.30 m에서 218 mm m\(^{-1}\), 0.30-0.60 m에서 207 mm m\(^{-1}\), 0.60-1.00 m에서 198 mm m\(^{-1}\), 1.00-2.00 m에서 179 mm m\(^{-1}\)이다. 마지막 구간도 실제 BIOME4 계산에서는 1.50 m까지만 사용하였다.

## 2.4 PFT별 finite-depth root accessibility

뿌리의 수직분포는 Gale and Grigal (1987)의 누적분포식

\[
\boxed{
Y(d)
=
1-\beta^d
}
\]

을 바탕으로 하였다. 여기서 \(Y(d)\)는 지표에서 깊이 \(d\)까지 존재하는 누적 뿌리분율이며, Jackson et al. (1996)은 이 식을 여러 생물군계와 PFT의 뿌리분포에 적용하였다. BIOME4 v4.2b2에서는 PFT별 상부 30 cm 누적 뿌리분율이 \`pftpar(pft,6)\`에 저장되어 있으며, 본 연구에서는 이를 \(r_{30,p}\)로 표기하였다.

McKenzie et al. (2003)은 plant available water capacity 계산에서 토심에 따른 root-density scaling을 고려하며 지수형 깊이감쇠를 사용하였다. 이를 BIOME4의 상부 30 cm 누적 뿌리분율과 연결하기 위해 본 연구에서는 PFT별 특성깊이 \(X_p\)를

\[
\boxed{
X_p
=
-\frac{0.30}
{\ln(1-r_{30,p})}
}
\]

로 계산하였다. 이 식은 McKenzie et al. (2003) 또는 Jackson et al. (1996)의 원식이 아니라 두 자료구조를 연결하기 위한 본 연구의 분석적 변환이다.

BIOME4에서 사용할 유효 토심은

\[
D
=
\min[\max(H,0),1.50]
\]

로 제한하였다. 실제 토심에서 접근할 수 있는 상층과 하층 뿌리분율은 각각

\[
R_{\mathrm{top},p}
=
1-
\exp
\left[
-\frac{\min(D,0.30)}{X_p}
\right]
\]

과

\[
R_{\mathrm{bottom},p}
=
\begin{cases}
0, & D\le0.30\\
\exp(-0.30/X_p)-\exp(-D/X_p), & D>0.30
\end{cases}
\]

로 계산하였다. PFT별 root-zone wetness는

\[
\omega_{r,p}
=
R_{\mathrm{top},p}\omega_{\mathrm{top}}
+
R_{\mathrm{bottom},p}\omega_{\mathrm{bottom}}
\]

으로 BIOME4 수문계산에 전달하였다. 얕은 토양에서 \(R_{\mathrm{top},p}+R_{\mathrm{bottom},p}<1\)이 되더라도 이를 1로 재정규화하지 않았다. 따라서 실제 토심 아래에 존재했을 뿌리분율을 상부 토양층으로 인위적으로 재배치하지 않았다.

## 2.5 EEMT

식생과 수문상태를 지형발달모형에 연결하는 기후에너지 변수로 Pelletier et al. (2013)의 EEMT를 사용하였다. Pelletier et al. (2013)은 유효강수에 의해 공급되는 에너지와 생물생산에 축적되는 에너지를 각각

\[
\boxed{
E_{\mathrm{PPT}}
=
\Delta T\,C_wP_{\mathrm{eff}}
}
\]

과

\[
\boxed{
E_{\mathrm{BIO}}
=
NPP\,h_{\mathrm{BIO}}
}
\]

로 정의하고, 두 성분의 합으로 EEMT를 계산하였다. 여기서 \(P_{\mathrm{eff}}=PPT-ET\)이다(Pelletier et al., 2013).

PB4에서는 BIOME4가 계산하는 월별 AET와 연간 carbon NPP를 이용하여 위 관계를 월별 forcing에 적용하였다.

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

여기서 \(R_m\)은 월강수량, \(AET_m\)은 월 실제증발산량이며, \(C_w=4186\ {\rm J\,kg^{-1}\,K^{-1}}\), \(h_{\mathrm{BIO}}=22\times10^6\ {\rm J\,kg^{-1}}\)을 사용하였다(Pelletier et al., 2013). \(NPP_C\)는 BIOME4가 출력하는 연간 carbon NPP이고, \(f_C=0.50\)은 carbon mass를 dry biomass로 변환하기 위한 본 연구의 명시적 가정이다. 따라서 이 월별 합산식 전체를 Pelletier et al. (2013)의 원식으로 간주하지 않고, 원 EEMT 관계를 BIOME4 출력에 적용한 본 연구의 구현식으로 구분하였다. \(R_m-AET_m\)은 0으로 clipping하지 않았으며, EEMT에도 과거 PB4에서 사용했던 1-80 MJ m\(^{-2}\) yr\(^{-1}\) 범위의 clipping을 적용하지 않았다.

## 2.6 BIOME4-derived AGB*

Pelletier et al. (2013)의 사면수송계수에는 AGB가 입력되지만 BIOME4 v4.2b2는 total anatomical AGB를 독립된 standing stock으로 출력하지 않는다. 따라서 본 연구에서는 BIOME4의 dominant PFT와 optimal LAI를 이용하여 잎과 살아 있는 변재로 구성된 BIOME4-derived aboveground living biomass proxy \(AGB^*\)를 계산하였다. 각 격자의 dominant PFT를 \(p^*\)라고 하면

\[
\boxed{
AGB^*
=
B_{\mathrm{leaf,dry},p^*}
+
B_{\mathrm{sapwood,dry},p^*}
}
\]

로 정의하였다.

잎 건조생체량에는 Reich et al. (1992, Table 1)의 전체 LEAVES 자료에 대한 SLA-life-span 회귀식을 사용하였다.

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

여기서 \(L_{m,p}\)는 PFT \(p\)의 잎수명이며 단위는 month이고, Reich et al. (1992)의 SLA 단위는 cm\(^2\) g\(^{-1}\)이다. SLA가 leaf area / leaf dry mass이고 LAI가 leaf area / ground area이므로 SLA를 m\(^2\) kg\(^{-1}\)로 변환한 뒤

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 잎 건조생체량을 계산하였다. 논문 Methods에서는 이 식을 대수적으로 전개하여 생성되는 소수계수를 별도의 경험계수처럼 제시하지 않았다.

변재량은 BIOME3에서 제시된 sapwood-LAI 관계

\[
\boxed{
C_s
=
LAI\,C_n
}
\]

를 사용하였다(Haxeltine & Prentice, 1996, Eq. 34). 식생모형 자체를 BIOME3와 결합한 것은 아니며, 이 관계는 BIOME4에 계승된 sapwood 계산의 문헌적 원전으로만 사용하였다. BIOME4 v4.2b2의 respiration source code에서는 \`stemcarbon=0.5\`가 sapwood carbon per unit LAI로 사용되므로 이를 \(C_n\)에 적용하였다. 변재 dry biomass는

\[
\boxed{
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
}
\]

로 환산하였다. 여기서 \(f_C=0.50\)은 EEMT의 biological term과 동일하게 사용한 본 연구의 carbon-fraction 가정이다. BIOME4 v4.2b2에서 \`pftpar(pft,10)=2\`로 sapwood respiration을 제거하는 PFT에는 \(AGB^*\) 계산에서도 변재항을 적용하지 않았다.

따라서 \(AGB^*\)는 total anatomical AGB가 아니라 BIOME4에서 추적 가능한 foliage와 living sapwood를 이용한 aboveground living biomass proxy이다. 심재와 장기 목질부처럼 BIOME4가 별도 standing stock으로 제공하지 않는 구성요소는 포함하지 않았다.

## 2.7 Pelletier 지형발달모형

지형발달에는 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 slope-wash/fluvial erosion 구조를 사용하였다. 원 논문의 과정식은 유지하되 결합모형 전체의 변수 일원화를 위해 기반암고도는 \(z_b\), 토심은 \(H\), 정방향 적분시간은 \(\tau\)로 표기하였다. 각 과정식은 서로 대입하여 하나의 통합식으로 전개하지 않았다.

지표고도는

\[
\boxed{
z=z_b+H
}
\]

로 정의하였다. 기반암고도의 변화는

\[
\boxed{
\frac{\partial z_b}{\partial\tau}
=
U
-
\frac{P}{\cos\theta}
}
\]

로 계산하고, 토심 변화는

\[
\boxed{
\frac{\partial H}{\partial\tau}
=
\frac{\rho_b}{\rho_s}
\frac{P}{\cos\theta}
-
E
}
\]

로 계산하였다(Pelletier et al., 2013).

### 2.7.1 토양생산

토심에 따른 토양생산률은

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

로 계산하였다. 잠재 토양생산률 \(P_0\)는 별도의 관계식

\[
\boxed{
P_0
=
a\exp(b\,EEMT)
}
\]

으로 계산하였다(Pelletier et al., 2013). Production에서는 \(a=0.037\ {\rm m\,kyr^{-1}}\), \(b=0.030\), \(H_0=0.50\ {\rm m}\), \(\rho_b/\rho_s=1.8\)을 사용하였다. \(P_0\)를 \(P\) 식에 대입하여 하나의 전개식으로 만들지 않았다.

### 2.7.2 비선형 사면수송

사면수송에 따른 침식 또는 퇴적항은

\[
\boxed{
E_c
=
\nabla\cdot\mathbf q
}
\]

로 나타냈다. 토심과 임계경사를 함께 고려하는 비선형 사면수송은

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

로 계산하였다(Pelletier et al., 2013). 수송계수 \(k_d\)는 별도의 식

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

으로 계산하였다. Pelletier et al. (2013)의 원식에서 AGB가 들어가는 위치는 유지하되, 그 상태변수를 본 연구에서 BIOME4로 계산한 \(AGB^*\)로 대체하였다. Production에서는 \(c=0.033\), \(d=0.050\)을 사용하였다. \(k_d\)를 \(\mathbf q\) 식 안에 대입하여 전개하지 않았다.

Pelletier et al. (2013)은 \(S_c=0.7\)을 기준값으로 사용하고 0.9를 sensitivity case로 검토하였다. 본 연구의 20 m real DEM에서는 이 값을 그대로 사용할 경우 초기 초임계경사가 광범위하게 발생하므로, 별도의 수치수렴시험을 통해 \(S_c=1.50\)을 production 값으로 사용하였다. 따라서 \(S_c=1.50\)은 Pelletier et al. (2013)의 원 파라미터가 아니라 용늪 raster 계산을 위한 본 연구의 수치설정이다.

### 2.7.3 slope-wash 및 fluvial erosion

Pelletier et al. (2013)의 slope-wash/fluvial erosion은

\[
\boxed{
E_f
=
K
\frac{A}{w}
|\nabla z|
}
\]

로 계산하였다. 여기서 \(A\)는 contributing area이고 \(w\)는 유효 유로폭이다. \(w\)는 모든 격자에서 \(gA^i\)로 계산하지 않았다. Pelletier et al. (2013)의 원 구조에 따라 hillslope의 sheet-flow 셀에서는

\[
\boxed{
w=\Delta x
}
\]

를 사용하고, tributary-valley 셀에서만

\[
\boxed{
w=gA^i
}
\]

를 사용하였다. 원 연구와 동일하게 \(g=0.005\), \(i=0.5\)의 구조를 유지하였다(Pelletier et al., 2013). Hillslope와 valley의 구분에는 Pelletier et al. (2013)이 설명한 grid-resolution-dependent \(A/w\) 분류논리를 적용하였다.

Regolith의 fluvial erodibility는

\[
\boxed{
K_{\mathrm{reg}}
=
\frac{K_0}{EEMT}
}
\]

로 계산하였다(Pelletier et al., 2013). Production에서는 \(K_0=0.020\ {\rm m^2\,MJ^{-1}}\)을 사용하였다. Pelletier et al. (2013)은 bedrock의 erodibility를 regolith보다 작게 두었으며 Table 1에서 두 erodibility의 비율을 \(F=10\)으로 설정하였다. 따라서 bedrock erodibility는 별도로

\[
\boxed{
K_{\mathrm{bed}}
=
\frac{K_{\mathrm{reg}}}{F}
}
\]

로 처리하였다. \(w\), \(K_{\mathrm{reg}}\), \(K_{\mathrm{bed}}\)을 \(E_f\) 식에 대입하여 하나의 전개식으로 만들지 않았다.

실제 PB4 raster 구현에서는 \(|\nabla z|\)을 flow-routing 방향 경사로 평가하였다. 또한 한 geomorphic substep에서 donor cell의 가용 레골리스보다 많은 물질이 제거되지 않도록 finite-supply constraint를 적용하였다. 이 공급제약은 Pelletier et al. (2013)의 과정식 자체가 아니라 PB4의 수치구현이다.

### 2.7.4 융기

Pelletier et al. (2013)의 원 실험에서는 \(U=0.05\ {\rm m\,kyr^{-1}}\)을 사용하였다. 본 연구에서는 동해안 중부의 장기적인 후기 제4기 융기율을 참고하여 \(U=0.20\ {\rm m\,kyr^{-1}}\)을 일정한 regional forcing으로 사용하였다. Park et al. (2017)은 고성에서 삼척까지 동해안 중부의 해안단구를 검토하고 당시 해수면을 고려했을 때 MIS 5 이후의 융기율을 약 0.16-0.28 m kyr\(^{-1}\)로 제시하였다. 따라서 0.20 m kyr\(^{-1}\)은 이 범위 안에 위치한다. 다만 이 값은 용늪 자체에서 직접 측정한 융기율이 아니라 인접 동해안 중부의 장기 지각융기를 대표하기 위해 적용한 지역값이다.

## 2.8 수치 적분과 결합 순서

기후와 식생은 100년 간격으로 갱신하였지만 지형발달모형은 각 100년 interval 내부에서 adaptive substep으로 적분하였다. 각 interval에서 현재 \(z\), \(z_b\), \(H\)와 해당 \(t_{\mathrm{BP}}\)의 기후를 이용해 available-water storage와 PFT별 root accessibility를 계산하고 BIOME4를 한 번 실행하였다. 이후 BIOME4의 NPP, AET, LAI와 dominant PFT로부터 EEMT와 \(AGB^*\)를 계산하여 해당 100년 interval의 지형 forcing으로 고정하였다. 따라서 지형 adaptive substep 사이에는 기후를 다시 읽거나 BIOME4를 재실행하지 않았다.

기본 explicit timestep은 Pelletier et al. (2013)의 안정성 추정형태를 따라

\[
\Delta\tau
=
0.01
\frac{\Delta x^2}
{2k_{d,\max}}
\]

로 계산하고 필요할 경우 더 작은 substep으로 줄였다. PB4에서는 trial step에서 hillslope transport, fluvial erosion 또는 threshold adjustment에 의한 최대 변화량이 0.025 m를 초과하면 그 trial을 폐기하고 동일한 accepted state에서 더 작은 timestep으로 재계산하였다. 0.025 m는 물리 파라미터가 아니라 용늪 real-DEM convergence audit에서 채택한 수치오차 허용기준이다.

또한 초임계경사를 포함하는 실제 DEM을 처리하기 위한 threshold-slope adjustment와 open outlet의 fixed base-level boundary를 적용하였다. 이들 절차와 finite-supply constraint는 Pelletier의 생태지형 과정식을 수정한 경험보정이 아니라 실제 raster에서 음의 토심과 수치발산을 방지하기 위한 수치구현으로 구분하였다.

## 2.9 정적 및 동적 실험

정적 실험에서는 초기 \(z\), \(z_b\), \(H\)를 고정하고 21.0-0.0 ka BP의 기후 forcing에 대해서만 BIOME4를 반복 계산하였다. 따라서 기후변화에 따른 식생반응은 나타나지만 지형과 토심의 feedback은 발생하지 않는다.

동적 실험에서는 각 100년 interval의 마지막에 지형발달모형이 계산한 \(z_b\)와 \(H\)를 갱신하고 \(z=z_b+H\)로 다음 지표고도를 정의하였다. 갱신된 \(H\)는 다음 시점의 available-water storage와 root accessibility를 바꾸며, 그 결과 BIOME4의 수분스트레스, NPP, LAI 및 dominant PFT가 달라질 수 있다. 변화한 식생은 다시 EEMT와 \(AGB^*\)를 통해 다음 지형발달에 입력된다.

## 2.10 Jang et al. (2011)에 의한 식생사 검증

최종 정량검증에는 Jang et al. (2011)의 용늪 화분기록만 사용하였다. Jang et al. (2011)은 180 cm 깊이의 용늪 퇴적물에서 61개 화분분석 시료와 5개 방사성탄소 연대시료를 분석하고 네 개의 local pollen zone을 구분하였다. 보고된 식생대는 LPZ-I 5,900-4,800 cal BP의 냉온대 중부/산지 낙엽활엽수림, LPZ-II 4,800-3,400 cal BP의 냉온대 북부/아고산 침엽수-낙엽활엽수 혼효림, LPZ-III 3,400-390 cal BP의 냉온대 중부/산지 낙엽활엽수림, LPZ-IV 390 cal BP-현재의 낙엽활엽수-침엽수 혼효림이다(Jang et al., 2011).

PB4 검증에서는 이 네 LPZ의 연대구간을 0.1 kyr 간격의 모델 출력시점과 대응시켰다. 프로젝트 내부 record는 \`95_01\`부터 \`95_04\`까지로 관리하며, 네 연대구간을 100년 출력격자에 대응한 결과 총 62개의 **모델 평가시점**이 생성되었다. 따라서 \(n=62\)는 Jang et al. (2011)의 화분 시료수가 아니라 PB4의 100년 출력격자에서 생성된 검증 항목수이다.

BIOME4 native biome 가운데 mixed forest에 해당하는 범주는 Jang의 식생대와 비교하기 위해 reduced class로 후처리하였다. 침엽수군과 활엽수군에서 각각 가장 높은 잠재 NPP를 갖는 PFT를 비교하여 한쪽의 비율이 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 유지하였다. 이 51% 기준은 BIOME4 내부 PFT 경쟁이나 생리과정의 임계값이 아니라 검증을 위한 출력 후처리 기준이다.

각 평가시점에서 Jang et al. (2011)의 해당 식생군이 모의 유역의 유효 격자 중 1% 이상에서 출현하면 일치로 판정하였다. 이 1% 역시 모델 내부 파라미터가 아니라 산지 유역 내부의 공간적 이질성을 허용하기 위한 검증 판정기준이다. 51%와 1% 기준은 별도의 과정식으로 정의하지 않고 검증 절차로만 사용하였다.

Park et al. (2021)은 최종 정량검증 점수 산정에 사용하지 않았다.

## 2.11 재현성

최종 production model은 \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`이며 package SHA-256은

\`a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34\`

이다. 기후 forcing은 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`를 사용하였으며, 21.0-0.0 ka BP의 211개 시점에 대해 static과 dynamic 실험을 동일 forcing으로 수행하였다. 최종 정량검증 대상은 Jang et al. (2011)의 네 LPZ를 100년 모델 출력격자에 대응한 62개 평가시점이다.

## 참고문헌

Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S., & Chappellaz, J. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*, 693-709. https://doi.org/10.1029/96GB02344

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*, 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling*. Doctoral dissertation, Lund University. ISBN 91-7874-089-4.

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*, 8171. https://doi.org/10.1029/2002JD002559

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k: high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales*. CRC for Catchment Hydrology Technical Report 03/3.

Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces and uplift rate in the East Coast of South Korea. *Journal of the Korean Geomorphological Association, 24*, 43-55.

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., & Rossiter, D. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116
