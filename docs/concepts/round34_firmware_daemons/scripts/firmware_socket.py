"""firmware_socket.png (where the chip sits on a slice, with tiers + states, valid/invalid sockets, the trigger cue)
and firmware_trigger.gif (Mirror landing CW of centre, then Leech paying RAM).

python firmware_socket.py [still|gif|all]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

import fwlib as F
import fwfx as X
L = F.L
K = F.K

_tc = {}


def tile_chip(prog, val, tier, state, fid, sc, lit=0.0, seed=3):
    key = (prog, val, tier, state, sc)
    if key not in _tc:
        fn = os.path.join(F.CACHE, "tile_%s_%s_%d_%s_%d.png" % (prog.replace("-", ""), val, tier, state, int(sc * 100)))
        if os.path.exists(fn):
            _tc[key] = Image.open(fn).convert("RGBA")
        else:
            _tc[key] = K.tile(prog, val, t=0.45, tier=tier, state=state, scale=sc, seed=seed)
            _tc[key].save(fn)
    im = _tc[key].copy()
    pad_top = 40 if state else 8
    cx, cy = im.width / 2, (360 + pad_top) * sc
    ang = -30 * F.SOCKET_DA
    x = cx + F.SOCKET_RHO * sc * math.sin(math.radians(ang))
    y = cy - F.SOCKET_RHO * sc * math.cos(math.radians(ang))
    if fid:
        im = F.put_chip(im, fid, x, y, ang, max(14, int(F.CHIP_MASTER * sc)), lit=lit)
    return im, (cx, cy), (x, y)


def callout(d, p0, p1, text, col=(230, 230, 240), anchor="lm"):
    d.line([p0, p1], fill=col + (200,), width=2)
    d.ellipse([p0[0] - 4, p0[1] - 4, p0[0] + 4, p0[1] + 4], fill=col + (255,))
    d.text((p1[0] + (8 if anchor == "lm" else -8), p1[1]), text, font=L.f_mono(15), fill=col + (255,), anchor=anchor)


def wedge(size, c, r_o, r_i, i, n, rot=0.0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    span = 360 / n
    a0 = -90 + i * span - span / 2 + rot
    d.pieslice([c - r_o, c - r_o, c + r_o, c + r_o], a0, a0 + span, fill=255)
    d.ellipse([c - r_i, c - r_i, c + r_i, c + r_i], fill=0)
    return m


# ------------------------------------------------------------------ static sheet
def socketing_panel(img, x0, y0):
    """Drag a chip onto the mini spinner: valid slices lit, invalid greyed, occupied = REPLACE."""
    d = ImageDraw.Draw(img)
    F.section(d, x0, y0, "SOCKETING  -  drag LEECH (ATK only)", L.LIME)
    sl = [("EXPLOIT", 6, 1, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
          ("EXPLOIT", 8, 2, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]
    fw = [None, None, "counterstrike", "siphon", None, None]
    w = F.socket_wheel(sl, fw, 150, "sock")
    c = w.width / 2
    valid = [0, 3]
    g = F.grey(w)
    g = Image.blend(g, Image.new("RGBA", g.size, (8, 6, 12, 255)), 0.55)
    g.putalpha(w.split()[3])
    for i in range(6):
        if i not in valid:
            w = Image.composite(g, w, wedge(w.size, c, 150 * 1.02, 0, i, 6))
    # lime outline on valid slices (round 31 focus language), hover on slot 1
    sc = X.Scene(0, 150, sl, fw, key="sock")
    for i in valid:
        w = X.outline_slice(w, sc, i, 0, L.LIME, k=1.0 if i == 0 else 0.55, w=4)
    wx, wy = x0 + 60, y0 + 80
    img.alpha_composite(w, (wx, wy))
    d = ImageDraw.Draw(img)
    # the dragged chip, tilted, at the cursor over slot 1
    ch = F.chip("leech", 64, lit=0.4)
    ch = ch.rotate(12, Image.BICUBIC, expand=True)
    cx, cy = wx + c - 40, wy + c - 10
    img = L.drop_shadow(img, ch, cx - ch.width / 2 + 40, cy - ch.height / 2 - 20, blur=8, off=(8, 12), op=0.6)
    d = ImageDraw.Draw(img)
    # tags
    t1 = X.term_chip("> SOCKET INTO SLOT 1", L.LIME, 15)
    img.alpha_composite(t1, (int(wx + w.width - 20), int(wy + 40)))
    t2 = X.term_chip("REPLACE SIPHON?", (255, 190, 60), 15)
    img.alpha_composite(t2, (int(wx + w.width - 20), int(wy + w.height - 70)))
    t3 = X.term_chip("ATK ONLY", (150, 150, 165), 14)
    img.alpha_composite(t3, (int(wx - 10), int(wy + w.height / 2 + 40)))
    d = ImageDraw.Draw(img)
    notes = [
        "valid  = lime brackets (FirmwareData.allowed_slice_types; empty = any)",
        "invalid = greyscale + dark 55 %, no drop, cursor shows ATK ONLY",
        "occupied = amber REPLACE? confirm: the old chip is destroyed",
        "  (GDD silent on swapping: open question, see NOTES)",
        "drop = chip snaps into the socket, pins first (0.18 s), LED on",
        "MISS slot accepts only MISS chips (Recycler) or ANY chips",
    ]
    for k, s in enumerate(notes):
        d.text((x0 + 10, y0 + 470 + k * 21), s, font=L.f_mono(14), fill=(190, 200, 215, 255))
    return img


def scene_frame(sc, rot, lit=None, lit_k=1.0, crop=(80, 0, 420, 250), scale=1.0, fx=None):
    w = sc.wheel(rot, lit=lit, lit_k=lit_k)
    canvas = Image.new("RGBA", (w.width, w.height), (12, 10, 18, 255))
    canvas.alpha_composite(w)
    canvas = X.pointer(canvas, sc.c, 14, tick=0.0)
    if fx:
        canvas = fx(canvas)
    out = canvas.crop(crop)
    if scale != 1.0:
        out = out.resize((int(out.width * scale), int(out.height * scale)), Image.LANCZOS)
    return out


def framed(img, im, x, y, title, sub=None, col=(255, 214, 64), top=False):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 4, y - 4, x + im.width + 3, y + im.height + 3], radius=8, outline=(60, 54, 76, 255), width=2)
    img.alpha_composite(im, (x, y))
    d = ImageDraw.Draw(img)
    d.text((x + 6, y + 6), title, font=L.f_num(20), fill=col + (255,), stroke_width=3, stroke_fill=(6, 5, 10, 255))
    if sub:
        for k, s in enumerate(sub):
            yy = (y + 46 + k * 16) if top else (y + im.height - 8 - (len(sub) - k - 1) * 17)
            d.text((x + 6, yy), s, font=L.f_mono(12 if top else 13), fill=(225, 225, 235, 255), anchor="ls", stroke_width=3, stroke_fill=(6, 5, 10, 255))
    return img


def leech_fx(stage, u=1.0):
    """stage 0 land, 1 flare, 2 trace, 3 payoff. Leech on the top slice (k = 3 of the fx wheel)."""
    sc = X.Scene(3)

    def fx(c):
        if stage >= 2:
            pts = X.trace_path(sc, 0, 0, 0)
            c = X.glow_line(c, X.sub_path(pts, u if stage == 2 else 1.0), w=4, k=1.0 if stage == 2 else 0.5, pulse=(u if stage == 2 else None))
        if stage == 3:
            (x, y), _ = sc.chip_xy(0)
            c = X.ram_pip(c, x - 40 * u, y + 60 + 80 * u, 1.0)
            c = X.pop(c, X.term_chip("+1 RAM", L.CYAN, 16), x + 50, y + 100, 1.0, rise=0)
        return c
    lit = {0: None, 1: 0, 2: 0, 3: 0}[stage]
    return sc, fx, lit


def main_still():
    img = F.bg(seed=5)
    d = F.header(img, "FIRMWARE SOCKET  +  TRIGGER",
                 "Round 34: the chip plugs into the slice's INNER, hub-side band, pins into the core, as if the slice were wired from the core outward. Status badge + its rule tag stay outer-CW; nothing covers the read block.")
    # --- A: anatomy hero
    F.section(d, 32, 112, "ANATOMY", L.YEL)
    hero, (hcx, hcy), (chx, chy) = tile_chip("ZERO-DAY", 12, 2, "OVERCLOCKED", "overvolt", 1.05)
    hx, hy = 40, 150
    img.alpha_composite(hero, (hx, hy))
    d = ImageDraw.Draw(img)
    callout(d, (hx + chx - 18, hy + chy), (hx + 10, hy + 410), "FIRMWARE socket (inner band, pins to the core)", L.LIME)
    bx = hx + hcx + 327 * 1.05 * math.sin(math.radians(19.8))
    by = hy + hcy - 327 * 1.05 * math.cos(math.radians(19.8))
    callout(d, (bx + 10, by), (hx + 300, hy + 300), "badge + rule tag", (255, 190, 60))
    callout(d, (hx + hcx, hy + 40 * 1.05 + 12), (hx + hcx + 120, hy - 10), "tier pips", (200, 200, 215))
    callout(d, (hx + hcx + 30, hy + hcy - 268 * 1.05), (hx + 420, hy + 150), "read block (always on top)", (230, 230, 240))
    d.text((40, 604), "Layer order: screen > tier > state overlay > CHIP > read block.", font=L.f_mono(14), fill=(190, 200, 215, 255))
    d.text((40, 622), "x1.5 / x0.5 rule tags moved from the inner edge to sit under the badge.", font=L.f_mono(14), fill=(190, 200, 215, 255))
    # --- B: tiers with a chip
    F.section(d, 600, 112, "WITH TIERS  (Overvolt)", L.YEL)
    for i, (v, t) in enumerate(((6, 1), (8, 2), (10, 3))):
        im, _, _ = tile_chip("EXPLOIT", v, t, None, "overvolt", 0.46)
        img.alpha_composite(im, (600 + i * 186, 160))
        d = ImageDraw.Draw(img)
        d.text((600 + i * 186 + im.width / 2, 160 + im.height + 10), ["I", "II", "III"][i], font=L.f_num(22), fill=(220, 220, 230, 255), anchor="mm")
    # --- C: states with a chip
    F.section(d, 600, 330, "WITH STATE OVERLAYS", L.YEL)
    states = [("FIREWALL", 5, "ENCRYPTED", "hardened", "ENCRYPTED + Hardened"), ("ZERO-DAY", 12, "OVERCLOCKED", "burner", "OVERCLOCKED + Burner"),
              ("EXPLOIT", 6, "CORRUPTED", "leech", "CORRUPTED + Leech"), ("PROXY", 4, "FROZEN", "counterstrike", "FROZEN + Counterstrike"),
              ("SANDBOX", 8, "LOCKED", "power_cell", "LOCKED + Power Cell"), ("PATCH", 3, "BURNING", "nanite_mesh", "BURNING + Nanite Mesh")]
    for i, (p, v, st, fid, lab) in enumerate(states):
        im, _, _ = tile_chip(p, v, 1, st, fid, 0.40)
        x = 600 + (i % 3) * 186
        y = 370 + (i // 3) * 165
        img.alpha_composite(im, (x, y))
        d = ImageDraw.Draw(img)
        d.text((x + im.width / 2, y + im.height + 6), lab, font=L.f_mono(12), fill=(200, 200, 215, 255), anchor="mm")
    # --- D: socketing
    img = socketing_panel(img, 1200, 112)
    # --- E: trigger storyboard (Leech)
    d = ImageDraw.Draw(img)
    F.section(d, 32, 704, "TRIGGER CUE  -  every chip, every fire (Leech shown)", L.YEL)
    caps = [("1  LAND", ["slice resolves first"]), ("2  FLARE  0.10 s", ["LED + lip + pins flash", "in rarity colour"]),
            ("3  TRACE  0.18 s", ["gold trace runs core", "outward: chip -> value"]), ("4  PAYOFF", ["effect leaves the chip:", "RAM pip -> RAM bar"])]
    for st in range(4):
        sc, fx, lit = leech_fx(st, 0.6 if st == 2 else 1.0)
        fr = scene_frame(sc, 0, lit=lit, crop=(95, 0, 405, 270), scale=0.95, fx=fx)
        img = framed(img, fr, 40 + st * 300, 748, caps[st][0], caps[st][1])
    # --- F: per-chip specifics
    d = ImageDraw.Draw(img)
    F.section(d, 1240, 704, "SPECIFIC CUES", L.YEL)
    # Mirror
    sc = X.Scene(0)

    def fx_m(c):
        pts = X.trace_path(sc, 0, 60, -8)
        c = X.glow_line(c, pts, w=4)
        c = X.outline_slice(c, sc, 1, -8, L.CYAN, k=0.7, w=3)
        rx, ry = sc.read_xy(0, -8)
        return X.ghost_read(c, sc, 1, (rx, ry), 0.95)
    fr = scene_frame(sc, -8, lit=0, crop=(60, -36, 500, 184), scale=0.75, fx=fx_m)
    img = framed(img, fr, 1240, 748, "MIRROR", ["landed CW of centre: copies", "the CW neighbour (ghost)"], L.CYAN, top=True)
    # Shunt
    sc2 = X.Scene(2)

    def fx_s(c):
        pts = X.trace_path(sc2, 0, -60, 8)
        c = X.glow_line(c, pts, w=4, col=L.LIME)
        c = X.outline_slice(c, sc2, 5, 8, L.LIME, k=1.0, w=4)
        rx, ry = sc2.read_xy(5, 8)
        return X.pop(c, X.term_chip("x1.5", L.LIME, 18), rx - 10, ry - 62)
    fr = scene_frame(sc2, 8, lit=0, crop=(0, -36, 440, 184), scale=0.75, fx=fx_s)
    img = framed(img, fr, 1572, 748, "SHUNT", ["landed CCW: the CCW", "neighbour resolves x1.5"], L.LIME, top=True)
    # Burner
    sc3 = X.Scene(4)

    def fx_b(c):
        (x, y), _ = sc3.chip_xy(0)
        c = X.glow_line(c, X.trace_path(sc3, 0, 0, 0), w=4, col=L.HEAT, k=0.7)
        return X.pop(c, X.term_chip("+1 HEAT", L.HEAT, 17), x + 4, y - 4, 1.0, rise=0)
    fr = scene_frame(sc3, 0, lit=0, crop=(30, 0, 470, 220), scale=0.75, fx=fx_b)
    img = framed(img, fr, 1240, 912, "BURNER", ["every trigger: +1 HEAT", "(stays OVERCLOCKED)"], L.HEAT, top=True)
    # Hardened: permanent, no flash
    hs = list(X.SLICES)
    hs[1] = ("FIREWALL", 5, 1, "ENCRYPTED")
    hf = list(X.FWS)
    hf[1] = "hardened"
    sc4 = X.Scene(1, slices=hs, fws=hf, key="hard")

    def fx_h(c):
        (x, y), _ = sc4.chip_xy(0)
        bx_, by_ = sc4.pos(327.5, 19.8)
        dd = ImageDraw.Draw(c)
        n = 10
        for j in range(n):
            if j % 2 == 0:
                dd.line([(x + (bx_ - x) * j / n, y + (by_ - y) * j / n), (x + (bx_ - x) * (j + 1) / n, y + (by_ - y) * (j + 1) / n)], fill=L.CYAN + (255,), width=2)
        return c
    fr = scene_frame(sc4, 0, crop=(30, 0, 470, 220), scale=0.75, fx=fx_h)
    img = framed(img, fr, 1572, 912, "HARDENED", ["permanent: no flash; dashed", "link chip -> ENCRYPTED badge"], L.CYAN, top=True)
    L.save(img, "firmware_socket.png")


# ------------------------------------------------------------------ GIF
def ease_out(t):
    return 1 - (1 - t) ** 3


def make_gif():
    crop = (30, 0, 470, 450)
    GK = 0.8
    frames, durs = [], []
    ram = 5

    def base(sc, rot, lit=None, lit_k=1.0, blur=0.0, fx=None, ram_n=5, ram_flash=0.0):
        w = sc.wheel(rot, lit=lit, lit_k=lit_k, blur=blur)
        cv = Image.new("RGBA", (w.width, w.height + 80), (12, 10, 18, 255))
        cv.alpha_composite(w)
        cv = X.pointer(cv, sc.c, 14)
        if fx:
            cv = fx(cv)
        cv = X.ram_bar(cv, crop[0] + 6, w.height - 30, 12, ram_n, ram_flash)
        out = cv.crop((crop[0], crop[1], crop[2], crop[3] + 90)).convert("RGB")
        return out.resize((int(out.width * GK), int(out.height * GK)), Image.LANCZOS)

    def spin(sc, rot_end, turns=1.25, n=16):
        tot = 360 * turns
        prev = None
        for f in range(n):
            t = f / (n - 1)
            a = rot_end + tot * (1 - ease_out(t))
            bl = 0 if prev is None else min(30.0, abs(prev - a) * 0.8)
            prev = a
            frames.append(base(sc, a, blur=bl if f < n - 1 else 0))
            durs.append(45)

    # --- A: Mirror lands CW of centre on EXPLOIT 6
    sc = X.Scene(0)
    spin(sc, -8)
    durs[-1] = 300
    for f in range(4):
        frames.append(base(sc, -8, lit=0, lit_k=[1.0, 0.8, 0.6, 0.5][f]))
        durs.append(50)
    pts = X.trace_path(sc, 0, 60, -8)
    for f in range(8):
        u = (f + 1) / 8
        frames.append(base(sc, -8, lit=0, lit_k=0.5, fx=lambda c, u=u: X.glow_line(c, X.sub_path(pts, u), w=4, pulse=u)))
        durs.append(40)
    rx, ry = sc.read_xy(0, -8)
    for f in range(8):
        k = (f + 1) / 8

        def fx(c, k=k):
            c = X.glow_line(c, pts, w=4, k=1 - 0.5 * k)
            c = X.outline_slice(c, sc, 1, -8, L.CYAN, k=0.7 * k, w=3)
            c = X.ghost_read(c, sc, 1, (rx, ry), k)
            return X.pop(c, X.term_chip("MIRROR: FIREWALL 5", L.CYAN, 15), sc.c, ry + 104, k)
        frames.append(base(sc, -8, lit=0, lit_k=0.5, fx=fx))
        durs.append(50)
    durs[-1] = 1100
    # --- B: Leech on EXPLOIT 8 II, +1 RAM
    sc = X.Scene(3)
    spin(sc, 2, turns=1.0, n=14)
    durs[-1] = 280
    for f in range(3):
        frames.append(base(sc, 2, lit=0, lit_k=[1.0, 0.8, 0.6][f]))
        durs.append(50)
    pts = X.trace_path(sc, 0, 0, 2)
    for f in range(6):
        u = (f + 1) / 6
        frames.append(base(sc, 2, lit=0, lit_k=0.6, fx=lambda c, u=u: X.glow_line(c, X.sub_path(pts, u), w=4, pulse=u)))
        durs.append(40)
    (cx_, cy_), _ = sc.chip_xy(0, 2)
    tx, ty = crop[0] + 6 + 84 + 5 * 13 + 5, sc.size - 30 + 30
    for f in range(10):
        u = ease_out((f + 1) / 10)
        x = cx_ + (tx - cx_) * u
        y = cy_ + (ty - cy_) * u - math.sin(u * math.pi) * 60

        def fx(c, x=x, y=y, u=u):
            c = X.glow_line(c, pts, w=4, k=0.5 * (1 - u))
            c = X.ram_pip(c, x, y)
            return X.pop(c, X.term_chip("LEECH +1 RAM", L.CYAN, 15), sc.c, sc.c + 10, min(1, u * 2), rise=20 * u)
        frames.append(base(sc, 2, lit=0, lit_k=0.5 * (1 - u), fx=fx))
        durs.append(45)
    for f in range(4):
        frames.append(base(sc, 2, ram_n=6, ram_flash=1 - f / 4,
                           fx=lambda c: X.pop(c, X.term_chip("LEECH +1 RAM", L.CYAN, 15), sc.c, sc.c + 10, 1.0, rise=20)))
        durs.append(60)
    durs[-1] = 1400
    pal = Image.new("RGB", (frames[0].width, frames[0].height * 3))
    for j, idx in enumerate((len(frames) // 3, len(frames) * 2 // 3, len(frames) - 1)):
        pal.paste(frames[idx], (0, j * frames[0].height))
    pal = pal.quantize(colors=160, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(F.OUT, "firmware_trigger.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, len(frames), "frames", os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("still", "all"):
        main_still()
    if what in ("gif", "all"):
        make_gif()
