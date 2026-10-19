"""Street r2 plan-level rule checks (R-REP-1, R-DET-2 ...) and the street-face frame helpers."""
from . import facade as FC
from . import onecity as OC
from .config import R


def _face_frame(b, nrm, axis):
    """(u0, u1, face, out) of a building's street face: out = the direction from the face toward the street."""
    if axis == 0:
        u0, u1 = b["x0"], b["x1"]
        face = b["y0"] if nrm[1] > 0 else b["y1"]
        out = -1.0 if nrm[1] > 0 else 1.0
    else:
        u0, u1 = b["y0"], b["y1"]
        face = b["x0"] if nrm[0] > 0 else b["x1"]
        out = -1.0 if nrm[0] > 0 else 1.0
    return u0, u1, face, out


def _pt(axis, u, d, z):
    return (u, d, z) if axis == 0 else (d, u, z)


# ---------------------------------------------------------------- plan-level rule checks (image checks: r2_checks.py)
def checks(seed, plan, D, OC, B, bk):
    """The plan-level rule tests (R-SIL, materials, R-REP-1, R-DET-2, props, horizon); adds `cap_px_ov` to the legible signs."""
    out = {}
    ov = D["overview"]
    # frontage.silhouette: steps, equal tops, crown share (the camera's row)
    fr = [bk[k] for k in plan["front"]]
    fl = OC.FLOOR_BU
    steps = [abs(int(a["h"] / fl) - int(b["h"] / fl)) for a, b in zip(fr, fr[1:])]
    eq = 0
    run = 0
    for s in steps:
        run = run + 1 if s <= 1 else 0
        eq = max(eq, run + 1 if run else 0)
    ncrown = sum(1 for c in plan["crowns"] if c["key"] in plan["front"])
    out["frontage.silhouette"] = dict(floors=[int(b["h"] / fl) for b in fr], min_step=min(steps) if steps else None,
                                      max_equal_tops=eq, crown_share=round(ncrown / max(1, len(fr)), 2),
                                      ok=(min(steps) >= R["frontage.silhouette"]["height_step_min"] if steps else True)
                                      and ncrown / max(1, len(fr)) >= R["frontage.silhouette"]["crown_share"] - 1e-6)
    # materials.mix
    ks = [plan["kits"].get(str(k)) for k in plan["front"]]
    adj = sum(1 for a, b in zip(ks, ks[1:]) if a == b)
    kinds = sorted(set(plan["kits"].values()))
    out["materials.mix"] = dict(kits_in_radius=len(kinds), frontage_kits=ks, adjacent_same=adj,
                                ok=len(kinds) >= R["materials.mix"]["material_kinds"] and adj == 0)
    mods = [plan["modules"][str(k)] for k in plan["front"]]
    mx, run = 1, 1
    for a, b in zip(mods, mods[1:]):
        run = run + 1 if (a == b and plan["kits"].get(str(fr[0]["uid"])) is not None) else 1
        mx = max(mx, run)
    # identical module = same kit AND same window module
    km = [(plan["kits"].get(str(k)), plan["modules"][str(k)]) for k in plan["front"]]
    mx, run = 1, 1
    for a, b in zip(km, km[1:]):
        run = run + 1 if a == b else 1
        mx = max(mx, run)
    out["repetition.guard"] = dict(max_same_module_run=mx, ok=mx <= R["repetition.guard"]["max_same_module_adjacent"])
    # dressing.signs: placement (on a face), hero per route column, central hero, legible count, megastructure
    S = R["dressing.signs"]
    bad = []
    legible, legible_ids = 0, []
    heroes = {}
    central = False
    for s in plan["signs"]:
        b = bk.get(s["key"])
        ok = b is not None and abs(s["d"] - s["face"]) <= 0.35 and s["u0"] >= min(b["x0"], b["y0"]) - 1e3
        if b is not None and s.get("roof"):
            bu0, bu1, face, out_ = _face_frame(b, plan["nrm"], plan["axis"])
            ok = bu0 - 0.01 <= s["u0"] and s["u1"] <= bu1 + 0.01 and abs(s["z0"] - s["legs"] - b["h"]) < 0.05
        elif b is not None:
            bu0, bu1, face, out_ = _face_frame(b, plan["nrm"], plan["axis"])
            ok = ok and bu0 - 0.01 <= s["u0"] and s["u1"] <= bu1 + 0.01 and s["z0"] >= -0.01 and s["z1"] <= b["h"] + 0.01
        if not ok:
            bad.append(s["id"])
        if s.get("hero"):
            heroes[s["key"]] = s["id"]
            x = OC.proj(ov, s["centre"])[0] / OC.W_
            if (1 - S["hero_central_frac"]) / 2 < x < 1 - (1 - S["hero_central_frac"]) / 2:
                central = True
        if s["text_frac"] > 0 and s["words"]:
            hpx = abs(OC.proj(ov, _pt(plan["axis"], (s["u0"] + s["u1"]) / 2, s["d"], s["z1"]))[1] -
                      OC.proj(ov, _pt(plan["axis"], (s["u0"] + s["u1"]) / 2, s["d"], s["z0"]))[1])
            wpx = abs(OC.proj(ov, _pt(plan["axis"], s["u1"], s["d"], s["z0"]))[0] - OC.proj(ov, _pt(plan["axis"], s["u0"], s["d"], s["z0"]))[0])
            cap = s["text_frac"] * (wpx if s["tex"]["style"] == "blade" else hpx)
            s["cap_px_ov"] = round(cap, 1)
            if cap >= S["legible_px"]:
                legible += 1
                legible_ids.append(s["id"])
    out["dressing.signs"] = dict(signs=len(plan["signs"]), off_face=bad, heroes=len(heroes), route_columns=len(plan["route"]),
                                 hero_central=central, legible_ov=legible, legible_ids=legible_ids,
                                 megastructure=plan["mega"] and plan["mega"]["kind"],
                                 ok=not bad and len(heroes) == len(plan["route"]) and central and legible >= S["signs_on_screen_min"]
                                 and plan["mega"] is not None)
    # roof clutter kinds on the frontage (crowns + the kit roof rules) - recorded by the Blender build too
    PF = R["props.facade"]
    blocked = [p["id"] for p in plan["props"] if FC.prop_hits_opening(p, D["rooms"], plan["axis"], plan["line"], PF["opening_margin"])]
    lamp_bad = sum(1 for l in plan["lamps"] if FC.prop_hits_opening(
        dict(u0=l["pos"][plan["axis"]] - 0.15, u1=l["pos"][plan["axis"]] + 0.15, z0=0.0, z1=R["streets.light"]["lamp_post_h"],
             face=l["pos"][1 - plan["axis"]], out=0.0, depth=0.0), D["rooms"], plan["axis"], plan["line"], PF["opening_margin"]))
    kinds_ = sorted({p["kind"] for p in plan["props"]})
    out["props.facade"] = dict(props=len(plan["props"]), kinds=kinds_, blocked_by_opening=blocked, lamps_in_front_of_openings=lamp_bad,
                               lamps_dropped=plan.get("lamps_dropped"), rhythm_buildings=len(plan["rhythm"]),
                               ok=not blocked and lamp_bad == 0 and len(kinds_) >= 4)
    out["horizon.break"] = dict(spikes=len(plan["spikes"]), ok=len(plan["spikes"]) >= R["horizon.break"]["spikes_min"])
    return out
