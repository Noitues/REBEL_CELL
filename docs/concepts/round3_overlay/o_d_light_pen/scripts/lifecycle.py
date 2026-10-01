"""04_lifecycle.png - the SEND IT verb: written in light -> idle pulse -> dissolves to particles."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from lightpen import *
from combat import edit_base, mark_send_it, SRC, SIZE

CROP = (1440, 668, 1920, 1080)  # x0, y0, x1, y1 around the EXECUTE button
PW = 600


def frame_write(base, frac=0.58):
    st, t_total = mark_send_it(np.random.default_rng(101))
    t_end = t_total * frac

    def pulse(s_, idx, n):  # the freshly drawn segment is still hot
        T = s_.T
        return np.where(T <= t_end, 1.1 * np.exp(-(t_end - T) / 0.06), 0.0)
    m = Masks(SIZE)
    head = raster(m, st, np.random.default_rng(1), t_end=t_end, pulse=pulse)
    out = compose(base, [dict(masks=m, color=PINK, trail=(-9, 4), light=1.3, veil=0.4, halo=1.3)])
    if head is not None:
        lin = np.zeros_like(out)
        pen_head(lin, head[0], head[1], scale=2.2)
        out = tonemap(out + lin)
    return out


def frame_idle(base):
    st, t_total = mark_send_it(np.random.default_rng(101))
    tp = t_total * 0.42  # where the travelling highlight is in this frame

    def pulse(s_, idx, n):
        return 1.8 * np.exp(-((s_.T - tp) / 0.09) ** 2)
    m = Masks(SIZE)
    raster(m, st, np.random.default_rng(1), pulse=pulse, flicker=0.35, sparks=False)
    # breathing: this frame sits at the low point of the pulse (slightly dimmer, softer halo)
    return compose(base, [dict(masks=m, color=PINK, trail=(-6, 3), light=1.4, veil=0.45, halo=1.5,
                               gain=0.92)])


def frame_leave(base, progress=0.55):
    st, _ = mark_send_it(np.random.default_rng(101))
    m = Masks(SIZE)
    raster(m, st, np.random.default_rng(1), sparks=False)
    parts = Masks(SIZE)
    keep = dissolve_particles(m, np.random.default_rng(9), progress, drift=(40, -80), n=2600,
                              into=parts, sweep=(1530, 1900))
    _, _, _, sp = parts.arrays()
    dim = base * 0.72  # the page is already transitioning out
    return compose(dim, [dict(masks=m, color=PINK, trail=(-5, 3), light=0.7 * (1 - progress) + 0.15,
                              veil=0.3, halo=1.1, keep=keep, extra_spark=sp * 0.7)])


def crop_scale(img):
    x0, y0, x1, y1 = CROP
    c = Image.fromarray((np.clip(img[y0:y1, x0:x1], 0, 1) * 255).astype(np.uint8))
    h = int(round((y1 - y0) * PW / (x1 - x0)))
    return c.resize((PW, h), Image.LANCZOS)


def render(out_path):
    base = edit_base(load(SRC))
    panels = [
        ("01", "WRITTEN IN LIGHT", ["Pen head leads; the fresh stroke is white-hot.",
                                    "Slow in corners = thick, fast runs = thin.",
                                    "0.0 - 0.7 s, sparks where the pen lifts."], frame_write(base)),
        ("02", "IDLE: PULSE + FLICKER", ["A highlight runs the stroke path every 2.4 s;",
                                         "the glow breathes +/-10%, faint flicker.",
                                         "The light on the button breathes with it."], frame_idle(base)),
        ("03", "LEAVING: DISSOLVE", ["Stroke breaks up from noise into light motes",
                                     "that drift up and fade with the page.",
                                     "0.45 s, base dims under it."], frame_leave(base)),
    ]
    W, H = 1920, 1080
    canvas = Image.new("RGB", (W, H), (11, 12, 17))
    d = ImageDraw.Draw(canvas)
    d.text((60, 58), "SEND IT  /  LIFECYCLE", font=font(44, "Bold Condensed"), fill=(236, 230, 240))
    d.text((60, 112), "AR light-pen overlay over the washed-out EXECUTE button (Cv2 base, unchanged)",
           font=font(22, "SemiLight Condensed"), fill=(150, 150, 166))
    gap = (W - 3 * PW) // 4
    for i, (num, name, cap, img) in enumerate(panels):
        x = gap + i * (PW + gap)
        y = 200
        p = crop_scale(img)
        canvas.paste(p, (x, y))
        d.rectangle([x - 1, y - 1, x + PW, y + p.size[1]], outline=(48, 50, 62))
        ty = y + p.size[1] + 26
        d.text((x, ty), num, font=font(40, "Bold Condensed"), fill=(255, 64, 170))
        d.text((x + 56, ty + 6), name, font=font(30, "Bold Condensed"), fill=(232, 228, 238))
        for k, line in enumerate(cap):
            d.text((x, ty + 60 + k * 30), line, font=font(23, "SemiLight Condensed"), fill=(160, 160, 176))
    canvas.save(out_path)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR + "04_lifecycle.png")
