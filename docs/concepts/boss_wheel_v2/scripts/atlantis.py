"""Boss Wheel v2: Tethys Deep / THE BLACK SMOKER (hub THE VENT CAP). Three directions on the same template.

  A ABYSS      backlit silhouettes in deep water, the black-smoker vent field behind the wheel, the giant octopus's
               arms curling over the rim, its eye as the hub, an anglerfish lure as the needle.
  B PRESSURE   every slice is a riveted porthole onto the scene, a brass collar with gauges and an air hose over
               the rim, the diver's helmet as the hub, a little helmet on its tether as the needle.
  C BIOLUME    figures drawn in living light (edge-glow) on black water, jellyfish tendrils and coral crust over the
               rim, a pulsing jellyfish bell hub, an octopus arm tip curled round the needle.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import bw_kit as K
import fig_atlantis as F
import render2d as RD
import roman as RM
import wheel_v2 as W
from shapes import Pen

ABYSS = (47, 107, 255)
RED = (200, 38, 78)
TRENCH = (6, 17, 42)
PHOTO = (124, 242, 228)
DIVE = (255, 233, 184)
BRASS = (196, 150, 72)

NAME, SUB = "THE BLACK SMOKER", "TETHYS DEEP  |  BOSS  |  PHASE %d"
HUB_NAME = "THE VENT CAP"

SLOTS = [
    dict(type="SHIM", value=12, fig="diver", label="HARPOON"),
    dict(type="OVERFLOW", value=22, fig="angler", label="ANGLERFISH"),
    dict(type="SANDBOX", value=10, fig="dome", label="PRESSURE DOME"),
    dict(type="NULL", value=None, fig=None, label="BLANK"),
    dict(type="DETOUR", value=None, fig="octo_ink", label="INK CLOUD"),
    dict(type="INFECT", value=3, fig="jelly", label="STING"),
]
FIGS = {"diver": F.diver, "angler": F.angler, "dome": F.dome, "octo_ink": F.octo_ink, "jelly": F.jelly}
FIG_W = 330


class Base(RM.Base):
    corp = "tethys"
    name, hub_name = NAME, HUB_NAME
    mat = dict(base=(40, 56, 74), hi=(150, 180, 200), lo=(8, 12, 22), accent=ABYSS, glass=(4, 10, 26))
    telemetry = "THE BLACK SMOKER // TETHYS DEEP // THE VENT CAP // breathe easy // -412 m"

    def __init__(self, slots=SLOTS):
        super().__init__()
        self._slots = slots

    def threat_ring(self, ctx):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        hot = RED if ctx.phase < 3 else (255, 70, 60)
        r0, r1 = W.R["threat_in"] * S, W.R["threat_out"] * S
        d.ellipse([ctx.cx - r1, ctx.cy - r1, ctx.cx + r1, ctx.cy + r1], outline=(6, 10, 22, 230), width=int((r1 - r0)))
        spin = -ctx.t * 9 - ctx.rot * 0.5
        n = 36
        for k in range(n):
            a = k * 360 / n + spin
            if -26 < ((a + 180) % 360) - 180 < 26:
                continue
            p0 = K.pol(ctx.cx, ctx.cy, (r0 + r1) / 2, a - 2.2)
            p1 = K.pol(ctx.cx, ctx.cy, (r0 + r1) / 2 + 5 * S, a + 0.8)
            p2 = K.pol(ctx.cx, ctx.cy, (r0 + r1) / 2 - 5 * S, a + 0.8)
            d.line([p1, p0, p2], fill=hot + (220,), width=max(1, int(2.6 * S)))
        return im

    def banner(self, ctx, y_master, width=330, col=ABYSS):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        cx, cy = ctx.cx, ctx.cy - y_master * S
        w, h = width * S, 64 * S
        d.polygon([(cx - w / 2 - 14 * S, cy - h / 2), (cx + w / 2 + 14 * S, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)],
                  fill=(4, 10, 24, 245), outline=col + (255,))
        d.line([(cx - w / 2, cy + h / 2 - 3 * S), (cx + w / 2, cy + h / 2 - 3 * S)], fill=PHOTO + (120,), width=max(1, int(1.2 * S)))
        t1 = K.text_img(self.name, K.f_anton(int(33 * S)), fill=(255, 255, 255))
        t2 = K.text_img(SUB % ctx.phase, K.f_ui(int(13 * S), b"Bold Condensed"), fill=K.mix(col, (255, 255, 255), 0.3))
        K.paste_c(im, t1, cx, cy - 8 * S)
        K.paste_c(im, t2, cx, cy + 20 * S)
        return im


# ================================================================== shared water pieces
def water_bg(ctx, key, phase, seed, fx=0.0, fy=0.0, w=None, murk=(6, 17, 42), floor=True, rays=True):
    S = ctx.S
    w = w or W.scene_box(ctx)
    size = (w, w)
    top = K.mix(murk, ABYSS, 0.35) if phase < 3 else K.mix(murk, RED, 0.25)
    im = K.lin_grad(size, top, K.mul(murk, 0.5))
    hz = int(w * 0.62 + fy)
    gx, gy = w / 2 + fx, hz - 64 * S
    glow = K.rad_grad(size, gx, gy, w * 0.50, K.mix(key, (255, 255, 255), 0.35), (0, 0, 0), gamma=0.8)
    im = K.screen(im, K.tone(glow, 1.0, 0.95 if phase < 3 else 0.7))
    if rays:
        im.alpha_composite(RD.light_rays(size, gx - 40 * S, -40 * S, 7, w * 1.2, 12 * S, K.mix(PHOTO, (255, 255, 255), 0.3), seed, alpha=26, spread=14, ang0=8))
    # far silhouettes: vent chimneys and kelp
    far = K.L(size)
    fd = ImageDraw.Draw(far)
    r = K.rng(seed)
    for j in range(6):
        x = r.uniform(0, w)
        hh = r.uniform(60, 150) * S
        ww = r.uniform(10, 22) * S
        fd.polygon([(x - ww, hz + 4 * S), (x - ww * 0.5, hz - hh), (x + ww * 0.4, hz - hh * 0.92), (x + ww, hz + 4 * S)], fill=255)
    im.alpha_composite(K.solid(K.blur(far, 1.5 * S), K.mix(murk, key, 0.18), 0.85))
    if floor:
        fl = K.L(size)
        ImageDraw.Draw(fl).rectangle([0, hz, w, w], fill=255)
        im.alpha_composite(K.fill_grad(fl, K.mix((30, 40, 52), key, 0.18), (4, 6, 12), hz, w))
        pool = K.rad_grad(size, gx, hz + 12 * S, w * 0.32, K.mix(key, (255, 255, 255), 0.4), (0, 0, 0), gamma=1.1)
        im = K.screen(im, K.masked(K.tone(pool, 1.0, 0.45), fl))
    # marine snow
    sn = K.particles(size, 70, seed + 3, 0.5 * S, 1.5 * S, (200, 230, 255), (40, 150))
    im = K.add(im, sn, 1.0)
    return im, hz


# ================================================================== A ABYSS
class AbyssA(Base):
    key = "A"
    title = "A  ABYSS"
    blurb = ["The wheel hangs in the trench: the black smoker vents behind it, the giant octopus's",
             "arms curl over the rim, its eye is the hub, an anglerfish lure is the needle.",
             "Slices are backlit silhouettes in deep water, lit in the slice colour."]

    def back_plate(self, ctx):
        tq = round(ctx.t * 6) / 6.0 if not ctx.get("still") else 0.0
        return self.cached(("bp", ctx.S, ctx.phase, tq), lambda: self._back(ctx, tq))

    def _back(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        # a dark water disc behind the rim (aura) with the vent glow at the bottom
        aura = K.ring_mask(ctx.size, cx, cy, 0, 500 * S)
        aura = K.blur(aura, 30 * S)
        im.alpha_composite(K.solid(aura, (2, 8, 20), 0.85))
        vent = K.rad_grad(ctx.size, cx, cy + 470 * S, 300 * S, (255, 90, 40) if ctx.phase >= 2 else (200, 60, 50), (0, 0, 0), gamma=0.9)
        im = K.screen(im, K.masked(K.tone(vent, 1.0, 0.55 if ctx.phase == 1 else 0.85), aura))
        # chimneys: the black smokers rising behind the rim (bottom left and right)
        ch = K.L(ctx.size)
        cd = ImageDraw.Draw(ch)
        for (a, hgt, wd) in ((150, 120, 40), (205, 150, 48), (232, 90, 30), (128, 80, 26)):
            x, y = K.pol(cx, cy, 380 * S, a)
            cd.polygon([(x - wd * S, y + 90 * S), (x - wd * 0.4 * S, y - hgt * S), (x + wd * 0.35 * S, y - hgt * 0.9 * S), (x + wd * S, y + 90 * S)], fill=255)
        im.alpha_composite(K.solid(ch, (10, 10, 16)))
        im = K.add(im, K.solid(K.blur(K.rim_light(ch, 0, 4 * S, 1), 3 * S), (255, 100, 50)), 0.8)
        # smoke plumes rising (idle drift)
        sm = K.rgba(ctx.size)
        sd = ImageDraw.Draw(sm)
        r = K.rng(12)
        for j in range(26):
            base_a = [150, 205, 232][j % 3]
            x, y = K.pol(cx, cy, 380 * S, base_a)
            rise = ((t * 18 + j * 37) % 260) * S
            sx = x + math.sin(j + t * 0.7) * 20 * S
            rr = (18 + rise / S * 0.18) * S
            sd.ellipse([sx - rr, y - 120 * S - rise - rr, sx + rr, y - 120 * S - rise + rr], fill=(14, 12, 18, int(160 * (1 - rise / (260 * S)))))
        im.alpha_composite(K.blur(sm, 10 * S))
        # phase 2/3: the water darkens, red lights wake in the trench walls
        if ctx.phase >= 2:
            lights = K.particles(ctx.size, 40 if ctx.phase == 2 else 90, 31, 1.4 * S, 3 * S, RED, (120, 255), area=(0, 0, ctx.C, ctx.C))
            lights = K.masked(lights, K.ring_mask(ctx.size, cx, cy, 420 * S, 520 * S))
            im = K.add(im, K.blur(lights, 2 * S), 1.4)
        return im

    def art_ring_under(self, ctx):
        return self.cached(("under", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2)), lambda: self._under(ctx))

    def _under(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        n = K.noise(ctx.size, int(36 * S), 9, 4)
        base = np.array((18, 30, 46), np.float32) * (0.5 + 0.8 * n[..., None])
        ridges = 0.85 + 0.15 * np.sin(rr / (7 * S) + n * 6)
        base *= ridges[..., None]
        a = ((rr <= 356 * S) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(base, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        # tube worms + small vent glows scattered on the floor ring
        r = K.rng(4)
        wl = K.rgba(ctx.size)
        wd = ImageDraw.Draw(wl)
        for j in range(60):
            aa = r.uniform(0, 360)
            rad = r.uniform(150, 345)
            x, y = K.pol(cx, cy, rad * S, aa)
            wd.ellipse([x - 2 * S, y - 2 * S, x + 2 * S, y + 2 * S], fill=(255, 80, 90, 200))
        im = K.add(im, K.blur(wl, 1.5 * S), 1.0)
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(4, 6, 10), glow=(255, 90, 50)))
        return im

    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 12) / 12.0
        aq = round(act, 2)
        return self.cached(("sc", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._scene(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def _fig(self, slot, ctx, t, act, fw):
        key = K.TYPE_COL[slot["type"]]
        masks = FIGS[slot["fig"]](fw * 2, t, act)
        size2 = (fw * 2, int(fw * 2 * 0.75))
        if slot["fig"] == "dome":
            fig = RD.silhouette({k: v for k, v in masks.items() if k not in ("eye",)}, size2, key, PHOTO, body=(8, 14, 26),
                                haze=K.mix(TRENCH, key, 0.4), gilt=K.mix(key, (255, 255, 255), 0.4), s=2 * ctx.S * 1.2)
            glass = K.solid(masks["eye"], K.mix(key, (255, 255, 255), 0.2), 0.22)
            fig.alpha_composite(glass)
        else:
            fig = RD.silhouette(masks, size2, key, PHOTO, body=(6, 10, 20), haze=K.mix(TRENCH, key, 0.35),
                                gilt=BRASS if slot["fig"] == "diver" else K.mix(key, (255, 255, 255), 0.5),
                                s=2 * ctx.S * 1.2, eye_col=K.mix(DIVE, key, 0.3))
            if "ink" in masks:
                ink = K.solid(K.blur(masks["ink"], 6 * ctx.S), (4, 4, 10), 0.92)
                inkrim = K.solid(K.blur(K.rim_light(masks["ink"], 4 * ctx.S, -6 * ctx.S, 2), 4 * ctx.S), key, 0.7)
                base = K.rgba(size2)
                base.alpha_composite(ink)
                base.alpha_composite(inkrim)
                base.alpha_composite(fig)
                fig = base
        return fig.resize((fw, int(fw * 0.75)), Image.LANCZOS)

    def _scene(self, slot, ctx, t, act, i, style="abyss"):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        a = W.slot_angle(i, ctx.rot)
        off = 44 * S
        ox = -math.sin(math.radians(a)) * off
        oy = math.cos(math.radians(a)) * off
        bg, hz = water_bg(ctx, key, ctx.phase, 21 + i, fx=ox, fy=oy)
        fw = int(FIG_W * S)
        fig = self._fig(slot, ctx, t, act, fw)
        gx = w / 2 - fw / 2 + ox
        gy = hz + 18 * S - fig.height * (250 / 300)
        bg.alpha_composite(fig, (int(gx), int(gy)))
        if act > 0:
            bg = act_fx(bg, slot, act, S, w, hz, key)
        vg = K.vignette((w, w), w / 2, w / 2, w * 0.66, 0.4)
        bg.alpha_composite(K.solid(vg, (0, 0, 0)))
        return bg

    # tentacles of the giant octopus over the rim (static, idle sway)
    def art_ring_over(self, ctx):
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        return self.cached(("over", ctx.S, ctx.phase, tq), lambda: self._over(ctx, tq))

    def _over(self, ctx, t):
        return octo_arms(ctx, t, ctx.phase)

    def hub(self, ctx):
        look = 0.0 if ctx.get("still") else math.sin(ctx.t * 0.8)
        if ctx.get("look") is not None:
            look = ctx.get("look")
        bl = ctx.get("blink", 0.0)
        return self.cached(("hub", ctx.S, ctx.phase, round(look * 4) / 4, round(bl, 2), ctx.get("wrath", 0)),
                           lambda: self._hub(ctx, look, bl))

    def _hub(self, ctx, look, blink):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        im = K.rgba(ctx.size)
        disc = K.ring_mask(ctx.size, cx, cy, 0, R0)
        px = int(R0 * 2)
        wrath = ctx.get("wrath", 0.0)
        m = F.octo_eye(px * 2, ctx.t, look, blink, wrath)
        sz = (px * 2, px * 2)
        skin = RD.relief(m["main"], sz, stone=(110, 36, 60), shadow=(30, 6, 18), hi=(200, 90, 110), s=2 * S, depth=10)
        nz = K.noise(sz, int(20 * S), 3, 3)
        skin = K.tone_map(skin, np.ones_like(nz), 0.7 + 0.6 * nz)
        skin.alpha_composite(K.solid(m["detail"], (40, 8, 22), 0.75))
        iris_c = (255, 196, 70) if ctx.phase < 3 else (255, 70, 60)
        iris = K.rad_grad(sz, px, px, px * 0.46, K.mix(iris_c, (255, 255, 255), 0.2), K.mul(iris_c, 0.35))
        rr_, aa_ = K.polar_field(sz, px, px)
        streak = (0.6 + 0.4 * np.sin(np.radians(aa_) * 37 + np.sin(np.radians(aa_) * 7) * 3)) * (0.75 + 0.25 * np.cos(rr_ / (3 * S)))
        iris = K.tone_map(iris, np.ones_like(streak), streak.astype(np.float32))
        lid = K.rad_grad(sz, px, px, px * 0.48, (255, 255, 255), (0, 0, 0), gamma=3.0)
        iris = K.tone_map(iris, np.ones_like(streak), (np.asarray(lid.convert("L"), np.float32) / 255 * 0.7 + 0.3))
        iris.putalpha(m["eye"])
        skin.alpha_composite(iris)
        skin.alpha_composite(K.solid(m["pupil"], (4, 2, 6)))
        skin.alpha_composite(K.solid(m["glint"], (255, 255, 240), 0.9))
        skin = K.add(skin, K.solid(K.blur(m["eye"], 14 * S), iris_c), 0.35)
        skin = skin.resize((px, px), Image.LANCZOS)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(skin, (int(cx - px / 2), int(cy - px / 2)))
        im.alpha_composite(K.masked(lay, disc))
        self._hub_rim(ctx, im)
        return im

    def _hub_rim(self, ctx, im, rim_col=(30, 40, 56), hair=ABYSS):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        f = K.f_ui(int(12 * S), b"Bold Condensed")
        t1 = K.text_img(self.hub_name, f, fill=(230, 240, 255), stroke=max(1, int(1.5 * S)))
        pd = ImageDraw.Draw(im)
        pw, ph = t1.width + 12 * S, t1.height + 4 * S
        pd.rounded_rectangle([cx - pw / 2, cy + 80 * S - ph / 2, cx + pw / 2, cy + 80 * S + ph / 2], radius=4 * S, fill=(4, 8, 18, 220), outline=hair + (255,))
        K.paste_c(im, t1, cx, cy + 80 * S)
        d = ImageDraw.Draw(im)
        for rr_, col, wd in ((W.R["hub"] + 8, rim_col, 16), (W.R["hub"] + 3, K.mix(rim_col, (255, 255, 255), 0.4), 3), (W.R["hub"] + 13, hair, 2)):
            d.ellipse([cx - rr_ * S, cy - rr_ * S, cx + rr_ * S, cy + rr_ * S], outline=col + (255,), width=max(1, int(wd * S)))

    # needle: the anglerfish lure
    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndl", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"),
                            round(ctx.t * 6) / 6 if not ctx.get("still") else 0, ctx.get("landed"), ctx.get("forecast")),
                           lambda: self._needle(ctx, slots, g))

    def _needle(self, ctx, slots, g):
        """g > 0: hit -> the lure flares white-hot and the stalk snaps taut; g < 0: whiff/blocked -> the lure dims and
        droops; 0 = idle sway."""
        S = ctx.S
        im = K.rgba(ctx.size)
        cx, cy = ctx.cx, ctx.cy
        im.alpha_composite(self.banner(ctx, 560))
        RM.blade(im, ctx, slots, crown=True, col=(240, 236, 226), edge=PHOTO, latch=ctx.get("latch", 0.0), tier=ctx.get("tier"))
        sway = 0 if ctx.get("still") else math.sin(ctx.t * 1.3) * 6
        droop = max(0.0, -g)
        flare = max(0.0, g)
        top = (cx - 70 * S, cy - 528 * S)
        mid = (cx - 120 * S + sway * S, cy - 470 * S)
        bulb = (cx + sway * 0.4 * S, cy - (446 - 18 * droop) * S)
        st = Pen(ctx.size, 1.0)
        st.limb([top, (cx - 140 * S, cy - 500 * S), mid, (cx - 50 * S + sway * S, cy - 470 * S + droop * 20 * S), bulb], 15 * S, 6 * S)
        stalk = RD.silhouette({"main": st.m}, ctx.size, PHOTO, ABYSS, body=(16, 20, 34), s=S)
        im.alpha_composite(stalk)
        # the esca: a glowing bulb, filaments
        bc = K.mix(PHOTO, (255, 255, 255), 0.3 + 0.6 * flare)
        k = 1.0 - 0.6 * droop + 0.8 * flare
        rr = (19 + 6 * flare) * S
        bm = K.ring_mask(ctx.size, bulb[0], bulb[1], 0, rr)
        im.alpha_composite(K.solid(bm, K.mix((20, 40, 50), bc, max(0.2, min(1, k)))))
        im = K.add(im, K.solid(K.blur(bm, 16 * S), PHOTO), 1.4 * k)
        im = K.add(im, K.solid(K.blur(bm, 50 * S), PHOTO), 0.5 * k)
        d = ImageDraw.Draw(im)
        for q in range(5):
            a = math.radians(100 + q * 22)
            d.line([bulb, (bulb[0] + 22 * S * math.cos(a), bulb[1] + 22 * S * math.sin(a))], fill=bc + (int(180 * k) if k < 1.4 else 255,), width=max(1, int(1.4 * S)))
        return im

    def fx(self, ctx, slots):
        return None


# ------------------------------------------------------------------ the giant octopus's arms (over-rim art)
ARM_SETS = {   # (base angle, sweep deg, width) per phase: the octopus wakes, more arms grip the rim
    1: [(232, 58, 54), (128, -58, 54)],
    2: [(232, 62, 58), (128, -62, 58), (300, 30, 40), (60, -30, 40)],
    3: [(226, 70, 62), (134, -70, 62), (296, 36, 46), (64, -36, 46), (196, -40, 40), (164, 40, 40)],
}


def arm_line(ctx, a0, sweep, t, j, wake, r_base=540, r_rim=372):
    """Centre line of one arm: rises from behind the wheel (r_base), hugs the rim with an S-wave, then curls."""
    S = ctx.S
    pts = []
    n = 40
    sway = 4 * math.sin(t * 1.1 + j * 1.7) * wake
    for q in range(n + 1):
        u = q / n
        aa = a0 + (sweep + sway) * u
        rr = r_base + (r_rim - r_base) * min(1, u * 1.6) + 16 * math.sin(math.pi * u * 2.2 + t * 0.8 + j) * (0.3 + u)
        pts.append((aa, rr))
    # spiral curl at the tip, curling outward (away from the values)
    aa, rr = pts[-1]
    sgn = 1 if sweep > 0 else -1
    for q in range(1, 22):
        u = q / 21
        ang = math.radians(90 * sgn + u * 300 * sgn)
        rad = 34 * (1 - u * 0.75)
        da = math.degrees(rad * math.sin(ang) / rr) * 1.0
        pts.append((aa + sweep * 0.0 + da + sgn * 6 * u, rr + 26 - rad * math.cos(ang)))
    return [K.pol(ctx.cx, ctx.cy, r_ * S, a_) for a_, r_ in pts]


def octo_arms(ctx, t, phase, skin=(96, 24, 52), hi=(255, 110, 130), keep_gap=30):
    S = ctx.S
    cx, cy = ctx.cx, ctx.cy
    wake = {1: 1.0, 2: 1.3, 3: 1.6}[phase]
    body_m = K.L(ctx.size)
    suck_m = K.L(ctx.size)
    suck_c = K.L(ctx.size)
    bd = ImageDraw.Draw(body_m)
    sd = ImageDraw.Draw(suck_m)
    cd = ImageDraw.Draw(suck_c)
    for j, (a0, sweep, wd) in enumerate(ARM_SETS[phase]):
        cl = arm_line(ctx, a0, sweep, t, j, wake)
        n = len(cl)
        w0, w1 = wd * S, 3.5 * S
        L, R = [], []
        for i in range(n):
            x, y = cl[i]
            xa, ya = cl[max(0, i - 1)]
            xb, yb = cl[min(n - 1, i + 1)]
            dx, dy = xb - xa, yb - ya
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            u = i / (n - 1)
            w = (w0 + (w1 - w0) * (u ** 0.7)) / 2
            L.append((x + nx * w, y + ny * w))
            R.append((x - nx * w, y - ny * w))
            # suckers on the side facing the wheel centre
            if i % 3 == 1 and u < 0.9:
                tx, ty = cx - x, cy - y
                side = 1 if (nx * tx + ny * ty) > 0 else -1
                sx, sy = x + nx * w * 0.62 * side, y + ny * w * 0.62 * side
                sr = max(1.2 * S, w * 0.34)
                sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=255)
                cd.ellipse([sx - sr * 0.45, sy - sr * 0.45, sx + sr * 0.45, sy + sr * 0.45], fill=255)
        bd.polygon(L + R[::-1], fill=255)
        x, y = cl[-1]
        bd.ellipse([x - w1 / 2, y - w1 / 2, x + w1 / 2, y + w1 / 2], fill=255)
    body = RD.silhouette({"main": body_m}, ctx.size, hi, PHOTO, body=skin, s=S * 1.6, glow_k=0.35)
    # round the tube: dark core edge-to-edge shading via a blurred-mask height
    h = np.asarray(K.blur(body_m, 10 * S), np.float32) / 255
    nz = K.noise(ctx.size, int(12 * S), 17, 3)
    body = K.tone_map(body, np.ones_like(h), (0.45 + 0.75 * h) * (0.8 + 0.4 * nz))
    sk = K.mask_mul(suck_m, body_m)
    body.alpha_composite(K.solid(sk, (236, 200, 196)))
    body.alpha_composite(K.solid(K.mask_mul(suck_c, body_m), (120, 40, 64)))
    body.alpha_composite(K.solid(K.rim_light(sk, 0, -1.5 * S, 0.5), (255, 255, 255), 0.6))
    # fade the bases into the dark (they come from behind the wheel)
    rr, ang = K.polar_field(ctx.size, cx, cy)
    fade = np.clip((560 * S - rr) / (90 * S), 0, 1)
    a = np.asarray(body.split()[3], np.float32) * fade
    body.putalpha(Image.fromarray(a.astype(np.uint8)))
    out = K.rgba(ctx.size)
    out.alpha_composite(K.solid(K.shifted(K.blur(Image.fromarray(a.astype(np.uint8)), 8 * S), 6 * S, 10 * S), (0, 0, 0), 0.65))
    out.alpha_composite(body)
    if keep_gap:
        gap = K.ring_mask(ctx.size, cx, cy, 300 * S, 700 * S, -keep_gap, keep_gap)
        out.putalpha(ImageChops.subtract(out.split()[3], gap))
    return out


def act_fx(bg, slot, act, S, w, hz, key):
    fx = K.rgba((w, w))
    d = ImageDraw.Draw(fx)
    fig = slot["fig"]
    if fig == "diver":       # bubble trail behind the harpoon
        r = K.rng(3)
        for j in range(30):
            x = w * (0.45 + 0.5 * r.random() * act)
            y = hz - 120 * S + r.uniform(-10, 10) * S
            rr = r.uniform(1.5, 4) * S
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=K.mix(key, (255, 255, 255), 0.6) + (200,), width=max(1, int(S)))
    elif fig == "angler":    # shock ring at the jaws
        rr = (30 + 90 * act) * S
        d.ellipse([w * 0.72 - rr, hz - 110 * S - rr, w * 0.72 + rr, hz - 110 * S + rr], outline=K.mix(key, (255, 255, 255), 0.5) + (int(255 * (1 - act)),), width=max(1, int(5 * S)))
    elif fig == "dome":
        rr = (90 + 40 * act) * S
        d.ellipse([w / 2 - rr, hz - 60 * S - rr, w / 2 + rr, hz - 60 * S + rr], outline=key + (int(255 * (1 - act * 0.7)),), width=max(1, int(6 * S)))
    elif fig == "jelly":
        sp = K.particles((w, w), 40, 9, 1 * S, 3 * S, K.mix(key, (255, 255, 255), 0.5), (120, 255), area=(w * 0.2, hz - 20 * S, w * 0.8, hz + 60 * S))
        fx.alpha_composite(sp)
    return K.add(bg, K.blur(fx, 1.0 * S), 1.2)


DIRS = {"A": AbyssA}
