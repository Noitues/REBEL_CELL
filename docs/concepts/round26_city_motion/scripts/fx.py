"""Heat / raid event props for the city map: alarm beacons, sky searchlights, police light clusters,
helicopters and drones with spotlights, corp convoy vehicles, Cell nodes + lime links, HUD chips.
All coordinates in out px (1x); drawing happens on the 2x layers handed in by cm.Scene.frame."""
import math
import random

from PIL import ImageDraw

import cm
from cm import SS, LIME, RED, BLUE

BEAM = (214, 230, 255)
ALARM = (255, 92, 36)


def _e(d, x, y, rx, ry, col):
    d.ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=col)


def beacon(addd, x, y, f, a=1.0, col=ALARM, ph=0):
    """Rotating alarm beacon on a roof: core, two sweeping flares, pulsing spill."""
    ang = (f + ph) * 2 * math.pi / 10
    pulse = 0.5 + 0.5 * math.cos(ang * 2)
    _e(addd, x, y + 3, 22, 11, col + (int(46 * a * (0.5 + pulse)),))
    for s in (0, math.pi):
        c, sn = math.cos(ang + s), math.sin(ang + s)
        ex, ey = x + c * 26, y - 2 + sn * 13
        px, py = -sn * 3.5, c * 1.8
        addd.polygon([(x * SS, (y - 2) * SS), ((ex + px) * SS, (ey + py) * SS), ((ex - px) * SS, (ey - py) * SS)],
                     fill=col + (int(120 * a * (0.4 + 0.6 * max(0, c))),))
    _e(addd, x, y - 2, 3.0, 3.0, (255, 230, 200, int(255 * a)))
    _e(addd, x, y - 2, 6, 6, col + (int(150 * a),))


def sky_searchlight(addd, x, y, ang, a=1.0, length=460, spread=0.11):
    """A ground/roof searchlight beam into the sky. ang: radians from vertical (+ right)."""
    n = 12
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        w0, w1 = 2 + length * u0 * spread, 2 + length * u1 * spread
        dx, dy = math.sin(ang), -math.cos(ang)
        px, py = -dy, dx
        p0 = (x + dx * length * u0, y + dy * length * u0)
        p1 = (x + dx * length * u1, y + dy * length * u1)
        al = int(70 * a * (1 - u0) ** 1.4)
        addd.polygon([((p0[0] + px * w0) * SS, (p0[1] + py * w0) * SS), ((p1[0] + px * w1) * SS, (p1[1] + py * w1) * SS),
                      ((p1[0] - px * w1) * SS, (p1[1] - py * w1) * SS), ((p0[0] - px * w0) * SS, (p0[1] - py * w0) * SS)],
                     fill=BEAM + (al,))
    _e(addd, x, y, 5, 3, (255, 255, 255, int(230 * a)))
    _e(addd, x, y, 12, 6, BEAM + (int(90 * a),))


def police(addd, x, y, f, seed, a=1.0):
    """A cluster of red/blue strobes on a street corner with their spill."""
    r = random.Random(seed)
    n = r.randint(2, 3)
    for k in range(n):
        ox, oy = r.uniform(-7, 7), r.uniform(-3, 3)
        ph = r.randrange(4)
        red = ((f + ph + k) % 4) < 2
        col = RED if red else BLUE
        flash = ((f + ph) % 2) == 0
        _e(addd, x + ox, y + oy, 18, 9, col + (int((70 if flash else 40) * a),))
        _e(addd, x + ox, y + oy - 1, 2.2, 1.8, (255, 255, 255, int(255 * a)) if flash else col + (int(255 * a),))
        _e(addd, x + ox, y + oy - 1, 5, 4, col + (int(170 * a),))


def spot(addd, ax, ay, gx, gy, r, a=1.0, col=BEAM):
    """Spotlight from an aircraft belly (ax, ay) to a ground pool at (gx, gy)."""
    addd.polygon([(ax * SS, ay * SS), ((gx - r) * SS, gy * SS), ((gx + r) * SS, gy * SS)], fill=col + (int(54 * a),))
    addd.polygon([(ax * SS, ay * SS), ((gx - r * 0.5) * SS, gy * SS), ((gx + r * 0.5) * SS, gy * SS)],
                 fill=col + (int(34 * a),))
    _e(addd, gx, gy, r * 1.25, r * 0.62, col + (int(70 * a),))
    _e(addd, gx, gy, r * 0.8, r * 0.4, (255, 255, 255, int(150 * a)))


