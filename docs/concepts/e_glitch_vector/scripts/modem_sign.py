"""GLITCH VECTOR CRT - the MODEM / CYBER SHOP vertical sign, redrawn as vector neon (original drawing,
keeping the spirit of the pre-W8c sign: tall rounded frame, stacked pink MODEM, cyan CYBER SHOP,
circuit traces with solder pads).

blender -b --factory-startup --python modem_sign.py -- <out.png>
Black background: the compositor ADDs it over the scene.
"""
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
import gv_font as gf

OUT = sys.argv[sys.argv.index("--") + 1:][0]
W, H = 1920, 1080
gv.reset((W, H), samples=8, black=True)
gv.camera((0, 0, 20), (0, 0, 0), ortho_scale=19.2)
gv.bloom(strength=1.0, threshold=0.5, size=0.65)
rng = random.Random(77)
G = gv.GP("sign", blend="ADD", depth_3d=False)


def px(x, y):
    return ((x - W / 2) / 100.0, (H / 2 - y) / 100.0)


def tube(pl, cname, core=0.018, halo=0.07, flicker=1.0):
    pts = [(x, y, 0) for (x, y) in pl]
    G.line(pts, gv.col(cname), halo, 0.28 * flicker)
    G.line(pts, gv.col(cname), core * 1.8, 0.9 * flicker)
    G.line(pts, gv.col("white"), core * 0.7, 0.85 * flicker)


def rrect(x0, y0, x1, y1, r, n=8):
    pts = []
    for (cx, cy, a0) in [(x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)]:
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts + [pts[0]]


# frame (in px -> world), tall rounded rectangle on the left edge
X0, Y0, X1, Y1 = px(24, 1010) + px(330, 96)
X0, Y0 = px(24, 1010)
X1, Y1 = px(330, 96)
tube(rrect(X0, Y0, X1, Y1, 0.45), "pink", 0.02)
G.line([(x, y, 0) for (x, y) in rrect(X0 + 0.14, Y0 + 0.14, X1 - 0.14, Y1 - 0.14, 0.34)], gv.col("pink"), 0.01, 0.45)

# MODEM stacked vertically, double-line tube letters
cap = 1.05
cx = (X0 + X1) / 2
ytop = Y1 - 0.45
for i, ch in enumerate("MODEM"):
    y = ytop - (i + 1) * 1.28
    w = gf.width(ch, cap)
    for pl in gf.layout(ch, cap, origin=(cx - w / 2, y)):
        pl = [(cx + (x - cx) * 1.55, yy) for (x, yy) in pl]  # wide, squarish sign letters
        tube(pl, "pink", 0.02, 0.09, flicker=0.55 if (i == 3) else 1.0)  # the second E flickers
        # outline echo (the original's hollow tube letters)
        G.line([(x + 0.07, y2 - 0.05, 0) for (x, y2) in pl], gv.col("magenta"), 0.008, 0.5)
# CYBER / SHOP in cyan
for j, word in enumerate(("CYBER", "SHOP")):
    s = 0.46
    w = gf.width(word, s)
    y = ytop - 5 * 1.28 - 0.55 - j * 0.72
    for pl in gf.layout(word, s, origin=(cx - w / 2, y)):
        tube(pl, "cyan", 0.014, 0.06)

# circuit traces with solder pads, 45-degree routing, on both inner edges
for side in (-1, 1):
    xs = X0 + 0.3 if side < 0 else X1 - 0.3
    y = Y1 - 0.8
    while y > Y0 + 3.1:
        L = rng.uniform(0.25, 0.6)
        pts = [(xs, y), (xs + side * -0.0, y - L), (xs - side * 0.18, y - L - 0.18)]
        pts = [(x, yy, 0) for (x, yy) in pts]
        G.line(pts, gv.col("pink"), 0.008, 0.6)
        ex, ey, _ = pts[-1]
        ring = [(ex + 0.05 * math.cos(a / 10 * 6.283), ey + 0.05 * math.sin(a / 10 * 6.283), 0) for a in range(11)]
        G.line(ring, gv.col("pink"), 0.008, 0.8)
        y -= L + rng.uniform(0.35, 0.8)

G.flush("sign")
gv.render(OUT)
print("SIGN DONE")
