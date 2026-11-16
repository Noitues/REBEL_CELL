"""dock_rules: the raid dock rules on the plate district, ported line by line from the build (read-only).

Two rule sets, both kept so each set stays reproducible:
- v40 (set 8 as first drawn, 2026-11-15): chain_click scripts/core/raid_dock.gd; levers content/config/b_raid_config.tres
  (dockRadius 3, dockRadiusHq 6, dockMin 4, dockMax 8, dockMaxHq 12, dockPerSocket 1): SOCKETS = route junctions near the post.
- v42 (set 8 re-staged, 2026-11-16): godot_look 6a99f5c0 (port-campaign-b, "port synced to prototype v42 (route slots,
  opening rule)") scripts/core/raid_dock.gd + scripts/ui/raid/b_raid_place_model.gd; the campaign's levers
  content/config/b_campaign_config.tres, copied onto the raid by BCampaignRaid.dock_lv (dockRule 1, slotRule 1, slotShare 0,
  dockRadius 3, dockRadiusHq 6, dockMin 4, dockMax 0, dockMaxHq 0 = no cap, dockPerSocket 1, dockSupSide 0, dockSupReach 2):
  ROUTE SLOTS ("street slot") = every street cell within the radius; one piece per slot (a weapon, or a street device).
  The v42 "opening rule" (core/takeover_opening.gd, takeover_setup.gd) is the street FIGHT's first-turn guard; it does not
  touch the raid dock, so nothing of it shows at raid plan time.

Cells are (c, r) on the 7 x 7 grid; the cell id is r * nc + c as in RaidGrid.  A path is the list of district cells a route
travels INCLUDING its end cell (the Safehouse / the site = g.hq, excluded from slots); the entry stack waits off the district,
so no district cell is an entry.  "Road" = a cell some corp route uses (RaidGrid: cl.road is set from the paths only).

python dock_rules.py   prints posts, v40 sockets and v42 slots for both plate raids, and a few v42 refusals.
"""
import sys
sys.dont_write_bytecode = True

DOCK = dict(radius=3, radius_hq=6, min=4, max=8, max_hq=12, per_socket=1)          # v40 (b_raid_config.tres as ported then)
DOCK42 = dict(radius=3, radius_hq=6, min=4, max=0, max_hq=0, per_socket=1,          # v42 (b_campaign_config.tres @ 6a99f5c0)
              slot_rule=1, slot_share=0, sup_side=0, sup_reach=2,
              sup_pct=15, sup_keep=1)                       # dockSupPct / dockSupKeep (RaidDock.sup_pct_on / sup_kept), PROVISIONAL
# street (road) devices (RaidContent.device_on_road; the lever text: barricade, mine, tar, shock fence, gate) and the
# blocking one (device_has r_dev_wall), for slot_piece
ROAD_DEVS = {'BARRICADE', 'MINE', 'TAR', 'SHOCK', 'GATE'}
WALL_DEVS = {'BARRICADE'}


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


# ------------------------------------------------------------------------------------------------ v40 (kept as drawn)
def sockets_of(spot, paths, hq, purge=False, nc=7, nr=7):
    """v40 RaidDock.sockets_of: junctions within R of the beacon; under dockMin the nearest plain road cells fill (R grows by
    one until it can); at most dockMax, the nearest win (cheb, then id); returned ascending by id"""
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
    """v40: the refusal code for docking on `cell` (RaidDock.why_dock's map part): None = legal"""
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


# ------------------------------------------------------------------------------------------------ v42 route slots
def slots_of(spot, paths, hq, purge=False, supporter=False, lv=DOCK42, nc=7, nr=7):
    """v42 RaidDock.sockets_of (6a99f5c0), line by line.  Returns (slots ascending by id, the radius used).
        road = road cells off hq and the entries, sorted (cheb to spot, id)
        supporter and not hq and dockSupSide != 0: reach = min(R, dockSupReach); the road cells within it (slotRule 1: all of
            them; else junctions, or all when none), the first mx (mx > 0), sorted by id
        else: R2 = R; loop: near = road within R2; slotRule 1: out = near (no junction preference); else v40's junctions +
            fill to dockMin; stop when len(out) >= dockMin or R2 >= max(w, h); else R2 += 1
        res = out[:mx] if mx > 0 else out (v42: dockMax / dockMaxHq 0 = no cap), sorted by id"""
    R = lv['radius_hq'] if purge else lv['radius']
    mn = lv['min']
    mx = lv['max_hq'] if purge else lv['max']
    jun = junctions(paths, hq)
    rd = sorted(road(paths, hq), key=lambda c: (cheb(c, spot), cid(c)))
    if not purge and lv['sup_side'] != 0 and supporter:
        reach = min(R, lv['sup_reach'])
        nr_ = [c for c in rd if cheb(c, spot) <= reach]
        q = nr_ if lv['slot_rule'] != 0 else [c for c in nr_ if c in jun]
        if not q:
            q = nr_
        r2 = q[:mx] if mx > 0 else list(q)
        return sorted(r2, key=cid), reach
    out = []
    R2 = R
    max_r = max(nc, nr)
    while True:
        near = [c for c in rd if cheb(c, spot) <= R2]
        if lv['slot_rule'] != 0:
            out = list(near)
        else:
            out = [c for c in near if c in jun]
            for c in near:
                if len(out) >= mn:
                    break
                if c not in jun:
                    out.append(c)
        if len(out) >= mn or R2 >= max_r:
            break
        R2 += 1
    res = out[:mx] if mx > 0 else list(out)
    return sorted(res, key=cid), R2


