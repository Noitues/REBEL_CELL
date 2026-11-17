"""glyphs_hq: the missing raid weapon / device pictograms (21 weapons, 8 devices) in the raid glyph grammar
(raid_v3/src/raid_icons.py, bible 3.5): one flat white silhouette on a 512 grid, few dark cut-outs, the dark rounded
outline added at draw time by RaidGlyphs (0.075 x box); strokes >= 40/512, cut-outs >= 24/512; attacks pointed,
defences blocky; saved 256 px, white on transparent, alpha = coverage, the full 512 canvas (RaidGlyphs draws the whole
texture into its box, so the silhouette's placement on the canvas is its placement in the box).

    python glyphs_hq.py <glyph_dir> <locked_dir> <sheet_png> <fonts_dir>
        -> <glyph_dir>/raid_<id>.png for every new glyph, <sheet_png> (the review sheet)
"""
import math, os, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

S = 512

# id -> (kind, display name, idea)
NEW = {
    'BARRIER': ('weapon', 'Barrier Kit', 'road sawhorse: striped plank on legs (6 hp wall)'),
    'BLADE':   ('weapon', 'Monoblade', 'single-edged blade, point up (point-blank cut)'),
    'BOUNTYG': ('weapon', 'Bounty Carbine', 'carbine + coin (each kill pays)'),
    'BULWARK': ('weapon', 'Bulwark Plate', 'tall riot plate with a view slot (10 hp wall)'),
    'CHARGE':  ('weapon', 'Shaped Charge', 'block with a cone cut + burst (wall that blows)'),
    'COIL':    ('weapon', 'Overload Coil', 'tesla coil with a spark'),
    'CROSS':   ('weapon', 'Crossroads Cannon', 'wheeled cannon + crossing mark'),
    'DRONES':  ('weapon', 'Drone Swarm', 'three quadcopters'),
    'FLAK':    ('weapon', 'Flak Cannon', 'twin AA barrels + air burst'),
    'FLAMER':  ('weapon', 'Flamer', 'nozzle gun + flame jet'),
    'GL':      ('weapon', 'Grenade Launcher', 'drum launcher (revolver drum, fat barrel)'),
    'LANCE':   ('weapon', 'Pulse Lance', 'lance through a split plate (ignores armor)'),
    'LANEG':   ('weapon', 'Lane Gun', 'shots down a lane between road edges'),
    'LONG':    ('weapon', 'Long Rifle', 'sniper rifle: scope + bipod'),
    'MARKS':   ('weapon', 'Marksman Rifle', 'rifle scope, side view'),
    'MORTAR':  ('weapon', 'Mortar Tube', 'tube on a baseplate + shell'),
    'NAIL':    ('weapon', 'Nail Gun', 'nail driven into a plank (wall + shots)'),
    'PISTOL':  ('weapon', 'Suppressed Pistol', 'pistol with a long suppressor'),
    'PULSE':   ('weapon', 'Pulse Beam', 'emitter disc + beam + pulse arcs'),
    'SLICK':   ('weapon', 'Slick Grenade', 'grenade over a slick puddle'),
    'WIRE':    ('weapon', 'Razor Wire', 'strand with barbs'),
    'BEACON':  ('device', 'Beacon', 'warning light with rays'),
    'DECOY':   ('device', 'Decoy', 'target dummy on a stake'),
    'DRONE':   ('device', 'Repair Drone', 'side-view drone carrying a wrench'),
    'GATE':    ('device', 'Gate', 'turn arrow, straight ahead barred'),
    'LURE':    ('device', 'Lure', 'fish hook'),
    'MAST':    ('device', 'Relay Mast', 'lattice mast with waves both ways'),
    'SHOCK':   ('device', 'Shock Fence', 'two posts, wires, bolt'),
    'TAR':     ('device', 'Tar', 'dripping goo'),
}

# the existing glyph of each id (raid_look.tres before this pass)
EXISTING = {'JAMMER': 'raid_jammer', 'RAIL': 'raid_rail', 'SHOTGUN': 'raid_shotgun', 'SMG': 'raid_smg',
            'BARRICADE': 'picto_block', 'MINE': 'placeholder_bomb', 'SENTRY': 'raid_sentry'}

