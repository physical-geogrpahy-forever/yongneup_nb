# 모델 의의의 문헌 근거 (2026-11-27 확인)

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
- Werner, C., Schmid, M., Ehlers, T. A., Fuentes-Espoz, J. P., Steinkamp, J., Forrest, M., Liakka, J., Maldonado, A. and Hickler, T., 2018, Effect of changing vegetation and precipitation on denudation - Part 1, Earth Surface Dynamics, 6, 829-858.
- Schmid, M., Ehlers, T. A., Werner, C., Hickler, T. and Fuentes-Espoz, J.-P., 2018, Effect of changing vegetation and precipitation on denudation - Part 2, Earth Surface Dynamics, 6, 859-881.
  - LPJ-GUESS로 21 ka 이후 식생을 모의하고 그 결과를 지형발달모델 입력으로 사용(단방향). 완전 결합은 향후 과제로 제시.
- Yetemen, O., Istanbulluoglu, E., Flores-Cervantes, J. H., Vivoni, E. R. and Bras, R. L., 2015, Ecohydrologic role of solar radiation on landscape evolution, Water Resources Research, 51, 1127-1157.
  - 반건조 유역에서 생태수문 식생 동역학과 지형발달을 양방향으로 결합한 선례. 식생은 생물량 동역학으로 단순화.
- Pelletier et al. (2013): 식생, 토양, 지형의 공진화를 EEMT와 AGB로 연결. AGB는 경험식.
- 따라서 "최초"라는 표현은 쓰지 않는다. VeSLEM의 차별점은 (1) PFT 경쟁을 계산하는 평형 생물군계 모델(BIOME4)을 (2) 토심을 매개로 양방향 결합하여 (3) 21 ka 동안 모의하고 (4) 화분 기록의 PFT 출현과 비교한 것.

## 주장 4. 작은 분지의 화분은 주변 수백 m 식생을 반영한다
- Sugita (1994): 반경 약 50 m 분지에서 화분은 주로 가장자리 300~400 m 이내 식생을 반영.

## 주장 5. 매개변수
- 최종 실행의 매개변수는 BIOME4 원본, Pelletier et al. (2013), Pelletier and Rasmussen (2009), Lee et al. (2024), SoilGrids 값을 그대로 사용. 화분 기록에 맞추어 조정한 값은 없음.
- 개발 과정에서 임계경사(1.5), EEMT 처리, 지형 자료를 바꾼 실행을 기록과 비교한 적이 있으나(`results/final_fab30_20261113/sensitivity/`), 최종 선택은 원 문헌 값으로 되돌린 것이다.
