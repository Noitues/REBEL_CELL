# Round 42: HQ mechanics on the overhead COMPOUND view. NOT a module: hq_scene.py exec()s this last.
# For the corp being rendered (COMPOUND=1), each HQ is built so its MOVING part changes per animation frame (one
# mechanic STEP over the frames), and NODE_POS(f) gives the world position of every run node in frame f; hq_scene writes
# them, projected, to <tag>_fXX_anchors.json for the overlay (compound42.py).
#   meridian  : round 31 loop (crane lowers a node container onto the train, the train leaves, the next arrives)
#   solace    : the helix (strands + walkways) turns 60 deg over the step
#   halcyon   : the eye sweeps its searchlight across the ziggurat (EYE_ANGLES)
#   orbital   : the silo doors slide open, the rocket rises
#   rebel_cell: static DISPATCH base (the mechanic is in the links: the cables rehang)

COMPOUND = os.environ.get("COMPOUND", "") == "1"


def _grp(f):
    return dict(solid=Acc("m42s%02d" % f), lit=Acc("m42l%02d" % f), neon=Acc("m42n%02d" % f), win=Acc("m42w%02d" % f))


def _swap42(g):
    global SOLID, LIT, NEON, WIN
    old = (SOLID, LIT, NEON, WIN)
    SOLID, LIT, NEON, WIN = g["solid"], g["lit"], g["neon"], g["win"]
    return old


def _restore42(old):
    global SOLID, LIT, NEON, WIN
    SOLID, LIT, NEON, WIN = old


def per_frame(build, n):
    """Build `build(f)` once per frame into its own accumulators (hq_scene hides all but the current frame)."""
    MOVE_FRAMES[:] = [_grp(f) for f in range(n)]
    for f in range(n):
        old = _swap42(MOVE_FRAMES[f])
        try:
            build(f)
        finally:
            _restore42(old)


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ SOLACE: the helix turns
SOL_R, SOL_Z0, SOL_Z1, SOL_TURNS, SOL_N = 13.5, 6.5, 108.0, 2.6, 160
SOL_RUNGS = list(range(4, SOL_N - 2, 4))


def sol_phi(f, n):
    """Helix rotation (deg) in frame f: still for 3 frames, turns 60 deg over 6, still for the rest."""
    return 60.0 * ease((f - 3) / 6.0)


def sol_strand(phi):
    A, B = [], []
    for i in range(SOL_N + 1):
        t = i / SOL_N
        a = t * SOL_TURNS * 2 * math.pi + math.radians(-45 + phi)
        z = SOL_Z0 + t * (SOL_Z1 - SOL_Z0)
        A.append((SOL_R * math.cos(a), SOL_R * math.sin(a), z))
        B.append((SOL_R * math.cos(a + math.pi), SOL_R * math.sin(a + math.pi), z))
    return A, B


def helix_moving(phi):
    A, B = sol_strand(phi)
    tube(A, 2.9, STRAND_A, n=12)
    tube(B, 2.9, STRAND_B, n=12)
    for S_, gc in ((A, (0.16, 0.40, 0.32)), (B, (0.24, 0.44, 0.10))):
        tube([(x * 1.21, y * 1.21, z) for (x, y, z) in S_], 0.45, gc, acc=NEON, n=6)
    for S_, col in ((A, (0.40, 1.0, 0.75)), (B, (0.62, 1.0, 0.25))):
        tube([(x, y, z - 2.7) for (x, y, z) in S_], 0.42, col, acc=NEON, n=6)
    for i in SOL_RUNGS:
        p, q = Vector(A[i]), Vector(B[i])
        d = (q - p).normalized()
        p2, q2 = p + d * 2.6, q - d * 2.6
        beam(tuple(p2), tuple(q2), 0.9, (0.70, 0.76, 0.74))
        side = d.cross(Vector((0, 0, 1))).normalized() * 0.55
        beam(tuple(p2 + side + Vector((0, 0, 0.9))), tuple(q2 + side + Vector((0, 0, 0.9))), 0.18, (0.82, 0.88, 0.86))
        beam(tuple(p2 - side + Vector((0, 0, 0.9))), tuple(q2 - side + Vector((0, 0, 0.9))), 0.18, (0.82, 0.88, 0.86))
        beam(tuple(p2 + Vector((0, 0, 0.5))), tuple(q2 + Vector((0, 0, 0.5))), 0.25, RUNG, acc=NEON)
    for S_ in (A, B):
        x, y, z = S_[-1]
        dome(x, y, z, 3.0, (0.62, 0.72, 0.68), n=12)


