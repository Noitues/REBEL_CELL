"""Storyboard v3 proof: ONE CONTINUOUS CITY. The netrun street is derived from the city map itself (no separate street
set, no remap transform). Pure python (Blender imports it too).

Derivation rules (NOTES "One continuous city"; numbers in RULES below):
  1. The link. The selected Site's border link on the map (the one the plan pencil follows in beat 2): a polyline of
     street-centre points in lots.
  2. The netrun street. Each straight leg of the link, on each side, has a FRONTAGE: the map buildings standing on the
     street level (z0 = 0) whose near edge lies within `front_band` BU of the leg's centre line and that overlap the leg.
     The street is the leg + side whose frontage best fits the run: score = sum over the run's layers of whether the
     next unused frontage building (in link order) has enough floors for that layer's rooms; ties by more floors, then
     by the start-on-the-left orientation of the side view. The route columns are the frontage buildings in link order
     from the relay end (a building too short for its layer is skipped, so the run uses real buildings only).
  3. Floors. A building's floors are its real height / `floor_bu` (the mainline window pitch row: 1.9 BU). Rooms sit on
     real floors: the layer's rooms take consecutive floors from `base_floor`, slot order bottom up.
  4. room_floor_span (1-2): a room spans 1 floor, or 2 consecutive floors as a double-height cutaway when one floor
     would project smaller than the camera's room-size target at OVERVIEW (`room_px_target`), and only if the building
     has the floors for it. The building is never rescaled.
  5. Room boxes. On the building's street face, inset `room_inset` BU from its corners, `room_depth` BU deep; the wall
     over each room is its own object (the REVEAL dissolves it); the rest of the facade is the building's own.
  6. The camera. The street OVERVIEW and DECISION poses are the v3_dynamic rig's, solved on these rooms; the camera looks
     at the street face (its normal), the side view's yaw bias follows the start's side of the screen.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "m44"))
os.environ.setdefault("NET36", "net_scope.json")
sys.dont_write_bytecode = True
import layout36 as L  # noqa: E402
import sgraph3 as G  # noqa: E402

RULES = dict(front_band=(0.8, 6.5), floor_bu=1.9, base_floor=0, room_inset=0.45, room_depth=2.6, room_px_target=46.0,
             min_width=2.5, max_setback=0.6, extend=(12.0, 60.0))


def floors(b):
    """Usable floors of a frontage building: real floors (height / floor_bu); on a tapered building only the floors
    whose facade setback at the room top stays within max_setback (the face slopes in toward the top)."""
    n = int(b["h"] / RULES["floor_bu"])
    if b["ts"] >= 0.99:
        return n
    depth = (b["y1"] - b["y0"]) if b.get("axis", 0) == 0 else (b["x1"] - b["x0"])
    k = 0
    while k < n:
        z = (k + 1) * RULES["floor_bu"]
        if (1 - b["ts"]) * depth / 2 * z / b["h"] > RULES["max_setback"]:
            break
        k += 1
    return k
SITE, RELAY = "m2_d", "m1_d"
LAYPATH = os.path.join(HERE, "scratch", "layout", "unified.json")
KH = L.U / 41.64 * 1.15


def lay():
    return json.load(open(LAYPATH))


def merged_buildings():
    """Map buildings as the game reads them: a street-level base plus the stacked parts above it (z0 > 0, footprint
    inside the base) are ONE building, its height the top of the highest part."""
    B = [bld_info(b) for b in lay()["buildings"]]
    bases = [b for b in B if b["z0"] <= 0.05]
    ups = [b for b in B if b["z0"] > 0.05]
    for b in bases:
        b["top"] = b["h"]
        b["parts"] = [b["key"]]
    for u in ups:
        cx, cy = (u["x0"] + u["x1"]) / 2, (u["y0"] + u["y1"]) / 2
        for b in bases:
            if b["x0"] <= cx <= b["x1"] and b["y0"] <= cy <= b["y1"]:
                b["top"] = max(b["top"], u["z0"] + u["h"])
                b["parts"].append(u["key"])
                break
    for b in bases:
        b["h"] = b["top"]
    return bases


def link_pts():
    net = L.load_net()
    lk = next(l for l in net["links"] if {l["a"], l["b"]} == {RELAY, SITE})
    pts = lk["pts"] if lk["a"] == RELAY else list(reversed(lk["pts"]))
    return [L.W(p) for p in pts]


def bld_info(b):
    q = [L.W(p) for p in b["q"]]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return dict(key=b["key"], q=q, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), z0=b["z0"] * KH, h=b["h"] * KH,
                ts=b["ts"])


def frontage(B, a, c, side):
    """Buildings fronting the leg a -> c on `side` (+1 = left of the walking direction), ordered from a."""
    ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
    d = 1 if c[ax] > a[ax] else -1
    lo, hi = sorted((a[ax], c[ax]))
    # left of the walking direction: along +x -> +y; along -x -> -y; along +y -> -x; along -y -> +x
    if ax == 0:
        nrm = (0.0, side * d)
    else:
        nrm = (-side * d, 0.0)
    out = []
    for b in B:
        if b["z0"] > 0.05:
            continue
        if ax == 0:
            a0, a1 = b["x0"], b["x1"]
            near = b["y0"] if nrm[1] > 0 else b["y1"]
            dist = (near - a[1]) * nrm[1]
        else:
            a0, a1 = b["y0"], b["y1"]
            near = b["x0"] if nrm[0] > 0 else b["x1"]
            dist = (near - a[0]) * nrm[0]
        if a1 > lo and a0 < hi and RULES["front_band"][0] < dist < RULES["front_band"][1] and a1 - a0 >= RULES["min_width"]:
            mid = (a0 + a1) / 2
            out.append(dict(b, along=(mid - a[ax]) * d, face=near, nrm=nrm, axis=ax, dirn=d))
    out.sort(key=lambda r: (r["along"], r["key"]))
    return out


def layers():
    return [sorted([i for i in G.NODES if G.LAYER[i] == l], key=lambda i: G.K[i]) for l in range(G.LAST + 1)]


def assign(front, span=1):
    """Layer -> frontage building, in link order, skipping a building without the floors for that layer."""
    LY = layers()
    out, k = [], 0
    for l, rooms in enumerate(LY):
        need = RULES["base_floor"] + len(rooms) * span
        while k < len(front) and floors(front[k]) < need:
            k += 1
        if k >= len(front):
            return out, False
        out.append((l, front[k]))
        k += 1
    return out, True


def choose_street(B=None):
    """The leg + side whose frontage fits the run best. A leg is extended along its own street line beyond its ends
    (the street the link runs on) by up to `extend` BU when its own length has too few buildings."""
    B = B or merged_buildings()
    pts = link_pts()
    best = None
    for li, (a0_, c0_) in enumerate(zip(pts, pts[1:])):
        L_ = math.hypot(c0_[0] - a0_[0], c0_[1] - a0_[1])
        ux, uy = (c0_[0] - a0_[0]) / L_, (c0_[1] - a0_[1]) / L_
        e = RULES["extend"]
        a, c = (a0_[0] - ux * e[0], a0_[1] - uy * e[0]), (c0_[0] + ux * e[1], c0_[1] + uy * e[1])
        for side in (1, -1):
            fr = frontage(B, a, c, side)
            asg, ok = assign(fr)
            nfl = sum(floors(b) for _, b in asg)
            # orientation: the camera faces the street face (-nrm); the start (leg start a) on the screen's left?
            nrm = fr[0]["nrm"] if fr else (0, 1)
            fwd = (nrm[0], nrm[1])
            right = (fwd[1], -fwd[0])
            walk = (c[0] - a[0], c[1] - a[1])
            start_left = (walk[0] * right[0] + walk[1] * right[1]) > 0
            score = (len(asg), nfl, 1 if start_left else 0)
            if best is None or score > best[0]:
                best = (score, li, side, a, c, fr, asg, start_left)
    return best


def room_boxes(asg, span):
    """node id -> dict(front=[4 world pts], box=(..), floor, span, bld). The street face is the building's near face."""
    LY = layers()
    rooms = {}
    for l, b in asg:
        ax, nrm = b["axis"], b["nrm"]
        span_l = span if floors(b) >= RULES["base_floor"] + len(LY[l]) * span else 1
        if ax == 0:
            u0, u1 = b["x0"] + RULES["room_inset"], b["x1"] - RULES["room_inset"]
        else:
            u0, u1 = b["y0"] + RULES["room_inset"], b["y1"] - RULES["room_inset"]
        for k, i in enumerate(LY[l]):
            f = RULES["base_floor"] + k * span_l
            z0 = f * RULES["floor_bu"] + 0.12
            z1 = (f + span_l) * RULES["floor_bu"] - 0.12
            face = b["face"]
            back = face + RULES["room_depth"] * (nrm[1] if ax == 0 else nrm[0])
            if ax == 0:
                fr = [(u0, face, z0), (u1, face, z0), (u1, face, z1), (u0, face, z1)]
                bk = [(u0, back, z0), (u1, back, z0), (u1, back, z1), (u0, back, z1)]
            else:
                fr = [(face, u0, z0), (face, u1, z0), (face, u1, z1), (face, u0, z1)]
                bk = [(back, u0, z0), (back, u1, z0), (back, u1, z1), (back, u0, z1)]
            rooms[i] = dict(front=fr, back=bk, floor=f, span=span_l, bld=b["key"], parts=b.get("parts", [b["key"]]),
                            layer=l, kind=G.KIND[i])
    return rooms


