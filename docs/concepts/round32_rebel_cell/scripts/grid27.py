"""Round 32: the Cell's district WITHOUT the fist streets. Patches the game's layout dict (round6 city_layout.json,
read-only on disk) in memory so the map (map27.py) and the Blender scene (layout27.py -> hq32.py) share it:
  1. the fist roads are dropped;
  2. the regular street grid is completed through the district: every missing cell on the grid's own street lines
     (the i / j lines the rest of the city uses) is added, copying lane colour, traffic and lane axis from the nearest
     cell of the same line, so the district has the same grid as the rest of the map;
  3. city buildings standing on those new street cells are removed;
  4. the empty strips the fist roads leave are filled with buildings cloned (shifted by whole lots) from the
     district's own small buildings, so no ghost of the fist remains. All choices are seeded.
"""
import bisect
import copy
import math
import random

import citydata as CD

BOX = (12, 61, 16, 61)  # district window in lots: i0, i1, j0, j1


def _shift_flat(flat, dX, dY):
    return [v + (dX if k % 2 == 0 else dY) for k, v in enumerate(flat)]


def patch(d):
    L = CD.Lots(d)
    fist = CD.fist_lots(d, L)
    palm = CD.rc_base_centre(d, L)
    i0, i1, j0, j1 = BOX
    cells = {(s["i"], s["j"]): s for s in d["streets"]}
    ilines = sorted({s["i"] for s in d["streets"] if s["ai"] and j0 - 8 <= s["j"] < j1 + 8 and i0 - 8 <= s["i"] < i1 + 8})
    jlines = sorted({s["j"] for s in d["streets"] if s["aj"] and j0 - 8 <= s["j"] < j1 + 8 and i0 - 8 <= s["i"] < i1 + 8})
    new = []
    for i in range(i0, i1):
        for j in range(j0, j1):
            if (i, j) in cells:
                continue
            ai, aj = i in ilines, j in jlines
            if not (ai or aj):
                continue
            # template: nearest existing cell with the same flags on the same line
            cands = [s for s in d["streets"] if s["ai"] == ai and s["aj"] == aj and
                     ((s["i"] == i) if (ai and not aj) else (s["j"] == j) if (aj and not ai) else True) and ("ab" in s or (ai and aj))]
            t = min(cands, key=lambda s: (abs(s["i"] - i) + abs(s["j"] - j), s["i"], s["j"]))
            di, dj = i - t["i"], j - t["j"]
            p = [L.iso(x, y) for (x, y) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            c = dict(i=i, j=j, ai=ai, aj=aj, traffic=t.get("traffic", 0.0), p=[v for q in p for v in q])
            if "col" in t:
                c["col"] = list(t["col"])
            if "ab" in t:
                ab = [L.iso(x + di, y + dj) for (x, y) in L.pts(t["ab"])]
                c["ab"] = [v for q in ab for v in q]
            new.append(c)
            cells[(i, j)] = c
    d["streets"] = d["streets"] + new
    newset = {(c["i"], c["j"]) for c in new}
    # buildings on the new street cells go
    ctxs = d["contexts"]

    def cen(p):
        q = L.pts(p["b"])
        return (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q))

    keep = []
    for p in d["prims"]:
        if p["t"] == "ext" and p.get("ctx", -1) >= 0 and ctxs[p["ctx"]]["kind"] == "bld":
            c = cen(p)
            if (math.floor(c[0]), math.floor(c[1])) in newset:
                continue
        keep.append(p)
    d["prims"] = keep
    # fill the strips the fist roads left empty
    occ = set()
    by_ctx = {}
    for p in d["prims"]:
        if p["t"] == "ext" and p.get("ctx", -1) >= 0 and ctxs[p["ctx"]]["kind"] == "bld":
            c = cen(p)
            occ.add((math.floor(c[0]), math.floor(c[1])))
            by_ctx.setdefault(p["ctx"], []).append(p)
    small = []
    for ci, ps in sorted(by_ctx.items()):
        qs = [xy for p in ps for xy in L.pts(p["b"])]
        xs, ys = [q[0] for q in qs], [q[1] for q in qs]
        if max(xs) - min(xs) < 1.1 and max(ys) - min(ys) < 1.1 and i0 <= min(xs) < i1 and j0 <= min(ys) < j1:
            small.append((ci, math.floor(sum(xs) / len(xs)), math.floor(sum(ys) / len(ys))))
    others = {ci: [p for p in d["prims"] if p.get("ctx", -1) == ci and p["t"] != "ext"] for ci, _, _ in small}
    added = 0
    # the game draws prims back to front (by cell i + j): clones are inserted at their depth
    depth = []
    last = -10 ** 9
    for p in d["prims"]:
        ci_ = p.get("ctx", -1)
        if ci_ >= 0 and "cell" in ctxs[ci_]:
            last = max(last, ctxs[ci_]["cell"][0] + ctxs[ci_]["cell"][1])
        depth.append(last)
    inserts = []
    for i in range(i0, i1):
        for j in range(j0, j1):
            if (i, j) in cells or (i, j) in occ:
                continue
            if not CD.near_fist((i + 0.5, j + 0.5), fist, 1.6):
                continue
            r = random.Random(i * 7919 + j * 104729 + 27)
            if r.random() < 0.18:  # a few lots stay open (yards), as elsewhere in the city
                continue
            ci, si, sj = small[r.randrange(len(small))]
            di, dj = i - si, j - sj
            dX, dY = (di - dj) * 34.0, (di + dj) * 17.0
            nc = copy.deepcopy(ctxs[ci])
            for key in ("base",):
                if key in nc and isinstance(nc[key], list) and len(nc[key]) >= 2:
                    nc[key] = [nc[key][0] + dX, nc[key][1] + dY] + nc[key][2:]
            if "cell" in nc:
                nc["cell"] = [i, j] + list(nc["cell"][2:])
            nc["terr"] = "rebel_cell"
            ctxs.append(nc)
            nci = len(ctxs) - 1
            block = []
            for p in by_ctx[ci] + others[ci]:
                q = copy.deepcopy(p)
                q["ctx"] = nci
                if "b" in q:
                    q["b"] = _shift_flat(q["b"], dX, dY)
                if "p" in q:
                    q["p"] = _shift_flat(q["p"], dX, dY)
                if "key" in q:
                    q["key"] = q["key"] * 31 + i * 1009 + j
                block.append(q)
            pos = bisect.bisect_right(depth, i + j)
            inserts.append((pos, len(inserts), block))
            added += 1
    out = []
    k = 0
    for pos, _, block in sorted(inserts, key=lambda t: (t[0], t[1])):
        out.extend(d["prims"][k:pos])
        out.extend(block)
        k = pos
    out.extend(d["prims"][k:])
    d["prims"] = out
    d["fist"] = []
    return dict(palm=palm, new_cells=len(new), filled=added, ilines=ilines, jlines=jlines)
