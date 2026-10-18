extends GutTest
## NA-02 (spec §12.3.1; NA02_FIELDS.md section 7): ArtSeed matches the frozen FNV-1a 64
## vectors bit for bit (u64 printed unsigned), takes no RngService and touches no RNG, and a
## seed is independent of the order seeds are asked for.

const VECTORS := "res://tools/netrun_art/fixtures/na02_vectors.json"


func _vectors() -> Array:
	var f := FileAccess.open(VECTORS, FileAccess.READ)
	assert_not_null(f, "vectors fixture opens")
	return JSON.parse_string(f.get_as_text())


## JSON numbers come back as floats; the vector keys are ints or strings.
func _keys(raw: Array) -> Array:
	var out := []
	for k: Variant in raw:
		out.append(int(k) if typeof(k) == TYPE_FLOAT else k)
	return out


func test_all_vectors_match_bit_for_bit() -> void:
	var vs := _vectors()
	assert_eq(vs.size(), 14, "14 frozen vectors")
	for v: Dictionary in vs:
		var ls := ArtSeed.u64_from_str(v["layout_seed"])
		assert_eq(ArtSeed.u64_str(ls), v["layout_seed"], "u64 round trip")
		var got := ArtSeed.derive_str(ls, v["stream"], _keys(v["keys"]))
		assert_eq(got, v["seed"], "%s %s %s" % [v["layout_seed"], v["stream"], str(v["keys"])])


func test_signed_seeds_print_as_their_twos_complement() -> void:
	for v: Dictionary in _vectors():
		var signed := str(v["layout_seed_signed"])
		if not signed.begins_with("-"):
			continue
		# The signed seed (as CityModel.city_seed holds it) hashes like its u64 string.
		var s := ArtSeed.u64_from_str(v["layout_seed"])
		assert_true(s < 0, "a signed seed is negative as an int")
		assert_eq(ArtSeed.derive_str(s, v["stream"], _keys(v["keys"])), v["seed"])
	assert_eq(ArtSeed.u64_str(-1), "18446744073709551615")
	assert_eq(ArtSeed.u64_str(-9223372036854775807 - 1), "9223372036854775808")
	assert_eq(ArtSeed.u64_str(-424242), "18446744073709127374")


func test_splitmix_draws_match_the_vectors() -> void:
	for v: Dictionary in _vectors():
		var state := ArtSeed.u64_from_str(v["seed"])
		var draws: Array = v["splitmix64_first3"]
		var first := 0
		for i in 3:
			var nx := ArtSeed.splitmix64(state)
			state = nx[0]
			if i == 0:
				first = nx[1]
			assert_eq(ArtSeed.u64_str(nx[1]), draws[i], "draw %d of %s" % [i, v["seed"]])
		assert_almost_eq(ArtSeed.uniform(first), float(v["uniform_first"]), 1e-11)


func test_json_quote_is_ensure_ascii() -> void:
	assert_eq(ArtSeed.json_quote("été"), "\"\\u00e9t\\u00e9\"")
	assert_eq(ArtSeed.json_quote("a\"b\\c\n"), "\"a\\\"b\\\\c\\n\"")
	assert_eq(ArtSeed.json_quote(String.chr(0x1f600)), "\"\\ud83d\\ude00\"")


func test_derive_reads_no_rng_stream() -> void:
	RngService.seed_campaign(4242)
	var before := RngService.to_dict()
	seed(99)
	var expect := randi()
	seed(99)
	for v: Dictionary in _vectors():
		ArtSeed.derive(ArtSeed.u64_from_str(v["layout_seed"]), v["stream"], _keys(v["keys"]))
	assert_eq(randi(), expect, "the global RNG is not advanced")
	assert_eq(RngService.to_dict(), before, "no RngService stream is read or advanced")
	# derive takes no RngService / RandomNumberGenerator parameter.
	for m: Dictionary in ArtSeed.new().get_script().get_script_method_list():
		if m["name"] == "derive":
			for a: Dictionary in m["args"]:
				assert_ne(a["class_name"], &"RandomNumberGenerator")
				assert_ne(a["class_name"], &"RngStreams")


func test_seed_is_independent_of_call_order() -> void:
	var inputs := []
	for i in 40:
		inputs.append([i * 7919 - 100, "building", ["%d:%d" % [i, -i]]])
		inputs.append([i, "lanes_tile", [i, i * 3]])
	var forward := {}
	for inp: Array in inputs:
		forward[str(inp)] = ArtSeed.derive(inp[0], inp[1], inp[2])
	var shuffled := inputs.duplicate()
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for i in range(shuffled.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var t: Variant = shuffled[i]
		shuffled[i] = shuffled[j]
		shuffled[j] = t
	for inp: Array in shuffled:
		assert_eq(ArtSeed.derive(inp[0], inp[1], inp[2]), forward[str(inp)], str(inp))
