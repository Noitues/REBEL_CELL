"""HQ kit (shared by Meridian, Solace, Orbital, Rebel Cell): the generic run-graph machinery, generalised from
hq_halcyon/scripts/hq_graph.py (pure python: no Blender, no PIL).

A corp's hq_graph.py defines its data and calls hqk_graph.bind(globals()). Data a corp module must define:
  NODES  path order (ties are broken by this order, never by dict order); "start" first, "srv" last
  KIND, LAYER, WORD, FILE, HP_ARRIVE, CP (with max_shortcuts), MECH (the mechanic's preset section)
  ROOM   {id: dict(o=(x, y, z0), n=(nx, ny), w, h, d)}: o = the centre of the opening's sill on the facade plane,
         n = the outward normal (unit, ground plane), the room goes d deep behind the opening; n None = seen from
         every side (a vault open all round)
  base_edges(walked, mt)  -> the links on offer at mechanic time mt (a corp's mechanic may add / cut links per step)
  edge_path(a, b, mt)     -> world polyline;   edge_type(a, b) -> str
  seg_normal(p)           -> the outward normal used to hide a link segment at p when its side faces away (or None)
  mech(walked, mt)        -> dict(affected=[ids], ...): the mechanic's state at this step (corp-defined)
Optional: room_rec(i, mt) for rooms that move (movers); RUNNERS (several tokens at once, Rebel Cell).
Bound functions: room_front, room_corners, room_center, room_normal, succ, reach, states, edge_states, branch,
shortcuts_used, edges, dump, step_of.
"""
import json
import math


def bind(M):
    g = M

    def step_of(walked):
        return len(walked) - 1

    def room_rec(i, mt=None):
        if "room_rec_corp" in g:
            r = g["room_rec_corp"](i, mt)
            if r is not None:
                return r
        return g["ROOM"][i]

    def _t(n):
        return (-n[1], n[0]) if n else (1.0, 0.0)

    def room_front(i, mt=None):
        """The opening's 4 world corners: bottom-left, bottom-right, top-right, top-left (seen from outside)."""
        r = room_rec(i, mt)
        ox, oy, z0 = r["o"]
        n = r["n"] or (0.0, -1.0)
        t = (n[1], -n[0])                     # screen-LEFT when looking at the opening from outside
        hw = r["w"] / 2.0
        z1 = z0 + r["h"]
        return [(ox - t[0] * hw, oy - t[1] * hw, z0), (ox + t[0] * hw, oy + t[1] * hw, z0),
                (ox + t[0] * hw, oy + t[1] * hw, z1), (ox - t[0] * hw, oy - t[1] * hw, z1)]

    def room_corners(i, mt=None):
        r = room_rec(i, mt)
        n = r["n"] or (0.0, -1.0)
        f = room_front(i, mt)
        back = [(p[0] - n[0] * r["d"], p[1] - n[1] * r["d"], p[2]) for p in f]
        return f + back

    def room_center(i, mt=None):
        c = room_corners(i, mt)
        return tuple(sum(p[k] for p in c) / len(c) for k in range(3))

    def room_normal(i, mt=None):
        return room_rec(i, mt)["n"]

    def edges(walked, mt=None):
        mt = step_of(walked) if mt is None else mt
        out = set(g["base_edges"](walked, mt))
        out |= set(e for e in zip(walked[:-1], walked[1:]) if e in g.get("ALL_EDGES", set()) or True)
        return sorted(out, key=lambda e: (g["ORDER"][e[0]], g["ORDER"][e[1]]))

    def succ(n, walked, mt=None):
        mt = step_of(walked) if mt is None else mt
        return sorted((b for a, b in g["base_edges"](walked, mt) if a == n and b not in walked),
                      key=lambda b: g["ORDER"][b])

    def reach(froms, walked, mt=None):
        """Everything reachable later. Ahead of the current step the mechanic's timing is unknown to the planner, so
        reach uses the union of the links on offer over one full mechanic cycle (a corp sets CYCLE)."""
        mt = step_of(walked) if mt is None else mt
        cyc = g.get("CYCLE", 1)
        alle = set()
        for k in range(cyc):
            alle |= set(g["base_edges"](walked, mt + 1 + k))
        seen, stack = set(), list(froms)
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(b for a, b in alle if a == n and b not in walked)
        return seen

    def states(walked, mt=None):
        cur = walked[-1]
        opts = succ(cur, walked, mt)
        fut = reach(opts, walked, mt)
        st = {}
        for i in g["NODES"]:
            if i == cur:
                st[i] = "current"
            elif i in walked:
                st[i] = "walked"
            elif i in opts:
                st[i] = "option"
            elif g["KIND"][i] == "target":
                st[i] = "target"
            elif i in fut:
                st[i] = "reach"
            else:
                st[i] = "grey"
        return st, opts

    def edge_states(walked, st, mt=None):
        out = {}
        mt = step_of(walked) if mt is None else mt
        cyc = g.get("CYCLE", 1)
        shown = set(g["base_edges"](walked, mt))
        for k in range(cyc):
            shown |= set(g["base_edges"](walked, mt + 1 + k))
        shown |= set(zip(walked[:-1], walked[1:]))
        now = set(g["base_edges"](walked, mt))
        for a, b in shown:
            if a in walked and b in walked and walked.index(b) == walked.index(a) + 1:
                out[(a, b)] = "walked"
            elif st[a] == "current" and st[b] == "option" and (a, b) in now:
                out[(a, b)] = "option"
            elif st[a] in ("option", "reach") and st[b] in ("reach", "target", "option"):
                out[(a, b)] = "future"
            else:
                out[(a, b)] = "grey"
        return out

    def shown_edges(walked, mt=None):
        st, _ = states(walked, mt)
        return sorted(edge_states(walked, st, mt), key=lambda e: (g["ORDER"][e[0]], g["ORDER"][e[1]]))

    def branch(o, walked=None, mt=None):
        walked = walked if walked is not None else g["WALK_MID"]
        ns = reach([o], walked, mt)
        es = set(edge_states(walked, states(walked, mt)[0], mt))
        return ns, {(a, b) for a, b in es if a in ns and b in ns}

    def shortcuts_used(walked):
        return sum(1 for e in zip(walked[:-1], walked[1:]) if g["edge_type"](*e) in g.get("SHORTCUT_TYPES", ()))

    def dump(path, walked, mt=None, extra=None):
        st, opts = states(walked, mt)
        mech = g["mech"](walked, mt)
        d = dict(nodes={i: dict(kind=g["KIND"][i], rec=room_rec(i, mt), order=g["ORDER"][i]) for i in g["NODES"]},
                 state=st, opts=opts, mech=mech, walked=walked)
        if extra:
            d.update(extra)
        with open(path, "w") as fh:
            json.dump(d, fh, indent=1)
        return d

    for k, v in dict(step_of=step_of, room_rec=room_rec, room_front=room_front, room_corners=room_corners,
                     room_center=room_center, room_normal=room_normal, edges=shown_edges, succ=succ, reach=reach,
                     states=states, edge_states=edge_states, branch=branch, shortcuts_used=shortcuts_used,
                     dump=dump).items():
        g.setdefault(k, v)
    g["ORDER"] = {n: i for i, n in enumerate(g["NODES"])}


def ring_pts(cx, cy, r, z, a0, a1, n):
    """Arc points (deg, 0 = north, clockwise) for link paths."""
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        out.append((cx + r * math.sin(a), cy + r * math.cos(a), z))
    return out
