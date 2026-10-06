# PB4Studio CHELSA21K U008 패키지 전면 감사

작성일: 2026-10-06

감사 대상 패키지 SHA-256:

\`4b7be121d6d427a5378eb1aab491781f20a1557ee7d646acbef512d230356fd8\`

모델 버전:

\`6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB-U008\`

## 1. 결론

GUI 고식생 검증에 표시된 \`정적 19/86 = 22.1%\`, \`동적 50/86 = 58.1%\`는 최종 생산 검증값이 아니다. 패키지 런타임 validation 자료가 최종 논문 검증체계와 불일치한 상태로 남아 있었기 때문에 발생한 재현성 결함이다.

최종 주 검증은 Jang et al. (2011)만 사용하고, corrected reduced mapping과 유역 내 1% 출현 기준을 적용한 62개 output-time 평가이다.

- 정적모델: 24/62 = 38.709677%
- 동적모델: 55/62 = 88.709677%

Park et al. (2021)은 독립 holdout이며 Jang 62개 주 정확도에 합산하지 않는다.

## 2. 86이라는 분모가 생긴 원인

기존 패키지의 \`pb4studio/embedded_data/nationwide_validation.csv\`에는 용늪 위치에서 Jang 2011 record와 Park 2021의 legacy categorical record가 동시에 들어 있었다. runner는 공간범위로 자동 필터링했기 때문에 둘을 같은 categorical validation으로 읽었다.

0.1 kyr output 기준:

- Jang 2011 = 62개
- Park 2021 legacy categorical record = 24개
- 합계 = 86개

따라서 GUI의 분모 86은 \`62 + 24\`로 정확히 설명된다.

## 3. Jang mapping도 legacy 상태였음

기존 embedded mapping:

- 95_01 = 혼효림
- 95_02 = 침엽수림
- 95_03 = 활엽수림
- 95_04 = 침엽수림

최종 corrected reduced mapping:

- 95_01 = 활엽수림
- 95_02 = 혼효림
- 95_03 = 활엽수림
- 95_04 = 혼효림

따라서 Park 24개를 제거하기만 해도 충분하지 않고, Jang mapping도 반드시 함께 수정해야 한다.

## 4. GUI 화면값 완전 재현

기존 최종 211시점 결과에 패키지의 legacy Jang mapping과 Park categorical record를 적용하면:

### 정적모델

- Jang legacy = 0/62
- Park legacy = 19/24
- 합계 = 19/86 = 22.093023%

### 동적모델

- Jang legacy = 31/62
- Park legacy = 19/24
- 합계 = 50/86 = 58.139535%

사용자 GUI 화면의 19/86, 50/86과 정확히 일치한다. 즉 단순 표시 오류가 아니라 옛 검증자료와 옛 mapping을 실제 계산한 값이다.

## 5. corrected Jang 회귀값

동일한 최종 211시점 결과에 corrected Jang mapping만 적용하면:

### 정적모델

- 95_01 = 12/12
- 95_02 = 9/15
- 95_03 = 0/31
- 95_04 = 3/4
- 합계 = 24/62 = 38.709677%

### 동적모델

- 95_01 = 12/12
- 95_02 = 9/15
- 95_03 = 31/31
- 95_04 = 3/4
- 합계 = 55/62 = 88.709677%

이는 \`FINAL_JANG1PCT_SUMMARY.csv\`와 일치한다.

## 6. 함께 발견한 패키지 결함

1. 표준 결과판 시점이 \`100/50/10/1 ka\`로 남아 있어 21 ka 패키지에서 자동 생성이 실패할 수 있었다. \`21/10/5/0 ka\`로 수정한다.
2. GUI raw snapshot 기본 간격이 5 kyr라 전 211시점 raw 출력 요구와 맞지 않았다. 기본값을 0으로 바꾸어 매 output-time 저장으로 수정한다.
3. \`CHECK_CHELSA21K_CONTRACT.bat\`이 배포 ZIP에 없는 옛 test script를 호출했다. 새 \`tools/check_package_contract.py\`로 대체한다.
4. \`MAKE_STANDARD_RESULT_FIGURES.bat\` 기본 출력경로가 옛 \`outputs_hotfix10n10_selfcontained\`였다. \`outputs_CHELSA21K\`로 수정한다.
5. FULL EXPORT batch가 Windows에서 bare \`python\`만 호출했다. \`py -3\` 우선, 없으면 \`python\` fallback으로 수정한다.
6. 배포 ZIP의 plot script가 repository 전용 경로를 참조해 ZIP 단독으로 실행되지 않았다. 패키지 내부 실제 input/output 경로로 수정한다.
7. legacy input, 사용하지 않는 옛 climate/grid, 과거 Fortran build directory, pycache/pyc가 배포 ZIP에 남아 있었다. 제거한다.
8. \`validation.py\`에 옛 \`66/86, 41/86, 39/86\` validation lineage 주석이 남아 있었다. 최종 Jang n=62 체계로 수정한다.
9. config의 EEMT clip 및 NPP->AGB legacy serialization field가 실제 production science처럼 읽힐 수 있었다. field는 호환성을 위해 유지하되 production에서는 사용하지 않는다고 명시한다.

## 7. 변경하지 않는 과학 핵심

이번 수정은 validation, GUI/리포트 계약, 실행경로, 배포정리 수정이며 다음 science equations/settings는 변경하지 않는다.

- regional uplift U = 0.08 m/kyr
- hillslope critical slope Sc = 1.50
- K0 = 0.020
- CHELSA native climate, 추가 lapse correction 없음
- EEMT에 1--80 clip 없음
- Reich leaf + Haxeltine/Prentice sapwood 기반 AGB*
- kd = 0.033 EEMT + 0.05 AGB*
- 51% reduced vegetation class rule
- 21.0--0.0 ka BP, 0.1 kyr interval

## 8. 감사 패키지 계약

수정 패키지는 다음을 자동 검사한다.

- 버전 = U008
- uplift = 0.08 m/kyr
- Sc = 1.50
- standard ages = 21, 10, 5, 0 ka
- primary validation record = 95_01..95_04만
- corrected expected code = 1,2,1,2
- Park 92_* record가 primary validation에 없음
- 고도/토심/NPP figure code는 21 -> 0 ka, firebrick/royalblue CHELSA 형식
- 핵심 실행 및 export script 존재

재현 builder:

\`pb4_chelsa21k/tools/audit_fix_package_v4.py\`
