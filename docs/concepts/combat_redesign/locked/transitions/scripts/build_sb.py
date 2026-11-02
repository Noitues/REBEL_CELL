"""Storyboard frames T2, T3, T5 (neutral + Solace) and T6 on the final locked combat board, and a sheet of them.
Reads the v3 storyboard helpers/text read-only (transitions/v3/scripts) and the option A keys from out/<corp>/keys.
Writes to transitions_work/sb/ (then copied to the repo deliverable folder by publish.py)."""
import os, sys, math, random, textwrap, copy
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/v3/scripts')
from helpers3 import *            # W, H, LIME, PINK, AMB, F, MF, L, GIF, zc, blend, dark, desat, scan, glow_line, marker, terminal_panel, stamp, R
from text3 import TEXT
import numpy as np

WK = 'D:/rc_scratch/combat_redesign/locked/transitions_work/'
OUT = WK + 'sb/'
os.makedirs(OUT, exist_ok=True)
FIN = R + 'combat_redesign/locked/final/'
plate = {'neutral': L(FIN + 'p1_decide.png'), 'solace': L(FIN + 'p1_decide_solace.png')}
bare = L('combat_backdrop/v3_1/room_bio_bare.png')


def key(corp, which, t):
    return Image.open(WK + 'out/%s/keys/%s_%03d.png' % (corp, which, int(round(t * 100)))).convert('RGB').resize((W, H), Image.LANCZOS)


# ---- K2: the real spinner layer (tower) scaled over the dimming room, at full resolution (a composite of real layers)
def spinner_in(corp, t=0.38):
    Z = np.load(WK + 'layers/%s_p1.npz' % corp)
    bg = Z['bg'][..., :3].astype(np.float32); bb = np.asarray(bare).astype(np.float32)
    u = min(max((t - 0.20) / 0.40, 0), 1); w = u * u * (3 - 2 * u)
    base = Image.fromarray(np.clip(bb + (bg - bb) * w, 0, 255).astype(np.uint8)).convert('RGBA')
    tw = Image.fromarray(Z['tower'])
    v = min(max((t - 0.25) / 0.30, 0), 1); e = 1 - (1 - v) ** 3
    s = 1 + 0.35 * (1 - e); rot = 7.0 * (1 - e); a = min(v * 2.2, 1)
    C = (536, 540); B = 260
    c = tw.crop((C[0] - B, C[1] - B, C[0] + B, C[1] + B))
    n = int(2 * B * s)
    c = c.resize((n, n), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC)
    c.putalpha(c.split()[3].point(lambda x: int(x * a)))
    base.alpha_composite(c, (int(C[0] - n / 2), int(C[1] - n / 2)))
    return base.convert('RGB')


# ---- copies of the v3 builders that T2/T3/T6 need (unchanged logic, build3.py)
MP = 'cohesion/map_pages_r42/'
TR = 'tide_raid/G1_parity/final_proposed/'
ZR4 = 'netrun_cel/zoom_rules/round4/zoom_motion.gif'
FLK = 'netrun_cel/zoom_rules/round7/street_band_flicker_4s_12fps.gif'
route = L(MP + 'route_page.png'); hqs = L(MP + 'hq_node_selected.png')
city = L(TR + '01_plan_side_by_side.png', half=True)
hl = L('netrun_cel/zoom_rules/round7b/candB/stage_1_layers.png')
street_raw = L('netrun_cel/zoom_rules/round6/street_frame.png')
NET = (.34, .58)
ROOMS = [(.378, 'FIGHT'), (.592, 'EVENT'), (.823, 'SHOP')]
def gf(i): return GIF(ZR4, i)
def zi(t, dur): return int(round(min(max(t / dur, 0), 1) * 74))


