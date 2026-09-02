from pathlib import Path

src = Path('treed120/julia/run_120ka.jl')
out = Path('treed120/julia/run_original_dynamic_10y.jl')
s = src.read_text(encoding='utf-8')

marker = 'function main()'
assert s.count(marker) == 1, 'unexpected production main() count'
prefix = s.split(marker, 1)[0]

# Keep every production function byte-for-byte above main().  Only the orchestration
# is replaced so the already-audited Dynamic model can be advanced for ten 1-year
# intervals from its archived 0 ka final state.
main = r'''
function original_dynamic_10y_main()
    mode = "dynamic"
    years = 10
    climate_age = 0
    interval_kyr = 0.001  # exactly one year

    length(ARGS) >= 2 || error("usage: julia run_original_dynamic_10y.jl <baseline-final-state.npz> <outdir>")
    baseline_state = abspath(ARGS[1])
    outdir = abspath(ARGS[2])
    isfile(baseline_state) || error("missing baseline final state: $baseline_state")

    work = joinpath(outdir, "work")
    snapdir = joinpath(outdir, "snapshots")
    mkpath(work); mkpath(snapdir)

    state = joinpath(work, "state_current.npz")
    cp(baseline_state, state; force=true)

    fixed_traits = Dict{Int,Any}()
    prev_es = Dict{Int,Vector{Float64}}()
    prev_jan = Dict{Int,Float64}()
    metrics = DataFrame()

    # The original pre-selective Direct-AGB v2 write_age_outputs has seven
    # positional arguments.  A later diagnostic source variant has an eighth
    # pathology-set argument.  This 10-y runner accepts either without changing
    # the model equations; the production payload used here should take the
    # seven-argument path.
    nargs_set = Set(m.nargs for m in methods(write_age_outputs))

    for year in 1:years
        forcing = joinpath(work, "forcing_year_$(lpad(year,3,'0')).csv")
        run(`python $(joinpath(ROOT,"python","prepare_age_input.py")) --age $climate_age --state $state --out $forcing`)
        inp = CSV.read(forcing, DataFrame)

        summary_path = joinpath(work, "summary_year_$(lpad(year,3,'0')).csv")
        monthly_path = joinpath(work, "monthly_year_$(lpad(year,3,'0')).csv")

        if 8 in nargs_set
            prev_es,prev_jan,summary = write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path)
        elseif 9 in nargs_set
            prev_es,prev_jan,summary = write_age_outputs(inp,mode,fixed_traits,prev_es,prev_jan,summary_path,monthly_path,Set{Int}())
        else
            error("unexpected write_age_outputs method arities: $(collect(nargs_set))")
        end

        nextstate = joinpath(work, "state_next.npz")
        metric_path = joinpath(work, "metric_year_$(lpad(year,3,'0')).csv")
        snapshot = joinpath(snapdir, "year_$(lpad(year,3,'0')).csv")
        cmd = `python $(joinpath(ROOT,"python","run_geomorph_step.py")) --state $state --forcing $forcing --summary $summary_path --monthly $monthly_path --next-state $nextstate --age $climate_age --interval-kyr $interval_kyr --metrics $metric_path --snapshot $snapshot`
        run(cmd)

        m = CSV.read(metric_path,DataFrame)
        m[!,:sim_year] = fill(year,nrow(m))
        m[!,:interval_years] = fill(1.0,nrow(m))
        m[!,:climate_age_ka] = fill(0.0,nrow(m))
        append!(metrics,m;cols=:union)
        CSV.write(joinpath(outdir,"timeseries_10y.csv"),metrics)

        mv(nextstate,state;force=true)
        println("YEAR_DONE year=$year meanH=$(metrics.mean_h_m[end]) meanNPP=$(metrics.mean_npp_gC_m2_yr[end]) meanZ=$(metrics.mean_z_m[end]) meanSoil=$(metrics.mean_soil_depth_m[end])")
        flush(stdout)
    end

    cp(state,joinpath(outdir,"final_state_10y.npz");force=true)
    println("ORIGINAL_DYNAMIC_10Y_COMPLETE years=$years interval_kyr=$interval_kyr climate_age_ka=$climate_age")
end

original_dynamic_10y_main()
'''

out.write_text(prefix + main, encoding='utf-8')
print('ORIGINAL_DYNAMIC_10Y_DRIVER_GENERATED')
