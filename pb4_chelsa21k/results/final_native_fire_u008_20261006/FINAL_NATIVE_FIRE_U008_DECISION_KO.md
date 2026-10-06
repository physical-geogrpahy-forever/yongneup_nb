# PB4Studio CHELSA21K 최종 산불 처리 결정

업데이트: 2026-10-06

## 최종 결정

최종 production은 `PB4Studio 6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008`의
BIOME4 v4.2b2 **native fire module**을 그대로 사용한다.

이전에 검토한 U009의
`fire event -> 다음 0.1 kyr PFT8 상태기억`
확장은 최종 모델에서 제외한다.

최종 구조:

```text
CHELSA(t) + H(t)
 -> BIOME4 2층 토양수분수지
 -> PFT별 native firedays
 -> BIOME4 v4.2b2 competition2의 원래 fire 규칙
 -> 같은 시점의 평형 PFT/biome 선택
 -> NPP, LAI, AET
 -> BIOME4-derived AGB*, EEMT
 -> [dynamic] Pelletier 지형변화
 -> 다음 0.1 kyr에서 다시 독립 평형 계산
```

## 유지하는 원본 fire 처리

- `subroutine fire`의 PFT별 토양수분 fire threshold
- 잠재 fire days 계산
- NPP가 1000 g C m^-2 yr^-1 미만일 때의 원 BIOME4 firedays scaling
- `competition2`의 원래 PFT별 fire 경쟁 규칙
- 예: PFT6 `firedays > 90 d yr^-1`

## 최종 모델에서 사용하지 않는 추가 규칙

- 산불 뒤 PFT8을 100년 유지하는 상태기억
- Park/Jang 연대를 직접 입력하는 fire event
- 화분 또는 charcoal 기록에 맞춘 fire threshold 재보정
- 기후 강수량의 결과맞춤형 보정
- 모든 목본을 일괄 탈락시키는 별도 fire rule

따라서 각 0.1 kyr 시점의 식생은 BIOME4의 원래 평형 경쟁으로 다시 결정된다.
한국의 온난습윤한 조건에서 fire pressure가 약해지면 다음 시점에 목본이 다시 우점할 수 있으며,
별도의 천이 지속시간을 강제하지 않는다.

## FIREACTIVE 실행판의 의미

`PB4Studio_v6.6.3_CHELSA21K_FINAL_NATIVE_FIRE_U008.zip`은 native fire 과학식을 바꾸지 않고
firedays 진단량을 정상 PB4 출력에 노출한 실행판이다.

추가 진단:
- `summary_timeseries.csv`: dominant/PFT별 firedays 평균과 최대
- snapshot/cell values: firedays 및 주요 PFT별 firedays

기후값, fire threshold, PFT 기후 niche, NPP, AGB*, EEMT, Pelletier 파라미터는 변경하지 않는다.

## 정량 검증

FIREACTIVE U008은 과학식을 변경하지 않는 diagnostics-only 판이므로 기존 production의 Jang 검증값을 그대로 유지한다.

- static: 24/62 = 38.71%
- dynamic: 55/62 = 88.71%

## 무결성

최종 native-fire 실행 ZIP SHA-256:

`578923dee512278a64f97d914acc9b1f67af7d13007a099bb2931b17b5e6a49c`

U009는 실험 후보로만 보존하고 production에서는 사용하지 않는다.


## Park et al. (2021) 독립 화재추세 점검

후기 홀로세 3.2–2.0 ka에서 native PFT6 최대 firedays와 Park et al. (2021)의
macrocharcoal 화재기를 비교하였다.

- Park 주요 화재기: 2.9–2.7 ka, 2.4–2.3 ka
- 모델은 첫 화재기에 116 -> 119 -> 134일로 상승하고 2.7 ka에서 최대값을 보임
- 두 번째 화재기에 120 -> 124일로 재상승
- 2.2 ka에는 104일로 감소
- 단, 2.1 ka에 129일의 추가 고점이 있어 완전한 일대일 대응은 아님
- 3.2–2.0 ka 탐색 비교에서 Park 화재시점 평균 122.6일, 나머지 시점 평균 112.625일
- point-biserial r = 0.542 (n=13, 탐색값)

상세:
`PARK2021_NATIVE_FIRE_TREND_AUDIT_KO.md`

원자료:
`NATIVE_FIRE_SPATIAL_3P5_2P0.csv`
