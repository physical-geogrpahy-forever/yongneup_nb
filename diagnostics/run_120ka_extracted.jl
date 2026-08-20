using CSV
using DataFrames
using Random
using Statistics

const ROOT = normpath(joinpath(@__DIR__, ".."))
include(joinpath(ROOT,"src","TREED_core.jl"))
using .TREEDCore

const EMAX=5.0
const AWC_PROFILE=[(0.00,0.05,237.0),(0.05,0.15,232.0),(0.15,0.30,218.0),(0.30,0.60,207.0),(0.60,1.00,198.0),(1.00,2.00,179.0)]
const DOIS=[15,46,73,104,134,166,196,227,259,288,319,349]
const SNAPSHOTS=Set([120,100,80,60,40,20,10,5,0])

function awc_total_mm(depth_m::Float64; maxdepth=1.5)
    h=clamp(depth_m,0.0,maxdepth); total=0.0
    for (a,b,awc) in AWC_PROFILE
        lo=max(0.0,a); hi=min(h,b); hi>lo && (total+=(hi-lo)*awc)
    end
    total
end

function base_env(df::DataFrame; esupply=nothing)
    tair=Float64.(df.tair_C); precip=Float64.(df.precip_m_day_for_TREED_env)
    clt=Float64.(df.cloud_fraction); rsds=Float64.(df.rsds_W_m2_BIOME4_bridge).*86400.*1e-6
    rss=rsds.*(1-0.15); rls=(0.2 .+ 0.8.*(1 .- clt)).*(107 .- tair).*86400.*1e-6.*(-1)
    lat=Float64(df.lat_deg[1]); daylength=[max(1.0,TREEDCore.daylength_calculation(lat,d)) for d in DOIS]
    return (precip_monthly=precip,Esupply_monthly=esupply,tair_monthly=tair,tair_annual=mean(tair),
        rsds_monthly=rsds,rss_monthly=rss,rls_monthly=rls,daylength=daylength,CO2_ppm=Float64(df.co2_ppm[1]),
        precip_annual=mean(precip))
end

function evaluate_traits(env,tr_primary)
    tr=(H=tr_primary.H,a_ll=tr_primary.a_ll,C_leaf=tr_primary.C_leaf,seasonality=tr_primary.seasonality,r_s_r=tr_primary.r_s_r,
        Tave_optim=tr_primary.Tave_optim,Tmax_optim=tr_primary.Tmax_optim,Tmin_optim=tr_primary.Tmin_optim,Pave_optim=tr_primary.Pave_optim)
    tr=TREEDCore.plant_allometry(tr=tr,par=TREEDCore.pars)
    gpp=TREEDCore.GPP_function_for_optimization(env=env,tr=tr,par=TREEDCore.pars)
    rmaint=TREEDCore.R_maintenance_function(env=env,tr=tr,par=TREEDCore.pars,GPP_out=gpp)
    npp=TREEDCore.calc_NPP(GPP_out=gpp,R_maintenance=rmaint,par=TREEDCore.pars)
    turn=TREEDCore.C_turnover_function(env=env,tr=tr,par=TREEDCore.pars)
    net=TREEDCore.calc_net_C_gain(NPP=npp,C_turnover_total=turn,par=TREEDCore.pars)
    agb=(tr.C_leaf+tr.C_sapwood+tr.C_heartwood)/tr.CA
    bgb=(tr.C_fineroot+tr.C_coarseroot)/tr.CA
    return (tr=tr,gpp=gpp,npp=npp,net=net,agb=agb,bgb=bgb,primary=tr_primary)
end

function evaluate_dynamic(env; seed=240819,iters=20)
    Random.seed!(seed)
    opt=TREEDCore.trait_optimizer(env=env,par=TREEDCore.pars,trait_optimization_function=TREEDCore.trait_optimization_function,iters=iters)
    primary=(H=opt.H_optimized,a_ll=opt.a_ll_optimized,C_leaf=opt.C_leaf_optimized,seasonality=opt.seasonality_optimized,r_s_r=opt.r_s_r_optimized,
        Tave_optim=mean(env.tair_monthly),Tmax_optim=maximum(env.tair_monthly),Tmin_optim=minimum(env.tair_monthly),Pave_optim=mean(env.precip_monthly))
    return evaluate_traits(env,primary)
