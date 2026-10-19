class_name NaFixture
extends RefCounted
## Test helper (NA-21): reads the Python oracle's parity fixtures (`tools/netrun_art/tests/fixtures/`).
## Inputs (`inputs/<seed>.json`) hold every float as `"~<hex>"` (Python `float.hex()` with the zero tail trimmed) so the
## doubles are rebuilt exactly; JSON integers are ints. Expected outputs (`expected/<seed>_{street,hq}_{derive,poses}.json`,
## `<seed>_street_dress.json`) are the canonical contract text, compared as text. `first_diff` names the first differing path.

const DIR := "res://tools/netrun_art/tests/fixtures/"
## The 12 fixture seeds (`gen_fixtures.SEEDS`).
const SEEDS: Array[String] = ["101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112"]


## The decoded inputs of one seed (`seed`, `site`, `corp`, `city`, `net`, `run_graph`, `partial_street`, `partial_hq`).
static func load_inputs(seed_name: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DIR + "inputs/%s.json" % seed_name))
	return decode(parsed)


## The expected canonical text `expected/<seed>_<kind>.json` (kind: street_derive, hq_derive, street_poses, hq_poses, street_dress).
static func expected_text(seed_name: String, kind: String) -> String:
	return FileAccess.get_file_as_string(DIR + "expected/%s_%s.json" % [seed_name, kind])


## Recursively turns `"~hex"` strings into floats and whole JSON numbers into ints.
static func decode(v: Variant) -> Variant:
	if v is String and String(v).begins_with("~"):
		return hex_float(String(v))
	if v is float:
		return int(v)
	if v is Array:
		var out: Array = []
		for e: Variant in v:
			out.append(decode(e))
		return out
	if v is Dictionary:
		var d: Dictionary = {}
		for k: Variant in v:
			d[k] = decode(v[k])
		return d
	return v


## The double of `"~[-]0x<int>.<frac>p<exp>"` (Python `float.hex()` form), built from exact integer and power-of-two parts.
static func hex_float(s: String) -> float:
	var t := s.substr(1)
	var neg := t.begins_with("-")
	if neg:
		t = t.substr(1)
	t = t.substr(2)  # 0x
	var p := t.find("p")
	var mant_txt := t.substr(0, p)
	var e := int(t.substr(p + 1))
	var dot := mant_txt.find(".")
	var int_txt := mant_txt if dot < 0 else mant_txt.substr(0, dot)
	var frac_txt := "" if dot < 0 else mant_txt.substr(dot + 1)
	var mant := ("0x" + int_txt + frac_txt).hex_to_int()
	var v := float(mant) * pow(2.0, float(e - 4 * frac_txt.length()))
	return -v if neg else v


## "" when both texts are equal, else a line naming the first differing JSON path (parsed values) or the first differing byte.
static func first_diff(got: String, want: String) -> String:
	if got == want:
		return ""
	var a: Variant = JSON.parse_string(got)
	var b: Variant = JSON.parse_string(want)
	var path := _diff(a, b, "$")
	if path != "":
		return path
	var n := mini(got.length(), want.length())
	for i in n:
		if got[i] != want[i]:
			return "text differs at char %d: %s | %s" % [i, got.substr(maxi(0, i - 30), 60), want.substr(maxi(0, i - 30), 60)]
	return "text length %d vs %d" % [got.length(), want.length()]


static func _diff(a: Variant, b: Variant, path: String) -> String:
	if a is Dictionary and b is Dictionary:
		var keys: Array = (b as Dictionary).keys()
		IdSort.sort_ids(keys)
		for k: Variant in keys:
			if not (a as Dictionary).has(k):
				return "%s.%s missing in the twin output" % [path, str(k)]
			var r := _diff(a[k], b[k], "%s.%s" % [path, str(k)])
			if r != "":
				return r
		for k: Variant in (a as Dictionary).keys():
			if not (b as Dictionary).has(k):
				return "%s.%s extra in the twin output" % [path, str(k)]
		return ""
	if a is Array and b is Array:
		if (a as Array).size() != (b as Array).size():
			return "%s length %d vs %d" % [path, (a as Array).size(), (b as Array).size()]
		for i in (a as Array).size():
			var r := _diff(a[i], b[i], "%s[%d]" % [path, i])
			if r != "":
				return r
		return ""
	if typeof(a) == typeof(b) and a == b:
		return ""
	return "%s: twin %s vs python %s" % [path, str(a), str(b)]
