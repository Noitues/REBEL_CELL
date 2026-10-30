"""Kit sheet: every module and prop (renders from bl_kit.py), labelled, plus the layout-grid diagrams of the three rooms.
usage: python kit_sheet.py -> v2/kit_sheet.jpg"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_gen

KIT = 'D:/rc_scratch/cutaway_kit/kit/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/kit_sheet.jpg'
FR = 'D:/rc_art/art-pass/assets/fonts/'
F = lambda n, s: ImageFont.truetype(FR + n, s)
MONO, ANTON = 'ShareTechMono-Regular.ttf', 'Anton-Regular.ttf'
BG = (14, 10, 28)
LIME = (150, 255, 70)
CYAN = (63, 230, 255)
PINK = (255, 70, 150)
TXT = (214, 226, 214)

GROUPS = [
    ('modules', 'SHELL MODULES', 'floor plate | wall panel | window | door | cut edge | corner post   (cel bands, ink, neon trim)',
     {'floor_plate': 'FLOOR PLATE 1x1 m, lit pool', 'wall_panel': 'WALL PANEL wainscot + neon trim', 'window_module': 'WINDOW 2 m, night glass',
      'door_module': 'DOOR 1.4 m, lit frame', 'cut_edge': 'CUT EDGE slab + hatch + neon', 'corner_post': 'CORNER POST'}),
    ('bio_lab', 'BIO-LAB  (Elite Router; Virus-exploit Site)', 'hero: helix tank   |   light: corp lime   |   props: culture vats, bench, centrifuge, incubator, cart',
     {'vat': 'VAT 1x1 h2.5', 'vat_bank': 'VAT BANK 3x1', 'bench': 'BENCH 3x1', 'centrifuge': 'CENTRIFUGE 1x1', 'incubator_pod': 'INCUBATOR 2x1',
      'monitor_cart': 'MONITOR CART 1x1', 'helix_tank': 'HERO helix tank 2x2'}),
    ('server_room', 'SERVER ROOM  (Server Rack nodes; Breach-exploit Site)', 'hero: core tower   |   light: cyan pool, lime trim   |   props: racks, cooling, console, UPS, cable trays',
     {'rack': 'RACK 1x1 h2.5', 'rack_row': 'RACK ROW 4x1', 'cooling': 'COOLING 2x1', 'console': 'CONSOLE 2x1', 'ups': 'UPS 1x1',
      'cable_tray': 'CABLE TRAY 3x1 (low)', 'core_tower': 'HERO core tower 2x2'}),
    ('greenhouse', 'GREENHOUSE / SEED VAULT  (Virus-exploit Site; Heat objective Sites)', 'hero: seed tree   |   light: lime pool + pink grow lamps   |   props: planters, tanks, seed drawers',
     {'planter': 'PLANTER 2x1', 'plant_tank': 'PLANT TANK 1x1', 'seed_wall': 'SEED WALL 3x1', 'grow_lamp': 'GROW LAMP 1x1 (pink)', 'cistern': 'CISTERN 1x1',
      'seed_tree': 'HERO seed tree 2x2'}),
    ('records_office', 'RECORDS / OFFICE  (Router; Intel-exploit and Scrub Records Sites)', 'hero: archive tower   |   light: amber pool, lime trim   |   props: desks, cabinets, shelves',
     {'desk': 'DESK 2x1', 'cabinet': 'CABINET 1x1', 'shelf_stack': 'SHELF STACK 2x1', 'copier': 'COPIER 1x1', 'box_pile': 'BOX PILE 1x1', 'archive_tower': 'HERO archive tower 2x2'}),
    ('lobby', 'LOBBY / RECEPTION  (Terminal and Mainframe nodes; the ground floor of every building)', 'hero: Solace helix sculpture   |   light: corp lime   |   props: reception, kiosk, seats, plants',
     {'reception': 'RECEPTION 3x1', 'kiosk': 'KIOSK 1x1', 'seats': 'SEATS 2x1', 'planter_lobby': 'PLANTER 1x1', 'emblem_sculpture': 'HERO helix sculpture 2x2'}),
]
CATCOL = {'vat': (120, 220, 60), 'rack': (80, 150, 200), 'plant': (120, 200, 90)}


def grid_diagram(room, seed, cell=44):
    sp = kit_gen.generate(room, seed)
    W, D = sp['W'], sp['D']
    im = Image.new('RGB', (W * cell + 20, D * cell + 60), BG)
    d = ImageDraw.Draw(im)
    f = F(MONO, 12)
    # y grows up on screen so +y (back wall) is at the top; camera sees bottom (-y) and right (+x) edges: the cut edges
    def cx(x):
        return 10 + x * cell

    def cy(y):
        return 10 + (D - 1 - y) * cell
    for i in range(W):
        for j in range(D):
            col = (24, 40, 44)
            if j < 2 or i >= W - 2:
                col = (40, 28, 54)          # cut-edge cells: low props only
            d.rectangle([cx(i), cy(j), cx(i) + cell - 2, cy(j) + cell - 2], fill=col)
    dw = sp['door']['pos']
    for i in range(max(0, dw - 1), min(W, dw + 3)):
        for j in range(D - 3, D):
            d.rectangle([cx(i), cy(j), cx(i) + cell - 2, cy(j) + cell - 2], outline=(255, 185, 56), width=1)
    for p in sp['props']:
        w, dd, h = kit_gen.CAT[p['name']]
        fw, fd = (w, dd) if p['rot'] % 2 == 0 else (dd, w)
        x0, y0 = cx(p['x']), cy(p['y'] + fd - 1)
        col = LIME if p.get('hero') else (96, 160, 150)
        d.rectangle([x0 + 1, y0 + 1, x0 + fw * cell - 3, y0 + fd * cell - 3], fill=(30, 70, 66), outline=col, width=2 if p.get('hero') else 1)
        # facing tick
        mx, my = x0 + fw * cell / 2, y0 + fd * cell / 2
        r = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}[p['rot']]
        d.line([mx, my, mx + r[0] * cell * 0.35, my + r[1] * cell * 0.35], fill=col, width=2)
        d.text((x0 + 4, y0 + 3), p['name'][:9], font=F(MONO, 10), fill=TXT)
    for l in sp['lights']:
        d.ellipse([cx(l['x'] - 0.5) + cell / 2 - 4, cy(l['y'] - 0.5) + cell / 2 - 4, cx(l['x'] - 0.5) + cell / 2 + 4, cy(l['y'] - 0.5) + cell / 2 + 4], fill=LIME if l.get('col') != 'pink' else PINK)
    d.text((10, D * cell + 16), '%s seed %d  density %.2f  props %d' % (room, sp['seed'], sp['rules']['density'], sp['rules']['props']), font=f, fill=TXT)
    d.text((10, D * cell + 32), 'door aisle = amber, cut-edge cells = violet, tick = facing', font=F(MONO, 11), fill=(150, 160, 150))
    return im


def main():
    TW, TH = 346, 360
    COLS = 7
    W = COLS * TW + 40
    rows = len(GROUPS)
    H = 120 + rows * (TH + 70) + 400
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((20, 18), 'COMBAT CUTAWAY KIT v2', font=F(ANTON, 40), fill=LIME)
    d.text((20, 70), 'procedural interior kit for the Solace combat cutaway (art proposal for the Godot port)   -   1 cell = 1 m, room grid 9 x 7, cel bands + ink + emissive accents', font=F(MONO, 16), fill=TXT)
    y = 110
    for key, title, sub, labels in GROUPS:
        d.text((20, y), title, font=F(ANTON, 24), fill=CYAN)
        d.text((20, y + 32), sub, font=F(MONO, 14), fill=(150, 165, 150))
        y += 58
        x = 20
        for item, lab in labels.items():
            p = KIT + '%s__%s.png' % (key, item)
            if os.path.exists(p):
                t = Image.open(p).convert('RGBA')
                t = t.resize((TW, int(TW * t.height / t.width)), Image.LANCZOS)
                tile = Image.new('RGBA', (TW, TH), BG + (255,))
                tile.alpha_composite(t, (0, (TH - t.height) // 2))
                im.paste(tile.convert('RGB'), (x, y))
                d.rectangle([x, y, x + TW - 2, y + TH - 2], outline=(40, 34, 70))
            d.text((x + 8, y + TH - 22), lab, font=F(MONO, 13), fill=LIME if 'HERO' in lab else TXT)
            x += TW
        y += TH + 12
    d.text((20, y), 'GENERATION: layout grid per room (seeded), props and light pools', font=F(ANTON, 24), fill=CYAN)
    y += 40
    x = 20
    for room, seed in (('bio_lab', 11), ('server_room', 23), ('greenhouse', 37)):
        g = grid_diagram(room, seed)
        im.paste(g, (x, y))
        x += g.width + 30
    # rule text
    rules = ['RULES', '1 door on back wall, 3-cell clear aisle', '2 hero prop: 2x2 pad, centre-back third', '3 wall band first (70%), then open floor',
             '4 density target 0.50-0.70 of 63 cells', '5 max 2 big / 3 small of one prop', '6 cut-edge cells (y<2, x>=7): props <= 1.2 m',
             '7 light = corp colour pool at hero + 1 per 3 props', '8 windows 2-3 on back wall, 1-2 on left wall']
    for i, t in enumerate(rules):
        d.text((x + 10, y + 8 + i * 22), t, font=F(MONO, 15), fill=LIME if i == 0 else TXT)
    im.convert('RGB').save(OUT, quality=92)
    print('kit sheet', im.size)


main()
