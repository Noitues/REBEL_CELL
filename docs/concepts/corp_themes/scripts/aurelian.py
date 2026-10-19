"""Aurelian Concord THE RING stills (1920 x 1080): R_pending, R_active, R_ring2_breached, R_lost (2D raid-map mocks over the
Grid capture) and H_overview_gates, H_overview_gates_step (HQ overview v2 plate with the rotating gate rings as overlay arcs).

Rules used (themes/aurelian.md "Art answers"): raid rings centre on the DEFENDED node; 4 rings, one gate per ring, 3
key-carrier threats hold the keys (INTEL, BREACH, VIRUS); a breached ring means its gate is open and threats pass inward.
HQ: the gate is a lit window on a ring-edge line (B-ROT), driven by gate_tick_now / gate_tick_next (tick x 12 deg); the
next position shows as a pencil-yellow ghost. Palette: gilt #C9A35A world lines, verdigris #29DBA6 on the raid map only
as thin ring strokes, Exploit gold for key icons. Ring strokes sit under every pin (matte = pin protect + 6 px).
Run:  python aurelian.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import solace_lib as L
import theme_lib as T

W, H = T.W, T.H
CORP = "aurelian"
GILT = (201, 163, 90)
VERD = (41, 219, 166)
GOLD = (255, 205, 70)
PENCIL = (255, 235, 90)
CENTRE = (790, 640)
RX = [135, 270, 405, 540]
RATIO = 0.8
GATE_AZ = [35, 160, 250, 320]                       # degrees, per ring (inner to outer), data in the real thing
KEY_AZ = [20, 140, 260]                             # key carriers on the outer ring
KEYS = ["INTEL", "BREACH", "VIRUS"]
ROMAN = ["I", "II", "III", "IV"]


def ell(r, a, c=CENTRE):
    t = math.radians(a)
    return (c[0] + r * math.cos(t), c[1] - r * RATIO * math.sin(t))


def ring_pts(r, a0, a1, n=120):
    return [ell(r, a0 + (a1 - a0) * k / n) for k in range(n + 1)]


def flat_masked(img, lay, mask):
    h, w = img.shape[:2]
    a = np.asarray(lay.resize((w, h), Image.LANCZOS), np.float32) / 255.0
    al = a[..., 3:4] * (1 - mask[..., None])
    return img * (1 - al) + a[..., :3] * al


def arch(d, x, y, w, h, col, open_=False, a=255):
    """Gate arch glyph: two jambs and a round head; open = jambs apart and no lintel line."""
    S = L.SS
    gap = w * (0.9 if open_ else 0.0)
    for sx in (-1, 1):
        xx = x + sx * (w / 2 + gap / 2)
        d.line([(xx * S, y * S), (xx * S, (y - h * 0.6) * S)], fill=col + (a,), width=3 * S)
    d.arc([(x - w / 2 - gap / 2) * S, (y - h) * S, (x + w / 2 + gap / 2) * S, (y - h * 0.2) * S], 180, 360, fill=col + (a,), width=3 * S)


def key_icon(d, x, y, name, held, col=GOLD):
    S = L.SS
    r = 16
    d.polygon([(x * S, (y - r) * S), ((x + r) * S, y * S), (x * S, (y + r) * S), ((x - r) * S, y * S)],
              fill=(col + (255,) if held else (12, 14, 18, 230)), outline=col + (255,), width=2 * S)
    T.text(d, x, y, name[0], 15, (20, 14, 4, 255) if held else col + (255,), "mm")
    T.text(d, x, y + r + 14, name, 12, (240, 225, 180, 255), "mm")


def wedge(d, x, y, toward, size=15, col=VERD):
    S = L.SS
    ang = math.atan2(toward[1] - y, toward[0] - x)
    pts = [(x + size * math.cos(ang), y + size * math.sin(ang)),
           (x + size * 0.8 * math.cos(ang + 2.5), y + size * 0.8 * math.sin(ang + 2.5)),
           (x + size * 0.8 * math.cos(ang - 2.5), y + size * 0.8 * math.sin(ang - 2.5))]
    d.polygon([(px * S, py * S) for px, py in pts], fill=col + (235,), outline=(10, 40, 30, 255))


def raid(name, state, breached=(), keys_held=(True, True, True), wedges_in=(), collapse=1.0, stamp=False):
    base = T.grid_base()
    r_, g_, b_ = base[..., 0], base[..., 1], base[..., 2]
    nodes = L.smoothstep(0.08, 0.2, g_ - np.maximum(r_, b_) * 0.95) * L.smoothstep(0.3, 0.5, g_)
    prot = nodes
    pm = np.asarray(Image.fromarray((nodes * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255.0
    mm = T.map_mask()
    pm = np.maximum(pm * 0.0 + pm, 1 - mm)
    # light touch on the map: a slight dim inside the ring set so the rings read, nothing more
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = np.hypot((xx - CENTRE[0]) / (RX[3] * collapse), (yy - CENTRE[1]) / (RX[3] * RATIO * collapse))
    inside = (1 - L.smoothstep(0.9, 1.05, q)) * mm
    img = base * (1 - 0.16 * (inside * (1 - prot))[..., None])
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    lay_g = T.canvas()
    dg = ImageDraw.Draw(lay_g)
    S = L.SS
    for i, rx in enumerate(RX):
        r = rx * collapse
        br = (i + 1) in breached
        lit = state != "PENDING"
        a = 150 if lit else 70
        if br:
            a = 95                                   # ring dims to x0.6 once breached
        ga = GATE_AZ[i]
        gap = 14 if not br else 30
        phase = (i * 12) * 0.5
        segs = [(ga + gap / 2, ga - gap / 2 + 360)]
        pts = ring_pts(r, segs[0][0], segs[0][1], 200)
        if lit:
            T.pattern_line(d, pts, (6, 20, 18, min(255, a + 60)), 6, "solid")
        T.pattern_line(d, pts, VERD + (min(255, a + 70),), 3, "solid" if lit else "dashed", dash=(10, 8), phase=phase)
        # ring chip at the north tick, then the gate arch in the gap
        nx, ny = ell(r, 90)
        T.chipbox(dg, nx, ny, ROMAN[i], GILT + (255,), 15, anchor="mm", fill=(8, 12, 12, 235))
        gx, gy = ell(r, ga)
        if state != "LOST":
            arch(dg, gx, gy + 8, 12, 24, GILT, open_=br)
    # lanes: radial dashed approach lines from the outer ring inward at the key azimuths
    for az in KEY_AZ:
        p0, p1 = ell(RX[3] * collapse, az), ell(40, az)
        T.pattern_line(d, [p0, p1], (VERD + (110 if state != "PENDING" else 50,)), 2, "dashed", dash=(8, 8))
    # keys on the outer ring (carriers): lit when the carrier is alive and on its way
    if state != "LOST":
        for az, nm, held in zip(KEY_AZ, KEYS, keys_held):
            kx, ky = ell(RX[3] * collapse, az)
            key_icon(dg, kx, ky, nm, held and state != "PENDING")
    # wedges: the levy legions on the lanes (outer ring when ACTIVE, inward past breached rings)
    if state in ("ACTIVE", "BREACH"):
        for az, k in zip(KEY_AZ, wedges_in):
            wx, wy = ell(RX[3] * (0.93 - 0.22 * k) if k is not None else RX[3] * 0.93, az)
            wedge(dg, wx, wy, CENTRE)
    out = flat_masked(img, lay, pm)
    out = T.flat(out, lay_g)
    # overlay: state header and legend (no netrun band applies; stays below the pin brightness)
    lay2 = T.canvas()
    d2 = ImageDraw.Draw(lay2)
    T.panel(d2, (70, 110, 760, 152), fill=(8, 12, 12, 228), outline=GILT + (235,))
    word = {"PENDING": "RAID  PENDING", "ACTIVE": "RAID  ONGOING", "BREACH": "RING II BREACHED  ONGOING", "LOST": "BREACHED  HOME SERVER FELL"}[state]
    T.text(d2, 90, 131, word, 18, (245, 235, 205, 255))
    for k in range(4):
        x = 560 + k * 48
        col = GILT if (k + 1) not in breached else VERD
        d2.ellipse([(x - 12) * S, (131 - 12) * S, (x + 12) * S, (131 + 12) * S], outline=col + (255,), width=2 * S)
        T.text(d2, x, 131, ROMAN[k], 12, col + (255,), "mm")
    if stamp:
        pts = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
        dd = ImageDraw.Draw(pts)
        f = L.font(44 * S)
        dd.rectangle([(CENTRE[0] - 130) * S, (CENTRE[1] - 78) * S, (CENTRE[0] + 130) * S, (CENTRE[1] - 28) * S], outline=GILT + (255,), width=4 * S)
        dd.text((CENTRE[0] * S, (CENTRE[1] - 53) * S), "PACIFIED", font=f, fill=GILT + (255,), anchor="mm")
        pts = pts.rotate(8, center=(CENTRE[0] * S, (CENTRE[1] - 53) * S))
        lay2.alpha_composite(pts)
    out = T.flat(out, lay2)
    T.save(out, os.path.join(T.out_dir(CORP), name + ".png"))
    return dict(map=L.metrics(img), still=L.metrics(out))


# ------------------------------------------------------------------------------------------ HQ overview
HQ = os.path.join(T.ROUTE, "hq_aurelian")
SC = 2560 / 2000.0
ARENA = (1170 * SC, 560 * SC)
HRX = [190 * SC, 300 * SC, 410 * SC, 520 * SC]          # ring radii (R4 inner .. R1 outer) in screen px
HRY = [105 * SC, 190 * SC, 270 * SC, 350 * SC]
GATES_NOW = [118, 70, 140, 100]                          # param angle (deg), R4, R3, R2, R1
GATES_STEP = 24                                          # one step turns every gate by 2 ticks (2 x 12 deg)
NAMES = ["IV", "III", "II", "I"]
FEED_NOTE = "gate_tick_now / gate_tick_next"


def hq_pt(i, a):
    t = math.radians(a)
    return (ARENA[0] + HRX[i] * math.cos(t), ARENA[1] - HRY[i] * math.sin(t))


def hq_still(name, shift):
    plate = np.asarray(Image.open(os.path.join(HQ, "plates", "H_overview_v2_plate.png")).convert("RGB"), np.float32) / 255.0
    comp = np.asarray(Image.open(os.path.join(HQ, "H_overview_v2.png")).convert("RGB"), np.float32) / 255.0
    chrome = (np.abs(comp - plate).max(axis=2) > 0.04).astype(np.float32)
    keep = np.asarray(Image.fromarray((chrome * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255.0
    S = 2
    lay = Image.new("RGBA", (2560 * S, 1440 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(4):
        now = GATES_NOW[i] + shift
        gap = 11
        # ring-edge gilt line over the visible arc (the rear seating; the front wall hides the rest), with a gap at the gate
        arcs = [(a0, a1) for a0, a1 in ((-8, now - gap), (now + gap, 188))]
        for a0, a1 in arcs:
            if a1 <= a0:
                continue
            pts = [hq_pt(i, a0 + (a1 - a0) * k / 80) for k in range(81)]
            d.line([(x * S, y * S) for x, y in pts], fill=(24, 14, 4, 230), width=int(11 * S), joint="curve")
            d.line([(x * S, y * S) for x, y in pts], fill=(240, 205, 125, 255), width=int(6 * S), joint="curve")
        # gate = a lit window sliding on the line: arch jambs + threshold slab
        gx, gy = hq_pt(i, now)
        d.rectangle([(gx - 14) * S, (gy - 26) * S, (gx + 14) * S, (gy + 4) * S], fill=(255, 240, 190, 120), outline=GILT + (255,), width=3 * S)
        d.arc([(gx - 14) * S, (gy - 40) * S, (gx + 14) * S, (gy - 12) * S], 180, 360, fill=GILT + (255,), width=3 * S)
        # the pencil-yellow ghost of the NEXT position (+2 ticks), at most one per ring
        nx, ny = hq_pt(i, now + GATES_STEP)
        d.rectangle([(nx - 12) * S, (ny - 22) * S, (nx + 12) * S, (ny + 3) * S], outline=PENCIL + (230,), width=2 * S)
        # ring label chip at the east tick
        lx, ly = hq_pt(i, -8)
        d.rectangle([(lx + 6) * S, (ly - 13) * S, (lx + 44) * S, (ly + 13) * S], fill=(10, 8, 4, 230), outline=GILT + (255,), width=2 * S)
        d.text(((lx + 25) * S, ly * S), NAMES[i], font=L.font(20 * S), fill=(245, 235, 205, 255), anchor="mm")
    lay = lay.resize((2560, 1440), Image.LANCZOS)
    a = np.asarray(lay, np.float32) / 255.0
    al = a[..., 3:4] * (1 - keep[..., None])
    plate_t = plate * (1 - al) + a[..., :3] * al
    plate_vals = L.metrics(plate_t)
    final = plate_t * (1 - chrome[..., None]) + comp * chrome[..., None]
    fin = Image.fromarray((np.clip(final, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS)
    # the key row and the step note live in a corner card (bottom right, clear of every room)
    lay2 = T.canvas()
    d2 = ImageDraw.Draw(lay2)
    T.panel(d2, (1380, 880, 1900, 990), fill=(8, 7, 4, 220), outline=GILT + (235,))
    T.text(d2, 1396, 900, "GATE RINGS  STEP %d" % (1 + shift // GATES_STEP), 16, (245, 235, 205, 255))
    T.text(d2, 1396, 926, "gilt window = gate now", 13, GILT + (255,))
    T.text(d2, 1396, 946, "yellow ghost = gate next step", 13, PENCIL + (255,))
    T.text(d2, 1396, 966, "tick x 12 deg; rings turn inward-out", 13, (200, 190, 160, 255))
    out = T.flat(np.asarray(fin, np.float32) / 255.0, lay2)
    T.save(out, os.path.join(T.out_dir(CORP), name + ".png"))
    return dict(plate_clean=L.metrics(plate), plate_with_theme=plate_vals, still=L.metrics(out))


def main(which="all"):
    res = {}
    jobs = [
        ("R_pending", lambda n: raid(n, "PENDING", keys_held=(False, False, False))),
        ("R_active", lambda n: raid(n, "ACTIVE", wedges_in=(None, None, None))),
        ("R_ring2_breached", lambda n: raid(n, "BREACH", breached=(3, 4), keys_held=(True, True, False), wedges_in=(1.2, 0.6, 1.2))),
        ("R_lost", lambda n: raid(n, "LOST", breached=(1, 2, 3, 4), collapse=0.34, stamp=True)),
        ("H_overview_gates", lambda n: hq_still(n, 0)),
        ("H_overview_gates_step", lambda n: hq_still(n, GATES_STEP)),
    ]
    for n, fn in jobs:
        if which != "all" and n not in which:
            continue
        res[n] = fn(n)
        print(n, res[n], flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else "all")