def solace42():
    plaza(27.5, (0.30, 0.78, 0.50), ground=(0.24, 0.30, 0.28), ring2=(0.45, 0.85, 0.35))
    cyl(0, 0, 0, 3.5, 23, (0.66, 0.72, 0.70), n=8, a_off=math.pi / 8)
    cyl(0, 0, 3.5, 6.5, 18, (0.58, 0.66, 0.62), n=8, a_off=math.pi / 8)
    ring_beams((0, 0, 3.6), (1, 0, 0), (0, 1, 0), 22.6, 0.4, (0.35, 0.80, 0.45), n=8)
    ring_beams((0, 0, 6.6), (1, 0, 0), (0, 1, 0), 17.6, 0.4, (0.35, 0.80, 0.45), n=8)
    cyl(0, 0, 6.5, 8.2, 2.6, (0.25, 0.30, 0.28), n=12)
    disc((0, 0, 8.25), (1, 0, 0), (0, 1, 0), 2.1, (0.85, 1.0, 0.75), acc=NEON, n=12)
    for k in range(6):  # the landing pods (static): walkways dock to them as the helix turns
        a = 2 * math.pi * k / 6
        px, py = 20 * math.cos(a), 20 * math.sin(a)
        cyl(px, py, 3.5, 5, 3.2, (0.72, 0.78, 0.74), n=12)
        cyl(px, py, 5, 10.5, 2.7, (0.30, 0.46, 0.36), n=12)
        dome(px, py, 10.5, 2.7, (0.40, 0.56, 0.46), n=12)
        ring_beams((px, py, 8), (1, 0, 0), (0, 1, 0), 2.78, 0.22, RUNG, n=12)
    if COMPOUND and CORP == "solace":
        per_frame(lambda f: helix_moving(sol_phi(f, NFRAMES)), NFRAMES)
    else:
        helix_moving(0.0)


SOL_NODE_RUNGS = [8, 36, 64, 92, 120, 148]   # rung indices that carry nodes (alternately on strand A / B)


def sol_nodes(f):
    A, B = sol_strand(sol_phi(f, NFRAMES))
    out = {"start": (16.0, -16.0, 3.7)}
    for k in range(6):
        a = 2 * math.pi * k / 6
        out["pod%d" % k] = (20 * math.cos(a), 20 * math.sin(a), 13.5)
    for j, i in enumerate(SOL_NODE_RUNGS):
        S_ = A if j % 2 == 0 else B
        x, y, z = S_[i]
        out["w%d" % j] = (x, y, z + 1.6)
    x, y, z = A[-1]
    out["srv"] = (x, y, z + 3.4)
    return out


# ------------------------------------------------------------------ HALCYON: the eye sweeps
def halcyon42():
    civic_core26()
    # one step: the eye turns 70 deg over the frames (from the left face to the right face of the ziggurat)
    EYE_ANGLES[:] = [-35.0 + 70.0 * ease((f - 2) / 7.0) for f in range(NFRAMES)]


def hal_nodes(f):
    tiers = [(27, 9), (23.5, 18), (20, 27), (16.5, 36), (13.5, 45), (10.5, 54)]
    out = {"start": (34.0, 0.0, 0.8)}
    # two nodes per terrace: one on the -Y face (front left), one on the +X face (front right)
    for k, (hs, z) in enumerate(tiers):
        out["L%d" % k] = (-hs * 0.55, -hs + 1.8, z + 0.6)
        out["R%d" % k] = (hs - 2.4, -(hs - 2.4), z + 0.6)  # the front corner (the eye reaches it at the end of the sweep)
    out["srv"] = (0.0, 0.0, 74.5)
    return out


# ------------------------------------------------------------------ ORBITAL: doors slide, the rocket rises
_src26 = open(os.path.join(_HERE, "heroes26.py"), encoding="utf-8-sig").read().replace("\r\n", "\n")
_a = _src26.index("def orbital_silo26():")
_b = _src26.index("\n# ======", _a)
_fn = _src26[_a:_b]
for _x, _y in (("def orbital_silo26():", "def orbital_parts(SL_=0.0, RISE=0.0):"),
               ('    open_ = globals().get("STATE", "") == "open"', "    open_ = SL_ > 0.04"),
               ("    slide = 13.6 if open_ else 0.0", "    slide = 13.6 * SL_"),
               ("        RZ = PZ + 8", "        RZ = PZ - 18 + 26 * RISE")):
    assert _x in _fn, _x
    _fn = _fn.replace(_x, _y)
