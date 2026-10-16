"""HQ compare: the five HQ OVERVIEWS side by side -> ../../hq_compare.jpg (Halcyon if its overview exists, then
Meridian, Solace, Orbital, Rebel Cell), each tile 1024 x 576 with its name; plates without UI on a second row.

python hq_compare.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
TILES = [("hq_halcyon", "HALCYON CIVIC", "the helix pyramid, the eye"),
         ("hq_meridian", "MERIDIAN FREIGHT", "the container fortress, the yard cycle"),
         ("hq_solace", "SOLACE BIOSYSTEMS", "the twin helix towers, the ladder"),
         ("hq_orbital", "ORBITAL COMMONS", "the launch ring, the retarget cycle"),
         ("hq_rebel_cell", "REBEL_CELL // DISPATCH", "the red fist, sync strike (option A)")]
TW, TH = 1024, 576


def font(sz):
    for p in (os.path.join(BASE, "..", "..", "..", "assets", "fonts", "ShareTechMono-Regular.ttf"),
              r"C:\Windows\Fonts\consola.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main():
    tiles = [(d, n, s) for (d, n, s) in TILES if os.path.exists(os.path.join(BASE, d, "H_overview.png"))]
    W = TW * len(tiles) + 20 * (len(tiles) + 1)
    H = 2 * TH + 3 * 20 + 120
    sheet = Image.new("RGB", (W, H), (12, 10, 18))
    d = ImageDraw.Draw(sheet)
    d.text((20, 18), "HQ NETRUNS  //  the five HQ overviews (with UI, then the plates)", font=font(34), fill=(240, 238, 232))
    for k, (dd, name, sub) in enumerate(tiles):
        x = 20 + k * (TW + 20)
        im = Image.open(os.path.join(BASE, dd, "H_overview.png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
        sheet.paste(im, (x, 80))
        pp = os.path.join(BASE, dd, "plates", "H_overview_plate.png")
        if os.path.exists(pp):
            sheet.paste(Image.open(pp).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, 100 + TH))
        d.text((x, 100 + 2 * TH + 10), name, font=font(28), fill=(255, 220, 160))
        d.text((x, 100 + 2 * TH + 46), sub, font=font(20), fill=(170, 182, 200))
    out = os.path.join(BASE, "hq_compare.jpg")
    sheet.save(out, quality=90)
    print("saved", out, len(tiles), "tiles")


if __name__ == "__main__":
    main()
