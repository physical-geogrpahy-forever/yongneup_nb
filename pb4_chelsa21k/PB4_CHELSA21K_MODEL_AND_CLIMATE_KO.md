# 용늪 PB4Studio CHELSA21K 모델 및 기후자료 설명

업데이트: 2026-10-04


> **연구 범위 명시**
> 이 작업은 대한민국 대암산 용늪을 대상으로 한 **습지생태학, 고생태학, 고기후학, 생물지형학 연구**이다. CHELSA-TraCE21k 기후자료와 BIOME4-Pelletier 결합모형을 사용해 과거 식생, 토심, 수문, 지형의 장기 상호작용을 분석한다. **병원체, 감염성 생물체, 독소, 생물학적 무기, 생화학 무기, 위해성 실험 또는 공격 목적과는 관련이 없다.** GitHub 업로드 역시 이 연구의 재현성, 데이터 보존, 모델 버전 관리를 위한 것이다.

## 1. 목적과 기준

이 디렉터리는 용늪 PB4Studio의 현재 CHELSA-TraCE21k 기후 forcing, 현재 CHELSA21K 모델 계보, 실제 계산 프로세스, 앞으로의 검증 규칙을 함께 보존한다.

과거 Beyer 실행이나 이전 hotfix의 정확도는 현재 CHELSA21K 결과로 재사용하지 않는다. 새 정확도는 반드시 여기 기록한 forcing과 코드로 새로 실행한 뒤 보고한다.

## 2. 현재 기후자료

원자료:

- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 압축본: `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`
- 계열: CHELSA-TraCE21k / EnviCloud
- 위치: 용늪 약 128.122518 E, 38.214643 N
- 기간: 21.0 ka BP에서 0.0 ka BP
- 간격: 0.1 kyr, 즉 100년
- 시점 수: 211
- 크기: 211행 x 39열
- 결측값: 0
- 변수: 시간 필드와 월별 Tmin, Tmax, 강수 원자료

SHA-256:

- CSV: `3f5d249bb59f4163bb0f78f5cb4759972575931bf977b8b2791db497805b0ec9`
- ZIP: `b2e0d8d485c60d3f6bbaae95d88ec175ec1020eab86a7d6976ea66837d18703b`

### 기후 변환 계약

CHELSA raw Tmin/Tmax는 Kelvin이다.

```text
Tmean_C = ((Tmin_K + Tmax_K) / 2) - 273.15
```

CHELSA21K 전용판은 CHELSA 기온에 추가 고도감률 보정을 하지 않으며 `lapse_rate_C_per_m = 0`을 강제한다. CHELSA는 이미 지형 하향화된 자료이기 때문이다.

CHELSA-TraCE21k Centennial 자료에 cloud가 없으므로 BIOME4의 광입력에 필요한 `cloud_pct`만 내장 Beyer cloud 0-21 ka를 보조자료로 선형보간한다. Beyer의 온도와 강수는 사용하지 않는다.

BIOME4 absolute Tmin은 CHELSA에 직접 제공되지 않으므로 원 BIOME4 회귀식

```text
alttmin = 0.006*cold^2 + 1.316*cold - 21.9
```

을 사용한다. CO2는 기존 PB4Studio와 동일하게 내장 Bereiter et al. (2015) 기록을 사용한다.

### 3300 BP 7월 확인

현재 보존 원자료에서 3300 BP와 3200 BP의 7월 값은 서로 다르다.

| 시점 | 7월 Tmin raw | 7월 Tmax raw | 7월 강수 raw |
|---:|---:|---:|---:|
| 3.3 ka BP | 287.0 | 294.5 | 362.0 |
| 3.2 ka BP | 287.0 | 295.9 | 366.0 |

따라서 3300 BP 7월 Tmax는 3200 BP 복제값이 아니다.

## 3. 현재 PB4Studio 패키지

현재 CHELSA 전용 패키지:

- `PB4Studio_v6.6.3_CHELSA21K.zip`
- SHA-256: `bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09`
- ZIP 무결성: `unzip -t` 오류 0
- 기반: PB4Studio v6.6.3, hotfix10n10 계보

같은 날 생성된 과거 forcing 비교용 별도 패키지:

- `PB4Studio_v6.6.3_BEYER120K.zip`

CHELSA 결과와 Beyer 결과를 같은 실행 결과로 취급하지 않는다.

