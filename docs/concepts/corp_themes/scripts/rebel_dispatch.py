"""REBEL_CELL "THREE LINES, ONE CLOCK", DISPATCH view stills (1920 x 1080).

Over the hq_rebel_cell v3 plates (read only; OVERVIEW and DECISION cameras). Room anchors are read off the composed
v3 stills (the plates have no room json) and stored below in the 2000 px wide preview frame (x0.96 -> 1920).
Three ribbons (ROOF dotted, STREET solid, SEWER dashed) run only in the gaps between rooms, converge on the kill-switch
column and the MAINFRAME target (DISPATCH red). Cards sit only in the left / right margins, outside every room hull.
Stills: B01_plan, B02_hover_roof, B03_live_out_of_step, B04_in_step_f0, B05_briefing, B06_greyscale (pattern proof).
Run:  python rebel_dispatch.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import theme_lib as T

W, H = T.W, T.H
RC = os.path.join(T.ROUTE, "hq_rebel_cell", "plates")
K = 0.96                                   # preview px -> 1920 px
PINK, CYAN, GREEN = (255, 80, 170), (60, 220, 255), (80, 255, 130)       # lane accents (thin edge lines and tokens only)
RED = (232, 20, 30)                         # Cell red / DISPATCH red
LIME, ORANGE, WHITE, GREY = (150, 255, 70), (255, 150, 30), (235, 235, 245), (140, 140, 150)
LANES = ("ROOF", "STREET", "SEWER")
ACC = {"ROOF": PINK, "STREET": CYAN, "SEWER": GREEN}
PAT = {"ROOF": "dotted", "STREET": "solid", "SEWER": "dashed"}

# preview-frame anchors (x, y). Each lane: rooms in step order, then the switch-column x (shaft) and target.
VIEWS = {
    "overview": dict(plate="H_overview_v3_plate.png",
                     ROOF=[(715, 452), (895, 368), (1035, 358), (1200, 440), (1458, 412)],
                     STREET=[(510, 608), (735, 600), (970, 600), (1205, 600), (1445, 600)],
                     SEWER=[(728, 760), (915, 815), (1045, 815), (1200, 762), (1452, 760)],
                     shaft=1568, target=(1708, 528), half=(66, 30)),
    "decision": dict(plate="H_decision_v3_plate.png",
                     ROOF=[(757, 430), (1000, 315), (1180, 300), (1400, 412), (1740, 372)],
                     STREET=[(480, 640), (775, 628), (1080, 628), (1385, 625), (1700, 610)],
                     SEWER=[(767, 833), (1010, 908), (1175, 905), (1390, 835), (1715, 835)],
                     shaft=1905, target=(2030, 540), half=(78, 36)),
}


def pt(p):
    return (p[0] * K, p[1] * K)


def trim(a, b, ha, hb):
    """Shorten the segment a->b by the room half-box at each end (so a ribbon never crosses a room face)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    n = np.hypot(dx, dy) + 1e-6
    ux, uy = dx / n, dy / n

    def cut(h):
        tx = h[0] / (abs(ux) + 1e-6)
        ty = h[1] / (abs(uy) + 1e-6)
        return min(tx, ty) + 6

    ca, cb = cut(ha), cut(hb)
    if ca + cb >= n - 4:
        return None
    return (ax + ux * ca, ay + uy * ca), (bx - ux * cb, by - uy * cb)


def node_cols(state, lane, i, pos):
    """walked / current / next / ahead / past colour for room i of a lane given the lane's current index."""
    if i < pos:
        return LIME
    if i == pos:
        return LIME
    if i == pos + 1:
        return ORANGE
    return WHITE


