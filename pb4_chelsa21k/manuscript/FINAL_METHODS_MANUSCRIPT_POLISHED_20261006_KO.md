# 2. 연구방법

## 2.1 VeSLEM의 구성과 결합 방식

본 연구에서는 21.0 ka BP 이후 기후 변화에 따른 식생, 토양 및 지형의 상호작용을 모의하기 위하여 평형 식생모델 BIOME4 v4.2b2와 수치지형발달모델을 결합한 식생-토양-지형발달모델(Vegetation-Soil-Landscape Evolution Model, VeSLEM)을 구축하였다.

식생 계산에는 BIOME4의 12개 PFT(PFT2-13)를 사용하였다. 각 PFT의 NPP와 LAI는 기후, 대기 CO2, 대기압, 토양수분 및 PFT별 기후제약에 따라 계산하였으며, PFT 간 경쟁으로 잠재 식생을 결정하였다(Kaplan, 2001; Kaplan et al., 2003). 토심은 토양수분 저장량과 PFT별 뿌리 접근성을 통해 식생 계산에 반영하였다.

분석 기간은 21.0 ka BP부터 0.0 ka BP까지로 설정하였으며, 식생모델과 지형발달모델의 결합 간격은 0.1 kyr, 즉 100년으로 설정하였다. 각 결합 시점의 기후, 지표고도 및 토심으로 식생을 계산하고, 산정된 EEMT와 AGB*를 지형발달 계산에 사용하였다. 갱신된 지표고도와 토심은 다음 결합 시점으로 전달하였다.

지표고도 (z), 기반암 또는 풍화전선 고도 (z_b), 토심 (H)의 관계는 다음과 같이 정의하였다.

식 (1)

```
H=z-z_b
```

연대는 (t_{BP}), 모델의 정방향 적분시간은 (tau)로 표기하였다.

## 2.2 공간 자료와 계산 격자

고도 자료는 국토정보플랫폼에서 제공하는 수치지형도를 이용하였다. QGIS 3.44.5에서 역거리 가중법(Inverse Distance Weighting, IDW)을 이용하여 10 m 해상도의 연속 고도면을 구축하고, GRASS GIS의 r.watershed 모듈을 이용하여 대암산 용늪을 포함하는 소유역을 추출하였다.

고도, 토심 및 토양 자료의 좌표계는 Korea 2000/Central Belt 2010(EPSG:5187)으로 통일하고 20 m 격자에 정렬하였다. 연속형 고도와 토심 자료는 평균값으로 집계하였으며, 범주형 토성 자료는 최근린법으로 변환하였다. 지형발달 계산은 20 m 격자에서 수행하였으며, 계산영역은 20행 × 23열 가운데 유역에 포함되는 298개 셀로 구성하였다.

유역 경계조건은 지정 유출구의 열린 경계와 유역 외곽의 무유출 경계로 정의하였다. 흐름 방향 계산에서는 지정 유출구를 통해 유역 외부로 배수되도록 하였으며, 사면 물질수송은 계산영역 내부의 인접 셀 사이에서 계산하였다. 흐름 방향과 기여면적은 싱크를 채운 지형면에서 계산하였다.

21.0 ka BP의 초기 지표고도에는 현대 수치지형도를, 초기 토심에는 ISRIC SoilGrids의 기반암 깊이 자료 BDRICM_M_1km_ll을 사용하였다(Hengl et al., 2017; Shangguan et al., 2017). 초기 기반암고도는 지표고도에서 토심을 뺀 값으로 산정하였다.

토성은 SoilGrids 기반의 3분류 토성 자료를 사용하였으며(Poggio et al., 2021), 연구 유역의 토성등급은 BIOME4 토성등급(texture class) 2로 설정하였다. 상층의 상대 토양수분 상태를 \(omega_{top}\)이라고 하면 일별 층간 이동량은 다음과 같이 계산하였다.

식 (2)

```
Perc=K_1 omega_{top}^4
```

