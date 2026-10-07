# 2. 연구방법

## 2.1 VeSLEM의 구성과 시간결합

본 연구에서는 21.0 ka BP 이후의 기후변화에 따른 식생, 토양 및 지형의 장기 상호작용을 모의하기 위하여 평형 식생모델 BIOME4 v4.2b2와 Pelletier et al. (2013)의 수치지형발달모델을 결합한 식생-토양-지형발달모델(Vegetation-Soil-Landscape Evolution Model, VeSLEM)을 구축하였다. BIOME4는 월별 기후, 대기 CO2 및 토양수분 조건을 이용하여 식물 기능형(Plant Functional Type, PFT)별 NPP와 LAI를 계산하고, PFT 간 경쟁을 통해 잠재 식생을 결정한다(Kaplan, 2001; Kaplan et al., 2003). VeSLEM에서는 BIOME4 v4.2b2의 PFT별 기후한계를 적용하고, 토심의 영향은 토양수분 저장량과 PFT별 뿌리 접근성의 변화를 통해 식생계산에 반영하였다.

분석기간은 21.0 ka BP부터 0.0 ka BP까지로 설정하였으며, 식생모델과 지형발달모델의 결합간격은 0.1 kyr로 설정하였다. 이에 따라 식생과 기후 상태는 211개 시점에서 계산하였고, 인접한 시점 사이의 지형발달은 210개의 0.1 kyr 구간으로 계산하였다. 각 구간의 시작에서 해당 시점의 기후와 토심을 이용하여 토양수분 저장량과 PFT별 뿌리 접근성을 산정한 뒤 BIOME4를 실행하였다. BIOME4에서 산출된 NPP와 실제증발산량(Actual Evapotranspiration, AET)을 이용하여 유효 에너지 및 물질 전달량(Effective Energy and Mass Transfer, EEMT)을 계산하고, LAI와 우점 PFT를 이용하여 지상부 생물량 대리변수 AGB*를 계산하였다. EEMT와 AGB*는 같은 0.1 kyr 구간의 지형발달 계산에 사용하였으며, 구간 말에 갱신된 토심과 기반암고도는 다음 시점의 상태변수로 전달하였다.

## 2.2 공간자료와 초기조건

고도자료는 국토정보플랫폼에서 제공하는 수치지형도를 이용하였다. QGIS 3.44.5에서 역거리가중법(Inverse Distance Weighting, IDW)을 이용하여 10 m 해상도의 연속 고도면을 구축하고, GRASS GIS의 `r.watershed`를 이용하여 대암산 용늪을 포함하는 소유역을 추출하였다. 이후 고도, 토심 및 토양 관련 공간자료의 좌표계를 Korea 2000/Central Belt 2010(EPSG:5187)으로 통일하고 20 m 격자로 리샘플링하여 VeSLEM의 계산격자를 구축하였다.

유역경계는 지정한 단일 유출구만 열린 경계로 설정하고 나머지 경계는 닫힌 경계로 처리하였다. D8 흐름방향 계산에서는 지정 유출구에서만 유역 외부로의 유출을 허용하였으며, 다른 경계셀에서는 유역 외부로 향하는 흐름을 허용하지 않았다. 사면 물질수송도 계산영역 내부의 인접 셀 사이에서만 계산하였다. D8 흐름계산에 앞서 싱크 채우기를 적용하여 유역 내부의 폐쇄된 흐름경로를 제거하였다.

초기 토심은 ISRIC SoilGrids의 기반암 깊이 자료 `BDRICM_M_1km_ll`을 이용하였다(Hengl et al., 2017; Shangguan et al., 2017). 토양수분 저장량 계산에는 용늪 지점(128.1236°E, 38.2153°N)의 SoilGrids 수분특성 자료를 이용하였다. 10 kPa와 1500 kPa에서의 체적수분함량 차이에 해당하는 가용수분밀도는 0-0.05 m에서 237 mm m^-1, 0.05-0.15 m에서 232 mm m^-1, 0.15-0.30 m에서 218 mm m^-1, 0.30-0.60 m에서 207 mm m^-1, 0.60-1.00 m에서 198 mm m^-1, 1.00-2.00 m에서 179 mm m^-1을 사용하였다(Turek et al., 2023). BIOME4의 수문계산에는 최대 1.50 m까지의 토양만 포함하였다.

