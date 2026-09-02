using CSV
using DataFrames

# The audited production driver is made includable by scripts/patch_treed3d_live_include.py.
# Including it exposes the exact production functions (coupled_cell,
# write_age_outputs, initialize_frozen_traits, etc.) without running main().
include(joinpath(@__DIR__, "..", "treed120", "julia", "run_120ka.jl"))

mutable struct LiveSession
    mode::String
    age::Int
    state::String
    work::String
    outdir::String
    fixed_traits::Dict{Int,Any}
    prev_es::Dict{Int,Vector{Float64}}
    prev_jan::Dict{Int,Float64}
    frozen_initial_pathology::Set{Int}
    metrics::DataFrame
end

function init_live_session(mode::String, session_dir::String; start_age::Int=120)
    mode in ("dynamic", "frozen") || error("mode must be dynamic or frozen")
    start_age == 120 || error("v0 live engine must start from the audited 120 ka initial state")

    root = ROOT
    work = joinpath(session_dir, "work")
    outdir = joinpath(session_dir, "results")
    mkpath(work)
    mkpath(outdir)
    mkpath(joinpath(outdir, "snapshots"))
    mkpath(joinpath(outdir, "physiology"))

    state = joinpath(work, "state_120.npz")
    cp(joinpath(root, "inputs", "init_grid.npz"), state; force=true)

    return LiveSession(
        mode,
        start_age,
        state,
        work,
        outdir,
        Dict{Int,Any}(),
        Dict{Int,Vector{Float64}}(),
        Dict{Int,Float64}(),
        Set{Int}(),
        DataFrame(),
    )
end

function step_age!(s::LiveSession)
    s.age < 0 && error("live session is already complete")

    age = s.age
    forcing = joinpath(s.work, "forcing_$(age).csv")
    run(`python $(joinpath(ROOT, "python", "prepare_age_input.py")) --age $age --state $(s.state) --out $forcing`)
    inp = CSV.read(forcing, DataFrame)

    if s.mode == "frozen" && age == 120
        s.fixed_traits, s.prev_es, s.prev_jan, s.frozen_initial_pathology = initialize_frozen_traits(inp)
    end

    summary_path = joinpath(s.work, "summary.csv")
    monthly_path = joinpath(s.work, "monthly.csv")
    s.prev_es, s.prev_jan, summary = write_age_outputs(
        inp,
        s.mode,
        s.fixed_traits,
        s.prev_es,
        s.prev_jan,
        summary_path,
        monthly_path,
        s.frozen_initial_pathology,
    )

    # Preserve the actual physiology/bucket state for the live front-end.
    summary_keep = joinpath(s.outdir, "physiology", "summary_$(lpad(age, 3, '0'))ka.csv")
    monthly_keep = joinpath(s.outdir, "physiology", "monthly_$(lpad(age, 3, '0'))ka.csv")
    cp(summary_path, summary_keep; force=true)
    cp(monthly_path, monthly_keep; force=true)

    nextstate = joinpath(s.work, "state_next.npz")
    metric_path = joinpath(s.work, "metric.csv")
    snapshot = joinpath(s.outdir, "snapshots", "snapshot_$(lpad(age, 3, '0'))ka.csv")
    interval = age == 0 ? 0.0 : 1.0

    cmd = `python $(joinpath(ROOT, "python", "run_geomorph_step.py")) --state $(s.state) --forcing $forcing --summary $summary_path --monthly $monthly_path --next-state $nextstate --age $age --interval-kyr $interval --metrics $metric_path --snapshot $snapshot`
    run(cmd)

    m = CSV.read(metric_path, DataFrame)
    m[!, :mode] = fill(s.mode, nrow(m))
    append!(s.metrics, m; cols=:union)
    CSV.write(joinpath(s.outdir, "timeseries.csv"), s.metrics)

    # Exact production state transition: state_next becomes the forcing/topography
    # state for the next age. At 0 ka production retains the current state.
    if age > 0
        mv(nextstate, s.state; force=true)
    else
        cp(s.state, joinpath(s.outdir, "final_state.npz"); force=true)
    end

    rm(forcing; force=true)
    rm(summary_path; force=true)
    rm(monthly_path; force=true)
    rm(metric_path; force=true)
    rm(nextstate; force=true)

    s.age -= 1
    return (
        completed_age=age,
        next_age=s.age,
        snapshot=snapshot,
        summary=summary_keep,
        monthly=monthly_keep,
        metric=NamedTuple(m[1, :]),
    )
end

function emit_status(s::LiveSession)
    println("LIVE_STATUS\tmode=$(s.mode)\tnext_age=$(s.age)\tsteps=$(nrow(s.metrics))")
    flush(stdout)
end

function emit_state(result)
    m = result.metric
    println(
        "LIVE_STATE",
        '\t', "age=", result.completed_age,
        '\t', "next_age=", result.next_age,
        '\t', "snapshot=", result.snapshot,
        '\t', "summary=", result.summary,
        '\t', "monthly=", result.monthly,
        '\t', "mean_z_m=", m.mean_z_m,
        '\t', "mean_h_m=", m.mean_h_m,
        '\t', "mean_npp_gC_m2_yr=", m.mean_npp_gC_m2_yr,
        '\t', "mean_agb_dry_kg_m2=", m.mean_agb_dry_kg_m2,
    )
    flush(stdout)
end

function command_loop(mode::String, session_dir::String)
    s = init_live_session(mode, session_dir)
    println("LIVE_READY\tmode=$(s.mode)\tnext_age=$(s.age)\tsession=$(session_dir)")
    flush(stdout)

    for raw in eachline(stdin)
        cmd = strip(raw)
        isempty(cmd) && continue
        if cmd == "STEP"
            emit_state(step_age!(s))
        elseif startswith(cmd, "RUN ")
            parts = split(cmd)
            length(parts) == 2 || error("RUN requires an integer step count")
            n = parse(Int, parts[2])
            n >= 1 || error("RUN step count must be >= 1")
            for _ in 1:n
                s.age < 0 && break
                emit_state(step_age!(s))
            end
        elseif cmd == "STATUS"
            emit_status(s)
        elseif cmd == "QUIT"
            println("LIVE_BYE")
            flush(stdout)
            return
        else
            println("LIVE_ERROR\tunknown_command=$(cmd)")
            flush(stdout)
        end
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    length(ARGS) >= 2 || error("usage: julia live_engine.jl <dynamic|frozen> <session_dir>")
    command_loop(ARGS[1], ARGS[2])
end