BIOME4에서 \(K_1\)은 상층 토양의 포화수리전도도(Ksat)로 정의되며, 토성등급 2에는 \(K_1=4.0\) mm h^-1을 적용하였다.

## 2.3 기후 및 대기 조건

기온과 강수량은 CHELSA-TraCE21k v1.0의 월별 자료를 사용하였다(Karger et al., 2023). 용늪 중심좌표인 128.122518°E, 38.214643°N에서 21.0 ka BP부터 0.0 ka BP까지 0.1 kyr 간격으로 추출한 월별 최저기온, 최고기온 및 강수량을 연구 유역의 기후 조건으로 사용하였다. 월평균기온은 다음과 같이 계산하였다.

식 (3)

```
T_m={(T_{min,m}+T_{max,m}) OVER 2}-273.15
```

여기서 (T_m)은 월 (m)의 평균기온이며, (T_{min,m})과 (T_{max,m})은 각각 Kelvin 단위의 월별 최저기온과 최고기온이다. PFT의 절대최저기온 제약에는 식 (4)로 추정한 (T_{absmin})을 사용하였다.

BIOME4의 광환경 계산에는 Beyer et al. (2020)의 월별 운량(cloudiness)을 각 시점에 선형보간한 뒤, (S_m=100-C_m)으로 변환한 월별 일조율을 사용하였다. 여기서 (C_m)은 월별 운량(%), (S_m)은 월별 일조율(%)이다. 대기 CO2 농도는 Bereiter et al. (2015)의 남극 복합기록(Antarctic composite)을 이용하여 각 시점 (t_{BP})에 선형보간하였다.

PFT의 저온한계 판정에 사용되는 절대최저기온은 BIOME4의 관계식을 이용하였다.

식 (4)

```
T_{absmin}=0.006 T_{cold}^2+1.316 T_{cold}-21.9
```

여기서 (T_{absmin})은 절대최저기온, (T_{cold})는 가장 추운 달의 월평균기온이다.

각 격자셀의 지표고도는 대기압 계산에 이용하였다. 대기압은 다음과 같이 산정하였다.

식 (5)

```
p(z)=101325(1-2.25577 TIMES 10^{-5} z)^{5.25588}
```

여기서 (p(z))는 고도 (z)에서의 대기압(Pa)이다. 대기압은 BIOME4의 CO2 및 O2 분압 계산에, 위도는 일장과 일사량 계산에 사용하였다. BIOME4에서는 월평균기온, 월강수량 및 월별 일조율을 일 단위로 보간하여 적설과 융설을 포함한 생리 및 수문 계산에 사용하였다.

## 2.4 토심에 따른 토양수분 저장량

토심에 따른 가용수분 저장량은 McKenzie et al. (2003)의 토양단면 가용수분용량(profile available water capacity) 개념으로 계산하였다. 깊이 (zeta)에서의 가용수분 밀도는 10 kPa와 1500 kPa에서의 체적수분함량 차이로 정의하였다.

식 (6)

```
AWC(zeta)=theta_{-10}(zeta)-theta_{-1500}(zeta)
```

여기서 (theta_{-10})과 (theta_{-1500})은 각각 10 kPa와 1500 kPa에서의 체적수분함량이다(McKenzie et al., 2003).

토양수분 특성은 SoilGrids의 수분보유량 자료(Turek et al., 2023)에서 용늪 지점인 128.1236°E, 38.2153°N의 깊이별 값을 추출하여 연구 유역에 적용하였다. 10 kPa와 1500 kPa의 체적수분함량 차이로 계산한 가용수분 밀도는 0-0.05 m에서 237 mm m^-1, 0.05-0.15 m에서 232 mm m^-1, 0.15-0.30 m에서 218 mm m^-1, 0.30-0.60 m에서 207 mm m^-1, 0.60-1.00 m에서 198 mm m^-1, 1.00-2.00 m에서 179 mm m^-1이었다.

