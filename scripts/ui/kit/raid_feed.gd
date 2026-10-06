class_name RaidFeed
extends ZineNote
## ART-6 3A: the LIVE RAID FEED's lines as the Cell's terminal text (ART_BIBLE v2 §1.2: the
## Cell's systems are CRT terminals, never paper): the RaidPlayoutPanel's log, a ZineNote
## without its torn paper (the RaidTerminal round it is the glass), in the terminal face.
## Parity RAID-09: the feed follows its newest line with the top line whole (the label's own
## scroll followed the foot and left the first line cut in half at the top): the lines are laid
## out whole (fit_content) in a clipped view and slid up so the view starts on a line.

## The room at the lines' sides and under them (px; the top line starts at the view's top, so
## no sliver of the line above shows there).
const EDGE := 2


func _init(p_title: String = "", min_size: Vector2 = Vector2(240, 120)) -> void:
	super._init("", min_size)
	title = p_title
	name = "RaidFeed"
	paper_color = Palette.AUTO
	clip_contents = true
	label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	label.offset_left = EDGE
	label.offset_right = -EDGE
	label.offset_top = EDGE
	label.scroll_following = false
	label.scroll_active = false
	label.fit_content = true
	label.add_theme_color_override("default_color", Palette.TERMINAL_TEXT)
	label.add_theme_font_size_override("normal_font_size", UiTheme.font_px(UiTheme.CAPTION))
	resized.connect(follow_newest)
	label.mouse_filter = Control.MOUSE_FILTER_PASS
	gui_input.connect(_on_wheel)


func append(text: String) -> void:
	super.append(text)
	follow_newest()
	follow_newest.call_deferred()  # again once the label has its new height


func clear() -> void:
	super.clear()
	follow_newest()


## Parity RAID-09: slides the lines so the newest is in view and the view's top is the top of
## a line: the first feed line (paragraph) whose top is at or below (the lines' height - the view).
func follow_newest() -> void:
	label.position.y = -_newest_top()


## The wheel reads back up the feed a line at a time (and down to the newest); a new line
## brings the newest back into view.
func _on_wheel(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed or not (mb.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]):
		return
	var tops: Array[float] = []
	for i in label.get_line_count():
		tops.append(label.get_line_offset(i))
	if tops.is_empty():
		return
	var at := tops.bsearch(view_top() - 0.5)
	var newest := -_newest_top()
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		at = maxi(0, at - 1)
		label.position.y = -tops[at]
	else:
		label.position.y = maxf(newest, -tops[mini(tops.size() - 1, at + 1)])
	accept_event()


func _newest_top() -> float:
	var want := label.get_content_height() - (size.y - EDGE)
	var top := 0.0
	if want > 0.0:
		# A line of the feed's own (a paragraph), never the wrapped tail of one ("Hub.").
		for i in label.get_paragraph_count():
			top = label.get_paragraph_offset(i)
			if top >= want - 0.5:
				break
	return top


## The view's top (px into the lines; tests).
func view_top() -> float:
	return -label.position.y


func _draw() -> void:
	pass
