"""Colour-blind check: Machado 2009 (severity 1.0, linear RGB) on five plates,
plus CIE Delta E 2000 between corp traffic colours under each deficiency."""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = "D:/rc_art/art-pass/docs/concepts/polish/colourblind"
SHEET_TILE_W = 360
LABEL_H = 22
DE_RISK = 10.0

IMAGES = [
    ("tide_city_r43", "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r43/compare_r42_r43.jpg", "right"),
    ("traffic_closeup_variant", "D:/rc_art/art-pass/docs/concepts/tide_raid/variants/traffic_corp/closeup_r43_vs_variant.jpg", "right"),
    ("netrun_street_frame_r4", "D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round4/street_frame.png", None),
    ("cohesion_route_page_r42", "D:/rc_art/art-pass/docs/concepts/cohesion/map_pages_r42/route_page.png", None),
    ("combat_p1_decide_e10", "D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png", None),
]

# Machado, Oliveira, Fernandes 2009, severity 1.0, applied to linear RGB.
MACHADO = {
    "normal": np.eye(3),
    "deutan": np.array([[0.367322, 0.860646, -0.227968],
                        [0.280085, 0.672501, 0.047413],
                        [-0.011820, 0.042940, 0.968881]]),
    "protan": np.array([[0.152286, 1.052583, -0.204868],
                        [0.114503, 0.786281, 0.099216],
                        [-0.003882, -0.048116, 1.051998]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779],
                        [-0.078411, 0.930809, 0.147602],
                        [0.004733, 0.691367, 0.303900]]),
}

# Corp traffic hues at full V (ART_BIBLE 2.4 values as given in the task).
CORP_HUE = {
    "solace": (0.588, 1.0, 0.275),
    "halcyon": (0.69, 0.43, 1.0),
    "meridian": (1.0, 0.55, 0.10),
    "orbital": (0.80, 0.94, 1.0),
    "aurelian": (0.16, 0.86, 0.65),
}
HEAD_V = 0.55
TAIL_V = 0.38


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def simulate_array(rgb, mat):
    """rgb: HxWx3 float sRGB in 0..1 -> simulated sRGB in 0..1."""
    lin = srgb_to_lin(rgb)
    out = lin @ mat.T
    return lin_to_srgb(np.clip(out, 0.0, 1.0))


def simulate_colour(rgb, mat):
    return simulate_array(np.array([[list(rgb)]]), mat)[0, 0]


SRGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                        [0.2126729, 0.7151522, 0.0721750],
                        [0.0193339, 0.1191920, 0.9503041]])
D65 = np.array([0.95047, 1.0, 1.08883])


def srgb_to_lab(rgb):
    xyz = SRGB_TO_XYZ @ srgb_to_lin(rgb) / D65
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    L = 116 * f[1] - 16
    a = 500 * (f[0] - f[1])
    b = 200 * (f[1] - f[2])
    return float(L), float(a), float(b)


def delta_e_2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p = (1 + G) * a1
    a2p = (1 + G) * a2
    C1p = math.hypot(a1p, b1)
    C2p = math.hypot(a2p, b2)
    h1p = 0.0 if C1p == 0 else math.degrees(math.atan2(b1, a1p)) % 360
    h2p = 0.0 if C2p == 0 else math.degrees(math.atan2(b2, a2p)) % 360
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        if dhp > 180:
            dhp -= 360
        elif dhp < -180:
            dhp += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp = (L1 + L2) / 2
    Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) > 180:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    else:
        hbp = (h1p + h2p) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dTheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    SC = 1 + 0.045 * Cbp
    SH = 1 + 0.015 * Cbp * T
    RT = -math.sin(math.radians(2 * dTheta)) * RC
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2
                     + RT * (dCp / SC) * (dHp / SH))


