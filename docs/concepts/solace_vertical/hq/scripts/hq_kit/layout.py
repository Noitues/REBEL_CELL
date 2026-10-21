"""hq_kit.layout: the generic HQ compound + run generator (pure python, no Blender, no PIL).

    from hq_kit.layout import Compound
    C = Compound(cfg)                     # cfg = an HQ's "compound" dict (+ "watch" for the scan rule), see below

A compound is a square stepped landmark centred on the origin (x east, y north, z up, BU). The run is a chain of
SEGMENTS; segment r holds rows[r] rooms in the face of a tier:
    path "spiral"      segment r on tier r, face (face0 + r) mod 4  (a helix round the landmark, counter-clockwise)
    path "switchback"  every segment on face face0, tier r, walked left-right then right-left (round 43 Halcyon)
    path "faces"       explicit cfg["faces"][r] and cfg["tiers"][r] per segment
Links (types): "ramp" (start -> first room), "gallery" (same segment), "corner_stair" (segment end -> next segment on
the next face), "stair" (switchback ends, same face), "climb" (shortcut straight up the outside of a face, room ->
the room directly above on the same face; skips the segments between), "core_lift" (last room -> the TARGET vault).
The TARGET vault sits on tier len(rows), open on all four faces.

Config keys (defaults in DEFAULTS): rows, path, face0, room_w, room_h, room_d, gap, tier_h, podium_h, podium_x,
tier_margin, target_w, target_h, crown_h, stair_run, start {x, y}, kinds (cycled by room number), max_shortcuts,
shortcuts ("climb" | "none" | explicit [[a, b], ...]), eye {z_above, ...} (the landmark's top piece).
Scan rule cfg["watch"] (optional): {"type": "lighthouse", "phase", "sector" (deg), "step" (deg per step)} or
{"type": "face", "phase"} (one whole face per step) or {"type": "none"}.

Graph API (r3 sgraph names, walked-aware): NODES, KIND, ROW, K, U, FACE, LAYER, ORDER, SHORTCUTS, PATH,
edges(walked), succ(n, walked), reach(froms, walked), states(walked) -> (state, options), edge_states(walked, st),
branch(o, walked), shortcuts_used(walked), edge_type(a, b), edge_path(a, b), door(i, side), room_box/room_front/
room_corners/room_center/room_z, half_size(r), tier_floor(r), tiers(), fp(face, d, u, z), start_pos(), eye_pos(),
crown_top(), watch_az(step), room_az(i), in_watch(i, step), scanned(walked) -> (rooms, az), dump(path, walked).
Ties are broken by path order (the node number), never by dict order.
"""
import json
import math

FACES = ["S", "E", "N", "W"]
N = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]       # outward normals
T = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]       # walking tangents (counter-clockwise from above)

DEFAULTS = dict(rows=[6, 5, 4, 3, 2, 1], path="spiral", face0=0, room_w=14.0, room_h=8.0, room_d=10.0, gap=9.0,
                tier_h=13.0, podium_h=6.0, podium_x=96.0, tier_margin=4.0, target_w=22.0, target_h=10.0, crown_h=7.0,
                stair_run=20.0, start={"x": -88.0, "y": -112.0}, kinds=["router", "terminal", "router", "elite", "modem"],
                max_shortcuts=2, shortcuts="climb", eye={"z_above": 20.0, "h": 24.0, "w": 42.0})
SLAB = 1.0
DOOR_Z = 1.6
YF = 0.7          # links run this far in front of the facade (r3 rule)


