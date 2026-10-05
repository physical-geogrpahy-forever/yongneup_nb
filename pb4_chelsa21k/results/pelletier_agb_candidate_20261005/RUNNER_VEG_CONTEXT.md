# Runner and vegetation context

## `pb4studio/runner.py` lines 530-600

```text
  530:     for i, ka in enumerate(times):
  531:         if progress_callback is not None:
  532:             progress_callback(case_label or output_subdir, i, len(times), float(ka))
  533:         temp, prec, cloud, tmin, co2 = climate_arrays_for_time(legacy_cfg, climate_df, float(ka), z, igrid.land)
  534:         bare_tol = max(float(run_config.science.bare_bedrock_tolerance_m), 0.0)
  535:         bare_bedrock = igrid.land & (np.asarray(h, dtype="float64") <= bare_tol)
  536:         biome4_land = igrid.land & (~bare_bedrock)
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
  562:                 basin_mask=igrid.land,
  563:             )
  564:             for vr in step_val:
  565:                 vr.update({"case": output_subdir, "case_label": case_label or output_subdir, "geomorph_dynamic": dynamic_on})
  566:             validation_step_rows.extend(step_val)
  567: 
  568:         row = summarize_snapshot(int(round(igrid.resolution_m)), float(ka), z, h, veg_code, npp, eemt, igrid.land)
  569:         row.update({
  570:             "case": output_subdir,
  571:             "geomorph_dynamic": dynamic_on,
  572:             "biome4_variant": str(run_config.science.biome4_variant),
  573:         })
  574:         summary_rows.append(row)
  575: 
  576:         if i in snapshot_index_to_labels:
  577:             snapshot_fields = {
  578:                 "elevation_m": z, "soil_depth_m": h, "soil_texture_class": igrid.texture0,
  579:                 "vegetation_code": veg_code, "npp": npp, "eemt": eemt,
  580:                 "bare_bedrock": bare_bedrock.astype("float32"),
  581:             }
  582:             if "lai_node" in veg:
  583:                 snapshot_fields["lai"] = np.asarray(veg["lai_node"], dtype="float32")
  584:             if "bgc_rootspace_node" in veg:
  585:                 snapshot_fields["bgc_rootspace"] = np.asarray(veg["bgc_rootspace_node"], dtype="float32")
  586:             if "bgc_lai_cap_node" in veg:
  587:                 snapshot_fields["bgc_lai_cap"] = np.asarray(veg["bgc_lai_cap_node"], dtype="float32")
  588:             fields = _mask_snapshot_fields(snapshot_fields, igrid.land)
  589:             for requested_ka in snapshot_index_to_labels[i]:
  590:                 snap_dir = res_dir / snapshot_dir_name(requested_ka)
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
```

## `pb4studio/climate.py` lines 650-770

