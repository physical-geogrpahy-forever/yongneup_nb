using CSV
using DataFrames
using Random
using Statistics

length(ARGS) >= 4 || error("usage: julia run_transient_smoke.jl <model-root> <evorate> <dispersal-km> <outdir>")
const ROOT = normpath(ARGS[1])
const EVORATE = parse(Float64, ARGS[2])
const DISPERSAL_KM = parse(Float64, ARGS[3])
const OUTDIR = normpath(ARGS[4])
include(joinpath(ROOT,"src","TREED_core.jl"))
using .TREEDCore

isdefined(TREEDCore,:trait_evolution) || error("production TREEDCore does not expose trait_evolution")
0.0 <= EVORATE <= 1.0 || error("evorate must be in [0,1]")
DISPERSAL_KM >= 0.0 || error("dispersal_km must be >=0")

const EMAX=5.0
const AWC_PROFILE=[(0.00,0.05,237.0),(0.05,0.15,232.0),(0.15,0.30,218.0),(0.30,0.60,207.0),(0.60,1.00,198.0),(1.00,2.00,179.0)]
const DOIS=[15,46,73,104,134,166,196,227,259,288,319,349]
const H_OPT_LOWER_BOUND=1.0
const H_OPT_BOUND_TOL=1e-3
const R_EARTH_KM=6371.0088

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

primary(tr; H=tr.H)=(H=H,a_ll=tr.a_ll,C_leaf=tr.C_leaf,seasonality=tr.seasonality,r_s_r=tr.r_s_r,
    Tave_optim=tr.Tave_optim,Tmax_optim=tr.Tmax_optim,Tmin_optim=tr.Tmin_optim,Pave_optim=tr.Pave_optim)

function evaluate_traits(env,tr_primary)
    tr=primary(tr_primary)
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

function optimize_primary(env; seed=240819,iters=20)
    Random.seed!(seed)
    opt=TREEDCore.trait_optimizer(env=env,par=TREEDCore.pars,trait_optimization_function=TREEDCore.trait_optimization_function,iters=iters)
    return (H=opt.H_optimized,a_ll=opt.a_ll_optimized,C_leaf=opt.C_leaf_optimized,seasonality=opt.seasonality_optimized,r_s_r=opt.r_s_r_optimized,
        Tave_optim=mean(env.tair_monthly),Tmax_optim=maximum(env.tair_monthly),Tmin_optim=minimum(env.tair_monthly),Pave_optim=mean(env.precip_monthly))
end

function evolve_primary(start,optimum,env,evorate)
    optimized_traits=(a_ll_optimized=optimum.a_ll,C_leaf_optimized=optimum.C_leaf,r_s_r_optimized=optimum.r_s_r,H_optimized=optimum.H,seasonality_optimized=optimum.seasonality)
    e=TREEDCore.trait_evolution(optimized_traits=optimized_traits,env=env,tr=start,par=TREEDCore.pars,evorate=evorate)
    return primary(e;H=NaN)
end

raw_unproductive(ev)=!isfinite(ev.npp) || ev.npp<=0.0
optimizer_pathological(ev)=raw_unproductive(ev) && isfinite(ev.tr.H) && ev.tr.H <= H_OPT_LOWER_BOUND+H_OPT_BOUND_TOL

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

function coupled_steady_cell(df; es_init=nothing,jan_init=nothing,tol=1e-4,maxiter=100,seed=240819)
    cap=awc_total_mm(Float64(df.soil_depth_m[1])); precip=Float64.(df.precip_mm_month); days=Float64.(df.days)
    jan=jan_init===nothing ? cap : clamp(Float64(jan_init),0.0,cap)
    es=es_init===nothing ? min.(EMAX,Float64.(df.precip_mean_mm_day)) : clamp.(Float64.(es_init),0.0,EMAX)
    final=nothing; finalrows=nothing; err=Inf
    for k in 1:maxiter
        env=base_env(df;esupply=es); p=optimize_primary(env;seed=seed,iters=20); ev=evaluate_traits(env,p)
        aet_req=optimizer_pathological(ev) || cap<=0 ? zeros(Float64,12) : Float64.(ev.gpp.AET_monthly_mm)
        rows,jan_new=simulate_bucket(cap,jan,precip,days,aet_req); es_new=[r.esupply_mm_day for r in rows]
        err=max(maximum(abs.(es_new.-es)),abs(jan_new-jan)); final=ev; finalrows=rows; es=es_new; jan=jan_new
        if err<tol
            env2=base_env(df;esupply=es); p2=optimize_primary(env2;seed=seed,iters=20); final=evaluate_traits(env2,p2)
            aet_req2=optimizer_pathological(final) || cap<=0 ? zeros(Float64,12) : Float64.(final.gpp.AET_monthly_mm)
            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,aet_req2)
            return final,finalrows,(converged=true,iterations=k,error=err,capacity=cap,jan=jan_final,es=[r.esupply_mm_day for r in finalrows])
        end
    end
    return final,finalrows,(converged=false,iterations=maxiter,error=err,capacity=cap,jan=jan,es=es)
