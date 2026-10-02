"""Round 20 street-plane grid: round 19 sockets with the NODE HEALTH combo, plus the decoy lure broadcast.

Health = how much of the socket is LIT. Full = fully lit. Damage fades the socket from its NORTH point (screen
top corner, current camera) toward its SOUTH point: the faded part takes the disabled look (dashed frame, dark
pins, dim glyph) but keeps the active status colour. A thin bright front marks the drain line.
At 0 the socket switches to the disabled colour + dashed outline (round 19 'disabled').
Numbers only appear on hover (or the Options 'always show health' toggle) as diegetic floats (ui20).
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
from netdecal19 import band, sstep, C, PAD_S, STATUS_COL, HARM, HALCYON, ICE, WHITE  # noqa: E402,F401

VIOLET = C(0.78, 0.35, 1.0)


class Net(N19.Net):
    def health_pad(self, key, state="holds", health=1.0, forecast=None, flash=None, exposed=False, t=0.0):
        """Socket with the lit-fraction health read. state: holds / home / disabled / seized / burnt."""
        if state in ("disabled", "seized", "burnt") or health <= 0.0:
            st = state if state in ("disabled", "seized", "burnt") else "disabled"
            return N19.Net.pad(self, key, st, integ=0.0, forecast=forecast, flash=flash, exposed=exposed, t=t)
        n = LY.NODES[key]
        x, y = n[0], n[1]
        S = PAD_S * (1.15 if key == "core" else 1.0)
        m = self._box(x, y, S * 1.3)
        em0, dk0 = self.em[m].copy(), self.dk[m].copy()
        # lit version (full, active)
        N19.Net.pad(self, key, state, integ=1.0, forecast=forecast, flash=flash, exposed=exposed, t=t)
        em_lit, dk_lit = self.em[m] - em0, self.dk[m] / np.maximum(dk0, 1e-6)
        self.em[m], self.dk[m] = em0, dk0
        # faded version: the disabled look, in the active colour, no forecast/flash repeats
        keep = STATUS_COL["disabled"]
        STATUS_COL["disabled"] = STATUS_COL[state]
        N19.Net.pad(self, key, "disabled", integ=0.0)
        STATUS_COL["disabled"] = keep
        em_fd, dk_fd = (self.em[m] - em0) * 0.32, self.dk[m] / np.maximum(dk0, 1e-6)
        self.em[m], self.dk[m] = em0, dk0
        # north -> south drain: b = screen-up offset; the socket's north corner is at +S * (|fh.x| + |fh.y|)
        dx, dy = self.X[m] - x, self.Y[m] - y
        b = dx * self.fh[0] + dy * self.fh[1]
        reach = S * 1.13 * (abs(self.fh[0]) + abs(self.fh[1]))
        thr = -reach + 2 * reach * health                     # lit where b < thr
        lit = 1 - sstep(thr - 0.35, thr + 0.35, b)
        front = band(np.abs(b - thr), -1, 0.22) * (np.maximum(np.abs(dx), np.abs(dy)) < S * 1.0)
        col = STATUS_COL[state]
        self.em[m] = em0 + em_lit * lit[:, None] + em_fd * (1 - lit[:, None]) + (front * 1.6)[:, None] * col
        self.dk[m] = dk0 * (dk_lit * lit + dk_fd * (1 - lit))

    def lure(self, key, t=0.0, k=1.0):
        """DECOY broadcast: violet rings pulsing outward from the socket over the street (pull 3)."""
        x, y = LY.NODES[key][0], LY.NODES[key][1]
        m = self._box(x, y, 40, self.GP)
        if not m.any():
            return
        r = np.hypot(self.X[m] - x, self.Y[m] - y)
        em = np.zeros(r.shape, np.float32)
        for i in range(3):
            rr = 12.0 + ((t + i / 3.0) % 1.0) * 26.0
            fade = 1.0 - ((t + i / 3.0) % 1.0)
            em += band(r, rr, rr + 0.7) * fade
        self.em[m] += (em * 1.3 * k)[:, None] * VIOLET * self.k

    def frost_link(self, a, b, amount, t=0.0):
        """A link frosting over from `a` toward `b` (0..1): ICE colour where frozen, normal beyond."""
        pa, pb = np.array(LY.pt(a), float), np.array(LY.pt(b), float)
        s, ac, L = N19.seg_coords(self.X, self.Y, pa, pb)
        m = (s > PAD_S) & (s < L - PAD_S) & (np.abs(ac) < 4.5) & self.G
        if not m.any():
            return
        ss, aa = s[m], ac[m]
        frozen = ss < PAD_S + (L - 2 * PAD_S) * amount
        cr = band(np.abs(np.mod(ss, 6.0) - 3.0 + aa * 0.6), -1, 0.18) * (np.abs(aa) < 3.6)
        tr = np.zeros(ss.shape, np.float32)
        for off in (-2.6, 0.0, 2.6):
            tr = np.maximum(tr, band(np.abs(aa - off), -1, 0.4))
        front = band(np.abs(ss - (PAD_S + (L - 2 * PAD_S) * amount)), -1, 0.8) * (np.abs(aa) < 4.2)
        self.em[m] += (frozen * (tr * 1.6 + cr * 1.2 + (np.abs(aa) < 4.0) * 0.25) + front * 2.0)[:, None] * ICE * self.k
