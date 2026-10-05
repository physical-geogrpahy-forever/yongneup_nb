# VeSLEM / PB4 논문용 수식 원전 대조 및 HWP 입력 가이드

작성 기준: 2026-10-05

## 0. 사용 원칙

이 문서는 다음 세 자료를 기준으로 수식을 대조한다.

1. Pelletier et al. (2013), *Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect*.
2. McKenzie, Gallant, & Gregory (2003), *Estimating Water Storage Capacities in Soil at Catchment Scales*.
3. 2026 한국지형학회 VeSLEM 발표자료는 식의 조합 방식과 논문 서술 순서를 확인하기 위한 참고자료로만 사용한다.

중요: `원문식`과 `현재 PB4 구현식`은 구분한다. Pelletier 또는 McKenzie에 없는 결합식을 해당 논문의 원식인 것처럼 인용하지 않는다.

**식생 코어 고정 원칙:** 본 연구는 BIOME4 v4.2b2를 사용한다. BIOME3는 최종 모델의 수식, 파라미터 또는 AGB bridge 근거로 사용하지 않는다.

한/글 수식 편집기는 스크립트 입력에서 `OVER`, `SUM`, `INT`, `PARTIAL`, 위첨자 `^`, 아래첨자 `_` 등을 사용할 수 있다. 아래의 `HWP 입력`은 한/글 수식 편집기 하단 스크립트 입력창에 붙여넣는 것을 전제로 작성하였다.

---

# I. 논문 본문에 권장하는 최종 수식 체계

## 1. EEMT

### 1.1 Pelletier et al. (2013) 원식

유효 에너지 및 물질 전달량(EEMT)은 유효강수 에너지와 생물생산 에너지의 합으로 정의한다.

**원문 Eq. (1)**

\[
E_{PPT}=\Delta T\,C_w P_{eff}
\]

HWP 입력:

```text
E_{PPT}=Delta T C_w P_{eff}
```

**원문 Eq. (2)**

\[
E_{BIO}=NPP\,h_{BIO}
\]

HWP 입력:

```text
E_{BIO}=NPP h_{BIO}
```

따라서 개념적으로

\[
EEMT=E_{PPT}+E_{BIO}
\]

HWP 입력:

```text
EEMT=E_{PPT}+E_{BIO}
```

여기서 Pelletier 원문의 \(P_{eff}=PPT-ET\)이며, \(h_{BIO}=22\times10^6\,\mathrm{J\,kg^{-1}}\)이다.

### 1.2 현재 PB4에서 실제 계산하는 월별 형태

현재 PB4는 BIOME4의 월별 AET와 기후입력을 이용하여 Pelletier Eq. (1)-(2)를 다음처럼 계산한다.

\[
EEMT=
\frac{C_w}{10^6}\sum_{m=1}^{12}T_m(P_m-AET_m)
+
\frac{h_{BIO}}{10^6}
\frac{\max(NPP_C,0)}{1000f_C}
\]

현재 코드에서 \(C_w=4186\,\mathrm{J\,kg^{-1}\,K^{-1}}\), \(h_{BIO}=22\times10^6\,\mathrm{J\,kg^{-1}}\), \(f_C=0.50\)이다. \(NPP_C\)는 BIOME4가 출력하는 탄소 기준 NPP(gC m⁻² yr⁻¹)이므로, dry biomass로 변환하기 위한 \(f_C\)가 들어간다.

HWP 입력:

```text
EEMT={C_w OVER 10^6} SUM _{m=1}^{12} T_m (P_m-AET_m)+{h_{BIO} OVER 10^6}{max(NPP_C,0) OVER {1000 f_C}}
```

**논문 주의:** 발표자료의 EEMT 식은 `NPP/1000`만 사용하지만, 현재 PB4 코드는 `NPP/(1000 f_C)`를 사용한다. 따라서 현재 모델을 기술할 논문에서는 위 식을 쓰는 것이 정확하다. \(f_C=0.5\)의 출처 또는 모델 가정을 별도로 명시해야 한다.

---

## 2. 토양 수분보유능: McKenzie 개념 + PB4/BIOME4 층 구조

### 2.1 McKenzie 원개념

Profile available water capacity는 토양 프로파일 깊이에 걸쳐 \(-10\) kPa와 \(-1.5\) MPa에서의 체적수분함량 차이를 적분한 값이다.

\[
AWC_{profile}(H)=1000\int_0^H
\left[\theta_{-10}(\xi)-\theta_{-1500}(\xi)\right]d\xi
\]

HWP 입력:

```text
AWC_{profile}(H)=1000 INT _0^H [theta_{-10}(xi)-theta_{-1500}(xi)] d xi
```

### 2.2 현재 PB4의 BIOME4 2층 적분식

현재 PB4는 BIOME4의 native hydraulic depth인 0-0.30 m와 0.30-1.50 m를 유지한다.

\[
WHC(H,T)=WHC_{top}(H,T)+WHC_{bottom}(H,T)
\]

\[
WHC_{top}=1000\int_0^{\min(H,0.30)}
\left[\theta_{-10}(\xi,T)-\theta_{-1500}(\xi,T)\right]d\xi
\]

\[
WHC_{bottom}=1000\int_{0.30}^{\min(\max(H,0.30),1.50)}
\left[\theta_{-10}(\xi,T)-\theta_{-1500}(\xi,T)\right]d\xi
\]

HWP 입력:

```text
WHC(H,T)=WHC_{top}(H,T)+WHC_{bottom}(H,T)
```

```text
WHC_{top}(H,T)=1000 INT _0^{min(H,0.30)} [theta_{-10}(xi,T)-theta_{-1500}(xi,T)] d xi
```

