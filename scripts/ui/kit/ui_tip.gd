class_name UiTip
extends RefCounted
## Tooltips (H20, ART_BIBLE §6.8): Godot's tooltip is a TooltipPanel popup parented to the
## hovered control, so it takes the screen's theme (UiTheme: GLASS, a pink title rule,
## TEXT_HI mono). Its label never wraps, so words are broken into lines here: between
## MIN_COLUMNS (26) and COLUMNS (36) characters a line (§6.8, STYLE_GUIDE 5.5). A tip of at
## most MONO_LINES (3) lines is Share Tech Mono; longer text is set in the `BodyText` face
## (IBM Plex Sans Condensed, §4.1) at the same width. `make` builds the body for kit
## controls that draw their own tooltip (_make_custom_tooltip) and FocusTip; a title the
## body repeats is said once (critique 56: "TWIN POINTER / Daemon Twin Pointer").
## `for_input` picks the words for the device in use: pad players never read "click" or
## "drag" (§6.8, §12). UI helper only; no game state.

## §6.8: the widest a tooltip line runs (characters), and the narrowest a fold may make it.
const COLUMNS := 36
const MIN_COLUMNS := 26
## §4.1: a tip over this many lines of mono is set in the body face.
## The body face's "column": an average lower-case letter.
const COLUMN_SAMPLE := "n"
const MONO_LINES := 3
## Gap between a tip's title and its body (px).
const TITLE_GAP := 2
## Mouse words a pad player never reads (§6.8), lower case, whole words, and the pad words
## that stand in for them when a caller passes mouse wording by mistake.
const MOUSE_WORDS := {"click": "press", "clicks": "presses", "clicked": "pressed", "clicking": "pressing",
	"right-click": "press", "double-click": "press", "drag": "move", "drags": "moves", "dragged": "moved",
	"dragging": "moving", "hover": "focus", "hovering": "focusing"}


## `text` with line breaks so no line runs past COLUMNS characters (a longer word stays
## whole). Existing line breaks are kept.
static func fold(text: String) -> String:
	return fold_to(text, COLUMNS)


## `text` folded to at most `cols` characters a line (a longer word stays whole); existing
## line breaks are kept (ANIM-R2: FocusTip folds a tip narrower when it covers something).
static func fold_to(text: String, cols: int) -> String:
	if text == "":
		return ""
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


## `text` folded to lines no wider than `width` px in `font` at `px` (a longer word stays
## whole); existing line breaks are kept. The body face's fold (§6.8 width in px).
static func fold_px(text: String, font: Font, px: int, width: float) -> String:
	if text == "":
		return ""
	var out := PackedStringArray()
	for para in text.split("\n"):
		var line := ""
		for word in para.split(" ", false):
			var next := word if line == "" else line + " " + word
			if line != "" and font.get_string_size(next, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width:
				out.append(line)
				line = word
			else:
				line = next
		out.append(line)
	return "\n".join(out)


## True when `text` folded to `cols` runs over MONO_LINES lines (so it is set in the body face).
static func is_long(text: String, cols: int = COLUMNS) -> bool:
	return fold_to(text, cols).count("\n") + 1 > MONO_LINES


## `text` without a first line that only repeats `title` ("Daemon Twin Pointer" under the
## title "TWIN POINTER"): case-insensitive, the title at the line's end or the whole line.
static func without_title(text: String, title: String) -> String:
	var t := title.strip_edges().to_lower()
	if t == "" or text == "":
		return text
	var lines := text.split("\n")
	var first := lines[0].strip_edges().to_lower()
	if first == t or (first.ends_with(" " + t) and first.split(" ", false).size() <= t.split(" ", false).size() + 1):
		lines.remove_at(0)
		return "\n".join(lines).strip_edges()
	return text


## A tooltip body: an optional title line in pink, then the text folded to `cols` columns
## (mono up to MONO_LINES lines, else the body face at the same width), at `font_px` (0: the
## theme's tooltip size). The popup round it is the theme's TooltipPanel.
static func make(text: String, title: String = "", cols: int = COLUMNS, font_px: int = 0) -> Control:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", TITLE_GAP)
	var body_text := without_title(text, title)
	if title != "":
		var head := Label.new()
		head.theme_type_variation = &"TooltipLabel"
		head.text = title.to_upper()
		head.add_theme_color_override("font_color", Palette.CELL_PINK)
		if font_px > 0:
			head.add_theme_font_size_override(&"font_size", font_px)
		box.add_child(head)
	if body_text == "":
		return box
	var body := Label.new()
	cols = clampi(cols, MIN_COLUMNS, COLUMNS)
	var px := font_px if font_px > 0 else UiTheme.font_px(UiTheme.BODY)
	if is_long(body_text, cols):
		# §4.1: over 3 lines, the body face, `cols` of its own characters a line (an average
		# lower-case letter: the condensed face runs narrower than the mono columns).
		body.theme_type_variation = UiTheme.BODY_TEXT
		var width := Palette.body().get_string_size(COLUMN_SAMPLE.repeat(cols), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		body.text = fold_px(body_text, Palette.body(), px, width)
		body.add_theme_font_size_override(&"font_size", px)
	else:
		body.theme_type_variation = &"TooltipLabel"
		body.text = fold_to(body_text, cols)
		if font_px > 0:
			body.add_theme_font_size_override(&"font_size", font_px)
	box.add_child(body)
	return box


## §6.8 / §12: the words for the device in use: `pad_text` while a pad is in use, else
## `mouse_text`. Pad players never read mouse wording: if `pad_text` still says "click" or
## "drag" (a caller's slip), those words are swapped for pad ones (and a debug warning).
static func for_input(mouse_text: String, pad_text: String) -> String:
	if not Settings.pad_active:
		return mouse_text
	if has_mouse_words(pad_text):
		if OS.is_debug_build():
			push_warning("UiTip.for_input: pad text has mouse words: '%s'" % pad_text)
		return pad_safe(pad_text)
	return pad_text


## True when `text` says a mouse word ("click", "drag", ...), as a whole word.
static func has_mouse_words(text: String) -> bool:
	for w in _words(text):
		if MOUSE_WORDS.has(w.to_lower()):
			return true
	return false


## `text` with every mouse word swapped for its pad word (the first letter's case kept).
static func pad_safe(text: String) -> String:
	var re := RegEx.create_from_string("[A-Za-z-]+")
	var out := ""
	var at := 0
	for m in re.search_all(text):
		out += text.substr(at, m.get_start() - at)
		var w := m.get_string()
		var swap: String = MOUSE_WORDS.get(w.to_lower(), "")
		if swap == "":
			out += w
		elif w == w.to_upper() and w.length() > 1:
			out += swap.to_upper()
		elif w[0] == w[0].to_upper():
			out += swap.capitalize()
		else:
			out += swap
		at = m.get_end()
	return out + text.substr(at)


static func _words(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	for m in RegEx.create_from_string("[A-Za-z-]+").search_all(text):
		out.append(m.get_string())
	return out