end

function supply_from_state(storage,cap,precip,days)
    phi=cap<=0 ? 0.0 : clamp(storage/cap,0.0,1.0)
    return min(EMAX*phi,max(0.0,(storage+precip)/days)),phi
end

function simulate_bucket(cap,jan,precip,days,aet_req)
    s=clamp(jan,0.0,cap); rows=NamedTuple[]
    for m in 1:12
        es,phi=supply_from_state(s,cap,precip[m],days[m]); available=s+precip[m]
        aet=min(max(0.0,aet_req[m]),available); after=available-aet; runoff=max(0.0,after-cap); send=clamp(after-runoff,0.0,cap)
        push!(rows,(month=m,storage_start_mm=s,phi_start=phi,esupply_mm_day=es,aet_actual_mm=aet,runoff_mm=runoff,storage_end_mm=send,balance_residual_mm=s+precip[m]-aet-runoff-send)); s=send
    end
    rows,s
end

function coupled_cell(df::DataFrame; mode::String, fixed_primary=nothing, es_init=nothing, jan_init=nothing, tol=1e-4,maxiter=100,seed=240819)
    cap=awc_total_mm(Float64(df.soil_depth_m[1])); precip=Float64.(df.precip_mm_month); days=Float64.(df.days)
    jan=jan_init===nothing ? cap : clamp(Float64(jan_init),0.0,cap)
    es=es_init===nothing ? min.(EMAX,Float64.(df.precip_mean_mm_day)) : clamp.(Float64.(es_init),0.0,EMAX)
    final=nothing; finalrows=nothing; err=Inf
    for k in 1:maxiter
        env=base_env(df;esupply=es)
        ev = mode=="dynamic" ? evaluate_dynamic(env;seed=seed,iters=20) : evaluate_traits(env,fixed_primary)
        rows,jan_new=simulate_bucket(cap,jan,precip,days,Float64.(ev.gpp.AET_monthly_mm)); es_new=[r.esupply_mm_day for r in rows]
        err=max(maximum(abs.(es_new.-es)),abs(jan_new-jan)); final=ev; finalrows=rows; es=es_new; jan=jan_new
        if err<tol
            env2=base_env(df;esupply=es)
            final = mode=="dynamic" ? evaluate_dynamic(env2;seed=seed,iters=20) : evaluate_traits(env2,fixed_primary)
            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,Float64.(final.gpp.AET_monthly_mm))
            return final,finalrows,(converged=true,iterations=k,error=err,capacity=cap,jan=jan_final,es=[r.esupply_mm_day for r in finalrows])
        end
    end
    return final,finalrows,(converged=false,iterations=maxiter,error=err,capacity=cap,jan=jan,es=es)
end

function write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path)
    summary=NamedTuple[]; monthly=DataFrame(); new_es=Dict{Int,Vector{Float64}}(); new_jan=Dict{Int,Float64}()
    for g in groupby(inp,:cell_id)
        df=DataFrame(g); sort!(df,:month); cell=Int(df.cell_id[1]); seed=240819+cell
        fixed_primary = mode=="frozen" ? fixed_traits[cell] : nothing
        es0=haskey(prev_es,cell) ? prev_es[cell] : nothing; jan0=haskey(prev_jan,cell) ? prev_jan[cell] : nothing
        ev,rows,conv=coupled_cell(df;mode=mode,fixed_primary=fixed_primary,es_init=es0,jan_init=jan0,seed=seed)
        if !conv.converged
            error("Soil-water/TREED fixed point failed: mode=$mode cell=$cell err=$(conv.error)")
        end
        tr=ev.tr; new_es[cell]=Float64.(conv.es); new_jan[cell]=Float64(conv.jan)
        push!(summary,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=Float64(df.soil_depth_m[1]),awc_capacity_mm=conv.capacity,
            converged=conv.converged,iterations=conv.iterations,convergence_error=conv.error,H_m=tr.H,a_ll_yr=tr.a_ll,C_leaf_gC_individual=tr.C_leaf,
            seasonality=tr.seasonality,r_s_r=tr.r_s_r,LAI=tr.LAI,FPC=tr.FPC,GPP_gC_m2_yr=ev.gpp.GPP,NPP_gC_m2_yr=ev.npp,AET_mm_yr=ev.gpp.AET,
            Net_C_gain_gC_m2_yr=ev.net,AGB_C_g_m2_component_sum=ev.agb,BGB_C_g_m2_component_sum=ev.bgb))
        md=DataFrame(rows); md[!,:cell_id]=fill(cell,nrow(md)); md[!,:row]=fill(Int(df.row[1]),nrow(md)); md[!,:col]=fill(Int(df.col[1]),nrow(md)); append!(monthly,md;cols=:union)
    end
    CSV.write(summary_path,DataFrame(summary)); CSV.write(monthly_path,monthly)
    return new_es,new_jan,summary
