"""gen_env: import the shared locked generator read-only, with its caches redirected to fx_cdhl/work/gen."""
import sys, os
sys.dont_write_bytecode = True
GEN = 'D:/rc_scratch/combat_redesign/locked/corp/src'
if GEN not in sys.path:
    sys.path.insert(0, GEN)
os.chdir(GEN)
_argv = sys.argv[:]
sys.argv = [sys.argv[0], 'p1']
import lw_render as LW
sys.argv = _argv
WORK = 'D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/gen/'
LW.R.WORK = WORK
LW.FH.CACHE = WORK
R = LW.R
A = R.A
