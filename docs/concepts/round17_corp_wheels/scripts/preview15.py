"""Round 15: card-play preview, option A (ghost blade), revised.

- every pointer gets its own ghost (primary: ghost blade, extra readers: ghost pin) at its landing tick;
- the landing slice(s) get a dashed outline;
- the move is traced OUTSIDE the rim with arrowheads every 18 deg showing direction;
- no aim pips;
- a docked drone at a landing tick: the ghost collapses to an in-rim ghost pin, the drone gets a dashed
  'lands here' ring and the ghost value hangs under the drone as a tag;
- future: gates on the trace radius; the trace lights where it passes THROUGH a gate.
A spin of N moves the slices N ticks clockwise, so each pointer's landing is at (pointer - 12N) on the
current wheel; the trace runs from the pointer to that landing.
"""
import math
from PIL import Image, ImageDraw
from frames import P, Q, layer, add_glow, over_pil, INK
from slicelib import R_OUT, R_IN, PROGRAMS, f_num, f_ui, f_mono, glyph_rgba
import frames as F

GOLD = (255, 205, 90)


def dashed_poly(d, pts, col, w, dash=8, gap=6, closed=True):
    seq = pts + ([pts[0]] if closed else [])
    period = dash + gap
    cum = 0.0
    for (xa, ya), (xb, yb) in zip(seq[:-1], seq[1:]):
        L = math.hypot(xb - xa, yb - ya)
        n = max(1, int(L / 1.5))
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            if (cum + L * (t0 + t1) / 2) % period < dash:
                d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)], fill=col, width=w)
        cum += L


def norm(a):
    return a % 360


def on_arc(a, a_from, a_to):
    """Is angle a on the arc going from a_from to a_to anticlockwise (decreasing angle)?"""
    span = (a_from - a_to) % 360
    return (a_from - a) % 360 <= span


def arrow_head(d, ss, r, a, direction, col, size=9):
    tip = P(r, a + direction * 2.2, ss)
    b1 = P(r + size, a - direction * 1.2, ss)
    b2 = P(r - size, a - direction * 1.2, ss)
    d.polygon([tip, b1, b2], fill=col)


