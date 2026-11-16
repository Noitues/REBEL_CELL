"""Transitions storyboard v4: Campaign B (build's B-100 list). DRAFT for the designer.
Writes only to transitions/v4/. Compositing only (PIL, numpy). No Godot, no Blender.
Run from anywhere:  python <repo>/docs/concepts/transitions/v4/scripts/build4.py
Method and layout follow v3 (../v3/scripts/build3.py)."""
import os, sys, math, random, hashlib, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers4 import *
from text4 import TEXT, STILL, CALLS, OPEN, LOG

OUT = R + 'transitions/v4/'
os.makedirs(OUT + 'plates', exist_ok=True)

# ---------------- sources ----------------
SRC = {
    'map': 'cohesion/map_pages_r42/hq_idle.png',
    'ov8': 'netrun_cel/zoom_rules/staged_run/run8_city_overview_highlight.png',
    'ov10': 'netrun_cel/zoom_rules/staged_run/run10_city_overview_highlight.png',
    'r8L0': 'netrun_cel/zoom_rules/staged_run/run8_first_L0.png',
    'r8L7': 'netrun_cel/zoom_rules/staged_run/run8_last_L7.png',
    'r10L0': 'netrun_cel/zoom_rules/staged_run/run10_first_L0.png',
    'pickB': 'netrun_cel/street_b/street_branch_B_next.png',
    'zr4': 'netrun_cel/zoom_rules/round4/zoom_motion.gif',
    'bio': 'combat_backdrop/v3_1/room_bio_bare.png', 'event': 'combat_backdrop/v3_1/room_event_bare.png',
    'shop': 'combat_backdrop/v3_1/room_shop_bare.png', 'srv': 'combat_backdrop/v3_1/room_srv_bare.png',
    'board': 'takeover_board/v3/v3_board.png', 'win': 'takeover_board/v3/v3_win.png',
    'fail': 'transitions/netrun_fail/A_crt_feed.png',
    'r3plan': 'raid_v3/r3_plan.png', 'r3place': 'raid_v3/r3_place.png', 'r3shop': 'raid_v3/r3_shop.png',
    'r3play': 'raid_v3/r3_playback.png', 'r3site': 'raid_v3/r3_site.png', 'r3aft': 'raid_v3/r3_aftermath.png',
    'r8plan': 'raid_v3/set8/r8_plan.png', 'r8place': 'raid_v3/set8/r8_place.png', 'r8play': 'raid_v3/set8/r8_playback.png',
    'room': 'round42_hq_room/hq_room.png', 'act': 'round42_hq_room/hq_actions.png',
    'loseB': 'solace_endscreens/v2/lose_B.png', 'winB': 'solace_endscreens/v2/win_B.png',
}
CAP_SCRATCH = 'D:/rc_scratch/raid_v3/city_hi/city_albedo_hi.png'
CAP_LOCAL = OUT + 'plates/raid_city_capture.jpg'
if not os.path.exists(CAP_LOCAL):
    Image.open(CAP_SCRATCH).convert('RGB').resize((W, H), Image.LANCZOS).save(CAP_LOCAL, quality=92)
lines = ['sources read at build time (md5 prefix):']
for k, v in SRC.items():
    lines.append('%-8s %s %s' % (k, hashlib.md5(open(R + v, 'rb').read()).hexdigest()[:10], v))
lines.append('%-8s %s %s (1920 px copy of %s)' % ('raidcap', hashlib.md5(open(CAP_LOCAL, 'rb').read()).hexdigest()[:10],
                                                  'transitions/v4/plates/raid_city_capture.jpg', CAP_SCRATCH))
open(OUT + 'plates/PLATES.txt', 'w').write('\n'.join(lines) + '\n')

S = {k: L(v) for k, v in SRC.items() if k not in ('zr4', 'pickB')}
S['pickB'] = Lc(SRC['pickB'], (0, 0, 1920, 1080))
S['cap'] = L(CAP_LOCAL)
MAP, OV8, OV10, CAP = S['map'], S['ov8'], S['ov10'], S['cap']


def gf(i): return GIF(SRC['zr4'], i)


# map page points (hq_idle, px)
SITE = (1130, 390); LINK = ((930, 548), (1122, 402)); HEART = (838, 782)
JACK = (1585, 915, 1850, 1020); HEATBOX = (18, 12, 356, 88); CREWBTN = (18, 846, 218, 982); DEFBTN = (18, 988, 218, 1054)
# pick B plate
ROOMB = (870, 745); YOU = (480, 745)
# HQ room deck CRT
CRT = (335, 585, 660, 820)


def heat_roll(im, val, col=(255, 70, 60)):
    out = flash_box(im, HEATBOX, .25); d = ImageDraw.Draw(out)
    d.rectangle((24, 22, 100, 84), fill=(20, 8, 10)); d.text((26, 24), str(val), font=F(52, True), fill=col)
    d.rectangle(HEATBOX, outline=col, width=4)
    return chip(out, (370, 96), 'HEAT %d CROSSED' % val, col, 40)


