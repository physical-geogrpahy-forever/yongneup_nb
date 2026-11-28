# 모델 의의의 문헌 근거 (2026-11-27)

## 주장 1. 식생모델은 토양을 고정 입력으로 둔다
- Kaplan et al. (2003); Kaplan (1999, BIOME4 v4.2b2 코드): 토성 등급과 층별 WHC를 입력으로 받음.
- Pelletier, J. D., Broxton, P. D., Hazenberg, P., Zeng, X., Troch, P. A., Niu, G.-Y., Williams, Z., Brunke, M. A. and Gochis, D., 2016, A gridded global data set of soil, intact regolith, and sedimentary deposit thicknesses for regional and global land surface modeling, Journal of Advances in Modeling Earth Systems, 8, 41-65, doi:10.1002/2015MS000526.
  - 초록: 지구시스템모델은 기반암 위 투수층의 두께를 전 지구에서 균일하게 근사하지만, 실제 두께는 지형, 기후, 지질에 따라 체계적으로 달라진다.

## 주장 2. 같은 기후에서도 토층 두께와 저류능이 식생을 나눈다
- Hahm, W. J., Rempe, D. M., Dralle, D. N., Dawson, T. E., Lovill, S. M., Bryk, A. B., Bish, D. L., Schieber, J. and Dietrich, W. E., 2019, Lithologically controlled subsurface critical zone thickness and water storage capacity determine regional plant community composition, Water Resources Research, 55(4), 3028-3055, doi:10.1029/2018WR023760.
  - 비슷한 기후 아래에서 두꺼운 임계대는 상록림을, 인접한 얇은 임계대는 사바나를 지탱한다.
- Nakamura et al. (2015): 자작나무속 일부 종은 암벽과 능선에서 토양 조건이 만든 극상림을 이룬다.
- 고승연 외 (2014), 이호영 외 (2021): 국내 아고산 산지에서 거제수나무는 암석노출도 50~60%의 계곡부, 사스래나무는 능선과 사면 상부에서 우세.

## 주장 3. 식생과 지형의 결합 모델링에서의 위치
- Werner, C., Schmid, M., Ehlers, T. A., Fuentes-Espoz, J. P., Steinkamp, J., Forrest, M., Liakka, J., Maldonado, A. and Hickler, T., 2018, Effect of changing vegetation and precipitation on denudation - Part 1: Predicted vegetation composition and cover over the last 21 thousand years along the Coastal Cordillera of Chile, Earth Surface Dynamics, 6(4), 829-858, doi:10.5194/esurf-6-829-2018.
  - LPJ-GUESS에 지형 단위(landform) 모드를 도입하여 21 ka 이후 칠레 해안산맥의 식생 조성과 피복을 모의. 지형발달모델과의 양방향 결합은 향후 과제로 제시.
- Schmid, M., Ehlers, T. A., Werner, C., Hickler, T. and Fuentes-Espoz, J.-P., 2018, Effect of changing vegetation and precipitation on denudation - Part 2: Predicted landscape response to transient climate and vegetation cover over millennial to million-year timescales, Earth Surface Dynamics, 6(4), 859-881, doi:10.5194/esurf-6-859-2018.
  - Landlab에서 식생피복(V)으로 사면확산계수(Kd = Kb exp(-aV))와 매닝 조도를 조절. 식생피복은 외부에서 주어진 값이며 토양생성 식은 없음.
- Schmid, M., 2020, The effect of changing climate and vegetation on the topographic evolution of catchments in the Chilean Coastal Cordillera over millennial timescales, PhD dissertation, Eberhard Karls Universität Tübingen, doi:10.15496/publikation-39130.
  - 구두심사 2020-01-27, 온라인 공개 2020-07-01, 표제지 연도 2019. 지도교수 Todd Ehlers, 제2심사 Thomas Hickler.
  - 3.2.2절(미출판 원고, 인쇄본 82-113쪽)에서 LPJ-GUESS와 Landlab을 100년 간격으로 결합하여 LGM부터 현재까지 4개 유역(Pan de Azúcar, Santa Gracia, La Campana, Nahuelbuta)을 모의.
  - LPJ-GUESS에서 Landlab으로: PFT별 LAI를 교목, 관목, 초본으로 묶어 피복률로 바꾸고 landform ID로 격자에 배정(88, 91쪽). 사면확산계수는 누적 식생피복의 함수(89쪽), 유수침식은 토양, 교목, 관목, 초본별 매닝 조도로 조절(90쪽 표 1, 91쪽).
  - Landlab에서 LPJ-GUESS로: landform별 평균 경사, 고도, 사면방향, 토심(91쪽). LPJ-GUESS 안에서 토심이 어떻게 쓰이는지는 기술되지 않음.
  - 토양생성: PR = PRmax exp(-H/H*) 형태(원문 식 (8)은 음의 부호 없이 인쇄), PRmax는 10Be 삭박률(Schaller et al., 2018)과 Stockmann et al.(2014)로 정함(90-91쪽). 식생 항 없음.
  - 화분 등 고식생 기록과의 비교 없음. 4장 결론의 향후 과제는 매개변수 제약, 사면 풍화와 물질이동 법칙, 수로와 사면 실험(125-126쪽).
