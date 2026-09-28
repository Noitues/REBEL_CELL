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
## ANIM-R1 C6: a RAM refusal's pulse on the cost circle (0..1; 0 = none).
var cost_alarm: float = 0.0
## The refusal's red, and how far its ring grows past the cost circle (share of its radius).
const REFUSED_COLOR := Color("#FF4D4D")
const COST_PULSE_GROW := 0.6
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
## Motion (Animation pass ANIM-3), drawn only (the card's rect and layout never move):
## the hover lift (px up), the deal-in offset (px) and tilt (radians) from the deck pile.
var lift: float = 0.0
var draw_offset: Vector2 = Vector2.ZERO
var draw_tilt: float = 0.0
## The sticker's resting tilt (degrees; hover tilts it to 0).
var rest_tilt: float = 0.0
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
const CUSTOM_PICTOS := {"calibrate_handler": "FREE NUDGE x%d", "momentum_handler": "SPIN %d+", "ring_lock_handler": "RING LOCK", # TR
	"steady_hand_handler": "PERFECT: RAM+", "undock_handler": "UNDOCK"} # TR
## The sticker's foot (the hand's key hint) at scale 1.0, and the gap kept between a tile's
## parts (px; H24 S10).
const STICKER_FOOT := 26.0
const TILE_GAP := 2.0
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
## ANIM-R1 M10: shop and reward cards show their whole text: the body (a sticker's) or the
## effect lines (a chip tile's) shrink, and a chip's icon gives way further, until every
## word fits; never under FIT_MIN_TEXT px (past that the focus tip carries the rest).
## Off for the combat hand (its cards keep their layout).
var fit_whole: bool = false
## ANIM-R1 M11: a Modem item bought on this visit: its place stays, dimmed and stamped SOLD.
var sold_stub: bool = false
const SOLD_WORD := "SOLD" # TR
const SOLD_FONT := 22
const SOLD_TILT := -0.25
const FIT_MIN_TEXT := 8
## A sticker's largest rest tilt either way (degrees; a row keeps room for it, ANIM-R2 E8).
const REST_TILT_MAX := 4
const CHIP_ICON_FIT_SHRINK := 0.3


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
	rest_tilt = float(((hash(card_title) % (REST_TILT_MAX * 2 + 1)) - REST_TILT_MAX)) if look == Look.STICKER else 0.0
	rotation_degrees = 0.0 if _lifted and look == Look.STICKER else rest_tilt


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
				# H24 S2/S3: the tags' words translated, the sign from TextDb.signed.
				if e.amount != 0:
					out.append({"kind": "tag", "text": TranslationServer.translate("RAM%s") % TextDb.signed(e.amount)})
			RC.EffectType.DRAW_CARDS:
				out.append({"kind": "tag", "text": TranslationServer.translate("DRAW %d") % e.amount})
			RC.EffectType.FREEZE:
				out.append({"kind": "tag", "text": TranslationServer.translate("FREEZE")})
			RC.EffectType.MODIFY_RESISTANCE:
				out.append({"kind": "tag", "text": TranslationServer.translate("RES%s") % TextDb.signed(e.amount)})
			RC.EffectType.HUB_BREACH:
				out.append({"kind": "tag", "text": TranslationServer.translate("BREACH")})
			RC.EffectType.CLEANSE:
				out.append({"kind": "tag", "text": TranslationServer.translate("CLEANSE")})
			RC.EffectType.DRAIN_RAM:
				out.append({"kind": "tag", "text": TranslationServer.translate("RAM%s") % TextDb.signed(-absi(e.amount))})
			RC.EffectType.SNAP_TO_CENTER:
				out.append({"kind": "tag", "text": TranslationServer.translate("SNAP")})
			RC.EffectType.DOUBLE_NUDGE_CARDS:
				out.append({"kind": "tag", "text": TranslationServer.translate("2x NUDGE")})
			RC.EffectType.RETRIGGER:
				out.append({"kind": "tag", "text": TranslationServer.translate("AGAIN")})
			RC.EffectType.CUSTOM:
				if e.custom_handler != null:
					var key := e.custom_handler.resource_path.get_file().get_basename()
					if CUSTOM_PICTOS.has(key):
						var text := TranslationServer.translate(String(CUSTOM_PICTOS[key]))
						out.append({"kind": "tag", "text": text % e.amount if String(CUSTOM_PICTOS[key]).contains("%d") else text})
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


