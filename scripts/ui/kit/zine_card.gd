class_name ZineCard
extends Button
## A card as a zine sticker (STYLE_GUIDE 4): black / pink / paper variants, slight
## rotation, tape strip, title in Anton, cost in marker; hovered or focused cards lift
## and glow acid. Emits Button signals; the scene decides what a press means.

## Right-click (inspect): the scene opens the detail popup.
signal inspected

enum Variant { PAPER, BLACK, PINK }
## Selection marks drawn over the card.
enum Mark { NONE, CROSS, CIRCLE }
## STICKER: the zine card (hand, loot). CHIP / CARD_TILE: shop tiles (reference: the
## Modem's microchips and card builder) with an icon, a name and a Cycle price.
enum Look { STICKER, CHIP, CARD_TILE, SLICE_TILE }

var card_title: String = ""
var cost: int = 0
var description: String = ""
var variant: int = Variant.PAPER
var hotkey: String = ""
var look: int = Look.STICKER
## Icon colour for shop tiles.
var accent: Color = Palette.NET_CYAN
## SLICE_TILE: the slice type and output drawn as the wheel draws them.
var slice_type: int = RC.SliceType.ATTACK
var slice_output: int = 0
## CARD_TILE icon: "" (mini card), "shred" (card through a shredder), "deck" (a fanned stack).
var icon_kind: String = ""
var mark: int = Mark.NONE:
	set(v):
		mark = v
		queue_redraw()
var _lifted: bool = false
## Hand index this card drags as (H20 drag-to-target), -1 = not draggable.
var drag_index: int = -1
## What the card does as pictograms (H21: readable without words): [{kind, amount,
## type}] from pictos_of(); drawn in a row above the foot of the sticker.
var pictos: Array[Dictionary] = []
## A pad is in use: the focused card shows the button that plays it.
var pad_hint: String = ""
## Pictogram row: icon radius and spacing at scale 1.0 (px).
const PICTO_RADIUS := 8.0
const PICTO_STEP := 34.0
const PICTO_FONT := 12
## Short tags for the scripted card effects (by handler script name; H22: they had no
## pictogram). "%d" takes the effect's amount.
const CUSTOM_PICTOS := {"calibrate_handler": "FREE NUDGE x%d", "momentum_handler": "SPIN %d+", "ring_lock_handler": "RING LOCK",
	"steady_hand_handler": "PERFECT: RAM+", "undock_handler": "UNDOCK"}
## Slice icon for each effect that does what a slice does.
const EFFECT_SLICE := {RC.EffectType.DEAL_DAMAGE: RC.SliceType.ATTACK, RC.EffectType.GAIN_BLOCK: RC.SliceType.DEFEND,
	RC.EffectType.GAIN_SHIELD: RC.SliceType.SHIELD, RC.EffectType.EVADE: RC.SliceType.EVADE, RC.EffectType.HEAL: RC.SliceType.HEAL,
	RC.EffectType.DEPLOY_DRONE: RC.SliceType.DEPLOY, RC.EffectType.APPLY_STATUS: RC.SliceType.AFFLICT}
## Lettering scale (the combat hand follows Settings.text_scale; see scaled()).
var text_scale: float = 1.0
## Sticker size and lettering at scale 1.0.
const STICKER_SIZE := Vector2(112, 148)
const TITLE_SIZE := 17
const BODY_SIZE := 11
const BODY_LINE := 15.0
const BODY_TOP := 58.0


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


