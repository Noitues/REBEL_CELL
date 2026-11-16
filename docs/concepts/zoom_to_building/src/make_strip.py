"""Zoom to an exact building (Campaign B, designer 2026-11-16): the review sheet from a capture run of
tools/b_capture/zoom_to_lot_capture.tscn (art clone, branch art/zoom-to-building).

Run: python src/make_strip.py <capture dir> [title line]   (from docs/concepts/zoom_to_building)
Reads strip_*.png (city -> street, in order), final_lot*.png (the final street at more lots) and log.txt (ZOOMTO lines),
writes zoom_strip.jpg here. Solace only.
"""
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = 'D:/rc_art/zoom_building/assets/fonts/'
BG = (16, 16, 22)
HI = (238, 240, 246)
MID = (160, 166, 182)
PINK = (255, 92, 178)
BAND = ['City', 'District', 'Near', 'Street', 'Close']


def font(name, size):
    p = FONTS + name
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()


def main():
    src = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else 'Zoom to an exact building: city to street, the Solace HQ lot'
    log = open(os.path.join(src, 'log.txt'), encoding='utf-8', errors='replace').read()
    strips = sorted(glob.glob(os.path.join(src, 'strip_*.png')))
    finals = sorted(glob.glob(os.path.join(src, 'final_lot*.png')))
    info = {int(m.group(1)): (float(m.group(2)), float(m.group(3)), int(m.group(4)))
            for m in re.finditer(r'ZOOMTO strip (\d+) w=([\d.]+) ppb=([\d.]+) band=(\d+)', log)}
    lot = re.search(r'ZOOMTO lot=(\S+ \S+) face=(\S+ \S+)', log)
    flines = re.findall(r'ZOOMTO final lot=(\S+ \S+) face=(\S+ \S+)', log)
    tw, th, pad, cap = 600, 338, 14, 46
    cols = 3
    rows_s = (len(strips) + cols - 1) // cols
    fw, fh = 900, 506
    H = 90 + rows_s * (th + cap + pad) + (fh + cap + pad if finals else 0) + 20
    W = max(cols * (tw + pad) + pad, len(finals) * (fw + pad) + pad + (fw + pad if strips else 0))
    sh = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sh)
    fa, fs = font('Anton-Regular.ttf', 32), font('ShareTechMono-Regular.ttf', 16)
    d.text((pad, 12), title, font=fa, fill=HI)
    sub = 'lot %s, frontage face %s; frames at even steps of the path (push on the lot, then the dolly); band = CityZoomRules.band_of(focus ppb)' % (
        lot.group(1) if lot else '?', lot.group(2) if lot else '?')
    d.text((pad, 56), sub, font=fs, fill=MID)
    y0 = 90
    for k, p in enumerate(strips):
        im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
        x = pad + (k % cols) * (tw + pad)
        y = y0 + (k // cols) * (th + cap + pad)
        sh.paste(im, (x, y))
        w, ppb, b = info.get(k, (0.0, 0.0, 0))
        d.text((x, y + th + 6), 'frame %d   w %.2f   %.1f px/BU   %s band' % (k, w, ppb, BAND[min(b, 4)]), font=fs, fill=HI)
    y = y0 + rows_s * (th + cap + pad)
    if finals:
        last = Image.open(strips[-1]).convert('RGB').resize((fw, fh), Image.LANCZOS) if strips else None
        x = pad
        if last is not None:
            sh.paste(last, (x, y))
            d.text((x, y + fh + 6), 'final street, lot %s' % (lot.group(1) if lot else '?'), font=fs, fill=PINK)
            x += fw + pad
        for i, p in enumerate(finals):
            im = Image.open(p).convert('RGB').resize((fw, fh), Image.LANCZOS)
            sh.paste(im, (x, y))
            fl = flines[i] if i < len(flines) else ('?', '?')
            d.text((x, y + fh + 6), 'final street, lot %s (face %s)' % fl, font=fs, fill=PINK)
            x += fw + pad
    out = os.path.join(HERE, 'zoom_strip.jpg')
    sh.save(out, quality=90)
    print('ok', out)


if __name__ == '__main__':
    main()
