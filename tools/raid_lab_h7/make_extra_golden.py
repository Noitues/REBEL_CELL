"""Extra parity cases for the H7 lab (tools/raid_lab_h7/parity_check.gd): the 5 seeded legs, 3 fixed fortress lines each,
replayed through the python rules (tools/raid_concepts/h7_golden.replay). Covers lost nodes (footholds), survivors, the
Lockdown freeze and breaches, which leg 0's two lines do not. Writes tools/raid_lab_h7/data/h7_extra_golden.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "raid_concepts"))
from h7_golden import replay  # noqa: E402
from h7_campaign import legs  # noqa: E402

LINES = {
    "bare": [([], [], "SAFE")] * 3,
    "fw_turret_ice": [(["TURRET", "ICE"], ["FW", "RELAY"], "FW")] + [(["TURRET"], ["FW"], "FW")] * 2,
    "decoy_sentry": [(["DECOY", "SENTRY"], ["SAFE", "PROXY"], "PROXY"), (["ICE"], ["PROXY"], "PROXY"), ([], [], "HOME")],
    "heavy_home": [(["RAILGUN"], ["HOME"], "HOME")] + [(["RAILGUN"], ["HOME"], "HOME")] * 2,
}
out = {}
for li, leg in enumerate(legs(5)):
    for name, line in LINES.items():
        lines = [{"raid": i, "buy": b, "place": p, "crew": c} for i, (b, p, c) in enumerate(line)]
        out[f"leg{li}_{name}"] = {"leg": li, "rows": replay([[tuple(t) for t in r] for r in leg], lines)}
(HERE / "data" / "h7_extra_golden.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
lost = sum(1 for v in out.values() for r in v["rows"] if r["lost"])
breach = sum(1 for v in out.values() for r in v["rows"] if r["breached"])
print(len(out), "cases;", lost, "rows with lost nodes;", breach, "breached rows")
