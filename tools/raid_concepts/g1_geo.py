"""G1 geometry (docs/handoff/raid_integration/G1_SIM.md): the boards the G1 oracle (sweep_g1.py) plays on.

Three board shapes, one interface:
- GraphGeo: the real Solace City Grid (content/corporations/solace.tres, copied through
  D:/rc_tmp/raid_design_lab/integration/solace_geom.py). A board cell is one Site. Lines are paths of Sites from the
  Genome Core to HOME (routes) or cross paths that never reach HOME (streets). Used by concepts A and C.
- WardGeo: concept B. The ten spokes regrouped into three wards (N a-c, M d-g, S h-j); a cell is a BLOCK (one ward at
  one tier). The Exploits move to t2_intel, t2_e, t2_h. Lines are the ward rows and the tier columns, lab style.
- LatticeGeo: concept D. A 3 x 3 lattice of anchors (lab board, W = 3); each anchor carries 2 annexes, and four Heat
  objective Sites hang off anchors as on Solace. Annexes are never on a line.

Pure data and pure functions; the only randomness comes from the rng the caller passes in."""
from __future__ import annotations

from dataclasses import dataclass

TIER_VALUE = {1: 6, 2: 8, 3: 10}        # G1_SIM: Site values T1 6, T2 8, T3 10 (exploit +6 lives in the score)
TYPES = ("D", "N", "E")
HOME = "HOME"
CORE = "core"


@dataclass(frozen=True)
class Line:
    kind: str           # "ROUTE" | "STREET"
    cells: tuple        # cells in scan order (a route: core side first)
    type: str           # D / N / E
    home: bool          # a route reaches HOME after its cells
    ward: int = -1      # WardGeo: the ward row a route runs (HOME hit feeds that ward's meter)


@dataclass
class RaidDraw:
    known: list         # [beam1, extra1, extra2]; extra k fires only at the Heat band
    cands: list         # the 3 sealed route candidates (distinct paths, distinct types)
    real: int           # sealed A
    real_b: int         # sealed B (!= real)
    hunter_type: str
    hunters: list       # 2 street candidates (static hunter), or None when hunter_fn is used
    hunt_real: int
    n_paths: int        # route paths available to the corp this raid
    hunter_fn: object = None   # tongue: fn(front) -> [Line, Line]


# --------------------------------------------------------------------------------------------- Solace (A, C, B base)
SOL_LINKS = {
    "home": ["t1_a", "t1_b", "t1_c", "t1_d", "t1_e", "t1_f", "t1_g", "t1_h", "t1_i", "t1_j"],
    "t1_a": ["t2_intel", "scrub_records"], "t1_b": ["t2_breach"], "t1_c": ["t2_virus"], "t1_d": ["t2_d"],
    "t1_e": ["t2_e"], "t1_f": ["t2_f"], "t1_g": ["t2_g"], "t1_h": ["t2_h"], "t1_i": ["purge_camera_logs"],
    "t1_j": ["wipe_biometrics"],
    "t2_intel": ["t3_core"], "t2_breach": ["t3_b"], "t2_virus": ["t3_c"], "t2_d": ["t3_d"],
    "t2_e": ["t3_e", "burn_the_ledger"], "t2_f": ["t3_f"], "t2_g": ["t3_g"], "t2_h": ["t3_h"],
    "t3_core": [CORE], "t3_b": [CORE], "t3_c": [CORE], "t3_d": [CORE], "t3_e": [CORE], "t3_f": [CORE],
    "t3_g": [CORE], "t3_h": [CORE],
}
SOL_LOCKED = [("t1_a", "t1_b"), ("t1_b", "t1_c"), ("t1_d", "t1_e"), ("t1_f", "t1_g"), ("t1_h", "t1_i"),
              ("t2_intel", "t2_breach"), ("t2_virus", "t2_d"), ("t2_f", "t2_g"),
              ("t3_core", "t3_b"), ("t3_d", "t3_e"), ("t3_g", "t3_h")]
