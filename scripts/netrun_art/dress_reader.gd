class_name DressReader
extends RefCounted
## NA-21: reader for `dress_<run>.json` v1 (the street dressing placement lists; DERIVE_V2_REVIEW Q4, AD resolutions
## 13-18) and the version / room-kind gate of the derive files (AD resolution 19). Pure: parses text, checks it against
## the v1 field table and returns the typed lists. JSON integers arrive from Godot's parser as floats; fields the
## schema calls `integer` are turned back into `int`. A bad file returns `{"error": "<named error>"}` and nothing else.
## Error names: `dress.version` (unknown version), `dress.kind`, `dress.missing`, `dress.type`, `dress.palette`,
## `derive.version`, `derive.room_kind` (unknown room kind).

## The one `dress_<run>.json` version this reader knows.
const DRESS_VERSION := 1
## The derive version the room-kind gate accepts (`NetrunArtDeriver.VERSION`).
const DERIVE_VERSION := 2
## Palette ids a dress item may use (`dress.PALETTE_IDS`).
const PALETTE_IDS: Array[String] = ["district_a", "district_b", "accent_warm", "accent_cool", "lamp_warm", "lamp_cool",
	"lane_head_a", "lane_head_b", "lane_tail_a", "lane_tail_b"]
## Field kinds of the table below.
const K_STR := "s"
const K_INT := "i"
const K_NUM := "n"
const K_PAL := "p"
const K_V2 := "v2"
const K_V3 := "v3"
const K_INT2 := "i2"
## The v1 lists: list name -> {field: kind}. `streaks` is checked as a nested list of `{u0, len, gap, bright}` numbers.
const LISTS: Dictionary = {
	"signs": {"bid": K_STR, "layer": K_INT, "pos": K_V3, "nrm": K_V2, "w": K_NUM, "h": K_NUM, "panels": K_INT,
		"pal": K_PAL, "band_pal": K_PAL},
	"lamps": {"u": K_NUM, "side": K_INT, "pos": K_V3, "pal": K_PAL},
	"washes": {"u": K_NUM, "pos": K_V3, "dir": K_V3, "power": K_NUM, "pal": K_PAL},
	"glows": {"cell": K_INT2, "pos": K_V3, "power": K_NUM, "pal": K_PAL, "drift": K_V3},
	"beams": {"bid": K_STR, "pos": K_V3, "lean": K_V2, "sweep_deg": K_NUM, "phase": K_NUM, "pal": K_PAL},
	"streak_lanes": {"lane_id": K_INT, "a": K_V2, "b": K_V2, "z": K_NUM, "speed": K_NUM, "pal": K_PAL},
	"fog_fields": {"id": K_STR, "min": K_V3, "max": K_V3, "density": K_NUM},
}
const STREAK_FIELDS: Array[String] = ["u0", "len", "gap", "bright"]