# ---------------- T1 ----------------
def term(base, title, rows, col=CYAN, box=(420, 300, 1500, 760)):
    out = dark(base, .45)
    return terminal_panel(out, box, title, rows, col=col)


jack_rows = [('> jack --from CULTURE_INTAKE --to SEED_VAULT', None, 30), ('  routing ........ 4 hops', None, 26),
             ('  handshake ...... ok', None, 26), ('', None, 16), ('CONNECTED', LIME, 56)]
mapjack = flash_box(MAP, JACK, .55)


def reveal(im, x_front, seed=4):
    """walls dissolve to bits left to right: rooms band behind the front opens dark, bits at the front."""
    out = im.copy(); d = ImageDraw.Draw(out); r = random.Random(seed); f = MF(20)
    band = (560, 870)
    op = Image.new('L', (W, H), 0)
    ImageDraw.Draw(op).rectangle((0, band[0], x_front - 90, band[1]), fill=150)
    out = Image.composite(dark(out, .45), out, op.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(out)
    for gy in range(band[0], band[1], 22):
        for gx in range(max(0, x_front - 420), x_front + 40, 15):
            p = 1 - abs(gx - (x_front - 170)) / 240
            if r.random() < max(0, p) * .95:
                c = (255, 255, 255) if gx > x_front - 30 else r.choice([(255, 210, 150), (200, 160, 255), (120, 230, 255)])
                d.text((gx, gy), r.choice('01'), font=f, fill=c)
    return glow_line(out, [(0, .78), (.12, .77), (.25, .70), (x_front / W - .12, .70)], col=(212, 255, 0), w=7)


T01 = [MAP, term(MAP, '> TERMINAL // CELL-9', jack_rows),
       rain_link(dark(MAP, .55), *LINK), crt_collapse(dark(MAP, .55), .7),
       OV8, zblur(zc(OV8, .5, .5, 2.2), .05), gf(50), S['r8L0'], reveal(S['r8L0'], 900), S['pickB']]

# ---------------- T2 ----------------
def pulse(im, k):
    pts = [(YOU[0] / W, YOU[1] / H), ((YOU[0] + (ROOMB[0] - YOU[0]) * k) / W, ROOMB[1] / H)]
    return glow_line(im, pts, col=(212, 255, 0), w=6)


pb = S['pickB']
k2 = pulse(pb, .7)
k3 = zblur(zc(ring_hi(pulse(pb, 1.0), (796, 700, 945, 790), (212, 255, 0), 7), ROOMB[0] / W, ROOMB[1] / H, 2.5), .05)
k4 = iris(zc(pulse(pb, 1.0), ROOMB[0] / W, ROOMB[1] / H, 3.0), scan(S['bio']), .2)
T02 = [pb, k2, k3, k4, S['bio'], S['event'], S['shop'], S['srv']]

# ---------------- T3 ----------------
B = S['board']; WC = (960, 545)


def mask_circle(r, feather=2):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((WC[0] - r, WC[1] - r, WC[0] + r, WC[1] + r), fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))


def mask_rects(rects):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for b in rects:
        d.rectangle(b, fill=255)
    return m


def layer(base, src, m, a=1.0):
    return Image.composite(src, base, m.point(lambda v: int(v * a)))


