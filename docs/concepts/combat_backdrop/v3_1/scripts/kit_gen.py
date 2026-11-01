"""Seeded interior generator (pure python, no bpy; the later Godot port is this logic in GDScript).
generate(room_type, seed) -> spec dict: grid W x D cells (1 cell = 1 m), wall modules, props, hero, lights.
Orientation: rot 0 = prop front faces -y, 1 = +x, 2 = +y, 3 = -x. The camera sees the -y and +x edges,
so the front (-y) and right (+x) edges are the CUT edges: only low props there (view rule)."""
import random
import zlib

W, D = 9, 7                 # layout grid (cells)
LOW = 1.2                   # max prop height on cut-edge cells
# name: (w, d, h)   footprint in cells (rot 0), height in metres
CAT = {
    # bio-lab
    'vat': (1, 1, 2.5), 'vat_bank': (3, 1, 2.6), 'bench': (3, 1, 1.1), 'centrifuge': (1, 1, 1.1),
    'incubator_pod': (2, 1, 1.2), 'monitor_cart': (1, 1, 1.5), 'helix_tank': (2, 2, 3.2),
    # server room
    'rack': (1, 1, 2.5), 'rack_row': (4, 1, 2.5), 'cooling': (2, 1, 1.7), 'console': (2, 1, 1.3),
    'ups': (1, 1, 1.2), 'core_tower': (2, 2, 3.3), 'cable_tray': (3, 1, 0.2),
    # greenhouse / seed vault
    'planter': (2, 1, 0.9), 'plant_tank': (1, 1, 2.2), 'seed_wall': (3, 1, 2.6), 'grow_lamp': (1, 1, 2.4),
    'cistern': (1, 1, 1.3), 'seed_tree': (2, 2, 3.4),
    # office / records
    'desk': (2, 1, 1.4), 'cabinet': (1, 1, 1.5), 'shelf_stack': (2, 1, 2.3), 'copier': (1, 1, 1.2),
    'archive_tower': (2, 2, 3.0), 'box_pile': (1, 1, 0.9),
    # lobby
    'reception': (3, 1, 1.3), 'kiosk': (1, 1, 1.7), 'seats': (2, 1, 0.9), 'planter_lobby': (1, 1, 1.4),
    'emblem_sculpture': (2, 2, 3.0),
    # v3 floor clutter (all <= 1.2 m, allowed on cut-edge cells)
    'crate': (1, 1, 0.7), 'crate_stack': (1, 1, 1.1), 'barrel': (1, 1, 0.9), 'cable_run': (2, 1, 0.12), 'box_small': (1, 1, 0.45),
    # v3 event room (back-room clinic / meeting)
    'holo_table': (2, 2, 2.4), 'exam_bed': (2, 1, 0.95), 'privacy_screen': (2, 1, 1.7), 'folding_chairs': (2, 1, 0.9),
    'med_cabinet': (1, 1, 1.7), 'iv_stand': (1, 1, 1.9), 'scanner_arch': (2, 1, 2.2), 'trestle': (3, 1, 0.8),
    # v3 shop room (street-level storefront)
    'display_island': (2, 2, 1.5), 'counter': (3, 1, 1.1), 'shelf_unit': (3, 1, 2.0), 'gondola': (2, 1, 1.15),
    'cooler': (1, 1, 1.9), 'vending': (1, 1, 1.8), 'crate_display': (1, 1, 0.8), 'basket_rack': (1, 1, 1.1),
    # v3.1 real props (2 per room type)
    'fume_hood': (2, 1, 2.2), 'sample_fridge': (1, 1, 1.9), 'patch_panel': (3, 1, 2.2), 'kvm_cart': (1, 1, 1.2),
    'potting_bench': (3, 1, 1.0), 'water_tank': (1, 1, 2.0), 'filing_row': (3, 1, 1.6), 'water_cooler': (1, 1, 1.5),
    'info_wall': (3, 1, 2.1), 'turnstile': (2, 1, 1.1), 'speaker_stack': (1, 1, 1.8), 'lectern': (1, 1, 1.3),
    'mannequin': (1, 1, 1.9), 'checkout': (1, 1, 1.4),
}
CLUTTER = {'crate', 'crate_stack', 'barrel', 'cable_run', 'box_small'}
ROOMS = {
    'bio_lab': dict(site='Elite Router; Virus-exploit Site (medical security)', hero='helix_tank', dens=(0.52, 0.68),
                    wall=['vat_bank', 'vat', 'bench', 'monitor_cart'], open=['bench', 'centrifuge', 'incubator_pod', 'monitor_cart', 'vat'],
                    light='lime'),
    'server_room': dict(site='Server Rack (layer 4 and 7); Breach-exploit Site', hero='core_tower', dens=(0.54, 0.70),
                        wall=['rack_row', 'rack', 'cooling'], open=['console', 'ups', 'rack', 'cable_tray', 'cooling'], light='cyan'),
    'greenhouse': dict(site='Virus-exploit Site (open-source patch); Heat objective Sites', hero='seed_tree', dens=(0.52, 0.68),
                       wall=['seed_wall', 'plant_tank', 'cistern', 'plant_tank'], open=['planter', 'planter', 'grow_lamp', 'plant_tank', 'cistern'],
                       light='lime'),
    'records_office': dict(site='Router (standard combat); Intel-exploit and Scrub Records Sites', hero='archive_tower', dens=(0.50, 0.66),
                           wall=['shelf_stack', 'cabinet', 'shelf_stack'], open=['desk', 'desk', 'copier', 'cabinet', 'box_pile'], light='amber'),
    'lobby': dict(site='Terminal (event) and Mainframe (shop) nodes; the entry floor of every building', hero='emblem_sculpture', dens=(0.50, 0.64),
                  dens_v2=(0.28, 0.42),
                  wall=['kiosk', 'planter_lobby', 'seats'], open=['seats', 'kiosk', 'planter_lobby', 'reception'], light='lime'),
    # v3 proposals for the netrun street (not Site rooms)
    'event_room': dict(site='PROPOSAL netrun street: event back-room (clinic / meeting)', hero='holo_table', dens=(0.50, 0.66),
                       wall=['privacy_screen', 'med_cabinet', 'scanner_arch', 'privacy_screen'], open=['exam_bed', 'folding_chairs', 'trestle', 'iv_stand', 'med_cabinet'],
                       light='violet', win_back=0, win_left=0, decor='screens'),
    'shop': dict(site='PROPOSAL netrun street: street-level shop interior', hero='display_island', dens=(0.50, 0.66),
                 wall=['shelf_unit', 'cooler', 'vending', 'shelf_unit'], open=['gondola', 'counter', 'crate_display', 'basket_rack', 'gondola'],
                 light='lime', win_back=0, win_left=1, ground=True),
}
CLUTTER_BY_ROOM = {
    'bio_lab': ['cable_run', 'box_small', 'crate', 'cable_run'],
    'server_room': ['cable_run', 'cable_run', 'crate', 'box_small'],
    'greenhouse': ['crate', 'barrel', 'box_small', 'barrel', 'cable_run'],
    'records_office': ['box_small', 'crate', 'crate_stack', 'box_small'],
    'lobby': ['box_small', 'crate', 'cable_run'],
    'event_room': ['cable_run', 'box_small', 'crate'],
    'shop': ['crate', 'crate_stack', 'box_small', 'barrel'],
}