WEAPONS = ['BARRIER', 'BLADE', 'BOUNTYG', 'BULWARK', 'CHARGE', 'COIL', 'CROSS', 'DRONES', 'FLAK', 'FLAMER', 'GL',
           'JAMMER', 'LANCE', 'LANEG', 'LONG', 'MARKS', 'MORTAR', 'NAIL', 'PISTOL', 'PULSE', 'RAIL', 'SHOTGUN', 'SLICK',
           'SMG', 'WIRE']
DEVICES = ['BARRICADE', 'BEACON', 'DECOY', 'DRONE', 'GATE', 'LURE', 'MAST', 'MINE', 'SENTRY', 'SHOCK', 'TAR']
NAMES = {'JAMMER': 'Jammer Rig', 'RAIL': 'Rail Rifle', 'SHOTGUN': 'Breach Shotgun', 'SMG': 'SMG',
         'BARRICADE': 'Barricade', 'MINE': 'Mine', 'SENTRY': 'Sentry'}


def fname(gid):
    return 'raid_' + gid.lower()


# ---------------------------------------------------------------- drawing helpers (512 grid, L masks)
def layer():
    m = Image.new('L', (S, S), 0)
    return m, ImageDraw.Draw(m)


def rot(pts, deg, c=(256, 256)):
    t = math.radians(deg); cs, sn = math.cos(t), math.sin(t)
    return [(c[0] + (x - c[0]) * cs - (y - c[1]) * sn, c[1] + (x - c[0]) * sn + (y - c[1]) * cs) for x, y in pts]


def bar(d, a, b, w, fill=255):
    """a thick straight bar from a to b, width w (square ends)"""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0; n = math.hypot(dx, dy) or 1
    px, py = -dy / n * w / 2, dx / n * w / 2
    d.polygon([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], fill=fill)


def ring(d, c, ro, ri, fill=255):
    d.ellipse([c[0] - ro, c[1] - ro, c[0] + ro, c[1] + ro], fill=fill)
    d.ellipse([c[0] - ri, c[1] - ri, c[0] + ri, c[1] + ri], fill=0 if fill == 255 else 255)


