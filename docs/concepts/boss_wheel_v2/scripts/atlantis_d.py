"""Boss Wheel v2: Tethys Deep FINAL (designer direction): "the octopus IS the wheel".

- Six arms radiate from the head and ARE the slice borders; each slice is the web between two arms. They turn with
  the slice ring (a spinning skirt round a calm head). The 2 spare arms are tucked: they curl round the head and hold
  the beak (they clench on a hit).
- The hub is the head (high 3/4 from above), FIXED like any needle.
- No external needle: the needle is the BEAK, pointing DOWN at 6 o'clock (pointer_tick = 15, a per-boss needle
  position; the template's needle_rig slot carries `pointer_angle`). Precision is read at the beak tip on the hub lip,
  where 30 tick notches turn with the wheel. A value window sits on the head above the beak.
- HP arc + phase pips move to the top (the free side); the readout rail sits in the bezel at the bottom, upright.
- Motion: arms ripple at idle, trail during the spin, the two arms bordering the landed slice curl in to grab it, the
  beak snaps; phase 2/3: the eyes open wider, the skin flushes and the blue rings bioluminesce.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import atlantis as AT
import bw_kit as K
import render2d as RD
import wheel_v2 as W
from shapes import Pen

PHOTO, ABYSS, RED = AT.PHOTO, AT.ABYSS, AT.RED
SKIN = {1: (104, 38, 50), 2: (150, 46, 40), 3: (176, 24, 44)}
RINGS = {1: (60, 110, 170), 2: (60, 170, 255), 3: (110, 240, 255)}


class OctopusD(AT.AbyssA):
    key = "D"
    title = "FINAL  THE OCTOPUS IS THE WHEEL"
    blurb = ["The octopus is the wheel: six arms radiate from the head and form the slice borders,",
             "the head is the hub, and the needle is its beak pointing down at 6 o'clock.",
             "Arms ripple, trail in the spin, grab the landed slice; the beak snaps; phase 2 it wakes and glows."]
    pointer_angle = 180.0
    hp_span = (-52, 52)
    mat = dict(base=(36, 44, 60), hi=(140, 160, 190), lo=(6, 8, 16), accent=(90, 150, 255), glass=(3, 8, 20))

    def separators(self, ctx, slots):
        return K.rgba(ctx.size)       # the arms are the borders (drawn in art_ring_over, under the plaques)

    # -------- the web between the arms: what the blank window shows
    def art_ring_under(self, ctx):
        return self.cached(("underD", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2)), lambda: self._underD(ctx))

    def _underD(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        n = K.noise(ctx.size, int(22 * S), 77, 4)
        base = np.array(K.mul(SKIN[ctx.phase], 0.55), np.float32)
        col = base * (0.55 + 0.7 * n[..., None]) * (0.6 + 0.4 * np.clip(1 - rr / (360 * S), 0, 1))[..., None]
        a = ((rr <= 356 * S) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        # veins radiating
        vd = ImageDraw.Draw(im)
        r = K.rng(5)
        for j in range(60):
            a0 = r.uniform(0, 360)
            pts = [K.pol(cx, cy, rr_ * S, a0 + 4 * math.sin(rr_ / 30 + j)) for rr_ in range(130, 352, 12)]
            vd.line(pts, fill=K.mul(SKIN[ctx.phase], 0.35) + (160,), width=max(1, int(1.4 * S)))
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(10, 2, 4), glow=(255, 90, 60)))
        return im

    # -------- slices: water scenes seen through the web, edges darkened by the membrane
    def slice_glass(self, ctx, i, rot, wm, slot):
        S = ctx.S
        lay = K.rgba(ctx.size)
        inner = ImageChops.subtract(wm, K.shrink(wm, 26 * S))
        web = K.blur(inner, 16 * S)
        lay.alpha_composite(K.solid(web, K.mul(SKIN[ctx.phase], 0.5), 0.9))
        return lay

    # -------- the arms (rotating with the slices, drawn above the bezel, under the plaques)
    def art_ring_over(self, ctx):
        tq = round(ctx.t * 12) / 12.0 if not ctx.get("still") else 0.0
        key = ("armsD", ctx.S, ctx.phase, tq, round(ctx.rot, 2), round(ctx.get("spin_speed", 0), 1),
               ctx.get("landed"), round(ctx.get("grab", 0), 2), round(ctx.get("recoil", 0), 2))
        return self.cached(key, lambda: self._arms(ctx, tq))

    def _arms(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rot = ctx.rot
        sp = ctx.get("spin_speed", 0.0)          # deg/frame, signed
        landed = ctx.get("landed")
        grab = ctx.get("grab", 0.0)
        recoil = ctx.get("recoil", 0.0)
        body = K.L(ctx.size)
        bd = ImageDraw.Draw(body)
        suck = K.L(ctx.size)
        sd = ImageDraw.Draw(suck)
        rings = K.L(ctx.size)
        rd = ImageDraw.Draw(rings)
        n_arms = 6
        for j in range(n_arms):
            b = W.SLOT_DEG * j + W.SLOT_DEG / 2 + rot          # border between slot j and j+1
            curl_dir = 0.0
            if landed is not None:
                if j == landed:            # border clockwise of the landed slot -> curl back (ccw)
                    curl_dir = -1.0
                elif (j + 1) % n_arms == landed:
                    curl_dir = 1.0
            cl = []
            n = 44
            for q in range(n + 1):
                u = q / n
                rr = 112 + (384 - 112) * u
                wave = 3.2 * math.sin(2 * math.pi * (u * 1.4 - t * 0.55) + j * 1.3) * u
                trail = -max(-1, min(1, sp / 14.0)) * 16 * u ** 1.6
                g = curl_dir * (grab * 14 * u ** 3) - curl_dir * recoil * 6 * u ** 2
                cl.append((b + wave + trail + g, rr))
            # the tip curl beyond the rim (outward), or inward over the landed slice when grabbing
            a_end, r_end = cl[-1]
            sgn = 1 if (j % 2 == 0) else -1
            if curl_dir and grab > 0.05:
                sgn = int(curl_dir)
            for q in range(1, 18):
                u = q / 17
                ang = math.radians(90 * sgn + u * 320 * sgn)
                rad = 24 * (1 - 0.7 * u) * (1 + 0.6 * grab * abs(curl_dir))
                cl.append((a_end + math.degrees(rad * math.sin(ang) / r_end) + sgn * 3 * u, r_end + 18 - rad * math.cos(ang) - 20 * grab * abs(curl_dir) * u))
            pts = [K.pol(cx, cy, r_ * S, a_) for a_, r_ in cl]
            L_, R_ = [], []
            m = len(pts)
            for i in range(m):
                x, y = pts[i]
                xa, ya = pts[max(0, i - 1)]
                xb, yb = pts[min(m - 1, i + 1)]
                dx, dy = xb - xa, yb - ya
                ln = math.hypot(dx, dy) or 1
                nx, ny = -dy / ln, dx / ln
                u = i / (m - 1)
                w = (48 * (1 - u) ** 1.1 + 3.5) * S / 2
                L_.append((x + nx * w, y + ny * w))
                R_.append((x - nx * w, y - ny * w))
                if i % 3 == 1 and u > 0.55:              # suckers show on the curling tip
                    sx, sy = x - nx * w * 0.55, y - ny * w * 0.55
                    q_ = max(1.2 * S, w * 0.35)
                    sd.ellipse([sx - q_, sy - q_, sx + q_, sy + q_], fill=255)
                if i % 4 == 2 and u < 0.75:              # ring markings (blue rings: they glow in phase 2/3)
                    q_ = w * 0.42
                    rd.ellipse([x - q_, y - q_, x + q_, y + q_], outline=255, width=max(1, int(2.0 * S)))
            bd.polygon(L_ + R_[::-1], fill=255)
        # inner tick ring on the hub lip: 30 notches turning with the wheel (precision read at the beak)
        ticks = K.rgba(ctx.size)
        td = ImageDraw.Draw(ticks)
        for k_ in range(30):
            a_ = k_ * 12 + rot
            ln = 12 if k_ % 5 == 0 else 6
            td.line([K.pol(cx, cy, 130 * S, a_), K.pol(cx, cy, (130 + ln) * S, a_)], fill=(200, 220, 255, 200), width=max(1, int(2 * S)))
        skin = SKIN[ctx.phase]
        arm = RD.silhouette({"main": body}, ctx.size, K.mix(skin, (255, 200, 180), 0.5), PHOTO, body=skin, s=S * 1.5, glow_k=0.25)
        h = np.asarray(K.blur(body, 8 * S), np.float32) / 255
        nz = K.noise(ctx.size, int(10 * S), 19, 3)
        arm = K.tone_map(arm, np.ones_like(h), (0.4 + 0.85 * h) * (0.78 + 0.44 * nz))
        rc = RINGS[ctx.phase]
        rk = K.mask_mul(rings, body)
        glow_k = {1: 0.25, 2: 0.9, 3: 1.3}[ctx.phase] * (0.8 + 0.2 * math.sin(t * 3))
        arm.alpha_composite(K.solid(rk, rc, 0.55 + 0.3 * min(1, glow_k)))
        arm = K.add(arm, K.solid(K.blur(rk, 4 * S), rc), glow_k)
        arm.alpha_composite(K.solid(K.mask_mul(suck, body), (232, 196, 190), 0.95))
        out = K.rgba(ctx.size)
        out.alpha_composite(ticks)
        out.alpha_composite(K.solid(K.shifted(K.blur(body, 7 * S), 5 * S, 9 * S), (0, 0, 0), 0.65))
        out.alpha_composite(arm)
        return out

    def threat_ring(self, ctx):
        return None

    # -------- hub: the head (fixed) + the beak needle + the tucked arms
    def hub(self, ctx):
        return K.rgba(ctx.size)        # drawn by needle() so the head sits above the arms and plaques

    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        key = ("headD", ctx.S, ctx.phase, round(g, 2), tq, round(ctx.get("beak", 0), 2), round(ctx.get("blink", 0), 2),
               ctx.get("tier"), round(ctx.get("latch", 0), 2), ctx.get("landed"), ctx.get("forecast"), round(ctx.get("look", 0) or 0, 2))
        return self.cached(key, lambda: self._head(ctx, slots, g, tq))

    def _head(self, ctx, slots, g, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        out = K.rgba(ctx.size)
        out.alpha_composite(self.banner(ctx, 512, width=330))
        P = lambda x, y: (cx + x * S, cy + y * S)  # noqa: E731
        ph = ctx.phase
        skin = SKIN[ph]
        breathe = 4 * math.sin(t * 1.3)
        open_ = max(0.05, 1 - ctx.get("blink", 0.0))
        wide = {1: 0.0, 2: 0.25, 3: 0.4}[ph]
        # the tucked arms: two arms curl round the head and cup the beak; clench on a hit
        cl = max(0.0, g)
        tuck = Pen(ctx.size, 1.0)
        for sgn in (-1, 1):
            pts = [P(sgn * 84, 44), P(sgn * 74, 92 - 6 * cl), P(sgn * (46 - 10 * cl), 122), P(sgn * (26 - 6 * cl), 118 - 4 * cl),
                   P(sgn * (24 - 4 * cl), 102), P(sgn * 34, 98)]
            cl_ = K.catmull(pts, 8, False)
            tuck.d.polygon(K.stroke_poly(cl_, 34 * S, 7 * S), fill=255)
        tk = RD.silhouette({"main": tuck.m}, ctx.size, K.mix(skin, (255, 200, 180), 0.5), PHOTO, body=K.mul(skin, 0.85), s=S * 1.5, glow_k=0.2)
        hh = np.asarray(K.blur(tuck.m, 6 * S), np.float32) / 255
        tk = K.tone_map(tk, np.ones_like(hh), 0.45 + 0.8 * hh)
        # the mantle (head), high 3/4 from above: a bulb rising toward 12 o'clock
        head = Pen(ctx.size, 1.0)
        head.d.polygon(K.catmull([P(0, -168 - breathe), P(72, -146), P(104, -76), P(100, 8), P(70, 70), P(30, 96), P(-30, 96), P(-70, 70),
                                  P(-100, 8), P(-104, -76), P(-72, -146)], 10), fill=255)
        hm = head.m
        rel = RD.relief(hm, ctx.size, stone=K.mix(skin, (255, 160, 140), 0.18), shadow=K.mul(skin, 0.3), hi=K.mix(skin, (255, 220, 210), 0.5), s=S, depth=26)
        nz = K.noise(ctx.size, int(12 * S), 23, 3)
        rel = K.tone_map(rel, np.ones_like(nz), 0.78 + 0.44 * nz)
        # papillae + blue rings on the mantle
        dots = K.rgba(ctx.size)
        dd = ImageDraw.Draw(dots)
        r = K.rng(31)
        rc = RINGS[ph]
        for j in range(26):
            x, y = r.uniform(-80, 80), r.uniform(-170, 40)
            q = r.uniform(4, 9) * S
            xx, yy = P(x, y)
            dd.ellipse([xx - q, yy - q, xx + q, yy + q], outline=rc + (210,), width=max(1, int(2 * S)))
        gk = {1: 0.2, 2: 0.9, 3: 1.3}[ph] * (0.8 + 0.2 * math.sin(t * 3 + 1))
        rel.alpha_composite(K.masked(dots, hm))
        rel = K.add(rel, K.masked(K.blur(dots, 4 * S), hm), gk)
        # eyes: low on the head, at the sides, gold with a bar pupil; wider in phase 2/3
        eyes = K.rgba(ctx.size)
        for sgn in (-1, 1):
            ex, ey = P(sgn * 64, 18)
            erx, ery = 26 * S * (1 + wide * 0.3), 22 * S * open_ * (1 + wide)
            em = K.L(ctx.size)
            ImageDraw.Draw(em).ellipse([ex - erx, ey - ery, ex + erx, ey + ery], fill=255)
            icol = (255, 196, 70) if ph < 3 else (255, 70, 60)
            iris = K.rad_grad(ctx.size, ex, ey, erx, K.mix(icol, (255, 255, 255), 0.25), K.mul(icol, 0.4))
            iris.putalpha(em)
            rr_, aa_ = K.polar_field(ctx.size, ex, ey)
            streak = (0.6 + 0.4 * np.sin(np.radians(aa_) * 37)).astype(np.float32)
            iris = K.tone_map(iris, np.ones_like(streak), streak)
            eyes.alpha_composite(K.solid(K.grow(em, 5 * S), K.mul(skin, 0.4)))
            eyes.alpha_composite(iris)
            ed = ImageDraw.Draw(eyes)
            look = (ctx.get("look") or 0.0) * 6 * S
            pw = 14 * S * (1 - 0.3 * wide)
            ed.rounded_rectangle([ex - pw + look, ey - 4 * S * open_, ex + pw + look, ey + 4 * S * open_], radius=4 * S, fill=(4, 2, 6, 255))
            ed.ellipse([ex - 12 * S, ey - 12 * S * open_, ex - 5 * S, ey - 6 * S * open_], fill=(255, 255, 240, 230))
            # heavy lid
            lid = K.L(ctx.size)
            ImageDraw.Draw(lid).polygon([P(sgn * 64 - 36, 18 - 24 * open_), P(sgn * 64 + 36, 18 - 30 * open_ + sgn * 6), P(sgn * 64 + 36, -20), P(sgn * 64 - 36, -20)], fill=255)
            eyes.alpha_composite(K.solid(K.mask_mul(lid, K.grow(em, 6 * S)), K.mul(skin, 0.7)))
            if g > 0.3 or ph >= 2:
                eyes = K.add(eyes, K.solid(K.blur(em, 10 * S), icol), 0.5 * max(g, 0.5))
        # the beak: two dark mandibles, pointing DOWN at 6 o'clock; snaps open/shut
        bo = ctx.get("beak", 0.0)            # 0 shut .. 1 wide open
        beak = Pen(ctx.size, 1.0)
        tip_r = 142
        beak.d.polygon(K.catmull([P(-26, 84), P(26, 84), P(18, 112), P(0, tip_r), P(-18, 112)], 6), fill=255)
        upper = beak.m
        low = Pen(ctx.size, 1.0)
        a_ = math.radians(-26 * bo)
        def Q(x, y):
            x0, y0 = 0, 92
            return P(x0 + (x - x0) * math.cos(a_) - (y - y0) * math.sin(a_), y0 + (x - x0) * math.sin(a_) + (y - y0) * math.cos(a_))
        low.d.polygon(K.catmull([Q(-20, 92), Q(4, 92), Q(10, 112), Q(2, 132), Q(-14, 110)], 6), fill=255)
        bk = RD.relief(ImageChops.lighter(upper, low.m), ctx.size, stone=(40, 30, 30), shadow=(6, 4, 6), hi=(170, 150, 140), s=S, depth=4)
        # compose: tucked arms behind the head, head, eyes, beak, then the value window + latch
        sh = K.solid(K.shifted(K.blur(ImageChops.lighter(hm, tuck.m), 10 * S), 6 * S, 12 * S), (0, 0, 0), 0.6)
        out.alpha_composite(sh)
        out.alpha_composite(rel)
        out.alpha_composite(tk)
        out.alpha_composite(eyes)
        out.alpha_composite(bk)
        # value window on the head above the beak (the locked blade's live value)
        under = int(round(((self.pointer_angle - ctx.rot) % 360) / W.SLOT_DEG)) % len(slots)     # the slot under the beak
        sl = slots[ctx.get("landed") if ctx.get("landed") is not None else under]
        d = ImageDraw.Draw(out)
        wx, wy = P(0, 60)
        ww, wh = 36 * S, 24 * S
        d.rounded_rectangle([wx - ww / 2, wy - wh / 2, wx + ww / 2, wy + wh / 2], radius=4 * S, fill=(12, 10, 18, 255),
                            outline=K.TYPE_COL[sl["type"]] + (255,), width=max(1, int(2 * S)))
        txt = "1/0" if sl["type"] == "NULL" else ("" if sl.get("value") is None else str(sl["value"]))
        if txt:
            K.paste_c(out, K.text_img(txt, K.f_num(int(22 * S)), fill=(255, 255, 255)), wx, wy)
        else:
            K.paste_c(out, K.glyph(K.TYPE_GLYPH[sl["type"]], int(18 * S)), wx, wy)
        # name plate across the brow
        t1 = K.text_img(self.hub_name, K.f_ui(int(12 * S), b"Bold Condensed"), fill=(230, 240, 255), stroke=max(1, int(1.5 * S)))
        bx, by = P(0, -40)
        d.rounded_rectangle([bx - t1.width / 2 - 6 * S, by - t1.height / 2 - 2 * S, bx + t1.width / 2 + 6 * S, by + t1.height / 2 + 2 * S],
                            radius=4 * S, fill=(4, 8, 18, 200), outline=(90, 150, 255, 255))
        K.paste_c(out, t1, bx, by)
        # PERFECT latch: a gold ring clamps the beak tip; GOOD: a white tick ring
        tx, ty = P(0, tip_r)
        if ctx.get("latch", 0) > 0:
            k = ctx.get("latch")
            rr = (16 - 6 * k) * S
            d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], outline=K.PERFECT_GOLD + (255,), width=max(1, int(4 * S)))
        elif ctx.get("tier") == "GOOD":
            d.ellipse([tx - 10 * S, ty - 10 * S, tx + 10 * S, ty + 10 * S], outline=(255, 255, 255, 230), width=max(1, int(2 * S)))
        return out