```text
  650:     and 0.30-1.50 m. The 1.50 m cap is therefore a BIOME4 structural limit, not
  651:     a McKenzie parameter.
  652:     """
  653:     h = np.clip(np.asarray(soil_depth_m, dtype="float64"), 0.0, float(max_depth_m))
  654:     # (top m, bottom m, theta_-10 - theta_-1500 in mm per metre)
  655:     profile = (
  656:         (0.00, 0.05, 237.0),
  657:         (0.05, 0.15, 232.0),
  658:         (0.15, 0.30, 218.0),
  659:         (0.30, 0.60, 207.0),
  660:         (0.60, 1.00, 198.0),
  661:         (1.00, 2.00, 179.0),
  662:     )
  663: 
  664:     def integrate(z0: float, z1: np.ndarray) -> np.ndarray:
  665:         total = np.zeros_like(h, dtype="float64")
  666:         upper = np.minimum(z1, float(max_depth_m))
  667:         for a, b, awc_per_m in profile:
  668:             lo = np.maximum(float(a), z0)
  669:             hi = np.minimum(float(b), upper)
  670:             thickness = np.maximum(hi - lo, 0.0)
  671:             total += thickness * float(awc_per_m)
  672:         return total
  673: 
  674:     top_end = np.minimum(h, 0.30)
  675:     whc_top = integrate(0.0, top_end)
  676:     whc_bottom = integrate(0.30, h)
  677:     return whc_top, whc_bottom
  678: 
  679: 
  680: def build_soil_arrays(cfg: YongneupConfig, soil_depth_m: np.ndarray, land: np.ndarray, texture_class: np.ndarray | None = None) -> Dict[str, np.ndarray]:
  681:     """Convert BDRICM-derived soil depth and texture class to BIOME4 soil inputs.
  682: 
  683:     In the original variant, soil depth changes only the two BIOME4 WHC stores.
  684:     In the mckenzie2003 variant, Yongneup SoilGrids theta(-10 kPa)-theta(-1500 kPa)
  685:     is integrated over actual profile depth while retaining BIOME4's 0-0.30 m and
  686:     0.30-1.50 m hydraulic domains; root-depth weights are handled in the Fortran
  687:     backend. No direct soil-depth multiplier is applied to NPP, LAI, FVC, or competition.
  688:     """
  689:     # 지형 상태의 토심을 그대로 사용한다. 노출 기반암(h=0)은 호출부에서
  690:     # BIOME4 활성 마스크에서 제외하므로, 여기서 가상의 1 mm 토양을 만들지 않는다.
  691:     h = np.maximum(np.asarray(soil_depth_m, dtype="float64"), 0.0)
  692:     h = np.where(land, h, np.nan)
  693: 
  694:     if str(getattr(cfg, "biome4_variant", "original")).strip().lower() == "mckenzie2003":
  695:         # The Yongneup SoilGrids point is classified as BIOME4 texture class 2
  696:         # across all valid model cells in the supplied texture raster. Guard
  697:         # against silently applying this site profile to a different texture.
  698:         if texture_class is not None:
  699:             tex = np.asarray(texture_class, dtype="float64")
  700:             vals = np.unique(np.rint(tex[land & np.isfinite(tex)]).astype(int))
  701:             if vals.size and np.any(vals != 2):
  702:                 raise ValueError(
  703:                     "McKenzie2003 Yongneup profile is site-specific to the supplied texture-2 domain; "
  704:                     f"found other texture classes: {vals.tolist()}"
  705:                 )
  706:         whc_top, whc_bottom = _mckenzie2003_yongneup_awc_stores(
  707:             h, max_depth_m=float(cfg.whc_max_depth_m)
  708:         )
  709:         # Hydraulic conductivity indices remain the native BIOME4 texture
  710:         # values; McKenzie (2003) is used only for available-water storage and
  711:         # root-density scaling, not to invent a new conductivity relation.
  712:         _, _, perc_top, perc_bottom = _texture_hydraulic_arrays(cfg, texture_class, h.shape)
  713:         out = {
  714:             "perc_top_mm_hr": np.where(land, perc_top, np.nan).astype("float32"),
  715:             "perc_bottom_mm_hr": np.where(land, perc_bottom, np.nan).astype("float32"),
  716:             "whc_top_mm": np.where(land, whc_top, np.nan).astype("float32"),
  717:             "whc_bottom_mm": np.where(land, whc_bottom, np.nan).astype("float32"),
  718:             "soil_depth_m": np.where(land, h, np.nan).astype("float32"),
  719:             "awc_method": "McKenzie2003_theta10_minus_theta1500_SoilGrids_Yongneup",
  720:         }
  721:         if texture_class is not None:
  722:             out["soil_texture_class"] = np.where(land, texture_class, np.nan).astype("float32")
  723:         return out
  724: 
  725:     top_thick = np.minimum(h, float(cfg.whc_top_layer_m))
  726:     bottom_thick = np.minimum(
  727:         np.maximum(h - float(cfg.whc_top_layer_m), 0.0),
  728:         max(float(cfg.whc_max_depth_m) - float(cfg.whc_top_layer_m), 0.0),
  729:     )
  730:     whc_top_per_m, whc_bottom_per_m, perc_top, perc_bottom = _texture_hydraulic_arrays(cfg, texture_class, h.shape)
  731:     whc_top = top_thick * whc_top_per_m
  732:     whc_bottom = bottom_thick * whc_bottom_per_m
  733:     out = {
  734:         "perc_top_mm_hr": np.where(land, perc_top, np.nan).astype("float32"),
  735:         "perc_bottom_mm_hr": np.where(land, perc_bottom, np.nan).astype("float32"),
  736:         "whc_top_mm": np.where(land, whc_top, np.nan).astype("float32"),
  737:         "whc_bottom_mm": np.where(land, whc_bottom, np.nan).astype("float32"),
  738:         "soil_depth_m": np.where(land, h, np.nan).astype("float32"),
  739:     }
  740:     if texture_class is not None:
  741:         out["soil_texture_class"] = np.where(land, texture_class, np.nan).astype("float32")
  742:     return out
  743: 
  744: 
  745: def pressure_from_elevation_pa(elevation_m: float) -> float:
  746:     """Approximate atmospheric pressure from elevation for BIOME4."""
  747:     z = max(float(elevation_m), -500.0)
  748:     return 101325.0 * (1.0 - 2.25577e-5 * z) ** 5.25588
  749: 
  750: 
  751: def run_biome4_dynamic_step(
  752:     cfg: YongneupConfig,
  753:     temp_monthly_C: np.ndarray,
  754:     prec_monthly_mm: np.ndarray,
  755:     cloud_percent_monthly: np.ndarray,
  756:     tmin_C: np.ndarray,
  757:     co2_ppm: float,
  758:     soil_arrays: Dict[str, np.ndarray],
  759:     lat_grid: np.ndarray,
  760:     lon_grid: np.ndarray,
  761:     elevation_m: np.ndarray,
  762:     land_mask: np.ndarray,
  763: ) -> Dict[str, np.ndarray]:
  764:     """Run the selected BIOME4 Fortran backend on every valid land cell."""
  765:     return biome4_backend.run_biome4_fortran_batch_grid(
  766:         temp_monthly_C=temp_monthly_C,
  767:         prec_monthly_mm=prec_monthly_mm,
  768:         cloud_percent_monthly=cloud_percent_monthly,
  769:         tmin_C=tmin_C,
  770:         co2_ppm=co2_ppm,
```

