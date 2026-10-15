"""Boss Wheel v2 round 3: Tethys Deep, THE TANK.

The designer's brief, built as rules-true as possible:
- The wheel is a fixed ring aquarium round a central water tank. NOTHING SPINS: the tank, the zones, the arms are fixed.
- 8 slots (8 x 45 deg; 40 ticks of 9 deg, 5 per slot - a per-boss tick count, flagged). Each slot is a PREDATOR (or a
  hazard). The predators ARE the slices: the "spin" is the predators migrating round the ring together (same order,
  same spacing), so `slice under pointer = (rotation + pointer_tick) mod ticks` is unchanged; only the art moves.
  Their plaques ride with them (the value belongs to the predator, not to the water).
- The 8 tank ZONES (kelp, reef, wreck site, sand flats, vent, trench, coral, open blue) are fixed scenery under the
  predators. They carry no rules.
- The octopus climbs out of the central tank. Every arm that emerges is a POINTER, radiating outward, its tip lit in the
  colour of the predator it grips. Arms emerge with HP: 2 (100-75 %), 4 (75-50 %), 6 (50-25 %), 8 (<25 %).
  Arms 5-8 are 'tired' (paler, thinner) and resolve at x0.5 (balance proposal).
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
import render2d as RD
import wheel_v2 as W
from shapes import Pen

NS = 8
SD = 360.0 / NS
TICKS = 40
ABYSS, PHOTO, RED = (47, 107, 255), (124, 242, 228), (200, 38, 78)
SLOTS = [
    dict(type="SHIM", value=8, fish="shark", label="SHARK"),
    dict(type="OVERFLOW", value=14, fish="swordfish", label="SWORDFISH"),
    dict(type="INFECT", value=2, fish="jelly", label="JELLYFISH SWARM"),
    dict(type="SANDBOX", value=6, fish="wreck", label="THE WRECK"),
    dict(type="SHIM", value=6, fish="moray", label="MORAY EEL"),
    dict(type="OVERFLOW", value=12, fish="mine", label="NAVAL MINE"),
    dict(type="SHIM", value=5, fish="eel", label="ELECTRIC EEL"),
    dict(type="NULL", value=None, fish="sub", label="SUBMARINE"),
]
ZONES = ["OPEN BLUE", "KELP FOREST", "REEF", "WRECK SITE", "SAND FLATS", "THE VENT", "TRENCH", "CORAL"]
ZONE_COL = [(18, 44, 86), (16, 54, 40), (40, 52, 70), (40, 34, 30), (70, 64, 48), (50, 22, 24), (8, 14, 34), (64, 30, 54)]
# arm order of emergence (pointer angles, deg) and the HP curve
ARM_ANGLES = [0, 180, 90, 270, 45, 225, 135, 315]
ARM_CURVE = [(0.75, 2), (0.50, 4), (0.25, 6), (0.0, 8)]
R_TANK = 112
R_IN, R_OUT, R_BAND = 128, 352, 334


def arms_for_hp(hp):
    for th, n in ARM_CURVE:
        if hp > th:
            return n
    return 8


def P(ctx, r, a):
    return ctx.P(r, a)


def wedge(ctx, i, rot, r0=R_IN, r1=R_OUT, inset=0.0, gap=2.0):
    a = SD * i + rot
    m = K.L(ctx.size)
    n = 40
    S = ctx.S
    g0, g1 = math.degrees((gap + inset) / r1), math.degrees((gap + inset) / max(1, r0))
    pts = [ctx.P(r1 - inset, a - SD / 2 + g0 + (SD - 2 * g0) * k / n) for k in range(n + 1)]
    pts += [ctx.P(r0 + inset, a + SD / 2 - g1 - (SD - 2 * g1) * k / n) for k in range(n + 1)]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


# ================================================================== predators, top-down, facing +x (unit 300 x 120)
def bend(pts, amp, ph, head_x=270, tail_x=10):
    out = []
    for x, y in pts:
        u = max(0.0, min(1.0, (head_x - x) / (head_x - tail_x)))
        out.append((x, y + amp * math.sin(ph - u * 3.0) * u ** 1.6))
    return out


def fish_masks(kind, px, t, act=0.0, swim=0.0):
    """Return dict(main, detail, glow) L masks for a predator. swim = 0..1 swimming intensity (migration)."""
    k = px / 300
    size = (px, int(120 * k))
    pens = {n: Pen(size, k) for n in ("main", "detail", "glow")}
    p, dt, gl = pens["main"], pens["detail"], pens["glow"]
    ph = t * (6 + 8 * swim)
    amp = 5 + 9 * swim
    if kind == "shark":
        body = [(276, 60), (258, 46), (210, 37), (140, 39), (90, 47), (50, 54), (26, 58), (26, 62), (50, 66), (90, 73), (140, 81), (210, 83), (258, 74)]
        p.blob(bend(body, amp, ph), n=8)
        for sg in (-1, 1):
            p.poly(bend([(196, 60 + sg * 18), (150, 60 + sg * 58), (176, 60 + sg * 20)], amp, ph))           # pectorals
            p.poly(bend([(96, 60 + sg * 10), (80, 60 + sg * 26), (88, 60 + sg * 8)], amp, ph))
        p.poly(bend([(30, 60), (2, 60 - 42), (14, 60), (2, 60 + 34)], amp * 1.3, ph))                           # tail
        dt.limb(bend([(220, 60), (120, 60)], amp, ph), 7, 3)                                                     # dorsal ridge
        for sg in (-1, 1):
            dt.ell(256, 60 + sg * 9, 3.5, 3.5)
            for j in range(4):
                dt.limb([(232 - j * 6, 60 + sg * 18), (228 - j * 6, 60 + sg * 22)], 1.6, 1.2)
        if act > 0.1:     # jaws open: a pale mouth at the snout
            gl.ell(266, 60, 8 * act, 10 * act)
    elif kind == "swordfish":
        body = [(250, 60), (230, 50), (170, 44), (100, 48), (56, 55), (40, 60), (56, 65), (100, 72), (170, 76), (230, 70)]
        p.blob(bend(body, amp, ph), n=8)
        p.limb([(244, 60), (300, 60)], 6, 2)                                                                      # the bill
        for sg in (-1, 1):
            p.poly(bend([(190, 60 + sg * 14), (150, 60 + sg * 50), (176, 60 + sg * 16)], amp, ph))
            p.poly(bend([(44, 60), (4, 60 + sg * 44), (24, 60)], amp * 1.3, ph))
        dt.limb(bend([(210, 60), (110, 60)], amp, ph), 10, 4)                                                    # the sail, folded
        gl.limb([(250, 60), (300 + 10 * act, 60)], 2.5, 1)
    elif kind == "moray":
        pts = [(280 - u * 9, 60 + (12 + 10 * swim) * math.sin(ph * 0.6 - u * 0.55)) for u in range(31)]
        p.limb(pts, 30, 6, n=4)
        jaw = 6 + 14 * act
        p.poly([(270, 52), (296, 60 - jaw), (286, 60), (296, 60 + jaw), (270, 68)])
        for j in range(14):
            x, y = pts[j * 2 + 1]
            dt.ell(x, y + (5 if j % 2 else -5), 3, 3)
        dt.ell(272, 54, 3, 3)
        dt.ell(272, 66, 3, 3)
    elif kind == "jelly":
        for j, (x, y, r) in enumerate(((230, 40, 26), (190, 84, 22), (140, 46, 30), (92, 82, 20), (60, 38, 18))):
            pul = 1 + 0.12 * math.sin(t * 3 + j)
            p.ell(x, y, r * pul, r * pul)
            for q in range(6):
                a = q * 60 + 15
                dt.limb([(x, y), (x + r * 0.8 * math.cos(math.radians(a)), y + r * 0.8 * math.sin(math.radians(a)))], 2, 1)
            for q in range(4):
                tx = x - r - 10 - q * 3
                gl.limb([(x - r * 0.6, y - 8 + q * 5), (tx - 20, y - 8 + q * 5 + 6 * math.sin(t * 2 + q)), (tx - 46 - 30 * act, y + q * 4)], 2.2, 0.8)
    elif kind == "mine":
        cx, cy = 150, 60
        spin = t * 20
        p.ell(cx, cy, 40, 40)
        for q in range(8):
            a = math.radians(q * 45 + spin)
            p.limb([(cx + 36 * math.cos(a), cy + 36 * math.sin(a)), (cx + 54 * math.cos(a), cy + 54 * math.sin(a))], 7, 5)
            gl.ell(cx + 56 * math.cos(a), cy + 56 * math.sin(a), 4, 4)
        dt.ell(cx, cy, 14, 14)
        for q in range(5):
            dt.ell(cx - 50 - q * 12, cy + 4 * math.sin(t + q), 5, 3)        # chain
        if act > 0.1:
            gl.ell(cx, cy, 30 + 60 * act, 30 + 60 * act)
            gl.ell(cx, cy, 24 + 56 * act, 24 + 56 * act, fill=0)
    elif kind == "wreck":
        hull = [(286, 60), (256, 40), (180, 30), (60, 32), (20, 44), (14, 60), (20, 76), (60, 88), (180, 90), (256, 80)]
        p.blob(hull, n=6)
        for j in range(8):
            dt.limb([(40 + j * 28, 38), (40 + j * 28, 82)], 1.6, 1.6)                      # deck planks
        dt.ell(170, 60, 12, 12)                                                            # broken mast stump
        dt.limb([(170, 60), (240, 14)], 5, 3)                                              # fallen mast
        p.ell(110, 70, 14, 10, fill=0)                                                     # holes
        p.ell(220, 50, 10, 8, fill=0)
        gl.ell(110, 70, 10, 7)                                                             # the octopus's eye in the hole
    elif kind == "eel":
        pts = [(280 - u * 9, 60 + (14 + 10 * swim) * math.sin(ph * 0.5 - u * 0.45)) for u in range(31)]
        p.limb(pts, 26, 8, n=4)
        dt.ell(272, 54, 3, 3)
        dt.ell(272, 66, 3, 3)
        z = []
        for j in range(30):
            x, y = pts[j]
            z.append((x, y + (6 if j % 2 else -6)))
        gl.line(z, 2.4 + 2 * act)
    elif kind == "sub":
        p.blob([(290, 60), (270, 44), (200, 38), (60, 40), (24, 50), (14, 60), (24, 70), (60, 80), (200, 82), (270, 76)], n=8)
        dt.rrect(150, 50, 200, 70, 8)                                                      # sail
        dt.limb([(160, 60), (190, 60)], 4, 4)
        for sg in (-1, 1):
            p.poly([(40, 60 + sg * 20), (20, 60 + sg * 36), (30, 60 + sg * 18)])
        gl.ell(10, 60, 10, 14)                                                             # prop wash
        gl.poly([(292, 56), (300, 20), (300, 100), (292, 64)])                             # searchlight
    return {n: q.m for n, q in pens.items()}


FISH_COL = {"shark": (96, 118, 140), "swordfish": (70, 96, 150), "moray": (86, 96, 40), "jelly": (180, 120, 230), "mine": (70, 60, 56),
            "wreck": (110, 80, 52), "eel": (60, 66, 40), "sub": (110, 116, 124)}


def fish_sprite(kind, key, px, t, act, swim, S, ghost=False):
    m = fish_masks(kind, px * 2, t, act, swim)
    size2 = m["main"].size
    base = FISH_COL[kind]
    rel = RD.relief(m["main"], size2, stone=base, shadow=K.mul(base, 0.35), hi=K.mix(base, (255, 255, 255), 0.45), s=2 * S, depth=5,
                    under=key, under_k=0.8)
    if kind == "jelly":
        a = np.asarray(rel.split()[3], np.float32) * 0.75
        rel.putalpha(Image.fromarray(a.astype(np.uint8)))
    rel.alpha_composite(K.solid(K.mask_mul(m["detail"], m["main"]) if kind not in ("jelly",) else m["detail"], K.mul(base, 0.45), 0.9))
    # type-colour rim light (the type reads even blurred) + glow bits
    rim = ImageChops.subtract(K.grow(m["main"], 3 * S), m["main"])
    out = K.rgba(size2)
    out.alpha_composite(K.solid(K.blur(rim, 3 * S), key, 0.9))
    out.alpha_composite(rel)
    gc = {"eel": (140, 230, 255), "mine": (255, 120, 60), "sub": (255, 240, 200), "wreck": (255, 200, 80)}.get(kind, K.mix(key, (255, 255, 255), 0.4))
    if m["glow"].getbbox():
        gm = m["glow"]
        out.alpha_composite(K.solid(gm, gc, 0.7 if kind == "sub" else 0.95))
        out = K.add(out, K.solid(K.blur(gm, 6 * S), gc), 0.8)
    if ghost:
        out = K.tone(out, 0.3, 0.5)
    return out.resize((px, int(px * 0.52)), Image.LANCZOS)


# ================================================================== the tank wheel
class TankV3:
    title = "V3  THE TANK"
    name = "THE BLACK SMOKER"
    mat = dict(base=(46, 60, 76), hi=(160, 186, 206), lo=(8, 12, 22), accent=ABYSS, glass=(4, 10, 26))

    def __init__(self):
        self._cache = {}

    def cached(self, key, fn):
        if key not in self._cache:
            if len(self._cache) > 400:
                self._cache.clear()
            self._cache[key] = fn()
        return self._cache[key]

    # ---- fixed: the ring aquarium's zones
    def zones(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        zi = (np.floor(((ang + SD / 2) % 360) / SD)).astype(np.int32) % NS
        col = np.array(ZONE_COL, np.float32)[zi]
        n = K.noise(ctx.size, int(30 * S), 3, 4)
        col = col * (0.7 + 0.6 * n[..., None])
        depth = np.clip((rr / S - R_IN) / (R_OUT - R_IN), 0, 1)
        col = col * (0.75 + 0.35 * depth[..., None])
        a = (((rr <= R_OUT * S) & (rr >= (R_TANK - 4) * S)) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(im)
        r = K.rng(21)
        for zi_ in range(NS):                               # zone props, fixed
            a0 = zi_ * SD
            for j in range(26):
                aa = a0 + r.uniform(-SD / 2 + 3, SD / 2 - 3)
                rad = r.uniform(R_IN + 14, R_OUT - 22)
                x, y = ctx.P(rad, aa)
                q = r.uniform(3, 9) * S
                c = {1: (30, 110, 60), 2: (110, 90, 120), 3: (90, 70, 50), 4: (150, 140, 110), 5: (180, 60, 30), 6: (20, 30, 60), 7: (220, 90, 140)}.get(zi_, (30, 60, 110))
                if zi_ == 1:      # kelp: long fronds
                    d.line([(x, y), (x + r.uniform(-8, 8) * S, y - r.uniform(14, 30) * S)], fill=c + (200,), width=max(1, int(3 * S)))
                else:
                    d.ellipse([x - q, y - q, x + q, y + q], fill=c + (int(r.uniform(90, 200)),))
        im = K.blur(im, 0.6 * S)
        # zone dividers: faint glass seams (fixed)
        for zi_ in range(NS):
            a = zi_ * SD + SD / 2
            d = ImageDraw.Draw(im)
            d.line([ctx.P(R_IN + 4, a), ctx.P(R_OUT - 2, a)], fill=(120, 170, 220, 60), width=max(1, int(2 * S)))
        # caustics (animated scroll)
        cz = K.noise(ctx.size, int(16 * S), 40 + int(t * 3) % 6, 2)
        caus = np.clip((np.abs(np.sin(cz * 18 + t * 1.5)) < 0.12) * 1.0, 0, 1) * (rr <= R_OUT * S) * (rr >= R_TANK * S)
        im = K.add(im, K.solid(K.blur(Image.fromarray((caus * 120).astype(np.uint8)), 1.2 * S), (150, 220, 255)), 0.8)
        return im

    def back(self, ctx, phase):
        S = ctx.S
        im = K.rgba(ctx.size)
        aura = K.blur(K.ring_mask(ctx.size, ctx.cx, ctx.cy, 0, 480 * S), 24 * S)
        im.alpha_composite(K.solid(aura, (2, 8, 20), 0.92))
        if phase >= 2:
            lights = K.particles(ctx.size, 30 * phase, 31, 1.4 * S, 3 * S, RED, (120, 255))
            im = K.add(im, K.blur(K.masked(lights, K.ring_mask(ctx.size, ctx.cx, ctx.cy, 410 * S, 500 * S)), 2 * S), 1.3)
        return im

    # ---- the tank wall (fixed bezel): steel + glass, rivets, zone labels, arm sockets
    def wall(self, ctx, n_arms, landed_cols=None):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        ring = K.ring_mask(ctx.size, cx, cy, R_OUT * S, 398 * S)
        im.alpha_composite(RD.relief(ring, ctx.size, stone=(56, 70, 86), shadow=(10, 14, 22), hi=(170, 196, 214), s=S, depth=5))
        glass = K.ring_mask(ctx.size, cx, cy, (R_OUT + 12) * S, (R_OUT + 30) * S)
        im.alpha_composite(K.solid(glass, (10, 30, 56), 0.9))
        d = ImageDraw.Draw(im)
        for k in range(48):
            x, y = ctx.P(R_OUT + 6, k * 7.5 + 3.75)
            d.ellipse([x - 2.4 * S, y - 2.4 * S, x + 2.4 * S, y + 2.4 * S], fill=(150, 170, 190, 255))
            x, y = ctx.P(392, k * 7.5)
            d.ellipse([x - 2.4 * S, y - 2.4 * S, x + 2.4 * S, y + 2.4 * S], fill=(150, 170, 190, 255))
        f = K.f_mono(max(6, int(12 * S)))
        for zi_, nm in enumerate(ZONES):
            a = zi_ * SD + 13
            s_ = "Z%d %s" % (zi_ + 1, nm)
            acc = a
            for ch in s_:
                wdeg = f.getlength(ch) / ((R_OUT + 21) * S) * 57.3
                ci = K.text_img(ch, f, fill=(120, 190, 230))
                ci = ci.rotate(-(acc + wdeg / 2), resample=Image.BICUBIC, expand=True)
                x, y = ctx.P(R_OUT + 21, acc + wdeg / 2)
                im.alpha_composite(ci, (int(x - ci.width / 2), int(y - ci.height / 2)))
                acc += wdeg
        # arm sockets on the wall: lit index tab for every emerged arm, an empty socket for the dormant ones
        for j, a in enumerate(ARM_ANGLES):
            x, y = ctx.P(410, a)
            on = j < n_arms
            tired = j >= 4
            c = (PHOTO if not tired else (150, 170, 190)) if on else (40, 48, 60)
            d.rounded_rectangle([x - 11 * S, y - 9 * S, x + 11 * S, y + 9 * S], radius=3 * S, fill=(6, 10, 20, 255), outline=c + (255,), width=max(1, int(2 * S)))
            ti = K.text_img(str(j + 1), K.f_num(int(15 * S)), fill=c if on else (70, 80, 96))
            K.paste_c(im, ti, x, y)
        return im

    # ---- the moving predator band: rim colours + 40 ticks + predators + plaques
    def predators(self, ctx, slots, rot, t, swim, offsets, act_slots, ghost=None):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        band = K.rgba(ctx.size)
        bd = ImageDraw.Draw(band)
        for i, sl in enumerate(slots):
            a = SD * i + rot + offsets[i]
            bm = wedge(ctx, i, rot + offsets[i], R_BAND, R_OUT, gap=3)
            band.alpha_composite(K.solid(bm, K.TYPE_COL[sl["type"]], 0.95 if sl["type"] != "NULL" else 0.7))
        for k in range(TICKS):
            a = k * 360 / TICKS + rot
            ln = 10 if k % 5 == 0 else 5
            bd.line([ctx.P(R_OUT - ln, a), ctx.P(R_OUT, a)], fill=(255, 255, 255, 170), width=max(1, int(1.6 * S)))
        fishes = K.rgba(ctx.size)
        for i, sl in enumerate(slots):
            a = SD * i + rot + offsets[i]
            kind = sl["fish"]
            key = K.TYPE_COL[sl["type"]]
            act = act_slots.get(i, 0.0)
            px = int({"mine": 150, "jelly": 190, "wreck": 196, "sub": 196, "moray": 200, "eel": 200}.get(kind, 190) * S)
            spr = self.cached(("fish", kind, px, round(t * 12) / 12, round(act, 2), round(swim, 1), ghost == i),
                              lambda: fish_sprite(kind, key, px, t, act, swim, S, ghost=(sl["type"] == "NULL")))
            radial = 214 + (8 * math.sin(t * 1.3 + i) if swim < 0.05 else 26 * swim * math.sin(t * 2 + i * 1.7))
            q = spr.rotate(-(a - 0), resample=Image.BICUBIC, expand=True)       # sprite +x = clockwise tangent at angle a
            x, y = ctx.P(radial, a)
            sh = K.solid(K.shifted(K.blur(q.split()[3], 4 * S), 8 * S, 14 * S), (0, 0, 0), 0.45)
            fishes.alpha_composite(sh, (int(x - q.width / 2), int(y - q.height / 2)))
            fishes.alpha_composite(q, (int(x - q.width / 2), int(y - q.height / 2)))
        return band, fishes

    def plaques(self, ctx, slots, rot, offsets, fade=1.0, half=()):
        lay = K.rgba(ctx.size)
        for i, sl in enumerate(slots):
            a = SD * i + rot + offsets[i]
            s2 = dict(sl)
            pk = ("plq", ctx.S, i, i in half)
            p = self.cached(pk, lambda: W.plaque(ctx, s2))
            x, y = ctx.P(290, a)
            if fade < 1:
                p = p.copy()
                p.putalpha(p.split()[3].point(lambda v: int(v * fade)))
            lay.alpha_composite(p, (int(x - p.width / 2), int(y - p.height / 2)))
        return lay

    # ---- the central tank + the octopus climbing out
    def tank(self, ctx, t, phase, n_arms, look=0.0, blink=0.0):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        water = K.ring_mask(ctx.size, cx, cy, 0, R_TANK * S)
        wcol = K.rad_grad(ctx.size, cx, cy, R_TANK * S, (30, 90, 130), (6, 20, 44))
        im.alpha_composite(K.masked(wcol, water))
        # dormant arms coiled under water (8 - n of them)
        coil = Pen(ctx.size, 1.0)
        for j in range(n_arms, 8):
            a = ARM_ANGLES[j]
            pts = []
            for q in range(18):
                u = q / 17
                rad = (70 - 40 * u) * S
                aa = a + 200 * u
                pts.append(K.pol(cx, cy, rad + 6 * S, aa))
            coil.d.polygon(K.stroke_poly(pts, 22 * S, 5 * S), fill=255)
        im.alpha_composite(K.solid(K.mask_mul(coil.m, water), (60, 30, 50), 0.75))
        # the tank's glass wall (rim)
        rim = K.ring_mask(ctx.size, cx, cy, (R_TANK - 2) * S, (R_TANK + 14) * S)
        im.alpha_composite(RD.relief(rim, ctx.size, stone=(70, 90, 110), shadow=(14, 20, 30), hi=(210, 230, 245), s=S, depth=4))
        gl = K.ring_mask(ctx.size, cx, cy, (R_TANK + 2) * S, (R_TANK + 6) * S, 290, 350)
        im.alpha_composite(K.solid(K.blur(gl, 1.5 * S), (255, 255, 255), 0.6))
        return im

    def head(self, ctx, t, stage, look=0.0, blink=0.0, reveal=1.0):
        """The creature in the tank, revealed by stage (= arms / 2 - 1):
        0: body unseen (a shadow under the water, bubbles); 1: the eyes break the surface; 2: the mantle is out;
        3: THE REVEAL - the cybernetic kraken, the corporation's brain: cranial plates, cable tendons, an LED eye array.
        reveal 0..1 blends a stage in (animation)."""
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        water = K.ring_mask(ctx.size, cx, cy, 0, R_TANK * S)
        skin = (120, 44, 56) if stage < 3 else (150, 36, 52)
        breathe = 3 * math.sin(t * 1.3)
        rise = {0: 0.0, 1: 0.45, 2: 1.0, 3: 1.0}[stage]
        if stage in (1, 2) and reveal < 1:
            rise = {1: 0.45 * reveal, 2: 0.45 + 0.55 * reveal}[stage]
        head = Pen(ctx.size, 1.0)
        hp = [(0, -96 - breathe), (60, -74), (80, -14), (70, 42), (34, 70), (-34, 70), (-70, 42), (-80, -14), (-60, -74)]
        head.d.polygon(K.catmull([(cx + x * S, cy + y * S) for x, y in hp], 10), fill=255)
        hm = head.m
        shadow = K.solid(K.blur(hm, 10 * S), (6, 10, 20), 0.75)
        im.alpha_composite(K.masked(shadow, water))
        r = K.rng(int(t * 6) + 3)
        d = ImageDraw.Draw(im)
        for j in range(10):
            x, y = cx + r.uniform(-70, 70) * S, cy + r.uniform(-70, 70) * S
            q = r.uniform(2, 5) * S
            d.ellipse([x - q, y - q, x + q, y + q], outline=(170, 220, 255, 170), width=max(1, int(1.2 * S)))
        if rise <= 0:
            for sg in (-1, 1):       # two faint eye-glints deep down (a hint)
                ex, ey = cx + sg * 30 * S, cy + 26 * S
                im = K.add(im, K.solid(K.blur(K.ring_mask(ctx.size, ex, ey, 0, 5 * S), 4 * S), (255, 190, 70)), 0.35)
            return im
        cut = K.L(ctx.size)
        top_y = cy - 100 * S
        bot_y = cy + 72 * S
        wl = bot_y - (bot_y - top_y) * min(1.0, 0.25 + 0.75 * rise) if rise < 1 else bot_y + 10 * S
        ImageDraw.Draw(cut).rectangle([0, 0, ctx.C, wl], fill=255)
        # stage 1: only the band of the eyes is above water (the top of the head stays a dark shape below)
        if stage == 1:
            cut = K.L(ctx.size)
            ImageDraw.Draw(cut).ellipse([cx - 64 * S, cy + 6 * S, cx + 64 * S, cy + 50 * S], fill=255)
        above = K.mask_mul(hm, cut) if (rise < 1 or stage == 1) else hm
        rel = RD.relief(above, ctx.size, stone=skin, shadow=K.mul(skin, 0.3), hi=K.mix(skin, (255, 220, 210), 0.45), s=S, depth=22)
        nz = K.noise(ctx.size, int(10 * S), 23, 3)
        rel = K.tone_map(rel, np.ones_like(nz), 0.75 + 0.5 * nz)
        im.alpha_composite(K.solid(K.shifted(K.blur(above, 8 * S), 4 * S, 8 * S), (0, 0, 0), 0.5))
        im.alpha_composite(rel)
        if stage <= 2 and (rise < 1 or stage == 1):   # waterline ripples round what is above the surface
            edge = ImageChops.subtract(K.grow(above, 4 * S), above)
            im.alpha_composite(K.solid(K.blur(edge, 2 * S), (200, 240, 255), 0.6))
        d = ImageDraw.Draw(im)
        ring_c = (70, 110, 170) if stage < 2 else ((70, 170, 255) if stage == 2 else (120, 240, 255))
        if stage >= 2:
            for (x, y, rr) in ((-30, -40, 8), (24, -54, 7), (36, -14, 6), (-44, 2, 6), (4, -66, 5), (0, -20, 7)):
                d.ellipse([cx + (x - rr) * S, cy + (y - rr) * S, cx + (x + rr) * S, cy + (y + rr) * S], outline=ring_c + (230,), width=max(1, int(2 * S)))
        open_ = max(0.05, 1 - blink) * (1.0 + 0.15 * stage)
        icol = (255, 196, 70) if stage < 3 else (255, 60, 50)
        ey0 = cy + 28 * S
        for sg in (-1, 1):
            ex, ey = cx + sg * 34 * S, ey0
            d.ellipse([ex - 16 * S, ey - 12 * S * open_, ex + 16 * S, ey + 12 * S * open_], fill=K.mul(skin, 0.4) + (255,))
            d.ellipse([ex - 13 * S, ey - 9 * S * open_, ex + 13 * S, ey + 9 * S * open_], fill=icol + (255,))
            d.rounded_rectangle([ex - 9 * S + look * 3 * S, ey - 2.4 * S * open_, ex + 9 * S + look * 3 * S, ey + 2.4 * S * open_], radius=2 * S, fill=(6, 4, 8, 255))
            d.polygon([(ex - 17 * S, ey - 14 * S), (ex + 17 * S, ey - 16 * S + sg * 4 * S), (ex + 17 * S, ey - 6 * S), (ex - 17 * S, ey - 4 * S)], fill=skin + (255,))
        for sg in (-1, 1):
            im = K.add(im, K.solid(K.blur(K.ring_mask(ctx.size, cx + sg * 34 * S, ey0, 0, 12 * S), 8 * S), icol), 0.4)
        if stage < 3:
            return im
        # ---------- THE REVEAL: corp hardware
        k = reveal
        hw = Pen(ctx.size, 1.0)
        for (x0, y0, x1, y1) in ((-50, -88, 50, -56), (-66, -50, -12, -20), (12, -50, 66, -20)):
            hw.d.rounded_rectangle([cx + x0 * S, cy + y0 * S, cx + x1 * S, cy + y1 * S], radius=8 * S, fill=255)
        plates = K.mask_mul(hw.m, hm)
        pr = RD.relief(plates, ctx.size, stone=(120, 134, 150), shadow=(30, 36, 46), hi=(230, 240, 250), s=S, depth=4)
        pr.putalpha(pr.split()[3].point(lambda v: int(v * k)))
        im.alpha_composite(pr)
        d = ImageDraw.Draw(im)
        for (x, y) in ((-44, -82), (44, -82), (-44, -62), (44, -62), (-60, -44), (-18, -44), (18, -44), (60, -44), (-60, -26), (60, -26)):
            d.ellipse([cx + (x - 2.5) * S, cy + (y - 2.5) * S, cx + (x + 2.5) * S, cy + (y + 2.5) * S], fill=(210, 220, 230, int(255 * k)))
        d.line([(cx + 30 * S, cy - 84 * S), (cx + 48 * S, cy - 124 * S)], fill=(150, 160, 175, int(255 * k)), width=max(1, int(3 * S)))
        bl = 0.6 + 0.4 * math.sin(t * 6)
        im = K.add(im, K.solid(K.blur(K.ring_mask(ctx.size, cx + 48 * S, cy - 124 * S, 0, 5 * S), 6 * S), (255, 60, 60)), 1.4 * bl * k)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([cx - 62 * S, cy - 6 * S, cx + 62 * S, cy + 10 * S], radius=6 * S, fill=(20, 22, 30, int(255 * k)), outline=(150, 160, 175, int(255 * k)))
        for j in range(7):       # the LED eye array across the brow
            x, y = cx + (-48 + j * 16) * S, cy + 2 * S
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([x - 5 * S, y - 4 * S, x + 5 * S, y + 4 * S], radius=2 * S, fill=(30, 6, 8, int(255 * k)))
            on = 0.5 + 0.5 * math.sin(t * 8 - j * 0.9)
            im = K.add(im, K.solid(K.ring_mask(ctx.size, x, y, 0, 3.4 * S), (255, 50 + int(60 * on), 50)), 1.2 * k)
        tp = K.text_img("TETHYS", K.f_mono(max(6, int(13 * S))), fill=(124, 242, 228))
        tp.putalpha(tp.split()[3].point(lambda v: int(v * k)))
        K.paste_c(im, tp, cx, cy - 72 * S)
        d = ImageDraw.Draw(im)
        for sg in (-1, 1):
            pts = [(cx + sg * 60 * S, cy - 30 * S), (cx + sg * 86 * S, cy + 10 * S), (cx + sg * 80 * S, cy + 60 * S)]
            d.line(K.catmull(pts, 8, False), fill=(124, 242, 228, int(230 * k)), width=max(1, int(3 * S)))
        return im

    def arms(self, ctx, n_arms, t, emerge=None, grab=0.0, landed_cols=None, latch=0.0, phase=1, cyber=0.0, emerge_from=None):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        body = K.L(ctx.size)
        tired_m = K.L(ctx.size)
        suck = K.L(ctx.size)
        bd = ImageDraw.Draw(body)
        td = ImageDraw.Draw(tired_m)
        sd = ImageDraw.Draw(suck)
        tips = []
        for j in range(n_arms):
            a = ARM_ANGLES[j]
            ext = 1.0
            if emerge is not None and j >= (n_arms - 1 if emerge_from is None else emerge_from):
                ext = max(0.02, emerge)
            tired = j >= 4
            r_end = R_TANK - 10 + (344 - (R_TANK - 10)) * ext
            pts = []
            n = 40
            for q in range(n + 1):
                u = q / n
                rr = R_TANK - 10 + (r_end - (R_TANK - 10)) * u
                wave = 4.5 * math.sin(2 * math.pi * (u * 1.1 - t * 0.5) + j * 1.1) * u ** 0.8
                g = grab * 5 * math.sin(math.pi * u) * (1 if j % 2 else -1)
                pts.append(ctx.P(rr, a + wave + g))
            # tip curl: grips (curls sideways) when grab
            ex, ey = pts[-1]
            curl = []
            if ext > 0.98:
                sg = 1 if j % 2 else -1
                for q in range(1, 12):
                    u = q / 11
                    ang = math.radians(a + sg * (90 + 260 * u))
                    rad = (10 + 6 * grab) * (1 - 0.6 * u) * S
                    curl.append((ex + rad * math.sin(ang) * 1.2, ey - rad * math.cos(ang) * 1.2))
            allp = pts + curl
            m = len(allp)
            L_, R_ = [], []
            w0 = (42 if not tired else 30) * S
            for i in range(m):
                x, y = allp[i]
                xa, ya = allp[max(0, i - 1)]
                xb, yb = allp[min(m - 1, i + 1)]
                dx, dy = xb - xa, yb - ya
                ln = math.hypot(dx, dy) or 1
                nx, ny = -dy / ln, dx / ln
                u = i / (m - 1)
                w = (w0 * (1 - u) ** 1.3 + 3 * S) / 2
                L_.append((x + nx * w, y + ny * w))
                R_.append((x - nx * w, y - ny * w))
                if i % 3 == 1 and 0.15 < u < 0.9:
                    sx, sy = x - nx * w * 0.5, y - ny * w * 0.5
                    q_ = max(1.2 * S, w * 0.32)
                    sd.ellipse([sx - q_, sy - q_, sx + q_, sy + q_], fill=255)
            (td if tired else bd).polygon(L_ + R_[::-1], fill=255)
            tips.append((j, pts[-1]))
        skin = {1: (120, 44, 56), 2: (160, 52, 44), 3: (186, 28, 46)}[phase]
        out = K.rgba(ctx.size)
        allm = ImageChops.lighter(body, tired_m)
        out.alpha_composite(K.solid(K.shifted(K.blur(allm, 7 * S), 6 * S, 10 * S), (0, 0, 0), 0.6))
        for m_, c in ((body, skin), (tired_m, K.mix(skin, (200, 190, 200), 0.35))):
            if m_.getbbox() is None:
                continue
            a_ = RD.silhouette({"main": m_}, ctx.size, K.mix(c, (255, 210, 190), 0.5), PHOTO, body=c, s=S * 1.4, glow_k=0.25)
            h = np.asarray(K.blur(K.shrink(m_, 3 * S), 9 * S), np.float32) / 255
            nz = K.noise(ctx.size, int(8 * S), 77, 3)
            a_ = K.tone_map(a_, np.ones_like(h), (0.3 + 1.0 * h ** 0.8) * (0.8 + 0.4 * nz))
            out.alpha_composite(K.solid(K.grow(m_, 2 * S), (30, 8, 14)))
            out.alpha_composite(a_)
        out.alpha_composite(K.solid(K.mask_mul(suck, allm), (236, 200, 196), 0.95))
        if cyber > 0:   # the reveal: a cable tendon runs along every arm + steel bands
            cab = K.L(ctx.size)
            cd = ImageDraw.Draw(cab)
            for j in range(n_arms):
                a = ARM_ANGLES[j]
                cd.line([ctx.P(R_TANK, a + 1.5), ctx.P(330, a + 0.8)], fill=255, width=max(1, int(3 * S)))
                for rr in (170, 230, 290):
                    cd.line([ctx.P(rr, a - 4), ctx.P(rr, a + 4)], fill=200, width=max(1, int(5 * S)))
            cab = K.mask_mul(cab, allm)
            out.alpha_composite(K.solid(cab, (124, 242, 228), 0.9 * cyber))
            out = K.add(out, K.solid(K.blur(cab, 4 * S), (124, 242, 228)), 0.6 * cyber)
        # lit tips: a ring in the colour of the predator gripped; PERFECT latch = gold
        d = ImageDraw.Draw(out)
        for j, (x, y) in tips:
            c = (landed_cols or {}).get(j, (230, 240, 255))
            rr = 9 * S
            tm = K.ring_mask(ctx.size, x, y, rr * 0.55, rr)
            out = K.add(out, K.solid(K.blur(K.ring_mask(ctx.size, x, y, 0, rr), 8 * S), c), 1.2)
            out.alpha_composite(K.solid(tm, K.mix(c, (255, 255, 255), 0.4)))
            if latch > 0:
                d = ImageDraw.Draw(out)
                lr = (16 - 6 * latch) * S
                d.ellipse([x - lr, y - lr, x + lr, y + lr], outline=K.PERFECT_GOLD + (255,), width=max(1, int(3 * S)))
        return out

    def banner(self, ctx, phase, n_arms):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        cx, cy = ctx.cx, ctx.cy - 470 * S
        w, h = 330 * S, 64 * S
        d.polygon([(cx - w / 2 - 14 * S, cy - h / 2), (cx + w / 2 + 14 * S, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)],
                  fill=(4, 10, 24, 245), outline=ABYSS + (255,))
        K.paste_c(im, K.text_img(self.name, K.f_anton(int(33 * S)), fill=(255, 255, 255)), cx, cy - 8 * S)
        K.paste_c(im, K.text_img("TETHYS DEEP  |  BOSS  |  %d ARMS" % n_arms, K.f_ui(int(13 * S), b"Bold Condensed"), fill=PHOTO), cx, cy + 20 * S)
        return im

    def hp_arc(self, ctx, hp):
        S = ctx.S
        im = K.rgba(ctx.size)
        d = ImageDraw.Draw(im)
        a0, a1 = 128, 232
        nseg = 26
        for k in range(nseg):
            aa = a1 - (a1 - a0) * (k + 0.1) / nseg
            ab = a1 - (a1 - a0) * (k + 0.9) / nseg
            on = (k + 0.5) / nseg <= hp
            pts = [ctx.P(452, aa + (ab - aa) * q / 4) for q in range(5)] + [ctx.P(432, ab - (ab - aa) * q / 4) for q in range(5)]
            d.polygon(pts, fill=((123, 224, 123, 255) if on else (40, 44, 48, 220)), outline=(6, 16, 8, 255))
        for th, n in ARM_CURVE[:-1]:
            aa = a1 - (a1 - a0) * th
            x0, y0 = ctx.P(462, aa)
            sz = 8 * S
            d.polygon([(x0, y0 - sz), (x0 + sz, y0), (x0, y0 + sz), (x0 - sz, y0)], fill=PHOTO + (255,), outline=K.INK + (255,))
        return im

    def compose(self, ctx, slots, st):
        """st: t, rot (predator ring), offsets[8] (per-fish lag during migration), swim, phase, hp, n_arms, emerge,
        landed (bool), grab, latch, act (dict slot->act), blur, plaque_fade."""
        t = st.get("t", 0.0)
        phase = st.get("phase", 1)
        n_arms = st.get("n_arms", arms_for_hp(st.get("hp", 1.0)))
        rot = st.get("rot", 0.0)
        offs = st.get("offsets", [0.0] * NS)
        out = K.rgba(ctx.size)
        out.alpha_composite(self.back(ctx, phase))
        out.alpha_composite(self.cached(("zones", ctx.S, round(t * 4) / 4), lambda: self.zones(ctx, t)))
        band, fish = self.predators(ctx, slots, rot, t, st.get("swim", 0.0), offs, st.get("act", {}))
        if st.get("blur", 0) > 0.5:     # motion trail on the fish only (the tank does not move)
            acc = np.zeros((ctx.C, ctx.C, 4), np.float32)
            n = 7
            for k in range(n):
                acc += np.asarray(K.rot_c(fish, -st["blur"] * k / n * 0.6, Image.BILINEAR), np.float32) * (1 - k / n * 0.6)
            fish = Image.fromarray(np.clip(acc / sum(1 - k / n * 0.6 for k in range(n)), 0, 255).astype(np.uint8), "RGBA")
        out.alpha_composite(fish)
        if st.get("school", 0) > 0:
            u = st["school"]
            sch = K.rgba(ctx.size)
            sd = ImageDraw.Draw(sch)
            r_ = K.rng(77)
            for j in range(46):
                a0 = -30 + 300 * u + r_.uniform(-14, 14)
                rad = r_.uniform(160, 320)
                x, y = ctx.P(rad, a0)
                tx, ty = ctx.P(rad, a0 - 3.5)
                sd.line([(tx, ty), (x, y)], fill=(200, 220, 235, 230), width=max(1, int(3 * ctx.S)))
            out.alpha_composite(K.masked(sch, K.ring_mask(ctx.size, ctx.cx, ctx.cy, R_TANK * ctx.S, R_BAND * ctx.S)))
        # the forecast / landed predators glow in their zone under each arm
        landed_cols = {}
        under = []
        for j in range(n_arms):
            a = ARM_ANGLES[j]
            i = int(round(((a - rot) % 360) / SD)) % NS
            under.append(i)
            landed_cols[j] = K.TYPE_COL[slots[i]["type"]]
        if st.get("landed"):
            for i in set(under):
                wm = wedge(ctx, i, rot, R_IN, R_OUT, inset=2)
                e = ImageChops.subtract(wm, K.shrink(wm, 3 * ctx.S))
                out.alpha_composite(K.solid(e, (255, 236, 200), 0.9))
        out.alpha_composite(band)
        out.alpha_composite(self.wall(ctx, n_arms))
        out.alpha_composite(self.hp_arc(ctx, st.get("hp", 1.0)))
        out.alpha_composite(self.tank(ctx, t, phase, n_arms, blink=st.get("blink", 0.0)))
        arms_l = self.arms(ctx, n_arms, t, emerge=st.get("emerge"), grab=st.get("grab", 0.0),
                                      landed_cols=landed_cols if (st.get("landed") or st.get("show_tips", True)) else None,
                                      latch=st.get("latch", 0.0), phase=phase,
                                      cyber=st.get("reveal", 1.0) if n_arms >= 8 else 0.0, emerge_from=st.get("emerge_from"))
        out.alpha_composite(arms_l)
        stage = st.get("stage", max(0, n_arms // 2 - 1))
        hk = 1.0 + (0.32 * st.get("reveal", 1.0) if stage >= 3 else 0.0)     # the reveal: it climbs OUT, over the tank rim
        if hk > 1.001:
            c2 = W.Ctx(ctx.S * hk)
            hd = self.head(c2, t, stage, blink=st.get("blink", 0.0), reveal=st.get("reveal", 1.0))
            o = int((c2.C - ctx.C) / 2)
            dy = int(26 * ctx.S)
            hd = hd.crop((o, o + dy, o + ctx.C, o + ctx.C + dy))
            out.alpha_composite(hd)
        else:
            out.alpha_composite(self.head(ctx, t, stage, blink=st.get("blink", 0.0), reveal=st.get("reveal", 1.0)))
        out.alpha_composite(self.plaques(ctx, slots, rot, [0.0] * NS, fade=st.get("plaque_fade", 1.0)))
        out.alpha_composite(self.banner(ctx, phase, n_arms))
        return out, under
