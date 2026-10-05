# 용늪 BIOME4-Pelletier 결합모형 Methods 본문 초안

작성일: 2026-10-06  
상태: **논문 본문용 Methods 초안**  
권위 기준: \`FINAL_METHODS_CANONICAL_20261006_KO.md\`

이 문서는 실제 논문 Methods에 바로 옮길 수 있도록 서술형으로 작성한 초안이다. 수식은 문헌의 과정 구조를 유지하되 논문 전체의 상태변수는 \(z\), \(z_b\), \(H\), \(\tau\)로 통일하였다. Pelletier 계열의 과정식은 서로 대입하여 하나의 통합식으로 만들지 않고 각각 독립적으로 제시한다.

## 2.1 모형 구성과 시간 결합

본 연구에서는 후기 빙기 이후 용늪의 기후, 식생 및 지형의 상호작용을 모의하기 위해 BIOME4 v4.2b2 식생모형과 Pelletier et al. (2013)의 식생-지형 결합 지형발달모형을 연결하였다. 모의기간은 21.0 ka BP부터 현재까지이며, 기후와 식생의 결합 간격은 0.1 kyr로 설정하여 총 211개 시점을 계산하였다.

정적 실험에서는 초기 지표고도와 토심을 전체 기간 동안 고정하고 각 시점의 기후만 BIOME4에 입력하였다. 동적 실험에서는 각 시점에서 BIOME4가 계산한 식생과 수문 상태를 이용해 EEMT와 지상부 생체량 지표를 산정한 뒤 지형발달모형을 100년 동안 적분하였다. 갱신된 지표고도와 토심은 다음 시점의 토양수분 저장량과 뿌리 접근성 계산을 거쳐 BIOME4에 다시 입력하였다. 따라서 동적 실험은 토심과 지형이 식생에 영향을 주고, 식생이 다시 지형발달에 영향을 주는 순환구조를 갖는다.

연대 좌표는 \(t_{\mathrm{BP}}\)로, 정방향 모델 적분시간은 \(\tau\)로 구분하였다. 지표고도는 \(z\), 기반암 또는 풍화전선 고도는 \(z_b\), 토심 또는 레골리스 두께는 \(H\)로 통일하였으며,

\[
\boxed{
H=z-z_b
}
\]

로 정의하였다.

## 2.2 기후자료와 BIOME4 입력

기후 forcing에는 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`를 사용하였다. 이 자료는 CHELSA-TraCE21k/EnviCloud 계열의 월별 최저기온, 최고기온 및 강수량을 21.0-0.0 ka BP에 대해 100년 간격으로 정리한 것이다. CHELSA 원자료의 기온은 Kelvin 단위이므로 월평균기온 \(T_m\)은

\[
T_m
=
\frac{T_{\min,m}+T_{\max,m}}{2}
-
273.15
\]

로 변환하였다. CHELSA 자료에는 별도의 고도감률 보정을 추가하지 않았다.

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

CHELSA-TraCE21k Centennial 자료에 cloud 변수가 없으므로 BIOME4의 복사계산에 필요한 cloud만 Beyer 계열 자료에서 시간 보간하였다. Beyer 자료의 기온과 강수량은 사용하지 않았다. 대기 CO2 농도는 PB4Studio에 포함된 Bereiter 계열 기록을 사용하였다.

식생계산에는 BIOME4 v4.2b2의 native PFT climate limits를 유지하였다. BIOME4는 각 PFT에 대해 기후, CO2와 토양수분 제약 아래에서 NPP와 optimal LAI를 계산한 뒤 PFT 경쟁을 통해 우점 PFT와 biome을 결정한다. 본 연구에서는 토심에 따른 NPP, LAI 또는 FVC의 별도 경험 multiplier를 사용하지 않았으며, 토심 효과는 토양의 available-water storage와 PFT별 뿌리 접근성을 통해서만 BIOME4의 수문계산에 전달하였다.

## 2.3 토심, available-water storage 및 뿌리 접근성

McKenzie et al. (2003)의 profile available water capacity 개념에 따라 깊이별 available water는 \(-10\) kPa와 \(-1.5\) MPa에서의 체적수분함량 차이로 정의하였다.

\[
AWC(\zeta)
=
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\]

