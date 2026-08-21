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

# Julia 1.11 dotted operators + H=0 bare boundary + selective realized-vegetation filter
p = ROOT/'julia'/'run_120ka.jl'
s = p.read_text()
s, n = re.subn(r'[ \t]*(\.\*|\./|\.\+|\.\-)[ \t]*', r' \1 ', s)
needle = '''        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)\n'''
replacement = '''        # BARE_SOIL_BOUNDARY_H_ZERO: no soil storage means no terrestrial vegetation.\n        if Float64(df.soil_depth_m[1]) <= 0.0\n            cap=0.0; precip=Float64.(df.precip_mm_month); days=Float64.(df.days)\n            rows,jan_final=simulate_bucket(cap,0.0,precip,days,zeros(Float64,12))\n            new_es[cell]=zeros(Float64,12); new_jan[cell]=0.0\n            push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=0.0,awc_capacity_mm=0.0,\n                converged=true,iterations=0,convergence_error=0.0,optimizer_pathological=false,inherited_initial_pathology=false,maladapted_frozen=false,woody_productive=false,latent_H_m=0.0,latent_a_ll_yr=0.0,latent_C_leaf_gC_individual=0.0,raw_NPP_gC_m2_yr=0.0,\n                H_m=0.0,a_ll_yr=0.0,C_leaf_gC_individual=0.0,seasonality=0.0,r_s_r=0.0,LAI=0.0,FPC=0.0,GPP_gC_m2_yr=0.0,NPP_gC_m2_yr=0.0,AET_mm_yr=0.0,\n                Net_C_gain_gC_m2_yr=0.0,AGB_C_g_m2_component_sum=0.0,BGB_C_g_m2_component_sum=0.0))\n            md=DataFrame(rows); md[!,:cell_id]=fill(cell,nrow(md)); md[!,:row]=fill(Int(df.row[1]),nrow(md)); md[!,:col]=fill(Int(df.col[1]),nrow(md)); append!(monthly,md;cols=:union)\n            continue\n        end\n        inherited_initial_pathology = mode=="frozen" && cell in frozen_initial_pathology\n        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed,inherited_initial_pathology=inherited_initial_pathology)\n'''
assert s.count(needle) == 1
s = s.replace(needle,replacement)

# Production optimizer bounds H to [1,50] m. The audited dynamic failure fringe is
# characterized by NPP<=0 together with H pinned to that lower bound. Use only a
# numerical tolerance around the known optimizer bound; do not add an ecological
# LAI/AGB threshold. Frozen NPP<=0 caused by later climate is maladaptation of the
# fixed 120-ka strategy, not a bare-state criterion. The exceptional frozen cell(s)
# whose fixed trait was already a 120-ka optimizer pathology inherit the same
# realized-zero treatment as dynamic so both arms start from the same realized state.
anchor = 'const SNAPSHOTS=Set([120,100,80,60,40,20,10,5,0])\n'
insert = '''const H_OPT_LOWER_BOUND=1.0\nconst H_OPT_BOUND_TOL=1e-3\n\nraw_unproductive(ev) = !isfinite(ev.npp) || ev.npp<=0.0\nat_optimizer_H_lower_bound(ev) = isfinite(ev.tr.H) && ev.tr.H <= H_OPT_LOWER_BOUND + H_OPT_BOUND_TOL\n\nfunction dynamic_optimizer_pathological(mode::String, ev)\n    mode=="dynamic" && raw_unproductive(ev) && at_optimizer_H_lower_bound(ev)\nend\n\nfunction frozen_inherited_pathological(mode::String, ev, inherited_initial_pathology::Bool)\n    mode=="frozen" && inherited_initial_pathology && raw_unproductive(ev)\nend\n\nfunction frozen_maladapted(mode::String, ev, inherited_initial_pathology::Bool=false)\n    mode=="frozen" && !inherited_initial_pathology && raw_unproductive(ev)\nend\n'''
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + insert)

# Carry provenance of the 120-ka initialization pathology through the frozen arm.
old = 'function coupled_cell(df::DataFrame; mode::String, fixed_primary=nothing, es_init=nothing, jan_init=nothing, tol=1e-4,maxiter=100,seed=240819)'
new = 'function coupled_cell(df::DataFrame; mode::String, fixed_primary=nothing, es_init=nothing, jan_init=nothing, tol=1e-4,maxiter=100,seed=240819,inherited_initial_pathology=false)'
assert s.count(old) == 1
s = s.replace(old,new)

