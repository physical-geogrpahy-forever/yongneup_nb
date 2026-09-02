using CSV
using DataFrames
using Statistics

include(joinpath(@__DIR__, "..", "treed120", "julia", "run_120ka.jl"))
include(joinpath(@__DIR__, "demography_experimental.jl"))

function main()
    length(ARGS) >= 2 || error("usage: julia run_one_cell_growth.jl <forcing.csv> <out.csv> [cell_id] [years]")
    forcing_path=ARGS[1]
    out_path=ARGS[2]
    cell_id=length(ARGS)>=3 ? parse(Int,ARGS[3]) : 1
    maxyears=length(ARGS)>=4 ? parse(Int,ARGS[4]) : 500

    inp=CSV.read(forcing_path,DataFrame)
    g=filter(:cell_id => ==(cell_id), inp)
    nrow(g)==12 || error("expected 12 forcing rows for cell $cell_id, got $(nrow(g))")
    sort!(g,:month)

    opt_ev,opt_rows,opt_conv=coupled_cell(g;mode="dynamic",seed=240819+cell_id)
    opt_conv.converged || error("target coupled TREED optimum did not converge")
    dynamic_optimizer_pathological("dynamic",opt_ev) && error("chosen target cell is an optimizer pathology")
    opt_ev.npp > 0 || error("chosen target cell has non-positive NPP")

    c=initialize_cohort_from_optimum(opt_ev;initial_H=0.5)
    es=nothing
    jan=nothing
    records=NamedTuple[]

    for _ in 1:maxyears
        r=step_cohort_year!(c,g;es_init=es,jan_init=jan)
        es=r.es
        jan=r.jan
        # Store the scalar diagnostics only; monthly water state remains internal.
        push!(records,(
            year=r.year,
            H_start_m=r.H_start,
            H_end_m=r.H_end,
            H_opt_m=r.H_opt,
            CA_start_m2=r.CA_start,
            CA_end_m2=r.CA_end,
            density_ind_m2=r.density_ind_m2,
            occupied_fraction_start=r.occupied_fraction_start,
            occupied_fraction_end=r.occupied_fraction_end,
            FPC_start=r.FPC_start,
            FPC_end=r.FPC_end,
            NPP_local_gC_m2_yr=r.NPP_local_gC_m2_yr,
            NCG_local_gC_m2_yr=r.NCG_local_gC_m2_yr,
            NPP_cell_gC_m2_yr=r.NPP_cell_gC_m2_yr,
            NCG_cell_gC_m2_yr=r.NCG_cell_gC_m2_yr,
            individual_C_start_g=r.individual_C_start_g,
            requested_growth_C_g_ind=r.requested_growth_C_g_ind,
            individual_C_end_g=r.individual_C_end_g,
            used_growth_C_g_ind=r.used_growth_C_g_ind,
            unallocated_C_g_ind=r.unallocated_C_g_ind,
            carbon_balance_residual_g_ind=r.carbon_balance_residual_g_ind,
            AGB_C_start_g_m2=r.AGB_C_start_g_m2,
            AGB_C_end_g_m2=r.AGB_C_end_g_m2,
            BGB_C_start_g_m2=r.BGB_C_start_g_m2,
            BGB_C_end_g_m2=r.BGB_C_end_g_m2,
            AET_local_mm_yr=r.AET_local_mm_yr,
            water_iterations=r.water_iterations,
            water_error=r.water_error,
        ))
        c.H >= c.H_opt-1e-9 && break
        # If the explicit cohort cannot grow under the target environment, stop and
        # report the stall rather than inventing a growth rate.
        r.NCG_local_gC_m2_yr <= 0 && break
    end

    out=DataFrame(records)
    mkpath(dirname(out_path))
    CSV.write(out_path,out)

    tr_opt=opt_ev.tr
    target_agb=Float64(opt_ev.agb)
    target_bgb=Float64(opt_ev.bgb)
    last=out[end,:]
    reached=last.H_end_m >= c.H_opt-1e-8

    summary=DataFrame([(
        cell_id=cell_id,
        years_simulated=nrow(out),
        reached_optimum=reached,
        initial_H_m=out.H_start_m[1],
        final_H_m=last.H_end_m,
        target_H_m=c.H_opt,
        target_CA_m2=tr_opt.CA,
        target_density_ind_m2=c.density_ind_m2,
        final_occupied_fraction=last.occupied_fraction_end,
        final_FPC=last.FPC_end,
        target_TREED_FPC=tr_opt.FPC,
        final_AGB_C_g_m2=last.AGB_C_end_g_m2,
        target_TREED_AGB_C_g_m2=target_agb,
        final_BGB_C_g_m2=last.BGB_C_end_g_m2,
        target_TREED_BGB_C_g_m2=target_bgb,
        max_abs_carbon_residual_g_ind=maximum(abs.(out.carbon_balance_residual_g_ind)),
        cumulative_unallocated_C_g_ind=c.cumulative_unallocated_C_g_ind,
    )])
    summary_path=replace(out_path,r"\.csv$"=>"_summary.csv")
    CSV.write(summary_path,summary)

    println("ONE_CELL_GROWTH_COMPLETE cell=$cell_id years=$(nrow(out)) reached=$reached H0=$(out.H_start_m[1]) H1=$(last.H_end_m) Hopt=$(c.H_opt) maxCres=$(summary.max_abs_carbon_residual_g_ind[1])")
end

main()
