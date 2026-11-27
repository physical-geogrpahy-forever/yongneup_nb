2) 연구 방법

(1) 식생-토양-지형발달모델의 구성

본 연구는 정적 식생모델인 BIOME4 v4.2b2(Kaplan et al., 2003)와 Pelletier et al.(2013)의 지형발달모델을 토양으로 결합하여 식생-토양-지형발달모델(VeSLEM)을 구성하였다(그림 ?). BIOME4는 각 시점의 기후, 대기 중 CO2 농도, 토양수분보유능력을 입력으로 격자별 식생유형과 순일차생산량(NPP), 엽면적지수(LAI), 실제증발산량을 계산하며, 지형발달모델은 이로부터 구한 유효에너지질량전달(EEMT)과 지상부 생체량(AGB)을 이용하여 다음 시점까지의 기반암 풍화, 사면 물질이동, 유수침식, 융기에 따른 고도와 토심의 변화를 계산한다. 변화한 토심은 다시 다음 시점 BIOME4의 토양수분보유능력과 뿌리 분포에 반영되며, 이를 통해 식생의 생산성이 토양생성과 지형발달에 영향을 미치고 지형발달에 따른 토심 변화가 다시 식생유형과 생산성에 영향을 미치는 양방향 결합을 구현하였다.

(2) 식생모델

BIOME4는 BIOME3(Haxeltine & Prentice, 1996)를 발전시킨 탄소와 수분 플럭스 결합 모델로, 월평균 기온, 강수량, 운량, 대기 중 CO2 농도와 토양 특성을 이용하여 평형 상태의 식생 분포와 구조, 생지화학적 특성을 계산한다(Kaplan, 2001; Kaplan et al., 2003). 생물기후적 한계값을 만족하는 식물기능형(PFT)마다 일 단위 토양수분수지와 월 단위 광합성, 호흡, 생물계절 계산을 통해 NPP를 최대화하는 LAI와 그때의 NPP를 구하고, NPP, LAI, 연평균 토양수분으로 우점 PFT와 부우점 PFT를 정한 뒤 그 조합과 환경 조건에 따라 28개 생물군계 중 하나를 판정한다(Kaplan et al., 2003). 본 연구에서는 생물기후적 한계값, 생리 계수, 판정 규칙을 BIOME4 v4.2b2 원본 코드(Kaplan, 1999)대로 두고, 토심의 변화가 식생 계산에 반영되도록 다음 세 가지를 수정하였다.

① 토양수분보유능력

BIOME4는 토양을 상층(0-30 cm)과 하층으로 나누어 토양수분수지를 계산한다(Kaplan, 1999). 본 연구에서는 하층을 0.3-1.5 m로 두고, 각 층의 토양수분보유능력(WHC)을 매 시점의 토심(H)까지 적분하여 구하였다(식 1).

$$WHC(H) = 1000\int_{0}^{\min(H,\,0.3)} \left[\theta_{-10}(\xi) - \theta_{-1500}(\xi)\right] d\xi + 1000\int_{0.3}^{\min(\max(H,\,0.3),\,1.5)} \left[\theta_{-10}(\xi) - \theta_{-1500}(\xi)\right] d\xi \tag{1}$$

식 (1)에서 ξ[m]는 깊이, θ−10과 θ−1500[m³/m³]은 −10 kPa와 −1500 kPa에서의 체적수분함량이며, 둘의 차이를 식물이 이용할 수 있는 수분량으로 보았다(McKenzie et al., 2003). 깊이별 값은 SoilGrids의 수분보유 자료(Turek et al., 2023)에서 용늪 지점의 값을 사용하였고, 각 깊이 구간 안에서는 일정하다고 가정하였다(표 2). 또한, SoilGrids 2.0(Poggio et al., 2021)의 모래, 미사, 점토 함량에 따르면 유역 전체가 FAO-UNESCO(1974)의 중립질에 해당하므로(그림 ?), 투수 지수는 BIOME4의 중립질 값을 사용하였다(Kaplan, 1999).

표 2. 연구 지역의 깊이별 식물 이용 가능 수분량(θ−10 − θ−1500)

| 깊이 (cm) | 0-5 | 5-15 | 15-30 | 30-60 | 60-100 | 100-200 |
|---|---:|---:|---:|---:|---:|---:|
| 식물 이용 가능 수분량 (mm/m) | 237 | 232 | 218 | 207 | 198 | 179 |

② 뿌리 분포와 근권 토양수분

BIOME4는 PFT별 상층 뿌리 비율(r30)로 상층과 하층의 상대 토양수분(W1, W2)을 가중평균하여 근권 토양수분을 구한다(Kaplan, 1999, 2001). 그러나 토심이 1.5 m보다 얕으면 하층의 일부 또는 전부가 존재하지 않으므로, 본 연구에서는 Jackson et al.(1996)의 누적 뿌리분포식(Y = 1 − β^d)을 이용하여 뿌리 분포를 토심에서 잘랐다. 먼저 r30으로 PFT별 β를 구하고(식 2), 토심 안의 상층과 하층 뿌리 비율(식 3)로 근권 토양수분(Wr)을 계산하였다(식 4).

