import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common42 as C
out = os.path.join(C.OUT, "scratch")
C.bg("city", [(90, 120, 1330, 1000)]).convert("RGB").save(os.path.join(out, "probe_city.png"))
C.bg("cutaway", [(300, 300, 1290, 800)]).convert("RGB").save(os.path.join(out, "probe_cut.png"))
