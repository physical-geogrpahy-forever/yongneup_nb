# 2. 연구방법

## 2.1 VeSLEM의 구성과 결합 방식

본 연구에서는 후기 빙기 이후의 기후변화에 따른 식생, 토양 및 지형의 장기 상호작용을 모의하기 위하여 평형 식생모델 BIOME4 v4.2b2와 Pelletier et al. (2013)의 수치지형발달모델을 결합한 식생-토양-지형발달모델(Vegetation-Soil-Landscape Evolution Model, VeSLEM)을 구축하였다. BIOME4는 기후, 대기 CO2 및 토양수분 조건을 이용하여 식물 기능형(Plant Functional Type, PFT)별 NPP와 LAI를 계산하고, PFT 간 경쟁을 통해 잠재 식생을 결정하는 평형 식생모델이다(Kaplan, 2001; Kaplan et al., 2003). 본 연구에서는 BIOME4 v4.2b2에 내장된 PFT별 기후한계를 적용하였으며, 토심의 영향은 토양수분 저장량과 PFT별 뿌리 접근성의 변화를 통해 반영하였다.

분석기간은 21.0 ka BP부터 0.0 ka BP까지로 설정하였으며, 식생모델과 지형발달모델의 결합간격은 0.1 kyr, 즉 100년으로 설정하였다. 이에 따라 21.0 ka BP부터 0.0 ka BP까지 총 211개 시간시점을 계산하였다. 각 100년 결합구간의 시작에서 해당 시점의 기후와 현재 토심을 이용하여 토양수분 저장량과 PFT별 뿌리 접근성을 계산한 뒤 BIOME4를 실행하였다. 이후 BIOME4에서 산출된 NPP, 실제증발산량(Actual Evapotranspiration, AET), LAI 및 우점 PFT를 이용하여 유효 에너지 및 물질 전달량(Effective Energy and Mass Transfer, EEMT)과 지상부 생물량 대리변수인 AGB*를 산정하였다. EEMT와 AGB*는 같은 100년 구간의 지형발달 계산에 입력하였으며, 지형발달모델은 해당 구간 내부에서 수치안정성을 만족하도록 더 짧은 시간간격으로 적분하였다. 구간 말에 갱신된 기반암고도와 토심은 다음 100년 시점의 식생계산에 전달하였다.

지표고도 \(z\), 기반암 또는 풍화전선 고도 \(z_b\), 토심 \(H\)의 관계는 다음과 같이 정의하였다.

식 (1)

```
H=z-z_b
```

연대는 \(t_{BP}\)로, 모델의 정방향 적분시간은 \(tau\)로 표기하여 두 시간축을 구분하였다.

## 2.2 공간 입력자료와 전처리

고도자료는 국토정보플랫폼에서 제공하는 수치지형도를 이용하였다. QGIS 3.44.5에서 역거리가중법(Inverse Distance Weighting, IDW)을 이용하여 10 m 해상도의 연속 고도면을 구축하고, GRASS GIS의 `r.watershed`를 이용하여 대암산 용늪을 포함하는 소유역을 추출하였다. 이후 고도, 토심 및 토양 관련 공간자료의 좌표계를 Korea 2000/Central Belt 2010(EPSG:5187)으로 통일하고 20 m 격자로 리샘플링하여 VeSLEM의 계산격자를 구축하였다.

유역경계는 지정한 단일 유출구만 열린 경계로 설정하고 나머지 경계는 닫힌 경계로 처리하였다. D8 흐름방향 계산에서는 유출구 셀에서만 유역 외부로의 유출을 허용하였으며, 다른 경계셀에서 유역 외부로 향하는 흐름은 허용하지 않았다. 사면 물질수송 역시 계산영역 내부의 인접 셀 사이에서만 계산하여 닫힌 경계를 가로지르는 물질수송량을 0으로 설정하였다. 또한 D8 흐름계산에서 내부 폐쇄가 발생하지 않도록 흐름경로를 계산하기 전에 싱크 채우기를 적용하였다.

