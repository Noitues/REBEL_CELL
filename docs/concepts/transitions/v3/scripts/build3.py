"""Transitions storyboard v3. Writes only to transitions/v3/. Compositing only (PIL, numpy). No Godot or Blender.
Run: python build3.py   (re-run after any change to combat_e10_design/final: it re-copies the plates)."""
import os, sys, math, random, shutil, hashlib, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers3 import *
from text3 import TEXT, STILL, LOG

OUT = R + 'transitions/v3/'
os.makedirs(OUT + 'plates', exist_ok=True)

# ---- re-copy the E10 design plates (a fix pass may update them) ----
E10D = R + 'combat_e10_design/final/'
stamp_lines = []
for n in ['p1_decide', 'p1_decide_srv', 'p1_decide_gh', 'p1_nowords', 'p3_resolve']:
    shutil.copy2(E10D + n + '.png', OUT + 'plates/' + n + '.png')
    stamp_lines.append('%s %s' % (n, hashlib.md5(open(E10D + n + '.png', 'rb').read()).hexdigest()[:10]))
open(OUT + 'plates/PLATES.txt', 'w').write('copied from combat_e10_design/final at build time:\n' + '\n'.join(stamp_lines) + '\n')

# ---- sources ----
MP = 'cohesion/map_pages_r42/'
TR = 'tide_raid/G1_parity/final_proposed/'
ZR4 = 'netrun_cel/zoom_rules/round4/zoom_motion.gif'
FLK = 'netrun_cel/zoom_rules/round7/street_band_flicker_4s_12fps.gif'
s1 = L('netrun_cel/godot_zoom/stage_1_base.png')
route = L(MP + 'route_page.png'); hqs = L(MP + 'hq_node_selected.png'); rsetup = L(MP + 'raid_setup.png')
rb = {n: L(TR + n + '_side_by_side.png', half=True) for n in ['01_plan', '03_reveal', '04_impact', '06_aftermath', '07_city_lost']}
city = rb['01_plan']
hl = L('netrun_cel/zoom_rules/round7b/candB/stage_1_layers.png')
street_raw = L('netrun_cel/zoom_rules/round6/street_frame.png')
room = {n: L('combat_backdrop/v3_1/room_%s_bare.png' % n) for n in ['bio', 'event', 'shop']}
bare = room['bio']
e10 = L('combat_e10_design/final/p1_decide.png')
ev = L('solace_vertical/nodes/godot/frames/now_event.png')
hero = L('netrun_cel/hq_set/round3/hero.png')
fly = [L('netrun_cel/hq_set/round3/fly_in/f_fly_%02d.png' % i) for i in range(8)]
helixc = L('netrun_cel/hq_set/round3/alt_helix_closeup.png')
winB = L('solace_endscreens/v2/win_B.png'); loseB = L('solace_endscreens/v2/lose_B.png')
RN = (.60, .40); NET = (.34, .58); HQN = (.78, .30)


def gf(i): return GIF(ZR4, i)
def zi(t, dur): return int(round(min(max(t / dur, 0), 1) * 74))
def zr(t, dur): return 74 - zi(t, dur)           # reversed track


ROOMS = [(.378, 'FIGHT'), (.592, 'EVENT'), (.823, 'SHOP')]


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
    if sel is not None:
        x = ROOMS[sel][0] * W
        d.rectangle((x - 90, 694, x + 90, 868), outline=(255, 255, 255), width=8)
        d.rectangle((x - 94, 690, x + 94, 872), outline=(255, 46, 158), width=3)
    return im


def event_card(rm):
    r = dark(rm, .6)
    card = ev.crop((int(.01 * W), int(.1 * H), int(.8 * W), int(.62 * H))).resize((int(W * .5), int(H * .29)), Image.LANCZOS)
    r.paste(card, (int(W * .05), int(H * .66)))
    return r


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


# ---- E10 wheel layer on the cutaway ----
def wheel_mask():
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse((12, 12, 1062, 1068), fill=255); d.rounded_rectangle((18, 958, 240, 1062), 14, fill=255)
    return m.filter(ImageFilter.GaussianBlur(2))