# Apply realized AET=0 inside the fixed point only to (a) current dynamic optimizer
# pathology or (b) the same pathology inherited by frozen from the common 120-ka
# initialization. Ordinary frozen maladaptation keeps its physiological AET/NPP.
old = '        rows,jan_new=simulate_bucket(cap,jan,precip,days,Float64.(ev.gpp.AET_monthly_mm)); es_new=[r.esupply_mm_day for r in rows]'
new = '''        optimizer_pathological=dynamic_optimizer_pathological(mode,ev)\n        inherited_pathological=frozen_inherited_pathological(mode,ev,Bool(inherited_initial_pathology))\n        realized_pathological=optimizer_pathological || inherited_pathological\n        aet_req=realized_pathological ? zeros(Float64,12) : Float64.(ev.gpp.AET_monthly_mm)\n        rows,jan_new=simulate_bucket(cap,jan,precip,days,aet_req); es_new=[r.esupply_mm_day for r in rows]'''
assert s.count(old) == 1
s = s.replace(old,new)

old = '            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,Float64.(final.gpp.AET_monthly_mm))'
new = '''            optimizer_pathological_final=dynamic_optimizer_pathological(mode,final)\n            inherited_pathological_final=frozen_inherited_pathological(mode,final,Bool(inherited_initial_pathology))\n            realized_pathological_final=optimizer_pathological_final || inherited_pathological_final\n            aet_req_final=realized_pathological_final ? zeros(Float64,12) : Float64.(final.gpp.AET_monthly_mm)\n            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,aet_req_final)'''
assert s.count(old) == 1
s = s.replace(old,new)

# The frozen writer must know which fixed traits came from an invalid 120-ka optimizer
# boundary solution. All other frozen negative-NPP cells are later maladaptation.
old = 'function write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path)'
new = 'function write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path,frozen_initial_pathology)'
assert s.count(old) == 1
s = s.replace(old,new)

# Replace realized summary block. Dynamic/current and inherited-initial pathologies
# are realized as zero woody vegetation but latent traits/raw NPP are retained.
# Ordinary frozen maladaptation is flagged only and keeps standing structure/fluxes.
start_marker = '        tr=ev.tr; new_es[cell]=Float64.(conv.es); new_jan[cell]=Float64(conv.jan)\n'
end_marker = '            Net_C_gain_gC_m2_yr=ev.net,AGB_C_g_m2_component_sum=ev.agb,BGB_C_g_m2_component_sum=ev.bgb))'
assert s.count(start_marker) == 1
assert s.count(end_marker) == 1
start = s.index(start_marker)
end = s.index(end_marker,start) + len(end_marker)
summary_replacement = '''        tr=ev.tr; new_es[cell]=Float64.(conv.es); new_jan[cell]=Float64(conv.jan)\n        optimizer_pathological=dynamic_optimizer_pathological(mode,ev)\n        inherited_pathological=frozen_inherited_pathological(mode,ev,Bool(inherited_initial_pathology))\n        maladapted_frozen=frozen_maladapted(mode,ev,Bool(inherited_initial_pathology))\n        realized_pathological=optimizer_pathological || inherited_pathological\n        woody_productive=!realized_pathological && isfinite(ev.npp) && ev.npp>0.0 && isfinite(tr.H) && tr.H>0.0\n        H_out=realized_pathological ? 0.0 : tr.H\n        a_ll_out=realized_pathological ? 0.0 : tr.a_ll\n        C_leaf_out=realized_pathological ? 0.0 : tr.C_leaf\n        LAI_out=realized_pathological ? 0.0 : tr.LAI\n        FPC_out=realized_pathological ? 0.0 : tr.FPC\n        GPP_out=realized_pathological ? 0.0 : ev.gpp.GPP\n        NPP_out=realized_pathological ? 0.0 : ev.npp\n        AET_out=realized_pathological ? 0.0 : ev.gpp.AET\n        Net_out=realized_pathological ? 0.0 : ev.net\n        AGB_out=realized_pathological ? 0.0 : ev.agb\n        BGB_out=realized_pathological ? 0.0 : ev.bgb\n        push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=Float64(df.soil_depth_m[1]),awc_capacity_mm=conv.capacity,\n            converged=conv.converged,iterations=conv.iterations,convergence_error=conv.error,optimizer_pathological=optimizer_pathological,inherited_initial_pathology=inherited_pathological,maladapted_frozen=maladapted_frozen,woody_productive=woody_productive,latent_H_m=tr.H,latent_a_ll_yr=tr.a_ll,latent_C_leaf_gC_individual=tr.C_leaf,raw_NPP_gC_m2_yr=ev.npp,\n            H_m=H_out,a_ll_yr=a_ll_out,C_leaf_gC_individual=C_leaf_out,seasonality=tr.seasonality,r_s_r=tr.r_s_r,LAI=LAI_out,FPC=FPC_out,GPP_gC_m2_yr=GPP_out,NPP_gC_m2_yr=NPP_out,AET_mm_yr=AET_out,\n            Net_C_gain_gC_m2_yr=Net_out,AGB_C_g_m2_component_sum=AGB_out,BGB_C_g_m2_component_sum=BGB_out))'''
s = s[:start] + summary_replacement + s[end:]

