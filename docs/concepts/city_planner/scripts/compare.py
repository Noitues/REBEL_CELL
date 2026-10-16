"""Comparison sheet: all designs side by side + scoring table."""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from canvas import get_font

OUT = os.path.join(os.path.dirname(__file__), '..')
BG = (11, 14, 21)
TXT = (232, 236, 242)
DIM = (150, 160, 178)

DESIGNS = [
    ('A', 'map_A_horseshoe_bay.png', 'A  HORSESHOE BAY', 'Bay city. Old port at the bay head, rings and radials, storm barrier at the mouth.'),
    ('B', 'map_B_ribbon_coast.png', 'B  RIBBON COAST', 'Linear coastal city. Three parallel motorways and a rail trunk between sea and mountains.'),
    ('C', 'map_C_river_meander.png', 'C  MEANDER', 'River city. Island old town in an omega bend, bridges everywhere, estuary port.'),
    ('D', 'map_D_delta_archipelago.png', 'D  DROWNED DELTA', 'Archipelago. Every district is an island; causeways and tunnels are the only roads.'),
    ('E', 'map_E_headland_hills.png', 'E  HEADLAND HILLS', 'Hilly peninsula. Ocean west, bay east, great bridges, summit HQs.'),
]
CRIT = [
    ('Reads at a glance (7 clear nodes)', [4, 3, 4, 5, 3]),
    ('Centre + six: short spokes, even spread', [4, 2, 4, 5, 3]),
    ('Feels like it evolved', [4, 5, 5, 3, 5]),
    ('Terrain justifies every corp site', [4, 4, 4, 4, 5]),
    ('Chokepoints for raids / Heat / gates', [3, 2, 4, 5, 4]),
    ('Identity / visual drama', [3, 3, 4, 5, 5]),
]
COLORS = [(120, 180, 255), (255, 190, 90), (120, 230, 170), (255, 120, 170), (200, 150, 255)]


def main():
    m = json.load(open(os.path.join(OUT, 'scripts', 'metrics.json')))
    cell, cap, mar = 860, 118, 40
    W = 3 * cell + 4 * mar
    H = 150 + 2 * (cell + cap) + 3 * 30
    sheet = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((mar, 36), 'REBEL_CELL  -  CITY PLANNER STUDY: FIVE LAYOUTS', font=get_font(52, title=True), fill=TXT)
    d.text((mar, 104), 'Same brief, five terrains. 1 unit = 20 m; each map is 20 km across. Scores 1-5 are the planner\'s judgement for a campaign map.',
           font=get_font(18, 'Regular'), fill=DIM)
    pos = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
    for (key, fn, title, line), (cx, cy) in zip(DESIGNS, pos):
        x = mar + cx * (cell + mar)
        y = 150 + cy * (cell + cap + 30)
        im = Image.open(os.path.join(OUT, fn)).resize((cell, cell), Image.LANCZOS)
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + cell, y + cell], outline=(70, 80, 100), width=2)
        d.text((x, y + cell + 10), title, font=get_font(30, title=True), fill=COLORS[DESIGNS.index((key, fn, title, line))])
        d.text((x, y + cell + 48), line, font=get_font(15, 'Regular'), fill=TXT)
        mm = m[key.lower()]
        d.text((x, y + cell + 74), 'mean centre-to-district distance %d units (%.1f km)   far/near ratio %.2f' %
               (mm['mean'], mm['mean'] * 0.02, mm['spread']), font=get_font(14, 'Regular'), fill=DIM)
    # scoring cell
    x = mar + 2 * (cell + mar)
    y = 150 + (cell + cap + 30)
    d.rectangle([x, y, x + cell, y + cell], fill=(16, 20, 30), outline=(70, 80, 100), width=2)
    d.text((x + 24, y + 22), 'SCORECARD', font=get_font(34, title=True), fill=TXT)
    cx0 = x + 440
    for i, (key, *_r) in enumerate(DESIGNS):
        d.text((cx0 + i * 76 + 24, y + 70), key, font=get_font(30, 'Bold'), fill=COLORS[i], anchor='mm')
    yy = y + 110
    tot = [0] * 5
    for lab, sc in CRIT:
        d.text((x + 24, yy + 22), lab, font=get_font(17, 'Regular'), fill=TXT, anchor='lm')
        for i, v in enumerate(sc):
            tot[i] += v
            cxx = cx0 + i * 76 + 24
            for k in range(5):
                col = COLORS[i] if k < v else (44, 52, 70)
                d.ellipse([cxx - 28 + k * 11.5, yy + 16, cxx - 28 + k * 11.5 + 8, yy + 24], fill=col)
        yy += 54
    d.line([(x + 24, yy), (x + cell - 24, yy)], fill=(70, 80, 100), width=2)
    d.text((x + 24, yy + 36), 'TOTAL (of 30)', font=get_font(22, 'Bold'), fill=TXT, anchor='lm')
    for i in range(5):
        d.text((cx0 + i * 76 + 24, yy + 36), str(tot[i]), font=get_font(30, 'Bold'), fill=COLORS[i], anchor='mm')
    yy += 90
    notes = [
        'D wins on readability and gate/raid design but is the most',
        'engineered looking; C is the safest "real city"; E is the',
        'most dramatic; A is the classic ring-radial; B is realistic',
        'but a poor game board (the centre is not central).',
        '',
        'Suggested path: D as the base, with C\'s canal-ring old town and',
        'A\'s ring-road logic folded in (see README).',
    ]
    for ln in notes:
        d.text((x + 24, yy), ln, font=get_font(18, 'Regular'), fill=DIM if ln else DIM)
        yy += 26
    sheet.save(os.path.join(OUT, 'comparison.png'))
    print('saved', sheet.size)


if __name__ == '__main__':
    main()
