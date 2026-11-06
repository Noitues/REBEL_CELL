"""python hz_run.py <h01|..|h11>[:nw] ...   (env CORP=neutral|solace|meridian)
 -> ../out/<name>[_nowords][_<corp>].png, ../chk/<same>.json"""
import sys, os, time, json, traceback
sys.dont_write_bytecode = True
import hz_plates as P
import hz_core as Z

OUT = Z.HERE + 'out/'
CHK = Z.HERE + 'chk/'
os.makedirs(OUT, exist_ok=True)
os.makedirs(CHK, exist_ok=True)
if __name__ == '__main__':
    for job in sys.argv[1:]:
        pid, _, mode = job.partition(':')
        words = mode != 'nw'
        name = P.NAMES[pid] + ('' if words else '_nowords') + ('' if Z.CORP == 'neutral' else '_' + Z.CORP)
        t = time.time()
        try:
            img, rep = P.BUILD[pid](words)
        except Exception:
            traceback.print_exc()
            print('FAIL', name, flush=True)
            continue
        img.save(OUT + name + '.png')
        rep['seconds'] = round(time.time() - t, 1)
        json.dump(rep, open(CHK + name + '.json', 'w'), indent=1, default=str)
        c = rep['collisions']
        print('ok', name, rep['seconds'], 'asserts %d/%d' % (rep['asserts']['passed'], rep['asserts']['total']),
              'pairs', c['mark_pairs_pass'], 'occ', c['occlusion_pass'], 'hover', c['hover_vs_marks_pass'], {k: v for k, v in c['hover_vs_marks_px'].items() if v},
              'hand', c['hand_vs_board'].get('pass'), 'dash', rep['dash_calls'], rep['dot_calls'], flush=True)