def draw_view(view, pos, hover=None, state="plan", beat=0.0, out_of_step=None):
    """RGBA layer (supersampled) with ribbons, pins, tokens, switches, shaft, target, ruler."""
    V = VIEWS[view]
    S = L.SS
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    hx, hy = V["half"]
    shaft = V["shaft"] * K
    for lane in LANES:
        pts = [pt(p) for p in V[lane]]
        rp = [(x + 55 * K, y + 5 * K) for x, y in pts]
        accent = ACC[lane]
        f = 1.0 if hover in (None, lane) else 0.35
        for i in range(len(pts) - 1):
            seg = trim(rp[i], rp[i + 1], (hx * K, hy * K), (hx * K, hy * K))
            if seg is None:
                continue
            col = LIME if i < pos[lane] else (ORANGE if i == pos[lane] else (WHITE if i == pos[lane] + 1 else GREY))
            if i > pos[lane]:
                col = (WHITE if i == pos[lane] + 1 else GREY)
            a = int(235 * f) if i >= pos[lane] else int(255 * f)
            (x0, y0), (x1, y1) = seg
            # thin lane accent edge, offset 4 px, then the patterned ribbon in the route colour
            ox, oy = (y1 - y0), -(x1 - x0)
            n = np.hypot(ox, oy) + 1e-6
            ox, oy = ox / n * 5, oy / n * 5
            d.line([((x0 + ox) * S, (y0 + oy) * S), ((x1 + ox) * S, (y1 + oy) * S)], fill=accent + (int(150 * f),), width=S)
            T.pattern_line(d, [(x0, y0), (x1, y1)], col + (a,), 4 if PAT[lane] != "dotted" else 4, PAT[lane], dot=(4, 11), dash=(14, 7))
        # convergence: last room -> switch glyph on the shaft
        lx, ly = rp[-1]
        sx = (shaft, ly)
        seg = trim((lx, ly), sx, (hx * K, hy * K), (4, 4))
        if seg:
            T.pattern_line(d, [seg[0], seg[1]], RED + (int(230 * f),), 3, PAT[lane], dot=(4, 11), dash=(14, 7))
        # pins (route kit look: ring + dot), tokens on the lane's current room
        for i, p in enumerate(pts):
            cx, cy = p
            col = LIME if i <= pos[lane] else (ORANGE if i == pos[lane] + 1 else (WHITE if i == pos[lane] + 2 or True else GREY))
            if i < pos[lane] - 0:
                col = LIME
            r = 13
            d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(10, 14, 16, int(235 * f)), outline=col + (int(255 * f),), width=3 * S)
        cx, cy = pts[pos[lane]]
        d.ellipse([(cx - 22) * S, (cy - 22) * S, (cx + 22) * S, (cy + 22) * S], outline=accent + (int(255 * f),), width=3 * S)
        T.text(d, cx, cy, lane[0], 17, accent + (int(255 * f),), "mm")
        # switch glyph on the shaft
        lit = state in ("ready", "thrown")
        sw = 16
        d.rectangle([(shaft - sw) * S, (ly - sw) * S, (shaft + sw) * S, (ly + sw) * S], fill=(24, 4, 8, 240),
                    outline=RED + (255,), width=3 * S)
        if lit:
            d.rectangle([(shaft - sw + 5) * S, (ly - sw + 5) * S, (shaft + sw - 5) * S, (ly + sw - 5) * S], fill=(255, 235, 235, 255))
        T.text(d, shaft + 28, ly, "SW", 14, RED + (255,), "lm")
    # the shaft: a vertical line joining the three switches, then the arrow to the target
    ys = [pt(V[l][-1])[1] for l in LANES]
    d.line([(shaft * S, min(ys) * S), (shaft * S, max(ys) * S)], fill=RED + (255,), width=3 * S)
    tx, ty = pt(V["target"])
    mid = sum(ys) / 3
    if tx < W:
        T.pattern_line(d, [(shaft, ys[1]), (tx - 40, ty)], RED + (255,), 4, "dashed", dash=(14, 7))
        d.ellipse([(tx - 40) * S, (ty - 40) * S, (tx + 40) * S, (ty + 40) * S], outline=RED + (255,), width=5 * S)
        T.chipbox(d, tx - 40, ty + 62, "MAINFRAME  DISPATCH", RED + (255,), 14, anchor="lm", fill=(20, 4, 8, 235))
    else:
        d.polygon([((shaft + 4) * S, (ys[1] - 6) * S), ((shaft + 30) * S, ys[1] * S), ((shaft + 4) * S, (ys[1] + 6) * S)], fill=RED + (255,))
        T.chipbox(d, shaft - 150, ys[1] - 52, "TO MAINFRAME", RED + (255,), 14, anchor="lm", fill=(20, 4, 8, 235))
    return lay, V


