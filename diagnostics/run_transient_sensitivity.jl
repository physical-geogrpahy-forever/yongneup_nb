# Yongneup TREED transient 120 -> 119 ka one-step sensitivity.
#
# Scientific isolation:
# - same audited production payload / physiology / allometry / direct AGB
# - same 120 ka soil-water coupled initialization
# - same 120 -> 119 ka Pelletier geomorphic step
# - same optimizer protocol: iters=20, seed=240819+cell, JULIA_NUM_THREADS=1
# - vary only TREED transient evorate and ecological search radius
#
# evorate values are taken directly from the official TREED v1 PETM lag case
# study at upstream commit 03ac7834178c40b3b9d90e0e2689a218d10bd545:
# 0.01 slow, 0.1 intermediate, 0.75 fast, 1.0 immediate adaptation.
#
# Official absolute dispersal examples (200-700 km) are not copied to this
# ~0.53 km Yongneup active domain. Instead we test geometric search scales:
# self only, one local grid spacing, five grid spacings, and whole active domain.
# These are sensitivity scales, not calibrated dispersal estimates.

include(joinpath(@__DIR__, "run_transient_smoke.jl"))

const SENS_EVORATES = [0.01, 0.1, 0.75, 1.0]

function active_geometry(inp::DataFrame)
    meta=unique(inp[:,[:cell_id,:lon_deg,:lat_deg]])
    sort!(meta,:cell_id)
    n=nrow(meta)
    n > 1 || error("need at least two active cells for dispersal sensitivity")
    nn=fill(Inf,n)
    diameter=0.0
    for i in 1:n
        for j in 1:n
            i==j && continue
            d=haversine_km(Float64(meta.lon_deg[i]),Float64(meta.lat_deg[i]),Float64(meta.lon_deg[j]),Float64(meta.lat_deg[j]))
            nn[i]=min(nn[i],d)
            diameter=max(diameter,d)
        end
    end
    spacing=median(nn)
    all(isfinite,nn) || error("non-finite nearest-neighbor geometry")
    return (spacing_km=spacing,diameter_km=diameter,
        scales=[
            (label="self",radius_km=0.0),
            (label="1cell",radius_km=spacing*1.001),
            (label="5cell",radius_km=spacing*5.001),
            (label="domain",radius_km=diameter+1e-9),
        ])
end

function build_common_120_to_119()
    mkpath(OUTDIR)
    work=joinpath(OUTDIR,"work")
    mkpath(work)

    state120=joinpath(work,"state_120.npz")
    cp(joinpath(ROOT,"inputs","init_grid.npz"),state120;force=true)
    forcing120=joinpath(work,"forcing_120.csv")
    run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age 120 --state $state120 --out $forcing120`)
    inp120=CSV.read(forcing120,DataFrame)

    traits120,es120,jan120,evals120,rows120=initialize_120(inp120)
    s120,m120=summary_monthly(inp120,traits120,evals120,rows120;label="transient_init")
    CSV.write(joinpath(OUTDIR,"baseline_120_summary.csv"),s120)
    CSV.write(joinpath(OUTDIR,"baseline_120_monthly.csv"),m120)

    summary120=joinpath(work,"summary_120.csv")
    monthly120=joinpath(work,"monthly_120.csv")
    CSV.write(summary120,s120)
    CSV.write(monthly120,m120)

    state119=joinpath(work,"state_119.npz")
    metrics120=joinpath(OUTDIR,"baseline_120_geomorph_metrics.csv")
    run_geomorph(state120,forcing120,summary120,monthly120,state119,120.0,1.0,metrics120)

    forcing119=joinpath(work,"forcing_119.csv")
    run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age 119 --state $state119 --out $forcing119`)
    inp119=CSV.read(forcing119,DataFrame)
    CSV.write(joinpath(OUTDIR,"forcing_119.csv"),inp119)

    return inp120,inp119,traits120,es120,jan120
end

