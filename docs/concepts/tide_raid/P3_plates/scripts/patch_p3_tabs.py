s = open('p2_scale.py').read()
new = '''

def head_tab_mask(typ, w, h, S_):
    """P3 (coordinator A-review): the card tab carries the LOCKED H6 head silhouette (D worm / N thorn claw / E sea-mine), ink on the type-colour tab, from p1_heads.sprite
    (the same source as the on-map heads). Returns a float mask (h*S_, w*S_) with the silhouette centred at (w/2, 25) of the 1x card."""
    import p1_heads
    sz = int(34 * S_)
    im = p1_heads.sprite(typ, 0, sz)
    a = np.asarray(im, np.float32)[..., 3] / 255
    ys, xs = np.nonzero(a > 0.08)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    fit_w, fit_h = 30 * S_, 26 * S_
    k = min(fit_w / a.shape[1], fit_h / a.shape[0])
    pil = Image.fromarray((a * 255).astype(np.uint8)).resize((max(1, int(a.shape[1] * k)), max(1, int(a.shape[0] * k))), Image.LANCZOS)
    a = np.asarray(pil, np.float32) / 255
    m = np.zeros((h * S_, w * S_), np.float32)
    cx, cy = int(w * S_ / 2), int(25 * S_)
    x0 = cx - a.shape[1] // 2; y0 = cy - a.shape[0] // 2
    m[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    return m


def patch_tabs(hy):
    """replace hy.vcard_sprite so the tab glyph is the H6 head silhouette (any S)."""
    def vcard_sprite(verb, typ, w=104, h=140, ss=3):
        col = hy.TYPE_COL[typ]
        outer, inner, gl, tab = (hy.Lyr((0, 0, w, h), ss=ss, pad=0) for _ in range(4))
        outer.rr(1, 1, w - 1, h - 1, 13, 255)
        inner.rr(7, 7, w - 7, h - 7, 8, 255)
        tab.rr(7, 7, w - 7, 43, 8, 255)
        tab.rr(7, 30, w - 7, 43, 0, 255)
        hy.ui.VERB_FN[verb](gl, (w / 2, h * .67), 28)
        hs, ws = h * S, w * S
        o, i_, g_, tb = (x.m[:hs, :ws] for x in (outer, inner, gl, tab))
        t_ = head_tab_mask(typ, w, h, S)
        img = np.zeros((hs, ws, 3), np.float32)
        img[:] = hy.hexc('FBF8EC')
        img = img * (1 - i_[..., None]) + hy.hexc('F1EBD8') * i_[..., None]
        img = img * (1 - tb[..., None]) + col * tb[..., None]
        img = img * (1 - g_[..., None]) + hy.INK * g_[..., None]
        img = img * (1 - t_[..., None]) + hy.INK * t_[..., None]
        return img, o
    hy.vcard_sprite = vcard_sprite
'''
s = s.replace("\n\ndef patch_modules(hy, ui, hb, eb):", new + "\n\ndef patch_modules(hy, ui, hb, eb):", 1)
s = s.replace('    """after the kit modules are imported: their own W/H copies are 1x layout numbers (hand centring etc.)"""\n    if S == 1:\n        return',
              '    """after the kit modules are imported: their own W/H copies are 1x layout numbers (hand centring etc.)"""\n    patch_tabs(hy)\n    if S == 1:\n        return', 1)
# the S>1 branch defines its own vcard_sprite later: drop it so the tab patch stays
a = s.index("    def vcard_sprite(verb, typ, w=104, h=140, ss=3):\n        col = hy.TYPE_COL[typ]\n        outer, inner, gl, tg, tab")
b = s.index("    hy.vcard_sprite = vcard_sprite\n", a) + len("    hy.vcard_sprite = vcard_sprite\n")
s = s[:a] + s[b:]
open('p2_scale.py', 'w').write(s)
print('ok')
