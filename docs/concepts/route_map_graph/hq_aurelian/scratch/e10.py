p = "hq_graph.py"
s = open(p, encoding="utf-8", newline="").read()
s = s.replace("def mech(walked, mt=None):", '''BAND_BAYS = 1          # DESIGN.md 14.7: one grid bay (6 deg) either side of the current room and its options


def band_points(walked, mt=None):
    """The landmark's FACE BAND at the current level (DESIGN.md 14.7): the arc of the level's face from the current room to the
    options' rooms, plus one bay either side, as kit points (the front plane, floor and room-top heights). The occlusion cone
    covers it, so a tower in front of the colonnade (or the ring) is cut even where no room sits behind it."""
    cur = walked[-1]
    st, opts = states(walked, mt)  # noqa: F821
    ids = [i for i in [cur] + list(opts) if i in SLOT]
    pts = []
    for lv in sorted(set(SLOT[i]["level"] for i in ids)):
        ts = [SLOT[i]["t"] for i in ids if SLOT[i]["level"] == lv]
        sl = next(SLOT[i] for i in ids if SLOT[i]["level"] == lv)
        pad = BAND_BAYS * 360.0 / 60.0
        t0, t1 = min(ts) - pad, max(ts) + pad
        r = _level_r(sl)
        z0, h = sl["pos"][2], sl["size"][1]
        inward = sl["kind"] in ("cavea", "podium")
        for k in range(9):
            t = math.radians(t0 + (t1 - t0) * k / 8)
            x, y = AL.ell(t, r)
            for z in (z0, z0 + h):
                pts.append((x * KS, y * KS, z * KS))
    return pts


def mech(walked, mt=None):''', 1)
open(p, "w", encoding="utf-8", newline="").write(s)

p = "hq_run.py"
s = open(p, encoding="utf-8", newline="").read()
s = s.replace('''        fr["section"] = KDT.occlusion_params(pose.loc(), OC.cone_points(G, ids, int(mt_)), dtc)''', '''        pts_ = OC.cone_points(G, ids, int(mt_))
        if zoom >= 0.5:                      # DESIGN.md 14.7: DECISION / HOVER also cover the face band at the current level
            band = G.band_points(walked, int(mt_))
            fr["band_pts"] = [list(b) for b in band]
            pts_ = pts_ + band
        fr["section"] = KDT.occlusion_params(pose.loc(), pts_, dtc)''')
open(p, "w", encoding="utf-8", newline="").write(s)

p = "occ_check.py"
s = open(p, encoding="utf-8", newline="").read()
s += '''

def count_band(BLD, section, pose, pts, w=2560, KDT=None):
    """Buildings above stub height in front of and overlapping the face band's screen box (+PAD px)."""
    if KDT is None:
        from hq_kit import downtown as KDT  # noqa: N806
    q = [pose.proj(p, w=w) for p in pts]
    q = [v for v in q if v]
    xs, ys = [v[0] for v in q], [v[1] for v in q]
    box = (min(xs) - PAD, min(ys) - PAD, max(xs) + PAD, max(ys) + PAD)
    f, cam = pose.dir(), pose.loc()
    dep = min(sum((p[k] - cam[k]) * f[k] for k in range(3)) for p in pts)
    n = 0
    for b in BLD:
        zc, _a = KDT.occlusion_state(section, b)
        if zc <= section["occ_stub"] + STUB_TOL:
            continue
        x, y, top, hx, hy = b
        zt = min(zc, top)
        dc = (x - cam[0]) * f[0] + (y - cam[1]) * f[1] + (zt * 0.5 - cam[2]) * f[2]
        if dc - math.hypot(hx, hy) > dep:
            continue
        hp = [pose.proj((x + sx * hx, y + sy * hy, z), w=w) for sx in (-1, 1) for sy in (-1, 1) for z in (0.0, zt)]
        if any(v is None for v in hp):
            continue
        if _clip_area(_hull(hp), *box) > 4.0:
            n += 1
    return n
'''
open(p, "w", encoding="utf-8", newline="").write(s)

p = "aurelian_landmark.py"
s = open(p, encoding="utf-8", newline="").read()
s = s.replace('''    res.update(frame=fr.get("name"), n_buildings=len(BLD))''', '''    res.update(frame=fr.get("name"), n_buildings=len(BLD))
    if fr.get("band_pts"):
        res["band_occluders"] = OC.count_band(BLD, sec, pose, [tuple(b) for b in fr["band_pts"]])''')
s = s.replace('''    K.log("OCC %s rooms %d hit %d occluders %d" % (fr.get("name"), res["rooms"], res["rooms_hit"], res["buildings"]))''', '''    K.log("OCC %s rooms %d hit %d occluders %d band %s" % (fr.get("name"), res["rooms"], res["rooms_hit"], res["buildings"],
                                                          res.get("band_occluders")))''')
open(p, "w", encoding="utf-8", newline="").write(s)
