class_name DecryptedHoloPanel
extends Control
## The decrypted holo panel (ART-1 1B; ART_BIBLE v2 §1.2 "Decrypted holo": hacked corp intel,
## what the Cell stole and decrypted: the selected Site file, THREAT INTEL, intercepted corp
## news toasts; never anything the Cell owns). The corp tint at about 78 %, 4 px scanlines,
## 3-4 slow bands (`holo_bands`, T0), a +-2 px RGB split on the edge only, a near-opaque
## scrim (0.88) behind it, the corp seal cracked with a red fracture and a DECRYPTED stamp in
## its slot. `addons/rc_look/shaders/rc_holo.gdshader`, glass under `content`, scanlines over.
## Reduce effects: the bands hold still and the RGB split is off (§5.4). A view only.
##
## M14 B1c (integration review D17; round 21 `intel_decrypt.png`, round 44 `raid_setup.png`):
## the finished material by default on every holo: the tint at 78 %, 4 px scanlines at 12 %,
## three slow bands (`holo_bands`: one pass in 6 s), the +-2 px edge split, a local 0.88 scrim
## right behind the plate (`backing`; `scrim` keeps the whole-screen one for modals), and the
## corp's seal (its emblem when `corporation` is set; ui21 `seal_overlay`: the two halves
## offset, a red fracture down the middle) under the DECRYPTED stamp, which is in the Cell's
## acid like the concepts' green stamp. Skins only swap the accent tokens.

const BANDS := &"holo_bands"
## LOOK-TOOLBOX 15: the glass, scanlines, bands, edge split and cracked seal are `RcLookHolo` (addons/rc_look; every
## number in look_holo.tres / look_quality.tres). TINT_SHARE is the tint's strength on the words (`ink`).
const TINT_SHARE := 0.78
## B1c (D17): the room (px round the plate) the local backing and its neighbours keep.
const BACKING_OUT := 4.0
## The crest's half size as a share of the seal radius (CorpSeal: the emblem inside the ring).
const CREST_SHARE := 0.62
## The seal's radius; the stamp's tilt (deg).
const SEAL_R := 30.0
## The seal centre's x in the stamp slot, as a share of the seal radius.
const SEAL_SLOT_X := 0.5
const STAMP_TILT_DEG := -8.0
const STAMP_WORD := "DECRYPTED"
const STAMP_SLOT := Vector2(180, 48)
## M14 12Q-ACCESS: the stamp box's room round its lettering (px each side) and the least lettering
## the stamp shrinks to (px) to stay in its slot.
const STAMP_BOX_PAD := Vector2(8, 2)
const STAMP_MIN_PX := 10
## B1c: the stamp's ink (the Cell's acid, as the route holo's DECRYPTED chip) and its alpha.
const STAMP_COLOR := Palette.CELL_ACID
const STAMP_ALPHA := 0.9
## B1c-b (art director): a dark ink under-shadow so the acid stamp reads on every corp tint
## (Solace's green above all): its offset (px) and alpha.
const STAMP_SHADOW_OFFSET := Vector2(2, 2)
const STAMP_SHADOW_ALPHA := 0.7
## The seal letter's baseline drop as a share of its height.
const SEAL_LETTER_DROP: float = 0.32

@export var corp_color: Color = Palette.CORP_SOLACE:
	set(v):
		corp_color = v
		_sync()
## The corp's seal letter (crest stand-in until the corp crests land).
@export var seal_letter: String = "S":
	set(v):
		seal_letter = v
		queue_redraw()
## Lays the 0.88 scrim over the whole screen behind the panel.
@export var scrim: bool = true:
	set(v):
		scrim = v
		if _scrim != null:
			_scrim.visible = v
## B1c (D17): the 0.88 scrim right behind the plate (BACKING_OUT round it), so the holo reads
## over a busy city even where the whole-screen scrim is off.
@export var backing: bool = true:
	set(v):
		backing = v
		queue_redraw()
## B1c: the corporation whose emblem the seal carries (CorpSeal); empty: the seal letter.
@export var corporation: StringName = &"":
	set(v):
		corporation = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()
@export var seed: int = 5
## Parity ROUTE-03: the cracked corp seal (off for the route's node holo: the concept's DEPOT 15
## holo has none, and it sat on the fields). B1c (D17): it sits under the DECRYPTED stamp, in
## the stamp's slot, so it moves with the stamp.
@export var seal: bool = true:
	set(v):
		seal = v
		if stamp_slot != null:
			stamp_slot.queue_redraw()

## LOOK-TOOLBOX 15: the look state the holo draws under (null: the live Settings). Tests and the lab set it.
var state_override: RcLookQualityState = null:
	set(v):
		state_override = v
		_sync()
		for c in get_children(true):
			if c is CanvasItem:
				(c as CanvasItem).queue_redraw()