토성자료는 BIOME4의 토성별 수리전도도를 결정하는 데 사용하였다. 연구유역의 유효격자는 모두 BIOME4의 texture class 2로 분류되었으며, 토양수분 저장량은 이 토성등급으로부터 재추정하지 않고 앞서 제시한 깊이별 체적수분함량 자료를 이용하여 계산하였다.

## 2.3 기후 및 대기 CO2 자료

기온과 강수량은 CHELSA-TraCE21k의 월별 자료를 사용하였다(Karger et al., 2023). CHELSA-TraCE21k는 지난 21 kyr에 대해 100년 간격의 월별 기온과 강수량을 1 km 공간해상도로 제공한다. 각 시점의 월평균기온은 월별 최저기온과 최고기온의 평균으로 계산하고 Kelvin에서 °C로 변환하였다.

식 (1)

```
T_m={(T_{min,m}+T_{max,m}) OVER 2}-273.15
```

여기서 \(T_m\)은 월 \(m\)의 평균기온이며, \(T_{min,m}\)과 \(T_{max,m}\)은 각각 월별 최저기온과 최고기온이다. 월별 기온과 강수량은 각 시점에서 유역 내 모든 유효격자에 동일하게 부여하였다. CHELSA-TraCE21k의 기온은 지형효과가 반영된 하향화 자료를 사용하였으며 별도의 고도감률 보정은 적용하지 않았다. BIOME4의 광환경 계산에 필요한 운량(cloudiness)은 Beyer et al. (2020)의 후기 제4기 기후자료에서 추출하여 시간축에 맞게 선형보간하였다. 대기 CO2 농도는 Bereiter et al. (2015)의 Antarctic composite를 각 분석시점에 선형보간하여 사용하였다.

BIOME4에서 PFT의 저온한계 판정에 사용하는 절대최저기온은 v4.2b2의 회귀관계를 이용하였다.

식 (2)

```
T_{absmin}=0.006 T_{cold}^2+1.316 T_{cold}-21.9
```

여기서 \(T_{absmin}\)은 절대최저기온의 추정값이며, \(T_{cold}\)는 가장 추운 달의 월평균기온이다.

## 2.4 토심에 따른 토양수분 저장량

토심에 따른 가용수분 저장량은 McKenzie et al. (2003)의 토양단면 가용수분용량(profile available water capacity) 개념을 이용하여 계산하였다. 깊이 \(zeta\)에서의 가용수분 체적비 \(Delta theta_{AW}\)는 10 kPa와 1500 kPa에서의 체적수분함량 차이로 정의하였다.

식 (3)

```
Delta theta_{AW}(zeta)=theta_{-10}(zeta)-theta_{-1500}(zeta)
```

여기서 \(theta_{-10}\)과 \(theta_{-1500}\)은 각각 10 kPa와 1500 kPa에서의 체적수분함량이다. BIOME4의 수문구조에 따라 토양층은 상층 0-0.30 m와 하층 0.30-1.50 m로 구분하고, 현재 토심 \(H\) 안에 존재하는 부분만 적분하였다. 상층과 하층의 가용수분 저장량은 각각 다음과 같이 계산하였다.

식 (4)

```
W_{top}(H)=1000 INT _0^{min(H,0.30)} Delta theta_{AW}(zeta) d zeta
```

식 (5)

```
W_{bottom}(H)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} Delta theta_{AW}(zeta) d zeta
```

여기서 \(W_{top}\)과 \(W_{bottom}\)은 각각 상층과 하층의 가용수분 저장량(mm)이다. 두 식은 McKenzie et al. (2003)의 토양단면 가용수분 개념을 BIOME4의 2층 수문구조와 시간에 따라 변화하는 토심에 적용한 것이다.

## 2.5 PFT별 뿌리 접근성

토심에 따라 각 PFT가 접근할 수 있는 토양수분이 달라지도록 뿌리의 수직분포를 고려하였다. 누적 뿌리분율은 Gale and Grigal (1987)이 제시하고 Jackson et al. (1996)이 전지구 생물군계에 적용한 관계를 이용하였다.

식 (6)

```
Y(d)=1-beta^d
```

