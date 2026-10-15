"""Round 40: map the locked raid-UI interaction set (rounds 20-23, written for the round 19 6-node district) onto the
ONE CITY at real scope (the shipped Meridian campaign network, net_scope.json).

The raid UI scripts read a round-19-style `layout` module (NODES relay/firewall/vault/proxy/safe/core, ENTRIES
e_east/e_west/e_south, ROUTES r1-r3, LINKS, CAM). This builds that data from the real network:
  * roles: CORE + the 5 owned nodes whose screen arrangement best matches the round 19 one (exhaustive permutation
    search, similarity fit), so the locked gifs' framing still lands on the same nodes;
  * entries: 3 available Sites, fitted the same way; routes = street BFS through the round 19 waypoints;
  * links: the network's own street polylines;
  * the camera = the similarity fit (same yaw / pitch as the city);
  * compat world = real world x K (K = 2), so the round 19 decal sizes (PAD_S 10.4) land at ~0.9 lot.
python build40.py -> ../scratch/layout/layout40.json
"""
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

K = 2.0
# round 19 reference (layout.py of round 19: metres, its own camera)
R19_NODES = {"core": (10, -50), "relay": (-60, -50), "firewall": (10, 20), "vault": (80, -50), "proxy": (-60, 20), "safe": (10, -120)}
R19_ENTRIES = {"e_east": (150, -50), "e_west": (-130, 20), "e_south": (80, -190)}
R19_CAM = dict(yaw=48.0, pitch=50.0, target=(20.01, -38.88, 0.0), ortho=440.0, dist=900.0)
R19_LINKS = [("core", "relay"), ("core", "firewall"), ("core", "vault"), ("core", "safe"), ("relay", "proxy"), ("proxy", "firewall")]
ROLE_KIND = {"core": "home", "relay": "relay", "firewall": "firewall", "vault": "vault", "proxy": "proxy", "safe": "safehouse"}
ROLE_LABEL = {"core": "CORE", "relay": "RELAY", "firewall": "FIREWALL RELAY", "vault": "VAULT TERMINAL", "proxy": "PROXY RELAY", "safe": "SAFEHOUSE"}
ROLE_STATUS = {"core": "home", "relay": "holds", "firewall": "holds", "vault": "disabled", "proxy": "seized", "safe": "holds"}
ROLE_INT = {"core": (50, 50), "relay": (15, 15), "firewall": (30, 30), "vault": (20, 20), "proxy": (15, 15), "safe": (20, 20)}


def proj(cam, x, y):
    return L.project(cam, x, y, 0.0)


def fit_sim(q, p):
    """p ~ s * q + t (least squares, scale + translation)."""
    n = len(q)
    qm = (sum(a[0] for a in q) / n, sum(a[1] for a in q) / n)
    pm = (sum(a[0] for a in p) / n, sum(a[1] for a in p) / n)
    num = sum((a[0] - qm[0]) * (b[0] - pm[0]) + (a[1] - qm[1]) * (b[1] - pm[1]) for a, b in zip(q, p))
    den = sum((a[0] - qm[0]) ** 2 + (a[1] - qm[1]) ** 2 for a in q) or 1
    s = num / den
    t = (pm[0] - s * qm[0], pm[1] - s * qm[1])
    err = sum((s * a[0] + t[0] - b[0]) ** 2 + (s * a[1] + t[1] - b[1]) ** 2 for a, b in zip(q, p))
    return s, t, err