```text
WHC_{bottom}(H,T)=1000 INT _{0.30}^{min(max(H,0.30),1.50)} [theta_{-10}(xi,T)-theta_{-1500}(xi,T)] d xi
```

이 식은 McKenzie가 제시한 profile AWC 정의를 SoilGrids 수분특성에 적용하고, BIOME4의 native 2층 수문구조에 맞춘 **PB4 결합식**이다. McKenzie 보고서 자체의 원식이라고 쓰면 안 된다.

---

## 3. 뿌리 접근성

### 3.1 McKenzie 원식

McKenzie 보고서의 깊이에 따른 root-density scaling은

\[
f(x)=\exp\left(-\frac{x}{X_i}\right)
\]

이다. \(X_i\)는 그 깊이보다 아래에 37%의 뿌리가 존재하는 특성깊이이다.

HWP 입력:

```text
f(x)=exp(-{x OVER X_i})
```

McKenzie의 A horizon과 B horizon plant-available storage 원식은 다음과 같다.

\[
A_{Total}=AAWC\,X_i\left(1-e^{-d_A/X_i}\right)
\]

\[
B_{Total}=BAWC\,X_i\left(e^{-d_A/X_i}-e^{-d_i/X_i}\right)
\]

HWP 입력:

```text
A_{Total}=AAWC X_i (1-exp(-{d_A OVER X_i}))
```

```text
B_{Total}=BAWC X_i (exp(-{d_A OVER X_i})-exp(-{d_i OVER X_i}))
```

### 3.2 현재 PB4의 PFT별 finite-depth root coupling

PB4는 BIOME4의 PFT별 상부 30 cm 뿌리비율 \(r_{30,p}\)을 사용하여 McKenzie 지수형식의 특성깊이를 분석적으로 구한다.

\[
X_p=-\frac{0.30}{\ln(1-r_{30,p})}
\]

HWP 입력:

```text
X_p=-{0.30 OVER ln(1-r_{30,p})}
```

유효 수문 깊이:

\[
D=\min[\max(H,0),1.50]
\]

HWP 입력:

```text
D=min(max(H,0),1.50)
```

상층 접근 뿌리비율:

\[
R_{top,p}=1-\exp\left[-\frac{\min(D,0.30)}{X_p}\right]
\]

HWP 입력:

```text
R_{top,p}=1-exp(-{min(D,0.30) OVER X_p})
```

하층 접근 뿌리비율:

\[
R_{bottom,p}=
\begin{cases}
0, & D\le0.30,\\
\exp(-0.30/X_p)-\exp(-D/X_p), & D>0.30.
\end{cases}
\]

HWP 입력:

```text
R_{bottom,p}=CASES{0 & D<=0.30 # exp(-{0.30 OVER X_p})-exp(-{D OVER X_p}) & D>0.30}
```

BIOME4 root-zone wetness는

\[
w_r=R_{top,p}w_{top}+R_{bottom,p}w_{bottom}
\]

HWP 입력:

```text
w_r=R_{top,p} w_{top}+R_{bottom,p} w_{bottom}
```

으로 계산한다.

**출처 구분:** 지수형 root scaling은 McKenzie, \(r_{30,p}\)은 BIOME4/Jackson, \(X_p=-0.30/\ln(1-r_{30,p})\)은 둘을 연결하기 위한 분석적 변환이다. McKenzie (2003)가 BIOME4용으로 직접 제시한 식이 아니다.

---

# II. Pelletier et al. (2013) 원문 수식 전체와 HWP 입력

아래는 원문 번호를 그대로 유지한다. 논문에서 사용 여부도 병기한다.

## Eq. (1): 유효강수 에너지

\[
E_{PPT}=\Delta T C_w P_{eff}
\]

```text
E_{PPT}=Delta T C_w P_{eff}
```

**PB4:** 사용. 월별 합으로 계산.

## Eq. (2): 생물생산 에너지

\[
E_{BIO}=NPP\,h_{BIO}
\]

```text
E_{BIO}=NPP h_{BIO}
```

**PB4:** 사용하되 BIOME4 carbon NPP를 dry biomass로 변환.

## Eq. (3): Pelletier 논문의 월별 EEMT 회귀식

\[
\begin{aligned}
EEMT_m={}&-3.13+0.00879(T+273.15)+0.562P\\
&+0.0326(T-17.65)(P-9.0)\\
&-0.00235VPD+0.00062(P-9.0)(VPD-662)
\end{aligned}
\]

```text
EEMT_m=-3.13+0.00879(T+273.15)+0.562P+0.0326(T-17.65)(P-9.0)-0.00235VPD+0.00062(P-9.0)(VPD-662)
```

**PB4:** 사용하지 않음. 현재 PB4는 Eq. (1)-(2)를 BIOME4의 AET/NPP로 직접 계산한다.

## Eq. (4): lidar MCH에서 AGB 추정

\[
AGB=aMCH^b
\]

```text
AGB=a MCH^b
```

**PB4:** 사용하지 않음.

## Eq. (5): EEMT-AGB 관계

\[
AGB=e\exp(fEEMT)
\]

```text
AGB=e exp(f EEMT)
```

**PB4:** 현재 사용하지 않음. 현재 코드는 `AGB = s_AGB max(NPP_C,0)` 프록시를 사용하므로 논문에서 Pelletier Eq. (5)를 썼다고 쓰면 틀림.

## Eq. (6): 지표고도, 기반암고도, 토심 관계

\[
z=b+h
\]

```text
z=b+h
```

**PB4:** 사용.

## Eq. (7): 기반암/풍화전선 고도 변화

\[
\frac{\partial b}{\partial t}=U-\frac{P}{\cos\theta}
\]

```text
{PARTIAL b OVER PARTIAL t}=U-{P OVER cos theta}
```

