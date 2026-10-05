class_name PencilWords
extends Control
## ART-10 4C: a short grease-pencil phrase written on the screen (ART_BIBLE v2 §1.2; round 33
## `title_screen.jpg`). With `art` it shows the concept's own pencil (round 33 title.py
## `slogan()`: NEVER SLEEP + the crown, baked by tools/art/bake_menus_r33.py into
## `assets/ui/menus/pencil/motto.png`). Without art (words the concept never drew, the HQ's
## TRUST NO ONE) it writes the words in Permanent Marker as wax with its under-shadow, tilted.
## Short words only, true to the game (the Cell's motto); never a live number. View only.

const STEP := UiTheme.HEADING
const MOTTO_ART := "res://assets/ui/menus/pencil/motto.png"
## The crown doodle's size (px) and its gap after the words (drawn words only).
const CROWN := Vector2(34, 22)

var words: String = ""
var tilt: float = 0.0
var crown := false
var _tex: Texture2D = null


## Where the motto sits on the title, relative to the sign's top left (the concept's own
## placement: title.py `slogan()` against `BOARD`, in game px).
static func motto_at() -> Vector2:
	var m: Array = PencilPlan.meta().get("motto_box", [0, 0, 0, 0])
	var sb: Array = NeonSign.meta().get("sign_box", [0, 0, 0, 0])
	return Vector2(float(m[0]) - float(sb[0]), float(m[1]) - float(sb[1])) * PencilPlan.BOARD_TO_GAME


func _init(p_words: String = "", p_tilt: float = 0.0, p_crown: bool = false, p_art: String = "") -> void:
	words = p_words
	tilt = p_tilt
	crown = p_crown
	if p_art != "" and ResourceLoader.exists(p_art):
		_tex = load(p_art) as Texture2D
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


func _get_minimum_size() -> Vector2:
	if _tex != null:
		return _tex.get_size() * PencilPlan.BOARD_TO_GAME
	var px := Chrome.px(STEP)
	var w := Chrome.pencil_font().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	return Vector2(ceilf(w + (CROWN.x + 10.0 if crown else 0.0)), ceilf(px * 1.5))


func _draw() -> void:
	if _tex != null:
		draw_texture_rect(_tex, Rect2(Vector2.ZERO, _tex.get_size() * PencilPlan.BOARD_TO_GAME), false)
		return
	var px := Chrome.px(STEP)
	var m := get_minimum_size()
	draw_set_transform(m * 0.5, deg_to_rad(tilt), Vector2.ONE)
	var at := Vector2(-m.x * 0.5, px * 0.4)
	PencilPlan.wax_text(self, at, words, px)
	if crown:
		var o := Vector2(m.x * 0.5 - CROWN.x, -CROWN.y * 0.5)
		PencilPlan.wax_line(self, PackedVector2Array([o + Vector2(0, CROWN.y), o, o + Vector2(CROWN.x * 0.3, CROWN.y * 0.55),
			o + Vector2(CROWN.x * 0.5, 0), o + Vector2(CROWN.x * 0.7, CROWN.y * 0.55), o + Vector2(CROWN.x, 0), o + Vector2(CROWN.x, CROWN.y),
			o + Vector2(0, CROWN.y)]), 3.0)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