SOL_SPOKE = {"t1_" + s: s for s in "abcdefghij"}
SOL_SPOKE.update({"t2_intel": "a", "t2_breach": "b", "t2_virus": "c", "t2_d": "d", "t2_e": "e", "t2_f": "f",
                  "t2_g": "g", "t2_h": "h", "t3_core": "a", "t3_b": "b", "t3_c": "c", "t3_d": "d", "t3_e": "e",
                  "t3_f": "f", "t3_g": "g", "t3_h": "h", "scrub_records": "a", "purge_camera_logs": "i",
                  "wipe_biometrics": "j", "burn_the_ledger": "e"})
SOL_TIER = {s: int(s[1]) for s in SOL_SPOKE if s.startswith("t") and s[1].isdigit()}
SOL_TIER.update({"scrub_records": 1, "purge_camera_logs": 1, "wipe_biometrics": 2, "burn_the_ledger": 3})
SOL_OBJECTIVE_HEAT = {"scrub_records": -5, "purge_camera_logs": -5, "wipe_biometrics": -8, "burn_the_ledger": -8}
SOL_EXPLOITS = ("t2_intel", "t2_breach", "t2_virus")
VIRUS_KEY, BREACH_KEY = "t2_virus", "t2_breach"


def _adj(pairs) -> dict:
    out = {}
    for a, b in pairs:
        out.setdefault(a, set()).add(b)
        out.setdefault(b, set()).add(a)
    return {k: tuple(sorted(v)) for k, v in out.items()}


SOL_BASE_PAIRS = [(a, b) for a, bs in SOL_LINKS.items() for b in bs]


class BaseGeo:
    """Shared Site data and claim rules. Subclasses set: sites (sorted), tier, value, exploits, objective_heat,
    base_adj, ward_of (site -> 0..2 or -1), cell_sites, site_cell, cells."""
    name = "base"
    sites: tuple = ()
    tier: dict = {}
    exploits: frozenset = frozenset()
    objective_heat: dict = {}
    base_adj: dict = {}
    ward_of: dict = {}
    cell_sites: dict = {}
    site_cell: dict = {}
    cells: tuple = ()
    parent: dict = {}           # LatticeGeo: annex/objective -> anchor

    def value(self, s: str) -> int:
        return TIER_VALUE[self.tier[s]]

    def claimable(self, owned: dict, fallen=()) -> list:
        """Sites not live-owned (unowned or TAKEN: a TAKEN Site can be claimed back) next to HOME or to a live owned
        Site by a base link. The Genome Core is never claimable. Sorted by id."""
        live = {s for s, v in owned.items() if v != "TAKEN"}
        out = []
        for s in self.sites:
            if s in live or self.ward_of.get(s, -1) in fallen and self.ward_of.get(s, -1) >= 0:
                continue
            for n in self.base_adj.get(s, ()):
                if n == "home" or n in live:
                    out.append(s)
                    break
        return out

    def cell_live(self, cell, owned: dict) -> bool:
        for s in self.cell_sites[cell]:
            v = owned.get(s)
            if v == "OK" or v == "DOWN":
                return True
        return False

    def live_cells(self, owned: dict) -> list:
        return [c for c in self.cells if self.cell_live(c, owned)]

    def cell_value(self, cell, owned: dict) -> int:
        """The best live owned Site value in a cell (naive placement order)."""
        best = 0
        for s in self.cell_sites[cell]:
            if owned.get(s) in ("OK", "DOWN"):
                best = max(best, self.value(s) + (6 if s in self.exploits else 0))
        return best

    def exploit_distance(self, s: str, targets) -> int:
        """Link distance (base links, not through HOME or the core) from s to the nearest target Site."""
        if s in targets:
            return 0
        seen = {s}
        frontier = [s]
        d = 0
        while frontier:
            d += 1
            nxt = []
            for a in frontier:
                for b in self.base_adj.get(a, ()):
                    if b in seen or b in ("home", CORE):
                        continue
                    if b in targets:
                        return d
                    seen.add(b)
                    nxt.append(b)
            frontier = nxt
        return 99