## Parses `text` as `dress_<run>.json` v1. Returns the dress Dictionary (`version`, `run`, `layout_seed`, `kind`, and the
## seven lists) with integer fields as `int`, or `{"error": "<name>: <detail>"}`.
static func read_text(text: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		return {"error": "dress.type: the file is not a JSON object"}
	var d: Dictionary = parsed
	for key: String in ["version", "run", "layout_seed", "kind"]:
		if not d.has(key):
			return {"error": "dress.missing: %s" % key}
	if not _is_int_value(d["version"]) or int(d["version"]) != DRESS_VERSION:
		return {"error": "dress.version: unknown version %s (this reader knows %d)" % [str(d["version"]), DRESS_VERSION]}
	if d["kind"] != "street":
		return {"error": "dress.kind: unknown kind %s" % str(d["kind"])}
	if not (d["run"] is String) or not (d["layout_seed"] is String) or not _is_u64_text(String(d["layout_seed"])):
		return {"error": "dress.type: run / layout_seed"}
	var out: Dictionary = {"version": DRESS_VERSION, "run": d["run"], "layout_seed": d["layout_seed"], "kind": "street"}
	for list_name: String in LISTS:
		if not d.has(list_name):
			return {"error": "dress.missing: %s" % list_name}
		if not (d[list_name] is Array):
			return {"error": "dress.type: %s is not a list" % list_name}
		var rows: Array = []
		var i := 0
		for item: Variant in d[list_name]:
			var row: Dictionary = _read_item(list_name, i, item)
			if row.has("error"):
				return row
			rows.append(row)
			i += 1
		out[list_name] = rows
	return out


## Reads `path` with `read_text`.
static func read_file(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"error": "dress.missing: file %s" % path}
	return read_text(FileAccess.get_file_as_string(path))


## True when `kind` is a room kind the readers accept: the four node types plus rest, workshop and cache (AD 19).
static func is_room_kind(kind: String) -> bool:
	return NetrunStreetDeriver.ROOM_KINDS.has(kind)


## The gate every derive reader runs: the `version` must be 2 and every room's `kind` a known one (AD 19). Returns ""
## when the derive is acceptable, else the named error.
static func check_derive(derive: Dictionary) -> String:
	if not derive.has("version") or not _is_int_value(derive["version"]) or int(derive["version"]) != DERIVE_VERSION:
		return "derive.version: unknown version %s (this reader knows %d)" % [str(derive.get("version")), DERIVE_VERSION]
	var rooms: Variant = derive.get("rooms", {})
	if not (rooms is Dictionary):
		return "derive.type: rooms is not an object"
	var ids: Array = (rooms as Dictionary).keys()
	IdSort.sort_ids(ids)
	for id: Variant in ids:
		var kind: Variant = (rooms as Dictionary)[id].get("kind", "")
		if not (kind is String) or not is_room_kind(String(kind)):
			return "derive.room_kind: room %s has unknown kind %s" % [String(id), str(kind)]
	return ""


static func _read_item(list_name: String, index: int, item: Variant) -> Dictionary:
	if not (item is Dictionary):
		return {"error": "dress.type: %s[%d] is not an object" % [list_name, index]}
	var spec: Dictionary = LISTS[list_name]
	var src: Dictionary = item
	var row: Dictionary = {}
	for field: String in spec:
		if not src.has(field):
			return {"error": "dress.missing: %s[%d].%s" % [list_name, index, field]}
		var v: Variant = _read_value(spec[field], src[field])
		if v == null:
			if spec[field] == K_PAL:
				return {"error": "dress.palette: %s[%d].%s = %s" % [list_name, index, field, str(src[field])]}
			return {"error": "dress.type: %s[%d].%s" % [list_name, index, field]}
		row[field] = v
	if list_name == "streak_lanes":
		if not src.has("streaks") or not (src["streaks"] is Array):
			return {"error": "dress.missing: %s[%d].streaks" % [list_name, index]}
		var streaks: Array = []
		for s: Variant in src["streaks"]:
			if not (s is Dictionary):
				return {"error": "dress.type: %s[%d].streaks" % [list_name, index]}
			var srow: Dictionary = {}
			for f: String in STREAK_FIELDS:
				if not (s as Dictionary).has(f) or not _is_number((s as Dictionary)[f]):
					return {"error": "dress.type: %s[%d].streaks.%s" % [list_name, index, f]}
				srow[f] = float((s as Dictionary)[f])
			streaks.append(srow)
		row["streaks"] = streaks
	return row


## A field value in its typed form, or null when it does not fit `kind`.
static func _read_value(kind: String, v: Variant) -> Variant:
	match kind:
		K_STR:
			return v if v is String else null
		K_INT:
			return int(v) if _is_int_value(v) else null
		K_NUM:
			return float(v) if _is_number(v) else null
		K_PAL:
			return v if (v is String and PALETTE_IDS.has(String(v))) else null
		K_V2:
			return _vec(v, 2)
		K_V3:
			return _vec(v, 3)
		K_INT2:
			if v is Array and (v as Array).size() == 2 and _is_int_value(v[0]) and _is_int_value(v[1]):
				return [int(v[0]), int(v[1])]
			return null
	return null


static func _vec(v: Variant, n: int) -> Variant:
	if not (v is Array) or (v as Array).size() != n:
		return null
	var out: Array = []
	for e: Variant in v:
		if not _is_number(e):
			return null
		out.append(float(e))
	return out


static func _is_number(v: Variant) -> bool:
	return v is float or v is int


static func _is_int_value(v: Variant) -> bool:
	if v is int:
		return true
	return v is float and floorf(v) == v


static func _is_u64_text(s: String) -> bool:
	if s == "0":
		return true
	return s.length() > 0 and s.is_valid_int() and not s.begins_with("0") and not s.begins_with("-") and not s.begins_with("+")
