# CHELSA21K에서 수정형 dynamic이 더 높은 이유

업데이트: 2026-10-04

## 결론

Jang et al. (2011) 원문 식생대, 1% 유역 출현 기준에서 수정형 dynamic은 55/62 = 88.71%이다. 원본 dynamic 19/62 = 30.65%, 수정형 static 24/62 = 38.71%보다 높다.

이 개선은 주로 다음 두 과정에서 나온다.

1. 동적 지형이 만든 매우 얕은 토양을 McKenzie2003/Jackson1996 finite-depth root hydrology가 식생 차이로 변환한다.
2. hotfix10n10 reduced classification이 native mixed BIOME4를 woody PFT 잠재 NPP의 51% 우점 기준으로 broadleaf/mixed로 구분한다.

PFT5/PFT6 온도범위 확장 자체는 Jang 검증구간의 성능 향상 주원인이 아니다.

## 1. 점수 차이의 구간별 분해

1% 기준:

| 기록 | 원본 dynamic | 수정형 dynamic | 차이 |
|---|---:|---:|---:|
| 95_01, 5.9-4.8 ka, 낙엽활엽수림 | 0/12 | 12/12 | +12 |
| 95_02, 4.8-3.4 ka, 혼효림 | 15/15 | 9/15 | -6 |
| 95_03, 3.4-0.39 ka, 낙엽활엽수림 | 0/31 | 31/31 | +31 |
| 95_04, 0.39-0 ka, 혼효림 | 4/4 | 3/4 | -1 |
| 합계 | 19/62 | 55/62 | +36 |

순증가 36개 가운데 가장 큰 항목은 95_03의 +31이다.

## 2. 95_03에서 dynamic이 결정적인 이유

모델 유역은 298셀이고 20 m 격자이므로 셀당 400 m2, 총면적은 119,200 m2이다.

1% 기준은 1,192 m2이므로 실제 격자 판정에서는 **3셀 = 1,200 m2 = 1.0067%**부터 통과한다.

수정형 dynamic에서 3.4-0.4 ka의 broadleaf 셀 수는 4-10셀, 즉 1.34-3.36% 범위로 모든 100년 시점에서 1%를 넘는다.

예:
- 3.4 ka: 10/298 = 3.36%
- 2.2-2.0 ka: 4/298 = 1.34%
- 0.4 ka: 5/298 = 1.68%

따라서 95_03의 31개 시점이 전부 정답이 된다.

## 3. broadleaf 패치는 어디에 생기는가

3.4 ka 수정형 dynamic snapshot:

- broadleaf 10셀
- broadleaf 셀 토심 평균 0.181 m
- 범위 0.037-0.305 m
- 나머지 mixed 288셀 토심 평균 2.395 m

0.4 ka:

- broadleaf 5셀
- broadleaf 셀 토심 평균 0.089 m
- 범위 0.044-0.199 m
- mixed 293셀 토심 평균 2.529 m

즉 broadleaf 출현은 임의의 위치가 아니라 **동적 지형발달로 극히 얕아진 토양 셀**에 집중된다.

## 4. 왜 원본 BIOME4에서는 같은 얕은 토양이 mixed로 남는가

3.4 ka의 동일한 dynamic 지형상태를 두 식생코어에 다시 넣어 비교했다.

원본 BIOME4:
- native full biome: 298/298 모두 biome 7
- reduced class: 298/298 모두 mixed
- PFT5 climate constraint pass: 0/298
- PFT6 pass: 298/298

수정형:
- native full biome 4: 4셀
- native full biome 7: 294셀
- reduced broadleaf: 10셀
- mixed: 288셀
- PFT5 pass: 298/298
- PFT6 pass: 298/298

가장 얕은 0.037 m 셀에서:
- 원본: full biome 7, NPP 약 500
- 수정형: full biome 4, NPP 약 353

수정형은 실제 토심을 McKenzie/Jackson finite-depth root weights에 넣어 root-accessible water를 제한한다. 그래서 극히 얕은 셀에서 PFT 경쟁과 native biome 자체가 바뀐다.

## 5. 51% mixed 재분류 효과

5.9 ka의 static 상태에서는 원본과 수정형의 총 NPP가 정확히 같고 native full biome도 모두 7이다.

그러나 broadleaf 최대 잠재 NPP 비율이 약 51.24%라서:
- 원본 reduced mapping: native biome 7을 mixed로 유지
- 수정형: 51% 기준을 넘으므로 broadleaf로 재분류

그 결과 95_01에서 수정형은 12/12를 얻는다.

반대로 이 규칙은 혼효림이 기대되는 95_02와 95_04 일부 시점에서는 손실을 만든다. 따라서 분류 규칙은 무조건 점수를 높이는 보정이 아니라 시점에 따라 득실이 있다.

## 6. PFT5/PFT6 온도조절은 주원인이 아님

정적 5.9-0 ka 전체에서 원본과 수정형의 mean NPP와 mean EEMT는 시간별로 동일했다.

대표적으로:
- 원본 PFT5는 native TCM 제한 때문에 constraint pass=0
- 수정형 PFT5는 확장 범위 때문에 pass=1
- 그러나 PFT6는 원본에서도 전 셀 pass
- 실제 우점/총 NPP가 변하지 않아 static 생태생산성 결과는 동일

따라서 현재 CHELSA21K/Jang 구간에서 PFT5/PFT6 온도범위 확장은 88.71%의 직접 원인이 아니다.

## 7. 지형 자체가 수정형에서 크게 달라진 것도 아님

3.4 ka의 실제 original dynamic과 modified dynamic 상태 비교:

- 평균 토심 차이: 약 +0.00105 m
- 평균 고도 차이: 약 -0.00041 m
- 최대 국지 토심 차이: 약 0.131 m
- 최대 국지 고도 차이: 약 0.283 m

따라서 수정형의 높은 점수는 전 유역 지형을 전혀 다른 형태로 만들어서가 아니다.

**두 dynamic run 모두 비슷한 지형 이질성을 만들지만, 수정형 BIOME4가 얕은 토양의 생태적 효과를 명시적으로 읽어 식생 차이로 변환한다는 점이 핵심이다.**

## 8. 최종 해석

수정형 dynamic의 높은 Jang 일치도는 다음 연결에서 나온다.

```text
21 ka부터 누적된 지형발달
-> 공간적으로 매우 얕은 토양 패치 형성
-> McKenzie AWC + Jackson finite-depth roots
-> 얕은 토양에서 PFT 수분 접근성과 NPP 경쟁 변화
-> 일부 셀이 broadleaf/native biome 4로 전환
-> 1% 유역 출현 기준 통과
-> 95_03 31/31
```

여기에 51% dominance reduced classification이 95_01을 broadleaf로 인식하게 해 +12를 추가하지만, 95_02와 95_04에서는 일부 점수를 잃는다.

따라서 이 결과는 "침엽수 온도보정이 잘 맞아서"라기보다 **토심-수문-뿌리 coupling과 동적 지형의 공간 이질성을 식생분류가 포착해서** 좋아진 것으로 해석하는 것이 맞다.