class GraphGeo(BaseGeo):
    """The real Solace graph (concepts A and C). path_rule in P-open / P-all / P-target; hunter in street / tongue."""

    def __init__(self, path_rule: str, hunter: str = "street", known_route: float = 0.5, known_early=(0, 0.0),
                 n_known: int = 3, known_target: bool = False):
        self.name = "graph"
        self.n_known = n_known              # known beams drawn per raid (G4 H4: 4, the PURGE band's third extra)
        self.known_target = known_target    # H6 (R-J): known beams draw among the paths through the most owned Sites
        self.known_route = known_route      # chance a known beam is a route (else a street); G1 0.5
        self.known_early = known_early      # (N, p): raids with index < N (st.raid_n) use chance p instead (G3)
        self.path_rule = path_rule
        self.hunter = hunter
        self.sites = tuple(sorted(SOL_TIER))
        self.tier = dict(SOL_TIER)
        self.exploits = frozenset(SOL_EXPLOITS)
        self.objective_heat = dict(SOL_OBJECTIVE_HEAT)
        self.base_adj = _adj(SOL_BASE_PAIRS)
        self.all_adj = _adj(SOL_BASE_PAIRS + SOL_LOCKED)
        self.ward_of = {s: -1 for s in self.sites}
        self.cell_sites = {s: (s,) for s in self.sites}
        self.site_cell = {s: s for s in self.sites}
        self.cells = self.sites
        self.spoke = dict(SOL_SPOKE)
        self.chain = {}         # spoke -> {tier: site} (main chain Sites only)
        for s in self.sites:
            if s in self.objective_heat:
                continue
            self.chain.setdefault(self.spoke[s], {})[self.tier[s]] = s
        self._all_paths = self._paths(self.all_adj, 5)
        self._open_cache = {}

    @staticmethod
    def _paths(adj: dict, max_edges: int) -> list:
        """Every simple path CORE -> home with at most max_edges links, as the Site tuple (core side first), sorted."""
        out = []

        def rec(node, path, seen):
            if len(path) > max_edges:      # path holds Sites (+ core implied); edges = len(path) + 1 at home
                return
            for n in adj.get(node, ()):
                if n == "home":
                    if path and len(path) + 1 <= max_edges:
                        out.append(tuple(path))
                    continue
                if n in seen or n == CORE:
                    continue
                seen.add(n)
                path.append(n)
                rec(n, path, seen)
                path.pop()
                seen.discard(n)

        rec(CORE, [], {CORE})
        return sorted(set(out))

    def open_paths(self, opened) -> list:
        key = frozenset(opened)
        p = self._open_cache.get(key)
        if p is None:
            pairs = SOL_BASE_PAIRS + [l for l in SOL_LOCKED if l in key]
            p = self._paths(_adj(pairs), 9)
            self._open_cache[key] = p
        return p

    def route_pool(self, owned: dict, opened) -> list:
        if self.path_rule == "P-open":
            return self.open_paths(opened)
        return self._all_paths

    def _rings(self, spokes) -> list:
        """Tier rings: the tier-t main-chain Sites of the given spokes, north to south (a street drawn by rule)."""
        out = []
        for t in (1, 2, 3):
            cells = tuple(self.chain[sp][t] for sp in sorted(spokes) if t in self.chain.get(sp, {}))
            if cells:
                out.append(cells)
        return out

    def ring_at(self, spokes, t: int) -> tuple:
        return tuple(self.chain[sp][t] for sp in sorted(spokes) if t in self.chain.get(sp, {}))

    def street_pool(self, cand_cells, owned: dict) -> list:
        """H-street pool: the three tier rings over the candidates' spokes, then the spoke segments (T3 -> T1, never
        HOME) of the other spokes that hold a live owned Site. Distinct cell tuples, in that order."""
        spokes = sorted({self.spoke[s] for cells in cand_cells for s in cells})
        pool = self._rings(spokes)
        live_spokes = sorted({self.spoke[s] for s, v in owned.items() if v != "TAKEN"} - set(spokes))
        for sp in live_spokes:
            ch = self.chain.get(sp, {})
            seg = tuple(ch[t] for t in (3, 2, 1) if t in ch)
            if len(seg) >= 2:
                pool.append(seg)
        seen, out = set(), []
        for p in pool:
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out

    def tongue_tiers(self, front: int) -> list:
        """H-tongue: the two tier columns first inward of the front (column t at t * 1000 strictly below the front),
        padded outward when fewer than two lie inward."""
        inward = [t for t in (3, 2, 1) if t * 1000 < front]
        tiers = inward[:2]
        for t in (1, 2, 3):
            if len(tiers) >= 2:
                break
            if t not in tiers:
                tiers.append(t)
        return tiers[:2]

    @staticmethod
    def most_owned(paths, owned) -> list:
        """H6 (R-J): the paths through the most live owned Sites, in pool order; every path when none crosses one."""
        live = {s for s, v in owned.items() if v != "TAKEN"}
        counts = [sum(1 for s in p if s in live) for p in paths]
        best = max(counts) if counts else 0
        if best == 0:
            return list(paths)
        return [p for p, n in zip(paths, counts) if n == best]

    def draw(self, st, rng) -> RaidDraw:
        pool = self.route_pool(st.owned, st.opened)
        if self.path_rule == "P-target":
            live = {s for s, v in st.owned.items() if v != "TAKEN"}
            keyed = sorted(pool, key=lambda p: (-sum(1 for s in p if s in live), rng.random()))
            cands = keyed[:3]
        else:
            cands = rng.sample(pool, 3)
        perm = list(TYPES)
        rng.shuffle(perm)
        cand_lines = [Line("ROUTE", c, perm[k], True) for k, c in enumerate(cands)]
        real = rng.randrange(3)
        real_b = [k for k in range(3) if k != real][rng.randrange(2)]
        spool = self.street_pool(cands, st.owned)
        kpool, kspool = pool, spool
        if self.known_target:       # H6 (R-J): the known beams aim at the owned Sites, as the sealed candidates do
            kpool = self.most_owned(pool, st.owned)
            kspool = self.most_owned(spool, st.owned)
        known = []
        for _ in range(self.n_known):
            p = self.known_early[1] if getattr(st, "raid_n", 0) < self.known_early[0] else self.known_route
            if rng.random() < p:
                known.append(Line("ROUTE", rng.choice(kpool), rng.choice(TYPES), True))
            else:
                known.append(Line("STREET", rng.choice(kspool), rng.choice(TYPES), False))
        ht = rng.choice(TYPES)
        if self.hunter == "tongue":
            spokes = sorted({self.spoke[s] for cells in cands for s in cells})

            def fn(front, spokes=spokes, ht=ht):
                return [Line("STREET", self.ring_at(spokes, t), ht, False) for t in self.tongue_tiers(front)]
            hunters = None
        else:
            fn = None
            hc = rng.sample(spool, 2) if len(spool) >= 2 else spool * 2
            hunters = [Line("STREET", c, ht, False) for c in hc]
        hreal = rng.randrange(2)
        return RaidDraw(known, cand_lines, real, real_b, ht, hunters, hreal, len(pool), fn)


