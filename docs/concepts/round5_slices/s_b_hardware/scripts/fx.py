"""Pillow/numpy: each program's shader behaviour, applied to the rendered tile the way a
Godot canvas_item shader would (UV offsets, additive masks, time uniform).

python fx.py -> shader_fx.gif, shader_fx_strip.png (reads WORK/sheet.png + atlas cells)
Every effect is a pure function of (tile pixels, tile-local coords, masks, t in [0,1)).
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import common as C
import compose
import ui

FRAMES = 36
FRAME_MS = 70


def crop_box(hx, hy):
    x0, y1 = compose.w2p(hx - 1.2, hy + 3.68)
    x1, y0 = compose.w2p(hx + 1.2, hy + 1.18)
    return int(x0), int(y1), int(x1), int(y0)


class Tile:
    def __init__(self, sheet, typ, ticks, value, hx, hy):
        self.typ, self.ticks, self.value = typ, ticks, value
        box = crop_box(hx, hy)
        self.img = np.array(sheet.crop(box)).astype(np.float32)
        h, w = self.img.shape[:2]
        self.h, self.w = h, w
        jj, ii = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = compose.w2p(hx, hy)
        self.x = (ii + box[0] - cx) / C.PPU
        self.y = (cy - (jj + box[1])) / C.PPU
        self.ii, self.jj = ii, jj
        self.alpha = self.img[..., 3] / 255.0
        ax, ay = compose.w2p(hx, hy + C.R_ANCHOR)
        self.ax, self.ay = ax - box[0], ay - box[1]
        pl = ui.plate((w, h), self.ax, self.ay, ui.chord_px(ticks, C.PPU) * 0.34 * 1.6,
                      ui.chord_px(ticks, C.PPU) * 0.34 * 2.6, 0, compose.PLATE[typ])
        self.plate = np.array(pl).astype(np.float32) / 255.0
        _, _, kind = C.PROGRAMS[typ]
        self.label = ui.label(kind, value, ui.chord_px(ticks, C.PPU))

    def cell(self, name):
        im = np.array(Image.open(os.path.join(C.WORK, name)).convert("RGB")).astype(np.float32) / 255.0
        u = ((self.x - C.TEX_X0) / C.TEX_SIZE * C.TEX_PX).clip(0, C.TEX_PX - 1).astype(int)
        v = ((C.TEX_Y0 + C.TEX_SIZE - self.y) / C.TEX_SIZE * C.TEX_PX).clip(0, C.TEX_PX - 1).astype(int)
        return im[v, u]

    def sample(self, dx, dy):
        """Displaced lookup (pixels), bilinear-ish via nearest on a 2x grid."""
        si = (self.ii + dx).clip(0, self.w - 1)
        sj = (self.jj + dy).clip(0, self.h - 1)
        i0, j0 = np.floor(si).astype(int), np.floor(sj).astype(int)
        i1, j1 = (i0 + 1).clip(0, self.w - 1), (j0 + 1).clip(0, self.h - 1)
        fi, fj = (si - i0)[..., None], (sj - j0)[..., None]
        a = self.img
        return (a[j0, i0] * (1 - fi) * (1 - fj) + a[j0, i1] * fi * (1 - fj) +
                a[j1, i0] * (1 - fi) * fj + a[j1, i1] * fi * fj)


def add(rgb, mask, color, k=1.0):
    return rgb + mask[..., None] * np.array(color, np.float32)[None, None, :] * k


def blur(m, r):
    im = Image.fromarray((m.clip(0, 1) * 255).astype(np.uint8))
    return np.array(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0


def pulse(t, centre, width):
    d = ((t - centre + 0.5) % 1.0) - 0.5
    return math.exp(-(d / width) ** 2)


# ---------------------------------------------------------------- per-program behaviours
def fx_exploit(T, t):
    """Specular glint sweep: a bright diagonal band crosses, scratches catch it harder."""
    if not hasattr(T, "scr"):
        T.scr = T.cell("exploit_scratch.png")[..., 0]
    out = T.img.copy()
    s = T.x * 0.55 + T.y * 0.835
    c = -0.2 + (t / 0.55) * 4.4 if t < 0.55 else 99
    band = np.exp(-((s - c) / 0.16) ** 2)
    m = band * (0.45 + 1.6 * T.scr) * T.alpha
    out[..., :3] = add(out[..., :3], m, (255, 225, 240), 0.9)
    return out


def fx_zeroday(T, t):
    """Refraction shimmer (UV wobble) + cracks flash."""
    if not hasattr(T, "crk"):
        T.crk = T.cell("zeroday_cracks.png")[..., 0] * T.alpha
        T.crk_glow = blur(T.crk, 3)
    ph = 2 * math.pi * t
    dx = 1.6 * np.sin(T.y * 9.0 + ph * 2) * np.sin(T.x * 5.0 - ph)
    dy = 1.6 * np.cos(T.x * 8.0 - ph * 2)
    out = T.sample(dx, dy)
    f = max(pulse(t, 0.18, 0.03), 0.7 * pulse(t, 0.26, 0.025), pulse(t, 0.66, 0.035))
    out[..., :3] = add(out[..., :3], T.crk, (255, 235, 250), 1.6 * f)
    out[..., :3] = add(out[..., :3], T.crk_glow, (255, 120, 210), 2.2 * f)
    return out


def fx_firewall(T, t):
    """Heat haze rising: horizontal UV ripple that grows toward the rim and travels outward."""
    k = ((T.y - C.R_IN) / (C.R_OUT - C.R_IN)).clip(0, 1)
    ph = 2 * math.pi * t
    dx = 2.4 * k * np.sin(T.y * 10.0 - ph * 3) + 0.8 * k * np.sin(T.y * 23.0 - ph * 5)
    dy = 0.8 * k * np.sin(T.x * 7.0 - ph * 2)
    out = T.sample(dx, dy)
    shimmer = (0.5 + 0.5 * np.sin(T.y * 6.0 - ph * 3)) ** 6 * k * T.alpha
    out[..., :3] = add(out[..., :3], shimmer, (140, 235, 255), 0.35)
    return out


def fx_sandbox(T, t):
    """Soft inner pulse: the caged cube brightens and its glow spreads through the frost."""
    cx, cy, _ = C.CUBE
    d = np.hypot(T.x - cx, T.y - cy)
    p = (0.5 - 0.5 * math.cos(2 * math.pi * t)) ** 1.5
    g = np.exp(-(d / (0.35 + 0.35 * p)) ** 2) * T.alpha
    out = T.img.copy()
    out[..., :3] = out[..., :3] * (1 + 0.18 * p * T.alpha[..., None])
    out[..., :3] = add(out[..., :3], g, (110, 255, 235), 0.85 * p)
    return out


def fx_proxy(T, t):
    """Reflection slides along the mirror band as if rerouted; tiles light in sequence."""
    if not hasattr(T, "mir"):
        size, ang, pts = C.mirror_tiles()
        ca, sa = math.cos(ang), math.sin(ang)
        m = np.zeros_like(T.x)
        for (px_, py_) in pts:
            if not C.inside(T.ticks, px_, py_, size * 0.75):
                continue
            lx = (T.x - px_) * ca + (T.y - py_) * sa
            ly = -(T.x - px_) * sa + (T.y - py_) * ca
            m = np.maximum(m, ((np.abs(lx) < size / 2) & (np.abs(ly) < size / 2)).astype(np.float32))
        T.mir = m
        T.along = (T.x * ca + (T.y - 2.45) * sa)
    c = -1.6 + 3.2 * t
    band = np.exp(-((T.along - c) / 0.18) ** 2)
    ghost = np.exp(-((T.along - c + 0.55) / 0.12) ** 2) * 0.4
    out = T.img.copy()
    out[..., :3] = add(out[..., :3], T.mir * (band + ghost), (225, 255, 225), 1.1)
    return out


def fx_patch(T, t):
    """Cooling glow: the solder blob flashes white-hot, cools through orange to settled metal."""
    sx, sy, sr = C.SOLDER
    d = np.hypot(T.x - sx, T.y - sy)
    heat = math.exp(-t / 0.22) if t < 0.85 else 0.0
    core = np.exp(-(d / (sr * 0.95)) ** 2)
    halo = np.exp(-(d / (sr * 2.6)) ** 2)
    col = np.array([255, 245, 220]) * heat + np.array([255, 120, 30]) * (1 - heat)
    k = heat ** 0.6 if t < 0.85 else 0.0
    out = T.img.copy()
    out[..., :3] = add(out[..., :3], core, col, 1.4 * k)
    out[..., :3] = add(out[..., :3], halo, (255, 150, 60), 0.7 * k)
    # the fresh trace wakes up behind the cooling joint
    if not hasattr(T, "trc"):
        T.trc = T.cell("patch_pcb.png")[..., 0] * T.alpha
    wave = np.exp(-((d - (0.2 + 2.2 * t)) / 0.25) ** 2) * T.trc
    out[..., :3] = add(out[..., :3], wave, (150, 255, 150), 0.6 * (1 - t))
    return out


def fx_virus(T, t):
    """Pustules throb: each swells (UV pinch toward its centre) out of phase, glow follows."""
    dx = np.zeros_like(T.x)
    dy = np.zeros_like(T.x)
    glow = np.zeros_like(T.x)
    for k, (px_, py_, r) in enumerate(C.pustules()):
        if not C.inside(T.ticks, px_, py_, r * 1.05):
            continue
        s = 0.5 - 0.5 * math.cos(2 * math.pi * (t * 2 + k * 0.37))
        d = np.hypot(T.x - px_, T.y - py_)
        f = np.clip(1 - d / (r * 1.7), 0, 1) ** 2 * 0.32 * s
        dx += -(T.x - px_) * C.PPU * f
        dy += (T.y - py_) * C.PPU * f
        glow += np.exp(-(d / (r * 1.1)) ** 2) * s
    out = T.sample(dx, dy)
    out[..., :3] = add(out[..., :3], glow * T.alpha, (215, 110, 255), 0.55)
    return out


def fx_trojan(T, t):
    """The panel cracks open along the seam; light leaks out, then it seals again."""
    if t < 0.25:
        o = 0.0
    elif t < 0.5:
        o = (t - 0.25) / 0.25
    elif t < 0.8:
        o = 1.0 + 0.12 * math.sin((t - 0.5) * 60)
    else:
        o = max(0.0, 1 - (t - 0.8) / 0.15)
    w = 8.0 * o
    panel = ((T.y > C.RIBBON_Y[1] + 0.05) & (T.y < C.R_OUT - 0.22)).astype(np.float32)
    side = np.sign(T.x - C.SEAM_X)
    dx = -side * w * panel
    out = T.sample(dx, np.zeros_like(dx))
    gap = (np.abs(T.x - C.SEAM_X) * C.PPU < w) * panel * T.alpha
    if not hasattr(T, "grv"):
        T.grv = T.cell("trojan_panel.png")[..., 0] * T.alpha
    leak = blur(gap.astype(np.float32), 12) * 2.4 + blur(T.grv, 2) * 1.5 * o
    out[..., :3] = out[..., :3] * (1 - gap[..., None]) + gap[..., None] * np.array([255, 245, 255])
    out[..., :3] = add(out[..., :3], leak * T.alpha, (210, 170, 255), 1.1 * o)
    return out


def fx_null(T, t):
    """Dull: nothing happens."""
    return T.img.copy()


FX = {"ATTACK": fx_exploit, "CRITICAL": fx_zeroday, "DEFEND": fx_firewall, "SHIELD": fx_sandbox,
      "EVADE": fx_proxy, "HEAL": fx_patch, "AFFLICT": fx_virus, "DEPLOY": fx_trojan, "MISS": fx_null}
FX_NOTE = {"ATTACK": "glint sweep", "CRITICAL": "shimmer + crack flash", "DEFEND": "heat haze",
           "SHIELD": "inner pulse", "EVADE": "reflection reroute", "HEAL": "solder cools",
           "AFFLICT": "pustules throb", "DEPLOY": "panel cracks, light leaks", "MISS": "nothing (dead)"}


def frame(T, t):
    a = FX[T.typ](T, t)
    a[..., :3] *= (1 - (T.plate * T.alpha)[..., None])
    a[..., 3] = T.img[..., 3]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    ui.place(im, T.label, T.ax, T.ay, 0)
    return im


def main():
    sheet = Image.open(os.path.join(C.WORK, "sheet.png")).convert("RGBA")
    tiles = [Tile(sheet, *row) for row in C.SHEET[:9]]
    cw, chh = tiles[0].w, tiles[0].h
    cols, rows = 3, 3
    pad, cap = 16, 54
    W = cols * (cw + pad) + pad
    H = rows * (chh + cap + pad) + pad + 50
    bg = ui.background(W, H, (120, 90, 200), seed=11)
    ui.text(bg, (pad, 12), "SHADER BEHAVIOURS  (loop, %d frames)" % FRAMES, 28, path=C.FONT_NUM)
    frames = []
    strip_times = [0.0, 0.17, 0.33, 0.5, 0.67, 0.83]
    strip_cells = {T.typ: [] for T in tiles}
    for f in range(FRAMES):
        t = f / FRAMES
        img = bg.copy()
        for k, T in enumerate(tiles):
            cx = pad + (k % cols) * (cw + pad)
            cy = 50 + pad + (k // cols) * (chh + cap + pad)
            fr = frame(T, t)
            g = ui.bloom(fr, thresh=215, radius=6, gain=0.6)
            sub = img.crop((cx, cy, cx + cw, cy + chh))
            sub.alpha_composite(fr)
            sub = ui.add_glow(sub, g)
            img.paste(sub, (cx, cy))
            name, hexc, _ = C.PROGRAMS[T.typ]
            col = tuple(int(c * 255) for c in C.hexrgb(hexc)) + (255,)
            ui.text(img, (cx + cw // 2, cy + chh + 4), name, 24, fill=col, path=C.FONT_NUM, anchor="ma")
            ui.text(img, (cx + cw // 2, cy + chh + 34), FX_NOTE[T.typ], 14, fill=(185, 180, 200, 255),
                    path=C.FONT_MONO, anchor="ma")
        frames.append(img.convert("RGB"))
    # strip: rows = programs, columns = time samples
    sc = 0.62
    tw, th = int(cw * sc), int(chh * sc)
    SW = 230 + len(strip_times) * (tw + 10) + 10
    SH = 60 + len(tiles) * (th + 12) + 10
    strip = ui.background(SW, SH, (120, 90, 200), seed=12)
    ui.text(strip, (16, 14), "SHADER FX STRIP  t = " + "  ".join("%.2f" % s for s in strip_times), 26,
            path=C.FONT_NUM)
    for r, T in enumerate(tiles):
        y = 60 + r * (th + 12)
        name, hexc, _ = C.PROGRAMS[T.typ]
        col = tuple(int(c * 255) for c in C.hexrgb(hexc)) + (255,)
        ui.text(strip, (16, y + th // 2 - 16), name, 28, fill=col, path=C.FONT_NUM)
        ui.text(strip, (16, y + th // 2 + 18), FX_NOTE[T.typ], 14, fill=(185, 180, 200, 255), path=C.FONT_MONO)
        for c, st in enumerate(strip_times):
            fr = frame(T, st)
            g = ui.bloom(fr, thresh=215, radius=6, gain=0.6)
            x = 230 + c * (tw + 10)
            cell = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            cell.alpha_composite(fr)
            cell = cell.resize((tw, th), Image.LANCZOS)
            gl = g.resize((tw, th), Image.LANCZOS)
            base = strip.crop((x, y, x + tw, y + th))
            base.alpha_composite(cell)
            base = ui.add_glow(base, gl)
            strip.paste(base, (x, y))
    strip.convert("RGB").save(os.path.join(C.OUT, "shader_fx_strip.png"))
    # GIF with one shared palette
    mosaic = Image.new("RGB", (W, H * 4))
    for k in range(4):
        mosaic.paste(frames[k * FRAMES // 4], (0, H * k))
    pal = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = os.path.join(C.OUT, "shader_fx.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=FRAME_MS, loop=0, optimize=True)
    print("fx ->", path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
