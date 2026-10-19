"""Landmark .glb export (queue item 4): one glTF 2.0 binary per corp from its standalone <corp>_landmark.py module.

    python export_landmarks.py [corp ...]        (default: halcyon solace orbital rebel_cell meridian tethys)

Pure python (no Blender): the modules are run with the recording ctx of route_map_graph/lm_common.py (the city_build
primitives ported 1:1, verified against the city's own dumps), at the HQ lot CENTRE (0, 0), camdir (0, -1) (the A2 hero
camera looks north from the south). Aurelian is not exported here (its redesign is a separate task).

Format (PIPELINE_SPEC 11.5): glTF 2.0 binary, Z-up -> Y-up by the exporter ((x, y, z) -> (x, z, -y)), BU units, per-vertex:
    POSITION, NORMAL (flat), TEXCOORD_0 (the city facade uv),
    COLOR_0   the face colour clamped 0..1 (linear; what a stock viewer shows),
    _col      the face colour as authored (VEC3, unclamped: emitters carry strength > 1)  <- the "col" attribute
    _bid      the building id as an integer index into the node's extras.building_ids (["hq:<corp>"]); one landmark = one id
    _wbid     the city shader's per-face 0..1 window-hash value ("bid" in city_build.Acc)
    _wc, _wl, _wm   window colour / lit share / mode (0 grid, 1 ribbon, 2 porthole, 3 none, 4 arch) of the facade shader
glTF requires application attributes to start with an underscore, hence "_col" / "_bid". One mesh, one primitive per city
accumulator: surf + smooth (opaque), neon (KHR_materials_unlit emitters), glass (blend), sign (Rebel Cell blade quad).
Node extras: corp, building_ids, entry / entry_nrm (HQ-lot-centre frame, Z-up, as ENTRIES.json) and entry_gltf (Y-up).
"""
import importlib.util
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RMG = os.path.normpath(os.path.join(HERE, "..", "route_map_graph"))
CAC = os.path.normpath(os.path.join(HERE, "..", "city_all_corps", "scripts"))
sys.dont_write_bytecode = True
sys.path.insert(0, RMG)
sys.path.insert(0, CAC)
import lm_common as LC  # noqa: E402
import city_preset as CP  # noqa: E402

MODULES = {
    "halcyon": "hq_halcyon/scripts/halcyon_landmark.py",
    "solace": "hq_solace/scripts/solace_landmark.py",
    "orbital": "hq_orbital/scripts/orbital_landmark.py",
    "rebel_cell": "hq_rebel_cell/scripts/rebel_cell_landmark.py",
    "meridian": "hq_meridian_v3/scripts/meridian_landmark.py",
    "tethys": "hq_tethys/scripts/tethys_landmark.py",
}
CAMDIR = (0.0, -1.0)


