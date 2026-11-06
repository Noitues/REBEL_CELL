"""bd_solve.py <common.json> <room>   per room: solve hull_value so the room squint mean hits TARGET_MEAN (bisection),
then chroma so the room's mean saturation lands on min(before, SAT_CAP); repeat once. Writes work/solve_<room>.json."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd_measure as M

common = json.load(open(sys.argv[1]))['_common']
room = sys.argv[2]
TARGET_MEAN = common.pop('_target_mean', 0.135)
SAT_CAP = common.pop('_sat_cap', 0.44)
extra = common.pop('_rooms', {}).get(room, {})
B = json.load(open(M.HERE + 'work/before.json'))['%s_neutral' % room]
reg = M.regions('neutral')
P = dict(common, **extra)
sat_t = min(B['room_detail']['sat'], SAT_CAP)


def ev(P):
    return M.measure(M.compose(M.after_backdrop(room, P)), 'neutral', reg)


for it in range(2):
    lo, hi = 0.30, 0.80
    for _ in range(7):
        P['hull_value'] = (lo + hi) / 2
        st = ev(P)
        if st['room']['mean'] > TARGET_MEAN:
            hi = P['hull_value']
        else:
            lo = P['hull_value']
    P['hull_value'] = round((lo + hi) / 2, 3)
    st = ev(P)
    if 'chroma' not in extra:
        P['chroma'] = round(float(np.clip(P['chroma'] * sat_t / max(st['room_detail']['sat'], 1e-3), 0.6, 1.2)), 3)
st = ev(P)
json.dump(dict(room=room, params=P, stats=st), open(M.HERE + 'work/solve_%s.json' % room, 'w'), indent=1)
print(room, json.dumps(P), json.dumps(st['room']), st['room_detail'], flush=True)
