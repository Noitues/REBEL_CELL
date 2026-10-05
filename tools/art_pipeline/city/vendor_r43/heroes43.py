# Round 43: the designer's HQ mechanics. NOT a module: hq_scene.py exec()s this after heroes42.py (COMPOUND=1).
#   meridian : 6 steps x 4 frames: the crane carries container A out (train arriving) > lowers A onto car 1 > the train
#              STAYS a full turn > the train shunts one car, the crane takes container B OFF car 2 > carries B into the
#              fortress (a new node + link inside the walls) > the train leaves with A.
#   solace   : static helix; the CAMERA orbits/climbs so the player node is always centre screen (CAM_FRAMES)
#   halcyon  : the eye alternates LEFT half / RIGHT half of the pyramid face, one side per step
#   orbital  : 3 states: doors shut / doors open + missile up (prep) / doors shut (finale overlay)

CAM_FRAMES = []          # per frame (target, azimuth deg, elevation deg, ortho) - empty = the fixed compound camera
COMP_CAM["solace"] = ((0, 0, 58), 190)
COMP_CAM["halcyon"] = ((2, -12, 36), 112)   # round 43: closer on the switchback face

# ------------------------------------------------------------------ MERIDIAN
M43_X_STOP = -(17 + 15 * 1)          # car 1 under the crane (crane at world x = 0)


def m43_state(f):
    """Per frame: train x0, cars' loads, crane dict, yard container placed?"""
    s, k = divmod(f, 4)
    u = (k + 1) / 4.0
    loads = [True, False, True]             # car0 C, car1 empty (gets A), car2 B
    yard_b = False
    if s == 0:   # train arrives, crane carries A out over the track
        x0 = M43_X_STOP + 220 * (1 - u) ** 2
        crane = dict(boom=0.0, t=6 + (TY - 6) * ease(u), cz=14.0, carry=True, col=(0.86, 0.42, 0.10))
    elif s == 1:  # lower A onto car 1
        x0 = M43_X_STOP
        crane = dict(boom=0.0, t=TY, cz=14.0 - (14.0 - 1.6) * ease(u), carry=k < 3, col=(0.86, 0.42, 0.10))
        loads[1] = k == 3
    elif s == 2:  # the train stays a full turn; the spreader rises empty
        x0 = M43_X_STOP
        loads[1] = True
        crane = dict(boom=0.0, t=TY, cz=1.6 + 12.4 * ease(u), carry=False, col=(0.16, 0.36, 0.62))
    elif s == 3:  # the train shunts one car (car 2 under the crane); the spreader comes down and takes B
        x0 = M43_X_STOP - 15 * ease(u)
        loads[1] = True
        crane = dict(boom=0.0, t=TY, cz=14.0 - 12.4 * ease(u), carry=k == 3, col=(0.16, 0.36, 0.62))
        loads[2] = k < 3
    elif s == 4:  # carry B into the fortress and set it down in the yard
        x0 = M43_X_STOP - 15
        loads[1], loads[2] = True, False
        crane = dict(boom=6 * math.sin(math.pi * u), t=TY - (TY - 6) * ease(u), cz=14.0 if k < 3 else 1.0, carry=k < 3, col=(0.16, 0.36, 0.62))
        yard_b = k == 3
    else:         # the train leaves with A (and C)
        x0 = M43_X_STOP - 15 - 26 * k * k
        loads[1], loads[2] = True, False
        crane = dict(boom=0.0, t=6, cz=14.0, carry=False, col=(0.16, 0.36, 0.62))
        yard_b = True
    return x0, loads, crane, yard_b


def meridian43():
    fort_v29_static()
    bolts_ladders_catwalks()
    faceted_water(S30 + 6.2, S30 + 11.5)
    rail_yard()

    def frame(f):
        x0, loads, c, yard_b = m43_state(f)
        build_at(lambda: crane_dyn(c["boom"], c["t"], c["cz"], c["carry"], c["col"]), rot=90.0)
        cols = [(0.72, 0.20, 0.12), (0.86, 0.42, 0.10), (0.16, 0.36, 0.62)]
        locomotive(x0, TY, -1)
        for j in range(3):
            flatcar(x0 + 17 + 15 * j, TY, [cols[j] if loads[j] else None])
        if yard_b:
            obox(0.0, 6.0, 1.0, 12.0, 2.5, HC * 0.8, 0, (0.16, 0.36, 0.62))
    per_frame(frame, NFRAMES)


