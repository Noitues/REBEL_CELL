"""asm_hooks: install the published plates' render hooks (corp/src asm_render.py with check 1: rb_capture.install, then asm_render's own
layer captures and the hand capture), so an effects base renders pixel-for-pixel like the published round-2 plate.
Round 2 found that without these hooks the base drew no faint arc lane line and no dark keys round the landing-arc marks (up to 47 / 255
off the published plate): the capture wrappers draw through temp layers.  This is a copy of asm_render's install sequence (read-only use of
corp/src; the masks go into a local dict and nothing is written)."""
import numpy as np
from PIL import Image

MASKS = {}


def install(R, A, beat):
    import rb_capture as RBC
    RBC.install(R, A, R.FH, MASKS, beat)

    def _cap(cls, fn_owner, fn_name, Lidx=0):
        orig = getattr(fn_owner, fn_name)

        def wrap(*a, **k):
            L = a[Lidx]
            T = R.L2()
            a2 = list(a)
            a2[Lidx] = T
            r = orig(*a2, **k)
            L.im.alpha_composite(T.im)
            al = T.im.split()[3].resize((1920, 1080), Image.BOX)
            m = np.asarray(al) >= 128
            MASKS[cls] = MASKS.get(cls, np.zeros((1080, 1920), bool)) | m
            return r
        setattr(fn_owner, fn_name, wrap)
    _cap('digits', A.S2, 'digits')
    _cap('labels', A.S2, 'labels')
    _cap('tags', A.M2, 'ring_tags')
    _cap('tags', A.P2, 'refund_place')
    _cap('badges', A.P2, 'twist_badge')
    _cap('badges', A.AU, 'warded_badge')
    _cap('badges', A.AU, 'dead_badge')
    _cap('tags', A.H2, 'hover_tag')
    _cap('leader', A.H2, 'leader')
    _cap('tickets', A.M2, 'future')
    _cap('tape', A.S2, 'live_cell')
    _cap('tape', A.S2, 'live_label')
    _cap('tape', A.S2, 'chevrons')
    _cap('plates', A.S2, 'hold_cell')
    _cap('plates', A.S2, 'hold_live')
    _cap('plates', A.S2.S, 'plus_cell')
    _odh = R.FH.draw_hand

    def _hand(base, *a, **k):
        T = Image.new('RGBA', base.size, (0, 0, 0, 0))
        r = _odh(T, *a, **k)
        base.alpha_composite(T)
        MASKS['hand'] = np.asarray(T.split()[3]) >= 128
        return r
    R.FH.draw_hand = _hand
