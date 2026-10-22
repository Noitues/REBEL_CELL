"""Tiny vector kit: one shape list renders to SVG (the Godot icon source) and to PIL (supersampled), identical by construction.

Units are the sticker canvas (130 x 130, the route art's size). Shapes: polygon (closed, fill and/or stroke), polyline (open stroke),
circle. Colours are (r, g, b) or (r, g, b, a) 0-255. `clip` names a clip polygon (the sticker field) the shape is cut to.
"""
import math
from PIL import Image, ImageDraw


def rgba(c):
    c = tuple(c)
    return (c[0], c[1], c[2], c[3] if len(c) > 3 else 255)


def hexs(c):
    return "#%02X%02X%02X" % tuple(c[:3])


def rot(pts, deg, c=(0, 0)):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]


def mv(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def circle_pts(cx, cy, r, n=48):
    return arc(cx, cy, r, 0, 360, n)[:-1]


def rrect(cx, cy, w, h, r, n=8, deg=0):
    r = min(r, w / 2, h / 2)
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    pts = []
    for (ccx, ccy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += arc(ccx, ccy, r, a0, a0 + 90, n)
    return rot(pts, deg, (cx, cy)) if deg else pts


def gear(cx, cy, r_root, r_tip, teeth=8, tip_deg=15.0, base_deg=24.0, phase=0.0):
    """A cog outline: `teeth` flat-topped teeth, tip arc `tip_deg` wide, base `base_deg`, notch bottoms between."""
    pts = []
    per = 360.0 / teeth
    for i in range(teeth):
        c = phase + i * per
        for a, r in ((c - base_deg / 2, r_root), (c - tip_deg / 2, r_tip), (c + tip_deg / 2, r_tip), (c + base_deg / 2, r_root)):
            pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
        # notch floor to the next tooth
        a_end = c + base_deg / 2
        a_next = c + per - base_deg / 2
        pts += arc(cx, cy, r_root, a_end, a_next, 3)[1:-1]
    return pts


def crescent(cx, cy, R, r, dx, dy):
    """Disc (cx, cy, R) with a disc (cx+dx, cy+dy, r) bitten out; returns the polygon."""
    c2 = (cx + dx, cy + dy)
    outer = []
    for i in range(720):
        a = math.radians(i * 0.5)
        p = (cx + R * math.cos(a), cy + R * math.sin(a))
        if math.hypot(p[0] - c2[0], p[1] - c2[1]) >= r:
            outer.append((i, p))
    # roll so the gap is at the ends
    idx = [i for i, _ in outer]
    gap_at = 0
    for k in range(len(idx)):
        if (idx[(k + 1) % len(idx)] - idx[k]) % 720 > 1:
            gap_at = (k + 1) % len(idx)
            break
    outer = outer[gap_at:] + outer[:gap_at]
    inner = []
    for i in range(720):
        a = math.radians(i * 0.5)
        p = (c2[0] + r * math.cos(a), c2[1] + r * math.sin(a))
        if math.hypot(p[0] - cx, p[1] - cy) < R:
            inner.append((i, p))
    idx = [i for i, _ in inner]
    gap_at = 0
    for k in range(len(idx)):
        if (idx[(k + 1) % len(idx)] - idx[k]) % 720 > 1:
            gap_at = (k + 1) % len(idx)
            break
    inner = inner[gap_at:] + inner[:gap_at]
    pts = [p for _, p in outer]
    inner_pts = [p for _, p in inner]
    # connect outer end to the nearer end of the inner arc
    if math.dist(pts[-1], inner_pts[0]) > math.dist(pts[-1], inner_pts[-1]):
        inner_pts.reverse()
    return pts + inner_pts


class Doc:
    def __init__(self, w=130, h=130, name="icon"):
        self.w, self.h, self.name = w, h, name
        self.items = []
        self.clips = {}

    # -- adding -------------------------------------------------------------------------------------------------
    def clip(self, name, pts):
        self.clips[name] = list(pts)

    def poly(self, pts, fill=None, stroke=None, sw=0.0, clip=None, closed=True):
        self.items.append(dict(t="poly" if closed else "line", pts=[tuple(p) for p in pts], fill=fill, stroke=stroke, sw=sw, clip=clip))

    def line(self, pts, stroke, sw, clip=None):
        self.poly(pts, None, stroke, sw, clip, closed=False)

    def circle(self, cx, cy, r, fill=None, stroke=None, sw=0.0, clip=None):
        self.items.append(dict(t="circle", c=(cx, cy), r=r, fill=fill, stroke=stroke, sw=sw, clip=clip))

    def group(self, pieces, fill, ink=None, ow=2.5, extra_levels=(), clip=None):
        """pieces: list of polygons drawn as ONE glyph: `extra_levels` [(colour, d)] outermost first, then the ink outline
        (d = ow), then every fill, so the glyph's own pieces never show seams."""
        for col, d in list(extra_levels) + ([(ink, ow)] if ink is not None else []):
            for p in pieces:
                self.poly(p, col, col, 2 * d, clip)
        for p in pieces:
            self.poly(p, fill, None, 0, clip)

    # -- SVG ----------------------------------------------------------------------------------------------------
    def svg(self):
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" height="%g">' % (self.w, self.h, self.w, self.h)]
        if self.clips:
            o.append("<defs>")
            for n, pts in self.clips.items():
                o.append('<clipPath id="%s"><polygon points="%s"/></clipPath>' % (n, " ".join("%.2f,%.2f" % p for p in pts)))
            o.append("</defs>")
        for it in self.items:
            def paint(it):
                s = ""
                f = it["fill"]
                st = it["stroke"]
                s += ' fill="%s"' % (hexs(f) if f else "none")
                if f and len(f) > 3 and f[3] < 255:
                    s += ' fill-opacity="%.3f"' % (f[3] / 255)
                if st and it["sw"] > 0:
                    s += ' stroke="%s" stroke-width="%.2f" stroke-linejoin="round" stroke-linecap="round"' % (hexs(st), it["sw"])
                    if len(st) > 3 and st[3] < 255:
                        s += ' stroke-opacity="%.3f"' % (st[3] / 255)
                if it["clip"]:
                    s += ' clip-path="url(#%s)"' % it["clip"]
                return s
            if it["t"] == "circle":
                o.append('<circle cx="%.2f" cy="%.2f" r="%.2f"%s/>' % (it["c"][0], it["c"][1], it["r"], paint(it)))
            else:
                tag = "polygon" if it["t"] == "poly" else "polyline"
                o.append('<%s points="%s"%s/>' % (tag, " ".join("%.2f,%.2f" % p for p in it["pts"]), paint(it)))
        o.append("</svg>")
        return "\n".join(o)

    # -- PIL ----------------------------------------------------------------------------------------------------
    @staticmethod
    def _stroke(d, P, w):
        if len(P) >= 2:
            d.line(P, fill=255, width=max(1, int(round(w))))
        r = w / 2.0
        for x, y in P:
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)

    def render(self, scale=1.0, ss=4, bg=None):
        from PIL import ImageChops
        W, H = int(round(self.w * scale)), int(round(self.h * scale))
        k = scale * ss
        SW, SH = W * ss, H * ss
        base = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        clipm = {}
        for n, pts in self.clips.items():
            m = Image.new("L", (SW, SH), 0)
            ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in pts], fill=255)
            clipm[n] = m

        def lay(mask, col, clip):
            nonlocal base
            col = rgba(col)
            if clip:
                mask = ImageChops.multiply(mask, clipm[clip])
            layer = Image.new("RGBA", (SW, SH), col)
            layer.putalpha(mask.point(lambda v: int(v * col[3] / 255)))
            base = Image.alpha_composite(base, layer)

        for it in self.items:
            has_s = bool(it["stroke"]) and it["sw"] > 0
            if it["t"] == "circle":
                cx, cy, r = it["c"][0] * k, it["c"][1] * k, it["r"] * k
                if it["fill"]:
                    m = Image.new("L", (SW, SH), 0)
                    ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
                    lay(m, it["fill"], it["clip"])
                if has_s:
                    hw = it["sw"] * k / 2
                    m = Image.new("L", (SW, SH), 0)
                    dd = ImageDraw.Draw(m)
                    dd.ellipse((cx - r - hw, cy - r - hw, cx + r + hw, cy + r + hw), fill=255)
                    if r - hw > 0:
                        dd.ellipse((cx - r + hw, cy - r + hw, cx + r - hw, cy + r - hw), fill=0)
                    lay(m, it["stroke"], it["clip"])
            else:
                P = [(x * k, y * k) for x, y in it["pts"]]
                closed = it["t"] == "poly"
                if closed and it["fill"]:
                    m = Image.new("L", (SW, SH), 0)
                    ImageDraw.Draw(m).polygon(P, fill=255)
                    lay(m, it["fill"], it["clip"])
                if has_s:
                    m = Image.new("L", (SW, SH), 0)
                    self._stroke(ImageDraw.Draw(m), P + ([P[0]] if closed and len(P) > 2 else []), it["sw"] * k)
                    lay(m, it["stroke"], it["clip"])
        out = base.resize((W, H), Image.LANCZOS)
        if bg is not None:
            b = Image.new("RGBA", (W, H), rgba(bg))
            b.alpha_composite(out)
            return b
        return out
