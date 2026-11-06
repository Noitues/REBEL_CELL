import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_sheets as S, wr_crops as CR, wr_config as CFG
D = S.DEST + 'crops/'
os.makedirs(D, exist_ok=True)
res = {}
for (eid, title, beat, lab, caps, base) in CFG.EL:
    lab_, st, specs = CR.STATES[eid][0]
    sc = min(2.0, S.fit_scale(specs))
    for o in 'EABC':
        if specs[0][0] == 'gproof':
            im = S.crop_specs(None, specs, sc, o)
        else:
            fn = 'pl_%s_%s%s.png' % (eid, o, '' if st == ('lab' if lab else beat) or (st == 'p1' and lab) else '_' + st)
            im = S.crop_specs(S.load(fn), specs, sc, o)
        p = D + '%s_%s.png' % (eid, o)
        im.save(p)
        res[(eid, o)] = p
json.dump({'%s_%s' % k: v for k, v in res.items()}, open(S.OUT + 'crops.json', 'w'))
print(len(res))
