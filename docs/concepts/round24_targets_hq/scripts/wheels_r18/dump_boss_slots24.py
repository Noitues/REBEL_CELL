"""Round 24: dump each corp boss's phase-1 slots + pointers (for the forecast tags)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import specs14 as S
out = {}
for corp in ["solace", "halcyon", "orbital", "rebel_cell"]:
    spec, m = S.boss(corp, 1)
    out[corp] = dict(name=m["name"], pointers=spec.get("pointers", [0]),
                     slots=[dict(program=s["program"], value=s["value"], special=s.get("special"), name=s.get("name")) for s in spec["slots"]])
json.dump(out, open(os.path.join(HERE, "..", "..", "scratch", "wheels", "boss_slots.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
