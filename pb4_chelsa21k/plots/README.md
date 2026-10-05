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
