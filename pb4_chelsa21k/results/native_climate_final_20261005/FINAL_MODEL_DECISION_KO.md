# PB4 CHELSA21K final scientific configuration — 2026-10-05

## 결정

최종 과학모형은 **PB4-McKenzie-nativeClimate + BIOME4-derived AGB***로 고정한다.

식생과 토양-지형 설정은 다음을 유지한다.

- BIOME4 v4.2b2의 native PFT5/PFT6 climate limits
- McKenzie 토심별 AWC coupling
- Jackson 계열 PFT별 finite-depth root accessibility
- native mixed biome의 broadleaf/conifer reduced classification에서 대칭적 51% 과반 규칙
- dynamic Pelletier 식생-지형 coupling

AGB 항은 기존 0.010 x NPP를 폐기하고 다음 \(AGB^*\)를 사용한다.

\[
\boxed{
AGB^*_{\mathrm{dry},p}
=
LAI_p
\left[
S_p
+
0.03630780547701014\,L_{m,p}^{0.43}
\right]
}
\]

여기서 \(L_{m,p}\)는 BIOME4 v4.2b2 pftpar(pft,7)의 expected leaf longevity in months이고,

\[
S_p=
\begin{cases}
1, & pftpar(p,10)=1\\
0, & pftpar(p,10)=2
\end{cases}
\]

이다.

잎 항은 Reich et al. (1992)의 SLA-life-span 회귀식에서 유도하고, 변재 항은 Haxeltine and Prentice (1996) BIOME3 Eq. (34)와 BIOME4 v4.2b2 source parameter stemcarbon=0.5를 사용한다. \(f_C=0.50\)은 dry-mass conversion을 위한 명시적 모델 가정이다.

최종 Pelletier coupling은

\[
\boxed{
k_d
=
0.033\,EEMT
+
0.05\,AGB^*
}
\]

이다. Pelletier et al. (2013)의 직접적인 EEMT-to-AGB 지수식은 용늪에 사용하지 않는다.

## 전체 재실행 검증

동일 CHELSA-TraCE21k/EnviCloud forcing으로 21.0-0.0 ka BP, 0.1 kyr 간격의 static/dynamic 각각 211시점을 새 AGB* 식으로 다시 실행했다.

| 항목 | static | dynamic |
|---|---:|---:|
| 21 ka AGB* 시계열 평균 kg m-2 | 3.19979 | 3.11600 |
| 0 ka AGB* kg m-2 | 3.48349 | 3.46620 |
| 0 ka AGB* t ha-1 | 34.8349 | 34.6620 |
| Jang correct / 62 | 24 | 55 |
| Jang accuracy | 38.71% | 88.71% |

Jang et al. (2011) corrected reduced mapping, 유역 1% 출현 기준 정확도는 기존 nativeClimate baseline과 동일하다.

## 패키지 상태

기존 nativeClimate canonical ZIP SHA-256:

eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d

이 ZIP은 **AGB 변경 전 비교 baseline**으로 보존한다.

최종 선택된 AGB* 구현 candidate SHA-256:

1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c

구현 패키지:

pb4_chelsa21k/model_candidates/PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip

따라서 과학적 AGB 방식은 확정되었으며, 기존 canonical ZIP은 비교 baseline으로만 남긴다. 최종 배포 ZIP을 다시 패키징할 때는 이 AGB* 구현을 production package에 반영한다.

## 권위 문서

AGB 수식, 변수 정의, PFT별 파라미터, 참고문헌의 최종 기준은 다음 파일이다.

pb4_chelsa21k/manuscript/BIOME4_REICH_LAI_SAPWOOD_AGB_FINAL_METHOD_20261005_KO.md

## 참고문헌

Kaplan, J. O., et al. (2003). Climate change and Arctic ecosystems: 2. Modeling, paleodata-model comparisons, and future projections. *Journal of Geophysical Research: Atmospheres, 108*(D19), 8171. https://doi.org/10.1029/2002JD002559

Haxeltine, A., & Prentice, I. C. (1996). BIOME3: An equilibrium terrestrial biosphere model based on ecophysiological constraints, resource availability, and competition among plant functional types. *Global Biogeochemical Cycles, 10*(4), 693-709. https://doi.org/10.1029/96GB02344

Reich, P. B., Walters, M. B., & Ellsworth, D. S. (1992). Leaf life-span in relation to leaf, plant, and stand characteristics among diverse ecosystems. *Ecological Monographs, 62*(3), 365-392. https://doi.org/10.2307/2937116

Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. *Journal of Geophysical Research: Earth Surface, 118*, 741-758. https://doi.org/10.1002/jgrf.20046

BIOME4 v4.2b2 source code, Jed O. Kaplan: https://github.com/jedokaplan/BIOME4
