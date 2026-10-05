class_name OperativeDossier
extends Control
## ART-7 3B (ART_BIBLE v2 §4.6 panels, §1.2 corp paper): the run's operative as the target
## corporation's intercepted file on them, pinned over the netrun map: the corp letterhead
## ("<CORP> SECURITY // PERSON OF INTEREST // FILE"), the subject's mugshot, the fields in the
## typewriter face (subject, class, rank, HP, RAM, wheel, hub core, deck), the class's raid
## station bonus in a ruled box, the red AT LARGE stamp by the name and the HEAT stamp
## ("HEAT 52: HUNTED", §4.3: the number lives here). Paper is what the Cell stole, so it never
## carries the Cell's own controls. Folds to a compact file (letterhead, subject, HP, the two
## stamps) when the full one would take more than MAX_WIDTH_SHARE of the screen (big text).
## The sheet is 1B's CorpPaperPanel (paper stock shader, the corp letterhead over its rule),
## drawn behind this file's own ink (fields, mugshot, stamps). View only: `show_file` takes
## what the scene read.

## The file at text scale 1.0 (px): width, margins, the letterhead's height, the mugshot's
## side, the gap between rows.
const WIDTH := 252.0
const MARGIN := 10.0
const HEAD_H := CorpPaperPanel.LETTERHEAD_H
const MUG := 64.0
const ROW_GAP := 2.0
## Lettering at text scale 1.0 (px): letterhead, its sub line, fields, stamps.
const HEAD_FONT := 17
const SUB_FONT := 12
const FIELD_FONT := 12
const STAMP_FONT := 15
## The stamps' tilts (rad), ruling (px) and alpha.
const AT_LARGE_TILT := 0.12
const HEAT_TILT := -0.08
const STAMP_RULE := 2.0
const STAMP_ALPHA := 0.88
## The share of the screen's width the full file may take before it folds to the compact one.
const MAX_WIDTH_SHARE := 0.24
## The paper's own tilt (rad) and its drop shadow (px).
const PAPER_TILT := 0.0
const SHADOW_OFFSET := Vector2(3, 4)
## The words (keys).
const SUBTITLE := "PERSON OF INTEREST // FILE" # TR
const SECURITY := "%s SECURITY" # TR
const F_SUBJECT := "SUBJECT" # TR
const F_CLASS := "CLASS" # TR
const F_RANK := "RANK" # TR
const F_HP := "HP" # TR
const F_RAM := "RAM" # TR
const F_WHEEL := "WHEEL" # TR
const F_HUB := "HUB CORE" # TR
const F_DECK := "DECK" # TR
const DECK_CARDS := "%d cards" # TR
const STATION := "IF STATIONED (RAIDS):" # TR
const AT_LARGE := "AT LARGE" # TR
const HEAT_STAMP := "HEAT %d: %s" # TR

## What the file shows (the scene reads it from the run): corp, corp_color, subject,
## class_word, class_id, operative_id, rank, hp, max_hp, ram, wheel (Array[String]), hub,
## deck, station (Array[String]), heat, band (the band's word).
var data: Dictionary = {}
## True while the compact file shows (big text on a small screen).
var compact: bool = false
## The screen folds the file when the route needs the room (ART-7 3B).
var force_compact: bool = false:
	set(v):
		if v != force_compact:
			force_compact = v
			_relayout()
var _rows: Array = []
## 1B's corp paper sheet under the ink (letterhead, stock, shadow).
var paper: CorpPaperPanel


func _init() -> void:
	name = "OperativeDossier"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	paper = CorpPaperPanel.new()
	paper.name = "Paper"
	paper.stamp = ""
	paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	paper.show_behind_parent = true
	add_child(paper)
	paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# The words are translated where the file is built; drawn as given.
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	Settings.changed.connect(_relayout)
	resized.connect(queue_redraw)


## Shows the file for `p_data` (see `data`).
func show_file(p_data: Dictionary) -> void:
	data = p_data
	# The letterhead carries the corp's mark word (MERIDIAN, HALCYON): the sheet's letterhead
	# is one line at a fixed size.
	var words := String(data.get("corp", "")).to_upper().split(" ", false)
	paper.corp_name = words[0] if not words.is_empty() else ""
	paper.corp_color = data.get("corp_color", Palette.CORP_MERIDIAN)
	_relayout()


