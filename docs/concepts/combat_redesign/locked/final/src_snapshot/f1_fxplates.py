"""f1_fxplates: slice-overlay effect moments on the redesigned board (resolve beat, peak frame)"""
import sys, os, time
sys.dont_write_bytecode = True
import f1_render as R
import f1_fx as FX
import f1_tower as FT
from f1_lib import Canvas
from cv_lib import C
from PIL import Image

MOMENTS = {
    # moment 1 (f1, the state before any card): the same shield, two outcomes in one frame
    'fx_moment_1_block_vs_break': dict(key='f1', beat='p1', fx=[('shield_break', 1, {}), ('slice_break', 2, {}), ('shield_block', 3, dict(ticks=1)), ('hit_land', 4, {})]),
    # moment 2 (f2, best line): the Brace clamp holds a whole landing, the soak funnel takes the overflow
    'fx_moment_2_brace_soak': dict(key='f2', fx=[('brace_block', 2, {}), ('soak_take', 1, {}), ('shield_block', 3, dict(ticks=1))]),
}


def build(name, room=None, out=None):
    m = MOMENTS[name]

    def extra(bg, f):
        cv = Canvas(FT.TW, FT.TW, 3, seed=29)
        for fn, s, kw in m['fx']:
            kw = dict(kw)
            if fn == 'shield_block':
                kw['w'] = f['wheel'][s]
            getattr(FX, fn)(cv, s, **kw)
        im = cv.down()
        bg.alpha_composite(im, (int(C[0] - FT.CT[0]), int(C[1] - FT.CT[1])))
    im = R.render(m.get('beat', 'p3'), key=m['key'], room=room, extra=extra, trim=False)
    return im


if __name__ == '__main__':
    t = time.time()
    nm = sys.argv[1]
    im = build(nm)
    im.save(R.OUT + nm + '.png')
    print('ok', round(time.time() - t, 1))
