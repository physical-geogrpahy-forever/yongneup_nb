# Plots

논문 그림과 재현 코드. 모든 그림은 `thesis_style.py`의 공통 형식(본문 폭 16 cm, Noto Sans CJK KR 8 pt, PNG 600 dpi와 SVG)을 쓴다. 캡션은 `FIGURE_CAPTIONS_KO.md`.

| 그림 | 코드 | 입력 |
|---|---|---|
| `fig_basin_analysis` | `plot_basin_analysis.py` | `../data/FABDEM_V1-2_yongneup_region_EPSG5187_27p4m.tif` |
| `fig_soil_texture_triangle` | `plot_fao_soil_texture_triangle.py` | 없음 (FAO-UNESCO 1974 경계) |
| `fig_climate_chelsa` | `plot_chelsa_climate.py` | `../data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv` |
| `fig_mean_timeseries` | `plot_mean_timeseries.py` | `../results/final_fab30_20261113/reference_run/model_*/summary_timeseries.csv` |
| `fig_firedays` (+ `_cells.csv`, `_depth.csv`) | `plot_firedays.py` | `../results/final_fab30_20261113/FINAL_STATE_CUBE.npz` |

실행: `python <코드>` (이 폴더에서).
