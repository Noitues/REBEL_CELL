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
