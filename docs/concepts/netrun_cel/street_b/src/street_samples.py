"""Read the port's street samples (content/b/street_sample/*.tres, copied to D:/rc_scratch/street_b/samples)
and report: layer sizes, type counts, link fan-out, and fork -> two lanes -> rejoin windows.

Run: python street_samples.py   (writes D:/rc_scratch/street_b/samples_report.txt and samples.json)
"""
import glob
import json
import os
import re

SRC = "D:/rc_scratch/street_b/samples"
OUT = "D:/rc_scratch/street_b"


def parse(path):
    txt = open(path, encoding="utf-8").read()
    depth = int(re.search(r"^depth = (\d+)", txt, re.M).group(1))
    places = re.findall(r'"([^"]+)"', re.search(r"^places = PackedStringArray\((.*)\)", txt, re.M).group(1))
    nodes = []
    for m in re.finditer(r"\{(.*?)\}", txt, re.S):
        body = m.group(1)
        g = lambda k: re.search(r'"%s": ([^,\n]+)' % k, body)
        if not g("id"):
            continue
        links = [int(x) for x in re.findall(r"\d+", re.search(r'"links": \[(.*?)\]', body, re.S).group(1))]
        nodes.append(dict(id=int(g("id").group(1)), layer=int(g("layer").group(1)), row=int(g("row").group(1)),
                          type=g("type").group(1).strip().strip('"'), arch=g("arch").group(1).strip().strip('"'),
                          links=links))
    return dict(depth=depth, places=places, nodes=nodes)


def windows(s):
    """fork node f -> exactly two next nodes a, b; each lane may run 1-2 layers with single links; both end at one node."""
    by = {n["id"]: n for n in s["nodes"]}
    out = []
    for f in s["nodes"]:
        if len(f["links"]) != 2:
            continue
        a, b = f["links"]
        for la in range(1, 3):
            pa, pb = [a], [b]
            ok = True
            for _ in range(la - 1):
                na, nb = by[pa[-1]], by[pb[-1]]
                if len(na["links"]) != 1 or len(nb["links"]) != 1 or na["links"] == nb["links"]:
                    ok = False
                    break
                pa.append(na["links"][0])
                pb.append(nb["links"][0])
            if not ok:
                continue
            ea, eb = by[pa[-1]]["links"], by[pb[-1]]["links"]
            common = sorted(set(ea) & set(eb))
            if common:
                out.append(dict(fork=f["id"], lane_a=pa, lane_b=pb, rejoin=common, lane_len=la,
                                pure=len(ea) == 1 and len(eb) == 1))
    return out


def main():
    rep = []
    allj = {}
    for p in sorted(glob.glob(os.path.join(SRC, "*.tres"))):
        s = parse(p)
        name = os.path.basename(p)
        allj[name] = s
        sizes = [sum(1 for n in s["nodes"] if n["layer"] == l) for l in range(1, s["depth"] + 1)]
        types = {}
        for n in s["nodes"]:
            types[n["type"]] = types.get(n["type"], 0) + 1
        fan = {}
        for n in s["nodes"]:
            fan[len(n["links"])] = fan.get(len(n["links"]), 0) + 1
        rep.append("== %s depth %d sizes %s" % (name, s["depth"], sizes))
        rep.append("   places %s" % s["places"])
        rep.append("   types %s fan-out %s" % (dict(sorted(types.items())), dict(sorted(fan.items()))))
        for l in range(1, s["depth"] + 1):
            rep.append("   L%d %s" % (l, "  ".join("%d r%d %s>%s" % (n["id"], n["row"], n["type"], n["links"])
                                                   for n in s["nodes"] if n["layer"] == l)))
        for w in windows(s):
            rep.append("   WINDOW %s" % w)
    open(os.path.join(OUT, "samples_report.txt"), "w").write("\n".join(rep))
    json.dump(allj, open(os.path.join(OUT, "samples.json"), "w"), indent=1)
    print("\n".join(rep))


if __name__ == "__main__":
    main()
