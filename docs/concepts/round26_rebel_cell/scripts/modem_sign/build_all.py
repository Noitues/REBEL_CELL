"""Render every round4_modem_sign deliverable:
sign_sheet.png, sign_rgba.png + sign_anchor.json, shop_with_sign.png, warmup_strip.png."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import modem_sign as ms
from modem_sign import (Sign, LIT, WARMUP, CW, CH, PW, PH, MARGIN, SHOP_PLATE_XY, OUT, ROOT,
                        to_img, font, gblur, tonemap)

SHOP = os.path.join(ROOT, "round2", "r2c_v2_modem", "modem_shop.png")


def spill_full(emis_canvas, origin, size):
    """Paste canvas emission into a full frame and build the soft light-spill map (HDR)."""
    W, H = size
    E = np.zeros((H, W, 3), np.float32)
    ox, oy = origin
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(W, ox + emis_canvas.shape[1]), min(H, oy + emis_canvas.shape[0])
    E[y0:y1, x0:x1] = emis_canvas[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    L = np.stack([gblur(E[..., c], 26) * 1.1 + gblur(E[..., c], 90) * 1.5 + gblur(E[..., c], 260) * 1.6
                  for c in range(3)], -1)
    return E, L


def place(full, arr, origin):
    H, W = full.shape[:2]
    ox, oy = origin
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(W, ox + arr.shape[1]), min(H, oy + arr.shape[0])
    out = np.zeros(full.shape[:2] + arr.shape[2:], np.float32)
    out[y0:y1, x0:x1] = arr[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    return out


def composite_on(base, r, origin, spill_gain=1.0):
    """base HxWx3 (0..1). Plate replaces what's under it; the spill lights the rest."""
    H, W = base.shape[:2]
    E, L = spill_full(r["emis"], origin, (W, H))
    lit = base * (1.0 + L * 2.3 * spill_gain) + L * 0.05 * spill_gain
    a = place(base, r["alpha"], origin)[..., None]
    plate = place(base, r["plate_rgb"], origin)
    glow = place(base, r["glow"], origin)
    # soft contact shadow so the plate sits on the wall
    sh = np.clip(gblur(a[..., 0], 10), 0, 1)[..., None] * 0.45
    lit = lit * (1 - sh)
    out = lit * (1 - a) + plate * a + glow
    return tonemap(out)


def facet_wall(W, H, rng, cell=64, tint=(0.11, 0.09, 0.13)):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    nx, ny = W // cell + 3, H // cell + 3
    pts = np.zeros((ny, nx, 2))
    for j in range(ny):
        for i in range(nx):
            pts[j, i] = ((i - 1) * cell + rng.uniform(-0.42, 0.42) * cell,
                         (j - 1) * cell + rng.uniform(-0.42, 0.42) * cell)
    t = np.array(tint)
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, e = pts[j, i], pts[j, i + 1], pts[j + 1, i], pts[j + 1, i + 1]
            for tri in ((a, b, c), (b, e, c)):
                col = t * rng.uniform(0.6, 1.4)
                d.polygon([tuple(p) for p in tri], fill=tuple(int(255 * v) for v in col))
    return np.asarray(im, np.float32) / 255.0


