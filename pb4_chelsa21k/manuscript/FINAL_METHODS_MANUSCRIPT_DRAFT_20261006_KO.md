# 2. 연구방법

작성 기준일: 2026-10-06  
모형: \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`  
이 문서는 논문 본문용 방법론 초안이며, 문헌에서 가져온 식과 본 연구의 결합 및 수치구현을 구분하여 서술한다.

## 2.1 결합모형의 구성과 시간적 결합

본 연구에서는 대암산 용늪의 후기 빙기 이후 식생과 지형의 상호작용을 모의하기 위해 평형 생물지리 및 생지화학 모형인 BIOME4와 식생, 토양생성 및 지형발달을 결합한 Pelletier et al. (2013)의 경관발달모형을 연계하였다. BIOME4는 기후와 토양 조건에 따라 PFT별 탄소 및 물 순환을 계산하고, 각 PFT에서 NPP를 최대화하는 LAI와 PFT 경쟁을 이용하여 잠재식생을 결정한다. BIOME4의 직접적인 모델 계보와 구조는 Kaplan (2001)과 Kaplan et al. (2003)을 따랐다. BIOME4가 계승한 탄소 및 수문 생리구조의 기반은 Haxeltine and Prentice (1996)의 BIOME3에 있다.

모의기간은 21.0 ka BP부터 0.0 ka BP까지로 설정하였다. 기후와 식생의 결합간격은 0.1 kyr로 하여 총 211개 시점을 계산하였다. 연대 좌표는 \(t_{\mathrm{BP}}\)로, 모형의 정방향 적분시간은 \(\tau\)로 구분하였다. 지표고도는 \(z\), 기반암 또는 풍화전선 고도는 \(z_b\), 토심 또는 이동 가능한 레골리스 두께는 \(H\)로 표기하였으며,

\[
\boxed{
H=z-z_b
}
\]

로 정의하였다. 이 표기는 Pelletier et al. (2013)의 \(z=b+h\)와 동일한 상태변수 관계를 유지하면서, Pelletier 원문의 기반암고도 \(b\)와 토양생산 경험계수 \(b\)가 본문에서 중복되는 것을 피하기 위해 기반암고도만 \(z_b\)로 바꾼 것이다.

정적 실험에서는 초기 지형과 토심을 전 기간 동안 고정하고 기후 forcing만 시간에 따라 변화시켰다. 동적 실험에서는 각 100년 시점에서 BIOME4를 실행하여 NPP, AET, LAI와 우점 PFT를 계산하고, 이 결과로부터 EEMT와 \(AGB^*\)를 산정하였다. 이후 동일한 EEMT와 \(AGB^*\)를 해당 100년 구간의 지형발달 forcing으로 사용하여 \(z\), \(z_b\), \(H\)를 갱신하고, 갱신된 토심과 지형을 다음 시점의 BIOME4 계산에 다시 입력하였다. 따라서 동적 실험은 토심 및 지형에서 토양수분과 식생으로 이어지는 경로와 식생에서 지형발달로 되돌아가는 경로를 연속적으로 연결한다.

## 2.2 기후 forcing과 BIOME4 입력

기후 forcing은 CHELSA-TraCE21k를 기반으로 구축한 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`를 사용하였다. CHELSA-TraCE21k는 TraCE-21k를 CHELSA 알고리즘으로 하향화하여 지난 21 ka 동안의 월별 기온과 강수량을 30 arcsec, 약 1 km 공간해상도와 100년 시간간격으로 제공한다 (Karger et al., 2023). 본 연구의 기후 파일은 용늪 지점의 월별 Tmin, Tmax 및 강수량을 21.0-0.0 ka BP의 211개 시점에 대해 저장한 자료이며, 최종 사용 파일의 SHA-256은 \`3f5d249bb59f4163bb0f78f5cb4759972575931bf977b8b2791db497805b0ec9\`이다.

CHELSA 원자료의 Tmin과 Tmax는 Kelvin이므로 월평균기온 \(T_m\)은

\[
T_m
=
\frac{T_{\min,m}+T_{\max,m}}{2}
-
273.15
\]

로 변환하였다. Karger et al. (2023)의 CHELSA-TraCE21k는 고해상도 고지형을 고려해 하향화된 기온 및 강수장을 제공하므로, 본 연구의 production 경로에서는 추가적인 DEM 고도감률 보정을 적용하지 않았다. 즉 이 처리는 CHELSA-TraCE21k 자체의 필수 규칙이 아니라 동일한 지형효과를 중복 적용하지 않기 위한 본 연구의 전처리 선택이다.

BIOME4가 요구하는 absolute minimum temperature는 CHELSA-TraCE21k에 직접 포함되어 있지 않으므로 BIOME4 v4.2b2 원 코드의 관계식

\[
T_{\mathrm{absmin}}
=
0.006T_{\mathrm{cold}}^2
+
1.316T_{\mathrm{cold}}
-
21.9
\]

을 사용하였다. 여기서 \(T_{\mathrm{cold}}\)는 해당 연도의 가장 추운 달의 월평균기온이다. 이 식은 별도로 보정하지 않고 BIOME4 v4.2b2 구현을 그대로 유지하였다 (Kaplan, 2001; BIOME4 v4.2b2 source code).

CHELSA-TraCE21k Centennial forcing에는 BIOME4 복사계산에 필요한 월별 cloud cover가 포함되어 있지 않으므로 cloud 변수만 Beyer et al. (2020)의 후기 제4기 기후자료에서 시간 보간하여 보조 입력으로 사용하였다. Beyer et al. (2020)은 월별 기온, 강수량, cloud cover 등을 포함하는 후기 제4기 기후자료를 제공하지만, 본 연구에서는 이 자료의 기온과 강수량은 사용하지 않았다. 대기 CO2는 PB4Studio에 내장된 Bereiter et al. (2015)의 갱신된 빙핵 CO2 composite를 각 모형 연대에 선형보간하여 사용하였다. Bereiter et al. (2015)은 800 ka CO2 기록을 갱신하면서 최근 연구를 포함한 마지막 빙기 주기의 CO2 자료도 함께 정리하였다.

식생모형은 BIOME4 v4.2b2로 고정하였으며 최종 production에서는 native PFT climate limits를 유지하였다. Kaplan (2001)과 Kaplan et al. (2003)의 BIOME4 구조에 따라 각 PFT의 생육가능성을 기후제약으로 판정하고, 잠재 PFT에 대해 탄소와 물 흐름, NPP 및 optimal LAI를 계산한 뒤 경쟁을 통해 우점 PFT와 biome을 결정하였다. 본 연구에서는 토심에 따라 NPP, LAI 또는 FVC에 별도의 경험적 multiplier를 직접 곱하지 않았다. 토심 변화는 아래에서 설명하는 available-water storage와 PFT별 finite-depth root accessibility를 통해서만 BIOME4 수문 및 수분스트레스 계산에 전달하였다.

## 2.3 토심에 따른 available-water storage와 PFT별 뿌리 접근성

토심에 따른 토양수분 저장량은 McKenzie et al. (2003)의 profile available water capacity 개념을 기반으로 계산하였다. McKenzie et al. (2003)은 토양 profile의 available water capacity를 약 \(-10\) kPa의 field capacity와 \(-1.5\) MPa의 wilting point에서의 체적수분함량 차이로 정의하고, 이를 토양 깊이에 걸쳐 적분하였다. 따라서 깊이 \(\zeta\)에서의 available-water density를

\[
AWC(\zeta)
=
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\]

로 두었다 (McKenzie et al., 2003).

용늪 토양수분 특성은 SoilGrids 2.0의 깊이별 토양정보를 기반으로 구축한 지점 profile을 사용하였다. SoilGrids 2.0은 250 m 공간해상도에서 0-5, 5-15, 15-30, 30-60, 60-100 및 100-200 cm의 표준 깊이구간에 대해 전 지구 토양특성을 제공한다 (Poggio et al., 2021). 본 연구에서 사용한 용늪 지점 profile의 available-water density는 0-0.05 m에서 237 mm m\(^{-1}\), 0.05-0.15 m에서 232 mm m\(^{-1}\), 0.15-0.30 m에서 218 mm m\(^{-1}\), 0.30-0.60 m에서 207 mm m\(^{-1}\), 0.60-1.00 m에서 198 mm m\(^{-1}\), 1.00-2.00 m에서 179 mm m\(^{-1}\)였다. 이 수치들은 SoilGrids 원 논문의 보편적 상수가 아니라 본 연구에서 사용한 용늪 지점 profile의 입력값이다.

BIOME4의 native 2층 수문구조를 유지하기 위해 상층을 0-0.30 m, 하층을 0.30-1.50 m로 구분하였다. 실제 토심 \(H\)에 따른 각 층의 available-water storage는

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

와

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

로 계산하였다. 두 식은 McKenzie et al. (2003)이 BIOME4용으로 직접 제시한 식이 아니라, McKenzie의 profile AWC 정의를 BIOME4 v4.2b2의 2층 수문구조에 적용한 본 연구의 결합식이다. BIOME4 수문구조의 깊이 상한을 유지하기 위해 1.50 m보다 깊은 토양은 추가 water store로 사용하지 않았다.

뿌리의 수직분포에는 Jackson et al. (1996)의 지수형 누적 뿌리분포와 McKenzie et al. (2003)의 깊이가중 개념을 결합하였다. Jackson et al. (1996)은 토양표면에서 깊이 \(d\)까지의 누적 뿌리분율 \(Y\)를

\[
Y(d)
=
1-\beta^d
\]

의 형태로 표현하였다. McKenzie et al. (2003)은 깊이에 따른 식물의 토양수분 이용가능성을

\[
f(x)
=
\exp\left(-\frac{x}{X_i}\right)
\]

형태의 scaling function으로 나타냈으며, \(X_i\)는 그 깊이보다 아래에 약 37%의 뿌리가 존재하는 특성깊이로 해석하였다.

BIOME4 v4.2b2의 \`pftpar(pft,6)\`에 저장된 PFT별 상부 30 cm 누적 뿌리분율을 \(r_{30,p}\)로 두고, 이를 McKenzie 형태의 특성깊이와 일치시키기 위해

\[
\boxed{
X_p
=
-\frac{0.30}
{\ln(1-r_{30,p})}
}
\]

로 변환하였다. 이 식은 Jackson et al. (1996) 또는 McKenzie et al. (2003)의 원식을 그대로 옮긴 것이 아니라 BIOME4의 PFT별 \(r_{30,p}\)와 McKenzie의 지수형 깊이함수를 연결하기 위해 본 연구에서 분석적으로 유도한 관계이다.

BIOME4 수문계산에 사용할 유효 토심은

\[
D
=
\min[\max(H,0),1.50]
\]

로 제한하였다. 실제 토심 내에서 접근 가능한 상층과 하층의 PFT별 뿌리분율은 각각

\[
R_{\mathrm{top},p}
=
1-
\exp
\left[
-\frac{\min(D,0.30)}{X_p}
\right]
\]

와

\[
R_{\mathrm{bottom},p}
=
\begin{cases}
0, & D\le0.30\\
\exp(-0.30/X_p)-\exp(-D/X_p), & D>0.30
\end{cases}
\]

로 계산하였다. 이에 따라 PFT \(p\)가 실제로 이용하는 root-zone wetness는

\[
\omega_{r,p}
=
R_{\mathrm{top},p}\omega_{\mathrm{top}}
+
R_{\mathrm{bottom},p}\omega_{\mathrm{bottom}}
\]

으로 계산하였다. 토양이 얕아 \(R_{\mathrm{top},p}+R_{\mathrm{bottom},p}<1\)이 되더라도 두 값을 1로 재정규화하지 않았다. 이는 실제 토심 아래에 분포했을 뿌리를 얕은 토양층으로 인위적으로 재배치하지 않기 위한 것이다.

## 2.4 EEMT 계산

지형발달에 대한 기후와 생물생산의 영향을 하나의 에너지 변수로 연결하기 위해 Pelletier et al. (2013)의 effective energy and mass transfer, EEMT를 사용하였다. Pelletier et al. (2013)은 유효강수에 의해 전달되는 에너지와 생물생산에 저장되는 에너지를 각각

\[
\boxed{
E_{\mathrm{PPT}}
=
\Delta T C_w P_{\mathrm{eff}}
}
\]

및

\[
\boxed{
E_{\mathrm{BIO}}
=
NPP h_{\mathrm{BIO}}
}
\]

로 정의하고, 두 항의 합을 EEMT로 사용하였다.

\[
EEMT
=
E_{\mathrm{PPT}}
+
E_{\mathrm{BIO}}
\]

여기서 \(P_{\mathrm{eff}}=PPT-ET\), \(C_w\)는 물의 비열, \(h_{\mathrm{BIO}}\)는 biomass의 연소열이다 (Pelletier et al., 2013).

본 연구에서는 BIOME4가 월별 AET와 탄소 기준 연간 NPP를 제공하므로 Pelletier et al. (2013)의 관계를 BIOME4 출력에 맞추어 다음과 같이 계산하였다.

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

여기서 \(T_m\)은 월평균기온, \(R_m\)은 월강수량, \(AET_m\)은 BIOME4의 월 실제증발산, \(NPP_C\)는 g C m\(^{-2}\) yr\(^{-1}\) 단위의 BIOME4 NPP이다. \(C_w=4186\ {\rm J\,kg^{-1}\,K^{-1}}\)와 \(h_{\mathrm{BIO}}=22\times10^6\ {\rm J\,kg^{-1}}\)을 사용하였다 (Pelletier et al., 2013). BIOME4가 탄소질량으로 NPP를 출력하므로 dry biomass로 환산하기 위한 탄소분율은 \(f_C=0.50\)으로 가정하였다. 이 월별 합산식은 Pelletier et al. (2013)의 별도 원식이 아니라 그 논문의 EEMT 정의를 본 연구의 BIOME4 forcing에 적용한 구현식이다.

최종 production 코드에서는 \(R_m-AET_m\)이 음수가 되는 경우 이를 0으로 강제하지 않았으며, 계산된 EEMT에도 별도의 경험적 최소값 또는 최대값 clipping을 적용하지 않았다. 노출 기반암 셀에서는 BIOME4 식생계산을 우회하여 NPP와 식생 AET를 0으로 두되 강수와 기온에 따른 물리적 EEMT 항은 유지하였다.

## 2.5 BIOME4-derived AGB*

Pelletier et al. (2013)의 사면수송식에서는 AGB가 \(k_d\)를 조절하는 식생변수로 사용된다. 그러나 BIOME4 v4.2b2는 total anatomical AGB를 독립적인 standing stock으로 직접 출력하지 않는다. 따라서 본 연구에서는 BIOME4가 계산하는 LAI와 PFT별 leaf longevity, 그리고 BIOME4 source code의 sapwood carbon 관계를 이용하여 잎과 살아 있는 변재로 구성된 BIOME4-derived aboveground living biomass proxy \(AGB^*\)를 정의하였다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

잎 건조생체량은 Reich et al. (1992)의 leaf life-span과 SLA 관계를 이용하였다. Reich et al. (1992)의 전체 LEAVES 자료에 대한 원 회귀식은

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

이며, 원 논문에서 \(L_{m,p}\)는 month, \(SLA_p\)는 cm\(^2\) g\(^{-1}\) 단위이다 (Reich et al., 1992). SLA는 leaf area / leaf dry mass이므로, 계산 단계에서 SLA를 m\(^2\) kg\(^{-1}\)로 단위변환한 뒤

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 잎 건조생체량을 계산하였다. Reich et al. (1992)의 회귀식을 대수적으로 전개해 얻어지는 소수계수는 독립적인 경험계수가 아니므로 본문식에는 사용하지 않았다.

변재량은 BIOME3에서 사용된 sapwood-LAI 관계의 원식

\[
\boxed{
C_s
=
LAI C_n
}
\]

을 따랐다 (Haxeltine and Prentice, 1996). 이 관계를 별도의 BIOME3 식생모형으로 결합한 것은 아니며, BIOME4에 계승된 sapwood와 LAI 관계의 문헌적 원전으로 사용하였다. BIOME4 v4.2b2의 respiration source code는 \`stemcarbon=0.5\`를 sapwood carbon per unit LAI로 사용하므로, sapwood respiration이 활성인 PFT에 대해 \(C_n=0.5\) kg C m\(^{-2}\) LAI\(^{-1}\)를 적용하였다. 변재의 dry biomass는

\[
\boxed{
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
}
\]

로 계산하였고, EEMT 계산과 동일하게 \(f_C=0.50\)을 사용하였다. BIOME4 v4.2b2에서 \`pftpar(pft,10)=2\`인 PFT는 source code에서 sapwood respiration이 제거되므로 해당 PFT의 \(AGB^*\)에서도 변재 항을 포함하지 않았다.

최종 셀 단위 \(AGB^*\)는 BIOME4 경쟁 후 선택된 우점 PFT \(p^*\)의 LAI와 parameter를 사용하여 계산하였다. 따라서 \(AGB^*\)는 잎과 살아 있는 변재를 포함하지만, 심재와 BIOME4가 별도 standing stock으로 제공하지 않는 장기 목질부를 포함하는 total anatomical AGB와는 구분된다.

## 2.6 토양생산과 지형발달

식생 및 기후변화가 지형발달에 미치는 영향은 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 slope-wash/fluvial erosion 구조를 사용하여 계산하였다. 원 논문의 과정구조는 유지하되 전체 결합모형에서 상태변수를 일관되게 사용하기 위해 Pelletier et al. (2013)의 토심 \(h\), 기반암고도 \(b\), 시간 \(t\)를 각각 \(H\), \(z_b\), \(\tau\)로 표기하였다. 과정식은 서로 대입해 하나의 통합식으로 만들지 않고 각 과정별로 분리하여 사용하였다.

Pelletier et al. (2013)의 Eq. (6)-(8)에 대응하는 상태변수와 질량수지는 다음과 같다.

\[
\boxed{
z=z_b+H
}
\]

\[
\boxed{
\frac{\partial z_b}{\partial\tau}
=
U
-
\frac{P}{\cos\theta}
}
\]

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

여기서 \(U\)는 융기율, \(P\)는 기반암에서 레골리스로의 토양생산 또는 풍화전선 후퇴율, \(\rho_b/\rho_s\)는 기반암과 레골리스의 밀도비, \(E\)는 지표물질의 순 제거항이다.

토양생산률은 Pelletier et al. (2013)의 Eq. (9)를 따라

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

로 계산하였다. 잠재 토양생산률 \(P_0\)는 Eq. (10)을 별도 식으로 사용하였다.

\[
\boxed{
P_0
=
a\exp(b\,EEMT)
}
\]

\(P_0\)를 위 토심감쇠식에 대입하여 하나의 통합식으로 재작성하지 않았다. production에서 \(a=0.037\ {\rm m\,kyr^{-1}}\), \(b=0.030\ {\rm m^2\,yr\,MJ^{-1}}\), \(H_0=0.50\ {\rm m}\), \(\rho_b/\rho_s=1.8\)을 사용하였다. 이 가운데 \(a\)와 \(b\)는 Pelletier et al. (2013)이 남부 애리조나의 화강암질 sky-island 환경에 대해 사용한 경험계수이며, 원 논문도 동일 암종 내에서도 절리밀도 등의 차이에 따라 이 관계가 보편적이지 않을 수 있음을 명시하였다. 본 연구에서는 이 계수들을 Jang et al. (2011)의 식생자료에 맞추어 재보정하지 않고 Pelletier et al. (2013)의 Table 1 값을 그대로 이식하였다.

사면물질수송에 따른 침식 및 퇴적항은 Pelletier et al. (2013)의 Eq. (11)에 따라

\[
\boxed{
E_c
=
\nabla\cdot\mathbf q
}
\]

로 나타냈다. 실제 사용한 토심의존 비선형 사면수송은 Eq. (14)의 구조를 유지하여

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

로 계산하였다. 수송계수 \(k_d\)는 Pelletier et al. (2013)의 Eq. (15)를 별도로 적용하였다.

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

여기서 \(c=0.033\)과 \(d=0.050\)은 Pelletier et al. (2013)의 Table 1 값을 유지하였다. 원 논문의 Eq. (15)는 \(AGB\)를 사용하지만, 본 연구에서는 이 입력만 BIOME4-derived \(AGB^*\)로 대체하였다. \(k_d\)를 \(\mathbf q\) 식에 대입하여 전개하지 않았다.

Slope-wash/fluvial erosion은 Pelletier et al. (2013)의 Eq. (16)을 따라

\[
\boxed{
E_f
=
K
\frac{A}{w}
|\nabla z|
}
\]

로 계산하였다. 여기서 \(A\)는 기여면적, \(w\)는 유효 유로폭이다. 유로폭은 Eq. (17),

\[
\boxed{
w
=
gA^i
}
\]

로 계산하고, 유수침식계수는 Eq. (18),

\[
\boxed{
K
=
\frac{K_0}{EEMT}
}
\]

를 별도로 적용하였다. Pelletier et al. (2013)의 Table 1에서 \(g=0.005\), \(i=0.5\), \(K_0=0.020\ {\rm m^2\,MJ^{-1}}\)가 사용되었으며, 본 production에서도 해당 Pelletier 계열 설정을 유지하였다. 원 연구의 \(K_0=0.020\)은 독립적으로 측정된 상수가 아니라 EEMT \(=10\ {\rm MJ\,m^{-2}\,yr^{-1}}\) 조건에서 관측된 mean distance-to-valley를 재현하도록 trial-and-error로 정해진 값이었다 (Pelletier et al., 2013). 따라서 본 연구에서 \(K_0\)의 사용은 용늪에서 새로 보정된 값이 아니라 원 연구지역의 계수를 전이한 것이다. 노출 기반암의 slope-wash/fluvial erodibility는 레골리스보다 작게 두었으며, Pelletier et al. (2013)의 상대 erodibility ratio \(F=10\) 설정을 사용하였다.

임계경사 \(S_c\)는 예외적으로 Pelletier et al. (2013)의 기본값을 그대로 사용하지 않았다. 원 연구는 unconsolidated material의 일반적인 angle of repose에 근거하여 \(S_c=0.7\)을 사용하고 \(S_c=0.9\)를 민감도 실험에 사용하였다. 본 연구에서는 용늪 20 m real-DEM의 초임계 경사와 수치수렴성을 고려한 별도 시험을 통해 \(S_c=1.50\)을 production 설정으로 사용하였다. 따라서 \(S_c=1.50\)은 Pelletier et al. (2013)의 원 파라미터가 아니라 용늪 raster 구현의 수치설정이다.

융기율은 production configuration에서 \(U=0.20\ {\rm m\,kyr^{-1}}\)을 사용하였다. 이 값은 현재 PB4 source에 동해안 융기율 참고값으로 기록되어 있으나, 보존된 project source audit만으로는 해당 수치를 직접 뒷받침하는 지역 지질학 문헌을 확인하지 못하였다. 따라서 투고본에서는 이 값에 대한 대암산 또는 한반도 동부 산지의 독립적인 융기율 문헌을 추가하여 근거를 보강해야 한다.

## 2.7 수치 적분과 operator splitting

기후와 BIOME4는 100년 간격으로 갱신하였으나, 지형발달 계산은 각 100년 coupling interval 안에서 adaptive substep으로 적분하였다. 각 시점에서 먼저 현재 \(z\), \(z_b\), \(H\)와 해당 \(t_{\mathrm{BP}}\)의 기후를 이용해 available-water storage와 PFT별 root accessibility를 계산한 뒤 BIOME4를 실행하였다. 이어서 BIOME4의 NPP, AET, LAI 및 우점 PFT로 EEMT와 \(AGB^*\)를 계산하였다. 이렇게 얻은 EEMT와 \(AGB^*\)는 다음 100년의 지형계산 동안 고정 forcing으로 사용하였으며 geomorphic substep마다 BIOME4를 재실행하지 않았다.

Pelletier et al. (2013)은 명시적 수치해법의 안정성을 위해 timestep을 충분히 작게 선택하고 필요할 경우 감소시키는 방식을 사용하였다. PB4의 기본 안정 timestep은 동일한 형태를 따라

\[
\Delta\tau
=
0.01
\frac{\Delta x^2}
{2k_{d,\max}}
\]

로 추정하고, 실제 trial에서 변화량이 허용범위를 넘으면 timestep을 줄여 동일한 accepted state에서 다시 계산하였다. PB4의 production tolerance는 한 trial에서 hillslope, fluvial 또는 threshold adjustment에 의해 발생하는 최대 지형변화 0.025 m로 설정하였다. Pelletier et al. (2013)은 동적 timestep 감소의 개념을 제시하지만 0.025 m라는 수치를 제시하지 않았으므로, 이 값은 물리 파라미터가 아니라 용늪 20 m DEM에 대한 convergence audit에서 채택한 수치오차 허용기준이다.

사면수송은 Pelletier et al. (2013)의 Eq. (20)-(22)에 대응하는 face flux와 질량보존형 explicit update로 계산하였다. 다만 실제 raster에서 음의 토심이 발생하지 않도록 donor cell이 보유한 이동가능 레골리스보다 많은 물질을 한 substep에 배출하지 못하게 finite-volume supply/positivity constraint를 적용하였다. 또한 초기 실제 DEM에 \(S_c\) 이상의 경사가 존재하는 경우 비선형식의 특이점을 직접 regularize하지 않고 별도의 threshold-slope adjustment로 처리하였다. 유역의 open outlet은 fixed base-level boundary로 유지하였고, adaptive substep 사이의 지형 상태는 float64로 보존하였다. 이들 처리는 Pelletier et al. (2013)의 새로운 물리과정으로 간주하지 않고 실제 DEM에서 원 과정식을 안정적으로 적분하기 위한 PB4의 수치구현으로 구분하였다.

## 2.8 식생 재분류와 고식생 검증

모형의 후기 홀로세 식생변화는 용늪 퇴적물의 화분분석을 수행한 Jang et al. (2011)을 이용하여 검증하였다. Jang et al. (2011)은 180 cm 깊이의 퇴적물에서 61개 화분시료와 5개 방사성탄소 연대시료를 분석하고 약 5.9 ka BP 이후의 식생사를 네 개의 local pollen zone으로 구분하였다. LPZ I은 5.9-4.8 ka BP의 냉온대 중부 및 산지 낙엽활엽수림, LPZ II는 4.8-3.4 ka BP의 냉온대 북부 및 고산성 침엽수-낙엽활엽수 혼효림, LPZ III은 3.4-0.39 ka BP의 냉온대 중부 및 산지 낙엽활엽수림, LPZ IV는 0.39 ka BP부터 현재까지의 낙엽활엽수-침엽수 혼효림으로 해석되었다 (Jang et al., 2011).

본 연구에서는 이 네 LPZ의 연대구간과 식생유형을 모형의 0.1 kyr 출력시간에 대응시켜 검증하였다. Jang et al. (2011)의 원자료가 62개 화분시료를 의미하는 것은 아니며, 본 연구의 \(n=62\)는 네 LPZ 연대구간을 100년 간격 모형 출력에 대응시킨 검증 시점의 수이다. 최종 corrected reduced mapping은 95_01을 낙엽활엽수림, 95_02를 혼효림, 95_03을 낙엽활엽수림, 95_04를 혼효림으로 두었다.

BIOME4의 출력은 Jang et al. (2011)의 식생유형과 비교할 수 있도록 reduced class로 후처리하였다. 침엽수군은 BIOME4 PFT 5-7, 활엽수군은 PFT 2-4, 개방식생군은 PFT 8-13으로 묶었다. BIOME4의 mixed biome에서는 활엽수군과 침엽수군 가운데 각 군에서 가장 높은 잠재 NPP를 갖는 PFT를 비교하여 어느 한쪽이 두 군의 합 중 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 유지하였다. 이 51% 기준은 BIOME4의 생리과정이나 PFT 경쟁에 사용되는 내부 임계값이 아니라 화분자료와 비교하기 위한 출력 재분류 규칙이다.

각 100년 검증시점에서 Jang et al. (2011)이 제시한 목표 식생군이 모의 유역 내 유효 격자의 1% 이상에서 출현한 경우 해당 시점을 일치로 판정하였다. 1% 기준 역시 BIOME4의 내부 파라미터가 아니라 유역 내 공간적으로 제한된 식생군의 존재를 판정하기 위한 본 연구의 검증규칙이다. 최종 정량검증에는 Jang et al. (2011)만 사용하였으며 Park et al. (2021)은 최종 검증점수 산정에 포함하지 않았다. 검증 정확도 자체는 Results에서 제시하였다.

## 2.9 재현성 및 최종 실행환경

최종 production model은 \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`이며 최종 package의 SHA-256은 \`a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34\`이다. 기후 forcing은 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`를 사용하였고, 21.0-0.0 ka BP를 0.1 kyr 간격으로 계산하여 static과 dynamic 각각 211개 시점을 생성하였다. 식생 코어는 BIOME4 v4.2b2의 native climate limits를 사용하였으며, 토심-수문 coupling은 McKenzie et al. (2003)의 AWC 및 root-depth 개념과 Jackson et al. (1996)의 뿌리분포를 BIOME4 수문구조에 결합한 production 경로를 사용하였다.

