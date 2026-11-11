from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from netCDF4 import Dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AGES = [120.0, 100.0, 80.0, 60.0, 50.0, 40.0, 20.0, 10.0, 5.9, 4.8, 4.1, 3.4, 3.0, 2.7, 2.2, 2.0, 1.0, 0.5, 0.4, 0.0]


def read_raster(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1, masked=True).filled(np.nan).astype(np.float64)


def scaled_i2(arr: np.ndarray, scale: float, valid: np.ndarray) -> np.ndarray:
    out = np.full(arr.shape, -32768, dtype=np.int16)
    vals = np.asarray(arr, dtype=np.float64)
    use = valid & np.isfinite(vals)
    q = np.rint(vals[use] / scale)
    if np.any(q < -32767) or np.any(q > 32767):
        raise ValueError(f"int16 overflow for scale={scale}: range={q.min()}..{q.max()}")
    out[use] = q.astype(np.int16)
    return out


def write_climate_nc(path: Path, igrid, z, land, temp, prec, cloud, tmin):
    ny, nx = land.shape
    with Dataset(path, 'w', format='NETCDF4') as nc:
        nc.createDimension('x', nx)
        nc.createDimension('y', ny)
        nc.createDimension('time', 12)
        vx = nc.createVariable('x', 'f8', ('x',))
        vy = nc.createVariable('y', 'f8', ('y',))
        vx[:] = igrid.x[0, :]
        vy[:] = igrid.y[:, 0]
        vx.units = 'm'
        vy.units = 'm'
        vlon = nc.createVariable('lon', 'f8', ('y', 'x'))
        vlat = nc.createVariable('lat', 'f8', ('y', 'x'))
        vlon[:] = np.where(land, igrid.lon, -9999.0)
        vlat[:] = np.where(land, igrid.lat, -9999.0)
        vlon.units = 'degrees_east'
        vlat.units = 'degrees_north'
        velv = nc.createVariable('elv', 'f4', ('y', 'x'), fill_value=np.float32(-9999.0))
        velv[:] = np.where(land, z, -9999.0).astype(np.float32)
        velv.units = 'm'
        for name, data, scale, units in [
            ('tmp', temp, 0.01, 'degC'),
            ('pre', prec, 0.1, 'mm'),
            ('cld', cloud, 0.01, 'percent'),
            ('tmin', np.broadcast_to(tmin[None, :, :], (12, ny, nx)), 0.01, 'degC'),
        ]:
            v = nc.createVariable(name, 'i2', ('time', 'y', 'x'), fill_value=np.int16(-32768), zlib=True)
            v.set_auto_maskandscale(False)
            v[:] = np.stack([scaled_i2(data[m], scale, land) for m in range(12)])
            v.scale_factor = np.float32(scale)
            v.add_offset = np.float32(0.0)
            v.missing_value = np.int16(-32768)
            v.units = units


def write_soil_nc(path: Path, soil_arrays, land):
    ny, nx = land.shape
    dz = np.array([10.0, 10.0, 10.0, 40.0, 40.0, 40.0], dtype=np.float32)
    whc_top = np.asarray(soil_arrays['whc_top_mm'], dtype=np.float64)
    whc_bottom = np.asarray(soil_arrays['whc_bottom_mm'], dtype=np.float64)
    k_top = np.asarray(soil_arrays['perc_top_mm_hr'], dtype=np.float64)
    k_bottom = np.asarray(soil_arrays['perc_bottom_mm_hr'], dtype=np.float64)
    whc = np.full((6, ny, nx), -9999.0, dtype=np.float32)
    ksat = np.full((6, ny, nx), -9999.0, dtype=np.float32)
    for i in range(3):
        whc[i, land] = (whc_top[land] / 30.0).astype(np.float32)
        ksat[i, land] = k_top[land].astype(np.float32)
    for i in range(3, 6):
        whc[i, land] = (whc_bottom[land] / 120.0).astype(np.float32)
        ksat[i, land] = k_bottom[land].astype(np.float32)
    with Dataset(path, 'w', format='NETCDF4') as nc:
        nc.createDimension('x', nx)
        nc.createDimension('y', ny)
        nc.createDimension('depth', 6)
        vdz = nc.createVariable('dz', 'f4', ('depth',))
        vdz[:] = dz
        vdz.units = 'cm'
        vwhc = nc.createVariable('whc', 'f4', ('depth', 'y', 'x'), fill_value=np.float32(-9999.0), zlib=True)
        vwhc[:] = whc
        vwhc.units = 'mm cm-1'
        vk = nc.createVariable('Ksat', 'f4', ('depth', 'y', 'x'), fill_value=np.float32(-9999.0), zlib=True)
        vk[:] = ksat
        vk.units = 'mm h-1'


