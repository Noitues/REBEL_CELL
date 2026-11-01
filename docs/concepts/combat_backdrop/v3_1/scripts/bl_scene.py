"""Cutaway backdrop scene. blender -b --factory-startup -P bl_scene.py -- <room_type> <seed> <mode main|refl|mask> <out.png> [samples] [cam_seed]
One street slice (3 floors of lobby + a cut-open room floor on top), neighbours, towers, signs, wet street.
Everything is flat emission with per-face toon bands (kit_lib). Ink = Freestyle on layer 'ink' only."""
import bpy, sys, os, math, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit_lib as K
import kit_gen

A = sys.argv[sys.argv.index('--') + 1:]
ROOM, SEED, MODE, OUT = A[0], int(A[1]), A[2], A[3]
SAMPLES = int(A[4]) if len(A) > 4 else 12
CAMS = int(A[5]) if len(A) > 5 else 3
P = K.PAL
H = K.hexc
W, D = kit_gen.W, kit_gen.D
SIGNDIR = 'D:/rc_scratch/cutaway_kit_v3_1/signs/'
PX = 50.0                        # px per world unit (ortho)
TARGET_PX = (1500.0, 612.0)      # where the room centre lands in the 1920x1080 frame
Z_LOBBY = 0.25
GROUND = (ROOM == 'shop')         # v3: the shop room sits at street level (no lobby below, front opens onto the street)
Z_ROOM = 0.62 if GROUND else 4.4   # room floor z

G = K.reset()
G.layers['ground'] = ([], [], [])
G.mirror = (MODE == 'refl')
G.haze_k = 1.0
RN = random.Random(CAMS * 31 + 5)
SIGNS = []                       # (name, corners[4 Vector], )

BODIES = ['#4b2f7e', '#6a2f80', '#2f3f80', '#2d5c70', '#5a3a8a', '#7b3070', '#3a3f78', '#34506e']
RIMS = ['#96FF46', '#96FF46', '#3FE6FF', '#FF4696', '#FFB938', '#96FF46', '#B07AFF']
WINC = ['#FFC878', '#7BE8FF', '#FF9AD0', '#C8FF8A', '#FFE7B8', '#9FD8FF']


def sign(name, face, x, y, z, w, h):
    """face: 'front' (-y plane, spans x..x+w) or 'right' (+x plane, spans y..y+w)"""
    if face == 'front':
        c = [Vector((x, y, z)), Vector((x + w, y, z)), Vector((x + w, y, z + h)), Vector((x, y, z + h))]
    else:
        c = [Vector((x, y, z)), Vector((x, y + w, z)), Vector((x, y + w, z + h)), Vector((x, y, z + h))]
    SIGNS.append((name, c))
    # neon frame glow strips are baked in the texture; add a thin dark backing box
    if face == 'front':
        K.box('fx', x - 0.06, y + 0.02, z - 0.06, w + 0.12, 0.05, h + 0.12, P['dark'])
    else:
        K.box('fx', x - 0.07, y - 0.06, z - 0.06, 0.05, w + 0.12, h + 0.12, P['dark'])    # v2 put this backing IN FRONT of the plane (hides solace_v); fixed for the ground shop only to keep v2 renders comparable