BIOME4의 수문구조에 따라 토양층은 상층 0-0.30 m와 하층 0.30-1.50 m로 구분하였다. 각 시점의 가용수분 저장량은 토심 (H)까지 포함되는 토양 두께에 따라 계산하였으며, 상층과 하층의 저장량은 다음과 같이 정의하였다.

식 (7)

```
W_{top}(H)=1000 INT _0^{min(H,0.30)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

식 (8)

```
W_{bottom}(H)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

여기서 (W_{top})과 (W_{bottom})은 각각 상층과 하층의 가용수분 저장량(mm)이다. 최대 수문 토심은 1.50 m로 설정하였다. 깊이별 수분보유 특성과 토성등급은 모의 기간 동안 일정하게 적용하였으며, 각 깊이 구간의 포함 두께는 토심 (H)에 따라 계산하였다.

## 2.5 PFT별 뿌리 접근성과 수문 계산

BIOME4의 PFT별 상부 0.30 m 뿌리분율은 Gale and Grigal (1987)이 제시하고 Jackson et al. (1996)이 전 지구 생물군계에 적용한 누적 뿌리분포 관계에 근거하였다.

식 (9)

```
Y(d)=1-beta^d
```

여기서 (Y(d))는 지표에서 깊이 (d)까지 존재하는 누적 뿌리분율이며, (beta)는 뿌리의 수직분포를 나타내는 계수이다. PFT별 상부 0.30 m 누적 뿌리분율 (r_{30,p})은 BIOME4에 정의된 값을 사용하였다.

McKenzie et al. (2003)의 지수형 깊이 함수를 이용하여 뿌리 접근성의 수직분포를 계산하였다.

식 (10)

```
f(x)=exp(-{x OVER X_i})
```

여기서 (X_i)는 지수형 깊이 함수의 특성깊이이다(McKenzie et al., 2003). (r_{30,p})와 식 (10)을 일치시키면 PFT별 특성깊이 (X_p)는 다음과 같이 계산된다.

식 (11)

```
X_p=-{0.30 OVER ln(1-r_{30,p})}
```

BIOME4의 수문계산에 이용되는 유효 토심은 다음과 같이 정의하였다.

식 (12)

```
D=min(max(H,0),1.50)
```

유효 토심 내에서 접근 가능한 상층과 하층의 PFT별 뿌리분율은 각각 다음과 같이 계산하였다.

식 (13)

```
R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})
```

식 (14)

```
R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}
```

PFT별 근권 토양수분상태는 다음과 같이 계산하였다.

식 (15)

```
omega_{r,p}=R_{top,p} omega_{top}+R_{bottom,p} omega_{bottom}
```

여기서 (omega_{top})과 (omega_{bottom})은 각각 상층과 하층의 토양수분 상태이다. 근권 토양수분 상태가 0보다 큰 경우 실제증발산량의 상층 및 하층 추출가중치는 각각 다음과 같이 계산하였다.

식 (16a)

```
F_{top,p}=R_{top,p}{omega_{top} OVER omega_{r,p}}
```

식 (16b)

```
F_{bottom,p}=R_{bottom,p}{omega_{bottom} OVER omega_{r,p}}
```

(omega_{r,p}=0)인 경우 두 추출가중치는 모두 0으로 설정하였다.

토심이 1×10^-6 m 이하인 셀은 노출 기반암으로 정의하였다. 노출 기반암 셀의 NPP, AET 및 AGB*는 0으로 설정하고, EEMT는 강수에 의한 물리적 에너지 성분으로 계산하였다.

## 2.6 EEMT 산정

식생 및 수문 조건과 지형발달의 결합변수로 Pelletier et al. (2013)의 EEMT를 사용하였다. 유효강수에 의해 토양계로 전달되는 에너지와 생물생산에 저장되는 에너지는 각각 다음과 같이 계산하였다.

식 (17)

```
E_{PPT}=Delta T C_w P_{eff}
```

식 (18)

