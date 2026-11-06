"""gen_env: import the shared rebuilt generator (corp/src) READ-ONLY, with its tower / card caches redirected to this folder's work/gen_<skin>.
The skin is installed at import (env CORP), so use one process per skin.  Nothing in corp/src is written."""
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
CORP = os.environ.get('CORP', 'neutral')
WORK = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/work/gen_%s/' % CORP
os.makedirs(WORK, exist_ok=True)
LW.R.WORK = WORK            # rb_patch set it to corp/work/rb_cache; our own cache, rendered fresh
LW.FH.CACHE = WORK
R = LW.R
A = R.A
import bd_grade as BG
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(CORP, 'bio')
