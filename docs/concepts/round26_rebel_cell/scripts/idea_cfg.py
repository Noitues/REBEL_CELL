"""Round 26: the shared rules of each base idea, used by BOTH the Blender scene (hq26.py) and the city map (map26.py)
so the close-up and the map always agree: which city buildings make way for the hero, which roofs carry paint.

Lot space as in round 25 (citydata.py). The palm of the fist roads is the origin P. Two screen-aligned axes:
    u = ((x - Px) - (y - Py)) / sqrt2      screen-right on the map
    v = ((x - Px) + (y - Py)) / sqrt2      screen-down on the map = toward the map / close-up camera
Hero builders work in a local frame lx = 6u, ly = -6v (BU), rotated +45 deg into the world (camera at local -Y).
Pure python (Blender and CPython).
"""
import math

S2 = math.sqrt(2.0)
IDEAS = ["tokyo", "roofs", "skyline", "deck", "rec"]
TITLE = {"tokyo": "1  TOKYO STREET", "roofs": "2  PAINTED ROOFS", "skyline": "3  HIJACKED SKYLINE", "deck": "4  KNUCKLE DECK",
         "rec": "RECOMMENDED: KNUCKLE DECK + HIJACKED CANYON"}


REC_DECK_HW, REC_DECK_Y0, REC_DECK_Y1 = 34.0, -34.0, 44.0  # the recommended deck's footprint in the canyon frame (BU)


class Cfg:
    def __init__(self, lay):
        self.P = tuple(lay["centre"])
        self.fist = [(tuple(s["a"]), tuple(s["b"])) for s in lay["fist"]]
        self._grid = None
        # the Tokyo canyon follows the fist road under the thumb (palm -> wrist), the longest inner road
        self.canyon = min(self.fist, key=lambda s: math.hypot(s[0][0] - 36.1, s[0][1] - 39.2) + math.hypot(s[1][0] - 48.2, s[1][1] - 45.5))

    def local_of(self, x, y):
        u, v = self.uv(x, y)
        return (6.0 * u, -6.0 * v)

    def canyon_frame(self):
        """(A local, LC length BU, CROT deg): the canyon frame's origin (palm end of the road), length, rotation."""
        A = self.local_of(*self.canyon[0])
        B = self.local_of(*self.canyon[1])
        LC = math.hypot(A[0] - B[0], A[1] - B[1])
        d = ((A[0] - B[0]) / LC, (A[1] - B[1]) / LC)
        return A, LC, math.degrees(math.atan2(-d[0], d[1]))

    def in_canyon(self, x, y):
        """lot -> canyon frame (BU): Y along the road toward the palm (0 = palm end), X across."""
        A, LC, rot = self.canyon_frame()
        lx, ly = self.local_of(x, y)
        dx, dy = lx - A[0], ly - A[1]
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        return (dx * c + dy * s, -dx * s + dy * c), LC

    def canyon_td(self, x, y):
        (ax, ay), (bx, by) = self.canyon
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        t = ((x - ax) * dx + (y - ay) * dy) / (L * L)
        d = abs((x - ax) * dy - (y - ay) * dx) / L
        return t, d, L

    def uv(self, x, y):
        dx, dy = x - self.P[0], y - self.P[1]
        return (dx - dy) / S2, (dx + dy) / S2

    # ---- the region enclosed by the fist roads (raster flood fill, 0.25 lot cells)
    def _build(self):
        res = 0.25
        xs = [p[0] for s in self.fist for p in s]
        ys = [p[1] for s in self.fist for p in s]
        x0, y0 = min(xs) - 2, min(ys) - 2
        nx, ny = int((max(xs) + 2 - x0) / res) + 1, int((max(ys) + 2 - y0) / res) + 1
        wall = [[False] * ny for _ in range(nx)]
        for (a, b) in self.fist:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(2, int(L / (res * 0.4)))
            for k in range(n + 1):
                t = k / n
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                i, j = int((px - x0) / res), int((py - y0) / res)
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if 0 <= i + di < nx and 0 <= j + dj < ny:
                            wall[i + di][j + dj] = True
        out = [[False] * ny for _ in range(nx)]
        st = [(0, 0)]
        out[0][0] = True
        while st:
            i, j = st.pop()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < nx and 0 <= b < ny and not out[a][b] and not wall[a][b]:
                    out[a][b] = True
                    st.append((a, b))
        self._grid = (x0, y0, res, nx, ny, out)

    def in_fist(self, x, y):
        if self._grid is None:
            self._build()
        x0, y0, res, nx, ny, out = self._grid
        i, j = int((x - x0) / res), int((y - y0) / res)
        if not (0 <= i < nx and 0 <= j < ny):
            return False
        return not out[i][j]

    # ---- per idea: city buildings that make way for the hero (footprint centroid, lots)
    def removed(self, idea, x, y):
        u, v = self.uv(x, y)
        if idea == "tokyo":
            t, d, L = self.canyon_td(x, y)
            return d < 3.4 and -0.36 < t < 1.06
        if idea == "roofs":
            return math.hypot(u, v) < 2.6
        if idea == "skyline":
            return abs(u) < 4.8 and abs(v) < 4.8
        if idea == "deck":
            return abs(u) < 6.6 and -6.8 < v < 7.4
        if idea == "rec":  # the knuckle deck at the head of a shorter canyon, both on the thumb road's axis
            (cx, cy), LC = self.in_canyon(x, y)
            return (abs(cx) < REC_DECK_HW and REC_DECK_Y0 - 2 < cy < REC_DECK_Y1 + 2) or (abs(cx) < 21.5 and -LC - 6 < cy < REC_DECK_Y0)
        return False

    # ---- PAINTED ROOFS: a roof carries paint when its PROJECTED position (as the map sees it) is inside the fist
    def painted(self, idea, x, y, ztop_px):
        if idea != "roofs":
            return False
        s = ztop_px / 34.0  # a roof h px up on the map sits where the ground point (x - h/34, y - h/34) is
        return self.in_fist(x - s, y - s)
