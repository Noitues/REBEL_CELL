D = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts\\"
s = open(D + "sb_onecity.py").read()
s = s.replace('''    return dict(edges=link_paths(rooms), floor_px=_FPX[0], leg=li, side=side,''',
'''    cols = [dict(layer=l, key=b["key"], top=b["h"], u0=(b["x0"] if b["axis"] == 0 else b["y0"]),
                 u1=(b["x1"] if b["axis"] == 0 else b["y1"]), face=b["face"]) for l, b in asg]
    return dict(col_info=cols, edges=link_paths(rooms), floor_px=_FPX[0], leg=li, side=side,''')
open(D + "sb_onecity.py", "w").write(s)
j = open(D + "sb_ocjobs.py").read()
j = j.replace('''rooms=d["rooms"], edges=d["edges"], overview=d["overview"],''', '''rooms=d["rooms"], edges=d["edges"], col_info=d["col_info"], overview=d["overview"],''')
j = j.replace('''             layout_path=OC.LAYPATH, edges=D["edges"])''', '''             layout_path=OC.LAYPATH, edges=D["edges"], col_info=D["col_info"], hero_sign_rule=OC.LAYOUT_RULES["hero_sign_rule"])''')
open(D + "sb_ocjobs.py", "w").write(j)
b = open(D + "m44/onecity_build.py").read()
o = '''RB_OBJ = RB.obj(TOON)'''
n = '''# (c) hero_sign_rule: one blade sign at each route column's street-face corner (the start side) and one lit band under
# its roof, in the district pair alternating along the street (look preset palette: magenta / cyan)
_HS = OC.get("hero_sign_rule") or {}
_PAL2 = [(1.0, 0.16, 0.6), (0.16, 0.8, 1.0)]
for k, ci in enumerate(sorted(OC.get("col_info", []), key=lambda c: c["layer"])):
    col = _PAL2[k % 2]
    i0 = next(iter(OPEN))
    ax, nrm = i0[1], i0[7]
    face = ci["face"]

    def PS(u, d, z):
        return (u, face - d * nrm, z) if ax == 0 else (face - d * nrm, u, z)
    hs = random.Random(9970 + k)
    if _HS.get("blade", True):
        uc = ci["u1"] - 0.25 if (OC["street"]["a"][ax] > OC["street"]["c"][ax]) else ci["u0"] + 0.25
        z0s, z1s = 2.2, max(4.5, ci["top"] - 1.6)
        beam(PS(uc, 0.25, z0s - 0.3), PS(uc, 0.25, z1s + 0.3), 0.12, (0.2, 0.2, 0.24), acc=RB)
        npan = max(3, int((z1s - z0s) / 1.4))
        for p in range(npan):
            za = z0s + (z1s - z0s) * p / npan
            zb = za + (z1s - z0s) / npan - 0.18
            cc = col if (p + k) % 3 else tuple(min(1, v * 0.6 + 0.4) for v in col)
            RBN.face([PS(uc - 0.0, 0.35, za), PS(uc, 1.15, za), PS(uc, 1.15, zb), PS(uc, 0.35, zb)], cc, (0, 0, 0))
            RBN.face([PS(uc, 1.15, za), PS(uc, 0.35, za), PS(uc, 0.35, zb), PS(uc, 1.15, zb)], cc, (0, 0, 0))
    if _HS.get("band", True):
        zt = ci["top"] - 0.75
        RBN.face([PS(ci["u0"] + 0.4, 0.06, zt), PS(ci["u1"] - 0.4, 0.06, zt), PS(ci["u1"] - 0.4, 0.06, zt + 0.32),
                  PS(ci["u0"] + 0.4, 0.06, zt + 0.32)], tuple(v * 0.85 for v in _PAL2[(k + 1) % 2]), (0, 0, 0))
print("ONECITY hero signs", len(OC.get("col_info", [])), flush=True)

RB_OBJ = RB.obj(TOON)'''
assert o in b
b = b.replace(o, n)
b = b.replace("i0 = next(iter(OPEN))", "i0 = OPEN[0]")
open(D + "m44/onecity_build.py", "w").write(b)
print("ok")
