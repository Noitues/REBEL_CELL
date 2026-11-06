"""mu_ui: the YOU strip, SEND IT and the nameplate repainted as mural plaques (no tape, no paper): plaster slabs with an ink + white keyline, and a sunset spray SEND IT slab.
Built from the street-graffiti st_ui source with targeted replacements so the layout and the game information are identical."""
import inspect, sys
sys.dont_write_bytecode = True
import numpy as np
import st_ui as U
import st_gfx as G
import mu_cards as MC

_ns = dict(U.__dict__)
_ns['tape_piece'] = lambda *a, **k: None


def _plaster_paper(w, h, **k):
    k.pop('base', None)
    return G.paper(w, h, base=MC.pal()['plaster'], **k)


_ns['paper'] = _plaster_paper

KEY = "    cv.paint(blur(grow(fm, 3.4 * ss), 0.3 * ss), INK)\n    cv.paint(blur(grow(fm, 1.8 * ss), 0.3 * ss), hx('FFFCF4'))\n"


def _src(fn, subs):
    s = inspect.getsource(fn)
    for a, b in subs:
        if a not in s:
            raise RuntimeError('mu_ui: missing snippet ' + a[:50])
        s = s.replace(a, b)
    exec(compile(s, 'mu_ui_' + fn.__name__, 'exec'), _ns)
    return _ns[fn.__name__]


you_strip = _src(U.you_strip, [
    ("    cv.paint(fm, pt * 0.96)\n", KEY + "    cv.paint(fm, pt * 0.96)\n"),
    ("tag_text(cv, 'YOU', x0 + 40, y0 + 26, 28, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=CHROME, drop=PINK_DK, drop_off=(1.6, 1.9), outline=1.6, rim_w=0.9,",
     "tag_text(cv, 'YOU', x0 + 40, y0 + 26, 28, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=hx('FFFCF4'), drop=INK, drop_off=(1.6, 1.9), outline=1.8, rim_w=0.9,"),
])
nameplate = _src(U.nameplate, [
    ("    cv.paint(fm, pt * 0.96); cv.paint(cm, pt)\n", KEY + "    cv.paint(fm, pt * 0.96); cv.paint(cm, pt)\n"),
    ("tag_text(cv, 'CELL-9', 160, cy_ - 11, 38, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=CHROME, drop=PINK_DK,",
     "tag_text(cv, 'CELL-9', 160, cy_ - 11, 38, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=hx('FFFCF4'), drop=INK,"),
])
send_it = _src(U.send_it, [
    ("    col = lerp((PINK * 0.55 + PINK_HI * 0.45)[None, None, :], PINK[None, None, :], np.clip((Y - 915) / 95.0, 0, 1)[..., None] ** 1.1)\n",
     "    _t = np.clip((Y - 915) / 95.0, 0, 1)[..., None]\n"
     "    _top = hx('FFB347') if MC.VAR[0] == 'A' else hx('FF7AC8')\n"
     "    _bot = hx('E8208C') if MC.VAR[0] == 'A' else hx('8A3CE0')\n"
     "    col = np.where(_t < 0.45, lerp(_top[None, None, :], PINK[None, None, :], _t / 0.45), lerp(PINK[None, None, :], _bot[None, None, :], (_t - 0.45) / 0.55))\n"),
])
_ns['MC'] = MC