def lvls(state):
    return {k: (("f", v[1]) if isinstance(v, tuple) else v) for k, v in state.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    sign = Sign(seed=7)
    origin = (SHOP_PLATE_XY[0] - MARGIN, SHOP_PLATE_XY[1] - MARGIN)

    # ---------------------------------------------------------- shop_with_sign.png
    base = np.asarray(Image.open(SHOP).convert("RGB"), np.float32) / 255.0
    lit = sign.render(LIT, pulse_t=0.37)
    shop = composite_on(base, lit, origin, spill_gain=1.3)
    to_img(shop).save(os.path.join(OUT, "shop_with_sign.png"))
    print("shop_with_sign", flush=True)

    # ---------------------------------------------------------- sign_rgba.png + anchor
    static = sign.render(LIT, pulse_t=None)  # reduce-effects: static lit state, no pulses
    glow_tm = tonemap(static["glow"])
    pm = static["alpha"]
    ga = np.clip(glow_tm.max(-1), 0, 1)
    alpha = np.maximum(pm, ga)
    rgb = static["rgb"] * pm[..., None] + (glow_tm / np.maximum(alpha, 1e-4)[..., None]) * (1 - pm[..., None])
    rgba = np.dstack([np.clip(rgb, 0, 1), alpha])
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, "sign_rgba.png"))
    anchor = {
        "image": "sign_rgba.png",
        "image_size": [CW, CH],
        "composition": "docs/concepts/round2/r2c_v2_modem/modem_shop.png (1920x1080)",
        "image_top_left_in_shop": [origin[0], origin[1]],
        "plate_rect_in_image": [MARGIN, MARGIN, PW, PH],
        "plate_rect_in_shop": [SHOP_PLATE_XY[0], SHOP_PLATE_XY[1], PW, PH],
        "pivot": "top-left; the image overhangs the screen edge by the glow margin",
        "replaces": ["old MODEM sign", "CYBER SHOP plate", "BUY/SELL/TRADE stickers"],
        "blend": "straight alpha; plate pixels opaque, glow semi-transparent. In Godot draw the glow "
                 "additively (or rely on 2D HDR glow) and add a PointLight2D/TextureLight2D spill "
                 "using the blurred emission, pink+cyan, energy ~1.2, range ~600 px",
        "state": "static lit (reduce-effects frame); pulses and warm-up are shader/animation driven",
    }
    with open(os.path.join(OUT, "sign_anchor.json"), "w", encoding="utf-8") as f:
        json.dump(anchor, f, indent=2)
    print("rgba", flush=True)

    # ---------------------------------------------------------- warmup_strip.png
    W, H = 1920, 1080
    canvas = Image.new("RGB", (W, H), (11, 12, 17))
    d = ImageDraw.Draw(canvas)
    d.text((40, 30), "MODEM SIGN  /  WARM-UP + TRACE PULSE", font=font(40), fill=(236, 230, 240))
    d.text((40, 78), "letter-by-letter strike like the original; then data packets run the traces. "
                     "Reduce-effects: the last frame without pulses, static.",
           font=font(21, "SemiLight Condensed"), fill=(150, 150, 166))
    crop = (0, 0, 470, 1080)  # shop-space crop: sign + spill on the wall and first panel
    sc = 0.8
    cw_, ch_ = int((crop[2] - crop[0]) * sc), int((crop[3] - crop[1]) * sc)
    gap = (W - 4 * cw_) // 5
    # 6 frames don't fit at this size -> 3 + 3 would be tiny; use 6 at narrower crop
    crop = (0, 0, 330, 1080)
    sc = 0.82
    cw_, ch_ = int(330 * sc), int(1080 * sc)
    gap = (W - 6 * cw_) // 7
    for i, (label, state, tfrac, pt, tl) in enumerate(WARMUP):
        r = sign.render(lvls(state), trace_frac=tfrac, pulse_t=pt, trace_level=tl)
        img = composite_on(base, r, origin)
        tile = to_img(img).crop(crop).resize((cw_, ch_), Image.LANCZOS)
        x = gap + i * (cw_ + gap)
        y = 130
        canvas.paste(tile, (x, y))
        d.rectangle([x - 1, y - 1, x + cw_, y + ch_], outline=(48, 50, 62))
        d.text((x, y + ch_ + 12), f"{i + 1:02d}", font=font(30), fill=(255, 64, 170))
        d.text((x + 40, y + ch_ + 17), label, font=font(19, "SemiBold Condensed"), fill=(220, 218, 230))
        print("strip", i, flush=True)
    canvas.save(os.path.join(OUT, "warmup_strip.png"))

    # ---------------------------------------------------------- sign_sheet.png
    sc = 0.78
    BW, BH = int(round(1280 / sc)), int(round(1080 / sc))
    wall = facet_wall(BW, BH, np.random.default_rng(3))
    states = [("OFF", {}, 0.0, None, 0.0), ("WARMING", lvls(WARMUP[3][1]), 0.45, None, 0.7),
              ("FULLY LIT", LIT, 1.0, 0.37, 1.0)]
    top = int(110 / sc)
    xs_big = [int(40 / sc) + k * (CW + 14) for k in range(3)]
    comp = wall
    for (name, st, tf, pt, tl), x in zip(states, xs_big):
        r = sign.render(st, trace_frac=tf, pulse_t=pt, trace_level=tl)
        comp = composite_on(comp, r, (x, top), spill_gain=0.8)
    left = to_img(comp).resize((1280, 1080), Image.LANCZOS)
    sheet_img = Image.new("RGB", (1920, 1080), (11, 12, 17))
    sheet_img.paste(left, (0, 0))
    # close-up of the circuit detail at 3x (same routing as the 1x sign)
    ms.set_scale(3)
    big = Sign(seed=7, traces=sign.traces)
    rb = big.render(LIT, pulse_t=0.37)
    ms.set_scale(1)
    zx0, zy0, zw, zh = 0, 392, 150, 196  # plate-local window: left traces, side chip, letter edge
    R = 3
    bx0, by0 = (MARGIN + zx0) * R, (MARGIN + zy0) * R
    patch = np.asarray(to_img(rb["rgb"] + (1 - rb["alpha"][..., None]) * 0.05), np.float32) / 255.0
    crop_big = patch[by0:by0 + zh * R, bx0:bx0 + zw * R]
    cimg = Image.fromarray((crop_big * 255).astype(np.uint8)).resize((zw * 4, zh * 4), Image.LANCZOS)
    cx, cy = 1920 - zw * 4 - 30, 110
    sheet_img.paste(cimg, (cx, cy))
    d = ImageDraw.Draw(sheet_img)
    d.rectangle([cx - 1, cy - 1, cx + zw * 4, cy + zh * 4], outline=(200, 60, 150), width=2)
    xs = [int(x * sc) for x in xs_big]
    lx = xs[2] + int((MARGIN + zx0) * sc)
    ly = 110 + int((MARGIN + zy0) * sc)
    d.rectangle([lx, ly, lx + int(zw * sc), ly + int(zh * sc)], outline=(200, 60, 150), width=2)
    d.rectangle([0, 0, 1920, 96], fill=(11, 12, 17))
    d.text((40, 22), "MODEM / CYBER SHOP SIGN  -  Cv2 circuit-board neon", font=font(42), fill=(236, 230, 240))
    for (name, *_), x in zip(states, xs):
        d.text((x + int(MARGIN * sc), 70), name, font=font(24, "SemiBold Condensed"), fill=(255, 90, 180))
    d.text((cx, 70), "CLOSE-UP  (3x)  traces, pads, vias, SMD chip, double-line tube",
           font=font(22, "SemiBold Condensed"), fill=(255, 90, 180))
    notes = ["Plate: dark triangulated PCB facets, ~12% copper-tone facets, faceted bezel.",
             "Tubes: hollow double-line glass, white-hot core, pink / cyan; crisp, not faceted.",
             "Traces: 45-degree routed copper under pink glow, pads + vias, SMD chips w/ status LED.",
             "Idle: data packets run the traces (~140 px/s). Reduce-effects = static lit frame."]
    for k, line in enumerate(notes):
        d.text((cx, cy + zh * 4 + 24 + k * 30), line, font=font(20, "SemiLight Condensed"), fill=(176, 176, 190))
    sheet_img.save(os.path.join(OUT, "sign_sheet.png"))
    print("sheet", flush=True)


if __name__ == "__main__":
    main()
