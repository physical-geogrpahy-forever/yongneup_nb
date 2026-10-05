# Current PB4 AGB source context

Canonical SHA-256: `eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d`

## `BIOME4_SD_MCKENZIE2003_MODEL_NOTE.txt` lines 5-17

```text
    5: Comparison path:
    6:   original BIOME4 v4.2b2
    7: 
    8: Soil-depth module:
    9:   McKenzie et al. (2003) profile AWC definition: theta(-10 kPa)-theta(-1.5 MPa)
   10:   SoilGrids Yongneup point: 128.1236 E, 38.2153 N
   11:   Jackson et al. (1996) exponential cumulative root distribution
   12:   BIOME4 native PFT top-30-cm root fractions
   13:   No direct soil-depth multiplier on NPP, LAI, FVC, or competition.
   14: 
   15: Important scope:
   16:   The soil-depth module is reference-derived and contains no fitted Yongneup vegetation coefficient.
   17:   The BIOME4<->Pelletier AGB bridge remains a separate unresolved full-model provenance issue.
```

## `FLUVIAL_ISSUE3_ADAPTIVE_TIMESTEP_AUDIT_2026-08-17.md` lines 12-36

```text
   12: 4. Accepted geomorphic `z/b/H` state is retained internally as float64 across substeps. This removes timestep-count-dependent float32 roundoff at ~1160 m elevations. Output and BIOME4 I/O may still use float32 at their existing boundaries.
   13: 5. Diagnostics now report rejected fluvial trials, accepted dt range, tolerance, and maximum accepted/trial fluvial change.
   14: 
   15: ## Why 0.025 m is the default
   16: Pelletier et al. (2013) describe dynamically reducing dt to limit per-step erosion/deposition and checking convergence by halving the threshold, but do not publish the numerical threshold used. Therefore 0.025 m is explicitly treated as a numerical tolerance, not a physical parameter or calibration coefficient.
   17: 
   18: Fluvial-only 1 kyr audit (hillslope disabled only in the audit harness):
   19: 
   20: | tolerance | accepted steps | accepted dt | max accepted fluvial change | H=0 cells |
   21: |---:|---:|---:|---:|---:|
   22: | 0.050 m | 80 | 0.0125 kyr | 0.0432903 m | 2 |
   23: | 0.025 m | 160 | 0.00625 kyr | 0.0216452 m | 2 |
   24: | 0.0125 m | 320 | 0.003125 kyr | 0.0108226 m | 2 |
   25: 
   26: Threshold-halving differences:
   27: 
   28: | comparison | max |ΔH| | p99 |ΔH| | max |Δz| | p99 |Δz| | bare-mask differences |
   29: |---|---:|---:|---:|---:|---:|
   30: | 0.050 → 0.025 m | 0.0430626 m | 0.00620888 m | 0.0439498 m | 0.00625624 m | 0 |
   31: | 0.025 → 0.0125 m | 0.0135511 m | 0.00189889 m | 0.0136663 m | 0.00193472 m | 0 |
   32: 
   33: Thus the 0.025→0.0125 halving changes 99% of cells by ~2 mm or less and the worst local difference by ~1.4 cm, with no change in the H=0 mask. 0.025 m is retained as the default numerical tolerance; 0.0125 m remains available for stricter convergence checks.
   34: 
   35: ## Reproducibility and rejection purity
   36: Fresh independent reruns reproduced:
```

## `MCKENZIE2003_REFERENCE_AUDIT_2026-08-17.md` lines 1-21

```text
    1: # BIOME4-SD McKenzie2003 reference audit — 2026-08-17
    2: 
    3: ## 1. Scope and status
    4: 
    5: This audit applies to the **soil-depth -> available-water storage -> root-accessibility** extension only.
    6: 
    7: Status: **reference-derived coupling; no empirical/fitted soil-depth coefficient introduced**.
    8: 
    9: This does **not** certify the entire BIOME4-Pelletier coupled model as assumption-free. In particular, the pre-existing BIOME4 NPP -> Pelletier AGB bridge remains a separate unresolved provenance issue and is not justified by McKenzie et al. (2003), Jackson et al. (1996), or SoilGrids.
   10: 
   11: At the time of this McKenzie-only audit, the pre-existing project climate settings were PFT5 TCM >= -8 degC and PFT6 TWM <= 22 degC. They are not part of the McKenzie soil-depth derivation. **hotfix10n5 supersedes only the PFT6 climate sieve with Sitch et al. (2003) BoNE (TCM -32.5..-2 degC, GDD5 >= 600, TWM <= 23 degC); PFT5 remains unchanged.**
   12: 
   13: ## 2. Reference inputs used
   14: 
   15: ### 2.1 McKenzie et al. (2003)
   16: 
   17: Reference:
   18: N. J. McKenzie et al. (2003), *Estimating Water Storage Capacities in Soil at Catchment Scales*, CRC for Catchment Hydrology Technical Report 03/3.
   19: 
   20: Directly used statements/equations:
   21: 
```

## `fortran_src/biome4_original_4_2b2.f` lines 2188-2212

```text
 2188:        real mstemresp(12),mrootresp(12),t0,respfact(13)
 2189:        real allocfact(13)
 2190:        real fpar(12),backleafresp(12),leafmaint
 2191: 
 2192: c       data (days(m),m=1,12) 
 2193: c     *   /  31.,28.,31.,30.,31.,30.,31.,31.,30.,31.,30.,31.  /
 2194: 
 2195: c      Grass defines if there is sapwood respiration
 2196: 
 2197: c      Ln  = Leaf litterfall per unit Leaf area index
 2198: c      m10 = Maintenance respiration of sapwood at 10oC, gC.month-1.KgC-1
 2199: c      k   = Extinction coefficient
 2200: c      y   = Efficiency with which carbon is turned into biomass
 2201: c      p1  = Fine root respiration to litterfall ratio
 2202: 
 2203: c      stemcarbon = sapwood mass as KgC.m-2(leaf area).m-2(ground area)
 2204:        parameter(Ln=50.,y=0.8,m10=1.6,p1=0.25,stemcarbon=0.5) 
 2205: 
 2206: c      e0, t0 and tref are parameters from Lloyd & Taylor 1995
 2207:        parameter(e0=308.56, tref=10.0,t0=46.02)
 2208: 
 2209: c      t0 can be used as a pft specific parameter to modify the shape of
 2210: c      the curve describing the temperature dependence of respiration
 2211: 
 2212:        data (respfact(m),m=1,13)
```

## `pb4studio/climate.py` lines 1-15

```text
    1: # -*- coding: utf-8 -*-
    2: """
    3: climate.py — 기후자료 로딩, BIOME4 결합, EEMT/AGB 계산, 스냅샷 출력.
    4: 
    5: yongneup_dynstat20m 패키지에서 검증된 코드를 그대로 옮겼다. 물리/통계 계산
    6: 로직은 손대지 않았고, 아래 두 가지만 새 아키텍처에 맞게 바꿨다:
    7: 
    8:     1) select_time_slices() 삭제 — 기존에는 cfg.time_slices_ka (없으면 기후
    9:        파일의 전체 ka_bp 목록)를 썼지만, 새 소프트웨어는 사용자가 지정한
   10:        TimeConfig(start_ka, end_ka, interval_kyr)에서 직접 시간 목록을
   11:        만든다 (config.py: TimeConfig.snapshot_times_ka()).
   12:     2) run_biome4_dynamic_step()이 PACKAGE_DIR 전역변수 대신
   13:        biome4_backend.run_biome4_fortran_batch_grid()를 호출하도록 정리.
   14: 
   15: 이 모듈의 함수들은 대부분 "cfg" 인자를 받는데, 이는 기존 YongneupConfig의
```

## `pb4studio/climate.py` lines 772-796

```text
  772:         lat_grid=lat_grid,
  773:         land_mask=land_mask,
  774:         elevation_m=elevation_m,
  775:         lon_grid=lon_grid,
  776:         light_input_kind=cfg.light_input_kind,
  777:         force_compile=bool(cfg.force_compile_biome4),
  778:         pressure_from_elevation_func=pressure_from_elevation_pa,
  779:         openmp_threads=int(cfg.biome4_threads_per_resolution),
  780:         biome4_variant=str(cfg.biome4_variant),
  781:     )
  782: 
  783: 
  784: def compute_eemt_and_agb(
  785:     cfg: YongneupConfig,
  786:     veg: Dict[str, np.ndarray],
  787:     temp_monthly_C: np.ndarray,
  788:     prec_monthly_mm: np.ndarray,
  789:     land: np.ndarray,
  790:     bare_bedrock: np.ndarray | None = None,
  791: ) -> Tuple[np.ndarray, np.ndarray]:
  792:     """Compute EEMT and the AGB proxy that feeds Pelletier kd."""
  793:     land = np.asarray(land, dtype=bool)
  794:     shape = land.shape
  795:     if bare_bedrock is None:
  796:         bare_bedrock = np.zeros(shape, dtype=bool)
```

## `pb4studio/climate.py` lines 780-804

