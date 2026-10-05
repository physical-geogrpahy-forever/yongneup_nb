# Pelletier coupling range audit for AGB bridge candidates

Date: 2026-10-05

## Source check

Pelletier et al. (2013), JGR Earth Surface, DOI 10.1002/jgrf.20046:

- observed AGB across the Santa Catalina and Pinaleno Mountains rises from a few kg dry m-2 to approximately 60 kg m-2 and 75 kg m-2, respectively.
- model EEMT experiments use 5-45 MJ m-2 yr-1.
- the colluvial transport coefficient uses a linear superposition of EEMT and AGB:
  kd = c EEMT + d AGB
- c = 0.033
- d = 0.05
- coefficients were chosen to give kd approximately 0.3 m kyr-1 at low elevation and approximately 3 m kyr-1 at high elevation, consistent with literature transport estimates.

## Yongneup candidate range

### AGB

Full 21-0 ka runs:
- JULES-LAI candidates: absolute AGB maximum about 11.2 kg m-2
- Xue/IBIS candidate: absolute AGB maximum about 20.7 kg m-2
- Xue/IBIS 0 ka domain mean: 17.564 kg m-2

Therefore neither AGB bridge extrapolates beyond the AGB magnitude observed in the original Pelletier calibration landscape. Even the IBIS maximum is far below the original approximately 60-75 kg m-2 high-elevation observations.

### EEMT

PB4-McKenzie-nativeClimate at 0 ka:
- mean EEMT about 93.33 MJ m-2 yr-1

This exceeds the Pelletier model experiment range of 5-45 MJ m-2 yr-1. The current code intentionally does not clip EEMT.

Thus the larger empirical extrapolation in the present Yongneup application is the EEMT term, not the revised AGB term.

## kd contribution at 0 ka

Using c=0.033 and d=0.05:

EEMT contribution:
- 0.033 * 93.33 = about 3.08 m kyr-1

JULES-LAI-IPCCCF:
- AGB about 8.75 kg m-2
- AGB contribution about 0.44 m kyr-1
- total kd about 3.52 m kyr-1
- AGB fraction about 12%

Xue/IBIS:
- AGB about 17.56 kg m-2
- AGB contribution about 0.88 m kyr-1
- total kd about 3.96 m kyr-1
- AGB fraction about 22%

The IBIS bridge materially strengthens the vegetation-driven transport term, but does not make AGB the dominant source of kd at 0 ka; EEMT remains dominant.

## Decision implication

The Xue/IBIS bridge should not be rejected on the grounds that its AGB magnitude exceeds the Pelletier source calibration range. It does not.

However, the Pelletier c*EEMT term is already extrapolated beyond the source experiment range in Yongneup. This limitation is independent of whether the AGB bridge is JULES or IBIS and should be documented separately in the manuscript/model limitations.

Primary source:
Pelletier, J. D., et al. (2013). Coevolution of nonlinear trends in vegetation, soils, and topography with elevation and slope aspect: A case study in the sky islands of southern Arizona. Journal of Geophysical Research: Earth Surface, 118, 741-758. https://doi.org/10.1002/jgrf.20046