$$\beta = (1 - r_{30})^{1/30} \tag{2}$$

$$r_{top} = 1 - \beta^{\min(d,\,30)}, \qquad r_{bottom} = \beta^{30} - \beta^{\min(d,\,150)} \tag{3}$$

$$W_r = r_{top}\,W_1 + r_{bottom}\,W_2 \tag{4}$$

식 (2)-(4)에서 d[cm]는 토심이며, 토심이 30 cm 이하이면 rbottom은 0이다. 토심이 얕을수록 rtop과 rbottom의 합은 1보다 작아지며, 상층 뿌리 비율이 낮은 PFT일수록 이용할 수 있는 수분이 크게 줄어든다. 이렇게 구한 Wr은 증산 공급량, 잎의 전개와 낙엽 시기, 우점 PFT와 생물군계 판정에 쓰이는 연평균 토양수분의 계산에 사용하였다.

③ 기반암 노출 격자

토심이 10⁻⁶ m 이하인 격자는 기반암 노출 격자로 보아 BIOME4 계산에서 제외하고 무식생으로 처리하였으며, 실제증발산량, NPP, AGB는 0으로 두었다.

(3) 지형발달모델

Pelletier et al.(2013)은 토층이 덮인 산지 사면이 기반암의 물리적 풍화에 의한 레골리스 생성과 사면 물질이동에 의한 제거로 발달하며, 레골리스 두께는 이 둘의 장기적인 균형으로 정해진다고 보고, 지표 고도, 기반암 고도, 레골리스 두께를 식 (5)-(7)과 같이 나타내었다.

$$z = b + H \tag{5}$$

$$\frac{\partial b}{\partial t} = U - \frac{P}{\cos\theta} \tag{6}$$

$$\frac{\partial H}{\partial t} = \frac{\rho_r}{\rho_s}\frac{P}{\cos\theta} - E_c - E_f \tag{7}$$

식 (5)-(7)에서 z[m]는 지표 고도, b[m]는 기반암 또는 풍화전선의 고도, H[m]는 레골리스 두께, t[kyr]는 시간, U[m/kyr]는 융기율, P[m/kyr]는 사면에 수직인 방향의 기반암 후퇴율, θ는 사면각, ρr/ρs는 기반암과 레골리스의 밀도비, Ec와 Ef[m/kyr]는 사면 물질이동과 유수에 의한 침식률이다. Pelletier et al.(2013)은 연구 지역의 화강암질 토양에 새프롤라이트가 거의 없어 레골리스 두께를 토양 두께로 보았으며, 본 연구에서도 레골리스 두께를 토심으로 사용하였다. 밀도비는 화강암질 기반암과 레골리스의 일반적인 값인 1.8을 적용하였고(Pelletier et al., 2013), 사면각은 고도를 중앙차분한 경사(S)로부터 cosθ = (1 + S²)^(−1/2)로 구하였다.

① 기반암 풍화

사면에 수직인 방향의 기반암 풍화율은 그 위를 덮는 토층의 두께에 따라 지수적으로 감소한다(Heimsath et al., 1997, 2001). Rasmussen & Tabor(2007)는 경사가 완만한 안정 사면에서 레골리스 두께가 EEMT에 따라 지수적으로 증가함을 보였으며, Pelletier & Rasmussen(2009)은 이를 바탕으로 토층이 없을 때의 풍화율도 EEMT에 따라 지수적으로 증가한다고 보았다(식 8).

$$P = P_0\,e^{-H\cos\theta/H_0}, \qquad P_0 = a\,e^{b_E\,\mathrm{EEMT}} \tag{8}$$

식 (8)에서 P0[m/kyr]는 토층이 없을 때의 풍화율, H0[m]는 Heimsath et al.(1997, 2001)의 자료에 근거한 풍화 특성깊이 0.5 m이며, a와 bE는 Pelletier & Rasmussen(2009)이 Riebe et al.(2004)의 화강암 유역 자료로 구한 0.037 m/kyr와 0.03 m² yr/MJ이다.

EEMT는 유효강수(강수량에서 증발산량을 뺀 값)가 토양에 전달하는 열에너지(EPPT)와 순일차생산으로 고정되는 에너지(EBIO)의 합이다(Pelletier et al., 2013). Rasmussen & Tabor(2007)는 유효강수가 0 °C에서 그 달의 평균기온까지 데워진다고 보고 유효강수가 양수인 달만 더하여 연간 EEMT를 구하였다. Pelletier et al.(2013)은 기온, 강수량, 수증기압 부족량의 회귀식으로 EEMT를 추정하였으나, 본 연구에서는 BIOME4가 계산한 격자별 NPP와 월 실제증발산량으로 EEMT를 직접 계산하였다(식 9).

