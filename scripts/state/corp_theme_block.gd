class_name CorpThemeBlock
extends RefCounted
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): the base of every `corp_theme` sub-object (the
## campaign, netrun and raid blocks and one typed sub-object per corporation inside them).
## A block's fields are its script variables with their defaults. `to_dict` writes only the
## fields that differ from a fresh block's, so a block at its defaults writes {} and its owner
## leaves "corp_theme" out of the save: saves and state hashes made before WH-02 read and hash
## exactly as before. `load_dict` reads every field present and keeps the default for the rest
## (an older save loads as defaults; no save-version bump).
##
## Field types a block may use: int, bool, String, StringName, PackedInt32Array, typed Arrays
## and typed Dictionaries of those, Array[Dictionary] (whole-number floats read back as ints),
## a nested block that is never null, or a block that is null by default (the subclass builds
## it in `_new_child`). Encoded values are JSON-ready: StringNames as Strings, packed arrays
## as Arrays, nested blocks as their own `to_dict`.


## The block's field names in declaration order.
func fields() -> PackedStringArray:
	var out := PackedStringArray()
	for p in get_property_list():
		if int(p["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE:
			out.append(String(p["name"]))
	return out


## The fields that differ from their defaults, JSON-ready; {} when every field is default.
func to_dict() -> Dictionary:
	var fresh := _fresh()
	var out := {}
	for f in fields():
		var enc: Variant = _encode(get(f))
		var def: Variant = _encode(fresh.get(f))
		if typeof(enc) != typeof(def) or enc != def:
			out[f] = enc
	return out


## Whether every field holds its default (then the owner saves and hashes without the block).
func is_default() -> bool:
	return to_dict().is_empty()


## Reads the fields present in `d` (a `to_dict`, possibly after a JSON round trip: numbers as
## floats); absent fields keep their defaults. Unknown keys are ignored.
func load_dict(d: Dictionary) -> void:
	for f in fields():
		if not d.has(f):
			continue
		var cur: Variant = get(f)
		var v: Variant = d[f]
		if cur is CorpThemeBlock:
			if v is Dictionary:
				(cur as CorpThemeBlock).load_dict(v)
		elif cur == null:
			var child := _new_child(f)
			if child != null and v is Dictionary:
				child.load_dict(v)
				set(f, child)
		else:
			set(f, _decode(v, cur))


## A deep copy (through to_dict / load_dict).
func copy() -> CorpThemeBlock:
	var c := _fresh()
	c.load_dict(to_dict())
	return c


## The block a null-by-default field `field` holds once a save has it; null = the field is
## never filled from a save. Subclasses with such a field override this.
func _new_child(_field: String) -> CorpThemeBlock:
	return null


func _fresh() -> CorpThemeBlock:
	return (get_script() as Script).new()


static func _encode(v: Variant) -> Variant:
	if v is CorpThemeBlock:
		return (v as CorpThemeBlock).to_dict()
	if v is StringName:
		return String(v)
	if v is PackedInt32Array:
		var ints := []
		for n in v:
			ints.append(n)
		return ints
	if v is Array:
		var arr := []
		for e in v:
			arr.append(_encode(e))
		return arr
	if v is Dictionary:
		var dict := {}
		for k in v:
			dict[String(k)] = _encode(v[k])
		return dict
	return v


## `v` read back in the type of `template` (the field's current value, typed).
static func _decode(v: Variant, template: Variant) -> Variant:
	if template is PackedInt32Array:
		var p := PackedInt32Array()
		if v is Array:
			for e in v:
				p.append(int(e))
		return p
	if template is Array:
		var arr: Array = (template as Array).duplicate()
		arr.clear()
		if v is Array:
			var t := arr.get_typed_builtin()
			for e in v:
				arr.append(_coerce(e, t))
		return arr
	if template is Dictionary:
		var dict: Dictionary = (template as Dictionary).duplicate()
		dict.clear()
		if v is Dictionary:
			var kt := dict.get_typed_key_builtin()
			var vt := dict.get_typed_value_builtin()
			for k in v:
				dict[_coerce(k, kt)] = _coerce(v[k], vt)
		return dict
	return _coerce(v, typeof(template))


static func _coerce(v: Variant, t: int) -> Variant:
	match t:
		TYPE_INT:
			return int(v)
		TYPE_BOOL:
			return bool(v)
		TYPE_FLOAT:
			return float(v)
		TYPE_STRING:
			return String(v)
		TYPE_STRING_NAME:
			return StringName(String(v))
	return _norm(v)


## Untyped JSON values: whole-number floats back to ints, containers walked.
static func _norm(v: Variant) -> Variant:
	if v is float and float(v) == floorf(float(v)):
		return int(v)
	if v is Array:
		var arr := []
		for e in v:
			arr.append(_norm(e))
		return arr
	if v is Dictionary:
		var dict := {}
		for k in v:
			dict[String(k)] = _norm(v[k])
		return dict
	return v
