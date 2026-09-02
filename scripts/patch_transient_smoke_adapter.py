from pathlib import Path

p = Path('diagnostics/run_transient_smoke.jl')
s = p.read_text(encoding='utf-8')

old = '''include(joinpath(ROOT,"src","TREED_core.jl"))
using .TREEDCore

isdefined(TREEDCore,:trait_evolution) || error("production TREEDCore does not expose trait_evolution")
'''
new = '''include(joinpath(ROOT,"src","TREED_core.jl"))
using .TREEDCore
include(joinpath(@__DIR__, "treed_v1_transient_adapter.jl"))

'''
assert s.count(old) == 1, 'unexpected smoke-runner header'
s = s.replace(old, new)

old_call = 'e=TREEDCore.trait_evolution(optimized_traits=optimized_traits,env=env,tr=start,par=TREEDCore.pars,evorate=evorate)'
new_call = 'e=treed_v1_trait_evolution(optimized_traits=optimized_traits,env=env,tr=start,par=TREEDCore.pars,evorate=evorate)'
assert s.count(old_call) == 1, 'unexpected trait-evolution call site'
s = s.replace(old_call, new_call)

p.write_text(s, encoding='utf-8')
print('TREED_V1_TRANSIENT_ADAPTER_INJECTED')