# --------------------------------------------------------------------------------------------- B: three wards
B_EXPLOITS = ("t2_e", "t2_h", "t2_intel")
WARD_NAMES = ("N", "M", "S")


class WardGeo(BaseGeo):
    """Concept B: Solace regrouped into three wards; cells are blocks (ward, tier)."""

    def __init__(self):
        self.name = "wards"
        self.sites = tuple(sorted(SOL_TIER))
        self.tier = dict(SOL_TIER)
        self.exploits = frozenset(B_EXPLOITS)
        self.objective_heat = dict(SOL_OBJECTIVE_HEAT)
        self.base_adj = _adj(SOL_BASE_PAIRS)
        self.ward_of = {s: (0 if SOL_SPOKE[s] in "abc" else 1 if SOL_SPOKE[s] in "defg" else 2) for s in self.sites}
        self.cells = tuple("%s%d" % (WARD_NAMES[w], t) for w in range(3) for t in (1, 2, 3))
        bonus = lambda s: self.value(s) + (6 if s in self.exploits else 0)
        cs = {c: [] for c in self.cells}
        for s in self.sites:
            cs["%s%d" % (WARD_NAMES[self.ward_of[s]], self.tier[s])].append(s)
        # a beam on a block HITs its most valuable live owned Site (ties by Site id)
        self.cell_sites = {c: tuple(sorted(v, key=lambda s: (-bonus(s), s))) for c, v in cs.items()}
        self.site_cell = {s: c for c, v in self.cell_sites.items() for s in v}

    def row(self, w: int, t: str) -> Line:
        return Line("ROUTE", tuple("%s%d" % (WARD_NAMES[w], k) for k in (3, 2, 1)), t, True, w)

    def col(self, k: int, down: bool, t: str) -> Line:
        ws = range(3) if down else range(2, -1, -1)
        return Line("STREET", tuple("%s%d" % (WARD_NAMES[w], k) for w in ws), t, False)

    def _rand_line(self, rng) -> Line:
        if rng.random() < 0.5:
            return self.row(rng.randrange(3), rng.choice(TYPES))
        k = rng.randrange(3) + 1
        down = rng.random() < 0.5
        return self.col(k, down, rng.choice(TYPES))

    def draw(self, st, rng) -> RaidDraw:
        known = [self._rand_line(rng) for _ in range(3)]
        perm = list(TYPES)
        rng.shuffle(perm)
        cands = [self.row(w, perm[w]) for w in range(3)]
        real = rng.randrange(3)
        real_b = [k for k in range(3) if k != real][rng.randrange(2)]
        ht = rng.choice(TYPES)
        hc = rng.sample((1, 2, 3), 2)
        hunters = [self.col(k, True, ht) for k in hc]
        return RaidDraw(known, cands, real, real_b, ht, hunters, rng.randrange(2), 3)


