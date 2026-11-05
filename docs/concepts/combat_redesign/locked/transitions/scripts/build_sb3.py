"""build_sb3 (2026-11-04 round 2; first written for the rebuild): storyboard strips T2, T3, T5 (neutral + Solace) and T6 on the round-2
board, and sheet.jpg.  Round 2 (C13): T6 holds on the room (the T4-reverse pull-out breaks the tile flash limit in every variant tried), so
T6 K4 is T6's own end frame, the bare room (REAL); the v3 street composite is no longer a T6 key.
Reads the v3 storyboard helpers and text read-only (transitions/v3/scripts), the T5 / T6 keys from out/<corp>/keys (1920x1080, rendered
from the generator by render3.py), and the netrun-failure generator read-only (transitions/netrun_fail/scripts: build_A, nf_trans).
Badges: REAL = an existing render used as it is; RENDER = a frame rendered by a generator from the board generator's own layers (this
folder's render3.py, or the netrun_fail glitch-in on the published plate); COMP = real renders composed with mock tags.  No frame is
CONCEPT.  Writes sb/ (publish3.py copies to the repo)."""
import os, sys, math, textwrap, copy
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/v3/scripts')
import helpers3 as H3
from helpers3 import F, LIME, AMB, R as ROOT, GIF, glow_line, marker, blend, dark, L
from text3 import TEXT
import numpy as np
from PIL import Image, ImageDraw
import sbkit as SB
W, H = H3.W, H3.H
WK = 'D:/rc_scratch/combat_redesign/locked/round2/transitions/'
OUT = WK + 'sb/'
os.makedirs(OUT, exist_ok=True)
FIN = ROOT + 'combat_redesign/locked/final/'
plate = {'neutral': Image.open(FIN + 'p1_decide.png').convert('RGB'), 'solace': Image.open(FIN + 'p1_decide_solace.png').convert('RGB')}


def key(corp, which, t):
    return Image.open(WK + 'out/%s/keys/%s_%03d.png' % (corp, which, int(round(t * 100)))).convert('RGB')


# ---- T2 / T3: the v3 frames (no combat board in either)
MP = 'cohesion/map_pages_r42/'
TR = 'tide_raid/G1_parity/final_proposed/'
ZR4 = 'netrun_cel/zoom_rules/round4/zoom_motion.gif'
FLK = 'netrun_cel/zoom_rules/round7/street_band_flicker_4s_12fps.gif'
hqs = L(MP + 'hq_node_selected.png')
city = L(TR + '01_plan_side_by_side.png', half=True)
hl = L('netrun_cel/zoom_rules/round7b/candB/stage_1_layers.png')
NET = (.34, .58)
def gf(i): return GIF(ZR4, i)
def zi(t, dur): return int(round(min(max(t / dur, 0), 1) * 74))


T = {t['id']: copy.deepcopy(t) for t in TEXT}
k1 = marker(city.copy(), *NET, 'before')
card = hqs.crop((1180, 440, 1920, 760)); btn = hqs.crop((1500, 900, 1920, 1080))
k2 = k1.copy(); k2.paste(card, (1160, 380))
k3 = k2.copy(); k3.paste(btn, (1500, 900)); k3 = Image.blend(k3, Image.new('RGB', (W, H), (255, 255, 255)), .35)
FR = {}
FR['t02'] = [k1, k2, k3, blend(dark(marker(city.copy(), *NET, 'before'), .75), hl, .5), hl]
FR['t03'] = [hl] + [glow_line(gf(zi(t, 1.4)), p) for t, p in (
    (.3, [(.2, .9), (.4, .6), (.6, .5)]), (.65, [(.1, .95), (.35, .7), (.6, .55), (.8, .4)]),
    (.95, [(.05, .98), (.4, .88), (.7, .8)]), (1.2, [(.02, .96), (.4, .9), (.8, .88)]))] + [SB.street(), GIF(FLK, 24)]
