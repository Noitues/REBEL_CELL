extends GutTest
## RG-02: the REST node. Placement (v2 graphs only, config weights), PATCH heal from config with
## preview == result, REWIRE only between legal Firmware slots (a swap never leaves a Firmware
## unslotted), UNDO, one mode per visit, save/load round trip of the open page, and no stream read.

const FIRMWARE := [&"leech", &"mirror", &"burner", &"power_cell", &"bulkhead", &"overvolt", &"hardened", &"shunt"]

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"meridian") as CorporationData


func _gen(seed: int, tier: int, v2: bool = true) -> MapGraph:
	return MapGenerator.generate(tier, _cfg, RngStreams.make_stream(seed, &"map"), 0.0, v2)


func _count(g: MapGraph, type: int) -> int:
	var n := 0
	for node in g.all_nodes():
		if int(node["type"]) == type:
			n += 1
	return n


## A started run standing on a REST page (a layer-1 node turned REST, then entered).
func _rest_session(seed: int = 5) -> NetrunSession:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"m1_a", seed, _corp)
	var first := s.available_nodes()[0]
	s.run.map.get_node(first)["type"] = RC.InfilNodeType.REST
	s.enter_node(first)
	return s


func test_every_v2_map_has_a_rest_in_the_guaranteed_layers_and_v1_has_none() -> void:
	for seed in 300:
		var tier := 1 + seed % 4
		var g := _gen(seed, tier)
		var rests: Array = []
		for node in g.all_nodes():
			if int(node["type"]) == RC.InfilNodeType.REST:
				rests.append(int(node["layer"]))
		assert_true(rests.size() >= 1 and rests.size() <= _cfg.rest_max_per_run, "seed %d: %s" % [seed, rests])
		var uniq := {}
		for l in rests:
			uniq[l] = true
		assert_eq(uniq.size(), rests.size(), "never two RESTs in a layer")
		if tier == 1:
			assert_eq(rests.size(), 1, "tier 1 has no extra REST (config 0 percent)")
		assert_eq(_count(_gen(seed, tier, false), RC.InfilNodeType.REST), 0, "a v1 map has none")


func test_the_v2_pass_leaves_the_v1_map_alone() -> void:
	for seed in 60:
		var a := _gen(seed, 2, false)
		var b := _gen(seed, 2, true)
		for node in a.all_nodes():
			var m := b.get_node(node["id"])
			assert_eq(m["next"], node["next"])
			assert_eq(m["elite"], node["elite"])
			if int(m["type"]) != RC.InfilNodeType.REST:
				assert_eq(m["type"], node["type"])


func test_weight_zero_places_no_rest() -> void:
	var cfg := _cfg.duplicate() as CampaignConfigData
	cfg.node_weight_rest = 0
	cfg.rest_extra_chance_pct_by_tier = PackedInt32Array([0, 0, 0, 0])
	for seed in 30:
		assert_eq(_count(MapGenerator.generate(3, cfg, RngStreams.make_stream(seed, &"map"), 0.0, true), RC.InfilNodeType.REST), 0)


func test_patch_heals_the_configured_share_and_preview_equals_result() -> void:
	var s := _rest_session()
	assert_eq(s.run.phase, RunState.Phase.REST)
	var op := s.run.operative
	for hp in [1, op.max_hp / 2, op.max_hp - 3, op.max_hp]:
		op.hp = hp
		s.run.node_state["done"] = false
		var pv := s.rest_patch_preview()
		var before := s.run.operative.hp
		s.rest_patch()
		assert_eq(s.run.operative.hp, int(pv["hp_after"]), "preview == result at %d HP" % hp)
		assert_lte(s.run.operative.hp, op.max_hp)
		assert_eq(int(pv["heal"]), mini((op.max_hp * _cfg.rest_heal_pct + 50) / 100, op.max_hp - before))
		s.rest_undo()
		assert_eq(s.run.operative.hp, before, "undo restores HP")


