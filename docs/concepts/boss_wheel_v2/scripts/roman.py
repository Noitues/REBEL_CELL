"""Boss Wheel v2: Aurelian Concord / THE ROSTRUM (hub THE GRAND STAND). Three directions on one template.

  A ARENA      the wheel is the arena seen from above: stands + crowd around the rim, sand under the slices,
               backlit silhouette scenes, an arcade crown over the rim, the pulvinar needle with the emperor's arm,
               a marble bust hub.
  B MOSAIC     slices are floor mosaics (tesserae, gilt grout lines), a meander mosaic ring under, a gilt laurel
               wreath over the rim, an aureus coin hub, the colossal gilt hand as the pointer.
  C FRIEZE     slices are carved travertine reliefs lit by verdigris neon from below, a rotunda of columns behind,
               broken colossus hands gripping the rim, a marble bust hub, a bronze rostrum (ship's ram) needle
               with the arm above it.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import bw_kit as K
import fig_roman as F
import render2d as RD
import emoji_hand as EH
import wheel_v2 as W
from shapes import Pen

VERD = (41, 219, 166)
TRAV = (233, 213, 170)
PORPH = (58, 20, 38)
GILT = (201, 163, 90)
MARBLE = (243, 239, 230)
HOT = (255, 92, 60)

NAME, SUB = "THE ROSTRUM", "AURELIAN CONCORD  |  BOSS  |  PHASE %d"
FIG_W = 340          # figure width in master units (the slice is ~245 wide at r 245)
HUB_NAME = "THE GRAND STAND"

SLOTS = [  # slot 0 sits under the needle at rot 0; clockwise
    dict(type="SHIM", value=14, fig="chariot", label="CHARIOT"),
    dict(type="OVERFLOW", value=24, fig="lion", label="LION"),
    dict(type="DEFRAG", value=12, fig="testudo", label="TESTUDO"),
    dict(type="NULL", value=None, fig=None, label="BLANK"),
    dict(type="SANDBOX", value=8, fig="secutor", label="SECUTOR"),
    dict(type="INFECT", value=3, fig="crowd", label="VERDICT", glyph="verdict"),
]
FIGS = {"chariot": F.chariot, "lion": F.lion, "testudo": F.testudo, "secutor": F.secutor, "crowd": F.crowd}


def thumb_mask(px=512):
    """VERDICT glyph (from new_corps nc_kit.thumb_down / g_verdict3, redrawn here): the thumbs-down, toga cuff on top."""
    m = Image.new("L", (512, 512), 0)
    d = ImageDraw.Draw(m)
    cx, cy, s = 198, 250, 1.48

    def R_(x0, y0, x1, y1, r, fill=255):
        d.rounded_rectangle([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s], radius=r * s, fill=fill)
    R_(-70, -150, 90, -96, 8)
    d.line([(cx - 70 * s, cy - 110 * s), (cx + 90 * s, cy - 110 * s)], fill=0, width=int(8 * s))
    R_(-70, -92, 70, 60, 26)
    for k in range(4):
        y0 = -90 + k * 38
        R_(30, y0, 128, y0 + 40, 20)
        d.line([(cx + 40 * s, cy + (y0 + 40) * s), (cx + 120 * s, cy + (y0 + 40) * s)], fill=0, width=int(7 * s))
    R_(-70, 0, -8, 190, 30)
    d.line([(cx - 64 * s, cy + 52 * s), (cx - 14 * s, cy + 52 * s)], fill=0, width=int(8 * s))
    return m.resize((px, px), Image.LANCZOS)


_THUMB = None


def special_mask(slot):
    global _THUMB
    if slot.get("glyph") == "verdict":
        if _THUMB is None:
            _THUMB = thumb_mask()
        return _THUMB
    return None


# ================================================================== shared Roman pieces
class Base:
    corp = "aurelian"
    name, hub_name = NAME, HUB_NAME
    mat = dict(base=(150, 128, 98), hi=(240, 226, 192), lo=(46, 32, 30), accent=VERD, glass=(10, 22, 20))
    telemetry = "THE ROSTRUM // AURELIAN CONCORD // THE GRAND STAND // VERDICT"
    key = "A"

    def __init__(self):
        self._cache = {}

    # ---- caching helper
    def cached(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def plaque(self, ctx, slot, i):
        return self.cached(("plq", ctx.S, i, slot.get("value"), ctx.get("values_dim", False)),
                           lambda: W.plaque(ctx, slot, special_mask(slot)))

    def slice_glass(self, ctx, i, rot, wm, slot):
        return W.default_glass(ctx, i, rot, wm)

    def blank_window(self, ctx, i, rot, wm, back, under):
        return W.default_blank(self, ctx, i, rot, wm, back, under)

    def rail(self, ctx, slots):
        tier = ctx.get("tier")
        sl = slots[ctx.get("forecast") if ctx.get("forecast") is not None else 0]
        if ctx.get("landed") is not None:
            sl = slots[ctx.get("landed")]
        txt = sl["type"] + ("" if sl.get("value") is None else " %d" % sl["value"])
        col = K.TYPE_COL[sl["type"]]
        if tier == "PERFECT":
            return (txt + " // PERFECT", K.PERFECT_GOLD)
        if tier == "GOOD":
            return (txt + " // GOOD", (235, 235, 240))
        if tier == "WEAK":
            return (txt + " // WEAK x0.5", (255, 176, 0))
        return (txt + " //", col)

    def bezel(self, ctx):
        rail = self.rail(ctx, self._slots)
        return W.bezel(ctx, self.mat, self.telemetry, rail=rail, cracks=ctx.get("dmg", 0.0), seed=31, rail_at=getattr(self, "pointer_angle", 0.0))

    def threat_ring(self, ctx):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        hot = (255, 64, 72) if ctx.phase < 3 else (255, 120, 40)
        r0, r1 = W.R["threat_in"] * S, W.R["threat_out"] * S
        d.ellipse([ctx.cx - r1, ctx.cy - r1, ctx.cx + r1, ctx.cy + r1], outline=(30, 10, 14, 230), width=int((r1 - r0)))
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

    def fx(self, ctx, slots):
        return None

    # ---- name banner (D4 boss extra) used by directions whose rig has no architrave
    def banner(self, ctx, y_master, width=300, col=VERD):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        cx, cy = ctx.cx, ctx.cy - y_master * S
        w, h = width * S, 62 * S
        d.polygon([(cx - w / 2 - 14 * S, cy - h / 2), (cx + w / 2 + 14 * S, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)],
                  fill=(16, 10, 16, 245), outline=col + (255,))
        t1 = K.text_img(self.name, K.f_anton(int(34 * S)), fill=(255, 255, 255))
        t2 = K.text_img(SUB % ctx.phase, K.f_ui(int(13 * S), b"Bold Condensed"), fill=col)
        K.paste_c(im, t1, cx, cy - 8 * S)
        K.paste_c(im, t2, cx, cy + 20 * S)
        return im


def arena_bg(ctx, key, phase, seed, style="dusk", w=None, fx=None, fy=0.0):
    """Scene background sprite: dusk sky in porphyry, a type-coloured sun of light behind the figure, distant arena
    tiers, raked sand. Returned square sprite of size `w`."""
    S = ctx.S
    w = w or W.scene_box(ctx)
    size = (w, w)
    sky_top = (26, 10, 22) if phase < 3 else (40, 10, 10)
    sky_mid = K.mix(PORPH, key, 0.30)
    im = K.lin_grad(size, sky_top, sky_mid)
    hz = int(w * 0.57 + fy)
    gx, gy = (w / 2 + (fx or 0.0), hz - 50 * S)
    # backlight: a big bright disc of the TYPE colour behind the figure (the silhouette reads against it)
    glow = K.rad_grad(size, gx, gy, w * 0.52, K.mix(key, (255, 255, 255), 0.40), (0, 0, 0), gamma=0.75)
    im = K.screen(im, glow)
    im = K.screen(im, K.tone(glow, 0.8, 0.45))
    core = K.rad_grad(size, gx, gy + 20 * S, w * 0.16, (255, 255, 255), (0, 0, 0), gamma=1.4)
    im = K.screen(im, K.tone(core, 1.0, 0.55))
    im.alpha_composite(RD.light_rays(size, gx, gy, 11, w * 0.7, 16 * S, K.mix(key, (255, 255, 255), 0.5), seed, alpha=46, spread=90, ang0=180))
    # distant arena wall: two tiers of arches (silhouette)
    wall = K.L(size)
    wd = ImageDraw.Draw(wall)
    for tier, (y0, y1, aw) in enumerate(((hz - 70 * S, hz - 34 * S, 26 * S), (hz - 34 * S, hz + 2 * S, 32 * S))):
        wd.rectangle([0, y0, w, y1], fill=255)
        x = -aw / 2 + (tier * aw / 2)
        while x < w + aw:
            ow = aw * 0.56
            wd.rectangle([x - ow / 2, y0 + (y1 - y0) * 0.38, x + ow / 2, y1 - 2 * S], fill=0)
            wd.ellipse([x - ow / 2, y0 + (y1 - y0) * 0.38 - ow / 2, x + ow / 2, y0 + (y1 - y0) * 0.38 + ow / 2], fill=0)
            x += aw
    wd.rectangle([0, hz - 76 * S, w, hz - 70 * S], fill=255)
    im.alpha_composite(K.solid(wall, K.mix((30, 14, 24), key, 0.22), 0.85))
    # crowd specks in the arches (more in phase 2/3)
    dens = {1: 70, 2: 160, 3: 200}[phase]
    sp = K.particles(size, dens, seed + 5, 0.8 * S, 1.8 * S, K.mix(TRAV, key, 0.3), (90, 200), area=(0, hz - 64 * S, w, hz))
    im.alpha_composite(K.masked(sp, K.grow(wall, 2)))
    if phase >= 3:   # fire along the far wall
        fire = K.rgba(size)
        fd = ImageDraw.Draw(fire)
        r = K.rng(seed + 9)
        for _ in range(14):
            x = r.uniform(0, w)
            fd.ellipse([x - 22 * S, hz - 90 * S, x + 22 * S, hz - 30 * S], fill=(255, 110, 30, 140))
        im = K.add(im, K.blur(fire, 14 * S), 1.0)
    # sand: gradient + rake lines
    sand = K.L(size)
    ImageDraw.Draw(sand).rectangle([0, hz, w, w], fill=255)
    im.alpha_composite(K.fill_grad(sand, K.mix((120, 86, 62), key, 0.22), (26, 16, 16), hz, w))
    pool = K.rad_grad(size, gx, hz + 20 * S, w * 0.34, K.mix(key, (255, 230, 200), 0.5), (0, 0, 0), gamma=1.1)
    im = K.screen(im, K.masked(K.tone(pool, 1.0, 0.6), sand))
    rk = K.rgba(size)
    rd = ImageDraw.Draw(rk)
    for j in range(14):
        yy = hz + (j ** 1.5) * 1.6 * S + 4 * S
        rd.line([(0, yy), (w, yy)], fill=K.mix(TRAV, key, 0.2) + (26,), width=max(1, int(1.2 * S)))
    im.alpha_composite(rk)
    # haze band at horizon
    hb = K.L(size)
    ImageDraw.Draw(hb).rectangle([0, hz - 10 * S, w, hz + 10 * S], fill=255)
    im.alpha_composite(K.solid(K.blur(hb, 12 * S), K.mix(key, (255, 255, 255), 0.2), 0.18))
    return im, hz


# ================================================================== A ARENA
class ArenaA(Base):
    key = "A"
    title = "A  ARENA"
    blurb = ["The wheel is the arena seen from the emperor's box: stands and crowd round the rim,",
             "sand under the slices, backlit silhouette scenes lit in the slice colour,",
             "an arcade crown over the rim, the pulvinar needle with the emperor's arm."]

    def __init__(self, slots=SLOTS):
        super().__init__()
        self._slots = slots

    # -------- back plate: the stands, seen from above, around the rim
    def back_plate(self, ctx):
        crowd_t = round(ctx.t * 6) / 6.0
        return self.cached(("bp", ctx.S, ctx.phase, crowd_t if ctx.get("idle_crowd", True) else 0), lambda: self._back(ctx, crowd_t))

    def _back(self, ctx, t):
        S = ctx.S
        im = K.rgba(ctx.size)
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        r0, r1 = 300 * S, 488 * S
        band = (rr >= r0) & (rr <= r1)
        tiers = 6
        tt = np.clip((rr - r0) / (r1 - r0), 0, 1)
        tier_i = np.floor(tt * tiers)
        frac = tt * tiers - tier_i
        stone = np.array(K.mix(TRAV, (0, 0, 0), 0.62), np.float32)
        step = np.where(frac < 0.22, 1.25, np.where(frac > 0.85, 0.55, 0.85))[..., None]
        shade = (0.55 + 0.45 * tt)[..., None]
        col = stone * step * shade
        # radial aisles (vomitoria) every 15 deg
        aisle = (np.abs(((ang + 7.5) % 15) - 7.5) < 0.9)
        col = np.where(aisle[..., None], col * 0.35, col)
        a = (band * 255).astype(np.float32)
        a = a * np.clip((r1 - rr) / (14 * S), 0, 1)
        im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        # crowd: lit heads on each tier (density by phase), ripple brightness with t
        dens = {1: 0.38, 2: 0.75, 3: 0.92}[ctx.phase]
        r = K.rng(77)
        crowd = K.rgba(ctx.size)
        cd = ImageDraw.Draw(crowd)
        for ti in range(tiers):
            rad = (r0 + (ti + 0.55) * (r1 - r0) / tiers)
            n = int(2 * math.pi * rad / (5.2 * S))
            for k in range(n):
                if r.random() > dens:
                    continue
                aa = k * 360 / n + r.uniform(-0.4, 0.4)
                if abs(((aa + 7.5) % 15) - 7.5) < 1.6:
                    continue
                wave = 0.5 + 0.5 * math.sin(math.radians(aa * 3) - t * 4.0 + ti)
                c = K.mix((120, 80, 70), (255, 214, 170), 0.35 + 0.5 * wave * r.random())
                x, y = K.pol(cx, cy, rad + r.uniform(-2, 2) * S, aa)
                rh = r.uniform(1.4, 2.2) * S
                cd.ellipse([x - rh, y - rh, x + rh, y + rh], fill=c + (230,))
        im.alpha_composite(crowd)
        # torches on the tier lips; phase 3 fires
        tor = K.rgba(ctx.size)
        td = ImageDraw.Draw(tor)
        ntor = {1: 12, 2: 24, 3: 24}[ctx.phase]
        for k in range(ntor):
            aa = k * 360 / ntor + 7.5
            x, y = K.pol(cx, cy, r1 - 8 * S, aa)
            fl = 1 + 0.25 * math.sin(t * 9 + k)
            td.ellipse([x - 6 * S * fl, y - 6 * S * fl, x + 6 * S * fl, y + 6 * S * fl], fill=(255, 170, 70, 255))
        im = K.add(im, K.blur(tor, 7 * S), 1.3)
        im.alpha_composite(K.blur(tor, 1.2 * S))
        if ctx.phase >= 3:
            fire = K.rgba(ctx.size)
            fd = ImageDraw.Draw(fire)
            rf = K.rng(99)
            for k in range(16):
                aa = rf.uniform(0, 360)
                x, y = K.pol(cx, cy, rf.uniform(r0 + 60 * S, r1), aa)
                rad = rf.uniform(14, 30) * S
                fd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 96, 24, 170))
            im = K.add(im, K.blur(fire, 16 * S), 1.0)
        # dark vignette outward + inner shadow at the bezel
        vg = K.ring_mask(ctx.size, cx, cy, r0, r1 + 4 * S)
        sh = K.rgba(ctx.size)
        sh.alpha_composite(K.solid(K.ring_mask(ctx.size, cx, cy, 380 * S, 420 * S), (0, 0, 0), 0.0))
        return im

    # -------- under ring: the arena sand floor (turns with the wheel)
    def art_ring_under(self, ctx):
        return self.cached(("under", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2)), lambda: self._under(ctx))

    def _under(self, ctx):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        n = K.noise(ctx.size, int(40 * S), 5, 4)
        sand = np.array((150, 112, 78), np.float32) * (0.55 + 0.5 * n[..., None])
        # raked circles + the hypogeum grid (dark slots)
        rake = 0.92 + 0.08 * np.sin(rr / (5 * S))
        sand *= rake[..., None]
        grid = ((np.abs(((rr / S) % 46) - 23) < 2.2) & (rr > 140 * S)) | (np.abs(((ang + 15) % 30) - 15) < 0.5)
        sand = np.where(grid[..., None], sand * 0.35, sand)
        a = ((rr <= 356 * S) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(sand, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        if ctx.phase >= 2:   # blood-dark stains and drag marks
            st = K.particles(ctx.size, 18, 41, 10 * S, 26 * S, (70, 14, 18), (60, 120))
            im.alpha_composite(K.masked(K.blur(st, 6 * S), im.split()[3]))
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(30, 14, 10), glow=(255, 120, 60)))
        return im

    # -------- slice scenes
    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 12) / 12.0
        aq = round(act, 2)
        return self.cached(("sc", ctx.S, slot["fig"], tq if not ctx.get("still") else 0, aq, ctx.phase, i),
                           lambda: self._scene(slot, ctx, tq if not ctx.get("still") else 0.0, aq, i))

    def _scene(self, slot, ctx, t, act, i):
        S = ctx.S
        key = K.TYPE_COL[slot["type"]]
        w = W.scene_box(ctx)
        a = W.slot_angle(i, ctx.rot)
        off = 44 * S
        ox = -math.sin(math.radians(a)) * off
        oy = math.cos(math.radians(a)) * off
        bg, hz = arena_bg(ctx, key, ctx.phase, 11 + i, fx=ox, fy=oy)
        fw = int(FIG_W * S)
        masks = FIGS[slot["fig"]](fw * 2, t, act)            # 2x supersample
        bright = slot["fig"] in ("testudo", "secutor")
        fig = RD.silhouette(masks, (fw * 2, int(fw * 2 * 0.75)), key, VERD, body=(46, 16, 30) if bright else (18, 10, 16),
                            haze=K.mix(PORPH, key, 0.3), gilt=GILT, s=2 * S * 1.2, eye_col=None,
                            detail_mode="bright" if bright else "lit")
        fig = fig.resize((fw, int(fw * 0.75)), Image.LANCZOS)
        # place: ground line of the figure (unit y 262/300) on the sand, pushed away from the plaque side
        gx = w / 2 - fw / 2 + ox
        gy = hz + 26 * S - fig.height * (262 / 300)
        # contact shadow
        sh = K.L((w, w))
        ImageDraw.Draw(sh).ellipse([w / 2 - fw * 0.36 + ox, hz + 18 * S, w / 2 + fw * 0.36 + ox, hz + 34 * S], fill=200)
        bg.alpha_composite(K.solid(K.blur(sh, 6 * S), (0, 0, 0), 0.7))
        bg.alpha_composite(fig, (int(gx), int(gy)))
        # dust / embers in the type colour
        emb = K.particles((w, w), 26, 300 + i, 0.6 * S, 1.8 * S, K.mix(key, (255, 255, 255), 0.4), (60, 200),
                          area=(0, hz - 120 * S, w, hz + 40 * S))
        bg = K.add(bg, emb, 1.0)
        if act > 0:
            bg = self._act_fx(bg, slot, act, ctx, w, hz, key)
        vg = K.vignette((w, w), w / 2, w / 2, w * 0.66, 0.35)
        bg.alpha_composite(K.solid(vg, (0, 0, 0)))
        return bg

    def _act_fx(self, bg, slot, act, ctx, w, hz, key):
        S = ctx.S
        fx = K.rgba((w, w))
        d = ImageDraw.Draw(fx)
        if slot["fig"] == "chariot":      # dust plume + speed streaks
            r = K.rng(5)
            for j in range(18):
                y = hz - r.uniform(20, 110) * S
                x0 = w * (0.1 + 0.3 * r.random())
                d.line([(x0, y), (x0 + (60 + 80 * act) * S, y)], fill=K.mix(key, (255, 255, 255), 0.5) + (int(140 * act),), width=max(1, int(2 * S)))
            dust = K.particles((w, w), 40, 8, 6 * S, 16 * S, (200, 160, 120), (40, 110), area=(0, hz - 10 * S, w * 0.5, hz + 30 * S))
            fx.alpha_composite(K.blur(dust, 5 * S))
        elif slot["fig"] == "lion":      # three claw slashes
            for j in range(3):
                x = w * (0.55 + 0.08 * j)
                d.line([(x, hz - 120 * S), (x + 50 * S, hz - 20 * S)], fill=K.mix(key, (255, 255, 255), 0.6) + (int(230 * act),), width=max(1, int(5 * S)))
        elif slot["fig"] in ("testudo", "secutor"):
            ring = K.L((w, w))
            rr = (60 + 80 * act) * S
            ImageDraw.Draw(ring).ellipse([w / 2 - rr, hz - 60 * S - rr, w / 2 + rr, hz - 60 * S + rr], outline=255, width=max(1, int(6 * S)))
            fx.alpha_composite(K.solid(K.blur(ring, 2 * S), key, 1 - act * 0.6))
        elif slot["fig"] == "crowd":
            pass
        return K.add(bg, fx, 1.0)

    # -------- over ring: the arcade crown (static) with a gap for the needle rig
    def art_ring_over(self, ctx):
        return self.cached(("over", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2), round(ctx.t * 4) / 4 if ctx.phase >= 2 else 0),
                           lambda: self._over(ctx))

    def _arcade_strip(self, ctx, sw, sh, n_arch, seed):
        """Flat elevation of the colosseum facade (row 0 = outer edge): cornice, attic with windows, arcade of
        round-headed arches framed by half-columns, crowd / fire glowing inside by phase."""
        S = ctx.S
        strip = K.rgba((sw, sh))
        full = K.L((sw, sh), 255)
        strip.alpha_composite(K.fill_grad(full, (176, 156, 124), (96, 76, 60), 0, sh))
        n = K.noise((sw, sh), max(3, int(10 * S)), seed, 3)
        stone_n = Image.fromarray((n * 255).astype(np.uint8))
        strip = K.tone_map(strip, np.ones((sh, sw), np.float32), 0.85 + 0.3 * n)
        sd = ImageDraw.Draw(strip)
        aw = sw / n_arch
        holes = K.L((sw, sh))
        hd = ImageDraw.Draw(holes)
        wins = K.L((sw, sh))
        wd = ImageDraw.Draw(wins)
        for k in range(n_arch):
            x = (k + 0.5) * aw
            ow = aw * 0.56
            top = sh * 0.36 + ow / 2
            hd.rectangle([x - ow / 2, top, x + ow / 2, sh * 0.95], fill=255)
            hd.ellipse([x - ow / 2, top - ow / 2, x + ow / 2, top + ow / 2], fill=255)
        # mouldings
        for y0, y1, c in ((0, 0.07, (96, 74, 58)), (0.20, 0.24, (236, 220, 188)), (0.24, 0.27, (110, 86, 66)), (0.95, 1.0, (80, 60, 48))):
            sd.rectangle([0, sh * y0, sw, sh * y1], fill=c + (255,))
        # half-columns between arches with a lit left edge
        for k in range(n_arch + 1):
            x = k * aw
            sd.rectangle([x - aw * 0.09, sh * 0.27, x + aw * 0.09, sh * 0.95], fill=(170, 150, 118, 255))
            sd.line([(x - aw * 0.09, sh * 0.27), (x - aw * 0.09, sh * 0.95)], fill=(240, 226, 196, 255), width=max(1, int(1.6 * S)))
            sd.line([(x + aw * 0.09, sh * 0.27), (x + aw * 0.09, sh * 0.95)], fill=(80, 62, 50, 255), width=max(1, int(1.6 * S)))
        # neon cornice (verdigris)
        sd.line([(0, sh * 0.075), (sw, sh * 0.075)], fill=VERD + (255,), width=max(1, int(2.6 * S)))
        # inside the arches: dark depth, the crowd lit warm, fire from phase 2
        ph = ctx.phase
        inside = K.fill_grad(holes, (54, 22, 26) if ph == 1 else (110, 34, 20), (10, 4, 8), sh * 0.4, sh)
        strip.paste(inside, (0, 0), holes)
        r = K.rng(seed + 1)
        crowd = K.rgba((sw, sh))
        cd = ImageDraw.Draw(crowd)
        dens = {1: 0.45, 2: 0.8, 3: 0.95}[ph]
        for k in range(int(sw / (4.2 * S))):
            if r.random() > dens:
                continue
            x = r.uniform(0, sw)
            y = sh * r.uniform(0.62, 0.9)
            bob = 1.5 * S * math.sin(ctx.t * 5 + x * 0.05)
            hr = r.uniform(1.6, 2.4) * S
            c = K.mix((150, 90, 70), (255, 214, 160), r.random() * 0.8)
            cd.ellipse([x - hr, y - hr + bob, x + hr, y + hr + bob], fill=c + (230,))
        strip.alpha_composite(K.masked(crowd, holes))
        if ph >= 2:
            glow = K.rgba((sw, sh))
            gd = ImageDraw.Draw(glow)
            for k in range(n_arch):
                if r.random() < (0.4 if ph == 2 else 0.9):
                    x = (k + 0.5) * aw
                    fl = 0.8 + 0.2 * math.sin(ctx.t * 8 + k)
                    gd.ellipse([x - aw * 0.26, sh * 0.62 - aw * 0.3 * fl, x + aw * 0.26, sh * 1.0], fill=(255, 120, 40, 220))
            strip = K.add(strip, K.masked(K.blur(glow, 4 * S), holes), 1.0)
        # neon: every arch opening is outlined in verdigris tube (the neon colosseum)
        neon = ImageChops.subtract(K.grow(holes, max(2, int(2.6 * S))), K.grow(holes, max(1, int(0.8 * S))))
        strip.alpha_composite(K.solid(neon, K.mix(VERD, (255, 255, 255), 0.45)))
        strip = K.add(strip, K.solid(K.blur(neon, 4 * S), VERD), 1.3)
        return strip

    def _over(self, ctx):
        S = ctx.S
        r0, r1 = 426, 508
        im = K.rgba(ctx.size)
        for side, (a0, span) in enumerate(((27, 101), (232, 101))):
            arc_len = 2 * math.pi * r1 * span / 360
            sw = int(arc_len * S)
            sh = int((r1 - r0) * S)
            strip = self._arcade_strip(ctx, sw, sh, 11, 40 + side)
            im.alpha_composite(K.polar_wrap(strip, ctx.size, ctx.cx, ctx.cy, r0 * S, r1 * S, ang0=a0, span=span))
        # directional light by angle (sun from the top left), darker toward the bottom
        rr, ang = K.polar_field(ctx.size, ctx.cx, ctx.cy)
        lightk = 0.78 + 0.28 * np.cos(np.radians(ang - 315))
        im = K.tone_map(im, np.ones_like(lightk), lightk.astype(np.float32))
        # cast shadow onto the bezel/threat ring
        sh_ = K.solid(K.blur(im.split()[3], 8 * S), (0, 0, 0), 0.55)
        out = K.rgba(ctx.size)
        out.alpha_composite(sh_)
        out.alpha_composite(im)
        # end caps beside the gap: two columns with verdigris braziers
        d = ImageDraw.Draw(out)
        for a_, braz in ((-27, True), (27, True), (128, False), (232, False)):
            p0 = K.pol(ctx.cx, ctx.cy, (r0 - 4) * S, a_)
            p1 = K.pol(ctx.cx, ctx.cy, (r1 + (18 if braz else 4)) * S, a_)
            d.line([p0, p1], fill=(236, 220, 186, 255), width=max(1, int(14 * S)))
            d.line([p0, p1], fill=(150, 128, 98, 255), width=max(1, int(6 * S)))
            if braz:
                x, y = p1
                fl = 1 + 0.15 * math.sin(ctx.t * 7 + a_)
                d.ellipse([x - 9 * S * fl, y - 9 * S * fl, x + 9 * S * fl, y + 9 * S * fl], fill=VERD + (255,))
                out = K.add(out, K.solid(K.blur(K.ring_mask(ctx.size, x, y, 0, 10 * S), 10 * S), VERD), 1.2)
                d = ImageDraw.Draw(out)
        if ctx.get("dmg", 0) > 0.3:
            cr = W.crack_layer(ctx, ctx.get("dmg"), r0, r1, 71, col=(30, 18, 14), glow=HOT)
            out.alpha_composite(K.masked(cr, out.split()[3]))
        return out

    # -------- hub: the emperor's marble bust
    def hub(self, ctx):
        look = math.sin(ctx.t * 0.9) if not ctx.get("still") else 0.0
        if ctx.get("look") is not None:
            look = ctx.get("look")
        lq = round(look * 4) / 4
        return self.cached(("hub", ctx.S, ctx.phase, lq, round(ctx.t * 3) / 3 if not ctx.get("still") else 0, ctx.get("wrath", 0)),
                           lambda: self._hub(ctx, lq))

    def _hub(self, ctx, look):
        S = ctx.S
        im = K.rgba(ctx.size)
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        disc = K.ring_mask(ctx.size, cx, cy, 0, R0)
        bgc = K.rad_grad(ctx.size, cx, cy - 20 * S, R0, (90, 30, 54), (24, 8, 16))
        im.alpha_composite(K.masked(bgc, disc))
        # chevron sweep (enemy hub rule) in verdigris, slow
        sw = K.rgba(ctx.size)
        sd = ImageDraw.Draw(sw)
        a0 = (ctx.t * 30) % 360
        sd.pieslice([cx - R0, cy - R0, cx + R0, cy + R0], a0 - 90, a0 - 60, fill=VERD + (34,))
        im.alpha_composite(K.masked(sw, disc))
        px = int(R0 * 2 * 1.02)
        wrath = ctx.get("wrath", 0.0)
        masks = F.emperor(px * 2, ctx.t if not ctx.get("still") else 0, look, wrath=wrath)
        bust = RD.relief(masks["main"], (px * 2, px * 2), stone=(222, 214, 200), shadow=(66, 52, 60), hi=(255, 252, 244),
                         s=2 * S, depth=7, under=VERD, under_k=0.5)
        det = K.solid(masks["detail"], (130, 116, 110), 0.55)
        bust.alpha_composite(K.masked(det, masks["main"]))
        gl = RD.relief(masks["glint"], (px * 2, px * 2), stone=GILT, shadow=(90, 60, 24), hi=(255, 236, 170), s=2 * S, depth=3)
        bust.alpha_composite(gl)
        eye_c = VERD if ctx.phase < 3 else (255, 80, 60)
        bust.alpha_composite(K.solid(masks["eye"], eye_c))
        bust = K.add(bust, K.solid(K.blur(masks["eye"], 10 * S), eye_c), 1.4)
        bust = bust.resize((px, px), Image.LANCZOS)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(bust, (int(cx - px / 2 + 6 * S), int(cy - px / 2 + 8 * S)))
        im.alpha_composite(K.masked(lay, disc))
        # name plate under the bust
        f = K.f_ui(int(12 * S), b"Bold Condensed")
        t1 = K.text_img(self.hub_name, f, fill=(250, 244, 230), stroke=max(1, int(1.5 * S)))
        pd = ImageDraw.Draw(im)
        pw, ph = t1.width + 12 * S, t1.height + 4 * S
        pd.rounded_rectangle([cx - pw / 2, cy + 72 * S - ph / 2, cx + pw / 2, cy + 72 * S + ph / 2], radius=4 * S, fill=(14, 8, 12, 220), outline=VERD + (255,))
        K.paste_c(im, t1, cx, cy + 72 * S)
        # rim: gilt ring + verdigris hairline
        d = ImageDraw.Draw(im)
        for rr_, col, wd in ((W.R["hub"] + 8, (60, 40, 30), 16), (W.R["hub"] + 4, GILT, 5), (W.R["hub"] + 13, VERD, 2)):
            d.ellipse([cx - rr_ * S, cy - rr_ * S, cx + rr_ * S, cy + rr_ * S], outline=col + (255,), width=max(1, int(wd * S)))
        return im

    # -------- needle rig: the pulvinar + the cream blade
    def needle(self, ctx, slots):
        g = ctx.get("gesture", 0.0)
        return self.cached(("ndl", ctx.S, round(g, 2), ctx.phase, round(ctx.get("latch", 0), 2), ctx.get("tier"),
                            round(ctx.t * 4) / 4 if not ctx.get("still") else 0),
                           lambda: self._needle(ctx, slots, g))

    def _needle(self, ctx, slots, g):
        S = ctx.S
        im = K.rgba(ctx.size)
        cx, cy = ctx.cx, ctx.cy
        # the locked cream notched blade with the value window
        blade(im, ctx, slots, crown=True, col=(246, 238, 220), edge=VERD, latch=ctx.get("latch", 0.0), tier=ctx.get("tier"), root_r=462)
        # the pulvinar: 400x300 unit box, ledge at y 210 -> sits on the blade root at r ~ 430
        bw = int(330 * S)
        m = F.pulvinar(bw * 2, gesture=g, t=ctx.t, fire=1.0 if ctx.phase >= 3 else 0.0, arm=0.0)
        size2 = (bw * 2, int(bw * 2 * 0.75))
        box = K.rgba(size2)
        # interior: deep purple with a warm lamp
        inner = RD.silhouette({"main": m["back"]}, size2, (255, 170, 90), VERD, body=(34, 12, 30), s=2 * S)
        box.alpha_composite(inner)
        lamp = K.solid(K.blur(m["back"], 30 * S), (255, 150, 60), 0.35)
        box = K.add(box, lamp, 1.0)
        fig = RD.silhouette({"main": m["detail"]}, size2, (255, 190, 120), VERD, body=(12, 6, 10), s=2 * S)
        box.alpha_composite(K.masked(fig, m["back"]))
        st = RD.relief(m["main"], size2, stone=(226, 210, 176), shadow=(70, 54, 46), hi=(255, 248, 228), s=2 * S, depth=4, under=VERD, under_k=0.6)
        box.alpha_composite(st)
        dr = RD.relief(m["drape"], size2, stone=(120, 24, 78), shadow=(40, 6, 26), hi=(200, 70, 140), s=2 * S, depth=6)
        box.alpha_composite(dr)
        gl = K.solid(m["glint"], GILT)
        box.alpha_composite(gl)
        # inscription on the architrave
        k2 = bw * 2 / 400
        band = K.L(size2)
        ImageDraw.Draw(band).rounded_rectangle([90 * k2, 74 * k2, 310 * k2, 102 * k2], radius=3 * k2, fill=255)
        box.alpha_composite(K.solid(band, (36, 12, 26)))
        nm = K.text_img("THE ROSTRUM", K.f_anton(int(26 * k2)), fill=(250, 226, 160), stroke=max(1, int(1.2 * k2)), edge=(30, 10, 20))
        K.paste_c(box, nm, 200 * k2, 88 * k2)
        box = box.resize((bw, int(bw * 0.75)), Image.LANCZOS)
        box = K.drop_shadow(box, 0, int(6 * S), 8 * S, 0.7)
        bx = cx - bw / 2
        by = cy - (W.R["threat_out"] + 44) * S - box.height * (236 / 300)
        im.alpha_composite(box, (int(bx), int(by)))
        # the emperor's arm: the VERDICT emoji hand (same drawing as the boss emblem), rooted on the ledge,
        # swinging about the sleeve root: down = thumb down (hit), up = thumb up (whiff / blocked), sideways = idle
        k_ = bw / 400
        rx, ry = bx + 312 * k_, by + 150 * k_
        hp = int(124 * S)
        hand = EH.hand_rgba(hp, g, pivot_centre=True, pivot=(200, 10), swing=-1.0)
        hand = K.drop_shadow(hand, int(4 * S), int(6 * S), 5 * S, 0.55)
        im.alpha_composite(hand, (int(rx - hand.width / 2), int(ry - hand.height / 2)))
        # verdigris neon trim on the pediment
        im = K.add(im, K.solid(K.blur(K.shifted(K.L(ctx.size), 0, 0), 1), VERD), 0)
        # sub-banner: boss phase line under the box ledge (the D4 nameplate info)
        t2 = K.text_img(SUB % ctx.phase, K.f_ui(int(13 * S), b"Bold Condensed"), fill=VERD, stroke=max(1, int(1.4 * S)))
        K.paste_c(im, t2, cx, by - 10 * S)
        return im


def blade(im, ctx, slots, crown=False, col=(246, 238, 220), edge=(255, 255, 255), latch=0.0, tier=None, tip_r=338, root_r=432, angle=0.0, value=True):
    """The locked D4 pointer: cream notched blade rooted in the bezel, tip biting the slice's outer bezel, a dark value
    window with the live value. latch 0..1 = PERFECT jaws clamp."""
    S = ctx.S
    cx, cy = ctx.cx, ctx.cy
    d = ImageDraw.Draw(im)
    hw = 22
    tip = ctx.P(tip_r, angle)
    pts = [ctx.P(root_r, angle - math.degrees(hw / root_r)), ctx.P(root_r, angle + math.degrees(hw / root_r)),
           ctx.P(372, angle + math.degrees(16 / 372)), tip, ctx.P(372, angle - math.degrees(16 / 372))]
    sh = K.L(ctx.size)
    ImageDraw.Draw(sh).polygon([(x + 4 * S, y + 6 * S) for x, y in pts], fill=200)
    im.alpha_composite(K.solid(K.blur(sh, 4 * S), (0, 0, 0), 0.7))
    d.polygon(pts, fill=col + (255,), outline=(30, 24, 20, 255))
    # notch
    n0 = ctx.P(392, angle)
    d.polygon([ctx.P(398, angle - 2.0), ctx.P(398, angle + 2.0), n0], fill=(60, 50, 40, 255))
    # value window
    sl = slots[ctx.get("landed") if ctx.get("landed") is not None else (ctx.get("forecast") or 0)]
    wx, wy = ctx.P(410, angle)
    ww, wh = 34 * S, 24 * S
    d.rounded_rectangle([wx - ww / 2, wy - wh / 2, wx + ww / 2, wy + wh / 2], radius=4 * S, fill=(12, 10, 18, 255),
                        outline=K.TYPE_COL[sl["type"]] + (255,), width=max(1, int(2 * S)))
    if value:
        txt = "1/0" if sl["type"] == "NULL" else str(sl.get("value", ""))
        ti = K.text_img(txt, K.f_num(int(22 * S)), fill=(255, 255, 255))
        K.paste_c(im, ti, wx, wy)
    if crown:   # small crown on the root (boss blade)
        for k in (-1, 0, 1):
            p = ctx.P(root_r + 4 + (8 if k == 0 else 4), angle + k * 3.0)
            d.polygon([(p[0] - 5 * S, p[1] + 4 * S), (p[0], p[1] - 7 * S), (p[0] + 5 * S, p[1] + 4 * S)], fill=edge + (255,))
    if latch > 0:   # PERFECT: two jaws clamp the tip
        for sgn in (-1, 1):
            off = (1 - latch) * 6 + 1.2
            j0 = ctx.P(356, angle + sgn * off)
            j1 = ctx.P(340, angle + sgn * (off - 0.8))
            j2 = ctx.P(352, angle + sgn * (off + 2.2))
            d.polygon([j0, j1, j2], fill=K.PERFECT_GOLD + (255,), outline=(60, 40, 0, 255))
    if tier == "GOOD":
        x, y = tip
        d.ellipse([x - 10 * S, y - 10 * S, x + 10 * S, y + 10 * S], outline=(255, 255, 255, 230), width=max(1, int(2 * S)))
    return tip
DIRS = {"A": ArenaA}
