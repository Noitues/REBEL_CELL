"""Design E - HEADLAND HILLS. A hilly peninsula between open ocean and a bay, bridged to the mainland."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from citymap import COL, CityMap, tint
from common import (NEU, corp_walls, district_labels, era_rings, fabric, glyphs, shields, slums, small_labels, wind)
from geom import blob, offset_line

OUT = os.path.join(os.path.dirname(__file__), '..')

PEN = [(110, 1060), (120, 900), (100, 800), (115, 700), (105, 600), (115, 500), (105, 400), (125, 300), (150, 220),
       (200, 150), (270, 110), (350, 95), (430, 88), (500, 100), (560, 128), (610, 168), (660, 225), (700, 285),
       (715, 355), (722, 425), (716, 500), (706, 570), (692, 630), (700, 700), (728, 775), (768, 845), (798, 900),
       (830, 1060)]
EAST = [(940, -60), (1060, -60), (1060, 1060), (900, 1060), (905, 900), (930, 800), (925, 650), (910, 500), (925, 350),
        (950, 200), (945, 60)]
NORTH = [(-60, -60), (1060, -60), (1060, 40), (700, 60), (500, 40), (300, 22), (100, 50), (-60, 70)]


def build():
    m = CityMap(seed=51)
    m.set_islands([(PEN, True), (EAST, True), (NORTH, True)], noise_amp=3.5)
    bumps = [(358, 645, 85, 85, 1.0, 0.0), (400, 450, 60, 190, 0.55, 0.0), (260, 205, 70, 60, 0.5, 0.0),
             (360, 250, 22, 22, 0.52, 0), (410, 300, 22, 22, 0.5, 0), (445, 340, 22, 22, 0.48, 0),
             (385, 335, 20, 20, 0.45, 0), (335, 300, 20, 20, 0.42, 0), (470, 262, 20, 20, 0.40, 0),
             (440, 215, 20, 20, 0.38, 0), (1000, 500, 100, 300, 0.6, 0), (500, -20, 300, 50, 0.6, 0),
             (180, 850, 70, 100, 0.35, 0), (560, 900, 120, 80, 0.2, 0.0)]
    m.base(bumps)
    m.lake([(300, 470), (335, 458), (360, 478), (345, 505), (308, 500)])
    m.sunken([(690, 250), (765, 262), (792, 332), (772, 412), (716, 424), (712, 330)], seed=4, grid_angle=10)
    # ---- districts
    centre = m.zone('centre', [(445, 470), (480, 425), (560, 410), (640, 420), (705, 445), (715, 520), (705, 590),
                               (650, 630), (570, 640), (490, 615), (450, 550)], COL['centre'], 0.30)
    teth = m.zone('tethys', [(585, 235), (640, 215), (700, 265), (716, 345), (715, 400), (650, 405), (600, 370),
                             (580, 300)], COL['tethys'], 0.24, smooth=False)
    aur = m.zone('aurelian', [(330, 225), (400, 200), (480, 225), (520, 290), (510, 360), (440, 395), (370, 375),
                              (330, 310)], COL['aurelian'], 0.24)
    sol = m.zone('solace', [(150, 215), (210, 150), (280, 120), (350, 110), (380, 160), (370, 230), (300, 275),
                            (210, 285)], COL['solace'], 0.24)
    orb = m.zone('orbital', [(118, 420), (190, 400), (260, 440), (275, 540), (250, 630), (170, 650), (118, 600)],
                 COL['orbital'], 0.24, smooth=False)
    halc = m.zone('halcyon', [(290, 590), (350, 555), (425, 575), (450, 640), (425, 710), (350, 730), (290, 690),
                              (272, 640)], COL['halcyon'], 0.26, smooth=False)
    mer = m.zone('meridian', [(520, 690), (600, 670), (680, 690), (725, 740), (752, 810), (720, 850), (640, 850),
                              (560, 820), (515, 760)], COL['meridian'], 0.24, smooth=False)
    cc = tint(COL['centre'], 0.25)
    m.tex_grid(centre, 12, 7.5, 6.5, jitter=0.35, warp_amp=7, warp_wl=70, gap=0.25, major=5, color=cc, a_minor=0.45,
               a_major=0.75, seed=1)
    m.tex_walks(centre, 120, (25, 70), 0.35, color=cc, a=0.5, seed=1)
    m.tex_super(teth, 10, 24, tint(COL['tethys'], 0.3), seed=6)
    m.tex_radial(aur, (430, 300), 12, 90, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, -8, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_curvi(sol, (270, 190), 15, 130, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=50, seed=3)
    m.tex_super(orb, 0, 36, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.55)
    m.tex_super(halc, 30, 28, tint(COL['halcyon'], 0.3), seed=2)
    m.tex_super(mer, 5, 36, tint(COL['meridian'], 0.3), seed=7)
    # ---- parks, civic, industry
    m.park([(120, 350), (320, 340), (335, 380), (120, 392)], seed=1, free=True, smooth=False)       # the great park
    m.park([(120, 760), (200, 740), (230, 880), (130, 900)], seed=2, free=True)
    m.park([(420, 740), (500, 735), (520, 800), (430, 820)], seed=3, free=True)
    m.park([(560, 850), (700, 860), (730, 910), (590, 920)], seed=4, free=True)
    m.park([(180, 60), (300, 70), (320, 110), (190, 100)], seed=5, free=True)
    m.park([(460, 530), (500, 520), (510, 560), (470, 570)], seed=6, a=0.7)
    m.park([(590, 450), (630, 445), (640, 490), (600, 495)], seed=7, a=0.7)
    m.park([(910, 100), (1000, 90), (1010, 200), (930, 210)], seed=8, free=True)
    m.park([(940, 640), (1000, 620), (1010, 760), (950, 790)], seed=9, free=True)
    m.built([(320, 440), (350, 430), (365, 455), (335, 465)], (110, 120, 110), 0.7, free=True)
    m.plaza([(560, 490), (590, 490), (590, 516), (560, 516)])
    m.plaza([(405, 285), (433, 285), (433, 310), (405, 310)])
    term = m.built([(660, 740), (722, 745), (742, 800), (670, 805)], (110, 120, 138), 0.55)
    m.container_yard(700, 775, 70, 55, 0.1, clip=term)
    m.built([(560, 725), (650, 715), (655, 740), (565, 750)], (60, 64, 76), 0.8)
    m.industry([(560, 770), (640, 775), (635, 835), (565, 815)], seed=2, free=False, angle=5)
    m.industry([(690, 860), (780, 880), (790, 930), (700, 925)], seed=3, angle=10)
    m.built([(750, 925), (790, 930), (788, 960), (748, 955)], (90, 96, 112), 0.7, free=True)      # power
    m.built([(280, 20), (340, 18), (345, 55), (285, 58)], (70, 90, 100), 0.7, free=True)          # data (north shore)
    m.built([(780, 990), (830, 995), (828, 1020), (778, 1015)], (130, 110, 90), 0.6, free=True)  # sewage
    m.built([(500, 900), (680, 905), (690, 960), (510, 965)], (40, 46, 60), 0.85, free=True)      # airport
    m.built([(930, 540), (980, 535), (990, 585), (940, 595)], (100, 130, 90), 0.6, free=True)    # recycling
    for i, (tx, ty, tr, nm) in enumerate([(965, 420, 14, 'EAST SHORE'), (955, 250, 12, ''), (960, 700, 14, 'BAYVIEW'),
                                           (985, 900, 12, '')]):
        m.town(tx, ty, tr, seed=i, name=nm)
    slums(m, [[(280, 460), (320, 490), (300, 540), (265, 520)], [(480, 640), (520, 650), (515, 685), (470, 675)],
              [(120, 660), (165, 670), (160, 720), (115, 710)], [(520, 330), (560, 340), (550, 385), (510, 375)],
              [(590, 860), (650, 880), (630, 905), (585, 890)], [(935, 380), (985, 395), (975, 440), (930, 425)],
              [(450, 880), (495, 890), (490, 920), (440, 910)]], seed=3)
    m.undercity([(480, 460), (550, 440), (640, 455), (680, 505), (660, 580), (580, 600), (500, 580), (470, 520)])
    era_rings(m, (580, 525), [(60, 52, '1790 harbour town', 580, 492), (108, 90, '', 0, 0)])
    fabric(m, blob(560, 540, 230, 190, random.Random(2), 0.08, 18), 12,
           blob(400, 620, 360, 520, random.Random(4), 0.06, 18), (420, 520), (260, 640), 18, seed=2)
    m.grid_ticks()
    # ---- network
    ring = [(580 + 118 * math.cos(t * 6.2832 / 16), 525 + 92 * math.sin(t * 6.2832 / 16)) for t in range(17)]
    m.add_road('R1', ring, 'ring')
    H2 = m.add_road('H2 Bayshore Freeway', [(760, 1020), (790, 900), (735, 800), (705, 720), (690, 650), (700, 560), (705, 480),
                                              (695, 400), (690, 330), (650, 260), (600, 190), (550, 130), (480, 100), (420, 92),
                                              (395, 40), (375, -20)], 'ring')
    H3 = m.add_road('H3 Coast Highway', [(190, 1020), (170, 900), (160, 800), (170, 700), (150, 600), (155, 500), (165, 400),
                                           (180, 300), (215, 230), (280, 180), (350, 150), (400, 115), (408, 90)], 'ring')
    m.add_road('H1 Skyline Highway', [(430, 1020), (425, 900), (415, 800), (430, 740), (462, 670), (468, 590), (452, 520),
                                        (428, 440), (412, 370), (405, 300), (392, 230), (386, 160), (392, 100)], 'motorway')
    m.add_road('X1 South Cross', [(160, 700), (260, 722), (340, 745), (430, 745), (520, 760), (610, 770), (710, 790)], 'motorway')
    m.add_road('X2 Bay Bridge', [(155, 500), (250, 510), (330, 520), (400, 520), (460, 520), (540, 520), (620, 520), (705, 520),
                                  (760, 500), (840, 490), (930, 480), (1020, 470)], 'motorway', tunnels=[(0.12, 0.3)])
    m.add_road('X3 North Cross', [(190, 260), (280, 270), (350, 300), (420, 300), (500, 285), (590, 275), (680, 280)], 'motorway')
    m.add_road('T1 Port Road', [(600, 770), (650, 745), (690, 705), (700, 660)], 'truck')
    m.add_road('T2 Freight Expressway', [(660, 820), (700, 900), (740, 1000), (760, 1060)], 'truck')
    arts = [('Embarcadero', [(640, 440), (700, 470), (706, 540), (680, 600)], False),
            ('Market Street', [(470, 480), (530, 500), (600, 520), (660, 540)], False),
            ('Grand Axis', [(580, 420), (580, 520), (580, 620)], False),
            ('Halcyon Rd', [(430, 590), (470, 560), (520, 540)], False),
            ('Orbital Blvd', [(125, 560), (200, 520), (260, 500)], True),
            ('Solace Drive', [(200, 200), (270, 220), (340, 240)], True),
            ('Aurelian Ave', [(340, 260), (420, 250), (500, 270)], False),
            ('Tethys Quay', [(640, 330), (700, 330), (730, 330)], True),
            ('Meridian Main', [(530, 740), (610, 740), (690, 745)], True),
            ('Airport Rd', [(560, 800), (560, 900), (570, 940)], True),
            ('Corporate Ave', [(450, 420), (500, 380), (580, 330)], True),
            ('Mission Rd', [(540, 640), (540, 690)], False)]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    m.add_rail('Freight Peninsula Main', [(790, 1060), (780, 980), (740, 900), (715, 850), (675, 805), (635, 775), (600, 760)], 'freight')
    m.add_rail('Orbital Tunnel Freight', [(600, 760), (520, 765), (440, 755), (360, 745), (290, 748), (210, 700), (180, 640), (190, 570), (195, 530)],
               'freight', tunnels=[(0.35, 0.75)])
    for k in (-6, 6):
        m.add_rail('yard', [(570, 755 + k), (655, 748 + k)], 'freight', smooth=False)
    CP = m.add_rail('C1 Peninsula Line', [(760, 1060), (760, 950), (730, 860), (700, 780), (690, 700), (670, 640), (620, 590)], 'commuter')
    CG = m.add_rail('C2 Gate Line', [(600, 560), (660, 430), (690, 340), (640, 260), (580, 180), (500, 120), (430, 95), (400, 40), (390, -20)], 'commuter')
    CT = m.add_rail('C3 Transbay Line', [(600, 560), (700, 520), (800, 510), (900, 490), (1020, 480)], 'commuter', tunnels=[(0.3, 0.8)])
    M1 = m.add_rail('M1', [(260, 190), (330, 250), (420, 330), (500, 430), (560, 520), (520, 590), (430, 650), (360, 650)], 'metro', tunnels=[(0.45, 0.8)])
    M2 = m.add_rail('M2', [(190, 520), (300, 520), (420, 520), (560, 525), (640, 470), (690, 380), (700, 330)], 'metro', tunnels=[(0.1, 0.4)])
    M3 = m.add_rail('M3', [(610, 760), (600, 680), (585, 600), (570, 525), (520, 430), (470, 330), (430, 260)], 'metro')
    m.draw_rails()
    m.draw_roads()
    m.auto_interchanges()
    m.stations_along(CP, (0.25, 0.45, 0.65, 0.82, 0.95), 'rail')
    m.stations_along(CG, (0.12, 0.3, 0.45, 0.6, 0.75, 0.9), 'rail')
    m.stations_along(CT, (0.2, 0.6, 0.98), 'rail')
    m.stations_along(M1, (0.08, 0.2, 0.35, 0.55, 0.7, 0.85, 0.97), 'metro')
    m.stations_along(M2, (0.08, 0.25, 0.4, 0.6, 0.75, 0.95), 'metro')
    m.stations_along(M3, (0.08, 0.25, 0.45, 0.6, 0.8, 0.95), 'metro')
    for p in ((590, 555), (610, 762), (690, 340), (430, 262), (195, 525), (358, 640)):
        m.station(p[0], p[1], 'hub')
    m.station(600, 760, 'freight')
    # ---- walls, defences, drones
    corp_walls(m, ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'))
    for run in m.coast_seg(lambda p: 700 > p[0] > 600 and 220 < p[1] < 800 or (p[0] > 700 and 300 < p[1] < 880 and p[0] < 800)):
        m.seawall(run)
    for run in m.coast_seg(lambda p: p[0] < 140 and 380 < p[1] < 680):
        m.seawall(run)
    m.dam([(700, 265), (770, 262), (793, 335), (772, 412), (716, 426)])
    m.dam([(405, 93), (392, 56)])
    m.dam([(775, 770), (800, 800)])
    m.drone_corridor([(358, 640), (460, 590), (580, 525)])
    m.drone_corridor([(358, 640), (400, 500), (430, 300)])
    m.drone_corridor([(358, 640), (500, 450), (640, 330)])
    m.drone_corridor([(358, 640), (500, 700), (640, 770)])
    m.drone_corridor([(358, 640), (270, 600), (190, 530)])
    m.drone_corridor([(430, 300), (350, 240), (280, 195)])
    m.ferry([(706, 540), (800, 545), (905, 540)])
    m.ferry([(716, 330), (820, 300), (920, 280)])
    m.ferry([(705, 650), (800, 700), (905, 740)])
    m.windfarm([(8, 140), (85, 160), (80, 340), (8, 340)])
    m.windfarm([(8, 690), (85, 700), (80, 990), (8, 990)])
    # ---- landmarks
    m.panopticon(358, 640, 33, COL['halcyon'], cone_to=(580, 525))
    m.helix(268, 192, 26, -0.4)
    m.launch_ring(190, 525, 32, math.pi, zone_r=88)
    m.gantry_castle(640, 775, 28, 0.0, cranes=(0.1, 0.5), crane_len=1.7)
    m.port_piers([(722, 738, 38, 8, 0.15), (738, 772, 38, 8, 0.3), (757, 806, 38, 8, 0.45)])
    m.circus(430, 300, 32, 0.2)
    m.pier_city(738, 330, 62, 0.0, n=9, spread=2.0)
    m.airport(600, 935, 0.0)
    glyphs(m, [(640, 470, 'stadium'), (570, 540, 'hospital'), (230, 200, 'hospital'), (740, 400, 'hospital'),
               (520, 450, 'university'), (330, 140, 'university'), (350, 340, 'university'),
               (545, 480, 'market'), (610, 580, 'market'), (440, 270, 'market'), (700, 760, 'market'),
               (770, 942, 'power'), (630, 740, 'power'), (330, 482, 'water'), (805, 1004, 'sewage'),
               (340, 450, 'cemetery'), (965, 565, 'cemetery'), (590, 920, 'airport'),
               (312, 38, 'datacentre'), (640, 270, 'datacentre'), (490, 540, 'arcology'), (660, 570, 'arcology'),
               (545, 400, 'arcology'), (400, 580, 'megastructure'), (310, 170, 'megastructure'),
               (660, 800, 'megastructure'), (955, 565, 'recycling'), (590, 560, 'rebel'), (500, 500, 'church'),
               (300, 190, 'school')])
    district_labels(m, [('halcyon', 360, 765, 'HALCYON', 21, 0), ('solace', 255, 90, 'SOLACE', 21, 0),
                        ('aurelian', 420, 185, 'AURELIAN CONCORD', 19, 0), ('tethys', 790, 230, 'TETHYS DEEP', 20, -40),
                        ('meridian', 618, 700, 'MERIDIAN', 21, 0), ('orbital', 62, 530, 'ORBITAL', 21, 90),
                        ('centre', 580, 400, 'THE OLD CITY', 22, 0)])
    m.text(590, 565, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(50, 760, 'THE OUTER OCEAN', 14, (150, 200, 235), spacing=8, weight='SemiBold', halo=False, angle=90)
    m.text(830, 640, 'THE BAY', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False, angle=90)
    m.text(600, 62, 'GATE STRAIT', 10, (150, 200, 235), spacing=4, weight='SemiBold', halo=False)
    small_labels(m, [(700, 790, 'CONTAINER TERMINAL'), (610, 755, 'YARDS'), (230, 365, 'THE GREAT PARK'),
                     (335, 435, 'NECROPOLIS'), (590, 960, 'AIRPORT'), (310, 70, 'DATA CAMPUS'),
                     (480, 655, 'THE MISSION'), (330, 485, 'RESERVOIR'), (960, 320, 'EAST SHORE'),
                     (700, 870, 'POWER'), (150, 820, 'DUNES'), (495, 345, 'FLATIRON SLUMS')])
    shields(m, [(760, 1020, 'H2'), (690, 330, 'H2'), (190, 1020, 'H3'), (170, 400, 'H3'), (430, 1000, 'H1'),
                (468, 590, 'H1'), (260, 722, 'X1'), (330, 520, 'X2'), (920, 480, 'X2'), (500, 285, 'X3'),
                (660, 445, 'R1'), (640, 770, 'T1'), (740, 1000, 'T2')])
    wind(m, 340, 800, 0.0)
    m.scalebar(40, 965)
    m.north(955, 965)
    m.title_block(34, 38, 'E  -  HEADLAND HILLS', 'hilly peninsula  /  open ocean west, bay east  /  big bridges to the mainland')
    return m


EVO = [
    ('c.1770', 'Mission and harbour on the sheltered bay side of a hilly peninsula; open ocean and dunes on the west.'),
    ('1850-1900', 'Harbour town on the bayshore flats; street grid forced straight over the hills; first rail arrives from the south.'),
    ('1930-1990', 'Great bridges north and east; bayshore and coast freeways; the Skyline highway climbs the ridge. A tunnel links the ocean flats to downtown.'),
    ('2040+', 'Corps take the hills and flats: Halcyon on the highest peak, Aurelian on the seven hills, Solace on the wooded headland, Orbital on the ocean flats, Meridian on the SE bay port, Tethys on the NE bay flats.'),
    ('2080+', 'Bay level rises: the NE bay flats drown behind dams and the Gate Strait gets a surge barrier. Pier city goes up.'),
    ('always', 'Informal quarters wedge into ravines and rail yards; towns spread across the bay on the East Shore.'),
]


META = dict(
    key='E', slug='E_headland_hills', title='E - HEADLAND HILLS',
    subtitle='Hilly peninsula between open ocean and a bay',
    blurb=['A ridge runs down a peninsula. Old harbour on the', 'bay side, outer-coast flats for the spaceport,',
           'bridges north and east, rail from the south.'],
    skip=set(),
    evo=EVO,
    notes={
        'halcyon': 'Surveillance. Highest peak, south; sees the bay.',
        'solace': 'Biotech. Wooded NW headland campus.',
        'orbital': 'Aerospace. Outer-coast flats, launches west.',
        'meridian': 'Freight. SE bay port, rail from the south.',
        'aurelian': 'Finance/politics. Seven hills, north-centre.',
        'tethys': 'Ocean tech. Drowned NE bay flats, pier city.',
    },
)