# --------------------------------------------------------------------------------------------- D: lattice
D_ROUTES = ("A", "B", "C")
D_OBJECTIVES = {"obj_A1": ("A1", -5), "obj_C1": ("C1", -5), "obj_C2": ("C2", -8), "obj_B3": ("B3", -8)}


class LatticeGeo(BaseGeo):
    """Concept D: 9 anchors (route A/B/C x tier 1..3, full streets), 2 annexes per anchor, 4 Heat objectives."""

    def __init__(self):
        self.name = "lattice"
        anchors = ["%s%d" % (r, t) for r in D_ROUTES for t in (1, 2, 3)]
        self.anchors = tuple(anchors)
        self.parent = {}
        tier = {}
        for a in anchors:
            tier[a] = int(a[1])
            for x in "ab":
                tier[a + x] = int(a[1])
                self.parent[a + x] = a
        self.objective_heat = {}
        for o, (a, h) in D_OBJECTIVES.items():
            tier[o] = int(a[1])
            self.parent[o] = a
            self.objective_heat[o] = h
        self.tier = tier
        self.sites = tuple(sorted(tier))
        self.exploits = frozenset("%s2" % r for r in D_ROUTES)
        pairs = []
        for r in range(3):
            pairs.append(("home", "%s1" % D_ROUTES[r]))
            for t in (1, 2, 3):
                a = "%s%d" % (D_ROUTES[r], t)
                if t < 3:
                    pairs.append((a, "%s%d" % (D_ROUTES[r], t + 1)))
                if r < 2:
                    pairs.append((a, "%s%d" % (D_ROUTES[r + 1], t)))
        for s, a in self.parent.items():
            pairs.append((a, s))
        self.base_adj = _adj(pairs)
        self.ward_of = {s: -1 for s in self.sites}
        self.cells = self.anchors
        self.cell_sites = {a: (a,) for a in anchors}
        self.site_cell = {a: a for a in anchors}

    def row(self, r: int, t: str) -> Line:
        return Line("ROUTE", tuple("%s%d" % (D_ROUTES[r], k) for k in (3, 2, 1)), t, True)

    def col(self, k: int, down: bool, t: str) -> Line:
        rs = range(3) if down else range(2, -1, -1)
        return Line("STREET", tuple("%s%d" % (D_ROUTES[r], k) for r in rs), t, False)

    def _rand_line(self, rng) -> Line:
        if rng.random() < 0.5:
            return self.row(rng.randrange(3), rng.choice(TYPES))
        k = rng.randrange(3) + 1
        down = rng.random() < 0.5
        return self.col(k, down, rng.choice(TYPES))

    def draw(self, st, rng) -> RaidDraw:
        known = [self._rand_line(rng) for _ in range(3)]
        perm = list(TYPES)
        rng.shuffle(perm)
        cands = [self.row(r, perm[r]) for r in range(3)]
        real = rng.randrange(3)
        real_b = [k for k in range(3) if k != real][rng.randrange(2)]
        ht = rng.choice(TYPES)
        hc = rng.sample((1, 2, 3), 2)
        hunters = [self.col(k, True, ht) for k in hc]
        return RaidDraw(known, cands, real, real_b, ht, hunters, rng.randrange(2), 3)