**PB4:** 기본 구조 사용. 실제 구현에서는 유수에 의한 기반암 침식항도 별도로 차감한다.

## Eq. (8): 토심 변화

\[
\frac{\partial h}{\partial t}
=\frac{\rho_b}{\rho_s}\frac{P}{\cos\theta}-E
\]

```text
{PARTIAL h OVER PARTIAL t}={rho_b OVER rho_s}{P OVER cos theta}-E
```

**PB4:** 핵심 질량수지 구조.

## Eq. (9): 토심 의존 토양생산

\[
P=P_0\exp\left(-\frac{h\cos\theta}{h_0}\right)
\]

```text
P=P_0 exp(-{h cos theta OVER h_0})
```

**PB4:** 사용.

## Eq. (10): EEMT 의존 잠재 토양생산율

\[
P_0=a\exp(bEEMT)
\]

```text
P_0=a exp(b EEMT)
```

**PB4:** 사용. 기본값 \(a=0.037\), \(b=0.03\)은 Pelletier Table 1 계열.

## Eq. (11): 사면물질수송에 따른 침식/퇴적

\[
E_c=\nabla\cdot\mathbf q
\]

```text
E_c=∇ BULLET q
```

**PB4:** 질량수지에서 사용.

## Eq. (12): 선형 사면확산

\[
\mathbf q=-k\nabla z
\]

```text
q=-k ∇z
```

**PB4:** 직접 사용하지 않고 Eq. (14)의 비선형, 토심의존식을 사용.

## Eq. (13): 비선형 사면수송

\[
\mathbf q=-\frac{k\nabla z}{1-(|\nabla z|/S_c)^2}
\]

```text
q=-{k ∇z OVER {1-({|∇z| OVER S_c})^2}}
```

**PB4:** 중간 원형. 최종은 Eq. (14).

## Eq. (14): 토심의존 비선형 사면수송

\[
\mathbf q=-\frac{k_d h\cos\theta\,\nabla z}
{1-(|\nabla z|/S_c)^2}
\]

```text
q=-{k_d h cos theta ∇z OVER {1-({|∇z| OVER S_c})^2}}
```

**PB4:** 사용. 수치구현에서는 face-average \(k_d\), \(h\)와 공급제약을 적용한다.

## Eq. (15): EEMT와 AGB에 따른 사면수송계수

\[
k_d=c\,EEMT+d\,AGB
\]

```text
k_d=c EEMT+d AGB
```

**PB4:** 사용. \(c=0.033\), \(d=0.05\)를 기본값으로 유지.

## Eq. (16): slope-wash/fluvial erosion

\[
E_f=K\frac{A}{w}|\nabla z|
\]

```text
E_f=K {A OVER w}|∇z|
```

**PB4:** 사용. 실제 계산에서는 flow-direction slope \(S_f\)를 사용하고 가용토심으로 regolith removal을 제한한다.

## Eq. (17): 유로폭

\[
w=gA^i
\]

```text
w=g A^i
```

**PB4:** 사용. 다만 hillslope/valley의 \(A/w\) 판정에는 Pelletier (2010)의 격자의존성 분류가 추가된다.

## Eq. (18): EEMT 의존 유수침식계수

\[
K=\frac{K_0}{EEMT}
\]

```text
K={K_0 OVER EEMT}
```

**PB4:** 사용.

## Eq. (19): 토양생산의 Euler update

\[
h_{i,j}(t+\Delta t)
=h_{i,j}(t)
+\Delta t\frac{\rho_b}{\rho_s}\frac{P_0}{\cos\theta}
\exp\left[-\frac{h(t)\cos\theta}{h_0}\right]
\]

```text
h_{i,j}(t+Delta t)=h_{i,j}(t)+Delta t {rho_b OVER rho_s}{P_0 OVER cos theta} exp(-{h(t) cos theta OVER h_0})
```

**PB4:** 동일 질량수지 원리를 사용.

## Eq. (20): x 방향 face flux

\[
q_{x,i+1/2,j}=-k_d
\frac{\frac12(h_{i+1,j}+h_{i,j})
\left(\frac{z_{i+1,j}-z_{i,j}}{\Delta x}\right)}
{1-\left[\frac{z_{i+1,j}-z_{i,j}}{\Delta x S_c}\right]^2}
\]

```text
q_{x,i+1/2,j}=-k_d {{1 OVER 2}(h_{i+1,j}+h_{i,j}){(z_{i+1,j}-z_{i,j}) OVER Delta x} OVER {1-({z_{i+1,j}-z_{i,j} OVER {Delta x S_c}})^2}}
```

## Eq. (21): y 방향 face flux

\[
q_{y,i,j+1/2}=-k_d
\frac{\frac12(h_{i,j+1}+h_{i,j})
\left(\frac{z_{i,j+1}-z_{i,j}}{\Delta x}\right)}
{1-\left[\frac{z_{i,j+1}-z_{i,j}}{\Delta x S_c}\right]^2}
\]

```text
q_{y,i,j+1/2}=-k_d {{1 OVER 2}(h_{i,j+1}+h_{i,j}){(z_{i,j+1}-z_{i,j}) OVER Delta x} OVER {1-({z_{i,j+1}-z_{i,j} OVER {Delta x S_c}})^2}}
```

## Eq. (22): FTCS 질량보존

\[
\begin{aligned}
h_{i,j}(t+\Delta t)=h_{i,j}(t)
&-\frac{\Delta t}{\Delta x}
(q_{x,i+1/2,j}-q_{x,i-1/2,j})\\
&-\frac{\Delta t}{\Delta x}
(q_{y,i,j+1/2}-q_{y,i,j-1/2}).
\end{aligned}
\]

