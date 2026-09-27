extends SceneTree
## Text export for localisation (GDD 10). Dumps every player-facing content string, the
## screen sentences (TextDb.UI_TEXT) and every word the code translates (H24 S1: the
## literals passed to tr / atr / TranslationServer.translate / TextDb.mark under
## scripts/) to assets/text/strings.csv as `keys,en` (Godot's CSV translation importer
## picks up extra locale columns). Run headless from the project root, then re-import
## (`godot --headless --path . --import`) to rebuild the .translation:
##   godot --headless --path . -s tools/export_text.gd
## Existing translations in other columns are kept; new keys get an empty cell.

const RegistryScript := preload("res://scripts/autoload/content_registry.gd")
const OUT_PATH := "res://assets/text/strings.csv"
## Where the code-side keys are read from (H24 S1).
const CODE_ROOT := "res://scripts"


func _init() -> void:
	var registry: Node = RegistryScript.new()
	registry.scan_directory(registry.CONTENT_ROOT)
	var lookup := ContentLookup.new()
	for id in registry.all_ids():
		lookup.add(registry.get_content(id))
	var rows := TextDb.collect(lookup)
	# H24 S1: the words the code translates (tr / atr / TranslationServer.translate /
	# TextDb.mark literals under scripts/), their English being the key itself.
	var have := {}
	for row in rows:
		have[String(row[0])] = true
	for k in TextDb.code_keys(PackedStringArray([CODE_ROOT])):
		if not have.has(k):
			rows.append([k, k])
			have[k] = true
	rows.sort_custom(func(a: Array, b: Array) -> bool: return String(a[0]) < String(b[0]))
	# Keep any translation columns already in the file.
	var existing := {}
	var locales: PackedStringArray = PackedStringArray(["en"])
	if FileAccess.file_exists(OUT_PATH):
		var f := FileAccess.open(OUT_PATH, FileAccess.READ)
		var header := f.get_csv_line()
		if header.size() > 1:
			locales = header.slice(1)
		while not f.eof_reached():
			var line := f.get_csv_line()
			if line.size() > 1 and line[0] != "":
				existing[line[0]] = line
		f.close()
	DirAccess.make_dir_recursive_absolute(OUT_PATH.get_base_dir())
	var out := FileAccess.open(OUT_PATH, FileAccess.WRITE)
	var header_row := PackedStringArray(["keys"])
	header_row.append_array(locales)
	out.store_csv_line(header_row)
	for row in rows:
		var key: String = row[0]
		var line := PackedStringArray([key, String(row[1])])
		for i in range(1, locales.size()):
			var old: PackedStringArray = existing.get(key, PackedStringArray())
			line.append(old[i + 1] if old.size() > i + 1 else "")
		out.store_csv_line(line)
	out.close()
	print("TEXT EXPORT: %d strings, locales %s -> %s" % [rows.size(), ", ".join(locales), OUT_PATH])
	registry.free()
	quit(0)
