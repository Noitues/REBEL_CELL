"""Street round 2: the facade rhythm and the facade props, as pure seeded rules (no Blender; the scene only builds them).

rule `repetition.guard` (extended, PIPELINE_SPEC 13.1 rank 12; test R-REP-1 on OVERVIEW and DECISION):
  bay rhythm        a per-building motif of bay widths (2-4 bays, jittered per repeat, with feature bays), so no two
                    stretches of a facade share a pitch
  mixed modules     the window module (cell width, slat count, slot spacing) changes between floor bands of one building
  varied floors     floor heights vary inside a building (a tall ground floor, mezzanines, double heights, a short top
                    floor); the floors below a route column's top room stay rigid (rooms sit on real floors, 1.9 BU)
  setbacks          the facade of a tall building steps back above a floor, with a lit ledge
  balconies         slabs with a rail and a lit door on some floors of glass / panel / atrium faces
rule `props.facade` (PIPELINE_SPEC 13.1 rank 2, `dressing.signs`; test R-DET-2): AC units, pipes, awnings, small lit signs,
  lit rooms on the street faces. Per-building art stream keyed by the building id (spec 3.5). No prop in front of a route
  room opening (spec 12.4 item 5: 0.15 BU lateral, vertical overlap, depth to the kerb; solid items only), none on a
  hero sign, none on another prop.
All numbers come from r2_config. Draws come from the stream handed in by the caller, so adding a building never moves
another one's rhythm.
"""
import math


# ---------------------------------------------------------------- rhythm
def _pick(r, items, weights=None):
    return r.choices(items, weights=weights)[0] if weights else items[r.randrange(len(items))]


def make_rhythm(r, kit, wdt, h, cfg, pal, rigid_top=None, fl=1.9):
    """The rhythm record of one building (JSON-safe). `wdt` = its street face width, `h` = its height (BU), `rigid_top` =
    the top of the highest route room when it is a route column (floors below stay at the 1.9 BU pitch)."""
    nfl = max(1, int(round(h / fl)))
    # bay rhythm: a motif of 2-4 multipliers, repeated with a jitter, with an occasional feature bay
    mot = [_pick(r, cfg["bay_mults"]) for _ in range(r.randint(*cfg["motif_len"]))]
    lo_m, hi_m = min(cfg["bay_mults"]), max(cfg["bay_mults"])
    if max(mot) / min(mot) < 1.9:                 # a motif needs contrast, else it is a uniform grid
        mot[0], mot[-1] = _pick(r, [m for m in cfg["bay_mults"] if m <= 0.85]), _pick(r, [m for m in cfg["bay_mults"] if m >= 1.6])
    nb = int(wdt / 0.9) + 6
    bays = []
    for i in range(nb):
        m = mot[i % len(mot)] * (1.0 + r.uniform(-cfg["bay_jitter"], cfg["bay_jitter"]))
        if r.random() < cfg["feature_bay_p"]:
            m = max(cfg["bay_mults"]) * r.uniform(1.0, 1.25)
        bays.append(round(m, 3))
    # floor heights: multipliers per floor (the ground floor is tall, the top is short, mezzanines and doubles between)
    fm = []
    for j in range(nfl):
        m = _pick(r, cfg["floor_mults"])
        if r.random() < cfg["p_double"] and 0 < j < nfl - 1:
            m = cfg["double_mult"]
        fm.append(m)
    if rigid_top is None:
        fm[0] = r.uniform(*cfg["ground_mult"])
    if nfl > 3 and rigid_top is None:
        fm[-1] = r.uniform(*cfg["top_mult"])
    # mixed window modules: a module per floor band of 2-4 floors, never the same as the band below
    mods, band, mprev = [], 0, r.randrange(3)
    j = 0
    while j < nfl:
        ln = r.randint(*cfg["band_floors"])
        m = mprev if band == 0 else _pick(r, [x for x in range(3) if x != mprev])
        if r.random() > cfg["p_mixed_modules"]:
            m = mprev
        mods += [m] * ln
        mprev, band, j = m, band + 1, j + ln
    # setback: above a floor, the facade steps back
    setback = None
    if nfl >= cfg["setback_min_floors"] and r.random() < cfg["p_setback"] and kit != "lit_atrium":
        lo = max(int(nfl * cfg["setback_from"][0]), int((rigid_top or 0.0) / fl) + 1)
        hi = max(lo, int(nfl * cfg["setback_from"][1]))
        setback = dict(floor=r.randint(lo, hi), d=round(r.uniform(*cfg["setback_depth"]), 2))
    # balconies: floor, centre (face fraction), span (BU); not on concrete_band (its faces are not per-cell) nor on rooms
    balc = []
    if kit != "concrete_band":
        lo_f = max(2, int((rigid_top or 0.0) / fl) + 1)
        for j in range(lo_f, nfl - 1):
            if r.random() < cfg["p_balcony_floor"]:
                bw = r.uniform(*cfg["balcony_w"])
                c = r.uniform(0.15, 0.85)
                balc.append(dict(floor=j, c=round(c, 3), w=round(min(bw, max(0.9, wdt * 0.6)), 2), depth=round(r.uniform(*cfg["balcony_depth"]), 2),
                                 lit=r.random() < 0.55))
    return dict(bays=bays, phase=r.randrange(len(bays)), fm=[round(x, 3) for x in fm], mods=mods, setback=setback, balc=balc,
                rigid_top=rigid_top, acc=list(pal[r.randrange(len(pal))]), tone=list(cfg["cell_tone"]), relief=cfg["cell_relief"],
                tones=[list(t) for t in r.sample(list(cfg["window_tone_pool"]), cfg["window_tones"])])


