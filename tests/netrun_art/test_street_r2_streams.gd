extends GutTest
## Street r2 art streams (P2-P4 step 1): the GDScript Mersenne Twister and the stream key text against the Python port
## (`tools/netrun_art/tests/fixtures/r2/{inputs,expected}/streams.json`, written by `gen_r2_fixtures.py`). Every draw kind the rules use
## (random, randrange, randint, uniform, choice, choices, sample) must match bit for bit; floats are compared as exact doubles.

const DIR := "res://tools/netrun_art/tests/fixtures/r2/"


func _json(path: String) -> Variant:
	return JSON.parse_string(FileAccess.get_file_as_string(DIR + path))


func _draw(r: StreetR2Rng, op: String) -> Variant:
	var p := op.split(":")
	match p[0]:
		"random":
			return r.random()
		"randrange":
			return r.randrange(int(p[1]))
		"randint":
			return r.randint(int(p[1]), int(p[2]))
		"uniform":
			return r.uniform(float(p[1]), float(p[2]))
		"choice":
			var a: Array = []
			for i in int(p[1]):
				a.append(i)
			return r.choice(a)
		"choices":
			var a: Array = []
			for i in int(p[1]):
				a.append(i)
			var w: Array = []
			for x in String(p[2]).split(","):
				w.append(float(x))
			return r.choices(a, w)
		"sample":
			var a: Array = []
			for i in int(p[1]):
				a.append(i)
			return r.sample(a, int(p[2]))
	return null


## "" when the draws match the expected ones (hex strings = exact doubles), else the first difference.
func _cmp_draws(r: StreetR2Rng, ops: Array, want: Array) -> String:
	for i in ops.size():
		var got: Variant = _draw(r, String(ops[i]))
		var w: Variant = want[i]
		if w is String:
			if got is float and NaFixture.hex_float(w) == got:
				continue
			return "draw %d (%s): got %s want %s" % [i, ops[i], got, w]
		if w is Array:
			var g: Array = got
			var ok := g.size() == (w as Array).size()
			for k in (w as Array).size() if ok else 0:
				ok = ok and int(w[k]) == int(g[k])
			if not ok:
				return "draw %d (%s): got %s want %s" % [i, ops[i], g, w]
			continue
		if not (got is int) or int(w) != got:
			return "draw %d (%s): got %s want %s" % [i, ops[i], got, w]
	return ""


func test_stream_keys_and_draws_match_python() -> void:
	var inp: Dictionary = NaFixture.decode(_json("inputs/streams.json"))
	var exp: Dictionary = _json("expected/streams.json")
	var rows: Array = exp["streams"]
	assert_eq(rows.size(), (inp["cases"] as Array).size())
	for i in (inp["cases"] as Array).size():
		var cs: Dictionary = inp["cases"][i]
		var seed: Variant = StreetR2Util.u64(cs["seed"]) if cs["seed_type"] == "int" else String(cs["seed"])
		var row: Dictionary = rows[i]
		var keys: Array = cs["keys"]
		assert_eq(StreetR2Rng.key_text(seed, cs["stream"], keys), row["key_text"], "case %d key text" % i)
		assert_eq(ArtSeed.u64_str(StreetR2Rng.art_seed(seed, cs["stream"], keys)), row["art_seed"], "case %d art seed" % i)
		var diff := _cmp_draws(StreetR2Rng.stream(seed, cs["stream"], keys), inp["ops"], row["draws"])
		assert_eq(diff, "", "case %d draws: %s" % [i, diff])


func test_raw_integer_seeds_match_python_random() -> void:
	var inp: Dictionary = NaFixture.decode(_json("inputs/streams.json"))
	var exp: Dictionary = _json("expected/streams.json")
	for i in (inp["raw"] as Array).size():
		var diff := _cmp_draws(StreetR2Rng.from_seed(StreetR2Util.u64(inp["raw"][i])), inp["ops"], exp["raw"][i]["draws"])
		assert_eq(diff, "", "raw seed %s: %s" % [inp["raw"][i], diff])


func test_py_round_is_half_even_and_float_key_text_is_the_python_repr() -> void:
	assert_eq(StreetR2Util.py_round(0.125, 2), 0.12)
	assert_eq(StreetR2Util.py_round(2.5, 0), 2.0)
	assert_eq(StreetR2Util.py_round(-2.5, 0), -2.0)
	assert_eq(StreetR2Util.py_round(0.7123, 3), 0.712)
	assert_eq(StreetR2Util.py_round0(3.5), 4)
	assert_eq(StreetR2Rng.py_repr_round(12.34567, 4), "12.3457")
	assert_eq(StreetR2Rng.py_repr_round(-30.0, 4), "-30.0")
	assert_eq(StreetR2Rng.py_repr_round(0.0001, 4), "0.0001")
	assert_eq(StreetR2Rng.py_repr_round(-0.00001, 4), "-0.0")
