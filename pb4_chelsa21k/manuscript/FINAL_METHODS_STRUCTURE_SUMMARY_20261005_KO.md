# 용늪 PB4 최종 방법론 구성 요약

작성일: 2026-10-05  
상태: **Methods 본문 작성 전 최종 구조 요약**

이 문서는 실제 논문 문장 작성에 앞서, 최종 방법론의 구성 순서, 수식, 출처, 변수 정의, 구현 범위를 하나로 정리한 기준 문서이다. 이후 Methods 본문은 이 문서의 순서와 구분을 따라 작성한다.

## 1. 전체 연구 구조

최종 계산 흐름은 다음과 같다.

    기후
    → 토심과 토양수분
    → PFT별 뿌리 접근성
    → BIOME4
    → NPP, AET, LAI, PFT
    → EEMT와 BIOME4-derived AGB*
    → Pelletier 지형발달
    → 새로운 지표고도, 기반암고도, 토심
    → 다음 100년 시점의 BIOME4 재계산

시간범위는 21.0-0.0 ka BP이며, 100년 간격 211시점을 사용한다.

dynamic 계산에서는 매 100년 시점마다 지형과 토심을 갱신하고 다음 시점 식생계산에 다시 입력한다. static 계산에서는 초기 지형과 토심을 고정한 채 같은 기후시계열에 대해 BIOME4만 반복 실행한다.

지형모형 내부에서는 수치안정성을 위해 adaptive substep을 사용할 수 있으나, 각 geomorphic substep마다 새로운 기후시점을 읽거나 BIOME4를 재실행하지 않는다.

## 2. 기후입력

주 기후자료는 YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv를 사용한다.

자료는 CHELSA-TraCE21k / EnviCloud 계열이며 월별 Tmin, Tmax, 강수를 사용한다.

CHELSA 원자료의 Tmin과 Tmax는 Kelvin이므로 월평균기온은 다음과 같이 변환한다.

HWP 입력:

    T_{mean}={(T_{min}+T_{max}) OVER 2}-273.15

CHELSA는 이미 지형 하향화된 자료이므로 추가 고도감률 보정은 적용하지 않는다.

BIOME4 absolute minimum temperature는 원 BIOME4 회귀식을 사용한다.

    T_{absmin}=0.006 T_{cold}^2+1.316 T_{cold}-21.9

CHELSA-TraCE21k Centennial 자료에 cloud 변수가 없으므로 BIOME4 광입력에 필요한 cloud만 기존 Beyer 계열 자료에서 보간한다. Beyer의 기온과 강수는 사용하지 않는다.

CO2는 기존 PB4Studio와 동일한 Bereiter 계열 기록을 사용한다.

## 3. BIOME4 식생모형

식생 코어는 BIOME4 v4.2b2로 고정한다.

BIOME4의 직접 모델 참고문헌은 Kaplan et al. (2003)이다. BIOME4는 기후와 토양조건에 따라 PFT별 NPP를 계산하고, 각 PFT에서 NPP를 최대화하는 seasonal maximum LAI를 결정한다. 이후 PFT 경쟁을 통해 biome을 판정한다.

최종 PB4 설정은 PB4-McKenzie-nativeClimate이며 다음을 유지한다.

- BIOME4 v4.2b2의 native PFT5/PFT6 climate limits
- McKenzie 기반 토심별 AWC coupling
- PFT별 finite-depth root accessibility
- 검증용 reduced classification에서 51% 과반 규칙
- dynamic Pelletier 식생-지형 coupling

중요한 구분은 다음과 같다. BIOME4 내부 PFT 경쟁과 생리계산은 원 식생모형의 과정이다. 반면 51% 과반 규칙은 화분자료 검증을 위한 reduced-class 후처리이며 BIOME4 내부 식생생리식이 아니다.

## 4. 토심과 토양 수분보유능

토심에 따른 식생반응은 NPP나 LAI에 임의의 보정계수를 직접 곱하지 않는다.

토심의 영향은 다음 경로를 통해서만 BIOME4에 전달한다.

    토심 H
    → 토양 수분보유능
    → PFT별 뿌리 접근성
    → BIOME4 수분스트레스
    → NPP와 LAI

McKenzie의 profile AWC 개념을 SoilGrids 수분특성에 적용하고, BIOME4의 native 2층 수문구조인 0-0.30 m, 0.30-1.50 m를 유지한다.

전체 수분보유능:

    WHC(H,T)=WHC_{top}(H,T)+WHC_{bottom}(H,T)

상층:

    WHC_{top}(H,T)=1000 INT _0^{min(H,0.30)} [theta_{-10}(xi,T)-theta_{-1500}(xi,T)] d xi

하층:

    WHC_{bottom}(H,T)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} [theta_{-10}(xi,T)-theta_{-1500}(xi,T)] d xi

