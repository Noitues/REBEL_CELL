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
