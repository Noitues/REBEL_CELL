D = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts\\"
s = open(D + "sb_onecity.py").read()
def sub(o, n):
    global s
    assert s.count(o) == 1, o
    s = s.replace(o, n)
sub('''LAYPATH = os.path.join(HERE, "scratch", "layout", "unified.json")''', '''LAYPATH0 = os.path.join(HERE, "scratch", "layout", "unified.json")
LAYPATH = os.path.join(HERE, "scratch", "layout", "unified_v3.json")     # the city with the v3 layout rules applied

# ---------------------------------------------------------------- v3 MAINLINE LAYOUT CHANGES (designer-approved)
# (a) frontage_min_floors: every building fronting a border-link street rises to at least this many floors
#     (+ 0..2 more floors by its key, so the street front is not a flat wall);
# (b) border_street_width: border-link streets are this wide (BU); the frontage on both sides steps back to it
#     (the base street tile is 6 BU = 1 lot);
# (c) hero_sign_rule: every route column carries one blade sign at its street-face corner and one lit band under its
#     roof, in the district pair alternating along the street (built in onecity_build.py).
LAYOUT_RULES = dict(frontage_min_floors=6, border_street_width=8.0, base_street_width=6.0,
                    hero_sign_rule=dict(blade=True, band=True, palette=("district_a", "district_b")))''')
sub('''def lay():
    return json.load(open(LAYPATH))''', '''def lay():
    if not os.path.exists(LAYPATH):
        apply_layout_rules()
    return json.load(open(LAYPATH))


def apply_layout_rules():
    """Write unified_v3.json: the base city with (a) the street-front band and (b) the wider border streets applied to
    the frontage of EVERY border link (not only the netrun's), so the HQ map and the netrun street are the same city."""
    LAY0 = json.load(open(LAYPATH0))
    net = L.load_net()
    fb = (0.8, 6.5)
    step = (LAYOUT_RULES["border_street_width"] - LAYOUT_RULES["base_street_width"]) / 2.0
    target_floors = LAYOUT_RULES["frontage_min_floors"]
    bases = []
    for b in LAY0["buildings"]:
        bi = bld_info(b)
        bi["ref"] = b
        bases.append(bi)
    tops = {}
    for bi in bases:
        if bi["z0"] > 0.05:
            cx, cy = (bi["x0"] + bi["x1"]) / 2, (bi["y0"] + bi["y1"]) / 2
            for bb in bases:
                if bb["z0"] <= 0.05 and bb["x0"] <= cx <= bb["x1"] and bb["y0"] <= cy <= bb["y1"]:
                    tops[bb["key"]] = max(tops.get(bb["key"], 0.0), bi["z0"] + bi["h"])
                    break
    done, raised, moved = set(), 0, 0
    for l in net["links"]:
        if l["state"] != "border":
            continue
        pts = [L.W(p) for p in l["pts"]]
        for a, c in zip(pts, pts[1:]):
            ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
            lo, hi = sorted((a[ax], c[ax]))
            for bi in bases:
                if bi["z0"] > 0.05 or bi["key"] in done:
                    continue
                if ax == 0:
                    a0, a1, d0, d1 = bi["x0"], bi["x1"], bi["y0"] - a[1], a[1] - bi["y1"]
                else:
                    a0, a1, d0, d1 = bi["y0"], bi["y1"], bi["x0"] - a[0], a[0] - bi["x1"]
                near = d0 if d0 > 0 else d1
                if not (a1 > lo and a0 < hi and fb[0] < near < fb[1]):
                    continue
                done.add(bi["key"])
                b = bi["ref"]
                # (b) step the street face back
                sgn = 1.0 if d0 > 0 else -1.0
                for p in b["q"]:
                    w = L.W(p)
                    if ax == 0 and abs(w[1] - (bi["y0"] if sgn > 0 else bi["y1"])) < 0.05:
                        p[1] -= sgn * step / L.U          # lots: y is flipped in W()
                        moved += 1
                    if ax == 1 and abs(w[0] - (bi["x0"] if sgn > 0 else bi["x1"])) < 0.05:
                        p[0] += sgn * step / L.U
                        moved += 1
                # (a) the street-front band
                top = max(bi["h"], tops.get(bi["key"], 0.0))
                want = (target_floors + abs(b["key"]) % 3) * RULES["floor_bu"] + 0.1
                if top < want:
                    b["h"] = want / KH
                    raised += 1
    json.dump(LAY0, open(LAYPATH, "w"))
    print("layout rules: frontage buildings %d, raised %d, street faces stepped back %d vertices" % (len(done), raised, moved))''')
open(D + "sb_onecity.py", "w").write(s)
print("ok")
