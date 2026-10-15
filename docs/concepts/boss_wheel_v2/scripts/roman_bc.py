"""Boss Wheel v2: Aurelian Concord directions B (MOSAIC) and C (FRIEZE). Same template, same slots as A."""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
import emoji_hand as EH
import fig_roman as F
import render2d as RD
import roman as RM
import wheel_v2 as W
from shapes import Pen

VERD, TRAV, PORPH, GILT, MARBLE = RM.VERD, RM.TRAV, RM.PORPH, RM.GILT, RM.MARBLE
GOLD_HI = (255, 236, 170)
GOLD_LO = (110, 70, 20)


def gilt(mask, size, s, depth=4):
    return RD.relief(mask, size, stone=(214, 168, 72), shadow=GOLD_LO, hi=GOLD_HI, s=s, depth=depth)


def scene_offset(ctx, i, off=44):
    a = W.slot_angle(i, ctx.rot)
    return -math.sin(math.radians(a)) * off * ctx.S, math.cos(math.radians(a)) * off * ctx.S


def eagle(pen, ex, ey, S, lift, k=1.0):
    """Heraldic aquila: body, head in profile, two raised wings with stepped primary feathers, fanned tail.
    lift -1..1: wings fold down (whiff) .. raise and spread (hit)."""
    S = S * k

    def P(x, y):
        return (ex + x * S, ey + y * S)
    pen.d.polygon([P(-12, -6), P(-8, -30), P(4, -36), P(12, -22), P(10, 6), P(0, 24), P(-10, 8)], fill=255)   # body
    pen.d.ellipse([ex - 2 * S, ey - 52 * S, ex + 18 * S, ey - 32 * S], fill=255)                                # head
    pen.d.polygon([P(16, -46), P(30, -42), P(22, -36), P(14, -38)], fill=255)                                   # hooked beak
    pen.d.polygon([P(-10, 18), P(10, 18), P(18, 42), P(0, 36), P(-18, 42)], fill=255)                           # tail
    for sgn in (-1, 1):
        rise = 34 * lift
        root = (sgn * 8, -20)
        pts = [P(*root)]
        tipx, tipy = sgn * 86, -64 - rise
        pts.append(P(sgn * 40, -60 - rise * 0.6))
        pts.append(P(tipx, tipy))
        # stepped primaries along the trailing edge back to the body
        for f_ in range(5):
            u = (f_ + 1) / 6
            bx = tipx + (root[0] - tipx) * u
            by = tipy + (root[1] + 6 - tipy) * u
            pts.append(P(bx + sgn * 4, by + 22 - 10 * u))
            pts.append(P(bx - sgn * 8, by + 12 - 6 * u))
        pts.append(P(sgn * 8, -6))
        pen.d.polygon(pts, fill=255)


