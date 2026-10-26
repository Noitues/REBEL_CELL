"""R-F calibration helper (Phase 2b): copies the breach states a balance run dumped (boss_<seed>.json, a bare CampaignState
dict) and sets the number of INFECTED cards in each Solace tide block, so the Genome Core fight can be replayed at a chosen
INFECTED count with `balance.py run boss --source save --state <out>`.

    python tools/raid_tide/set_infected.py <in_dir> <out_dir> <n_infected>

Every WOUND card is dropped from the tide deck and `n_infected` fresh ones ("w900".."w9xx", tied to "t1_a") are added. A
state without a tide block gets one with the default counters.
"""
import json
import sys
from pathlib import Path


def main() -> int:
    src, dst, n = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src.glob("boss_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        camp = d.get("campaign", d)
        theme = camp.setdefault("corp_theme", {}).setdefault("solace", {})
        tide = theme.setdefault("tide", {"deck": [], "ghost": 2, "last_sac": -9})
        deck = [c for c in tide.get("deck", []) if c[2] != "WOUND"]
        for i in range(n):
            deck.append(["w%03d" % (900 + i), "t1_a", "WOUND"])
        deck.sort()
        tide["deck"] = deck
        (dst / f.name).write_text(json.dumps(d), encoding="utf-8")
        count += 1
    print("wrote %d states with %d INFECTED to %s" % (count, n, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
