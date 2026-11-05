"""r2_fg_extract.py <corp>   (2026-11-04 round 2, backdrop stage)
Round-2 board transfer for the backdrop composites.  Renders the current p1 board (corp/src, read only) twice with the backdrop replaced
by a flat colour (0 and 128) and recovers the board as a linear transfer
    plate = F + T * backdrop
(per pixel and channel; every layer above the backdrop, the UI scrim slabs included, is an alpha composite, so the plate is linear in the
backdrop).  Writes round2/backdrop/work/fg_<corp>.npz (F uint8, T float16) and fg_<corp>_src.json (the corp/src sha1 it was rendered from).

Round 2: the published plates are rendered by asm_render.py with its capture hooks on (rb_set: 'asm_render.py <beat> auto 1').  Those
hooks draw each captured mark class into its own layer and composite it, which is not the same pixels as drawing it straight into the
board layer (a plain lw_render p1 misses the ring +1 lane line at r ~ 451 and parts of the bezel cube-glyph discs: max 47/255 vs
final/p1_decide.png).  So this script installs the same hooks as asm_render (text log, card log, non-raising draw asserts, rb_capture,
the per-class _cap wrappers and the hand wrapper) before it renders, and renders with the skin's own room, exactly as asm_render does.
Nothing is written to corp/: the masks stay in memory and the render cache is a fresh folder in round2/backdrop/work."""
import sys, os, time, hashlib, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/'
sys.path.insert(0, SRC)
os.chdir(SRC)
corp = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
os.environ['CORP'] = corp
beat = 'p1'
# ---------------------------------------------------------------- the asm_render hooks (asm_render.py lines 9-121, check = True), copied
from PIL import ImageDraw
TEXTLOG = []
_otext = ImageDraw.ImageDraw.text


def _t(self, xy, text, *a, **k):
    TEXTLOG.append(str(text))
    return _otext(self, xy, text, *a, **k)


ImageDraw.ImageDraw.text = _t
import lw_render as LW
import card_render as CR
CARDLOG = {}
_CUR = [None]
_orb = CR.render_base
_otx = CR.text


def _rb(spec, nowords=False, R=4.0, seed=0):
    _CUR[0] = (spec['name'], bool(nowords))
    return _orb(spec, nowords, R, seed)


def _tx(cv, txt, *a, **k):
    if _CUR[0] is not None:
        CARDLOG.setdefault('%s|%d' % _CUR[0], []).append(txt)
    return _otx(cv, txt, *a, **k)


CR.render_base = _rb
CR.text = _tx
import numpy as np
from PIL import Image
R = LW.R
A = R.A
import bd_grade as _BG
ROOMS = {r: 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % r for r in _BG.KIT_ROOMS}
room = _BG.CORP_ROOM.get(corp, 'bio')
LOGD = []
B10 = A.B10


def AD(name, got, want):
    LOGD.append(dict(name=name, ok=bool(got == want), got=str(got), want=str(want)))


B10.AD = AD
MASKS = {}


def _cap(cls, fn_owner, fn_name, Lidx=0):
    orig = getattr(fn_owner, fn_name)

    def wrap(*a, **k):
        L = a[Lidx]
        T = R.L2()
        a2 = list(a)
        a2[Lidx] = T
        r = orig(*a2, **k)
        L.im.alpha_composite(T.im)
        al = T.im.split()[3].resize((1920, 1080), Image.BOX)
        m = np.asarray(al) >= 128
        MASKS[cls] = MASKS.get(cls, np.zeros((1080, 1920), bool)) | m
        return r
    setattr(fn_owner, fn_name, wrap)


import rb_capture as RBC
RBC.install(R, A, R.FH, MASKS, beat)
_cap('digits', A.S2, 'digits')
_cap('labels', A.S2, 'labels')
_cap('tags', A.M2, 'ring_tags')
_cap('tags', A.P2, 'refund_place')
_cap('badges', A.P2, 'twist_badge')
_cap('badges', A.AU, 'warded_badge')
_cap('badges', A.AU, 'dead_badge')
_cap('tags', A.H2, 'hover_tag')
_cap('leader', A.H2, 'leader')
_cap('tickets', A.M2, 'future')
_cap('tape', A.S2, 'live_cell')
_cap('tape', A.S2, 'live_label')
_cap('tape', A.S2, 'chevrons')
_cap('plates', A.S2, 'hold_cell')
_cap('plates', A.S2, 'hold_live')
_cap('plates', A.S2.S, 'plus_cell')
_odh = R.FH.draw_hand


def _hand(base, *a, **k):
    T = Image.new('RGBA', base.size, (0, 0, 0, 0))
    r = _odh(T, *a, **k)
    base.alpha_composite(T)
    MASKS['hand'] = np.asarray(T.split()[3]) >= 128
    return r


R.FH.draw_hand = _hand
# ---------------------------------------------------------------- the transfer
WK = OUT + 'cache_r2h_%s/' % corp            # fresh: the tower is rendered under the hooks too
os.makedirs(WK, exist_ok=True)
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
    outs[v] = np.asarray(R.render(beat, room=ROOMS[room], check=False), np.float32)
    print('flat', v, round(time.time() - t0, 1), flush=True)
G2.backdrop = _orig_backdrop
F = outs[0]
T = np.clip((outs[128] - outs[0]) / 128.0, 0, 1)
np.savez_compressed(OUT + 'fg_%s.npz' % corp, F=F.astype(np.uint8), T=T.astype(np.float16))
hs = {}
for fn in sorted(os.listdir(SRC)):
    if fn.endswith('.py'):
        hs[fn] = hashlib.sha1(open(os.path.join(SRC, fn), 'rb').read()).hexdigest()[:12]
json.dump(dict(corp=corp, room=room, path='asm_render hooks (check on)', seconds=round(time.time() - t0, 1), src_sha1=hs,
               asserts=len(LOGD), assert_fail=sum(1 for x in LOGD if not x['ok'])), open(OUT + 'fg_%s_src.json' % corp, 'w'), indent=1)
print('done', corp, round(time.time() - t0, 1), flush=True)