droom = dark(S['bio'], .55)
GLASS = mask_circle(470)
hubring = Image.new('L', (W, H), 0)
ImageDraw.Draw(hubring).ellipse((WC[0] - 470, WC[1] - 470, WC[0] + 470, WC[1] + 470), fill=255)
ImageDraw.Draw(hubring).ellipse((WC[0] - 395, WC[1] - 395, WC[0] + 395, WC[1] + 395), fill=0)
glass_only = Image.blend(droom, Image.new('RGB', (W, H), (16, 20, 28)), .55)
k2 = layer(droom, glass_only, GLASS, .9); k2 = layer(k2, B, hubring, .85)
k3 = bits_to(layer(k2, B, GLASS, .25), (.80, .62), (.62, .30), n=260, col=(40, 205, 190), seed=3)
k3 = bits_ring(k3, (.5, .505), 400, n=330, col=(40, 205, 190), seed=5, rings=1)
LEFT = mask_rects([(0, 150, 560, 800), (18, 815, 525, 945)])
# keep only the stickers and chips, not the board plate's dark backdrop behind them
_lum = B.convert('L').point(lambda v: 255 if v > 48 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
LEFT = Image.fromarray((np.asarray(LEFT).astype(np.uint16) * np.asarray(_lum) // 255).astype('uint8'))
k4 = layer(droom, B, GLASS); k4 = layer(k4, B, LEFT)
HUD = mask_rects([(0, 0, 520, 150), (1395, 0, 1920, 790), (1620, 790, 1920, 960)])
k5 = layer(k4, B, HUD)
T03 = [S['bio'], k2, k3, k4, k5, B]

# ---------------- T4 ----------------
def tear(im, seed=8, n=20):
    out = im.copy(); rr = random.Random(seed)
    for _ in range(n):
        y = rr.randrange(0, H - 40); h_ = rr.randrange(10, 50)
        out.paste(out.crop((0, y, W, y + h_)), (rr.randrange(-90, 90), y))
    return out


street_won = marker(pb.copy(), ROOMB[0] / W, ROOMB[1] / H, 'win')
fb = tear(B); d_ = ImageDraw.Draw(fb); d_.rectangle((400, 22, 505, 66), fill=(30, 6, 10)); d_.text((405, 24), '0/30', font=F(40, True), fill=(255, 60, 60))
T04 = [S['win'], bits_dissolve(S['win'], .45), bits_dissolve(dark(S['bio'], .7), .7), street_won, fb, S['fail']]

# ---------------- T5 ----------------
def bits_band(im, x0, x1, k, seed=6):
    out = im.copy(); d = ImageDraw.Draw(out); r = random.Random(seed); f = MF(20)
    for gy in range(560, 870, 22):
        for gx in range(x0, x1, 15):
            if r.random() < k:
                d.text((gx, gy), r.choice('01'), font=f, fill=r.choice([(255, 255, 255), (255, 200, 140), (180, 150, 255)]))
    return out


rack = marker(S['r8L7'].copy(), .5, .66, 'win')
rack_out = dark(zc(S['r8L7'], .5, .62, 1.25), .8)
adv = dark(MAP, .4)
for i, (nm, tier, rw) in enumerate([('T2 // NEUTRAL GROUND', 'T2', '+12 Schematics'), ('T2 // GENE LOCKER', 'T2', '+10, firmware'),
                                    ('T3 // ROOT ARCHIVE', 'T3', '+20, Heat +3')]):
    x = 150 + i * 560
    terminal_panel(adv, (x, 330, x + 520, 700), '> ADVANCE // OPENS', [(nm, None, 28), ('', None, 12), ('tier   ' + tier, None, 24),
                                                                     ('reward ' + rw, None, 24), ('', None, 12), ('[ PICK ]', LIME, 28)])
T05 = [zc(rack, .5, .62, 1.25), dark(S['r8L7'], .85), bits_band(S['r8L7'], 1000, 1920, .45), S['r8L7'], gf(18), OV8,
       crt_collapse(dark(MAP, .6), .45),
       term(MAP, '> TERMINAL // CELL-9', [('> jack --out', None, 30), ('  DISCONNECTED', None, 30), ('', None, 12),
                                          ('banked: +14 Schematics, 2 cards', LIME, 28)]),
       marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'win'), adv]

# ---------------- T6 ----------------
order = S['r3place'].crop((1495, 5, 1915, 560))
fold = S['r3plan'].crop((1520, 8, 1910, 195))


def with_order(base, s=1.25):
    out = base.copy(); o = order.resize((int(order.width * s), int(order.height * s)), Image.LANCZOS).rotate(-2, expand=True, fillcolor=(0, 0, 0))
    m = Image.new('L', o.size, 0); ImageDraw.Draw(m).rectangle((6, 6, o.width - 6, o.height - 6), fill=255)
    m = m.rotate(0)
    out.paste(o, ((W - o.width) // 2, (H - o.height) // 2 - 10), order.resize((int(order.width * s), int(order.height * s))).convert('L').point(lambda v: 255).rotate(-2, expand=True))
    return out


alert = banner(tint(heat_roll(MAP, 50), (120, 0, 10), .12), 'RAID INCOMING', 'SOLACE // Heat 50 crossed // work order intercepted')
k4 = dark(MAP, .85).copy(); k4.paste(fold, (W - fold.width - 12, 110))
T06 = [heat_roll(MAP, 50), alert, with_order(dark(alert, .55)), k4,
       blend(zblur(zc(MAP, .55, .5, 1.6), .04), CAP, .55), iso_grid(CAP, a=.5, w=3), S['r3plan']]

# ---------------- T7 ----------------
T07 = [ring_hi(MAP, DEFBTN, PINK, 7), blend(zc(MAP, .5, .5, 1.3), iso_grid(CAP), .5), S['r3plan'], S['r3place'], S['r8place'],
       S['r3shop'], S['r3site'], blend(dark(S['r3plan'], .7), MAP, .45), MAP]

# ---------------- T8 ----------------
lost = desat(S['r3aft'], .55); dl = ImageDraw.Draw(lost)
st = Image.new('RGBA', (420, 170), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
ds.rounded_rectangle((6, 6, 414, 164), 18, fill=(200, 20, 30, 235), outline=(255, 255, 255, 255), width=8)
ds.text((210, 85), 'LOST', font=F(120, True), fill=(255, 255, 255, 255), anchor='mm')
st = st.rotate(-6, expand=True, resample=Image.BICUBIC)
lost = lost.convert('RGBA'); lost.alpha_composite(st, (880, 680)); lost = lost.convert('RGB')
held_map = chip(marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'win'), (HEART[0] + 40, HEART[1] - 30), 'HQ 44/50', LIME)
lost_map = chip(marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'lose'), (HEART[0] + 40, HEART[1] - 30), 'HQ 44 > 41', (255, 70, 60))
T08 = [flash_box(S['r3plan'], (1670, 640, 1870, 780), .55), S['r3play'], S['r8play'], S['r3aft'], lost, held_map, lost_map]

# ---------------- T9 ----------------
room_map = paste_fit(S['room'], MAP, CRT)
CX, CY = (CRT[0] + CRT[2]) / 2 / W, (CRT[1] + CRT[3]) / 2 / H
act = S['act']
recruit = act.crop((972, 22, 1898, 528)).resize((W, H), Image.LANCZOS)
crew = act.crop((22, 552, 948, 1058)).resize((W, H), Image.LANCZOS)
tal = terminal_panel(dark(S['room'], .4), (430, 220, 1490, 820), '> TALENTS // CELL-9 (BREAKER)', [
    ('[ ] overclock      +1 RAM at turn 1', None, 28), ('[x] cold boot      first program free', LIME, 28),
    ('[ ] deep cover     -1 Heat per street', None, 28), ('', None, 14), ('points 1   (concept: no screen exists)', AMB, 26)], col=CYAN)
T09 = [ring_hi(MAP, CREWBTN, LIME, 7), zc(room_map, CX, CY, 1.9), S['room'], recruit, crew, tal, zc(room_map, CX, CY, 2.0), MAP]

# ---------------- T10 ----------------
purge = banner(tint(heat_roll(MAP, 100), (150, 0, 10), .18), 'PURGE', 'SOLACE // Heat 100 // all operatives recalled to HQ')
rec = purge
for i, (p, col) in enumerate([((650, 510), (255, 140, 60)), ((1110, 650), (92, 160, 255)), ((1250, 715), (80, 230, 120)), ((1280, 470), (180, 120, 255))]):
    rec = streak(rec, p, (HEART[0] + 10 * i - 15, HEART[1] - 8), col)
wall = S['room'].crop((0, 320, 430, 650)).resize((860, 660), Image.LANCZOS)
dw = ImageDraw.Draw(wall)
for (x, y) in [(60, 150), (300, 150), (560, 150), (60, 470), (300, 470), (560, 470)]:
    dw.rectangle((x, y, x + 230, y + 50), fill=(150, 10, 20)); dw.text((x + 12, y + 6), 'RECALLED', font=MF(34), fill=(255, 230, 230))
k4 = dark(rec, .5).copy(); k4.paste(wall, (530, 210)); ImageDraw.Draw(k4).rectangle((530, 210, 1390, 870), outline=(232, 20, 30), width=6)
T10 = [heat_roll(MAP, 100), purge, rec, k4, blend(zblur(zc(MAP, HEART[0] / W, HEART[1] / H, 1.7), .04), iso_grid(CAP), .5), S['r8plan']]

# ---------------- T11 ----------------
k1 = S['r8plan'].copy(); d1 = ImageDraw.Draw(k1)
d1.line((30, 18, 400, 80), fill=(235, 30, 40), width=9); d1.line((30, 80, 400, 18), fill=(235, 30, 40), width=9)
d1.text((420, 4), '0', font=F(80, True), fill=(235, 30, 40))
k2 = tint(desat(dark(k1, .5), .5), (120, 10, 60), .2)
T11 = [k1, k2, shrink_on(dark(k1, .35), S['loseB'], .78, .5, .5, rot=-2), S['loseB']]

# ---------------- T12 ----------------
HQB = (120, 70, 1560, 880)
def hqc(sw):
    """warm (the Meridian landmark's orange) to Cell cyan, sweeping up from the bottom of HQB (concept FX)."""
    im = zc(S['r10L0'], .5, .45, 1.0 + .04 * sw)
    a = np.asarray(im).astype(np.float32); r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
    x0, y0, x1, y1 = HQB; yy, xx = np.mgrid[0:H, 0:W]
    sel = (r_ - b_ > 18) & (r_ > 60) & (xx >= x0) & (xx <= x1) & (yy <= y1) & (yy >= y1 - sw * (y1 - y0))
    out = a.copy()
    out[..., 0] = np.where(sel, r_ * .3, r_); out[..., 1] = np.where(sel, np.maximum(g_, r_ * .95), g_)
    out[..., 2] = np.where(sel, np.maximum(b_, r_ * 1.05), b_)
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))
t3m = chip(marker(MAP.copy(), 1265 / W, 390 / H, 'win'), (1180, 130), 'TIER 3: 3 / 3', LIME)
T12 = [t3m, OV10, zblur(zc(OV10, .6, .32, 2.2), .05), S['r10L0'], hqc(.55),
       blend(hqc(1.0), Image.new('RGB', (W, H), (255, 255, 255)), .7),
       shrink_on(dark(hqc(1.0), .4), S['winB'], .78, .5, .5, rot=-2), S['winB']]

FR = {'t01': T01, 't02': T02, 't03': T03, 't04': T04, 't05': T05, 't06': T06, 't07': T07, 't08': T08,
      't09': T09, 't10': T10, 't11': T11, 't12': T12}
# R real, r real from a DRAFT set, C composite of real renders, X concept
KIND = {'t01': 'RCXXrCRrXR', 't02': 'RCCCRRRR', 't03': 'RCXCCR', 't04': 'RXXCXX', 't05': 'CCXrRrXCCX',
        't06': 'CXCCCCR', 't07': 'CCRRrRRCR', 't08': 'CRrRXCC', 't09': 'CCRRRXCR', 't10': 'CXXCCr',
        't11': 'CCCR', 't12': 'CrCrXXCR'}

T = []
for t in TEXT:
    ims, labs, kd = FR[t['id']], t['labels'], KIND[t['id']]
    assert len(ims) == len(labs) == len(kd), (t['id'], len(ims), len(labs), len(kd))
    t = dict(t); t['keys'] = [(lb, stamp(im) if k == 'X' else im, k) for lb, im, k in zip(labs, ims, kd)]
    T.append(t)

COL = {'R': LIME, 'r': LIME, 'C': (70, 200, 255), 'X': AMB}
TAG = {'R': 'REAL', 'r': 'REAL  DRAFT', 'C': 'COMP', 'X': 'CONCEPT'}
TAGW = {'R': 84, 'r': 150, 'C': 84, 'X': 126}


def badge(d, x, y, kind, s=1.0):
    w = int(TAGW[kind] * s); h = int(26 * s)
    d.rectangle((x, y, x + w, y + h), fill=COL[kind])
    d.text((x + int(6 * s), y + int(3 * s)), TAG[kind], font=F(int(18 * s), True), fill=(10, 10, 10))
    if kind == 'r':
        d.rectangle((x + int(64 * s), y, x + w, y + h), fill=AMB)
        d.text((x + int(70 * s), y + int(3 * s)), 'DRAFT', font=F(int(18 * s), True), fill=(10, 10, 10))


def strip(tr, cols=3):
    n = len(tr['keys']); rows = math.ceil(n / cols)
    tw, th, g, lab, mx = 616, 347, 24, 36, 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA PATH', tr['cam']), ('UI HAND-OVER', tr['ui']),
              ('REDUCED MOTION', tr['rm']), ('REAL VS CONCEPT', tr['real']), ('CHANGE VS V3', tr['chg']), ('FEEL', tr['feel'])]
    f, fb = F(19), F(19, True)
    lines = [(h, textwrap.wrap(x, 150) or ['']) for h, x in blocks]
    th_text = sum(len(w) for _, w in lines) * 25 + len(lines) * 33 + 20
    top = 70
    Wd = mx * 2 + cols * tw + (cols - 1) * g
    S_ = Image.new('RGB', (Wd, top + rows * (th + lab + g) + th_text + 20), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 18), tr['title'][:110], font=F(30, True), fill=LIME)
    d.text((Wd - mx - 250, 20), 'DRAFT  v4  Campaign B', font=F(24, True), fill=AMB)
    for i, (lb, im, kind) in enumerate(tr['keys']):
        r, c = divmod(i, cols)
        x = mx + c * (tw + g); y = top + r * (th + lab + g)
        S_.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x - 2, y - 2, x + tw + 1, y + th + 1), outline=COL[kind] if kind != 'r' else AMB, width=3)
        badge(d, x, y, kind)
        d.text((x, y + th + 6), lb[:78], font=F(17, True), fill=(235, 235, 240))
        if c < cols - 1 and i < n - 1:
            d.polygon([(x + tw + 4, y + th // 2 - 14), (x + tw + 20, y + th // 2), (x + tw + 4, y + th // 2 + 14)], fill=LIME)
    y = top + rows * (th + lab + g) + 8
    for h, wr in lines:
        d.text((mx, y), h, font=fb, fill=AMB); y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222)); y += 25
        y += 8
    return S_


def grid_h(n, cols=3):
    return 70 + math.ceil(n / cols) * (347 + 36 + 24)


def flow():
    S_ = Image.new('RGB', (2300, 1330), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((40, 20), 'Transition flow v4 (DRAFT): Campaign B, how the 12 connect (numbers are T1 to T12)', font=F(40, True), fill=LIME)
    B_ = {}

    def box(k, x, y, label, col=(60, 70, 90), w=360, h=92):
        B_[k] = (x, y, w, h)
        d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(26, 30, 40), outline=col, width=4)
        for j, t in enumerate(label.split('\n')):
            d.text((x + 14, y + 12 + j * 28), t, font=F(23 if j else 24, j == 0), fill=(235, 235, 240) if j == 0 else (190, 195, 205))

    box('map', 760, 560, 'CITY MAP\nsites, Heat, CREW / MARKET / DEFENCE', LIME, w=420, h=100)
    box('street', 1330, 560, 'NETRUN STREET\nstaged run, pick B next room', LIME, w=400)
    box('room', 1330, 300, 'ROOM\nv3.1 cutaway by node kind', LIME, w=400)
    box('fight', 1860, 300, 'FIGHT\nDeface v3 board', LIME, w=380)
    box('fail', 1860, 700, 'NETRUN FAILURE\noperative lost (CONCEPT)', PINK, w=380)
    box('hq', 120, 560, 'HQ WORKSHOP\nrecruit, weapons, talents', AMB, w=380)
    box('alert', 120, 880, 'RAID ALERT\nwork order INCOMING', (232, 20, 30), w=380)
    box('plan', 760, 880, 'RAID PLANNING\nposts, dock, shop, evacuate', LIME, w=420)
    box('run', 1330, 880, 'RAID PLAYS\nthen RESULT (held / lost)', LIME, w=400)
    box('purge', 120, 1110, 'PURGE RECALL\nHeat 100, crew to HQ', (232, 20, 30), w=380)
    box('lose', 760, 1180, 'DOSSIER (LOSE)\nHQ integrity 0', PINK, w=420)
    box('hqnet', 760, 200, 'HQ NETRUN\nfly-in, 10 layers, BLOCK SERVER', AMB, w=420)
    box('win', 1330, 90, 'DOSSIER (WIN)\nslot B, campaign won', LIME, w=400)

    def pt(k, s):
        x, y, w, h = B_[k]
        return {'l': (x, y + h / 2), 'r': (x + w, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[s]

    def arrow(a, b, n, col=LIME, off=(0, 0), side=('r', 'l'), off2=None):
        p, q = pt(a, side[0]), pt(b, side[1])
        o2 = off2 if off2 is not None else off
        p = (p[0] + off[0], p[1] + off[1]); q = (q[0] + o2[0], q[1] + o2[1])
        d.line((p, q), fill=col, width=5)
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        d.polygon([q, (q[0] - 22 * math.cos(ang - .4), q[1] - 22 * math.sin(ang - .4)), (q[0] - 22 * math.cos(ang + .4), q[1] - 22 * math.sin(ang + .4))], fill=col)
        if n:
            mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            d.ellipse((mx_ - 21, my_ - 21, mx_ + 21, my_ + 21), fill=col)
            d.text((mx_ - (13 if n > 9 else 6), my_ - 13), str(n), font=F(22, True), fill=(10, 10, 10))

    arrow('map', 'street', 1, off=(0, -22)); arrow('street', 'map', 5, off=(0, 22), side=('l', 'r'))
    arrow('street', 'room', 2, side=('t', 'b')); arrow('room', 'fight', 3)
    arrow('fight', 'street', 4, AMB, side=('b', 'r'), off=(-80, 0), off2=(0, 0)); arrow('fight', 'fail', 4, PINK, side=('b', 't'), off=(80, 0), off2=(80, 0))
    arrow('fail', 'map', None, PINK, side=('b', 'b'), off=(0, 0), off2=(120, 0))
    arrow('map', 'alert', 6, (232, 20, 30), side=('b', 't'), off=(-140, 0), off2=(0, 0)); arrow('alert', 'plan', None, (232, 20, 30))
    arrow('map', 'plan', 7, side=('b', 't'), off=(-30, 0)); arrow('plan', 'map', None, side=('t', 'b'), off=(60, 0))
    arrow('plan', 'run', 8); arrow('run', 'map', 8, side=('t', 'r'), off2=(0, 30))
    arrow('map', 'hq', 9, AMB, off=(0, -22), side=('l', 'r')); arrow('hq', 'map', None, AMB, off=(0, 22))
    arrow('map', 'purge', 10, (232, 20, 30), side=('l', 't'), off=(0, 40), off2=(60, 0)); arrow('purge', 'plan', None, (232, 20, 30), side=('r', 'b'))
    arrow('run', 'lose', 11, PINK, side=('b', 'r'))
    arrow('map', 'hqnet', 12, AMB, side=('t', 'b')); arrow('hqnet', 'win', 12, AMB)
    d.text((40, 1295), 'Lime box = approved or real render at that screen; amber = special path (HQ workshop, HQ netrun); red = Heat-driven raid entry; pink = loss. 4 branches on the fight result; 7, 8 and 9 return to the map; 10 opens the PURGE raid planning.', font=F(20), fill=(215, 215, 222))
    return S_


def sheet():
    tw, th, g, lw, mx = 230, 130, 8, 300, 20
    cols = max(len(t['keys']) for t in T)
    rowh = th + 24 + g
    S_ = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 64 + len(T) * rowh), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 14), "REBEL_CELL transitions v4, Campaign B (DRAFT). Green = real render, green+amber = real from a DRAFT set, cyan = composite of real renders, amber = concept", font=F(24, True), fill=LIME)
    for r, t in enumerate(T):
        y = 64 + r * rowh
        for k, w in enumerate(textwrap.wrap(t['title'], 30)[:4]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), textwrap.wrap(t['dur'], 34)[0], font=F(14), fill=LIME)
        for i, (lb, im, kind) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S_.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=COL[kind] if kind != 'r' else AMB, width=3)
            badge(d, x, y, kind, .6)
            d.text((x, y + th + 3), lb[:40], font=F(12), fill=(200, 200, 208))
    return S_


