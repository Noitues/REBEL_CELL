class_name ZineCard
extends Button
## A card as a PAPER object (ART_BIBLE 6.3, 2; STYLE_GUIDE 4). The card Look (STICKER) is
## the full frame: a cost gem top-left (marker numeral in a circle), the title in Anton,
## an illustration window 60% of the card's height, an effect band at the foot (the key
## glyph and number) and the rules text in the Plex body face. The stock colour means the
## card type (CardArt.Type: paper / black / pink). A hand-size card shows the compact face
## (no rules text: the band carries the effect, the detail and tooltip the words); a card
## that must show its words (`fit_whole`: shop, loot, deck view; the DETAIL size) shows
## the full face, whose text steps down one type step, then lets the art yield, then grows
## the card taller; it never truncates. Shop tiles (CHIP, CARD_TILE, SLICE_TILE) are GLASS.
## Emits Button signals; the scene decides what a press means.

## Right-click (inspect): the scene opens the detail popup.
signal inspected

enum Variant { PAPER, BLACK, PINK }
## Selection marks drawn over the card.
enum Mark { NONE, CROSS, CIRCLE }
## STICKER: the card (hand, loot, deck). CHIP / CARD_TILE: shop tiles (reference: the
## Modem's microchips and card builder) with an icon, a name and a Cycle price.
enum Look { STICKER, CHIP, CARD_TILE, SLICE_TILE }
## W4 (ART_BIBLE 6.3): HAND = the sticker size callers give it (STICKER_SIZE x scale);
## DETAIL = the detail view's card (DETAIL_SIZE), full face with the whole 3:2 art.
enum SizeMode { HAND, DETAIL }

var card_title: String = ""
var cost: int = 0
## ANIM-R1 C6: a RAM refusal's pulse on the cost circle (0..1; 0 = none).
var cost_alarm: float = 0.0
## How far the refusal's ring grows past the cost circle (share of its radius).
const COST_PULSE_GROW := 0.6
var description: String = ""
var variant: int = Variant.PAPER
var hotkey: String = ""
var look: int = Look.STICKER
## W4: the card this sticker shows (null for a Firmware or Daemon sticker): its type,
## rarity and illustration.
var card_data: CardData = null
var size_mode: int = SizeMode.HAND
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
## the hover lift (px up), the hover scale, the deal-in offset (px) and tilt (radians).
var lift: float = 0.0
var hover_scale: float = 1.0
var draw_offset: Vector2 = Vector2.ZERO
var draw_tilt: float = 0.0
## The sticker's resting tilt (degrees; hover tilts it to 0).
var rest_tilt: float = 0.0
## W4 (for W3): false = the card doesn't lift on its own on hover and focus; the scene
## calls set_hovered() instead.
var auto_hover: bool = true
## Hand index this card drags as (H20 drag-to-target), -1 = not draggable.
var drag_index: int = -1
## What the card does as pictograms (H21: readable without words): [{kind, amount,
## type}] from pictos_of(); drawn in the effect band.
var pictos: Array[Dictionary] = []
## A pad is in use: the focused card shows the button that plays it.
var pad_hint: String = ""
## Short tags for the scripted card effects (by handler script name; H22: they had no
## pictogram). "%d" takes the effect's amount.
const CUSTOM_PICTOS := {"calibrate_handler": "FREE NUDGE x%d", "momentum_handler": "SPIN %d+", "ring_lock_handler": "RING LOCK", # TR
	"steady_hand_handler": "PERFECT: RAM+", "undock_handler": "UNDOCK"} # TR
## The gap kept between a tile's parts (px; H24 S10).
const TILE_GAP := 2.0
## Slice icon for each effect that does what a slice does.
const EFFECT_SLICE := {RC.EffectType.DEAL_DAMAGE: RC.SliceType.ATTACK, RC.EffectType.GAIN_BLOCK: RC.SliceType.DEFEND,
	RC.EffectType.GAIN_SHIELD: RC.SliceType.SHIELD, RC.EffectType.EVADE: RC.SliceType.EVADE, RC.EffectType.HEAL: RC.SliceType.HEAL,
	RC.EffectType.DEPLOY_DRONE: RC.SliceType.DEPLOY, RC.EffectType.APPLY_STATUS: RC.SliceType.AFFLICT}
## Lettering scale (the combat hand follows Settings.text_scale; see scaled()).
var text_scale: float = 1.0
## Sticker size at scale 1.0 (the hand's size contract; W3 lays the hand out with it).
const STICKER_SIZE := Vector2(112, 148)
## ANIM-R1 M10: shop and reward cards show their whole text (the full face; see the class
## doc). Off for the combat hand (the compact face).
var fit_whole: bool = false
## ANIM-R1 M11: a Modem item bought on this visit: its place stays, dimmed and stamped SOLD.
var sold_stub: bool = false
const SOLD_WORD := "SOLD" # TR
const SOLD_TILT := -0.25
## The shade laid over a SOLD stub and over a disabled card's art (INK at this alpha).
const SOLD_SHADE := 0.6
const DISABLED_SHADE := 0.5
## A sticker's largest rest tilt either way (degrees; a row keeps room for it, ANIM-R2 E8).
const REST_TILT_MAX := 4
const CHIP_ICON_FIT_SHRINK := 0.3

# --- W4 frame geometry (ART_BIBLE 6.3; px at scale 1.0 unless a share) ----------------------
## The detail view's card at scale 1.0: the full face with the art window at 3:2.
const DETAIL_SIZE := Vector2(288, 320)
## The illustration window's share of the card height, the least share it yields to when
## the words need the room, and the art's aspect (the 768x512 master, ART_BIBLE 7.3).
const ART_SHARE := 0.6
const ART_FLOOR := 0.15
const ART_ASPECT := 1.5
## The effect band's height as a share of the card, between the label and heading steps.
const BAND_SHARE := 0.18
## The cost gem's radius (a 3-digit cost gets the wider one), the frame rule, the hard
## shadow's offset and the tape strip (PAPER: tape and a hard shadow, ART_BIBLE 2).
const GEM_R := 13.0
const GEM_R_WIDE := 17.0
const FRAME_LINE := 2.0
const WINDOW_LINE := 1.0
const SHADOW_OFFSET := 3.0
const TAPE_SIZE := Vector2(44, 12)
const TAPE_AT := 0.3
## Anton's cap height as a share of its size (centres capitals in a line box).
const ANTON_CAP := 0.72
## The effect band: a pictogram's radius as a share of the band height, and the size of
## the second and later pictograms against the first.
const BAND_GLYPH := 0.34
const BAND_SECONDARY := 0.72
## FOCUS brackets (ART_BIBLE 6): arm length, stroke and offset (px at scale 1.0).
const FOCUS_ARM := 12.0
const FOCUS_STROKE := 2.0
const FOCUS_OFFSET := 4.0
## The draw order a hovered card rises to over its row, and its hover scale (ART_BIBLE
## 6.3: lift 12 px = `card_hover`'s amplitude, scale 1.12, straighten; `card_hover`'s timing).
const HOVER_Z := 1
const HOVER_SCALE := 1.12