## 참고문헌

Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S., & Chappellaz, J. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*(3), 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling* [Doctoral dissertation, Lund University]. ISBN 91-7874-089-4. https://lup.lub.lu.se/search/publication/3bfcb2f2-dec3-40a3-a6d3-8764f660ce56

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., Cramer, W., Matveyeva, N. V., McGuire, A. D., Murray, D. F., Razzhivin, V. Y., Smith, B., Walker, D. A., Anderson, P. M., Andreev, A. A., Brubaker, L. B., Edwards, M. E., & Lozhkin, A. V. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k: High-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology. https://www.ewater.org.au/archive/crcch/overview/archive/pubs/pdfs/technical200303.pdf

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., & Rossiter, D. (2021). SoilGrids 2.0: Producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365-392. https://doi.org/10.2307/2937116

## 편집 메모

투고 전 반드시 해결할 항목은 \(U=0.20\ {\rm m\,kyr^{-1}}\)의 지역 지질학적 문헌 근거이다. 또한 유수침식의 \(g\), \(i\), \(F\)는 Pelletier et al. (2013) 원문 Table 1과 project equation guide에서 동일값 유지가 확인되었으나, 최종 binary package의 해당 config 선언부를 제출 전 한 번 더 직접 대조하는 것이 바람직하다. 이 메모는 투고본에서 삭제한다.