## A fresh copy of how this card or tile looks (no buy sticker, no hotkey, not pressable):
## the ghost and the flying copies of a dragged Modem, loot or deck item (ANIM-4b).
func ghost_copy() -> ZineCard:
	var g := ZineCard.new(card_title, cost, description, 0)
	g.variant = variant
	g.look = look
	g.accent = accent
	g.slice_type = slice_type
	g.slice_output = slice_output
	g.icon_kind = icon_kind
	g.pictos = pictos
	g.text_scale = text_scale
	g.price = price
	g.price_from = price_from
	g.hotkey = ""
	g.focus_mode = Control.FOCUS_NONE
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	g.custom_minimum_size = size if size.x > 0.0 and size.y > 0.0 else custom_minimum_size
	g.size = g.custom_minimum_size
	return g


## Drag the card onto a target (the combat scene decides what the drop means).
func _get_drag_data(_at_position: Vector2) -> Variant:
	if drag_index < 0 or disabled:
		return null
	var ghost := ZineCard.new(card_title, cost, description, drag_index).scaled(text_scale)
	ghost.pictos = pictos
	ghost.variant = variant
	ghost.size = ghost.custom_minimum_size
	# ANIM-3: the ghost trails the cursor with a lag and a tilt (DragGhost).
	set_drag_preview(DragGhost.new(ghost))
	return {"hand_index": drag_index}


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
		inspected.emit()
		accept_event()


## Hover / focus: the sticker lifts `card_hover` px, tilts to 0 and glows (ANIM-3); off,
## it settles back to its resting tilt.
func _set_lift(on: bool) -> void:
	_lifted = on
	if look == Look.STICKER and is_inside_tree():
		pivot_offset = size / 2.0
		Motion.run(&"card_hover", self, ^"lift", Motion.amplitude(&"card_hover") if on and not disabled else 0.0)
		Motion.run(&"card_hover", self, ^"rotation_degrees", 0.0 if on else rest_tilt)
	queue_redraw()


## Deals the sticker in from `pile` (global): it starts there, turned `fan` degrees and
## clear, and lands in its slot after `delay` (`card_draw`). Drawn only: the slot is
## already where the card lives, so nothing under the cursor moves.
func deal_from(pile: Vector2, fan: float, delay: float) -> void:
	if not Motion.live(&"card_draw"):
		return
	var e := Motion.entry(&"card_draw")
	draw_offset = pile - get_global_rect().get_center()
	draw_tilt = deg_to_rad(fan)
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_property(self, "modulate:a", 1.0, 0.0)
	tw.tween_method(_deal_step.bind(draw_offset, draw_tilt), 0.0, 1.0, Motion.seconds(&"card_draw")).set_ease(e.ease).set_trans(e.trans)
	_deal_tween = tw


var _deal_tween: Tween = null


## Loot (Animation pass ANIM-6, ANIMATION_HANDOFF 4.20): the sticker fans in from `from`
## (global, the row's foot), turned `fan` degrees and clear, after `delay` (`loot_fan`).
## Drawn only, like deal_from: the slot never moves.
func fan_in(from: Vector2, fan: float, delay: float) -> void:
	if not Motion.live(&"loot_fan"):
		return
	var e := Motion.entry(&"loot_fan")
	draw_offset = from - get_global_rect().get_center()
	draw_tilt = deg_to_rad(fan)
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_interval(delay)
	tw.tween_property(self, "modulate:a", 1.0, 0.0)
	tw.tween_method(_deal_step.bind(draw_offset, draw_tilt), 0.0, 1.0, Motion.seconds(&"loot_fan")).set_ease(e.ease).set_trans(e.trans)
	_deal_tween = tw


func _deal_step(p: float, from: Vector2, tilt: float) -> void:
	draw_offset = from * (1.0 - p)
	draw_tilt = tilt * (1.0 - p)
	queue_redraw()


## Ends a deal-in at once (skip): the card sits in its slot.
func finish_deal() -> void:
	if _deal_tween != null and _deal_tween.is_valid():
		_deal_tween.kill()
	_deal_tween = null
	draw_offset = Vector2.ZERO
	draw_tilt = 0.0
	modulate.a = 1.0
	queue_redraw()


