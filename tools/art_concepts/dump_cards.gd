extends SceneTree
## Writes tools/art_concepts/cards.psv (id|family|unique|type|rarity|class|name), the card
## list the brief and concept scripts read (W4, ART_BIBLE 7.3). Run from the project root:
##   godot --headless --path . -s tools/art_concepts/dump_cards.gd

const OUT := "res://tools/art_concepts/cards.psv"


func _init() -> void:
	var names := DirAccess.get_files_at("res://content/cards")
	names.sort()
	var f := FileAccess.open(OUT, FileAccess.WRITE)
	for n in names:
		if not n.ends_with(".tres"):
			continue
		var c := load("res://content/cards/" + n) as CardData
		f.store_line("%s|%s|%s|%s|%s|%s|%s" % [c.id, CardArt.family_of(c), CardArt.is_unique(c), CardArt.TYPE_WORDS[CardArt.type_of(c)],
			RC.Rarity.keys()[c.rarity], c.class_id, c.display_name])
	f.close()
	quit()
