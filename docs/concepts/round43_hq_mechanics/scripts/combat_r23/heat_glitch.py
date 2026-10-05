"""Round 18 / 3: screen-wide HEAT glitch on the D4 combat screen (ART_FEEDBACK_R2 item 11).

One post effect, four Heat bands (art_asset A3: COOL 0-24, NOTICED 25-49, FLAGGED 50-74, HUNTED 75+).
Each band adds a layer; every burst is brief (<= 320 ms) and periodic, so values are never hidden:
the HUD, the hand and the overlay stickers sit ABOVE the glitch layer, and the wheels' read blocks are
masked to 35 %. Last segment: Options > HEAT GLITCH switched off (a static edge tint stays).

python heat_glitch.py          # heat_glitch.gif + heat_glitch_storyboard.png
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import plates as P
import make_combat as MC
import fxlib as FX
from fxlib import seg, lerp, ease_out_cubic, ease_in_out
from slicelib import f_num, f_ui, f_mono

OUT = P.OUT
W, H = 1920, 1080
CORP = (255, 120, 48)  # Meridian orange: the corporation that is hunting you

# band table (would live in content config): heat, word, period s, burst ms, layers
BANDS = [
    dict(heat=12, word="COOL", period=3.2, burst=80, flicker=1.0),
    dict(heat=31, word="NOTICED", period=2.6, burst=160, flicker=1.0, tears=10, tear_dx=18, tear_split=4),
    dict(heat=58, word="FLAGGED", period=2.0, burst=260, flicker=1.0, tears=12, tear_dx=26, tear_split=5, roll=1, blocks=48),
    dict(heat=82, word="HUNTED", period=1.6, burst=320, flicker=1.0, tears=18, tear_dx=40, tear_split=7, roll=1, blocks=96,
         slip=14, split=6, scan=0.07, edge=0.22),
]
SEG_MS = 2400        # each band's slot in the clip
BURST_AT = 920       # burst start inside a slot (ms)
STEP = 80             # a glitch state holds for 80 ms (2 frames at 25 fps)
OFF_SLOT = 4         # slot 5: Options toggle -> OFF, at HUNTED


# ------------------------------------------------------------------ masks
def protect_mask():
    """1 where values must stay readable (the wheels' slice discs); the glitch is cut to 35 % there."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for c, r in ((P.PLAYER["c"], P.PLAYER["r"]), (P.BOSS["c"], P.BOSS["r"])):
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(10))
    return np.asarray(m, np.float32)[..., None] / 255


PROTECT = None


# ------------------------------------------------------------------ glitch ops (numpy, uint8 HxWx3)
def flicker(a, k, rng):
    out = (a.astype(np.float32) * (1 - 0.07 * k)).astype(np.uint8)
    for _ in range(2):
        y = int(rng.integers(0, H - 3))
        out[y:y + 2] = np.roll(out[y:y + 2], int(rng.integers(1, 3)), axis=1)
    return out


def tears(a, rng, n, maxdx, split):
    out = a.copy()
    for _ in range(n):
        h = int(rng.integers(4, 44))
        y = int(rng.integers(0, H - h))
        dx = int(rng.integers(-maxdx, maxdx + 1))
        band = np.roll(a[y:y + h], dx, axis=1)
        band[..., 0] = np.roll(band[..., 0], -split, axis=1)
        band[..., 2] = np.roll(band[..., 2], split, axis=1)
        out[y:y + h] = band
    return out


def roll(a, phase):
    """A rolling bright band with tight scan lines (vertical hold drifting), top -> bottom."""
    out = a.astype(np.float32)
    cy = phase * (H + 160) - 80
    yy = np.arange(H, dtype=np.float32)
    w = np.exp(-((yy - cy) / 70) ** 2)
    lines = np.where((np.arange(H) % 3) == 0, 0.72, 1.0)
    gain = (1 + 0.22 * w) * (1 - (1 - lines) * w)
    out *= gain[:, None, None]
    sh = (np.sin(yy / 7) * 6 * w).astype(int)
    for y in np.nonzero(w > 0.3)[0]:
        out[y] = np.roll(out[y], sh[y], axis=0)
    return np.clip(out, 0, 255).astype(np.uint8)