def star(c, ro, ri, n, a0=-90):
    pts = []
    for k in range(2 * n):
        r = ro if k % 2 == 0 else ri
        t = math.radians(a0 + 180 * k / n)
        pts.append((c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
    return pts


def disc(d, c, r, fill=255):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill)


def quad(d, c, s):
    """a top-down quadcopter: body disc, X arms, four rotor discs (s = half span to a rotor centre)"""
    for sx in (-1, 1):
        for sy in (-1, 1):
            bar(d, c, (c[0] + sx * s, c[1] + sy * s), 40)
            disc(d, (c[0] + sx * s, c[1] + sy * s), 38)
    disc(d, c, 40)


def _new(name):
    m, d = layer()
    if name == 'BARRIER':
        d.rectangle([36, 120, 476, 246], fill=255)                                  # top plank
        for x in (70, 190, 310, 430):                                               # warning stripes (cut-outs)
            d.polygon([(x, 206), (x + 24, 160), (x + 60, 160), (x + 36, 206)], fill=0)
        d.polygon([(96, 236), (160, 236), (130, 468), (60, 468)], fill=255)          # legs
        d.polygon([(352, 236), (416, 236), (452, 468), (382, 468)], fill=255)
        d.rectangle([90, 318, 422, 362], fill=255)                                  # lower rail
    elif name == 'BLADE':
        l2, d2 = layer()
        d2.ellipse([22, 230, 74, 282], fill=255)                                    # pommel
        d2.rectangle([48, 232, 156, 280], fill=255)                                 # grip
        d2.rounded_rectangle([150, 184, 192, 328], radius=10, fill=255)             # guard
        d2.polygon([(192, 222), (420, 222), (500, 252), (430, 292), (192, 292)], fill=255)   # blade, pointed
        for x in (78, 118):                                                         # grip wraps (cut-outs)
            d2.rectangle([x, 232, x + 14, 280], fill=0)
        m = l2.rotate(40, resample=Image.BICUBIC, center=(256, 256))
    elif name == 'BOUNTYG':
        d.polygon([(24, 214), (122, 196), (122, 276), (34, 296)], fill=255)          # stock
        d.rectangle([118, 186, 300, 262], fill=255)                                 # receiver
        d.polygon([(296, 198), (470, 198), (490, 222), (470, 244), (296, 244)], fill=255)   # barrel
        d.polygon([(150, 258), (198, 258), (186, 344), (138, 338)], fill=255)        # grip
        d.polygon([(228, 258), (276, 258), (262, 330), (216, 326)], fill=255)        # magazine
        d.rectangle([150, 206, 270, 230], fill=0)                                   # cut-out
        disc(d, (382, 372), 120, fill=0)                                            # clear room for the coin
        disc(d, (382, 372), 96)                                                     # coin
        ring(d, (382, 372), 64, 40, fill=0)
        d.rectangle([370, 330, 394, 414], fill=0)                                   # the coin's slot mark
    elif name == 'BULWARK':
        d.polygon([(150, 36), (362, 36), (408, 82), (408, 430), (362, 476), (150, 476), (104, 430), (104, 82)], fill=255)
        d.rounded_rectangle([160, 104, 352, 150], radius=12, fill=0)                # view slot
        for y in (236, 316, 396):                                                   # rivets down the plate
            d.rectangle([150, y, 178, y + 28], fill=0); d.rectangle([334, y, 362, y + 28], fill=0)
    elif name == 'CHARGE':
        d.polygon(star((256, 128), 118, 54, 8, -90), fill=255)                      # the blast
        d.rectangle([96, 272, 416, 470], fill=255)                                  # the block
        d.polygon([(166, 300), (346, 300), (256, 430)], fill=0)                     # the cone cut (shaped charge)
    elif name == 'COIL':
        d.polygon([(140, 476), (372, 476), (334, 424), (178, 424)], fill=255)        # base
        d.rectangle([228, 190, 284, 430], fill=255)                                 # column
        for y, w in ((236, 84), (300, 100), (364, 116)):                            # coil windings
            d.rounded_rectangle([256 - w, y, 256 + w, y + 34], radius=12, fill=255)
        d.ellipse([150, 120, 362, 204], fill=255)                                   # top torus
        d.ellipse([214, 146, 298, 178], fill=0)
        d.polygon([(330, 128), (420, 20), (412, 82), (496, 50), (404, 160), (410, 104)], fill=255)  # spark
    elif name == 'CROSS':
        l2, d2 = layer()
        d2.polygon([(150, 222), (470, 236), (494, 256), (470, 276), (150, 300)], fill=255)  # barrel, pointed muzzle
        d2.ellipse([110, 210, 194, 312], fill=255)                                  # breech
        m = l2.rotate(28, resample=Image.BICUBIC, center=(180, 300))
        m = m.transform(m.size, Image.AFFINE, (1, 0, 10, 0, 1, -40))
        d = ImageDraw.Draw(m)
        disc(d, (200, 360), 120, fill=0)
        ring(d, (200, 360), 98, 56)                                                 # wheel
        disc(d, (200, 360), 28)
        for a in (0, 60, 120):
            t = math.radians(a)
            bar(d, (200 - 80 * math.cos(t), 360 - 80 * math.sin(t)), (200 + 80 * math.cos(t), 360 + 80 * math.sin(t)), 26)
        d.rectangle([370, 316, 412, 476], fill=255)                                 # the crossing mark (+)
        d.rectangle([312, 374, 470, 416], fill=255)
    elif name == 'DRONES':
        quad(d, (136, 140), 62)
        quad(d, (376, 140), 62)
        quad(d, (256, 372), 62)
    elif name == 'FLAK':
        d.polygon([(76, 476), (336, 476), (300, 404), (112, 404)], fill=255)         # base
        disc(d, (206, 360), 76)                                                     # mount
        for o in (-34, 34):                                                         # twin barrels
            a = (206 + o * 0.7071, 360 + o * 0.7071); b = (a[0] + 190, a[1] - 190)
            bar(d, a, b, 38)
        d.polygon(star((416, 98), 90, 40, 8, -90), fill=255)                        # the air burst
    elif name == 'FLAMER':
        d.rectangle([40, 212, 250, 282], fill=255)                                  # body
        d.polygon([(80, 278), (132, 278), (120, 372), (70, 366)], fill=255)          # grip
        d.rounded_rectangle([146, 286, 246, 344], radius=18, fill=255)              # fuel cell
        d.rectangle([246, 228, 296, 266], fill=255)                                 # nozzle
        d.rectangle([96, 230, 226, 254], fill=0)                                    # cut-out
        d.polygon([(296, 247), (330, 196), (360, 214), (402, 132), (428, 196), (500, 162), (470, 240), (506, 290),
                   (448, 296), (470, 368), (398, 318), (356, 352), (330, 300)], fill=255)   # flame jet, pointed tongues
        d.polygon([(352, 248), (400, 214), (440, 246), (402, 280)], fill=0)          # flame core cut-out
    elif name == 'GL':
        d.polygon([(22, 236), (118, 214), (118, 290), (32, 310)], fill=255)          # stock
        d.rectangle([114, 204, 250, 276], fill=255)                                 # body
        d.polygon([(132, 272), (180, 272), (168, 362), (120, 356)], fill=255)        # grip
        d.rectangle([290, 196, 466, 274], fill=255)                                 # fat barrel
        d.rectangle([448, 182, 490, 288], fill=255)                                 # muzzle ring
        disc(d, (262, 300), 106, fill=0)
        disc(d, (262, 300), 92)                                                     # revolver drum
        for a in (-90, 30, 150):
            t = math.radians(a)
            disc(d, (262 + 50 * math.cos(t), 300 + 50 * math.sin(t)), 22, fill=0)   # chambers
    elif name == 'LANCE':
        d.rectangle([20, 234, 104, 278], fill=255)                                  # grip
        d.polygon([(104, 170), (164, 226), (164, 286), (104, 342)], fill=255)        # vamplate
        d.polygon([(164, 222), (500, 256), (164, 290)], fill=255)                    # the lance, pointed
        d.polygon([(306, 56), (366, 56), (366, 196), (346, 214), (326, 190), (306, 206)], fill=255)   # split plate, top
        d.polygon([(306, 306), (326, 322), (346, 298), (366, 316), (366, 456), (306, 456)], fill=255)   # bottom
    elif name == 'LANEG':
        for y in (110, 362):                                                        # the lane's edges, dashed
            for x0, x1 in ((24, 156), (196, 316), (356, 488)):
                d.rectangle([x0, y, x1, y + 40], fill=255)
        d.rectangle([24, 198, 120, 314], fill=255)                                  # the gun block
        for x in (154, 266, 378):                                                   # three shots down the lane
            d.polygon([(x, 228), (x + 70, 228), (x + 106, 256), (x + 70, 284), (x, 284)], fill=255)
    elif name == 'LONG':
        d.polygon([(16, 230), (118, 214), (140, 244), (118, 296), (26, 296)], fill=255)   # stock
        d.rectangle([116, 220, 300, 266], fill=255)                                 # body
        d.rectangle([296, 228, 498, 258], fill=255)                                 # long barrel
        d.rectangle([466, 220, 498, 266], fill=255)                                 # muzzle brake
        d.rounded_rectangle([140, 148, 306, 192], radius=16, fill=255)              # scope
        d.polygon([(124, 140), (150, 150), (150, 190), (124, 200)], fill=255)
        d.polygon([(296, 150), (330, 136), (330, 204), (296, 190)], fill=255)
        d.rectangle([180, 188, 208, 222], fill=255); d.rectangle([248, 188, 276, 222], fill=255)
        d.polygon([(146, 262), (192, 262), (182, 346), (136, 340)], fill=255)        # grip
        bar(d, (400, 256), (342, 420), 34); bar(d, (412, 256), (458, 420), 34)      # bipod
    elif name == 'MARKS':
        d.rounded_rectangle([132, 196, 380, 270], radius=20, fill=255)              # tube
        d.polygon([(36, 178), (140, 206), (140, 260), (36, 288)], fill=255)          # eyepiece bell
        d.polygon([(372, 202), (480, 150), (480, 316), (372, 264)], fill=255)        # objective bell
        d.rectangle([226, 140, 286, 200], fill=255)                                 # turret
        d.rectangle([212, 128, 300, 152], fill=255)
        d.rectangle([168, 266, 212, 330], fill=255); d.rectangle([300, 266, 344, 330], fill=255)   # rings
        d.rectangle([132, 326, 380, 366], fill=255)                                 # rail
        d.rectangle([420, 196, 448, 270], fill=0)                                   # lens cut
    elif name == 'MORTAR':
        d.polygon([(40, 470), (330, 470), (304, 428), (66, 428)], fill=255)          # baseplate
        bar(d, (160, 440), (318, 176), 88)                                          # tube
        bar(d, (305, 198), (340, 140), 112)                                         # muzzle
        bar(d, (262, 300), (360, 450), 34)                                          # bipod leg
        bar(d, (262, 300), (230, 440), 34)
        l2, d2 = layer()                                                            # the shell, nose up-right
        d2.polygon([(380, 68), (440, 68), (488, 100), (440, 132), (380, 132)], fill=255)
        d2.polygon([(352, 58), (384, 76), (384, 124), (352, 142)], fill=255)
        l2 = l2.rotate(30, resample=Image.BICUBIC, center=(420, 100))
        m = ImageChops.lighter(m, l2)
    elif name == 'NAIL':
        d.rectangle([28, 350, 484, 446], fill=255)                                  # the plank
        d.rectangle([66, 382, 196, 406], fill=0); d.rectangle([316, 382, 446, 406], fill=0)   # grain cut-outs
        l2, d2 = layer()
        d2.rounded_rectangle([156, 30, 356, 92], radius=14, fill=255)               # the nail's head
        d2.polygon([(222, 92), (290, 92), (282, 290), (256, 360), (230, 290)], fill=255)   # shaft, pointed
        l2 = l2.rotate(-18, resample=Image.BICUBIC, center=(256, 350))
        m = ImageChops.lighter(m, l2)
        d = ImageDraw.Draw(m)
        for a, b in (((120, 300), (60, 250)), ((392, 300), (452, 250))):            # impact ticks
            bar(d, a, b, 30)
    elif name == 'PISTOL':
        d.rectangle([60, 170, 290, 242], fill=255)                                  # slide
        d.rounded_rectangle([284, 180, 494, 232], radius=14, fill=255)              # suppressor
        d.rectangle([380, 194, 404, 218], fill=0)
        d.polygon([(70, 238), (156, 238), (136, 410), (40, 396)], fill=255)          # grip, raked
        d.rectangle([156, 238, 220, 262], fill=255)                                 # trigger guard
        d.rectangle([196, 238, 220, 300], fill=255); d.rectangle([150, 286, 220, 306], fill=255)
        d.rectangle([116, 192, 236, 216], fill=0)                                   # ejection port
    elif name == 'PULSE':
        ring(d, (118, 256), 100, 46)                                                # emitter disc
        disc(d, (118, 256), 24)
        d.polygon([(216, 230), (450, 230), (500, 256), (450, 282), (216, 282)], fill=255)   # the beam, pointed
        for r in (110, 190):                                                        # pulse arcs off the emitter
            d.arc([210 - r, 256 - r, 210 + r, 256 + r], -42, 42, fill=255, width=40)
    elif name == 'SLICK':
        d.ellipse([136, 108, 340, 336], fill=255)                                   # grenade body
        d.rectangle([196, 70, 280, 116], fill=255)                                  # cap
        d.polygon([(270, 74), (370, 104), (360, 250), (328, 250), (334, 126), (270, 108)], fill=255)   # lever
        d.rectangle([136, 210, 340, 234], fill=0)                                   # groove
        d.rectangle([226, 116, 250, 336], fill=0)
        ring(d, (156, 70), 44, 20)                                                  # pin ring
        d.ellipse([36, 392, 476, 478], fill=255)                                    # the slick
        d.ellipse([150, 412, 260, 440], fill=0)
    elif name == 'WIRE':
        d.rectangle([20, 236, 492, 276], fill=255)                                  # the strand
        for x in (96, 256, 416):                                                    # barbs, 4 points each
            d.polygon(star((x, 256), 96, 28, 4, -45), fill=255)
    elif name == 'BEACON':
        d.polygon([(130, 478), (382, 478), (352, 424), (160, 424)], fill=255)        # base
        d.pieslice([166, 214, 346, 394], 180, 360, fill=255)                        # dome
        d.rectangle([166, 300, 346, 426], fill=255)
        d.rectangle([166, 330, 346, 356], fill=0)                                   # band
        for a in (-162, -126, -90, -54, -18):                                       # rays, pointed outwards
            t = math.radians(a); c = (256, 300)
            p0 = (c[0] + 132 * math.cos(t), c[1] + 132 * math.sin(t))
            p1 = (c[0] + 256 * math.cos(t), c[1] + 256 * math.sin(t))
            n = (-math.sin(t) * 24, math.cos(t) * 24)
            d.polygon([(p0[0] + n[0], p0[1] + n[1]), (p1[0], p1[1]), (p0[0] - n[0], p0[1] - n[1])], fill=255)
    elif name == 'DECOY':
        disc(d, (256, 104), 68)                                                     # head
        d.rounded_rectangle([132, 186, 380, 400], radius=70, fill=255)              # torso
        ring(d, (256, 290), 70, 44, fill=0)                                         # bullseye (cut-out ring)
        d.rectangle([234, 396, 278, 480], fill=255)                                 # stake
        d.rectangle([160, 452, 352, 488], fill=255)
    elif name == 'DRONE':
        d.rounded_rectangle([40, 96, 236, 140], radius=20, fill=255)                # rotors
        d.rounded_rectangle([276, 96, 472, 140], radius=20, fill=255)
        d.rectangle([118, 132, 158, 190], fill=255); d.rectangle([354, 132, 394, 190], fill=255)   # arms
        d.rounded_rectangle([106, 172, 406, 260], radius=34, fill=255)              # body
        d.rectangle([200, 202, 312, 228], fill=0)                                   # body cut-out
        d.rectangle([234, 256, 278, 400], fill=255)                                 # wrench handle
        disc(d, (256, 420), 66)                                                     # wrench head
        d.rectangle([232, 400, 280, 500], fill=0)                                   # open jaw
    elif name == 'GATE':
        d.polygon([(178, 484), (258, 484), (258, 278), (370, 278), (370, 334), (494, 238), (370, 142), (370, 198),
                   (178, 198)], fill=255)                                           # the turn arrow
        d.rectangle([110, 36, 326, 132], fill=255)                                  # the bar across straight ahead
        d.polygon([(166, 62), (206, 62), (186, 106), (146, 106)], fill=0)
        d.polygon([(250, 62), (290, 62), (270, 106), (230, 106)], fill=0)
    elif name == 'LURE':
        ring(d, (316, 74), 50, 22)                                                  # eye
        d.rectangle([292, 118, 340, 330], fill=255)                                 # shank
        d.pieslice([132, 222, 340, 430], 0, 180, fill=255)                          # bend
        d.pieslice([180, 270, 292, 382], 0, 180, fill=0)
        d.rectangle([180, 270, 292, 326], fill=0)
        d.polygon([(132, 326), (180, 326), (180, 236), (204, 270), (174, 170), (110, 262), (132, 252)], fill=255)   # point + barb
    elif name == 'MAST':
        bar(d, (256, 150), (140, 484), 44); bar(d, (256, 150), (372, 484), 44)      # legs
        d.rectangle([190, 286, 322, 322], fill=255)                                 # braces
        d.rectangle([160, 396, 352, 432], fill=255)
        disc(d, (256, 118), 44)                                                     # emitter
        for r in (108, 176):                                                        # waves, both ways
            d.arc([256 - r, 118 - r, 256 + r, 118 + r], 196, 244, fill=255, width=38)
            d.arc([256 - r, 118 - r, 256 + r, 118 + r], 296, 344, fill=255, width=38)
    elif name == 'SHOCK':
        d.rectangle([40, 70, 104, 484], fill=255); d.rectangle([408, 70, 472, 484], fill=255)   # posts
        d.rectangle([104, 120, 408, 156], fill=255); d.rectangle([104, 408, 408, 444], fill=255)   # wires
        d.polygon([(300, 180), (174, 314), (250, 314), (204, 388), (344, 252), (266, 252), (322, 180)], fill=255)   # bolt
    elif name == 'TAR':
        d.rounded_rectangle([40, 60, 472, 220], radius=70, fill=255)                # the smear
        for x, y1 in ((108, 330), (228, 430), (356, 370)):                          # drips
            d.rectangle([x, 200, x + 54, y1], fill=255)
            disc(d, (x + 27, y1), 46)
        d.ellipse([110, 104, 230, 140], fill=0)                                     # sheen cut-out
    return m


# ---------------------------------------------------------------- glyph files
def save_new(glyph_dir):
    for n in NEW:
        m = _new(n).resize((256, 256), Image.LANCZOS)
        im = Image.new('RGBA', (256, 256), (255, 255, 255, 0)); im.putalpha(m)
        im.save(os.path.join(glyph_dir, fname(n) + '.png'))


def alpha_of(path):
    return np.asarray(Image.open(path).convert('RGBA').split()[3]).astype(np.float32) / 255.0


# ---------------------------------------------------------------- RaidGlyphs.draw, emulated
# Godot draws the 256 px texture into the box with linear filtering and no mipmaps (the .import defaults): each screen
# pixel samples the texture bilinearly at its centre. The outline is the texture drawn 12 times round the centre at
# max(1, box * outline_share) px in the ink, then the fill on top.
OUTLINE_SHARE = 0.075
INK = (12, 10, 22)


def sample(a, x0, y0, box, w, h):
    """coverage (h x w) of texture alpha `a` drawn in the square [x0, x0+box) x [y0, y0+box) of a w x h canvas"""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    u = (xs - x0) / box; v = (ys - y0) / box
    inside = (u >= 0) & (u < 1) & (v >= 0) & (v < 1)
    n = a.shape[0]
    tx = np.clip(u * n - 0.5, 0, n - 1); ty = np.clip(v * n - 0.5, 0, n - 1)
    ix = np.floor(tx).astype(int); iy = np.floor(ty).astype(int)
    fx = tx - ix; fy = ty - iy
    ix1 = np.minimum(ix + 1, n - 1); iy1 = np.minimum(iy + 1, n - 1)
    c = (a[iy, ix] * (1 - fx) * (1 - fy) + a[iy, ix1] * fx * (1 - fy) + a[iy1, ix] * (1 - fx) * fy + a[iy1, ix1] * fx * fy)
    return np.where(inside, c, 0.0)


def draw_glyph(canvas, a, at, box, fill):
    """canvas: float32 HxWx3 (0..1), drawn over in place, like RaidGlyphs.draw"""
    h, w, _ = canvas.shape
    x0, y0 = at[0] - box / 2, at[1] - box / 2
    o = max(1.0, box * OUTLINE_SHARE)
    ink = np.array(INK, np.float32) / 255
    for k in range(12):
        t = 2 * math.pi * k / 12
        c = sample(a, x0 + math.cos(t) * o, y0 + math.sin(t) * o, box, w, h)[..., None]
        canvas[:] = canvas * (1 - c) + ink * c
    c = sample(a, x0, y0, box, w, h)[..., None]
    canvas[:] = canvas * (1 - c) + (np.array(fill, np.float32) / 255) * c


def tile(a, size, bg, fill, share=0.84, icon_h=None):
    """a roster tile (BHqLook.icon in a TILE): bg, the glyph box = min(icon w, icon h) * 0.84, centred in the icon area"""
    w, h = size
    ih = icon_h if icon_h is not None else h
    cv = np.zeros((h, w, 3), np.float32) + np.array(bg, np.float32) / 255
    draw_glyph(cv, a, (w / 2, ih / 2 + 1), min(w, ih) * share, fill)
    return Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8), 'RGB')