## The card's effects as pictograms: spin / nudge / flip / respin arrows, slice icons for
## damage, block, shield, evade, heal, deploy, statuses, and short tags for the rest.
static func pictos_of(card: CardData) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if card == null:
		return out
	for e in card.effects:
		if e == null:
			continue
		match e.type:
			RC.EffectType.SPIN:
				out.append({"kind": "spin", "amount": e.amount})
			RC.EffectType.NUDGE:
				out.append({"kind": "nudge", "amount": maxi(1, e.amount), "inner": e.ring_scope == RC.RingScope.INNER})
			RC.EffectType.FLIP:
				out.append({"kind": "flip", "amount": 0})
			RC.EffectType.RESPIN:
				out.append({"kind": "respin", "amount": 0})
			RC.EffectType.GAIN_RAM:
				if e.amount != 0:
					out.append({"kind": "tag", "text": "RAM%+d" % e.amount})
			RC.EffectType.DRAW_CARDS:
				out.append({"kind": "tag", "text": "DRAW %d" % e.amount})
			RC.EffectType.FREEZE:
				out.append({"kind": "tag", "text": "FREEZE"})
			RC.EffectType.MODIFY_RESISTANCE:
				out.append({"kind": "tag", "text": "RES%+d" % e.amount})
			RC.EffectType.HUB_BREACH:
				out.append({"kind": "tag", "text": "BREACH"})
			RC.EffectType.CLEANSE:
				out.append({"kind": "tag", "text": "CLEANSE"})
			RC.EffectType.DRAIN_RAM:
				out.append({"kind": "tag", "text": "RAM-%d" % absi(e.amount)})
			RC.EffectType.SNAP_TO_CENTER:
				out.append({"kind": "tag", "text": "SNAP"})
			RC.EffectType.DOUBLE_NUDGE_CARDS:
				out.append({"kind": "tag", "text": "2x NUDGE"})
			RC.EffectType.RETRIGGER:
				out.append({"kind": "tag", "text": "AGAIN"})
			RC.EffectType.CUSTOM:
				if e.custom_handler != null:
					var key := e.custom_handler.resource_path.get_file().get_basename()
					if CUSTOM_PICTOS.has(key):
						var text := String(CUSTOM_PICTOS[key])
						out.append({"kind": "tag", "text": text % e.amount if text.contains("%d") else text})
			_:
				if EFFECT_SLICE.has(e.type):
					out.append({"kind": "slice", "type": EFFECT_SLICE[e.type], "amount": e.amount,
						"status": e.status if e.type == RC.EffectType.APPLY_STATUS else RC.Status.NONE})
	return out


## Sets the pictograms from the card's data (combat hand, loot, shop, deck views).
func with_card(card: CardData) -> ZineCard:
	pictos = pictos_of(card)
	return self


## Scales the sticker and its lettering by `s` (the combat hand at text scale > 1).
func scaled(s: float) -> ZineCard:
	text_scale = s
	custom_minimum_size = STICKER_SIZE * s
	return self


## Drag the card onto a target (the combat scene decides what the drop means).
func _get_drag_data(_at_position: Vector2) -> Variant:
	if drag_index < 0 or disabled:
		return null
	var ghost := ZineCard.new(card_title, cost, description, drag_index).scaled(text_scale)
	ghost.pictos = pictos
	ghost.modulate.a = 0.8
	ghost.size = ghost.custom_minimum_size
	var holder := Control.new()
	holder.add_child(ghost)
	ghost.position = -ghost.size * 0.5
	set_drag_preview(holder)
	return {"hand_index": drag_index}


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
		inspected.emit()
		accept_event()


func _set_lift(on: bool) -> void:
	_lifted = on
	queue_redraw()


func _draw() -> void:
	if look != Look.STICKER:
		_draw_tile_any()
	else:
		_draw_sticker()
	_draw_price_tag()
	match mark:
		Mark.CROSS:
			HandMarks.draw_x(self, Rect2(Vector2.ZERO, size), DripButton.DRIP_PINK)
		Mark.CIRCLE:
			HandMarks.draw_drip_circle(self, size * 0.5, size * 0.5 * Vector2(0.95, 0.8), DripButton.DRIP_PINK)


