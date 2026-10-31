"""Round 16 -> ../contact_sheet.jpg : glyph set + changes, tiers, firewall screen."""
import os
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def main():
    W = 2000
    gl = fit(Image.open(os.path.join(OUT, "glyph_set.png")).convert("RGB"), W // 2 - 5)
    gc = fit(Image.open(os.path.join(OUT, "glyph_changes.png")).convert("RGB"), W // 2 - 5)
    fw = fit(Image.open(os.path.join(OUT, "firewall_screen.png")).convert("RGB"), W // 2 - 5)
    ti = fit(Image.open(os.path.join(OUT, "tiers.png")).convert("RGB"), W // 2 - 5)
    right_h = gc.height + 10 + fw.height
    top = max(gl.height, right_h)
    H = top + 10 + ti.height
    sheet = Image.new("RGB", (W, H), (8, 8, 12))
    sheet.paste(gl, (0, 0))
    sheet.paste(gc, (W // 2 + 5, 0))
    sheet.paste(fw, (W // 2 + 5, gc.height + 10))
    sheet.paste(ti, (0, top + 10))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg", sheet.size)


if __name__ == "__main__":
    main()
