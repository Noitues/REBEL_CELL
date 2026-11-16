"""Transitions storyboard v5: v4 per the designer's rulings (build's B-105, DECISIONS 2026-11-16 "transitions v4 rulings").
Writes only to transitions/v5/. Compositing and 2D drawing only (PIL, numpy). No Godot, no Blender. v4 stays untouched.
Run:  python <repo>/docs/concepts/transitions/v5/scripts/build5.py
Method and layout follow v4 (../v4/scripts/build4.py)."""
import os, sys, math, random, hashlib, textwrap, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers5 import *
from text5 import TEXT, STILL, CALLS, OPEN, LOG, T10_NOTE, V4D
import blocklab5

OUT = R + 'transitions/v5/'
V4 = R + 'transitions/v4/'
for sub in ('plates', 'plates/zoom_to', 'archive'):
    os.makedirs(OUT + sub, exist_ok=True)

# ---------------- sources ----------------
SRC = {
    'map': 'cohesion/map_pages_r42/hq_idle.png',
    'bio': 'combat_backdrop/v3_1/room_bio_bare.png', 'event': 'combat_backdrop/v3_1/room_event_bare.png',
    'shop': 'combat_backdrop/v3_1/room_shop_bare.png', 'srv': 'combat_backdrop/v3_1/room_srv_bare.png',
    'board': 'takeover_board/v3/v3_board.png', 'win': 'takeover_board/v3/v3_win.png',
    'failC': 'transitions/netrun_fail/C_trace_printout.png',
    'r3plan': 'raid_v3/r3_plan.png', 'r3place': 'raid_v3/r3_place.png', 'r3shop': 'raid_v3/r3_shop.png',
    'r3play': 'raid_v3/r3_playback.png', 'r3site': 'raid_v3/r3_site.png', 'r3aft': 'raid_v3/r3_aftermath.png',
    'r8plan': 'raid_v3/set8/r8_plan.png', 'r8place': 'raid_v3/set8/r8_place.png', 'r8play': 'raid_v3/set8/r8_playback.png',
    'loseB': 'solace_endscreens/v2/lose_B.png', 'winB': 'solace_endscreens/v2/win_B.png',
    'cap': 'transitions/v4/plates/raid_city_capture.jpg',
}
# zoom-to-building captures (A-143 lit street v2, the frames of zoom_to_building/zoom_strip.jpg); 1280 px, copied up to 1920
ZT_SRC = 'D:/rc_tmp/claude/zt/final/'
ZT = ['strip_00', 'strip_05', 'dense_008', 'dense_012', 'dense_015', 'dense_019', 'dense_021', 'dense_023', 'final_lot3']
for n in ZT:
    p = OUT + 'plates/zoom_to/%s.jpg' % n
    if not os.path.exists(p):
        Image.open(ZT_SRC + n + '.png').convert('RGB').resize((W, H), Image.LANCZOS).save(p, quality=92)
for n in ('room_block_server', 'room_block_server_beaten'):
    if not os.path.exists(OUT + 'plates/%s.png' % n):
        blocklab5.build(state='live' if n == 'room_block_server' else 'dead').save(OUT + 'plates/%s.png' % n)

lines = ['sources read at build time (md5 prefix):']
for k, v in SRC.items():
    lines.append('%-8s %s %s' % (k, hashlib.md5(open(R + v, 'rb').read()).hexdigest()[:10], v))
for n in ZT:
    lines.append('%-8s %s %s (1920 px copy of %s%s.png)' % ('zt', hashlib.md5(open(OUT + 'plates/zoom_to/%s.jpg' % n, 'rb').read()).hexdigest()[:10],
                                                         'transitions/v5/plates/zoom_to/%s.jpg' % n, ZT_SRC, n))
for n in ('room_block_server', 'room_block_server_beaten'):
    lines.append('%-8s %s transitions/v5/plates/%s.png (drawn by scripts/blocklab5.py over room_bio_bare)' % (
        'blk', hashlib.md5(open(OUT + 'plates/%s.png' % n, 'rb').read()).hexdigest()[:10], n))
open(OUT + 'plates/PLATES.txt', 'w').write('\n'.join(lines) + '\n')

S = {k: L(v) for k, v in SRC.items()}
Z = {n: L(OUT + 'plates/zoom_to/%s.jpg' % n) for n in ZT}
S['blk'] = L(OUT + 'plates/room_block_server.png'); S['blkd'] = L(OUT + 'plates/room_block_server_beaten.png')
MAP, CAP = S['map'], S['cap']
SOL = (61, 255, 139); ACID = (212, 255, 0)

# map page points (hq_idle, px)
SITE = (1130, 390); LINK = ((930, 548), (1122, 402)); HEART = (838, 782)
JACK = (1585, 915, 1850, 1020); HEATBOX = (18, 12, 356, 88); CREWBTN = (18, 846, 218, 982); DEFBTN = (18, 988, 218, 1054)
CARDS = {'CELL-9': (245, 862, 382, 1045), 'NOVA': (390, 882, 527, 1065), 'RIG-4': (540, 878, 677, 1062)}
# capture target marks (ZOOMTO mark px, lit run): city frame
MARK0 = (928, 547)


def heat_roll(im, val, col=(255, 70, 60)):
    out = flash_box(im, HEATBOX, .25); d = ImageDraw.Draw(out)
    d.rectangle((24, 22, 100, 84), fill=(20, 8, 10)); d.text((26, 24), str(val), font=F(52, True), fill=col)
    d.rectangle(HEATBOX, outline=col, width=4)
    return chip(out, (370, 96), 'HEAT %d CROSSED' % val, col, 40)


def term(base, title, rows, col=CYAN, box=(420, 300, 1500, 760)):
    return terminal_panel(dark(base, .45), box, title, rows, col=col)