```text
  780:         biome4_variant=str(cfg.biome4_variant),
  781:     )
  782: 
  783: 
  784: def compute_eemt_and_agb(
  785:     cfg: YongneupConfig,
  786:     veg: Dict[str, np.ndarray],
  787:     temp_monthly_C: np.ndarray,
  788:     prec_monthly_mm: np.ndarray,
  789:     land: np.ndarray,
  790:     bare_bedrock: np.ndarray | None = None,
  791: ) -> Tuple[np.ndarray, np.ndarray]:
  792:     """Compute EEMT and the AGB proxy that feeds Pelletier kd."""
  793:     land = np.asarray(land, dtype=bool)
  794:     shape = land.shape
  795:     if bare_bedrock is None:
  796:         bare_bedrock = np.zeros(shape, dtype=bool)
  797:     else:
  798:         bare_bedrock = np.asarray(bare_bedrock, dtype=bool) & land
  799:     aet_monthly = np.zeros((12,) + shape, dtype="float64")
  800:     for m in range(1, 13):
  801:         key = f"aet_month_{m:02d}_node"
  802:         if key in veg:
  803:             aet_monthly[m - 1] = np.asarray(veg[key], dtype="float64")
  804:         else:
```

## `pb4studio/climate.py` lines 807-831

```text
  807: 
  808:     # BIOME4를 우회한 노출 기반암 셀에서는 식생 증발산과 생산성을 0으로
  809:     # 둔다. 따라서 EEMT의 물리적 기후항(유효강수)은 유지되지만 생물에너지항은 0이다.
  810:     aet_monthly[:, bare_bedrock] = 0.0
  811: 
  812:     # Pelletier et al. (2013), Eqs. (1)-(2): Peff = PPT - ET and
  813:     # DeltaT = Tambient - 273 K. Do not impose PB4-specific zero clips.
  814:     peff_mm = np.asarray(prec_monthly_mm, dtype="float64") - aet_monthly
  815:     eppt_mj = np.nansum(np.asarray(temp_monthly_C, dtype="float64") * float(cfg.eemt_cw_j_kg_k) * peff_mm, axis=0) / 1.0e6
  816: 
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
```

## `pb4studio/climate.py` lines 808-832

```text
  808:     # BIOME4를 우회한 노출 기반암 셀에서는 식생 증발산과 생산성을 0으로
  809:     # 둔다. 따라서 EEMT의 물리적 기후항(유효강수)은 유지되지만 생물에너지항은 0이다.
  810:     aet_monthly[:, bare_bedrock] = 0.0
  811: 
  812:     # Pelletier et al. (2013), Eqs. (1)-(2): Peff = PPT - ET and
  813:     # DeltaT = Tambient - 273 K. Do not impose PB4-specific zero clips.
  814:     peff_mm = np.asarray(prec_monthly_mm, dtype="float64") - aet_monthly
  815:     eppt_mj = np.nansum(np.asarray(temp_monthly_C, dtype="float64") * float(cfg.eemt_cw_j_kg_k) * peff_mm, axis=0) / 1.0e6
  816: 
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
```

## `pb4studio/climate.py` lines 814-838

```text
  814:     peff_mm = np.asarray(prec_monthly_mm, dtype="float64") - aet_monthly
  815:     eppt_mj = np.nansum(np.asarray(temp_monthly_C, dtype="float64") * float(cfg.eemt_cw_j_kg_k) * peff_mm, axis=0) / 1.0e6
  816: 
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
  833: # -----------------------------------------------------------------------------
  834: # Output helpers
  835: # -----------------------------------------------------------------------------
  836: 
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
```

## `pb4studio/climate.py` lines 815-839

```text
  815:     eppt_mj = np.nansum(np.asarray(temp_monthly_C, dtype="float64") * float(cfg.eemt_cw_j_kg_k) * peff_mm, axis=0) / 1.0e6
  816: 
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
  833: # -----------------------------------------------------------------------------
  834: # Output helpers
  835: # -----------------------------------------------------------------------------
  836: 
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
  839:     shape: Tuple[int, int],
```

## `pb4studio/climate.py` lines 816-840

```text
  816: 
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
  833: # -----------------------------------------------------------------------------
  834: # Output helpers
  835: # -----------------------------------------------------------------------------
  836: 
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
  839:     shape: Tuple[int, int],
  840:     land: np.ndarray | None = None,
```

## `pb4studio/climate.py` lines 817-841

```text
  817:     npp_gC = np.asarray(veg.get("npp_node", np.zeros(shape)), dtype="float64")
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
  833: # -----------------------------------------------------------------------------
  834: # Output helpers
  835: # -----------------------------------------------------------------------------
  836: 
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
  839:     shape: Tuple[int, int],
  840:     land: np.ndarray | None = None,
  841:     bare_bedrock: np.ndarray | None = None,
```

## `pb4studio/climate.py` lines 818-842

```text
  818:     npp_gC = np.where(bare_bedrock, 0.0, npp_gC)
  819:     npp_kg_biomass = np.maximum(npp_gC, 0.0) / 1000.0 / max(float(cfg.eemt_carbon_fraction), 1e-6)
  820:     ebio_mj = npp_kg_biomass * float(cfg.eemt_hbio_j_kg) / 1.0e6
  821: 
  822:     # No PB4 1--80 MJ m^-2 yr^-1 clipping.
  823:     eemt = eppt_mj + ebio_mj
  824:     eemt = np.where(land & np.isfinite(eemt), eemt, np.nan)
  825: 
  826:     # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
  827:     agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
  828:     agb = np.where(bare_bedrock, 0.0, agb)
  829:     agb = np.where(land & np.isfinite(agb), agb, np.nan)
  830:     return eemt.astype("float32"), agb.astype("float32")
  831: 
  832: 
  833: # -----------------------------------------------------------------------------
  834: # Output helpers
  835: # -----------------------------------------------------------------------------
  836: 
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
  839:     shape: Tuple[int, int],
  840:     land: np.ndarray | None = None,
  841:     bare_bedrock: np.ndarray | None = None,
  842: ) -> np.ndarray:
```

## `pb4studio/config.py` lines 77-101

```text
   77:         "unit": "kg/m^3", "label": "토양 용적밀도",
   78:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다.",
   79:     },
   80:     "uplift_m_per_kyr": {
   81:         "unit": "m/kyr", "label": "융기율",
   82:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다 "
   83:                 "(동해안 융기율 참고값, 0.2 m/kyr = 0.2 mm/yr). 융기가 없는 "
   84:                 "민감도 실험을 하려는 경우에만 0으로 바꾸십시오.",
   85:     },
   86:     "kd_c_eemt_m_per_kyr_per_mj": {
   87:         "unit": "m·kyr^-1 per MJ m^-2 yr^-1", "label": "사면수송계수 EEMT항 (c)",
   88:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   89:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 c항.",
   90:     },
   91:     "kd_d_agb_m_per_kyr_per_kgm2": {
   92:         "unit": "m·kyr^-1 per kg m^-2", "label": "사면수송계수 AGB항 (d)",
   93:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   94:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 d항 (식생 지상부바이오매스 효과).",
   95:     },
   96:     "hillslope_critical_slope": {
   97:         "unit": "m/m", "label": "임계경사 (Sc)",
   98:         "help": "용늪 실제 DEM용 수치 기본값은 1.5입니다. "
   99:                 "Pelletier et al. (2013)의 본 실험값 0.7 및 sensitivity 값 0.9는 "
  100:                 "비교용으로 유지합니다. 비선형 사면수송식의 임계경사입니다.",
  101:     },
```

## `pb4studio/config.py` lines 79-103

```text
   79:     },
   80:     "uplift_m_per_kyr": {
   81:         "unit": "m/kyr", "label": "융기율",
   82:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다 "
   83:                 "(동해안 융기율 참고값, 0.2 m/kyr = 0.2 mm/yr). 융기가 없는 "
   84:                 "민감도 실험을 하려는 경우에만 0으로 바꾸십시오.",
   85:     },
   86:     "kd_c_eemt_m_per_kyr_per_mj": {
   87:         "unit": "m·kyr^-1 per MJ m^-2 yr^-1", "label": "사면수송계수 EEMT항 (c)",
   88:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   89:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 c항.",
   90:     },
   91:     "kd_d_agb_m_per_kyr_per_kgm2": {
   92:         "unit": "m·kyr^-1 per kg m^-2", "label": "사면수송계수 AGB항 (d)",
   93:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   94:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 d항 (식생 지상부바이오매스 효과).",
   95:     },
   96:     "hillslope_critical_slope": {
   97:         "unit": "m/m", "label": "임계경사 (Sc)",
   98:         "help": "용늪 실제 DEM용 수치 기본값은 1.5입니다. "
   99:                 "Pelletier et al. (2013)의 본 실험값 0.7 및 sensitivity 값 0.9는 "
  100:                 "비교용으로 유지합니다. 비선형 사면수송식의 임계경사입니다.",
  101:     },
  102:     "hillslope_denom_min": {
  103:         "unit": "-", "label": "비선형 분모 하한 (사용하지 않음)",
```

## `pb4studio/config.py` lines 80-104

