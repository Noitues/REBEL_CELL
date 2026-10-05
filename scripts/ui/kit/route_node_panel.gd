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


func _relayout() -> void:
	var s := _s()
	var f := Palette.body()
	var fs := roundi(FIELD_FONT * s)
	var tf := Palette.body_medium()
	var tfs := roundi(TITLE_FONT * s)
	var h := maxf(MARGIN * s + tf.get_height(tfs), DecryptedHoloPanel.STAMP_SLOT.y) + MARGIN * s * 0.5
	h += f.get_height(fs) * _rows().size()
	h += DecryptedHoloPanel.SEAL_R + MARGIN * s
	custom_minimum_size = Vector2(WIDTH * minf(s, MAX_WIDTH_SCALE), h)
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
	# The plate's DECRYPTED stamp holds the top right; its seal the bottom right.
	var stamp_w := DecryptedHoloPanel.STAMP_SLOT.x
	var seal_w := DecryptedHoloPanel.SEAL_R * 2.0 + m
	var ty := m + tf.get_ascent(tfs)
	draw_string(tf, Vector2(m, ty), String(data.get("title", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, maxf(r.size.x - m * 2.0 - stamp_w, r.size.x * 0.4), tfs, corp.lerp(RouteInk.HOLO_TEXT, 0.35))
	var f := Palette.body()
	var mono := Palette.mono()
	var fs := roundi(FIELD_FONT * s)
	var y2 := maxf(ty + tf.get_descent(tfs), DecryptedHoloPanel.STAMP_SLOT.y) + m * 0.5
	var lw := (r.size.x - m * 2.0) * LABEL_SHARE
	for row in _rows():
		y2 += f.get_ascent(fs)
		draw_string(mono, Vector2(m, y2), String(row[0]), HORIZONTAL_ALIGNMENT_LEFT, lw, fs, RouteInk.HOLO_FIELD)
		draw_string(f, Vector2(m + lw, y2), String(row[1]), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - m * 2.0 - lw - seal_w * 0.5, fs, RouteInk.HOLO_TEXT)
		y2 += f.get_descent(fs)
