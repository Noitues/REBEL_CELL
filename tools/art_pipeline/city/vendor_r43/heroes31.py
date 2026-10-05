# Round 31: the same castle (round 30), the camera faces the boom (from world +Y, beyond the track), and a new loop:
# a train pulls in left->right on the loading track, the crane lowers a container onto its empty flatcar, the train
# speeds off to the right with motion streaks, the next train arrives. Camera looks along -Y, so screen-right = world -X.
# NOT a module: exec()'d after heroes30.py.

NFRAMES = 20
ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
MOVE_FRAMES[:] = [dict(solid=Acc("mv_s%02d" % f), lit=Acc("mv_l%02d" % f), neon=Acc("mv_n%02d" % f)) for f in range(NFRAMES)]
TY = TRACK_Y[0]           # the loading track, in front of the castle
EMPTY_K = 1               # the flatcar that receives the container (index behind the locomotive)
X_STOP = -(17 + 15 * EMPTY_K)
LOADED = [True, False, True, True, False, True]


def train_x(f):
    """Locomotive x per frame (it leads toward -X = screen right). None = out of view."""
    if 4 <= f <= 10:
        return float(X_STOP)
    if f in (15, 16, 17, 18, 19, 0, 1, 2, 3):        # arriving from screen-left, decelerating
        k = (f - 15) % 20                              # 0..8
        u = 1 - (k + 1) / 10.0
        return X_STOP + 260 * u * u
    if 11 <= f <= 14:                                   # speeding off to screen-right
        k = f - 10
        return X_STOP - 18 * k * k
    return None


def train_speed(f):
    a, b = train_x(f), train_x((f + 1) % NFRAMES)
    if a is None or b is None:
        return 0.0
    return abs(b - a)


def crane31(f):
    """Trolley over the track (world y = TY) holding a container high; lowers it f4..f9; returns empty to the yard
    f10..f14; picks and carries the next one out f15..f19."""
    if f <= 3:
        return dict(boom=0.0, t=TY, cz=14.0, carry=True)
    if f <= 9:
        u = (f - 3) / 6
        return dict(boom=0.0, t=TY, cz=14.0 - (14.0 - 1.6) * u, carry=f < 9)
    if f <= 14:
        u = (f - 9) / 5
        return dict(boom=10 * math.sin(math.pi * u), t=TY - (TY - 6) * u, cz=14.0, carry=False)
    u = (f - 14) / 5
    return dict(boom=0.0, t=6 + (TY - 6) * u, cz=14.0 - 7 * math.sin(math.pi * u) if f == 15 else 14.0, carry=True)


def streaks(x0, y, speed):
    """Motion streaks trailing the speeding train (toward +X, behind it): lit lines at headlight / container heights."""
    L = min(70.0, speed * 2.2)
    n_cars = len(LOADED)
    x_tail = x0 + 17 + 15 * (n_cars - 1) + 7
    for z, c, w in ((2.4, (1.0, 0.95, 0.80), 0.14), (3.6, (0.86, 0.42, 0.10), 0.22), (5.0, (0.16, 0.36, 0.62), 0.18),
                    (6.0, (0.95, 0.80, 0.30), 0.12)):
        for dy in (-1.8, 1.8):
            NEON.face([(x0 - 2, y + dy, z), (x_tail + L, y + dy, z), (x_tail + L, y + dy, z + w), (x0 - 2, y + dy, z + w)],
                      tuple(v * 0.7 for v in c), (0, 0, 0))
    for k in range(3):  # ghost copies of the locomotive nose (smear)
        gx = x0 + 4 + k * speed * 0.35
        NEON.face([(gx, y + 1.65, 1.2), (gx + 6, y + 1.65, 1.2), (gx + 6, y + 1.65, 5.5), (gx, y + 1.65, 5.5)], (0.30 - k * 0.08, 0.15 - k * 0.04, 0.04), (0, 0, 0))


def fort_v31():
    fort_v29_static()
    bolts_ladders_catwalks()
    faceted_water(S30 + 6.2, S30 + 11.5)
    rail_yard()
    for f in range(NFRAMES):
        old = _swap(MOVE_FRAMES[f])
        try:
            c = crane31(f)
            build_at(lambda: crane_dyn(c["boom"], c["t"], c["cz"], c["carry"]), rot=90.0)
            x0 = train_x(f)
            if x0 is not None:
                loaded = list(LOADED)
                if 9 <= f <= 14:
                    loaded[EMPTY_K] = True
                freight_train(x0, TY, n=len(LOADED), loaded=loaded, d=-1)
                if 11 <= f <= 14:
                    streaks(x0, TY, train_speed(f - 1) + 18)
        finally:
            _restore(old)


HEROES26["meridian"] = fort_v31
