"""GLITCH VECTOR CRT - combat layer: two holographic stacked-ring spinners + a binary-shard hit.

blender -b --factory-startup --python spinners.py -- <out.png> <fonts_dir>
Transparent film; writes <out>.json with screen positions for the Pillow compositor.
Depth techniques shown (DIRECTION.md): parallax-offset ring layers at different heights under a
tilted camera, translucent additive slice fill, glyphs floating above the fill, projected base
glow + projector beams, needle with a drop shadow on the base plate, phosphor trail on the needle.
"""
import bpy, sys, os, math, random, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
import gv_font as gf

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
FONTS = argv[1]
rng = random.Random(4242)

sc = gv.reset((1920, 1080), samples=8, black=True)
TILT = 24.0
cam = gv.camera((0, 0, 0), (TILT, 0, 0), ortho_scale=19.2)
bpy.context.view_layer.update()
V = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
cam.location = Vector((0, 0, 0)) - V * 40
bpy.context.view_layer.update()
gv.bloom(strength=0.7, threshold=0.75, size=0.5)
mono = gv.load_font(os.path.join(FONTS, "ShareTechMono-Regular.ttf"))

G = gv.GP("wheels", blend="ADD")
G_top = gv.GP("wheels_top", blend="ADD")
TAU = 2 * math.pi


def circle(c, r, z, n=96, a0=0.0, a1=TAU):
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n), z) for i in range(n + 1)]


def tick_angle(t):
    """tick 0 at 12 o'clock, clockwise."""
    return math.pi / 2 - TAU * t / 30.0


SLICE_COL = {"ATK": "pink", "DEF": "cyan", "EVD": "gain", "AFF": "violet", "CRIT": "pink", "MISS": "#6A6A6A"}


def glyph(kind, c, s, z):
    """Vector slice glyphs (original): sword, shield, chevrons, drop, burst, dash."""
    x, y = c
    out = []
    if kind == "ATK":
        out = [[(x - s * 0.6, y - s * 0.6, z), (x + s * 0.55, y + s * 0.55, z)],
               [(x - s * 0.55, y - s * 0.15, z), (x - s * 0.15, y - s * 0.55, z)],
               [(x + s * 0.55, y + s * 0.55, z), (x + s * 0.3, y + s * 0.62, z), (x + s * 0.62, y + s * 0.3, z), (x + s * 0.55, y + s * 0.55, z)]]
    elif kind == "DEF":
        out = [[(x - s * 0.5, y + s * 0.5, z), (x + s * 0.5, y + s * 0.5, z), (x + s * 0.45, y - s * 0.1, z), (x, y - s * 0.6, z),
                (x - s * 0.45, y - s * 0.1, z), (x - s * 0.5, y + s * 0.5, z)], [(x, y + s * 0.5, z), (x, y - s * 0.45, z)]]
    elif kind == "EVD":
        out = [[(x - s * 0.55, y + s * 0.45, z), (x - s * 0.1, y, z), (x - s * 0.55, y - s * 0.45, z)],
               [(x + s * 0.0, y + s * 0.45, z), (x + s * 0.45, y, z), (x + s * 0.0, y - s * 0.45, z)]]
    elif kind == "AFF":
        out = [[(x, y + s * 0.65, z)] + [(x + s * 0.4 * math.cos(a), y - s * 0.15 + s * 0.4 * math.sin(a), z)
                                          for a in [math.radians(d) for d in range(30, -211, -20)]] + [(x, y + s * 0.65, z)]]
    elif kind == "CRIT":
        pts = []
        for k in range(17):
            a = TAU * k / 16
            r = s * (0.7 if k % 2 == 0 else 0.25)
            pts.append((x + r * math.cos(a), y + r * math.sin(a), z))
        out = [pts]
    else:
        out = [[(x - s * 0.5, y, z), (x + s * 0.5, y, z)]]
    return out


