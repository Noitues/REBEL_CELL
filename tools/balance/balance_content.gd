extends RefCounted
## BalanceContent (docs/handoff/plan2/BALANCE_SIM.md S1): a sim-local copy of the whole content
## graph with data overrides applied to the COPIES only. The loaded Resources (the
## ContentRegistry's, which are the files) are never written to (CLAUDE.md rule 3): the copier
## walks every resource reachable from the registry once, keeps shared references shared (one
## copy per original, memoised by instance id) and the overrides then edit those copies.
##   --set <id>.<prop>[.<prop|index>...]=<json>   assign       e.g. config.heat_max=120  or  ground_control.hp=40
##   --set <path>*=<number>                       multiply     e.g. config.target_turns_per_phase*=1.1
##   --set <path>+=<number>                       add          (ints stay ints; Vector2i and Packed*Array int lists element-wise)
## `config` (or `campaign_config`) is the CampaignConfigData. Lists and Vector2i take JSON arrays.
## Pure tooling: no autoloads, no RNG, no files written.

## Original resource instance id -> its copy.
var _copies: Dictionary = {}
## Content id -> copy (what the lookup is built from).
var _by_id: Dictionary = {}
var config: CampaignConfigData = null
var lookup: ContentLookup = null
## The override strings applied, in order (recorded in every report).
var applied: PackedStringArray = PackedStringArray()


## Copies `registry` (anything with all_ids() / get_content(), plus `config`).
func _init(registry: Object) -> void:
	for id in registry.all_ids():
		var res: Resource = registry.get_content(id)
		_by_id[id] = _copy_of(res)
	config = _copy_of(registry.config) as CampaignConfigData
	lookup = ContentLookup.new().add_registry(_Adapter.new(_by_id))


## The copy that stands for content id `id` (null when unknown).
func content(id: StringName) -> Resource:
	return _by_id.get(id, null)


## True when `res` is one of this object's copies (never a loaded original).
func is_copy(res: Resource) -> bool:
	for k in _copies:
		if _copies[k] == res:
			return true
	return false


## Applies one override string; returns "" or an error message. The target must live in the copy.
func apply(spec: String) -> String:
	var op := "="
	var at := -1
	for candidate in ["*=", "+=", "="]:
		at = spec.find(candidate)
		if at > 0:
			op = candidate
			break
	if at <= 0:
		return "override '%s': expected <path>=<value>" % spec
	var path := spec.substr(0, at).strip_edges()
	var raw_text := spec.substr(at + op.length()).strip_edges()
	var parsed: Variant = JSON.parse_string(raw_text)
	if parsed == null and raw_text != "null":
		parsed = raw_text  # a bare word is a string (an id, a name)
	var tokens: Array = Array(path.split("."))
	if tokens.size() < 2:
		return "override '%s': path needs <id>.<property>" % spec
	var head := StringName(tokens[0])
	var target: Resource = config if (head == &"config" or head == &"campaign_config") else content(head)
	if target == null:
		return "override '%s': unknown content id '%s'" % [spec, head]
	var err := [""]
	_assign(target, tokens, 1, parsed, op, err)
	if err[0] != "":
		return "override '%s': %s" % [spec, err[0]]
	applied.append(spec)
	return ""


## Applies a list of overrides; returns every error (empty = all applied).
func apply_all(specs: Array) -> PackedStringArray:
	var errors := PackedStringArray()
	for s in specs:
		var e := apply(String(s))
		if e != "":
			errors.append(e)
	return errors


# --- Copier ---------------------------------------------------------------------------------

func _copy_of(res: Resource) -> Resource:
	if res == null:
		return null
	if res.get_script() == null:
		return res  # engine resources (textures, fonts) stay shared; overrides never target them
	var key := res.get_instance_id()
	if _copies.has(key):
		return _copies[key]
	var copy := res.duplicate(false)
	_copies[key] = copy
	for prop in copy.get_property_list():
		if (prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE) == 0:
			continue
		var value: Variant = copy.get(prop.name)
		if value is Resource or value is Array or value is Dictionary:
			copy.set(prop.name, _map(value))
		elif typeof(value) >= TYPE_PACKED_BYTE_ARRAY and typeof(value) <= TYPE_PACKED_VECTOR4_ARRAY:
			copy.set(prop.name, value.duplicate())  # Packed arrays are shared by reference
	return copy


## Value with every Resource inside swapped for its copy; containers are rebuilt, never edited in place.
func _map(value: Variant) -> Variant:
	if value is Resource:
		return _copy_of(value)
	if value is Array:
		var arr: Array = value.duplicate()
		for i in arr.size():
			arr[i] = _map(arr[i])
		return arr
	if value is Dictionary:
		var d: Dictionary = value.duplicate()
		for k in d:
			d[k] = _map(d[k])
		return d
	return value


# --- Overrides ------------------------------------------------------------------------------

