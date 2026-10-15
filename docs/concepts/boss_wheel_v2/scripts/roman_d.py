"""Boss Wheel v2: Aurelian Concord FINAL (designer direction): "the wheel IS the colosseum arena pit, seen from above".

- The whole spinner is the arena floor, top-down: raked sand, the arena wall (the D4 bezel in travertine) as the rim,
  the stands and crowd beyond it (static), the emperor's box on the wall at the top: the VERDICT emoji hand is the needle.
- OUTER slice ring = the chariot track (r 246-352): one tiny quadriga per slice position, its driver's plume and cloth
  in the slice TYPE colour (team colour = type). Chariots hold station in their slice and gallop in place while the
  track streams under them (dust, rake lines), so a chariot always means its slice. The blank slice is an empty lane.
- INNER ring = the fighting floor (r 130-242), a boss inner ring of 3 segments x 10 ticks (round 45 rules: the active
  segment under the needle is raised + lit with a notch tick, the others dim; the outer slice under the needle carries
  the ghost wedge with the modifier's mark). LION = x2, RETIARIUS (the net) = ANCHOR, MURMILLO = PIERCE.
- Hub: the captives ("innocent gladiators") huddled round a stake in a small pen: the stakes of the fight.
- Slice borders are only chalk lines in the sand; type colour lives in the thin rim band and the plaques.
- Phase 2/3: the crowd fills, braziers light on the wall, the four gates open and beasts walk in; P3 fire.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
import render2d as RD
import roman as RM
import wheel_v2 as W
from shapes import Pen

VERD, TRAV, GILT = RM.VERD, RM.TRAV, RM.GILT
TRACK_IN, INNER_OUT = 246, 238
INNER = [  # (name, modifier, mark, tint)
    ("LION", "x2 DOUBLE", "x2", (255, 210, 77)),
    ("RETIARIUS", "ANCHOR", "anchor", (176, 196, 214)),
    ("MURMILLO", "PIERCE", "pierce", (242, 246, 255)),
]
SAND = (196, 160, 112)
SHADOW_OFF = (5, 8)       # screen-space shadow offset (light from the top left), master units


def rotate_sprite(spr, ang):
    return spr.rotate(-ang, resample=Image.BICUBIC, expand=True)


def with_shadow(spr, S, k=0.55):
    """Shadow computed in SCREEN space after rotation (the light does not turn with the floor)."""
    spr = K.keyline(spr, max(1, 1.3 * S), col=(30, 18, 12), soft=0.4)
    a = K.blur(spr.split()[3], 2.2 * S)
    pad = int(12 * S)
    out = K.rgba((spr.width + 2 * pad, spr.height + 2 * pad))
    out.alpha_composite(K.solid(a, (40, 22, 12), k), (pad + int(SHADOW_OFF[0] * S * 0.6), pad + int(SHADOW_OFF[1] * S * 0.6)))
    out.alpha_composite(spr, (pad, pad))
    return out


# ------------------------------------------------------------------ tiny units, top-down (facing +x)
def quadriga(px, team, t, act=0.0, seed=0):
    """Top-down four-horse chariot facing +x. px = sprite width. team = the driver's plume / cloth colour."""
    ss = 3
    W_ = px * ss
    H_ = int(W_ * 0.55)
    k = W_ / 100.0
    im = K.rgba((W_, H_))
    d = ImageDraw.Draw(im)
    cy = H_ / 2
    ph = t * 9 + seed
    horse_cols = [(244, 238, 226), (30, 24, 22), (236, 228, 214), (40, 30, 26)]
    # dust trail behind the car
    r = K.rng(seed + int(t * 12))
    for j in range(10):
        x = (8 - r.uniform(0, 10 + 14 * act)) * k
        y = cy + r.uniform(-12, 12) * k
        q = r.uniform(2, 5) * k
        d.ellipse([x - q, y - q, x + q, y + q], fill=(214, 186, 140, int(r.uniform(40, 110))))
    # the car: a D-shape opening backward, two wheels at the sides
    car_x = 22 * k
    for sgn in (-1, 1):
        d.rounded_rectangle([car_x - 9 * k, cy + sgn * 13 * k - 2.2 * k, car_x + 9 * k, cy + sgn * 13 * k + 2.2 * k], radius=1.5 * k, fill=(28, 20, 16, 255))
    d.line([(car_x - 4 * k, cy - 14 * k), (car_x - 4 * k, cy + 14 * k)], fill=(50, 36, 26, 255), width=int(2 * k))
    d.pieslice([car_x - 12 * k, cy - 12 * k, car_x + 12 * k, cy + 12 * k], -90, 90, fill=(150, 104, 54, 255))
    d.rectangle([car_x - 8 * k, cy - 12 * k, car_x, cy + 12 * k], fill=(150, 104, 54, 255))
    d.arc([car_x - 12 * k, cy - 12 * k, car_x + 12 * k, cy + 12 * k], -90, 90, fill=GILT + (255,), width=int(2 * k))
    # the driver: shoulders + head + crested helmet in the team colour, cloak flaring back
    dx = car_x + 2 * k
    d.polygon([(dx - 4 * k, cy - 7 * k), (dx - 16 * k, cy - 10 * k + 2 * k * math.sin(ph)), (dx - 18 * k, cy + 9 * k), (dx - 4 * k, cy + 7 * k)], fill=team + (255,))
    d.ellipse([dx - 5 * k, cy - 7 * k, dx + 5 * k, cy + 7 * k], fill=(196, 150, 110, 255))
    d.ellipse([dx - 3.6 * k, cy - 3.6 * k, dx + 3.6 * k, cy + 3.6 * k], fill=(120, 110, 100, 255))
    d.line([(dx - 4 * k, cy), (dx + 3 * k, cy)], fill=team + (255,), width=int(2.2 * k))
    # pole + reins
    d.line([(car_x + 10 * k, cy), (car_x + 36 * k, cy)], fill=(60, 40, 26, 255), width=int(1.6 * k))
    # four horses abreast, galloping (heads bob, legs flick)
    hx0 = car_x + 30 * k
    for j in range(4):
        hy = cy + (j - 1.5) * 9.5 * k
        bob = 2.2 * k * math.sin(ph + j * 0.9)
        c = horse_cols[j]
        d.line([(dx + 3 * k, cy), (hx0 + 30 * k, hy)], fill=(40, 30, 20, 180), width=max(1, int(0.8 * k)))
        d.ellipse([hx0, hy - 4 * k, hx0 + 26 * k, hy + 4 * k], fill=c + (255,))
        d.ellipse([hx0 + 22 * k + bob, hy - 3 * k, hx0 + 36 * k + bob, hy + 3 * k], fill=c + (255,))     # neck + head
        d.ellipse([hx0 + 32 * k + bob, hy - 2.4 * k, hx0 + 39 * k + bob, hy + 2.4 * k], fill=K.mul(c, 0.8) + (255,))
        for lj, (lx, side) in enumerate(((4, -1), (6, 1), (20, -1), (22, 1))):
            sw = 5 * k * math.sin(ph * 1.0 + j + lj * 1.6)
            d.ellipse([hx0 + lx * k + sw - 2 * k, hy + side * 4.5 * k - 1.2 * k, hx0 + lx * k + sw + 2 * k, hy + side * 4.5 * k + 1.2 * k], fill=K.mul(c, 0.7) + (255,))
        d.line([(hx0 + 1 * k, hy), (hx0 - 6 * k, hy + 2 * k * math.sin(ph + j))], fill=K.mul(c, 0.6) + (255,), width=int(2 * k))   # tail
        # team colour plume on the bridle
        d.ellipse([hx0 + 30 * k + bob, hy - 1.4 * k, hx0 + 33 * k + bob, hy + 1.4 * k], fill=team + (255,))
    return im.resize((px, int(px * 0.55)), Image.LANCZOS)


