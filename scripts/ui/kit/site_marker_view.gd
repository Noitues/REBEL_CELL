class_name SiteMarkerView
extends Control
## ART-5 5d: one Site marker v4 on screen (SiteMarker): its disc is a vinyl node sticker
## (VinylSticker, ART-1 1B: node stickers are vinyl, bible §1.2) holding the round 42
## generator's disc art (M14 asset parity; an Exploit Site's with its type sub-badge); the ring, pips,
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
	if sticker != null and is_instance_valid(_art):
		_art.queue_redraw()  # a cleared disc is the concept's grey art


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
	sticker.resized.connect(_place_sticker)
	_place_sticker.call_deferred()


## The disc art the sticker shows (SiteMarker.disc_art: its texture name, "" for another
## corp's crest on the plain disc). An Exploit Site's carries its type sub-badge.
func disc_art() -> String:
	return SiteMarker.disc_art(spec) if sticker != null else ""


func _place_sticker() -> void:
	if sticker == null or not is_instance_valid(sticker):
		return
	# The body's centre on the marker's origin (the sticker scales about its pivot, the
	# body's centre, so a hover or press keeps it there).
	sticker.position = -sticker.body_rect.get_center()
	var cr := sticker.content_root
	_art.position = Vector2.ZERO
	_art.size = cr.size
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
	SiteMarker.draw_art(_art, spec, sz * 0.5, minf(sz.x, sz.y) * 0.5)


func _draw() -> void:
	if spec.is_empty():
		return
	if with_pad:
		SiteMarker.draw_pad(self, spec, Vector2(0, SiteMarker.PAD_DROP))
	SiteMarker.draw_under(self, spec, Vector2.ZERO)


func _draw_over() -> void:
	if spec.get("status") == SiteMarker.ST_DOWN:
		SiteMarker.draw_bolt(_over, Vector2.ZERO, SiteMarker.disc_px(spec))
