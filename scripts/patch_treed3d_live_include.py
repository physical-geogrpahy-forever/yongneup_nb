from pathlib import Path

p = Path('treed120/julia/run_120ka.jl')
s = p.read_text()
old = '\nmain()\n'
new = '\nif abspath(PROGRAM_FILE) == @__FILE__\n    main()\nend\n'
if old not in s:
    raise SystemExit('Expected terminal main() call not found')
if s.count(old) != 1:
    raise SystemExit(f'Expected exactly one terminal main() call, found {s.count(old)}')
p.write_text(s.replace(old, new))
print('TREED3D_INCLUDE_GUARD_OK')
