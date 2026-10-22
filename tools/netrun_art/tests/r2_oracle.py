"""Test helper (street P2-P4 step 1): runs the art-pass `street_r2` modules unchanged, from a temp copy, on the plate's own input.

Not a test. `run(art_root, seed, work)` copies `docs/concepts/route_map_graph/{street_r2,storyboard}` python (and the storyboard's
scratch layout json) out of an art-pass checkout, runs `layout_pass(seed)` and `plan_pass(seed)` in a subprocess with the scratch
folder pointed at `work`, and returns the products as Python objects. `run_kits` execs `r2_kits.py` the way `r2_scene.py` does (with
recording accumulators); `run_signs` runs `r2_signs.py` with the PIL draw calls recorded. Used by `gen_r2_fixtures.py` (writes the
committed fixtures) and by the live golden test (skipped when no art-pass checkout is present). Reads the checkout read-only.
"""
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict

RMG = os.path.join("docs", "concepts", "route_map_graph")

_DRIVER = r'''
import json, os, sys
work, seed = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, os.path.join(work, "rmg", "street_r2", "scripts"))
sys.dont_write_bytecode = True
import r2_rules as R
scr = os.path.join(work, "scr")
os.makedirs(scr, exist_ok=True)
R.SCR = scr
R.layout_pass(seed)
plan = R.plan_pass(seed)
D = json.load(open(os.path.join(scr, "derive_v3.json")))
lay = json.load(open(os.path.join(scr, "unified_r2_s%d.json" % seed)))
log = json.load(open(os.path.join(scr, "layout_log_s%d.json" % seed)))
json.dump(dict(derive=D, plan=plan, layout_log=log, buildings=lay["buildings"]), open(os.path.join(work, "oracle_out.json"), "w"))
'''

_KIT_DRIVER = r'''
import json, math, os, random, sys
work = sys.argv[1]
sys.path.insert(0, os.path.join(work, "rmg", "street_r2", "scripts"))
sys.dont_write_bytecode = True
import r2_facade as FC


class Faces:
    def __init__(self):
        self.faces, self.prims = [], []

    def face(self, pts, col, bid, fj=None):
        self.faces.append(dict(pts=[list(p) for p in pts], col=list(col), bid=list(bid) if isinstance(bid, (tuple, list)) else bid, fj=fj))

    def prim(self, kind, *args):
        self.prims.append([kind] + [list(a) if isinstance(a, (tuple, list)) else a for a in args])


state = dict(n=0, SOLID=None)


def rid():
    state["n"] += 1
    return state["n"]


def cyl36(cx, cy, z0, z1, rad, col, n=8):
    state["SOLID"].prim("cyl36", cx, cy, z0, z1, rad, col)


def box(x0, y0, z0, x1, y1, z1, col, taper=0.0, facet=True, bid=None, top=True):
    state["SOLID"].prim("box", x0, y0, z0, x1, y1, z1, col)


def beam(p0, p1, w, col, acc=None, bid=None):
    (acc or state["SOLID"]).prim("beam", p0, p1, w, col)


ns = dict(math=math, FC=FC, rid=rid, cyl36=cyl36, box=box, beam=beam, RED=(1.0, 0.15, 0.12), ANTS=[],
          WIN_COLS=[(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)])
exec(open(os.path.join(work, "rmg", "street_r2", "scripts", "r2_kits.py"), encoding="utf-8").read(), ns)
out = []
for cs in json.load(open(os.path.join(work, "kit_cases.json"))):
    state["n"] = 0
    r = random.Random(cs["seed"])
    if cs["op"] == "face":
        accs = {k: Faces() for k in ("conc", "glass", "panel", "win", "neon")}
        ns["kit_face"](cs["kit"], cs["a"], cs["c"], cs["z0"], cs["z1"], cs["nx"], cs["ny"], cs["col"], r, accs, module=cs["module"],
                       fl=cs.get("fl", 1.9), lit_low=cs.get("lit_low"), lite=cs.get("lite", False), rh=cs.get("rh"))
        out.append({k: v.faces for k, v in accs.items()})
    else:
        solid, neon, kinds = Faces(), Faces(), set()
        state["SOLID"] = solid
        ns["SOLID"] = solid
        ns["ANTS"].clear()
        ns["roof_clutter"](cs["kit"], cs["top"], cs["zt"], r, solid, neon, kinds)
        out.append(dict(faces=solid.faces, prims=solid.prims, neon=neon.faces, kinds=sorted(kinds), ants=[list(a) for a in ns["ANTS"]]))
json.dump(out, open(os.path.join(work, "kit_out.json"), "w"))
'''

