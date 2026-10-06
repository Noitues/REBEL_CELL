class_name PencilPlan
extends Control
## ART-10 4C: the grease-pencil plan beside the title's three verb stickers (ART_BIBLE v2
## §1.2 "Grease pencil", §4.13 title option A "the plan"; round 33 `title_screen.jpg`). The art
## is the concept's own (round 33 title.py `static_ui`: the numbers 1. 2. 3. and the plan
## bracket in `ui31.Pencil`, baked by tools/art/bake_menus_r33.py into
## `assets/ui/menus/pencil/plan.png`); the verb rows keep its 112 px board pitch
## (`row_pitch`) so each number sits on its row. B1b (integration review D3 / D25): the art is
## drawn through the kit's one wax material (a GreasePencilArt child), so it writes on when the
## title shows instead of appearing whole. View only.

const ART := "res://assets/ui/menus/pencil/plan.png"
const META := "res://assets/ui/menus/pencil/meta.json"
## The concept board (1920 wide) to the game's 1280.
const BOARD_TO_GAME := GreasePencilMark.BOARD_TO_CANVAS

static var _meta: Dictionary = {}

## The column whose rows the numbers stand beside (kept for the layout's reference).
var rows: Control = null
var _tex: Texture2D = null
var _art: GreasePencilArt = null


static func meta() -> Dictionary:
	if _meta.is_empty():
		var f := FileAccess.open(META, FileAccess.READ)
		if f != null:
			_meta = JSON.parse_string(f.get_as_text())
	return _meta


## The art's scale with the text (stickers and the plan scale as whole objects, up to
## VerbSticker.SCALE_MAX).
static func art_scale() -> float:
	return BOARD_TO_GAME * clampf(Settings.text_scale, 1.0, VerbSticker.SCALE_MAX)


## The verb rows' pitch (px): the concept's 112 board px, scaled.
static func row_pitch() -> float:
	return float(meta().get("row_pitch", 112)) * art_scale()


func _init(p_rows: Control = null) -> void:
	rows = p_rows
	name = "PencilPlan"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_tex = load(ART) as Texture2D
	custom_minimum_size = Vector2(_tex.get_size().x * art_scale(), 0.0) if _tex != null else Vector2.ZERO
	if _tex != null:
		_art = GreasePencilArt.new(_tex, _tex.get_size() * art_scale())
		_art.name = "Art"
		add_child(_art)
		_place()


## The plan's pencil (tests: the kit's material).
func art() -> GreasePencilArt:
	return _art


func _place() -> void:
	# The plan art's first number sits on the first row's centre (the concept's row_y[0]).
	var box: Array = meta().get("plan_box", [0, 300, 0, 0])
	var row_y: Array = meta().get("row_y", [392])
	var k := art_scale()
	_art.position = Vector2(0, row_pitch() * 0.5 - (float(row_y[0]) - float(box[1])) * k)