```text
   80:     "uplift_m_per_kyr": {
   81:         "unit": "m/kyr", "label": "융기율",
   82:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다 "
   83:                 "(동해안 융기율 참고값, 0.2 m/kyr = 0.2 mm/yr). 융기가 없는 "
   84:                 "민감도 실험을 하려는 경우에만 0으로 바꾸십시오.",
   85:     },
   86:     "kd_c_eemt_m_per_kyr_per_mj": {
   87:         "unit": "m·kyr^-1 per MJ m^-2 yr^-1", "label": "사면수송계수 EEMT항 (c)",
   88:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   89:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 c항.",
   90:     },
   91:     "kd_d_agb_m_per_kyr_per_kgm2": {
   92:         "unit": "m·kyr^-1 per kg m^-2", "label": "사면수송계수 AGB항 (d)",
   93:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   94:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 d항 (식생 지상부바이오매스 효과).",
   95:     },
   96:     "hillslope_critical_slope": {
   97:         "unit": "m/m", "label": "임계경사 (Sc)",
   98:         "help": "용늪 실제 DEM용 수치 기본값은 1.5입니다. "
   99:                 "Pelletier et al. (2013)의 본 실험값 0.7 및 sensitivity 값 0.9는 "
  100:                 "비교용으로 유지합니다. 비선형 사면수송식의 임계경사입니다.",
  101:     },
  102:     "hillslope_denom_min": {
  103:         "unit": "-", "label": "비선형 분모 하한 (사용하지 않음)",
  104:         "help": "하위호환용 필드입니다. 현재 Eq.20-21 경로에서는 분모 하한을 사용하지 않습니다.",
```

## `pb4studio/config.py` lines 82-106

```text
   82:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다 "
   83:                 "(동해안 융기율 참고값, 0.2 m/kyr = 0.2 mm/yr). 융기가 없는 "
   84:                 "민감도 실험을 하려는 경우에만 0으로 바꾸십시오.",
   85:     },
   86:     "kd_c_eemt_m_per_kyr_per_mj": {
   87:         "unit": "m·kyr^-1 per MJ m^-2 yr^-1", "label": "사면수송계수 EEMT항 (c)",
   88:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   89:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 c항.",
   90:     },
   91:     "kd_d_agb_m_per_kyr_per_kgm2": {
   92:         "unit": "m·kyr^-1 per kg m^-2", "label": "사면수송계수 AGB항 (d)",
   93:         "help": "이 계수는 본 패키지 Pelletier-process 모듈의 기본값입니다. "
   94:                 "비선형 사면수송계수 kd = c·EEMT + d·AGB 의 d항 (식생 지상부바이오매스 효과).",
   95:     },
   96:     "hillslope_critical_slope": {
   97:         "unit": "m/m", "label": "임계경사 (Sc)",
   98:         "help": "용늪 실제 DEM용 수치 기본값은 1.5입니다. "
   99:                 "Pelletier et al. (2013)의 본 실험값 0.7 및 sensitivity 값 0.9는 "
  100:                 "비교용으로 유지합니다. 비선형 사면수송식의 임계경사입니다.",
  101:     },
  102:     "hillslope_denom_min": {
  103:         "unit": "-", "label": "비선형 분모 하한 (사용하지 않음)",
  104:         "help": "하위호환용 필드입니다. 현재 Eq.20-21 경로에서는 분모 하한을 사용하지 않습니다.",
  105:     },
  106:     "min_land_soil_m": {
```

## `pb4studio/config.py` lines 339-363

```text
  339:     climate_nc_path: str
  340:     soil_depth_path: str
  341:     soil_texture_path: str
  342:     basin_polygon_path: str
  343:     open_free_shp: Optional[str] = None
  344:     open_fixed_slope_shp: Optional[str] = None
  345:     soil_depth_unit: str = "cm"  # 토심 래스터의 단위 (BDRICM 기본값은 cm)
  346:     validation_points_csv: Optional[str] = None  # None=내장 전국 검증 데이터셋 자동 사용, ""=검증 끄기, 경로=그 파일 사용
  347: 
  348: 
  349: @dataclass
  350: class ScienceConfig:
  351:     """BIOME4 결합/토양 수리/EEMT/AGB 계수. 기본값은 모두 원본
  352:     yongneup_dynstat20m 패키지(YongneupConfig)와 동일하다.
  353: 
  354:     Pelletier 지형발달 계수(PelletierStrictConfig)와는 별개로, BIOME4에 넘길
  355:     토양 수리 파라미터 변환, EEMT(유효에너지·물질전달) 계산, AGB(지상부
  356:     바이오매스) 프록시 산출에 쓰이는 상수들이다.
  357:     """
  358: 
  359:     # hotfix10l default scientific path: BIOME4-SD reference-derived adapter.
  360:     # Soil water storage follows McKenzie et al. (2003): theta(-10 kPa) -
  361:     # theta(-1.5 MPa) integrated through actual soil depth using the Yongneup
  362:     # SoilGrids point values supplied by the user. Root-depth scaling follows
  363:     # McKenzie f(z)=exp(-z/Xi), with Xi analytically fixed from BIOME4's native
```

## `pb4studio/config.py` lines 343-367

```text
  343:     open_free_shp: Optional[str] = None
  344:     open_fixed_slope_shp: Optional[str] = None
  345:     soil_depth_unit: str = "cm"  # 토심 래스터의 단위 (BDRICM 기본값은 cm)
  346:     validation_points_csv: Optional[str] = None  # None=내장 전국 검증 데이터셋 자동 사용, ""=검증 끄기, 경로=그 파일 사용
  347: 
  348: 
  349: @dataclass
  350: class ScienceConfig:
  351:     """BIOME4 결합/토양 수리/EEMT/AGB 계수. 기본값은 모두 원본
  352:     yongneup_dynstat20m 패키지(YongneupConfig)와 동일하다.
  353: 
  354:     Pelletier 지형발달 계수(PelletierStrictConfig)와는 별개로, BIOME4에 넘길
  355:     토양 수리 파라미터 변환, EEMT(유효에너지·물질전달) 계산, AGB(지상부
  356:     바이오매스) 프록시 산출에 쓰이는 상수들이다.
  357:     """
  358: 
  359:     # hotfix10l default scientific path: BIOME4-SD reference-derived adapter.
  360:     # Soil water storage follows McKenzie et al. (2003): theta(-10 kPa) -
  361:     # theta(-1.5 MPa) integrated through actual soil depth using the Yongneup
  362:     # SoilGrids point values supplied by the user. Root-depth scaling follows
  363:     # McKenzie f(z)=exp(-z/Xi), with Xi analytically fixed from BIOME4's native
  364:     # Jackson-et-al. top-30-cm root fraction. No fitted depth→NPP/LAI/FVC
  365:     # coefficient is used. PFT6 uses the Sitch et al. (2003) BoNE climate sieve; the pre-existing
  366:     # PFT5 TCM=-8 C project setting is retained unchanged in this patch.
  367:     biome4_variant: str = "mckenzie2003"
```

## `pb4studio/config.py` lines 382-406

```text
  382:     texture2_whc_mm_per_m: float = 150.0
  383:     texture3_whc_mm_per_m: float = 120.0
  384:     whc_top_layer_m: float = 0.30
  385:     whc_max_depth_m: float = 1.50
  386: 
  387:     # EEMT 계산
  388:     eemt_cw_j_kg_k: float = 4186.0
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
```

## `pb4studio/config.py` lines 383-407

```text
  383:     texture3_whc_mm_per_m: float = 120.0
  384:     whc_top_layer_m: float = 0.30
  385:     whc_max_depth_m: float = 1.50
  386: 
  387:     # EEMT 계산
  388:     eemt_cw_j_kg_k: float = 4186.0
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
```

## `pb4studio/config.py` lines 384-408

```text
  384:     whc_top_layer_m: float = 0.30
  385:     whc_max_depth_m: float = 1.50
  386: 
  387:     # EEMT 계산
  388:     eemt_cw_j_kg_k: float = 4186.0
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
  408:     geomorph_adaptive_substeps: bool = True
```

## `pb4studio/config.py` lines 387-411

```text
  387:     # EEMT 계산
  388:     eemt_cw_j_kg_k: float = 4186.0
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
  408:     geomorph_adaptive_substeps: bool = True
  409:     # Pure numerical tolerance, not a Pelletier process coefficient. Pelletier
  410:     # et al. (2013) dynamically reduced dt when a trial produced too much
  411:     # erosion/deposition and verified convergence by halving the threshold, but
```

## `pb4studio/config.py` lines 388-412

```text
  388:     eemt_cw_j_kg_k: float = 4186.0
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
  408:     geomorph_adaptive_substeps: bool = True
  409:     # Pure numerical tolerance, not a Pelletier process coefficient. Pelletier
  410:     # et al. (2013) dynamically reduced dt when a trial produced too much
  411:     # erosion/deposition and verified convergence by halving the threshold, but
  412:     # did not publish its numerical value. The field name is retained for JSON
```

## `pb4studio/config.py` lines 389-413

```text
  389:     eemt_hbio_j_kg: float = 22.0e6
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
  408:     geomorph_adaptive_substeps: bool = True
  409:     # Pure numerical tolerance, not a Pelletier process coefficient. Pelletier
  410:     # et al. (2013) dynamically reduced dt when a trial produced too much
  411:     # erosion/deposition and verified convergence by halving the threshold, but
  412:     # did not publish its numerical value. The field name is retained for JSON
  413:     # compatibility; hotfix10n2 applies the same 0.025 m tolerance to the maximum
```

## `pb4studio/config.py` lines 390-414

