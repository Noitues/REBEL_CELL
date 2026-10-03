"""Round 26: the city map with the round 26 HQs -> ../city_night_hq_v5.jpg + ../hq_<corp>_city.jpg crops.
Round 26 adds the view-corridor rule (citydata.blocks_view): tall buildings between a close-up camera and its HQ / Site
are dropped here exactly as in the close-ups.

Round 25 header:
Round 25: the city map with the round 25 HQs.

The map is still the round 6 restyler over the game's own layout (round6_city_restyle/city_layout.json, read-only),
night theme, same framing and labels as round 24. What changes:
  - the four old HQ drawings (and their roof signs) are taken out of the layout;
  - the city buildings that stand on the Cell's base plot or on the fist roads are taken out (the same rule the
    close-ups use, so the fist stays readable and the base has its plot);
  - each HQ (and the Cell's base) is pasted back as the SPRITE of the very Blender model used by its combat
    close-up (hq_scene.py map view: orthographic, the game's 2:1 iso projection, front buildings as holdout),
    finished here with the map's ink.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "city_r6"))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "..", "round6_city_restyle")
MAP = os.path.join(OUT, "scratch", "map")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import lowpoly
import views as V
from restyle import View, labels
import citydata as CD

CORPS = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]


def edges(a, thr):
    e = np.zeros(a.shape[:2], bool)
    for dy, dx in ((0, 1), (1, 0)):
        b = np.roll(np.roll(a, -dy, 0), -dx, 1)
        d = np.abs(a - b)
        d = d.sum(axis=2) if d.ndim == 3 else d
        e |= d > thr
    return e


def sprite(tag):
    """Beauty + the map's ink (part id, normal and silhouette edges), a soft glow of the lit parts."""
    b = np.asarray(Image.open(os.path.join(MAP, tag + "_map_beauty.png")).convert("RGBA"), np.float32) / 255
    n = np.asarray(Image.open(os.path.join(MAP, tag + "_map_normal.png")).convert("RGB"), np.float32) / 255
    i = np.asarray(Image.open(os.path.join(MAP, tag + "_map_id.png")).convert("RGB"), np.float32) / 255
    a = b[..., 3]
    ink = (edges(i, 0.04) | edges(n, 0.45)) & (a > 0.5)
    sil = edges(a[..., None], 0.5)
    ink = ink | sil
    inkm = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    rgb = np.clip(b[..., :3] * (0.85 if tag.startswith("meridian") else 1.3), 0, 1)  # the lit-toon towers are already bright  # lift to the map's brightness (the restyler's neon-lit facades)
    rgb = rgb * (1 - inkm[..., None] * 0.85) + np.array([0.05, 0.04, 0.08]) * inkm[..., None] * 0.85
    alpha = np.maximum(a, inkm * (np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), np.float32) / 255))
    lum = rgb.max(axis=2)
    hot = np.clip((lum - 0.55) / 0.45, 0, 1)[..., None] * rgb * alpha[..., None]
    g = Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    g = np.asarray(g, np.float32) / 255
    out = np.concatenate([np.clip(rgb + g * 0.5, 0, 1), alpha[..., None]], axis=2)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def edit_layout(d):
    L = CD.Lots(d)
    hq = CD.hq_centres(d)
    base = CD.rc_base_centre(d, L)
    fist = CD.fist_lots(d, L)
    CD.jobs(d, L)  # fills CD.VIEWS (the close-up cameras)
    hq_ctx = {i for i, c in enumerate(d["contexts"]) if c["kind"] == "hq"}
    keep = []
    for p in d["prims"]:
        ci = p.get("ctx", -1)
        if ci in hq_ctx:
            continue  # old HQ drawing + its roof sign
        if p["t"] == "ext" and ci >= 0:
            q = L.pts(p["b"])
            c = (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q))
            if (abs(c[0] - base[0]) < 4.6 and abs(c[1] - base[1]) < 4.6) or CD.near_fist(c, fist, 0.9) or CD.blocks_view(c, p["h"] + p["z0"]):
                continue
        keep.append(p)
    drop_ctx = set()
    d["prims"] = keep
    # also drop the raw decorations (roof boxes, quads) of buildings that lost all their extrusions
    alive = {p["ctx"] for p in keep if p["t"] == "ext"}
    d["prims"] = [p for p in keep if p["t"] == "ext" or p.get("ctx", -1) < 0 or p["ctx"] in alive or d["contexts"][p["ctx"]]["kind"] != "bld"]
    centres = dict(hq)
    centres["rebel_cell"] = base
    return {k: L.iso(*v) for k, v in centres.items()}


def main():
    d = json.load(open(os.path.join(SRC, "city_layout.json")))
    screens = edit_layout(d)
    V.set_theme("night")
    vw = d["view"]
    full = View(0, 0, vw["zoom"], vw["w"], vw["h"])
    lowpoly.W, lowpoly.H = full.w, full.h
    img = V.ViewRestyler(d, full, "night", False).render().convert("RGBA")
    z = vw["zoom"]
    # paste back to front (by screen y) so nearer HQs overlap farther ones correctly
    for corp in sorted(CORPS, key=lambda c: screens[c][1]):
        sp = sprite("%s_hq" % corp)
        sp = sp.resize((int(sp.width * z / 2), int(sp.height * z / 2)), Image.LANCZOS)
        X, Y = screens[corp]
        cx, cy = X * z, (Y - 450) * z
        img.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))
    img = img.convert("RGB")
    for corp in CORPS:  # city-map crops (full 3840 resolution)
        X, Y = screens[corp]
        cx, cy = X * z, (Y - 200) * z
        s = 1100 if corp != "rebel_cell" else 1500
        crop = img.crop((int(cx - s / 2), int(cy - s / 2 * 0.62), int(cx + s / 2), int(cy + s / 2 * 0.62)))
        dd = ImageDraw.Draw(crop)
        f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 30)
        dd.rectangle([0, 0, 520, 44], fill=(10, 9, 16))
        dd.text((14, 6), "CITY MAP  -  %s HQ" % corp.upper().replace("_", " ") if corp != "rebel_cell" else "CITY MAP  -  THE CELL'S BASE (fist)",
                font=f, fill=(240, 236, 226))
        if corp != "rebel_cell":
            if corp == "meridian":
                crop.save(os.path.join(OUT, "hq_%s_city.jpg" % corp), quality=90)
        print("crop", corp, flush=True)
    img = labels(img, d, full)
    img.resize((2560, 1440), Image.LANCZOS).save(os.path.join(OUT, "city_night_hq_v5.jpg"), quality=90)
    print("wrote city_night_hq_v5.jpg", flush=True)


if __name__ == "__main__":
    main()