def heli(over, addd, x, y, heading, f, scale=1.8, livery=(64, 70, 104), lights=True, a=1.0):
    """Police / corp helicopter seen from above at 3/4: faceted body, tail boom, rotor blur, nav lights."""
    L = 11 * scale
    c, s = math.cos(heading), math.sin(heading)
    fx, fy = c, s * 0.5                      # forward on screen
    rx, ry = -s, c * 0.5                     # right on screen

    def pt(u, v, h=0.0):
        return ((x + fx * u * L + rx * v * L) * SS, (y + fy * u * L + ry * v * L - h * L) * SS)
    al = int(255 * a)
    ink = (6, 5, 10, al)
    # tail boom + fin
    over.line([pt(-0.3, 0, 0.1), pt(-1.55, 0, 0.18)], fill=ink, width=int(4 * scale) + 1)
    over.line([pt(-0.3, 0, 0.1), pt(-1.55, 0, 0.18)], fill=livery + (al,), width=int(2 * scale) + 1)
    over.polygon([pt(-1.45, 0, 0.18), pt(-1.7, 0, 0.55), pt(-1.6, 0, 0.18)], fill=livery + (al,), outline=ink)
    # body: lower hull, cabin top, glass
    hull = [pt(0.95, 0, 0), pt(0.45, 0.42, 0), pt(-0.45, 0.4, 0), pt(-0.6, 0, 0.05), pt(-0.45, -0.4, 0), pt(0.45, -0.42, 0)]
    over.polygon(hull, fill=livery + (al,), outline=ink)
    top = [pt(0.6, 0, 0.32), pt(0.25, 0.3, 0.36), pt(-0.4, 0.28, 0.32), pt(-0.4, -0.28, 0.32), pt(0.25, -0.3, 0.36)]
    lt = tuple(min(255, int(v * 1.5 + 18)) for v in livery)
    over.polygon(top, fill=lt + (al,), outline=ink)
    over.line([pt(0.6, 0, 0.32), pt(0.25, -0.3, 0.36), pt(-0.4, -0.28, 0.32)], fill=(190, 200, 235, al), width=2)
    _e(addd, *[v / SS for v in pt(0.2, 0, -0.05)], 2.6, 2.0, (255, 255, 255, al))
    over.polygon([pt(0.92, 0, 0.04), pt(0.55, 0.3, 0.26), pt(0.55, -0.3, 0.26)], fill=(120, 170, 220, al), outline=ink)
    # rotor blur and blades
    rr = 1.25 * L
    over.ellipse([(x - rr) * SS, (y - 0.42 * L - rr * 0.5) * SS, (x + rr) * SS, (y - 0.42 * L + rr * 0.5) * SS],
                 fill=(200, 205, 220, int(46 * a)), outline=(230, 235, 250, int(110 * a)), width=2)
    ba = f * 1.9
    for k in range(2):
        b = ba + k * math.pi / 2
        over.line([((x + math.cos(b) * rr) * SS, (y - 0.42 * L + math.sin(b) * rr * 0.5) * SS),
                   ((x - math.cos(b) * rr) * SS, (y - 0.42 * L - math.sin(b) * rr * 0.5) * SS)],
                  fill=(16, 14, 22, int(170 * a)), width=2)
    if lights:
        blink = (f % 8) < 2
        lx, ly = pt(0, 0.45, 0.05)
        _e(addd, lx / SS, ly / SS, 1.6, 1.6, (60, 255, 120, al))
        lx, ly = pt(0, -0.45, 0.05)
        _e(addd, lx / SS, ly / SS, 1.6, 1.6, (255, 50, 50, al))
        if blink:
            lx, ly = pt(-1.6, 0, 0.6)
            _e(addd, lx / SS, ly / SS, 3, 3, (255, 255, 255, al))


