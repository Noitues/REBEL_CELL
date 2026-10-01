"""01_combat.png - light-pen overlay on the Cv2 combat still."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from lightpen import *
from holo import holo_card

SRC = BASE_DIR + "round2/r2c_geo_vector_gritty/stills/04_combat.png"
SIZE = (1920, 1080)
BTN = (1760, 890)  # centre of the old GO button


def edit_base(img):
    """Remove old overlay bits (tape) and turn GO into a washed-out digital EXECUTE."""
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    # tape strip near ROUND 3
    lum = img.mean(-1)
    tape = ((xx > 805) & (xx < 895) & (yy > 10) & (yy < 50) & (lum > 0.45)).astype(np.float32)
    img = inpaint(img, dilate(tape, 2.0), 300)
    # GO + SPIN BOTH WHEELS text
    lum = img.mean(-1)
    r = np.hypot(xx - BTN[0], yy - (BTN[1] - 5))
    txt = ((r < 105) & (lum < 0.22) & (yy > 850) & (yy < 955) & (xx > 1680) & (xx < 1840)).astype(np.float32)
    img = inpaint(img, dilate(txt, 1.5), 500)
    # wash out the button: desaturate + darken inside the button disc (incl. its dashed ring)
    r2 = np.hypot(xx - BTN[0], yy - BTN[1])
    disc = np.clip((150 - r2) / 14.0, 0, 1)[..., None]
    gray = img.mean(-1, keepdims=True)
    washed = gray * np.array([0.52, 0.5, 0.56]) * 0.9 + 0.02
    img = img * (1 - disc) + washed * disc
    # the dim system word
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((BTN[0], BTN[1] - 14), "EXECUTE", font=font(54, "Bold Condensed"),
           fill=(200, 200, 210, 120), anchor="mm")
    d.text((BTN[0], BTN[1] + 24), "SPIN BOTH WHEELS", font=font(19, "SemiBold Condensed"),
           fill=(190, 190, 200, 70), anchor="mm")
    img = over(img, layer)
    return img


def mark_send_it(rng):
    paths = write("SEND IT", 1534, 850, 84, rng, slant=0.3, rot_deg=-8, track=0.06)
    # fast underline swash, thin -> thick where it brakes
    paths.append(curve([(1556, 990), (1650, 978), (1770, 950), (1866, 918)]))
    return build(paths, 84, 14, 36, rng, px_speed=900)


def mark_target(rng):
    paths = [loop(1236, 382, 66, 58, rng, turns=1.2, start_deg=-150, tilt_deg=-10)]
    paths += write("HIT IT", 930, 186, 60, rng, slant=0.28, rot_deg=-6)
    paths += arrow([(1052, 262), (1100, 292), (1150, 318), (1177, 340)], head=22, rng=rng)
    return build(paths, 60, 6, 20, rng)


def mark_note(rng):
    paths = write("ICE IS SLOW\nBAIT THE 9 -\nTHEN BACKDOOR", 850, 505, 23, rng, slant=0.22,
                  rot_deg=-3, jit=0.03, flick=0.04)
    return build(paths, 23, 1.8, 5.5, rng)


def mark_crew(rng, x, y, w, h):
    paths = brackets(x, y, w, h, rng, arm=0.2, over=12)
    paths += write("KIRA", x + 52, y + h + 14, 34, rng, slant=0.3, rot_deg=-4)
    return build(paths, 40, 4, 13, rng)


def render(out_path):
    base = edit_base(load(SRC))
    groups = []
    m = Masks(SIZE)
    st, _ = mark_send_it(np.random.default_rng(101))
    raster(m, st, np.random.default_rng(1))
    groups.append(dict(masks=m, color=PINK, trail=(-6, 3), light=1.6, veil=0.45, halo=1.3))
    m = Masks(SIZE)
    st, _ = mark_target(np.random.default_rng(202))
    raster(m, st, np.random.default_rng(2))
    groups.append(dict(masks=m, color=PINK, trail=(-4, 2), light=0.8, veil=0.25))
    m = Masks(SIZE)
    st, _ = mark_note(np.random.default_rng(303))
    raster(m, st, np.random.default_rng(3), spark_n=(0, 1), dry=0.4)
    groups.append(dict(masks=m, color=np.array([0.82, 0.86, 1.0], np.float32), halo=0.6,
                       light=0.25, veil=0.5))
    cx, cy, cw, ch = 46, 478, 228, 262
    m = Masks(SIZE)
    st, _ = mark_crew(np.random.default_rng(404), cx, cy, cw, ch)
    raster(m, st, np.random.default_rng(4), spark_n=(1, 3))
    groups.append(dict(masks=m, color=PINK, trail=(-3, 2), light=0.6, veil=0.3))
    hadd, hveil = holo_card(base.shape[:2], cx, cy, cw, ch, np.random.default_rng(505))
    out = compose(base, groups, extra_add=hadd, extra_veil=hveil)
    save(out, out_path)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR + "01_combat.png")