def floor_bounds(rh, z0, h, fl=1.9):
    """Floor boundary heights (absolute z, nf + 1 values) of a face of height h starting at z0. Without a rhythm the
    floors are uniform. Route columns: the floors under rigid_top keep the 1.9 BU pitch."""
    nf = max(1, int(round(h / fl)))
    if not rh or not rh.get("fm"):
        return [z0 + h * j / nf for j in range(nf + 1)]
    rt = rh.get("rigid_top")
    nrig = 0
    if rt and rt > z0:
        nrig = min(nf - 1, int(math.ceil((rt - z0) / fl - 1e-6)))
    hr = nrig * fl
    free = [rh["fm"][(nrig + k) % len(rh["fm"])] for k in range(nf - nrig)]
    sc = (h - hr) / max(1e-6, sum(free))
    zs = [z0 + fl * j for j in range(nrig + 1)]
    for m in free:
        zs.append(zs[-1] + m * sc)
    zs[-1] = z0 + h
    return zs


def bay_edges(L, cw, rh, band):
    """The bay edges (along-face fractions) of one floor band: widths cw x the rhythm's multipliers, phase shifted per band,
    scaled so they close at the face end."""
    if not rh:
        nu = max(1, int(round(L / cw)))
        return [(i / nu, (i + 1) / nu) for i in range(nu)]
    bays = rh["bays"]
    ph = rh["phase"] + band * 3
    w, tot, i = [], 0.0, 0
    while tot < L - 0.05:
        v = cw * bays[(ph + i) % len(bays)]
        w.append(v)
        tot += v
        i += 1
    if len(w) > 1 and (L - (tot - w[-1])) < 0.45 * cw:       # a sliver at the end joins the previous bay
        w.pop()
    s = L / sum(w)
    out, u = [], 0.0
    for v in w:
        out.append((u / L, min(1.0, (u + v * s) / L)))
        u += v * s
    return out


def floor_inset(rh, j):
    """Setback depth in force on floor j."""
    sb = rh.get("setback") if rh else None
    return sb["d"] if sb and j >= sb["floor"] else 0.0


def floor_module(rh, j, module):
    """Window module of floor j."""
    if not rh or not rh.get("mods"):
        return module
    return rh["mods"][j % len(rh["mods"])]


# ---------------------------------------------------------------- props
def _hit(a, b, pad=0.0):
    return a[0] < b[2] + pad and a[2] > b[0] - pad and a[1] < b[3] + pad and a[3] > b[1] - pad


def prop_hits_opening(p, rooms, axis, line, margin):
    """Spec 12.4 item 5: a prop is blocked when it overlaps an opening laterally within `margin`, overlaps it vertically,
    and stands between the opening's plane and the kerb (it is not behind the opening)."""
    sd = abs(p["face"] + p["out"] * p["depth"] - line)        # the prop's street-side distance from the centre line
    for r in rooms.values():
        us = [q[axis] for q in r["front"]]
        zs = [q[2] for q in r["front"]]
        fplane = r["front"][0][1 - axis]
        if p["u0"] < max(us) + margin and p["u1"] > min(us) - margin and p["z0"] < max(zs) and p["z1"] > min(zs):
            if sd <= abs(fplane - line) + 0.25:
                return True
    return False


