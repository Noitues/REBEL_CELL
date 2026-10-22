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
## The entry word stands this many radii over the node, above the TAKEN flag.
const ENTRY_LIFT := 3.4


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
	for id in entries:
		var p := RaidMapAnchor.site(overlay, id)
		if p.x != INF:
			_pool.word("entry_%s" % id, tr(ENTRY_WORD), p - Vector2(0.0, r * ENTRY_LIFT), UiTheme.CAPTION, GreasePencilMark.Ink.THREAT, 1.0, 1.0, 0.0, -0.05)
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
