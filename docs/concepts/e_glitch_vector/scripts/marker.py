"""GLITCH VECTOR CRT - the Cell's marker: Grease Pencil strokes, hot pink, dripping, NOT glowing.

blender -b --factory-startup --python marker.py -- <jobs.json> <out.png>
jobs.json: list of {"text", "x", "y" (baseline, px), "cap" (px), "seed", "write" (0..1),
                    "drip": "none"|"forming"|"running", "drip_len" (px), "rot" (deg), "drips" (count)}
Renders on a transparent film with REGULAR (alpha) layers, so it sits on top of everything
as the only analog thing on the screen (no bloom, no light spill, never glitched).
"""
import bpy, sys, os, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
import gv_font as gf

argv = sys.argv[sys.argv.index("--") + 1:]
jobs = json.load(open(argv[0]))
OUT = argv[1]
W, H = 1920, 1080
sc = gv.reset((W, H), samples=16, transparent=True)
gv.camera((0, 0, 20), (0, 0, 0), ortho_scale=19.2)
sc.render.use_compositing = False

INK = gv.col("pink")
INK_DARK = gv.col("#B01C6C")
INK_HI = gv.col("#FF8FCB")


def px(x, y):
    return ((x - W / 2) / 100.0, (H / 2 - y) / 100.0)


# one GP object, 2D layer order (edge < ink < highlight); three stroke lists collected first
MK = gv.GP("marker", blend="REGULAR", depth_3d=False)


class _Bucket:
    def __init__(self):
        self.strokes = []

    def line(self, *a, **k):
        MK.line(*a, **k)
        self.strokes.append(MK.strokes.pop())


G_edge, G_ink, G_hi = _Bucket(), _Bucket(), _Bucket()

for job in jobs:
    rng = random.Random(job.get("seed", 1))
    cap = job["cap"] / 100.0
    ox, oy = px(job["x"], job["y"])
    if job.get("shape") == "circle":
        # a quick hand-drawn loop around something (overshoots its start, like a real circle-it)
        rx, ry = job["rx"] / 100.0, job["ry"] / 100.0
        a0 = rng.uniform(0, 6.28)
        pts = []
        n = 70
        for i in range(n + 1):
            t = i / n * 1.12
            a = a0 + t * 6.283
            wob = 1 + 0.05 * math.sin(t * 9 + a0) + 0.04 * t
            pts.append((ox + rx * wob * math.cos(a), oy + ry * wob * math.sin(a)))
        strokes = [(pts, [0.8 + 0.2 * math.sin(math.pi * i / n) for i in range(n + 1)])]
    else:
        strokes = gf.marker_hand(job["text"], cap, rng, origin=(ox, oy), rot_deg=job.get("rot", -4.0),
                                 spacing=job.get("spacing", 6.3))
    base_r = cap * job.get("weight", 0.112)
    # write-on: truncate by cumulative length
    lens = []
    for (pl, pr) in strokes:
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pl, pl[1:]))
        lens.append(L)
    total = sum(lens)
    budget = total * job.get("write", 1.0) + (1e-3 if job.get("write", 1.0) >= 1.0 else 0.0)
    drawn = []
    for (pl, pr), L in zip(strokes, lens):
        if budget <= 0:
            break
        if L <= budget:
            drawn.append((pl, pr, False))
            budget -= L
        else:
            acc, cut = 0.0, [pl[0]]
            for a, b in zip(pl, pl[1:]):
                d = math.hypot(b[0] - a[0], b[1] - a[1])
                if acc + d >= budget:
                    t = (budget - acc) / max(d, 1e-6)
                    cut.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                    break
                cut.append(b)
                acc += d
            drawn.append((cut, pr[:len(cut)], True))
            budget = 0
    for (pl, pr, live) in drawn:
        n = len(pl)
        # ink pools at the start and end of a stroke (the pen rests)
        radii = []
        for i in range(n):
            e = 1.0 + 0.35 * math.exp(-i * 0.9) + 0.25 * math.exp(-(n - 1 - i) * 0.9)
            radii.append(base_r * pr[min(i, len(pr) - 1)] * e)
        pts = [(x, y, 0.0) for (x, y) in pl]
        G_edge.line(pts, INK_DARK, radii=[r * 1.1 for r in radii], radius=base_r)
        G_ink.line([(x, y, 0.01) for (x, y) in pl], INK, radii=radii, radius=base_r)
        # streaky highlight off-centre: the chisel tip's lighter drag
        # dry streaks of the felt tip (flat marker, not a glossy tube)
        G_hi.line([(x - base_r * 0.3, y + base_r * 0.35, 0.02) for (x, y) in pl], INK_HI,
                  radii=[r * 0.16 for r in radii], radius=base_r, opac=[0.3 * max(0.0, math.sin(i * 1.3)) for i in range(n)])
        if live and n:
            x, y = pl[-1]
            G_ink.line([(x, y, 0.03), (x + 0.001, y, 0.03)], INK_DARK, radius=base_r * 1.5)  # wet pen tip
    # ---------------- drips: from low points on the letters
    mode = job.get("drip", "none")
    if mode == "none" or job.get("write", 1.0) < 1.0:
        continue
    cands = []
    for (pl, pr, live) in drawn:
        for i in range(1, len(pl) - 1):
            if pl[i][1] <= pl[i - 1][1] and pl[i][1] <= pl[i + 1][1]:
                cands.append(pl[i])
        cands.append(min(pl, key=lambda p: p[1]))
    cands.sort(key=lambda p: (round(p[0], 2), p[1]))
    rng.shuffle(cands)
    picks = []
    for c in cands:
        if all(abs(c[0] - q[0]) > cap * 0.45 for q in picks):
            picks.append(c)
        if len(picks) >= job.get("drips", 5):
            break
    for k, (x, y) in enumerate(picks):
        if mode == "forming":
            L = rng.uniform(0.25, 0.75) * cap * 0.55
        else:
            L = job.get("drip_len", 400) / 100.0 * rng.uniform(0.45, 1.0)
        n = max(6, int(L / 0.03))
        pts, radii = [], []
        wob = rng.uniform(0, 6)
        for i in range(n + 1):
            t = i / n
            xx = x + math.sin(wob + t * 5) * 0.012 * (L / cap)
            pts.append((xx, y - L * t, 0.005))
            # neck thins below the letter, fattens into a bead at the end
            r = base_r * (0.75 - 0.4 * math.sin(math.pi * min(1, t * 1.1)) if mode == "running" else 0.8 - 0.3 * t)
            radii.append(max(r, base_r * 0.28))
        G_edge.line(pts, INK_DARK, radii=[r * 1.2 for r in radii], radius=base_r)
        G_ink.line([(a, b, 0.012) for (a, b, _) in pts], INK, radii=radii, radius=base_r)
        bx, by = pts[-1][0], pts[-1][1]
        bead = base_r * (1.15 if mode == "forming" else 1.0)
        G_edge.line([(bx, by - bead * 0.3, 0.0), (bx, by - bead * 0.31, 0.0)], INK_DARK, radius=bead * 1.2)
        G_ink.line([(bx, by - bead * 0.3, 0.013), (bx, by - bead * 0.31, 0.013)], INK, radius=bead)
        G_hi.line([(bx - bead * 0.35, by, 0.02), (bx - bead * 0.34, by + 0.001, 0.02)], INK_HI, radius=bead * 0.3, opacity=0.8)

for name, b in (("edge", G_edge), ("ink", G_ink), ("hi", G_hi)):
    MK.strokes = b.strokes
    MK.flush(name)
gv.render(OUT)
print("MARKER DONE", OUT)
