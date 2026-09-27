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
	return _or_own(key_for(res, field), String(res.get(field)))


## Translated UI string by key (`ui.<name>`), or the fallback.
static func ui(key: String, fallback: String) -> String:
	return _or_own(key, fallback)


## `key` translated when a catalogue has it, else `own` (H24 S4: under pseudolocalisation
## Godot "translates" a key no catalogue has into the key itself, so a generated Mirror
## elite showed "[ĈàŕðÐàţà.ṁîŕŕôŕ_...]"). Own text is pseudolocalised like everything else
## then, once.
static func _or_own(key: String, own: String) -> String:
	if not has_message(key):
		return String(TranslationServer.pseudolocalize(own)) if TranslationServer.pseudolocalization_enabled and own != "" else own
	var translated := String(TranslationServer.translate(key))
	return own if translated == key or translated == "" else translated


## Whether a loaded catalogue has `key` for the player's language or the fallback one.
static func has_message(key: String) -> bool:
	for locale in [TranslationServer.get_locale(), String(ProjectSettings.get_setting("internationalization/locale/fallback", "en"))]:
		var cat := TranslationServer.get_translation_object(locale)
		if cat != null and String(cat.get_message(key)) != "":
			return true
	return false


## A signed number for the screen ("+3", "-2", "0"; H24 S2): translated formats take it
## as "%s" (Godot's pseudolocalisation does not skip "%+d" and broke the format).
static func signed(n: int) -> String:
	return ("+%d" % n) if n > 0 else str(n)


## Marks `text` as a translation key used in code without translating it here (it is
## translated where it is shown, e.g. a top-bar tag's name). `tools/export_text.gd` exports
## every `TextDb.mark("...")`, `tr("...")`, `atr("...")` and `TranslationServer.translate("...")`
## literal under scripts/ (H24 S1).
static func mark(text: String) -> String:
	return text


## Makes `node` and everything under it show its words as given (H24 S4: translate exactly
## once). Screens translate where they build their words (tr for code words, TextDb for
## content); the Controls that show them must not translate them again (a pseudolocalised
## "[[Warm Cache] (10)]"), tooltips included.
static func shown_as_given(node: Node) -> void:
	node.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	if node is Control:
		(node as Control).tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	# The map keys under it show their fixed row words as keys and translate them themselves.
	_legends_translate(node)


## The map key's class: it shows its fixed row words as keys and translates them itself.
const LEGEND_CLASS := &"MapLegend"


static func _legends_translate(node: Node) -> void:
	for child in node.get_children():
		# By class name: TextDb stays free of the kit's view classes (tools load it alone).
		var script: Script = child.get_script()
		if script != null and script.get_global_name() == LEGEND_CLASS:
			translates_itself(child)
		else:
			_legends_translate(child)


## Lets a part that shows its own fixed words as keys (a map legend's rows) translate them
## itself inside a page shown as given (`shown_as_given`).
static func translates_itself(node: Node) -> void:
	node.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_ALWAYS


## Code-side translation keys (H24 S1): every string literal passed to `tr`, `atr`,
## `TranslationServer.translate` or `TextDb.mark` in the .gd files under `dirs` (recursive,
## comment lines skipped), and every string literal on a line ending in the marker
## `# TR` (words kept in constants, translated where they are shown), unescaped, sorted,
## no duplicates.
static func code_keys(dirs: PackedStringArray) -> PackedStringArray:
	var re := RegEx.create_from_string("(?<![A-Za-z0-9_])(?:tr|atr|TranslationServer\\.translate|TextDb\\.mark)\\(\\s*\"((?:[^\"\\\\]|\\\\.)*)\"")
	var any := RegEx.create_from_string("(?<![&A-Za-z0-9_])\"((?:[^\"\\\\]|\\\\.)*)\"")
	var seen := {}
	for dir in dirs:
		for path in _gd_files(dir):
			var src := FileAccess.get_file_as_string(path)
			for line in src.split("\n"):
				if line.strip_edges().begins_with("#"):
					continue
				var marked := line.strip_edges(false, true).ends_with(CODE_MARK)
				for m in (any if marked else re).search_all(line):
					var k := unescape(m.get_string(1))
					if k != "":
						seen[k] = true
	var out := PackedStringArray(seen.keys())
	out.sort()
	return out


## The end-of-line marker for lines whose string literals are all translation keys.
const CODE_MARK := "# TR"


## A GDScript string literal's body as the string it makes (\n, \t, \", \', \\).
static func unescape(body: String) -> String:
	var out := ""
	var i := 0
	while i < body.length():
		var ch := body[i]
		if ch == "\\" and i + 1 < body.length():
			var nx := body[i + 1]
			match nx:
				"n":
					out += "\n"
				"t":
					out += "\t"
				_:
					out += nx
			i += 2
			continue
		out += ch
		i += 1
	return out


static func _gd_files(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_gd_files(dir.path_join(sub)))
	return out


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
	return _or_own(voice_key(set, index), set.lines[index].text)


## Screen sentences that are not content (H23 S5: the raid setup's opening line), by key;
## exported with the content strings so translators see them.
const UI_TEXT := {
	"ui.raid_intro": "The corp is raiding your CORE. Place defences to cut the damage, then START DEFENSE.",
}


## A screen sentence from UI_TEXT in the player's language.
static func ui_text(key: String) -> String:
	return ui(key, String(UI_TEXT.get(key, key)))
