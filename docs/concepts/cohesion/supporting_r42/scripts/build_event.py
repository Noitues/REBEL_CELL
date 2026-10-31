"""Terminal event card on the r42 city (event.py unchanged except via the patched backdrop)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import r31lib as L
import event as E
C.patch_save(L, {"event_screen.png": "01_terminal_event.png", "event_screen_memo.png": "01b_terminal_event_memo.png"})
L.backdrop = lambda path, **kw: C.bg("city", [(90, 120, 1330, 1000), (1380, 120, 1880, 330)], blur=3)
E.main_event()
E.memo_event()