def draw(canvas, spec, Ls, ss, pv, ptrs, RA, top, ps, index_at, glyph_name):
    im, d = layer(ss)
    gl, gd = layer(ss)
    N = pv["moves"]
    R_tr = RA + 52
    drone_angles = [norm(a) for a in spec.get("drone_angles", [])]
    gates = pv.get("gates", [])
    lit_gates = set()
    for k, a_p in enumerate(ptrs):
        a_l = a_p - 12 * N
        L = Ls[index_at(spec, a_l)]
        pc = PROGRAMS[L["prog"]]["col"]
        # dashed landing slice
        wp = F.wedge_pts(L["a0"] + 1.2, L["a0"] + L["span"] - 1.2, R_IN + 4, R_OUT - 4, ss, 50)
        gd.polygon(wp, outline=pc + (255,), width=int(10 * ss))
        dashed_poly(d, wp, pc + (255,), int(4.5 * ss), dash=12 * ss, gap=8 * ss)
        # trace outside the rim, pointer -> landing, arrows along it
        direction = -1 if N > 0 else 1
        steps = max(8, int(abs(12 * N) / 1.2))
        pts = [P(R_tr, a_p + (a_l - a_p) * j / steps, ss) for j in range(steps + 1)]
        gd.line(pts, fill=(255, 255, 255, 170), width=int(8 * ss))
        d.line(pts, fill=(255, 255, 255, 235), width=int(3.5 * ss))
        a = a_p + direction * 9
        while (a - a_l) * direction < -6:
            arrow_head(d, ss, R_tr, a, direction, (255, 255, 255, 255), 8)
            a += direction * 18
        arrow_head(d, ss, R_tr, a_l + 0.0, direction, pc + (255,), 13)
        x, y = P(R_tr, a_p, ss)
        r = 6 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255), outline=INK + (255,), width=int(2 * ss))
        for gi, gate in enumerate(gates):
            ga, glabel = gate[0], gate[1]
            crossed = ((a_p - ga) % 360 <= 12 * N) if N > 0 else ((ga - a_p) % 360 <= -12 * N)
            if crossed:
                lit_gates.add(gi)
                seg = [P(R_tr, ga + j * 0.5, ss) for j in range(-12, 13)]
                gd.line(seg, fill=GOLD + (255,), width=int(16 * ss))
                d.line(seg, fill=GOLD + (255,), width=int(6 * ss))
        # ghost: primary = ghost blade; extra readers or a drone in the way = in-rim ghost pin
        drone_here = any(abs(((norm(a_l) - da + 180) % 360) - 180) < 8 for da in drone_angles)
        txt = str(L["value"]) if L["value"] is not None else None
        if k == 0 and not drone_here:
            sh = RA + 18 * ps
            pts = [Q(R_OUT - 24, 0, a_l, ss), Q(sh, 34 * ps, a_l, ss), Q(top, 50 * ps, a_l, ss), Q(top, -50 * ps, a_l, ss), Q(sh, -34 * ps, a_l, ss)]
            fill = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(fill).polygon(pts, fill=(255, 255, 255, 60))
            im.alpha_composite(fill)
            d = ImageDraw.Draw(im)
            gd.polygon(pts, outline=(255, 255, 255, 200), width=int(8 * ss))
            dashed_poly(d, pts, (255, 255, 255, 255), int(4 * ss), dash=12 * ss, gap=7 * ss)
            w0, w1 = RA + 30 * ps, top - 18 * ps
            wpts = [Q(w0, -36 * ps, a_l, ss), Q(w0, 36 * ps, a_l, ss), Q(w1, 36 * ps, a_l, ss), Q(w1, -36 * ps, a_l, ss)]
            d.polygon(wpts, fill=(12, 12, 18, 210), outline=pc + (255,), width=int(2.4 * ss))
            cx, cy = Q((w0 + w1) / 2, 0, a_l, ss)
            ghost_value(im, d, ss, cx, cy, (w1 - w0) * 0.9, txt, L, pc)
        else:
            pin = [Q(R_OUT - 24, 0, a_l, ss), Q(R_OUT + 2, 20 * ps, a_l, ss), Q(RA - 26, 22 * ps, a_l, ss), Q(RA - 26, -22 * ps, a_l, ss), Q(R_OUT + 2, -20 * ps, a_l, ss)]
            fill = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(fill).polygon(pin, fill=(255, 255, 255, 60))
            im.alpha_composite(fill)
            d = ImageDraw.Draw(im)
            dashed_poly(d, pin, (255, 255, 255, 255), int(3.5 * ss), dash=10 * ss, gap=6 * ss)
            cx, cy = Q(R_OUT + 20, 0, a_l, ss)
            r = 19 * ss * ps
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(12, 12, 18, 220), outline=pc + (255,), width=int(2.4 * ss))
            ghost_value(im, d, ss, cx, cy, r * 1.7, txt, L, pc)
            if drone_here:  # the drone keeps its dock; it gets a 'lands here' ring and the value tag
                dx, dy = P(RA + 74, a_l, ss)
                rr = 58 * ss
                dashed_poly(d, [(dx + rr * math.cos(math.radians(j * 6)), dy + rr * math.sin(math.radians(j * 6))) for j in range(60)],
                            pc + (255,), int(4 * ss), dash=10 * ss, gap=6 * ss)
                tx, ty = P(RA + 74 + 82, a_l, ss)
                f = f_num(int(26 * ss))
                s = "%s %s" % (L["prog"], txt or "")
                tw = f.getlength(s)
                d.rounded_rectangle([tx - tw / 2 - 12 * ss, ty - 18 * ss, tx + tw / 2 + 12 * ss, ty + 18 * ss], radius=8 * ss,
                                    fill=(12, 10, 18, 240), outline=pc + (255,), width=int(2.5 * ss))
                d.text((tx - tw / 2, ty - 16 * ss), s, font=f, fill=(255, 255, 255, 255))
    for gi, gate in enumerate(gates):  # future: gates
        ga, glabel = gate[0], gate[1]
        la = gate[2] if len(gate) > 2 else ga
        lit = gi in lit_gates
        col = GOLD if lit else (130, 130, 140)
        for side in (-3.2, 3.2):
            d.line([P(R_tr - 16, ga + side, ss), P(R_tr + 16, ga + side, ss)], fill=INK + (255,), width=int(8 * ss))
            d.line([P(R_tr - 16, ga + side, ss), P(R_tr + 16, ga + side, ss)], fill=col + (255,), width=int(4.5 * ss))
        d.line([P(R_tr + 16, ga - 3.6, ss), P(R_tr + 16, ga + 3.6, ss)], fill=col + (255,), width=int(5 * ss))
        x, y = P(R_tr + 70, la, ss)
        f = f_ui(int(17 * ss), b"Bold SemiCondensed")
        s1 = ("PASSES THROUGH GATE: " if lit else "GATE (not crossed): ") + glabel
        s2 = "future: gates"
        w = max(f.getlength(s1), f.getlength(s2)) + 20 * ss
        x0 = x - w / 2
        d.rounded_rectangle([x0, y - 22 * ss, x0 + w, y + 24 * ss], radius=6 * ss, fill=(14, 12, 20, 235), outline=col + (255,), width=int(2 * ss))
        d.text((x0 + 10 * ss, y - 20 * ss), s1, font=f, fill=col + (255,))
        d.text((x0 + 10 * ss, y + 1 * ss), s2, font=f_mono(int(14 * ss), False), fill=(190, 190, 205, 255))
        if lit:
            gd.ellipse([P(R_tr, ga, ss)[0] - 26 * ss, P(R_tr, ga, ss)[1] - 26 * ss, P(R_tr, ga, ss)[0] + 26 * ss, P(R_tr, ga, ss)[1] + 26 * ss], fill=GOLD + (255,))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)


def ghost_value(im, d, ss, cx, cy, h, txt, L, pc):
    if txt:
        f = f_num(int(h * 0.95))
        tw = f.getlength(txt)
        d.text((cx - tw / 2, cy - h * 0.6), txt, font=f, fill=pc + (255,), stroke_width=int(1.5 * ss), stroke_fill=INK + (255,))
    else:
        from roster_wheel import SPECIAL_GLYPH
        g = glyph_rgba(SPECIAL_GLYPH.get(L["special"]) or L["prog"], int(h * 0.8), 2 * ss)
        im.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