```
E_{BIO}=NPP h_{BIO}
```

EEMT는 두 성분의 합으로 정의하였다.

식 (19)

```
EEMT=E_{PPT}+E_{BIO}
```

여기서 (P_{eff}=PPT-ET)이다(Pelletier et al., 2013). 격자별 EEMT는 BIOME4의 일별 AET를 월별 총량으로 집계한 값과 연간 탄소 NPP를 이용하여 다음과 같이 계산하였다.

식 (20)

```
EEMT={C_w OVER 10^6} SUM _{m=1}^{12} T_m (R_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}
```

여기서 (R_m)은 월강수량(mm), (AET_m)은 BIOME4의 일별 AET를 월별로 합산한 값(mm month^-1), (C_w=4186) J kg^-1 K^-1, (h_{BIO}=22 TIMES 10^6) J kg^-1이며, (NPP_C)는 BIOME4가 산출한 연간 탄소 NPP(g C m^-2 yr^-1)이다. 식 (20)의 (T_m)은 섭씨로 변환한 월평균기온으로 Pelletier et al. (2013)의 (Delta T) 항에 적용하였다.

탄소질량분율은 (f_C=0.50)으로 설정하였다. 월별 유효강수는 (P_{eff,m}=R_m-AET_m)으로 정의하였으며, EEMT의 단위는 MJ m^-2 yr^-1로 하였다.

## 2.7 BIOME4 기반 지상부 생물량 대리변수 AGB*

지상부 생물량 대리변수 AGB*는 BIOME4의 우점 PFT와 LAI를 이용하여 산정하였다. 격자의 우점 PFT를 (p^*)라고 할 때 AGB*는 잎과 살아 있는 변재의 건조생체량 합으로 정의하였다.

식 (21)

```
AGB^*=B_{leaf,dry,p^*}+B_{sapwood,dry,p^*}
```

잎 건조생체량은 Reich et al. (1992)의 잎수명과 비엽면적(Specific Leaf Area, SLA)의 관계를 이용하였다.

식 (22)

```
log_{10}(SLA_p)=2.44-0.43 log_{10}(L_{m,p})
```

여기서 (L_{m,p})는 BIOME4에 정의된 PFT (p)의 잎수명(개월)이다. SLA를 cm^2 g^-1에서 m^2 kg^-1로 변환한 뒤, 잎 건조생체량을 다음과 같이 계산하였다.

식 (23)

```
B_{leaf,dry,p}={LAI_p OVER SLA_p}
```

변재 탄소량은 Haxeltine and Prentice (1996)의 변재 탄소량-LAI 관계(sapwood-LAI relationship)를 이용하였다.

식 (24)

```
C_{s,p}=LAI_p C_{n,p}
```

여기서 (C_{s,p})는 변재 탄소량, (C_{n,p})은 단위 LAI당 변재 탄소량이다. 식 (24)는 Haxeltine and Prentice (1996)의 변재 탄소량-LAI 관계를 따르며, (C_{n,p})는 BIOME4의 변재 탄소계수인 0.5 kg C m^-2 LAI^-1로 설정하였다. 변재 건조생체량은 다음과 같이 계산하였다.

식 (25)

```
B_{sapwood,dry,p}=CASES{{C_{s,p} OVER f_C} & p in {2,3,4,5,6,7,10,11,13} # 0 & p in {8,9,12}}
```

여기서 (f_C=0.50)이다. AGB*의 단위는 kg dry biomass m^-2로 하였다.

## 2.8 지형발달모델

지형발달은 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 사면세류와 하천침식 과정을 이용하여 계산하였다. 지표고도는 기반암고도와 토심의 합으로 정의하였다.

식 (26)

```
z=z_b+H
```

기반암 또는 풍화전선 고도의 변화는 다음과 같이 계산하였다.

식 (27)

```
{PARTIAL z_b OVER PARTIAL tau}=U-{P OVER cos theta}
```

토심 변화는 다음과 같이 계산하였다.