def target_ring(im, p, col=PINK, r=46):
    out = im.copy(); d = ImageDraw.Draw(out)
    for rr, w in ((r + 22, 3), (r, 6)):
        d.ellipse((p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr), outline=col, width=w)
    d.line((p[0], p[1] - r - 40, p[0], p[1] - r - 6), fill=col, width=5)
    return out


# ---------------- the real street with rooms (zoom-to capture + v3.1 cutaways placed on its frontage) ----------------
STREET = Z['strip_05']
SC = 2
SLOTS = {  # name: (box on the 1920 street, room plate)
    'walked': ((410, 320, 690, 590), 'event'),
    'leaflet': ((862, 632, 1104, 900), 'shop'),
    'ours': ((1150, 632, 1380, 900), 'bio'),
    'chloro': ((1440, 632, 1592, 900), 'srv'),
    'hotel': ((1620, 632, 1792, 900), 'bio'),
}
ORDER = ['walked', 'leaflet', 'ours', 'chloro', 'hotel']
OURS_C = ((1150 + 1380) / 2, (632 + 900) / 2)
# wax link: the walked room down to the street, along the street to ours
LK = [(550, 590), (700, 945), (1265, 920)]
_street2 = STREET.resize((W * SC, H * SC), Image.LANCZOS)


def room_crop(plate, box):
    w, h = box[2] - box[0], box[3] - box[1]
    hc = 400; wc = int(hc * w / h)
    cx, cy = 1495, 590
    return S[plate].crop((cx - wc // 2, cy - hc // 2, cx + wc // 2, cy + hc // 2)).resize((w * SC, h * SC), Image.LANCZOS)


def shutter(d, box, k, rng):
    """walls close: the cutaway front slides shut top to bottom, 0/1 bits on the closing edge (k 0 open .. 1 shut)."""
    if k <= 0:
        return
    x0, y0, x1, y1 = [v * SC for v in box]
    ye = y0 + (y1 - y0) * min(k, 1)
    d.rectangle((x0, y0, x1, ye), fill=(34, 26, 72))
    for yy in range(int(y0) + 22, int(ye), 26):
        d.line((x0, yy, x1, yy), fill=(26, 20, 56), width=3)
    if k >= 1:
        for wx in (x0 + (x1 - x0) * .2, x0 + (x1 - x0) * .6):
            d.rectangle((wx, y0 + 60, wx + 34, y0 + 100), fill=(255, 196, 120))
    else:
        f = MF(26)
        for gx in range(int(x0), int(x1) - 10, 17):
            for j in range(3):
                if rng.random() < .8:
                    d.text((gx, ye - 10 + j * 22 - 20), rng.choice('01'), font=f, fill=(255, 255, 255) if j == 0 else ACID)
    d.rectangle((x0, y0, x1, y1), outline=(90, 70, 160), width=3)


def sticker(d, p, kind):
    x, y = p[0] * SC, p[1] * SC
    col = {'walked': LIME, 'ours': PINK, 'next': AMB, 'idle': (200, 200, 215)}[kind]
    r = 30
    d.ellipse((x - r - 10, y - r - 10, x + r + 10, y + r + 10), outline=col, width=5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(12, 12, 18), outline=(240, 240, 245), width=5)
    if kind == 'walked':
        d.line((x - 15, y, x - 4, y + 13, x + 16, y - 13), fill=LIME, width=8)
    else:
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col)


def scene(close=None, marks=True, pad=False, pulse=None, walked_ok=True, cleared=None, z=1.0, c=(960, 540), seed=4, link=1.0):
    close = close or {}
    rng = random.Random(seed)
    im = _street2.copy()
    for n in ORDER:
        box, plate = SLOTS[n]
        im.paste(room_crop(plate, box), (box[0] * SC, box[1] * SC))
    d = ImageDraw.Draw(im)
    for n in ORDER:
        box, _ = SLOTS[n]
        k = close.get(n, 0)
        if k < 1:
            d.rectangle([v * SC for v in box], outline=(150, 255, 70), width=4)
        shutter(d, box, k, rng)
    if pad:
        box = [v * SC for v in SLOTS['ours'][0]]
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rectangle(box, fill=PINK + (70,), outline=PINK + (255,), width=14)
        im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); d = ImageDraw.Draw(im)
    if marks:
        # wax link: walked room down to the street, along to ours (written on to `link`)
        def lerp(a, b, t):
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        pts = list(LK)
        if link < 1:
            pts = [LK[0], lerp(LK[0], LK[1], min(1, link * 2))] + ([lerp(LK[1], LK[2], link * 2 - 1)] if link > .5 else [])
        g = Image.new('RGB', im.size, (0, 0, 0)); ImageDraw.Draw(g).line([(x * SC, y * SC) for x, y in pts], fill=(212, 255, 0), width=30, joint='curve')
        im = Image.fromarray(np.clip(np.asarray(im).astype(int) + np.asarray(g.filter(ImageFilter.GaussianBlur(16))).astype(int) * .6, 0, 255).astype('uint8'))
        d = ImageDraw.Draw(im)
        d.line([(x * SC, y * SC) for x, y in pts], fill=(212, 255, 0) if pulse is None else (255, 255, 255), width=8, joint='curve')
        if pulse is not None:
            px, py = lerp(LK[1], LK[2], pulse)
            d.ellipse((px * SC - 22, py * SC - 22, px * SC + 22, py * SC + 22), fill=(212, 255, 0), outline=(255, 255, 255), width=4)
        for n in ORDER:
            box, _ = SLOTS[n]
            p = ((box[0] + box[2]) / 2, box[1] + 2)
            kind = 'walked' if n == 'walked' and walked_ok else ('ours' if n == 'ours' and pad else ('next' if n in ('ours', 'leaflet', 'chloro') else 'idle'))
            if cleared == n:
                kind = 'walked'
            sticker(d, p, kind)
    out = im
    w, h = W * SC / z, H * SC / z
    x0 = min(max(c[0] * SC - w / 2, 0), W * SC - w); y0 = min(max(c[1] * SC - h / 2, 0), H * SC - h)
    return out.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)


