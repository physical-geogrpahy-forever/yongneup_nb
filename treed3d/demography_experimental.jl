# Experimental demographic extension for TREED3D.
#
# This file assumes the audited production driver has already been included, so
# evaluate_traits, evaluate_dynamic, base_env, simulate_bucket, awc_total_mm and
# TREEDCore are available in Main.

mutable struct CohortState
    H::Float64
    a_ll::Float64
    C_leaf::Float64
    seasonality::Float64
    r_s_r::Float64
    Tave_optim::Float64
    Tmax_optim::Float64
    Tmin_optim::Float64
    Pave_optim::Float64
    density_ind_m2::Float64
    H_opt::Float64
    age_yr::Int
    cumulative_unallocated_C_g_ind::Float64
end

primary_from_cohort(c::CohortState; H::Float64=c.H) = (
    H=H,
    a_ll=c.a_ll,
    C_leaf=c.C_leaf,
    seasonality=c.seasonality,
    r_s_r=c.r_s_r,
    Tave_optim=c.Tave_optim,
    Tmax_optim=c.Tmax_optim,
    Tmin_optim=c.Tmin_optim,
    Pave_optim=c.Pave_optim,
)

function individual_standing_C(tr)
    tr.C_leaf + tr.C_fineroot + tr.C_sapwood + tr.C_heartwood + tr.C_coarseroot
end

function cohort_occupied_fraction(c::CohortState, tr)
    clamp(c.density_ind_m2 * tr.CA, 0.0, 1.0)
end

function cohort_FPC(c::CohortState, tr)
    clamp(cohort_occupied_fraction(c,tr) * tr.FPC, 0.0, 1.0)
end

function cohort_AGB_C_g_m2(c::CohortState, tr)
    c.density_ind_m2 * (tr.C_leaf + tr.C_sapwood + tr.C_heartwood)
end

function cohort_BGB_C_g_m2(c::CohortState, tr)
    c.density_ind_m2 * (tr.C_fineroot + tr.C_coarseroot)
end

# Exact fixed-trait soil-water coupling, analogous to production coupled_cell,
# except that no optimizer is called because this is one explicit cohort state.
function coupled_cohort_cell(df::DataFrame, c::CohortState;
    es_init=nothing, jan_init=nothing, tol=1e-4, maxiter=100)

    cap=awc_total_mm(Float64(df.soil_depth_m[1]))
    precip=Float64.(df.precip_mm_month)
    days=Float64.(df.days)
    jan=jan_init===nothing ? cap : clamp(Float64(jan_init),0.0,cap)
    es=es_init===nothing ? min.(EMAX,Float64.(df.precip_mean_mm_day)) : clamp.(Float64.(es_init),0.0,EMAX)
    final=nothing; finalrows=nothing; err=Inf

    for k in 1:maxiter
        env=base_env(df;esupply=es)
        ev=evaluate_traits(env,primary_from_cohort(c))
        # No selective optimizer-pathology filter is applied here: the cohort is
        # not an optimizer solution. Its positive/negative carbon balance is an
        # actual demographic diagnostic for this explicit state.
        rows,jan_new=simulate_bucket(cap,jan,precip,days,Float64.(ev.gpp.AET_monthly_mm))
        es_new=[r.esupply_mm_day for r in rows]
        err=max(maximum(abs.(es_new .- es)),abs(jan_new-jan))
        final=ev; finalrows=rows; es=es_new; jan=jan_new
        if err<tol
            env2=base_env(df;esupply=es)
            final=evaluate_traits(env2,primary_from_cohort(c))
            finalrows,jan_final=simulate_bucket(cap,jan,precip,days,Float64.(final.gpp.AET_monthly_mm))
            return final,finalrows,(converged=true,iterations=k,error=err,capacity=cap,jan=jan_final,es=[r.esupply_mm_day for r in finalrows])
        end
    end
    return final,finalrows,(converged=false,iterations=maxiter,error=err,capacity=cap,jan=jan,es=es)
end

