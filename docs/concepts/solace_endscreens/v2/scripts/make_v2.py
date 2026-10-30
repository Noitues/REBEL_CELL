"""Build win/lose for the three image-slot variants (A helix print, B survey map, C CCTV strip).
usage: python make_v2.py A|B|C [win|lose]"""
import sys
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
from v2_lib import *
import prints


def build(win, variant):
    img = desk()
    img = manila_folder(img, 'SB-7718  //  CELL-03', 'BIOSAFETY  //  RESTRICTED')
    # ---- left page: the image slot
    if variant == 'A':
        pic = prints.helix_print(win, 400, 500)
        glossy_print(img, pic, 292, 408, -3, border=22, caption='FIG. 1   HELIX PARK, 23:41' if win else 'FIG. 1   HELIX PARK, 23:58')
        routing_slip(img, 760, 290, 2.5, win)
        sample_log(img, win, 70, 722, 840, 290)
        slot_note = (610, 500, 900, 650)
    elif variant == 'B':
        pic = prints.survey_map(win, 780, 470)
        glossy_print(img, pic, 504, 395, -1.2, border=18, caption='SITE SURVEY 7  //  CELL NETWORK' if win else 'SITE SURVEY 7  //  NETWORK LOST')
        routing_slip(img, 805, 872, 3, win, 270, 250)
        sample_log(img, win, 70, 722, 600, 290)
        slot_note = None
    else:
        strip = prints.cctv_strip(win)
        L = layer(strip.width / K + 8, strip.height / K + 8)
        L.alpha_composite(strip, (S(4), S(4)))
        rotate_paste(img, L, 250, 418, -2.5)
        tape(img, 160, 112, -30)
        tape(img, 340, 112, 30)
        routing_slip(img, 700, 262, 2.5, win)
        sample_log(img, win, 70, 722, 840, 290)
        slot_note = (500, 470, 900, 640)
    # ---- the memo
    m = memo(win, 850, 880)
    rotate_paste(img, m, 1405, 560, -0.5)
    paperclip(img, 1030, 122, 6)
    if win:
        stamp(img, 'CONTAINMENT FAILED', 1370, 905, (205, 40, 50, 235), rot=-7, size=52)
        postit(img, (1680, 150, 1900, 320), (170, 226, 255, 245), 'contaminant is\nin the supply\nline. who left\nthe lid off?', rot=4, size=25)
        postit(img, (1690, 790, 1905, 960), (170, 255, 120, 245), 'it hums the\nSolace jingle.\nflag it.', rot=-4, size=25, fg=(30, 70, 40, 255))
        stamp(img, 'ROUTED', 790, 640 if variant == 'A' else 705, (40, 90, 200, 220), rot=-9, size=40)
    else:
        stamp(img, 'STERILE', 1580, 520, (30, 140, 40, 240), rot=-7, size=84)
        postit(img, (1680, 150, 1900, 320), (200, 255, 150, 245), 'all strains\naccounted for.\nlid sealed.', rot=3, size=25, fg=(30, 70, 40, 255))
        postit(img, (1690, 790, 1905, 960), (255, 226, 80, 245), 'they will be\nback. log the\nPHANTOM.', rot=-4, size=25)
        stamp(img, 'FILED', 790, 640 if variant == 'A' else 705, (30, 140, 40, 220), rot=-9, size=40)
    buttons(img, main_xy=(1470, 1042), new_xy=(1740, 1044))
    img = vignette(img, 0.35)
    return img


if __name__ == '__main__':
    v = sys.argv[1]
    kinds = [sys.argv[2]] if len(sys.argv) > 2 else ['win', 'lose']
    for k in kinds:
        img = build(k == 'win', v)
        finish(img, OUT + '%s_%s.png' % (k, v), 5, 1 if k == 'win' else 2)
        print('ok', v, k)
