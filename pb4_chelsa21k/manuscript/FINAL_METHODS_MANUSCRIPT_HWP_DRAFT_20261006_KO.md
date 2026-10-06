# VeSLEM Methods 한글 수식편집기 입력본

작성일: 2026-10-06  
대상: 용늪 VeSLEM 최종 논문 Methods 초안  
기준 production: `6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`  
canonical SHA-256: `0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4`

## 작성 원칙

- 아래 모든 제시식은 한글 수식편집기 하단 스크립트 입력창에 복사할 수 있는 형식으로 기록하였다.
- McKenzie et al. (2003)의 원 개념과 본 연구의 BIOME4 결합식을 구분하였다.
- Pelletier et al. (2013)의 원 과정식은 서로 대입해 하나의 통합식으로 만들지 않았다.
- CHELSA-TraCE21k 기온과 강수에는 추가 고도감률 보정을 적용하지 않았다. Beyer et al. (2020)은 cloudiness 보조자료로만 사용하였다.
- 최종 지형계산은 20 m real DEM 기준이며, S_c=1.50은 이 격자에서의 수치수렴 설정이다.

# 2. 연구방법

## 2.1 연구 설계와 VeSLEM의 결합 구조

본 연구는 후기 빙기 이후 기후변화에 따른 식생, 토양 및 지형의 장기 상호작용을 모의하기 위하여 평형 식생모델 BIOME4 v4.2b2와 Pelletier et al. (2013)의 수치지형발달모델을 결합한 식생-토양-지형발달모델(Vegetation-Soil-Landscape Evolution Model, VeSLEM)을 구축하였다. BIOME4는 기후, 대기 CO2 및 토양수분 조건에 따라 식물 기능형(Plant Functional Type, PFT)별 NPP와 LAI를 계산하고, PFT 간 경쟁을 통해 잠재 식생을 판정하는 평형 식생모델이다(Kaplan, 2001; Kaplan et al., 2003). 본 연구는 BIOME4 v4.2b2의 native PFT climate limits를 유지하였으며, 토심에 따른 NPP, LAI 또는 식생피복률의 직접적인 경험 보정계수는 사용하지 않았다.

분석기간은 21.0 ka BP부터 0.0 ka BP까지로 설정하였고, 식생과 지형의 결합간격은 0.1 kyr, 즉 100년으로 설정하였다. 따라서 전체 기간은 211개 시간시점으로 구성하였다. 각 100년 결합구간의 시작에서 해당 시점의 기후와 현재 토심을 이용하여 토양수분 저장량 및 PFT별 뿌리 접근성을 계산한 뒤 BIOME4를 한 번 실행하였다. BIOME4가 산출한 NPP, AET, LAI 및 우점 PFT를 이용하여 EEMT와 지상부 생물량 대리변수인 AGB*를 계산하고, 이를 동일한 100년 구간의 지형발달 forcing으로 사용하였다. 지형발달모델은 각 100년 구간 내부에서 수치안정성을 위한 adaptive substep으로 적분하였으며, substep 사이에는 BIOME4를 다시 실행하지 않았다. 구간 말에 갱신된 기반암고도와 토심은 다음 100년 시점의 BIOME4 계산에 전달하였다.

지표고도 z, 기반암 또는 풍화전선 고도 z_b, 토심 H의 관계는 다음과 같이 정의하였다.

식 (1)

```
H=z-z_b
```

연대 좌표는 t_BP, 정방향 모델 적분시간은 tau로 구분하였다.

## 2.2 공간 입력자료와 전처리

고도자료는 국토정보플랫폼에서 제공하는 수치지형도를 이용하였다. QGIS 3.44.5에서 역거리가중법(Inverse Distance Weighting, IDW)을 이용하여 10 m 해상도의 연속 고도면을 구축하고, GRASS GIS의 r.watershed를 이용하여 대암산 용늪을 포함하는 소유역을 추출하였다. 이후 고도, 토심 및 토양 관련 공간자료를 Korea 2000/Central Belt 2010 좌표계(EPSG:5187)로 통일하고 20 m 격자로 리샘플링하여 최종 VeSLEM 계산격자를 구성하였다. 따라서 10 m는 수치지형도 보간 단계의 해상도이고, 실제 지형발달모델의 계산 해상도는 20 m이다.