## Walks `tokens` from `i` inside `cur`; returns the value `cur` should now hold.
func _assign(cur: Variant, tokens: Array, i: int, raw: Variant, op: String, err: Array) -> Variant:
	if i >= tokens.size():
		return _coerce(cur, raw, op, err)
	var t: String = tokens[i]
	if cur is Resource:
		if not (t in cur):
			err[0] = "no property '%s' on %s" % [t, cur.get_script().get_global_name()]
			return cur
		var child: Variant = cur.get(t)
		var nv: Variant = _assign(child, tokens, i + 1, raw, op, err)
		if err[0] == "":
			cur.set(t, nv)
		return cur
	if cur is Array or cur is PackedInt32Array or cur is PackedFloat32Array or cur is PackedStringArray or cur is PackedInt64Array or cur is PackedFloat64Array:
		if not t.is_valid_int() or int(t) < 0 or int(t) >= cur.size():
			err[0] = "bad index '%s'" % t
			return cur
		var work: Variant = cur.duplicate()  # Packed arrays are shared by reference: never edit the one we were handed
		var nv2: Variant = _assign(work[int(t)], tokens, i + 1, raw, op, err)
		if err[0] == "":
			work[int(t)] = nv2
		return work
	if cur is Vector2i or cur is Vector2:
		var axis := 0 if (t == "x" or t == "0") else (1 if (t == "y" or t == "1") else -1)
		if axis < 0:
			err[0] = "bad component '%s'" % t
			return cur
		var nv3: Variant = _assign(cur[axis], tokens, i + 1, raw, op, err)
		if err[0] == "":
			cur[axis] = nv3
		return cur
	if cur is Dictionary:
		if not cur.has(t):
			err[0] = "no key '%s'" % t
			return cur
		var dict: Dictionary = cur.duplicate()
		var nv4: Variant = _assign(dict[t], tokens, i + 1, raw, op, err)
		if err[0] == "":
			dict[t] = nv4
		return dict
	err[0] = "cannot descend into '%s'" % t
	return cur


## The new value for a leaf currently holding `cur`, from the JSON value `raw` and the operator.
func _coerce(cur: Variant, raw: Variant, op: String, err: Array) -> Variant:
	if op != "=":
		return _arith(cur, raw, op, err)
	match typeof(cur):
		TYPE_INT:
			return int(raw) if raw is float or raw is int else _bad(err, "expected a number")
		TYPE_FLOAT:
			return float(raw) if raw is float or raw is int else _bad(err, "expected a number")
		TYPE_BOOL:
			return bool(raw) if raw is bool or raw is float or raw is int else _bad(err, "expected true/false")
		TYPE_STRING:
			return String(raw)
		TYPE_STRING_NAME:
			return StringName(String(raw))
		TYPE_VECTOR2I:
			return Vector2i(int(raw[0]), int(raw[1])) if raw is Array and raw.size() == 2 else _bad(err, "expected [x, y]")
		TYPE_VECTOR2:
			return Vector2(float(raw[0]), float(raw[1])) if raw is Array and raw.size() == 2 else _bad(err, "expected [x, y]")
		TYPE_PACKED_INT32_ARRAY:
			return PackedInt32Array(raw) if raw is Array else _bad(err, "expected a list")
		TYPE_PACKED_INT64_ARRAY:
			return PackedInt64Array(raw) if raw is Array else _bad(err, "expected a list")
		TYPE_PACKED_FLOAT32_ARRAY:
			return PackedFloat32Array(raw) if raw is Array else _bad(err, "expected a list")
		TYPE_PACKED_FLOAT64_ARRAY:
			return PackedFloat64Array(raw) if raw is Array else _bad(err, "expected a list")
		TYPE_PACKED_STRING_ARRAY:
			return PackedStringArray(raw) if raw is Array else _bad(err, "expected a list")
		TYPE_ARRAY:
			if not (raw is Array):
				return _bad(err, "expected a list")
			var out: Array = cur.duplicate()
			out.clear()
			for v in raw:
				if v is Dictionary or v is Array:
					return _bad(err, "lists of structures cannot be set whole; use <path>.<index>.<property>")
				out.append(v)
			return out
	return _bad(err, "this property type (%s) cannot be set from a value" % type_string(typeof(cur)))


func _arith(cur: Variant, raw: Variant, op: String, err: Array) -> Variant:
	if not (raw is float or raw is int):
		return _bad(err, "%s needs a number" % op)
	var n: float = float(raw)
	match typeof(cur):
		TYPE_INT:
			return roundi(float(cur) * n) if op == "*=" else int(cur) + roundi(n)
		TYPE_FLOAT:
			return float(cur) * n if op == "*=" else float(cur) + n
		TYPE_VECTOR2I:
			var v: Vector2i = cur
			return Vector2i(roundi(v.x * n), roundi(v.y * n)) if op == "*=" else Vector2i(v.x + roundi(n), v.y + roundi(n))
		TYPE_PACKED_INT32_ARRAY:
			var a: PackedInt32Array = cur.duplicate()
			for k in a.size():
				a[k] = roundi(a[k] * n) if op == "*=" else a[k] + roundi(n)
			return a
	return _bad(err, "%s is not defined for %s" % [op, type_string(typeof(cur))])


func _bad(err: Array, msg: String) -> Variant:
	err[0] = msg
	return null


## What ContentLookup.add_registry needs from a dictionary of copies.
class _Adapter extends RefCounted:
	var _d: Dictionary
	func _init(d: Dictionary) -> void:
		_d = d
	func all_ids() -> Array:
		var ids: Array = _d.keys()
		ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
		return ids
	func get_content(id: StringName) -> Resource:
		return _d[id]