end

function haversine_km(lon1,lat1,lon2,lat2)
    p1=deg2rad(lat1); p2=deg2rad(lat2); dp=deg2rad(lat2-lat1); dl=deg2rad(lon2-lon1)
    a=sin(dp/2)^2+cos(p1)*cos(p2)*sin(dl/2)^2
    2R_EARTH_KM*asin(min(1.0,sqrt(a)))
end

function build_neighbors(inp,radius_km)
    meta=unique(inp[:,[:cell_id,:lon_deg,:lat_deg]]); sort!(meta,:cell_id)
    ids=Int.(meta.cell_id); out=Dict{Int,Vector{Int}}()
    for i in 1:nrow(meta)
        c=ids[i]; v=Int[]
        for j in 1:nrow(meta)
            d=haversine_km(meta.lon_deg[i],meta.lat_deg[i],meta.lon_deg[j],meta.lat_deg[j])
            d <= radius_km+1e-12 && push!(v,ids[j])
        end
        c in v || push!(v,c); out[c]=v
    end
    out
end

function choose_donor(cell,component,traits_start,traits_evolved,traits_optimized,neighbors)
    cand=[c for c in neighbors[cell] if traits_start[c].H>0]
    cell in cand || push!(cand,cell)
    target=getproperty(traits_optimized[cell],component)
    vals=[getproperty(traits_evolved[c],component) for c in cand]
    return cand[argmin(abs.(vals .- target))]
end

function height_viability(env,tr_without_H)
    find_H_new=function(h)
        tr=primary(tr_without_H;H=h)
        trc=TREEDCore.plant_allometry(tr=tr,par=TREEDCore.pars)
        g=TREEDCore.GPP_function_for_optimization(env=env,tr=trc,par=TREEDCore.pars)
        rm=TREEDCore.R_maintenance_function(env=env,tr=trc,par=TREEDCore.pars,GPP_out=g)
        n=TREEDCore.calc_NPP(GPP_out=g,R_maintenance=rm,par=TREEDCore.pars)
        turn=TREEDCore.C_turnover_function(env=env,tr=trc,par=TREEDCore.pars)
        net=TREEDCore.calc_net_C_gain(NPP=n,C_turnover_total=turn,par=TREEDCore.pars)
        net <= -80 ? 0 : 1
    end
    hs=collect(0.0:0.25:50.0); e=find_H_new.(hs)
    sum(e)==0 && return 0.0
    idx=findlast(Int8.([1,0]),Int8.(e))
    idx===nothing && return 50.0
    return hs[idx[1]]
end

function projected_ecology(traits_start,traits_evolved,traits_optimized,envs,neighbors)
    out=Dict{Int,Any}()
    for cell in sort(collect(keys(traits_start)))
        da=choose_donor(cell,:a_ll,traits_start,traits_evolved,traits_optimized,neighbors)
        dc=choose_donor(cell,:C_leaf,traits_start,traits_evolved,traits_optimized,neighbors)
        dtave=choose_donor(cell,:Tave_optim,traits_start,traits_evolved,traits_optimized,neighbors)
        dtmin=choose_donor(cell,:Tmin_optim,traits_start,traits_evolved,traits_optimized,neighbors)
        dtmax=choose_donor(cell,:Tmax_optim,traits_start,traits_evolved,traits_optimized,neighbors)
        dp=choose_donor(cell,:Pave_optim,traits_start,traits_evolved,traits_optimized,neighbors)
        a_ll=traits_evolved[da].a_ll
        seasonality=(a_ll<=1.0 && traits_evolved[da].seasonality<1.0) ? 0.0 : 1.0
        tr=(H=NaN,a_ll=a_ll,C_leaf=traits_evolved[dc].C_leaf,seasonality=seasonality,r_s_r=traits_evolved[cell].r_s_r,
            Tave_optim=traits_evolved[dtave].Tave_optim,Tmax_optim=traits_evolved[dtmax].Tmax_optim,Tmin_optim=traits_evolved[dtmin].Tmin_optim,Pave_optim=traits_evolved[dp].Pave_optim)
        H=height_viability(envs[cell],tr)
        out[cell]=primary(tr;H=H)
    end
    out
