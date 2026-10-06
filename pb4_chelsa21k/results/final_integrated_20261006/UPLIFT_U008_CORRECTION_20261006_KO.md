# PB4 uplift U correction audit

- 2026-08-20 한국지형학회 발표 확정값: **80 mm kyr^-1 = 0.08 m kyr^-1**
- 근거: Lee et al. (2024), Earth Surface Dynamics 12, 1091-1120
- 이전 canonical 실제 기본값: 0.20 m kyr^-1
- 교정 production: **0.08 m kyr^-1**
- 이전 U020 SHA-256: `796faeae61fa00ca31512d3e087d6134dbdd01428beea760d79d184fa6481f86`
- 교정 U008 SHA-256: `0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4`

Jang static은 24/62, dynamic은 55/62로 변하지 않았다. 반면 dynamic 21 ka 평균고도 변화는 U020에서 +3.256468 m였고 U008에서는 +0.768020 m이다. 따라서 U는 식생 검증점수를 바꾸지 않았지만 지형 결과에는 실질적인 영향을 주므로 package와 Methods를 함께 교정하였다.

80 mm kyr^-1은 용늪에서 직접 관측한 지각융기율이 아니다. Lee et al. (2024)이 태백산맥의 약 22 Ma 이후 장기 삭박 및 exhumation rate에 맞추어 regional uplift forcing으로 사용한 값을 채택한 모델 가정이다.
