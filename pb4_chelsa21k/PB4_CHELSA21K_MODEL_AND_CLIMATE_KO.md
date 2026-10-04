# 용늪 PB4Studio CHELSA21K 모델 및 기후자료 설명

업데이트: 2026-10-04

## 1. 목적

이 디렉터리는 용늪 PB4Studio의 현재 기후 강제력과 모델 프로세스를 함께 보존한다. 이후 수행할 정적/동적 비교와 원본/수정형 BIOME4 비교는 여기 기록한 자료와 모델 버전을 기준으로 한다.

이 문서에는 과거 Beyer 실행이나 이전 hotfix의 정확도 값을 현재 결과처럼 재사용하지 않는다. 새로운 정확도는 반드시 아래 자료와 모델로 새로 실행한 뒤 보고한다.

## 2. 현재 기후자료

기본 원자료:

- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`
- 압축본: `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`
- 자료 계열: CHELSA-TraCE21k / EnviCloud
- 추출 위치: 용늪 약 128.122518 E, 38.214643 N
- 기간: 21.0 ka BP에서 0.0 ka BP
- 시간간격: 0.1 kyr, 즉 100년
- 시점 수: 211
- 테이블 크기: 211행 x 39열
- 결측값: 0
- 변수: 1월부터 12월까지 월별 Tmin, Tmax, 강수 원자료와 시간 필드

SHA-256:

- CSV: `3f5d249bb59f4163bb0f78f5cb4759972575931bf977b8b2791db497805b0ec9`
- ZIP: `b2e0d8d485c60d3f6bbaae95d88ec175ec1020eab86a7d6976ea66837d18703b`

### 온도와 강수 처리

원자료 온도는 Kelvin이다. PB4용 월평균 기온은 다음처럼 계산한다.

```text
Tmean_C = ((Tmin_K + Tmax_K) / 2) - 273.15
```

BIOME4 인터페이스의 연간 최저기온 입력은 Celsius로 변환한 월별 Tmin 가운데 최솟값을 사용한다.

강수는 이 저장소에서 원자료 값을 그대로 보존한다. PB4용 forcing 생성 단계에서 기준 기후와 대조하여 단위를 검증한 뒤 사용하며, 임의의 배율을 조용히 적용하지 않는다.

CHELSA21K 설정에서는 CHELSA 기온에 추가 고도감률 보정을 적용하지 않는다.

### 3300 BP 7월 복구 확인

3300 BP의 7월 Tmin/Tmax는 3200 BP 값을 복제한 것이 아니다. 현재 보존 원자료를 직접 확인한 값은 다음과 같다.

| 시점 | 7월 Tmin raw | 7월 Tmax raw | 7월 강수 raw |
|---:|---:|---:|---:|
| 3.3 ka BP | 287.0 | 294.5 | 362.0 |
| 3.2 ka BP | 287.0 | 295.9 | 366.0 |

이 검사는 이전 추출 과정에서 3300 BP 7월 온도자료 복구 문제가 있었기 때문에 기록한다.

## 3. 현재 PB4Studio 패키지

현재 CHELSA용 패키지명:

- `PB4Studio_v6.6.3_CHELSA21K.zip`

계보:

- PB4Studio v6.6.3
- hotfix10n10 기반 CHELSA fork
- CHELSA 21 ka branch와 Beyer 120 ka branch를 별도 유지

Beyer 비교용 패키지는 `PB4Studio_v6.6.3_BEYER120K.zip`이다. Beyer 결과와 CHELSA 결과를 같은 실행 결과처럼 섞지 않는다.

## 4. 결합 모델의 상태변수

PB4Studio는 BIOME4 식생계산과 Pelletier 계열 지형발달 계산을 결합한다.

```text
z(t) = 지표고도
b(t) = 기반암고도
H(t) = 토심/레골리스 두께 = z(t) - b(t)
```

동적 모형의 한 coupling step은 다음 순서로 진행한다.

```text
현재 z(t), b(t), H(t)
        |
        v
