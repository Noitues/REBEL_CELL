"""Round 38 SCOPE TEST: the real campaign graph on the one city model.

Source: content/corporations/meridian.tres (read-only) - the shipped Meridian campaign: 32 Sites (13 T1, 9 T2, 9 T3,
1 T4 boss = Manifest Control) + the home server, its links and locked links, and each Site's map_position (x = tier
column, y = spread). GDD 4.1: one corporation per campaign, 30-40 Sites.

Placement: the graph is laid between the Cell's base (home) and Meridian HQ (the T4 boss): map_position x runs along
the Cell -> HQ axis, y spreads across it; every Site snaps to the nearest unused street junction (>= 5 lots apart).
Links are the Site graph's links, routed on the real streets.

Mid-campaign state (a realistic player network): 11 runs done. Owned (claimed, nodes installed): 7 T1 + 2 T2 + home =
10 nodes, with node types; grey (run, not claimed) 2; available = every unowned Site linked from an owned one;
the rest white. The raid comes from the Meridian side through the available Sites.

python scope38.py  -> ../scratch/layout/net_scope.json (same schema as layout36's net36.json)
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout36 as L  # noqa: E402

ROOT = os.path.dirname(HERE)
TRES = os.path.abspath(os.path.join(ROOT, "..", "..", "..", "content", "corporations", "meridian.tres"))


def parse(path):
    sites = []
    cur = None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("[sub_resource"):
            cur = {}
            sites.append(cur)
        elif cur is not None and "=" in line:
            k, v = [x.strip() for x in line.split("=", 1)]
            if k == "id":
                cur["id"] = v.strip('&"')
            elif k == "tier":
                cur["tier"] = int(v)
            elif k in ("links", "locked_links"):
                cur[k] = re.findall(r'&"([^"]+)"', v)
            elif k == "map_position":
                cur["pos"] = [float(a) for a in re.findall(r"[-\d.]+", v.split("(", 1)[1])]
            elif k == "claimable":
                cur["claimable"] = v == "true"
            elif k == "display_name":
                cur["name"] = v.strip('"')
    return [s for s in sites if "id" in s and "pos" in s]


OWNED = ["m1_c", "m1_d", "m1_e", "m1_f", "m1_g", "m1_h", "m1_b", "m2_virus", "m2_e"]
GREY = ["m1_a", "m2_f"]
KINDS = ["relay", "firewall", "vault", "safehouse", "proxy", "relay", "firewall", "vault", "relay"]


def build():
    import citydata as CD
    import grid27
    d = CD.load()
    Ls = CD.Lots(d)
    hq = CD.hq_centres(d)
    cb = CD.rc_base_centre(d, Ls)
    grid27.patch(d)
    cells = L.street_graph(d)
    J = [c for c in cells if L.junction(c, cells)]
    sites = parse(TRES)
    byid = {s["id"]: s for s in sites}
    xs = [s["pos"][0] for s in sites]
    ys = [s["pos"][1] for s in sites]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    home = (cb[0] - 3.5, cb[1] - 3.5)
    tgt = hq["meridian"]
    ax, ay = tgt[0] - home[0], tgt[1] - home[1]
    Lax = math.hypot(ax, ay)
    ux, uy = ax / Lax, ay / Lax
    px, py = -uy, ux
    used = []
    nodes = []
    order = sorted(sites, key=lambda s: (s.get("tier", 1), s["pos"][1], s["id"]))
    home_s = byid["m_home"]
    order.remove(home_s)
    order = [home_s] + order
    for s in order:
        if s["id"] == "m_home":
            p = home
        else:
            fx = (s["pos"][0] - x0) / (x1 - x0)            # 0 home .. 1 boss
            fy = (s["pos"][1] - (y0 + y1) / 2) / (y1 - y0)  # -0.5 .. 0.5
            along = 4 + fx * (Lax - 4)
            across = fy * 46.0 * (1 - 0.55 * fx)          # fan out near home, converge on the HQ
            p = (home[0] + ux * along + px * across, home[1] + uy * along + py * across)
        best = None
        for c in J:
            if any(math.hypot(c[0] - u[0], c[1] - u[1]) < 4.5 for u in used):
                continue
            if math.hypot(c[0] + 0.5 - tgt[0], c[1] + 0.5 - tgt[1]) < 6.5 and s.get("tier") != 4:
                continue
            dd = math.hypot(c[0] + 0.5 - p[0], c[1] + 0.5 - p[1])
            if best is None or dd < best[0]:
                best = (dd, c)
        c = best[1]
        used.append(c)
        sid = s["id"]
        if sid == "m_home":
            st, kind = "core", "core"
        elif sid in OWNED:
            st, kind = "owned", KINDS[OWNED.index(sid)]
        elif sid in GREY:
            st, kind = "grey", "site"
        else:
            st, kind = "white", "key" if s.get("tier") == 3 and sid.startswith("m3") and sid.endswith(("_a", "_core")) else "site"
        nodes.append(dict(id=sid, cell=list(c), lot=[c[0] + 0.5, c[1] + 0.5], state=st, kind=kind, tier=s.get("tier", 1),
                          corp="meridian", name=s.get("name", sid)))
    for n in nodes:                                       # the home server is the Cell's CORE in every view
        if n["id"] == "m_home":
            n["id"] = "core"
    for s_ in sites:
        if s_["id"] == "m_home":
            s_["id"] = "core"
        for k_ in ("links", "locked_links"):
            s_[k_] = ["core" if v == "m_home" else v for v in s_.get(k_, [])]
    byid = {s_["id"]: s_ for s_ in sites}
    nb = {n["id"]: n for n in nodes}
    owned = {n["id"] for n in nodes if n["state"] in ("owned", "core")}
    for n in nodes:                                       # available = linked from an owned node
        if n["state"] == "white":
            if any(n["id"] in byid[o].get("links", []) or o in byid[n["id"]].get("links", []) for o in owned):
                n["state"] = "available"
    links = []
    seen = set()
    for s in sites:
        for kind_, lst in (("open", s.get("links", [])), ("locked", s.get("locked_links", []))):
            for t in lst:
                if t not in nb or s["id"] not in nb:
                    continue
                key = tuple(sorted((s["id"], t)))
                if key in seen:
                    continue
                seen.add(key)
                a, b = nb[s["id"]], nb[t]
                p = L.bfs(tuple(a["cell"]), tuple(b["cell"]), cells)
                if not p:
                    continue
                sa, sb = a["state"], b["state"]
                if kind_ == "locked":
                    st = "white"
                elif sa in ("owned", "core") and sb in ("owned", "core"):
                    st = "owned"
                elif "grey" in (sa, sb) and ({sa, sb} & {"owned", "core"}):
                    st = "grey"
                elif {sa, sb} & {"owned", "core"}:
                    st = "border"
                else:
                    st = "white"
                links.append(dict(a=a["id"], b=b["id"], state=st, pts=L.simplify(p), locked=kind_ == "locked"))
    # the transit view: the longest border link
    bl = [l for l in links if l["state"] == "border"]
    lk = max(bl, key=lambda l: sum(math.hypot(q[0] - p_[0], q[1] - p_[1]) for p_, q in zip(l["pts"], l["pts"][1:])))
    if lk["a"] not in owned:
        lk["a"], lk["b"] = lk["b"], lk["a"]
        lk["pts"] = lk["pts"][::-1]
    lp = [L.W(p) for p in lk["pts"]]
    tfit = fit(lp, margin=1.25, lo=88.0, hi=190.0)
    mid = tfit["t"]
    # the raid camera fitted to the player network (owned nodes + the available Sites the raid enters through)
    pts = [L.W(n["lot"]) for n in nodes if n["state"] in ("owned", "core")]
    raid = fit(pts)
    net = dict(nodes=nodes, links=links, hq={k: list(v) for k, v in hq.items()}, cell_base=list(cb),
               transit=dict(link=[lk["a"], lk["b"]], t=list(mid), ortho=tfit["ortho"]), raid=raid, fist=[], corp="meridian")
    os.makedirs(L.DST, exist_ok=True)
    json.dump(net, open(os.path.join(L.DST, "net_scope.json"), "w"), indent=1)
    from collections import Counter
    print("sites", len(nodes), Counter(n["state"] for n in nodes), "links", Counter(l["state"] for l in links), "raid", raid)
    return net


def fit(world_pts, margin=1.18, lo=150.0, hi=420.0):
    """Ortho camera fit: project the network's world points with the iso camera, size the view to their bounds
    (16:9, margin for the panels), clamp. The raid zoom therefore depends on the network size (GDD-driven)."""
    cam = L.cam((0, 0), 1000.0)
    r, u, f = L.basis(cam)
    sx = [p[0] * r[0] + p[1] * r[1] for p in world_pts]
    sy = [p[0] * u[0] + p[1] * u[1] for p in world_pts]
    w = (max(sx) - min(sx)) * margin + 40
    h = (max(sy) - min(sy)) * margin + 40
    ortho = max(lo, min(hi, max(w, h * 16 / 9)))
    cx, cy = (max(sx) + min(sx)) / 2, (max(sy) + min(sy)) / 2
    # back to world (on the ground plane z = 0): solve x*r + y*r = cx, x*u + y*u = cy
    a, b, c_, d_ = r[0], r[1], u[0], u[1]
    det = a * d_ - b * c_
    wx = (cx * d_ - b * cy) / det
    wy = (a * cy - c_ * cx) / det
    t = L.lots(wx, wy)
    return dict(t=[t[0], t[1]], ortho=ortho)


if __name__ == "__main__":
    build()
