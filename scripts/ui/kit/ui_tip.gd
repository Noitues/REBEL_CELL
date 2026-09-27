class_name UiTip
extends RefCounted
## Tooltips (H20): Godot's tooltip is a TooltipPanel popup parented to the hovered
## control, so it takes the screen's theme (UiTheme: terminal glass, pink edge, scaled
## mono text). Its label never wraps, so long descriptions are broken into lines here
## before they are set. `make` builds the same look for kit controls that draw their own
## tooltip (_make_custom_tooltip). UI helper only; no game state.

## Characters per tooltip line at text scale 1.0 (fewer at larger text).
const COLUMNS := 56


## `text` with line breaks so no line runs past COLUMNS / text scale characters. Existing
## line breaks are kept.
static func fold(text: String) -> String:
	if text == "":
		return ""
	var cols := maxi(24, roundi(COLUMNS / maxf(1.0, Settings.text_scale)))
	var out := PackedStringArray()
	for para in text.split("\n"):
		var line := ""
		for word in para.split(" ", false):
			if line != "" and line.length() + 1 + word.length() > cols:
				out.append(line)
				line = word
			else:
				line = word if line == "" else line + " " + word
		out.append(line)
	return "\n".join(out)


## A tooltip body: an optional title line in pink, then the wrapped text, in the theme's
## tooltip font (the popup around it is the theme's TooltipPanel).
static func make(text: String, title: String = "") -> Control:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 2)
	if title != "":
		var head := Label.new()
		head.theme_type_variation = &"TooltipLabel"
		head.text = title.to_upper()
		head.add_theme_color_override("font_color", Palette.CELL_PINK)
		box.add_child(head)
	var body := Label.new()
	body.theme_type_variation = &"TooltipLabel"
	body.text = fold(text)
	box.add_child(body)
	return box