def ruler(d, V, cur, laggard=None):
    """Step ruler above the roof lane: one tick per step column (columns taken from the street lane x)."""
    S = L.SS
    cols = [pt(p)[0] for p in V["STREET"]]
    ytop = min(pt(p)[1] for p in V["ROOF"]) - 74
    d.line([(cols[0] * S, ytop * S), ((V["shaft"] * K) * S, ytop * S)], fill=(210, 215, 225, 230), width=S)
    for i, x in enumerate(cols):
        lag = laggard is not None and i == laggard
        d.line([(x * S, (ytop - 8) * S), (x * S, (ytop + 8) * S)], fill=(255, 220, 120, 255) if lag else (210, 215, 225, 230), width=(3 if lag else 1) * S)
        T.text(d, x, ytop - 22, str(i + 1), 15, (255, 220, 120, 255) if lag else (215, 220, 230, 255), "mm")
    if laggard is not None:
        x = cols[laggard]
        d.rectangle([(x - 26) * S, (ytop - 36) * S, (x + 26) * S, (ytop + 14) * S], outline=(255, 220, 120, 200), width=S)
        # the lagging column: a hairline down through the gaps
        T.pattern_line(d, [(x, ytop + 14), (x, ytop + 480)], (255, 220, 120, 110), 1, "dashed", dash=(6, 10))
    T.text(d, cols[0] - 20, ytop - 22, "STEP", 14, (190, 200, 210, 255), "rm")


def lane_tags(d, V, hover=None):
    S = L.SS
    for lane in LANES:
        y = pt(V[lane][0])[1]
        f = 1.0 if hover in (None, lane) else 0.4
        x0, x1 = 28, 28 + 220 * 0.84
        d.rectangle([x0 * S, (y - 20) * S, x1 * S, (y + 20) * S], fill=(8, 10, 14, int(225 * f)), outline=ACC[lane] + (int(255 * f),), width=2 * S)
        T.pattern_line(d, [(x0 + 10, y), (x0 + 56, y)], ACC[lane] + (int(255 * f),), 3, PAT[lane], dot=(3, 9), dash=(12, 6))
        T.text(d, x0 + 66, y, lane, 17, (240, 244, 250, int(255 * f)))


def sync_ring(d, cx, cy, r, offs):
    """SYNC RING: ring with 3 pips; offs = angular offsets (deg) of the roof / street / sewer pips from 12 o'clock."""
    S = L.SS
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=(200, 205, 215, 255), width=2 * S)
    d.line([(cx * S, (cy - r - 8) * S), (cx * S, (cy - r + 4) * S)], fill=(255, 255, 255, 255), width=2 * S)
    for lane, o in zip(LANES, offs):
        a = np.radians(90 - o)
        px, py = cx + r * np.cos(a), cy - r * np.sin(a)
        d.ellipse([(px - 6) * S, (py - 6) * S, (px + 6) * S, (py + 6) * S], fill=ACC[lane] + (255,), outline=(255, 255, 255, 255), width=S)


def card_left(d, state, offs, hover=None, pos=None):
    S = L.SS
    x0, y0, x1, y1 = 22, 88, 300, 388
    T.panel(d, (x0, y0, x1, y1), fill=(6, 8, 12, 178), outline=(150, 155, 170, 230))
    T.triline(d, x0 + 14, y0 + 26, 34, RED + (255,), 2)
    T.text(d, x0 + 62, y0 + 26, "DISPATCH VIEW", 19, (245, 245, 250, 255))
    T.text(d, x0 + 14, y0 + 58, "THREE LINES, ONE CLOCK", 13, (170, 175, 190, 255))
    sync_ring(d, x0 + 70, y0 + 128, 38, offs)
    st = {"plan": "PLAN", "hover": "HOVER", "live": "OUT OF STEP", "ready": "IN STEP", "thrown": "THROWN"}[state]
    T.text(d, x0 + 130, y0 + 110, "SYNC", 15, (170, 175, 190, 255))
    T.text(d, x0 + 130, y0 + 136, st, 20, RED + (255,) if state in ("live",) else (245, 245, 250, 255))
    for k, lane in enumerate(LANES):
        y = y0 + 205 + k * 30
        d.rectangle([(x0 + 14) * S, (y - 12) * S, (x0 + 30) * S, (y + 12) * S], fill=ACC[lane] + (255,))
        T.text(d, x0 + 42, y, lane, 14, (230, 232, 240, 255))
        # HP / RAM gauge slots (per operative, reserved)
        d.rectangle([(x0 + 112) * S, (y - 9) * S, (x0 + 252) * S, (y - 1) * S], outline=(120, 125, 140, 255), width=S)
        d.rectangle([(x0 + 113) * S, (y - 8) * S, (x0 + 113 + 100 + 12 * k) * S, (y - 2) * S], fill=(120, 220, 140, 230))
        d.rectangle([(x0 + 112) * S, (y + 3) * S, (x0 + 252) * S, (y + 11) * S], outline=(120, 125, 140, 255), width=S)
        d.rectangle([(x0 + 113) * S, (y + 4) * S, (x0 + 113 + 70 + 18 * k) * S, (y + 10) * S], fill=(120, 170, 255, 230))


