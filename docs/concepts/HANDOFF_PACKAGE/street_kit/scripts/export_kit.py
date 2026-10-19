"""Street kit export: every street_r2 prop, built ONCE at its default size, to one glb per prop (+ roles.json).

Run (headless, one Blender job at a time; see D:/rc_scratch/GPU_LOCK):
  blender -b --factory-startup --python export_kit.py -- export [scratch_dir]   build + export glb + roles.json
  blender -b --factory-startup --python export_kit.py -- verify [scratch_dir]   re-import every glb, check, render tiles
  python contact_sheet.py [scratch_dir]                                         compose kit_contact_sheet.png (PIL)

HOW THE GEOMETRY IS REUSED (nothing is redrawn by hand)
  The plate scripts (docs/concepts/route_map_graph/street_r2/scripts/) build props inside r2_scene.py through module-level
  accumulators (CITY, CNEON, CWIN, CPANEL, CGLASS, SOLID, GLANE) and, for many props, inline inside big loops. This file
  recreates the same module environment and runs the SAME source:
    - target_corps.py lines 1..314 (Acc, beam, box, strip, rid, WIN_COLS, ...) is exec'd as r2_scene.py does.
    - r2_props.py (props.facade) is exec'd WHOLE, once per prop, with a one-prop PLAN. r2_kits.py is exec'd whole and
      kit_face() is called; r2_facade.py is imported as FC.
    - r2_scene.py functions (trim_face/_segs/band_zs, cyl36, flying_car, mixc) are exec'd by source line range.
    - code that is inline in a loop (lamp post, crowns, signs in r2_build.py; drain pipe, ledge, neon blade, water tank,
      antenna, holo billboard, roof rim, street car in r2_scene.py) is exec'd as a SOURCE SLICE (line range found by
      regex, so it follows edits to the plate scripts) with the loop variables set to default values.
  Minimal wrappers (the only things that are not the plate code):
    * fresh accumulators per prop, and a harvest step that turns each accumulator into a role-named material slot;
    * a "mid-range" stand-in RNG (MidRng) for slices/functions that draw sizes with r.uniform(a, b): it returns the
      midpoint, r.randint(a, b) returns a, r.random() returns 0.0, r.choice(s) returns s[0]. That is what "default size"
      means for random-sized props (the plate rules pick the size per instance);
    * balcony / setback ledge: kit_face() has no entry for them alone, so kit_face is run twice with the SAME seed
      (once without the feature, once with) and only the faces appended by the feature are kept (the feature code runs
      after the cell loop, so the diff is exactly its geometry);
    * roof_clutter(): one call per kit with MidRng, a kinds-collector that splits the output per kind;
    * _acc_obj/_quad_obj of r2_build.py are replaced by harvesting stand-ins (the signs slice calls them);
    * random.Random is swapped for MidRng only while the r2_build crowns slice runs.
  Not exported: the megastructure (globe/arch/holo hero, one-off, scale of the street, textured), room interiors / walls /
  section cut (scene-specific), facade kit CELLS (wall surfaces, they are rules not props), sign t1 LOD proxy (flat fill +
  rim, a LOD of the same sign), sky-lane boxes (loop disabled with range(0) in the plates).

CONVENTIONS OF THE EXPORT
  Blender is Z-up; glTF export_yup (default) maps Blender (x, y, z) -> glTF (x, z, -y). Wall props are built with the wall
  plane at Blender y = 0, the wall running along +X, the outward direction = Blender -Y = glTF +Z. So in the glb: +Y up,
  wall surface = the XY plane at z = 0, props stick out toward +Z.
  Units BU = metres. Vertex colour COLOR_0 = the authored plate colour, unmodified (display-referred sRGB values, as the
  toon shader showed them; set vertex_color_is_srgb in Godot). Materials are double sided (the plate rules do not wind all
  faces consistently). Emissive roles (*_emit) carry emissive colour = the authored colour, strength 1.0.
"""
import json
import math
import os
import random
import re
import sys
import textwrap
import zlib

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
KIT_DIR = os.path.normpath(os.path.join(HERE, ".."))
CONCEPTS = os.path.normpath(os.path.join(HERE, "..", "..", ".."))            # docs/concepts
SCR = os.path.join(CONCEPTS, "route_map_graph", "street_r2", "scripts")
M44 = os.path.join(CONCEPTS, "route_map_graph", "storyboard", "scripts", "m44")
_ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = _ARGV[0] if _ARGV else "export"
SCRATCH = _ARGV[1] if len(_ARGV) > 1 else "D:/rc_scratch/street_kit"
os.makedirs(SCRATCH, exist_ok=True)
sys.dont_write_bytecode = True

FILES = dict(props=os.path.join(SCR, "r2_props.py"), facade=os.path.join(SCR, "r2_facade.py"), kits=os.path.join(SCR, "r2_kits.py"),
             scene=os.path.join(SCR, "r2_scene.py"), build=os.path.join(SCR, "r2_build.py"), target=os.path.join(M44, "target_corps.py"))
REL = {k: os.path.relpath(v, CONCEPTS).replace("\\", "/") for k, v in FILES.items()}
_TXT = {}


def lines(key):
    if key not in _TXT:
        _TXT[key] = open(FILES[key], encoding="utf-8-sig").read().split("\n")
    return _TXT[key]


def find(key, regex, after=0):
    """1-based line number of the first line (> after) matching regex."""
    for i, ln in enumerate(lines(key), 1):
        if i > after and re.search(regex, ln):
            return i
    raise KeyError("%s: %s" % (key, regex))


G = globals()


def run_lines(key, a, b):
    """exec source lines a..b (1-based, inclusive) of a plate file in this module's globals; line numbers kept for tracebacks."""
    block = textwrap.dedent("\n".join(lines(key)[a - 1:b]))
    exec(compile("\n" * (a - 1) + block, FILES[key], "exec"), G)


