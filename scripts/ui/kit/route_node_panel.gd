class_name RouteNodePanel
extends Control
## ART-7 3B (ART_BIBLE v2 §4.6 panels, §1.2 decrypted holo; D14): the netrun node's file as
## hacked corp intel: the corp tint at about 78 % over a near-opaque scrim, 4 px scanlines, a
## +-2 px RGB split on the edge only, the corp seal cracked with a red fracture and the
## DECRYPTED stamp. It shows only tier, type and rewards (and what entering costs in Heat),
## and only for a decrypted node: under the current rules (GDD 4.2) every route node's kind
## is known, so every node shown on the map is decrypted (DECISIONS, ART-7 3B). View only:
## `show_node` takes the words the scene built from the rules. The plate is 1B's
## DecryptedHoloPanel (tint, scanlines, bands, edge split, cracked seal, DECRYPTED stamp),
## drawn behind the words (no full-screen scrim over the map).

## The panel at text scale 1.0 (px): width, margins, title lettering, field lettering, the
## field column's share.
const WIDTH := 300.0
const MARGIN := 12.0
const TITLE_FONT := 18
const FIELD_FONT := 13
const LABEL_SHARE := 0.3
## The panel widens with the text only this far (the ROUTE column sets the rest).
const MAX_WIDTH_SCALE := 1.3
## The words (keys).
const F_TIER := "TIER" # TR
const F_TYPE := "TYPE" # TR
const F_REWARDS := "REWARDS" # TR
const F_HEAT := "HEAT" # TR
## Parity ROUTE-03 (round 37 `city_default`: the DEPOT 15 holo): DECRYPTED is a small chip in the
## foot's corner beside the seal, never over the title or a field; its lettering (px at 1.0),
## padding (px) and keyline (px). Every field's words wrap in their column (none is cut) and end
## above the foot.
const STAMP_WORD := "DECRYPTED" # TR
const CHIP_STEP := UiTheme.CAPTION
const CHIP_PAD := Vector2(6, 2)
const CHIP_LINE := 1.5

## What the panel shows: title, tier (int), type (words), rewards (Array[String]), heat
## (words, "" = none), corp_color.
var data: Dictionary = {}
## The node shown (&"" = none).
var node_id: StringName = &""
## 1B's holo plate behind the words.
var plate: DecryptedHoloPanel


func _init() -> void:
	name = "RouteNodePanel"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate = DecryptedHoloPanel.new()
	plate.name = "Plate"
	plate.scrim = false
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.show_behind_parent = true
	add_child(plate)
	plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Parity ROUTE-03: the plate's big stamp sat over the title and its seal on the fields (the
	# concept's DEPOT 15 holo has neither): the panel letters its own DECRYPTED chip.
	plate.stamp_slot.visible = false
	plate.seal = false
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	Settings.changed.connect(_relayout)
	resized.connect(queue_redraw)


## Shows node `id`'s file (`p_data`: see `data`); an empty dict hides it.
func show_node(id: StringName, p_data: Dictionary) -> void:
	node_id = id
	data = p_data
	visible = not data.is_empty()
	if not data.is_empty():
		plate.corp_color = data.get("corp_color", Palette.CORP_MERIDIAN)
		plate.seal_letter = String(data.get("seal", "")) if String(data.get("seal", "")) != "" else plate.seal_letter
	_relayout()


func _s() -> float:
	return Settings.text_scale


func _rows() -> Array:
	var out: Array = []
	if data.is_empty():
		return out
	out.append([tr(F_TIER), "T%d" % int(data.get("tier", 1))])
	out.append([tr(F_TYPE), String(data.get("type", ""))])
	var rewards: Array = data.get("rewards", [])
	for i in rewards.size():
		out.append([tr(F_REWARDS) if i == 0 else "", String(rewards[i])])
	if String(data.get("heat", "")) != "":
		out.append([tr(F_HEAT), String(data["heat"])])
	return out


## The panel's width at the text size now (px).
func panel_width() -> float:
	return WIDTH * minf(_s(), MAX_WIDTH_SCALE)


