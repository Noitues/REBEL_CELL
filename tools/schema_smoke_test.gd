extends SceneTree
## Schema smoke test. Run headless from the project root:
##   godot --headless --path . -s tools/schema_smoke_test.gd
## Exits with code 0 when every check passes.

func _init() -> void:
	var fails := _batch1() + _batch2() + _batch3()
	print("SCHEMA SMOKE TEST: ", "PASS" if fails == 0 else "FAIL (%d)" % fails)
	quit(0 if fails == 0 else 1)


func _mk_effect(t, target, amount := 0, scope := RC.RingScope.OUTER, mult := 1.0) -> EffectData:
	var e := EffectData.new()
	e.type = t; e.target = target; e.amount = amount; e.ring_scope = scope; e.multiplier = mult
	return e

func _batch1() -> int:
	var fails := 0
	# Slices
	var atk := SliceData.new(); atk.id = &"attack"; atk.slice_type = RC.SliceType.ATTACK; atk.base_output = 6
	var crit := SliceData.new(); crit.id = &"crit"; crit.slice_type = RC.SliceType.CRIT; crit.base_output = 12
	var def := SliceData.new(); def.id = &"defend"; def.slice_type = RC.SliceType.DEFEND; def.target_rule = RC.TargetRule.SELF; def.base_output = 5
	var miss := SliceData.new(); miss.id = &"miss"; miss.slice_type = RC.SliceType.MISS
	# Mirror firmware
	var mirror := FirmwareData.new(); mirror.id = &"mirror"; mirror.neighbor_rule = RC.NeighborRule.MIRROR
	var leech := FirmwareData.new(); leech.id = &"leech"
	leech.allowed_slice_types = [RC.SliceType.ATTACK]
	var t := TriggeredEffectData.new(); t.min_tier = RC.PrecisionTier.GOOD
	t.effects = [_mk_effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 1)]
	leech.triggered_effects = [t]
	# Breaker hub
	var hub := HubCoreData.new(); hub.id = &"breaker_core"
	var hook := TriggeredEffectData.new(); hook.trigger = RC.Trigger.ON_PERFECT
	hook.effects = [_mk_effect(RC.EffectType.RETRIGGER, RC.EffectTarget.SELF)]
	hub.perfect_hook = hook
	# Wheel
	var w := WheelData.new(); w.hub = hub
	var layout = [crit, atk, atk, atk, def, miss]
	var slots: Array[WheelSlotData] = []
	for s in layout:
		var sl := WheelSlotData.new(); sl.slice = s; slots.append(sl)
	slots[1].firmware = leech
	slots[4].firmware = leech   # should fail: leech only fits ATTACK
	w.slots = slots
	var errs := w.validate()
	print("Breaker wheel errors (expect 1): ", errs)
	if errs.size() != 1: fails += 1
	# Satellite wheel with 3 slices
	var sat := WheelData.new(); sat.slice_count = 3
	var sslots: Array[WheelSlotData] = []
	for s in [atk, def, atk]:
		var sl := WheelSlotData.new(); sl.slice = s; sslots.append(sl)
	sat.slots = sslots
	print("Satellite errors (expect 0): ", sat.validate(), " ticks/slice=", sat.ticks_per_slice())
	if sat.validate().size() != 0: fails += 1
	# Boss with 3 pointers, bad 4-slice
	var bad := WheelData.new(); bad.slice_count = 4
	print("4-slice errors (expect >=1): ", bad.validate())
	# Clean Signal daemon
	var cs := DaemonData.new(); cs.id = &"clean_signal"
	var ct := TriggeredEffectData.new(); ct.trigger = RC.Trigger.ON_PERFECT; ct.consecutive_required = 3
	ct.effects = [_mk_effect(RC.EffectType.MODIFY_HEAT, RC.EffectTarget.CAMPAIGN, -2)]
	cs.triggered_effects = [ct]
	print("Clean Signal errors (expect 0): ", ct.validate())
	# Bad effects
	var spin_bad := _mk_effect(RC.EffectType.SPIN, RC.EffectTarget.TARGET_WHEEL, 4)
	print("Spin on outer ring (expect 1): ", spin_bad.validate())
	if spin_bad.validate().size() != 1: fails += 1
	# Card
	var nudge := CardData.new(); nudge.id = &"nudge"
	nudge.effects = [_mk_effect(RC.EffectType.NUDGE, RC.EffectTarget.TARGET_WHEEL, 1, RC.RingScope.INNER)]
	print("Card errors (expect 0): ", nudge.validate())
	# Site
	var site := SiteData.new(); site.id = &"t2_a"; site.objective = RC.SiteObjective.HEAT_REDUCTION; site.heat_change = 5
	print("Site errors (expect 1): ", site.validate())
	# Save round trip
	var err := ResourceSaver.save(w, "user://smoke_breaker_wheel.tres")
	var loaded: WheelData = load("user://smoke_breaker_wheel.tres")
	print("Save=", err, " reload slots=", loaded.slots.size(), " slot1 fw=", loaded.slots[1].firmware.id)
	# Instantiate every schema
	for c in [NetworkNodeData, DefenseAssetData, ThreatData, InfiltrationNodeData, AdjacencyBonusData, RingSegmentData, InnerRingData]:
		c.new()
	return fails