def hex_to_rgb01(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def build_colours():
    cols = {}
    for name, hue in CORP_HUE.items():
        cols[f"{name}_head"] = tuple(c * HEAD_V for c in hue)
        cols[f"{name}_tail"] = tuple(c * TAIL_V for c in hue)
    cols["solace_lime_96FF46"] = hex_to_rgb01("#96FF46")
    cols["cell_lime_D4FF00"] = hex_to_rgb01("#D4FF00")
    return cols


def pair_table(cols):
    names = list(cols.keys())
    rows = []
    # Head-vs-head and tail-vs-tail between corps, plus the lime pair.
    groups = [
        [n for n in names if n.endswith("_head") and n.startswith(tuple(CORP_HUE))],
        [n for n in names if n.endswith("_tail") and n.startswith(tuple(CORP_HUE))],
    ]
    pairs = []
    for g in groups:
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                pairs.append((g[i], g[j]))
    pairs.append(("solace_lime_96FF46", "cell_lime_D4FF00"))
    for a, b in pairs:
        row = {"pair": f"{a} vs {b}", "de2000": {}}
        for dname, mat in MACHADO.items():
            sa = simulate_colour(cols[a], mat)
            sb = simulate_colour(cols[b], mat)
            row["de2000"][dname] = round(delta_e_2000(srgb_to_lab(sa), srgb_to_lab(sb)), 2)
        row["risk"] = sorted(d for d, v in row["de2000"].items() if v < DE_RISK)
        rows.append(row)
    return rows


def load_plate(path, crop):
    img = Image.open(path).convert("RGB")
    if crop == "right":
        w, h = img.size
        img = img.crop((w // 2, 0, w, h))
    return img


def make_sheet(rows, risky_text):
    font = ImageFont.load_default()
    tiles_per_row = 4
    row_imgs = []
    for label, path, crop in IMAGES:
        base = load_plate(path, crop)
        scale = SHEET_TILE_W / base.width
        base = base.resize((SHEET_TILE_W, max(1, int(base.height * scale))), Image.LANCZOS)
        arr = np.asarray(base).astype(np.float64) / 255.0
        tiles = []
        for dname in ["normal", "deutan", "protan", "tritan"]:
            sim = simulate_array(arr, MACHADO[dname]) if dname != "normal" else arr
            tiles.append(Image.fromarray((sim * 255).round().astype(np.uint8)))
        th = max(t.height for t in tiles)
        text_w = 520
        W = SHEET_TILE_W * tiles_per_row + text_w
        H = th + LABEL_H
        canvas = Image.new("RGB", (W, H), (20, 20, 20))
        d = ImageDraw.Draw(canvas)
        for k, (dname, t) in enumerate(zip(["normal", "deutan", "protan", "tritan"], tiles)):
            x = k * SHEET_TILE_W
            canvas.paste(t, (x, LABEL_H))
            d.text((x + 4, 4), f"{label} | {dname}", fill=(230, 230, 230), font=font)
        tx = SHEET_TILE_W * tiles_per_row + 8
        d.text((tx, 4), "Risky pairs (dE2000 < 10), worst first:", fill=(255, 220, 120), font=font)
        y = LABEL_H + 4
        for line in risky_text:
            d.text((tx, y), line, fill=(230, 230, 230), font=font)
            y += 14
        row_imgs.append(canvas)
    total_w = max(r.width for r in row_imgs)
    total_h = sum(r.height for r in row_imgs) + 8 * len(row_imgs)
    sheet = Image.new("RGB", (total_w, total_h), (10, 10, 10))
    y = 0
    for r in row_imgs:
        sheet.paste(r, (0, y))
        y += r.height + 8
    sheet.save(os.path.join(OUT, "sheet.jpg"), quality=90)


def main():
    cols = build_colours()
    rows = pair_table(cols)
    rows_sorted = sorted(rows, key=lambda r: min(r["de2000"].values()))
    worst = rows_sorted[0]
    risky = [r for r in rows_sorted if r["risk"]]
    risky_text = []
    for r in risky[:12]:
        worst_val = min(r["de2000"].values())
        risky_text.append(f"{r['pair'][:44]}  min {worst_val:.1f} {','.join(r['risk'])}")
    if not risky_text:
        risky_text = ["none under dE 10"]
    make_sheet(rows, risky_text)
    result = {
        "colours_srgb01": {k: [round(x, 4) for x in v] for k, v in cols.items()},
        "pairs": rows_sorted,
        "worst_pair": worst["pair"],
        "worst_de": min(worst["de2000"].values()),
        "risky_count": len(risky),
    }
    with open(os.path.join(OUT, "scripts", "results.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"pairs={len(rows)} risky={len(risky)} worst={worst['pair']} de={min(worst['de2000'].values()):.2f}")
    for r in rows_sorted:
        print(r["pair"], r["de2000"], r["risk"])


if __name__ == "__main__":
    main()
