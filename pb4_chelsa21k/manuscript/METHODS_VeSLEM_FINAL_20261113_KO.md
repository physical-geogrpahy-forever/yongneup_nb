2) 연구 방법

(1) 모델 개요

VeSLEM은 BIOME4 v4.2b2(Kaplan et al., 2003)와 Pelletier et al.(2013)의 지형발달모델을 토양을 매개로 결합한 모델이다(그림 ?). 각 시점에서 BIOME4는 기후와 대기 중 CO2 농도, 토양수분보유능력을 입력받아 각 격자의 식생유형과 NPP, LAI, 실제증발산량을 계산하며, 지형발달모델은 이로부터 산정한 EEMT와 AGB를 이용하여 다음 시점까지 기반암 풍화와 사면 물질이동, 유수침식, 융기에 따른 지형과 토심의 변화를 계산한다. 변화한 토심은 다음 시점의 BIOME4에서 토양수분보유능력과 뿌리가 이용할 수 있는 수분을 결정하므로, 식생과 지형은 토양을 통해 서로 영향을 주고받게 된다.

(2) 식생모델

BIOME4는 Haxeltine & Prentice(1996)의 BIOME3를 발전시킨 탄소 및 수분 플럭스 결합 모델로, 월평균 기온, 강수량, 운량과 대기 중 CO2 농도, 토양 특성을 입력받아 평형 상태의 식생 분포와 구조, 생지화학적 특성을 예측한다(Kaplan, 2001; Kaplan et al., 2003). 각 PFT에는 몇 가지 생물기후적 한계값이 주어지며, 이를 만족하는 PFT에 대해서만 일 단위 토양수분수지와 월 단위 광합성, 호흡, 생물계절 계산을 통해 NPP를 최대화하는 LAI와 그때의 NPP를 구한다. 이후 NPP, LAI, 연평균 토양수분을 기준으로 우점 PFT와 부우점 PFT를 정하고, 이들의 조합과 환경 조건에 따라 생물군계를 판정한다(Kaplan et al., 2003). 본 연구에서는 BIOME4의 생물기후적 한계값과 생리 계수, 우점 PFT와 생물군계의 판정 규칙을 그대로 사용하였으며, 토심의 변화를 반영하기 위해 토양수분보유능력과 뿌리 분포의 계산을 다음과 같이 수정하였다.

① 토양수분보유능력

BIOME4는 토양을 상층(0-30 cm)과 그 아래의 하층으로 나누고, 토양 자료로부터 산정한 각 층의 수분보유능력(WHC)과 투수 지수를 입력받아 토양수분수지를 계산한다(Kaplan, 2001). 본 연구에서는 하층을 0.3-1.5 m로 두고, 각 층의 WHC를 토심(H)까지 적분하여 매 시점 다시 계산하였다.

$$WHC(H) = 1000\int_{0}^{\min(H,\,0.3)} \left[\theta_{-10}(\xi) - \theta_{-1500}(\xi)\right] d\xi + 1000\int_{0.3}^{\min(\max(H,\,0.3),\,1.5)} \left[\theta_{-10}(\xi) - \theta_{-1500}(\xi)\right] d\xi \tag{1}$$

식 (1)에서 WHC[mm]의 첫째 항과 둘째 항은 각각 상층과 하층의 수분보유능력이며, ξ[m]는 깊이, θ−10과 θ−1500[m³/m³]은 −10 kPa와 −1500 kPa에서의 체적수분함량이다. 두 체적수분함량의 차이는 식물이 이용할 수 있는 수분량에 해당하며(McKenzie et al., 2003), 깊이별 값은 SoilGrids의 수분보유 자료(Turek et al., 2023)에서 용늪 지점의 값을 사용하였다(표 2).

표 2. 연구 지역의 깊이별 식물 이용 가능 수분량(θ−10 − θ−1500)

| 깊이 (cm) | 0-5 | 5-15 | 15-30 | 30-60 | 60-100 | 100-200 |
|---|---:|---:|---:|---:|---:|---:|
| 식물 이용 가능 수분량 (mm/m) | 237 | 232 | 218 | 207 | 198 | 179 |

② 뿌리 분포와 근권 토양수분

