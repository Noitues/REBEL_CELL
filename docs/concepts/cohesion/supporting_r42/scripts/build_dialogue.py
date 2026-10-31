"""Dispatch briefing / dialogue (A: CRT feed, B: sticker portrait) on the r42 city."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import r31lib as L
import dialogue as D
C.patch_save(L, {"dialogue.png": "02_dialogue_A.png", "dialogue_B.png": "02_dialogue_B.png"})
L.backdrop = lambda path, **kw: C.bg("city", [(100, 270, 1840, 940)], blur=3)
D.make_a()
D.make_b()