# --- W4 rarity by stock (ART_BIBLE 6.3) -------------------------------------------------------
## The stock a rarity is printed on: COMMON photocopy paper (grain and toner), UNCOMMON a
## glossy sticker (a white die-cut margin, a specular edge and a sheen), RARE and BOSS
## holographic foil (foil.gdshader on the border band and art window, tilting with the
## pointer or stick; a static sheen under reduce effects). In greyscale each also reads
## by its edge (plain / die-cut / hatched) and its pip glyph (dot / diamond / star).
enum Stock { PHOTOCOPY, GLOSSY, FOIL }
## The rarity pip's radius, the die-cut margin, the hatch spacing on a foil edge (px at
## scale 1.0), and the alphas of the grain, the sheen, the specular edge and the hatch.
const PIP_R := 4.0
## The pip's tab radius as a multiple of the pip's.
const PIP_TAB := 1.9
const DIECUT := 3.0
const FOIL_HATCH := 5.0
## HACK (pink) stock's type hatch (ART_BIBLE 3.1): spacing and stroke (px at scale 1.0) and alpha.
const TYPE_HATCH_STEP := 7.0
const TYPE_HATCH_W := 1.0
const TYPE_HATCH_ALPHA := 0.14
const GRAIN_ALPHA := 0.22
const GLOSS_ALPHA := 0.16
const SPECULAR_ALPHA := 0.75
const EDGE_SHADE := 0.3
const HATCH_ALPHA := 0.45
## The glossy sheen band: where it crosses the card (share of the width) and its width.
const GLOSS_AT := 0.62
const GLOSS_WIDTH := 0.16
## The foil's strength over the art window (the border band is at full strength), the
## tilt shown under reduce effects, and the stick's dead zone.
const FOIL_ART_STRENGTH := 0.35
const FOIL_STATIC := Vector2(0.35, -0.2)
const STICK_DEADZONE := 0.2
## How far one unit of pointer tilt slides the foil (the shader's `tilt`); the foil eases
## to the pointer with `card_hover`'s duration as its time constant.
const FOIL_REACH := 1.0
const FOIL_SHADER := preload("res://shaders/foil.gdshader")
## The foil's tilt now (-1..1 per axis; the shader's `tilt`), and a hold that stops it
## following the pointer (the cards lab shows fixed tilts).
var foil_tilt: Vector2 = Vector2.ZERO
var foil_hold: bool = false
var _foil_ci: RID = RID()
var _foil_mat: ShaderMaterial = null
## Type steps tried, largest first: the title, the rules text (one step down, never under
## caption; ART_BIBLE 4.3) and the band's key number.
const TITLE_STEPS: Array[int] = [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]
const RULES_STEPS: Array[int] = [UiTheme.BODY, UiTheme.CAPTION]
const BAND_STEPS: Array[int] = [UiTheme.HEADING, UiTheme.TITLE, UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]

var _layout_key: String = ""
var _layout: Dictionary = {}
## The height the full face added to the caller's minimum (the tall mode; 0 = none).
var _tall_extra: float = 0.0
var _tall_min: float = -1.0


func _init(p_title: String = "", p_cost: int = 0, p_description: String = "", index: int = 0) -> void:
	card_title = p_title
	cost = p_cost
	description = p_description
	variant = index % 3
	hotkey = str(index + 1) if index < 9 else ""
	custom_minimum_size = STICKER_SIZE
	flat = true
	focus_mode = Control.FOCUS_ALL
	# Draws its own hover/focus marks; no theme box around the sticker.
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	tooltip_text = p_description
	mouse_entered.connect(_auto_lift.bind(true))
	mouse_exited.connect(_auto_lift.bind(false))
	focus_entered.connect(_auto_lift.bind(true))
	focus_exited.connect(_auto_lift.bind(false))


func _ready() -> void:
	pivot_offset = size / 2.0
	rest_tilt = float(((hash(card_title) % (REST_TILT_MAX * 2 + 1)) - REST_TILT_MAX)) if look == Look.STICKER and size_mode == SizeMode.HAND else 0.0
	rotation_degrees = 0.0 if _lifted and look == Look.STICKER else rest_tilt
	_refit_tall.call_deferred()
	set_process(is_foil())


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		pivot_offset = size / 2.0
		_refit_tall.call_deferred()
	elif what == NOTIFICATION_PREDELETE and _foil_ci.is_valid():
		RenderingServer.free_rid(_foil_ci)


## The card's rarity (RC.Rarity), or -1 for a sticker without card data.
func rarity() -> int:
	return card_data.rarity if card_data != null else -1


## The stock `rarity` is printed on (Stock); no card data prints on photocopy paper.
static func stock_of(p_rarity: int) -> int:
	match p_rarity:
		RC.Rarity.UNCOMMON:
			return Stock.GLOSSY
		RC.Rarity.RARE, RC.Rarity.BOSS:
			return Stock.FOIL
	return Stock.PHOTOCOPY


## What a stock looks like, colour aside (tests: each rarity distinct and readable in
## greyscale): its pip glyph, its edge, grain, gloss and foil.
static func stock_marks(stock: int) -> Dictionary:
	match stock:
		Stock.GLOSSY:
			return {"pip": "diamond", "edge": "diecut", "grain": false, "gloss": true, "foil": false}
		Stock.FOIL:
			return {"pip": "star", "edge": "hatch", "grain": false, "gloss": false, "foil": true}
	return {"pip": "dot", "edge": "plain", "grain": true, "gloss": false, "foil": false}


## True when this is a card Look on foil stock.
func is_foil() -> bool:
	return look == Look.STICKER and stock_of(rarity()) == Stock.FOIL


## Where the foil points for a pointer or stick at `p` (-1..1 per axis): `p` itself, or the
## fixed FOIL_STATIC under reduce effects (a static sheen, ART_BIBLE 8, 12).
static func foil_target(p: Vector2) -> Vector2:
	if Settings.reduce_effects:
		return FOIL_STATIC
	return p.clamp(-Vector2.ONE, Vector2.ONE)


## The foil follows the pointer (over the card, or from across the screen), or under a pad
## the right stick, else the card's place on screen (a focused card tilts as focus moves).
func _process(delta: float) -> void:
	if not is_foil() or foil_hold or not is_visible_in_tree():
		return
	var target := foil_target(_pointer_tilt())
	var tau := maxf(0.001, Motion.seconds(&"card_hover"))
	foil_tilt = target if Settings.reduce_effects else foil_tilt.lerp(target, 1.0 - exp(-delta / tau))
	if _foil_mat != null:
		_foil_mat.set_shader_parameter(&"tilt", foil_tilt * FOIL_REACH)


func _pointer_tilt() -> Vector2:
	var vp := get_viewport_rect().size
	var centre := get_global_rect().get_center()
	if Settings.pad_active:
		var stick := Vector2(Input.get_joy_axis(0, JOY_AXIS_RIGHT_X), Input.get_joy_axis(0, JOY_AXIS_RIGHT_Y))
		if stick.length() > STICK_DEADZONE:
			return stick
		return (centre / vp) * 2.0 - Vector2.ONE if vp.x > 0.0 else Vector2.ZERO
	if _lifted and size.x > 0.0:
		return (get_local_mouse_position() / size) * 2.0 - Vector2.ONE
	return (get_global_mouse_position() - centre) / vp * 2.0 if vp.x > 0.0 else Vector2.ZERO


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