func _s() -> float:
	return Settings.text_scale


## The file's width at the current text size.
func file_width() -> float:
	return WIDTH * _s()


func _relayout() -> void:
	var vw := get_viewport_rect().size.x if is_inside_tree() else 1280.0
	compact = force_compact or file_width() > vw * MAX_WIDTH_SHARE
	_rows = _build_rows()
	custom_minimum_size = Vector2(file_width() if not compact else minf(file_width(), vw * MAX_WIDTH_SHARE), _height())
	update_minimum_size()
	queue_redraw()


## [label, value] rows of the fields (compact: subject, class and HP only).
func _build_rows() -> Array:
	var out: Array = []
	if data.is_empty():
		return out
	out.append([tr(F_SUBJECT), String(data.get("subject", ""))])
	out.append([tr(F_CLASS), String(data.get("class_word", "")).to_upper()])
	if not compact:
		out.append([tr(F_RANK), "R%d" % int(data.get("rank", 0))])
	out.append([tr(F_HP), "%d / %d" % [int(data.get("hp", 0)), int(data.get("max_hp", 0))]])
	if not compact:
		out.append([tr(F_RAM), str(int(data.get("ram", 0)))])
	return out


func _line_h(fs: int) -> float:
	return RouteInk.paper_font().get_height(fs) + ROW_GAP * _s()


## The file's height for its rows (px).
func _height() -> float:
	var s := _s()
	var fs := roundi(FIELD_FONT * s)
	var lh := _line_h(fs)
	var h := HEAD_H + RouteInk.paper_font().get_height(maxi(roundi(SUB_FONT * s), 1)) + MARGIN * s
	h += maxf(MUG * s if not compact else 0.0, lh * _rows.size())
	if not compact:
		h += MARGIN * s + lh * 6.0  # wheel, hub core, deck (label + value each)
		var station: Array = data.get("station", [])
		if not station.is_empty():
			h += MARGIN * s + lh * (1.0 + station.size()) + MARGIN * s
	h += (STAMP_FONT * s) * (2.2 if not compact else 3.6) + MARGIN * s
	return h