def run_file(key):
    exec(compile("\n".join(lines(key)), FILES[key], "exec"), G)


# =========================================================================================== environment (as r2_scene.py)
class MidRng:
    """Default-size stand-in for random.Random: midpoint / first / lowest."""

    def uniform(self, a, b):
        return (a + b) / 2.0

    def randint(self, a, b):
        return a

    def randrange(self, *a):
        return a[0] if len(a) > 1 else 0

    def random(self):
        return 0.0

    def choice(self, seq):
        return seq[0]


def _boot():
    sv = sys.argv
    sys.argv = ["blender", "--", "meridian_boss", os.path.join(SCRATCH, "_tc")]
    try:
        run_lines("target", 1, 314)                         # r2_scene.py: exec("\n".join(_SRC[0:314]))
    finally:
        sys.argv = sv
    G["math"], G["random"] = math, random
    run_lines("scene", find("scene", r"^AMBER, CYAN"), find("scene", r"^LIME ="))
    run_lines("scene", find("scene", r"^SIGNC ="), find("scene", r"^SIGNC ="))
    run_lines("scene", find("scene", r"^def mixc"), find("scene", r"^def seg_d") - 1)
    run_lines("scene", find("scene", r"^def _segs"), find("scene", r"^ROOF_KINDS =") - 1)       # _segs, band_zs, trim_face
    run_lines("scene", find("scene", r"^def cyl36"), find("scene", r"^# r2: kit accumulators") - 1)
    run_lines("scene", find("scene", r"^def flying_car"), find("scene", r'^if os.environ.get\("CARS38"') - 1)
    sys.path.insert(0, SCR)
    import r2_facade as FC
    G["FC"] = FC
    run_file("kits")                                        # kit_face, roof_clutter
    G["ANTS"] = []
    G["LAMP_HEADS"] = []


# accumulator name -> default role of its material slot
ACC_ROLE = dict(CITY="conc", CPANEL="panel", CGLASS="glass", CNEON="neon_emit", CWIN="lit_emit", SOLID="panel", GLANE="neon_emit")
_ALL_ACC = []


def fresh():
    """New module-level accumulators, as r2_scene.py has them (the plate functions find them by global name)."""
    for a in _ALL_ACC:
        try:
            a.bm.free()
        except Exception:
            pass
    del _ALL_ACC[:]
    for n in ACC_ROLE:
        G[n] = Acc(n.lower())
        _ALL_ACC.append(G[n])


def acc_faces(acc, role, start=0):
    out = []
    bm = acc.bm
    bm.faces.ensure_lookup_table()
    for i in range(start, len(bm.faces)):
        f = bm.faces[i]
        c = f[acc.col]
        out.append(dict(role=role, pts=[tuple(v.co) for v in f.verts], col=(c[0], c[1], c[2]), uv=None))
    return out


def harvest(over=None, extra=None):
    """All module accumulators -> faces. over: acc name -> role override; extra: name -> (acc, role)."""
    over = over or {}
    out = []
    for n, r in ACC_ROLE.items():
        out += acc_faces(G[n], over.get(n, r))
    for n, (acc, r) in (extra or {}).items():
        out += acc_faces(acc, over.get(n, r))
    return out


# =========================================================================================== prop builders
def b_props(prop, over=None):
    """r2_props.py exec'd whole with a one-prop PLAN (u along +X, depth out of the wall toward Blender -Y)."""
    fresh()
    p = dict(prop, face=0.0, out=-1.0, axis=0, id=prop["kind"], key="kit", solid=prop["kind"] in ("ac", "pipe", "awning"))
    G["PLAN"] = {"axis": 0, "props": [p]}
    G["rid_"] = None
    run_file("props")
    return harvest(over)


def b_ac():
    return b_props(dict(kind="ac", u0=-0.4375, u1=0.4375, z0=0.0, z1=0.59, depth=0.465, col=[0.30, 0.30, 0.34], led=True, ledcol=[0.3, 0.85, 1.0]))


def b_pipe():
    return b_props(dict(kind="pipe", u0=-0.09, u1=0.09, z0=0.0, z1=6.0, depth=0.2, col=[0.21, 0.21, 0.25], elbow=True))


def b_awning():
    return b_props(dict(kind="awning", u0=-1.175, u1=1.175, z0=0.0, z1=0.35, depth=0.775, col=[0.6 * 0.8, 0.22 * 0.8 + 0.1, 0.3 * 0.8], trim=True,
                        trimcol=[1.0, 0.3, 0.65]), over=dict(CITY="awning_cloth"))


def b_sign_box_small():
    return b_props(dict(kind="small_sign", u0=-0.95, u1=0.95 - 0.0, z0=0.0, z1=0.55, depth=0.12, col=[1.0, 0.3, 0.65], blade=False, bars=0))


def b_sign_blade_small():
    return b_props(dict(kind="small_sign", u0=-0.175, u1=0.175, z0=0.0, z1=1.45, depth=0.37, col=[0.3, 0.85, 1.0], blade=True, bars=0))


def b_lit_window():
    return b_props(dict(kind="lit_room", u0=-0.725, u1=0.725, z0=0.0, z1=0.9, depth=0.05, col=[1.0, 0.7, 0.35], mull=True))


_BAYS = dict(bays=[1.0], phase=0, fm=[1.0, 1.0, 1.0], mods=[0, 0, 0], rigid_top=None, acc=[0.4, 0.8, 1.0], tone=[1.0, 1.0], relief=0.0,
             tones=[[1.0, 0.8, 0.5], [0.45, 0.9, 1.0]])
_KIT_ROLE = dict(conc="conc", glass="glass", panel="panel", win="lit_emit", neon="neon_emit")