BIOME4는 PFT별로 상층에 분포하는 뿌리의 비율(r30)을 정하고, 상층과 하층의 상대 토양수분(W1, W2)을 r30과 1 − r30으로 가중평균하여 근권 토양수분을 구한다(Kaplan, 2001). 그러나 토심이 1.5 m보다 얕아지면 하층의 일부 또는 전부가 존재하지 않으므로, 본 연구에서는 Jackson et al.(1996)의 누적 뿌리분포식(Y = 1 − β^d)을 이용하여 뿌리분포를 토심에서 절단하였다. r30으로부터 PFT별 β를 구한 뒤(식 2), 토심 안에 분포하는 상층과 하층의 뿌리 비율을 계산하고(식 3), 이를 가중치로 근권 토양수분(Wr)을 구하였다(식 4).

$$\beta = (1 - r_{30})^{1/30} \tag{2}$$

$$r_{top} = 1 - \beta^{\min(d,\,30)}, \qquad r_{bottom} = \beta^{30} - \beta^{\min(d,\,150)} \tag{3}$$

$$W_r = r_{top}\,W_1 + r_{bottom}\,W_2 \tag{4}$$

식 (2)-(4)에서 d[cm]는 토심이며, 토심이 30 cm 이하이면 rbottom은 0이다. 토심이 150 cm 이상이면 PFT4(온대 낙엽활엽수)의 상층과 하층 뿌리 비율은 각각 0.65와 0.345로 원래의 BIOME4(0.65, 0.35)와 거의 같으나, 토심이 얕아지면 토심 아래에 분포해야 할 뿌리의 비율만큼 두 값의 합이 1보다 작아진다. 이에 따라 상층 뿌리 비율이 낮아 깊게 뿌리내리는 PFT일수록 얕은 토양에서 이용할 수 있는 수분이 크게 감소한다. 식 (4)의 근권 토양수분은 증산 공급량과 잎의 전개 및 낙엽 시기, PFT의 순위와 생물군계 판정에 쓰이는 연평균 토양수분의 계산에 사용하였다.

③ 산불잠재일수

BIOME4의 산불잠재일수는 근권 토양수분이 PFT별로 정해진 포장용수량 대비 비율보다 낮은 날의 수를 NPP에 따라 보정한 값으로, 우점 PFT를 정하는 규칙에 사용된다(Kaplan, 2001). 그런데 식 (4)를 그대로 적용하면 토심이 얕은 격자에서는 두 뿌리 비율의 합이 1보다 작아 토양이 포화되더라도 근권 토양수분이 임계값을 넘지 못하므로, 연중 모든 날이 건조한 날로 계산된다. 따라서 산불잠재일수를 계산할 때에는 원래의 BIOME4와 같이 가중치의 합이 1이 되도록 Wr을 (rtop + rbottom)으로 나눈 값을 사용하였다. 한편, 토심이 10⁻⁶ m 이하인 격자는 기반암이 노출된 것으로 보아 BIOME4 계산에서 제외하고 무식생으로 처리하였다.

(3) 지형발달모델

Pelletier et al.(2013)은 토층이 덮인 산지 사면이 주로 기반암의 물리적 풍화에 의한 레골리스의 생성과 사면 물질이동에 의한 제거를 통해 발달하며, 레골리스의 두께는 이 둘의 장기적인 균형에 의해 결정된다고 보았다. 이를 지표 고도, 기반암 고도, 레골리스 두께에 대한 연속방정식으로 나타내면 다음과 같다.

$$z = b + H \tag{5}$$

$$\frac{\partial b}{\partial t} = U - \frac{P}{\cos\theta} \tag{6}$$

$$\frac{\partial H}{\partial t} = \frac{\rho_r}{\rho_s}\frac{P}{\cos\theta} - E_c - E_f \tag{7}$$

식 (5)-(7)에서 z[m]는 지표 고도, b[m]는 기반암 또는 풍화전선의 고도, H[m]는 레골리스 두께, t[kyr]는 시간, U[m/kyr]는 융기율, P[m/kyr]는 사면에 수직인 방향의 기반암 후퇴율, θ는 사면각, ρr/ρs는 기반암과 레골리스의 밀도비, Ec와 Ef[m/kyr]는 각각 사면 물질이동과 유수에 의한 침식률이다(Pelletier et al., 2013). Pelletier et al.(2013)은 연구 지역의 화강암질 토양에 새프롤라이트가 거의 없다는 점에서 레골리스 두께를 토양 두께와 같은 것으로 보았으며, 본 연구에서도 레골리스 두께를 토심으로 사용하였다. 밀도비는 Pelletier et al.(2013)과 같이 화강암질 기반암과 레골리스에 대한 일반적인 값인 1.8을 사용하였다.