```text
h_{i,j}(t+Delta t)=h_{i,j}(t)-{Delta t OVER Delta x}(q_{x,i+1/2,j}-q_{x,i-1/2,j})-{Delta t OVER Delta x}(q_{y,i,j+1/2}-q_{y,i,j-1/2})
```

**PB4:** 이 finite-volume/explicit 구조를 따르되, 초임계경사 처리, donor supply positivity constraint, adaptive timestep, open fixed-base-level boundary가 추가된다.

---

# III. 현재 PB4의 지형발달식을 논문에 한 식으로 제시할 경우

발표자료의 결합식은 Pelletier Eqs. (8)-(18)을 하나의 토심 방정식으로 묶은 것이다. 현재 PB4 구조를 설명하는 개념식으로는 다음이 가장 적절하다.

\[
\frac{\partial H}{\partial t}
=
\frac{\rho_r}{\rho_s\cos\theta}
\left[a\exp(b_E EEMT)\right]
\exp\left(-\frac{H\cos\theta}{H_0}\right)
+
\nabla\cdot
\left[
\frac{(c_EEEMT+c_AAGB)H\nabla z}
{1-(|\nabla z|/S_c)^2}
\right]
-
E_{f,reg}
\]

여기서 PB4의 regolith fluvial erosion은

\[
E_{f,pot}=\frac{K_0}{EEMT}\frac{A}{w}S_f
\]

\[
E_{f,reg}=\min\left(E_{f,pot},\frac{H_{avail}}{\Delta t}\right)
\]

로 공급제약을 적용한다.

HWP 입력:

```text
{PARTIAL H OVER PARTIAL t}={rho_r OVER {rho_s cos theta}}[a exp(b_E EEMT)]exp(-{H cos theta OVER H_0})+∇ BULLET [{(c_E EEMT+c_A AGB)H ∇z OVER {1-({|∇z| OVER S_c})^2}}]-E_{f,reg}
```

```text
E_{f,pot}={K_0 OVER EEMT}{A OVER w}S_f
```

```text
E_{f,reg}=min(E_{f,pot},{H_{avail} OVER Delta t})
```

**중요:** `min(H_avail/Δt)` 공급제약과 Pelletier (2010) 기반의 \(A/w\) 분류는 Pelletier et al. (2013) 원문 Eq. (16) 자체가 아니라 PB4 수치구현의 확장이다. 논문에는 “following Pelletier et al. (2013), with a finite regolith-supply constraint”와 같이 구분해서 써야 한다.

---

# IV. AGB 항: 최신 원문 및 코드 감사

Pelletier et al. (2013)의 수치모델은 Eq. (5)

\[
AGB=e\exp(fEEMT)
\]

을 사용한다.

현재 PB4 production은 BIOME4가 total standing AGB를 직접 prognose하지 않기 때문에

\[
AGB=s_{AGB}\max(NPP_C,0),\qquad s_{AGB}=0.010
\]

을 coupling proxy로 사용한다. 이 식은 Pelletier 원식이 아니며 현재 provenance 재검토 대상이다.

## IV-1. BIOME4-only 원칙

BIOME3 계보는 검토했지만 최종 방법론에서 제외한다. AGB 문제는 BIOME4 v4.2b2의 실제 source와 BIOME4 문헌만으로 해결한다. BIOME3의 biomass 식과 파라미터는 본 연구의 후보식으로 사용하지 않는다.

## IV-2. BIOME4 v4.2b2 source의 실제 값

원본 BIOME4 v4.2b2 `respiration()`은

```fortran
parameter(Ln=50.,y=0.8,m10=1.6,p1=0.25,stemcarbon=0.5)
```

를 사용하며 `stemcarbon`을 sapwood mass per leaf area로 정의한다.

따라서 BIOME4 내부의 sapwood-carbon diagnostic은 사실상

\[
\boxed{C_{sap}=0.5\,LAI}
\]

이다.

PFT4-7은 `allocfact=1.2`이므로 leaf litterfall/minimum allocation은

\[
L_f=60\,LAI
\quad [{\rm g\ C\ m^{-2}\ yr^{-1}}]
\]

이다.

**중요:** (C_{sap}=0.5LAI)는 total AGB가 아니라 sapwood carbon이다. 이를 그대로 “BIOME4 AGB”라고 부르면 안 된다.

현재 해결해야 할 문제:

1. BIOME4 v4.2b2의 `stemcarbon=0.5`에 대한 BIOME4 문헌적 근거
2. BIOME4를 사용해 total AGB 또는 vegetation carbon을 추정한 선행연구
3. sapwood carbon에서 total aboveground biomass로 연결할 수 있는 BIOME4 계열의 공식 또는 allometry
4. dry biomass 변환에 사용하는 (f_C)의 문헌 근거

이 검토가 끝나기 전에는 production AGB식을 변경하지 않는다. 새 AGB식을 채택하면 CHELSA 21-0 ka 전체 dynamic을 새로 실행하고 Jang n=62, 1% 기준을 재검증해야 한다.


## IV-3. Xue/IBIS 원문 수식과 용늪 equilibrium AGB bridge

### IV-3.1 원문 보유 및 출처 구분

Xue 계열에서 현재 직접 확인한 자료는 두 종류이다.

1. **Xue et al. (2017), Ecological Modelling 최종 출판본**
   - *Evaluation of modeled global vegetation carbon dynamics: Analysis based on global carbon flux and above-ground biomass data*
   - *Ecological Modelling* 355:84-96, doi:10.1016/j.ecolmodel.2017.04.012
   - 최종 PDF를 직접 대조하여 Eq. (1)-(4), Table 1, AGB calibration/validation 표본수, carbon-density-to-AGB 변환을 확인했다.
   - 2016 Biogeosciences Discussions preprint는 역사적 선행본으로만 남기고, 수식과 parameter의 주 출처는 최종 출판본으로 한다.

