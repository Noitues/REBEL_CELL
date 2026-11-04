"""staged.py (2026-11-04 rebuild): render the rebuilt p1 board as separate RGBA layers for the T5 / T6 transitions.
Usage:  CORP=neutral|solace  python staged.py [beat]
Imports the shared generator read-only from locked/corp/src (no file there is edited); its tower / card caches go to this
folder's cache/<corp>/.  It is a copy of the current f1_render._render (non hover beats) that keeps each stage on its own
transparent layer; the rebuild patches (rb_patch, rb2_patch, rb3_patch) are installed by lw_render exactly as for the plates.
The room is the skin's own room (bd_grade.CORP_ROOM), as asm_render 'auto' picks it.
Writes layers/<corp>_<beat>.npz (uint8 RGBA 1920x1080 layers + the bare and graded rooms), <corp>_<beat>.json (meta and the
compose check against the published plate in locked/final/)."""
import sys, os, copy, json, time
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/'
CORP = os.environ.get('CORP', 'neutral')
CACHE = HERE + 'cache/' + CORP + '/'
os.makedirs(CACHE, exist_ok=True)
os.makedirs(HERE + 'layers', exist_ok=True)
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import lw_render as LW            # installs the player family, the corp skin (CORP env) and rb_patch / rb2_patch / rb3_patch
R = LW.R
R.WORK = CACHE                    # fresh tower cache: never a stale tower from another pass
LW.FH.CACHE = CACHE
A = R.A
FH = R.FH
import bd_grade as BG
from cv_lib import C, W, H, L2
ROOM_NAME = BG.CORP_ROOM.get(CORP, 'bio')
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % ROOM_NAME
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
PLATE = {'p1': 'p1_decide', 'nowords': 'p1_nowords'}


def T():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def staged(beat='p1'):
    """f1_render._render (2026-11-04, non hover) with each stage on its own transparent layer"""
    A.set_room(ROOM)
    words = beat != 'nowords'
    R.NOW['words'] = words
    A.E.reg_reset()
    A.AU.BADGE_LOG.clear()
    A.CB9.HUB['name'] = 'Breaker' if words else ''
    key = R.KEY[beat]
    f = copy.deepcopy(A.J[key])
    o = dict(R.WCR.PICKS)
    R.WCR.sel_for(o, beat)
    hb = 'p1' if beat in ('nowords', 'p2b') else beat
    pbeat = hb
    out = {}
    Lhud = L2()
    saved = R.hud2.SCHED
    R.hud2.SCHED = R.ENAMEL
    bottom = R.hud2.draw_hud(Lhud, f, hb, None)
    R.hud2.SCHED = saved
    A.INFO['hud_bottom'] = bottom
    # the rooms: v3.1 bare, the rb2-1 grade alone (no board scrim) and the plate's room (grade + board scrim)
    out['room_bare'] = np.asarray(Image.fromarray(np.clip(A.G2.bare(), 0, 255).astype(np.uint8)).convert('RGB'))
    out['room_graded'] = np.clip(A.G2.grade('P'), 0, 255).astype(np.uint8)
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
    gl = T(); gl.alpha_composite(g); out['guns'] = gl
    e2 = T()
    e2.alpha_composite(La.done())
    Llb = L2(); A.S2.labels(Llb, f['schedule'], {}); e2.alpha_composite(Llb.done())
    out['tickets'] = Lq.done()          # the W4-W6 tickets (the queue): own layer, composited in the same place as before
    e2b = T()
    e2b.alpha_composite(Ltag.done())
    Ldg = L2(); A.S2.digits(Ldg, 'P'); e2b.alpha_composite(Ldg.done())
    out['enemy2'] = e2
    out['enemy3'] = e2b
    out['hud'] = Lhud.done()
    # ---- UI: YOU strip, each card on its own layer, nameplate, SEND IT + UNDO stack
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
    try:
        FH.draw_hand(hand_all, A.J, beat, nw=not words, lift=None, dim_others=None)
    finally:
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
    meta = dict(beat=beat, corp=CORP, room=ROOM_NAME, hand=hand, played=played, cards=cards, C=list(C), hud_bottom=bottom)
    return out, meta


ORDER = ['scrim', 'base', 'tower', 'enemy1', 'guns', 'enemy2', 'tickets', 'enemy3', 'hud', 'you']


def compose(out, ncards):
    im = out['bg'].copy().convert('RGBA')
    for k in ORDER:
        im.alpha_composite(out[k])
    for i in range(ncards):
        im.alpha_composite(out['card%d' % i])
    im.alpha_composite(out['name'])
    im.alpha_composite(out['send'])
    return im.convert('RGB')


def diff(a, b):
    d = np.abs(np.asarray(a).astype(int) - np.asarray(b).astype(int))
    return dict(max=int(d.max()), mean=round(float(d.mean()), 4), px_over_2=int((d.max(-1) > 2).sum()), px_over_8=int((d.max(-1) > 8).sum()))


if __name__ == '__main__':
    t0 = time.time()
    beat = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    out, meta = staged(beat)
    nc = len(meta['cards'])
    comp = compose(out, nc)
    tag = '%s_%s' % (CORP, beat)
    comp.save(HERE + 'layers/%s_compose.png' % tag)
    pub = FINAL + PLATE[beat] + ('' if CORP == 'neutral' else '_' + CORP) + '.png'
    meta['published_plate'] = pub
    meta['compose_vs_published'] = diff(comp, Image.open(pub).convert('RGB'))
    if os.environ.get('REAL', '0') == '1':
        real = R.render(beat, room=ROOM)
        real.save(HERE + 'layers/%s_real.png' % tag)
        meta['compose_vs_real_render'] = diff(comp, real)
        meta['real_render_vs_published'] = diff(real, Image.open(pub).convert('RGB'))
    np.savez_compressed(HERE + 'layers/%s.npz' % tag, **{k: (np.asarray(v.convert('RGBA')) if isinstance(v, Image.Image) else v) for k, v in out.items()})
    json.dump(meta, open(HERE + 'layers/%s.json' % tag, 'w'), indent=1)
    print('ok', tag, 'vs published', meta['compose_vs_published'], meta.get('compose_vs_real_render'), round(time.time() - t0, 1), flush=True)