def blocks(a, rng, n):
    """Block corruption: macroblocks copied from elsewhere, posterised and pulled to the corp colour."""
    out = a.copy()
    for _ in range(n):
        bw = int(rng.choice([16, 24, 32, 48, 64]))
        bh = int(rng.choice([8, 16, 16, 24, 32]))
        x, y = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
        sx = int(np.clip(x + rng.integers(-120, 121), 0, W - bw))
        sy = int(np.clip(y + rng.integers(-40, 41), 0, H - bh))
        blk = a[sy:sy + bh, sx:sx + bw].astype(np.float32)
        blk = np.floor(blk / 64) * 64 + 32 + 30
        t = 0.5 if rng.random() < 0.8 else 0.0
        blk = blk * (1 - t) + np.array(CORP, np.float32) * t
        out[y:y + bh, x:x + bw] = np.clip(blk, 0, 255).astype(np.uint8)
    return out


def slip(a, dy):
    return np.roll(a, dy, axis=0)


def split(a, s):
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], -s, axis=1)
    out[..., 2] = np.roll(a[..., 2], s, axis=1)
    return out


def scanlines(a, k):
    f = np.where((np.arange(H) % 3) == 0, 1 - k, 1.0).astype(np.float32)
    return (a.astype(np.float32) * f[:, None, None]).astype(np.uint8)


_EDGE = {}


def edge_tint(a, k):
    """Static corp-colour edge glow: the Heat level is still readable with the glitch switched off."""
    if "m" not in _EDGE:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        q = np.maximum(np.abs(xx - W / 2) / (W / 2), np.abs(yy - H / 2) / (H / 2))
        _EDGE["m"] = np.clip((q - 0.78) / 0.22, 0, 1) ** 1.6
    m = _EDGE["m"][..., None] * k
    return np.clip(a.astype(np.float32) * (1 - m) + np.array(CORP, np.float32) * m, 0, 255).astype(np.uint8)


def glitch(a, band, age, seed):
    """Apply one band's burst at `age` ms into it (age < 0 or > burst: ambient layers only)."""
    b = BANDS[band]
    rng = np.random.default_rng(seed)
    out = a
    if b.get("scan"):
        out = scanlines(out, b["scan"])
    if 0 <= age <= b["burst"]:
        q = age / b["burst"]
        env = math.sin(math.pi * min(1.0, q * 1.15))  # up fast, out
        out = flicker(out, env * b["flicker"], rng)
        if b.get("tears"):
            out = tears(out, rng, max(1, int(b["tears"] * env)), int(b["tear_dx"] * env) + 2, max(1, int(b["tear_split"] * env)))
        if b.get("roll"):
            out = roll(out, q)
        if b.get("blocks") and 0.15 < q < 0.85:
            out = blocks(out, rng, int(b["blocks"] * env))
        if b.get("slip") and 0.3 < q < 0.5:
            out = slip(out, b["slip"])
        if b.get("split") and q < 0.45:
            out = split(out, int(b["split"] * env) + 1)
    if b.get("edge"):
        out = edge_tint(out, b["edge"])
    return out


# ------------------------------------------------------------------ HUD additions
def heat_chip(img, band):
    """Compact combat Heat poster (art_asset: 'HEAT', value, bar with 3 thresholds, band word)."""
    b = BANDS[band]
    d = ImageDraw.Draw(img)
    x, y, w = 760, 84, 400
    d.rounded_rectangle([x, y, x + w, y + 44], radius=8, fill=(10, 9, 15, 235), outline=CORP + (200,), width=2)
    d.text((x + 14, y + 4), "HEAT", font=f_num(30), fill=(255, 255, 255, 255))
    d.text((x + 82, y + 4), "%d" % b["heat"], font=f_num(30), fill=CORP + (255,))
    bx0, bx1, by = x + 130, x + 290, y + 22
    d.rounded_rectangle([bx0, by - 6, bx1, by + 6], radius=4, fill=(40, 36, 46, 255))
    d.rounded_rectangle([bx0, by - 6, bx0 + (bx1 - bx0) * b["heat"] / 100, by + 6], radius=4, fill=CORP + (255,))
    for th in (25, 50, 75):
        tx = bx0 + (bx1 - bx0) * th / 100
        d.line([(tx, by - 10), (tx, by + 10)], fill=(255, 255, 255, 255), width=2)
    d.text((x + 302, y + 10), b["word"], font=f_ui(20, b"Bold Condensed"), fill=CORP + (255,))