## ANIM-R1 C6: not enough RAM for this card: its cost circle pulses red (`ram_refusal`:
## its duration, amplitude = pulses). With motion off it shows red at once and stays so
## until the hand is dealt again.
func pulse_cost() -> void:
	if not Motion.live(&"ram_refusal"):
		cost_alarm = 1.0
		queue_redraw()
		return
	var pulses := maxf(1.0, Motion.amplitude(&"ram_refusal"))
	var e := Motion.entry(&"ram_refusal")
	var tw := create_tween()
	tw.tween_method(func(p: float) -> void:
		cost_alarm = absf(sin(p * PI * pulses))
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"ram_refusal")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(func() -> void: cost_alarm = 0.0; queue_redraw())


## True while the card is still being dealt in.
func dealing() -> bool:
	return _deal_tween != null and _deal_tween.is_valid() and _deal_tween.is_running()


func _draw() -> void:
	if lift != 0.0 or draw_offset != Vector2.ZERO or draw_tilt != 0.0:
		var c := size * 0.5
		draw_set_transform_matrix(Transform2D(draw_tilt, c + draw_offset + Vector2(0.0, -lift)) * Transform2D(0.0, -c))
	if look != Look.STICKER:
		_draw_tile_any()
	else:
		_draw_sticker()
	_draw_price_tag()
	if sold_stub:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0, 0, 0, 0.6))
		var fs := roundi(SOLD_FONT * text_scale)
		draw_set_transform(size * 0.5, SOLD_TILT, Vector2.ONE)
		var word := tr(SOLD_WORD)
		var w := Palette.display().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var box := Rect2(Vector2(-w * 0.5 - 6.0, -fs * 0.7), Vector2(w + 12.0, fs * 1.3))
		draw_rect(box, Palette.CELL_PINK, false, 3.0)
		draw_string(Palette.display(), Vector2(-w * 0.5, fs * 0.36), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.CELL_PINK)
		draw_set_transform(Vector2.ZERO)
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
		var cost_fill := Palette.CELL_ACID if variant != Variant.PINK else Palette.PAPER
		if cost_alarm > 0.0:
			# ANIM-R1 C6: a RAM refusal pulses the cost red (not enough RAM for it).
			cost_fill = cost_fill.lerp(REFUSED_COLOR, cost_alarm)
			draw_arc(Vector2(size.x - r - 5, r + 5), r + 2.0 + r * COST_PULSE_GROW * cost_alarm, 0, TAU, 24, Color(REFUSED_COLOR, cost_alarm), 3.0, true)
		draw_circle(Vector2(size.x - r - 5, r + 5), r, cost_fill)
		draw_string(Palette.marker(), Vector2(size.x - r * 2 - 5, r + 5 + 6 * s), str(cost), HORIZONTAL_ALIGNMENT_CENTER, r * 2, roundi((14 if cost >= 100 else 16) * s), Palette.INK)
	var title_size := roundi(TITLE_SIZE * s)
	while title_size > 9 and Palette.display().get_string_size(card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, title_size).x > title_w:
		title_size -= 1  # long names shrink to fit beside the cost
	draw_string(Palette.display(), Vector2(8, 34 * s), card_title.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, title_w, title_size, fg)
	# The body wraps to the sticker's width; what doesn't fit ends in an ellipsis (the full
	# text is the tooltip and the inspect). ANIM-R1 M10: with `fit_whole` it shrinks first.
	var fit := sticker_body_fit()
	var body: int = fit["fs"]
	var lines: PackedStringArray = fit["lines"]
	var room: int = fit["rows"]
	var step: float = fit["line"]
	for i in mini(lines.size(), room):
		var t := lines[i]
		if i == room - 1 and lines.size() > room:
			t = t.substr(0, maxi(0, t.length() - 1)) + "…"
		draw_string(Palette.mono(), Vector2(8, BODY_TOP * s + i * step), t, HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, body, fg)
	_draw_pictos(Vector2(8 + PICTO_RADIUS * s, _sticker_foot_top() - PICTO_RADIUS * s - 2.0), s, fg)
	# H24 S10: the corner chip mark is decoration; a shop card's buy sticker sits there.
	if buy_button == null:
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
	# Within the icon's frame (a scaled tile draws its icon under `_icon_xf`, H24 S10).
	draw_set_transform_matrix(_icon_xf * Transform2D(-0.12, c))
	draw_rect(Rect2(Vector2(-19, -25), Vector2(40, 52)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.NOTE_PAPER)
	draw_rect(Rect2(Vector2(-22, -28), Vector2(40, 52)), Palette.INK, false, 1.0)
	draw_rect(Rect2(Vector2(-10, -32), Vector2(16, 7)), Palette.NOTE_TAPE)
	var initials := ""
	for w in card_title.split(" "):
		if w != "" and initials.length() < 2 and initials_on:
			initials += w[0].to_upper()
	draw_string(Palette.display(), Vector2(-22, 8), initials, HORIZONTAL_ALIGNMENT_CENTER, 40, 22, col.darkened(0.2))
	draw_set_transform_matrix(_icon_xf)


## The frame a tile's icon is drawn in (identity but while a scaled tile draws its icon).
var _icon_xf: Transform2D = Transform2D.IDENTITY


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


## Where the sticker's foot starts (px from the top): the buy sticker's top on a shop card
## (H24 S10), else the room the hand's key hint takes.
func _sticker_foot_top() -> float:
	if buy_button != null:
		return size.y - buy_room()
	return size.y - STICKER_FOOT * text_scale


## How many body lines fit on the sticker above its pictograms and foot.
func sticker_body_rows() -> int:
	var s := text_scale
	return _body_rows_at(BODY_LINE * s)


func _body_rows_at(line: float) -> int:
	var s := text_scale
	var picto_h := (PICTO_RADIUS * 2.0 + 6.0) * s if not pictos.is_empty() else 0.0
	return maxi(1, int((_sticker_foot_top() - picto_h - BODY_TOP * s) / line))


## The sticker body as drawn: {"fs": font px, "line": line step px, "rows": lines that fit,
## "lines": the wrapped text}. ANIM-R1 M10: with `fit_whole` the font steps down (never
## under FIT_MIN_TEXT) until every line fits.
func sticker_body_fit() -> Dictionary:
	var s := text_scale
	var fs := roundi(BODY_SIZE * s)
	var line := BODY_LINE * s
	var lines := wrap_px(description, size.x - 16, fs)
	var rows := _body_rows_at(line)
	while fit_whole and lines.size() > rows and fs > FIT_MIN_TEXT:
		fs -= 1
		line = BODY_LINE * s * fs / float(roundi(BODY_SIZE * s))
		lines = wrap_px(description, size.x - 16, fs)
		rows = _body_rows_at(line)
	return {"fs": fs, "line": line, "rows": rows, "lines": lines}


## True when the whole text shows on the card (body lines, or a chip tile's effect lines).
func text_whole() -> bool:
	if look == Look.STICKER:
		var fit := sticker_body_fit()
		return (fit["lines"] as PackedStringArray).size() <= int(fit["rows"])
	if look == Look.CHIP:
		var parts := tile_parts()
		return int(parts["rows"]) >= (parts["desc_lines"] as PackedStringArray).size()
	return true


## The sticker's parts as drawn (local rects; H24 S10 tests: none overlaps another): the
## title, each body line shown, the pictogram row, the corner chip mark and the buy sticker.
func sticker_parts() -> Dictionary:
	var s := text_scale
	var mono := Palette.mono()
	var fit := sticker_body_fit()
	var body: int = fit["fs"]
	var lines: PackedStringArray = fit["lines"]
	var rows: Array[Rect2] = []
	for i in mini(lines.size(), int(fit["rows"])):
		var base := BODY_TOP * s + i * float(fit["line"])
		rows.append(Rect2(8, base - mono.get_ascent(body), size.x - 16, mono.get_height(body)))
	var out := {"body": rows}
	if not pictos.is_empty():
		var y := _sticker_foot_top() - PICTO_RADIUS * s - 2.0
		out["pictos"] = Rect2(8, y - PICTO_RADIUS * s, size.x - 16, PICTO_RADIUS * 2.0 * s)
	if buy_button == null:
		out["chip"] = Rect2(Vector2(size.x - 24, size.y - 22) - Vector2(11, 11), Vector2(22, 22))
	else:
		out["buy"] = Rect2(buy_button.position, buy_button.size)
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


## Tiles at text scale 1.0 draw as before; at other scales, or with a buy sticker at the
## foot (H24 S10), the lettering and the icon are laid out by `tile_parts` inside the tile.
func _draw_tile_any() -> void:
	if look == Look.CHIP:
		_draw_chip_tile()
	elif is_equal_approx(text_scale, 1.0) and buy_button == null:
		_draw_tile()
	else:
		_draw_tile_scaled()


## The room a shop item's foot takes (px): its buy sticker, the edge under it and a gap
## (H24 S10: text and icons ran under the sticker at 1.6), else the price tag's.
func buy_room() -> float:
	var s := text_scale
	if buy_button != null:
		var h := buy_button.size.y if buy_button.size.y > 0.0 else BuyButton.BUY_HEIGHT * s
		# ANIM-R4 C7: and the reach of its flap (`note_flap` degrees about its top edge lift a
		# top corner by half its width x sin: at 1.0 the flapping BUY lay on the text's last line).
		var flap := buy_button.size.x * 0.5 * absf(sin(deg_to_rad(Motion.amplitude(&"note_flap"))))
		return h + BuyButton.EDGE * s + TILE_GAP * s + flap
	return PRICE_TAG_H * s + 8.0 if (price >= 0 or cost >= 0) else 6.0


## The icon's extent round its centre at scale 1 for this tile's look (px): [left, top,
## right, bottom] as positive distances.
func _icon_extent() -> Vector4:
	match look:
		Look.CHIP:
			return Vector4(26, 26, 26, 26)
		Look.SLICE_TILE:
			return Vector4(37, 27, 37, 28)
	if icon_kind == "shred":
		return Vector4(30, 42, 30, 36)
	return Vector4(24, 33, 21, 27)


## A shop tile's layout (H24 S10; local px): "icon" (its rect), "k" (its scale), "centre",
## "names" (a rect per name line), "fs" (the name size), "desc" (a rect per effect line,
## chip tiles), "rows" (their count), "dfs" and "buy" (the sticker's rect).
func tile_parts() -> Dictionary:
	var s := text_scale
	var mono := Palette.mono()
	var foot := buy_room()
	var fs := roundi(TILE_NAME_SIZE * s)
	var lines := wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	while lines.size() > 2 and fs > 9:
		fs -= 1
		lines = wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	var line_h := mono.get_height(fs)
	var shown := mini(lines.size(), 2)
	var desc_rows := 0
	var dfs := roundi(CHIP_TEXT_SIZE * s)
	var dline := mono.get_height(dfs)
	var ext := _icon_extent()
	var icon_h := ext.y + ext.w
	var desc_lines := PackedStringArray()
	var icon_floor := CHIP_ICON_SHRINK
	if look == Look.CHIP:
		desc_lines = wrap_px(tile_description(), size.x - 8.0, dfs)
		var spare := size.y - foot - line_h * shown - icon_h * CHIP_ICON_SHRINK - TILE_GAP * 2.0 * s
		desc_rows = clampi(floori(spare / dline), 0, desc_lines.size())
		if fit_whole and desc_rows < desc_lines.size():
			# ANIM-R1 M10: the icon gives way further, then the lettering steps down, until
			# the whole effect text fits (never under FIT_MIN_TEXT px).
			icon_floor = CHIP_ICON_FIT_SHRINK
			while true:
				dline = mono.get_height(dfs)
				desc_lines = wrap_px(tile_description(), size.x - 8.0, dfs)
				spare = size.y - foot - line_h * shown - icon_h * icon_floor - TILE_GAP * 2.0 * s
				desc_rows = clampi(floori(spare / dline), 0, desc_lines.size())
				if desc_rows >= desc_lines.size() or dfs <= FIT_MIN_TEXT:
					break
				dfs -= 1
	var text_top := size.y - foot - desc_rows * dline
	var name_top := text_top - line_h * shown
	# The icon in the room above the names, shrunk (never under CHIP_ICON_SHRINK) when the
	# room is short, centred in it.
	var room := name_top - TILE_GAP * s * 2.0
	var k := clampf(room / icon_h, icon_floor, 1.0)
	var top := TILE_GAP * s + maxf(0.0, (room - icon_h * k) * 0.5)
	var centre := Vector2(size.x * 0.5, top + ext.y * k)
	var out := {"k": k, "centre": centre, "fs": fs, "dfs": dfs, "rows": desc_rows, "lines": lines, "desc_lines": desc_lines,
		"icon": Rect2(centre - Vector2(ext.x, ext.y) * k, Vector2(ext.x + ext.z, ext.y + ext.w) * k)}
	var names: Array[Rect2] = []
	for i in shown:
		var w := minf(size.x - 8.0, mono.get_string_size(lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
		names.append(Rect2((size.x - w) * 0.5, name_top + i * line_h, w, line_h))
	out["names"] = names
	var desc: Array[Rect2] = []
	for i in desc_rows:
		var w := minf(size.x - 8.0, mono.get_string_size(desc_lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, dfs).x)
		desc.append(Rect2((size.x - w) * 0.5, text_top + i * dline, w, dline))
	out["desc"] = desc
	if buy_button != null:
		out["buy"] = Rect2(buy_button.position, buy_button.size)
	return out


func _draw_tile_scaled() -> void:
	var s := text_scale
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Color(0.02, 0.05, 0.11, 0.95))
	if hot:
		draw_rect(rect.grow(3), Color(Palette.CELL_PINK, 0.3), false, 6.0)
	draw_rect(rect, Palette.CELL_PINK if hot else Color(accent, 0.7), false, 1.5)
	var parts := tile_parts()
	var fs: int = parts["fs"]
	var lines: PackedStringArray = parts["lines"]
	var names: Array[Rect2] = parts["names"]
	var shown := names.size()
	var line_h := names[0].size.y if shown > 0 else 0.0
	var name_top := names[0].position.y if shown > 0 else size.y - buy_room()
	var icon_c: Vector2 = parts["centre"]
	var ik: float = parts["k"]
	_icon_xf = Transform2D(0.0, Vector2(ik, ik), 0.0, icon_c)
	draw_set_transform_matrix(_icon_xf)
	var home := icon_c
	icon_c = Vector2.ZERO
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
	_icon_xf = Transform2D.IDENTITY
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	icon_c = home
	# H23 S8: the shade dims the art only; the name stays in the text colour.
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))
	var mono := Palette.mono()
	for i in shown:
		draw_string(mono, Vector2(4, name_top + mono.get_ascent(fs) + i * line_h), lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	if cost >= 0 and buy_button == null:
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
## text is the tooltip and shows on focus). The foot is the buy button's (H24 S10: the
## text measured against the sticker's real height; its third line ran under it at 1.6).
func _draw_chip_tile() -> void:
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Color(0.02, 0.05, 0.11, 0.95))
	if hot:
		draw_rect(rect.grow(3), Color(Palette.CELL_PINK, 0.3), false, 6.0)
	draw_rect(rect, Palette.CELL_PINK if hot else Color(accent, 0.7), false, 1.5)
	var parts := tile_parts()
	var k: float = parts["k"]
	draw_set_transform(parts["centre"], 0.0, Vector2(k, k))
	draw_circle(Vector2.ZERO, 24, Color(accent, 0.1))
	_big_chip(Vector2.ZERO, accent)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if disabled:
		draw_rect(rect, Color(0, 0, 0, 0.55))
	var mono := Palette.mono()
	var fs: int = parts["fs"]
	var lines: PackedStringArray = parts["lines"]
	var names: Array[Rect2] = parts["names"]
	for i in names.size():
		draw_string(mono, Vector2(4, names[i].position.y + mono.get_ascent(fs)), lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	var dfs: int = parts["dfs"]
	var desc: PackedStringArray = parts["desc_lines"]
	var rows_at: Array[Rect2] = parts["desc"]
	var rows := rows_at.size()
	for i in rows:
		var t := desc[i]
		if i == rows - 1 and desc.size() > rows:
			t = t.substr(0, maxi(0, t.length() - 1)) + "…"
		draw_string(mono, Vector2(4, rows_at[i].position.y + mono.get_ascent(dfs)), t, HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, dfs, Color(Palette.TERMINAL_TEXT, 0.85))


## The chip's effect lines shown on the tile now (tests: at least one at every text size).
func chip_lines_shown() -> int:
	return int(tile_parts()["rows"])
