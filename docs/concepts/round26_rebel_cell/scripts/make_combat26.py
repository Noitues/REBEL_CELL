"""Round 26: the DISPATCH boss fight over the recommended base -> ../combat_rebel_cell.png (1920 x 1080).
Round 25 composite unchanged (combat_r23/make_combat25.py: locked D4 player wheel + HUD, round 18 DISPATCH boss wheel,
sticker cards, raid-style SEND IT sticker); only the backdrop is the round 26 base as DISPATCH (rc26_rec_dispatch_night)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import make_combat25 as M

M.BACK["rebel_cell"] = "rc26_rec_dispatch_night"
M.SITE["rebel_cell"] = "THE KNUCKLE DECK (TAKEN)"
M.compose("rebel_cell")
