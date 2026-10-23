"""sheet.jpg (2560 wide): rows A / B / C, columns map | street | inside, and under each row its squint strip (320 px crisp + the same with a 4 px blur at
1920 scale, for every frame). python gs_sheet.py"""
import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

G = "D:/rc_art/art-pass/docs/concepts/solace_vertical/garden/"
FONTS = "D:/rc_art/godot_look_bloom/assets/fonts/"
BG = (12, 7, 20)


def anton(px):
    return ImageFont.truetype(FONTS + "Anton-Regular.ttf", px)


def mono(px):
    return ImageFont.truetype(FONTS + "ShareTechMono-Regular.ttf", px)


NAMES = {"A": ("GLASS WARD", "porcelain clinic plinth + an iron-ribbed Victorian palm house in 5 stepped glass tiers; domed glass vault crown. The calmest read."),
         "B": ("CULTURE STACK", "stacked oval incubator trays (petri dishes) in hex cell skin, mint agar light; the seed vault is a sealed cryo drum."),
         "C": ("HANGING MOUNTAIN", "a terraced green mountain in a glass diagrid shell, planter-walk ramp spiralling up, mist-waterfall core, seed-pod crown.")}
COLS = (("map", "CITY MAP  cel + ink, the Godot city camera, HQ helix for scale"), ("street", "STREET NETRUN at the plaza (O2)  AAA-2, Bloom A creeping"),
        ("inside", "INSIDE  I1 / I3 + workshop / I5, glazing open  AAA-2, Bloom catching"))
FW = 780
FH = 439
LW = 170
GAP = 10


def squint(im, sigma_px=4.0):
    w = 320
    h = round(im.size[1] * w / im.size[0])
    c = im.resize((w, h), Image.LANCZOS)
    b = im.filter(ImageFilter.GaussianBlur(sigma_px * im.size[0] / 1920.0)).resize((w, h), Image.LANCZOS)
    return c, b


def main():
    rows = 3
    RH = FH + 28 + 180 + 36
    W = LW + 3 * (FW + GAP) + 10
    H = 150 + rows * RH + 40
    S = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(S)
    d.text((16, 12), "SOLACE // CULTURE GARDEN (EX-11, Virus key exploit building)  -  concept round, three directions (art-pass, Solace list item 5)", font=anton(34), fill=(240, 244, 250))
    d.text((16, 62), "rows A / B / C  |  media: map = cel + ink (District / HQ park scene), street + inside = AAA-2 night (Cycles)  |  lot 48 x 42 BU (spec 48 x 36; +6 BU of plaza apron), clearance 8 BU, height 49 / 55 / 44 BU vs HQ helix 86 BU",
           font=mono(15), fill=(160, 175, 200))
    d.text((16, 86), "route chrome in the frames (rings, columns, slot frames) is a concept proxy of the game's own chrome  |  squint rows: 320 px, and the same with a 4 px blur at 1920 scale  |  no red cross anywhere",
           font=mono(15), fill=(160, 175, 200))
    for ci, (key, lab) in enumerate(COLS):
        d.text((LW + ci * (FW + GAP), 118), lab, font=mono(15), fill=(210, 220, 235))
    for ri, k in enumerate("ABC"):
        y0 = 150 + ri * RH
        d.text((14, y0), k, font=anton(80), fill=(150, 255, 70))
        d.text((14, y0 + 96), NAMES[k][0], font=anton(24 if len(NAMES[k][0]) < 14 else 18), fill=(240, 244, 250))
        # wrapped description
        words, line, yy = NAMES[k][1].split(), "", y0 + 134
        for wd in words:
            if len(line) + len(wd) > 21:
                d.text((14, yy), line, font=mono(13), fill=(165, 180, 205))
                line, yy = "", yy + 17
            line += wd + " "
        d.text((14, yy), line, font=mono(13), fill=(165, 180, 205))
        for ci, (key, _lab) in enumerate(COLS):
            im = Image.open(G + "%s_%s.png" % (k, key)).convert("RGB")
            x = LW + ci * (FW + GAP)
            S.paste(im.resize((FW, FH), Image.LANCZOS), (x, y0))
            c, b = squint(im)
            sy = y0 + FH + 28
            S.paste(c, (x, sy))
            S.paste(b, (x + 330, sy))
            d.text((x, sy - 16), "squint 320 px", font=mono(12), fill=(130, 145, 170))
            d.text((x + 330, sy - 16), "+ 4 px blur", font=mono(12), fill=(130, 145, 170))
        d.line([(0, y0 + RH - 16), (W, y0 + RH - 16)], fill=(40, 34, 60), width=1)
    S.save(G + "sheet.jpg", quality=92)
    print("sheet", S.size)


if __name__ == "__main__":
    main()
