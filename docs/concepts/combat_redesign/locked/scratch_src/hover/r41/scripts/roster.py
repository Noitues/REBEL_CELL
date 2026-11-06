"""Build wheel specs for the whole roster from content/*.tres (via tresdata)."""
import re
import tresdata as T
from roster_wheel import CLASS_STYLE, CORP_EMBLEM

CLASSES = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]
ALT_OF = {"wrecker": "breaker", "phantom": "ghost", "overclocker": "rigger", "hivemind": "botnet"}
CLASS_IDENTITY = {
    "breaker": ("Riveted plates: 12 steel plates, two rivets each, pink neon rim.",
                "Hub ring rimmed with a riveted band."),
    "wrecker": ("Breaker's plates, welded and dented: glowing weld beads on every seam, hammer dents, orange rim.",
                "Hub ring: welded seams."),
    "ghost": ("Flickering translucent rim: a see-through bezel whose neon breaks into dashes of varying brightness.",
              "Hub ring: flicker dashes."),
    "phantom": ("Ghost's flicker rim plus an after-image double rim, offset and fading (violet + cyan).",
                "Hub ring: doubled, offset rim."),
    "rigger": ("Cable-wrapped rim: diagonal wraps all round, four cable ties/plugs in green.",
               "Hub ring: cable wrap."),
    "overclocker": ("Rigger's cable wrap plus vented heat-sink fins with glowing amber tips.",
                    "Hub ring: wrap + mini fins."),
    "botnet": ("A ring of orbiting dots outside the rim; every sixth dot is a big drone light.",
               "Hub ring: dotted orbit."),
    "hivemind": ("Botnet's orbit dots, linked into a hex lattice on the bezel (violet).",
                 "Hub ring: hex lattice."),
}
CLASS_DRONES = {"botnet": 3, "hivemind": 4}  # Swarm Core up to 3, Hive Core up to 4 (content/hub_cores)
SEG_DESC = {"seg_accelerator": "Nudge cards next turn trigger twice.", "seg_anchor": "On Perfect: your wheel skips its next respin.",
            "seg_blank": "No modifier.", "seg_corrupt": "The target's resolved slice becomes CORRUPTED.",
            "seg_echo": "The outer slice triggers again at half output.", "seg_pierce": "Ignore block and shield.",
            "seg_x2": "Outer slice output doubled."}

ENEMY_PICKS = {
    "meridian": ["route_optimizer", "drone_dispatcher", "last_mile_enforcer"],
    "solace": ["care_swarm", "compliance_officer", "recall_unit"],
    "halcyon": ["transit_controller", "permit_office", "zoning_board"],
    "orbital": ["tracking_station", "weather_satellite", "geostationary_guard"],
    "rebel_cell": ["cell_informant", "dead_drop", "rc_template_elite"],
}
BOSSES = {"meridian": "the_manifest", "solace": "renewal_engine", "halcyon": "civic_core",
          "orbital": "commons_array", "rebel_cell": "dispatch_core"}
BOSS_SIGNATURE = {
    "the_manifest": ("Manifest board on every screen (PKG / LANE rows) and a red routing laser through all slices.",
                     "PEAK SEASON: hazard-striped outer band, red-hot tint, a second laser lane; second routing head."),
    "renewal_engine": ("A giant heartbeat runs through the wheel and every screen counts down 'RENEWS IN 00:xx'.",
                       "PAYMENT OVERDUE: cells turn infected magenta, the ECG goes erratic; a second read head."),
    "civic_core": ("Gold counter-flow runs the civic rings, district blocks light up across the blueprint.",
                   "STATE OF EMERGENCY: the grid goes red, siren stripes cross every screen; three readers."),
    "commons_array": ("Bright constellation drawn in gold across the star maps.",
                      "SOLAR FLARE: a white-hot whiteout sweeps across the screens; two fast-orbiting readers."),
    "dispatch_core": ("DISPATCH's order log scrolls on the corrupted Cell board ('> ORDER 0x11 ISSUED').",
                      "It runs YOUR programs: every screen shows the player's own C program, red-shifted and torn; wheel reconfigured, two readers."),
}


def badge_for(sl):
    nm = sl.get("name") or ""
    m = re.search(r"drains (\d+) RAM", nm)
    if m:
        return "-%s RAM" % m.group(1)
    if sl.get("badge") == "+1R":
        return "+1 RES"
    return None


def slots_from(w):
    out = []
    for s in w["slots"]:
        out.append(dict(program=s["program"], value=s["value"], special=s["special"], badge=badge_for(s),
                        name=s["name"], id=s["id"]))
    return out