```text
  390:     eemt_carbon_fraction: float = 0.50
  391:     eemt_clip_min_mj_m2_yr: float = 1.0
  392:     eemt_clip_max_mj_m2_yr: float = 80.0
  393: 
  394:     # AGB 프록시 (kd = c*EEMT + d*AGB 의 AGB 입력)
  395:     # NOTE: PelletierStrictConfig currently requires standing AGB. BIOME4 does
  396:     # not prognose standing AGB, so this legacy bridge is retained only to keep
  397:     # the existing Pelletier runner operational. It is NOT part of the claimed
  398:     # pure-BIOME4 vegetation response and remains explicitly unresolved for a
  399:     # future reference-only AGB coupling.
  400:     agb_from_npp_scale: float = 0.010
  401:     agb_min_kg_m2: float = 0.1
  402:     agb_max_kg_m2: float = 100.0
  403: 
  404:     # 지형발달 최대 서브스텝 (kyr). 기본 0.1 kyr = 100년이다. 실제 dt는
  405:     # Pelletier et al. (2013)의 명시적 안정시간 추정식에 따라 더 작아질 수 있다.
  406:     geomorph_substep_kyr: float = 0.1
  407:     geomorph_min_substep_kyr: float = 1.0e-10
  408:     geomorph_adaptive_substeps: bool = True
  409:     # Pure numerical tolerance, not a Pelletier process coefficient. Pelletier
  410:     # et al. (2013) dynamically reduced dt when a trial produced too much
  411:     # erosion/deposition and verified convergence by halving the threshold, but
  412:     # did not publish its numerical value. The field name is retained for JSON
  413:     # compatibility; hotfix10n2 applies the same 0.025 m tolerance to the maximum
  414:     # hillslope/fluvial/threshold-adjustment change in a trial.
```

## `pb4studio/pelletier_geomorph.py` lines 47-71

```text
   47:     """
   48: 
   49:     p0_base_m_per_kyr: float = 0.037
   50:     eemt_to_p0_b: float = 0.030
   51:     h0_m: float = 0.50
   52:     # Pelletier et al. (2013), Table 1 / Eq. (8): direct bedrock/regolith density ratio.
   53:     bedrock_regolith_density_ratio: float = 1.8
   54:     # Legacy serialization-only fields; no longer used in Eq. (8).
   55:     rock_density_kg_m3: float = 2700.0
   56:     soil_bulk_density_kg_m3: float = 1400.0
   57:     uplift_m_per_kyr: float = 0.20
   58:     kd_c_eemt_m_per_kyr_per_mj: float = 0.033
   59:     kd_d_agb_m_per_kyr_per_kgm2: float = 0.050
   60:     # Yongneup real-DEM numerical default selected after the bundled 20 m / 1 kyr
   61:     # convergence audit. Pelletier et al. (2013) used Sc=0.7 and tested 0.9;
   62:     # those values remain sensitivity cases rather than the Yongneup default.
   63:     hillslope_critical_slope: float = 1.50
   64:     # Legacy JSON field only; the active Eq. (20)-(21) path does not use a
   65:     # denominator floor. Supercritical faces are handled before Eq. (20).
   66:     hillslope_denom_min: float = 0.0
   67:     # 하위호환용 필드. v6.1부터 상태변수 h에는 양의 최소토심을 강제하지
   68:     # 않는다. 값이 들어와도 계산에는 사용하지 않으며 h >= 0만 보장한다.
   69:     min_land_soil_m: float = 0.0
   70:     k0_regolith: float = 0.020
   71:     # Legacy field retained for old JSON compatibility only. Eq. (18) uses actual positive EEMT.
```

## `pb4studio/pelletier_geomorph.py` lines 580-604

```text
  580:         "bedrock_lowered_m": bedrock_lowered,
  581:         "adjusted_mask": adjusted,
  582:         "threshold_export_mass_equivalent_m": mass_equiv,
  583:     }
  584: 
  585: 
  586: def nonlinear_hillslope_change_closed_boundary(
  587:     cfg: PelletierStrictConfig,
  588:     z: np.ndarray,
  589:     h: np.ndarray,
  590:     land: np.ndarray,
  591:     eemt: np.ndarray,
  592:     agb: np.ndarray,
  593:     dt_kyr: float,
  594:     dx_m: float,
  595: ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
  596:     """Pelletier et al. (2013) Eqs. (20)-(22), on subcritical faces.
  597: 
  598:     The singular Eqs. (20)-(21) are evaluated only where |S_face| < Sc.
  599:     Faces numerically equal to Sc are handled by ``threshold_slope_adjustment``
  600:     and carry no Eq. (20) flux during that explicit substep.  No 1e-6
  601:     denominator replacement, Sc-epsilon physical cap, or sign reversal is used.
  602: 
  603:     A finite-volume *supply/positivity* constraint scales a donor's outgoing
  604:     face fluxes only when the finite explicit step would export more mobile
```

## `pb4studio/pelletier_geomorph.py` lines 600-624

```text
  600:     and carry no Eq. (20) flux during that explicit substep.  No 1e-6
  601:     denominator replacement, Sc-epsilon physical cap, or sign reversal is used.
  602: 
  603:     A finite-volume *supply/positivity* constraint scales a donor's outgoing
  604:     face fluxes only when the finite explicit step would export more mobile
  605:     regolith than exists in that donor.  It is not a substitute for the
  606:     nonlinear stability solver and does not regularize the singular denominator.
  607:     """
  608:     land = np.asarray(land, dtype=bool)
  609:     z = _as_float_array(z)
  610:     h = np.maximum(_as_float_array(h), 0.0)
  611:     eemt = _as_float_array(eemt)
  612:     agb = np.maximum(_as_float_array(agb), 0.0)
  613:     nrows, ncols = z.shape
  614: 
  615:     slope, cos_theta = local_slope_and_costheta(z, dx_m, land)
  616:     kd = cfg.kd_c_eemt_m_per_kyr_per_mj * eemt + cfg.kd_d_agb_m_per_kyr_per_kgm2 * agb
  617:     kd = np.where(land & np.isfinite(kd), np.maximum(kd, 0.0), 0.0)
  618:     mobile_h = np.where(land, np.maximum(h, 0.0), 0.0)
  619:     sc = float(cfg.hillslope_critical_slope)
  620:     if not np.isfinite(sc) or sc <= 0.0:
  621:         raise ValueError("hillslope_critical_slope must be finite and > 0")
  622: 
  623:     qx = np.zeros((nrows, max(ncols - 1, 1)), dtype="float64")
  624:     qy = np.zeros((max(nrows - 1, 1), ncols), dtype="float64")
```

## `pb4studio/pelletier_geomorph.py` lines 604-628

```text
  604:     face fluxes only when the finite explicit step would export more mobile
  605:     regolith than exists in that donor.  It is not a substitute for the
  606:     nonlinear stability solver and does not regularize the singular denominator.
  607:     """
  608:     land = np.asarray(land, dtype=bool)
  609:     z = _as_float_array(z)
  610:     h = np.maximum(_as_float_array(h), 0.0)
  611:     eemt = _as_float_array(eemt)
  612:     agb = np.maximum(_as_float_array(agb), 0.0)
  613:     nrows, ncols = z.shape
  614: 
  615:     slope, cos_theta = local_slope_and_costheta(z, dx_m, land)
  616:     kd = cfg.kd_c_eemt_m_per_kyr_per_mj * eemt + cfg.kd_d_agb_m_per_kyr_per_kgm2 * agb
  617:     kd = np.where(land & np.isfinite(kd), np.maximum(kd, 0.0), 0.0)
  618:     mobile_h = np.where(land, np.maximum(h, 0.0), 0.0)
  619:     sc = float(cfg.hillslope_critical_slope)
  620:     if not np.isfinite(sc) or sc <= 0.0:
  621:         raise ValueError("hillslope_critical_slope must be finite and > 0")
  622: 
  623:     qx = np.zeros((nrows, max(ncols - 1, 1)), dtype="float64")
  624:     qy = np.zeros((max(nrows - 1, 1), ncols), dtype="float64")
  625:     sx = np.zeros_like(qx)
  626:     sy = np.zeros_like(qy)
  627:     super_x = np.zeros_like(qx, dtype=bool)
  628:     super_y = np.zeros_like(qy, dtype=bool)
```

## `pb4studio/pelletier_geomorph.py` lines 991-1015

```text
  991: 
  992:     return e_reg, e_bed, area_m2, slope, routing_z, sink_fill_depth, area_halfmax_m2, grid_ratio_f, valley
  993: 
  994: 
  995: def update_pelletier_strict(
  996:     cfg: PelletierStrictConfig,
  997:     z: np.ndarray,
  998:     b: np.ndarray,
  999:     h: np.ndarray,
 1000:     land: np.ndarray,
 1001:     boundary_cfg: BoundaryConfig,
 1002:     eemt: np.ndarray,
 1003:     agb: np.ndarray,
 1004:     dt_kyr: float,
 1005:     dx_m: float,
 1006: ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
 1007:     """z, b, h 상태를 한 geomorphic substep 전진시킨다."""
 1008:     land = np.asarray(land, dtype=bool)
 1009:     b = _as_float_array(b)
 1010:     h = np.maximum(_as_float_array(h), 0.0)
 1011:     h = np.where(land, h, 0.0)
 1012: 
 1013:     # Every open outlet is a fixed base-level (Dirichlet) geomorphic boundary.
 1014:     # The boundary type still controls only the routing-surface tie-break /
 1015:     # prescribed routing gradient.  The physical z/b/h state of an open cell
```

## `pb4studio/pelletier_geomorph.py` lines 1011-1035

