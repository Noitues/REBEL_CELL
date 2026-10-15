extends GutTest
## Plan 2 B-CODEX (PB-PT-003b C3): every combat term the playtesters met resolves to a Codex
## entry, and the Codex search finds the nudge entry from "nud".

const TERMS: Array[String] = ["Nudge", "Free nudge", "Tick", "RAM", "Null", "Corrupted", "Resistance",
	"Blocked", "Guard", "Heat thresholds", "Cycles", "Perfect", "Good", "Weak"]


func _titles(all: Dictionary) -> Dictionary:
	var out := {}
	for section in all:
		for e in all[section]:
			out[String(e["title"]).to_lower()] = e
	return out


func test_each_term_has_an_entry() -> void:
	var titles := _titles(Codex.entries(RunManager.lookup()))
	for term in TERMS:
		assert_true(titles.has(term.to_lower()), "Codex entry for %s" % term)
		if titles.has(term.to_lower()):
			assert_ne(String(titles[term.to_lower()]["text"]), "", "%s has text" % term)


func test_search_finds_nudge() -> void:
	var rows := Codex.search(Codex.entries(RunManager.lookup()), "nud")
	assert_gt(rows.size(), 0)
	var titles: Array = []
	for r in rows:
		titles.append(r["title"])
	assert_true(titles.has("Nudge"))
	assert_true(titles.has("Free nudge"))
	assert_eq(Codex.search(Codex.entries(RunManager.lookup()), "  ").size(), 0, "empty query finds nothing")


func test_search_field_flow_type_click_clear() -> void:
	var book: CodexBook = add_child_autofree(CodexBook.new(Codex.entries(RunManager.lookup()), 0.0, 1200.0))
	await get_tree().process_frame
	book.search.text = "nud"
	book.search.text_changed.emit("nud")
	assert_true(book.searching())
	var titles: Array = []
	var row: Control = null
	for r in book.columns.get_child(0).get_children():
		titles.append(String(r.get_meta(&"title")))
		if String(r.get_meta(&"title")) == "Nudge":
			row = r
	assert_true(titles.has("Nudge"), "results list Nudge")
	assert_true(titles.has("Free nudge"), "results list Free nudge")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	row.gui_input.emit(click)
	assert_eq(book.section, "Lexicon", "the click opens the entry's section")
	assert_eq(book.opened_title, "Nudge")
	assert_eq(book.search.text, "", "the field clears")
	book.search.text = "nud"
	book.search.text_changed.emit("nud")
	book.search.text = ""
	book.search.text_changed.emit("")
	assert_false(book.searching())
	assert_eq(book.section, "Lexicon", "clearing restores the tab view")
	assert_not_null(book.current_tab())