def fighter(d, x, y, k, kind, team, face, t, lunge=0.0):
    """One tiny gladiator top-down at (x,y), facing angle `face` (rad). kind: retiarius, secutor, murmillo, thraex, bestiarius."""
    ca, sa = math.cos(face), math.sin(face)
    def P(u, v):
        return (x + (u * ca - v * sa) * k, y + (u * sa + v * ca) * k)
    bob = math.sin(t * 6 + x * 0.01) * 0.8
    u0 = lunge * 6
    # shoulders + head
    d.ellipse([P(u0, 0)[0] - 5 * k, P(u0, 0)[1] - 5 * k, P(u0, 0)[0] + 5 * k, P(u0, 0)[1] + 5 * k], fill=(186, 140, 100, 255))
    sh = [P(u0 - 2, -7), P(u0 + 2, -7), P(u0 + 2, 7), P(u0 - 2, 7)]
    d.polygon(sh, fill=team + (255,))
    hx, hy = P(u0 + 0.5, 0)
    d.ellipse([hx - 3.2 * k, hy - 3.2 * k, hx + 3.2 * k, hy + 3.2 * k], fill=(150, 150, 156, 255) if kind != "retiarius" else (90, 60, 40, 255))
    if kind in ("murmillo", "secutor", "thraex"):
        d.line([P(u0 - 3, 0), P(u0 + 4, 0)], fill=team + (255,), width=max(1, int(1.6 * k)))              # crest
    if kind in ("murmillo", "secutor"):
        d.polygon([P(u0 + 4, -8), P(u0 + 7, -8), P(u0 + 7, 6), P(u0 + 4, 6)], fill=(150, 30, 40, 255))   # big scutum
        d.line([P(u0 + 2, 6), P(u0 + 12 + 6 * lunge, 7 + bob)], fill=(220, 224, 230, 255), width=max(1, int(1.2 * k)))
    elif kind == "thraex":
        d.polygon([P(u0 + 4, -6), P(u0 + 6, -6), P(u0 + 6, 0), P(u0 + 4, 0)], fill=(170, 130, 50, 255))
        d.arc([P(u0 + 4, 2)[0] - 6 * k, P(u0 + 4, 2)[1] - 6 * k, P(u0 + 4, 2)[0] + 6 * k, P(u0 + 4, 2)[1] + 6 * k], 0, 90, fill=(220, 224, 230, 255), width=max(1, int(1.2 * k)))
    elif kind == "retiarius":
        nx, ny = P(u0 + 9 + 4 * lunge, -4)
        rr = (5 + 3 * lunge) * k
        d.ellipse([nx - rr, ny - rr, nx + rr, ny + rr], outline=(220, 210, 180, 230), width=max(1, int(0.8 * k)))
        d.line([(nx - rr, ny), (nx + rr, ny)], fill=(220, 210, 180, 200), width=max(1, int(0.6 * k)))
        d.line([(nx, ny - rr), (nx, ny + rr)], fill=(220, 210, 180, 200), width=max(1, int(0.6 * k)))
        d.line([P(u0, 6), P(u0 + 16 + 6 * lunge, 6)], fill=(200, 200, 210, 255), width=max(1, int(1.2 * k)))     # trident
        for q in (-1.5, 0, 1.5):
            d.line([P(u0 + 16 + 6 * lunge, 6 + q), P(u0 + 19 + 6 * lunge, 6 + q)], fill=(200, 200, 210, 255), width=max(1, int(0.8 * k)))
    elif kind == "bestiarius":
        d.line([P(u0 - 4, 4), P(u0 + 18 + 6 * lunge, 4)], fill=(170, 130, 80, 255), width=max(1, int(1.2 * k)))
        d.polygon([P(u0 + 18 + 6 * lunge, 2.5), P(u0 + 22 + 6 * lunge, 4), P(u0 + 18 + 6 * lunge, 5.5)], fill=(220, 224, 230, 255))