def main():
    import citydata as CD
    import grid27
    d = CD.load()
    grid27.patch(d)
    cells = L.street_graph(d)
    net = L.load_net()
    nb = {n["id"]: n for n in net["nodes"]}
    # reference camera for the real world (same yaw / pitch as the city), ortho 1000 around the origin
    ref = L.cam((0, 0), 1000.0)
    target19 = {k: proj(R19_CAM, *v) for k, v in R19_NODES.items()}
    target19.update({k: proj(R19_CAM, *v) for k, v in R19_ENTRIES.items()})
    cl = nb["core"]["lot"]
    owned = sorted((n["id"] for n in net["nodes"] if n["state"] == "owned"),
                   key=lambda i: (math.hypot(nb[i]["lot"][0] - cl[0], nb[i]["lot"][1] - cl[1]), i))[:6]   # a compact district
    qc = proj(ref, *L.W(nb["core"]["lot"]))
    roles = ["relay", "firewall", "vault", "proxy", "safe"]
    best = None
    for perm in itertools.permutations(owned, 5):
        q = [qc] + [proj(ref, *L.W(nb[o]["lot"])) for o in perm]
        p = [target19["core"]] + [target19[r] for r in roles]
        s, t, err = fit_sim(q, p)
        if s <= 0:
            continue
        if best is None or err < best[0]:
            best = (err, perm, s, t)
    err, perm, s, t = best
    role_of = dict(zip(roles, perm))
    role_of["core"] = "core"
    # entries: 3 available Sites, best fit with the same transform
    av = sorted(n["id"] for n in net["nodes"] if n["state"] == "available")
    eb = None
    for perm_e in itertools.permutations(av, 3):
        e = 0.0
        for ek, sid in zip(("e_east", "e_west", "e_south"), perm_e):
            q = proj(ref, *L.W(nb[sid]["lot"]))
            pp = target19[ek]
            e += (s * q[0] + t[0] - pp[0]) ** 2 + (s * q[1] + t[1] - pp[1]) ** 2
        if eb is None or e < eb[0]:
            eb = (e, perm_e)
    ent_of = dict(zip(("e_east", "e_west", "e_south"), eb[1]))
    # v2: each route enters at the available Site nearest its first target node (round 19: entries one block out)
    used_e = set()
    for ek, tgt in (("e_east", "vault"), ("e_west", "proxy"), ("e_south", "safe")):
        tl = nb[role_of[tgt]]["lot"]
        cand = sorted((a for a in av if a not in used_e), key=lambda a: (math.hypot(nb[a]["lot"][0] - tl[0], nb[a]["lot"][1] - tl[1]), a))
        ent_of[ek] = cand[0]
        used_e.add(cand[0])
    # camera (round 40 v2): FRAME the six nodes + three entries (the round 19 similarity fit is only used to assign roles)
    import scope39
    pts = [L.W(nb[role_of[r]]["lot"]) for r in role_of] + [L.W(nb[sid]["lot"]) for sid in ent_of.values()]
    fc = scope39.fit(pts, margin=1.45, lo=200.0, hi=700.0)
    tw = L.W(fc["t"])
    cam_fit = L.cam(fc["t"], fc["ortho"])
    r_, u_, f_ = L.basis(cam_fit)
    lift = 70.0 / 1080 * fc["ortho"] * 1080 / 1920          # the panels / tray: bbox centre sits 70 px above the frame centre
    cam_real = dict(yaw=L.YAW, pitch=L.PITCH, target=(tw[0] - u_[0] * lift * 0 - (u_[0] * lift), tw[1] - (u_[1] * lift), 0.0),
                    ortho=fc["ortho"], dist=2600.0)
    if False:
        pass
    # (unused) old similarity camera: scale s means ortho / s; the frame centre in ref screen coords -> world on the ground
    r, u, f = L.basis(ref)
    cam_real = cam_real if 'cam_real' in dir() else None
    cxs = ((960 - t[0]) / s, (540 - t[1]) / s)                 # ref-screen point that must land in the frame centre
    xc = (cxs[0] / 1920 - 0.5) * 1000.0
    yc = (0.5 - cxs[1] / 1080) * (1000.0 * 1080 / 1920)
    det = r[0] * u[1] - r[1] * u[0]
    wx = (xc * u[1] - r[1] * yc) / det
    wy = (r[0] * yc - u[0] * xc) / det
    if cam_real is None:
        cam_real = dict(yaw=L.YAW, pitch=L.PITCH, target=(wx, wy, 0.0), ortho=1000.0 / s, dist=2600.0)

    def KW(p):
        x, y = L.W(p)
        return (x * K, y * K)
    nodes = {}
    for role, sid in role_of.items():
        x, y = KW(nb[sid]["lot"])
        nodes[role] = [x, y, ROLE_KIND[role], ROLE_LABEL[role], ROLE_STATUS[role], list(ROLE_INT[role]), sid]
    extra = [n for n in net["nodes"] if n["state"] == "owned" and n["id"] not in role_of.values()]
    for n in extra:
        x, y = KW(n["lot"])
        nodes[n["id"]] = [x, y, n["kind"] if n["kind"] != "safehouse" else "safehouse", n["kind"].upper(), "holds", [15, 15], n["id"]]
    sid2role = {v: k for k, v in role_of.items()}
    for n in extra:
        sid2role[n["id"]] = n["id"]
    entries = {ek: list(KW(nb[sid]["lot"])) for ek, sid in ent_of.items()}

    def street(a_cell, b_cell):
        p = L.bfs(tuple(a_cell), tuple(b_cell), cells)
        return [list(KW(q)) for q in L.simplify(p)]
    # links: the round 19 role pairs + the network's other owned links, along the real streets
    links, link_pts = [], {}
    pairs = list(R19_LINKS)
    for l in net["links"]:
        if l["state"] == "owned":
            a, b = sid2role.get(l["a"]), sid2role.get(l["b"])
            if a and b and (a, b) not in pairs and (b, a) not in pairs:
                pairs.append((a, b))
    for a, b in pairs:
        sa, sb = nodes[a][6], nodes[b][6]
        own = next((l for l in net["links"] if {l["a"], l["b"]} == {sa, sb}), None)
        if own:
            pts = [list(KW(q)) for q in own["pts"]]
            if own["a"] != sa:
                pts = pts[::-1]
        else:
            pts = street(nb[sa]["cell"], nb[sb]["cell"])
        links.append([a, b])
        link_pts["%s|%s" % (a, b)] = pts
    # routes (the round 19 waypoints, along the streets)
    ways = {"r1": ["e_east", "vault", "core"], "r2": ["e_west", "proxy", "firewall", "core"], "r3": ["e_south", "safe", "core"]}
    routes = {}
    for rid, keys in ways.items():
        cells_ = [nb[ent_of[k]]["cell"] if k in ent_of else nb[nodes[k][6]]["cell"] for k in keys]
        pts = []
        for a, b in zip(cells_, cells_[1:]):
            seg = street(a, b)
            pts += seg if not pts else seg[1:]
        routes[rid] = dict(keys=keys, pts=pts)
    cam = dict(yaw=L.YAW, pitch=L.PITCH, target=[cam_real["target"][0] * K, cam_real["target"][1] * K, 0.0], ortho=cam_real["ortho"] * K,
               dist=2600.0 * K)
    out = dict(K=K, nodes=nodes, links=links, link_pts=link_pts, entries=entries, routes=routes, cam=cam, cam_real=cam_real,
               roles=role_of, entry_sites=ent_of, fit_err=err)
    json.dump(out, open(os.path.join(L.DST, "layout40.json"), "w"), indent=1)
    print("roles", role_of, "entries", ent_of, "cam_real", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in cam_real.items()},
          "err/node px", round(math.sqrt(err / 6), 1))


if __name__ == "__main__":
    main()