식 (28)

```
{PARTIAL H OVER PARTIAL tau}={rho_b OVER rho_s}{P OVER cos theta}-E
```

여기서 (U)는 지역 융기율, (P)는 토양생산률, (rho_b/rho_s)는 기반암과 토양의 밀도비, (E)는 사면수송과 유수침식에 따른 순 침식률이며 퇴적이 우세한 경우 음의 값을 갖는다.

### 2.8.1 토양생산

토심에 따른 토양생산률은 다음과 같이 계산하였다(Pelletier et al., 2013).

식 (29)

```
P=P_0 exp(-{H cos theta OVER H_0})
```

잠재 토양생산률 (P_0)는 EEMT의 함수로 계산하였다.

식 (30)

```
P_0=a exp(b EEMT)
```

(a=0.037) m kyr^-1, (b=0.030), (H_0=0.50) m, (rho_b/rho_s=1.8)을 사용하였다.

### 2.8.2 비선형 사면수송

사면수송에 따른 침식 또는 퇴적은 토사유속의 발산으로 계산하였다.

식 (31)

```
E_c=nabla BULLET q
```

토심과 임계경사를 고려한 비선형 사면수송은 Pelletier et al. (2013)의 Forward-Time-Centered-Space (FTCS) 방식으로 셀 경계면별로 계산하였다. 토심과 사면수송계수의 경계면 값은 인접한 두 셀의 산술평균으로 정의하였으며, 경계면 (f)의 토사유속은 다음과 같다.

식 (32)

```
q_f=-{k_{d,f} H_f S_f OVER {1-({|S_f| OVER S_c})^2}}
```

여기서 (S_f)는 인접한 두 셀 사이의 경사이며, (H_f)와 (k_{d,f})는 각각 경계면 토심과 사면수송계수이다. 사면수송계수 (k_d)는 EEMT와 AGB*의 함수로 계산하였다.

식 (33)

```
k_d=c EEMT+d AGB^*
```

(c=0.033), (d=0.050)을 사용하였다(Pelletier et al., 2013). 임계경사 (S_c)는 20 m 계산 격자에서 1.50으로 설정하였다.

### 2.8.3 사면세류 및 하천침식

사면세류와 하천침식은 다음 식을 이용하였다(Pelletier et al., 2013).

식 (34)

```
E_f=K {A OVER w}|nabla z|
```

여기서 (A)는 기여면적, (w)는 유효 유로폭, (K)는 침식계수이다. 사면 셀에서는 격자폭을 유효 유로폭으로 사용하였다.

식 (35)

```
w=Delta x
```

곡저 셀에서는 기여면적에 따른 유로폭을 다음과 같이 계산하였다.

식 (36)

```
w=g A^i
```

(g=0.005), (i=0.5)를 사용하였다(Pelletier et al., 2013). 기여면적은 Freeman (1991)의 다중흐름방향(Multiple Flow Direction, MFD) 방법을 이용하여 계산하였으며, 흐름분배의 경사지수는 1.10으로 설정하였다.

사면과 곡저는 Pelletier (2010)의 격자해상도 의존성 최소화 방법을 이용하여 구분하였다. 기준 격자폭 (Delta x)의 지형과 이를 이중선형 보간(bilinear interpolation)으로 세분한 격자폭 (Delta x/2)의 지형에서 각각 MFD 기여면적을 계산하였다. 세분 격자에서는 하나의 기준 격자셀에 대응하는 2×2 셀 가운데 최대 기여면적을 사용하여 다음의 비를 계산하였다.

식 (37)

```
f={A_{Delta x} OVER A_{Delta x/2}^{max}}
```

(f<1.20)인 셀은 곡저로, (f>=1.20)인 셀은 사면으로 분류하였다. 식 (34)의 (A)는 기준 격자에서 계산한 MFD 기여면적을 사용하였으며, (|nabla z|)에는 D8 방식으로 결정한 하류 수신셀 방향의 경사를 사용하였다.

