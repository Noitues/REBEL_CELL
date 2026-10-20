class_name EntryTimelineDemo
extends Control
## NA-25 motion-lab demo: the street entry's beats (EntryBeats, the HQ side then the street side) as one strip at their real
## `entry_*` times, a playhead crossing them once. The real thing runs in `EntryCover` over the street view; this shows the table
## a tuned time changes. Lab only.

const ROW_H := 34.0
const LEFT := 24.0
const FONT := 16
var _rows: Array[Dictionary] = []
var _total := 0.0
var _t := 0.0


func _init() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var beats: Array = EntryBeats.HQ_BEATS + EntryBeats.STREET_BEATS + EntryBeats.ZOOM_BEATS
	_rows = EntryBeats.table(beats, false, false)
	_total = EntryBeats.total(_rows)


## The strip's length (s).
func length() -> float:
	return _total


func _process(delta: float) -> void:
	_t = minf(_t + delta, _total)
	queue_redraw()


func _draw() -> void:
	var f := Palette.mono()
	var w := size.x - LEFT * 2.0
	var y := 120.0
	for r in _rows:
		var x0 := LEFT + w * float(r["start"]) / maxf(_total, 0.001)
		var x1 := LEFT + w * float(r["end"]) / maxf(_total, 0.001)
		var live := _t >= float(r["start"]) and _t < float(r["end"])
		draw_rect(Rect2(x0, y, maxf(x1 - x0 - 2.0, 1.0), ROW_H - 6.0), Palette.CELL_ACID if live else Palette.NET_CYAN)
		draw_string(f, Vector2(LEFT, y + ROW_H - 12.0), "%s  %.2f s" % [String(r["beat"]).to_upper(), float(r["end"]) - float(r["start"])],
				HORIZONTAL_ALIGNMENT_LEFT, -1, FONT, Palette.TEXT_HI)
		y += ROW_H
	var px := LEFT + w * _t / maxf(_total, 0.001)
	draw_line(Vector2(px, 100.0), Vector2(px, y + 8.0), Palette.TEXT_HI, 2.0)
