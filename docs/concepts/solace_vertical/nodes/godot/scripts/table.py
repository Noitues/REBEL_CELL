import sys
sys.path.insert(0, ".")
exec(open('hue_search2.py').read().split("res = {}")[0])
c = (136, 8, 28)
names = {"fight": "FIGHT ring (#6CF7FF)", "elite": "ELITE ring (#FF8C1A)", "event": "EVENT ring (#4EFF9E)", "shop": "SHOP ring (#62A9FF)", "rack": "RACK ring (#FFA02A)",
 "rest": "REST (#BF73FF)", "workshop": "WORKSHOP (#FFD14D)", "r_router": "room router (#389EFF)", "r_terminal": "room terminal (#4DF280)", "r_mainframe": "room mainframe (#6673FF)",
 "r_rack": "room server_rack (#FF9433)", "r_elite": "room elite (#FF591F)", "ring_walked": "ring walked (#D4FF00)", "ring_next": "ring next (#FF8C1A)", "ring_unavail": "ring not yet (#F2F6FF)", "pink": "Cell pink (#FF3DA8)"}
print("| vs | normal | protan | deutan | tritan |\n|---|---|---|---|---|")
mins = {v: 999 for v in vis}
for k, v in KINDS.items():
    row = [de(c, v, x) for x in vis]
    for x, r in zip(vis, row): mins[x] = min(mins[x], r)
    print("| %s | %s |" % (names[k], " | ".join("%.0f" % r for r in row)))
print("| **least** | %s |" % " | ".join("**%.0f**" % mins[x] for x in vis))
