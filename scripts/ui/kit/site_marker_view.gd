class_name SiteMarkerView
extends Control
## ART-5 5d: one Site marker v4 on screen (SiteMarker): its disc is a vinyl node sticker
## (VinylSticker, ART-1 1B: node stickers are vinyl, bible §1.2) holding the kind's art and,
## on an Exploit Site, the type sub-badge from the glyph atlas (GlyphIcon); the ring, pips,
## corner badge and the SEIZURE NOTICE slip draw under it, the DOWN bolt over it. A cleared
## disc is grey vinyl; a DOWN node is the disabled sticker (grey, 80 %) under the white bolt.
## The control's origin is the disc's centre; `scale` sizes it (the map undoes its zoom).
## Shared by the Grid map and its key, so the key shows exactly what the map draws. A view:
## it never changes game state.

## The sticker's art is drawn at this many px per screen px (crisp when the map zooms in).
const ART_SCALE := 2.0
## The sticker's white die-cut border (screen px): a node sticker's thin rim.
const BORDER_PX := 1.5

var spec: Dictionary = {}
## Draws the pad under the disc (the key's swatches; on the map the pad sits on the roof).
var with_pad: bool = false
var sticker: VinylSticker = null
var _holder: Control = null
var _art: Control = null
var _badge: GlyphIcon = null
var _over: Control = null


func _init(p_spec: Dictionary = {}, p_with_pad: bool = false) -> void:
	name = "SiteMarker"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	with_pad = p_with_pad
	_over = Control.new()
	_over.name = "Over"
	_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_over.draw.connect(_draw_over)
	add_child(_over, false, Node.INTERNAL_MODE_BACK)
	set_spec(p_spec)


## Shows marker `p_spec` (SiteMarker.spec_for); rebuilds the sticker only when its disc
## changes.
func set_spec(p_spec: Dictionary) -> void:
	var old := spec
	spec = p_spec.duplicate()
	var needs_disc: bool = not spec.is_empty() and spec.get("status") != SiteMarker.ST_TAKEN and spec.get("kind") != SiteMarker.KIND_CENTRAL_SERVER
	if not needs_disc:
		if sticker != null:
			sticker.queue_free()
			sticker = null
	elif sticker == null or _disc_key(old) != _disc_key(spec):
		_build_sticker()
	_apply_state()
	queue_redraw()
	_over.queue_redraw()


func _disc_key(s: Dictionary) -> String:
	return "%s|%s|%s|%s|%s" % [s.get("kind"), s.get("status") == SiteMarker.ST_CLAIMED or s.get("status") == SiteMarker.ST_DOWN,
		s.get("avail") == SiteMarker.AV_NOT_YET, s.get("exploit"), s.get("corp")]


func _build_sticker() -> void:
	if sticker != null:
		sticker.queue_free()
	if _holder == null:
		# The sticker's own scale is its motion's (hover, press, disabled reset it to 1): the
		# art scale lives on a holder.
		_holder = Control.new()
		_holder.name = "DiscHolder"
		_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_holder.scale = Vector2.ONE / ART_SCALE
		add_child(_holder)
		move_child(_holder, 0)
	var d := SiteMarker.disc_px(spec) * ART_SCALE
	sticker = VinylSticker.new()
	sticker.name = "Disc"
	sticker.shape = VinylSticker.Shape.CIRCLE
	sticker.stock = VinylSticker.Stock.GLOSS
	sticker.border_px = BORDER_PX * ART_SCALE
	sticker.body_size = Vector2(d, d)
	sticker.seed = absi(hash(_disc_key(spec))) % 997 + 1
	_holder.add_child(sticker)
	_art = Control.new()
	_art.name = "Art"
	_art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_art.draw.connect(_draw_art)
	sticker.content_root.add_child(_art)
	_badge = null
	if spec.get("kind") == SiteMarker.KIND_EXPLOIT and int(spec.get("exploit", 0)) != RC.ExploitType.NONE \
			and spec.get("status") != SiteMarker.ST_CLAIMED and spec.get("status") != SiteMarker.ST_DOWN:
		var key := GlyphTableData.key_for_exploit(int(spec["exploit"]))
		var t := GlyphIcon.table()
		var glyph: StringName = t.ids.get(key, GlyphTableData.PENDING)
		var r := d * SiteMarker.SUB_BADGE_SHARE
		_badge = GlyphIcon.make(glyph, r * 1.3)
		_badge.name = "TypeBadge"
		_badge.fill = Palette.PAPER
		sticker.content_root.add_child(_badge)
	sticker.resized.connect(_place_sticker)
	_place_sticker.call_deferred()


## The exploit type glyph's atlas name (checks; &"" without one).
func type_glyph() -> StringName:
	return _badge.glyph if _badge != null else &""


func _place_sticker() -> void:
	if sticker == null or not is_instance_valid(sticker):
		return
	# The body's centre on the marker's origin (the sticker scales about its pivot, the
	# body's centre, so a hover or press keeps it there).
	sticker.position = -sticker.body_rect.get_center()
	var cr := sticker.content_root
	_art.position = Vector2.ZERO
	_art.size = cr.size
	if _badge != null:
		var d := cr.size.x
		var r := sticker.body_size.x * SiteMarker.SUB_BADGE_SHARE
		var at := cr.size * 0.5 + SiteMarker.SUB_BADGE_AT * sticker.body_size.x
		_badge.position = at - _badge.custom_minimum_size * 0.5
		_badge.size = _badge.custom_minimum_size
		_art.set_meta(&"badge", [at, r, d])
	sticker.refresh()


func _apply_state() -> void:
	if sticker == null:
		return
	if spec.get("status") == SiteMarker.ST_DOWN:
		sticker.set_state(VinylSticker.State.DISABLED)
	else:
		if sticker.state != VinylSticker.State.REST:
			sticker.set_state(VinylSticker.State.REST)
		# A cleared disc is grey vinyl (set after any state change: its end state resets grey).
		sticker.grey = 1.0 if spec.get("status") == SiteMarker.ST_CLEARED else 0.0
	sticker.refresh()


func _draw_art() -> void:
	var sz := _art.size
	var c := sz * 0.5
	var r := minf(sz.x, sz.y) * 0.5
	_art.draw_circle(c, r, SiteMarker.disc_fill(spec))
	SiteMarker.draw_art(_art, spec, c, r)
	if _art.has_meta(&"badge"):
		var b: Array = _art.get_meta(&"badge")
		_art.draw_circle(b[0], b[1], Palette.NIGHT_SKY.lerp(Palette.RESIST_GOLD, SiteMarker.DISC_TINT))
		_art.draw_arc(b[0], b[1], 0.0, TAU, 24, Palette.RESIST_GOLD, maxf(1.5, b[1] * 0.14), true)


func _draw() -> void:
	if spec.is_empty():
		return
	if with_pad:
		SiteMarker.draw_pad(self, spec, Vector2(0, SiteMarker.PAD_DROP))
	SiteMarker.draw_under(self, spec, Vector2.ZERO)


func _draw_over() -> void:
	if spec.get("status") == SiteMarker.ST_DOWN:
		SiteMarker.draw_bolt(_over, Vector2.ZERO, SiteMarker.disc_px(spec))
