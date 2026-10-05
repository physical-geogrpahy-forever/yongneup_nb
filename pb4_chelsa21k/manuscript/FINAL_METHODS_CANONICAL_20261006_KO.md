# 용늪 PB4 최종 방법론 기준문서

작성일: 2026-10-06  
상태: **최종 Methods 기준문서, 원식 대조 완료**

이 문서는 용늪 PB4 연구의 논문 Methods에서 사용할 수식, 변수, 구현식과 검증 절차를 통일한 기준문서이다.

핵심 원칙은 다음과 같다.

- 출판문헌에서 가져온 수식은 가능한 한 원식과 원 기호를 그대로 제시한다.
- 본 연구에서 문헌들을 연결하여 새로 만든 식은 반드시 "본 연구 구현식"으로 구분한다.
- 단순한 대수 전개나 단위변환으로 생긴 소수계수를 독립 파라미터처럼 제시하지 않는다.
- 코드의 수치안정화 장치와 물리적 또는 생태적 파라미터를 구분한다.
- 최종 정량 검증은 Jang et al. (2011)만 사용한다.

## 1. 실행 provenance

- 기후자료: \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`
- 기간: 21.0-0.0 ka BP
- 간격: 0.1 kyr, 총 211 시점
- 식생모형: BIOME4 v4.2b2
- production configuration: PB4-McKenzie-nativeClimate + BIOME4-derived AGB*
- 모델 버전: \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`
- 최종 package SHA-256: \`a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34\`
- 검증자료: Jang et al. (2011)
- 검증 표본: 62개 100년 output-time

## 2. 표기 원칙과 원문 기호의 대응

논문 전체에서 상태변수는 다음처럼 통일한다.

| 본문 기호 | 의미 | 단위 |
|---|---|---|
| \(t_{\mathrm{BP}}\) | 연대 좌표 | ka BP |
| \(\tau\) | 정방향 모델 적분시간 | kyr |
| \(z\) | 지표고도 | m |
| \(z_b\) | 기반암 또는 풍화전선 고도 | m |
| \(H\) | 토심 또는 레골리스 두께 | m |
| \(T_m\) | 월평균기온 | °C |
| \(R_m\) | 월강수량 | mm month\(^{-1}\) |
| \(AET_m\) | 월 실제증발산 | mm month\(^{-1}\) |
| \(NPP_C\) | BIOME4 carbon NPP | g C m\(^{-2}\) yr\(^{-1}\) |
| \(LAI_p\) | PFT \(p\)의 optimal LAI | 무차원 |
| \(AGB^*\) | BIOME4-derived aboveground living biomass proxy | kg dry biomass m\(^{-2}\) |

Pelletier et al. (2013)의 원식에서는 기반암고도를 \(b\), 토심을 \(h\), 시간을 \(t\)로 표기한다. 원문식을 인용할 때는 이 기호를 그대로 유지한다. 실제 PB4 설명에서는 다음과 같이 대응한다.

\[
b\rightarrow z_b,\qquad
h\rightarrow H,\qquad
t\rightarrow\tau
\]

따라서 Pelletier의 경험계수 \(b\)와 기반암고도 \(b\)가 같은 문단에서 혼동되지 않도록, 본 연구 상태변수의 기반암고도는 항상 \(z_b\)로 쓴다.

## 3. 기후입력과 BIOME4

CHELSA-TraCE21k/EnviCloud의 월별 Tmin, Tmax, 강수를 사용한다. 원자료의 Tmin과 Tmax는 Kelvin이므로 월평균기온은

\[
T_m=
\frac{T_{\min,m}+T_{\max,m}}{2}
-273.15
\]

로 변환한다.

CHELSA 자료에는 추가 고도감률 보정을 적용하지 않는다.

BIOME4 v4.2b2의 absolute minimum temperature 회귀식은 원 코드 그대로 사용한다.

\[
T_{\mathrm{absmin}}
=
0.006T_{\mathrm{cold}}^2
+
1.316T_{\mathrm{cold}}
-
21.9
\]

CHELSA-TraCE21k Centennial 자료에 cloud가 없으므로 BIOME4 광입력에 필요한 cloud만 Beyer 계열 자료에서 시간 보간한다. Beyer의 기온과 강수는 사용하지 않는다. CO2는 PB4Studio에 포함된 Bereiter 계열 기록을 사용한다.

식생 코어는 BIOME4 v4.2b2이다. production에서는 native PFT climate limits를 사용한다. 토심에 따른 NPP, LAI 또는 FVC의 직접적인 경험 multiplier는 사용하지 않는다.

## 4. 토심과 available-water storage

토심은

\[
\boxed{
H=z-z_b
}
\]

로 정의한다.

### 4.1 McKenzie et al. (2003)의 원 개념

McKenzie et al. (2003)은 profile available water capacity를 \(-10\) kPa와 \(-1.5\) MPa에서의 체적수분함량 차이에 기반하여 정의한다.

\[
AWC(\zeta)
=
\theta_{-10}(\zeta)
-
\theta_{-1500}(\zeta)
\]

또한 뿌리밀도의 깊이 가중함수는

\[
\boxed{
f(x)=\exp\left(-\frac{x}{X_i}\right)
}
\]

로 제시한다.

이 두 관계가 McKenzie에서 직접 가져온 부분이다. McKenzie et al. (2003)이 BIOME4용 2층 토심모형을 제시한 것은 아니다.

### 4.2 본 연구의 BIOME4 2층 구현

PB4는 McKenzie의 available-water 개념을 용늪 SoilGrids profile에 적용하면서 BIOME4의 기존 0-0.30 m와 0.30-1.50 m 수문층을 유지한다.

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

이는 **본 연구 구현식**이다.

production code에 사용된 깊이별 available-water density는 다음과 같다.

| 깊이 m | mm m\(^{-1}\) |
|---|---:|
| 0.00-0.05 | 237 |
| 0.05-0.15 | 232 |
| 0.15-0.30 | 218 |
| 0.30-0.60 | 207 |
| 0.60-1.00 | 198 |
| 1.00-2.00 | 179 |

BIOME4의 구조적 수문깊이 상한 때문에 실제 적분은 1.50 m까지만 수행한다.

## 5. PFT별 finite-depth root accessibility

BIOME4 v4.2b2의 \`pftpar(pft,6)\`은 Jackson et al. 계열의 상부 30 cm 누적 뿌리분율이다. 이를 \(r_{30,p}\)로 쓴다.

Jackson 계열의 누적 뿌리분포는

\[
Y(d)=1-\beta^d
\]

의 지수형 구조를 갖는다.

PB4에서는 이를 McKenzie의

\[
f(x)=\exp(-x/X_i)
\]

와 연결한다. 따라서 다음 특성깊이는 문헌 원식이 아니라 **본 연구의 분석적 변환**이다.

\[
\boxed{
X_p
=
-\frac{0.30}
{\ln(1-r_{30,p})}
}
\]

BIOME4에서 사용할 유효 토심은

\[
D=\min[\max(H,0),1.50]
\]

으로 두며, 접근 가능한 상층과 하층 뿌리분율은

\[
R_{\mathrm{top},p}
=
1-
\exp
\left[
-\frac{\min(D,0.30)}{X_p}
\right]
\]

\[
R_{\mathrm{bottom},p}
=
\begin{cases}
0, & D\le0.30\\
\exp(-0.30/X_p)-\exp(-D/X_p), & D>0.30
\end{cases}
\]

로 계산한다.

BIOME4 hydrology의 root-zone wetness는

\[
\omega_{r,p}
=
R_{\mathrm{top},p}\omega_{\mathrm{top}}
+
R_{\mathrm{bottom},p}\omega_{\mathrm{bottom}}
\]

으로 계산한다.

위 네 식은 McKenzie와 Jackson의 관계를 BIOME4 2층 수문구조에 연결한 **본 연구 구현식**이다. 얕은 토양에서 \(R_{\mathrm{top},p}+R_{\mathrm{bottom},p}<1\)이어도 1로 재정규화하지 않는다.

## 6. EEMT

### 6.1 Pelletier et al. (2013)의 원식

유효강수 에너지와 생물생산 에너지는 원문 Eq. (1)과 Eq. (2)를 그대로 사용한다.

\[
\boxed{
E_{\mathrm{PPT}}
=
\Delta T\,C_wP_{\mathrm{eff}}
}
\]

\[
\boxed{
E_{\mathrm{BIO}}
=
NPP\,h_{\mathrm{BIO}}
}
\]

따라서

\[
EEMT
=
E_{\mathrm{PPT}}
+
E_{\mathrm{BIO}}
\]

이며 \(P_{\mathrm{eff}}=PPT-ET\)이다.

### 6.2 PB4의 월별 구현

BIOME4가 월별 AET와 탄소 기준 NPP를 제공하므로 PB4에서는 위 원식을 다음과 같이 구현한다.

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

여기서

\[
C_w=4186\ {\rm J\,kg^{-1}\,K^{-1}},
\qquad
h_{\mathrm{BIO}}=22\times10^6\ {\rm J\,kg^{-1}}
\]

이고 \(f_C=0.50\)은 carbon NPP를 dry biomass로 변환하기 위한 본 연구의 명시적 가정이다.

이 월별 합산식은 Pelletier 원문의 별도 번호식이 아니라 **원 Eq. (1)-(2)를 BIOME4 출력에 적용한 본 연구 구현식**이다.

코드에서는 \(R_m-AET_m\)을 0으로 clip하지 않으며, EEMT 자체에도 과거 PB4의 1-80 MJ m\(^{-2}\) yr\(^{-1}\) clipping을 적용하지 않는다.

## 7. BIOME4-derived AGB*

본 연구에서 Pelletier의 AGB 항은 total anatomical AGB가 아니라 BIOME4-derived aboveground living biomass proxy \(AGB^*\)로 대체한다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
}
\]

### 7.1 잎

Reich et al. (1992)의 원 회귀식을 그대로 사용한다.

\[
\boxed{
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
}
\]

\(L_{m,p}\)의 단위는 month, \(SLA_p\)의 원 단위는 cm\(^2\) g\(^{-1}\)이다.

SLA의 정의에 따라

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
}
\]

로 계산하며, 계산 시 SLA 단위만 m\(^2\) kg\(^{-1}\)로 변환한다.

논문 본문에서는 이를 전개해 얻는 \`0.0363078055...\`를 별도의 계수로 제시하지 않는다.

### 7.2 변재

Haxeltine and Prentice (1996) Eq. (34)의 원식은

\[
\boxed{
C_s=LAI\,C_n
}
\]

이다.

BIOME4 v4.2b2 source code에서 \`stemcarbon=0.5\`는 sapwood carbon per unit LAI로 사용된다. 따라서 BIOME4에서 sapwood respiration이 활성인 PFT는 \(C_n=0.5\)를 적용하며,

\[
B_{\mathrm{sapwood,dry},p}
=
\frac{C_{\mathrm{sapwood},p}}{f_C}
\]

로 dry biomass로 변환한다. \(f_C=0.50\)은 본 연구의 명시적 변환 가정이다.

BIOME4 source에서 sapwood respiration을 제거하는 PFT에는 sapwood term을 적용하지 않는다. 이를 위해 코드에서 indicator를 사용할 수 있지만, 논문 원식에 새로운 생태 파라미터처럼 제시하지 않는다.

## 8. Pelletier 지형발달

이 절에서는 Pelletier et al. (2013)의 원식을 그대로 제시한다. 실제 PB4에서는 \(b\rightarrow z_b\), \(h\rightarrow H\), \(t\rightarrow\tau\), \(AGB\rightarrow AGB^*\)로 대응한다.

### 8.1 상태변수와 토양생산

Pelletier Eq. (6):

\[
\boxed{
z=b+h
}
\]

Eq. (7):

\[
\boxed{
\frac{\partial b}{\partial t}
=
U
-
\frac{P}{\cos\theta}
}
\]

Eq. (8):

\[
\boxed{
\frac{\partial h}{\partial t}
=
\frac{\rho_b}{\rho_s}
\frac{P}{\cos\theta}
-
E
}
\]

Eq. (9):

\[
\boxed{
P
=
P_0
\exp
\left(
-\frac{h\cos\theta}{h_0}
\right)
}
\]

Eq. (10):

\[
\boxed{
P_0
=
a\exp(b\,EEMT)
}
\]

여기서 \(a\), \(b\), \(h_0\)는 Pelletier 원문의 기호를 그대로 유지한다. 별도의 \(a_P\), \(b_P\)로 다시 이름 붙이지 않는다.

### 8.2 사면수송

Pelletier Eq. (11):

\[
\boxed{
E_c
=
\nabla\cdot\mathbf q
}
\]

본 연구에서 실제 사용하는 depth-dependent nonlinear transport는 Pelletier Eq. (14)이다.

\[
\boxed{
\mathbf q
=
-
\frac{
k_dh\cos\theta\,\nabla z
}{
1-(|\nabla z|/S_c)^2
}
}
\]

기후와 식생에 따른 수송계수는 Eq. (15)를 그대로 사용한다.

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB
}
\]

PB4에서는 마지막 항의 \(AGB\)만 \(AGB^*\)로 대체한다.

\[
\boxed{
k_d
=
c\,EEMT
+
d\,AGB^*
}
\]

이는 Pelletier Eq. (15)의 결합구조를 유지하면서 biomass 상태변수만 BIOME4-derived \(AGB^*\)로 바꾼 것이다. \(k_d\), \(c\), \(d\)를 다른 기호로 다시 정의하지 않는다.

### 8.3 유수침식

Pelletier Eq. (16):

\[
\boxed{
E_f
=
K
\frac{A}{w}
|\nabla z|
}
\]

Eq. (17):

\[
\boxed{
w=gA^i
}
\]

Eq. (18):

\[
\boxed{
K
=
\frac{K_0}{EEMT}
}
\]

따라서 논문 본문에서는 \(K_f\), \(A_c\), \(w_c\)와 같은 새 기호로 원식을 다시 쓰지 않는다.

PB4 수치구현에서는 \(|\nabla z|\)을 flow-routing 방향 경사로 평가하고, 한 substep에서 실제 가용 레골리스보다 많은 물질을 제거하지 못하도록 finite-supply constraint를 적용한다. 이 부분은 Pelletier Eq. (16)-(18)의 원식이 아니라 **PB4 수치구현 확장**으로 별도 기술한다.

## 9. Pelletier 원 연구값과 용늪 production 값의 구분

최종 package의 지형모형 코드와 보존된 source audit를 대조하면 다음과 같다.

| 항목 | Pelletier et al. (2013) | 용늪 production |
|---|---:|---:|
| \(a\) | 0.037 m kyr\(^{-1}\) | 0.037 |
| \(b\) | 0.030 m\(^2\) yr MJ\(^{-1}\) | 0.030 |
| \(h_0\) | 0.50 m | 0.50 m |
| \(\rho_b/\rho_s\) | 1.8 | 1.8 |
| \(c\) | 0.033 | 0.033 |
| \(d\) | 0.050 | 0.050 |
| \(K_0\) | 0.020 m\(^2\) MJ\(^{-1}\) | 0.020 |
| \(S_c\) | 0.7, 0.9 sensitivity | **1.50** |
| \(U\) | 0.05 m kyr\(^{-1}\) | **0.20 m kyr\(^{-1}\)** |

따라서 \(S_c=1.50\)과 \(U=0.20\)은 Pelletier et al. (2013)의 원 연구값이라고 쓰면 안 된다. \(S_c=1.50\)은 용늪 20 m real-DEM 수치수렴시험을 거쳐 채택된 모델별 수치설정이다. \(U=0.20\ {\rm m\,kyr^{-1}}\)은 현재 package에 '동해안 융기율 참고값'으로 기록되어 있으나, 현재 GitHub 보존자료에서는 이를 직접 뒷받침하는 서지문헌을 확인하지 못했다. 따라서 투고본에서 이 값을 유지하려면 별도의 지역 융기율 문헌을 명시적으로 연결해야 하며, 그 전까지는 '문헌 검증 필요' 파라미터로 취급한다.

또한 Pelletier의 모델실험 EEMT 범위는 대략 5-45 MJ m\(^{-2}\) yr\(^{-1}\)였으나 용늪 PB4에서는 이 범위를 넘는 EEMT가 발생한다. 따라서 EEMT 관련 계수의 외삽은 한계로 명시한다.

## 10. 수치해석과 source equation의 구분

Pelletier et al. (2013)의 물리식과 별개로 PB4에는 다음 수치 구현이 있다.

- 100년 coupling interval 내부의 adaptive geomorphic substep
- finite-volume donor-supply positivity constraint
- 실제 DEM의 초임계 경사를 처리하는 threshold-slope adjustment
- open outlet의 fixed base-level boundary
- accepted state를 float64로 유지
- 최대 허용 변화량 0.025 m를 기준으로 한 adaptive trial rejection

0.025 m는 물리 파라미터가 아니다. Pelletier et al. (2013)은 timestep을 동적으로 줄여 안정성을 확보했지만 이 프로젝트의 0.025 m 값 자체는 PB4 convergence audit에서 정한 **수치오차 허용기준**이다.

기본 explicit timestep 추정은 Pelletier의 형태를 따라

\[
\Delta t
=
0.01
\frac{\Delta x^2}
{2k_{d,\max}}
\]

를 사용하고, 필요할 경우 더 작은 substep으로 줄인다.

## 11. dynamic coupling

한 100년 coupling interval의 계산순서는 다음과 같다.

\`\`\`text
현재 z, z_b, H
-> 해당 t_BP의 CHELSA 기후
-> available-water storage
-> PFT별 root accessibility
-> BIOME4
-> NPP, AET, LAI, dominant PFT
-> EEMT, AGB*
-> Pelletier 지형발달
-> 새로운 z, z_b, H
-> 다음 t_BP
\`\`\`

각 100년 구간에서 BIOME4를 한 번 계산하고, 그 구간의 geomorphic adaptive substep 동안 동일한 EEMT와 AGB* forcing을 사용한다.

static 실험에서는 초기 지형과 토심을 고정한다. dynamic 실험에서는 변화한 지형과 토심이 다음 시점의 수문과 BIOME4 계산으로 다시 들어간다.

## 12. 검증

최종 정량 검증에는 Jang et al. (2011)의 \`95_01\`, \`95_02\`, \`95_03\`, \`95_04\`만 사용하며 총 62개 100년 output-time을 평가한다.

BIOME4 mixed biome의 검증용 reduced classification에서는 가장 강한 활엽수 PFT의 잠재 NPP와 가장 강한 침엽수 PFT의 잠재 NPP를 비교한다. 한쪽 비율이 51% 이상이면 해당 식생군으로 분류하고, 어느 쪽도 51%에 도달하지 않으면 혼효림으로 둔다. 이는 BIOME4 내부 PFT 경쟁식이 아니라 검증용 후처리이다.

각 Jang 검증 시점에서 관측 식생군이 모의 유역 내 유효 격자의 1% 이상에서 출현하면 일치한 것으로 판정한다. 1% 기준은 별도의 모델 수식으로 만들지 않는다.

최종 production 결과는 static 24/62 = 38.71%, dynamic 55/62 = 88.71%이다.

Park et al. (2021)의 holdout, PC2 상관, Herbs 비교는 최종 Methods와 최종 정량검증에서 사용하지 않는다.

## 13. Methods 본문에서 제시할 핵심 수식

본문에서는 다음 원식과 핵심 구현식만 제시한다.

1. McKenzie root-depth 원식 \(f(x)=\exp(-x/X_i)\)과 PB4 2층 water-store 구현
2. Jackson/BIOME4 \(r_{30,p}\)에서 \(X_p\)로 가는 본 연구 변환
3. Pelletier EEMT Eq. (1)-(2)와 PB4 월별 구현
4. Reich SLA-life-span 원식과 \(B_{\mathrm{leaf}}=LAI/SLA\)
5. Haxeltine and Prentice \(C_s=LAI\,C_n\)
6. \(AGB^*=B_{\mathrm{leaf}}+B_{\mathrm{sapwood}}\)
7. Pelletier Eq. (6)-(10), Eq. (14)-(18)
8. 수치구현은 별도 서술하고 Eq. (20)-(22)는 보충자료에 제시

검증의 51% 재분류와 1% 출현 기준은 검증 절에서 문장으로 설명한다.

## 14. 문서 권위순위

1. 이 문서 \`FINAL_METHODS_CANONICAL_20261006_KO.md\`
2. 최종 production package와 \`results/final_integrated_20261006/FINAL_PROVENANCE.json\`
3. AGB 세부근거 \`BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md\`
4. 원문 대조용 \`VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md\`

과거 문서에 이 문서와 다른 변수명, 전개 소수계수, 폐기된 AGB 식 또는 Park 정량검증이 남아 있으면 이 문서를 따른다.

## 15. 핵심 참고문헌

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. Journal of Geophysical Research: Atmospheres, 108(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. Global Biogeochemical Cycles, 10(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. Ecological Monographs, 62(3), 365-392. https://doi.org/10.2307/2937116

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). Estimating water storage capacities in soil at catchment scales. CRC for Catchment Hydrology.

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. Journal of Geophysical Research: Earth Surface, 118, 741-758. https://doi.org/10.1002/jgrf.20046