```text
 1011:     h = np.where(land, h, 0.0)
 1012: 
 1013:     # Every open outlet is a fixed base-level (Dirichlet) geomorphic boundary.
 1014:     # The boundary type still controls only the routing-surface tie-break /
 1015:     # prescribed routing gradient.  The physical z/b/h state of an open cell
 1016:     # is held at its value on entry to this substep.  Because the next substep
 1017:     # receives that unchanged state, the boundary remains fixed at its initial
 1018:     # model value without inventing an external elevation or slope.
 1019:     fixed_baselevel_mask = _fixed_baselevel_mask_from_boundary(land, boundary_cfg)
 1020: 
 1021:     z_state = b + h
 1022:     eemt_arr = _as_float_array(eemt)
 1023:     agb_arr = _as_float_array(agb)
 1024:     nonfinite_eemt = land & ~np.isfinite(eemt_arr)
 1025:     nonfinite_agb = land & ~np.isfinite(agb_arr)
 1026:     if np.any(nonfinite_eemt):
 1027:         first = tuple(int(v) for v in np.argwhere(nonfinite_eemt)[0])
 1028:         raise ValueError(f"Non-finite EEMT on active land: first at row={first[0]}, col={first[1]}")
 1029:     if np.any(nonfinite_agb):
 1030:         first = tuple(int(v) for v in np.argwhere(nonfinite_agb)[0])
 1031:         raise ValueError(f"Non-finite AGB on active land: first at row={first[0]}, col={first[1]}")
 1032: 
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
```

## `pb4studio/pelletier_geomorph.py` lines 1013-1037

```text
 1013:     # Every open outlet is a fixed base-level (Dirichlet) geomorphic boundary.
 1014:     # The boundary type still controls only the routing-surface tie-break /
 1015:     # prescribed routing gradient.  The physical z/b/h state of an open cell
 1016:     # is held at its value on entry to this substep.  Because the next substep
 1017:     # receives that unchanged state, the boundary remains fixed at its initial
 1018:     # model value without inventing an external elevation or slope.
 1019:     fixed_baselevel_mask = _fixed_baselevel_mask_from_boundary(land, boundary_cfg)
 1020: 
 1021:     z_state = b + h
 1022:     eemt_arr = _as_float_array(eemt)
 1023:     agb_arr = _as_float_array(agb)
 1024:     nonfinite_eemt = land & ~np.isfinite(eemt_arr)
 1025:     nonfinite_agb = land & ~np.isfinite(agb_arr)
 1026:     if np.any(nonfinite_eemt):
 1027:         first = tuple(int(v) for v in np.argwhere(nonfinite_eemt)[0])
 1028:         raise ValueError(f"Non-finite EEMT on active land: first at row={first[0]}, col={first[1]}")
 1029:     if np.any(nonfinite_agb):
 1030:         first = tuple(int(v) for v in np.argwhere(nonfinite_agb)[0])
 1031:         raise ValueError(f"Non-finite AGB on active land: first at row={first[0]}, col={first[1]}")
 1032: 
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
 1036:     z_state, b, h, threshold_pre = threshold_slope_adjustment(
 1037:         cfg, z_state, b, h, land, boundary_cfg, dx_m
```

## `pb4studio/pelletier_geomorph.py` lines 1017-1041

```text
 1017:     # receives that unchanged state, the boundary remains fixed at its initial
 1018:     # model value without inventing an external elevation or slope.
 1019:     fixed_baselevel_mask = _fixed_baselevel_mask_from_boundary(land, boundary_cfg)
 1020: 
 1021:     z_state = b + h
 1022:     eemt_arr = _as_float_array(eemt)
 1023:     agb_arr = _as_float_array(agb)
 1024:     nonfinite_eemt = land & ~np.isfinite(eemt_arr)
 1025:     nonfinite_agb = land & ~np.isfinite(agb_arr)
 1026:     if np.any(nonfinite_eemt):
 1027:         first = tuple(int(v) for v in np.argwhere(nonfinite_eemt)[0])
 1028:         raise ValueError(f"Non-finite EEMT on active land: first at row={first[0]}, col={first[1]}")
 1029:     if np.any(nonfinite_agb):
 1030:         first = tuple(int(v) for v in np.argwhere(nonfinite_agb)[0])
 1031:         raise ValueError(f"Non-finite AGB on active land: first at row={first[0]}, col={first[1]}")
 1032: 
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
 1036:     z_state, b, h, threshold_pre = threshold_slope_adjustment(
 1037:         cfg, z_state, b, h, land, boundary_cfg, dx_m
 1038:     )
 1039: 
 1040:     slope, cos_theta = local_slope_and_costheta(z_state, dx_m, land)
 1041:     # Eq. (18)의 0 나눗셈 방지 하한은 하천침식 분모에만 적용한다.
```

## `pb4studio/pelletier_geomorph.py` lines 1018-1042

```text
 1018:     # model value without inventing an external elevation or slope.
 1019:     fixed_baselevel_mask = _fixed_baselevel_mask_from_boundary(land, boundary_cfg)
 1020: 
 1021:     z_state = b + h
 1022:     eemt_arr = _as_float_array(eemt)
 1023:     agb_arr = _as_float_array(agb)
 1024:     nonfinite_eemt = land & ~np.isfinite(eemt_arr)
 1025:     nonfinite_agb = land & ~np.isfinite(agb_arr)
 1026:     if np.any(nonfinite_eemt):
 1027:         first = tuple(int(v) for v in np.argwhere(nonfinite_eemt)[0])
 1028:         raise ValueError(f"Non-finite EEMT on active land: first at row={first[0]}, col={first[1]}")
 1029:     if np.any(nonfinite_agb):
 1030:         first = tuple(int(v) for v in np.argwhere(nonfinite_agb)[0])
 1031:         raise ValueError(f"Non-finite AGB on active land: first at row={first[0]}, col={first[1]}")
 1032: 
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
 1036:     z_state, b, h, threshold_pre = threshold_slope_adjustment(
 1037:         cfg, z_state, b, h, land, boundary_cfg, dx_m
 1038:     )
 1039: 
 1040:     slope, cos_theta = local_slope_and_costheta(z_state, dx_m, land)
 1041:     # Eq. (18)의 0 나눗셈 방지 하한은 하천침식 분모에만 적용한다.
 1042:     # Eq. (10) 토양생산과 Eq. (15) 사면수송은 실제 finite EEMT를 사용한다.
```

## `pb4studio/pelletier_geomorph.py` lines 1019-1043

```text
 1019:     fixed_baselevel_mask = _fixed_baselevel_mask_from_boundary(land, boundary_cfg)
 1020: 
 1021:     z_state = b + h
 1022:     eemt_arr = _as_float_array(eemt)
 1023:     agb_arr = _as_float_array(agb)
 1024:     nonfinite_eemt = land & ~np.isfinite(eemt_arr)
 1025:     nonfinite_agb = land & ~np.isfinite(agb_arr)
 1026:     if np.any(nonfinite_eemt):
 1027:         first = tuple(int(v) for v in np.argwhere(nonfinite_eemt)[0])
 1028:         raise ValueError(f"Non-finite EEMT on active land: first at row={first[0]}, col={first[1]}")
 1029:     if np.any(nonfinite_agb):
 1030:         first = tuple(int(v) for v in np.argwhere(nonfinite_agb)[0])
 1031:         raise ValueError(f"Non-finite AGB on active land: first at row={first[0]}, col={first[1]}")
 1032: 
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
 1036:     z_state, b, h, threshold_pre = threshold_slope_adjustment(
 1037:         cfg, z_state, b, h, land, boundary_cfg, dx_m
 1038:     )
 1039: 
 1040:     slope, cos_theta = local_slope_and_costheta(z_state, dx_m, land)
 1041:     # Eq. (18)의 0 나눗셈 방지 하한은 하천침식 분모에만 적용한다.
 1042:     # Eq. (10) 토양생산과 Eq. (15) 사면수송은 실제 finite EEMT를 사용한다.
 1043:     eemt_model = np.where(np.isfinite(eemt_arr), eemt_arr, 0.0)
```

## `pb4studio/pelletier_geomorph.py` lines 1033-1057

```text
 1033:     # Real-DEM threshold closure: remove excess topography before evaluating the
 1034:     # singular Pelletier Eq.20/21.  In ordinary accepted states this is a no-op;
 1035:     # it is essential for an initially oversteepened measured DEM.
 1036:     z_state, b, h, threshold_pre = threshold_slope_adjustment(
 1037:         cfg, z_state, b, h, land, boundary_cfg, dx_m
 1038:     )
 1039: 
 1040:     slope, cos_theta = local_slope_and_costheta(z_state, dx_m, land)
 1041:     # Eq. (18)의 0 나눗셈 방지 하한은 하천침식 분모에만 적용한다.
 1042:     # Eq. (10) 토양생산과 Eq. (15) 사면수송은 실제 finite EEMT를 사용한다.
 1043:     eemt_model = np.where(np.isfinite(eemt_arr), eemt_arr, 0.0)
 1044:     eemt_safe = np.maximum(eemt_model, cfg.eemt_min_for_erodibility)
 1045:     agb_safe = np.maximum(np.where(np.isfinite(agb_arr), agb_arr, 0.0), 0.0)
 1046: 
 1047:     p0 = float(cfg.p0_base_m_per_kyr) * np.exp(float(cfg.eemt_to_p0_b) * eemt_model)
 1048:     p_normal = p0 * np.exp(-(h * cos_theta) / max(float(cfg.h0_m), 1e-6))
 1049:     weathering_vertical = p_normal / np.maximum(cos_theta, 1e-6) * float(dt_kyr)
 1050:     density_ratio = float(cfg.bedrock_regolith_density_ratio)
 1051:     if not np.isfinite(density_ratio) or density_ratio <= 0.0:
 1052:         raise ValueError("bedrock_regolith_density_ratio must be finite and > 0")
 1053:     soil_gain = weathering_vertical * density_ratio
 1054:     uplift = float(cfg.uplift_m_per_kyr) * float(dt_kyr)
 1055: 
 1056:     # Soil production is available to the mobile layer in this geomorphic
 1057:     # substep; the finite-volume supply constraint therefore sees h+soil_gain.
```