def _kit_run(setback, balc):
    """kit_face on a 6 x 5.7 BU wall (3 floors of 1.9 BU), wall at y = 0, outward -Y; returns the accumulators."""
    accs = {k: Acc("k_" + k) for k in _KIT_ROLE}
    rh = dict(_BAYS, setback=setback, balc=balc)
    G["kit_face"]("panel_grille", (-3.0, 0.0), (3.0, 0.0), 0.0, 5.7, 0.0, -1.0, (0.40, 0.38, 0.46), random.Random(5), accs, module=0, rh=rh)
    return accs


def _kit_diff(setback, balc):
    base = _kit_run(None, [])
    n0 = {k: len(a.bm.faces) for k, a in base.items()}
    feat = _kit_run(setback, balc)
    out = []
    for k, a in feat.items():
        assert len(a.bm.faces) >= n0[k], "kit_face prefix changed"
        out += acc_faces(a, _KIT_ROLE[k], start=n0[k])
    return out


def b_balcony():
    """slab + rail + posts + lit door; width = mid of balcony_w (1.5..5.5), depth = mid of balcony_depth (0.45..0.7), on floor 1."""
    return _kit_diff(None, [dict(floor=1, c=0.5, w=3.5, depth=0.575, lit=True)])


def b_setback_ledge():
    """the slab + lit lip where a facade steps back (depth = mid of setback_depth 0.6..1.4); built on a 6 BU wide face."""
    return _kit_diff(dict(floor=1, d=1.0), [])


# ---- r2_build.py slices
def _plan(**kw):
    G["PLAN"] = dict({"seed": 1, "axis": 0, "line": -10.0, "props": [], "signs": [], "crowns": [], "lamps": []}, **kw)
    G["OC"] = {}


REG = []


def _acc_obj(acc, name):
    """stand-in for r2_build._acc_obj: harvest instead of creating an object."""
    roles = (("_t1", None), ("_t3n", "neon_emit"), ("_t3d", "bracket"), ("_frame", "frame"), ("r2_lamp_post", "pole"), ("r2_lamp_head", "lamp_emit"))
    for suf, role in roles:
        if name.endswith(suf):
            if role:
                REG.extend(acc_faces(acc, role))
            return None
    raise KeyError(name)


def _quad_obj(name, pts, uv=((0, 0), (1, 0), (1, 1), (0, 1))):
    """stand-in for r2_build._quad_obj: the blank sign board (UV 0..1 for the texture the build team applies)."""
    REG.append(dict(role="sign_board", pts=[tuple(p) for p in pts], col=(0.5, 0.5, 0.5), uv=[tuple(u) for u in uv]))
    return None


def b_sign(style, u0, u1, z0, z1, roof=False, legs=0.0, col=(1.0, 0.3, 0.65)):
    fresh()
    del REG[:]
    G["_acc_obj"], G["_quad_obj"] = _acc_obj, _quad_obj
    s = dict(id="kit", axis=0, d=-0.12, out=-1.0, u0=u0, u1=u1, z0=z0, z1=z1, col=list(col), tex={"style": style}, roof=roof, legs=legs, off=0.12,
             centre=[0, 0, 0])
    _plan(signs=[s])
    run_lines("build", find("build", r"^SIGN_OBJS = \[\]"), find("build", r'^print\("R2 signs"') - 1)
    return list(REG)


def b_sign_box():
    return b_sign("box", -1.5, 1.5, 0.0, 0.9)


def b_sign_blade():
    return b_sign("blade", -0.2, 0.2, 3.0, 5.0, col=(0.3, 0.85, 1.0))


def b_sign_wall():
    return b_sign("wall", -2.5, 2.5, 0.0, 3.0, col=(1.0, 0.62, 0.15))


def b_billboard_roof():
    return b_sign("wall", -3.0, 3.0, 1.0, 3.52, roof=True, legs=1.0, col=(0.75, 0.45, 1.0))


def b_lamp():
    fresh()
    del REG[:]
    G["_acc_obj"], G["_quad_obj"] = _acc_obj, _quad_obj
    _plan(lamps=[dict(pos=[0.0, 0.0, 0.0], side=1, col=[1.0, 0.72, 0.42])])      # line < y: the arm reaches toward Blender -Y (the road)
    G["OC"] = {}                                                                  # lamp_post_h default 4.6, lamp_arm 1.1 (r2_config streets.light)
    run_lines("build", find("build", r"^LP_S, LP_H = Acc"), find("build", r"^LAMP_OBJS =") - 1)
    return acc_faces(G["LP_S"], "pole") + acc_faces(G["LP_H"], "lamp_emit")


def b_crown(kind, q, h=6.0, floors=3):
    fresh()
    _plan(crowns=[dict(key="kit", kind=kind, side=1, top=0.0, q=q, col=[1.0, 0.3, 0.65], floors=floors, h=h)])
    sv = random.Random
    random.Random = lambda *a, **k: MidRng()                 # the crowns slice draws rc = random.Random(seed): default sizes
    try:
        run_lines("build", find("build", r"^CROWN_N = Acc"), find("build", r'^print\("R2 crowns"') - 1)
    finally:
        random.Random = sv
    return harvest(extra=dict(CROWN_N=(G["CROWN_N"], "neon_emit")))


_SQ_C = [[-4, -4], [4, -4], [4, 4], [-4, 4]]
_SQ_E = [[-4, 0], [4, 0], [4, 8], [-4, 8]]


def b_crown_sign_frame():
    return b_crown("sign_frame", _SQ_E)


def b_crown_spire():
    return b_crown("spire", _SQ_C)


def b_crown_roof_box():
    return b_crown("roof_box", _SQ_C)


def b_crown_setback():
    return b_crown("setback", _SQ_C)


