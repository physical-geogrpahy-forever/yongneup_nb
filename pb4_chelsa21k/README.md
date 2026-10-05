# PB4Studio CHELSA21K archive

용늪 PB4Studio의 현재 CHELSA-TraCE21k forcing, 실행 패키지, 모델 프로세스 설명을 함께 보존하는 디렉터리다.

핵심 파일:

- `PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md`: 데이터, 모델 계보, coupling 프로세스, static/dynamic 및 original/modified 비교 설계
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`: 21–0 ka, 100년 간격 211시점 CHELSA/EnviCloud 원자료
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`: 위 CSV의 원본 압축본
- `payload/`: `PB4Studio_v6.6.3_CHELSA21K.zip`의 base64 분할 보존본
- `reconstruct_pb4.py`: PB4 ZIP 재구성 및 SHA-256 검증
- `SHA256SUMS.txt`: 원자료와 모델 패키지 무결성 값
- `manuscript/VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md`: Pelletier/McKenzie 원문 대조, PB4 수식, HWP 입력 가이드
- `manuscript/WORKLOG_20261005_HWP_AGB_LITERATURE_AUDIT_KO.md`: 2026-10-05까지의 AGB coupling 문헌감사, BIOME4 v4.2b2 source audit, 잠정적 최종모델 위치, 미해결 과제 및 다음 실행 계획

## 현재 최종 과학모형

AGB 검토는 종료되었으며 최종 과학모형은 **PB4-McKenzie-nativeClimate + BIOME4-derived AGB***로 고정한다. 기존 nativeClimate canonical ZIP은 AGB 변경 전 비교 baseline으로 보존하고, AGB*가 반영된 별도 candidate package를 최종 AGB 구현 기준으로 사용한다.

- 모델: `PB4-McKenzie-nativeClimate`
- canonical: `model/PB4Studio_v6.6.3_CHELSA21K.zip`
- explicit alias: `model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`
- SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
- production commit: `cfd220b2be2b9d166aa0d5e220c3dc1d9c78634a`
- 결과/provenance: `results/native_climate_final_20261005/`

**식생 코어는 BIOME4 v4.2b2로 고정한다.** AGB*의 변재-LAI 관계는 BIOME 계보의 Haxeltine and Prentice (1996) Eq. (34)를 사용하고, 실제 계수와 PFT 적용은 BIOME4 v4.2b2 source code를 따른다. 잎 건조생체량은 Reich et al. (1992)의 SLA-life-span 회귀식을 사용한다. AGB* candidate는 21-0 ka 전체 재실행 및 Jang 검증을 완료했다.

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


### 2026-10-05 final AGB* decision

Final AGB* equation:

[
AGB^*_{dry,p}
=
LAI_p
left[
S_p + 0.03630780547701014 L_{m,p}^{0.43}
ight]
]

Pelletier coupling:

[
k_d = 0.033 EEMT + 0.05 AGB^*
]

The direct Pelletier exponential EEMT-to-AGB equation is not used for Yongneup.

- authoritative method: `manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md`
- final decision: `results/agb_bridge_comparison_20261005/AGB_BRIDGE_PROMOTION_DECISION_KO.md`
- full-run results: `results/reich_lai_sapwood_agb_candidate_20261005/`
- selected AGB* package: `model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip`
- selected AGB* package SHA-256: `1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c`
- dynamic 21 ka mean AGB*: 3.11600 kg m^-2
- dynamic 0 ka AGB*: 3.46620 kg m^-2 = 34.662 t ha^-1
- Jang dynamic validation: 55/62 = 88.71%

