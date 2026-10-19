"""Street round 2: the rules as seeded generator passes over the one-city lots (port of the art-pass `r2_rules.py`; pure python, no files).

`layout_pass(seed, city, links, D)` changes heights; `plan_pass(seed, D, city, layout_log)` makes the dressing plan; `checks` holds the
plan-level rule tests (R-REP-1 / R-DET-2 ...). Differences from the art-pass file: no scratch folder, the street derivation `D`, the
lot data and the network arrive as arguments, and the passes return their products instead of writing them.

Layout passes (they change the one city, like the approved v3 layout rules; both looks read the same city):
  frontage.silhouette  every border-link frontage gets a seeded height rhythm (low / mid / tall classes, never the same
                       class 3 times running, neighbours >= height_step_min floors apart); route columns rise
                       route_sign_floors over their top room; on the netrun street, the frontage in front of the corp
                       landmark stays under sightline_floors so the landmark keeps its sightline from the OVERVIEW
  horizon.break        3-5 backdrop towers behind the street become spikes (>= spike_k x the median backdrop roof, their
                       roofs landing in spike_top of the OVERVIEW frame, >= 1/6 frame apart)
Plan passes (dressing; nothing in the layout):
  materials.mix        a facade kit per building (4 kits, district weights, no two adjacent frontage buildings alike)
  repetition.guard     no more than max_same_module_adjacent identical facade modules side by side (kit + window module)
  dressing.signs       hero sign per route column, shopfront + shop sign per frontage base, secondary signs, backdrop
                       signs, one megastructure; each sign with its LOD tiers
  streets.light        kerb lamp posts, fg lanes
  palette.districts    every sign / crown / bank glow coloured from its district's palette
  atmosphere.layers    plume sources, the bank-glow stops along the street
Every random draw comes from art_seed(stream, *content ids) (spec 3.5): adding or removing one object never moves another.
"""
import copy
import math
from typing import Any, Dict, List, Sequence

from . import facade as FC
from . import onecity as OC
from .checks import _face_frame, _pt, checks  # noqa: F401
from .layout_rules import _border_legs, _frontage_rows, _tops, horizon_pick, layout_pass  # noqa: F401
from .config import ADS, R, SUBS
from .config import WORDS as CFG_WORDS
from .streams import art_seed, rng


