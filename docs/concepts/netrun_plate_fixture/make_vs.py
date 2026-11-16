"""Netrun plate fixture: the Godot render beside the golden plate it targets, same 16:9 aspect.

Plate: docs/concepts/golden_plates/hq_rebel_cell_decision.png. Render: tools/b_capture/netrun_plate_fixture.tscn
(art clone, branch art/netrun-street-integrated), its plate_view.png.

Run: python make_vs.py <render png> <NN> [note]   (writes vs_plate_NN.jpg here)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PLATE = os.path.join(os.path.dirname(HERE), 'golden_plates', 'hq_rebel_cell_decision.png')
FONTS = 'D:/rc_art/street_integrated/assets/fonts/'
BG = (16, 16, 22)
HI = (238, 240, 246)
MID = (160, 166, 182)


def font(name, size):
    p = FONTS + name
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()


def values(im):
    """The plate values (golden_plates INDEX 12.1): median luminance, share under 0.10, share over 0.85 (Rec. 709 luma of sRGB)."""
    g = im.convert('RGB').resize((640, 360), Image.BILINEAR)
    px = list(g.getdata())
    lum = sorted((0.2126 * r + 0.7152 * gg + 0.0722 * b) / 255.0 for r, gg, b in px)
    n = len(lum)
    return lum[n // 2], sum(1 for v in lum if v < 0.10) / n, sum(1 for v in lum if v > 0.85) / n


def main():
    render, nn = sys.argv[1], sys.argv[2]
    note = sys.argv[3] if len(sys.argv) > 3 else ''
    w, h, pad, top = 1280, 720, 16, 96
    sheet = Image.new('RGB', (pad * 3 + w * 2, top + h + pad + 40), BG)
    d = ImageDraw.Draw(sheet)
    fa, fs = font('Anton-Regular.ttf', 30), font('IBMPlexSansCondensed-Medium.ttf', 18)
    d.text((pad, 10), 'Netrun street fixture vs golden plate  (%s)' % nn, font=fa, fill=HI)
    d.text((pad, 54), note, font=fs, fill=MID)
    for i, (path, title) in enumerate([(PLATE, 'TARGET  golden_plates/hq_rebel_cell_decision.png'),
                                       (render, 'GODOT  netrun_plate_fixture: plate_view.png')]):
        src = Image.open(path).convert('RGB')
        med, under, over = values(src)
        im = src.resize((w, h), Image.LANCZOS)
        x = pad + i * (w + pad)
        sheet.paste(im, (x, top))
        d.text((x, top + h + 8), '%s   median %.3f / under 0.10 %.1f %% / over 0.85 %.1f %%' % (title, med, under * 100, over * 100), font=fs, fill=HI)
        print(title, 'median %.4f under %.4f over %.4f' % (med, under, over))
    out = os.path.join(HERE, 'vs_plate_%s.jpg' % nn)
    sheet.save(out, quality=88)
    print('ok', out)


if __name__ == '__main__':
    main()