def class_spec(cid):
    k = T.load_class(cid)
    w = k["wheel"]
    spec = dict(theme="player", cls=cid, slots=slots_from(w), pointers=w["pointers"], orbit=0,
                hub=dict(name=k["name"], sub=w["hub"]["name"], emblem=CLASS_STYLE[cid]["emblem"]),
                ring=k["ring"], hp=(k["hp"], k["hp"]), seed=CLASSES.index(cid) + 1,
                drones=[dict(name="Drone", hp=5)] * CLASS_DRONES.get(cid, 0))
    meta = dict(name=k["name"], desc=k["desc"], hp=k["hp"], core=w["hub"], ring=k["ring"],
                alt_of=ALT_OF.get(cid), identity=CLASS_IDENTITY[cid])
    return spec, meta


def mechanics(e, w=None, spawns=None, phase=None):
    w = w or e["wheel"]
    out = []
    ptr = phase["pointers"] if phase and phase["pointers"] else w["pointers"]
    if len(ptr) > 1:
        out.append("%d READERS @ %s" % (len(ptr), " / ".join(str(p) for p in ptr)))
    orb = phase["orbit"] if phase else w["orbit"]
    if orb:
        out.append("ORBIT +%d / TURN" % orb)
    if w["hub"] and w["hub"]["id"] == "compliance_lock":
        out.append("HUB LOCK: RES 3")
    if w["resistance"]:
        out.append("RESISTANCE %d" % w["resistance"])
    for s in (spawns if spawns is not None else e["spawns"]):
        out.append("DRONE: %s x%d (HP %d)" % (s["name"], s["max_active"], s["hp"]))
    specials = sorted({s["id"] for s in w["slots"] if s["special"]})
    if specials:
        out.append("SPECIAL: " + ", ".join(x.replace("_", " ").upper() for x in specials))
    if any(badge_for(s) for s in w["slots"]):
        out.append("RULE CHIPS: " + ", ".join(sorted({badge_for(s) for s in w["slots"] if badge_for(s)})))
    return out


def enemy_spec(eid, corp=None, lod=False):
    e = T.load_enemy(eid)
    corp = corp or e["corp"] or "rebel_cell"
    w = e["wheel"]
    hubcore = w["hub"]["name"] if w["hub"] else T_CORPNAME(corp)
    res = w["resistance"]
    lock = False
    if w["hub"] and w["hub"]["id"] == "compliance_lock":
        res, lock = 3, True
    emblem = CORP_EMBLEM[corp]
    if eid.startswith("rc_template"):
        emblem = "EM_BREAKER"  # a copy of one of your operatives
        hubcore = "copy of your Breaker"
    drones = []
    for s in e["spawns"]:
        drones += [dict(name=s["name"], hp=s["hp"])] * s["max_active"]
    spec = dict(theme=corp, slots=slots_from(w), pointers=w["pointers"], orbit=w["orbit"], resistance=res, lock=lock,
                hub=dict(name=e["name"], sub=hubcore, emblem=emblem), ring=None, hp=(e["hp"], e["hp"]),
                drones=drones, seed=sum(map(ord, eid)) % 50 + 1)
    meta = dict(name=e["name"], role=e["role"], hp=e["hp"], desc=e["desc"], mech=mechanics(e), corp=corp)
    return spec, meta


def T_CORPNAME(corp):
    from slicelib import CORPS
    return CORPS[corp]["name"].title()


def boss_specs(corp):
    from slicelib import CORPS
    eid = BOSSES[corp]
    e = T.load_enemy(eid)
    w = e["wheel"]
    pips = [p["threshold"] for p in e["phases"]]
    base = dict(theme=corp, ring=None, seed=sum(map(ord, eid)) % 50 + 1)
    p1 = dict(base, slots=slots_from(w), pointers=w["pointers"], orbit=0, resistance=w["resistance"],
              hub=dict(name=e["name"], sub=w["hub"]["name"], emblem=CORP_EMBLEM[corp]), hp=(e["hp"], e["hp"]), drones=[],
              boss=dict(phase=1, pips=pips, title=e["name"].upper(), sub="%s  |  BOSS  |  PHASE 1" % CORPS[corp]["name"]))
    ph = e["phases"][0]
    w2 = ph["wheel"] or w
    hub2 = ph["hub"] or w2["hub"] or w["hub"]
    drones = []
    for s in ph["spawns"]:
        drones += [dict(name=s["name"], hp=s["hp"])] * s["max_active"]
    p2 = dict(base, slots=slots_from(w2), pointers=ph["pointers"] or w2["pointers"], orbit=ph["orbit"],
              resistance=w2["resistance"], hub=dict(name=e["name"], sub=hub2["name"], emblem=CORP_EMBLEM[corp]),
              hp=(int(e["hp"] * 0.6), e["hp"]), drones=drones,
              boss=dict(phase=2, pips=pips, title=e["name"].upper(), sub="%s  |  BOSS  |  PHASE 2" % CORPS[corp]["name"]))
    meta = dict(name=e["name"], id=eid, hp=e["hp"], desc=e["desc"], core=w["hub"], phases=e["phases"],
                sig=BOSS_SIGNATURE[eid], mech1=mechanics(e), mech2=mechanics(e, w2, ph["spawns"], ph))
    return p1, p2, meta
