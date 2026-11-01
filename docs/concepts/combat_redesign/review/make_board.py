"""Art-director review board: all style plates side by side with the ranking.

Run: python make_board.py   (writes board.jpg next to this script)
Reads only the explore/ deliverables; writes nothing else.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EX = HERE.parent / "explore"
FONTS = HERE.parents[1] / "tide_raid" / "C_war_table" / "scripts"
ANTON = str(FONTS / "Anton-Regular.ttf")
MONO = str(FONTS / "ShareTechMono-Regular.ttf")

BG = (12, 10, 22)
PANEL = (22, 20, 36)
PINK = (255, 61, 168)
TEXT = (242, 246, 255)
MID = (175, 192, 214)
LO = (122, 136, 156)
GOLD = (255, 196, 40)

# rank order, best first
ROWS = [
    dict(rank=1, key="sketchbook_graffiti", name="SKETCHBOOK GRAFFITI (G2)",
         plates=["plate_A.png", "plate_B.png"], crop="plate_A_wheel_2x.png",
         finalist="FINALIST F1 base",
         verdict=["Most art-led and most 'ours': one pen on tower, cards, SEND IT, nameplate.",
                  "Ballpoint second ink and marker-misses-the-line give real hand craft.",
                  "Weak: paper disc too bright, icons loosened (Brace box, rockets), thin rules text."]),
    dict(rank=2, key="street_graffiti", name="STREET GRAFFITI (G1)",
         plates=["plate_A.png", "plate_B.png"], crop="wheel_A_2x.png",
         finalist="F1 donor: tags, paste, SEND IT",
         verdict=["Best cards and best SEND IT on the board (A: wheat-paste, tag title, tape).",
                  "Tower is a pink pie with marker trim, not wildstyle; reads busy at 1x.",
                  "Pink cards are the brightest thing on screen."]),
    dict(rank=3, key="spiderverse_print", name="SPIDER-VERSE PRINT (G3)",
         plates=["plate_A.png", "plate_B.png"], crop="crop_wheel_A.png",
         finalist="FINALIST F2 base",
         verdict=["Cleanest and most legible; icons survive best; comic-panel cards polished.",
                  "Misregistration too timid at 1x: risks reading as E10 with a filter.",
                  "Defect: Twist icon reads as '?'. Red trim on red hatch is busy."]),
    dict(rank=4, key="zine_collage", name="ZINE COLLAGE (G5)",
         plates=["plate_A.png", "plate_B.png"], crop="plate_A_wheel_2x.png",
         finalist="donor: ransom nameplate only",
         verdict=["Strong concept and best written rules; ransom alphabet is ours alone.",
                  "A's black tower sinks into the dark board; ransom titles slow to read.",
                  "B's cream tower fights the HOT marks."]),
    dict(rank=5, key="arcane_painterly", name="ARCANE PAINTERLY (G4)",
         plates=["plate_A.png", "plate_B.png"], crop="crop_A_wheel_2x.png",
         finalist="F2 donor: neon doodles only",
         verdict=["Procedural bristle reads as scratch noise, not Arcane brushwork.",
                  "Dark tower with pink spokes loses the owned mass; texture gone at 1x.",
                  "Keep only: Jinx-style neon doodles, one painted rim highlight."]),
]

TW, TH = 576, 324          # plate thumbnails (0.3x)
CW = TH                     # square wheel crop
LABEL_W = 430
GAP = 16
HEAD = 150
ROW_H = TH + 2 * GAP
W = LABEL_W + 2 * TW + CW + 5 * GAP
H = HEAD + len(ROWS) * ROW_H + 120


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((GAP * 2, 22), "COMBAT REDESIGN // STYLE REVIEW", font=font(ANTON, 54), fill=TEXT)
    d.text((GAP * 2, 92),
           "p1_decide, state f1, bio room. Ranked against: art style first, player-owned read, "
           "Spider-Verse / Arcane craft, legibility.  Gold = finalist base.  ART CALL 51.",
           font=font(MONO, 20), fill=MID)
    d.text((LABEL_W + GAP, HEAD - 30), "VARIANT A", font=font(MONO, 18), fill=LO)
    d.text((LABEL_W + TW + 2 * GAP, HEAD - 30), "VARIANT B", font=font(MONO, 18), fill=LO)
    d.text((LABEL_W + 2 * TW + 3 * GAP, HEAD - 30), "TOWER 2x (A)", font=font(MONO, 18), fill=LO)

    for i, r in enumerate(ROWS):
        y0 = HEAD + i * ROW_H
        fin = r["rank"] == 1 or r["rank"] == 3
        d.rectangle([GAP, y0, W - GAP, y0 + ROW_H - GAP], fill=PANEL,
                    outline=GOLD if fin else (50, 48, 70), width=3 if fin else 1)
        x = GAP * 2
        d.text((x, y0 + 12), f"#{r['rank']}", font=font(ANTON, 64), fill=GOLD if fin else PINK)
        d.text((x + 86, y0 + 22), r["name"], font=font(ANTON, 26), fill=TEXT)
        d.text((x + 86, y0 + 60), r["finalist"], font=font(MONO, 15),
               fill=GOLD if fin else MID)
        ty = y0 + 110
        for line in r["verdict"]:
            # wrap at ~44 chars
            words, cur = line.split(), ""
            for w_ in words:
                if len(cur) + len(w_) + 1 > 44:
                    d.text((x, ty), cur, font=font(MONO, 16), fill=MID); ty += 21; cur = w_
                else:
                    cur = (cur + " " + w_).strip()
            d.text((x, ty), cur, font=font(MONO, 16), fill=MID); ty += 29
        px = LABEL_W + GAP
        for p in r["plates"]:
            im = Image.open(EX / r["key"] / p).convert("RGB").resize((TW, TH), Image.LANCZOS)
            img.paste(im, (px, y0 + GAP // 2 + 4))
            px += TW + GAP
        cr = Image.open(EX / r["key"] / r["crop"]).convert("RGB")
        s = min(cr.size)
        cr = cr.crop(((cr.width - s) // 2, (cr.height - s) // 2,
                      (cr.width + s) // 2, (cr.height + s) // 2)).resize((CW, CW), Image.LANCZOS)
        img.paste(cr, (px, y0 + GAP // 2 + 4))

    fy = HEAD + len(ROWS) * ROW_H + 8
    d.text((GAP * 2, fy),
           "FINALIST F1  BLACK-BOOK BURNER  = sketchbook graffiti tower + street-graffiti tag titles, "
           "wheat-paste cards and spray SEND IT.", font=font(MONO, 20), fill=GOLD)
    d.text((GAP * 2, fy + 32),
           "FINALIST F2  ZAUN PRESS  = Spider-Verse inked print, pushed misregistration and kirby hit frames, "
           "plus Arcane neon doodle layer and one painted rim highlight.", font=font(MONO, 20), fill=GOLD)
    d.text((GAP * 2, fy + 70),
           "Every plate above still sits on the E10 board (dashes, lane colours, W4-W6 arcs). Finalists must "
           "ship on the redesigned board: see REVIEW.md section 2.", font=font(MONO, 18), fill=PINK)
    out = HERE / "board.jpg"
    img.save(out, quality=90)
    print(out, img.size)


if __name__ == "__main__":
    main()