def legend_row(d):
    S = L.SS
    y = 1042
    x = 560
    T.panel(d, (540, 1020, 1380, 1062), fill=(6, 8, 12, 190), outline=(110, 115, 130, 220))
    for lane in LANES:
        T.pattern_line(d, [(x, y), (x + 46, y)], ACC[lane] + (255,), 4, PAT[lane], dot=(4, 11), dash=(14, 7))
        T.text(d, x + 56, y, lane, 16, (235, 238, 245, 255))
        x += 170
    T.text(d, x + 10, y, "ribbons run in the gaps; rooms keep their own colours", 14, (170, 175, 190, 255))


def finish(view, name, pos, hover=None, state="plan", offs=(0, 0, 0), laggard=None, extras=None, fade_world=0.0, legend=True):
    plate = T.load_rgb(os.path.join(RC, VIEWS[view]["plate"]))
    m0 = L.metrics(plate)
    lay, V = draw_view(view, pos, hover, state)
    d = ImageDraw.Draw(lay)
    ruler(d, V, pos, laggard)
    lane_tags(d, V, hover)
    out = T.flat(plate, lay)
    mt = L.metrics(out)
    lay2 = T.canvas()
    d2 = ImageDraw.Draw(lay2)
    card_left(d2, state, offs, hover, pos)
    if legend:
        legend_row(d2)
    if extras:
        extras(d2, V)
    out = T.flat(out, lay2)
    T.save(out, os.path.join(T.out_dir("rebel_cell"), name + ".png"))
    return dict(plate_clean=m0, plate_with_theme=mt, still=L.metrics(out))


def shaft_beat(img_fn, V, f):
    pass


def beat_layer(V, sweep):
    """Switch-lamp flash on frame 0 and the glow sweep rising up the shaft (0..1)."""
    S = L.SS
    shaft = V["shaft"] * K
    ys = [pt(V[l][-1])[1] for l in LANES]
    ytop, ybot = min(ys) - 60, max(ys) + 60
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    for y in ys:
        for r, a in ((46, 60), (30, 110), (18, 200)):
            d.ellipse([(shaft - r) * S, (y - r) * S, (shaft + r) * S, (y + r) * S], fill=(255, 70, 80, a))
    yy = ybot - (ybot - ytop) * sweep
    d.rectangle([(shaft - 10) * S, yy * S, (shaft + 10) * S, ybot * S], fill=(255, 60, 70, 90))
    d.rectangle([(shaft - 4) * S, yy * S, (shaft + 4) * S, ybot * S], fill=(255, 150, 150, 160))
    return lay


def main(which="all"):
    res = {}

    def run(name, *a, **k):
        if which != "all" and name not in which:
            return
        res[name] = finish(*a, **k)
        print(name, res[name], flush=True)

    pos_plan = dict(ROOF=0, STREET=0, SEWER=0)
    run("B01_plan", "overview", "B01_plan", pos_plan, None, "plan", (0, 0, 0))
    run("B02_hover_roof", "overview", "B02_hover_roof", dict(ROOF=2, STREET=2, SEWER=2), "ROOF", "hover", (0, 0, 0))
    run("B03_live_out_of_step", "decision", "B03_live_out_of_step", dict(ROOF=2, STREET=1, SEWER=2), None, "live", (0, 58, 0), laggard=1)

    if which == "all" or "B04_in_step_f0" in which:
        pos = dict(ROOF=2, STREET=2, SEWER=2)
        plate = T.load_rgb(os.path.join(RC, VIEWS["overview"]["plate"]))
        lay, V = draw_view("overview", pos, None, "ready")
        d = ImageDraw.Draw(lay)
        ruler(d, V, pos, None)
        lane_tags(d, V)
        out = T.flat(plate, lay)
        out = T.flat(out, beat_layer(V, 0.35))
        mt = L.metrics(out)
        lay2 = T.canvas()
        d2 = ImageDraw.Draw(lay2)
        card_left(d2, "ready", (0, 0, 0))
        legend_row(d2)
        T.chipbox(d2, 1580 * K, 960 * K, "SWITCHES READY  f0", RED + (255,), 16, anchor="lm", fill=(20, 4, 8, 235))
        out = T.flat(out, lay2)
        T.save(out, os.path.join(T.out_dir("rebel_cell"), "B04_in_step_f0.png"))
        res["B04_in_step_f0"] = dict(plate_with_theme=mt, still=L.metrics(out))
        print("B04", res["B04_in_step_f0"], flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else "all")