function sensitivity_main()
    inp120,inp119,traits120,es120,jan120=build_common_120_to_119()
    geom=active_geometry(inp119)
    println("SENS_GEOMETRY spacing_km=$(geom.spacing_km) diameter_km=$(geom.diameter_km)")

    matrix_rows=NamedTuple[]
    cell_rows=NamedTuple[]

    for evorate in SENS_EVORATES
        for scale in geom.scales
            radius=scale.radius_km
            tr=transient_fixed_point(inp119,traits120,es120,jan120;evorate=evorate,dispersal_km=radius)
            s,m=summary_monthly(inp119,tr.traits_end,tr.evals,tr.rows;label="transient_sensitivity")
            s[!,:iterations].=tr.iterations
            s[!,:convergence_error].=tr.error

            neighbor_counts=Dict(c=>length(v) for (c,v) in tr.neighbors)
            nc=collect(values(neighbor_counts))
            donor_a_nonself=0
            donor_c_nonself=0
            changed=0

            for r in eachrow(s)
                cell=Int(r.cell_id)
                start=traits120[cell]
                final=tr.traits_end[cell]
                opt=tr.optimized[cell]
                evo=tr.evolved[cell]
                da=choose_donor(cell,:a_ll,traits120,tr.evolved,tr.optimized,tr.neighbors)
                dc=choose_donor(cell,:C_leaf,traits120,tr.evolved,tr.optimized,tr.neighbors)
                donor_a_nonself += da != cell
                donor_c_nonself += dc != cell
                ischanged=(abs(final.H-start.H)>1e-12 || abs(final.a_ll-start.a_ll)>1e-12 || abs(final.C_leaf-start.C_leaf)>1e-9)
                changed += ischanged
                push!(cell_rows,(
                    evorate=evorate,dispersal_label=scale.label,dispersal_km=radius,
                    cell_id=cell,row=Int(r.row),col=Int(r.col),soil_depth_m=Float64(r.soil_depth_m),neighbor_count=neighbor_counts[cell],
                    H_120=start.H,H_optimized_119=opt.H,H_119=final.H,dH=final.H-start.H,
                    a_ll_120=start.a_ll,a_ll_optimized_119=opt.a_ll,a_ll_evolved_pre_ecology=evo.a_ll,a_ll_119=final.a_ll,da_ll=final.a_ll-start.a_ll,donor_a_ll=da,
                    C_leaf_120=start.C_leaf,C_leaf_optimized_119=opt.C_leaf,C_leaf_evolved_pre_ecology=evo.C_leaf,C_leaf_119=final.C_leaf,dC_leaf=final.C_leaf-start.C_leaf,donor_C_leaf=dc,
                    Tave_optim_120=start.Tave_optim,Tave_optim_119=final.Tave_optim,
                    woody_productive=Bool(r.woody_productive),r_s_r=Float64(r.r_s_r),LAI=Float64(r.LAI),FPC=Float64(r.FPC),
                    NPP_gC_m2_yr=Float64(r.NPP_gC_m2_yr),AET_mm_yr=Float64(r.AET_mm_yr),AGB_C_g_m2=Float64(r.AGB_C_g_m2_component_sum),
                    raw_NPP_gC_m2_yr=Float64(r.raw_NPP_gC_m2_yr)))
            end

            soilpos=(s.soil_depth_m .> 0)
            unprod_soilpos=sum(soilpos .& .!Bool.(s.woody_productive))
            maxbal=maximum(abs.(Float64.(m.balance_residual_mm)))
            all(Float64.(s.r_s_r) .== 1.0) || error("r_s_r drift in evorate=$evorate scale=$(scale.label)")
            all(isfinite,Float64.(s.NPP_gC_m2_yr)) || error("nonfinite NPP")
            all(isfinite,Float64.(s.AET_mm_yr)) || error("nonfinite AET")
            all(Float64.(s.AGB_C_g_m2_component_sum) .>= 0) || error("negative AGB")
            maxbal < 1e-9 || error("water-balance residual $maxbal")

            push!(matrix_rows,(
                evorate=evorate,dispersal_label=scale.label,dispersal_km=radius,
                neighbor_min=minimum(nc),neighbor_median=median(nc),neighbor_max=maximum(nc),
                fixedpoint_iterations=tr.iterations,fixedpoint_error=tr.error,max_monthly_water_balance_residual_mm=maxbal,
                changed_cells=changed,productive_cells=sum(Bool.(s.woody_productive)),unproductive_soilpositive_cells=unprod_soilpos,
                donor_a_ll_nonself_fraction=donor_a_nonself/nrow(s),donor_C_leaf_nonself_fraction=donor_c_nonself/nrow(s),
                mean_H_m=mean(Float64.(s.H_m)),mean_latent_H_m=mean(Float64.(s.latent_H_m)),mean_a_ll_yr=mean(Float64.(s.a_ll_yr)),
                mean_C_leaf_gC_individual=mean(Float64.(s.C_leaf_gC_individual)),mean_LAI=mean(Float64.(s.LAI)),mean_FPC=mean(Float64.(s.FPC)),
                mean_NPP_gC_m2_yr=mean(Float64.(s.NPP_gC_m2_yr)),mean_AET_mm_yr=mean(Float64.(s.AET_mm_yr)),mean_AGB_C_g_m2=mean(Float64.(s.AGB_C_g_m2_component_sum)),
                mean_abs_dH=mean([abs(tr.traits_end[c].H-traits120[c].H) for c in keys(traits120)]),
                mean_abs_da_ll=mean([abs(tr.traits_end[c].a_ll-traits120[c].a_ll) for c in keys(traits120)]),
                mean_abs_dC_leaf=mean([abs(tr.traits_end[c].C_leaf-traits120[c].C_leaf) for c in keys(traits120)])))

            println("SENS_OK evorate=$evorate scale=$(scale.label) radius_km=$radius iters=$(tr.iterations) prod=$(sum(Bool.(s.woody_productive))) donor_a_nonself=$(donor_a_nonself/nrow(s)) donor_c_nonself=$(donor_c_nonself/nrow(s))")
        end
    end

    matrix=DataFrame(matrix_rows)
    cells=DataFrame(cell_rows)
    CSV.write(joinpath(OUTDIR,"transient_sensitivity_matrix.csv"),matrix)
    CSV.write(joinpath(OUTDIR,"transient_sensitivity_cells.csv"),cells)

    nrow(matrix)==length(SENS_EVORATES)*length(geom.scales) || error("incomplete sensitivity matrix")
    nrow(cells)==nrow(matrix)*298 || error("incomplete cell sensitivity output")
    println("TREED_TRANSIENT_SENSITIVITY_OK combinations=$(nrow(matrix)) cell_rows=$(nrow(cells))")
end

sensitivity_main()