def drone(over, addd, x, y, f, a=1.0, ph=0, lit=(255, 50, 60)):
    al = int(255 * a)
    _e(addd, x, y + 1.5, 2.2, 1.4, (255, 255, 255, al))
    over.polygon([((x - 3) * SS, y * SS), (x * SS, (y - 1.6) * SS), ((x + 3) * SS, y * SS), (x * SS, (y + 1.6) * SS)],
                 fill=(70, 74, 100, al), outline=(6, 5, 10, al))
    for dx, dy in ((-3.6, -1.4), (3.6, -1.4), (-3.6, 1.4), (3.6, 1.4)):
        over.ellipse([(x + dx - 2.2) * SS, (y + dy - 1.1) * SS, (x + dx + 2.2) * SS, (y + dy + 1.1) * SS],
                     fill=(210, 216, 236, int(110 * a)), outline=(240, 244, 255, int(140 * a)))
    if (f + ph) % 6 < 2:
        _e(addd, x, y - 1, 2.2, 2.2, lit + (al,))


def vehicle(over, addd, x, y, dx, dy, f, a=1.0, hull=(132, 112, 240), bar=cm.HAL_A, glow=cm.HAL_V, ph=0, night=True, part='all'):
    """part: 'light' = street spill + headlights (under the fog), 'body' = hull + light bar (drawn late so
    additive light never washes the hull), 'all' = both."""
    """Corp armoured carrier on the street, heading (dx, dy) unit screen dir."""
    al = int(255 * a)
    L, Wd, Ht = 6.5, 3.0, 3.6
    px, py = -dy, dx
    if py < 0:
        px, py = -px, -py
    if part != 'body':
        _e(addd, x, y + 1, 11, 5.5, glow + (int(80 * a),))
        hx, hy = x + dx * (L + 1), y + dy * (L + 1)
        addd.polygon([(hx * SS, hy * SS), ((hx + dx * 18 + px * 5) * SS, (hy + dy * 18 + py * 5) * SS),
                      ((hx + dx * 18 - px * 5) * SS, (hy + dy * 18 - py * 5) * SS)], fill=(255, 244, 220, int(50 * a)))
        if part == 'light':
            return

    def q(u, v, h):
        return ((x + dx * u + px * v) * SS, (y + dy * u + py * v - h) * SS)
    base = [q(L, -Wd, 0), q(L, Wd, 0), q(-L, Wd, 0), q(-L, -Wd, 0)]
    roof = [q(L * 0.7, -Wd * 0.85, Ht), q(L * 0.7, Wd * 0.85, Ht), q(-L, Wd * 0.85, Ht), q(-L, -Wd * 0.85, Ht)]
    over.polygon([base[1], base[2], roof[2], roof[1]], fill=tuple(int(v * 0.6) for v in hull) + (al,))
    over.polygon([base[0], base[1], roof[1], roof[0]], fill=tuple(int(v * 0.8) for v in hull) + (al,))
    over.polygon([base[1], base[2], roof[2], roof[1]], outline=(8, 6, 14, al))
    over.polygon([base[0], base[1], roof[1], roof[0]], outline=(8, 6, 14, al))
    over.polygon(roof, fill=hull + (al,), outline=(8, 6, 14, al))
    over.polygon([q(L * 0.1, -Wd * 0.5, Ht), q(L * 0.1, Wd * 0.5, Ht), q(-L * 0.6, Wd * 0.5, Ht), q(-L * 0.6, -Wd * 0.5, Ht)], fill=(236, 230, 255, al))
    on = ((f + ph) % 4) < 2
    bx0, by0 = q(-0.6, -Wd * 0.7, Ht + 0.3)
    bx1, by1 = q(-0.6, Wd * 0.7, Ht + 0.3)
    addd.line([(bx0, by0), (bx1, by1)], fill=bar + (al if on else int(90 * a),), width=4)
    if on:
        addd.ellipse([bx0 - 5, by0 - 5, bx0 + 5, by0 + 5], fill=bar + (int(110 * a),))
    else:
        addd.ellipse([bx1 - 5, by1 - 5, bx1 + 5, by1 + 5], fill=bar + (int(110 * a),))


