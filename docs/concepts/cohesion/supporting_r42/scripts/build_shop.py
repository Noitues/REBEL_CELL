"""Shop, MAINFRAME, on the cutaway street (the old MARKET NEON facade plate is replaced; the MAINFRAME tube sign is redrawn)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import r31lib as L
import shop3 as S3
C.patch_save(L, {"shop_v3_layout.png": "04_shop_mainframe.png"})
S3.make_layout()
