"""title_screen.png (option A) + title_screen_option_b.png + title_screen.gif (A): the main menu over the living night city (round 26 v4 motion,
re-rendered without labels by city_frames.py).

Media: REBEL_CELL neon tube sign on a circuit-board backing (MARKET NEON energy, Anton outline tubes,
OFL); CONTINUE = the one sticker verb; the rest of the menu, slot summary, profile and the radio
ticker = terminal (the Cell's systems); NEVER SLEEP + the plan note = grease pencil.
GIF loop (48 x 80 ms, seamless): city traffic, cursor '_' blink, one E stutter, a two-frame drop to
'CELL' only, a slow gloss sweep over CONTINUE, the radio ticker.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import sticker_lib31 as SL  # noqa: E402
import ui31 as U  # noqa: E402
import cm  # noqa: E402
import menu33 as M  # noqa: E402

W, H = 1920, 1080
N = 48
CITY = os.path.join(U.SCR, 'city')
OUT_PNG = os.path.join(U.ROOT, 'title_screen.png')
OUT_GIF = os.path.join(U.ROOT, 'title_screen.gif')
OUT_ALT = os.path.join(U.ROOT, 'title_screen_alt_simulate.png')
GLITCH_FRAMES = {9: 0, 10: 1, 27: 1, 28: 0}   # two short DISABLE bursts per 3.84 s loop

BOARD = (70, 46, 1010, 300)
WORD = [('REBEL', U.PINK), ('_', U.LIME), ('CELL', U.PINK)]


# ------------------------------------------------------------------ backdrop
_grad = None


def backdrop(f):
    global _grad
    src = Image.open(os.path.join(CITY, 'f%02d.png' % f)).convert('RGB')
    sharp = np.asarray(src, np.float32)
    soft = np.asarray(src.filter(ImageFilter.GaussianBlur(5)), np.float32)
    if _grad is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        # tilt-shift: sharp band through the middle-right, soft top and bottom
        band = np.clip(1 - np.abs((y / H) - 0.56) / 0.36, 0, 1) ** 0.8
        # menu side darkening (left) + bottom
        dark = 1 - 0.62 * np.clip(1 - x / 900, 0, 1) ** 1.4 - 0.35 * np.clip((y / H - 0.82) / 0.18, 0, 1)
        vig = 1 - 0.35 * (((x / W - 0.6) * 1.3) ** 2 + ((y / H - 0.5) * 1.1) ** 2)
        _grad = (band[..., None], (dark * vig)[..., None] * 0.86)
    band, k = _grad
    a = soft * (1 - band) + sharp * band
    a = a * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ------------------------------------------------------------------ neon sign
def word_masks():
    """Per-letter tube masks for REBEL_CELL in Anton outline (1x canvas coords)."""
    f = U.F(U.ANTON, 164)
    total = sum(f.getlength(ch) + (14 if ch != '_' else 4) for part, _ in WORD for ch in part) - 14
    x = (BOARD[0] + BOARD[2]) / 2 - total / 2
    y = BOARD[1] + 132
    letters = []
    for part, col in WORD:
        for ch in part:
            m = Image.new('L', (W, H), 0)
            ImageDraw.Draw(m).text((x, y), ch, font=f, fill=255, anchor='lm')
            if ch == '_':
                m = Image.new('L', (W, H), 0)
                ImageDraw.Draw(m).rounded_rectangle([x + 4, y + 62, x + 70, y + 76], 7, fill=255)
            ring = ImageChops.subtract(SL.dilate(m, 3), SL.erode(m, 3)) if ch != '_' else m
            core = ImageChops.subtract(SL.dilate(m, 1), SL.erode(m, 1)) if ch != '_' else SL.erode(m, 3)
            g = (np.asarray(ring.filter(ImageFilter.GaussianBlur(26)), np.float32) * 1.6
                 + np.asarray(ring.filter(ImageFilter.GaussianBlur(8)), np.float32) * 1.1) / 255
            letters.append(dict(ch=ch, col=col, ring=ring, core=core, fill=m, glow=g[..., None],
                                ringa=(np.asarray(ring, np.float32) / 255)[..., None],
                                corea=(np.asarray(core, np.float32) / 255)[..., None]))
            x += f.getlength(ch) + (14 if ch != '_' else 4)
    return letters


def board(img, seed=31):
    x0, y0, x1, y1 = BOARD
    rng = random.Random(seed)
    d = U.BD(img)
    # hanging cables
    for cx in (x0 + 120, x1 - 120):
        d.line([(cx, 0), (cx, y0 + 6)], fill=(30, 30, 36, 255), width=5)
        d.line([(cx + 2, 0), (cx + 2, y0 + 6)], fill=(70, 70, 80, 255), width=1)
    m = U.rect_mask(img.size, BOARD, r=12)
    img = U.shadow(img, m, (8, 14), 16, 0.7)
    img = U.over(img, (10, 22, 20), m)
    # copper traces
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    for _ in range(70):
        px, py = rng.uniform(x0 + 14, x1 - 14), rng.uniform(y0 + 14, y1 - 14)
        pts = [(px, py)]
        for _ in range(rng.randint(2, 5)):
            if rng.random() < 0.5:
                px = min(x1 - 14, max(x0 + 14, px + rng.choice([-1, 1]) * rng.uniform(20, 90)))
            else:
                py = min(y1 - 14, max(y0 + 14, py + rng.choice([-1, 1]) * rng.uniform(10, 50)))
            pts.append((px, py))
        dl.line(pts, fill=(36, 78, 64, 255), width=2)
        ex, ey = pts[-1]
        dl.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(112, 94, 52, 255))
    for _ in range(12):
        cx, cy = rng.uniform(x0 + 30, x1 - 60), rng.uniform(y0 + 20, y1 - 40)
        dl.rectangle([cx, cy, cx + rng.uniform(20, 46), cy + rng.uniform(12, 22)], fill=(18, 18, 22, 255))
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    img = Image.alpha_composite(img, lay)
    e = ImageChops.subtract(m, SL.erode(m, 5))
    img = U.over(img, (58, 60, 68), e)
    d = U.BD(img)
    for sx, sy in ((x0 + 16, y0 + 16), (x1 - 16, y0 + 16), (x0 + 16, y1 - 16), (x1 - 16, y1 - 16)):
        d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=(150, 150, 160, 255), outline=(30, 30, 34, 255))
        d.line([(sx - 4, sy), (sx + 4, sy)], fill=(40, 40, 46, 255), width=2)
    U.text(img, (x0 + 34, y1 - 22), 'RC-03 // NEON RIG REV.B', U.F(U.MONO, 14), (80, 136, 110), 'la', 1.2)
    return img


def neon(img, letters, lit, flick=None):
    """lit: per-letter brightness 0..1 (0 = dark tube, still visible as glass)."""
    flick = flick or {}
    spill = Image.new('RGB', img.size, (0, 0, 0))
    out = img
    # dark glass tubes for every letter
    for L in letters:
        out = U.over(out, (60, 30, 50) if L['col'] == U.PINK else (50, 60, 20), L['ring'], 0.9)
    arr = np.asarray(out, np.float32)
    for i, L in enumerate(letters):
        b = lit[i]
        if b <= 0:
            continue
        col = np.array(L['col'], np.float32)
        ring, core = L['ringa'], L['corea']
        arr[..., :3] += L['glow'] * col * b
        tube = col * 0.75 + 255 * 0.25
        arr[..., :3] = arr[..., :3] * (1 - ring * b) + tube * ring * b
        arr[..., :3] = arr[..., :3] * (1 - core * b) + np.array([255, 236, 248], np.float32) * core * b
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def street_spill(img, letters, lit):
    """Pink light from the sign falling on the city below it."""
    k = sum(lit) / len(lit)
    if k <= 0:
        return img
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).ellipse([BOARD[0] - 40, BOARD[3] - 60, BOARD[2] + 40, BOARD[3] + 260], fill=110)
    m = m.filter(ImageFilter.GaussianBlur(70))
    return U.add_glow(img, m, U.PINK, 1, 0.55 * k)


# ------------------------------------------------------------------ menu options (round 32)
# The menu the game needs (art_asset G1/G2/G7, GDD 1.3): Continue, New campaign (via Campaigns), Campaign
# slots, Tutorial, Codex, Stats & achievements, Options, Quit. Every punchy verb carries its plain
# meaning underneath, so the meaning is never lost.
OPT_A = [  # "THE PLAN": the designer's three verbs are the three big actions, numbered in grease pencil
    ('BREACH', U.FILL_PINK, 'CONTINUE', 'slot 1 // Halcyon Civic // run 9 // Heat 58'),
    ('DISABLE', 'glitch', 'TUTORIAL', 'learn the wheels on a practice target'),
    ('OVERTHROW', 'fist', 'NEW CAMPAIGN', 'pick a corporation to bring down'),
]
OPT_ALT = [OPT_A[0], ('SIMULATE', 'glitch', 'TUTORIAL', 'a practice run in a simulated net'), OPT_A[2]]
OPT_A_MORE = [('CAMPAIGN SLOTS', '[C]'), ('CODEX', '[X]'), ('STATS & ACHIEVEMENTS', '[S]'), ('OPTIONS', '[O]'), ('QUIT', '[ESC]')]
OPT_B = [  # "ONE VERB PER ITEM": every line is a verb; the plain item is the second line
    ('OVERTHROW', 'new campaign'), ('CASE FILES', 'campaign slots: load, delete'), ('DRILL', 'tutorial'),
    ('INTEL', 'codex'), ('RAP SHEET', 'stats & achievements'), ('RIG', 'options'), ('GO DARK', 'quit'),
]


def stk(word, fill, size, seed, focus=False):
    if fill == 'glitch':
        gs = M.glitch_sticker_set(word, size, seed, phases=(-1, 0, 1))
        bb = gs[-1]['img'].split()[3].getbbox()
        return dict(base=gs[-1], sweeps=[], glitch={0: gs[0], 1: gs[1]}, w=(bb[2] - bb[0]) / SL.SS)
    if fill == 'fist':
        base = M.fist_word_sticker(word.replace('THROW', 'THR@W'), size, seed)
        bb = base['img'].split()[3].getbbox()
        return dict(base=base, sweeps=[], w=(bb[2] - bb[0]) / SL.SS)
    art = SL.lettering([word], size, [fill], key_w=5, extrude=7, seed=seed, jitter=2.0, track=-1)
    base = SL.build_sticker(art, border=12, gloss_k=0.22, seed=seed)
    sweeps = []
    if focus:
        for k in range(12):
            sweeps.append(U.focus_sticker(SL.build_sticker(art, border=12, gloss_k=0.85, gloss_pos=-0.15 + k * 0.13, seed=seed)))
        base = U.focus_sticker(base)
    bb = base['img'].split()[3].getbbox()
    w1 = (bb[2] - bb[0]) / SL.SS
    return dict(base=base, sweeps=sweeps, w=w1)


def common_ui(lay, version='v0.33'):
    lay = U.term_panel(lay, (1500, 742, 1868, 958), 'PROFILE // CELL-03', seed=8, alpha=222)
    stats = [('CAMPAIGNS', '7'), ('WON', '2'), ('BEST ICE', '6'), ('RUNS', '61'), ('RAIDS HELD', '14'), ('BADGES', '5 / 10')]
    for k, (a, b) in enumerate(stats):
        col, row = k % 2, k // 2
        x = 1520 + col * 176
        yy = 790 + row * 52
        U.text(lay, (x, yy), a, U.F(U.MONO, 15), (120, 160, 190), 'la', 1.0)
        U.text(lay, (x, yy + 18), b, U.F(U.MONO, 26), U.WHITE, 'la', 1.0)
    U.text(lay, (94, 996), 'REBEL_CELL %s.0  //  build 2026-10-03  //  godot 4.7' % version, U.F(U.MONO, 16), (130, 140, 160), 'la', 0.8)
    x = 1500
    for g, s in (('A', 'select'), ('B', 'back'), ('Y', 'codex')):
        d = U.BD(lay)
        d.ellipse([x, 985, x + 26, 1011], fill=(240, 238, 232, 255), outline=(10, 10, 14, 255), width=2)
        U.text(lay, (x + 13, 999), g, U.F(U.BAHN, 16, 'Bold'), (14, 14, 20), 'mm')
        U.text(lay, (x + 34, 998), s, U.F(U.MONO, 17), U.WHITE, 'lm', 0.8)
        x += 120
    return lay


def slogan(pen):
    pen.text('NEVER SLEEP', 846, 338, 36, angle=-5)
    pen.stroke(pen.wobble([(952, 300), (958, 282), (968, 296), (978, 278), (986, 296), (994, 280), (998, 302), (952, 304)], 0.6), width=5)


def static_ui(opt):
    """Returns (layer, stickers) where stickers = [(sticker dict, cx, cy, angle, animated)]."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay = common_ui(lay)
    pen = U.Pencil((W, H), U.PEN_Y, seed=12)
    slogan(pen)
    stickers = []
    if opt in ('a', 'alt'):
        rows_def = OPT_A if opt == 'a' else OPT_ALT
        X0 = 150
        rows = [stk(w, f, 60, 50 + k, focus=(k == 0)) for k, (w, f, _, _) in enumerate(rows_def)]
        wmax = max(r['w'] for r in rows)
        for k, ((w, f, plain, meta), r) in enumerate(zip(rows_def, rows)):
            cy = 392 + k * 112
            pen.text('%d.' % (k + 1), 110, cy + 4, 44, angle=-4)
            stickers.append((r, X0 + r['w'] / 2, cy, (-2, 1.5, -1)[k], k == 0))
            cx0 = int(X0 + wmax + 26)
            lay = U.term_panel(lay, (cx0, cy - 32, cx0 + 470, cy + 32), None, hexbg=False, chamfer=10, header=False,
                               glow=0.4 if k == 0 else 0.2, alpha=220, accent=U.CYAN if k == 0 else (110, 150, 180))
            U.text(lay, (cx0 + 18, cy - 11), plain, U.F(U.MONO, 22), U.WHITE, 'lm', 1.6)
            U.text(lay, (cx0 + 18, cy + 15), meta, U.F(U.MONO, 15), U.CYAN if k == 0 else (150, 176, 200), 'lm', 0.6)
        pen.stroke(pen.wobble([(96, 340), (90, 500), (96, 690)], 1.2), width=5)        # the plan bracket
        lay = U.term_panel(lay, (92, 732, 560, 966), 'MORE', tag='v0.33', seed=5, alpha=226)
        for k, (nm, key) in enumerate(OPT_A_MORE):
            yy = 782 + k * 38
            U.text(lay, (128, yy), nm, U.F(U.MONO, 23), (190, 214, 232) if nm != 'QUIT' else (150, 160, 178), 'lm', 1.4)
            U.text(lay, (540, yy), key, U.F(U.MONO, 16), (90, 130, 160), 'rm', 0.8)
    else:
        r = stk('BREACH', U.FILL_PINK, 76, 44, focus=True)
        stickers.append((r, 150 + r['w'] / 2, 392, -2, True))
        lay = U.term_panel(lay, (92, 452, 700, 516), None, hexbg=False, chamfer=10, header=False, glow=0.4, alpha=220)
        U.text(lay, (112, 472), 'CONTINUE  //  SLOT 1  //  HALCYON CIVIC', U.F(U.MONO, 20), U.WHITE, 'lm', 1.2)
        U.text(lay, (112, 498), 'run 9   Heat 58 FLAGGED   ICE 5   crew 3', U.F(U.MONO, 16), U.CYAN, 'lm', 0.9)
        lay = U.term_panel(lay, (92, 540, 640, 966), 'MAIN', tag='v0.32', seed=5, alpha=226)
        keys = ['[N]', '[C]', '[T]', '[X]', '[S]', '[O]', '[ESC]']
        for k, (verb, plain) in enumerate(OPT_B):
            yy = 594 + k * 52
            U.text(lay, (128, yy), verb, U.F(U.MONO, 27), (200, 222, 238) if verb != 'GO DARK' else (160, 170, 188), 'lm', 1.8)
            U.text(lay, (130, yy + 23), plain, U.F(U.MONO, 15), (120, 160, 190), 'lm', 0.8)
            U.text(lay, (620, yy + 4), keys[k], U.F(U.MONO, 16), (90, 130, 160), 'rm', 0.8)
        # the designer's three words stay as the Cell's slogan (top right)
        pen.text('1. BREACH', 1640, 96, 40, angle=-3)
        pen.text('2. DISABLE', 1656, 150, 40, angle=-2)
        pen.text('3. OVERTHROW', 1680, 204, 40, angle=-4)
        pen.stroke(pen.wobble([(1544, 240), (1680, 236), (1820, 242)], 1.0), width=6)
    lay = pen.ink(lay, 0.9)
    return lay, stickers


