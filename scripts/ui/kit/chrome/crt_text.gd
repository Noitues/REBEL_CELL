class_name CrtText
extends CrtWindow
## ART-10 4C: a v2 terminal window holding reference text (the codex, stats, achievements,
## run history; ART_BIBLE v2 §1.2 "CRT terminal": the Cell's own systems; the zine note they
## used is a rejected medium). Prose in IBM Plex Sans Condensed (§2.9 body), headings in
## the terminal CAPS (`heading()`), keywords in Medium. It keeps ZineNote's reference API
## (`label`, `append`, `clear`, `make_reference`): up/down on the focused text scrolls it by
## a quarter page and moves on at either end, so a pad never gets trapped. View only.

var label: RichTextLabel


func _init(p_title: String = "", min_size: Vector2 = Vector2(240, 120), p_accent: Color = Palette.NET_CYAN) -> void:
	super(p_title, p_accent)
	hex = false
	label = RichTextLabel.new()
	label.name = "Text"
	label.bbcode_enabled = true
	label.scroll_following = false
	label.custom_minimum_size = Vector2(min_size.x, min_size.y * Settings.text_scale)
	label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	label.add_theme_font_override(&"normal_font", Chrome.body_font())
	label.add_theme_font_override(&"bold_font", Chrome.body_medium_font())
	label.add_theme_font_override(&"mono_font", Chrome.caps_font(UiTheme.LABEL))
	for key in [&"normal_font_size", &"bold_font_size"]:
		label.add_theme_font_size_override(key, Chrome.px(UiTheme.BODY))
	label.add_theme_font_size_override(&"mono_font_size", Chrome.px(UiTheme.LABEL))
	label.add_theme_color_override(&"default_color", Palette.TEXT_HI)
	label.add_theme_constant_override(&"line_separation", UiTheme.line_spacing_px(Chrome.body_font(), UiTheme.BODY, Chrome.px(UiTheme.BODY)))
	body.add_child(label)


## Reference text: starts at the top, takes focus so a pad or the keyboard can scroll it.
func make_reference() -> CrtText:
	label.focus_mode = Control.FOCUS_ALL
	label.scroll_to_line.call_deferred(0)
	if not label.gui_input.is_connected(_on_reference_input):
		label.gui_input.connect(_on_reference_input)
	return self


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


## A section heading line: terminal CAPS in the accent ("> SLICES").
func heading(text: String) -> void:
	label.append_text("[color=#%s][code]> %s[/code][/color]\n" % [accent.to_html(false), text.to_upper()])


func clear() -> void:
	label.clear()
