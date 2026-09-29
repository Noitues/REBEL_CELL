class_name CrewChip
extends Button
## A small crew Polaroid (Animation pass ANIM-4): an operative's own face on white paper
## with the name's first letters under it. The City Grid's Site card lays the living crew
## out as chips (press one, or drag it onto JACK IN, to pick who runs it); the HQ drags an
## operative's dossier as one. Emits Button signals; the screen decides what a press means.
## View only.
##
## Art pass W8b (§10.2, critique gifs/09): a picked chip is stamped (a CELL_PINK edge and a
## round stamp with the JACK IN plug on the photo's corner), so the pick is seen at once;
## the caption never goes under `caption` (a name too long shows its initial and number).

## Chip size at text scale 1.0 (px); it grows with the text size.
const CHIP_SIZE := Vector2(60, 76)
## The paper border round the photo (px at scale 1.0), the caption's type step.
const BORDER := 4.0
const CAPTION_STEP := UiTheme.CAPTION
## The pick's stamp: its radius as a share of the chip's width, its edge (px), the
## hover/focus glow's reach and alpha, and the ink edge's alpha.
const STAMP_SHARE := 0.24
const STAMP_EDGE := 3.0
const GLOW := 3.0
const GLOW_ALPHA := 0.5
const EDGE_ALPHA := 0.4

var class_id: StringName = &""
var operative_id: StringName = &""
var display_name: String = ""
## Picked to run (stamped).
var picked: bool = false:
	set(v):
		picked = v
		queue_redraw()
var _hot: bool = false


func _init(p_class: StringName = &"", p_operative: StringName = &"", p_name: String = "") -> void:
	class_id = p_class
	operative_id = p_operative
	display_name = p_name
	custom_minimum_size = CHIP_SIZE * Settings.text_scale
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	# The caption is drawn from the operative's name as given (never a translation key).
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## Shows another operative (the Polaroid beside JACK IN follows the pick).
func show_operative(p_class: StringName, p_operative: StringName, p_name: String) -> void:
	class_id = p_class
	operative_id = p_operative
	display_name = p_name
	queue_redraw()


## The caption as drawn at `px` for the chip's width: the whole name,
## else its initial and its last word ("B 2": two Breakers read apart), never cut.
func caption_text(px: int) -> String:
	var text := display_name.to_upper()
	var room := (size.x if size.x > 0.0 else custom_minimum_size.x) - BORDER * Settings.text_scale
	var f := Palette.marker()
	if f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= room:
		return text
	var words := text.split(" ", false)
	if words.is_empty():
		return text
	return "%s %s" % [words[0].left(1), words[words.size() - 1]] if words.size() > 1 else words[0].left(1)


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	if _hot and not disabled:
		draw_rect(r.grow(GLOW), Color(Palette.FOCUS, GLOW_ALPHA))
	if _hot and has_focus():
		StyleBoxBrackets.draw_on(self, r, Palette.FOCUS)
	draw_rect(r, Palette.PAPER)
	draw_rect(r, Palette.CELL_PINK if picked else Color(Palette.INK, EDGE_ALPHA), false, STAMP_EDGE if picked else 1.0)
	var b := BORDER * s
	var side := size.x - b * 2.0
	PortraitArt.draw(self, Rect2(b, b, side, side), PortraitArt.operative_subject(class_id, operative_id, display_name))
	var f := Palette.marker()
	var fs := UiTheme.font_px(CAPTION_STEP)
	draw_string(f, Vector2(b * 0.5, size.y - b), caption_text(fs), HORIZONTAL_ALIGNMENT_CENTER, size.x - b, fs, Palette.INK)
	if picked:
		# The pick's stamp: a pink disc with the JACK IN plug, on the photo's top right.
		var sr := size.x * STAMP_SHARE
		var c := Vector2(size.x - sr * 0.7, sr * 0.7)
		draw_circle(c, sr, Palette.CELL_PINK)
		draw_arc(c, sr, 0, TAU, 20, Palette.INK, 1.0)
		StatIcon.draw(self, c, sr * 0.7, StatIcon.JACK_IN, Palette.INK)
