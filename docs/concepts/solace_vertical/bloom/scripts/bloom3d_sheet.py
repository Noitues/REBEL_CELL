"""sheet_A3d.jpg: A Necrosis in 3D. Rows: street CREEPING / CLOSE / CATCHING; HQ overview CATCHING / decision CLOSE with the clean plates
beside them; raid 20 / 60 / 90 %; the gauge strip. 2560 px wide."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

import solace_lib as L

OUT = L.OUT
BS = "D:/rc_scratch/solace_v1/bloom3d"
GAP = 10


def tile(im, w):
    return im.resize((w, int(im.size[1] * w / im.size[0])), Image.LANCZOS)


def main():
    W = 2560
    pages = []
    cw = (W - 4 * GAP) // 3
    rows = [
        [("STREET  CREEPING  gap 2.5", "A3d_street_creeping.png"), ("STREET  CLOSE  gap 1.25", "A3d_street_close.png"), ("STREET  CATCHING  gap 0.6", "A3d_street_catching.png")],
        [("HQ overview  CATCHING  front floor 9 / 27", "A3d_hq_overview.png"), ("HQ decision  CLOSE  gap 1.25", "A3d_hq_decision.png"), ("HQ clean (v5 plates, for the value check)", None)],
        [("RAID  infection 20 %", "A3d_raid_20.png"), ("RAID  infection 60 %", "A3d_raid_60.png"), ("RAID  infection 90 %", "A3d_raid_90.png")],
    ]
    clean_hq = [os.path.join(BS, "clean_hq_overview.png"), os.path.join(BS, "clean_hq_decision.png")]
    ims = []
    y = 44
    sheet = Image.new("RGB", (W, 3200), (12, 7, 20))
    d = ImageDraw.Draw(sheet)
    d.text((GAP, 10), "SOLACE  THE BLOOM v2   A NECROSIS IN 3D   world material, Cycles (street, HQ) / Eevee + ink (raid)", font=L.font(22), fill=(255, 70, 150))
    for r, row in enumerate(rows):
        x = GAP
        h = 0
        for cap, fn in row:
            if fn is None:
                p = None
                for c in clean_hq:
                    if os.path.exists(c):
                        p = Image.open(c).convert("RGB")
                        break
                im = p
            else:
                pth = os.path.join(OUT, fn)
                im = Image.open(pth).convert("RGB") if os.path.exists(pth) else None
            if im is not None:
                t = tile(im, cw)
                sheet.paste(t, (x, y + 22))
                h = max(h, t.size[1])
            d.text((x + 2, y + 2), cap, font=L.font(16), fill=(235, 235, 245))
            x += cw + GAP
        y += 22 + h + GAP
    gp = os.path.join(OUT, "A3d_gauge.png")
    if os.path.exists(gp):
        g = Image.open(gp).convert("RGB")
        t = tile(g, 1900)
        d.text((GAP, y + 2), "TIDE gauge x5 bands (CRT) + CAUGHT binary bits (4 frames), 2D over the 3D CATCHING street frame", font=L.font(16), fill=(235, 235, 245))
        sheet.paste(t, (GAP, y + 22))
        y += 22 + t.size[1] + GAP
    sheet.crop((0, 0, W, y)).save(os.path.join(OUT, "sheet_A3d.jpg"), quality=88)
    print((W, y))


if __name__ == "__main__":
    main()
