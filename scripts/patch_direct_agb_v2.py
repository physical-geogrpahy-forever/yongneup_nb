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

# Julia 1.11 dotted operators + H=0 bare boundary + official TREED realized-vegetation filter
p = ROOT/'julia'/'run_120ka.jl'
s = p.read_text()
s, n = re.subn(r'[ \t]*(\.\*|\./|\.\+|\.\-)[ \t]*', r' \1 ', s)
needle = '''        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)\n'''
replacement = '''        # BARE_SOIL_BOUNDARY_H_ZERO: no soil storage means no terrestrial vegetation.\n        if Float64(df.soil_depth_m[1]) <= 0.0\n            cap=0.0; precip=Float64.(df.precip_mm_month); days=Float64.(df.days)\n            rows,jan_final=simulate_bucket(cap,0.0,precip,days,zeros(Float64,12))\n            new_es[cell]=zeros(Float64,12); new_jan[cell]=0.0\n            push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=0.0,awc_capacity_mm=0.0,\n                converged=true,iterations=0,convergence_error=0.0,woody_productive=false,latent_H_m=0.0,latent_a_ll_yr=0.0,latent_C_leaf_gC_individual=0.0,raw_NPP_gC_m2_yr=0.0,\n                H_m=0.0,a_ll_yr=0.0,C_leaf_gC_individual=0.0,seasonality=0.0,r_s_r=0.0,LAI=0.0,FPC=0.0,GPP_gC_m2_yr=0.0,NPP_gC_m2_yr=0.0,AET_mm_yr=0.0,\n                Net_C_gain_gC_m2_yr=0.0,AGB_C_g_m2_component_sum=0.0,BGB_C_g_m2_component_sum=0.0))\n            md=DataFrame(rows); md[!,:cell_id]=fill(cell,nrow(md)); md[!,:row]=fill(Int(df.row[1]),nrow(md)); md[!,:col]=fill(Int(df.col[1]),nrow(md)); append!(monthly,md;cols=:union)\n            continue\n        end\n        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)\n'''
assert s.count(needle) == 1
s = s.replace(needle,replacement)

# Official TREED semantics: NPP<=0 (or non-positive H) means the realized woody vegetation is absent.
# This is applied INSIDE the soil-water fixed point so an unproductive woody state has realized AET=0.
# The latent/frozen primary traits are not modified and can reappear at a later age if climate becomes productive again.
old = '        rows,jan_new=simulate_bucket(cap,jan,precip,days,Float64.(ev.gpp.AET_monthly_mm)); es_new=[r.esupply_mm_day for r in rows]'
new = '''        woody_productive=isfinite(ev.npp) && ev.npp>0.0 && isfinite(ev.tr.H) && ev.tr.H>0.0\n        aet_req=woody_productive ? Float64.(ev.gpp.AET_monthly_mm) : zeros(Float64,12)\n        rows,jan_new=simulate_bucket(cap,jan,precip,days,aet_req); es_new=[r.esupply_mm_day for r in rows]'''
assert s.count(old) == 1
s = s.replace(old,new)

old = '            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,Float64.(final.gpp.AET_monthly_mm))'
new = '''            woody_productive_final=isfinite(final.npp) && final.npp>0.0 && isfinite(final.tr.H) && final.tr.H>0.0\n            aet_req_final=woody_productive_final ? Float64.(final.gpp.AET_monthly_mm) : zeros(Float64,12)\n            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,aet_req_final)'''
assert s.count(old) == 1
s = s.replace(old,new)