## Parity ROUTE-03: the field rows as drawn, each value wrapped in its column (whole words,
## never cut): [[label, [lines]], ...] for a panel `w` wide.
func row_lines(w: float) -> Array:
	var s := _s()
	var m := MARGIN * s
	var fs := roundi(FIELD_FONT * s)
	var room := value_room(w)
	var out: Array = []
	for row in _rows():
		var lines := TilePicker.wrap_words(String(row[1]), Palette.body(), fs, room)
		out.append([String(row[0]), lines if not lines.is_empty() else PackedStringArray([""])])
	return out


## Parity ROUTE-03: the value column's width in a panel `w` wide (px).
func value_room(w: float) -> float:
	var m := MARGIN * _s()
	return w - m * 2.0 - (w - m * 2.0) * LABEL_SHARE


## Parity ROUTE-03: the foot's height (the DECRYPTED chip, px).
func foot_height() -> float:
	return chip_size().y


## Parity ROUTE-03: the DECRYPTED chip's size (px).
func chip_size() -> Vector2:
	var px := UiTheme.font_px(CHIP_STEP)
	var sz := Palette.mono().get_string_size(tr(STAMP_WORD), HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	return Vector2(sz.x, Palette.mono().get_height(px)) + CHIP_PAD * 2.0 * _s()


## Parity ROUTE-03: the DECRYPTED chip's rect (local): the foot's right corner.
func chip_rect() -> Rect2:
	var cs := chip_size()
	var m := MARGIN * _s()
	return Rect2(size - cs - Vector2(m, m * 0.5), cs)


## Parity ROUTE-03: where the fields end (local y): above the foot.
func fields_end() -> float:
	return size.y - foot_height() - MARGIN * _s() * 0.5


func _relayout() -> void:
	var s := _s()
	var f := Palette.body()
	var fs := roundi(FIELD_FONT * s)
	var tf := Palette.body_medium()
	var tfs := roundi(TITLE_FONT * s)
	var w := panel_width()
	var h := MARGIN * s + tf.get_height(tfs) + MARGIN * s * 0.5
	for row in row_lines(w):
		h += f.get_height(fs) * (row[1] as PackedStringArray).size()
	h += MARGIN * s * 0.5 + foot_height()
	custom_minimum_size = Vector2(w, h)
	update_minimum_size()
	queue_redraw()


func _draw() -> void:
	if data.is_empty():
		return
	var s := _s()
	var r := Rect2(Vector2.ZERO, size)
	var corp: Color = data.get("corp_color", Palette.CORP_MERIDIAN)
	var m := MARGIN * s
	var tf := Palette.body_medium()
	var tfs := roundi(TITLE_FONT * s)
	# Parity ROUTE-03: the title has the whole width (the stamp is a chip in the foot).
	var ty := m + tf.get_ascent(tfs)
	draw_string(tf, Vector2(m, ty), String(data.get("title", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - m * 2.0, tfs, corp.lerp(RouteInk.HOLO_TEXT, 0.35))
	var f := Palette.body()
	var mono := Palette.mono()
	var fs := roundi(FIELD_FONT * s)
	var y2 := ty + tf.get_descent(tfs) + m * 0.5
	var lw := (r.size.x - m * 2.0) * LABEL_SHARE
	for row in row_lines(r.size.x):
		var first := true
		for line: String in row[1]:
			y2 += f.get_ascent(fs)
			if first:
				draw_string(mono, Vector2(m, y2), String(row[0]), HORIZONTAL_ALIGNMENT_LEFT, lw, fs, RouteInk.HOLO_FIELD)
			draw_string(f, Vector2(m + lw, y2), line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, RouteInk.HOLO_TEXT)
			y2 += f.get_descent(fs)
			first = false
	# The DECRYPTED chip: a small keyline box in the foot's corner (round 37's holo).
	var chip := chip_rect()
	var px := UiTheme.font_px(CHIP_STEP)
	draw_rect(chip, Color(Palette.NIGHT_SKY, 0.6))
	draw_rect(chip, Palette.CELL_ACID, false, CHIP_LINE)
	draw_string(mono, chip.position + Vector2(CHIP_PAD.x * s, CHIP_PAD.y * s + mono.get_ascent(px)), tr(STAMP_WORD), HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.CELL_ACID)
