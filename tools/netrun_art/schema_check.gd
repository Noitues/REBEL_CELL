extends RefCounted
## NA-02: checks a parsed contract file against its JSON Schema (tools/netrun_art/schemas/).
## A small subset of JSON Schema: type (string or list), const, enum, pattern, required,
## properties, additionalProperties (false or a schema), items, minItems, maxItems, plus one
## keyword of our own, `x-unique-by`: the array's items (objects) must differ in that property
## (the duplicate-id rule a plain schema cannot say). Godot's JSON parser returns every number
## as a float, so "integer" accepts a float with no fraction.

const SCHEMA_DIR := "res://tools/netrun_art/schemas/"


## The schema `name` ("city", "net", "run_graph", "key_locations", "derive").
static func schema(name: String) -> Dictionary:
	var f := FileAccess.open(SCHEMA_DIR + name + ".schema.json", FileAccess.READ)
	return JSON.parse_string(f.get_as_text()) if f != null else {}


## Problems of `obj` against `sch` (empty = valid).
static func validate(obj: Variant, sch: Dictionary, path: String = "$") -> PackedStringArray:
	var errs := PackedStringArray()
	if sch.has("type"):
		var names: Array = sch["type"] if sch["type"] is Array else [sch["type"]]
		var ok := false
		for n: String in names:
			ok = ok or _type_ok(obj, n)
		if not ok:
			errs.append("%s: expected %s, got %s" % [path, str(sch["type"]), type_string(typeof(obj))])
			return errs
	if sch.has("const") and not _same(obj, sch["const"]):
		errs.append("%s: expected %s" % [path, str(sch["const"])])
	if sch.has("enum"):
		var hit := false
		for e: Variant in sch["enum"]:
			hit = hit or _same(obj, e)
		if not hit:
			errs.append("%s: %s not in enum" % [path, str(obj)])
	if sch.has("pattern") and obj is String:
		var re := RegEx.create_from_string(sch["pattern"])
		if re.search(obj) == null:
			errs.append("%s: '%s' does not match %s" % [path, obj, sch["pattern"]])
	if obj is Dictionary:
		var props: Dictionary = sch.get("properties", {})
		for r: String in sch.get("required", []):
			if not obj.has(r):
				errs.append("%s: missing %s" % [path, r])
		var keys: Array = obj.keys()
		keys.sort()
		for k: Variant in keys:
			var sub := "%s.%s" % [path, k]
			if props.has(k):
				errs.append_array(validate(obj[k], props[k], sub))
			elif sch.has("additionalProperties"):
				var ap: Variant = sch["additionalProperties"]
				if ap is bool and not ap:
					errs.append("%s: unexpected key" % sub)
				elif ap is Dictionary:
					errs.append_array(validate(obj[k], ap, sub))
	if obj is Array:
		if sch.has("minItems") and obj.size() < int(sch["minItems"]):
			errs.append("%s: fewer than %d items" % [path, int(sch["minItems"])])
		if sch.has("maxItems") and obj.size() > int(sch["maxItems"]):
			errs.append("%s: more than %d items" % [path, int(sch["maxItems"])])
		if sch.has("items"):
			for i in obj.size():
				errs.append_array(validate(obj[i], sch["items"], "%s[%d]" % [path, i]))
		if sch.has("x-unique-by"):
			var seen := {}
			var key: String = sch["x-unique-by"]
			for i in obj.size():
				if obj[i] is Dictionary and obj[i].has(key):
					var v := str(obj[i][key])
					if seen.has(v):
						errs.append("%s[%d]: duplicate %s '%s'" % [path, i, key, v])
					seen[v] = true
	return errs


static func _type_ok(obj: Variant, name: String) -> bool:
	match name:
		"object":
			return obj is Dictionary
		"array":
			return obj is Array
		"string":
			return obj is String
		"boolean":
			return obj is bool
		"null":
			return obj == null
		"number":
			return obj is float or obj is int
		"integer":
			return obj is int or obj is float and is_finite(obj) and obj == floorf(obj)
	return false


static func _same(a: Variant, b: Variant) -> bool:
	if (a is float or a is int) and (b is float or b is int):
		return float(a) == float(b)
	return typeof(a) == typeof(b) and a == b