end

function initialize_frozen_traits(inp)
    fixed=Dict{Int,Any}(); dummy_es=Dict{Int,Vector{Float64}}(); dummy_jan=Dict{Int,Float64}()
    # At 120 ka the frozen baseline is initialized from the same fully coupled optimized state.
    for g in groupby(inp,:cell_id)
        df=DataFrame(g); sort!(df,:month); cell=Int(df.cell_id[1]); ev,rows,conv=coupled_cell(df;mode="dynamic",seed=240819+cell)
        conv.converged || error("Frozen initialization failed at cell $cell")
        fixed[cell]=ev.primary; dummy_es[cell]=Float64.(conv.es); dummy_jan[cell]=Float64(conv.jan)
    end
    return fixed,dummy_es,dummy_jan
end

function main()
    mode=length(ARGS)>=1 ? ARGS[1] : "dynamic"
    mode in ("dynamic","frozen") || error("mode must be dynamic or frozen")
    outdir=joinpath(ROOT,"results",mode); work=joinpath(ROOT,"work",mode); mkpath(outdir); mkpath(work); mkpath(joinpath(outdir,"snapshots"))
    state=joinpath(work,"state_120.npz"); cp(joinpath(ROOT,"inputs","init_grid.npz"),state;force=true)
    fixed_traits=Dict{Int,Any}(); prev_es=Dict{Int,Vector{Float64}}(); prev_jan=Dict{Int,Float64}(); metrics=DataFrame()
    for age in 120:-1:0
        forcing=joinpath(work,"forcing_$(age).csv")
        run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age $age --state $state --out $forcing`)
        inp=CSV.read(forcing,DataFrame)
        if mode=="frozen" && age==120
            fixed_traits,prev_es,prev_jan=initialize_frozen_traits(inp)
        end
        summary_path=joinpath(work,"summary.csv"); monthly_path=joinpath(work,"monthly.csv")
        prev_es,prev_jan,summary=write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path)
        nextstate=joinpath(work,"state_next.npz"); metric_path=joinpath(work,"metric.csv")
        snapshot = age in SNAPSHOTS ? joinpath(outdir,"snapshots","snapshot_$(lpad(age,3,'0'))ka.csv") : ""
        cmd=`python $(joinpath(ROOT,"python","run_geomorph_step.py")) --state $state --forcing $forcing --summary $summary_path --monthly $monthly_path --next-state $nextstate --age $age --interval-kyr $(age==0 ? 0.0 : 1.0) --metrics $metric_path`
        if snapshot != ""; cmd=`$cmd --snapshot $snapshot`; end
        run(cmd)
        m=CSV.read(metric_path,DataFrame); m[!,:mode]=fill(mode,nrow(m)); append!(metrics,m;cols=:union); CSV.write(joinpath(outdir,"timeseries.csv"),metrics)
        if age>0
            mv(nextstate,state;force=true)
        end
        rm(forcing;force=true); rm(summary_path;force=true); rm(monthly_path;force=true); rm(metric_path;force=true); rm(nextstate;force=true)
        println("AGE_DONE mode=$mode age=$age meanH=$(metrics.mean_h_m[end]) meanNPP=$(metrics.mean_npp_gC_m2_yr[end])")
        flush(stdout)
    end
    cp(state,joinpath(outdir,"final_state.npz");force=true)
    println("RUN120_COMPLETE mode=$mode")
end
main()
