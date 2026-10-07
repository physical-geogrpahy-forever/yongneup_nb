# 용늪 PB4 최종 Methods 원문 및 코드 출처 감사

작성일: 2026-10-06  
상태: **추가 검토 계속**  
대상 문서: \`FINAL_METHODS_MANUSCRIPT_DRAFT_20261006_KO.md\`  
목적: 논문 Methods의 각 식, 계수, 결합규칙이 원문, BIOME4 source code, PB4 production implementation 중 어디에서 유래하는지 분리하여 기록한다.

## 1. 판정 기준

| 판정 | 의미 |
|---|---|
| 원문 직접 | 해당 수식 또는 파라미터를 원 논문에서 직접 확인 |
| source 직접 | BIOME4 또는 PB4 source code에서 직접 확인 |
| 본 연구 구현 | 여러 문헌 또는 source 구조를 연결하기 위해 본 연구에서 정의 |
| 본 연구 가정 | 문헌 원 파라미터가 아니라 연구 설계상 명시적으로 채택 |
| 수치설정 | 물리 파라미터가 아니라 raster 적분 안정성 또는 수렴을 위해 채택 |
| 추가 확인 | 제출 전 원문 또는 최종 canonical archive의 세부사항을 한 번 더 대조할 항목 |

## 2. 기후 forcing

| 항목 | 원문 및 자료 근거 | production 구현 | 판정 |
|---|---|---|---|
| CHELSA-TraCE21k | Karger et al. (2023), *Climate of the Past* 19:439-456. LGM 이후 월별 기온 및 강수, 1 km 하향화 자료 | \`YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv\` | 원문 직접 + source 직접 |
| 월평균기온 | 입력 Tmin/Tmax를 이용한 산술평균 | \(T_m=(T_{\min,m}+T_{\max,m})/2-273.15\) | 본 연구 자료변환 |
| 추가 lapse correction | CHELSA 입력은 이미 downscaled forcing | \`lapse_rate_C_per_m=0\`, \`tmin_lapse_rate_C_per_m=0\` | source 직접 |
| cloudiness | Beyer et al. (2020), *Scientific Data* 7:236. 후기 제4기 월별 cloudiness 포함 | \`AUX_BEYER_CLOUD_0_21KA.csv\`를 month별 선형보간. Beyer T/P는 미사용 | 원문 직접 + source 직접 |
| CO2 | Bereiter et al. (2015), GRL 42:542-549, revised Antarctic composite | package의 NOAA/NCEI \`antarctica2015co2composite-noaa.txt\`를 model age에 직접 선형보간 | 원문 직접 + source 직접 |
| BIOME4 absolute Tmin | BIOME4 v4.2b2 source regression | \(T_{\rm absmin}=0.006T_{\rm cold}^2+1.316T_{\rm cold}-21.9\) | source 직접 |

기후 source 확인 파일:

\`pb4_chelsa21k/results/herbaceous_cause_20261006/source_snapshot/climate.py\`

## 3. BIOME4

| 항목 | 근거 | 판정 |
|---|---|---|
| 식생모형 | Kaplan (2001)의 BIOME4 개발 논문집/학위논문 및 BIOME4 v4.2b2 source | 원문 직접 + source 직접 |
| 입력 | 월별 기온, 강수, cloudiness, absolute Tmin, CO2, 토양수문조건 | source 직접 |
| PFT 수 | v4.2b2 source에 13 parameterized PFT가 정의되지만 PFT1 tropical evergreen은 `pfts(1)=0`으로 비활성화되어 실제 경쟁에는 12 active PFT가 참여 | source 직접 |
| PFT별 NPP 및 optimal LAI | BIOME4/BIOME3 계열 생리 및 경쟁구조 | 원문 직접 + source 직접 |
| native climate limits | 최종 production에서 v4.2b2 native limits 유지 | source/provenance 직접 |
| temperate grass photosynthetic pathway | Kaplan (2001)의 표는 temperate grass를 C3/C4 잠재형으로 설명하지만 사용한 v4.2b2 source의 active branch는 `if (pft.eq.9.or.pft.eq.10) c4=.true.`이고 PFT8은 C3 branch로 실행 | source 직접 |

| 토심별 NPP 또는 LAI 직접 multiplier | 사용하지 않음 | source 직접 |

BIOME4 source 확인 파일:

\`pb4_chelsa21k/results/herbaceous_cause_20261006/source_snapshot/biome4_original_4_2b2.f\`

## 3.1 공간 입력자료 및 계산격자 감사

과거 기술보고서의 공간 전처리 기록과 현재 production의 20 m real-DEM 설정을 대조하였다.

| 항목 | 확인 내용 | 판정 |
|---|---|---|
| 원 고도자료 | 국토정보플랫폼 수치지형도 | project 입력 |
| DEM 생성 | QGIS 3.44.5 IDW로 10 m 연속 고도면 생성 | project 전처리 기록 직접 |
| 유역 추출 | GRASS GIS r.watershed로 용늪 포함 소유역 추출 | project 전처리 기록 직접 |
| 최종 좌표계 | Korea 2000/Central Belt 2010, EPSG:5187 | project 전처리 기록 직접 |
| 최종 계산격자 | 모든 공간자료를 20 m로 리샘플링 | project 전처리 기록 직접 + production 20 m 설정과 일치 |
| 경계조건 | 단일 유출구만 open, 나머지 유역 경계 closed | project 전처리 기록 직접 |
| D8 처리 | 유출구 외 경계로의 flow receiver 금지, 계산 전 sink filling | project 전처리 기록 직접 |
| 사면수송 경계 | final mask 내부 인접 셀 사이에서만 계산, closed boundary flux=0 | project 전처리 기록 직접 |

따라서 Methods에서는 “DEM을 10 m로 보간하였다”와 “모델 해상도는 20 m이다”를 충돌하는 문장으로 쓰지 않고, **10 m IDW 보간 후 모든 공간입력을 20 m 계산격자로 리샘플링하였다**고 단계적으로 기술한다.

## 4. 토심과 available-water storage

McKenzie et al. (2003), Technical Report 03/3은 profile available water capacity를 field capacity와 wilting point에 대응하는 \(-10\) kPa와 \(-1.5\) MPa의 체적수분함량 차이로 설명하고, plant available water를 계산할 때 root distribution을 별도로 고려한다.

| 식 또는 입력 | 출처 | 판정 |
|---|---|---|
| \(AWC=\theta_{-10}-\theta_{-1500}\) | McKenzie et al. (2003), profile available water capacity 정의 | 원문 직접 |
| \(W_{\rm top}(H)\) 적분식 | McKenzie의 AWC 개념 + BIOME4 0-0.30 m layer | 본 연구 구현 |
| \(W_{\rm bottom}(H)\) 적분식 | McKenzie의 AWC 개념 + BIOME4 0.30-1.50 m layer | 본 연구 구현 |
| 1.50 m cap | BIOME4 native hydraulic profile | source 직접 |
| 용늪 water-density profile 237, 232, 218, 207, 198, 179 mm m\(^{-1}\) | production source 주석상 SoilGrids Explore에서 128.1236 E, 38.2153 N에 대해 확보한 \(\theta_{-10}-\theta_{-1500}\) profile. SoilGrids의 wv0010 및 wv1500 정의와 6개 표준 깊이구간은 Turek et al. (2023) 및 ISRIC layer documentation과 일치 | project 입력 + source 직접 + 원문 직접 |
| AWC profile 생성 방식 | 위 SoilGrids 수분함량 차이를 깊이구간별로 직접 적분. coarse-fragment correction, PTF, calibration, pollen-fit coefficient 없음 | source 직접 |
| texture class | supplied texture raster의 모든 유효셀은 BIOME4 texture class 2. McKenzie profile 적용 전 source에서 이를 검사 | source 직접 |
| texture의 역할 | McKenzie production에서는 native BIOME4 hydraulic conductivity 선택에 사용. AWC 저장량 자체는 위 SoilGrids 수분 profile에서 계산 | source 직접 |
| BDRICM_M_1km_ll | ISRIC former/2017-03-10/aggregated/1km archive에 파일명이 그대로 존재. SoilGrids250m의 depth-to-bedrock 예측은 Hengl et al. (2017), 세부 DTB 모델은 Shangguan et al. (2017) | 자료 archive 직접 + 원문 직접 |
| SoilGrids water retention | wv0010=10 kPa, wv1500=1500 kPa. Turek et al. (2023)의 global volumetric water-retention mapping | 자료 정의 + 원문 직접 |
| SoilGrids 2.0 일반 자료체계 | Poggio et al. (2021) | 보조 일반근거 |

주의: Poggio et al. (2021)이 용늪의 특정 \(\theta_{-10}\), \(\theta_{-1500}\) 수치를 논문에서 직접 제시한 것으로 쓰지 않는다. 또한 현재 production의 237-179 mm m\(^{-1}\) 값은 sand/silt/clay에서 본 연구가 PTF로 재계산한 값이 아니다.

## 5. 뿌리분포와 finite-depth accessibility

Gale and Grigal (1987)은 누적 뿌리분율을

\[
Y(d)=1-\beta^d
\]

로 제시하였다. Jackson et al. (1996)은 이 함수를 전지구 생물군계의 root distribution에 적용하였다.

BIOME4 v4.2b2 source에서 \`pftpar(pft,6)\`은 PFT-specific root parameter로 사용되며 output에서 root percent로 기록된다.

| 식 | 출처 | 판정 |
|---|---|---|
| \(Y(d)=1-\beta^d\) | Gale & Grigal (1987), Jackson et al. (1996) | 원문 직접 |
| McKenzie root-depth exponential scaling | McKenzie et al. (2003), plant available water scaling | 원문 직접 |
| \(X_p=-0.30/\ln(1-r_{30,p})\) | BIOME4 \(r_{30,p}\)와 exponential profile의 analytical matching | 본 연구 구현 |
| \(D=\min[\max(H,0),1.50]\) | BIOME4 hydraulic depth 제한 | 본 연구 구현 |
| \(R_{\rm top,p}\), \(R_{\rm bottom,p}\) | exponential profile을 BIOME4 2층에 적분 | 본 연구 구현 |
| \(\omega_{r,p}=R_{\rm top,p}\omega_{\rm top}+R_{\rm bottom,p}\omega_{\rm bottom}\) | production hydrology adapter | 본 연구 구현 |
| shallow soil에서 root fraction 미재정규화 | production code | source 직접 |

## 6. EEMT

Pelletier et al. (2013)의 EEMT 원 구조:

\[
E_{\rm PPT}=\Delta T C_wP_{\rm eff}
\]

\[
E_{\rm BIO}=NPP\,h_{\rm BIO}
\]

\[
EEMT=E_{\rm PPT}+E_{\rm BIO}
\]

| 항목 | 근거 | 판정 |
|---|---|---|
| \(C_w=4186\) J kg\(^{-1}\) K\(^{-1}\) | Pelletier et al. (2013) | 원문 직접 |
| \(h_{\rm BIO}=22\times10^6\) J kg\(^{-1}\) | Pelletier et al. (2013) | 원문 직접 |
| 월별 \(\sum T_m(R_m-AET_m)\) | Pelletier 원 구조를 BIOME4 monthly AET에 적용 | 본 연구 구현 |
| \(NPP_C/(1000f_C)\) | BIOME4 carbon NPP를 dry biomass로 변환 | 본 연구 구현 |
| \(f_C=0.50\) | study-wide carbon fraction | 본 연구 가정 |
| \(P_{\rm eff}\) zero clipping 없음 | production code | source 직접 |
| EEMT 1-80 clipping 없음 | production code | source 직접 |

## 7. BIOME4-derived AGB*

### 7.1 foliage

Reich et al. (1992), Table 1의 전체 LEAVES regression:

\[
\log_{10}(SLA)
=
2.44-0.43\log_{10}(L_m)
\]

원문에서 leaf life-span은 month, SLA는 cm\(^2\) g\(^{-1}\)이다.

\[
B_{\rm leaf,dry}
=
\frac{LAI}{SLA}
\]

는 SLA와 LAI의 정의에 따른 질량변환이다.

판정: Reich regression은 **원문 직접**, \(LAI/SLA\) 변환은 **정의에 따른 구현**.

### 7.2 sapwood

Haxeltine and Prentice (1996)의 publisher PDF를 직접 시각 확인하였다. **Eq. (34)는 정확히 \(C_s=LAI\,C_n\)이다.** 원문에서 \(C_s\)는 total sapwood carbon content(kg C m^-2), \(C_n\)은 sapwood carbon content per unit LAI이며, BIOME3에서는 여러 자료를 종합하여 \(C_n=1\ {\rm kg\ C\ m^{-2}}\)를 사용한다.

따라서 Haxeltine and Prentice (1996)에서 가져오는 것은 Eq. (34)의 구조이며, 본 연구의 실제 계수 0.5는 해당 논문에서 가져온 값이 아니다.

\[
C_s=LAI\,C_n
\]

BIOME4 v4.2b2 source에서는

\`stemcarbon=0.5\`

이며 source comment는 이를 sapwood mass in kg C per unit leaf area per unit ground area로 정의한다. 또한 \`pftpar(pft,10)\`은 sapwood respiration의 적용 여부를 제어한다.

| 항목 | 판정 |
|---|---|
| \(C_s=LAI C_n\) | 문헌식, 제출 전 publisher PDF에서 Eq. 34 번호와 기호를 마지막으로 시각 대조할 것 |
| \`stemcarbon=0.5\` | BIOME4 source 직접 |
| \`pftpar(pft,10)\`에 따른 sapwood term on/off | BIOME4 source 직접 |
| \(B_{\rm sapwood,dry}=C_{\rm sapwood}/f_C\) | 본 연구 dry-mass conversion |
| \(f_C=0.50\) | 본 연구 가정 |

### 7.3 cell-level AGB*

Production patch는 각 셀의 \`optpft_node\`와 \`lai_node\`를 읽어 dominant PFT \(p^*\)에 대해 계산한다.

\[
AGB^*
=
B_{\rm leaf,dry,p^*}
+
B_{\rm sapwood,dry,p^*}
\]

따라서 all-PFT 합산이 아니다.

확인 파일:

\`pb4_chelsa21k/results/reich_lai_sapwood_agb_candidate_20261005/REICH_LAI_SAPWOOD_AGB.patch\`

논문에는 \`0.0363078055...\` 또는 PFT별 \(AGB^*/LAI\) 파생 소수계수를 쓰지 않는다.

## 8. Pelletier soil production

Pelletier et al. (2013)의 과정식은 서로 분리한다.

\[
P
=
P_0
\exp\left(-\frac{H\cos\theta}{H_0}\right)
\]

\[
P_0
=
a\exp(b\,EEMT)
\]

Production:

- \(a=0.037\ {\rm m\,kyr^{-1}}\)
- \(b=0.030\)
- \(H_0=0.50\ {\rm m}\)
- \(\rho_b/\rho_s=1.8\)

판정: 구조와 기본계수는 **Pelletier 원문 직접**, \(h\rightarrow H\) 등 상태변수 치환은 **논문 표기 일원화**.

## 9. Pelletier nonlinear hillslope transport

\[
E_c=\nabla\cdot\mathbf q
\]

\[
\mathbf q
=
-\frac{k_dH\cos\theta\nabla z}
{1-(|\nabla z|/S_c)^2}
\]

\[
k_d
=
c\,EEMT+d\,AGB^*
\]

Production:

- \(c=0.033\)
- \(d=0.050\)
- \(S_c=1.50\)

\(c\)와 \(d\)는 Pelletier et al. (2013) 구조와 값을 유지한다. \(AGB\) 위치에는 본 연구의 \(AGB^*\)가 들어간다.

Pelletier et al. (2013)의 기준 \(S_c=0.7\) 및 sensitivity \(S_c=0.9\)와 달리 production은 \(S_c=1.50\)이다. 이 값은 용늪 20 m real-DEM convergence audit에서 정한 **수치설정**이다.

## 10. Pelletier slope-wash 및 fluvial erosion

### 10.1 원문 구조

\[
E_f
=
K\frac{A}{w}|\nabla z|
\]

중요: \(w=gA^i\)는 모든 셀의 일반식이 아니다.

Pelletier et al. (2013)의 설명에 따라

hillslope sheet-flow:

\[
w=\Delta x
\]

tributary valley:

\[
w=gA^i
\]

원 값:

- \(g=0.005\)
- \(i=0.5\)

regolith:

\[
K_{\rm reg}
=
\frac{K_0}{EEMT}
\]

- \(K_0=0.020\ {\rm m^2\,MJ^{-1}}\)

bedrock:

\[
K_{\rm bed}
=
\frac{K_{\rm reg}}{F}
\]

- \(F=10\)

### 10.2 production code 판정

보존된 source audit는 fluvial K0/F/EEMT logic과 Pelletier-2010 \(A/w\) classifier가 후속 패치에서 변경되지 않았음을 기록한다. 따라서 manuscript에서는 원문의 conditional width와 regolith/bedrock erodibility를 분리하여 기술한다.

**추가 확인:** 최종 canonical ZIP은 binary blob이라 현재 GitHub text connector로 직접 압축해제할 수 없었다. 최종 제출 전 canonical archive를 로컬에서 풀어 \`pelletier_geomorph.py\`의 \(g\), \(i\), \(F\), valley classifier 상수와 source line을 다시 한 번 대조한다. 현재 근거는 canonical 이전 package의 source audit와 final integration이 geomorph core를 변경하지 않았다는 build provenance이다.

## 11. regional uplift

Pelletier et al. (2013)의 원 실험값:

\[
U=0.05\ {\rm m\,kyr^{-1}}
\]

용늪 production:

\[
U=0.08\ {\rm m\,kyr^{-1}}
\]

Lee et al. (2024)은 landscape-evolution model의 regional uplift를 80 mm kyr\(^{-1}\)로 설정했으며, 이 값을 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate와 동일하게 선택했다고 명시하였다. 용늪에서는 이 0.08 m kyr\(^{-1}\)를 regional background forcing으로 채택하며, 용늪 직접 측정 융기율로 해석하지 않는다.

판정: **지역 문헌에 근거한 본 연구 forcing**. 용늪 자체의 site-specific uplift measurement가 아니므로 이 점을 Methods와 Limitations에 명시한다.

## 12. numerical integration

| 항목 | 근거 | 판정 |
|---|---|---|
| 100년 coupling interval | study design | 본 연구 설정 |
| geomorph adaptive substep | Pelletier stability concept + PB4 solver | 원 개념 + 수치구현 |
| \(\Delta\tau=0.01\Delta x^2/(2k_{d,\max})\) | Pelletier explicit-step estimate의 PB4 raster 적용 | 원 구조 + 구현 |
| maximum-change tolerance 0.025 m | Yongneup convergence audit | 수치설정 |
| finite-volume donor-supply constraint | PB4 | 수치구현 |
| threshold-slope adjustment | PB4 real-DEM treatment | 수치구현 |
| open outlet fixed base level | PB4 boundary implementation | 수치구현 |
| geomorph substep 사이 BIOME4 미재실행 | production runner | source 직접 |

## 12.1 S_c=1.50 수치수렴 감사

보존된 `HILLSLOPE_SC15_AUDIT_2026-08-17.md`를 재확인하였다. 이는 20 m real DEM에서 1 kyr 경로를 대상으로 한 독립 수치감사이며, S_c=1.50을 자연사면의 보편적인 임계경사로 주장하는 근거가 아니다.

- 초기 land-land face: 552
- 초기 최대 cardinal-face slope: 약 1.332
- 초기 S>S_c: 0
- 초기 threshold adjustment: 0 cell
- tolerance 0.025 m에서 accepted substep: 120, dt=6.25-12.5 yr
- 최종 H min/mean/max: 0.104840/1.836665/3.267830 m
- 최종 최대 cardinal-face slope: 1.182459
- 최종 S>S_c: 0
- outlet drift: 0 m
- tolerance 0.025 -> 0.0125 m에서 max |Delta H|=0.008139 m, p99 |Delta H|=0.002596 m, mean |Delta H|=0.000299 m
- max |Delta z|=0.008139 m, max |Delta z_b|=0.000602 m

판정: **S_c=1.50은 20 m Yongneup production을 위한 본 연구 수치설정이며 수치수렴 근거가 보존되어 있다. 외부 논문으로 1.50 자체를 정당화할 필요는 없다. Pelletier et al. (2013)은 원 과정식 및 원 연구의 S_c 값 0.7/0.9를 설명하는 문헌으로만 인용한다.**

## 13. Jang et al. (2011) validation

원문 확인:

- pollen-analysis samples: 61
- radiocarbon samples: 5
- LPZ-I: 5,900-4,800 cal BP, deciduous broad-leaved forest
- LPZ-II: 4,800-3,400 cal BP, mixed coniferous and deciduous broad-leaved forest
- LPZ-III: 3,400-390 cal BP, deciduous broad-leaved forest
- LPZ-IV: 390 cal BP-present, mixed deciduous broad-leaved and coniferous forest

PB4 내부의 \`95_01\`-\`95_04\`는 Jang 원문의 sample ID가 아니라 project validation record ID이다.

네 LPZ 연대구간을 0.1-kyr model output grid에 대응하여 생성된 **모델 평가시점이 62개**이다. 따라서 manuscript에서 “Jang n=62 samples”라고 쓰면 틀리며 “Jang의 네 LPZ에 대응한 62개 model output-time”이라고 쓴다.

51% mixed-class majority rule은 **본 연구 postprocessing**이다.

1% basin-presence criterion은 **본 연구 validation rule**이다.

둘 다 BIOME4 process equation으로 쓰지 않는다.

### 검증 기준의 연구이력

- **유역 1% 출현 기준:** 2026-08-12에 생성된 `PB4Studio_v663_corrected_dynamic_validation_rows.csv`에 이미 `basin_presence_min_fraction=0.01`, `basin_presence_min_percent=1.0`이 기록되어 있다. 따라서 최종 CHELSA21K U008 결과를 선택하기 전에 사용되고 있던 검증기준임을 직접 확인하였다.
- **51% reduced-class majority rule:** 2026-10-05의 `NATIVE_CLIMATE_ABLATION_PROVENANCE.json`에서 PFT5/PFT6 climate tuning을 제거하는 최종 ablation 이전부터 `51% majority reduced classification`을 retained rule로 명시한다. 그러나 현재 보존자료만으로는 이 규칙이 모든 초기 결과 탐색보다 앞서 정해졌다고까지 입증하지 않는다. 논문에서는 preregistered threshold라고 표현하지 않고 **본 연구의 고정된 최종 후처리 규칙**이라고 기술한다.

## 14. 현재 추가 검토 상태

### 완료

- CHELSA-TraCE21k 원문과 production file 역할
- Beyer cloud-only 사용범위
- Bereiter CO2 interpolation
- BIOME4 v4.2b2 주요 input 및 source parameter
- McKenzie profile available-water 개념
- Gale/Jackson root-distribution 원식
- Reich Table 1 SLA-life-span 원식
- Pelletier EEMT, soil production, nonlinear hillslope transport
- Pelletier conditional fluvial width 구조
- Pelletier \(K_0\), \(F\), \(g\), \(i\) 원값
- 태백산맥 장기 삭박 및 exhumation 기반 regional uplift 문헌
- Jang 61 pollen samples, 5 radiocarbon samples 및 네 LPZ
- BIOME4 v4.2b2의 13 parameter sets, PFT1 비활성화 및 PFT8 C3 실제 실행경로

## 14.1 canonical ZIP 직접 압축해제 감사

GitHub Actions에서 repository의 canonical ZIP 자체를 checkout한 뒤 직접 압축해제하여 source를 재검증하였다. 감사 run은 `37414681328`이며 성공적으로 완료되었다.

현재 canonical ZIP은 `PB4Studio_v6.6.3_CHELSA21K.zip`이며, `FINAL_PROVENANCE.json`과 package audit에서 확인한 SHA-256은 `93790ba804a9cbce01291015af2750974d85b9688f0894de8d51d46cfb5a4b7b`이다.

압축해제한 `pb4studio/pelletier_geomorph.py`에서 다음을 직접 확인하였다.

- `uplift_m_per_kyr: float = 0.08`
- `hillslope_critical_slope: float = 1.50`
- `channel_width_coeff: float = 0.005`
- `channel_width_exp: float = 0.50`
- `grid_dependence_valley_threshold: float = 1.20`
- `bedrock_erosion_resistance: float = 10.0`
- hillslope width는 `dx_m`을 사용
- valley width는 `channel_width_coeff * A ** channel_width_exp` 구조
- valley/hillslope 분류 후 `np.where(valley, width_valley, width_hill)`로 적용
- uplift는 `cfg.uplift_m_per_kyr * dt_kyr`로 실제 적분에 사용

압축해제한 `pb4studio/climate.py`에서 CHELSA production branch의

- `df["lapse_rate_C_per_m"] = 0.0`
- `df["tmin_lapse_rate_C_per_m"] = 0.0`

을 직접 확인하였다. 파일 상단에는 다른 기후경로용 비영(非零) lapse-rate 함수가 남아 있으나, CHELSA21K production converter는 두 값을 명시적으로 0으로 덮어쓰므로 최종 production에는 추가 고도감률이 적용되지 않는다.

압축해제한 `fortran_src/biome4_original_4_2b2.f`에서는

- `stemcarbon=0.5`
- `mstemresp(m) = lai*stemcarbon*...`

를 직접 확인하였다.

강화된 exact assertion은 `g=0.005`, `i=0.5`, `F=10`, `S_c=1.5`, `U=0.08`, valley threshold 1.2, valley-width 식, hillslope-width 식, CHELSA lapse-rate 0, BIOME4 stemcarbon 0.5에 대해 모두 `True`로 통과하였다.

따라서 **최종 canonical ZIP 자체와 Methods/canonical 문서 사이의 핵심 지형, 기후 및 AGB source 설정 불일치는 발견되지 않았다.**

### 제출 전 마지막 확인

1. Haxeltine and Prentice (1996) publisher PDF 확인 완료: Eq. (34) = \(C_s=LAI C_n\), BIOME3 원 \(C_n=1\). 본 연구의 \(C_n=0.5\)는 BIOME4 v4.2b2 source에서 가져온 값으로 분리 표기
2. 최종 canonical ZIP을 로컬에서 직접 압축해제하여 \`pelletier_geomorph.py\`의 \(g=0.005\), \(i=0.5\), \(F=10\), valley classifier source line을 final SHA package와 다시 대조
3. \(S_c=1.50\) convergence audit 수치는 위 12.1에 확보 완료. 제출 시 Supplementary 표 형태로만 편집
4. SoilGrids provenance는 BDRICM_M_1km_ll의 ISRIC 2017-03-10 archive 경로와 wv0010/wv1500 정의까지 확인 완료. 제출 시 다운로드 날짜 또는 로컬 원본 파일 metadata가 남아 있으면 Supplementary에 추가
5. 완료: 1% 기준은 2026-08-12 validation export에서 확인되었고, 51% 기준은 최종 ablation 이전 retained rule임을 확인하였다. 51%는 preregistered라고 과장하지 않고 최종 고정 후처리 규칙으로 서술

## 14.2 최초 모델 관점 추가 감사

- 토심에 따른 PFT별 root fraction은 root-zone wetness 계산뿐 아니라 AET의 상층 및 하층 추출가중치에도 사용된다.
- SoilGrids의 깊이별 가용수분 밀도는 외부 논문에 용늪값으로 제시된 수치가 아니라 SoilGrids water-retention product에서 용늪 지점을 추출하여 계산한 값이다.
- 비선형 사면수송은 격자 경계면에서 Pelletier et al. (2013)의 FTCS 이산형식을 적용하며, 실제 flux 식은 face-average \(H\)와 \(k_d\) 및 face slope를 사용한다.
- Pelletier (2010)의 grid-resolution classifier에서 기여면적은 Freeman (1991) MFD로 계산하며 경사지수는 1.10이다. 절반 격자는 현재 DEM을 bilinear interpolation하여 생성하고, 각 원 격자셀에 대응하는 2x2 fine cells 가운데 최대 기여면적을 사용한다.
- fluvial erosion의 \(A\)는 native-grid MFD contributing area이고, 침식경사는 D8 receiver slope를 사용한다.
- geomorphic substep의 계산순서는 토양생산, 비선형 사면수송, 유수침식 순이다. 새로 생산된 레골리스는 같은 substep에서 이동 가능하며, fluvial erosion은 사면수송 뒤 남은 가용 레골리스를 사용한다.
- 잠재 유수침식량이 가용 레골리스를 초과하면 레골리스를 먼저 제거하고 잔여 침식능을 \(F\)로 나누어 기반암 침식에 적용한다.
- 혼효림 재분류는 biome 6, 7, 9에만 적용하고 broadleaf PFT2-4와 conifer PFT5-7의 각 최대 potential NPP를 비교한다.
- Jang 1% criterion의 분모는 reduced vegetation class 0-3의 식생 셀이며 비식생 class 4는 제외한다.

## 15. 핵심 참고문헌

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Bereiter, B., et al. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Freeman, T. G. (1991). Calculating catchment area with divergent flow based on a regular grid. *Computers & Geosciences, 17*(3), 413-422. https://doi.org/10.1016/0098-3004(91)90048-I

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*, 693-709. https://doi.org/10.1029/96GB02344

Jackson, R. B., et al. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*, 259-267. https://doi.org/10.5141/JEFB.2011.028

Kaplan, J. O. (2001). *Geophysical applications of vegetation modeling*. Doctoral dissertation, Lund University. ISBN 91-7874-089-4.

Karger, D. N., et al. (2023). CHELSA-TraCE21k: high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales*. CRC for Catchment Hydrology Technical Report 03/3.

Lee, C.-H., Seong, Y. B., Weber, J., Ha, S., Kim, D.-E., & Yu, B. Y. (2024). Topographic metrics for unveiling fault segmentation and tectono-geomorphic evolution with insights into the impact of inherited topography, Ulsan Fault Zone, South Korea. *Earth Surface Dynamics, 12*, 1091-1120. https://doi.org/10.5194/esurf-12-1091-2024

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., et al. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116


Hengl, T., Mendes de Jesus, J., Heuvelink, G. B. M., Ruiperez Gonzalez, M., Kilibarda, M., Blagotić, A., Shangguan, W., Wright, M. N., Geng, X., Bauer-Marschallinger, B., Guevara, M. A., Vargas, R., MacMillan, R. A., Batjes, N. H., Leenaars, J. G. B., Ribeiro, E., Wheeler, I., Mantel, S., & Kempen, B. (2017). SoilGrids250m: Global gridded soil information based on machine learning. *PLoS ONE, 12*(2), e0169748. https://doi.org/10.1371/journal.pone.0169748

Shangguan, W., Hengl, T., Mendes de Jesus, J., Yuan, H., & Dai, Y. (2017). Mapping the global depth to bedrock for land surface modeling. *Journal of Advances in Modeling Earth Systems, 9*(1), 65-88. https://doi.org/10.1002/2016MS000686

Turek, M. E., Poggio, L., Batjes, N. H., Armindo, R. A., de Jong van Lier, Q., de Sousa, L., & Heuvelink, G. B. M. (2023). Global mapping of volumetric water retention at 100, 330 and 15,000 cm suction using the WoSIS database. *International Soil and Water Conservation Research, 11*(2), 225-239. https://doi.org/10.1016/j.iswcr.2022.08.001
