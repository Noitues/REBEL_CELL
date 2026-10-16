"""Design A2 - HORSESHOE BAY, refined. Rebalanced corp distances, sprawl-coloured old city with a perimeter ring,
proper ramps and interchanges, Meridian freight hub (rail + highway alongside the HQ, rail ends at a big container
port), Tethys drowned quarter behind dams, smooth curves, dense low-rise suburbs, named neighbourhoods."""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageChops

from citymap import COL, INDUSTRY, SLUM, TEXT, tint
from citymap2 import CityMap2
from geom import (Noise, blob, catmull, circle_pts, ellipse_pts, mix, offset_line, plen, pt_at, rect_pts, resample, rot,
                  sub)

OUT = os.path.join(os.path.dirname(__file__), '..')
SPRAWL = (208, 144, 92)
COL['centre'] = SPRAWL
SUB_LINE = (196, 186, 170)
SUB_LOT = (180, 166, 146)
U2M = 20.0     # world units -> metres

LM = []          # landmarks
NEIGH = []       # neighbourhoods
CHECKPOINTS = []


def ell(cx, cy, rx, ry, n, start_deg=0.0, wob=0.0, seed=0):
    out = []
    for i in range(n):
        t = math.radians(start_deg + 360.0 * i / n)
        k = 1 + wob * math.sin(3 * t + seed)
        out.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    return out


def lm(kind, name, pos, **kw):
    d = dict(kind=kind, name=name, pos=(round(pos[0], 2), round(pos[1], 2)))
    d.update(kw)
    LM.append(d)


def runs_from(pts_iter, mk, minlen):
    runs, cur = [], []
    for p in pts_iter:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < 1000 and 0 <= y < 1000 and mk[y, x]:
            cur.append(p)
        else:
            if len(cur) >= minlen:
                runs.append(cur)
            cur = []
    if len(cur) >= minlen:
        runs.append(cur)
    return runs


