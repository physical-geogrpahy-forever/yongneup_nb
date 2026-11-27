import sys, re
sys.path.insert(0, '/home/claude/final/PB4Studio_v6.6.3_CHELSA21K')
from pathlib import Path
from pb4studio import biome4_backend as B
src = B._find_file(B._variant_source_filename('mckenzie2003'))
out = Path('/home/claude/firecheck/patched.f')
B._patch_fortran_source(src, out, biome4_variant='mckenzie2003')
t = out.read_text(encoding='latin-1')
assert t.count("       wet(d)=wr_n\n")==1
t = t.replace("       wet(d)=wr_n\n","       wet(d)=wr_n\n       write(77,'(2I5,8F11.4)') pft,d,w(1),w(2),wr_n,dprec(d),\n     >  dmelt(d),aet,rtop_eff,rbot_eff\n",1)
out.write_text(t, encoding='latin-1')
B._write_batch_wrapper(Path('/home/claude/firecheck/wrapper.f90'), biome4_variant='mckenzie2003')
print('ok')
