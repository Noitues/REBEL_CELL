"""Design D - DROWNED DELTA ARCHIPELAGO. Seven islands in a flooded lagoon, linked by causeways, bridges and tunnels."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from citymap import COL, CityMap, tint
from common import (NEU, corp_walls, district_labels, era_rings, fabric, glyphs, shields, slums, small_labels, wind)
from geom import arc_pts, blob, circle_pts, offset_line

OUT = os.path.join(os.path.dirname(__file__), '..')

MAIN = [(390, 500), (402, 440), (450, 405), (520, 395), (590, 415), (625, 465), (620, 540), (580, 590), (520, 610),
        (455, 600), (410, 560)]
HALC = [(430, 215), (455, 160), (520, 140), (575, 165), (595, 225), (565, 275), (500, 290), (448, 265)]
SOL = [(700, 270), (730, 225), (790, 215), (845, 245), (855, 300), (820, 345), (755, 350), (712, 320)]
ORB = [(870, 350), (910, 330), (950, 380), (965, 520), (945, 650), (900, 690), (870, 640), (860, 500)]
MER = [(640, 700), (720, 680), (810, 700), (850, 760), (830, 830), (740, 860), (660, 835), (630, 770)]
AUR = [(150, 600), (190, 545), (260, 535), (320, 570), (335, 640), (300, 705), (220, 720), (160, 680)]
KEEP = [(385, 775), (440, 752), (490, 772), (500, 820), (452, 848), (395, 835)]
MAINLAND = [(-60, -60), (1060, -60), (1060, 70), (920, 100), (800, 95), (700, 120), (600, 90), (500, 60), (400, 95),
            (320, 130), (250, 170), (205, 250), (170, 340), (140, 430), (120, 520), (100, 610), (105, 700), (130, 780),
            (160, 860), (150, 960), (120, 1060), (-60, 1060)]


def build():
    m = CityMap(seed=41)
    m.set_islands([(MAINLAND, True), (MAIN, True), (HALC, True), (SOL, True), (ORB, True), (MER, False), (AUR, True),
                   (KEEP, True),
                   ([(625, 625), (655, 615), (670, 640), (650, 662), (625, 650)], True),     # necropolis islet
                   ([(540, 700), (575, 695), (588, 720), (552, 732)], True),                 # power platform
                   ([(930, 740), (972, 735), (988, 775), (952, 792)], True),                 # landfill islet
                   ([(378, 318), (410, 312), (422, 340), (390, 352)], True)], noise_amp=3.0)  # fort islet
    bumps = [(500, 215, 60, 50, 0.95, 0.0), (780, 285, 50, 45, 0.5, 0.0), (520, 490, 60, 50, 0.3, 0.0),
             (205, 600, 22, 22, 0.40, 0), (255, 585, 22, 22, 0.38, 0), (290, 625, 22, 22, 0.36, 0),
             (240, 660, 20, 20, 0.34, 0), (190, 640, 20, 20, 0.32, 0), (280, 560, 18, 18, 0.30, 0),
             (0, 300, 150, 260, 0.7, 0.0), (300, -20, 260, 100, 0.55, 0), (900, 0, 160, 80, 0.4, 0),
             (100, 880, 90, 120, 0.3, 0)]
    m.base(bumps)
    m.sunken([(335, 735), (420, 705), (520, 725), (550, 800), (510, 880), (410, 905), (335, 860)], seed=4, grid_angle=14)
    m.sunken([(330, 620), (370, 600), (400, 640), (380, 700), (335, 690)], seed=5, grid_angle=-6)   # flooded lower town
    # ---- districts (each island is a node)
    centre = m.zone('centre', MAIN, COL['centre'], 0.30)
    halc = m.zone('halcyon', HALC, COL['halcyon'], 0.26)
    sol = m.zone('solace', SOL, COL['solace'], 0.24)
    orb = m.zone('orbital', ORB, COL['orbital'], 0.24)
    mer = m.zone('meridian', MER, COL['meridian'], 0.24, smooth=False)
    aur = m.zone('aurelian', AUR, COL['aurelian'], 0.24)
    teth = m.zone('tethys', KEEP, COL['tethys'], 0.24)
    cc = tint(COL['centre'], 0.25)
    m.tex_grid(centre, 20, 7.5, 6.5, jitter=0.35, warp_amp=7, warp_wl=70, gap=0.25, major=5, color=cc, a_minor=0.45,
               a_major=0.75, seed=1)
    m.tex_walks(centre, 130, (25, 70), 0.35, color=cc, a=0.5, seed=1)
    m.tex_radial(halc, (505, 215), 8, 90, 18, 9, tint(COL['halcyon'], 0.3), 0.55, seed=2)
    m.tex_super(halc, 0, 34, tint(COL['halcyon'], 0.3), seed=3, fill_prob=0.5)
    m.tex_curvi(sol, (775, 285), 15, 110, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=40, seed=3)
    m.tex_grid(orb, 90, 14, 40, jitter=0.1, major=2, color=tint(COL['orbital'], 0.3), a_minor=0.3, a_major=0.5, seed=8)
    m.tex_super(orb, 90, 40, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.4)
    m.tex_super(mer, 5, 36, tint(COL['meridian'], 0.3), seed=7)
    m.tex_radial(aur, (240, 615), 14, 80, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, -12, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_super(teth, 0, 22, tint(COL['tethys'], 0.3), seed=6)
    # ---- parks, civic, industry (on islands and mainland)
    m.park([(450, 440), (490, 430), (505, 470), (460, 485)], seed=7, a=0.7)
    m.park([(560, 520), (600, 510), (610, 555), (570, 568)], seed=8, a=0.7)
    m.park([(215, 570), (250, 560), (262, 600), (225, 610)], seed=9)
    m.park([(720, 245), (760, 238), (772, 275), (735, 285)], seed=10)
    m.park([(470, 170), (510, 160), (520, 195), (480, 205)], seed=11)
    m.park([(240, 40), (360, 30), (440, 80), (360, 110), (260, 100)], seed=2, free=True)
    m.park([(560, 20), (700, 30), (800, 60), (700, 90), (590, 70)], seed=3, free=True)
    m.park([(0, 560), (90, 540), (100, 650), (20, 680)], seed=4, free=True)
    m.park([(30, 800), (110, 790), (140, 880), (50, 930)], seed=5, free=True)
    m.park([(920, 10), (1000, 20), (1010, 80), (940, 70)], seed=6, free=True)
    m.plaza([(498, 470), (524, 470), (524, 496), (498, 496)])
    m.plaza([(235, 600), (262, 600), (262, 626), (235, 626)])
    term = m.built([(660, 760), (740, 750), (748, 800), (668, 812)], (110, 120, 138), 0.55)
    m.container_yard(704, 782, 85, 52, -0.1, clip=term)
    m.built([(740, 700), (830, 715), (835, 740), (745, 728)], (60, 64, 76), 0.8)
    m.industry([(760, 760), (836, 770), (830, 825), (760, 840)], seed=2, free=False, angle=8)
    m.built([(545, 702), (572, 698), (580, 718), (552, 726)], (90, 96, 112), 0.7)               # power platform
    m.built([(936, 745), (968, 741), (980, 772), (950, 786)], (100, 130, 90), 0.6)              # landfill
    m.built([(630, 628), (652, 620), (664, 640), (648, 656), (630, 646)], (110, 120, 110), 0.7)  # necropolis
    m.built([(100, 140), (200, 125), (225, 190), (130, 215)], (40, 46, 60), 0.85, free=True)    # airport
    m.built([(300, 160), (360, 150), (370, 190), (310, 200)], (70, 90, 100), 0.7, free=True)    # data
    m.built([(105, 740), (130, 745), (128, 775), (100, 770)], (130, 110, 90), 0.6)               # sewage
    m.built([(870, 12), (930, 8), (940, 40), (880, 48)], (70, 90, 100), 0.7, free=True)         # water works
    for i, (tx, ty, tr, nm) in enumerate([(70, 470, 14, 'PORTLEY'), (60, 330, 12, ''), (65, 840, 14, 'SOUTHSHORE'),
                                           (620, 40, 12, 'NORTHSIDE')]):
        m.town(tx, ty, tr, seed=i, name=nm)
    slums(m, [[(130, 300), (180, 320), (170, 370), (120, 350)], [(115, 460), (150, 470), (140, 520), (105, 505)],
              [(120, 650), (150, 660), (140, 710), (110, 700)], [(560, 100), (610, 105), (620, 135), (565, 130)],
              [(490, 585), (530, 590), (525, 606), (485, 600)], [(255, 120), (310, 130), (300, 160), (250, 150)]], seed=3)
    m.undercity([(430, 450), (500, 430), (570, 445), (595, 495), (570, 550), (510, 570), (450, 550), (425, 500)])
    era_rings(m, (510, 500), [(58, 50, '1650 sandbar town', 510, 462), (100, 90, '', 0, 0)])
    fabric(m, blob(130, 440, 240, 460, random.Random(2), 0.07, 18), 8,
           blob(220, 380, 360, 560, random.Random(4), 0.06, 18), (500, 500), (330, 700), 20, seed=2)
    m.grid_ticks()
    # ---- network (everything crosses water: bridges are automatic)
    R1 = m.add_road('R1', [(505, 438), (562, 458), (592, 505), (570, 555), (510, 572), (450, 555), (425, 505), (450, 460),
                           (505, 438)], 'ring')
    R2 = m.add_road('R2 Lagoon Ring', [(455, 190), (520, 165), (600, 195), (690, 255), (760, 292), (830, 312), (890, 380),
                                        (915, 470), (912, 570), (890, 655), (830, 725), (760, 775), (690, 805),
                                        (610, 850), (545, 845), (480, 825), (415, 815), (350, 790), (305, 700), (250, 640),
                                        (215, 575), (185, 480), (172, 380), (210, 290), (290, 205), (380, 170), (455, 190)], 'ring')
    m.add_road('N1 Halcyon Causeway', [(505, 412), (506, 340), (503, 290), (500, 215), (500, 130), (500, 40), (500, -20)], 'motorway')
    m.add_road('NE1 Solace Bridge', [(590, 440), (660, 392), (720, 342), (772, 290), (800, 200), (850, 100), (900, -20)], 'motorway')
    m.add_road('E1 Barrier Causeway', [(615, 500), (720, 505), (820, 500), (915, 490)], 'motorway')
    m.add_road('SE1 Port Causeway', [(585, 575), (640, 645), (700, 710), (745, 765)], 'motorway')
    m.add_road('S1 Dam Road', [(500, 575), (488, 680), (472, 760), (452, 815)], 'motorway')
    m.add_road('W1 Aurelian Causeway', [(430, 520), (370, 560), (310, 610), (250, 640), (170, 635), (90, 640), (-20, 650)], 'motorway')
    m.add_road('T1 Freight Viaduct', [(-20, 760), (120, 748), (200, 778), (300, 806), (400, 868), (500, 886), (590, 855),
                                       (660, 810), (740, 770)], 'truck')
    m.add_road('T2 Barrier Spur', [(790, 700), (850, 690), (890, 660), (915, 600)], 'truck')
    arts = [('Island Ring', [(420, 505), (505, 410), (590, 440), (620, 505), (580, 575)], False),
            ('Grand Axis', [(505, 410), (505, 480), (505, 570)], False),
            ('Via Sacra', [(395, 520), (460, 510), (520, 505), (600, 505)], False),
            ('Halcyon Gate', [(500, 290), (560, 240), (590, 220)], False),
            ('Solace Spine', [(715, 300), (780, 300), (840, 295)], True),
            ('Meridian Main', [(640, 770), (700, 775), (760, 790), (830, 790)], True),
            ('Orbital Strip', [(905, 360), (915, 420), (918, 520), (912, 620)], True),
            ('Aurelian Ring', [(190, 600), (250, 580), (310, 620)], False),
            ('Airport Road', [(205, 190), (230, 240), (205, 290)], True),
            ('Quay Road', [(645, 740), (700, 725), (750, 735), (790, 745)], True),
            ('Keep Quay', [(400, 800), (450, 790), (490, 800)], False)]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    m.add_rail('Freight South Main', [(-20, 770), (120, 758), (205, 788), (305, 815), (405, 878), (500, 896), (595, 865),
                                      (665, 820), (730, 785), (790, 760)], 'freight')
    m.add_rail('Orbital Branch', [(790, 740), (850, 705), (890, 670), (915, 620), (925, 560)], 'freight')
    for k in (-6, 6):
        m.add_rail('yard', [(745, 745 + k), (835, 765 + k)], 'freight', smooth=False)
    CN = m.add_rail('C1 North Line', [(520, 492), (512, 420), (508, 330), (502, 250), (500, 140), (505, 40), (505, -20)], 'commuter', tunnels=[(0.18, 0.28)])
    CW = m.add_rail('C2 West Line', [(520, 492), (450, 510), (380, 550), (310, 600), (240, 625), (160, 620), (80, 620), (-20, 610)], 'commuter', tunnels=[(0.3, 0.4)])
    CE = m.add_rail('C3 Barrier Line', [(520, 492), (640, 498), (760, 498), (880, 490), (930, 480)], 'commuter', tunnels=[(0.3, 0.55)])
    CNE = m.add_rail('C4 Solace Line', [(520, 492), (600, 430), (690, 350), (770, 295), (830, 220), (900, 120), (950, -20)], 'commuter', tunnels=[(0.3, 0.5)])
    M1 = m.add_rail('M1 Loop', [(505 + 62 * math.cos(t * 6.2832 / 14), 500 + 52 * math.sin(t * 6.2832 / 14)) for t in range(15)], 'metro')
    M2 = m.add_rail('M2', [(250, 620), (330, 590), (420, 540), (510, 500), (590, 560), (650, 640), (710, 710), (760, 770)], 'metro', tunnels=[(0.05, 0.3), (0.55, 0.8)])
    M3 = m.add_rail('M3', [(452, 800), (480, 700), (500, 600), (510, 500), (505, 400), (502, 300), (500, 220)], 'metro', tunnels=[(0.1, 0.35), (0.6, 0.72)])
    m.draw_rails()
    m.draw_roads()
    m.auto_interchanges()
    m.stations_along(CN, (0.35, 0.5, 0.65, 0.8), 'rail')
    m.stations_along(CW, (0.2, 0.55, 0.75, 0.9), 'rail')
    m.stations_along(CE, (0.2, 0.5, 0.75, 0.97), 'rail')
    m.stations_along(CNE, (0.2, 0.4, 0.6, 0.8), 'rail')
    m.stations_along(M1, [i / 7 for i in range(7)], 'metro')
    m.stations_along(M2, (0.05, 0.2, 0.33, 0.65, 0.78, 0.95), 'metro')
    m.stations_along(M3, (0.05, 0.4, 0.55, 0.8, 0.95), 'metro')
    for p in ((510, 498), (748, 765), (503, 250), (772, 295), (905, 490), (250, 625), (452, 805)):
        m.station(p[0], p[1], 'hub')
    m.station(790, 760, 'freight')
    m.station(925, 560, 'freight')
    # ---- walls, barriers, drones
    corp_walls(m, ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'))
    for run in m.coast_seg(lambda p: p[0] > 840 and 320 < p[1] < 700):
        m.seawall(run)
    for run in m.coast_seg(lambda p: p[1] > 820 and 620 < p[0] < 850):
        m.seawall(run)
    m.dam([(355, 735), (440, 712), (520, 735), (546, 800)])
    m.dam([(546, 800), (520, 870), (440, 892), (370, 866), (342, 800), (355, 735)])
    m.dam([(858, 310), (868, 345)])
    m.dam([(868, 690), (892, 700)])
    m.drone_corridor([(500, 215), (500, 330), (510, 495)])
    m.drone_corridor([(500, 215), (640, 250), (775, 285)])
    m.drone_corridor([(500, 215), (700, 400), (900, 480)])
    m.drone_corridor([(500, 215), (620, 500), (740, 740)])
    m.drone_corridor([(500, 215), (480, 520), (452, 800)])
    m.drone_corridor([(500, 215), (380, 400), (250, 600)])
    m.ferry([(520, 292), (505, 400)])
    m.ferry([(590, 440), (680, 400), (740, 330)])
    m.ferry([(520, 610), (600, 700), (680, 790)])
    m.ferry([(500, 610), (470, 700), (452, 790)])
    m.ferry([(400, 580), (330, 620), (290, 640)])
    m.ferry([(620, 520), (780, 560), (880, 520)])
    m.windfarm([(560, 925), (840, 945), (880, 995), (520, 995)])
    # ---- landmarks
    m.panopticon(508, 215, 33, COL['halcyon'], cone_to=(510, 498))
    m.helix(775, 284, 26, -0.4)
    m.launch_ring(912, 590, 32, 0.0, zone_r=82)
    m.gantry_castle(742, 775, 28, 0.0, cranes=(math.pi * 0.5, math.pi * 0.7), crane_len=1.6)
    m.port_piers([(700, 858, 34, 8, math.pi / 2), (738, 860, 34, 8, math.pi / 2), (776, 856, 34, 8, math.pi / 2)])
    m.circus(240, 620, 32, 0.5)
    m.pier_city(445, 850, 64, math.pi / 2, n=9, spread=2.0)
    m.airport(160, 175, 0.5)
    glyphs(m, [(560, 440, 'stadium'), (500, 520, 'hospital'), (800, 310, 'hospital'), (440, 790, 'hospital'),
               (470, 470, 'university'), (740, 255, 'university'), (280, 590, 'university'),
               (490, 540, 'market'), (555, 480, 'market'), (210, 640, 'market'), (700, 805, 'market'),
               (565, 715, 'power'), (800, 740, 'power'), (905, 28, 'water'), (116, 757, 'sewage'),
               (648, 640, 'cemetery'), (180, 340, 'cemetery'), (178, 150, 'airport'),
               (330, 175, 'datacentre'), (470, 800, 'datacentre'), (440, 510, 'arcology'), (590, 480, 'arcology'),
               (470, 580, 'arcology'), (540, 190, 'megastructure'), (810, 280, 'megastructure'),
               (800, 800, 'megastructure'), (960, 765, 'recycling'), (520, 545, 'rebel'), (420, 480, 'church'),
               (730, 330, 'school')])
    district_labels(m, [('halcyon', 510, 120, 'HALCYON', 21, 0), ('solace', 780, 195, 'SOLACE', 21, 0),
                        ('aurelian', 235, 515, 'AURELIAN CONCORD', 19, 0), ('tethys', 520, 925, 'TETHYS DEEP', 21, 0),
                        ('meridian', 740, 895, 'MERIDIAN', 21, 0), ('orbital', 965, 440, 'ORBITAL', 19, 90),
                        ('centre', 510, 380, 'THE OLD CITY', 22, 0)])
    m.text(520, 555, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(915, 880, 'THE OPEN SEA', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False)
    m.text(620, 330, 'THE LAGOON', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False)
    small_labels(m, [(360, 660, 'FLOODED LOWER TOWN'), (450, 740, 'DROWNED QUARTER'), (650, 600, 'NECROPOLIS'),
                     (565, 745, 'POWER'), (704, 828, 'CONTAINER TERMINAL'), (790, 715, 'MARSHALLING YARD'),
                     (160, 235, 'AIRPORT'), (320, 205, 'DATA CAMPUS'), (905, 70, 'WATERWORKS'),
                     (950, 810, 'LANDFILL'), (130, 400, 'MAINLAND SPRAWL'), (395, 365, 'FORT')])
    shields(m, [(505, 438, 'R1'), (592, 505, 'R1'), (520, 165, 'R2'), (912, 570, 'R2'), (350, 790, 'R2'),
                (503, 300, 'N1'), (700, 360, 'NE1'), (820, 500, 'E1'), (680, 690, 'SE1'), (488, 680, 'S1'),
                (120, 640, 'W1'), (300, 806, 'T1'), (870, 690, 'T2')])
    wind(m, 700, 40, 0.3)
    m.scalebar(40, 965)
    m.north(955, 965)
    m.title_block(34, 38, 'D  -  DROWNED DELTA', 'archipelago city  /  every district an island  /  causeways and tunnels')
    return m


EVO = [
    ('c.1500', 'Fishing town on a sandbar in a river delta; nearby clay hills, farmed polders and a marshy mainland shore.'),
    ('1700-1890', 'Sandbar town grows along tidal creeks; rail arrives on a causeway from the mainland; mainland polder grid.'),
    ('1950-1990', 'Causeways and a lagoon ring road tie the islands together. Highways cut across the old sandbar and the mainland sprawl.'),
    ('2040+', 'Corps colonise the islands: Halcyon on the hill island, Solace on the terraced island, Aurelian on the seven-hills island, Orbital on the barrier spit facing open sea, Meridian on reclaimed land.'),
    ('2070-2100', 'Sea-level rise drowns the low floodplain between islands; Tethys builds a dammed keep and pier city over the drowned quarter.'),
    ('always', 'Informal housing clings to the mainland shore and the causeway heads; everything crosses water by bridge or tunnel.'),
]


META = dict(
    key='D', slug='D_delta_archipelago', title='D - DROWNED DELTA',
    subtitle='Archipelago city: seven islands in a flooded lagoon',
    blurb=['The old delta floodplain drowned: hills became islands.', 'Each district is an island node, linked by',
           'causeways, bridges and tunnels; checkpoints at bridgeheads.'],
    skip=set(),
    evo=EVO,
    notes={
        'halcyon': 'Surveillance. Hill island north, sees every bridge.',
        'solace': 'Biotech. Terraced campus island, NE.',
        'orbital': 'Aerospace. Barrier-island spit; launches east.',
        'meridian': 'Freight. Reclaimed port island, SE.',
        'aurelian': 'Finance/politics. Seven-hills island, west.',
        'tethys': 'Ocean tech. Dammed keep, pier city, drowned quarter.',
    },
)