def _fits(occ, x, y, w, d):
    if x < 0 or y < 0 or x + w > W or y + d > D:
        return False
    for i in range(x, x + w):
        for j in range(y, y + d):
            if occ[i][j]:
                return False
    return True


def _mark(occ, x, y, w, d, v=1):
    for i in range(x, x + w):
        for j in range(y, y + d):
            occ[i][j] = v



# ---------------------------------------------------------------- v3.1 phase B: staged dressing (deterministic, seeded)
EXTRAS = {      # real (non-clutter) props added after the v2 layout: (name, 'wall' | 'floor')
    'bio_lab': [('fume_hood', 'wall'), ('sample_fridge', 'wall')],
    'server_room': [('patch_panel', 'wall'), ('kvm_cart', 'floor')],
    'greenhouse': [('potting_bench', 'floor'), ('water_tank', 'wall')],
    'records_office': [('filing_row', 'wall'), ('water_cooler', 'floor')],
    'lobby': [('info_wall', 'wall'), ('turnstile', 'floor')],
    'event_room': [('speaker_stack', 'wall'), ('lectern', 'floor')],
    'shop': [('mannequin', 'floor'), ('checkout', 'floor')],
}
POWERED = {     # props a floor cable may connect (the hero is always one)
    'bio_lab': {'centrifuge', 'incubator_pod', 'monitor_cart', 'vat', 'vat_bank', 'bench', 'fume_hood', 'sample_fridge'},
    'server_room': {'rack', 'rack_row', 'cooling', 'console', 'ups', 'patch_panel', 'kvm_cart'},
    'greenhouse': {'grow_lamp', 'cistern', 'plant_tank', 'planter', 'water_tank', 'seed_wall'},
    'records_office': {'copier', 'desk', 'cabinet', 'filing_row', 'water_cooler', 'shelf_stack'},
    'lobby': {'kiosk', 'reception', 'turnstile', 'info_wall', 'seats'},
    'event_room': {'scanner_arch', 'iv_stand', 'med_cabinet', 'speaker_stack', 'lectern', 'exam_bed', 'privacy_screen'},
    'shop': {'counter', 'vending', 'cooler', 'checkout', 'display_island', 'gondola', 'shelf_unit', 'mannequin'},
}
CABLE_COL = {'bio_lab': 'lime', 'server_room': 'cyan', 'greenhouse': 'pink', 'records_office': 'amber', 'lobby': 'lime',
             'event_room': 'violet', 'shop': 'lime'}
