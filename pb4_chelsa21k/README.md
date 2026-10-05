# PB4Studio CHELSA21K archive

용늪 PB4Studio의 현재 CHELSA-TraCE21k forcing, 실행 패키지, 모델 프로세스 설명을 함께 보존하는 디렉터리다.

핵심 파일:

- `PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md`: 데이터, 모델 계보, coupling 프로세스, static/dynamic 및 original/modified 비교 설계
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`: 21–0 ka, 100년 간격 211시점 CHELSA/EnviCloud 원자료
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`: 위 CSV의 원본 압축본
- `payload/`: `PB4Studio_v6.6.3_CHELSA21K.zip`의 base64 분할 보존본
- `reconstruct_pb4.py`: PB4 ZIP 재구성 및 SHA-256 검증
- `SHA256SUMS.txt`: 원자료와 모델 패키지 무결성 값

과거 Beyer 실행 정확도나 이전 hotfix 정확도는 현재 CHELSA21K 결과로 간주하지 않는다. 새 결과는 동일 CHELSA21K forcing으로 다시 실행한 뒤 별도로 기록한다.

## 2026-10-04 four-way CHELSA21K run

The new original-BIOME4/static, original-BIOME4/dynamic, modified/static, and modified/dynamic comparison is complete. Primary validation uses the Jang et al. (2011) original vegetation-zone descriptions, 62 100-year output-time items, and the project **1% basin-presence criterion**.

See [results/fourway_20261004/PB4_CHELSA21K_FOURWAY_RESULTS_KO.md](results/fourway_20261004/PB4_CHELSA21K_FOURWAY_RESULTS_KO.md).


## 2026-10-05 production model: native BIOME4 climate limits

PFT5/PFT6 climate tuning only was removed and the full 21-0 ka CHELSA21K run was repeated. Jang 2011 corrected 1% validation was unchanged: static **24/62 = 38.71%**, dynamic **55/62 = 88.71%**.

The canonical package is now `PB4-McKenzie-nativeClimate`: McKenzie AWC, finite-depth PFT root coupling, the symmetric 51% majority reduced-class rule, and dynamic Pelletier coupling are retained, while PFT5/PFT6 climate limits are the native BIOME4 v4.2b2 limits.

- Final package: `model/PB4Studio_v6.6.3_CHELSA21K.zip`
- Explicit final alias: `model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`
- Final decision/results: `results/native_climate_final_20261005/`
- Canonical SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
