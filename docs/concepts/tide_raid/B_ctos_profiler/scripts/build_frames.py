"""Builds the direction-B beat frames over the real Solace plates.  usage: python build_frames.py [frame ...]"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctos_common import *
from ctos_scene import *

CITY = load_city()
CITY_DECAY = load_city(22)   # decay scenario camera sits 22 plate px higher
_masks = {}
OUTF = OUT


def mask_for(j):
    if 'm' not in _masks:
        _masks['m'] = territory_mask(j)
    return _masks['m']


def base(sc, taken=(), grow=1.0, sweep=None, wire=0.55, extra=None, flood=None, radius=130, bright=1.0, keep=0.10, vein=1.0, city=None):
    g = grade(city if city is not None else CITY, sc.mask, sweep, wire)
    g = np.clip(g * bright, 0, 1.2)
    f = None
    cs = infect_centres(sc.j, set(taken), sc.anch, extra)
    if cs:
        g, f = infect(g, cs, radius=radius, grow=grow, keep=keep, vein=vein)
    return g


def ambient(sc, img, n=46, seed=5, a=120):
    """Living city: faint profiler brackets + glyph ticks on lit rooftops and moving cars across the territory."""
    rnd = random.Random(seed)
    L = lum(img)
    ys, xs = np.where((L > 0.62) & (sc.mask > 0.55))
    if len(xs) == 0:
        return
    pts = []
    tries = 0
    while len(pts) < n and tries < 4000:
        tries += 1
        i = rnd.randrange(len(xs))
        x, y = float(xs[i]), float(ys[i])
        if y < 140 or y > 960 or any(math.hypot(x - px, y - py) < 62 for px, py in pts):
            continue
        pts.append((x, y))
    G = sc.G
    for k, (x, y) in enumerate(pts):
        c = GRID
        kind = k % 4
        if kind == 0:
            bracket_box(G, x - 9, y - 7, 18, 14, c, c=4, th=1.2, a=a, glow=0.2)
        elif kind == 1:
            G.line([(x, y), (x + 14, y - 14), (x + 30, y - 14)], c, 1.0, a, glow=0.15)
            G.poly(hexg(x + 33, y - 14, 3.2, 0), outline=c, w=1.0, a=a)
        elif kind == 2:
            bracket_box(G, x - 7, y - 5, 14, 10, (255, 255, 255), c=3, th=1.0, a=a, glow=0.1)
            G.line([(x - 22, y + 2), (x - 9, y + 2)], c, 1.0, a // 2)
        else:
            G.poly(hexg(x, y, 4, math.pi / 6), outline=c, w=1.0, a=a)
            G.line([(x, y - 4), (x, y - 20)], c, 0.9, a // 2)


def finish_save(sc, img, name, glow_gain=1.0, ground_first=True):
    if not getattr(sc, 'noamb', False):
        ambient(sc, img)
    img = blend_layer(img, sc.G, glow_gain)
    img = blend_layer(img, sc.U, glow_gain)
    img = finish(img)
    to_img(img).save(f'{OUTF}/{name}.png')
    return img


def taken_ids(j):
    return [s['id'] for s in j['sites'] if s['state'] in ('TAKEN', 'INFECTED')] + [t for t in j['taken']]


# ------------------------------------------------------------------ stats for the forecast
def forecast_stats(j):
    guards = {c['site']: c['type'] for c in j['defense_cards'] if c['verb'] == 'GUARD'}
    hit = {}
    shield = {}
    for b in j['beams']:
        w = {'known': 1.0, 'cand': 1 / 3, 'hunter': 0.5}[b['role']]
        for sid in b['site_path']:
            if sid in ('the_genome_core', 'home'):
                continue
            if guards.get(sid) == b['type']:
                shield[sid] = shield.get(sid, 0) + w
                break
            hit[sid] = 1 - (1 - hit.get(sid, 0)) * (1 - w)
    return hit, shield, guards


def ordered(j):
    order = {'known': 0, 'cand': 1, 'hunter': 2}
    return sorted(j['beams'], key=lambda b: (order[b['role']], b['name']))


# ------------------------------------------------------------------ site furniture
def site_furniture(sc, tags=True, hit=None, shield=None, guards=None, chips=True, marks=True, only_tags=None, words=True, spent=()):
    j = sc.j
    U, G = sc.U, sc.G
    hit = hit or {}
    shield = shield or {}
    for s in j['sites']:
        sid = s['id']
        x, y = sc.A(sid)
        top = (x, y - 58)
        if s['state'] in ('DOWN',) and marks:
            down_mark(U, x, y - 56, seed=hash(sid) % 97)
        if s['state'] in ('TAKEN', 'INFECTED') and marks:
            taken_mark(U, x, y - 56, seed=hash(sid) % 89)
    if chips and guards is not None:
        for c in j['defense_cards']:
            x, y = sc.A(c['site'])
            chip(U, x - 36, y - 16, c['verb'], c['type'], spent=c['site'] in spent)


def draw_tags(sc, hit, shield, offs=None, only=None):
    U, G = sc.U, sc.G
    offs = offs or {}
    for sid, s in sc.sites.items():
        if only is not None and sid not in only:
            continue
        x, y = sc.A(sid)
        dx, dy = offs.get(sid, (0, 0))
        top = (x + dx, y - 98 + dy)
        h = hit.get(sid, 0)
        sh = shield.get(sid, 0)
        if h > 0:
            col, num, pct = TIER['LOST'], int(round(h * 100)), h
        elif sh > 0:
            col, num, pct = TIER['HOLDS'], int(round(sh * 100)), 1.0
        else:
            col, num, pct = TIER['UNTOUCHED'], None, None
        if num is None:
            U.poly(hexg(x, y - 50, 5, math.pi / 6), outline=col, w=1.4, glow=0.4)
            continue
        tag_tether(G, (x, y - 70), (top[0], top[1] + 16), col)
        threat_tag(U, top[0], top[1], col, num=num, exploit=s['exploit'], pct=pct)


def home_dial(sc, n_pips=12, tiers=None, hp=44, hpmax=50, pulse=0.0):
    """Radial threat dial at HOME: a ring of outcome pips (one per forecast outcome) in the tier colours."""
    U, G = sc.U, sc.G
    x, y = T(sc.anch['home'])
    tiers = tiers or ['LOST'] * n_pips
    R = 92
    for k, tr in enumerate(tiers):
        a0 = -90 + k * 360 / n_pips + 2
        col = TIER[tr]
        U.arc(x, y, R, R * ISO, a0, a0 + 360 / n_pips - 4, col, w=7, glow=0.9, step=3)
    U.arc(x, y, R + 9, (R + 9) * ISO, -92, -88, WHITE, w=3)
    # outer ticks
    for k in range(n_pips):
        a = math.radians(-90 + k * 360 / n_pips)
        U.line([(x + math.cos(a) * (R + 6), y + math.sin(a) * (R + 6) * ISO), (x + math.cos(a) * (R + 14), y + math.sin(a) * (R + 14) * ISO)], (190, 205, 225), 1.2, 160)


def grid_scene(j, taken_extra=(), **kw):
    sc = Scene(j)
    return sc


# ================================================================== FRAMES
def f_decay():
    j = load_coords('decay', 'decay')
    sc = Scene(j)
    tk = ['t1_a', 't1_b']
    img = base(sc, taken=tk, grow=1.0, radius=215, city=CITY_DECAY)
    draw_network(sc)
    draw_sites(sc)
    draw_hq(sc, pulse=0.6)
    draw_home(sc, 44, 50)
    # the tide: a Solace ring creeping out of the HQ (hot plum hairline, dashed) toward the Sites
    hx_, hy_ = T(sc.anch['hq'])
    iso_ring(sc.G, hx_, hy_, 330, VEIN, w=2.2, glow=0.8, dash=(10, 4))
    iso_ring(sc.G, hx_, hy_, 560, VEIN, w=1.4, a=160, glow=0.4, dash=(8, 6))
    U = sc.U
    for k, sid in enumerate(tk):
        x, y = sc.A(sid)
        down_mark(U, x, y - 56, seed=k + 3)                 # the old DOWN slash ...
        taken_mark(U, x, y - 56, seed=k * 5 + 9)            # ... crossed out into TAKEN
    # INFECTED cards flying from the two TAKEN Sites to the deck strip (binary bits on the arc)
    tgt = [(366 + 22 + 8 * 20 + 20 * i, 52) for i in range(3)]
    for i, sid in enumerate(tk):
        x, y = sc.A(sid)
        sx, sy = x, y - 72
        tx, ty = tgt[i + 1]
        for t in np.linspace(0, 0.8, 9):
            px = sx + (tx - sx) * t
            py = sy + (ty - sy) * t - math.sin(t * math.pi) * 70
            U.text((px, py), '01'[(int(t * 20) + i) % 2], font('mono', 15 - t * 4), (255, 255, 255) if t < .3 else VEIN, glow=.8, stroke=.8)
        t = 0.6
        px = sx + (tx - sx) * t
        py = sy + (ty - sy) * t - math.sin(t * math.pi) * 70
        U.poly(chamfer(px - 18, py - 24, 36, 48, 7), fill=(44, 12, 50), outline=VEIN, w=2.5, glow=1.2)
        U.line([(px - 9, py - 12), (px + 9, py + 12)], VEIN, 3)
        U.line([(px + 9, py - 12), (px - 9, py + 12)], VEIN, 3)
    hud(sc, 44, 50, 80, 8, 3, 9, raid=1, queued=0, flash_inf=0.8)
    finish_save(sc, img, 'decay')


def sweep_draw_frame():
    pass


def f_draw():
    j = load_coords('default', 'draw')
    jf = load_coords('default', 'forecast')            # the draw plate has no beams yet; the threats come from the same raid's forecast
    sc = Scene(j)
    ang = 0.55
    u0 = 1010
    band, behind, edge = sweep_field(u0, 80, ang)
    sw = np.clip(behind * 1.0 + band * 1.4, 0, 2)
    img = base(sc, sweep=sw, wire=0.75)
    img = img + (band * 0.20 + edge * 0.9)[..., None] * np.array(CYAN, np.float32) / 255.0
    draw_network(sc)
    draw_sites(sc, dim=0.8)
    draw_hq(sc, pulse=0.3)
    draw_home(sc)
    U = sc.U
    ux = lambda q: q[0] * math.cos(ang) + q[1] * math.sin(ang)
    for b in ordered(jf):
        st = beam_state(b, alpha=0.95, bead_gap=40, sealed=(b['role'] == 'cand'), nolabel=True, clip=lambda q: ux(q) > u0 - 20)
        if b['role'] == 'hunter':
            st['alpha'] = 0.0
            continue
        draw_beam(sc, b, st)
    for s_ in j['sites']:
        if s_['state'] == 'DOWN':
            x, y = sc.A(s_['id'])
            down_mark(U, x, y - 56)
    hand_cards = [('GUARD', 'N', ''), ('SHIFT', 'E', ''), ('JAM', 'N', ''), ('GUARD', 'D', ''), ('GUARD', 'E', '')]
    hand(sc, hand_cards, y=1010)
    for i, (px, py, a) in enumerate(((760, 430, -14), (560, 250, -24))):
        for t in np.linspace(0.1, 0.9, 9):
            qx = 380 + (px - 380) * t
            qy = 60 + (py - 60) * t
            U.text((qx, qy), '01'[i % 2 if int(t * 10) % 2 else 1 - i % 2], font('mono', 13), (255, 255, 255) if t > .6 else CYAN, glow=.7)
        card(U, px, py, ['GUARD', 'SHIFT'][i], ['D', 'E'][i], ang=a, w=60, h=84)
    hud(sc, 44, 50, 80, 8, 0, 9, raid=1, queued=1)
    finish_save(sc, img, 'draw')


def f_plan(words=True, name='plan'):
    j = load_coords('default', 'plan_placed')
    sc = Scene(j)
    img = base(sc, wire=0.6)
    draw_network(sc)
    draw_sites(sc, dim=0.9)
    draw_hq(sc)
    draw_home(sc)
    U, G = sc.U, sc.G
    picked_t = 'D'
    d_paths = {}
    for b in ordered(j):
        match = b['type'] == picked_t and b['role'] != 'hunter'
        st = beam_state(b, alpha=1.0 if match else 0.28, bead_gap=40, sealed=(b['role'] == 'cand'))
        if b['role'] == 'hunter':
            st['alpha'] = 0.3
        p = draw_beam(sc, b, st)
        if match:
            d_paths[b['name']] = b
    # sockets eligible for the lifted D card: pulse rings in D hue; the hovered one carries the lime focus halo
    elig = set()
    for b in d_paths.values():
        for sid in b['site_path'][1:-1]:
            elig.add(sid)
    for sid in elig:
        x, y = sc.A(sid)
        iso_ring(G, x, y, 24, BEAM['D'], w=2, glow=0.9)
        iso_ring(G, x, y, 34, BEAM['D'], w=1.2, a=150, glow=0.5)
    fx, fy = sc.A('t1_c')
    iso_ring(G, fx, fy, 30, LIME, w=3.5, glow=1.2)
    iso_ring(G, fx, fy, 42, LIME, w=1.6, a=200, glow=0.7)
    # placed chips
    for c in j['defense_cards']:
        x, y = sc.A(c['site'])
        chip(U, x - 36, y - 16, c['verb'], c['type'])
    # ghost D guard hovering above the focus socket, with its drop line
    gx, gy = fx, fy - 44
    U.line([(gx, gy + 14), (fx, fy - 6)], LIME, 1.6, 200, glow=0.6)
    chip(U, gx, gy, 'GUARD', 'D', accent=LIME, scale=1.1)
    # the lifted card in hand, a pencil-yellow drag line to the ghost
    cards = [('GUARD', 'N', 'dim'), ('SHIFT', 'E', 'dim'), ('JAM', 'N', ''), ('GUARD', 'D', ''), ('SHIFT', 'E', 'dim'), ('GUARD', 'E', ''), ('GUARD', 'N', '')]
    hand(sc, cards, y=1000, picked=3)
    hxx = W / 2 + 90
    pts = [(hxx, 930), (hxx - 120, 800), (fx + 40, fy + 80), (gx, gy + 28)]
    cur = []
    for t in np.linspace(0, 1, 30):
        a = (1 - t) ** 3 * np.array(pts[0]) + 3 * (1 - t) ** 2 * t * np.array(pts[1]) + 3 * (1 - t) * t * t * np.array(pts[2]) + t ** 3 * np.array(pts[3])
        cur.append((float(a[0]), float(a[1])))
    for k in range(0, len(cur) - 1, 2):
        U.line(cur[k:k + 2], PENCIL_YEL, 3.2, glow=0.5)
    hud(sc, 44, 50, 80, 8, 0, 9)
    finish_save(sc, img, name)


def f_forecast(words=True, name='forecast', scn='default'):
    j = load_coords(scn, 'forecast')
    sc = Scene(j)
    img = base(sc, taken=taken_ids(j) if scn != 'default' else [], wire=0.42)
    draw_network(sc)
    draw_sites(sc, dim=0.7)
    draw_hq(sc)
    draw_home(sc)
    U, G = sc.U, sc.G
    for b in ordered(j):
        st = beam_state(b, alpha={'known': 0.8, 'cand': 0.6, 'hunter': 0.6}[b['role']], bead_gap=46, sealed=(b['role'] == 'cand'), nolabel=True)
        draw_beam(sc, b, st)
    hit, shield, guards = forecast_stats(j)
    for s in j['sites']:
        if s['state'] == 'DOWN':
            x, y = sc.A(s['id'])
            down_mark(U, x, y - 56, seed=4)
    offs = {'t1_a': (-48, -16), 't1_b': (50, -32), 't1_c': (-72, 6), 't2_breach': (0, -4), 't2_virus': (0, 6), 't3_b': (14, -8), 't3_c': (22, 14), 't3_core': (-12, -4), 't2_intel': (-8, -10)}
    draw_tags(sc, hit, shield, offs)
    for c in j['defense_cards']:
        x, y = sc.A(c['site'])
        chip(U, x - 36, y - 16, c['verb'], c['type'])
        # a guard that stops nothing on this site: the chip's shape does not match any beam shape here -> pencil cross
        if c['verb'] == 'GUARD' and not any(b['type'] == c['type'] and c['site'] in b['site_path'] for b in j['beams']):
            grease(U, [(x - 54, y - 30), (x - 18, y - 2)], PENCIL_RED, w=4.5, seed=21)
            grease(U, [(x - 18, y - 30), (x - 54, y - 2)], PENCIL_RED, w=4.5, seed=22)
    home_dial(sc, 12, ['LOST'] * 12)
    hand(sc, [('GUARD', 'N', ''), ('SHIFT', 'E', ''), ('JAM', 'N', ''), ('GUARD', 'D', ''), ('SHIFT', 'E', ''), ('GUARD', 'E', ''), ('GUARD', 'N', '')], y=1010)
    hud(sc, 44, 50, 80, 8, 0, 9)
    finish_save(sc, img, name)


def f_response():
    j = load_coords('default', 'response_picked')
    sc = Scene(j)
    img = base(sc, wire=0.55)
    draw_network(sc)
    draw_sites(sc, dim=0.7)
    draw_hq(sc)
    draw_home(sc)
    U, G = sc.U, sc.G
    for b in ordered(j):
        st = beam_state(b, alpha={'known': 0.7, 'cand': 0.45, 'hunter': 0.4}[b['role']], bead_gap=50, sealed=(b['role'] == 'cand'), nolabel=True)
        draw_beam(sc, b, st)
    hit, shield, guards = forecast_stats(j)
    fx, fy = sc.A('t1_c')
    # chosen DEPLOY(D) previews its outcome on the map: D beams stop at t1_c in a hex shield; tags recomputed
    draw_tags(sc, hit, shield, {'t1_a': (-48, -16), 't1_b': (50, -32), 't1_c': (-72, 6)}, only={'t1_a', 't1_b', 't2_breach', 't2_virus', 't3_b', 't3_c'})
    for c in j['defense_cards']:
        x, y = sc.A(c['site'])
        chip(U, x - 36, y - 16, c['verb'], c['type'])
    iso_ring(G, fx, fy, 30, LIME, w=3.5, glow=1.2)
    # DEPLOY fan at the Site: D / N / E drones, each with the tier it would give
    fan = [('D', -92, TIER['HOLDS']), ('N', 0, TIER['LOST']), ('E', 92, TIER['LOST'])]
    for t, dx, tc in fan:
        px, py = fx + dx, fy - 150 + abs(dx) * 0.28
        sel = t == 'D'
        U.line([(fx, fy - 8), (px, py + 26)], LIME if sel else (120, 140, 170), 1.6 if sel else 1.0, 200)
        U.poly(chamfer(px - 34, py - 30, 68, 60, 9), fill=(4, 12, 30), outline=LIME if sel else CYAN, w=3 if sel else 1.8, glow=1.0 if sel else 0.4, a=245)
        type_glyph(U, t, px, py - 5, 12)
        U.poly([(px - 6, py + 14), (px + 6, py + 14), (px, py + 22)], fill=tc)   # drop arrow in the outcome tier colour
        U.line([(px - 26, py + 27), (px + 26, py + 27)], tc, 3.4, glow=0.7)
    U.text((fx, fy - 205), 'DEPLOY', font('mono', 17), (210, 230, 245), a=230, glow=0.2)
    # HOLD / MOVE sockets by HOME
    hx_, hy_ = T(sc.anch['home'])
    for k, (verb, dx) in enumerate((('HOLD', -90), ('MOVE', 90))):
        px, py = hx_ + dx, hy_ - 150 - (0 if k == 0 else 12)
        U.poly(chamfer(px - 34, py - 30, 68, 60, 9), fill=(4, 12, 30), outline=CYAN, w=1.8, glow=0.4, a=245)
        if verb == 'HOLD':
            U.line([(px - 7, py - 14), (px - 7, py + 6)], WHITE, 6)
            U.line([(px + 7, py - 14), (px + 7, py + 6)], WHITE, 6)
        else:
            verb_glyph(U, 'SHIFT', px, py - 4, 15, WHITE)
        U.line([(px - 26, py + 24), (px + 26, py + 24)], TIER['LOST'], 3.4, glow=0.7)
        U.text((px, py - 42), verb, font('mono', 15), (210, 230, 245), a=230)
    home_dial(sc, 12, ['HOLDS'] * 4 + ['LOST'] * 8)
    hand(sc, [('GUARD', 'N', 'dim'), ('SHIFT', 'E', 'dim'), ('JAM', 'N', 'dim'), ('GUARD', 'D', 'dim'), ('SHIFT', 'E', 'dim'), ('GUARD', 'E', 'dim'), ('GUARD', 'N', 'dim')], y=1030, dim_all=True)
    hud(sc, 44, 50, 80, 8, 0, 9)
    finish_save(sc, img, 'response')


def _fired_beam(sc, b, until_site, alpha=1.0, hot=True):
    p = sc.beam_path(b)
    sp = b['site_path']
    # arc-length fraction at which the beam reaches until_site (nearest path point to that site's anchor)
    tx, ty = sc.A(until_site) if until_site in sc.anch else T(sc.anch['home'])
    bestd, bests = 1e9, 0
    acc = 0
    for (a, c) in zip(p, p[1:]):
        for t in np.linspace(0, 1, 12):
            q = (a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
            d = math.dist(q, (tx, ty - 6))
            if d < bestd:
                bestd, bests = d, acc + math.dist(a, c) * t
        acc += math.dist(a, c)
    frac = bests / plen(p)
    st = beam_state(b, prog=frac, alpha=alpha, hot=hot, bead_gap=44)
    draw_beam(sc, b, st)
    return sample(p, bests)


def f_playout_impact():
    j = load_coords('default', 'playout_beam1_stage1')
    sc = Scene(j)
    img = base(sc, wire=0.65, bright=1.02)
    draw_network(sc)
    draw_sites(sc, dim=0.8)
    draw_hq(sc, pulse=0.2)
    draw_home(sc)
    U, G = sc.U, sc.G
    spent = {'known0': 0.22}
    cur = None
    for b in ordered(j):
        if b['name'] == 'known0':
            _fired_beam(sc, b, 't1_c', alpha=0.28, hot=False)
        elif b['name'] == 'known1':
            cur = b
        elif b['role'] == 'cand':
            draw_beam(sc, b, beam_state(b, alpha=0.22, bead_gap=60, sealed=True, nolabel=True))
    # K2 reaches the D guard on t1_c: hex shield flash, the packet crumbles into mint bits
    q, ang = _fired_beam(sc, cur, 't1_c', alpha=1.0)
    fx, fy = sc.A('t1_c')
    hex_shield(U, G, fx, fy - 50, 48, TIER['UNTOUCHED'])
    bits(U, fx - 70, fy - 40, BEAM['D'], n=60, spread=150, seed=4)
    chip(U, fx - 36, fy - 16, 'GUARD', 'D')
    # earlier in the same raid: t1_b took the hit (D hue burst fading, red slash)
    bx, by = sc.A('t1_b')
    impact_flash(G, bx, by - 6, BEAM['D'], r=46)
    bits(U, bx, by - 50, BEAM['D'], n=60, spread=130, seed=7)
    down_mark(U, bx, by - 56, seed=5)
    ax, ay = sc.A('t1_a')
    down_mark(U, ax, ay - 56, seed=4)
    # the guards that did not fire this beat stay quiet
    for c in j['defense_cards']:
        if c['site'] != 't1_c':
            x, y = sc.A(c['site'])
            chip(U, x - 36, y - 16, c['verb'], c['type'], spent=True)
    # HOME dial: pip counter shows 1 shield held (teal)
    home_dial(sc, 12, ['HOLDS'] * 2 + ['LOST'] * 10)
    hud(sc, 44, 50, 80, 8, 0, 9)
    finish_save(sc, img, 'playout_impact')


def f_playout_home():
    j = load_coords('lost', 'playout_beam0_stage1')
    sc = Scene(j)
    tk = [s['id'] for s in j['sites'] if s['state'] in ('INFECTED', 'TAKEN')]
    img = base(sc, taken=tk, grow=0.62, wire=0.6, radius=120)
    draw_network(sc)
    draw_sites(sc, dim=0.7)
    draw_hq(sc, pulse=0.1)
    draw_home(sc, 38, 50, hit=0.9)
    U, G = sc.U, sc.G
    b = [b for b in j['beams'] if b['name'] == 'known0'][0]
    p = sc.beam_path(b)
    st = beam_state(b, prog=0.985, alpha=1.0, hot=False, bead_gap=44)
    draw_beam(sc, b, st)
    hx_, hy_ = T(sc.anch['home'])
    impact_flash(G, hx_, hy_ - 10, BEAM['E'], r=70)
    G.ellipse(hx_, hy_ - 20, 120, 80, outline=TIER['DAMAGED'], w=3, glow=1.0)
    bits(U, hx_, hy_ - 60, BEAM['E'], n=90, spread=190, seed=9, white=0.4)
    # HP ring: segments blown off (shards), the orange 'DAMAGED' stamp number
    U.text((hx_ + 4, hy_ - 150), '-6', font('anton', 60), TIER['DAMAGED'], glow=0.8, stroke=3)
    for k in range(3):
        a = math.radians(-60 + k * 50)
        U.poly(hexg(hx_ + math.cos(a) * 120, hy_ + math.sin(a) * 120 * ISO - 20, 6, 0.3 * k), fill=TIER['DAMAGED'])
    for sid in tk:
        x, y = sc.A(sid)
        taken_mark(U, x, y - 56, seed=hash(sid) % 40)
    cx, cy = sc.A('t1_c')
    down_mark(U, cx, cy - 56, seed=3)
    hud(sc, 38, 50, 80, 8, 7, 9, hurt=True)
    # screen-edge hit flash
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - hx_) / 1100, (yy - hy_) / 800)
    img = img + (np.clip(r - .45, 0, 1) ** 2 * 0.35)[..., None] * np.array(TIER["DAMAGED"], np.float32) / 255.0 * 0.30
    finish_save(sc, img, 'playout_home')


def f_aftermath():
    j = load_coords('default', 'aftermath')
    sc = Scene(j)
    downs = [s['id'] for s in j['sites'] if s['state'] == 'DOWN']
    img = base(sc, wire=0.5)
    draw_network(sc)
    draw_sites(sc, dim=0.6)
    draw_hq(sc)
    draw_home(sc, 44, 50)
    U, G = sc.U, sc.G
    for b in ordered(j):
        if b['role'] == 'hunter':
            continue
        draw_beam(sc, b, beam_state(b, alpha=0.2, bead_gap=70, sealed=False, nolabel=True))
    for sid in downs:
        x, y = sc.A(sid)
        down_mark(U, x, y - 56, seed=hash(sid) % 50)
        site_glyph(U, x, y - 56, 11.5, TIER['LOST'], w=2.4, glow=1.0)
        # DECAY: red dashed pencil front forecast around the DOWN Site (it is TAKEN if still DOWN next raid)
        iso_ring(G, x, y, 52, PENCIL_RED, w=3, glow=0.5, dash=(14, 6))
        # plum seep at the pad (the Bloom waiting)
        G.ellipse(x, y, 20, 13, outline=VEIN, w=1.6, glow=0.8)
        # clock ring
        U.arc(x + 30, y - 84, 9, 9, -90, 90, VEIN, w=3)
        U.ellipse(x + 30, y - 84, 9, 9, outline=(200, 190, 210), w=1.4)
    for c in j['defense_cards']:
        x, y = sc.A(c['site'])
        chip(U, x - 36, y - 16, c['verb'], c['type'], spent=True)
    # verdict: HOLDS (teal stamp), slammed on HOME's lot
    hx_, hy_ = T(sc.anch['home'])
    col = TIER['HOLDS']
    sx, sy = hx_ + 330, hy_ - 190
    ang = math.radians(-9)
    def R(px, py): return (sx + px * math.cos(ang) - py * math.sin(ang), sy + px * math.sin(ang) + py * math.cos(ang))
    box = [R(-150, -52), R(150, -52), R(150, 52), R(-150, 52)]
    U.poly([(x + 3, y + 5) for x, y in box], fill=(0, 0, 0), a=120)
    U.poly(box, fill=(6, 40, 40), outline=col, w=5, glow=0.8, a=235)
    box2 = [R(-140, -43), R(140, -43), R(140, 43), R(-140, 43)]
    U.poly(box2, outline=col, w=1.6)
    U.poly(shield_pts(*R(-95, 0), 24), fill=col)
    for k, ch in enumerate('HOLDS'):
        px, py = R(-52 + k * 31, 3)
        U.text((px, py), ch, font('anton', 52), col, glow=0.5)
    hud(sc, 44, 50, 87, 8, 0, 9, raid=0, queued=0)
    hand(sc, [('GUARD', 'N', 'dim'), ('SHIFT', 'E', 'dim'), ('JAM', 'N', 'dim'), ('GUARD', 'D', 'dim'), ('SHIFT', 'E', 'dim'), ('GUARD', 'E', 'dim'), ('GUARD', 'N', 'dim')], y=1040, dim_all=True)
    finish_save(sc, img, 'aftermath')


def wrench(L, x, y, r, col):
    L.line([(x - r * .8, y + r * .8), (x + r * .35, y - r * .35)], col, r * .5)
    L.ellipse(x + r * .5, y - r * .5, r * .55, r * .55, outline=col, w=r * .38)


def cost(U, x, y, n, col=(255, 210, 90)):
    U.poly([(x - 8, y - 6), (x + 2, y - 6), (x + 2, y + 6), (x - 8, y + 6)], outline=col, w=1.6)
    U.line([(x - 8, y), (x + 2, y)], col, 1.2)
    U.text((x + 16, y + 1), str(n), font('mono', 16), (240, 240, 250))


def f_hq_step():
    j = load_coords('default', 'hq_step')
    sc = Scene(j)
    downs = [s['id'] for s in j['sites'] if s['state'] == 'DOWN']
    img = base(sc, wire=0.5, bright=0.95)
    draw_network(sc)
    draw_sites(sc, dim=0.6)
    draw_hq(sc)
    draw_home(sc, 44, 50)
    U, G = sc.U, sc.G
    hx_, hy_ = T(sc.anch['home'])
    # the HOME building opens action sockets: four slots on an iso ring around it, cost in Schematics beside each
    acts = [('PATCH', -150, -60, True, 6), ('COOL', -60, -150, True, 25), ('CLEAN', 140, -60, False, 10), ('INSTALL', 50, -150, False, 20)]
    iso_ring(G, hx_, hy_, 150, PENCIL_YEL, w=1.4, a=160, glow=0.4, dash=(8, 6))
    for name, dx, dy, on, c in acts:
        px, py = hx_ + dx + 40, hy_ + dy * 0.9 - 40
        col = CYAN if on else (90, 100, 120)
        U.line([(hx_, hy_ - 30), (px, py + 26)], col, 1.2, 170 if on else 60, glow=0.3 if on else 0)
        U.poly(chamfer(px - 36, py - 28, 72, 56, 9), fill=(4, 12, 30), outline=col, w=2.2 if on else 1.4, glow=0.9 if on else 0, a=245)
        gc = WHITE if on else (95, 105, 125)
        if name == 'PATCH':
            house(U, px, py - 4, 13, gc)
            U.line([(px + 12, py - 20), (px + 12, py - 8)], TIER['HOLDS'], 3.4)
            U.line([(px + 6, py - 14), (px + 18, py - 14)], TIER['HOLDS'], 3.4)
        elif name == 'COOL':
            flame(U, px, py - 4, 11, gc if not on else (255, 150, 60))
            U.poly([(px + 14, py - 8), (px + 24, py - 8), (px + 19, py + 2)], fill=TIER['UNTOUCHED'])
        elif name == 'CLEAN':
            U.poly(chamfer(px - 9, py - 15, 18, 24, 4), outline=(120, 70, 120), w=2)
            U.line([(px - 5, py - 9), (px + 5, py + 4)], (120, 70, 120), 1.8)
        else:
            U.poly(rot_sq(px, py - 4, 11, 0), outline=gc, w=2.4)
        cost(U, px - 18, py + 20, c, (255, 210, 90) if on else (110, 100, 80))
        if not on:
            U.line([(px - 36, py + 28), (px + 36, py - 28)], (95, 105, 125), 1.4, 150)
    # REPAIR sockets on the DOWN Sites: the wrench chip rises from each Site's pad
    for sid in downs:
        x, y = sc.A(sid)
        down_mark(U, x, y - 56, seed=hash(sid) % 50)
        px, py = x + (-34 if sid == 't1_a' else 34), y - 100
        U.line([(x, y - 44), (px, py + 26)], PENCIL_YEL, 1.4, 220, glow=0.5)
        U.poly(chamfer(px - 34, py - 26, 68, 52, 9), fill=(4, 12, 30), outline=PENCIL_YEL, w=2.2, glow=0.9, a=245)
        wrench(U, px - 2, py - 3, 12, WHITE)
        cost(U, px - 16, py + 17, 10, (255, 210, 90))
    for c in j['defense_cards']:
        x, y = sc.A(c['site'])
        chip(U, x - 36, y - 16, c['verb'], c['type'], spent=True)
    # DONE: a hex check at the HQ origin side? keep wordless: tick glyph chip bottom right
    U.poly(chamfer(1700, 930, 120, 70, 12), fill=(4, 24, 24), outline=TIER['HOLDS'], w=3, glow=1.0)
    U.line([(1737, 966), (1757, 984), (1790, 946)], TIER['HOLDS'], 8, glow=0.6)
    hud(sc, 44, 50, 87, 8, 0, 9, raid=0, queued=0)
    finish_save(sc, img, 'hq_step')


def f_city_lost():
    j = load_coords('lost', 'city_lost')
    sc = Scene(j)
    tk = [s['id'] for s in j['sites'] if s['state'] in ('INFECTED', 'TAKEN')] + list(j['taken'])
    hx_, hy_ = T(sc.anch['home'])
    qx, qy = T(sc.anch['hq'])
    ex = [(hx_, hy_, 1.6), (qx - 120, qy + 40, 1.8), (960, 560, 2.8), (700, 640, 2.4), (1200, 520, 2.2)]
    img = base(sc, taken=tk, grow=2.0, wire=0.35, extra=ex, radius=170, bright=0.9, keep=0.42, vein=0.55)
    # desaturate the dead city further and push toward plum-black
    L = lum(img)[..., None]
    img = img * 0.8 + L * 0.2
    draw_network(sc, a=0.5)
    U, G = sc.U, sc.G
    for sid in tk:
        x, y = sc.A(sid)
        taken_mark(U, x, y - 56, seed=hash(sid) % 40, s=1.1)
    # the skull glyph, huge, over the territory, with a plum halo; the verdict word beneath it
    sx, sy = 960, 430
    G.ellipse(sx, sy, 190, 150, outline=VEIN, w=4, glow=1.0)
    G.ellipse(sx, sy, 150, 118, outline=HOT, w=2, glow=0.8)
    skull(U, sx, sy, 92, (250, 246, 252), eye=(40, 6, 36))
    for k, ch in enumerate('CITY LOST'):
        pass
    U.text((sx, sy + 190), 'CITY LOST', font('anton', 118), (255, 232, 246), glow=0.9, stroke=5, stroke_col=(40, 6, 36))
    hud(sc, 44, 50, 80, 8, 11, 9, raid=0, queued=0, flash_inf=0.6, hurt=False)
    finish_save(sc, img, 'city_lost')


def f_all_panels_removed():
    """Forecast beat with every word removed: marks, glyphs, numbers and the HUD counters only."""
    f_forecast(name='all_panels_removed')


FRAMES = {'decay': f_decay, 'draw': f_draw, 'plan': f_plan, 'forecast': f_forecast, 'response': f_response,
          'playout_impact': f_playout_impact, 'playout_home': f_playout_home, 'aftermath': f_aftermath,
          'hq_step': f_hq_step, 'city_lost': f_city_lost, 'all_panels_removed': f_all_panels_removed}

if __name__ == '__main__':
    todo = sys.argv[1:] or list(FRAMES)
    for n in todo:
        print('build', n, flush=True)
        FRAMES[n]()
