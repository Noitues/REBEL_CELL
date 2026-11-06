"""sp_render: the Spider-Punk collage plate set.  Reuses the F1 board + HUD + grammar; swaps the player family (wheel, hand, SEND IT, nameplate, YOU strip) and removes the needle.
usage: python sp_render.py A|B [beat]"""
import sys, os, time
sys.dont_write_bytecode = True
import f1_render as R
import f1_tower as FT0
import f1_hand as FH
import sp_tower as SPT
import sp_cards as SC
import sp_ui as SU
from PIL import Image

ROOT = 'D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/'
SEEDS = {'Brace': 1, 'Spin3': 4, 'Trigger': 7, 'Twist': 10}

# the new concept has no needle
R.A.S2.needle = lambda L, opt: None

FT0.render_tower = SPT.render_tower
_V = ['A']


def card_hi(name, nw, seed=None):
    key = (name, nw, _V[0])
    if key in FH._mem:
        return FH._mem[key]
    fp = FH.CACHE + 'card_%s_%d.png' % (name, nw)
    if os.path.exists(fp):
        im = Image.open(fp).convert('RGBA')
    else:
        SC.NW[0] = nw
        im = SC.render_card(name, _V[0], seed=SEEDS.get(name, 13), ss=4, scale=2)
        SC.NW[0] = False
        im.save(fp)
    FH._mem[key] = im
    return im


def ui_img(kind, nw, f=None, seed=0):
    key = (kind, nw, _V[0], None if f is None else (f['hp'], f['pv']['hp_after']))
    if key in FH._ui:
        return FH._ui[key]
    if kind == 'send':
        r = SU.send_it(_V[0], ss=3, scale=1, nw=nw)
    elif kind == 'name':
        r = SU.nameplate(_V[0], ss=3, scale=1, nw=nw)
    else:
        r = SU.you_strip(f, _V[0], ss=3, nw=nw)
    FH._ui[key] = r
    return r


FH.card_hi = card_hi
FH.ui_img = ui_img


def setv(V):
    _V[0] = V
    SPT.VARIANT[0] = V
    R.WORK = ROOT + 'w2_%s/' % V
    FH.CACHE = R.WORK
    os.makedirs(R.WORK, exist_ok=True)
    R._tw.clear()


def render(V, beat='p1', **kw):
    setv(V)
    return R.render(beat=beat, **kw)


if __name__ == '__main__':
    V = sys.argv[1] if len(sys.argv) > 1 else 'A'
    beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
    t = time.time()
    im = render(V, beat)
    os.makedirs(ROOT + 'out/', exist_ok=True)
    im.save(ROOT + 'out/%s_%s.png' % (beat, V))
    print('ok', V, beat, round(time.time() - t))
