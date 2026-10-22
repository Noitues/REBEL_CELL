"""Street round 2 on the build session's street: convert its plate inputs into the r2 pipeline's own inputs.

python r2_from_build.py <plate_inputs dir> <out scratch dir>

The build session (Godot) exports, per seed, the city it renders (city.json), the street it derived (derive_street.json),
its net (net.json) and the two plate cameras (street_*_capture.json). The r2 pipeline reads the unified layout (lots,
layout36 frame), the v3 derivation (derive_v3.json), a layout log and the storyboard net. This writes those four from
the build files, so `R2_SCR=<out> NET36=<net name> python r2_jobs.py ...` renders the plates on the build street.

Nothing is re-derived: build's street, rooms and cameras are taken as they are. The art layout rules do run
(`R2_FROM_BUILD=1 r2_jobs.py prep`): build's city.json comes out of NetrunArtLayoutRules, but its frontage on seed 1 stays
low (median top 15 BU against 24 on the r2 street; frontage.silhouette fails), and the plate is the target look on this
street, so r2_rules.layout_pass raises it from unified_base_s1.json, with the netrun street as its one leg. Frames:
- build world (BU) = layout36 W(lots) with CX = CY = 6, so lots = (x / 6 + 6, -y / 6 + 6);
- build lot cell (i, j) spans x in [(i - 2.5) * 6, (i - 1.5) * 6], so its lot corner is (i + 3.5, j + 3.5);
- heights: the unified layout stores game px, BU = px * KH;
- yaw: build uses the rig convention (0 north, clockwise), layout36 the math one: yaw = 90 - rig yaw.
"""
import json
import math
import os
import sys

U = 6.0
CX = CY = 6.0
KH = U / 41.64 * 1.15
LOT_OFF = 3.5                          # build lot index -> unified lot corner
# lane colours of the r2 city (unified_r2_s1 tiles, the eight district lane colours)
LANES = [(0.239, 1.0, 0.545), (0.69, 0.302, 1.0), (1.0, 0.549, 0.102), (0.498, 0.659, 1.0), (1.0, 0.69, 0.0),
         (1.0, 0.239, 0.659), (0.549, 0.482, 1.0), (0.3, 0.85, 1.0)]
TERR = {"": [1, 1, 1], "solace": [0.239, 1.0, 0.545], "meridian": [1.0, 0.549, 0.102], "halcyon": [0.549, 0.482, 1.0],
        "orbital": [0.498, 0.659, 1.0], "rebel_cell": [0.91, 0.078, 0.118]}


def lots(p):
    return [p[0] / U + CX, -p[1] / U + CY]


def cell_q(i, j):
    x0, y0 = i + LOT_OFF, j + LOT_OFF
    return [[x0, y0], [x0 + 1, y0], [x0 + 1, y0 + 1], [x0, y0 + 1]]


def _h(*v):
    """Deterministic small hash (no python hash(): it is salted per process)."""
    h = 1469598103934665603
    for x in v:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h


def city(c):
    """unified layout: one record per building part; uid = '<ci>_<key>' with ci = the building index, key unique."""
    out, by_bid, key = [], {}, 0
    for ci, b in enumerate(c["buildings"]):
        uids = []
        for p in sorted(b["parts"], key=lambda p: p["z0"]):
            key += 1
            out.append(dict(q=[lots(v) for v in p["poly"]], z0=p["z0"] / KH, h=p["h"] / KH, ts=float(p["taper"]),
                            ink=list(TERR.get(b["terr"], TERR[""])), terr=b["terr"], ci=ci, key=key))
            uids.append((ci, key))
        by_bid[b["bid"]] = uids
    tiles = []
    for s in c["streets"]:
        i, j = s["lot"]
        q = cell_q(i, j)
        ab, col = None, None
        if s["along_i"] != s["along_j"]:                 # a street run (not a crossing): its centre line and lane colour
            x0, y0 = i + LOT_OFF, j + LOT_OFF
            if s["along_i"]:
                ab = [[x0, y0 + 0.5], [x0 + 1, y0 + 0.5]]
                col = LANES[_h(1, j) % len(LANES)]
            else:
                ab = [[x0 + 0.5, y0], [x0 + 0.5, y0 + 1]]
                col = LANES[_h(2, i) % len(LANES)]
        tiles.append(dict(q=q, ab=ab, col=list(col) if col else None, tr=float(s["traffic"]), i=i, j=j))
    plazas = [dict(q=cell_q(*pz["lot"]), terr=pz["terr"]) for pz in c["plazas"]]
    hqs = {k: [v[0] + v[2] / 2.0 + LOT_OFF, v[1] + v[3] / 2.0 + LOT_OFF] for k, v in sorted(c["hqs"].items())}
    return dict(centre=[CX, CY], radius=122.0, tiles=tiles, buildings=out, plazas=plazas, trails=[], fist=[],
                fist_col=TERR["rebel_cell"], fist_half=17.0, terr=TERR, street=[0.02, 0.024, 0.035], ground=[0.039, 0.047, 0.078],
                hqs=hqs), by_bid


def net(n):
    """The storyboard net: lots in the layout36 frame; build's `core` is the Cell's home (the uplink pad)."""
    nodes = [dict(id=x["id"], lot=lots(x["lot"]), state=x["state"], kind=x["state"]) for x in n["nodes"]]
    links = [dict(a=l["a"], b=l["b"], state=l["state"], pts=[lots(p) for p in l["pts"]]) for l in n["links"]]
    home = next((x for x in nodes if x["state"] == "core"), None)
    return dict(nodes=nodes, links=links, fist=[], cell_base=home["lot"] if home else [CX, CY])


