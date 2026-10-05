class_name HeatTrace
extends Control
## ART-11 4D: the audit report's Heat chart (ref round 21 `campaign_dossier.jpg`, dossier21.py
## `heat_chart`): the subject's exposure, typed on the report. The game keeps no Heat history,
## only the thresholds it crossed (each set a raid off), so the trace runs from 0 through every
## threshold crossed (red dots: the raids) to the Heat at closure; the major Heat levels are
## dashed rules. Look only.

var marks: Array[int] = []
var heat: int = 0
var heat_max: int = 100
var levels: Array[int] = []

## The chart's height at text scale 1.0 (px), the left room for the level numbers, the dash
## and gap of a rule, and the dots' radii (px at 1.0).
const HEIGHT := 92.0
const LEFT := 26.0
const DASH := 5.0
const DASH_GAP := 5.0
const DOT := 2.5
const RAID_DOT := 4.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(0, HEIGHT * Settings.text_scale)


func _y(v: float) -> float:
	var pad := DOT * 2.0 * Settings.text_scale
	return size.y - pad - (size.y - pad * 2.0) * clampf(v / maxf(1.0, heat_max), 0.0, 1.0)


func _draw() -> void:
	var s := Settings.text_scale
	var f := EndFaces.typed()
	var fs := UiTheme.font_px(UiTheme.CAPTION)
	var left := LEFT * s
	for lv in levels:
		var y := _y(lv)
		var x := left
		while x < size.x:
			draw_line(Vector2(x, y), Vector2(minf(x + DASH * s, size.x), y), PaperInk.text(Palette.END_TYPE_SOFT), 1.0)
			x += (DASH + DASH_GAP) * s
		draw_string(f, Vector2(0, y + f.get_ascent(fs) * 0.4), str(lv), HORIZONTAL_ALIGNMENT_LEFT, left, fs, PaperInk.text(Palette.END_TYPE_SOFT))
	var values: Array[int] = [0]
	values.append_array(marks)
	values.append(heat)
	var pts := PackedVector2Array()
	for i in values.size():
		pts.append(Vector2(left + (size.x - left - RAID_DOT * s) * i / maxf(1.0, values.size() - 1.0), _y(values[i])))
	draw_polyline(pts, PaperInk.text(Palette.END_TYPE_INK), maxf(1.5, 1.5 * s), true)
	for i in pts.size():
		var raid := i > 0 and i < pts.size() - 1
		draw_circle(pts[i], (RAID_DOT if raid else DOT) * s, PaperInk.text(Palette.END_STAMP_RED if raid else Palette.END_TYPE_INK))
