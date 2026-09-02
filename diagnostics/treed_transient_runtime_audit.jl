using CSV
using DataFrames
using Statistics

length(ARGS) == 1 || error("usage: julia treed_transient_runtime_audit.jl <reconstructed-model-root>")
root = normpath(ARGS[1])
core = joinpath(root, "src", "TREED_core.jl")
isfile(core) || error("missing TREED core: $core")
include(core)
using .TREEDCore

println("TREED_TRANSIENT_RUNTIME_AUDIT_BEGIN")
println("core_path=", core)
for sym in (:trait_optimizer, :trait_evolution, :plant_allometry, :GPP_function_for_optimization,
            :R_maintenance_function, :C_turnover_function, :calc_NPP, :calc_net_C_gain, :pars)
    println("symbol_", sym, "=", isdefined(TREEDCore, sym))
end

if isdefined(TREEDCore, :trait_evolution)
    println("trait_evolution_methods=")
    show(stdout, MIME("text/plain"), methods(TREEDCore.trait_evolution)); println()
end

cells_path = joinpath(root, "inputs", "cells.csv")
isfile(cells_path) || error("missing cells.csv: $cells_path")
cells = CSV.read(cells_path, DataFrame)
required = [:cell_id, :row, :col, :lon_deg, :lat_deg]
all(c -> c in propertynames(cells), required) || error("cells.csv missing required columns")
println("cell_count=", nrow(cells))
println("row_span=", minimum(cells.row), ":", maximum(cells.row))
println("col_span=", minimum(cells.col), ":", maximum(cells.col))
println("lon_span_deg=", minimum(cells.lon_deg), ":", maximum(cells.lon_deg))
println("lat_span_deg=", minimum(cells.lat_deg), ":", maximum(cells.lat_deg))

# Haversine distances are used only to audit the physical scale of the regional grid.
const R_EARTH_KM = 6371.0088
function haversine_km(lon1, lat1, lon2, lat2)
    p1 = deg2rad(lat1); p2 = deg2rad(lat2)
    dp = deg2rad(lat2-lat1); dl = deg2rad(lon2-lon1)
    a = sin(dp/2)^2 + cos(p1)*cos(p2)*sin(dl/2)^2
    return 2R_EARTH_KM * asin(min(1.0, sqrt(a)))
end

n = nrow(cells)
nearest = fill(Inf, n)
diameter = 0.0
for i in 1:n-1, j in i+1:n
    d = haversine_km(cells.lon_deg[i], cells.lat_deg[i], cells.lon_deg[j], cells.lat_deg[j])
    d < nearest[i] && (nearest[i] = d)
    d < nearest[j] && (nearest[j] = d)
    d > diameter && (diameter = d)
end
println("nearest_neighbor_km_median=", median(nearest))
println("nearest_neighbor_km_min=", minimum(nearest))
println("nearest_neighbor_km_max=", maximum(nearest))
println("domain_diameter_km=", diameter)

# The official TREED ecology implementation uses a dispersal radius in km.  Report
# how the published case-study radii compare with this regional domain; do not select
# a Yongneup parameter here.
for r in (200.0, 400.0, 600.0, 700.0)
    println("published_case_radius_", Int(r), "km_covers_domain=", r >= diameter)
end

println("TREED_TRANSIENT_RUNTIME_AUDIT_OK")