# ---------------------------------------------------------------- PLAN
def plan_pass(seed, D, city, layout_log, merged=None, terr=None):
    """The dressing plan of art seed `seed` on the street derivation `D`, the post-layout city (raw lot records) and the layout
    pass log. The street, the rooms and the cameras are `D`: art passes never move the netrun street.
    The game city is already in BU: `adapter` passes its buildings as `merged` (BU records, see `onecity.merged_buildings`) and the
    district per uid as `terr`, and `city` is then unused."""
    ov, dec = D["overview"], D["decision"]
    LAY = city
    if terr is None:
        terr = {"%d_%d" % (b["ci"], b["key"]): b["terr"] for b in LAY["buildings"]}
    B = merged if merged is not None else OC.merged_buildings(LAY["buildings"])
    bk = {b["uid"]: b for b in B}
    nrm, axis = D["nrm"], (0 if abs(D["a"][1] - D["c"][1]) < 1e-6 else 1)
    sa, sc = D["a"], D["c"]
    line = sa[1 - axis]
    route = list(D["column_uids"])
    rset = set(route)
    lylog = layout_log
    spikes = [s["key"] for s in lylog["spikes"]]
    mid = ((sa[0] + sc[0]) / 2, (sa[1] + sc[1]) / 2)
    u0_s, u1_s = sorted((sa[axis], sc[axis]))
    W_, H_ = OC.W_, OC.H_

    def far_of(b):
        cx, cy = (b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2
        return (cy - line) * nrm[1] if axis == 0 else (cx - line) * nrm[0]

    def sx_of(p, c=ov):
        q = OC.proj(c, p)
        return q[0] / W_, q[1] / H_

    # the frontage row the camera sees (the far side), in order along the street
    front = OC.frontage(B, sa, sc, D["side"])
    fkeys = [b["uid"] for b in front]
    # ------------------------------------------------ palette.districts: a district per building (terr; neutral = "")
    PD = R["palette.districts"]

    def dist_of(key):
        t = terr.get(key, "")
        return t if t in PD["sign_pal"] else ""

    # ------------------------------------------------ materials.mix + repetition.guard
    M = R["materials.mix"]
    kits = {}
    for b in sorted(B, key=lambda b: b["uid"]):
        cx, cy = (b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2
        if math.hypot(cx - mid[0], cy - mid[1]) > M["kit_radius"]:
            continue
        w = M["district_weights"].get(dist_of(b["uid"]), M["district_weights"][""])
        kits[b["uid"]] = rng(seed, "kit", b["uid"]).choices(M["kits"], weights=w)[0]
    # the frontage (both sides) never repeats a kit between neighbours
    for side in (1, -1):
        row = OC.frontage(B, sa, sc, side)
        prev = None
        for b in row:
            k = kits.get(b["uid"], "concrete_band")
            if k == prev:
                opts = [x for x in M["kits"] if x != prev]
                k = opts[rng(seed, "kit_fix", b["uid"]).randrange(len(opts))]
            kits[b["uid"]] = k
            prev = k
    # stacked parts take their base's kit
    for b in B:
        for p in b.get("parts_uid", []):
            if b["uid"] in kits:
                kits[p] = kits[b["uid"]]
    # window module per building (repetition guard: a module index; neighbours may share at most max_same_module_adjacent)
    modules = {}
    prevm, runm = None, 0
    for b in front:
        m = rng(seed, "module", b["uid"]).randrange(3)
        if m == prevm and runm >= R["repetition.guard"]["max_same_module_adjacent"]:
            m = (m + 1) % 3
        runm = runm + 1 if m == prevm else 1
        prevm = m
        modules[b["uid"]] = m
    # ------------------------------------------------ crowns (frontage.silhouette)
    P = R["frontage.silhouette"]
    crowns = []
    for side in (1, -1):
        row = OC.frontage(B, sa, sc, side)
        if not row:
            continue
        need = int(math.ceil(P["crown_share"] * len(row)))
        sc_ = sorted(row, key=lambda b: (rng(seed, "crown_pick", b["uid"]).random(), b["uid"]))
        chosen = {b["uid"] for b in sc_[:need]}
        for b in row:
            r_ = rng(seed, "crown", b["uid"])
            if b["uid"] in chosen or r_.random() < 0.15:
                kind = P["crown_kinds"][r_.randrange(len(P["crown_kinds"]))]
                if b["x1"] - b["x0"] < 3.6 and b["y1"] - b["y0"] < 3.6 and kind == "setback":
                    kind = "spire"
                pal = PD["sign_pal"][dist_of(b["uid"])]
                crowns.append(dict(key=b["uid"], kind=kind, side=side, top=b["h"], q=[list(p) for p in b["q"]],
                                   box=[b["x0"], b["y0"], b["x1"], b["y1"]], col=list(pal[r_.randrange(len(pal))]),
                                   floors=r_.randint(2, 4), h=r_.uniform(4.0, 9.0)))
    # ------------------------------------------------ lit silhouette trims (frontage.silhouette: roof rim, bands, corners)
    trims = {}
    for side in (1, -1):
        for b in OC.frontage(B, sa, sc, side):
            r_ = rng(seed, "trim", b["uid"])
            pal = PD["sign_pal"][dist_of(b["uid"])]
            trims[b["uid"]] = dict(col=list(pal[r_.randrange(len(pal))]), col2=list(pal[r_.randrange(len(pal))]),
                                   band_every=r_.randint(*P["band_every"]), corner=r_.random() < P["p_corner"],
                                   roof=bool(P["roof_rim"]), gap_p=P["band_gap_p"])
    # ------------------------------------------------ dressing.signs
    S = R["dressing.signs"]
    signs = []
    rooms_by_b = {}
    for i, r in D["rooms"].items():
        rooms_by_b.setdefault(r["bld_uid"], []).append((i, r))

    def room_hit(key, u0, u1, z0, z1):
        for i, r in rooms_by_b.get(key, []):
            us = [p[axis] for p in r["front"]]
            if u0 < max(us) + 0.1 and u1 > min(us) - 0.1 and z0 < r["front"][2][2] + 0.1 and z1 > r["front"][0][2] - 0.1:
                return i
        return None

    def add(kind, b, u0, u1, z0, z1, col, tex, emit, text_frac, words=None, **kw):
        bu0, bu1, face, out = _face_frame(b, nrm, axis)
        u0, u1 = max(u0, bu0 + 0.05), min(u1, bu1 - 0.05)
        if u1 - u0 < 0.4:
            return None
        d = face + out * S["sign_off"]
        c3 = _pt(axis, (u0 + u1) / 2, d, (z0 + z1) / 2)
        sid = "%s_%s_%d" % (kind, b["uid"], len(signs))
        sg = dict(id=sid, kind=kind, key=b["uid"], axis=axis, face=face, out=out, d=d, u0=u0, u1=u1, z0=z0, z1=z1,
                  col=list(col), tex=tex, emit=emit, text_frac=text_frac, centre=list(c3), words=words or [],
                  wall=room_hit(b["uid"], u0, u1, z0, z1), district=dist_of(b["uid"]))
        sg.update(kw)
        signs.append(sg)
        return sg

    WORDS = CFG_WORDS
    fl = OC.FLOOR_BU
    room_top = {}
    for r in D["rooms"].values():
        room_top[r["bld_uid"]] = max(room_top.get(r["bld_uid"], 0.0), r["front"][2][2])
    hero_i = 0
    for b in front:
        key = b["uid"]
        r_ = rng(seed, "signs", key)
        dis = dist_of(key)
        pal = PD["sign_pal"][dis]
        words = WORDS[dis]
        bu0, bu1, face, out = _face_frame(b, nrm, axis)
        wdt = bu1 - bu0
        # shopfront strip on every frontage base + a shop sign over it (p_shop_sign)
        sc_col = pal[r_.randrange(len(pal))]
        add("shopfront", b, bu0 + 0.35, bu1 - 0.35, 0.15, 1.45, sc_col,
            dict(style="shop", word=words[r_.randrange(len(words))], seed=art_seed(seed, "tex", key, "shop")), S["shop_emit"], 0.0)
        if r_.random() < S["p_shop_sign"]:
            sw = min(wdt * 0.8, r_.uniform(2.6, 4.0))
            u0 = bu0 + r_.uniform(0.3, max(0.31, wdt - sw - 0.3))
            wd = words[r_.randrange(len(words))]
            add("shop_sign", b, u0, u0 + sw, 1.6, 1.6 + sw / r_.uniform(2.0, 2.6), pal[r_.randrange(len(pal))],
                dict(style="box", word=wd, sub=SUBS[r_.randrange(len(SUBS))], seed=art_seed(seed, "tex", key, "shopsign")),
                S["shop_emit"], 0.5, words=[wd])
        top = b["h"]
        if key in rset:
            # hero sign over the rooms, in the district pair (hero_i alternates) - blade (vertical) or wall (board)
            z0 = room_top.get(key, 6 * fl) + 0.45
            z1 = top - 0.7
            kind = S["hero_kinds"][r_.randrange(2)] if (z1 - z0) > 3.2 and wdt > 4.2 else "blade"
            hcol = pal[hero_i % 2] if dis != "" else [(1.0, 0.16, 0.6), (0.16, 0.8, 1.0)][hero_i % 2]
            wd = words[r_.randrange(len(words))]
            if kind == "blade":
                bw = min(2.6, max(1.6, wdt * 0.3))
                bh = min(z1 - z0, 0.46 * bw * (len(wd.replace(" ", "")) + 1.5))
                left = r_.random() < 0.5
                u0 = bu0 + 0.2 if left else bu1 - 0.2 - bw
                add("hero_blade", b, u0, u0 + bw, z1 - bh, z1, hcol, dict(style="blade", word=wd, sub=SUBS[r_.randrange(len(SUBS))],
                    seed=art_seed(seed, "tex", key, "hero")), S["hero_emit"], 0.38, words=[wd],
                    hero=True)
            else:
                bw = min(wdt - 0.8, r_.uniform(4.0, 6.5))
                bh = min(z1 - z0, bw / r_.uniform(1.7, 2.3))
                u0 = bu0 + (wdt - bw) / 2
                zc = z0 + r_.uniform(0.0, max(0.0, z1 - z0 - bh))
                ad = None
                if r_.random() < 0.5:
                    ad = ADS["hero"][dis][r_.randrange(3)]
                add("hero_wall", b, u0, u0 + bw, zc, zc + bh, hcol, dict(style="ad" if ad else "wall", ad=ad, word=wd,
                    sub=SUBS[r_.randrange(len(SUBS))], seed=art_seed(seed, "tex", key, "hero")), S["hero_emit"], 0.30, words=[wd],
                    hero=True)
            hero_i += 1
        # secondary sign (p_secondary): a small blade / box / holo, off the rooms
        if r_.random() < S["p_secondary"]:
            kind = ("sec_blade", "sec_box", "sec_holo")[r_.randrange(3)]
            zlo = room_top.get(key, 2.2) + 0.3 if key in rset else 2.4
            if top - 0.8 - zlo > 2.0:
                wd = words[r_.randrange(len(words))]
                if kind == "sec_blade":
                    bw = 0.8
                    bh = min(top - 0.8 - zlo, r_.uniform(2.6, 4.4))
                    u0 = bu0 + 0.15 if r_.random() < 0.5 else bu1 - 0.95
                    tx = dict(style="blade", word=wd[:6], sub="", seed=art_seed(seed, "tex", key, "sec"))
                    tf = 0.38
                else:
                    bw = min(wdt * 0.75, r_.uniform(2.6, 4.2))
                    bh = bw / r_.uniform(1.5, 2.2)
                    u0 = bu0 + r_.uniform(0.2, max(0.21, wdt - bw - 0.2))
                    tx = dict(style="box" if kind == "sec_box" else "holo", word=wd, sub=SUBS[r_.randrange(len(SUBS))],
                              seed=art_seed(seed, "tex", key, "sec"))
                    tf = 0.42 if kind == "sec_box" else 0.26
                z0 = zlo + r_.uniform(0, max(0.0, top - 0.8 - zlo - bh))
                s_ = add(kind, b, u0, u0 + bw, z0, z0 + bh, pal[r_.randrange(len(pal))], tx, S["sec_emit"], tf, words=[wd])
                if s_ and s_["wall"]:
                    signs.remove(s_)
    # backdrop signs: a tall vertical sign high on visible backdrop towers (the spikes first)
    for key in spikes:
        b = bk.get(key)
        if b is None:
            continue
        r_ = rng(seed, "backdrop_sign", key)
        if r_.random() > S["backdrop_sign_p"] and key != spikes[0]:
            continue
        dis = dist_of(key)
        pal = PD["sign_pal"][dis]
        wd = CFG_WORDS[dis][r_.randrange(3)]
        bu0, bu1, face, out = _face_frame(b, nrm, axis)
        bw = min(4.5, (bu1 - bu0) * 0.5)
        bh = min(b["h"] * 0.4, 0.46 * bw * (len(wd.replace(" ", "")) + 1.5))
        z1 = b["h"] - r_.uniform(1.5, 4.0)
        u0 = bu0 + 0.3 if r_.random() < 0.5 else bu1 - 0.3 - bw
        add("backdrop_blade", b, u0, u0 + bw, z1 - bh, z1, pal[r_.randrange(len(pal))],
            dict(style="blade", word=wd, sub="", seed=art_seed(seed, "tex", key, "bd")), S["backdrop_emit"], 0.36, words=[wd])
    # megastructure: on the tallest spike inside the central 2/3 of the OVERVIEW, off the DECISION frame
    mega = None
    cands = []
    front_top = max(b["h"] for b in front)

    def mega_size(cx, cy, h):
        return 150.0 / W_ * math.dist(ov["persp"]["loc"], (cx, cy, h)) * 36.0 / ov["persp"]["lens"]
    for b in sorted(B, key=lambda b: b["uid"]):
        if b["uid"] in rset or b["z0"] > 0.05 or not (24.0 < far_of(b) < 170.0) or b["h"] < front_top * 0.8:
            continue
        cx, cy = (b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2
        x, y = sx_of((cx, cy, b["h"]))
        xd, yd = sx_of((cx, cy, b["h"]), dec)
        in_dec = 0.0 < xd < 1.0 and 0.0 < yd < 1.0
        sz = mega_size(cx, cy, b["h"])
        ytop = sx_of((cx, cy, b["h"] + 1.6 + sz * 0.75))[1]          # the tallest kind (globe on its mast)
        if 1 / 6 < x < 5 / 6 and not in_dec and ytop > S["mega_headroom"] and y < 0.45:
            cands.append((b["h"] + (40.0 if b["uid"] in spikes else 0.0), b["uid"], b, x, y))
    if cands:
        cands.sort(key=lambda c_: (-c_[0], c_[1]))
        h, key, b, x, y = cands[0]
        r_ = rng(seed, "mega", key)
        kind = S["mega_kinds"][r_.randrange(len(S["mega_kinds"]))]
        cx, cy = (b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2
        dis = dist_of(key)
        col = [(0.35, 0.9, 1.0), (1.0, 0.25, 0.65), (1.0, 0.65, 0.2)][r_.randrange(3)]
        # size: the megastructure reads at about 150 px wide in the OVERVIEW
        h = b["h"]
        size = mega_size(cx, cy, h)
        mega = dict(kind=kind, key=key, pos=[cx, cy, h], size=size, col=list(col), screen=[x, y], district=dis,
                    tex=dict(style="ad", ad=ADS["mega"][r_.randrange(len(ADS["mega"]))], word="", sub="",
                             seed=art_seed(seed, "tex", key, "mega")), emit=S["mega_emit"])
    # roof boards (dressing.signs): every sign_frame crown on the camera row carries a lit board, and backdrop roofs over
    # 14 BU in the OVERVIEW carry one with p_roof_board. Boards stand on legs at the roof's street edge, facing the street.
    def roof_board(b, kind, w_, h_, st, z_lift=0.9):
        r_ = rng(seed, "roof_board", b["uid"])
        bu0, bu1, face, out = _face_frame(b, nrm, axis)
        dis = dist_of(b["uid"])
        pal = PD["sign_pal"][dis]
        uc = (bu0 + bu1) / 2
        d = face - out * 0.4
        z0 = b["h"] + z_lift
        wd = CFG_WORDS[dis][r_.randrange(len(CFG_WORDS[dis]))]
        ad = ADS["board"][r_.randrange(len(ADS["board"]))] if st == "ad" else None
        sid = "%s_%s_%d" % (kind, b["uid"], len(signs))
        signs.append(dict(id=sid, kind=kind, key=b["uid"], axis=axis, face=d, out=out, d=d, u0=uc - w_ / 2, u1=uc + w_ / 2,
                          z0=z0, z1=z0 + h_, col=list(pal[r_.randrange(len(pal))]),
                          tex=dict(style=st, ad=ad, word=wd, sub=SUBS[r_.randrange(len(SUBS))], seed=art_seed(seed, "tex", b["uid"], kind)),
                          emit=S["sec_emit"], text_frac=0.3 if st != "ad" else 0.25, centre=list(_pt(axis, uc, d, z0 + h_ / 2)),
                          words=[wd] if st != "ad" else [], wall=None, district=dis, roof=True, legs=z_lift))
    for c_ in crowns:
        if c_["kind"] == "sign_frame" and c_["side"] == D["side"]:
            b = bk[c_["key"]]
            w_ = min(b["x1"] - b["x0"] if axis == 0 else b["y1"] - b["y0"], 7.0) * 0.85
            roof_board(b, "crown_board", w_, w_ * 0.42, ("wall", "ad", "holo")[rng(seed, "crown_board", b["uid"]).randrange(3)])
    for b in sorted(B, key=lambda b: b["uid"]):
        if b["uid"] in rset or b["uid"] in spikes or (mega and b["uid"] == mega["key"]) or b["z0"] > 0.05 or b["h"] < 14.0:
            continue
        if not (12.0 < far_of(b) < 170.0) or rng(seed, "p_roof_board", b["uid"]).random() > S["p_roof_board"]:
            continue
        x, y = sx_of(((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2, b["h"]))
        if not (0.02 < x < 0.98 and 0.04 < y < 0.8):
            continue
        wv = min(b["x1"] - b["x0"] if axis == 0 else b["y1"] - b["y0"], 7.5) * 0.8
        if wv < 2.5:
            continue
        roof_board(b, "roof_board", wv, wv * 0.6, ("holo", "ad", "wall")[rng(seed, "roof_board_kind", b["uid"]).randrange(3)])
    # ------------------------------------------------ repetition.guard (rhythm) + props.facade
    RG, PF = R["repetition.guard"], R["props.facade"]
    rhythm = {}
    for b in sorted(B, key=lambda b: b["uid"]):
        uid = b["uid"]
        if uid not in kits:
            continue
        bu0_, bu1_, _f, _o = _face_frame(b, nrm, axis)
        rhythm[uid] = FC.make_rhythm(rng(seed, "rhythm", uid), kits[uid], bu1_ - bu0_, b["h"], RG, PD["sign_pal"][dist_of(uid)],
                                     rigid_top=room_top.get(uid))
    for b in B:                                   # stacked parts follow their base's rhythm
        for pu in b.get("parts_uid", []):
            if b["uid"] in rhythm and pu != b["uid"]:
                rhythm[pu] = rhythm[b["uid"]]
    props = []
    prow = list(front) + [b for b in sorted(B, key=lambda b: b["uid"]) if b["uid"] not in set(fkeys) and b["z0"] <= 0.05 and b["uid"] in kits
                          and 0.5 < far_of(b) < 6.5 + PF["second_row_band"] and u0_s - 20 < ((b["x0"] + b["x1"]) / 2 if axis == 0 else (b["y0"] + b["y1"]) / 2) < u1_s + 20]
    for b in prow:
        uid = b["uid"]
        if uid not in rhythm:
            continue
        ff = _face_frame(b, nrm, axis)
        rh = rhythm[uid]
        fz = FC.floor_bounds(rh, 0.0, b["h"])
        rects = [[s_["u0"], s_["z0"], s_["u1"], s_["z1"]] for s_ in signs if s_["key"] == uid]
        rects.append([ff[0], 0.0, ff[1], 1.9])                                   # the shopfront zone
        for r_ in D["rooms"].values():
            if r_["bld_uid"] == uid:
                us_ = [q[axis] for q in r_["front"]]
                rects.append([min(us_) - 0.15, r_["front"][0][2], max(us_) + 0.15, r_["front"][2][2]])
        props += FC.make_props(rng(seed, "facade_props", uid), uid, b, ff, axis, line, rh, PD["sign_pal"][dist_of(uid)], D["rooms"], rects,
                               PF, fz, room_top.get(uid), None)
    # ------------------------------------------------ streets.light: kerb lamp posts, fg lanes
    L_ = R["streets.light"]
    u0s, u1s = sorted((sa[axis], sc[axis]))
    lamps = []
    lamps_dropped = 0
    k = 0
    u = u0s - 30.0
    while u <= u1s + 30.0:
        for side in (-1, 1):
            r_ = rng(seed, "lamp", round(u, 1), side)
            pos = _pt(axis, u + r_.uniform(-L_["lamp_jit"], L_["lamp_jit"]), line + side * L_["kerb_off"] * (nrm[1] if axis == 0 else nrm[0]), 0.0)
            warm = (k % 3) != 0
            ok_ = None
            for dsh in (0.0, 0.8, -0.8, 1.6, -1.6, PF["lamp_shift_max"], -PF["lamp_shift_max"]):
                uu_ = pos[axis] + dsh
                if not FC.prop_hits_opening(dict(u0=uu_ - 0.15, u1=uu_ + 0.15, z0=0.0, z1=L_["lamp_post_h"], face=pos[1 - axis], out=0.0, depth=0.0),
                                            D["rooms"], axis, line, PF["opening_margin"]):
                    ok_ = uu_
                    break
            if ok_ is None:
                lamps_dropped += 1
                k += 1
                continue
            pos = _pt(axis, ok_, pos[1 - axis], 0.0)
            lamps.append(dict(pos=list(pos), side=side, col=[1.0, 0.72, 0.42] if warm else [0.55, 0.85, 1.0]))
            k += 1
        u += L_["lamp_step"]
    # ------------------------------------------------ atmosphere.layers: plumes + bank glow stops along the street
    A = R["atmosphere.layers"]
    plume_src = []
    for c_ in crowns:
        if c_["kind"] in ("roof_box", "setback") and c_["side"] == D["side"]:
            b = bk.get(c_["key"])
            if b:
                plume_src.append(((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2, b["h"], c_["key"]))
    for key in spikes:
        b = bk.get(key)
        if b and (mega is None or key != mega["key"]):
            plume_src.append(((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2, b["h"], key))
    plume_src.sort(key=lambda p: (rng(seed, "plume", p[3]).random(), p[3]))
    plumes = []
    for x, y, z, key in plume_src[:A["plumes"]]:
        r_ = rng(seed, "plume_size", key)
        plumes.append(dict(pos=[x, y, z], h=r_.uniform(*A["plume_h"]), r=r_.uniform(*A["plume_r"]), key=key))
    stops = []
    for k in range(0, 13):
        uu = u0s - 150 + k * (u1s - u0s + 300) / 12.0
        cnt = {}
        for b in B:
            cu = (b["x0"] + b["x1"]) / 2 if axis == 0 else (b["y0"] + b["y1"]) / 2
            if abs(cu - uu) < 18 and 10 < far_of(b) < 140:
                d_ = dist_of(b["uid"])
                cnt[d_] = cnt.get(d_, 0) + 1
        dsel = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if cnt else ""
        col = PD["hues"][dsel] if dsel else [(1.0, 0.16, 0.6), (0.16, 0.8, 1.0)][k % 2]
        stops.append(dict(u=uu, district=dsel, col=list(col)))
    near = []                        # streets.light section_spill: the cut near-side frontage keeps its light
    for b in OC.frontage(B, sa, sc, -D["side"]):
        bu0, bu1, face, out = _face_frame(b, [-nrm[0], -nrm[1]], axis)
        near.append(dict(uid=b["uid"], u0=bu0, u1=bu1, face=face, out=out, top=b["h"], col=trims[b["uid"]]["col"]))
    faces = []
    for b in front:
        bu0, bu1, face, out = _face_frame(b, nrm, axis)
        faces.append(dict(uid=b["uid"], u0=bu0, u1=bu1, face=face, out=out, top=b["h"], col=trims[b["uid"]]["col"]))
    # the fog underlight ramp: the AAA pair and the districts in view whose hue is not the ambient violet (the cap)
    ul = [list(PD["hues"][d_]) for d_ in sorted({s_["district"] for s_ in stops if s_["district"]}) if d_ not in ("halcyon", "orbital")]
    plan = dict(seed=seed, axis=axis, nrm=nrm, line=line, route=route, front=fkeys, front_faces=faces, near_faces=near, trims=trims, rhythm=rhythm, props=props, lamps_dropped=lamps_dropped,
                underlight=ul + [[1.0, 0.16, 0.6]], kits={str(k): v for k, v in kits.items()},
                modules={str(k): v for k, v in modules.items()}, crowns=crowns, signs=signs, mega=mega, lamps=lamps,
                plumes=plumes, bank_stops=stops, spikes=spikes, fg_lanes=list(R["foreground.street"]["fg_lanes"]),
                lod=R["lod.signs"], districts_in_view=sorted({dist_of(k) for k in fkeys}))
    plan["checks"] = checks(seed, plan, D, OC, B, bk)
    return plan