def build():
    m = CityMap2(seed=11)
    C = (505.0, 470.0)           # old-city centre
    # ------------------------------------------------------------- coast + terrain
    coast = [(-60, 760), (40, 775), (130, 810), (220, 850), (300, 885), (360, 905), (392, 895),
             (386, 860), (362, 815), (340, 765), (330, 715), (342, 665), (375, 625), (425, 600), (500, 592),
             (575, 600), (625, 625), (658, 665), (670, 715), (660, 765), (638, 815), (614, 860), (608, 895),
             (655, 915), (730, 930), (800, 925), (860, 895), (910, 850), (940, 790), (955, 700), (960, 620),
             (958, 540), (962, 460), (960, 380), (970, 290), (990, 200), (1010, 120)]
    closing = [(1100, 120), (1100, 1100), (-100, 1100), (-100, 760)]
    m.set_ocean(coast, closing, noise_amp=4.0)
    bumps = [
        (535, 205, 75, 62, 0.95, 0.0), (480, 110, 260, 70, 0.55, 0.1), (270, 250, 85, 70, 0.55, 0.0),
        (110, 430, 26, 26, 0.38, 0), (180, 410, 24, 24, 0.36, 0), (95, 520, 26, 26, 0.34, 0),
        (150, 570, 24, 24, 0.34, 0), (115, 620, 22, 22, 0.30, 0), (60, 480, 24, 24, 0.30, 0),
        (790, 160, 120, 60, 0.30, 0.3), (880, 330, 70, 110, 0.25, 0.0), (520, 440, 90, 70, 0.14, 0.0),
        (60, 100, 120, 90, 0.35, 0.2),
    ]
    m.base(bumps)
    # ------------------------------------------------------------- water
    river = m.river([(405, -20), (400, 60), (396, 150), (398, 250), (392, 330), (360, 395), (318, 440), (282, 500),
                     (262, 560), (262, 620), (285, 680), (318, 725), (338, 748)], 3.0, 9.0, jitter=3.0,
                    name='Veyra River')
    m.lake([(30, 70), (80, 60), (110, 85), (95, 115), (50, 115)], name='Westmere Reservoir')
    m.river([(455, 592), (455, 545), (445, 505), (435, 470)], 2.6, 2.6, smooth=True, name='Saltcut Canal', kind='canal')
    m.river([(548, 592), (548, 550), (565, 515)], 2.6, 2.6, smooth=True, name='Tannery Canal', kind='canal')
    lagoon_poly = [(260, 705), (310, 687), (355, 695), (382, 735), (378, 805), (340, 845), (290, 837), (250, 805),
                   (232, 755)]
    m.drowned(lagoon_poly, seed=4)
    lagoon_dense = catmull(lagoon_poly, closed=True, step=4.0)
    # ------------------------------------------------------------- districts (all smooth)
    r1_ctrl = ell(C[0], C[1], 160, 100, 16, 60, 0.025, 1.0)
    core = ell(C[0], C[1], 148, 88, 16, 60, 0.025, 1.0)
    centre = m.zone('centre', core, COL['centre'], 0.36)
    halc = m.zone('halcyon', [(430, 175), (480, 130), (560, 120), (625, 155), (645, 215), (620, 275), (560, 300),
                              (485, 295), (440, 255)], COL['halcyon'], 0.26)
    sol = m.zone('solace', [(170, 200), (240, 168), (320, 185), (365, 230), (358, 300), (300, 335), (228, 330),
                            (178, 280)], COL['solace'], 0.24)
    aur = m.zone('aurelian', [(55, 400), (125, 363), (205, 385), (245, 435), (250, 520), (238, 605), (180, 650),
                              (105, 635), (60, 570), (40, 480)], COL['aurelian'], 0.24)
    teth = m.zone('tethys', [(130, 700), (200, 667), (272, 677), (335, 701), (360, 750), (360, 805), (345, 841),
                             (300, 847), (240, 821), (170, 767)], COL['tethys'], 0.24)
    mer = m.zone('meridian', [(672, 640), (740, 610), (820, 625), (870, 670), (885, 740), (860, 810), (790, 835),
                              (710, 825), (672, 775), (662, 705)], COL['meridian'], 0.24)
    orb = m.zone('orbital', [(800, 380), (870, 360), (930, 395), (950, 470), (942, 550), (890, 588), (820, 562),
                             (795, 480)], COL['orbital'], 0.24)
    # old city: sprawl texture (dense organic lots)
    cs = tint(SPRAWL, 0.35)
    m.tex_grid(centre, 23, 7.0, 6.0, jitter=0.35, warp_amp=7, warp_wl=70, gap=0.2, major=5, color=cs, a_minor=0.5,
               a_major=0.8, seed=1)
    m.tex_walks(centre, 160, (25, 80), 0.35, color=cs, a=0.55, seed=1)
    m.tex_slum(centre, 1.45, (232, 160, 104), 0.7, seed=3, size=(0.8, 1.9))
    # corp textures
    m.tex_super(halc, 6, 30, tint(COL['halcyon'], 0.3), seed=2)
    m.tex_curvi(sol, (262, 255), 15, 140, 8, 0, 6.28, 0.3, 24, tint(COL['solace'], 0.3), 0.5, cul=60, seed=3)
    m.tex_radial(aur, (205, 530), 14, 80, 20, 9, tint(COL['aurelian'], 0.3), 0.55, seed=4)
    m.tex_grid(aur, -12, 12, jitter=0.1, major=3, color=tint(COL['aurelian'], 0.3), a_minor=0.35, a_major=0.5, seed=5)
    m.tex_super(teth, -10, 26, tint(COL['tethys'], 0.3), seed=6)
    m.tex_super(mer, 12, 36, tint(COL['meridian'], 0.3), seed=7)
    m.tex_super(orb, 0, 40, tint(COL['orbital'], 0.3), seed=8, fill_prob=0.5)
    # ------------------------------------------------------------- parks (named)
    m.park(m.strip_poly(river, 14, 0.18, 0.62), name='Veyra Greenway', seed=1, free=True, smooth=False)
    m.park([(700, 110), (790, 100), (850, 150), (800, 205), (715, 195)], name='Kestrel Forest', seed=2, free=True)
    m.park([(250, 52), (330, 40), (385, 78), (335, 132), (262, 122)], name='Ridge Woods', seed=3, free=True)
    m.park([(630, 560), (662, 575), (668, 625), (640, 615)], name='Bay Gardens', seed=4, free=True)
    m.park([(0, 300), (120, 280), (150, 350), (60, 392), (0, 380)], name='West Heath', seed=5, free=True)
    m.park([(655, 355), (715, 325), (740, 395), (690, 430)], name='Kingsway Green', seed=6, free=True)
    m.park([(70, 410), (110, 400), (122, 450), (82, 462)], name='Aurelian Gardens', seed=7)
    m.park([(190, 230), (250, 215), (262, 262), (212, 282)], name='Solace Arboretum', seed=8)
    m.park([(436, 420), (470, 408), (486, 446), (452, 460)], name='Founders Park', seed=9, a=0.7)
    m.park([(548, 485), (584, 478), (590, 520), (556, 528)], name='The Commons', seed=10, a=0.7)
    m.park([(900, 600), (950, 590), (958, 660), (915, 670)], name='Orbital Dunes', seed=11, free=True)
    m.park([(780, 860), (860, 850), (880, 890), (800, 905)], name='Meridian Wetlands', seed=12, free=True)
    m.park([(745, 430), (785, 425), (790, 468), (750, 474)], name='Eastside Common', seed=13, free=True)
    m.park([(15, 640), (85, 650), (100, 720), (30, 730)], name='Hawthorn Woods', seed=14, free=True)
    m.park([(560, 40), (640, 32), (655, 66), (575, 74)], name='Northmere Fen', seed=15, free=True)
    m.built([(298, 586), (330, 582), (340, 620), (310, 635)], (110, 120, 110), 0.7, free=True, name='Old Necropolis',
            kind='cemetery')
    m.built([(735, 380), (770, 376), (775, 412), (739, 416)], (110, 120, 110), 0.7, free=True, name='Hill Cemetery',
            kind='cemetery')
    m.plaza([(488, 458), (514, 458), (514, 484), (488, 484)], name='Grand Plaza')
    m.plaza([(190, 466), (224, 466), (224, 496), (190, 496)], name='The Forum')
    m.plaza([(515, 300), (545, 300), (545, 314), (515, 314)], name='Gate Plaza')
    # ------------------------------------------------------------- Meridian port and logistics
    port_poly = [(668, 662), (752, 656), (758, 806), (668, 806)]
    term = m.built(port_poly, (110, 120, 138), 0.58, name='Port of Meridian (container terminal)', kind='container_terminal')
    m.container_yard(710, 732, 80, 130, 0, clip=term)
    m.built([(800, 646), (886, 640), (890, 678), (804, 684)], (60, 64, 76), 0.8, name='Meridian Intermodal Yard',
            kind='rail_yard')
    m.industry([(832, 702), (884, 706), (888, 792), (842, 810)], name='Meridian Works', seed=2, free=False, angle=12)
    m.industry([(690, 520), (745, 505), (768, 560), (715, 590), (685, 570)], name='Foundry Row', seed=3, angle=-20)
    m.built([(626, 828), (662, 822), (670, 862), (636, 872)], (90, 96, 112), 0.7, free=True, name='Bay Power Station',
            kind='power')
    m.built([(840, 215), (890, 208), (900, 255), (850, 262)], (70, 90, 100), 0.7, free=True, name='Cold Campus data centres',
            kind='data_centre')
    m.built([(880, 820), (915, 810), (925, 840), (885, 850)], (130, 110, 90), 0.6, free=True, name='Bayshore Sewage Works',
            kind='sewage')
    m.built([(900, 300), (940, 296), (944, 330), (905, 334)], (100, 130, 90), 0.6, free=True, name='Scrapworks',
            kind='recycling')
    m.built([(665, 236), (790, 216), (815, 250), (800, 292), (680, 300)], (40, 46, 60), 0.85, free=True,
            name='Veyra Airport', kind='airport')

    def slum_patch(name, poly, seed):
        mk, pts = m.free_mask(poly, True)
        m._feat('slum', name, pts)
        m.fill_mask(mk, SLUM, 0.12)
        m.tex_slum(mk, 0.7, SLUM, 0.66, seed=seed)
        m.line(pts + [pts[0]], SLUM, 0.8, 0.5, clip=m.dry)
    slum_patch('River Flats', [(312, 425), (346, 418), (346, 520), (336, 575), (310, 580), (305, 520)], 1)
    slum_patch('Rail Slums', [(690, 598), (740, 605), (748, 625), (696, 630)], 2)
    slum_patch('Stilt Town', [(215, 672), (262, 662), (268, 700), (224, 716)], 3)
    slum_patch('Spur Stacks', [(800, 300), (835, 295), (840, 345), (805, 350)], 4)
    slum_patch('North Spur', [(330, 345), (385, 336), (392, 388), (345, 402)], 5)
    slum_patch('Eastgate Stacks', [(668, 400), (700, 410), (712, 470), (672, 482), (666, 440)], 6)
    undercity_poly = [(400, 420), (470, 395), (560, 400), (620, 440), (630, 500), (590, 545), (520, 560), (450, 545),
                      (400, 500)]
    m.undercity(undercity_poly)
    # ------------------------------------------------------------- suburbs: dense low-rise, rail grid then rings
    occ0 = m.occupied.copy()
    core_poly_mask = m.poly_mask(catmull(r1_ctrl, closed=True, step=3.0))
    sub_in, _ = m.free_mask(ell(C[0], C[1], 235, 175, 18, 0, 0.05, 2.0), True)
    m.img.paste(SUB_LINE, mask=sub_in.point(lambda v: int(v * 0.08)))
    m.tex_grid(sub_in, -8, 8.5, jitter=0.06, major=4, color=SUB_LINE, a_minor=0.36, a_major=0.55, seed=2, gap=0.0,
               w_major=1.3)
    m.tex_lots(sub_in, -8, 8.5, color=SUB_LOT, a=0.62, seed=2)
    sub_out, _ = m.free_mask(ell(C[0], C[1] + 6, 470, 430, 22, 0, 0.05, 3.0), True)
    m.img.paste(SUB_LINE, mask=sub_out.point(lambda v: int(v * 0.06)))
    m.tex_suburb_ellipses(sub_out, C, 160, 100, 70, 420, 7.5, SUB_LINE, SUB_LOT, seed=3, a_street=0.3, a_lot=0.55)
    hint, _ = m.free_mask([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], False)
    m.img.paste((88, 110, 78), mask=hint.point(lambda v: int(v * 0.12)))
    m.tex_grid(hint, 14, 26, 22, jitter=0.2, warp_amp=14, warp_wl=180, gap=0.35, seg=(40, 120), major=0,
               color=(120, 140, 108), a_minor=0.3, seed=5)
    m.tex_dots(hint, 500, (50, 90, 54), 0.5, 1.4, seed=9)
    m.grid_ticks()
    # ------------------------------------------------------------- road network
    R1 = m.add_road('R1 Perimeter Ring', r1_ctrl, 'ring', closed=True, tunnels=[(0.02, 0.15)])
    R2pts = [(394, 890), (350, 880), (305, 862), (262, 838), (232, 808), (222, 765), (232, 722), (212, 690), (150, 682),
             (95, 654), (52, 598), (30, 520), (32, 430), (48, 335), (92, 240), (160, 160), (260, 105), (380, 75),
             (500, 62), (620, 72), (740, 100), (830, 135), (870, 185), (850, 250), (815, 320), (788, 400), (777, 470),
             (780, 540), (800, 595), (850, 612), (900, 642), (928, 702), (922, 765), (895, 825), (850, 865), (790, 890),
             (725, 903), (668, 903), (615, 890), (555, 894), (500, 896), (445, 894)]
    R2 = m.add_road('R2 Outer Ring', R2pts, 'ring', closed=True)
    m.add_road('N1 Halcyon Radial', [(470, 372), (468, 300), (466, 230), (472, 160), (482, 100), (492, 62)], 'motorway')
    m.add_road('N2 Solace Parkway', [(405, 405), (386, 350), (372, 290), (366, 235), (350, 182), (318, 138), (268, 105)], 'motorway')
    m.add_road('W1 Via Aurelia', [(352, 480), (300, 486), (250, 484), (190, 478), (100, 470), (30, 470)], 'motorway')
    m.add_road('SW1 Tethys Link', [(410, 540), (370, 585), (335, 625), (300, 665), (262, 700), (236, 738)], 'motorway')
    m.add_road('NE1 Airport Expressway', [(615, 372), (662, 332), (712, 292), (768, 240), (822, 180), (862, 165)], 'motorway')
    m.add_road('E1 Eastern Highway', [(648, 448), (715, 455), (775, 468)], 'motorway')
    m.add_road('T1 Port Expressway', [(922, 768), (885, 778), (840, 780), (790, 779), (740, 780), (700, 781), (672, 783)], 'truck')
    m.add_road('T2 Foundry Link', [(846, 640), (818, 600), (776, 560), (730, 525), (690, 516), (646, 514)], 'truck')
    m.add_road('T3 Rocket Road', [(872, 632), (868, 585), (858, 540), (842, 500), (814, 482)], 'truck')
    arts = [
        ('Grand Avenue', [(505, 362), (505, 420), (507, 480), (503, 572)], True),
        ('Via Sacra', [(337, 480), (430, 478), (505, 476), (580, 478), (672, 480)], True),
        ('Bayfront Boulevard', [(425, 578), (470, 581), (505, 581), (545, 580), (588, 577)], False),
        ('Halcyon Gate Road', [(566, 392), (558, 350), (550, 322), (545, 300)], True),
        ('Airport Link', [(640, 262), (700, 262), (745, 262)], True),
        ('Solace Spine', [(262, 335), (236, 400), (210, 450)], False),
        ('Meridian Main', [(672, 632), (740, 622), (810, 628), (872, 650), (905, 690)], True),
        ('Orbital Boulevard', [(777, 470), (830, 462), (868, 436), (900, 404)], True),
        ('Dam Avenue', [(195, 676), (218, 705)], False),
        ('Riverside Drive', [(412, 360), (412, 250), (416, 160)], True),
        ('Tethys Quay Road', [(298, 730), (328, 690), (342, 660)], False),
        ('Forum Way', [(205, 500), (262, 512)], False),
        ('Port Gate Road', [(740, 632), (738, 700), (736, 780)], True),
    ]
    for nm, pts, rp in arts:
        m.add_road(nm, pts, 'arterial', ramp=rp)
    # auto radial arterials and collector rings in the suburbs (street hierarchy)
    avail = ImageChops.subtract(ImageChops.multiply(m.poly_mask(catmull(R2pts, closed=True, step=3.0)), m.dry), occ0)
    avail = ImageChops.subtract(avail, m.poly_mask(catmull(ell(C[0], C[1], 168, 108, 16, 60, 0.025, 1.0), closed=True, step=3.0)))
    avail = ImageChops.subtract(avail, m.poly_mask(catmull(R2pts, closed=True, step=3.0)).point(lambda v: 0))
    mk = m.mnp(avail)
    nz = Noise(77, 3, 140.0)
    st_names = ['Kingsway', 'Harrow Road', 'Mill Lane', 'Beacon Avenue', 'Quarry Road', 'Elm Avenue', 'Chandler Road',
                'Ferry Road', 'Orchard Avenue', 'Smith Street', 'Hollow Road', 'Cinder Lane', 'Tanner Avenue', 'Saltpan Road',
                'Cross Street', 'Ropewalk', 'Gasworks Road', 'Bridle Way']
    n_art = 14
    for i in range(n_art):
        th = math.radians(8 + i * 360.0 / n_art)
        pts = []
        r = 150.0
        while r < 480:
            sw = nz(r, i * 37.0) * 5.0
            pts.append((C[0] + (r * 1.0) * math.cos(th) * 1.15 - math.sin(th) * sw, C[1] + r * math.sin(th) * 0.88 + math.cos(th) * sw))
            r += 3.0
        for k, run in enumerate(runs_from(pts, mk, 16)):
            flag = (i % 2 == 0)
            if flag:
                def ext(a, b, L=11.0):
                    dd = math.hypot(a[0] - b[0], a[1] - b[1]) or 1.0
                    return (a[0] + (a[0] - b[0]) / dd * L, a[1] + (a[1] - b[1]) / dd * L)
                run = [ext(run[0], run[3])] + list(run) + [ext(run[-1], run[-4])]
            m.add_road('%s %d' % (st_names[i % len(st_names)], k + 1), run, 'arterial', smooth=True, step=3.0, ramp=flag)
    for gi, g in enumerate((42, 92, 145, 200)):
        rx, ry = 160 + g, 100 + g
        pts = [(C[0] + rx * math.cos(t), C[1] + ry * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 420)]
        for k, run in enumerate(runs_from(pts, mk, 14)):
            m.add_road('Ring Collector %d.%d' % (gi + 1, k + 1), run, 'collector', smooth=True, step=3.0)
    # ---- rail
    fm_pts = [(868, -10), (862, 100), (852, 200), (838, 300), (826, 400), (826, 500), (834, 570), (846, 618), (838, 650),
              (808, 665), (760, 668), (716, 671), (690, 676)]
    FM = m.add_rail('Freight Main (to Port of Meridian)', fm_pts, 'freight')
    yard_main = sub(FM['pts'], 0.86, 0.985)
    for k in (-5, 5, 10):
        m.add_rail('yard track', offset_line(yard_main, k), 'freight', smooth=False)
    C1 = m.add_rail('C1 West Line', [(0, 432), (80, 445), (150, 468), (230, 486), (300, 498), (380, 492), (450, 478), (505, 470)], 'commuter')
    C2 = m.add_rail('C2 North Line', [(505, 470), (560, 420), (625, 365), (655, 290), (670, 200), (675, 100), (670, -10)], 'commuter')
    C3 = m.add_rail('C3 Airport Line', [(505, 470), (570, 430), (640, 395), (700, 335), (745, 280)], 'commuter')
    C4 = m.add_rail('C4 Southeast Line', [(505, 470), (565, 505), (625, 555), (675, 600), (715, 640), (740, 656)], 'commuter')
    C5 = m.add_rail('C5 Spaceport Line', [(505, 478), (600, 484), (690, 488), (765, 486), (812, 482)], 'commuter')
    M1 = m.add_rail('M1 Loop', ell(505, 470, 88, 55, 16, 0, 0.0), 'metro', closed=True)
    M2 = m.add_rail('M2', [(310, 335), (340, 380), (385, 425), (445, 462), (505, 470), (570, 510), (625, 570), (665, 640), (700, 700)], 'metro', tunnels=[(0.3, 0.7)])
    M3 = m.add_rail('M3', [(296, 722), (300, 680), (312, 640), (335, 595), (372, 548), (430, 505), (505, 470), (520, 410), (522, 340)], 'metro', tunnels=[(0.3, 0.7)])
    m.draw_rails()
    m.draw_roads()
    inter = m.auto_interchanges(forced={('R1 Perimeter Ring', 'N1 Halcyon Radial'): 'cloverleaf',
                                        ('R1 Perimeter Ring', 'W1 Via Aurelia'): 'cloverleaf',
                                        ('R1 Perimeter Ring', 'NE1 Airport Expressway'): 'stack'})
    # stations
    def stations(line, specs, kind):
        for f, nm in specs:
            p, _a = pt_at(line['pts'], plen(line['pts']) * f)
            m.station(p[0], p[1], kind, name=nm, lines=[line['name']])
            if kind == 'rail':
                m.text(p[0] + 4, p[1] - 8, nm, 6.5, (225, 230, 240), weight='Regular')
    LABEL_ST = True
    stations(C1, [(0.1, 'Hawthorn'), (0.3, 'Aurelian Gate'), (0.5, 'The Forum'), (0.67, 'Westbury'), (0.84, 'River Flats')], 'rail')
    stations(C2, [(0.2, 'Hillfoot'), (0.38, 'Halcyon East Gate'), (0.58, 'Kestrel Gate'), (0.8, 'Lakeside')], 'rail')
    stations(C3, [(0.3, 'Kingsway'), (0.55, 'Eastgate'), (0.8, 'Airfield Village'), (0.99, 'Veyra Airport')], 'rail')
    stations(C4, [(0.3, 'Saltmarket Halt'), (0.58, 'Harbourside'), (0.99, 'Meridian Yards')], 'rail')
    stations(C5, [(0.35, 'Cinder Lane'), (0.62, 'Foundry Row'), (0.99, 'Spaceport Gate')], 'rail')
    stations(M1, [(i / 6.0, nm) for i, nm in enumerate(['Knoll', 'Lantern', 'Saltmarket', 'Old Port', 'Tanners', 'Founders'])], 'metro')
    stations(M2, [(0.04, 'Solace Gate'), (0.16, 'Quarry Rise'), (0.3, 'River Flats'), (0.62, 'Saltmarket East'), (0.8, 'Harbourside Metro'), (0.97, 'Port Halt')], 'metro')
    stations(M3, [(0.04, 'Pier Gate'), (0.17, 'Dam End'), (0.3, 'Aurelian South'), (0.46, 'Tanners West'), (0.62, 'Founders West'), (0.83, 'Lantern North'), (0.97, 'Halcyon Gate')], 'metro')
    for p, nm in (((505, 470), 'Old Central'), ((740, 656), 'Meridian Yards Hub'), ((745, 280), 'Airport Hub'),
                  ((522, 340), 'Halcyon Gate Hub'), ((812, 482), 'Spaceport Gate Hub')):
        m.station(p[0], p[1], 'hub', name=nm, lines=['multimodal'])
    m.station(846, 640, 'freight', name='Meridian Intermodal Yard', lines=[FM['name']])
    m.station(692, 676, 'freight', name='Port of Meridian rail terminal', lines=[FM['name']])
    # ------------------------------------------------------------- walls, gates, sea defences
    for key in ('halcyon', 'solace', 'tethys', 'meridian', 'orbital', 'aurelian'):
        w = m.wall(m.z[key]['poly'], COL[key], closed=True, name=key)
        for g in m.gates_on(w):
            CHECKPOINTS.append(dict(district=key, pos=(round(g[0], 2), round(g[1], 2))))
    for i, run in enumerate(m.coast_seg(lambda p: 330 < p[0] < 680 and 590 < p[1] < 895 and not (p[0] < 400 and p[1] > 690))):
        m.seawall(run, name='Bay sea wall %d' % (i + 1))
    for i, run in enumerate(m.coast_seg(lambda p: p[0] > 612 and p[1] > 900 or p[0] > 905 and 300 < p[1] < 900)):
        m.seawall(run, name='Outer sea wall %d' % (i + 1))
    m.dam([(396, 892), (486, 894)], name='Bay Barrier west leaf', kind='barrier')
    m.dam([(514, 894), (606, 889)], name='Bay Barrier east leaf', kind='barrier')
    m.dam([(235, 720), (272, 695), (320, 683), (356, 687)], name='Tethys north dam')
    m.dam([(235, 720), (224, 765), (235, 805), (265, 833), (310, 847), (356, 859)], name='Tethys west dam')
    # undercity network
    m.undercity_net([[(430, 450), (505, 420), (580, 440), (610, 490), (570, 530), (505, 540), (440, 520), (420, 480), (430, 450), (505, 420)],
                     [(505, 420), (505, 470), (500, 540), (500, 585)], [(420, 480), (380, 470), (340, 440)],
                     [(610, 490), (650, 500), (690, 520)], [(570, 530), (600, 570), (630, 600)]],
                    [(500, 585, 'Port Gate'), (340, 440, 'Flats Stair'), (690, 520, 'Foundry Shaft'),
                     (630, 600, 'Bayshore Lift'), (505, 420, 'Knoll Well'), (440, 520, 'Tanners Sink'), (580, 440, 'Lantern Hatch')])
    # ferries and offshore wind
    m.ferry([(500, 612), (450, 700), (390, 770), (355, 800)])
    m.ferry([(500, 612), (580, 700), (630, 760), (664, 775)])
    m.ferry([(500, 612), (500, 760), (500, 890), (500, 1000)])
    m.windfarm([(380, 945), (620, 945), (640, 995), (380, 995)])
    # drones
    m.drone_corridor([(535, 205), (640, 330), (700, 450), (770, 640)])
    m.drone_corridor([(535, 205), (420, 330), (330, 440), (240, 540)])
    m.drone_corridor([(535, 205), (640, 250), (745, 262)])
    m.drone_corridor([(535, 205), (300, 262)])
    m.drone_corridor([(535, 205), (700, 300), (880, 440)])
    # ------------------------------------------------------------- landmarks (HQs and civic)
    m.panopticon(535, 205, 36, COL['halcyon'], cone_to=C)
    lm('hq', 'The Panopticon (Halcyon HQ)', (535, 205), district='halcyon', style='pyramid', radius_m=36 * 1.25 * U2M)
    m.helix(265, 255, 27, -0.5)
    lm('hq', 'Twin Helix Tower (Solace HQ)', (265, 255), district='solace', style='twin_helix', radius_m=27 * 1.5 * U2M)
    m.launch_ring(915, 470, 34, 0.0, zone_r=80)
    lm('hq', 'Launch Ring (Orbital HQ)', (915, 470), district='orbital', style='launch_ring', ring_radius_m=34 * U2M,
       exclusion_radius_m=80 * U2M, azimuth_deg=90.0)
    m.gantry_castle(790, 720, 28, 0.0, cranes=(math.pi, math.pi * 0.8), crane_len=2.2)
    lm('hq', 'Gantry-Crane Castle (Meridian HQ)', (790, 720), district='meridian', style='gantry_castle',
       half_size_m=28 * 1.1 * U2M, crane_bearings_deg=[270.0, 252.0])
    m.circus(215, 556, 32, 0.3)
    lm('hq', 'Circus Aurelius (Aurelian HQ)', (215, 556), district='aurelian', style='colosseum_circus', radius_m=32 * 1.3 * U2M)
    m.pier_city(322, 770, 66, 0.15, n=9, spread=2.0)
    lm('hq', 'Floating Pier City (Tethys HQ)', (322, 770), district='tethys', style='pier_city', radius_m=66 * 1.4 * U2M)
    m.port_piers([(668, 672, 55, 8, math.pi), (668, 704, 55, 8, math.pi), (668, 736, 55, 8, math.pi),
                  (666, 768, 55, 8, math.pi), (662, 798, 52, 8, math.pi)])
    m.airport(745, 258, 0.05)
    glyph_items = [
        ((705, 425, 'stadium'), 'Founders Stadium'), ((530, 440, 'hospital'), 'Central Hospital'),
        ((300, 262, 'hospital'), 'Solace Medical'), ((262, 790, 'hospital'), 'Hyperbaric Clinic'),
        ((680, 380, 'hospital'), 'Eastside General'), ((445, 425, 'university'), 'Old University'),
        ((240, 215, 'university'), 'Solace Institute'), ((178, 500, 'university'), 'Forum Academy'),
        ((480, 440, 'market'), 'Night Bazaar'), ((500, 585, 'market'), 'Harbour Fish Market'),
        ((205, 486, 'market'), 'Forum Market'), ((690, 818, 'market'), 'Quay Bazaar'),
        ((565, 505, 'market'), 'Saltmarket'), ((690, 455, 'market'), 'Eastgate Market'),
        ((646, 848, 'power'), 'Bay Power Station'), ((715, 575, 'power'), 'Foundry Substation'),
        ((84, 95, 'water'), 'Westmere Waterworks'), ((900, 832, 'sewage'), 'Bayshore Sewage Works'),
        ((318, 608, 'cemetery'), 'Old Necropolis'), ((755, 396, 'cemetery'), 'Hill Cemetery'),
        ((745, 238, 'airport'), 'Veyra Airport'), ((865, 236, 'datacentre'), 'Cold Campus'),
        ((352, 845, 'datacentre'), 'Cable Landing'), ((352, 445, 'arcology'), 'River Stack'),
        ((690, 420, 'arcology'), 'Eastgate Stack'), ((440, 345, 'arcology'), 'Hillfoot Stack'),
        ((590, 258, 'megastructure'), 'Eye Tower'), ((218, 300, 'megastructure'), 'Spire'),
        ((840, 792, 'megastructure'), 'Crane Yard Tower'), ((860, 430, 'megastructure'), 'Assembly Hall'),
        ((922, 316, 'recycling'), 'Scrapworks'), ((520, 495, 'rebel'), 'REBEL CELL hideout'),
        ((160, 436, 'church'), 'Aurelian Basilica'), ((230, 305, 'school'), 'Solace Academy'),
    ]
    for (x, y, k), nm in glyph_items:
        m.glyph(k, x, y, 7.4)
        lm('glyph:' + k, nm, (x, y))
    # ------------------------------------------------------------- labels and neighbourhoods
    m.text(535, 100, 'HALCYON', 21, tint(COL['halcyon'], 0.4), spacing=5)
    m.text(270, 150, 'SOLACE', 21, tint(COL['solace'], 0.4), spacing=5)
    m.text(140, 356, 'AURELIAN CONCORD', 19, tint(COL['aurelian'], 0.4), spacing=4)
    m.text(135, 878, 'TETHYS DEEP', 21, tint(COL['tethys'], 0.4), spacing=5, angle=18)
    m.text(780, 598, 'MERIDIAN', 20, tint(COL['meridian'], 0.4), spacing=5)
    m.text(985, 470, 'ORBITAL', 19, tint(COL['orbital'], 0.5), spacing=5, angle=90)
    m.text(505, 392, 'THE OLD CITY', 22, tint(SPRAWL, 0.55), spacing=4)
    m.text(530, 512, 'REBEL CELL', 11, (255, 110, 110), spacing=2)
    m.text(500, 740, 'THE HORSESHOE', 15, (150, 200, 235), spacing=8, weight='SemiBold', halo=False)
    m.text(500, 914, 'BAY BARRIER', 10, (210, 225, 240), spacing=3, weight='SemiBold')
    m.text(365, 702, 'veyra estuary', 10, (150, 200, 235), weight='Regular', halo=False, angle=-35)
    nb = [
        ('The Knoll', 505, 436, 'old_core', 26), ('Founders Row', 440, 478, 'old_core', 24), ('Saltmarket', 568, 520, 'old_core', 24),
        ('Old Port', 520, 562, 'old_core', 22), ('Tanners Reach', 425, 540, 'old_core', 22), ('Lantern Quarter', 585, 455, 'old_core', 22),
        ('Hillfoot', 505, 338, 'rail_grid', 30), ('Kingsway', 620, 345, 'rail_grid', 30), ('Eastgate', 700, 440, 'rail_grid', 28),
        ('Cinder Lane', 702, 548, 'industrial', 26), ('Harbourside', 650, 596, 'rail_grid', 24), ('Westbury', 320, 535, 'rail_grid', 26),
        ('River Flats', 330, 470, 'informal', 26), ('Tannery Row', 340, 598, 'rail_grid', 24), ('Ferryside', 305, 650, 'suburb', 26),
        ('Greenfield', 735, 360, 'suburb', 30), ('Lakeside', 705, 160, 'suburb', 30), ('Kestrel Heights', 590, 70, 'suburb', 26),
        ('Quarry Rise', 330, 395, 'suburb', 22), ('Hawthorn', 60, 330, 'suburb', 26), ('Dockyard Estate', 640, 700, 'suburb', 20),
        ('Airfield Village', 745, 330, 'suburb', 22), ('Beacon Hill', 560, 270, 'suburb', 20), ('Orchard End', 565, 850, 'suburb', 26),
        ('Stilt Town', 242, 690, 'informal', 22), ('Rail Slums', 718, 616, 'informal', 18),
    ]
    for name, x, y, kind, r in nb:
        NEIGH.append(dict(name=name, pos=(x, y), kind=kind, radius=r))
        m.text(x, y, name, 8, (232, 226, 214), weight='SemiBold', spacing=0.5)
    for (nm, x, y) in [('Veyra Greenway', 395, 215), ('Kestrel Forest', 775, 150), ('Ridge Woods', 320, 90), ('Bay Gardens', 648, 592),
                       ('West Heath', 60, 345), ('Founders Park', 462, 440), ('The Commons', 570, 505), ('Orbital Dunes', 930, 630),
                       ('Meridian Wetlands', 825, 880), ('Hawthorn Woods', 55, 690), ('Northmere Fen', 605, 52), ('Aurelian Gardens', 96, 438)]:
        m.text(x, y, nm, 7.5, (170, 220, 170), weight='Regular', spacing=0.5)
    for (x, y, t) in [(700, 770, 'PORT OF MERIDIAN'), (846, 700, 'INTERMODAL YARD'), (745, 262, ''), (735, 214, 'AIRPORT'),
                      (880, 188, 'COLD CAMPUS'), (330, 840, 'DROWNED QUARTER'), (500, 603, ''), (738, 568, 'FOUNDRY ROW'),
                      (325, 625, 'NECROPOLIS'), (190, 487, 'THE FORUM'), (855, 338, ''), (80, 128, 'WESTMERE RES.')]:
        if t:
            m.text(x, y, t, 8.5, (214, 220, 232), spacing=1, weight='SemiBold')
    # station labels (selected)
    for p, nm in (((505, 470), 'Old Central'), ((740, 656), 'Meridian Yards'), ((522, 340), 'Halcyon Gate'), ((812, 482), 'Spaceport Gate'),
                  ((745, 280), 'Airport')):
        m.text(p[0] + 4, p[1] + 12, nm, 7.5, (255, 255, 255), weight='Bold')
    # shields
    for (x, y, t) in [(505, 372, 'R1'), (660, 520, 'R1'), (346, 520, 'R1'), (28, 530, 'R2'), (500, 62, 'R2'), (777, 470, 'R2'),
                      (500, 896, 'R2'), (928, 702, 'R2'), (468, 160, 'N1'), (368, 235, 'N2'), (140, 475, 'W1'), (300, 665, 'SW1'),
                      (768, 240, 'NE1'), (715, 455, 'E1'), (840, 780, 'T1'), (730, 525, 'T2'), (858, 540, 'T3')]:
        m.shield(x, y, t)
    # wind, frame
    m.line([(890, 62), (950, 62)], (200, 215, 235), 1.6, 0.9)
    m.poly([(960, 62), (948, 56), (948, 68)], (200, 215, 235), 0.9)
    m.text(920, 48, 'PREVAILING WIND', 9, (200, 215, 235), spacing=1.5, weight='SemiBold')
    m.scalebar(40, 965)
    m.north(930, 955)
    m.title_block(34, 38, 'A2  -  HORSESHOE BAY', 'refined plan  /  even corp spacing  /  sprawl core  /  ramps and interchanges')
    m.layout_extra = dict(C=C, r1_ctrl=r1_ctrl, core=core, lagoon=lagoon_dense, bumps=bumps, coast_ctrl=coast, closing=closing,
                          port_poly=port_poly, undercity=undercity_poly, river=river, R2pts=R2pts)
    return m


