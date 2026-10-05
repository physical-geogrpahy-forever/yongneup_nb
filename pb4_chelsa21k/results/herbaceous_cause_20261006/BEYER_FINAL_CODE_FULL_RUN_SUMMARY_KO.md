# Current final PB4 code with Beyer forcing: full 21 ka run summary

작성일: 2026-10-06

## 실험

최종 canonical PB4 code를 그대로 사용하고 climate forcing만 package 내부에 보존된 Beyer 월별 시계열로 교체하여 21.0-0.0 ka BP, 0.1 kyr 간격의 static/dynamic 전체 실행을 수행했다.

변경하지 않은 항목:

- BIOME4 v4.2b2 native climate limits
- McKenzie soil-depth/AWC coupling
- PFT별 finite-depth root accessibility
- BIOME4-derived AGB*
- Pelletier dynamic geomorphic coupling
- Jang validation mapping and 1% basin-presence criterion

Beyer long-format climate loader만 temporary copy에서 다시 활성화했다. canonical package 자체는 변경하지 않았다.

## 전체 실행 결과

전체 model execution은 정상 종료되었다.

Jang 1% validation:

| mode | correct | n | accuracy |
|---|---:|---:|---:|
| static | 19 | 62 | 30.65% |
| dynamic | **62** | 62 | **100.00%** |

주요 PFT occurrence:

| mode | PFT | positive timesteps | oldest ka | youngest ka | max cells |
|---|---:|---:|---:|---:|---:|
| dynamic | 4 | 1 | 0.0 | 0.0 | 38 |
| dynamic | 6 | 211 | 21.0 | 0.0 | 298 |
| dynamic | 7 | 198 | 20.6 | 0.0 | 26 |
| dynamic | **8** | **0** | - | - | **0** |
| dynamic | 12 | 0 | - | - | 0 |
| static | 4 | 1 | 0.0 | 0.0 | 67 |
| static | 6 | 211 | 21.0 | 0.0 | 298 |
| static | 7 | 0 | - | - | 0 |
| static | **8** | **0** | - | - | **0** |
| static | 12 | 0 | - | - | 0 |

## 핵심 해석

과거 Beyer 기반 5 cm 단일토심 sensitivity에서 PFT8 temperate grass가 선택되었던 것과 달리, **현재 final PB4의 실제 full spatial run에서는 Beyer forcing으로 되돌려도 PFT8이 한 시점도 우점하지 않았다.**

따라서 실제 full model에서 초본 소실을 단순히 `CHELSA forcing 때문`이라고 결론내릴 수 없다.

현재 남는 가능성은 다음과 같다.

1. 과거 Beyer PFT8은 매우 얕은 강제 토심 sensitivity에서만 나타났고 full dynamic spatial model의 실제 토심분포에서는 해당 competition state가 충분히 실현되지 않았을 가능성
2. final McKenzie finite-depth coupling과 현재 BIOME4 competition에서 PFT7/PFT6 tree dominance가 full spatial run에서 지속되는 구조
3. 과거 sensitivity와 현재 final code 사이의 implementation 차이

이를 분리하기 위해 current final code 자체에 Beyer forcing을 넣은 동일 depth sweep을 별도로 실행한다.

## 중요한 결론

현재까지의 full-run 증거만으로는 climate dataset을 Beyer로 되돌리는 것으로 temperate grass 문제를 해결할 수 없다.

또한 Beyer dynamic Jang score가 62/62라는 결과는 climate sensitivity로는 매우 중요하지만, 이 결과만을 근거로 현재 CHELSA production forcing을 폐기하지 않는다. forcing 선택은 자료 품질과 독립적인 과학적 근거를 기준으로 별도 판단한다.

## 실행 provenance

Successful full-run GitHub Actions job:
- workflow: `Run final PB4 with Beyer forcing`
- run: `37350582530`
- model execution step: success
- summarization step: success
- final repository push: concurrent main update로 rejected

따라서 위 수치는 successful run log에서 직접 회수한 결과이며, raw output archive는 별도 재실행 또는 재저장을 통해 보존한다.
