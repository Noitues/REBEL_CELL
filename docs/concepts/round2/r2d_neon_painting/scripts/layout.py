"""Shared layout data for the Blender builder and the Pillow post-pass.

Plain Python (no bpy), so both `blender --python` and system `python` import it.
Everything a still needs to line 3D geometry up with 2D labels lives here.
"""

W, H = 1920, 1080
SEED = 4242

# ---- City grid -------------------------------------------------------------
PITCH = 11.0          # street centreline spacing (world units)
STREET = 3.0          # street width
GRID_I = range(-8, 9)     # street lines along x
GRID_J = range(-2, 20)    # street lines along y

# City camera (same for stills 01-03)
CITY_CAM_LOC = (0.0, -45.0, 55.0)
CITY_CAM_TARGET = (0.0, 43.0, 0.0)
CITY_CAM_LENS = 24.0

# Navigation nodes: id, grid (i, j), label, kind
NODES = [
    ("A", (-2, 1), "SAFEHOUSE", "safe"),
    ("B", (0, 2), "RELAY 7", "relay"),
    ("C", (-3, 4), "DATA VAULT", "vault"),
    ("D", (2, 4), "HALCYON LABS", "target"),
    ("E", (0, 5), "NIGHT MARKET", "market"),
    ("F", (-1, 7), "SIGNAL SPIRE", "relay"),
    ("G", (3, 1), "BACKALLEY CLINIC", "clinic"),
    ("H", (2, 7), "ORBIS HQ", "boss"),
]
EDGES = [("A", "B"), ("A", "C"), ("B", "E"), ("B", "G"), ("C", "F"),
         ("E", "F"), ("E", "D"), ("G", "D"), ("D", "H"), ("F", "H")]
YOU_ARE_HERE = "A"

NODE_COLORS = {  # linear-ish RGB for emission
    "safe": (0.55, 1.0, 1.0),
    "relay": (0.62, 0.35, 1.0),
    "vault": (0.1, 0.75, 1.0),
    "target": (1.0, 0.12, 0.45),
    "market": (1.0, 0.5, 0.08),
    "clinic": (0.2, 1.0, 0.6),
    "boss": (1.0, 0.08, 0.12),
}


def node_world(node):
    i, j = node[1]
    return (i * PITCH, j * PITCH)


def edge_polyline(a, b):
    """L-shaped route along streets: along x first, then along y."""
    ax, ay = a
    bx, by = b
    pts = [(ax, ay)]
    if ax != bx and ay != by:
        pts.append((bx, ay))
    pts.append((bx, by))
    return pts


# ---- Combat layout (pixels) -----------------------------------------------
UI_DIST = 10.0     # distance of the flat UI plane from the camera
UI_LENS = 35.0
PPU = (W / 2) / (UI_DIST * 18.0 / UI_LENS)   # pixels per UI-plane unit


def px_to_ui(px, py):
    return ((px - W / 2) / PPU, (H / 2 - py) / PPU)


SPINNER_R_PX = 235
SPINNERS = {
    "player": {"center": (560, 430), "hp": (34, 40), "name": "CELL // VEX-0",
               "color": (0.1, 0.85, 1.0),
               # ticks per slice (sum 30), kind, value
               "slices": [(5, "atk", 6), (4, "blk", 4), (3, "hack", 2), (4, "empty", 0),
                          (5, "atk", 4), (3, "blk", 3), (3, "hack", 3), (3, "empty", 0)],
               "rot_ticks": 1.5},
    "enemy": {"center": (1360, 430), "hp": (27, 52), "name": "SENTINEL ICE  MK.IX",
              "color": (1.0, 0.15, 0.5),
              "slices": [(6, "atk", 8), (4, "empty", 0), (5, "blk", 6), (3, "atk", 3),
                         (4, "hack", 4), (5, "atk", 5), (3, "empty", 0)],
              "rot_ticks": -4.0},
}
SLICE_COLORS = {
    "atk": (1.0, 0.12, 0.38),
    "blk": (0.08, 0.7, 1.0),
    "hack": (1.0, 0.52, 0.06),
    "empty": (0.16, 0.1, 0.3),
}
SLICE_TAGS = {"atk": "ATK", "blk": "BLK", "hack": "HAK", "empty": ""}

HPBAR = {"w": 420, "h": 30, "dy": 290}   # below spinner centre

CARD_W, CARD_H = 196, 272
HAND_Y = 912
HAND = [  # name, cost, kind, text
    ("SPIKE", 1, "atk", "+3 to ATK slices"),
    ("FIREWALL", 1, "blk", "Next BLK x2"),
    ("BACKDOOR", 2, "hack", "Nudge wheel 3 ticks"),
    ("OVERCLOCK", 0, "atk", "Spin +20% speed"),
    ("GHOST PING", 1, "hack", "Peek enemy stop"),
]
HAND_X0, HAND_DX = 560, 210
HAND_FAN_DEG = 2.5
GO_BTN = {"center": (1640, 918), "w": 300, "h": 120}

# ---- Shop layout (pixels) --------------------------------------------------
SHOP_CARDS = [  # name, kind, price, text
    ("DAEMON FORK", "hack", 85, "Copy last slice"),
    ("RAZORWIRE", "atk", 60, "ATK slices +2"),
    ("MIRROR SHELL", "blk", 70, "Reflect 3 dmg"),
]
SHOP_CARD_XS = [330, 560, 790]
SHOP_ROW_Y = 560
SHOP_PARTS = [  # name, kind, price, text
    ("OVERCLOCK SLICE", "slice", 120, "+1 ATK slice, 4 ticks"),
    ("CHROME RIM", "rim", 150, "Wheel gains 2 ticks"),
    ("GHOST POINTER", "pointer", 95, "Pointer skips EMPTY"),
]
SHOP_PART_XS = [1130, 1400, 1670]
LEAVE_BTN = {"center": (190, 1000), "w": 250, "h": 84}
CREDITS = 240


def slice_geometry(sp):
    """(a0_deg, a1_deg, kind, value) per slice. Angle 90 = top (pointer); ticks run clockwise."""
    out = []
    t = 0.0
    for n, kind, val in sp["slices"]:
        a0 = 90.0 - (t + sp["rot_ticks"]) * 12.0
        a1 = 90.0 - (t + n + sp["rot_ticks"]) * 12.0
        out.append((a1, a0, kind, val))   # a1 < a0
        t += n
    return out


def hand_card(k):
    """Pixel centre and fan angle (deg, counter-clockwise) of hand card k."""
    mid = (len(HAND) - 1) / 2.0
    off = k - mid
    return (HAND_X0 + k * HAND_DX, HAND_Y + off * off * 5.0), -off * HAND_FAN_DEG