## Sets the card's data: its pictograms, and its stock colour from its type (ART_BIBLE 6.3:
## colour means card type; combat hand, loot, shop and deck views).
func with_card(card: CardData) -> ZineCard:
	card_data = card
	pictos = pictos_of(card)
	if card != null:
		variant = CardArt.variant_of(card)
	set_process(is_foil())
	queue_redraw()
	return self


## Scales the sticker and its lettering by `s` (the combat hand at text scale > 1).
func scaled(s: float) -> ZineCard:
	text_scale = s
	custom_minimum_size = STICKER_SIZE * s
	_tall_extra = 0.0
	return self


## W4: makes this the detail view's card (ART_BIBLE 6.3): the full face with the whole 3:2
## art and every word, lettering at text scale `s_text`, the card sized to fit `room` (px;
## a zero axis = no limit). Its words keep their size when the card is held smaller: the
## art yields, then the card grows taller (the view scrolls).
func as_detail(s_text: float, room: Vector2 = Vector2.ZERO) -> ZineCard:
	size_mode = SizeMode.DETAIL
	text_scale = s_text
	fit_whole = true
	hotkey = ""
	var k := s_text
	if room.x > 0.0:
		k = minf(k, room.x / DETAIL_SIZE.x)
	if room.y > 0.0:
		k = minf(k, room.y / DETAIL_SIZE.y)
	custom_minimum_size = DETAIL_SIZE * k
	_tall_extra = 0.0
	return self


## A fresh copy of how this card or tile looks (no buy sticker, no hotkey, not pressable):
## the ghost and the flying copies of a dragged Modem, loot or deck item (ANIM-4b).
func ghost_copy() -> ZineCard:
	var g := ZineCard.new(card_title, cost, description, 0)
	g.variant = variant
	g.look = look
	g.card_data = card_data
	g.size_mode = size_mode
	g.fit_whole = fit_whole
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
	ghost.card_data = card_data
	ghost.variant = variant
	ghost.size = ghost.custom_minimum_size
	# ANIM-3: the ghost trails the cursor with a lag and a tilt (DragGhost).
	set_drag_preview(DragGhost.new(ghost))
	return {"hand_index": drag_index}


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
		inspected.emit()
		accept_event()


## W4 (ART_BIBLE 6.3, for W3's hand): hover on or off. The card lifts `card_hover` px (12),
## scales to HOVER_SCALE (1.12) and straightens to 0 degrees; off, it settles back
## to its resting tilt. Drawn only: its rect, minimum size and the hand never reflow.
func set_hovered(on: bool) -> void:
	_set_lift(on)


## True while the card is hovered or focused (lifted).
func is_hovered_card() -> bool:
	return _lifted


func _auto_lift(on: bool) -> void:
	if auto_hover:
		_set_lift(on)


## Hover / focus: the sticker lifts, grows and tilts to 0 (ANIM-3, ART_BIBLE 6.3); off, it
## settles back to its resting tilt.
func _set_lift(on: bool) -> void:
	_lifted = on
	if look == Look.STICKER and is_inside_tree():
		pivot_offset = size / 2.0
		var up := on and not disabled
		# Drawn over its neighbours while it grows (a draw order, never a reflow).
		z_index = HOVER_Z if up else 0
		Motion.run(&"card_hover", self, ^"lift", Motion.amplitude(&"card_hover") if up else 0.0)
		Motion.run(&"card_hover", self, ^"hover_scale", HOVER_SCALE if up else 1.0)
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


## The drawn-only transform (lift, hover scale, deal-in offset and tilt) about the centre.
func draw_transform() -> Transform2D:
	var c := size * 0.5
	return Transform2D(draw_tilt, Vector2.ONE * hover_scale, 0.0, c + draw_offset + Vector2(0.0, -lift)) * Transform2D(0.0, -c)


func _draw() -> void:
	var moved := lift != 0.0 or hover_scale != 1.0 or draw_offset != Vector2.ZERO or draw_tilt != 0.0
	if moved:
		draw_set_transform_matrix(draw_transform())
	if look != Look.STICKER:
		_draw_tile_any()
	else:
		_draw_sticker()
	_draw_price_tag()
	if sold_stub:
		draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.INK, SOLD_SHADE))
		var fs := UiTheme.font_px_at(UiTheme.TITLE, text_scale)
		var base := draw_transform() if moved else Transform2D.IDENTITY
		draw_set_transform_matrix(base * Transform2D(SOLD_TILT, size * 0.5))
		var word := tr(SOLD_WORD)
		var w := Palette.display().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var pad := UiTheme.SP_XS * text_scale
		var box := Rect2(Vector2(-w * 0.5 - pad, -fs * 0.7), Vector2(w + pad * 2.0, fs * 1.3))
		draw_rect(box, Palette.CELL_PINK, false, 3.0)
		draw_string(Palette.display(), Vector2(-w * 0.5, fs * 0.36), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.CELL_PINK)
		draw_set_transform_matrix(base)
	match mark:
		Mark.CROSS:
			HandMarks.draw_x(self, Rect2(Vector2.ZERO, size), DripButton.DRIP_PINK)
		Mark.CIRCLE:
			HandMarks.draw_drip_circle(self, size * 0.5, size * 0.5 * Vector2(0.95, 0.8), DripButton.DRIP_PINK)


# --- W4 the frame (ART_BIBLE 6.3) --------------------------------------------------------------

## The stock colour and ink colour of the card's type (ART_BIBLE 6.3).
func stock_colors() -> Array[Color]:
	match variant:
		Variant.BLACK:
			return [Palette.INK, Palette.PAPER]
		Variant.PINK:
			return [Palette.STICKER_PINK, Palette.INK]
	return [Palette.PAPER, Palette.INK]


## True when the rules text is on the face (the full face: `fit_whole` or the DETAIL size).
func rules_on_face() -> bool:
	return fit_whole or size_mode == SizeMode.DETAIL


## Splits `text` into lines no wider than `width` px in `font` at `fs`, at word boundaries
## only (ART_BIBLE 4.3.3: never mid-word, never hyphenated); a newline starts a line. A
## word wider than `width` stands alone on its line (see lines_fit).
static func wrap_words(font: Font, text: String, width: float, fs: int) -> PackedStringArray:
	var out := PackedStringArray()
	for para in text.split("\n"):
		var line := ""
		for word in para.split(" ", false):
			var trial := word if line == "" else line + " " + word
			if line != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
				out.append(line)
				line = word
			else:
				line = trial
		if line != "":
			out.append(line)
	return out


## True when every line of `lines` is at most `width` px wide.
static func lines_fit(font: Font, lines: PackedStringArray, width: float, fs: int) -> bool:
	for l in lines:
		if font.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width + 0.5:
			return false
	return true


## The line height (px) of type step `step` at `fs` px.
static func step_line(step: int, fs: int) -> float:
	return fs * UiTheme.line_height(step)


## The room the foot of the card takes (px): the buy sticker's or the price tag's.
func _foot_room() -> float:
	if buy_button != null or price >= 0:
		return buy_room()
	return 0.0


