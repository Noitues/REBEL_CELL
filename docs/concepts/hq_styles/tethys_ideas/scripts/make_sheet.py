"""Assemble the deliverables: A..E pngs, ideas_sheet.jpg (current plate + the 5 ideas, labelled grid, 2400 px wide) and E_manta_motion.jpg.
python make_sheet.py   (reads D:/rc_scratch/hq_styles/tethys_ideas/<tag>/<tag>.png)"""
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
S = "D:/rc_scratch/hq_styles/tethys_ideas"
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "..", "golden_plates", "hq_tethys_overview.png"))
SRC = dict(A=("A/A.png", "A_jelly_bloom.png"), B=("B2/B2.png", "B_coral_spire.png"), C=("C2/C2.png", "C_whale_fall.png"),
           D=("D2/D2.png", "D_man_o_war.png"), E=("E5/E5_sh.png", "E_manta.png"))
CAP = {
    "now": "Current plate: hex pier city, one big dome with pods on the joints.",
    "A": "A  Jelly bloom: one colossal bell on glowing tentacle shafts; an instant jellyfish, but it reads like a striped parasol.",
    "B": "B  Coral spire: a pale branching coral tree on a reef mound; reads as coral, small and light against the city.",
    "C": "C  Whale fall: a rib arcade over the deck and a lit skull hall; reads as a skeleton, a little like a boxy fish.",
    "D": "D  Man o war: a pink float with a crest and blue tentacles below; squints as a jelly cap, the sail and the chain route are weak.",
    "E": "E  Manta: a low arcology on a ray gliding over the drowned city, with shadow and wake; the clearest silhouette.",
}
try:
    FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    FONTB = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 19)
except Exception:
    FONT = FONTB = ImageFont.load_default()


def main():
    for k, (src, dst) in SRC.items():
        p = os.path.join(S, src)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, dst))
    tiles = [("now", Image.open(GOLD).convert("RGB"))]
    for k in "ABCDE":
        p = os.path.join(OUT, SRC[k][1])
        if os.path.exists(p):
            tiles.append((k, Image.open(p).convert("RGB")))
    W, Hc, cap_h = 800, 450, 62
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, (Hc + cap_h) * rows), (10, 14, 20))
    d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(tiles):
        x, y = (i % cols) * W, (i // cols) * (Hc + cap_h)
        sheet.paste(im.resize((W, Hc), Image.LANCZOS), (x, y))
        txt = CAP[k]
        words, lines, cur = txt.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=FONT) > W - 16:
                lines.append(cur)
                cur = w
            else:
                cur = t
        lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            d.text((x + 8, y + Hc + 4 + j * 20), ln, fill=(235, 240, 245), font=FONTB if j == 0 and False else FONT)
    sheet.save(os.path.join(OUT, "ideas_sheet.jpg"), quality=90)
    # the manta motion strip: three frames along the loop (wings up, level, down)
    fr = [("Eup/Eup_sh.png", "wings up, loop -135 deg"), ("E5/E5_sh.png", "wings level, loop -90 deg (the still)"), ("Edown/Edown_sh.png", "wings down, loop -45 deg")]
    ims = [(Image.open(os.path.join(S, p)).convert("RGB"), c) for p, c in fr if os.path.exists(os.path.join(S, p))]
    if ims:
        cw, ch = 640, 360
        strip = Image.new("RGB", (cw * len(ims), ch + 30), (10, 14, 20))
        dd = ImageDraw.Draw(strip)
        for i, (im, c) in enumerate(ims):
            w, h = im.size
            strip.paste(im.crop((int(w * 0.10), 0, int(w * 0.90), int(h * 0.80))).resize((cw, ch), Image.LANCZOS), (i * cw, 0))
            dd.text((i * cw + 8, ch + 5), c, fill=(235, 240, 245), font=FONT)
        strip.save(os.path.join(OUT, "E_manta_motion.jpg"), quality=90)


if __name__ == "__main__":
    main()