초기 토심은 ISRIC SoilGrids의 기반암 깊이 자료 `BDRICM_M_1km_ll`을 이용하였다(Hengl et al., 2017; Shangguan et al., 2017). 토양수분 저장량 계산에는 용늪 지점의 SoilGrids 수분특성 자료를 이용하였다. 128.1236°E, 38.2153°N 지점에서 10 kPa와 1500 kPa의 체적수분함량 차이를 각 깊이구간별로 산정하였다. 깊이별 available-water density는 0-0.05 m에서 237 mm m^-1, 0.05-0.15 m에서 232 mm m^-1, 0.15-0.30 m에서 218 mm m^-1, 0.30-0.60 m에서 207 mm m^-1, 0.60-1.00 m에서 198 mm m^-1, 1.00-2.00 m에서 179 mm m^-1을 사용하였다(Turek et al., 2023). BIOME4의 수문구조에 따라 실제 토양수분 저장량 계산은 최대 1.50 m까지만 수행하였다.

계산에 사용한 토성격자는 모든 유효 셀에서 BIOME4의 texture class 2로 분류되었다. 이 토성정보는 BIOME4에 내장된 토성별 hydraulic conductivity를 선택하는 데 사용하였다. 반면 토양수분 저장량은 모래, 실트 및 점토 비율을 이용하여 새로 추정하지 않고, 앞서 산정한 깊이별 체적수분함량 차이를 직접 이용하였다.

## 2.3 기후 및 대기 CO2 자료

기온과 강수량은 CHELSA-TraCE21k의 월별 자료를 사용하였다(Karger et al., 2023). 21.0 ka BP부터 0.0 ka BP까지 0.1 kyr 간격의 자료를 이용하였으며, 월평균기온은 월별 최저기온과 최고기온의 평균으로 계산하였다. CHELSA-TraCE21k의 기온자료는 Kelvin 단위로 제공되므로 월평균기온은 다음과 같이 변환하였다.

식 (2)

```
T_m={(T_{min,m}+T_{max,m}) OVER 2}-273.15
```

여기서 \(T_m\)은 월 \(m\)의 평균기온, \(T_{min,m}\)과 \(T_{max,m}\)은 각각 월별 최저기온과 최고기온이다. CHELSA-TraCE21k는 지형효과를 고려하여 하향화된 기후자료이므로 본 연구에서는 추가적인 고도감률 보정을 적용하지 않았다. 따라서 지형발달에 따라 고도가 변화하더라도 별도의 기온감률을 이용하여 월별 기온을 다시 보정하지 않았다.

CHELSA-TraCE21k의 Centennial 자료에는 BIOME4의 광환경 계산에 필요한 cloudiness가 포함되어 있지 않으므로, cloudiness는 Beyer et al. (2020)의 후기 제4기 기후자료에서 추출하여 각 시간시점에 맞게 보간하였다. Beyer et al. (2020)의 기온과 강수량은 최종 모형의 기후입력으로 사용하지 않았다. 대기 CO2 농도는 Bereiter et al. (2015)의 revised Antarctic composite를 각 \(t_{BP}\)에 선형보간하여 사용하였다.

BIOME4에서 PFT의 저온한계를 판정하기 위한 절대최저기온은 v4.2b2의 회귀식을 사용하였다.

식 (3)

```
T_{absmin}=0.006 T_{cold}^2+1.316 T_{cold}-21.9
```

여기서 \(T_{absmin}\)은 추정된 절대최저기온, \(T_{cold}\)는 가장 추운 달의 월평균기온이다.

## 2.4 토심에 따른 토양수분 저장량

토심 변화가 BIOME4의 수분조건에 반영되도록 McKenzie et al. (2003)의 profile available water capacity 개념을 이용하였다. McKenzie et al. (2003)은 토양의 가용수분량을 약 -10 kPa와 -1.5 MPa에서의 체적수분함량 차이를 토양깊이에 대해 적분한 값으로 정의하였다. 이를 본 연구의 기호로 나타내면 깊이 \(zeta\)에서의 available-water density는 다음과 같다.

식 (4)

```
AWC(zeta)=theta_{-10}(zeta)-theta_{-1500}(zeta)
```

