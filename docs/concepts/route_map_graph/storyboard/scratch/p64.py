D = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts\\"
s = open(D + "sb_onecity.py").read()
o = '''        pts = [L.W(p) for p in l["pts"]]
        for a, c in zip(pts, pts[1:]):
            ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
            lo, hi = sorted((a[ax], c[ax]))'''
n = '''        pts = [L.W(p) for p in l["pts"]]
        for a, c in zip(pts, pts[1:]):
            ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
            lo, hi = sorted((a[ax], c[ax]))
            # the border street includes the stretch a netrun may extend along (choose_street's `extend`)
            lo, hi = lo - max(RULES["extend"]), hi + max(RULES["extend"])'''
assert o in s
s = s.replace(o, n)
open(D + "sb_onecity.py", "w").write(s)
print("ok")
