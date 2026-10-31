"""Deck screen (loadout window, DECK tab) on the r42 city with the strong grade."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import b44 as K
import deck_viewer as DV
_orig = K.save
K.save = lambda img, name: _orig(img, {"deck_viewer.png": "05_deck_screen.png"}.get(name, "_unused_" + name))
K.city_backdrop = lambda dim=0.56, blur=5, sat=0.85: C.bg("city", [(90, 130, 1830, 1000)], blur=5)
DV.deck()