① 기반암 풍화

우주기원 핵종 연구에 따르면 사면에 수직인 방향의 기반암 풍화율은 그 위를 덮는 토층의 두께에 따라 지수적으로 감소한다(Heimsath et al., 1997, 2001). 또한 Rasmussen & Tabor(2007)는 경사가 완만한 안정 사면에서 레골리스 두께가 EEMT에 따라 지수적으로 증가함을 보였으며, Pelletier & Rasmussen(2009)은 이로부터 토층이 없을 때의 풍화율도 EEMT에 따라 지수적으로 증가한다고 보았다.

$$P = P_0\,e^{-H\cos\theta/H_0}, \qquad P_0 = a\,e^{b_E\,\mathrm{EEMT}} \tag{8}$$

식 (8)에서 P0[m/kyr]는 토층이 없을 때의 풍화율, H0[m]는 풍화 특성깊이로 Heimsath et al.(1997, 2001)의 자료에 근거한 0.5 m를 사용하였다. a와 bE는 Pelletier & Rasmussen(2009)이 Riebe et al.(2004)의 화강암 유역 자료로 산정한 0.037 m/kyr와 0.03 m² yr/MJ를 사용하였다.

EEMT(Effective Energy and Mass Transfer)는 유효강수에 의해 토양에 전달되는 열에너지(EPPT)와 순일차생산에 의해 고정되는 에너지(EBIO)의 합이다. Rasmussen & Tabor(2007)는 유효강수가 0 °C에서 그 달의 평균기온까지 데워진다고 보고, 유효강수가 양수인 달의 값만 더하여 연간 EEMT를 구하였다. Pelletier et al.(2013)은 NPP와 증발산량 자료를 구하기 어려워 기온, 강수량, 수증기압 부족량에 대한 회귀식으로 EEMT를 추정하였으나, 본 연구에서는 BIOME4에서 계산된 각 격자의 NPP와 월별 실제증발산량을 이용하여 직접 계산하였다.

$$\mathrm{EEMT} = E_{PPT} + E_{BIO} = \sum_{m=1}^{12} c_w\,\max(T_m,\,0)\,\max(P_m - \mathrm{AET}_m,\,0) + \frac{h_{BIO}}{f_C}\,\max(\mathrm{NPP},\,0) \tag{9}$$

식 (9)에서 Tm[°C]은 m월의 평균기온, Pm과 AETm[kg/m²]은 m월의 강수량과 실제증발산량, NPP[kgC/m²/yr]는 순일차생산량이며, cw는 물의 비열(4,186 J/kg/K), hBIO는 생체량의 에너지 함량(22 MJ/kg), fC는 생체량의 탄소 비율(0.5)이다. 영하에서 내린 강수는 풍화에 기여하지 않으므로(Pelletier & Rasmussen, 2009), 평균기온이 0 °C 이하인 달의 EPPT는 0으로 하였다. 식 (9)의 AETm은 BIOME4가 최종 선택한 PFT(초본과 목본이 함께 나타나는 PFT 14인 경우 목본 PFT)의 최적 LAI에서 계산된 일별 실제증발산량을 달별로 합한 값이다. BIOME4 v4.2b2는 토양 증발을 0으로 두므로 AETm은 식생 증산이며, 잎이 없는 날에는 평형증발량의 25%, 일평균기온이 −10 °C 이하인 날에는 0으로 계산된다. BIOME4를 거치지 않는 노출 기반암 격자는 AETm과 NPP를 0으로 두었다.

② 사면 물질이동

토층이 덮인 사면에서는 토양포행, 생물교란과 같은 붕적 과정(colluvial processes)에 의해 사면에서의 점진적인 물질이동이 일어나며, 이에 의한 침식 및 퇴적량은 질량보존에 따라 물질 이동량(q)의 발산으로 나타낸다(Ec = ∇·q). Culling(1960)은 이동량이 경사에 비례하는 확산식을 제시하였으나, 경사가 급해지면 이 선형 관계가 성립하지 않으므로 Roering et al.(1999)은 이동량이 임계경사에 가까워질수록 무한히 커지는 비선형 경사의존모델을 제시하였다. Pelletier et al.(2013)은 여기에 토심에 따른 이동량의 차이를 반영하여, 이동량이 사면에 수직인 방향의 토심에 비례하는 식을 사용하였다.