여기서 \(Y(d)\)는 지표에서 깊이 \(d\)까지 존재하는 누적 뿌리분율이며, \(beta\)는 뿌리 수직분포계수이다. BIOME4 v4.2b2의 PFT별 상부 0.30 m 누적 뿌리분율을 \(r_{30,p}\)로 정의하였다.

McKenzie et al. (2003)의 깊이에 따른 뿌리 가중함수는 다음과 같다.

식 (7)

```
f(x)=exp(-{x OVER X_i})
```

여기서 \(X_i\)는 깊이 \(X_i\) 아래에 약 37%의 뿌리가 존재하도록 하는 특성깊이이다. BIOME4의 PFT별 \(r_{30,p}\)와 식 (7)의 지수분포가 상부 0.30 m에서 일치하도록 PFT별 특성깊이 \(X_p\)를 다음과 같이 계산하였다.

식 (8)

```
X_p=-{0.30 OVER ln(1-r_{30,p})}
```

BIOME4에 적용하는 유효 토심 \(D\)는 다음과 같이 정의하였다.

식 (9)

```
D=min(max(H,0),1.50)
```

현재 토심에서 접근 가능한 상층과 하층의 뿌리분율은 각각 다음과 같이 계산하였다.

식 (10)

```
R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})
```

식 (11)

```
R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}
```

PFT별 근권 토양수분상태는 각 수문층의 토양수분상태를 접근 가능한 뿌리분율로 가중하여 계산하였다.

식 (12)

```
omega_{r,p}=R_{top,p} omega_{top}+R_{bottom,p} omega_{bottom}
```

여기서 \(omega_{top}\)과 \(omega_{bottom}\)은 각각 BIOME4 상층과 하층의 토양수분상태이다. 접근 가능한 뿌리분율은 실제 토심까지만 적분하였으므로 얕은 토양에서는 \(R_{top,p}+R_{bottom,p}\)이 1보다 작을 수 있으며, 이를 통해 유한 토심에 따른 뿌리 접근성 감소를 수분스트레스 계산에 반영하였다.

토심이 0인 노출 기반암 셀에서는 식생을 배치하지 않고 NPP, AET 및 AGB*를 0으로 두었다. 이 경우 EEMT의 생물생산항은 0이며, 강수에 의한 에너지항은 AET가 0인 조건에서 계산하였다.

## 2.6 EEMT 산정

식생과 수문조건을 지형발달 과정에 연결하기 위하여 Pelletier et al. (2013)의 EEMT를 이용하였다. 유효강수에 의해 토양계로 전달되는 에너지와 생물생산에 저장되는 에너지는 각각 다음과 같다.

식 (13)

```
E_{PPT}=Delta T C_w P_{eff}
```

식 (14)

```
E_{BIO}=NPP h_{BIO}
```

EEMT는 두 성분의 합으로 계산하였다.

식 (15)

```
EEMT=E_{PPT}+E_{BIO}
```

여기서 \(P_{eff}=PPT-ET\), \(C_w=4186\) J kg^-1 K^-1, \(h_{BIO}=22 TIMES 10^6\) J kg^-1이다(Pelletier et al., 2013). 본 연구에서는 BIOME4의 월별 AET와 연간 carbon NPP를 이용하여 EEMT를 다음과 같이 계산하였다.

식 (16)

```
EEMT={C_w OVER 10^6} SUM _{m=1}^{12} Delta T_m (R_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}
```

여기서 \(Delta T_m\)은 월평균기온을 °C로 표현한 값, \(R_m\)은 월강수량(mm), \(AET_m\)은 월 실제증발산량(mm), \(NPP_C\)는 BIOME4의 연간 NPP(g C m^-2 yr^-1)이며, \(f_C=0.50\)은 건조생체량에서 탄소가 차지하는 질량분율이다. 1 mm의 물은 1 kg m^-2에 해당하므로 첫 번째 항은 MJ m^-2 yr^-1 단위로 계산하였다. 두 번째 항에서는 carbon NPP를 kg dry biomass m^-2 yr^-1로 변환한 뒤 생물생산 에너지로 환산하였다.

## 2.7 BIOME4 기반 지상부 생물량 대리변수

