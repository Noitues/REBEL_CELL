"""Meridian v3: the flat orthographic PLAN of the Gatehouse Gantry (north up) -> ../plan.png
Reads the same numbers as the 3D build (hq_preset compound, hq_graph rooms + illustrative links). Pure PIL.

python plan.py
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_graph as G  # noqa: E402
import hq_preset as HP  # noqa: E402
import meridian_rail as MR  # noqa: E402

CP = HP.PRESET["hq"]["compound"]
L, WT = CP["lot"], CP["wall"]["t"]
GC = CP["gantry"]
S = 2.2                                    # px per BU
X0, Y1 = -262.0, 190.0                    # world window: x from X0, y down from Y1
MAPW, MAPH = int(524 * S), int(440 * S)
PANEL = 560
W, H = MAPW + PANEL, MAPH + 90
im = Image.new("RGB", (W, H), (14, 15, 19))
d = ImageDraw.Draw(im, "RGBA")


def font(sz, bold=False):
    for f in (("consolab.ttf" if bold else "consola.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            continue
    return ImageFont.load_default()


F1, F2, F3, F4 = font(30, True), font(17, True), font(15), font(13)
OY = 70


def P(x, y):
    return ((x - X0) * S, OY + (Y1 - y) * S)


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1):
    a, b = P(min(x0, x1), max(y0, y1)), P(max(x0, x1), min(y0, y1))
    d.rectangle([a, b], fill=fill, outline=outline, width=width)


def label(x, y, text, f=F4, col=(235, 235, 235), anchor="mm", bg=True):
    p = P(x, y)
    if bg:
        bb = d.textbbox(p, text, font=f, anchor=anchor)
        d.rectangle([bb[0] - 4, bb[1] - 2, bb[2] + 4, bb[3] + 2], fill=(10, 10, 14, 215))
    d.text(p, text, font=f, fill=col, anchor=anchor)


def arrow(x0, y0, x1, y1, col, w=3, head=10):
    a, b = P(x0, y0), P(x1, y1)
    d.line([a, b], fill=col, width=w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-1, 1):
        d.line([b, (b[0] - head * math.cos(ang + s * 0.45), b[1] - head * math.sin(ang + s * 0.45))], fill=col, width=w)


def dashed(pts, col, w=2, on=8, off=6):
    for (a, b) in zip(pts, pts[1:]):
        pa, pb = P(*a), P(*b)
        Lp = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        n = int(Lp / (on + off)) + 1
        for k in range(n):
            t0, t1 = k * (on + off) / max(Lp, 1), min(1.0, (k * (on + off) + on) / max(Lp, 1))
            if t0 >= 1:
                break
            d.line([(pa[0] + (pb[0] - pa[0]) * t0, pa[1] + (pb[1] - pa[1]) * t0),
                    (pa[0] + (pb[0] - pa[0]) * t1, pa[1] + (pb[1] - pa[1]) * t1)], fill=col, width=w)


CL = MR.centreline(CP)


def MR_near(x, y, dmax):
    for a, b in zip(CL, CL[1:]):
        vx, vy = b[0] - a[0], b[1] - a[1]
        L2 = vx * vx + vy * vy or 1.0
        t = max(0.0, min(1.0, ((x - a[0]) * vx + (y - a[1]) * vy) / L2))
        yield math.hypot(x - a[0] - vx * t, y - a[1] - vy * t) < dmax


# ------------------------------------------------------------ the city right up to the lot (one street between)

r = random.Random(5401)
spans = [(161 + 30 * k, 183 + 30 * k) for k in range(3)]
spans += [(-b, -a) for (a, b) in spans] + [(-120 + 30 * k, -98 + 30 * k) for k in range(8)]
for (xa, xb) in spans:
    for (ya, yb) in spans:
        cx, cy = (xa + xb) / 2, (ya + yb) / 2
        if abs(cx) < 160 and abs(cy) < 160:
            continue
        if any(MR_near(cx, cy, 16.0)):
            continue
        low = any(MR_near(cx, cy, 40.0))
        g = 34 if low else 44 + r.randrange(14)
        rect(xa, ya, xb, yb, fill=(g, g + 2, g + 8))
# the lot
rect(-L, -L, L, L, fill=(40, 40, 42))
dashed([(-L, -L), (L, -L), (L, L), (-L, L), (-L, -L)], (140, 140, 150), 1, 5, 5)
# the truck RING ROAD (round 2) and its highway exits
RGD = CP["ring"]
r0_, r1_ = RGD["r"]
for (x0_, y0_, x1_, y1_) in ((-r1_, -r1_, r1_, -r0_), (-r1_, r0_, r1_, r1_), (-r1_, -r0_, -r0_, r0_), (r0_, -r0_, r1_, r0_)):
    rect(x0_, y0_, x1_, y1_, fill=(22, 22, 26))
for li in range(1, RGD["lanes"]):
    d_ = r0_ + li * (r1_ - r0_) / RGD["lanes"]
    colr_ = (200, 140, 60) if li == RGD["lanes"] // 2 else (90, 90, 96)
    dashed([(-d_, -d_), (d_, -d_), (d_, d_), (-d_, d_), (-d_, -d_)], colr_, 1, 5, 4) if li != RGD["lanes"] // 2 else \
        d.line([P(-d_, -d_), P(d_, -d_), P(d_, d_), P(-d_, d_), P(-d_, -d_)], fill=colr_, width=2)
for nm_, pts_ in MR.highways(CP).items():
    a_, b_ = pts_[0], pts_[2]
    d.line([P(a_[0], a_[1]), P(b_[0], b_[1])], fill=(70, 70, 82), width=int(RGD["deck_w"] * S))
for e_ in MR.exits(CP):
    x_, y_, _ = e_["p"]
    a_ = math.radians(e_["heading"])
    arrow(x_, y_, x_ + math.sin(a_) * 60, y_ + math.cos(a_) * 60, (120, 255, 200), 4, 12)
    cx_, cy_ = 18.0 + x_ * 0.2375, 222.0 + y_ * 0.2375
    label(x_ + math.sin(a_) * 34 + (0 if e_["name"] == "S" else 0), y_ + math.cos(a_) * 34 + (8 if e_["name"] != "S" else 0),
          "EXIT %s  hdg %d  city (%.1f, %.1f)" % (e_["name"], e_["heading"], cx_, cy_), F4, (120, 255, 200))
label(0, -r0_ - 3, "TRUCK RING ROAD: 6 lanes, queues at each gate", F4, (200, 200, 205))
# ------------------------------------------------------------ the rail (N edge), the quay, the train
half = (CP["rail"]["y"][1] - CP["rail"]["y"][0]) / 2
for a, b in zip(CL, CL[1:]):
    dx, dy = b[0] - a[0], b[1] - a[1]
    hz = math.hypot(dx, dy) or 1.0
    sx_, sy_ = -dy / hz, dx / hz
    elev = max(a[2], b[2]) > 1.5
    wpx = (CP["rail"]["deck_w"] if elev else 2 * half + 8.4) * S
    d.line([P(a[0], a[1]), P(b[0], b[1])], fill=(60, 66, 84) if elev else (26, 30, 40), width=int(wpx))
    for sg in (-1, 1):
        d.line([P(a[0] + sx_ * sg * half, a[1] + sy_ * sg * half), P(b[0] + sx_ * sg * half, b[1] + sy_ * sg * half)],
               fill=(120, 170, 220), width=2)
label(-130, 160, "VIADUCT TO THE PORT (city polyline; deck 73.7 kit = 17.5 city BU)", F4, (150, 205, 255))
q0_, q1_ = CP["quay"]
rect(-L + WT, q0_, L - WT, q1_, fill=(70, 70, 74))
tx0, tx1 = CP["rail"]["train_x"]
ty = CP["rail"]["y"][0]
rect(tx0, ty - 3.4, tx1, ty + 3.4, fill=(200, 215, 230), outline=(140, 200, 255), width=2)
d.polygon([P(tx1, ty - 3.4), P(tx1 + 19.6, ty), P(tx1, ty + 3.4)], fill=(200, 215, 230))
d.polygon([P(tx0, ty - 3.4), P(tx0 - 19.6, ty), P(tx0, ty + 3.4)], fill=(200, 215, 230))
x = tx0 + 24.8
while x < tx1 - 34:
    d.line([P(x, ty - 3.4), P(x, ty + 3.4)], fill=(60, 80, 110), width=2)
    x += 22.8
arrow(tx1 + 24, ty, tx1 + 50, ty, (140, 200, 255))
label(0, L + 22, "HIGH-SPEED FREIGHT LINE (the 4th side): lit carriages, a nose at each end", F3, (150, 205, 255))
label(60, (q0_ + q1_) / 2, "THE QUAY", F4, (210, 210, 210))
# ------------------------------------------------------------ walls, towers, gates
WALLC, TOWC = (128, 62, 34), (78, 72, 70)
GHW, GTX = CP["gate"]["half"], CP["gate"]["tower"][0]
gg = GHW + 2 * GTX
gy = CP["gate"]["ew_y"]
for sx in (-1, 1):
    xo, xi = sx * L, sx * (L - WT)
    RG = CP["railgate"]
    for (ya, yb) in ((-L + 2 * CP["corner"]["half"], gy - gg), (gy + gg, RG["y0"])):
        rect(xo, ya, xi, yb, fill=WALLC)
        yy = ya
        while yy < yb:
            d.line([P(xo, yy), P(xi, yy)], fill=(80, 36, 18), width=1)
            yy += 6.6
    # the rail gate: the arched bridge (dashed: open below) + two drum turrets
    rect(xo, RG["y0"], xi, L, outline=TOWC, width=3)
    for ya_ in RG["arch"]:
        dashed([(xo, ya_), (xi, ya_)], (140, 200, 255), 2, 4, 3)
    rr_ = RG["drum_r"]
    for tyy in (RG["y0"] - rr_ + 1.0, L - rr_):
        c = P(sx * (L - WT - rr_ + 0.5), tyy)
        d.ellipse([c[0] - rr_ * S, c[1] - rr_ * S, c[0] + rr_ * S, c[1] + rr_ * S], fill=TOWC)
    label(sx * (L - WT / 2), L + 6, "RAIL GATE (arch)", F4, (150, 205, 255))
    # the S corner tower (inside the lot corner)
    CH_ = CP["corner"]["half"]
    rect(sx * (L - 2 * CH_), -L, sx * L, -L + 2 * CH_, fill=TOWC)
    # the E / W gatehouse
    for s in (-1, 1):
        rect(xo, gy + s * (GHW + GTX) - GTX, sx * (L - WT - 6), gy + s * (GHW + GTX) + GTX, fill=TOWC)
    rect(xo, gy - GHW, xi, gy + GHW, fill=(30, 30, 34))
    arrow(sx * (L + 40), gy, sx * (L - WT - 8), gy, (255, 210, 40), 3)
    label(sx * (L + 30), gy + 14, "TRUCK GATE " + ("W" if sx < 0 else "E"), F4, (255, 215, 60))
rect(-L + 2 * CP["corner"]["half"], -L, -gg, -L + WT, fill=WALLC)
rect(gg, -L, L - 2 * CP["corner"]["half"], -L + WT, fill=WALLC)
xx = -L + WT
while xx < L - WT:
    if abs(xx) > gg:
        d.line([P(xx, -L), P(xx, -L + WT)], fill=(80, 36, 18), width=1)
    xx += 6.6
for s in (-1, 1):
    rect(s * (GHW + GTX) - GTX, -L, s * (GHW + GTX) + GTX, -L + WT + 6, fill=TOWC)
rect(-GHW, -L, GHW, -L + WT + 2, fill=(30, 30, 34))
arrow(0, -L - 42, 0, -L + WT + 8, (255, 210, 40), 3)
label(0, -L - 48, "TRUCK GATE S", F4, (255, 215, 60))
# ------------------------------------------------------------ truck lanes + trucks (the drop / pick-up bays)
LN = CP["lane"]


def truck(x, y, along_x):
    if along_x:
        rect(x - 9, y - 2.9, x + 9.6, y + 2.9, fill=(255, 205, 40), outline=(30, 30, 30))
    else:
        rect(x - 2.9, y - 9, x + 2.9, y + 9.6, fill=(255, 205, 40), outline=(30, 30, 30))


rect(-L + WT, LN["s_y"] - 7, L - WT, LN["s_y"] + 7, fill=(28, 28, 30))
for xx in (-82.0, -58.0, -34.0, 34.0, 58.0, 82.0):
    truck(xx, LN["s_y"], True)
for sx in (-1, 1):
    rect(sx * LN["ew_x"] - 7, -L + WT, sx * LN["ew_x"] + 7, LN["n_end"], fill=(28, 28, 30))
    for yy in (-78.0, -62.0, 4.0, 26.0, 48.0):
        truck(sx * LN["ew_x"], yy, False)
label(-60, LN["s_y"] + 11, "TRUCK BAYS S", F4, (255, 215, 60))
label(-LN["ew_x"], -94, "BAYS W", F4, (255, 215, 60))
label(LN["ew_x"], -94, "BAYS E", F4, (255, 215, 60))
# the yard stacks (the bailey)
x0_, x1_, y0_, y1_ = CP["yard"]
ry = random.Random(5411)
xx = x0_
while xx < x1_ - 14:
    yy = y0_
    while yy < y1_ - 6:
        g = 70 + ry.randrange(40)
        rect(xx, yy, xx + 14, yy + 6.2, fill=(g, int(g * 0.62), int(g * 0.45)))
        yy += 7.0
        if int(round((yy - y0_) / 7.0)) % 5 == 0:
            yy += 6.0
    xx += 14.6 if (xx - x0_) % 44 < 30 else 22.0
label(0, -40, "THE BAILEY: container stacks", F3, (230, 200, 170))
# ------------------------------------------------------------ the gantry: runways, reach, legs, span, keep
GY = GC["y"]
LEGX = L - WT / 2
OR = (214, 96, 40)                         # the rust-orange paint
# crane reach: gantry travel (N-S, on the runways) x trolley travel (E-W, along the span)
LHX_, LHY_ = GC["leg"]
reach_y0, reach_y1 = -L + WT + LHY_ + 5, L - LHY_ - 5
d.rectangle([P(-LEGX + LHX_, reach_y1), P(LEGX - LHX_, reach_y0)], fill=(255, 140, 26, 34))
for k in range(-30, 40):
    a = P(-LEGX + LHX_ + k * 8, reach_y0)
    b = (a[0] + (reach_y1 - reach_y0) * S * 0.6, a[1] - (reach_y1 - reach_y0) * S)
    d.line([a, b], fill=(255, 140, 26, 40), width=1)
rect(-LEGX + LHX_, reach_y0, LEGX - LHX_, reach_y1, outline=(255, 140, 26, 160), width=2)
for sx in (-1, 1):
    dashed([(sx * LEGX - 4, -L + WT), (sx * LEGX - 4, L)], OR, 2, 10, 6)
    dashed([(sx * LEGX + 4, -L + WT), (sx * LEGX + 4, L)], OR, 2, 10, 6)
    rect(sx * LEGX - LHX_, GY - LHY_, sx * LEGX + LHX_, GY + LHY_, fill=OR, outline=(255, 220, 160), width=2)
    for (px, py) in ((sx * LEGX - LHX_, GY - 12), (sx * LEGX + LHX_, GY - 12), (sx * LEGX - LHX_, GY + 12), (sx * LEGX + LHX_, GY + 12)):
        c = P(px, py)
        d.ellipse([c[0] - 3.2 * S, c[1] - 3.2 * S, c[0] + 3.2 * S, c[1] + 3.2 * S], fill=(230, 120, 20))
rect(-LEGX + LHX_, GY - 7, LEGX - LHX_, GY + 7, fill=(170, 64, 26), outline=(255, 214, 150), width=2)
GN = L - LHY_ - 5                          # the gantry at its N stop: the span over the train
dashed([(-LEGX, GN - 7), (LEGX, GN - 7), (LEGX, GN + 7), (-LEGX, GN + 7), (-LEGX, GN - 7)], (255, 214, 150), 2, 6, 5)
label(40, (q0_ + q1_) / 2 - 6, "N STOP (dashed): the span over the train", F4, (255, 214, 150))
KX = GC["keep_x"]
rect(KX - GC["keep"][0], GY - GC["keep"][1], KX + GC["keep"][0], GY + GC["keep"][1], fill=(200, 185, 160), outline=(255, 240, 210), width=2)
# the server (in the keep's crown)
c = P(KX, GY)
d.ellipse([c[0] - 22, c[1] - 22, c[0] + 22, c[1] + 22], outline=(255, 40, 30), width=5)
d.ellipse([c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8], fill=(255, 60, 40))
label(KX + 20, GY - 20, "THE KEEP (the trolley, parked)  >  THE MASTER MANIFEST", F3, (255, 120, 100))
arrow(KX + 18, GY, KX + 50, GY, (255, 240, 210), 3)
arrow(KX - 18, GY, KX - 50, GY, (255, 240, 210), 3)
label(60, GY - 12, "SPAN (the battlemented bridge)", F4, (255, 200, 140))
for sx in (-1, 1):
    arrow(sx * LEGX, GY + 18, sx * LEGX, GY + 40, OR, 3)
    arrow(sx * LEGX, GY - 18, sx * LEGX, GY - 40, OR, 3)
label(-LEGX, GY + 52, "LEG", F4, OR)
label(LEGX, GY + 52, "LEG", F4, OR)
label(-LEGX - 2, -78, "RUNWAY", F4, OR)
label(LEGX + 2, -78, "RUNWAY", F4, OR)
label(0, reach_y0 + 18, "CRANE REACH: train, quay, bailey, all three bay lanes, the wall tops", F4, (255, 170, 80))
# ------------------------------------------------------------ the illustrative route (slots; topology = game graph)
RC = (210, 255, 0)
for (a, b) in G.EDGES:
    pa = G.ROOM[a]["o"]
    pb = G.ROOM[b]["o"]
    dashed([(pa[0], pa[1]), (pb[0], pb[1])], (210, 255, 0, 170), 2, 6, 5)
num = {}
for k, i in enumerate([n for n in G.NODES]):
    o = G.ROOM[i]["o"]
    num[i] = k
    c = P(o[0], o[1])
    rad = 11
    col = (255, 60, 40) if i == "srv" else ((255, 255, 255) if i == "start" else RC)
    d.ellipse([c[0] - rad, c[1] - rad, c[0] + rad, c[1] + rad], fill=(12, 12, 14), outline=col, width=3)
    d.text(c, "S" if i == "start" else ("T" if i == "srv" else str(k)), font=F4, fill=col, anchor="mm")
# ------------------------------------------------------------ title, compass, scale
d.text((16, 14), "MERIDIAN HQ v3  //  THE GATEHOUSE GANTRY  //  plan (north up)", font=F1, fill=OR)
c = P(230, 170)
d.polygon([(c[0], c[1] - 26), (c[0] - 10, c[1] + 6), (c[0] + 10, c[1] + 6)], fill=(230, 230, 230))
d.text((c[0], c[1] + 20), "N", font=F2, fill=(230, 230, 230), anchor="mm")
a = P(-250, -235)
d.line([a, (a[0] + 50 * S, a[1])], fill=(230, 230, 230), width=3)
d.text((a[0], a[1] + 8), "50 BU (kit) = 6.6 floors; the lot = 240 x 240 BU", font=F4, fill=(200, 200, 200))
# ------------------------------------------------------------ the panel: legend + the route slots
d.rectangle([MAPW, 0, W, H], fill=(14, 15, 19))
d.line([(MAPW, OY), (MAPW, H)], fill=(60, 60, 70), width=2)
px = MAPW + 24
y = 84
d.text((px, y), "LEGEND", font=F2, fill=(235, 235, 235))
y += 30
for (colr, text) in ((WALLC, "Container curtain wall (crosswise boxes, 4 high)"), (TOWC, "Towers / gatehouses (cast concrete)"),
                     ((255, 205, 40), "Trucks: drop / pick-up bays (W, S, E)"), ((200, 215, 230), "High-speed freight train (N)"),
                     (OR, "The gantry: legs ride the wall runways"), ((200, 185, 160), "The keep = the crane's trolley"),
                     ((255, 140, 26, 90), "Crane reach (travel x trolley)")):
    d.rectangle([px, y, px + 26, y + 16], fill=colr)
    d.text((px + 36, y + 8), text, font=F3, fill=(220, 220, 220), anchor="lm")
    y += 26
y += 10
d.text((px, y), "ROUTE SLOTS (illustrative; topology = game graph)", font=F2, fill=RC)
y += 28
SLOTNAME = {"gatehouse": "S gatehouse chamber, over the arch", "wall_outer": "wall, outer face (a cut-open box)",
            "corner_tower": "corner tower, S face", "truck_box": "a truck's box in the W bay lane",
            "wall_inner": "wall, inner face (yard side)", "train_box": "a train car's box", "leg": "gantry leg, S face",
            "span": "the span's gallery, S face", "keep_crown": "the keep's crown: THE SERVER"}
for i in G.NODES:
    if i == "start":
        t = "S  start: the hack box among the queued trucks"
    elif i == "srv":
        t = "T  " + SLOTNAME[G.SLOT[i]]
    else:
        o = G.ROOM[i]["o"]
        t = "%-2d %s  (z %d)" % (num[i], SLOTNAME[G.SLOT[i]], round(o[2]))
    d.text((px, y), t, font=F4, fill=(255, 90, 70) if i == "srv" else (215, 215, 215))
    y += 19
y += 14
for line in ("Read it as a siege: in at a truck gate, along / up", "the walls and towers, up a gantry leg, across",
             "the span, into the keep. Branches: the outer E wall", "and the train vs the W bay lane and inner wall.",
             "", "The gantry is shown at its overview position", "(mid-north). It rolls the whole yard length; at", "its N stop the span stands over the train."):
    d.text((px, y), line, font=F4, fill=(185, 185, 190))
    y += 18
im.save(os.path.join(os.path.dirname(HERE), "plan.png"))
print("saved", im.size)