# ---- r2_kits.roof_clutter, split per kind
class _Kinds(set):
    def __init__(self):
        super().__init__()
        self.marks = {n: 0 for n in ACC_ROLE}
        self.groups = {}

    def add(self, name):
        g = self.groups.setdefault(name, [])
        for n, r in ACC_ROLE.items():
            g += acc_faces(G[n], r, start=self.marks[n])
            self.marks[n] = len(G[n].bm.faces)
        super().add(name)


def b_roof(kind):
    fresh()
    top = [(-4.0, -4.0), (4.0, -4.0), (4.0, 4.0), (-4.0, 4.0)]
    for kit in ("glass_curtain", "panel_grille", "lit_atrium"):
        fresh()
        kinds = _Kinds()
        G["roof_clutter"](kit, top, 0.0, MidRng(), G["SOLID"], G["CNEON"], kinds)
        if kind in kinds.groups:
            return kinds.groups[kind]
    raise KeyError(kind)


# ---- r2_scene.py slices
_TR = dict(col=(1.0, 0.55, 0.1), col2=(0.16, 0.8, 1.0), band_every=1, corner=False, gap_p=0.0, roof=True)


def b_trim_band():
    fresh()
    G["trim_face"]((0.0, 0.0), (1.9, 0.0), 0.0, 3.0, 0.0, -1.0, dict(_TR), G["CNEON"])      # exactly one band at z = 1.85, one 1.9 BU segment
    return harvest()


def b_trim_corner():
    fresh()
    G["trim_face"]((0.0, 0.0), (1.9, 0.0), 0.0, 6.0, 0.0, -1.0, dict(_TR, band_every=99, corner=True), G["CNEON"])
    return [f for f in harvest() if sum(p[0] for p in f["pts"]) / len(f["pts"]) < 0.95]      # keep the corner strip at u = 0 only


def _slice_run(a_re, b_re=None, nlines=None, after=0, **ns):
    fresh()
    G.update(ns)
    a = find("scene", a_re, after)
    b = find("scene", b_re, a - 1) if b_re else a + nlines - 1
    run_lines("scene", a, b)


def b_roof_rim():
    anchor = find("scene", r'TRIMS\[uid\]\["roof"\]:')
    fresh()
    G.update(n=4, top=[(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)], zt=0.0, uid="u", TRIMS={"u": {"col": [1.0, 0.55, 0.1], "roof": True}})
    run_lines("scene", anchor + 1, anchor + 3)
    return harvest()


def b_ledge():
    _slice_run(r"zl = z0 \+ 3\.0 \* k", nlines=2, a=(-1.5, 0.0), c=(1.5, 0.0), z0=0.0, k=0, nx=0.0, ny=-1.0, col=(0.42, 0.40, 0.52))
    return harvest()


def b_drain_pipe():
    _slice_run(r"t0 = r\.uniform\(0\.3, L - 0\.3\)", nlines=3, r=MidRng(), L=2.0, a=(-1.0, 0.0), ux=1.0, uy=0.0, nx=0.0, ny=-1.0, z0=0.0, h=6.0)
    return harvest()


def b_neon_blade():
    _slice_run(r"sc = r\.choice\(SIGNC\)", r"^\s*beam\(\(bx, by, zb\)", r=MidRng(), L=4.0, h=8.0, a=(-2.0, 0.0), ux=1.0, uy=0.0, nx=0.0, ny=-1.0)
    return harvest()


def b_water_tank():
    _slice_run(r"tx, ty = r\.uniform", r'ROOF_KINDS\[uid\]\.add\("tank"\)', r=MidRng(), x0=-4.0, x1=4.0, y0=-4.0, y1=4.0, zt=0.0, uid="u", ROOF_KINDS={"u": set()})
    return harvest()


def b_antenna_band():
    _slice_run(r"ax, ay = \(x0 \+ x1\) / 2, \(y0 \+ y1\) / 2", r"ANTS\.append\(\(ax, ay, zt \+ hh \+ 0\.25\)\)", r=MidRng(), x0=-4.0, x1=4.0, y0=-4.0,
               y1=4.0, zt=0.0)
    return harvest()


def b_holo_billboard():
    _slice_run(r"hc = r\.choice\(\[\(1\.0, 0\.3, 0\.7\)", r"tuple\(v \* 0\.75 for v in hc\), \(0, 0, 0\)\)", r=MidRng(), x0=-4.0, x1=4.0, y0=-4.0, y1=4.0, zt=0.0)
    return harvest()


def b_ground_car():
    fresh()
    G.update(x=0.0, y=0.0, fw=(0.0, -1.0), nx=1.0, ny=0.0, cc=(0.5, 0.2, 0.2))              # heading Blender -Y = glTF +Z
    run_lines("scene", find("scene", r"^\s*hl, hw = 0\.85, 0\.42"), find("scene", r"^\s*strip\(GLANE, \(x - fw\[0\] \* hl"))
    return harvest()


def b_hover_car():
    fresh()
    G["flying_car"](dict(x=0.0, y=0.0, z=0.0, dx=0.0, dy=-1.0, col=(0.3, 0.85, 1.0)), 1.0)
    return harvest()


def cls_car(role, col):
    c = tuple(round(v, 2) for v in col)
    if role == "panel":
        return "glass" if c in ((0.08, 0.1, 0.16), (0.1, 0.12, 0.2)) else "car_body"
    if role == "neon_emit":
        if c[0] > 0.9 and c[1] > 0.9 and c[2] > 0.8:
            return "headlight_emit"
        if c[0] > 0.9 and c[1] < 0.2:
            return "taillight_emit"
    return role


# =========================================================================================== catalogue
def S(key, regex, what, after=0):
    return dict(file=REL[key], line=find(key, regex, after), what=what)


