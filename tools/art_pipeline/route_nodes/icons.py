"""The node icon trio (REST, WORKSHOP, CACHE) in three directions, as Doc vector sources (130 x 130, the route art's canvas).

Family rules read from the shipped route art (assets/netrun/route/node_*.png, round 37 r32ui.node_sd) and measured: canvas 130,
die-cut 122 wide (centre 65), white band 9, ink keyline 5, bright accent ring 4 inside the keyline, a dark tinted field, a
cream pictogram with an ink outline, two faint gloss streaks. The state ring is NOT in the icon (the overlay draws it).
"""
import math
from vec import *

C = (65, 65)
INK = (17, 17, 17)
WHITE = (252, 251, 249)
EDGE = (109, 105, 110)
CREAM = (248, 245, 234)

# kind colours = the street room glow colours (street_route.tres rooms.colors), so the sticker and its room are one thing
KIND = {
    "rest": dict(acc=(191, 115, 255), field=(46, 28, 76), hi=(86, 52, 132), mid=(150, 92, 214)),
    "workshop": dict(acc=(255, 209, 77), field=(72, 52, 14), hi=(122, 92, 28), mid=(214, 168, 46)),
    "cache": dict(acc=(255, 140, 120), field=(60, 8, 18), hi=(220, 80, 96), mid=(210, 44, 64)),  # brick crimson (round 2: off FIGHT cyan)
}


def shift(pts, x, y):
    return [(px + x, py + y) for px, py in pts]


# ---------------------------------------------------------------------------------------------------------------------
# sticker stack for a field silhouette: comps(d) -> list of polygons at outward offset d
# ---------------------------------------------------------------------------------------------------------------------
def stack(doc, comps, k, die=18.0, ink=9.0, ring=4.0):
    """white die-cut (with the 1 px grey edge), ink keyline, accent ring, dark field; registers clip 'f0' (the main body)."""
    for d, col in ((die + 1.0, EDGE), (die, WHITE), (ink, INK), (ring, k["acc"]), (0.0, k["field"])):
        for p in comps(d):
            doc.poly(p, col)
    doc.clip("f0", comps(0.0)[0])
    # shading and the two gloss streaks, as the shipped stickers carry
    doc.poly([(0, 0), (130, 0), (130, 62), (0, 62)], (255, 255, 255, 14), clip="f0")
    doc.poly([(84, 0), (98, 0), (36, 130), (22, 130)], (255, 255, 255, 26), clip="f0")
    doc.poly([(100, 0), (106, 0), (48, 130), (42, 130)], (255, 255, 255, 20), clip="f0")


def circ(r):
    return lambda d: [circle_pts(65, 65, r + d, 72)]


def pill(w, h):
    return lambda d: [rrect(65, 65, w + 2 * d, h + 2 * d, h / 2 + d, 12)]


def cog(root, tip, teeth=8, tip_deg=15.0, base_deg=24.0, phase=22.5):
    return lambda d: [gear(65, 65, root + d, tip + d, teeth, tip_deg, base_deg, phase)]


def canbody(w, h, cy, hw, hh, hy):
    return lambda d: [rrect(65, cy, w + 2 * d, h + 2 * d, 10 + d, 8), rrect(65, hy, hw + 2 * d, hh + 2 * d, 8 + d, 8)]


# ---------------------------------------------------------------------------------------------------------------------
# glyph helpers
# ---------------------------------------------------------------------------------------------------------------------
def plus_pts(cx, cy, arm, th):
    a, t = arm, th / 2
    return [(cx - t, cy - a), (cx + t, cy - a), (cx + t, cy - t), (cx + a, cy - t), (cx + a, cy + t), (cx + t, cy + t),
            (cx + t, cy + a), (cx - t, cy + a), (cx - t, cy + t), (cx - a, cy + t), (cx - a, cy - t), (cx - t, cy - t)]


