# Pelletier Eq. (5) AGB candidate 21–0 ka 실행 결과

작성일: 2026-10-05

## 1. 실행 상태와 provenance

이 결과는 **새로 실행한 21–0 ka 전체 후보 실험**이다.

- GitHub Actions run: `37261755927`
- job: `111610259666`
- 실행 step: **success**
- 결과 저장 step: GitHub 원격 main에 다른 감사 작업 커밋이 먼저 들어와 non-fast-forward로 push만 실패
- 따라서 모델 실행 자체는 성공했으며, 아래 수치는 Actions 로그에 실제 출력된 값을 복구해 기록한다.
- baseline: `PB4-McKenzie-nativeClimate`
- baseline SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`
- candidate SHA-256: `3f632362aa9c18786a6e49b84bdd5f9a93653e52287d60ceb67593cffc5de7e8`
- climate: CHELSA-TraCE21k/EnviCloud, 21–0 ka BP, 0.1 kyr
- validation: Jang et al. (2011) corrected reduced mapping, n=62, 1% basin-presence criterion

## 2. 유일한 지형 coupling 변경

기존 잠정 최종 baseline:

[
AGB=0.010NPP
]

후보:

[
AGB=eexp(fEEMT)
]

Pelletier et al. (2013) Eq. (5)의 원 계수를 그대로 사용:

[
e=1 {m kg,m^{-2}},qquad
f=0.1 {m yr,m^2,MJ^{-1}}
]

용늪 재적합, AGB clipping, 임의 상한은 적용하지 않았다.

McKenzie AWC, finite-depth roots, native BIOME4 climate limits, 51% reduced-class rule, CHELSA forcing, Pelletier의 다른 지형계수는 유지했다.

## 3. Jang 1% 검증 결과

| 모델 | static | dynamic |
|---|---:|---:|
| 잠정 최종 baseline | 24/62 = 38.71% | **55/62 = 88.71%** |
| Pelletier Eq.(5) AGB candidate | 24/62 = 38.71% | **54/62 = 87.10%** |

따라서 Pelletier Eq. (5)를 그대로 복원하면 static은 동일하지만 dynamic은 1개 시점이 추가로 실패하여 55/62에서 54/62로 감소했다.

## 4. Wang et al. (2011) 독립 진단

Wang 진단은 지형계산에 넣지 않았다.

[
C_{m veg}=NPP,	au_{m veg}
]

단위는 kg C m^-2이며, Pelletier AGB의 kg live dry biomass m^-2와 동일한 변수로 취급하지 않았다.

Actions 로그의 211시점 요약:

| mode | Pelletier AGB, 시간별 유역평균의 평균 | 시간별 유역평균 최소–최대 | 전체 셀 절대최대 | Wang Cveg, 시간별 유역평균의 평균 | Wang 유역평균 최소–최대 |
|---|---:|---:|---:|---:|---:|
| static | 3414.11 kg m^-2 | 172.94–12836.98 | 13567.40 | 4.142 kg C m^-2 | 2.655–6.266 |
| dynamic | 3487.47 kg m^-2 | 153.43–13007.80 | 23991.11 | 3.780 kg C m^-2 | 2.372–6.171 |

## 5. 핵심 판정

**Pelletier Eq. (5)의 Arizona 계수를 현재 PB4 EEMT에 그대로 적용하는 후보는 물리적으로 기각해야 한다.**

이유:

1. Pelletier 원 연구에서 AGB는 대체로 수 kg m^-2에서 최대 약 60–75 kg m^-2 범위였다.
2. 현재 용늪 PB4 EEMT에 Eq. (5)를 그대로 적용하면 유역평균조차 최소 약 153–173 kg m^-2이고, 시간평균 유역평균은 약 3.4×10^3 kg m^-2에 달한다.
3. 셀 절대최대는 약 1.36×10^4 kg m^-2(static), 2.40×10^4 kg m^-2(dynamic)로 비현실적이다.
4. Wang BIOME4 vegetation-carbon 진단은 같은 실행에서 유역평균 약 2.4–6.3 kg C m^-2 규모이다. 단위와 정의가 달라 직접 동등비교할 수는 없지만, Pelletier Eq. (5)의 무보정 외삽이 비정상적인 규모라는 점은 명백하다.
5. Jang dynamic 정확도 역시 88.71%에서 87.10%로 소폭 악화되었다.

따라서 **현재 canonical baseline은 교체하지 않는다.**

## 6. 다음 단계

AGB 문제를 누더기식으로 해결하지 않기 위해 다음 비교는 두 체계로 제한한다.

1. 현재 baseline `AGB=0.010NPP`은 비교대조군으로만 보존
2. BIOME4 자체를 이용한 steady-state vegetation carbon 접근, 특히 Wang et al. (2011)의
   [
   C_{m veg}=NPP	au_{m veg}
   ]
   를 기반으로 Pelletier의 식생 지형효과 항을 어떻게 **일관된 하나의 재정의된 변수**로 바꿀 수 있는지 검토

Pelletier Eq. (5)의 (e,f)를 용늪 결과에 맞춰 임의 재보정하는 방법은 우선 채택하지 않는다. 그렇게 하면 단순 성능 맞춤이 될 위험이 있기 때문이다.

## 7. 주의

이번 workflow는 모델 실행과 결과파일 생성까지 성공했지만 마지막 push가 non-fast-forward로 실패했다. 원래 job workspace에서 생성된 상세 zone CSV와 211시점 원본 timeseries는 원격 저장소에 올라가지 못했다. 여기 기록한 수치는 Actions job log에 실제 출력된 요약값이며 추정값이 아니다.