def bits_front(im, x_front, band=(320, 900), seed=7, cols=((255, 255, 255), (212, 255, 0), (120, 230, 255))):
    out = im.copy(); d = ImageDraw.Draw(out); r = random.Random(seed); f = MF(20)
    for gy in range(band[0], band[1], 22):
        for gx in range(max(0, x_front - 300), x_front + 40, 15):
            p = 1 - abs(gx - (x_front - 120)) / 180
            if r.random() < max(0, p) * .9:
                d.text((gx, gy), r.choice('01'), font=f, fill=cols[0] if gx > x_front - 30 else r.choice(cols[1:]))
    return out


# ---------------- T1 ----------------
jack_rows = [('> jack --from CULTURE_INTAKE --to SEED_VAULT', None, 30), ('  routing ........ 4 hops', None, 26),
             ('  handshake ...... ok', None, 26), ('', None, 16), ('CONNECTED', LIME, 56)]
reveal_open = {'walked': 0, 'leaflet': 0, 'ours': .35, 'chloro': .85, 'hotel': 1}
T01 = [MAP, term(MAP, '> TERMINAL // CELL-9', jack_rows), rain_link(dark(MAP, .55), *LINK), crt_collapse(dark(MAP, .55), .7),
       target_ring(Z['strip_00'], MARK0), Z['dense_008'], Z['dense_015'], Z['dense_023'],
       bits_front(scene(close=reveal_open, marks=True, link=.45), 1330), scene()]

# ---------------- T2 ----------------
def pan_angle(k4):
    """K5: the cutaway pose coming in: the bio plate warped toward street pitch over the zoomed street, motion blurred."""
    q = S['bio'].transform((W, H), Image.QUAD, data=(1240, 260, 1080, 930, 1900, 930, 1760, 260), resample=Image.BICUBIC)
    return zblur(blend(q, k4, .22), .05)


k3_close = {'walked': .5, 'leaflet': .55, 'chloro': .45, 'hotel': .2}
k4_close = {n: 1 for n in ORDER if n != 'ours'}
t2k4 = scene(close=k4_close, pad=True, z=2.6, c=OURS_C)
T02 = [scene(pad=True), scene(pad=True, pulse=.6), scene(close=k3_close, pad=True, z=1.35, c=OURS_C), t2k4, pan_angle(t2k4),
       S['bio'], S['blk'], S['event'], S['shop'], S['srv']]

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


