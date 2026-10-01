"""02_city.png - light-pen overlay on the Cv2 night city map."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lightpen import *

SRC = BASE_DIR + "round2/r2c_geo_vector_gritty/stills/02_city_night.png"
SIZE = (1920, 1080)


def mark_target(rng):
    paths = [loop(1293, 590, 46, 62, rng, turns=1.22, start_deg=-60, tilt_deg=12)]
    paths += write("HIT THIS", 1330, 452, 50, rng, slant=0.3, rot_deg=-7)
    return build(paths, 50, 7, 21, rng)


def mark_home(rng):
    paths = [loop(705, 598, 40, 40, rng, turns=1.15, start_deg=150, tilt_deg=0)]
    paths += write("OURS", 560, 668, 40, rng, slant=0.28, rot_deg=-5)
    return build(paths, 40, 3.5, 13, rng)


def mark_route(rng):
    # planned path along the streets, home -> target, one fast gesture with a braking head
    pts = [(742, 640), (800, 700), (900, 735), (1010, 742), (1110, 718), (1200, 676), (1252, 638)]
    paths = arrow(pts, head=30, rng=rng, spread=30)
    return build(paths, 60, 3, 16, rng, end_speed=0.15)


def mark_threat(rng):
    paths = write("THEM", 1660, 548, 46, rng, slant=0.3, rot_deg=6)
    # jagged warning strike under the word and two hatch ticks at the boss
    paths.append(polyline([(1652, 616), (1690, 606, C), (1712, 622, C), (1748, 604, C), (1772, 620, C),
                           (1806, 604)]))
    paths += arrow([(1688, 628), (1660, 640), (1632, 652)], head=18, rng=rng)
    return build(paths, 46, 4, 15, rng)


def mark_heat(rng):
    cx, cy, R = 1716, 178, 84
    paths = []
    # flame glyph to the left of the ring
    fx, fy = 1556, 192
    paths.append(curve([(fx + 4, fy + 62), (fx - 30, fy + 34), (fx - 30, fy - 8), (fx - 10, fy - 44),
                        (fx + 6, fy - 84), (fx + 22, fy - 44), (fx + 40, fy - 14), (fx + 40, fy + 30),
                        (fx + 16, fy + 60), (fx - 2, fy + 62)]))
    paths.append(curve([(fx + 6, fy + 50), (fx - 8, fy + 26), (fx + 4, fy - 6), (fx + 10, fy - 26),
                        (fx + 22, fy + 8), (fx + 22, fy + 36), (fx + 10, fy + 50)]))
    # the outer ring, hand-drawn
    paths.append(loop(cx, cy, R + 14, R + 14, rng, turns=1.06, start_deg=-100, tilt_deg=0, wob=0.015))
    # the 62% counter: ticks round the ring, bright up to 62
    ticks_on, ticks_off = [], []
    nt = 34
    for i in range(nt):
        a = -math.pi / 2 + 2 * math.pi * i / nt
        r0, r1 = R - 12, R + 2
        p0 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        p1 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        (ticks_on if i / nt < 0.62 else ticks_off).append(curve([p0, p1]))
    paths += ticks_on
    paths += write("62", cx - 46, cy - 40, 74, rng, slant=0.22, track=0.06, rot_deg=-4)
    paths += write("FLAGGED", 1586, 300, 40, rng, slant=0.3, rot_deg=-4)
    paths.append(curve([(1584, 356), (1700, 352), (1846, 340)]))
    st, t = build(paths, 60, 3.5, 15, rng)
    st_off, _ = build(ticks_off, 30, 1.2, 3, rng, t0=t)
    hd, _ = build(write("HEAT", cx - 24, cy + 42, 18, rng, slant=0.2), 18, 1.3, 3.5, rng, t0=t)
    return st, st_off + hd


def render(out_path):
    base = load(SRC)
    groups = []
    for seed, fn, col, kw in ((11, mark_target, PINK, dict(trail=(-5, 3), light=1.2, veil=0.58)),
                              (12, mark_home, CYAN, dict(trail=(-3, 2), light=0.6, veil=0.4, halo=0.8)),
                              (13, mark_route, PINK, dict(trail=(-4, 3), light=0.9, veil=0.2)),
                              (14, mark_threat, PINK, dict(trail=(4, 3), light=1.0, veil=0.55))):
        m = Masks(SIZE)
        st, _ = fn(np.random.default_rng(seed))
        raster(m, st, np.random.default_rng(seed + 100))
        groups.append(dict(masks=m, color=col, **kw))
    m = Masks(SIZE)
    st, st_dim = mark_heat(np.random.default_rng(15))
    raster(m, st, np.random.default_rng(115))
    groups.append(dict(masks=m, color=PINK, trail=(-4, 3), light=1.1, veil=0.5, halo=1.1))
    m = Masks(SIZE)
    raster(m, st_dim, np.random.default_rng(116), sparks=False, streaks=False, body_level=0.5,
           core_gain=0.5)
    groups.append(dict(masks=m, color=np.array([0.85, 0.8, 0.95], np.float32), halo=0.5, light=0.1,
                       veil=0.3))
    out = compose(base, groups)
    save(out, out_path)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR + "02_city.png")