PILE = {        # clutter that makes up wall piles / door stacks
    'bio_lab': ['crate', 'box_small', 'crate_stack'], 'server_room': ['crate', 'box_small', 'crate_stack'],
    'greenhouse': ['crate', 'crate_stack', 'box_small'], 'records_office': ['box_small', 'crate', 'crate_stack', 'box_small'],
    'lobby': ['box_small', 'crate'], 'event_room': ['box_small', 'crate'], 'shop': ['crate', 'crate_stack', 'box_small', 'crate'],
}
NO_BARREL = {'lobby', 'event_room'}      # corners get box piles instead


def _cells(p):
    w, d, h = CAT[p['name']]
    fw, fd = (w, d) if p['rot'] % 2 == 0 else (d, w)
    return [(i, j) for i in range(p['x'], p['x'] + fw) for j in range(p['y'], p['y'] + fd)]


def _route(occ, srcs, dsts, maxlen):
    """Dijkstra over free cells with a turn penalty. srcs/dsts: {free_cell: prop_cell}. returns (cells, start_stub, end_stub) or None"""
    import heapq
    DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    pq = []
    best = {}
    for c in sorted(srcs):
        heapq.heappush(pq, (1.0, c, -1, (c,)))
    while pq:
        cost, c, dr, path = heapq.heappop(pq)
        if (c, dr) in best:
            continue
        best[(c, dr)] = cost
        if c in dsts:
            return list(path)
        if len(path) >= maxlen:
            continue
        for k, (dx, dy) in enumerate(DIRS):
            n = (c[0] + dx, c[1] + dy)
            if not (0 <= n[0] < W and 0 <= n[1] < D) or occ[n[0]][n[1]] not in (0, 2) or n in path:
                continue
            heapq.heappush(pq, (cost + 1.0 + (0.5 if occ[n[0]][n[1]] == 2 else 0.0) + (0.7 if (dr != -1 and dr != k) else 0.0), n, k, path + (n,)))
    return None


