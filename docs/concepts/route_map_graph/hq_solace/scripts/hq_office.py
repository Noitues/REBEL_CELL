"""HQ Solace v4: the office-floor kit behind every window (small, instanced by rule, seeded per floor).

Each tower floor of each strand is ONE office floor: a sheared floor slab (its top = the bridge deck level), an
elevator core, conference rooms (glass walls, a table, chairs), cubicle rows (partitions, desk, monitor, chair),
plants, ceiling light panels, and tiny people. Everything upright; every footprint is tested against the sheared
tube wall (the tube slides along the helix), so nothing pokes through the skin.

Scale: `person_h` BU for a standing adult (preset compound.office.person_h). The tube is 20 BU across, so a real-scale
(5.8 BU) crowd would fit only ~3 across; the people are ~2.4 BU: the floor reads as a 25 m office and the people are
tiny against the 8.4 BU window.
"""
import math

PEOPLE = False        # designer (v4 final): NO people anywhere (office occupants or walkers); the kit keeps the figure code

SKIN = [(0.86, 0.66, 0.52), (0.62, 0.44, 0.33), (0.40, 0.27, 0.20), (0.93, 0.78, 0.66)]
SHIRT = [(0.12, 0.14, 0.2), (0.75, 0.78, 0.8), (0.18, 0.28, 0.22), (0.5, 0.15, 0.18), (0.25, 0.25, 0.28),
         (0.82, 0.62, 0.2), (0.15, 0.35, 0.5), (0.9, 0.9, 0.88)]
BRIGHT = [(0.9, 0.9, 0.85), (0.9, 0.45, 0.2), (0.25, 0.7, 0.9), (0.85, 0.8, 0.3), (0.5, 0.9, 0.5)]
TINTS = [(1.0, 0.9, 0.78), (0.86, 0.95, 1.0), (0.88, 1.0, 0.9), (1.0, 0.97, 0.9)]
WARM = [(1.0, 0.76, 0.52), (1.0, 0.72, 0.46), (1.0, 0.8, 0.58), (0.95, 0.85, 0.7)]    # ~3500 K ceiling panels (a few cooler)
CHAIR = [(0.7, 0.15, 0.2), (0.1, 0.35, 0.6), (0.9, 0.55, 0.1), (0.1, 0.5, 0.3), (0.35, 0.15, 0.5)]


def obx(acc, o, ex, ey, u0, u1, v0, v1, z0, z1, col, k=0.0, top=True, bottom=False):
    """An oriented box: corner o (x, y), horizontal axes ex (u) and ey (v, ccw of ex), z0..z1."""
    u0, u1, v0, v1 = min(u0, u1), max(u0, u1), min(v0, v1), max(v0, v1)

    def p(u, v, z):
        return (o[0] + ex[0] * u + ey[0] * v, o[1] + ex[1] * u + ey[1] * v, z)
    acc.face([p(u0, v0, z0), p(u1, v0, z0), p(u1, v0, z1), p(u0, v0, z1)], col, k)
    acc.face([p(u1, v1, z0), p(u0, v1, z0), p(u0, v1, z1), p(u1, v1, z1)], col, k)
    acc.face([p(u0, v1, z0), p(u0, v0, z0), p(u0, v0, z1), p(u0, v1, z1)], col, k)
    acc.face([p(u1, v0, z0), p(u1, v1, z0), p(u1, v1, z1), p(u1, v0, z1)], col, k)
    if top:
        acc.face([p(u0, v0, z1), p(u1, v0, z1), p(u1, v1, z1), p(u0, v1, z1)], col, k)
    if bottom:
        acc.face([p(u0, v1, z0), p(u1, v1, z0), p(u1, v0, z0), p(u0, v0, z0)], col, k)


