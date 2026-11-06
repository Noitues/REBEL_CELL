"""render the linocut plates: python lc_run.py A|B [beat]"""
import sys, os, time
sys.dont_write_bytecode = True
import lc_tower as LT
import lc_cards as LC
import lc_ui as LU
import f1_render as R
import f1_hand as FH

ROOT = 'D:/rc_scratch/combat_redesign/punk/linocut/'
R.A.S2.needle = lambda L, o: None          # ART CALL 52: no needle in the new concept


def setup(v):
    LT.VARIANT[0] = v
    wd = ROOT + 'work_%s/' % v
    os.makedirs(wd, exist_ok=True)
    R.WORK = wd
    FH.CACHE = wd
    FH._mem.clear()
    FH._ui.clear()
    R._tw.clear()
    FH.K = LC
    FH.UI = LU
    FH.CARD_SCALE = 1.10
    FH.STEP = 190


if __name__ == '__main__':
    v = sys.argv[1] if len(sys.argv) > 1 else 'A'
    beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
    setup(v)
    t = time.time()
    im = R.render(beat, check=True)
    out = ROOT + 'out/plate_%s_%s.png' % (v, beat)
    im.save(out)
    print('ok', out, round(time.time() - t))
