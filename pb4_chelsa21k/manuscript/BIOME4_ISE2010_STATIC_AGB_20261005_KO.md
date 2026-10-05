# NPP와 PFT로 계산하는 정적 AGB: Ise et al. (2010)의 VISIT 평형식 이식

> **적용 판정 추가, 2026-10-05:** 아래 식의 산술 재현은 확인했지만, 원계수를 그대로 용늪 모델의 검증된 최종 AGB 계수로 채택하지 않는다. 관측연도가 겹치는 31개 성숙림 관측구와 비교한 예측/관측 비율의 중앙값은 PFT4=0.784(n=7), PFT5=0.489(n=15), PFT6=2.247(n=8), PFT7=1.810(n=1)이다. 이는 조건부 평형식의 존재와 실제 적용 정확도가 다르다는 직접 검증 결과다. 계산기는 진단용으로 보존한다.

## 판정과 적용 범위

**NPP와 PFT만 입력하는 정적 계산은 가능하다.** Ise et al. (2010)은 실제로 성분별 NPP에서 평형 생체량을 계산했다. 이 문서와 코드는 논문의 VISIT 배분식과 체류율을 결합하여 총 NPP를 입력받도록 정리한 것이다.

다만 이 논문의 Table 1은 온대 산림과 아한대 산림을 각각 하나의 군으로 취급한다. 여기서는 BIOME4 PFT4/5를 온대, PFT6/7을 아한대에 대응시킨다. **이 대응은 명시적인 모델 간 이식이며, 네 PFT를 각각 보정한 관측 회귀식은 아니다. PFT4=5, PFT6=7의 계수가 같다.**

PFT7에 broadleaf-only 자료를 대입하거나 Larix만 별도 논문에서 가져오지 않는다. Boreal forest라는 넓은 모델 군에 PFT6/7을 함께 대응시킨다. 이 때문에 broadleaf와 deciduous conifer를 포함하는 PFT7의 하위형마다 별도 계수가 필요하지는 않지만, 그 하위형들에 대한 독립 정확도가 검증되었다는 뜻은 아니다.

## 출처와 이번 작업