def options_panel(img, t_in, on):
    """Settings > Accessibility snippet: the HEAT GLITCH switch (with reduce effects / motion)."""
    d = ImageDraw.Draw(img)
    x, y, w, h = 690, 300, 540, 300
    a = ease_out_cubic(seg(t_in, 0, 160))
    if a <= 0:
        return None
    y += int(30 * (1 - a))
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=(12, 11, 18, int(245 * a)), outline=(92, 225, 255, int(255 * a)), width=2)
    d.text((x + 22, y + 14), "SETTINGS  //  ACCESSIBILITY", font=f_ui(24, b"Bold Condensed"), fill=(255, 255, 255, int(255 * a)))
    rows = [("REDUCE EFFECTS", False), ("REDUCE MOTION", False), ("FLASH LIMITER", True), ("HEAT GLITCH", on)]
    sw = None
    for i, (lab, val) in enumerate(rows):
        yy = y + 70 + i * 54
        hl = lab == "HEAT GLITCH"
        if hl:
            d.rounded_rectangle([x + 12, yy - 8, x + w - 12, yy + 40], radius=8, fill=(30, 26, 40, int(255 * a)))
        d.text((x + 26, yy), lab, font=f_ui(24, b"Bold SemiCondensed"), fill=(235, 235, 245, int(255 * a)))
        if hl:
            d.text((x + 26 + 170, yy + 6), "screen-wide Heat distortion", font=f_mono(13, False), fill=(160, 160, 176, int(255 * a)))
        sx = x + w - 110
        d.rounded_rectangle([sx, yy, sx + 80, yy + 32], radius=16, fill=((92, 225, 255) if val else (60, 58, 70)) + (int(255 * a),))
        kx = sx + 50 if val else sx + 4
        d.ellipse([kx, yy + 3, kx + 26, yy + 29], fill=(250, 250, 250, int(255 * a)))
        d.text((sx - 46, yy + 4), "ON" if val else "OFF", font=f_ui(20, b"Bold Condensed"), fill=(200, 200, 214, int(255 * a)))
        if hl:
            sw = (sx + 40, yy + 16)
    return sw


def caption(img, text):
    d = ImageDraw.Draw(img)
    f = P.mono(28)
    x, y = 30, 214
    tw = f.getlength(text)
    d.rounded_rectangle([x, y, x + tw + 24, y + 42], radius=6, fill=(10, 9, 15, 225), outline=(255, 214, 64, 255), width=2)
    d.text((x + 12, y + 6), text, font=f, fill=(255, 214, 64, 255))


# ------------------------------------------------------------------ frame
_BASE = {}


def world():
    if "w" not in _BASE:
        _BASE["w"] = np.asarray(P.hp_scene().convert("RGB")).copy()
    return _BASE["w"]


def ui_layer():
    """Everything drawn above the glitch: HUD, hand, overlay stickers (transparent background)."""
    if "ui" not in _BASE:
        ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        P.hud(ui)
        P.stickers(ui)
        from card_play import card_face
        for i in range(5):
            x, y, r = P.hand_slot(i, 5)
            FX.place(ui, card_face(i, 144, 192), x, y + 96, 1, 1, r, shadow=((3, 5), 3, 0.55))
        _BASE["ui"] = ui
    return _BASE["ui"]