def spinner(name, C, R, slices, owner_col, bezel_col, hostile, needle_tick, hub_label, hp, hp_max, pos_json):
    cx, cy = C
    Z_BASE, Z_BEZEL, Z_FILL, Z_GLYPH, Z_GLASS, Z_NEEDLE = -0.9, 0.0, 0.35, 0.75, 1.15, 1.45
    ocol = gv.col(owner_col)
    bcol = gv.col(bezel_col)
    # ---- 1. projected base glow + projector emitter rings (the hologram's source)
    gv.disc(name + "_glow", R * 1.55, gv.radial_glow_mat(name + "_gm", ocol, 0.55, 1.8), loc=(cx, cy, Z_BASE))
    for k, rr in enumerate((0.35, 0.55, R * 0.98, R * 1.12)):
        G.line(circle(C, rr, Z_BASE, 64), ocol, 0.012, 0.55 if k < 2 else 0.22)
    # projector beams from the emitter ring up to the bezel (light cone)
    for k in range(12):
        a = TAU * k / 12 + 0.13
        G.line([(cx + 0.55 * math.cos(a), cy + 0.55 * math.sin(a), Z_BASE), (cx + R * 1.02 * math.cos(a), cy + R * 1.02 * math.sin(a), Z_BEZEL)],
               ocol, 0.006, opac=[0.5, 0.05])
    # ---- 2. bezel (outermost layer) with 30 ticks
    G.line(circle(C, R * 1.08, Z_BEZEL, 120), bcol, 0.03)
    G.line(circle(C, R * 1.0, Z_BEZEL, 120), bcol, 0.014, 0.8)
    if hostile:
        # notched hostile edge: sawtooth outside the bezel
        pts = []
        for k in range(60):
            a = TAU * k / 60
            r = R * (1.13 if k % 2 == 0 else 1.18)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), Z_BEZEL))
        G.line(pts + [pts[0]], bcol, 0.014, 0.85)
        # corp pattern: 45 deg container stripes on the bezel band (Meridian)
        for k in range(0, 120, 3):
            a = TAU * k / 120
            G.line([(cx + R * 1.005 * math.cos(a), cy + R * 1.005 * math.sin(a), Z_BEZEL),
                    (cx + R * 1.075 * math.cos(a + 0.03), cy + R * 1.075 * math.sin(a + 0.03), Z_BEZEL)], bcol, 0.008, 0.6)
    else:
        # operative: riveted plates (Breaker)
        for k in range(10):
            a = TAU * k / 10 + 0.1
            G.line(circle((cx + R * 1.04 * math.cos(a), cy + R * 1.04 * math.sin(a)), 0.035, Z_BEZEL, 8), bcol, 0.012)
    for t in range(30):
        a = tick_angle(t)
        L = 0.16 if t % 5 == 0 else 0.08
        G.line([(cx + R * 0.94 * math.cos(a), cy + R * 0.94 * math.sin(a), Z_BEZEL + 0.02),
                (cx + (R * 0.94 - L) * math.cos(a), cy + (R * 0.94 - L) * math.sin(a), Z_BEZEL + 0.02)],
               gv.col("white"), 0.011 if t % 5 == 0 else 0.007, 0.9 if t % 5 == 0 else 0.5)
    # ---- 3. translucent slice fill (mesh, additive) + bright rims (GP)
    t0 = 0
    r_in, r_out = R * 0.42, R * 0.9
    for (kind, n, val) in slices:
        cn = SLICE_COL[kind]
        a0, a1 = tick_angle(t0), tick_angle(t0 + n)
        o = gv.annulus_sector(name + "_s%d" % t0, r_in, r_out, a1, a0,
                              gv.emit_mat(name + "_sm%d" % t0, gv.col(cn), 1.0, 0.12 if kind != "MISS" else 0.05), z=Z_FILL, seg=max(4, n * 4))
        o.location = (cx, cy, 0)
        # outer rim arc (bright) + inner rim (dim) + dividers
        G.line(circle(C, r_out, Z_FILL, max(4, n * 4), a1, a0), gv.col(cn), 0.03)
        G.line(circle(C, r_in, Z_FILL, max(4, n * 4), a1, a0), gv.col(cn), 0.012, 0.6)
        G.line([(cx + r_in * math.cos(a0), cy + r_in * math.sin(a0), Z_FILL), (cx + r_out * math.cos(a0), cy + r_out * math.sin(a0), Z_FILL)],
               gv.col("white"), 0.01, 0.55)
        # ---- 4. glyph + value floating above the fill (their own depth layer)
        am = (a0 + a1) / 2
        gc = (cx + (r_in + r_out) / 2 * math.cos(am), cy + (r_in + r_out) / 2 * math.sin(am))
        for pl in glyph(kind, gc, 0.34, Z_GLYPH):
            G_top.line(pl, gv.col("white"), 0.022)
            # the glyph's "shadow" on the fill layer, offset by the projection
            G.line([(p[0], p[1], Z_FILL + 0.01) for p in pl], gv.col(cn), 0.02, 0.35)
        if val:
            vx, vy = cx + R * 1.24 * math.cos(am), cy + R * 1.24 * math.sin(am)
            w = gf.width(str(val), 0.3)
            for pl in gf.layout(str(val), 0.3, origin=(vx - w / 2, vy - 0.15)):
                G_top.line([(p[0], p[1], Z_BEZEL) for p in pl], gv.col(cn), 0.02)
        t0 += n
    # ---- 5. glass top layer: thin outer ring, hub ring, specular arc
    G_top.line(circle(C, R * 0.92, Z_GLASS, 120), gv.col("white"), 0.008, 0.35)
    G_top.line(circle(C, R * 0.4, Z_GLASS, 64), ocol, 0.022)
    G_top.line(circle(C, R * 0.36, Z_GLASS, 64), ocol, 0.008, 0.6)
    G_top.line(circle(C, R * 0.86, Z_GLASS, 30, math.radians(100), math.radians(150)), gv.col("white"), 0.02, 0.55)
    G_top.line(circle(C, R * 0.80, Z_GLASS, 20, math.radians(108), math.radians(135)), gv.col("white"), 0.012, 0.35)
    gv.disc(name + "_hub", R * 0.4, gv.emit_mat(name + "_hubm", gv.col("void"), 1.0, 1.0, additive=False), loc=(cx, cy, Z_GLASS - 0.05))
    # hub label in vector type
    w = gf.width(hub_label, 0.14)
    for pl in gf.layout(hub_label, 0.14, origin=(cx - w / 2, cy - 0.3)):
        G_top.line([(p[0], p[1], Z_GLASS) for p in pl], gv.col("white"), 0.012, 0.9)
    # ---- 6. needle + counterweight + phosphor trail + drop shadow on the base plate
    a = tick_angle(needle_tick)
    tip = (cx + R * 0.97 * math.cos(a), cy + R * 0.97 * math.sin(a))
    tail = (cx - R * 0.3 * math.cos(a), cy - R * 0.3 * math.sin(a))
    G_top.line([(tail[0], tail[1], Z_NEEDLE), (tip[0], tip[1], Z_NEEDLE)], gv.col("acid"), 0.035)
    G_top.line(circle(tail, 0.12, Z_NEEDLE, 16), gv.col("acid"), 0.02)
    G.line([(tail[0], tail[1], Z_BASE), (tip[0], tip[1], Z_BASE)], gv.col("acid"), 0.05, 0.12)  # shadow on the base
    for k in range(1, 14):
        ak = a + k * 0.028
        G_top.line([(cx + R * 0.3 * math.cos(ak), cy + R * 0.3 * math.sin(ak), Z_NEEDLE - 0.02),
                    (cx + R * 0.95 * math.cos(ak), cy + R * 0.95 * math.sin(ak), Z_NEEDLE - 0.02)], gv.col("acid"), 0.012, 0.35 * (1 - k / 14) ** 2)
    # ---- 7. HP arc: segmented, under the wheel on the bezel plane
    frac = hp / hp_max
    hpcol = "gain" if frac >= 0.5 else ("amber" if frac >= 0.25 else "harm")
    segs = 20
    for k in range(segs):
        a0 = math.radians(-135 + k * (90 / segs)); a1 = a0 + math.radians(90 / segs * 0.8)
        on = k < round(frac * segs)
        G.line(circle(C, R * 1.47, Z_BEZEL, 6, a0, a1), gv.col(hpcol if on else "#1F3A30"), 0.07, 1.0 if on else 0.6)
    pos_json[name] = {"center": proj((cx, cy, Z_BEZEL)), "top": proj((cx, cy + R * 1.2, Z_BEZEL)),
                      "bottom": proj((cx, cy - R * 1.55, Z_BEZEL)), "radius_px": R * 100, "hp_label": proj((cx, cy - R * 1.62, Z_BEZEL)),
                      "hub": proj((cx, cy, Z_GLASS)), "hub_top": proj((cx, cy + R * 0.28, Z_GLASS))}


