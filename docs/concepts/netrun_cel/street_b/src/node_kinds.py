"""Plate 2: node_kinds.png. The six Campaign B node kinds: key strip (proposal silhouettes on the locked sticker art),
the locked round 31/32 stickers beside them, silhouette / greyscale / 16 px checks, and the six kinds placed in
context on the staged street at the approved zoom (1:1, 40 px stickers).
Writes D:/rc_scratch/street_b/silhouette_iou.json too.
Run: python node_kinds.py
"""
import json

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import sb_lib as B

DOES = {
    "fight": ["fight (Takeover).", "Win: 3 class cards to pick, credits for", "segments held over the cap."],
    "elite": ["elite fight.", "Win: Heat +1, the rich card offer", "and 2 implants."],
    "event": ["no fight. Pick one:", "heal 5 run health, take an implant,", "or upgrade 2 cards."],
    "shop": ["the shop: buy cards / an implant,", "upgrade, remove, transform, patch.", "Credits."],
    "rack": ["fight at elite strength, then BANK", "the run's loot. Mid rack (L4) heals 6;", "the last layer's rack ends the street."],
    "boss": ["HQ street only: its last node.", "The corp HQ boss fight; the result", "ends the campaign (won / lost)."],
}
NOTE = (190, 205, 222)
TXT = (215, 222, 232)
DIMT = (130, 140, 160)