$$\mathrm{EEMT} = E_{PPT} + E_{BIO} = \sum_{m=1}^{12} c_w\,\max(T_m,\,0)\,\max(P_m - \mathrm{AET}_m,\,0) + \frac{h_{BIO}}{f_C}\,\max(\mathrm{NPP},\,0) \tag{9}$$

식 (9)에서 EEMT의 단위는 MJ/m²/yr이며, Tm[°C]은 m월의 평균기온, Pm과 AETm[kg/m²]은 m월의 강수량과 실제증발산량, NPP[kgC/m²/yr]는 순일차생산량, cw는 물의 비열(4,186 J/kg/K), hBIO는 생체량의 에너지 함량(22 MJ/kg), fC는 생체량의 탄소 비율(0.5)이다. 평균기온이 0 °C 이하인 달의 EPPT는 0으로 두었다(Pelletier & Rasmussen, 2009).

② 사면 물질이동

토양포행과 생물교란 같은 붕적 과정에 의한 침식과 퇴적은 물질 이동량(q)의 발산으로 나타낸다(Ec = ∇·q). Culling(1960)은 이동량이 경사에 비례하는 확산식을 제시하였으며, Roering et al.(1999)은 이동량이 임계경사에 가까워질수록 급격히 커지는 비선형 경사의존모델을 제시하였다. Pelletier et al.(2013)은 여기에 이동량이 사면에 수직인 방향의 토심에 비례하는 항을 더하였다(식 10).

$$\mathbf{q} = -\frac{k_d\,H\cos\theta\,\nabla z}{1 - \left(|\nabla z|/S_c\right)^2} \tag{10}$$

$$k_d = c_E\,\mathrm{EEMT} + c_A\,\mathrm{AGB} \tag{11}$$

식 (10), (11)에서 q[m²/kyr]는 단위폭당 물질 이동량, kd[m/kyr]는 사면 물질이동 계수, Sc는 임계경사, AGB[kg/m²]는 지상부 생체량이다. Pelletier et al.(2013)은 kd를 토양포행과 생물교란 성분의 합으로 보고, 동결과 융해에 필요한 수분이 많을수록 활발한 토양포행은 EEMT에, 식물이 많을수록 활발한 생물교란은 AGB에 비례하도록 하였다. cE와 cA는 Pelletier et al.(2013)이 건조한 저지대와 습윤한 고지대의 kd 값에 맞추어 구한 0.033과 0.05이며, 임계경사는 미고결 물질의 일반적인 안식각(35°)에 해당하는 0.7이다(Pelletier et al., 2013).

Pelletier et al.(2013)은 항공 라이다로 추정한 AGB와 EEMT의 경험적 관계를 사용하였으나, 본 연구에서는 식생유형에 따른 생체량의 차이를 반영하기 위해 우점 PFT의 잎과 변재의 건조생체량 합으로 AGB를 구하였다(식 13). 잎 생체량은 우점 PFT의 LAI를 Reich et al.(1992)이 제시한 잎 수명(L[월])과 비엽면적(SLA[cm²/g])의 관계(식 12)로 환산하였으며, 변재 생체량은 LAI와 변재 탄소량의 비례 관계(Haxeltine & Prentice, 1996)에 BIOME4의 계수(LAI당 0.5 kgC/m²)를 적용하고 탄소 비율 0.5로 나누어 구하였다.

$$\log_{10}\mathrm{SLA} = 2.44 - 0.43\,\log_{10}L \tag{12}$$

$$\mathrm{AGB} = \mathrm{LAI}\left(s + \frac{L^{0.43}}{0.1\times10^{2.44}}\right) \tag{13}$$

식 (13)에서 0.1은 SLA[cm²/g]를 m²/kg으로 바꾸는 계수이고, L은 BIOME4의 PFT별 예상 잎 수명(PFT4 7개월, PFT5 30개월, PFT6과 PFT7 24개월, PFT8 8개월 등)이며, s는 변재 호흡이 있는 PFT에서 1, 없는 PFT(PFT8, 9, 12)에서 0이다(Kaplan, 1999, 2001).

③ 유수침식

유수침식은 사면에서 넓게 퍼져 흐르는 포상류와 곡저에 집중된 흐름에 의한 침식이다. Pelletier et al.(2013)은 이를 선형 유수력 모델로 나타내고, 기반암 하도가 아닌 사면과 사면 오목부, 저차 곡지의 레골리스 분리제어 침식에 적용하였다(식 14).

$$E_f = K\,\frac{A}{w}\,|\nabla z|, \qquad K = \frac{K_0}{\mathrm{EEMT}} \tag{14}$$

식 (14)에서 A[m²]는 기여면적, w[m]는 흐름의 유효 폭, K[1/kyr]는 침식계수이다. Langbein & Schumm(1958)은 연평균 유효강수량이 약 0.3 m를 넘으면 식생 피복이 토양을 붙잡아 강수가 많을수록 퇴적물 생산량이 줄어든다고 보고하였으며, Pelletier et al.(2013)은 이를 반영하여 레골리스의 침식계수를 EEMT에 반비례하도록 하였다. K0는 0.02 m²/MJ이며, 레골리스가 모두 침식되면 남은 침식능으로 레골리스 침식계수의 1/10로 기반암을 침식한다(Pelletier et al., 2013).

