class_name PencilWords
extends Control
## ART-10 4C: a short grease-pencil phrase written on the screen (ART_BIBLE v2 §1.2; round 33
## `title_screen.jpg` "NEVER SLEEP" and the crown on the sign): yellow wax with its
## under-shadow, tilted, optionally with the three-point crown doodle. Short words only,
## true to the game (the Cell's motto); never a live number. Words are given translated.
## View only.

const STEP := UiTheme.HEADING
## The crown doodle's size (px) and its gap after the words.
const CROWN := Vector2(34, 22)

var words: String = ""
var tilt: float = 0.0
var crown := false


func _init(p_words: String = "", p_tilt: float = 0.0, p_crown: bool = false) -> void:
	words = p_words
	tilt = p_tilt
	crown = p_crown
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


func _get_minimum_size() -> Vector2:
	var px := Chrome.px(STEP)
	var w := Chrome.pencil_font().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	return Vector2(ceilf(w + (CROWN.x + 10.0 if crown else 0.0)), ceilf(px * 1.5))


func _draw() -> void:
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