유역 경계에서는 지정한 단일 유출구만 열린 경계로 두고 나머지 경계는 닫힌 경계로 처리하였다. D8 흐름에서는 유출구 셀에서만 유역 외부로의 유출을 허용하였고, 그 외 경계 셀에서 유역 외부로 향하는 흐름은 허용하지 않았다. 사면 물질수송 역시 계산 마스크 내부의 인접 셀 사이에서만 계산하여 닫힌 경계를 가로지르는 유출량을 0으로 두었다. D8 흐름 계산에서 내부 폐쇄가 발생하지 않도록 흐름경로 계산 전에 싱크 채우기를 적용하였다.

초기 토심은 SoilGrids250m 자료를 1 km로 집계한 과거 ISRIC 배포본의 기반암 깊이 자료 `BDRICM_M_1km_ll`을 이용하였다(Hengl et al., 2017; Shangguan et al., 2017). 해당 파일은 ISRIC의 2017-03-10 SoilGrids archive의 aggregated/1km 자료에 포함된다. 토양수분 저장량 계산에는 SoilGrids 기반의 용늪 지점 수분특성 profile을 사용하였다. 최종 production source에는 128.1236 E, 38.2153 N 지점에서 확보한 10 kPa와 1500 kPa 체적수분함량의 차이, 즉 theta_{-10}-theta_{-1500}를 각 깊이구간에 직접 입력하였다. SoilGrids에서 wv0010은 10 kPa의 체적수분함량, wv1500은 1500 kPa의 체적수분함량을 의미하며, 두 자료는 0-5, 5-15, 15-30, 30-60, 60-100 및 100-200 cm의 여섯 표준 깊이구간으로 제공된다(Turek et al., 2023). 별도의 pedotransfer function, 자갈함량 보정, 경험적 보정 또는 화분자료 적합계수는 적용하지 않았다. 깊이별 available-water density는 0-0.05 m에서 237 mm m^-1, 0.05-0.15 m에서 232 mm m^-1, 0.15-0.30 m에서 218 mm m^-1, 0.30-0.60 m에서 207 mm m^-1, 0.60-1.00 m에서 198 mm m^-1, 1.00-2.00 m에서 179 mm m^-1을 사용하였다. BIOME4의 수문구조상 실제 적분은 최대 1.50 m까지만 수행하였다.

최종 production에 제공된 토성 격자는 모든 유효 셀에서 BIOME4 texture class 2로 판정되었다. 이 토성정보는 BIOME4의 기존 hydraulic conductivity 값을 선택하는 데 사용하였으며, 위 available-water density profile 자체는 모래, 실트 및 점토 비율로부터 본 연구에서 새롭게 추정한 값이 아니라 SoilGrids에서 확보한 theta_{-10}과 theta_{-1500}의 차이를 사용하였다.

## 2.3 기후 및 대기 CO2 forcing

기온과 강수량은 CHELSA-TraCE21k의 월별 자료를 사용하였다(Karger et al., 2023). 사용한 production forcing 파일은 `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`이며, 21.0-0.0 ka BP의 0.1 kyr 간격 자료를 이용하였다. CHELSA-TraCE21k의 월별 최저기온과 최고기온은 Kelvin 단위이므로 월평균기온은 다음과 같이 변환하였다.

식 (2)

```
T_m={(T_{min,m}+T_{max,m}) OVER 2}-273.15
```

CHELSA-TraCE21k는 지형효과를 고려하여 하향화된 자료이므로 본 연구에서는 추가적인 고도감률 보정을 적용하지 않았다. 따라서 이전 방법론에서 사용하였던 현재 고도에 따른 셀별 기온 보정식은 최종 VeSLEM에서 사용하지 않았다. 지형발달에 따른 고도 변화가 다시 월기온을 변화시키는 별도의 lapse-rate feedback도 적용하지 않았다.

