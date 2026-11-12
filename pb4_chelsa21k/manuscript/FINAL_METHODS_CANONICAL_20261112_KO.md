# PB4Studio U008 최종 방법론 초안
## 용늪 21–0 ka 식생–토양–지형 결합모델 및 근권 습윤도 민감도 실험

### 1. 모델 개요와 분석 설계

본 연구에서는 용늪 소유역의 후기 최종빙기 이후 식생–토양–지형 상호작용을 재현하기 위해 PB4Studio v6.6.3의 CHELSA21K 전용판을 사용하였다. 최종 생산모델의 과학 설정은 `6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`이며, 현재 배포본 SHA-256은 `93790ba804a9cbce01291015af2750974d85b9688f0894de8d51d46cfb5a4b7b`이다. PFT 보조 검증에는 이 최종 U008 위에 검증 코드만 추가한 `PB4Studio_v6.6.3_CHELSA21K_pftval.zip`(SHA-256 `7b0b29bc658420feb0b09e246a2141e44d9fee4134c445de7e9ac095b8039256`)을 사용하였다. PFT 검증 코드는 BIOME4, 지형발달식, 기후입력, 토양수문식 및 생산 파라미터를 변경하지 않고 이미 계산된 셀별 PFT 출력과 화분자료를 비교하도록 구성하였다.

기준 생산모델은 이하에서 **U008-A**로 표기한다. A는 최종 U008의 McKenzie–Jackson 토심 결합을 그대로 사용하는 기준형이다. 이후 실시한 B–E 실험은 근권 습윤도와 산불 계산의 구조적 민감도를 검토하기 위한 별도 실험이며, 현재 생산모델의 파라미터 보정이나 대체를 의미하지 않는다.

두 가지 지형 시나리오를 동일한 기후강제력으로 비교하였다. 정적모델(static)은 21–0 ka 동안 매 0.1 kyr 시점마다 기후와 BIOME4 식생을 다시 계산하되 초기 고도와 토심을 고정하였다. 동적모델(dynamic)은 각 시점에서 BIOME4를 계산한 뒤 EEMT와 AGB*를 산출하고, 이를 Pelletier 계열 지형발달모듈에 전달하여 다음 시점까지 고도·기반암·토심을 갱신하였다. 따라서 두 시나리오의 차이는 기후변화 자체가 아니라 지형–토심 피드백의 허용 여부이다. BIOME4는 각 0.1 kyr 시점마다 평형상태를 독립적으로 다시 계산하며, 전 시점의 PFT를 다음 시점에 직접 계승하는 천이 상태기억은 사용하지 않았다.

### 2. 공간격자와 초기조건

계산영역은 EPSG:5187 좌표계의 20 m 격자로 구성하였다. 내장 exact grid는 20행 × 23열이며, 유역 내 활성 셀은 298개이다. 모델 해상도는 20 m이고 초기 평균고도는 1163.0775 m, 초기 평균토심은 1.94039 m이다. 초기 토심 범위는 약 1.9400–1.9575 m이다. 유역에는 하나의 `open_free` 출구를 두었으며 해당 격자 위치는 row 2, col 16이다. 나머지 경계는 폐쇄경계로 처리하였다. 지형모듈에서는 개방 출구 셀의 z, 기반암고도 b, 토심 h를 각 지형 서브스텝의 진입값으로 유지하여 고정 기저면(Dirichlet boundary)으로 사용하였다. 유역 내부의 함몰지는 흐름경로 계산을 위해 채움 처리하되, 실제 지형상태와 라우팅 표면을 구분하였다.

### 3. 시간축과 기후강제력

모의기간은 21.0 ka BP부터 0.0 ka BP까지이고 결합 및 출력간격은 0.1 kyr(100년)이다. 따라서 정적·동적 각각 211개 시점이 계산된다. 기후자료는 내장 `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`를 사용하였다.

월평균 기온은 CHELSA-TraCE21k의 월별 tasmin과 tasmax를 사용하여 `(tasmin + tasmax)/2 - 273.15`로 계산하였다. 월강수량은 CHELSA 원자료의 `pr_raw`를 그대로 사용하였다. CHELSA 자료는 이미 지형 하향조정된 자료이므로 별도의 고도감률 보정은 적용하지 않았고, `lapse_rate_C_per_m = 0`으로 유지하였다. BIOME4가 요구하는 광조건은 CHELSA-TraCE21k Centennial 자료에 직접 포함되어 있지 않으므로, Beyer 계열 보조자료의 0–21 ka 월별 cloud percentage만 선형보간하여 사용하였다. Beyer 자료는 온도와 강수에는 사용하지 않았다.