# ================================================================== B MOSAIC
class MosaicB(RM.ArenaA):
    key = "B"
    title = "B  MOSAIC"
    blurb = ["ALTERNATE (designer favourite): every slice is a tiled fresco: black figures on cream tesserae,",
             "the slice colour set in glass smalti, a gilded border and fresco cracks per panel; a gilt laurel",
             "wreath grips the rim, an aureus coin is the hub, a gilt eagle standard + vexillum is the needle."]
    mat = dict(base=(150, 112, 46), hi=(255, 226, 150), lo=(60, 36, 12), accent=(232, 186, 90), glass=(24, 14, 10))

    def back_plate(self, ctx):
        return self.cached(("bpB", ctx.S, ctx.phase), lambda: self._backB(ctx))

    def _backB(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        aura = K.blur(K.ring_mask(ctx.size, cx, cy, 0, 470 * S), 20 * S)
        im.alpha_composite(K.solid(aura, (22, 8, 14), 0.9))
        # gold tesserae rings radiating
        r = K.rng(5)
        t = K.rgba(ctx.size)
        d = ImageDraw.Draw(t)
        for ring in range(4):
            rad = (410 + ring * 16) * S
            n = int(2 * math.pi * rad / (8 * S))
            for k in range(n):
                if r.random() < 0.08 + 0.12 * ctx.phase:
                    a = k * 360 / n
                    x, y = K.pol(cx, cy, rad, a)
                    q = 2.8 * S
                    c = K.mix(GILT, (255, 240, 200), r.random() * 0.5) if ring % 2 == 0 else (60, 20, 40)
                    d.rectangle([x - q, y - q, x + q, y + q], fill=c + (220,))
        im.alpha_composite(t)
        return im

    def art_ring_under(self, ctx):
        return self.cached(("underB", ctx.S, round(ctx.get("dmg", 0), 2)), lambda: self._underB(ctx))

    def _underB(self, ctx):
        S = ctx.S
        sw = int(2 * math.pi * 356 * S)
        sh = int(226 * S)
        strip = K.rgba((sw, sh), (226, 210, 176), 255)
        d = ImageDraw.Draw(strip)
        # meander (key) band in black tesserae, two rows
        u = 14 * S
        for row in (0.18, 0.62):
            y0 = sh * row
            x = 0
            while x < sw:
                pts = [(x, y0 + 4 * u), (x, y0), (x + 4 * u, y0), (x + 4 * u, y0 + 3 * u), (x + 2 * u, y0 + 3 * u), (x + 2 * u, y0 + 1.6 * u)]
                d.line(pts, fill=(20, 14, 16, 255), width=max(1, int(u * 0.6)))
                x += 5 * u
        st = RD.mosaic(strip, 6 * S, seed=3, grout=(150, 132, 104))
        im = K.polar_wrap(st, ctx.size, ctx.cx, ctx.cy, 130 * S, 356 * S)
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(40, 30, 24), glow=(255, 160, 60)))
        return im

    def _scene(self, slot, ctx, t, act, i):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        ox, oy = scene_offset(ctx, i)
        bg = K.rgba((w, w), (232, 218, 186), 255)
        d = ImageDraw.Draw(bg)
        cx, cy = w / 2 + ox, w / 2 + oy - 6 * S
        # medallion frame in the type colour (glass smalti) + a dark ring
        for rr, c, wd in ((150, (30, 20, 22), 10), (138, key, 8), (124, (30, 20, 22), 4)):
            d.ellipse([cx - rr * S, cy - rr * S, cx + rr * S, cy + rr * S], outline=c + (255,), width=max(1, int(wd * S)))
        # ground line: a band of dark wave crests
        gy = cy + 62 * S
        for k in range(12):
            x = cx - 120 * S + k * 22 * S
            d.arc([x, gy - 8 * S, x + 22 * S, gy + 14 * S], 180, 360, fill=(40, 30, 30, 255), width=max(1, int(4 * S)))
        fw = int(RM.FIG_W * 0.86 * S)
        masks = RM.FIGS[slot["fig"]](fw * 2, t, act)
        size2 = (fw * 2, int(fw * 2 * 0.75))
        fig = RD.front_lit(masks, size2, (24, 18, 20), key, s=2 * S, gilt=GILT, dark=(8, 6, 8))
        # smalti: the figure's rim in the type colour (bright glass tesserae)
        rim = K.rim_light(masks["main"].resize(size2), 3 * S * 2, -3 * S * 2, 1)
        fig.alpha_composite(K.solid(rim, key))
        fig = fig.resize((fw, int(fw * 0.75)), Image.LANCZOS)
        bg.alpha_composite(fig, (int(cx - fw / 2), int(gy - fig.height * (262 / 300) + 6 * S)))
        mos = RD.mosaic(bg, max(3, 6.5 * S), seed=11 + i, grout=(150, 136, 110))
        # twinkle: a few smalti in the type colour catch the light (idle)
        tw = K.particles((w, w), 14, int(t * 3) + i * 7, 1.2 * S, 2.6 * S, K.mix(key, (255, 255, 255), 0.6), (120, 255),
                         area=(cx - 140 * S, cy - 140 * S, cx + 140 * S, cy + 140 * S))
        mos = K.add(mos, K.blur(tw, 1.5 * S), 1.0)
        if act > 0:
            mos = K.add(mos, K.solid(K.blur(K.ring_mask((w, w), cx, cy, 0, (60 + 80 * act) * S), 30 * S), key), 0.6 * (1 - act * 0.5))
        vg = K.vignette((w, w), w / 2, w / 2, w * 0.7, 0.35)
        mos.alpha_composite(K.solid(vg, (20, 10, 10)))
        return mos

    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 6) / 6.0
        aq = round(act, 2)
        return self.cached(("scB", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._scene(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def slice_glass(self, ctx, i, rot, wm, slot):
        """Gilded border round each mosaic panel + fresco cracks running through the tesserae (seeded per slice)."""
        S = ctx.S
        lay = K.rgba(ctx.size)
        inner = ImageChops.subtract(wm, K.shrink(wm, 10 * S))
        lay.alpha_composite(K.solid(K.blur(inner, 6 * S), (40, 20, 10), 0.6))
        frame = ImageChops.subtract(K.shrink(wm, 4 * S), K.shrink(wm, 9 * S))
        lay.alpha_composite(gilt(frame, ctx.size, S, depth=2))
        cr = K.rot_c(W.crack_layer(ctx, 0.45, 150, 330, 300 + i * 13, col=(60, 44, 36), glow=(230, 190, 120), n_max=4), rot)
        lay.alpha_composite(K.masked(cr, K.shrink(wm, 10 * S)))
        return lay

    def art_ring_over(self, ctx):
        return self.cached(("overB", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2), round(ctx.t * 4) / 4 if ctx.phase >= 3 else 0),
                           lambda: self._overB(ctx))

    def _overB(self, ctx):
        """A gilt laurel wreath gripping the rim: two branches from the ribbon at the bottom up to the needle gap."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        pen = Pen(ctx.size, 1.0)
        vein = Pen(ctx.size, 1.0)
        R0 = 412
        for side in (-1, 1):
            n = 22
            for j in range(n):
                a = 180 + side * (8 + j * (140 / n))
                x, y = K.pol(cx, cy, R0 * S, a)
                tang = a + side * 90          # leaves point up toward the needle
                for sgn, dr in ((-1, -1), (1, 1)):
                    la = math.radians(tang + sgn * 32)
                    L_ = (40 - j * 0.5) * S
                    bx, by = x + dr * 0 * S, y
                    tip = (bx + L_ * math.sin(la), by - L_ * math.cos(la))
                    mid = (bx + L_ * 0.5 * math.sin(la), by - L_ * 0.5 * math.cos(la))
                    nx, ny = math.cos(la) * 9 * S, math.sin(la) * 9 * S
                    pen.d.polygon(K.catmull([(bx, by), (mid[0] + nx, mid[1] + ny), tip, (mid[0] - nx, mid[1] - ny)], 6), fill=255)
                    vein.d.line([(bx, by), tip], fill=255, width=max(1, int(1.6 * S)))
            # stem
            stem = [K.pol(cx, cy, R0 * S, 180 + side * (4 + j * 7.3)) for j in range(21)]
            pen.d.line(stem, fill=255, width=max(1, int(7 * S)))
        # ribbon at the bottom
        rb = [K.pol(cx, cy, (R0 + 10) * S, 180 + a) for a in (-14, -4, 4, 14)]
        pen.d.polygon([rb[0], rb[1], K.pol(cx, cy, (R0 - 24) * S, 180), rb[2], rb[3], K.pol(cx, cy, (R0 + 40) * S, 180)], fill=255)
        m = pen.m
        out = K.rgba(ctx.size)
        out.alpha_composite(K.solid(K.shifted(K.blur(m, 6 * S), 4 * S, 8 * S), (0, 0, 0), 0.7))
        g = gilt(m, ctx.size, S, depth=3)
        g.alpha_composite(K.solid(K.mask_mul(vein.m, m), GOLD_LO, 0.8))
        if ctx.phase >= 2:   # phase 2: gems set; phase 3: the leaves burn at the edges
            gem = K.particles(ctx.size, 0, 1, 1, 1, (0, 0, 0))
            gd = ImageDraw.Draw(gem)
            for side in (-1, 1):
                for j in range(0, 20, 4):
                    x, y = K.pol(cx, cy, R0 * S, 180 + side * (10 + j * 7))
                    gd.ellipse([x - 5 * S, y - 5 * S, x + 5 * S, y + 5 * S], fill=VERD + (255,))
            g.alpha_composite(gem)
            g = K.add(g, K.blur(gem, 5 * S), 1.0)
        if ctx.phase >= 3:
            edge = ImageChops.subtract(m, K.shrink(m, 2 * S))
            fl = 0.7 + 0.3 * math.sin(ctx.t * 9)
            g = K.add(g, K.solid(K.blur(edge, 3 * S), (255, 110, 30)), 1.4 * fl)
        out.alpha_composite(g)
        gap = K.ring_mask(ctx.size, cx, cy, 300 * S, 700 * S, -30, 30)
        out.putalpha(ImageChops.subtract(out.split()[3], gap))
        if ctx.get("dmg", 0) > 0.3:
            cr = W.crack_layer(ctx, ctx.get("dmg"), 390, 440, 71, col=(60, 30, 10), glow=(255, 140, 40))
            out.alpha_composite(K.masked(cr, out.split()[3]))
        return out

    def hub(self, ctx):
        return self.cached(("hubB", ctx.S, ctx.phase, round(ctx.t * 4) / 4 if not ctx.get("still") else 0, ctx.get("wrath", 0)),
                           lambda: self._hubB(ctx))

    def _hubB(self, ctx):
        """The aureus: a gold coin, the emperor's profile struck in relief, the legend round the rim."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = (W.R["hub"] + 12) * S
        im = K.rgba(ctx.size)
        coin = K.ring_mask(ctx.size, cx, cy, 0, R0)
        base = K.rad_grad(ctx.size, cx - 30 * S, cy - 40 * S, R0 * 1.6, (255, 226, 140), (150, 96, 26))
        im.alpha_composite(K.masked(base, coin))
        # raised rim
        rim = K.ring_mask(ctx.size, cx, cy, R0 - 12 * S, R0)
        im.alpha_composite(gilt(rim, ctx.size, S, depth=3))
        px = int(R0 * 1.55)
        m = F.emperor(px * 2, 0, 0)
        sz = (px * 2, px * 2)
        head = ImageChops.lighter(m["main"], m["glint"])
        rel = RD.relief(head, sz, stone=(232, 180, 80), shadow=(120, 74, 18), hi=(255, 246, 200), s=2 * S, depth=4)
        rel.alpha_composite(K.solid(K.mask_mul(m["detail"], m["main"]), (150, 96, 26), 0.7))
        rel = rel.resize((px, px), Image.LANCZOS)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(rel, (int(cx - px / 2 + 6 * S), int(cy - px / 2 + 4 * S)))
        im.alpha_composite(K.masked(lay, K.ring_mask(ctx.size, cx, cy, 0, R0 - 14 * S)))
        # legend
        f = K.f_plex(int(13 * S))
        txt = "AVRELIVS . CONCORDIA . GRAND STAND . "
        n = len(txt)
        for j, ch in enumerate(txt):
            a = -150 + j * (300 / n)
            ci = K.text_img(ch, f, fill=(110, 66, 14))
            ci = ci.rotate(-a, resample=Image.BICUBIC, expand=True)
            x, y = K.pol(cx, cy, R0 - 24 * S, a)
            im.alpha_composite(ci, (int(x - ci.width / 2), int(y - ci.height / 2)))
        # a slow glint sweep across the coin (idle)
        if not ctx.get("still"):
            ga = (ctx.t * 50) % 360
            sw = K.L(ctx.size)
            x0, y0 = K.pol(cx, cy, R0, ga)
            x1, y1 = K.pol(cx, cy, R0, ga + 180)
            ImageDraw.Draw(sw).line([(x0, y0), (x1, y1)], fill=255, width=int(22 * S))
            im = K.add(im, K.solid(K.mask_mul(K.blur(sw, 10 * S), coin), (255, 250, 220)), 0.35)
        return im

    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndlB", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"), ctx.get("landed"), ctx.get("forecast")),
                           lambda: self._needleB(ctx, slots, g))

    def _needleB(self, ctx, slots, g):
        """A gilt eagle standard. g > 0 hit: wings rise and spread; g < 0 whiff: wings fold and droop."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        RM.blade(im, ctx, slots, crown=False, col=(246, 238, 220), edge=GILT, latch=ctx.get("latch", 0.0), tier=ctx.get("tier"), root_r=470)
        pen = Pen(ctx.size, 1.0)
        top = cy - 616 * S
        pen.d.rectangle([cx - 4 * S, top, cx + 4 * S, cy - 462 * S], fill=255)            # pole
        pen.d.rounded_rectangle([cx - 46 * S, cy - 478 * S, cx + 46 * S, cy - 462 * S], radius=4 * S, fill=255)   # blade collar
        pen.d.rounded_rectangle([cx - 176 * S, cy - 604 * S, cx + 176 * S, cy - 592 * S], radius=5 * S, fill=255)  # vexillum crossbar
        for sgn in (-1, 1):
            pen.d.ellipse([cx + sgn * 176 * S - 9 * S, cy - 607 * S, cx + sgn * 176 * S + 9 * S, cy - 589 * S], fill=255)
        lift = g                 # -1..1
        ex, ey = cx, top - 14 * S
        eagle(pen, ex, ey, S, lift, k=0.78)
        g_ = gilt(pen.m, ctx.size, S, depth=3)
        im.alpha_composite(K.solid(K.shifted(K.blur(pen.m, 5 * S), 4 * S, 6 * S), (0, 0, 0), 0.6))
        im.alpha_composite(g_)
        if g > 0.3:
            im = K.add(im, K.solid(K.blur(pen.m, 12 * S), (255, 200, 90)), 0.6 * g)
        # the vexillum: the name banner hangs from the crossbar (porphyry cloth, gilt fringe)
        im.alpha_composite(self.banner(ctx, 556, width=320, col=(232, 186, 90)))
        d = ImageDraw.Draw(im)
        for j in range(40):
            x = cx - 160 * S + j * 8.2 * S
            d.line([(x, cy - 524 * S), (x, cy - 514 * S)], fill=GILT + (255,), width=max(1, int(2 * S)))
        return im


# ================================================================== C FRIEZE
class FriezeC(RM.ArenaA):
    key = "C"
    title = "C  FRIEZE"
    blurb = ["Every slice is a carved travertine relief under-lit by a neon tube in the slice colour;",
             "two colossal marble hands grip the rim, the VERDICT hand is the hub emblem,",
             "a bronze rostrum (a ship's ram) carries the blade, the emperor's hand above it."]
    mat = dict(base=(176, 160, 132), hi=(248, 240, 222), lo=(60, 48, 42), accent=VERD, glass=(16, 24, 22))

    def back_plate(self, ctx):
        return self.cached(("bpC", ctx.S, ctx.phase), lambda: self._backC(ctx))

    def _backC(self, ctx):
        """A rotunda: columns radiating round the wheel, verdigris light between them."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        aura = K.blur(K.ring_mask(ctx.size, cx, cy, 0, 500 * S), 22 * S)
        im.alpha_composite(K.solid(aura, (10, 16, 16), 0.92))
        glow = K.ring_mask(ctx.size, cx, cy, 400 * S, 490 * S)
        im = K.add(im, K.solid(K.blur(glow, 16 * S), VERD if ctx.phase < 3 else (255, 110, 40)), 0.25 + 0.1 * ctx.phase)
        col = Pen(ctx.size, 1.0)
        for k in range(24):
            a = k * 15 + 7.5
            if -30 < ((a + 180) % 360) - 180 < 30:
                continue
            p0 = K.pol(cx, cy, 404 * S, a)
            p1 = K.pol(cx, cy, 486 * S, a)
            col.d.line([p0, p1], fill=255, width=int(14 * S))
            for rr, hw in ((410, 6), (480, 7)):
                q = [K.pol(cx, cy, (rr - 7) * S, a - hw * 1.0), K.pol(cx, cy, (rr - 7) * S, a + hw * 1.0),
                     K.pol(cx, cy, (rr + 7) * S, a + hw * 1.0), K.pol(cx, cy, (rr + 7) * S, a - hw * 1.0)]
                col.d.polygon(q, fill=255)
        im.alpha_composite(RD.relief(col.m, ctx.size, stone=(206, 192, 166), shadow=(50, 44, 40), hi=(255, 250, 236), s=S, depth=5))
        return im

    def art_ring_under(self, ctx):
        return self.cached(("underC", ctx.S, round(ctx.get("dmg", 0), 2)), lambda: self._underC(ctx))

    def _underC(self, ctx):
        S = ctx.S
        rr, ang = K.polar_field(ctx.size, ctx.cx, ctx.cy)
        n = K.noise(ctx.size, int(60 * S), 21, 5)
        vein = np.abs(np.sin(n * 18))
        col = np.array(PORPH, np.float32) * (0.7 + 0.6 * n[..., None]) + np.array((120, 90, 100), np.float32) * (vein[..., None] < 0.08)
        a = ((rr <= 356 * S) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(20, 8, 12), glow=(255, 120, 60)))
        return im

    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 6) / 6.0
        aq = round(act, 2)
        return self.cached(("scC", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._sceneC(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def _sceneC(self, slot, ctx, t, act, i):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        ox, oy = scene_offset(ctx, i)
        n = K.noise((w, w), int(18 * S), 31 + i, 4)
        stone = np.array((150, 134, 110), np.float32) * (0.8 + 0.3 * n[..., None])
        bg = Image.fromarray(np.concatenate([np.clip(stone, 0, 255), np.full((w, w, 1), 255, np.float32)], 2).astype(np.uint8), "RGBA")
        cx, cy = w / 2 + ox, w / 2 + oy
        gy = cy + 60 * S
        fw = int(RM.FIG_W * 0.9 * S)
        masks = RM.FIGS[slot["fig"]](fw * 2, t, act)
        size2 = (fw * 2, int(fw * 2 * 0.75))
        allm = masks["main"]
        for nm in ("back", "glint"):
            if nm in masks:
                allm = ImageChops.lighter(allm, masks[nm].point(lambda v: int(v * (0.7 if nm == "back" else 1.0))))
        rel = RD.relief(allm, size2, stone=(214, 198, 168), shadow=(70, 56, 46), hi=(255, 250, 236), s=2 * S, depth=7, under=key, under_k=1.1)
        rel.alpha_composite(K.solid(K.mask_mul(masks["detail"], allm), (90, 72, 60), 0.6))
        rel = rel.resize((fw, int(fw * 0.75)), Image.LANCZOS)
        fx0, fy0 = int(cx - fw / 2), int(gy - rel.height * (262 / 300))
        # carved recess shadow (the figure stands proud of the slab)
        sh = K.solid(K.shifted(K.blur(rel.split()[3], 4 * S), 5 * S, 7 * S), (40, 30, 24), 0.55)
        bg.alpha_composite(sh, (fx0, fy0))
        bg.alpha_composite(rel, (fx0, fy0))
        # the neon tube along the ground line in the type colour, lighting upward
        tube = K.L((w, w))
        ImageDraw.Draw(tube).rounded_rectangle([cx - 140 * S, gy + 8 * S, cx + 140 * S, gy + 15 * S], radius=4 * S, fill=255)
        up = K.rad_grad((w, w), cx, gy + 12 * S, 170 * S, key, (0, 0, 0), gamma=1.2)
        up.putalpha(K.L((w, w), 255))
        bg = K.screen(bg, K.tone(up, 1.0, 0.32 + 0.3 * act))
        bg.alpha_composite(K.solid(tube, K.mix(key, (255, 255, 255), 0.6)))
        bg = K.add(bg, K.solid(K.blur(tube, 6 * S), key), 1.3)
        vg = K.vignette((w, w), w / 2, w / 2, w * 0.66, 0.5)
        bg.alpha_composite(K.solid(vg, (20, 14, 12)))
        return bg

    def art_ring_over(self, ctx):
        return self.cached(("overC", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2)), lambda: self._overC(ctx))

    def _overC(self, ctx):
        """A carved procession frieze round the rim (legionaries with standards marching toward the needle),
        travertine relief with a verdigris neon cornice; cracks open with damage, fire behind it in phase 3."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        r0, r1 = 430, 494
        out = K.rgba(ctx.size)
        for side, (a0, span) in enumerate(((30, 100), (230, 100))):
            sw = int(2 * math.pi * r1 * span / 360 * S)
            sh = int((r1 - r0) * S)
            fig = Pen((sw, sh), 1.0)
            n = 15
            step = sw / n
            for k_ in range(n):
                x = (k_ + 0.5) * step
                walk = math.sin(k_ * 1.3) * 0.15
                # strip row 0 = outer; figures stand on the inner edge (bottom of the strip), heads outward
                gy = sh * 0.92
                u = sh / 64
                d = -1 if side == 0 else 1      # march toward the top (the needle) on both sides
                fig.d.ellipse([x - 5 * u, gy - 58 * u, x + 5 * u, gy - 47 * u], fill=255)                 # head
                fig.d.polygon([(x - 5 * u, gy - 62 * u), (x + 5 * u, gy - 62 * u), (x + d * 9 * u, gy - 66 * u)], fill=255)  # crest
                fig.d.rounded_rectangle([x - 7 * u, gy - 47 * u, x + 7 * u, gy - 22 * u], radius=3 * u, fill=255)     # torso
                fig.d.line([(x - 3 * u, gy - 22 * u), (x - 3 * u - d * 7 * u * (1 + walk), gy)], fill=255, width=max(1, int(5 * u)))
                fig.d.line([(x + 3 * u, gy - 22 * u), (x + 3 * u + d * 7 * u * (1 - walk), gy)], fill=255, width=max(1, int(5 * u)))
                fig.d.rounded_rectangle([x + d * 4 * u - 8 * u, gy - 44 * u, x + d * 4 * u + 8 * u, gy - 18 * u], radius=3 * u, fill=255)  # scutum
                if k_ % 4 == 1:          # a standard bearer: pole + laurel disc
                    fig.d.line([(x - d * 8 * u, gy - 20 * u), (x - d * 8 * u, gy - 64 * u)], fill=255, width=max(1, int(2.4 * u)))
                    fig.d.ellipse([x - d * 8 * u - 6 * u, gy - 70 * u, x - d * 8 * u + 6 * u, gy - 58 * u], fill=255)
                else:                    # pilum over the shoulder
                    fig.d.line([(x - d * 6 * u, gy - 14 * u), (x + d * 12 * u, gy - 64 * u)], fill=255, width=max(1, int(1.8 * u)))
            slab = K.rgba((sw, sh), (176, 160, 130), 255)
            nz = K.noise((sw, sh), max(3, int(8 * S)), 50 + side, 3)
            slab = K.tone_map(slab, np.ones((sh, sw), np.float32), 0.85 + 0.3 * nz)
            rel = RD.relief(fig.m, (sw, sh), stone=(226, 212, 184), shadow=(70, 58, 48), hi=(255, 250, 236), s=S, depth=2.5)
            slab.alpha_composite(K.solid(K.shifted(K.blur(fig.m, 1.5 * S), 2 * S, 2 * S), (60, 48, 40), 0.7))
            slab.alpha_composite(rel)
            sd = ImageDraw.Draw(slab)
            sd.rectangle([0, 0, sw, sh * 0.08], fill=(110, 92, 74, 255))
            sd.line([(0, sh * 0.06), (sw, sh * 0.06)], fill=VERD + (255,), width=max(1, int(2.4 * S)))
            sd.rectangle([0, sh * 0.94, sw, sh], fill=(110, 92, 74, 255))
            wr = K.polar_wrap(slab, ctx.size, cx, cy, r0 * S, r1 * S, ang0=a0, span=span)
            if side == 1:
                # the left half is drawn mirrored so both processions walk up to the needle
                pass
            out.alpha_composite(wr)
        rr, ang = K.polar_field(ctx.size, cx, cy)
        lightk = 0.78 + 0.28 * np.cos(np.radians(ang - 315))
        out = K.tone_map(out, np.ones_like(lightk), lightk.astype(np.float32))
        for a_, sp in ((30, 100), (230, 100)):
            neon = K.ring_mask(ctx.size, cx, cy, (r1 - 4) * S, (r1 - 1) * S, a_, a_ + sp)
            out = K.add(out, K.solid(K.blur(neon, 4 * S), VERD), 0.9)
        sh_ = K.solid(K.shifted(K.blur(out.split()[3], 8 * S), 4 * S, 8 * S), (0, 0, 0), 0.6)
        res = K.rgba(ctx.size)
        res.alpha_composite(sh_)
        res.alpha_composite(out)
        dmg = ctx.get("dmg", 0)
        if ctx.phase >= 2 or dmg > 0:
            cr = W.crack_layer(ctx, max(dmg, 0.3 * (ctx.phase - 1)), r0, r1, 91, col=(40, 30, 26),
                               glow=VERD if ctx.phase < 3 else (255, 110, 40), n_max=10)
            res.alpha_composite(K.masked(cr, res.split()[3]))
        return res

    def hub(self, ctx):
        tq = round(ctx.t * 6) / 6 if not ctx.get("still") else 0
        return self.cached(("hubC", ctx.S, ctx.phase, tq, round(ctx.get("gesture", 0), 1)), lambda: self._hubC(ctx, tq))

    def _hubC(self, ctx, t):
        """The emblem hub: the VERDICT hand on porphyry under a verdigris neon ring; it bobs, the ring pulses."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        im = K.rgba(ctx.size)
        disc = K.ring_mask(ctx.size, cx, cy, 0, R0)
        im.alpha_composite(K.masked(K.rad_grad(ctx.size, cx, cy - 20 * S, R0, (96, 34, 62), (26, 8, 18)), disc))
        ring = K.ring_mask(ctx.size, cx, cy, R0 - 9 * S, R0 - 5 * S)
        pulse = 0.7 + 0.3 * math.sin(t * 2.4)
        col = VERD if ctx.phase < 3 else (255, 110, 40)
        im.alpha_composite(K.solid(ring, K.mix(col, (255, 255, 255), 0.4)))
        im = K.add(im, K.solid(K.blur(ring, 8 * S), col), 1.2 * pulse)
        bob = 4 * math.sin(t * 1.7) * S
        h = EH.hand_rgba(int(R0 * 1.62), -1.0, outline=13)
        im.alpha_composite(h, (int(cx - h.width / 2 + 4 * S), int(cy - h.height / 2 + bob - 2 * S)))
        d = ImageDraw.Draw(im)
        for rr_, c, wd in ((W.R["hub"] + 8, (60, 48, 42), 16), (W.R["hub"] + 4, TRAV, 4), (W.R["hub"] + 13, VERD, 2)):
            d.ellipse([cx - rr_ * S, cy - rr_ * S, cx + rr_ * S, cy + rr_ * S], outline=c + (255,), width=max(1, int(wd * S)))
        return im

    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndlC", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"), ctx.get("landed"), ctx.get("forecast")),
                           lambda: self._needleC(ctx, slots, g))

    def _needleC(self, ctx, slots, g):
        """The bronze rostrum (a warship's ram) holds the blade; the emperor's hand turns above it."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        im.alpha_composite(self.banner(ctx, 622, col=VERD))
        RM.blade(im, ctx, slots, crown=False, col=(246, 238, 220), edge=VERD, latch=ctx.get("latch", 0.0), tier=ctx.get("tier"), root_r=470)
        pen = Pen(ctx.size, 1.0)
        fins = Pen(ctx.size, 1.0)
        # the ram: a bronze beak pointing down with three horizontal blades (fins)
        top, bot = cy - 586 * S, cy - 432 * S
        pen.d.polygon([(cx - 54 * S, top), (cx + 54 * S, top), (cx + 40 * S, bot - 30 * S), (cx, bot), (cx - 40 * S, bot - 30 * S)], fill=255)
        for j, yy in enumerate((top + 40 * S, top + 78 * S, top + 114 * S)):
            wv = (86 - j * 14) * S
            fins.d.polygon([(cx - wv, yy), (cx + wv, yy), (cx + wv - 14 * S, yy + 16 * S), (cx - wv + 14 * S, yy + 16 * S)], fill=255)
        allm = ImageChops.lighter(pen.m, fins.m)
        bronze = RD.relief(allm, ctx.size, stone=(150, 104, 54), shadow=(46, 28, 14), hi=(240, 200, 130), s=S, depth=5, under=VERD, under_k=0.8)
        im.alpha_composite(K.solid(K.shifted(K.blur(allm, 6 * S), 5 * S, 8 * S), (0, 0, 0), 0.6))
        im.alpha_composite(bronze)
        hp = int(124 * S)
        hand = EH.hand_rgba(hp, g, pivot_centre=True, pivot=(200, 10), swing=-1.0)
        hand = K.drop_shadow(hand, int(4 * S), int(6 * S), 5 * S, 0.55)
        rx, ry = cx + 84 * S, top + 30 * S
        im.alpha_composite(hand, (int(rx - hand.width / 2), int(ry - hand.height / 2)))
        return im