여기서 \(theta_{-10}\)과 \(theta_{-1500}\)은 각각 -10 kPa와 -1500 kPa에서의 체적수분함량이다. 식 (4)는 McKenzie et al. (2003)의 개념적 정의를 본 연구의 기호로 나타낸 것이다.

BIOME4 v4.2b2의 기존 수문구조를 유지하기 위하여 토양층은 상층 0-0.30 m와 하층 0.30-1.50 m로 구분하였다. 현재 토심 \(H\)에 따라 실제로 존재하는 토양부분만 수분저장량 계산에 포함하였으며, 상층과 하층의 available-water storage는 각각 다음과 같이 계산하였다.

식 (5)

```
W_{top}(H)=1000 INT _0^{min(H,0.30)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

식 (6)

```
W_{bottom}(H)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

여기서 \(W_{top}\)과 \(W_{bottom}\)은 각각 BIOME4 상층과 하층의 가용수분 저장량이다. 식 (5)와 식 (6)은 McKenzie et al. (2003)의 profile available-water 개념을 BIOME4의 2층 수문구조와 동적 토심에 적용하기 위하여 본 연구에서 구성한 식이다.

## 2.5 유한 토심에 따른 PFT별 뿌리 접근성

토심 감소에 따라 PFT가 실제로 접근할 수 있는 뿌리분율이 감소하도록 뿌리의 수직분포를 고려하였다. 뿌리의 누적 수직분포는 Gale and Grigal (1987)의 관계와 Jackson et al. (1996)의 전지구 뿌리분포 자료를 이용하였다.

식 (7)

```
Y(d)=1-beta^d
```

여기서 \(Y(d)\)는 지표에서 깊이 \(d\)까지 존재하는 누적 뿌리분율이며, \(beta\)는 뿌리의 수직분포를 나타내는 계수이다. BIOME4 v4.2b2의 `pftpar(pft,6)`은 PFT별 상부 0.30 m의 누적 뿌리분율을 나타내며, 본 연구에서는 이를 \(r_{30,p}\)로 표기하였다.

McKenzie et al. (2003)은 plant available water capacity를 계산할 때 깊이에 따른 뿌리밀도 감소를 다음과 같은 지수함수로 나타냈다.

식 (8)

```
f(x)=exp(-{x OVER X_i})
```

여기서 \(X_i\)는 깊이 \(X_i\) 아래에 약 37%의 뿌리가 존재하도록 하는 특성깊이이다. 본 연구에서는 이 지수형식을 BIOME4의 PFT별 상부 0.30 m 뿌리분율과 연결하기 위하여 PFT별 특성깊이 \(X_p\)를 다음과 같이 계산하였다.

식 (9)

```
X_p=-{0.30 OVER ln(1-r_{30,p})}
```

식 (9)는 McKenzie et al. (2003)의 지수형 뿌리 가중개념과 BIOME4의 PFT별 뿌리분율을 연결하기 위하여 본 연구에서 유도한 관계식이다.

BIOME4에 반영되는 유효 토심은 최대 수문깊이인 1.50 m를 넘지 않도록 다음과 같이 제한하였다.

식 (10)

```
D=min(max(H,0),1.50)
```

현재 토심에서 접근 가능한 상층 뿌리분율은 다음과 같이 계산하였다.

식 (11)

```
R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})
```

하층의 접근 가능한 뿌리분율은 다음과 같이 계산하였다.

식 (12)

```
R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}
```

이후 PFT별 근권 토양수분상태는 각 수문층의 토양수분상태를 접근 가능한 뿌리분율로 가중하여 계산하였다.

식 (13)

```
omega_{r,p}=R_{top,p} omega_{top}+R_{bottom,p} omega_{bottom}
```

여기서 \(omega_{top}\)과 \(omega_{bottom}\)은 각각 BIOME4 상층과 하층의 토양수분상태이다. 토심이 얕아 \(R_{top,p}+R_{bottom,p}<1\)이 되더라도 두 값을 다시 1로 정규화하지 않았다. 따라서 실제 토심보다 아래에 존재할 뿌리분율을 상부 토양층으로 인위적으로 재배치하지 않았다.

## 2.6 EEMT 산정

