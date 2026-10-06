# PB4 final integrated production result

Final SHA-256: 0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4

## Scientific configuration

- BIOME4 v4.2b2 native PFT climate limits
- McKenzie AWC and finite-depth root coupling
- BIOME4-derived AGB*
- Pelletier geomorphic coupling with kd=0.033 EEMT + 0.05 AGB*
- regional uplift U=0.08 m kyr^-1 = 80 mm kyr^-1, Lee et al. (2024) 기반
- U는 용늪 직접 측정값이 아니라 regional background forcing을 위한 모델 가정

## Primary Jang validation

- static: 24/62 = 38.7097%
- dynamic: 55/62 = 88.7097%

## 21 ka dynamic geomorphic change

- mean elevation: 1163.077482 -> 1163.845503 m
- change: +0.768020 m
- mean soil depth: 1.940388 -> 2.499603 m
- change: +0.559216 m

## AGB*

- dynamic time mean: 3.116480679 kg m^-2
- dynamic modern 0 ka: 3.467422244 kg m^-2
- static time mean: 3.199793926 kg m^-2
- static modern 0 ka: 3.483490511 kg m^-2

## Park et al. (2021)

- PC2 vs dynamic cold-tree fraction: rho=0.754, p=0.00047466
- PC2 vs static cold-tree fraction: rho=-0.255, p=0.32296
- broadleaf pollen vs dynamic temperate-deciduous fraction: rho=0.427, p=0.087253
- Park 자료는 독립 holdout이며 모델 재보정에 사용하지 않음