2. **Xue et al. (2017), Global Biogeochemical Cycles**
   - *Global patterns of woody residence time and its influence on model simulation of aboveground biomass*
   - DOI: 10.1002/2016GB005557
   - 이 PDF는 현재 프로젝트 라이브러리에 실제 보존되어 있다.
   - woody residence time의 관측 정의와 IBIS carbon-pool 식을 원문에서 직접 확인했다.

아래에서는 **Xue 원문식**, **Xue Table 1 parameter**, **PB4에서 유도한 equilibrium 식**을 구분한다.

### IV-3.2 Xue et al. (2017, Ecological Modelling) 원문 Eq. (1): stomatal conductance

\[
g_{s,H_2O}=m\frac{A_n h_s}{C_s}+b
\]

여기서 \(A_n\)은 잎 수준 순광합성률, \(h_s\)는 잎 표면 상대습도, \(C_s\)는 잎 표면 CO2 농도, \(m,b\)는 경험계수이다.

HWP 입력:

    g_{s,H_2O}=m {A_n h_s OVER C_s}+b

**PB4 AGB bridge:** 직접 사용하지 않음. IBIS의 전체 생리구조를 기록하기 위해 원문식으로 보존한다.

### IV-3.3 Xue et al. (2017, Ecological Modelling) 원문 Eq. (2): NPP

\[
NPP=(1-\eta)\int(A_g-R_{leaf}-R_{stem}-R_{root})dt
\]

여기서 \(A_g\)는 gross canopy production이다. 최종 출판본은 \(\eta\)를 **“fraction of carbon lost by maintenance respiration”**이라고 표현하며 0.3으로 고정한다. \(R_{leaf}\), \(R_{stem}\), \(R_{root}\)는 각각 잎, 줄기, 뿌리 호흡이다. 같은 식에서 조직별 respiration을 별도로 차감하므로, 본 문서는 저자의 용어를 그대로 기록하며 \(\eta\)를 별도의 growth-respiration parameter로 재해석하지 않는다.

HWP 입력:

    NPP=(1-eta) INT (A_g-R_{leaf}-R_{stem}-R_{root}) dt

**PB4 AGB bridge:** 이 IBIS NPP 계산식 자체를 가져오지 않는다. PB4는 BIOME4가 직접 계산한 \(NPP_i\)를 입력으로 사용한다.

### IV-3.4 Xue et al. (2017, Ecological Modelling) 원문 Eq. (3): PFT별 biomass pool 질량수지

본 연구의 AGB bridge에 가장 중요한 Xue 원식이다.

\[
\boxed{
\frac{\partial C_{i,j}}{\partial t}
=
a_{i,j}NPP_i
-
\frac{C_{i,j}}{\tau_{i,j}}
}
\]

여기서 \(C_{i,j}\)는 PFT \(i\)의 biomass pool \(j\)의 carbon stock, \(a_{i,j}\)는 annual NPP allocation fraction, \(\tau_{i,j}\)는 carbon residence time이다. 원문은 annual NPP를 leaf, stem, root의 세 carbon pool에 배분한다고 명시한다.

HWP 입력:

    {PARTIAL C_{i,j} OVER PARTIAL t}=a_{i,j} NPP_i-{C_{i,j} OVER tau_{i,j}}

### IV-3.5 Xue et al. (2017, Ecological Modelling) 원문 Eq. (4): growing season index

\[
GSI=f(\overline{T_m})f(\overline{R_g})f(\overline{VPD})
\]

HWP 입력:

    GSI=f(bar{T_m}) f(bar{R_g}) f(bar{VPD})

여기서 \(\overline{T_m}\), \(\overline{R_g}\), \(\overline{VPD}\)는 multi-day running mean air temperature, solar radiation, vapor pressure deficit이다.

**PB4 AGB bridge:** 사용하지 않음. BIOME4 phenology를 유지한다.

### IV-3.6 Xue et al. (2017, Ecological Modelling) Table 1: IBIS PFT별 carbon-pool parameter

AGB bridge에 직접 필요한 열은 \(\tau_l,\tau_r,\tau_w,a_{leaf},a_{root},a_{wood}\)이다.

| IBIS PFT | 식생형 | \(\tau_l\) yr | \(\tau_r\) yr | \(\tau_w\) yr | \(a_{leaf}\) | \(a_{root}\) | \(a_{wood}\) |
|---:|---|---:|---:|---:|---:|---:|---:|
|1|tropical broadleaf evergreen tree|1.01|1|60|0.30|0.30|0.40|
|2|tropical broadleaf drought-deciduous tree|1|1|60|0.30|0.30|0.40|
|3|warm-temperate broadleaf evergreen tree|1|1|25|0.30|0.30|0.40|
|4|temperate conifer evergreen tree|2|1|35|0.30|0.40|0.30|
|5|temperate broadleaf cold-deciduous tree|1|1|35|0.30|0.30|0.40|
|6|boreal conifer evergreen tree|2.5|1|52|0.30|0.40|0.30|
|7|boreal broadleaf cold-deciduous tree|1|1|52|0.30|0.30|0.40|
|8|boreal conifer cold-deciduous tree|1|1|52|0.30|0.30|0.40|
|9|evergreen shrub|1.5|1|5|0.45|0.40|0.15|
|10|cold-deciduous shrub|1|1|5|0.45|0.35|0.20|
|11|warm C4 grass|1.25|1|wood pool 없음|0.45|0.55|0|
|12|cool C3 grass|1.5|1|wood pool 없음|0.45|0.55|0|

