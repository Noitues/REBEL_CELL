"""Boss Wheel v2: Tethys Deep directions B (KRAKEN, octopus variant) and C (BIOLUME, the alternate)."""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import atlantis as AT
import bw_kit as K
import fig_atlantis as F
import render2d as RD
import roman as RM
import wheel_v2 as W
from shapes import Pen

ABYSS, RED, TRENCH, PHOTO, DIVE, BRASS = AT.ABYSS, AT.RED, AT.TRENCH, AT.PHOTO, AT.DIVE, AT.BRASS
PORT_R = 203      # porthole centre radius (master)
PORT_RAD = 86     # porthole radius


def brass(mask, size, s, depth=4):
    return RD.relief(mask, size, stone=(190, 140, 64), shadow=(60, 38, 14), hi=(255, 228, 160), s=s, depth=depth)


def octo_head(px, t=0.0, look=0.0, blink=0.0, wrath=0.0):
    """Front view of the octopus: the mantle dome, two eyes with bar pupils, the arm roots below. Box 400."""
    k = px / 400
    size = (px, px)
    pens = {n: Pen(size, k) for n in ("main", "detail", "eye", "pupil", "glint")}
    p, det, ey, pu, gl = (pens[n] for n in ("main", "detail", "eye", "pupil", "glint"))
    breathe = 6 * math.sin(t * 1.3)
    p.blob([(200, 40 - breathe), (282, 70), (318, 150), (306, 236), (262, 286), (200, 300), (138, 286), (94, 236), (82, 150), (118, 70)])
    for j in range(8):                     # arm roots spreading out of the frame at the bottom
        a = math.radians(200 + j * 20)
        x0, y0 = 200 + 70 * math.cos(a) * 0.9, 300
        p.limb([(x0, 270), (x0 + 140 * math.cos(math.radians(110 - j * 20 + 90)) * 0.6, 340), (x0 + 200 * math.cos(math.radians(110 - j * 20 + 90)), 420)], 40, 18)
    for j in range(16):
        det.dot((120 + (j * 53) % 170, 70 + (j * 37) % 150), 4 + j % 3)
    open_ = max(0.05, 1 - blink)
    for sgn in (-1, 1):
        x = 200 + sgn * 64
        inner, outer = x - sgn * 42, x + sgn * 42
        ey.ell(x, 210, 34, 26 * open_)
        drop = 10 + 8 * wrath
        ey.poly([(outer, 210 - 22), (inner, 210 - 4 + drop * 0.4), (inner, 150), (outer, 150)], fill=0)   # heavy lid: a glare
        det.limb([(outer + sgn * 6, 210 - 26), (x, 210 - 18), (inner - sgn * 4, 210 - 6 + drop * 0.4)], 15, 13)
        pw = 18 - 6 * wrath
        pu.rrect(x - pw + look * 8, 212 - 5 * open_, x + pw + look * 8, 212 + 5 * open_, 5 * open_)
        gl.ell(x - 10, 214, 4, 3 * open_)
    return {n: q.m for n, q in pens.items()}