- Yetemen, O., Istanbulluoglu, E., Flores-Cervantes, J. H., Vivoni, E. R. and Bras, R. L., 2015, Ecohydrologic role of solar radiation on landscape evolution, Water Resources Research, 51(2), 1127-1157, doi:10.1002/2014WR016169.
  - 반건조 유역에서 일사, 토양수분, 식생 생물량, 유사 수지를 CHILD 안에서 결합. 식생은 단일 생물량 변수.
  - 원고의 "Yetemen et al., 2015"는 이 논문으로 본다. 같은 해 WRR 51(12)의 Yetemen, Istanbulluoglu and Duvall (2015)도 같은 CHILD 생태지형 모델로 식생을 생물량 하나로 다룬다.
- Pelletier et al. (2013): 식생, 토양, 지형의 공진화를 EEMT와 AGB로 연결. AGB는 경험식.

### Schmid (2020)과 VeSLEM의 차이 (원문 확인 사항만)
| 항목 | Schmid (2020) | VeSLEM |
|---|---|---|
| 식생모델 | LPJ-GUESS (동적, PFT 경쟁) | BIOME4 (평형, PFT 경쟁) |
| 결합 간격 | 100년 | 0.1 kyr |
| 식생 계산 단위 | landform (고도 구간, 사면 위치, 사면방향) | 30 m 격자 |
| 지형에서 식생으로 | landform 평균 경사, 고도, 사면방향, 토심 | 격자별 토심, 고도(기압) |
| 토심의 식생 효과 | 기술 없음 | 토양수분보유능력과 뿌리 분포 |
| 식생에서 지형으로 | 피복률과 생활형별 조도 → 사면확산, 유수침식 | NPP → EEMT → 기반암 풍화와 사면확산, 우점 PFT의 LAI → AGB → 사면확산 |
| 토양생성의 식생 의존 | 없음 | EEMT로 연결 |
| 고식생 기록 검증 | 없음 | 화분 2개 기록, PFT 출현 |

- 따라서 "최초"라는 표현은 쓰지 않는다. 양방향 결합과 토심 전달은 Schmid (2020)에 이미 있다.
- VeSLEM의 차별점은 (1) 식생 생산성을 토양생성에 연결하고, (2) 토심을 격자 단위로 식생모델의 수분보유능력과 뿌리 분포에 반영하며, (3) 그 결과를 화분 기록의 PFT 출현과 비교한 것이다.
- (2)는 결과와 직결된다. 동적 모델에서 PFT7과 온대 낙엽수 격자는 토심이 얇은 곡저 축에 나타났는데(유역 내 비우점 식생 비율 3.2%, 정적 0.33%), landform 평균 토심을 쓰는 방식에서는 이런 격자 단위 차이가 평균에 묻힌다.

### 원고 서론에 대한 확인 결과
- 원고의 Schmid (2020) 기술(양방향 결합, 변화한 지형과 토심 전달, 교목 관목 초본 재분류, NPP를 토양생성에 연결하지 않음)은 원문과 맞는다.
- 덧붙일 수 있는 사실: 식생 계산과 토심 전달이 landform 단위 평균으로 이루어졌다는 점, 고식생 기록과 비교하지 않았다는 점. 유수침식에는 피복률뿐 아니라 교목, 관목, 초본별 매닝 조도가 쓰였으므로 "주로 식생피복률을 통해"라는 표현은 유지하되 "단일 변수" 비판은 사면확산에 한정하는 편이 정확하다.

## 주장 4. 작은 분지의 화분은 주변 수백 m 식생을 반영한다
- Sugita (1994): 반경 약 50 m 분지에서 화분은 주로 가장자리 300~400 m 이내 식생을 반영.

## 주장 5. 매개변수
- 최종 실행의 매개변수는 BIOME4 원본, Pelletier et al. (2013), Pelletier and Rasmussen (2009), Lee et al. (2024), SoilGrids 값을 그대로 사용. 화분 기록에 맞추어 조정한 값은 없음.
- 개발 과정에서 임계경사(1.5), EEMT 처리, 지형 자료를 바꾼 실행을 기록과 비교한 적이 있으나(`results/final_fab30_20261113/sensitivity/`), 최종 선택은 원 문헌 값으로 되돌린 것이다.
