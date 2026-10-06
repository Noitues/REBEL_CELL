"""Round 44: print the scope network (ids, states, kinds, lots) to plan the HQ framing."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
n = json.load(open(os.path.join(HERE, "..", "scratch", "layout", "net_scope.json")))
print(list(n.keys()))
print("hq", n["hq"])
print("raid", n["raid"], "transit", n["transit"])
for x in n["nodes"]:
    print(x["id"], x["state"], x.get("kind"), x.get("tier"), [round(v, 1) for v in x["lot"]], x.get("name"))
print(n["links"][0])