## BIG-TEXT: the text scale the stamp is lettered at (a panel built smaller to fit sets it); 0 = the player's.
var text_k: float = 0.0
## BIG-TEXT: the stamp slot and the seal in it at this share of their size (a panel built smaller to fit).
var slot_k: float = 1.0
var content: Control = null
## The stamp slot (top right): DECRYPTED is drawn here; a caller may add its own stamp.
var stamp_slot: Control = null

var _glass_mat: ShaderMaterial = null
var _over_mat: ShaderMaterial = null
var _over: Control = null
var _scrim: ColorRect = null


func _init() -> void:
	_glass_mat = RcLookHolo.material(RcLookHolo.GLASS)
	_over_mat = RcLookHolo.material(RcLookHolo.OVER)
	_scrim = ColorRect.new()
	_scrim.color = Palette.HOLO_SCRIM
	_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrim.top_level = true  # the whole screen, behind the panel
	add_child(_scrim, false, Node.INTERNAL_MODE_FRONT)
	var glass := Control.new()
	glass.name = "Glass"
	glass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glass.material = _glass_mat
	glass.draw.connect(func() -> void: glass.draw_rect(Rect2(Vector2.ZERO, size).grow(RcLookHolo.bleed_px(_state())), Palette.NO_TINT))
	add_child(glass, false, Node.INTERNAL_MODE_FRONT)
	glass.set_anchors_preset(Control.PRESET_FULL_RECT)
	content = Control.new()
	content.name = "Content"
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content, false, Node.INTERNAL_MODE_FRONT)
	content.set_anchors_preset(Control.PRESET_FULL_RECT)
	stamp_slot = Control.new()
	stamp_slot.name = "StampSlot"
	stamp_slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stamp_slot.draw.connect(_draw_stamp)
	add_child(stamp_slot, false, Node.INTERNAL_MODE_FRONT)
	_over = Control.new()
	_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_over.material = _over_mat
	_over.draw.connect(func() -> void: _over.draw_rect(Rect2(Vector2.ZERO, size), Palette.NO_TINT))
	add_child(_over, false, Node.INTERNAL_MODE_BACK)
	_over.set_anchors_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	resized.connect(_layout)
	Settings.changed.connect(_sync)
	_layout()


func _layout() -> void:
	stamp_slot.size = STAMP_SLOT * slot_k
	stamp_slot.position = Vector2(size.x - stamp_slot.size.x - UiTheme.SP_M, UiTheme.SP_S)
	_scrim.visible = scrim
	_scrim.position = Vector2.ZERO
	_scrim.size = get_viewport_rect().size if is_inside_tree() else size
	_sync()
	for c in get_children(true):
		if c is CanvasItem:
			(c as CanvasItem).queue_redraw()


## The player's look state this panel draws under: the live Settings, or `state_override` (tests, labs).
func _state() -> RcLookQualityState:
	return state_override if state_override != null else RcLookQualityState.from_settings()


func _sync() -> void:
	if _glass_mat == null:
		return
	var st := _state()
	# M14 12Q-ACCESS (L78): high contrast: opaque black glass with no tint, scanlines, bands or
	# split, and a thick solid edge in the corp's colour (RcLookHolo's quality rules + HighContrast).
	var hc := st.high_contrast
	var live := Motion.live(BANDS)
	var over := {
		&"band_seconds": maxf(Motion.seconds(BANDS), 0.1),
		&"edge_px": maxf(RcLookHolo.config().edge_px * HighContrast.HC_EDGE_SCALE, float(HighContrast.HC_EDGE_MIN)) if hc else RcLookHolo.config().edge_px,
	}
	var entry := Motion.entry(BANDS)
	if entry != null and not entry.enabled:
		over[&"band_strength"] = 0.0  # the entry is switched off
	if not live:
		over[&"band_roll"] = 0.0  # held still: reduce effects / motion, headless, or the entry off
	var tint := HighContrast.lift(corp_color) if hc else corp_color
	var deep := HighContrast.BG if hc else Palette.NET_BG_OUTER
	for m in [_glass_mat, _over_mat]:
		RcLookHolo.apply(m as ShaderMaterial, size, tint, deep, st, body_share(corp_color), over)
	queue_redraw()
	if stamp_slot != null:
		stamp_slot.queue_redraw()


## B1c (D17): the local backing right behind the plate; LOOK-TOOLBOX 15: its alpha is the quality rule's (the blurred
## glass carries the legibility on mid and high; the low tier, with no blur, backs it harder).
func _draw() -> void:
	if backing:
		var a := float(RcLookHolo.settings(_state())[&"backing_alpha"])
		draw_rect(Rect2(Vector2.ZERO, size).grow(BACKING_OUT), HighContrast.plate(Color(Palette.HOLO_SCRIM, a)))


## The seal's centre (stamp-slot local): at the stamp's left end, so the stamp lies over half of it and the cracked half
## shows (LOOK-TOOLBOX 15: centred under the stamp it was hidden by the lettering).
func seal_center() -> Vector2:
	return Vector2(SEAL_R * slot_k * SEAL_SLOT_X, stamp_slot.size.y * 0.5)


