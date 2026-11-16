"""Zoom to an exact building on RC1b (Campaign B, designer 2026-11-16): the review sheet from a game capture of
tools/b_capture/zoom_to_lot_capture.tscn (art clone, branch art/zoom-to-building on port-campaign-b): the netrun street's
zoom from the city view to the in-street pose (strip_*.png), then the landing with the rooms (final_1) and the next
steps (final_2, final_3), each on the rules' room lot of the campaign's own city. Solace only.

Run: python src/make_strip_rc1.py <capture dir> [probe dir]   (from docs/concepts/zoom_to_building)
Reads strip_*.png, final_*.png and log.txt (ZOOMTO lines); with a probe dir also probe_street.png (art's lot pose at
(-47, -26), city 7) with the building corners marked by CityIsoCamera.project (pink) and Camera3D.unproject_position
(cyan). Writes zoom_strip_rc1.jpg here.
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
CYAN = (80, 230, 255)
BAND = ['City', 'District', 'Near', 'Street', 'Close']
VEC = r'\(([-\d.e]+), ([-\d.e]+)\)'


def font(name, size):
    p = FONTS + name
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()


def main():
    src = sys.argv[1]
    probe = sys.argv[2] if len(sys.argv) > 2 else None
    log = open(os.path.join(src, 'log.txt'), encoding='utf-8', errors='replace').read()
    strips = sorted(glob.glob(os.path.join(src, 'strip_*.png')))
    finals = sorted(glob.glob(os.path.join(src, 'final_*.png')))
    info = {int(m.group(1)): (float(m.group(2)), float(m.group(3)), int(m.group(4)))
            for m in re.finditer(r'ZOOMTO strip (\d+) w=([\d.]+) ppb=([\d.]+) band=(\d+)', log)}
    fin = {int(m.group(1)): (m.group(2), m.group(3), m.group(4))
           for m in re.finditer(r'ZOOMTO final_(\d+) in_street=(\w+) zoom_room=(\d+) lot=(\(\S+ \S+\))', log)}
    errs = {}
    for blk in re.split(r'(?=ZOOMTO final_)', log):
        m = re.match(r'ZOOMTO final_(\d+)', blk)
        if m:
            e = [(float(a), float(b)) for a, b in re.findall(r'err_iso=([\d.]+) px err_rect=([-\d.]+) px', blk)]
            errs[int(m.group(1))] = e
    seed = re.search(r'ZOOMTO seed=(\d+) city_seed=(-?\d+)', log)
    tw, th, pad, cap = 600, 338, 14, 30
    fw, fh = 600, 338
    cols = 3
    rows_s = (len(strips) + cols - 1) // cols
    W = cols * (tw + pad) + pad
    H = 96 + rows_s * (th + cap + pad) + ((fh + cap * 2 + pad) if finals else 0) + ((fh + cap * 2 + pad) if probe else 0) + 10
    sh = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sh)
    fa, fs = font('Anton-Regular.ttf', 30), font('ShareTechMono-Regular.ttf', 15)
    d.text((pad, 10), 'Netrun street on RC1b: zoom from the city to the exact building, rooms on landing', font=fa, fill=HI)
    d.text((pad, 54), 'campaign seed %s, city seed %s (the campaign\'s own city), Solace only; rooms = the rules\' room lots on drawn buildings;'
           ' frames at even steps of the path (push, then dolly to the in-street pose)' % (seed.group(1) if seed else '?', seed.group(2) if seed else '?'),
           font=fs, fill=MID)
    y0 = 90
    for k, p in enumerate(strips):
        im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
        x = pad + (k % cols) * (tw + pad)
        y = y0 + (k // cols) * (th + cap + pad)
        sh.paste(im, (x, y))
        w, ppb, b = info.get(k, (0.0, 0.0, 0))
        d.text((x, y + th + 6), 'frame %d   w %.2f   %.1f px/BU   %s band' % (k, w, ppb, BAND[min(b, 4)]), font=fs, fill=HI)
    y = y0 + rows_s * (th + cap + pad)
    for i, p in enumerate(finals[:cols]):
        im = Image.open(p).convert('RGB').resize((fw, fh), Image.LANCZOS)
        x = pad + i * (fw + pad)
        sh.paste(im, (x, y))
        f = fin.get(i + 1, ('?', '?', '?'))
        e = errs.get(i + 1, [])
        d.text((x, y + fh + 6), 'final %d: %s room %s on lot %s' % (i + 1, 'landed, rooms shown;' if i == 0 else 'next step;', f[1], f[2]), font=fs, fill=PINK)
        if e:
            d.text((x, y + fh + 24), 'room_rect vs live Camera3D: max %.1f px (project: max %.1f px)' % (max(b for _, b in e), max(a for a, _ in e)), font=fs, fill=MID)
    if probe and os.path.exists(os.path.join(probe, 'probe_street.png')):
        y += fh + cap * 2 + pad
        plog = open(os.path.join(probe, 'log.txt'), encoding='utf-8', errors='replace').read()
        for j, name in enumerate(['probe_lot.png', 'probe_street.png']):
            pth = os.path.join(probe, name)
            if not os.path.exists(pth):
                continue
            im = Image.open(pth).convert('RGB')
            sx, sy = fw / im.width, fh / im.height
            im = im.resize((fw, fh), Image.LANCZOS)
            dd = ImageDraw.Draw(im)
            if name == 'probe_street.png':
                for m in re.finditer(r'ZOOMTO probe corner iso=' + VEC + ' live=' + VEC, plog):
                    for (cx, cy), col in (((float(m.group(1)), float(m.group(2))), PINK), ((float(m.group(3)), float(m.group(4))), CYAN)):
                        px, py = cx * sx, cy * sy
                        dd.ellipse((px - 5, py - 5, px + 5, py + 5), outline=col, width=2)
            x = pad + j * (fw + pad)
            sh.paste(im, (x, y))
            d.text((x, y + fh + 6), 'lot (-47, -26), city 7: ' + ('top-down' if j == 0 else 'art\'s lot pose; corners: pink project, cyan Camera3D'), font=fs, fill=HI)
        pm = re.search(r'ZOOMTO probe prism \d+ (.*)', plog)
        if pm:
            txt = pm.group(1)
            x = pad + 2 * (fw + pad)
            for li, part in enumerate(re.findall(r'\S+=\S+', txt)):
                d.text((x, y + li * 20), part, font=fs, fill=MID)
    out = os.path.join(HERE, 'zoom_strip_rc1.jpg')
    sh.save(out, quality=90)
    print('ok', out)


if __name__ == '__main__':
    main()
