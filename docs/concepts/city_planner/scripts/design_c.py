"""Design C - MEANDER. A river city: old town on an omega meander island, estuary port, hills and bridges."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from citymap import COL, CityMap, tint
from common import (NEU, corp_walls, district_labels, era_rings, fabric, glyphs, shields, slums, small_labels, wind)
from geom import arc_pts, blob, offset_line

OUT = os.path.join(os.path.dirname(__file__), '..')


def build():
    m = CityMap(seed=31)
    coast = [(110, -50), (135, 120), (150, 260), (160, 380), (150, 470), (130, 540), (150, 590), (145, 640), (140, 700),
             (165, 780), (250, 850), (360, 895), (500, 920), (650, 930), (800, 920), (900, 895), (1000, 870)]
    m.set_ocean(coast, [(1100, 870), (1100, 1100), (-100, 1100), (-100, -50)], noise_amp=4.0)
    bumps = [(1000, 40, 230, 200, 1.0, 0.0), (700, -20, 200, 90, 0.7, 0), (535, 265, 62, 52, 0.95, 0.0),
             (770, 262, 80, 60, 0.5, 0.0), (322, 320, 120, 100, 0.2, 0.0),
             (280, 290, 24, 24, 0.40, 0), (330, 270, 24, 24, 0.38, 0), (360, 320, 24, 24, 0.36, 0),
             (300, 350, 22, 22, 0.34, 0), (255, 330, 22, 22, 0.32, 0), (345, 360, 20, 20, 0.30, 0),
             (930, 520, 70, 160, 0.35, 0), (860, 800, 120, 60, 0.18, 0), (250, 120, 160, 80, 0.45, 0.2)]
    m.base(bumps)
    river = m.river([(1030, 60), (960, 140), (900, 210), (870, 300), (800, 370), (730, 378), (672, 408), (652, 470),
                     (648, 540), (612, 590), (545, 618), (470, 618), (420, 580), (408, 510), (412, 450), (440, 415),
                     (390, 405), (330, 422), (270, 470), (215, 540), (180, 590), (150, 640)], 4.0, 22.0, jitter=1.5)
    # neck canal across the meander + canal rings in the old town
    m.river([(672, 408), (600, 410), (520, 412), (440, 415)], 5.5, 5.5, smooth=True, bank=True)
    for r in (34, 60, 88):
        m.river(arc_pts(535, 540, r, math.radians(185), math.radians(355), 22), 2.4, 2.4, smooth=False)
    m.river([(535, 452), (535, 618)], 2.4, 2.4, smooth=False)
    m.lake([(880, 90), (925, 80), (960, 105), (940, 140), (895, 135)])
    m.drowned([(150, 478), (200, 468), (238, 500), (218, 548), (178, 582), (148, 576)], seed=4, over_ocean=True, grid_angle=18)
    # ---- districts
    centre = m.zone('centre', [(415, 470), (430, 428), (500, 418), (580, 422), (640, 438), (652, 520), (628, 585),
                               (560, 612), (480, 610), (425, 572), (408, 520)], COL['centre'], 0.30)
    halc = m.zone('halcyon', [(470, 208), (540, 188), (610, 214), (632, 272), (592, 330), (522, 346), (466, 310),
                              (450, 255)], COL['halcyon'], 0.26, smooth=False)
    sol = m.zone('solace', [(690, 218), (770, 198), (840, 228), (856, 290), (800, 330), (722, 326), (680, 276)],
                 COL['solace'], 0.24)
    aur = m.zone('aurelian', [(250, 250), (330, 232), (395, 278), (400, 350), (345, 402), (280, 390), (240, 330)],
                 COL['aurelian'], 0.24)
    mer = m.zone('meridian', [(180, 618), (270, 588), (350, 602), (395, 652), (380, 742), (300, 790), (215, 762),
                              (165, 692)], COL['meridian'], 0.24, smooth=False)
    teth = m.zone('tethys', [(150, 425), (215, 418), (262, 470), (240, 505), (195, 470), (152, 478)],
                  COL['tethys'], 0.24, smooth=False)
    orb = m.zone('orbital', [(560, 822), (650, 800), (760, 810), (840, 850), (830, 895), (740, 918), (640, 925),
                             (570, 885)], COL['orbital'], 0.24, smooth=False)
    cc = tint(COL['centre'], 0.25)
    m.tex_grid(centre, 12, 7.5, 6.5, jitter=0.3, warp_amp=6, warp_wl=60, gap=0.2, major=5, color=cc, a_minor=0.45,
               a_major=0.75, seed=1)
    m.tex_walks(centre, 110, (25, 70), 0.35, color=cc, a=0.5, seed=1)
    m.tex_super(halc, -6, 30, tint(COL['halcyon'], 0.3), seed=2)
    m.tex_curvi(sol, (770, 262), 15, 120, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=50, seed=3)
    m.tex_radial(aur, (338, 372), 12, 90, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, 15, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_super(mer, 38, 34, tint(COL['meridian'], 0.3), seed=7)
    m.tex_super(teth, 18, 20, tint(COL['tethys'], 0.3), seed=6)
    m.tex_super(orb, 0, 40, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.5)
    # ---- parks, civic, industry
    m.park(m.strip_poly(river, 16, 0.50, 0.70), seed=1, free=True, smooth=False)     # floodplain park downstream
    m.park(m.strip_poly(river, 18, 0.05, 0.30), seed=11, free=True, smooth=False)    # upstream gorge woods
    m.park([(560, 40), (700, 60), (760, 140), (620, 170), (540, 120)], seed=2, free=True)
    m.park([(60, 120), (140, 100), (160, 220), (70, 230)], seed=3, free=True)
    m.park([(420, 790), (520, 770), (560, 840), (470, 860)], seed=4, free=True)
    m.park([(880, 380), (960, 360), (990, 440), (900, 470)], seed=5, free=True)
    m.park([(700, 640), (780, 620), (820, 700), (730, 720)], seed=6, free=True)
    m.park([(445, 505), (480, 495), (490, 540), (452, 548)], seed=7, a=0.7)
    m.park([(580, 500), (620, 495), (628, 545), (588, 552)], seed=8, a=0.7)
    m.park([(715, 232), (760, 225), (772, 262), (730, 270)], seed=9)
    m.built([(556, 628), (590, 622), (600, 660), (565, 668)], (110, 120, 110), 0.7, free=True)
    m.built([(762, 410), (800, 404), (806, 440), (768, 446)], (110, 120, 110), 0.7, free=True)
    m.plaza([(520, 480), (548, 480), (548, 506), (520, 506)])
    m.plaza([(318, 400), (352, 400), (352, 425), (318, 425)])
    term = m.built([(200, 640), (300, 628), (305, 670), (205, 685)], (110, 120, 138), 0.55)
    m.container_yard(252, 656, 95, 36, -0.12, clip=term)
    m.built([(300, 690), (390, 680), (392, 712), (305, 722)], (60, 64, 76), 0.8)
    m.industry([(215, 730), (310, 745), (350, 735), (330, 700), (240, 690)], seed=2, free=False, angle=35)
    m.industry([(660, 575), (720, 560), (770, 600), (720, 640), (670, 625)], seed=3, angle=20)
    m.built([(310, 860), (350, 868), (345, 892), (305, 884)], (90, 96, 112), 0.7, free=True)   # power
    m.built([(940, 150), (990, 140), (996, 190), (946, 196)], (70, 90, 100), 0.7, free=True)   # data
    m.built([(190, 800), (230, 810), (226, 836), (185, 828)], (130, 110, 90), 0.6, free=True)  # sewage
    m.built([(930, 640), (975, 650), (968, 690), (925, 678)], (100, 130, 90), 0.6, free=True)  # recycling
    m.built([(842, 478), (940, 456), (968, 520), (900, 572), (842, 540)], (40, 46, 60), 0.85, free=True)  # airport
    for i, (tx, ty, tr, nm) in enumerate([(800, 120, 14, 'UPPERBANK'), (940, 330, 16, 'HIGH MILL'),
                                           (860, 650, 16, 'EASTFIELD'), (250, 130, 14, 'NORTHWOOD'),
                                           (460, 810, 14, 'SOUTHEND')]):
        m.town(tx, ty, tr, seed=i, name=nm)
    slums(m, [[(640, 640), (700, 660), (690, 700), (630, 690)], [(405, 640), (440, 650), (440, 690), (400, 680)],
              [(420, 330), (470, 350), (460, 395), (415, 380)], [(655, 360), (700, 345), (710, 375), (665, 392)],
              [(600, 700), (650, 720), (640, 760), (590, 740)], [(160, 380), (200, 395), (190, 420), (155, 410)],
              [(700, 500), (740, 520), (730, 560), (690, 545)]], seed=5)
    m.undercity([(455, 460), (520, 450), (590, 465), (610, 520), (590, 575), (520, 590), (460, 565), (440, 515)])
    era_rings(m, (530, 520), [(60, 52, '1500 island town', 530, 488), (112, 98, '', 0, 0)])
    fabric(m, blob(530, 520, 270, 240, random.Random(2), 0.08, 18), 12,
           blob(520, 500, 470, 440, random.Random(4), 0.06, 18), (530, 520), (260, 600), 20, seed=2)
    m.grid_ticks()
    # ---- network
    R1 = m.add_road('R1', [(530, 668), (460, 655), (395, 610), (362, 540), (372, 460), (420, 395), (500, 372), (580, 372),
                           (650, 392), (700, 440), (708, 520), (690, 590), (640, 650), (580, 668), (530, 668)], 'ring')
    R2 = m.add_road('R2', [(170, 215), (260, 160), (400, 120), (540, 110), (700, 125), (840, 150), (930, 215), (975, 330),
                           (985, 460), (968, 590), (935, 700), (880, 770), (830, 790), (740, 785), (650, 780),
                           (560, 775), (480, 770), (430, 790), (370, 820), (300, 842), (232, 822)], 'ring')
    m.add_road('N1 Halcyon Radial', [(530, 392), (532, 350), (535, 270), (538, 190), (540, 110)], 'motorway')
    m.add_road('NW1 Aurelian Way', [(425, 440), (395, 398), (345, 345), (300, 295), (240, 250), (170, 215)], 'motorway')
    m.add_road('NE1 Solace Parkway', [(640, 420), (690, 380), (740, 335), (770, 275), (800, 200), (840, 150)], 'motorway')
    m.add_road('E1 Airport Highway', [(690, 520), (780, 520), (870, 520), (985, 480)], 'motorway')
    m.add_road('SE1 Orbital Highway', [(620, 640), (645, 700), (662, 770), (690, 830), (700, 905)], 'motorway')
    m.add_road('SW1 Port Expressway', [(445, 650), (400, 668), (340, 690), (270, 705), (200, 700)], 'motorway')
    m.add_road('W1 Delta Link', [(380, 500), (330, 505), (280, 505), (230, 495), (190, 480), (152, 470)], 'motorway')
    m.add_road('T1 River Port Road', [(215, 652), (260, 646), (320, 652), (380, 648), (440, 650), (520, 668)], 'truck')
    m.add_road('T2 Rocket Freight', [(330, 705), (420, 712), (520, 745), (620, 772), (700, 790)], 'truck')
    arts = [('Embankment Road', [(425, 572), (480, 590), (545, 598), (612, 575)], False),
            ('Grand Canal Street', [(440, 400), (520, 396), (600, 396), (668, 392)], False),
            ('Island Spine', [(535, 420), (535, 480), (535, 560), (535, 610)], False),
            ('Canal Ring Way', [(430, 520), (470, 520), (535, 520), (600, 520), (650, 520)], False),
            ('Halcyon Gate', [(575, 372), (585, 330), (580, 270)], False),
            ('Aurelian Embankment', [(250, 420), (300, 408), (360, 400)], True),
            ('Solace Spine', [(700, 300), (760, 300), (820, 290)], True),
            ('Meridian Main', [(190, 660), (260, 700), (330, 730), (380, 740)], True),
            ('Orbital Blvd', [(580, 880), (660, 870), (740, 880), (820, 870)], True),
            ('Estuary Road', [(215, 540), (200, 600), (190, 660)], False),
            ('Airport Link', [(850, 520), (890, 500)], True),
            ('Tethys Quay', [(160, 470), (180, 520), (200, 560)], False)]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    m.add_rail('Freight Valley Main', [(1020, 400), (900, 480), (800, 560), (700, 650), (630, 705), (520, 722), (440, 712), (380, 682),
                                       (330, 655), (280, 628), (230, 605)], 'freight')
    m.add_rail('Orbital Branch', [(700, 650), (690, 720), (672, 790), (655, 840)], 'freight')
    for k in (-6, 6):
        m.add_rail('yard', [(205, 655 + k), (300, 640 + k)], 'freight', smooth=False)
    CN = m.add_rail('C1 North Line', [(520, 495), (500, 420), (480, 340), (440, 250), (400, 150), (380, 0)], 'commuter')
    CE = m.add_rail('C2 East Line', [(520, 495), (620, 480), (720, 470), (800, 480), (880, 520)], 'commuter')
    CW = m.add_rail('C3 Delta Line', [(520, 495), (440, 500), (370, 500), (300, 505), (230, 495), (170, 470)], 'commuter')
    CS = m.add_rail('C4 South Line', [(520, 495), (540, 580), (580, 680), (600, 760), (610, 830)], 'commuter')
    M1 = m.add_rail('M1', [(330, 372), (390, 420), (460, 470), (535, 500), (610, 540), (660, 600), (720, 640)], 'metro', tunnels=[(0.3, 0.75)])
    M2 = m.add_rail('M2', [(535, 270), (535, 350), (535, 430), (535, 500), (535, 570), (520, 640), (480, 700), (400, 730), (330, 720)], 'metro',
                    tunnels=[(0.35, 0.7)])
    M3 = m.add_rail('M3', [(180, 480), (250, 500), (340, 505), (440, 505), (535, 500), (640, 490), (740, 460)], 'metro')
    m.draw_rails()
    m.draw_roads()
    m.auto_interchanges()
    m.stations_along(CN, (0.15, 0.3, 0.45, 0.6, 0.75, 0.9), 'rail')
    m.stations_along(CE, (0.25, 0.5, 0.75, 0.97), 'rail')
    m.stations_along(CW, (0.3, 0.55, 0.8, 0.97), 'rail')
    m.stations_along(CS, (0.25, 0.5, 0.75, 0.95), 'rail')
    m.stations_along(M1, (0.08, 0.2, 0.32, 0.65, 0.8, 0.95), 'metro')
    m.stations_along(M2, (0.08, 0.2, 0.35, 0.65, 0.78, 0.9, 0.97), 'metro')
    m.stations_along(M3, (0.1, 0.25, 0.4, 0.65, 0.8, 0.95), 'metro')
    for p in ((535, 500), (700, 650), (880, 520), (535, 330), (200, 655), (170, 470)):
        m.station(p[0], p[1], 'hub')
    m.station(230, 605, 'freight')
    m.station(655, 840, 'freight')
    # ---- walls, defences, drones
    corp_walls(m, ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'))
    for run in m.coast_seg(lambda p: p[1] > 590 or (p[1] > 300 and p[0] < 170 and p[1] < 470)):
        m.seawall(run)
    m.dam([(150, 478), (200, 466), (238, 498), (220, 548), (178, 584), (148, 578)])
    m.dam([(141, 604), (143, 626)])
    m.dam([(143, 658), (143, 672)])
    m.drone_corridor([(535, 268), (535, 360), (535, 505)])
    m.drone_corridor([(535, 268), (420, 330), (338, 372)])
    m.drone_corridor([(535, 268), (650, 270), (770, 262)])
    m.drone_corridor([(535, 268), (700, 420), (880, 520)])
    m.drone_corridor([(535, 268), (420, 440), (300, 560), (230, 640)])
    m.drone_corridor([(535, 268), (330, 420), (200, 480)])
    m.drone_corridor([(255, 640), (400, 700), (620, 770), (700, 860)])
    m.ferry([(150, 640), (110, 700), (100, 800), (110, 960)])
    m.ferry([(150, 600), (100, 520), (70, 420), (60, 300)])
    # ---- landmarks
    m.panopticon(535, 268, 33, COL['halcyon'], cone_to=(535, 505))
    m.helix(770, 262, 26, 0.4)
    m.launch_ring(700, 868, 34, math.pi / 2, zone_r=84)
    m.gantry_castle(290, 668, 28, 0.0, cranes=(-2.3, -1.9), crane_len=1.8)
    m.port_piers([(236, 556, 30, 8, -2.4), (214, 586, 30, 8, -2.35), (196, 616, 28, 8, -2.3)])
    m.circus(338, 372, 32, 0.4)
    m.pier_city(150, 525, 70, math.pi, n=9, spread=2.0)
    m.airport(900, 522, -0.2)
    glyphs(m, [(598, 385, 'stadium'), (560, 520, 'hospital'), (790, 280, 'hospital'), (190, 440, 'hospital'),
               (480, 450, 'university'), (740, 250, 'university'), (300, 420, 'university'),
               (500, 540, 'market'), (580, 470, 'market'), (420, 345, 'market'), (230, 700, 'market'),
               (330, 876, 'power'), (330, 735, 'power'), (910, 112, 'water'), (207, 818, 'sewage'),
               (575, 645, 'cemetery'), (785, 425, 'cemetery'), (905, 506, 'airport'),
               (965, 170, 'datacentre'), (170, 600, 'datacentre'), (445, 620, 'arcology'), (700, 420, 'arcology'),
               (370, 470, 'arcology'), (590, 300, 'megastructure'), (730, 290, 'megastructure'),
               (350, 745, 'megastructure'), (950, 665, 'recycling'), (540, 560, 'rebel'), (460, 470, 'church'),
               (780, 300, 'school')])
    district_labels(m, [('halcyon', 535, 175, 'HALCYON', 21, 0), ('solace', 770, 182, 'SOLACE', 21, 0),
                        ('aurelian', 320, 218, 'AURELIAN CONCORD', 19, 0), ('tethys', 190, 405, 'TETHYS DEEP', 20, 0),
                        ('meridian', 290, 810, 'MERIDIAN', 21, 0), ('orbital', 700, 958, 'ORBITAL', 21, 0),
                        ('centre', 535, 448, 'THE OLD CITY', 20, 0)])
    m.text(545, 585, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(70, 520, 'THE WESTERN SEA', 14, (150, 200, 235), spacing=8, weight='SemiBold', halo=False, angle=90)
    m.text(930, 220, 'upper river', 9, (150, 200, 235), weight='Regular', halo=False, angle=-50)
    m.text(170, 560, 'estuary', 9, (150, 200, 235), weight='Regular', halo=False, angle=-60)
    small_labels(m, [(520, 625, 'ISLAND QUAYS'), (680, 600, 'GASWORKS'), (640, 700, 'RAIL SLUMS'),
                     (250, 735, 'MARSHALLING YARD'), (255, 622, 'RIVER PORT'), (870, 500, 'AIRPORT'),
                     (965, 125, 'DATA CAMPUS'), (900, 70, 'RESERVOIR'), (180, 495, 'DROWNED DELTA'),
                     (560, 410, 'GRAND CANAL'), (395, 650, 'SOUTH BANK')])
    shields(m, [(530, 372, 'R1'), (708, 520, 'R1'), (540, 110, 'R2'), (985, 440, 'R2'), (560, 775, 'R2'),
                (538, 200, 'N1'), (300, 295, 'NW1'), (770, 270, 'NE1'), (870, 520, 'E1'), (690, 830, 'SE1'),
                (300, 695, 'SW1'), (280, 505, 'W1'), (380, 648, 'T1'), (520, 745, 'T2')])
    wind(m, 820, 60, 2.6, 'PREVAILING WIND')
    m.scalebar(30, 965)
    m.north(955, 965)
    m.title_block(250, 38, 'C  -  MEANDER', 'river city  /  omega-bend island town  /  bridges and an estuary port')
    return m


EVO = [
    ('c.1400', 'Ford and fishing village on a defensible meander island, a day upriver from the sea.'),
    ('1500-1850', 'Island town: organic lanes and three canal rings; the neck is cut as the Grand Canal. Estuary port grows downstream.'),
    ('1850-1930', 'Railway follows the valley; freight yards and quays on the south bank; rail-era grid fills both banks.'),
    ('1960-1990', 'R1 rings the river loop with a bridge at every crossing; R2 closes the outer ring; radials meet at stack interchanges.'),
    ('2040+', 'Corps arrive by corridor: Halcyon on the tor north, Solace upstream NE (clean water, upwind), Aurelian on the west-bank hills, Meridian and the port on the south bank, Orbital on the south cape.'),
    ('2080+', 'Estuary delta floods: Tethys barrier, dams and pier city at the mouth.'),
    ('always', 'Rail slums and informal quarters grow on the flood-prone river margins and along the freight line.'),
]


META = dict(
    key='C', slug='C_river_meander', title='C - MEANDER',
    subtitle='River city: island old town in an omega bend, estuary to the sea',
    blurb=['A river runs from the NE mountains to the western', 'sea. The old town is on a meander island;',
           'winds blow from the NE, so industry sits downriver.'],
    skip={'windfarm'},
    evo=EVO,
    notes={
        'halcyon': 'Surveillance. Rock tor north of the island.',
        'solace': 'Biotech. Upstream NE terraces, clean water.',
        'orbital': 'Aerospace. South cape; launches over the sea.',
        'meridian': 'Freight. South-bank river port and yards.',
        'aurelian': 'Finance/politics. Seven hills on the west bank.',
        'tethys': 'Ocean tech. Estuary delta, pier city, barrier.',
    },
)