def tower(x0, x1, y0, y1, h, seed, front_shop=False, rim=None, depth_cue=0.0):
    r = random.Random(seed + SEED * 131)
    body = H(r.choice(BODIES))
    bodyd = tuple(b * 0.8 for b in body)
    rimc = H(rim or r.choice(RIMS))
    # setbacks: main + optional upper tier
    tiers = [(x0, x1, y0, y1, 0, h)]
    if h > 14 and r.random() < 0.6:
        sh = h * r.uniform(0.55, 0.8)
        tiers = [(x0, x1, y0, y1, 0, sh), (x0 + 0.8, x1 - 0.8, y0 + 0.8, y1 - 0.8, sh, h)]
    for (a0, a1, b0, b1, z0, z1) in tiers:
        K.box('ink', a0, b0, z0, a1 - a0, b1 - b0, z1 - z0, body)
        # roof rim neon (front + right edges)
        K.box('fx', a0, b0 - 0.02, z1 - 0.02, a1 - a0, 0.16, 0.14, rimc, emit=True)
        K.box('fx', a1 - 0.14, b0, z1 - 0.02, 0.16, b1 - b0, 0.14, rimc, emit=True)
        # windows on front (-y) and right (+x) faces
        # panel strips (vertical tone changes) so big faces are not flat
        px = a0
        while px < a1 - 0.5:
            pw = r.choice([1.2, 1.8, 2.4])
            if r.random() < 0.5:
                K.box('fx', px, b0 - 0.008, z0 + 0.4, min(pw, a1 - px), 0.015, (z1 - z0) - 0.8, bodyd, emit=True, k=0.8 + 0.25 * r.random())
            px += pw + r.choice([0.0, 0.6])
        py = b0
        while py < b1 - 0.5:
            pw = r.choice([1.2, 1.8, 2.4])
            if r.random() < 0.5:
                K.box('fx', a1 - 0.0, py, z0 + 0.4, 0.015, min(pw, b1 - py), (z1 - z0) - 0.8, bodyd, emit=True, k=0.7 + 0.2 * r.random())
            py += pw + r.choice([0.0, 0.6])
        # windows: small, dense, random lit
        zf = z0 + (3.6 if (front_shop and z0 == 0) else 1.0)
        while zf + 0.5 < z1 - 0.5:
            x = a0 + 0.5
            while x + 0.55 < a1 - 0.4:
                u = r.random()
                if u < 0.30:
                    K.box('fx', x, b0 - 0.02, zf, 0.55, 0.02, 0.38, H(r.choice(WINC)), emit=True, k=1.0)
                elif u < 0.6:
                    K.box('fx', x, b0 - 0.02, zf, 0.55, 0.02, 0.38, bodyd, emit=True, k=1.25)
                x += 0.95
            y = b0 + 0.5
            while y + 0.55 < b1 - 0.4:
                u = r.random()
                if u < 0.24:
                    K.box('fx', a1 - 0.0, y, zf, 0.02, 0.55, 0.38, H(r.choice(WINC)), emit=True, k=0.9)
                elif u < 0.58:
                    K.box('fx', a1 - 0.0, y, zf, 0.02, 0.55, 0.38, bodyd, emit=True, k=1.15)
                y += 0.95
            zf += 1.05
        # horizontal ledge neon lines at random floors
        for k in range(int((z1 - z0) / 8)):
            if r.random() < 0.35:
                zl = z0 + 4 + k * 8
                K.box('fx', a0, b0 - 0.02, zl, a1 - a0, 0.03, 0.1, rimc, emit=True, k=0.8)
        # vertical corner strip on the front-right edge
        if r.random() < 0.5:
            K.box('fx', a1 - 0.1, b0 - 0.03, z0 + 1, 0.12, 0.05, (z1 - z0) - 2, rimc, emit=True, k=0.9)
    # rooftop clutter
    top = tiers[-1]
    for _ in range(r.randint(1, 3)):
        ux = r.uniform(top[0] + 0.6, top[1] - 2.0)
        vy = r.uniform(top[2] + 0.6, top[3] - 2.0)
        K.box('ink', ux, vy, top[5], r.uniform(0.8, 1.6), r.uniform(0.8, 1.4), r.uniform(0.5, 1.1), P['metal_d'])
    if r.random() < 0.5:
        mx = (top[0] + top[1]) / 2
        K.box('ink', mx - 0.06, (top[2] + top[3]) / 2, top[5], 0.12, 0.12, r.uniform(2.5, 5), P['metal_d'])
        K.box('fx', mx - 0.08, (top[2] + top[3]) / 2 - 0.02, top[5] + 4.5, 0.16, 0.16, 0.16, P['pink'], emit=True)


