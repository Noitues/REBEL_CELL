"""Server Rack on the cutaway (the Rack sits in the Seed Vault lab)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
import r31lib as L
import server_rack as SR
C.patch_save(L, {"server_rack.png": "06_server_rack.png"})
L.backdrop = lambda path, **kw: C.bg("cutaway", [(40, 220, 460, 520), (520, 150, 1300, 830), (1320, 150, 1880, 760)], blur=2)
SR.main()
