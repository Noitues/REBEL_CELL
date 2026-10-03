"""Round 27: the shared rules of the Cell's district, used by BOTH hq27.py (Blender) and map27.py (city map):
  - PAINTED ROOFS: a roof carries the Cell's paint when its PROJECTED position on the map (the game's 2:1 iso,
    roof h px above its ground point) falls inside the crest (the Cell's raised fist) drawn over the district;
  - THE CANYON: the grid street j = 36 between the cross streets i = 26 and i = 46 is the Tokyo canyon; the city
    buildings in the two lot strips that face it make way for its shophouses.
Pure python (Blender and CPython). Lots as in round 25 citydata.py: X = ox + (x - y) * 34, Y = oy + (x + y) * 17.
"""
import math

TA, TB = 34.0, 17.0
CREST_H = 470.0           # crest height on the map, city px
CREST_DY = -40.0          # (unused since CREST_LOT)
CREST_LOT = (39.0, 43.9)  # the crest's centre (lots): the block just south of the canyon, so its fingers touch the canyon
CANYON_J = 36             # the street row (lots) that becomes the canyon
CANYON_I0, CANYON_I1 = 27, 46
CROSS_I = (32, 36, 40)    # grid cross streets that cut the canyon (left open)
SHOP_DEPTH_LOTS = 1.55    # shophouse depth (9 BU) + facade offset


def _crest_parts():
    parts = []
    for i in range(4):
        x0 = -5.2 + i * 2.65
        parts.append((x0, x0 + 2.2, 8.5, 13.2 + (0.6 if i in (1, 2) else 0)))
    parts.append((-5.2, 5.4, 5.4, 8.1))
    parts.append((-3.5, 3.5, 0.0, 5.1))
    return parts


CREST = _crest_parts()


TEN_Z_PX = 45.0           # typical tenement roof height on the map, px (for choosing the painted block's lots)


class Cfg:
    def __init__(self, palm, streets=None):
        self.P = tuple(palm)
        self.ten = {}
        if streets is not None:
            self.ten = self.tenement_lots(streets)

    def tenement_lots(self, streets):
        """THE PAINTED BLOCK: the non-street lots under the crest are rebuilt as low flat-roof tenements (one per lot,
        seeded height), so the stencil lands on a near-continuous field of roofs and the fist can read from above.
        -> {(i, j): height BU}"""
        import random
        rects = self.crest_rects()
        out = {}
        for i in range(10, 64):
            for j in range(14, 64):
                if (i, j) in streets:
                    continue
                X, Y = self.iso(i + 0.5, j + 0.5)
                Y -= TEN_Z_PX
                if not any(r[0] - 22 <= X <= r[2] + 22 and r[1] - 22 <= Y <= r[3] + 22 for r in rects):
                    continue
                if self.in_canyon_band(i + 0.5, j + 0.5):
                    continue
                r = random.Random(i * 7919 + j * 104729 + 2727)
                out[(i, j)] = 6.5 + (0.0 if r.random() < 0.85 else 1.2)  # one roof field: low, level (a few lots a floor up)
        return out

    @staticmethod
    def iso(x, y):
        return ((x - y) * TA, (x + y) * TB)  # relative screen px (origin free: only differences are used)

    def crest_uv(self, x, y, ztop_px):
        X, Y = self.iso(x, y)
        PX, PY = self.iso(*self.P)
        k = CREST_H / 14.8
        u = (X - PX) / k
        v = ((PY + CREST_DY + CREST_H / 2) - (Y - ztop_px)) / k  # 0 at the wrist, up the screen
        return u, v

    def painted(self, x, y, ztop_px):
        u, v = self.crest_uv(x, y, ztop_px)
        return any(a0 <= u <= a1 and b0 <= v <= b1 for (a0, a1, b0, b1) in CREST)

    # ---- the paint is a stencil: each roof carries only the part that lies inside the crest as the map sees it
    def crest_rects(self, dx=0.0, dy=0.0):
        """Crest rectangles in screen px (relative iso + offset): (x0, y0, x1, y1)."""
        PX, PY = self.iso(*CREST_LOT)
        k = CREST_H / 14.8
        base = PY - TEN_Z_PX + CREST_H / 2  # the crest sits on the roof field of the painted block
        return [(PX + a0 * k + dx, base - b1 * k + dy, PX + a1 * k + dx, base - b0 * k + dy) for (a0, a1, b0, b1) in CREST]

    @staticmethod
    def clip_rect(poly, r):
        """Sutherland-Hodgman: convex/concave polygon clipped by an axis-aligned rect."""
        x0, y0, x1, y1 = r
        edges = [(lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
                 (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
                 (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
                 (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))]
        out = list(poly)
        for inside, cut in edges:
            if not out:
                break
            src, out = out, []
            for i in range(len(src)):
                a, b = src[i - 1], src[i]
                if inside(b):
                    if not inside(a):
                        out.append(cut(a, b))
                    out.append(b)
                elif inside(a):
                    out.append(cut(a, b))
        return out if len(out) >= 3 else []

    def pieces_screen(self, poly, dx=0.0, dy=0.0):
        return [q for q in (self.clip_rect(poly, r) for r in self.crest_rects(dx, dy)) if q]

    def pieces_lot(self, poly_lot, ztop_px):
        """Roof polygon in lots at height ztop_px -> the painted pieces, in lots."""
        scr = [(self.iso(x, y)[0], self.iso(x, y)[1] - ztop_px) for (x, y) in poly_lot]
        out = []
        for q in self.pieces_screen(scr):
            out.append([((X / TA + (Y + ztop_px) / TB) / 2, ((Y + ztop_px) / TB - X / TA) / 2) for (X, Y) in q])
        return out

    # ---- the canyon
    @staticmethod
    def in_canyon_band(x, y):
        if not (CANYON_I0 - 0.2 <= x <= CANYON_I1 + 0.2):
            return False
        return (CANYON_J - SHOP_DEPTH_LOTS - 0.1 <= y < CANYON_J) or (CANYON_J + 1 < y <= CANYON_J + 1 + SHOP_DEPTH_LOTS + 0.1)

    def removed(self, x, y):
        """City buildings that make way: the canyon's two facing strips and the painted block's lots."""
        return self.in_canyon_band(x, y) or (math.floor(x), math.floor(y)) in self.ten

    @staticmethod
    def canyon_origin():
        return (CANYON_I1, CANYON_J + 0.5)  # lot point: canyon frame origin (the camera end); local Y runs toward -x

    @staticmethod
    def canyon_len():
        return (CANYON_I1 - CANYON_I0) * 6.0

    @staticmethod
    def canyon_gaps():
        return [((CANYON_I1 - i - 1) * 6.0 - 0.2, (CANYON_I1 - i) * 6.0 + 0.2) for i in CROSS_I]
