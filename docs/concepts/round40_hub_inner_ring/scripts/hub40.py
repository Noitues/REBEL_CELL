"""Round 40: enemy LOCKDOWN (Hub Breach) as a draining waterline of encrypted bits; the real-needle
sub-needle; status stack indicators."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import slicelib as SL
import hubkit as H
import hub39 as X
from slicelib import f_num, f_ui, f_mono

INK = H.INK
HARM = H.HARM
CIPHER = (150, 240, 255)
GLYPHS = "01#*$%&@0x7F3A9C"


def lockdown(hub, level, t=0.0, ss=3, size=260, turns=1, seed=3):
    """level 1 -> 0: the encrypted-bit water fills the hub at 1 and drains with the lockdown timer.
    The passive is OFF while any water remains."""
    im, c, R = X._disc_layer(hub, size, ss, t, None, breached=False)
    cx, cy = c
    W, Hh = im.size
    on = level > 0
    if on:
        # dim the hub under the lock
        arr = np.asarray(im, np.float32).copy()
        yy, xx = np.mgrid[0:Hh, 0:W]
        disc = np.hypot(xx - cx, yy - cy) < R
        arr[..., :3] = np.where(disc[..., None], arr[..., :3] * 0.55, arr[..., :3])
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        # waterline: top of the water at y_w; a gentle wave
        y_w = cy + R - 2 * R * level
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        f = f_mono(int(9 * ss))
        step_x, step_y = 9 * ss, 12 * ss
        rng = np.random.default_rng(seed)
        frame = int(t * 12)
        for row, y in enumerate(np.arange(cy - R, cy + R + step_y, step_y)):
            for col, x in enumerate(np.arange(cx - R, cx + R + step_x, step_x)):
                wave = 3 * ss * math.sin(x / (14 * ss) + t * 2 * math.pi)
                if y < y_w + wave:
                    continue
                if math.hypot(x - cx, y - cy) > R - 4 * ss:
                    continue
                h = (row * 31 + col * 17 + frame * 7 * ((row + col) % 3 == 0)) % len(GLYPHS)
                depth = min(1.0, (y - y_w) / (R * 0.6) + 0.35)
                a = int(255 * (0.30 + 0.45 * depth))
                ld.text((x, y), GLYPHS[h], font=f, fill=CIPHER + (a,), anchor="mm")
        # the water body tint + the bright surface line
        body = Image.new("RGBA", im.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        pts = [(x, y_w + 3 * ss * math.sin(x / (14 * ss) + t * 2 * math.pi)) for x in np.arange(cx - R, cx + R + 2, 2 * ss)]
        bd.polygon(pts + [(cx + R, cy + R), (cx - R, cy + R)], fill=(20, 70, 100, 120))
        msk = Image.new("L", im.size, 0)
        ImageDraw.Draw(msk).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        for L in (body, layer):
            L.putalpha(Image.fromarray(np.minimum(np.asarray(L.split()[3]), np.asarray(msk))))
            im.alpha_composite(L)
        sl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sl).line(pts, fill=(200, 250, 255, 255), width=int(2 * ss))
        sl.putalpha(Image.fromarray(np.minimum(np.asarray(sl.split()[3]), np.asarray(msk))))
        glow = sl.filter(ImageFilter.GaussianBlur(3 * ss))
        im.alpha_composite(glow)
        im.alpha_composite(sl)
        d = ImageDraw.Draw(im)
        # LOCKDOWN plate with a padlock + turns left
        fp = f_num(int(16 * ss))
        tx = "LOCKDOWN"
        lk = SL.glyph_rgba("ST_LOCKED", int(18 * ss), 1.5 * ss)
        w = fp.getlength(tx) + lk.width + 16 * ss
        y0 = cy - R - 12 * ss
        d.rounded_rectangle([cx - w / 2, y0, cx + w / 2, y0 + 22 * ss], radius=4 * ss, fill=(30, 120, 160, 255), outline=INK + (255,), width=int(2 * ss))
        im.alpha_composite(lk, (int(cx - w / 2 + 4 * ss), int(y0 + 11 * ss - lk.height / 2)))
        d.text((cx - w / 2 + lk.width + 10 * ss, y0 + 1 * ss), tx, font=fp, fill=(255, 255, 255, 255))
        left = math.ceil(level * turns - 1e-6)
        fl = f_num(int(26 * ss))
        d.text((cx + R * 0.62, cy - R * 0.70), str(left), font=fl, fill=(255, 255, 255, 255), stroke_width=int(3 * ss), stroke_fill=(30, 120, 160, 255))
    return im.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ the sub-needle: the real pointer shape, small
def needle_shape(d, tip, base, w, ss):
    """The D4 blade (hubkit.pointer): a cream triangle with an ink outline; tip -> base along its axis."""
    (tx, ty), (bx, by) = tip, base
    ang = math.atan2(ty - by, tx - bx)
    nx, ny = -math.sin(ang), math.cos(ang)
    p1 = (bx + nx * w, by + ny * w)
    p2 = (bx - nx * w, by - ny * w)
    d.polygon([p1, p2, (tx, ty)], fill=(240, 232, 214, 255))
    d.line([p1, (tx, ty), p2, p1], fill=INK + (255,), width=int(3 * ss))


def sub_needle_post(angle):
    def post(img, c, ss, g):
        import ring2 as R2
        d = ImageDraw.Draw(img)
        a = math.radians(angle)
        r_base, r_tip = R2.R1 - 2, R2.R1 + 58  # rides the ring's outer lip, pointing outward
        base = (c[0] + r_base * ss * math.sin(a), c[1] - r_base * ss * math.cos(a))
        tip = (c[0] + r_tip * ss * math.sin(a), c[1] - r_tip * ss * math.cos(a))
        needle_shape(d, tip, base, 10 * ss, ss)
        rr = (R2.R1 + 245) * ss
        tx2, ty2 = c[0] + rr * math.sin(a), c[1] - rr * math.cos(a)
        f = f_ui(int(15 * ss), b"Bold SemiCondensed")
        s = "TRIGGERS"
        w2 = f.getlength(s) + 10 * ss
        d.rounded_rectangle([tx2 - w2 / 2, ty2 - 12 * ss, tx2 + w2 / 2, ty2 + 12 * ss], radius=4 * ss, fill=(240, 232, 214, 255), outline=INK + (255,), width=int(2 * ss))
        d.text((tx2 - f.getlength(s) / 2, ty2 - 10 * ss), s, font=f, fill=INK + (255,))
    return post


# ------------------------------------------------------------------ hangar: two drones docked on the slice
def hangar_post(angle=0, n=2):
    def post(img, c, ss, g):
        from slicelib import R_OUT
        d = ImageDraw.Draw(img)
        rr = (R_OUT - 2) * ss
        offs = [-13, 13] if n == 2 else [0]
        for k, o in enumerate(offs):
            a = math.radians(angle + o)
            x, y = c[0] + rr * math.sin(a), c[1] - rr * math.cos(a)
            # docking clamp on the rim
            d.rounded_rectangle([x - 12 * ss, y - 5 * ss, x + 12 * ss, y + 5 * ss], radius=3 * ss, fill=(60, 56, 80, 255), outline=INK + (255,), width=int(2 * ss))
            # the drone pod: a disc with the drone glyph, sitting on the rim, plus its own mini HP pips
            pr = 21 * ss
            py = y - 18 * ss
            d.ellipse([x - pr, py - pr, x + pr, py + pr], fill=(24, 20, 36, 255), outline=(176, 140, 255, 255), width=int(3 * ss))
            gl = SL.glyph_rgba("DRONE", int(pr * 1.4), 2 * ss)
            img.alpha_composite(gl, (int(x - gl.width / 2), int(py - gl.height / 2)))
            for j in range(3):
                cx2 = x - 8 * ss + j * 8 * ss
                d.rectangle([cx2 - 3 * ss, py - pr - 9 * ss, cx2 + 3 * ss, py - pr - 4 * ss], fill=(123, 224, 123, 255) if j < 3 - k else (60, 60, 70, 255))
    return post


# ------------------------------------------------------------------ status stacks
def stack_badge(gid, px, col, kind, n, style="pips", tab_k=0.42):
    """The status badge with a stack count. style: 'pips' (n<=3 dots under the badge), 'count' (a xN tab),
    'ghost' (stacked badge outlines behind)."""
    import make_glyphs as MG
    b = MG.badge(gid, px, col, kind)
    pad = int(px * 0.5)
    W = px + 2 * pad
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    if style == "ghost":
        for k in range(min(n, 4) - 1, 0, -1):
            o = int(k * px * 0.14)
            g = MG.badge(gid, px, col, kind)
            g.putalpha(g.split()[3].point(lambda v, k=k: int(v * (0.55 - 0.12 * k))))
            out.alpha_composite(g, (pad + o, pad - o))
    out.alpha_composite(b, (pad, pad))
    if style == "pips":
        r = max(3, int(px * 0.11))
        sp = r * 3
        y = pad + px + r + 2
        for k in range(n):
            x = pad + px // 2 + int((k - (n - 1) / 2) * sp)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,), outline=INK + (255,), width=max(1, r // 2))
    if style in ("count", "ghost") and n > 1:
        f = f_num(max(8, int(px * tab_k)))
        s = "x%d" % n
        tw = f.getlength(s)
        x0 = pad + px - int(tw * 0.55)
        y0 = pad - int(px * 0.18)
        d.rounded_rectangle([x0 - 3, y0, x0 + tw + 4, y0 + int(px * tab_k * 1.1)], radius=max(2, px // 10), fill=INK + (255,), outline=col + (255,), width=max(1, px // 22))
        d.text((x0, y0 - int(px * 0.04)), s, font=f, fill=(255, 255, 255, 255))
    return out
