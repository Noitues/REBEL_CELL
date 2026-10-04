"""Round 39 hub states on top of hubkit (round 38 D4 hub):
  phantom echo trail (moving after-images), enemy BREACHED as a 1-turn timer state
  (online -> hit -> timer runs down -> reboot), and the player DEFEAT (core turns to bits and drains).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import slicelib as SL
import hubkit as H
from slicelib import f_num, f_ui, f_mono

INK = H.INK
HARM = H.HARM


def _disc_layer(hub, size, ss, t, ring_segs=None, breached=False):
    """Render a hub close-up layer at master scale (no resize)."""
    S = int((H.RING_OUT + 14) * 2 * ss)
    c = S / 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if ring_segs:
        H.draw_ring(im, (c, c), ss, hub["acc"], ring_segs, 0)
        H.draw_hub(im, (c, c), ss, hub["acc"], hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                   hub.get("enemy", False), breached, t, False, 3)
        R = H.HUB_R * ss
    else:
        old = H.HUB_R
        H.HUB_R = int(H.RING_OUT * 0.84)
        H.draw_hub(im, (c, c), ss, hub["acc"], hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                   hub.get("enemy", False), breached, t, False, 3)
        R = H.HUB_R * ss
        H.HUB_R = old
    return im, (c, c), R


# ------------------------------------------------------------------ phantom echo
def phantom(hub, t=0.0, ss=3, size=240, ring_segs=None):
    """The mask stays; after-images trail behind it to the left and slide off as if it were moving."""
    h2 = dict(hub, emblem="CORE_phantom_core")
    im, c, R = _disc_layer(dict(h2, emblem="SEG_blank" if False else h2["emblem"]), size, ss, t, ring_segs)
    # redraw: clear the emblem area by re-drawing the hub without emblem is complex; draw echoes UNDER a
    # fresh emblem copy instead: echoes are dim and offset, then the sharp mask is pasted on top again.
    cx, cy = c
    epx = R * 0.86
    ey = cy - R * 0.18
    acc = hub["acc"]
    base = SL.glyph_rgba("CORE_phantom_core", int(epx), max(1.5, epx * 0.07))
    a = base.split()[3]
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    n = 4
    for k in range(n, 0, -1):
        ph = (k - (t % 1.0)) / n  # 0..1, slides left and fades as t advances
        off = ph * R * 0.62
        al = max(0.0, 1 - ph) * 0.55
        tint = Image.new("RGBA", base.size, acc + (0,))
        edge = a.filter(ImageFilter.MaxFilter(5))
        ring_a = Image.fromarray(np.clip(np.asarray(edge, np.int16) - np.asarray(a.filter(ImageFilter.MinFilter(5)), np.int16), 0, 255).astype(np.uint8))
        tint.putalpha(Image.fromarray(np.maximum(np.asarray(ring_a) * al, np.asarray(a) * al * 0.35).astype(np.uint8)))
        layer.alpha_composite(tint, (int(cx - off - base.width / 2), int(ey - base.height / 2)))
    # keep echoes inside the disc
    msk = Image.new("L", im.size, 0)
    ImageDraw.Draw(msk).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    layer.putalpha(Image.fromarray(np.minimum(np.asarray(layer.split()[3]), np.asarray(msk))))
    im.alpha_composite(layer)
    g = H._glow_glyph("CORE_phantom_core", epx, acc, ss)
    H._paste_c(im, g, cx, ey)
    return im.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ enemy BREACHED as a 1-turn timer
STAGES = ["ONLINE", "BREACHED", "TIMER OUT", "REBOOT"]


def breach_stage(hub, stage, t=0.3, ss=3, size=240, left=1.0):
    """stage: ONLINE | BREACHED (left = turns-fraction remaining, 1 -> 0 over the enemy's turn) | REBOOT."""
    br = stage in ("BREACHED", "TIMER OUT")
    im, c, R = _disc_layer(hub, size, ss, t, None, breached=br)
    cx, cy = c
    d = ImageDraw.Draw(im)
    if br:
        fr = left if stage == "BREACHED" else 0.0
        rr = R + 7 * ss
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(70, 20, 20, 255), width=int(7 * ss))
        if fr > 0:
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], -90, -90 + 360 * fr, fill=HARM + (255,), width=int(7 * ss))
        # a pip per remaining turn (Hub Breach 1, Short Circuit 2)
        f = f_num(int(26 * ss))
        s = "1" if fr > 0 else "0"
        d.text((cx + R * 0.62, cy + R * 0.42), s, font=f, fill=(255, 255, 255, 255), stroke_width=int(3 * ss), stroke_fill=HARM + (255,))
        fp = f_num(int(16 * ss))  # the BREACHED plate again, on top of the timer ring
        tx = "BREACHED"
        w = fp.getlength(tx) + 14 * ss
        y0 = cy - R - 12 * ss
        d.rounded_rectangle([cx - w / 2, y0, cx + w / 2, y0 + 22 * ss], radius=4 * ss, fill=HARM + (255,), outline=INK + (255,), width=int(2 * ss))
        d.text((cx - fp.getlength(tx) / 2, y0 + 1 * ss), tx, font=fp, fill=(255, 255, 255, 255))
    if stage == "REBOOT":  # a scan wipe brings the screen back from the top
        p = t % 1.0
        y = cy - R + 2 * R * p
        over = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        od.rectangle([0, y, im.size[0], im.size[1]], fill=(8, 8, 12, 215))
        msk = Image.new("L", im.size, 0)
        ImageDraw.Draw(msk).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        over.putalpha(Image.fromarray(np.minimum(np.asarray(over.split()[3]), np.asarray(msk))))
        im.alpha_composite(over)
        d = ImageDraw.Draw(im)
        d.line([(cx - R, y), (cx + R, y)], fill=hub["acc"] + (255,), width=int(2 * ss))
        f = f_mono(int(10 * ss))
        s = "REBOOTING"
        d.text((cx - f.getlength(s) / 2, cy + R * 0.62), s, font=f, fill=hub["acc"] + (255,), stroke_width=int(2 * ss), stroke_fill=INK + (255,))
    return im.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ player DEFEAT: the core turns to bits and drains
