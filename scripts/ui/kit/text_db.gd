class_name TextDb
extends RefCounted
## Text externalisation (GDD 10, gap analysis 2.4): every player-facing string in content
## has a stable key (`<class>.<id>.<field>`); `tools/export_text.gd` dumps them to
## `assets/text/strings.csv` for translators, and Godot's CSV importer turns extra
## locale columns into translations. `t()` returns the translated string for the current
## locale when one exists and the content's own text otherwise, so untranslated builds
## never show keys.


## Key for a resource field, e.g. "CardData.jolt.description".
static func key_for(res: Resource, field: String) -> String:
	var script: Script = res.get_script()
	var cls := String(script.get_global_name()) if script != null else res.get_class()
	var id: String = String(res.get("id")) if "id" in res else res.resource_path.get_file()
	return "%s.%s.%s" % [cls, id, field]


## Translated `field` of `res`, or its own text.
static func t(res: Resource, field: String) -> String:
	if res == null or not (field in res):
		return ""
	var fallback := String(res.get(field))
	var key := key_for(res, field)
	var translated := TranslationServer.translate(key)
	return fallback if translated == key or translated == "" else String(translated)


## Translated UI string by key (`ui.<name>`), or the fallback.
static func ui(key: String, fallback: String) -> String:
	var translated := TranslationServer.translate(key)
	return fallback if translated == key or translated == "" else String(translated)


## Fields that carry player-facing text on any content resource.
const TEXT_FIELDS := ["display_name", "description", "text", "title", "premise", "label", "result_text",
	"warning_text", "phase_line", "event_text"]


## Every (key, text) pair in a lookup's content, sorted by key.
static func collect(lookup: ContentLookup) -> Array[Array]:
	var out: Array[Array] = []
	var seen := {}
	for id in lookup.ids():
		_walk(lookup.get_content(id), out, seen)
	for key in UI_TEXT:
		out.append([String(key), String(UI_TEXT[key])])
	out.sort_custom(func(a: Array, b: Array) -> bool: return String(a[0]) < String(b[0]))
	return out


static func _walk(res: Resource, out: Array[Array], seen: Dictionary) -> void:
	if res == null or seen.has(res.get_instance_id()) or res.get_script() == null:
		return
	seen[res.get_instance_id()] = true
	var has_id := "id" in res and res.get("id") is StringName and String(res.get("id")) != ""
	for field in TEXT_FIELDS:
		if field in res and res.get(field) is String and String(res.get(field)) != "":
			if has_id:
				out.append([key_for(res, field), String(res.get(field))])
	for prop in res.get_property_list():
		if (prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE) == 0:
			continue
		var value: Variant = res.get(prop.name)
		if value is Resource:
			_walk(value, out, seen)
		elif value is Array:
			for item in value:
				if item is Resource:
					_walk(item, out, seen)
	# H23 S15: voice lines have no id; they are keyed by their set and place.
	if res is LineSetData and has_id:
		var set := res as LineSetData
		for i in set.lines.size():
			if set.lines[i] != null and set.lines[i].text != "":
				out.append([voice_key(set, i), set.lines[i].text])


# --- H23: voice lines and screen sentences ---------------------------------------------------

## Key of line `index` of voice line set `set` (H23 S15: a VoiceLineData has no id of its
## own, so its set's id and its place in the set name it).
static func voice_key(set: LineSetData, index: int) -> String:
	return "LineSetData.%s.lines.%d" % [set.id, index]


## Line `index` of `set` in the player's language, or its own text.
static func voice(set: LineSetData, index: int) -> String:
	if set == null or index < 0 or index >= set.lines.size() or set.lines[index] == null:
		return ""
	var fallback := set.lines[index].text
	var key := voice_key(set, index)
	var translated := TranslationServer.translate(key)
	return fallback if translated == key or translated == "" else String(translated)


## Screen sentences that are not content (H23 S5: the raid setup's opening line), by key;
## exported with the content strings so translators see them.
const UI_TEXT := {
	"ui.raid_intro": "The corp is raiding your CORE. Place defences to cut the damage, then RUN THE RAID.",
}


## A screen sentence from UI_TEXT in the player's language.
static func ui_text(key: String) -> String:
	return ui(key, String(UI_TEXT.get(key, key)))