exec(_fn)


def orb_sl(f):
    return ease((f - 2) / 4.0)          # doors slide open over frames 2..6


def orb_rise(f):
    return ease((f - 5) / 5.0)          # the rocket rises over frames 5..10


def orbital42():
    if COMPOUND and CORP == "orbital":
        per_frame(lambda f: orbital_parts(orb_sl(f), orb_rise(f)), NFRAMES)
    else:
        orbital_parts(1.0 if globals().get("STATE", "") == "open" else 0.0, 1.0)


def orb_nodes(f):
    PZ = 6.0
    sl = orb_sl(f)
    out = {"start": (19.0, -19.0, 6.5)}
    out["doorL"] = (-6.0 - 13.6 * sl, 0.0, PZ - 1.4)
    out["doorR"] = (6.0 + 13.6 * sl, 0.0, PZ - 1.4)
    out["rim_s"] = (13.0 * 0.7071, -13.0 * 0.7071, PZ + 0.4)
    out["rim_n"] = (-13.0 * 0.7071, 13.0 * 0.7071, PZ + 0.4)
    out["dishE"] = (20.5 * math.cos(math.radians(90)), 20.5 * math.sin(math.radians(90)), PZ + 18)
    out["dishW"] = (20.5 * math.cos(math.radians(180)), 20.5 * math.sin(math.radians(180)), PZ + 18)
    out["rocket"] = (0.0, 0.0, PZ - 18 + 26 * orb_rise(f) + 13 + 8)
    back = math.radians(135)
    out["srv"] = (20 * math.cos(back), 20 * math.sin(back), PZ + 6)
    return out


# ------------------------------------------------------------------ MERIDIAN: the round 31 loop
def mer_nodes(f):
    S = 18.0
    out = {"start": (40.0, 0.0, 0.5), "g1": (18.0, -6.6, 16.2), "g2": (18.0, 6.6, 16.2),
           "t1": (18.0, -18.0, 21.2), "t2": (18.0, 18.0, 21.2), "t3": (-18.0, 18.0, 21.2), "srv": (-18.0, -18.0, 21.2),
           "y1": (10.0, -11.0, 0.8), "y2": (-10.0, -8.0, 0.8)}
    c = crane31(f)
    if c["carry"]:
        out["crane"] = (0.0, c["t"], c["cz"] + HC * 0.8 + 0.6)
    x0 = train_x(f)
    if x0 is not None:
        for j, key in ((0, "car0"), (2, "car2")):
            out[key] = (x0 + 17 + 15 * j, TY, 1.6 + HC * 0.8 + 0.4)
        if 9 <= f <= 14:  # the crane's node is now on car 1
            out["crane"] = (x0 + 17 + 15 * EMPTY_K, TY, 1.6 + HC * 0.8 + 0.4)
    return out


# ------------------------------------------------------------------ REBEL_CELL: DISPATCH's base (static model)
def rc_nodes(f):
    blocks = [(-24, -24, -8, -12, 14), (-24, -12, -14, 12, 18), (-24, 12, 0, 24, 12), (0, 14, 24, 24, 16), (12, -6, 24, 14, 10),
              (6, -24, 24, -12, 9)]
    out = {"start": (24.0, -24.0, 0.5)}
    for k, (x0, y0, x1, y1, h) in enumerate(blocks):
        out["b%d" % k] = ((x0 + x1) / 2, (y0 + y1) / 2, h + 0.6)
    out["yard"] = (-2.0, -4.0, 0.6)
    out["srv"] = (0.0, 0.0, 35.6)
    return out


NODE_FNS = {"meridian": mer_nodes, "solace": sol_nodes, "halcyon": hal_nodes, "orbital": orb_nodes, "rebel_cell": rc_nodes}
COMP_CAM = {"meridian": ((4, 12, 6), 150), "solace": ((0, 0, 58), 190), "halcyon": ((0, -4, 44), 170), "orbital": ((0, 0, 14), 125),
            "rebel_cell": ((0, 0, 8), 125)}
if COMPOUND:
    NFRAMES = {"meridian": 20, "solace": 12, "halcyon": 12, "orbital": 12, "rebel_cell": 1}[CORP]
    if CORP != "meridian":
        ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
        MOVE_FRAMES[:] = []
HEROES26["solace"] = solace42
HEROES26["halcyon"] = halcyon42
HEROES26["orbital"] = orbital42