# Replace the realized summary block while preserving latent traits for diagnosis.
start_marker = '        tr=ev.tr; new_es[cell]=Float64.(conv.es); new_jan[cell]=Float64(conv.jan)\n'
end_marker = '            Net_C_gain_gC_m2_yr=ev.net,AGB_C_g_m2_component_sum=ev.agb,BGB_C_g_m2_component_sum=ev.bgb))'
assert s.count(start_marker) == 1
assert s.count(end_marker) == 1
start = s.index(start_marker)
end = s.index(end_marker,start) + len(end_marker)
summary_replacement = '''        tr=ev.tr; new_es[cell]=Float64.(conv.es); new_jan[cell]=Float64(conv.jan)\n        woody_productive=isfinite(ev.npp) && ev.npp>0.0 && isfinite(tr.H) && tr.H>0.0\n        H_out=woody_productive ? tr.H : 0.0\n        a_ll_out=woody_productive ? tr.a_ll : 0.0\n        C_leaf_out=woody_productive ? tr.C_leaf : 0.0\n        LAI_out=woody_productive ? tr.LAI : 0.0\n        FPC_out=woody_productive ? tr.FPC : 0.0\n        GPP_out=woody_productive ? ev.gpp.GPP : 0.0\n        NPP_out=woody_productive ? ev.npp : 0.0\n        AET_out=woody_productive ? ev.gpp.AET : 0.0\n        Net_out=woody_productive ? ev.net : 0.0\n        AGB_out=woody_productive ? ev.agb : 0.0\n        BGB_out=woody_productive ? ev.bgb : 0.0\n        push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=Float64(df.soil_depth_m[1]),awc_capacity_mm=conv.capacity,\n            converged=conv.converged,iterations=conv.iterations,convergence_error=conv.error,woody_productive=woody_productive,latent_H_m=tr.H,latent_a_ll_yr=tr.a_ll,latent_C_leaf_gC_individual=tr.C_leaf,raw_NPP_gC_m2_yr=ev.npp,\n            H_m=H_out,a_ll_yr=a_ll_out,C_leaf_gC_individual=C_leaf_out,seasonality=tr.seasonality,r_s_r=tr.r_s_r,LAI=LAI_out,FPC=FPC_out,GPP_gC_m2_yr=GPP_out,NPP_gC_m2_yr=NPP_out,AET_mm_yr=AET_out,\n            Net_C_gain_gC_m2_yr=Net_out,AGB_C_g_m2_component_sum=AGB_out,BGB_C_g_m2_component_sum=BGB_out))'''
s = s[:start] + summary_replacement + s[end:]
p.write_text(s)

# Direct TREED AGB-C -> Pelletier dry biomass kg/m2, with raw-NPP/productivity audit fields.
p = ROOT/'python'/'run_geomorph_step.py'
s = p.read_text()
replacements = [
("npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float)",
 "npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float); agb_c=np.full(shape,np.nan,float); raw_npp=np.full(shape,np.nan,float); woody_productive=np.full(shape,False,bool)"),
("        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)",
 "        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)\n        if 'AGB_C_g_m2_component_sum' in cols: agb_c[rr,cc]=float(x.AGB_C_g_m2_component_sum)\n        if 'raw_NPP_gC_m2_yr' in cols: raw_npp[rr,cc]=float(x.raw_NPP_gC_m2_yr)\n        if 'woody_productive' in cols: woody_productive[rr,cc]=bool(x.woody_productive)"),
("    return npp,aet,lai,htrait,all_yr,cleaf",
 "    return npp,aet,lai,htrait,all_yr,cleaf,agb_c,raw_npp,woody_productive"),
("    npp,aet,lai,htrait,all_yr,cleaf=assemble(summary,monthly,z.shape)",
 "    npp,aet,lai,htrait,all_yr,cleaf,agb_c,raw_npp,woody_productive=assemble(summary,monthly,z.shape)"),
("    agb=np.where(land,np.maximum(npp,0.0)*0.010,np.nan)",
 "    agb_carbon_fraction=0.47\n    agb=np.where(land & np.isfinite(agb_c),np.maximum(agb_c,0.0)/(1000.0*agb_carbon_fraction),np.nan)\n    bad_agb=land & ~np.isfinite(agb)\n    if np.any(bad_agb):\n        rr,cc=np.argwhere(bad_agb)[0]\n        raise ValueError(f'Non-finite direct TREED AGB at row={rr}, col={cc}')"),
("'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_LAI':",
 "'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_agb_C_g_m2':float(np.nanmean(agb_c[land])),'mean_agb_dry_kg_m2':float(np.nanmean(agb[land])),'unproductive_woody_cells':int(np.count_nonzero(land & (h>0) & np.isfinite(raw_npp) & (~woody_productive))),'mean_LAI':"),
("'EEMT_MJ_m2_yr':eemt[rr,cc],'LAI':lai[rr,cc]",
 "'EEMT_MJ_m2_yr':eemt[rr,cc],'raw_NPP_gC_m2_yr':raw_npp[rr,cc],'woody_productive':bool(woody_productive[rr,cc]),'AGB_C_g_m2_component_sum':agb_c[rr,cc],'Pelletier_AGB_dry_kg_m2':agb[rr,cc],'LAI':lai[rr,cc]")
]
for old,new in replacements:
    assert s.count(old) == 1, old[:80]
    s = s.replace(old,new)
assert 'np.maximum(npp,0.0)*0.010' not in s
p.write_text(s)
print('DIRECT_AGB_OFFICIAL_REALIZED_FILTER_PATCH_OK dotted_fixes=', n)
