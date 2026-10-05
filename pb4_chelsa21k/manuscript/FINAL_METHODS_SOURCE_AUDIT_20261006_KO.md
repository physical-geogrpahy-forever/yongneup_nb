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
| 식생모형 | Kaplan et al. (2003) 및 BIOME4 v4.2b2 source | 원문 직접 + source 직접 |
| 입력 | 월별 기온, 강수, cloudiness, absolute Tmin, CO2, 토양수문조건 | source 직접 |
| PFT 수 | production v4.2b2 source에 13 PFT | source 직접 |
| PFT별 NPP 및 optimal LAI | BIOME4/BIOME3 계열 생리 및 경쟁구조 | 원문 직접 + source 직접 |
| native climate limits | 최종 production에서 v4.2b2 native limits 유지 | source/provenance 직접 |
| 토심별 NPP 또는 LAI 직접 multiplier | 사용하지 않음 | source 직접 |

BIOME4 source 확인 파일:

\`pb4_chelsa21k/results/herbaceous_cause_20261006/source_snapshot/biome4_original_4_2b2.f\`

## 4. 토심과 available-water storage

McKenzie et al. (2003), Technical Report 03/3은 profile available water capacity를 field capacity와 wilting point에 대응하는 \(-10\) kPa와 \(-1.5\) MPa의 체적수분함량 차이로 설명하고, plant available water를 계산할 때 root distribution을 별도로 고려한다.

| 식 또는 입력 | 출처 | 판정 |
|---|---|---|
| \(AWC=\theta_{-10}-\theta_{-1500}\) | McKenzie et al. (2003), profile available water capacity 정의 | 원문 직접 |
| \(W_{\rm top}(H)\) 적분식 | McKenzie의 AWC 개념 + BIOME4 0-0.30 m layer | 본 연구 구현 |
| \(W_{\rm bottom}(H)\) 적분식 | McKenzie의 AWC 개념 + BIOME4 0.30-1.50 m layer | 본 연구 구현 |
| 1.50 m cap | BIOME4 native hydraulic profile | source 직접 |
| 용늪 water-density profile 237, 232, 218, 207, 198, 179 mm m\(^{-1}\) | 용늪 SoilGrids 기반 project point profile | project 입력 |
| SoilGrids 일반 자료체계 | Poggio et al. (2021), 250 m global product | 원문 직접 |

주의: Poggio et al. (2021)이 용늪의 \(\theta_{-10}\) 및 \(\theta_{-1500}\) 값을 직접 제시한 것으로 쓰지 않는다.

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

Haxeltine and Prentice (1996)의 BIOME3 sapwood-LAI 관계를 문헌 원전으로 사용한다.

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
U=0.20\ {\rm m\,kyr^{-1}}
\]

Park et al. (2017)은 고성-삼척 동해안 중부에서 당시 해수면을 고려한 MIS 5 이후 융기율을 0.16-0.28 m kyr\(^{-1}\)로 정리하였다. 따라서 0.20은 이 범위에 포함된다.

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
- 동해안 중부 regional uplift 문헌
- Jang 61 pollen samples, 5 radiocarbon samples 및 네 LPZ

### 제출 전 마지막 확인

1. Haxeltine and Prentice (1996) publisher PDF에서 \(C_s=LAI\,C_n\)의 Eq. (34) 번호와 표기 시각 재확인
2. 최종 canonical ZIP을 로컬에서 직접 압축해제하여 \`pelletier_geomorph.py\`의 \(g=0.005\), \(i=0.5\), \(F=10\), valley classifier source line을 final SHA package와 다시 대조
3. \(S_c=1.50\) convergence audit의 실험조건과 선택근거를 Supplementary 표로 정리
4. 용늪 SoilGrids point profile의 원 다운로드 metadata와 좌표, SoilGrids version을 Supplementary provenance에 명시
5. 51%와 1% validation rule이 최종 결과 선택 전에 고정되었는지 연구이력상 시점을 다시 기록하여 reviewer가 tuning으로 오해하지 않도록 설명

## 15. 핵심 참고문헌

Beyer, R. M., Krapp, M., & Manica, A. (2020). High-resolution terrestrial climate, bioclimate and vegetation for the last 120,000 years. *Scientific Data, 7*, 236. https://doi.org/10.1038/s41597-020-0552-1

Bereiter, B., et al. (2015). Revision of the EPICA Dome C CO2 record from 800 to 600 kyr before present. *Geophysical Research Letters, 42*, 542-549. https://doi.org/10.1002/2014GL061957

Gale, M. R., & Grigal, D. F. (1987). Vertical root distributions of northern tree species in relation to successional status. *Canadian Journal of Forest Research, 17*, 829-834. https://doi.org/10.1139/x87-131

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*, 693-709. https://doi.org/10.1029/96GB02344

Jackson, R. B., et al. (1996). A global analysis of root distributions for terrestrial biomes. *Oecologia, 108*, 389-411. https://doi.org/10.1007/BF00333714

Jang, B.-O., Kang, S.-J., & Choi, K.-R. (2011). Vegetation history around Yongneup moor at Mt. Daeamsan, Korea. *Journal of Ecology and Environment, 34*, 259-267. https://doi.org/10.5141/JEFB.2011.028

Karger, D. N., et al. (2023). CHELSA-TraCE21k: high-resolution (1 km) downscaled transient temperature and precipitation data since the Last Glacial Maximum. *Climate of the Past, 19*, 439-456. https://doi.org/10.5194/cp-19-439-2023

McKenzie, N. J., Gallant, J. C., & Gregory, L. J. (2003). *Estimating water storage capacities in soil at catchment scales*. CRC for Catchment Hydrology Technical Report 03/3.

Park, C.-S., Kim, Y.-H., Nam, W.-H., & Lee, G.-R. (2017). Formative age of coastal terraces and uplift rate in the East Coast of South Korea. *Journal of the Korean Geomorphological Association, 24*, 43-55.

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

Poggio, L., et al. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL, 7*, 217-240. https://doi.org/10.5194/soil-7-217-2021

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*, 365-392. https://doi.org/10.2307/2937116