식생과 수문조건을 지형발달 과정에 연결하기 위하여 Pelletier et al. (2013)의 EEMT를 이용하였다. Pelletier et al. (2013)은 유효강수에 의해 토양계로 전달되는 에너지와 생물생산에 저장되는 에너지를 각각 다음과 같이 정의하였다.

식 (14)

```
E_{PPT}=Delta T C_w P_{eff}
```

식 (15)

```
E_{BIO}=NPP h_{BIO}
```

이에 따라 EEMT는 두 성분의 합으로 정의된다.

식 (16)

```
EEMT=E_{PPT}+E_{BIO}
```

여기서 \(P_{eff}=PPT-ET\)이다. 본 연구에서는 BIOME4가 월별 AET와 연간 carbon NPP를 산출하므로 Pelletier et al. (2013)의 관계를 BIOME4 출력자료에 맞추어 다음과 같이 계산하였다.

식 (17)

```
EEMT={C_w OVER 10^6} SUM _{m=1}^{12} T_m (R_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}
```

여기서 \(R_m\)은 월강수량, \(AET_m\)은 월 실제증발산량, \(C_w=4186\) J kg^-1 K^-1, \(h_{BIO}=22 TIMES 10^6\) J kg^-1이며, \(NPP_C\)는 BIOME4가 산출한 연간 carbon NPP이다. \(f_C=0.50\)은 탄소량을 건조생체량으로 환산하기 위하여 적용한 탄소질량분율이다. 식 (17)은 Pelletier et al. (2013)의 EEMT 관계를 BIOME4의 월별 수문출력과 연간 NPP 출력에 적용하기 위하여 본 연구에서 구성한 계산식이다. 월별 \(R_m-AET_m\)이 음수가 되는 경우 이를 0으로 절단하지 않았으며, EEMT에도 별도의 상한 또는 하한을 적용하지 않았다.

## 2.7 BIOME4 기반 지상부 생물량 대리변수

Pelletier et al. (2013)의 사면수송계수에는 AGB가 입력되지만, BIOME4 v4.2b2는 전체 해부학적 지상부 생물량을 별도의 저장량으로 출력하지 않는다. 따라서 본 연구에서는 BIOME4의 우점 PFT와 optimal LAI를 이용하여 잎과 살아 있는 변재의 건조생체량을 합한 지상부 생물량 대리변수 AGB*를 계산하였다. 격자의 우점 PFT를 \(p^*\)라고 하면 AGB*는 다음과 같이 정의된다.

식 (18)

```
AGB^*=B_{leaf,dry,p^*}+B_{sapwood,dry,p^*}
```

잎 건조생체량은 Reich et al. (1992)의 잎수명과 비엽면적(Specific Leaf Area, SLA)의 관계를 이용하였다.

식 (19)

```
log_{10}(SLA_p)=2.44-0.43 log_{10}(L_{m,p})
```

여기서 \(L_{m,p}\)는 PFT \(p\)의 잎수명(month)이다. 원 식의 SLA 단위인 cm^2 g^-1을 m^2 kg^-1로 변환한 뒤, 잎 건조생체량은 다음과 같이 계산하였다.

식 (20)

```
B_{leaf,dry,p}={LAI_p OVER SLA_p}
```

변재는 Haxeltine and Prentice (1996)의 sapwood-LAI 관계를 이용하였다. Haxeltine and Prentice (1996)의 Eq. (34)는 다음과 같다.

식 (21)

```
C_{s,p}=LAI_p C_{n,p}
```

여기서 \(C_{s,p}\)는 PFT \(p\)의 변재 탄소량, \(C_{n,p}\)은 단위 LAI당 변재 탄소량이다. Haxeltine and Prentice (1996)의 BIOME3에서는 \(C_n=1\) kg C m^-2를 사용하였으나, 본 연구에서 실제로 사용한 BIOME4 v4.2b2는 `stemcarbon=0.5`를 사용하고 월별 stem respiration 계산에서 `LAI TIMES stemcarbon`의 형태로 적용한다. 따라서 본 연구에서는 Haxeltine and Prentice (1996)의 관계식 구조를 따르되, 실제 변재 탄소계수에는 BIOME4 v4.2b2의 \(C_n=0.5\)를 적용하였다. 변재 건조생체량은 다음과 같이 계산하였다.