def camera(cap):
    """build pose -> the r2 camera dict (layout36 yaw, the perspective block the scene and the projections read)."""
    k = cap["camera"]
    yaw = 90.0 - k["yaw"]
    return dict(yaw=yaw, pitch=k["pitch"], target=list(k["tgt"]), ortho=k["dist"] * 36.0 / k["lens"], dist=k["dist"],
                persp=dict(loc=list(k["loc"]), lens=k["lens"], sx=k["shift_x"], sy=k["shift_y"], tgt=list(k["tgt"])))


def derive(d, by_bid, cap_ov, cap_dec):
    nrm = d["nrm"]
    axis = 0 if abs(nrm[0]) < 0.5 else 1             # the street runs across its normal
    a, c = d["street"]["a"], d["street"]["c"]
    # the r2 code reads the axis from a / c: keep the leg straight along the axis, through `a`'s line
    if axis == 1:
        a2, c2 = [a[0], a[1]], [a[0], c[1]]
    else:
        a2, c2 = [a[0], a[1]], [c[0], a[1]]
    sgn = 1.0 if c2[axis] >= a2[axis] else -1.0
    # side: +1 = left of the walking direction a -> c (r2_onecity.frontage)
    if axis == 0:
        side = int(round(nrm[1] * sgn))
    else:
        side = int(round(-nrm[0] * sgn))

    def base_uid(bid):
        ci, key = by_bid[bid][0]
        return "%d_%d" % (ci, key)

    rooms = {}
    for rid, r in sorted(d["rooms"].items()):
        uids = ["%d_%d" % u for u in by_bid[r["bld"]]]
        keys = [u[1] for u in by_bid[r["bld"]]]
        rooms[rid] = dict(front=r["front"], back=r["back"], floor=r["floor"], span=r["span"], bld=keys[0], bld_uid=uids[0],
                          parts=[keys[i] for i in r.get("parts", [0]) if i < len(keys)], layer=r["layer"], kind=r["kind"])
    col_info = []
    for ci_ in d["col_info"]:
        ci, key = by_bid[ci_["bid"]][0]
        col_info.append(dict(layer=ci_["layer"], key=key, uid="%d_%d" % (ci, key), top=ci_["top"],
                             u0=a2[axis] + sgn * ci_["u0"], u1=a2[axis] + sgn * ci_["u1"], face=ci_["face"]))
    columns = [[layer, by_bid[bid][0][1]] for layer, bid in d["columns"]]
    column_uids = [base_uid(bid) for _, bid in d["columns"]]
    route_uids, route_keys = [], []
    for bid in d["route_keys"]:
        for ci, key in by_bid[bid]:
            route_uids.append("%d_%d" % (ci, key))
            route_keys.append(key)
    frontage = [[by_bid[f[0]][0][1]] + list(f[1:]) for f in d["frontage"]]
    street_len = abs(c2[axis] - a2[axis])
    return dict(col_info=col_info, edges=d["edges"], leg=0, side=side, a=a2, c=c2, nrm=nrm, start_left=d["start_left"],
                span=d["span"], columns=columns, column_uids=column_uids, route_uids=route_uids, route_keys=route_keys,
                street_len=street_len, rooms=rooms, overview=camera(cap_ov), decision=camera(cap_dec), frontage=frontage,
                source=dict(run=d["run"], layout_seed=d["layout_seed"], street=d["street"]))


def main(src, out, net_dir):
    os.makedirs(out, exist_ok=True)
    J = lambda n: json.load(open(os.path.join(src, n)))
    c, d, n = J("city.json"), J("derive_street.json"), J("net.json")
    cap_ov, cap_dec = J("street_overview_capture.json"), J("street_decision_capture.json")
    lay, by_bid = city(c)
    nt = net(n)
    lay["cell_base"] = nt["cell_base"]
    D = derive(d, by_bid, cap_ov, cap_dec)
    # the city before the art layout rules: r2_rules.layout_pass (R2_FROM_BUILD) writes unified_r2_s1.json from it
    json.dump(lay, open(os.path.join(out, "unified_base_s1.json"), "w"))
    json.dump(D, open(os.path.join(out, "derive_v3.json"), "w"), indent=1)
    json.dump(dict(seed=1, source="build plate_inputs", spikes=[]), open(os.path.join(out, "layout_log_s1.json"), "w"), indent=1)
    nt.update(hq={k: v for k, v in lay["hqs"].items()}, corp="meridian")
    json.dump(nt, open(os.path.join(net_dir, "net_build_s1.json"), "w"), indent=1)
    print("buildings %d parts %d tiles %d plazas %d hqs %s; street axis %d side %d len %.1f; rooms %d, columns %d, route parts %d"
          % (len(c["buildings"]), len(lay["buildings"]), len(lay["tiles"]), len(lay["plazas"]), sorted(lay["hqs"]),
             0 if abs(D["nrm"][0]) < 0.5 else 1, D["side"], D["street_len"], len(D["rooms"]), len(D["columns"]), len(D["route_uids"])))
    for nm in ("overview", "decision"):
        k = D[nm]
        f = [k["target"][i] - k["persp"]["loc"][i] for i in range(3)]
        print(nm, "yaw %.2f (from loc->tgt %.2f) pitch %.2f (from loc->tgt %.2f) dist %.2f (|loc-tgt| %.2f)"
              % (k["yaw"], math.degrees(math.atan2(f[1], f[0])), k["pitch"], math.degrees(math.atan2(-f[2], math.hypot(f[0], f[1]))),
                 k["dist"], math.sqrt(sum(v * v for v in f))))


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    NETD = "D:/rc_art/art-pass/docs/concepts/route_map_graph/storyboard/scripts/scratch/layout"
    main(sys.argv[1], sys.argv[2], NETD)
