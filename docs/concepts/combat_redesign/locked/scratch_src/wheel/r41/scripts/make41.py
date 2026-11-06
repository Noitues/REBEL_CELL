"""Round 41 build: python make41.py multi | popup | pdrones | combined"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
import sat2 as S2
import sat3 as S3
import stack41 as K
import specs14 as S
import roster as RS
import preview16 as PV
from preview15 import dashed_poly
from frames import INK, CREAM
from slicelib import f_num, f_ui, f_mono, R_OUT, R_IN, PROGRAMS
from make_sat2 import city, tag, fit_into, trim, at_r, save_gif, botnet, care_swarm

BG = (16, 15, 22)
YEL = (255, 214, 64)
WHITE = (255, 255, 255)
PAR = (214, 60, 255)
SIZE = (2000, 2000)


def header(Sh, title, sub, col=YEL):
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=col)
    d.text((26, 6), title, font=f_num(44), fill=WHITE)
    d.text((26, 56), sub, font=f_mono(14, False), fill=(185, 185, 200))
    return d


def comp(spec, rot=0.0, hp=True, lod=False, size=SIZE):
    if lod:
        s = dict(spec)
        s["drones"] = []
        import d4corp as D
        h = D.render(s, ss=1, rot=rot, lod=True)
    else:
        h = S2.host_image(spec, rot, hp_number=hp)
    return S2.Comp(h, size), h


def breaker():
    return S.player()


# ================================================================== 1 multi drone
def multi():
    W, H = 1920, 1180
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = header(Sh, "TWO DRONES ON ONE SLICE  (hangar segment)", "Both share ONE blended dock: one rim band over the slice, a neck + collar per drone; the pair sits at +-14 deg "
                   "so the collars clear each other and a needle passes between them.")
    pb, eb = botnet(), care_swarm()
    jobs = [("PLAYER  BOTNET: 2 drones on TROJAN (slice 2), 1 on slice 4", pb, [(1, 2), (3, 1)], S2.BOTNET_DRONE),
            ("ENEMY  CARE SWARM: 2 on slice 3, 1 on slice 5", eb, [(2, 2), (4, 1)], S2.CARE_DRONE)]
    for k, (title, spec, docks, sat) in enumerate(jobs):
        x0 = 10 + k * 645
        Sh.alpha_composite(city(635, 760, 20 + k), (x0, 84))
        c, h = comp(spec)
        for slot, n in docks:
            K.put_drones(c, sat, 60 * slot, n, spec)
        fit_into(Sh, trim(at_r(c, 220)), (x0 + 4, 114, x0 + 631, 840))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    x0 = 1300
    Sh.alpha_composite(city(610, 760, 33), (x0, 84))
    d.text((x0 + 10, 90), "UNDER THE NEEDLE: the blade passes between the pair", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    c, h = comp(pb, rot=300.0)
    K.put_drones(c, S2.BOTNET_DRONE, 0, 2, pb, rot=300.0)
    crop = (int(c.C[0] - 520), int(c.C[1] - 960), int(c.C[0] + 520), int(c.C[1] - 60))
    fit_into(Sh, c.image(crop=crop), (x0 + 6, 116, x0 + 604, 560))
    d.text((x0 + 10, 580), "r = 60", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    c, h = comp(pb, lod=True)
    K.put_drones(c, S2.BOTNET_DRONE, 60, 2, pb, lod=True)
    fit_into(Sh, trim(at_r(c, 60)), (x0 + 20, 600, x0 + 300, 840))
    c, h = comp(eb, lod=True)
    K.put_drones(c, S2.CARE_DRONE, 120, 2, eb, lod=True)
    fit_into(Sh, trim(at_r(c, 60)), (x0 + 310, 600, x0 + 600, 840))
    notes = ["- hangar allows TWO drones per slice; the dock grows a second neck + collar",
             "- pair at slice centre +-14 deg; a single drone stays centred",
             "- each drone keeps its own pointer, HP and intent; both resolve after the host slice",
             "- REPLACE on a full hangar: the drone being replaced is the one the card targets",
             "  (default: the older one) and it returns to the core as green bits (round 40)",
             "- OPEN (from round 40, still open): damage with two drones on one slice"]
    for j, ln in enumerate(notes):
        d.text((24, 870 + j * 24), ln, font=f_mono(16, False), fill=(215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "multi_drone.png"))
    print("multi", flush=True)


# ================================================================== 2 parasite pop-up gif
def popup():
    P = breaker()
    slot = 2                     # VIRUS 3
    N = 35                       # a long spin: the parasite crosses the needle mid-spin and keeps going
    rot_end = 240.0              # slot 2 ends under the needle
    rot0 = rot_end - 12 * N
    fr, du = [], []

    def frame(rot, state, cap, dur, lit=None, beam=0.0, tagtxt=None):
        c, h = comp(P, rot)
        top = h[2]["top_r"]
        r_in, r_out = K.parasite(c, slot, rot, top, state, lit=lit)
        if beam:
            S3.link(c, "A", r_in, r_out, top, k=beam)
        im = c.image(crop=(int(c.C[0] - 820), int(c.C[1] - 860), int(c.C[0] + 820), int(c.C[1] + 640)), scale=0.42)
        base = city(im.width, im.height, 8)
        base.alpha_composite(im)
        dd = ImageDraw.Draw(base)
        dd.rectangle([0, 0, base.width, 50], fill=(10, 9, 16, 240))
        dd.text((14, 8), cap, font=f_num(28), fill=WHITE)
        if tagtxt:
            tag(dd, (base.width // 2, 82), tagtxt[0], tagtxt[1], (255, 150, 160), size=24)
        fr.append(base.convert("RGB"))
        du.append(dur)
        print("f", cap[:24], round(rot, 1), flush=True)
    frame(rot0, 0.0, "1  the PARASITE stays ATTACHED: the needle is elsewhere", 1500)
    steps = 14
    for s in range(1, steps + 1):
        q = s / steps
        q = 1 - (1 - q) ** 2.2
        rot = rot0 + 12 * N * q
        a_par = (120 + rot) % 360
        crossing = min(a_par, 360 - a_par) < 30
        frame(rot, 0.0, "2  SPINNING: it stays attached" + ("  (crossing the needle)" if crossing else ""), 80 if s < steps else 500)
    for k, st in enumerate((0.25, 0.5, 0.75, 1.0)):
        frame(rot_end, st, "3  SETTLED with the needle on it: it POPS UP", 90 if st < 1 else 700)
    for b in (0.5, 1.0):
        frame(rot_end, 1.0, "4  the sub-slice in line fires", 120, lit=1, beam=b)
    frame(rot_end, 1.0, "4  the sub-slice in line fires", 2200, lit=1, beam=1.0,
          tagtxt=("YOU: VIRUS 3   |   PARASITE: PATCH 6 -> BOSS +6 HP", "popped beyond the needle tip (option A)"))
    for st in (0.66, 0.33):
        frame(rot_end, st, "5  next spin: it drops back to ATTACHED", 90)
    frame(rot_end, 0.0, "5  next spin: it drops back to ATTACHED", 900)
    save_gif(fr, du, "parasite_popup.gif")


# ================================================================== 3 parasite + drones
def pdrones():
    W, H = 1920, 1240
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = header(Sh, "PARASITE + DRONES ON ONE SLICE", "Radial order on a slice: host frame -> parasite ring -> drones. The drones' dock necks pass under the parasite; "
                   "when the parasite pops up (needle on the slice), the drones are pushed out beyond it.", PAR)
    P = breaker()
    cases = [("1 drone, parasite ATTACHED", 0.0, 1, 60.0, 0.0), ("2 drones, parasite ATTACHED", 0.0, 2, 60.0, 0.0),
             ("1 drone, parasite POPPED (needle on it)", 1.0, 1, 0.0, 300.0), ("2 drones, parasite POPPED", 1.0, 2, 0.0, 300.0)]
    tw = 470
    for k, (title, st, n, a_slice, rot) in enumerate(cases):
        x0 = 10 + k * (tw + 6)
        Sh.alpha_composite(city(tw, 640, 40 + k), (x0, 84))
        c, h = comp(P, rot)
        top = h[2]["top_r"]
        K.parasite(c, 1, rot, top, st, lit=1 if st >= 1 else None)
        K.put_drones(c, S2.BOTNET_DRONE, 60 + rot, n, P, rot=rot, r_dock=K.drone_r(c, st, top))
        a = 60 + rot
        sx, sy = c.PP(c.RA + 260, a)
        crop = (int(sx - 560), int(sy - 640), int(sx + 560), int(sy + 520))
        fit_into(Sh, c.image(crop=crop), (x0 + 4, 116, x0 + tw - 4, 720))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    y0 = 740
    Sh.alpha_composite(city(940, 480, 9), (10, y0))
    d.text((20, y0 + 6), "WHOLE WHEEL  r = 220  (parasite + 2 drones on EXPLOIT 6, needle elsewhere)", font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    c, h = comp(P)
    top = h[2]["top_r"]
    K.parasite(c, 1, 0.0, top, 0.0)
    K.put_drones(c, S2.BOTNET_DRONE, 60, 2, P, r_dock=K.drone_r(c, 0.0, top))
    fit_into(Sh, trim(at_r(c, 150)), (14, y0 + 30, 946, y0 + 476))
    Sh.alpha_composite(city(300, 480, 10), (960, y0))
    d.text((970, y0 + 6), "r = 60", font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    c, h = comp(P, lod=True)
    K.parasite(c, 1, 0.0, top, 0.0, lod=True)
    K.put_drones(c, S2.BOTNET_DRONE, 60, 2, P, r_dock=K.drone_r(c, 0.0, top), lod=True)
    fit_into(Sh, trim(at_r(c, 60)), (970, y0 + 30, 1250, y0 + 470))
    rules = ["RULES (proposal)",
             "- radial order: frame > parasite > drones",
             "- drones dock beyond the parasite (+26),",
             "  necks pass under it",
             "- parasite pops -> its drones move out",
             "  with it (tweened together)",
             "- bodyguard is unchanged: a pointer attack",
             "  on this slice hits a drone first",
             "- the parasite is NOT a satellite: it is",
             "  never hit and never guards"]
    for j, ln in enumerate(rules):
        d.text((1280, y0 + 10 + j * 26), ln, font=f_mono(16, False), fill=YEL if j == 0 else (215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "parasite_drones.png"))
    print("pdrones", flush=True)


# ================================================================== 4 combined worst case
def worst(lod=False, size=SIZE, hp=True):
    """Breaker, slot 0 under the needle carries every layer; a card preview ghost lands on slot 1."""
    P = copy.deepcopy(breaker())
    P["slot_tier"] = {0: 3}
    P["variant"] = "worst"
    c, h = comp(P, 0.0, hp=hp, lod=lod, size=size)
    top = h[2]["top_r"]
    # inside the slice: ring texture extension, firmware socket, sub-needle, state overlay; read block re-stamped on top
    K.ring_extension(c, 0, 0.0)
    K.firmware_socket(c, 0, 0.0)
    K.sub_needle(c, 0, 0.0)
    K.state_overlay(c, 0, 0.0, stacks=2)
    K.read_block(c, P, 0, 0.0)
    # outside: parasite popped beyond the tip, two drones beyond it
    K.parasite(c, 0, 0.0, top, 1.0, lit=1, lod=lod)
    K.put_drones(c, S2.BOTNET_DRONE, 0.0, 2, P, r_dock=K.drone_r(c, 1.0, top), lod=lod)
    # card preview ghost blade landing on slot 1 (NUDGE +4 ticks), with its dashed parasite-would-pop hint
    lay, ld = F.layer(1)
    gl, gd = F.layer(1)
    a_l = 48.0
    L = dict(prog="FIREWALL", value=5, special=None)
    pc = PROGRAMS["FIREWALL"]["col"]
    ld = PV.ghost_blade(lay, ld, gd, 1, a_l, c.RA, top, 1.0, L, pc, 1, 1)
    ox, oy = int(c.C[0] - F.CX), int(c.C[1] - F.CY)
    c.top.alpha_composite(gl.filter(ImageFilter.GaussianBlur(7)), (ox, oy))
    c.top.alpha_composite(lay, (ox, oy))
    d = ImageDraw.Draw(c.top)
    wp = [c.PP(R_OUT - 4, 31 + 58 * j / 40) for j in range(41)] + [c.PP(R_IN + 4, 89 - 58 * j / 40) for j in range(41)]
    dashed_poly(d, wp, pc + (255,), 5, dash=12, gap=8)
    return c, h


def zone_diagram(Sh, box):
    """Radial zoning of one slice, drawn to scale (master units)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(Sh)
    cx, cy = (x0 + x1) / 2, y1 - 20
    s = (y1 - y0 - 50) / 800.0
    zones = [(0, 127, (60, 60, 75), "hub + inner ring"), (122, 152, CREAM, "sub-needle (tip stops at the slice lip)"),
             (132, 182, (255, 205, 90), "ring texture extension"), (142, 194, (200, 200, 215), "firmware socket (r 168)"),
             (130, 360, (120, 60, 90), "slice screen + tier inset + state overlay"), (230, 306, WHITE, "READ BLOCK (always on top)"),
             (300, 350, (255, 176, 60), "state badge + xN tab (outer-CW corner)"), (360, 414, (110, 100, 130), "frame + telemetry"),
             (336, 510, CREAM, "needle blade / card-preview ghost blade"), (420, 462, PAR, "parasite ATTACHED"),
             (526, 616, PAR, "parasite POPPED (needle on it)"), (642, 884, (123, 224, 123), "drones (beyond any ring)")]
    for j, (r0, r1, col, lab) in enumerate(zones):
        a0, a1 = -120 - 30, -60 + 30
        a0, a1 = 270 - 30, 270 + 30
        bb0 = [cx - r1 * s, cy - r1 * s, cx + r1 * s, cy + r1 * s]
        d.pieslice(bb0, 240, 300, fill=col + (90,), outline=col + (255,), width=2)
        if r0 > 0:
            bb1 = [cx - r0 * s, cy - r0 * s, cx + r0 * s, cy + r0 * s]
            d.pieslice(bb1, 240, 300, fill=(16, 15, 22, 0))
    # labels at the right with leader lines
    for j, (r0, r1, col, lab) in enumerate(sorted(zones, key=lambda z: -z[1])):
        ry = cy - (r0 + r1) / 2 * s
        tx = cx + 0.62 * 884 * s
        ty = y0 + 10 + j * ((y1 - y0 - 40) / len(zones))
        d.line([(cx + 8, ry), (tx - 6, ty + 9)], fill=col + (200,), width=1)
        d.text((tx, ty), "%3d-%3d  %s" % (r0, r1, lab), font=f_mono(13, False), fill=col)