식 (22)

```
B_{sapwood,dry,p}={C_{s,p} OVER f_C}
```

여기서 \(f_C=0.50\)을 사용하였다. BIOME4에서 sapwood respiration을 적용하지 않는 PFT에는 변재항을 적용하지 않았다. 따라서 본 연구의 AGB*는 전체 해부학적 AGB가 아니라 BIOME4에서 직접 연결할 수 있는 잎과 살아 있는 변재를 이용한 지상부 생물량 대리변수이다.

## 2.8 지형발달모델

지형발달은 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 사면세류와 하천침식 과정을 이용하여 계산하였다. 원 논문의 과정별 구조는 유지하되, 본 연구에서는 변수표기의 일관성을 위하여 기반암고도를 \(z_b\), 토심을 \(H\), 정방향 적분시간을 \(tau\)로 통일하였다.

지표고도는 기반암고도와 토심의 합으로 정의하였다.

식 (23)

```
z=z_b+H
```

기반암 또는 풍화전선 고도의 변화는 다음과 같이 계산하였다.

식 (24)

```
{PARTIAL z_b OVER PARTIAL tau}=U-{P OVER cos theta}
```

토심 변화는 다음과 같이 계산하였다.

식 (25)

```
{PARTIAL H OVER PARTIAL tau}={rho_b OVER rho_s}{P OVER cos theta}-E
```

여기서 \(U\)는 regional uplift, \(P\)는 토양생산률, \(rho_b/rho_s\)는 기반암과 토양의 밀도비, \(E\)는 침식 및 물질수송에 따른 순 토양제거율이다.

### 2.8.1 토양생산

토심에 따른 토양생산률은 다음과 같이 계산하였다.

식 (26)

```
P=P_0 exp(-{H cos theta OVER H_0})
```

잠재 토양생산률 \(P_0\)는 EEMT의 함수로 다음과 같이 계산하였다.

식 (27)

```
P_0=a exp(b EEMT)
```

본 연구에서는 \(a=0.037\) m kyr^-1, \(b=0.030\), \(H_0=0.50\) m, \(rho_b/rho_s=1.8\)을 사용하였다(Pelletier et al., 2013).

### 2.8.2 비선형 사면수송

사면수송에 따른 침식 또는 퇴적은 토사유속의 발산으로 계산하였다.

식 (28)

```
E_c=nabla BULLET q
```

토심과 임계경사를 고려한 비선형 사면수송은 다음과 같이 계산하였다.

식 (29)

```
q=-{k_d H cos theta nabla z OVER {1-({|nabla z| OVER S_c})^2}}
```

여기서 \(q\)는 사면방향 토사유속, \(S_c\)는 임계경사, \(k_d\)는 사면수송계수이다. \(k_d\)는 EEMT와 AGB*의 함수로 다음과 같이 계산하였다.

식 (30)

```
k_d=c EEMT+d AGB^*
```

본 연구에서는 \(c=0.033\), \(d=0.050\)을 사용하였으며, Pelletier et al. (2013)의 AGB 항에 본 연구에서 산정한 AGB*를 입력하였다.

Pelletier et al. (2013)은 \(S_c=0.7\)을 기준값으로 사용하고 \(S_c=0.9\)를 민감도 실험에 사용하였다. 그러나 본 연구의 20 m 실제 DEM에서는 이 값을 그대로 적용할 경우 초기 지형의 일부가 곧바로 초임계경사로 처리될 수 있으므로 수치수렴시험을 통해 \(S_c=1.50\)을 사용하였다. 20 m 격자에서 초기 최대 cardinal-face slope는 1.332였으며, \(S_c=1.50\)을 적용했을 때 초기 초임계경사와 threshold adjustment는 발생하지 않았다. 또한 1 kyr 회귀시험에서 수치허용오차를 0.025 m에서 0.0125 m로 절반으로 줄였을 때 최대 토심 차이는 0.008139 m였다. 따라서 \(S_c=1.50\)은 자연사면의 보편적 임계경사를 의미하는 값이 아니라, 초기 DEM을 인위적으로 재성형하지 않으면서 수치수렴을 확보하기 위하여 본 연구의 20 m 격자에 적용한 수치설정이다.