## The frame's parts as drawn (local px; cached per size, text and scale): "title_lines",
## "title_fs", "title_step", "title_line", "title" (rect), "gem_c", "gem_r", "art" (rect),
## "band" (rect), "band_over" (the band lies on the art's foot), "band_fs", "rules_lines",
## "rules_fs", "rules_step", "rules_line", "rules" (rect), "rules_on_face", "fits" (every
## word shows) and "needed_h" (the height the whole face needs; the tall mode).
func face_layout() -> Dictionary:
	var key := "%s|%s|%s|%.4f|%d|%d|%s|%d|%.2f|%d|%s" % [size, card_title, description.hash(), text_scale, cost,
		size_mode, fit_whole, pictos.size(), _foot_room(), hotkey.length(), pad_hint]
	if key == _layout_key:
		return _layout
	_layout = _compute_layout()
	_layout_key = key
	return _layout


func _compute_layout() -> Dictionary:
	var s := text_scale
	var w := size.x if size.x > 0.0 else custom_minimum_size.x
	var h := size.y if size.y > 0.0 else custom_minimum_size.y
	var m := UiTheme.SP_XS * s
	var gap := UiTheme.SP_XS * s * 0.5
	var inner_w := w - m * 2.0
	var out := {}
	# Cost gem (cost < 0 = none: Firmware and Daemon offers).
	var gem_r := 0.0 if cost < 0 else (GEM_R if cost < 100 else GEM_R_WIDE) * s
	out["gem_r"] = gem_r
	# Title: Anton at `label`, one step down at a time (never under caption), then on more
	# lines at caption; always at word boundaries.
	var title_x := m + (gem_r * 2.0 + UiTheme.SP_XS * s if cost >= 0 else UiTheme.SP_XS * s)
	var title_w := maxf(1.0, w - m - UiTheme.SP_XS * s - title_x)
	var disp := Palette.display()
	var upper := card_title.to_upper()
	var t_step: int = TITLE_STEPS[TITLE_STEPS.size() - 1]
	var t_fs := UiTheme.font_px_at(t_step, s)
	var t_lines := wrap_words(disp, upper, title_w, t_fs)
	for step in TITLE_STEPS:
		var fs := UiTheme.font_px_at(step, s)
		var lines := wrap_words(disp, upper, title_w, fs)
		if lines.size() <= 1 and lines_fit(disp, lines, title_w, fs):
			t_step = step
			t_fs = fs
			t_lines = lines
			break
	var t_line := step_line(t_step, t_fs)
	var title_h := maxf(t_line * maxi(1, t_lines.size()), gem_r * 2.0 * 0.85)
	out["title_lines"] = t_lines
	out["title_fs"] = t_fs
	out["title_step"] = t_step
	out["title_line"] = t_line
	out["title"] = Rect2(title_x, m, title_w, title_h)
	out["gem_c"] = Vector2(m + gem_r, m + gem_r * 0.9)
	var art_top := m + title_h + gap
	var bottom := h - m - _foot_room()
	var band_h := clampf(h * BAND_SHARE, step_line(UiTheme.LABEL, UiTheme.font_px_at(UiTheme.LABEL, s)),
		step_line(UiTheme.HEADING, UiTheme.font_px_at(UiTheme.HEADING, s)))
	var target := h * ART_SHARE
	if size_mode == SizeMode.DETAIL:
		target = minf(target, inner_w / ART_ASPECT)
	var floor_h := h * ART_FLOOR
	var on_face := rules_on_face()
	out["rules_on_face"] = on_face
	var art_h := target
	var band_over := false
	var r_step: int = RULES_STEPS[0]
	var r_fs := UiTheme.font_px_at(r_step, s)
	var r_lines := PackedStringArray()
	var r_line := 0.0
	var fits := true
	var needed := h
	var body := Palette.body()
	var r_w := inner_w - UiTheme.SP_XS * s * 2.0
	if not on_face:
		# Compact: the art at its share, the band under it (or on its foot when short).
		art_h = minf(target, maxf(0.0, bottom - art_top))
		if bottom - (art_top + art_h + gap) < band_h * 0.6:
			band_over = true
			band_h = minf(band_h, art_h * 0.4)
		else:
			band_h = bottom - (art_top + art_h + gap)
	else:
		var placed := false
		# 1) the rules at body, then caption, with the art at its share (band under the
		# art, or on its foot); 2) caption with the art yielding to its floor; 3) taller.
		for step in RULES_STEPS:
			var fs := UiTheme.font_px_at(step, s)
			var lines := wrap_words(body, description, r_w, fs)
			if not lines_fit(body, lines, r_w, fs):
				continue
			var need := step_line(step, fs) * lines.size()
			for over in [false, true]:
				var room := bottom - art_top - need - gap - (0.0 if over else band_h + gap)
				if room >= target - 0.01:
					art_h = target
					band_over = over
					r_step = step
					r_fs = fs
					r_lines = lines
					placed = true
					break
			if placed:
				break
		if not placed:
			r_step = RULES_STEPS[RULES_STEPS.size() - 1]
			r_fs = UiTheme.font_px_at(r_step, s)
			r_lines = wrap_words(body, description, r_w, r_fs)
			var need := step_line(r_step, r_fs) * r_lines.size()
			band_over = true
			# The art keeps at least its floor clear of the band that lies on its foot; then
			# the band gives way (the rules say what it says); then the card grows.
			var room := bottom - art_top - need - gap
			if room >= floor_h + band_h:
				art_h = room
			elif room >= floor_h - 0.5:
				art_h = room
				band_h = 0.0
			else:
				art_h = floor_h
				band_h = 0.0
				fits = false
				# H = fixed + art: the art's floor grows with the card, so solve for H.
				var fixed := art_top + need + gap + m + _foot_room()
				needed = ceilf(fixed / (1.0 - ART_FLOOR))
		r_line = step_line(r_step, r_fs)
	var art := Rect2(m, art_top, inner_w, art_h)
	out["art"] = art
	# The rarity pip on a stock-coloured tab in the art window's top-right corner.
	out["pip_c"] = art.position + Vector2(art.size.x - PIP_R * PIP_TAB * s, PIP_R * PIP_TAB * s)
	var band := Rect2(m, art.end.y - band_h, inner_w, band_h) if band_over else Rect2(m, art.end.y + gap, inner_w, band_h)
	out["band"] = band
	out["band_over"] = band_over
	out["rules_lines"] = r_lines
	out["rules_fs"] = r_fs
	out["rules_step"] = r_step
	out["rules_line"] = r_line
	out["rules"] = Rect2(m + UiTheme.SP_XS * s, band.end.y + gap, r_w, r_line * r_lines.size())
	out["fits"] = fits and (not on_face or lines_fit(body, r_lines, r_w, r_fs)) and lines_fit(disp, t_lines, title_w, t_fs)
	out["needed_h"] = maxf(needed, h)
	out["band_fs"] = _band_font(band)
	return out


## The band's key-number size: the largest step from `heading` down whose capitals fit the
## band's height and whose pictograms fit its width (never under caption).
func _band_font(band: Rect2) -> int:
	if band.size.y <= 0.0:
		return UiTheme.font_px_at(UiTheme.CAPTION, text_scale)
	var pad := UiTheme.SP_XS * text_scale
	for step in BAND_STEPS:
		var fs := UiTheme.font_px_at(step, text_scale)
		if fs * ANTON_CAP > band.size.y - pad * 2.0:
			continue
		if _band_width(band, fs) <= band.size.x - pad * 2.0:
			return fs
	return UiTheme.font_px_at(UiTheme.CAPTION, text_scale)


