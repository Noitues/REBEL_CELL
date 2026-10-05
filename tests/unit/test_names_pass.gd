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
## The Manifest's hub's old name (ruling 6.1); it is the Customs Seal now.
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


func test_no_player_string_or_content_names_the_old_shop_node() -> void:
	var hits: Array[String] = []
	for s in _csv_strings() + _content_strings():
		if SHOP_OLD.search(s) != null:
			hits.append(s)
	assert_eq(hits, [] as Array[String], "the shop node is the Mainframe (ruling 6.5)")


func test_no_player_string_or_content_names_the_old_manifest_hub() -> void:
	var hits: Array[String] = []
	for s in _csv_strings() + _content_strings():
		if HUB_OLD.search(s) != null:
			hits.append(s)
	assert_eq(hits, [] as Array[String], "the Manifest's hub is the Customs Seal (ruling 6.1)")


## Ruling 5: ids, enums, file and class names follow the words; no alias is kept.
func test_no_code_file_or_path_keeps_an_old_name() -> void:
	var hits: Array[String] = []
	for root in CODE_ROOTS:
		for path in _files(root, CODE_EXTS):
			if SHOP_OLD.search(path) != null or HUB_OLD.search(path) != null:
				hits.append(path)
				continue
			var lines := FileAccess.get_file_as_string(path).split("\n")
			for i in lines.size():
				var line := lines[i]
				if SHOP_OLD.search(line) != null or HUB_OLD.search(line) != null:
					hits.append("%s:%d" % [path, i + 1])
				elif _raid_hit(line) and _raid_identifier(line):
					hits.append("%s:%d" % [path, i + 1])
	assert_eq(hits, [] as Array[String], "the old names are gone from the code (ruling 5)")


## A line naming the old raid states as code (enum value, field, outcome string), not the
## UI-control or Hub-Breach "disabled".
func _raid_identifier(line: String) -> bool:
	var ident := RegEx.create_from_string("(?i)sei" + "z(e|ed|es)\\b|Condition\\.DIS" + "ABLED|outcome\\W+dis" + "abled|\"dis" + "abled\"\\s*:")
	return ident.search(line) != null


# --- Part 2 (DECISIONS "2026-10-05 — Designer rulings: names for M14", D2–D8, D11–D12) -----------
# Each entry: the item, a regex over player strings (strings.csv English, content .tres strings),
# a regex over code lines (scripts / scenes / tests / tools / content; this file is skipped), and
# substrings allowed in player strings for an unrelated meaning.

const PART2: Array = [
	["D2 slice programs",
		"(?-i)\\b(ATK|ATTACK|DEFEND|AFFLICT|AFL|EVD|DEF|CRIT|HEAL)\\b|\\bCRITICAL\\b|\\b(EVADE|Evade) slices?\\b",
		"SliceType\\.(ATTACK|CRIT|DEFEND|EVADE|HEAL|AFFLICT)\\b|(?<![A-Za-z0-9])(atk|crit|def|evade|heal)_\\d",
		["reads CRITICAL"]],
	["D3 Meridian programs",
		"(?-i)\\bTariff\\b|(?i)\\bjudge?ment\\b",
		"slices/tariff|&\"tariff\"|\"tariff\"|slot_tariff|(?i)judge?ment",
		["Tariff Collector", "Tariff Calculation Office", "Tariff season"]],
	["D5 Central Server",
		"(?i)mainframe gate|\\bboss site\\b",
		"SiteObjective\\.BOSS\\b|KIND_BOSS|GLYPH_BOSS|renewal_engine_site|the_manifest_site|civic_core_site|commons_array_site|(?i)mainframe gate",
		[]],
	["D6 Firmware",
		"(?i)micro ?chips?",
		"(?i)micro ?chip",
		[]],
	["D8 WEAK",
		"(?i)\\bpartial\\b",
		"PrecisionTier\\.PARTIAL|partial_multiplier|precision_partial",
		[]],
	["D12 RESPIN / UNDO",
		"(?i)\\bcheckpoints?\\b",
		"(?-i)\\bCHECKPOINT\\b",
		[]],
	["D4 WEIGHT",
		"(?i)\\binertia\\b",
		"(?i)inertia",
		[]],
]


func _part2_player_hits(entry: Array) -> Array[String]:
	var re := RegEx.create_from_string(String(entry[1]))
	var hits: Array[String] = []
	for s in _csv_strings() + _content_strings():
		var rest := s
		for a in entry[3]:
			rest = rest.replace(String(a), "")
		if re.search(rest) != null:
			hits.append(s)
	return hits