### 2.8.3 사면세류 및 하천침식

사면세류와 하천침식은 다음 식을 이용하여 계산하였다.

식 (31)

```
E_f=K {A OVER w}|nabla z|
```

여기서 \(A\)는 기여면적, \(w\)는 유효 유로폭, \(K\)는 침식계수이다. 사면 셀에서는 격자폭을 유효 유로폭으로 사용하였다.

식 (32)

```
w=Delta x
```

곡저로 분류된 셀에서는 기여면적에 따른 유로폭을 다음과 같이 계산하였다.

식 (33)

```
w=g A^i
```

본 연구에서는 \(g=0.005\), \(i=0.5\)를 사용하였다(Pelletier et al., 2013). 사면과 곡저의 구분은 Pelletier의 grid-dependence 접근을 따라 원 격자와 절반 격자크기에서 계산한 기여면적의 비를 이용하였으며, 그 비가 1.20 미만인 셀을 곡저로 분류하였다.

레골리스의 하천침식계수는 EEMT의 역수에 비례하도록 다음과 같이 계산하였다.

식 (34)

```
K_{reg}={K_0 OVER EEMT}
```

기반암의 침식계수는 다음과 같이 계산하였다.

식 (35)

```
K_{bed}={K_{reg} OVER F}
```

본 연구에서는 \(K_0=0.020\) m^2 MJ^-1, \(F=10\)을 사용하였다(Pelletier et al., 2013). 실제 격자계산에서는 D8 흐름방향의 경사를 사용하였으며, 한 수치적분단계에서 공급 가능한 레골리스보다 많은 양이 제거되지 않도록 finite-supply constraint를 적용하였다.

### 2.8.4 Regional uplift

Pelletier et al. (2013)의 원 모델실험에서는 \(U=0.05\) m kyr^-1을 사용하였으나, 본 연구에서는 태백산맥의 장기 삭박 및 exhumation rate를 고려하여 Lee et al. (2024)이 적용한 80 mm kyr^-1을 regional background forcing으로 사용하였다.

식 (36)

```
U=0.08 m kyr^{-1}=80 mm kyr^{-1}
```

이 값은 연구유역에서 직접 측정한 지각융기율을 의미하지 않으며, 연구지역이 속한 산지의 장기적인 지형발달 배경을 나타내기 위한 지역적 외부강제력으로 적용하였다.

## 2.9 수치적분과 순차결합

기후와 식생은 0.1 kyr 간격으로 갱신하였으며, 지형발달모델은 각 0.1 kyr 구간 내부에서 수치안정성을 만족하도록 적응형 시간간격으로 적분하였다. 기본 explicit timestep은 Pelletier et al. (2013)의 안정성 추정형태를 따라 다음과 같이 계산하였다.

식 (37)

```
Delta tau=0.01 {Delta x^2 OVER {2 k_{d,max}}}
```

여기서 \(Delta x\)는 격자크기, \(k_{d,max}\)는 해당 시점의 최대 사면수송계수이다. 시도한 시간단계에서 사면수송, 유수침식 또는 임계경사 조정에 따른 최대 지형변화가 0.025 m를 초과하면 해당 계산을 폐기하고 동일한 이전 상태에서 더 작은 시간간격으로 다시 계산하였다. 0.025 m는 물리적 또는 생태적 매개변수가 아니라 실제 DEM을 이용한 수치수렴시험에서 설정한 수치오차 허용기준이다. 또한 레골리스의 유한공급 조건, 임계경사 조정 및 단일 유출구의 고정 기준고도 경계조건을 함께 적용하였다.