func _draw_sticker() -> void:
	var bg := Palette.PAPER
	var fg := Palette.INK
	match variant:
		Variant.BLACK:
			bg = Palette.INK
			fg = Palette.PAPER
		Variant.PINK:
			bg = Palette.STICKER_PINK
			fg = Palette.INK
	var rect := Rect2(Vector2.ZERO, size)
	if _lifted:
		draw_rect(rect.grow(4), Color(Palette.CELL_ACID, 0.5))
	draw_rect(rect, bg)
	draw_rect(rect, Palette.INK if variant != Variant.BLACK else Palette.PAPER, false, 2.0)
	draw_rect(Rect2(size.x * 0.3, -5, 44, 12), Palette.TAPE)
	var s := text_scale
	# cost < 0 = no cost circle (Firmware and Daemon offers). The title stops short of it.
	var title_w := size.x - 16
	if cost >= 0:
		var r := (13.0 if cost < 100 else 17.0) * s
		title_w -= r * 2 + 4
		draw_circle(Vector2(size.x - r - 5, r + 5), r, Palette.CELL_ACID if variant != Variant.PINK else Palette.PAPER)
		draw_string(Palette.marker(), Vector2(size.x - r * 2 - 5, r + 5 + 6 * s), str(cost), HORIZONTAL_ALIGNMENT_CENTER, r * 2, roundi((14 if cost >= 100 else 16) * s), Palette.INK)
	var title_size := roundi(TITLE_SIZE * s)
	while title_size > 9 and Palette.display().get_string_size(card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, title_size).x > title_w:
		title_size -= 1  # long names shrink to fit beside the cost
	draw_string(Palette.display(), Vector2(8, 34 * s), card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, title_w, title_size, fg)
	# The body wraps to the sticker's width; what doesn't fit ends in an ellipsis (the full
	# text is the tooltip and the inspect).
	var body := roundi(BODY_SIZE * s)
	var lines := wrap_px(description, size.x - 16, body)
	var foot := (26.0 + (PICTO_RADIUS * 2.0 + 6.0 if not pictos.is_empty() else 0.0)) * s
	var room := maxi(1, int((size.y - BODY_TOP * s - foot) / (BODY_LINE * s)))
	for i in mini(lines.size(), room):
		var t := lines[i]
		if i == room - 1 and lines.size() > room:
			t = t.substr(0, maxi(0, t.length() - 1)) + "…"
		draw_string(Palette.mono(), Vector2(8, BODY_TOP * s + i * BODY_LINE * s), t, HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, body, fg)
	_draw_pictos(Vector2(8 + PICTO_RADIUS * s, size.y - 26.0 * s - PICTO_RADIUS * s - 2.0), s, fg)
	_chip(Vector2(size.x - 24, size.y - 22), fg)
	var key := pad_hint if pad_hint != "" and has_focus() else hotkey
	if key != "":
		draw_string(Palette.marker(), Vector2(8, size.y - 8), "[%s]" % key, HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(14 * s), fg)
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
	elif look == Look.SLICE_TILE:
		# A wedge of wheel with the slice icon and value, as on the spinner.
		var pts := PackedVector2Array()
		for k in 9:
			var a := lerpf(-PI * 0.5 - 0.5, -PI * 0.5 + 0.5, k / 8.0)
			pts.append(icon_c + Vector2(0, 50) + Vector2(cos(a), sin(a)) * 76)
		for k in 9:
			var a := lerpf(-PI * 0.5 + 0.5, -PI * 0.5 - 0.5, k / 8.0)
			pts.append(icon_c + Vector2(0, 50) + Vector2(cos(a), sin(a)) * 30)
		var sc := Palette.slice_color(slice_type)
		draw_colored_polygon(pts, Color(sc, 0.35))
		pts.append(pts[0])
		draw_polyline(pts, sc, 1.5)
		SliceIcon.draw_on_slice(self, icon_c + Vector2(0, -15), 11, slice_type, sc)
		if slice_output > 0:
			draw_string(Palette.display(), icon_c + Vector2(-20, 22), str(slice_output), HORIZONTAL_ALIGNMENT_CENTER, 40, 20, Palette.PAPER)
	elif icon_kind == "shred":
		_mini_card(icon_c + Vector2(0, -8), accent, false)
		draw_rect(Rect2(icon_c + Vector2(-30, 10), Vector2(60, 12)), Palette.DESK_METAL)
		draw_rect(Rect2(icon_c + Vector2(-30, 10), Vector2(60, 12)), accent, false, 1.5)
		for k in 6:
			draw_line(icon_c + Vector2(-18 + k * 7, 22), icon_c + Vector2(-20 + k * 7, 36), Palette.NOTE_PAPER, 2.0)
	elif icon_kind == "deck":
		for k in 3:
			draw_set_transform(icon_c + Vector2(-10 + k * 10, 4), -0.25 + k * 0.25, Vector2.ONE)
			draw_rect(Rect2(Vector2(-16, -24), Vector2(32, 44)), [Palette.NOTE_PAPER, Palette.STICKER_PINK, Palette.NOTE_YELLOW][k])
			draw_rect(Rect2(Vector2(-16, -24), Vector2(32, 44)), Palette.INK, false, 1.0)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	else:
		_mini_card(icon_c, accent)
	# H23 S8: the shade dims the art only; the name stays in the text colour.
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))
	var name_lines := _wrap(card_title.to_upper(), 13)
	for i in mini(name_lines.size(), 2):
		draw_string(Palette.mono(), Vector2(4, 100 + i * 13), name_lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, 11, Palette.TERMINAL_TEXT)
	if cost >= 0:
		var price := "%d" % cost
		var pw := Palette.mono().get_string_size(price, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x
		var px := size.x / 2.0 - (pw + 18) / 2.0
		draw_arc(Vector2(px + 6, size.y - 15), 6, 0, TAU, 16, Palette.CELL_ACID, 1.5)
		draw_circle(Vector2(px + 6, size.y - 15), 2, Palette.CELL_ACID)
		draw_string(Palette.mono(), Vector2(px + 17, size.y - 10), price, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.CELL_ACID)


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
func _mini_card(c: Vector2, col: Color, initials_on: bool = true) -> void:
	draw_set_transform(c, -0.12, Vector2.ONE)
	draw_rect(Rect2(Vector2(-19, -25), Vector2(40, 52)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.NOTE_PAPER)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.INK, false, 1.0)
	draw_rect(Rect2(Vector2(-10, -32), Vector2(16, 7)), Palette.NOTE_TAPE)
	var initials := ""
	for w in card_title.split(" "):
		if w != "" and initials.length() < 2 and initials_on:
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


## Word-wraps `text` to `width` px at `font_size` in the mono face.
static func wrap_px(text: String, width: float, font_size: int) -> PackedStringArray:
	var out := PackedStringArray()
	var line := ""
	for word in text.split(" "):
		var trial := word if line == "" else line + " " + word
		if line != "" and Palette.mono().get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > width:
			out.append(line)
			line = word
		else:
			line = trial
	if line != "":
		out.append(line)
	return out


## The pictogram row, left to right from `at` (the first icon's centre).
func _draw_pictos(at: Vector2, s: float, fg: Color) -> void:
	var r := PICTO_RADIUS * s
	var x := at.x
	var fs := roundi(PICTO_FONT * s)
	for p in pictos:
		var c := Vector2(x, at.y)
		var label := ""
		match String(p["kind"]):
			"spin", "respin":
				# A circular arrow: clockwise for a positive spin.
				var d := -1.0 if int(p["amount"]) < 0 else 1.0
				draw_arc(c, r, -PI * 0.9, PI * 0.6, 12, fg, 2.0 * s)
				var a := PI * 0.6 if d > 0.0 else -PI * 0.9
				var tip := c + Vector2(cos(a), sin(a)) * r
				var tg := Vector2(-sin(a), cos(a)) * d
				draw_colored_polygon(PackedVector2Array([tip + tg * 4.0 * s, tip + tg.orthogonal() * 3.5 * s, tip - tg.orthogonal() * 3.5 * s]), fg)
				label = "?" if String(p["kind"]) == "respin" else str(absi(int(p["amount"])))
			"nudge":
				# Two small arrows, one each way (a nudge card is aimed either way).
				for side in [-1.0, 1.0]:
					var t := c + Vector2(side * r, 0)
					draw_colored_polygon(PackedVector2Array([t, t - Vector2(side * r * 0.8, r * 0.6), t - Vector2(side * r * 0.8, -r * 0.6)]), fg)
				label = "×%d" % int(p["amount"]) + (" IN" if bool(p.get("inner", false)) else "")
			"flip":
				draw_line(c + Vector2(-r * 0.4, -r), c + Vector2(-r * 0.4, r), fg, 2.0 * s)
				draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.4, -r - 3 * s), c + Vector2(-r * 0.9, -r * 0.3), c + Vector2(0.1 * r, -r * 0.3)]), fg)
				draw_line(c + Vector2(r * 0.4, -r), c + Vector2(r * 0.4, r), fg, 2.0 * s)
				draw_colored_polygon(PackedVector2Array([c + Vector2(r * 0.4, r + 3 * s), c + Vector2(-0.1 * r, r * 0.3), c + Vector2(r * 0.9, r * 0.3)]), fg)
			"slice":
				SliceIcon.draw_icon(self, c, r, int(p["type"]), Palette.slice_color(int(p["type"])))
				var st := int(p.get("status", RC.Status.NONE))
				label = String(Palette.STATUS_GLYPHS.get(st, "")) if st != RC.Status.NONE else (str(int(p["amount"])) if int(p["amount"]) > 0 else "")
			"tag":
				draw_string(Palette.mono(), Vector2(c.x - r, c.y + fs * 0.35), String(p["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fg)
				x += Palette.mono().get_string_size(String(p["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 8.0 * s
				continue
		if label != "":
			draw_string(Palette.mono(), Vector2(c.x + r + 2.0 * s, c.y + fs * 0.35), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fg)
		x += PICTO_STEP * s + (Palette.mono().get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x if label.length() > 2 else 0.0)
		if x > size.x - 30.0:
			break


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


# --- H21 screens: price tags and big lettering on shop tiles ------------------------------

## A shop price (Cycles), drawn on a price tag with the coin (H21 #12: prices sat in the
## RAM-cost circle and read as a play cost; the circle keeps the card's real RAM cost).
## -1 = no price.
var price: int = -1
## The tag reads "N+" (a slice's price depends on the slot it overwrites).
var price_from: bool = false
## Price tag height, coin radius and lettering at scale 1.0 (px).
const PRICE_TAG_H := 20.0
const PRICE_COIN_R := 6.0
const PRICE_FONT := 14
## Shop tile lettering at scale 1.0 (the tile keeps its size; the lettering grows).
const TILE_NAME_SIZE := 11
const TILE_VALUE_SIZE := 20
## Largest scale of a slice tile's value (its wedge does not grow).
const TILE_VALUE_MAX_SCALE := 1.3


## Puts a shop price on the card or tile (a price tag with the coin, H21 #12).
func with_price(p_price: int, p_from: bool = false) -> ZineCard:
	price = p_price
	price_from = p_from
	queue_redraw()
	return self


## Scales a shop tile's lettering by `s` without growing the tile (H21 #15).
func tile_text(s: float) -> ZineCard:
	text_scale = s
	queue_redraw()
	return self


## The price as the tag reads it ("" without a price).
func price_text() -> String:
	if price < 0:
		return ""
	return ("%d+" if price_from else "%d") % price


## The price tag's rect (local): bottom right of a sticker, bottom centre of a tile.
func price_tag_rect() -> Rect2:
	var s := text_scale
	var fs := roundi(PRICE_FONT * s)
	var h := PRICE_TAG_H * s
	var tw := Palette.display().get_string_size(price_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var w := h * 0.45 + PRICE_COIN_R * 2.0 * s + 3.0 * s + tw + 6.0 * s
	var y := size.y - h - 4.0 * s
	if look == Look.STICKER:
		return Rect2(size.x - w - 4.0 * s, y, w, h)
	return Rect2((size.x - w) * 0.5, y, w, h)


func _draw_price_tag() -> void:
	if price < 0 or buy_button != null:
		return  # H23 S8: the buy button carries the price
	var s := text_scale
	var rt := price_tag_rect()
	var h := rt.size.y
	var pts := PackedVector2Array([rt.position + Vector2(h * 0.35, 0), rt.position + Vector2(rt.size.x, 0), rt.end,
		rt.position + Vector2(h * 0.35, h), rt.position + Vector2(0, h * 0.5)])
	# Out of reach (disabled in the shop): the tag turns pink.
	draw_colored_polygon(pts, Palette.NOTE_PINK if disabled else Palette.NOTE_YELLOW)
	pts.append(pts[0])
	draw_polyline(pts, Palette.INK, 1.0)
	draw_circle(rt.position + Vector2(h * 0.28, h * 0.5), 1.6 * s, Palette.INK)
	var coin := rt.position + Vector2(h * 0.45 + PRICE_COIN_R * s, h * 0.5)
	StatIcon.draw(self, coin, PRICE_COIN_R * s, StatIcon.CYCLES, Palette.INK)
	var fs := roundi(PRICE_FONT * s)
	draw_string(Palette.display(), Vector2(coin.x + PRICE_COIN_R * s + 3.0 * s, rt.position.y + h * 0.5 + fs * 0.36), price_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.INK)


## Tiles at text scale 1.0 draw as before; at other scales the lettering grows inside the
## same tile (the icon moves up to make room).
func _draw_tile_any() -> void:
	if look == Look.CHIP:
		_draw_chip_tile()
	elif is_equal_approx(text_scale, 1.0):
		_draw_tile()
	else:
		_draw_tile_scaled()


func _draw_tile_scaled() -> void:
	var s := text_scale
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Color(0.02, 0.05, 0.11, 0.95))
	if hot:
		draw_rect(rect.grow(3), Color(Palette.CELL_PINK, 0.3), false, 6.0)
	draw_rect(rect, Palette.CELL_PINK if hot else Color(accent, 0.7), false, 1.5)
	var fs := roundi(TILE_NAME_SIZE * s)
	var lines := wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	while lines.size() > 2 and fs > 9:
		fs -= 1
		lines = wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	var line_h := fs + 2.0
	var foot := PRICE_TAG_H * s + 8.0 if (price >= 0 or cost >= 0) else 6.0
	var shown := mini(lines.size(), 2)
	var name_top := size.y - foot - line_h * shown
	var icon_c := Vector2(size.x / 2.0, clampf(name_top * 0.5, 32.0, 50.0))
	draw_circle(icon_c, 34, Color(accent, 0.08))
	draw_circle(icon_c, 24, Color(accent, 0.1))
	if look == Look.CHIP:
		_big_chip(icon_c, accent)
	elif look == Look.SLICE_TILE:
		var pts := PackedVector2Array()
		for k in 9:
			var a := lerpf(-PI * 0.5 - 0.5, -PI * 0.5 + 0.5, k / 8.0)
			pts.append(icon_c + Vector2(0, 50) + Vector2(cos(a), sin(a)) * 76)
		for k in 9:
			var a := lerpf(-PI * 0.5 + 0.5, -PI * 0.5 - 0.5, k / 8.0)
			pts.append(icon_c + Vector2(0, 50) + Vector2(cos(a), sin(a)) * 30)
		var sc := Palette.slice_color(slice_type)
		draw_colored_polygon(pts, Color(sc, 0.35))
		pts.append(pts[0])
		draw_polyline(pts, sc, 1.5)
		SliceIcon.draw_on_slice(self, icon_c + Vector2(0, -15), 11, slice_type, sc)
		if slice_output > 0:
			var vs := roundi(TILE_VALUE_SIZE * minf(s, TILE_VALUE_MAX_SCALE))
			draw_string(Palette.display(), icon_c + Vector2(-20, 22), str(slice_output), HORIZONTAL_ALIGNMENT_CENTER, 40, vs, Palette.PAPER)
	elif icon_kind == "shred":
		_mini_card(icon_c + Vector2(0, -8), accent, false)
		draw_rect(Rect2(icon_c + Vector2(-30, 10), Vector2(60, 12)), Palette.DESK_METAL)
		draw_rect(Rect2(icon_c + Vector2(-30, 10), Vector2(60, 12)), accent, false, 1.5)
		for k in 6:
			draw_line(icon_c + Vector2(-18 + k * 7, 22), icon_c + Vector2(-20 + k * 7, 36), Palette.NOTE_PAPER, 2.0)
	else:
		_mini_card(icon_c, accent)
	# H23 S8: the shade dims the art only; the name stays in the text colour.
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))
	for i in shown:
		draw_string(Palette.mono(), Vector2(4, name_top + fs + i * line_h), lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	if cost >= 0:
		var pfs := roundi(14 * s)
		var cost_text := "%d" % cost
		var pw := Palette.mono().get_string_size(cost_text, HORIZONTAL_ALIGNMENT_LEFT, -1, pfs).x
		var px := size.x / 2.0 - (pw + 18 * s) / 2.0
		StatIcon.draw(self, Vector2(px + 6 * s, size.y - 15 * s), 6 * s, StatIcon.CYCLES, Palette.CELL_ACID)
		draw_string(Palette.mono(), Vector2(px + 17 * s, size.y - 10 * s), cost_text, HORIZONTAL_ALIGNMENT_LEFT, -1, pfs, Palette.CELL_ACID)


# --- H23 screens: chips say what they do, a buy button on every shop item ------------------

## The shop item's buy button (a sticker at the foot of the card or tile, over where the
## price tag hung); null when the card is not for sale.
var buy_button: BuyButton = null
## A price that depends on a choice made later (a slice's slot): the highest (-1 = one price).
var price_high: int = -1
## Chip tiles: description lettering at scale 1.0 (px) and the chip icon's least room (px).
const CHIP_TEXT_SIZE := 10
const CHIP_ICON_MIN := 30.0
## Share of the chip icon's usual size when it gives way to the description.
const CHIP_ICON_SHRINK := 0.6


## Gives the shop item a buy button reading `verb` and its price (H23 S8: the price tags
## and the decoration did not read as buttons). The card stays the focus stop (the pad
## presses it with A); the button presses it too and shows the pad button when focused.
func with_buy(verb: String = "BUY") -> ZineCard:
	if buy_button == null:
		buy_button = BuyButton.new(self, verb)
		add_child(buy_button)
	buy_button.verb = verb
	buy_button.refit()
	queue_redraw()
	return self


## The price in words for the buy button: "45", or "100-150" when it depends on a choice.
func price_words() -> String:
	if price < 0:
		return ""
	if price_high > price:
		return "%d-%d" % [price, price_high]
	return "%d" % price


## The description as the tile shows it: a chip's effect text (the kind prefix dropped).
func tile_description() -> String:
	var d := description
	var colon := d.find(": ")
	if colon > 0 and colon < 12:
		d = d.substr(colon + 2)
	return d


## A microchip tile (Firmware, Daemons) at any text scale (H23 S8: chips had no words for
## what they do): the chip icon (smaller when the words need the room), the name in the
## text colour, then as much of the effect text as fits, ending in an ellipsis (the whole
## text is the tooltip and shows on focus). The foot is the buy button's.
func _draw_chip_tile() -> void:
	var s := text_scale
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Color(0.02, 0.05, 0.11, 0.95))
	if hot:
		draw_rect(rect.grow(3), Color(Palette.CELL_PINK, 0.3), false, 6.0)
	draw_rect(rect, Palette.CELL_PINK if hot else Color(accent, 0.7), false, 1.5)
	var foot := PRICE_TAG_H * s + 8.0 if price >= 0 else 6.0
	var fs := roundi(TILE_NAME_SIZE * s)
	var names := wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	while names.size() > 2 and fs > 9:
		fs -= 1
		names = wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	var dfs := roundi(CHIP_TEXT_SIZE * s)
	var dline := dfs + 2.0
	var desc := wrap_px(tile_description(), size.x - 8.0, dfs)
	var name_h := (fs + 2.0) * mini(names.size(), 2)
	var room := size.y - foot - name_h - CHIP_ICON_MIN - 4.0
	var rows := clampi(floori(room / dline), 0, desc.size())
	var text_top := size.y - foot - rows * dline
	var name_top := text_top - name_h
	var icon_c := Vector2(size.x / 2.0, maxf(CHIP_ICON_MIN * 0.5 + 2.0, name_top * 0.5))
	var k := clampf((name_top - 4.0) / 60.0, CHIP_ICON_SHRINK, 1.0)
	draw_set_transform(icon_c, 0.0, Vector2(k, k))
	draw_circle(Vector2.ZERO, 24, Color(accent, 0.1))
	_big_chip(Vector2.ZERO, accent)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))
	for i in mini(names.size(), 2):
		draw_string(Palette.mono(), Vector2(4, name_top + fs + i * (fs + 2.0)), names[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	for i in rows:
		var t := desc[i]
		if i == rows - 1 and desc.size() > rows:
			t = t.substr(0, maxi(0, t.length() - 1)) + "…"
		draw_string(Palette.mono(), Vector2(4, text_top + dfs + i * dline), t, HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, dfs, Color(Palette.TERMINAL_TEXT, 0.85))


## The chip's effect lines shown on the tile now (tests: at least one at every text size).
func chip_lines_shown() -> int:
	var s := text_scale
	var foot := PRICE_TAG_H * s + 8.0 if price >= 0 else 6.0
	var fs := roundi(TILE_NAME_SIZE * s)
	var names := wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	while names.size() > 2 and fs > 9:
		fs -= 1
		names = wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	var dfs := roundi(CHIP_TEXT_SIZE * s)
	var room := size.y - foot - (fs + 2.0) * mini(names.size(), 2) - CHIP_ICON_MIN - 4.0
	return clampi(floori(room / (dfs + 2.0)), 0, wrap_px(tile_description(), size.x - 8.0, dfs).size())
