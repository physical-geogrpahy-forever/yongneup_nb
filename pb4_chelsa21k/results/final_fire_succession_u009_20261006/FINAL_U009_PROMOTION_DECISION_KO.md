# PB4 U009 native-fire succession 최종 승격 결정

업데이트: 2026-10-06

## 최종 결정

용늪 CHELSA21K production 식생-지형 결합모형의 코드 기준을
**PB4Studio 6.6.3-CHELSA21K-FINAL-FIRE-SUCCESSION-U009**로 승격한다.

U009의 원칙은 다음과 같다.

- BIOME4 v4.2b2의 native fire 계산과 native fire 임계값을 변경하지 않는다.
- 별도의 Park/Jang 연대 강제조건이나 기후 보정값을 사용하지 않는다.
- 현재 목본 우점 셀에서 native BIOME4가 계산한 fire signal이 원 경쟁식의 목본 임계값을 넘으면 fire event로 기록한다.
- 사용 임계값은 원 BIOME4 competition2의 PFT4 firedays > 180 d yr-1, PFT6 firedays > 90 d yr-1이다.
- fire event가 발생한 셀은 다음 0.1 kyr output step에서 post-fire open succession 후보가 된다.
- 이때 BIOME4 자체가 PFT8을 생리적으로 허용하고 PFT8 NPP와 LAI가 양수일 때만 PFT8 Temperate grassland를 실제 post-fire state로 채택한다.
- post-fire PFT8 상태에서는 NPP, LAI, AET, wetness, firedays, greendays를 같은 BIOME4 PFT8 계산결과에서 일관되게 사용한다.
- 다음 시점부터는 다시 BIOME4의 기후-토양 경쟁으로 목본 재진입이 가능하다. 연속 native fire event가 있으면 open state가 이어질 수 있다.

따라서 최종 결합 구조는 다음과 같다.

CHELSA climate + dynamic soil depth
→ BIOME4 soil-water balance
→ native firedays
→ native woody fire threshold
→ one-step post-fire PFT8 succession
→ NPP/AET/LAI/PFT
→ BIOME4-derived AGB*
→ EEMT
→ Pelletier geomorphic update
→ next 0.1 kyr state

## 제어실험

실제 CHELSA 후기 홀로세 기후와 동일한 조건에서 토심만 제어한 smoke test를 수행하였다.

- 토심 0.05 m: 약 2.7 ka에서 PFT6 firedays가 90일을 넘으며 native fire event가 발생하고, 다음 0.1 kyr step에서 PFT8 post-fire state가 정상적으로 활성화됨.
- 토심 1.5 m: 같은 후기 홀로세 구간에서 해당 fire event와 post-fire PFT8 전환이 발생하지 않음.
- PFT8 monthly AET 12개월 출력이 모두 유효하여 EEMT와 지형결합에도 동일 PFT 상태가 전달됨.

이 결과는 U009 전환이 특정 고식생 연대를 강제한 것이 아니라
**기후-토심-수분수지에서 계산된 BIOME4 native fire signal**에 의해 작동함을 확인한다.

## 정량 결과 상태

U009는 최종 production **코드 정의**로 승격한다.
다만 U009의 21-0 ka 전체 coupled dynamic 재실행은 별도의 장시간 계산이므로,
완료 전까지 기존 U008/FIREACTIVE의 정량 결과를 U009 결과로 재사용하지 않는다.

특히 다음 기존 값은 U009 검증값으로 인용하지 않는다.

- Jang static 24/62 = 38.71%
- Jang dynamic 55/62 = 88.71%

위 값은 U008/FIREACTIVE baseline이다.
U009의 최종 Jang 정확도, Park 후기 홀로세 PFT8 출현, NPP, AGB*, EEMT 및 지형 결과는
U009 전체 21-0 ka 재실행 산출물로 새로 확정한다.

## 배포 무결성

최종 로컬 배포 ZIP:

`PB4Studio_v6.6.3_CHELSA21K_FINAL_FIRE_SUCCESSION_U009.zip`

SHA-256:

`b41003b08f9591ca53a64cf33f1c2466fc85517a87fccd15613f2a815efe2520`

ZIP 무결성 검사를 통과하였다.
