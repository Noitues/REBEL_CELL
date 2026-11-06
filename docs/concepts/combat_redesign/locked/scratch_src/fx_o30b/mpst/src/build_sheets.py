"""build_sheets.py: family sheets fx_<F>_<name>.png + timings_MPST.json from work/res_*.json and the strips."""
import sys, os, json, glob, textwrap
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import fx_eff as E
from fxlib import font, ME

OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
SW = 2000
BG = (12, 12, 18)
FAM = {
    'M': ('FX-M MOTION', 'motion', (255, 61, 168),
          'THINGS MOVE // stroboscopic print echoes + the arrowed outline (movement only)',
          ['Material: three echo copies of the thing that moves, 26 / 52 / 78 ms behind it (9 / 18 / 27 ms on the fast tower), tinted 25 % toward the mover\'s colour; on a turning disc or ring only where an echo differs from the frame (edges, icons, marks). Echoes exist only while it moves.',
           'Arrowed outline: an ink-cased 5 px stroke with an open V head (the board\'s own movement line). It draws ahead in the anticipate beat and is eaten by the mover.',
           'Who moves it decides the colour: PINK = the Cell\'s card at resolve (pencil yellow is the hover / preview form only); SILVER = the clock (the THIS TURN tape stock, with a white specular core); CORP COLOUR = the enemy wave (Solace lime, Meridian orange, graphite enamel on the neutral corp).',
           'Separation from the skins: no facets (WPAP cards), no paper inks or Ben-Day (spinner), no enamel fill (corp rings), no cyan (HUD). Silver sits in the gap at r 426 beside the tape, never on it.']),
    'P': ('FX-P PROTECT', 'protect', (241, 234, 214),
          'YOUR DEFENCE HOLDS // bone plate stock slams on: ink key line, pink double line, rivets, hard offset shadow, no glow',
          ['Material: bone card #F1EAD6 with a 3.4 px ink key line, a pink 1.6 px double line inside it, ink rivets, a hard offset shadow (3, 5) at 55 % ink. Flat tints only (pink 18 % for a block, SOAK 16 % for a soak). White spark ticks on impact, never a starburst (that is D) and never red on the plate (that is H).',
           'The plate always sits clear of the slice icon and the slice pips: shield plate r 171-203, the clamp is a frame round the wedge, the funnel apex stops at r 158.',
           'Separation from the skins: the spinner is xerox ink on paper with Ben-Day and a pink scissor halo; P is a separate cut card laid on top with its own shadow, bone not paper-white, and no texture.']),
    'S': ('FX-S SYSTEM', 'system', (160, 60, 255),
          'TRACE // stepped violet glitch bands, 6 px shears, R/B split, scanlines',
          ['Material: horizontal bands 4-11 px tall shear 6 px left or right, the red and blue channels split 3 px, a 35 % violet tint and dark scanlines on every second row. Steps of 33 ms, never smooth, new rows every step (no pixel flickers twice).',
           'Violet #A03CFF means Trace only (the card +Trace tab and the HUD pips). The settled pip is the HUD\'s own lit pip, cut from the same plate.']),
    'T': ('FX-T COMMIT', 'commit', (255, 61, 168),
          'PLAN BECOMES PAINT // pencil marks burn into pink paint along the path',
          ['Material: each pencil-yellow plan mark turns into the generator\'s own pink resolve mark along its length, ordered by geodesic distance from the route start (component by component), behind a white-hot front 2 frames deep; a pink ping rings the route end; then the rest of the board steps from preview to resolve.',
           'Both ends are the generator\'s plates (p2 and p3 of each skin); the effect is only the path between them. After it no yellow is left.'])}


def wrap(d, xy, s, f, fill, width_px):
    x, y = xy
    cw = f.getlength('n')
    n = max(20, int(width_px / cw))
    for line in textwrap.wrap(s, n):
        d.text((x, y), line, font=f, fill=fill)
        y += int(f.size * 1.32)
    return y


def gantt(spec, w=900, h=None):
    ph = spec['timing']['phases']
    tot = spec['timing']['total']
    rh = 22
    h = 34 + rh * len(ph) + 8
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    x0, x1 = 300, w - 20
    sx = lambda t: x0 + (x1 - x0) * t / tot
    f = font('mono', 13)
    for t in range(0, tot + 1, 100):
        d.line([(sx(t), 22), (sx(t), h - 6)], fill=(46, 46, 60), width=1)
        if t % 200 == 0:
            d.text((sx(t) - 10, 4), '%d' % t, font=f, fill=(150, 150, 170))
    for i, (nm, a, b, ease) in enumerate(ph):
        y = 30 + i * rh
        d.text((8, y + 2), nm[:40], font=f, fill=(220, 220, 232))
        col = (255, 61, 168) if spec['fam'] in 'MT' else ((241, 234, 214) if spec['fam'] == 'P' else (160, 60, 255))
        if spec['id'] in ('fx_rings_step', 'fx_hold'):
            col = (206, 212, 222)
        d.rectangle([sx(a), y + 3, max(sx(a) + 2, sx(b)), y + rh - 4], fill=col)
        d.text((min(sx(b) + 6, w - 150), y + 2), ease, font=font('mono', 12), fill=(170, 176, 196))
    return im


