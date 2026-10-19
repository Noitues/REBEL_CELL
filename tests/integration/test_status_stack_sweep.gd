extends GutTest
## Plan 2 N8 sweep: 200 seeded real-content fights against status-applying enemies (Citation
## OUTPUT_DOWN x2, Dose CORRUPTED, Botnet parasites) replay to the same state hash turn by
## turn, and stacks of 2 or more do occur; every v2 fixture migrates and resumes.

const PAIRS: Array = [[&"breaker", &"parking_warden"], [&"botnet", &"parking_warden"],
	[&"breaker", &"dosage_dispenser"], [&"botnet", &"permit_office"]]
const SEEDS_PER_PAIR := 50
const FIRST_SEED := 1000
const TURNS := 6

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


## One scripted fight: each turn plays the first card it can, then ends the turn. Returns
## the hash after every turn and the largest stack count seen on any wheel.
func _fight(class_id: StringName, enemy: StringName, fight_seed: int) -> Dictionary:
	var s := CombatSession.start(_resolver, class_id, [enemy], fight_seed, &"rank:1")
	var hashes: Array = []
	var most := 0
	for turn in TURNS:
		if s.state.is_over():
			break
		var played := false
		for i in s.state.hand.size():
			for wheel_id in [s.state.target_id, &"player"]:
				var a := CombatAction.play_card(i, wheel_id)
				if not played and s.resolver.validate_action(s.state, a) == "":
					s.apply(a)
					played = true
			if played:
				break
		s.apply(CombatAction.end_turn())
		hashes.append(s.state_hash())
		for c in [s.state.player] + s.state.drones + s.state.enemies:
			if c == null or c.wheel == null:
				continue
			for d in c.wheel.slice_stacks:
				for st in d:
					most = maxi(most, int(d[st]))
	return {"hashes": hashes, "most": most}


func test_200_seed_fight_replay_hash_equal() -> void:
	var fights := 0
	var stacked := 0
	for pair in PAIRS:
		for k in SEEDS_PER_PAIR:
			var fight_seed := FIRST_SEED + k
			var a := _fight(pair[0], pair[1], fight_seed)
			var b := _fight(pair[0], pair[1], fight_seed)
			assert_eq(a["hashes"], b["hashes"], "%s vs %s seed %d replays" % [pair[0], pair[1], fight_seed])
			fights += 1
			if int(a["most"]) >= 2:
				stacked += 1
	assert_eq(fights, PAIRS.size() * SEEDS_PER_PAIR)
	assert_gt(stacked, 0, "some fights carry x2 or more (%d of %d)" % [stacked, fights])


func test_all_fixture_saves_migrate_and_resume() -> void:
	for f in StatusSaveFixture.FIXTURES:
		var file: Dictionary = SaveService.migrate(JSON.parse_string(FileAccess.get_file_as_string(StatusSaveFixture.FIXTURE_DIR + f + ".json")))
		assert_eq(SaveService.last_error, "", f)
		var s := CombatSession.from_dict(StatusSaveFixture.resolver(), StatusSaveFixture.session_dict(file))
		for turn in 3:
			if s.state.is_over():
				break
			assert_true(s.apply(CombatAction.end_turn()).ok(), "%s resumes (turn %d)" % [f, turn + 1])
		assert_eq(SaveMigration.validate_v3(CombatSession.from_dict(StatusSaveFixture.resolver(), s.to_dict()).to_dict()), "", "%s saves back as a sound v3" % f)