## The cracked seal under the stamp (RcLookHolo.draw_seal): a corp ring with its emblem (or letter), the emblem's halves
## offset and a red fracture down the middle (ui21 `seal_overlay`), the ring cut where it crosses.
func _draw_seal() -> void:
	var c := seal_center()
	var r := SEAL_R * slot_k
	var ring := corp_color
	ring.a = RcLookHolo.config().seal_ring_alpha
	var t := CorpSeal.emblem(corporation) if corporation != &"" else null
	RcLookHolo.draw_seal(stamp_slot, c, r, corp_color, Palette.HARM, t)
	if t == null:
		var font := Palette.display()
		var px := UiTheme.font_px_at(UiTheme.TITLE, text_k if text_k > 0.0 else Settings.text_scale)
		var w := font.get_string_size(seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
		HighContrast.draw_text(stamp_slot, font, c + Vector2(-w.x * 0.5, w.y * SEAL_LETTER_DROP), seal_letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ring)


## The DECRYPTED stamp over the cracked seal: Anton in a ruled box, tilted (a rubber stamp's
## ink), in the Cell's acid (the concepts' green DECRYPTED: the Cell's own mark on stolen data).
func _draw_stamp() -> void:
	if seal:
		_draw_seal()
	var font := Palette.display()
	var px := stamp_px(stamp_slot.size, text_k if text_k > 0.0 else Settings.text_scale)
	var sz := font.get_string_size(STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var col := HighContrast.ink(STAMP_COLOR)
	col.a = 1.0 if HighContrast.on() else STAMP_ALPHA
	var centre := stamp_slot.size * 0.5
	var box := stamp_box(sz)
	for pass_shadow in [true, false]:
		var at: Vector2 = centre + (STAMP_SHADOW_OFFSET if pass_shadow else Vector2.ZERO)
		var ink: Color = stamp_shadow_color() if pass_shadow else col
		stamp_slot.draw_set_transform(at, deg_to_rad(STAMP_TILT_DEG))
		stamp_slot.draw_rect(box, ink, false, 3.0)
		HighContrast.draw_text(stamp_slot, font, Vector2(-sz.x * 0.5, sz.y * 0.32), STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ink)
	stamp_slot.draw_set_transform(Vector2.ZERO, 0.0)


## M14 12Q-ACCESS (12Q-HQ, seen at text 2.0): the stamp's ruled box round lettering of size `sz`.
static func stamp_box(sz: Vector2) -> Rect2:
	return Rect2(-sz * 0.5 - STAMP_BOX_PAD, sz + STAMP_BOX_PAD * 2.0)


## M14 12Q-ACCESS: the stamp's lettering (px) at text scale `k` in a slot of `slot` px: the
## HEADING step, made smaller only as far as the tilted box must to stay inside the slot's width
## (at text 2.0 the stamp reached past the HQ Site holo's right edge).
static func stamp_px(slot: Vector2, k: float) -> int:
	var font := Palette.display()
	var px := UiTheme.font_px_at(UiTheme.HEADING, k)
	while px > STAMP_MIN_PX and stamp_width(font.get_string_size(STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px)) > slot.x:
		px -= 1
	return px


## M14 12Q-ACCESS: the width the tilted stamp box round lettering of size `sz` takes on screen.
static func stamp_width(sz: Vector2) -> float:
	var b := stamp_box(sz).size
	var a := absf(deg_to_rad(STAMP_TILT_DEG))
	return b.x * cos(a) + b.y * sin(a)


## B4 (art director, round 44 `hq_idle.png`): the body's tint fill and scanlines are FILL_SHARE /
## SCAN_STRENGTH as measured on round 44's Meridian file; a brighter corp hue (Solace's green
## carries twice the orange's luminance) takes its share times this factor, so every corp's
## body is the same dark glass (never a green box): BODY_LUMA_REF over the hue's luminance,
## at most 1 (a darker hue keeps the measured share).
static func body_share(tint: Color) -> float:
	return clampf(Palette.luminance(BODY_LUMA_REF) / maxf(Palette.luminance(tint), 0.0001), 0.0, 1.0)


## B4: the hue the measured body shares belong to (round 44's Meridian file).
const BODY_LUMA_REF := Palette.CORP_MERIDIAN


## B1c-b: the stamp's under-shadow ink (dark, STAMP_SHADOW_ALPHA).
static func stamp_shadow_color() -> Color:
	return Color(Palette.INK, STAMP_SHADOW_ALPHA)


## B1c-b: the holo's words and edge colour for corp tint `tint`: the tint at TINT_SHARE over the
## bright text white (the full corp colour on the words; the body stays dark).
static func ink(tint: Color) -> Color:
	return Palette.TEXT_HI.lerp(tint, TINT_SHARE)


## LOOK-TOOLBOX 15: how far the cracked seal reaches left of the stamp slot (px) at slot scale `k`, for a layout that
## keeps its words clear of it.
static func seal_reach(k: float) -> float:
	return maxf(SEAL_R * k * (1.0 - SEAL_SLOT_X), 0.0)
