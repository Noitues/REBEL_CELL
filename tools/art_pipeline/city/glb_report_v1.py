"""ART-5 5b: summarise a .glb (nodes, meshes, attributes, materials, animations, extensions, bytes per attribute).

  python glb_report_v1.py <file.glb> [...]
"""
import json
import struct
import sys

SIZES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
CT = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, length = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67, "not a glb"
    clen, ctype = struct.unpack_from("<II", data, 12)
    js = json.loads(data[20:20 + clen].decode("utf-8"))
    return js, length


def report(path):
    js, length = read_glb(path)
    acc = js.get("accessors", [])
    by_attr = {}
    for m in js.get("meshes", []):
        for p in m["primitives"]:
            for k, i in p["attributes"].items():
                a = acc[i]
                by_attr.setdefault(k, [0, set()])
                by_attr[k][0] += a["count"] * SIZES[a["type"]] * CT[a["componentType"]]
                by_attr[k][1].add("%s/%d" % (a["type"], a["componentType"]))
            if "indices" in p:
                a = acc[p["indices"]]
                by_attr.setdefault("indices", [0, set()])
                by_attr["indices"][0] += a["count"] * CT[a["componentType"]]
    print(path, "bytes", length)
    print("  nodes", len(js.get("nodes", [])), "meshes", len(js.get("meshes", [])), "materials", [m["name"] for m in js.get("materials", [])])
    for k, (b, t) in sorted(by_attr.items()):
        print("  attr %-10s %9d B %s" % (k, b, sorted(t)))
    per = []
    for m in js.get("meshes", []):
        b = 0
        for p in m["primitives"]:
            for i in list(p["attributes"].values()) + ([p["indices"]] if "indices" in p else []):
                a = acc[i]
                b += a["count"] * SIZES[a["type"]] * CT[a["componentType"]]
        per.append((b, m.get("name", "?")))
    for b, n in sorted(per, reverse=True)[:6]:
        print("  mesh %-44s %9d B" % (n, b))
    for a in js.get("animations", []):
        print("  animation", a.get("name"), "channels", len(a["channels"]), "interp", sorted({s["interpolation"] for s in a["samplers"]}))
    print("  extensionsUsed", js.get("extensionsUsed"))
    for m in js.get("materials", [])[:3]:
        print("  material", json.dumps(m)[:300])


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
