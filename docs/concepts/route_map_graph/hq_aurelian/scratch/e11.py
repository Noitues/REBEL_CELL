p = "hq_graph.py"
s = open(p, encoding="utf-8", newline="").read()
s = s.replace("def band_points(walked, mt=None):", "def band_points(walked, mt=None, pose=None):")
s = s.replace('''        pad = BAND_BAYS * 360.0 / 60.0
        t0, t1 = min(ts) - pad, max(ts) + pad
        r = _level_r(sl)
        z0, h = sl["pos"][2], sl["size"][1]
        inward = sl["kind"] in ("cavea", "podium")
        for k in range(9):
            t = math.radians(t0 + (t1 - t0) * k / 8)
            x, y = AL.ell(t, r)
            for z in (z0, z0 + h):
                pts.append((x * KS, y * KS, z * KS))
    return pts''', '''        pad = BAND_BAYS * 360.0 / 60.0
        t0, t1 = min(ts) - pad, max(ts) + pad
        r = _level_r(sl)
        z0, h = sl["pos"][2], sl["size"][1]
        if pose is not None:
            # the band runs on to the frame edge: every point of the level's face in frame (the AD's left-centre tower stood two bays
            # beyond the options' +1 bay and still hid the colonnade)
            a0, a1 = next(L_ for L_ in AL._levels(CONCEPT) if L_["name"] == lv)["arc"]
            t0, t1 = min(a0, a1) - 12.0, max(a0, a1) + 12.0
            n_ = int((t1 - t0) / 3.0)
        else:
            n_ = 8
        for k in range(n_ + 1):
            t = math.radians(t0 + (t1 - t0) * k / n_)
            x, y = AL.ell(t, r)
            for z in (z0, z0 + h):
                p_ = (x * KS, y * KS, z * KS)
                if pose is not None:
                    q = pose.proj(p_, w=2560)
                    if q is None or not (0 <= q[0] <= 2560 and 0 <= q[1] <= 1440):
                        continue
                    if not (math.cos(t) * 0 + 1):
                        continue
                pts.append(p_)
    return pts''')
open(p, "w", encoding="utf-8", newline="").write(s)
p = "hq_run.py"
s = open(p, encoding="utf-8", newline="").read()
s = s.replace("band = G.band_points(walked, int(mt_))", "band = G.band_points(walked, int(mt_), pose) or G.band_points(walked, int(mt_))")
open(p, "w", encoding="utf-8", newline="").write(s)
