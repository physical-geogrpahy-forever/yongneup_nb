# 최종 모델: 산불잠재일수 근권 토양수분 정규화

## 변경 내용

원본 BIOME4 v4.2b2는 두 토층의 토양수분을 뿌리 비율로 가중평균한 근권 토양수분 wr = root·w(1) + (1−root)·w(2)로 산불잠재일수를 계산하며, 이때 두 가중치의 합은 1이다. U008은 토심이 1.5 m보다 얕은 격자에서 뿌리 비율을 실제 토심까지 잘라 쓰므로(rtop_eff, rbot_eff) 가중치의 합이 1보다 작아지고, 포화된 얕은 토양도 산불 판정에서는 매일 건조한 것으로 계산되었다.

최종 모델은 산불 판정에 쓰는 근권 토양수분만 가중치의 합으로 나누어 원본과 같은 정의로 되돌린다.

```fortran
       wr = rtop_eff*w(1) + rbot_eff*w(2)
       wr_n=wr/max(rtop_eff+rbot_eff,1.0e-6)
...
       wet(d)=wr_n
```

수분 공급(supply), 낙엽 계절성(phenology), meanwr은 U008과 같이 잘린 가중치의 wr을 사용한다. 연료량 보정(NPP/1000), 산불 임계값(90/180/210일)은 원본 그대로이다.

- 패키지: `../../model/PB4Studio_v6.6.3_CHELSA21K.zip` (version `6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008-FIREWRN`)
- 수정 위치: `pb4studio/biome4_backend.py`의 McKenzie2003 Fortran 패치
- 이전 패키지: `../../model/archive/PB4Studio_v6.6.3_CHELSA21K_U008_PRE_FIREWRN.zip`
- 생성 Fortran: `abcd/B_generated_fortran.f` (SHA-256 `8b9037e2ddbb2f8ad0c927d6f2d79650659bc2f9523c12581d0481c24b2c4dbe`). 최종 패키지가 생성하는 Fortran과 바이트 단위로 같다.
- U008 대비 Fortran 차이: `abcd/A_to_B.diff`

## 검증 결과

| 모델 | Jang et al. (2011) | Park et al. (2021) PFT TSS |
|:--|--:|--:|
| 정적 지형 모델 | 24/62 (38.7%) | 0.522 |
| 동적 지형 모델 | 55/62 (88.7%) | 0.588 |

U008과 검증 결과가 같다. 산불 정규화는 식생 경쟁 결과를 바꾸지 않고 얕은 토양의 산불잠재일수만 바꾼다.

- 정적 지형 모델: 모든 격자의 토심이 1.5 m 이상이므로 산불잠재일수는 0일이다.
- 동적 지형 모델: 토심 0.3 m 미만 격자에서만 산불잠재일수가 나타난다. 3.5–2.0 ka 유역 최대값은 50–55일이다(`../../plots/YONGNEUP_FINAL_max_firedays_3p5_2p0ka.png`).

## 재현 확인 (2026-11-13)

최종 패키지를 새로 풀어 `tools/run_yongneup_21ka_chelsa_selfcontained.py`로 21–0 ka 정적/동적 지형 모델을 다시 실행했다(Linux, GNU Fortran 13.3.0).

- `validation_accuracy.csv`, `validation_per_output_time.csv`, `pft_validation_summary.csv`, `pft_model_cells_per_output_time.csv`: 기준 실행(`abcd/raw_run_B`)과 파일 단위로 같다.
- `summary_timeseries.csv`: 시점별 최대 산불잠재일수는 같고, 연속 변수는 컴파일 환경 차이로 소수점 아래에서 다르다(동적 지형 모델 LAI 최대 차이 0.08).
- `tools/check_package_contract.py`: PASS

## 폴더

- `abcd/`: U008(A)과 정규화 범위를 달리한 B, C, D 실험. B가 최종 모델이다. C는 낙엽 계절성과 meanwr, D는 수분 공급까지 정규화한다. D는 동적 지형 모델 Jang 정확도가 24/62로 떨어진다.
- `abcd/raw_run_B/`: 최종 모델 기준 실행 원자료
- `b_vs_e/`: 산불 판정에 표층 토양수분 w(1)을 쓰는 E와의 비교. `13_B_STATE_CUBE.npz`는 최종 모델의 시점별 격자 상태(산불잠재일수, 우점 PFT, biome, 토심)이다.