## The band's content width at key size `fs`: every pictogram and the key hint.
func _band_width(band: Rect2, fs: int) -> float:
	var x := 0.0
	var r := band.size.y * BAND_GLYPH
	for i in pictos.size():
		var k := 1.0 if i == 0 else BAND_SECONDARY
		x += _picto_width(pictos[i], r * k, roundi(fs * k)) + UiTheme.SP_XS * text_scale
	var key := _key_text()
	if key != "":
		x += Palette.marker().get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px_at(UiTheme.CAPTION, text_scale)).x + UiTheme.SP_XS * text_scale
	return x


## The key hint the band shows ("[1]" on a keyboard, the pad's play button when focused).
func _key_text() -> String:
	var key := pad_hint if pad_hint != "" and has_focus() else hotkey
	return "[%s]" % key if key != "" else ""


## The width of one pictogram in the band: its glyph and its number or tag.
func _picto_width(p: Dictionary, r: float, fs: int) -> float:
	var label := _picto_label(p)
	var disp := Palette.display()
	if String(p["kind"]) == "tag":
		return disp.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var tw := disp.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x if label != "" else 0.0
	return r * 2.0 + (UiTheme.SP_XS * text_scale * 0.5 + tw if label != "" else 0.0)


## A pictogram's number or tag as the band prints it.
static func _picto_label(p: Dictionary) -> String:
	match String(p["kind"]):
		"spin":
			return str(absi(int(p["amount"])))
		"respin":
			return "?"
		"nudge":
			return "×%d" % int(p["amount"]) + (" IN" if bool(p.get("inner", false)) else "")
		"flip":
			return ""
		"tag":
			return String(p["text"])
		"slice":
			var st := int(p.get("status", RC.Status.NONE))
			if st != RC.Status.NONE:
				return String(Palette.STATUS_GLYPHS.get(st, ""))
			return str(int(p["amount"])) if int(p["amount"]) > 0 else ""
	return ""


## The height the whole face needs (px): its size, or more in the tall mode.
func needed_height() -> float:
	if look != Look.STICKER or not rules_on_face():
		return size.y
	return float(face_layout()["needed_h"])


## The tall mode (ART_BIBLE 6.3, 4.3): a full face whose words don't fit even at caption
## with the art at its floor grows its minimum height; a chip tile whose effect text
## doesn't fit does the same. Never shrinks below the caller's size.
func _refit_tall() -> void:
	if not is_inside_tree() or size.y <= 0.0:
		return
	var need := size.y
	if look == Look.STICKER and rules_on_face():
		need = float(face_layout()["needed_h"])
	elif look == Look.CHIP:
		need = size.y + float(tile_parts()["short_by"])
	# A caller that set the minimum again since the last growth owns the new base.
	if not is_equal_approx(custom_minimum_size.y, _tall_min):
		_tall_extra = 0.0
	var base := custom_minimum_size.y - _tall_extra
	var extra := maxf(0.0, ceilf(need) - base) if need > size.y + 0.01 else _tall_extra
	if not is_equal_approx(extra, _tall_extra):
		_tall_extra = extra
		custom_minimum_size.y = base + extra
	_tall_min = custom_minimum_size.y


func _draw_sticker() -> void:
	var L := face_layout()
	var s := text_scale
	var cols := stock_colors()
	var bg: Color = cols[0]
	var fg: Color = cols[1]
	var rect := Rect2(Vector2.ZERO, size)
	var stock := stock_of(rarity())
	var marks := stock_marks(stock)
	# PAPER: a hard shadow under the stock, tape over the top edge (ART_BIBLE 2). A glossy
	# sticker sits on its white die-cut margin.
	var outline := rect.grow(DIECUT * s) if stock == Stock.GLOSSY else rect
	draw_rect(Rect2(outline.position + Vector2.ONE * SHADOW_OFFSET * s, outline.size), Palette.SHADOW)
	if stock == Stock.GLOSSY:
		draw_rect(outline, Palette.PAPER)
		draw_rect(outline, Palette.INK, false, WINDOW_LINE * s)
	draw_rect(rect, bg)
	if bool(marks["grain"]):
		draw_texture_rect(CardArt.grain_texture(), rect, true, Color(fg, GRAIN_ALPHA))
	if type_hatched(variant):
		_draw_type_hatch(rect, fg, s)
	var art: Rect2 = L["art"]
	_draw_art(art, bg, fg)
	draw_rect(art, fg, false, WINDOW_LINE * s)
	if stock == Stock.FOIL:
		_draw_foil_edge(rect, fg, L)
	draw_rect(rect, fg, false, FRAME_LINE * s)
	if bool(marks["gloss"]):
		_draw_gloss(rect)
	draw_rect(Rect2(size.x * TAPE_AT, -TAPE_SIZE.y * 0.6 * s, TAPE_SIZE.x * s, TAPE_SIZE.y * s), Palette.TAPE)
	_draw_title(L, fg)
	if card_data != null:
		draw_circle(L["pip_c"], PIP_R * PIP_TAB * s, bg)
		draw_arc(L["pip_c"], PIP_R * PIP_TAB * s, 0, TAU, 16, fg, WINDOW_LINE * s, true)
		_draw_pip(L["pip_c"], PIP_R * s, String(marks["pip"]), fg)
	if (L["band"] as Rect2).size.y > 0.0:
		_draw_band(L["band"], int(L["band_fs"]), fg, bg)
	if bool(L["rules_on_face"]):
		_draw_rules(L, fg)
	_draw_gem(L)
	if disabled:
		draw_rect(rect, Color(Palette.INK, DISABLED_SHADE))
	if has_focus():
		_draw_focus(rect.grow(FOCUS_OFFSET * s))
	_update_foil(L, stock == Stock.FOIL)


## Whether a card colour carries the type hatch: HACK (pink) stock only (ART_BIBLE 3.1).
static func type_hatched(p_variant: int) -> bool:
	return p_variant == Variant.PINK


## ART_BIBLE 3.1 (never colour alone): HACK (pink) stock carries a light 45 degree hatch, so
## it reads apart from paper stock in greyscale. The art window is drawn over it.
func _draw_type_hatch(rect: Rect2, fg: Color, s: float) -> void:
	var step := TYPE_HATCH_STEP * s
	var col := Color(fg, TYPE_HATCH_ALPHA)
	var w := rect.size.x
	var h := rect.size.y
	var x := -h
	while x < w:
		var t0 := maxf(0.0, -x)
		var t1 := minf(h, w - x)
		if t1 > t0:
			draw_line(rect.position + Vector2(x + t0, t0), rect.position + Vector2(x + t1, t1), col, TYPE_HATCH_W * s)
		x += step


## The rarity pip: a dot (common), a diamond (uncommon) or a star (rare and up).
func _draw_pip(c: Vector2, r: float, kind: String, col: Color) -> void:
	match kind:
		"diamond":
			draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r * 1.25), c + Vector2(r, 0), c + Vector2(0, r * 1.25), c + Vector2(-r, 0)]), col)
		"star":
			var pts := PackedVector2Array()
			for k in 10:
				var a := -PI * 0.5 + k * PI / 5.0
				pts.append(c + Vector2(cos(a), sin(a)) * (r * 1.4 if k % 2 == 0 else r * 0.6))
			draw_colored_polygon(pts, col)
		_:
			draw_circle(c, r * 0.8, col)


