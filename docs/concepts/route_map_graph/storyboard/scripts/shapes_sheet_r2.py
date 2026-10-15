"""AAA-2 r2: the building-shapes sheet (exec'd into scene_aaa.py when the job has "shapes_sheet"). Every new shape of
designer note 5 stands alone in a row far off to the side of the street (x >= SHEET_X0), on its own wet ground, lit by
a low key and a cool fill. The labels are drawn in post (sheet_r2.py) from the projected cell centres written here."""

SHEET_X0 = 3000.0
SHEET_STEP = 46.0
SHEET_CELLS = []
_g = (0.16, 0.14, 0.2)
with OwnRng(9500):
    set_sem(0.2, 0, 0)
    box(SHEET_X0 - 40, -60, -1.0, SHEET_X0 + SHEET_STEP * 9 + 20, 60, 0.0, _g, facet=False)
    fam = FAMS


    def cell(k):
        return SHEET_X0 + SHEET_STEP * k


    # 1. round tower (mid row)
    set_sem(0.6, 0, 0)
    round_tower(cell(0), 6.0, 6.5, 62.0, tuple(v * 0.82 for v in fam[1]), crown=CYAN, spire_h=12.0)
    SHEET_CELLS.append((cell(0), "ROUND TOWER", "drum + 2 setback drums, crown ring"))
    # 2. the cut drum route column, with room boxes in its cut storeys
    set_sem(0.1, 0, 5)
    x0, x1 = cell(1) - 7.0, cell(1) + 7.0
    cut_drum(x0, x1, 0.0, 5, {1, 3}, fam[4], TRIMS[0])
    for f, lc in ((1, (0.36, 0.88, 1.0)), (3, (1.0, 0.77, 0.24))):
        za, zb = f * FH, (f + 1) * FH
        box(x0, 0, za - SLAB / 2, x1, DEPTH, za + SLAB / 2, CUT, facet=False)
        box(x0, 0, zb - SLAB / 2, x1, DEPTH, zb + SLAB / 2, CUT, facet=False)
        box(x0, 0, za, x0 + 0.7, DEPTH, zb, CUT, facet=False)
        box(x1 - 0.7, 0, za, x1, DEPTH, zb, CUT, facet=False)
        quad_y(SOLID, x0 + 0.7, za + 0.45, x1 - 0.7, zb - 0.45, DEPTH - 0.6, (0.22, 0.2, 0.26))
        quad_y(NEON, x0 + 1.0, za + 0.8, x1 - 1.0, zb - 0.8, DEPTH - 0.62, tuple(v * 0.5 for v in lc))
    SHEET_CELLS.append((cell(1), "CUT DRUM (ROUTE)", "rooms sliced at the front plane"))
    # 3. stepped ziggurat
    set_sem(0.6, 0, 0)
    ziggurat(cell(2) - 11.0, -6.0, cell(2) + 11.0, 12.0, 70.0, 5, fam[0], inset=2.0, trim=VIOLET)
    SHEET_CELLS.append((cell(2), "ZIGGURAT", "5 stepped tiers"))
    # 4. convex curved facade
    curved_block(cell(3) - 15.0, -4.0, cell(3) + 15.0, 12.0, 46.0, fam[5], 5.0, CYAN)
    SHEET_CELLS.append((cell(3), "CURVED FACADE", "convex street face"))
    # 5. concave crescent
    prism(fp_curved(cell(4) - 15.0, -2.0, cell(4) + 15.0, 14.0, -4.5, 16), 0.0, 40.0, fam[2])
    ring_trim(fp_curved(cell(4) - 15.0, -2.1, cell(4) + 15.0, 14.0, -4.5, 16)[:17], 40.1, PINK, 0.25, closed=False)
    SHEET_CELLS.append((cell(4), "CRESCENT", "concave curved facade"))
    # 6. terraced run on shared walls
    terraced_run(cell(5) - 18.0, -4.0, cell(5) + 18.0, 12.0, (44.0, 34.0, 24.0), fam[0], VIOLET)
    SHEET_CELLS.append((cell(5), "TERRACED RUN", "adjoining, shared walls"))
    # 7. two towers joined by a podium (columns 1 + 2)
    set_sem(0.1, 0, 1)
    fa = fam[4]
    prism(fp_rect(cell(6) - 19.0, -3.0, cell(6) - 7.0, 9.0), 0.0, 44.0, fa)
    prism(fp_rect(cell(6) + 7.0, 2.0, cell(6) + 19.0, 14.0), 0.0, 52.0, tuple(v * 0.95 for v in fa))
    prism(fp_rect(cell(6) - 7.6, 4.2, cell(6) + 7.6, 16.0), 0.0, 6.4, tuple(v * 0.9 for v in fa))
    prism(fp_rect(cell(6) - 7.6, 7.2, cell(6) + 7.6, 16.0), 6.4, 12.4, tuple(v * 0.84 for v in fa))
    quad_y(NEON, cell(6) - 6.8, 0.6, cell(6) + 6.8, 3.2, 4.14, (0.06, 0.33, 0.4))
    for k in range(5):
        wx = cell(6) - 6.4 + k * 2.6
        WIN.face([(wx, 7.15, 8.0), (wx + 1.3, 7.15, 8.0), (wx + 1.3, 7.15, 10.6), (wx, 7.15, 10.6)], (0.62, 0.42, 0.18), (0, 0, 0))
    SHEET_CELLS.append((cell(6), "PODIUM-JOINED PAIR", "route columns 1 + 2"))
    # 8. fat block with rounded corners
    set_sem(0.6, 0, 0)
    prism(fp_round_corners(cell(7) - 19.0, -4.0, cell(7) + 19.0, 14.0, 6.0), 0.0, 30.0, fam[3])
    prism(fp_round_corners(cell(7) - 14.0, 0.0, cell(7) + 14.0, 14.0, 4.0), 30.0, 38.0, tuple(v * 0.94 for v in fam[3]))
    SHEET_CELLS.append((cell(7), "FAT BLOCK", "wide, rounded corners"))
    # 9. stepped drum megastructure (scaled 1:6)
    _cx, _r = cell(8), 14.0
    _c = (0.16, 0.15, 0.2)
    prism(fp_circle(_cx, _r - 4, _r, n=40), 0, 34, _c)
    prism(fp_circle(_cx, _r - 4, _r * 0.8, n=40), 34, 50, _c)
    prism(fp_circle(_cx, _r - 4, _r * 0.56, n=40), 50, 62, _c)
    for _z, _k in ((34, 1.0), (50, 0.8)):
        ring_trim(fp_circle(_cx, _r - 4, _r * _k + 0.3, n=40), _z - 0.6, (0.28, 0.12, 0.3), 0.5)
    SHEET_CELLS.append((cell(8), "DRUM MEGASTRUCTURE", "far skyline (1:6)"))

# sheet lights: a low warm key from the front left, a cool fill from the right, a rim from behind
_sx = SHEET_X0 + SHEET_STEP * 4
for nm, loc, rot, e, c, sz in (("sheet_key", (_sx - 160, -260, 160), (math.radians(58), 0, math.radians(-32)), 2.2e6, (1.0, 0.8, 0.62), 120.0),
                               ("sheet_fill", (_sx + 220, -200, 60), (math.radians(75), 0, math.radians(48)), 9.0e5, (0.55, 0.7, 1.0), 120.0),
                               ("sheet_rim", (_sx, 220, 120), (math.radians(-60), 0, 0), 1.2e6, (1.0, 0.35, 0.75), 200.0)):
    ld = bpy.data.lights.new(nm, "AREA")
    ld.energy, ld.color, ld.size = e, c, sz
    ob = bpy.data.objects.new(nm, ld)
    ob.location, ob.rotation_euler = loc, rot
    ob.visible_camera = False
    scene.collection.objects.link(ob)
print("shapes sheet: %d cells" % len(SHEET_CELLS), flush=True)