BIOME4의 absolute minimum temperature는 원본식 `alttmin = 0.006·TCM² + 1.316·TCM - 21.9`로 계산하였다. 대기 CO₂는 PB4Studio에 내장된 Antarctica/Bereiter 2015 계열 CO₂ 기록을 시간에 따라 적용하였다. 각 셀의 대기압은 해당 시점의 고도에서 표준대기 근사식으로 계산하므로, 동적모델에서는 지형변화에 따른 고도 변화가 BIOME4 대기압 입력에도 반영된다.

### 4. BIOME4 식생모듈

식생계산에는 BIOME4 v4.2b2의 원본 Fortran computational core를 사용하였다. BIOME4는 월별 기온·강수·광조건, 절대최저기온, 대기 CO₂, 토양수리특성을 입력받아 일별 토양수분수지와 월별 광합성·호흡·생물계절 계산을 수행하고, 각 PFT에서 NPP를 최대화하는 LAI를 찾은 뒤 PFT 경쟁규칙을 이용하여 최종 PFT와 biome을 결정한다. 본 모델은 BIOME4 v4.2b2의 원래 기후허용범위와 경쟁규칙을 유지하였고, 프로젝트별 기후 niche 완화는 적용하지 않았다. 원본 코드에서 PFT1은 비활성화되어 있고 PFT2–13이 원래 경쟁규칙에 참여한다.

특히 최종 U008에서 PFT5의 기후허용범위는 원본 BIOME4 표를 그대로 사용한다. PFT5의 coldest-month temperature 하한은 −2°C이고 GDD5 하한은 900 degree-days이다. 과거 중간 실험에서 언급된 −19°C는 PFT5의 최종 기후제약이 아니며 최종 생산모델에는 적용되지 않는다.

BIOME4의 `present(pft)`는 기본적으로 `optnpp(pft) > 0`인지를 나타낸다(PFT12의 원본 예외규칙 제외). 최종 biome은 단순히 NPP가 가장 큰 하나의 PFT만으로 결정되는 것이 아니라, woody PFT와 grass PFT의 상대적 경쟁, LAI, 수분상태, 산불일수와 원본 BIOME4의 biome 판정규칙을 함께 사용한다. 따라서 `optpft`와 최종 biome은 동일한 정보가 아니며, 예를 들어 `optpft=4`이면서 PFT6이 `present`이면 원본 BIOME4 규칙에서 cool mixed forest가 선택될 수 있다.

### 5. 토심–토양수분 결합

#### 5.1 가용수분용량

토심은 각 시점의 실제 지형상태 h를 BIOME4에 전달하였다. 노출기반암으로 판단되는 `h ≤ 1×10⁻⁶ m` 셀은 BIOME4 활성계산에서 제외하였다. U008의 `mckenzie2003` 변형에서는 용늪 SoilGrids 지점(128.1236°E, 38.2153°N)의 −10 kPa와 −1500 kPa 체적함수량 차이를 이용하여 가용수분용량(AWC)을 깊이별로 적분하였다. 사용한 AWC는 0–0.05 m 237 mm m⁻¹, 0.05–0.15 m 232 mm m⁻¹, 0.15–0.30 m 218 mm m⁻¹, 0.30–0.60 m 207 mm m⁻¹, 0.60–1.00 m 198 mm m⁻¹, 1.00–2.00 m 179 mm m⁻¹이다.

BIOME4의 원래 두 수리층 구조는 유지하였다. 상층은 0–0.30 m, 하층은 0.30–1.50 m이고, 실제 토심보다 깊은 부분의 저장용량은 존재하지 않는 것으로 처리하였다. 따라서

`WHC_top = ∫[0,min(h,0.30)] AWC(z) dz`

`WHC_bottom = ∫[0.30,min(h,1.50)] AWC(z) dz`

로 계산하였다. 1.50 m는 McKenzie 계수에서 새로 도입한 값이 아니라 BIOME4의 기존 수리 프로파일 상한이다. 수리전도도는 별도로 재보정하지 않고 내장 토성등급의 BIOME4 값을 사용하였다. 용늪 제공 토성래스터의 유효 셀은 모두 texture class 2임을 전제로 하며 다른 토성등급이 발견될 경우 계산을 중지하도록 하였다.

#### 5.2 유효 근권