func _slice(id, t, out, rule := RC.TargetRule.POINTER) -> SliceData:
	var s := SliceData.new(); s.id = id; s.slice_type = t; s.base_output = out; s.target_rule = rule
	return s

func _wheel(slices: Array, ptrs := PackedInt32Array([0])) -> WheelData:
	var w := WheelData.new(); w.slice_count = slices.size(); w.pointer_ticks = ptrs
	var slots: Array[WheelSlotData] = []
	for s in slices:
		var sl := WheelSlotData.new(); sl.slice = s; slots.append(sl)
	w.slots = slots
	return w

func _site(id, tier, links: Array[StringName], obj := RC.SiteObjective.NONE, ex := RC.ExploitType.NONE) -> SiteData:
	var s := SiteData.new(); s.id = id; s.tier = tier; s.links = links; s.objective = obj; s.exploit_type = ex
	return s

func _batch2() -> int:
	var fails := 0
	var atk := _slice(&"atk", RC.SliceType.ATTACK, 6)
	var def := _slice(&"def", RC.SliceType.DEFEND, 5, RC.TargetRule.SELF)
	var miss := _slice(&"miss", RC.SliceType.MISS, 0)
	var crit := _slice(&"crit", RC.SliceType.CRIT, 12)

	# Class
	var hub := HubCoreData.new(); hub.id = &"breaker_core"
	var hook := TriggeredEffectData.new(); hook.trigger = RC.Trigger.ON_PERFECT
	var re := EffectData.new(); re.type = RC.EffectType.RETRIGGER; re.target = RC.EffectTarget.SELF
	hook.effects = [re]; hub.perfect_hook = hook
	var cls := ClassData.new(); cls.id = &"breaker"
	cls.starting_wheel = _wheel([crit, atk, atk, atk, def, miss]); cls.starting_wheel.hub = hub
	var card := CardData.new(); card.id = &"spin"; cls.starting_deck = [card]
	var r1 := RankRewardData.new(); r1.rank = 1
	var r1b := RankRewardData.new(); r1b.rank = 1
	cls.rank_rewards = [r1, r1b]
	var ce := cls.validate(); print("Class (expect 1 dup rank): ", ce)
	if ce.size() != 1: fails += 1

	# Boss with satellites + phases (cyclic EnemyData <-> SatelliteSpawnData)
	var sat := EnemyData.new(); sat.id = &"drone"; sat.wheel = _wheel([atk, def, atk])
	var sp := SatelliteSpawnData.new(); sp.satellite = sat
	var p1 := BossPhaseData.new(); p1.hp_threshold_pct = 0.66; p1.pointer_behavior = RC.PointerBehavior.MULTIPLY; p1.pointer_ticks = PackedInt32Array([0, 15])
	var p2 := BossPhaseData.new(); p2.hp_threshold_pct = 0.33; p2.pointer_behavior = RC.PointerBehavior.ORBIT; p2.orbit_ticks_per_turn = 2
	var boss := EnemyData.new(); boss.id = &"renewal_engine"; boss.is_boss = true
	boss.wheel = _wheel([atk, atk, def, def, crit, miss]); boss.spawns = [sp]; boss.phases = [p1, p2]
	var be := boss.validate(); print("Boss (expect 0): ", be)
	if be.size() != 0: fails += 1
	boss.phases = [p2, p1]
	print("Boss wrong order (expect 1): ", boss.validate())

	# Grid: home, 3 chains, T3, boss. Also a bad T1 with two T2s.
	var sites: Array[SiteData] = [
		_site(&"home", 1, [&"a1", &"b1", &"c1"]),
		_site(&"a1", 1, [&"a2"]), _site(&"a2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.INTEL),
		_site(&"b1", 1, [&"b2"]), _site(&"b2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.BREACH),
		_site(&"c1", 1, [&"c2"]), _site(&"c2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.VIRUS),
		_site(&"t3", 3, [&"boss"]), _site(&"boss", 4, [], RC.SiteObjective.BOSS),
	]
	var grid := CityGridData.new(); grid.sites = sites; grid.home_site_id = &"home"; grid.boss_site_id = &"boss"
	var ge := grid.validate(); print("Grid (expect 0): ", ge, " warnings: ", grid.size_warnings())
	if ge.size() != 0: fails += 1
	sites[1].links = [&"a2", &"b2"]
	print("Grid T1 double (expect 1): ", grid.validate())
	sites[1].links = [&"a2"]
	sites[7].links = []  # cut t3 -> boss
	print("Grid unreachable (expect 1): ", grid.validate())
	sites[7].links = [&"boss"]

	# Story + corp
	var beat := StoryBeatData.new(); beat.id = &"b"
	var paths: Array[StoryPathData] = []
	for i in 5:
		var p := StoryPathData.new(); p.id = StringName("p%d" % i); p.beats = [beat, beat, beat]; p.finale = beat
		paths.append(p)
	var corp := CorporationData.new(); corp.id = &"solace"; corp.city_grid = grid; corp.final_boss = boss; corp.story_paths = paths
	boss.phases = [p1, p2]
	var coe := corp.validate(); print("Corp (expect 0): ", coe)
	if coe.size() != 0: fails += 1

	# Config
	var cfg := CampaignConfigData.new()
	var h1 := HeatThresholdData.new(); h1.heat = 25; h1.kind = RC.ThresholdKind.MAJOR
	var h2 := HeatThresholdData.new(); h2.heat = 10
	cfg.heat_thresholds = [h1, h2]
	print("Config wrong order (expect 1): ", cfg.validate())

	# Home server
	var core := NetworkNodeData.new(); core.node_type = RC.NetworkNodeType.HOME_SERVER
	var hs := HomeServerVariantData.new(); hs.id = &"std"; hs.core = core; hs.internal_nodes = [NetworkNodeData.new()]
	hs.internal_links = [Vector2i(0, 1), Vector2i(0, 5)]
	print("Home server (expect 1 bad link): ", hs.validate())

	# Save/load the whole corp graph
	var err := ResourceSaver.save(corp, "user://smoke_solace.tres")
	var loaded: CorporationData = load("user://smoke_solace.tres")
	print("Save=", err, " boss phases=", loaded.final_boss.phases.size(), " sat=", loaded.final_boss.spawns[0].satellite.id, " sites=", loaded.city_grid.sites.size())
	for c in [ExploitData, TerminalEventData, EventChoiceData, RaidData, RaidWaveData, RuleModifierData, IceLevelData, ProfileUnlockData, HeatGatedEffectData]:
		c.new()
	return fails


## M0: CampaignConfigData carries the whole of GDD Section 11 (shop, costs, RAM ranges).
func _batch3() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	var ce := cfg.validate(); print("Config defaults (expect 0): ", ce)
	if ce.size() != 0: fails += 1
	cfg.card_price_range = Vector2i(75, 50)
	cfg.node_upgrade_costs = PackedInt32Array()
	ce = cfg.validate(); print("Config bad range + empty upgrades (expect 2): ", ce)
	if ce.size() != 2: fails += 1
	var err := ResourceSaver.save(cfg, "user://smoke_config.tres")
	var loaded: CampaignConfigData = load("user://smoke_config.tres")
	print("Save=", err, " reload card_price_range=", loaded.card_price_range, " respin=", loaded.respin_ram_cost)
	if loaded.card_price_range != Vector2i(75, 50) or loaded.respin_ram_cost != 4: fails += 1
	return fails + _batch4()


## Vertical-slice fixes (2026-09-24): CardData.offered (Bug card), HubCoreData.drone
## (DEPLOY template), RankRewardData.ring_segment_options, WheelState migrations.
func _batch4() -> int:
	var fails := 0
	var bug := CardData.new(); bug.id = &"bug"; bug.offered = false; bug.exhaust = true
	bug.effects = [_mk_effect(RC.EffectType.DRAIN_RAM, RC.EffectTarget.SELF, 1)]
	print("Bug card (expect 0 errors, offered=false): ", bug.validate(), " ", bug.offered)
	if bug.validate().size() != 0 or bug.offered: fails += 1
	var atk := _slice(&"atk", RC.SliceType.ATTACK, 3)
	var def := _slice(&"def", RC.SliceType.DEFEND, 3, RC.TargetRule.SELF)
	var drone := EnemyData.new(); drone.id = &"drone"; drone.hp = 5; drone.wheel = _wheel([atk, def])
	var hub := HubCoreData.new(); hub.id = &"botnet_core"; hub.max_drones = 3; hub.drone = drone
	var seg := RingSegmentData.new(); seg.id = &"seg_echo"
	var r3 := RankRewardData.new(); r3.rank = 3; r3.ring_segment_options = [seg]
	var err := ResourceSaver.save(hub, "user://smoke_hub.tres")
	var loaded: HubCoreData = load("user://smoke_hub.tres")
	print("Hub save=", err, " drone=", loaded.drone.id, " max=", loaded.max_drones, " rank3 options=", r3.ring_segment_options.size())
	if err != OK or loaded.drone == null or loaded.max_drones != 3: fails += 1
	var w := WheelState.from_wheel_data(drone.wheel)
	w.pending_pointer_ticks = PackedInt32Array([5, 20])
	var back := WheelState.from_dict(w.to_dict())
	print("WheelState pending pointers round trip: ", back.pending_pointer_ticks)
	if back.pending_pointer_ticks != PackedInt32Array([5, 20]): fails += 1
	if not back.apply_pending_pointers() or back.pointer_ticks != PackedInt32Array([5, 20]): fails += 1
	return fails + _batch5()


## Vertical-slice fixes batch 2: NetrunBoostData, StoryBeatData.triggers_raid, GridState
## home-variant capacity and frozen links, CampaignState boosts/objectives/home variant.
func _batch5() -> int:
	var fails := 0
	var empty := NetrunBoostData.new(); empty.id = &"nothing"
	print("Empty boost (expect 1): ", empty.validate())
	if empty.validate().size() != 1: fails += 1
	var boost := NetrunBoostData.new(); boost.id = &"cache"; boost.cost = 10; boost.cycles = 40
	var cfg := CampaignConfigData.new(); cfg.netrun_boosts = [boost]
	print("Config with a 10-Schematic boost (expect 0): ", cfg.validate())
	if cfg.validate().size() != 0: fails += 1
	boost.cost = 99
	print("Config with a 99-Schematic boost (expect 1): ", cfg.validate())
	if cfg.validate().size() != 1: fails += 1
	var beat := StoryBeatData.new(); beat.id = &"b"; beat.triggers_raid = true
	var err := ResourceSaver.save(beat, "user://smoke_beat.tres")
	var loaded: StoryBeatData = load("user://smoke_beat.tres")
	print("Beat save=", err, " triggers_raid=", loaded.triggers_raid)
	if err != OK or not loaded.triggers_raid: fails += 1
	var g := GridState.new(); g.home_site_id = &"home"; g.home_asset_slots = 3; g.home_built_in = ["turret"]
	g.freeze_link(&"home", &"c1")
	var back := GridState.from_dict(g.to_dict())
	print("GridState round trip: slots=", back.home_asset_slots, " built_in=", back.home_built_in, " frozen=", back.is_link_frozen(&"c1", &"home"))
	if back.home_asset_slots != 3 or back.home_built_in != ["turret"] or not back.is_link_frozen(&"c1", &"home"): fails += 1
	var c := CampaignState.new(); c.pending_boosts = [&"cache"]; c.disabled_objectives = [&"scrub"]; c.home_variant_id = &"home_bunker"
	var cb := CampaignState.from_dict(c.to_dict())
	print("CampaignState round trip: ", cb.pending_boosts, cb.disabled_objectives, cb.home_variant_id)
	if cb.pending_boosts != [&"cache"] or cb.disabled_objectives != [&"scrub"] or cb.home_variant_id != &"home_bunker": fails += 1
	return fails
