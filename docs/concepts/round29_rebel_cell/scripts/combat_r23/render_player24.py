"""Round 24: the locked D4 player wheel (Breaker) as used on the round 22/23 combat screen.
Writes ../../scratch/wheels/player.png + .json."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DST = os.path.join(HERE, "..", "..", "scratch", "wheels")
os.makedirs(DST, exist_ok=True)
import make_sheets as MS

im, c, meta, s = MS.cached("d4", "player", ss=2, rot=0.0, tag="d4_player_r000.00_s2")
im.save(os.path.join(DST, "player.png"))
json.dump(dict(c=c, meta=meta, ss=s), open(os.path.join(DST, "player.json"), "w"))
print("player wheel", im.size, flush=True)