def defeat(hub, p, ss=3, size=260, ring_segs=None, seed=11):
    """p 0..1: the core dissolves into pixel bits that fall and drain out of the bottom of the disc;
    the disc and ring go dark; FLATLINED stamps in at the end."""
    im, c, R = _disc_layer(hub, size, ss, 0.2, ring_segs)
    cx, cy = c
    arr = np.asarray(im, np.float32)
    Hh, W = arr.shape[:2]
    out = arr.copy()
    yy, xx = np.mgrid[0:Hh, 0:W]
    disc = np.hypot(xx - cx, yy - cy) < R
    # dim everything as p grows
    dim = 1 - 0.7 * min(1.0, p * 1.2)
    out[..., :3] *= dim
    B = int(4 * ss)
    rng = np.random.default_rng(seed)
    holes = Image.new("L", (W, Hh), 0)
    hd = ImageDraw.Draw(holes)
    bits = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bits)
    acc = hub["acc"]
    for by in range(int(cy - R), int(cy + R), B):
        for bx in range(int(cx - R), int(cx + R), B):
            if not (0 <= by < Hh and 0 <= bx < W) or not disc[by, bx]:
                continue
            blk = arr[by:by + B, bx:bx + B, :3]
            lum = blk.mean()
            delay = 0.05 + 0.35 * ((cy + R - by) / (2 * R)) + 0.25 * rng.random()  # bottom rows go first
            q = float(np.clip((p - delay) / 0.4, 0, 1))
            if q <= 0:
                continue
            hd.rectangle([bx, by, bx + B - 1, by + B - 1], fill=255)  # the origin goes dark
            if lum < 45:
                continue
            fall = q * q * (R * 2.0)
            ny = by + fall
            if ny > cy + R * 0.9:
                continue  # drained
            drift = (rng.random() - 0.5) * 8 * ss * q
            col = tuple(int(v) for v in blk.reshape(-1, 3).mean(0))
            c2 = tuple(int(v * (1 - q) + a2 * q) for v, a2 in zip(col, acc))
            bd.rectangle([bx + drift, ny, bx + drift + B - 1, ny + B - 1], fill=c2 + (int(255 * (1 - q) ** 0.6),))
    hole = np.asarray(holes, np.float32)[..., None] / 255
    out[..., :3] = out[..., :3] * (1 - hole * 0.85)
    base = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    base.alpha_composite(bits)
    d = ImageDraw.Draw(base)
    # the drain: a glowing slot at the bottom of the disc pulling the bits out
    sl = int(R * 0.5)
    gl = int(255 * min(1, p * 2) * (1 - max(0, p - 0.85) / 0.15))
    d.rounded_rectangle([cx - sl, cy + R * 0.86, cx + sl, cy + R * 0.94], radius=3 * ss, fill=acc + (max(0, gl),))
    if p > 0.7:
        k = min(1.0, (p - 0.7) / 0.2)
        f = f_num(int(30 * ss))
        s = "FLATLINED"
        w = f.getlength(s)
        d.rectangle([cx - w / 2 - 8 * ss, cy - 20 * ss, cx + w / 2 + 8 * ss, cy + 20 * ss], fill=(14, 12, 18, int(230 * k)), outline=(150, 150, 160, int(255 * k)), width=int(2 * ss))
        d.text((cx - w / 2, cy - 18 * ss), s, font=f, fill=(200, 200, 210, int(255 * k)))
        y2 = cy + 26 * ss
        d.line([(cx - R * 0.8, y2), (cx + R * 0.8, y2)], fill=(200, 200, 210, int(200 * k)), width=int(2 * ss))  # the flat line
    return base.resize((size, size), Image.LANCZOS)