**중요:** 35 yr와 52 yr는 최종 Xue et al. (2017) Table 1의 **calibrated PFT parameter set**이다. 저자들은 대부분의 parameter에는 Foley et al. (1996)과 Kucharik et al. (2000)의 default를 사용하되, GPP와 AGB에 민감한 parameter를 Table 1처럼 보정했다고 명시한다. 따라서 35/52 yr를 “IBIS 보편 기본값”이라고 쓰지 않는다. 별도 Xue et al. (2017, GBC)의 model-comparison Table 2는 Kucharik et al. (2000)의 IBIS default woody residence time을 warm-temperate 25 yr, temperate 50 yr, boreal 100 yr로 요약한다.

### IV-3.7 Xue et al. (2017, Ecological Modelling)의 carbon density -> dry AGB 변환

최종 출판본은 IBIS가 \(Mg\ C\ ha^{-1}\) 단위의 carbon density를 계산하기 때문에 관측 AGB와 비교할 때 IPCC (2003)에 따라 2.0을 곱했다고 명시한다.

\[
\boxed{AGB_{dry}=2C_{AG}}
\]

HWP 입력:

    AGB_{dry}=2 C_{AG}

**정의 주의:** Eq. (3)의 IBIS vegetation state에는 leaf, stem/wood, root pool이 모두 존재한다. 따라서 이 문장의 ×2만으로 total vegetation carbon 전체를 AGB로 바꿀 수 있다고 해석하지 않는다. PB4에서는 먼저 Xue의 AGB diagnostic과 대응되는 지상부 후보 pool을 선택한 뒤, ×2를 carbon mass -> dry biomass mass 변환으로만 사용한다. 0.48 또는 0.51 같은 별도 carbon fraction을 다시 적용하면 이중변환이다.

**IBIS wood-pool 구조 주의:** Xue 최종 논문은 세 pool을 leaves, stems (for trees), roots로 서술하고 GBC 논문은 woody residence time을 stems and branches에 대응시킨다. 그러나 다른 IBIS 구현 문헌에는 generic woody pool에 coarse roots가 포함된다는 설명도 있다. 따라서 아래 leaf + wood 평형식은 **Xue/IBIS AGB diagnostic의 재현을 위한 평형축약**으로 사용하며, 모든 IBIS version에서 해부학적으로 순수한 aboveground pool임이 입증된 식이라고 표현하지 않는다.

### IV-3.7a 최종본 AGB calibration 표본수와 검증 지위

최종 *Ecological Modelling* 논문은 plot-level AGB 자료를 필터링한 뒤 **992 samples를 calibration, 982 samples를 independent validation**에 사용했다고 명시한다. 합계 1,974 plot samples이며, 이전 작업기록의 “2,101 plots” 표현은 최종 출판본 기준으로 사용하지 않는다.

또한 저자들은 Table 1의 민감 parameter를 GPP와 AGB 관측에 맞춰 trial-and-error로 보정했다고 설명한다. 따라서 Table 1의 35/52 yr와 allocation coefficient는 단순 이론값보다 강한 **AGB-tested calibrated parameterization**이지만, 한 PFT 내 공간적으로 불변인 single parameter set이라는 한계가 있고 저자 스스로 이를 AGB spatial bias의 원인으로 지적한다.

### IV-3.8 Xue et al. (2017, GBC) 원문 Eq. (1): woody residence time 관측 정의

보유 중인 Xue et al. (2017) GBC 원문은 near-equilibrium forest에서

\[
\boxed{\tau_w=\frac{M_w}{W_p}}
\]

로 정의한다.

여기서 \(M_w\)는 mean AGB \((Mg\ ha^{-1})\), \(W_p\)는 mean aboveground woody productivity, stem + branch \((Mg\ ha^{-1}\ yr^{-1})\)이다.

HWP 입력:

    tau_w={M_w OVER W_p}

원문은 주요 교란이 최소 100년 이상 없고 mature 또는 old-growth로 판단된 forest plot을 중심으로 \(\tau_w\)를 구축했다.

### IV-3.9 Xue et al. (2017, GBC) 원문 Eq. (2): IBIS carbon pool

\[
\boxed{
\frac{\partial C_{i,j}}{\partial t}
=
a_{i,j}NPP_i
-
\frac{C_{i,j}}{\tau_{i,j}}
}
\]

HWP 입력:

    {PARTIAL C_{i,j} OVER PARTIAL t}=a_{i,j} NPP_i-{C_{i,j} OVER tau_{i,j}}

stem 및 branch carbon pool에 대해서는 \(\tau_{i,j}=\tau_w\)이다.

### IV-3.10 PB4에서 사용하는 equilibrium 해: 원문식에서의 분석적 유도

다음은 Xue 논문의 별도 번호식이 아니라 위 원문 mass-balance 식에 BIOME4의 equilibrium 조건을 적용한 유도식이다.

\[
\frac{\partial C_{i,j}}{\partial t}=0
\]

이므로

\[
\boxed{C_{i,j}=a_{i,j}\tau_{i,j}NPP_i}
\]

HWP 입력:

    C_{i,j}=a_{i,j} tau_{i,j} NPP_i

Xue 최종 논문의 AGB calibration 구조를 재현하기 위한 **Xue-style aboveground diagnostic**은 leaf + wood candidate로 두어

\[
\boxed{
AGB_{C,i}
=
NPP_i
(a_{leaf,i}\tau_{leaf,i}+a_{wood,i}\tau_{wood,i})
}
\]

HWP 입력:

    AGB_{C,i}=NPP_i (a_{leaf,i} tau_{leaf,i}+a_{wood,i} tau_{wood,i})

BIOME4 NPP가 \(g\ C\ m^{-2}\ yr^{-1}\)이고 Xue가 AGB 비교에 사용한 dry-biomass 변환 2.0을 적용하면

\[
\boxed{
AGB_{dry,i}
=
\frac{2}{1000}
NPP_i
(a_{leaf,i}\tau_{leaf,i}+a_{wood,i}\tau_{wood,i})
}
\]

