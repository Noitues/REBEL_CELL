"""Plate 1 assembly: the in-game frame (street_branch.main) + plate callouts + a caption strip with the whole street.
Run: python street_branch.py   (or python street_branch_compose.py)
"""
from PIL import Image, ImageDraw

import sb_lib as B
import street_branch as SB

CAP_H = 250
NOTE = (190, 205, 222)


def callout(img, x, y, letter, tx=None, ty=None):
    """A plate note (not UI): a thin circled letter, optional leader to (tx, ty)."""
    d = ImageDraw.Draw(img)
    if tx is not None:
        d.line([(x, y), (tx, ty)], fill=NOTE + (200,), width=1)
        d.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=NOTE + (230,))
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(8, 10, 20, 225), outline=NOTE + (255,), width=2)
    B.K.text(img, (x, y + 1), letter, B.font_mono(17), NOTE, "mm", 0)
    return img


def mini_graph(img, x0, y0, w, h, N, depth, lanes, cur, hover, opts, reach):
    """The whole street of the sample (8 layers x 4 stories): the frame's window bracketed, the lanes coloured."""
    d = ImageDraw.Draw(img)
    lx = lambda l: x0 + 18 + (l - 1) * (w - 36) / (depth - 1)
    ry = lambda r: y0 + h - 16 - r * (h - 40) / 3
    # window bracket
    a, b = lx(SB.FIRST) - 14, lx(SB.LAST) + 14
    d.rectangle([a, y0 + 6, b, y0 + h - 2], outline=NOTE + (120,), width=1)
    B.K.text(img, (a, y0 - 4), "THIS FRAME (L5-L8)", B.font_mono(12), NOTE, "lm", 0.5)
    B.K.text(img, (x0 + 6, y0 - 4), "WHOLE STREET", B.font_mono(12), NOTE, "lm", 0.5)
    for r, lab in enumerate(["ground", "2nd", "3rd", "top"]):
        B.K.text(img, (x0 - 4, ry(r)), lab, B.font_mono(11), (120, 130, 150), "rm", 0)
    hi, lo = lanes[hover], [p for o, p in lanes.items() if o != hover][0]
    for i, n in N.items():
        for j in n["links"]:
            m = N[j]
            p0, p1 = (lx(n["layer"]), ry(n["row"])), (lx(m["layer"]), ry(m["row"]))
            if i in hi and j in hi and hi.index(j) == hi.index(i) + 1:
                d.line([p0, p1], fill=B.PICKB + (255,), width=4)
            elif i in lo and j in lo and lo.index(j) == lo.index(i) + 1:
                d.line([p0, p1], fill=(255, 190, 120, 200), width=2)
            else:
                d.line([p0, p1], fill=(90, 86, 104, 255), width=1)
    for i, n in N.items():
        x, y = lx(n["layer"]), ry(n["row"])
        k = B.KINDS[n["type"]]
        st = "current" if i == cur else ("option" if i in opts else ("ahead" if i in reach else None))
        r = 7
        d.ellipse([x - r, y - r, x + r, y + r], fill=k["ring"] + (255,), outline=(10, 8, 14, 255), width=1)
        if st:
            col = {"current": B.LIME, "option": B.ORANGE, "ahead": B.WHITE}[st]
            d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], outline=col + (255,), width=2)
    for l in range(1, depth + 1):
        B.K.text(img, (lx(l), y0 + h + 10), "L%d" % l, B.font_mono(11), (120, 130, 150), "mm", 0)
    return img


def run():
    frame, N, lanes, win, opts, reach = SB.main()
    frame.convert("RGB").save(B.SCR + "/street_branch_frame.png")
    img = frame.copy()
    bx = lambda i: SB.box_of(N[i])
    # plate notes on the frame
    c = bx(SB.CUR)
    img = callout(img, c[0] - 70, c[1] - 60, "A", c[0] - 22, c[1] - 4)
    h1 = bx(SB.HOVER)
    img = callout(img, h1[2] + 70, h1[1] - 70, "B", h1[2] + 6, h1[1] - 6)
    lo = [p for o, p in lanes.items() if o != SB.HOVER][0]
    l1 = bx(lo[1])
    img = callout(img, l1[2] + 64, l1[3] + 46, "C", l1[2] + 6, l1[3] + 4)
    e = bx(lanes[SB.HOVER][-1])
    img = callout(img, e[2] + 70, e[1] + 10, "D", e[2] + 8, (e[1] + e[3]) / 2)
    g = bx(64)
    img = callout(img, g[0] - 60, g[1] - 40, "E", g[0] - 8, g[1])

    out = Image.new("RGBA", (B.W, B.H + CAP_H), (10, 9, 16, 255))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.line([(0, B.H), (B.W, B.H)], fill=(60, 60, 80, 255), width=2)
    y0 = B.H + 18
    t = B.font_anton(30)
    B.K.text(out, (40, y0 + 14), "CAMPAIGN B STREET: FORK, TWO LANES, REJOIN", t, (240, 240, 250), "lm", 0.5)
    B.K.text(out, (40, y0 + 44), "Real data: port-campaign-b street_sample seed 2 tier 2, layers 5-8 of 8. Rows are stories (ground .. top floor),",
             B.font_mono(15), NOTE, "lm", 0)
    B.K.text(out, (40, y0 + 64), "so a lane is a run of rooms on floors. Staged on golden_plates/street_overview.png; rooms from the locked route view.",
             B.font_mono(15), NOTE, "lm", 0)
    notes = [
        ("A", "FORK. You are at node 52 (ELITE, 2nd floor, lime). It links to two rooms: the player picks one (go:NODE)."),
        ("B", "LANE 2 (hovered): TERMINAL -> ROUTER, climbs a floor a layer. Round 7b pick B: pink 4 px edge, 22 % fill, beam."),
        ("C", "LANE 1: ROUTER -> ROUTER on the ground floor. Dimmed (rooms x0.6, wax 55 %), still orange: still a choice."),
        ("D", "REJOIN: both lanes end at the final SERVER RACK (top floor, 'roof relay'). The beam rises from it."),
        ("E", "CUT OFF (grey): rooms of these layers that 52 cannot reach. Whole graph stays drawn (bible 4.6)."),
    ]
    yy = y0 + 96
    for k, s in notes:
        callout(out, 54, yy, k)
        B.K.text(out, (78, yy), s, B.font_mono(15), (215, 222, 232), "lm", 0)
        yy += 28
    import json
    s = json.load(open(B.SCR + "/samples.json"))[SB.SAMPLE]
    out = mini_graph(out, 1340, B.H + 34, 540, 172, N, s["depth"], lanes, SB.CUR, SB.HOVER, opts, reach)
    out.convert("RGB").save(B.OUTDIR + "/street_branch.png")
    print("saved", B.OUTDIR + "/street_branch.png")


if __name__ == "__main__":
    run()
