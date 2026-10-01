"""04_lifecycle.png -- SEND IT: appear (brush writes it), idle (ink bleeds + dries), leave (wet wash-off)."""
import sys
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inklib as K
import glyphs as Gl
import scenes as S
import render_combat as RC

CROP = (1488, 700, 1920, 1080)   # 1x region around the verb (432 x 380)


def overlay(state):
    """Verb overlay as RGBA (transparent elsewhere) at SS for one lifecycle state."""
    Lv = S.Layers()
    kind, v = state
    if kind == "appear":
        RC.paint_verb(Lv, cut_frac=v)
        return Lv.compose(Image.new("RGBA", (K.CW, K.CH), (0, 0, 0, 0)), sheen=1.0, bleed=0.0)
    RC.paint_verb(Lv)
    if kind == "leave":
        Lv.seals = []
    if kind == "idle":
        return Lv.compose(Image.new("RGBA", (K.CW, K.CH), (0, 0, 0, 0)), sheen=0.9 * (1 - v), bleed=0.15 + 0.85 * v,
                          matte=v)
    return Lv.compose(Image.new("RGBA", (K.CW, K.CH), (0, 0, 0, 0)), sheen=0.0, bleed=1.0, matte=1.0)


def crop_ss(img):
    return img.crop(tuple(int(c * K.SS) for c in CROP))


def wipe(O, f, seed=3):
    """Wet wash-off: a diagonal wet front sweeps left->right; behind it the ink is dragged into a
    diluted streak with drips; at the front a glossy bead of water."""
    rng = random.Random(seed)
    w, h = O.size
    S2 = K.SS
    xf = int((-0.15 + 1.3 * f) * w)
    # front mask (1 = already washed), slanted, with a ragged wet edge
    M = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(M)
    poly = [(0, 0)]
    for i in range(0, h + 1, 6 * S2):
        poly.append((xf + 0.22 * (i - h / 2) + rng.gauss(0, 4) * S2, i))
    poly.append((0, h))
    d.polygon(poly, fill=255)
    M = K.blur(M, 3 * S2)
    a = O.getchannel("A")
    keep = O.copy()
    keep.putalpha(ImageChops.multiply(a, ImageChops.invert(M)))
    # smear: the washed part dragged along the wipe direction, thinning out
    streak = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    washed = O.copy()
    washed.putalpha(ImageChops.multiply(a, M))
    n = 30
    for k in range(n):
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer.paste(washed, (int(k * 3.4 * S2), int(k * 0.8 * S2)))
        la = layer.getchannel("A")
        layer.putalpha(K.scale_l(la, 0.085 * (1 - k / n) + 0.01))
        streak.alpha_composite(layer)
    # drips running down from the washed zone
    da = streak.getchannel("A")
    drip = Image.new("L", (w, h), 0)
    dd = ImageDraw.Draw(drip)
    for _ in range(18):
        x = rng.uniform(0, min(w, xf + 40 * S2))
        y0 = rng.uniform(0.35, 0.8) * h
        if da.getpixel((int(min(w - 1, max(0, x))), int(y0))) < 30:
            continue
        ln = rng.uniform(25, 90) * S2
        wd = rng.uniform(1.5, 4) * S2
        dd.line([(x, y0), (x + rng.uniform(-2, 2) * S2, y0 + ln)], fill=150, width=int(wd))
        dd.ellipse((x - wd, y0 + ln - wd * 0.6, x + wd, y0 + ln + wd * 1.4), fill=190)
    drip = K.blur(drip, 0.8 * S2)
    dripimg = Image.new("RGBA", (w, h), K.PINK_WASH_DEEP + (0,))
    dripimg.putalpha(K.scale_l(drip, 0.55))
    # glossy water bead along the front
    bead = Image.new("L", (w, h), 0)
    bd = ImageDraw.Draw(bead)
    pts = [(xf + 0.22 * (i - h / 2) + 3 * S2, i) for i in range(0, h + 1, 8 * S2)]
    bd.line(pts, fill=255, width=int(5 * S2))
    bead = K.blur(bead, 2 * S2)
    hl = Image.new("L", (w, h), 0)
    ImageDraw.Draw(hl).line([(x - 2 * S2, y) for x, y in pts], fill=255, width=int(1.5 * S2))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(streak)
    out.alpha_composite(dripimg)
    out.alpha_composite(keep)
    beadimg = Image.new("RGBA", (w, h), (120, 30, 80, 0))
    beadimg.putalpha(K.scale_l(ImageChops.multiply(bead, K.scale_l(ImageChops.lighter(da, a), 1.0, 60)), 0.35))
    out.alpha_composite(beadimg)
    hli = Image.new("RGBA", (w, h), (255, 240, 250, 0))
    hli.putalpha(K.scale_l(ImageChops.multiply(K.blur(hl, 0.6 * S2), K.ramp(K.blur(a, 3 * S2), 120, 255)), 0.45))
    out.alpha_composite(hli)
    return out


def frame(static_crop, state, size):
    O = crop_ss(overlay(state if state[0] != "leave" else ("leave", 0)))
    if state[0] == "leave":
        O = wipe(O, state[1])
    im = static_crop.copy()
    im.alpha_composite(O)
    return im.convert("RGB").resize(size, Image.LANCZOS)