# ---------------------------------------------------------------- cameras (unified world: yaw convention of layout36)
W_, H_ = 1920, 1080
USE = (300.0, 138.0, 1900.0, 1012.0)


def cam(target, yaw, pitch, dist, lens, sx=0.0, sy=0.0):
    r, u, f = L.basis(dict(yaw=yaw, pitch=pitch))
    loc = [target[i] - f[i] * dist for i in range(3)]
    return dict(yaw=yaw, pitch=pitch, target=list(target), ortho=dist * 36.0 / lens, dist=dist,
                persp=dict(loc=loc, lens=lens, sx=sx, sy=sy))


def proj(c, p):
    return L.project(c, p[0], p[1], p[2], W_, H_)


def frame(pts, yaw, pitch, lens, fw, fh, bias=0.0):
    xs, ys, zs = zip(*pts)
    F = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    uw, uh = USE[2] - USE[0], USE[3] - USE[1]
    lo, hi = 2.0, 4000.0
    for _ in range(60):
        d = math.sqrt(lo * hi)
        c = cam(F, yaw, pitch, d, lens)
        q = [proj(c, p) for p in pts]
        bw = max(p[0] for p in q) - min(p[0] for p in q)
        bh = max(p[1] for p in q) - min(p[1] for p in q)
        if max(bw / (fw * uw), bh / (fh * uh)) > 1.0:
            lo = d
        else:
            hi = d
    c = cam(F, yaw, pitch, hi, lens)
    q = [proj(c, p) for p in pts]
    cx = (max(p[0] for p in q) + min(p[0] for p in q)) / 2
    cy = (max(p[1] for p in q) + min(p[1] for p in q)) / 2
    ucx, ucy = (USE[0] + USE[2]) / 2 + bias * uw, (USE[1] + USE[3]) / 2
    sx = (cx - ucx) / W_
    sy = -(cy - ucy) / W_
    return cam(F, yaw, pitch, hi, lens, sx, sy)


