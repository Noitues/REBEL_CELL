"""ck_patch3.py : hv_checks.py -> the reference strokes drawn as disc unions (the way wax_stroke draws since 2026-11-04) and the pencil widths
measured on the coverage (Pv__) when the plate saved it"""
import sys, io
sys.dont_write_bytecode = True
p = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/src/hv_checks.py'
s = io.open(p, encoding='utf-8').read()
old_ref = s[s.index('def _ref_widths():'):s.index('REF_W = {}')]
new_ref = '''def _ref_widths():
    """the estimator on reference strokes drawn the way wax_stroke draws and records them (a union of discs at 2x, BOX to 1x; the mask at
    >= 50 %, the width integrated on the coverage): a ring and two straight strokes at 7 px (wax), 13 px (L6 with ink), 3 px (L5 edge) and
    7.5 px (L5 with keyline)"""
    from PIL import ImageDraw as _D
    out = {}
    for nm, w in (('L6_wax', 7.0), ('L6_all', 13.0), ('L5_wax', 3.0), ('L5_all', 7.5)):
        im = Image.new('L', (520, 260), 0)
        d = _D.Draw(im)
        q = w - 0.5                                   # 2x radius w, bbox r - 0.5 (hv_core._stamp)
        paths = [[(130 + 90 * math.cos(t), 130 + 70 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 400)],
                 [(260 + 230 * f, 30 + 40 * f) for f in np.linspace(0, 1, 400)], [(280 + 220 * f, 210 - 30 * f) for f in np.linspace(0, 1, 400)]]
        for path in paths:
            for x, y in path:
                d.ellipse([2 * x - q, 2 * y - q, 2 * x + q, 2 * y + q], fill=255)
        c = np.asarray(im.resize((260, 130), Image.BOX)).astype(np.float32) / 255.0
        out[nm] = stroke_width(c >= 0.5, cov=c)
    return out


'''
s = s.replace(old_ref, new_ref)
old = "    r = dict(mask=dict(L6_wax=stroke_width(g(M, 'P__L6_wax')), L6_all=stroke_width(g(M, 'P__L6_all')), L5_wax=stroke_width(g(M, 'P__L5_wax')),\n                       L5_all=stroke_width(g(M, 'P__L5_all'))), reference=dict(REF_W))"
assert old in s
new = ("    sw = lambda k: stroke_width(g(M, 'P__' + k), cov=M.get('Pv__' + k))\n"
       "    r = dict(mask=dict(L6_wax=sw('L6_wax'), L6_all=sw('L6_all'), L5_wax=sw('L5_wax'), L5_all=sw('L5_all')), reference=dict(REF_W),\n"
       "             measure='coverage integrated along the normal' if 'Pv__L6_all' in M else '50 % mask run')")
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