이 식은 McKenzie의 profile AWC 정의와 BIOME4의 2층 수문구조를 결합한 PB4 구현식이다. McKenzie (2003)의 원식이라고 직접 표기하지 않는다.

## 5. PFT별 finite-depth root accessibility

BIOME4의 PFT별 상부 30 cm 뿌리비율 r_{30,p}을 지수형 뿌리 깊이분포에 연결한다.

특성깊이는 다음과 같이 계산한다.

    X_p=-{0.30 OVER ln(1-r_{30,p})}

실제 사용 가능한 수문깊이는

    D=min(max(H,0),1.50)

로 제한한다.

상층 접근 뿌리비율은

    R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})

이다.

하층 접근 뿌리비율은

    R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}

이다.

출처 구분은 다음과 같이 한다.

- r_{30,p}: BIOME4 / Jackson 계열
- 지수형 깊이감쇠: McKenzie 계열
- X_p=-0.30/ln(1-r_{30,p}): 두 구조를 연결하기 위한 본 연구의 분석적 변환

따라서 마지막 식을 McKenzie 또는 BIOME4 원식으로 표기하지 않는다.

## 6. EEMT

EEMT는 Pelletier et al. (2013)의 유효강수 에너지와 생물생산 에너지 개념을 사용하되, 현재 PB4에서 실제 계산되는 월별 형태를 방법론에 제시한다.

HWP 입력:

    EEMT={C_w OVER 10^6} SUM _{m=1}^{12} T_m (P_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}

사용값:

    C_w=4186

    h_{BIO}=22 times 10^6

    f_C=0.50

여기서 NPP_C는 BIOME4가 출력하는 탄소 기준 NPP이다.

f_C=0.50은 dry biomass 변환을 위한 명시적 모델 가정으로 표기한다. BIOME4 원 파라미터라고 쓰지 않는다.

## 7. BIOME4-derived AGB*

최종 AGB 방식은 **BIOME4-derived aboveground living biomass proxy (AGB*)**로 고정한다.

최초 Methods 정의에서 AGB*는 잎과 살아 있는 변재를 포함한다고 명시한다. 심재, 굵은 가지 등 BIOME4가 독립 standing stock으로 제공하지 않는 장기 목질부를 포함한 total anatomical AGB는 아니다.

### 7.1 잎 건조생체량

Reich et al. (1992), Table 1의 전체 LEAVES 회귀식:

    log_10(SLA)=2.44-0.43 log_10(L_m)

원 논문에서 life-span 단위는 month이고 SLA 단위는 cm^2 g^-1이다.

따라서

    SLA=10^{2.44} L_m^{-0.43}

이다.

단위를 m^2 kg^-1로 변환하면

    SLA=27.542287 L_m^{-0.43}

이다.

SLA는 leaf area / leaf dry mass이고 LAI는 leaf area / ground area이므로

    B_{leaf,dry}={LAI OVER SLA}

가 된다.

최종적으로

    B_{leaf,dry,p}=0.0363078055 LAI_p L_{m,p}^{0.43}

이다.

단위는 kg dry biomass m^-2이다.

### 7.2 변재 건조생체량

Haxeltine and Prentice (1996), BIOME3 Eq. (34)의 실제 출판식:

    C_s=LAI C_n

BIOME4 v4.2b2 source code에서는

    stemcarbon=0.5

를 사용한다.

따라서 BIOME4 구현의 sapwood carbon은

    C_{sapwood,p}=0.5 LAI_p

로 계산한다.

dry biomass conversion에 f_C=0.50을 적용하면

    B_{sapwood,dry,p}=S_p LAI_p

가 된다.

여기서 S_p는 본 연구가 정의한 indicator이다.

    S_p=1 , pftpar(p,10)=1

    S_p=0 , pftpar(p,10)=2

S_p를 BIOME4 원 변수명으로 쓰지 않는다.

### 7.3 최종 AGB* 식

최종식은 다음 하나로 통일한다.

    AGB^*_{dry,p}=LAI_p [S_p+0.0363078055 L_{m,p}^{0.43}]

단위는 kg dry biomass m^-2이다.

기존 AGB=0.010 x NPP, Xue/IBIS, JULES 방식은 production 식으로 사용하지 않는다.

## 8. Pelletier 지형모형과 AGB* 결합

Pelletier et al. (2013)의 EEMT-AGB 지형결합 구조는 유지한다.

사면수송계수는

    k_d=c EEMT+d AGB^*

이고 최종 구현은

    k_d=0.033 EEMT+0.05 AGB^*

이다.

Pelletier et al. (2013)의 직접적인 EEMT-to-AGB 지수식

    AGB=e exp(f EEMT)