$$\mathbf{q} = -\frac{k_d\,H\cos\theta\,\nabla z}{1 - \left(|\nabla z|/S_c\right)^2} \tag{10}$$

$$k_d = c_E\,\mathrm{EEMT} + c_A\,\mathrm{AGB} \tag{11}$$

식 (10), (11)에서 q[m²/kyr]는 단위폭당 물질 이동량, kd[m/kyr]는 사면 물질이동 계수, Sc는 임계경사, AGB[kg/m²]는 지상부 생체량이다. Pelletier et al.(2013)은 습윤한 기후일수록, 또 식생이 많을수록 사면 물질이동 계수가 커진다는 선행연구를 바탕으로 이를 토양포행에 의한 성분과 생물교란에 의한 성분의 합으로 나타내었다. 물이 제한된 환경에서 토양포행은 동결과 융해에 필요한 수분이 많을수록 활발하므로 EEMT에 비례하도록 하였고, 생물교란은 이를 일으키는 식물이 많을수록 활발하므로 AGB에 비례하도록 하였다. cE와 cA는 Pelletier et al.(2013)이 건조한 저지대와 습윤한 고지대의 kd 값을 맞추어 산정한 0.033과 0.05를 사용하였다.

Pelletier et al.(2013)은 항공 라이다로 추정한 AGB와 EEMT의 경험적 관계를 이용하였으나, BIOME4는 지상부 생체량을 계산하지 않으므로 본 연구에서는 잎과 변재의 건조생체량의 합으로 AGB를 산정하였다. 잎 생체량은 BIOME4의 LAI를 Reich et al.(1992)의 잎 수명(L[월])과 비엽면적(SLA[cm²/g])의 관계(식 12)로 환산하였으며, 변재 생체량은 Haxeltine & Prentice(1996)의 LAI와 변재의 관계에 BIOME4의 변재 탄소량(LAI당 0.5 kgC/m²)을 적용하여 산정하였다.

$$\log_{10}\mathrm{SLA} = 2.44 - 0.43\,\log_{10}L \tag{12}$$

임계경사는 Pelletier et al.(2013)과 같이 미고결 물질의 일반적인 안식각(35°)에 해당하는 0.7을 사용하였다.

③ 유수침식

유수침식은 사면에서 넓게 퍼져 흐르는 포상류와 곡저에 집중된 흐름에 의한 침식이다(Pelletier et al., 2013). Pelletier et al.(2013)은 이를 선형 유수력 모델로 나타내었는데, 이 식을 기반암 하도의 침식이 아니라 사면과 사면 오목부, 저차 곡지에 쌓인 레골리스의 분리제어 침식에 적용하였다.

$$E_f = K\,\frac{A}{w}\,|\nabla z|, \qquad K = \frac{K_0}{\mathrm{EEMT}} \tag{13}$$

식 (13)에서 A[m²]는 기여면적, w[m]는 흐름의 유효 폭, K[1/kyr]는 침식계수이다. Langbein & Schumm(1958)은 연평균 유효강수량이 약 0.3 m를 넘는 지역에서는 강수가 많아질수록 식생 피복이 토양을 붙잡아 퇴적물 생산량이 감소한다고 보고하였으며, Pelletier et al.(2013)은 이를 반영하여 레골리스의 침식계수가 EEMT에 반비례하도록 하였다. K0는 Pelletier et al.(2013)과 같이 0.02 m²/MJ를 사용하였으며, 토층이 없는 곳에서는 기반암이 침식되도록 하되 기반암의 침식계수는 레골리스의 1/10로 하였다.

흐름의 유효 폭은 포상류가 일어나는 사면에서는 격자 크기와 같고, 흐름이 곡저에 집중되는 곳에서는 기여면적의 거듭제곱 함수(w = gA^(1/2), g = 0.005)로 나타낸다(Leopold & Maddock, 1953; Pelletier et al., 2013). 사면과 곡저는 Pelletier(2010)의 방법에 따라 다방향 흐름 알고리즘으로 원래 격자와 절반 크기 격자에서 각각 계산한 기여면적의 비(f)를 이용하여 구분하였으며, 이 비가 1.2보다 작아 격자 해상도에 대한 의존성이 작은 격자를 곡저로 보았다(Pelletier, 2013).