# Record which common 120-ka optimized traits are themselves boundary pathologies.
old = '    fixed=Dict{Int,Any}(); dummy_es=Dict{Int,Vector{Float64}}(); dummy_jan=Dict{Int,Float64}()'
new = '    fixed=Dict{Int,Any}(); dummy_es=Dict{Int,Vector{Float64}}(); dummy_jan=Dict{Int,Float64}(); initial_pathology=Set{Int}()'
assert s.count(old) == 1
s = s.replace(old,new)
old = '        fixed[cell]=ev.primary; dummy_es[cell]=Float64.(conv.es); dummy_jan[cell]=Float64(conv.jan)'
new = '        fixed[cell]=ev.primary; dummy_es[cell]=Float64.(conv.es); dummy_jan[cell]=Float64(conv.jan); dynamic_optimizer_pathological("dynamic",ev) && push!(initial_pathology,cell)'
assert s.count(old) == 1
s = s.replace(old,new)
old = '    return fixed,dummy_es,dummy_jan\nend\n\nfunction main()'
new = '    return fixed,dummy_es,dummy_jan,initial_pathology\nend\n\nfunction main()'
assert s.count(old) == 1
s = s.replace(old,new)

old = '    fixed_traits=Dict{Int,Any}(); prev_es=Dict{Int,Vector{Float64}}(); prev_jan=Dict{Int,Float64}(); metrics=DataFrame()'
new = '    fixed_traits=Dict{Int,Any}(); prev_es=Dict{Int,Vector{Float64}}(); prev_jan=Dict{Int,Float64}(); frozen_initial_pathology=Set{Int}(); metrics=DataFrame()'
assert s.count(old) == 1
s = s.replace(old,new)
old = '            fixed_traits,prev_es,prev_jan=initialize_frozen_traits(inp)'
new = '            fixed_traits,prev_es,prev_jan,frozen_initial_pathology=initialize_frozen_traits(inp)'
assert s.count(old) == 1
s = s.replace(old,new)
old = '        prev_es,prev_jan,summary=write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path)'
new = '        prev_es,prev_jan,summary=write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path,frozen_initial_pathology)'
assert s.count(old) == 1
s = s.replace(old,new)
p.write_text(s)