BIOME4의 각 PFT에 주어진 상부 30 cm 뿌리비율 `r30 = pftpar(pft,6)`을 Jackson et al. (1996)의 누적 뿌리분포와 연결하였다. 지수형 근분포의 깊이척도는 별도 보정 없이

`Xi = -0.30 / ln(1 - r30)`

로 계산하였다. 계산에 사용하는 유효 뿌리깊이는

`rd = min(max(h,0),1.5)`

로 제한하였다. 상·하층의 유효 뿌리가중치는

`rtop_eff = 1 - exp[-min(rd,0.30)/Xi]`

`rbot_eff = exp(-0.30/Xi) - exp(-rd/Xi)`  (rd > 0.30 m)

이며 rd ≤ 0.30 m이면 `rbot_eff = 0`이다. 이 가중치는 BIOME4의 일별 수분수지에서 근권수분

`wr = rtop_eff·w(1) + rbot_eff·w(2)`

을 계산하는 데 사용된다. 또한 상·하층의 실제 수분흡수분배도 동일한 유효 근분포를 사용한다. 토심에 NPP, LAI 또는 FVC를 직접 곱하는 경험적 토심계수는 적용하지 않았다. 토심은 WHC와 접근 가능한 뿌리공간을 통해서만 BIOME4 생리와 경쟁에 영향을 준다.

### 6. 산불과 생물계절

최종 생산모델 A는 BIOME4 v4.2b2의 native fire module을 사용한다. 외부 화재연대를 모델에 직접 입력하거나, 산불 이후 특정 PFT를 일정 기간 강제로 유지하는 상태기억은 사용하지 않는다. 각 PFT의 일별 토양수분이 원본 fire threshold보다 낮을 때 잠재 산불일수가 증가하고, threshold와 threshold+0.05 사이에서는 원본 연속함수를 사용한다. PFT4, PFT6, PFT7의 threshold는 0.33, PFT8은 0.40이다. 연간 NPP가 1000 gC m⁻² yr⁻¹ 미만이면 잠재 산불일수에 `NPP/1000`을 곱하여 연료부족을 반영하는 원본 보정도 그대로 사용한다.

생산모델 A에서 fire 서브루틴으로 전달되는 일별 습윤도는 위 근권수분 `wr`이다. raingreen 생물계절의 on/off 수분판정, 월평균 근권수분, transpiration supply 역시 원본 계산경로의 `wr`을 사용한다. U009에서 시험했던 “화재 이후 PFT8 100년 유지” 규칙은 최종 생산모델에서 제외하였다.

### 7. EEMT와 지상부 생체량 AGB*

BIOME4 계산 후 각 셀에서 EEMT를 계산하여 지형발달모듈에 전달하였다. 유효강수는 월강수량에서 BIOME4의 월 AET를 뺀 값으로 계산하였다.

`Peff_m = PPT_m - AET_m`

기후에너지항은 Pelletier et al. (2013)의 구현을 따라 월별 기온과 유효강수를 이용하여 계산하였다.

`E_ppt = Σ_m [T_m · c_w · Peff_m] / 10⁶`

여기서 `c_w = 4186 J kg⁻¹ K⁻¹`이고 월강수와 AET의 mm 값은 단위면적당 물질량으로 사용하였다. 생물에너지항은 BIOME4 NPP를 건조생체량으로 변환한 후 `H_bio = 22×10⁶ J kg⁻¹`, 탄소분율 `f_C = 0.50`을 적용하였다.

`E_bio = (NPP/1000/f_C) · H_bio / 10⁶`

`EEMT = E_ppt + E_bio`

최종 U008에서는 과거 설정에 존재했던 1–80 MJ m⁻² yr⁻¹ clipping을 적용하지 않는다.

지형결합에 사용되는 AGB*는 단순 `0.010×NPP`가 아니라 BIOME4의 최적 LAI와 PFT별 잎수명을 사용하여 계산하였다. Reich et al. (1992)의 잎수명–SLA 관계

`log10(SLA[cm² g⁻¹]) = 2.44 - 0.43·log10(leaf lifespan[month])`

를 이용해 LAI에서 잎 건조생체량을 산정하였다. 목본 PFT의 변재량은 Haxeltine and Prentice (1996)의 LAI–sapwood 관계와 BIOME4의 `stemcarbon = 0.5 kg C m⁻² LAI⁻¹`, 탄소분율 0.5를 연결하여 계산하였다. 최종 AGB*는 선택 PFT의 잎 건조생체량과 살아있는 변재 건조생체량의 합으로 정의하였다. 비식생 및 노출기반암 셀의 AGB*는 0으로 두었다.