# ================================================================== B KRAKEN
class KrakenB(AT.AbyssA):
    key = "B"
    title = "B  KRAKEN"
    blurb = ["The octopus has the station: every slice is a riveted porthole onto the scene, its arms",
             "coil round a brass pressure collar with gauges, its face fills the hub, and an arm",
             "tip curls round the needle (squeezes on a hit, lets go on a whiff)."]
    mat = dict(base=(120, 92, 50), hi=(240, 210, 150), lo=(34, 22, 12), accent=(222, 170, 80), glass=(4, 14, 18))

    def back_plate(self, ctx):
        return self.cached(("bpK", ctx.S, ctx.phase), lambda: self._backK(ctx))

    def _backK(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        aura = K.blur(K.ring_mask(ctx.size, cx, cy, 0, 480 * S), 20 * S)
        im.alpha_composite(K.solid(aura, (6, 12, 16), 0.92))
        # hull plates with rivet rows behind the rim
        d = ImageDraw.Draw(im)
        for k in range(12):
            a = k * 30
            for rr in range(404, 470, 14):
                x, y = K.pol(cx, cy, rr * S, a)
                d.ellipse([x - 2.5 * S, y - 2.5 * S, x + 2.5 * S, y + 2.5 * S], fill=(90, 80, 60, 200))
        if ctx.phase >= 2:
            lights = K.particles(ctx.size, 40 if ctx.phase == 2 else 90, 31, 1.4 * S, 3 * S, RED, (120, 255))
            im = K.add(im, K.blur(K.masked(lights, K.ring_mask(ctx.size, cx, cy, 420 * S, 520 * S)), 2 * S), 1.4)
        return im

    def art_ring_under(self, ctx):
        return self.cached(("underK", ctx.S, round(ctx.get("dmg", 0), 2)), lambda: self._underK(ctx))

    def _underK(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        im.alpha_composite(K.solid(K.ring_mask(ctx.size, cx, cy, 0, 356 * S), (14, 20, 24)))
        pipes = Pen(ctx.size, 1.0)
        for rr in (160, 196, 300, 336):
            pipes.d.ellipse([cx - rr * S, cy - rr * S, cx + rr * S, cy + rr * S], outline=255, width=max(1, int(12 * S)))
        im.alpha_composite(brass(pipes.m, ctx.size, S, depth=4))
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(4, 6, 10), glow=(255, 90, 50)))
        return im

    def _porthole(self, ctx, i, rot, wm, empty=False):
        S = ctx.S
        a = W.slot_angle(i, rot)
        px, py = ctx.P(PORT_R, a)
        R_ = PORT_RAD * S
        lay = K.rgba(ctx.size)
        hole = K.ring_mask(ctx.size, px, py, 0, R_)
        plate = ImageChops.subtract(wm, hole)
        nz = K.noise(ctx.size, int(30 * S), 40 + i, 3)
        steel = K.solid(plate, (40, 46, 50))
        steel = K.tone_map(steel, np.ones_like(nz), 0.7 + 0.5 * nz)
        lay.alpha_composite(steel)
        # rivets along the plate's edges
        d = ImageDraw.Draw(lay)
        for rr in range(150, 350, 22):
            for da in (-25, 25):
                x, y = ctx.P(rr, a + da * (1 - 8 / rr))
                d.ellipse([x - 3 * S, y - 3 * S, x + 3 * S, y + 3 * S], fill=(120, 110, 90, 255))
        ring = K.ring_mask(ctx.size, px, py, R_ - 2 * S, R_ + 13 * S)
        lay.alpha_composite(K.solid(K.shifted(K.blur(ring, 5 * S), 3 * S, 5 * S), (0, 0, 0), 0.7))
        lay.alpha_composite(brass(ring, ctx.size, S, depth=4))
        for k in range(8):
            x, y = K.pol(px, py, R_ + 6 * S, k * 45 + 22.5)
            bm = K.ring_mask(ctx.size, x, y, 0, 4 * S)
            lay.alpha_composite(brass(bm, ctx.size, S, depth=2))
        # glass: inner shadow + a curved reflection
        inner = ImageChops.subtract(hole, K.shrink(hole, 14 * S))
        lay.alpha_composite(K.solid(K.blur(inner, 8 * S), (0, 0, 0), 0.8))
        rf = K.ring_mask(ctx.size, px, py, R_ * 0.72, R_ * 0.8, 300, 350)
        lay.alpha_composite(K.solid(K.blur(rf, 2 * S), (255, 255, 255), 0.35))
        if empty:
            lay.alpha_composite(K.solid(hole, (2, 6, 10), 0.55))
            em = K.ring_mask(ctx.size, px, py, R_ - 16 * S, R_ - 14 * S)
            lay.alpha_composite(K.solid(em, (90, 96, 110), 0.9))
        return K.masked(lay, wm)

    def slice_glass(self, ctx, i, rot, wm, slot):
        return self._porthole(ctx, i, rot, wm)

    def blank_window(self, ctx, i, rot, wm, back, under):
        lay = W.default_blank(self, ctx, i, rot, wm, back, under)
        lay.alpha_composite(self._porthole(ctx, i, rot, wm, empty=True))
        return lay

    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 12) / 12.0
        aq = round(act, 2)
        return self.cached(("scK", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._sceneK(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def _sceneK(self, slot, ctx, t, act, i):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        a = W.slot_angle(i, ctx.rot)
        off = (W.R["sl_in"] + W.R["sl_out"]) / 2 + 6 - PORT_R
        ox, oy = -math.sin(math.radians(a)) * off * S, math.cos(math.radians(a)) * off * S
        bg, hz = AT.water_bg(ctx, key, ctx.phase, 61 + i, fx=ox, fy=oy - 10 * S, murk=(4, 30, 30))
        fw = int(AT.FIG_W * 0.62 * S)
        fig = self._fig(slot, ctx, t, act, fw)
        gx = w / 2 - fw / 2 + ox
        gy = hz + 14 * S - fig.height * (250 / 300)
        bg.alpha_composite(fig, (int(gx), int(gy)))
        if act > 0:
            bg = AT.act_fx(bg, slot, act, S, w, hz, key)
        return bg

    def art_ring_over(self, ctx):
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        return self.cached(("overK", ctx.S, ctx.phase, tq, round(ctx.get("dmg", 0), 2)), lambda: self._overK(ctx, tq))

    def _overK(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        out = K.rgba(ctx.size)
        collar = K.ring_mask(ctx.size, cx, cy, 428 * S, 452 * S)
        out.alpha_composite(K.solid(K.shifted(K.blur(collar, 6 * S), 4 * S, 6 * S), (0, 0, 0), 0.6))
        out.alpha_composite(brass(collar, ctx.size, S, depth=5))
        d = ImageDraw.Draw(out)
        for k in range(48):
            x, y = K.pol(cx, cy, 440 * S, k * 7.5)
            d.ellipse([x - 3 * S, y - 3 * S, x + 3 * S, y + 3 * S], fill=(90, 60, 20, 255))
        # pressure gauges on the collar: the needle in each gauge creeps toward red with the phase
        for a_ in (124, 236, 300):
            x, y = K.pol(cx, cy, 440 * S, a_)
            gm = K.ring_mask(ctx.size, x, y, 0, 30 * S)
            out.alpha_composite(brass(gm, ctx.size, S, depth=4))
            face = K.ring_mask(ctx.size, x, y, 0, 22 * S)
            out.alpha_composite(K.solid(face, (236, 230, 210)))
            d = ImageDraw.Draw(out)
            d.arc([x - 18 * S, y - 18 * S, x + 18 * S, y + 18 * S], 300, 30, fill=RED + (255,), width=max(1, int(4 * S)))
            na = -120 + 70 * ctx.phase + 8 * math.sin(t * 3 + a_)
            d.line([(x, y), K.pol(x, y, 17 * S, na)], fill=(20, 20, 20, 255), width=max(1, int(2.5 * S)))
        arms = AT.octo_arms(ctx, t, ctx.phase, skin=(120, 30, 40), hi=(255, 120, 90))
        out.alpha_composite(arms)
        if ctx.get("dmg", 0) > 0.3:
            cr = W.crack_layer(ctx, ctx.get("dmg"), 426, 454, 71, col=(30, 18, 8), glow=(255, 120, 40))
            out.alpha_composite(K.masked(cr, collar))
        return out

    def hub(self, ctx):
        look = 0.0 if ctx.get("still") else math.sin(ctx.t * 0.8)
        if ctx.get("look") is not None:
            look = ctx.get("look")
        bl = ctx.get("blink", 0.0)
        return self.cached(("hubK", ctx.S, ctx.phase, round(look * 4) / 4, round(bl, 2), round(ctx.t * 4) / 4 if not ctx.get("still") else 0),
                           lambda: self._hubK(ctx, look, bl))

    def _hubK(self, ctx, look, blink):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        im = K.rgba(ctx.size)
        disc = K.ring_mask(ctx.size, cx, cy, 0, R0)
        im.alpha_composite(K.masked(K.rad_grad(ctx.size, cx, cy - 30 * S, R0, (20, 50, 60), (2, 10, 14)), disc))
        px = int(R0 * 2.1)
        sz = (px * 2, px * 2)
        m = octo_head(px * 2, ctx.t if not ctx.get("still") else 0, look, blink, 1.0 if ctx.phase >= 3 else 0.0)
        skin = RD.relief(m["main"], sz, stone=(118, 30, 44), shadow=(28, 4, 12), hi=(214, 96, 96), s=2 * S, depth=12)
        nz = K.noise(sz, int(16 * S), 5, 3)
        skin = K.tone_map(skin, np.ones_like(nz), 0.75 + 0.5 * nz)
        skin.alpha_composite(K.solid(K.mask_mul(m["detail"], m["main"]), (60, 10, 20), 0.7))
        iris_c = (255, 196, 70) if ctx.phase < 3 else (255, 70, 60)
        rr_, aa_ = K.polar_field(sz, px, px)
        iris = K.solid(m["eye"], iris_c)
        streak = (0.55 + 0.45 * np.sin(np.radians(aa_) * 41)).astype(np.float32)
        iris = K.tone_map(iris, np.ones_like(streak), 0.6 + 0.4 * streak)
        skin.alpha_composite(iris)
        skin.alpha_composite(K.solid(m["pupil"], (4, 2, 6)))
        skin.alpha_composite(K.solid(m["glint"], (255, 255, 240), 0.9))
        skin = K.add(skin, K.solid(K.blur(m["eye"], 10 * S), iris_c), 0.5)
        skin = skin.resize((px, px), Image.LANCZOS)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(skin, (int(cx - px / 2), int(cy - px * 0.48)))
        im.alpha_composite(K.masked(lay, disc))
        self._hub_rim(ctx, im, rim_col=(110, 80, 40), hair=(222, 170, 80))
        return im

    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndlK", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"),
                            round(ctx.t * 6) / 6 if not ctx.get("still") else 0, ctx.get("landed"), ctx.get("forecast")),
                           lambda: self._needleK(ctx, slots, g))

    def _needleK(self, ctx, slots, g):
        """An arm tip curls round the blade shank. g > 0 hit: it squeezes tight, suckers flush red;
        g < 0 whiff: it lets go and recoils upward; 0: a lazy coil."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        im.alpha_composite(self.banner(ctx, 600, col=(222, 170, 80)))
        RM.blade(im, ctx, slots, crown=True, col=(240, 236, 226), edge=(222, 170, 80), latch=ctx.get("latch", 0.0), tier=ctx.get("tier"), root_r=470)
        sway = 0 if ctx.get("still") else math.sin(ctx.t * 1.2) * 4
        tight = max(0.0, g)
        let = max(0.0, -g)
        pts = [(cx - 150 * S, cy - 566 * S), (cx - 120 * S + sway * S, cy - 520 * S), (cx - 60 * S, cy - 494 * S)]
        # the coil round the shank (r ~ 440-470): an ellipse sampled, radius shrinks when squeezing
        rx = (30 - 10 * tight + 26 * let) * S
        ry = 10 * S
        yc = cy - (448 + 50 * let) * S
        for q in range(14):
            a = math.radians(180 + q * 30)
            pts.append((cx + rx * math.cos(a), yc + ry * math.sin(a) - q * 2.2 * S))
        tip = pts[-1]
        pts += [(tip[0] + 14 * S, tip[1] - 10 * S), (tip[0] + 22 * S, tip[1] - 2 * S)]
        p = Pen(ctx.size, 1.0)
        sk = Pen(ctx.size, 1.0)
        F.tentacle(p, pts, 30 * S, 4 * S, suckers=sk, sk=1.0)
        body = RD.silhouette({"main": p.m}, ctx.size, (255, 120, 90), PHOTO, body=(120, 30, 40), s=S * 1.4, glow_k=0.3)
        h = np.asarray(K.blur(p.m, 6 * S), np.float32) / 255
        body = K.tone_map(body, np.ones_like(h), 0.5 + 0.7 * h)
        sc = (255, 90, 90) if tight > 0.3 else (236, 200, 196)
        body.alpha_composite(K.solid(K.mask_mul(sk.m, p.m), sc))
        im.alpha_composite(K.solid(K.shifted(K.blur(p.m, 5 * S), 4 * S, 6 * S), (0, 0, 0), 0.6))
        im.alpha_composite(body)
        return im


# ================================================================== C BIOLUME (the alternate)
class BiolumeC(AT.AbyssA):
    key = "C"
    title = "C  BIOLUME (alternate)"
    blurb = ["The alternate: everything is living light on black water. Figures are drawn as",
             "bioluminescent outlines in the slice colour, jellyfish tendrils and a coral crust",
             "hang over the rim, a jellyfish bell pulses in the hub, a diver's helmet on its tether is the needle."]
    mat = dict(base=(20, 30, 50), hi=(90, 130, 180), lo=(2, 6, 14), accent=PHOTO, glass=(2, 6, 16))

    def back_plate(self, ctx):
        tq = round(ctx.t * 6) / 6.0 if not ctx.get("still") else 0.0
        return self.cached(("bpC", ctx.S, ctx.phase, tq), lambda: self._backC(ctx, tq))

    def _backC(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        aura = K.blur(K.ring_mask(ctx.size, cx, cy, 0, 500 * S), 24 * S)
        im.alpha_composite(K.solid(aura, (0, 4, 12), 0.95))
        r = K.rng(8)
        dots = K.rgba(ctx.size)
        d = ImageDraw.Draw(dots)
        for j in range(160):
            a = r.uniform(0, 360)
            rr = r.uniform(380, 520)
            x, y = K.pol(cx, cy, rr * S, a + t * 2 * (1 if j % 2 else -1))
            q = r.uniform(1, 2.6) * S
            c = PHOTO if j % 5 else (RED if ctx.phase >= 2 else ABYSS)
            d.ellipse([x - q, y - q, x + q, y + q], fill=c + (int(r.uniform(60, 220)),))
        im = K.add(im, K.blur(dots, 1.4 * S), 1.3)
        return im

    def art_ring_under(self, ctx):
        return self.cached(("underC", ctx.S, round(ctx.get("dmg", 0), 2)), lambda: self._underC(ctx))

    def _underC(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        im.alpha_composite(K.solid(K.ring_mask(ctx.size, cx, cy, 0, 356 * S), (1, 4, 10)))
        for rr in range(150, 350, 28):
            ring = K.ring_mask(ctx.size, cx, cy, (rr - 1) * S, (rr + 1) * S)
            im = K.add(im, K.solid(K.blur(ring, 2 * S), ABYSS), 0.35)
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(0, 0, 0), glow=RED))
        return im

    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 12) / 12.0
        aq = round(act, 2)
        return self.cached(("scBC", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._sceneC(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def _sceneC(self, slot, ctx, t, act, i):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        a = W.slot_angle(i, ctx.rot)
        off = 44 * S
        ox, oy = -math.sin(math.radians(a)) * off, math.cos(math.radians(a)) * off
        bg = K.lin_grad((w, w), (2, 8, 22), (0, 2, 6))
        glow = K.rad_grad((w, w), w / 2 + ox, w / 2 + oy - 10 * S, w * 0.45, K.mul(key, 0.35), (0, 0, 0), gamma=1.2)
        bg = K.screen(bg, glow)
        sn = K.particles((w, w), 60, 70 + i, 0.5 * S, 1.6 * S, K.mix(key, PHOTO, 0.5), (40, 180))
        bg = K.add(bg, sn, 1.0)
        fw = int(AT.FIG_W * S)
        masks = AT.FIGS[slot["fig"]](fw * 2, t, act)
        if slot["fig"] == "dome":
            masks = {k_: v for k_, v in masks.items() if k_ != "eye"}
        size2 = (fw * 2, int(fw * 2 * 0.75))
        fig = RD.emissive(masks, size2, K.mix(key, (255, 255, 255), 0.15), s=2 * S, body_k=0.22 + 0.3 * act)
        if "ink" in masks:
            fig2 = K.solid(K.blur(masks["ink"], 8 * S), (0, 0, 0), 0.9)
            fig2.alpha_composite(fig)
            fig = fig2
        fig = fig.resize((fw, int(fw * 0.75)), Image.LANCZOS)
        hz = w * 0.62 + oy
        bg.alpha_composite(fig, (int(w / 2 - fw / 2 + ox), int(hz + 18 * S - fig.height * (250 / 300))))
        if act > 0:
            bg = AT.act_fx(bg, slot, act, S, w, hz, key)
        return bg

    def art_ring_over(self, ctx):
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        return self.cached(("overBC", ctx.S, ctx.phase, tq), lambda: self._overC(ctx, tq))

    def _overC(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        lines = Pen(ctx.size, 1.0)
        n = 22 if ctx.phase == 1 else 34
        for j in range(n):
            a0 = 40 + j * (280 / n)
            if 150 < a0 < 210:
                continue
            x0, y0 = K.pol(cx, cy, 404 * S, a0)
            ln = (90 + 40 * math.sin(j * 1.7)) * S
            pts = []
            for q in range(9):
                u = q / 8
                sway = math.sin(t * 1.4 + j * 0.7 + u * 3) * 10 * S * u
                pts.append((x0 + sway + (x0 - cx) / max(1, abs(x0 - cx)) * 6 * S * u, y0 + ln * u))
            lines.d.line(pts, fill=255, width=max(1, int(2.2 * S)), joint="curve")
        tl = lines.m
        out = K.rgba(ctx.size)
        out = K.add(out, K.solid(K.blur(tl, 4 * S), PHOTO), 1.0)
        out.alpha_composite(K.solid(tl, K.mix(PHOTO, (255, 255, 255), 0.4), 0.9))
        # coral crust along the lower rim (grows with the phase)
        coral = Pen(ctx.size, 1.0)
        r = K.rng(14)
        count = {1: 30, 2: 60, 3: 90}[ctx.phase]
        for j in range(count):
            a = r.uniform(100, 260)
            if 150 < a < 210 and r.random() < 0.7:
                continue
            rr = r.uniform(400, 432)
            x, y = K.pol(cx, cy, rr * S, a)
            q = r.uniform(3, 9) * S
            coral.d.ellipse([x - q, y - q, x + q, y + q], fill=255)
        cm = coral.m
        cr = K.solid(cm, (60, 16, 40))
        cr.alpha_composite(K.solid(K.rim_light(cm, 0, -2 * S, 1), (255, 120, 160)))
        out.alpha_composite(cr)
        out = K.add(out, K.solid(K.blur(cm, 6 * S), (255, 80, 140)), 0.35)
        gap = K.ring_mask(ctx.size, cx, cy, 300 * S, 700 * S, -30, 30)
        a = ImageChops.subtract(out.split()[3], gap)
        out.putalpha(a)
        return out

    def hub(self, ctx):
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        return self.cached(("hubBC", ctx.S, ctx.phase, tq), lambda: self._hubC(ctx, tq))

    def _hubC(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        im = K.rgba(ctx.size)
        disc = K.ring_mask(ctx.size, cx, cy, 0, R0)
        im.alpha_composite(K.solid(disc, (1, 4, 12)))
        px = int(R0 * 2.4)
        m = F.jelly(px * 2, t, 0.0, scale=1.25)
        size2 = (px * 2, int(px * 2 * 0.75))
        col = PHOTO if ctx.phase < 3 else (255, 90, 120)
        fig = RD.emissive(m, size2, col, s=2 * S, body_k=0.3)
        fig = fig.resize((px, int(px * 0.75)), Image.LANCZOS)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(fig, (int(cx - px / 2), int(cy - px * 0.42)))
        im.alpha_composite(K.masked(lay, disc))
        self._hub_rim(ctx, im, rim_col=(20, 34, 54), hair=PHOTO)
        return im

    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndlBC", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"),
                            round(ctx.t * 6) / 6 if not ctx.get("still") else 0, ctx.get("landed"), ctx.get("forecast")),
                           lambda: self._needleC(ctx, slots, g))

    def _needleC(self, ctx, slots, g):
        """A diver's helmet on its air tether: hit -> the port flares red and bubbles burst; whiff -> the port goes
        dark and the helmet swings."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        im.alpha_composite(self.banner(ctx, 610, col=PHOTO))
        RM.blade(im, ctx, slots, crown=True, col=(236, 240, 244), edge=PHOTO, latch=ctx.get("latch", 0.0), tier=ctx.get("tier"), root_r=470)
        swing = (math.sin(ctx.t * 1.1) * 3 if not ctx.get("still") else 0) + (-10 * max(0, -g))
        hx, hy = K.pol(cx, cy - 560 * S, 70 * S, 180 + swing)
        d = ImageDraw.Draw(im)
        d.line([(cx, cy - 578 * S), (hx, hy - 30 * S)], fill=(70, 80, 90, 255), width=max(1, int(4 * S)))
        hp = int(110 * S)
        m = F.helmet_front(hp * 2)
        sz = (hp * 2, hp * 2)
        hel = brass(m["main"], sz, 2 * S, depth=5)
        hel.alpha_composite(K.mask_mul(brass(m["glint"], sz, 2 * S, depth=2), K.L(sz, 255)) if False else brass(m["glint"], sz, 2 * S, depth=2))
        port = (255, 60, 70) if g > 0.3 else ((20, 30, 40) if g < -0.3 else K.mix(PHOTO, DIVE, 0.5))
        hel.alpha_composite(K.solid(m["eye"], port))
        hel.alpha_composite(K.solid(K.mask_mul(m["detail"], m["eye"]), (40, 30, 20)))
        if g >= -0.3:
            hel = K.add(hel, K.solid(K.blur(m["eye"], 12 * S), port), 0.9)
        hel = hel.resize((hp, hp), Image.LANCZOS)
        im.alpha_composite(K.drop_shadow(hel, int(4 * S), int(6 * S), 5 * S), (int(hx - hp / 2), int(hy - hp / 2)))
        # bubbles
        r = K.rng(int(ctx.t * 4) + 3)
        nb = 4 + int(14 * max(0, g))
        for j in range(nb):
            bx = hx + r.uniform(-20, 20) * S
            by = hy - 40 * S - r.uniform(0, 80) * S
            q = r.uniform(2, 6) * S
            d = ImageDraw.Draw(im)
            d.ellipse([bx - q, by - q, bx + q, by + q], outline=K.mix(PHOTO, (255, 255, 255), 0.5) + (200,), width=max(1, int(1.2 * S)))
        return im