func test_one_mode_per_visit_and_leave_returns_to_the_map() -> void:
	var s := _rest_session()
	s.run.operative.hp = 1
	s.rest_patch()
	assert_true(s.rest_done())
	var hp := s.run.operative.hp
	s.rest_patch()
	assert_eq(s.run.operative.hp, hp, "a second PATCH is refused")
	assert_ne(s.rest_error(), "")
	s.leave_rest()
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_true(s.run.node_state.is_empty())


func _fill(s: NetrunSession, rng: RandomNumberGenerator) -> void:
	var op := s.run.operative
	for i in op.slot_firmware_ids.size():
		op.slot_firmware_ids[i] = &""
	var pool: Array = FIRMWARE.duplicate()
	var n := rng.randi_range(1, mini(3, op.slot_firmware_ids.size()))
	for k in n:
		var fw: StringName = pool.pop_at(rng.randi_range(0, pool.size() - 1))
		var slot := rng.randi_range(0, op.slot_firmware_ids.size() - 1)
		if op.slot_firmware_ids[slot] == &"" and s.firmware_slot_error(fw, slot) == "":
			op.slot_firmware_ids[slot] = fw


func _held(ids: Array[StringName]) -> Array:
	var out: Array = []
	for id in ids:
		if id != &"":
			out.append(String(id))
	out.sort()
	return out


func test_a_swap_never_leaves_a_firmware_unslotted_or_in_an_illegal_slot() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 77
	var legal_swaps := 0
	var refused := 0
	for trial in 40:
		var s := _rest_session(trial + 1)
		_fill(s, rng)
		var op := s.run.operative
		var n := op.slot_slice_ids.size()
		for a in n:
			for b in n:
				s.run.node_state["done"] = false
				var before := op.slot_firmware_ids.duplicate()
				var err := s.rest_rewire_error(a, b)
				var pv := s.rest_rewire_preview(a, b)
				s.rest_rewire(a, b)
				if err != "":
					refused += 1
					assert_eq(op.slot_firmware_ids, before, "a refused swap changes nothing")
					continue
				legal_swaps += 1
				assert_eq(op.slot_firmware_ids, pv, "preview == result")
				assert_eq(_held(op.slot_firmware_ids), _held(before), "the same chips are slotted")
				for i in n:
					if op.slot_firmware_ids[i] != &"":
						assert_eq(s.firmware_slot_error(op.slot_firmware_ids[i], i), "", "every chip sits in a legal slot")
				s.rest_undo()
				assert_eq(op.slot_firmware_ids, before, "undo restores the layout")
	assert_gt(legal_swaps, 20, "the sweep saw legal swaps")
	assert_gt(refused, 20, "and refused ones")


func test_an_incompatible_swap_is_refused_with_a_reason() -> void:
	var s := _rest_session()
	var op := s.run.operative
	var leech := _lookup.get_content(&"leech") as FirmwareData
	if leech == null or leech.allowed_slice_types.is_empty():
		pending("leech has no slice restriction here")
		return
	var ok := -1
	var bad := -1
	for i in op.slot_slice_ids.size():
		if s.firmware_slot_error(&"leech", i) == "":
			ok = i
		else:
			bad = i
	if ok < 0 or bad < 0:
		pending("the starting wheel has no illegal slot for leech")
		return
	for i in op.slot_firmware_ids.size():
		op.slot_firmware_ids[i] = &""
	op.slot_firmware_ids[ok] = &"leech"
	assert_ne(s.rest_rewire_error(ok, bad), "")
	assert_eq(s.rest_rewire_error(ok, ok), "Choose two different wheel slots.")


func test_the_open_page_survives_a_save_and_reads_no_stream() -> void:
	var s := _rest_session()
	var streams_before := s.run.streams.duplicate(true)
	s.run.operative.hp = 2
	s.rest_patch()
	var hash_before := s.state_hash()
	var back := NetrunSession.from_dict(_resolver, s.campaign, s.to_dict(), _corp)
	assert_eq(back.state_hash(), hash_before, "the REST page round trips")
	assert_true(back.rest_done())
	back.rest_undo()
	assert_eq(back.run.operative.hp, 2)
	assert_eq(s.run.streams, streams_before, "no stream state moved")
