class_name MainframeArt
extends RefCounted
## ART-9 4A: the MAINFRAME's, the loot sheet's and the event's art as the concept scripts drew it
## (tools/art_bake/mainframe_parts_bake.py on tag `art-concepts-r43`: fwlib.chip, daemon_row,
## shop.pegboard / dymo, r31lib.price_tag, slicekit.wheel, recycle.scene, reward.liner / kiss_cut,
## event.plate_button). The parts are at the concepts' scale (their 1920x1080 canvas); `SCALE` brings
## them to the game's 1280x720. Helpers draw them on any CanvasItem (whole, or sliced so the middle
## stretches). View only.

const DIR := "res://assets/ui/mainframe/"
const TABLE := DIR + "parts.json"
## Concept px -> game px (1920 -> 1280).
const SCALE := 2.0 / 3.0

static var _tex: Dictionary = {}
static var _meta: Dictionary = {}


## Part `name`'s texture (null when the bake has no such part).
static func tex(name: String) -> Texture2D:
	if not _tex.has(name):
		var p := DIR + name + ".png"
		_tex[name] = load(p) as Texture2D if ResourceLoader.exists(p) else null
	return _tex[name]


## True when the bake has part `name`.
static func has(name: String) -> bool:
	return tex(name) != null


## The parts table (sizes and anchors in concept px).
static func meta() -> Dictionary:
	if _meta.is_empty():
		var j := load(TABLE) as JSON
		_meta = j.data if j != null and j.data is Dictionary else {}
	return _meta


## Part `name`'s anchor (concept px; its top-left when it has none).
static func anchor(name: String) -> Vector2:
	var m: Dictionary = meta().get(name, {})
	var a: Array = m.get("anchor", [0, 0])
	return Vector2(float(a[0]), float(a[1]))


## Draws part `name` whole with its anchor at `at`, at `k` x the game scale.
static func draw_at(ci: CanvasItem, name: String, at: Vector2, k: float = 1.0, modulate: Color = Palette.NO_TINT) -> void:
	var t := tex(name)
	if t == null:
		return
	var s := SCALE * k
	ci.draw_texture_rect(t, Rect2(at - anchor(name) * s, t.get_size() * s), false, modulate)


## Draws part `name` into `r` (game px) sliced in three across: its left `left` and right `right`
## concept px keep their shape at the game scale, the middle stretches.
static func draw_h3(ci: CanvasItem, name: String, r: Rect2, left: float, right: float, modulate: Color = Palette.NO_TINT) -> void:
	var t := tex(name)
	if t == null:
		return
	var sz := t.get_size()
	var k := r.size.y / sz.y
	var lw := minf(left * k, r.size.x * 0.5)
	var rw := minf(right * k, r.size.x * 0.5)
	ci.draw_texture_rect_region(t, Rect2(r.position, Vector2(lw, r.size.y)), Rect2(0, 0, left, sz.y), modulate)
	ci.draw_texture_rect_region(t, Rect2(r.position + Vector2(lw, 0), Vector2(maxf(0.0, r.size.x - lw - rw), r.size.y)), Rect2(left, 0, sz.x - left - right, sz.y), modulate)
	ci.draw_texture_rect_region(t, Rect2(Vector2(r.end.x - rw, r.position.y), Vector2(rw, r.size.y)), Rect2(sz.x - right, 0, right, sz.y), modulate)


## Draws part `name` into `r` (game px) sliced in nine: its `edge` concept px border keeps its shape
## at the game scale; the middle is cut from the part's own middle at the game scale (no stretch:
## the pegboard keeps its holes' pitch), from its top-left.
static func draw_9(ci: CanvasItem, name: String, r: Rect2, edge: float, modulate: Color = Palette.NO_TINT) -> void:
	var t := tex(name)
	if t == null:
		return
	var sz := t.get_size()
	var e := edge * SCALE
	var inner := Rect2(r.position + Vector2(e, e), r.size - Vector2(e, e) * 2.0)
	var src_in := Vector2(minf(inner.size.x / SCALE, sz.x - edge * 2.0), minf(inner.size.y / SCALE, sz.y - edge * 2.0))
	ci.draw_texture_rect_region(t, inner, Rect2(Vector2(edge, edge), src_in), modulate)
	# edges: cut from the part's sides (as long as they need, from the start)
	ci.draw_texture_rect_region(t, Rect2(r.position + Vector2(e, 0), Vector2(inner.size.x, e)), Rect2(edge, 0, src_in.x, edge), modulate)
	ci.draw_texture_rect_region(t, Rect2(Vector2(r.position.x + e, r.end.y - e), Vector2(inner.size.x, e)), Rect2(edge, sz.y - edge, src_in.x, edge), modulate)
	ci.draw_texture_rect_region(t, Rect2(r.position + Vector2(0, e), Vector2(e, inner.size.y)), Rect2(0, edge, edge, src_in.y), modulate)
	ci.draw_texture_rect_region(t, Rect2(Vector2(r.end.x - e, r.position.y + e), Vector2(e, inner.size.y)), Rect2(sz.x - edge, edge, edge, src_in.y), modulate)
	# corners
	ci.draw_texture_rect_region(t, Rect2(r.position, Vector2(e, e)), Rect2(0, 0, edge, edge), modulate)
	ci.draw_texture_rect_region(t, Rect2(Vector2(r.end.x - e, r.position.y), Vector2(e, e)), Rect2(sz.x - edge, 0, edge, edge), modulate)
	ci.draw_texture_rect_region(t, Rect2(Vector2(r.position.x, r.end.y - e), Vector2(e, e)), Rect2(0, sz.y - edge, edge, edge), modulate)
	ci.draw_texture_rect_region(t, Rect2(r.end - Vector2(e, e), Vector2(e, e)), Rect2(sz - Vector2(edge, edge), Vector2(edge, edge)), modulate)


## The label-maker word for `word` as the concept drew it (its English art; null when the
## player's language says it otherwise: then the word is lettered live).
static func dymo(word: String) -> Texture2D:
	if TranslationServer.translate(word) != word:
		return null
	return tex("dymo_" + word.to_lower().replace(" ", "_"))
