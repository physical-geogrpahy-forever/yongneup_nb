# Methods 원문 대조 감사기록

작성일: 2026-10-06  
대상: \`FINAL_METHODS_MANUSCRIPT_DRAFT_20261006_KO.md\`

이 문서는 최종 Methods에 들어간 문헌기반 수식과 자료 설명을 원 논문 또는 원 보고서와 다시 대조한 기록이다. 논문 본문보다 이 감사기록이 우선하는 것은 아니며, 향후 수정 시 잘못된 출처 귀속이나 수식 변형을 방지하기 위한 provenance 문서이다.

| 항목 | 원문 확인 | 최종 Methods 처리 | 판정 |
|---|---|---|---|
| CHELSA-TraCE21k | Karger et al. (2023)은 30 arcsec 공간해상도, 월별 기온과 강수, 100년 간격, 지난 21 ka 자료를 제시 | 기후자료 원출처로 인용. 추가 lapse correction 미적용은 본 연구 전처리 선택으로 구분 | 확인 |
| Beyer climate | Beyer et al. (2020)은 월별 temperature, precipitation, cloud cover 등을 포함한 120 ka 자료를 제시 | cloud만 보조 forcing으로 사용하고 Beyer temperature와 precipitation은 사용하지 않았다고 명시 | 확인 |
| CO2 | Bereiter et al. (2015)은 800 ka CO2 history의 갱신본과 last glacial cycle을 포함한 composite를 제시 | PB4Studio 내장 composite의 provenance로 사용 | 확인 |
| BIOME4 | Kaplan (2001)은 BIOME4의 개발과 적용을 직접 기술. Kaplan et al. (2003)은 BIOME4의 탄소 및 물 순환, PFT, NPP, soil depth 입력 등을 기술 | Kaplan (2001)을 직접 모델 참고문헌으로, Kaplan et al. (2003)을 구조 설명의 보조 문헌으로 사용 | 확인 |
| McKenzie AWC | McKenzie et al. (2003)은 약 -10 kPa와 -1.5 MPa의 VWC 차이에 기초한 profile AWC와 깊이별 root scaling을 제시 | BIOME4 2층 적분식은 McKenzie 원식이 아니라 본 연구 결합식으로 명시 | 확인 |
| Jackson roots | Jackson et al. (1996)의 누적 뿌리분포는 \(Y=1-\beta^d\) 형태 | BIOME4 top-30-cm root fraction과 McKenzie exponential scaling의 연결근거로 사용 | 확인 |
| \(X_p\) 변환 | 원문에 동일 식 없음 | \(X_p=-0.30/\ln(1-r_{30,p})\)은 본 연구의 분석적 변환으로 명시 | 확인 |
| Reich SLA | Reich et al. (1992) Table 1의 LEAVES 전체자료: \(\log_{10}(SLA)=2.44-0.43\log_{10}(\mathrm{life-span})\), life-span month, SLA cm2 g-1 | 원식 그대로 사용. 0.036307... 파생계수는 Methods에서 제거 | 확인 |
| Sapwood-LAI | Haxeltine and Prentice (1996) Eq. 34의 \(C_s=LAI C_n\) 관계를 기존 원문 감사에서 확인 | BIOME3를 별도 모형으로 결합하지 않고 BIOME4에 계승된 관계의 문헌 원전으로만 사용 | 확인 |
| BIOME4 stemcarbon | v4.2b2 source의 \`stemcarbon=0.5\`와 sapwood respiration flag 확인 | source implementation parameter로 명시하고 출판식과 구분 | 확인 |
| EEMT | Pelletier et al. (2013) Eq. 1-2의 \(E_{\mathrm{PPT}}\), \(E_{\mathrm{BIO}}\) 관계 확인 | 월 AET와 carbon NPP에 맞춘 PB4 합산식은 본 연구 구현식으로 구분 | 확인 |
| Pelletier state equations | Eq. 6-10의 \(z=b+h\), 기반암고도 변화, 토심질량수지, \(P\), \(P_0\) 확인 | 상태변수만 \(z_b,H,\tau\)로 일원화하고 식은 분리 | 확인 |
| Pelletier hillslope | Eq. 11, 14, 15의 divergence, nonlinear depth-dependent flux, \(k_d=cEEMT+dAGB\) 확인 | \(AGB\) 입력만 \(AGB^*\)로 교체. \(k_d\)를 flux 식에 대입하지 않음 | 확인 |
| Pelletier fluvial | Eq. 16-18의 \(E_f=K(A/w)|\nabla z|\), \(w=gA^i\), \(K=K_0/EEMT\) 확인 | 세 식을 각각 독립식으로 유지 | 확인 |
| Pelletier \(a,b,c,d,H_0,\rho_b/\rho_s\) | Table 1의 원 연구값 확인 | production에서 원 연구값을 유지하되 남부 애리조나 화강암질 환경의 경험계수라는 사실을 명시 | 확인 |
| Pelletier \(K_0=0.020\) | 원문은 EEMT=10에서 mean distance-to-valley를 맞추도록 trial-and-error로 calibration했다고 명시 | 용늪에서 새로 보정한 값처럼 서술하지 않음 | 확인 |
| Pelletier \(g=0.005,i=0.5,F=10\) | Table 1과 본문에서 확인 | project equation guide에서는 동일값 유지로 기록. 최종 binary package config 직접 재대조는 제출 전 확인 항목 | 부분 확인 |
| \(S_c\) | Pelletier 기본값 0.7, sensitivity 0.9 확인 | 용늪 production의 1.50은 20 m real-DEM 수치수렴 설정으로 명확히 분리 | 확인 |
| \(U\) | Pelletier 원 연구는 0.05 m kyr-1 | 용늪 production은 0.20 m kyr-1이나 project source에는 지역 참고값이라는 주석만 존재 | 문헌 보강 필요 |
| Jang pollen data | Jang et al. (2011)은 61 pollen samples, 5 radiocarbon samples, 4 LPZ를 보고 | 본 연구의 n=62는 61개 pollen sample 수가 아니라 4 LPZ를 100년 model output에 대응시킨 검증시점 수라고 명시 | 확인 |
| Jang LPZ mapping | 5.9-4.8 ka deciduous, 4.8-3.4 ka mixed, 3.4-0.39 ka deciduous, 0.39-0 ka mixed | corrected reduced mapping과 일치 | 확인 |
| 51% rule | 원 Jang 또는 BIOME4 생리식에 없음 | 검증용 output reclassification이라고 명시 | 확인 |
| 1% rule | 원 Jang 또는 BIOME4 내부 임계값이 아님 | 본 연구의 basin-presence 판정기준이라고 서술형으로 명시 | 확인 |

## 원문에서 특히 중요한 주의사항

Pelletier et al. (2013)의 \(a\), \(b\), \(c\), \(d\), \(K_0\)는 보편 상수가 아니다. 특히 원 논문은 \(P_0\)-EEMT 관계가 같은 암종에서도 절리밀도 등에 따라 달라질 수 있음을 지적하며, \(K_0=0.020\)은 관측 mean distance-to-valley를 기준으로 조정한 값이다. 용늪 PB4는 이 계수들을 Jang 자료에 맞추어 새로 보정하지 않고 원 연구값을 이식하였다. 따라서 논문에서는 "Pelletier et al. (2013)의 식과 계수를 사용하였다"와 "용늪에서 이 계수를 관측자료로 보정하였다"를 명확히 구분한다.

Reich et al. (1992)의 SLA-life-span 회귀식은 원식을 그대로 제시한다. 이를 단위변환하고 정리하여 얻는 0.036307...은 새로운 생태계수가 아니므로 논문 Methods에 별도 계수로 표시하지 않는다.

McKenzie et al. (2003)의 AWC 및 root scaling과 PB4의 BIOME4 2층 구현은 구분한다. 특히 \(X_p=-0.30/\ln(1-r_{30,p})\), \(W_{\mathrm{top}}\), \(W_{\mathrm{bottom}}\), \(R_{\mathrm{top},p}\), \(R_{\mathrm{bottom},p}\)는 문헌의 개념을 BIOME4 구조에 연결한 본 연구 구현이다.

## 원문 링크

- Karger et al. (2023): https://doi.org/10.5194/cp-19-439-2023
- Beyer et al. (2020): https://doi.org/10.1038/s41597-020-0552-1
- Bereiter et al. (2015): https://doi.org/10.1002/2014GL061957
- Kaplan (2001): https://lup.lub.lu.se/search/publication/3bfcb2f2-dec3-40a3-a6d3-8764f660ce56
- Kaplan et al. (2003): https://doi.org/10.1029/2002JD002559
- McKenzie et al. (2003): https://www.ewater.org.au/archive/crcch/overview/archive/pubs/pdfs/technical200303.pdf
- Jackson et al. (1996): https://doi.org/10.1007/BF00333714
- Reich et al. (1992): https://doi.org/10.2307/2937116
- Haxeltine and Prentice (1996): https://doi.org/10.1029/96GB02344
- Pelletier et al. (2013): https://doi.org/10.1002/jgrf.20046
- Poggio et al. (2021): https://doi.org/10.5194/soil-7-217-2021
- Jang et al. (2011): https://doi.org/10.5141/JEFB.2011.028
