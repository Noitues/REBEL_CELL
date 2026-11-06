"""fg_extract.py <corp> [verify]
Render the final p1 board twice with the backdrop replaced by a flat colour (0 and 128) and recover the board as a
linear transfer:  plate = F + T * backdrop   (per pixel, per channel; every layer above the backdrop is an alpha
composite, so the plate is linear in the backdrop).  Writes work/fg_<corp>.npz (F uint8, T float16).
'verify' also renders the real bio plate and reports the reconstruction error against it."""
import sys, os, time
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
corp = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
verify = len(sys.argv) > 2 and sys.argv[2] == 'verify'
os.environ['CORP'] = corp
import numpy as np
from PIL import Image
import lw_render as LW
HERE = 'D:/rc_scratch/combat_redesign/locked/backdrop/'
# stage 2: a fresh cache per generator version (the step-6 cache_<corp>/ held the pre-rebuild tower, which made the composites stale)
WK = HERE + 'work/cache_%s_%s/' % (os.environ.get('FG_CACHE_TAG', 'rb2'), corp)
os.makedirs(WK, exist_ok=True)
R = LW.R
R.WORK = WK
LW.FH.CACHE = WK
G2 = R.A.G2
_orig_backdrop = G2.backdrop


def flat(v):
    return lambda *a, **k: Image.new('RGBA', (1920, 1080), (v, v, v, 255))


t0 = time.time()
outs = {}
for v in (0, 128):
    G2.backdrop = flat(v)
    outs[v] = np.asarray(R.render('p1'), np.float32)
    print('flat', v, round(time.time() - t0, 1), flush=True)
F = outs[0]
T = np.clip((outs[128] - outs[0]) / 128.0, 0, 1)
np.savez_compressed(HERE + 'work/fg_%s.npz' % corp, F=F.astype(np.uint8), T=T.astype(np.float16))
if verify:
    G2.backdrop = _orig_backdrop
    real = np.asarray(R.render('p1'), np.float32)
    Image.fromarray(real.astype(np.uint8)).save(HERE + 'work/real_p1_%s.png' % corp)
    bd = np.asarray(_orig_backdrop('P', 'P').convert('RGB'), np.float32)
    rec = F + T * bd
    err = np.abs(rec - real)
    print('verify mean abs err', float(err.mean()), 'p99.9', float(np.percentile(err, 99.9)), 'max', float(err.max()), flush=True)
print('done', corp, round(time.time() - t0, 1), flush=True)