def _phase_b(R, cfg, spec, occ, used, counts, target, dw, room_type):
    """Staged dressing after the v2 layout (the v2 prop list is untouched):
    B1 real extra props (2 per room type), B2 hard-prop fill toward 0.50, B3 floor cables that connect hero/powered props,
    B4 crates + box stacks beside the door (outside its 3 cell aisle), B5 barrels in corners, B6 box/crate piles against walls
    (and against props) up to the seeded density, B7 puddles on the street side (cut-edge cells). Rule 7 holds for all."""
    Wc = W * D
    hard_goal = 0.50 * Wc
    max_total = 0.70 * Wc
    state = dict(used=used, cl_n=0, cl_cells=0)

    def put(name, x, y, rot, clutter=False, tag=None):
        w, d, h = CAT[name]
        fw, fd = (w, d) if rot % 2 == 0 else (d, w)
        if h > LOW and (y < 2 or x + fw > W - 2):
            return False
        if not _fits(occ, x, y, fw, fd):
            return False
        if clutter and state['used'] + fw * fd > max_total:
            return False
        _mark(occ, x, y, fw, fd)
        pr = dict(name=name, x=x, y=y, rot=rot)
        if clutter:
            pr['clutter'] = True; state['cl_n'] += 1; state['cl_cells'] += fw * fd
            if tag:
                pr['tag'] = tag
        spec['props'].append(pr)
        state['used'] += fw * fd
        counts[name] = counts.get(name, 0) + 1
        return True

    def free(x, y):
        return 0 <= x < W and 0 <= y < D and occ[x][y] == 0

    # B1 extras
    spec['extras'] = []
    for name, kind in EXTRAS[room_type]:
        w, d, h = CAT[name]
        for _t in range(800):
            if kind == 'wall' and _t < 400:
                if R.random() < 0.6:
                    x = R.randrange(0, W - w + 1); y = D - d; rot = 0
                else:
                    y = R.randrange(0, D - w + 1); x = 0; rot = 1
            else:
                rot = R.choice([0, 0, 1, 1, 2, 3])
                fw, fd = (w, d) if rot % 2 == 0 else (d, w)
                if W - fw - 1 < 1 or D - fd - 1 < 1:
                    continue
                x = R.randrange(1, W - fw); y = R.randrange(1, D - fd)
            if put(name, x, y, rot):
                spec['extras'].append(name)
                break
    # B3 cables: hero -> nearest powered prop -> next nearest ... (2-3 runs)
    spec['cables'] = []
    pw = [p for p in spec['props'] if p.get('hero') or (p['name'] in POWERED[room_type] and not p.get('clutter'))]
    if len(pw) < 3:
        pw = [p for p in spec['props'] if not p.get('clutter') and CAT[p['name']][2] >= 1.0]
    hero = next(p for p in spec['props'] if p.get('hero'))

    def ctr(p):
        cs = _cells(p)
        return (sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs))
    def border(p):
        m = {}
        own = set(_cells(p))
        for (cx_, cy_) in own:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cx_ + dx, cy_ + dy)
                if 0 <= n[0] < W and 0 <= n[1] < D and occ[n[0]][n[1]] in (0, 2) and n not in own:
                    m[n] = (cx_, cy_)
        return m
    cur = hero
    visited = [hero]
    budget = R.choice([7, 9, 11])
    for _k in range(R.choice([2, 3])):
        cx, cy = ctr(cur)
        cands = [p for p in pw if not any(p is v for v in visited)]
        dist = lambda p: ((ctr(p)[0] - cx) ** 2 + (ctr(p)[1] - cy) ** 2) ** 0.5
        cands.sort(key=lambda p: (dist(p) < 2.5, dist(p) + R.random() * 1.5))
        sa = border(cur)
        done = False
        for b in cands:
            sb = border(b)
            if not sa or not sb:
                continue
            path = _route(occ, sa, sb, 12)
            if not path or len([c for c in path if occ[c[0]][c[1]] == 0]) > budget:
                continue
            s0, s1 = path[0], path[-1]
            pa, pb = sa[s0], sb[s1]
            pts = [(s0[0] + 0.5 + (pa[0] - s0[0]) * 0.5, s0[1] + 0.5 + (pa[1] - s0[1]) * 0.5)]
            pts += [(c[0] + 0.5, c[1] + 0.5) for c in path]
            pts.append((s1[0] + 0.5 + (pb[0] - s1[0]) * 0.5, s1[1] + 0.5 + (pb[1] - s1[1]) * 0.5))
            newc = [c for c in path if occ[c[0]][c[1]] == 0]
            for c in newc:
                occ[c[0]][c[1]] = 3
            state['used'] += len(newc); state['cl_cells'] += len(newc); budget -= len(newc)
            spec['cables'].append(dict(pts=pts, cells=path, new=len(newc), col=CABLE_COL[room_type], a=cur['name'], b=b['name']))
            visited.append(b); cur = b; done = True
            break
        if not done:
            break
    spec['cable_cells'] = sum(c['new'] for c in spec['cables'])
    # B2 hard fill toward 0.50 (variety cap loosened to 3 big / 5 small, wall band first)
    tries = 0
    wpool = cfg['wall'] + [n for n, k in EXTRAS[room_type] if k == 'wall']
    opool = cfg['open'] + [n for n, k in EXTRAS[room_type] if k == 'floor']
    while state['used'] - state['cl_cells'] < hard_goal and tries < 4000:
        tries += 1
        if R.random() < 0.5:
            name = R.choice(wpool); w, d, h = CAT[name]
            if R.random() < 0.6:
                x = R.randrange(0, W - w + 1); y = D - d; rot = 0
            else:
                y = R.randrange(0, D - w + 1); x = 0; rot = 1
        else:
            name = R.choice(opool); w, d, h = CAT[name]
            rot = R.choice([0, 0, 1, 1, 2, 3])
            fw, fd = (w, d) if rot % 2 == 0 else (d, w)
            if W - fw - 1 < 1 or D - fd - 1 < 1:
                continue
            x = R.randrange(1, W - fw); y = R.randrange(1, D - fd)
        if counts.get(name, 0) >= (3 if w * d > 1 else 5):
            continue
        put(name, x, y, rot)
    hard_used = state['used']
    goal = min(max_total, max(target, hard_used + 6))        # total fill goal: seeded target, but always >= 6 more cells of dressing
    pile = PILE[room_type]
    # B4 door stacks: just outside the 3 cell aisle, against the back wall
    for xa, side in ((dw - 2, -1), (dw + 3, 1)):
        if R.random() < 0.8 and 0 <= xa < W and state['used'] < goal:
            if put(R.choice(['crate', 'crate_stack']), xa, D - 1, 0, True, 'door'):
                if R.random() < 0.6:
                    put(R.choice(['box_small', 'crate']), xa + side, D - 1, 0, True, 'door') if 0 <= xa + side < W else None
                if R.random() < 0.5:
                    put('box_small', xa, D - 2, R.choice([0, 1]), True, 'door')
    # B5 barrels (or box piles) in corners: back corners first
    corners = [(0, D - 1), (W - 1, D - 1), (0, 0), (W - 1, 0)]
    if R.random() < 0.3:
        corners[2:] = corners[2:][::-1]
    placed = 0
    want = R.choice([1, 2, 2])
    for (cx_, cy_) in corners:
        if placed >= want or state['used'] >= goal:
            break
        if room_type in NO_BARREL:
            ok = put('box_small', cx_, cy_, R.choice([0, 1, 2, 3]), True, 'corner')
        else:
            ok = put('barrel', cx_, cy_, 0, True, 'corner')
            if ok and R.random() < 0.5:
                nx, ny = (cx_ + (1 if cx_ == 0 else -1), cy_) if R.random() < 0.5 else (cx_, cy_ + (1 if cy_ == 0 else -1))
                if free(nx, ny):
                    put('barrel', nx, ny, 0, True, 'corner')
        if ok:
            placed += 1
    # B6 piles against walls and against props, until the density goal
    tries = 0
    while state['used'] < goal and tries < 600:
        tries += 1
        cand = []
        for i in range(W):
            for j in range(D):
                if occ[i][j]:
                    continue
                wall = (i == 0 or j == D - 1)
                near = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + dx < W and 0 <= j + dy < D and occ[i + dx][j + dy] in (1, 3))
                near_cl = any(p.get('clutter') and (i, j) in set((c[0] + dx, c[1] + dy) for c in _cells(p) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) for p in spec['props'][-6:])
                sc = (3 if wall else 0) + (2 if near else 0) + (3 if near_cl else 0)
                if tries > 300:
                    sc += 1
                if sc >= 2:
                    cand.append((sc, i, j))
        if not cand:
            cand = [(1, i, j) for i in range(W) for j in range(D) if not occ[i][j]]
        if not cand:
            break
        top = max(c[0] for c in cand)
        pick = R.choice([c for c in cand if c[0] >= top - 1])
        _, i, j = pick
        rot = 0 if j == D - 1 else (1 if i == 0 else R.choice([0, 1, 2, 3]))
        put(R.choice(pile), i, j, rot, True, 'pile')
    # B7 puddles on the street side (front / right cut edges), floor only
    spec['decals'] = []
    street = [(i, j) for i in range(W) for j in range(D) if occ[i][j] == 0 and (j <= 2 or i >= W - 3)]
    other = [(i, j) for i in range(W) for j in range(D) if occ[i][j] == 0 and (i, j) not in street]
    R.shuffle(street); R.shuffle(other)
    for (i, j) in (street + other)[:R.choice([2, 3, 4])]:
        spec['decals'].append(dict(name='puddle', x=i, y=j, s=R.choice([0.7, 0.9, 1.1])))
    return state['used'], state['cl_n'], state['cl_cells']