def street(sel=None, ribbon=True, cleared=None):
    im = glow_line(street_raw, [(.02, .96), (.3, .92), (.5, .90), (.72, .92), (.98, .96)]) if ribbon else street_raw.copy()
    d = ImageDraw.Draw(im)
    for i, (xr, tag) in enumerate(ROOMS):
        x = xr * W
        d.rectangle((x - 78, 742, x + 78, 858), outline=LIME, width=5)
        d.rectangle((x - 78, 706, x + 78, 742), fill=(10, 40, 20))
        d.text((x - 62, 710), tag, font=MF(24), fill=LIME)
        if cleared == i:
            d.line((x + 30, 716, x + 42, 732, x + 62, 706), fill=LIME, width=6)
    return im


def fail_screen():
    im = dark(desat(route, .35), .35)
    r = random.Random(5)
    for _ in range(14):
        y = r.randrange(0, H - 40); h_ = r.randrange(8, 40); dx = r.randrange(-60, 60)
        im.paste(im.crop((0, y, W, y + h_)), (dx, y))
    im = Image.blend(im, Image.new('RGB', (W, H), (90, 10, 60)), .22)
    im = scan(im, .25)
    terminal_panel(im, (300, 250, 1620, 800), '> TERMINAL // SOLACE BIOSYSTEMS // TRACE COMPLETE', [
        ('CELL-9 SIGNAL LOST', PINK, 64), ('', None, 20),
        ('> netrun terminated at node 4 of 7', None, 28), ('> operative flatlined; home server holds', None, 28),
        ('> rewards forfeited, heat +2', AMB, 28), ('', None, 20),
        ('[ BACK TO CITY ]        [ VIEW TRACE LOG ]', LIME, 30)], col=PINK)
    ImageDraw.Draw(im).text((1180, 640), 'NETRUN LOST', font=F(72, True), fill=(255, 60, 100))
    return im


def tear_of(im):
    tear = im.copy(); rr = random.Random(8)
    for _ in range(20):
        y = rr.randrange(0, H - 40); h_ = rr.randrange(10, 50)
        tear.paste(tear.crop((0, y, W, y + h_)), (rr.randrange(-90, 90), y))
    return Image.blend(tear, Image.new('RGB', (W, H), (80, 0, 50)), .25)


T = {t['id']: copy.deepcopy(t) for t in TEXT}

# ---- T2, T3: same frames as v3 (they contain no combat board)
k1 = marker(city.copy(), *NET, 'before')
card = hqs.crop((1180, 440, 1920, 760)); btn = hqs.crop((1500, 900, 1920, 1080))
k2 = k1.copy(); k2.paste(card, (1160, 380))
k3 = k2.copy(); k3.paste(btn, (1500, 900)); k3 = Image.blend(k3, Image.new('RGB', (W, H), (255, 255, 255)), .35)
FR = {}
FR['t02'] = [k1, k2, k3, blend(dark(marker(city.copy(), *NET, 'before'), .75), hl, .5), hl]
FR['t03'] = [hl] + [glow_line(gf(zi(t, 1.4)), p) for t, p in (
    (.3, [(.2, .9), (.4, .6), (.6, .5)]), (.65, [(.1, .95), (.35, .7), (.6, .55), (.8, .4)]),
    (.95, [(.05, .98), (.4, .88), (.7, .8)]), (1.2, [(.02, .96), (.4, .9), (.8, .88)]))] + [street(), GIF(FLK, 24)]
KIND = {'t02': 'CCCCR', 't03': 'RCCCCCR'}
NOTE23 = (' Unchanged in this pass (2026-11-02, locked combat board): T2 and T3 contain no combat board. The old wheel-circle zoom was '
          'removed in v3, so there is no combat frame here to replace; the frames are the v3 frames, re-rendered on the new sheet.')
for k in ('t02', 't03'):
    T[k]['chg'] = T[k]['chg'] + NOTE23

