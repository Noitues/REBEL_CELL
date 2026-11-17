"""Game netrun screen vs golden plate: the plate beside the real game's netrun screen captures (street_integrated_capture,
branch art/netrun-street-integrated, RC3 gs.street_run() plate view), one row per campaign seed.

Each label gives the plate values (make_vs.values: median luminance, share under 0.10, share over 0.85) twice: for the whole
frame, and for the scene with the game's UI chrome cropped out (the top bar and NETRUN header, CHROME_TOP px, and the legend
strip, CHROME_BOT px, at a 720-tall capture; scaled with the frame's height). The plate has no chrome: one value set.

Run: python make_game_vs.py <out.jpg> <seed>:<land.png>,<mid.png>,<ug.png> [<seed>:...]
"""
import sys

from PIL import Image, ImageDraw

from make_vs import PLATE, BG, HI, MID, font, values

W, H, PAD, TOP, LAB = 760, 428, 12, 70, 52
CHROME_TOP, CHROME_BOT, CHROME_REF_H = 120, 40, 720


def scene(im):
    """`im` with the game's UI chrome cropped off (top bar + header, legend strip)."""
    k = im.height / CHROME_REF_H
    return im.crop((0, round(CHROME_TOP * k), im.width, im.height - round(CHROME_BOT * k)))


def fmt(v):
    med, under, over = v
    return 'median %.3f  <0.10 %.0f%%  >0.85 %.1f%%' % (med, under * 100, over * 100)


def main():
    out = sys.argv[1]
    rows = []
    for arg in sys.argv[2:]:
        seed, files = arg.split(':', 1)
        rows.append((seed, files.split(',')))
    cols = 4
    sheet = Image.new('RGB', (PAD + cols * (W + PAD), TOP + len(rows) * (H + LAB + PAD)), BG)
    d = ImageDraw.Draw(sheet)
    fa, fs = font('Anton-Regular.ttf', 28), font('IBMPlexSansCondensed-Medium.ttf', 16)
    d.text((PAD, 8), 'Game netrun screen (RC3 street run, plate view) vs golden plate', font=fa, fill=HI)
    d.text((PAD, 44), 'art/netrun-street-integrated; street_integrated_capture on the real game screen.  frame = whole capture;  '
           'scene = UI chrome cropped (top %d px, bottom %d px at %d tall)' % (CHROME_TOP, CHROME_BOT, CHROME_REF_H), font=fs, fill=MID)
    plate = Image.open(PLATE).convert('RGB')
    for r, (seed, files) in enumerate(rows):
        y = TOP + r * (H + LAB + PAD)
        names = ['seed %s  landing' % seed, 'seed %s  mid step' % seed, 'seed %s  underground rooms' % seed]
        items = [(plate, 'TARGET plate', None)] + [(Image.open(f).convert('RGB'), t, True) for f, t in zip(files, names)]
        for c, (im, title, game) in enumerate(items):
            x = PAD + c * (W + PAD)
            sheet.paste(im.resize((W, H), Image.LANCZOS), (x, y))
            if game:
                d.text((x, y + H + 4), '%s   frame %s' % (title, fmt(values(im))), font=fs, fill=HI)
                d.text((x, y + H + 24), 'scene  %s' % fmt(values(scene(im))), font=fs, fill=HI)
            else:
                d.text((x, y + H + 4), '%s   %s' % (title, fmt(values(im))), font=fs, fill=HI)
                d.text((x, y + H + 24), '(no UI chrome: frame = scene)', font=fs, fill=MID)
    sheet.save(out, quality=88)
    print('ok', out)


if __name__ == '__main__':
    main()