## `pb4studio/pelletier_geomorph.py` lines 1048-1072

```text
 1048:     p_normal = p0 * np.exp(-(h * cos_theta) / max(float(cfg.h0_m), 1e-6))
 1049:     weathering_vertical = p_normal / np.maximum(cos_theta, 1e-6) * float(dt_kyr)
 1050:     density_ratio = float(cfg.bedrock_regolith_density_ratio)
 1051:     if not np.isfinite(density_ratio) or density_ratio <= 0.0:
 1052:         raise ValueError("bedrock_regolith_density_ratio must be finite and > 0")
 1053:     soil_gain = weathering_vertical * density_ratio
 1054:     uplift = float(cfg.uplift_m_per_kyr) * float(dt_kyr)
 1055: 
 1056:     # Soil production is available to the mobile layer in this geomorphic
 1057:     # substep; the finite-volume supply constraint therefore sees h+soil_gain.
 1058:     h_mobile = h + soil_gain
 1059:     dz_hill, slope_hill, cos_hill, hill_diag = nonlinear_hillslope_change_closed_boundary(
 1060:         cfg=cfg, z=z_state, h=h_mobile, land=land, eemt=eemt_model, agb=agb_safe, dt_kyr=dt_kyr, dx_m=dx_m,
 1061:     )
 1062: 
 1063:     h_after_hillslope = h_mobile + dz_hill
 1064:     min_intermediate = float(np.nanmin(h_after_hillslope[land])) if np.any(land) else 0.0
 1065:     if min_intermediate < -1e-8:
 1066:         raise FloatingPointError(
 1067:             f"Negative soil depth after production+hillslope transport: {min_intermediate:.6g} m"
 1068:         )
 1069:     h_after_hillslope = np.where(land, np.maximum(h_after_hillslope, 0.0), 0.0)
 1070: 
 1071:     e_reg, e_bed, area_m2, slope_flow, routing_z, sink_fill_depth, area_halfmax_m2, grid_ratio_f, valley_mask = fluvial_erosion_depths_multi_boundary(
 1072:         cfg=cfg, z=z_state, h=h, land=land, boundary_cfg=boundary_cfg,
```

## `pb4studio/pelletier_geomorph.py` lines 1146-1170

```text
 1146:         ),
 1147:     }
 1148:     # Keep dynamic geomorphic state in float64 across adaptive substeps.
 1149:     # Recasting ~1-km elevations to float32 after every accepted dt makes
 1150:     # round-off depend on substep count and can destroy T -> T/2 convergence.
 1151:     # Output writers may still down-cast at the I/O boundary.
 1152:     return z_new.astype("float64"), b_new.astype("float64"), h_new.astype("float64"), diagnostics
 1153: 
 1154: 
 1155: def pelletier_default_stable_dt_kyr(
 1156:     cfg: PelletierStrictConfig,
 1157:     eemt: np.ndarray,
 1158:     agb: np.ndarray,
 1159:     land: np.ndarray,
 1160:     dx_m: float,
 1161: ) -> float:
 1162:     """Return Pelletier et al. (2013)'s conservative explicit-step estimate.
 1163: 
 1164:     The paper used ``0.01 * dx^2 / (2 * kd)`` as the default step for its
 1165:     depth- and nonlinear-slope-dependent transport implementation, with further
 1166:     dynamic reduction when necessary.  We use the maximum active-cell ``kd`` so
 1167:     one accepted substep is safe for the whole raster.
 1168:     """
 1169:     land = np.asarray(land, dtype=bool)
 1170:     eemt = np.maximum(_as_float_array(eemt), 0.0)
```

## `pb4studio/pelletier_geomorph.py` lines 1159-1177

```text
 1159:     land: np.ndarray,
 1160:     dx_m: float,
 1161: ) -> float:
 1162:     """Return Pelletier et al. (2013)'s conservative explicit-step estimate.
 1163: 
 1164:     The paper used ``0.01 * dx^2 / (2 * kd)`` as the default step for its
 1165:     depth- and nonlinear-slope-dependent transport implementation, with further
 1166:     dynamic reduction when necessary.  We use the maximum active-cell ``kd`` so
 1167:     one accepted substep is safe for the whole raster.
 1168:     """
 1169:     land = np.asarray(land, dtype=bool)
 1170:     eemt = np.maximum(_as_float_array(eemt), 0.0)
 1171:     agb = np.maximum(_as_float_array(agb), 0.0)
 1172:     kd = cfg.kd_c_eemt_m_per_kyr_per_mj * eemt + cfg.kd_d_agb_m_per_kyr_per_kgm2 * agb
 1173:     valid = land & np.isfinite(kd) & (kd > 0.0)
 1174:     if not np.any(valid):
 1175:         return float("inf")
 1176:     kd_max = float(np.nanmax(kd[valid]))
 1177:     return 0.01 * float(dx_m) ** 2 / (2.0 * kd_max)
```

## `pb4studio/pelletier_geomorph.py` lines 1160-1177

```text
 1160:     dx_m: float,
 1161: ) -> float:
 1162:     """Return Pelletier et al. (2013)'s conservative explicit-step estimate.
 1163: 
 1164:     The paper used ``0.01 * dx^2 / (2 * kd)`` as the default step for its
 1165:     depth- and nonlinear-slope-dependent transport implementation, with further
 1166:     dynamic reduction when necessary.  We use the maximum active-cell ``kd`` so
 1167:     one accepted substep is safe for the whole raster.
 1168:     """
 1169:     land = np.asarray(land, dtype=bool)
 1170:     eemt = np.maximum(_as_float_array(eemt), 0.0)
 1171:     agb = np.maximum(_as_float_array(agb), 0.0)
 1172:     kd = cfg.kd_c_eemt_m_per_kyr_per_mj * eemt + cfg.kd_d_agb_m_per_kyr_per_kgm2 * agb
 1173:     valid = land & np.isfinite(kd) & (kd > 0.0)
 1174:     if not np.any(valid):
 1175:         return float("inf")
 1176:     kd_max = float(np.nanmax(kd[valid]))
 1177:     return 0.01 * float(dx_m) ** 2 / (2.0 * kd_max)
```

## `pb4studio/runner.py` lines 1-24

```text
    1: # -*- coding: utf-8 -*-
    2: """
    3: runner.py — 정적/동적/정적+동적 비교 실행 오케스트레이터.
    4: 
    5: yongneup_dynstat20m의 ``run_one_resolution_worker`` (검증된 시간 루프)를
    6: 그대로 따르되, 아래를 새 모듈로 교체했다:
    7: 
    8:     - grid.py       : DEM 기준 CRS/셀크기 자동감지 + 재투영 (기존: 고정 EPSG:5187)
    9:     - boundary.py   : 다중 open 경계(shp 기반)          (기존: 단일 outlet 좌표)
   10:     - config.py     : TimeConfig(시작/종료/간격)          (기존: cfg.time_slices_ka)
   11: 
   12: BIOME4 호출과 EEMT/AGB 결합을 유지하면서, 실행 전 기후 연대범위 검사를
   13: 강제하고 교정된 지형발달 계산을 호출한다.
   14: """
   15: from __future__ import annotations
   16: 
   17: from pathlib import Path
   18: from typing import Dict, List, Optional, Tuple
   19: import json
   20: 
   21: import numpy as np
   22: import pandas as pd
   23: import rasterio
   24: from rasterio.enums import Resampling
```

## `pb4studio/runner.py` lines 20-44

```text
   20: 
   21: import numpy as np
   22: import pandas as pd
   23: import rasterio
   24: from rasterio.enums import Resampling
   25: 
   26: from . import grid
   27: from .boundary import BoundaryConfig, BoundaryType
   28: from .snapshots import map_snapshot_ages_to_output_indices, snapshot_dir_name
   29: from .config import RunConfig, RunMode, TimeConfig
   30: from .climate import (
   31:     load_climate, climate_arrays_for_time, build_soil_arrays,
   32:     run_biome4_dynamic_step, compute_eemt_and_agb, vegetation_array,
   33:     write_geotiff, write_cell_csv, summarize_snapshot,
   34: )
   35: from .pelletier_geomorph import (
   36:     PelletierStrictConfig,
   37:     update_pelletier_strict,
   38:     pelletier_default_stable_dt_kyr,
   39: )
   40: from . import validation as validation_mod
   41: from . import figures as figures_mod
   42: from . import standard_report as standard_report_mod
   43: 
   44: 
```

## `pb4studio/runner.py` lines 85-109