# ---- T5 (neutral, Solace) and T6 on the final locked board
for corp, tid in (('neutral', 't05'), ('solace', 't05s')):
    nm = '' if corp == 'neutral' else ' (Solace skin)'
    FR[tid] = [bare, spinner_in(corp), key(corp, 't5', .55), key(corp, 't5', .85), key(corp, 't5', 1.12), plate[corp]]
    KIND[tid] = 'RCXXXR'
    base = copy.deepcopy(TEXT[[t['id'] for t in TEXT].index('t05')])
    base['id'] = tid
    base['title'] = 'T5  Room to combat: the spinner flies in, the enemy rings fly from the room as bits' + nm
    base['file'] = 't05_room_to_combat%s.jpg' % ('' if corp == 'neutral' else '_solace')
    base['labels'] = ['K1  0.00 s  cutaway room, nothing on it (v3.1 bio)',
                      'K2  0.38 s  the spinner flies in, 1.35x to 1.0x (real layer)',
                      'K3  0.55 s  glyph bits leave the lab, keylines start the rings',
                      'K4  0.85 s  rings 0-2 drawn, the frame band (silver tape) closing',
                      'K5  1.12 s  locked; guns armed, HUD and WPAP cards deal in',
                      'K6  1.20 s  combat begins: final locked board p1_decide' + ('_solace' if corp == 'solace' else '')]
    base['real'] = ('K1 (v3.1 bio room) and K6 (the final locked p1 plate%s, locked/final/) are real and share one room. K2 is the real spinner '
                    'layer of that plate (rendered on its own from the locked generator) scaled over the dimming room: COMP. K3-K5 carry the '
                    'option A bits FX recoloured to the new palette: concept (drawn glyphs and keylines over real board layers). K3-K5 are '
                    'rendered at 960 px and enlarged.' % ('' if corp == 'neutral' else ', Solace skin'))
    base['chg'] = ('2026-11-02: every frame now shows the final locked board (O-29 fix pass) instead of the E10 design plate. The board is split '
                   'into its real layers: the spinner (player) flies in as a sprite; the enemy rings, the frame band and the W4-W6 tickets are '
                   'drawn by option A glyph streams in the corp skin colours%s; the THIS TURN band keyline is the neutral silver tape; the guns '
                   'arm in player pink at the lock; the WPAP cards deal with a glyph trail in their type colour (TOWER cobalt, WAVE orange, '
                   'Trace violet). K2 is sampled at 0.38 s (at 0.25 s the spinner is still transparent). Timing unchanged.'
                   % (' (Solace lime, leaf and teal greens, porcelain)' if corp == 'solace' else ' (neutral steel greys)'))
    T[tid] = base

FR['t06'] = [plate['neutral'], key('neutral', 't6', .2), key('neutral', 't6', .4), street(cleared=0), tear_of(plate['neutral']), fail_screen()]
KIND['t06'] = 'RXXCXX'
T['t06']['labels'] = ['K1  0.00 s  combat ends (final locked board, p1 plate)', 'K2  0.20 s  cards shed glyphs, the frame band and ring 2 go',
                      'K3  0.40 s  pink keyline eats the spinner; spot-ink glyphs drain', 'K4  0.80 s  back on the netrun street, room cleared',
                      'K5  0.20 s  FAIL branch: signal glitch, the board tears', 'K6  0.60 s  FAIL: netrun-failure screen (concept)']
T['t06']['real'] = ('K1 is the real final locked plate (a decide-beat plate stands in for the won state; no won-state plate exists). K2-K3 are the '
                    'option A bits FX recoloured, over the real board layers and the real v3.1 room: concept (rendered at 960 px, enlarged). '
                    'K4 is the r6 street with mock tags (COMP). The glitch tear (K5, now on the final plate) and the failure screen (K6, unchanged) are concept.')
T['t06']['chg'] = ('2026-11-02: K1-K3 and K5 now use the final locked board. The win path is option A recoloured: the hand breaks into glyphs '
                   'in the WPAP type colours, the keyline eats the frame band (silver tape), rings 2, 1, 0 (corp colours), then the spinner with a '
                   'player-pink keyline whose glyphs take the slice spot inks. K4 and K6 are the v3 frames. Timing unchanged.')

