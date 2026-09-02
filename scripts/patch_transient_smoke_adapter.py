from pathlib import Path

p = Path('diagnostics/run_transient_smoke.jl')
s = p.read_text(encoding='utf-8')

# Julia include() resolves relative paths against the including source file, not
# necessarily the process working directory.  Make CLI paths absolute before
# the runner includes the reconstructed production TREED core.
old_root = 'const ROOT = normpath(ARGS[1])\n'
new_root = 'const ROOT = abspath(ARGS[1])\n'
assert s.count(old_root) == 1, 'unexpected smoke-runner ROOT declaration'
s = s.replace(old_root, new_root)

old_out = 'const OUTDIR = normpath(ARGS[4])\n'
new_out = 'const OUTDIR = abspath(ARGS[4])\n'
assert s.count(old_out) == 1, 'unexpected smoke-runner OUTDIR declaration'
s = s.replace(old_out, new_out)

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
print('TREED_V1_TRANSIENT_ADAPTER_INJECTED_ABSOLUTE_PATHS')
