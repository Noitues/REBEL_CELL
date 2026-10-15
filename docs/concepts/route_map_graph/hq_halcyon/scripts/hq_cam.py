"""HQ Halcyon: the orbit camera = hq_kit.orbit.Orbit on the Halcyon compound (the rules are in hq_kit/orbit.py).

Module-level names kept for the Halcyon scripts: Pose, ease, ease_out, lerp, decision, hover, overview, zoom_of,
visible_face, UCX, UCY, FPS, stills().
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_graph as G  # noqa: E402
from hq_kit import orbit as OR  # noqa: E402

ORB = OR.Orbit(G.C)
Pose, ease, ease_out, lerp = OR.Pose, OR.ease, OR.ease_out, OR.lerp
UCX, UCY, W, H = OR.UCX, OR.UCY, OR.W, OR.H
FPS = 24
decision, hover, overview, visible_face = ORB.decision, ORB.hover, ORB.overview, ORB.visible_face


def zoom_of(pose, walked=None):
    return ORB.zoom_of(pose, walked or G.WALK_LATE)


def stills():
    return {
        "H_overview": (overview(G.WALK_LATE), dict(walked=G.WALK_LATE, zoom=1.0)),
        "H_decision_S": (decision(G.WALK_EARLY), dict(walked=G.WALK_EARLY)),
        "H_hover_S": (hover(G.WALK_EARLY, G.HOVER_EARLY), dict(walked=G.WALK_EARLY, hover=G.HOVER_EARLY, hover_k=1.0)),
        "H_decision_E": (decision(G.WALK_LATE), dict(walked=G.WALK_LATE)),
        "H_hover_E": (hover(G.WALK_LATE, G.HOVER_LATE), dict(walked=G.WALK_LATE, hover=G.HOVER_LATE, hover_k=1.0)),
    }


if __name__ == "__main__":
    for name, (p, s) in stills().items():
        print(name, [round(v, 1) for v in p.loc()], "yaw %.1f pitch %.1f dist %.1f sx %.3f sy %.3f zoom %.2f" % (
            p.yaw, p.pitch, p.dist, p.sx, p.sy, zoom_of(p)), "faces seen",
            [G.FACES[f] for f in range(4) if visible_face(f, p)])
