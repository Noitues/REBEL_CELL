"""Round 40 ADAPTER: the round 19-23 raid-UI `finish19.finish(...)` signature, rendered by the ONE CITY post
(post40: translucent darkened buildings, lane dimming, sky lanes, x-ray network) on the unified Blender passes.

The raid-UI decal Net (netdecal21, sockets / links / health / frost / lure / threat rings, round 19 sizes) runs on the
compat world = the unified GROUND-only position pass x K (layout.K), so the decals live in the same coordinates as the
compat layout and the locked gif code. Everything else (ink, bloom, fog, rain) is post40's.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(1, PARENT)
import layout as LY  # noqa: E402  (compat)
import netdecal19 as ND  # noqa: E402
import post40 as P40  # noqa: E402
import finish as F0  # noqa: E402,F401

SRC = P40.SRC
load = P40.load_img


class _Lod:
    lod = 1.0                                            # raid band: see-through buildings, dimmed lanes


def _factory(net_cls, mode, link, t):
    def make(P):
        pos = P.gpos * LY.K
        net = (net_cls or ND.Net)(pos, mode=mode, link=link)
        net.lod = 1.0
        net.t = t

        def pool(x, y, r, k=1.0):
            X, Y, Z = P.gpos[..., 0], P.gpos[..., 1], P.gpos[..., 2]
            return np.exp(-((np.hypot(X - x / LY.K, Y - y / LY.K) / (r / LY.K)) ** 2) * 1.6) * (Z < 40) * k
        net.pool = pool
        return net
    return make


def finish(tag, mode="night", decorate=None, prefix="", frame=0, heat=1, fog=None, tilt=1.0, seed=1, creep=None, pools=None,
           link="lime", out_size=None, rain=True, focus=-12.0, box=None, net_cls=None, t=0.0):
    img, cam = P40.finish(prefix + tag if prefix else tag, decorate=decorate, pools=pools or (), out_size=(LY.W, LY.H), seed=seed,
                          t=t, rain=rain, fog=0.18 if fog is None else fog * 0.3, net_factory=_factory(net_cls, mode, link, t))
    if box is not None:
        x0, y0, x1, y1 = box
        img = img[y0:y1, x0:x1].copy()
    return img