def generate(room_type, seed, v2=False):
    """v2=True reproduces the v2 generator exactly (variety cap stops the fill, no clutter); used for the layer below the room."""
    R = random.Random(seed * 7919 + zlib.crc32(room_type.encode()) % 1000)
    cfg = ROOMS[room_type]
    occ = [[0] * D for _ in range(W)]
    spec = dict(room_type=room_type, seed=seed, W=W, D=D, props=[], hero=None, lights=[], windows=[], door=None, rules={})
    # 1. wall modules: back wall (+y, length W) and left wall (-x, length D)
    dw = R.choice([2, 3, 5, 6])
    spec['door'] = dict(wall='back', pos=dw, w=1.4)
    nwin_b = R.choice([2, 3])
    xs = [x for x in range(0, W - 1) if not (dw - 1 <= x <= dw + 2)]
    R.shuffle(xs)
    wins, taken = [], []
    for x in xs:
        if len(wins) >= nwin_b:
            break
        if all(abs(x - t) >= 3 for t in taken):
            wins.append(('back', x, 2)); taken.append(x)
    spec['windows'] = wins
    ly = R.choice([1, 2, 3])
    spec['windows'] += [('left', ly, 2), ('left', ly + 3, 2)] if ly + 3 < D - 1 else [('left', ly, 2)]
    if 'win_back' in cfg:          # v3 rooms override the window counts (RNG draws above are kept so layouts stay seed-stable)
        spec['windows'] = [w for w in spec['windows'] if w[0] == 'back'][:cfg['win_back']] + [w for w in spec['windows'] if w[0] == 'left'][:cfg['win_left']]
    spec['decor'] = cfg.get('decor')
    spec['ground'] = bool(cfg.get('ground'))
    # 2. keep-out: door aisle (3 cells deep from the door) and the hero pad
    for i in range(max(0, dw - 1), min(W, dw + 3)):
        for j in range(D - 3, D):
            occ[i][j] = 2
    hx = R.choice([3, 4, 5]); hy = R.choice([3, 4])
    hw, hd, hh = CAT[cfg['hero']]
    hx = min(hx, W - hw - 2); hy = min(hy, D - hd - 1)
    if any(occ[i][j] for i in range(hx, hx + hw) for j in range(hy, hy + hd)):
        hx = 1 if dw > 4 else W - hw - 2
    spec['hero'] = dict(name=cfg['hero'], x=hx, y=hy, rot=0)
    spec['props'].append(dict(name=cfg['hero'], x=hx, y=hy, rot=0, hero=True))
    _mark(occ, hx, hy, hw, hd)
    # 3. wall band first (back row faces -y, left column faces +x), then the open floor
    target = R.uniform(*(cfg['dens_v2'] if (v2 and 'dens_v2' in cfg) else cfg['dens'])) * W * D
    used = hw * hd
    tries = 0
    counts = {}
    while used < target and tries < 500:
        tries += 1
        wall = R.random() < 0.7 and used < target * 0.65
        if wall:
            name = R.choice(cfg['wall'])
            w, d, h = CAT[name]
            if R.random() < 0.6:
                x = R.randrange(0, W - w + 1); y = D - d; rot = 0; fw, fd = w, d
            else:
                y = R.randrange(0, D - w + 1); x = 0; rot = 1; fw, fd = d, w
        else:
            name = R.choice(cfg['open'])
            w, d, h = CAT[name]
            rot = R.choice([0, 0, 1, 1, 2, 3])
            fw, fd = (w, d) if rot % 2 == 0 else (d, w)
            if W - fw - 1 < 1 or D - fd - 1 < 1:
                continue
            x = R.randrange(1, W - fw); y = R.randrange(1, D - fd)
        # view rule: tall props never on the cut-edge cells (y<2 or x>=W-2)
        if h > LOW and (y < 2 or x + fw > W - 2):
            continue
        if not _fits(occ, x, y, fw, fd):
            continue
        if counts.get(name, 0) >= (2 if w * d > 1 else 3):     # variety rule: max 2 big / 3 small of one prop
            continue
        counts[name] = counts.get(name, 0) + 1
        _mark(occ, x, y, fw, fd)
        spec['props'].append(dict(name=name, x=x, y=y, rot=rot))
        used += fw * fd
    n_v2 = len(spec['props'])
    clutter_n = 0
    clutter_cells = 0
    if not v2:
        used, clutter_n, clutter_cells = _phase_b(R, cfg, spec, occ, used, counts, target, dw, room_type)
    else:
        spec['decals'] = []
    ncab = len(spec.get('cables', []))
    spec['rules'] = dict(density=round(used / (W * D), 2), props=len(spec['props']), clutter=clutter_n, cables=ncab,
                         cable_cells=spec.get('cable_cells', 0), clutter_cells=clutter_cells,
                         density_hard=round((used - clutter_cells) / (W * D), 2), extras=spec.get('extras', []), v2_props=n_v2)
    # 4. lights: hero glow + one pool per 3 props
    spec['light'] = cfg['light']
    spec['lights'] = [dict(x=hx + hw / 2, y=hy + hd / 2, z=1.5, r=4.2)]
    for k, p in enumerate(spec['props']):
        if k % 3 == 1 and not p.get('hero') and not p.get('clutter'):
            w, d, h = CAT[p['name']]
            spec['lights'].append(dict(x=p['x'] + w / 2, y=p['y'] + d / 2, z=1.0, r=2.6))
        if p['name'] == 'grow_lamp':
            spec['lights'].append(dict(x=p['x'] + 0.5, y=p['y'] + 0.5, z=1.5, r=3.2, col='pink'))
    return spec


if __name__ == '__main__':
    for rt, s in (('bio_lab', 11), ('server_room', 23), ('greenhouse', 37), ('records_office', 41), ('lobby', 53), ('event_room', 67), ('shop', 71)):
        sp = generate(rt, s)
        v = generate(rt, s, v2=True)
        print(rt, s, 'v2', v['rules']['density'], 'v3.1', sp['rules'])
