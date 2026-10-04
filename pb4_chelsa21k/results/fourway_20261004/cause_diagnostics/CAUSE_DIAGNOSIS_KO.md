# PB4Studio CHELSA21K 수정형 성능 향상 원인 진단

업데이트: 2026-10-04

## 연구 범위와 실행 지위

본 진단은 대암산 용늪의 습지생태학, 고생태학, 고기후학, 생물지형학 연구를 위한 PB4Studio 분석이다.

- 기후: `YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`, CHELSA-TraCE21k/EnviCloud, 21-0 ka BP
- 모델: `PB4Studio_v6.6.3_CHELSA21K`
- 비교: 순수 BIOME4 v4.2b2 control과 hotfix10n10 `mckenzie2003`
- 실행: 2026-10-04 새 실행 및 직접 PFT 진단
- 검증: Jang et al. (2011) 원문 식생대 reduced mapping, n=62, 유역 1% 출현을 주 기준으로 사용

## 결론

수정형 dynamic의 55/62 = 88.71% 성능은 하나의 수정 때문이 아니라 두 단계로 설명된다.

1. 원본 static 19/62 -> 수정형 static 24/62의 증가는 주로 hotfix10n10의 51% reduced-class dominance 판정 때문에 발생한다.
2. 수정형 static 24/62 -> 수정형 dynamic 55/62의 +31개 증가는 지형발달이 만든 극천부 토양 포켓과 McKenzie/Jackson finite-depth root-water coupling이 결합되어 95_03 전체 31시점에서 native BIOME4 temperate deciduous forest를 실제로 만들기 때문에 발생한다.

따라서 가장 중요한 생태지형학적 개선은 침엽수 온도한계 조정 자체가 아니라 **동적 토심 이질성 + 토심에 민감한 뿌리/수분 결합**이다.

## 1. 원본에서 수정형 static으로 좋아진 이유

5.9 ka의 동일 CHELSA 기후와 동일 static 토심에서 원본과 수정형은 모두 298셀 전체가 native BIOME4 biome 7, Cool mixed forest이다.

핵심 PFT 평균 NPP도 사실상 동일하다.

- PFT4: 약 486.75
- PFT6: 약 463.22
- PFT7: 약 420.23
- broadleaf dominance share: 약 0.512386

수정형은 broadleaf 대 conifer/taiga 최대 NPP 비교에서 broadleaf share가 51% 이상이면 reduced class를 broadleaf로 재분류한다. 따라서 5.9 ka에는 298셀 전체가 reduced broadleaf가 된다. 반면 순수 원본 control은 native biome 7을 mixed로 유지한다.

즉 95_01에서 수정형 static이 12/12를 얻는 핵심은 native biome 자체가 완전히 바뀐 것이 아니라 **51% reduced mapping**이다.

PFT5는 원본에서 native 기후제약 때문에 이 시기 NPP=0이고 수정형에서는 허용되지만, 실제 strongest conifer/taiga competitor는 PFT6이므로 PFT5 완화가 이 성능 차이의 주원인은 아니다.

## 2. 수정형 dynamic이 static보다 크게 좋아진 이유

95_03은 3.4-0.39 ka의 낙엽활엽수림 구간이다.

static에서는 토심이 거의 전 유역에서 약 1.94 m로 균질하며 이 구간 31시점 모두 broadleaf 기준을 충족하지 못해 0/31이다.

dynamic에서는 장기 지형발달로 토심 분포가 크게 벌어진다.

- 3.4 ka 평균 H 약 2.32 m
- 0.4 ka 평균 H 약 2.49 m
- 그러나 국지 최소 H는 대체로 약 0.03-0.06 m
- 최대 H는 약 11-12 m

즉 평균 토심은 증가하지만 침식부에는 몇 cm 수준의 극천부 토양 포켓이 지속된다.

95_03의 모든 31시점에서 native BIOME4 broadleaf cell이 3-4셀 존재한다.

- 3/298 = 1.0067%
- 4/298 = 1.3423%

따라서 사용자가 지정한 1% 기준을 31/31 모두 통과한다. hotfix 51% post-classification은 몇 셀을 더 broadleaf로 추가하지만, **95_03의 31/31 통과 자체에는 필요하지 않다.** native BIOME4 biome이 이미 broadleaf로 바뀐 셀이 1%를 넘는다.

