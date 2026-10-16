"""Legend panel + composition for the plan maps."""
import math
import random

from PIL import Image

from canvas import Canvas
from citymap import COL, INDUSTRY, PARK, PARK_DARK, ROAD_CASING, ROAD_FILL, SLUM, TEXT, tint
from geom import circle_pts, mix, rect_pts

PW, PH = 640, 2000
BG = (11, 14, 21)
DIM = (150, 160, 178)

DISTRICTS = [
    ('centre', 'OLD CITY  /  THE REBEL CELL', 'The original port town. Organic core, sprawl, undercity.'),
    ('halcyon', 'HALCYON', 'Surveillance. Pyramid HQ "The Panopticon".'),
    ('solace', 'SOLACE', 'Biotech. Twin-helix tower.'),
    ('orbital', 'ORBITAL', 'Aerospace. Launch ring and rocket.'),
    ('meridian', 'MERIDIAN', 'Freight. Gantry-crane castle, rail, port.'),
    ('aurelian', 'AURELIAN CONCORD', 'Finance and politics. Circus Aurelius.'),
    ('tethys', 'TETHYS DEEP', 'Ocean tech. Pier city over a drowned quarter.'),
]


def _pattern(c, kind, x, y, w, h, col):
    rng = random.Random(3)
    c.poly(rect_pts(x + w / 2, y + h / 2, w, h), (22, 26, 36), 1.0, (70, 78, 96), 1.0)
    if kind == 'organic':
        for _ in range(14):
            px, py = x + rng.uniform(3, w - 3), y + rng.uniform(3, h - 3)
            a = rng.uniform(0, 6.3)
            pts = [(px, py)]
            for _k in range(6):
                a += rng.uniform(-0.6, 0.6)
                px += math.cos(a) * 4.5
                py += math.sin(a) * 4.5
                pts.append((min(x + w - 1, max(x + 1, px)), min(y + h - 1, max(y + 1, py))))
            c.line(pts, col, 1.0, 0.9)
    elif kind == 'grid':
        for i in range(1, 8):
            c.line([(x + i * w / 8, y + 1), (x + i * w / 8, y + h - 1)], col, 1.0, 0.8)
        for j in range(1, 5):
            c.line([(x + 1, y + j * h / 5), (x + w - 1, y + j * h / 5)], col, 1.0, 0.8)
    elif kind == 'super':
        for i in range(1, 3):
            c.line([(x + i * w / 3, y + 1), (x + i * w / 3, y + h - 1)], col, 1.6, 0.9)
        for j in range(1, 2):
            c.line([(x + 1, y + j * h / 2), (x + w - 1, y + j * h / 2)], col, 1.6, 0.9)
        for i in range(3):
            for j in range(2):
                c.poly(rect_pts(x + (i + 0.5) * w / 3, y + (j + 0.5) * h / 2, w / 3 * 0.6, h / 2 * 0.6),
                       col, 0.45)
    elif kind == 'curvi':
        for r in range(8, 70, 8):
            pts = [(x + 2 + r * math.cos(t), y + h - 2 + r * math.sin(t)) for t in [i * 0.08 for i in range(-20, 1)]]
            pts = [(px, py) for px, py in pts if x < px < x + w and y < py < y + h]
            if len(pts) > 1:
                c.line(pts, col, 1.0, 0.8)
        for k in range(5):
            a = -0.2 - k * 0.3
            c.line([(x + 2 + 8 * math.cos(a), y + h - 2 + 8 * math.sin(a)), (x + 2 + 62 * math.cos(a), y + h - 2 + 62 * math.sin(a))], col, 1.0, 0.6)
    elif kind == 'radial':
        cx, cy = x + w / 2, y + h / 2
        for r in (8, 15, 22):
            c.line(circle_pts(cx, cy, r, 30) + [circle_pts(cx, cy, r, 30)[0]], col, 1.0, 0.8)
        for k in range(10):
            a = k * math.pi / 5
            c.line([(cx + 4 * math.cos(a), cy + 4 * math.sin(a)), (cx + 26 * math.cos(a), cy + 26 * math.sin(a))], col, 1.0, 0.7)
    elif kind == 'slum':
        for _ in range(110):
            px, py = x + rng.uniform(2, w - 2), y + rng.uniform(2, h - 2)
            c.poly(rect_pts(px, py, rng.uniform(1.5, 3), rng.uniform(1.5, 3), rng.uniform(0, 3)), SLUM, 0.8)


