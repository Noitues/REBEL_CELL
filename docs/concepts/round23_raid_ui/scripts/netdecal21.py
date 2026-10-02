"""Round 21 street-plane grid: health read v2 + a frozen link that looks frozen.

Health (designer, round 21): the OUTLINE (frame + pins) keeps its active colour and the node ICON (glyph + inner
square) stays fully lit the whole time; only the inner LIT FILL drains, north point -> south point. The drained part
shows the dim hatch of the disabled look in the active colour. At 0 the socket switches to the disabled look.
"""
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import netdecal19 as N19  # noqa: E402
import netdecal20 as N20  # noqa: E402
from netdecal19 import band, sstep, C, PAD_S, STATUS_COL, ICE  # noqa: E402,F401


class Net(N20.Net):
    def health_pad(self, key, state="holds", health=1.0, forecast=None, flash=None, exposed=False, t=0.0):
        if state in ("disabled", "seized", "burnt") or health <= 0.0:
            st = state if state in ("disabled", "seized", "burnt") else "disabled"
            return N19.Net.pad(self, key, st, integ=0.0, forecast=forecast, flash=flash, exposed=exposed, t=t)
        n = LY.NODES[key]
        x, y = n[0], n[1]
        S = PAD_S * (1.15 if key == "core" else 1.0)
        m = self._box(x, y, S * 1.3)
        em0 = self.em[m].copy()
        # the full lit socket (outline, pins, track, icon, forecast / flash) from round 19
        N19.Net.pad(self, key, state, integ=1.0, forecast=forecast, flash=flash, exposed=exposed, t=t)
        add = self.em[m] - em0
        dx, dy = self.X[m] - x, self.Y[m] - y
        cheb = np.maximum(np.abs(dx), np.abs(dy))
        b = dx * self.fh[0] + dy * self.fh[1]
        reach = S * 0.86 * (abs(self.fh[0]) + abs(self.fh[1]))
        thr = -reach + 2 * reach * health
        lit = 1 - sstep(thr - 0.3, thr + 0.3, b)
        col = STATUS_COL[state]
        interior = (cheb < S * 0.86).astype(np.float32)
        track = band(cheb, S * 0.70, S * 0.78)
        # icon = the inner square ring + glyph area; keep it lit (exclude it from the drain)
        icon = (cheb < S * 0.62).astype(np.float32)
        # drained part: remove the track's lit share there (outline + icon untouched)
        drain = (1 - lit) * track * (1 - icon)
        add = add * (1 - 0.88 * drain)[:, None]
        # the lit FILL: a soft glow of the active colour inside the socket, north part drains away
        fill = interior * (1 - band(cheb, S * 0.55, S * 0.62)) * lit * 0.22
        hatch = interior * (1 - icon) * (1 - lit) * (np.mod((dx - dy) * 0.5, 1.0) < 0.28) * 0.14
        front = band(np.abs(b - thr), -1, 0.22) * interior * (1 - icon)
        self.em[m] = em0 + add + (fill + hatch + front * 1.4)[:, None] * col * self.k

    def link(self, a, b, state="ok", t=0.0, packets=False):
        if state != "frozen":
            return N19.Net.link(self, a, b, state, t=t, packets=packets)
        # round 19 frozen trace look (kept), the frost crust is added in screen space (ui21.frost)
        return N19.Net.link(self, a, b, "frozen", t=t, packets=False)
