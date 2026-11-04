"""bd2_set.py <in.json> <out.json> <room> key=value ... : copy a param file and override keys for one room (helper for tuning)"""
import sys, json
sys.dont_write_bytecode = True
src, dst, room = sys.argv[1], sys.argv[2], sys.argv[3]
J = json.load(open(src))
P = dict(J[room] if room in J else next(iter(J.values())))
for kv in sys.argv[4:]:
    k, v = kv.split('=', 1)
    P[k] = json.loads(v)
J = {room: P}
json.dump(J, open(dst, 'w'))
print(json.dumps(P))
