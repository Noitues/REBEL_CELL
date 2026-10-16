"""Rebel Cell, option C (the converging map): the Blender build (called through hq_build.py).

The district (rc_district: the fist in red windows, the sequence + pulse shader), the south street (the GHOST's lane,
open), DISPATCH: a plain building at the palm with a roof shack (the TARGET), the rooftop rooms and switches of the
west / east lanes, the street rooms, plank and cable bridges, sodium street light, a rim from the city behind.
"""
import math

import rc_district


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, obox, oquad, tube, box = K.A, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("district",)}
    RED, SOD = pal("red_hot"), pal("sodium")
    PX, PY = CP["palm"]
    SX, SY = CP["start"]

    def free(x, y):
        if abs(x) < 13.0 and SY - 20.0 < y < PY - 14.0:       # the south street (the alley lane)
            return True
        if abs(x - PX) < 12.0 and abs(y - PY - 4.0) < 12.0:   # the DISPATCH building (built below)
            return True
        if abs(x - SX) < 26.0 and SY - 24.0 < y < SY + 14.0:  # the drop square
            return True
        return False
    rooms = [tuple(r["o"]) for i, r in G.ROOM.items() if i not in ("start", "srv")]
    accs, SEQ, PULSE, _cat = rc_district.build(K, keep_free=free, low_near=rooms)
    hooks["accs"].update(accs)
    # DISPATCH: an ordinary building at the palm (no tower: round 34); the roof shack is the showdown room
    dz = CP["dispatch_z"]
    box(A["rough"], PX - 10, PY - 6, 0.0, PX + 10, PY + 14, dz, (0.08, 0.075, 0.08))
    emv = K.ROOM_EMIT.setdefault("srv", K.Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
    box(A["metal"], PX - 7, PY - 4, dz, PX + 7, PY + 8, dz + 8.0, (0.06, 0.06, 0.07))
    for k in range(5):
        box(emv, PX - 6 + k * 2.6, PY - 4.05, dz + 1.5, PX - 4.8 + k * 2.6, PY - 3.95, dz + 6.5, (1.0, 0.15, 0.1), 4.0)
    tube(A["metal"], (PX + 4, PY + 4, dz + 8), (PX + 4, PY + 4, dz + 20), 0.25, (0.1, 0.1, 0.1), n=5)
    box(A["small"], PX + 3.5, PY + 3.5, dz + 20, PX + 4.5, PY + 4.5, dz + 21, RED, 10.0)
    # rooms (rooftop huts on the roof lanes, street rooms on the south street), the kill switches
    for i, r in G.ROOM.items():
        if i in ("start", "srv"):
            continue
        K.room_shell(i, r, kind="router" if G.KIND[i] == "switch" else None)
        o = r["o"]
        if o[2] > 5.0:
            obox(A["rough"], r, -r["w"] / 2 - 1.0, r["w"] / 2 + 1.0, -r["d"] - 1.0, 0.0, o[2] + r["h"], o[2] + r["h"] + 0.6,
                 (0.12, 0.12, 0.13))
        if G.KIND[i] == "switch":                      # the switch: a red lever box in the room, a red beacon on top
            obox(A["metal"], r, -1.2, 1.2, -r["d"] + 1.0, -r["d"] + 2.4, o[2], o[2] + 4.5, (0.15, 0.15, 0.16))
            obox(A["trim"], r, -0.8, 0.8, -r["d"] + 2.4, -r["d"] + 2.5, o[2] + 2.5, o[2] + 4.0, RED, 4.0)
            box(A["small"], o[0] - 0.6, o[1] + 4.0, o[2] + r["h"] + 0.6, o[0] + 0.6, o[1] + 5.2, o[2] + r["h"] + 1.6, RED, 12.0)
    sx_, sy_ = CP["start"]
    box(A["rough"], sx_ - 4, sy_, 0, sx_ + 4, sy_ + 5, 4.0, (0.2, 0.2, 0.21))
    box(A["trim"], sx_ - 3.0, sy_ - 0.05, 1.4, sx_ - 2.0, sy_, 2.8, (0.55, 1.0, 0.0), 6.0)
    K.add_light("hack", "POINT", (sx_ - 2.5, sy_ - 1.0, 2.0), 160.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    for (a, b_) in G.PATH:                             # links: plank bridges, ladders, the street walk
        pth = G.edge_path(a, b_)
        for p, q in zip(pth, pth[1:]):
            p, q = Vector(p), Vector(q)
            d = q - p
            if math.hypot(d.x, d.y) < 0.3 and abs(d.z) > 0.5:
                for s_ in (-0.5, 0.5):
                    tube(A["metal"], p + Vector((s_, 0, -1.6)), q + Vector((s_, 0, -0.6)), 0.08, (0.3, 0.28, 0.25), n=4)
                continue
            K.seg_box(A["rough"], p + Vector((0, 0, -1.55)), q + Vector((0, 0, -1.55)), 1.8, 0.25, (0.16, 0.12, 0.09))
    for s_ in (-1.2, 1.2):                             # the red cable lane down the south street
        box(A["trim"], s_ - 0.1, SY, 0.02, s_ + 0.1, PY - 14.0, 0.12, RED, 0.8)
    for k in range(7):
        y = SY + 10 + k * 28.0
        K.add_light("sod_%d" % k, "SPOT", (0.0, y, 12.0), LH["sod_w"], SOD, aim=(0.0, y, 0.0), size=0.6, spot=90, blend=0.9,
                    group="corp")
    RIMRX = bpy.data.collections.new("rim_rx")
    for k, (rx, c_) in enumerate(((-140.0, "neon_a"), (140.0, "neon_b"))):
        K.add_light("rim_%d" % k, "AREA", (rx, PY + 260.0, 60.0), LH["rim_w"], pal(c_), aim=(0.0, PY, 40.0), size=140.0,
                    size_y=80.0, group="corp", shadow=False, receivers=RIMRX)
    K.add_light("dispatch_key", "SPOT", (PX, PY - 80.0, 30.0), LH["key_w"], (0.8, 0.85, 1.0), aim=(PX, PY, dz),
                size=1.5, spot=30, blend=0.5, group="corp")
    K.log("option C built")

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
