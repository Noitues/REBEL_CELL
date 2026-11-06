import sys, os, time, traceback
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_run as R
import wr_crops as CR
import wr_config as CFG


def run(els=None, force=True):
    log = open(R.OUT + 'run_log.txt', 'a')
    for (eid, title, beat, lab, caps, base) in CFG.EL:
        if els and eid not in els:
            continue
        for st in CR.EXTRA.get(eid, []):
            for o in ('E', 'A', 'B', 'C'):
                fn = R.OUT + 'pl_%s_%s_%s.png' % (eid, o, st)
                if os.path.exists(fn) and not force:
                    continue
                opts = dict(base)
                if o != 'E':
                    opts[eid] = o
                t = time.time()
                try:
                    im = R.plate(st, lab, opts)
                    im.crop(R.BOARD_BOX).save(fn)
                    log.write('%s_%s ok %.1fs\n' % (R.tag(eid, o), st, time.time() - t))
                except Exception as e:
                    log.write('%s_%s FAIL %s\n%s\n' % (R.tag(eid, o), st, e, traceback.format_exc()))
                log.flush()
    log.close()


if __name__ == '__main__':
    run(sys.argv[1:] or None)