WL = e10.convert('RGBA'); WL.putalpha(wheel_mask())
WC = (535, 540)


def with_wheel(bg, s=1.0, a=1.0):
    out = bg.convert('RGBA')
    t = WL.resize((int(W * s), int(H * s)), Image.LANCZOS)
    t.putalpha(t.split()[3].point(lambda v: int(v * a)))
    out.alpha_composite(t, (int(WC[0] - WC[0] * s), int(WC[1] - WC[1] * s)))
    return out.convert('RGB')


dim_room = dark(bare, .55)
board_bare = with_wheel(dim_room)

HX = (840, 20, 1200, 760)
def hero_cyan(sw): return to_cyan(zc(hero, .5, .45, 1.0 + .04 * sw), sw, HX)


def hq_chrome(base):
    out = base.copy()
    out.paste(hqs.crop((1180, 440, 1920, 760)), (1180, 300))
    out.paste(hqs.crop((1500, 900, 1920, 1080)), (1500, 900))
    return out


FR = {
    't01': [s1, zblur(zc(s1, .55, .5, 1.25), .04), blend(zc(s1, .55, .5, 1.5), city, .6), city],
    't02': [marker(city.copy(), *NET, 'before'), None, None,
            blend(dark(marker(city.copy(), *NET, 'before'), .75), hl, .5), hl],
    't03': [hl] + [glow_line(gf(zi(t, 1.4)), p) for t, p in (
        (.3, [(.2, .9), (.4, .6), (.6, .5)]), (.65, [(.1, .95), (.35, .7), (.6, .55), (.8, .4)]),
        (.95, [(.05, .98), (.4, .88), (.7, .8)]), (1.2, [(.02, .96), (.4, .9), (.8, .88)]))] + [street(), GIF(FLK, 24)],
    't04': [street(), street(0), zblur(zc(street(0), ROOMS[0][0], .73, 3.0), .05),
            iris(zblur(zc(street(0), ROOMS[0][0], .73, 3.4), .05), scan(bare), .22),
            bare, room['event'], room['shop'], event_card(room['event'])],
    't05': [bare, with_wheel(dark(bare, .8), 1.35, .7), bits_to(board_bare, (.76, .60), (.27, .52), seed=1),
            bits_ring(board_bare, (.279, .5), 480), blend(bits_ring(board_bare, (.279, .5), 480, n=160), e10, .6), e10],
    't06': [e10, bits_dissolve(e10, .45), bits_dissolve(bare, .75), street(cleared=0), None, fail_screen()],
    't07': [street(), glow_line(gf(zr(.3, 1.2)), [(.05, .98), (.4, .88), (.7, .8)]), gf(zr(.6, 1.2)), hl,
            marker(city.copy(), *RN, 'before'), marker(city.copy(), *RN, 'win'), marker(city.copy(), *RN, 'lose')],
    't08': [rb['07_city_lost'], desat(dark(rb['07_city_lost'], .5), .5),
            shrink_on(dark(rb['07_city_lost'], .35), loseB, .78, .5, .5, rot=-2), loseB],
    't09': [city, blend(zc(city, .5, .5, 1.15), rsetup, .45), rsetup, zc(rsetup, .72, .72, 1.6), blend(city, rsetup, .35), city],
    't10': [city, rb['03_reveal'], rb['04_impact'], rb['06_aftermath'], rb['07_city_lost'], marker(city.copy(), *RN, 'win')],
    't11': [marker(city.copy(), *HQN, 'before'), blend(zblur(zc(city, .79, .30, 1.8), .05), fly[0], .55),
            fly[1], fly[3], fly[5], fly[7], hq_chrome(hero)],
    't12': [hqs, blend(hqs, hero, .6), hero_cyan(.5),
            blend(to_cyan(helixc), Image.new('RGB', (W, H), (255, 255, 255)), .7),
            shrink_on(dark(hero_cyan(1.0), .4), winB, .78, .5, .5, rot=-2), winB],
}
# t02 K2/K3 and t06 K5 need composition
card = hqs.crop((1180, 440, 1920, 760)); btn = hqs.crop((1500, 900, 1920, 1080))
k2 = FR['t02'][0].copy(); k2.paste(card, (1160, 380))
k3 = k2.copy(); k3.paste(btn, (1500, 900)); k3 = Image.blend(k3, Image.new('RGB', (W, H), (255, 255, 255)), .35)
FR['t02'][1], FR['t02'][2] = k2, k3
tear = e10.copy(); rr = random.Random(8)
for _ in range(20):
    y = rr.randrange(0, H - 40); h_ = rr.randrange(10, 50)
    tear.paste(tear.crop((0, y, W, y + h_)), (rr.randrange(-90, 90), y))