def lion_top(d, x, y, k, face, t, pounce=0.0):
    ca, sa = math.cos(face), math.sin(face)
    def P(u, v):
        return (x + (u * ca - v * sa) * k, y + (u * sa + v * ca) * k)
    u0 = pounce * 8
    body = [P(u0 + a * 9, b * 5) for a, b in ((1, 0), (0.7, 0.7), (0, 1), (-0.8, 0.8), (-1.1, 0), (-0.8, -0.8), (0, -1), (0.7, -0.7))]
    d.polygon(body, fill=(190, 140, 70, 255))
    mx, my = P(u0 + 8, 0)
    d.ellipse([mx - 6.5 * k, my - 6.5 * k, mx + 6.5 * k, my + 6.5 * k], fill=(120, 70, 30, 255))
    hx, hy = P(u0 + 10.5, 0)
    d.ellipse([hx - 3.6 * k, hy - 3.6 * k, hx + 3.6 * k, hy + 3.6 * k], fill=(200, 150, 80, 255))
    tx, ty = P(u0 - 10, 0)
    sw = math.sin(t * 3) * 4
    d.line([(tx, ty), P(u0 - 18, sw)], fill=(170, 120, 60, 255), width=max(1, int(1.6 * k)))
    for lx, side in ((5, -1), (5, 1), (-6, -1), (-6, 1)):
        fx, fy = P(u0 + lx + math.sin(t * 5 + lx) * 1.5 * (1 + pounce), side * 5.5)
        d.ellipse([fx - 1.6 * k, fy - 1.6 * k, fx + 1.6 * k, fy + 1.6 * k], fill=(150, 100, 50, 255))


