class_name HoloSticker
extends Button
## ART-9 4A (ART_BIBLE v2 §4.10 "a colourful holographic LEAVE sticker with a pink chevron
## arrow", §1.2 "Vinyl sticker"): a verb sticker button. The sticker itself is 1B's VinylSticker
## (Anton, ink keyline, extrude, white die-cut, gloss and its sweep; holo foil for LEAVE), with a
## pink plate under the verb when it has one ("THE MAINFRAME"). `word` makes a plain word sticker
## ("FIGHT WON" in yellow, "SKIP" in white, the node's "TERMINAL"). The button is the focus stop;
## hover and focus put the sticker in its HOVER state (lift, curl, sweep), a press in PRESSED.

## Verb and plate lettering (px at scale 1).
const VERB_PX := 50
const PLATE_PX := 15
## The plate's padding and its overlap with the sticker's foot (px at scale 1).
const PLATE_PAD := Vector2(8, 2)
const PLATE_TUCK := 10.0

var verb: String = ""
var plate: String = ""
var text_scale: float = 1.0
## The verb's lettering at scale 1 (a word sticker may set its own).
var verb_px_base: int = VERB_PX
var sticker: VinylSticker
var _plate: Control


func _init(p_verb: String = "", p_plate: String = "", ts: float = 1.0, fill: int = VinylSticker.Fill.HOLO, p_verb_px: int = VERB_PX) -> void:
	verb = p_verb
	plate = p_plate
	text_scale = ts
	verb_px_base = p_verb_px
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())
	sticker = VinylSticker.new()
	sticker.name = "Vinyl"
	sticker.text = verb
	sticker.shape = VinylSticker.Shape.WORD
	sticker.fill = fill
	# the vinyl's lettering follows the player's text size itself: ask for this sticker's size
	sticker.font_step = maxi(1, roundi(verb_px_base * ts / maxf(0.01, Settings.text_scale)))
	sticker.seed = absi(verb.hash()) % 997
	sticker.ambient_sweep = true  # the queue sweeps only the screen's primary (B1d)
	sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Its size from the start (the vinyl measures itself when it is built): the page lays out
	# once, the same at once and after its entrance.
	sticker.set(&"_built", true)
	sticker.call(&"_rebuild")
	add_child(sticker)
	if plate != "":
		_plate = Control.new()
		_plate.name = "Plate"
		_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_plate.draw.connect(_draw_plate)
		add_child(_plate)
	sticker.resized.connect(_fit)
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(_set_hot.bind(true))
	focus_exited.connect(_set_hot.bind(false))
	button_down.connect(func() -> void: sticker.set_state(VinylSticker.State.PRESSED))
	button_up.connect(func() -> void: sticker.set_state(VinylSticker.State.HOVER if (has_focus() or is_hovered()) else VinylSticker.State.REST))
	_fit()


func _ready() -> void:
	if _fold_room_base != "":
		_apply_fold_room()  # in the tree the fold's real px (the viewport's height) is known
	_fit()


## A plain word sticker: `text` with fill `p_fill` (VinylSticker.Fill), no plate.
static func word(text: String, p_fill: int, ts: float = 1.0, verb_px: int = VERB_PX) -> HoloSticker:
	return HoloSticker.new(text, "", ts, p_fill, verb_px)


## The sticker's size for its words (px): the vinyl (once built, else an estimate) and the plate.
func sticker_size() -> Vector2:
	var f := Palette.display()
	var vs := roundi(verb_px_base * text_scale)
	# the sticker's body (its die-cut outline); the vinyl's shadow room hangs outside the button
	var v := sticker.body_rect.size if sticker != null and sticker.body_rect.size.x > 1.0 else Vector2(f.get_string_size(verb, HORIZONTAL_ALIGNMENT_LEFT, -1, vs).x + vs * 0.9, vs * 1.3)
	return v + Vector2(0, _plate_size().y - PLATE_TUCK * text_scale if plate != "" else 0.0)


func _plate_size() -> Vector2:
	var f := Palette.display()
	var ps := roundi(PLATE_PX * text_scale)
	return Vector2(f.get_string_size(plate, HORIZONTAL_ALIGNMENT_LEFT, -1, ps).x, f.get_height(ps)) + PLATE_PAD * 2.0 * text_scale


func _fit() -> void:
	custom_minimum_size = sticker_size()
	sticker.position = Vector2((custom_minimum_size.x - sticker.body_rect.size.x) * 0.5, 0.0) - sticker.body_rect.position
	if _plate != null:
		var ps := _plate_size()
		_plate.size = ps
		_plate.position = Vector2((custom_minimum_size.x - ps.x) * 0.5, sticker.body_rect.size.y - PLATE_TUCK * text_scale)
	pivot_offset = custom_minimum_size * 0.5


func _set_hot(on: bool) -> void:
	if sticker == null or disabled:
		return
	sticker.set_state(VinylSticker.State.HOVER if on else VinylSticker.State.REST)


## G2R2-4: pads the sticker's right edge with the focus fold's room (no-break spaces of its own
## lettering, as the run end's BACK TO HQ does), so the peel-back never covers the last letters.
## G2 polish P1: the room is measured against the fold itself (`peel_px`: it follows the text scale and the
## viewport) and again when the sticker is ready in the tree, where the real viewport height is known.
func add_fold_room() -> void:
	if _fold_room_base == "":
		_fold_room_base = sticker.text
	_apply_fold_room()


var _fold_room_base: String = ""

## A runaway guard for the fold room's spaces, not a tuning value.
const FOLD_ROOM_MAX_SPACES := 40
## The share of the lettering's px the fold keeps clear past a letter's advance (the drawn glyph's outline and slant).
const FOLD_ROOM_OVERHANG_SHARE := 0.1


func _apply_fold_room() -> void:
	sticker.text = _fold_room_base
	var guard := 0
	# the drawn letter stands a little past its advance (outline, slant): keep a share of the lettering clear too
	var overhang := float(sticker.get(&"_px")) * FOLD_ROOM_OVERHANG_SHARE
	while guard < FOLD_ROOM_MAX_SPACES and room_past_last_letter() < sticker.peel_px() + overhang:
		sticker.text += " "
		guard += 1
	_fit()


## px between the last drawn letter's right edge and the sticker body's right edge.
func room_past_last_letter() -> float:
	var f := Palette.display()  # the display face's own advances (the same as the run end's BACK TO HQ is held to)
	var px: int = sticker.get(&"_px")
	var last_end := 0.0
	for g in sticker.get(&"_glyphs"):
		last_end = maxf(last_end, (g[1] as Vector2).x + f.get_string_size(g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return sticker.body_rect.end.x - last_end


func _draw_plate() -> void:
	var f := Palette.display()
	var ps := roundi(PLATE_PX * text_scale)
	var r := Rect2(Vector2.ZERO, _plate.size)
	_plate.draw_rect(r, Palette.CELL_PINK)
	_plate.draw_rect(r, Palette.STICKER_DIE_CUT, false, 2.0)
	HighContrast.draw_text(_plate, f, Vector2(PLATE_PAD.x * text_scale, PLATE_PAD.y * text_scale + f.get_ascent(ps)), plate, HORIZONTAL_ALIGNMENT_LEFT, -1, ps, Palette.STICKER_DIE_CUT)
