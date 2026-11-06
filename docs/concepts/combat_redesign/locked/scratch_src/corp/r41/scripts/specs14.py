"""Round 14 wheel specs: per corp a regular, an elite and the boss in phases 1-3 (from content via roster/tresdata)."""
import copy
import tresdata as T
import roster as RS
import combat_specs as CS
from slicelib import CORPS

PICKS = {  # (regular, elite) per corp; enemies whose mechanics show on the wheel
    "meridian": ("route_optimizer", "last_mile_enforcer"),
    "solace": ("care_swarm", "recall_unit"),
    "halcyon": ("permit_office", "zoning_board"),
    "orbital": ("tracking_station", "geostationary_guard"),
    "rebel_cell": ("cell_informant", "the_handler"),
}
CORP_TITLE = {"meridian": "MERIDIAN FREIGHT SYSTEMS", "solace": "SOLACE BIOSYSTEMS", "halcyon": "HALCYON CIVIC",
              "orbital": "ORBITAL COMMONS", "rebel_cell": "REBEL_CELL  (corrupted by DISPATCH)"}
MERGE = {"rebel_cell": (2, 3)}  # DISPATCH P3: two adjacent ZERO-DAY 24 screens merge


def enemy(eid, corp, tier):
    s, m = RS.enemy_spec(eid, corp)
    s = copy.deepcopy(s)
    s["theme"] = corp
    s["tier"] = tier
    s["key"] = eid
    s["drones"] = []
    return s, m


def boss(corp, phase):
    p1, p2, m = RS.boss_specs(corp)
    e = T.load_enemy(RS.BOSSES[corp])
    if phase == 1:
        s = copy.deepcopy(p1)
        s["hp"] = (e["hp"], e["hp"])
    elif phase == 2:
        s = copy.deepcopy(p2)
    else:
        s = copy.deepcopy(p2)
        ph = e["phases"][1]
        w = ph["wheel"] or e["wheel"]
        s["slots"] = RS.slots_from(w)
        if ph["pointers"]:
            s["pointers"] = ph["pointers"]
        s["orbit"] = ph["orbit"]
        s["drones"] = []
        for sp in ph["spawns"]:
            s["drones"] += [dict(name=sp["name"], hp=sp["hp"])] * sp["max_active"]
        s["hp"] = (int(e["hp"] * 0.28), e["hp"])
        s["armour"] = True
        if corp in MERGE:
            s["merge"] = MERGE[corp]
        s["boss"] = dict(s["boss"], phase=3, sub="%s  |  BOSS  |  PHASE 3" % CORPS[corp]["name"])
    if phase == 2:
        s["drones"] = []
    s["tier"] = "boss"
    s["key"] = RS.BOSSES[corp]
    s["variant"] = "p%d" % phase
    s["pred"] = 0
    lines = [ph.get("line", "") for ph in e["phases"]]
    return s, dict(name=e["name"], hp=e["hp"], lines=lines, phases=e["phases"])


def player():
    s = CS.player(41, 14)[0]
    s["key"] = "breaker"
    return s
