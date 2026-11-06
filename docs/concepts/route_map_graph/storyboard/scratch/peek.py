import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import post_aaa as PA
import sb_ocjobs as OJ
nm = sys.argv[1]
im = PA.finish(OJ.OUTC, "real", shot=nm, t=19.0, over=dict(exposure=1.1))
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "peek_%s.png" % nm))
