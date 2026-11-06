import sys, os, time, traceback, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build as WBd
import wr_latent as WLT
import wr_config as CFG
from wr_build import J, ROOT

OUT = ROOT + 'out/'
BOARD_BOX = (0, 0, 1100, 1080)
_LAB = {}


def lab_f(name):
    if name not in _LAB:
        _LAB[name] = WLT.lab_frame(J, name)
    return _LAB[name]


def plate(beat, lab, opts):
    f = lab_f(lab) if lab else None
    return WBd.render(beat, opts, hud=False, f_override=f)


def tag(el, o):
    return '%s_%s' % (el, o)


def run(els=None, force=False):
    log = open(OUT + 'run_log.txt', 'a')
    for (eid, title, beat, lab, caps, base) in CFG.EL:
        if els and eid not in els:
            continue
        for o in ('E', 'A', 'B', 'C'):
            fn = OUT + 'pl_%s.png' % tag(eid, o)
            if os.path.exists(fn) and not force:
                continue
            opts = dict(base)
            if o != 'E':
                opts[eid] = o
            t = time.time()
            try:
                im = plate(beat, lab, opts)
                im.crop(BOARD_BOX).save(fn)
                log.write('%s ok %.1fs\n' % (tag(eid, o), time.time() - t))
            except Exception as e:
                log.write('%s FAIL %s\n%s\n' % (tag(eid, o), e, traceback.format_exc()))
            log.flush()
    log.close()


if __name__ == '__main__':
    els = sys.argv[1:] or None
    run(els, force=bool(els))
