"""Round 33 kit: Firmware ("microchips") and Daemons.

- FIRMWARE / DAEMONS: the real content (content/firmware/*.tres, content/daemons/*.tres): name, effect text,
  rarity, allowed slice types, trigger family.
- icon(name, px): the 42 new glyphs (18 chip effect glyphs + 24 daemon sigils), flat bold white silhouettes
  drawn on a 256 grid at 4x and downsampled. None reuses a round 17 slice glyph or card pictogram.
- chip(...): the socketed die (pins on top = the edge that plugs into the slice bezel, LED in rarity colour).
- daemon_tile(...): the small CRT tile a Daemon runs on (sigil in phosphor of its trigger family).
- socket_wheel(...): a locked round 17 wheel with chips socketed into the outer-left (counter-clockwise) corner.

All randomness is seeded.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "lib17"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

import r31lib as L

OUT = L.OUT
SCRATCH = L.SCRATCH
CACHE = os.path.join(SCRATCH, "r33")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ content (read from content/*.tres)
# slice type ids (RC.SliceType): 0 ATTACK, 1 CRIT, 2 DEFEND, 3 EVADE, 4 SHIELD, 5 DEPLOY, 6 HEAL, 7 AFFLICT, 8 MISS
TYPE_NAME = ["ATK", "CRIT", "DEF", "EVADE", "SHIELD", "DEPLOY", "HEAL", "AFFLICT", "MISS"]
TYPE_PROG = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "PROXY", "SANDBOX", "TROJAN", "PATCH", "VIRUS", "NULL"]
RAR_NAME = ["COMMON", "UNCOMMON", "RARE", "BOSS"]
RAR_COL = [(214, 222, 236), (92, 225, 255), (255, 214, 64), (255, 70, 86)]   # LED / bezel colour
RAR_PIPS = [1, 2, 3, 3]

# id, name, rarity, allowed types ([] = any), effect (description in the .tres), family colour of the trigger cue
FIRMWARE = [
    ("patch_plus", "Patch+", 0, [], "Slice output +50%."),
    ("hardened", "Hardened", 0, [], "Slice permanently ENCRYPTED."),
    ("burner", "Burner", 0, [], "Permanently OVERCLOCKED (1.5x); each trigger adds 1 Heat."),
    ("leech", "Leech", 0, [0], "ATK slice restores 1 RAM on Good or better."),
    ("mirror", "Mirror", 0, [], "Copies the neighbour on the side you landed; both on Perfect."),
    ("shunt", "Shunt", 0, [], "Resolves the neighbour on the side you landed toward at 1.5x."),
    ("overvolt", "Overvolt", 0, [0, 1], "ATK and CRIT slices: output +25%."),
    ("bulkhead", "Bulkhead", 0, [2, 4], "DEF and SHIELD slices: output +50%."),
    ("siphon", "Siphon", 0, [0], "ATK slice heals you 2 on Good or better."),
    ("static_coat", "Static Coat", 0, [2], "DEF slice also grants 2 shield."),
    ("barbed_wire", "Barbed Wire", 0, [2], "DEF slice also deals 2 damage to the pointer target."),
    ("recycler", "Recycler", 0, [8], "The Miss slice restores 2 RAM when it resolves."),
    ("counterstrike", "Counterstrike", 1, [3], "EVADE slice also deals 4 damage to the pointer target."),
    ("nanite_mesh", "Nanite Mesh", 1, [6], "HEAL slice: output +50%, and it cleanses itself."),
    ("power_cell", "Power Cell", 1, [4], "SHIELD slice also restores 1 RAM."),
    ("tracer", "Tracer", 1, [0, 1], "ATK or CRIT slice strips 1 resistance on a Perfect."),
    ("skimmer", "Skimmer", 1, [0], "ATK slice: +3 Cycles on a Perfect (twice per combat)."),
    ("coolant_loop", "Coolant Loop", 2, [], "Once per combat, a Perfect here lowers Heat by 1."),
]
FW = {f[0]: f for f in FIRMWARE}

# trigger families -> phosphor colour of the daemon sigil
FAM = {
    "PERFECT": (255, 214, 64),
    "MISS": (236, 48, 58),
    "TURN": (92, 225, 255),
    "ACTION": (186, 146, 255),
    "RUN": (150, 255, 110),
    "HEAT": (255, 140, 60),
}
FAM_NOTE = {
    "PERFECT": "fires on a Perfect", "MISS": "fires on the Miss slice", "TURN": "combat / turn start, always-on",
    "ACTION": "fires on your nudge or card", "RUN": "after a won fight / Server Rack", "HEAT": "netrun / Heat",
}
# id, name, rarity, family, effect, counter (None | ("pips", n) | ("stack",) | ("once",))
DAEMONS = [
    ("clean_signal", "Clean Signal", 1, "PERFECT", "3 consecutive Perfects: -2 Heat.", ("pips", 3)),
    ("kernel_sync", "Kernel Sync", 1, "PERFECT", "Each Perfect: +1 damage for the rest of the combat.", ("stack",)),
    ("zero_day", "Zero Day", 1, "PERFECT", "A Perfect on the Miss slice resolves as a 3x Crit.", None),
    ("botnet_seed", "Botnet Seed", 1, "PERFECT", "Each Perfect deploys a 1-HP drone on the triggered slice (max 2).", ("pips", 2)),
    ("adrenal_loop", "Adrenal Loop", 1, "PERFECT", "Each Perfect heals 2.", None),
    ("cascade", "Cascade", 1, "PERFECT", "Two Perfects in a row: +1 RAM.", ("pips", 2)),
    ("fault_tolerance", "Fault Tolerance", 1, "MISS", "The Miss slice deals 3 damage to the pointer target.", None),
    ("fail_forward", "Fail Forward", 1, "MISS", "The Miss slice restores 2 RAM.", None),
    ("stolen_intent", "Stolen Intent", 2, "MISS", "Once per combat, when you would resolve Miss, swap resolved slices with the target.", ("once",)),
    ("twin_pointer", "Twin Pointer", 2, "TURN", "Your wheel is also read at the bottom; both trigger. Max RAM halved.", None),
    ("warm_boot", "Warm Boot", 1, "TURN", "Start every combat with +2 RAM.", None),
    ("shield_cache", "Shield Cache", 1, "TURN", "Start every combat with 5 shield.", None),
    ("idle_armor", "Idle Armor", 1, "TURN", "Gain 2 block at the start of every turn.", None),
    ("static_field", "Static Field", 2, "TURN", "At the start of every turn, deal 1 damage to every enemy.", None),
    ("linked_bus", "Linked Bus", 1, "ACTION", "Nudging an enemy wheel also moves your wheel the same way, free.", None),
    ("tuning_fork", "Tuning Fork", 1, "ACTION", "Every nudge action grants 1 block.", None),
    ("feedback_loop", "Feedback Loop", 2, "ACTION", "Every card you play deals 1 damage to every enemy.", None),
    ("salvager", "Salvager", 0, "RUN", "+5 Cycles after every won fight.", None),
    ("field_medic", "Field Medic", 0, "RUN", "Heal 4 after every won fight.", None),
    ("bounty_code", "Bounty Code", 2, "RUN", "+1 Schematic banked after every won fight.", None),
    ("rack_skimmer", "Rack Skimmer", 1, "RUN", "Capturing a Server Rack banks 3 extra Schematics.", None),
    ("cold_exit", "Cold Exit", 1, "HEAT", "Finish a netrun without the Miss slice resolving: -3 Heat.", None),
    ("scrubber", "Scrubber", 1, "HEAT", "Capturing a Server Rack removes 1 Heat instead of adding it.", None),
    ("log_wiper", "Log Wiper", 2, "HEAT", "Finishing a netrun lowers Heat by 1.", None),
]
DM = {d[0]: d for d in DAEMONS}


def allowed_text(types):
    return "ANY SLICE" if not types else " + ".join(TYPE_NAME[t] for t in types)


# ------------------------------------------------------------------ icon drawing (256 grid, 4x supersample)
K4 = 4
_icache = {}


class Pad:
    def __init__(self):
        self.m = Image.new("L", (256 * K4, 256 * K4), 0)
        self.d = ImageDraw.Draw(self.m)

    @staticmethod
    def s(v):
        return [c * K4 for c in v]

    def poly(self, pts, on=True):
        self.d.polygon([(x * K4, y * K4) for x, y in pts], fill=255 if on else 0)

    def rect(self, b, on=True):
        self.d.rectangle(self.s(b), fill=255 if on else 0)

    def rrect(self, b, r, on=True):
        self.d.rounded_rectangle(self.s(b), radius=r * K4, fill=255 if on else 0)

    def circle(self, cx, cy, r, on=True):
        self.d.ellipse(self.s([cx - r, cy - r, cx + r, cy + r]), fill=255 if on else 0)

    def ellipse(self, b, on=True):
        self.d.ellipse(self.s(b), fill=255 if on else 0)

    def ring(self, cx, cy, r, w, on=True):
        self.circle(cx, cy, r + w / 2, on)
        self.circle(cx, cy, r - w / 2, not on)

    def arc(self, cx, cy, r, a0, a1, w, on=True, caps=True):
        self.d.arc(self.s([cx - r - w / 2, cy - r - w / 2, cx + r + w / 2, cy + r + w / 2]), a0, a1, fill=255 if on else 0, width=int(w * K4))
        if caps:
            for a in (a0, a1):
                x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
                self.circle(x, y, w / 2 - 0.5, on)

    def line(self, pts, w, on=True, caps=True):
        self.d.line([(x * K4, y * K4) for x, y in pts], fill=255 if on else 0, width=int(w * K4), joint="curve")
        if caps:
            for x, y in (pts[0], pts[-1]):
                self.circle(x, y, w / 2 - 0.5, on)
            for x, y in pts[1:-1]:
                self.circle(x, y, w / 2 - 0.5, on)

    def arrow(self, p0, p1, w, head, on=True):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        bx, by = p1[0] - ux * head * 0.9, p1[1] - uy * head * 0.9
        self.line([p0, (bx, by)], w, on, caps=False)
        self.circle(p0[0], p0[1], w / 2 - 0.5, on)
        px, py = -uy, ux
        self.poly([(p1[0], p1[1]), (bx + px * head * 0.62, by + py * head * 0.62), (bx - px * head * 0.62, by - py * head * 0.62)], on)

    def ering(self, cx, cy, a, b, rot, w, on=True):
        pts_o, pts_i = [], []
        for k in range(73):
            t = 2 * math.pi * k / 72
            for (aa, bb, lst) in ((a + w / 2, b + w / 2, pts_o), (a - w / 2, b - w / 2, pts_i)):
                x, y = aa * math.cos(t), bb * math.sin(t)
                c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
                lst.append((cx + x * c - y * s, cy + x * s + y * c))
        m = Image.new("L", self.m.size, 0)
        dm = ImageDraw.Draw(m)
        dm.polygon([(x * K4, y * K4) for x, y in pts_o], fill=255)
        dm.polygon([(x * K4, y * K4) for x, y in pts_i], fill=0)
        self.m = ImageChops.lighter(self.m, m) if on else ImageChops.subtract(self.m, m)
        self.d = ImageDraw.Draw(self.m)

    def flame(self, cx, base, h, w, on=True):
        r = w / 2
        self.circle(cx, base - r, r, on)
        self.poly([(cx - r * 0.98, base - r * 1.1), (cx + r * 0.98, base - r * 1.1), (cx + r * 0.25, base - h), (cx - r * 0.1, base - h * 0.78)], on)


def _hexpts(cx, cy, r, rot=0):
    return [(cx + r * math.cos(math.radians(rot + 60 * i)), cy + r * math.sin(math.radians(rot + 60 * i))) for i in range(6)]


def _star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        rr = R if i % 2 == 0 else r
        a = math.radians(rot + 180 * i / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# ---- firmware effect glyphs
def g_patch_plus(p):
    p.rect([36, 116, 176, 160]); p.rect([84, 68, 128, 208])
    p.rect([162, 50, 236, 76]); p.rect([186, 26, 212, 100])


def g_hardened(p):
    p.poly(_hexpts(128, 128, 112, 0))
    p.poly(_hexpts(128, 128, 84, 0), on=False)
    p.poly(_hexpts(128, 128, 70, 0))
    for x in (92, 128, 164):
        p.circle(x, 128, 15, on=False)


def g_burner(p):
    p.ellipse([30, 176, 226, 232]); p.ellipse([74, 190, 182, 218], on=False)
    p.flame(80, 182, 92, 44); p.flame(128, 182, 150, 54); p.flame(176, 182, 92, 44)
    p.rect([30, 176, 226, 182], on=False)


def g_leech(p):
    p.circle(128, 160, 76)
    p.poly([(128, 16), (58, 128), (198, 128)])
    p.rect([84, 136, 172, 152], on=False)
    p.poly([(92, 150), (116, 150), (104, 194)], on=False)
    p.poly([(140, 150), (164, 150), (152, 194)], on=False)


def g_mirror(p):
    p.poly([(20, 52), (20, 204), (104, 128)])
    p.poly([(236, 52), (236, 204), (152, 128)])
    p.rect([118, 24, 138, 232])


def g_shunt(p):
    p.line([(128, 236), (128, 150)], 36, caps=False)
    p.arrow((128, 156), (40, 46), 34, 76)
    p.arrow((128, 156), (216, 46), 34, 76)
    p.circle(128, 150, 26)


def g_overvolt(p):
    p.poly([(160, 12), (60, 142), (118, 142), (88, 244), (200, 102), (140, 102), (186, 12)])


def g_bulkhead(p):
    p.rrect([30, 36, 226, 220], 26)
    p.rect([58, 92, 198, 110], on=False); p.rect([58, 146, 198, 164], on=False)
    for x, y in ((54, 60), (202, 60), (54, 196), (202, 196)):
        p.circle(x, y, 9, on=False)


def g_siphon(p):
    p.arc(118, 100, 60, 180, 360, 30)
    p.rect([43, 98, 73, 160]); p.rect([163, 98, 193, 186])
    p.pieslice = None
    p.d.pieslice(Pad.s([16, 120, 100, 228]), 0, 180, fill=255)
    p.rect([16, 172, 100, 176])
    p.flame(178, 248, 50, 34)


def g_static_coat(p):
    p.poly([(40, 30), (216, 30), (216, 118), (196, 172), (128, 232), (60, 172), (40, 118)])
    p.line([(56, 98), (88, 74), (118, 108), (150, 74), (180, 108), (204, 84)], 16, on=False)
    p.line([(64, 152), (92, 128), (120, 160), (150, 128), (178, 158)], 16, on=False)


def g_barbed_wire(p):
    p.rect([8, 116, 248, 140])
    for x in (52, 128, 204):
        p.line([(x - 34, 92), (x + 34, 164)], 16)
        p.line([(x + 34, 92), (x - 34, 164)], 16)
        p.circle(x, 128, 22)


def g_recycler(p):
    V = [(128 + 108 * math.cos(math.radians(-90 + 120 * i)), 146 + 108 * math.sin(math.radians(-90 + 120 * i))) for i in range(3)]
    for i in range(3):
        a, b = V[i], V[(i + 1) % 3]
        s = (a[0] + (b[0] - a[0]) * 0.16, a[1] + (b[1] - a[1]) * 0.16)
        e = (a[0] + (b[0] - a[0]) * 0.80, a[1] + (b[1] - a[1]) * 0.80)
        p.arrow(s, e, 30, 66)


def g_coolant_loop(p):
    w = 28
    p.line([(48, 52), (196, 52)], w); p.arc(196, 92, 40, -90, 90, w)
    p.line([(196, 132), (60, 132)], w); p.arc(60, 172, 40, 90, 270, w)
    p.line([(60, 212), (208, 212)], w)
    for x in (100, 156):
        p.rect([x - 6, 30, x + 6, 234])


def g_counterstrike(p):
    p.arrow((36, 80), (236, 80), 34, 80)
    p.arrow((220, 176), (20, 176), 34, 80)


def g_nanite_mesh(p):
    for (cx, cy) in ((128, 78), (82, 160), (174, 160)):
        p.poly(_hexpts(cx, cy, 54, 30))
    for (cx, cy) in ((128, 78), (82, 160), (174, 160)):
        p.poly(_hexpts(cx, cy, 22, 30), on=False)


def g_power_cell(p):
    p.rrect([22, 62, 206, 194], 18); p.rrect([200, 100, 238, 156], 8)
    p.rect([76, 116, 152, 140], on=False); p.rect([102, 90, 126, 166], on=False)


def g_tracer(p):
    p.rect([100, 92, 176, 164])
    p.d.pieslice(Pad.s([136, 92, 244, 164]), 270, 450, fill=255)
    p.rect([100, 86, 112, 170])
    p.line([(28, 102), (76, 102)], 16); p.line([(8, 128), (80, 128)], 16); p.line([(28, 154), (76, 154)], 16)


def g_skimmer(p):
    for y in (186, 146):
        p.ellipse([32, y - 30, 196, y + 30])
        p.ellipse([32, y - 34, 196, y + 18], on=False)
        p.ellipse([32, y - 36, 196, y + 12])
    p.poly([(96, 40), (240, 70), (226, 116), (82, 86)])
    p.line([(102, 60), (226, 86)], 8, on=False)


# ---- daemon sigils
def s_clean_signal(p):
    pts = [(24 + x * 2.08, 128 - 64 * math.sin(math.radians(x * 5.4))) for x in range(101)]
    p.line(pts, 34)


def s_cold_exit(p):
    p.rect([46, 26, 154, 48]); p.rect([46, 208, 154, 230]); p.rect([46, 26, 68, 230]); p.rect([132, 26, 154, 98]); p.rect([132, 160, 154, 230])
    p.arrow((92, 129), (244, 129), 34, 72)


def s_scrubber(p):
    p.rrect([96, 18, 160, 112], 16)
    p.rrect([30, 104, 226, 152], 10)
    for k in range(7):
        x = 40 + k * 29
        p.rect([x, 160, x + 16, 228])


def s_fault_tolerance(p):
    p.rect([8, 162, 92, 190]); p.rect([164, 162, 248, 190])
    p.arc(128, 176, 52, 180, 360, 28)
    p.circle(76, 176, 24); p.circle(180, 176, 24)
    p.poly([(116, 40), (148, 40), (140, 92), (124, 92)]); p.circle(132, 108, 11)


def s_kernel_sync(p):
    p.ering(128, 128, 112, 42, 35, 20)
    p.ering(128, 128, 112, 42, -35, 20)
    p.circle(128, 128, 34)


def s_zero_day(p):
    p.ering(128, 128, 62, 104, 0, 34)
    p.line([(54, 236), (202, 20)], 30)


def s_linked_bus(p):
    # belt drive: two wheels in one belt, each with its own pointer notch
    p.rrect([10, 62, 246, 194], 66)
    p.rrect([30, 82, 226, 174], 46, on=False)
    p.circle(76, 128, 30); p.circle(180, 128, 30)
    p.poly([(64, 22), (88, 22), (76, 54)]); p.poly([(168, 22), (192, 22), (180, 54)])


def s_stolen_intent(p):
    # domino (bandit) mask with ribbon tails
    p.poly([(18, 98), (52, 62), (104, 74), (128, 92), (152, 74), (204, 62), (238, 98), (226, 160), (176, 186),
            (140, 170), (128, 150), (116, 170), (80, 186), (30, 160)])
    p.poly([(52, 112), (100, 100), (110, 134), (66, 146)], on=False)
    p.poly([(204, 112), (156, 100), (146, 134), (190, 146)], on=False)
    p.poly([(22, 110), (0, 196), (34, 176), (38, 150)])
    p.poly([(234, 110), (256, 196), (222, 176), (218, 150)])


def s_twin_pointer(p):
    p.ring(128, 128, 62, 26)
    p.poly([(88, 4), (168, 4), (128, 58)])
    p.poly([(88, 252), (168, 252), (128, 198)])
    p.circle(128, 128, 18)


def s_botnet_seed(p):
    p.ellipse([88, 170, 168, 244])
    p.line([(128, 176), (128, 116)], 20)
    p.line([(128, 128), (60, 66)], 20); p.line([(128, 128), (196, 66)], 20)
    p.circle(60, 58, 30); p.circle(196, 58, 30); p.circle(128, 96, 26)


def s_warm_boot(p):
    p.arc(128, 140, 86, -55, 235, 32)
    p.rrect([112, 16, 144, 138], 16)


def s_shield_cache(p):
    p.ellipse([36, 22, 220, 84]); p.rect([36, 53, 220, 204]); p.ellipse([36, 174, 220, 236])
    p.ellipse([36, 44, 220, 106], on=False); p.ellipse([36, 40, 220, 98])
    p.poly([(96, 118), (160, 118), (160, 160), (128, 200), (96, 160)], on=False)


def s_idle_armor(p):
    p.rect([36, 16, 220, 42]); p.rect([36, 214, 220, 240])
    p.poly([(60, 42), (196, 42), (196, 60), (144, 128), (196, 196), (196, 214), (60, 214), (60, 196), (112, 128), (60, 60)])
    p.poly([(84, 196), (172, 196), (128, 158)], on=False)


def s_adrenal_loop(p):
    p.ring(128, 128, 98, 22)
    p.line([(10, 136), (72, 136), (98, 54), (132, 206), (158, 100), (176, 136), (246, 136)], 24)


def s_fail_forward(p):
    p.rect([40, 20, 80, 172]); p.rect([40, 136, 184, 176])
    p.poly([(176, 100), (176, 212), (244, 156)])
    p.line([(120, 30), (176, 86)], 18); p.line([(176, 30), (120, 86)], 18)


def s_feedback_loop(p):
    # a speaker cone feeding back into itself: cone + a return arrow arcing over it
    p.rect([24, 104, 64, 168])
    p.poly([(64, 104), (124, 60), (124, 212), (64, 168)])
    p.arc(128, 136, 92, -70, 70, 24)
    p.arc(128, 136, 52, -60, 60, 22)
    p.poly([(176, 236), (220, 210), (170, 200)])


def s_tuning_fork(p):
    p.arc(128, 104, 54, 0, 180, 30, caps=False)
    p.rect([59, 20, 89, 106]); p.rect([167, 20, 197, 106])
    p.rect([113, 156, 143, 240])
    p.circle(128, 240, 18)


def s_static_field(p):
    p.circle(128, 196, 28)
    for r in (68, 112):
        p.arc(128, 196, r, 215, 325, 26)
    p.arc(128, 196, 156, 228, 312, 26)


def s_cascade(p):
    p.rect([16, 30, 100, 82]); p.rect([86, 98, 170, 150]); p.rect([156, 166, 240, 218])
    p.flame(100, 118, 34, 22); p.flame(170, 186, 34, 22)
    p.poly([(100, 92), (90, 110), (110, 110)])


def s_salvager(p):
    p.rrect([84, 12, 172, 40], 10)
    p.rect([114, 36, 142, 150])
    p.arc(104, 156, 40, -10, 180, 30)
    p.poly([(50, 156), (78, 156), (64, 118)])


def s_field_medic(p):
    p.arc(128, 74, 42, 180, 360, 22)
    p.rrect([24, 72, 232, 226], 22)
    p.rect([108, 104, 148, 200], on=False); p.rect([80, 132, 176, 172], on=False)


def s_bounty_code(p):
    pts = _star(128, 134, 116, 52)
    p.poly(pts)
    for i in range(0, 10, 2):
        p.circle(pts[i][0], pts[i][1], 16)
    p.circle(128, 134, 24, on=False)


def s_rack_skimmer(p):
    p.rrect([46, 14, 210, 242], 14)
    for y in (42, 104, 166):
        p.rect([70, y, 186, y + 36], on=False)
        p.circle(168, y + 18, 8)
        p.rect([82, y + 12, 140, y + 24])


def s_log_wiper(p):
    p.poly([(36, 18), (150, 18), (196, 64), (196, 238), (36, 238)])
    for y in (66, 104):
        p.rect([62, y, 170, y + 16], on=False)
    p.poly([(150, 18), (150, 64), (196, 64)], on=False)
    p.poly([(98, 236), (208, 126), (246, 164), (136, 252)], on=False)
    p.poly([(112, 232), (206, 138), (236, 168), (142, 254)])
    p.line([(144, 200), (172, 172)], 6, on=False)


ICONS = {}
for _k, _v in list(globals().items()):
    if _k.startswith("g_"):
        ICONS[_k[2:]] = _v
    elif _k.startswith("s_"):
        ICONS[_k[2:]] = _v


def icon(name, px):
    """White-on-transparent alpha mask (L) of an icon at px."""
    key = (name, px)
    if key in _icache:
        return _icache[key]
    big = ("big", name)
    if big not in _icache:
        p = Pad()
        ICONS[name](p)
        _icache[big] = p.m
    m = _icache[big].resize((px, px), Image.LANCZOS)
    _icache[key] = m
    return m


def icon_rgba(name, px, fill=(255, 255, 255), ow=0, outline=L.INK):
    m = icon(name, px)
    pad = ow + 1
    A = Image.new("L", (px + 2 * pad, px + 2 * pad), 0)
    A.paste(m, (pad, pad))
    out = Image.new("RGBA", A.size, (0, 0, 0, 0))
    if ow:
        o = A.filter(ImageFilter.MaxFilter(2 * ow + 1))
        lay = Image.new("RGBA", A.size, outline + (255,))
        lay.putalpha(o)
        out.alpha_composite(lay)
    lay = Image.new("RGBA", A.size, fill + (255,))
    lay.putalpha(A)
    out.alpha_composite(lay)
    return out


# ------------------------------------------------------------------ the chip
GOLD_PIN = (226, 186, 92)


def _glow(size, box, col, r, k=1.0):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * k)))
    lay = Image.new("RGBA", size, col + (0,))
    lay.putalpha(m)
    return lay


def chip(fid, s, lit=0.0, glyph=True, led=True, flat=False, grey=False):
    """Socketed die, s px wide (height 1.12 s). Pins along the TOP edge (they plug into the slice bezel).
    lit 0..1: trigger flare (LED + plate glow + pins hot). flat=True: the sticker-print version (no gloss/LED glow)."""
    _, name, rar, types, eff = FW[fid]
    S = 4 if s < 80 else 2
    W = s * S
    H = int(s * 1.12) * S
    pad = int(W * 0.10)
    im = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad, pad
    pin_h = int(H * 0.13)
    bx0, by0, bx1, by1 = ox, oy + pin_h, ox + W, oy + H
    ch = int(W * 0.16)
    ink = L.INK + (255,)
    # pins (top comb)
    n = 5 if s >= 22 else 3
    pw = W * (0.09 if n == 5 else 0.14)
    pin_col = tuple(int(c + (255 - c) * lit * 0.8) for c in GOLD_PIN)
    for i in range(n):
        x = bx0 + ch + (W - 2 * ch) * (i + 0.5) / n
        d.rectangle([x - pw / 2, oy + 2, x + pw / 2, by0 + 4 * S], fill=pin_col + (255,), outline=ink, width=max(1, S))
    # body: chamfered octagon (faceted die)
    oct_ = [(bx0 + ch, by0), (bx1 - ch, by0), (bx1, by0 + ch), (bx1, by1 - ch), (bx1 - ch, by1), (bx0 + ch, by1), (bx0, by1 - ch), (bx0, by0 + ch)]
    d.polygon(oct_, fill=(44, 42, 56, 255), outline=ink)
    d.line(oct_ + [oct_[0]], fill=ink, width=max(2, int(W * 0.03)))
    # facets: lit top-left bevel, dark bottom-right bevel
    e = int(W * 0.10)
    inner = [(bx0 + ch + e * 0.4, by0 + e), (bx1 - ch - e * 0.4, by0 + e), (bx1 - e, by0 + ch + e * 0.4), (bx1 - e, by1 - ch - e * 0.4),
             (bx1 - ch - e * 0.4, by1 - e), (bx0 + ch + e * 0.4, by1 - e), (bx0 + e, by1 - ch - e * 0.4), (bx0 + e, by0 + ch + e * 0.4)]
    if not flat:
        d.polygon([oct_[7], oct_[0], oct_[1], inner[1], inner[0], inner[7]], fill=(92, 88, 112, 255))
        d.polygon([oct_[3], oct_[4], oct_[5], inner[5], inner[4], inner[3]], fill=(24, 22, 32, 255))
        d.polygon([oct_[1], oct_[2], oct_[3], inner[3], inner[2], inner[1]], fill=(34, 32, 44, 255))
        d.polygon([oct_[5], oct_[6], oct_[7], inner[7], inner[6], inner[5]], fill=(70, 66, 86, 255))
    plate = (18, 16, 26) if not flat else (30, 28, 40)
    if lit > 0:
        plate = tuple(int(plate[i] + (RAR_COL[rar][i] * 0.55 - plate[i]) * lit * 0.6) for i in range(3))
    d.polygon(inner, fill=plate + (255,), outline=(10, 9, 14, 255))
    # orientation notch on the bottom edge (DIP style)
    nr = W * 0.07
    d.pieslice([(bx0 + bx1) / 2 - nr, by1 - nr, (bx0 + bx1) / 2 + nr, by1 + nr], 180, 360, fill=(10, 9, 14, 255))
    # gloss streak
    if not flat:
        g = Image.new("L", im.size, 0)
        ImageDraw.Draw(g).polygon([(inner[0][0], inner[0][1]), (inner[0][0] + W * 0.22, inner[0][1]), (inner[7][0], inner[7][1] + W * 0.22), (inner[7][0], inner[7][1])], fill=60)
        im = L.SL.over(im, (255, 255, 255), g)
        d = ImageDraw.Draw(im)
    # rarity pips (greyscale-safe): small bars bottom-left on the plate
    nr_ = RAR_PIPS[rar]
    if s >= 30:
        for i in range(nr_):
            x = inner[6][0] + W * 0.02 + i * W * 0.075
            d.rectangle([x, by1 - e - W * 0.13, x + W * 0.045, by1 - e - W * 0.05], fill=(235, 235, 245, 255))
    # LED (rarity colour), top-right corner of the plate
    lc = RAR_COL[rar]
    lr = max(W * 0.075, 2.2 * S)
    lx, ly = bx1 - e - lr * 1.6, by0 + e + lr * 1.6
    if led and not flat:
        im.alpha_composite(_glow(im.size, [lx - lr * 1.8, ly - lr * 1.8, lx + lr * 1.8, ly + lr * 1.8], lc, lr * 0.8, 0.45 + 1.5 * lit))
        d = ImageDraw.Draw(im)
    d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(tuple(min(255, int(c * (0.85 + 0.3 * lit) + 40 * lit)) for c in lc) + (255,)), outline=ink, width=max(1, S // 2))
    if not flat:
        d.ellipse([lx - lr * 0.45, ly - lr * 0.55, lx - lr * 0.05, ly - lr * 0.15], fill=(255, 255, 255, 220))
    # glyph
    if glyph:
        gs = int((inner[2][0] - inner[6][0]) * 0.70)
        gim = icon_rgba(fid, gs, ow=max(1, S), fill=(255, 255, 255))
        gx = (bx0 + bx1) / 2 - gim.width / 2
        gy = (by0 + by1) / 2 - gim.height / 2 + H * 0.02
        if lit > 0:
            im.alpha_composite(_glow(im.size, [gx, gy, gx + gim.width, gy + gim.height], (255, 240, 200), gs * 0.12, 0.9 * lit))
        im.alpha_composite(gim, (int(gx), int(gy)))
    out = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    if grey:
        a = out.split()[3]
        out = ImageOps.grayscale(out.convert("RGB")).convert("RGBA")
        out.putalpha(a)
    return out


def chip_anchor(s):
    """Offset of the chip centre inside the image returned by chip(s)."""
    pad = int(s * 0.10)
    return pad + s / 2, pad + s * 1.12 / 2


# ------------------------------------------------------------------ the daemon CRT tile
def daemon_tile(did, s, t=0.0, fire=0.0, counter_val=None, spent=False, grey=False, label=False):
    """s px square CRT tile. t: idle phase 0..1 (loops). fire 0..1: trigger flash. counter_val: pips filled / stack."""
    _, name, rar, fam, eff, counter = DM[did]
    S = 4 if s < 90 else 2
    W = s * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rc = RAR_COL[rar]
    fc = FAM[fam]
    ink = L.INK + (255,)
    # bezel by rarity: common gunmetal, uncommon cyan-anodised edge, rare gold bezel + corner brackets
    bez = {0: (66, 68, 80), 1: (40, 70, 86), 2: (120, 92, 30)}[min(rar, 2)]
    r = W * 0.16
    d.rounded_rectangle([0, 0, W - 1, W - 1], radius=r, fill=bez + (255,), outline=ink, width=max(2, int(W * 0.025)))
    edge = tuple(int(c * 0.9) for c in rc)
    d.rounded_rectangle([W * 0.035, W * 0.035, W * 0.965, W * 0.965], radius=r * 0.8, outline=edge + (255,), width=max(1, int(W * (0.018 if rar else 0.01))))
    if rar >= 2:
        L_ = W * 0.22
        for (x, y, sx, sy) in ((W * 0.02, W * 0.02, 1, 1), (W * 0.98, W * 0.02, -1, 1), (W * 0.02, W * 0.98, 1, -1), (W * 0.98, W * 0.98, -1, -1)):
            d.line([(x, y + sy * r * 0.2), (x + sx * L_, y + sy * r * 0.2)], fill=(255, 226, 120, 255), width=int(W * 0.03))
            d.line([(x + sx * r * 0.2, y), (x + sx * r * 0.2, y + sy * L_)], fill=(255, 226, 120, 255), width=int(W * 0.03))
    # glass
    g0, g1 = W * 0.11, W * 0.83
    glass_col = tuple(int(c * 0.10) + 6 for c in fc)
    if spent:
        glass_col = (14, 14, 18)
    d.rounded_rectangle([g0, g0, g1 + g0 * 0.0 + W * 0.06, g1], radius=W * 0.09, fill=glass_col + (255,))
    gx0, gy0, gx1, gy1 = g0, g0, g1 + W * 0.06, g1
    # sigil in phosphor
    breath = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    gs = int((gy1 - gy0) * 0.72)
    cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    sc = 1.0 + 0.14 * fire
    gs2 = int(gs * sc)
    m = icon(did, gs2)
    if not spent:
        core = tuple(int(c + (255 - c) * (0.55 + 0.45 * fire)) for c in fc)
        glow_k = 0.55 + 0.25 * breath + 1.4 * fire
        gl = Image.new("L", im.size, 0)
        gl.paste(m, (int(cx - gs2 / 2), int(cy - gs2 / 2)))
        gl = gl.filter(ImageFilter.GaussianBlur(W * 0.05)).point(lambda v: min(255, int(v * glow_k)))
        im = L.SL.over(im, fc, gl)
        if fire > 0.05:   # chromatic split on fire
            for dx, col in ((-W * 0.03 * fire, (255, 60, 90)), (W * 0.03 * fire, (60, 220, 255))):
                mm = Image.new("L", im.size, 0)
                mm.paste(m, (int(cx - gs2 / 2 + dx), int(cy - gs2 / 2)))
                im = L.SL.over(im, col, mm.point(lambda v: int(v * 0.55 * fire)))
        mm = Image.new("L", im.size, 0)
        mm.paste(m, (int(cx - gs2 / 2), int(cy - gs2 / 2)))
        im = L.SL.over(im, core, mm)
        if fire > 0:
            fl = Image.new("L", im.size, 0)
            ImageDraw.Draw(fl).rounded_rectangle([gx0, gy0, gx1, gy1], radius=W * 0.09, fill=int(120 * fire))
            im = L.SL.over(im, (255, 255, 255), fl)
    else:
        mm = Image.new("L", im.size, 0)
        mm.paste(m, (int(cx - gs2 / 2), int(cy - gs2 / 2)))
        im = L.SL.over(im, (70, 70, 80), mm)
        rng = np.random.default_rng(int(t * 1000) + 7)
        st = Image.fromarray((rng.random((int(gy1 - gy0), int(gx1 - gx0))) * 70).astype(np.uint8))
        sm = Image.new("L", im.size, 0)
        sm.paste(st, (int(gx0), int(gy0)))
        msk = Image.new("L", im.size, 0)
        ImageDraw.Draw(msk).rounded_rectangle([gx0, gy0, gx1, gy1], radius=W * 0.09, fill=255)
        im = L.SL.over(im, (200, 200, 210), ImageChops.multiply(sm, msk))
    d = ImageDraw.Draw(im)
    # scanlines + rolling bar (idle)
    sl = Image.new("L", im.size, 0)
    ds = ImageDraw.Draw(sl)
    step = max(3, int(W / 40))
    for y in range(int(gy0), int(gy1), step):
        ds.line([(gx0, y), (gx1, y)], fill=70, width=max(1, step // 3))
    msk = Image.new("L", im.size, 0)
    ImageDraw.Draw(msk).rounded_rectangle([gx0, gy0, gx1, gy1], radius=W * 0.09, fill=255)
    im = L.SL.over(im, (0, 0, 0), ImageChops.multiply(sl, msk))
    roll = Image.new("L", im.size, 0)
    ry = gy0 + (gy1 - gy0) * ((t * 1.0) % 1.0)
    ImageDraw.Draw(roll).rectangle([gx0, ry - W * 0.05, gx1, ry + W * 0.05], fill=26)
    roll = roll.filter(ImageFilter.GaussianBlur(W * 0.03))
    im = L.SL.over(im, fc if not spent else (120, 120, 130), ImageChops.multiply(roll, msk))
    # glass sheen
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).polygon([(gx0, gy0), (gx0 + (gx1 - gx0) * 0.55, gy0), (gx0, gy0 + (gy1 - gy0) * 0.45)], fill=34)
    im = L.SL.over(im, (255, 255, 255), ImageChops.multiply(sh, msk))
    d = ImageDraw.Draw(im)
    # bottom lip: rarity pips (left) + heartbeat LED (right)
    by = W * 0.915
    for i in range(RAR_PIPS[rar]):
        x = W * 0.14 + i * W * 0.085
        d.rectangle([x, by - W * 0.025, x + W * 0.055, by + W * 0.02], fill=(236, 236, 244, 255))
    led_on = (t % 1.0) < 0.12 or fire > 0.3
    lc = fc if led_on and not spent else tuple(int(c * 0.3) for c in (fc if not spent else (120, 120, 120)))
    lr = W * 0.035
    d.ellipse([W * 0.86 - lr, by - lr, W * 0.86 + lr, by + lr], fill=lc + (255,), outline=ink, width=max(1, S // 2))
    out = im.resize((s, s), Image.LANCZOS)
    if grey:
        a = out.split()[3]
        out = ImageOps.grayscale(out.convert("RGB")).convert("RGBA")
        out.putalpha(a)
    return out


def counter_strip(did, w, filled, fire=0.0):
    """Counter under a tile: pips (Clean Signal 3, Cascade 2, Botnet Seed drones 2), a stack number (Kernel Sync),
    or ONCE / SPENT (Stolen Intent)."""
    _, name, rar, fam, eff, counter = DM[did]
    fc = FAM[fam]
    h = max(12, int(w * 0.24))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if counter is None:
        return None
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=(8, 10, 16, 230), outline=tuple(int(c * 0.6) for c in fc) + (255,), width=1)
    if counter[0] == "pips":
        n = counter[1]
        pw = (w - 12 - (n - 1) * 4) / n
        for i in range(n):
            x = 6 + i * (pw + 4)
            col = fc + (255,) if i < filled else tuple(int(c * 0.22) for c in fc) + (255,)
            d.rounded_rectangle([x, h * 0.3, x + pw, h * 0.7], radius=2, fill=col)
    elif counter[0] == "stack":
        d.text((w / 2, h / 2 + 1), "+%d DMG" % filled, font=L.f_num(int(h * 0.9)), fill=fc + (255,), anchor="mm")
    elif counter[0] == "once":
        txt = "READY" if filled == 0 else "SPENT"
        col = fc if filled == 0 else (130, 130, 140)
        d.text((w / 2, h / 2 + 1), txt, font=L.f_mono(int(h * 0.8)), fill=col + (255,), anchor="mm")
    return im


# ------------------------------------------------------------------ socketed wheel
import slicekit as K
K.TIER_STYLE = "a"
K.TIER_STRENGTH = 2

SOCKET_RHO = 160.0     # master px (R_IN = 130, R_OUT = 360): the inner, hub-side band under the read block
SOCKET_DA = 0.0        # on the slice midline
CHIP_MASTER = 50.0     # chip width in master px (33 px at r = 220)
SMALL_RHO = 160.0      # LOD (r < 150): same place, the read block shrinks less than the slice


def wheel_cached(slices, r_px, key):
    fn = os.path.join(CACHE, "wheel_%s_%d.png" % (key, r_px))
    if os.path.exists(fn):
        return Image.open(fn).convert("RGBA")
    w = K.wheel(slices, t=0.45, r_px=r_px)
    w.save(fn)
    return w


def socket_pos(n, i, r_px, size):
    """Chip centre on a wheel image: on the slice midline, in the inner band, pins toward the hub (round 34)."""
    span = 360 / n
    ang = i * span - span / 2 * SOCKET_DA
    small = r_px < 150
    k = r_px / 360.0
    rho = (SMALL_RHO if small else SOCKET_RHO) * k
    c = size / 2
    return c + rho * math.sin(math.radians(ang)), c - rho * math.cos(math.radians(ang)), ang


def chip_px(r_px):
    return max(12, int(round(CHIP_MASTER * r_px / 360.0 * (0.9 if r_px < 150 else 1.0))))


def put_chip(img, fid, x, y, ang, s, lit=0.0, upright_glyph=True):
    """Chip body radial (pins to the rim), glyph kept upright like the read block."""
    body = chip(fid, s, lit=lit, glyph=False)
    ax, ay = chip_anchor(s)
    # the socket: a recess cut into the bezel with a rarity-coloured lip (what makes it read at r = 60)
    rc = RAR_COL[FW[fid][2]]
    k = 4
    so = int(s * 1.30) * k
    sock = Image.new("RGBA", (so, int(so * 1.1)), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sock)
    ds.rounded_rectangle([k, k, so - k, int(so * 1.1) - k], radius=so * 0.18, fill=(6, 5, 10, 235),
                         outline=tuple(int(c * (0.75 + 0.25 * lit)) for c in rc) + (255,), width=max(k, int(so * 0.06)))
    sock = sock.resize((sock.width // k, sock.height // k), Image.LANCZOS).rotate(-(ang + 180), Image.BICUBIC, expand=True)
    if lit > 0:
        img.alpha_composite(_glow(img.size, [x - s, y - s, x + s, y + s], rc, s * 0.4, lit))
    img.alpha_composite(sock, (int(x - sock.width / 2), int(y - sock.height / 2)))
    rot = body.rotate(-(ang + 180), Image.BICUBIC, expand=True)
    # expand=True recentres: the anchor maps to the image centre only when anchor is the centre; it is
    ox, oy = rot.width / 2, rot.height / 2
    img.alpha_composite(rot, (int(x - ox), int(y - oy)))
    if s >= 20:
        gs = int(s * 0.50)
        g = icon_rgba(fid, gs, ow=1)
        if lit > 0:
            img.alpha_composite(_glow(img.size, [x - gs * 0.6, y - gs * 0.6, x + gs * 0.6, y + gs * 0.6], (255, 240, 200), gs * 0.18, lit))
        img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2 - s * 0.04)))
    return img


def socket_wheel(slices, fws, r_px, key, angle=0.0, lit=None, lit_k=1.0):
    """slices: 6 (prog, val, tier, state); fws: list of firmware id or None per slice. Returns RGBA wheel image
    (rotated by angle degrees clockwise) with chips socketed."""
    base = wheel_cached(slices, r_px, key)
    img = base.copy()
    s = chip_px(r_px)
    n = len(slices)
    for i, f in enumerate(fws):
        if not f:
            continue
        x, y, a = socket_pos(n, i, r_px, img.width)
        img = put_chip(img, f, x, y, a, s, lit=(lit_k if lit == i else 0.0))
    if angle:
        img = img.rotate(-angle, Image.BICUBIC)
    return img


def grey(img):
    a = img.split()[3]
    g = ImageOps.grayscale(img.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def text(d, xy, s, size, col=(230, 230, 240), anchor="la", f=None, stroke=0):
    d.text(xy, s, font=f or L.f_mono(size), fill=tuple(col[:3]) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(6, 5, 10, 255))


def wrap(s, f, w):
    out, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if f.getlength(t) > w and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def bg(w=1920, h=1080, seed=1):
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3), np.float32)
    a[:] = (11, 10, 17)
    a += rng.normal(0, 2.0, (h, w, 1))
    yy = np.arange(h)[:, None]
    a[..., 2] += np.exp(-((yy - h) / 500.0) ** 2) * 8
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def header(img, title, sub, col=L.YEL):
    d = ImageDraw.Draw(img)
    d.text((32, 22), title, font=L.f_num(52), fill=(245, 245, 250, 255))
    d.text((34, 84), sub, font=L.f_mono(16), fill=(170, 170, 190, 255))
    return d


def section(d, x, y, s, col=L.YEL):
    d.rectangle([x, y + 4, x + 6, y + 30], fill=col + (255,))
    d.text((x + 16, y), s, font=L.f_num(30), fill=(240, 240, 248, 255))
