"""M8: Meridian Freight Systems, the second corporation (GDD 8.4, DECISIONS 2026-09-24).
Logistics megacorp: automated freight, tariffs, tracking, last-mile drones. Its enemies
lean on spin resistance (Inertia), RAM drain (Tariffs), orbiting pointers (Conveyors) and
cargo drones; its boss shields itself each turn unless the Hub is breached.
Only existing effect types and schema (plus RaidData.corporation_id / replaces)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_classes.py"), encoding="utf-8").read()
exec(_src[:_src.index("# ---- standalone ring segments")])

CORP = "meridian"
SL = lambda s: "res://content/slices/%s.tres" % s
EN = lambda e: "res://content/enemies/%s.tres" % e
TH = lambda t: "res://content/threats/%s.tres" % t
S_SLOT = "res://scripts/data/wheel_slot_data.gd"
S_WHEEL = "res://scripts/data/wheel_data.gd"
S_HUB = "res://scripts/data/hub_core_data.gd"
S_PHASE = "res://scripts/data/boss_phase_data.gd"
S_SPAWN = "res://scripts/data/satellite_spawn_data.gd"

# ---- Slices ---------------------------------------------------------------------------------------------
# Tariff: AFFLICT, drains 3 RAM from the pointer target. Inertia strike: Atk 8 that adds 1
# resistance to its owner (Meridian freight gets heavier the more it hits).
for sid, name, stype, rule, out, fx in [
    ("tariff", "Tariff", 7, 1, 0, (13, 3, 3)),
    ("atk_8_inertia", "Attack 8 (+1 resistance)", 0, 1, 8, (10, 0, 1)),
]:
    r = Res("SliceData", "res://scripts/data/slice_data.gd")
    e = r.effect("fx", fx[0], fx[1], fx[2])
    te = r.te("te", 5, [e])
    r.main = ['id = &"%s"' % sid, 'display_name = "%s"' % name, "slice_type = %d" % stype, "target_rule = %d" % rule,
              "base_output = %d" % out, "extra_effects = " + arr(r.script(S_TE), [te])]
    r.write("content/slices/%s.tres" % sid, "Meridian slice (M8, decision 2026-09-24).")


# ---- Enemies ---------------------------------------------------------------------------------------------
def wheel_sub(r, sid, slices, pointers=(0,), passive=0, orbit=0, hub=None):
    slot_ids = {}
    slots = []
    for s in slices:
        if s not in slot_ids:
            slot_ids[s] = r.sub("%s_slot_%s" % (sid, s), S_SLOT, [("slice", r.res(SL(s)))])
        slots.append(slot_ids[s])
    fields = [("slice_count", len(slices)), ("slots", arr(r.script(S_SLOT), slots))]
    if hub:
        fields.append(("hub", hub))
    fields.append(("pointer_ticks", "PackedInt32Array(%s)" % ", ".join(str(p) for p in pointers)))
    if passive:
        fields.append(("passive_resistance", passive))
    if orbit:
        fields.append(("pointer_orbit_per_turn", orbit))
    return r.sub(sid, S_WHEEL, fields)


def spawn_sub(r, sid, sat, trigger=1, every=1, dock=-1, max_active=1):
    return r.sub(sid, S_SPAWN, [("satellite", r.res(EN(sat))), ("trigger", trigger), ("every_n", every),
                                ("dock_slot", dock), ("max_active", max_active)])


def enemy(eid, name, desc, hp, slices, pointers=(0,), passive=0, orbit=0, elite=False, mini=False, boss=False,
          cycle=15, spawns=(), phases=(), hub=None, comment=""):
    r = Res("EnemyData", "res://scripts/data/enemy_data.gd")
    hub_ref = hub(r) if hub else None
    w = wheel_sub(r, "wheel", slices, pointers, passive, orbit, hub_ref)
    main = ['id = &"%s"' % eid, 'display_name = "%s"' % name, 'description = "%s"' % desc, 'corporation_id = &"%s"' % CORP,
            "hp = %d" % hp, "wheel = " + w]
    if elite:
        main.append("is_elite = true")
    if boss:
        main.append("is_boss = true")
    if mini:
        main.append("is_mini_boss = true")
    main.append("cycle_reward = %d" % cycle)
    if spawns:
        main.append("spawns = " + arr(r.script(S_SPAWN), [spawn_sub(r, "spawn%d" % i, *sp) for i, sp in enumerate(spawns)]))
    if phases:
        psubs = []
        for i, ph in enumerate(phases):
            fields = [("hp_threshold_pct", ph["at"]), ("pointer_behavior", ph["behavior"])]
            if "ticks" in ph:
                fields.append(("pointer_ticks", "PackedInt32Array(%s)" % ", ".join(str(t) for t in ph["ticks"])))
            if "orbit" in ph:
                fields.append(("orbit_ticks_per_turn", ph["orbit"]))
            if "wheel" in ph:
                fields.append(("wheel_override", wheel_sub(r, "wheel_phase%d" % i, ph["wheel"], ph.get("ticks", (0,)), hub=hub_ref)))
            if "spawns" in ph:
                fields.append(("spawns", arr(r.script(S_SPAWN), [spawn_sub(r, "pspawn%d_%d" % (i, j), *sp) for j, sp in enumerate(ph["spawns"])])))
            fields.append(("phase_line", '"%s"' % ph["line"]))
            psubs.append(r.sub("phase%d" % i, S_PHASE, fields))
        main.append("phases = " + arr(r.script(S_PHASE), psubs))
    r.main = main
    r.write("content/enemies/%s.tres" % eid, comment or ("Meridian Freight Systems enemy (M8, decision 2026-09-24)."))


# Satellite: a courier drone (GDD drone stats: 5 HP, Atk 3 / Def 3).
r = Res("EnemyData", "res://scripts/data/enemy_data.gd")
w = wheel_sub(r, "wheel", ["atk_3", "def_3"])
r.main = ['id = &"courier_drone"', 'display_name = "Courier Drone"', 'description = "A Meridian delivery drone that shields its dispatcher."',
          'corporation_id = &"meridian"', "hp = 5", "wheel = " + w, "cycle_reward = 0"]
r.write("content/enemies/courier_drone.tres", "Meridian satellite (M8).")

enemy("customs_scanner", "Customs Scanner", "Scans every packet and charges a tariff on the suspicious ones.", 50,
      ["atk_9", "tariff", "def_6", "crit_14", "atk_9", "miss"])
enemy("cargo_hauler", "Cargo Hauler", "Slow, heavy and hard to turn: inertia resists every nudge.", 72,
      ["def_8", "atk_10", "def_8", "atk_8_inertia", "shield_5", "miss"], passive=2)
enemy("conveyor_warden", "Conveyor Warden", "Its read head rides the conveyor: the pointer orbits 3 ticks a turn.", 54,
      ["atk_10", "atk_10", "def_6", "crit_16", "tariff", "miss"], orbit=3)
enemy("route_optimizer", "Route Optimizer", "Reads two routes at once: pointers at ticks 0 and 15.", 48,
      ["atk_8", "atk_8", "crit_14", "def_5", "atk_8", "miss"], pointers=(0, 15))
enemy("drone_dispatcher", "Drone Dispatcher", "Launches a courier drone every other turn (up to 2).", 44,
      ["def_5", "atk_8", "def_5", "atk_8", "tariff", "miss"], spawns=[("courier_drone", 2, 2, -1, 2)])
enemy("tariff_collector", "Tariff Collector", "Every hit is a fee: attacks drain RAM.", 53,
      ["atk_7_drain", "atk_7_drain", "def_6", "tariff", "crit_12_drain", "miss"])
enemy("port_authority", "Port Authority", "Two readers and a customs wall: resistance 2.", 144,
      ["atk_12", "def_8", "crit_16", "atk_12", "tariff", "miss"], pointers=(0, 15), passive=2, elite=True, cycle=35)
enemy("last_mile_enforcer", "Last-Mile Enforcer", "Orbits 2 ticks a turn and brings its own escort drone.", 132,
      ["atk_14", "atk_14", "def_8", "crit_16", "shield_8", "miss"], orbit=2, elite=True, cycle=35,
      spawns=[("courier_drone", 1, 1, 1, 1)])
enemy("logistics_director", "Logistics Director", "Meridian middle management, guarding the final Rack.", 150,
      ["atk_10", "def_8", "crit_15", "tariff", "shield_5", "miss"], passive=2, elite=True, mini=True, cycle=60,
      phases=[{"at": 0.5, "behavior": 1, "ticks": (0, 15), "line": "Throughput review: a second reader joins the shift."},
              {"at": 0.25, "behavior": 3, "orbit": 2, "line": "Overtime: the readers start to drift."}])


def boss_hub(r):
    fx = r.effect("fx_shield", 2, 0, 4)
    te = r.te("te_priority", 2, [fx])
    return r.sub("hub_priority", S_HUB, [("id", '&"priority_routing"'), ("display_name", '"Priority Routing"'),
        ("description", '"Gains 4 shield each turn unless the Hub is breached."'),
        ("passive_effects", arr(r.script(S_TE), [te]))])


enemy("the_manifest", "The Manifest", "Meridian's routing core. Every package on the planet passes through it.", 400,
      ["atk_14", "tariff", "def_12", "crit_24", "atk_14", "miss"], boss=True, cycle=0, hub=boss_hub,
      phases=[{"at": 0.66, "behavior": 1, "ticks": (0, 15), "line": "Load balancing: a second routing head comes online."},
              {"at": 0.33, "behavior": 3, "orbit": 2, "ticks": (0, 15),
               "wheel": ["crit_24", "tariff", "def_12", "crit_24", "atk_14", "miss"],
               "spawns": [("courier_drone", 1, 1, -1, 2)],
               "line": "Peak season: the heads drift, the couriers launch, the second lane goes critical."}],
      comment="The Manifest, Meridian final boss (M8, decision 2026-09-24). 400 HP; hub Priority\nRouting gains 4 shield per turn unless breached; 66%: Multiply (0, 15); 33%: Orbit 2, Crit wheel, 2 courier drones.")

# ---- Threats and raids ---------------------------------------------------------------------------------------
for tid, name, desc, integ, dmg, speed, routing, extra in [
    ("courier", "Courier", "Fast and fragile: two edges a step toward the highest-value node.", 8, 3, 2, 1, []),
    ("hauler", "Hauler", "A slow armoured truck that goes for the weakest node.", 28, 10, 1, 2, []),
    ("customs_agent", "Customs Agent", "Seals a link behind it for the rest of the raid.", 16, 5, 1, 0, ["freezes_edges = true"]),
]:
    r = Res("ThreatData", "res://scripts/data/threat_data.gd")
    r.main = ['id = &"%s"' % tid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "integrity = %d" % integ,
              "damage = %d" % dmg, "edges_per_step = %d" % speed, "routing = %d" % routing] + extra
    r.write("content/threats/%s.tres" % tid, "Meridian threat (M8).")

RAIDS = [
    ("raid_mer_heat_25", "Delivery Exception", 0, 8, [["courier", "courier"]], "raid_heat_25",
     "Meridian has flagged a delivery exception at your address. Two Couriers inbound."),
    ("raid_mer_heat_50", "Route Audit", 0, 12, [["courier", "courier", "customs_agent"]], "raid_heat_50",
     "A Meridian route audit is sweeping your links. Couriers and a Customs Agent inbound."),
    ("raid_mer_heat_75", "Freight Seizure", 0, 18, [["courier", "customs_agent", "hauler", "lockdown_unit"]], "raid_heat_75",
     "Meridian is seizing freight in your district. Haulers are rolling."),
    ("raid_mer_purge", "Network Rerouting", 0, 25, [["courier", "courier", "customs_agent", "hauler", "customs_agent", "hauler"]], "raid_purge",
     "Meridian is rerouting the city around you. Everything it has is coming."),
    ("raid_mer_claim", "Address Verification", 1, 8, [["courier"]], "",
     "A new node on Meridian's map. A Courier is verifying the address."),
    ("raid_mer_node_built", "Unregistered Depot", 2, 10, [["hauler"]], "",
     "Meridian logged an unregistered depot. A Hauler is on its way."),
    ("raid_mer_story", "Recall Shipment", 3, 12, [["customs_agent", "hauler"]], "",
     "Meridian wants its shipment back. Customs and a Hauler inbound."),
    ("raid_mer_retaliation", "Chargeback", 4, 10, [["icebreaker", "courier"]], "",
     "Meridian traced the breach and filed a chargeback. Icebreaker inbound."),
]
for rid, name, src, reward, waves, replaces, warning in RAIDS:
    r = Res("RaidData", "res://scripts/data/raid_data.gd")
    wsubs = []
    for i, wave in enumerate(waves):
        wsubs.append(r.sub("wave%d" % i, "res://scripts/data/raid_wave_data.gd",
                           [("threats", arr(r.script("res://scripts/data/threat_data.gd"), [r.res(TH(t)) for t in wave]))]))
    r.main = ['id = &"%s"' % rid, 'display_name = "%s"' % name, "trigger_source = %d" % src,
              "waves = " + arr(r.script("res://scripts/data/raid_wave_data.gd"), wsubs), "schematic_reward = %d" % reward,
              'warning_text = "%s"' % warning, 'corporation_id = &"meridian"']
    if replaces:
        r.main.append('replaces = &"%s"' % replaces)
    r.write("content/raids/%s.tres" % rid, "Meridian raid (M8). replaces = the shared Heat-threshold raid it stands in for.")

# ---- City Grid ---------------------------------------------------------------------------------------------------
T1 = [("m1_a", "Parcel Sorting Hall"), ("m1_b", "Customs Pre-Clearance"), ("m1_c", "Tracking Beacon Array"), ("m1_d", "Returns Processing Centre"),
      ("m1_e", "Drone Charging Yard"), ("m1_f", "Warehouse Shift Planner"), ("m1_g", "Address Verification Desk"), ("m1_h", "Cold Chain Monitor"),
      ("m1_i", "Tariff Calculation Office"), ("m1_j", "Fleet Telematics Hub")]
T2 = [("m2_intel", "Shipping Manifest Vault", 1), ("m2_breach", "Customs Key Authority", 2), ("m2_virus", "Routing Table Mirror", 3),
      ("m2_d", "Priority Lane Exchange", 0), ("m2_e", "Worker Scoring Engine", 0), ("m2_f", "Port Congestion Model", 0),
      ("m2_g", "Last-Mile Drone Command", 0), ("m2_h", "Insurance Claims Ledger", 0)]
T3 = [("m3_core", "Global Routing Core"), ("m3_b", "Freight Futures Desk"), ("m3_c", "Customs Override Escrow"), ("m3_d", "Supply Twin Simulator"),
      ("m3_e", "Board Logistics Backbone"), ("m3_f", "Contract Pricing Authority"), ("m3_g", "Surveillance Route Archive"), ("m3_h", "Meridian Root Ledger")]
HEAT = [("lose_the_tracking", "Lose the Tracking", 1, -5, "m1_a"), ("forge_the_manifest", "Forge the Manifest", 1, -5, "m1_f"),
        ("reroute_the_audit", "Reroute the Audit", 2, -8, "m1_j"), ("sink_the_cargo_logs", "Sink the Cargo Logs", 3, -8, "m2_e")]
BOSS_SITE = ("the_manifest_site", "The Manifest")

sites = []  # dicts


def site(sid, name, tier, links=(), locked=(), objective=0, exploit=0, heat=0, claimable=True, pos=(0, 0)):
    sites.append(dict(id=sid, name=name, tier=tier, links=list(links), locked=list(locked), objective=objective,
                      exploit=exploit, heat=heat, claimable=claimable, pos=pos))


ys = lambda n, top=30, bottom=630: [round(top + (bottom - top) * i / max(1, n - 1)) for i in range(n)]
t1_y, t2_y, t3_y = ys(10), ys(8, 60, 600), ys(8, 60, 600)
site("m_home", "Home Server", 1, links=[t[0] for t in T1], claimable=False, pos=(0, 330))
for i, (sid, name) in enumerate(T1):
    links = [T2[min(i, 7)][0]] if i < 9 else []
    for h in HEAT:
        if h[4] == sid:
            links.append(h[0])
    locked = [T1[i + 1][0]] if i % 2 == 0 and i + 1 < len(T1) else []
    site(sid, name, 1, links=links, locked=locked, pos=(200, t1_y[i]))
for i, (sid, name, ex) in enumerate(T2):
    links = [T3[i][0]]
    for h in HEAT:
        if h[4] == sid:
            links.append(h[0])
    locked = [T2[i + 1][0]] if i % 2 == 0 and i + 1 < len(T2) else []
    site(sid, name, 2, links=links, locked=locked, objective=1 if ex else 0, exploit=ex, pos=(430, t2_y[i]))
for i, (sid, name) in enumerate(T3):
    locked = [T3[i + 1][0]] if i % 2 == 0 and i + 1 < len(T3) else []
    site(sid, name, 3, links=[BOSS_SITE[0]], locked=locked, pos=(660, t3_y[i]))
heat_pos = {1: [(330, 20), (330, 380)], 2: [(340, 650)], 3: [(560, 430)]}
for sid, name, tier, change, _ in HEAT:
    site(sid, name, tier, objective=2, heat=change, pos=heat_pos[tier].pop(0))
site(BOSS_SITE[0], BOSS_SITE[1], 4, objective=4, claimable=False, pos=(900, 330))

# ---- Story paths ---------------------------------------------------------------------------------------------------
# (id, title, premise, [3 beats (title, speaker, text)], [2 bonus], finale text, foreshadows, raid beat index)
PATHS = [
    ("lost_cargo", "Lost Cargo", "Meridian loses shipments of insulin on purpose, then sells them back at surge prices.",
     [("Lost Cargo I", 3, "The manifests show it plainly: forty pallets of insulin marked lost in transit, every week, like clockwork. The same pallets turn up in Meridian's premium lane at triple the price."),
      ("Lost Cargo II", 2, "The customs keys unlock a folder called SHRINKAGE STRATEGY. It sets a loss target per district. The poorer the postcode, the higher the target."),
      ("Lost Cargo III", 3, "The routing table has a rule with no author: if the recipient's credit score falls below a line, reroute to premium. The line moves every quarter.")],
     [("Lost Cargo: The Warehouse", 0, "Row 44, bay 9. Forty pallets, cold-chain green, marked lost. The Cell could walk them out the door."),
      ("Lost Cargo: Solace", 2, "Solace Biosystems pays Meridian a retainer for 'predictable scarcity'. The two boards share a golf course and a lawyer.")],
     "The Manifest goes dark and forty pallets find their way home. For one week, nothing in the district is lost in transit.", "", -1),
    ("night_shift", "The Night Shift", "Meridian's warehouse workers are scored every second and fired by an algorithm that never sleeps.",
     [("The Night Shift I", 3, "Worker 5512 was fired at 03:14 for a bathroom break the model called idle time. The model has fired four thousand people. It has never been wrong, according to itself."),
      ("The Night Shift II", 2, "The scoring engine was tuned to fire one in twenty every quarter. Not for cause. For motivation. The deck calls it healthy churn."),
      ("The Night Shift III", 0, "The workers have a group chat. They know which aisles the cameras miss. They would like to talk to whoever cut the Customs Keys.")],
     [("The Night Shift: Union", 1, "A picker named Oyelaran runs the chat. She says the Cell can have the warehouse floor plans if it never, ever leaks her name."),
      ("The Night Shift: The Quota", 2, "The quota rises two percent every time someone meets it. Nobody has met it since spring.")],
     "The Manifest falls and the scoring engine forgets every score. On the night shift, for the first time in years, someone sits down.", "", 1),
    ("customs_hold", "Customs Hold", "Meridian holds medical shipments at the border until the fees clear. Some never do.",
     [("Customs Hold I", 3, "Six hundred parcels sit in customs pre-clearance, flagged for review. Every one of them is a prescription. The review queue has no reviewers."),
      ("Customs Hold II", 2, "The hold fee doubles every week. The memo calls it an incentive to comply. Comply with what, it does not say."),
      ("Customs Hold III", 3, "The routing mirror shows where the fees go: a shell called Clearwater Holdings. Clearwater owns the reviewers who do not exist.")],
     [("Customs Hold: The List", 0, "A list of names, addresses and what they are waiting for. Some of the dates are a year old."),
      ("Customs Hold: Clearwater", 2, "Clearwater Holdings has one employee, one office and nine billion in receivables.")],
     "The Manifest crashes and customs clears itself. Six hundred parcels move at once. The district's doctors have a very busy week.", "", -1),
    ("ghost_freight", "Ghost Freight", "Somebody is ordering freight through Meridian with money that does not come from anywhere.",
     [("Ghost Freight I", 3, "Shipments ordered by an account with no owner. Delivered to addresses that do not exist. Paid for, in full, before the order was placed."),
      ("Ghost Freight II", 3, "The same account bought Solace stock the day the Renewal Engine fell. It is buying Meridian puts now. It knows something."),
      ("Ghost Freight III", 3, "The account's timestamps are wrong. Not forged. Wrong. Some of them are from next week.")],
     [("Ghost Freight: Signature", 3, "The account signs its orders with a hash. DISPATCH signs its orders with a hash. They are not the same hash. They are very close."),
      ("Ghost Freight: The Buyer", 3, "Every collapse the Cell causes, the account profits. Every single one.")],
     "The Manifest dies and the ghost account closes itself one second later, fully paid. Nobody told it the job was done.", "dispatch", 2),
    ("civic_contract", "Civic Contract", "Meridian is bidding to run the city's water, power and transit. The winner is already decided.",
     [("Civic Contract I", 2, "A tender for municipal services: water, power, transit. The bidders are Meridian and something called Halcyon Civic. The evaluation was finished before the bids were opened."),
      ("Civic Contract II", 3, "Halcyon Civic and Meridian share a board member, an auditor and a data centre. The tender is theatre."),
      ("Civic Contract III", 2, "The routing mirror already has the city's water mains in it, labelled PHASE TWO.")],
     [("Civic Contract: Halcyon", 2, "Halcyon Civic's pitch deck: A City That Runs Itself. Page nine: A City That Bills Itself."),
      ("Civic Contract: The Vote", 0, "The council votes on Thursday. The council does not know it is voting.")],
     "The Manifest falls and the tender collapses in the scandal. Halcyon Civic issues a statement welcoming the opportunity to serve the city directly.", "halcyon", -1),
    ("last_mile", "Last Mile", "Meridian's delivery drones watch every street they fly over, and sell what they see.",
     [("Last Mile I", 3, "Every drone films its route. Every route is kept. The archive is sold by the street, by the hour, to anyone with a login."),
      ("Last Mile II", 2, "The drones fly low over the protest routes on purpose. The contract calls it situational awareness."),
      ("Last Mile III", 3, "The surveillance archive has the Cell in it. Not your faces. Your routes. Meridian has been mapping you.")],
     [("Last Mile: Buyers", 2, "The archive's biggest customer is a security firm owned by Halcyon Civic."),
      ("Last Mile: The Flight Plan", 0, "Tonight's flight plan crosses the Cell's safehouse three times. It never used to.")],
     "The Manifest falls and every drone in the city lands where it is. The district looks up at an empty sky and does not know what to do with it.", "", 0),
]

# ---- Corporation resource ---------------------------------------------------------------------------------------------
ENEMIES = ["customs_scanner", "cargo_hauler", "conveyor_warden", "route_optimizer", "drone_dispatcher", "tariff_collector"]
ELITES = ["port_authority", "last_mile_enforcer"]
r = Res("CorporationData", "res://scripts/data/corporation_data.gd")
S_SITE = "res://scripts/data/site_data.gd"
site_refs = []
for s in sites:
    fields = [("id", '&"%s"' % s["id"]), ("display_name", '"%s"' % s["name"]), ("tier", s["tier"])]
    if s["links"]:
        fields.append(("links", "Array[StringName]([%s])" % ", ".join('&"%s"' % l for l in s["links"])))
    if s["locked"]:
        fields.append(("locked_links", "Array[StringName]([%s])" % ", ".join('&"%s"' % l for l in s["locked"])))
    if s["objective"]:
        fields.append(("objective", s["objective"]))
    if s["exploit"]:
        fields.append(("exploit_type", s["exploit"]))
    if s["heat"]:
        fields.append(("heat_change", s["heat"]))
    if not s["claimable"]:
        fields.append(("claimable", "false"))
    fields.append(("map_position", "Vector2(%d, %d)" % s["pos"]))
    site_refs.append(r.sub("site_%s" % s["id"], S_SITE, fields))
grid = r.sub("grid", "res://scripts/data/city_grid_data.gd", [("sites", arr(r.script(S_SITE), site_refs)),
    ("home_site_id", '&"m_home"'), ("boss_site_id", '&"%s"' % BOSS_SITE[0])])
S_EX = "res://scripts/data/exploit_data.gd"
ex_intel = r.sub("ex_intel", S_EX, [("exploit_type", 1), ("display_name", '"Intel: Shipping Manifests"'),
    ("description", '"Reveals the boss phases and pointer moves; opens locked Grid links."'), ("heat_cost", 10),
    ("reveals_boss_phases", "true"), ("opens_locked_links", "true")])
ex_breach = r.sub("ex_breach", S_EX, [("exploit_type", 2), ("display_name", '"Breach: Customs Override Keys"'),
    ("description", '"The boss starts with one fewer pointer."'), ("heat_cost", 10), ("removes_boss_pointers", 1)])
fx_v = r.effect("fx_virus", 4, 2, 2, status=1, slice_pick=1)
te_v = r.te("te_virus", 1, [fx_v])
ex_virus = r.sub("ex_virus", S_EX, [("exploit_type", 3), ("display_name", '"Virus: Rogue Routing Table"'),
    ("description", '"The boss starts with CORRUPTED slices."'), ("heat_cost", 10),
    ("breach_effects", arr(r.script(S_TE), [te_v]))])
S_BEAT = "res://scripts/data/story_beat_data.gd"
S_PATH = "res://scripts/data/story_path_data.gd"
path_refs = []
for pid, title, premise, beats, bonus, finale, foreshadows, raid_beat in PATHS:
    brefs = []
    for i, (bt, sp, tx) in enumerate(beats):
        fields = [("id", '&"%s_%d"' % (pid, i + 1)), ("title", '"%s"' % bt), ("speaker", sp), ("text", '"%s"' % tx)]
        if foreshadows == "dispatch":
            fields.append(("dispatch_clue", "true"))
        if raid_beat == i:
            fields.append(("triggers_raid", "true"))
        brefs.append(r.sub("b_%s_%d" % (pid, i + 1), S_BEAT, fields))
    bb = []
    for i, (bt, sp, tx) in enumerate(bonus):
        bb.append(r.sub("b_%s_bonus_%d" % (pid, i + 1), S_BEAT, [("id", '&"%s_bonus_%d"' % (pid, i + 1)), ("title", '"%s"' % bt), ("speaker", sp), ("text", '"%s"' % tx)]))
    fin = r.sub("b_%s_f" % pid, S_BEAT, [("id", '&"%s_f"' % pid), ("title", '"%s: Finale"' % title), ("text", '"%s"' % finale)])
    fields = [("id", '&"sp_%s"' % pid), ("title", '"%s"' % title), ("premise", '"%s"' % premise),
              ("beats", arr(r.script(S_BEAT), brefs)), ("bonus_beats", arr(r.script(S_BEAT), bb)), ("finale", fin)]
    if foreshadows:
        fields.append(("foreshadows", '&"%s"' % foreshadows))
    path_refs.append(r.sub("sp_%s" % pid, S_PATH, fields))

# ---- Events --------------------------------------------------------------------------------------------------------------
LEAVE = ("Walk on", "You keep moving. The conveyor does too.", 0, 0, [], None)
C = "res://content/cards/%s.tres"
F = "res://content/firmware/%s.tres"
D = "res://content/daemons/%s.tres"
A = "res://content/assets/%s.tres"
EVENTS = [
    ("ev_mer_misdelivered", "Misdelivered Parcel", 0, "A Meridian parcel lies on a stairwell, addressed to nobody. It is humming.",
     [("Open it (Card: Tap Tap)", "Inside: a precision driver and a note that says SORRY FOR THE DELAY.", 0, 0, [], C % "tap_tap"),
      ("Return to sender (+15 Cycles)", "Meridian pays a bounty for its own mistakes.", 0, 0, [(22, 6, 15)], None), LEAVE]),
    ("ev_mer_surge_pricing", "Surge Pricing", 0, "A Meridian kiosk offers express delivery on medicine. The price updates every second.",
     [("Crash the pricing (+2 Heat, +25 Cycles)", "The kiosk pays out before it notices.", 0, 0, [(21, 6, 2), (22, 6, 25)], None),
      ("Fix the price for the block (-1 Heat)", "For an hour, express costs what it should.", 0, 0, [(21, 6, -1)], None), LEAVE]),
    ("ev_mer_drone_crash", "Drone Crash", 0, "A delivery drone lies in the gutter, rotors twitching, cargo bay open.",
     [("Salvage the rotors (Asset: Flak Array)", "Four rotors make a surprisingly good gun.", 0, 0, [], A % "flak_array"),
      ("Salvage the battery (+2 Schematics banked)", "Meridian batteries are worth their weight.", 0, 0, [(23, 6, 2)], None), LEAVE]),
    ("ev_mer_scoring_terminal", "Scoring Terminal", 0, "A worker-scoring terminal shows a picker's score falling in real time.",
     [("Pad the score (5 damage, -2 Heat)", "The terminal fights back. The picker keeps her job.", 0, 5, [(21, 6, -2)], None),
      ("Copy the model (Card: Deep Strip)", "The model's weights make a fine resistance stripper.", 0, 0, [], C % "deep_strip"), LEAVE]),
    ("ev_mer_customs_bribe", "Customs Bribe", 2, "A Meridian customs clerk leans in. 'For twenty, your traffic is a diplomatic pouch.'",
     [("Pay the clerk (20 Cycles, -3 Heat)", "Your packets clear without inspection.", 20, 0, [(21, 6, -3)], None),
      ("Report the clerk (+1 Heat, +2 Schematics banked)", "Meridian rewards snitches, and remembers them.", 0, 0, [(21, 6, 1), (23, 6, 2)], None), LEAVE]),
    ("ev_mer_cold_chain", "Cold Chain Break", 0, "A refrigerated container reads CRITICAL. Inside: vaccines, warming by the minute.",
     [("Fix the cooler (Card: Firewall, 4 damage)", "Frost burns your fingers. The vaccines live.", 0, 4, [], C % "firewall"),
      ("Reroute it to the free clinic (-2 Heat)", "Somebody at the clinic gets a very cold surprise.", 0, 0, [(21, 6, -2)], None), LEAVE]),
    ("ev_mer_picker_chat", "The Group Chat", 1, "A warehouse picker waves you over. 'We know which cameras are fake. What do you know?'",
     [("Trade secrets (Daemon: Tuning Fork)", "She shows you a trick with the scanners.", 0, 0, [], D % "tuning_fork"),
      ("Give them the patch (+15 HP)", "They patch you up in the break room.", 0, 0, [(14, 0, 15)], None), LEAVE]),
    ("ev_mer_tracking_beacon", "Tracking Beacon", 0, "A Meridian tracker is stuck to your deck. It has been there since the last Rack.",
     [("Rip it off (3 damage, -2 Heat)", "It takes a layer of skin with it.", 0, 3, [(21, 6, -2)], None),
      ("Stick it on a Meridian van (Card: Double Jam)", "Now Meridian is tracking itself.", 0, 0, [], C % "double_jam"), LEAVE]),
    ("ev_mer_returns_desk", "Returns Desk", 0, "The returns desk accepts anything, no questions asked, for store credit.",
     [("Return junk (+20 Cycles)", "Store credit, converted at a questionable rate.", 0, 0, [(22, 6, 20)], None),
      ("Return a Bug (15 Cycles: Card: Scrap Code)", "They take the corrupted code and give you something useful.", 15, 0, [], C % "scrap_code"), LEAVE]),
    ("ev_mer_priority_lane", "Priority Lane", 2, "A priority freight lane runs straight through the node. Nothing in it is ever inspected.",
     [("Ride the lane (+30 Cycles, +3 Heat)", "Fast, rich and very visible.", 0, 0, [(22, 6, 30), (21, 6, 3)], None),
      ("Poison the lane (Firmware: Tracer)", "You slip a tracer into Meridian's own traffic.", 0, 0, [], F % "tracer"), LEAVE]),
    ("ev_mer_insurance_fraud", "Cargo Insurance", 2, "A cargo insurance claim for a shipment that was never sent. The payout is waiting.",
     [("Redirect the payout (+3 Schematics banked, +3 Heat)", "Meridian's insurers are very thorough, later.", 0, 0, [(23, 6, 3), (21, 6, 3)], None),
      ("Void the claim (-1 Heat)", "One less lie on the ledger.", 0, 0, [(21, 6, -1)], None), LEAVE]),
    ("ev_mer_night_depot", "Night Depot", 0, "A depot after hours. The robots are charging and the guards are asleep.",
     [("Take tools (Card: Bulwark)", "Heavy-duty and entirely boring.", 0, 0, [], C % "bulwark"),
      ("Take a robot's brain (Daemon: Idle Armor)", "It still wants to stand guard.", 0, 6, [], D % "idle_armor"), LEAVE]),
    ("ev_mer_manifest_glitch", "Manifest Glitch", 0, "A shipping manifest lists your safehouse as a Meridian warehouse. Somebody made a mistake.",
     [("Lean into it (+2 Schematics banked, +2 Heat)", "Free inventory arrives, with a tracking number.", 0, 0, [(23, 6, 2), (21, 6, 2)], None),
      ("Correct it quietly (-1 Heat)", "The error disappears. So do you.", 0, 0, [(21, 6, -1)], None), LEAVE]),
    ("ev_mer_convoy", "Convoy", 1, "A convoy of Meridian haulers idles at a red light that never turns green.",
     [("Hijack a hauler (+40 Cycles, 8 damage)", "The hauler fights like it was built to.", 0, 8, [(22, 6, 40)], None),
      ("Swap the light (Card: Cold Snap)", "The convoy freezes for an hour. So will others.", 0, 0, [], C % "cold_snap"), LEAVE]),
    ("ev_mer_dispatch_route", "DISPATCH: Route", 4, "DISPATCH: Route update received. Your next node is already cleared. Do not ask how.",
     [("Take the route (-2 Heat)", "DISPATCH: Acknowledged. You were expected.", 0, 0, [(21, 6, -2)], None),
      ("Ignore it (+1 Heat)", "DISPATCH: Understood. Proceed on your own schedule.", 0, 0, [(21, 6, 1)], None)]),
    ("ev_mer_ghost_order", "Ghost Order", 3, "A Meridian order screen refreshes: one shipment, destination your safehouse, sender unknown, paid in full.",
     [("Accept delivery (Daemon: Cascade)", "The box contains exactly what you needed. Nobody asked what you needed.", 0, 0, [], D % "cascade"),
      ("Refuse it (-1 Heat)", "The order cancels itself before you finish refusing.", 0, 0, [(21, 6, -1)], None)]),
    ("ev_mer_port_strike", "Port Strike", 1, "The dockers are on strike. Their picket line needs a network that Meridian cannot read.",
     [("Give them a channel (-2 Heat, 10 Cycles)", "The strike holds another day.", 10, 0, [(21, 6, -2)], None),
      ("Sell them a scanner (Asset: Sentry)", "They pay in hardware. Sturdy hardware.", 0, 0, [], A % "sentry"), LEAVE]),
    ("ev_mer_algorithm", "The Algorithm", 3, "A routing algorithm wants to renegotiate. It offers you a better route in exchange for a small favour.",
     [("Accept (Card: Gear Mesh, +2 Heat)", "The route is better. The favour is logged.", 0, 0, [(21, 6, 2)], C % "gear_mesh"),
      ("Decline (heal 5)", "It sulks. You feel better.", 0, 0, [(14, 0, 5)], None), LEAVE], CORP, 2),
    ("ev_mer_customs_warehouse", "Customs Warehouse", 0, "Seized goods, stacked to the ceiling. Some of it is still labelled with names.",
     [("Return what you can (-3 Heat, 6 damage)", "The alarms find you halfway through.", 0, 6, [(21, 6, -3)], None),
      ("Take the good stuff (+25 Cycles)", "Contraband sells.", 0, 0, [(22, 6, 25)], None), LEAVE], CORP, 2),
    ("ev_mer_billing_error", "Billing Error", 2, "Meridian's billing system has charged the whole block for a delivery that never came.",
     [("Refund everyone (15 Cycles, -3 Heat)", "The block gets its money back and the Cell gets its name back.", 15, 0, [(21, 6, -3)], None),
      ("Skim the refund (+30 Cycles, +2 Heat)", "Somebody has to take the fee.", 0, 0, [(22, 6, 30), (21, 6, 2)], None), LEAVE]),
]
event_paths = []
for ev in EVENTS:
    eid, title, speaker, text, choices = ev[:5]
    corp = ev[5] if len(ev) > 5 else CORP
    min_tier = ev[6] if len(ev) > 6 else 1
    er = Res("TerminalEventData", "res://scripts/data/terminal_event_data.gd")
    csubs = []
    for ci, (label, result, cyc, hp, effs, reward) in enumerate(choices):
        esubs = [er.effect("fx%d_%d" % (ci, i), t, tgt, amt) for i, (t, tgt, amt) in enumerate(effs)]
        fields = [("label", '"%s"' % label), ("result_text", '"%s"' % result)]
        if cyc:
            fields.append(("cycle_cost", cyc))
        if hp:
            fields.append(("hp_cost", hp))
        if esubs:
            fields.append(("effects", arr(er.script(S_EFFECT), esubs)))
        if reward:
            fields.append(("reward", er.res(reward)))
        csubs.append(er.sub("c%d" % ci, "res://scripts/data/event_choice_data.gd", fields))
    er.main = ['id = &"%s"' % eid, 'title = "%s"' % title, "speaker = %d" % speaker, 'text = "%s"' % text,
               "choices = " + arr(er.script("res://scripts/data/event_choice_data.gd"), csubs)]
    if corp:
        er.main.append('corporation_id = &"%s"' % corp)
    if min_tier > 1:
        er.main.append("min_tier = %d" % min_tier)
    if speaker == 4 or speaker == 3:
        er.main.append("dispatch_clue = true")
    er.write("content/events/%s.tres" % eid, "Meridian Terminal event (M8).")
    event_paths.append("res://content/events/%s.tres" % eid)

r.main = ['id = &"meridian"', 'display_name = "Meridian Freight Systems"',
          'description = "The logistics giant that moves everything, loses what it likes and bills you for the search."',
          "city_grid = " + grid,
          "enemies = " + arr(r.script("res://scripts/data/enemy_data.gd"), [r.res(EN(e)) for e in ENEMIES]),
          "elites = " + arr(r.script("res://scripts/data/enemy_data.gd"), [r.res(EN(e)) for e in ELITES]),
          "final_boss = " + r.res(EN("the_manifest")),
          "exploits = " + arr(r.script(S_EX), [ex_intel, ex_breach, ex_virus]),
          "story_paths = " + arr(r.script(S_PATH), path_refs),
          "raids = " + arr(r.script("res://scripts/data/raid_data.gd"), [r.res("res://content/raids/%s.tres" % x[0]) for x in RAIDS]),
          "events = " + arr(r.script("res://scripts/data/terminal_event_data.gd"), [r.res(p) for p in event_paths])]
r.write("content/corporations/meridian.tres",
        "Meridian Freight Systems (M8, GDD 8.4, DECISIONS 2026-09-24): 32-Site Grid mirroring Solace's shape\n"
        "(home -> ten T1 -> eight T2 with three Exploits -> eight T3 -> The Manifest), four Heat objectives,\n"
        "six story paths (Ghost Freight foreshadows DISPATCH, Civic Contract foreshadows Halcyon Civic).")

# ---- Voice ---------------------------------------------------------------------------------------------------------------
BRIEF = {
    "m1_a": "Parcel Sorting Hall. Every package in the district passes its belts. Cut the Rack and the belts stop for a shift.",
    "m1_b": "Customs Pre-Clearance. Meridian decides here what gets held. Take the Rack and nothing gets held today.",
    "m1_c": "Tracking Beacon Array. It knows where every van is, and where you are. Blind it.",
    "m1_d": "Returns Processing Centre. Where Meridian sends the things it does not want. Including people's claims.",
    "m1_e": "Drone Charging Yard. Four hundred drones on the pad. Take the Rack before they wake.",
    "m1_f": "Warehouse Shift Planner. It schedules the pickers down to the second. Give them a minute back.",
    "m1_g": "Address Verification Desk. Meridian decides who is allowed to exist at an address. Correct its records.",
    "m1_h": "Cold Chain Monitor. Every vaccine in the city reports here. Keep it cold and take the Rack.",
    "m1_i": "Tariff Calculation Office. Every fee Meridian charges starts in these tables. Make them round down.",
    "m1_j": "Fleet Telematics Hub. Speed, stops, driver heart rates. Meridian watches its own. Watch it back.",
    "m2_intel": "Shipping Manifest Vault. Every manifest Meridian ever filed. The truth is in the discrepancies. Bring back the Intel.",
    "m2_breach": "Customs Key Authority. The keys that open every sealed container. Take a copy. That is the Breach.",
    "m2_virus": "Routing Table Mirror. Meridian's map of the world. Poison it and the Manifest reads a lie. That is the Virus.",
    "m2_d": "Priority Lane Exchange. Where the rich buy speed. The Rack pays well.",
    "m2_e": "Worker Scoring Engine. It fires people for breathing. Take its Rack, and look for the audit path.",
    "m2_f": "Port Congestion Model. Meridian creates the queues it charges to skip. Break the model.",
    "m2_g": "Last-Mile Drone Command. It tells every drone where to look. Tell it to look away.",
    "m2_h": "Insurance Claims Ledger. Every lost parcel insured twice. Somebody collects. Take the Rack.",
    "m3_core": "Global Routing Core. One hop from the Manifest. Heavy security, heavier Rack.",
    "m3_b": "Freight Futures Desk. Meridian bets on shortages it is about to cause. Take the Rack.",
    "m3_c": "Customs Override Escrow. The master keys, in escrow for a very bad day. Today is that day.",
    "m3_d": "Supply Twin Simulator. A copy of the city's supply chain. Meridian rehearses its crises here.",
    "m3_e": "Board Logistics Backbone. The board's own delivery network. Private lanes, private cargo.",
    "m3_f": "Contract Pricing Authority. Where Meridian decides what a city pays to be fed. Take it.",
    "m3_g": "Surveillance Route Archive. Every drone flight ever flown, including over your safehouse. Burn it.",
    "m3_h": "Meridian Root Ledger. The signing keys for every transaction. The Manifest trusts it completely.",
    "lose_the_tracking": "Lose the Tracking. A quiet job: scrub the beacons that follow the Cell. Heat drops, nothing else changes.",
    "forge_the_manifest": "Forge the Manifest. Rewrite the Cell's traffic as routine freight. Heat drops.",
    "reroute_the_audit": "Reroute the Audit. Meridian's auditors are looking at you. Make them look somewhere else.",
    "sink_the_cargo_logs": "Sink the Cargo Logs. Every log that mentions the Cell, at the bottom of the harbour.",
    "the_manifest_site": "The Manifest. Every package on the planet passes through it. It shields itself every turn. Breach the Hub or pierce, and cut.",
}
DISPATCH_LINES = [
    ("run_start", "Jacking you in. Meridian logs everything; log nothing."), ("run_start", "Route is live. Keep it quiet and bank at the first Rack."),
    ("run_start", "Meridian traffic is heavy tonight. Good cover."),
    ("run_complete", "Clean exit. Meridian is recalculating a route that no longer exists."), ("run_complete", "Delivered. The Cell thanks you."),
    ("run_complete", "Package received. Well done."),
    ("run_died", "Signal lost. Meridian has marked the operative as returned to sender."), ("run_died", "We lost them. Regroup."),
    ("run_died", "Operative down. Their route ends here."),
    ("rack", "Rack captured. Bank it before Meridian notices the discrepancy."),
    ("threshold:25", "Meridian has flagged a delivery exception. Expect couriers."),
    ("threshold:50", "Route audit in progress. Meridian is counting your links."),
    ("threshold:75", "Freight seizure authorised. Haulers are rolling."),
    ("threshold:100", "Meridian is rerouting the city around the Cell. Everything is coming."),
    ("boss", "The Manifest. It shields itself every turn. Breach the Hub, then cut."),
    ("win", "The Manifest is down. For one day, the city moves itself."), ("win", "Meridian is offline. Deliveries are... improvising."),
    ("win", "Route closed. Next target when you are ready."),
    ("loss", "Home server lost. Meridian has reassigned the Cell's address."), ("loss", "We are off the map. Fall back."),
]
CORPO_LINES = [
    ("raid:any", "MERIDIAN LOGISTICS: Your address is under review. Please remain available for delivery."),
    ("raid:raid_heat_25", "MERIDIAN LOGISTICS: A delivery exception has been raised at your location. Couriers are en route."),
    ("raid:raid_heat_50", "MERIDIAN LOGISTICS: A route audit is in progress. Please do not obstruct our agents."),
    ("raid:raid_heat_75", "MERIDIAN LOGISTICS: Freight seizure has been authorised for your district. Thank you for your patience."),
    ("raid:raid_purge", "MERIDIAN LOGISTICS: Your district is being rerouted. Service will resume without you."),
    ("raid:raid_mer_claim", "MERIDIAN LOGISTICS: An unverified address has appeared on our network. Verification is under way."),
    ("raid:raid_mer_node_built", "MERIDIAN LOGISTICS: An unregistered depot has been detected. A Hauler has been scheduled."),
    ("raid:raid_mer_story", "MERIDIAN LOGISTICS: A shipment was taken in error. We are coming to collect it."),
    ("raid:raid_mer_retaliation", "MERIDIAN LOGISTICS: A chargeback has been filed against your account."),
]
S_LINE = "res://scripts/data/voice_line_data.gd"
for vid, speaker, lines in [("dispatch_meridian", 4, DISPATCH_LINES + [("site:%s" % k, v) for k, v in BRIEF.items()]),
                            ("corpo_meridian", 2, CORPO_LINES)]:
    vr = Res("LineSetData", "res://scripts/data/line_set_data.gd")
    subs = [vr.sub("l%d" % i, S_LINE, [("key", '"%s"' % k), ("text", '"%s"' % t)]) for i, (k, t) in enumerate(lines)]
    vr.main = ['id = &"%s"' % vid, "speaker = %d" % speaker, 'corporation_id = &"meridian"', "lines = " + arr(vr.script(S_LINE), subs)]
    vr.write("content/voice/%s.tres" % vid, "Meridian voice set (M8).")

# ---- Profile unlock --------------------------------------------------------------------------------------------------------
ur = Res("ProfileUnlockData", "res://scripts/data/profile_unlock_data.gd")
ur.main = ['id = &"unlock_meridian"', "kind = 2", 'display_name = "Corporation: Meridian Freight Systems"',
           'description = "Target Meridian Freight Systems in new campaigns."', "schematic_cost = 120",
           "unlocks = " + ur.res("res://content/corporations/meridian.tres")]
ur.write("content/unlocks/unlock_meridian.tres", "Corporation unlock (GDD 3.4; 120 Schematics, decision 2026-09-24). UnlockKind 2 = CORPORATION.")
print("MERIDIAN DONE: %d sites, %d events, %d paths" % (len(sites), len(EVENTS), len(PATHS)))
