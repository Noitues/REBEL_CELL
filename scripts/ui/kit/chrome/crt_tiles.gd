class_name CrtTiles
extends HFlowContainer
## ART-10 4C: a row of terminal tiles that picks one value (round 31 `settings_menu.jpg`
## COLOUR-BLIND CORRECTION / RESOLVE SPEED tiles): each tile a MenuChip with the
## choice's word in CAPS and its gloss under it ("Deutan (green-weak)" -> DEUTAN /
## green-weak); the chosen one cyan-filled (§2.10, never lime). It fronts an OptionButton
## (`option`, kept hidden in the row): a tile press selects that item and emits its
## `item_selected`, and the tiles follow the option when anything else selects it. So the
## settings code and its tests drive the option as before. View only.

const GAP := 8

var option: OptionButton
var tiles: Array[MenuChip] = []


func _init(p_option: OptionButton) -> void:
	option = p_option
	name = String(option.name) + "Tiles"
	add_theme_constant_override("h_separation", GAP)
	add_theme_constant_override("v_separation", GAP)
	option.visible = false
	add_child(option)
	for i in option.item_count:
		var words := split(option.get_item_text(i))
		var t := MenuChip.new(words[0], words[1])
		t.pre_translated = true
		t.name = "Tile%d" % i
		t.label_step = UiTheme.BODY
		t.set_meta(UiFocus.META_NO_SCALE, true)
		var idx := i
		t.pressed.connect(func() -> void: pick(idx))
		add_child(t)
		tiles.append(t)
	option.item_selected.connect(func(_i: int) -> void: _sync())
	_sync()


## "Deutan (green-weak)" -> ["Deutan", "green-weak"]; a word with no gloss -> [word, ""].
static func split(t: String) -> PackedStringArray:
	var at := t.find(" (")
	if at < 0:
		return PackedStringArray([t, ""])
	var rest := t.substr(at + 2)
	var close := rest.rfind(")")
	if close >= 0:
		rest = rest.substr(0, close) + rest.substr(close + 1)
	return PackedStringArray([t.substr(0, at), rest])


## Selects item `i` as a player's pick would (the option's item_selected fires).
func pick(i: int) -> void:
	if i == option.selected:
		return
	option.select(i)
	option.item_selected.emit(i)


func _sync() -> void:
	for i in tiles.size():
		tiles[i].selected = i == option.selected


## The OptionButton's own selection moved (select() emits nothing): the tiles follow.
func refresh() -> void:
	_sync()