def shopfront(x0, x1, y0, seed, names=()):
    """street level strip: lit glass, awning, signs, on the -y face"""
    r = random.Random(seed + SEED * 131)
    x = x0 + 0.4
    i = 0
    while x + 2.4 < x1 - 0.3:
        w = r.choice([2.4, 3.0, 3.6])
        if x + w > x1 - 0.3:
            break
        col = H(r.choice(['#FFC878', '#7BE8FF', '#FF9AD0', '#C8FF8A']))
        K.box('fx', x, y0 - 0.02, 0.3, w, 0.03, 2.2, col, emit=True, k=0.8)
        K.box('fx', x, y0 - 0.05, 2.55, w, 0.5, 0.18, H(r.choice(RIMS)), emit=True, k=0.9)
        for q in range(int(w / 0.6)):
            K.box('fx', x + 0.15 + q * 0.6, y0 - 0.04, 0.9, 0.04, 0.04, 1.2, P['ink'], emit=True)
        if i < len(names):
            sign(names[i], 'front', x + 0.2, y0 - 0.1, 2.82, w - 0.4, 0.8)
        x += w + 0.35
        i += 1


def street():
    # ground tiles: road + sidewalk, banded neon pools
    lights = [(-26, -4, '#FF4696'), (-14, -3, '#3FE6FF'), (-5, -3.5, '#96FF46'), (4.5, -3, '#96FF46'), (14, -4, '#FFB938'), (24, -3, '#FF4696'), (34, -4, '#3FE6FF'),
              (9, -2.5, '#96FF46'), (-36, -4, '#FFB938')]
    for (lx, ly, c) in lights:
        G.lights.append(dict(p=Vector((lx, ly, 0)), col=H(c), r=9, zone=(-80, -30, -1, 90, 0.5, 0.5), k=1.0))
    T = 1.0
    for ix in range(-80, 60):
        for iy in range(-30, 0):
            x0, y0 = ix * T, iy * T
            side = y0 >= -2.0
            base = P['slab_d'] if side else P['dark']
            base = tuple(b * (1.05 if (ix + iy) % 2 else 0.93) for b in base)
            K.face('ground', [(x0, y0, 0), (x0 + T, y0, 0), (x0 + T, y0 + T, 0), (x0, y0 + T, 0)], base, (0, 0, 1), False)
    # curb line + lane dashes + neon traffic streaks (golden plate: orange/pink/white streaks on a wet road)
    K.box('fx', -70, -2.3, 0, 140, 0.18, 0.12, P['metal'])
    for i in range(-35, 30):
        K.box('fx', i * 4.0, -8.8, 0.01, 1.8, 0.12, 0.01, P['amber'], emit=True, k=0.7)
    rs = random.Random(5)
    for k in range(34):
        y = -rs.uniform(3.2, 15)
        x = rs.uniform(-60, 50)
        L = rs.uniform(4, 14)
        col = rs.choice([P['pink'], P['amber'], P['cyan'], P['white'], P['pink'], P['lime']])
        K.box('fx', x, y, 0.01, L, 0.12, 0.01, col, emit=True, k=0.9)
    # street lamps on the kerb
    for i in range(-9, 8):
        x = i * 8.0 + 2
        K.box('ink', x, -2.0, 0, 0.1, 0.1, 3.4, P['metal_d'])
        K.box('fx', x - 0.2, -2.1, 3.4, 0.5, 0.3, 0.1, rs_col(i), emit=True)


def rs_col(i):
    return (P['amber'], P['cyan'], P['pink'])[i % 3]