EEMT가 양수인 셀에서 레골리스의 침식계수는 EEMT의 역수에 비례하도록 계산하였다.

식 (38)

```
K_{reg}={K_0 OVER EEMT}
```

기반암의 침식계수는 다음과 같이 계산하였다.

식 (39)

```
K_{bed}={K_{reg} OVER F}
```

(K_0=0.020) m^2 MJ^-1, (F=10)을 사용하였다(Pelletier et al., 2013). 레골리스 침식량은 가용 레골리스량으로 제한하였다.

### 2.8.4 지역 융기율

지역 융기율 (U)은 80 mm kyr^-1로 설정하였다(Lee et al., 2024).

식 (40)

```
U=0.08 m kyr^{-1}=80 mm kyr^{-1}
```

## 2.9 수치적분과 순차결합

식생과 지형은 0.1 kyr 간격으로 결합하였으며, 지형발달 계산은 각 0.1 kyr 구간 내부에서 적응형 시간간격으로 적분하였다. 수치적분 시간간격의 안정성 기준은 다음과 같이 계산하였다(Pelletier et al., 2013).

식 (41)

```
Delta tau=0.01 {Delta x^2 OVER {2 k_{d,max}}}
```

여기서 (Delta x)는 격자크기, (k_{d,max})는 각 시점의 최대 사면수송계수이다. 적응형 시간간격은 각 수치적분 단계의 최대 지형변화가 0.025 m 이하가 되도록 1/2씩 조정하였다.

BIOME4는 21.0-0.0 ka BP에서 0.1 kyr 간격으로 계산하였으며, 지형발달은 인접한 두 시점 사이에서 적분하였다. 각 0.1 kyr 구간에서는 구간 시작 시점의 기후, 지표고도 및 토심으로 토양수분 저장량과 뿌리 접근성을 계산한 뒤, BIOME4, EEMT와 AGB*, 지형발달의 순서로 계산하였다.

각 지형발달 시간단계는 임계경사 조정, 토양생산, 비선형 사면수송, 유수침식, 임계경사 조정의 순서로 계산하였다. 토양생산량은 같은 시간단계의 이동 가능한 레골리스에 포함하였으며, 유수침식량은 사면수송 후 남은 가용 레골리스량으로 제한하였다. 가용 레골리스를 초과하는 침식능은 기반암 침식에 적용하였다.

임계경사 조정에 따른 토양 및 기반암 제거량은 계산영역 외부 유출량으로 계산하였다. 각 0.1 kyr 구간의 지형발달에는 구간 시작 시점의 EEMT와 AGB*를 사용하였고, 갱신된 지표고도와 토심은 다음 시점의 대기압, 토양수분 저장량 및 뿌리 접근성 계산에 사용하였다.

## 2.10 정적 실험과 동적 실험

지형 및 토심 변화의 효과는 동일한 기후 조건을 사용한 정적 실험과 동적 실험의 비교로 평가하였다. 정적 실험에서는 초기 지표고도, 기반암고도 및 토심을 분석 기간 동안 고정하고 각 시점의 기후 조건에 대한 BIOME4의 식생 반응을 계산하였다.

동적 실험에서는 각 0.1 kyr 구간의 지형발달 계산을 통해 (z_b)와 (H)를 갱신하고 식 (26)에 따라 다음 시점의 (z)를 계산하였다.

## 2.11 고식생 자료를 이용한 검증

정량 검증 자료로 Jang et al. (2011)의 대암산 용늪 화분 기록을 사용하였다. Jang et al. (2011)은 5.9 ka cal BP 이후를 네 개의 국지 화분대(local pollen zone, LPZ)로 구분하였다.

LPZ-I(5.9-4.8 ka cal BP)와 LPZ-III(3.4-0.39 ka cal BP)는 낙엽활엽수림으로, LPZ-II(4.8-3.4 ka cal BP)와 LPZ-IV(0.39-0 ka cal BP)는 침엽수와 낙엽활엽수가 함께 나타나는 혼효림으로 해석하였다.

