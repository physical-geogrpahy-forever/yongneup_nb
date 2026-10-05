# 용늪 PB4 최종 Methods 작성 가이드

갱신일: 2026-10-06  
상태: **현재 논문 Methods 작성용 구조 가이드**

실제 본문 초안은 다음 파일을 사용한다.

\`FINAL_METHODS_MANUSCRIPT_DRAFT_20261006_KO.md\`

수식과 변수의 최종 권위 기준은 다음 파일이다.

\`FINAL_METHODS_CANONICAL_20261006_KO.md\`

이 문서는 과거 방법론 스냅샷을 대체하며, 이후 Methods 작성에서는 아래 원칙만 따른다.

## 1. 기본 작성 원칙

문헌에서 가져온 과정식은 구조를 유지하되 논문 전체의 상태변수는 통일한다. Pelletier et al. (2013)의 \(h\), 기반암고도 \(b\), 시간 \(t\)는 각각 \(H\), \(z_b\), \(\tau\)로 표기한다. 반면 Pelletier의 토양생산 경험계수 \(b\), 사면수송계수 \(k_d\), 유수침식계수 \(K\) 등 과정계수는 원래 기호를 유지한다.

각 과정식은 서로 대입하여 하나의 통합식으로 만들지 않는다. 특히 다음 관계는 반드시 분리한다.

\[
P
=
P_0
\exp
\left(
-\frac{H\cos\theta}{H_0}
\right)
\]

\[
P_0
=
a\exp(b\,EEMT)
\]

\[
\mathbf q
=
-
\frac{k_dH\cos\theta\nabla z}
{1-(|\nabla z|/S_c)^2}
\]

\[
k_d
=
c\,EEMT+d\,AGB^*
\]

\[
E_f
=
K\frac{A}{w}|\nabla z|
\]

\[
w=gA^i
\]

\[
K=\frac{K_0}{EEMT}
\]

따라서 \(P_0\)를 \(P\) 안에 대입하거나, \(k_d\)를 \(\mathbf q\) 안에 대입하거나, \(K\)와 \(w\)를 \(E_f\) 안에 대입하지 않는다.

## 2. Methods 본문 순서

최종 본문은 다음 순서로 작성한다.

1. 모형 구성과 시간 결합
2. 기후자료와 BIOME4 입력
3. 토심, available-water storage 및 뿌리 접근성
4. EEMT
5. BIOME4-derived AGB*
6. Pelletier 지형발달모형
7. 수치 적분과 coupling
8. Jang et al. (2011) 검증
9. 재현성

Park et al. (2021)은 최종 정량검증에 포함하지 않는다.

## 3. 토심과 수문 coupling

토심은

\[
H=z-z_b
\]

로 통일한다.

McKenzie et al. (2003)에서 직접 가져오는 핵심 관계는 available water를 \(\theta_{-10}-\theta_{-1500}\)로 정의하는 개념과 지수형 root-density function

\[
f(x)=\exp(-x/X_i)
\]

이다.

BIOME4의 0-0.30 m와 0.30-1.50 m 수문층에 적용하는 water-store 적분식은 본 연구 구현식으로 기술한다.

BIOME4의 상부 30 cm 누적 뿌리분율 \(r_{30,p}\)과 McKenzie의 지수형 뿌리분포를 연결하는

\[
X_p
=
-\frac{0.30}{\ln(1-r_{30,p})}
\]

역시 본 연구의 분석적 변환으로 기술한다.

## 4. EEMT

Pelletier et al. (2013)의 원 관계

\[
E_{\mathrm{PPT}}
=
\Delta T C_wP_{\mathrm{eff}}
\]

\[
E_{\mathrm{BIO}}
=
NPP\,h_{\mathrm{BIO}}
\]

를 먼저 제시한다.

그 다음 BIOME4의 월 AET와 탄소 NPP에 적용한 월별 합산식을 본 연구 구현식으로 제시한다. 두 단계를 섞어 Pelletier 원식이라고 표현하지 않는다.

## 5. AGB*

잎 부분은 Reich et al. (1992)의 원식

\[
\log_{10}(SLA_p)
=
2.44
-
0.43\log_{10}(L_{m,p})
\]

과

\[
B_{\mathrm{leaf,dry},p}
=
\frac{LAI_p}{SLA_p}
\]

를 사용한다.

변재 부분은 Haxeltine and Prentice (1996)의

\[
C_s=LAI\,C_n
\]

을 사용하고 BIOME4 v4.2b2 source의 \`stemcarbon=0.5\`를 실제 구현 parameter로 적용한다.

최종 정의는

\[
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
\]

로 둔다.

\`0.0363078055...\`와 같은 대수 전개 소수계수나 PFT별 \(AGB^*/LAI\) 파생계수는 본문 수식에 제시하지 않는다.

## 6. Pelletier 지형발달

상태변수와 과정식은 다음처럼 분리한다.

\[
z=z_b+H
\]

\[
\frac{\partial z_b}{\partial\tau}
=
U-\frac{P}{\cos\theta}
\]

\[
\frac{\partial H}{\partial\tau}
=
\frac{\rho_b}{\rho_s}
\frac{P}{\cos\theta}
-E
\]

이후 토양생산, 사면수송, 유수침식의 식을 각각 독립적으로 설명한다.

production에서 Pelletier와 동일하게 유지되는 주요 값은 \(a=0.037\), \(b=0.030\), \(H_0=0.50\) m, \(\rho_b/\rho_s=1.8\), \(c=0.033\), \(d=0.050\), \(K_0=0.020\)이다.

\(S_c=1.50\)은 용늪 20 m real DEM의 수치수렴시험을 통해 채택한 용늪 production 설정으로 기술한다.

현재 \(U=0.20\ {\rm m\,kyr^{-1}}\)의 지역 문헌 근거는 별도 확인이 필요하다. 해당 값은 Pelletier 원 연구값으로 기술하지 않는다.

## 7. 수치구현

100년 coupling interval과 geomorphic adaptive substep을 구분한다.

각 100년 시점에서 BIOME4를 한 번 실행하고, 그 결과로 계산된 EEMT와 \(AGB^*\)를 해당 interval 내부의 지형 substep 동안 고정 forcing으로 사용한다.

0.025 m trial-rejection threshold는 물리 파라미터가 아니라 수치수렴시험에서 정한 tolerance로 기술한다.

finite-volume donor-supply constraint, threshold-slope adjustment, fixed base-level outlet도 Pelletier 원 과정식과 구분하여 PB4의 수치구현으로 서술한다.

## 8. 검증

최종 검증은 Jang et al. (2011)만 사용한다.

사용 record는 \`95_01\`, \`95_02\`, \`95_03\`, \`95_04\`이며 총 62개 100년 output-time을 평가한다.

51% 기준은 mixed biome의 reduced-class 후처리 기준으로 문장으로 설명한다.

1% 기준은 각 시점에서 관측 식생군이 유역 내 유효 격자의 1% 이상에서 출현하면 일치로 판정한다는 방식으로 문장으로 설명한다. 별도의 수식으로 만들지 않는다.

## 9. 재현성 표기

Methods 또는 Supplementary에서 반드시 다음을 명시한다.

- climate file: \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\`
- vegetation core: BIOME4 v4.2b2
- model: \`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB\`
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- number of time slices: 211
- final package SHA-256: \`a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34\`
- validation: Jang et al. (2011), \(n=62\)

## 10. 문체

한국어를 우선한다. NPP, LAI, AET, EEMT, AGB, PFT 등 일반적인 학술 약어는 그대로 사용한다. 가운뎃점은 사용하지 않는다.

Methods에서는 결과 해석을 섞지 않는다. static 24/62와 dynamic 55/62 같은 검증결과는 결과절 또는 Methods의 재현성 확인 문장에서만 최소한으로 언급하고, AGB 시계열 평균이나 0 ka biomass 값은 Results로 보낸다.

과거 후보식인 \`AGB=0.010 x NPP\`, Xue/IBIS, JULES, Pelletier Eq. (5)의 직접 EEMT-to-AGB 식은 최종 본문 방법론에서 장황하게 설명하지 않고 필요하면 Supplementary의 모델선정 과정에 둔다.