def font(sz, bold=True):
    f = ImageFont.truetype(S.SYS_FONT, sz)
    try:
        f.set_variation_by_name("Bold" if bold else "Light")
    except Exception:
        pass
    return f


def render(out_path):
    base = RC.machine_layer(K.load_base(S.BASE_COMBAT))
    static = RC.static_layers().compose(base)
    sc = crop_ss(static)
    W, H = 1920, 1080
    rng = random.Random(9)
    bg = K.noise(W, H, 90, rng).point(lambda v: 16 + v // 40)
    canvas = Image.merge("RGB", (bg.point(lambda v: v + 2), bg, bg.point(lambda v: v + 5)))
    d = ImageDraw.Draw(canvas)
    d.text((34, 22), "SEND IT", font=font(34), fill=(236, 230, 220))
    d.text((176, 31), "verb lifecycle  //  sumi ink + watercolour overlay", font=font(22, False), fill=(150, 144, 150))
    PW, PH = 600, 528
    xs = [30, 660, 1290]
    phases = [
        ("01  APPEAR", "the brush writes it: wash blooms first, then each stroke, wet sheen on the pools",
         "0.55 s  //  wash 0.07 s, then strokes in writing order, ease-out per stroke",
         ("appear", 0.62), [("appear", 0.18), ("appear", 0.42), ("appear", 0.82)]),
        ("02  IDLE", "waiting: ink feathers out into the wash and the shine dries to matte",
         "4 s settle, then holds  //  bleed halo creeps, sheen fades, nothing loops harshly",
         ("idle", 1.0), [("idle", 0.0), ("idle", 0.45), ("idle", 1.0)]),
        ("03  LEAVE", "page turns: a wet streak washes the ink off, drips run, the bead leads",
         "0.35 s  //  front sweeps left to right, drips trail for 0.2 s after",
         ("leave", 0.52), [("leave", 0.2), ("leave", 0.62), ("leave", 0.95)]),
    ]
    for i, (title, sub, timing, main, thumbs) in enumerate(phases):
        x = xs[i]
        img = frame(sc, main, (PW, PH))
        canvas.paste(img, (x, 72))
        d.rectangle((x - 1, 71, x + PW, 72 + PH), outline=(60, 56, 62))
        d.text((x, 612), title, font=font(28), fill=(255, 92, 168))
        d.text((x, 650), sub, font=font(17, False), fill=(214, 208, 204))
        d.text((x, 674), timing, font=font(15, False), fill=(140, 134, 140))
        for j, st in enumerate(thumbs):
            t = frame(sc, st, (190, 167))
            tx = x + j * 205
            canvas.paste(t, (tx, 704))
            d.rectangle((tx - 1, 703, tx + 190, 704 + 167), outline=(60, 56, 62))
            d.text((tx + 4, 875), f"{['t0', 't1', 't2'][j]}", font=font(14, False), fill=(120, 114, 120))
    # stamp vocabulary: original hanko designs
    d.text((34, 925), "STAMP VOCABULARY", font=font(22), fill=(236, 230, 220))
    d.text((34, 954), "carved seals, stamped once,", font=font(16, False), fill=(150, 144, 150))
    d.text((34, 974), "never animated beyond the press", font=font(16, False), fill=(150, 144, 150))
    seals = [
        (Gl.seal_patch(["VIC", "TORY"], 120, 120, 301), "VICTORY", -4),
        (Gl.seal_patch(["FLAGGED"], 230, 58, 302), "FLAGGED", 3),
        (Gl.seal_patch(["RAID", "ED"], 120, 120, 303, negative=False, border=0.08), "RAIDED", 6),
        (Gl.seal_patch(["OK"], 96, 96, 304, shape="round", negative=False, border=0.09), "OK", -8),
        (Gl.seal_patch(["SOLD"], 96, 96, 305, shape="round"), "SOLD", 5),
        (Gl.seal_patch(["CE", "LL"], 96, 96, 306), "CELL (signature)", -3),
    ]
    rots = [p.rotate(-ang, resample=Image.BICUBIC, expand=True) for p, _, ang in seals]
    total = sum(r.width // K.SS for r in rots) + 70 * (len(rots) - 1)
    sx = 420 + (1440 - total) // 2
    paper = K.paper_patch(1480, 150, 307, fibre=0.8)
    pp = paper.resize((paper.width // K.SS, paper.height // K.SS), Image.LANCZOS)
    cv = canvas.convert("RGBA")
    cv.alpha_composite(pp, (380 - 14, 908 - 14))
    for patch, name, ang in seals:
        p = patch.rotate(-ang, resample=Image.BICUBIC, expand=True)
        p = p.resize((p.width // K.SS, p.height // K.SS), Image.LANCZOS)
        cy = 975
        cv.alpha_composite(p, (int(sx), int(cy - p.height / 2)))
        ImageDraw.Draw(cv).text((sx, 1040), name, font=font(14, False), fill=(90, 80, 84))
        sx += p.width + 70
    cv.convert("RGB").save(out_path)


if __name__ == "__main__":
    render(os.path.join(S.OUT, "04_lifecycle.png"))