def checks(m):
    out = []
    hq = {d['district']: d['pos'] for d in LM if d['kind'] == 'hq'}
    for dist_key, pos in hq.items():
        best_r = 1e9
        for r in m.roads:
            if r['cls'] in ('ring', 'motorway', 'truck'):
                best_r = min(best_r, m.min_dist_to([r['pts']], pos))
        best_t = min(m.min_dist_to([r['pts']], pos) for r in m.rails)
        out.append((dist_key, round(best_r, 1), round(best_t, 1)))
    ends = []
    for kind, items in (('road', m.roads), ('rail', m.rails)):
        for r in items:
            for e in (r['pts'][0], r['pts'][-1]):
                if math.hypot(e[0] - hq['meridian'][0], e[1] - hq['meridian'][1]) < 60:
                    ends.append((kind, r['name']))
    return out, ends, m.check_turns()


META = dict(
    key='A2', slug='A2_horseshoe_bay', title='A2 - HORSESHOE BAY',
    subtitle='Refined plan: even corp spacing, sprawl core, ramps and interchanges',
    blurb=['A rebalanced Horseshoe Bay. Every corp sits 5.2 to 7.9 km',
           'from the Rebel Cell. R1 rings the sprawl core; R2 rings the',
           'suburbs. Meridian sits between the port and the rail yard.'],
    skip=set(),
    notes={
        'centre': 'Sprawl-coloured dense low-rise core. Organic lanes, undercity.',
        'halcyon': 'Surveillance. N hill, sees the core and the ring.',
        'solace': 'Biotech. Upstream NW terraces, twin-helix tower.',
        'orbital': 'Aerospace. East coast flats; launches east over sea.',
        'meridian': 'Freight hub. HQ between the port and the yard.',
        'aurelian': 'Finance/politics. West-bank hills and forum.',
        'tethys': 'Ocean tech. Drowned SW quarter behind dams, pier city.',
    },
    evo=[
        ('c.1650', 'Fishing village and quay at the bay head; a ford where the river meets the bay.'),
        ('1750-1890', 'Walled port town on the knoll, organic lanes, two canals; rail-era grid outside the wall.'),
        ('1890-1930', 'Rail terminus (Old Central) at the old edge; freight and foundries east and downwind.'),
        ('1962-1988', 'R1 is cut round the old edge as the perimeter ring, R2 follows as the outer ring; cloverleaf and stack interchanges.'),
        ('1990-2040', 'Dense low-rise suburbs fill the ring between R1 and R2: rail grid inside, curved streets outside.'),
        ('2040+', 'Corp megaprojects grafted on: each is walled, gated, and entered by a motorway ramp.'),
        ('2080+', 'Sea-level rise drowns the river-mouth lowland: Tethys dams, barrier and pier city.'),
    ],
)


if __name__ == '__main__':
    import time
    t0 = time.time()
    m = build()
    rep = checks(m)
    print('HQ clearance (district, road dist, rail dist):', rep[0])
    print('Road/rail ends within 60 of Meridian HQ:', rep[1])
    print('Sharp turns:', rep[2])
    m.save_map(os.path.join(OUT, 'wip_a2.png'), 2000)
    print('done', round(time.time() - t0, 1))