FR['t06'][4] = Image.blend(tear, Image.new('RGB', (W, H), (80, 0, 50)), .25)

KIND = {'t01': 'RCCR', 't02': 'CCCCR', 't03': 'RCCCCCR', 't04': 'CCCCRRRC', 't05': 'RCXXXR', 't06': 'RXXCXX',
        't07': 'CCRRCCC', 't08': 'RCCR', 't09': 'RCRCCR', 't10': 'RRRRRC', 't11': 'CCRRRRC', 't12': 'RCXXCR'}

T = []
for t in TEXT:
    ims = FR[t['id']]
    labs = t['labels']
    assert len(ims) == len(labs) == len(KIND[t['id']]), t['id']
    keys = []
    for lb, im, k in zip(labs, ims, KIND[t['id']]):
        keys.append((lb, stamp(im) if k == 'X' else im, k))
    t = dict(t); t['keys'] = keys
    T.append(t)

COL = {'R': LIME, 'C': (70, 200, 255), 'X': AMB}
TAG = {'R': 'REAL', 'C': 'COMP', 'X': 'CONCEPT'}
TAGW = {'R': 84, 'C': 84, 'X': 126}


def strip(tr, cols=3):
    n = len(tr['keys']); rows = math.ceil(n / cols)
    tw, th, g, lab, mx = 616, 347, 24, 36, 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA PATH', tr['cam']), ('UI HAND-OVER', tr['ui']),
              ('REDUCED MOTION', tr['rm']), ('REAL VS CONCEPT', tr['real']), ('CHANGE VS V2', tr['chg']), ('FEEL', tr['feel'])]
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


def grid_h(n, cols=3):
    return 70 + math.ceil(n / cols) * (347 + 36 + 24)