_SIGN_DRIVER = r'''
import json, os, random, sys
work, fonts = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(work, "rmg", "street_r2", "scripts"))
sys.dont_write_bytecode = True
import r2_signs as S
K = S.K
K.ANTON = os.path.join(fonts, "Anton-Regular.ttf")
K.MONO = os.path.join(fonts, "ShareTechMono-Regular.ttf")
REG, TABLE, ops, flags = {}, {}, [], dict(in_grad=False)
_F = K.F


def F(path, size, var=None):
    f = _F(path, size, var)
    REG[id(f)] = ("anton" if "Anton" in path else "mono", int(size))
    return f


K.F = F


def norm(v):
    return [norm(e) for e in v] if isinstance(v, (list, tuple)) else v


class Rec:
    def __init__(self, real):
        self.real = real

    def textbbox(self, xy, s, font=None, anchor=None, **kw):
        b = self.real.textbbox(xy, s, font=font, anchor=anchor, **kw)
        name, size = REG[id(font)]
        TABLE.setdefault((name, size, s), (b[2] - b[0], b[3] - b[1]))
        return b

    def text(self, xy, s, font=None, fill=None, anchor=None, **kw):
        name, size = REG[id(font)]
        ops.append(dict(op="text", xy=norm(xy), s=s, font=name, size=size, fill=norm(fill), anchor=anchor))
        return self.real.text(xy, s, font=font, fill=fill, anchor=anchor, **kw)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        ops.append(dict(op="rect", box=norm(xy), fill=norm(fill) if fill is not None else None,
                        outline=norm(outline) if outline is not None else None, width=width))
        return self.real.rectangle(xy, fill=fill, outline=outline, width=width)

    def ellipse(self, xy, fill=None, outline=None, width=1):
        ops.append(dict(op="ellipse", box=norm(xy), outline=norm(outline), width=width))
        return self.real.ellipse(xy, fill=fill, outline=outline, width=width)

    def line(self, xy, fill=None, width=0, **kw):
        if not flags["in_grad"]:
            ops.append(dict(op="line", pts=norm(xy), fill=norm(fill), width=width))
        return self.real.line(xy, fill=fill, width=width, **kw)

    def __getattr__(self, n):
        return getattr(self.real, n)


class IDraw:
    @staticmethod
    def Draw(im):
        return Rec(S.PILDraw.Draw(im))


class IImage:
    def __init__(self, real):
        self.real = real

    def new(self, mode, size, color=0):
        if not flags["in_grad"]:
            ops.append(dict(op="fill", w=size[0], h=size[1], col=norm(color)))
        return self.real.new(mode, size, color)

    def merge(self, mode, bands):
        ops.append(dict(op="holo_shift", r=-3, b=3))
        return self.real.merge(mode, bands)

    def __getattr__(self, n):
        return getattr(self.real, n)


S.PILDraw = S.ImageDraw
S.ImageDraw = IDraw
S.Image = IImage(S.Image)
_grad = S.grad


def grad(w, h, top, bot):
    ops.append(dict(op="grad", w=w, h=h, top=norm(top), bot=norm(bot)))
    flags["in_grad"] = True
    try:
        return _grad(w, h, top, bot)
    finally:
        flags["in_grad"] = False


def glow(im, k=0.55, r=8):
    ops.append(dict(op="glow", k=k, r=r))
    return im


def ad(name, aspect):
    ops.append(dict(op="ad", name=name, aspect=aspect))
    return S.Image.real.new("RGB", (1, 1))


S.grad, S.glow, S.ad = grad, glow, ad
plan = json.load(open(os.path.join(work, "sign_plan.json")))
specs = {}
for s in plan["signs"]:
    t = s["tex"]
    r = random.Random(t["seed"])
    aspect = (s["u1"] - s["u0"]) / max(0.05, s["z1"] - s["z0"])
    st = t["style"]
    ops.clear()
    if st == "box":
        im = S.box(t["word"], t.get("sub", ""), s["col"], aspect, r)
    elif st == "blade":
        im = S.blade(t["word"], t.get("sub", ""), s["col"], aspect, r)
    elif st == "wall":
        im = S.wall(t["word"], t.get("sub", ""), s["col"], aspect, r)
    elif st == "ad":
        im = S.ad(t["ad"], aspect)
    elif st == "holo":
        im = S.holo(t["word"], t.get("sub", ""), s["col"], aspect, r)
    else:
        im = S.shop(t["word"], s["col"], aspect, r)
    specs[s["id"]] = dict(w=None if st == "ad" else im.size[0], h=None if st == "ad" else im.size[1], ops=list(ops))
json.dump(dict(specs=specs, measure=[[k[0], k[1], k[2], v[0], v[1]] for k, v in TABLE.items()]), open(os.path.join(work, "sign_out.json"), "w"))
'''


