class_name ZineNote
extends Control
## Torn-paper strip holding a RichTextLabel (STYLE_GUIDE 4: the log strip, notes,
## "THE PLAN" sidebar). Text uses the mono font on paper; the title is marker.

var title: String = ""
var label: RichTextLabel


func _init(p_title: String = "", min_size: Vector2 = Vector2(240, 120)) -> void:
	title = p_title
	custom_minimum_size = min_size
	label = RichTextLabel.new()
	label.bbcode_enabled = true
	label.scroll_following = true
	label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	label.offset_left = 10
	label.offset_top = 24 if p_title != "" else 8
	label.offset_right = -10
	label.offset_bottom = -8
	label.add_theme_color_override("default_color", Palette.INK)
	label.add_theme_font_override("normal_font", Palette.mono())
	add_child(label)


## Reference text (codex, stats, history): starts at the top, does not follow new lines,
## and takes focus so a pad or the keyboard can scroll it (up/down, page up/down).
func make_reference() -> ZineNote:
	label.scroll_following = false
	label.focus_mode = Control.FOCUS_ALL
	label.scroll_to_line.call_deferred(0)
	if not label.gui_input.is_connected(_on_reference_input):
		label.gui_input.connect(_on_reference_input)
	return self


## Up/down on a focused reference note scroll it by a quarter page, from any device (a
## RichTextLabel alone only scrolls on keyboard arrows); at the top or bottom edge the
## press moves focus to the neighbour instead, so the note never traps the player.
func _on_reference_input(event: InputEvent) -> void:
	var down := event.is_action_pressed("ui_down", true)
	var up := event.is_action_pressed("ui_up", true)
	if not (down or up):
		return
	var bar := label.get_v_scroll_bar()
	var at_edge := bar == null or not bar.visible or (down and bar.value >= bar.max_value - bar.page - 0.5) or (up and bar.value <= bar.min_value + 0.5)
	if at_edge:
		var next := label.find_valid_focus_neighbor(SIDE_BOTTOM if down else SIDE_TOP)
		if next != null:
			next.grab_focus()
	else:
		bar.value = clampf(bar.value + (1.0 if down else -1.0) * maxf(1.0, bar.page * 0.25), bar.min_value, bar.max_value - bar.page)
	label.accept_event()


func append(text: String) -> void:
	label.append_text(text + "\n")


func clear() -> void:
	label.clear()


func _draw() -> void:
	var pts := PackedVector2Array()
	var steps := 18
	for i in steps + 1:
		var x := size.x * i / steps
		pts.append(Vector2(x, 0 + float((i * 7) % 5)))
	for i in steps + 1:
		var x := size.x - size.x * i / steps
		pts.append(Vector2(x, size.y - float((i * 5) % 6)))
	draw_colored_polygon(pts, Palette.PAPER_ALT)
	draw_polyline(pts, Color(Palette.INK, 0.5), 1.0)
	if title != "":
		draw_string(Palette.marker(), Vector2(10, 18), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Palette.INK)
