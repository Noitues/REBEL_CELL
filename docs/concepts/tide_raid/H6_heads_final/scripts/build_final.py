"""heads_final.png: construction sheet, each head at 256 px, build geometry and hex palette."""
from common import *

METR = json.load(open(os.path.join(HERE, 'metrics.json')))
M44 = METR['44']
GEOM = {
    'D': ['spine: 23-pt S-wave, amplitude .27 u, wavelength 1.3 u (phase runs tail -> head)',
          'body: taper .22 u (tail) -> .32 u (neck), tail bead r .13 u',
          'head: circle r .35 u at the lead end; dot r .18 u at head + .05 u',
          'footprint 2.10 u long x ~.9 u: THIN, one stroke, no gaps',
          'direction: round head + eye-dot lead; the wave runs backward'],
    'N': ['hub: circle r .38 u at x -.45 (dot r .18 u inside), stub .35 x .40 u behind it',
          'horns x2: bezier (-.3,.3) (.3,.6) (.6,1.3) (1.1,.55), taper .28 -> .16 u',
          'centre thorn: x -.2 -> .55, taper .24 -> .16 u (tips .16 u = 3 px at 44 px)',
          'footprint 2.10 u: OPEN, 3 prongs and gaps, fill hull .46',
          'direction: hub trails, all three prongs open forward'],
    'E': ['ball: circle r .88 u, 8 spikes at 45 deg, width .30 u, knobs r .18 u',
          'lead spike (0 deg): reach 1.10 u, knob r .30 u; rear spike .94; others .98',
          'armour ring r .50 / .38 u round the dot (ink, cut at >= 40 px) = density',
          'dot r .18 u at x +.12: forward of centre',
          'footprint 1.79 u (.852 x N): SOLID; direction: lead spike + forward dot'],
    'X': ['shell: ellipse .74 x .56 u at x -.2, split line (cut at >= 40 px)',
          'head: circle r .36 u at x .58 (dot r .18 u), 2 antennae with knobs r .16 u',
          'antenna sweep +-.1 u in motion',
          'footprint 1.79 u (= E): mid weight, neutral grey, future type',
          'direction: head + antennae lead'],
}
CW, CH = 500, 470


def construction_cell(t):
    im = Image.new('RGBA', (CW, CH), (20, 14, 36, 255))
    d = ImageDraw.Draw(im)
    cx, cy = CW // 2, 236
    size = 256
    u = (size - 2 * size * OW_FRAC) / FOOT
    for g in range(-6, 7):
        d.line([(cx + g * 40, 40), (cx + g * 40, CH - 20)], fill=(30, 24, 52))
    for g in range(-5, 6):
        d.line([(10, cy + g * 40), (CW - 10, cy + g * 40)], fill=(30, 24, 52))
    d.line([(10, cy), (CW - 10, cy)], fill=(60, 50, 96))
    d.line([(cx, 40), (cx, CH - 20)], fill=(60, 50, 96))
    d.ellipse([cx - u * 1.05, cy - u * 1.05, cx + u * 1.05, cy + u * 1.05], outline=(60, 50, 96))
    ops = head(t)
    paste_head(im, ops, cx, cy, size, 0, t)
    d = ImageDraw.Draw(im)
    fw = FOOTS[t]
    d.rectangle([cx - fw / 2 * u, cy - fw / 2 * u, cx + fw / 2 * u, cy + fw / 2 * u], outline=(255, 255, 255, 70))
    d.text((cx + fw / 2 * u - 66, cy + fw / 2 * u + 3), f'{fw:.2f} u', font=F(FONT_M, 12), fill=(200, 200, 225))
    for k, p in ops:
        for x, y in p:
            if k == 'mot':
                continue
            px, py = cx + x * u, cy + y * u
            d.rectangle([px - 1.5, py - 1.5, px + 1.5, py + 1.5], outline=(120, 255, 200, 200) if k == 'add' else (255, 120, 120, 200))
    ay = cy + FOOT / 2 * u + 24
    d.line([(cx - 40, ay), (cx + 60, ay)], fill=(150, 150, 190), width=2)
    d.polygon([(cx + 60, ay), (cx + 50, ay - 6), (cx + 50, ay + 6)], fill=(150, 150, 190))
    d.text((cx + 70, ay - 7), 'travel', font=F(FONT_M, 12), fill=(150, 150, 190))
    d.text((10, 8), NAMES[t], font=F(FONT_M, 17), fill=HUE[t])
    return im


def swatch_row(t):
    fill = HUE[t]
    items = [('fill', fill), ('rim light', rim_lite(fill)), ('rim dark', rim_dark(fill)), ('ink/outline', INK), ('core dot', INK)]
    im = Image.new('RGB', (CW, 66), BG)
    d = ImageDraw.Draw(im)
    for i, (n, c) in enumerate(items):
        x = 8 + i * 98
        d.rectangle([x, 4, x + 90, 30], fill=c, outline=(200, 200, 220))
        d.text((x, 33), n, font=F(FONT_M, 12), fill=(200, 200, 225))
        d.text((x, 48), hexs(c), font=F(FONT_M, 13), fill=(255, 255, 255))
    return im