COL = {'R': LIME, 'C': (70, 200, 255), 'X': AMB}
TAG = {'R': 'REAL', 'C': 'COMP', 'X': 'CONCEPT'}
TAGW = {'R': 84, 'C': 84, 'X': 126}
ORDER = ['t02', 't03', 't05', 't05s', 't06']
TT = []
for tid in ORDER:
    t = T[tid]
    ims = FR[tid]
    assert len(ims) == len(t['labels']) == len(KIND[tid]), tid
    t['keys'] = [(lb, stamp(im) if k == 'X' else im, k) for lb, im, k in zip(t['labels'], ims, KIND[tid])]
    TT.append(t)


def strip(tr, cols=3):
    n = len(tr['keys']); rows = math.ceil(n / cols)
    tw, th, g, lab, mx = 616, 347, 24, 36, 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA PATH', tr['cam']), ('UI HAND-OVER', tr['ui']),
              ('REDUCED MOTION', tr['rm']), ('REAL VS CONCEPT', tr['real']), ('CHANGE', tr['chg']), ('FEEL', tr['feel'])]
    f, fb = F(19), F(19, True)
    lines = [(h, textwrap.wrap(x, 150) or ['']) for h, x in blocks]
    th_text = sum(len(w) for _, w in lines) * 25 + len(lines) * 33 + 20
    top = 70
    Wd = mx * 2 + cols * tw + (cols - 1) * g
    S = Image.new('RGB', (Wd, top + rows * (th + lab + g) + th_text + 20), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((mx, 18), tr['title'][:105], font=F(32, True), fill=LIME)
    for i, (lb, im, kind) in enumerate(tr['keys']):
        r, c = divmod(i, cols)
        x = mx + c * (tw + g); y = top + r * (th + lab + g)
        S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x - 2, y - 2, x + tw + 1, y + th + 1), outline=COL[kind], width=3)
        d.rectangle((x, y, x + TAGW[kind], y + 26), fill=COL[kind])
        d.text((x + 6, y + 3), TAG[kind], font=F(18, True), fill=(10, 10, 10))
        d.text((x, y + th + 6), lb[:80], font=F(17, True), fill=(235, 235, 240))
        if c < cols - 1 and i < n - 1:
            d.polygon([(x + tw + 4, y + th // 2 - 14), (x + tw + 20, y + th // 2), (x + tw + 4, y + th // 2 + 14)], fill=LIME)
    y = top + rows * (th + lab + g) + 8
    for h, wr in lines:
        d.text((mx, y), h, font=fb, fill=AMB); y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222)); y += 25
        y += 8
    return S


def sheet():
    tw, th, g, lw, mx = 300, 169, 8, 300, 20
    cols = max(len(t['keys']) for t in TT)
    rowh = th + 26 + g
    S = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 70 + len(TT) * rowh + 30), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((mx, 14), 'REBEL_CELL transitions T2 / T3 / T5 / T6 on the final locked combat board (green real, cyan composite, amber concept)', font=F(24, True), fill=LIME)
    for r, t in enumerate(TT):
        y = 64 + r * rowh
        for k, w in enumerate(textwrap.wrap(t['title'], 30)[:5]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 120), textwrap.wrap(t['dur'], 32)[0], font=F(15), fill=LIME)
        for i, (lb, im, kind) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=COL[kind], width=3)
            d.rectangle((x, y, x + TAGW[kind] - 20, y + 20), fill=COL[kind])
            d.text((x + 4, y + 2), TAG[kind], font=F(14, True), fill=(10, 10, 10))
            d.text((x, y + th + 4), lb[:44], font=F(12), fill=(200, 200, 208))
    d.text((mx, S.height - 26), 'T2 and T3 contain no combat board (unchanged v3 frames). T5 is shown on the neutral skin and on Solace. K3-K5 of T5 and K2-K3 of T6 are option A recoloured (concept).', font=F(15), fill=(200, 200, 208))
    return S


if __name__ == '__main__':
    for t in TT:
        strip(t).save(OUT + t['file'], quality=90)
        print('wrote', t['file'])
    sheet().save(OUT + 'sheet.jpg', quality=88)
    print('ok')