class ArenaPitD(RM.ArenaA):
    key = "D"
    title = "FINAL  THE ARENA PIT"
    blurb = ["The wheel is the arena pit seen from above: chariots race the outer track (one per slice,",
             "plumed in the slice colour), gladiators fight on the inner ring (x2 / ANCHOR / PIERCE), captives wait",
             "in the centre, and the emperor's box on the wall gives the thumb."]
    mat = dict(base=(170, 148, 114), hi=(244, 232, 206), lo=(60, 46, 36), accent=VERD, glass=(30, 22, 16))
    telemetry = "THE ROSTRUM // AURELIAN CONCORD // THE GRAND STAND // VERDICT // LUDI CIRCENSES"

    # -------- the floor (turns with the wheel): track + fighting floor + chalk
    def art_ring_under(self, ctx):
        tq = round(ctx.t * 12) / 12.0 if not ctx.get("still") else 0.0
        return self.cached(("underD", ctx.S, ctx.phase, round(ctx.get("dmg", 0), 2), tq), lambda: self._floor(ctx, tq))

    def _floor(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        rr, ang = K.polar_field(ctx.size, cx, cy)
        n = K.noise(ctx.size, int(26 * S), 5, 4)
        n2 = K.noise(ctx.size, int(5 * S), 6, 2)
        sand = np.array(SAND, np.float32) * (0.72 + 0.32 * n[..., None] + 0.08 * n2[..., None])
        track = rr > TRACK_IN * S
        # the track: darker compacted sand with ruts that STREAM backward (the chariots gallop in place)
        flow = t * 40.0
        ruts = 0.86 + 0.14 * np.sin((rr / S) * 0.9) * (0.6 + 0.4 * np.sin(np.radians(ang * 6 - flow * 3)))
        sand = np.where(track[..., None], sand * 0.86 * ruts[..., None], sand)
        # rake lines on the fighting floor
        rake = 0.94 + 0.06 * np.sin(np.radians(ang) * 90 + (rr / S) * 0.05)
        sand = np.where(track[..., None], sand, sand * rake[..., None])
        a = ((rr <= 356 * S) * 255).astype(np.float32)
        im = Image.fromarray(np.concatenate([np.clip(sand, 0, 255), a[..., None]], 2).astype(np.uint8), "RGBA")
        if ctx.phase >= 2:
            st = K.particles(ctx.size, 22, 41, 6 * S, 18 * S, (110, 24, 20), (50, 110))
            im.alpha_composite(K.masked(K.blur(st, 5 * S), im.split()[3]))
        if ctx.phase >= 3:   # the arena glows red from the burning stands; embers on the sand
            glow = K.ring_mask(ctx.size, cx, cy, 250 * S, 356 * S)
            im = K.add(im, K.masked(K.solid(K.blur(glow, 30 * S), (255, 80, 30)), im.split()[3]), 0.35)
            emb = K.particles(ctx.size, 90, 43 + int(t * 6), 1.2 * S, 3 * S, (255, 170, 80), (120, 255))
            im = K.add(im, K.masked(K.blur(emb, 1.2 * S), im.split()[3]), 1.0)
        if ctx.get("dmg", 0) > 0:
            im.alpha_composite(W.crack_layer(ctx, ctx.get("dmg"), 150, 340, 52, col=(70, 46, 28), glow=(255, 140, 60)))
        return im

    def separators(self, ctx, slots):
        """Slice borders: just chalk lines across the track (and a faint rake break)."""
        S = ctx.S
        lay = K.rgba(ctx.size)
        d = ImageDraw.Draw(lay)
        for i in range(len(slots)):
            a = W.slot_angle(i, ctx.rot) + W.SLOT_DEG / 2
            for q in range(10):
                r0 = TRACK_IN + 4 + q * 10.5
                d.line([ctx.P(r0, a), ctx.P(r0 + 6, a)], fill=(246, 238, 220, 120), width=max(1, int(2 * S)))
        return lay

    def slice_glass(self, ctx, i, rot, wm, slot):
        return K.rgba(ctx.size)

    def blank_window(self, ctx, i, rot, wm, back, under):
        """The blank slice: an empty lane. The track is dimmed and desaturated, a thin empty outline, no chariot."""
        S = ctx.S
        lay = K.rgba(ctx.size)
        tm = W.wedge_mask(ctx, i, rot, TRACK_IN, W.R["sl_out"])
        lay.alpha_composite(K.solid(tm, (10, 8, 12), 0.55))
        em = W.wedge_mask(ctx, i, rot, TRACK_IN, W.R["sl_out"], inset=10)
        edge = ImageChops.subtract(em, K.shrink(em, max(1, 2.2 * S)))
        lay.alpha_composite(K.solid(edge, (150, 150, 160), 0.9))
        # a lost wheel lying in the empty lane (nothing here)
        x, y = ctx.P(318, W.slot_angle(i, rot) + 18)
        d = ImageDraw.Draw(lay)
        d.ellipse([x - 9 * S, y - 9 * S, x + 9 * S, y + 9 * S], outline=(60, 44, 30, 200), width=max(1, int(2.4 * S)))
        return lay

    # -------- chariots on the track: one per slice, plumed in the slice colour
    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 12) / 12.0 if not ctx.get("still") else 0.0
        return self.cached(("scD", ctx.S, i, tq, round(act, 2), round(ctx.rot, 2)), lambda: self._chariot(slot, ctx, tq, act, i))

    def _chariot(self, slot, ctx, t, act, i):
        S = ctx.S
        w = W.scene_box(ctx)
        spr = K.rgba((w, w))
        a = W.slot_angle(i, ctx.rot)
        sc = W.slice_centre(ctx, i, ctx.rot)
        surge = 14 * math.sin(math.pi * min(1, act)) if act > 0 else 0.0
        ca = a + 19 + surge + 1.2 * math.sin(t * 2 + i)          # just ahead of the plaque, along the track
        px_, py_ = ctx.P(316, ca)
        team = K.TYPE_COL[slot["type"]]
        q = quadriga(int(122 * S), team, t + i * 0.37, act, seed=i * 7)
        q = rotate_sprite(q, ca)          # sprite faces +x; the clockwise tangent at screen angle ca is +x turned by ca
        q = with_shadow(q, S)
        spr.alpha_composite(q, (int(px_ - sc[0] + w / 2 - q.width / 2), int(py_ - sc[1] + w / 2 - q.height / 2)))
        if act > 0.05:      # dust burst + speed lines on the landing (the overtake)
            d = ImageDraw.Draw(spr)
            r = K.rng(i)
            for j in range(16):
                aa = ca - r.uniform(4, 16)
                rr = 312 + r.uniform(-16, 16)
                x, y = ctx.P(rr, aa)
                qq = r.uniform(3, 8) * S * (0.5 + act)
                d.ellipse([x - sc[0] + w / 2 - qq, y - sc[1] + w / 2 - qq, x - sc[0] + w / 2 + qq, y - sc[1] + w / 2 + qq],
                          fill=(226, 200, 156, int(150 * act)))
        return spr

    # -------- the inner ring: the fighting floor, 3 segments (round 45 rules)
    def inner_ring(self, ctx, slots):
        tq = round(ctx.t * 12) / 12.0 if not ctx.get("still") else 0.0
        irot = ctx.get("inner_rot", 0.0)
        key = ("innerD", ctx.S, tq, round(irot, 2), round(ctx.rot, 2), ctx.get("landed"), round(ctx.get("finisher", 0), 2), round(ctx.get("blur", 0), 1))
        return self.cached(key, lambda: self._inner(ctx, slots, tq, irot))

    def _inner(self, ctx, slots, t, irot):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        lay = K.rgba(ctx.size)
        ann = K.ring_mask(ctx.size, cx, cy, W.R["hub_rim"] - 4 * S, INNER_OUT * S)
        rr, ang = K.polar_field(ctx.size, cx, cy)
        n = K.noise(ctx.size, int(20 * S), 15, 3)
        sand = np.array((214, 182, 132), np.float32) * (0.78 + 0.3 * n[..., None])
        rake = 0.93 + 0.07 * np.sin((rr / S) * 0.55)
        sand = sand * rake[..., None]
        floor = Image.fromarray(np.concatenate([np.clip(sand, 0, 255), np.asarray(ann, np.float32)[..., None]], 2).astype(np.uint8), "RGBA")
        lay.alpha_composite(floor)
        # which segment is under the needle (0 deg)
        act_seg = int(((-irot) % 360) // 120)
        d = ImageDraw.Draw(lay)
        for sgi, (nm, mod, mark, tint) in enumerate(INNER):
            a0 = sgi * 120 + irot
            seg = K.ring_mask(ctx.size, cx, cy, W.R["hub_rim"] - 4 * S, INNER_OUT * S, a0 + 1.2, a0 + 120 - 1.2)
            if sgi != act_seg:
                lay = Image.composite(K.tone(lay, 0.8, 0.72), lay, seg)
            else:   # raised + lit: a tint edge glow
                edge = ImageChops.subtract(seg, K.shrink(seg, 4 * S))
                lay.alpha_composite(K.solid(edge, tint, 0.6))
                lay = K.add(lay, K.solid(K.blur(edge, 6 * S), tint), 0.25)
            d = ImageDraw.Draw(lay)
            # segment dividers: low wooden barriers
            d.line([ctx.P(W.R["hub_rim"], a0), ctx.P(INNER_OUT, a0)], fill=(96, 64, 40, 255), width=max(1, int(5 * S)))
            # 10 ticks per segment on the outer lip
            for k_ in range(10):
                aa = a0 + 6 + k_ * 12
                d.line([ctx.P(INNER_OUT - 8, aa), ctx.P(INNER_OUT - 2, aa)], fill=(120, 90, 60, 200), width=max(1, int(1.6 * S)))
            # the vignette: two fighters spar at the segment's centre
            ca = a0 + 60
            fx, fy = ctx.P(188, ca)
            face = math.radians(ca)          # radial axis
            sp = 1.2 * math.sin(t * 3.0 + sgi)
            fin = ctx.get("finisher", 0.0) if sgi == act_seg else 0.0
            kk = 3.1 * S
            tmp = K.rgba(ctx.size)
            td = ImageDraw.Draw(tmp)
            perp = face + math.pi / 2
            ox, oy = math.cos(perp) * (12 - sp) * kk, math.sin(perp) * (12 - sp) * kk
            if nm == "LION":
                lion_top(td, fx + ox, fy + oy, kk, perp + math.pi, t, pounce=fin)
                fighter(td, fx - ox, fy - oy, kk, "bestiarius", VERD, perp, t, lunge=0.3 * math.sin(t * 3))
            elif nm == "RETIARIUS":
                fighter(td, fx + ox, fy + oy, kk, "retiarius", VERD, perp + math.pi, t, lunge=fin + 0.3 * max(0, math.sin(t * 3)))
                fighter(td, fx - ox, fy - oy, kk, "secutor", (200, 60, 60), perp, t)
            else:
                fighter(td, fx + ox, fy + oy, kk, "murmillo", VERD, perp + math.pi, t, lunge=fin + 0.3 * max(0, math.sin(t * 3 + 1)))
                fighter(td, fx - ox, fy - oy, kk, "thraex", (220, 160, 60), perp, t)
            tmp = K.keyline(tmp, max(1, 1.2 * S), col=(30, 18, 12), soft=0.4)
            sh = K.solid(K.shifted(K.blur(tmp.split()[3], 1.6 * S), SHADOW_OFF[0] * S * 0.5, SHADOW_OFF[1] * S * 0.5), (60, 36, 18), 0.5)
            lay.alpha_composite(sh)
            lay.alpha_composite(tmp)
            # (round 45: modifier words only on hover / aim; the ghost wedge marks carry it at rest)
        # notch tick at the needle for the active segment
        d = ImageDraw.Draw(lay)
        tint = INNER[act_seg][3]
        d.polygon([ctx.P(INNER_OUT + 2, -3), ctx.P(INNER_OUT + 2, 3), ctx.P(INNER_OUT - 14, 0)], fill=tint + (255,))
        # the curb between the fighting floor and the track (spina wall) with a verdigris neon line
        curb = K.ring_mask(ctx.size, cx, cy, INNER_OUT * S, TRACK_IN * S)
        lay.alpha_composite(RD.relief(curb, ctx.size, stone=(206, 190, 160), shadow=(80, 64, 50), hi=(255, 248, 230), s=S, depth=3))
        neon = K.ring_mask(ctx.size, cx, cy, (TRACK_IN - 2.5) * S, (TRACK_IN - 0.5) * S)
        lay = K.add(lay, K.solid(K.blur(neon, 3 * S), VERD), 0.8)
        lay.alpha_composite(K.solid(neon, K.mix(VERD, (255, 255, 255), 0.4)))
        # ghost wedge on the outer slice under the needle: the active modifier's mark tiled at 24 %
        if ctx.get("blur", 0) < 1:
            ia = int(round(((-ctx.rot) % 360) / 60.0)) % 6
            if slots[ia]["type"] != "NULL":
                wm = W.wedge_mask(ctx, ia, ctx.rot, TRACK_IN + 4, W.R["band_in"] - 2)
                marks = K.rgba(ctx.size)
                md = ImageDraw.Draw(marks)
                f = K.f_ui(int(20 * S), b"Bold Condensed")
                txt = {"x2": "x2", "anchor": "ANCHOR", "pierce": ">>"}[INNER[act_seg][2]]
                for rr_ in (264, 300, 334):
                    for da in range(-28, 30, 12 if txt != "ANCHOR" else 22):
                        x, y = ctx.P(rr_, W.slot_angle(ia, ctx.rot) + da + (6 if rr_ == 300 else 0))
                        md.text((x, y), txt, font=f, fill=INNER[act_seg][3] + (70,), anchor="mm")
                lay.alpha_composite(K.masked(marks, wm))
                edge = ImageChops.subtract(wm, K.shrink(wm, 2.5 * S))
                lay.alpha_composite(K.solid(edge, INNER[act_seg][3], 0.55))
        return lay

    # -------- the hub: the captives huddled round a stake
    def hub(self, ctx):
        tq = round(ctx.t * 6) / 6.0 if not ctx.get("still") else 0.0
        return self.cached(("hubD", ctx.S, ctx.phase, tq), lambda: self._captives(ctx, tq))

    def _captives(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        im = K.rgba(ctx.size)
        R0 = W.R["hub_rim"] * S
        pen = K.ring_mask(ctx.size, cx, cy, 0, R0)
        n = K.noise(ctx.size, int(14 * S), 8, 3)
        sand = K.solid(pen, (150, 118, 84))
        sand = K.tone_map(sand, np.ones_like(n), 0.75 + 0.35 * n)
        im.alpha_composite(sand)
        # the pen: a ring of stakes (palisade) top-down + a grate
        d = ImageDraw.Draw(im)
        for k_ in range(28):
            x, y = K.pol(cx, cy, (W.R["hub_rim"] - 8) * S, k_ * 360 / 28)
            d.ellipse([x - 4.5 * S, y - 4.5 * S, x + 4.5 * S, y + 4.5 * S], fill=(90, 60, 36, 255))
            d.ellipse([x - 2.6 * S, y - 2.6 * S, x + 1 * S, y + 1 * S], fill=(140, 100, 64, 255))
        # the stake at the centre, ropes radiating to the captives
        caps = K.rgba(ctx.size)
        cd = ImageDraw.Draw(caps)
        r = K.rng(3)
        # the stake (upright post, high 3/4) with ropes to the captives
        cd.rounded_rectangle([cx - 3 * S, cy - 44 * S, cx + 3 * S, cy + 6 * S], radius=2 * S, fill=(96, 62, 36, 255))
        cd.ellipse([cx - 5 * S, cy - 48 * S, cx + 5 * S, cy - 40 * S], fill=(120, 80, 46, 255))
        spots = [(-44, -6), (-24, 14), (0, 24), (26, 14), (46, -4), (-30, -30), (32, -28), (-8, -40), (12, 40), (-40, 30)]
        tunics = [(214, 204, 180), (170, 154, 128), (196, 182, 154), (150, 128, 104), (226, 218, 198)]
        order = sorted(range(len(spots)), key=lambda j: spots[j][1])
        for j in order:
            sx, sy = spots[j]
            x, y = cx + sx * S + 0.8 * S * math.sin(t * 7 + j * 2.1), cy + sy * S
            cd.line([(cx, cy - 20 * S), (x, y - 10 * S)], fill=(176, 146, 96, 200), width=max(1, int(1.4 * S)))
            tc = tunics[j % len(tunics)]
            kneel = j % 3 != 0
            hgt = 14 if kneel else 20
            cd.polygon([(x - 7 * S, y), (x + 7 * S, y), (x + 5 * S, y - hgt * S), (x - 5 * S, y - hgt * S)], fill=tc + (255,))     # tunic
            cd.line([(x - 5 * S, y - hgt * 0.6 * S), (x + 5 * S, y - hgt * 0.6 * S)], fill=K.mul(tc, 0.7) + (255,), width=max(1, int(1.5 * S)))  # bound arms
            hy = y - hgt * S - 4.5 * S + (1.5 * S if kneel else 0)
            cd.ellipse([x - 4.6 * S, hy - 4.6 * S, x + 4.6 * S, hy + 4.6 * S], fill=(150, 104, 72, 255))
            cd.ellipse([x - 4.8 * S, hy - 5 * S, x + 4.8 * S, hy - 0.5 * S], fill=(54, 36, 26, 255))                      # hair
        caps = K.keyline(caps, max(1, 1.1 * S), col=(40, 24, 14), soft=0.4)
        sh = K.solid(K.shifted(K.blur(caps.split()[3], 2 * S), 3 * S, 5 * S), (40, 24, 14), 0.5)
        im.alpha_composite(K.masked(sh, pen))
        im.alpha_composite(caps)
        d = ImageDraw.Draw(im)
        # name plate + a gilt rim
        t1 = K.text_img(self.hub_name, K.f_ui(int(12 * S), b"Bold Condensed"), fill=(250, 244, 230), stroke=max(1, int(1.5 * S)))
        pw, ph = t1.width + 12 * S, t1.height + 4 * S
        d.rounded_rectangle([cx - pw / 2, cy + 88 * S - ph / 2, cx + pw / 2, cy + 88 * S + ph / 2], radius=4 * S, fill=(14, 8, 12, 220), outline=VERD + (255,))
        K.paste_c(im, t1, cx, cy + 88 * S)
        for rr_, col, wd in ((W.R["hub_rim"] + 1, (90, 66, 44), 6), (W.R["hub_rim"] + 3, VERD, 2)):
            d.ellipse([cx - rr_ * S, cy - rr_ * S, cx + rr_ * S, cy + rr_ * S], outline=col + (255,), width=max(1, int(wd * S)))
        return im

    # -------- over the wall: gates, braziers, beasts entering (static; the floor turns under them)
    def art_ring_over(self, ctx):
        tq = round(ctx.t * 8) / 8.0 if not ctx.get("still") else 0.0
        return self.cached(("overD", ctx.S, ctx.phase, tq, round(ctx.get("gates", 0), 2), round(ctx.get("dmg", 0), 2)),
                           lambda: self._wall(ctx, tq))

    def _wall(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        out = K.rgba(ctx.size)
        d = ImageDraw.Draw(out)
        gates_open = ctx.get("gates", 1.0 if ctx.phase >= 2 else 0.0)
        for a in (60, 120, 240, 300):
            # the gate: a dark opening through the wall with a portcullis that lifts
            gm = K.ring_mask(ctx.size, cx, cy, (W.R["bezel_in"] - 2) * S, (W.R["bezel_out"] + 4) * S, a - 5, a + 5)
            out.alpha_composite(K.solid(gm, (14, 8, 6)))
            d = ImageDraw.Draw(out)
            for q in range(5):
                aa = a - 4 + q * 2
                r0 = W.R["bezel_in"] + (W.R["bezel_out"] - W.R["bezel_in"]) * gates_open
                d.line([K.pol(cx, cy, r0 * S, aa), K.pol(cx, cy, (W.R["bezel_out"] + 2) * S, aa)], fill=(70, 60, 50, 255), width=max(1, int(2.2 * S)))
            # braziers either side of the gate, lit from phase 2
            for side in (-1, 1):
                x, y = K.pol(cx, cy, (W.R["bezel_out"] + 14) * S, a + side * 9)
                d.ellipse([x - 7 * S, y - 7 * S, x + 7 * S, y + 7 * S], fill=(60, 44, 30, 255), outline=(150, 120, 80, 255))
                if ctx.phase >= 2:
                    fl = 1 + 0.25 * math.sin(t * 9 + a + side)
                    fm = K.ring_mask(ctx.size, x, y, 0, 6 * S * fl)
                    out.alpha_composite(K.solid(fm, (255, 190, 90)))
                    out = K.add(out, K.solid(K.blur(fm, 12 * S), (255, 120, 40)), 1.2)
                    d = ImageDraw.Draw(out)
            # beasts walk in through the open gates (phase 2+)
            if gates_open > 0.3:
                bx, by = K.pol(cx, cy, (W.R["bezel_in"] - 12 - 16 * gates_open) * S, a)
                tmp = K.rgba(ctx.size)
                lion_top(ImageDraw.Draw(tmp), bx, by, 1.7 * S, math.radians(a + 90 + 90), t, 0)
                out.alpha_composite(K.solid(K.shifted(K.blur(tmp.split()[3], 1.6 * S), 3 * S, 5 * S), (40, 24, 12), 0.5))
                out.alpha_composite(tmp)
        return out