def make_panel(title, subtitle, blurb_lines, district_notes=None, skip=(), extras=(), evo=(), compact=False):
    c = Canvas(PW, PH, 2, 1.0, BG)
    y = 38
    c.text(28, y, title, 46, TEXT, spacing=3, title=True, anchor='lm', halo=False)
    y += 34
    c.text(28, y, subtitle, 15, (130, 200, 255), anchor='lm', halo=False, weight='SemiBold')
    y += 24
    for ln in blurb_lines:
        c.text(28, y, ln, 12.5, DIM, anchor='lm', halo=False, weight='Regular')
        y += 17
    y += 8

    def header(name):
        nonlocal y
        c.line([(28, y + 10), (PW - 28, y + 10)], (50, 58, 76), 1.0, 1.0)
        c.text(28, y, name, 13, (255, 255, 255), spacing=3, anchor='lm', halo=False, weight='Bold')
        y += 26

    header('DISTRICTS')
    notes = district_notes or {}
    for key, name, desc in DISTRICTS:
        col = COL[key]
        c.poly(rect_pts(46, y + 14, 36, 28), col, 0.30, tint(col, 0.1), 2.0)
        c.poly(rect_pts(46, y + 14, 36, 28), None, 1.0, col, 2.0)
        c.text(76, y + 4, name, 16, tint(col, 0.35), anchor='lm', halo=False, weight='Bold', spacing=0.5)
        c.text(76, y + 23, notes.get(key, desc), 12, DIM, anchor='lm', halo=False, weight='Regular')
        y += 44
    y += 4

    header('MOVEMENT NETWORK')
    rows = [
        ('ring', 'Ring motorway (R1 inner, R2 outer)'),
        ('motorway', 'Radial motorway'),
        ('ramp', 'On/off ramps; cloverleaf and stack interchanges'),
        ('truck', 'Freight expressway (heavy trucks only)'),
        ('arterial', 'Arterial avenue'),
        ('collector', 'Collector street (locals = thinnest lines)'),
        ('freight', 'Freight rail (to port and yards)'),
        ('commuter', 'Commuter / regional rail'),
        ('metro', 'Metro (underground = dashed)'),
        ('bridge', 'Bridge / viaduct over water'),
        ('drone', 'Drone corridor (Halcyon-licensed airspace)'),
        ('ferry', 'Ferry / shipping lane'),
    ]
    for kind, label in rows:
        if kind in skip:
            continue
        x0, x1 = 40, 112
        yy = y + 8
        if kind == 'ring':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 11.5)
            c.line([(x0, yy), (x1, yy)], ROAD_FILL, 8)
        elif kind == 'motorway':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 9.5)
            c.line([(x0, yy), (x1, yy)], ROAD_FILL, 6.4)
            c.circle(76, yy, 5.5, (10, 12, 18), (255, 255, 255), 1.4)
        elif kind == 'truck':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 9)
            c.line([(x0, yy), (x1, yy)], (210, 214, 220), 6)
            c.line([(x0, yy), (x1, yy)], (255, 150, 30), 1.4, dash=(3, 3))
        elif kind == 'arterial':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 4.8)
            c.line([(x0, yy), (x1, yy)], (196, 202, 214), 3)
        elif kind == 'collector':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 2.7)
            c.line([(x0, yy), (x1, yy)], (156, 162, 178), 1.5)
        elif kind == 'ramp':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 6.0)
            c.line([(x0, yy), (x1, yy)], ROAD_FILL, 3.4)
            for sx in (58, 96):
                pts = [(sx - 10, yy), (sx - 4, yy - 2), (sx + 1, yy - 7), (sx + 8, yy - 11), (sx + 14, yy - 8), (sx + 12, yy - 3), (sx + 6, yy)]
                c.line(pts, ROAD_CASING, 4.0)
                c.line(pts, (255, 232, 168), 2.1)
        elif kind == 'freight':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 5.6)
            c.line([(x0, yy), (x1, yy)], (232, 232, 236), 3.4)
            c.line([(x0, yy), (x1, yy)], (24, 26, 34), 3.4, dash=(2.1, 2.1))
            c.circle(x1 + 8, yy, 3.4, (255, 190, 90), (8, 10, 14), 1.4)
        elif kind == 'commuter':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 4.4)
            c.line([(x0, yy), (x1, yy)], (190, 198, 214), 2.4)
            c.circle(x1 + 8, yy, 4.0, (200, 206, 224), (8, 10, 14), 1.6)
            c.circle(x1 + 8, yy, 1.6, (8, 10, 14))
        elif kind == 'metro':
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 4.6)
            c.line([(x0, yy), (x1, yy)], (255, 255, 255), 2.4)
            c.circle(x1 + 8, yy, 3.6, (255, 255, 255), (8, 10, 14), 1.4)
        elif kind == 'bridge':
            c.line([(x0, yy), (x1, yy)], (236, 246, 255), 11.2)
            c.line([(x0, yy), (x1, yy)], ROAD_CASING, 8.6)
            c.line([(x0, yy), (x1, yy)], ROAD_FILL, 6.2)
        elif kind == 'drone':
            c.line([(x0, yy), (x1, yy)], (80, 235, 255), 1.3, 0.85, dash=(4, 3))
        elif kind == 'ferry':
            c.line([(x0, yy), (x1, yy)], (150, 225, 255), 1.2, 0.8, dash=(3, 4))
            c.circle(x0, yy, 3.0, (8, 10, 16), (150, 225, 255), 1.4)
            c.circle(x1, yy, 3.0, (8, 10, 16), (150, 225, 255), 1.4)
        c.text(140 if kind in ('freight', 'commuter', 'metro') else 128, yy, label, 12.5, TEXT, anchor='lm', halo=False,
               weight='Regular')
        y += 25
    y += 6

    header('LAND USE AND OVERLAYS')
    items = [
        ('park', 'Park / greenbelt / woodland'),
        ('plaza', 'Plaza, civic square, forum'),
        ('industry', 'Industry, depots, yards'),
        ('port', 'Port, container terminal, piers'),
        ('slum', 'Informal housing, stacked slums'),
        ('drowned', 'Drowned quarter (behind dams)'),
        ('undercity', 'Undercity (hatched, below the old core)'),
        ('airport', 'Airport / spaceport / exclusion zone'),
        ('lots', 'Dense low-rise suburb lots'),
        ('sprawl', 'Old-city sprawl (organic, dense)'),
        ('wall', 'Corporate enclave wall and gates'),
        ('seawall', 'Sea wall / storm barrier / dam'),
        ('windfarm', 'Offshore wind farm'),
    ]
    for kind, label in items:
        if kind in skip:
            continue
        yy = y + 8
        bx = rect_pts(60, yy, 40, 16)
        if kind == 'park':
            c.poly(bx, PARK, 0.85)
            for k in range(8):
                c.circle(46 + k * 4.5, yy + (k % 2) * 4 - 2, 2, PARK_DARK)
        elif kind == 'plaza':
            c.poly(bx, (214, 208, 190), 0.55, (240, 236, 220), 1.0)
        elif kind == 'industry':
            c.poly(bx, (22, 26, 36), 1.0)
            for k in range(5):
                c.poly(rect_pts(46 + k * 7.5, yy - 3 + (k % 2) * 5, 6, 5), INDUSTRY, 0.8)
        elif kind == 'port':
            c.poly(bx, (120, 130, 146), 1.0, (200, 210, 224), 1.0)
            cc = ((200, 90, 60), (70, 130, 200), (210, 190, 70), (90, 170, 120))
            for k in range(8):
                c.poly(rect_pts(44 + k * 4.6, yy - 3 + (k % 2) * 5.5, 3.6, 3.4), cc[k % 4], 0.9)
        elif kind == 'slum':
            _pattern(c, 'slum', 40, yy - 8, 40, 16, SLUM)
        elif kind == 'drowned':
            c.poly(bx, (24, 72, 92), 0.96, (130, 220, 240), 1.0, 0.5)
            for k in range(1, 5):
                c.line([(40 + k * 8, yy - 8), (40 + k * 8, yy + 8)], (110, 200, 220), 0.8, 0.45)
            c.line([(40, yy), (80, yy)], (110, 200, 220), 0.8, 0.45)
        elif kind == 'undercity':
            c.poly(bx, (22, 26, 36), 1.0)
            for k in range(-4, 8):
                c.line([(40 + k * 5, yy + 8), (40 + k * 5 + 16, yy - 8)], (190, 130, 255), 0.8, 0.45)
            c.line(bx + [bx[0]], (190, 130, 255), 1.4, 0.9, dash=(2, 2.5))
        elif kind == 'airport':
            c.poly(bx, (24, 28, 40), 1.0, (90, 100, 120), 1.0)
            c.line([(44, yy + 3), (76, yy - 3)], (230, 236, 250), 2)
            c.line([(46, yy - 4), (74, yy + 5)], (230, 236, 250), 2)
        elif kind == 'lots':
            c.poly(bx, (22, 26, 36), 1.0)
            for k in range(7):
                for q in range(2):
                    c.poly(rect_pts(44 + k * 5.4, yy - 3.5 + q * 7, 4.2, 2.8), (182, 166, 144), 0.8)
        elif kind == 'sprawl':
            c.poly(bx, (74, 52, 36), 1.0)
            rr = random.Random(5)
            for _ in range(46):
                c.poly(rect_pts(rr.uniform(42, 78), yy + rr.uniform(-6, 6), rr.uniform(1.3, 2.6), rr.uniform(1.3, 2.4), rr.uniform(0, 3)), (222, 150, 96), 0.85)
        elif kind == 'wall':
            c.line([(40, yy), (80, yy)], ROAD_CASING, 4.6)
            c.line([(40, yy), (80, yy)], (255, 160, 170), 2.6, dash=(9, 1.6))
            c.glyph('checkpoint', 94, yy, 5.5)
        elif kind == 'seawall':
            c.line([(40, yy), (80, yy)], ROAD_CASING, 5.6)
            c.line([(40, yy), (80, yy)], (206, 220, 236), 3.4)
            for k in range(9):
                c.line([(42 + k * 4.5, yy + 1), (42 + k * 4.5, yy + 5)], (206, 220, 236), 1.0)
        if kind == 'windfarm':
            c.poly(bx, (10, 24, 46), 1.0, (90, 110, 140), 0.8)
            for k in range(4):
                c.circle(46 + k * 9, yy, 1.6, (230, 240, 250))
                for q in range(3):
                    a = q * 2.094 + k
                    c.line([(46 + k * 9, yy), (46 + k * 9 + 4 * math.cos(a), yy + 4 * math.sin(a))], (230, 240, 250), 0.9)
        c.text(128 if kind != 'wall' else 112, yy, label, 12.5, TEXT, anchor='lm', halo=False, weight='Regular')
        y += 25
    y += 6

    header('STREET PATTERN BY ERA')
    pats = [('organic', 'Medieval port core'), ('grid', 'Rail-era grid'), ('curvi', 'Mid-century suburb'),
            ('super', 'Corp superblocks'), ('radial', 'Planned / Roman radial'), ('slum', 'Informal growth')]
    for i, (k, lab) in enumerate(pats):
        cx_ = 28 + (i % 3) * 200
        cy_ = y + (i // 3) * 78
        _pattern(c, k, cx_, cy_, 90, 50, tint(COL['centre'], 0.1) if k not in ('slum',) else SLUM)
        c.text(cx_ + 45, cy_ + 62, lab, 11.5, DIM, halo=False, weight='Regular')
    y += 168

    header('SYMBOLS')
    syms = [
        ('rebel', 'Rebel Cell hideout'), ('hub', 'Multimodal transit hub'),
        ('arcology', 'Arcology / residential megablock'), ('megastructure', 'Megastructure / corp tower'),
        ('stadium', 'Stadium / arena'), ('hospital', 'Hospital'),
        ('university', 'University / research campus'), ('market', 'Neon market'),
        ('datacentre', 'Data centre'), ('power', 'Power plant / substation'),
        ('water', 'Water works'), ('sewage', 'Sewage works'),
        ('cemetery', 'Cemetery'), ('airport', 'Airport / spaceport'),
        ('checkpoint', 'Checkpoint / gate'), ('recycling', 'Recycling / landfill'),
    ]
    for i, (k, lab) in enumerate(syms):
        if k in skip:
            continue
        cx_ = 40 + (i % 2) * 300
        cy_ = y + (i // 2) * 27
        c.glyph(k, cx_, cy_ + 6, 8.5)
        c.text(cx_ + 18, cy_ + 6, lab, 12, TEXT, anchor='lm', halo=False, weight='Regular')
    y += 8 * 27 + 4
    if evo:
        import textwrap
        header('HOW THE CITY GREW')
        for era, txt in evo:
            lines = textwrap.wrap(txt, 74)
            c.text(28, y + 2, era, 12, (255, 214, 140), anchor='lm', halo=False, weight='Bold')
            for ln in lines:
                c.text(112, y + 2, ln, 11.5, (200, 208, 224), anchor='lm', halo=False, weight='Regular')
                y += 15
            y += 5
    for lab in extras:
        c.text(28, y, lab, 12, DIM, anchor='lm', halo=False)
        y += 17
    return c.img.resize((PW, PH), Image.LANCZOS)


def compose(map_img, panel_img, path):
    W = map_img.width + panel_img.width
    out = Image.new('RGB', (W, max(map_img.height, panel_img.height)), BG)
    out.paste(map_img, (0, 0))
    out.paste(panel_img, (map_img.width, 0))
    out.save(path)
    return out
