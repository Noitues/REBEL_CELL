"""Headless id_ground check: python glb_tris.py <new.glb> <old.glb>  (exit 1 on failure). No Blender, no Godot."""
import json, struct, sys


def load(path):
    d = open(path, "rb").read()
    jl, _ = struct.unpack_from("<II", d, 12)
    return json.loads(d[20:20 + jl].decode())


def tris_by_node(g):
    out = {}
    for n in g["nodes"]:
        if "mesh" not in n:
            continue
        t = {}
        for pr in g["meshes"][n["mesh"]]["primitives"]:
            cnt = g["accessors"][pr["indices"]]["count"] if "indices" in pr else g["accessors"][pr["attributes"]["POSITION"]]["count"]
            m = g["materials"][pr["material"]]["name"]
            t[m] = t.get(m, 0) + cnt // 3
        out[n.get("name", "?")] = t
    return out


def main(new, old):
    gn, go = load(new), load(old)
    tn, to = tris_by_node(gn), tris_by_node(go)
    ok = True
    if "id_ground" not in tn:
        print("FAIL no id_ground node"); ok = False
    else:
        idx = [i for i, n in enumerate(gn["nodes"]) if n.get("name") == "id_ground"]
        if len(idx) != 1:
            print("FAIL %d id_ground nodes" % len(idx)); ok = False
        parents = [i for i, n in enumerate(gn["nodes"]) if idx[0] in n.get("children", [])]
        print("id_ground tris by material:", tn["id_ground"], "parent:", [gn["nodes"][p].get("name") for p in parents] or "scene root")
        pos = [a for n in gn["nodes"] if n.get("name") == "id_ground" for pr in gn["meshes"][n["mesh"]]["primitives"] for a in [gn["accessors"][pr["attributes"]["POSITION"]]]]
        print("id_ground glTF y range: %.3f .. %.3f" % (min(a["min"][1] for a in pos), max(a["max"][1] for a in pos)))
    sum_new = sum(sum(t.values()) for t in tn.values())
    sum_old = sum(sum(t.values()) for t in to.values())
    by_new, by_old = {}, {}
    for t in tn.values():
        for k, v in t.items(): by_new[k] = by_new.get(k, 0) + v
    for t in to.values():
        for k, v in t.items(): by_old[k] = by_old.get(k, 0) + v
    print("total tris new %d old %d; by material equal: %s" % (sum_new, sum_old, by_new == by_old))
    if sum_new != sum_old or by_new != by_old:
        print("FAIL tri count differs", by_new, by_old); ok = False
    print("materials new %s old %s" % (sorted(m["name"] for m in gn["materials"]), sorted(m["name"] for m in go["materials"])))
    return 0 if ok else 1


sys.exit(main(sys.argv[1], sys.argv[2]))