func test_part2_no_player_string_keeps_an_old_word() -> void:
	for entry in PART2:
		assert_eq(_part2_player_hits(entry), [] as Array[String], "%s: the old words are gone from player text" % entry[0])


func test_part2_no_code_keeps_an_old_name() -> void:
	var own := (get_script() as Script).resource_path
	for entry in PART2:
		var re := RegEx.create_from_string(String(entry[2]))
		var hits: Array[String] = []
		for root in CODE_ROOTS:
			for path in _files(root, CODE_EXTS):
				if path == own:
					continue
				if re.search(path) != null:
					hits.append(path)
					continue
				var lines := FileAccess.get_file_as_string(path).split("\n")
				for i in lines.size():
					if re.search(lines[i]) != null:
						hits.append("%s:%d" % [path, i + 1])
		assert_eq(hits, [] as Array[String], "%s: the old names are gone from the code" % entry[0])


## D5: each corporation's Central Server (its boss Site) carries its own name.
func test_d5_each_central_server_has_its_name() -> void:
	var want := {&"solace": "The Genome Core", &"meridian": "The Master Manifest", &"halcyon": "The Panopticon",
		&"orbital": "Launch Control", &"rebel_cell": "DISPATCH"}
	for corp_id in want:
		var corp := ContentRegistry.get_content(corp_id) as CorporationData
		var names: Array[String] = []
		for s in corp.city_grid.sites:
			if s.objective == RC.SiteObjective.CENTRAL_SERVER:
				names.append(s.display_name)
		assert_eq(names, [want[corp_id]] as Array[String], "%s's Central Server" % corp_id)


## D2: every slice's display name uses the program's new word.
func test_d2_slice_display_names_use_the_program_words() -> void:
	var old := RegEx.create_from_string("(?-i)^(Attack|Crit|Defend|Evade|Heal)\\b")
	for id in ContentRegistry.all_ids():
		var s := ContentRegistry.get_content(id) as SliceData
		if s != null:
			assert_null(old.search(s.display_name), "%s: %s" % [id, s.display_name])
	assert_eq(RC.SliceType.keys().slice(0, 9), ["SHIM", "OVERFLOW", "DEFRAG", "DETOUR", "SANDBOX", "TROJAN", "HOTFIX", "INFECT", "NULL"])


# --- Part 3 (DECISIONS "2026-10-05 — Designer rulings: SANDBOX / TROJAN / NULL and five Heat
# bands", ruling 1; "Art direction — ART-0 names pass, part 3") ------------------------------------
# Same shape as PART2. Kept meanings, never matched: shield the resource (block / shield, the
# shield cap, "+4 shield" hubs, Shield Wall, Shield Cache, "+%d SHIELD"), deploy the verb (drones
# and Armory assets, DEPLOY_DRONE, the "deploy" drone event and bark), miss in prose ("Miss a
# payment", "the cameras miss", "make a miss count", missing / mission ...).

const PART3: Array = [
	["SANDBOX slice program",
		"(?-i)\\bSHD\\b|\\b(Shield|SHIELD) \\d|\\bSHIELD slices?\\b|\\bShield slices?\\b|SliceData\\.shield_",
		"SliceType\\.SHIELD\\b|(?<![A-Za-z0-9])shield_[58]\\b|slices/shield_",
		[]],
	["TROJAN slice program",
		"(?-i)\\bDEP\\b|\\bDeploy \\d|\\b(DEPLOY|Deploy) slices?\\b|\\bPerfect Deploy\\b|\\bon a Deploy\\b|^DEPLOY$|SliceData\\.deploy_",
		"SliceType\\.DEPLOY\\b|(?<![A-Za-z0-9])deploy_1\\b|slices/deploy_|SLICE_DEPLOY|mirror_" + "deploy_base",
		[]],
	["NULL slice program",
		"(?-i)\\bMISS\\b|\\bMiss\\b|\\bnon-Miss\\b|SliceData\\.miss\\b",
		"SliceType\\.MISS\\b|RANDOM_NON_MISS|ON_MISS_SLICE|SLICE_MISS|MISS_X_|slices/miss\\.tres|&\"miss\"|bark:miss|_bark\\(\"miss\"|\"type\": \"miss\"|(?i:miss)_(resolved|static|slot|wheel|slice)|\\bis_miss\\b|\\bnon_miss\\b|\\b(s|fx|cd|dm|dr|fw|g|h1\\d)_miss\\b|(?<![A-Za-z0-9])_miss\\b|slot_miss\\b",
		["Miss a payment"]],
]