각 0.1 kyr 구간에서는 먼저 해당 시점의 기후와 현재 토심으로 토양수분 저장량 및 PFT별 뿌리 접근성을 계산하고 BIOME4를 실행하였다. 이후 BIOME4의 NPP와 AET로 EEMT를, LAI와 우점 PFT로 AGB*를 계산하였다. 이 두 변수를 이용하여 같은 100년 구간의 토양생산, 사면수송 및 유수침식을 계산한 뒤 기반암고도와 토심을 갱신하였다. 갱신된 토심은 다음 시점의 토양수분 저장량과 PFT별 뿌리 접근성에 반영되었다. VeSLEM에서 토양과 식생 사이의 피드백은 토심 변화가 식물이 이용할 수 있는 수분량과 뿌리 접근가능 깊이를 변화시키고, 이에 따른 BIOME4의 식생유형과 생산성 변화가 다시 EEMT와 AGB*를 통해 지형발달에 영향을 미치는 방식으로 구성하였다.

## 2.10 정적 실험과 동적 실험

지형 및 토심 변화의 효과를 평가하기 위하여 정적 실험과 동적 실험을 동일한 기후입력으로 수행하였다. 정적 실험에서는 초기 지표고도, 기반암고도 및 토심을 21.0 ka BP부터 0.0 ka BP까지 고정하고, 각 시점의 기후변화에 대해서만 BIOME4를 반복 실행하였다. 따라서 정적 실험에서는 기후변화에 따른 식생반응은 계산되지만 지형 및 토심 변화에 따른 피드백은 발생하지 않는다.

동적 실험에서는 각 0.1 kyr 구간 말에 지형발달모델에서 계산된 기반암고도와 토심을 갱신하고, 식 (23)에 따라 다음 시점의 지표고도를 계산하였다. 갱신된 토심은 다음 시점의 토양수분 저장량과 PFT별 뿌리 접근성에 반영되며, 이에 따라 BIOME4의 NPP, LAI 및 우점 PFT가 변화할 수 있다. 변화한 식생조건은 다시 EEMT와 AGB*를 통해 다음 지형발달 계산에 입력하였다. 정적 실험과 동적 실험의 차이는 동일한 기후변화 조건에서 토심과 지형의 시간적 변화를 식생계산에 되먹임하는지 여부에 있다.

## 2.11 고식생 자료를 이용한 검증

고식생 복원결과의 정량검증에는 Jang et al. (2011)의 대암산 용늪 화분기록을 이용하였다. Jang et al. (2011)이 구분한 네 개의 local pollen zone 연대범위를 0.1 kyr 간격의 모델 출력시점과 대응시켜 총 62개의 평가시점을 구성하였다. 따라서 본 연구에서 사용한 \(n=62\)는 화분시료의 개수가 아니라 네 식생대의 연대범위를 100년 간격 모델출력과 대응시킨 평가항목의 수이다.

BIOME4의 혼효림 출력은 검증을 위하여 침엽수군과 활엽수군의 잠재 NPP를 이용하여 후처리하였다. 한 식생군이 비교대상 두 군의 51% 이상을 차지하면 해당 식생군으로 분류하고, 어느 군도 51%에 도달하지 않으면 혼효림으로 유지하였다. 이 기준은 BIOME4 내부의 PFT 경쟁임계값이 아니라 고식생 자료와의 비교를 위하여 적용한 검증용 후처리 기준이다.

각 평가시점에서는 Jang et al. (2011)의 해당 식생군이 모의유역 내 유효격자의 1% 이상에서 출현하면 일치한 것으로 판정하였다. 이 1% 기준은 유역규모의 모의결과와 지점 화분기록을 비교하기 위한 검증기준으로 설정하였다. Park et al. (2021)의 자료는 Jang et al. (2011)을 이용한 정량 정확도 산정과 구분하여 보조적으로 비교하였다.


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

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k: High-resolution 1 km downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. https://doi.org/10.5194/esurf-12-1091-2024

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology.

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116

Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H., & Dai, Y. (2017). Mapping the global depth to bedrock for land surface modeling. *Journal of Advances in Modeling Earth Systems, 9*(1), 65-88. https://doi.org/10.1002/2016MS000686

Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L., & Heuvelink, G. B. M. (2023). Global mapping of volumetric water retention at 100, 330 and 15,000 cm suction using the WoSIS database. *International Soil and Water Conservation Research, 11*(2), 225-239. https://doi.org/10.1016/j.iswcr.2022.08.001
