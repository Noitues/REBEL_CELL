"""Round 38 -> portraits_classes.png, portrait_states.png, portrait_contexts.png.
Busts come from bust_rig.py (render_busts.py) in scratch/busts. Every live portrait sits on the locked
CRT comms feed (dialogue option A); paper contexts use the photo as a print.

python portraits.py [classes|states|contexts|all]
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageChops

import r31lib as L
import sticker_lib19 as SL

BUSTS = os.path.join(L.SCRATCH, "busts")
CLASS = [  # id, label, colour, base-of, role line
    ("breaker", "BREAKER", (255, 61, 168), None, "hits hard, spins harder"),
    ("wrecker", "WRECKER", (255, 110, 50), "breaker", "heavier Perfect"),
    ("ghost", "GHOST", (91, 224, 255), None, "slips past resistance"),
    ("phantom", "PHANTOM", (219, 193, 255), "ghost", "dodges instead"),
    ("rigger", "RIGGER", (122, 224, 122), None, "runs hot on RAM"),
    ("overclocker", "OVERCLOCKER", (255, 176, 64), "rigger", "banks raw RAM"),
    ("botnet", "BOTNET", (96, 114, 255), None, "fights through drones"),
    ("hivemind", "HIVEMIND", (198, 89, 255), "botnet", "bigger swarm, stays put"),
]
COL = {c[0]: c[2] for c in CLASS}
CALLSIGNS = {
    "breaker": ["KESTREL", "BRICK", "SAFFRON"], "wrecker": ["MALLET", "OXIDE", "JUNO"],
    "ghost": ["NULLCAT", "WREN", "SLEET"], "phantom": ["MIRAGE", "VESPER", "ECHO"],
    "rigger": ["SPROCKET", "TALLY", "KITE"], "overclocker": ["FUSE", "AMPERE", "CINDER"],
    "botnet": ["SWARM", "PIXEL", "HIVE-3"], "hivemind": ["CHORUS", "LATTICE", "MOTH"],
}
_c = {}


def bust(name):
    if name not in _c:
        im = Image.open(os.path.join(BUSTS, name + ".png")).convert("RGBA")
        _c[name] = im.crop((40, 0, 560, 600))
    return _c[name]


# ------------------------------------------------------------------ the CRT comms feed
def feed(name, w, h, acc, label=None, mode="idle", seed=1, sub=None):
    """mode: idle | talk | hurt | stationed | dead | recruit."""
    rng = np.random.default_rng(seed)
    bg = Image.new("RGBA", (w, h), (8, 12, 18, 255))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(10 + 20 * k), int(14 + 12 * k), int(24 + 18 * k), 255))
    gs = max(14, w // 14)
    for x in range(0, w, gs):
        d.line([(x, 0), (x, h)], fill=(20, 34, 44, 255))
    for y in range(0, h, gs):
        d.line([(0, y), (w, y)], fill=(20, 34, 44, 255))
    b = bust(name)
    bw = int(w * 1.0)
    bh = int(bw * b.height / b.width)
    bi = b.resize((bw, bh), Image.LANCZOS)
    ox = (w - bw) // 2 + (int(rng.integers(-6, 6)) if mode == "hurt" else 0)
    bg.alpha_composite(bi, (ox, h - bh + int(h * 0.1)))
    a = np.asarray(bg.convert("RGB"), np.float32)
    a = a * 0.9 + np.array(acc, np.float32) * 0.05
    yy = np.arange(h)[:, None]
    if mode == "hurt":
        # red alarm wash + torn horizontal bands
        a = a * np.array([1.15, 0.7, 0.7], np.float32)
        for _ in range(5):
            y0 = int(rng.integers(0, h - 12))
            hh = int(rng.integers(4, 14))
            a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], int(rng.integers(-24, 24)), axis=1)
    if mode == "stationed":
        g = a.mean(axis=2, keepdims=True)
        a = g * np.array(acc, np.float32)[None, None, :] / 255 * 1.25 * 0.85 + a * 0.15
        a *= 0.8
    if mode == "dead":
        g = a.mean(axis=2, keepdims=True)
        a = np.repeat(g, 3, axis=2) * 0.45
        noise = rng.random((h, w, 1)) * 150
        mask = (rng.random((h, w, 1)) < 0.5).astype(np.float32)
        a = a * 0.6 + noise * mask * 0.55 + 10
    if mode == "recruit":
        g = a.mean(axis=2, keepdims=True)
        a = np.repeat(g, 3, axis=2) * 0.75
    # RGB split + scanlines + rolling bar
    sh = 2 if mode != "hurt" else 6
    r = np.roll(a[..., 0], sh, axis=1)
    bl = np.roll(a[..., 2], -sh, axis=1)
    a = np.stack([r, a[..., 1], bl], -1)
    a *= (0.80 + 0.20 * (yy % 3 != 0))[..., None]
    a += (np.exp(-((yy - h * 0.62) / 18.0) ** 2) * 16)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    if mode not in ("dead", "recruit"):
        img = L.bloom(img, 0.3, 0.7, 6)
    d = ImageDraw.Draw(img)
    fs = max(11, w // 22)
    if label:
        lw = L.f_mono(fs).getlength(label)
        d.rectangle([8, 8, 30 + lw, 12 + fs + 6], fill=(6, 8, 12, 230))
        live = mode in ("idle", "talk", "hurt")
        if live:
            d.ellipse([13, 12 + fs / 2 - 5, 23, 12 + fs / 2 + 5], fill=(255, 50, 60, 255))
        d.text((28 if live else 14, 12 + fs / 2), label, font=L.f_mono(fs), fill=acc + (255,), anchor="lm")
    if mode == "talk":
        # voice level bars at the bottom
        n = 18
        for i in range(n):
            v = abs(math.sin(i * 0.9 + seed)) * (0.4 + 0.6 * rng.random())
            x = 12 + i * (w - 24) / n
            hh = 4 + v * h * 0.1
            d.rectangle([x, h - 12 - hh, x + (w - 24) / n - 3, h - 12], fill=acc + (230,))
    if mode == "hurt":
        d.rectangle([w - 92, 10, w - 10, 34], fill=(120, 10, 20, 230))
        d.text((w - 51, 22), "HP 12/55", font=L.f_mono(13), fill=(255, 210, 210, 255), anchor="mm")
        # cracked glass
        cx, cy = w * 0.72, h * 0.3
        for k in range(7):
            ang = k * 0.9 + 0.3
            pts = [(cx, cy)]
            x, y = cx, cy
            for s in range(4):
                ang += rng.uniform(-0.5, 0.5)
                x += math.cos(ang) * w * 0.07
                y += math.sin(ang) * w * 0.07
                pts.append((x, y))
            d.line(pts, fill=(230, 240, 255, 200), width=2)
    if mode == "stationed" and w >= 200:
        d.rectangle([0, h - 40, w, h], fill=(6, 8, 12, 220))
        d.text((12, h - 20), sub or "ON SAFEHOUSE // 12 fps", font=L.f_mono(max(11, w // 24)), fill=acc + (255,), anchor="lm")
    if mode == "dead":
        d.rectangle([0, h * 0.44, w, h * 0.56], fill=(6, 6, 8, 235))
        d.text((w / 2, h / 2), "NO SIGNAL", font=L.f_num(max(18, w // 9)), fill=(220, 220, 225, 255), anchor="mm")
    # bezel
    out = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    od.rounded_rectangle([0, 0, w + 23, h + 23], radius=18, fill=(26, 24, 32, 255), outline=(8, 6, 12, 255), width=3)
    od.rounded_rectangle([5, 5, w + 18, h + 18], radius=15, outline=(60, 56, 72, 255), width=2)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=20, fill=255)
    img.putalpha(m)
    out.alpha_composite(img, (12, 12))
    shm = SL.diag(w, h, 30).point(SL.band_lut(0.2, 0.1, 0.16))
    lay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    lay.putalpha(ImageChops.multiply(shm, m))
    out.alpha_composite(lay, (12, 12))
    od = ImageDraw.Draw(out)
    led = {"idle": (80, 255, 140), "talk": (80, 255, 140), "hurt": (255, 60, 60), "stationed": acc, "dead": (60, 60, 70), "recruit": (255, 214, 64)}[mode]
    od.ellipse([w - 4, h + 4, w + 8, h + 16], fill=led + (255,))
    return out


def dispatch_feed(w, h, seed=3):
    """DISPATCH: no face, ever. A red voice trace on black, the REBEL_CELL red, a slow scan sweep."""
    img = Image.new("RGBA", (w, h), (6, 3, 5, 255))
    d = ImageDraw.Draw(img)
    acc = (232, 20, 30)
    for y in range(0, h, 16):
        d.line([(0, y), (w, y)], fill=(30, 8, 10, 255))
    for k in range(5):
        pts = []
        for x in range(0, w, 3):
            u = x / w
            env = math.sin(math.pi * u) ** 2
            y = h / 2 + env * (h * 0.3 - k * 8) * math.sin(u * 26 + k * 0.9 + seed) * math.cos(u * 7 + k)
            pts.append((x, y))
        d.line(pts, fill=acc + (255 - k * 45,), width=3 if k == 0 else 1)
    img = L.bloom(img, 0.6, 0.4, 8)
    d = ImageDraw.Draw(img)
    d.text((w / 2, 22), "DISPATCH", font=L.f_num(max(18, w // 12)), fill=(255, 90, 90, 255), anchor="mm")
    d.text((w / 2, h - 18), "VOICE ONLY // NO FEED", font=L.f_mono(max(11, w // 26)), fill=(170, 40, 50, 255), anchor="mm")
    yy = np.arange(h)[:, None]
    a = np.asarray(img, np.float32)
    a[..., :3] *= (0.78 + 0.22 * (yy % 3 != 0))[..., None]
    img = Image.fromarray(a.astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    od.rounded_rectangle([0, 0, w + 23, h + 23], radius=18, fill=(40, 10, 14, 255), outline=(8, 6, 12, 255), width=3)
    od.rounded_rectangle([5, 5, w + 18, h + 18], radius=15, outline=(140, 20, 30, 255), width=2)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=20, fill=255)
    img.putalpha(m)
    out.alpha_composite(img, (12, 12))
    return out


def title(canvas, text, sub, col="yellow"):
    sd = L.sticker_word([text], 60, fills=[col], seed=len(text))
    canvas = L.place_sticker(canvas, sd, 60 + len(text) * 15, 62, angle=-1.5)
    d = ImageDraw.Draw(canvas)
    d.text((140 + len(text) * 30, 66), sub, font=L.f_mono(18), fill=(180, 180, 200, 255), anchor="lm")
    return canvas


def bg():
    img = Image.new("RGBA", (L.W, L.H), (11, 10, 16, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, L.H, 4):
        d.line([(0, y), (L.W, y)], fill=(14, 13, 20, 255))
    return img


# ------------------------------------------------------------------ 1. classes
def make_classes():
    img = title(bg(), "OPERATIVES", "8 classes x 3 procedural rookies on the CRT comms feed; variants = skin, hair, jaw, beard + a gear swap")
    bw_, bh_ = 460, 470
    for k, (cid, lab, col, base, role) in enumerate(CLASS):
        cx = 20 + (k % 4) * (bw_ + 16)
        cy = 130 + (k // 4) * (bh_ + 10)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([cx, cy, cx + bw_, cy + bh_], radius=14, fill=(18, 16, 24, 255), outline=tuple(int(c * 0.5) for c in col) + (255,), width=2)
        hero = feed("%s_1" % cid, 270, 300, col, "%s // %s" % (lab, CALLSIGNS[cid][0]), seed=k)
        img = L.paste(img, hero, cx + 10, cy + 10)
        for j in (2, 3):
            v = feed("%s_%d" % (cid, j), 140, 155, col, CALLSIGNS[cid][j - 1], seed=k * 3 + j)
            img = L.paste(img, v, cx + 300, cy + 10 + (j - 2) * 172)
        d = ImageDraw.Draw(img)
        d.text((cx + 16, cy + 340), lab, font=L.f_num(44), fill=col + (255,))
        d.text((cx + 18, cy + 396), ("alt of " + base.upper() + "  //  " if base else "base class  //  ") + role, font=L.f_mono(15), fill=(180, 180, 195, 255))
        d.text((cx + 18, cy + 424), "gear: " + GEAR[cid], font=L.f_mono(14), fill=tuple(int(c * 0.8) for c in col) + (255,))
    L.save(img, "portraits_classes.png")


GEAR = {
    "breaker": "hood + visor bar, class stripe", "wrecker": "respirator + shoulder pads",
    "ghost": "hood/no hood, face mask, eye slits", "phantom": "half face-mask, lilac seam",
    "rigger": "headset, mic, goggles up/down", "overclocker": "slot goggles, heat-sink fins",
    "botnet": "antenna, monocle, 2-3 drones", "hivemind": "hex node circlet + jack",
}


# ------------------------------------------------------------------ 2. states
def stamp_on(im, text, col, angle, size=34, pos=None, seed=4):
    st = L.stamp(text, size, col=col, angle=angle, seed=seed)
    x, y = pos or ((im.width - st.width) // 2, (im.height - st.height) // 2)
    im.alpha_composite(st, (int(x), int(y)))
    return im


def make_states():
    img = title(bg(), "PORTRAIT STATES", "one rookie (RIGGER // SPROCKET), every state the feed can be in")
    col = COL["rigger"]
    cells = [
        ("IDLE", feed("rigger_1", 380, 420, col, "RIGGER // SPROCKET", "idle", 1), "live feed, slow blink, green LED"),
        ("TALKING", feed("state_talk", 380, 420, col, "RIGGER // SPROCKET", "talk", 2), "mouth-open render + voice bars"),
        ("HURT", feed("state_hurt", 380, 420, col, "RIGGER // SPROCKET", "hurt", 3), "HP 25% or less, grimace, red wash + tearing, cracked glass"),
        ("STATIONED", feed("rigger_1", 380, 420, col, "RIGGER // SPROCKET", "stationed", 4, sub="ON LANE 15 RELAY // 12 fps"), "class-colour mono, low frame rate"),
        ("FLATLINED", feed("state_dead", 380, 420, col, "RIGGER // SPROCKET", "dead", 5), "static, NO SIGNAL, crossed out"),
        ("RECRUIT", feed("rigger_2", 380, 420, col, "RIGGER // ROOKIE", "recruit", 6), "grey until hired, hire stamp, 15 Schematics"),
    ]
    for k, (lab, im, note) in enumerate(cells):
        x = 30 + (k % 3) * 630
        y = 130 + (k // 3) * 470
        if lab == "FLATLINED":
            im = im.copy()
            p = SL.Pen(im.size, L.GP_RED, seed=9)
            p.stroke(SL.catmull([(30, 40), (200, 220), (380, 410)], 8), width=12)
            p.stroke(SL.catmull([(380, 40), (210, 230), (30, 410)], 8), width=12)
            im = p.ink(im)
            im = stamp_on(im, "FLATLINED", L.STAMP_RED, -12, 40, pos=(70, 300))
        if lab == "RECRUIT":
            im = im.copy()
            st = L.stamp("HIRE: 15 SCHEMATICS", 26, col=(255, 200, 80), angle=-8, seed=7)
            im.alpha_composite(st, (im.width - st.width - 20, im.height - st.height - 40))
        img = L.drop_shadow(img, im, x, y, blur=12)
        d = ImageDraw.Draw(img)
        d.text((x + 420, y + 30), lab, font=L.f_num(36), fill=(col if lab != "FLATLINED" else (255, 90, 90)) + (255,))
        words = note.split(", ")
        for j, w_ in enumerate(words):
            d.text((x + 422, y + 84 + j * 26), w_, font=L.f_mono(15), fill=(185, 185, 200, 255))
        led = {"IDLE": "LED green", "TALKING": "LED green", "HURT": "LED red", "STATIONED": "LED class colour", "FLATLINED": "LED off", "RECRUIT": "LED amber"}[lab]
        d.text((x + 422, y + 84 + len(words) * 26 + 10), led, font=L.f_mono(15), fill=(120, 140, 150, 255))
    L.caption(img, "triumphant (art_asset B1) = talking render + gold rim + the feed's bloom up; deferred to the dedicated portrait pass", x=24, y=1068, size=16)
    L.save(img, "portrait_states.png")


# ------------------------------------------------------------------ 3. contexts
CREW = [("rigger_1", "rigger", "SPROCKET", 2, "41/55", "READY"), ("ghost_2", "ghost", "WREN", 1, "50/50", "ON LANE 15 RELAY"),
        ("breaker_3", "breaker", "SAFFRON", 0, "60/60", "READY"), ("botnet_1", "botnet", "SWARM", 1, "--", "FLATLINED")]


def roster():
    c = L.CRT(700, 540, L.CYAN, "CREW ROSTER", tag="CYBERDECK HQ", seed=81)
    y = 56
    for name, cid, call, rank, hp, st in CREW:
        mode = "dead" if st == "FLATLINED" else ("stationed" if st.startswith("ON") else "idle")
        f = feed(name, 84, 90, COL[cid], None, mode, seed=y)
        c.paste(f, 16, y)
        col = COL[cid]
        c.text((140, y + 8), call, 28, (255, 255, 255) if mode != "dead" else (120, 120, 130), fnt=L.f_num(32))
        c.text((140, y + 50), cid.upper() + "  //  RANK %d" % rank, 16, col if mode != "dead" else (110, 110, 120))
        c.text((140, y + 76), "HP " + hp, 16, (150, 200, 220) if mode != "dead" else (110, 110, 120))
        scol = {"READY": (120, 255, 150), "FLATLINED": (255, 90, 90)}.get(st, col)
        c.text((680, y + 14), st, 17, scol, anchor="ra")
        if mode == "dead":
            c.d.line([(136, y + 28), (360, y + 28)], fill=(255, 90, 90, 255), width=3)
        y += 118
    return c.finish()


def photo_print(name, size, warm=True, seed=1):
    """The bust as a printed surveillance photo: flat backdrop, halftone-ish grain, desaturated."""
    w, h = size
    ph = Image.new("RGBA", (w, h), (120, 124, 120, 255) if warm else (90, 96, 104, 255))
    d = ImageDraw.Draw(ph)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(150 - 50 * k), int(150 - 48 * k), int(142 - 40 * k), 255))
    b = bust(name)
    bi = b.resize((int(w * 1.05), int(w * 1.05 * b.height / b.width)), Image.LANCZOS)
    ph.alpha_composite(bi, ((w - bi.width) // 2, h - bi.height + int(h * 0.1)))
    ph = ImageEnhance.Color(ph.convert("RGB")).enhance(0.45)
    a = np.asarray(ph, np.float32)
    a = a * np.array([1.05, 1.0, 0.88]) if warm else a
    n = np.random.default_rng(seed).normal(0, 9, a.shape[:2])[..., None]
    a = np.clip(a + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def paperclip():
    im = Image.new("RGBA", (44, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, 40, 116], radius=18, outline=(170, 175, 185, 255), width=5)
    d.rounded_rectangle([12, 22, 32, 100], radius=10, outline=(200, 205, 215, 255), width=4)
    return im


def dossier():
    w, h = 640, 520
    pp = L.paper(w, h, seed=31)
    d = ImageDraw.Draw(pp)
    d.text((30, 26), "MERIDIAN FREIGHT  //  LOSS PREVENTION", font=L.font(L.ANTON, 26), fill=(180, 80, 10, 255))
    d.line([(30, 66), (w - 30, 66)], fill=(180, 80, 10, 255), width=3)
    d.text((30, 80), "PERSON OF INTEREST  //  FILE 0419-K", font=L.font(L.TYPE_B, 18), fill=L.PAPER_INK + (255,))
    ph = photo_print("rigger_1", (210, 250), seed=3)
    ImageDraw.Draw(ph).rectangle([0, 0, 209, 249], outline=(250, 250, 245, 255), width=8)
    pp = L.drop_shadow(pp, L.rotate_rgba(ph, -3), 34, 120, blur=6, off=(4, 6), op=0.5)
    pp.alpha_composite(L.rotate_rgba(paperclip(), 8), (60, 96))
    rows = [("ALIAS", "SPROCKET"), ("ROLE", "rigger (RAM)"), ("SEEN", "Lane 15 depot, 03:12"),
            ("ASSOC.", "REBEL_CELL"), ("THREAT", "moderate"), ("ACTION", "flag on sight")]
    for k, (a_, b_) in enumerate(rows):
        d = ImageDraw.Draw(pp)
        d.text((290, 130 + k * 40), a_, font=L.font(L.TYPE_B, 17), fill=(90, 86, 90, 255))
        d.text((390, 130 + k * 40), b_, font=L.font(L.TYPE, 18), fill=L.PAPER_INK + (255,))
    st = L.stamp("FLAGGED", 34, angle=-9, seed=6)
    pp.alpha_composite(st, (360, 400))
    p = SL.Pen(pp.size, L.GP_RED, seed=4)
    p.circle(140, 245, 110, 130, width=7)
    pp = p.ink(pp, shadow=0.3)
    return pp


def polaroid(name, caption, w=230, seed=1, dead=False):
    ph = photo_print(name, (w - 24, w - 24), warm=True, seed=seed)
    if dead:
        g = ImageOps.grayscale(ph.convert("RGB")).convert("RGBA")
        ph = g
    card = Image.new("RGBA", (w, int(w * 1.2)), (246, 244, 236, 255))
    card.alpha_composite(ph, (12, 12))
    d = ImageDraw.Draw(card)
    d.text((w / 2, w + 12), caption, font=L.font(L.PEN_FONT, 22), fill=(40, 40, 60, 255), anchor="mm")
    d.rectangle([0, 0, w - 1, card.height - 1], outline=(200, 196, 186, 255), width=1)
    if dead:
        p = SL.Pen(card.size, L.GP_RED, seed=seed)
        p.stroke(SL.catmull([(20, 20), (w / 2, w / 2), (w - 20, w - 20)], 6), width=8)
        p.stroke(SL.catmull([(w - 20, 20), (w / 2, w / 2 + 6), (20, w - 20)], 6), width=8)
        card = p.ink(card, shadow=0.3)
    return card


def audit():
    w, h = 640, 520
    pp = L.paper(w, h, seed=41, tint=(226, 222, 210))
    d = ImageDraw.Draw(pp)
    d.text((30, 24), "CAMPAIGN AUDIT  //  CELL PERSONNEL", font=L.font(L.ANTON, 26), fill=(40, 60, 90, 255))
    d.line([(30, 64), (w - 30, 64)], fill=(40, 60, 90, 255), width=3)
    pols = [("ghost_2", "WREN  r1", False, -6), ("breaker_3", "SAFFRON  r0", False, 4), ("botnet_1", "SWARM  KIA", True, -3)]
    for k, (n, cap, dead, ang) in enumerate(pols):
        pl = L.rotate_rgba(polaroid(n, cap, 180, seed=k + 2, dead=dead), ang)
        pp = L.drop_shadow(pp, pl, 26 + k * 200, 100 + (k % 2) * 24, blur=6, off=(4, 6), op=0.5)
    # auditor post-it
    pi = Image.new("RGBA", (200, 150), (255, 236, 120, 255))
    dpi = ImageDraw.Draw(pi)
    for j, ln in enumerate(["1 lost on Lane 15.", "replace from", "recruit pool?"]):
        dpi.text((14, 18 + j * 34), ln, font=L.font(L.PEN_FONT, 24), fill=(40, 40, 70, 255))
    pp = L.drop_shadow(pp, L.rotate_rgba(pi, 5), 420, 350, blur=5, off=(3, 5), op=0.4)
    return pp


def contacts_panel():
    w, h = 700, 420
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    f1 = feed("contact_fixer", 200, 222, (92, 225, 255), "FIXER", seed=11)
    f2 = feed("contact_merc_talk", 200, 222, (255, 190, 80), "STREET MERC", "talk", seed=12)
    f3 = dispatch_feed(200, 222)
    for k, f in enumerate((f1, f2, f3)):
        c.alpha_composite(f, (k * 234, 0))
    d = ImageDraw.Draw(c)
    notes = [("FIXER", "contact: cyan feed,", "glasses, lapels"), ("STREET MERC", "amber feed, cap,", "scar, straps"), ("DISPATCH", "never a face:", "red voice trace")]
    for k, (a_, b_, c_) in enumerate(notes):
        d.text((k * 234 + 10, 262), a_, font=L.f_num(26), fill=(230, 230, 240, 255))
        d.text((k * 234 + 10, 298), b_, font=L.f_mono(14), fill=(170, 170, 185, 255))
        d.text((k * 234 + 10, 320), c_, font=L.f_mono(14), fill=(170, 170, 185, 255))
    return c


def make_contexts():
    img = title(bg(), "PORTRAIT CONTEXTS", "the same bust as a live feed (Cell systems) and as a print (corp paper)")
    r = roster()
    img = L.crt_glow_under(img, (40, 140, 740, 680), L.CYAN, 0.12)
    img = L.paste(img, r, 40, 130)
    dz = dossier()
    dz = L.rotate_rgba(dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS), 2)
    img = L.drop_shadow(img, dz, 800, 130, blur=14)
    ad = audit()
    ad = L.rotate_rgba(ad.resize((int(ad.width * 0.86), int(ad.height * 0.86)), Image.LANCZOS), -2)
    img = L.drop_shadow(img, ad, 1330, 600, blur=14)
    cp = contacts_panel()
    img = L.paste(img, cp, 40, 704)
    d = ImageDraw.Draw(img)
    labs = [(40, 692, "CREW ROSTER (CRT): live feeds; stationed tinted, flatlined static + struck"),
            (800, 120, "CORP DOSSIER: photo print, paper-clipped, red pencil ring"),
            (1340, 594, "CAMPAIGN AUDIT: polaroids, KIA crossed out")]
    for x, y, t in labs:
        d.text((x, y), t, font=L.f_mono(15), fill=(255, 214, 64, 255), anchor="ls")
    d.text((40, 1074), "CONTACTS: fixer / street merc on the same feed, their own accent; DISPATCH is voice only", font=L.f_mono(15), fill=(255, 214, 64, 255), anchor="ls")
    L.save(img, "portrait_contexts.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("classes", "all"):
        make_classes()
    if what in ("states", "all"):
        make_states()
    if what in ("contexts", "all"):
        make_contexts()