CHELSA 기후(t)
        |
        v
토양 수분저장량 + PFT별 유효 뿌리 접근성
        |
        v
BIOME4
기후 sieve -> PFT별 NPP/LAI 최적화 -> 경쟁 -> biome 판정
        |
        +--> NPP, AET, LAI, PFT/biome 결과
        |
        v
EEMT + AGB proxy
        |
        v
Pelletier 지형발달
토양생산/풍화 + 사면수송 + 하천침식 + 융기
        |
        v
새 z(t+1), b(t+1), H(t+1)
        |
        v
다음 100년 기후시점에서 BIOME4 재실행
```

지형 계산은 수치안정성을 위해 100년 구간 안에서 더 작은 adaptive substep을 사용할 수 있다. 그러나 그 내부 substep 하나하나가 별도의 기후시점은 아니다.

## 5. 토심에서 식생으로 가는 경로

현재 production 계보는 토심에 임의의 직접 생산성 배율을 적용하지 않는다. 예를 들어 `NPP *= f(H)`나 `LAI *= f(H)` 같은 보정식을 최종 경로에 두지 않는다.

과정은 다음과 같다.

```text
토심 H
  -> available-water storage
  -> PFT별 finite-depth root accessibility
  -> BIOME4 2층 토양수분수지
  -> 수분스트레스와 AET
  -> NPP와 LAI
  -> PFT 경쟁과 biome
```

BIOME4의 수문층은 다음 범위를 사용한다.

- 상층: 0에서 0.30 m
- 하층: 0.30에서 1.50 m
- BIOME4 유효 토심 상한: 1.50 m

용늪 production 계보의 McKenzie/SoilGrids AWC 프로파일은 실제 토심까지 적분한다. PFT별 유효 뿌리 접근성은 BIOME4/Jackson의 상부 30 cm 뿌리분율을 토대로 계산하며 용늪 화분자료에 맞춰 별도 계수를 보정하지 않는다.

## 6. 수정형 BIOME4 설정

CHELSA21K 패키지는 현재 비교에서 사용하는 hotfix10n10 수정형 BIOME4 계보를 따른다.

새 실행에서 유지해야 할 핵심은 다음과 같다.

- hotfix10n10 계보의 활성 PFT 경쟁 구조 유지
- PFT5 reference climate extension 유지
- PFT6의 Sitch/BoNE 계열 기후범위 확장과 후기 계보의 TWM 23 C 상한 유지
- 토심에 대한 직접 pollen-fit 생산성 계수 없음
- biome 판정은 BIOME4의 PFT 생산성과 경쟁 뒤에 이루어지며 단순한 최대 NPP 라벨이 아님

원본 BIOME4 대조군에는 이 수정형 PFT 기후한계나 후기 수정형 biome 재분류 규칙을 섞으면 안 된다.

## 7. 정적과 동적 모형

### 정적

지형과 토심을 고정한다.

```text
CHELSA(t) -> 고정 z,H -> BIOME4(t)
```

따라서 다음 시점 식생에 지형 피드백이 없다.

### 동적

지형과 토심을 갱신한다.

```text
CHELSA(t)
  -> z(t),H(t)
  -> BIOME4
  -> NPP/AET
  -> EEMT/AGB
  -> 지형변화
  -> z(t+1),H(t+1)
