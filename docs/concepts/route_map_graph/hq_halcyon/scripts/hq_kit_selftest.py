"""hq_kit self-test: build three compounds from configs only (Halcyon's spiral, a round-43 style switchback, a short
two-face spiral) and print their segments, shortcuts, link types, the scan rule and the orbit poses."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from hq_kit.layout import Compound, FACES  # noqa: E402
from hq_kit.orbit import Orbit  # noqa: E402
from hq_kit import lod  # noqa: E402

CASES = {
    "halcyon spiral": (dict(rows=[6, 5, 4, 3, 2, 1], path="spiral"), dict(type="lighthouse", phase=0, sector=90, step=45)),
    "switchback": (dict(rows=[6, 5, 4, 3, 2, 1], path="switchback", shortcuts="none"), dict(type="face", phase=0)),
    "short spiral": (dict(rows=[4, 4, 3, 3, 2], path="spiral", face0=1, kinds=["router", "elite"]), dict(type="none")),
}
for name, (cfg, watch) in CASES.items():
    C = Compound(cfg, watch)
    O = Orbit(C)
    walked = ["start"] + C.NODES[1:4]
    st, opts = C.states(walked)
    types = sorted({C.edge_type(a, b) for a, b in C.edges(walked)})
    print("%-15s rooms %2d segments %s shortcuts %s" % (name, C.N_ROOMS, [FACES[f] for f in C.SEG_FACE],
                                                         ["%s>%s" % (a[1:], b[1:]) for a, b in C.SHORTCUTS]))
    print("   at %s options %s links %s scanned %s" % (walked[-1], opts, types, C.scanned(walked)[0]))
    d, o = O.decision(walked), O.overview(walked)
    print("   decision yaw %.0f dist %.0f | overview yaw %.0f dist %.0f | zoom(decision) %.2f | lod %s" % (
        d.yaw, d.dist, o.yaw, o.dist, O.zoom_of(d, walked),
        {k: round(v, 2) for k, v in lod.weights(0.7).items()}))
