class_name CellStamp
extends Control
## B5 (round 44 B_menus `campaign_slots.png`, review D21: the slots are the Cell's own case files, so they carry the
## Cell's stamp, never a corp letterhead): the Cell's red hex-and-fist rubber stamp ("ACTIVE // REBEL_CELL // OWN
## FILE"), the concept's own image (`campaign_slots.cell_stamp`, exported unchanged by tools/art/export_cell_stamp.py
## into `assets/ui/menus/stamps/`, one per state word), shown at its 1080p board size and tilted. A word the
## export has no image for (a translated one) is the live RubberStamp in the Cell's red. A view only.

const DIR := "res://assets/ui/menus/stamps/"
## The stamp's size on screen as a share of its board px (round 44 places it at 0.74 of the drawn stamp).
const BOARD_SHARE := 0.74
## The board height the images were drawn on (the 1920x1080 concept board).
const BOARD_H := 1080.0
## The live fallback's type step.
const FALLBACK_STEP := UiTheme.BODY
## The stamp's ink alpha over paper (the image carries its own uneven ink; this is the fallback's).
const FALLBACK_ALPHA := 0.88

## The state word (a key: ACTIVE, IN A RUN, WON, LOST, ABANDONED).
var word: String = ""
var tilt_deg: float = 0.0
var _tex: Texture2D = null
var _live: RubberStamp = null


func _init(p_word: String = "ACTIVE", p_tilt: float = 0.0) -> void:
	word = p_word
	tilt_deg = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var shown := tr(word)
	var path := DIR + "cell_stamp_%s.png" % word.to_lower().replace(" ", "_")
	if shown == word and ResourceLoader.exists(path):
		_tex = load(path) as Texture2D
	else:
		_live = RubberStamp.new(shown, Color(Palette.CORP_REBEL_CELL, FALLBACK_ALPHA), FALLBACK_STEP, p_tilt)
		add_child(_live)
	resized.connect(func() -> void: pivot_offset = size * 0.5)


func _ready() -> void:
	_fit()


## True when the concept's image draws it (not the live fallback).
func baked() -> bool:
	return _tex != null


## The image's size on screen now (px): its board size x BOARD_SHARE, on this screen's height.
func shown_size() -> Vector2:
	if _tex == null:
		return _live.get_combined_minimum_size()
	var h := get_viewport_rect().size.y if is_inside_tree() else 720.0
	return (_tex.get_size() * BOARD_SHARE * h / BOARD_H).ceil()


func _fit() -> void:
	custom_minimum_size = shown_size()
	size = custom_minimum_size
	pivot_offset = size * 0.5
	rotation_degrees = tilt_deg if _tex != null else 0.0  # the live stamp tilts itself
	queue_redraw()


func _draw() -> void:
	if _tex != null:
		draw_texture_rect(_tex, Rect2(Vector2.ZERO, size), false)