## 4. 실제 BIOME4 backend 구조

현재 코드의 `ScienceConfig.biome4_variant` 기본값은 `mckenzie2003`이다.

과학 실행 경로에서 허용하는 backend는 다음 두 개이다.

- `mckenzie2003`: 현재 production 경로
- `original`: 비교 경로

과거의 `modified`, `muso_rootzone`, `bgc_hybrid`는 현 release의 과학 실행 경로에서 비활성이다.

두 활성 경로 모두 보존된 `fortran_src/biome4_original_4_2b2.f`를 원천 소스로 사용하고, 컴파일 전에 Python backend가 필요한 계측과 선택된 coupling patch를 생성한다.

### 현재 production의 BIOME4 기후제약

과거 CHELSA21K 후보판에는 PFT5/PFT6 climate-sieve 조정이 포함된 시점이 있었으나, 2026-10-05 native-climate ablation 이후 이 조정은 최종 production에서 제거하였다. 현재 `PB4Studio_v6.6.3_CHELSA21K.zip`의 `original`과 `mckenzie2003` 활성 경로는 모두 BIOME4 v4.2b2의 native PFT climate limits를 유지한다. `mckenzie2003` 경로는 기후한계를 수정하지 않고 McKenzie/Jackson soil-water/root coupling만 추가한다.

따라서 아래의 과거 PFT5/PFT6 조정값(`TCM >= -19 C`, `GDD5 >= 900`; `-32.5 <= TCM < -2 C`, `GDD5 >= 600`, `TWM <= 23 C`)은 최종 production 설정으로 사용하지 않는다.

## 5. production `mckenzie2003` 식생-토심 경로

`mckenzie2003`는 원 BIOME4 v4.2b2를 기반으로 다음 coupling을 추가한다.

```text
토심 H
  -> SoilGrids/McKenzie AWC를 실제 토심까지 적분
  -> PFT별 finite-depth root accessibility
  -> BIOME4 2층 토양수분수지
  -> 수분스트레스와 AET
  -> NPP와 LAI
  -> PFT 경쟁과 biome
```

BIOME4 수문층은 다음 범위를 사용한다.

- 상층: 0-0.30 m
- 하층: 0.30-1.50 m
- 유효 토심 상한: 1.50 m

PFT별 유효 뿌리 접근성은 원 BIOME4의 top-30-cm root fraction과 Jackson et al. (1996) 계열 지수분포로부터 계산한다.

중요하게 production 경로에는 화분자료를 맞추기 위한 직접적인

- `NPP *= f(H)`
- `LAI *= f(H)`
- `FVC *= f(H)`

같은 토심 보정계수가 없다.

## 6. hotfix10n10의 PFT 경쟁과 출력 재분류

hotfix10n10은 원 BIOME4에서 PFT1이 비활성인 상태를 유지하며 PFT2-13이 각 기후제약을 통과할 경우 경쟁할 수 있게 복원했다.

검증용 축약 식생군은 다음과 같다.

- 침엽수군: PFT5, PFT6, PFT7
- 활엽수군: PFT2, PFT3, PFT4
- 개방식생군: PFT8-PFT13

원 BIOME4 mixed biome 6/7/9에서는 가장 강한 활엽수 잠재 NPP와 가장 강한 침엽수 잠재 NPP를 비교한다.

- 침엽수 share >= 51%: 침엽수림
- 활엽수 share >= 51%: 활엽수림
- 그 외: 혼효림

이 5분류 축약은 BIOME4 내부 PFT 경쟁 자체가 아니라 **출력/검증용 재분류**임을 구분한다.

## 7. 전체 PB4 계산 프로세스

상태변수:

```text
z(t) = 지표고도
b(t) = 기반암고도
H(t) = z(t) - b(t)
```

한 100년 coupling interval의 흐름은 다음과 같다.

```text
현재 z(t), b(t), H(t)
        |
        v
CHELSA 기후(t)
        |
        v
AWC + PFT별 뿌리 접근성
        |
        v
BIOME4
기후제약 -> PFT별 NPP/LAI -> 경쟁 -> biome
        |
        +--> NPP, AET, LAI, PFT/biome
        |
        v
EEMT + AGB proxy
        |
        v
[dynamic만] Pelletier 지형발달
토양생산/풍화 + 사면수송 + 하천침식 + 융기
        |
        v
z(t+1), b(t+1), H(t+1)
        |
        v
다음 100년 기후시점에서 BIOME4 재실행
```

