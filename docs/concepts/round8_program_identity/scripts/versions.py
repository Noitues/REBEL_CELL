"""Round 7: three spinner versions built on the round-6 Screens & Data wheel.

V1 "Program cartridges": per-program frame silhouettes + name tabs, sculpted class/corp ring,
   boss: an orbit of armoured satellite modules.
V2 "Living programs": a mascot watermark in every screen, a live readout-strip ring with emblems,
   boss: hologram crown with face + emblem, and a second concentric ring of enemy programs.
V3 "Mixed media": screens in anodised hardware housings, salvaged sticker ring (player) /
   machined branded ring (enemy), boss: cables + conduits, power gauges, phase meter in the rim.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import slicelib as SL
from slicelib import PROGRAMS, CORPS, render_slice, glyph_rgba, f_num, f_ui, f_mono, c01
import roster_wheel as RW
from roster_wheel import CLASS_STYLE, CORP_EMBLEM, SPECIAL_GLYPH, LOD

R_OUT, R_IN = 360.0, 130.0
PLAYER_INK = (12, 10, 20)

READOUT = {
    "breaker": "CELL-9 // BREAKER // RIG OK // SPIN +1 // PERFECT = RESOLVE x2 // RING x2 . PIERCE . - // RAM 6/12 // HP 60/60 // ",
    "route_optimizer": "MERIDIAN FREIGHT // ROUTE OPTIMIZER // LANE 00 OK // LANE 15 OK // ETA 00:14 // PKG 4471 ROUTED // ",
    "the_manifest": "THE MANIFEST // PRIORITY ROUTING +4 SHIELD // PHASE 1 OF 3 // MULTIPLY @66% // ORBIT @33% // ",
    "ghost": "CELL-9 // GHOST // MESH ONLINE // FIRST NUDGE IGNORES RES // PERFECT: STRIP 2 RES // RING PIERCE . x2 . ECHO // HP 50/50 // ",
    "drone_dispatcher": "MERIDIAN FREIGHT // DRONE DISPATCHER // COURIER BAY 2/2 // TARIFF ARMED // PKG 0447 OUTBOUND // ",
}


def set_canvas(cw, ch, cx, cy):
    RW.CW, RW.CH, RW.CX, RW.CY = cw, ch, cx, cy


def pol(cx, cy, r, a, ss):
    t = math.radians(a)
    return (cx + r * ss * math.sin(t), cy - r * ss * math.cos(t))


def wedge(cx, cy, r0, r1, a0, a1, ss, n=24):
    return [pol(cx, cy, r1, a0 + (a1 - a0) * i / n, ss) for i in range(n + 1)] + \
           [pol(cx, cy, r0, a1 - (a1 - a0) * i / n, ss) for i in range(n + 1)]


def paste_rot(img, im, x, y, ang):
    """Paste im centred at (x, y), rotated so its 'up' points outward at compass angle ang."""
    r = -ang if not (90 < ang % 360 < 270) else -(ang + 180)
    im = im.rotate(r, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def label_plate(text, px, ss, bg, fg=PLAYER_INK, font=None):
    f = font or f_mono(int(px * ss))
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + int(10 * ss), bb[3] - bb[1] + int(7 * ss)
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w + 2, h + 2], radius=int(3 * ss), fill=bg + (255,), outline=(10, 8, 16, 255), width=max(1, ss))
    d.text((2 + int(5 * ss) - bb[0], 2 + int(3.5 * ss) - bb[1]), text, font=f, fill=fg + (255,))
    return im


def screw(d, x, y, r, ss):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 150, 158, 255), outline=(30, 30, 34, 255), width=max(1, ss))
    d.line([(x - r * 0.6, y - r * 0.6), (x + r * 0.6, y + r * 0.6)], fill=(40, 40, 46, 255), width=max(1, ss))
    d.line([(x - r * 0.6, y + r * 0.6), (x + r * 0.6, y - r * 0.6)], fill=(40, 40, 46, 255), width=max(1, ss))


# ================================================================== per-slice overlays
def slice_overlay(img, d, gd, cx, cy, a0, span, prog, label, ss, version, theme):
    a1 = a0 + span
    mid = (a0 + a1) / 2
    col = PROGRAMS[prog]["col"]
    P = lambda r, a: pol(cx, cy, r, a, ss)
    if version == 1:
        if prog == "SANDBOX":
            for (r, a) in ((R_OUT - 7, a0 + 1.8), (R_OUT - 7, a1 - 1.8), (R_IN + 7, a0 + 4.5), (R_IN + 7, a1 - 4.5)):
                x, y = P(r, a)
                screw(d, x, y, 4.2 * ss, ss)
            for (r, a, s1, s2) in ((R_OUT - 16, a0 + 3.5, 1, -1), (R_OUT - 16, a1 - 3.5, -1, -1)):
                p0 = P(r, a)
                d.line([p0, P(r, a + s1 * 5)], fill=(235, 255, 250, 255), width=int(2.4 * ss))
                d.line([p0, P(r - 16, a)], fill=(235, 255, 250, 255), width=int(2.4 * ss))
        elif prog == "PROXY":
            for k, al in ((1, 160), (2, 70)):
                off = (6 * ss * k, -5 * ss * k)
                pts = [(x + off[0], y + off[1]) for (x, y) in wedge(cx, cy, R_IN + 3, R_OUT - 3, a0 + 0.8, a1 - 0.8, ss)]
                d.line(pts + [pts[0]], fill=col + (al,), width=int(2.2 * ss))
        elif prog == "PATCH":
            for a in (a0 + 0.4, a1 - 0.4):
                tape = Image.new("RGBA", (int(52 * ss), int(20 * ss)), (0, 0, 0, 0))
                dt = ImageDraw.Draw(tape)
                w, h = tape.size
                pts = [(0, 0)] + [(w * i / 8, (3 * ss if i % 2 else 0)) for i in range(1, 8)] + [(w, 0), (w, h)] + \
                      [(w - w * i / 8, h - (3 * ss if i % 2 else 0)) for i in range(1, 8)] + [(0, h)]
                dt.polygon(pts, fill=(226, 212, 172, 210))
                for xx in range(int(4 * ss), w, int(7 * ss)):
                    dt.line([(xx, h / 2), (xx + 3 * ss, h / 2)], fill=(120, 100, 70, 255), width=max(1, ss))
                for r in (210, 290):
                    x, y = P(r, a)
                    t = tape.rotate(-a, resample=Image.BICUBIC, expand=True)
                    img.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))
        elif prog == "TROJAN":
            lav = (200, 175, 255)
            for (ra, rb) in ((R_OUT - 1, R_OUT - 13), (R_IN + 1, R_IN + 12)):
                d.line([P(ra, mid), P(rb, mid)], fill=lav + (255,), width=int(15 * ss))
                d.line([P(ra, mid - 1.2), P(rb, mid - 1.2)], fill=(120, 90, 200, 255), width=max(1, int(1.6 * ss)))
            x, y = P(R_OUT - 4, mid)
            bow = Image.new("RGBA", (int(60 * ss), int(30 * ss)), (0, 0, 0, 0))
            db = ImageDraw.Draw(bow)
            db.ellipse([0, 2 * ss, 27 * ss, 28 * ss], fill=lav + (255,), outline=(90, 60, 170, 255), width=max(1, ss))
            db.ellipse([33 * ss, 2 * ss, 60 * ss, 28 * ss], fill=lav + (255,), outline=(90, 60, 170, 255), width=max(1, ss))
            db.ellipse([24 * ss, 8 * ss, 36 * ss, 22 * ss], fill=(240, 230, 255, 255))
            paste_rot(img, bow, x, y, mid)
        elif prog == "ZERO-DAY":
            x, y = P(R_OUT - 7, a0 + span * 0.22)
            r = 13 * ss
            gd.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=(255, 120, 215, 230))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 30, 120, 255), outline=(255, 230, 245, 255), width=int(2 * ss))
            g = glyph_rgba("ZERO-DAY", int(19 * ss), 1.5 * ss)
            img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        elif prog == "EXPLOIT":
            a = a0 + span * 0.7
            pts = [P(R_OUT - 1, a), P(R_OUT - 7, a + 1.2), P(R_OUT - 12, a - 0.6), P(R_OUT - 20, a + 1.8), P(R_OUT - 27, a + 0.8)]
            gd.line(pts, fill=(255, 80, 160, 200), width=int(5 * ss))
            d.line(pts, fill=(255, 235, 245, 255), width=int(1.8 * ss))
            pts2 = [P(R_IN + 1, a0 + span * 0.25), P(R_IN + 7, a0 + span * 0.25 + 2), P(R_IN + 12, a0 + span * 0.25 + 1)]
            d.line(pts2, fill=(255, 235, 245, 255), width=int(1.6 * ss))
        elif prog == "VIRUS":
            for k in range(int(span / 3)):
                a = a0 + 2 + k * 3
                x, y = P(R_OUT + 1.5 + (k % 2) * 2, a)
                r = (2.6 if k % 2 else 1.8) * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
        elif prog == "NULL":
            pts = [P(R_OUT - 12, a1 - 5), P(R_OUT - 34, a1 - 9), P(R_OUT - 66, a1 - 8), P(R_OUT - 92, a1 - 15)]
            d.line(pts, fill=(20, 20, 22, 255), width=int(7 * ss), joint="curve")
            d.line(pts, fill=(90, 90, 96, 255), width=int(2 * ss), joint="curve")
            x, y = pts[-1]
            plug = Image.new("RGBA", (int(30 * ss), int(34 * ss)), (0, 0, 0, 0))
            dp = ImageDraw.Draw(plug)
            dp.rounded_rectangle([4 * ss, 12 * ss, 26 * ss, 32 * ss], radius=3 * ss, fill=(70, 70, 76, 255), outline=(15, 15, 18, 255), width=max(1, ss))
            dp.rectangle([9 * ss, 0, 12 * ss, 12 * ss], fill=(200, 190, 140, 255))
            dp.rectangle([18 * ss, 0, 21 * ss, 12 * ss], fill=(200, 190, 140, 255))
            plug = plug.rotate(150 - mid, resample=Image.BICUBIC, expand=True)
            img.alpha_composite(plug, (int(x - plug.width / 2), int(y - plug.height / 2)))
        # program-name tab on the rim edge
        tab = label_plate(label + ".exe", 10, ss, col, PLAYER_INK, f_mono(int(10 * ss)))
        x, y = P(R_OUT - 5, mid + (span * 0.18 if prog in ("ZERO-DAY",) else 0) + (-span * 0.2 if prog == "EXPLOIT" else 0))
        paste_rot(img, tab, x, y, mid)
    elif version == 3:
        for (r, a) in ((R_OUT - 8, a0 + 2.2), (R_OUT - 8, a1 - 2.2), (R_IN + 8, a0 + 5.5), (R_IN + 8, a1 - 5.5)):
            x, y = P(r, a)
            screw(d, x, y, 4 * ss, ss)
        for k in (-1, 0, 1):  # vent slots on the inner lip
            a = mid + k * 5.5
            d.line([P(R_IN + 5.5, a - 1.6), P(R_IN + 5.5, a + 1.6)], fill=(10, 10, 12, 255), width=int(3 * ss))
        eng = f_mono(int(8 * ss))
        t = "MOD-" + label
        tw = eng.getlength(t)
        im = Image.new("RGBA", (int(tw + 6 * ss), int(12 * ss)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((3 * ss, 0), t, font=eng, fill=(20, 20, 24, 210))
        x, y = P(R_OUT - 7, mid)
        paste_rot(img, im, x, y, mid)


# ================================================================== rings
def text_ring(img, text, r, a_start, a_end, ss, font, col, head=None):
    cx, cy = RW.CX * ss, RW.CY * ss
    a = a_start
    i = 0
    while a < a_end:
        ch = text[i % len(text)]
        adv = font.getlength(ch)
        if ch != " ":
            c = col
            if head is not None and abs(((a - head + 180) % 360) - 180) < 14:
                c = (255, 255, 255)
            im = Image.new("RGBA", (int(adv + 4), int(font.size * 1.3)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((2, 0), ch, font=font, fill=c + (255,))
            x, y = pol(cx, cy, r, a + math.degrees(adv / 2 / (r * ss)), ss)
            im = im.rotate(-(a + math.degrees(adv / 2 / (r * ss))), resample=Image.BICUBIC, expand=True)
            img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        a += math.degrees(adv / (r * ss))
        i += 1


def emblem_badge(img, d, gd, x, y, r, acc, emblem, ss):
    gd.ellipse([x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5], fill=acc + (150,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(10, 10, 14, 255), outline=acc + (255,), width=int(2.4 * ss))
    g = RW.tinted_glyph(emblem, int(r * 1.3), acc)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def ring_v1(img, d, gd, spec, R0, R1, ss, acc, rng):
    P = lambda r, a: pol(RW.CX * ss, RW.CY * ss, r, a, ss)
    if spec.get("boss"):  # armoured segments
        for i in range(8):
            a0, a1 = i * 45 + 2, i * 45 + 43
            pts = [P(R0 + 2, a0 + 2), P(R1 + 6, a0 + 4), P(R1 + 6, a1 - 4), P(R0 + 2, a1 - 2)]
            pts = wedge(RW.CX * ss, RW.CY * ss, R0 + 2, R1 + 6, a0 + 1.5, a1 - 1.5, ss, 16)
            d.polygon(pts, fill=(52, 48, 46, 255), outline=(14, 12, 12, 255))
            d.line([P(R1 + 5, a0 + 2) , P(R1 + 5, (a0 + a1) / 2), P(R1 + 5, a1 - 2)], fill=acc + (255,), width=int(2 * ss))
            d.line([P((R0 + R1) / 2, a0 + 6), P((R0 + R1) / 2 + 0.01, a1 - 6)], fill=(90, 86, 82, 255), width=int(3 * ss))
            inner = wedge(RW.CX * ss, RW.CY * ss, R0 + 10, R1 - 4, a0 + 5, a1 - 5, ss, 16)
            d.line(inner + [inner[0]], fill=(84, 78, 74, 255), width=max(1, int(1.4 * ss)))
            for a in (a0 + 3.5, a1 - 3.5):
                x, y = P((R0 + R1) / 2, a)
                screw(d, x, y, 5 * ss, ss)
        return
    if spec["theme"] == "player":  # Breaker: heavy riveted plates + crowbar clamp
        for i in range(10):
            a0, a1 = i * 36 + 1, i * 36 + 35
            d.polygon(wedge(RW.CX * ss, RW.CY * ss, R0 + 2, R1, a0, a1, ss, 12), fill=(62, 60, 70, 255), outline=(12, 10, 14, 255))
            outer = [P(R1 - 2, a0 + (a1 - a0) * k / 12) for k in range(13)]
            inner = [P(R0 + 4, a0 + (a1 - a0) * k / 12) for k in range(13)]
            d.line(outer, fill=(150, 146, 160, 255), width=int(2 * ss))
            d.line(inner, fill=(20, 18, 24, 255), width=int(2 * ss))
            for a in (a0 + 5, (a0 + a1) / 2, a1 - 5):
                x, y = P((R0 + R1) / 2, a)
                r = 5.2 * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=(130, 126, 140, 255), outline=(20, 18, 24, 255), width=max(1, ss))
                d.ellipse([x - r * 0.6, y - r * 0.6, x, y], fill=(235, 235, 245, 255))
        # crowbar clamp around 300 deg
        for a in (286, 314):
            d.polygon(wedge(RW.CX * ss, RW.CY * ss, R0 - 2, R1 + 22, a - 3, a + 3, ss, 4), fill=(34, 32, 38, 255), outline=(150, 146, 160, 255))
            x, y = P(R1 + 14, a)
            screw(d, x, y, 4 * ss, ss)
        bar = [P(R1 + 14, 274 + k * 2.2) for k in range(24)]
        gd.line(bar, fill=acc + (160,), width=int(16 * ss))
        d.line(bar, fill=(46, 44, 52, 255), width=int(13 * ss), joint="curve")
        d.line([(x, y - 3 * ss) for (x, y) in bar], fill=acc + (255,), width=int(2 * ss))
        hook = [P(R1 + 14 - k * 2.5, 326 + k * 1.8) for k in range(8)]
        d.line(hook, fill=(46, 44, 52, 255), width=int(13 * ss), joint="curve")
        x, y = bar[0]
        d.polygon([(x - 8 * ss, y - 6 * ss), (x + 2 * ss, y - 8 * ss), (x + 4 * ss, y + 8 * ss), (x - 10 * ss, y + 6 * ss)], fill=(46, 44, 52, 255))
        return
    # Meridian: corrugated band, container corner-castings, twist-locks
    for i in range(240):
        a = i * 1.5
        d.line([P(R0 + 3, a), P(R1 - 3, a)], fill=(150, 75, 22, 255) if i % 2 else (95, 44, 12, 255), width=int(2.6 * ss))
    ptr = [p * 12 for p in spec.get("pointers", [0])]
    for a in (45, 135, 225, 315):
        x, y = P((R0 + R1) / 2, a)
        s = 21 * ss
        blk = Image.new("RGBA", (int(2 * s + 8), int(2 * s + 8)), (0, 0, 0, 0))
        db = ImageDraw.Draw(blk)
        c = blk.width / 2
        db.rounded_rectangle([c - s, c - s, c + s, c + s], radius=4 * ss, fill=(170, 92, 30, 255), outline=(40, 18, 6, 255), width=int(2 * ss))
        db.rounded_rectangle([c - s * 0.55, c - s * 0.3, c + s * 0.55, c + s * 0.3], radius=6 * ss, fill=(20, 10, 4, 255))
        db.line([(c - s + 3 * ss, c - s + 3 * ss), (c + s - 3 * ss, c - s + 3 * ss)], fill=(240, 160, 80, 255), width=max(1, ss))
        paste_rot(img, blk, x, y, a)
    for a in (90, 270) + tuple(x for x in (0, 180) if all(abs(((x - p + 180) % 360) - 180) > 10 for p in ptr)):
        x, y = P((R0 + R1) / 2, a)
        r = 9 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 120, 128, 255), outline=(20, 20, 24, 255), width=max(1, ss))
        tl = Image.new("RGBA", (int(36 * ss), int(12 * ss)), (0, 0, 0, 0))
        ImageDraw.Draw(tl).rounded_rectangle([0, 0, tl.width - 1, tl.height - 1], radius=4 * ss, fill=(200, 200, 210, 255), outline=(20, 20, 24, 255), width=max(1, ss))
        tl = tl.rotate(-(a + 35), resample=Image.BICUBIC, expand=True)
        img.alpha_composite(tl, (int(x - tl.width / 2), int(y - tl.height / 2)))


def ring_v2(img, d, gd, spec, R0, R1, ss, acc, key, emblem):
    f = f_mono(int(13 * ss))
    for rr in (R0 + 4, R1 - 4):  # strip edges
        bb = [RW.CX * ss - rr * ss, RW.CY * ss - rr * ss, RW.CX * ss + rr * ss, RW.CY * ss + rr * ss]
        d.ellipse(bb, outline=tuple(int(v * 0.5) for v in acc) + (255,), width=max(1, ss))
    text_ring(img, READOUT[key], (R0 + R1) / 2 - 5, 0, 360, ss, f, tuple(int(v * 0.95) for v in acc), head=320)
    ptr = [p * 12 for p in spec.get("pointers", [0])]
    for a in (0, 90, 180, 270):
        if any(abs(((a - p + 180) % 360) - 180) < 10 for p in ptr):
            continue
        x, y = pol(RW.CX * ss, RW.CY * ss, (R0 + R1) / 2, a, ss)
        emblem_badge(img, d, gd, x, y, 19 * ss, acc, emblem, ss)


def ring_v3(img, d, gd, spec, R0, R1, ss, acc, rng, emblem):
    P = lambda r, a: pol(RW.CX * ss, RW.CY * ss, r, a, ss)
    if spec["theme"] == "player":  # salvaged ring: scratches, stickers, tape, grease-pencil tally
        for k in range(70):
            a = rng.random() * 360
            r = R0 + 3 + rng.random() * (R1 - R0 - 6)
            L = 2 + rng.random() * 8
            d.line([P(r, a), P(r + rng.random() * 3 - 1.5, a + L)], fill=(200, 200, 210, int(60 + rng.random() * 90)), width=max(1, ss // 2 + 1))
        stickers = [("NO CORP", (255, 61, 168), 32), ("CELL", (92, 225, 255), 75), ("404", (255, 220, 60), 118),
                    ("<3", (255, 255, 255), 238), ("RIP\nMERIDIAN", (123, 224, 123), 262), ("SKULL", (255, 140, 40), 345),
                    ("v0.9", (200, 90, 255), 204)]
        for txt, c, a in stickers:
            fs = f_ui(int(15 * ss), b"Bold Condensed")
            lines = txt.split("\n")
            tw = max(fs.getlength(l) for l in lines)
            h = len(lines) * 16 * ss + 8 * ss
            st = Image.new("RGBA", (int(tw + 16 * ss), int(h + 6 * ss)), (0, 0, 0, 0))
            ds = ImageDraw.Draw(st)
            if txt == "SKULL":
                st = glyph_rgba("ZERO-DAY", int(38 * ss), 4 * ss, fill=c, edge=(255, 255, 255))
            else:
                ds.rounded_rectangle([0, 0, st.width - 1, st.height - 1], radius=6 * ss, fill=(255, 255, 255, 255))
                ds.rounded_rectangle([3 * ss, 3 * ss, st.width - 3 * ss, st.height - 3 * ss], radius=4 * ss, fill=c + (255,))
                for i, l in enumerate(lines):
                    ds.text((8 * ss, 4 * ss + i * 16 * ss), l, font=fs, fill=PLAYER_INK + (255,))
            st = st.rotate(rng.integers(-25, 25), resample=Image.BICUBIC, expand=True)
            x, y = P((R0 + R1) / 2, a)
            sh = Image.new("RGBA", st.size, (0, 0, 0, 0))
            sh.putalpha(st.split()[3].point(lambda v: int(v * 0.5)))
            img.alpha_composite(sh, (int(x - st.width / 2 + 2 * ss), int(y - st.height / 2 + 3 * ss)))
            img.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))
        for a in (150, 300):  # tape strips across the ring
            tape = Image.new("RGBA", (int(26 * ss), int(70 * ss)), (0, 0, 0, 0))
            ImageDraw.Draw(tape).rectangle([0, 0, tape.width, tape.height], fill=(228, 216, 180, 170))
            x, y = P((R0 + R1) / 2, a)
            t = tape.rotate(-a + 8, resample=Image.BICUBIC, expand=True)
            img.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))
        # grease-pencil tally around 222 deg
        for g in range(2):
            for k in range(5):
                a = 216 + g * 9 + k * 1.4
                if k < 4:
                    d.line([P(R0 + 10, a + rng.random() * 0.4), P(R1 - 10, a)], fill=(245, 245, 235, 230), width=int(2.2 * ss))
                else:
                    d.line([P(R0 + 12, a - 6), P(R1 - 12, a)], fill=(245, 245, 235, 230), width=int(2.2 * ss))
        return
    # enemy: clean machined ring, branded, pattern band
    for k in range(int(R0) + 4, int(R1) - 2, 3):
        bb = [RW.CX * ss - k * ss, RW.CY * ss - k * ss, RW.CX * ss + k * ss, RW.CY * ss + k * ss]
        d.ellipse(bb, outline=(255, 255, 255, 18), width=max(1, ss // 2))
    pb0, pb1 = R0 + (R1 - R0) * 0.62, R0 + (R1 - R0) * 0.86
    for i in range(90):
        a = i * 4
        d.polygon([P(pb0, a), P(pb1, a + 2), P(pb1, a + 3.4), P(pb0, a + 1.4)], fill=acc + (255,))
    name = CORPS[spec["theme"]]["name"] if spec["theme"] in CORPS else ""
    f = f_ui(int(12 * ss), b"Bold SemiCondensed")
    ptr = [p * 12 for p in spec.get("pointers", [0])]
    for a0 in (20, 200):
        text_ring(img, name + "  -  MACHINED IN MERIDIAN BAY", R0 + (R1 - R0) * 0.33, a0, a0 + 130, ss, f, (45, 45, 52))
    for a in (110, 290):
        x, y = P(R0 + (R1 - R0) * 0.4, a)
        g = RW.tinted_glyph(emblem, int(26 * ss), (40, 40, 46))
        img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


# ================================================================== boss extras
def boss_v1_modules(img, d, gd, spec, R1, ss, acc):
    cx, cy = RW.CX * ss, RW.CY * ss
    ro = R1 + 96
    for k in range(120):  # dashed orbit
        if k % 2:
            continue
        a = k * 3
        d.arc([cx - ro * ss, cy - ro * ss, cx + ro * ss, cy + ro * ss], a - 90, a - 90 + 2, fill=acc + (150,), width=max(1, int(1.6 * ss)))
    slots = spec["slots"]
    for i, a in enumerate([-118, -78, -38, 38, 78, 118]):
        x, y = pol(cx, cy, ro, a, ss)
        trail = [pol(cx, cy, ro, a - 14 + j, ss) for j in range(13)]
        gd.line(trail, fill=acc + (170,), width=int(6 * ss))
        mod = Image.new("RGBA", (int(120 * ss), int(70 * ss)), (0, 0, 0, 0))
        dm = ImageDraw.Draw(mod)
        c = (mod.width / 2, mod.height / 2)
        for sx in (-1, 1):  # solar wings
            x0 = c[0] + sx * 30 * ss
            dm.rectangle([min(x0, x0 + sx * 28 * ss), c[1] - 9 * ss, max(x0, x0 + sx * 28 * ss), c[1] + 9 * ss],
                         fill=(30, 50, 130, 255), outline=(170, 180, 200, 255), width=max(1, ss))
            for j in range(1, 4):
                xx = x0 + sx * j * 7 * ss
                dm.line([(xx, c[1] - 9 * ss), (xx, c[1] + 9 * ss)], fill=(170, 180, 200, 255), width=max(1, ss // 2 + 1))
        hexp = [(c[0] + 27 * ss * math.cos(math.radians(60 * j)), c[1] + 27 * ss * math.sin(math.radians(60 * j))) for j in range(6)]
        dm.polygon(hexp, fill=(58, 54, 50, 255), outline=acc + (255,), width=int(2.4 * ss))
        dm.ellipse([c[0] - 14 * ss, c[1] - 14 * ss, c[0] + 14 * ss, c[1] + 14 * ss], fill=(20, 12, 8, 255), outline=(10, 8, 6, 255))
        sl = slots[i % len(slots)]
        gname = SPECIAL_GLYPH.get(sl.get("special")) or sl["program"]
        g = glyph_rgba(gname, int(20 * ss), 1.5 * ss)
        mod.alpha_composite(g, (int(c[0] - g.width / 2), int(c[1] - g.height / 2)))
        for j in (0, 3):
            bx, by = hexp[j]
            dm.ellipse([bx - 2.5 * ss, by - 2.5 * ss, bx + 2.5 * ss, by + 2.5 * ss], fill=(230, 230, 235, 255))
        mod = mod.rotate(-(a + 90), resample=Image.BICUBIC, expand=True)
        img.alpha_composite(mod, (int(x - mod.width / 2), int(y - mod.height / 2)))


def boss_v2_hologram(layer, ss, top_y, acc, emblem):
    """Projected crown: emitter beams, a halo ring, a corporate face and the corp emblem."""
    W, H = layer.size
    d = ImageDraw.Draw(layer)
    cx = RW.CX * ss
    holo = tuple(min(255, int(v * 1.0 + 60)) for v in acc)
    fy = top_y - 175 * ss  # face centre
    # beams from two emitters on the banner corners up to the chin
    for sx in (-1, 1):
        ex, ey = cx + sx * 150 * ss, top_y + 4 * ss
        d.polygon([(ex - 6 * ss, ey), (ex + 6 * ss, ey), (cx + sx * 40 * ss, fy + 110 * ss), (cx + sx * 4 * ss, fy + 110 * ss)], fill=holo + (60,))
        d.ellipse([ex - 7 * ss, ey - 4 * ss, ex + 7 * ss, ey + 4 * ss], fill=(255, 255, 255, 230))
    # halo / crown ring above the head
    hy = fy - 120 * ss
    d.ellipse([cx - 170 * ss, hy - 26 * ss, cx + 170 * ss, hy + 26 * ss], outline=holo + (220,), width=int(4 * ss))
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        x, y = cx + 170 * ss * math.cos(a), hy + 26 * ss * math.sin(a)
        h = (34 if k % 2 == 0 else 20) * ss
        d.polygon([(x - 7 * ss, y), (x + 7 * ss, y), (x, y - h)], fill=holo + (200,))
    # face
    d.ellipse([cx - 92 * ss, fy - 115 * ss, cx + 92 * ss, fy + 112 * ss], outline=holo + (230,), width=int(4 * ss), fill=holo + (40,))
    d.rounded_rectangle([cx - 84 * ss, fy - 34 * ss, cx + 84 * ss, fy + 4 * ss], radius=12 * ss, fill=holo + (150,))  # visor
    for sx in (-1, 1):
        d.rectangle([cx + sx * 46 * ss - 22 * ss, fy - 20 * ss, cx + sx * 46 * ss + 22 * ss, fy - 12 * ss], fill=(255, 255, 255, 255))
    d.line([(cx - 34 * ss, fy + 58 * ss), (cx + 34 * ss, fy + 58 * ss)], fill=holo + (230,), width=int(4 * ss))
    d.line([(cx, fy + 10 * ss), (cx, fy + 34 * ss)], fill=holo + (160,), width=int(3 * ss))
    d.line([(cx - 60 * ss, fy + 110 * ss), (cx - 110 * ss, fy + 150 * ss)], fill=holo + (200,), width=int(4 * ss))
    d.line([(cx + 60 * ss, fy + 110 * ss), (cx + 110 * ss, fy + 150 * ss)], fill=holo + (200,), width=int(4 * ss))
    g = RW.tinted_glyph(emblem, int(56 * ss), holo)
    layer.alpha_composite(g, (int(cx - g.width / 2), int(fy - 98 * ss - g.height / 2 + 10 * ss)))
    # scanlines + chromatic offset
    arr = np.asarray(layer).astype(np.float32)
    arr[::int(3 * ss), :, 3] *= 0.35
    out = arr.copy()
    sh = int(3 * ss)
    out[:, sh:, 0] = np.maximum(arr[:, sh:, 0], arr[:, :-sh, 0] * 0.6)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def tube(d, pts, ss, ring_col):
    for w, c in ((26, (14, 14, 16)), (20, (52, 52, 58)), (10, (82, 82, 90)), (3, (160, 160, 170))):
        d.line(pts, fill=c + (255,), width=int(w * ss), joint="curve")
    for i in range(4, len(pts) - 2, 5):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        d.line([(x0 - nx * 13 * ss, y0 - ny * 13 * ss), (x0 + nx * 13 * ss, y0 + ny * 13 * ss)], fill=(20, 20, 22, 255), width=int(3 * ss))
    x, y = pts[-1]
    d.ellipse([x - 17 * ss, y - 17 * ss, x + 17 * ss, y + 17 * ss], fill=(40, 40, 44, 255), outline=ring_col + (255,), width=int(4 * ss))
    d.ellipse([x - 7 * ss, y - 7 * ss, x + 7 * ss, y + 7 * ss], fill=(170, 170, 178, 255))


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        e = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def boss_v3_rig(img, d, gd, spec, R0, R1, ss, acc):
    cx, cy = RW.CX * ss, RW.CY * ss
    W, H = RW.CW * ss, RW.CH * ss
    for a, edge in ((-62, (0, cy - 330 * ss)), (-112, (0, cy + 330 * ss)), (62, (W, cy - 330 * ss)), (112, (W, cy + 330 * ss))):
        sx, sy = pol(cx, cy, R1 + 6, a, ss)
        ox, oy = pol(cx, cy, R1 + 90, a, ss)
        pts = bezier(edge, (edge[0] * 0.5 + ox * 0.5, edge[1]), (ox, oy), (sx, sy))
        tube(d, pts, ss, acc)
    for a, lab, v in ((34, "PWR", 0.82), (-34, "LOAD", 0.55)):  # power gauges on the rim
        x, y = pol(cx, cy, (R0 + R1) / 2 + 6, a, ss)
        r = 30 * ss
        gd.ellipse([x - r - 4 * ss, y - r - 4 * ss, x + r + 4 * ss, y + r + 4 * ss], fill=acc + (120,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(18, 18, 20, 255), outline=(170, 170, 178, 255), width=int(3 * ss))
        for k in range(11):
            t = math.radians(-225 + k * 27)
            c = (255, 70, 60) if k >= 8 else (230, 230, 235)
            d.line([(x + r * 0.72 * math.cos(t), y + r * 0.72 * math.sin(t)), (x + r * 0.9 * math.cos(t), y + r * 0.9 * math.sin(t))], fill=c + (255,), width=max(1, int(1.6 * ss)))
        t = math.radians(-225 + v * 270)
        d.line([(x, y), (x + r * 0.8 * math.cos(t), y + r * 0.8 * math.sin(t))], fill=acc + (255,), width=int(2.4 * ss))
        d.ellipse([x - 3 * ss, y - 3 * ss, x + 3 * ss, y + 3 * ss], fill=(230, 230, 235, 255))
        fs = f_ui(int(9 * ss), b"Bold Condensed")
        d.text((x - fs.getlength(lab) / 2, y + r * 0.3), lab, font=fs, fill=(220, 220, 228, 255))
    # phase meter built into the rim (bottom)
    a0, a1 = 152, 208
    d.polygon(RW.arc_poly(R0 + 10, R1 - 8, a0, a1, ss, 30), fill=(8, 8, 10, 255), outline=(170, 170, 178, 255))
    for i, lab in enumerate(("P1", "P2", "P3")):
        sa = a0 + 2 + i * (a1 - a0 - 4) / 3
        sb = sa + (a1 - a0 - 4) / 3 - 1.5
        on = i == 0
        d.polygon(RW.arc_poly(R0 + 14, R1 - 12, sa, sb, ss, 8), fill=(acc if on else (60, 40, 20)) + (255,))
        if on:
            gd.polygon(RW.arc_poly(R0 + 14, R1 - 12, sa, sb, ss, 8), fill=acc + (220,))
        x, y = pol(cx, cy, (R0 + R1) / 2 + 1, (sa + sb) / 2, ss)
        fs = f_num(int(13 * ss))
        im = Image.new("RGBA", (int(24 * ss), int(16 * ss)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((2 * ss, 0), lab, font=fs, fill=(20, 12, 4, 255) if on else (170, 140, 100, 255))
        paste_rot(img, im, x, y, (sa + sb) / 2)


# ================================================================== main
def subject_key(spec):
    return spec.get("key", "")


def render_v(spec, version, ss=2, lod=False):
    boss = spec.get("boss")
    theme = spec["theme"]
    if boss and version == 2:
        set_canvas(1160, 1600, 580, 990)
    elif boss and version == 1:
        set_canvas(1220, 1220, 610, 620)
    elif boss and version == 3:
        set_canvas(1260, 1220, 630, 620)
    else:
        set_canvas(1100, 1200, 550, 610)
    CW, CH = RW.CW, RW.CH
    rng = np.random.default_rng(spec.get("seed", 1) + version * 31)
    canvas = np.zeros((CH * ss, CW * ss, 4), np.float32)
    if theme == "player":
        st = CLASS_STYLE[spec["cls"]]
        acc = st["acc"]
        emblem = st["emblem"]
    else:
        st = None
        acc = CORPS[theme]["col"]
        emblem = CORP_EMBLEM[theme]
    R1 = R_OUT + (58 if boss and version != 2 else 40)
    if version == 1:
        base = (0.08, 0.075, 0.09) if theme == "player" else (0.13, 0.08, 0.05)
        RW.ring_base(canvas, ss, R_OUT + 1, R1, base, acc, rim=0.9)
    elif version == 2:
        RW.ring_base(canvas, ss, R_OUT + 1, R1, (0.025, 0.03, 0.04), acc, rim=1.4)
    else:
        if theme == "player":
            RW.ring_base(canvas, ss, R_OUT + 1, R1, (0.20, 0.19, 0.20), acc, brushed=True, rim=0.6)
        else:
            RW.ring_base(canvas, ss, R_OUT + 1, R1, (0.56, 0.56, 0.58), acc, brushed=True, rim=0.7, seed=5)
    opts = dict(LOD) if lod else {}
    if boss:
        opts.update(boss=True, phase=boss.get("phase", 1))
    if version == 1:
        opts["frame"] = "v1"
    elif version == 2:
        if spec.get("art", True):  # round 8: bold identity art (icons8) replaces the faint mascots
            opts["art"] = True
            opts["art_map"] = spec.get("art_map", {})
            opts["plate"] = 0.55 if not lod else 0.8
        else:
            opts["mascot"] = True
            opts["plate"] = min(opts.get("plate", 0.62), 0.55) if not lod else 0.8
    elif version == 3:
        opts["frame"] = "v3"
    if boss and version == 2:  # back plate of the outer program ring first (it repaints the centre)
        RW.ring_base(canvas, ss, 412 - 6, 476 + 4, (0.03, 0.03, 0.04), acc, rim=1.2)
        RW.ring_base(canvas, ss, R_OUT + 1, R1, (0.025, 0.03, 0.04), acc, rim=1.4)
    a = -30.0
    slot_angles = []
    for i, sl in enumerate(spec["slots"]):
        val = sl["value"]
        if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff"):
            val = None
        render_slice(canvas, CX(ss), CY(ss), sl["program"], a, 60, val, (0.3 + i * 0.137) % 1.0, theme, ss, opts,
                     seed=i + spec.get("seed", 1) * 7, glyph=SPECIAL_GLYPH.get(sl.get("special")), badge=sl.get("badge"),
                     special=sl.get("special"))
        slot_angles.append((a, sl))
        a += 60
    hp_R = R1
    banner_R = R1
    if boss and version == 2:  # second concentric ring of enemy programs
        r_in2, r_out2 = 412, 476
        so, si = SL.R_OUT, SL.R_IN
        SL.R_OUT, SL.R_IN = float(r_out2), float(r_in2)
        o2 = dict(opts)
        o2.update(glyph_scale=0.36, number_scale=0.95, plate=0.7)
        try:
            for k in range(12):
                sl = spec["slots"][k % len(spec["slots"])]
                val = None if (sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff")) else sl["value"]
                render_slice(canvas, CX(ss), CY(ss), sl["program"], -15 + k * 30, 30, val, (k * 0.21) % 1.0, theme, ss, o2,
                             seed=40 + k, glyph=SPECIAL_GLYPH.get(sl.get("special")), special=sl.get("special"))
        finally:
            SL.R_OUT, SL.R_IN = so, si
        hp_R = r_out2 + 6
        banner_R = r_out2 + 6
    over = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    glow = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    gd = ImageDraw.Draw(glow)
    # per-slice identity
    for (a0, sl) in slot_angles:
        lab = (sl["special"].replace("_", "-").upper() if sl.get("special") else sl["program"])
        slice_overlay(over, d, gd, CX(ss), CY(ss), a0, 60, sl["program"], lab, ss, version, theme)
    # border
    if version == 1:
        ring_v1(over, d, gd, spec, R_OUT + 1, R1, ss, acc, rng)
    elif version == 2:
        ring_v2(over, d, gd, spec, R_OUT + 1, R1, ss, acc, spec.get("key"), emblem)
    else:
        ring_v3(over, d, gd, spec, R_OUT + 1, R1, ss, acc, rng, emblem)
    # inner ring + hub
    if spec.get("ring"):
        RW.draw_inner_ring(over, d, gd, spec["ring"], ss, acc, st)
        hub_r = 96
    else:
        hub_r = 126
    hub = spec["hub"]
    RW.draw_hub(over, d, gd, ss, hub_r, acc, hub.get("emblem"), hub["name"], hub.get("sub", ""))
    if spec.get("resistance"):
        RW.draw_res_badge(over, d, gd, ss, spec["resistance"], hub_r, lock=spec.get("lock", False))
    # boss extras
    if boss and version == 1:
        boss_v1_modules(over, d, gd, spec, R1, ss, acc)
    if boss and version == 3:
        boss_v3_rig(over, d, gd, spec, R_OUT + 1, R1, ss, acc)
    # pointers
    R_piv = R_OUT + (44 if boss and version != 2 else 30)
    ptrs = spec.get("pointers", [0])
    for k, tk in enumerate(ptrs):
        ang = tk * 12
        if spec.get("orbit"):
            RW.draw_orbit(d, gd, ang, spec["orbit"], R_OUT + 18, ss, acc)
            RW.draw_pointer(d, gd, ang + spec["orbit"] * 12, R_piv, ss, acc, ghost=True)
        RW.draw_pointer(d, gd, ang, R_piv, ss, acc, label=str(k + 1) if len(ptrs) > 1 else None)
    hp = spec.get("hp")
    if hp:
        RW.draw_hp(d, gd, ss, hp_R, hp[0], hp[1], phases=boss.get("pips") if boss else None,
                   active_phase=boss.get("phase", 1) if boss else 1)
    if boss:
        RW.draw_banner(over, d, gd, ss, banner_R, boss["title"], boss["sub"], acc)
    if boss and version == 2:
        top_y = (RW.CY - banner_R - 34 - 82) * ss
        holo = boss_v2_hologram(Image.new("RGBA", over.size, (0, 0, 0, 0)), ss, top_y, acc, emblem)
        hg = holo.filter(ImageFilter.GaussianBlur(8 * ss))
        glow.alpha_composite(hg)
        over.alpha_composite(holo)
    glow = glow.filter(ImageFilter.GaussianBlur(7 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] = canvas[..., :3] + g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    out = im.resize((CW, CH), Image.LANCZOS)
    set_canvas(1100, 1200, 550, 610)
    return out


def CX(ss):
    return RW.CX * ss


def CY(ss):
    return RW.CY * ss


def render_tile(prog, value, version, ss=2, scale=0.5, theme="player", label=None):
    """A single 60-degree program tile with the version's slice treatment (for the program strips)."""
    span = 60
    pad = 14
    Ro = R_OUT * ss
    w = int(2 * Ro * math.sin(math.radians(span / 2)) + 2 * pad * ss)
    h = int(Ro - R_IN * ss * math.cos(math.radians(span / 2)) + 2 * pad * ss)
    cx, cy = w / 2, Ro + pad * ss
    canvas = np.zeros((h, w, 4), np.float32)
    opts = {"frame": "v1"} if version == 1 else {"mascot": True, "plate": 0.55} if version == 2 else {"frame": "v3"} if version == 3 else {}
    render_slice(canvas, cx, cy, prog, -span / 2, span, value, 0.3, theme, ss, opts, seed=3)
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d, gd = ImageDraw.Draw(over), ImageDraw.Draw(glow)
    slice_overlay(over, d, gd, cx, cy, -span / 2, span, prog, label or prog, ss, version, theme)
    glow = glow.filter(ImageFilter.GaussianBlur(6 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] += g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return im.resize((int(w / ss * scale), int(h / ss * scale)), Image.LANCZOS)