def build_city():
    # left, tall neighbours (behind the target on screen)
    shops = {
        -1: ['pharma_v'], }
    tower(-7.2, -0.8, 0, 7, 30, 101, True, '#96FF46')
    tower(-15, -7.8, 0, 7, 40, 102, True, '#3FE6FF')
    tower(-24, -15.8, 0, 7, 24, 103, True, '#FF4696')
    tower(-33, -24.8, 0, 7, 34, 104, True, '#96FF46')
    tower(-42, -33.8, 0, 7, 28, 105, True)
    tower(-52, -42.8, 0, 7, 36, 106, True)
    shopfront(-7.2, -0.8, 0, 1, ['bar_h', 'rx_h'])
    shopfront(-15, -7.8, 0, 2, ['noodle_h', 'data_h'])
    shopfront(-24, -15.8, 0, 3, ['tea_v'.replace('_v', '_h') if False else 'vita_h'])
    shopfront(-33, -24.8, 0, 4, ['karaoke_h', 'arcade_h'])
    shopfront(-42, -33.8, 0, 5, ['gene_h'])
    # right, low neighbours (nearer the camera: must stay below the room floor)
    for (a, b, hh, sd, nm) in ((10.2, 17.0, 3.6, 201, ['gene_h', 'bar_h']), (17.8, 26.0, 3.6, 202, ['karaoke_h']), (26.8, 36, 3.6, 203, ['vita_h']), (36.8, 46, 3.6, 204, [])):
        if GROUND and a < 18:          # ground-level shop: this neighbour becomes a low kiosk strip (<= 1.8 m) so it cannot hide the room
            K.box('ink', a, 0, 0, b - a, 7, 1.8, H('#2f3f80'))
            K.box('fx', a, -0.02, 1.78, b - a, 0.16, 0.14, H('#FFB938'), emit=True)
            K.box('fx', b - 0.14, 0, 1.78, 0.16, 7, 0.14, H('#FFB938'), emit=True)
            for q in range(3):
                K.box('fx', a + 0.6 + q * 2.1, -0.04, 0.4, 1.4, 0.04, 1.0, H(['#FFC878', '#7BE8FF', '#C8FF8A'][q]), emit=True, k=0.8)
            continue
        K.box('ink', a, 0, 0, b - a, 7, hh, H(['#6a2f80', '#2f3f80', '#7b3070', '#2d5c70'][sd % 4]))
        K.box('fx', a, -0.02, hh - 0.02, b - a, 0.16, 0.14, H(RIMS[sd % len(RIMS)]), emit=True)
        K.box('fx', b - 0.14, 0, hh - 0.02, 0.16, 7, 0.14, H(RIMS[sd % len(RIMS)]), emit=True)
        shopfront(a, b, 0, sd, nm)
        rr = random.Random(sd)
        for _ in range(3):
            K.box('ink', rr.uniform(a + 0.5, b - 2), rr.uniform(1, 5), hh, rr.uniform(0.8, 1.6), rr.uniform(0.8, 1.4), rr.uniform(0.5, 1.0), P['metal_d'])
        # right-facing window strip
        for q in range(3):
            K.box('fx', b - 0.0, 0.8 + q * 2.0, 1.0, 0.02, 1.2, 1.6, H(WINC[(q + sd) % len(WINC)]), emit=True, k=0.9)
    # tall towers behind: lots on a 6.5 grid, all of (x,y) with y>=8.2 within the visible (u,w) range
    rr = random.Random(77)
    n = 0
    for j in range(0, 12):
        for i in range(-30, 8):
            x0 = i * 7.0
            y0 = 8.2 + j * 7.4
            u = x0 + y0
            w = y0 - x0
            if not (-60 < u < 44):
                continue
            if x0 < -1 and y0 < 7.5:
                continue
            h = rr.uniform(12, 30) + j * 3.0 + rr.random() * 10
            tower(x0, x0 + 6.2, y0, y0 + 6.2, h, 300 + n, False)
            n += 1
    # left column rows (x<-52) already covered by i range; fill a back strip right of the target
    for j in range(0, 12):
        for i in range(0, 8):
            x0 = i * 7.0
            y0 = 8.2 + j * 7.4
            u = x0 + y0
            if u > 44:
                continue