- Ise, T., Litton, C. M., Giardina, C. P., & Ito, A. (2010). Comparison of modeling approaches for carbon partitioning: Impact on estimates of global net primary production and equilibrium biomass of woody vegetation from MODIS GPP. *Journal of Geophysical Research*, 115, G04025. DOI: [10.1029/2010JG001326](https://doi.org/10.1029/2010JG001326).
- [출판사 원문](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JG001326).
- [공저자 대학 사이트의 원문 PDF](https://gms.ctahr.hawaii.edu/gs/handler/getmedia.ashx?dt=3&g=12&moid=6541). 공저자 Litton의 연구 페이지에서 연결된 파일이다.
- 확인 위치: Table 1은 PDF p.3, Eq. (7)-(12)는 p.4, Appendix A의 Eq. (A10)-(A15)는 p.10. 이 세 페이지의 표와 식을 시각적으로 확인했다.
- 논문의 원래 전지구 실험은 MODIS MOD17 2001-2006 GPP와 Hansen et al. 토지피복을 사용한다. 이번 작업은 그 실험을 재실행하지 않았다.
- 이번에 새로 실행한 것은 아래 계산기의 산술 재현과 탄소 수지 검증이다. BIOME4, 기후 입력, 지형 모델을 실행하지 않았고 용늪의 예측값으로 제시하지 않는다.
- 새 계산기: `ise2010_static_agb.py`. 외부 패키지 없이 Python 표준 라이브러리로 실행된다.

## 원문 계수

| 계수 | 의미 | 온대 산림 | 아한대 산림 |
|---|---|---:|---:|
| f_f | EPP 중 잎으로 배분되는 비율 | 0.198 | 0.134 |
| f_s | 잎 배분 이후 남은 EPP 중 stem으로 배분되는 비율 | 0.500 | 0.500 |
| k_gf | 잎 성장 호흡 비율 | 0.498 | 0.466 |
| k_gs | stem 성장 호흡 비율 | 0.145 | 0.118 |
| k_gr | 뿌리 성장 호흡 비율 | 0.243 | 0.214 |
| k_f | 잎 turnover rate, yr^-1 | 1.08 | 0.702 |
| k_s | stem turnover rate, yr^-1 | 0.0234 | 0.0108 |
| k_r | 뿌리 turnover rate, yr^-1 | 0.288 | 0.137 |

**f_f와 f_s는 총 NPP의 배분율이 아니다.** EPP는 GPP에서 유지 호흡을 뺀 탄소이며, 아직 성장 호흡을 포함한다. 특히 f_s는 잎 배분 이후의 잔여량에 적용된다. 이 계수를 그대로 총 NPP에 곱하면 잘못된 계산이 된다.

원문은 stem과 root의 sapwood/heartwood를 별도로 계산한다. 아래 AGB는 원문의 지상부 잎과 stem 풀의 합이며 root 풀은 제외한다. generic wood에 coarse root가 섞인 IBIS 값을 사용하거나 임의의 root-to-shoot correction을 추가하지 않는다. 잎 외 지상부는 이 모델의 집약된 stem 풀로 표현되며 별도 과실 풀 등은 없다.

## 총 NPP에서의 유도

Eq. (A10)-(A15)에 따라 EPP 한 단위당 순생산량을 다음처럼 둔다.

```math
q_f=f_f(1-k_{gf}),
q_s=(1-f_f)f_s(1-k_{gs}),
q_r=(1-f_f)(1-f_s)(1-k_{gr}).
```

```math
NPP=(q_f+q_s+q_r)EPP,
\qquad
a_j=\frac{q_j}{q_f+q_s+q_r}.
```

따라서 총 NPP가 주어지면 EPP, GPP, 기온, 산림 나이를 별도 입력할 필요 없이 성분별 NPP를 계산할 수 있다. NPP를 다시 GPP로 오인하거나 유지 호흡을 중복 차감하지 않는다.

Eq. (10)-(11)의 평형해에서 지상부 탄소량은 다음과 같다.

```math
C^*_{AG}=NPP\left(\frac{a_f}{k_f}+\frac{a_s}{k_s}\right).
```

건물 탄소 비율 f_C를 추가하여 건조 AGB로 변환한다.

```math
AGB^*_{dry}=\frac{NPP}{1000f_C}
\left(\frac{a_f}{k_f}+\frac{a_s}{k_s}\right).
```

- NPP 입력: g C m^-2 yr^-1.
- AGB 출력: kg dry matter m^-2.
- f_C=0.5는 이번 연결 계산의 명시적 공통 가정이며, 해당 논문에서 새로 추정한 값이라고 표현하지 않는다.
- stock 계산의 k 값은 turnover **rate**이다. 체류시간은 1/k이며 k 자체를 yr 단위 체류시간으로 사용하지 않는다.

## 계산된 배분율과 결과

| 군 | a_f | a_s | a_r | 잎 체류시간, yr | stem 체류시간, yr |
|---|---:|---:|---:|---:|---:|
| 온대 | 0.133272907 | 0.459709469 | 0.407017624 | 0.925925926 | 42.735042735 |
| 아한대 | 0.090143613 | 0.481111111 | 0.428745276 | 1.424501425 | 92.592592593 |

f_C=0.5일 때 아래 계수 c에 대해 AGB=c*NPP이다.

| BIOME4 입력 | 이식한 군 | c | NPP=500일 때 AGB, kg dry m^-2 |
|---|---|---:|---:|
| PFT4, temperate deciduous trees | 온대 | 0.0395382093253 | 19.769104663 |
| PFT5, temperate evergreen conifers | 온대 | 0.0395382093253 | 19.769104663 |
| PFT6, boreal evergreen trees | 아한대 | 0.0893514696160 | 44.675734808 |
| PFT7, boreal deciduous trees | 아한대 | 0.0893514696160 | 44.675734808 |

위 숫자의 자릿수는 산술 재현을 위한 것이다. 생태학적 정확도를 그 자릿수까지 보장하지 않는다. 동일 군의 두 PFT에 서로 다른 숫자를 만들기 위한 추가 보정은 하지 않았다.

## 실행

```bash
python ise2010_static_agb.py --npp 500 --pft 7
```

출력에는 dry AGB, 성분별 탄소량, NPP 배분율, 실제 사용한 군, 탄소 비율 가정과 출처가 포함된다. root carbon은 별도로 출력하되 AGB 합산에서 제외한다. PFT4-7 외 입력, 음수/비유한 NPP, 잘못된 탄소 비율은 오류로 처리한다. NPP=0이면 AGB=0이다.

함수 호출:

```python
from ise2010_static_agb import static_agb
agb = static_agb(npp=500, pft=7)["agb_dry_kg_m2"]
```

## 검증과 해석의 한계

2026-10-05 새로 검증했다. Decimal 40자리 연산으로 EPP=1000에서 원문 A10-A15를 직접 계산하고, 그렇게 얻은 총 NPP를 계산기에 넣어 결과를 대조했다. PFT4/5/6/7 모두 일치했다. 세 성분의 NPP 비율 합=1, 각 stock의 loss=NPP, NPP=0의 결과=0, NPP 선형 배율, f_C 역비례와 7개의 잘못된 입력 처리도 확인했다.

이 검증은 **원문 식의 산술 재현**이다. 네 PFT의 독립 관측 AGB 검증이나 용늪 현장 보정이 아니다. 장기적으로 생산과 손실이 균형인 살아 있는 식생의 평형량을 계산하므로 어린 산림, 최근 산불, 벌채 직후의 실제 AGB로 해석하지 않는다. 온대에서 상록/낙엽, 아한대에서 상록/낙엽의 차이를 각각 따로 추정하는 해상도는 이 Table 1에 없다.

제공된 NPP를 이 관측/모델 체계의 잎+stem+root 순생산량과 대응시키는 것 역시 연결 가정이다. BIOME4 NPP의 단위와 대상 PFT를 확인해 입력해야 한다. 이 계산기만으로 BIOME4 원모델의 네 PFT별 AGB 출력이 존재한다고 주장하지 않는다.

**사용 가능한 결론:** 공통된 한 논문의 VISIT 계수와 평형식으로 모든 forest PFT4-7 입력을 처리하는 온대/아한대 2군 정적 AGB 계산기를 제공한다. 네 PFT마다 독립 계수를 갖는 더 세분된 모델이 확인됐다는 결론은 내리지 않는다.

## 추가 적용 검증: 원계수 채택 보류

사용자의 요청에 따라 단위/입출력 코드와 실제 관측 AGB를 대조했다. 이 절의 판정이 위 계산기의 사용 가능 범위를 제한한다.

### BIOME4 NPP 확인

현재 canonical `PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip`을 읽었다. SHA-256은 `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`로 기존 기준과 일치한다. Production 파일을 수정하거나 재실행하지 않았다.

`fortran_src/biome4_original_4_2b2.f`의 호흡 계산에서 NPP는 GPP에서 stemresp, leafresp, finerootresp와 growthresp를 뺀 연간 탄소 순생산량이다. 따라서 이를 ANPP나 wood production으로 취급하면 안 된다. `findnpp`는 LAI를 바꾸며 최대 NPP를 찾는다. 즉 이 값은 관측 산림의 나이별 생산량을 직접 계산한 값이 아니라 해당 PFT의 최적 LAI 하에서 계산된 잠재 생산량이다.

원 Fortran의 output(3)을 Python의 `npp_node=out[2]`로 전달한다. PFT별 생산량은 `pftXX_mod_npp_node` 등으로도 노출된다. `tree_npp_total_node`나 `total_pft_npp_node`는 서로 대안적으로 경쟁하는 PFT들의 잠재 NPP를 합한 진단값이므로 관측 forest total NPP와 같다고 보고 AGB 식에 넣으면 안 된다. 선택한 PFT와 일치하는 NPP를 사용해야 한다. 현재 `npp_node`에 곧바로 다른 dominant diagnostic에서 얻은 PFT를 붙이는 것도 해당 output들이 같은 선택을 나타내는지 확인한 뒤에만 가능하다.

단위와 NPP/ANPP 구분은 해결됐지만, BIOME4의 잠재 NPP를 다른 모델의 pooled stock parameters로 이식한 연결이 현장 AGB까지 정확하다는 근거는 아직 없다.

### 관측자료와 비교

입력: 기존에 검증해 보존한 `BIOME4_LUYSSAERT_FORC_DIAGNOSTIC_PAIRS_20261005.csv`. ForC commit `407c520e6350917bca42e6bf7d5031dbcc551362`의 Luyssaert-origin 자료다. NPP_1_C와 biomass_ag_C를 같은 site/plot/vegetation으로 연결했고 두 기록 모두 reported stand age >=100인 44개 연결 기록, 35개 관측구다. 999는 성숙림 표시이며 실제 999년이라고 해석하지 않는다.

NPP는 Mg C ha^-1 yr^-1에서 100을 곱해 g C m^-2 yr^-1로, AGB는 Mg C ha^-1에서 0.1/f_C를 곱해 kg dry m^-2로 변환했다. 예측과 관측에 동일한 f_C=0.5를 사용하므로 예측/관측 비율에서는 f_C가 소거된다. 이 오차를 탄소-건물 환산계수만 바꿔 해소할 수는 없다.

동일 plot에 여러 연결 기록이 있으면 각 예측/관측 비율의 중앙값을 먼저 구했다. 이어 PFT별로 plot들을 동일한 가중치로 요약했다. 전체 자료와 시간 중첩 자료, 시간 중첩+동일 reported age 자료를 모두 확인했으며 이 자료에 모델 계수를 맞추지 않았다.

| 관측연도 중첩 자료 | 관측구 수 | 예측/관측 AGB 비율 중앙값 | plot 비율의 평균 절대백분율오차 |
|---|---:|---:|---:|
| PFT4 | 7 | 0.783975 | 27.03% |
| PFT5 | 15 | 0.488637 | 48.31% |
| PFT6 | 8 | 2.247305 | 157.09% |
| PFT7 | 1 | 1.809878 | 80.99% |

시간 중첩과 동일 reported age를 모두 요구해도 관측구 수는 각각 6/14/8/1이며 중앙값은 0.783440/0.480888/2.247305/1.809878이다. PFT5 과소예측과 PFT6 과대예측은 이 추가 제한으로 없어지지 않는다.

PFT7의 시간 중첩 관측은 Aheden broadleaf 1곳이다. Larix가 있는 Tura는 NPP 2000-2004에 비해 AGB 관측연도가 불명이라 strict comparison에서 제외했다. Tura를 포함한 전체 진단에서는 예측/관측=8.479753이지만, 이를 동시점 정확도 검증으로 제시하지 않는다. 원계수에 Larix-specific 적용성이 입증됐다고 말할 수 없다.

이 mature diagnostic selection이 교란 없는 수학적 평형 산림만으로 구성되었다고 입증된 것은 아니다. 따라서 오차로 원 논문의 평형 이론 자체를 기각하지 않는다. 그러나 현 프로젝트에서 이 원계수를 검증된 실측 AGB 예측식으로 채택할 근거로 삼을 수도 없다.

재현 코드: `audit_ise2010_applicability.py`.
수치와 관측별 출처: `BIOME4_ISE2010_APPLICABILITY_20261005.json`.

**최종 적용 판정:** 원문 평형 구조와 총 NPP 변환의 산술은 확인됐다. 제시한 0.0395382093/0.0893514696 원계수는 이식 후보의 진단값이며, 현 프로젝트의 검증된 최종 계수로 채택하지 않는다. 특히 PFT5/6의 관측 불일치와 PFT7의 strict validation 표본 부족이 남는다. Production AGB bridge를 이 후보로 바꾸지 않았다.
