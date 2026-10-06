# Park et al. (2021) 독립 holdout 검증 결과

작성일: 2026-10-06
대상 모델: **PB4-FINAL-nativeClimate-BIOME4AGB-U008**
최종 canonical SHA-256: `0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4`

## 자료 및 원칙

사용자가 제공한 Park et al. (2021) Supplementary Excel의 pollen, PCA, temperature reconstruction을 사용하였다. 주 정량구간은 16-69 cm의 53 pollen samples이며, 원 연대에 따라 가장 가까운 100년 PB4 output window에 배정하여 17개 window로 집계하였다. 시료 사이 보간은 하지 않았고 이 자료를 모델 재보정에 사용하지 않았다.

## PC2 cold-warm signal

- dynamic: Spearman rho = **0.754**, p = **0.00047466**, n = 17
- static: Spearman rho = **-0.255**, p = **0.32296**, n = 17

## broadleaf-conifer signal

- dynamic: Spearman rho = **0.427**, p = **0.087253**, n = 17
- static: Spearman rho = **0.255**, p = **0.32296**, n = 17
- dynamic temperate-deciduous fraction mean = **0.987762**
- range = **0.986577-0.989933**

## 2738-2206 cal yr BP open-vegetation event

2.2-2.7 ka의 dynamic PB4에서 PFT8-PFT13 dominant-cell 총계는 **0**이다.

## 판정

Park et al. (2021)은 Jang accuracy score에 합치지 않는 독립 holdout이다. U를 0.08 m kyr^-1로 교정한 production 결과로 위 통계를 다시 산출하였다.