def ground_room(spec_room, corp='lime'):
    """v3 shop: the room floor plate sits on the pavement, back + left walls, front and right open onto the street."""
    G.room_zone = None
    colr = {'lime': P['lime'], 'cyan': P['cyan'], 'pink': P['pink'], 'amber': P['amber'], 'violet': P['violet'], 'lime_p': P['lime_p']}[spec_room['light']]
    G.room_zone = (-0.4, -0.4, Z_ROOM, W + 0.4, D + 0.4, Z_ROOM + 3.4)
    G.amb = 0.8
    for l in spec_room['lights']:
        G.lights.append(dict(p=Vector((l['x'], l['y'], Z_ROOM + l['z'])), col=(P[l['col']] if 'col' in l else colr), r=l['r'], zone=G.room_zone, k=1.0))
    K.room_shell(W, D, Z_ROOM, spec_room, corp=corp)
    for p in spec_room['props']:
        K.place_prop(p['name'], p['x'], p['y'], p['rot'], Z_ROOM, kit_gen.CAT, seed=SEED * 3 + p['x'] * 5 + p['y'])
    decals(spec_room, colr)
    G.room_zone = None
    dp = spec_room['door']['pos']
    sx = 0.6 if dp >= 4 else 5.2
    sign('shop_h', 'front', sx, D - 0.12, Z_ROOM + 2.35, 3.2, 0.7)
    sign('shop_v', 'right', W + 2.5, -3.4, 0.7, 0.62, 2.5)      # blade sign out on the kerb, low enough (head 3.2 m) not to hide any floor cell
    for bx in (1.0, 4.5, 8.0):                       # bollards + A-frame on the pavement
        K.box('ink', bx, -1.0, 0, 0.18, 0.18, 0.8, P['metal_d'])
        K.box('fx', bx, -1.0, 0.8, 0.18, 0.18, 0.05, P['amber'], emit=True)
    K.box('ink', 2.4, -1.6, 0, 0.8, 0.1, 0.95, P['metal_dd'])
    K.box('fx', 2.45, -1.62, 0.1, 0.7, 0.03, 0.75, P['lime'], emit=True, k=0.8)


def decals(spec_room, colr):
    base = K.lerp3(P['teal'], colr, 0.35)
    for i, d in enumerate(spec_room.get('decals', [])):
        K.place_decal('puddle', d['x'], d['y'], d['s'], Z_ROOM, base, 0.85, seed=SEED * 11 + i)
    for cb in spec_room.get('cables', []):       # v3.1: floor cables that connect the hero / powered props
        K.draw_cable(cb['pts'], Z_ROOM + 0.02, P[cb['col']], 0.9)