Pelletier et al. (2013)의 사면수송계수에는 AGB가 포함되지만, BIOME4 v4.2b2는 전체 지상부 생물량을 하나의 저장량으로 출력하지 않는다. 따라서 우점 PFT의 optimal LAI로부터 잎과 살아 있는 변재의 건조생체량을 계산하고 이를 합하여 지상부 생물량 대리변수 AGB*를 정의하였다. 격자의 우점 PFT를 \(p^*\)라고 하면 다음과 같다.

식 (17)

```
AGB^*=B_{leaf,dry,p^*}+B_{sapwood,dry,p^*}
```

잎 건조생체량은 Reich et al. (1992)의 잎수명과 비엽면적(Specific Leaf Area, SLA)의 관계를 이용하였다.

식 (18)

```
log_{10}(SLA_p)=2.44-0.43 log_{10}(L_{m,p})
```

여기서 \(L_{m,p}\)는 PFT \(p\)의 잎수명(month)이다. SLA를 cm^2 g^-1에서 m^2 kg^-1로 변환한 뒤 잎 건조생체량을 다음과 같이 계산하였다.

식 (19)

```
B_{leaf,dry,p}={LAI_p OVER SLA_p}
```

변재 탄소량은 Haxeltine and Prentice (1996)의 sapwood-LAI 관계를 이용하였다.

식 (20)

```
C_{s,p}=LAI_p C_n
```

여기서 \(C_{s,p}\)는 변재 탄소량(kg C m^-2), \(C_n\)은 단위 LAI당 변재 탄소량이다. BIOME4 v4.2b2의 \(C_n=0.5\) kg C m^-2 값을 적용하였으며, 변재 건조생체량은 다음과 같이 계산하였다.

식 (21)

```
B_{sapwood,dry,p}={C_{s,p} OVER f_C}
```

변재항은 BIOME4에서 sapwood respiration을 계산하는 PFT에만 적용하였다. 따라서 AGB*는 우점 PFT의 잎과 살아 있는 변재로 구성된 지상부 생물량 대리변수이며, 전체 해부학적 AGB를 의미하지 않는다.

## 2.8 지형발달 과정

지형발달은 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 유수침식 과정을 이용하여 계산하였다. 지표고도 \(z\)는 기반암 또는 풍화전선 고도 \(z_b\)와 토심 \(H\)의 합으로 정의하였다.

식 (22)

```
z=z_b+H
```

기반암 또는 풍화전선 고도의 변화는 다음과 같이 계산하였다.

식 (23)

```
{PARTIAL z_b OVER PARTIAL tau}=U-{P OVER cos theta}
```

토심의 변화는 다음과 같이 계산하였다.

식 (24)

```
{PARTIAL H OVER PARTIAL tau}={rho_b OVER rho_s}{P OVER cos theta}-E
```

여기서 \(tau\)는 정방향 적분시간, \(U\)는 지역 융기율, \(P\)는 토양생산률, \(rho_b/rho_s\)는 기반암과 토양의 밀도비, \(theta\)는 사면각, \(E\)는 침식 및 물질수송에 따른 순 토양제거율이다.

### 2.8.1 토양생산

토심에 따른 토양생산률은 다음과 같이 계산하였다.

식 (25)

```
P=P_0 exp(-{H cos theta OVER H_0})
```

잠재 토양생산률 \(P_0\)는 EEMT의 함수로 계산하였다.

식 (26)

```
P_0=a exp(b EEMT)
```

\(a=0.037\) m kyr^-1, \(b=0.030\) (MJ m^-2 yr^-1)^-1, \(H_0=0.50\) m, \(rho_b/rho_s=1.8\)을 사용하였다(Pelletier et al., 2013).

### 2.8.2 비선형 사면수송

사면수송에 따른 침식 또는 퇴적은 토사유속의 발산으로 계산하였다.

식 (27)

```
E_c=nabla BULLET q
```

토심과 임계경사를 고려한 비선형 사면수송은 다음과 같이 계산하였다.

식 (28)

```
q=-{k_d H cos theta nabla z OVER {1-({|nabla z| OVER S_c})^2}}
```

여기서 \(q\)는 사면방향 토사유속, \(S_c\)는 임계경사, \(k_d\)는 사면수송계수이다. \(k_d\)는 EEMT와 AGB*의 함수로 계산하였다.

식 (29)

```
k_d=c EEMT+d AGB^*
```