기여면적은 다방향 흐름 알고리즘(Freeman, 1991)으로 구하였으며, 각 격자의 흐름은 하류 방향 인접 격자에 경사의 1.1제곱에 비례하여 나누었다. 흐름 경로는 우선순위 채우기(Barnes et al., 2014)로 와지를 채운 지형에서 구하였고, 채운 지형은 흐름 계산에만 사용하였다. 흐름의 유효 폭은 포상류가 일어나는 사면에서 격자 크기와 같고, 흐름이 곡저에 집중되는 곳에서 w = gA^(1/2), g = 0.005이다(Leopold & Maddock, 1953; Pelletier et al., 2013). 사면과 곡저는 Pelletier(2010, 2013)의 방법에 따라, 30 m 격자의 기여면적과 지형을 쌍선형 보간한 15 m 격자에서 대응하는 네 격자 기여면적의 최댓값 사이의 비(f)가 1.2보다 작은 격자를 곡저로 구분하였다.

④ 융기

융기율(U)은 Lee et al.(2024)이 태백산맥의 장기 삭박률에 맞추어 제시한 0.08 m/kyr를 유출구를 제외한 모든 격자의 기반암에 같게 적용하였다.

⑤ 수치 계산

지형발달모델은 BIOME4가 계산한 EEMT와 AGB를 0.1 kyr 동안 일정하게 두고, 이 기간을 여러 계산 간격(Δt)으로 나누어 진행하였다. 각 계산 간격에서는 임계경사 조정, 기반암 풍화, 사면 물질이동, 유수침식, 융기, 임계경사 조정의 순서로 계산하였다. 임계경사를 넘는 사면은 Campforts et al.(2017)의 방법으로 임계경사까지 낮추었으며(식 15), 낮아진 만큼은 토층에서 먼저 빼고 토층이 모자라면 기반암에서 뺀 뒤 유역 밖으로 내보냈다.

$$z'_i = \min\left[\,z_i,\ \min_{j}\left(z_j + S_c\,d_{ij}\right)\right] \tag{15}$$

식 (15)에서 dij[m]는 격자 i와 j 사이의 수평 거리이다. 기반암 풍화량(PΔt/cosθ)은 계산 간격 시작 시점의 토심으로 구하고, 여기에 밀도비를 곱한 레골리스 생성량을 토심에 더하였다(Pelletier et al., 2013). 사면 물질이동량은 격자 경계에서 인접한 두 격자의 kd와 토심의 평균으로 계산하였으며(식 16; Pelletier et al., 2013), 한 계산 간격 동안 격자에서 빠져나가는 양이 토심을 넘으면 그 격자의 유출량을 비례적으로 줄였다.

$$q_{x,\,i+1/2} = -\,\bar{k}_d\,\bar{H}\,\frac{(z_{i+1} - z_i)/\Delta x}{1 - \left[(z_{i+1} - z_i)/(\Delta x\,S_c)\right]^2} \tag{16}$$

식 (16)에서 k̄d와 H̄는 인접한 두 격자의 평균, Δx는 격자 크기(30 m)이며, y 방향도 같은 방식으로 계산하였다. 계산 간격은 0.1 kyr에서 시작하여 0.01Δx²/(2kd) 이하가 될 때까지 절반으로 줄였고, 한 계산 간격의 최대 고도 변화가 0.025 m를 넘으면 그 계산을 버리고 간격을 절반으로 줄여 다시 계산하였다(Pelletier et al., 2013). 유출구 격자는 융기하지 않는 고정 침식기준면으로 두어 고도, 기반암 고도, 토심을 초기값으로 고정하였으며(Pelletier et al., 2013), 나머지 경계에서는 물질이 드나들지 않도록 하였다.

(4) 입력 자료와 모의 설정

기후 자료는 CHELSA-TraCE21k(Karger et al., 2023)에서 용늪 지점을 포함하는 격자의 100년 간격 월 최저기온, 월 최고기온, 월강수량을 사용하였으며, 월평균 기온은 월 최저기온과 최고기온의 평균으로 하였다. CHELSA-TraCE21k는 지형을 고려하여 상세화된 자료이므로 고도에 따른 기온 보정 없이 유역 내 모든 격자에 같은 값을 적용하였다. 절대최저기온은 Prentice et al.(1992)의 회귀식(식 17)으로 추정하였다.

$$T_{min} = 0.006\,T_c^2 + 1.316\,T_c - 21.9 \tag{17}$$

식 (17)에서 Tc[°C]는 가장 추운 달의 평균기온이다. 운량은 Beyer et al.(2020)의 0.5° 격자에서 1,000년 간격으로 제공되는 월별 운량을 0.1 kyr 간격으로 선형보간하였고, 100에서 운량[%]을 뺀 값을 일조율로 입력하였다. 대기 중 CO2 농도는 Bereiter et al.(2015)의 남극 빙하코어 종합 기록을 각 모델 시점으로 선형보간하였으며, 기압은 각 격자의 고도(z[m])에서 미국 표준대기(NOAA et al., 1976)의 식(식 18)으로 계산하였다.