def flash_panel(results, w=900):
    h = 30 + 92 * len(results)
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    f = font('mono', 13)
    d.text((8, 6), 'FLASH CHECK, 60 fps, per skin: mean relative luminance of the effect footprint (curve, full motion pink, reduce grey)', font=f, fill=(220, 220, 232))
    for i, r in enumerate(results):
        y = 30 + i * 92
        fc, fr = r['flash'], r['flash_reduce']
        d.text((8, y), r['skin'].upper(), font=font('anton', 18), fill=(255, 214, 0))
        txt = ['footprint %d px, %d frames' % (fc['footprint_px'], fc['frames']),
               'full: %d flash(es), max %d / s, area swing up %.0f %% down %.0f %%' % (fc['flashes'], fc['max_flashes_per_s'], 100 * fc['max_area_swing_up'], 100 * fc['max_area_swing_down']),
               'reduce: %d flash(es), max %d / s' % (fr['flashes'], fr['max_flashes_per_s']),
               'max mean step %.3f / frame, range %.3f' % (fc['max_mean_step'], fc['mean_range']),
               'PASS (<= 3 / s)' if fc['passed'] and fr['passed'] else 'FAIL']
        for k, s_ in enumerate(txt):
            d.text((110, y + k * 16), s_, font=f, fill=(120, 230, 140) if s_.startswith('PASS') else ((255, 90, 80) if s_ == 'FAIL' else (200, 204, 220)))
        cx0, cx1, cy0, cy1 = 520, w - 12, y + 4, y + 84
        d.rectangle([cx0, cy0, cx1, cy1], outline=(60, 60, 76))
        for curve, col in ((fr['mean_curve'], (150, 150, 160)), (fc['mean_curve'], (255, 61, 168))):
            c = np.array(curve)
            allc = np.array(fc['mean_curve'] + fr['mean_curve'])
            lo, hi = allc.min(), allc.max()
            if hi - lo < 0.02:
                mid = (hi + lo) / 2
                lo, hi = mid - 0.01, mid + 0.01
            pts = [(cx0 + (cx1 - cx0) * j / max(1, len(c) - 1), cy1 - 4 - (cy1 - cy0 - 8) * (v - lo) / (hi - lo)) for j, v in enumerate(c)]
            d.line(pts, fill=col, width=2)
        for fr_ in fc['flash_frames']:
            xx = cx0 + (cx1 - cx0) * fr_ / max(1, len(fc['mean_curve']) - 1)
            d.line([(xx, cy0), (xx, cy1)], fill=(255, 214, 0), width=1)
        d.text((cx0 + 4, cy0 + 2), 'L %.3f-%.3f' % (min(fc['mean_curve']), max(fc['mean_curve'])), font=font('mono', 11), fill=(150, 150, 170))
    return im