def person(acc, x, y, z0, ex, ey, h, rng, mode="stand", kk=0.5, bright=False):
    """A tiny person (h BU tall standing): legs, torso, arms, head. mode: stand | sit | walk. No-op while PEOPLE is False."""
    if not PEOPLE:
        return
    shirt = SHIRT[rng.randrange(len(SHIRT))]
    if bright:
        shirt = BRIGHT[rng.randrange(len(BRIGHT))]
    trou = (0.10, 0.11, 0.14) if rng.random() < 0.6 else (0.28, 0.27, 0.25)
    skin = SKIN[rng.randrange(len(SKIN))]
    w = 0.26 * h                       # shoulder half width scale
    o = (x, y)
    hip = 0.47 * h
    if mode == "sit":
        z0 += 0.0
        obx(acc, o, ex, ey, -0.16 * h, 0.16 * h, 0.0, 0.5 * h, z0 + 0.22 * h, z0 + 0.32 * h, trou, kk)      # thighs
        obx(acc, o, ex, ey, -0.16 * h, 0.16 * h, 0.4 * h, 0.5 * h, z0, z0 + 0.32 * h, trou, kk)             # shins
        hip = 0.32 * h
        z_t = z0 + hip
    else:
        d = 0.06 * h if mode == "walk" else 0.0
        obx(acc, o, ex, ey, -0.13 * h, -0.01 * h, -0.07 * h + d, 0.07 * h + d, z0, z0 + hip, trou, kk)
        obx(acc, o, ex, ey, 0.01 * h, 0.13 * h, -0.07 * h - d, 0.07 * h - d, z0, z0 + hip, trou, kk)
        z_t = z0 + hip
    obx(acc, o, ex, ey, -w, w, -0.08 * h, 0.08 * h, z_t, z_t + 0.31 * h, shirt, kk)                           # torso
    for sg in (-1, 1):
        a0, a1 = (w, w + 0.07 * h) if sg > 0 else (-w - 0.07 * h, -w)
        obx(acc, o, ex, ey, a0, a1, -0.05 * h, 0.05 * h, z_t + 0.05 * h, z_t + 0.31 * h, shirt, kk)           # arms
    obx(acc, o, ex, ey, -0.07 * h, 0.07 * h, -0.07 * h, 0.07 * h, z_t + 0.31 * h, z_t + 0.31 * h + 0.14 * h,
        skin, kk)                                                                                           # head


def _fits(G, t, pts, z0, z1, m):
    for z in (z0, z1):
        c = G.tube_pt(t, z, 0.0, 0.0)
        for (x, y) in pts:
            if math.hypot(x - c[0], y - c[1]) > G.RT - m:
                return False
    return True


def slab(G, t, f, accs, col_top, col_side, k_top, z0=None, z1=None, col_bot=(0.42, 0.43, 0.44), k_bot=0.06):
    """A sheared floor slab disc from z0 up to z1 (default: the floor line up to the deck level; top = the deck).
    Its underside is the dropped ceiling of the storey below."""
    z0 = G.floor_z(f) if z0 is None else z0
    z1 = G.deck_z(f) if z1 is None else z1
    NS = 48
    r = G.RT - 0.03
    top = [G.tube_pt(t, z1, 2 * math.pi * j / NS, r) for j in range(NS)]
    bot = [G.tube_pt(t, z0, 2 * math.pi * j / NS, r) for j in range(NS)]
    off = accs["off"]
    off.face(top[::-1], col_top, k_top)
    off.face(bot, col_bot, k_bot)
    for j in range(NS):
        j1 = (j + 1) % NS
        off.face([bot[j], bot[j1], top[j1], top[j]], col_side, 0.12)


def ceiling_disc(G, t, z, accs, col=(0.42, 0.43, 0.44), k=0.06):
    accs["off"].face([G.tube_pt(t, z, 2 * math.pi * j / 48, G.RT - 0.03) for j in range(48)], col, k)


