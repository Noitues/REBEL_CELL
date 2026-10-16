"""Rebel Cell: the shared SYNC STRIKE machinery for the option graphs (hq_graph_A / hq_graph_C): three operatives on
three lanes, each lane ending at a KILL SWITCH; the three switches must be thrown on the SAME step (a lone throw
re-arms, round 43); DISPATCH counters one room (STALL +1); the roof lanes have DETOURS (+1 step) to stay in step; when
all three are thrown, ONE operative enters DISPATCH (the showdown), the other two PARK at their switches as support.

A variant module defines: NODES, LANES ('L', 'C', 'R'), LANE {node: lane}, PATH [(a, b)], KIND, RUNNERS {lane: name},
MECH {countered, stall}, SWITCH {lane: node}, and calls rc_lanes.bind(globals()).
Walked: one flat list in step order (start, then L, C, R per step; a stall repeats the held room); 'srv' last when an
operative has entered the showdown.
"""


def bind(g):
    def lane_walk(walked, s):
        return ["start"] + [n for n in walked if g["LANE"].get(n) == s]

    def lane_currents(walked):
        return {s: lane_walk(walked, s)[-1] for s in g["LANES"]}

    def _succ(n, walked):
        return sorted((b for a, b in g["PATH"] if a == n and b not in walked), key=lambda b: g["ORDER"][b])

    def thrown(walked):
        return [s for s in g["LANES"] if g["SWITCH"][s] in walked]

    def succ(n, walked, mt=None):
        return _succ(n, walked)

    def states(walked, mt=None):
        cur = lane_currents(walked)
        opts = []
        all_thrown = len(thrown(walked)) == len(g["LANES"])
        for s in g["LANES"]:
            c = cur[s]
            if c == "start":
                opts += [b for b in _succ("start", walked) if g["LANE"].get(b) == s]
            elif c in g["MECH"]["countered"] and walked.count(c) == 1:
                continue                                  # COUNTERED: the runner is held this step (the stall)
            elif g["KIND"].get(c) == "switch":
                if all_thrown and "srv" not in walked:
                    opts += ["srv"]
            else:
                opts += _succ(c, walked)
        opts = sorted(set(opts), key=lambda n: g["ORDER"][n])
        fut, stack = set(), list(opts)
        while stack:
            n = stack.pop()
            if n in fut:
                continue
            fut.add(n)
            stack += [b for a, b in g["PATH"] if a == n]
        st = {}
        curs = set(cur.values())
        for i in g["NODES"]:
            if i in curs and i != "start":
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
        if all(c == "start" for c in cur.values()):
            st["start"] = "current"
        return st, opts

    def edge_states(walked, st, mt=None):
        out = {}
        wl = {s: lane_walk(walked, s) for s in g["LANES"]}
        for a, b in g["PATH"]:
            ln = g["LANE"].get(b, g["LANE"].get(a))
            lw = wl.get(ln, [])
            if a in lw and b in lw and lw.index(b) == lw.index(a) + 1:
                out[(a, b)] = "walked"
            elif b == "srv" and "srv" in walked and a == walked[walked.index("srv") - 1]:
                out[(a, b)] = "walked"
            elif st[b] == "option" and (st[a] == "current" or a == "start"):
                out[(a, b)] = "option"
            elif st[a] in ("option", "reach") and st[b] in ("reach", "target"):
                out[(a, b)] = "future"
            else:
                out[(a, b)] = "grey"
        return out

    def edges(walked, mt=None):
        return list(g["PATH"])

    def branch(o, walked=None, mt=None):
        ns, stack = set(), [o]
        while stack:
            n = stack.pop()
            if n in ns:
                continue
            ns.add(n)
            stack += [b for a, b in g["PATH"] if a == n and b != "srv"]
        return ns, {(a, b) for a, b in g["PATH"] if a in ns and b in ns}

    def eta(walked, s):
        """Steps until lane s throws its switch: (earliest, latest) over its open lines, COUNTERED stalls counted."""
        cur = lane_currents(walked)[s]
        best = []
        M = g["MECH"]

        def walk(n, d):
            if g["KIND"].get(n) == "switch":
                best.append(d)
                return
            for a, b in g["PATH"]:
                if a == n and g["LANE"].get(b) == s:
                    walk(b, d + 1 + (M["stall"] if b in M["countered"] else 0))
        pend = M["stall"] if (cur in M["countered"] and walked.count(cur) == 1) else 0
        walk(cur, pend)
        step = (len([n for n in walked if n not in ("start", "srv")]) + 2) // 3
        return (step + min(best), step + max(best)) if best else (step, step)

    def mech(walked, mt=None):
        e = {s: eta(walked, s) for s in g["LANES"]}
        sync = max(v[0] for v in e.values())
        ok = all(v[0] <= sync <= v[1] for v in e.values())
        th = thrown(walked)
        entered = None
        if "srv" in walked:
            entered = g["LANE"].get(walked[walked.index("srv") - 1])
        return dict(eta=e, sync=sync, sync_ok=ok, countered=list(g["MECH"]["countered"]), affected=list(g["MECH"]["countered"]),
                    thrown=th, showdown=len(th) == len(g["LANES"]), entered=entered, walked=list(walked),
                    step=(len([n for n in walked if n not in ("start", "srv")]) + 2) // 3)

    for k, v in dict(lane_walk=lane_walk, lane_currents=lane_currents, succ=succ, states=states, edge_states=edge_states,
                     edges=edges, branch=branch, eta=eta, mech=mech, thrown=thrown).items():
        g[k] = v
