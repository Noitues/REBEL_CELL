extends SceneTree
## Text export for localisation (GDD 10). Dumps every player-facing content string to
## assets/text/strings.csv as `keys,en` (Godot's CSV translation importer picks up extra
## locale columns). Run headless from the project root:
##   godot --headless --path . -s tools/export_text.gd
## Existing translations in other columns are kept; new keys get an empty cell.

const RegistryScript := preload("res://scripts/autoload/content_registry.gd")
const OUT_PATH := "res://assets/text/strings.csv"


func _init() -> void:
	var registry: Node = RegistryScript.new()
	registry.scan_directory(registry.CONTENT_ROOT)
	var lookup := ContentLookup.new()
	for id in registry.all_ids():
		lookup.add(registry.get_content(id))
	var rows := TextDb.collect(lookup)
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
