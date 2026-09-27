class_name CrewChip
extends Button
## A small crew Polaroid (Animation pass ANIM-4): an operative's own face on white paper
## with the name's first letters under it. The City Grid's Site card lays the living crew
## out as chips to drag onto JACK IN (who runs it); the HQ drags an operative's dossier as
## one. Emits Button signals; the screen decides what a press means. View only.

## Chip size at text scale 1.0 (px); it grows with the text size.
const CHIP_SIZE := Vector2(46, 58)
## The paper border round the photo and the caption's lettering at scale 1.0 (px).
const BORDER := 4.0
const CAPTION_SIZE := 10
## The least caption lettering (px): a long name shrinks to fit down to it.
const CAPTION_MIN := 6

var class_id: StringName = &""
var operative_id: StringName = &""
var display_name: String = ""
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


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	if _hot and not disabled:
		draw_rect(r.grow(3), Color(Palette.CELL_ACID, 0.5))
	draw_rect(r, Palette.PAPER)
	draw_rect(r, Color(Palette.INK, 0.4), false, 1.0)
	var b := BORDER * s
	var side := size.x - b * 2.0
	PortraitArt.draw(self, Rect2(b, b, side, side), PortraitArt.operative_subject(class_id, operative_id, display_name))
	# The whole name, a size smaller while it is wider than the chip (two "Breaker"s must
	# read apart).
	var f := Palette.marker()
	var text := display_name.to_upper()
	var fs := roundi(CAPTION_SIZE * s)
	while fs > CAPTION_MIN and f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > size.x - b:
		fs -= 1
	draw_string(f, Vector2(b * 0.5, size.y - b), text, HORIZONTAL_ALIGNMENT_CENTER, size.x - b, fs, Palette.INK)