# Direct TREED AGB-C -> Pelletier dry biomass kg/m2, with pathology/maladaptation audit fields.
p = ROOT/'python'/'run_geomorph_step.py'
s = p.read_text()
replacements = [
("npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float)",
 "npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float); latent_h=np.full(shape,np.nan,float); latent_all=np.full(shape,np.nan,float); latent_cleaf=np.full(shape,np.nan,float); agb_c=np.full(shape,np.nan,float); raw_npp=np.full(shape,np.nan,float); woody_productive=np.full(shape,False,bool); optimizer_pathological=np.full(shape,False,bool); inherited_initial_pathology=np.full(shape,False,bool); maladapted_frozen=np.full(shape,False,bool)"),
("        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)",
 "        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)\n        if 'latent_H_m' in cols: latent_h[rr,cc]=float(x.latent_H_m)\n        if 'latent_a_ll_yr' in cols: latent_all[rr,cc]=float(x.latent_a_ll_yr)\n        if 'latent_C_leaf_gC_individual' in cols: latent_cleaf[rr,cc]=float(x.latent_C_leaf_gC_individual)\n        if 'AGB_C_g_m2_component_sum' in cols: agb_c[rr,cc]=float(x.AGB_C_g_m2_component_sum)\n        if 'raw_NPP_gC_m2_yr' in cols: raw_npp[rr,cc]=float(x.raw_NPP_gC_m2_yr)\n        if 'woody_productive' in cols: woody_productive[rr,cc]=bool(x.woody_productive)\n        if 'optimizer_pathological' in cols: optimizer_pathological[rr,cc]=bool(x.optimizer_pathological)\n        if 'inherited_initial_pathology' in cols: inherited_initial_pathology[rr,cc]=bool(x.inherited_initial_pathology)\n        if 'maladapted_frozen' in cols: maladapted_frozen[rr,cc]=bool(x.maladapted_frozen)"),
("    return npp,aet,lai,htrait,all_yr,cleaf",
 "    return npp,aet,lai,htrait,all_yr,cleaf,latent_h,latent_all,latent_cleaf,agb_c,raw_npp,woody_productive,optimizer_pathological,inherited_initial_pathology,maladapted_frozen"),
("    npp,aet,lai,htrait,all_yr,cleaf=assemble(summary,monthly,z.shape)",
 "    npp,aet,lai,htrait,all_yr,cleaf,latent_h,latent_all,latent_cleaf,agb_c,raw_npp,woody_productive,optimizer_pathological,inherited_initial_pathology,maladapted_frozen=assemble(summary,monthly,z.shape)"),
("    agb=np.where(land,np.maximum(npp,0.0)*0.010,np.nan)",
 "    agb_carbon_fraction=0.47\n    agb=np.where(land & np.isfinite(agb_c),np.maximum(agb_c,0.0)/(1000.0*agb_carbon_fraction),np.nan)\n    bad_agb=land & ~np.isfinite(agb)\n    if np.any(bad_agb):\n        rr,cc=np.argwhere(bad_agb)[0]\n        raise ValueError(f'Non-finite direct TREED AGB at row={rr}, col={cc}')"),
("'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_LAI':",
 "'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_agb_C_g_m2':float(np.nanmean(agb_c[land])),'mean_agb_dry_kg_m2':float(np.nanmean(agb[land])),'optimizer_pathological_cells':int(np.count_nonzero(land & optimizer_pathological)),'inherited_initial_pathology_cells':int(np.count_nonzero(land & inherited_initial_pathology)),'maladapted_frozen_cells':int(np.count_nonzero(land & maladapted_frozen)),'unproductive_woody_cells':int(np.count_nonzero(land & (h>0) & np.isfinite(raw_npp) & (~woody_productive))),'mean_LAI':"),
("'EEMT_MJ_m2_yr':eemt[rr,cc],'LAI':lai[rr,cc]",
 "'EEMT_MJ_m2_yr':eemt[rr,cc],'raw_NPP_gC_m2_yr':raw_npp[rr,cc],'woody_productive':bool(woody_productive[rr,cc]),'optimizer_pathological':bool(optimizer_pathological[rr,cc]),'inherited_initial_pathology':bool(inherited_initial_pathology[rr,cc]),'maladapted_frozen':bool(maladapted_frozen[rr,cc]),'latent_H_m':latent_h[rr,cc],'latent_a_ll_yr':latent_all[rr,cc],'latent_C_leaf_gC_individual':latent_cleaf[rr,cc],'AGB_C_g_m2_component_sum':agb_c[rr,cc],'Pelletier_AGB_dry_kg_m2':agb[rr,cc],'LAI':lai[rr,cc]")
]
for old,new in replacements:
    assert s.count(old) == 1, old[:80]
    s = s.replace(old,new)
assert 'np.maximum(npp,0.0)*0.010' not in s
p.write_text(s)
print('DIRECT_AGB_SELECTIVE_DYNAMIC_PATHOLOGY_PATCH_OK dotted_fixes=', n)