### 8. 지형발달모듈

지형상태는 지표고도 z, 기반암고도 b, 이동가능한 토층 h로 구성하며 `z=b+h`이다. 동적모델에서만 각 0.1 kyr 기후–식생 시점 이후 다음 시점까지 지형을 갱신한다.

토양생성률의 기준값은 EEMT에 따라

`P0 = 0.037 · exp(0.030·EEMT)`  [m kyr⁻¹]

로 계산한다. 토층피복 효과는 사면법선방향 토심 `h cosθ`를 사용하여

`P_normal = P0 · exp[-(h cosθ)/0.50]`

로 계산하고, 이를 수직방향 풍화량으로 변환하였다. 기반암/토층 밀도비는 1.8이다.

비선형 사면수송계수는

`kd = 0.033·EEMT + 0.050·AGB*`

로 계산하였다. 임계경사는 `Sc = 1.50 m m⁻¹`이다. 각 격자면의 사면수송량은 Pelletier et al. (2013)의 비선형 형식을 사용하여

`q = -kd · h · S / [1 - (S/Sc)²]`

로 계산하였다. `|S| ≥ Sc`인 면에 분모를 임의로 보정하거나 Sc−ε의 물리적 상한을 두지 않고, 실제 지형을 사전에 threshold-slope adjustment하여 임계경사 이하의 상태로 되돌린 뒤 식을 계산한다. 유한차분 한 스텝에서 존재하는 이동가능 토층보다 많은 양을 반출하려는 경우에는 donor cell의 외향 flux만 비례축소하여 토심의 비음수성을 보장한다.

하천·집중류 침식은 Pelletier 계열의 `K = K0/EEMT` 관계를 사용하며 `K0 = 0.020`이다. 단위집수면적 `A/w`는 Pelletier (2010)의 격자해상도 의존성 보정경로를 사용하고, 흐름수용부 경사는 D8 receiver slope를 사용하였다. 계산된 토층침식량은 해당 서브스텝에서 실제 이용 가능한 토심을 넘을 수 없도록 제한하고, 초과침식은 기반암침식으로 전환하되 기반암침식 저항계수 10을 적용하였다. 고정된 기여면적 임계치로 하천과 사면을 이분하는 방식은 최종 strict path에서 사용하지 않는다.

융기는 전체 유역에 `U = 0.08 m kyr⁻¹`를 적용하였다. 이는 용늪에서 직접 측정된 융기율이 아니라 Lee et al. (2024)이 장기 태백산맥 삭박·exhumation rate와 맞추기 위해 사용한 80 mm kyr⁻¹의 regional uplift forcing을 채택한 모델 가정이다.

지형계산은 최대 0.1 kyr의 적응형 서브스텝을 사용한다. 한 trial에서 사면수송, 하천침식 또는 임계경사 조정에 따른 최대 지형변화가 0.025 m를 넘으면 해당 trial을 거부하고 dt를 절반으로 줄여 재계산한다. 최소 허용 서브스텝은 `1×10⁻¹⁰ kyr`이다. 이 0.025 m 값은 물리과정 계수가 아니라 수치해석 안정성을 위한 허용오차이다.

### 9. 식생 축약분류와 Jang et al. (2011) 주 검증

BIOME4의 full biome은 고식생자료와 비교하기 위해 용늪용 축약 식생형으로 변환하였다. 축약범주는 침엽수림(0), 낙엽활엽수림(1), 혼효림(2), 초본·개방식생(3), 비식생·노출기반암(4)이다. Native mixed forest biome 6, 7, 9는 우선 혼효림으로 두고, 활엽수군(PFT2–4)과 침엽·taiga 수목군(PFT5–7) 각각에서 가장 높은 potential NPP를 비교하였다. 어느 한 군의 비율이 51% 이상이면 해당 수목군으로 재분류하고, 51% 미만이면 혼효림을 유지하였다. 여러 PFT를 단순 합산하지 않고 각 군의 최대 NPP를 비교하여 PFT 수가 많은 군에 구조적 우위를 주지 않도록 하였다.

