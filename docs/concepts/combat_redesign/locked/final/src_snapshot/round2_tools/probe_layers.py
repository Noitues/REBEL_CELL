"""C3 source hunt: render one plate with the asm_render + rb_capture classes AND extra per-drawer classes, then report which drawer owns the
bright pixels (L* >= thr) inside r < 480 that no rb_capture / asm class covers.
python probe_layers.py <beat> <corp> <outdir> [thr]"""
import sys, os, time
sys.dont_write_bytecode = True
beat, corp, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
thr = float(sys.argv[4]) if len(sys.argv) > 4 else 88.0
os.environ['CORP'] = corp
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.makedirs(OUT, exist_ok=True)
import lw_render as LW
import bd_grade as BG
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R = LW.R
R.WORK = OUT + '/'
A = R.A
import card_render as _CR  # noqa
import rb_capture as RBC
import rb_tokens as T
M = {}
RBC.install(R, A, R.FH, M, beat)


def cap(cls, owner, name, Lidx=0):
    orig = getattr(owner, name)

    def wrap(*a, **k):
        L = a[Lidx]
        Tl = R.L2()
        a2 = list(a)
        a2[Lidx] = Tl
        r = orig(*a2, **k)
        L.im.alpha_composite(Tl.im)
        m = np.asarray(Tl.im.split()[3].resize((1920, 1080), Image.BOX)) >= 128
        M[cls] = M.get(cls, np.zeros((1080, 1920), bool)) | m
        CNT[cls] = CNT.get(cls, 0) + 1
        return r
    setattr(owner, name, wrap)


def cap_img(cls, owner, name):
    orig = getattr(owner, name)

    def wrap(*a, **k):
        im = orig(*a, **k)
        al = np.asarray(im.convert('RGBA').split()[3]) >= 128
        M[cls] = M.get(cls, np.zeros((1080, 1920), bool)) | al
        CNT[cls] = CNT.get(cls, 0) + 1
        return im
    setattr(owner, name, wrap)


CNT = {}
# asm_render classes
for cls, ow, nm in (('digits', A.S2, 'digits'), ('labels', A.S2, 'labels'), ('tags', A.M2, 'ring_tags'), ('badges', A.P2, 'twist_badge'),
                    ('badges', A.AU, 'warded_badge'), ('badges', A.AU, 'dead_badge'), ('tickets', A.M2, 'future'), ('tape', A.S2, 'live_cell'),
                    ('tape', A.S2, 'live_label'), ('tape', A.S2, 'chevrons'), ('plates', A.S2, 'hold_cell'), ('plates', A.S2, 'hold_live'),
                    ('plates', A.S2.S, 'plus_cell')):
    cap(cls, ow, nm)
import wr2_units as W2U
import r2_arcs as RA
import f1_board as FB
import gram as G
X = {}
cand = [('x_outline', W2U, 'outline'), ('x_gutters', A.W2C, 'gutters'), ('x_schedule', A.S2, 'schedule'), ('x_ward', A.W2B, 'ward_arc'),
        ('x_adjuster', A.W2B, 'adjuster'), ('x_arcframe', RA, 'frame'), ('x_arcdisc', RA, 'disc'), ('x_turndots', RA, 'turn_dots'),
        ('x_nowdot', RA, 'now_dot'), ('x_landing', RA, 'landing_arcs'), ('x_empty', FB, 'empty_cell'), ('x_halo', A.W2U, 'halo'),
        ('x_hpw2', W2U, 'hp_row')]
for cls, ow, nm in cand:
    if hasattr(ow, nm):
        cap(cls, ow, nm)
cap('x_paint', R, 'paint_cells') if hasattr(R, 'paint_cells') else None
cap_img('x_plate', A.G2, 'plate')
cap_img('x_bezel', A.G2, 'bezel_layer')
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(corp, 'bio')
t = time.time()
im = R.render(beat, room=ROOM)
im.save(OUT + '/plate.png')
print('rendered', round(time.time() - t), 's; hook counts', CNT, flush=True)
rgb = np.asarray(im).astype(np.float64)
Ls = T.lstar(T.lum(rgb))
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
known = np.zeros((1080, 1920), bool)
for k, m in M.items():
    if not k.startswith('x_') and not k.startswith('card_') and k != 'scrim':
        known |= m
sel = (rho < 480) & ~known & (Ls >= thr)
print('unclassed bright px', int(sel.sum()))
for k in sorted(M):
    if k.startswith('x_'):
        own = sel & M[k]
        print('  %-12s owns %6d of them; class px %7d; max L* in class %.1f' % (k, int(own.sum()), int(M[k].sum()), float(Ls[M[k]].max()) if M[k].any() else 0))
rest = sel.copy()
for k in M:
    if k.startswith('x_') and k not in ('x_plate', 'x_bezel', 'x_paint', 'x_landing', 'x_schedule'):
        rest &= ~M[k]
lab, n = ndi.label(rest, structure=np.ones((3, 3)))
print('not owned by a narrow drawer:', int(rest.sum()), 'clusters', n)
rows = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    m = lab[sl] == i
    rows.append((int(m.sum()), sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, float(Ls[sl][m].max()), float(np.median(rho[sl][m])),
                 [k for k in ('x_plate', 'x_bezel', 'x_paint', 'x_landing', 'x_schedule') if k in M and (M[k][sl] & m).any()]))
rows.sort(key=lambda r: -r[0])
for r in rows[:30]:
    print('  px %5d box x %d-%d y %d-%d maxL %.1f r %.0f in %s' % r)
np.savez_compressed(OUT + '/masks.npz', **{k: np.packbits(v) for k, v in M.items() if not k.startswith('card_')})
