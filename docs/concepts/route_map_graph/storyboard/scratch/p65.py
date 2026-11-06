D = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts\\"
s = open(D + "sb_onecity.py").read()
o = '''# ---------------------------------------------------------------- cameras (unified world: yaw convention of layout36)'''
n = '''def link_paths(rooms):
    """The route links on the derived street (the wax pencil's world paths): from the side of room a facing b, out to
    the facade line (0.5 BU in front of the street faces), across at mid height between the two buildings, and into
    room b; Manhattan, on the facade plane, so the pencil reads as running along the street front."""
    out = []
    for (a, b) in sorted(G.edge_states(G.WALK_START, G.states(G.WALK_START)[0]).keys()):
        ra, rb = rooms[a], rooms[b]
        fa, fb_ = ra["front"], rb["front"]
        ax = 0 if abs(fa[0][1] - fa[1][1]) < 1e-6 else 1
        nrm_s = 1.0 if (ra["back"][0][1 - ax] > fa[0][1 - ax]) else -1.0
        face = min(fa[0][1 - ax], fb_[0][1 - ax]) if nrm_s > 0 else max(fa[0][1 - ax], fb_[0][1 - ax])
        face = face - 0.5 * nrm_s
        ua = [p[ax] for p in fa]
        ub = [p[ax] for p in fb_]
        dirn = 1.0 if sum(ub) > sum(ua) else -1.0
        xa = max(ua) if dirn > 0 else min(ua)
        xb = min(ub) if dirn > 0 else max(ub)
        za = (fa[0][2] + fa[2][2]) / 2
        zb = (fb_[0][2] + fb_[2][2]) / 2
        xm = (xa + xb) / 2

        def P(u, z):
            return (u, face, z) if ax == 0 else (face, u, z)
        out.append(dict(a=a, b=b, type="facade", path=[P(xa - dirn * 0.3, za), P(xm, za), P(xm, zb), P(xb + dirn * 0.3, zb)]))
    return out


# ---------------------------------------------------------------- cameras (unified world: yaw convention of layout36)'''
assert o in s
s = s.replace(o, n)
s = s.replace('''    return dict(floor_px=_FPX[0], leg=li, side=side,''', '''    return dict(edges=link_paths(rooms), floor_px=_FPX[0], leg=li, side=side,''')
open(D + "sb_onecity.py", "w").write(s)
j = open(D + "sb_ocjobs.py").read()
j = j.replace('''               columns=d["columns"], route_keys=d["route_keys"], rooms=d["rooms"], overview=d["overview"],''',
              '''               columns=d["columns"], route_keys=d["route_keys"], rooms=d["rooms"], edges=d["edges"], overview=d["overview"],''')
j = j.replace('''    b = dict(mode=mode, route_keys=D["route_keys"], rooms=D["rooms"], street=D["street"], look=LOOK, nrm=D["nrm"])''',
              '''    b = dict(mode=mode, route_keys=D["route_keys"], rooms=D["rooms"], street=D["street"], look=LOOK, nrm=D["nrm"],
             layout_path=OC.LAYPATH, edges=D["edges"])''')
open(D + "sb_ocjobs.py", "w").write(j)
print("ok")