## The glossy sticker: a sheen band across the card and a specular top-left edge with a
## shaded bottom-right edge (the sticker's thickness).
func _draw_gloss(rect: Rect2) -> void:
	var s := text_scale
	var x := rect.size.x * GLOSS_AT
	var w := rect.size.x * GLOSS_WIDTH
	var slant := rect.size.y * 0.35
	draw_colored_polygon(PackedVector2Array([Vector2(x, 0), Vector2(x + w, 0), Vector2(x + w - slant, rect.size.y), Vector2(x - slant, rect.size.y)]), Color(Palette.TEXT_HI, GLOSS_ALPHA))
	var e := FRAME_LINE * s
	draw_line(Vector2(e, e), Vector2(rect.size.x - e, e), Color(Palette.TEXT_HI, SPECULAR_ALPHA), e)
	draw_line(Vector2(e, e), Vector2(e, rect.size.y - e), Color(Palette.TEXT_HI, SPECULAR_ALPHA), e)
	draw_line(Vector2(e, rect.size.y + e), Vector2(rect.size.x + e, rect.size.y + e), Color(Palette.INK, EDGE_SHADE), e)
	draw_line(Vector2(rect.size.x + e, e), Vector2(rect.size.x + e, rect.size.y + e), Color(Palette.INK, EDGE_SHADE), e)


## A foil card's edge reads in greyscale too: diagonal hatch in its border band.
func _draw_foil_edge(rect: Rect2, fg: Color, _L: Dictionary) -> void:
	var s := text_scale
	var m := UiTheme.SP_XS * s
	var step := FOIL_HATCH * s
	var col := Color(fg, HATCH_ALPHA)
	var x := 0.0
	while x < rect.size.x:
		draw_line(Vector2(x, m), Vector2(x + m, 0.0), col, 1.0)
		draw_line(Vector2(x, rect.size.y), Vector2(x + m, rect.size.y - m), col, 1.0)
		x += step
	var y := 0.0
	while y < rect.size.y:
		draw_line(Vector2(0.0, y + m), Vector2(m, y), col, 1.0)
		draw_line(Vector2(rect.size.x - m, y + m), Vector2(rect.size.x, y), col, 1.0)
		y += step


## The foil layer (a child canvas item with foil.gdshader, added over the stock): the
## border band at full strength and the art window at FOIL_ART_STRENGTH, never over the
## title, band or rules text. Follows the drawn-only transform (lift, hover, deal-in).
func _update_foil(L: Dictionary, on: bool) -> void:
	if not on:
		if _foil_ci.is_valid():
			RenderingServer.canvas_item_clear(_foil_ci)
		return
	if not _foil_ci.is_valid():
		_foil_ci = RenderingServer.canvas_item_create()
		RenderingServer.canvas_item_set_parent(_foil_ci, get_canvas_item())
		_foil_mat = ShaderMaterial.new()
		_foil_mat.shader = FOIL_SHADER
		RenderingServer.canvas_item_set_material(_foil_ci, _foil_mat.get_rid())
	_foil_mat.set_shader_parameter(&"card_size", size)
	_foil_mat.set_shader_parameter(&"static_tilt", FOIL_STATIC)
	_foil_mat.set_shader_parameter(&"tilt", foil_tilt * FOIL_REACH)
	RenderingServer.canvas_item_clear(_foil_ci)
	var moved := lift != 0.0 or hover_scale != 1.0 or draw_offset != Vector2.ZERO or draw_tilt != 0.0
	RenderingServer.canvas_item_set_transform(_foil_ci, draw_transform() if moved else Transform2D.IDENTITY)
	var m := UiTheme.SP_XS * text_scale
	var full := Color.WHITE
	for r in [Rect2(0, 0, size.x, m), Rect2(0, size.y - m, size.x, m), Rect2(0, m, m, size.y - m * 2.0), Rect2(size.x - m, m, m, size.y - m * 2.0)]:
		RenderingServer.canvas_item_add_rect(_foil_ci, r, full)
	var art: Rect2 = L["art"]
	if bool(L["band_over"]):
		art.size.y -= (L["band"] as Rect2).size.y
	RenderingServer.canvas_item_add_rect(_foil_ci, art, Color(full, FOIL_ART_STRENGTH))


## The illustration this card shows in a window `window_h` px tall: CardData.art when set
## (the final art, no code change), else CardArt's cached risograph stand-in (null while
## the frame's render budget is spent; the card asks again next frame).
func art_texture(window_h: float) -> Texture2D:
	return CardArt.texture_for(card_data, variant, window_h, card_title)


## The part of `tex` a window of `win` shows: the 3:2 art centre-cropped to its aspect.
static func art_region(tex_size: Vector2, win: Vector2) -> Rect2:
	var wa := win.x / maxf(1.0, win.y)
	if wa < tex_size.x / tex_size.y:
		var w := tex_size.y * wa
		return Rect2((tex_size.x - w) * 0.5, 0.0, w, tex_size.y)
	var h := tex_size.x / wa
	return Rect2(0.0, (tex_size.y - h) * 0.5, tex_size.x, h)


## The illustration in the window (ART_BIBLE 7.3): the art, centre-cropped to the window.
func _draw_art(art: Rect2, bg: Color, _fg: Color) -> void:
	var tex := art_texture(art.size.y)
	if tex == null:
		draw_rect(art, bg.lerp(Palette.PAPER_ALT, 0.5))
		if is_inside_tree() and not get_tree().process_frame.is_connected(queue_redraw):
			get_tree().process_frame.connect(queue_redraw, CONNECT_ONE_SHOT)
		return
	draw_texture_rect_region(tex, art, art_region(tex.get_size(), art.size))


func _draw_title(L: Dictionary, fg: Color) -> void:
	var lines: PackedStringArray = L["title_lines"]
	var fs: int = L["title_fs"]
	var line: float = L["title_line"]
	var r: Rect2 = L["title"]
	var top := r.position.y + (r.size.y - line * lines.size()) * 0.5
	for i in lines.size():
		var base := top + i * line + (line + fs * ANTON_CAP) * 0.5
		draw_string(Palette.display(), Vector2(r.position.x, base), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fg)


func _draw_rules(L: Dictionary, fg: Color) -> void:
	var lines: PackedStringArray = L["rules_lines"]
	var fs: int = L["rules_fs"]
	var line: float = L["rules_line"]
	var r: Rect2 = L["rules"]
	var body := Palette.body()
	var lead := (line - body.get_height(fs)) * 0.5 + body.get_ascent(fs)
	for i in lines.size():
		draw_string(body, Vector2(r.position.x, r.position.y + i * line + lead), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, fg)