def mer43_nodes(f):
    x0, loads, c, yard_b = m43_state(f)
    wall = 2 * HC + 0.6
    tower = 4 * HC + 0.6
    out = {"start": (40.0, 0.0, 0.5), "g1": (18.0, -6.6, 3 * HC + 0.6), "g2": (18.0, 6.6, 3 * HC + 0.6),
           "t1": (18.0, -18.0, tower), "wS1": (6.0, -18.0, wall), "wS2": (-6.0, -18.0, wall), "srv": (-18.0, -18.0, tower),
           "t2": (18.0, 18.0, tower), "wN1": (6.0, 18.0, wall), "wN2": (-6.0, 18.0, wall), "t3": (-18.0, 18.0, tower),
           "wB": (-18.0, 0.0, wall)}
    top = 1.6 + HC * 0.8 + 0.4
    out["car0"] = (x0 + 17, TY, top)
    if loads[1]:
        out["A"] = (x0 + 32, TY, top)
    if loads[2]:
        out["B"] = (x0 + 47, TY, top)
    if c["carry"]:
        key = "A" if f < 8 else "B"
        out[key] = (0.0, c["t"], c["cz"] + HC * 0.8 + 0.6)
    if yard_b:
        out["B"] = (0.0, 6.0, 1.0 + HC * 0.8 + 0.4)
    return out


# ------------------------------------------------------------------ SOLACE: two strands, crossovers, camera follows
SA_RUNGS = [12, 32, 52, 72, 92, 112, 132, 150]
SB_RUNGS = [20, 40, 60, 80, 100, 120, 140]
SX_RUNGS = [44, 84, 124]                       # crossover walkways (node at the walkway's middle)
SOL_PATH = ["start", "A0", "A1", "X0", "B2", "B3", "X1", "A4"]


def sol43_nodes(f=0):
    A, B = sol_strand(0.0)
    out = {"start": (16.0, -16.0, 3.7)}
    for j, i in enumerate(SA_RUNGS):
        x, y, z = A[i]
        out["A%d" % j] = (x * 1.12, y * 1.12, z + 3.2)
    for j, i in enumerate(SB_RUNGS):
        x, y, z = B[i]
        out["B%d" % j] = (x * 1.12, y * 1.12, z + 3.2)
    for j, i in enumerate(SX_RUNGS):
        out["X%d" % j] = (0.0, 0.0, A[i][2] + 1.6)
    x, y, z = A[-1]
    out["srv"] = (x, y, z + 3.4)
    return out


def sol43_cams(n):
    """The camera keeps the player's node centre screen: per frame, the position along SOL_PATH (2 frames a hop)."""
    P = sol43_nodes()
    cams = []
    for f in range(n):
        h = min(len(SOL_PATH) - 1.0, f / 2.0)
        i0 = int(h)
        i1 = min(len(SOL_PATH) - 1, i0 + 1)
        u = ease(h - i0)
        a, b = Vector(P[SOL_PATH[i0]]), Vector(P[SOL_PATH[i1]])
        p = a.lerp(b, u)
        def az(q):
            if math.hypot(q[0], q[1]) < 1.0:
                return None
            return math.degrees(math.atan2(q[1], q[0]))
        za, zb = az(a), az(b)
        if za is None:
            za = zb if zb is not None else -45.0
        if zb is None:
            zb = za
        d = ((zb - za + 180) % 360) - 180
        cams.append(((p.x, p.y, p.z), za + d * u, 32.0, 95.0))
    return cams


# ------------------------------------------------------------------ HALCYON: switchback rows 6-5-4-3-2-1 on the -Y face
H_ROWS = [6, 5, 4, 3, 2, 1]
H_TIERS = [(27, 9), (23.5, 18), (20, 27), (16.5, 36), (13.5, 45), (10.5, 54)]