## 3. 3 ka 직접 PFT 비교

### 순수 원본 dynamic의 얕은 토양

예를 들어 3 ka의 매우 얕은 셀에서도 원본은 다음과 같다.

- H=0.0374 m
- WHC=5.60 mm
- PFT4 NPP=528.21
- PFT6 NPP=505.94
- PFT7 NPP=462.17
- optPFT=4, subPFT=6
- native biome=7, mixed

즉 **지형이 얕은 토양을 만드는 것만으로는 충분하지 않다.**

### 수정형 dynamic의 같은 종류의 얕은 토양

3 ka 수정형에서는:

- H=0.0455 m
- WHC=10.77 mm
- PFT4 NPP=344.35
- PFT6 NPP=284.37
- PFT7 NPP=389.47
- optPFT=7, subPFT=4
- native biome=4, Temperate deciduous forest

다른 예에서도 H 약 0.0496-0.0541 m에서 같은 optPFT7/subPFT4 구조가 나타난다.

원 BIOME4 `newassignbiome`에는 optPFT=7이고 subPFT=4일 때 biome 4로 배정하는 규칙이 있다. 따라서 수정형의 토심-수문 결합이 PFT 경쟁 순서를 바꾸고, 그 결과는 BIOME4 자체의 원래 biome 판정 규칙을 통해 temperate deciduous forest로 나타난다.

## 4. McKenzie/Jackson coupling이 필요한 이유

수정형은 실제 토심에 따라 AWC와 PFT별 뿌리 접근성을 제한한다.

예를 들어 대략:

- H=0.05 m에서 PFT4 접근 뿌리 비율 약 0.16
- H=0.05 m에서 PFT6/PFT7 접근 뿌리 비율 약 0.26
- H=0.10 m에서 PFT4 약 0.30
- H=0.10 m에서 PFT6/PFT7 약 0.45

AWC도 극천부 토양에서는 약 10-30 mm 수준으로 감소한다. 깊은 토양에서는 약 298.55 mm이다.

따라서 얕은 토양에서는 단순히 전체 생산성이 일정 비율로 감소하는 것이 아니라 PFT별 수분 접근성과 수분스트레스가 다르게 변한다. 그 결과 PFT 경쟁 순서가 바뀐다.

원본 dynamic에도 얕은 토양은 생기지만 이 finite-depth root-water coupling이 없기 때문에 PFT4가 계속 optPFT로 남아 native mixed forest가 유지된다. 이는 **지형발달 alone이 아니라 지형발달과 수정형 토심-뿌리-수문 coupling의 결합이 핵심**임을 보여준다.

## 5. 침엽수 온도 조정의 역할

PFT5의 -19 C 확장과 PFT6 Sitch/BoNE 조정은 수정형 구성의 일부이지만, 이번 Jang 기간 성능향상의 주된 원인은 아니다.

- 원본 PFT5는 주요 시점에서 기후제약을 통과하지 못하고 NPP=0
- 수정형 PFT5는 통과한다
- 그러나 strongest conifer/taiga competitor는 주로 PFT6 또는 PFT7이다
- PFT6은 주요 Jang 시점에서 원본과 수정형 모두 기후적으로 허용된다

따라서 88.71%의 주원인을 단순히 '침엽수 온도범위를 넓혀서'라고 설명하면 잘못이다.

## 6. 최종 원인 사슬

```text
21 ka부터 누적된 동적 지형발달
        ↓
침식부에 H 약 3-12 cm의 극천부 토양 포켓 형성
        ↓
McKenzie AWC + Jackson finite-depth root accessibility
        ↓
PFT별 수분스트레스와 NPP 경쟁 순서 변화
        ↓
일부 셀에서 optPFT7 / subPFT4
        ↓
원 BIOME4 newassignbiome 규칙
        ↓
native biome 4, Temperate deciduous forest
        ↓
3-4 / 298셀 = 1.01-1.34%
        ↓
Jang 95_03의 1% 기준 31/31 통과
        ↓
수정형 dynamic 전체 55/62 = 88.71%
```

이 결과는 작은 공간 비율이지만 3.4-0.4 ka 전 기간에 지속되는 국지적 낙엽활엽수림 포켓으로 해석할 수 있다. 'refugium-like pocket'이라는 표현을 사용할 경우에는 모델 기반 해석임을 명시한다.