KIND = {'t02': 'CCCCR', 't03': 'RCCCCCR'}
NOTE23 = (' Unchanged in the 2026-11-04 rebuild: T2 and T3 contain no combat board (the wheel-circle zoom was removed in v3), so there is '
          'no board frame to replace; these are the v3 frames, re-rendered on the new sheet from the v3 sources.')
for k in ('t02', 't03'):
    T[k]['chg'] = T[k]['chg'] + NOTE23

# ---- T5 (neutral, Solace) on the rebuilt board: every key rendered from the generator (render3.py) at 1920x1080
for corp, tid in (('neutral', 't05'), ('solace', 't05s')):
    nm = '' if corp == 'neutral' else ' (Solace skin)'
    FR[tid] = [key(corp, 't5', 0.0), key(corp, 't5', .38), key(corp, 't5', .55), key(corp, 't5', .85), key(corp, 't5', 1.12), key(corp, 't5', 1.2)]
    KIND[tid] = 'RGGGGR'
    base = copy.deepcopy(T['t05'])
    base['id'] = tid
    base['title'] = 'T5  Room to combat: the spinner flies in, the enemy rings fly from the room as bits' + nm
    base['cam'] = ('Fixed iso camera on the room; the camera does not move. The only motion is the spinner (scale 1.35 to 1.0, slight spin '
                   'settle) and the bit streams, which leave the lab (the building in the right half, where the enemy lives), come in to '
                   'the rim, go round it and drop radially into the three rings and the frame band, so no bit crosses the wheel face. The '
                   'room is the same v3.1 render in K1 and under K6, dimmed to the plate grade from K2 to the lock.')
    base['ui'] = ('0.00-0.25 s: nothing. 0.25-0.55 s: spinner in. 0.32-1.00 s: bits; the rings build 0.56-0.99 s and lock at 1.00 s with a '
                  '90 ms snap; the guns arm 0.98-1.10 s. 1.05-1.20 s: the top HUD slides in from the top, the nameplate from the left, the '
                  'cards deal from the bottom (30 ms stagger, each with a trail of its own bits), SEND IT and UNDO last. No input until 1.20 s.')
    base['file'] = 't05_room_to_combat%s.jpg' % ('' if corp == 'neutral' else '_solace')
    base['labels'] = ['K1  0.00 s  the room as T4 left it (v3.1 bio, bare)',
                      'K2  0.38 s  the spinner flies in over the room, 1.35x to 1.0x',
                      'K3  0.55 s  bits leave the lab, white-hot, round the rim',
                      'K4  0.85 s  rings NOW to +2 built, the frame band closing',
                      'K5  1.12 s  locked; guns armed, HUD and cards deal in',
                      'K6  1.20 s  combat begins: the published plate p1_decide' + ('_solace' if corp == 'solace' else '')]
    base['real'] = ('K1 is the v3.1 bare room (the last frame of T4) and K6 is the published plate (locked/final/p1_decide%s.png): both REAL. '
                    'K2-K5 are RENDER: frames of transitions/scripts/render3.py at 1920x1080, made of the round-2 board generator\'s own layers '
                    '(corp/src, read-only; the layers recompose the published plate to within 1/255) and the bits FX, whose every bit '
                    'takes the colour of the board pixel it becomes. No frame is enlarged and none is CONCEPT.' % ('' if corp == 'neutral' else '_solace'))
    base['chg'] = ('2026-11-04 round 2: every frame is on the round-2 board (C1-C18 of the re-review). C13: the bits that go more than 90 degrees '
                   'round the rim from the lab (the far side, over the dark city) thin to 50 % at the far point, so no 120 px tile flashes '
                   'more than 2 times in any 1 s. Kept from the rebuild (review 1.7, 3.12): K1 is the room as T4 leaves it, at its own '
                   'level; the room dims to the plate grade from K2 to the lock. The bits are Share Tech Mono 0/1 in the colour of their '
                   'source (ART_BIBLE 1.2), white-hot (HIT_PAPER) for 80 ms, flipping and tumbling; they leave the lab, go round the rim and '
                   'drop radially into their ring, so none crosses the wheel face. Keylines, ghosts and lock take each ring\'s median bit '
                   'colour; the spinner snap and the guns stay player pink. Timing unchanged.')
    T[tid] = base