HWP 입력:

    AGB_{dry,i}={2 OVER 1000} NPP_i (a_{leaf,i} tau_{leaf,i}+a_{wood,i} tau_{wood,i})

### IV-3.11 용늪에서 실제 출현한 BIOME4 PFT의 대응식

canonical 21-0 ka full coverage audit에서 실제 dominant PFT는 4, 6, 7, 10이며 PFT5는 0회였다.

**BIOME4 PFT4 -> IBIS PFT5**

\[
0.30(1)+0.40(35)=14.30
\]

\[
\boxed{AGB_{dry}=0.0286NPP}
\]

**BIOME4 PFT6 -> IBIS PFT6**

\[
0.30(2.5)+0.30(52)=16.35
\]

\[
\boxed{AGB_{dry}=0.0327NPP}
\]

**BIOME4 PFT7 -> IBIS PFT7 또는 PFT8**

두 IBIS PFT는 AGB 관련 parameter가 동일하다.

\[
0.30(1)+0.40(52)=21.10
\]

\[
\boxed{AGB_{dry}=0.0422NPP}
\]

**BIOME4 PFT10 -> IBIS PFT9 evergreen-shrub analogue**

\[
0.45(1.5)+0.15(5)=1.425
\]

\[
AGB_{dry}=0.00285NPP
\]

PFT10은 구조적 analogue이며 전체 21 ka 기여가 매우 작으므로 별도 불확실성으로 표시한다.

### IV-3.12 PFT5 처리

BIOME4 PFT5는 canonical 21-0 ka에서 static과 dynamic 모두 0/211 timestep, 0 dominant cell-observation이었다. 따라서 PFT5 coefficient는 본 용늪 연구의 과학적 근거에서 제외한다. 향후 forcing 또는 모델 버전 변경으로 PFT5가 실제 dominant로 나타나면 자동 대응하지 않고 별도 검토한다.

### IV-3.13 논문에서 권장하는 서술

권장:

> BIOME4는 standing AGB pool을 직접 예측하지 않으므로, BIOME4가 계산한 PFT별 NPP를 Xue et al.의 IBIS carbon-pool allocation and residence-time formulation에 연결하였다. Xue의 biomass-pool mass-balance equation을 BIOME4의 equilibrium potential-vegetation 상태에 적용하여 \(C_{i,j}=a_{i,j}\tau_{i,j}NPP_i\)의 평형해를 사용하고, leaf와 wood pool을 합산하여 aboveground carbon을 구한 뒤 Xue et al.이 사용한 carbon-to-dry-biomass factor 2.0으로 변환하였다.

피해야 할 서술:

> “BIOME4가 Xue 식으로 AGB를 직접 계산한다.”

> “0.0286, 0.0327, 0.0422는 BIOME4 고유계수이다.”

이들은 cross-model equilibrium bridge의 유도계수이다.

### IV-3.14 Xue 원문 링크

- Xue et al. (2017) Ecological Modelling final article: https://doi.org/10.1016/j.ecolmodel.2017.04.012
- 2016 Biogeosciences Discussions preprint (historical version): https://bg.copernicus.org/preprints/bg-2016-142/bg-2016-142.pdf
- Xue et al. (2017) Global Biogeochemical Cycles: https://doi.org/10.1002/2016GB005557


# V. McKenzie 원문과 현재 PB4의 관계를 논문에 쓰는 방식

권장 서술:

> 토심에 따른 토양 수분저장량은 McKenzie et al. (2003)의 profile available water capacity 정의에 따라, \(-10\) kPa와 \(-1500\) kPa에서의 체적수분함량 차이를 토심까지 적분하여 계산하였다. BIOME4의 기존 2층 수문구조를 유지하기 위해 적분 구간은 0-0.30 m와 0.30-1.50 m로 구분하였다. 뿌리 접근성은 McKenzie et al. (2003)의 지수형 깊이 가중함수와 BIOME4의 PFT별 상부 30 cm 뿌리분율을 결합하여 산정하였다.

피해야 할 서술:

> “McKenzie et al. (2003)의 BIOME4 토심모형을 사용하였다.”

McKenzie 보고서는 BIOME4 확장을 제안한 문헌이 아니므로 이 표현은 틀리다.

---

# VI. 변수 정의 표

| 기호 | 의미 | 대표 단위 | 출처/상태 |
|---|---|---|---|
| \(z\) | 지표고도 | m | Pelletier Eq. 6 |
| \(b\) | 기반암/풍화전선 고도 | m | Pelletier Eq. 6-7 |
| \(H,h\) | 토심/레골리스 두께 | m | Pelletier Eq. 6-9 |
| \(U\) | 융기율 | m kyr⁻¹ | Pelletier Eq. 7, 용늪에서는 별도 지역값 |
| \(P\) | 기반암 풍화/후퇴율 | m kyr⁻¹ | Pelletier Eq. 9 |
| \(P_0\) | 잠재 풍화율 | m kyr⁻¹ | Pelletier Eq. 10 |
| \(H_0,h_0\) | 풍화 특성깊이 | m | Pelletier Eq. 9 |
| \(\rho_r/\rho_s\) | 기반암/레골리스 밀도비 | - | Pelletier Table 1 |
| EEMT | 유효 에너지 및 물질 전달량 | MJ m⁻² yr⁻¹ | Pelletier Eq. 1-3 |
| AGB | 지상부 생물량 | kg m⁻² | Pelletier Eq. 4-5, PB4에서는 NPP proxy |
| \(k_d\) | 토심의존 사면수송계수 | m kyr⁻¹ | Pelletier Eq. 15 |
| \(S_c\) | 임계경사 | - | Pelletier Eq. 13-14, PB4 지역 설정값 별도 |
| \(E_f\) | 유수침식률 | m kyr⁻¹ | Pelletier Eq. 16 |
| \(K\) | 유수침식계수 | kyr⁻¹ | Pelletier Eq. 16, 18 |
| \(K_0\) | EEMT-유수침식 기준계수 | m² MJ⁻¹ | Pelletier Eq. 18 |
| \(A\) | 기여면적 | m² | Pelletier Eq. 16-17 |
| \(w\) | 유효 유로폭 | m | Pelletier Eq. 16-17 |
| \(S_f\) | 유로방향 경사 | - | PB4 Eq.16 구현 |
| \(\theta_{-10}\) | -10 kPa 체적수분함량 | m³ m⁻³ | McKenzie/SoilGrids |
| \(\theta_{-1500}\) | -1500 kPa 체적수분함량 | m³ m⁻³ | McKenzie/SoilGrids |
| \(X_i\) | root scaling 특성깊이 | m | McKenzie p.13 |
| \(r_{30,p}\) | PFT p의 상부 30 cm 누적 뿌리분율 | - | BIOME4/Jackson |
| \(R_{top,p},R_{bottom,p}\) | 실제 토심에서 접근 가능한 PFT별 뿌리비율 | - | PB4 coupling |

