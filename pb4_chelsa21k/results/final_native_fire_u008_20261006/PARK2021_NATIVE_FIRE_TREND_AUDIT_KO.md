# Park et al. (2021) vs BIOME4 native firedays 추세 감사

업데이트: 2026-10-06

## 목적

최종 production인 `PB4Studio 6.6.3-CHELSA21K-FINAL_NATIVE_FIRE_U008`의
BIOME4 v4.2b2 native fire signal이 Park et al. (2021)의 용늪 macrocharcoal 화재기와
시간적으로 정합적인지 확인한다.

이 비교는 Park 기록을 이용해 fire threshold를 보정하는 calibration이 아니라
**이미 고정된 원본 BIOME4 fire module에 대한 독립적 과정 검증**이다.

## Park et al. (2021) 관측

Park et al.은 용늪 YN-C core에서 두 개의 뚜렷한 후기 홀로세 화재기를 보고하였다.

- ca. **2.9–2.7 ka BP**
- ca. **2.4–2.3 ka BP**

논문은 77–71 cm, 2738–2206 cal yr BP에서 arboreal pollen 감소와
Poaceae 및 Artemisia 증가를 보고하고, 두 macrocharcoal peak의 charcoal abundance를
235.2 및 200.0 counts mL^-1로 제시한다.

저자 해석은 두 화재기가 건조하고 바람이 강한 겨울-봄 조건과 관련되었을 가능성이 크다는 것이다.

## U008 dynamic native fire 결과

Park 비교에 가장 직접적인 진단량으로 PFT6의 **공간 최대 firedays**를 사용한다.
Park charcoal은 용늪 주변의 국지적 화재를 기록하므로, 유역 전체 평균 firedays보다
얕은 토심 fire-prone cell의 최대값 또는 임계값 초과 면적이 더 적절한 비교량이다.

| ka BP | max PFT6 firedays (d yr^-1) | Park 주요 화재기 |
|---:|---:|:---:|
| 3.2 | 103 | |
| 3.1 | 111 | |
| 3.0 | 109 | |
| 2.9 | 116 | O |
| 2.8 | 119 | O |
| 2.7 | **134** | O |
| 2.6 | 118 | |
| 2.5 | 119 | |
| 2.4 | 120 | O |
| 2.3 | 124 | O |
| 2.2 | 104 | |
| 2.1 | **129** | |
| 2.0 | 108 | |

## 패턴 평가

첫 번째 Park 화재기에는 PFT6 최대 firedays가
`116 -> 119 -> 134 d yr^-1`로 증가하여 **2.7 ka에서 국지 최대값**을 보인다.

그 뒤 2.6–2.5 ka에는 118–119일로 약화되었다가,
두 번째 Park 화재기인 2.4–2.3 ka에 `120 -> 124 d yr^-1`로 다시 상승하고,
2.2 ka에는 104일로 감소한다.

따라서 3.2–2.0 ka 범위에서는 다음 형태를 보인다.

```text
상승
 -> 2.9–2.7 ka 1차 고점
 -> 일시 약화
 -> 2.4–2.3 ka 재상승
 -> 2.2 ka 급락
```

이는 Park et al.의 두 주요 화재 episode와 **대체로 같은 시간 구조**이다.

탐색적 수치 비교:

- Park 화재구간 5개 100년 시점의 max PFT6 firedays 평균: **122.6 d yr^-1**
- 같은 3.2–2.0 ka 범위의 나머지 8개 시점 평균: **112.625 d yr^-1**
- 차이: **+9.975 d yr^-1**
- Park 화재구간 여부와 max PFT6 firedays의 point-biserial correlation: **r = 0.542**

이 통계는 n=13의 소표본 탐색값이며 독립적인 유의성 검정이나 calibration 지표로 사용하지 않는다.

## 불일치와 한계

완전한 일대일 대응은 아니다.

가장 뚜렷한 false-positive 후보는 **2.1 ka**로,
Park의 두 주요 화재기에 포함되지 않지만 max PFT6 firedays가 **129 d yr^-1**까지 상승한다.

또한 native firedays는 실제 화재 발생 횟수나 CHAR와 동일한 변수가 아니다.
이는 BIOME4 수분수지에서 계산된 **potential fire-days climate/hydrology signal**이다.
따라서 Park의 macrocharcoal peak magnitude와 직접적인 절대값 회귀를 수행하지 않는다.

## 강수 해석

화재신호는 연강수량 하나에 단순 비례하지 않는다.
예를 들어 2.8 ka의 연강수량은 1952 mm임에도 max PFT6 firedays는 119일이다.

따라서 후기 홀로세 화재를 단순한 연강수 감소로 설명하지 않고,
BIOME4의 계절별 기후, 토양수분수지, AET, 토심 및 PFT별 수분이용이 결합된 결과로 해석한다.
이는 Park et al.이 두 주요 화재기를 건조하고 바람이 강한 겨울-봄 조건과 연결한 해석과도
방향적으로 정합적이다.

## static vs dynamic

동일한 기후 forcing에서 static은 깊은 고정 토심 때문에 PFT4/PFT6/PFT7의 firedays가
3.5–2.0 ka 동안 0일로 유지된다.
반면 dynamic에서는 지형발달로 생성된 얕은 토심 cell에서 PFT6 firedays가
100일 이상으로 상승한다.

따라서 현재 결과는 다음 경로가 실제로 작동함을 보여준다.

```text
지형발달
 -> 공간적으로 얕은 토심
 -> 낮은 가용 수분 저장
 -> 높은 native firedays
 -> BIOME4 fire-sensitive competition
```

## 최종 판정

**부분적으로 강한 정합성이 있다.**

BIOME4 native fire signal은 Park et al. (2021)이 확인한
2.9–2.7 ka와 2.4–2.3 ka 화재기의 시간적 변동을 대체로 재현한다.
특히 첫 화재기에는 2.7 ka에서 최대값을 보이고,
두 번째 화재기에도 다시 상승한다.

다만 2.1 ka의 추가 고점 때문에 관측 화재기와 일대일 대응한다고 표현해서는 안 된다.

논문용 권장 표현:

> BIOME4의 native fire signal은 Park et al. (2021)이 보고한
> 2.9–2.7 ka 및 2.4–2.3 ka 화재기에서 상대적으로 높은 값을 보였으며,
> 특히 첫 화재기 말기에 최대값을 나타냈다. 다만 2.1 ka에도 높은 잠재 산불일수가
> 계산되어 관측 화재기와 완전한 일대일 대응은 나타나지 않았다.

## 관련 파일

- `NATIVE_FIRE_SPATIAL_3P5_2P0.csv`: static/dynamic native firedays 및 강수 진단 원자료
- `FINAL_NATIVE_FIRE_U008_DECISION_KO.md`: 최종 산불모듈 결정
