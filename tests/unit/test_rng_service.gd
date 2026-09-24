extends GutTest
## RngService: same seed -> same sequences; streams are independent (M0 acceptance).

const RngServiceScript := preload("res://scripts/autoload/rng_service.gd")
const SEED := 20260924
const DRAWS := 64


func _new_service(campaign_seed: int) -> Node:
	var service: Node = autofree(RngServiceScript.new())
	service.seed_campaign(campaign_seed)
	return service


func _draw(rng: RandomNumberGenerator, count: int) -> PackedInt64Array:
	var out := PackedInt64Array()
	for i in count:
		out.append(rng.randi())
	return out


func test_service_is_unseeded_until_seed_campaign() -> void:
	var service: Node = autofree(RngServiceScript.new())
	assert_false(service.is_seeded())
	service.seed_campaign(SEED)
	assert_true(service.is_seeded())


func test_every_named_stream_exists_after_seeding() -> void:
	var service := _new_service(SEED)
	for stream_name in RngServiceScript.STREAM_NAMES:
		assert_not_null(service.get_stream(stream_name), "stream %s" % stream_name)


func test_same_seed_gives_same_sequence_on_every_stream() -> void:
	var a := _new_service(SEED)
	var b := _new_service(SEED)
	for stream_name in RngServiceScript.STREAM_NAMES:
		assert_eq(_draw(a.get_stream(stream_name), DRAWS), _draw(b.get_stream(stream_name), DRAWS),
			"stream %s" % stream_name)


func test_different_seeds_give_different_sequences() -> void:
	var a := _new_service(SEED)
	var b := _new_service(SEED + 1)
	assert_ne(_draw(a.get_stream(&"map"), DRAWS), _draw(b.get_stream(&"map"), DRAWS))


func test_stream_seeds_differ_per_name() -> void:
	var seen := {}
	for stream_name in RngServiceScript.STREAM_NAMES:
		seen[RngServiceScript.derive_seed(SEED, stream_name)] = true
	assert_eq(seen.size(), RngServiceScript.STREAM_NAMES.size(), "each stream gets its own seed")


func test_streams_produce_different_sequences_from_each_other() -> void:
	var service := _new_service(SEED)
	var seen := {}
	for stream_name in RngServiceScript.STREAM_NAMES:
		seen[_draw(service.get_stream(stream_name), DRAWS)] = true
	assert_eq(seen.size(), RngServiceScript.STREAM_NAMES.size(), "no two streams share a sequence")


func test_drawing_from_other_streams_never_changes_a_stream() -> void:
	var untouched := _new_service(SEED)
	var expected := _draw(untouched.get_stream(&"map"), DRAWS)
	var busy := _new_service(SEED)
	for stream_name in RngServiceScript.STREAM_NAMES:
		if stream_name != &"map":
			_draw(busy.get_stream(stream_name), 500)
	assert_eq(_draw(busy.get_stream(&"map"), DRAWS), expected, "map stream unaffected by other streams")


func test_reseeding_restarts_every_stream() -> void:
	var service := _new_service(SEED)
	var first := _draw(service.get_stream(&"combat"), DRAWS)
	_draw(service.get_stream(&"combat"), 17)
	service.seed_campaign(SEED)
	assert_eq(_draw(service.get_stream(&"combat"), DRAWS), first)


func test_stream_state_snapshot_restores_the_sequence() -> void:
	var service := _new_service(SEED)
	_draw(service.get_stream(&"combat"), 10)
	var snapshot: int = service.get_stream_state(&"combat")
	var expected := _draw(service.get_stream(&"combat"), DRAWS)
	service.set_stream_state(&"combat", snapshot)
	assert_eq(_draw(service.get_stream(&"combat"), DRAWS), expected)


func test_restoring_combat_stream_leaves_other_streams_alone() -> void:
	var service := _new_service(SEED)
	var snapshot: int = service.get_stream_state(&"combat")
	_draw(service.get_stream(&"combat"), 10)
	var reference := _new_service(SEED)
	_draw(reference.get_stream(&"rewards"), 3)
	_draw(service.get_stream(&"rewards"), 3)
	service.set_stream_state(&"combat", snapshot)
	assert_eq(_draw(service.get_stream(&"rewards"), DRAWS), _draw(reference.get_stream(&"rewards"), DRAWS))


func test_to_dict_from_dict_round_trip_through_json() -> void:
	var a := _new_service(SEED)
	for stream_name in RngServiceScript.STREAM_NAMES:
		_draw(a.get_stream(stream_name), 7)
	var json := JSON.stringify(a.to_dict())
	var b: Node = autofree(RngServiceScript.new())
	b.from_dict(JSON.parse_string(json))
	assert_eq(b.campaign_seed, SEED)
	for stream_name in RngServiceScript.STREAM_NAMES:
		assert_eq(_draw(b.get_stream(stream_name), DRAWS), _draw(a.get_stream(stream_name), DRAWS),
			"stream %s continues after round trip" % stream_name)
