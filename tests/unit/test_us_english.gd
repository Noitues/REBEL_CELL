extends GutTest
## Designer ruling 2026-10-13: player-facing text is US English. Scans the English column of
## the exported strings.csv (content display fields, TextDb screen sentences and every
## translated code literal) for the British forms. Identifiers (ids, node names, keys) are not
## in that column, so no allow-list is needed.

const CSV_PATH := "res://assets/text/strings.csv"
const BRITISH_PATTERN := "\\b(anticlockwise|armour\\w*|authoris\\w*|unauthoris\\w*|centre\\w*|centred|colour\\w*|defence\\w*|favour\\w*|grey\\w*|harbour\\w*|kilometre\\w*|labelled|licence\\w*|litres?|metres?|monetis\\w*|neighbour\\w*|organis\\w*|practising|prioritis\\w*|recognis\\w*|rumour\\w*|sterilis\\w*|theatre\\w*|behaviour\\w*|honour\\w*|travelled|cancelled|programme\\w*)\\b"


func test_no_british_spellings_in_player_text() -> void:
	var re := RegEx.new()
	assert_eq(re.compile(BRITISH_PATTERN, true), OK, "pattern compiles")
	var f := FileAccess.open(CSV_PATH, FileAccess.READ)
	assert_not_null(f, "strings.csv exists")
	if f == null:
		return
	f.get_csv_line()
	var hits: Array[String] = []
	var rows := 0
	while not f.eof_reached():
		var line := f.get_csv_line()
		if line.size() < 2:
			continue
		rows += 1
		var m := re.search(line[1])
		if m != null:
			hits.append("%s -> %s" % [line[0], m.get_string()])
	f.close()
	assert_gt(rows, 100, "the export has rows")
	assert_eq(hits, [] as Array[String], "British spellings in player text (use US English)")