def ticker(img, f):
    y0, y1 = 1028, 1064
    m = U.rect_mask(img.size, (0, y0, W, y1))
    img = U.over(img, U.NAVY, m, 0.92)
    d = U.BD(img)
    d.line([(0, y0), (W, y0)], fill=U.CYAN + (180,), width=2)
    d.rectangle([0, y0 + 2, 210, y1], fill=U.CYAN + (230,))
    seg = '  +++  PIRATE RADIO 88.1  //  HALCYON RAISES FARES AGAIN'
    f_ = U.F(U.MONO, 19)
    P = int(U.tw(seg, f_, 1.0))
    off = (f / N) * P
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = 220 - off
    while x < W:
        U.text(lay, (x, (y0 + y1) / 2 + 1), seg, f_, U.CYAN, 'lm', 1.0)
        x += P
    clip = U.rect_mask(img.size, (214, y0, W, y1))
    lay.putalpha(ImageChops.multiply(lay.split()[3], clip))
    img = Image.alpha_composite(img, lay)
    U.text(img, (105, (y0 + y1) / 2 + 1), 'ON AIR', U.F(U.MONO, 19), U.NAVY, 'mm', 2.0)
    return img


def lit_state(f, n_letters):
    lit = [1.0] * n_letters
    cur = 5                                                      # index of '_'
    lit[cur] = 1.0 if (f // 6) % 2 == 0 else 0.0                 # cursor blink, 12-frame period
    if f in (20, 22):                                            # E stutter (second letter)
        lit[1] = 0.15
    if f == 21:
        lit[1] = 0.55
    if f in (31, 32):                                            # drop: only CELL stays lit
        for i in range(0, 6):
            lit[i] = 0.0
    if f == 33:
        for i in range(0, 5):
            lit[i] = 0.5
    return lit


def compose(f, letters, ui, stickers, board_img_cache={}):
    img = backdrop(f)
    lit = lit_state(f, len(letters))
    img = street_spill(img, letters, lit)
    if 'b' not in board_img_cache:
        board_img_cache['b'] = board(Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    img = Image.alpha_composite(img, board_img_cache['b'])
    img = neon(img, letters, lit)
    img = Image.alpha_composite(img, ui)
    for r, cx, cy, ang, anim in stickers:
        sd = r['sweeps'][f - 36] if (anim and r['sweeps'] and 36 <= f < 48) else r['base']
        if r.get('glitch') and f in GLITCH_FRAMES:
            sd = r['glitch'][GLITCH_FRAMES[f]]
        img = U.place(img, sd, cx, cy, angle=ang)
    img = ticker(img, f)
    return img


def main(gif=True):
    letters = word_masks()
    for opt, path in (('a', OUT_PNG), ('alt', OUT_ALT)):
        ui, stickers = static_ui(opt)
        frame0 = compose(0, letters, ui, stickers)
        frame0.convert('RGB').save(path)
        print('wrote', path, flush=True)
        if opt != 'a' or not gif:
            continue
        frames = []
        for f in range(N):
            fr = compose(f, letters, ui, stickers) if f else frame0
            frames.append(fr.convert('RGB').resize((960, 540), Image.LANCZOS))
            print('gif frame', f, flush=True)
        size = cm.save_gif(frames, OUT_GIF, 80, tol=30)
        print('wrote', OUT_GIF, round(size / 1e6, 2), 'MB')


if __name__ == '__main__':
    main(gif='nogif' not in sys.argv)
