"""Round 13 -> ../contact_sheet.jpg : the three sheets + four GIF frames."""
import os
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def main():
    W = 2000
    gl = fit(Image.open(os.path.join(OUT, "glyph_set.png")).convert("RGB"), W)
    ti = fit(Image.open(os.path.join(OUT, "tiers.png")).convert("RGB"), W // 2 - 5)
    st = fit(Image.open(os.path.join(OUT, "states.png")).convert("RGB"), W // 2 - 5)
    g = Image.open(os.path.join(OUT, "states_fx.gif"))
    frames = []
    for i in (0, 6, 12, 18):
        g.seek(i)
        frames.append(fit(g.convert("RGB"), W // 4 - 8))
    H = gl.height + max(ti.height, st.height) + frames[0].height + 30
    sheet = Image.new("RGB", (W, H), (8, 8, 12))
    sheet.paste(gl, (0, 0))
    y = gl.height + 10
    sheet.paste(ti, (0, y))
    sheet.paste(st, (W // 2 + 5, y))
    y += max(ti.height, st.height) + 10
    for i, f in enumerate(frames):
        sheet.paste(f, (i * (W // 4) + 4, y))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg", sheet.size)


if __name__ == "__main__":
    main()