주 고식생 검증은 Jang et al. (2011)의 용늪 화분대 4구간만 사용하였다. 최종 corrected reduced mapping은 95_01=낙엽활엽수림, 95_02=혼효림, 95_03=낙엽활엽수림, 95_04=혼효림이다. 각 화분대 연대구간 내부에 포함되는 0.1 kyr 모델 출력시점을 각각 평가하며, 총 평가단위는 62개이다. 각 시점에서 유효 식생셀(축약등급 0–3) 가운데 해당 관측형에 허용된 식생등급이 유역의 1% 이상을 차지하면 일치로 판정하였다. class 4 비식생·노출기반암은 분모에서 제외하였다. 검증은 `per_output_time` 방식이며, 62개 시점은 서로 독립적인 62개 화분기록이 아니라 4개 고식생구간 안의 반복 시간평가이다.

최종 U008 회귀검사에서 정적모델은 24/62(38.71%), 동적모델은 55/62(88.71%)로 재현되어야 한다. 이 값은 과학코드나 진단출력을 수정할 때 생산모델과의 동일성을 확인하는 regression criterion으로 사용하였다.

### 10. Park et al. (2021) 기반 PFT 보조 검증

PFT 수준의 보조검증은 Park et al. (2021)의 YN-C 코어 화분계수 자료를 이용하였다. 자료는 72개 시료, 약 3181–515 cal BP 범위를 포함한다. 이 검증은 Jang 주 정확도에 합산하지 않고 별도의 보조검증으로 수행하였다.

육상 화분합은 Park 자료의 목본(A)과 초본(B) 범주를 기본으로 하되, 용늪 현지 습원식생의 영향이 큰 Alnus, Apiaceae, Filipendula, Sanguisorba 등 `EXCLUDE_LOCAL` 분류군을 제외하였다. 수생식물·사초과 및 포자는 `EXCLUDE_NONTERRESTRIAL`로 제외하였다. 아속을 분리할 수 없는 Pinus는 육상 화분합에는 포함하되 특정 PFT 그룹의 채점에는 사용하지 않았다.

채점 PFT 그룹은 다음과 같다.

| PFT 검증그룹 | 관측 분류군의 예 | BIOME4 PFT | 기본 출현문턱 | 모델 출현정의 |
|---|---|---:|---:|---|
| TBD | 낙엽성 온대활엽수 | 4 | 2% | optpft |
| BDE | Betula, Salix | 7 | 2% | optpft |
| CON | Abies, Picea, Tsuga, Cupressaceae | 5, 6 | 1% | potential |
| TBE | 상록활엽수 | 3 | 5% | optpft |
| GRS | Poaceae | 8 | 2% | optpft |
| DWD | Ephedra | 10 | 5% | optpft |

각 0.1 kyr 출력시점 t에 대해 `[t−0.05, t+0.05)` ka 범위에 들어오는 화분시료의 계수를 합산하여 그룹별 백분율을 계산하였다. 관측 백분율이 그룹별 문턱 이상이면 관측 출현으로 판정하였다. 모델은 유역 내 비기반암 셀에서 해당 그룹 PFT가 최소 1셀 이상 출현하면 모델 출현으로 판정하였다.

모델 출현정의는 `optpft`, `top2_npp`, `potential` 세 가지를 구현하였다. `optpft`는 최종 선택 PFT, `top2_npp`는 NPP 상위 2개 PFT 중 양의 NPP를 갖는 PFT, `potential`은 기후제약을 통과하고 양의 `optnpp`를 갖는 PFT이다. 기본 검증은 CON만 `potential`을 사용하고 나머지 그룹은 `optpft`를 사용한다. 이는 BIOME4에서 PFT4가 optpft이면서 PFT6이 present인 경우 cool mixed forest가 형성될 수 있어, optpft만 사용하면 혼효림 내부의 침엽성분을 누락할 수 있기 때문이다.

출력시점 × PFT 그룹별 TP, FP, FN, TN을 계산하고 accuracy, sensitivity, specificity 및 TSS를 산출하였다. 민감도 분석에서는 세 모델 출현정의를 모든 그룹에 동일하게 적용하고 관측문턱을 그룹 기본값 및 0.5, 1, 2, 5, 10%로 변화시켰다. 추가로 기존 Park 정량 holdout과 맞추기 위해 깊이 16–69 cm의 53개 시료만 사용한 분석도 별도로 수행하였다. 인접 0.1 kyr 출력창은 동일 화분시료를 공유할 수 있으므로 서로 독립적인 표본으로 해석하지 않았다.

### 11. 근권 습윤도 정규화 및 산불 구조 민감도 실험

