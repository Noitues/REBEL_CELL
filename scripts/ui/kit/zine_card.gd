class_name ZineCard
extends Button
## A card as a zine sticker (STYLE_GUIDE 4): black / pink / paper variants, slight
## rotation, tape strip, title in Anton, cost in marker; hovered or focused cards lift
## and glow acid. Emits Button signals; the scene decides what a press means.

enum Variant { PAPER, BLACK, PINK }
## STICKER: the zine card (hand, loot). CHIP / CARD_TILE: shop tiles (reference: the
## Modem's microchips and card builder) with an icon, a name and a Cycle price.
enum Look { STICKER, CHIP, CARD_TILE }

var card_title: String = ""
var cost: int = 0
var description: String = ""
var variant: int = Variant.PAPER
var hotkey: String = ""
var look: int = Look.STICKER
## Icon colour for shop tiles.
var accent: Color = Palette.NET_CYAN
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
	rotation_degrees = float(((hash(card_title) % 9) - 4)) if look == Look.STICKER else 0.0


## Turns this into a shop tile (chip or card builder) in `p_accent`.
func as_tile(p_look: int, p_accent: Color) -> ZineCard:
	look = p_look
	accent = p_accent
	custom_minimum_size = Vector2(118, 150)
	return self


func _set_lift(on: bool) -> void:
	_lifted = on
	queue_redraw()


func _draw() -> void:
	if look != Look.STICKER:
		_draw_tile()
		return
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
	_chip(Vector2(size.x - 24, size.y - 22), fg)
	if hotkey != "":
		draw_string(Palette.marker(), Vector2(8, size.y - 8), "[%s]" % hotkey, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, fg)
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.5))


func _draw_tile() -> void:
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Color(0.02, 0.05, 0.11, 0.95))
	if hot:
		draw_rect(rect.grow(3), Color(Palette.CELL_PINK, 0.3), false, 6.0)
	draw_rect(rect, Palette.CELL_PINK if hot else Color(accent, 0.7), false, 1.5)
	var icon_c := Vector2(size.x / 2.0, 50)
	# Glow under the icon.
	draw_circle(icon_c, 34, Color(accent, 0.08))
	draw_circle(icon_c, 24, Color(accent, 0.1))
	if look == Look.CHIP:
		_big_chip(icon_c, accent)
	else:
		_mini_card(icon_c, accent)
	var name_lines := _wrap(card_title.to_upper(), 13)
	for i in mini(name_lines.size(), 2):
		draw_string(Palette.mono(), Vector2(4, 100 + i * 13), name_lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, 11, Palette.PAPER)
	if cost >= 0:
		var price := "%d" % cost
		var pw := Palette.mono().get_string_size(price, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x
		var px := size.x / 2.0 - (pw + 18) / 2.0
		draw_arc(Vector2(px + 6, size.y - 15), 6, 0, TAU, 16, Palette.CELL_ACID, 1.5)
		draw_circle(Vector2(px + 6, size.y - 15), 2, Palette.CELL_ACID)
		draw_string(Palette.mono(), Vector2(px + 17, size.y - 10), price, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.CELL_ACID)
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))


## The reference's glowing microchip: a die with pins and a circuit square inside.
func _big_chip(c: Vector2, col: Color) -> void:
	var r := Rect2(c - Vector2(20, 20), Vector2(40, 40))
	draw_rect(r.grow(3), Color(col, 0.15))
	draw_rect(r, Palette.NIGHT_SKY)
	draw_rect(r, col, false, 2.0)
	draw_rect(r.grow(-8), Color(col, 0.35))
	draw_rect(r.grow(-8), col, false, 1.5)
	draw_rect(r.grow(-14), col)
	var pin := Color(col, 0.85)
	for k in 5:
		var o := -16.0 + k * 8.0
		draw_line(c + Vector2(o, -20), c + Vector2(o, -26), pin, 1.5)
		draw_line(c + Vector2(o, 20), c + Vector2(o, 26), pin, 1.5)
		draw_line(c + Vector2(-20, o), c + Vector2(-26, o), pin, 1.5)
		draw_line(c + Vector2(20, o), c + Vector2(26, o), pin, 1.5)


## A little paper card, tilted, for the card builder.
func _mini_card(c: Vector2, col: Color) -> void:
	draw_set_transform(c, -0.12, Vector2.ONE)
	draw_rect(Rect2(Vector2(-19, -25), Vector2(40, 52)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.NOTE_PAPER)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.INK, false, 1.0)
	draw_rect(Rect2(Vector2(-10, -32), Vector2(16, 7)), Palette.NOTE_TAPE)
	var initials := ""
	for w in card_title.split(" "):
		if w != "" and initials.length() < 2:
			initials += w[0].to_upper()
	draw_string(Palette.display(), Vector2(-22, 8), initials, HORIZONTAL_ALIGNMENT_CENTER, 40, 22, col.darkened(0.2))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## A small microchip mark in the corner (the reference's chip stickers).
func _chip(c: Vector2, col: Color) -> void:
	var r := Rect2(c - Vector2(8, 8), Vector2(16, 16))
	draw_rect(r, Color(col, 0.15))
	draw_rect(r, Color(col, 0.7), false, 1.5)
	draw_rect(r.grow(-5), Color(col, 0.7))
	for k in 3:
		var o := -5.0 + k * 5.0
		draw_line(c + Vector2(o, -8), c + Vector2(o, -11), Color(col, 0.7), 1.0)
		draw_line(c + Vector2(o, 8), c + Vector2(o, 11), Color(col, 0.7), 1.0)
		draw_line(c + Vector2(-8, o), c + Vector2(-11, o), Color(col, 0.7), 1.0)
		draw_line(c + Vector2(8, o), c + Vector2(11, o), Color(col, 0.7), 1.0)


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
