"""Shared corporation generator (M9+). A corporation is a spec dict; build(spec) writes its
slices, satellite, enemies, threats, raids, corporation resource (grid, exploits, story
paths), events, voice sets and Profile unlock. Same schema and conventions as M8's
Meridian generator. Enum values: see gen_meridian.py / gen_pools.py headers."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_classes.py"), encoding="utf-8").read()
exec(_src[:_src.index("# ---- standalone ring segments")])

SL = lambda s: "res://content/slices/%s.tres" % s
EN = lambda e: "res://content/enemies/%s.tres" % e
TH = lambda t: "res://content/threats/%s.tres" % t
S_SLOT = "res://scripts/data/wheel_slot_data.gd"
S_WHEEL = "res://scripts/data/wheel_data.gd"
S_HUB = "res://scripts/data/hub_core_data.gd"
S_PHASE = "res://scripts/data/boss_phase_data.gd"
S_SPAWN = "res://scripts/data/satellite_spawn_data.gd"
S_SITE = "res://scripts/data/site_data.gd"
S_EX = "res://scripts/data/exploit_data.gd"
S_BEAT = "res://scripts/data/story_beat_data.gd"
S_PATH = "res://scripts/data/story_path_data.gd"
S_LINE = "res://scripts/data/voice_line_data.gd"
S_CHOICE = "res://scripts/data/event_choice_data.gd"


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


def hub_sub(r, hub):
    """hub = dict(id, name, desc, effects=[(type, target, amount)], trigger=2)."""
    subs = [r.effect("hfx%d" % i, t, tgt, amt) for i, (t, tgt, amt) in enumerate(hub["effects"])]
    te = r.te("hte", hub.get("trigger", 2), subs)
    return r.sub("hub_%s" % hub["id"], S_HUB, [("id", '&"%s"' % hub["id"]), ("display_name", '"%s"' % hub["name"]),
        ("description", '"%s"' % hub["desc"]), ("passive_effects", arr(r.script(S_TE), [te]))])


def enemy(corp, e):
    r = Res("EnemyData", "res://scripts/data/enemy_data.gd")
    hub_ref = hub_sub(r, e["hub"]) if e.get("hub") else None
    w = wheel_sub(r, "wheel", e["slices"], e.get("pointers", (0,)), e.get("passive", 0), e.get("orbit", 0), hub_ref)
    main = ['id = &"%s"' % e["id"], 'display_name = "%s"' % e["name"], 'description = "%s"' % e["desc"],
            'corporation_id = &"%s"' % corp, "hp = %d" % e["hp"], "wheel = " + w]
    for flag in ("elite", "boss", "mini"):
        if e.get(flag):
            main.append("is_%s = true" % {"elite": "elite", "boss": "boss", "mini": "mini_boss"}[flag])
    main.append("cycle_reward = %d" % e.get("cycle", 15))
    if e.get("spawns"):
        main.append("spawns = " + arr(r.script(S_SPAWN), [spawn_sub(r, "spawn%d" % i, *sp) for i, sp in enumerate(e["spawns"])]))
    if e.get("phases"):
        psubs = []
        for i, ph in enumerate(e["phases"]):
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
    r.write("content/enemies/%s.tres" % e["id"], e.get("comment", "%s enemy (decision 2026-09-24)." % corp))


def build(spec):
    corp = spec["id"]
    # Slices: (id, name, slice_type, target_rule, base_output, (effect type, target, amount, extra kw))
    for sid, name, stype, rule, out, fx in spec.get("slices", []):
        r = Res("SliceData", "res://scripts/data/slice_data.gd")
        kw = fx[3] if len(fx) > 3 else {}
        e = r.effect("fx", fx[0], fx[1], fx[2], **kw)
        te = r.te("te", 5, [e])
        r.main = ['id = &"%s"' % sid, 'display_name = "%s"' % name, "slice_type = %d" % stype, "target_rule = %d" % rule,
                  "base_output = %d" % out, "extra_effects = " + arr(r.script(S_TE), [te])]
        r.write("content/slices/%s.tres" % sid, "%s slice (decision 2026-09-24)." % corp)
    sat = spec["satellite"]
    r = Res("EnemyData", "res://scripts/data/enemy_data.gd")
    w = wheel_sub(r, "wheel", ["atk_3", "def_3"])
    r.main = ['id = &"%s"' % sat["id"], 'display_name = "%s"' % sat["name"], 'description = "%s"' % sat["desc"],
              'corporation_id = &"%s"' % corp, "hp = 5", "wheel = " + w, "cycle_reward = 0"]
    r.write("content/enemies/%s.tres" % sat["id"], "%s satellite (decision 2026-09-24)." % corp)
    for e in spec["enemies"] + spec["elites"] + [spec["mini_boss"], spec["boss"]]:
        enemy(corp, e)
    for tid, name, desc, integ, dmg, speed, routing, extra in spec["threats"]:
        r = Res("ThreatData", "res://scripts/data/threat_data.gd")
        r.main = ['id = &"%s"' % tid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "integrity = %d" % integ,
                  "damage = %d" % dmg, "edges_per_step = %d" % speed, "routing = %d" % routing] + extra
        r.write("content/threats/%s.tres" % tid, "%s threat (decision 2026-09-24)." % corp)
    for rid, name, src, reward, waves, replaces, warning in spec["raids"]:
        r = Res("RaidData", "res://scripts/data/raid_data.gd")
        wsubs = [r.sub("wave%d" % i, "res://scripts/data/raid_wave_data.gd",
                       [("threats", arr(r.script("res://scripts/data/threat_data.gd"), [r.res(TH(t)) for t in wave]))])
                 for i, wave in enumerate(waves)]
        r.main = ['id = &"%s"' % rid, 'display_name = "%s"' % name, "trigger_source = %d" % src,
                  "waves = " + arr(r.script("res://scripts/data/raid_wave_data.gd"), wsubs), "schematic_reward = %d" % reward,
                  'warning_text = "%s"' % warning, 'corporation_id = &"%s"' % corp]
        if replaces:
            r.main.append('replaces = &"%s"' % replaces)
        r.write("content/raids/%s.tres" % rid, "%s raid (decision 2026-09-24)." % corp)

    # Grid: home -> ten T1 -> eight T2 (Exploits) -> eight T3 -> boss; four Heat objectives.
    sites = []

    def site(sid, name, tier, links=(), locked=(), objective=0, exploit=0, heat=0, claimable=True, pos=(0, 0)):
        sites.append(dict(id=sid, name=name, tier=tier, links=list(links), locked=list(locked), objective=objective,
                          exploit=exploit, heat=heat, claimable=claimable, pos=pos))

    ys = lambda n, top=30, bottom=630: [round(top + (bottom - top) * i / max(1, n - 1)) for i in range(n)]
    T1, T2, T3, HEAT, BOSS_SITE, HOME = spec["t1"], spec["t2"], spec["t3"], spec["heat_sites"], spec["boss_site"], spec["home_site"]
    t1_y, t2_y, t3_y = ys(10), ys(8, 60, 600), ys(8, 60, 600)
    site(HOME, "Home Server", 1, links=[t[0] for t in T1], claimable=False, pos=(0, 330))
    for i, (sid, name) in enumerate(T1):
        links = [T2[min(i, 7)][0]] if i < 9 else []
        links += [h[0] for h in HEAT if h[4] == sid]
        locked = [T1[i + 1][0]] if i % 2 == 0 and i + 1 < len(T1) else []
        site(sid, name, 1, links=links, locked=locked, pos=(200, t1_y[i]))
    for i, (sid, name, ex) in enumerate(T2):
        links = [T3[i][0]] + [h[0] for h in HEAT if h[4] == sid]
        locked = [T2[i + 1][0]] if i % 2 == 0 and i + 1 < len(T2) else []
        site(sid, name, 2, links=links, locked=locked, objective=1 if ex else 0, exploit=ex, pos=(430, t2_y[i]))
    for i, (sid, name) in enumerate(T3):
        locked = [T3[i + 1][0]] if i % 2 == 0 and i + 1 < len(T3) else []
        site(sid, name, 3, links=[BOSS_SITE[0]], locked=locked, pos=(660, t3_y[i]))
    heat_pos = {1: [(330, 20), (330, 380)], 2: [(340, 650)], 3: [(560, 430)]}
    for sid, name, tier, change, _ in HEAT:
        site(sid, name, tier, objective=2, heat=change, pos=heat_pos[tier].pop(0))
    site(BOSS_SITE[0], BOSS_SITE[1], 4, objective=4, claimable=False, pos=(900, 330))

    r = Res("CorporationData", "res://scripts/data/corporation_data.gd")
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
        ("home_site_id", '&"%s"' % HOME), ("boss_site_id", '&"%s"' % BOSS_SITE[0])])
    xi, xb, xv = spec["exploit_names"]
    ex_intel = r.sub("ex_intel", S_EX, [("exploit_type", 1), ("display_name", '"%s"' % xi),
        ("description", '"Reveals the boss phases and pointer moves; opens locked Grid links."'), ("heat_cost", 10),
        ("reveals_boss_phases", "true"), ("opens_locked_links", "true")])
    ex_breach = r.sub("ex_breach", S_EX, [("exploit_type", 2), ("display_name", '"%s"' % xb),
        ("description", '"The boss starts with one fewer pointer."'), ("heat_cost", 10), ("removes_boss_pointers", 1)])
    fx_v = r.effect("fx_virus", 4, 2, 2, status=1, slice_pick=1)
    te_v = r.te("te_virus", 1, [fx_v])
    ex_virus = r.sub("ex_virus", S_EX, [("exploit_type", 3), ("display_name", '"%s"' % xv),
        ("description", '"The boss starts with CORRUPTED slices."'), ("heat_cost", 10),
        ("breach_effects", arr(r.script(S_TE), [te_v]))])
    path_refs = []
    for pid, title, premise, beats, bonus, finale, foreshadows, raid_beat in spec["paths"]:
        brefs = []
        for i, (bt, sp, tx) in enumerate(beats):
            fields = [("id", '&"%s_%d"' % (pid, i + 1)), ("title", '"%s"' % bt), ("speaker", sp), ("text", '"%s"' % tx)]
            if foreshadows == "dispatch":
                fields.append(("dispatch_clue", "true"))
            if raid_beat == i:
                fields.append(("triggers_raid", "true"))
            brefs.append(r.sub("b_%s_%d" % (pid, i + 1), S_BEAT, fields))
        bb = [r.sub("b_%s_bonus_%d" % (pid, i + 1), S_BEAT, [("id", '&"%s_bonus_%d"' % (pid, i + 1)), ("title", '"%s"' % bt),
                                                             ("speaker", sp), ("text", '"%s"' % tx)])
              for i, (bt, sp, tx) in enumerate(bonus)]
        fin = r.sub("b_%s_f" % pid, S_BEAT, [("id", '&"%s_f"' % pid), ("title", '"%s: Finale"' % title), ("text", '"%s"' % finale)])
        fields = [("id", '&"sp_%s"' % pid), ("title", '"%s"' % title), ("premise", '"%s"' % premise),
                  ("beats", arr(r.script(S_BEAT), brefs)), ("bonus_beats", arr(r.script(S_BEAT), bb)), ("finale", fin)]
        if foreshadows:
            fields.append(("foreshadows", '&"%s"' % foreshadows))
        path_refs.append(r.sub("sp_%s" % pid, S_PATH, fields))

    event_paths = []
    leave = ("Walk on", spec.get("leave_text", "You keep moving."), 0, 0, [], None)
    for ev in spec["events"]:
        eid, title, speaker, text, choices = ev[:5]
        min_tier = ev[5] if len(ev) > 5 else 1
        er = Res("TerminalEventData", "res://scripts/data/terminal_event_data.gd")
        csubs = []
        for ci, ch in enumerate(choices + ([leave] if speaker not in (3, 4) else [])):
            label, result, cyc, hp, effs, reward = ch
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
            csubs.append(er.sub("c%d" % ci, S_CHOICE, fields))
        er.main = ['id = &"%s"' % eid, 'title = "%s"' % title, "speaker = %d" % speaker, 'text = "%s"' % text,
                   "choices = " + arr(er.script(S_CHOICE), csubs), 'corporation_id = &"%s"' % corp]
        if min_tier > 1:
            er.main.append("min_tier = %d" % min_tier)
        if speaker in (3, 4):
            er.main.append("dispatch_clue = true")
        er.write("content/events/%s.tres" % eid, "%s Terminal event (decision 2026-09-24)." % corp)
        event_paths.append("res://content/events/%s.tres" % eid)

    r.main = ['id = &"%s"' % corp, 'display_name = "%s"' % spec["name"], 'description = "%s"' % spec["desc"],
              "city_grid = " + grid,
              "enemies = " + arr(r.script("res://scripts/data/enemy_data.gd"), [r.res(EN(e["id"])) for e in spec["enemies"]]),
              "elites = " + arr(r.script("res://scripts/data/enemy_data.gd"), [r.res(EN(e["id"])) for e in spec["elites"]]),
              "final_boss = " + r.res(EN(spec["boss"]["id"])),
              "exploits = " + arr(r.script(S_EX), [ex_intel, ex_breach, ex_virus]),
              "story_paths = " + arr(r.script(S_PATH), path_refs),
              "raids = " + arr(r.script("res://scripts/data/raid_data.gd"), [r.res("res://content/raids/%s.tres" % x[0]) for x in spec["raids"]]),
              "events = " + arr(r.script("res://scripts/data/terminal_event_data.gd"), [r.res(p) for p in event_paths])]
    r.write("content/corporations/%s.tres" % corp, spec["comment"])

    for vid, speaker, lines in [("dispatch_%s" % corp, 4, spec["dispatch"] + [("site:%s" % k, v) for k, v in spec["briefings"].items()]),
                                ("corpo_%s" % corp, 2, spec["corpo"])]:
        vr = Res("LineSetData", "res://scripts/data/line_set_data.gd")
        subs = [vr.sub("l%d" % i, S_LINE, [("key", '"%s"' % k), ("text", '"%s"' % t)]) for i, (k, t) in enumerate(lines)]
        vr.main = ['id = &"%s"' % vid, "speaker = %d" % speaker, 'corporation_id = &"%s"' % corp, "lines = " + arr(vr.script(S_LINE), subs)]
        vr.write("content/voice/%s.tres" % vid, "%s voice set (decision 2026-09-24)." % corp)

    ur = Res("ProfileUnlockData", "res://scripts/data/profile_unlock_data.gd")
    ur.main = ['id = &"unlock_%s"' % corp, "kind = 2", 'display_name = "Corporation: %s"' % spec["name"],
               'description = "Target %s in new campaigns."' % spec["name"], "schematic_cost = %d" % spec["unlock_cost"],
               "unlocks = " + ur.res("res://content/corporations/%s.tres" % corp)]
    ur.write("content/unlocks/unlock_%s.tres" % corp, "Corporation unlock (GDD 3.4; decision 2026-09-24). UnlockKind 2 = CORPORATION.")
    missing = [s["id"] for s in sites if s["id"] != HOME and s["id"] not in spec["briefings"]]
    assert not missing, "missing briefings: %s" % missing
    print("%s DONE: %d sites, %d events, %d paths" % (corp, len(sites), len(spec["events"]), len(spec["paths"])))