end

function cell_tables(inp)
    d=Dict{Int,DataFrame}()
    for g in groupby(inp,:cell_id)
        df=DataFrame(g); sort!(df,:month); d[Int(df.cell_id[1])]=df
    end
    d
end

function evaluate_transient_given_supply(inp,tables,traits_start,es,evorate,neighbors)
    envs=Dict{Int,Any}(); opt=Dict{Int,Any}(); evolved=Dict{Int,Any}()
    for cell in sort(collect(keys(tables)))
        env=base_env(tables[cell];esupply=es[cell]); envs[cell]=env
        p=optimize_primary(env;seed=240819+cell,iters=20); opt[cell]=p
        evolved[cell]=evolve_primary(traits_start[cell],p,env,evorate)
    end
    tend=projected_ecology(traits_start,evolved,opt,envs,neighbors)
    return envs,opt,evolved,tend
end

function transient_fixed_point(inp,traits_start,prev_es,prev_jan;evorate,dispersal_km,tol=1e-4,maxiter=100)
    tables=cell_tables(inp); neighbors=build_neighbors(inp,dispersal_km)
    es=Dict{Int,Vector{Float64}}(); jan=Dict{Int,Float64}()
    for (cell,df) in tables
        cap=awc_total_mm(Float64(df.soil_depth_m[1]))
        es[cell]=haskey(prev_es,cell) ? clamp.(Float64.(prev_es[cell]),0.0,EMAX) : min.(EMAX,Float64.(df.precip_mean_mm_day))
        jan[cell]=haskey(prev_jan,cell) ? clamp(Float64(prev_jan[cell]),0.0,cap) : cap
    end
    err=Inf
    for k in 1:maxiter
        envs,opt,evolved,tend=evaluate_transient_given_supply(inp,tables,traits_start,es,evorate,neighbors)
        es_new=Dict{Int,Vector{Float64}}(); jan_new=Dict{Int,Float64}(); rows_all=Dict{Int,Any}(); evals=Dict{Int,Any}(); err=0.0
        for cell in sort(collect(keys(tables)))
            df=tables[cell]; cap=awc_total_mm(Float64(df.soil_depth_m[1])); precip=Float64.(df.precip_mm_month); days=Float64.(df.days)
            ev=nothing; aet_req=zeros(Float64,12)
            if cap>0 && tend[cell].H>0
                ev=evaluate_traits(envs[cell],tend[cell]); (isfinite(ev.npp) && ev.npp>0) && (aet_req=Float64.(ev.gpp.AET_monthly_mm))
            end
            rows,jnew=simulate_bucket(cap,jan[cell],precip,days,aet_req); enew=[r.esupply_mm_day for r in rows]
            err=max(err,maximum(abs.(enew.-es[cell])),abs(jnew-jan[cell]))
            es_new[cell]=enew; jan_new[cell]=jnew; rows_all[cell]=rows; evals[cell]=ev
        end
        es=es_new; jan=jan_new
        if err<tol
            envs,opt,evolved,tend=evaluate_transient_given_supply(inp,tables,traits_start,es,evorate,neighbors)
            rows_all=Dict{Int,Any}(); evals=Dict{Int,Any}(); es_final=Dict{Int,Vector{Float64}}(); jan_final=Dict{Int,Float64}()
            for cell in sort(collect(keys(tables)))
                df=tables[cell]; cap=awc_total_mm(Float64(df.soil_depth_m[1])); precip=Float64.(df.precip_mm_month); days=Float64.(df.days)
                ev=nothing; aet_req=zeros(Float64,12)
                if cap>0 && tend[cell].H>0
                    ev=evaluate_traits(envs[cell],tend[cell]); (isfinite(ev.npp) && ev.npp>0) && (aet_req=Float64.(ev.gpp.AET_monthly_mm))
                end
                rows,jnew=simulate_bucket(cap,jan[cell],precip,days,aet_req); enew=[r.esupply_mm_day for r in rows]
                rows_all[cell]=rows; evals[cell]=ev; es_final[cell]=enew; jan_final[cell]=jnew
            end
            return (converged=true,iterations=k,error=err,traits_end=tend,optimized=opt,evolved=evolved,envs=envs,evals=evals,rows=rows_all,es=es_final,jan=jan_final,neighbors=neighbors)
        end
    end
    error("transient soil-water fixed point failed err=$err")