def street_yaw(nrm):
    """The camera looks at the street face (from the street into the building): fwd = nrm, as a layout36 yaw."""
    return math.degrees(math.atan2(nrm[1], nrm[0]))


_FPX = [0.0]


def derive(span=None):
    """The whole derivation: street, assignment, rooms, the OVERVIEW / DECISION poses; span by the room-size rule."""
    best = choose_street()
    score, li, side, a, c, fr, asg, start_left = best
    nrm = fr[0]["nrm"]
    y0 = street_yaw(nrm)
    sgn = 1.0 if start_left else -1.0          # the rig's yaw bias toward the unexplored side of the screen

    def poses(rooms):
        pts = [p for r in rooms.values() for p in r["front"] + r["back"]]
        ov = frame(pts, y0 - sgn * 7.2, 6.0, 40.0, 0.95, 0.90)
        cur = [G.WALK_START[-1]]
        opts = G.states(G.WALK_START)[1]
        dpts = [p for i in cur + opts for p in rooms[i]["front"] + rooms[i]["back"]]
        dec = frame(dpts, y0 - sgn * 24.0, 9.0, 30.0, 0.66, 0.70, bias=sgn * 0.10)
        return ov, dec
    if span is None:
        rooms = room_boxes(asg, 1)
        ov, dec = poses(rooms)
        r0 = rooms[G.WALK_START[-1]]
        fpx = abs(proj(ov, r0["front"][0])[1] - proj(ov, r0["front"][3])[1])
        # the double-height cutaway where one floor projects under the target; per building, only where the building
        # has the floors for it (room_boxes falls back to 1 floor per room otherwise): the columns stay the same
        span = 2 if fpx < RULES["room_px_target"] else 1
        _FPX[0] = fpx
    rooms = room_boxes(asg, span)
    ov, dec = poses(rooms)
    return dict(floor_px=_FPX[0], leg=li, side=side, a=a, c=c, nrm=nrm, start_left=start_left, span=span,
                columns=[(l, b["key"]) for l, b in asg], route_keys=[k for _, b in asg for k in b.get("parts", [b["key"]])], street_len=math.hypot(c[0] - a[0], c[1] - a[1]),
                rooms=rooms, overview=ov, decision=dec, frontage=[(b["key"], round(b["h"], 1), floors(b), round(b["ts"], 2)) for b in fr])


if __name__ == "__main__":
    d = derive()
    print("leg", d["leg"], d["a"], "->", d["c"], "side", d["side"], "nrm", d["nrm"], "start_left", d["start_left"],
          "span", d["span"])
    print("frontage", d["frontage"])
    print("columns", d["columns"])
    for i in sorted(d["rooms"], key=lambda i: (G.LAYER[i], G.K[i])):
        r = d["rooms"][i]
        print(i, r["kind"], "floor", r["floor"], "span", r["span"], [tuple(round(v, 1) for v in r["front"][0])])
    for nm in ("overview", "decision"):
        c = d[nm]
        print(nm, "yaw %.1f pitch %.1f dist %.1f lens %.0f" % (c["yaw"], c["pitch"], c["dist"], c["persp"]["lens"]),
              [round(v, 1) for v in c["persp"]["loc"]], "shift %.3f %.3f" % (c["persp"]["sx"], c["persp"]["sy"]))
