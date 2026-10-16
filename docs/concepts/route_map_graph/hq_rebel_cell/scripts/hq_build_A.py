"""Rebel Cell, option A (three stacked lanes in one side-view section): the Blender build (through hq_build.py).

The real district (rc_district) is cut along the street line `stack.cut` (no blocks south of it, no ground in front of
it: a dollhouse section); the first row of blocks behind the cut hosts the lanes: LANE BUILDINGS (their ground
floors = the street rooms, their roofs = the rooftop rooms; the windows follow the fist sequence like every block);
the EARTH under the street is cut open too: the service TUNNEL (the third lane) and its deeper detour level; the
SWITCH column at x_switch (roof / street / tunnel switches), the SERVICE SHAFT beside it up to DISPATCH (the palm
row's building: its server floor is the TARGET).
HQ_DISTRICT_ONLY=1 builds the whole district without the cut or the lanes (the red sequence from above).
"""
import math
import os

import rc_district


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, obox, oquad, tube, box = K.A, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("district",)}
    RED, SOD = pal("red_hot"), pal("sodium")
    ST = CP["stack"]
    CUT = ST["cut"]
    only = bool(os.environ.get("HQ_DISTRICT_ONLY"))
    RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
    cols = sorted({round(r["o"][0], 1) for i, r in G.ROOM.items() if i not in ("start",)})

    def free(x, y):
        if only:
            return False
        if CUT < y < CUT + 16.0 and any(abs(x - c) < 13.0 for c in cols + [G.SHAFT_X]):
            return True
        return False
    accs, SEQ, PULSE, cat = rc_district.build(K, keep_free=free, cut_y=None if only else CUT)
    hooks["accs"].update(accs)
    DIST = accs["district"]
    if only:
        hooks["no_room_light"] = tuple(G.NODES)
    else:
        # ---------------------------------------------------------------- the lane buildings (the first row, opened)
        EARTH = (0.11, 0.075, 0.055)
        dzt = ST["dispatch_z"]
        builds = {}
        for i, r in G.ROOM.items():
            if i == "start":
                continue
            x, y, z = r["o"]
            b = builds.setdefault(round(x, 1), dict(x=x, roof=0.0, street=False, srv=False))
            if G.LANE.get(i) == "L":
                b["roof"] = max(b["roof"], z)
            if G.LANE.get(i) == "C":
                b["street"] = True
            if i == "srv":
                b["srv"] = True
                b["roof"] = max(b["roof"], dzt + 26.0)
        for key, b in builds.items():
            x = b["x"]
            roof = b["roof"] or 30.0
            y0, y1 = CUT + 0.6, CUT + 18.0
            c = cat(x, CUT + 9.0)
            # ground floor: a frame round the street room (or solid), then the floors up to the roof (district windows)
            if b["street"]:
                box(DIST, x - 10.0, y0, 0.0, x - RW / 2 - 0.4, y1, 9.6, (0.08, 0.075, 0.08), k=float(c))
                box(DIST, x + RW / 2 + 0.4, y0, 0.0, x + 10.0, y1, 9.6, (0.08, 0.075, 0.08), k=float(c))
                box(DIST, x - RW / 2 - 0.4, CUT + RD + 0.5, 0.0, x + RW / 2 + 0.4, y1, 9.6, (0.08, 0.075, 0.08), k=float(c))
                zb = 9.6
            else:
                zb = 0.0
            if b["srv"]:
                box(DIST, x - 12.0, y0, zb, x + 12.0, y1, dzt - 0.4, (0.08, 0.075, 0.08), k=float(c))
                box(DIST, x - 12.0, y0, dzt - 0.4, x - 9.4, y1, dzt + RH + 2.0, (0.08, 0.075, 0.08), k=float(c))
                box(DIST, x + 9.4, y0, dzt - 0.4, x + 12.0, y1, dzt + RH + 2.0, (0.08, 0.075, 0.08), k=float(c))
                box(DIST, x - 12.0, y0, dzt + RH + 2.0, x + 12.0, y1, roof, (0.08, 0.075, 0.08), k=float(c))
            elif roof > zb + 1.0:
                box(DIST, x - 10.0, y0, zb, x + 10.0, y1, roof, (0.08, 0.075, 0.08), k=float(c))
        # the detour rooftop structures: raised huts on a steel frame above the lane-2 roof
        for i in ("L2a", "L2b"):
            r = G.ROOM[i]
            x, y, z = r["o"]
            for dx in (-6.5, 6.5):
                for dy in (1.0, RD - 1.0):
                    tube(A["metal"], (x + dx, y + dy, ST["roofs"]["2"]), (x + dx, y + dy, z - 0.3), 0.3, (0.2, 0.2, 0.2), n=5)
            box(A["rough"], x - RW / 2 - 0.6, y, z - 0.6, x + RW / 2 + 0.6, y + RD + 0.6, z, (0.15, 0.14, 0.13))
        # ---------------------------------------------------------------- the earth, the tunnel, the deeper level
        ze = ST["earth"]
        ztb, ztt = G.ZL["R"] - 3.0, G.ZL["R"] + RH + 4.0           # the tunnel cavity
        zdb, zdt = G.ZL["R"] - 12.0 - 3.0, ztb                      # the detour cavity (deeper)
        xa, xb = G.X0 - 45.0, G.SHAFT_X + 4.0
        dxa, dxb = G.XS["2a"] - 12.0, G.XS["2b"] + 12.0
        yb = CUT + 16.0
        E = A["rough"]
        box(E, -320.0, yb, ze, 120.0, CUT + 160.0, -0.06, EARTH)                # behind the cavities
        box(E, -320.0, CUT, ztt, 120.0, yb, -0.06, EARTH)                       # above the tunnel (the street's bed)
        box(E, -320.0, CUT, ztb, xa, yb, ztt, EARTH)
        box(E, xb, CUT, ztb, 120.0, yb, ztt, EARTH)
        box(E, -320.0, CUT, ze, dxa, yb, ztb, EARTH)
        box(E, dxb, CUT, ze, 120.0, yb, ztb, EARTH)
        box(E, dxa, CUT, ze, dxb, yb, zdb, EARTH)
        for (x0_, x1_, z0_, z1_) in ((xa, xb, ztb, ztt), (dxa, dxb, zdb, zdt)):  # cavity linings, the tunnel floor
            box(A["metal"], x0_, CUT, z0_ - 0.3, x1_, yb, z0_, (0.2, 0.2, 0.21))
            box(A["civic"], x0_, yb - 0.4, z0_, x1_, yb, z1_, (0.16, 0.16, 0.17))
            x = x0_ + 6.0
            while x < x1_ - 4.0:                                               # tunnel lights + pipes
                box(A["trim"], x - 1.5, CUT + 2.0, z1_ - 0.5, x + 1.5, CUT + 6.0, z1_ - 0.3, (0.75, 0.9, 1.0), 2.0)
                x += 18.0
            tube(A["metal"], (x0_, yb - 1.2, z1_ - 2.0), (x1_, yb - 1.2, z1_ - 2.0), 0.6, (0.25, 0.2, 0.15), n=6)
            tube(A["metal"], (x0_, yb - 2.6, z1_ - 3.4), (x1_, yb - 2.6, z1_ - 3.4), 0.4, (0.15, 0.25, 0.2), n=6)
        for s_ in (-0.7, 0.7):                                                  # a service rail in the tunnel
            box(A["metal"], xa, CUT + 7.0 + s_, ztb, xb, CUT + 7.2 + s_, ztb + 0.3, (0.4, 0.38, 0.35))
        # the section edge of the street (a lit kerb line) + the street's red cable lane
        box(A["trim"], -320.0, CUT - 0.05, -0.3, 120.0, CUT + 0.05, 0.0, (0.9, 0.85, 0.8), 0.6)
        for s_ in (3.0, 5.0):
            box(A["trim"], -260.0, CUT + s_, 0.02, ST["dispatch_x"] - 12.0, CUT + s_ + 0.2, 0.12, RED, 0.6)
        # the service shaft: a lit cage up the switch column to DISPATCH's floor and down into the tunnel
        sx = G.SHAFT_X
        box(E, sx - 3.0, CUT, ztt, sx + 3.0, CUT + 0.01, -0.06, EARTH)
        for dx in (-2.5, 2.5):
            tube(A["metal"], (sx + dx, CUT - 1.0, ztb), (sx + dx, CUT - 1.0, ST["roofs"]["K"] + RH), 0.15, (0.4, 0.38, 0.35), n=4)
        z = ztb
        while z < ST["roofs"]["K"] + RH:
            box(A["small"], sx - 2.5, CUT - 1.1, z, sx + 2.5, CUT - 0.9, z + 0.15, RED, 2.0)
            z += 4.0
        # rooms: rooftop / street / tunnel / switches / DISPATCH
        emv = K.ROOM_EMIT.setdefault("srv", K.Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
        for i, r in G.ROOM.items():
            if i == "start":
                continue
            if i == "srv":
                x, y, z = r["o"]
                K.room_shell("srv", dict(r, n=(0.0, -1.0)), kind="router")
                for k in range(6):
                    box(emv, x - 7.0 + k * 2.6, y + RD - 0.4, z + 1.0, x - 5.6 + k * 2.6, y + RD - 0.2, z + 7.0, (1.0, 0.12, 0.08), 5.0)
                continue
            K.room_shell(i, r, kind="router" if G.KIND[i] == "switch" else None)
            o = r["o"]
            if G.LANE.get(i) == "L":
                obox(A["rough"], r, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.0, o[2] + RH, o[2] + RH + 0.6, (0.12, 0.12, 0.13))
            if G.KIND[i] == "switch":
                obox(A["metal"], r, -1.2, 1.2, -RD + 1.0, -RD + 2.4, o[2], o[2] + 4.5, (0.15, 0.15, 0.16))
                obox(A["trim"], r, -0.8, 0.8, -RD + 2.4, -RD + 2.5, o[2] + 2.5, o[2] + 4.0, RED, 4.0)
        sxy = G.ROOM["start"]["o"]
        box(A["rough"], sxy[0] - 4, sxy[1] + 1, 0, sxy[0] + 4, sxy[1] + 6, 4.0, (0.2, 0.2, 0.21))
        box(A["trim"], sxy[0] - 3.0, sxy[1] + 0.95, 1.4, sxy[0] - 2.0, sxy[1] + 1.0, 2.8, (0.55, 1.0, 0.0), 6.0)
        K.add_light("hack", "POINT", (sxy[0] - 2.5, sxy[1] - 1.0, 2.0), 160.0, (0.55, 1.0, 0.0), size=0.3, group="start")
        for (a, b_) in G.PATH:                                                  # the walkways on the section plane
            pth = G.edge_path(a, b_)
            for p, q in zip(pth, pth[1:]):
                p, q = Vector(p), Vector(q)
                d = q - p
                if math.hypot(d.x, d.y) < 0.3 and abs(d.z) > 0.5:
                    for s_ in (-0.5, 0.5):
                        tube(A["metal"], p + Vector((s_, 0.3, -1.6)), q + Vector((s_, 0.3, -0.6)), 0.08, (0.3, 0.28, 0.25), n=4)
                    continue
                K.seg_box(A["rough"], p + Vector((0, 0.6, -1.55)), q + Vector((0, 0.6, -1.55)), 1.6, 0.25, (0.16, 0.12, 0.09))
        # light: tunnel work lights (cold), sodium on the street, rooftop work lights, a soft key on the section face
        for x in range(int(xa) + 10, int(xb), 30):
            K.add_light("tun_%d" % x, "AREA", (x, CUT + 5.0, ztt - 1.0), 900.0, (0.75, 0.9, 1.0), aim=(x, CUT + 5.0, ztb),
                        size=8.0, size_y=4.0, group="corp")
        for x in range(int(xa) + 20, int(xb) + 40, 40):
            K.add_light("sod_%d" % x, "SPOT", (x, CUT - 4.0, 14.0), LH["sod_w"], SOD, aim=(x, CUT + 4.0, 0.0), size=0.6,
                        spot=90, blend=0.9, group="corp")
            K.add_light("roof_%d" % x, "SPOT", (x, CUT - 8.0, 60.0), LH["sod_w"] * 0.8, (0.85, 0.85, 1.0),
                        aim=(x, CUT + 6.0, 34.0), size=0.6, spot=60, blend=0.9, group="corp")
        K.add_light("section_key", "AREA", (-80.0, CUT - 160.0, 20.0), LH["key_w"] * 2.0, (0.8, 0.82, 0.95),
                    aim=(-80.0, CUT, 0.0), size=260.0, size_y=90.0, group="corp", shadow=False)
    RIMRX = bpy.data.collections.new("rim_rx")
    for k, (rx, c_) in enumerate(((-160.0, "neon_a"), (100.0, "neon_b"))):
        K.add_light("rim_%d" % k, "AREA", (rx, CUT + 300.0, 70.0), LH["rim_w"], pal(c_), aim=(rx * 0.5, CUT, 30.0),
                    size=160.0, size_y=80.0, group="corp", shadow=False, receivers=RIMRX)
    K.log("option A built", "district only" if only else "")

    def post_build(OBJ):
        for name, ob in OBJ.items():
            if ob is not None and any(c.name in ("compound", "rooms") for c in ob.users_collection):
                RIMRX.objects.link(ob)
    hooks["post_build"] = post_build

    def apply(fr, ctx):
        me = fr.get("mech") or {}
        SEQ.outputs[0].default_value = float(me.get("seq", 2.0))   # the netrun: the fist lit, not at full blaze
        PULSE.outputs[0].default_value = float(me.get("pulse", 0.0))
    hooks["apply"] = apply
    return hooks
