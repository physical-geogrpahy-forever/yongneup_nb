# PB4Studio CHELSA21K archive

용늪 PB4Studio의 현재 CHELSA-TraCE21k forcing, 실행 패키지, 모델 프로세스 설명을 함께 보존하는 디렉터리다.

핵심 파일:

- `PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md`: 데이터, 모델 계보, coupling 프로세스, static/dynamic 및 original/modified 비교 설계
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`: 21–0 ka, 100년 간격 211시점 CHELSA/EnviCloud 원자료
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`: 위 CSV의 원본 압축본
- `payload/`: `PB4Studio_v6.6.3_CHELSA21K.zip`의 base64 분할 보존본
- `reconstruct_pb4.py`: PB4 ZIP 재구성 및 SHA-256 검증
- `SHA256SUMS.txt`: 원자료와 모델 패키지 무결성 값
- `manuscript/FINAL_METHODS_CANONICAL_20261006_KO.md`: 최종 Methods 수식, 변수명, 검증정책의 권위 기준
- `manuscript/FINAL_METHODS_MANUSCRIPT_DRAFT_20261006_KO.md`: 실제 논문 본문에 옮길 수 있는 최종 Methods 서술 초안
- `manuscript/FINAL_METHODS_SOURCE_AUDIT_20261006_KO.md`: 원문, source code, 본 연구 구현을 식별한 Methods 출처 감사표
- `manuscript/VESLEM_PB4_HWP_EQUATION_GUIDE_KO.md`: Pelletier/McKenzie 원문 대조용 참고 감사문서
- `manuscript/WORKLOG_20261005_HWP_AGB_LITERATURE_AUDIT_KO.md`: 2026-10-05까지의 AGB coupling 문헌감사, BIOME4 v4.2b2 source audit, 잠정적 최종모델 위치, 미해결 과제 및 다음 실행 계획

## 현재 최종 과학모형

AGB 검토와 통합 재실행을 완료했으며 최종 과학모형은 **PB4-McKenzie-nativeClimate + BIOME4-derived AGB***로 고정한다. AGB* 구현은 이제 candidate가 아니라 canonical production package에 통합되었다. AGB 변경 전 nativeClimate 패키지는 archive에 보존한다.

- 모델: `PB4-FINAL-nativeClimate-BIOME4AGB`
- canonical: `model/PB4Studio_v6.6.3_CHELSA21K.zip`
- explicit final alias: `model/PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip`
- compatibility alias: `model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`
- canonical SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- final integration commit: `2e0df5606e5c23d35b1b4ad421a4adf2d3031e08`
- 최종 결과/provenance: `results/final_integrated_20261006/`
- pre-AGB archive SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

**식생 코어는 BIOME4 v4.2b2로 고정한다.** AGB*의 변재-LAI 관계는 BIOME 계보의 Haxeltine and Prentice (1996) Eq. (34)를 사용하고, 실제 계수와 PFT 적용은 BIOME4 v4.2b2 source code를 따른다. 잎 건조생체량은 Reich et al. (1992)의 SLA-life-span 회귀식을 사용한다. AGB* candidate는 21-0 ka 전체 재실행 및 Jang 검증을 완료했다.

과거 Beyer 실행 정확도나 이전 hotfix 정확도는 현재 CHELSA21K 결과로 간주하지 않는다. 새 결과는 동일 CHELSA21K forcing으로 다시 실행한 뒤 별도로 기록한다.

## 2026-10-04 four-way CHELSA21K run

The new original-BIOME4/static, original-BIOME4/dynamic, modified/static, and modified/dynamic comparison is complete. Primary validation uses the Jang et al. (2011) original vegetation-zone descriptions, 62 100-year output-time items, and the project **1% basin-presence criterion**.

See [results/fourway_20261004/PB4_CHELSA21K_FOURWAY_RESULTS_KO.md](results/fourway_20261004/PB4_CHELSA21K_FOURWAY_RESULTS_KO.md).


## 2026-10-05 production model: native BIOME4 climate limits

PFT5/PFT6 climate tuning only was removed and the full 21-0 ka CHELSA21K run was repeated. Jang 2011 corrected 1% validation was unchanged: static **24/62 = 38.71%**, dynamic **55/62 = 88.71%**.

The canonical package is now `PB4-McKenzie-nativeClimate`: McKenzie AWC, finite-depth PFT root coupling, the symmetric 51% majority reduced-class rule, and dynamic Pelletier coupling are retained, while PFT5/PFT6 climate limits are the native BIOME4 v4.2b2 limits.

- Final package: `model/PB4Studio_v6.6.3_CHELSA21K.zip`
- Explicit final alias: `model/PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip`
- Final decision/results: `results/final_integrated_20261006/`
- Canonical SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`


### 2026-10-05 final AGB* decision

Final AGB* definition:

\[
AGB^*_{\mathrm{dry},p}
=
B_{\mathrm{leaf,dry},p}
+
B_{\mathrm{sapwood,dry},p}
\]

Leaf biomass uses the Reich et al. (1992) SLA-life-span equation in its published form, with \(B_{\mathrm{leaf,dry},p}=LAI_p/SLA_p\). The decimal-expanded implementation coefficient is code-level only and is not treated as an independent Methods parameter.

Pelletier coupling:

\[
k_d = 0.033\,EEMT + 0.05\,AGB^*
\]

The direct Pelletier exponential EEMT-to-AGB equation is not used for Yongneup.

- authoritative method: `manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md`
- final decision: `results/agb_bridge_comparison_20261005/AGB_BRIDGE_PROMOTION_DECISION_KO.md`
- full-run results: `results/reich_lai_sapwood_agb_candidate_20261005/`
- AGB* candidate used for final integration: `model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip`
- AGB* candidate SHA-256: `1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c`
- final integrated canonical SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`
- dynamic 21 ka mean AGB*: 3.11600 kg m^-2
- dynamic 0 ka AGB*: 3.46620 kg m^-2 = 34.662 t ha^-1
- Jang dynamic validation: 55/62 = 88.71%



### 최종 검증정책

최종 Methods와 정량 검증은 **Jang et al. (2011)만 사용**한다.

- 대상: `95_01`, `95_02`, `95_03`, `95_04`
- 총 62개 100년 output-time
- 판정: 관측 식생군이 모의 유역 내 유효 격자의 1% 이상에서 출현하면 일치
- 결과: static **24/62 = 38.71%**, dynamic **55/62 = 88.71%**
- 51% 과반 규칙은 mixed biome의 검증용 reduced-class 재분류에만 사용하며 BIOME4 내부 경쟁식이 아님

Park et al. (2021) 관련 holdout, PC2 상관, Herbs 비교는 연구과정 기록으로만 보존하고 최종 Methods와 최종 정량 검증에서는 사용하지 않는다.

최종 방법론 기준:
`manuscript/FINAL_METHODS_CANONICAL_20261006_KO.md`
