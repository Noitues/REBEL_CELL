"""Design B - RIBBON COAST. A linear coastal city on a diagonal shore, mountains behind, old harbour in a cove."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from citymap import COL, INDUSTRY, SLUM, CityMap, tint
from common import (NEU, corp_walls, district_labels, era_rings, fabric, glyphs, shields, slums, small_labels, wind)
from geom import blob, offset_line
import random

OUT = os.path.join(os.path.dirname(__file__), '..')


def build():
    m = CityMap(seed=21)
    coast = [(-60, 430), (40, 470), (130, 520), (210, 570), (290, 625), (350, 670), (395, 705), (410, 692), (440, 676),
             (470, 672), (500, 680), (520, 702), (535, 728), (580, 765), (640, 800), (710, 830), (790, 860), (870, 890),
             (950, 915), (1050, 945)]
    m.set_ocean(coast, [(1100, 1100), (-100, 1100), (-100, 430)], noise_amp=4.0)
    bumps = [(860, 150, 220, 160, 1.0, 0.3), (640, 60, 200, 90, 0.85, 0.0), (960, 450, 110, 220, 0.65, 0.0),
             (250, 220, 160, 80, 0.45, 0.0), (700, 515, 60, 55, 0.85, 0.0), (225, 455, 70, 60, 0.55, 0.0),
             (400, 320, 24, 24, 0.40, 0), (455, 292, 24, 24, 0.38, 0), (495, 352, 24, 24, 0.36, 0),
             (420, 392, 22, 22, 0.34, 0), (360, 345, 22, 22, 0.32, 0), (470, 405, 20, 20, 0.30, 0),
             (30, 120, 120, 120, 0.4, 0)]
    m.base(bumps)
    river = m.river([(780, -20), (720, 120), (640, 250), (575, 370), (525, 470), (490, 570), (472, 672)], 3.0, 8.0,
                    jitter=3.0)
    m.lake([(690, 90), (730, 78), (765, 100), (755, 135), (715, 140)])
    m.drowned([(235, 590), (300, 598), (360, 640), (392, 690), (360, 735), (300, 722), (240, 672), (205, 620)],
              seed=4, over_ocean=True, grid_angle=34)
    # ---- districts
    centre = m.zone('centre', [(372, 615), (392, 555), (450, 520), (520, 525), (575, 570), (585, 635), (552, 690),
                               (500, 700), (470, 680), (425, 690), (385, 670)], COL['centre'], 0.30)
    aur = m.zone('aurelian', [(360, 280), (430, 252), (515, 272), (548, 340), (522, 410), (452, 432), (382, 402),
                              (352, 340)], COL['aurelian'], 0.24)
    halc = m.zone('halcyon', [(640, 455), (700, 440), (752, 470), (768, 530), (735, 585), (672, 590), (630, 540)],
                  COL['halcyon'], 0.26, smooth=False)
    mer = m.zone('meridian', [(612, 705), (690, 690), (780, 705), (845, 745), (850, 812), (790, 835), (710, 822),
                              (640, 790)], COL['meridian'], 0.24, smooth=False)
    sol = m.zone('solace', [(120, 415), (200, 385), (290, 405), (325, 465), (292, 535), (222, 548), (150, 510)],
                 COL['solace'], 0.24)
    orb = m.zone('orbital', [(-10, 300), (70, 280), (135, 320), (145, 395), (105, 440), (30, 445), (-10, 415)],
                 COL['orbital'], 0.24, smooth=False)
    teth = m.zone('tethys', [(215, 540), (270, 535), (330, 570), (380, 625), (350, 625), (300, 585), (235, 565)],
                  COL['tethys'], 0.24, smooth=False)
    cc = tint(COL['centre'], 0.25)
    m.tex_grid(centre, 40, 7.5, 6.5, jitter=0.35, warp_amp=7, warp_wl=70, gap=0.25, major=5, color=cc, a_minor=0.45,
               a_major=0.75, seed=1)
    m.tex_walks(centre, 140, (25, 80), 0.35, color=cc, a=0.5, seed=1)
    m.tex_radial(aur, (455, 345), 14, 80, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, -12, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_super(halc, 20, 28, tint(COL['halcyon'], 0.3), seed=2)
    m.tex_super(mer, 25, 34, tint(COL['meridian'], 0.3), seed=7)
    m.tex_curvi(sol, (215, 455), 15, 140, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=60, seed=3)
    m.tex_super(orb, 10, 36, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.55)
    m.tex_super(teth, 35, 20, tint(COL['tethys'], 0.3), seed=6)
    # ---- parks, civic, industry
    m.park(m.strip_poly(river, 14, 0.35, 0.82), seed=1, free=True, smooth=False)
    m.park([(640, 160), (760, 180), (820, 280), (740, 360), (650, 320)], seed=2, free=True)
    m.park([(150, 250), (280, 220), (330, 280), (240, 350), (140, 340)], seed=3, free=True)
    m.park([(330, 520), (385, 505), (395, 545), (345, 560)], seed=4, free=True)
    m.park([(760, 560), (840, 540), (880, 600), (800, 640)], seed=5, free=True)
    m.park([(660, 345), (720, 330), (740, 395), (690, 410)], seed=6, free=True)
    m.park([(405, 580), (440, 565), (455, 610), (420, 625)], seed=7, a=0.7)
    m.park([(240, 430), (280, 425), (290, 470), (250, 478)], seed=8)
    m.built([(570, 600), (600, 590), (612, 625), (580, 635)], (110, 120, 110), 0.7)
    m.built([(878, 700), (916, 696), (922, 730), (884, 736)], (110, 120, 110), 0.7, free=True)
    m.plaza([(462, 600), (488, 600), (488, 626), (462, 626)])
    m.plaza([(440, 335), (470, 335), (470, 362), (440, 362)])
    term = m.built([(640, 760), (712, 790), (700, 815), (632, 790)], (110, 120, 138), 0.55)
    m.container_yard(672, 790, 70, 30, 0.45, clip=term)
    m.built([(745, 712), (850, 725), (850, 745), (745, 732)], (60, 64, 76), 0.8)
    m.industry([(780, 755), (845, 760), (848, 815), (792, 832)], seed=2, free=False, angle=25)
    m.industry([(560, 640), (610, 650), (640, 690), (600, 700), (565, 680)], seed=3, angle=40)
    m.built([(920, 878), (960, 888), (958, 912), (916, 905)], (90, 96, 112), 0.7, free=True)    # power
    m.built([(300, 150), (380, 140), (392, 190), (310, 200)], (70, 90, 100), 0.7, free=True)    # data
    m.built([(990, 930), (1000, 925), (1000, 945), (985, 942)], (130, 110, 90), 0.6)           # sewage
    m.built([(880, 600), (930, 595), (940, 640), (888, 650)], (40, 46, 60), 0.85, free=True)    # airport
    m.built([(930, 760), (975, 770), (970, 805), (925, 795)], (100, 130, 90), 0.6, free=True)   # recycling
    for i, (tx, ty, tr, nm) in enumerate([(900, 380, 17, 'HIGHGATE'), (820, 150, 14, 'RIDGEVIEW'),
                                           (610, 120, 14, 'FOOTHILL'), (170, 215, 15, 'WESTMARK'), (960, 250, 12, '')]):
        m.town(tx, ty, tr, seed=i, name=nm)
    slums(m, [[(560, 705), (600, 728), (612, 760), (575, 745)], [(850, 700), (900, 720), (905, 760), (855, 745)],
              [(400, 470), (450, 490), (440, 505), (395, 490)], [(325, 505), (370, 520), (360, 555), (320, 540)],
              [(150, 330), (190, 345), (195, 372), (155, 362)], [(570, 480), (615, 500), (610, 530), (570, 525)],
              [(500, 740), (545, 760), (540, 775), (495, 755)]], seed=3)
    m.undercity([(420, 560), (480, 545), (540, 565), (555, 615), (520, 655), (450, 650), (410, 610)])
    era_rings(m, (470, 625), [(62, 52, '1750 harbour town', 470, 590), (112, 92, '', 0, 0)])
    fabric(m, blob(480, 615, 200, 150, random.Random(2), 0.08, 18, 0.5), 38,
           blob(520, 600, 560, 300, random.Random(3), 0.06, 18, 0.55), (480, 640), (190, 600), 25, seed=2)
    m.grid_ticks()
    # ---- network
    H1 = m.add_road('H1 Coast Motorway', [(-20, 400), (60, 445), (150, 497), (240, 552), (310, 598), (372, 650), (400, 690),
                                          (445, 712), (495, 722), (538, 735), (585, 755), (650, 788), (715, 818),
                                          (790, 848), (870, 876), (950, 900), (1020, 920)], 'ring')
    H2 = m.add_road('H2 Inland Bypass', [(-20, 325), (90, 360), (190, 400), (290, 445), (390, 490), (490, 500), (558, 562),
                                         (618, 636), (668, 690), (760, 694), (850, 716), (940, 766), (1020, 812)], 'ring')
    H3 = m.add_road('H3 Mountain Road', [(-20, 235), (120, 258), (255, 262), (350, 248), (440, 244), (560, 256), (640, 325),
                                         (720, 398), (800, 465), (885, 520), (1020, 560)], 'ring')
    R1 = m.add_road('R1', [(500, 656), (440, 652), (398, 630), (382, 585), (410, 540), (470, 515), (535, 520), (580, 555),
                           (595, 605), (575, 650), (545, 664), (500, 656)], 'motorway', tunnels=[(0.0, 0.06), (0.92, 1.0)])
    m.add_road('K1 Solace Link', [(240, 556), (248, 480), (262, 430), (275, 350), (290, 252)], 'motorway')
    m.add_road('K2 Via Aurelia', [(478, 650), (480, 505), (472, 440), (470, 350), (462, 240)], 'motorway')
    m.add_road('K3 Halcyon Road', [(560, 540), (630, 520), (690, 495), (750, 470), (795, 462)], 'motorway')
    m.add_road('K5 Orbital Road', [(130, 508), (115, 450), (100, 390), (92, 330), (85, 250)], 'motorway')
    m.add_road('T1 Freight Expressway', [(715, 822), (724, 760), (748, 694), (775, 610), (805, 520), (830, 440), (880, 340),
                                         (960, 250), (1020, 200)], 'truck')
    m.add_road('T2 Port Spur', [(640, 792), (672, 742), (700, 700), (748, 694)], 'truck')
    arts = [('Waterfront Avenue', [(398, 640), (440, 660), (500, 664), (545, 670), (590, 690)], False),
            ('Grand Axis', [(470, 540), (472, 600), (478, 656)], False),
            ('Solace Spine', [(150, 470), (220, 470), (290, 470)], True),
            ('Aurelian Ring Rd', [(380, 300), (450, 285), (520, 305)], False),
            ('Halcyon Gate', [(600, 470), (650, 480), (700, 500)], False),
            ('Meridian Main', [(630, 745), (710, 750), (790, 762), (845, 778)], True),
            ('Orbital Blvd', [(10, 340), (70, 360), (120, 380)], True),
            ('Airport Road', [(805, 520), (860, 580), (884, 612)], True),
            ('Quay Road', [(640, 798), (720, 826), (790, 852)], False),
            ('Dam Road', [(310, 598), (325, 640), (318, 690)], False),
            ('Corporate Ave', [(540, 560), (610, 600), (640, 650)], True),
            ('Old City Cross', [(385, 600), (440, 598), (520, 600), (580, 610)], False)]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    m.add_rail('Freight East Main', [(1020, 840), (930, 790), (850, 752), (800, 735), (760, 732), (722, 752), (690, 778)], 'freight')
    for k in (-6, 6):
        m.add_rail('yard', [(750, 724 + k), (850, 734 + k)], 'freight', smooth=False)
    m.add_rail('Orbital Freight', offset_line(H2['pts'], 10), 'freight', smooth=False)
    CL = m.add_rail('Coast Line', offset_line(H1['pts'], -10), 'commuter', smooth=False)
    CV = m.add_rail('Valley Line', [(482, 604), (485, 520), (480, 440), (500, 380), (540, 300), (600, 200), (650, 100), (700, -10)], 'commuter')
    CE = m.add_rail('East Line', [(482, 604), (560, 560), (640, 522), (740, 540), (830, 580), (884, 620)], 'commuter')
    M1 = m.add_rail('M1', [(185, 500), (260, 530), (340, 570), (420, 590), (482, 604), (540, 590), (600, 570), (655, 525)], 'metro',
                    tunnels=[(0.45, 0.75)])
    M2 = m.add_rail('M2', [(460, 350), (470, 430), (478, 520), (482, 604), (520, 655), (570, 705), (630, 745), (690, 775)], 'metro',
                    tunnels=[(0.4, 0.8)])
    M3 = m.add_rail('M3', [(305, 692), (318, 640), (345, 615), (410, 598), (482, 604)], 'metro')
    m.draw_rails()
    m.draw_roads()
    m.auto_interchanges()
    m.stations_along(CL, (0.1, 0.22, 0.34, 0.47, 0.6, 0.72, 0.85, 0.95), 'rail')
    m.stations_along(CV, (0.2, 0.4, 0.55, 0.7, 0.85), 'rail')
    m.stations_along(CE, (0.3, 0.55, 0.8, 0.97), 'rail')
    m.stations_along(M1, (0.1, 0.25, 0.4, 0.6, 0.75, 0.9), 'metro')
    m.stations_along(M2, (0.1, 0.25, 0.4, 0.7, 0.85, 0.97), 'metro')
    m.stations_along(M3, (0.2, 0.5, 0.8), 'metro')
    for p in ((482, 604), (748, 694), (884, 614), (632, 540), (305, 692)):
        m.station(p[0], p[1], 'hub')
    m.station(690, 778, 'freight')
    # ---- walls, sea defences, drones
    corp_walls(m, ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'))
    for run in m.coast_seg(lambda p: p[0] > 120 and p[1] > 500 and not (200 < p[0] < 400 and 570 < p[1] < 740)):
        m.seawall(run)
    m.dam([(205, 612), (245, 590), (300, 596), (350, 625), (382, 665), (394, 693)])
    m.dam([(398, 702), (452, 709)])
    m.dam([(478, 714), (535, 728)])
    m.drone_corridor([(705, 515), (640, 580), (560, 610), (482, 610)])
    m.drone_corridor([(705, 515), (720, 620), (710, 740)])
    m.drone_corridor([(705, 515), (800, 570), (880, 612)])
    m.drone_corridor([(705, 515), (560, 420), (470, 360)])
    m.drone_corridor([(705, 515), (500, 480), (260, 470)])
    m.drone_corridor([(100, 360), (160, 440), (230, 470)])
    m.ferry([(470, 700), (400, 735), (340, 710), (315, 700)])
    m.ferry([(500, 715), (590, 790), (650, 830), (690, 840)])
    m.ferry([(470, 700), (420, 800), (380, 900), (360, 990)])
    m.windfarm([(120, 800), (330, 870), (350, 990), (100, 990)])
    m.windfarm([(820, 960), (980, 990), (780, 1000)])
    # ---- landmarks
    m.panopticon(705, 515, 33, COL['halcyon'], cone_to=(480, 610))
    m.helix(225, 458, 26, -0.4)
    m.launch_ring(72, 405, 32, 2.5, zone_r=72)
    m.gantry_castle(698, 756, 28, 0.0, cranes=(2.0, 1.7), crane_len=2.0)
    m.port_piers([(655, 796, 46, 8, 2.0), (690, 809, 46, 8, 2.0), (726, 822, 46, 8, 2.0), (766, 837, 46, 8, 2.0)])
    m.circus(455, 345, 32, 0.3)
    m.pier_city(305, 690, 70, 2.3, n=9, spread=2.0)
    m.airport(884, 628, -0.3)
    glyphs(m, [(535, 480, 'stadium'), (470, 590, 'hospital'), (290, 500, 'hospital'), (345, 720, 'hospital'),
               (440, 560, 'university'), (250, 400, 'university'), (400, 360, 'university'),
               (500, 570, 'market'), (440, 640, 'market'), (480, 330, 'market'), (700, 800, 'market'),
               (940, 878, 'power'), (790, 725, 'power'), (725, 140, 'water'), (990, 930, 'sewage'),
               (580, 612, 'cemetery'), (900, 715, 'cemetery'), (884, 590, 'airport'),
               (340, 170, 'datacentre'), (370, 700, 'datacentre'), (400, 480, 'arcology'), (590, 500, 'arcology'),
               (545, 680, 'arcology'), (760, 520, 'megastructure'), (190, 440, 'megastructure'),
               (855, 800, 'megastructure'), (950, 782, 'recycling'), (470, 635, 'rebel'), (440, 395, 'church'),
               (305, 520, 'school')])
    district_labels(m, [('halcyon', 700, 425, 'HALCYON', 21, 0), ('solace', 205, 365, 'SOLACE', 21, 0),
                        ('aurelian', 440, 238, 'AURELIAN CONCORD', 19, 0), ('tethys', 215, 760, 'TETHYS DEEP', 21, 38),
                        ('meridian', 770, 670, 'MERIDIAN', 21, 0), ('orbital', 80, 275, 'ORBITAL', 21, 0),
                        ('centre', 470, 505, 'THE OLD CITY', 22, 0)])
    m.text(480, 645, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(560, 925, 'THE OPEN SEA', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False, angle=22)
    m.text(468, 708, 'OLD HARBOUR', 8.5, (210, 225, 240), spacing=2, weight='SemiBold')
    small_labels(m, [(560, 725, 'DOCKSIDE STACKS'), (610, 525, 'FOUNDRY'), (360, 540, 'THE HEATH'),
                     (280, 600, 'DROWNED QUARTER'), (755, 725, 'MARSHALLING YARD'), (880, 650, 'AIRPORT'),
                     (340, 125, 'DATA CAMPUS'), (735, 160, 'RESERVOIR'), (670, 788, 'CONTAINER TERMINAL')])
    shields(m, [(60, 440, 'H1'), (900, 884, 'H1'), (90, 360, 'H2'), (940, 766, 'H2'), (120, 258, 'H3'), (885, 520, 'H3'),
                (262, 430, 'K1'), (470, 350, 'K2'), (690, 495, 'K3'), (100, 390, 'K5'), (805, 520, 'T1'), (672, 742, 'T2'),
                (450, 654, 'R1')])
    wind(m, 880, 60, 0.0)
    m.scalebar(40, 965)
    m.north(955, 965)
    m.title_block(34, 38, 'B  -  RIBBON COAST', 'linear coastal city  /  three parallel motorways  /  rail trunk on the shore')
    return m


EVO = [
    ('c.1600', 'Fishing hamlet in a cove, a river mouth behind it and mountains behind that. Only the shore strip was flat.'),
    ('1800-1890', 'Cove harbour town with an organic core and canal; a coastal grid is laid out along the shore in both directions.'),
    ('1880-1930', 'Coast railway squeezed between shore and old streets; freight yards and quays strung along the straight coast to the east.'),
    ('1960-1990', 'Coast Motorway and the Inland Bypass built parallel to the rail, with cross-spurs every 150 units; Mountain Road caps the ribbon.'),
    ('2040+', 'Corporate districts stack along the ribbon: Orbital and Solace west, Halcyon on the spur above the old city, Aurelian on the river hills, Meridian on the deep-water coast. The Harbour Bridge replaces the old cove entrance.'),
    ('2080+', 'The south-west shore floods: dams, Tethys pier city and a drowned quarter.'),
    ('always', 'Informal stacks fill gaps between the motorways; satellite towns grow in the foothills.'),
]


META = dict(
    key='B', slug='B_ribbon_coast', title='B - RIBBON COAST',
    subtitle='Linear coastal city: old harbour cove, ribbon along the shore',
    blurb=['A diagonal shore with mountains behind. The cove', 'harbour is the centre; Coast, Inland and Mountain',
           'motorways run parallel, linked by cross-spurs.'],
    skip=set(),
    evo=EVO,
    notes={
        'halcyon': 'Surveillance. Spur above the old city, sees it all.',
        'solace': 'Biotech. Clean upwind coastal hills, west.',
        'orbital': 'Aerospace. NW cape, launches SW over open sea.',
        'meridian': 'Freight. Piers on the straight deep-water coast.',
        'aurelian': 'Finance/politics. Seven hills on the river, north.',
        'tethys': 'Ocean tech. Pier city over the drowned SW shore.',
    },
)