\(c=0.033\) m kyr^-1 (MJ m^-2 yr^-1)^-1, \(d=0.050\) m kyr^-1 (kg m^-2)^-1을 사용하였다(Pelletier et al., 2013).

임계경사 \(S_c\)는 20 m DEM을 이용한 수치수렴시험을 통해 1.50으로 설정하였다. 초기 최대 cardinal-face slope는 1.332였으며 \(S_c=1.50\)에서 초기 초임계경사가 발생하지 않았다. 또한 1 kyr 시험에서 지형변화 허용오차를 0.025 m에서 0.0125 m로 절반으로 줄였을 때 최대 토심 차이는 0.008139 m로 나타났다.

### 2.8.3 유수침식

유수에 의한 사면 및 하천침식률은 다음과 같이 계산하였다(Pelletier et al., 2013).

식 (30)

```
E_f=K {A OVER w}|nabla z|
```

여기서 \(A\)는 기여면적, \(w\)는 유효 유로폭, \(K\)는 침식계수이다. 사면과 곡저에서 격자해상도에 대한 기여면적의 민감도가 다르다는 점을 이용하여 두 영역을 구분하였다(Pelletier, 2010; Pelletier et al., 2013). 원 격자의 기여면적 \(A_Delta\)와 격자크기를 절반으로 줄여 계산한 기여면적 \(A_{Delta/2,max}\)의 비를 다음과 같이 계산하였다.

식 (31)

```
f={A_Delta OVER A_{Delta/2,max}}
```

\(f<1.20\)인 셀은 곡저로 분류하고, 그 밖의 셀은 사면으로 분류하였다. 사면에서는 유효 유로폭을 격자폭과 같게 두었다.

식 (32)

```
w=Delta x
```

곡저에서는 기여면적에 따른 유로폭을 다음과 같이 계산하였다.

식 (33)

```
w=g A^i
```

\(g=0.005\), \(i=0.5\)를 사용하였다(Pelletier et al., 2013). 레골리스의 침식계수는 EEMT의 함수로 계산하였다.

식 (34)

```
K_{reg}={K_0 OVER EEMT}
```

기반암의 침식계수는 다음과 같이 계산하였다.

식 (35)

```
K_{bed}={K_{reg} OVER F}
```

\(K_0=0.020\) m^2 MJ^-1, \(F=10\)을 사용하였다(Pelletier et al., 2013). 격자계산에서는 D8 흐름방향의 경사를 사용하였으며, 한 적분단계에서 공급 가능한 레골리스보다 많은 토양이 제거되지 않도록 유한공급제약(finite-supply constraint)을 적용하였다.

### 2.8.4 지역 융기

지역 융기율은 0.08 m kyr^-1로 설정하였다. Lee et al. (2024)은 태백산맥의 약 22 Ma 이후 장기 exhumation rate에 맞추어 지형발달모델의 배경 융기율을 80 mm kyr^-1로 설정하였으며, 본 연구에서도 이를 연구지역의 장기적인 지역 배경값으로 사용하였다.

식 (36)

```
U=0.08 m kyr^{-1}=80 mm kyr^{-1}
```

## 2.9 수치적분과 순차결합

기후와 식생은 0.1 kyr 간격으로 갱신하고, 각 0.1 kyr의 지형발달은 적응형 시간간격을 이용하여 적분하였다. 사면수송에 대한 기본 안정 시간간격은 다음과 같이 계산하였다(Pelletier et al., 2013).

식 (37)

```
Delta tau=0.01 {Delta x^2 OVER {2 k_{d,max}}}
```

여기서 \(Delta x\)는 격자크기, \(k_{d,max}\)는 해당 시점의 최대 사면수송계수이다. 각 시도단계에서 유수침식, 사면수송 또는 임계경사 조정에 의한 최대 지형변화량을 계산하고, 그 값이 0.025 m를 초과하면 해당 시도단계를 폐기한 뒤 시간간격을 절반으로 줄여 동일한 상태에서 다시 계산하였다. 0.025 m는 20 m DEM을 이용한 시간간격 수렴시험에서 설정한 수치적분 허용오차이다. 적분에는 유한공급제약과 임계경사 조정을 함께 적용하였으며, 지정 유출구의 기준고도는 고정하였다.