def wrench_parts(length, head_r, handle_w, jaw_w, deg, at):
    """A spanner pointing up in local space, rotated `deg` and moved to `at`. Returns (pieces, jaw polygon, hole polygon)."""
    hh = length / 2
    head_c = (0, -hh + head_r)
    handle = rrect(0, (head_c[1] + hh) / 2 + 2, handle_w, hh * 2 - head_r - 2 + 8, handle_w / 2, 6)
    head = circle_pts(head_c[0], head_c[1], head_r, 40)
    jaw = [(-jaw_w / 2, -hh - 4), (jaw_w / 2, -hh - 4), (jaw_w / 2, head_c[1] + 1), (-jaw_w / 2, head_c[1] + 1)]
    hole = circle_pts(0, hh - handle_w / 2 + 2, handle_w * 0.22, 16)
    f = lambda p: shift(rot(p, deg), at[0], at[1])
    return [f(handle), f(head)], f(jaw), f(hole)


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION A: "Kit" - the family as it is (round die-cut, cream pictogram on a dark tinted field)
# ---------------------------------------------------------------------------------------------------------------------
def a_rest():
    k = KIND["rest"]
    d = Doc(name="A_rest")
    stack(d, circ(43), k)
    moon = crescent(60, 64, 26, 22, 12, -9)
    d.group([moon], CREAM, INK, 2.4, clip="f0")
    # a small star
    star = []
    for i in range(8):
        a = math.radians(-90 + i * 45)
        r = 7.5 if i % 2 == 0 else 2.6
        star.append((88 + r * math.cos(a), 43 + r * math.sin(a)))
    d.group([star], CREAM, INK, 1.8, clip="f0")
    d.group([plus_pts(85, 86, 11, 7.5)], k["acc"], INK, 2.4, clip="f0")
    return d


def a_workshop():
    k = KIND["workshop"]
    d = Doc(name="A_workshop")
    stack(d, circ(43), k)
    cogp = gear(48, 85, 12.5, 17, 8, 14, 22, 0)
    d.group([cogp], k["acc"], INK, 2.2, clip="f0")
    d.poly(circle_pts(48, 85, 5, 18), INK, clip="f0")
    pieces, jaw, hole = wrench_parts(78, 15, 12, 10, 42, (70, 60))
    d.group(pieces, CREAM, INK, 2.4, clip="f0")
    d.poly(jaw, INK, clip="f0")
    d.poly(hole, INK, clip="f0")
    return d


def a_cache():
    k = KIND["cache"]
    d = Doc(name="A_cache")
    stack(d, circ(43), k)
    # an ammo can with its lid thrown back and the stash showing: lid, three cards, the body in front, a latch, two glints
    lid = [(38, 70), (92, 70), (87, 45), (43, 45)]
    d.group([lid], k["mid"], INK, 2.4, clip="f0")
    cards = [rrect(50, 61, 14, 20, 2, 3, -16), rrect(66, 57, 14, 20, 2, 3, 0), rrect(82, 61, 14, 20, 2, 3, 16)]
    d.group(cards, CREAM, INK, 2.2, clip="f0")
    body = rrect(65, 85, 68, 28, 5, 6)
    d.group([body], k["acc"], INK, 2.4, clip="f0")
    d.poly(rrect(65, 80, 68, 6, 2, 3), (255, 255, 255, 70), clip="f0")
    d.poly(rrect(65, 88, 12, 12, 2.5, 4), INK, clip="f0")
    d.poly(rrect(65, 88, 7.5, 7.5, 1.5, 4), CREAM, clip="f0")
    for (x, y, r) in ((36, 52, 5), (95, 48, 4)):
        st = []
        for q in range(8):
            a = math.radians(-90 + q * 45)
            rr = r if q % 2 == 0 else r * 0.36
            st.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.poly(st, CREAM, clip="f0")
    return d


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION B: "Cutout" - the die-cut itself is the object (pod pill, cog, ammo can), same field + pictogram family
# ---------------------------------------------------------------------------------------------------------------------
def b_rest():
    k = KIND["rest"]
    d = Doc(name="B_rest")
    stack(d, pill(90, 38), k)
    # bunk: frame, mattress, blanket, pillow, a crescent
    d.group([rrect(36, 65, 6, 26, 2.5, 4), rrect(94, 71, 6, 14, 2.5, 4), rrect(66, 71, 62, 10, 4, 5)], CREAM, INK, 2.0, clip="f0")
    d.group([rrect(48, 64, 14, 10, 5, 5)], CREAM, INK, 1.8, clip="f0")
    d.group([rrect(77, 65.5, 36, 9.5, 4, 5)], k["acc"], INK, 1.8, clip="f0")
    d.group([crescent(91, 55, 8.5, 7, 3.6, -2.8)], CREAM, INK, 1.6, clip="f0")
    return d