def mask_mul(a, b):
    return Image.fromarray((np.asarray(a).astype(np.uint16) * np.asarray(b) // 255).astype('uint8'))


def sector(f):
    m = Image.new('L', (W, H), 0)
    if f > 0:
        ImageDraw.Draw(m).pieslice((WC[0] - 560, WC[1] - 560, WC[0] + 560, WC[1] + 560), -90, -90 + 360 * f, fill=255)
    return m


def layer(base, src, m, a=1.0):
    return Image.composite(src, base, m.point(lambda v: int(v * a)))


def arc_pt(f, rad=432):
    a = math.radians(-90 + 360 * f)
    return ((WC[0] + math.cos(a) * rad) / W, (WC[1] + math.sin(a) * rad) / H)


def bits_arc(im, f, n=260, seed=5, col=(40, 205, 190)):
    """bits lying on the built part of the rim (0..f), denser at the head."""
    r = random.Random(seed); out = im.copy(); d = ImageDraw.Draw(out); fnt = MF(22)
    for i in range(n):
        t = f * (1 - r.random() ** 2.2)
        a = math.radians(-90 + 360 * t); rr = 432 + r.gauss(0, 14)
        d.text((WC[0] + math.cos(a) * rr - 6, WC[1] + math.sin(a) * rr - 11), r.choice('01'), font=fnt,
               fill=(255, 255, 255) if t > f - .02 else (col if r.random() < .8 else PINK))
    return out


droom = dark(S['bio'], .55)
hubring = Image.new('L', (W, H), 0)
ImageDraw.Draw(hubring).ellipse((WC[0] - 470, WC[1] - 470, WC[0] + 470, WC[1] + 470), fill=255)
ImageDraw.Draw(hubring).ellipse((WC[0] - 395, WC[1] - 395, WC[0] + 395, WC[1] + 395), fill=0)
GLASS = mask_circle(470)
glass_only = Image.blend(droom, Image.new('RGB', (W, H), (16, 20, 28)), .55)
ROOMP = (.80, .62)
TEAL = (40, 205, 190)


def ring_build(f, glass_a, wedge_a, seed):
    im = layer(droom, glass_only, GLASS, glass_a)
    if wedge_a:
        im = layer(im, B, mask_mul(GLASS, sector(f)), wedge_a)
    im = layer(im, B, mask_mul(hubring, sector(f)), .95)
    im = bits_arc(im, f, n=int(420 * f) + 40, seed=seed)
    for j in range(4):   # streams from the room to the head of the ring and just behind it
        im = bits_to(im, ROOMP, arc_pt(max(0, f - .04 * j)), n=70, col=TEAL, spread=40, seed=seed + j)
    return im


k2 = bits_to(dark(S['bio'], .8), ROOMP, (.70, .30), n=160, col=TEAL, spread=50, seed=2)
LEFT = mask_rects([(0, 150, 560, 800), (18, 815, 525, 945)])
_lum = B.convert('L').point(lambda v: 255 if v > 48 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
LEFT = mask_mul(LEFT, _lum)
k5 = layer(droom, B, GLASS); k5 = layer(k5, B, LEFT)
HUD = mask_rects([(0, 0, 520, 150), (1395, 0, 1920, 790), (1620, 790, 1920, 960)])
T03 = [S['bio'], k2, ring_build(1 / 3, .45, 0, 11), ring_build(2 / 3, .9, .45, 13), k5, layer(k5, B, HUD), B]

# ---------------- T4 ----------------
def tear(im, seed=8, n=20):
    out = im.copy(); rr = random.Random(seed)
    for _ in range(n):
        y = rr.randrange(0, H - 40); h_ = rr.randrange(10, 50)
        out.paste(out.crop((0, y, W, y + h_)), (rr.randrange(-90, 90), y))
    return out


fb = tear(B); d_ = ImageDraw.Draw(fb); d_.rectangle((400, 22, 505, 66), fill=(30, 6, 10)); d_.text((405, 24), '0/30', font=F(40, True), fill=(255, 60, 60))
street_won = scene(cleared='ours')
T04 = [S['win'], bits_dissolve(S['win'], .45), bits_dissolve(dark(S['bio'], .7), .7), street_won, fb, S['failC']]

# ---------------- T5 ----------------
adv = dark(MAP, .4)
for i, (nm, tier, rw) in enumerate([('T2 // NEUTRAL GROUND', 'T2', '+12 Schematics'), ('T2 // GENE LOCKER', 'T2', '+10, firmware'),
                                    ('T3 // ROOT ARCHIVE', 'T3', '+20, Heat +3')]):
    x = 150 + i * 560
    terminal_panel(adv, (x, 330, x + 520, 700), '> ADVANCE // OPENS', [(nm, None, 28), ('', None, 12), ('tier   ' + tier, None, 24),
                                                                     ('reward ' + rw, None, 24), ('', None, 12), ('[ PICK ]', LIME, 28)])
HOTEL_C = ((1620 + 1792) / 2, (632 + 900) / 2)
k1 = scene(cleared='hotel', z=1.3, c=HOTEL_C)
close_rl = {'hotel': 1, 'chloro': 1, 'ours': .6, 'leaflet': .15}
T05 = [k1, dark(scene(marks=False), .8), bits_front(scene(close=close_rl, marks=False), 1500, cols=((255, 255, 255), (255, 200, 140), (180, 150, 255))),
       Z['dense_021'], Z['dense_012'], target_ring(Z['strip_00'], MARK0, LIME), crt_collapse(dark(MAP, .6), .45),
       term(MAP, '> TERMINAL // CELL-9', [('> jack --out', None, 30), ('  DISCONNECTED', None, 30), ('', None, 12),
                                          ('banked: +14 Schematics, 2 cards', LIME, 28)]),
       marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'win'), adv]

# ---------------- T6, T7, T8 (unchanged; frames rebuilt only for sheet.jpg, strips are byte copies of v4) ----------------
order = S['r3place'].crop((1495, 5, 1915, 560))
fold = S['r3plan'].crop((1520, 8, 1910, 195))


def with_order(base, s=1.25):
    out = base.copy(); o = order.resize((int(order.width * s), int(order.height * s)), Image.LANCZOS).rotate(-2, expand=True, fillcolor=(0, 0, 0))
    out.paste(o, ((W - o.width) // 2, (H - o.height) // 2 - 10), order.resize((int(order.width * s), int(order.height * s))).convert('L').point(lambda v: 255).rotate(-2, expand=True))
    return out


alert = banner(tint(heat_roll(MAP, 50), (120, 0, 10), .12), 'RAID INCOMING', 'SOLACE // Heat 50 crossed // work order intercepted')
k4 = dark(MAP, .85).copy(); k4.paste(fold, (W - fold.width - 12, 110))
T06 = [heat_roll(MAP, 50), alert, with_order(dark(alert, .55)), k4,
       blend(zblur(zc(MAP, .55, .5, 1.6), .04), CAP, .55), iso_grid(CAP, a=.5, w=3), S['r3plan']]
T07 = [ring_hi(MAP, DEFBTN, PINK, 7), blend(zc(MAP, .5, .5, 1.3), iso_grid(CAP), .5), S['r3plan'], S['r3place'], S['r8place'],
       S['r3shop'], S['r3site'], blend(dark(S['r3plan'], .7), MAP, .45), MAP]
lost = desat(S['r3aft'], .55)
st = Image.new('RGBA', (420, 170), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
ds.rounded_rectangle((6, 6, 414, 164), 18, fill=(200, 20, 30, 235), outline=(255, 255, 255, 255), width=8)
ds.text((210, 85), 'LOST', font=F(120, True), fill=(255, 255, 255, 255), anchor='mm')
st = st.rotate(-6, expand=True, resample=Image.BICUBIC)
lost = lost.convert('RGBA'); lost.alpha_composite(st, (880, 680)); lost = lost.convert('RGB')
held_map = chip(marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'win'), (HEART[0] + 40, HEART[1] - 30), 'HQ 44/50', LIME)
lost_map = chip(marker(MAP.copy(), SITE[0] / W, SITE[1] / H, 'lose'), (HEART[0] + 40, HEART[1] - 30), 'HQ 44 > 41', (255, 70, 60))
T08 = [flash_box(S['r3plan'], (1670, 640, 1870, 780), .55), S['r3play'], S['r8play'], S['r3aft'], lost, held_map, lost_map]

# ---------------- T9: the workshop as an overlay on the city map ----------------
GLASSC = (5, 13, 28)
PANEL = (400, 150, 1520, 930)


def overlay(base, tab, slide=0, alpha=.93):
    out = base.convert('RGBA')
    x0, y0, x1, y1 = PANEL; y0 += slide; y1 += slide
    ov = Image.new('RGBA', out.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((x0, y0, x1, y1), fill=GLASSC + (int(255 * alpha),), outline=CYAN + (190,), width=4)
    d.text((x0 + 24, y0 + 16), '> WORKSHOP // THE CELL', font=MF(30), fill=CYAN + (255,))
    d.line((x0 + 24, y0 + 62, x1 - 24, y0 + 62), fill=PINK + (255,), width=4)
    for i, tn in enumerate(['RECRUIT', 'WEAPONS', 'TALENTS']):
        tx = x0 + 24 + i * 250
        on = tn == tab
        d.rectangle((tx, y0 + 80, tx + 230, y0 + 130), fill=(LIME + (255,)) if on else (14, 30, 46, 255), outline=CYAN + (200,), width=2)
        d.text((tx + 20, y0 + 90), tn, font=MF(28), fill=(10, 10, 10, 255) if on else (190, 220, 235, 255))
    d.text((x1 - 260, y0 + 92), '[Esc] back to map', font=MF(22), fill=(150, 180, 200, 255))
    out = Image.alpha_composite(out, ov)
    d = ImageDraw.Draw(out); cy = y0 + 160
    if tab == 'RECRUIT':
        for i, (nm, cost) in enumerate([('NOVA', '40 schem.'), ('RIG-4', '55 schem.'), ('CELL-9', 'on crew')]):
            cx = x0 + 40 + i * 350
            card = MAP.crop(CARDS[nm]).resize((274, 366), Image.LANCZOS)
            out.paste(card, (cx, cy))
            d.rectangle((cx, cy + 380, cx + 274, cy + 430), fill=(14, 30, 46), outline=CYAN, width=2)
            d.text((cx + 14, cy + 390), ('HIRE  ' + cost) if cost != 'on crew' else 'ON CREW', font=MF(26), fill=LIME if cost != 'on crew' else (150, 170, 190))
        d.text((x0 + 40, y1 - 110), 'crew 3 / 4   recruits refresh each round', font=MF(26), fill=(190, 220, 235))
    elif tab == 'WEAPONS':
        rows = [('CELL-9', 'SMG ** ', 'SHOTGUN *', '[ empty ]'), ('NOVA', 'PISTOL *', '[ empty ]', '[ empty ]'), ('RIG-4', 'MINE **', 'SMG *', '[ empty ]')]
        for i, row in enumerate(rows):
            yy = cy + i * 200
            out.paste(MAP.crop(CARDS[row[0]]).resize((120, 160), Image.LANCZOS), (x0 + 40, yy))
            for j, wpn in enumerate(row[1:]):
                bx = x0 + 200 + j * 290
                d.rectangle((bx, yy + 30, bx + 270, yy + 130), fill=(14, 30, 46), outline=(AMB if 'empty' not in wpn else (70, 90, 110)), width=3)
                d.text((bx + 16, yy + 62), wpn, font=MF(28), fill=(255, 220, 160) if 'empty' not in wpn else (110, 130, 150))
    else:
        nodes = [(560, 330, 'overclock'), (560, 520, 'cold boot'), (900, 420, 'ghost route'), (900, 640, 'deep cover'), (1240, 520, 'root kit')]
        for (a, b) in ((0, 2), (1, 2), (1, 3), (2, 4), (3, 4)):
            d.line((nodes[a][0], nodes[a][1] + slide, nodes[b][0], nodes[b][1] + slide), fill=(90, 120, 150), width=4)
        for i, (nx, ny, nm) in enumerate(nodes):
            ny += slide; on = i in (1, 2)
            d.ellipse((nx - 44, ny - 44, nx + 44, ny + 44), fill=(14, 30, 46), outline=LIME if on else CYAN, width=6)
            d.text((nx - 60, ny + 54), nm, font=MF(24), fill=LIME if on else (190, 220, 235))
        d.text((x0 + 40, y1 - 110), 'points 1', font=MF(26), fill=AMB)
    return out.convert('RGB')


mapdim = dark(MAP, .45)
for b in (HEATBOX, CREWBTN, DEFBTN):
    mapdim.paste(MAP.crop(b), b[:2])
pick = ring_hi(MAP, CREWBTN, LIME, 7)
T09 = [pick, overlay(blend(pick, mapdim, .6), 'RECRUIT', slide=48, alpha=.6), overlay(mapdim, 'RECRUIT'), overlay(mapdim, 'WEAPONS'),
       overlay(mapdim, 'TALENTS'), overlay(blend(mapdim, MAP, .5), 'TALENTS', slide=40, alpha=.45), MAP]

# ---------------- T11 (labels only changed) ----------------
k1 = S['r8plan'].copy(); d1 = ImageDraw.Draw(k1)
d1.line((30, 18, 400, 80), fill=(235, 30, 40), width=9); d1.line((30, 80, 400, 18), fill=(235, 30, 40), width=9)
d1.text((420, 4), '0', font=F(80, True), fill=(235, 30, 40))
T11 = [k1, tint(desat(dark(k1, .5), .5), (120, 10, 60), .2), shrink_on(dark(k1, .35), S['loseB'], .78, .5, .5, rot=-2), S['loseB']]

# ---------------- T12: Solace HQ, real streets ----------------
hq_st = Z['final_lot3']
recol = tint(hue_sweep(hq_st, 150, 250, 48, sweep=1.0, smin=70, vmin=120), ACID, .08)
t3m = chip(marker(MAP.copy(), 1265 / W, 390 / H, 'win'), (1180, 130), 'TIER 3: 3 / 3', LIME)
k2_12 = chip(target_ring(Z['strip_00'], MARK0, SOL), (520, 40), 'DISPATCH // SOLACE HQ OPEN', SOL, 44)
T12 = [t3m, k2_12, Z['dense_012'], hq_st, S['blkd'], recol, blend(recol, Image.new('RGB', (W, H), (255, 255, 255)), .7),
       shrink_on(dark(recol, .4), S['winB'], .78, .5, .5, rot=-2), S['winB']]

FR = {'t01': T01, 't02': T02, 't03': T03, 't04': T04, 't05': T05, 't06': T06, 't07': T07, 't08': T08,
      't09': T09, 't11': T11, 't12': T12}
# R real, r real from a DRAFT set, C composite of real renders, X concept, N new 2D plate (this pass)
KIND = {'t01': 'RCXXCRRRXC', 't02': 'CCXXCRNRRR', 't03': 'RXXXCCR', 't04': 'RXXCXR', 't05': 'CCXRRCXCCX',
        't06': 'CXCCCCR', 't07': 'CCRRrRRCR', 't08': 'CRrRXCC', 't09': 'CCXXXCR', 't11': 'CCCR', 't12': 'CCRRNXXCR'}

T = []
for t in TEXT:
    ims, labs, kd = FR[t['id']], t['labels'], KIND[t['id']]
    assert len(ims) == len(labs) == len(kd), (t['id'], len(ims), len(labs), len(kd))
    t = dict(t); t['keys'] = [(lb, stamp(im) if k == 'X' else im, k) for lb, im, k in zip(labs, ims, kd)]
    T.append(t)

COL = {'R': LIME, 'r': LIME, 'C': (70, 200, 255), 'X': AMB, 'N': PINK}
TAG = {'R': 'REAL', 'r': 'REAL  DRAFT', 'C': 'COMP', 'X': 'CONCEPT', 'N': 'NEW 2D PLATE'}
TAGW = {'R': 84, 'r': 150, 'C': 84, 'X': 126, 'N': 166}


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
              ('REDUCED MOTION', tr['rm']), ('REAL VS CONCEPT', tr['real']), ('CHANGE VS V4', tr['chg']), ('FEEL', tr['feel'])]
    f, fb_ = F(19), F(19, True)
    lines_ = [(h, textwrap.wrap(x, 150) or ['']) for h, x in blocks]
    th_text = sum(len(w) for _, w in lines_) * 25 + len(lines_) * 33 + 20
    top = 70
    Wd = mx * 2 + cols * tw + (cols - 1) * g
    S_ = Image.new('RGB', (Wd, top + rows * (th + lab + g) + th_text + 20), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 18), tr['title'][:110], font=F(30, True), fill=LIME)
    d.text((Wd - mx - 250, 20), 'DRAFT  v5  Campaign B', font=F(24, True), fill=AMB)
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
    for h, wr in lines_:
        d.text((mx, y), h, font=fb_, fill=AMB); y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222)); y += 25
        y += 8
    return S_


def grid_h(n, cols=3):
    return 70 + math.ceil(n / cols) * (347 + 36 + 24)


def flow():
    S_ = Image.new('RGB', (2300, 1330), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((40, 20), 'Transition flow v5 (DRAFT): Campaign B after the designer\'s v4 rulings (numbers are T1 to T12; T10 held)', font=F(38, True), fill=LIME)
    B_ = {}

    def box(k, x, y, label, col=(60, 70, 90), w=360, h=92):
        B_[k] = (x, y, w, h)
        d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(26, 30, 40), outline=col, width=4)
        for j, t in enumerate(label.split('\n')):
            d.text((x + 14, y + 12 + j * 28), t, font=F(23 if j else 24, j == 0), fill=(235, 235, 240) if j == 0 else (190, 195, 205))

    box('map', 760, 560, 'CITY MAP (r42 hq_idle, Solace)\nsites, Heat, CREW / MARKET / DEFENCE', LIME, w=470, h=100)
    box('street', 1330, 560, 'NETRUN STREET\nreal street, zoom to the building', LIME, w=420)
    box('room', 1330, 300, 'ROOM\ncutaway by kind; BLOCK SERVER lab', LIME, w=420)
    box('fight', 1860, 300, 'FIGHT\nDeface v3 board', LIME, w=380)
    box('fail', 1860, 700, 'NETRUN FAILURE\ntrace printout (design C)', PINK, w=380)
    box('hq', 120, 560, 'HQ WORKSHOP\noverlay on the map', AMB, w=380)
    box('alert', 120, 880, 'RAID ALERT\nany Heat line, 100 included', (232, 20, 30), w=380)
    box('plan', 760, 880, 'RAID PLANNING\nposts, dock, shop, evacuate', LIME, w=420)
    box('run', 1330, 880, 'RAID PLAYS\nvia claimed sites, ends at HQ', LIME, w=420)
    box('lose', 760, 1180, 'DOSSIER (LOSE)\nHQ integrity 0', PINK, w=420)
    box('hqnet', 760, 200, 'HQ NETRUN\nSolace HQ street, BLOCK SERVER', AMB, w=420)
    box('win', 1330, 90, 'DOSSIER (WIN)\nslot B, campaign won', LIME, w=420)
    box('held', 120, 1130, 'T10 PURGE RECALL\nHELD (ruling 7), archive/', (90, 90, 100), w=380)
    d.line((130, 1140, 490, 1212), fill=(160, 60, 60), width=4)

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
    arrow('map', 'alert', 6, (232, 20, 30), side=('b', 't'), off=(-180, 0), off2=(0, 0)); arrow('alert', 'plan', None, (232, 20, 30))
    arrow('map', 'plan', 7, side=('b', 't'), off=(-30, 0)); arrow('plan', 'map', None, side=('t', 'b'), off=(60, 0))
    arrow('plan', 'run', 8); arrow('run', 'map', 8, side=('t', 'r'), off2=(0, 30))
    arrow('map', 'hq', 9, AMB, off=(0, -22), side=('l', 'r')); arrow('hq', 'map', None, AMB, off=(0, 22))
    arrow('run', 'lose', 11, PINK, side=('b', 'r'))
    arrow('map', 'hqnet', 12, AMB, side=('t', 'b')); arrow('hqnet', 'win', 12, AMB)
    d.text((40, 1295), 'Lime = approved or real render at that screen; amber = special path (workshop overlay, HQ netrun); red = Heat raid entry (Heat 100 is a normal raid); pink = loss. T10 PURGE is held (B-105 ruling 7).', font=F(20), fill=(215, 215, 222))
    return S_


def sheet():
    tw, th, g, lw, mx = 230, 130, 8, 300, 20
    cols = max(len(t['keys']) for t in T)
    rowh = th + 24 + g
    rows = T[:9] + [None] + T[9:]
    S_ = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 64 + len(T) * rowh + 60), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 14), "REBEL_CELL transitions v5, Campaign B (DRAFT). Green = real render, green+amber = DRAFT set, cyan = composite, amber = concept, pink = new 2D plate", font=F(24, True), fill=LIME)
    y = 64
    for t in rows:
        if t is None:
            d.rectangle((mx, y + 6, S_.width - mx, y + 50), fill=(26, 26, 32), outline=(90, 90, 100), width=2)
            d.text((mx + 14, y + 16), 'T10  PURGE recall: HELD / withdrawn (B-105 ruling 7). Heat 100 is a normal raid (T6 > T7 > T8). Old sheet: archive/t10_purge_recall_HELD.jpg', font=F(20, True), fill=(200, 200, 210))
            y += 60
            continue
        for k, w in enumerate(textwrap.wrap(t['title'], 30)[:4]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), textwrap.wrap(t['dur'], 34)[0], font=F(14), fill=LIME)
        d.text((mx, y + 120), 'unchanged (v4 copy)' if t['status'] == 'copied' else 'changed in v5', font=F(14, True), fill=(150, 150, 160) if t['status'] == 'copied' else AMB)
        for i, (lb, im, kind) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S_.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=COL[kind] if kind != 'r' else AMB, width=3)
            badge(d, x, y, kind, .6)
            d.text((x, y + th + 3), lb[:40], font=F(12), fill=(200, 200, 208))
        y += rowh
    return S_.crop((0, 0, S_.width, y + 10))