def target_building(spec_room, spec_lobby, corp='lime'):
    if GROUND:
        return ground_room(spec_room, corp)
    # lobby floor + shell (3.8 clear), props
    G.room_zone = None
    zl = Z_LOBBY
    # the building body below the room slab: back/left/right walls
    TH = 0.3
    K.box('ink', -TH, -TH, 0, W + 2 * TH, D + 2 * TH, zl, P['slab'])                       # plinth
    for i in range(W):
        for j in range(D):
            a = P['floor_a'] if (i + j) % 2 == 0 else P['floor_b']
            K.quad_z('fx', zl + 0.012, i + 0.025, i + 0.975, j + 0.025, j + 0.975, a)
    hl = Z_ROOM - 0.6 - zl
    K.box('ink', -TH, D, zl, W + TH * 2, TH, hl, P['teal_d'])                                # back wall
    K.box('ink', -TH, 0, zl, TH, D, hl, P['teal_d'])                                         # left wall
    K.box('ink', W, 0, zl, TH, D + TH, hl, P['body'] if 'body' in P else P['teal_d'])        # right wall (exterior faces camera)
    # lobby wall dressing: wainscot + neon trims
    K.box('fx', -TH, D - 0.03, zl, W + TH, 0.04, 0.9, P['teal_dd'])
    K.box('fx', -TH, D - 0.04, zl + 0.9, W + TH, 0.05, 0.07, P[corp], emit=True)
    K.box('fx', -0.04, 0, zl, 0.04, D, 0.9, P['teal_dd'])
    K.box('fx', -0.04, 0, zl + 0.9, 0.05, D, 0.07, P[corp], emit=True)
    K.box('fx', -TH, D - 0.04, Z_ROOM - 0.6 - 0.25, W + TH, 0.05, 0.1, P[corp], emit=True)
    # back wall: big helix emblem panel, lit
    K.quad_y('fx', D - 0.05, 2.6, 6.4, zl + 1.2, zl + 3.2, H('#103a3a'), -1, True)
    for q in range(26):
        t = q / 25
        zz = zl + 1.5 + t * 1.5
        xx = 4.5 + 0.7 * math.sin(t * math.pi * 3)
        xx2 = 4.5 - 0.7 * math.sin(t * math.pi * 3)
        K.quad_y('fx', D - 0.06, xx - 0.07, xx + 0.07, zz, zz + 0.12, P['lime'], -1, True)
        K.quad_y('fx', D - 0.06, xx2 - 0.07, xx2 + 0.07, zz, zz + 0.12, P['cyan'], -1, True)
    # windows on the right wall (exterior)
    for q in range(3):
        K.box('fx', W + TH, 0.8 + q * 2.0, zl + 1.2, 0.02, 1.3, 1.6, P['lime_p'], emit=True, k=0.8)
        K.box('fx', W + TH + 0.0, 0.8 + q * 2.0 - 0.06, zl + 2.9, 0.04, 1.42, 0.1, P[corp], emit=True)
    # front pillars (open storefront)
    for px in (-0.15, 3.0, 6.0, 8.85):
        K.box('ink', px, -0.2, zl, 0.3, 0.3, hl, P['metal_d'])
        K.box('fx', px + 0.26, -0.21, zl, 0.04, 0.03, hl, P[corp], emit=True)
    # lobby lighting + props
    G.lights = [l for l in G.lights]
    lz = (-0.5, -0.5, zl, W + 0.5, D + 0.5, Z_ROOM - 0.6)
    for l in spec_lobby['lights']:
        G.lights.append(dict(p=Vector((l['x'], l['y'], zl + l['z'])), col=P['lime'], r=l['r'], zone=lz, k=0.9))
    G.room_zone = lz
    G.amb = 0.75
    for p in spec_lobby['props']:
        K.place_prop(p['name'], p['x'], p['y'], p['rot'], zl, kit_gen.CAT, seed=SEED + p['x'] * 7 + p['y'])
    # the cut-open room floor on top
    G.room_zone = (-0.4, -0.4, Z_ROOM, W + 0.4, D + 0.4, Z_ROOM + 3.4)
    G.amb = 0.8
    colr = {'lime': P['lime'], 'cyan': P['cyan'], 'pink': P['pink'], 'amber': P['amber'], 'violet': P['violet'], 'lime_p': P['lime_p']}[spec_room['light']]
    for l in spec_room['lights']:
        G.lights.append(dict(p=Vector((l['x'], l['y'], Z_ROOM + l['z'])), col=(P[l['col']] if 'col' in l else colr), r=l['r'], zone=G.room_zone, k=1.0))
    K.room_shell(W, D, Z_ROOM, spec_room, corp='lime')
    for p in spec_room['props']:
        K.place_prop(p['name'], p['x'], p['y'], p['rot'], Z_ROOM, kit_gen.CAT, seed=SEED * 3 + p['x'] * 5 + p['y'])
    decals(spec_room, colr)
    G.room_zone = None
    # signs on the building
    sign('solace_h', 'front', 1.0, -0.4, Z_ROOM - 0.6 - 1.05, 7.0, 0.85)
    sign('solace_v', 'right', W + 0.5, -0.9, 0.5 + 0.0, 1.0, 4.0)
    K.box('fx', W + 0.38, -0.95, 4.5, 0.06, 1.1, 0.1, P['lime'], emit=True)


