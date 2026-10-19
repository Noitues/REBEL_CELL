"""HQ-LADDER-UI capture sheet (2x2): the ladder overview, an ACROSS hover, the mini-boss hover and the crown fight's label.
Usage: python tools/screens/hq_ladder_sheet.py --shots <dir with overview/across/minimb/crown .png> --out <jpg>"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

TILES = [
    ("overview", "1  Ladder overview: two towers, ACROSS bridges as raised arcs, rest / mini-boss stickers, FRONT chip"),
    ("across", "2  ACROSS option hovered: tag + room file show tower, move and the exact Bloom gap"),
    ("minimb", "3  Mini-boss room hovered (UP): its own name, sticker and gap"),
    ("crown", "4  The crown fight: address line reads BOSS: THE GENOME CORE"),
]


def font(size):
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tw, th = 960, 540
    sheet = Image.new("RGB", (tw * 2, (th + 22) * 2), (10, 12, 24))
    d = ImageDraw.Draw(sheet)
    f = font(14)
    for i, (name, label) in enumerate(TILES):
        path = os.path.join(a.shots, name + ".png")
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = (i % 2) * tw, (i // 2) * (th + 22)
        sheet.paste(im, (x, y + 22))
        d.text((x + 6, y + 3), label, fill=(240, 246, 255), font=f)
    sheet.save(a.out, quality=88)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