def make_props(r, uid, b, face_frame, axis, line, rh, pal, rooms, rects, cfg, floors_z, rigid_top, nrm_open):
    """Props on one building's street face. Returns a list of dicts (u0, u1, z0, z1 along the face and height; depth out of
    the face; kind and colour). `rects` (list of [u0, z0, u1, z1]) are no-go areas on the face (hero signs, shopfront, rooms);
    accepted props are appended to it so props never overlap each other."""
    bu0, bu1, face, out = face_frame
    wdt = bu1 - bu0
    h = b["h"]
    area = wdt * max(0.0, h - 2.0)
    quiet = r.random() < cfg["p_quiet"]
    n = int(round(area * cfg["density"] * (0.6 + 0.8 * r.random()) * (cfg["quiet_k"] if quiet else 1.0)))
    n = max(1 if quiet else (cfg["min_per_face"] if wdt > 3.0 else 1), min(n, cfg["max_per_face"]))
    kinds = list(cfg["kinds"].keys())
    weights = [cfg["kinds"][k] for k in kinds]
    props = []
    tries = 0
    nfl = len(floors_z) - 1
    while len(props) < n and tries < n * 14:
        tries += 1
        k = _pick(r, kinds, weights)
        j = r.randrange(1, max(2, nfl - 1)) if nfl > 2 else 0       # never the ground floor (the shopfront owns it)
        zb, zt = floors_z[j], floors_z[min(j + 1, nfl)]
        if zt > h - 0.5 or zb < 1.5:
            continue
        pc = pal[r.randrange(len(pal))]
        if k == "ac":
            w = r.uniform(0.7, 1.05)
            u0 = bu0 + 0.25 + r.random() * max(0.01, wdt - w - 0.5)
            p = dict(kind=k, u0=u0, u1=u0 + w, z0=zb + 0.28, z1=zb + 0.28 + r.uniform(0.5, 0.68), depth=r.uniform(0.38, 0.55), col=[0.30, 0.30, 0.34],
                     led=r.random() < 0.45, ledcol=list(pc))
        elif k == "pipe":
            u = bu0 + 0.2 + (r.random() < 0.5) * max(0.01, wdt - 0.4)
            za = r.uniform(0.3, max(0.5, h * 0.25))
            zbb = min(h - 0.4, za + r.uniform(3.0, 9.0))
            p = dict(kind=k, u0=u - 0.09, u1=u + 0.09, z0=za, z1=zbb, depth=0.2, col=[0.21, 0.21, 0.25], elbow=r.random() < 0.6)
        elif k == "awning":
            w = r.uniform(1.3, min(3.4, max(1.4, wdt - 0.5)))
            u0 = bu0 + 0.25 + r.random() * max(0.01, wdt - w - 0.5)
            p = dict(kind=k, u0=u0, u1=u0 + w, z0=zb + 1.0, z1=zb + 1.35, depth=r.uniform(0.6, 0.95),
                     col=[v * 0.8 for v in pc], trim=r.random() < 0.55, trimcol=list(pc))
        elif k == "small_sign":
            w = r.uniform(0.55, 1.35)
            hh = w * r.uniform(0.42, 0.75)
            blade = r.random() < 0.3
            if blade:
                w, hh = r.uniform(0.28, 0.42), r.uniform(1.0, 1.9)
            u0 = bu0 + 0.2 + r.random() * max(0.01, wdt - w - 0.4)
            z0 = zb + r.uniform(0.2, max(0.21, (zt - zb) - hh))
            p = dict(kind=k, u0=u0, u1=u0 + w, z0=z0, z1=z0 + hh, depth=0.12 + (0.25 if blade else 0.0), col=list(pc), blade=blade,
                     bars=r.randint(1, 3))
        elif k == "lit_room":
            w = r.uniform(0.9, 2.0)
            u0 = bu0 + 0.3 + r.random() * max(0.01, wdt - w - 0.6)
            wc = [(1.0, 0.7, 0.35), (0.5, 0.92, 1.0), (1.0, 0.5, 0.8), (1.0, 0.85, 0.6)][r.randrange(4)]
            p = dict(kind=k, u0=u0, u1=u0 + w, z0=zb + 0.35, z1=zb + 1.25, depth=0.05, col=[v * (0.8 + 0.2 * r.random()) for v in wc], mull=r.random() < 0.6)
        else:
            continue
        box = [p["u0"], p["z0"], p["u1"], p["z1"]]
        if any(_hit(box, q, 0.2) for q in rects):
            continue
        p.update(id="%s_%s_%d" % (k, uid, len(props)), key=uid, face=face, out=out, axis=axis, solid=k in ("ac", "pipe", "awning"))
        if prop_hits_opening(p, rooms, axis, line, cfg["opening_margin"]):
            continue
        rects.append(box)
        props.append(p)
    return props