④ 융기

융기율(U)은 Lee et al.(2024)이 태백산맥의 장기 삭박률을 바탕으로 사용한 0.08 m/kyr를 유역 전체에 동일하게 적용하였다.

⑤ 수치 계산

지형발달모델은 각 계산 간격에서 기반암 풍화와 사면 물질이동, 유수침식, 융기를 차례로 계산하였다. 사면 물질이동은 Pelletier et al.(2013)과 같이 인접한 두 격자의 토심 평균을 이용하여 격자 경계에서의 이동량을 계산하였으며, 한 계산 간격 동안 격자에서 빠져나가는 양이 토심을 넘으면 그 격자의 유출량을 비례적으로 줄였다. 유수침식의 경사는 D8 방향의 하류 격자와의 경사를 사용하였으며, 한 계산 간격 동안의 레골리스 침식량은 남아 있는 토심을 넘지 않도록 하였다. 계산 중에 임계경사를 넘는 사면이 생기면 해당 사면을 임계경사까지 낮추었다. 계산 간격은 Pelletier et al.(2013)과 같이 한 간격 동안의 침식 또는 퇴적량이 일정 값을 넘지 않도록 조절하였으며, 고도 변화가 0.025 m를 넘으면 간격을 절반으로 줄여 다시 계산하였다. 유역 출구 격자는 고도와 토심을 고정하였고, 나머지 경계는 물질의 출입이 없도록 설정하였다.

(4) 입력 자료와 모의 설정

기후 자료는 CHELSA-TraCE21k(Karger et al., 2023)의 월평균 기온과 월강수량을 사용하였으며, 월평균 기온은 월 최저기온과 최고기온의 평균으로 산정하였다. CHELSA-TraCE21k는 지형의 영향을 고려하여 상세화된 자료이므로 유역 내 모든 격자에 용늪 지점의 값을 동일하게 적용하였다. CHELSA-TraCE21k에서 제공하지 않는 운량은 1,000년 간격으로 제공되는 Beyer et al.(2020)의 월별 운량을 0.1 kyr 간격으로 선형보간하여 사용하였으며, 대기 중 CO2 농도는 Bereiter et al.(2015)의 남극 빙하코어 기록을 사용하였다. 지형은 FABDEM V1-2(Hawker et al., 2022)를 EPSG:5187 좌표계로 투영하여 30 m 격자로 구성하였다. 유역은 와지를 채운 지형에서 D8 흐름 방향으로 구하였으며, 출구는 용늪에서 흘러나가는 유로가 처음 지류와 합류하는 지점의 바로 아래로 하였다(656개 격자, 59.0 ha). 초기 토심은 SoilGrids(Hengl et al., 2017)의 1 km 기반암까지의 깊이 자료를 이용하였으며, 이 자료는 Shangguan et al.(2017)의 방법으로 추정된 것이다.

모의는 21 ka BP부터 현재까지 0.1 kyr 간격으로 211개 시점에 대해 수행하였다. 동적 지형 모델은 각 시점에서 BIOME4로 식생을 계산한 뒤 이로부터 산정한 EEMT와 AGB를 이용하여 다음 0.1 kyr 동안의 지형발달을 계산하고, 변화한 고도와 토심을 다음 시점의 BIOME4에 입력하였다. 정적 지형 모델은 동일한 기후 조건에서 고도와 토심을 초기값으로 고정한 채 식생만 계산하였다. 두 모델의 결과를 고식생 기록과 비교하여, 토양과 지형을 시간에 따라 변화하는 요소로 고려하였을 때 고식생 복원 결과가 어떻게 달라지는지 평가하였다.

(5) 고식생 검증

모델 결과는 용늪의 두 고식생 기록과 비교하였다. 먼저 Jang et al.(2011)과 비교하기 위해 BIOME4의 생물군계를 활엽수림, 침엽수림, 혼효림, 초본 및 개방식생, 무식생의 다섯 식생유형으로 재분류하였다(표 3). 혼효림에 해당하는 생물군계는 활엽수 PFT(PFT2-4)와 침엽수 PFT(PFT5-7) 중 NPP가 가장 큰 값을 서로 비교하여, 한쪽이 51% 이상이면 해당 식생유형으로 분류하였다.