def metrics_block(t):
    im = Image.new('RGB', (CW, 120), BG)
    d = ImageDraw.Draw(im)
    o0 = RAW[t](0.0, 1.0)
    xs = [x for k, p in o0 if k == 'add' for x, y in p]
    ys = [y for k, p in o0 if k == 'add' for x, y in p]
    s = FOOTS[t] / max(max(xs) - min(xs), max(ys) - min(ys))
    adds = sum(1 for k, p in o0 if k == 'add')
    lines = ['primitives: %d silhouette parts + dot' % adds + (' + ring' if t == 'E' else '') + (' + split' if t == 'X' else ''),
             'normalise scale %.3f (build units -> footprint)' % s,
             'at 44 px: area %d px (outline in), colour fill %d px, hull fill %.2f' % (M44['area_' + t], M44['fillarea_' + t], M44['hullfill_' + t]),
             'pieces at 44 px: %d   bbox %d x %d px' % (M44['pieces_' + t], M44['bbox_' + t][0], M44['bbox_' + t][1]),
             'frame delta idle->travel: %.2f' % M44['motion_' + t]]
    for i, l in enumerate(lines):
        d.text((8, 4 + i * 18), l, font=F(FONT_M, 12), fill=(210, 215, 235))
    return im


def geom_block(t):
    im = Image.new('RGB', (CW, 112), BG)
    d = ImageDraw.Draw(im)
    for i, l in enumerate(GEOM[t]):
        d.text((8, 4 + i * 20), l, font=F(FONT_M, 11), fill=(235, 235, 250))
    return im


def main():
    W = CW * 4 + 50
    rows = []
    hd = Image.new('RGB', (W, 150), BG)
    d = ImageDraw.Draw(hd)
    d.text((20, 8), 'H6 BEAM HEADS, FINAL FAMILY  |  D drone, N netrunner, E enforcer, 4th beetle', font=F(FONT_T, 42), fill=(120, 230, 255))
    d.text((20, 64), 'ONE FAMILY CONTRACT: outline 7.5 % of size in ink 0E081C | corner radius .10 u (applied after the footprint scale) | core dot ink r .18 u in a round node on every head |', font=F(FONT_M, 14), fill=(235, 235, 250))
    d.text((20, 84), 'rim light top-left (+38 % to white) / bottom-right (x .66) in screen space | footprint N = D = 2.10 u, E = beetle = 1.79 u (E .852 x N, designer ruling) | 40-48 px at 1920, 27-32 px at 1280.', font=F(FONT_M, 14), fill=(235, 235, 250))
    d.text((20, 104), 'MASS RAMP by solidity, not size: D thin (one 0.22-0.32 u stroke) < beetle < N open (3 prongs, gaps) < E solid (full ball, armour ring, 8 short spikes).', font=F(FONT_M, 14), fill=(255, 220, 120))
    d.text((20, 124), 'direction: D head leads, N prongs open forward, E lead spike + forward dot, beetle head + antennae lead; the ribbon (chain / braid / chevrons / ticks) carries the rest.', font=F(FONT_M, 14), fill=(190, 200, 225))
    rows.append(hd)
    col = []
    for t in TYPES:
        c = Image.new('RGB', (CW, CH + 66 + 120 + 112), BG)
        c.paste(construction_cell(t).convert('RGB'), (0, 0))
        c.paste(swatch_row(t), (0, CH))
        c.paste(geom_block(t), (0, CH + 66))
        c.paste(metrics_block(t), (0, CH + 66 + 112))
        col.append(c)
    body = Image.new('RGB', (W, col[0].height), BG)
    for i, c in enumerate(col):
        body.paste(c, (i * (CW + 16), 0))
    rows.append(body)
    strip = Image.new('RGBA', (W, 260), BG + (255,))
    pl = crop(PLATE, 40, 745, W // 2 - 20, 250)
    strip.paste(pl, (0, 0))
    d = ImageDraw.Draw(strip)
    for i, t in enumerate(TYPES):
        paste_head(strip, head(t), 70 + i * 120, 80, CHOSEN, -26, t)
        paste_head(strip, head(t), 70 + i * 120, 170, CHOSEN, 0, t, fill=(255, 255, 255), shade=False)
    d.text((8, 6), 'lineup at %d px: city (up-right) and flat white silhouettes' % CHOSEN, font=F(FONT_M, 13), fill=(255, 255, 255))
    x0 = W // 2 + 20
    d.text((x0, 6), 'WEIGHT BY SOLIDITY at 44 px: bar = hull fill ratio of the colour fill', font=F(FONT_M, 13), fill=(130, 220, 255))
    for i, t in enumerate(TYPES):
        y = 40 + i * 52
        hf = M44['hullfill_' + t]
        d.text((x0, y), t, font=F(FONT_T, 30), fill=HUE[t])
        d.rectangle([x0 + 40, y + 4, x0 + 40 + hf * 500, y + 28], fill=HUE[t], outline=INK)
        d.text((x0 + 48 + hf * 500, y + 8), 'hull %.2f  fill %d px  footprint %.2f u' % (hf, M44['fillarea_' + t], FOOTS[t]), font=F(FONT_M, 13), fill=(235, 235, 250))
    rows.append(strip.convert('RGB'))
    out = stack(rows, W)
    out.save(os.path.join(OUT, 'heads_final.png'))
    print(out.size)


if __name__ == '__main__':
    main()