각 LPZ의 연대 범위에 포함되는 0.1 kyr 간격의 모의 시점을 비교하여 총 62개의 시점-식생대 조합을 평가하였다. LPZ 경계 시점인 4.8 ka cal BP와 3.4 ka cal BP는 각각 양쪽 인접 LPZ의 평가에 포함하였다.

검증 범주는 침엽수림, 활엽수림, 혼효림, 초본 및 개방식생, 비식생지의 5개로 정의하였다. BIOME4 생물군계(biome) 1-4는 활엽수림, 5, 8, 10, 11은 침엽수림으로 분류하였다. 생물군계 12-20과 22-26은 초본 및 개방식생으로, 27과 28 및 노출 기반암은 비식생지로 분류하였다.

생물군계 21은 우점 PFT가 존재하면서 NPP 또는 LAI가 양수인 경우 초본 및 개방식생으로, 우점 PFT가 없거나 NPP와 LAI가 모두 0인 경우 비식생지로 분류하였다.

BIOME4의 혼합림 생물군계 6, 7, 9에서는 활엽수 PFT 2-4와 침엽수 PFT 5-7 가운데 각각 잠재 NPP가 가장 큰 PFT를 선택하고 두 값의 상대비율을 계산하였다. 침엽수 비율이 51% 이상인 경우 침엽수림, 활엽수 비율이 51% 이상인 경우 활엽수림, 두 비율이 모두 51% 미만인 경우 혼효림으로 분류하였다.

각 평가 시점에서 식생 점유율은 침엽수림, 활엽수림, 혼효림, 초본 및 개방식생으로 분류된 유역 셀을 분모로 계산하였다. Jang et al. (2011)에서 제시한 식생군의 점유율이 1% 이상이면 일치한 것으로 판정하였다. 전체 정확도는 62개 시점-식생대 조합 가운데 관측 식생군과 일치한 조합의 비율로 계산하였다. 정적 실험과 동적 실험은 동일한 분류 및 판정기준으로 평가하였다.

## 참고문헌

Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S., & Chappellaz, J. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Freeman, T. G. (1991). Calculating catchment area with divergent flow based on a regular grid. *Computers & Geosciences, 17*(3), 413-422. https://doi.org/10.1016/0098-3004(91)90048-I

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S., & Kempen, B. (2017). SoilGrids250m: Global gridded soil information based on machine learning. *PLoS ONE, 12*(2), e0169748. https://doi.org/10.1371/journal.pone.0169748

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*(3), 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling*. Doctoral dissertation, Lund University.

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., Cramer, W., Matveyeva, N. V., McGuire, A. D., Murray, D. F., Razzhivin, V. Y., Smith, B., Walker, D. A., Anderson, P. M., Andreev, A. A., Brubaker, L. B., Edwards, M. E., & Lozhkin, A. V. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k - high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. https://doi.org/10.5194/esurf-12-1091-2024

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology. https://www.ewater.org.au/archive/crcch/overview/archive/pubs/pdfs/technical200303.pdf

Pelletier, J. D. (2010). Minimizing the grid-resolution dependence of flow-routing algorithms for geomorphic applications. *Geomorphology, 122*(1-2), 91-98. https://doi.org/10.1016/j.geomorph.2010.06.001

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., & Rossiter, D. (2021). SoilGrids 2.0: Producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116

Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H., & Dai, Y. (2017). Mapping the global depth to bedrock for land surface modeling. *Journal of Advances in Modeling Earth Systems, 9*(1), 65-88. https://doi.org/10.1002/2016MS000686

Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L., & Heuvelink, G. B. M. (2023). Global mapping of volumetric water retention at 100, 330 and 15,000 cm suction using the WoSIS database. *International Soil and Water Conservation Research, 11*(2), 225-239. https://doi.org/10.1016/j.iswcr.2022.08.001
