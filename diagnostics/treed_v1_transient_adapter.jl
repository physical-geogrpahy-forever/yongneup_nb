# Source-backed transient adapter for the Yongneup reduced TREEDCore.
#
# The canonical Yongneup production payload intentionally contains a reduced
# TREED_core.jl and does not define `trait_evolution`.  This adapter restores only
# the TREED v1.0 trait-evolution rule needed by the non-steady coupling experiment.
# It does not modify the production core and does not introduce new ecological
# coefficients.
#
# Audited upstream source:
# julrogger/TREED commit 03ac7834178c40b3b9d90e0e2689a218d10bd545
# src/TREED_physiological_functions.jl, `trait_evolution`.

function treed_v1_trait_evolution(; optimized_traits, env, tr, par, evorate)
    0.0 <= evorate <= 1.0 || error("evorate must be in [0,1]")

    new_C_leaf = tr.C_leaf + evorate * (optimized_traits.C_leaf_optimized - tr.C_leaf)
    new_r_s_r = tr.r_s_r + evorate * (optimized_traits.r_s_r_optimized - tr.r_s_r)
    new_a_ll = tr.a_ll + evorate * (optimized_traits.a_ll_optimized - tr.a_ll)

    potential_seasonality = sum(env.tair_monthly .<= par.temp_threshold_growing_season) >= 3.0 ? 0.0 : 1.0
    new_seasonality = (new_a_ll < 1.0 && potential_seasonality == 0.0) ? 0.0 : 1.0

    new_Tave_optim = tr.Tave_optim + evorate * (env.tair_annual - tr.Tave_optim)
    new_Tmin_optim = tr.Tmin_optim + evorate * (minimum(env.tair_monthly) - tr.Tmin_optim)
    new_Tmax_optim = tr.Tmax_optim + evorate * (maximum(env.tair_monthly) - tr.Tmax_optim)
    new_Pave_optim = tr.Pave_optim + evorate * (env.precip_annual - tr.Pave_optim)

    return (
        H = NaN,
        a_ll = new_a_ll,
        C_leaf = new_C_leaf,
        seasonality = new_seasonality,
        r_s_r = new_r_s_r,
        Tave_optim = new_Tave_optim,
        Tmax_optim = new_Tmax_optim,
        Tmin_optim = new_Tmin_optim,
        Pave_optim = new_Pave_optim,
    )
end
