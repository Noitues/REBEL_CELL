"""Round 39: the netrun's own map ON the city streets (GDD 4.2: 7 layers, 2-4 nodes each, Server Racks at layer 4 and 7).

The run starts at the Cell's node on the chosen border link and ends at the Site (TARGET). Its paths follow the street
grid with many turns (side streets): the main line walks through waypoints pushed 2-4 lots off the straight line, the
alternatives sit 2-3 lots aside, and every edge is a street BFS path. Mid-run state: layers 0-1 walked, the operative on
layer 2, its next options on layer 3; everything else exists but is hidden (round 37 netrun rule).

python runmap39.py  -> ../scratch/layout/run39.json  (+ the fitted transit camera in net_scope.json["transit"])
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

LAYERS = [1, 3, 3, 4, 3, 3, 1]          # layer 0 = the start node's own street (one), 6 = the Site's Server Rack (target)
KINDS = ["router", "router", "elite", "terminal", "modem", "router", "elite", "router"]


def build():
    import citydata as CD
    import grid27
    import scope39
    d = CD.load()
    grid27.patch(d)
    cells = L.street_graph(d)
    J = [c for c in cells if L.junction(c, cells)]
    net = L.load_net()
    nb = {n["id"]: n for n in net["nodes"]}
    lk = net["transit"]["link"]
    a, b = nb[lk[0]], nb[lk[1]]
    ax, ay = a["cell"]
    bx, by = b["cell"]
    Ld = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / Ld, (by - ay) / Ld
    px, py = -uy, ux
    r = random.Random(3939)
    used = [tuple(a["cell"]), tuple(b["cell"])]
    nodes = []
    for li, n in enumerate(LAYERS):
        if li == 0:
            nodes.append(dict(id="L0_0", layer=0, k=0, cell=list(a["cell"]), kind="start"))
            continue
        if li == len(LAYERS) - 1:
            nodes.append(dict(id="L6_0", layer=li, k=0, cell=list(b["cell"]), kind="rack"))
            continue
        u = li / (len(LAYERS) - 1)
        wig = r.uniform(-3.0, 3.0)
        for k in range(n):
            off = wig + (k - (n - 1) / 2) * 3.4
            tgt = (ax + (bx - ax) * u + px * off, ay + (by - ay) * u + py * off)
            c = min((c for c in J if all(math.hypot(c[0] - q[0], c[1] - q[1]) >= 2.0 for q in used)),
                    key=lambda c: (math.hypot(c[0] - tgt[0], c[1] - tgt[1]), c))
            used.append(c)
            kind = "rack" if (li == 3 and k == n - 1) else r.choice(KINDS)
            nodes.append(dict(id="L%d_%d" % (li, k), layer=li, k=k, cell=list(c), kind=kind))
    by_l = {}
    for n in nodes:
        by_l.setdefault(n["layer"], []).append(n)
    edges = []
    for li in range(len(LAYERS) - 1):
        cur, nxt = by_l[li], by_l[li + 1]
        for n in cur:
            # each node reaches the 1-2 nearest of the next layer (by lateral index)
            order = sorted(nxt, key=lambda m: (abs(m["k"] / max(1, len(nxt) - 1) - n["k"] / max(1, len(cur) - 1)), m["k"]))
            for m in order[:2 if len(nxt) > 1 else 1]:
                p = scope39.meander(tuple(n["cell"]), tuple(m["cell"]), cells, J, (n["id"], m["id"]))
                edges.append(dict(a=n["id"], b=m["id"], pts=L.simplify(p)))
        for m in nxt:                                # nobody unreachable
            if not any(e["b"] == m["id"] for e in edges):
                n = min(cur, key=lambda n: abs(n["k"] - m["k"]))
                p = scope39.meander(tuple(n["cell"]), tuple(m["cell"]), cells, J, (n["id"], m["id"]))
                edges.append(dict(a=n["id"], b=m["id"], pts=L.simplify(p)))
    # mid-run state
    walked = ["L0_0", by_l[1][1]["id"], by_l[2][1]["id"]]
    cur = walked[-1]
    opts = [e["b"] for e in edges if e["a"] == cur]
    for n in nodes:
        n["lot"] = [n["cell"][0] + 0.5, n["cell"][1] + 0.5]
        n["state"] = ("current" if n["id"] == cur else "walked" if n["id"] in walked else "option" if n["id"] in opts else
                      "target" if n["layer"] == len(LAYERS) - 1 else "hidden")
    for e in edges:
        sa = next(n["state"] for n in nodes if n["id"] == e["a"])
        sb = next(n["state"] for n in nodes if n["id"] == e["b"])
        e["state"] = "walked" if (sa in ("walked", "current") and sb in ("walked", "current") and walked.index(e["b"]) == walked.index(e["a"]) + 1
                                  if (e["a"] in walked and e["b"] in walked) else False) else \
            "option" if (e["a"] == cur and sb == "option") else "hidden"
    # transit camera: fitted to what is shown (walked, current, options, target)
    show = [L.W(n["lot"]) for n in nodes if n["state"] not in ("hidden",)]
    tc = scope39.fit(show, margin=1.12, lo=110.0, hi=190.0)
    net["transit"]["t"] = tc["t"]
    net["transit"]["ortho"] = tc["ortho"]
    json.dump(net, open(os.path.join(L.DST, "net_scope.json"), "w"), indent=1)
    out = dict(nodes=nodes, edges=edges, link=lk)
    json.dump(out, open(os.path.join(L.DST, "run39.json"), "w"), indent=1)
    from collections import Counter
    print("run nodes", len(nodes), Counter(n["state"] for n in nodes), "edges", Counter(e["state"] for e in edges), "cam", tc)
    return out


def load():
    return json.load(open(os.path.join(L.DST, "run39.json")))


if __name__ == "__main__":
    build()