생산모델 A의 얕은 토심에서 유효 뿌리가중치의 합 `rtop_eff+rbot_eff`가 1보다 작아지는 구조가 근권 습윤도와 산불계산에 미치는 영향을 조사하기 위해 B–E 변형을 구축하였다. 모든 변형은 U008의 기후, 토심–WHC 계산, 뿌리분포, BIOME4 생리계수, Pelletier 결합계수, 융기율 및 검증설정을 그대로 유지하고 Fortran hydrology 내부에서 지정된 변수만 변경하였다.

정규화 근권습윤도는

`wr_n = wr / max(rtop_eff + rbot_eff, 1×10⁻⁶)`

로 정의하였다.

| 변형 | 변경내용 |
|---|---|
| A | 최종 U008 기준형. `wet(d)=wr`; raingreen, `meanwr`, `supply=emax·wr` 모두 원본 경로 |
| B | fire 입력만 `wet(d)=wr_n` |
| C | B + raingreen 수분판정(`wr>offw`, `wr>onnw`)과 `meanwr(month,1)`에 `wr_n` 사용 |
| D | C + transpiration supply를 `supply=emax·wr_n`으로 변경 |
| E | B를 기준으로 fire 입력만 `wet(d)=w(1)`로 변경. supply, raingreen, meanwr는 B와 동일 |

E는 표토층 상대수분 자체가 fire에 미치는 영향을 분리하기 위한 분기실험이다. 토심이 0.30 m보다 얕으면 `rbot_eff=0`이고, 비기반암 셀에서는 `wr_n = w(1)`이 되므로 B와 E의 fire 입력은 이론적으로 동일하다. 실제 비교에서는 이 조건을 셀×시점 단위로 확인하였다.

B–E는 생산모델 선택을 위한 구조 민감도 분석이며 별도 경험계수를 추가하거나 관측자료에 맞추어 threshold를 재보정하지 않았다. Native fire threshold, threshold+0.05의 부분연소구간, `NPP<1000`일 때의 `NPP/1000` 연료보정은 모든 변형에서 동일하게 유지하였다. B/E 비교에서는 연료보정 직전의 잠재 건조·산불일수도 `raw_drydays` 진단량으로 별도 저장하였다.

### 12. 재현성 관리

최종 U008 생산배포본, PFT 검증판, 습윤도 민감도판은 서로 구분하여 SHA-256으로 관리하였다. 생산 과학식의 변경 여부는 생성 Fortran과 핵심 Python 모듈의 hash 및 diff로 확인하였다. 특히 A 모드에서 생성된 Fortran은 기존 U008 생성 Fortran과 바이트 수준으로 동일해야 하며, B–E는 각 실험에서 지정한 치환 외의 과학식 변경이 없어야 한다. 모든 실험에서 static과 dynamic을 21–0 ka, 0.1 kyr, 211시점으로 재실행하고 Jang 회귀점수를 확인하였다.

현재 방법론상 본문에서 인용할 생산모델은 U008-A이다. B–E는 주모델의 결과를 대체하지 않고 모델구조의 민감도를 평가하는 부록·민감도 분석으로 기술한다. 향후 B 또는 E를 최종 생산모델로 채택할 경우에는 해당 선택을 명시적으로 확정한 뒤 본문 6절의 fire/wetness 정의와 재현성 hash를 갱신해야 한다.

## 참고문헌

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693–709. https://doi.org/10.1029/96GB02344

Jackson, R. B., Canadell, J., Ehleringer, J. R., Mooney, H. A., Sala, O. E., & Schulze, E.-D. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389–411.

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*(3), 259–267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O., Bigelow, N. H., Prentice, I. C., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*(5), 1091–1120. https://doi.org/10.5194/esurf-12-1091-2024

Park, J., Jin, Q., Choi, J., Bahk, J., & Park, J. (2021). Late Holocene climate variability in central Korea indicated by vegetation, geochemistry, and fire records of the Yongneup moor. *Palaeogeography, Palaeoclimatology, Palaeoecology*, 110705. https://doi.org/10.1016/j.palaeo.2021.110705

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741–758. https://doi.org/10.1002/jgrf.20046

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365–392. https://doi.org/10.2307/2937116

McKenzie et al. (2003) 방식의 plant-available water capacity는 본 패키지의 SoilGrids 기반 AWC 적분 구현과 함께 사용하였다. 최종 원고에서는 사용자가 보유한 정확한 원문 서지정보를 확인하여 참고문헌 항목을 확정한다.