def b_workshop():
    k = KIND["workshop"]
    d = Doc(name="B_workshop")
    stack(d, cog(31, 44, 8, 16, 27, 22.5), k, die=18, ink=9, ring=4)
    # the spinner with one slot picked: ring, six cells, one in the kind colour, hub
    d.circle(65, 65, 25.5, INK, None, 0, clip="f0")
    d.circle(65, 65, 24, CREAM, None, 0, clip="f0")
    for i in range(6):
        a = math.radians(i * 60 - 90)
        d.line([(65 + 8 * math.cos(a), 65 + 8 * math.sin(a)), (65 + 24 * math.cos(a), 65 + 24 * math.sin(a))], INK, 2.6, clip="f0")
    wedge = [(65, 65)] + arc(65, 65, 23, -90, -30, 8)
    d.poly(wedge, k["acc"], clip="f0")
    d.line([(65, 65), (65, 42)], INK, 2.6, clip="f0")
    d.line([(65, 65), (65 + 23 * math.cos(math.radians(-30)), 65 + 23 * math.sin(math.radians(-30)))], INK, 2.6, clip="f0")
    d.circle(65, 65, 8.5, INK, None, 0, clip="f0")
    d.circle(65, 65, 5.5, CREAM, None, 0, clip="f0")
    return d


def b_cache():
    k = KIND["cache"]
    d = Doc(name="B_cache")
    stack(d, canbody(90, 44, 80, 50, 14, 52), k)
    # a brick wall with one brick pushed out, the hollow behind it lit
    bw, bh, gap = 21, 10, 2.6
    x0, ys = 32, (68, 80, 92)
    d.poly(rrect(65, 80, 76, 36, 3, 4), INK, clip="f0")
    rows = []
    for r, y in enumerate(ys):
        off = 0 if r % 2 == 0 else bw / 2 + gap / 2
        for c in range(4):
            x = x0 + off + c * (bw + gap)
            if r == 1 and c == 1:
                continue
            if x + bw > 100 or x < 30 - 0.1:
                if x < 30:
                    pass
                else:
                    continue
            rows.append((x + bw / 2, y))
    # hollow
    hx = x0 + bw / 2 + gap / 2 + 1 * (bw + gap)
    d.poly(rrect(hx + bw / 2, ys[1], bw + 1, bh + 1, 2, 3), k["acc"], clip="f0")
    for (cx, cy) in rows:
        d.poly(rrect(cx, cy, bw, bh, 2.2, 4), CREAM, clip="f0")
    # the loose brick, pulled out toward the viewer
    d.poly(rrect(hx + bw / 2 + 4, ys[1] + 5, bw, bh, 2.2, 4), INK, clip="f0")
    d.group([rrect(hx + bw / 2 + 2, ys[1] + 3, bw, bh, 2.2, 4)], k["mid"], INK, 1.8, clip="f0")
    return d


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION C: "Slap-tag" - no field: the glyph IS the sticker (white contour die-cut round a saturated glyph)
# ---------------------------------------------------------------------------------------------------------------------
LV = ((EDGE, 15.2), (WHITE, 14), (INK, 5.5))


