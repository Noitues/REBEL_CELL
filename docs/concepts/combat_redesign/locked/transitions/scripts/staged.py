"""staged.py: render the final locked p1 board as separate RGBA layers (for the T5/T6 bits FX and storyboard frames).
Usage:  CORP=neutral|solace  python staged.py [beat]
Imports the shared generator read-only from locked/corp/src (no file there is edited); caches go to transitions_work/cache.
Writes layers/<corp>_<beat>.npz with uint8 RGBA layers at 1920x1080 and a check composite (must match the real plate)."""
import sys, os, copy, json, time
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
HERE = 'D:/rc_scratch/combat_redesign/locked/transitions_work/'
CACHE = HERE + 'cache/' + os.environ.get('CORP', 'neutral') + '/'
os.makedirs(CACHE, exist_ok=True)
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import lw_render as LW            # installs the player family and the corp skin (CORP env)
R = LW.R
R.WORK = CACHE
LW.FH.CACHE = CACHE
A = R.A
FH = R.FH
from cv_lib import C, W, H, L2


def T():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def staged(beat='p1'):
    """a copy of f1_render._render (non hover beats) that keeps each stage on its own transparent layer"""
    A.set_room(R.ROOM)
    words = beat != 'nowords'
    R.NOW['words'] = words
    A.E.reg_reset()
    A.AU.BADGE_LOG.clear()
    A.CB9.HUB['name'] = 'Breaker' if words else ''
    key = R.KEY[beat]
    f = copy.deepcopy(A.J[key])
    hb = 'p1' if beat in ('nowords', 'p2b') else beat
    pbeat = hb
    out = {}
    Lhud = L2()
    saved = R.hud2.SCHED
    R.hud2.SCHED = R.ENAMEL
    bottom = R.hud2.draw_hud(Lhud, f, hb, None)
    R.hud2.SCHED = saved
    A.INFO['hud_bottom'] = bottom
    bg = A.G2.backdrop('P', 'P')
    out['bg'] = bg.copy()
    scr = T(); R.hud2.scrim_layers(scr, bottom); out['scrim'] = scr
    base = T(); base.alpha_composite(A.G2.plate('P').convert('RGBA')); base.alpha_composite(A.G2.bezel_layer('P').convert('RGBA'))
    out['base'] = base
    tw = R.tower_img(f, key, skip=None, hot=(beat != 'p3'), hov_sectors=None, nw=not words, trim=True)
    tsh, pad = R.shadow_of(tw, (3, 5), 7, 0.55)
    ox, oy = int(C[0] - R.FT.CT[0]), int(C[1] - R.FT.CT[1])
    tl = T(); tl.alpha_composite(tsh, (ox - pad, oy - pad)); tl.alpha_composite(tw, (ox, oy))
    out['tower'] = tl
    L = L2()
    A.S2.SKIP_LABELS[0] = True
    A.S2.schedule(L, f['schedule'], {})
    A.S2.SKIP_LABELS[0] = False
    A.S2.needle(L, 'P')
    R.paint_cells(L, f, pbeat)
    Lq = L2()
    A.M2.future(Lq, f, A.B10.arcs_data(f), {})
    A.W2B.ward_arc(L, f)
    R.draw_units(L, f, pbeat, skip=None)
    A.W2B.adjuster(L, f['adj'], pbeat)
    La = L2()
    R.A2.landing_arcs(La, f, {}, only={u['id'] for u in f['units']})
    Ltag = L2()
    A.M2.ring_tags(Ltag, f, 'P')
    if beat in ('p2', 'p3'):
        R.P2.twist_badge(Ltag, f, 'A')
        if f.get('refunds'):
            R.P2.refund_place(Ltag, f, 'A', 'A', words)
    if beat == 'p2':
        for tr in A.J['trigs']:
            R.PL.trigger_path(Ltag, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']), 'A')
    out['enemy1'] = L.done()
    g, _ = R.FG.make_guns(f, 0.58 if beat == 'p2' else 1.0, words)
    out['guns'] = g
    e2 = T()
    e2.alpha_composite(La.done())
    Llb = L2(); A.S2.labels(Llb, f['schedule'], {}); e2.alpha_composite(Llb.done())
    e2.alpha_composite(Lq.done())
    e2.alpha_composite(Ltag.done())
    Ldg = L2(); A.S2.digits(Ldg, 'P'); e2.alpha_composite(Ldg.done())
    out['enemy2'] = e2
    out['hud'] = Lhud.done()
    # ---- UI: YOU strip (rides the HUD), each card on its own layer, played slots, nameplate, SEND IT + UNDO stack
    you = T(); FH.place_ui(you, 'you', not words, f); out['you'] = you
    cards = []
    _put = FH.put

    def put(base_, im, cx, cy, ang=0.0, scale=1.0, shadow=True, off=(4, 8), blur=7):
        lay = T()
        r = _put(lay, im, cx, cy, ang, scale, shadow, off, blur)
        cards.append(dict(cx=cx, cy=cy, ang=ang))
        out['card%d' % (len(cards) - 1)] = lay
        base_.alpha_composite(lay)
        return r
    FH.put = put
    hand_all = T()
    FH.draw_hand(hand_all, A.J, beat, nw=not words)
    FH.put = _put
    hand, played, hov = FH.hand_lists(A.J, beat)
    lay, info = R.AS.stack_layer(words, {})
    m = Image.new('L', lay.size, 0)
    dr = ImageDraw.Draw(m)
    dr.rectangle([1655, 850, 1895, 899], fill=255)
    dr.rectangle([1660, 1028, 1900, 1060], fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    nm = T(); FH.place_ui(nm, 'name', not words); out['name'] = nm
    sd = T(); FH.place_ui(sd, 'send', not words); sd.alpha_composite(lay); out['send'] = sd
    meta = dict(beat=beat, corp=os.environ.get('CORP', 'neutral'), hand=hand, played=played, cards=cards, C=list(C))
    return out, meta


ORDER = ['scrim', 'base', 'tower', 'enemy1', 'guns', 'enemy2', 'hud', 'you']


def compose(out, ncards):
    im = out['bg'].copy().convert('RGBA')
    for k in ORDER:
        im.alpha_composite(out[k])
    for i in range(ncards):
        im.alpha_composite(out['card%d' % i])
    im.alpha_composite(out['name'])
    im.alpha_composite(out['send'])
    return im.convert('RGB')


if __name__ == '__main__':
    t0 = time.time()
    beat = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    corp = os.environ.get('CORP', 'neutral')
    out, meta = staged(beat)
    nc = len(meta['cards'])
    comp = compose(out, nc)
    tag = '%s_%s' % (corp, beat)
    comp.save(HERE + 'layers/%s_compose.png' % tag)
    real = R.render(beat)
    real.save(HERE + 'layers/%s_real.png' % tag)
    d = np.abs(np.asarray(comp).astype(int) - np.asarray(real).astype(int))
    meta['compose_vs_real'] = dict(max=int(d.max()), mean=float(d.mean()), px_over_8=int((d.max(-1) > 8).sum()))
    np.savez_compressed(HERE + 'layers/%s.npz' % tag, **{k: np.asarray(v.convert('RGBA')) for k, v in out.items()})
    json.dump(meta, open(HERE + 'layers/%s.json' % tag, 'w'), indent=1)
    print('ok', tag, meta['compose_vs_real'], round(time.time() - t0, 1))
