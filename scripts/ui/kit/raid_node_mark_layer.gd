class_name RaidNodeMarkLayer
extends Control
## RAID-VIS F2: the per-node outcome marks on a CityMapOverlay that has no playout layer: the after-action report's
## map and the HQ / Grid afterwards. It lays `RaidNodeMarks` (the one helper) on the raid pencil layer at each
## marked node, following the map's camera, with the tint disc (DOWN dimmed, TAKEN in the corporation's colour)
## drawn under the map's labels... on this layer. DOWN and TAKEN stay; a HOLDS check is written, held and wiped
## once (the motion table's pencil mark timings). View glue: it reads, it never changes state.

## site id (String) -> RaidNodeMarks.DOWN / TAKEN / HOLDS.
var marks: Dictionary = {}
var overlay: CityMapOverlay = null
var corp_color: Color = Palette.CORP_SOLACE
var _pool: RaidPencilPool = null
var _age: float = 0.0
## RAID-VIS F3: TAKEN Sites next to the territory: each is a new raid entry point and is written ENTRY POINT.
var entries: Array[StringName] = []
const ENTRY_WORD := "ENTRY POINT" # TR
## The entry word stands this many radii over the node, above the TAKEN flag, when nothing is in the way.
const ENTRY_LIFT := 3.4
## A-085: the label's candidate spots, in turn (shares of the node's radius from its centre: x is added to half the
## word's width on the left / right spots), and the room it keeps from node icons and HUD words (px) and from the frame.
const ENTRY_SPOTS: Array[Vector2] = [Vector2(0.0, -3.4), Vector2(0.0, 3.2), Vector2(-1.0, -1.2), Vector2(1.0, -1.2),
	Vector2(-1.0, 1.6), Vector2(1.0, 1.6), Vector2(0.0, -5.4), Vector2(0.0, 5.2), Vector2(-1.0, -3.6), Vector2(1.0, -3.6),
	Vector2(0.0, -8.0), Vector2(0.0, 8.0), Vector2(-1.6, -5.0), Vector2(1.6, -5.0), Vector2(-1.6, 5.0), Vector2(1.6, 5.0), Vector2(-2.4, 0.0), Vector2(2.4, 0.0)]
const ENTRY_PAD := 4.0
const FRAME_MARGIN := 8.0
## The icon's reach for the label's clearance (x radius).
const ICON_CLEAR := 2.2
## HUD words the label keeps off (global px rects), supplied by the screen; null = none.
var avoid: Callable = Callable()
## The last placed label per entry id: {"rect": Rect2 (global px), "moved": bool}.
var _entry_spots: Dictionary = {}


## A-085: where entry `id`'s label stands (global px): the first candidate spot, clamped into the frame, that misses every
## node icon and HUD word (the TARGET word's placement rule); else the least covered one. Empty when off the map.
func entry_label(id: StringName) -> Dictionary:
	var p := RaidMapAnchor.site(overlay, id)
	if p.x == INF:
		return {}
	var r := CityMapOverlay.ICON_RADIUS * RaidMapAnchor.scale(overlay)
	var size := RaidPencilPool.word_size(tr(ENTRY_WORD), UiTheme.CAPTION) + Vector2(ENTRY_PAD, ENTRY_PAD) * 2.0
	var frame := get_viewport_rect().grow(-FRAME_MARGIN)
	var blocks: Array[Rect2] = []
	for n: Dictionary in overlay.nodes:
		var q := RaidMapAnchor.site(overlay, n["id"])
		if q.x != INF and n["id"] != id:
			blocks.append(Rect2(q - Vector2(r, r) * ICON_CLEAR, Vector2(r, r) * 2.0 * ICON_CLEAR))
	if avoid.is_valid():
		for w in avoid.call():
			blocks.append(w)
	var best := Rect2()
	var best_cover := INF
	var best_i := 0
	for i in ENTRY_SPOTS.size():
		var sp := ENTRY_SPOTS[i]
		var c := p + Vector2(sp.x * (size.x * 0.5 + r * ICON_CLEAR), sp.y * r)
		var rect := Rect2(c - size * 0.5, size)
		rect.position.x = clampf(rect.position.x, frame.position.x, maxf(frame.position.x, frame.end.x - size.x))
		rect.position.y = clampf(rect.position.y, frame.position.y, maxf(frame.position.y, frame.end.y - size.y))
		var cover := 0.0
		for b in blocks:
			if b.intersects(rect):
				cover += b.intersection(rect).get_area()
		if cover < best_cover:
			best_cover = cover
			best = rect
			best_i = i
		if cover <= 0.0:
			break
	return {"rect": best, "moved": best_i != 0, "node": p}


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
	name = "RaidNodeMarks"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Sets the marks to show (replaces them; a HOLDS check restarts).
func set_marks(p_marks: Dictionary, p_corp: Color, p_entries: Array[StringName] = []) -> void:
	marks = p_marks.duplicate()
	corp_color = p_corp
	entries = p_entries.duplicate()
	_age = 0.0
	queue_redraw()


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


func _process(delta: float) -> void:
	_age += delta
	if overlay == null or overlay.city == null or not is_visible_in_tree():
		return
	queue_redraw()
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var zoom := RaidMapAnchor.scale(overlay)
	var r := CityMapOverlay.ICON_RADIUS * zoom
	var ids := marks.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		var outcome := String(marks[id])
		var p := RaidMapAnchor.site(overlay, StringName(id))
		if p.x == INF:
			continue
		var write := 1.0
		var wipe := 0.0
		if outcome == RaidNodeMarks.HOLDS:
			var w := RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WRITE)
			var h := RaidFxLayer.mark_seconds(RaidFxLayer.MARK_HOLD)
			var wp := RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WIPE)
			write = 1.0 if w <= 0.0 else clampf(_age / w, 0.0, 1.0)
			wipe = (1.0 if wp <= 0.0 else clampf((_age - w - h) / wp, 0.0, 1.0)) if _age >= w + h else 0.0
		RaidNodeMarks.draw(_pool, String(id), outcome, p, r, write, wipe, String(id).hash())
	_entry_spots.clear()
	for id in entries:
		var spot := entry_label(id)
		if spot.is_empty():
			continue
		_entry_spots[id] = spot
		var rect: Rect2 = spot["rect"]
		_pool.word("entry_%s" % id, tr(ENTRY_WORD), rect.get_center(), UiTheme.CAPTION, GreasePencilMark.Ink.THREAT, 1.0, 1.0, 0.0, -0.05)
		if bool(spot["moved"]):
			# A short pencil leader from the label to its node when the label had to move off the default spot.
			var np: Vector2 = spot["node"]
			var from := Vector2(clampf(np.x, rect.position.x, rect.end.x), clampf(np.y, rect.position.y, rect.end.y))
			var dir := (np - from).normalized()
			_pool.stroke("entry_lead_%s" % id, [PackedVector2Array([from, np - dir * r * 1.4])], GreasePencilMark.Ink.THREAT, 1.0, 0.0, false, 7)
	_pool.end()


func _draw() -> void:
	if overlay == null or overlay.city == null:
		return
	var r := CityMapOverlay.ICON_RADIUS * overlay.screen_k()
	for id in marks:
		var outcome := String(marks[id])
		if outcome == RaidNodeMarks.HOLDS:
			continue
		var c := overlay.icon_at(StringName(id))
		if c.x == INF:
			continue
		RaidNodeMarks.tint(self, outcome, c, r, corp_color)