end

function summary_monthly(inp,traits_state,evals,rows_all; label="transient")
    tables=cell_tables(inp); s=NamedTuple[]; monthly=DataFrame()
    for cell in sort(collect(keys(tables)))
        df=tables[cell]; trp=traits_state[cell]; ev=evals[cell]
        productive=ev!==nothing && isfinite(ev.npp) && ev.npp>0 && trp.H>0 && Float64(df.soil_depth_m[1])>0
        if productive
            tr=ev.tr; raw=ev.npp
            vals=(H=tr.H,a_ll=tr.a_ll,C_leaf=tr.C_leaf,seasonality=tr.seasonality,r_s_r=tr.r_s_r,LAI=tr.LAI,FPC=tr.FPC,GPP=ev.gpp.GPP,NPP=ev.npp,AET=ev.gpp.AET,Net=ev.net,AGB=ev.agb,BGB=ev.bgb)
        else
            raw=ev===nothing ? 0.0 : ev.npp
            vals=(H=0.0,a_ll=0.0,C_leaf=0.0,seasonality=trp.seasonality,r_s_r=trp.r_s_r,LAI=0.0,FPC=0.0,GPP=0.0,NPP=0.0,AET=0.0,Net=0.0,AGB=0.0,BGB=0.0)
        end
        push!(s,(cell_id=cell,row=Int(df.row[1]),col=Int(df.col[1]),soil_depth_m=Float64(df.soil_depth_m[1]),awc_capacity_mm=awc_total_mm(Float64(df.soil_depth_m[1])),
            converged=true,iterations=0,convergence_error=0.0,optimizer_pathological=false,inherited_initial_pathology=false,maladapted_frozen=false,woody_productive=productive,
            latent_H_m=trp.H,latent_a_ll_yr=trp.a_ll,latent_C_leaf_gC_individual=trp.C_leaf,raw_NPP_gC_m2_yr=raw,
            H_m=vals.H,a_ll_yr=vals.a_ll,C_leaf_gC_individual=vals.C_leaf,seasonality=vals.seasonality,r_s_r=vals.r_s_r,LAI=vals.LAI,FPC=vals.FPC,
            GPP_gC_m2_yr=vals.GPP,NPP_gC_m2_yr=vals.NPP,AET_mm_yr=vals.AET,Net_C_gain_gC_m2_yr=vals.Net,AGB_C_g_m2_component_sum=vals.AGB,BGB_C_g_m2_component_sum=vals.BGB,mode=label))
        md=DataFrame(rows_all[cell]); md[!,:cell_id]=fill(cell,nrow(md)); md[!,:row]=fill(Int(df.row[1]),nrow(md)); md[!,:col]=fill(Int(df.col[1]),nrow(md)); append!(monthly,md;cols=:union)
    end
    DataFrame(s),monthly
end

function initialize_120(inp)
    traits=Dict{Int,Any}(); es=Dict{Int,Vector{Float64}}(); jan=Dict{Int,Float64}(); evals=Dict{Int,Any}(); rows=Dict{Int,Any}()
    for g in groupby(inp,:cell_id)
        df=DataFrame(g); sort!(df,:month); cell=Int(df.cell_id[1]); ev,r,conv=coupled_steady_cell(df;seed=240819+cell)
        conv.converged || error("120 ka steady initialization failed cell=$cell")
        p=primary(ev.primary)
        if optimizer_pathological(ev) || Float64(df.soil_depth_m[1])<=0
            p=primary(p;H=0.0)
        end
        traits[cell]=p; es[cell]=Float64.(conv.es); jan[cell]=Float64(conv.jan); evals[cell]=ev; rows[cell]=r
    end
    traits,es,jan,evals,rows
