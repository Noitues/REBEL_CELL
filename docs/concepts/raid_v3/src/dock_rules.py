"""dock_rules: the v40 dock rules (game-v2 page / chain_click scripts/core/raid_dock.gd, read-only) on the plate district.

Cells are (c, r) on the 7 x 7 grid; the cell id is r * nc + c as in RaidGrid.  A path is the list of district cells a route
travels INCLUDING its end cell (the Safehouse / the site = g.hq, excluded from sockets); the entry stack waits off the district,
so no district cell is an entry.  Levers: content/config/b_raid_config.tres (dockRadius 3, dockRadiusHq 6, dockMin 4,
dockMax 8, dockMaxHq 12, dockPerSocket 1).
"""
import sys
sys.dont_write_bytecode = True

DOCK = dict(radius=3, radius_hq=6, min=4, max=8, max_hq=12, per_socket=1)


def cid(cell, nc=7):
    return cell[1] * nc + cell[0]


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def junctions(paths, hq):
    """road cells off the HQ where two paths meet or one path turns (RaidDock.junctions)"""
    on = {}
    for p, cs in enumerate(paths):
        for i, c in enumerate(cs):
            on.setdefault(c, []).append((p, i))
    out = set()
    for c, lst in on.items():
        if c == hq:
            continue
        if len(lst) >= 2:
            out.add(c); continue
        p, i = lst[0]
        cs = paths[p]
        if i <= 0 or i >= len(cs) - 1:
            continue
        a, b = cs[i - 1], cs[i + 1]
        if (c[0] - a[0]) != (b[0] - c[0]) or (c[1] - a[1]) != (b[1] - c[1]):
            out.add(c)
    return out


def road(paths, hq):
    return sorted({c for cs in paths for c in cs if c != hq}, key=cid)


def sockets_of(spot, paths, hq, purge=False, nc=7, nr=7):
    """RaidDock.sockets_of: junctions within R of the beacon; under dockMin the nearest plain road cells fill (R grows by one
    until it can); at most dockMax, the nearest win (cheb, then id); returned ascending by id"""
    R = DOCK['radius_hq'] if purge else DOCK['radius']
    mx = DOCK['max_hq'] if purge else DOCK['max']
    jun = junctions(paths, hq)
    rd = sorted(road(paths, hq), key=lambda c: (cheb(c, spot), cid(c)))
    R2 = R
    while True:
        near = [c for c in rd if cheb(c, spot) <= R2]
        out = [c for c in near if c in jun]
        for c in near:
            if len(out) >= DOCK['min']:
                break
            if c not in jun:
                out.append(c)
        if len(out) >= DOCK['min'] or R2 >= max(nc, nr):
            break
        R2 += 1
    return sorted(out[:mx], key=cid), R2


def why(cell, spot, paths, hq, docked, purge=False):
    """the refusal code for docking on `cell` (RaidDock.why_dock's map part): None = legal"""
    socks, _ = sockets_of(spot, paths, hq, purge)
    if cell not in socks:
        if cell not in road(paths, hq) and cell != hq:
            return 'not_a_street'
        if cell == hq:
            return 'safehouse'
        R = DOCK['radius_hq'] if purge else DOCK['radius']
        if cheb(cell, spot) > R:
            return 'too_far'
        return 'not_a_socket'
    if cell in docked:
        return 'socket_taken'
    return None


def beacons_purge(order, hq, legal):
    """RaidDock.beacons for the recalled crew: the first (lowest id) on HQ, the rest on the nearest legal cells to HQ"""
    out, taken = {}, {hq}
    first = True
    for oid in order:
        if first:
            out[oid] = hq; first = False; continue
        cand = sorted([c for c in legal if c not in taken], key=lambda c: (cheb(c, hq), cid(c)))
        out[oid] = cand[0]; taken.add(cand[0])
    return out


if __name__ == '__main__':
    import raid_v3_city as V
    G = V.G
    cl = G.clear()
    for r in range(G.nr):
        print(' '.join('%s:%.2f' % (G.name(c, r), cl[c, r]) for c in range(G.nc)))
    PA = V.RA + [V.SAFE]
    PB = V.RB + [V.SAFE]
    paths = [PA, PB]
    print('junctions', sorted(G.name(*c) for c in junctions(paths, V.SAFE)))
    legal = V.legal_cells(V.RA + V.RB, {V.BARR, V.SAFE})
    print('legal', sorted(G.name(*c) for c in legal))
    bc = beacons_purge(['KAI', 'VEX', 'MOTH', 'RUNE'], V.SAFE, legal)
    print('purge beacons', {k: G.name(*v) for k, v in bc.items()})
    for k, v in bc.items():
        s, R2 = sockets_of(v, paths, V.SAFE, purge=True)
        print(' ', k, [G.name(*c) for c in s], R2)
    sp = [V.SA + [V.SITE], V.SB + [V.SITE], V.SC + [V.SITE]]
    print('site junctions', sorted(G.name(*c) for c in junctions(sp, V.SITE)))
    sl = V.legal_cells(V.SA + V.SB + V.SC, {V.SITE, V.SCORE})
    print('site legal', sorted(G.name(*c) for c in sl))
    for k, v in (('KAI', V.SITE), ('VEX', V.S_VEX)):
        s, R2 = sockets_of(v, sp, V.SITE)
        print(' ', k, G.name(*v), [G.name(*c) for c in s], R2)
    print('SITE', G.name(*V.SITE), 'SCORE', G.name(*V.SCORE), 'S_KAI', G.name(*V.S_KAI), 'S_VEX', G.name(*V.S_VEX))
