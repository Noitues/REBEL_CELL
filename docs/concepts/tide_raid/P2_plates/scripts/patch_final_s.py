s = open('p1_final.py').read()
s = s.replace("sys.path.insert(0, L.H2)\nimport lib as PL", "sys.path.insert(0, L.H2)\nimport p2_scale\np2_scale.install()\nimport lib as PL", 1)
s = s.replace("import ui, hy, hb, eb as EB, glyphs\n", "import ui, hy, hb, eb as EB, glyphs\np2_scale.patch_modules(hy, ui, hb, EB)\n", 1)
s = s.replace("OUTDIR = L.OUT + 'plates/'", "OUTDIR = L.OUT + ('plates/' if os.environ.get('P2_S', '1') == '1' else 'plates4k/')", 1)
s = s.replace("W, H = 1920, 1080\n", "W, H = C.W, C.H\n", 1)
s = s.replace("sh = int(round(fringe))", "sh = int(round(fringe * C.S))")
s = s.replace("img = img * (1 - scan * (np.mod(yy, 3) == 0))[..., None]", "img = img * (1 - scan * (np.mod(np.floor(yy / C.S), 3) == 0))[..., None]")
open('p1_final.py', 'w').write(s)
m = open('p2_scale.py').read()
m += '''
    _hud = hy.hud

    def hud(cv, *a, flash=0.0, **kw):
        _hud(cv, *a, flash=0.0, **kw)
        if flash:
            cv.add(hy.TIER['DAMAGED'], np.full((56 * S, 226 * S), flash * .3, np.float32), 1, (22 * S, 14 * S))
    hy.hud = hud
    _gt = ui.glitch_tear

    def glitch_tear(cv, box, amount=1.0, seed=7, bands=9, split=True, maxdx=48):
        _gt(cv, tuple(v * S for v in box), amount, seed, bands, split, maxdx * S)
    ui.glitch_tear = glitch_tear
'''
open('p2_scale.py', 'w').write(m)
print('ok')