def proj(p):
    v = world_to_camera_view(sc, cam, Vector(p))
    return [round(v.x * 1920, 1), round((1 - v.y) * 1080, 1)]


pos = {}
# the camera looks down the tilted axis; wheel centres sit in the upper-middle band
OP = (-3.7, 0.9)
EN = (3.5, 1.2)
spinner("op", OP, 2.25, [("ATK", 6, 6), ("DEF", 5, 4), ("CRIT", 2, 12), ("EVD", 4, 2), ("ATK", 6, 6), ("DEF", 7, 4)],
        "pink", "pink", False, 3, "BREAKER", 60, 60, pos)
spinner("en", EN, 2.25, [("AFF", 5, 14), ("ATK", 7, 8), ("DEF", 6, 6), ("MISS", 3, 0), ("ATK", 5, 8), ("DEF", 4, 6)],
        "orange", "orange", True, 17, "COLLECTIONS", 27, 40, pos)

# ---- enemy hologram bust above the enemy wheel (vector wireframe head on a tripod of light)
hx, hy, hz = EN[0] + 2.9, EN[1] + 2.6, 0.2
for k in range(7):
    lat = -1.2 + k * 0.4
    r = 0.55 * math.cos(lat * 0.9)
    G_top.line([(hx + r * math.cos(a / 24 * TAU), hy + 0.55 * math.sin(lat * 0.9) * 1.1 + 0.0, hz + r * 0.35 * math.sin(a / 24 * TAU)) for a in range(25)],
               gv.col("orange"), 0.01, 0.7)