## `pb4studio/climate.py` lines 837-910

```text
  837: def vegetation_array(
  838:     veg: Dict[str, np.ndarray],
  839:     shape: Tuple[int, int],
  840:     land: np.ndarray | None = None,
  841:     bare_bedrock: np.ndarray | None = None,
  842: ) -> np.ndarray:
  843:     """Return the five-class vegetation raster used by maps and validation.
  844: 
  845:     hotfix10n10 restores all native BIOME4 competition PFTs (PFT2--13), so the
  846:     reduced Yongneup classes are assigned from native biome physiognomy plus
  847:     dominant functional-group diagnostics rather than from the old 4/5/6/8
  848:     subset.  The reduced classes remain:
  849: 
  850:       0 conifer forest; 1 broadleaf forest; 2 mixed forest;
  851:       3 herbaceous/open vegetation; 4 truly non-vegetated/bare.
  852: 
  853:     Functional-group interpretation of restored PFTs:
  854:       PFT2/3/4 = broadleaf-tree group;
  855:       PFT5/6/7 = conifer/taiga-tree group (PFT7 is boreal deciduous taiga);
  856:       PFT8/9 = grass; PFT10 = desert woody; PFT11 = tundra shrub;
  857:       PFT12 = cold herbaceous; PFT13 = lichen/forb.
  858: 
  859:     Native mixed biomes 6/7/9 keep the symmetric 51% dominance rule.  To avoid
  860:     bias merely because one functional group contains more PFTs, the strongest
  861:     potential-NPP member of each woody group is compared, not the sum of all
  862:     group members.  Native Desert (21) is classed as open vegetation when a
  863:     real PFT and positive productivity/LAI are present; only Barren (27), Land
  864:     ice (28), PB4 exposed bedrock, or a genuinely vegetation-free desert cell
  865:     are class 4.
  866:     """
  867:     if land is None:
  868:         land = np.ones(shape, dtype=bool)
  869:     land = np.asarray(land, dtype=bool)
  870:     if bare_bedrock is None:
  871:         bare_bedrock = np.zeros(shape, dtype=bool)
  872:     else:
  873:         bare_bedrock = np.asarray(bare_bedrock, dtype=bool) & land
  874: 
  875:     out = np.full(shape, np.nan, dtype="float32")
  876:     if "biome4_full_id_node" not in veg:
  877:         return out
  878:     full = np.asarray(veg["biome4_full_id_node"], dtype="float32")
  879:     optpft = np.asarray(veg.get("optpft_node", np.zeros(shape)), dtype="float64")
  880:     npp = np.asarray(veg.get("npp_node", np.full(shape, np.nan)), dtype="float64")
  881:     lai = np.asarray(veg.get("lai_node", np.full(shape, np.nan)), dtype="float64")
  882: 
  883:     # Closed-forest physiognomies.
  884:     out[np.isin(full, [5, 8, 10, 11]) & land] = 0  # conifer/taiga forest
  885:     out[np.isin(full, [1, 2, 3, 4]) & land] = 1   # broadleaf forest
  886: 
  887:     # Native mixed forest, generalized to all restored woody PFTs.
  888:     mixed = np.isin(full, [6, 7, 9]) & land
  889:     out[mixed] = 2
  890:     broad_arrays = [veg.get(f"pft{i:02d}_mod_npp_node") for i in (2, 3, 4)]
  891:     conif_arrays = [veg.get(f"pft{i:02d}_mod_npp_node") for i in (5, 6, 7)]
  892:     if all(x is not None for x in broad_arrays + conif_arrays):
  893:         broad = np.maximum.reduce([np.asarray(x, dtype="float64") for x in broad_arrays])
  894:         conifer = np.maximum.reduce([np.asarray(x, dtype="float64") for x in conif_arrays])
  895:         denom = broad + conifer
  896:         con_share = np.divide(conifer, denom, out=np.full(shape, np.nan), where=denom > 0.0)
  897:         brd_share = np.divide(broad, denom, out=np.full(shape, np.nan), where=denom > 0.0)
  898:         out[mixed & np.isfinite(con_share) & (con_share >= 0.51)] = 0
  899:         out[mixed & np.isfinite(brd_share) & (brd_share >= 0.51)] = 1
  900: 
  901:     # Savanna/woodland, shrub, grass and tundra are reduced to open vegetation.
  902:     out[np.isin(full, [12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26]) & land] = 3
  903: 
  904:     # BIOME4 Desert may still contain low-productivity desert woody/grass PFTs.
  905:     desert = (full == 21) & land
  906:     desert_vegetated = desert & (optpft > 0) & (
  907:         (np.isfinite(npp) & (npp > 0.0)) | (np.isfinite(lai) & (lai > 0.0))
  908:     )
  909:     out[desert_vegetated] = 3
  910:     out[desert & ~desert_vegetated] = 4
```