$$p = 101325\,(1 - 2.25577\times10^{-5}\,z)^{5.25588} \tag{18}$$

지형은 FABDEM V1-2(Hawker et al., 2022)를 EPSG:5187로 투영한 뒤 쌍선형 보간으로 30 m 격자로 구성하였다. 유역은 우선순위 채우기(Barnes et al., 2014)로 와지를 채운 지형의 D8 흐름 방향으로 구하였으며, 유출구는 용늪에서 나가는 유로가 처음 지류와 합류하는 지점 바로 아래 격자(128.1265°E, 38.2180°N)로 하였다. 이에 따라 유출구로 흘러드는 656개 격자(59.0 ha, 고도 1,138-1,284 m)를 모델 유역으로 설정하였다(그림 ?). 초기 토심은 SoilGrids(Hengl et al., 2017)의 1 km 기반암 깊이 자료(Shangguan et al., 2017)에 따라 유역 전체에 1.94 m를 적용하였으며, 초기 기반암 고도는 지표 고도에서 초기 토심을 뺀 값으로 하였다.

모의는 21 ka BP부터 현재까지 0.1 kyr 간격으로 211개 시점에 대해 수행하였다. 동적 지형 모델은 각 시점에서 BIOME4로 식생을 계산하고, 그 EEMT와 AGB로 다음 0.1 kyr 동안의 지형발달을 계산한 뒤 변화한 고도와 토심을 다음 시점의 BIOME4에 입력하였다. 반면, 정적 지형 모델은 같은 기후 조건에서 고도와 토심을 초기값으로 고정하고 식생만 계산하였다. 두 모델의 결과를 비교함으로써 지형과 토심의 변화가 식생 복원에 미치는 영향을 확인하고자 하였다.

(5) 고식생 검증

모델 결과는 용늪의 두 고식생 기록과 비교하였다. Jang et al.(2011)의 코어(38°12′57.4″N, 128°7′30.2″E)와 Park et al.(2021)의 YN-C 코어(38°12′54.40″N, 128°7′25.1″E, 해발 1,189 m)는 약 155 m 떨어져 있으며, 모두 모델 유역 안에 위치한다. 반경 약 50 m의 분지에서 관련 화분 공급원 범위는 분지 가장자리에서 300-400 m이며, 이 범위 안에서 오는 화분은 전체의 30-45%이다(Sugita, 1994). 따라서 본 연구에서는 용늪(약 7,490 m²; Jang et al., 2011)의 화분 기록을 유역 단위 모델 결과와 비교하되, 화분 비율을 식생 면적 비율에 대응시키지 않고 식생유형과 PFT의 출현 여부를 비교하였다. 모델에서는 기반암 노출 격자를 제외한 식생 격자의 1% 이상(7개 격자 이상)을 차지하는 식생유형 또는 PFT를 출현으로 판정하였다.

첫째, Jang et al.(2011)과 비교하기 위해 BIOME4가 판정한 생물군계를 그대로 다섯 식생유형으로 묶었다(표 3). Jang et al.(2011)의 5,900-4,800 cal yr BP와 3,400-390 cal yr BP는 활엽수림, 4,800-3,400 cal yr BP와 390 cal yr BP 이후는 혼효림과 비교하였으며, 각 화분대 연대 구간에 속하는 0.1 kyr 간격의 모델 시점을 평가하였다. 이때 화분대 경계인 4.8 ka와 3.4 ka는 양쪽 화분대에서 모두 평가하여 총 62개 시점을 비교하였다. 또한, Jang et al.(2011)은 3,400-390 cal yr BP를 낙엽활엽수림으로 구분하였으나 약 1,300 cal yr BP까지 대암산 정상부와 그 주변에 침엽수-낙엽활엽수 혼효림이 발달하였다고 해석하였으므로, 이 기간의 전부 또는 일부를 혼효림으로 본 경우도 비교하였다. 연대모델이 5개의 AMS 연대 중 역전된 1개를 뺀 4개에 기반하므로(Jang et al., 2011), 화분대 경계 전후 0.1-0.3 kyr의 시점을 제외한 경우도 함께 비교하였다.

표 3. BIOME4 생물군계의 검증용 식생유형 재분류

| 식생유형 | BIOME4 생물군계 |
|---|---|
| 활엽수림 | 열대 상록림, 열대 반낙엽림, 열대 낙엽림 및 소림, 온대 낙엽활엽림 |
| 침엽수림 | 온대 침엽수림, 냉량 침엽수림, 상록 타이가 및 산지림, 낙엽 타이가 및 산지림 |
| 혼효림 | 난온대 혼효림, 냉량 혼효림, 한랭 혼효림 |
| 초본 및 개방식생 | 열대 사바나, 열대 건생관목림, 온대 건생관목림, 온대 경엽수 소림, 온대 활엽수 사바나, 개방 침엽수 소림, 아한대 소림지대, 열대 초지, 온대 초지, 툰드라, 식생이 있는 사막 |
| 무식생 | 나지, 빙하, 식생이 없는 사막, 기반암 노출 격자 |