def catalogue():
    F = "props"
    return [
        dict(id="ac_unit", role="ac", mount="wall", build=b_ac, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the unit's underside (u centre, wall plane, bottom); depth sticks out +Z",
             src=[S(F, r'_k == "ac"', "r2_props.py ac branch (exec'd whole)"), S("facade", r'if k == "ac":', "size ranges w .7-1.05, h .5-.68, depth .38-.55 (midpoints used)")]),
        dict(id="pipe_run", role="pipe", mount="wall", build=b_pipe, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the pipe foot; runs up +Y; default 6 BU (range 3-9) with an elbow to +X at the top",
             src=[S(F, r'_k == "pipe"', "r2_props.py pipe branch"), S("facade", r'elif k == "pipe":', "length range 3-9")]),
        dict(id="awning", role="awning", mount="wall", build=b_awning, attach=("c", "0", "max"),
             rule="origin = centre of the wall hinge line (top edge on the wall); slopes out and down 0.35 over a 0.775 depth",
             src=[S(F, r'_k == "awning"', "r2_props.py awning branch (CITY face -> awning_cloth, trim tube -> neon_emit)"), S("facade", r'elif k == "awning":', "w 1.3-3.4, depth .6-.95")]),
        dict(id="sign_box_small", role="sign_small", mount="wall", build=b_sign_box_small, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the board bottom; lit face blank (bars=0)",
             src=[S(F, r'_k == "small_sign"', "r2_props.py small_sign (box), bars=0"), S("facade", r'elif k == "small_sign":', "w .55-1.35 (h .42-.75 w)")]),
        dict(id="blade_sign_small", role="blade_sign", mount="wall", build=b_sign_blade_small, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the blade bottom; blade projects 0.37 from the wall, blank lit face",
             src=[S(F, r'_k == "small_sign"', "r2_props.py small_sign, blade=True, bars=0"), S("facade", r"blade = r\.random\(\) < 0\.3", "blade w .28-.42, h 1.0-1.9")]),
        dict(id="lit_window", role="lit_room", mount="wall", build=b_lit_window, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the window bottom; lit quad 0.04 off the wall + mullion cross",
             src=[S(F, r'_k == "lit_room"', "r2_props.py lit_room branch"), S("facade", r'elif k == "lit_room":', "w .9-2.0")]),
        dict(id="balcony", role="balcony", mount="wall", build=b_balcony, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the slab underside; rail 0.85 above the slab, posts at both ends, lit door behind (on the wall)",
             src=[S("kits", r"# balconies: slab, rail", "r2_kits.kit_face balcony block (kit_face run twice, diff kept)"), S("facade", r"balc\.append", "w 1.5-5.5, depth .45-.7")]),
        dict(id="setback_ledge", role="trim", mount="wall", build=b_setback_ledge, attach=("c", "0", "0"),
             rule="origin = wall-contact line at the floor height where the facade steps back; slab 1.0 deep INTO the wall (-Z) and a lit lip",
             src=[S("kits", r"# setback ledge", "r2_kits.kit_face setback ledge"), S("facade", r"setback = dict", "d 0.6-1.4")]),
        dict(id="sign_box_hero", role="sign_box", mount="wall", build=b_sign_box, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the board bottom; board is a UV 0..1 quad 0.12 off the wall (apply the sign texture), dark frame, bracket tubes to the wall, lamp heads over the top, lit rim",
             src=[S("build", r"^SIGN_OBJS = \[\]", "r2_build signs block, style=box (t2 board+frame, t3 detail; t1 LOD proxy skipped)")]),
        dict(id="sign_blade_hero", role="blade_sign", mount="wall", build=b_sign_blade, attach=("c", "0", "min"),
             rule="origin = wall at the foot of the cable (z = 0 of the building); blade board 0.4 x 2.0 at z 3..5, UV 0..1, brackets and the cable down to z=0",
             src=[S("build", r"^SIGN_OBJS = \[\]", "r2_build signs block, style=blade"), S("build", r's\["tex"\]\["style"\] == "blade"', "blade cable")]),
        dict(id="sign_wall_hero", role="sign_wall", mount="wall", build=b_sign_wall, attach=("c", "0", "min"),
             rule="origin = wall-contact centre of the board bottom; hero poster board 5 x 3, UV 0..1",
             src=[S("build", r"^SIGN_OBJS = \[\]", "r2_build signs block, style=wall")]),
        dict(id="billboard_board_roof", role="billboard_board", mount="roof", build=b_billboard_roof, attach=("c", "0", "min"),
             rule="origin = street-edge centre of the roof at the foot of the legs; board 6 x 2.52 on two legs of 1.0 BU, UV 0..1",
             src=[S("build", r's\.get\("roof"\):', "r2_build signs block, roof=True legs"), S("build", r"^SIGN_OBJS = \[\]", "signs block")]),
        dict(id="lamp_post", role="lamp", mount="ground", build=b_lamp, attach=("0", "0", "0"),
             rule="origin = foot of the pole on the kerb; pole 4.6 BU, arm 1.1 BU toward the road (glTF +Z), lamp head quad under the arm",
             src=[S("build", r"^LP_S, LP_H = Acc", "r2_build kerb lamp posts (streets.light)")]),
        dict(id="crown_billboard_frame", role="billboard_frame", mount="roof", build=b_crown_sign_frame, attach=("0", "0", "0"),
             rule="origin = street-edge centre of the roof surface (roof is 8 x 8 behind it); two legs + lit rim, the board is a separate sign (billboard_board_roof)",
             src=[S("build", r'elif k == "sign_frame":', "r2_build crowns, sign_frame")]),
        dict(id="crown_spire", role="crown", mount="roof", build=b_crown_spire, attach=("0", "0", "0"),
             rule="origin = roof surface centre; spire 6 BU + 35 % extension, two lit rings, red light on top",
             src=[S("build", r'elif k == "spire":', "r2_build crowns, spire")]),
        dict(id="crown_roof_box", role="crown", mount="roof", build=b_crown_roof_box, attach=("0", "0", "0"),
             rule="origin = roof surface centre (8 x 8 roof); machine box with lit rim and window, water tank on four legs",
             src=[S("build", r'elif k == "roof_box":', "r2_build crowns, roof_box")]),
        dict(id="crown_setback", role="crown", mount="roof", build=b_crown_setback, attach=("0", "0", "0"),
             rule="origin = roof surface centre of an 8 x 8 roof; 3 setback floors, lit rims, lit band windows (building massing, scales with the footprint)",
             src=[S("build", r'if k == "setback":', "r2_build crowns, setback")]),
        dict(id="roof_vent_stack", role="roof_clutter", mount="roof", build=lambda: b_roof("vent_stack"), attach=("c", "c", "min"),
             rule="origin = base centre; 8-sided cylinder, mid size (h 1.7, r 0.35)",
             src=[S("kits", r"# vent stacks", "r2_kits.roof_clutter vent_stack")]),
        dict(id="roof_ac", role="ac", mount="roof", build=lambda: b_roof("ac"), attach=("c", "c", "min"),
             rule="origin = base centre of the 0.9 x 0.7 x 0.55 rooftop AC box",
             src=[S("kits", r"# AC units", "r2_kits.roof_clutter ac"), S("scene", r"box\(vx, vy, zt, vx \+ 0\.9", "same box in city_building")]),
        dict(id="roof_dish", role="roof_clutter", mount="roof", build=lambda: b_roof("dish"), attach=("c", "c", "min"),
             rule="origin = base centre of the stub; dish radius 0.8 on a 1.0 stub",
             src=[S("kits", r"# dish on a stub", "r2_kits.roof_clutter dish")]),
        dict(id="roof_antenna", role="roof_clutter", mount="roof", build=lambda: b_roof("antenna"), attach=("c", "c", "min"),
             rule="origin = base centre; mast 4.0 BU with a red aircraft-light quad (CNEON)",
             src=[S("kits", r"# antenna with a red light", "r2_kits.roof_clutter antenna")]),
        dict(id="trim_floor_band", role="trim", mount="wall", build=b_trim_band, attach=("c", "0", "c"),
             rule="origin = centre of one 1.9 BU lit band segment, 0.1 off the wall; tile along the wall; width 0.08-0.17 per segment in the plates (seeded by position), this sample = what trim_face drew",
             src=[S("scene", r"^def trim_face", "r2_scene.trim_face (bands)"), S("scene", r"^def _segs", "segment step 1.9")]),
        dict(id="trim_corner_strip", role="trim", mount="wall", build=b_trim_corner, attach=("c", "0", "min"),
             rule="origin = foot of the lit corner strip (starts 2.0 above the building z0), 0.13 wide, 1.9 BU segments",
             src=[S("scene", r"if tr\[\"corner\"\] and zr is None:", "r2_scene.trim_face corner strips")]),
        dict(id="trim_roof_rim", role="trim", mount="roof", build=b_roof_rim, attach=("0", "0", "0"),
             rule="origin = roof surface centre of a 4 x 4 sample loop; 0.2 square tube 0.1 above the roof, one beam per edge (stretch to the footprint)",
             src=[S("scene", r'TRIMS\[uid\]\["roof"\]:', "r2_scene city_building roof rim (slice)")]),
        dict(id="trim_ledge", role="trim", mount="wall", build=b_ledge, attach=("c", "0", "c"),
             rule="origin = centre of a 3 BU ledge beam, 0.12 off the wall, 0.16 square",
             src=[S("scene", r"zl = z0 \+ 3\.0 \* k", "r2_scene city_building ledges (slice)")]),
        dict(id="drain_pipe", role="pipe", mount="wall", build=b_drain_pipe, attach=("c", "0", "min"),
             rule="origin = wall-contact point of the foot of the 6 BU drain pipe (0.14 square, 0.12 off the wall)",
             src=[S("scene", r"# a drain pipe down the facade", "r2_scene city_building drain pipe (slice)")]),
        dict(id="neon_blade_tube", role="blade_sign", mount="wall", build=b_neon_blade, attach=("c", "0", "min"),
             rule="origin = wall point under the 2.4 BU vertical neon tube (0.36 wide, 0.5 off the wall)",
             src=[S("scene", r"# a blade sign \(vertical neon\)", "r2_scene city_building neon blade (slice)")]),
        dict(id="roof_water_tank", role="roof_clutter", mount="roof", build=b_water_tank, attach=("c", "c", "min"),
             rule="origin = centre of the tank footprint on the roof; four legs 0.9, cylinder r 0.8 up to 2.1",
             src=[S("scene", r"# water tank on legs|water tank on legs", "r2_scene city_building tank (slice)")]),
        dict(id="antenna_band", role="roof_clutter", mount="roof", build=b_antenna_band, attach=("c", "c", "min"),
             rule="origin = base centre; mast 5 BU, 0.18 wide, red light quad (concrete_band variant of roof_antenna)",
             src=[S("scene", r"antenna with a red aircraft light", "r2_scene city_building antenna (slice)")]),
        dict(id="holo_billboard_panel", role="billboard_frame", mount="roof", build=b_holo_billboard, attach=("c", "c", "min"),
             rule="origin = roof surface at the post foot; 1.0 post then a lit panel 5.75 x 3.45 (faces Blender -X,-Y in the plates: yaw it to the street)",
             src=[S("scene", r"# holo billboard", "r2_scene city_building holo billboard (slice)")]),
        dict(id="hover_car", role="hover_car", mount="free", build=b_hover_car, attach=("c", "c", "0"), classify=cls_car,
             rule="origin = centre of the hull underside (under-glow plate is 0.12 below); nose toward glTF +Z; 3.4 long, 1.5 wide",
             src=[S("scene", r"^def flying_car", "r2_scene.flying_car(c, s=1.0)")]),
        dict(id="ground_car", role="ground_car", mount="ground", build=b_ground_car, attach=("c", "c", "0"), classify=cls_car,
             rule="origin = centre of the car footprint at street level; nose toward glTF +Z; 1.7 long, 0.84 wide, 0.45 high + light bars",
             src=[S("scene", r"hl, hw = 0\.85, 0\.42", "r2_scene street traffic (slice)")]),
    ]


