"""Rewards, FIGHT WON, on the picked cutaway (the Seed Vault lab the Cell just took) with the strong grade."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import r31lib as L
import reward as RW
C.patch_save(L, {"reward_screen_v2.png": "03_reward_fight_won.png"})
_c = {}


def base(bg_only=False):
    if "b" not in _c:
        im = C.bg("cutaway", [(300, 300, 1290, 800), (1360, 300, 1860, 800)], blur=1.5)
        im = L.bloom(im, 0.3, 0.6, 14)
        _c["b"] = L.vignette(im, 0.6)
    return _c["b"].copy()


RW.base = base
RW.make_a()