## The cost gem: a marker numeral in a circle (cost < 0 = none). ANIM-R1 C6: a RAM refusal
## pulses it HARM.
func _draw_gem(L: Dictionary) -> void:
	if cost < 0:
		return
	var s := text_scale
	var r: float = L["gem_r"]
	var c: Vector2 = L["gem_c"]
	var fill := Palette.NOTE_YELLOW
	if cost_alarm > 0.0:
		fill = fill.lerp(Palette.HARM, cost_alarm)
		draw_arc(c, r + 2.0 * s + r * COST_PULSE_GROW * cost_alarm, 0, TAU, 24, Color(Palette.HARM, cost_alarm), 3.0, true)
	draw_circle(c + Vector2.ONE * s, r, Palette.SHADOW)
	draw_circle(c, r, fill)
	draw_arc(c, r, 0, TAU, 24, Palette.INK, FRAME_LINE * s, true)
	var fs := UiTheme.font_px_at(UiTheme.LABEL if cost < 100 else UiTheme.BODY, s)
	var mk := Palette.marker()
	var txt := str(cost)
	var tw := mk.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(mk, Vector2(c.x - tw * 0.5, c.y + fs * 0.36), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.INK)


## The effect band: the key glyph and number at `fs` (heading when it fits), the other
## pictograms smaller, and the key hint at the right. Printed in the card's ink with its
## stock colour for the lettering.
func _draw_band(band: Rect2, fs: int, fg: Color, bg: Color) -> void:
	draw_rect(band, fg)
	var s := text_scale
	var pad := UiTheme.SP_XS * s
	var r := band.size.y * BAND_GLYPH
	var x := band.position.x + pad
	var cy := band.get_center().y
	for i in pictos.size():
		var k := 1.0 if i == 0 else BAND_SECONDARY
		x += _draw_picto(pictos[i], Vector2(x, cy), r * k, roundi(fs * k), bg) + pad
	var key := _key_text()
	if key != "":
		var kfs := UiTheme.font_px_at(UiTheme.CAPTION, s)
		var kw := Palette.marker().get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1, kfs).x
		draw_string(Palette.marker(), Vector2(band.end.x - pad - kw, cy + kfs * 0.36), key, HORIZONTAL_ALIGNMENT_LEFT, -1, kfs, bg)