class Compound:
    def __init__(self, cfg, watch=None):
        c = dict(DEFAULTS)
        c.update(cfg)
        self.cfg = c
        self.watch = watch or cfg.get("watch") or {"type": "none"}
        self.ROWS = list(c["rows"])
        self.R = len(self.ROWS)
        self.RW, self.RH, self.RD = c["room_w"], c["room_h"], c["room_d"]
        self.PITCH = self.RW + c["gap"]
        self.TH = c["tier_h"]
        self.PODIUM = c["podium_h"]
        self._segments()
        self.NODES = ["start"]
        self.ROW, self.K, self.U, self.FACE = {}, {}, {}, {}
        n = 0
        for r, cnt in enumerate(self.ROWS):
            for k in range(cnt):
                n += 1
                nid = "n%d" % n
                self.NODES.append(nid)
                self.ROW[nid], self.K[nid] = r, k
                self.U[nid] = (k - (cnt - 1) / 2.0) * self.PITCH * self.SEG_DIR[r]   # walked along +/- the tangent
                self.FACE[nid] = self.SEG_FACE[r]
        self.NODES.append("srv")
        self.ROW["start"], self.K["start"], self.U["start"], self.FACE["start"] = -1, 0, 0.0, self.SEG_FACE[0]
        self.ROW["srv"], self.K["srv"], self.U["srv"], self.FACE["srv"] = self.R, 0, 0.0, -1
        self.N_ROOMS = n
        self.ORDER = {x: i for i, x in enumerate(self.NODES)}
        self.KIND = {"start": "start", "srv": "target"}
        for i in range(1, n + 1):
            self.KIND["n%d" % i] = c["kinds"][i % len(c["kinds"])]
        self.LAYER = {x: self.ROW[x] + 1 for x in self.NODES}
        self.PATH = [(self.NODES[k], self.NODES[k + 1]) for k in range(len(self.NODES) - 1)]
        self.SHORTCUTS = self._shortcuts()

    # ---------------------------------------------------------------- segments
    def _segments(self):
        c, R = self.cfg, self.R
        if c["path"] == "spiral":
            self.SEG_FACE = [(c["face0"] + r) % 4 for r in range(R)]
            self.SEG_TIER = list(range(R))
            self.SEG_DIR = [1] * R
        elif c["path"] == "switchback":
            self.SEG_FACE = [c["face0"]] * R
            self.SEG_TIER = list(range(R))
            self.SEG_DIR = [1 if r % 2 == 0 else -1 for r in range(R)]
        else:
            self.SEG_FACE = list(c["faces"])
            self.SEG_TIER = list(c.get("tiers", range(R)))
            self.SEG_DIR = list(c.get("dirs", [1] * R))

    # ---------------------------------------------------------------- geometry
    def tier_floor(self, r):
        return self.PODIUM + r * self.TH

    def half_size(self, r):
        if r >= self.R:
            return self.cfg["target_w"] / 2.0 + 2.0
        return max(self.ROWS) * self.PITCH / 2.0 + self.cfg["tier_margin"] - r * self.PITCH / 2.0

    def tiers(self):
        return [dict(r=r, hs=self.half_size(r), z0=self.tier_floor(r), z1=self.tier_floor(r) + self.TH)
                for r in range(self.R + 1)]

    @staticmethod
    def fp(f, d, u, z):
        """Face frame -> world: d along the outward normal from the centre, u along the walking tangent."""
        n, t = N[f], T[f]
        return (n[0] * d + t[0] * u, n[1] * d + t[1] * u, z)

    def tier_of(self, i):
        r = self.ROW[i]
        return self.SEG_TIER[r] if 0 <= r < self.R else r

    def room_z(self, i):
        z0 = self.tier_floor(self.tier_of(i)) + SLAB
        return z0, z0 + (self.cfg["target_h"] if i == "srv" else self.RH)

    def room_front(self, i, f=None):
        f = self.FACE[i] if f is None else f
        hs = self.half_size(self.tier_of(i))
        w = self.cfg["target_w"] if i == "srv" else self.RW
        z0, z1 = self.room_z(i)
        u = self.U[i]
        return [self.fp(f, hs, u - w / 2, z0), self.fp(f, hs, u + w / 2, z0), self.fp(f, hs, u + w / 2, z1),
                self.fp(f, hs, u - w / 2, z1)]

    def room_corners(self, i):
        if i == "start":
            x, y, z = self.start_pos()
            return [(x + dx, y + dy, z + dz) for dx in (-5, 5) for dy in (-4, 4) for dz in (0, 7)]
        f = self.FACE[i] if self.FACE[i] >= 0 else 0
        hs = self.half_size(self.tier_of(i))
        w = self.cfg["target_w"] if i == "srv" else self.RW
        z0, z1 = self.room_z(i)
        return [self.fp(f, d, u, z) for d in (hs, hs - self.RD) for u in (self.U[i] - w / 2, self.U[i] + w / 2)
                for z in (z0, z1)]

    def room_center(self, i):
        c = self.room_corners(i)
        return tuple(sum(p[k] for p in c) / len(c) for k in range(3))

    def start_pos(self):
        s = self.cfg["start"]
        return (s["x"], s["y"], 0.0)

    def crown_top(self):
        return self.tier_floor(self.R) + self.TH + self.cfg["crown_h"]

    def eye_pos(self):
        return (0.0, 0.0, self.crown_top() + self.cfg["eye"]["z_above"])

    # ---------------------------------------------------------------- shortcuts
    def _shortcuts(self):
        sc = self.cfg["shortcuts"]
        if sc == "none":
            return []
        if isinstance(sc, (list, tuple)):
            return [tuple(e) for e in sc]
        out = []                                  # "climb": straight up the outside of a face, same u
        rooms = [x for x in self.NODES if x not in ("start", "srv")]
        for a in rooms:
            above = [b for b in rooms if self.FACE[b] == self.FACE[a] and self.tier_of(b) > self.tier_of(a) + 1
                     and abs(self.U[b] - self.U[a]) <= 1.0 and self.ORDER[b] > self.ORDER[a] + 1]
            if above:
                b = min(above, key=lambda x: (self.tier_of(x), self.ORDER[x]))
                out.append((a, b))
        return sorted(out, key=lambda e: (self.ORDER[e[0]], self.ORDER[e[1]]))

    def shortcuts_used(self, walked):
        return sum(1 for e in zip(walked[:-1], walked[1:]) if e in self.SHORTCUTS)

    # ---------------------------------------------------------------- graph
    def edges(self, walked):
        out = set(self.PATH)
        if self.shortcuts_used(walked) < self.cfg["max_shortcuts"]:
            out |= set(self.SHORTCUTS)
        out |= set(e for e in zip(walked[:-1], walked[1:]) if e in self.SHORTCUTS)
        return sorted(out, key=lambda e: (self.ORDER[e[0]], self.ORDER[e[1]]))

    def succ(self, n, walked):
        return sorted((b for a, b in self.edges(walked) if a == n), key=lambda b: self.ORDER[b])

    def reach(self, froms, walked):
        seen, stack = set(), list(froms)
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.succ(n, walked))
        return seen

    def states(self, walked):
        """node -> current | walked | option | target | reach | grey (past / cut off)."""
        cur = walked[-1]
        opts = self.succ(cur, walked)
        fut = self.reach(opts, walked)
        st = {}
        for i in self.NODES:
            if i == cur:
                st[i] = "current"
            elif i in walked:
                st[i] = "walked"
            elif i in opts:
                st[i] = "option"
            elif self.KIND[i] == "target":
                st[i] = "target"
            elif i in fut:
                st[i] = "reach"
            else:
                st[i] = "grey"
        return st, opts

    def edge_states(self, walked, st):
        out = {}
        for a, b in self.edges(walked):
            if a in walked and b in walked and walked.index(b) == walked.index(a) + 1:
                out[(a, b)] = "walked"
            elif st[a] == "current" and st[b] == "option":
                out[(a, b)] = "option"
            elif st[a] in ("option", "reach") and st[b] in ("reach", "target"):
                out[(a, b)] = "future"
            else:
                out[(a, b)] = "grey"
        return out

    def branch(self, o, walked):
        ns = self.reach([o], walked)
        return ns, {(a, b) for a, b in self.edges(walked) if a in ns and b in ns}

    # ---------------------------------------------------------------- links
    def edge_type(self, a, b):
        if a == "start":
            return "ramp"
        if (a, b) in self.SHORTCUTS:
            return "climb"
        if b == "srv":
            return "core_lift"
        if self.ROW[a] == self.ROW[b]:
            return "gallery"
        return "corner_stair" if self.FACE[a] != self.FACE[b] else "stair"

    def door(self, i, side):
        """side -1 = the jamb at the room's low-u end, +1 = the high-u end; just in front of the facade."""
        f = self.FACE[i]
        hs = self.half_size(self.tier_of(i))
        z0, _ = self.room_z(i)
        return self.fp(f, hs + YF, self.U[i] + side * self.RW / 2, z0 + DOOR_Z)

    def edge_path(self, a, b):
        t = self.edge_type(a, b)
        fp, hsz = self.fp, self.half_size
        if t == "ramp":
            sx, sy, _ = self.start_pos()
            d1 = self.door(b, -1)
            py0 = -self.cfg["podium_x"]
            return [(sx + 4.0, sy, 1.2), (sx + 10.0, sy, 1.2), (sx + 10.0, py0 - 5.0, 1.2),
                    (sx + 22.0, py0 - 2.0, self.PODIUM + 0.4), (d1[0] - 5.0, d1[1], d1[2]), d1]
        if t == "gallery":
            s = 1 if self.U[b] > self.U[a] else -1
            return [self.door(a, s), self.door(b, -s)]
        if t == "corner_stair":
            fa, fb = self.FACE[a], self.FACE[b]
            hs = hsz(self.tier_of(a))
            za, zb = self.door(a, 1)[2], self.door(b, -1)[2]
            run = self.cfg["stair_run"]
            return [self.door(a, 1), fp(fa, hs + YF, hs + YF, za), fp(fb, hs + YF, -hs + YF + run, zb),
                    fp(fb, hsz(self.tier_of(b)) + YF, -hs + YF + run, zb), self.door(b, -1)]
        if t == "stair":
            s = 1 if self.U[a] > 0 else -1
            da, db = self.door(a, s), self.door(b, s)
            f = self.FACE[a]
            return [da, fp(f, hsz(self.tier_of(a)) + YF, self.U[a] + s * (self.RW / 2 + 2.2), da[2]),
                    fp(f, hsz(self.tier_of(b)) + YF, self.U[b] + s * (self.RW / 2 + 2.2), db[2]), db]
        if t == "climb":
            f = self.FACE[a]
            u = self.U[a] + self.RW * 0.5 + 1.2
            za = self.room_z(a)[0] + DOOR_Z
            pts = [self.door(a, 1), fp(f, hsz(self.tier_of(a)) + YF, u, za)]
            for r in range(self.tier_of(a), self.tier_of(b)):
                z1 = self.tier_floor(r) + self.TH + 0.6
                pts.append(fp(f, hsz(r) + YF, u, z1))
                pts.append(fp(f, hsz(r + 1) + YF, u, z1))
            pts.append(fp(f, hsz(self.tier_of(b)) + YF, u, self.room_z(b)[0] + DOOR_Z))
            pts.append(self.door(b, 1))
            return pts
        zb = self.room_z(b)[0] + DOOR_Z
        za = self.room_z(a)[0] + DOOR_Z
        fa = self.FACE[a]
        ha = hsz(self.tier_of(a))
        return [fp(fa, ha + YF * 0.3, self.U[a], za), fp(fa, ha - self.RD + 0.5, self.U[a], za),
                fp(fa, ha - self.RD + 0.5, self.U[a], zb), fp(fa, hsz(self.R), 0.0, zb)]

    # ---------------------------------------------------------------- the scan rule
    def watch_az(self, step):
        w = self.watch
        if w["type"] == "lighthouse":
            return (w.get("step", 45.0) * (w.get("phase", 0) + step)) % 360.0
        if w["type"] == "face":
            f = (w.get("phase", 0) - step) % 4
            return math.degrees(math.atan2(N[f][0], N[f][1])) % 360.0
        return None

    def room_az(self, i):
        c = self.room_center(i)
        return math.degrees(math.atan2(c[0], c[1])) % 360.0

    def in_watch(self, i, step):
        az = self.watch_az(step)
        if az is None:
            return False
        half = self.watch.get("sector", 90.0) / 2.0
        d = (self.room_az(i) - az + 180.0) % 360.0 - 180.0
        return -half <= d < half

    def scanned(self, walked):
        """Rooms in the eye this step: options and rooms ahead inside the watched sector (not walked, not past)."""
        step = len(walked) - 1
        st, _ = self.states(walked)
        return sorted((n for n in self.NODES if n not in ("start", "srv") and st[n] in ("option", "reach")
                       and self.in_watch(n, step)), key=lambda n: self.ORDER[n]), self.watch_az(step)

    # ---------------------------------------------------------------- dump
    def dump(self, path, walked, extra=None):
        st, opts = self.states(walked)
        sc, az = self.scanned(walked)
        d = dict(nodes={i: dict(kind=self.KIND[i], row=self.ROW[i], k=self.K[i], u=self.U[i], face=self.FACE[i],
                                tier=self.tier_of(i) if i != "start" else -1,
                                z=(self.room_z(i) if i != "start" else None)) for i in self.NODES},
                 all_edges=[dict(a=a, b=b, type=self.edge_type(a, b), path=self.edge_path(a, b)) for a, b in sorted(
                     set(self.PATH) | set(self.SHORTCUTS), key=lambda e: (self.ORDER[e[0]], self.ORDER[e[1]]))],
                 tiers=self.tiers(), eye=self.eye_pos(), start=self.start_pos(), crown_top=self.crown_top(),
                 seg_face=self.SEG_FACE, seg_tier=self.SEG_TIER,
                 state=st, opts=opts, scanned=sc, eye_az=az, walked=walked, N=N, T=T,
                 const=dict(RW=self.RW, RH=self.RH, RD=self.RD, PITCH=self.PITCH, TH=self.TH, PODIUM=self.PODIUM,
                            SLAB=SLAB, DOOR_Z=DOOR_Z, YF=YF))
        if extra:
            d.update(extra)
        with open(path, "w") as fh:
            json.dump(d, fh, indent=1)
        return d