def hal43_nodes(f=0):
    out = {"start": (0.0, -40.0, 0.5)}
    n = 0
    for r, cnt in enumerate(H_ROWS):
        hs, z = H_TIERS[r]
        xs = [(-0.78 + 1.56 * (i + 0.5) / cnt) * hs for i in range(cnt)] if cnt > 1 else [0.0]
        if r % 2 == 1:
            xs = xs[::-1]
        for x in xs:
            n += 1
            out["n%d" % n] = (x, -hs + 2.0, z + 0.6)
    out["srv"] = (0.0, -5.0, 62.6)
    return out


def hal43_eye(f):
    """The eye alternates halves, one per step (4 frames): LEFT (-30) for steps 0, 2; RIGHT (+30) for steps 1, 3."""
    s, k = divmod(f, 4)
    side = [-30.0, 30.0][s % 2]
    prev = [-30.0, 30.0][(s - 1) % 2]
    return prev + (side - prev) * ease((k + 1) / 2.0)


# ------------------------------------------------------------------ ORBITAL: the lap loop
def orb43_state(f):
    return [(0.0, 0.0), (1.0, 1.0), (0.0, 0.0)][f]


def orb43_nodes(f=0):
    PZ = 6.0
    out = {"start": (19.0, -19.0, PZ + 0.5)}
    for key, deg, r, z in (("dishE", 90, 20.5, PZ + 18), ("dishW", 180, 20.5, PZ + 18), ("dishNE", 60, 23.5, PZ + 7),
                           ("dishSW", 210, 23.5, PZ + 7)):
        out[key] = (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)), z)
    back = math.radians(135)
    out["mast"] = (20 * math.cos(back), 20 * math.sin(back), PZ + 40)
    out["plat"] = (13.0 * 0.7071, -13.0 * 0.7071, PZ + 0.4)
    out["missile"] = (0.0, 0.0, PZ + 21)
    out["srv"] = (20 * math.cos(back), 20 * math.sin(back), PZ + 6)
    return out


def orbital43():
    per_frame(lambda f: orbital_parts(*orb43_state(f)), NFRAMES)


if COMPOUND:
    if CORP == "meridian":
        NFRAMES = 24
        ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
        MOVE_FRAMES[:] = []
        HEROES26["meridian"] = meridian43
        NODE_FNS["meridian"] = mer43_nodes
    elif CORP == "solace":
        NFRAMES = 2 * (len(SOL_PATH) - 1) + 1
        ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
        NODE_FNS["solace"] = sol43_nodes
        CAM_FRAMES[:] = sol43_cams(NFRAMES)
    elif CORP == "halcyon":
        NFRAMES = 16
        ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
        NODE_FNS["halcyon"] = hal43_nodes
    elif CORP == "orbital":
        NFRAMES = 3
        ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
        HEROES26["orbital"] = orbital43
        NODE_FNS["orbital"] = orb43_nodes


def solace43():
    """No spinning: the round 42 helix built once (phi 0)."""
    plaza(27.5, (0.30, 0.78, 0.50), ground=(0.24, 0.30, 0.28), ring2=(0.45, 0.85, 0.35))
    cyl(0, 0, 0, 3.5, 23, (0.66, 0.72, 0.70), n=8, a_off=math.pi / 8)
    cyl(0, 0, 3.5, 6.5, 18, (0.58, 0.66, 0.62), n=8, a_off=math.pi / 8)
    ring_beams((0, 0, 3.6), (1, 0, 0), (0, 1, 0), 22.6, 0.4, (0.35, 0.80, 0.45), n=8)
    cyl(0, 0, 6.5, 8.2, 2.6, (0.25, 0.30, 0.28), n=12)
    helix_moving(0.0)


def halcyon43():
    civic_core26()
    EYE_ANGLES[:] = [hal43_eye(f) for f in range(NFRAMES)]


if COMPOUND and CORP == "solace":
    HEROES26["solace"] = solace43
if COMPOUND and CORP == "halcyon":
    HEROES26["halcyon"] = halcyon43