CHELSA-TraCE21k의 Centennial forcing에는 BIOME4의 광환경 계산에 필요한 cloudiness가 포함되어 있지 않으므로, cloudiness만 Beyer et al. (2020)의 후기 제4기 기후자료에서 추출하여 각 시점에 시간보간하였다. Beyer et al. (2020)의 기온과 강수량은 최종 production에 사용하지 않았다. 대기 CO2 forcing은 Bereiter et al. (2015)의 revised Antarctic composite를 각 t_BP에 선형보간하여 사용하였다.

BIOME4의 absolute minimum temperature는 v4.2b2 원 코드의 회귀식을 그대로 사용하였다.

식 (3)

```
T_{absmin}=0.006 T_{cold}^2+1.316 T_{cold}-21.9
```

여기서 T_cold는 가장 추운 달의 월평균기온이다.

## 2.4 토심에 따른 available-water storage

토심이 BIOME4 수문상태에 미치는 영향은 McKenzie et al. (2003)의 profile available water capacity 개념을 이용하여 구현하였다. McKenzie et al. (2003)은 profile available water capacity를 약 -10 kPa와 -1.5 MPa에서의 체적수분함량 차이를 토양깊이에 대해 적분한 양으로 정의하였다. 이를 본 연구의 표기로 나타내면 깊이 zeta에서의 available-water density는 다음과 같다.

식 (4)

```
AWC(zeta)=theta_{-10}(zeta)-theta_{-1500}(zeta)
```

식 (4)는 McKenzie et al. (2003)의 개념적 정의를 본 연구의 기호로 나타낸 것이며, McKenzie의 번호식 자체를 그대로 옮긴 것은 아니다.

BIOME4 v4.2b2의 기존 수문구조를 유지하기 위해 상층은 0-0.30 m, 하층은 0.30-1.50 m로 구분하였다. 실제 토심 H에 따른 각 층의 available-water storage는 다음과 같이 계산하였다.

식 (5)