func _draw() -> void:
	if data.is_empty():
		return
	var s := _s()
	var w := size.x
	var h := size.y
	draw_set_transform(Vector2.ZERO, PAPER_TILT)
	var head_h := HEAD_H
	var pf := RouteInk.paper_font()
	var sfs := maxi(roundi(SUB_FONT * s), 1)
	var x := MARGIN * s
	# Under the sheet's letterhead: "<CORP> SECURITY // PERSON OF INTEREST // FILE".
	var sub := "%s // %s" % [(tr(SECURITY) % "").strip_edges(), tr(SUBTITLE)]
	draw_string(pf, Vector2(x, head_h + pf.get_ascent(sfs)), sub, HORIZONTAL_ALIGNMENT_LEFT, w - x * 2.0, sfs, RouteInk.PAPER_FIELD)
	head_h += pf.get_height(sfs)
	# The mugshot and the fields.
	var y := head_h + MARGIN * s
	var fs := roundi(FIELD_FONT * s)
	var lh := _line_h(fs)
	var fx := x
	if not compact:
		var mug := Rect2(Vector2(x, y), Vector2(MUG, MUG) * s)
		draw_rect(mug, Palette.DESK_DARK)
		PortraitArt.draw_operative(self, mug.grow(-2.0 * s), StringName(data.get("class_id", "")), StringName(data.get("operative_id", "")), String(data.get("subject", "")))
		draw_rect(mug, RouteInk.PAPER_INK, false, s)
		fx = mug.end.x + MARGIN * s
	var label_w := (w - fx - MARGIN * s) * 0.42
	var ry := y + pf.get_ascent(fs)
	for row in _rows:
		draw_string(pf, Vector2(fx, ry), String(row[0]), HORIZONTAL_ALIGNMENT_LEFT, label_w, fs, RouteInk.PAPER_FIELD)
		draw_string(pf, Vector2(fx + label_w, ry), String(row[1]), HORIZONTAL_ALIGNMENT_LEFT, w - fx - label_w - MARGIN * s, fs, RouteInk.PAPER_INK)
		ry += lh
	# AT LARGE beside the name (rubber stamp).
	# AT LARGE by the name, over the short rows' free right side (HP, RAM); the compact file
	# gives it a row of its own above the Heat stamp.
	if not compact:
		var stamp_y := y + lh * minf(3.5, _rows.size() - 0.5)
		_stamp(Vector2(w - MARGIN * s, stamp_y), tr(AT_LARGE), AT_LARGE_TILT, true)
	else:
		_stamp(Vector2(w - MARGIN * s, h - MARGIN * s - STAMP_FONT * s * 1.9), tr(AT_LARGE), AT_LARGE_TILT, true)
	y = maxf(y + (MUG * s if not compact else 0.0), y + lh * _rows.size())
	if not compact:
		y += MARGIN * s * 0.5
		draw_line(Vector2(x, y), Vector2(w - x, y), RouteInk.PAPER_RULE, s)
		y += MARGIN * s * 0.5
		var wheel: Array = data.get("wheel", [])
		var parts := PackedStringArray()
		for wd in wheel:
			parts.append(String(wd))
		for pair in [[tr(F_WHEEL), " ".join(parts)], [tr(F_HUB), String(data.get("hub", ""))], [tr(F_DECK), tr(DECK_CARDS) % int(data.get("deck", 0))]]:
			draw_string(pf, Vector2(x, y + pf.get_ascent(fs)), String(pair[0]), HORIZONTAL_ALIGNMENT_LEFT, w - x * 2.0, fs, RouteInk.PAPER_FIELD)
			y += lh
			draw_string(pf, Vector2(x, y + pf.get_ascent(fs)), String(pair[1]), HORIZONTAL_ALIGNMENT_LEFT, w - x * 2.0, fs, RouteInk.PAPER_INK)
			y += lh
		var station: Array = data.get("station", [])
		if not station.is_empty():
			y += MARGIN * s * 0.5
			var box := Rect2(Vector2(x, y), Vector2(w - x * 2.0, lh * (1.0 + station.size()) + MARGIN * s * 0.5))
			draw_rect(box, RouteInk.PAPER_STAMP, false, STAMP_RULE * s * 0.6)
			var sy := y + MARGIN * s * 0.25 + pf.get_ascent(fs)
			draw_string(pf, Vector2(x + MARGIN * s * 0.5, sy), tr(STATION), HORIZONTAL_ALIGNMENT_LEFT, box.size.x - MARGIN * s, fs, RouteInk.PAPER_STAMP)
			for line in station:
				sy += lh
				draw_string(pf, Vector2(x + MARGIN * s * 0.5, sy), String(line), HORIZONTAL_ALIGNMENT_LEFT, box.size.x - MARGIN * s, fs, RouteInk.PAPER_INK)
			y = box.end.y + MARGIN * s * 0.5
	# The Heat stamp at the foot, right.
	_stamp(Vector2(w - MARGIN * s, h - MARGIN * s - STAMP_FONT * s * 0.6), heat_words(), HEAT_TILT, true)
	draw_set_transform(Vector2.ZERO, 0.0)


## "HEAT 52: HUNTED" (translated).
func heat_words() -> String:
	return tr(HEAT_STAMP) % [int(data.get("heat", 0)), String(data.get("band", "")).to_upper()]


## A red rubber stamp of `text` with its right edge at `right` (its centre line at right.y),
## tilted `tilt`.
func _stamp(right: Vector2, text: String, tilt: float, ruled: bool) -> void:
	var s := _s()
	var f := RouteInk.stamp_font()
	var fs := roundi(STAMP_FONT * s)
	var tw := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var pad := 4.0 * s
	var box := Rect2(Vector2(-tw - pad * 2.0, -f.get_height(fs) * 0.5 - pad * 0.5), Vector2(tw + pad * 2.0, f.get_height(fs) + pad))
	var col := Color(RouteInk.PAPER_STAMP, STAMP_ALPHA)
	draw_set_transform(right.rotated(PAPER_TILT), PAPER_TILT + tilt)
	if ruled:
		draw_rect(box, col, false, STAMP_RULE * s)
	draw_string(f, Vector2(box.position.x + pad, box.position.y + pad * 0.5 + f.get_ascent(fs)), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	draw_set_transform(Vector2.ZERO, PAPER_TILT)