표 3. BIOME4 생물군계의 검증용 식생유형 재분류

| 식생유형 | BIOME4 생물군계 |
|---|---|
| 활엽수림 | 열대 상록림, 열대 반낙엽림, 열대 낙엽림 및 소림, 온대 낙엽활엽림 |
| 침엽수림 | 온대 침엽수림, 냉량 침엽수림, 상록 타이가 및 산지림, 낙엽 타이가 및 산지림 |
| 혼효림 | 난온대 혼효림, 냉량 혼효림, 한랭 혼효림 |
| 초본 및 개방식생 | 열대 사바나, 열대 건생관목림, 온대 건생관목림, 온대 경엽수 소림, 온대 활엽수 사바나, 개방 침엽수 소림, 아한대 소림지대, 열대 초지, 온대 초지, 툰드라, 식생이 있는 사막 |
| 무식생 | 나지, 빙하, 기반암 노출 격자 |

Jang et al.(2011)의 5,900-4,800 cal yr BP와 3,400-390 cal yr BP는 활엽수림, 4,800-3,400 cal yr BP와 390 cal yr BP 이후는 혼효림과 비교하였다. 각 시기에 속하는 0.1 kyr 간격의 모델 결과 62개 시점에 대해, 유역 내 식생 격자 중 관측된 식생유형이 1% 이상 나타나면 일치하는 것으로 판정하였다. 또한 판정 기준을 1개 격자에서 20개 격자까지 변화시켜 기준에 따른 결과의 차이를 확인하였다.

다음으로 Park et al.(2021)의 YN-C 코어 화분 자료(72개 시료, 약 3,181-515 cal yr BP)를 이용하여 PFT 단위로 모델 결과를 검증하였다. 화분 분류군은 Prentice et al.(1996)과 Takahara et al.(2000)을 참고하여 PFT 그룹으로 묶었으며(표 4), 용늪의 습원 식생을 반영하는 오리나무속, 산형과, 터리풀속, 오이풀속과 수생식물, 사초과, 포자는 육상 화분 합에서 제외하였다. 소나무속은 아속을 구분할 수 없어 육상 화분 합에는 포함하였으나 PFT 그룹에는 배정하지 않았다.

표 4. 화분 분류군의 PFT 그룹

| PFT 그룹 | 대표 분류군 | BIOME4 PFT | 화분 비율 기준 | 모델 판정 |
|---|---|---|---:|---|
| 온대 낙엽활엽수 | 참나무속(낙엽성), 서어나무속, 단풍나무속 등 | 4 | 2% | 우점 PFT |
| 아한대 낙엽수 | 자작나무속, 버드나무속 | 7 | 2% | 우점 PFT |
| 상록 침엽수 | 전나무속, 가문비나무속, 솔송나무속, 측백나무과 | 5, 6 | 1% | 생육 가능 PFT |
| 온대 상록활엽수 | 참나무속(상록성), 감탕나무속 등 | 3 | 5% | 우점 PFT |
| 초본 | 벼과 | 8 | 2% | 우점 PFT |
| 건조지 목본 | 마황속 | 10 | 5% | 우점 PFT |

각 모델 시점에서 ±0.05 kyr 이내의 시료를 합산하여 그룹별 화분 비율을 구하고, 이 비율이 그룹별 기준값 이상이면 해당 PFT가 출현한 것으로 보았다. 모델에서는 유역 내 식생 격자 중 하나 이상에서 해당 PFT가 우점 PFT로 선택되면 출현한 것으로 판정하였다. 다만 BIOME4는 온대 낙엽활엽수(PFT4)가 우점 PFT이고 아한대 상록수(PFT6)가 생육 가능하면 냉량 혼효림으로 판정하므로, 상록 침엽수는 우점 여부 대신 생육 가능 여부(생물기후적 한계값을 만족하고 NPP가 0보다 큰 경우)로 판정하였다. 검증 결과는 그룹별로 정확도, 민감도, 특이도, TSS를 계산하여 평가하였으며, 판정 방식과 화분 비율 기준을 바꾸어 민감도 분석을 수행하였다. 건조지 목본은 대응하는 화분 분류군이 풍매화인 마황속뿐이고, 얕은 암반에 자라는 관목은 대부분 충매화여서 화분으로 출현을 확인하기 어려우므로, 이 그룹을 제외한 TSS도 함께 제시하였다.