def flow():
    S = Image.new('RGB', (2200, 1270), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((40, 20), 'Transition flow v3: how the 12 connect (numbers are T1 to T12)', font=F(40, True), fill=LIME)
    B = {}

    def box(k, x, y, label, col=(60, 70, 90), w=300, h=84):
        B[k] = (x, y, w, h)
        d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(26, 30, 40), outline=col, width=4)
        for j, t in enumerate(label.split('\n')):
            d.text((x + 14, y + 12 + j * 28), t, font=F(24, True), fill=(235, 235, 240))

    box('grid', 40, 520, 'CITY GRID'); box('raid', 480, 520, 'RAID VIEW\n(main campaign city)', LIME, h=100)
    box('plan', 480, 140, 'RAID SETUP\n(planning)'); box('run', 480, 900, 'RAID RUN\nthen RESULT')
    box('lost', 480, 1060, 'DOSSIER (LOSE)\nslot B, campaign over', PINK, w=420, h=84)
    box('jack', 960, 520, 'NETRUN STREET\n(r6 render, jack-in lands)', LIME, w=360, h=100)
    box('room', 1400, 330, 'ROOM CUTAWAY\nv3.1: combat / event / shop', LIME, w=420)
    box('combat', 1800, 470, 'COMBAT\nE10 design plate', LIME, w=330)
    box('fail', 1400, 720, 'NETRUN FAILURE\nterminal (CONCEPT)', PINK)
    box('hq', 960, 140, 'HQ NETRUN\n(authored set, real fly-in)', LIME, w=380)
    box('win', 1400, 60, 'DOSSIER (WIN)\nslot B, campaign won', LIME, w=420)

    def arrow(a, b, n, col=LIME, off=(0, 0), side=('r', 'l')):
        def pt(k, s):
            x, y, w, h = B[k]
            return {'l': (x, y + h / 2), 'r': (x + w, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[s]
        p, q = pt(a, side[0]), pt(b, side[1])
        p = (p[0] + off[0], p[1] + off[1]); q = (q[0] + off[0], q[1] + off[1])
        d.line((p, q), fill=col, width=5)
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        d.polygon([q, (q[0] - 20 * math.cos(ang - .4), q[1] - 20 * math.sin(ang - .4)), (q[0] - 20 * math.cos(ang + .4), q[1] - 20 * math.sin(ang + .4))], fill=col)
        mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        d.ellipse((mx_ - 20, my_ - 20, mx_ + 20, my_ + 20), fill=col)
        d.text((mx_ - (13 if n > 9 else 6), my_ - 13), str(n), font=F(22, True), fill=(10, 10, 10))

    arrow('grid', 'raid', 1); arrow('raid', 'jack', 2, off=(0, -20)); arrow('raid', 'jack', 3, off=(0, 20))
    arrow('jack', 'room', 4); arrow('room', 'combat', 5, side=('b', 't'), off=(120, 0))
    arrow('combat', 'jack', 6, AMB, side=('b', 'r')); arrow('jack', 'fail', 6, PINK, side=('b', 'l'))
    arrow('fail', 'raid', 7, PINK, side=('l', 'b')); arrow('jack', 'raid', 7, LIME, off=(0, 60), side=('l', 'r'))
    arrow('raid', 'lost', 8, PINK, side=('b', 't')); arrow('raid', 'plan', 9, side=('t', 'b'))
    arrow('raid', 'run', 10, side=('b', 't'), off=(60, 0)); arrow('raid', 'hq', 11, AMB, side=('t', 'l')); arrow('hq', 'win', 12)
    d.text((40, 1200), 'Lime border = real render at both ends; pink = loss branch; amber arrow = special path (combat return, HQ). 2 and 3 share the Raid view to street leg; 6 and 7 branch on result; 9, 10 and 7 return to the raid view. Only the failure screen is still concept.', font=F(21), fill=(215, 215, 222))
    return S


def sheet():
    tw, th, g, lw, mx = 230, 130, 8, 300, 20
    cols = max(len(t['keys']) for t in T)
    rowh = th + 24 + g
    S = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 64 + len(T) * rowh), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((mx, 14), "REBEL_CELL transitions v3 (green = real render, cyan = composite of real renders, amber = concept)", font=F(26, True), fill=LIME)
    for r, t in enumerate(T):
        y = 64 + r * rowh
        for k, w in enumerate(textwrap.wrap(t['title'], 30)[:4]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), textwrap.wrap(t['dur'], 32)[0], font=F(15), fill=LIME)
        for i, (lb, im, kind) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=COL[kind], width=3)
            d.text((x, y + th + 3), lb[:40], font=F(12), fill=(200, 200, 208))
    return S


V2N = {'t01': 4, 't02': 4, 't03': 6, 't04': 6, 't05': 6, 't06': 6, 't07': 6, 't08': 4, 't09': 6, 't10': 6, 't11': 6, 't12': 5}