은 용늪에 사용하지 않는다.

이 식은 Pelletier 원 연구의 대상지 경험식이며, 용늪 EEMT가 원 실험범위를 크게 초과하기 때문에 직접 외삽할 경우 AGB가 비현실적으로 폭주한다.

따라서 방법론에서는 Pelletier의 지형수송 결합식은 유지하고 AGB 상태변수만 BIOME4-derived AGB*로 대체한다고 설명한다.

## 9. 토양생산과 사면수송

Pelletier의 EEMT 의존 토양생산 구조를 유지한다.

    P_0=a exp(b_E EEMT)

토심에 따른 토양생산은

    P=P_0 exp(-{H cos theta OVER H_0})

이다.

비선형 사면수송은

    q=-{k_d H cos theta grad z OVER {1-({|grad z| OVER S_c})^2}}

으로 정리한다.

여기서 k_d에 최종 AGB*가 들어간다.

## 10. 유수침식

잠재 유수침식은

    E_{f,pot}={K_0 OVER EEMT}{A OVER w}S_f

로 계산한다.

유로폭은

    w=g A^i

이다.

실제 regolith removal은 한 step에서 가용 토심을 초과하지 못하도록 공급제약을 적용한다.

    E_{f,reg}=min(E_{f,pot},{H_{avail} OVER Delta t})

이 공급제약은 Pelletier 원 Eq. (16) 자체가 아니라 PB4의 수치적 확장이다.

## 11. dynamic coupling 계산순서

한 100년 시점의 계산순서는 다음과 같다.

    1. 현재 z, b, H 읽기
    2. 기후입력 읽기
    3. H에 따른 WHC 계산
    4. PFT별 finite-depth root accessibility 계산
    5. BIOME4 실행
    6. NPP, AET, LAI, PFT 계산
    7. EEMT 계산
    8. BIOME4-derived AGB* 계산
    9. Pelletier 토양생산, 사면수송, 유수침식 계산
    10. z, b, H 갱신
    11. 다음 100년 시점으로 이동

dynamic에서는 10번에서 갱신된 지형과 토심이 다음 BIOME4 계산에 다시 들어간다.

static에서는 지형과 토심을 갱신하지 않는다.

## 12. 검증

주 검증자료는 Jang et al. (2011)이다.

사용 record:

    95_01
    95_02
    95_03
    95_04

총 62개 100년 output-time을 평가한다.

검증 식생군은 Jang et al. (2011)의 원문 식생대에 맞춘 corrected reduced mapping을 사용한다.

주 판정기준은 목표 식생군이 유역 내 valid cell의 1% 이상 출현하는지 여부이다.

최종 AGB* 적용 후 검증결과:

    static: 24/62 = 38.71%
    dynamic: 55/62 = 88.71%

이는 기존 nativeClimate baseline과 동일하다.

Park et al. (2021)은 이 62개 categorical 총점에 합치지 않는다. 최종모형을 Jang 검증으로 고정한 뒤 수행하는 독립 holdout으로만 사용하며, Park 결과를 이용한 재보정은 하지 않는다. Park의 Supplementary sample-level pollen composition을 100년 window로 집계하되 보간하지 않고, 완전히 발달한 peatland 이후인 69-16 cm 구간을 주 정량 비교구간으로 사용한다. 지역 식생 비교는 conifer와 deciduous broadleaf의 상대조성, arboreal/non-arboreal 변화방향, 2738-2206 cal yr BP의 arboreal 감소와 herbaceous 증가 사건 재현을 중심으로 평가한다. pollen percentage와 model area fraction은 같은 물리량이 아니므로 binary accuracy나 절대 RMSE보다 Spearman 상관과 변화방향 일치도를 주 지표로 사용한다. 세부 정책은 PARK2021_INDEPENDENT_VALIDATION_POLICY_20261006_KO.md를 따른다.

## 13. 최종 AGB* 실행 결과

동일 CHELSA-TraCE21k/EnviCloud forcing으로 21.0-0.0 ka BP, 0.1 kyr 간격의 static과 dynamic 각각 211시점을 새 AGB* 식으로 다시 실행했다.

21 ka 전체 basin mean AGB*의 시계열 평균:

    static = 3.19979 kg m^-2
    dynamic = 3.11600 kg m^-2

0 ka:

    static = 3.48349 kg m^-2
    dynamic = 3.46620 kg m^-2

0 ka dynamic:

    34.662 t ha^-1

기존 0.010 x NPP bridge보다 21 ka 평균은 약 22% 낮고, 0 ka에서는 약 43% 낮다.

## 14. Methods 작성 시 반드시 유지할 출처 구분

### BIOME4

Kaplan et al. (2003)

- BIOME4의 모델구조
- PFT
- NPP
- optimal LAI
- biome competition

