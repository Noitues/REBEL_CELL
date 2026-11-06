"""Round 16: card-play preview A2 (ghost blades).

- every needle gets the SAME full ghost blade with its value window; a small index tab (1, 2, 3) tells them apart;
- the landing slice(s) get a dashed outline;
- the move is a plain trace outside the rim (no arrowheads: they fought the threat ring's red chevrons);
  a solid dot marks where each needle starts, the trace runs to its ghost blade;
- docked drones ride their slice: each gets a dashed ghost drone where it ENDS UP, with its own dashed trace
  on the drone orbit;
- no aim pips, no gates.
A spin of N moves the slices N ticks clockwise: a needle lands at (pointer - 12N), a drone ends at (drone + 12N).
"""
import math
from PIL import Image, ImageDraw
from frames import P, Q, layer, add_glow, over_pil, INK
from slicelib import R_OUT, R_IN, PROGRAMS, f_num, f_ui, glyph_rgba
import frames as F
from preview15 import dashed_poly, ghost_value

WHITE = (255, 255, 255)


def arc_pts(r, a0, a1, ss, step=1.0):
    n = max(2, int(abs(a1 - a0) / step))
    return [P(r, a0 + (a1 - a0) * k / n, ss) for k in range(n + 1)]


def ghost_blade(im, d, gd, ss, a_l, RA, top, ps, L, pc, idx, n_needles):
    sh = RA + 18 * ps
    pts = [Q(R_OUT - 24, 0, a_l, ss), Q(sh, 34 * ps, a_l, ss), Q(top, 50 * ps, a_l, ss), Q(top, -50 * ps, a_l, ss), Q(sh, -34 * ps, a_l, ss)]
    fill = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(fill).polygon(pts, fill=WHITE + (60,))
    im.alpha_composite(fill)
    d = ImageDraw.Draw(im)
    gd.polygon(pts, outline=WHITE + (200,), width=int(8 * ss))
    dashed_poly(d, pts, WHITE + (255,), int(4 * ss), dash=12 * ss, gap=7 * ss)
    w0, w1 = RA + 30 * ps, top - 18 * ps
    wpts = [Q(w0, -36 * ps, a_l, ss), Q(w0, 36 * ps, a_l, ss), Q(w1, 36 * ps, a_l, ss), Q(w1, -36 * ps, a_l, ss)]
    d.polygon(wpts, fill=(12, 12, 18, 215), outline=pc + (255,), width=int(2.4 * ss))
    cx, cy = Q((w0 + w1) / 2, 0, a_l, ss)
    txt = str(L["value"]) if L["value"] is not None else None
    ghost_value(im, d, ss, cx, cy, (w1 - w0) * 0.9, txt, L, pc)
    if n_needles > 1:  # index tab on the blade's shoulder
        tx, ty = Q(sh + 4 * ps, 0, a_l, ss)
        r = 12 * ss * ps
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=WHITE + (255,), outline=INK + (255,), width=int(2 * ss))
        f = f_num(int(r * 1.5))
        s = str(idx)
        d.text((tx - f.getlength(s) / 2, ty - r * 0.95), s, font=f, fill=INK + (255,))
    return d


def draw(canvas, spec, Ls, ss, pv, ptrs, RA, top, ps, index_at, acc):
    im, d = layer(ss)
    gl, gd = layer(ss)
    N = pv["moves"]
    R_tr = RA + 50
    for k, a_p in enumerate(ptrs):
        a_l = a_p - 12 * N
        L = Ls[index_at(spec, a_l)]
        pc = PROGRAMS[L["prog"]]["col"]
        wp = F.wedge_pts(L["a0"] + 1.2, L["a0"] + L["span"] - 1.2, R_IN + 4, R_OUT - 4, ss, 50)
        gd.polygon(wp, outline=pc + (255,), width=int(10 * ss))
        dashed_poly(d, wp, pc + (255,), int(4.5 * ss), dash=12 * ss, gap=8 * ss)
        pts = arc_pts(R_tr, a_p, a_l, ss)
        gd.line(pts, fill=WHITE + (150,), width=int(8 * ss))
        d.line(pts, fill=WHITE + (235,), width=int(3.5 * ss))
        x, y = P(R_tr, a_p, ss)
        r = 6 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE + (255,), outline=INK + (255,), width=int(2 * ss))
        d = ghost_blade(im, d, gd, ss, a_l, RA, top, ps, L, pc, k + 1, len(ptrs))
    # docked drones ride their slice: dashed ghost drone at the end position + a dashed trace on the drone orbit
    R_dr = RA + 74
    for a_d, dr in zip(spec.get("drone_angles", []), spec.get("drones", [])):
        a_e = a_d + 12 * N
        pts = arc_pts(R_dr, a_d, a_e, ss)
        dashed_poly(d, pts, acc + (255,), int(3 * ss), dash=10 * ss, gap=7 * ss, closed=False)
        x, y = P(R_dr, a_e, ss)
        r = 46 * ss
        circ = [(x + r * math.cos(math.radians(j * 6)), y + r * math.sin(math.radians(j * 6))) for j in range(60)]
        fill = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(fill).ellipse([x - r, y - r, x + r, y + r], fill=acc + (50,))
        im.alpha_composite(fill)
        d = ImageDraw.Draw(im)
        dashed_poly(d, circ, acc + (255,), int(3.5 * ss), dash=10 * ss, gap=6 * ss)
        g = glyph_rgba("DRONE", int(46 * ss), 2 * ss)
        g.putalpha(g.split()[3].point(lambda v: int(v * 0.55)))
        im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        f = f_ui(int(15 * ss), b"Bold SemiCondensed")
        s = "%s ENDS HERE" % dr["name"].upper()
        tw = f.getlength(s)
        d.rounded_rectangle([x - tw / 2 - 8 * ss, y + r + 4 * ss, x + tw / 2 + 8 * ss, y + r + 26 * ss], radius=5 * ss,
                            fill=(12, 10, 18, 235), outline=acc + (255,), width=int(2 * ss))
        d.text((x - tw / 2, y + r + 6 * ss), s, font=f, fill=acc + (255,))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)