둘째, Park et al.(2021)의 YN-C 코어 화분 자료로 PFT 단위의 검증을 수행하였다. 해당 자료는 16-88 cm 구간에서 1 cm 간격으로 분석한 72개 시료(50 cm 제외)이며, 16-90 cm 구간 전암 시료 11개의 AMS 연대를 rbacon(Blaauw & Christen, 2011)과 IntCal20(Reimer et al., 2020)으로 보정한 연대모델에 따라 3,181-515 cal yr BP에 해당한다(Park et al., 2021). 분석에는 Park et al.(2021) 부록의 분류군별 계수 자료를 사용하였다.

화분 분류군은 Ni et al.(2010)의 PFT 배정에 따라 BIOME4의 PFT 그룹으로 묶었다(표 4). 교목 PFT 중 아한대 냉량 낙엽 활엽교목은 아한대 낙엽수(PFT7), 온대와 난온대의 냉량 낙엽 활엽교목은 온대 낙엽활엽수(PFT4), 상록 침엽교목은 상록 침엽수(PFT5, 6), 난온대 상록 활엽교목은 온대 상록활엽수(PFT3)에 대응시켰으며, 초본 PFT 중 벼과는 온대 초본(PFT8), 마황속이 속한 내한성 소엽 관목은 건조지 목본(PFT10)에 대응시켰다. 여러 PFT에 배정된 분류군의 화분은 Ni et al.(2010)과 같이 해당 그룹 모두에 더하였다. 화분 합은 Park et al.(2021)의 목본과 초본의 합에서 습원과 그 주변에 사는 오리나무속(Jang et al., 2011)과 습원 초본인 산형과, 오이풀속(Jang et al., 2011; Park et al., 2021)을 뺀 값으로 하였고, 포자는 Ni et al.(2010)과 같이 포함하지 않았다.

표 4. 화분 분류군의 PFT 그룹(Ni et al., 2010)

| PFT 그룹 | 배정 분류군 | BIOME4 PFT | 모델 판정 |
|---|---|---|---|
| 온대 낙엽활엽수 | 참나무속(낙엽성), 서어나무속, 단풍나무속, 물푸레나무속, 느릅나무속, 피나무속, 개암나무속, 밤나무속, 가래나무속, 너도밤나무속, 팽나무속, 뽕나무속, 굴피나무속, 히코리속, 옻나무속, 인동속, 딱총나무속, 장미과, 화살나무속, 갈매나무과, 소귀나무속, 자작나무속, 버드나무속 | 4 | 우점 PFT |
| 아한대 낙엽수 | 자작나무속, 버드나무속 | 7 | 우점 PFT |
| 상록 침엽수 | 소나무속, 전나무속, 가문비나무속, 솔송나무속, 측백나무과 | 5, 6 | 생육 가능 PFT |
| 온대 상록활엽수 | 참나무속(상록성), 감탕나무속, 회양목속, 동백나무속, 화살나무속, 갈매나무과, 소귀나무속 | 3 | 우점 PFT |
| 초본 | 벼과 | 8 | 우점 PFT |
| 건조지 목본 | 마황속 | 10 | 우점 PFT |

각 모델 시점(t)의 그룹별 화분 비율은 [t − 0.05, t + 0.05) kyr에 속하는 시료의 계수를 합하여 구하였으며, 이에 따라 72개 시료는 28개 모델 시점(3.2-0.5 ka)에 한 번씩 배정된다. 화분 비율이 0.5% 이상인 그룹을 출현으로 보았는데, 이 값은 Prentice et al.(1996)이 생물군계 복원에 가장 잘 맞는 일괄 기준으로 선정한 값이며 Ni et al.(2010)도 같은 값을 사용하였다. 다만 이 기준을 넘는 화분 비율이 그 분류군의 실제 출현을 의미하지는 않는다(Prentice et al., 1996). 모델에서는 유역 식생 격자의 1% 이상에서 우점 PFT로 선택된 PFT를 출현으로 판정하였다. 상록 침엽수는 우점 여부 대신 생육 가능 여부(생물기후적 한계값을 만족하고 NPP가 0보다 큼)로 판정하였는데, 이는 BIOME4가 온대 낙엽활엽수(PFT4)가 우점하고 아한대 상록수(PFT6)가 생육 가능하면 냉량 혼효림으로 판정하기 때문이다(Kaplan, 1999). 정확도는 여섯 그룹과 28개 시점의 출현 여부 168건을 합산하여 구하였으며, 민감도, 특이도, TSS(민감도 + 특이도 − 1; Allouche et al., 2006)와 그룹별 결과를 함께 제시하였다.