지형 계산은 수치안정성을 위해 한 100년 구간 내부에서 adaptive substep을 더 잘게 사용할 수 있다. 그 geomorphic substep마다 별도 기후시점을 읽거나 BIOME4를 다시 실행하는 구조는 아니다.

## 8. BIOME4에서 지형으로 가는 피드백

BIOME4 출력의 NPP와 AET를 이용해 EEMT를 계산한다. 지형식에 들어가는 식생량은 더 이상 NPP의 단순 선형 proxy를 사용하지 않고, BIOME4 optimal LAI와 PFT parameter를 이용한 최종 \(AGB^*\)를 사용한다.

잎 건조생체량은 Reich et al. (1992)의 SLA-life-span 회귀식

\[
\log_{10}(SLA)
=
2.44-0.43\log_{10}(\mathrm{life\mbox{-}span})
\]

을 이용한다. BIOME4의 expected leaf longevity \(L_m\)을 적용하면

\[
\boxed{
B_{\mathrm{leaf,dry},p}
=
0.03630780547701014\,LAI_p L_{m,p}^{0.43}
}
\]

가 된다.

변재는 Haxeltine and Prentice (1996) BIOME3 Eq. (34)

\[
C_s=LAI\,C_n
\]

과 BIOME4 v4.2b2 source code의 stemcarbon=0.5를 이용한다. 탄소분율 \(f_C=0.50\)을 명시적 conversion assumption으로 두면 sapwood가 활성인 PFT에서

\[
B_{\mathrm{sapwood,dry},p}=LAI_p
\]

이다. BIOME4 v4.2b2에서 pftpar(pft,10)=2인 PFT는 sapwood term을 0으로 둔다.

따라서 최종 식생량은

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
LAI_p
\left[
S_p
+
0.03630780547701014L_{m,p}^{0.43}
\right]
}
\]

이며, \(S_p=1\) for pftpar(p,10)=1, \(S_p=0\) for pftpar(p,10)=2이다.

Pelletier et al. (2013)의 지형 결합구조는 유지한다.

\[
\boxed{
k_d
=
0.033EEMT
+
0.05AGB^*
}
\]

단, Pelletier Eq. (5)의 직접적인 EEMT-to-AGB 지수식은 용늪에서 사용하지 않는다.

따라서 전체 feedback은 다음과 같이 이해한다.

    H,z
     -> 토양수분과 BIOME4 식생
     -> NPP,AET,LAI,PFT
     -> EEMT, BIOME4-derived AGB*
     -> Pelletier 지형변화
     -> 새 H,z

AGB*는 total anatomical AGB가 아니라 foliage + sapwood를 포함하는 BIOME4-derived aboveground living biomass proxy이다.

최종 수식, PFT별 계수, 참고문헌은 다음 문서를 권위 기준으로 한다.

pb4_chelsa21k/manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md

## 9. static과 dynamic의 차이

### static

```text
CHELSA(t) -> 고정 z,H -> BIOME4(t)
```

DEM, 기반암, 토심을 시간에 따라 갱신하지 않는다.

### dynamic

```text
CHELSA(t)
 -> z(t),H(t)
 -> BIOME4
 -> NPP/AET
 -> EEMT/AGB
 -> Pelletier
 -> z(t+1),H(t+1)
```

따라서 지형과 토심 변화가 다음 시점 식생에 다시 입력된다.

## 10. 앞으로 새로 실행할 공정한 2 x 2 실험

현재 CHELSA21K에서 사용자가 요구한 비교는 다음처럼 정의한다.

| 식생 코어 | 지형 | 기후 |
|---|---|---|
| `native_v4.2b2` 순수 원본 control | static | CHELSA21K |
| `native_v4.2b2` 순수 원본 control | dynamic | CHELSA21K |
| production `mckenzie2003` | static | CHELSA21K |
| production `mckenzie2003` | dynamic | CHELSA21K |

여기서 `native_v4.2b2`는 현재 패키지의 단순 `variant="original"`과 구별한다. 순수 원본 control은 PFT5/PFT6 climate-sieve patch와 hotfix10n10 축약 판정 변경을 원 BIOME4 식생 계산에 섞지 않아야 한다.