end

function run_geomorph(state,forcing,summary,monthly,nextstate,age,interval,metrics;snapshot="")
    cmd=`python $(joinpath(ROOT,"python","run_geomorph_step.py")) --state $state --forcing $forcing --summary $summary --monthly $monthly --next-state $nextstate --age $age --interval-kyr $interval --metrics $metrics`
    snapshot!="" && (cmd=`$cmd --snapshot $snapshot`)
    run(cmd)
end

function main()
    mkpath(OUTDIR); work=joinpath(OUTDIR,"work"); mkpath(work)
    state120=joinpath(work,"state_120.npz"); cp(joinpath(ROOT,"inputs","init_grid.npz"),state120;force=true)
    forcing120=joinpath(work,"forcing_120.csv"); run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age 120 --state $state120 --out $forcing120`)
    inp120=CSV.read(forcing120,DataFrame)
    traits120,es120,jan120,evals120,rows120=initialize_120(inp120)
    s120,m120=summary_monthly(inp120,traits120,evals120,rows120;label="transient_init")
    summary120=joinpath(work,"summary_120.csv"); monthly120=joinpath(work,"monthly_120.csv"); CSV.write(summary120,s120); CSV.write(monthly120,m120)
    state119=joinpath(work,"state_119.npz"); metrics120=joinpath(OUTDIR,"metrics_120.csv")
    run_geomorph(state120,forcing120,summary120,monthly120,state119,120.0,1.0,metrics120)

    forcing119=joinpath(work,"forcing_119.csv"); run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age 119 --state $state119 --out $forcing119`)
    inp119=CSV.read(forcing119,DataFrame)
    tr=transient_fixed_point(inp119,traits120,es120,jan120;evorate=EVORATE,dispersal_km=DISPERSAL_KM)
    s119,m119=summary_monthly(inp119,tr.traits_end,tr.evals,tr.rows;label="transient")
    s119[!,:iterations].=tr.iterations; s119[!,:convergence_error].=tr.error
    summary119=joinpath(OUTDIR,"summary_119.csv"); monthly119=joinpath(OUTDIR,"monthly_119.csv"); CSV.write(summary119,s119); CSV.write(monthly119,m119)
    state119same=joinpath(work,"state_119_same.npz"); metrics119=joinpath(OUTDIR,"metrics_119.csv"); snap119=joinpath(OUTDIR,"snapshot_119ka.csv")
    run_geomorph(state119,forcing119,summary119,monthly119,state119same,119.0,0.0,metrics119;snapshot=snap119)

    rows=NamedTuple[]
    for cell in sort(collect(keys(traits120)))
        a=traits120[cell]; b=tr.traits_end[cell]
        push!(rows,(cell_id=cell,H_120=a.H,H_119=b.H,dH=b.H-a.H,a_ll_120=a.a_ll,a_ll_119=b.a_ll,da_ll=b.a_ll-a.a_ll,
            C_leaf_120=a.C_leaf,C_leaf_119=b.C_leaf,dC_leaf=b.C_leaf-a.C_leaf,Tave_optim_120=a.Tave_optim,Tave_optim_119=b.Tave_optim))
    end
    trans=DataFrame(rows); CSV.write(joinpath(OUTDIR,"trait_transition_120_to_119.csv"),trans)
    neighbor_counts=[length(v) for v in values(tr.neighbors)]
    println("TRANSIENT_SMOKE_OK evorate=$EVORATE dispersal_km=$DISPERSAL_KM fixedpoint_iters=$(tr.iterations) err=$(tr.error)")
    println("neighbor_count_min=$(minimum(neighbor_counts)) median=$(median(neighbor_counts)) max=$(maximum(neighbor_counts))")
    println("mean_H_120=$(mean(trans.H_120)) mean_H_119=$(mean(trans.H_119)) mean_abs_da_ll=$(mean(abs.(trans.da_ll))) mean_abs_dC_leaf=$(mean(abs.(trans.dC_leaf)))")
end

main()