def v4_vs_v5(strips):
    sc = .40
    gw = int(1968 * sc)
    rows = []
    for i in ['t%02d' % k for k in range(1, 13)]:
        v4t = V4D[i]
        a = Image.open(V4 + v4t['file']).convert('RGB'); a = a.crop((0, 0, a.width, grid_h(len(v4t['labels']))))
        tt = [x for x in T if x['id'] == i]
        if i == 't10':
            b = Image.new('RGB', (1968, 500), (22, 24, 30)); db = ImageDraw.Draw(b)
            db.text((60, 160), 'HELD (ruling 7)', font=F(80, True), fill=AMB)
            db.text((60, 290), 'no PURGE event: Heat 100 is a normal raid (T6 > T7 > T8); sheet in archive/', font=F(34), fill=(210, 210, 220))
            title = 'T10  HELD'
        elif tt[0]['status'] == 'copied':
            b = Image.new('RGB', (1968, 500), (22, 24, 30)); db = ImageDraw.Draw(b)
            db.text((60, 200), 'unchanged in v5 (copied from v4)', font=F(64, True), fill=(160, 165, 175))
            title = tt[0]['title']
        else:
            b = strips[i]; b = b.crop((0, 0, b.width, grid_h(len(tt[0]['keys'])))); title = tt[0]['title']
        rows.append((v4t['title'], title, a, b))
    tot = 90 + sum(int(max(a.height, b.height) * sc) + 44 for _, _, a, b in rows)
    S_ = Image.new('RGB', (gw * 2 + 90, tot), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((30, 18), 'v4 (left) vs v5 (right, DRAFT): the designer\'s rulings on v4 (B-105)', font=F(26, True), fill=LIME)
    y = 70
    for t4, t5, a, b in rows:
        d.text((30, y), ('v4: ' + t4)[:80], font=F(19, True), fill=(180, 185, 195))
        d.text((gw + 60, y), t5[:84], font=F(19, True), fill=AMB)
        y += 32
        A = a.resize((gw, int(a.height * sc)), Image.LANCZOS); B2 = b.resize((gw, int(b.height * sc)), Image.LANCZOS)
        S_.paste(A, (30, y)); S_.paste(B2, (gw + 60, y))
        y += max(A.height, B2.height) + 12
    return S_.crop((0, 0, S_.width, y + 10))


def archive_t10():
    a = Image.open(V4 + 't10_purge_recall.jpg').convert('RGB')
    ov = Image.new('RGBA', a.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((0, 0, a.width, 64), fill=(30, 30, 36, 255))
    d.text((36, 14), 'HELD / WITHDRAWN 2026-11-16 (B-105 ruling 7): no PURGE event; Heat 100 is a normal raid. Recall-streak FX held.', font=F(26, True), fill=AMB + (255,))
    t = Image.new('RGBA', (1500, 300), (0, 0, 0, 0)); ImageDraw.Draw(t).text((750, 150), 'HELD', font=F(260, True), fill=(255, 170, 60, 110), anchor='mm')
    t = t.rotate(14, expand=True, resample=Image.BICUBIC)
    ov.alpha_composite(t, ((a.width - t.width) // 2, 400))
    out = a.convert('RGBA'); out.alpha_composite(ov); return out.convert('RGB')


SOURCES = ['## Sources (read only)\n',
           '- **Rulings:** build mailbox B-105 and DECISIONS 2026-11-16 "transitions v4 rulings" (origin/port-campaign-b); jack timings from art/jack-6s 980f31f1a (`content/config/ui_motion.tres`, DECISIONS "jack-in / jack-out at 6-7 s").',
           '- **City map page:** `cohesion/map_pages_r42/hq_idle.png` (r42, Solace; ruling 6).',
           '- **Real streets:** art/zoom-to-building lit captures (A-143, seed 7, hq = solace), the frames of `zoom_to_building/zoom_strip.jpg`, read from `D:/rc_tmp/claude/zt/final/` and copied to `plates/zoom_to/` (strip_00 city, dense_008 / 012 / 015 / 019 / 021 / 023 along the path, strip_05 the lit street, final_lot3 a street by the Solace HQ).',
           '- **Rooms:** `combat_backdrop/v3_1/room_{bio,event,shop,srv}_bare.png`; new `plates/room_block_server.png` and `_beaten.png` (BLOCK SERVER bio lab, drawn by `scripts/blocklab5.py` over the bio box).',
           '- **Fight:** `takeover_board/v3/v3_board.png`, `v3_win.png`. **Netrun failure:** `transitions/netrun_fail/C_trace_printout.png` (design C, ruling 2).',
           '- **Raid:** set 7 `raid_v3/r3_*.png`, set 8 (DRAFT) `raid_v3/set8/r8_*.png`, raid capture `transitions/v4/plates/raid_city_capture.jpg`. **End screens:** `solace_endscreens/v2/{win,lose}_B.png`.', '']


def md():
    o = ['# Transitions storyboard v5: Campaign B, the designer\'s rulings on v4 (DRAFT, 2026-11-16)\n',
         '**DRAFT.** v4 (`../v4/`) redone per the designer\'s rulings (build\'s B-105; DECISIONS 2026-11-16 "transitions v4 rulings") and the standing rulings (no staged streets: every netrun is on the exact city street and zooms to the exact building; Solace only). Concept plates only (PIL compositing and 2D drawing); no Godot or Blender run. v4 stays as the record. Each transition\'s **Change vs v4** line cites the ruling.\n',
         'Badges: **REAL** (green) an existing render or a crop; **REAL DRAFT** (green + amber) from a DRAFT set; **COMP** (cyan) real renders composed here; **CONCEPT** (amber, stamped) invented FX or a screen with no render; **NEW 2D PLATE** (pink) a plate drawn in this pass (the BLOCK SERVER bio lab).\n',
         '- `flow.jpg`: how the transitions connect. `sheet.jpg`: all strips on one page. `v4_vs_v5.jpg`: each v5 transition beside its v4 one. `plates/PLATES.txt`: sources and hashes. `archive/t10_purge_recall_HELD.jpg`: the held T10.\n',
         '## Rulings applied (B-105)\n',
         '1. Jack 6-7 s: T1 6.52 s, T5 jack-out 6.82 s (art/jack-6s).', '2. Fail screen: design C (trace printout): T4.',
         '3. HQ workshop: an overlay on the city map, no round 42 room: T9.', '4. T3: the bits fly first and build the ring.',
         '5. T2: one seamless move, the other rooms close their walls; BLOCK SERVER = an enhanced bio lab with a giant tank: T2 (and T12).',
         '6. Map page: r42 hq_idle, Solace only (all map frames).', '7. T10 PURGE held; Heat 100 is a normal raid (T6 / T7 / T8); T11 relabelled.',
         '8. T8 approved (copied); T12 approved and redone on the Solace HQ and real streets.', '']
    o += SOURCES
    o += ['## Master timing table\n', '| # | Transition | v5 | Duration | Easing |', '|---|---|---|---|---|']
    for t in T:
        o.append('| %s | %s | %s | %s | %s |' % (t['id'].upper(), t['title'][4:].strip(), 'unchanged' if t['status'] == 'copied' else 'changed', t['dur'], t['ease']))
        if t['id'] == 't09':
            o.append('| T10 | PURGE recall | HELD | (ruling 7) | |')
    o += ['', 'Jack beats (art/jack-6s, the animatic at 0.5): jack-in = terminal 0.70, rain 0.625, CRT collapse 0.225, dive 1.50, REVEAL 1.82, MARK 0.50 + hold 0.40, ZOOM 0.50 + settle 0.25 = **6.52 s**. Jack-out = the street side backwards (4.97 s), select hold 0.30, the HQ side backwards (1.55 s) = **6.82 s**. Reduced motion stays a 0.25 s cross-fade everywhere.\n',
          '![flow](flow.jpg)\n']
    for t in T:
        o += ['## %s%s\n' % (t['title'], '  (unchanged, copied from v4)' if t['status'] == 'copied' else ''), '![%s](%s)\n' % (t['id'], t['file']),
              '- **Keys:** ' + '; '.join('%s [%s]' % (k[0].strip(), TAG[k[2]].lower().replace('  ', ' ')) for k in t['keys']),
              '- **Duration:** ' + t['dur'], '- **Easing:** ' + t['ease'], '- **Camera path:** ' + t['cam'],
              '- **UI hand-over:** ' + t['ui'], '- **Reduced motion:** ' + t['rm'], '- **Feel:** ' + t['feel'],
              '- **Real vs concept:** ' + t['real'], '- **Change vs v4:** ' + t['chg'], '']
        if t['id'] == 't09':
            o += ['## T10  PURGE recall: HELD\n', T10_NOTE, '']
    o += ['## The BLOCK SERVER room (ruling 5)\n', '![block server](plates/room_block_server.png)\n',
          'An enhanced bio lab: a giant glowing tank in the centre (corp_solace liquid, a dark curled specimen with one lit eye, bubbles, steel bands, a cap with pipes up out of the cutaway), cables from the tank to server racks along the back walls (floor runs and overhead sagging lines), two lab consoles facing the tank, an amber hazard ring. Drawn in 2D over the v3.1 bio cutaway box, so the building, street and SOLACE signage match the other rooms. `room_block_server_beaten.png` is the same room with the tank dark (T12 K5).', '']
    o += STILL + CALLS + OPEN + LOG
    return '\n'.join(o)


strips = {}
for t in T:
    if t['status'] == 'copied':
        shutil.copyfile(V4 + t['file'], OUT + t['file'])
    else:
        strips[t['id']] = strip(t); strips[t['id']].save(OUT + t['file'], quality=90)
archive_t10().save(OUT + 'archive/t10_purge_recall_HELD.jpg', quality=88)
sheet().save(OUT + 'sheet.jpg', quality=88)
flow().save(OUT + 'flow.jpg', quality=90)
v4_vs_v5(strips).save(OUT + 'v4_vs_v5.jpg', quality=84)
open(OUT + 'STORYBOARD.md', 'w', encoding='utf-8').write(md())
print('ok')
