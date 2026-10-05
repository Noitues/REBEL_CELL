class_name RouteNodePanel
extends Control
## ART-7 3B (ART_BIBLE v2 §4.6 panels, §1.2 decrypted holo; D14): the netrun node's file as
## hacked corp intel: the corp tint at about 78 % over a near-opaque scrim, 4 px scanlines, a
## +-2 px RGB split on the edge only, the corp seal cracked with a red fracture and the
## DECRYPTED stamp. It shows only tier, type and rewards (and what entering costs in Heat),
## and only for a decrypted node: under the current rules (GDD 4.2) every route node's kind
## is known, so every node shown on the map is decrypted (DECISIONS, ART-7 3B). View only:
## `show_node` takes the words the scene built from the rules.

## The panel at text scale 1.0 (px): width, margins, title lettering, field lettering, the
## field column's share, the seal's radius.
const WIDTH := 300.0
const MARGIN := 12.0
const TITLE_FONT := 18
const FIELD_FONT := 13
const LABEL_SHARE := 0.3
const SEAL_R := 13.0
## Scanlines (px apart, alpha), the edge's RGB split (px) and its alpha, the border's width.
const SCAN_STEP := 4.0
const SCAN_ALPHA := 0.12
const SPLIT := 2.0
const SPLIT_ALPHA := 0.45
const EDGE := 2.0
## The words (keys).
const F_TIER := "TIER" # TR
const F_TYPE := "TYPE" # TR
const F_REWARDS := "REWARDS" # TR
const F_HEAT := "HEAT" # TR
const DECRYPTED := "DECRYPTED" # TR

## What the panel shows: title, tier (int), type (words), rewards (Array[String]), heat
## (words, "" = none), corp_color.
var data: Dictionary = {}
## The node shown (&"" = none).
var node_id: StringName = &""


func _init() -> void:
	name = "RouteNodePanel"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	Settings.changed.connect(_relayout)
	resized.connect(queue_redraw)


## Shows node `id`'s file (`p_data`: see `data`); an empty dict hides it.
func show_node(id: StringName, p_data: Dictionary) -> void:
	node_id = id
	data = p_data
	visible = not data.is_empty()
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
	var h := MARGIN * s * 2.0 + tf.get_height(tfs) + MARGIN * s * 0.5
	h += f.get_height(fs) * _rows().size()
	h += Palette.mono().get_height(fs) + MARGIN * s
	custom_minimum_size = Vector2(WIDTH * s, h)
	update_minimum_size()
	queue_redraw()


func _draw() -> void:
	if data.is_empty():
		return
	var s := _s()
	var r := Rect2(Vector2.ZERO, size)
	var corp: Color = data.get("corp_color", Palette.CORP_MERIDIAN)
	draw_rect(r, Color(RouteInk.HOLO_SCRIM, RouteInk.HOLO_SCRIM_ALPHA))
	# The theme's HoloPanel plate in the corp's hue (1A); 1B's holo shader goes over it.
	draw_style_box(UiTheme.holo_box(corp), r)
	var y := 0.0
	while y < r.size.y:
		draw_rect(Rect2(0, y, r.size.x, 1.0), Color(RouteInk.HOLO_SCRIM, SCAN_ALPHA))
		y += SCAN_STEP * s
	# The edge: the corp hue, with a red / cyan split either side (the edge only).
	draw_rect(r.grow(-SPLIT * s), Color(RouteInk.HOLO_FRACTURE, SPLIT_ALPHA), false, EDGE * s * 0.5)
	draw_rect(r.grow(SPLIT * s * 0.5), Color(Palette.NET_CYAN, SPLIT_ALPHA), false, EDGE * s * 0.5)
	var m := MARGIN * s
	var tf := Palette.body_medium()
	var tfs := roundi(TITLE_FONT * s)
	var seal_r := SEAL_R * s
	var ty := m + tf.get_ascent(tfs)
	draw_string(tf, Vector2(m, ty), String(data.get("title", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - m * 3.0 - seal_r * 2.0, tfs, corp.lerp(RouteInk.HOLO_TEXT, 0.25))
	_seal(Vector2(r.size.x - m - seal_r, m + seal_r), seal_r, corp)
	var f := Palette.body()
	var mono := Palette.mono()
	var fs := roundi(FIELD_FONT * s)
	var y2 := ty + tf.get_descent(tfs) + m * 0.5
	var lw := (r.size.x - m * 2.0) * LABEL_SHARE
	for row in _rows():
		y2 += f.get_ascent(fs)
		draw_string(mono, Vector2(m, y2), String(row[0]), HORIZONTAL_ALIGNMENT_LEFT, lw, fs, RouteInk.HOLO_FIELD)
		draw_string(f, Vector2(m + lw, y2), String(row[1]), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - m * 2.0 - lw, fs, RouteInk.HOLO_TEXT)
		y2 += f.get_descent(fs)
	# DECRYPTED, bottom right, in a ruled terminal chip.
	var word := tr(DECRYPTED)
	var ww := mono.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var chip := Rect2(Vector2(r.size.x - m - ww - 8.0 * s, r.size.y - m * 0.6 - mono.get_height(fs) - 4.0 * s), Vector2(ww + 8.0 * s, mono.get_height(fs) + 4.0 * s))
	draw_rect(chip, Color(RouteInk.HOLO_SCRIM, RouteInk.HOLO_SCRIM_ALPHA))
	draw_rect(chip, RouteInk.HOLO_STAMP, false, s)
	draw_string(mono, Vector2(chip.position.x + 4.0 * s, chip.position.y + 2.0 * s + mono.get_ascent(fs)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, RouteInk.HOLO_STAMP)


## The corp seal, cracked: a ring in the corp hue with a red fracture through it.
func _seal(c: Vector2, rr: float, corp: Color) -> void:
	var s := _s()
	draw_arc(c, rr, 0, TAU, 28, corp, 2.0 * s)
	draw_arc(c, rr * 0.62, 0, TAU, 20, Color(corp, 0.6), 1.2 * s)
	var crack := PackedVector2Array([c + Vector2(-rr * 0.9, -rr * 0.5), c + Vector2(-rr * 0.2, -rr * 0.1), c + Vector2(-rr * 0.05, rr * 0.35),
		c + Vector2(rr * 0.45, rr * 0.2), c + Vector2(rr * 0.95, rr * 0.7)])
	draw_polyline(crack, RouteInk.HOLO_FRACTURE, 2.0 * s)
