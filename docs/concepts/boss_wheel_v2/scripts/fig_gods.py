"""Boss Wheel v2 round 3: the Roman gods as fresco busts (frontal, head and shoulders, one attribute each).

god(name, px, t, act) -> dict of L masks: robe, skin, hair, beard, metal, accent, dark, white, halo
Unit box 400 x 300 (x right, y down). Bust base on y = 300. Frontal faces read best once tiled into tesserae.
All shapes are procedural; nothing random.
"""
import math

from PIL import Image

from shapes import Pen

UW, UH = 400, 300
LAYERS = ("halo", "robe", "skin", "hair", "beard", "white", "metal", "accent", "dark")


def _pens(px):
    k = px / UW
    size = (px, int(UH * k))
    return {n: Pen(size, k) for n in LAYERS}


def _out(P):
    return {n: p.m for n, p in P.items()}


def face(P, cx, cy, s=1.0, brow=0.0, beard=False, old=False, look=0.0, mouth_open=0.0):
    """Frontal head: oval face, ears, eyes, brows, nose, mouth. (cx, cy) = face centre."""
    sk, dk = P["skin"], P["dark"]
    sk.ell(cx, cy, 38 * s, 48 * s)
    sk.ell(cx - 38 * s, cy + 2 * s, 7 * s, 12 * s)
    sk.ell(cx + 38 * s, cy + 2 * s, 7 * s, 12 * s)
    sk.rrect(cx - 16 * s, cy + 36 * s, cx + 16 * s, cy + 70 * s, 6 * s)          # neck
    for sx in (-1, 1):
        ex = cx + sx * 15 * s + look * 3 * s
        dk.ell(ex, cy - 2 * s, 5.5 * s, 4.2 * s)                                   # eye
        P["white"].ell(cx + sx * 15 * s, cy - 2 * s, 8.5 * s, 5 * s)
        a0 = -8 * brow * sx
        dk.limb([(cx + sx * 6 * s, cy - 13 * s + brow * 3 * s), (cx + sx * 15 * s, cy - 16 * s), (cx + sx * 25 * s, cy - 13 * s - brow * 2 * s)],
                3.6 * s, 2.4 * s)                                                  # brow (brow > 0 = frown)
    dk.limb([(cx + 1 * s, cy - 6 * s), (cx + 3 * s, cy + 12 * s), (cx - 3 * s, cy + 15 * s)], 2.6 * s, 2.2 * s)   # nose
    mo = mouth_open
    dk.limb([(cx - 9 * s, cy + 25 * s), (cx, cy + 26 * s + 2 * mo * s), (cx + 9 * s, cy + 25 * s)], 2.8 * s, 2.8 * s)
    if mo > 0.2:
        dk.ell(cx, cy + 27 * s, 6 * s, 4 * mo * s)
    if beard:
        bd = P["white"] if old else P["beard"]
        bd.blob([(cx - 36 * s, cy + 4 * s), (cx - 30 * s, cy + 46 * s), (cx - 14 * s, cy + 74 * s), (cx, cy + 82 * s), (cx + 14 * s, cy + 74 * s),
                 (cx + 30 * s, cy + 46 * s), (cx + 36 * s, cy + 4 * s), (cx + 20 * s, cy + 22 * s), (cx, cy + 30 * s), (cx - 20 * s, cy + 22 * s)], n=6)
        sk.ell(cx, cy + 26 * s, 9 * s, 5 * s)       # lips peek through
        dk.limb([(cx - 9 * s, cy + 25 * s), (cx + 9 * s, cy + 25 * s)], 2.8 * s, 2.8 * s)
        for j in range(5):                         # curl lines
            x = cx - 22 * s + j * 11 * s
            dk.limb([(x, cy + 40 * s), (x + 3 * s, cy + 58 * s)], 1.6 * s, 1.0 * s)