```
W_{top}(H)=1000 INT _0^{min(H,0.30)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

식 (6)

```
W_{bottom}(H)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} [theta_{-10}(zeta)-theta_{-1500}(zeta)] d zeta
```

식 (5)와 식 (6)은 McKenzie et al. (2003)의 profile available-water 개념을 BIOME4의 2층 수문구조에 연결한 본 연구의 구현식이다. 즉 McKenzie et al. (2003)이 BIOME4용 0-0.30 m 및 0.30-1.50 m 수문층을 제시한 것은 아니다.

## 2.5 PFT별 finite-depth root accessibility

뿌리 수직분포는 Gale and Grigal (1987)의 누적분포식과 Jackson et al. (1996)의 전지구 뿌리분포 자료를 이용하였다.

식 (7)

```
Y(d)=1-beta^d
```

여기서 Y(d)는 지표에서 깊이 d까지 존재하는 누적 뿌리분율이다. BIOME4 v4.2b2의 pftpar(pft,6)은 PFT별 상부 30 cm 누적 뿌리분율을 나타내며, 본 연구에서는 이를 r_{30,p}로 표기하였다.

McKenzie et al. (2003)은 plant available water capacity를 계산할 때 깊이에 따른 뿌리밀도 감소를 다음의 지수함수로 나타냈다.

식 (8)

```
f(x)=exp(-{x OVER X_i})
```

여기서 X_i는 해당 깊이보다 아래에 약 37%의 뿌리가 존재하는 특성깊이이다. McKenzie et al. (2003)의 지수형식을 BIOME4의 PFT별 상부 30 cm 뿌리분율과 연결하기 위하여, 본 연구에서는 PFT별 특성깊이 X_p를 다음과 같이 분석적으로 계산하였다.

식 (9)

```
X_p=-{0.30 OVER ln(1-r_{30,p})}
```

식 (9)는 McKenzie et al. (2003) 또는 Jackson et al. (1996)의 원식이 아니라, 두 자료구조를 연결하기 위한 본 연구의 분석적 변환이다.

BIOME4에 전달되는 유효 토심은 다음과 같이 제한하였다.

식 (10)

```
D=min(max(H,0),1.50)
```

실제 토심 안에서 접근 가능한 상층 뿌리분율은 다음과 같이 계산하였다.

식 (11)

```
R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})
```

하층 뿌리분율은 다음과 같이 계산하였다.

식 (12)

```
R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}
```

PFT별 root-zone wetness는 다음과 같이 BIOME4 수문계산에 전달하였다.

식 (13)

```
omega_{r,p}=R_{top,p} omega_{top}+R_{bottom,p} omega_{bottom}
```

얕은 토양에서 R_{top,p}+R_{bottom,p}<1이 되더라도 이를 1로 재정규화하지 않았다. 따라서 실제 토심 아래에 위치할 뿌리분율을 상부 토양층으로 인위적으로 재배치하지 않았다.

## 2.6 EEMT 산정

식생과 수문상태를 지형발달모델에 연결하기 위해 Pelletier et al. (2013)의 유효 에너지 및 물질 전달량(Effective Energy and Mass Transfer, EEMT)을 사용하였다. Pelletier et al. (2013)은 유효강수에 의해 공급되는 에너지와 생물생산에 축적되는 에너지를 각각 다음과 같이 정의하였다.

식 (14)

```
E_{PPT}=Delta T C_w P_{eff}
```

식 (15)

```
E_{BIO}=NPP h_{BIO}
```

따라서 EEMT는 두 성분의 합으로 정의된다.

식 (16)

```
EEMT=E_{PPT}+E_{BIO}
```

여기서 P_eff=PPT-ET이다. 본 연구에서는 BIOME4가 월별 AET와 연간 carbon NPP를 산출하므로, Pelletier et al. (2013)의 관계를 다음과 같이 월별 forcing에 적용하였다.

식 (17)

```
EEMT={C_w OVER 10^6} SUM _{m=1}^{12} T_m (R_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}
```

여기서 R_m은 월강수량, AET_m은 월 실제증발산량, C_w=4186 J kg^-1 K^-1, h_BIO=22 TIMES 10^6 J kg^-1이며, NPP_C는 BIOME4가 출력하는 연간 carbon NPP이다. f_C=0.50은 carbon mass를 dry biomass로 변환하기 위한 본 연구의 명시적 가정이다. 식 (17)은 Pelletier et al. (2013)의 별도 원식이 아니라 원 EEMT 관계를 BIOME4 출력에 적용한 본 연구 구현식이다. R_m-AET_m은 0으로 clipping하지 않았으며, EEMT에도 별도의 상한 및 하한 clipping을 적용하지 않았다.

## 2.7 BIOME4-derived AGB*

Pelletier et al. (2013)의 사면수송계수에는 AGB가 입력되지만 BIOME4 v4.2b2는 total anatomical AGB를 별도의 standing stock으로 출력하지 않는다. 따라서 본 연구에서는 BIOME4의 우점 PFT와 optimal LAI를 이용하여 잎과 살아 있는 변재를 합한 BIOME4-derived aboveground living biomass proxy인 AGB*를 계산하였다. 각 격자의 우점 PFT를 p*라고 하면 다음과 같이 정의하였다.

식 (18)

```
AGB^*=B_{leaf,dry,p^*}+B_{sapwood,dry,p^*}
```

잎 건조생체량은 Reich et al. (1992)의 leaf life-span과 SLA 관계를 사용하였다.

식 (19)

```
log_{10}(SLA_p)=2.44-0.43 log_{10}(L_{m,p})
```

여기서 L_{m,p}는 PFT p의 잎수명이며 단위는 month이고, SLA의 원 단위는 cm^2 g^-1이다. SLA를 m^2 kg^-1로 변환한 뒤 잎 건조생체량은 정의에 따라 다음과 같이 계산하였다.

식 (20)

```
B_{leaf,dry,p}={LAI_p OVER SLA_p}
```

변재는 Haxeltine and Prentice (1996)의 sapwood-LAI 관계를 사용하였다. Haxeltine and Prentice (1996)의 Eq. (34)는 다음과 같다.

식 (21)

```
C_s=LAI C_n
```

여기서 C_s는 총 sapwood carbon content(kg C m^-2), C_n은 단위 LAI당 sapwood carbon content(kg C m^-2)이다. Haxeltine and Prentice (1996)의 BIOME3에서는 여러 자료를 종합하여 C_n=1 kg C m^-2를 사용하였다. 반면 본 연구에서 실제로 실행한 BIOME4 v4.2b2 source는 동일한 구조의 sapwood-LAI 관계를 유지하면서 `stemcarbon=0.5`를 사용하고, 월별 stem respiration 계산에서 `lai*stemcarbon`으로 적용한다. 따라서 본 연구에서는 Haxeltine and Prentice (1996)에서 관계식의 구조를, BIOME4 v4.2b2 source에서 실제 계수 C_n=0.5를 가져와 사용하였다. 즉 C_n=0.5를 Haxeltine and Prentice (1996)의 값으로 해석하지 않는다. 변재 dry biomass는 다음과 같이 계산하였다.

식 (22)

```
B_{sapwood,dry,p}={C_{sapwood,p} OVER f_C}
```

여기서 f_C=0.50을 사용하였다. BIOME4 source에서 sapwood respiration을 제거하는 PFT에는 sapwood 항을 적용하지 않았다. 따라서 AGB*는 total anatomical AGB가 아니라 BIOME4가 추적할 수 있는 foliage와 living sapwood를 이용한 aboveground living biomass proxy이다.

## 2.8 Pelletier 지형발달모델

지형발달에는 Pelletier et al. (2013)의 토양생산, 비선형 사면수송 및 slope-wash/fluvial erosion 구조를 사용하였다. 원 논문의 과정식 구조는 유지하되 변수표기의 일관성을 위해 기반암고도는 z_b, 토심은 H, 정방향 적분시간은 tau로 통일하였다.

지표고도는 다음과 같이 정의하였다.

식 (23)

```
z=z_b+H
```

기반암 또는 풍화전선 고도의 변화는 다음과 같이 계산하였다.

식 (24)

```
{PARTIAL z_b OVER PARTIAL tau}=U-{P OVER cos theta}
```

토심의 변화는 다음과 같이 계산하였다.

식 (25)

```
{PARTIAL H OVER PARTIAL tau}={rho_b OVER rho_s}{P OVER cos theta}-E
```

여기서 U는 regional uplift forcing, P는 토양생산률, rho_b/rho_s는 기반암과 토양의 밀도비, E는 침식 및 수송에 의한 순 토양 제거항이다.

### 2.8.1 토양생산

토심에 따른 토양생산률은 다음과 같이 계산하였다.

식 (26)

```
P=P_0 exp(-{H cos theta OVER H_0})
```

잠재 토양생산률 P_0는 EEMT의 함수로 다음과 같이 계산하였다.

식 (27)

```
P_0=a exp(b EEMT)
```

Production에서는 a=0.037 m kyr^-1, b=0.030, H_0=0.50 m, rho_b/rho_s=1.8을 사용하였다(Pelletier et al., 2013).

### 2.8.2 비선형 사면수송

사면수송에 의한 침식 또는 퇴적항은 다음과 같이 계산하였다.

식 (28)

```
E_c=nabla BULLET q
```

토심과 임계경사를 고려한 비선형 사면수송은 다음과 같다.

식 (29)

```
q=-{k_d H cos theta nabla z OVER {1-({|nabla z| OVER S_c})^2}}
```

기후와 식생에 따른 사면수송계수는 다음과 같이 계산하였다.

식 (30)

```
k_d=c EEMT+d AGB^*
```

Production에서는 c=0.033, d=0.050을 사용하였다. Pelletier et al. (2013)의 원식에서 AGB가 위치한 항에 본 연구의 BIOME4-derived AGB*를 입력하였다.

Pelletier et al. (2013)은 S_c=0.7을 기준값으로 사용하고 0.9를 민감도 실험에 사용하였다. 본 연구에서는 20 m real DEM의 수치수렴시험을 바탕으로 S_c=1.50을 사용하였다. 20 m 격자에서 초기 최대 cardinal-face slope는 1.332였으며 S_c=1.50 적용 시 초기 초임계경사 및 threshold adjustment가 발생하지 않았다. 또한 1 kyr 회귀시험에서 수치허용오차를 0.025 m에서 0.0125 m로 절반으로 줄였을 때 최대 토심 차이는 0.008139 m였다. 따라서 S_c=1.50은 Pelletier et al. (2013)의 원 연구값이나 자연사면의 보편적 임계경사가 아니라, 초기 DEM을 인위적으로 재성형하지 않으면서 수치수렴을 확보하기 위해 채택한 본 연구의 20 m raster 수치설정이다.

### 2.8.3 slope-wash 및 fluvial erosion

Slope-wash 및 fluvial erosion은 다음 식을 사용하였다.

식 (31)

```
E_f=K {A OVER w}|nabla z|
```

여기서 A는 contributing area, w는 유효 유로폭이다. Hillslope의 sheet-flow 셀에서는 다음과 같이 grid-cell width를 사용하였다.

식 (32)

```
w=Delta x
```

Tributary-valley 셀에서는 다음 관계를 사용하였다.

식 (33)

```
w=g A^i
```

원 연구와 동일하게 g=0.005, i=0.5의 구조를 유지하였다. Regolith의 fluvial erodibility는 다음과 같이 계산하였다.

식 (34)

```
K_{reg}={K_0 OVER EEMT}
```

Bedrock의 erodibility는 다음과 같이 계산하였다.

식 (35)

```
K_{bed}={K_{reg} OVER F}
```

Production에서는 K_0=0.020 m^2 MJ^-1, F=10을 사용하였다(Pelletier et al., 2013). 실제 raster 계산에서는 flow-routing 방향의 경사를 사용하였고, 한 substep에서 donor cell의 가용 레골리스보다 많은 물질이 제거되지 않도록 finite-supply constraint를 적용하였다.

### 2.8.4 Regional uplift

Pelletier et al. (2013)의 원 모델실험은 U=0.05 m kyr^-1을 사용하였으나, 본 연구의 최종 production은 다음 값을 사용하였다.

식 (36)

```
U=0.08 m kyr^{-1}=80 mm kyr^{-1}
```

Lee et al. (2024)은 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate와 동일하도록 landscape-evolution model의 regional uplift를 80 mm kyr^-1로 설정하였다. 본 연구에서는 이 값을 장기적인 regional background forcing으로 사용하였다. 이 값은 용늪에서 직접 측정된 지각융기율이 아니다.

## 2.9 수치 적분 및 순차 결합

기후와 식생은 0.1 kyr 간격으로 갱신하였으며, 지형발달모델은 각 0.1 kyr 구간 내부에서 adaptive substep으로 적분하였다. 기본 explicit timestep은 Pelletier et al. (2013)의 안정성 추정형태를 따라 다음과 같이 설정하였다.

식 (37)

```
Delta tau=0.01 {Delta x^2 OVER {2 k_{d,max}}}
```

Trial step에서 사면수송, 유수침식 또는 threshold-slope adjustment에 의한 최대 변화량이 0.025 m를 초과하면 해당 trial을 폐기하고, 동일한 accepted state에서 더 작은 timestep으로 재계산하였다. 0.025 m는 물리적 또는 생태적 파라미터가 아니라 용늪 real-DEM convergence audit에서 채택한 수치오차 허용기준이다. 또한 finite-supply constraint, threshold-slope adjustment 및 open outlet의 fixed base-level boundary를 적용하였다.

한 0.1 kyr 구간의 계산순서는 다음과 같다.

```
현재 z, z_b, H
-> 해당 t_BP의 CHELSA 기후
-> 토심별 available-water storage
-> PFT별 finite-depth root accessibility
-> BIOME4
-> NPP, AET, LAI, dominant PFT
-> EEMT, AGB*
-> Pelletier 지형발달모델
-> 새로운 z_b, H 및 z
-> 다음 t_BP
```

현재 production에서는 CHELSA 기온에 고도감률을 다시 적용하지 않으므로, 지형고도 변화가 별도의 셀별 기온 변화로 BIOME4에 재입력되지는 않는다. 동적 식생 feedback에서 가장 직접적인 토양-식생 연결은 갱신된 토심이 available-water storage와 PFT별 root accessibility를 변화시키고, 이것이 BIOME4의 수분스트레스, NPP 및 식생경쟁에 영향을 미치는 경로이다.

## 2.10 정적 및 동적 실험

정적 실험에서는 초기 지표고도, 기반암고도 및 토심을 전체 기간 동안 고정하고 21.0-0.0 ka BP의 기후 forcing에 대해서만 BIOME4를 반복 실행하였다. 따라서 기후변화에 대한 식생반응은 계산되지만 지형과 토심의 feedback은 발생하지 않는다.

동적 실험에서는 각 0.1 kyr 구간의 말에 지형발달모델이 계산한 z_b와 H를 갱신하고, z=z_b+H로 다음 시점의 지표고도를 정의하였다. 갱신된 H는 다음 시점의 available-water storage와 root accessibility에 반영되고, 이에 따라 BIOME4의 수분상태, NPP, LAI 및 우점 PFT가 달라질 수 있다. 변화한 식생은 다시 EEMT와 AGB*를 통해 다음 지형발달 계산에 입력하였다.

## 2.11 고식생 검증

최종 정량검증에는 Jang et al. (2011)의 대암산 용늪 화분기록을 사용하였다. Jang et al. (2011)이 구분한 네 local pollen zone의 연대구간을 0.1 kyr 간격의 모델 출력시점에 대응시켜 총 62개의 모델 평가시점을 구성하였다. 따라서 n=62는 화분시료수가 아니라 네 식생대의 연대범위를 100년 모델 출력격자에 대응시킨 평가항목수이다.

BIOME4의 mixed forest 출력은 검증을 위해 침엽수군과 활엽수군의 최대 잠재 NPP를 비교하여 재분류하였다. 한 식생군의 비율이 51% 이상이면 해당 군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 유지하였다. 이 51% 기준은 BIOME4 내부 경쟁과정의 임계값이 아니라 검증용 후처리 기준이다.

각 평가시점에서 Jang et al. (2011)에 해당하는 식생군이 모의 유역 유효격자의 1% 이상에서 출현하면 일치로 판정하였다. 1% 기준 역시 BIOME4 또는 Pelletier 모델 내부 파라미터가 아니라 본 연구의 검증 판정기준이다. Park et al. (2021)은 최종 Jang 정확도 점수의 산정에는 포함하지 않았다.

## 2.12 재현성

최종 production model은 `6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`이며 canonical SHA-256은 `0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4`이다. 기후 forcing은 `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`를 사용하였으며, 21.0-0.0 ka BP의 211개 시점에 대해 정적 및 동적 실험을 동일 forcing으로 수행하였다. 최종 production의 regional uplift는 U=0.08 m kyr^-1이며, 이전 U=0.20 m kyr^-1 버전은 `U020_PRE_UFIX` archive로 보존하였다.

## 참고문헌

Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S., & Chappellaz, J. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*, 693-709. https://doi.org/10.1029/96GB02344

Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S., & Kempen, B. (2017). SoilGrids250m: Global gridded soil information based on machine learning. *PLoS ONE, 12*(2), e0169748. https://doi.org/10.1371/journal.pone.0169748

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*, 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling*. Doctoral dissertation, Lund University.

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2023). CHELSA-TraCE21k: High-resolution 1 km downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. https://doi.org/10.5194/esurf-12-1091-2024

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology.

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., & Rossiter, D. (2021). SoilGrids 2.0: Producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116


Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H., & Dai, Y. (2017). Mapping the global depth to bedrock for land surface modeling. *Journal of Advances in Modeling Earth Systems, 9*(1), 65-88. https://doi.org/10.1002/2016MS000686

Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L., & Heuvelink, G. B. M. (2023). Global mapping of volumetric water retention at 100, 330 and 15,000 cm suction using the WoSIS database. *International Soil and Water Conservation Research, 11*(2), 225-239. https://doi.org/10.1016/j.iswcr.2022.08.001