def floor_interior(G, t, f, accs, rng, person_h=2.4, node_panels=None, lit=None, zf=None, ceil_h=4.0):
    """Build the office on floor f of strand t. node_panels: callable(core_front_origin, ex, ey, z0) or None.
    Returns a stats dict."""
    off, glass, lamp = accs["off"], accs["glass"], accs["lamp"]
    q = person_h / 2.4
    fr = G.win_frame(t, f, "in")
    ex, ey = fr["tw"], fr["nw"]                     # local u (across), v (toward the inward window)
    zf = G.deck_z(f) if zf is None else zf
    zc_ = zf + ceil_h
    tint = WARM[rng.randrange(len(WARM))]
    lit = (rng.random() < 0.86) if lit is None else lit
    kf = 1.0 if lit else 0.25
    ck = 0.22 * kf + 0.04                           # furniture self light
    stats = dict(boxes=0, people=0, cubicles=0, conf=0, plants=0)
    cen = lambda z: G.tube_pt(t, z, 0.0, 0.0)
    O = cen(zf + 2.0)

    def W(u, v, O_=None):
        o_ = O_ or O
        return (o_[0] + ex[0] * u + ey[0] * v, o_[1] + ex[1] * u + ey[1] * v)

    taken = []            # (u0, u1, v0, v1) footprints (local, around O)

    def free(u0, u1, v0, v1, m=0.4):
        for (a0, a1, b0, b1) in taken:
            if u0 < a1 + m and u1 > a0 - m and v0 < b1 + m and v1 > b0 - m:
                return False
        return True
    wall_col = (0.19, 0.18, 0.165)
    # ------------------------------------------------------------------ the elevator core (full height)
    O5 = cen(zf + 5.1)
    cu, cv = rng.uniform(-1.4, 1.4), rng.uniform(-0.8, 0.8)
    hu, hv = 2.5, 2.7
    c0 = W(cu - hu, cv - hv, O5)
    obx(off, c0, ex, ey, 0.0, 2 * hu, 0.0, 2 * hv, zf, zc_, (0.14, 0.135, 0.125), 0.12, top=False)
    taken.append((cu - hu - 0.2, cu + hu + 0.2, cv - hv - 0.2, cv + hv + 0.2))
    # re-express the core footprint around O (O5 differs by a small slide): keep the larger box
    for sv in (-1, 1):                                # elevator doors on the two faces toward the windows
        for dd in (-0.9, 0.9):
            pc = W(cu + dd, cv + sv * (hv + 0.03), O5)
            obx(lamp, (pc[0] - ex[0] * 0.55, pc[1] - ex[1] * 0.55), ex, ey, 0.0, 1.1, -0.02, 0.02, zf, zf + 2.4,
                (0.88, 0.95, 1.0), 0.9 * kf + 0.12, top=False)
    obx(lamp, W(cu - hu, cv + hv + 0.03, O5), ex, ey, 0.0, 2 * hu, -0.02, 0.02, zf + 2.55, zf + 2.75, (0.5, 1.0, 0.7),
        1.2 * kf + 0.2, top=False)
    if node_panels is not None:
        node_panels(W(cu, cv + hv + 0.05, O5), ex, ey, zf)
    stats["boxes"] += 3
    # ------------------------------------------------------------------ conference rooms (glass, table, chairs)
    slots = [(-5.0, -4.6), (5.0, -4.6), (-5.0, 4.8), (5.0, 4.8), (0.0, -6.4), (0.0, 6.4)]
    rng.shuffle(slots)
    n_conf = 1 + (rng.random() < 0.7)
    for (su, sv_) in slots:
        if stats["conf"] >= n_conf:
            break
        su += rng.uniform(-0.6, 0.6)
        sv_ += rng.uniform(-0.5, 0.5)
        cw, cd = 4.6 * q + 0.4, 3.4 * q + 0.4
        fp = [W(su + a * cw / 2, sv_ + b * cd / 2) for a in (-1, 1) for b in (-1, 1)]
        if not free(su - cw / 2, su + cw / 2, sv_ - cd / 2, sv_ + cd / 2, 0.3):
            continue
        if not _fits(G, t, fp, zf, zf + 2.9, 0.6):
            continue
        taken.append((su - cw / 2, su + cw / 2, sv_ - cd / 2, sv_ + cd / 2))
        stats["conf"] += 1
        h_g = 2.8 * q
        for (a0, a1, b0, b1) in ((-cw / 2, cw / 2, -cd / 2 - 0.03, -cd / 2 + 0.03),
                                 (-cw / 2, cw / 2, cd / 2 - 0.03, cd / 2 + 0.03),
                                 (-cw / 2 - 0.03, -cw / 2 + 0.03, -cd / 2, cd / 2),
                                 (cw / 2 - 0.03, cw / 2 + 0.03, -cd / 2, cd / 2)):
            obx(glass, W(su, sv_), ex, ey, a0, a1, b0, b1, zf, zf + h_g, (0.7, 0.85, 0.8), 0.0, top=False)
        for a in (-1, 1):                              # frame posts + a rail
            for b in (-1, 1):
                obx(off, W(su + a * cw / 2, sv_ + b * cd / 2), ex, ey, -0.07, 0.07, -0.07, 0.07, zf, zf + h_g,
                    (0.3, 0.32, 0.34), 0.2)
        obx(lamp, W(su, sv_), ex, ey, -cw / 2, cw / 2, -cd / 2, cd / 2, zf + h_g, zf + h_g + 0.04, tint, 1.2 * kf + 0.1,
            top=False)                                  # a lit conference ceiling
        tw_, td_ = 2.5 * q, 1.1 * q
        obx(off, W(su, sv_), ex, ey, -tw_ / 2, tw_ / 2, -td_ / 2, td_ / 2, zf + 0.78 * q, zf + 0.9 * q, (0.36, 0.21, 0.11),
            ck + 0.05)
        obx(off, W(su, sv_), ex, ey, -0.1, 0.1, -0.1, 0.1, zf, zf + 0.78 * q, (0.2, 0.2, 0.22), 0.15)
        seats = []
        for a in (-0.8, 0.0, 0.8):
            for b in (-1, 1):
                seats.append((su + a * tw_ / 2.0 * 1.0, sv_ + b * (td_ / 2 + 0.45 * q), b))
        for (uu, vv, b) in seats:
            pc = W(uu, vv)
            obx(off, (pc[0] - ex[0] * 0.22 * q, pc[1] - ex[1] * 0.22 * q), ex, ey, 0.0, 0.44 * q,
                -0.22 * q, 0.22 * q, zf + 0.35 * q, zf + 0.45 * q, CHAIR[rng.randrange(len(CHAIR))], ck + 0.1)
            if rng.random() < 0.55:
                epy = (-b * ey[0], -b * ey[1])
                person(off, pc[0], pc[1], zf, (epy[1], -epy[0]), epy, person_h, rng, "sit", ck + 0.15)
                stats["people"] += 1
        if rng.random() < 0.5:                         # a presenter standing at the end
            pc = W(su + cw / 2 - 0.7, sv_)
            person(off, pc[0], pc[1], zf, ex, ey, person_h, rng, "stand", ck + 0.15)
            stats["people"] += 1
        obx(lamp, W(su, sv_ - cd / 2 + 0.12), ex, ey, -1.0 * q, 1.0 * q, 0.0, 0.03, zf + 1.2 * q, zf + 2.2 * q,
            (0.7, 0.9, 1.0), 0.6 * kf + 0.1, top=False)  # a wall screen
    # ------------------------------------------------------------------ cubicle rows
    cu_step, cv_step = 2.7, 3.0
    for j in range(-3, 4):
        vj = j * cv_step
        back = 1 if j % 2 == 0 else -1
        for i in range(-4, 5):
            ui = i * cu_step
            if rng.random() < 0.14:
                continue
            u0, u1, v0, v1 = ui - 1.2, ui + 1.2, vj - 1.3, vj + 1.3
            if not free(u0, u1, v0, v1, 0.1):
                continue
            fp = [W(u0, v0), W(u1, v0), W(u1, v1), W(u0, v1)]
            if not _fits(G, t, fp, zf, zf + 1.9, 0.5):
                continue
            taken.append((u0, u1, v0, v1))
            stats["cubicles"] += 1
            ph = 1.6 * q
            pc = W(ui, vj)
            vb = back * 1.2
            obx(off, pc, ex, ey, -1.2, 1.2, vb - 0.04, vb + 0.04, zf, zf + ph, wall_col, ck)                  # back panel
            for sgn in (-1, 1):
                obx(off, pc, ex, ey, sgn * 1.2 - 0.04, sgn * 1.2 + 0.04, vb - back * 2.2, vb, zf, zf + ph, wall_col, ck)
            obx(off, pc, ex, ey, -1.0, 1.0, vb - back * 0.75, vb - back * 0.05, zf + 0.74 * q, zf + 0.82 * q,
                (0.06, 0.065, 0.075), ck)                                                              # desk (charcoal)
            mc = rng.choice(((0.35, 0.9, 1.0), (0.9, 0.95, 1.0), (0.4, 1.0, 0.6), (1.0, 0.75, 0.4)))
            on = rng.random() < 0.45
            obx(lamp, (pc[0] + ey[0] * (vb - back * 0.15), pc[1] + ey[1] * (vb - back * 0.15)), ex, ey, -0.35, 0.35, -0.03,
                0.03, zf + 0.9 * q, zf + 1.3 * q, mc, (1.1 if on else 0.05) * kf + 0.05, top=False)           # monitor
            cy_ = vb - back * 1.15
            obx(off, pc, ex, ey, -0.3, 0.3, cy_ - 0.3, cy_ + 0.3, zf + 0.38 * q, zf + 0.46 * q, CHAIR[rng.randrange(len(CHAIR))], ck + 0.1)
            r_ = rng.random()
            if r_ < 0.17 and lit:
                pp = W(ui, cy_)
                epy = (back * ey[0], back * ey[1])
                person(off, pp[0], pp[1], zf, (epy[1], -epy[0]), epy, person_h, rng, "sit", ck + 0.15)
                stats["people"] += 1
            elif r_ < 0.24 and lit:
                pp = W(ui + rng.uniform(-0.5, 0.5), vj + back * -0.4)
                person(off, pp[0], pp[1], zf, ex, ey, person_h, rng, "stand", ck + 0.15)
                stats["people"] += 1
    # ------------------------------------------------------------------ plants + a few people in the aisles
    tries = 0
    while stats["plants"] < 5 and tries < 80:
        tries += 1
        pu, pv = rng.uniform(-7.5, 7.5), rng.uniform(-7.5, 7.5)
        if not free(pu - 0.5, pu + 0.5, pv - 0.5, pv + 0.5, 0.0):
            continue
        pw = W(pu, pv)
        if not _fits(G, t, [pw], zf, zf + 2.2, 0.8):
            continue
        taken.append((pu - 0.5, pu + 0.5, pv - 0.5, pv + 0.5))
        stats["plants"] += 1
        obx(off, (pw[0] - 0.3, pw[1] - 0.3), (1.0, 0.0), (0.0, 1.0), 0.0, 0.6, 0.0, 0.6, zf, zf + 0.5 * q, (0.14, 0.14, 0.15), ck)
        gh = rng.uniform(1.0, 1.6) * q
        obx(off, (pw[0] - 0.33, pw[1] - 0.33), (1.0, 0.0), (0.0, 1.0), 0.0, 0.66, 0.0, 0.66, zf + 0.5 * q, zf + 0.5 * q + gh,
            (0.08, 0.3, 0.1), 0.22)
        obx(off, (pw[0] - 0.2, pw[1] - 0.2), (1.0, 0.0), (0.0, 1.0), 0.0, 0.4, 0.0, 0.4, zf + 0.5 * q + gh,
            zf + 0.5 * q + gh * 1.5, (0.12, 0.38, 0.14), 0.25)
    for _ in range(int(2 * q) + 2):
        if not lit:
            break
        pu, pv = rng.uniform(-7.0, 7.0), rng.uniform(-7.0, 7.0)
        if not free(pu - 0.4, pu + 0.4, pv - 0.4, pv + 0.4, 0.0):
            continue
        pw = W(pu, pv)
        if not _fits(G, t, [pw], zf, zf + person_h + 0.3, 0.9):
            continue
        a = rng.uniform(0, 2 * math.pi)
        e2 = (math.cos(a), math.sin(a))
        person(off, pw[0], pw[1], zf, e2, (-e2[1], e2[0]), person_h, rng, "walk" if rng.random() < 0.5 else "stand", ck + 0.15)
        stats["people"] += 1
    # ------------------------------------------------------------------ the dropped-ceiling light grid (the main light)
    Oc = cen(zc_)
    for a in range(-5, 6):
        for b in range(-5, 6):
            uu, vv = a * 2.0, b * 2.0
            px, py = Oc[0] + ex[0] * uu + ey[0] * vv, Oc[1] + ex[1] * uu + ey[1] * vv
            fp = [(px + ex[0] * s1 * 0.6 + ey[0] * s2 * 0.6, py + ex[1] * s1 * 0.6 + ey[1] * s2 * 0.6)
                  for s1 in (-1, 1) for s2 in (-1, 1)]
            if not _fits(G, t, fp, zc_, zc_, 0.5):
                continue
            if rng.random() < (0.12 if lit else 0.75):
                continue
            c1 = (px - ex[0] * 0.6 - ey[0] * 0.6, py - ex[1] * 0.6 - ey[1] * 0.6)
            lamp.face([(c1[0], c1[1], zc_ - 0.03),
                       (c1[0] + ex[0] * 1.2, c1[1] + ex[1] * 1.2, zc_ - 0.03),
                       (c1[0] + ex[0] * 1.2 + ey[0] * 1.2, c1[1] + ex[1] * 1.2 + ey[1] * 1.2, zc_ - 0.03),
                       (c1[0] + ey[0] * 1.2, c1[1] + ey[1] * 1.2, zc_ - 0.03)][::-1], tint, 1.0 * kf)
    return stats