function solve_height_for_individual_C(c::CohortState, target_C::Float64;
    atol_C::Float64=1e-8, maxiter::Int=100)

    lo=c.H
    hi=c.H_opt
    lo >= hi && return hi

    tr_lo=TREEDCore.plant_allometry(tr=primary_from_cohort(c;H=lo),par=TREEDCore.pars)
    tr_hi=TREEDCore.plant_allometry(tr=primary_from_cohort(c;H=hi),par=TREEDCore.pars)
    C_lo=individual_standing_C(tr_lo)
    C_hi=individual_standing_C(tr_hi)
    target_C <= C_lo && return lo
    target_C >= C_hi && return hi

    # Individual standing carbon is monotonic in H for a fixed leaf strategy
    # under the TREED allometry used here. The CI regression verifies this for
    # the tested trajectory rather than assuming it silently.
    for _ in 1:maxiter
        mid=(lo+hi)/2
        tr_mid=TREEDCore.plant_allometry(tr=primary_from_cohort(c;H=mid),par=TREEDCore.pars)
        C_mid=individual_standing_C(tr_mid)
        abs(C_mid-target_C) <= atol_C && return mid
        if C_mid < target_C
            lo=mid
        else
            hi=mid
        end
    end
    (lo+hi)/2
end

function initialize_cohort_from_optimum(opt_ev; initial_H::Float64=0.5)
    tr=opt_ev.tr
    primary=opt_ev.primary
    density=1.0/tr.CA
    CohortState(
        initial_H,
        tr.a_ll,
        tr.C_leaf,
        tr.seasonality,
        tr.r_s_r,
        primary.Tave_optim,
        primary.Tmax_optim,
        primary.Tmin_optim,
        primary.Pave_optim,
        density,
        tr.H,
        0,
        0.0,
    )
end

function step_cohort_year!(c::CohortState, df::DataFrame; es_init=nothing, jan_init=nothing)
    ev,rows,conv=coupled_cohort_cell(df,c;es_init=es_init,jan_init=jan_init)
    conv.converged || error("Cohort soil-water fixed point failed")

    tr0=ev.tr
    C0=individual_standing_C(tr0)
    NCG_local=Float64(ev.net) # TREED area-normalized NCG under this crown
    dC_ind=max(NCG_local,0.0)*tr0.CA
    requested_C=C0+dC_ind

    H1=solve_height_for_individual_C(c,requested_C)
    tr1=TREEDCore.plant_allometry(tr=primary_from_cohort(c;H=H1),par=TREEDCore.pars)
    C1=individual_standing_C(tr1)
    used_C=max(0.0,C1-C0)
    unallocated=max(0.0,dC_ind-used_C)

    c.H=H1
    c.age_yr+=1
    c.cumulative_unallocated_C_g_ind += unallocated

    cover0=cohort_occupied_fraction(c,tr0)
    # Re-evaluate cover using updated H while retaining the actual year's fluxes
    # from the pre-growth state. This follows an annual end-of-year allocation.
    cover1=cohort_occupied_fraction(c,tr1)

    return (
        year=c.age_yr,
        H_start=tr0.H,
        H_end=tr1.H,
        H_opt=c.H_opt,
        CA_start=tr0.CA,
        CA_end=tr1.CA,
        density_ind_m2=c.density_ind_m2,
        occupied_fraction_start=cover0,
        occupied_fraction_end=cover1,
        FPC_start=cohort_FPC(c,tr0),
        FPC_end=cohort_FPC(c,tr1),
        NPP_local_gC_m2_yr=Float64(ev.npp),
        NCG_local_gC_m2_yr=NCG_local,
        NPP_cell_gC_m2_yr=Float64(ev.npp)*cover0,
        NCG_cell_gC_m2_yr=NCG_local*cover0,
        individual_C_start_g=C0,
        requested_growth_C_g_ind=dC_ind,
        individual_C_end_g=C1,
        used_growth_C_g_ind=used_C,
        unallocated_C_g_ind=unallocated,
        carbon_balance_residual_g_ind=(C1-C0)+unallocated-dC_ind,
        AGB_C_start_g_m2=cohort_AGB_C_g_m2(c,tr0),
        AGB_C_end_g_m2=cohort_AGB_C_g_m2(c,tr1),
        BGB_C_start_g_m2=cohort_BGB_C_g_m2(c,tr0),
        BGB_C_end_g_m2=cohort_BGB_C_g_m2(c,tr1),
        AET_local_mm_yr=Float64(ev.gpp.AET),
        water_iterations=conv.iterations,
        water_error=conv.error,
        es=Float64.(conv.es),
        jan=Float64(conv.jan),
    )
end