```

즉 식생, 수문, 토심, 지형이 함께 변화할 수 있다.

## 8. 원본 BIOME4 대조군

원본 대조군은 보존된 BIOME4 v4.2b2 식생방정식과 원래 기후제약을 사용해야 한다. PB4가 공간 토양상태를 전달하고 출력을 회수하는 데 필요한 I/O 연결은 유지할 수 있지만 수정형 PFT5/PFT6 기후한계와 후기 수정형 biome 판정은 원본 대조군에 들어가면 안 된다.

최종 비교 설계는 다음 4개이다.

| 식생 코어 | 지형모드 | 기후 forcing |
|---|---|---|
| 원본 BIOME4 v4.2b2 | static | 현재 CHELSA21K |
| 원본 BIOME4 v4.2b2 | dynamic | 현재 CHELSA21K |
| hotfix10n10 수정형 BIOME4 | static | 현재 CHELSA21K |
| hotfix10n10 수정형 BIOME4 | dynamic | 현재 CHELSA21K |

네 실행은 동일한 기후자료, DEM/토양영역, 시간축, 검증기준을 사용해야 한다.

## 9. 고식생 검증 규칙

현재 검증에서는 Jang과 Park를 분리한다.

### Jang et al. (2011)

범주형 100년 검증은 Jang의 네 기록만 사용한다.

- `95_01`
- `95_02`
- `95_03`
- `95_04`
- 총 62개 비교시점

Jang과 과거 Park categorical record를 합친 86개 정확도는 과거 참고값이며 현재 최종 검증 정확도로 사용하지 않는다.

### Park et al. (2021)

과거 Park 24개 categorical item을 Jang 총점에 넣지 않는다. Park는 Supplementary의 실측 화분자료를 100년 창으로 집계한 별도 검증으로 평가하며 보간하지 않는다.

## 10. 결과 보고 형식

앞으로 새 결과를 제시할 때는 수치보다 먼저 다음 네 항목을 반드시 적는다.

1. 사용한 데이터/forcing 파일명과 버전
2. 모델/코드 버전과 핵심 설정
3. 이번에 새로 실행한 결과인지 과거 참고값인지
4. 검증 대상, 표본 수, 판정기준

예시:

```text
데이터: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv, 21-0 ka, 100년 간격
모델: PB4Studio_v6.6.3_CHELSA21K, modified BIOME4, dynamic
실행: 이번 분석에서 새로 실행
검증: Jang et al. (2011)만 사용, n=62 categorical time points
결과: ...
```

과거 Beyer/hotfix 결과를 새 CHELSA21K 실행값 대신 사용하지 않는다.

## 11. 현재 보존 상태

이번 GitHub 업데이트에서 보존하는 것은 다음과 같다.

- 최신 CHELSA-TraCE21k/EnviCloud RAW WIDE 원자료
- 21에서 0 ka, 100년 간격 211시점
- 결측값 0 확인
- 원자료 SHA-256
- PB4 CHELSA21K 모델 프로세스와 비교 설계
- Jang/Park 검증 분리 규칙

이 문서에서 아직 주장하지 않는 것은 다음과 같다.

- 새 static/dynamic 정확도
- 새 original/modified BIOME4 정확도
- 과거 Beyer 결과가 CHELSA21K에도 그대로 적용된다는 주장

이 값들은 동일한 CHELSA21K forcing으로 네 실험을 새로 실행한 뒤 기록한다.

## 12. GitHub 보존 패키지

현재 실행 패키지 자체도 이 디렉터리에 보존한다. GitHub 저장 과정에서는 원본 ZIP 바이트를 base64 조각으로 나누어 저장하고 `reconstruct_pb4.py`로 원래 ZIP을 복원한다. 복원 뒤 SHA-256이 아래 값과 정확히 일치해야 한다.

- `PB4Studio_v6.6.3_CHELSA21K.zip`: `bc336bdc3232dcfb912cc8f4072565591714064c6446dfb28630f785ee90fb09`
- base64 조각 경로: `payload/PB4Studio_v6.6.3_CHELSA21K.zip.b64.part001`부터 `part012`

복원 예시:

```bash
python reconstruct_pb4.py
```

복원 스크립트는 조각을 파일명 순서대로 연결해 base64를 해독하고 ZIP SHA-256을 검증한다. 따라서 이후 분석에서는 파일명만 같은 다른 PB4 사본이 아니라 이 SHA가 일치하는 패키지를 사용한다.