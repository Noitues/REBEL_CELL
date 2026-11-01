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
    if not v2:
        # v3 phase B: the v2 layout is kept, then the fill continues with (a) a loosened variety cap (3 big / 5 small) and
        # (b) floor clutter (crates, barrels, boxes, cable runs) on any free cell, until the density target is met.
        cl = CLUTTER_BY_ROOM[room_type]
        tries = 0
        while used < target and tries < 2500:
            tries += 1
            if R.random() < 0.5:
                name = R.choice(cl)
                w, d, h = CAT[name]
                rot = R.choice([0, 1, 2, 3])
                fw, fd = (w, d) if rot % 2 == 0 else (d, w)
                x = R.randrange(0, W - fw + 1); y = R.randrange(0, D - fd + 1)
                if counts.get(name, 0) >= 5:
                    continue
            else:
                wall = R.random() < 0.5
                if wall:
                    name = R.choice(cfg['wall']); w, d, h = CAT[name]
                    if R.random() < 0.6:
                        x = R.randrange(0, W - w + 1); y = D - d; rot = 0; fw, fd = w, d
                    else:
                        y = R.randrange(0, D - w + 1); x = 0; rot = 1; fw, fd = d, w
                else:
                    name = R.choice(cfg['open']); w, d, h = CAT[name]
                    rot = R.choice([0, 0, 1, 1, 2, 3])
                    fw, fd = (w, d) if rot % 2 == 0 else (d, w)
                    if W - fw - 1 < 1 or D - fd - 1 < 1:
                        continue
                    x = R.randrange(1, W - fw); y = R.randrange(1, D - fd)
                if counts.get(name, 0) >= (3 if w * d > 1 else 5):
                    continue
            if h > LOW and (y < 2 or x + fw > W - 2):       # rule 7 holds for everything
                continue
            if not _fits(occ, x, y, fw, fd):
                continue
            counts[name] = counts.get(name, 0) + 1
            _mark(occ, x, y, fw, fd)
            pr = dict(name=name, x=x, y=y, rot=rot)
            if name in CLUTTER:
                pr['clutter'] = True; clutter_n += 1
            spec['props'].append(pr)
            used += fw * fd
        # puddle decals (no occupancy, floor only): 2-4 on free cells, flavoured to the room light
        spec['decals'] = []
        free = [(i, j) for i in range(W) for j in range(D) if occ[i][j] == 0]
        R.shuffle(free)
        for (i, j) in free[:R.choice([2, 3, 4])]:
            spec['decals'].append(dict(name='puddle', x=i, y=j, s=R.choice([0.7, 0.9, 1.1])))
    else:
        spec['decals'] = []
    spec['rules'] = dict(density=round(used / (W * D), 2), props=len(spec['props']), clutter=clutter_n,
                         density_hard=round((used - sum((lambda c: c[0] * c[1])(CAT[p['name']]) for p in spec['props'] if p.get('clutter'))) / (W * D), 2),
                         v2_props=n_v2)
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
        print(rt, s, 'v2', v['rules']['density'], 'v3', sp['rules'])
