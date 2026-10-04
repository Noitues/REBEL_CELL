"""flicker_sign.py - round 32 (MAINFRAME; copied from round 27): renamed MODEM-style circuit-board neon signs with a Cell takeover.

Reuses the round 4 sign pipeline (modem_sign_r4.py, a copy): plate facets, hollow double-line tubes,
PCB traces routed around the letters, chips, self-lit plate and glow. What's new:
  - any layout of letters (vertical hero word + horizontal rows), every letter its own element;
  - takeover rendering: chosen letters (or a partial stroke of a letter) lit in Cell lime, the rest dark
    glass; letters never used by the message get broken tubes (gaps + soot);
  - per-frame levels for a flicker sequence.
Plate stays 250x1034 (canvas 390x1174) so it drops into the round 12 facade at the same anchor.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modem_sign_r4 as M          # noqa: E402
from lightpen import gblur, tonemap  # noqa: E402

PW, PH, MARGIN, CW, CH = M.PW, M.PH, M.MARGIN, M.CW, M.CH
PINK, CYAN, PINK_OFF, CYAN_OFF = M.PINK, M.CYAN, M.PINK_OFF, M.CYAN_OFF
LIME = np.array([0.62, 1.0, 0.16], np.float32)        # Cell takeover colour
TRACE_RED = np.array([1.0, 0.12, 0.14], np.float32)
# round 32 palettes: (tube colour, unlit glass tint, trace colour)
PAL = {
    "blue": (np.array([0.22, 0.52, 1.0], np.float32), np.array([0.12, 0.18, 0.32], np.float32),
             np.array([0.25, 0.6, 1.0], np.float32)),
    "red": (np.array([1.0, 0.09, 0.10], np.float32), np.array([0.32, 0.10, 0.10], np.float32),
            np.array([1.0, 0.16, 0.12], np.float32)),
}
SIGN_PAL = "blue"          # palette of the 'normal' letters (set by the caller)
MSG_COL = np.array([1.0, 0.09, 0.10], np.float32)   # takeover message colour

# ------------------------------------------------------------------ extra glyphs (same chamfered style)
M.LET.update({
    "A": [[(0, 1), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.22), (1, 1)], [(0, 0.56), (1, 0.56)]],
    "G": [[(1, 0.16), (0.84, 0), (0.16, 0), (0, 0.16), (0, 0.84), (0.16, 1), (0.84, 1), (1, 0.84), (1, 0.56),
           (0.52, 0.56)]],
    "I": [[(0.5, 0), (0.5, 1)], [(0.18, 0), (0.82, 0)], [(0.18, 1), (0.82, 1)]],
    "K": [[(0, 0), (0, 1)], [(1, 0), (0, 0.56)], [(0.34, 0.38), (1, 1)]],
    "L": [[(0, 0), (0, 1), (1, 1)]],
    "F": [[(1, 0), (0, 0), (0, 1)], [(0, 0.5), (0.74, 0.5)]],
    "N": [[(0, 1), (0, 0), (1, 1), (1, 0)]],
    "T": [[(0, 0), (1, 0)], [(0.5, 0), (0.5, 1)]],
    "U": [[(0, 0), (0, 0.84), (0.16, 1), (0.84, 1), (1, 0.84), (1, 0)]],
    "&": [[(1, 1), (0.22, 0.42), (0.22, 0.14), (0.38, 0), (0.62, 0), (0.78, 0.14), (0.78, 0.3), (0.08, 0.7),
           (0.08, 0.88), (0.24, 1), (0.6, 1), (1, 0.62)]],
})
# partial strokes: a sub-shape of a letter that reads as another letter
ALT = {("A", "o"): [[(0, 0.56), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.22), (1, 0.56), (0, 0.56)]],
       ("R", "o"): [[(0, 0.5), (0, 0), (0.8, 0), (1, 0.14), (1, 0.38), (0.8, 0.5), (0, 0.5)]]}

# ------------------------------------------------------------------ layouts
LAYOUTS = {
    "mainframe": dict(name="MAINFRAME", rows=[
        dict(text="MAINFRAME", mode="v", w=92, h=88, y0=40, step=106, W=17, t=3.0, col="pink")]),
    "market": dict(name="MARKET NEON", rows=[
        dict(text="MARKET", mode="v", w=100, h=100, y0=44, step=116, W=20, t=3.4, col="pink"),
        dict(text="NEON", mode="h", y=772, w=46, h=72, gap=8, W=13, t=2.8, col="cyan")]),
    "neonmodem": dict(name="NEON MODEM / REPAIR & MAINTENANCE", rows=[
        dict(text="NEON", mode="h", y=40, w=42, h=56, gap=8, W=13, t=2.8, col="cyan"),
        dict(text="MODEM", mode="v", w=104, h=104, y0=116, step=124, W=20, t=3.4, col="pink"),
        dict(text="REPAIR &", mode="h", y=752, w=22, h=46, gap=3.5, W=9, t=2.2, col="cyan"),
        dict(text="MAINTENANCE", mode="h", y=816, w=16.4, h=42, gap=2.4, W=7, t=1.8, col="cyan")]),
    "repairs": dict(name="REPAIRS / SECURE UPGRADES", rows=[
        dict(text="REPAIRS", mode="v", w=96, h=92, y0=40, step=108, W=18, t=3.2, col="pink"),
        dict(text="SECURE", mode="h", y=812, w=30, h=48, gap=5, W=11, t=2.5, col="cyan"),
        dict(text="UPGRADES", mode="h", y=876, w=22, h=44, gap=3.5, W=9, t=2.2, col="cyan")]),
    "techhelp": dict(name="TECH HELP / CELL / REPAIR", rows=[
        dict(text="TECH HELP", mode="h", y=40, w=21, h=48, gap=3, W=9, t=2.2, col="cyan"),
        dict(text="CELL", mode="v", w=104, h=130, y0=112, step=152, W=22, t=3.6, col="pink"),
        dict(text="REPAIR", mode="h", y=740, w=30, h=56, gap=5, W=11, t=2.5, col="cyan")]),
}

# takeover sequences: words as lists of letter indices into the sign's letters (spaces ignored, reading
# order); an index can be (i, "o") for a partial stroke.
SEQUENCES = {
    # MAINFRAME: M0 A1 I2 N3 F4 R5 A6 M7 E8
    "mainframe": [("NO", [3, (5, "o")]), ("MoRE", [0, (1, "o"), 5, 8]), ("MAN", [0, 1, 3])],
    "iamin": [("I AM", [2, 6, 7]), ("IN", [2, 3])],
    "noname": [("NO", [3, (5, "o")]), ("NAME", [3, 6, 7, 8])],
    "armme": [("ARM", [1, 5, 7]), ("ME", [7, 8])],
    "aiframe": [("AI", [1, 2]), ("FRAME", [4, 5, 6, 7, 8])],
    "market": [("NO", [6, 8]), ("MRE", [0, 2, 4]), ("MAN", [0, 1, 9])],
    "market_more": [("NO", [6, 8]), ("MoRE", [0, (1, "o"), 2, 4]), ("MAN", [0, 1, 9])],
    "neonmodem": [("NO", [0, 2]), ("MORE", [4, 5, 9, 10]), ("MAN", [16, 17, 19])],
    "repairs": [("RISE", [0, 4, 6, 8]), ("UP", [13, 14]), ("US", [10, 20])],
    "techhelp": [("THE", [0, 3, 5]), ("CELL", [8, 9, 10, 11]), ("HERE", [4, 5, 12, 13])],
}


def letters(layout):
    """[(key, ch, x, y, w, h, W, t, col)] in reading order (spaces skipped)."""
    out = []
    for r, row in enumerate(layout["rows"]):
        txt = row["text"]
        if row["mode"] == "v":
            x = (PW - row["w"]) / 2
            for i, ch in enumerate(txt):
                out.append((f"r{r}_{i}", ch, x, row["y0"] + i * row["step"], row["w"], row["h"], row["W"],
                            row["t"], row["col"]))
        else:
            sp = row["w"] * 0.55
            tot = sum(sp if c == " " else row["w"] for c in txt) + (len(txt) - 1) * row["gap"]
            x = (PW - tot) / 2
            for i, ch in enumerate(txt):
                if ch != " ":
                    out.append((f"r{r}_{i}", ch, x, row["y"], row["w"], row["h"], row["W"], row["t"], row["col"]))
                x += (sp if ch == " " else row["w"]) + row["gap"]
    return out


def _tube(strokes, x, y, w, h, W, t):
    A, B = M._canvas(), M._canvas()
    da, db = ImageDraw.Draw(A), ImageDraw.Draw(B)
    for stroke in strokes:
        pts = [(x + W / 2 + u * (w - W), y + W / 2 + v * (h - W)) for u, v in stroke]
        M._poly_stroke(da, pts, W)
        M._poly_stroke(db, pts, W - 2 * t)
    a, b = np.asarray(A, np.float32), np.asarray(B, np.float32)
    ring = Image.fromarray(np.clip(a - b, 0, 255).astype(np.uint8))
    return M._arr(ring), M._arr(A)


class FlickerSign:
    def __init__(self, layout_key, seed=7):
        self.layout = LAYOUTS[layout_key]
        self.lets = letters(self.layout)
        M.element_list = lambda: [(k, ch, x, y, w, h, W, t, col) for k, ch, x, y, w, h, W, t, col in self.lets]
        M.ELEMENTS = ["frame"] + [l[0] for l in self.lets]
        self.base = M.Sign(seed=seed)          # plate, traces, chips, frame + tube masks for our letters
        self.keys = [l[0] for l in self.lets]
        self.col = {l[0]: l[8] for l in self.lets}
        self.alt = {}
        rng = np.random.default_rng(seed + 11)
        self.brk = {}
        self.soot = np.zeros((CH, CW), np.float32)
        for k, ch, x, y, w, h, W, t, col in self.lets:
            for (c, v), strokes in ALT.items():
                if c == ch:
                    self.alt[(k, v)] = _tube(strokes, x, y, w, h, W, t)[0]
            # broken-tube mask: 1-2 gaps where the glass is snapped, soot around them
            gm = Image.new("L", (CW * M.SR, CH * M.SR), 255)
            sm = Image.new("L", (CW * M.SR, CH * M.SR), 0)
            dg, ds = ImageDraw.Draw(gm), ImageDraw.Draw(sm)
            strokes = M.LET[ch]
            for _ in range(int(rng.integers(1, 3))):
                st = strokes[int(rng.integers(0, len(strokes)))]
                j = int(rng.integers(0, len(st) - 1))
                f = rng.uniform(0.25, 0.75)
                u = st[j][0] + (st[j + 1][0] - st[j][0]) * f
                v = st[j][1] + (st[j + 1][1] - st[j][1]) * f
                px, py = M._P(x + W / 2 + u * (w - W), y + W / 2 + v * (h - W))
                r = W * 0.75 * M.SR
                dg.ellipse([px - r, py - r, px + r, py + r], fill=0)
                rs = W * 2.2 * M.SR
                ds.ellipse([px - rs, py - rs, px + rs, py + rs], fill=150)
            self.brk[k] = M._arr(gm)
            self.soot = np.maximum(self.soot, gblur(M._arr(sm), 4))

    def message_keys(self, idx_list):
        out = {}
        for it in idx_list:
            i, var = (it if isinstance(it, tuple) else (it, None))
            out[self.keys[i]] = var
        return out

    def words(self, seq_key):
        return [(w, self.message_keys(ix)) for w, ix in SEQUENCES[seq_key]]

    def used_keys(self, seq_key):
        s = set()
        for _, mk in self.words(seq_key):
            s |= set(mk)
        return s

    def render(self, normal=None, msg=None, frame=1.0, traces=1.0, trace_col=None, broken=None,
               pulse_t=None, msg_level=1.0):
        """normal: {key: level | ('f', level)} pink/cyan; msg: {key: variant|None} lit lime at msg_level
        (a key can be ('f', v) partial flicker via msg_level tuple); broken: set of keys with snapped tubes."""
        b = self.base
        normal = normal or {}
        msg = msg or {}
        broken = broken or set()
        emis = np.zeros((CH, CW, 3), np.float32)
        glass = np.zeros((CH, CW, 3), np.float32)
        for k in ["frame"] + self.keys:
            t = b.tubes[k]
            if k in broken:
                t = t * self.brk[k]
            col, off, _ = PAL[SIGN_PAL]
            lit_mask, lv, c = None, 0.0, col
            if k == "frame":
                lit_mask, lv = t, frame
            elif k in msg:
                var = msg[k]
                lit_mask = self.alt[(k, var)] if var else t
                lv, c = msg_level, MSG_COL
            elif k in normal:
                lit_mask, lv = t, normal[k]
            part = None
            if isinstance(lv, tuple):
                part, lv = b.bands.get(k, 1.0), lv[1]
            if lit_mask is not None and lv > 0:
                m = lit_mask * (part if part is not None else 1.0)
                warm = c * (0.55 + 0.45 * lv) + np.array([0.2, 0.0, 0.35]) * (1 - lv)
                emis += warm[None, None] * (m * lv * 1.55)[..., None]
                core = np.clip((gblur(lit_mask, 0.6) - 0.55) / 0.45, 0, 1) * (part if part is not None else 1.0)
                emis += np.array([1.0, 0.96, 0.92])[None, None] * (core * lv * 0.85)[..., None]
                glass += off[None, None] * np.clip(t - lit_mask, 0, 1)[..., None]
                glass += off[None, None] * (lit_mask * (1 - 0.6 * lv))[..., None]
            else:
                glass += off[None, None] * t[..., None] * 0.9
            glass += off[None, None] * (0.2 * b.letter_fill[k] * (self.brk[k] if k in broken else 1))[..., None]
        tm, pdm, pum = M.draw_traces(b.traces, 1.0, pulse_t, b.phase)
        tc = PAL[SIGN_PAL][2] if trace_col is None else trace_col
        emis += tc * (tm * 0.55 + pdm * 0.8)[..., None] * traces
        if pulse_t is not None:
            emis += (0.5 * tc + 0.5) * (pum * 2.4)[..., None] * traces
        glass += np.array([0.30, 0.17, 0.09], np.float32) * (tm * 0.55 + pdm * 0.8)[..., None] * (1 - 0.7 * min(1, traces))
        emis += tc * (b.chip_pins * 0.45)[..., None] * traces
        emis += PAL[SIGN_PAL][2] * (gblur(b.chip_led, 0.7) * 2.2)[..., None] * min(1.0, traces + 0.3)
        alb = b.plate_alb * (1 - b.chip_m[..., None]) + b.chip_alb * b.chip_m[..., None] + glass
        if broken:
            alb = alb * (1 - 0.75 * self.soot[..., None])
        self_light = np.stack([gblur(emis[..., c], 7) * 1.1 + gblur(emis[..., c], 24) * 1.2 for c in range(3)], -1)
        plate_rgb = alb * (0.5 + self_light * 2.4) + emis
        glow = np.stack([0.45 * gblur(emis[..., c], 2.0) + 0.34 * gblur(emis[..., c], 7) +
                         0.26 * gblur(emis[..., c], 20) + 0.14 * gblur(emis[..., c], 44) for c in range(3)], -1)
        pm = b.plate_m[..., None]
        return dict(plate=tonemap(plate_rgb), glow=glow, alpha=b.plate_m, rgb=tonemap(plate_rgb * pm + glow))

    # convenience states
    def state_normal(self, pulse_t=0.0):
        return self.render(normal={k: 1.0 for k in self.keys}, frame=1.0, traces=1.0, pulse_t=pulse_t)

    def state_word(self, seq_key, wi, level=1.0):
        used = self.used_keys(seq_key)
        dead = set(self.keys) - used
        return self.render(msg=self.words(seq_key)[wi][1], frame=0.0, traces=0.22, trace_col=TRACE_RED,
                           broken=dead, msg_level=level)


def save_rgba(res, path):
    rgb = (np.clip(res["rgb"], 0, 1) * 255 + 0.5).astype(np.uint8)
    a = (np.clip(res["alpha"], 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, a]), "RGBA").save(path)