def v2_vs_v3():
    V2 = R + 'transitions/v2/'
    sc = .42
    gw = int(1968 * sc)
    rows = []
    for t in T:
        a = Image.open(V2 + t['file']).convert('RGB')
        a = a.crop((0, 0, a.width, grid_h(V2N[t['id']])))
        b = strip(t); b = b.crop((0, 0, b.width, grid_h(len(t['keys']))))
        rows.append((t, a, b))
    tot = 90 + sum(int(max(a.height, b.height) * sc) + 40 for _, a, b in rows)
    S = Image.new('RGB', (gw * 2 + 90, tot), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((30, 18), 'v2 (left) vs v3 (right), per transition. v3 frames: green real, cyan composite, amber concept. v2: green real, amber mock.', font=F(26, True), fill=LIME)
    y = 70
    for t, a, b in rows:
        d.text((30, y), t['title'][:110], font=F(20, True), fill=AMB)
        y += 30
        A = a.resize((gw, int(a.height * sc)), Image.LANCZOS); B_ = b.resize((gw, int(b.height * sc)), Image.LANCZOS)
        S.paste(A, (30, y)); S.paste(B_, (gw + 60, y))
        y += max(A.height, B_.height) + 10
    return S.crop((0, 0, S.width, y + 10))


def md():
    o = ["# Transitions storyboard v3 (art-pass, 2026-11-01): the designer's 12, on real renders (choices logged as O-23)\n",
         "Replaces v2 where a new real render exists; v2 (`../v2/`) stays as a record. Built by `scripts/build3.py` (with `helpers3.py`, `text3.py`) from existing renders and labelled composites. No Godot or Blender run; no game design. Structure, timings, easings, hand-overs and the ten v2 assumptions are kept; each change is in the transition's **Change vs v2** line and in the log at the end.\n",
         "Every key carries a badge and a frame colour:",
         "- **REAL** (green): an existing render or an existing crop of one, nothing added.",
         "- **COMP** (cyan): real renders, composed here (crop, blend, iris, mock route ribbon and room tags, node markers, pasted r42 chrome). Shows sequence and timing; the pictures under it are real.",
         "- **CONCEPT** (amber, CONCEPT stamped on the frame): invented FX or a screen with no render yet (bits streams, bits dissolve, glitch tear, the helix colour sweep and flash, the netrun-failure screen).\n",
         "- `flow.jpg`: how the 12 connect. `sheet.jpg`: all strips on one page. `v2_vs_v3.jpg`: v2 and v3 key frames per transition. `plates/`: the E10 plates as copied at build time (`PLATES.txt` has their hashes).\n",
         "## Master timing table\n", "| # | Transition | Duration | Easing | Reduced motion |", "|---|---|---|---|---|"]
    for t in T:
        o.append('| %s | %s | %s | %s | 0.25 s cross-fade |' % (t['id'].upper(), t['title'][4:], t['dur'], t['ease']))
    o += ['', 'No timing changed from v2. The v2 consistency rules stand: T3 is 1.4 s and T1 a lighter 1.2 s; entering a room (T4) is 0.8 s and leaving it (T6) 0.8 s; every UI card or folder slides in 0.3 to 0.5 s with a 60 to 80 ms stagger; no chrome is on screen while the camera moves; every reduced-motion variant is a 0.25 s cross-fade (under the 0.3 s cap).\n',
          '![flow](flow.jpg)\n']
    for t in T:
        o += ['## %s\n' % t['title'], '![%s](%s)\n' % (t['id'], t['file']),
              '- **Keys:** ' + '; '.join('%s [%s]' % (k[0].strip(), TAG[k[2]].lower()) for k in t['keys']),
              '- **Real vs concept:** ' + t['real'], '- **Change vs v2:** ' + t['chg'],
              '- **Duration:** ' + t['dur'], '- **Easing:** ' + t['ease'], '- **Camera path:** ' + t['cam'],
              '- **UI hand-over:** ' + t['ui'], '- **Reduced motion:** ' + t['rm'], '- **Feel:** ' + t['feel'], '']
    o += STILL + LOG
    return '\n'.join(o)


for t in T:
    strip(t).save(OUT + t['file'], quality=90)
sheet().save(OUT + 'sheet.jpg', quality=88)
flow().save(OUT + 'flow.jpg', quality=90)
v2_vs_v3().save(OUT + 'v2_vs_v3.jpg', quality=84)
open(OUT + 'STORYBOARD.md', 'w', encoding='utf-8').write(md())
print('ok')