def draw_wedges(Sh, box):
    """Draw the zones as nested wedges properly (outer first so inner zones stay visible)."""
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", Sh.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = x0 + 200, y1 - 10
    s = (y1 - y0 - 30) / 884.0
    zones = [(642, 884, (123, 224, 123), "DRONES  beyond any ring on the slice"),
             (526, 616, PAR, "PARASITE  popped (needle on it)"),
             (336, 510, CREAM, "NEEDLE blade + PREVIEW ghost blade"),
             (420, 462, PAR, "PARASITE  attached"),
             (360, 414, (130, 120, 150), "FRAME + telemetry"),
             (300, 352, (255, 176, 60), "STATE badge + xN tab (outer-CW)"),
             (130, 360, (150, 70, 110), "SCREEN + tier inset + state overlay"),
             (230, 306, WHITE, "READ BLOCK  (always on top)"),
             (142, 194, (200, 200, 215), "FIRMWARE socket (r 168)"),
             (132, 182, (255, 205, 90), "RING texture extension"),
             (122, 152, (250, 240, 214), "SUB-NEEDLE (tip stops at r 152)"),
             (0, 127, (70, 70, 90), "HUB + inner ring")]
    for (r0, r1, col, lab) in zones:
        pts = []
        for j in range(25):
            a = math.radians(-18 + 36 * j / 24)
            pts.append((cx + r1 * s * math.sin(a), cy - r1 * s * math.cos(a)))
        for j in range(25):
            a = math.radians(18 - 36 * j / 24)
            pts.append((cx + r0 * s * math.sin(a), cy - r0 * s * math.cos(a)))
        d.polygon(pts, fill=col + (110,), outline=col + (255,))
    Sh.alpha_composite(lay)
    d = ImageDraw.Draw(Sh)
    order = sorted(zones, key=lambda z: -(z[0] + z[1]))
    for j, (r0, r1, col, lab) in enumerate(order):
        ry = cy - (r0 + r1) / 2 * s
        tx, ty = x0 + 400, y0 + 4 + j * ((y1 - y0 - 20) / len(order))
        d.line([(cx + (r0 + r1) / 2 * s * 0.31, ry), (tx - 6, ty + 9)], fill=col + (180,), width=1)
        d.text((tx, ty), "r %3d-%3d  %s" % (r0, r1, lab), font=f_mono(13, False), fill=col)


