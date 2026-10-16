"""Design A - HORSESHOE BAY. A bay city: the old port at the head of a horseshoe bay, six districts around it."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from citymap import COL, INDUSTRY, PARK, SLUM, TEXT, CityMap, tint
from geom import circle_pts, ellipse_pts, mix, rect_pts
from panel import compose, make_panel

OUT = os.path.join(os.path.dirname(__file__), '..')
NEU = (150, 162, 182)


def build(phase=9):
    m = CityMap(seed=11)
    # ------------------------------------------------------------- coast + terrain
    coast = [(-60, 760), (40, 775), (130, 810), (220, 850), (300, 885), (360, 905), (392, 895),
             (386, 860), (362, 815), (340, 765), (330, 715), (342, 665), (375, 625), (425, 600), (500, 592),
             (575, 600), (625, 625), (658, 665), (670, 715), (660, 765), (638, 815), (614, 860), (608, 895),
             (655, 915), (730, 935), (810, 940), (890, 925), (950, 905), (1010, 880)]
    m.set_ocean(coast, [(1100, 880), (1100, 1100), (-100, 1100), (-100, 760)], noise_amp=4.0)
    bumps = [
        (520, 265, 75, 62, 0.95, 0.0), (480, 120, 260, 70, 0.55, 0.1), (270, 250, 85, 70, 0.55, 0.0),
        (110, 450, 26, 26, 0.38, 0), (180, 430, 24, 24, 0.36, 0), (95, 545, 26, 26, 0.34, 0),
        (150, 590, 24, 24, 0.34, 0), (115, 640, 22, 22, 0.30, 0), (60, 500, 24, 24, 0.30, 0),
        (790, 160, 120, 60, 0.30, 0.3), (880, 420, 90, 140, 0.22, 0.0), (520, 470, 90, 70, 0.14, 0.0),
        (60, 120, 120, 90, 0.35, 0.2),
    ]
    m.base(bumps)
    # ------------------------------------------------------------- water
    river = m.river([(405, -20), (400, 60), (396, 150), (398, 250), (392, 330), (360, 395), (318, 440), (282, 500),
                     (262, 560), (262, 620), (285, 680), (318, 725), (338, 748)], 3.0, 9.0, jitter=3.0)
    m.lake([(545, 105), (580, 92), (615, 105), (625, 135), (595, 150), (560, 145)])
    m.river([(455, 598), (455, 540), (430, 500), (420, 470)], 2.6, 2.6, smooth=False)
    m.river([(548, 598), (548, 545), (572, 520)], 2.6, 2.6, smooth=False)
    m.drowned([(250, 730), (300, 712), (345, 720), (372, 760), (368, 830), (330, 870), (280, 862), (240, 830),
               (222, 780)], seed=4)
    # ------------------------------------------------------------- districts
    centre = m.zone('centre', [(385, 490), (398, 425), (450, 385), (520, 375), (588, 398), (625, 455), (622, 525),
                               (598, 588), (530, 618), (470, 618), (410, 585)], COL['centre'], 0.30)
    halc = m.zone('halcyon', [(440, 215), (500, 192), (585, 205), (635, 245), (632, 305), (575, 343), (492, 345),
                              (436, 308), (418, 255)], COL['halcyon'], 0.26, smooth=False)
    sol = m.zone('solace', [(170, 200), (240, 170), (320, 185), (365, 230), (358, 300), (300, 335), (228, 330),
                            (178, 280)], COL['solace'], 0.24)
    aur = m.zone('aurelian', [(60, 420), (130, 385), (205, 405), (245, 455), (250, 540), (238, 625), (180, 670),
                              (105, 655), (60, 590), (45, 500)], COL['aurelian'], 0.24)
    teth = m.zone('tethys', [(120, 725), (190, 692), (262, 702), (325, 726), (350, 775), (350, 830), (335, 866),
                             (290, 872), (230, 846), (160, 792)], COL['tethys'], 0.24, smooth=False)
    mer = m.zone('meridian', [(672, 625), (745, 600), (815, 615), (880, 670), (905, 740), (870, 800), (790, 818),
                              (710, 815), (670, 770), (662, 700)], COL['meridian'], 0.24, smooth=False)
    orb = m.zone('orbital', [(715, 880), (790, 852), (870, 850), (940, 842), (998, 832), (1000, 884), (952, 904),
                             (892, 923), (812, 936), (742, 926)], COL['orbital'], 0.24, smooth=False)
    cc = tint(COL['centre'], 0.25)
    m.tex_grid(centre, 23, 7.5, 6.5, jitter=0.35, warp_amp=7, warp_wl=70, gap=0.25, major=5, color=cc, a_minor=0.45,
               a_major=0.75, seed=1)
    m.tex_walks(centre, 140, (25, 80), 0.35, color=cc, a=0.5, seed=1)
    m.tex_super(halc, 6, 30, tint(COL['halcyon'], 0.3), seed=2)
    m.tex_curvi(sol, (260, 255), 15, 140, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=60, seed=3)
    m.tex_radial(aur, (205, 540), 14, 80, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, -12, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_super(teth, -10, 26, tint(COL['tethys'], 0.3), seed=6)
    m.tex_super(mer, 12, 36, tint(COL['meridian'], 0.3), seed=7)
    m.tex_super(orb, 0, 40, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.5)
    # ------------------------------------------------------------- parks, civic, industry, slums
    m.park(m.strip_poly(river, 14, 0.18, 0.62), seed=1, free=True, smooth=False)
    m.park([(700, 330), (790, 312), (860, 340), (850, 420), (770, 452), (700, 420)], seed=2, free=True)
    m.park([(250, 52), (330, 40), (385, 78), (335, 132), (262, 122)], seed=3, free=True)
    m.park([(628, 562), (662, 575), (668, 625), (640, 615)], seed=4, free=True)
    m.park([(0, 300), (120, 280), (150, 350), (60, 392), (0, 380)], seed=5, free=True)
    m.park([(660, 362), (722, 330), (742, 402), (692, 432)], seed=6, free=True)
    m.park([(70, 430), (110, 420), (122, 470), (82, 482)], seed=7)             # Aurelian gardens
    m.park([(190, 230), (250, 215), (262, 262), (212, 282)], seed=8)           # Solace arboretum
    m.park([(436, 440), (470, 428), (486, 466), (452, 480)], seed=9, a=0.7)    # old city commons
    m.park([(548, 505), (584, 498), (590, 540), (556, 548)], seed=10, a=0.7)
    m.built([(298, 606), (330, 602), (340, 640), (310, 655)], (110, 120, 110), 0.7, free=True)  # necropolis
    m.built([(704, 380), (742, 376), (746, 410), (708, 414)], (110, 120, 110), 0.7)
    m.plaza([(488, 488), (514, 488), (514, 514), (488, 514)])
    m.plaza([(190, 486), (224, 486), (224, 516), (190, 516)])
    m.plaza([(515, 336), (545, 336), (545, 350), (515, 350)])
    # industry and logistics
    term = m.built([(672, 688), (742, 688), (742, 790), (668, 790)], (110, 120, 138), 0.55)
    m.container_yard(706, 740, 60, 90, 0, clip=term)
    yard = m.built([(742, 640), (850, 640), (850, 672), (742, 672)], (60, 64, 76), 0.8)
    m.industry([(830, 690), (900, 700), (900, 792), (840, 806)], seed=2, free=False, angle=12)
    m.industry([(680, 520), (742, 505), (762, 570), (702, 600), (672, 582)], seed=3, angle=-20)
    m.built([(626, 828), (662, 822), (670, 862), (636, 872)], (90, 96, 112), 0.7, free=True)   # power
    m.built([(760, 118), (842, 108), (852, 160), (772, 176)], (70, 90, 100), 0.7, free=True)   # data centres
    m.built([(896, 598), (934, 592), (940, 632), (900, 640)], (130, 110, 90), 0.6, free=True)  # sewage
    m.built([(922, 548), (960, 544), (966, 578), (928, 584)], (100, 130, 90), 0.6, free=True)  # recycling
    air = m.built([(665, 236), (790, 216), (815, 250), (800, 292), (680, 300)], (40, 46, 60), 0.85, free=True)
    # slums / informal housing
    for i, poly in enumerate([
            [(345, 430), (385, 420), (386, 520), (374, 590), (340, 600), (335, 520)],
            [(655, 420), (700, 430), (715, 510), (672, 520), (655, 480)],
            [(215, 700), (260, 690), (266, 730), (222, 746)],
            [(910, 690), (960, 700), (965, 762), (915, 772)],
            [(330, 345), (385, 336), (392, 388), (345, 402)],
            [(690, 585), (740, 596), (748, 604), (696, 612)],
            [(470, 624), (520, 626), (520, 640), (470, 640)]]):
        mk, pts = m.free_mask(poly, True)
        m.fill_mask(mk, SLUM, 0.12)
        m.tex_slum(mk, 0.55, SLUM, 0.62, seed=i)
        m.line(pts + [pts[0]], SLUM, 0.8, 0.5, clip=m.dry)
    # undercity (under the old core)
    m.undercity([(420, 430), (480, 410), (560, 420), (590, 470), (580, 540), (520, 570), (450, 550), (415, 500)])
    import random as _r
    from geom import blob as _blob
    for (rx, ry, lab, ly) in ((70, 60, '1750 town wall', 440), (118, 100, '1890 rail-era edge', 396)):
        pts = m_blob(505, 490, rx, ry, 5)
        from geom import catmull as _cm
        d_ = _cm(pts, closed=True, step=3)
        m.line(d_ + [d_[0]], (240, 220, 180), 0.9, 0.6, dash=(3, 2.5), clip=m.dry)
    m.text(505, 427, '1750 town wall', 7.5, (240, 220, 180), weight='Regular', halo=True)
    # fabric: rail-era grid, mid-century suburbs, hinterland
    f1, _ = m.free_mask(m_blob(505, 495, 215, 195, 3), True)
    m.img.paste(NEU, mask=f1.point(lambda v: int(v * 0.10)))
    m.tex_grid(f1, -8, 9, jitter=0.08, major=5, color=NEU, a_minor=0.34, a_major=0.5, seed=2, gap=0.04)
    f2, _ = m.free_mask(m_blob(505, 480, 350, 360, 4), True)
    m.img.paste(NEU, mask=f2.point(lambda v: int(v * 0.07)))
    m.tex_curvi(f2, (505, 490), 190, 560, 7.5, 0, 6.2832, 0.28, 20, NEU, 0.40, cul=140, seed=3)
    f3, _ = m.free_mask([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], False)
    m.img.paste((88, 110, 78), mask=f3.point(lambda v: int(v * 0.12)))
    m.tex_grid(f3, 14, 26, 22, jitter=0.2, warp_amp=14, warp_wl=180, gap=0.35, seg=(40, 120), major=0,
               color=(120, 140, 108), a_minor=0.35, seed=5)
    m.tex_dots(f3, 500, (50, 90, 54), 0.5, 1.4, seed=9)
    m.grid_ticks()
    # ------------------------------------------------------------- network
    R1 = m.add_road('R1', [(500, 578), (425, 588), (378, 556), (352, 500), (358, 440), (392, 390), (450, 357), (520, 345),
                           (590, 358), (640, 395), (662, 450), (660, 510), (635, 560), (580, 588), (500, 578)], 'ring',
                    tunnels=[(0.0, 0.07), (0.94, 1.0)])
    R2 = m.add_road('R2', [(394, 890), (345, 884), (300, 872), (255, 858), (225, 830), (215, 790), (225, 745), (205, 705),
                           (150, 700), (95, 672), (50, 615), (28, 530), (30, 430), (48, 335), (92, 240), (160, 160),
                           (260, 105), (380, 75), (500, 62), (620, 72), (740, 100), (850, 150), (930, 230), (972, 340),
                           (985, 460), (975, 580), (945, 690), (900, 780), (835, 836), (760, 846), (690, 870),
                           (640, 884), (608, 888), (500, 894), (394, 890)], 'ring')
    m.add_road('N1 Halcyon Radial', [(470, 372), (466, 290), (468, 210), (478, 140), (492, 62)], 'motorway')
    m.add_road('N2 Solace Parkway', [(405, 402), (368, 350), (322, 300), (262, 235), (205, 170), (160, 160)], 'motorway')
    m.add_road('W1 Via Aurelia', [(372, 500), (300, 495), (250, 490), (190, 480), (100, 470), (30, 470)], 'motorway')
    m.add_road('SW1 Tethys Link', [(385, 560), (345, 610), (300, 650), (262, 692), (228, 748)], 'motorway')
    m.add_road('NE1 Airport Expressway', [(612, 378), (670, 330), (730, 290), (780, 225), (850, 150)], 'motorway')
    m.add_road('E1 Coastal Highway', [(640, 440), (720, 445), (800, 455), (880, 470), (985, 465)], 'motorway')
    m.add_road('T1 Port Expressway', [(672, 748), (710, 752), (770, 752), (840, 745), (905, 745), (950, 692)], 'truck')
    m.add_road('T2 Yard Link', [(790, 655), (745, 592), (700, 545), (648, 495)], 'truck')
    m.add_road('T3 Launch Road', [(800, 752), (815, 800), (840, 845), (880, 880)], 'truck')
    # arterials
    arts = [
        ('Bayfront Boulevard', [(425, 594), (470, 590), (500, 588), (550, 592), (590, 596)], False),
        ('Grand Avenue', [(505, 350), (505, 420), (508, 490), (505, 580)], False),
        ('Via Sacra', [(355, 505), (430, 498), (505, 492), (580, 495), (660, 500)], False),
        ('Halcyon Gate', [(540, 345), (545, 290), (540, 240), (530, 200)], False),
        ('Meridian Main', [(672, 700), (740, 712), (810, 722), (880, 725)], True),
        ('Orbital Boulevard', [(740, 892), (820, 892), (900, 882), (990, 862)], True),
        ('Airport Link', [(640, 262), (700, 262), (745, 262)], True),
        ('Solace Spine', [(260, 335), (230, 400), (200, 450)], False),
        ('Dam Avenue', [(190, 672), (214, 702)], False),
        ('Meridian Cross', [(790, 618), (790, 818)], True),
        ('Corporate Ring Ave', [(662, 548), (688, 612), (720, 650)], False),
        ('Riverside Drive N', [(412, 360), (412, 250), (416, 160)], True),
        ('Tethys Quay Road', [(300, 755), (330, 700), (342, 670)], False),
        ('Forum Way', [(200, 520), (260, 512)], True),
        ('Orbital Gate Rd', [(870, 760), (880, 840), (885, 870)], True),
    ]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    # rail
    F1 = m.add_rail('Freight East Main', [(1000, 575), (960, 600), (900, 640), (850, 660), (790, 670), (740, 692),
                                          (700, 725), (672, 742)], 'freight')
    for k in (-6, 6):
        m.add_rail('yard', [(745, 656 + k), (850, 656 + k)], 'freight', smooth=False)
    m.add_rail('Freight North Belt', [(790, 655), (830, 560), (850, 450), (845, 330), (840, 220), (860, 110), (870, -10)],
               'freight')
    m.add_rail('Orbital Spur', [(800, 690), (815, 770), (840, 845), (870, 880)], 'freight')
    CA = m.add_rail('C1 West', [(0, 432), (80, 445), (150, 470), (230, 490), (300, 505), (380, 495), (460, 485), (500, 480)], 'commuter')
    CB = m.add_rail('C2 North', [(500, 480), (505, 400), (510, 330), (515, 250), (520, 150), (520, -10)], 'commuter')
    CC = m.add_rail('C3 Northeast', [(500, 480), (560, 440), (640, 400), (700, 330), (745, 275), (800, 215), (900, 170), (1000, 150)], 'commuter')
    CD = m.add_rail('C4 Southeast', [(500, 480), (570, 520), (640, 580), (690, 640), (720, 700)], 'commuter')
    M1 = m.add_rail('M1 Loop', [(505 + 95 * math.cos(t * 6.2832 / 20), 495 + 80 * math.sin(t * 6.2832 / 20)) for t in range(21)], 'metro', smooth=True)
    M2 = m.add_rail('M2', [(262, 280), (310, 350), (380, 425), (450, 472), (505, 495), (570, 535), (625, 590), (660, 650), (690, 712)], 'metro',
                    tunnels=[(0.3, 0.7)])
    M3 = m.add_rail('M3', [(312, 800), (300, 730), (250, 640), (230, 570), (300, 540), (420, 505), (505, 495), (520, 420), (525, 345), (530, 262)],
                    'metro', tunnels=[(0.35, 0.75)])
    m.draw_rails()
    m.draw_roads()
    inter = m.auto_interchanges()
    # stations
    m.stations_along(CA, (0.12, 0.35, 0.6, 0.8), 'rail')
    m.stations_along(CB, (0.2, 0.4, 0.6, 0.75), 'rail')
    m.stations_along(CC, (0.25, 0.4, 0.55, 0.72, 0.85), 'rail')
    m.stations_along(CD, (0.3, 0.6, 0.9), 'rail')
    m.stations_along(M1, [i / 6 for i in range(6)], 'metro')
    m.stations_along(M2, (0.08, 0.2, 0.32, 0.65, 0.82, 0.95), 'metro')
    m.stations_along(M3, (0.04, 0.16, 0.3, 0.45, 0.62, 0.8, 0.95), 'metro')
    for p in ((505, 493), (700, 655), (745, 262), (528, 345), (300, 740)):
        m.station(p[0], p[1], 'hub')
    m.station(790, 664, 'freight')
    m.station(672, 742, 'freight')
    m.station(870, 880, 'freight')
    # ------------------------------------------------------------- walls, gates, sea walls, dams
    for key in ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'):
        pts = m.z[key]['poly']
        w = m.wall(pts, COL[key], closed=True)
        m.gates_on(w)
    for run in m.coast_seg(lambda p: 330 < p[0] < 680 and 590 < p[1] < 895 and not (p[0] < 400 and p[1] > 700)):
        m.seawall(run)
    for run in m.coast_seg(lambda p: p[0] > 612 and p[1] > 900):
        m.seawall(run)
    m.dam([(396, 892), (486, 894)])
    m.dam([(514, 894), (606, 889)])
    m.dam([(225, 745), (262, 720), (310, 708), (346, 712)])
    m.dam([(225, 745), (214, 790), (225, 830), (255, 858), (300, 872), (346, 884)])
    # ferries, wind farm
    m.ferry([(500, 612), (450, 700), (390, 770), (355, 800)])
    m.ferry([(500, 612), (580, 700), (630, 760), (664, 775)])
    m.ferry([(500, 612), (500, 760), (500, 890), (500, 1000)])
    m.windfarm([(380, 945), (620, 945), (640, 995), (380, 995)])
    # drones
    m.drone_corridor([(535, 268), (640, 340), (720, 480), (770, 640), (790, 700)])
    m.drone_corridor([(535, 268), (420, 330), (330, 420), (260, 520), (230, 545)])
    m.drone_corridor([(535, 268), (640, 262), (745, 262)])
    m.drone_corridor([(535, 268), (300, 270)])
    m.drone_corridor([(860, 860), (820, 790), (790, 720)])
    # ------------------------------------------------------------- landmarks
    m.panopticon(535, 268, 33, COL['halcyon'], cone_to=(505, 490))
    m.helix(268, 262, 26, -0.5)
    m.launch_ring(885, 888, 34, math.radians(35), zone_r=84)
    m.gantry_castle(772, 705, 28, 0.0, cranes=(math.pi, math.pi*0.75), crane_len=2.2)
    m.port_piers([(668, 692, 46, 8, math.pi), (666, 722, 50, 8, math.pi), (664, 752, 48, 8, math.pi), (654, 782, 40, 8, math.pi)])
    m.circus(224, 548, 32, 0.3)
    m.pier_city(312, 795, 66, 0.15, n=9, spread=2.0)
    m.airport(740, 262, 0.05)
    for (x, y, k) in [(700, 470, 'stadium'), (530, 445, 'hospital'), (300, 262, 'hospital'), (262, 775, 'hospital'),
                      (440, 425, 'university'), (240, 215, 'university'), (178, 520, 'university'),
                      (480, 455, 'market'), (560, 572, 'market'), (205, 505, 'market'), (690, 722, 'market'),
                      (646, 845, 'power'), (815, 648, 'power'), (595, 168, 'water'), (917, 616, 'sewage'),
                      (318, 628, 'cemetery'), (725, 395, 'cemetery'), (745, 238, 'airport'),
                      (800, 142, 'datacentre'), (345, 820, 'datacentre'), (365, 455, 'arcology'), (668, 445, 'arcology'),
                      (420, 352, 'arcology'), (590, 300, 'megastructure'), (210, 300, 'megastructure'),
                      (840, 790, 'megastructure'), (944, 566, 'recycling'), (520, 515, 'rebel'), (160, 440, 'church'),
                      (230, 305, 'school')]:
        m.glyph(k, x, y, 7.4)
    # ------------------------------------------------------------- labels
    D = dict(size=21, spacing=5, weight='Bold')
    m.text(528, 172, 'HALCYON', 21, tint(COL['halcyon'], 0.4), spacing=5)
    m.text(270, 152, 'SOLACE', 21, tint(COL['solace'], 0.4), spacing=5)
    m.text(150, 372, 'AURELIAN CONCORD', 19, tint(COL['aurelian'], 0.4), spacing=4)
    m.text(150, 872, 'TETHYS DEEP', 21, tint(COL['tethys'], 0.4), spacing=5, angle=18)
    m.text(800, 590, 'MERIDIAN', 21, tint(COL['meridian'], 0.4), spacing=5)
    m.text(860, 965, 'ORBITAL', 21, tint(COL['orbital'], 0.5), spacing=5)
    m.text(505, 402, 'THE OLD CITY', 22, tint(COL['centre'], 0.3), spacing=4)
    m.text(520, 530, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(500, 740, 'THE HORSESHOE', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False)
    m.text(500, 912, 'BAY BARRIER', 10, (210, 225, 240), spacing=3, weight='SemiBold')
    m.text(360, 700, 'veyra estuary', 10, (150, 200, 235), weight='Regular', halo=False, angle=-35)
    for (x, y, t) in [(360, 490, 'RIVER FLATS'), (722, 548, 'FOUNDRY ROW'), (245, 724, 'STILT TOWN'),
                      (330, 662, 'NECROPOLIS'), (190, 560, 'THE FORUM'), (700, 770, 'CONTAINER TERMINAL'),
                      (800, 640, 'MARSHALLING YARD'), (735, 215, 'AIRPORT'), (880, 118, 'DATA CAMPUS'),
                      (320, 805, 'DROWNED QUARTER'), (500, 610, 'OLD PORT'), (860, 890, '')]:
        if t:
            m.text(x, y, t, 8.5, (214, 220, 232), spacing=1, weight='SemiBold')
    m.text(580, 120, 'RESERVOIR', 8, (150, 200, 235), spacing=1, weight='SemiBold')
    # road shields
    for (x, y, t) in [(500, 345, 'R1'), (660, 480, 'R1'), (28, 530, 'R2'), (500, 62, 'R2'), (985, 440, 'R2'), (500, 894, 'R2'),
                      (468, 160, 'N1'), (232, 195, 'N2'), (140, 475, 'W1'), (330, 628, 'SW1'), (770, 235, 'NE1'),
                      (880, 466, 'E1'), (870, 752, 'T1'), (720, 568, 'T2'), (830, 850, 'T3')]:
        m.shield(x, y, t)
    # wind + frame
    m.line([(890, 62), (950, 62)], (200, 215, 235), 1.6, 0.9)
    m.poly([(960, 62), (948, 56), (948, 68)], (200, 215, 235), 0.9)
    m.text(920, 48, 'PREVAILING WIND', 9, (200, 215, 235), spacing=1.5, weight='SemiBold')
    m.scalebar(40, 965)
    m.north(955, 960)
    m.title_block(34, 38, 'A  -  HORSESHOE BAY', 'bay city  /  old port at the bay head  /  six districts on the arc')
    return m


def m_blob(cx, cy, rx, ry, seed):
    import random
    from geom import blob
    return blob(cx, cy, rx, ry, random.Random(seed), 0.08, 18)


if __name__ == '__main__':
    import time
    t0 = time.time()
    m = build()
    m.save_map(os.path.join(OUT, 'wip_a.png'), 2000)
    print('done', time.time() - t0)


EVO = [
    ('c.1650', 'Fishing village and quay at the head of a sheltered horseshoe bay, a ford where the river meets the bay.'),
    ('1750-1890', 'Walled port town on the knoll; organic lanes, two canals to the quays; rail-era grid laid out beyond the wall.'),
    ('1890-1930', 'Rail terminus at the old edge; freight line and foundries go east and downwind, commuter lines radiate.'),
    ('1962-1988', 'Highway era: R1 is cut through the grid and slums at the old edge (tunnelled on the waterfront), R2 follows as a bypass through farmland.'),
    ('2040+', 'Corporate megaprojects are grafted onto the ring road: Halcyon on the north hill, Solace on upstream terraces, Aurelian on the river hills, Meridian on the bay port, Orbital on the south-east cape. Each is walled and gated.'),
    ('2080+', 'Sea-level rise drowns the river-mouth lowland. Dams, the Bay Barrier and Tethys pier city take it over.'),
    ('always', 'Informal sprawl fills the slack: river flats, foundry row, rail-yard edges.'),
]


META = dict(
    key='A', slug='A_horseshoe_bay', title='A - HORSESHOE BAY',
    subtitle='Bay city: old port at the bay head, six districts on the arc',
    blurb=['The old port sits at the head of a horseshoe bay.', 'R1 hugs the old edge, R2 circles everything and',
           'closes across a storm-surge barrier at the mouth.'],
    skip=set(),
    evo=EVO,
    notes={
        'halcyon': 'Surveillance. Pyramid on the N hill, sees the core.',
        'solace': 'Biotech. Upstream NW terraces, twin-helix tower.',
        'orbital': 'Aerospace. SE cape; launches over open sea.',
        'meridian': 'Freight. Bay-shore port, yards, castle on the quay.',
        'aurelian': 'Finance/politics. Seven hills on the river west.',
        'tethys': 'Ocean tech. Pier city over the drowned SW quarter.',
    },
)
