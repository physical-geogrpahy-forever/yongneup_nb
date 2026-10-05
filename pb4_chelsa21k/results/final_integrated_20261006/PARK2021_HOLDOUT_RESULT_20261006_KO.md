# Park et al. (2021) 독립 holdout 검증 결과

작성일: 2026-10-06  
대상 모델: **PB4-FINAL-nativeClimate-BIOME4AGB**  
최종 canonical SHA-256: `a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34`

## 1. 실제 사용한 Supplementary

사용자가 이미 제공한 Park et al. (2021) Supplementary Excel을 직접 사용하였다.

- 파일: `1-s2.0-S0031018221004909-mmc1(1).xlsx`
- SHA-256: `6d4ad8310434e02e1f963ee36932e30ae66f757d6028260d33ea98e7359c8f97`
- pollen counts: 72 samples
- pollen percents: 72 samples, 16-88 cm, 515-3181 cal yr BP
- temperature reconstruction: 16-69 cm
- PCA: 16-69 cm

이 자료는 누락된 것이 아니며, 2026-10-06 현재 Park 독립검증에 실제 사용한 source로 고정한다.

주 정량 holdout은 Park et al. (2021)이 완전히 발달한 peatland 이후로 구분한 **16-69 cm, 515-2072 cal yr BP** 구간만 사용하였다. 이 구간의 53 pollen samples를 원 연대에 따라 가장 가까운 100년 PB4 output window에 배정하여 17개 window로 집계하였다. 시료 사이 보간은 하지 않았다.

## 2. 비교변수

pollen conifer group:

- Pinus
- Abies
- Picea
- Tsuga
- Cupressaceae

broadleaf woody group은 Group A의 나머지 woody taxa를 사용하되 Ephedra는 conifer+broadleaf closure에서 제외하였다.

pollen broadleaf fraction:

[
F_{broad,pollen}
=
rac{P_{broad}}
{P_{broad}+P_{conifer}}
]

모델의 cold-tree group은 기존 PB4 reduced mapping과 일관되게 PFT5, PFT6, PFT7을 사용하고, temperate-deciduous group은 PFT2, PFT3, PFT4를 사용하였다.

[
F_{cold,model}
=
rac{N_5+N_6+N_7}
{N_2+N_3+N_4+N_5+N_6+N_7}
]

[
F_{tempdec,model}=1-F_{cold,model}
]

pollen percentage와 model cell fraction은 동일한 물리량으로 보지 않았으므로 절대 RMSE를 주 통계로 사용하지 않았다.

## 3. Park PC2의 내부 검증

Park Supplementary의 PC2와 pollen-based reconstructed temperature를 동일한 100년 window로 집계하였다.

- Spearman rho = **-0.865**
- p = **7.32 × 10^-6**
- n = **17**

즉 Supplementary 자체에서도 PC2가 증가할수록 reconstructed temperature가 감소하여, Park 논문에서 제시한 cold-warm vegetation axis가 명확히 재현된다.

## 4. Park cold-warm vegetation signal과 PB4 비교

Park PC2와 모델의 cold-tree PFT fraction을 비교하였다.

### dynamic

- Spearman rho = **+0.632**
- p = **0.00644**
- n = **17**

### static

- Spearman rho = **-0.255**
- p = **0.323**
- n = **17**

따라서 Park의 독립 Late Holocene pollen PCA에서 나타나는 cold-warm vegetation direction은 **dynamic PB4에서 유의한 같은 방향의 관계**를 보였고 static에서는 재현되지 않았다.

Park 자료는 현재 모델의 파라미터 조정에 사용하지 않았으므로 이 결과는 Jang 주 검증과 독립적인 holdout 결과이다.

다만 dynamic의 cold-tree cell fraction 자체는 약 1.0-1.3%로 작다. 따라서 이 결과는 **변화 방향과 순위의 일치**를 지지하는 것이지 변화 진폭까지 재현했다는 뜻은 아니다.

## 5. broadleaf-conifer 조성 비교

100년 window의 pollen broadleaf fraction과 모델 temperate-deciduous tree fraction을 비교하였다.

### dynamic

- Spearman rho = **+0.448**
- p = **0.0713**
- n = **17**

### static

- Spearman rho = **+0.255**
- p = **0.323**
- n = **17**

dynamic은 양의 관계를 보이지만 0.05 기준에서 유의하지 않았다.

절대 조성은 다음과 같다.

- Park pollen broadleaf fraction mean = **0.669**
- Park 100년-window range = **0.593-0.745**
- dynamic PB4 temperate-deciduous fraction mean = **0.988**
- dynamic range = **0.987-0.990**
- static mean = **0.9996**

따라서 fine-scale broadleaf/conifer composition의 절대크기를 재현했다고 주장해서는 안 된다. pollen productivity와 dispersal 차이 때문에 pollen fraction과 model area fraction을 직접 일치시키는 것도 적절하지 않다.

## 6. 2738-2206 cal yr BP open-vegetation event

Park Supplementary의 77-71 cm, 2738-2206 cal yr BP 구간에서는 arboreal pollen 감소와 herb 증가가 뚜렷하다.

해당 7 samples:

- Trees and Shrubs mean = **55.99%**
- range = **43.31-70.78%**
- Herbs mean = **38.25%**
- Ferns mean = **5.76%**

동일한 2.2-2.7 ka에서 최종 dynamic PB4의 dominant PFT는 PFT4, PFT6, PFT7에 한정되며 PFT8-PFT13 open/herbaceous PFT는 출현하지 않는다.

따라서 이 open-vegetation event는 PB4가 **open vegetation으로는 재현하지 못한다**. 일부 시점의 PFT6 증가는 cold-tree response이지만 Park에서 관찰된 arboreal decline과 herb expansion을 대체하지 못한다.

이 구간은 peatland 완전 발달 이전 Zone 1이므로 주 정량 holdout score에는 포함하지 않고 명시적 limitation으로 보고한다.

## 7. 최종 판정

Park holdout은 다음처럼 해석한다.

1. **dynamic feedback에 대한 독립 지지**
   - Park PC2 vs dynamic cold-tree fraction: rho=0.632, p=0.00644
   - static에서는 유의한 관계 없음

2. **fine-scale 조성 재현은 제한적**
   - pollen broadleaf fraction vs dynamic model fraction: rho=0.448, p=0.0713
   - 절대 조성은 모델이 훨씬 더 temperate-deciduous dominant

3. **peatland/open vegetation process는 미재현**
   - 2738-2206 cal yr BP의 arboreal decline/herb expansion을 open PFT로 재현하지 못함

따라서 Park et al. (2021)은 Jang과 같은 accuracy score에 합치지 않는다. 논문에서는 **dynamic climate-vegetation response의 방향을 독립적으로 지지하는 동시에, local peatland/open-vegetation representation의 한계를 보여주는 holdout 검증**으로 제시한다.

이 결과를 이용해 최종 PB4를 재보정하지 않는다.
