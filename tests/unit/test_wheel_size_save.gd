extends GutTest
## Plan 2 N12 (save v4): wheels may carry uneven "slot_sizes" (and authored "slot_quality"),
## written only when not the equal layout so legacy wheels save and hash as before. A v3 save
## recorded on the pre-N12 build (tests/fixtures/saves/v3/) loads as equal 5-tick slots with
## the same state hash and resolves its End Turn to the same HP. A shop overwrite keeps the sum.

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")
const V3_FIXTURE := "res://tests/fixtures/saves/v3/v3_pre_n12.json"

var _saves: Node


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())


func _fixture() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(V3_FIXTURE))


func test_save_version_is_4() -> void:
	assert_eq(SaveServiceScript.SAVE_VERSION, 4)


func test_legacy_save_without_size_ticks_loads_as_5() -> void:
	var file := _fixture()
	assert_eq(int(file["version"]), 3, "recorded by the v3 build")
	var d: Dictionary = _saves.migrate(file)
	assert_eq(_saves.last_error, "")
	var s := CombatSession.from_dict(StatusSaveFixture.resolver(), StatusSaveFixture.session_dict(d))
	assert_eq(s.state.player.wheel.layout(), PackedInt32Array([5, 5, 5, 5, 5, 5]))
	assert_eq(str(s.state_hash()), String(file["expect_hash_before"]), "same hash as the v3 build")
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok())
	var want: Dictionary = file["expect_end_turn"]
	var got := StatusSaveFixture.hp_by_id(s.state)
	for id in want:
		assert_eq(int(got.get(id, -1)), int(want[id]), "%s HP after End Turn equals the v3 build's" % id)
	assert_eq(str(s.state_hash()), String(file["expect_hash_after"]))


func test_round_trip_variable_wheel_equal() -> void:
	var w := WheelFixtures.state(PackedInt32Array([6, 4, 0, 6, 4, 10]))
	var maps: Array[PackedInt32Array] = [PackedInt32Array(), PackedInt32Array([0, 2, 2, 0]), PackedInt32Array(), PackedInt32Array(), PackedInt32Array(), PackedInt32Array()]
	w.set_quality_maps(maps)
	w.rotation = 17
	var text := JSON.stringify({"version": 4, "run": {"combat": {"state": {"player": {"wheel": w.to_dict()}}}}})
	var d: Dictionary = _saves.migrate(JSON.parse_string(text))
	assert_eq(_saves.last_error, "")
	var back := WheelState.from_dict(d["run"]["combat"]["state"]["player"]["wheel"])
	assert_eq(back.to_dict(), w.to_dict())
	assert_eq(back.layout(), PackedInt32Array([6, 4, 0, 6, 4, 10]))
	assert_eq(back.quality_override(1), PackedInt32Array([0, 2, 2, 0]))


func test_equal_layout_writes_no_new_key() -> void:
	var w := WheelFixtures.state(PackedInt32Array([5, 5, 5, 5, 5, 5]))
	assert_false(w.to_dict().has("slot_sizes"), "legacy wheels hash as before")
	assert_false(w.to_dict().has("slot_quality"))


func test_broken_slot_sizes_refused() -> void:
	for bad in [[5, 5, 5, 5, 5, 4], [5, 5, 5, 5, 5], [35, -5, 0, 0, 0, 0], "x"]:
		var d := {"version": 4, "w": {"slot_slice_ids": ["a", "b", "c", "d", "e", "f"], "slot_sizes": bad}}
		assert_eq(_saves.migrate(d), {}, "%s" % [bad])
		assert_eq(_saves.last_error, SaveMigration.ERR_SLOT_SIZES)
		assert_push_error("invalid_slot_sizes")


func test_shop_overwrite_keeps_sum_30() -> void:
	var resolver := CombatFixture.resolver()
	var cfg := resolver.config
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	var s := NetrunSession.start(resolver, c, &"op_1", 1, &"t1_a", 11)
	s.run.phase = RunState.Phase.SHOP
	s.run.shop = {"slices": [String(cfg.shop_slices[0].id)]}
	s.run.cycles = 1000
	s.overwrite_slice(1, 0)
	assert_eq(s.run.operative.slot_slice_ids[1], cfg.shop_slices[0].id)
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var w := WheelState.from_wheel_data(cls.starting_wheel, null, s.run.operative.slot_slice_ids, s.run.operative.slot_firmware_ids)
	var total := 0
	for x in w.layout():
		total += x
	assert_eq(total, 30, "the slot keeps its size; only the slice changes")
	assert_eq(w.layout(), cls.starting_wheel.slot_sizes())
