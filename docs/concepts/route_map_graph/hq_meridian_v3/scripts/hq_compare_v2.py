"""HQ compare v2: the five HQ OVERVIEWS after the 2026-10-15 review -> ../../hq_compare_v2.jpg (Halcyon, Meridian,
Solace, Orbital, Rebel Cell), each tile 1024 x 576 with its name, the v2 change and the value numbers; plates without
UI on a second row. Reads <hq>/H_overview_v2.png + plates/H_overview_v2_plate.png and D:/rc_scratch/hq_rev/values.json.

python hq_compare_v2.py
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
TILES = [("hq_halcyon", "HALCYON CIVIC", "the city right up to the plinth; the section cut"),
         ("hq_meridian", "MERIDIAN FREIGHT", "the ring route round all four walls; the shuttles"),
         ("hq_solace", "SOLACE BIOSYSTEMS", "lit city close round the towers; the plaza wash"),
         ("hq_orbital", "ORBITAL COMMONS", "the rocket + silo read: dark pad, doors, gantry"),
         ("hq_rebel_cell", "REBEL_CELL // DISPATCH", "the Tokyo alley canyon; MAINFRAME; the fist holo")]
TW, TH = 1024, 576
VALS = r"D:\rc_scratch\hq_rev\values.json"


def font(sz):
    for p in (os.path.join(BASE, "..", "..", "..", "assets", "fonts", "ShareTechMono-Regular.ttf"),
              r"C:\Windows\Fonts\consola.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main():
    vals = json.load(open(VALS)) if os.path.exists(VALS) else {}
    tiles = [(d, n, s) for (d, n, s) in TILES if os.path.exists(os.path.join(BASE, d, "H_overview_v2.png"))]
    W = TW * len(tiles) + 20 * (len(tiles) + 1)
    H = 2 * TH + 3 * 20 + 150
    sheet = Image.new("RGB", (W, H), (12, 10, 18))
    d = ImageDraw.Draw(sheet)
    d.text((20, 18), "HQ NETRUNS v2  //  the five HQ overviews after the review (with UI, then the plates)", font=font(34),
           fill=(240, 238, 232))
    for k, (dd, name, sub) in enumerate(tiles):
        x = 20 + k * (TW + 20)
        im = Image.open(os.path.join(BASE, dd, "H_overview_v2.png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
        sheet.paste(im, (x, 80))
        pp = os.path.join(BASE, dd, "plates", "H_overview_v2_plate.png")
        if os.path.exists(pp):
            sheet.paste(Image.open(pp).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, 100 + TH))
        d.text((x, 100 + 2 * TH + 10), name, font=font(28), fill=(255, 220, 160))
        d.text((x, 100 + 2 * TH + 46), sub, font=font(20), fill=(170, 182, 200))
        v = vals.get(dd, {}).get("H_overview")
        if v:
            txt = "median %.3f   <0.10 %.0f %%   >0.85 %.1f %%   landmark / bg %s" % (
                v["median"], 100 * v["under_010"], 100 * v["over_085"],
                ("%.2f" % v["ratio"]) if v.get("ratio") else "-")
            d.text((x, 100 + 2 * TH + 76), txt, font=font(19), fill=(150, 230, 170))
    out = os.path.join(BASE, "hq_compare_v2.jpg")
    sheet.save(out, quality=90)
    print("saved", out, len(tiles), "tiles")


if __name__ == "__main__":
    main()