각 결합구간에서는 BIOME4 계산과 EEMT 및 AGB* 산정을 한 번 수행하고, 같은 값을 해당 0.1 kyr 구간의 모든 지형발달 세부시간단계에 적용하였다. 지형발달 후 갱신된 토심은 다음 시점의 가용수분 저장량과 PFT별 뿌리 접근성 계산에 사용하였다. 따라서 VeSLEM에서 지형발달이 식생에 미치는 시간적 피드백은 토심 변화에 따른 토양수분 저장량과 뿌리 접근성의 변화를 통해 구현하였다.

## 2.10 정적 실험과 동적 실험

토심과 지형의 시간적 변화가 고식생 복원에 미치는 영향을 평가하기 위하여 동일한 기후와 대기 CO2 조건에서 정적 실험과 동적 실험을 수행하였다. 정적 실험에서는 초기 지표고도, 기반암고도 및 토심을 분석기간 동안 고정하고 각 시점의 기후변화에 대해서만 BIOME4를 계산하였다.

동적 실험에서는 각 0.1 kyr 구간마다 BIOME4에서 계산된 EEMT와 AGB*를 이용하여 지형발달을 계산하고, 갱신된 토심을 다음 시점의 식생계산에 반영하였다. 두 실험의 차이는 토심과 지형 상태를 시간에 따라 갱신하여 식생계산에 반영하는지 여부로 설정하였다.

## 2.11 고식생 자료를 이용한 검증

고식생 복원결과는 Jang et al. (2011)의 대암산 용늪 화분기록을 이용하여 검증하였다. Jang et al. (2011)은 용늪 퇴적물에서 네 개의 local pollen zone을 구분하였으며, 각 식생대의 연대범위를 0.1 kyr 간격의 모델 출력시점과 대응시켰다. 이에 따라 총 62개의 모델 출력시점을 평가하였다. 이 62개 값은 화분시료 수가 아니라 각 화분대의 연대구간에 포함되는 반복적인 시간평가값이다.

모델 식생은 화분기록과 비교할 수 있도록 침엽수림, 활엽수림 및 혼효림의 세 산림범주로 후처리하였다. 각 격자에서 활엽수 PFT 가운데 최대 잠재 NPP와 침엽수 PFT 가운데 최대 잠재 NPP를 비교하고, 두 값의 합에서 한 군이 차지하는 비율이 51% 이상이면 해당 군으로 분류하였다. 어느 군도 51%에 도달하지 않는 경우 혼효림으로 분류하였다.

각 평가시점에서 화분기록에 해당하는 식생범주가 모의유역 유효격자의 1% 이상에서 출현하면 일치한 것으로 판정하였다. 전체 일치율은 다음과 같이 계산하였다.

식 (38)

```
Accuracy={N_{match} OVER N_{eval}} TIMES 100
```

여기서 \(N_{match}\)는 관측 식생범주와 일치한 모델 출력시점의 수, \(N_{eval}=62\)는 전체 평가시점의 수이다. 동일한 검증절차를 정적 실험과 동적 실험에 각각 적용하여 고식생 복원성능을 비교하였다.

## 참고문헌

Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S., & Chappellaz, J. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S., & Kempen, B. (2017). SoilGrids250m: Global gridded soil information based on machine learning. *PLoS ONE, 12*(2), e0169748. https://doi.org/10.1371/journal.pone.0169748

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*, 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling*. Doctoral dissertation, Lund University.

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k - high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. https://doi.org/10.5194/esurf-12-1091-2024

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology.

Pelletier, J. D. (2010). Minimizing the grid-resolution dependence of flow-routing algorithms for geomorphic applications. *Geomorphology, 122*(1-2), 91-98. https://doi.org/10.1016/j.geomorph.2010.06.001

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365-392. https://doi.org/10.2307/2937116

Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H., & Dai, Y. (2017). Mapping the global depth to bedrock for land surface modeling. *Journal of Advances in Modeling Earth Systems, 9*(1), 65-88. https://doi.org/10.1002/2016MS000686

Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L., & Heuvelink, G. B. M. (2023). Global mapping of volumetric water retention at 100, 330 and 15,000 cm suction using the WoSIS database. *International Soil and Water Conservation Research, 11*(2), 225-239. https://doi.org/10.1016/j.iswcr.2022.08.001
