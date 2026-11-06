"""js_render: the Jinx scribble plate set.  python js_render.py <A|B> [beat ...]
Wraps f1_render with: js_tower (wheel), js_cards (hand), js_ui; the needle on the outer schedule ring is removed (ART CALL 52)."""
import sys, os, time
sys.dont_write_bytecode = True
import f1_render as R
import f1_tower as FT
import f1_hand as FH
import js_tower as JT
import js_cards as JC
import js_ui as JU
import a2_stick  # noqa

ROOT = 'D:/rc_scratch/combat_redesign/punk/jinx_scribble/'


class _K:
    NW = JC.NW

    @staticmethod
    def render_card(name, v, seed=0, ss=4, scale=2):
        return JC.render_card(name, JC.CUR[0], seed=seed, ss=ss, scale=scale)


def setup(var):
    JT.install()
    JT.VAR[0] = var
    JC.CUR = [var]
    JC.V_IS_A[0] = var == 'A'
    FH.K = _K
    FH.CACHE = ROOT + 'work_%s/' % var
    os.makedirs(FH.CACHE, exist_ok=True)
    FH._mem.clear()
    R.WORK = ROOT + 'work_t%s/' % var
    os.makedirs(R.WORK, exist_ok=True)
    R._tw.clear()
    JU.install()
    JU._cache.clear()
    R.A.S2.needle = lambda *a, **k: None       # no needle in the new concepts
    if not hasattr(R.A.S2, '_orig_labels'):
        R.A.S2._orig_labels = R.A.S2.labels

        def labels(L, *a, **k):          # the sector digits come back on top: the needle used to cover the 0, and the ring plates clip its lower half
            R.A.S2._orig_labels(L, *a, **k)
            R.A.S2.digits(L, 'P')
        R.A.S2.labels = labels


if __name__ == '__main__':
    var = sys.argv[1]
    beats = sys.argv[2:] or ['p1']
    setup(var)
    for b in beats:
        t = time.time()
        im = R.render(beat=b, check=False)
        im.save(ROOT + 'out/plate_%s_%s.png' % (var, b))
        print(var, b, round(time.time() - t), flush=True)
