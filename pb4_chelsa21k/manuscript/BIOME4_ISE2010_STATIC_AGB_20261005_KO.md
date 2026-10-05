# NPP와 PFT로 계산하는 정적 AGB: Ise et al. (2010)의 VISIT 평형식 이식

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