for k in range(6):
    ph = k / 6 * math.pi
    G_top.line([(hx + 0.55 * math.sin(t / 24 * TAU) * math.cos(ph), hy + 0.6 * math.cos(t / 24 * TAU), hz + 0.55 * math.sin(t / 24 * TAU) * math.sin(ph))
                for t in range(25)], gv.col("orange"), 0.007, 0.45)
G_top.line([(hx - 0.45, hy + 0.05, hz + 0.3), (hx + 0.45, hy + 0.05, hz + 0.3)], gv.col("harm"), 0.05)
G_top.line([(hx - 0.7, hy - 0.9, hz), (hx, hy - 0.62, hz), (hx + 0.7, hy - 0.9, hz)], gv.col("orange"), 0.014, 0.8)

# ---- the hit: binary shards thrown off the enemy wheel at the attack point
hit_a = tick_angle(24)  # upper-left of the enemy wheel, facing the operative
HIT = Vector((EN[0] + 2.1 * math.cos(hit_a), EN[1] + 2.1 * math.sin(hit_a), 0.6))
gv.disc("hitflash", 0.75, gv.radial_glow_mat("hitm", gv.col("white"), 1.6, 2.6), loc=tuple(HIT))
gv.disc("hitflash2", 1.6, gv.radial_glow_mat("hitm2", gv.col("pink"), 0.7, 2.0), loc=tuple(HIT))
# slash streak (attack hit shape)
G_top.line([tuple(HIT + Vector((-0.9, 0.7, 0.5))), tuple(HIT + Vector((0.8, -0.6, 0.5)))], gv.col("white"), 0.04,
           radii=[0.005, 0.05], opac=[0.2, 1.0])
shard_mats = {c: gv.emit_mat("shard_" + c, gv.col(c), 3.0, 1.0, additive=False) for c in ("white", "pink", "cyan")}
for k in range(46):
    ang = rng.gauss(math.radians(150), 0.55)          # thrown up-left, away from the wheel centre
    spd = rng.uniform(0.4, 2.8)
    d = Vector((math.cos(ang), math.sin(ang), rng.uniform(0.0, 0.7)))
    p = HIT + d * spd
    size = rng.uniform(0.2, 0.5) * (1.25 - spd / 4.5)
    cname = "white" if spd < 1.4 else rng.choice(("pink", "pink", "cyan", "white"))
    ch = rng.choice("01")
    t = gv.text(ch, shard_mats[cname], tuple(p), size=size, rot=(math.radians(TILT), 0, rng.uniform(-0.6, 0.6)), font=mono)
    # phosphor persistence trail back toward the hit
    trail = [tuple(p - d.normalized() * spd * 0.55 * q / 6) for q in range(7)][::-1]
    G_top.line(trail, gv.col(cname), 0.012, opac=[(q + 1) / 7 * 0.6 for q in range(7)])
pos["hit"] = proj(tuple(HIT))

for g in (G, G_top):
    g.flush()
gv.render(OUT)
with open(os.path.splitext(OUT)[0] + ".json", "w") as f:
    json.dump(pos, f, indent=1)
print("SPINNERS DONE", json.dumps(pos))