네 실행은 동일한 CHELSA 원자료, 공간영역, 초기 DEM/토심, CO2, 시간축을 사용한다.

## 11. 고식생 검증 규칙

### Jang et al. (2011)

기존 범주형 100년 검증에서는 Jang 네 기록만 사용한다.

- `95_01`
- `95_02`
- `95_03`
- `95_04`
- 총 62개 비교시점

Jang 62개와 과거 Park 24개 categorical item을 합친 86개 총점은 현재 최종 검증에 사용하지 않는다.

### Park et al. (2021)

Park는 Supplementary의 실제 화분자료로 별도 평가한다.

- 100년 창 집계
- 보간 없음
- 침엽수, 낙엽활엽수, Trees and Shrubs, Herbs 등 실제 조성변수 사용

## 12. 결과 보고 규칙

앞으로 수치 결과보다 먼저 반드시 다음을 적는다.

1. 사용 데이터와 forcing 파일명/버전
2. 모델/코드 버전과 핵심 설정
3. 이번에 새로 실행한 결과인지 과거 참고값인지
4. 검증 대상, 표본 수, 판정기준

예시:

```text
데이터: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv, 21-0 ka, 100년 간격
모델: PB4Studio_v6.6.3_CHELSA21K, mckenzie2003, dynamic
실행: 이번 분석에서 새로 실행
검증: Jang et al. (2011), n=62 categorical time points
결과: ...
```

## 13. 2026-10-04 4-way 새 실행 완료

CHELSA21K 기준 4개 실험을 실제 새 실행했다.

- 순수 BIOME4 v4.2b2 control, static
- 순수 BIOME4 v4.2b2 control, dynamic
- production mckenzie2003, static
- production mckenzie2003, dynamic

코드 감사에서 기존 `variant="original"`에도 hotfix10n10의 PFT5/PFT6 climate-sieve 수정이 들어가는 문제가 확인되었다. 이번 원본 대조군에서는 해당 수정과 51% mixed 재분류를 제거했고, 원본 BIOME4의 native PFT 기후한계와 native mixed biome identity를 유지했다.

동적 실행은 21-0 ka 전체를 0.1 kyr 간격으로 수행했다. 실행시간 제한 때문에 exact restart chunk를 사용했지만, 연속 실행과 분할 실행의 `z`, `b`, `H` 최종 배열이 `array_equal=True`, 최대 절대차 0.0임을 회귀검증했다.

Jang et al. (2011)의 원문 식생대와 기존 PB4 축약 라벨이 일부 불일치한다는 기존 감사 결과를 반영해, 원문 서술에 맞춘 reduced class를 주 검증으로 사용한다. 주 기준은 프로젝트의 **1% 유역 출현 기준**이며 총 62개 record x 100년 output-time 평가항목이다.

| BIOME4 | 지형 | Jang 원문 기준 1% 정확도 |
|---|---|---:|
| 원본 v4.2b2 | static | 19/62 = 30.65% |
| 원본 v4.2b2 | dynamic | 19/62 = 30.65% |
| hotfix10n10 수정형 | static | 24/62 = 38.71% |
| hotfix10n10 수정형 | dynamic | 55/62 = 88.71% |

사용자가 지정한 주 기준인 1%에서는 수정형 dynamic이 **55/62 = 88.71%**로 가장 높다. 5%와 10%에서 23/62 = 37.10%로 낮아지는 값은 임계값 민감도 분석으로 별도 보존한다.

상세 결과, 임계값 민감도, Jang 분류 교정, 실행 provenance, 원본-control 패치는 다음 경로에 보존한다.

- `results/fourway_20261004/PB4_CHELSA21K_FOURWAY_RESULTS_KO.md`
- `results/fourway_20261004/PRIMARY_JANG2011_1PCT_FOURWAY.csv`
- `results/fourway_20261004/FOURWAY_JANG_ACCURACY_1_5_10PCT.csv`
- `results/fourway_20261004/FOURWAY_JANG_ZONE_BREAKDOWN.csv`
- `results/fourway_20261004/JANG2011_CORRECTED_REDUCED_MAPPING.csv`
- `results/fourway_20261004/EXECUTION_PROVENANCE.json`
- `results/fourway_20261004/TRUE_ORIGINAL_AND_EXACT_RESTART.patch`