---

# VII. 원문 파라미터와 용늪 모델을 혼동하지 말아야 할 항목

Pelletier et al. (2013) Table 1은 원 연구지역의 수치모델에 대해 \(S_c=0.7\), \(U=0.05\,m\,kyr^{-1}\) 등을 사용한다. 용늪 VeSLEM/PB4에서는 지역 설정과 수치 안정성 검증을 통해 다른 값을 사용할 수 있으므로, **수식은 원문을 따르더라도 파라미터 값까지 원문과 동일하다고 쓰면 안 된다.**

반대로 현재 모델에서 원문 기본값을 유지하는 주요 계수는 \(a=0.037\), \(b=0.03\), \(c=0.033\), \(d=0.05\), \(h_0=0.5\), \(K_0=0.02\), \(g=0.005\), \(i=0.5\), \(F=10\), \(\rho_b/\rho_s=1.8\) 계열이다. 실제 제출 논문에서는 최종 실행 configuration을 다시 읽어 최종 숫자를 고정해야 한다.

---

# VIII. 논문 Methods에서 실제로 제시할 수식의 최소 세트

본문이 너무 길어지는 것을 피하려면 다음 8개 묶음을 본문에 제시하고, Pelletier Eq. (19)-(22)는 보충자료로 보내는 구성이 가장 자연스럽다.

1. EEMT: Pelletier Eq. (1)-(2)를 월별 합산한 현재 PB4 식
2. Profile AWC/WHC: McKenzie 정의 + BIOME4 2층 적분식
3. PFT별 finite-depth root accessibility
4. \(z=b+H\), 기반암/토심 질량수지
5. \(P=P_0e^{-H\cos\theta/H_0}\), \(P_0=ae^{bEEMT}\)
6. \(q=-k_dH\cos\theta\nabla z/[1-(|\nabla z|/S_c)^2]\), \(k_d=cEEMT+dAGB\)
7. \(E_f=(K_0/EEMT)(A/w)S_f\), \(w=gA^i\)
8. 실제 가용토심을 넘지 않는 fluvial supply constraint

---

# IX. 참고문헌 표기

Pelletier, J. D., Barron-Gafford, G. A., Breshears, D. D., Brooks, P. D., Chorover, J., Durcik, M., Harman, C. J., Huxman, T. E., Lohse, K. A., Lybrand, R., Meixner, T., McIntosh, J. C., Papuga, S. A., Rasmussen, C., Schaap, M., Swetnam, T. L., & Troch, P. A. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*(2), 741-758. https://doi.org/10.1002/jgrf.20046

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales* (Technical Report 03/3). Cooperative Research Centre for Catchment Hydrology.


Xue, B.-L., Guo, Q., Hu, T., Wang, G., Wang, Y., Tao, S., Su, Y., Liu, J., & Zhao, X. (2017). Evaluation of modeled global vegetation carbon dynamics: Analysis based on global carbon flux and above-ground biomass data. *Ecological Modelling, 355*, 84-96. https://doi.org/10.1016/j.ecolmodel.2017.04.012

Xue, B.-L., Guo, Q., Hu, T., Xiao, J., Yang, Y., Wang, G., Tao, S., Su, Y., Liu, J., & Zhao, X. (2017). Global patterns of woody residence time and its influence on model simulation of aboveground biomass. *Global Biogeochemical Cycles, 31*, 821-835. https://doi.org/10.1002/2016GB005557


---

# X. 최종 체크리스트

- Pelletier Eq. (1)-(22)와 현재 PB4 식을 동일시하지 않는다.
- EEMT 회귀식 Eq. (3)은 현재 PB4에서 사용하지 않는다.
- Pelletier Eq. (5) AGB-EEMT식도 현재 PB4에서 사용하지 않는다.
- 현재 PB4의 `NPP -> AGB` 프록시는 별도 가정으로 명시한다.
- McKenzie의 root scaling과 PB4/Jackson 기반 PFT별 root-depth 변환을 구분한다.
- PPT Eq. (2)의 NPP 생물량 변환은 현재 코드의 carbon fraction 0.5를 반영해 수정한다.
- PPT Eq. (3)의 WHC 식은 원문 McKenzie 식이 아니라 PB4/BIOME4 결합식으로 표기한다.
- Pelletier Table 1의 원 연구지역 파라미터와 용늪 최종 configuration을 구분한다.
- 최종 제출 전에는 `PB4-McKenzie-nativeClimate` 최종 ZIP의 configuration에서 U, Sc, 시간간격, 격자크기 등을 다시 고정한다.