---

이 절에서 새로 인용한 문헌(PPT 참고문헌에 없는 것)

Culling, W. E. H., 1960, Analytical theory of erosion, Journal of Geology, 68, 336-344.
Haxeltine, A. and Prentice, I. C., 1996, BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types, Global Biogeochemical Cycles, 10(4), 693-709.
Heimsath, A. M., Dietrich, W. E., Nishiizumi, K. and Finkel, R. C., 1997, The soil production function and landscape equilibrium, Nature, 388, 358-361.
Heimsath, A. M., Dietrich, W. E., Nishiizumi, K. and Finkel, R. C., 2001, Stochastic processes of soil production and transport: Erosion rates, topographic variation and cosmogenic nuclides in the Oregon Coast Range, Earth Surface Processes and Landforms, 26, 531-552.
Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C. and Neal, J., 2022, A 30 m global map of elevation with forests and buildings removed, Environmental Research Letters, 17(2), 024016.
Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S. and Kempen, B., 2017, SoilGrids250m: Global gridded soil information based on machine learning, PLoS ONE, 12(2), e0169748.
Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E. and Schulze, E.-D., 1996, A global analysis of root distributions for terrestrial biomes, Oecologia, 108, 389-411.
Kaplan, J. O., 2001, Geophysical Applications of Vegetation Modeling, Ph.D. dissertation, Lund University, Lund.
Langbein, W. B. and Schumm, S. A., 1958, Yield of sediment in relation to mean annual precipitation, Transactions, American Geophysical Union, 39, 1076-1084.
Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E. and Yu, B. Y., 2024, Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea, Earth Surface Dynamics, 12(5), 1091-1120.
Leopold, L. B. and Maddock, T. Jr., 1953, The hydraulic geometry of stream channels and some physiographic implications, U.S. Geological Survey Professional Paper 252.
Pelletier, J. D., 2010, Minimizing the grid-resolution dependence of flow-routing algorithms for geomorphic applications, Geomorphology, 122, 91-98.
Pelletier, J. D., 2013, Fundamental principles and techniques of landscape evolution modeling, in Shroder, J. and Baas, A. C. W.(eds.), Treatise on Geomorphology, Vol. 2, Quantitative Modeling of Geomorphology, Academic Press, San Diego, 29-43.
Pelletier, J. D. and Rasmussen, C., 2009, Quantifying the climatic and tectonic controls on hillslope steepness and erosion rate, Lithosphere, 1(2), 73-80.
Prentice, I. C., Guiot, J., Huntley, B., Jolly, D. and Cheddadi, R., 1996, Reconstructing biomes from palaeoecological data: A general method and its application to European pollen data at 0 and 6 ka, Climate Dynamics, 12(3), 185-194.
Rasmussen, C. and Tabor, N. J., 2007, Applying a quantitative pedogenic energy model across a range of environmental gradients, Soil Science Society of America Journal, 71(6), 1719-1729.
Reich, P. B., Walters, M. B. and Ellsworth, D. S., 1992, Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems, Ecological Monographs, 62(3), 365-392.
Riebe, C. S., Kirchner, J. W. and Finkel, R. C., 2004, Erosional and climatic effects on long-term chemical weathering rates in granitic landscapes spanning diverse climate regimes, Earth and Planetary Science Letters, 224(3-4), 547-562.
Roering, J. J., Kirchner, J. W. and Dietrich, W. E., 1999, Evidence for nonlinear, diffusive sediment transport on hillslopes and implications for landscape morphology, Water Resources Research, 35(3), 853-870.
Takahara, H., Sugita, S., Harrison, S. P., Miyoshi, N., Morita, Y. and Uchiyama, T., 2000, Pollen-based reconstructions of Japanese biomes at 0, 6000 and 18,000 14C yr BP, Journal of Biogeography, 27(3), 665-683.
Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L. and Heuvelink, G. B. M., 2023, Global mapping of volumetric water retention at 100, 330 and 15000 cm suction using the WoSIS database, International Soil and Water Conservation Research, 11(2), 225-239.