Park et al. (2021)은 이 62개 categorical 총점에 포함하지 않고 Supplementary 실측 화분자료로 별도 평가한다.


## 14. Native-climate ablation, 2026-10-05

PB4-McKenzie의 토심별 AWC, PFT별 finite-depth roots, 51% 과반 reduced-class 판정, dynamic Pelletier coupling을 유지한 채 PFT5/PFT6 기후제약만 BIOME4 v4.2b2 원본값으로 복원해 21-0 ka 전체를 새로 실행했다.

Jang 원문 식생대, n=62, 유역 1% 출현 기준 결과는 tunedClimate 판과 동일했다.

- static 24/62 = 38.71%
- dynamic 55/62 = 88.71%

따라서 현재 증거에서는 PFT5/PFT6 기후제약 튜닝이 성능에 기여하지 않는다. 향후 production candidate는 원본 BIOME4 PFT 기후제약을 유지하고 McKenzie/Jackson soil-root-water coupling과 51% 과반 판정을 유지하는 구성이 우선이다.


## 14. 2026-10-05 최종 production 결정: native BIOME4 climate limits

PFT5/PFT6 기후제약 보정만 제거하고 CHELSA21K 21-0 ka 전체를 새로 실행했다. McKenzie AWC, PFT별 finite-depth root accessibility, 51% 과반 reduced-class 규칙, dynamic Pelletier coupling은 그대로 유지했다.

Jang et al. (2011) 원문 식생대, n=62, 유역 1% 기준에서 결과는 이전 tunedClimate와 완전히 동일했다.

- static: **24/62 = 38.71%**
- dynamic: **55/62 = 88.71%**
- dynamic 95_03: **31/31**
- 95_03 broadleaf fraction: 약 **1.3423-3.3557%**

따라서 PFT5/PFT6 기후튜닝은 정확도 향상에 불필요하다고 판정하고 최종 production 모델에서 제거했다. 최종 모델은 **PB4-McKenzie-nativeClimate**이며, BIOME4 v4.2b2의 원래 PFT 기후 niche를 유지하면서 통합 모델에 필요한 토심-AWC-뿌리-지형 coupling만 추가한다.

최종 canonical ZIP SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

상세 자료: `results/native_climate_final_20261005/`

## 15. 2026-10-06 폐기된 실험 후보: U009 post-fire state memory

U009에서는 native fire event 다음 0.1 kyr 시점에 PFT8 상태를 한 번 유지하는 실험을 검토하였다.
그러나 최종 모델에서는 이 상태기억을 사용하지 않는다. 이유는 BIOME4의 0.1 kyr 출력 간격에서
각 시점의 기후와 토양조건에 따른 원래 평형경쟁을 그대로 유지하는 편이 가정이 더 적기 때문이다.

U009는 감사와 민감도 기록으로만 보존한다.

## 16. 2026-10-06 최종 production 결정: BIOME4 native fire U008

최종 산불 처리는 BIOME4 v4.2b2의 원래 fire 계산과 competition 규칙을 그대로 사용한다.

```text
CHELSA(t), H(t)
 -> BIOME4 soil-water balance
 -> native PFT-specific firedays
 -> native competition2 fire rules
 -> equilibrium PFT/biome at t
 -> NPP, LAI, AET
 -> AGB*, EEMT
 -> [dynamic] Pelletier
 -> H(t+1), z(t+1)
 -> 다음 0.1 kyr에서 다시 독립 BIOME4 경쟁
```

추가적인 post-fire PFT8 유지시간, Park/Jang 연대 기반 fire event, fire threshold 재보정,
결과에 맞춘 기후 보정은 적용하지 않는다.

FIREACTIVE U008에서 추가된 부분은 firedays 진단 출력뿐이며 과학식은 변경하지 않는다.
따라서 기존 production 검증값은 그대로 유지한다.

- static Jang 1%: **24/62 = 38.71%**
- dynamic Jang 1%: **55/62 = 88.71%**

최종 native-fire 실행 ZIP SHA-256:
`578923dee512278a64f97d914acc9b1f67af7d13007a099bb2931b17b5e6a49c`

상세 결정:
`results/final_native_fire_u008_20261006/FINAL_NATIVE_FIRE_U008_DECISION_KO.md`