# =========================================================================================== mesh + materials
def emissive(role):
    return role.endswith("_emit")


def _mat(name, role, emit_rgb):
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    vc = nt.nodes.new("ShaderNodeVertexColor")
    vc.layer_name = "Col"
    nt.links.new(vc.outputs["Color"], pb.inputs["Base Color"])
    pb.inputs["Metallic"].default_value = 0.0
    pb.inputs["Roughness"].default_value = 0.12 if role in ("glass",) else 0.8
    if emit_rgb is not None:
        pb.inputs["Emission Color"].default_value = tuple(emit_rgb) + (1.0,)
        pb.inputs["Emission Strength"].default_value = 1.0
    m.use_backface_culling = False
    return m


def finalize(spec, faces):
    """faces -> one mesh object with role-named material slots, origin at the attach point."""
    pid = spec["id"]
    cls = spec.get("classify")
    for f in faces:
        if cls:
            f["role"] = cls(f["role"], f["col"])
    allp = [p for f in faces for p in f["pts"]]
    mn = [min(p[i] for p in allp) for i in range(3)]
    mx = [max(p[i] for p in allp) for i in range(3)]
    t = []
    for i, mode in enumerate(spec["attach"]):
        t.append(dict(c=-(mn[i] + mx[i]) / 2, min=-mn[i], max=-mx[i])["c" if mode == "c" else mode] if mode != "0" else 0.0)
    # slots
    ckey = lambda c: tuple(round(v, 2) for v in c)                                  # noqa: E731
    ncol = {}
    for f in faces:
        if emissive(f["role"]):
            ncol.setdefault(f["role"], set()).add(ckey(f["col"]))
    slots, index = [], {}
    sums = {}
    for f in faces:
        r = f["role"]
        key = (r, ckey(f["col"])) if (emissive(r) and len(ncol[r]) <= 3) else (r, None)
        if key not in index:
            index[key] = len(slots)
            nm = r if not any(s["role"] == r for s in slots) else "%s_%d" % (r, sum(1 for s in slots if s["role"] == r) + 1)
            slots.append(dict(name=nm, role=r, emissive=emissive(r), key=key, tris=0))
        f["slot"] = index[key]
        sums.setdefault(index[key], []).append(f["col"])
    for i, s in enumerate(slots):
        if s["emissive"]:
            cs = sums[i]
            s["emit_rgb"] = [round(sum(c[k] for c in cs) / len(cs), 3) for k in range(3)] if s["key"][1] is None else list(s["key"][1])
        else:
            s["emit_rgb"] = None
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if any(f["uv"] for f in faces) else None
    cols = []
    for f in faces:
        vs = [bm.verts.new((p[0] + t[0], p[1] + t[1], p[2] + t[2])) for p in f["pts"]]
        bf = bm.faces.new(vs)
        bf.material_index = f["slot"]
        bf.smooth = False
        if uvl and f["uv"]:
            for lp, uv in zip(bf.loops, f["uv"]):
                lp[uvl].uv = uv
        cols.append(f["col"])
    me = bpy.data.meshes.new(pid)
    bm.to_mesh(me)
    bm.free()
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    flat = []
    for poly, c in zip(me.polygons, cols):
        flat += [c[0], c[1], c[2], 1.0] * poly.loop_total
    ca.data.foreach_set("color", flat)
    me.color_attributes.active_color = ca
    for s in slots:
        me.materials.append(_mat(s["name"], s["role"], s["emit_rgb"]))
    me.calc_loop_triangles()
    for tri in me.loop_triangles:
        slots[me.polygons[tri.polygon_index].material_index]["tris"] += 1
    ob = bpy.data.objects.new(pid, me)
    bpy.context.scene.collection.objects.link(ob)
    vv = [v.co for v in me.vertices]
    bmn = [min(v[i] for v in vv) for i in range(3)]
    bmx = [max(v[i] for v in vv) for i in range(3)]
    return ob, slots, len(me.loop_triangles), bmn, bmx