여기서 \(\zeta\)는 토양 표면으로부터의 깊이이다. 용늪 SoilGrids profile에서 계산한 깊이별 available-water density를 이용하되 BIOME4의 native 2층 수문구조를 유지하였다. 상층은 0-0.30 m, 하층은 0.30-1.50 m로 두었으며 실제 토심 \(H\)에 따라 저장량을 다음과 같이 계산하였다.

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

이 두 식은 McKenzie et al. (2003)의 profile AWC 개념을 BIOME4의 2층 수문구조에 적용한 본 연구의 구현식이다. BIOME4 수문구조의 상한 때문에 1.50 m보다 깊은 토양은 추가 water store로 사용하지 않았다.

뿌리분포는 BIOME4 v4.2b2의 \`pftpar(pft,6)\`에 저장된 상부 30 cm 누적 뿌리분율을 사용하였다. 이 값을 \(r_{30,p}\)로 표기하였다. McKenzie et al. (2003)의 지수형 깊이 가중함수

\[
f(x)
=
\exp\left(-\frac{x}{X_i}\right)
\]

와 연결하기 위해 PFT별 특성깊이 \(X_p\)를

\[
\boxed{
X_p
=
-\frac{0.30}
{\ln(1-r_{30,p})}
}
\]

로 계산하였다. 이 식은 BIOME4의 상부 30 cm 뿌리분율과 McKenzie의 지수형 깊이감쇠를 연결한 본 연구의 분석적 변환이다.

BIOME4에 사용되는 유효 토심은

\[
D
=
\min[\max(H,0),1.50]
\]

로 제한하였다. 실제 토심에서 접근 가능한 상층과 하층의 뿌리분율은 각각

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

로 계산하였다. BIOME4의 PFT별 root-zone wetness는

\[
\omega_{r,p}
=
R_{\mathrm{top},p}\omega_{\mathrm{top}}
+
R_{\mathrm{bottom},p}\omega_{\mathrm{bottom}}
\]

으로 계산하였다. 얕은 토양에서 \(R_{\mathrm{top},p}+R_{\mathrm{bottom},p}<1\)이 되더라도 두 값을 1로 재정규화하지 않았다. 이는 실제 토심보다 아래에 존재할 뿌리를 얕은 층으로 인위적으로 재배치하지 않기 위함이다.

## 2.4 EEMT

지형발달에 필요한 유효 에너지 및 물질전달량은 Pelletier et al. (2013)의 EEMT 개념을 사용하였다. Pelletier et al. (2013)의 유효강수 에너지와 생물생산 에너지 관계는 각각

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

이며,

\[
EEMT
=
E_{\mathrm{PPT}}
+
E_{\mathrm{BIO}}
\]

로 정의된다. 여기서 \(P_{\mathrm{eff}}=PPT-ET\)이다.

PB4에서는 BIOME4가 제공하는 월별 AET와 탄소 기준 NPP를 이용하여 위 관계를 월별 forcing에 적용하였다.

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

여기서 \(C_w=4186\ {\rm J\,kg^{-1}\,K^{-1}}\), \(h_{\mathrm{BIO}}=22\times10^6\ {\rm J\,kg^{-1}}\)을 사용하였다. \(NPP_C\)는 BIOME4가 출력하는 연간 탄소 NPP이며, \(f_C=0.50\)은 탄소량을 dry biomass로 환산하기 위한 본 연구의 가정이다. 월별 \(R_m-AET_m\) 값은 0으로 절단하지 않았으며 EEMT에도 별도의 상한 또는 하한 clipping을 적용하지 않았다.

## 2.5 BIOME4-derived AGB*

Pelletier et al. (2013)의 사면수송계수에는 AGB가 입력되지만 BIOME4는 total anatomical AGB를 독립적인 상태변수로 직접 출력하지 않는다. 따라서 본 연구에서는 BIOME4의 LAI와 PFT parameter를 이용하여 잎과 살아 있는 변재로 구성된 BIOME4-derived aboveground living biomass proxy \(AGB^*\)를 계산하였다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

잎 건조생체량에는 Reich et al. (1992)의 SLA-life-span 회귀식을 사용하였다.

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

여기서 \(L_{m,p}\)는 BIOME4 v4.2b2의 PFT별 expected leaf longevity이며 단위는 month이다. Reich et al. (1992)의 SLA는 cm\(^2\) g\(^{-1}\) 단위로 정의되므로 계산 단계에서 m\(^2\) kg\(^{-1}\)로 변환하였다. SLA가 leaf area / leaf dry mass이고 LAI가 leaf area / ground area이므로 잎 건조생체량은

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 계산하였다.

변재량은 Haxeltine and Prentice (1996)의 sapwood-LAI 관계

\[
\boxed{
C_s
=
LAI\,C_n
}
\]

를 사용하였다. BIOME4 v4.2b2의 respiration subroutine에서 \`stemcarbon=0.5\`가 sapwood carbon per unit LAI로 사용되므로 해당 source parameter를 \(C_n\)에 적용하였다. 변재 건조생체량은

\[
\boxed{
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
}
\]

로 환산하였다. \(f_C=0.50\)은 EEMT 계산과 동일한 dry-biomass conversion 가정이다. BIOME4 source에서 \`pftpar(pft,10)=2\`로 sapwood respiration이 제거되는 PFT에는 AGB* 계산에서도 변재항을 적용하지 않았다.

\(AGB^*\)는 total anatomical AGB가 아니라 BIOME4에서 직접 추적 가능한 잎과 살아 있는 변재를 이용한 지상부 생체량 proxy이다. 따라서 심재와 BIOME4가 별도 standing stock으로 제공하지 않는 장기 목질부는 포함하지 않았다.

## 2.6 Pelletier 지형발달모형

Pelletier et al. (2013)의 토양생산, 사면수송 및 유수침식 구조를 사용하였다. 원 논문의 과정식은 유지하되 전체 결합모형의 상태변수를 일원화하기 위해 기반암고도는 \(z_b\), 토심은 \(H\), 적분시간은 \(\tau\)로 표기하였다. 각 과정식은 서로 대입하여 하나의 통합식으로 전개하지 않았다.

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

로 계산하며, 토심의 변화는

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

로 계산하였다.

토심에 따른 토양생산률은 Pelletier et al. (2013)의 관계에 따라

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

로 계산하였다. 잠재 토양생산률은 별도 식으로

\[
\boxed{
P_0
=
a\exp(b\,EEMT)
}
\]

를 사용하였다. production 설정에서 \(a=0.037\ {\rm m\,kyr^{-1}}\), \(b=0.030\), \(H_0=0.50\ {\rm m}\), \(\rho_b/\rho_s=1.8\)을 사용하였다.

사면수송에 따른 침식 또는 퇴적은

\[
\boxed{
E_c
=
\nabla\cdot\mathbf q
}
\]

로 나타냈다. 토심의존 비선형 사면수송은

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

로 계산하였다. 수송계수 \(k_d\)는 별도의 관계식

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

으로 계산하였다. 여기서 \(c=0.033\), \(d=0.050\)을 사용하였다. 즉 Pelletier et al. (2013)의 EEMT-AGB 결합구조는 유지하고 AGB 입력만 본 연구의 \(AGB^*\)로 대체하였다. \(k_d\) 식을 사면수송식에 직접 대입하여 전개하지 않았다.

유수침식은

\[
\boxed{
E_f
=
K
\frac{A}{w}
|\nabla z|
}
\]

로 계산하였다. 유로폭과 erodibility는 각각

\[
\boxed{
w=gA^i
}
\]

및

\[
\boxed{
K
=
\frac{K_0}{EEMT}
}
\]

로 별도 계산하였다. production 설정에서 \(K_0=0.020\)을 사용하였다. 실제 PB4 수치구현에서는 \(|\nabla z|\)을 flow-routing 방향의 경사로 평가하였다.

용늪 real DEM에서 비선형 사면수송식을 안정적으로 적분하기 위해 \(S_c=1.50\)을 사용하였다. 이 값은 Pelletier et al. (2013)의 원 실험값이 아니라 용늪 20 m DEM에 대한 수치수렴시험을 통해 채택한 용늪 production 설정이다. 융기율은 현재 production package에서 \(U=0.20\ {\rm m\,kyr^{-1}}\)로 설정되어 있다. 이 값은 현재 코드에 동해안 융기율 참고값으로 기록되어 있으나, 투고본에서는 지역 융기율 문헌을 별도로 연결하여 근거를 명시해야 한다.

## 2.7 수치 적분과 결합 순서

기후와 식생은 100년 간격으로 계산하였지만 지형발달모형은 각 100년 interval 내부에서 adaptive substep으로 적분하였다. 한 interval에서 먼저 현재 \(z\), \(z_b\), \(H\)와 해당 연대의 기후를 이용하여 available-water storage와 PFT별 root accessibility를 계산한 뒤 BIOME4를 실행하였다. 이후 BIOME4의 NPP, AET, LAI와 dominant PFT로부터 EEMT와 \(AGB^*\)를 계산하고, 이 값을 해당 100년 interval의 지형 forcing으로 사용하였다. 지형 adaptive substep 사이에는 BIOME4를 재실행하지 않았다.

기본 explicit timestep은 Pelletier et al. (2013)의 안정성 추정형태를 따라

\[
\Delta\tau
=
0.01
\frac{\Delta x^2}
{2k_{d,\max}}
\]

로 추정하고 필요할 경우 더 작은 substep으로 줄였다. PB4에서는 trial step의 최대 지형변화가 0.025 m를 초과하면 해당 trial을 폐기하고 더 작은 timestep으로 재계산하였다. 0.025 m는 물리 파라미터가 아니라 수치수렴시험으로 정한 허용오차이다.

또한 finite-volume 계산에서 한 substep에 donor cell의 가용 레골리스보다 많은 물질이 유출되지 않도록 공급제약을 적용하였다. 초임계 경사를 포함하는 실제 DEM을 처리하기 위한 threshold-slope adjustment와 open outlet의 fixed base-level boundary도 수치구현에 포함하였다. 이들 처리는 Pelletier의 과정식 자체가 아니라 실제 raster 모형을 안정적으로 적분하기 위한 PB4의 수치구현이다.

## 2.8 식생 결과의 재분류와 Jang et al. (2011) 검증

최종 정량검증에는 Jang et al. (2011)의 네 record인 \`95_01\`, \`95_02\`, \`95_03\`, \`95_04\`를 사용하였다. 100년 간격의 모형 출력과 대응하여 총 62개 시점을 평가하였다.

BIOME4의 native biome 가운데 mixed forest에 해당하는 범주는 검증을 위해 침엽수림, 활엽수림 및 혼효림의 reduced class로 재분류하였다. 이때 활엽수군과 침엽수군에서 각각 가장 높은 잠재 NPP를 갖는 PFT를 비교하였다. 한 식생군의 비율이 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 유지하였다. 이 51% 기준은 BIOME4 내부의 PFT 경쟁이나 생리과정에 사용되는 임계값이 아니라 Jang et al. (2011)과의 비교를 위한 출력 후처리 기준이다.

각 검증시점에서 Jang et al. (2011)이 제시한 식생군이 모의 유역의 유효 격자 가운데 1% 이상에서 출현한 경우 해당 시점을 일치로 판정하였다. 이 1% 기준 역시 식생모형 내부 파라미터가 아니라 공간적으로 이질적인 산지 유역에서 목표 식생군의 존재 여부를 판정하기 위한 검증 기준이다.

최종 Methods와 정량검증에는 Jang et al. (2011)만 사용하였으며 Park et al. (2021)은 검증 점수 산정에 포함하지 않았다.

## 2.9 재현성

최종 production model은 \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`이며 사용한 package의 SHA-256은

\`a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34\`

이다. 기후 forcing은 \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`를 사용하였다. 최종 실행은 21.0-0.0 ka BP의 211개 시점에 대해 동일 forcing으로 static과 dynamic 실험을 수행하였다.

## 본문 작성 시 확인사항

이 초안에서 논문 제출 전 추가 확인이 필요한 사항은 융기율 \(U=0.20\ {\rm m\,kyr^{-1}}\)의 지역 문헌 근거이다. 해당 출처가 확정되면 2.6절의 문헌 검증 필요 문장을 실제 인용문헌으로 교체한다. 나머지 수식은 \`FINAL_METHODS_CANONICAL_20261006_KO.md\`와 동일한 구조를 따른다.