# ---------------------------------------------------------------- twin check (raid_icons.py's 16 px rule)
def soft16(a):
    g = Image.fromarray((a * 255).astype(np.uint8), 'L')
    bb = g.getbbox(); g = g.crop(bb); k = 15 / max(g.size)
    g = g.resize((max(1, int(round(g.width * k))), max(1, int(round(g.height * k)))), Image.LANCZOS)
    c = Image.new('L', (16, 16), 0); c.paste(g, ((16 - g.width) // 2, (16 - g.height) // 2))
    return np.asarray(c.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255


def twin_check(alphas, locked_dir):
    """max soft IoU at 16 px of every weapon / device glyph against the other 35 and the locked set"""
    atlas = {}
    for fn in sorted(os.listdir(locked_dir)):
        if fn.endswith('.png'):
            atlas['locked:' + fn[:-4]] = soft16(alpha_of(os.path.join(locked_dir, fn)))
    mine = {k: soft16(a) for k, a in alphas.items()}
    res = {}
    for k, a in mine.items():
        best = (0.0, '')
        own = EXISTING.get(k, '')
        for o, b in list(mine.items()) + list(atlas.items()):
            if o == k or (own and o == 'locked:' + own):
                continue
            iou = float(np.minimum(a, b).sum() / max(np.maximum(a, b).sum(), 1e-6))
            if iou > best[0]:
                best = (iou, o)
        res[k] = best
    return res


# ---------------------------------------------------------------- the review sheet
BG = (22, 20, 30); CELL = (34, 32, 44); PAPER = (240, 234, 220); INKF = (12, 10, 22); GLASS = (8, 12, 23)
TEAL = (90, 214, 200); PINK = (255, 110, 196); TXT = (236, 236, 240); DIM = (160, 160, 176); RED = (255, 90, 90)
TILE = (46, 38)


def sheet(glyph_dir, locked_dir, out, fonts):
    ids = WEAPONS + DEVICES
    alphas = {}
    for k in ids:
        g = EXISTING.get(k, fname(k))
        alphas[k] = alpha_of(os.path.join(glyph_dir, g + '.png'))
    tw = twin_check(alphas, locked_dir)
    fa = ImageFont.truetype(os.path.join(fonts, 'Anton-Regular.ttf'), 26)
    fh = ImageFont.truetype(os.path.join(fonts, 'Anton-Regular.ttf'), 40)
    fm = ImageFont.truetype(os.path.join(fonts, 'ShareTechMono-Regular.ttf'), 15)
    fs = ImageFont.truetype(os.path.join(fonts, 'ShareTechMono-Regular.ttf'), 17)
    cols, cw, ch = 5, 404, 236
    wrows = (len(WEAPONS) + cols - 1) // cols; drows = (len(DEVICES) + cols - 1) // cols
    H = 150 + wrows * ch + 70 + drows * ch + 30
    W = cols * cw + 28
    sh = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(sh)
    d.text((16, 12), 'Raid weapon + device pictograms: existing (teal) and new (pink), 25 weapons + 11 devices', font=fh, fill=TXT)
    d.text((16, 66), 'each: the roster tile 1:1 (46 x 38, ink on paper, glyph box 19.8 px) | x4 nearest of that tile | raid gear tag 1:1 '
                     '(22 px, white on glass) | 96 px.  Drawn like RaidGlyphs.draw: 256 px texture, linear filter, no mipmaps, 12-step ink outline.',
           font=fm, fill=DIM)
    d.text((16, 88), 'Note: the paper tile draws fill INK over the ink outline (BHqLook.icon on port-b/sc1b), so cut-outs close at 1:1; the glass column is the glyph grammar.  IoU = max soft IoU at 16 px vs the other 35 and the LOCKED set (16 px rule: < 0.68 passes).',
           font=fm, fill=DIM)

    def cell(k, x, y):
        new = k in NEW
        d.rounded_rectangle([x, y, x + cw - 14, y + ch - 12], radius=10, fill=CELL, outline=PINK if new else TEAL, width=2)
        a = alphas[k]
        t1 = tile(a, TILE, PAPER, INKF, icon_h=TILE[1] * 0.62)
        sh.paste(t1, (x + 14, y + 52))
        t4 = t1.resize((TILE[0] * 4, TILE[1] * 4), Image.NEAREST)
        sh.paste(t4, (x + 74, y + 52))
        g22 = tile(a, (30, 30), GLASS, (255, 255, 255), share=22 / 30)
        sh.paste(g22, (x + 14, y + 104))
        g96 = tile(a, (112, 112), GLASS, (255, 255, 255), share=96 / 112)
        sh.paste(g96, (x + 268, y + 52))
        nm = NEW[k][1] if new else NAMES[k]
        d.text((x + 12, y + 8), k, font=fa, fill=TXT)
        d.text((x + 14 + fa.getlength(k) + 10, y + 18), nm, font=fs, fill=DIM)
        iou, who = tw[k]
        d.text((x + 12, y + 206), ('new ' + fname(k)) if new else ('existing ' + EXISTING[k]), font=fm,
               fill=PINK if new else TEAL)
        d.text((x + 268, y + 172), 'IoU %.2f' % iou, font=fm, fill=RED if iou >= 0.68 else DIM)
        d.text((x + 268, y + 188), who.replace('locked:', 'L:')[:16], font=fm, fill=DIM)

    y0 = 120
    d.text((16, y0), 'WEAPONS (25)', font=fa, fill=TXT)
    for i, k in enumerate(WEAPONS):
        cell(k, 14 + (i % cols) * cw, y0 + 36 + (i // cols) * ch)
    y1 = y0 + 36 + wrows * ch + 10
    d.text((16, y1), 'DEVICES (11)', font=fa, fill=TXT)
    for i, k in enumerate(DEVICES):
        cell(k, 14 + (i % cols) * cw, y1 + 36 + (i // cols) * ch)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sh.save(out)
    return tw


if __name__ == '__main__':
    glyph_dir, locked_dir, out, fonts = sys.argv[1:5]
    save_new(glyph_dir)
    tw = sheet(glyph_dir, locked_dir, out, fonts)
    for k in WEAPONS + DEVICES:
        print('%-10s IoU %.2f %s' % (k, tw[k][0], tw[k][1]))
