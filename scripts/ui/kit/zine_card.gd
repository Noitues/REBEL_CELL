class_name ZineCard
extends Button
## A card as a zine sticker (STYLE_GUIDE 4): black / pink / paper variants, slight
## rotation, tape strip, title in Anton, cost in marker; hovered or focused cards lift
## and glow acid. Emits Button signals; the scene decides what a press means.

enum Variant { PAPER, BLACK, PINK }

var card_title: String = ""
var cost: int = 0
var description: String = ""
var variant: int = Variant.PAPER
var hotkey: String = ""
var _lifted: bool = false


func _init(p_title: String = "", p_cost: int = 0, p_description: String = "", index: int = 0) -> void:
	card_title = p_title
	cost = p_cost
	description = p_description
	variant = index % 3
	hotkey = str(index + 1) if index < 9 else ""
	custom_minimum_size = Vector2(112, 148)
	flat = true
	focus_mode = Control.FOCUS_ALL
	# Draws its own hover/focus glow; no theme box around the sticker.
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	tooltip_text = p_description
	mouse_entered.connect(_set_lift.bind(true))
	mouse_exited.connect(_set_lift.bind(false))
	focus_entered.connect(_set_lift.bind(true))
	focus_exited.connect(_set_lift.bind(false))


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = float(((hash(card_title) % 9) - 4))


func _set_lift(on: bool) -> void:
	_lifted = on
	queue_redraw()


func _draw() -> void:
	var bg := Palette.PAPER
	var fg := Palette.INK
	match variant:
		Variant.BLACK:
			bg = Palette.INK
			fg = Palette.PAPER
		Variant.PINK:
			bg = Palette.CELL_PINK
			fg = Palette.INK
	var rect := Rect2(Vector2.ZERO, size)
	if _lifted:
		draw_rect(rect.grow(4), Color(Palette.CELL_ACID, 0.5))
	draw_rect(rect, bg)
	draw_rect(rect, Palette.INK if variant != Variant.BLACK else Palette.PAPER, false, 2.0)
	draw_rect(Rect2(size.x * 0.3, -5, 44, 12), Palette.TAPE)
	draw_string(Palette.display(), Vector2(8, 34), card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, 17, fg)
	# cost < 0 = no cost circle (Firmware and Daemon offers).
	if cost >= 0:
		var r := 13.0 if cost < 100 else 17.0
		draw_circle(Vector2(size.x - r - 5, r + 5), r, Palette.CELL_ACID if variant != Variant.PINK else Palette.PAPER)
		draw_string(Palette.marker(), Vector2(size.x - r * 2 - 1, r + 11), str(cost), HORIZONTAL_ALIGNMENT_LEFT, -1, 14 if cost >= 100 else 16, Palette.INK)
	var lines := _wrap(description, 16)
	for i in mini(lines.size(), 5):
		draw_string(Palette.mono(), Vector2(8, 58 + i * 15), lines[i], HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, 11, fg)
	if hotkey != "":
		draw_string(Palette.marker(), Vector2(8, size.y - 8), "[%s]" % hotkey, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, fg)
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.5))


static func _wrap(text: String, width: int) -> PackedStringArray:
	var out := PackedStringArray()
	var line := ""
	for word in text.split(" "):
		if line.length() + word.length() + 1 > width and line != "":
			out.append(line)
			line = word
		else:
			line = word if line == "" else line + " " + word
	if line != "":
		out.append(line)
	return out