Z_ORDER = ["1  slice screen (program / corp animation)", "2  ring texture extension (slice root)", "3  tier inset (V2)",
           "4  state overlay wash", "5  firmware socket", "6  sub-needle", "7  READ BLOCK (glyph + value)",
           "8  state badge + xN tab + rule tag", "9  frame + telemetry rail", "10 dock lobes (under the frame edge)",
           "11 parasite ring (attached / popped)", "12 drones (satellites)", "13 needle blades",
           "14 card-preview ghosts (top while hovering)"]


def combined():
    W, H = 1920, 1560
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = header(Sh, "WHEEL STACK  -  every layer on one slice at once", "Worst case on Breaker's top slice (needle on it): tier III, OVERCLOCKED x2, firmware, ring extension, sub-needle, "
                   "parasite popped, 2 drones; a card preview ghost lands on the next slice.")
    c, h = worst()
    Sh.alpha_composite(city(760, 1000, 3), (10, 84))
    d.text((20, 90), "WHOLE WHEEL  r = 220", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    fit_into(Sh, trim(at_r(c, 220)), (14, 116, 766, 1080))
    Sh.alpha_composite(city(560, 1000, 4), (780, 84))
    d.text((790, 90), "THE WORST-CASE SLICE (enlarged)", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    crop = (int(c.C[0] - 430), int(c.C[1] - 1000), int(c.C[0] + 430), int(c.C[1] - 90))
    fit_into(Sh, c.image(crop=crop), (784, 116, 1336, 1080))
    Sh.alpha_composite(city(560, 470, 5), (1350, 84))
    d.text((1360, 90), "r = 60", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    c60, h60 = worst(lod=True, hp=False)
    fit_into(Sh, trim(at_r(c60, 60)), (1360, 116, 1906, 548))
    d.text((1360, 566), "Z-ORDER (bottom -> top)", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    for j, ln in enumerate(Z_ORDER):
        d.text((1360, 594 + j * 24), ln, font=f_mono(15, False), fill=(215, 215, 225))
    y0 = 1100
    d.line([(20, y0 - 8), (1900, y0 - 8)], fill=(60, 60, 74))
    d.text((24, y0), "RADIAL ZONES OF ONE SLICE  (master units; player frame edge RA = 414)", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    draw_wedges(Sh, (20, y0 + 26, 900, H - 10))
    conflicts = ["CONFLICTS -> RULES",
                 "1 ghost blade vs popped parasite / drones: while a card is hovered,",
                 "  popped parasites on OTHER slices drop to attached; ghosts draw on top",
                 "2 sub-needle tip vs firmware socket: tip stops at the slice lip (r 152),",
                 "  the socket sits at r 168: a gap, never overlapping",
                 "3 state overlay vs read block: wash <= 45 %, block re-stamped on top",
                 "4 drones vs needle: pairs flank the blade at +-14 deg; a single drone",
                 "  on the needle slice sits centred beyond the blade top / parasite",
                 "5 popped parasite + drones need ~470 master units of headroom: the",
                 "  forecast tag moves aside (or the wheel scales) when both are on top",
                 "6 r = 60: only colour, glyphs and the parasite/drone silhouettes",
                 "  survive; values go to the forecast chip"]
    for j, ln in enumerate(conflicts):
        d.text((940, y0 + 6 + j * 22), ln, font=f_mono(15, False), fill=YEL if j == 0 else (215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "wheel_stack_combined.png"))
    print("combined", flush=True)


if __name__ == "__main__":
    {"multi": multi, "popup": popup, "pdrones": pdrones, "combined": combined}[sys.argv[1]]()
    print("done")
