"""Composes the per-element LOD sheets (1920 px wide) and INDEX.jpg from the lod_lab captures.

usage: python make_lod_sheets.py <raw dir> <out dir> [--only id,id]
Raw dir: ctx_<id>_b<band>.png, lab_<id>_b<band>.png and meta_<id>.json from tools/look_parity/lod_lab.gd.
Run it by path (never from stdin).
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import lod_data  # noqa: E402

W = 1920
GAP = 12
COLS = 5
CW = (W - GAP * (COLS + 1)) // COLS
CH = int(CW * 1.15)
ASPECT = CW / CH
FRAME = (1920.0, 1080.0)
FONT = "C:/Windows/Fonts/arial.ttf"
FONTB = "C:/Windows/Fonts/arialbd.ttf"
MONO = "C:/Windows/Fonts/consola.ttf"
BG = (14, 12, 20)
PANEL = (24, 20, 34)
INK = (232, 226, 240)
DIM = (150, 142, 168)
BADGE = {"built": ((60, 190, 120), "BUILT"), "partial": ((230, 190, 70), "PARTIAL"), "asis": ((110, 150, 230), "AS R43"), "none": ((230, 80, 90), "NOT YET BUILT")}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def crop_box(r, aspect, margin, frame):
    """Mirror of LodLabMath.crop_box."""
    x, y, w, h = r
    cx, cy = x + w / 2, y + h / 2
    w = max(w * margin, 8.0)
    h = max(h * margin, 8.0)
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    k = min(1.0, min(frame[0] / w, frame[1] / h))
    w *= k
    h *= k
    x = min(max(cx - w / 2, 0.0), frame[0] - w)
    y = min(max(cy - h / 2, 0.0), frame[1] - h)
    return (x, y, w, h)


def cell_from(path, box, margin):
    """Crop `path` to the cell and return (image, scale)."""
    if not os.path.exists(path):
        return None, 1.0
    im = Image.open(path).convert("RGB")
    x, y, w, h = crop_box(box, ASPECT, margin, FRAME)
    c = im.crop((int(round(x)), int(round(y)), int(round(x + w)), int(round(y + h))))
    scale = CW / c.size[0]
    return c.resize((CW, CH), Image.LANCZOS), scale


def dark_cell(draw, img, x, y, status, spec, title):
    draw.rectangle((x, y, x + CW, y + CH), fill=(18, 14, 24), outline=BADGE[status][0])
    f1 = font(FONTB, 18)
    f2 = font(FONT, 14)
    draw.text((x + 10, y + 10), title, font=f1, fill=BADGE[status][0])
    yy = y + 40
    for ln in wrap(draw, spec, f2, CW - 20):
        draw.text((x + 10, yy), ln, font=f2, fill=INK)
        yy += 18


def make_sheet(sd, raw, out):
    eid = sd["id"]
    meta_p = os.path.join(raw, "meta_%s.json" % eid)
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {"poses": {}}
    f_t = font(FONTB, 30)
    f_s = font(FONT, 16)
    f_h = font(FONTB, 16)
    f_c = font(FONT, 13)
    f_sm = font(FONT, 12)
    tmp = Image.new("RGB", (W, 10))
    d0 = ImageDraw.Draw(tmp)
    look_lines = wrap(d0, "LOOK AT: " + sd["look"], f_s, W - 2 * GAP)
    head_h = 52 + 22 * len(look_lines) + 8
    band_h = 44
    cap_h = 150
    row_label = 22
    total = head_h + band_h + row_label + CH + GAP + row_label + CH + GAP + cap_h + GAP
    img = Image.new("RGB", (W, total), BG)
    d = ImageDraw.Draw(img)
    d.text((GAP, 10), sd["title"], font=f_t, fill=INK)
    yy = 52
    for ln in look_lines:
        d.text((GAP, yy), ln, font=f_s, fill=DIM)
        yy += 22
    y0 = head_h
    r1 = y0 + band_h + row_label
    r2 = r1 + CH + GAP + row_label
    cap_y = r2 + CH + GAP
    d.text((GAP, y0 + band_h + 2), "ISOLATED   (the element alone, scaled to fill the cell)", font=f_sm, fill=DIM)
    d.text((GAP, r1 + CH + GAP + 2), "IN CONTEXT   (real city, zoom rules on, same band and scale, wider crop)", font=f_sm, fill=DIM)
    for b in range(COLS):
        x = GAP + b * (CW + GAP)
        st = sd["status"][b]
        col, label = BADGE[st]
        d.rectangle((x, y0, x + CW, y0 + band_h - 6), fill=PANEL)
        d.text((x + 8, y0 + 3), "%s   %s" % (lod_data.BANDS[b], lod_data.RANGES[b]), font=f_h, fill=INK)
        d.rectangle((x, y0 + band_h - 10, x + CW, y0 + band_h - 6), fill=col)
        d.text((x + 8, y0 + 22), label, font=f_sm, fill=col)
        pose = meta["poses"].get(str(b))
        # row 1: isolated
        c1 = None
        scale = 1.0
        if st != "none" and pose and b < 4:
            if pose["src"] == "lab":
                c1, scale = cell_from(os.path.join(raw, "lab_%s_b%d.png" % (eid, b)), pose["lab_box"], 1.12)
            else:
                c1, scale = cell_from(os.path.join(raw, "ctx_%s_b%d.png" % (eid, b)), pose["tight_box"], 1.12)
        if c1 is not None:
            img.paste(c1, (x, r1))
            d.rectangle((x, r1, x + CW, r1 + CH), outline=col)
            d.text((x + 6, r1 + CH - 18), "%.1f px/BU  x%.1f%s" % (pose["ppb"], scale, "  real instance" if pose["src"] == "ctx" else ""), font=f_sm, fill=(255, 255, 255))
        else:
            dark_cell(d, img, x, r1, "none" if st == "none" else st, sd["spec"][b], "NOT YET BUILT" if st == "none" else "NO RENDER")
        # row 2: in context
        c2 = None
        if pose and b < 4:
            c2, s2 = cell_from(os.path.join(raw, "ctx_%s_b%d.png" % (eid, b)), pose["ctx_box"], 1.0)
        if c2 is not None:
            img.paste(c2, (x, r2))
            d.rectangle((x, r2, x + CW, r2 + CH), outline=(70, 64, 90))
            d.text((x + 6, r2 + CH - 18), "%.1f px/BU  x%.1f" % (pose["ppb"], s2), font=f_sm, fill=(255, 255, 255))
        else:
            d.rectangle((x, r2, x + CW, r2 + CH), fill=(18, 14, 24), outline=(70, 64, 90))
            d.text((x + 10, r2 + 10), "NOT RENDERED" if b == 4 else "NO SHOT", font=f_h, fill=DIM)
        # caption strip
        d.rectangle((x, cap_y, x + CW, cap_y + cap_h), fill=PANEL)
        cy = cap_y + 4
        for ln in wrap(d, "SPEC: " + sd["spec"][b], f_c, CW - 12)[:7]:
            d.text((x + 6, cy), ln, font=f_c, fill=INK)
            cy += 15
        note = sd["notes"][b]
        if note:
            cy += 2
            for ln in wrap(d, "CODE: " + note, f_c, CW - 12)[:5]:
                d.text((x + 6, cy), ln, font=f_c, fill=col)
                cy += 15
    path = os.path.join(out, sd["file"])
    img.convert("RGB").save(path, quality=88)
    return img


def make_index(sheets, out):
    n = len(sheets)
    cols = 3
    tw = 620
    thumbs = []
    for sd, im in sheets:
        h = int(im.size[1] * tw / im.size[0])
        thumbs.append((sd, im.resize((tw, h), Image.LANCZOS)))
    rows = (n + cols - 1) // cols
    rh = max(t[1].size[1] for t in thumbs) + 26
    img = Image.new("RGB", (cols * (tw + GAP) + GAP, rows * rh + 50), BG)
    d = ImageDraw.Draw(img)
    d.text((GAP, 8), "LOD sheets: every element, five bands (City / District / Near-street / Street / Close)", font=font(FONTB, 24), fill=INK)
    for i, (sd, t) in enumerate(thumbs):
        x = GAP + (i % cols) * (tw + GAP)
        y = 46 + (i // cols) * rh
        img.paste(t, (x, y + 22))
        d.text((x, y), sd["file"], font=font(FONTB, 15), fill=INK)
        # status squares
        for b in range(5):
            d.rectangle((x + tw - 90 + b * 18, y + 3, x + tw - 90 + b * 18 + 14, y + 17), fill=BADGE[sd["status"][b]][0])
    img.save(os.path.join(out, "INDEX.jpg"), quality=85)


def main():
    raw, out = sys.argv[1], sys.argv[2]
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    os.makedirs(out, exist_ok=True)
    made = []
    for sd in lod_data.SHEETS:
        if only and sd["id"] not in only:
            continue
        made.append((sd, make_sheet(sd, raw, out)))
        print("sheet", sd["file"])
    if not only:
        make_index(made, out)
        print("INDEX.jpg")


if __name__ == "__main__":
    main()