def read_standalone_output(path: Path):
    with Dataset(path, 'r') as nc:
        biome = np.asarray(nc.variables['biome'][:], dtype=np.float64)
        optpft = np.asarray(nc.variables['wdom'][:], dtype=np.float64)
        npp = np.asarray(nc.variables['NPP'][:], dtype=np.float64)
        lai = np.asarray(nc.variables['LAI'][:], dtype=np.float64)
        npp = np.where(npp < -1000, np.nan, npp)
        lai = np.where(lai < -1000, np.nan, lai)
        biome = np.where(biome < -1000, np.nan, biome)
        optpft = np.where(optpft < -1000, np.nan, optpft)
    return biome, optpft, npp, lai


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pb4-root', required=True)
    ap.add_argument('--biome4-root', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--threads', type=int, default=2)
    args = ap.parse_args()
    pb4_root = Path(args.pb4_root).resolve()
    biome4_root = Path(args.biome4_root).resolve()
    out_root = Path(args.output_dir).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(pb4_root))
    os.environ['OMP_NUM_THREADS'] = str(max(1, args.threads))
    os.environ['OMP_DYNAMIC'] = 'FALSE'
    os.environ['OMP_WAIT_POLICY'] = 'PASSIVE'
    from pb4studio.config import RunConfig
    from pb4studio.runner import build_initial_grid
    from pb4studio.climate import load_climate, climate_arrays_for_time, build_soil_arrays
    from pb4studio.climate import run_biome4_dynamic_step

    run_json = pb4_root / 'outputs_hotfix10n10_selfcontained' / 'run_config_hotfix10n10_selfcontained.json'
    cfg = RunConfig.from_json(run_json)
    igrid = build_initial_grid(cfg)
    climate_df = load_climate(Path(cfg.inputs.climate_nc_path),
                              lon_value=float(np.nanmean(igrid.lon[igrid.land])),
                              lat_value=float(np.nanmean(igrid.lat[igrid.land])))
    legacy_cfg = cfg.legacy_cfg_shim()
    output_root = Path(cfg.output_dir)
    biome4_exe = biome4_root / 'biome4'
    if not biome4_exe.exists():
        raise FileNotFoundError(biome4_exe)

    summary_rows, cell_rows, pft_rows = [], [], []
    for case_label, model_dir in [('static', 'model_static'), ('dynamic', 'model_dynamic')]:
      for age in AGES:
        label = f'{age:g}'
        snap = output_root / model_dir / f'snapshot_{label}ka'
        if not snap.exists():
            raise FileNotFoundError(f'Missing PB4 {case_label} snapshot: {snap}')
        z = read_raster(snap / 'elevation_m.tif')
        h = read_raster(snap / 'soil_depth_m.tif')
        texture = read_raster(snap / 'soil_texture_class.tif')
        land = igrid.land & np.isfinite(z) & np.isfinite(h) & np.isfinite(texture)
        biome4_land = land & (h > float(cfg.science.bare_bedrock_tolerance_m))
        temp, prec, cloud, tmin, co2 = climate_arrays_for_time(legacy_cfg, climate_df, float(age), z, land)
        soil_arrays = build_soil_arrays(legacy_cfg, h, biome4_land, texture)
        pb4_veg = run_biome4_dynamic_step(
            legacy_cfg, temp, prec, cloud, tmin, co2, soil_arrays,
            igrid.lat, igrid.lon, z, biome4_land,
        )
        pb4_biome = np.asarray(pb4_veg['biome4_full_id_node'], dtype=np.float64)
        pb4_optpft = np.asarray(pb4_veg['optpft_node'], dtype=np.float64)
        pb4_npp = np.stack([np.asarray(pb4_veg[f'pft{p:02d}_mod_npp_node'], dtype=np.float64) for p in range(1, 14)])
        pb4_lai = np.stack([np.asarray(pb4_veg[f'pft{p:02d}_mod_lai_node'], dtype=np.float64) for p in range(1, 14)])
        pb4_opt_npp = np.asarray(pb4_veg['npp_node'], dtype=np.float64)
        pb4_opt_lai = np.asarray(pb4_veg['lai_node'], dtype=np.float64)

        case_dir = out_root / f'{case_label}_age_{label}ka'
        case_dir.mkdir(parents=True, exist_ok=True)
        climate_nc = case_dir / 'climate.nc'
        soil_nc = case_dir / 'soil.nc'
        output_nc = case_dir / 'biome4_standalone.nc'
        namelist = case_dir / 'joboptions.namelist'
        write_climate_nc(climate_nc, igrid, z, biome4_land, temp, prec, cloud, tmin)
        write_soil_nc(soil_nc, soil_arrays, biome4_land)
        namelist.write_text(
            '&joboptions\n'
            f"climatefile = '{climate_nc}',\n"
            f"soilfile = '{soil_nc}',\n"
            f'co2 = {float(co2):.8f},\n'
            'diag = .false.\n/\n', encoding='utf-8'
        )
        env = os.environ.copy()
        env['OMP_NUM_THREADS'] = str(max(1, args.threads))
        env['OMP_DYNAMIC'] = 'FALSE'
        proc = subprocess.run([str(biome4_exe), str(namelist), 'alldata', str(output_nc)],
                              cwd=str(biome4_root), env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (case_dir / 'biome4_stdout.log').write_text(proc.stdout, encoding='utf-8')
        if proc.returncode != 0 or not output_nc.exists():
            raise RuntimeError(f'Standalone BIOME4 failed at {age} ka ({case_label}); see {case_dir}/biome4_stdout.log')
        st_biome, st_optpft, st_npp, st_lai = read_standalone_output(output_nc)
        valid = biome4_land & np.isfinite(pb4_biome) & np.isfinite(st_biome)
        if not np.any(valid):
            raise RuntimeError(f'No overlapping valid cells at {age} ka ({case_label})')
        st_opt_npp = np.full(valid.shape, np.nan, dtype=np.float64)
        st_opt_lai = np.full(valid.shape, np.nan, dtype=np.float64)
        for p in range(1, 14):
            m = valid & np.isclose(st_optpft, p)
            st_opt_npp[m] = st_npp[p-1][m]
            st_opt_lai[m] = st_lai[p-1][m]
        biome_match = np.isclose(pb4_biome[valid], st_biome[valid])
        optpft_valid = valid & np.isfinite(pb4_optpft) & np.isfinite(st_optpft)
        optpft_match = np.isclose(pb4_optpft[optpft_valid], st_optpft[optpft_valid]) if np.any(optpft_valid) else np.array([])
        npp_valid = valid & np.isfinite(pb4_opt_npp) & np.isfinite(st_opt_npp)
        lai_valid = valid & np.isfinite(pb4_opt_lai) & np.isfinite(st_opt_lai)
        pft_valid = np.broadcast_to(valid, pb4_npp.shape) & np.isfinite(pb4_npp) & np.isfinite(st_npp)
        pft_lai_valid = np.broadcast_to(valid, pb4_lai.shape) & np.isfinite(pb4_lai) & np.isfinite(st_lai)

        def metrics(a, b, mask):
            d = np.asarray(a)[mask] - np.asarray(b)[mask]
            if d.size == 0:
                return (np.nan, np.nan, np.nan)
            return (float(np.mean(np.abs(d))), float(np.sqrt(np.mean(d*d))), float(np.mean(d)))

        npp_mae, npp_rmse, npp_bias = metrics(pb4_opt_npp, st_opt_npp, npp_valid)
        lai_mae, lai_rmse, lai_bias = metrics(pb4_opt_lai, st_opt_lai, lai_valid)
        pft_npp_mae, pft_npp_rmse, _ = metrics(pb4_npp, st_npp, pft_valid)
        pft_lai_mae, pft_lai_rmse, _ = metrics(pb4_lai, st_lai, pft_lai_valid)
        summary_rows.append({
            'pb4_case': case_label, 'age_ka': age, 'valid_cells': int(valid.sum()),
            'biome_agreement_pct': 100.0 * float(np.mean(biome_match)),
            'biome_mismatch_cells': int((~biome_match).sum()),
            'dominant_pft_agreement_pct': 100.0 * float(np.mean(optpft_match)) if optpft_match.size else np.nan,
            'pb4_co2_ppm': float(co2),
            'optimal_npp_mae_gC_m2_yr': npp_mae, 'optimal_npp_rmse_gC_m2_yr': npp_rmse, 'optimal_npp_bias_pb4_minus_biome4': npp_bias,
            'optimal_lai_mae': lai_mae, 'optimal_lai_rmse': lai_rmse, 'optimal_lai_bias_pb4_minus_biome4': lai_bias,
            'all_pft_npp_mae_gC_m2_yr': pft_npp_mae, 'all_pft_npp_rmse_gC_m2_yr': pft_npp_rmse,
            'all_pft_lai_mae': pft_lai_mae, 'all_pft_lai_rmse': pft_lai_rmse,
        })
        for r, c in zip(*np.where(valid)):
            cell_rows.append({
                'pb4_case': case_label, 'age_ka': age, 'row': int(r), 'col': int(c),
                'pb4_biome_id': int(pb4_biome[r,c]), 'standalone_biome_id': int(st_biome[r,c]),
                'pb4_optpft': int(pb4_optpft[r,c]) if np.isfinite(pb4_optpft[r,c]) else np.nan,
                'standalone_optpft': int(st_optpft[r,c]) if np.isfinite(st_optpft[r,c]) else np.nan,
                'pb4_opt_npp': float(pb4_opt_npp[r,c]), 'standalone_opt_npp': float(st_opt_npp[r,c]),
                'pb4_opt_lai': float(pb4_opt_lai[r,c]), 'standalone_opt_lai': float(st_opt_lai[r,c]),
                'soil_depth_m': float(h[r,c]), 'elevation_m': float(z[r,c]),
            })
        for p in range(1, 14):
            mask = valid & np.isfinite(pb4_npp[p-1]) & np.isfinite(st_npp[p-1])
            nmae, nrmse, _ = metrics(pb4_npp[p-1], st_npp[p-1], mask)
            lmae, lrmse, _ = metrics(pb4_lai[p-1], st_lai[p-1], mask)
            pft_rows.append({'pb4_case': case_label, 'age_ka': age, 'pft': p, 'cells': int(mask.sum()),
                             'npp_mae_gC_m2_yr': nmae, 'npp_rmse_gC_m2_yr': nrmse,
                             'lai_mae': lmae, 'lai_rmse': lrmse})
        print(f"[COMPARE] {case_label} | {age:g} ka | biome agreement={summary_rows[-1]['biome_agreement_pct']:.1f}% | NPP RMSE={npp_rmse:.3f} | LAI RMSE={lai_rmse:.3f}", flush=True)

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out_root / 'comparison_summary.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(cell_rows).to_csv(out_root / 'comparison_by_cell.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(pft_rows).to_csv(out_root / 'comparison_by_pft.csv', index=False, encoding='utf-8-sig')
    fig, axes = plt.subplots(3, 1, figsize=(10, 11), constrained_layout=True)
    for case_label, g in summary.groupby('pb4_case'):
        g = g.sort_values('age_ka')
        axes[0].plot(g.age_ka, g.biome_agreement_pct, marker='o', label=case_label)
        axes[1].plot(g.age_ka, g.optimal_npp_rmse_gC_m2_yr, marker='o', label=case_label)
        axes[2].plot(g.age_ka, g.optimal_lai_rmse, marker='o', label=case_label)
    axes[0].set_ylabel('Biome agreement (%)')
    axes[0].set_ylim(0, 100)
    axes[1].set_ylabel('Optimal NPP RMSE (gC m$^{-2}$ yr$^{-1}$)')
    axes[2].set_ylabel('Optimal LAI RMSE')
    axes[2].set_xlabel('Age (ka BP)')
    for ax in axes:
        ax.invert_xaxis()
        ax.grid(alpha=.25)
        ax.legend(frameon=False)
    fig.savefig(out_root / 'comparison_over_time.png', dpi=180)
    plt.close(fig)
    metadata = {
        'PB4Studio_mode': 'comparison (static + dynamic)',
        'PB4Studio_BIOME4_variant': cfg.science.biome4_variant,
        'standalone_model': 'BIOME4-main original v4.2b2 source and driver',
        'ages_ka': AGES, 'grid_shape': list(igrid.shape), 'active_cells': int(igrid.land.sum()),
        'grid_crs': str(igrid.crs), 'resolution_m': float(igrid.resolution_m),
        'soil_comparison': 'same PB4 snapshot soil depth; McKenzie2003 AWC stores mapped to six native BIOME4 layers; same Ksat values',
        'climate_comparison': 'same PB4 monthly temperature, precipitation, cloudiness, Tmin, and time-varying CO2 at each age',
        'known_structural_difference': 'standalone BIOME4 has no soil-depth input/root-depth adapter; PB4Studio applies McKenzie2003/Jackson1996 depth-dependent root weighting and PFT5/PFT6 climate-sieve patches',
        'interpretation': 'Differences are model-structure/parameterization differences under matched climate and hydraulic stores, not a strict bitwise regression test.'
    }
    (out_root / 'comparison_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