def sil(kind, mode, px):
    sd = B.sticker_sd(kind, 96, mode)
    t = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    t = B.L.place_sticker(t, sd, 110, 110, angle=0, shadow=0.0)
    a = t.split()[3]
    bb = a.getbbox()
    a = a.crop(bb)
    s = max(a.size)
    sq = Image.new("L", (s, s), 0)
    sq.paste(a, ((s - a.width) // 2, (s - a.height) // 2))
    return sq.resize((px, px), Image.LANCZOS)


def iou_table(mode, kinds, px):
    m = {k: np.asarray(sil(k, mode, px), np.float32) / 255 for k in kinds}
    out = {}
    for i, a in enumerate(kinds):
        for b in kinds[i + 1:]:
            out[a + "/" + b] = round(float(np.minimum(m[a], m[b]).sum() / np.maximum(m[a], m[b]).sum()), 3)
    return out


def main():
    Wd, Hd = 1920, 1500
    img = Image.new("RGBA", (Wd, Hd), (12, 10, 20, 255))
    d = ImageDraw.Draw(img)
    B.K.text(img, (40, 40), "CAMPAIGN B NODE KINDS", B.font_anton(40), (240, 240, 250), "lm", 0.5)
    B.K.text(img, (40, 78), "Words exactly as the port names them (content/b/street_rules node_labels). Sticker art = the locked round 31/32 "
             "netrun icons; the outer die-cut SILHOUETTE per kind is a PROPOSAL; BLOCK SERVER is a new sticker (PROPOSAL).",
             B.font_mono(15), NOTE, "lm", 0)

    # ---------------- key strip: six kinds
    colw = 300
    x0 = 60
    y = 200
    for i, k in enumerate(B.ORDER):
        kd = B.KINDS[k]
        cx = x0 + colw * i + colw / 2 - 30
        B.put(img, B.node_tile(k, 128, None), cx, y)
        B.K.text(img, (cx, y + 96), kd["word"], B.font_anton(30), (245, 245, 250), "mm", 0.6)
        B.K.text(img, (cx, y + 124), "type: %s" % k, B.font_mono(14), DIMT, "mm", 0)
        for j, line in enumerate(DOES[k]):
            B.K.text(img, (cx, y + 152 + j * 19), line, B.font_mono(14), TXT, "mm", 0)
        tag = "NEW STICKER: PROPOSAL" if kd["locked"] is None else "art LOCKED r31/32, shape PROPOSAL"
        tc = B.PICKB if kd["locked"] is None else (255, 200, 90)
        B.K.text(img, (cx, y + 222), tag, B.font_mono(13), tc, "mm", 0)
        # swatch of the kind colour + its word as a hex
        d.rectangle([cx - 40, y + 238, cx + 40, y + 246], fill=kd["ring"] + (255,))

    # ---------------- comparison rows
    y2 = 500
    d.line([(40, y2 - 30), (Wd - 40, y2 - 30)], fill=(50, 50, 70, 255), width=1)
    labels = ["locked r31/32 (64 px)", "proposal (64 px)", "silhouette 24 px", "silhouette 16 px", "greyscale (64 px)"]
    rows_y = [y2 + 40, y2 + 130, y2 + 210, y2 + 262, y2 + 330]
    for lab, ry in zip(labels, rows_y):
        B.K.text(img, (40, ry), lab, B.font_mono(15), NOTE, "lm", 0)
    for i, k in enumerate(B.ORDER):
        cx = 330 + i * 250
        kd = B.KINDS[k]
        if kd["locked"]:
            B.put(img, B.node_tile(k, 64, None, mode="locked"), cx, rows_y[0])
        else:
            B.K.text(img, (cx, rows_y[0]), "(none: HQ final node used", B.font_mono(13), DIMT, "mm", 0)
            B.K.text(img, (cx, rows_y[0] + 18), "the rack sticker + red circle)", B.font_mono(13), DIMT, "mm", 0)
        B.put(img, B.node_tile(k, 64, None), cx, rows_y[1])
        for px, ry in ((24, rows_y[2]), (16, rows_y[3])):
            s = sil(k, "proposal", px)
            blk = Image.new("RGBA", s.size, (235, 235, 245, 255))
            blk.putalpha(s)
            img.alpha_composite(blk, (int(cx - 20 - px / 2), int(ry - px / 2)))
            if kd["locked"]:
                s2 = sil(k, "locked", px)
                blk2 = Image.new("RGBA", s2.size, (120, 120, 135, 255))
                blk2.putalpha(s2)
                img.alpha_composite(blk2, (int(cx + 20 - px / 2), int(ry - px / 2)))
        t = B.node_tile(k, 64, None)
        g = ImageOps.grayscale(t.convert("RGB")).convert("RGBA")
        g.putalpha(t.split()[3])
        B.put(img, g, cx, rows_y[4])
    B.K.text(img, (40, rows_y[2] + 22), "(white = proposal, grey = locked)", B.font_mono(12), DIMT, "lm", 0)

    # silhouette IoU (bible 5.2: soft IoU below ~0.68 at 16 px)
    kinds5 = [k for k in B.ORDER if B.KINDS[k]["locked"]]
    res = {"proposal_16": iou_table("proposal", B.ORDER, 16), "proposal_24": iou_table("proposal", B.ORDER, 24),
           "locked_16": iou_table("locked", kinds5, 16)}
    json.dump(res, open(B.SCR + "/silhouette_iou.json", "w"), indent=1)
    mp = max(res["proposal_16"].items(), key=lambda kv: kv[1])
    ml = max(res["locked_16"].items(), key=lambda kv: kv[1])
    lo = min(res["locked_16"].items(), key=lambda kv: kv[1])
    circ = [kv for kv in res["locked_16"].items() if "rack" not in kv[0]]
    tx = 1660
    lines = [("16 px soft IoU, worst pair", NOTE),
             ("locked: %.2f (%s;" % (ml[1], ml[0].replace("/", "=")), (255, 90, 90)),
             ("  4 of 5 are circles)", (255, 90, 90)),
             ("proposal: %.2f (%s)" % (mp[1], mp[0].replace("/", "/")), (255, 200, 90)),
             ("pairs < 0.68: %d of 15" % sum(1 for v in res["proposal_16"].values() if v < 0.68), (255, 200, 90)),
             ("filled stickers stay blobs at", DIMT),
             ("16 px: the glyph rule (5.2) is", DIMT),
             ("not met; shape reads from 24 px", DIMT)]
    for j, (s, c) in enumerate(lines):
        B.K.text(img, (tx, rows_y[1] + 40 + j * 21), s, B.font_mono(14), c, "lm", 0)

    # ---------------- in context: the six kinds on the staged street at the approved zoom
    y3 = 900
    d.line([(40, y3 - 22), (Wd - 40, y3 - 22)], fill=(50, 50, 70, 255), width=1)
    B.K.text(img, (40, y3), "IN CONTEXT, 1:1 at the approved street zoom (40 px stickers, ZOOM_RULES 6.3). A gallery: the six never share one layer "
             "(BLOCK SERVER only ends the HQ street).", B.font_mono(15), NOTE, "lm", 0)
    street = Image.open(B.GOLDEN).convert("RGBA")
    place = [("fight", 300, 0, "ahead"), ("elite", 560, 1, "option"), ("event", 880, 0, "option"),
             ("shop", 1130, 1, "ahead"), ("rack", 1400, 2, "ahead"), ("boss", 1760, 1, "ahead")]
    boxes = []
    for k, x, r, st in place:
        top = 786 - 66 * r
        bx = (x - 43, top, x + 43, top + 50)
        boxes.append(bx)
        street = B.room(street, k, bx, "full")
    for (k, x, r, st), bx in zip(place, boxes):
        col = {"option": B.ORANGE, "ahead": B.WHITE}[st]
        street = B.frame_room(street, bx, col, 3 if st == "option" else 2, 1.0 if st == "option" else 0.75, glow=st == "option")
    for (k, x, r, st), bx in zip(place, boxes):
        B.put(street, B.node_tile(k, 40, st, ring_w=4 if st == "option" else 3), bx[0] + 2, (bx[1] + bx[3]) / 2)
    crop = street.crop((0, 560, 1920, 900))
    img.alpha_composite(crop, (0, y3 + 24))
    cd = ImageDraw.Draw(img)
    for (k, x, r, st), bx in zip(place, boxes):
        B.K.text(img, (x, y3 + 24 + 340 + 20), B.KINDS[k]["word"], B.font_mono(15), TXT, "mm", 0.4)
    # 3x inset of the 40 px stickers (what the eye resolves at 1080p)
    y4 = y3 + 24 + 340 + 46
    B.K.text(img, (40, y4 + 40), "3x zoom of the frame above:", B.font_mono(14), NOTE, "lm", 0)
    xx = 330
    for (k, x, r, st), bx in zip(place, boxes):
        cy = (bx[1] + bx[3]) / 2
        c = street.crop((int(bx[0] - 30), int(cy - 30), int(bx[0] + 54), int(cy + 30))).resize((252, 180), Image.NEAREST)
        img.alpha_composite(c.convert("RGBA").crop((0, 40, 252, 140)), (xx, y4))
        xx += 260
    img = img.crop((0, 0, Wd, y4 + 112))
    img.convert("RGB").save(B.OUTDIR + "/node_kinds.png")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
