"""Round 38 netrun transit v2 -> transit_v2.png, transit_step.gif.

The run's own map (runmap38.py: 18 nodes, 7 layers + the start, branches merge) meandering THROUGH the city blocks
along the border link m1_d -> m2_d, at the close transit zoom (ortho 118; round 39 was 190), on the unified city model.
Paths are SINGLE dashed lines (designer round 38), drawn on the ground decal so buildings occlude them (x-ray hatch).
Locked round 37 netrun UI: option A rings (white / orange / lime) on normal-colour node-type stickers, the hidden
non-next-nodes rule (+ legend hover = show all), the corp-paper dossier, calm Heat B, the TARGET circle, the info window.

  transit_v2.png    the run mid-way, LEGEND HOVERED: all 18 nodes shown (white = not yet, grey = behind you)
  transit_step.gif  default (only walked / current / next / target) > pick 1 > the token rides the dashed path >
                    the next options light up > hover the legend: every node fades in

NET36=net_scope.json python transit38.py [png|gif|all]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
os.environ.setdefault("CARS39", "box")              # close zoom: the medium car LOD (boxes), not far dots
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import layout36 as L  # noqa: E402
import post39 as P  # noqa: E402
import screens39 as S  # noqa: E402
import runmap38 as RM  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402

OUT = os.path.dirname(HERE)
band = P.band if hasattr(P, "band") else None


def _runpath1(self, pts_lots, col, k=1.0, period=2.0, on=1.15, width=1.0):
    """SINGLE dashed line (designer round 38), on the ground, animated by t."""
    pts = [np.array(L.W(p), float) for p in pts_lots]
    acc = 0.0
    w = max(0.12, self.px(width))
    for i in range(len(pts) - 1):
        pa, pb = pts[i], pts[i + 1]
        d = pb - pa
        Ls = float(np.hypot(*d))
        if Ls < 1e-4:
            continue
        ux, uy = d / Ls
        lo, hi = np.minimum(pa, pb) - 1.5, np.maximum(pa, pb) + 1.5
        m = (self.X > lo[0]) & (self.X < hi[0]) & (self.Y > lo[1]) & (self.Y < hi[1]) & self.G
        if m.any():
            dx, dy = self.X[m] - pa[0], self.Y[m] - pa[1]
            s = dx * ux + dy * uy
            a = np.abs(-dx * uy + dy * ux)
            inside = (s > -w) & (s < Ls + w)
            tr = np.clip(1 - a / w, 0, 1) ** 0.6 * (np.mod(acc + s - self.t * 3, period) < on)
            self.dk[m] *= 1 - 0.3 * np.clip(1 - a / (w * 3), 0, 1) * inside
            self.em[m] += (tr * inside * k)[:, None] * col
        acc += Ls
    return None


P.Net36.runpath1 = _runpath1
GREYC = P.C(0.40, 0.40, 0.46)
STK = {"router": "router", "elite": "elite", "terminal": "terminal", "modem": "modem", "rack": "rack"}


def edge_state(e, st, walked):
    a, b = st[e["a"]], st[e["b"]]
    if e["a"] in walked and e["b"] in walked and walked.index(e["b"]) == walked.index(e["a"]) + 1:
        return "walked"
    if a == "current" and b == "option":
        return "option"
    if a in ("option", "white") and b in ("white", "target"):
        return "white"
    if b == "target" and a in ("option", "white"):
        return "white"
    if a in ("past", "walked", "current") and b in ("past",) or a == "past":
        return "past"
    return "hidden"


def render(tag, walked, cur, show_all=False, move=None, t=0.2, legend_hot=False, cursor=None, size=(1920, 1080), fade=1.0):
    run = RM.load()
    nodes = {n["id"]: n for n in run["nodes"]}
    st = RM.states(run, walked, cur, show_all)
    if move:                                              # mid-move: the edge being run is half lime
        st[move[0]] = "option"
    E = {}
    for e in run["edges"]:
        E[(e["a"], e["b"])] = edge_state(e, st, walked)
    if move:
        E[(cur, move[0])] = "moving"
    COL = {"walked": P.LIME, "option": P.ORANGE, "white": P.WHITE, "past": GREYC}

    def deco(net):
        for l in P.NET["links"]:                           # the Cell's own network, dim, under the run
            if l["state"] == "owned":
                net.link(l["pts"], P.LINK_COL["owned"], k=0.35, packets=False)
        for e in run["edges"]:
            s = E[(e["a"], e["b"])]
            if s == "hidden":
                continue
            if s == "moving":
                n = len(e["pts"])
                cutn = max(2, int(n * move[1]))
                net.runpath1(e["pts"][:cutn], P.LIME, k=1.5)
                net.runpath1(e["pts"][cutn - 1:], P.ORANGE, k=1.6)
                continue
            kk = {"walked": 1.4, "option": 1.7, "white": 0.75 * fade, "past": 0.6 * fade}[s]
            net.runpath1(e["pts"], COL[s], k=kk, width=1.0 if s in ("walked", "option") else 0.8)
        for n in P.NET["nodes"]:
            if n["state"] in ("owned", "core"):
                net.node(n)
    pools = [(L.W(nodes["L5_2"]["lot"])[0], L.W(nodes["L5_2"]["lot"])[1], 16.0, 0.32)]   # calm Heat B: one slow, soft sweep
    img, cam = P.finish(tag, decorate=deco, pools=pools, t=t, sky=False)   # no sky-lane cars over the run map
    cv = S.to_rgba(img)
    if cv.size != (1920, 1080):
        cv = cv.resize((1920, 1080), Image.LANCZOS)
    # stickers + option A rings
    for n in sorted(run["nodes"], key=lambda n: S.prj(cam, n["lot"])[1]):
        s = st[n["id"]]
        if s == "hidden" or n["kind"] == "start":
            continue
        if s in ("white", "past") and fade <= 0:
            continue
        x, y = S.prj(cam, n["lot"], 0)
        px = {"walked": 44, "current": 54, "option": 62, "target": 72, "white": 46, "past": 40}[s]
        sd = U32.node_sd(STK[n["kind"]], px)
        lift = 34 if s != "target" else 42
        op = 1.0 if s not in ("white", "past") else (0.95 if s == "white" else 0.7) * fade
        cv = RL.place_sticker(cv, sd, x, y - lift, angle=((sum(map(ord, n["id"])) % 9) - 4) * 0.8, opacity=op,
                              hover=0.35 if s == "option" else 0.0, shadow=op)
        col = {"walked": S.LIME, "current": S.LIME, "option": S.MER, "white": S.WHITE, "past": (110, 106, 120)}.get(s)
        if col and (s not in ("white", "past") or fade > 0.3):
            cv = S.ring(cv, x, y - lift, px / 2 + 8, col, w=5 if s in ("option", "current") else 3,
                        glow={"option": 0.9, "current": 0.9, "walked": 0.5}.get(s, 0.0))
    # numbered choices on the options (the finite next step)
    if not move:
        opts = sorted([i for i, s in st.items() if s == "option"], key=lambda i: S.prj(cam, nodes[i]["lot"])[0])
        for k, i in enumerate(opts):
            x, y = S.prj(cam, nodes[i]["lot"], 0)
            cv = U32.chip(cv, (x - 44, y - 78), str(k + 1), S.MER, 17, bright=True)
    # the operative token: on the current node or riding the path
    if move:
        e = next(e for e in run["edges"] if e["a"] == cur and e["b"] == move[0])
        pts = e["pts"]
        q = pts[min(len(pts) - 1, int((len(pts) - 1) * move[1]))]
        x, y = S.prj(cam, q, 0)
    else:
        x, y = S.prj(cam, nodes[cur]["lot"], 0)
    cv = RL.place_sticker(cv, U32.token_sd(52), x + 30, y - 90, angle=-14, hover=0.6)
    # TARGET (the Site's Server Rack)
    tx, ty = S.prj(cam, nodes["L7_0"]["lot"], 0)
    pr = RL.pen(RL.GP_RED, seed=381)
    pr.circle(tx, ty - 42, 72, 60, width=9)
    pr.text("TARGET", tx + 120, ty - 70, 30, angle=-6)
    cv = RL.ink(cv, pr)
    sx, sy = S.prj(cam, nodes["L0_0"]["lot"], 0)
    cv = U32.chip(cv, (sx + 74, sy + 34), "YOUR NODE (start)", S.LIME, 13, bright=True)
    cv = hud(cv, legend_hot)
    if cursor:
        cv = S.cursor(cv, *cursor)
    return RL.bloom(cv, 0.12, 0.82, 8)


def hud(cv, legend_hot):
    cv = RL.place_sticker(cv, RL.sticker_word(["NETRUN"], 58, fills=["yellow"], seed=63), 150, 54, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 52: HUNTED")
    dz = dz.resize((int(dz.width * 0.62), int(dz.height * 0.62)), Image.LANCZOS)
    cv = RL.drop_shadow(cv, dz, 18, 100, blur=12, off=(6, 10), op=0.6)
    site = P.NODES["m2_d"]
    cv = R.node_info(cv, (1540, 860, 1900, 1036), site.get("name", "SITE").upper()[:24], "T%d" % site.get("tier", 2),
                     ["+12 Schematics", "an Exploit"], "Priority exchange")
    cv = U32.term_button(cv, (18, 990, 200, 1056), "DECK", "[D]")
    cv = U32.term_button(cv, (212, 990, 394, 1056), "MENU", "[ESC]")
    c = RL.CRT(1120, 46, U32.LIME if legend_hot else U32.CYAN, None, header=False, seed=357)
    x0 = 14
    for kind, lab in (("router", "COMBAT"), ("elite", "ELITE"), ("terminal", "EVENT"), ("modem", "SHOP"), ("rack", "RACK")):
        ic = U32.icon(kind, 28)
        c.im.alpha_composite(ic, (x0, 9))
        x0 += 32 + int(c.text((x0 + 32, 13), lab, 14, (215, 225, 230))) + 14
    for col, s in ((S.LIME, "walked"), (S.MER, "next"), (S.WHITE, "not yet")):
        c.d.ellipse([x0 + 2, 14, x0 + 20, 32], outline=col + (255,), width=3)
        x0 += 26 + int(c.text((x0 + 26, 13), s, 14, (215, 225, 230))) + 12
    c.text((x0 + 4, 13), "| SHOWING ALL NODES" if legend_hot else "| HOVER: SHOW ALL", 14, S.LIME if legend_hot else U32.CYAN)
    return RL.paste(cv, c.finish(scan=0.15), 410, 1010)


WALKED = ["L0_0", "L1_1", "L2_1"]


def png():
    img = render("t_run38", WALKED, "L2_1", show_all=True, legend_hot=True, cursor=(1300, 1032))
    img.convert("RGB").save(os.path.join(OUT, "transit_v2.png"), optimize=True)
    print("saved transit_v2.png")


def gif():
    frames, durs = [], []

    def add(im, ms):
        frames.append(im.convert("RGB"))
        durs.append(ms)
    add(render("t_run38g", WALKED, "L2_1", t=0.0), 1400)
    run = RM.load()
    opts = [e["b"] for e in run["edges"] if e["a"] == "L2_1"]
    tgt = "L3_1" if "L3_1" in opts else opts[0]
    for i, m in enumerate((0.25, 0.5, 0.75)):
        add(render("t_run38g", WALKED, "L2_1", move=(tgt, m), t=0.15 * (i + 1)), 160)
    w2 = WALKED + [tgt]
    add(render("t_run38g", w2, tgt, t=0.6), 1600)
    add(render("t_run38g", w2, tgt, show_all=True, legend_hot=True, cursor=(1300, 1032), t=0.7, fade=0.5), 160)
    add(render("t_run38g", w2, tgt, show_all=True, legend_hot=True, cursor=(1300, 1032), t=0.8), 2000)
    out = os.path.join(OUT, "transit_step.gif")
    size = U32.save_gif(frames, durs, out, size=(960, 540))
    if size > 3_000_000:
        size = U32.save_gif(frames, durs, out, size=(800, 450))
    print("saved transit_step.gif", size)


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("png", "all"):
        png()
    if w in ("gif", "all"):
        gif()