func _entry_player_hits(entry: Array) -> Array[String]:
	return _part2_player_hits(entry)


func test_part3_no_player_string_keeps_an_old_word() -> void:
	for entry in PART3:
		assert_eq(_entry_player_hits(entry), [] as Array[String], "%s: the old words are gone from player text" % entry[0])


func test_part3_no_code_keeps_an_old_name() -> void:
	var own := (get_script() as Script).resource_path
	for entry in PART3:
		var re := RegEx.create_from_string(String(entry[2]))
		var hits: Array[String] = []
		for root in CODE_ROOTS:
			for path in _files(root, CODE_EXTS):
				if path == own:
					continue
				if re.search(path) != null:
					hits.append(path)
					continue
				var lines := FileAccess.get_file_as_string(path).split("\n")
				for i in lines.size():
					if re.search(lines[i]) != null:
						hits.append("%s:%d" % [path, i + 1])
		assert_eq(hits, [] as Array[String], "%s: the old names are gone from the code" % entry[0])


## The kept meanings stay: the shield resource, the deploy verb, miss in prose.
func test_part3_the_kept_meanings_stay() -> void:
	var all := "\n".join(_csv_strings())
	for kept in ["+%d SHIELD", "Gain 4 shield.", "Shield Wall", "Deploy armory asset", "Miss a payment"]:
		assert_string_contains(all, kept, "%s keeps its meaning" % kept)
	assert_true(RC.EffectType.keys().has("DEPLOY_DRONE"), "deploying a drone is a verb, not the program")


## Ruling 1: the programs' ids, files, display names, words and tags follow the new words.
func test_b3_the_slice_programs_are_sandbox_trojan_null() -> void:
	var want := {&"sandbox_5": ["Sandbox 5", RC.SliceType.SANDBOX], &"sandbox_8": ["Sandbox 8", RC.SliceType.SANDBOX],
		&"trojan_1": ["Trojan 1", RC.SliceType.TROJAN], &"null": ["Null", RC.SliceType.NULL]}
	for id in want:
		var s := ContentRegistry.get_content(id) as SliceData
		assert_not_null(s, "%s exists" % id)
		if s != null:
			assert_eq(s.display_name, want[id][0])
			assert_eq(s.slice_type, want[id][1])
			assert_true(ResourceLoader.exists("res://content/slices/%s.tres" % id), "%s's file follows its id" % id)
	assert_eq(Palette.SLICE_WORDS[RC.SliceType.SANDBOX], "SANDBOX")
	assert_eq(Palette.SLICE_WORDS[RC.SliceType.TROJAN], "TROJAN")
	assert_eq(Palette.SLICE_WORDS[RC.SliceType.NULL], "NULL")
	assert_eq(Palette.SLICE_NAMES[RC.SliceType.SANDBOX], "SBOX")
	assert_eq(Palette.SLICE_NAMES[RC.SliceType.TROJAN], "TRJN")
	assert_eq(Palette.SLICE_NAMES[RC.SliceType.NULL], "NULL")


## The compact tags SBOX / TRJN / NULL take no more room at text size 2.0 than the part-2 tags
## (SHIM, OVFL, DFRG, DTOR, HFIX, INFC) the slot lists and shop tiles already fit.
func test_b3_the_new_tags_fit_like_the_others_at_text_size_2() -> void:
	var font := Palette.mono()
	var px := roundi(UiTheme.BASE_SIZE * 2.0)
	var widest := 0.0
	for t in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW, RC.SliceType.DEFRAG, RC.SliceType.DETOUR, RC.SliceType.HOTFIX, RC.SliceType.INFECT]:
		widest = maxf(widest, font.get_string_size(String(Palette.SLICE_NAMES[t]), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	for t in [RC.SliceType.SANDBOX, RC.SliceType.TROJAN, RC.SliceType.NULL]:
		var w := font.get_string_size(String(Palette.SLICE_NAMES[t]), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		assert_true(w <= widest + 0.5, "%s is %.1f px at 2.0, the widest part-2 tag %.1f" % [Palette.SLICE_NAMES[t], w, widest])