## Draws one pictogram with its left edge at `at` (vertical centre); returns its width.
func _draw_picto(p: Dictionary, at: Vector2, r: float, fs: int, col: Color) -> float:
	var s := text_scale
	var c := at + Vector2(r, 0.0)
	var label := _picto_label(p)
	var disp := Palette.display()
	var stroke := maxf(1.5, 2.0 * s * r / (UiTheme.SP_S * s))
	match String(p["kind"]):
		"spin", "respin":
			# A circular arrow: clockwise for a positive spin.
			var d := -1.0 if int(p["amount"]) < 0 else 1.0
			draw_arc(c, r * 0.85, -PI * 0.9, PI * 0.6, 16, col, stroke)
			var a := PI * 0.6 if d > 0.0 else -PI * 0.9
			var tip := c + Vector2(cos(a), sin(a)) * r * 0.85
			var tg := Vector2(-sin(a), cos(a)) * d
			draw_colored_polygon(PackedVector2Array([tip + tg * r * 0.5, tip + tg.orthogonal() * r * 0.42, tip - tg.orthogonal() * r * 0.42]), col)
		"nudge":
			# Two small arrows, one each way (a nudge card is aimed either way).
			for side in [-1.0, 1.0]:
				var t := c + Vector2(side * r, 0)
				draw_colored_polygon(PackedVector2Array([t, t - Vector2(side * r * 0.8, r * 0.6), t - Vector2(side * r * 0.8, -r * 0.6)]), col)
		"flip":
			draw_line(c + Vector2(-r * 0.4, -r), c + Vector2(-r * 0.4, r), col, stroke)
			draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.4, -r - r * 0.3), c + Vector2(-r * 0.9, -r * 0.3), c + Vector2(0.1 * r, -r * 0.3)]), col)
			draw_line(c + Vector2(r * 0.4, -r), c + Vector2(r * 0.4, r), col, stroke)
			draw_colored_polygon(PackedVector2Array([c + Vector2(r * 0.4, r + r * 0.3), c + Vector2(-0.1 * r, r * 0.3), c + Vector2(r * 0.9, r * 0.3)]), col)
		"slice":
			SliceIcon.draw_icon(self, c, r, int(p["type"]), Palette.slice_color(int(p["type"])))
		"tag":
			var w := disp.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			draw_string(disp, Vector2(at.x, at.y + fs * ANTON_CAP * 0.5), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			return w
	if label == "":
		return r * 2.0
	var lx := at.x + r * 2.0 + UiTheme.SP_XS * s * 0.5
	# A status glyph is a font glyph (Anton lacks it): the body face draws it.
	var font := Palette.body() if String(p["kind"]) == "slice" and int(p.get("status", RC.Status.NONE)) != RC.Status.NONE else disp
	draw_string(font, Vector2(lx, at.y + fs * ANTON_CAP * 0.5), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	return lx - at.x + font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x


## FOCUS brackets (ART_BIBLE 6): four corner marks round `r`.
func _draw_focus(r: Rect2) -> void:
	var s := text_scale
	var arm := FOCUS_ARM * s
	var w := FOCUS_STROKE * s
	for corner in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if corner.x <= r.get_center().x else -1.0
		var sy := 1.0 if corner.y <= r.get_center().y else -1.0
		draw_line(corner, corner + Vector2(arm * sx, 0.0), Palette.FOCUS, w)
		draw_line(corner, corner + Vector2(0.0, arm * sy), Palette.FOCUS, w)


## Word-wraps `text` to `width` px at `font_size` in the mono face (tiles; at word
## boundaries only).
static func wrap_px(text: String, width: float, font_size: int) -> PackedStringArray:
	return wrap_words(Palette.mono(), text, width, font_size)


## How many rules lines the face shows (0 on the compact face).
func sticker_body_rows() -> int:
	return (face_layout()["rules_lines"] as PackedStringArray).size() if rules_on_face() else 0


## The rules text as drawn: {"fs": font px, "line": line step px, "rows": lines shown,
## "lines": the wrapped text}. The compact face shows none.
func sticker_body_fit() -> Dictionary:
	var L := face_layout()
	var lines: PackedStringArray = L["rules_lines"] if rules_on_face() else PackedStringArray()
	return {"fs": L["rules_fs"], "line": L["rules_line"], "rows": lines.size(), "lines": lines}


## True when the whole text shows on the card: a full face whose every word fits (a chip
## tile: every effect line). The compact face carries its words in the band, the tooltip
## and the detail view, so it reports false.
func text_whole() -> bool:
	if look == Look.STICKER:
		var L := face_layout()
		return bool(L["rules_on_face"]) and bool(L["fits"])
	if look == Look.CHIP:
		var parts := tile_parts()
		return int(parts["rows"]) >= (parts["desc_lines"] as PackedStringArray).size()
	return true


## The sticker's parts as drawn (local rects; H24 S10 tests: none overlaps another): the
## title, the gem, the art window, each rules line shown ("body"), the effect band
## ("pictos") and the buy sticker.
func sticker_parts() -> Dictionary:
	var L := face_layout()
	var rows: Array[Rect2] = []
	if bool(L["rules_on_face"]):
		var r: Rect2 = L["rules"]
		var line: float = L["rules_line"]
		for i in (L["rules_lines"] as PackedStringArray).size():
			rows.append(Rect2(r.position.x, r.position.y + i * line, r.size.x, line))
	var out := {"body": rows, "title": L["title"], "art": L["art"], "pictos": L["band"]}
	if cost >= 0:
		var gr: float = L["gem_r"]
		out["gem"] = Rect2(Vector2(L["gem_c"]) - Vector2(gr, gr), Vector2(gr, gr) * 2.0)
	if buy_button != null:
		out["buy"] = Rect2(buy_button.position, buy_button.size)
	return out


func _draw_tile() -> void:
	var s := text_scale
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Palette.TERMINAL_BG)
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
			draw_string(Palette.display(), icon_c + Vector2(-20, 22), str(slice_output), HORIZONTAL_ALIGNMENT_CENTER, 40, UiTheme.font_px_at(UiTheme.LABEL, s), Palette.PAPER)
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
		draw_rect(rect, Color(Palette.INK, DISABLED_SHADE))
	var fs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	var mono := Palette.mono()
	var name_lines := wrap_px(card_title.to_upper(), size.x - 8, fs)
	var line_h := mono.get_height(fs)
	for i in name_lines.size():
		draw_string(mono, Vector2(4, 100 + i * line_h), name_lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	if cost >= 0:
		var pfs := UiTheme.font_px_at(UiTheme.BODY, s)
		var cost_text := "%d" % cost
		var pw := mono.get_string_size(cost_text, HORIZONTAL_ALIGNMENT_LEFT, -1, pfs).x
		var px := size.x / 2.0 - (pw + 18) / 2.0
		StatIcon.draw(self, Vector2(px + 6, size.y - 15), 6, StatIcon.CYCLES, Palette.CELL_ACID)
		draw_string(mono, Vector2(px + 17, size.y - 10), cost_text, HORIZONTAL_ALIGNMENT_LEFT, -1, pfs, Palette.CELL_ACID)


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
	draw_string(Palette.display(), Vector2(-22, 8), initials, HORIZONTAL_ALIGNMENT_CENTER, 40, UiTheme.TITLE, col.darkened(0.2))
	draw_set_transform_matrix(_icon_xf)


## The frame a tile's icon is drawn in (identity but while a scaled tile draws its icon).
var _icon_xf: Transform2D = Transform2D.IDENTITY


# --- H21 screens: price tags and big lettering on shop tiles ------------------------------

## A shop price (Cycles), drawn on a price tag with the coin (H21 #12: prices sat in the
## RAM-cost circle and read as a play cost; the circle keeps the card's real RAM cost).
## -1 = no price.
var price: int = -1
## The tag reads "N+" (a slice's price depends on the slot it overwrites).
var price_from: bool = false
## Price tag height and coin radius at scale 1.0 (px); its lettering is the body step.
const PRICE_TAG_H := 20.0
const PRICE_COIN_R := 6.0
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
	var fs := UiTheme.font_px_at(UiTheme.BODY, s)
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
	var fs := UiTheme.font_px_at(UiTheme.BODY, s)
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
## chip tiles), "rows" (their count), "dfs", "buy" (the sticker's rect) and "short_by"
## (px the chip's effect text lacks; the tile grows by it, W4 tall mode). Names and
## effect text are at the caption step at least and wrap at word boundaries (W4, ART_BIBLE
## 4.3); every name line shows.
func tile_parts() -> Dictionary:
	var s := text_scale
	var mono := Palette.mono()
	var foot := buy_room()
	var fs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	var lines := wrap_px(card_title.to_upper(), size.x - 8.0, fs)
	var line_h := mono.get_height(fs)
	var shown := lines.size()
	var desc_rows := 0
	var dfs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	var dline := mono.get_height(dfs)
	var ext := _icon_extent()
	var icon_h := ext.y + ext.w
	var desc_lines := PackedStringArray()
	var icon_floor := CHIP_ICON_SHRINK
	var short_by := 0.0
	if look == Look.CHIP:
		desc_lines = wrap_px(tile_description(), size.x - 8.0, dfs)
		# ANIM-R1 M10: the icon gives way further for the whole effect text.
		if fit_whole:
			icon_floor = CHIP_ICON_FIT_SHRINK
		var spare := size.y - foot - line_h * shown - icon_h * icon_floor - TILE_GAP * 2.0 * s
		desc_rows = clampi(floori(spare / dline), 0, desc_lines.size())
		# ANIM-R1 M10 in the Modem's fixed quads: the effect text steps down toward the
		# caption step at scale 1.0 (never smaller: ART_BIBLE 4.3.2), then the tile grows.
		while fit_whole and desc_rows < desc_lines.size() and dfs > UiTheme.CAPTION:
			dfs -= 1
			dline = mono.get_height(dfs)
			desc_lines = wrap_px(tile_description(), size.x - 8.0, dfs)
			desc_rows = clampi(floori(spare / dline), 0, desc_lines.size())
		short_by = maxf(0.0, desc_lines.size() * dline - maxf(0.0, spare))
	var text_top := size.y - foot - desc_rows * dline
	var name_top := text_top - line_h * shown
	# The icon in the room above the names, shrunk (never under its floor) when the room
	# is short, centred in it.
	var room := name_top - TILE_GAP * s * 2.0
	var k := clampf(room / icon_h, icon_floor, 1.0)
	var top := TILE_GAP * s + maxf(0.0, (room - icon_h * k) * 0.5)
	var centre := Vector2(size.x * 0.5, top + ext.y * k)
	var out := {"k": k, "centre": centre, "fs": fs, "dfs": dfs, "rows": desc_rows, "lines": lines, "desc_lines": desc_lines,
		"icon": Rect2(centre - Vector2(ext.x, ext.y) * k, Vector2(ext.x + ext.z, ext.y + ext.w) * k), "short_by": short_by}
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
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Palette.TERMINAL_BG)
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
			var vs := UiTheme.font_px_at(UiTheme.LABEL, minf(s, TILE_VALUE_MAX_SCALE))
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
		draw_rect(rect, Color(Palette.INK, DISABLED_SHADE))
	var mono := Palette.mono()
	for i in shown:
		draw_string(mono, Vector2(4, name_top + mono.get_ascent(fs) + i * line_h), lines[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, fs, Palette.TERMINAL_TEXT)
	if cost >= 0 and buy_button == null:
		var pfs := UiTheme.font_px_at(UiTheme.BODY, s)
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
## Chip tiles: the chip icon's least room (px).
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
## text colour, then the effect text; the tile grows taller when it doesn't fit (W4: no
## ellipsis, ART_BIBLE 6.3). The foot is the buy button's (H24 S10: the text measured
## against the sticker's real height; its third line ran under it at 1.6).
func _draw_chip_tile() -> void:
	var rect := Rect2(Vector2.ZERO, size)
	var hot := _lifted and not disabled
	draw_rect(rect, Palette.TERMINAL_BG_HOT if hot else Palette.TERMINAL_BG)
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
		draw_rect(rect, Color(Palette.INK, DISABLED_SHADE))
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
		draw_string(mono, Vector2(4, rows_at[i].position.y + mono.get_ascent(dfs)), desc[i], HORIZONTAL_ALIGNMENT_CENTER, size.x - 8, dfs, Palette.TERMINAL_TEXT)


## The chip's effect lines shown on the tile now (tests: at least one at every text size).
func chip_lines_shown() -> int:
	return int(tile_parts()["rows"])
