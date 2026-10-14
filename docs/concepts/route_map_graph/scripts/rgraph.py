"""Route map graph: the run graph used by every direction (GDD 4.2: 7 layers, 2-4 nodes, Racks at L4 and L7).

L0 = the start (the Cell's owned node), L1 all Routers, a Modem in L3-5, about one Elite per layer in L3-6,
the optional Rack in L4 and the TARGET Rack in L7. 19 nodes, 23 edges, no crossing pairs inside a layer gap.
Pure data + reachability. Ties broken by (layer, k), never by dict order.
"""

KIND = {
    "L0_0": "start",
    "L1_0": "router", "L1_1": "router", "L1_2": "router",
    "L2_0": "terminal", "L2_1": "router", "L2_2": "router",
    "L3_0": "modem", "L3_1": "elite", "L3_2": "terminal",
    "L4_0": "router", "L4_1": "rack", "L4_2": "router",
    "L5_0": "elite", "L5_1": "router", "L5_2": "modem",
    "L6_0": "router", "L6_1": "elite",
    "L7_0": "target",
}
_E = {
    0: [(0, 0), (0, 1), (0, 2)],
    1: [(0, 0), (1, 0), (1, 1), (2, 2)],
    2: [(0, 0), (1, 1), (2, 1), (2, 2)],
    3: [(0, 0), (0, 1), (1, 1), (2, 2)],
    4: [(0, 0), (1, 0), (1, 1), (2, 2)],
    5: [(0, 0), (1, 0), (1, 1), (2, 1)],
    6: [(0, 0), (1, 0)],
}
EDGES = [("L%d_%d" % (l, a), "L%d_%d" % (l + 1, b)) for l in sorted(_E) for a, b in _E[l]]
NODES = sorted(KIND, key=lambda i: (int(i[1]), int(i[3])))
LAYER = {i: int(i[1]) for i in NODES}
K = {i: int(i[3]) for i in NODES}
WIDTH = {l: sum(1 for i in NODES if LAYER[i] == l) for l in range(8)}

WORD = {"start": "START", "router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK",
        "target": "TARGET"}
FILE = {  # node file rows (the locked FIGHT // L3 file, extended to every type)
    "router": ("T1", "Fight: win it for Cycles and loot", ["15-25 Cycles, a card", "maybe a Firmware chip"]),
    "elite": ("T1", "Elite fight, +1 Heat", ["30-40 Cycles, a rare card", "a Firmware chip"]),
    "terminal": ("T1", "Event: a Terminal voice", ["a choice: card, Cycles or HP"]),
    "modem": ("T1", "Shop: spend Cycles", ["cards, Firmware, a heal"]),
    "rack": ("T2", "Rack: elite fight, then banks", ["banks your Schematics now", "+3 Heat"]),
    "target": ("T2", "The Site's Server Rack", ["the Site, +12 Schematics", "an Exploit"]),
}

WALK_START = ["L0_0"]
WALK_MID = ["L0_0", "L1_0", "L2_0", "L3_0"]          # fight, event, now at the shop


def succ(i):
    return sorted([b for a, b in EDGES if a == i], key=lambda n: (LAYER[n], K[n]))


def reach(froms):
    seen, stack = set(), list(froms)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(succ(n))
    return seen


def states(walked):
    """node -> walked | current | option | reach | target | grey (past or cut off)."""
    cur = walked[-1]
    opts = succ(cur)
    fut = reach(opts)
    st = {}
    for i in NODES:
        if i == cur:
            st[i] = "current"
        elif i in walked:
            st[i] = "walked"
        elif i in opts:
            st[i] = "option"
        elif KIND[i] == "target":
            st[i] = "target"
        elif i in fut:
            st[i] = "reach"
        else:
            st[i] = "grey"
    return st, opts


def edge_states(walked, st):
    out = {}
    for a, b in EDGES:
        if a in walked and b in walked and walked.index(b) == walked.index(a) + 1:
            out[(a, b)] = "walked"
        elif st[a] == "current" and st[b] == "option":
            out[(a, b)] = "option"
        elif st[a] in ("option", "reach") and st[b] in ("reach", "target"):
            out[(a, b)] = "future"
        else:
            out[(a, b)] = "grey"
    return out


def lanes(opts):
    """Per numbered option: the set of nodes it can still reach (itself included) and the edges inside that set."""
    out = []
    for o in opts:
        ns = reach([o])
        es = {(a, b) for a, b in EDGES if a in ns and b in ns}
        out.append((ns, es))
    return out
