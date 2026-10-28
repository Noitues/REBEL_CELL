"""P1 shared geometry: the Godot raid camera (zoom 1.5 about plate px (722,500)), screen<->world, terrain G, routes from the H2 World.
Godot world (gx,gy,gz), Blender (gx,-gz,gy). Screen px are 1920x1080 frame px."""
import sys, json, numpy as np
H2 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts'
WORK = 'D:/rc_scratch/tide_concepts/p3_work/'
OUT = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/'
import os
S = int(os.environ.get('P2_S', '1'))            # 1 = 1920x1080 plates, 2 = native 3840x2160 (true-2x crops)
WB = WORK if S == 1 else WORK + 's2/'           # per-beat Blender layers / specs
os.makedirs(WB, exist_ok=True)
CAMJ = json.load(open(WORK + 'depth15/capture.json'))['camera']
O = np.array(CAMJ['position'], float)
SIZE = CAMJ['size']                      # ortho WIDTH in BU
RIGHT = np.array([0.707107, 0.0, -0.707107])
UP = np.array([-0.454519, 0.766044, -0.454519])
BACK = np.array([0.541675, 0.642788, 0.541675])
FWD = -BACK
W, H = 1920, 1080
BU_PX = SIZE / W                          # BU per pixel (0.2055)
_hf = None


def hf():
    global _hf
    if _hf is None:
        z = np.load(WORK + 'hf15.npz')
        _hf = {k: z[k] for k in z.files}
    return _hf


def ray_origin(px):
    u = px[0] / W - .5
    v = .5 - px[1] / H
    return O + RIGHT * u * SIZE + UP * v * SIZE * H / W


def to_screen(p):
    """Godot world (N,3) -> screen px (N,2)."""
    p = np.asarray(p, float).reshape(-1, 3)
    d = p - O
    sx = (d @ RIGHT) / SIZE + .5
    sy = .5 - (d @ UP) / (SIZE * H / W)
    return np.stack([sx * W, sy * H], -1)


def ground(x, z):
    """terrain Y at Godot (x,z) (bilinear on G)."""
    h = hf(); G = h['G']; c = float(h['cell'])
    fx = (np.asarray(x, float) - float(h['x0'])) / c
    fz = (np.asarray(z, float) - float(h['z0'])) / c
    fx = np.clip(fx, 0, G.shape[1] - 1.001); fz = np.clip(fz, 0, G.shape[0] - 1.001)
    ix = fx.astype(int); iz = fz.astype(int)
    ax = fx - ix; az = fz - iz
    return (G[iz, ix] * (1 - ax) * (1 - az) + G[iz, ix + 1] * ax * (1 - az) + G[iz + 1, ix] * (1 - ax) * az + G[iz + 1, ix + 1] * ax * az)


def roof(x, z):
    h = hf(); Hh = h['H']; c = float(h['cell'])
    ix = np.clip(((np.asarray(x, float) - float(h['x0'])) / c).astype(int), 0, Hh.shape[1] - 1)
    iz = np.clip(((np.asarray(z, float) - float(h['z0'])) / c).astype(int), 0, Hh.shape[0] - 1)
    return Hh[iz, ix]


def screen_to_ground(px, lift=0.0, iters=6):
    """screen px (N,2) -> Godot world on the terrain (+lift)."""
    px = np.asarray(px, float).reshape(-1, 2)
    out = np.zeros((len(px), 3))
    for i, q in enumerate(px):
        o = ray_origin(q)
        y = 0.0
        for _ in range(iters):
            t = (y - o[1]) / FWD[1]
            p = o + FWD * t
            y = float(ground(p[0], p[2])) + lift
        t = (y - o[1]) / FWD[1]
        out[i] = o + FWD * t
    return out


def g2b(p):
    """Godot (N,3) -> Blender (N,3)."""
    p = np.asarray(p, float).reshape(-1, 3)
    return np.stack([p[:, 0], -p[:, 2], p[:, 1]], -1)


def load_world(scn='default'):
    """H2 World (routes in 1.5x-zoom screen px)."""
    if H2 not in sys.path:
        sys.path.insert(0, H2)
    import common
    common.LANE_K = 21.0          # P1: wider lanes so D / N / E bodies sit side by side on a shared street
    return common.World(scn)
