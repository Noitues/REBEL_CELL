"""python hv_run.py <h01|..|h11>[:nw] ...   (env CORP=neutral|solace|meridian)
 -> round2/hover/out/<name>.png, chk/<name>.json (the plate report), chk/<name>.npz (masks for hv_checks)"""
import sys, os, time, json, traceback
sys.dont_write_bytecode = True
import numpy as np
import hv_plates as P
import hv_core as V
import hv_comp as K

OUT = V.HERE + 'out/'
CHK = V.HERE + 'chk/'
os.makedirs(OUT, exist_ok=True)
os.makedirs(CHK, exist_ok=True)


def plate_name(pid, words, corp):
    return P.NAMES[pid] + ('' if words else '_nowords') + ('' if corp == 'neutral' else '_' + corp)


def save_masks(name):
    arrs = {}
    for pre, d in (('Z', V.MASKS), ('R', K.RBM), ('P', V.PEN_MASKS), ('F', V.FOCUS_MASK), ('Y', V.YOU_MASK), ('Hd', K.HAND_MASKS), ('B', K.BTN)):
        for k, v in d.items():
            if isinstance(v, np.ndarray) and v.dtype == bool and v.shape == (1080, 1920):
                arrs['%s__%s' % (pre, k)] = np.packbits(v)
    lm = P.STATE.get('mask')
    if lm is not None:
        arrs['lit'] = lm.astype(np.uint8)
    hf = P.STATE.get('hud_hero_full')
    if hf is not None:
        arrs['Zf__hud_hero_full'] = np.packbits(hf)
    for i, c in enumerate(K.FOCUS_CALLS):
        arrs['Fc__%03d' % i] = np.packbits(c['m'])
    for k, v in V.PEN_COV.items():                   # pencil coverage (0-255), for the coverage-integrated width checks
        arrs['Pv__%s' % k] = np.round(v * 255.0).astype(np.uint8)
    np.savez_compressed(CHK + name + '.npz', **arrs)


def save_geometry(name):
    """rb_capture geometry of the board frame (cell polygons, states, token discs) and the skin's empty-cell probe, for check a"""
    f_board = P.STATE.get('f_board')
    if f_board is None:
        return None
    geo = V.RBC.geometry(V.A, f_board, 'p1', P.STATE.get('hover_unit'))
    probe = V.RBC.empty_probe(V.R, V.A, f_board, 'p1')
    probe.save(CHK + name + '_probe.png')
    return geo


if __name__ == '__main__':
    for job in sys.argv[1:]:
        pid, _, mode = job.partition(':')
        words = mode != 'nw'
        name = plate_name(pid, words, V.CORP)
        t = time.time()
        try:
            img, rep = P.BUILD[pid](words)
        except Exception:
            traceback.print_exc()
            print('FAIL', name, flush=True)
            continue
        img.save(OUT + name + '.png')
        save_masks(name)
        try:
            rep['geometry'] = save_geometry(name)
        except Exception:
            traceback.print_exc()
            rep['geometry'] = None
        rep['focus_calls'] = [dict(i=i, fn=c['fn'], thick=c['thick']) for i, c in enumerate(K.FOCUS_CALLS)]
        rep['seconds'] = round(time.time() - t, 1)
        rep['rbc'] = dict(text=list(V.RBC.TEXT), uncaptured=list(V.RBC.UNCAPTURED))
        rep['hud2_R'] = {k: v for k, v in V.hud2.R.items() if k in ('bill_frame', 'hero_pair', '_hero_xy', 'you_hp_tally', 'next_row', '_opt_rows', '_bill_room',
                                                                       'best_line_tag')}
        rep['obj2_R'] = {k: v for k, v in V.obj2.R.items() if k in ('obj_plate', 'res_plate', 'ram_pips', 'trace_pips', 'ram_refund', 'refund_tab')}
        json.dump(rep, open(CHK + name + '.json', 'w'), indent=1, default=str)
        h = rep['hand']
        print('ok', name, rep['seconds'], 'asserts %d/%d' % (rep['asserts']['passed'], rep['asserts']['total']), 'hand', h.get('ok'), h.get('layout'),
              'rings', [(x['tag'], x['form'], x['ok']) for x in rep['hud_ring_fits']], rep['snap'].get('cache'), flush=True)