```text
   85:         "biome4_backend": "not_called_all_bare",
   86:     }
   87: 
   88: 
   89: def _advance_geomorph_interval_adaptive(
   90:     cfg: PelletierStrictConfig,
   91:     z: np.ndarray,
   92:     b: np.ndarray,
   93:     h: np.ndarray,
   94:     land: np.ndarray,
   95:     boundary_cfg: BoundaryConfig,
   96:     eemt: np.ndarray,
   97:     agb: np.ndarray,
   98:     interval_kyr: float,
   99:     dx_m: float,
  100:     max_substep_kyr: float,
  101:     min_substep_kyr: float,
  102:     fluvial_max_change_tolerance_m: float = 0.025,
  103:     adaptive: bool = True,
  104: ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, object]]:
  105:     """Advance one climate interval with adaptive geomorphic substeps.
  106: 
  107:     Two independent numerical controls are applied without modifying any
  108:     process rate:
  109: 
```

## `pb4studio/runner.py` lines 117-141

```text
  117:     The threshold magnitude is not published by Pelletier et al. (2013).  The
  118:     bundled default (0.025 m) is therefore a numerical tolerance selected by a
  119:     T -> T/2 convergence audit, not a physical calibration coefficient.  No
  120:     process amount is capped to this value: rejected trials are discarded and
  121:     recomputed from the unchanged accepted state.  After an accepted trial the
  122:     next candidate dt is allowed to double (up to max_dt); this prevents a brief
  123:     near-critical transient from locking the rest of a kyr-scale interval to a
  124:     minute-scale substep.
  125:     """
  126:     remaining = max(float(interval_kyr), 0.0)
  127:     max_dt = max(float(max_substep_kyr), 1e-12)
  128:     min_dt = max(float(min_substep_kyr), 1e-12)
  129:     stable_dt = pelletier_default_stable_dt_kyr(cfg, eemt, agb, land, dx_m)
  130:     fluvial_tol = float(fluvial_max_change_tolerance_m)
  131:     if not np.isfinite(fluvial_tol) or fluvial_tol < 0.0:
  132:         raise ValueError("geomorph_fluvial_max_change_m must be finite and >= 0")
  133: 
  134:     accepted = 0
  135:     rejected = 0
  136:     rejected_stability = 0
  137:     rejected_fluvial = 0
  138:     rejected_process_change = 0
  139:     rejected_other = 0
  140:     min_used = float("inf")
  141:     max_used = 0.0
```

## `pb4studio/runner.py` lines 162-186

```text
  162:                 rejected += 1
  163:                 rejected_stability += 1
  164:                 if dt < min_dt:
  165:                     raise RuntimeError(
  166:                         "Pelletier 안정시간 조건을 만족하려면 지형발달 서브스텝이 "
  167:                         f"최소 허용값({min_dt:g} kyr)보다 작아져야 합니다. "
  168:                         f"추정 안정 dt={stable_dt:g} kyr, 격자={dx_m:g} m"
  169:                     )
  170: 
  171:         while True:
  172:             try:
  173:                 z_try, b_try, h_try, diag = update_pelletier_strict(
  174:                     cfg, z, b, h, land, boundary_cfg, eemt, agb, dt, dx_m,
  175:                 )
  176:                 valid = (
  177:                     np.all(np.isfinite(z_try[land]))
  178:                     and np.all(np.isfinite(b_try[land]))
  179:                     and np.all(np.isfinite(h_try[land]))
  180:                     and float(np.nanmin(h_try[land])) >= -1e-8
  181:                 ) if np.any(land) else True
  182:                 if not valid:
  183:                     raise FloatingPointError("non-finite or negative geomorphic state")
  184: 
  185:                 # Pelletier et al. (2013) reduced dt dynamically so the
  186:                 # maximum erosion/deposition in one explicit step remained
```

## `pb4studio/runner.py` lines 537-561

```text
  537:         soil_arrays = build_soil_arrays(legacy_cfg, h, biome4_land, igrid.texture0)
  538:         # ``force_compile_biome4`` means rebuild once at run start, not once per
  539:         # model timestep.  The shim may safely carry this per-call override.
  540:         legacy_cfg.force_compile_biome4 = force_compile_pending
  541:         if np.any(biome4_land):
  542:             veg = run_biome4_dynamic_step(
  543:                 legacy_cfg, temp, prec, cloud, tmin, co2, soil_arrays,
  544:                 igrid.lat, igrid.lon, z, biome4_land,
  545:             )
  546:             force_compile_pending = False
  547:         else:
  548:             veg = _empty_biome4_result_for_bare_bedrock(igrid.shape, igrid.land)
  549:         eemt, agb = compute_eemt_and_agb(
  550:             legacy_cfg, veg, temp, prec, igrid.land, bare_bedrock=bare_bedrock,
  551:         )
  552:         npp = np.asarray(veg.get("npp_node", np.full(igrid.shape, np.nan)), dtype="float32")
  553:         npp = np.where(bare_bedrock, 0.0, npp)
  554:         npp = np.where(igrid.land & np.isfinite(npp), npp, np.nan).astype("float32")
  555:         eemt = np.where(igrid.land & np.isfinite(eemt), eemt, np.nan).astype("float32")
  556:         veg_code = vegetation_array(veg, igrid.shape, igrid.land, bare_bedrock=bare_bedrock).astype("float32")
  557: 
  558:         if validation_records:
  559:             step_val = validation_mod._sample_validation_records_for_step(
  560:                 validation_records, int(round(igrid.resolution_m)), float(ka), veg_code, igrid.transform,
  561:                 basin_presence_min_fraction=run_config.science.basin_presence_min_fraction,
```

## `pb4studio/runner.py` lines 591-615

```text
  591:                 snap_dir.mkdir(parents=True, exist_ok=True)
  592:                 for name, arr in fields.items():
  593:                     write_geotiff(snap_dir / f"{name}.tif", arr, igrid.transform, str(igrid.crs))
  594:                 write_cell_csv(snap_dir / "cell_values.csv", igrid.x, igrid.y, igrid.lon, igrid.lat, igrid.land, fields)
  595:                 snap_row = row.copy()
  596:                 snap_row["snapshot_requested_ka"] = float(requested_ka)
  597:                 snapshot_rows.append(snap_row)
  598: 
  599:         if dynamic_on and i < len(times) - 1:
  600:             next_ka = float(times[i + 1])
  601:             interval_kyr = max(float(ka) - next_ka, 0.0)
  602:             z, b, h, geomorph_stats = _advance_geomorph_interval_adaptive(
  603:                 geomorph_cfg, z, b, h, igrid.land, boundary_cfg, eemt, agb,
  604:                 interval_kyr=interval_kyr,
  605:                 dx_m=float(igrid.resolution_m),
  606:                 max_substep_kyr=float(run_config.science.geomorph_substep_kyr),
  607:                 min_substep_kyr=float(run_config.science.geomorph_min_substep_kyr),
  608:                 fluvial_max_change_tolerance_m=float(run_config.science.geomorph_fluvial_max_change_m),
  609:                 adaptive=bool(run_config.science.geomorph_adaptive_substeps),
  610:             )
  611:             row["geomorph_accepted_substeps_to_next"] = geomorph_stats["accepted_substeps"]
  612:             row["geomorph_rejected_substeps_to_next"] = geomorph_stats["rejected_or_halved_substeps"]
  613:             row["geomorph_rejected_fluvial_trials_to_next"] = geomorph_stats["rejected_fluvial_trials"]
  614:             row["geomorph_min_dt_kyr_to_next"] = geomorph_stats["min_dt_kyr"]
  615:             row["geomorph_max_dt_kyr_to_next"] = geomorph_stats["max_dt_kyr"]
```

## `tools/test_fluvial_adaptive_convergence.py` lines 14-38

```text
   14: if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
   15: import pb4studio.pelletier_geomorph as pg
   16: import pb4studio.runner as rr
   17: from pb4studio.boundary import BoundaryConfig, BoundaryType
   18: 
   19: def boundary_from_state(land, outlet):
   20:     bt=np.full(land.shape,int(BoundaryType.CLOSED),dtype=np.uint8)
   21:     bt[outlet]=int(BoundaryType.OPEN_FREE)
   22:     return BoundaryConfig(boundary_type=bt, free_tie_break_eps_m=1e-4)
   23: 
   24: def run_one(state, tol, interval, max_dt, min_dt, outlet):
   25:     z0=state['z'].astype(float); h0=state['h'].astype(float); b0=state['b'].astype(float)
   26:     eemt=state['eemt'].astype(float); agb=state['agb'].astype(float); land=state['land'].astype(bool)
   27:     transform=state['transform'].astype(float); dx=abs(float(transform[0]))
   28:     bc=boundary_from_state(land,outlet)
   29:     def no_hill(cfg,z,h,land,eemt,agb,dt_kyr,dx_m):
   30:         slope,cost=pg.local_slope_and_costheta(z,dx_m,land)
   31:         return np.zeros_like(z,dtype=float),slope,cost,{"hillslope_supply_limited_mask":np.zeros_like(land,dtype=bool)}
   32:     def no_threshold(cfg,z,b,h,land,boundary_cfg,dx_m,block_size=512):
   33:         zeros=np.zeros_like(z,dtype=float)
   34:         return z.copy(),b.copy(),h.copy(),{
   35:           "surface_lowering_m":zeros,"soil_removed_m":zeros,"bedrock_lowered_m":zeros,
   36:           "adjusted_mask":np.zeros_like(land,dtype=bool),"threshold_export_mass_equivalent_m":zeros}
   37:     orig=pg.nonlinear_hillslope_change_closed_boundary
   38:     orig_thr=pg.threshold_slope_adjustment
```

## `tools/test_fluvial_adaptive_convergence.py` lines 17-41

