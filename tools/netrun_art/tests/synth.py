"""Synthetic seeded city, net and run graph for the NA-03 tests (the mock stays a test fixture, spec 8.4).

`make_world(seed)` -> dict(city, net, run_graph, site, corp). A 28 x 28 lot grid: streets on every 4th row and column,
one building per other lot, an HQ block (3 x 3 lots) with three tiers, a 5 x 5 street-junction network. All draws come
from `seeds.splitmix64(seeds.art_seed(...))` so a world is a pure function of its seed.
"""
from typing import Any, Dict, List

from netrun_art import seeds

N = 28
ORIGIN = [14.0, 14.0]
LOT = 6.0
HQ_BLOCK = (9, 9)          # lot (i, j) of the HQ block corner (the block of lots 9..11)
CORP = "meridian"


def _u(layout_seed, stream, *keys):
    return seeds.uniform(next(seeds.splitmix64(seeds.art_seed(layout_seed, stream, *keys))))


def plan(i: float, j: float) -> List[float]:
    """Plan BU of a lot point."""
    return [(i - ORIGIN[0]) * LOT, -(j - ORIGIN[1]) * LOT]


def _rect(i, j, w=1, h=1, inset=0.0):
    x0, y1 = plan(i, j)
    x1, y0 = plan(i + w, j + h)
    return [[x0 + inset, y0 + inset], [x1 - inset, y0 + inset], [x1 - inset, y1 - inset], [x0 + inset, y1 - inset]]


def make_city(layout_seed: str) -> Dict[str, Any]:
    """The city.json v1 dict."""
    blds, streets = [], []
    hi, hj = HQ_BLOCK
    for i in range(N):
        for j in range(N):
            if i % 4 == 0 or j % 4 == 0:
                streets.append(dict(lot=[i, j], along_i=j % 4 == 0, along_j=i % 4 == 0, traffic=round(_u(layout_seed, "t", i, j), 3)))
                continue
            if hi <= i < hi + 3 and hj <= j < hj + 3:
                continue
            h = 9.5 + _u(layout_seed, "h", i, j) * 22.0
            taper = 0.7 if _u(layout_seed, "tp", i, j) < 0.15 else 1.0
            parts = [dict(poly=_rect(i, j), z0=0.0, h=h, taper=taper)]
            if _u(layout_seed, "st", i, j) < 0.2:
                parts.append(dict(poly=_rect(i, j, inset=1.0), z0=h, h=4.0 + 6.0 * _u(layout_seed, "sh", i, j), taper=1.0))
            blds.append(dict(bid=f"{i}:{j}", cell=[i, j, 1, 1], terr="" if (i + j) % 3 else "meridian", hq=False,
                             key=int(_u(layout_seed, "k", i, j) * 1000), parts=parts))
    cx, cy = hi + 1.5, hj + 1.5
    tiers = []
    for t, (half, h) in enumerate(((8.0, 7.0), (6.0, 7.0), (4.0, 7.0))):
        c = plan(cx, cy)
        tiers.append(dict(poly=[[c[0] - half, c[1] - half], [c[0] + half, c[1] - half], [c[0] + half, c[1] + half],
                                [c[0] - half, c[1] + half]], z0=t * 7.0, h=h, taper=1.0))
    blds.append(dict(bid="hq:" + CORP, cell=[hi, hj, 3, 3], terr=CORP, hq=True, key=7919, parts=tiers))
    blds.sort(key=lambda b: b["bid"])
    streets.sort(key=lambda s: tuple(s["lot"]))
    return dict(version=1, layout_seed=layout_seed, units="BU", lot_bu=LOT, origin_lot=list(ORIGIN), buildings=blds,
                streets=streets, plazas=[], hqs={CORP: [hi, hj, 3, 3]})


def make_net(layout_seed: str) -> Dict[str, Any]:
    """The net.json v1 dict (straight links; plan BU `lot`)."""
    owned = {(12, 12), (8, 12), (12, 16), (16, 12)}
    nodes, ids = [], {}
    for a in range(1, 7):
        for b in range(1, 7):
            if a * 4 > N - 4 or b * 4 > N - 4:
                continue
            nid = f"s{a * 4}_{b * 4}"
            ids[(a * 4, b * 4)] = nid
            st = "core" if (a * 4, b * 4) == (12, 12) else "owned" if (a * 4, b * 4) in owned else "corporate"
            nodes.append(dict(id=nid, lot=plan(a * 4 + 0.5, b * 4 + 0.5), state=st))
    links = []
    for (i, j), nid in sorted(ids.items()):
        for di, dj in ((4, 0), (0, 4)):
            m = ids.get((i + di, j + dj))
            if m:
                a, b = sorted((nid, m))
                pa = next(n["lot"] for n in nodes if n["id"] == a)
                pb = next(n["lot"] for n in nodes if n["id"] == b)
                links.append(dict(a=a, b=b, state="open", pts=[pa, pb]))
    # one diagonal link (exercises the street router)
    a, b = sorted((ids[(8, 8)], ids[(12, 12)]))
    pa = next(n["lot"] for n in nodes if n["id"] == a)
    pb = next(n["lot"] for n in nodes if n["id"] == b)
    links.append(dict(a=a, b=b, state="open", pts=[pa, pb]))
    links.sort(key=lambda l: (l["a"], l["b"]))
    nodes.sort(key=lambda n: n["id"])
    return dict(version=1, layout_seed=layout_seed, nodes=nodes, links=links)


def make_graph(layout_seed: str, layers: int = 7) -> Dict[str, Any]:
    """The run_graph.json v1 dict: 7 layers of 2-4 nodes, each node linked forward."""
    types = ["router", "terminal", "mainframe", "server_rack"]
    counts = [2 + int(_u(layout_seed, "gn", l) * 3) for l in range(1, layers + 1)]
    counts[-1] = 1
    nodes, edges = [], []
    for l, n in enumerate(counts, 1):
        for k in range(n):
            nodes.append(dict(id=f"L{l}N{k}", layer=l, index=k, type=types[int(_u(layout_seed, "ty", l, k) * 4)],
                              elite=_u(layout_seed, "el", l, k) < 0.1))
    for l in range(1, layers):
        n, m = counts[l - 1], counts[l]
        for k in range(m):
            src = min(k, n - 1)
            edges.append((f"L{l}N{src}", f"L{l + 1}N{k}"))
        for k in range(n):
            if not any(e[0] == f"L{l}N{k}" for e in edges):
                edges.append((f"L{l}N{k}", f"L{l + 1}N{min(k, m - 1)}"))
    edges = sorted(set(edges))
    return dict(version=1, run="run1", layers=layers, nodes=nodes, edges=[dict(a=a, b=b) for a, b in edges])


def make_world(seed: int) -> Dict[str, Any]:
    """A whole fixture world for layout seed `seed`."""
    from netrun_art import layout
    ls = str(seed)
    net = make_net(ls)
    own = {n["id"] for n in net["nodes"] if n["state"] in layout.OWN_STATES}
    sites = sorted({l["b"] if l["a"] in own else l["a"] for l in layout.border_links(net)})
    return dict(city=make_city(ls), net=net, run_graph=make_graph(ls), site=sites[seed % len(sites)], corp=CORP, seed=ls)