# ------------------------------------------------------------------ mesh/material plumbing
def make_mat(name, kind='vc'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    if kind == 'vc':
        em = nt.nodes.new('ShaderNodeEmission')
        at = nt.nodes.new('ShaderNodeAttribute')
        at.attribute_name = 'Col'
        nt.links.new(at.outputs['Color'], em.inputs['Color'])
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    elif kind == 'hold':
        h = nt.nodes.new('ShaderNodeHoldout')
        nt.links.new(h.outputs['Holdout'], out.inputs['Surface'])
    elif kind == 'white':
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (1, 1, 1, 1)
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def mk_object(name, layer, mat, coll):
    verts, faces, cols = G.layers[layer]
    if not verts:
        return None
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(cols):
        ca.data[i].color = c
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def sign_objects(coll):
    for k, (name, c) in enumerate(SIGNS):
        if MODE == 'mask':
            continue
        verts = [(v.x, v.y, -v.z if G.mirror else v.z) for v in c]
        me = bpy.data.meshes.new('sign%d' % k)
        me.from_pydata(verts, [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new(name='UV')
        for li, loop in enumerate(me.loops):
            vi = loop.vertex_index
            uvc = [(0, 0), (1, 0), (1, 1), (0, 1)][vi]
            uv.data[li].uv = (uvc[0], (1 - uvc[1]) if G.mirror else uvc[1])
        m = bpy.data.materials.new('sm%d' % k)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Strength'].default_value = 1.0
        tx = nt.nodes.new('ShaderNodeTexImage')
        tx.image = bpy.data.images.load(SIGNDIR + name + '.png')
        tx.image.colorspace_settings.name = 'sRGB'
        tx.interpolation = 'Linear'
        nt.links.new(tx.outputs['Color'], em.inputs['Color'])
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
        me.materials.append(m)
        ob = bpy.data.objects.new('sign%d' % k, me)
        coll.objects.link(ob)


def main():
    spec_room = kit_gen.generate(ROOM, SEED)
    spec_lobby = kit_gen.generate('lobby', SEED + 100, v2=True)
    if MODE != 'refl':
        street()
    build_city()
    target_building(spec_room, spec_lobby)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    cy = scene.cycles
    cy.device = 'CPU'
    cy.samples = SAMPLES
    cy.use_denoising = False
    cy.max_bounces = 0
    cy.use_adaptive_sampling = False
    cy.filter_width = 1.0
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.display_settings.display_device = 'sRGB'
    scene.render.threads_mode = 'AUTO'

    root = scene.collection
    inkc = bpy.data.collections.new('inkc')
    root.children.link(inkc)
    if MODE == 'main':
        mat = make_mat('vc')
        mk_object('ink', 'ink', mat, inkc)
        mk_object('fx', 'fx', mat, root)
        mk_object('ground', 'ground', mat, root)
        sign_objects(root)
    elif MODE == 'refl':
        mat = make_mat('vc')
        mk_object('ink', 'ink', mat, root)
        mk_object('fx', 'fx', mat, root)
        sign_objects(root)
    else:
        hold = make_mat('hold', 'hold')
        white = make_mat('white', 'white')
        mk_object('ink', 'ink', hold, root)
        mk_object('fx', 'fx', hold, root)
        mk_object('ground', 'ground', white, root)

    # camera
    el = math.radians(35.264)
    cd = bpy.data.cameras.new('cam')
    cd.type = 'ORTHO'
    cd.ortho_scale = 1920.0 / PX
    cd.clip_start = 1
    cd.clip_end = 900
    cam = bpy.data.objects.new('cam', cd)
    root.objects.link(cam)
    scene.camera = cam
    tgt = Vector((W / 2, D / 2, Z_ROOM + 0.9))
    dirv = Vector((math.cos(el) * 0.70710678, -math.cos(el) * 0.70710678, math.sin(el)))
    cam.location = tgt + dirv * 300
    cam.rotation_euler = (-dirv).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    for _ in range(3):
        v = world_to_camera_view(scene, cam, tgt)
        tu, tv = TARGET_PX[0] / 1920.0, 1 - TARGET_PX[1] / 1080.0
        cd.shift_x -= (tu - v.x)
        cd.shift_y -= (tv - v.y) * (1080.0 / 1920.0)
        bpy.context.view_layer.update()

    if MODE == 'main':
        scene.render.use_freestyle = True
        scene.render.line_thickness_mode = 'ABSOLUTE'
        scene.render.line_thickness = 1.0
        vl = scene.view_layers[0]
        vl.use_freestyle = True
        fs = vl.freestyle_settings
        fs.crease_angle = math.radians(105)
        for ls in list(fs.linesets):
            fs.linesets.remove(ls)
        ls = fs.linesets.new('ink')
        ls.select_silhouette = True
        ls.select_border = True
        ls.select_crease = True
        ls.select_by_collection = True
        ls.collection = inkc
        st = ls.linestyle
        st.color = (0.03, 0.02, 0.08)
        st.thickness = 2.6
        st.use_chaining = True
        st.caps = 'ROUND'
    print('DBG objs', [(o.name, len(o.data.vertices) if o.type == 'MESH' else 0) for o in scene.objects], tuple(cam.location), cd.shift_x, cd.shift_y, tuple(world_to_camera_view(scene, cam, tgt)))
    scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print('RENDERED', OUT, 'prop count', len(spec_room['props']), spec_room['rules'])


main()
