"""street_b_sheet.jpg: the two plates plus the approved references they are built from.
Run after street_branch.py and node_kinds.py: python sheet.py
"""
from PIL import Image, ImageDraw

import sb_lib as B

SW = 2400
NOTE = (190, 205, 222)


def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def main():
    sb = Image.open(B.OUTDIR + "/street_branch.png").convert("RGB")
    nk = Image.open(B.OUTDIR + "/node_kinds.png").convert("RGB")
    gold = Image.open(B.GOLDEN).convert("RGB")
    r7 = Image.open(B.CONC + "/netrun_cel/zoom_rules/round7b/crop_sheet.png").convert("RGB").crop((1100, 345, 1640, 690))
    aaa = Image.open(B.CONC + "/route_map_graph/side_view/v3_aaa/r3/AAA2r3.png").convert("RGB")
    left = fit(sb, 1560)
    rw = SW - left.width - 60
    refs = [(fit(gold, rw), "approved: golden_plates/street_overview.png (base of every frame)"),
            (fit(r7, rw), "approved: round 7b PICK candB (pink edge 4 px, fill 0.22, beam_k 3)"),
            (fit(aaa, rw), "locked: route view hybrid D (AAA2r3), rooms, stickers, wax, states")]
    top_h = max(left.height, sum(r.height + 40 for r, _ in refs))
    H = 90 + top_h + 40 + nk.height + 30
    out = Image.new("RGB", (SW, H), (12, 10, 20))
    o = out.convert("RGBA")
    B.K.text(o, (30, 45), "REBEL_CELL  //  CAMPAIGN B NETRUN STREET: BRANCHES + SIX NODE KINDS  (B-096, concept plates, PIL)",
             B.font_anton(34), (240, 240, 250), "lm", 0.4)
    o.paste(left, (20, 90))
    y = 90
    for r, cap in refs:
        o.paste(r, (left.width + 40, y))
        B.K.text(o, (left.width + 40, y + r.height + 16), cap, B.font_mono(14), NOTE, "lm", 0)
        y += r.height + 40
    o.paste(nk, ((SW - nk.width) // 2, 90 + top_h + 40))
    o.convert("RGB").save(B.OUTDIR + "/street_b_sheet.jpg", quality=88)
    print("sheet", o.size)


if __name__ == "__main__":
    main()
