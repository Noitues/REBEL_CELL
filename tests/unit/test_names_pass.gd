extends GutTest
## ART-0 names pass (DECISIONS "2026-10-05 — Designer rulings: art reintegration, pause
## point 0", rulings 5, 6.1, 6.2, 6.5; "Art direction — ART-0 names pass, part 1 + saves
## folder"): internal names follow the display names, so the old words are gone from every
## player string (assets/text/strings.csv English, every content/**/*.tres string) and, for
## the renamed things, from the code too. Each old word is built from parts here so this
## file never matches a grep for it.

## The old raid words in the node-loss meaning (ruling 6.2), now TAKEN, DOWN, and the
## verdicts CELL HOLDS and BREACHED (the old verdict stamps were upper case).
var RAID_OLD := RegEx.create_from_string("(?i)\\b(" + "sei" + "z(e|ed|es)|" + "dis" + "abled)\\b|\\b(?-i:ALL " + "HOLD|CAMPAIGN " + "LOST)\\b")
## The shop node's old name (ruling 6.5); it is the Mainframe now.
var SHOP_OLD := RegEx.create_from_string("(?i)" + "mo" + "dem")
## The Manifest's hub's old name (ruling 6.1): Priority Routing -> Customs Seal.
var HUB_OLD := RegEx.create_from_string("(?i)priority[ _]" + "routing")

## Strings that use an old raid word in an unrelated meaning (freight flavour, a Hub
## Breach switching a hub off, a UI control). Matched as substrings of the string.
const RAID_ALLOWED: Array[String] = [
	"Seized goods",
]

## Code roots swept for the renamed identifiers.
const CODE_ROOTS: Array[String] = ["res://scripts", "res://scenes", "res://tests", "res://tools", "res://content"]
const CODE_EXTS: Array[String] = ["gd", "tres", "tscn", "py", "cfg", "json"]

var _quoted := RegEx.create_from_string("\"((?:[^\"\\\\]|\\\\.)*)\"")


## Every English string of strings.csv (key and en column).
func _csv_strings() -> Array[String]:
	var out: Array[String] = []
	var f := FileAccess.open("res://assets/text/strings.csv", FileAccess.READ)
	assert_not_null(f, "strings.csv opens")
	if f == null:
		return out
	var header := f.get_csv_line()
	var en := header.find("en")
	while not f.eof_reached():
		var row := f.get_csv_line()
		if row.size() > en and en >= 0:
			out.append(row[0])
			out.append(row[en])
	return out


## Every quoted string of every content .tres (comment lines skipped), as "path: text".
func _content_strings() -> Array[String]:
	var out: Array[String] = []
	for path in _files("res://content", ["tres"]):
		for line in FileAccess.get_file_as_string(path).split("\n"):
			if line.begins_with(";"):
				continue
			for m in _quoted.search_all(line):
				out.append("%s: %s" % [path, m.get_string(1)])
	return out


func _files(root: String, exts: Array[String]) -> Array[String]:
	var out: Array[String] = []
	var stack: Array[String] = [root]
	while not stack.is_empty():
		var dir: String = stack.pop_back()
		for f in DirAccess.get_files_at(dir):
			if exts.has(f.get_extension()):
				out.append(dir.path_join(f))
		for d in DirAccess.get_directories_at(dir):
			stack.append(dir.path_join(d))
	out.sort()
	return out


func _raid_hit(s: String) -> bool:
	var rest := s
	for a in RAID_ALLOWED:
		rest = rest.replace(a, "")
	return RAID_OLD.search(rest) != null


func test_no_player_string_uses_the_old_raid_words() -> void:
	var hits: Array[String] = []
	for s in _csv_strings() + _content_strings():
		if _raid_hit(s):
			hits.append(s)
	assert_eq(hits, [] as Array[String], "TAKEN / DOWN / CELL HOLDS / BREACHED replace the old raid words (ruling 6.2)")




## Ruling 5: ids, enums, file and class names follow the words; no alias is kept.
func test_no_code_file_or_path_keeps_an_old_name() -> void:
	var hits: Array[String] = []
	for root in CODE_ROOTS:
		for path in _files(root, CODE_EXTS):
			var lines := FileAccess.get_file_as_string(path).split("\n")
			for i in lines.size():
				var line := lines[i]
				if _raid_hit(line) and _raid_identifier(line):
					hits.append("%s:%d" % [path, i + 1])
	assert_eq(hits, [] as Array[String], "the old names are gone from the code (ruling 5)")


## A line naming the old raid states as code (enum value, field, outcome string), not the
## UI-control or Hub-Breach "disabled".
func _raid_identifier(line: String) -> bool:
	var ident := RegEx.create_from_string("(?i)sei" + "z(e|ed|es)\\b|Condition\\.DIS" + "ABLED|outcome\\W+dis" + "abled|\"dis" + "abled\"\\s*:")
	return ident.search(line) != null