def frame(t, keep=None):
    global PROTECT
    if PROTECT is None:
        PROTECT = protect_mask()
    slot = min(OFF_SLOT, int(t // SEG_MS))
    lt = t - slot * SEG_MS
    a = world()
    if slot < OFF_SLOT:
        band = slot
        age = lt - BURST_AT
        age = (age // STEP) * STEP if age >= 0 else age  # glitch states hold 2 frames (steppy, cheaper)
        g = glitch(a, band, age, seed=1000 * band + int(max(0, age) // STEP))
        k = 0.65 * PROTECT
        out = (a.astype(np.float32) * k + g.astype(np.float32) * (1 - k)).astype(np.uint8)
        cap = "HEAT %d  %s  -  burst %d ms every %.1f s" % (BANDS[band]["heat"], BANDS[band]["word"], BANDS[band]["burst"], BANDS[band]["period"])
    else:
        band = 3
        on = lt < 900
        if on:  # still glitching until the switch flips
            age = -1  # between bursts: ambient layers only until the switch flips
            age = (age // STEP) * STEP if age >= 0 else age
            g = glitch(a, band, age, seed=7000 + int(max(0, age) // STEP))
            k = 0.65 * PROTECT
            out = (a.astype(np.float32) * k + g.astype(np.float32) * (1 - k)).astype(np.uint8)
        else:
            out = edge_tint(a, 0.22)  # OFF: the static edge tint remains, no motion
        cap = "OPTIONS: HEAT GLITCH %s  -  HEAT 82 HUNTED" % ("ON" if on else "OFF (static edge tint only)")
    img = Image.fromarray(out).convert("RGBA")
    img.alpha_composite(ui_layer())
    heat_chip(img, band)
    if slot == OFF_SLOT:
        sw = options_panel(img, lt - 450, lt < 900) if lt < 1440 else None  # panel closes
        if sw is not None and lt < 1500:
            cx = lerp(sw[0] + 140, sw[0], ease_in_out(seg(lt, 450, 820)))
            cy = lerp(sw[1] + 90, sw[1], ease_in_out(seg(lt, 450, 820)))
            FX.cursor(img, cx, cy, 860 <= lt < 960)
        if lt >= 1500:
            pass
    caption(img, cap)
    return img


KEYS = [
    (BURST_AT + 40, "01 COOL  (0-24)", ["Luminance dip <= 7 % + two 2 px line", "jitters; 80 ms every 3.2 s."]),
    (SEG_MS + BURST_AT + 80, "02 NOTICED  (25-49)", ["+ chromatic tears: 10 bands slip <= 18 px", "with 4 px RGB split; 160 ms / 2.6 s."]),
    (2 * SEG_MS + BURST_AT + 80, "03 FLAGGED: ROLL", ["+ scanline roll: bright band with 3 px", "lines runs top->bottom in 260 ms."]),
    (2 * SEG_MS + BURST_AT + 160, "04 FLAGGED: BLOCKS", ["+ 48 macroblocks copied, posterised,", "pulled to the corp colour; 2.0 s period."]),
    (3 * SEG_MS + BURST_AT + 120, "05 HUNTED: SLIP + SPLIT", ["+ 14 px vertical hold slip, 6 px RGB", "split, 96 blocks; 320 ms / 1.6 s."]),
    (3 * SEG_MS + BURST_AT + 600, "06 HUNTED: BETWEEN", ["Ambient only: 7 % scanlines + corp edge", "tint; every value fully readable."]),
    (4 * SEG_MS + 760, "07 OPTIONS", ["Settings > HEAT GLITCH (off switch, beside", "reduce effects / motion, flash limiter)."]),
    (4 * SEG_MS + 1600, "08 GLITCH OFF", ["No motion at any Heat: static edge tint", "+ the HEAT chip carry the level."]),
]
T_END = 5 * SEG_MS


def main():
    frames, durs = [], []
    keyt = {k[0]: k for k in KEYS}
    crops = {}
    CROP = (700, 60, 1700, 640)
    for t in range(0, T_END, int(FX.DT)):
        img = frame(t)
        if t in keyt:
            crops[t] = img.convert("RGB").crop(CROP if t < 4 * SEG_MS else (460, 60, 1460, 640))
        frames.append(img.convert("RGB").resize((960, 540), Image.LANCZOS))
        durs.append(int(FX.DT))
        if t % 2000 == 0:
            print("t", t, flush=True)
    for k in keyt:
        assert k in crops, k
    size = FX.save_gif(frames, durs, os.path.join(OUT, "heat_glitch.gif"))
    print("gif", size // 1024, "KB", flush=True)
    cells = [(crops[t], lab, "%d ms" % t, caps) for t, lab, caps in KEYS]
    FX.storyboard(cells, os.path.join(OUT, "heat_glitch_storyboard.png"),
                  "HEAT GLITCH  -  one post shader, four Heat bands, an Options switch",
                  "1:1 crops (1000x580) of the 1920x1080 D4 combat screen. Each band adds to the one before. HUD, hand and stickers are drawn above the glitch layer; wheel discs get 35 %.",
                  cols=4,
                  note_lines=["bursts are periodic and short (80-320 ms) and never on a value: CanvasLayer order = world (city, wheels) | HEAT GLITCH post | HUD + hand + stickers",
                              "reduce effects / flash limiter: only the slowest layer remains (scanline roll off, no RGB split, no slip); HEAT GLITCH off: static edge tint only."])
    print("done", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "test":
        for a in sys.argv[2:]:
            frame(int(a)).convert("RGB").save(os.path.join(P.SCR, "hg_%s.png" % a))
            print("test", a, flush=True)
    else:
        main()