def to_gltf_axes(v):
    return [round(v[0], 4), round(v[2], 4), round(-v[1], 4)]


def do_export():
    _boot()
    out = []
    for spec in catalogue():
        rng.seed(zlib.crc32(spec["id"].encode()))
        faces = spec["build"]()
        if spec["id"] == "trim_corner_strip":
            pass
        assert faces, spec["id"] + ": no faces"
        ob, slots, tris, bmn, bmx = finalize(spec, faces)
        path = os.path.join(KIT_DIR, spec["id"] + ".glb")
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True)
        gmn, gmx = to_gltf_axes(bmn), to_gltf_axes(bmx)
        lo = [min(gmn[i], gmx[i]) for i in range(3)]
        hi = [max(gmn[i], gmx[i]) for i in range(3)]
        out.append(dict(id=spec["id"], file=spec["id"] + ".glb", role=spec["role"], mount=spec["mount"],
                        source=spec["src"], attach=spec["rule"],
                        bbox_size_m=[round(hi[i] - lo[i], 4) for i in range(3)], bbox_min_m=lo, bbox_max_m=hi, tri_count=tris,
                        materials=[dict(slot=s["name"], role=s["role"], emissive=s["emissive"], emit_rgb=s["emit_rgb"], tris=s["tris"]) for s in slots]))
        bpy.data.objects.remove(ob)
        print("EXPORTED %-22s tris %5d size %s slots %s" % (spec["id"], tris, out[-1]["bbox_size_m"], [s["name"] for s in slots]), flush=True)
    doc = dict(
        about="REBEL_CELL street kit: every street_r2 prop at default size, one glb each. Built by scripts/export_kit.py from the plate scripts.",
        conventions=dict(
            units="1 BU = 1 metre", up="+Y (glTF)", wall="wall props: the wall surface is the XY plane at z = 0, the wall runs along +X, the prop sticks out toward +Z; "
            "recess geometry (balcony door, setback slab) goes to -Z", ground="ground/roof props stand on y = 0",
            vertex_colour="COLOR_0 = authored plate colour per face, unmodified (display-referred sRGB values, as the toon shader showed them); "
            "set vertex_color_is_srgb in Godot", material_roles="slot names are roles; emissive roles end in _emit and carry emissive colour = authored colour, strength 1.0; "
            "an emissive role with several colours gets role_2, role_3 slots",
            sizes="random-sized props use the midpoint of the plate rule's range; ranges are quoted in the source notes",
            double_sided="all materials are double sided (the plate rules do not wind every face consistently)"),
        props=out)
    json.dump(doc, open(os.path.join(KIT_DIR, "roles.json"), "w"), indent=1)
    print("DONE export", len(out), flush=True)