셋째, 판정 기준과 비교 범위에 따라 결과가 달라지는지 확인하기 위해 민감도 분석을 수행하였다. 모델의 출현 기준은 1개 격자와 유역의 1-5%로, 화분의 출현 기준은 모든 그룹 0.5-10%로 바꾸어 비교하였다. 또한, 화분의 공급원 범위는 유역 경계가 아니라 시료 위치로부터의 거리에 따라 정해지므로(Janssen, 1966; Jacobson & Bradshaw, 1981; Sugita, 1994), 유역 전체 대신 각 코어로부터 반경 100-1,000 m 안의 격자만으로 출현을 판정한 경우와 코어로부터의 거리에 반비례(1/d, 1/d²)하는 가중치를 적용한 경우를 비교하였다. 이때 Jang et al.(2011)과의 비교에는 Jang 코어를, Park et al.(2021)과의 비교에는 YN-C 코어를 기준으로 하였다. 마지막으로, 유역의 크기에 따른 영향을 확인하기 위해 유출구를 하류로 옮겨 유역 면적이 처음 1 km²를 넘는 합류 지점(1,119개 격자, 100.7 ha, 고도 975-1,284 m)으로 설정한 경우를 같은 조건에서 모의하여 비교하였다.

코드(PB4Studio v6.6.3-CHELSA21K), 입력 자료, 실행 설정, 검증 스크립트는 GitHub 저장소(https://github.com/physical-geogrpahy-forever/yongneup_nb)에 공개하였다.

---

참고문헌(연구 방법)

Allouche, O., Tsoar, A. and Kadmon, R., 2006, Assessing the accuracy of species distribution models: prevalence, kappa and the true skill statistic (TSS), Journal of Applied Ecology, 43(6), 1223-1232.
Barnes, R., Lehman, C. and Mulla, D., 2014, Priority-flood: An optimal depression-filling and watershed-labeling algorithm for digital elevation models, Computers & Geosciences, 62, 117-127.
Bereiter, B., Eggleston, S., Schmitt, J., Nehrbass-Ahles, C., Stocker, T. F., Fischer, H., Kipfstuhl, S. and Chappellaz, J., 2015, Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present, Geophysical Research Letters, 42(2), 542-549.
Beyer, R. M., Krapp, M. and Manica, A., 2020, High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years, Scientific Data, 7, 236.
Blaauw, M. and Christen, J. A., 2011, Flexible paleoclimate age-depth models using an autoregressive gamma process, Bayesian Analysis, 6(3), 457-474.
Blöthe, J. H., Korup, O. and Schwanghart, W., 2015, Large landslides lie low: Excess topography in the Himalaya-Karakoram ranges, Geology, 43(6), 523-526.
Campforts, B., Schwanghart, W. and Govers, G., 2017, Accurate simulation of transient landscape evolution by eliminating numerical diffusion: the TTLEM 1.0 model, Earth Surface Dynamics, 5(1), 47-66.
Culling, W. E. H., 1960, Analytical theory of erosion, Journal of Geology, 68, 336-344.
FAO-UNESCO, 1974, Soil Map of the World, 1:5 000 000, Volume I, Legend, UNESCO, Paris.
Freeman, T. G., 1991, Calculating catchment area with divergent flow based on a regular grid, Computers & Geosciences, 17(3), 413-422.
Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C. and Neal, J., 2022, A 30 m global map of elevation with forests and buildings removed, Environmental Research Letters, 17(2), 024016.
Haxeltine, A. and Prentice, I. C., 1996, BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types, Global Biogeochemical Cycles, 10(4), 693-709.
Heimsath, A. M., Dietrich, W. E., Nishiizumi, K. and Finkel, R. C., 1997, The soil production function and landscape equilibrium, Nature, 388, 358-361.
Heimsath, A. M., Dietrich, W. E., Nishiizumi, K. and Finkel, R. C., 2001, Stochastic processes of soil production and transport: Erosion rates, topographic variation and cosmogenic nuclides in the Oregon Coast Range, Earth Surface Processes and Landforms, 26, 531-552.
Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S. and Kempen, B., 2017, SoilGrids250m: Global gridded soil information based on machine learning, PLoS ONE, 12(2), e0169748.
Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E. and Schulze, E.-D., 1996, A global analysis of root distributions for terrestrial biomes, Oecologia, 108, 389-411.
Jacobson, G. L. Jr. and Bradshaw, R. H. W., 1981, The selection of sites for paleovegetational studies, Quaternary Research, 16(1), 80-96.
Jang, B.-O., Kang, S. J. and Choi, K. R., 2011, Vegetation history around Yongneup moor at Mt. Daeamsan, Korea, Journal of Ecology and Field Biology, 34(3), 259-267.
Janssen, C. R., 1966, Recent pollen spectra from the deciduous and coniferous-deciduous forests of northeastern Minnesota: a study in pollen dispersal, Ecology, 47(5), 804-825.
Kaplan, J. O., 1999, BIOME4 v4.2b2 source code (biome4.f), https://pmip2.lsce.ipsl.fr/synth/biome4.shtml.
Kaplan, J. O., 2001, Geophysical Applications of Vegetation Modeling, Ph.D. dissertation, Lund University, Lund, doi:10.5281/zenodo.1492908.
Kaplan, J. O., Bigelow, N. H., Prentice, I. C., Harrison, S. P., Bartlein, P. J., Christensen, T. R., Cramer, W., Matveyeva, N. V., McGuire, A. D., Murray, D. F., Razzhivin, V. Y., Smith, B., Walker, D. A., Anderson, P. M., Andreev, A. A., Brubaker, L. B., Edwards, M. E. and Lozhkin, A. V., 2003, Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections, Journal of Geophysical Research, 108(D19), 8171.
Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H. and Zimmermann, N. E., 2023, CHELSA-TraCE21k - high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum, Climate of the Past, 19(2), 439-456.
Langbein, W. B. and Schumm, S. A., 1958, Yield of sediment in relation to mean annual precipitation, Transactions, American Geophysical Union, 39, 1076-1084.
Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E. and Yu, B. Y., 2024, Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea, Earth Surface Dynamics, 12(5), 1091-1120.
Leopold, L. B. and Maddock, T. Jr., 1953, The hydraulic geometry of stream channels and some physiographic implications, U.S. Geological Survey Professional Paper 252.
McKenzie, N. J., Gallant, J. C. and Gregory, L. J., 2003, Estimating water storage capacities in soil at catchment scales, Technical Report 03/3, Cooperative Research Centre for Catchment Hydrology, Canberra.
Ni, J., Yu, G., Harrison, S. P. and Prentice, I. C., 2010, Palaeovegetation in China during the late Quaternary: Biome reconstructions based on a global scheme of plant functional types, Palaeogeography, Palaeoclimatology, Palaeoecology, 289, 44-61.
NOAA, NASA and USAF, 1976, U.S. Standard Atmosphere, 1976, U.S. Government Printing Office, Washington, D.C.
Park, J., Jin, Q., Choi, J., Bahk, J. and Park, J., 2021, Late Holocene climate variability in central Korea indicated by vegetation, geochemistry, and fire records of the Yongneup moor, Palaeogeography, Palaeoclimatology, Palaeoecology, 584, 110705.
Pelletier, J. D. and Rasmussen, C., 2009, Quantifying the climatic and tectonic controls on hillslope steepness and erosion rate, Lithosphere, 1(2), 73-80.
Pelletier, J. D., 2010, Minimizing the grid-resolution dependence of flow-routing algorithms for geomorphic applications, Geomorphology, 122, 91-98.
Pelletier, J. D., 2013, Fundamental principles and techniques of landscape evolution modeling, in Shroder, J. and Baas, A. C. W.(eds.), Treatise on Geomorphology, Vol. 2, Quantitative Modeling of Geomorphology, Academic Press, San Diego, 29-43.
Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L. and Troch, P. A., 2013, Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona, Journal of Geophysical Research: Earth Surface, 118(2), 741-758.
Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E. and Rossiter, D., 2021, SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty, SOIL, 7(1), 217-240.
Prentice, I. C., Cramer, W., Harrison, S. P., Leemans, R., Monserud, R. A. and Solomon, A. M., 1992, A global biome model based on plant physiology and dominance, soil properties and climate, Journal of Biogeography, 19(2), 117-134.
Prentice, I. C., Guiot, J., Huntley, B., Jolly, D. and Cheddadi, R., 1996, Reconstructing biomes from palaeoecological data: A general method and its application to European pollen data at 0 and 6 ka, Climate Dynamics, 12(3), 185-194.
Rasmussen, C. and Tabor, N. J., 2007, Applying a quantitative pedogenic energy model across a range of environmental gradients, Soil Science Society of America Journal, 71(6), 1719-1729.
Reich, P. B., Walters, M. B. and Ellsworth, D. S., 1992, Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems, Ecological Monographs, 62(3), 365-392.
Reimer, P. J. et al., 2020, The IntCal20 Northern Hemisphere radiocarbon age calibration curve (0-55 cal kBP), Radiocarbon, 62(4), 725-757.
Riebe, C. S., Kirchner, J. W. and Finkel, R. C., 2004, Erosional and climatic effects on long-term chemical weathering rates in granitic landscapes spanning diverse climate regimes, Earth and Planetary Science Letters, 224(3-4), 547-562.
Roering, J. J., Kirchner, J. W. and Dietrich, W. E., 1999, Evidence for nonlinear, diffusive sediment transport on hillslopes and implications for landscape morphology, Water Resources Research, 35(3), 853-870.
Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H. and Dai, Y., 2017, Mapping the global depth to bedrock for land surface modeling, Journal of Advances in Modeling Earth Systems, 9(1), 65-88.
Sugita, S., 1994, Pollen representation of vegetation in Quaternary sediments: theory and method in patchy vegetation, Journal of Ecology, 82, 881-897.
Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L. and Heuvelink, G. B. M., 2023, Global mapping of volumetric water retention at 100, 330 and 15 000 cm suction using the WoSIS database, International Soil and Water Conservation Research, 11(2), 225-239.