def briefing_strip(d2, V):
    """B05: the pre-launch 2D briefing. A strip over the dark undercroft (below every lane), outside all room hulls."""
    S = L.SS
    x0, y0, x1, y1 = 330, 876, 1590, 1060
    T.panel(d2, (x0, y0, x1, y1), fill=(5, 7, 11, 215), outline=(150, 155, 170, 235))
    T.triline(d2, x0 + 14, y0 + 22, 30, RED + (255,), 2)
    T.text(d2, x0 + 54, y0 + 22, "BRIEFING  //  ASSIGN THREE OPERATIVES  //  ARRIVE ON ONE STEP", 16, (245, 245, 250, 255))
    cls = {"ROOF": "BREAKER", "STREET": "GHOST", "SEWER": "RIGGER"}
    cw = 330
    for k, lane in enumerate(LANES):
        cx = x0 + 18 + k * (cw + 18)
        cy = y0 + 46
        d2.rectangle([cx * S, cy * S, (cx + cw) * S, (y1 - 12) * S], fill=(10, 12, 18, 235), outline=ACC[lane] + (255,), width=2 * S)
        d2.ellipse([(cx + 12) * S, (cy + 12) * S, (cx + 52) * S, (cy + 52) * S], outline=ACC[lane] + (255,), width=3 * S)
        T.text(d2, cx + 32, cy + 32, cls[lane][0], 20, ACC[lane] + (255,), "mm")
        T.text(d2, cx + 64, cy + 22, lane + "  LANE", 16, (240, 244, 250, 255))
        T.text(d2, cx + 64, cy + 44, "OPERATIVE  " + cls[lane], 13, (170, 175, 190, 255))
        T.pattern_line(d2, [(cx + 210, cy + 22), (cx + 310, cy + 22)], ACC[lane] + (255,), 4, PAT[lane], dot=(4, 11), dash=(14, 7))
        for j, (nm, w, col) in enumerate((("HP", 0.85 - 0.1 * k, (120, 220, 140)), ("RAM", 0.7 + 0.08 * k, (120, 170, 255)))):
            yy = cy + 68 + j * 18
            T.text(d2, cx + 12, yy, nm, 12, (170, 175, 190, 255))
            d2.rectangle([(cx + 52) * S, (yy - 5) * S, (cx + 250) * S, (yy + 5) * S], outline=(120, 125, 140, 255), width=S)
            d2.rectangle([(cx + 53) * S, (yy - 4) * S, (cx + 53 + 196 * w) * S, (yy + 4) * S], fill=col + (230,))
        T.text(d2, cx + 262, cy + 80, "SW %d" % (k + 1), 15, RED + (255,))
        T.text(d2, cx + 262, cy + 98, "STEP 5", 13, (200, 205, 215, 255))
    T.chipbox(d2, x1 - 4, y0 - 20, "LAUNCH: HQ NETRUN", RED + (255,), 16, anchor="rm", fill=(20, 4, 8, 240))


def extra_outputs():
    od = T.out_dir("rebel_cell")
    r = finish("overview", "B05_briefing", dict(ROOF=0, STREET=0, SEWER=0), None, "plan", (0, 0, 0), extras=briefing_strip, legend=False)
    print("B05", r, flush=True)
    a = np.asarray(Image.open(os.path.join(od, "B01_plan.png")).convert("L"), np.float32) / 255.0
    T.save(np.stack([a, a, a], -1), os.path.join(od, "B06_greyscale.png"))


if __name__ == "__main__" and len(sys.argv) <= 1:
    extra_outputs()
