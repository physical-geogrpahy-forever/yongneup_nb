from pathlib import Path
import re

ROOT = Path('treed120')

# OptimizationSolution compatibility
p = ROOT/'src'/'TREED_physiological_functions.jl'
s = p.read_text()
old = '    a_ll_optimized, C_leaf_optimized, H_optimized = Optimization.solve(prob, ECA(), maxiters = iters, abstol = 50)'
new = '    opt_solution = Optimization.solve(prob, ECA(), maxiters = iters, abstol = 50)\n    a_ll_optimized, C_leaf_optimized, H_optimized = opt_solution.u'
assert s.count(old) == 1
p.write_text(s.replace(old,new))

# Julia 1.11 dotted operators + H=0 bare boundary
p = ROOT/'julia'/'run_120ka.jl'
s = p.read_text()
s, n = re.subn(r'[ \t]*(\.\*|\./|\.\+|\.\-)[ \t]*', r' \1 ', s)
needle = '''        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)\n'''
replacement = '''        # BARE_SOIL_BOUNDARY_H_ZERO: no soil storage means no terrestrial vegetation.\n        if Float64(df.soil_depth_m[1]) <= 0.0\n            cap=0.0; precip=Float64.(df.precip_mm_month); days=Float64.(df.days)\n            rows,jan_final=simulate_bucket(cap,0.0,precip,days,zeros(Float64,12))\n            new_es[cell]=zeros(Float64,12); new_jan[cell]=0.0\n            push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=0.0,awc_capacity_mm=0.0,\n                converged=true,iterations=0,convergence_error=0.0,H_m=0.0,a_ll_yr=0.0,C_leaf_gC_individual=0.0,\n                seasonality=0.0,r_s_r=0.0,LAI=0.0,FPC=0.0,GPP_gC_m2_yr=0.0,NPP_gC_m2_yr=0.0,AET_mm_yr=0.0,\n                Net_C_gain_gC_m2_yr=0.0,AGB_C_g_m2_component_sum=0.0,BGB_C_g_m2_component_sum=0.0))\n            md=DataFrame(rows); md[!,:cell_id]=fill(cell,nrow(md)); md[!,:row]=fill(Int(df.row[1]),nrow(md)); md[!,:col]=fill(Int(df.col[1]),nrow(md)); append!(monthly,md;cols=:union)\n            continue\n        end\n        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)\n'''
assert s.count(needle) == 1
p.write_text(s.replace(needle,replacement))

# Direct TREED AGB-C -> Pelletier dry biomass kg/m2
p = ROOT/'python'/'run_geomorph_step.py'
s = p.read_text()
replacements = [
("npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float)",
 "npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float); agb_c=np.full(shape,np.nan,float)"),
("        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)",
 "        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)\n        if 'AGB_C_g_m2_component_sum' in cols: agb_c[rr,cc]=float(x.AGB_C_g_m2_component_sum)"),
("    return npp,aet,lai,htrait,all_yr,cleaf",
 "    return npp,aet,lai,htrait,all_yr,cleaf,agb_c"),
("    npp,aet,lai,htrait,all_yr,cleaf=assemble(summary,monthly,z.shape)",
 "    npp,aet,lai,htrait,all_yr,cleaf,agb_c=assemble(summary,monthly,z.shape)"),
("    agb=np.where(land,np.maximum(npp,0.0)*0.010,np.nan)",
 "    agb_carbon_fraction=0.47\n    agb=np.where(land & np.isfinite(agb_c),np.maximum(agb_c,0.0)/(1000.0*agb_carbon_fraction),np.nan)\n    bad_agb=land & ~np.isfinite(agb)\n    if np.any(bad_agb):\n        rr,cc=np.argwhere(bad_agb)[0]\n        raise ValueError(f'Non-finite direct TREED AGB at row={rr}, col={cc}')"),
("'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_LAI':",
 "'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_agb_C_g_m2':float(np.nanmean(agb_c[land])),'mean_agb_dry_kg_m2':float(np.nanmean(agb[land])),'mean_LAI':"),
("'EEMT_MJ_m2_yr':eemt[rr,cc],'LAI':lai[rr,cc]",
 "'EEMT_MJ_m2_yr':eemt[rr,cc],'AGB_C_g_m2_component_sum':agb_c[rr,cc],'Pelletier_AGB_dry_kg_m2':agb[rr,cc],'LAI':lai[rr,cc]")
]
for old,new in replacements:
    assert s.count(old) == 1, old[:80]
    s = s.replace(old,new)
assert 'np.maximum(npp,0.0)*0.010' not in s
p.write_text(s)
print('DIRECT_AGB_V2_PATCH_OK dotted_fixes=', n)
