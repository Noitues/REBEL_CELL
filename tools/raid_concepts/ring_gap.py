"""Ring Siege: does the choice matter? Per scenario, the net of 500 seeded random plans (median, 10th percentile)
against the best hill-climbed plan (from ring_siege.json). A big gap = placement and speed matter (skill), a small one
= anything works."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from depth_harness import scenarios  # noqa: E402
from ring_siege import net, random_plan, resolve  # noqa: E402

best = json.load(open(r"D:/rc_tmp/raid_design_lab/ring_siege.json"))["per"]
gaps = []
for si, sc in enumerate(scenarios()):
    rng = random.Random(900 + si)
    vals = sorted(net(resolve(random_plan(rng), sc)) for _ in range(500))
    med, p10 = vals[len(vals) // 2], vals[len(vals) // 10]
    b = best[si]["best"]
    gaps.append(b - med)
    print(si, "best", b, "median random", med, "p10", p10, "share >= best-3", round(sum(v >= b - 3 for v in vals) / 500, 3))
print("mean gap best - median random", round(sum(gaps) / len(gaps), 1))