### Haxeltine and Prentice (1996)

- BIOME3 Eq. (34)
- sapwood carbon과 LAI의 관계

    C_s=LAI C_n

BIOME4가 BIOME3에서 계승한 관계의 원전으로 사용한다.

### BIOME4 v4.2b2 source code

- stemcarbon=0.5
- pftpar(pft,7)
- pftpar(pft,10)
- 실제 PFT별 parameter

즉 출판식과 BIOME4 실제 구현계수를 구분한다.

### Reich et al. (1992)

- SLA-life-span 회귀식

    log_10(SLA)=2.44-0.43 log_10(life-span)

### McKenzie et al. (2003)

- profile AWC 개념
- 지수형 root-density scaling의 근거

### Pelletier et al. (2013)

- EEMT 개념
- 토양생산
- 비선형 사면수송
- EEMT와 AGB가 k_d에 들어가는 구조
- 유수침식

Pelletier Eq. (5)의 직접 EEMT-to-AGB 지수식은 최종 용늪모형에서 사용하지 않는다.

## 15. 폐기된 AGB 경로

다음은 최종 Methods에서 production 식으로 제시하지 않는다.

    AGB=0.010 x NPP

출처가 충분하지 않은 historical comparator이다.

Xue/IBIS 방식은 PFT 대응과 aboveground 해석이 충분히 정합되지 않아 sensitivity only로 남긴다.

JULES 방식은 별도 vegetation model의 allometry를 BIOME4에 전이하는 방식이므로 sensitivity only로 남긴다.

Pelletier Eq. (5)의

    AGB=e exp(f EEMT)

는 용늪 EEMT 범위에서 직접 외삽하지 않는다.

## 16. 실제 Methods 본문 권장 순서

실제 논문 문장은 다음 순서로 작성한다.

    1. 연구대상지와 초기 지형자료
    2. 기후자료와 21 ka forcing
    3. BIOME4 식생모형
    4. 토심-토양수분-뿌리 coupling
    5. EEMT
    6. BIOME4-derived AGB*
    7. Pelletier 지형발달모형
    8. static과 dynamic 실험설계
    9. 고식생 검증
    10. 수치구현과 시간간격

이 순서에서는 원인과 피드백이 자연스럽게 이어지며, AGB*가 Pelletier 지형식 안에서 어떤 역할을 하는지 앞뒤가 끊기지 않는다.

## 17. 문체 및 표기 원칙

실제 본문 작성 시 다음을 유지한다.

- 한국어를 우선한다.
- pH, EC, PCA, MANOVA, NBR, dNBR, NPP, LAI, AET, EEMT, AGB, PFT, WHC 등 학계에서 통상 사용하는 약어는 유지한다.
- 가운뎃점은 사용하지 않는다.
- 원문식, 본 연구의 결합식, 코드 구현식을 구분한다.
- 본 연구에서 새로 정의한 S_p, X_p 등의 변수는 새 정의임을 명시한다.
- 모델명과 파일명은 실제 사용 버전을 적는다.
- 결과값을 방법론 근거처럼 섞지 않고, 필요한 실행 및 검증 정보만 Methods 마지막에 배치한다.
- 과거 후보식은 최종 Methods 본문에서 길게 설명하지 않고 sensitivity 또는 Supplementary로 이동한다.

## 18. 권위 기준 문서

AGB* 수식과 참고문헌의 최종 기준:

    pb4_chelsa21k/manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md

최종 통합 package와 실행결과:

    pb4_chelsa21k/results/final_integrated_20261006/FINAL_INTEGRATED_DECISION_KO.md

최종 과학모형 결정 이력:

    pb4_chelsa21k/results/native_climate_final_20261005/FINAL_MODEL_DECISION_KO.md

AGB 최종 선택 결정:

    pb4_chelsa21k/results/agb_bridge_comparison_20261005/AGB_BRIDGE_PROMOTION_DECISION_KO.md

전체 모델 프로세스:

    pb4_chelsa21k/PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md

최종 canonical SHA-256:

    a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34

Park 독립검증 정책:

    pb4_chelsa21k/manuscript/PARK2021_INDEPENDENT_VALIDATION_POLICY_20261006_KO.md

## 19. 핵심 참고문헌

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. Journal of Geophysical Research: Atmospheres, 108(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. Global Biogeochemical Cycles, 10(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. Ecological Monographs, 62(3), 365-392. https://doi.org/10.2307/2937116

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). Estimating water storage capacities in soil at catchment scales. CRC for Catchment Hydrology.

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. Journal of Geophysical Research: Earth Surface, 118, 741-758. https://doi.org/10.1002/jgrf.20046

BIOME4 v4.2b2 source code, Jed O. Kaplan:
https://github.com/jedokaplan/BIOME4