# =========================================================================================== verify + tiles
def do_verify():
    from mathutils import Vector
    doc = json.load(open(os.path.join(KIT_DIR, "roles.json")))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    try:
        sc.eevee.taa_render_samples = 16
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 480, 320
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bgn = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bgn.inputs["Color"].default_value = (0.045, 0.05, 0.07, 1)
    bgn.inputs["Strength"].default_value = 1.0
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 2.5
    sun.rotation_euler = (math.radians(55), math.radians(15), math.radians(35))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    sc.collection.objects.link(cam)
    sc.camera = cam
    report, bad = [], 0
    for p in doc["props"]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(KIT_DIR, p["file"]))
        meshes = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
        tris, vv, mats, hascol = 0, [], [], True
        for o in meshes:
            me = o.data
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
            vv += [o.matrix_world @ v.co for v in me.vertices]
            mats += [m.name for m in me.materials if m]
            hascol = hascol and len(me.color_attributes) > 0
        mn = [min(v[i] for v in vv) for i in range(3)]
        mx = [max(v[i] for v in vv) for i in range(3)]
        size = [round(mx[0] - mn[0], 4), round(mx[2] - mn[2], 4), round(mx[1] - mn[1], 4)]      # back to glTF axes (x, up, depth)
        exp = p["bbox_size_m"]
        ok = tris == p["tri_count"] and all(abs(size[i] - exp[i]) < 2e-3 for i in range(3)) and hascol
        okm = sorted(m.split(".")[0] if re.search(r"\.\d{3}$", m) else m for m in mats) == sorted(s["slot"] for s in p["materials"])
        bad += (0 if (ok and okm) else 1)
        report.append(dict(id=p["id"], ok=bool(ok and okm), tris=tris, tris_expected=p["tri_count"], size=size, size_expected=exp, vertex_colour=hascol,
                           materials=mats, file_bytes=os.path.getsize(os.path.join(KIT_DIR, p["file"]))))
        # tile
        mn_v, mx_v = Vector(mn), Vector(mx)
        ctr = (mn_v + mx_v) / 2
        wall = p["mount"] == "wall"
        helper = None
        if p["mount"] in ("wall", "roof", "ground"):
            me2 = bpy.data.meshes.new("bg")
            s_ = 40.0
            if wall:
                vs = [(ctr.x - s_, 0.004, ctr.z - s_), (ctr.x + s_, 0.004, ctr.z - s_), (ctr.x + s_, 0.004, ctr.z + s_), (ctr.x - s_, 0.004, ctr.z + s_)]
            else:
                vs = [(ctr.x - s_, ctr.y - s_, -0.004), (ctr.x + s_, ctr.y - s_, -0.004), (ctr.x + s_, ctr.y + s_, -0.004), (ctr.x - s_, ctr.y + s_, -0.004)]
            me2.from_pydata(vs, [], [(0, 1, 2, 3)])
            helper = bpy.data.objects.new("bg", me2)
            gm = bpy.data.materials.new("bgm")
            gm.use_nodes = True
            nb = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            nb.inputs["Base Color"].default_value = (0.16, 0.16, 0.2, 1)
            nb.inputs["Roughness"].default_value = 0.9
            me2.materials.append(gm)
            sc.collection.objects.link(helper)
        d = Vector((0.55, -1.0, 0.45)).normalized()
        rot = d.to_track_quat("Z", "Y")                                  # camera looks along -Z toward the centre
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        inv = cam.rotation_euler.to_matrix().inverted()
        corners = [inv @ (Vector((x, y, z)) - ctr) for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])]
        ex = max(c.x for c in corners) - min(c.x for c in corners)
        ey = max(c.y for c in corners) - min(c.y for c in corners)
        cam.data.ortho_scale = max(ex, ey * 1.5, 0.3) * 1.2
        cam.location = ctr + d * 60.0
        cam.data.clip_end = 200.0
        sc.render.filepath = os.path.join(SCRATCH, "tile_%s.png" % p["id"])
        bpy.ops.render.render(write_still=True)
        keep = {"sun", "cam"}
        for nm in [o.name for o in bpy.data.objects if o.name not in keep and o not in before]:
            if nm in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[nm])
        for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
            for it in list(coll):
                if it.users == 0:
                    coll.remove(it)
        print("VERIFY %-22s %s tris %d/%d size %s vcol %s" % (p["id"], "OK " if (ok and okm) else "BAD", tris, p["tri_count"], size, hascol), flush=True)
    json.dump(report, open(os.path.join(SCRATCH, "verify.json"), "w"), indent=1)
    print("DONE verify bad=%d of %d" % (bad, len(report)), flush=True)


if MODE == "export":
    do_export()
elif MODE == "verify":
    do_verify()
