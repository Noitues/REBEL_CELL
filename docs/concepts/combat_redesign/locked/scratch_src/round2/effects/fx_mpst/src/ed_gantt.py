"""ed_gantt.py: one-off edit of mp_sheets.py (seen at 1x on the published sheets): the phase names were cut at 40 characters and the
easing label ran over the bar when the bar ends near 600 ms; the header 'Board:' line ran off the right edge. Names now wrap in the
label column, the easing label goes left of the bar when it does not fit on the right, and the header line wraps."""
P = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/mp_sheets.py'
s = open(P, encoding='utf-8').read()
a = s[s.index('def gantt(spec, w=900):'):s.index('def flash_panel(')]
b = '''def gantt(spec, w=900):
    ph = spec['timing']['phases']
    tot = E.CAP_MS
    rph = spec['reduce_phases']
    f = font('mono', 13)
    fe = font('mono', 12)
    x0, x1 = 340, w - 20
    ncol = int((x0 - 16) / f.getlength('n'))
    rows = [(textwrap.wrap(nm, ncol), a_, b_, e_, False) for nm, a_, b_, e_ in ph] + [(['REDUCE MOTION'], None, None, None, True)] + \
           [(textwrap.wrap(nm, ncol), a_, b_, e_, True) for nm, a_, b_, e_ in rph]
    rhs = [max(22, 15 * len(r[0]) + 7) for r in rows]
    h = 30 + sum(rhs) + 26
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    sx = lambda t: x0 + (x1 - x0) * t / tot
    for t in range(0, tot + 1, 100):
        d.line([(sx(t), 22), (sx(t), h - 6)], fill=(46, 46, 60), width=1)
        d.text((sx(t) - 10, 4), '%d' % t, font=f, fill=(150, 150, 170))
    d.line([(sx(tot), 22), (sx(tot), h - 6)], fill=(255, 90, 80), width=2)
    d.text((sx(tot) - 120, h - 20), 'T2 cap 600 ms', font=fe, fill=(255, 90, 80))
    col = fam_col(spec)
    y = 30
    for (lines, a_, b_, e_, red), rh in zip(rows, rhs):
        for k, ln in enumerate(lines):
            d.text((8, y + 2 + 15 * k), ln, font=f, fill=(255, 214, 0) if red else (220, 220, 232))
        if a_ is not None:
            ym = y + rh / 2
            if red:
                d.rectangle([sx(a_), ym - 4, max(sx(a_) + 2, sx(b_)), ym + 4], fill=(150, 150, 160))
            else:
                d.rectangle([sx(a_), ym - 7, max(sx(a_) + 2, sx(b_)), ym + 7], fill=col)
                el = fe.getlength(e_)
                ex = sx(b_) + 6 if sx(b_) + 6 + el <= x1 - 4 else sx(a_) - 6 - el
                if ex < x0:
                    ex = None
                if ex is not None:
                    d.text((ex, ym - 8), e_, font=fe, fill=(170, 176, 196))
        y += rh
    return im


'''
s = s.replace(a, b)
a2 = """        d.text((40, y + 6), 'Board: the rebuilt board (2026-11-03 rebuild, gate 1), base plates rendered from corp/src with the plates\' own capture hooks (matches locked/final: max 1-3 / 255). Strips: keyframes with ms; the yellow-framed tile is reduce motion. Every total <= 600 ms (VfxTier T2, no override). Flash method in NOTES_MPST.md.',
               font=font('mono', 14), fill=(150, 150, 170))
        hdr = hdr.crop((0, 0, SW, y + 36))"""
b2 = """        y = wrap(d, (40, y + 6), 'Board: the rebuilt board (2026-11-03 rebuild, gate 1), base plates rendered from corp/src with the plates\' own capture hooks (matches locked/final: max 1-3 / 255). Strips: keyframes with ms; the yellow-framed tile is reduce motion. Every total <= 600 ms (VfxTier T2, no override). Flash method in NOTES_MPST.md.',
                 font('mono', 14), (150, 150, 170), SW - 80)
        hdr = hdr.crop((0, 0, SW, y + 16))"""
a2 = b2 = ""
s = s.replace(a2, b2)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