V3N = {'t01': 4, 't02': 5, 't03': 7, 't04': 8, 't05': 6, 't06': 6, 't07': 7, 't08': 4, 't09': 6, 't10': 6, 't11': 7, 't12': 6}
V3F = {'t01': 't01_city_to_raid_view.jpg', 't02': 't02_raid_to_select_jackin.jpg', 't03': 't03_jackin_zoom.jpg', 't04': 't04_street_to_room.jpg',
       't05': 't05_room_to_combat.jpg', 't06': 't06_combat_to_netrun_or_fail.jpg', 't07': 't07_netrun_to_raid_view.jpg',
       't08': 't08_raid_lose_to_dossier.jpg', 't09': 't09_raid_to_plan_and_back.jpg', 't10': 't10_raid_start_result_back.jpg',
       't11': 't11_raid_to_hq_netrun.jpg', 't12': 't12_hq_to_win_dossier.jpg'}


def v3_vs_v4():
    V3 = R + 'transitions/v3/'
    sc = .40
    gw = int(1968 * sc)
    rows = []
    for t in TEXT:
        tt = [x for x in T if x['id'] == t['id']][0]
        b = strip(tt); b = b.crop((0, 0, b.width, grid_h(len(tt['keys']))))
        if t['v3']:
            a = Image.open(V3 + V3F[t['v3']]).convert('RGB'); a = a.crop((0, 0, a.width, grid_h(V3N[t['v3']])))
        else:
            a = Image.new('RGB', (1968, 500), (22, 24, 30)); da = ImageDraw.Draw(a)
            da.text((60, 200), 'NEW in v4: no v3 counterpart', font=F(70, True), fill=AMB)
        rows.append((tt, a, b))
    tot = 90 + sum(int(max(a.height, b.height) * sc) + 44 for _, a, b in rows)
    S_ = Image.new('RGB', (gw * 2 + 90, tot), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((30, 18), 'v3 (left, nearest v3 transition) vs v4 Campaign B (right, DRAFT)', font=F(26, True), fill=LIME)
    y = 70
    for t, a, b in rows:
        d.text((30, y), ('v3: ' + t['v3name'])[:70], font=F(19, True), fill=(180, 185, 195))
        d.text((gw + 60, y), t['title'][:80], font=F(19, True), fill=AMB)
        y += 32
        A = a.resize((gw, int(a.height * sc)), Image.LANCZOS); B2 = b.resize((gw, int(b.height * sc)), Image.LANCZOS)
        S_.paste(A, (30, y)); S_.paste(B2, (gw + 60, y))
        y += max(A.height, B2.height) + 12
    return S_.crop((0, 0, S_.width, y + 10))


SOURCES = ['## Sources (current, approved or latest; read only)\n',
           '- **City map page:** `cohesion/map_pages_r42/hq_idle.png` (r42, Solace; site dossier, JACK IN, CREW / MARKET / DEFENCE).',
           '- **Netrun street, Campaign B:** staged run (B-103 option 1, DRAFT) `netrun_cel/zoom_rules/staged_run/` run8_* (site street, 8 layers) and run10_* (HQ street, 10 layers), city overviews with the highlight; pick B plate `netrun_cel/street_b/street_branch_B_next.png` (designer pick 2026-11-15, "keep the web"); round 4 zoom track `netrun_cel/zoom_rules/round4/zoom_motion.gif` as the dive stand-in.',
           '- **Rooms:** `combat_backdrop/v3_1/room_{bio,event,shop,srv}_bare.png`.',
           '- **Fight:** Deface v3, approved (A-119): `takeover_board/v3/v3_board.png`, `v3_win.png`. Port captures (`v3/port_check/`) were checked; they are placeholder-styled, so the plates are used.',
           '- **Netrun failure:** `transitions/netrun_fail/A_crt_feed.png` (design A, art\'s recommendation).',
           '- **Raid:** set 7 (approved, direction C) `raid_v3/r3_{plan,place,shop,playback,site,aftermath}.png`; set 8 (DRAFT, v40 dock rules) `raid_v3/set8/r8_{plan,place,playback}.png`; the raw raid city capture `D:/rc_scratch/raid_v3/city_hi/city_albedo_hi.png` (copied to `plates/`).',
           '- **HQ:** `round42_hq_room/hq_room.png`, `hq_actions.png`. **End screens:** `solace_endscreens/v2/{win,lose}_B.png`.',
           '- **Timings reused, not invented:** bible 4.6 netrun entry lock (terminal 1.40, rain 1.25, CRT collapse 0.45, dive 3.0, REVEAL 3.64, MARK 1.0 + 0.8, ZOOM 1.0 + 0.5; jack-out reversed); DECISIONS ANIM (route_pulse 0.4 s, node_pop 0.25 s BACK, visited_dim 0.3 s, jack_in / jack_out 0.8 s IN_OUT CUBIC at 2.6x about the deck CRT, panel_in 0.22 s, panel_drop 0.22 s); ZOOM_RULES 5.5 (path, along-route dolly 0.6 s, rate cap); TAKEOVER_PORT_SPEC (slap, Dissolve A, reduce effects); raid NOTES (Tab unfold, drag spring lag; no motion times exist there); v3 for everything else.', '']


def md():
    o = ['# Transitions storyboard v4: Campaign B (DRAFT for the designer\'s morning review, 2026-11-16)\n',
         '**DRAFT.** Build\'s B-100 list (from ART CALL 49) storyboarded on the current Campaign B frames. Concept plates only (PIL compositing of existing renders); no Godot or Blender run, no game code. v3 (`../v3/`) stays as the record. Same method and structure as v3; each change is in the transition\'s **Change vs v3** line.\n',
         'Every key carries a badge and a frame colour:',
         '- **REAL** (green): an existing render or plate, or a crop of one, nothing added. **REAL DRAFT** (green + amber): the same, from a set still in DRAFT (staged run, raid set 8).',
         '- **COMP** (cyan): real renders composed here (crop, blend, iris, pulse, markers, pasted panels). Shows sequence and timing; the pictures under it are real.',
         '- **CONCEPT** (amber, CONCEPT stamped): invented FX or a screen with no render yet.\n',
         '- `flow.jpg`: how the 12 connect. `sheet.jpg`: all strips on one page. `v3_vs_v4.jpg`: each v4 transition beside its nearest v3 one. `plates/PLATES.txt`: sources and hashes.\n']
    o += SOURCES
    o += ['## Master timing table\n', '| # | Transition | Duration | Easing | Reduced motion |', '|---|---|---|---|---|']
    for t in T:
        o.append('| %s | %s | %s | %s | 0.25 s cross-fade |' % (t['id'].upper(), t['title'][4:].strip(), t['dur'], t['ease']))
    o += ['', 'Consistency rules kept from v3: entering a room (T2) is 0.8 s and leaving it (T4) 0.8 s; every UI card or folder slides in 0.22-0.5 s with a 60-80 ms stagger; no chrome is on screen while the camera moves; every reduced-motion variant is a 0.25 s cross-fade (under the 0.3 s cap). Changed for Campaign B: the jack-in and jack-out follow the locked bible 4.6 chain (about 13 s, one press skips) instead of v3\'s 1.4 s and 1.2 s.\n',
          '![flow](flow.jpg)\n']
    for t in T:
        o += ['## %s\n' % t['title'], '![%s](%s)\n' % (t['id'], t['file']),
              '- **Keys:** ' + '; '.join('%s [%s]' % (k[0].strip(), TAG[k[2]].lower().replace('  ', ' ')) for k in t['keys']),
              '- **Duration:** ' + t['dur'], '- **Easing:** ' + t['ease'], '- **Camera path:** ' + t['cam'],
              '- **UI hand-over:** ' + t['ui'], '- **Reduced motion:** ' + t['rm'], '- **Feel:** ' + t['feel'],
              '- **Real vs concept:** ' + t['real'], '- **Change vs v3:** ' + t['chg'], '']
    o += STILL + CALLS + OPEN + LOG
    return '\n'.join(o)


for t in T:
    strip(t).save(OUT + t['file'], quality=90)
sheet().save(OUT + 'sheet.jpg', quality=88)
flow().save(OUT + 'flow.jpg', quality=90)
v3_vs_v4().save(OUT + 'v3_vs_v4.jpg', quality=84)
open(OUT + 'STORYBOARD.md', 'w', encoding='utf-8').write(md())
print('ok')