def node(over, addd, x, y, f, a=1.0, warn=0.0):
    """A claimed Cell Site marker on the map: lime uplink pad + beacon (round 20 B, map scale)."""
    al = int(255 * a)
    over.polygon([((x - 7) * SS, y * SS), (x * SS, (y - 3.5) * SS), ((x + 7) * SS, y * SS), (x * SS, (y + 3.5) * SS)],
                 fill=(14, 16, 8, al), outline=LIME + (al,))
    pul = 0.5 + 0.5 * math.sin(f * 0.5)
    _e(addd, x, y, 10, 5, LIME + (int((50 + 50 * pul) * a),))
    over.line([(x * SS, y * SS), (x * SS, (y - 9) * SS)], fill=LIME + (al,), width=2)
    _e(addd, x, y - 9, 2.2, 2.2, LIME + (al,))
    if warn > 0:
        r = 8 + ((f % 10) / 10) * 16
        addd.ellipse([(x - r) * SS, (y - r * 0.5) * SS, (x + r) * SS, (y + r * 0.5) * SS], outline=RED + (int(220 * warn
                                                                                                            * (1 - (f % 10) / 10)),), width=3)


def link(addd, pts, f, a=1.0):
    """The Cell's network link along streets: lime trace + packets."""
    seg = [(x * SS, y * SS) for x, y in pts]
    addd.line(seg, fill=LIME + (int(120 * a),), width=3)
    Ln = cm._plen(pts)
    n = max(1, int(Ln / 22))
    for k in range(n):
        s = (k * Ln / n + f * 2.0) % Ln
        x, y, dx, dy = cm._at(pts, s)
        _e(addd, x, y, 1.8, 1.8, (240, 255, 170, int(255 * a)))


def hud_heat(img, value, band, col, a=1.0, flash=0.0, sub=None):
    """Top-left Heat chip: HEAT <value> // <BAND>, a bar with threshold ticks at 25/50/75."""
    d = ImageDraw.Draw(img, 'RGBA')
    f1 = cm.font(20)
    f2 = cm.font(12, bold=False)
    x0, y0, w, h = 16, 14, 270, 54
    d.polygon([(x0 + 8, y0), (x0 + w, y0), (x0 + w - 8, y0 + h), (x0, y0 + h)], fill=(10, 9, 16, 236))
    d.polygon([(x0 + 8, y0), (x0 + 16, y0), (x0 + 8, y0 + h), (x0, y0 + h)], fill=col + (255,))
    d.text((x0 + 24, y0 + 6), 'HEAT %d' % value, font=f1, fill=(236, 230, 214, 255))
    d.text((x0 + 120, y0 + 6), band, font=f1, fill=col + (255,))
    bx, by, bw = x0 + 24, y0 + 36, w - 48
    d.rectangle([bx, by, bx + bw, by + 7], fill=(36, 32, 46, 255))
    d.rectangle([bx, by, bx + int(bw * value / 100), by + 7], fill=col + (255,))
    for th in (25, 50, 75):
        tx = bx + int(bw * th / 100)
        d.line([(tx, by - 3), (tx, by + 10)], fill=(236, 230, 214, 255), width=1)
    if flash > 0:
        d.polygon([(x0 + 8, y0), (x0 + w, y0), (x0 + w - 8, y0 + h), (x0, y0 + h)], fill=col + (int(150 * flash),))
    if sub:
        d.text((x0 + 4, y0 + h + 8), sub, font=f2, fill=(236, 230, 214, 230))


def banner(img, text, col, a=1.0, y=18, sub=None):
    """A centred warning banner (UI layer, crisp)."""
    d = ImageDraw.Draw(img, 'RGBA')
    f1 = cm.font(22)
    f2 = cm.font(12, bold=False)
    tw = d.textlength(text, font=f1)
    w = tw + 70
    x0 = (cm.W - w) / 2
    al = int(240 * a)
    d.polygon([(x0 + 10, y), (x0 + w, y), (x0 + w - 10, y + 36), (x0, y + 36)], fill=(10, 9, 16, al))
    for k in range(int(w // 14)):
        sx = x0 + k * 14
        d.polygon([(sx, y + 36), (sx + 7, y + 36), (sx + 3, y + 40), (sx - 4, y + 40)], fill=col + (al,))
    d.polygon([(x0 + 10, y), (x0 + 20, y), (x0 + 10, y + 36), (x0, y + 36)], fill=col + (al,))
    d.text((x0 + 34, y + 18), text, font=f1, fill=col + (int(255 * a),), anchor='lm')
    if sub:
        d.text((cm.W / 2, y + 52), sub, font=f2, fill=(236, 230, 214, int(230 * a)), anchor='mm')