def load(corp):
    path = os.path.join(RMG, MODULES[corp])
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("lm_" + corp, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(corp):
    """-> (accs {name: Recorder}, ret dict, ENTRY, spots)."""
    mod = load(corp)
    accs = dict(SURF=LC.Recorder("surf"), SMOOTH=LC.Recorder("smooth", True), NEON=LC.Recorder("neon"),
                GLASS=LC.Recorder("glass", True), STREAK=LC.Recorder("streak"))
    ctx = LC.make_ctx(corp, (0.0, 0.0), CP.DISTRICTS[corp], accs, CAMDIR, cp=CP, footprint=CP.LANDMARK_FP.get(corp))
    if corp == "tethys":
        ns = dict(SURF=ctx.SURF, SMOOTH=ctx.SMOOTH, NEON=ctx.NEON, GLASS=ctx.GLASS, box=LC.box, bar=LC.bar, cyl=LC.cyl,
                  dome=LC.dome, ring_line=LC.ring_line, annulus=LC.annulus, sc=LC.sc, spot_at=ctx.spot_at,
                  ZW=CP.WATER["z"], W=lambda p: p, O={"hq": {"tethys": (0.0, 0.0)}}, KH=CP.KH, STATION={})
        info = mod.build_ns(ns, centre=(0.0, 0.0))        # the station, pods, piers and the trench; wildlife is movers
        ret = dict(label=info["label"], crown=info["crown"], hue=info["hue"])
    else:
        ret = mod.build(ctx)
    signs = ctx.station.get("signs", [])
    return accs, ret, mod.ENTRY, signs


def _newell(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    L = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / L, ny / L, nz / L) if L > 1e-12 else (0.0, 0.0, 1.0)


def yup(p):
    return (p[0], p[2], -p[1])


def prim_data(rec, building_index=0):
    """Triangulate (fan) one Recorder -> attribute arrays (Y-up)."""
    P, N, UV, C, COL, BID, WB, WC, WL, WM = [], [], [], [], [], [], [], [], [], []
    for fi, f in enumerate(rec.F):
        pts = [rec.V[i] for i in f]
        if len(pts) < 3:
            continue
        n = _newell(pts)
        col, wc = rec.col[fi], rec.wc[fi]
        for k in range(1, len(pts) - 1):
            for vi in (0, k, k + 1):
                P.append(yup(pts[vi]))
                N.append(yup(n))
                UV.append(tuple(rec.UV[f[vi]]))
                C.append((min(1.0, max(0.0, col[0])), min(1.0, max(0.0, col[1])), min(1.0, max(0.0, col[2])), 1.0))
                COL.append(tuple(col[:3]))
                BID.append(float(building_index))
                WB.append(float(rec.bid[fi]))
                WC.append(tuple(wc[:3]))
                WL.append(float(rec.wl[fi]))
                WM.append(float(rec.wm[fi]))
    return dict(POSITION=P, NORMAL=N, TEXCOORD_0=UV, COLOR_0=C, _col=COL, _bid=BID, _wbid=WB, _wc=WC, _wl=WL, _wm=WM)


def sign_rec(signs):
    r = LC.Recorder("sign")
    for quad, _tex in signs:
        r.face(quad, (1.0, 0.16, 0.12), [(0, 0), (1, 0), (1, 1), (0, 1)])
    return r


def write_glb(path, corp, prims, extras):
    """prims: [(name, material_index, attrs)]; materials fixed below."""
    bin_ = bytearray()
    views, accessors, mprims = [], [], []
    CT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def add(arr, typ, target=34962, minmax=False):
        flat = [v for e in arr for v in (e if isinstance(e, (tuple, list)) else (e,))]
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(struct.pack("<%df" % len(flat), *flat))
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(flat) * 4, target=target))
        a = dict(bufferView=len(views) - 1, componentType=5126, count=len(arr), type=typ)
        if minmax:
            nc = CT[typ]
            a["min"] = [min(e[i] for e in arr) for i in range(nc)]
            a["max"] = [max(e[i] for e in arr) for i in range(nc)]
        accessors.append(a)
        return len(accessors) - 1

    for name, mat, at in prims:
        if not at["POSITION"]:
            continue
        attrs = {}
        for key, typ in (("POSITION", "VEC3"), ("NORMAL", "VEC3"), ("TEXCOORD_0", "VEC2"), ("COLOR_0", "VEC4"), ("_col", "VEC3"),
                         ("_bid", "SCALAR"), ("_wbid", "SCALAR"), ("_wc", "VEC3"), ("_wl", "SCALAR"), ("_wm", "SCALAR")):
            attrs[key] = add(at[key], typ, minmax=(key == "POSITION"))
        n = len(at["POSITION"])
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(struct.pack("<%dI" % n, *range(n)))
        views.append(dict(buffer=0, byteOffset=off, byteLength=n * 4, target=34963))
        accessors.append(dict(bufferView=len(views) - 1, componentType=5125, count=n, type="SCALAR"))
        mprims.append(dict(attributes=attrs, indices=len(accessors) - 1, material=mat, mode=4, extras=dict(accumulator=name)))
    materials = [
        dict(name="surf", pbrMetallicRoughness=dict(baseColorFactor=[1, 1, 1, 1], metallicFactor=0.0, roughnessFactor=0.8), doubleSided=True),
        dict(name="neon", pbrMetallicRoughness=dict(baseColorFactor=[1, 1, 1, 1], metallicFactor=0.0, roughnessFactor=1.0),
             extensions={"KHR_materials_unlit": {}}, doubleSided=True),
        dict(name="glass", pbrMetallicRoughness=dict(baseColorFactor=[1, 1, 1, 0.35], metallicFactor=0.0, roughnessFactor=0.07),
             alphaMode="BLEND", doubleSided=True),
    ]
    gltf = dict(asset=dict(version="2.0", generator="export_landmarks.py (rebel_cell art-pass, queue item 4)"),
                extensionsUsed=["KHR_materials_unlit"], scene=0, scenes=[dict(nodes=[0])],
                nodes=[dict(name="landmark_" + corp, mesh=0, extras=extras)], meshes=[dict(name=corp + "_landmark", primitives=mprims)],
                materials=materials, buffers=[dict(byteLength=len(bin_))], bufferViews=views, accessors=accessors)
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * (-len(js) % 4)
    while len(bin_) % 4:
        bin_.append(0)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_))
    return total


def main(corps):
    entries = {}
    for corp in corps:
        accs, ret, entry, signs = run(corp)
        bid = "hq:%s" % corp
        prims = []
        for name, mat in (("SURF", 0), ("SMOOTH", 0), ("NEON", 1), ("GLASS", 2), ("STREAK", 1)):
            prims.append((name.lower(), mat, prim_data(accs[name])))
        if signs:
            prims.append(("sign", 1, prim_data(sign_rec(signs))))
        e = entry["entry"]
        extras = dict(corp=corp, building_ids=[bid], units="BU", up="Y (exported from Z-up)", entry=e, entry_nrm=entry["entry_nrm"],
                      entry_gltf=[e[0], e[2], -e[1]], label=list(ret["label"]), crown=list(ret["crown"]) if ret.get("crown") else None,
                      hue=list(ret["hue"]), sign_texture="mainframe_blade.png" if signs else None)
        out = os.path.join(HERE, "%s_landmark.glb" % corp)
        size = write_glb(out, corp, prims, extras)
        nv = sum(len(p[2]["POSITION"]) for p in prims)
        print("%-11s %9d bytes  %7d vertices  entry %s" % (corp, size, nv, entry))
        entries[corp] = entry
    return entries


if __name__ == "__main__":
    main(sys.argv[1:] or list(MODULES))