# ---- T6: the win path rendered from the generator (dissolve, then the T4 iris reversed); the FAIL branch from the netrun_fail generator
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/netrun_fail/scripts')
import build_A as NFA
import nf_trans as NFT
nf_bg, nf_full, _ph = NFA.build()
fail_k5 = NFT.frame(plate['neutral'], nf_bg, nf_full, 0.12)
fail_k6 = NFT.frame(plate['neutral'], nf_bg, nf_full, 0.60)
pub_a = Image.open(ROOT + 'transitions/netrun_fail/A_crt_feed.png').convert('RGB')
K6_VS_PUBLISHED = int(np.abs(np.asarray(fail_k6).astype(int) - np.asarray(pub_a).astype(int)).max())
FR['t06'] = [key('neutral', 't6', 0.0), key('neutral', 't6', .2), key('neutral', 't6', .4), key('neutral', 't6', .8), fail_k5, fail_k6]
KIND['t06'] = 'RGGRGR'
T06_END_VS_ROOM = int(np.abs(np.asarray(FR['t06'][3]).astype(int) - np.asarray(key('neutral', 't5', 0.0)).astype(int)).max())
T['t06']['labels'] = ['K1  0.00 s  combat ends (the published p1 plate)', 'K2  0.20 s  cards shed their bits; frame band and ring +2 go',
                      'K3  0.40 s  pink keyline eats the spinner; bits drain round the rim', 'K4  0.80 s  the room as T4 left it; camera held (C13)',
                      'K5  0.12 s  FAIL branch: the board tears (netrun_fail A glitch-in)', 'K6  0.60 s  FAIL: netrun-failure screen A (O-26)']
T['t06']['cam'] = ('Combat: fixed iso camera; the board dissolves in place over the cutaway and the room comes back to the level T4 left it at. '
                   'Round 2 call (C13): the camera holds on the room. The T4-reverse iris and 3.4x pull-out to the street, composited into '
                   'the 0.8 s, put a 120 px tile at 3 flashes in 1 s in every variant tried (lime, ink and soft iris edge, motion-blurred '
                   'zoom, even with no ring bits), over the limit of 2. Failure (netrun_fail design A): no pull-out; the board tears (row '
                   'offsets, chroma split, never brighter), then a hard cut to the CRT feed of the street with SIGNAL LOST and the run log.')
T['t06']['ui'] = ('0.00-0.20 s: UNDO, SEND IT, the top HUD and the hand fade; each card sheds its own bits; the frame band, rings +2, +1, NOW '
                  'and then the spinner break into bits that go round the rim and drain into the lab. 0.40-0.80 s: the last bits drain and '
                  'the room settles at its T4 level; the camera holds. Failure (nf_trans): the board tears 0.00-0.20 s, hard cut at 0.20 s, '
                  'the panel opens at 0.30 s, input (GRID VIEW [G]) at 0.60 s.')
T['t06']['real'] = ('K1 is the published plate (a decide-beat plate stands in for the won state; no won-state plate exists): REAL. K2 and K3 '
                    'are RENDER frames of render3.py (board layers + bits; t6_A.gif is the same shot). K4 is the last frame of T6, which is '
                    'the v3.1 bare room T4 left (the same image as T5 K1): REAL. K5 is RENDER: the netrun_fail glitch-in generator '
                    '(nf_trans.py, design A) run on the published plate. K6 is design A of the netrun-failure screen '
                    '(transitions/netrun_fail/A_crt_feed.png, the O-26 pick; its numbers are its tagged placeholders): REAL.')
