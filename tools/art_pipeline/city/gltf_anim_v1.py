"""ART-5 5b: add glTF 2.0 animations to an exported .glb (v1). Pure Python (runs inside Blender or outside).

The Blender exporter's animation output depends on its action / slot handling and sampling options; the landmark
loops are simple (a turning pivot, step-keyed flipbooks, a sliding train), so the driver records them as tracks and
this module writes them straight into the glb: one animation per loop, one sampler per track.

  track = dict(node=<node name>, path="translation" | "rotation" | "scale", interp="LINEAR" | "STEP",
               times=[seconds...], values=[[x, y, z] or [x, y, z, w] ...])   # glTF frame (+Y up)
"""
import json
import struct

FLOAT = 5126


def _read(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError("not a glb: %s" % path)
    off = 12
    js, binc = None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk.decode("utf-8"))
        elif ctype == 0x004E4942:
            binc = bytes(chunk)
        off += 8 + clen
    return js, bytearray(binc)


def _write(path, js, binc):
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * ((4 - len(jb) % 4) % 4)
    while len(binc) % 4:
        binc.append(0)
    total = 12 + 8 + len(jb) + 8 + len(binc)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        f.write(struct.pack("<II", len(binc), 0x004E4942))
        f.write(bytes(binc))


def _accessor(js, binc, floats, comps, minmax=False):
    while len(binc) % 4:
        binc.append(0)
    off = len(binc)
    flat = [v for row in floats for v in (row if isinstance(row, (list, tuple)) else [row])]
    binc.extend(struct.pack("<%df" % len(flat), *flat))
    js.setdefault("bufferViews", []).append(dict(buffer=0, byteOffset=off, byteLength=4 * len(flat)))
    acc = dict(bufferView=len(js["bufferViews"]) - 1, componentType=FLOAT, count=len(floats),
               type={1: "SCALAR", 3: "VEC3", 4: "VEC4"}[comps])
    if minmax:
        acc["min"] = [min(floats)]
        acc["max"] = [max(floats)]
    js.setdefault("accessors", []).append(acc)
    return len(js["accessors"]) - 1


def add_animations(path, animations):
    """animations: {name: [track, ...]}; writes them into the glb at `path` (replacing same-named ones)."""
    js, binc = _read(path)
    names = {n.get("name"): i for i, n in enumerate(js.get("nodes", []))}
    anims = [a for a in js.get("animations", []) if a.get("name") not in animations]
    for name, tracks in animations.items():
        samplers, channels = [], []
        for t in tracks:
            if t["node"] not in names:
                raise KeyError("no node %s in %s" % (t["node"], path))
            ti = _accessor(js, binc, t["times"], 1, minmax=True)
            vo = _accessor(js, binc, t["values"], len(t["values"][0]))
            samplers.append(dict(input=ti, output=vo, interpolation=t["interp"]))
            channels.append(dict(sampler=len(samplers) - 1, target=dict(node=names[t["node"]], path=t["path"])))
        anims.append(dict(name=name, samplers=samplers, channels=channels))
    js["animations"] = anims
    js["buffers"][0]["byteLength"] = len(binc) + ((4 - len(binc) % 4) % 4)
    _write(path, js, binc)