```text
   17: from pb4studio.boundary import BoundaryConfig, BoundaryType
   18: 
   19: def boundary_from_state(land, outlet):
   20:     bt=np.full(land.shape,int(BoundaryType.CLOSED),dtype=np.uint8)
   21:     bt[outlet]=int(BoundaryType.OPEN_FREE)
   22:     return BoundaryConfig(boundary_type=bt, free_tie_break_eps_m=1e-4)
   23: 
   24: def run_one(state, tol, interval, max_dt, min_dt, outlet):
   25:     z0=state['z'].astype(float); h0=state['h'].astype(float); b0=state['b'].astype(float)
   26:     eemt=state['eemt'].astype(float); agb=state['agb'].astype(float); land=state['land'].astype(bool)
   27:     transform=state['transform'].astype(float); dx=abs(float(transform[0]))
   28:     bc=boundary_from_state(land,outlet)
   29:     def no_hill(cfg,z,h,land,eemt,agb,dt_kyr,dx_m):
   30:         slope,cost=pg.local_slope_and_costheta(z,dx_m,land)
   31:         return np.zeros_like(z,dtype=float),slope,cost,{"hillslope_supply_limited_mask":np.zeros_like(land,dtype=bool)}
   32:     def no_threshold(cfg,z,b,h,land,boundary_cfg,dx_m,block_size=512):
   33:         zeros=np.zeros_like(z,dtype=float)
   34:         return z.copy(),b.copy(),h.copy(),{
   35:           "surface_lowering_m":zeros,"soil_removed_m":zeros,"bedrock_lowered_m":zeros,
   36:           "adjusted_mask":np.zeros_like(land,dtype=bool),"threshold_export_mass_equivalent_m":zeros}
   37:     orig=pg.nonlinear_hillslope_change_closed_boundary
   38:     orig_thr=pg.threshold_slope_adjustment
   39:     pg.nonlinear_hillslope_change_closed_boundary=no_hill
   40:     pg.threshold_slope_adjustment=no_threshold
   41:     try:
```

## `tools/test_fluvial_adaptive_convergence.py` lines 33-57

```text
   33:         zeros=np.zeros_like(z,dtype=float)
   34:         return z.copy(),b.copy(),h.copy(),{
   35:           "surface_lowering_m":zeros,"soil_removed_m":zeros,"bedrock_lowered_m":zeros,
   36:           "adjusted_mask":np.zeros_like(land,dtype=bool),"threshold_export_mass_equivalent_m":zeros}
   37:     orig=pg.nonlinear_hillslope_change_closed_boundary
   38:     orig_thr=pg.threshold_slope_adjustment
   39:     pg.nonlinear_hillslope_change_closed_boundary=no_hill
   40:     pg.threshold_slope_adjustment=no_threshold
   41:     try:
   42:         t=time.time()
   43:         z,b,h,stats=rr._advance_geomorph_interval_adaptive(
   44:             pg.PelletierStrictConfig(), z0.copy(), b0.copy(), h0.copy(), land, bc,
   45:             eemt, agb, interval, dx, max_dt, min_dt, tol, True,
   46:         )
   47:         elapsed=time.time()-t
   48:     finally:
   49:         pg.nonlinear_hillslope_change_closed_boundary=orig
   50:         pg.threshold_slope_adjustment=orig_thr
   51:     diag=stats.pop('last_diagnostics')
   52:     report={
   53:         'tol_m':tol,'elapsed_s':elapsed,'stats':stats,
   54:         'h_min':float(h[land].min()),'h_mean':float(h[land].mean()),'h_max':float(h[land].max()),
   55:         'bare_n':int(np.count_nonzero((h<=1e-8)&land)),
   56:         'dz_min':float((z-z0)[land].min()),'dz_mean':float((z-z0)[land].mean()),'dz_max':float((z-z0)[land].max()),
   57:         'outlet':list(map(int,outlet)),'outlet_h_change':float(h[outlet]-h0[outlet]),
```

## `tools/test_hillslope_sc15_20m_1k.py` lines 1-22

```text
    1: import sys, json, time
    2: from pathlib import Path
    3: import numpy as np
    4: BASE=Path(__file__).resolve().parents[1]
    5: sys.path.insert(0,str(BASE))
    6: from pb4studio.pelletier_geomorph import PelletierStrictConfig, threshold_slope_adjustment
    7: from pb4studio.boundary import BoundaryConfig, BoundaryType
    8: from pb4studio.runner import _advance_geomorph_interval_adaptive
    9: S=np.load(BASE/'diagnostics'/'reference_6ka_geomorph_state.npz')
   10: z10=S['z'].astype(float); h10=S['h'].astype(float); b10=S['b'].astype(float); land10=S['land'].astype(bool); e10=S['eemt'].astype(float); a10=S['agb'].astype(float)
   11: dx=float(abs(S['transform'][0]))*2
   12: 
   13: def agg(arr):
   14:     out=np.full((20,23),np.nan); mask=np.zeros((20,23),bool)
   15:     for r in range(20):
   16:         for c in range(23):
   17:             sl=(slice(2*r,2*r+2),slice(2*c,2*c+2)); m=land10[sl]&np.isfinite(arr[sl])
   18:             if np.any(m): out[r,c]=np.mean(arr[sl][m]); mask[r,c]=1
   19:     return out,mask
   20: z,land=agg(z10); h,_=agg(h10); b,_=agg(b10); eemt,_=agg(e10); agb,_=agg(a10); z=b+h
   21: outlet=(2,16); assert land[outlet]
   22: bt=np.zeros_like(land,dtype=np.uint8); bt[outlet]=int(BoundaryType.OPEN_FREE)
```

## `tools/test_hillslope_sc15_20m_1k.py` lines 8-32

```text
    8: from pb4studio.runner import _advance_geomorph_interval_adaptive
    9: S=np.load(BASE/'diagnostics'/'reference_6ka_geomorph_state.npz')
   10: z10=S['z'].astype(float); h10=S['h'].astype(float); b10=S['b'].astype(float); land10=S['land'].astype(bool); e10=S['eemt'].astype(float); a10=S['agb'].astype(float)
   11: dx=float(abs(S['transform'][0]))*2
   12: 
   13: def agg(arr):
   14:     out=np.full((20,23),np.nan); mask=np.zeros((20,23),bool)
   15:     for r in range(20):
   16:         for c in range(23):
   17:             sl=(slice(2*r,2*r+2),slice(2*c,2*c+2)); m=land10[sl]&np.isfinite(arr[sl])
   18:             if np.any(m): out[r,c]=np.mean(arr[sl][m]); mask[r,c]=1
   19:     return out,mask
   20: z,land=agg(z10); h,_=agg(h10); b,_=agg(b10); eemt,_=agg(e10); agb,_=agg(a10); z=b+h
   21: outlet=(2,16); assert land[outlet]
   22: bt=np.zeros_like(land,dtype=np.uint8); bt[outlet]=int(BoundaryType.OPEN_FREE)
   23: bc=BoundaryConfig(bt,free_tie_break_eps_m=0.0001)
   24: 
   25: def face_stats(zz,sc):
   26:     vals=[]; nr,nc=zz.shape
   27:     for r in range(nr):
   28:       for c in range(nc):
   29:         if not land[r,c]: continue
   30:         for dr,dc in ((0,1),(1,0)):
   31:           rr,cc=r+dr,c+dc
   32:           if rr<nr and cc<nc and land[rr,cc]: vals.append(abs(zz[r,c]-zz[rr,cc])/dx)
```

## `tools/test_hillslope_sc15_20m_1k.py` lines 33-57

```text
   33:     vals=np.asarray(vals)
   34:     return {'faces':int(vals.size),'over':int(np.sum(vals>sc+1e-10)),'at':int(np.sum(np.abs(vals-sc)<=1e-10)),'max':float(vals.max()),'p95':float(np.quantile(vals,.95))}
   35: 
   36: def run(tol):
   37:     cfg=PelletierStrictConfig()
   38:     assert cfg.hillslope_critical_slope == 1.5, cfg.hillslope_critical_slope
   39:     sc=cfg.hillslope_critical_slope
   40:     initial_face=face_stats(z,sc)
   41:     zi,bi,hi,iadj=threshold_slope_adjustment(cfg,z,b,h,land,bc,dx)
   42:     after_init=face_stats(zi,sc)
   43:     t0=time.time()
   44:     zo,bo,ho,stats=_advance_geomorph_interval_adaptive(
   45:         cfg,z,b,h,land,bc,eemt,agb,interval_kyr=1.0,dx_m=dx,
   46:         max_substep_kyr=0.1,min_substep_kyr=1e-12,
   47:         fluvial_max_change_tolerance_m=tol,adaptive=True)
   48:     arr=ho[land]; dh=(ho-hi)[land]
   49:     last=stats.pop('last_diagnostics')
   50:     out={
   51:       'tol_m':tol,'Sc_default':sc,'dx_m':dx,'land_cells':int(land.sum()),
   52:       'initial_faces':initial_face,
   53:       'initial_adjustment':{
   54:         'cells':int(np.sum(iadj['adjusted_mask'])),
   55:         'lowering_sum_m':float(np.sum(iadj['surface_lowering_m'][land])),
   56:         'lowering_max_m':float(np.max(iadj['surface_lowering_m'][land])),
   57:         'soil_removed_depthsum_m':float(np.sum(iadj['soil_removed_m'][land])),
```