def fit(im, w):
    if im.width <= w:
        return im
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def main():
    timings = {}
    for F, (name, word, col, tag, rules) in FAM.items():
        specs = [s for s in E.FX.values() if s['fam'] == F]
        blocks = []
        for s in specs:
            res = []
            for sk in s['skins']:
                fp = ME + 'work/res_%s_%s.json' % (s['id'], sk)
                if os.path.exists(fp):
                    res.append(json.load(open(fp)))
            timings[s['id']] = dict(family=F, title=s['title'], total_ms=s['timing']['total'],
                                    phases=[dict(name=p[0], start_ms=p[1], end_ms=p[2], easing=p[3]) for p in s['timing']['phases']],
                                    keyframes_ms=[k[0] for k in s['keys']], skins=s['skins'], reduce_motion=s['reduce_note'],
                                    flash_check={r['skin']: dict(full=dict((k, r['flash'][k]) for k in ('footprint_px', 'frames', 'flashes', 'flash_frames', 'max_flashes_per_s', 'max_area_swing_up', 'max_area_swing_down', 'max_mean_step', 'mean_range', 'passed')),
                                                                 reduce=dict((k, r['flash_reduce'][k]) for k in ('flashes', 'max_flashes_per_s', 'passed'))) for r in res},
                                    strips={r['skin']: 'strips/' + os.path.basename(r['strip']) for r in res})
            # block image
            g = gantt(s)
            fpn = flash_panel(res) if res else Image.new('RGB', (900, 40), (20, 20, 28))
            tmp = Image.new('RGB', (SW, 4000), BG)
            d = ImageDraw.Draw(tmp)
            d.rectangle([0, 0, 8, 60], fill=col)
            d.text((22, 0), s['id'], font=font('mono', 30), fill=(255, 255, 255))
            d.text((22 + font('mono', 30).getlength(s['id']) + 20, 4), s['title'].upper(), font=font('anton', 30), fill=col)
            d.text((SW - 520, 10), '%s  |  %s' % (name, ', '.join(s['skins'])), font=font('mono', 16), fill=(170, 176, 196))
            y = 50
            fb = font('plex', 19)
            y = wrap(d, (22, y), 'STILL: ' + s['still'], fb, (232, 232, 240), SW - 980)
            y = wrap(d, (22, y + 4), 'SOURCE: ' + s['src'], font('plex', 17), (160, 166, 186), SW - 980)
            y = wrap(d, (22, y + 4), 'STYLE MUST KEEP: ' + s['keep'], font('plex', 18), (255, 214, 0), SW - 980)
            y = wrap(d, (22, y + 4), 'REDUCE MOTION: ' + s['reduce_note'], font('plex', 17), (255, 214, 0), SW - 980)
            y = wrap(d, (22, y + 4), 'NOTE: ' + s['notes'], font('plex', 17), (160, 166, 186), SW - 980)
            tmp.paste(g, (SW - 930, 50))
            tmp.paste(fpn, (SW - 930, 50 + g.height + 8))
            y = max(y, 50 + g.height + 8 + fpn.height) + 14
            stp = {r['skin']: Image.open(r['strip']).convert('RGB') for r in res}
            if 'neutral' in stp:
                im = fit(stp['neutral'], SW - 20)
                tmp.paste(im, (10, y))
                y += im.height + 10
            corp = [stp[k] for k in ('solace', 'meridian') if k in stp]
            if corp:
                cw = (SW - 30) // 2
                ims = [fit(c, cw) for c in corp]
                for i, im in enumerate(ims):
                    tmp.paste(im, (10 + i * (cw + 10), y))
                y += max(i_.height for i_ in ims) + 10
            blocks.append(tmp.crop((0, 0, SW, y + 16)))
        # family header
        hdr = Image.new('RGB', (SW, 4000), BG)
        d = ImageDraw.Draw(hdr)
        d.rectangle([14, 16, 24, 110], fill=col)
        d.text((40, 6), name, font=font('anton', 64), fill=col)
        d.text((40, 84), tag, font=font('mono', 22), fill=(230, 230, 240))
        d.text((SW - 700, 14), 'combat redesign / locked board / effects step 4 / %d effect%s' % (len(specs), '' if len(specs) == 1 else 's'), font=font('mono', 16), fill=(150, 150, 170))
        y = 130
        for r_ in rules:
            y = wrap(d, (40, y), r_, font('plex', 19), (210, 212, 226), SW - 80) + 4
        d.text((40, y + 6), 'Board: the final locked plates (locked/final, state E10). Strips: keyframes with ms; the yellow-framed tile is the reduce-motion form. Flash check method in NOTES_MPST.md.',
               font=font('mono', 15), fill=(150, 150, 170))
        hdr = hdr.crop((0, 0, SW, y + 36))
        Ht = hdr.height + sum(b.height + 6 for b in blocks)
        sheet = Image.new('RGB', (SW, Ht), BG)
        sheet.paste(hdr, (0, 0))
        yy = hdr.height
        for b in blocks:
            ImageDraw.Draw(sheet).line([(0, yy + 2), (SW, yy + 2)], fill=(44, 44, 58), width=2)
            sheet.paste(b, (0, yy + 6))
            yy += b.height + 6
        fp = OUTD + 'fx_%s_%s.png' % (F, word)
        sheet.quantize(colors=208, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(fp, optimize=True)
        print('sheet', fp, sheet.size, os.path.getsize(fp))
    json.dump(dict(scope='M motion, P protect, S system, T commit (roadmap step 4, locked board)', fps=60,
                   flash_method='see NOTES_MPST.md: footprint = pixels whose WCAG relative luminance moves > 0.02 from frame 0; per-pixel extremum tracker logs a swing at >= 0.10; a region event = >= 25 % of the footprint swinging the same way inside 100 ms; a flash = two opposite region events; pass = <= 3 flashes in any 1 s window',
                   effects=timings), open(OUTD + 'timings_MPST.json', 'w'), indent=1)
    print('timings ok')


if __name__ == '__main__':
    main()
