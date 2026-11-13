# Plots

논문 및 분석용 그림과 재현 코드를 저장하는 폴더입니다.

## CHELSA-TraCE21k 기후 변화

- `plot_chelsa_climate.py`: CHELSA-TraCE21k 월자료에서 연평균 기온과 연강수량을 계산하고 이중 y축 그래프를 생성합니다.
- `CHELSA_TraCE21k_Yongneup_temperature_precipitation.svg`: 현재 기온-강수량 그래프입니다.
- 입력자료: `../data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- x축: 21 ka BP에서 현재
- 왼쪽 y축: 연평균 기온 (°C)
- 오른쪽 y축: 연강수량 (mm)
- 기온: 적색 실선
- 강수량: 청색 실선
- 제목 없음

Python 스크립트를 실행하면 동일 폴더에 PNG와 SVG가 생성됩니다.

## 3.5–2.0 ka 최대 산불잠재일수

- `plot_max_firedays_3p5_2p0ka.py`: 최종 모델의 동적/정적 지형 모델 결과에서 시점별 유역 최대 산불잠재일수를 계산하고 연강수량과 함께 그립니다.
- `YONGNEUP_FINAL_max_firedays_3p5_2p0ka.png`, `.svg`, `.csv`: 현재 그림과 그림 자료입니다.
- 입력자료: `../results/final_fire_wetness_20261112/b_vs_e/13_B_STATE_CUBE.npz`, `../data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 음영: Park et al. (2021) 산불 시기 2.9–2.7 ka, 2.4–2.3 ka
- 동적 지형 모델: 적색 실선, 정적 지형 모델: 청색 실선, 연강수량: 회색 파선
- 제목 없음