def c_rest():
    k = KIND["rest"]
    d = Doc(name="C_rest")
    roof = [(65, 26), (106, 62), (24, 62)]
    wall = [(35, 60), (95, 60), (95, 102), (35, 102)]
    chim = [(80, 30), (91, 30), (91, 52), (80, 52)]
    d.group([roof, wall, chim], k["mid"], INK, 3.0, extra_levels=LV)
    d.poly(roof, k["acc"])
    d.poly(roof, None, INK, 2.0)
    d.poly(chim, k["acc"])
    # arched door, a lit window, a crescent on the roof
    door = [(55, 102), (55, 82)] + arc(65, 82, 10, 180, 360, 8) + [(75, 82), (75, 102)]
    d.poly(door, INK)
    d.poly([(57.5, 102), (57.5, 82)] + arc(65, 82, 7.5, 180, 360, 8) + [(72.5, 82), (72.5, 102)], CREAM)
    d.poly(rrect(84, 80, 11, 11, 2, 3), CREAM)
    d.poly(rrect(84, 80, 11, 11, 2, 3), None, INK, 1.6)
    d.group([crescent(64, 49, 9.5, 8, 4.2, -3.4)], CREAM, INK, 1.8)
    return d


def c_workshop():
    k = KIND["workshop"]
    d = Doc(name="C_workshop")
    pieces, jaw, hole = wrench_parts(104, 21, 17, 13, 42, (64, 66))
    d.group(pieces, k["acc"], INK, 3.0, extra_levels=LV)
    d.poly(jaw, INK)
    d.poly(hole, INK)
    # a shaded lower flank on the handle for weight
    hl, _, _ = wrench_parts(104, 21, 5, 13, 42, (60, 70))
    d.poly(hl[0], (255, 255, 255, 90))
    return d


def c_cache():
    k = KIND["cache"]
    d = Doc(name="C_cache")
    # a loose-brick stash: two courses of bricks, the top right one pushed half out and tilted, the hole behind it lit
    bot = [rrect(45, 84, 40, 22, 4, 5), rrect(87, 84, 40, 22, 4, 5)]
    top = [rrect(36, 60, 24, 22, 4, 5), rrect(63, 60, 30, 22, 4, 5)]
    out = rrect(97, 54, 34, 22, 4, 5, -12)
    hole = rrect(88, 60, 30, 22, 3, 4)
    d.group(bot + top + [out], k["mid"], INK, 3.0, extra_levels=LV)
    d.poly(hole, k["acc"])
    d.poly(hole, None, INK, 2.0)
    for p in bot + top:
        d.poly(p, k["mid"])
        d.poly(p, None, INK, 2.0)
        d.poly(rrect(sum(q[0] for q in p) / len(p), min(q[1] for q in p) + 5, 22, 4, 2, 3), (255, 255, 255, 60))
    d.poly(out, INK)
    d.poly(rrect(97, 54, 31, 19, 3.5, 5, -12), k["acc"])
    d.poly(rrect(97, 54, 31, 19, 3.5, 5, -12), None, INK, 2.0)
    return d



MAKERS = {
    ("A", "rest"): a_rest, ("A", "workshop"): a_workshop, ("A", "cache"): a_cache,
    ("B", "rest"): b_rest, ("B", "workshop"): b_workshop, ("B", "cache"): b_cache,
    ("C", "rest"): c_rest, ("C", "workshop"): c_workshop, ("C", "cache"): c_cache,
}
KINDS = ("rest", "workshop", "cache")


def make(direction, kind):
    return MAKERS[(direction, kind)]()


def c_cache_small():
    """The legend glyph (16.8 px): the same stack with fewer, fatter pieces: no gloss strokes, wider mortar, a bigger loose brick."""
    k = KIND["cache"]
    d = Doc(name="C_cache_small")
    bot = [rrect(42, 88, 40, 28, 4, 5), rrect(88, 88, 40, 28, 4, 5)]
    top = [rrect(36, 56, 28, 28, 4, 5), rrect(70, 56, 32, 28, 4, 5)]
    out = rrect(100, 48, 34, 28, 4, 5, -14)
    d.group(bot + top + [out], k["mid"], INK, 4.2, extra_levels=((EDGE, 17.0), (WHITE, 15.8), (INK, 6.6)))
    for p in bot + top:
        d.poly(p, k["mid"])
        d.poly(p, None, INK, 3.0)
    d.poly(out, INK)
    d.poly(rrect(100, 48, 30, 24, 3.5, 5, -14), k["acc"])
    d.poly(rrect(100, 48, 30, 24, 3.5, 5, -14), None, INK, 3.0)
    return d
