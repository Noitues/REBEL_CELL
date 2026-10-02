"""Round 18 raid grid: the district layout shared by the Blender scene (district.py) and the post
scripts (finish.py, screens.py). Pure Python, no numpy, so Blender can import it too.

World: metres, z up, ground at z = 0. The Cell's HQ block sits in the middle; claimed nodes are pads
ON THE STREET PLANE at intersections; links run along the streets between them.
Camera: orthographic, looking north-east and down (3/4 iso), so streets read as diagonals.
"""
import math

W, H = 1920, 1080          # final frame
RW, RH = 2880, 1620        # render size (1.5x, downsampled in post)

# ------------------------------------------------------------------ camera
CAM = dict(
    yaw=48.0,             # horizontal view direction, degrees from +x toward +y
    pitch=50.0,           # degrees below the horizon
    target=(20.01, -38.88, 0.0),
    ortho=440.0,          # visible width in metres (core pad lands at 960, 590)
    dist=900.0,
)


def cam_basis():
    """Right, up and forward unit vectors of the camera (world space)."""
    yw, pt = math.radians(CAM["yaw"]), math.radians(CAM["pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    right = (math.sin(yw), -math.cos(yw), 0.0)
    # up = right x fwd
    up = (right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0])
    return right, up, fwd


def cam_location():
    _, _, f = cam_basis()
    t = CAM["target"]
    return (t[0] - f[0] * CAM["dist"], t[1] - f[1] * CAM["dist"], t[2] - f[2] * CAM["dist"])


def project(x, y, z=0.0, w=W, h=H):
    """World point -> (px, py, depth) in a w x h frame."""
    r, u, f = cam_basis()
    t = CAM["target"]
    d = (x - t[0], y - t[1], z - t[2])
    xc = d[0] * r[0] + d[1] * r[1] + d[2] * r[2]
    yc = d[0] * u[0] + d[1] * u[1] + d[2] * u[2]
    zc = d[0] * f[0] + d[1] * f[1] + d[2] * f[2]
    s = CAM["ortho"]
    return ((xc / s + 0.5) * w, (0.5 - yc / (s * h / w)) * h, zc)


# ------------------------------------------------------------------ streets
STREETS_X = [-270, -200, -130, -60, 10, 80, 150, 220, 290]   # streets running along y (constant x)
STREETS_Y = [-260, -190, -120, -50, 20, 90, 160, 230, 300]   # streets running along x (constant y)
AVENUE_X, AVENUE_Y = 10, -50
SW = 17.0                  # street width
AW = 22.0                  # avenue width


def street_w(axis, v):
    return AW if (axis == "x" and v == AVENUE_X) or (axis == "y" and v == AVENUE_Y) else SW


# elevated highways: (axis, coordinate, deck heights); they run above these streets
HIGHWAYS = [("y", 90, (12.0, 22.0)), ("x", 220, (17.0,))]

# ------------------------------------------------------------------ the Cell's network
HQ_BLOCK = (10, -50, 80, 20)        # x0, y0, x1, y1 (street centrelines)
NODES = {
    #  id         x     y     kind              label          setup status   integrity (now, max)
    "core":     (10, -50, "home", "CORE", "home", (50, 50)),
    "relay":    (-60, -50, "relay", "RELAY", "holds", (15, 15)),
    "firewall": (10, 20, "firewall", "FIREWALL RELAY", "holds", (30, 30)),
    "vault":    (80, -50, "vault", "VAULT TERMINAL", "disabled", (20, 20)),
    "proxy":    (-60, 20, "proxy", "PROXY RELAY", "seized", (15, 15)),
    "safe":     (10, -120, "safehouse", "SAFEHOUSE", "holds", (20, 20)),
}
LINKS = [("core", "relay"), ("core", "firewall"), ("core", "vault"), ("core", "safe"),
         ("relay", "proxy"), ("proxy", "firewall")]

# corporate entry Sites (Halcyon Civic) where threats spawn, and the threat routes (street polylines)
CORP = "halcyon"
ENTRIES = {
    "e_east": (150, -50),
    "e_west": (-130, 20),
    "e_south": (80, -190),
}
ROUTES = {
    "r1": ["e_east", "vault", "core"],
    "r2": ["e_west", "proxy", "firewall", "core"],
    "r3": ["e_south", (80, -120), "safe", "core"],
}


def pt(k):
    if isinstance(k, tuple):
        return k
    if k in NODES:
        return NODES[k][0], NODES[k][1]
    return ENTRIES[k]


def route_points(rid):
    return [pt(k) for k in ROUTES[rid]]


def is_intersection_reserved(x, y, pad):
    for n in NODES.values():
        if abs(x - n[0]) < pad and abs(y - n[1]) < pad:
            return True
    return False


if __name__ == "__main__":
    for k, n in NODES.items():
        print(k, [round(v) for v in project(n[0], n[1])])
    for k, e in ENTRIES.items():
        print(k, [round(v) for v in project(*e)])
    for x in (-270, 290):
        for y in (-260, 300):
            print("corner", x, y, [round(v) for v in project(x, y)])


# ------------------------------------------------------------------ round 19: nodes that live in buildings
# The street socket stays the tactical node; the node's MACHINE lives in the corner building behind it
# (north-east of the intersection, its -x / -y faces look onto the pad). design:
#   server = ground-floor server room lit behind glass, riser into the door
#   dish   = rooftop dish, riser up the facade corner
#   shop   = shopfront with the node glyph sign, socket riser to its door
NODE_BUILDINGS = {
    "vault": ("server", 16.0),
    "firewall": ("server", 13.0),
    "relay": ("dish", 24.0),
    "proxy": ("dish", 18.0),
    "safe": ("shop", 11.0),
}
LOT = 18.0          # node building footprint (m)


def node_lot(key):
    x, y = NODES[key][0], NODES[key][1]
    hw = street_w("x", x) / 2 + 3.0
    hh = street_w("y", y) / 2 + 3.0
    return (x + hw, y + hh, x + hw + LOT, y + hh + LOT)


LINK_COLOURS = {"lime": (0.83, 1.0, 0.0), "cyan": (0.36, 0.88, 1.0)}


def riser_paths(key):
    """Three parallel inlay traces from the street socket into the node's building (3D polylines).
    Ground (z 0.02) -> up the curb (0.36) -> across the sidewalk -> up the facade (-y face)."""
    design, h = NODE_BUILDINGS[key]
    x, y = NODES[key][0], NODES[key][1]
    x0, y0, x1, y1 = node_lot(key)
    hw = street_w("x", x) / 2
    hh = street_w("y", y) / 2
    xd = {"server": x0 + 9.0, "dish": x0 + 2.2, "shop": x0 + 5.0}[design]
    ztop = {"server": 0.75, "dish": h, "shop": 0.4}[design]
    out = []
    for off in (-0.9, 0.0, 0.9):
        p = [(x + hw - 1.2 + off, y + hh - 1.2, 0.02),
             (x + hw + 0.4 + off, y + hh + 0.4, 0.02),
             (x + hw + 0.5 + off, y + hh + 0.5, 0.36),
             (xd + off, y0 - 0.9, 0.36),
             (xd + off, y0 - 0.02, 0.36)]
        if ztop > 0.5:
            p.append((xd + off, y0 - 0.02, ztop))
        out.append(p)
    return out


# ------------------------------------------------------------------ round 20: rooftop identity + station slot
# A node building's roof is marked as the node's (variant A crown inlay, B uplink pad, C mast + lit hatch).
# B's pad is also the operative STATION SLOT on a Safehouse (GDD 3.2 / 5.4).
def roof_spec(key, variant):
    """Roof geometry shared by district20.py (models) and the post decals: top z, pad box, mast, hatch."""
    design, h = NODE_BUILDINGS[key]
    x0, y0, x1, y1 = node_lot(key)
    s = dict(top=h, lot=(x0, y0, x1, y1), variant=variant)
    if design == "dish":
        s["pad"] = (x0 + 6.0, y0 + 6.0, 3.6)          # centre x, centre y, half size
        s["dish"] = (x0 + 13.0, y0 + 13.0, 4.5)
    else:
        s["pad"] = (x0 + 8.4, y0 + 8.4, 4.4)
    s["pad_h"] = 0.7
    s["mast"] = (x1 - 3.5, y1 - 3.5)
    s["hatch"] = (x0 + 6.0, y0 + 6.0, 1.6)
    return s


def climb_paths(key, variant):
    """Round 20: three more inlay traces that climb the -x facade from the sidewalk to the roof feature."""
    s = roof_spec(key, variant)
    x0, y0, x1, y1 = s["lot"]
    h = s["top"]
    px, py, hs = s["pad"]
    out = []
    for off in (-0.7, 0.0, 0.7):
        ya = y0 + 2.0 + off
        xs = x0 - 2.2 + off
        p = [(xs, y0 - 2.6, 0.36), (xs, ya, 0.36), (x0 - 0.02, ya, 0.36), (x0 - 0.02, ya, h + 0.9),
             (x0 + 0.45, ya, h + 0.9), (x0 + 0.45, ya, h + 0.03)]
        if variant == "B":
            p.append((px - hs - 0.2, ya, h + 0.03))
        elif variant == "C":
            p.append((s["hatch"][0] - 2.0, ya, h + 0.03))
        else:
            p.append((x0 + 2.2, ya, h + 0.03))
        out.append(p)
    return out


# ------------------------------------------------------------------ round 20: a mixed-corp wave for the vehicle / icon toggle
# (corp, unit index 0 fast / 1 heavy / 2 special, x, y, heading, upgraded, hp fraction)
THREATS_V2 = [
    ("HALCYON", 1, 118, -45, math.pi, False, 0.8),
    ("HALCYON", 0, 96, -54.5, math.pi, True, 1.0),
    ("MERIDIAN", 1, 84, -100, math.pi / 2, True, 0.55),
    ("MERIDIAN", 0, 138, -45.5, math.pi, False, 1.0),
    ("ORBITAL", 2, 154, -96, 0.0, False, 1.0),
    ("SOLACE", 2, 76, -76, math.pi / 2, False, 0.4),
    ("ORBITAL", 0, 146, -72, -math.pi / 2, True, 0.9),
    ("REBEL_CELL", 0, 120, -124, math.pi, True, 1.0),
    ("SOLACE", 0, 56, -45.5, math.pi, False, 0.7),
]