def _ignore(_d: str, names):
    keep = (".py", ".json")
    out = []
    for n in names:
        p = os.path.join(_d, n)
        if os.path.isdir(p):
            if n in ("render_s1", "render_s2", "plates", "stills", "__pycache__"):
                out.append(n)
        elif not n.endswith(keep):
            out.append(n)
    return out


def _prep(art_root: str, work: str) -> None:
    """Copy the art-pass python (street_r2 scripts, storyboard scripts and layout json) into `work/rmg` once."""
    if os.path.exists(os.path.join(work, "rmg")):
        return
    os.makedirs(work, exist_ok=True)
    src = os.path.join(art_root, RMG)
    for sub in ("street_r2", "storyboard"):
        shutil.copytree(os.path.join(src, sub), os.path.join(work, "rmg", sub), ignore=_ignore)
    _drop_mega(os.path.join(work, "rmg", "street_r2", "scripts", "r2_rules.py"))


# The designer dropped the megastructure (2026-10-22, DECISIONS): the copy of the art-pass plan_pass places none and its check does
# not ask for one, the same drop our twins carry, so the golden comparison holds everything else to the plate.
MEGA_DROP = [
    ("    if cands:\n        cands.sort(key=lambda c_: (-c_[0], c_[1]))", "    if False:\n        cands.sort(key=lambda c_: (-c_[0], c_[1]))"),
    ("signs=signs, mega=mega, lamps=lamps", "signs=signs, lamps=lamps"),
    ("                                 megastructure=plan[\"mega\"] and plan[\"mega\"][\"kind\"],\n", ""),
    ("S[\"signs_on_screen_min\"]\n                                 and plan[\"mega\"] is not None)", "S[\"signs_on_screen_min\"])"),
]


def _drop_mega(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        s = f.read()
    for a, b in MEGA_DROP:
        if s.count(a) != 1:
            raise RuntimeError("r2_rules.py changed: megastructure drop patch does not apply: " + a[:60])
        s = s.replace(a, b)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def _spawn(work: str, name: str, source: str, *args: str) -> None:
    path = os.path.join(work, name)
    with open(path, "w") as f:
        f.write(source)
    r = subprocess.run([sys.executable, path, work, *args], capture_output=True, text=True, timeout=1800, cwd=work)
    if r.returncode != 0:
        raise RuntimeError(name + " failed:\n" + r.stdout[-2000:] + r.stderr[-4000:])


def run(art_root: str, seed: int, work: str) -> Dict[str, Any]:
    """Run layout_pass + plan_pass of the art-pass modules; returns dict(derive, plan, layout_log, buildings)."""
    if os.path.exists(work):
        shutil.rmtree(work)
    _prep(art_root, work)
    _spawn(work, "driver_r2.py", _DRIVER, str(seed))
    with open(os.path.join(work, "oracle_out.json")) as f:
        return json.load(f)


def run_kits(art_root: str, work: str, cases) -> list:
    """The art-pass `kit_face` / `roof_clutter` on `cases` (dicts, see `gen_r2_fixtures`); returns the recorded output per case."""
    _prep(art_root, work)
    with open(os.path.join(work, "kit_cases.json"), "w") as f:
        json.dump(cases, f)
    _spawn(work, "driver_kits.py", _KIT_DRIVER)
    with open(os.path.join(work, "kit_out.json")) as f:
        return json.load(f)


def run_signs(art_root: str, work: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """The art-pass sign textures of `plan` with their PIL draw calls recorded: `dict(specs, measure)`. `measure` rows are
    `[font, size, text, w, h]`: every glyph-box query the fit-to-sign search made."""
    _prep(art_root, work)
    with open(os.path.join(work, "sign_plan.json"), "w") as f:
        json.dump(plan, f)
    _spawn(work, "driver_signs.py", _SIGN_DRIVER, os.path.join(art_root, "assets", "fonts"))
    with open(os.path.join(work, "sign_out.json")) as f:
        return json.load(f)


def raw_inputs(art_root: str) -> Dict[str, Any]:
    """The pre-layout city (unified_v3.json buildings and hqs) and the scope network the passes read."""
    d = os.path.join(art_root, RMG, "storyboard", "scripts", "scratch", "layout")
    with open(os.path.join(d, "unified_v3.json")) as f:
        city = json.load(f)
    with open(os.path.join(d, "net_scope.json")) as f:
        net = json.load(f)
    return dict(city=city, net=net)


def art_commit(art_root: str) -> str:
    """The art-pass commit that last changed the street_r2 scripts, and the checkout's HEAD (for the fixture provenance line)."""
    path = os.path.join(RMG, "street_r2", "scripts")
    last = subprocess.run(["git", "-C", art_root, "log", "-1", "--format=%H", "--", path], capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "-C", art_root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return "%s (street_r2 scripts last changed; checkout HEAD %s)" % (last[:8], head[:8])