T['t06']['chg'] = ('2026-11-04 round 2: K1-K4 are one rendered shot on the round-2 board. C13: in T6 the board is eaten first, so the whole '
                   'wheel sits over the dark city: every ring, spinner and ticket stream keeps 45 % of its bits up to 90 degrees round the '
                   'rim from the lab and 25 % at the far point (worst tile 3 -> 2 in any 1 s). The camera holds on the room (the T4-reverse '
                   'pull-out could not meet that limit); K4 is now T6\'s own end frame, not the v3 street. Kept: the cards shed bits in '
                   'their own colours, the keyline eats the frame band, rings +2, +1 and NOW, then the spinner (player-pink keyline), every '
                   'bit coloured by its source; FAIL is netrun-failure design A. Timing unchanged.')

COL = {'R': LIME, 'C': (70, 200, 255), 'G': (180, 150, 255)}
TAG = {'R': 'REAL', 'C': 'COMP', 'G': 'RENDER'}
TAGW = {'R': 84, 'C': 84, 'G': 110}
ORDER = ['t02', 't03', 't05', 't05s', 't06']
TT = []
for tid in ORDER:
    t = T[tid]
    ims = FR[tid]
    assert len(ims) == len(t['labels']) == len(KIND[tid]), tid
    assert 'X' not in KIND[tid]
    t['keys'] = [(lb, im, k) for lb, im, k in zip(t['labels'], ims, KIND[tid])]
    TT.append(t)


def strip(tr, cols=3):
    n = len(tr['keys']); rows = math.ceil(n / cols)
    tw, th, g, lab, mx = 616, 347, 24, 36, 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA PATH', tr['cam']), ('UI HAND-OVER', tr['ui']),
              ('REDUCED MOTION', tr['rm']), ('REAL VS RENDER', tr['real']), ('CHANGE', tr['chg']), ('FEEL', tr['feel'])]
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
    for h_, wr in lines:
        d.text((mx, y), h_, font=fb, fill=AMB); y += 25
        for w_ in wr:
            d.text((mx, y), w_, font=f, fill=(215, 215, 222)); y += 25
        y += 8
    return S


def sheet():
    tw, th, g, lw, mx = 300, 169, 8, 300, 20
    cols = max(len(t['keys']) for t in TT)
    rowh = th + 26 + g
    S = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 70 + len(TT) * rowh + 30), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((mx, 14), 'REBEL_CELL transitions T2 / T3 / T5 / T6 on the round-2 combat board (green real, violet render, cyan composite)', font=F(24, True), fill=LIME)
    for r, t in enumerate(TT):
        y = 64 + r * rowh
        for k, w_ in enumerate(textwrap.wrap(t['title'], 30)[:5]):
            d.text((mx, y + 4 + k * 20), w_, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 120), textwrap.wrap(t['dur'], 32)[0], font=F(15), fill=LIME)
        for i, (lb, im, kind) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=COL[kind], width=3)
            d.rectangle((x, y, x + TAGW[kind] - 20, y + 20), fill=COL[kind])
            d.text((x + 4, y + 2), TAG[kind], font=F(14, True), fill=(10, 10, 10))
            d.text((x, y + th + 4), lb[:44], font=F(12), fill=(200, 200, 208))
    d.text((mx, S.height - 26), 'T2 and T3 contain no combat board (v3 frames). T5 is shown on the neutral skin and on Solace. No frame is CONCEPT: every T5 / T6 board key is rendered by render3.py or nf_trans.py from the round-2 board layers; T6 holds on the room (C13).', font=F(15), fill=(200, 200, 208))
    return S


if __name__ == '__main__':
    for t in TT:
        strip(t).save(OUT + t['file'], quality=90)
        print('wrote', t['file'])
    sheet().save(OUT + 'sheet.jpg', quality=88)
    print('fail K6 (nf_trans at 0.60 s) vs netrun_fail/A_crt_feed.png: max diff', K6_VS_PUBLISHED)
    print('T6 K4 (render3 t6 at 0.80 s) vs T5 K1 (the bare room): max diff', T06_END_VS_ROOM)
    badges = {tid: ''.join(KIND[tid]) for tid in ORDER}
    assert all(set(v) <= set('RCG') for v in badges.values()), badges          # REAL / COMP / RENDER only: no CONCEPT badge (review 1.7)
    print('badges', badges)
    print('ok')