def slot_piece(dk, lv=DOCK42):
    """v42 RaidDock.slot_piece: a street device of kind dk excludes a weapon on its cell (slotShare 0: every street device;
    1: only the blocking one; 2 / slotRule 0: none)"""
    if lv['slot_rule'] == 0 or lv['slot_share'] >= 2 or dk not in ROAD_DEVS:
        return False
    return lv['slot_share'] == 0 or dk in WALL_DEVS


def why42(cell, spot, paths, hq, wpn_at, dev_at, purge=False, supporter=False, own_cell=None, lv=DOCK42):
    """v42 RaidDock.why_dock's map part, the checks in the source's order: None = legal, else the code.
    wpn_at: {cell: owner} of the docked weapons; dev_at: {cell: device kind} of the live street devices; own_cell: the held
    weapon's own slot (None = not docked).  dockOverrun 0 and dockSupMax 0 in the campaign: those two checks never fire."""
    slots, _ = slots_of(spot, paths, hq, purge, supporter, lv)
    if cell not in slots:
        R = lv['radius_hq'] if purge else lv['radius']
        if cell not in road(paths, hq) and cell != hq:
            return 'not_a_street'
        if cell == hq:
            return 'safehouse'
        if cheb(cell, spot) > R:
            return 'too_far'
        return 'not_a_socket'
    if own_cell is not None and own_cell == cell:
        return 'already_here'
    if cell in dev_at and slot_piece(dev_at[cell], lv):
        return 'slot_piece'                                   # "<device> here"
    if cell in wpn_at and cell != own_cell:
        return 'socket_taken'
    return None


def why_dev42(cell, dk, wpn_at, lv=DOCK42):
    """v42 BRaidPlaceModel.why (DEVICE) map part: a street device refused on a weapon's slot ('slot_piece', "weapon here")"""
    if cell in wpn_at and slot_piece(dk, lv):
        return 'slot_piece'
    return None


def beacons_purge(order, hq, legal):
    """RaidDock.beacons for the recalled crew (unchanged v40 -> v42): the first (lowest id) on HQ, the rest on the nearest
    legal cells to HQ"""
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
    nm = lambda cs: [G.name(*c) for c in cs]
    PA = V.RA + [V.SAFE]
    PB = V.RB + [V.SAFE]
    paths = [PA, PB]
    legal = V.legal_cells(V.RA + V.RB, {V.BARR, V.SAFE})
    bc = beacons_purge(['KAI', 'VEX', 'MOTH', 'RUNE'], V.SAFE, legal)
    print('PURGE beacons', {k: G.name(*v) for k, v in bc.items()})
    print('  road', nm(road(paths, V.SAFE)), 'junctions', sorted(nm(junctions(paths, V.SAFE))))
    for k, v in bc.items():
        s42 = slots_of(v, paths, V.SAFE, purge=True)
        print('  v40', k, nm(sockets_of(v, paths, V.SAFE, purge=True)[0]), '| v42', nm(s42[0]), 'R', s42[1])
    sp = [V.SA + [V.SITE], V.SB + [V.SITE], V.SC + [V.SITE]]
    print('SITE', G.name(*V.SITE), 'road', nm(road(sp, V.SITE)))
    for k, v, sup in (('KAI', V.SITE, False), ('VEX', V.S_VEX, True)):
        print('  v40', k, G.name(*v), nm(sockets_of(v, sp, V.SITE)[0]), '| v42', nm(slots_of(v, sp, V.SITE, supporter=sup)[0]))
    w = {(1, 4): 'KAI', (1, 6): 'VEX'}
    for cell in [(4, 5), (1, 2), (1, 4), (2, 5), (1, 6), (0, 4)]:
        print('  VEX holds its rail (on b7) over', G.name(*cell), '->', why42(cell, V.S_VEX, sp, V.SITE, w, {}, supporter=True, own_cell=(1, 6)))
    wp = {(3, 6): 'KAI', (1, 6): 'MOTH'}
    dv = {V.BARR: 'BARRICADE'}
    for cell in [(1, 3), (3, 6), (3, 5), (1, 0), (2, 6)]:
        print('  RUNE holds its shotgun over', G.name(*cell), '->', why42(cell, bc['RUNE'], paths, V.SAFE, wp, dv, purge=True))
    print('  a MINE held over d7 ->', why_dev42((3, 6), 'MINE', wp))