def shoulders(P, cx, s=1.0, drape="left", fold=True):
    r = P["robe"]
    r.blob([(cx - 150 * s, 300), (cx - 128 * s, 228), (cx - 70 * s, 196), (cx, 192), (cx + 70 * s, 196), (cx + 128 * s, 228), (cx + 150 * s, 300)], n=6)
    sk = P["skin"]
    if drape == "left":        # one bare shoulder (right side of the image), the cloak over the other
        sk.blob([(cx + 22 * s, 204), (cx + 84 * s, 206), (cx + 132 * s, 236), (cx + 140 * s, 300), (cx + 40 * s, 300), (cx + 20 * s, 240)], n=6)
        P["metal"].limb([(cx - 70 * s, 204), (cx + 20 * s, 300)], 7 * s, 7 * s)      # gilt hem across the chest
        P["metal"].ell(cx - 70 * s, 208, 9 * s, 9 * s)                                # fibula
    if fold:
        for j in range(4):
            x = cx - 120 * s + j * 30 * s
            P["dark"].limb([(x, 300), (x + 16 * s, 246 - j * 6), (x + 40 * s, 222)], 2.2 * s, 1.4 * s)


def mars(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 200
    thrust = 40 * act
    # spear: diagonal across the panel, the point up and right (thrusts outward on act)
    P["metal"].limb([(cx - 150, 290), (cx + 130 + thrust, 30 - thrust * 0.6)], 7, 6)
    P["metal"].poly([(cx + 120 + thrust, 26 - thrust * 0.6), (cx + 158 + thrust, 4 - thrust * 0.6), (cx + 140 + thrust, 44 - thrust * 0.6)])
    shoulders(P, cx, 1.0, drape="right")
    P["metal"].blob([(cx - 140, 214), (cx - 70, 196), (cx + 70, 196), (cx + 140, 214), (cx + 128, 260), (cx - 128, 260)], n=6)   # cuirass
    for j in range(5):
        P["dark"].limb([(cx - 80 + j * 40, 218), (cx - 80 + j * 40, 252)], 2.2, 2.2)
    face(P, cx, 116, 1.0, brow=1.0)
    # Corinthian helmet pushed up + a tall red crest
    P["metal"].blob([(cx - 44, 104), (cx - 46, 70), (cx - 30, 46), (cx, 38), (cx + 30, 46), (cx + 46, 70), (cx + 44, 104), (cx + 36, 86), (cx - 36, 86)], n=6)
    P["accent"].blob([(cx - 34, 46), (cx - 20, 6), (cx + 10, -8), (cx + 50, 2), (cx + 70, 24), (cx + 40, 34), (cx + 4, 30)], n=6)
    for j in range(6):
        P["dark"].limb([(cx - 18 + j * 12, 30), (cx - 10 + j * 14, 6)], 1.6, 1.0)
    # round shield edge at the left
    P["metal"].ell(cx - 128, 236, 62, 62)
    P["accent"].ell(cx - 128, 236, 48, 48)
    P["metal"].ell(cx - 128, 236, 12, 12)
    return _out(P)


def jupiter(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 196
    shoulders(P, cx, 1.0, drape="left")
    face(P, cx, 112, 1.0, brow=0.6, beard=True, old=True, mouth_open=act)
    # wild white hair + laurel
    P["white"].blob([(cx - 50, 116), (cx - 58, 70), (cx - 40, 40), (cx, 30), (cx + 40, 40), (cx + 58, 70), (cx + 50, 116), (cx + 34, 74), (cx - 34, 74)], n=6)
    for j in range(7):
        a = math.radians(200 + j * 23)
        P["metal"].ell(cx + 46 * math.cos(a), 78 + 36 * math.sin(a), 9, 4, ang=math.degrees(a) + 90)
    # raised fist with a thunderbolt (zigzag), flashing on act
    hx, hy = cx + 120, 120 - 16 * act
    P["skin"].limb([(cx + 100, 240), (cx + 128, 180), (hx, hy + 20)], 26, 20)
    P["skin"].ell(hx, hy + 10, 16, 18)
    zz = [(hx - 30, hy - 110), (hx + 14, hy - 60), (hx - 14, hy - 40), (hx + 26, hy + 10), (hx + 4, hy + 20), (hx + 40, hy + 80)]
    for j in range(len(zz) - 1):
        P["metal"].limb([zz[j], zz[j + 1]], 16 - j * 1.5, 14 - j * 1.5)
    P["metal"].poly([(hx + 28, hy + 64), (hx + 52, hy + 100), (hx + 30, hy + 86)])
    if act > 0.1:
        for j in range(8):
            a = math.radians(j * 45 + 20)
            P["halo"].limb([(hx + 30 * math.cos(a), hy - 30 + 30 * math.sin(a)), (hx + (60 + 50 * act) * math.cos(a), hy - 30 + (60 + 50 * act) * math.sin(a))], 5, 1)
    return _out(P)


def minerva(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 210
    shoulders(P, cx, 1.0, drape="none")
    P["metal"].blob([(cx - 70, 204), (cx + 70, 204), (cx + 40, 250), (cx - 40, 250)], n=5)          # aegis collar
    for j in range(6):
        P["accent"].ell(cx - 50 + j * 20, 214, 4, 4)
    face(P, cx, 118, 1.0, brow=0.3)
    # Attic helmet with a long horsehair crest sweeping back
    P["metal"].blob([(cx - 44, 104), (cx - 46, 66), (cx - 26, 40), (cx + 4, 34), (cx + 34, 44), (cx + 46, 70), (cx + 44, 100), (cx + 30, 80), (cx - 30, 80)], n=6)
    P["accent"].blob([(cx - 10, 36), (cx - 40, 8), (cx - 96, 4), (cx - 150, 30), (cx - 120, 44), (cx - 70, 34), (cx - 30, 44)], n=6)
    P["metal"].ell(cx + 46, 84, 8, 16)
    # the great round shield raised (guard) on the left: rises on act
    sy = 220 - 30 * act
    P["metal"].ell(cx - 110, sy, 84, 84)
    P["robe"].ell(cx - 110, sy, 70, 70)
    P["metal"].ell(cx - 110, sy, 24, 24)
    P["accent"].ell(cx - 110, sy, 16, 16)               # gorgoneion
    for j in range(8):
        a = math.radians(j * 45)
        P["dark"].limb([(cx - 110 + 28 * math.cos(a), sy + 28 * math.sin(a)), (cx - 110 + 66 * math.cos(a), sy + 66 * math.sin(a))], 2, 2)
    # the owl on the right shoulder
    ox, oy = cx + 104, 176
    P["beard"].blob([(ox - 20, oy + 30), (ox - 22, oy - 6), (ox - 14, oy - 26), (ox, oy - 20), (ox + 14, oy - 26), (ox + 22, oy - 6), (ox + 20, oy + 30)], n=6)
    for sx in (-1, 1):
        P["white"].ell(ox + sx * 8, oy - 8, 7, 7)
        P["dark"].ell(ox + sx * 8, oy - 8, 3.5, 3.5)
    P["metal"].poly([(ox - 3, oy - 2), (ox + 3, oy - 2), (ox, oy + 6)])
    return _out(P)


def mercury(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 200
    shoulders(P, cx, 1.0, drape="left")
    face(P, cx, 120, 1.0, brow=-0.4, look=0.6)
    P["hair"].blob([(cx - 40, 110), (cx - 44, 84), (cx - 30, 70), (cx + 30, 70), (cx + 44, 84), (cx + 40, 110), (cx + 30, 92), (cx - 30, 92)], n=6)
    # petasos (round winged hat)
    P["metal"].ell(cx, 74, 70, 16)
    P["metal"].blob([(cx - 40, 74), (cx - 34, 46), (cx, 38), (cx + 34, 46), (cx + 40, 74)], n=6)
    flap = 6 * math.sin(t * 9) + 18 * act
    for sx in (-1, 1):
        for j in range(3):
            P["white"].blob([(cx + sx * 38, 56 + j * 4), (cx + sx * (70 + j * 16), 30 - j * 10 - flap), (cx + sx * (60 + j * 12), 54 + j * 2)], n=4)
    # caduceus: staff, two snakes, wings
    sx0 = cx + 120
    P["metal"].limb([(sx0, 300), (sx0, 30)], 7, 6)
    P["metal"].ell(sx0, 26, 9, 9)
    for side in (-1, 1):
        pts = [(sx0 + side * 18 * math.sin(u * 0.6), 280 - u * 8.6) for u in range(0, 30)]
        P["accent"].limb(pts, 6, 4)
        P["white"].blob([(sx0, 44), (sx0 + side * 40, 24 - flap * 0.5), (sx0 + side * 34, 50)], n=4)
    # speed streaks on act (Mercury = DETOUR, speed)
    if act > 0.05:
        for j in range(6):
            y = 120 + j * 26
            P["halo"].limb([(cx - 190, y), (cx - 190 + 140 * act, y)], 4, 1)
    return _out(P)


def vulcan(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 190
    shoulders(P, cx, 1.0, drape="left")
    face(P, cx, 118, 1.0, brow=1.0, beard=True)
    P["accent"].blob([(cx - 42, 100), (cx - 40, 66), (cx - 20, 34), (cx + 14, 22), (cx + 34, 40), (cx + 42, 70), (cx + 42, 100), (cx, 84)], n=6)   # pileus cap
    # hammer raised over the shoulder: swings down on act
    a = math.radians(-70 + 80 * act)
    hx, hy = cx + 104, 210
    tx, ty = hx + 130 * math.cos(a), hy + 130 * math.sin(a)
    P["skin"].limb([(cx + 100, 240), (hx, hy)], 26, 22)
    P["metal"].limb([(hx, hy), (tx, ty)], 12, 11)
    nx, ny = -math.sin(a) * 1.5, math.cos(a) * 1.5
    P["dark"].poly([(tx + nx * 28 - math.cos(a) * 8, ty + ny * 28 - math.sin(a) * 8), (tx - nx * 28 - math.cos(a) * 8, ty - ny * 28 - math.sin(a) * 8),
                    (tx - nx * 28 + math.cos(a) * 22, ty - ny * 28 + math.sin(a) * 22), (tx + nx * 28 + math.cos(a) * 22, ty + ny * 28 + math.sin(a) * 22)])
    # flames of the forge along the bottom (burn / infect)
    for j in range(7):
        x = 40 + j * 54
        h = 50 + 18 * math.sin(t * 7 + j * 1.9) + 40 * act
        P["halo"].blob([(x - 22, 300), (x - 8, 300 - h * 0.6), (x, 300 - h), (x + 10, 300 - h * 0.5), (x + 22, 300)], n=5)
    return _out(P)


def neptune(px, t=0.0, act=0.0):
    P = _pens(px)
    cx = 200
    shoulders(P, cx, 1.0, drape="left")
    face(P, cx, 112, 1.0, brow=0.8, beard=True, old=True)
    P["white"].blob([(cx - 52, 120), (cx - 62, 76), (cx - 70, 50), (cx - 40, 40), (cx, 26), (cx + 40, 40), (cx + 70, 50), (cx + 62, 76), (cx + 52, 120), (cx + 34, 76), (cx - 34, 76)], n=6)
    P["metal"].limb([(cx - 140, 300), (cx - 140, 20)], 7, 6)                     # trident
    for dx in (-22, 0, 22):
        P["metal"].limb([(cx - 140 + dx, 60), (cx - 140 + dx, 6)], 5, 3)
    P["metal"].limb([(cx - 162, 60), (cx - 118, 60)], 6, 6)
    for j in range(8):                                                           # the wave along the bottom (sweep)
        x = j * 56 - 20 + 30 * act
        P["halo"].blob([(x, 300), (x + 10, 262 - 20 * act), (x + 40, 246 - 30 * act), (x + 56, 266), (x + 40, 262), (x + 56, 300)], n=5)
    return _out(P)


def pluto(px, t=0.0, act=0.0):
    """The NULL slice: the underworld void. A veiled figure barely there, Cerberus in silhouette."""
    P = _pens(px)
    cx = 200
    P["robe"].blob([(cx - 120, 300), (cx - 70, 150), (cx - 40, 60), (cx, 40), (cx + 40, 60), (cx + 70, 150), (cx + 120, 300)], n=6)   # veil
    P["dark"].ell(cx, 108, 30, 38)
    for sx in (-1, 1):
        P["accent"].ell(cx + sx * 11, 104, 3, 2)                                  # two embers for eyes
    for j, x in enumerate((cx - 120, cx - 92, cx - 64)):                           # Cerberus: three heads
        P["dark"].blob([(x - 18, 300), (x - 20, 250), (x - 6, 226 - j * 4), (x + 16, 232 - j * 4), (x + 22, 260), (x + 20, 300)], n=5)
        P["dark"].poly([(x - 10, 230 - j * 4), (x - 4, 214 - j * 4), (x + 2, 230 - j * 4)])
    P["metal"].limb([(cx + 110, 300), (cx + 110, 60)], 5, 4)                       # bident
    for dx in (-12, 12):
        P["metal"].limb([(cx + 110 + dx, 80), (cx + 110 + dx, 44)], 4, 2)
    P["metal"].limb([(cx + 98, 80), (cx + 122, 80)], 4, 4)
    return _out(P)


GODS = {"mars": mars, "jupiter": jupiter, "minerva": minerva, "mercury": mercury, "vulcan": vulcan, "neptune": neptune, "pluto": pluto}
