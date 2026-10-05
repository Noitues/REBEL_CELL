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
	return fold_to(text, maxi(24, roundi(COLUMNS / maxf(1.0, Settings.text_scale))))


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


## A tooltip body: an optional terminal header (the title in mono caps over a cyan rule,
## ART-2 2D, ART_BIBLE v2 §4.13), then the wrapped text in the body face (Plex), in the
## theme's tooltip size (the popup around it is the theme's TooltipPanel).
static func make(text: String, title: String = "") -> Control:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 2)
	if title != "":
		var head := Label.new()
		head.name = "TipHeader"
		head.theme_type_variation = &"TooltipLabel"
		head.text = "> " + title.to_upper()
		head.add_theme_font_override("font", HudSkin.mono())
		head.add_theme_color_override("font_color", HudSkin.TERMINAL_HI)
		box.add_child(head)
		var rule := ColorRect.new()
		rule.color = HudSkin.TERMINAL_EDGE
		rule.custom_minimum_size = Vector2(0, 1)
		box.add_child(rule)
	var body := Label.new()
	body.theme_type_variation = &"TooltipLabel"
	body.text = fold(text)
	body.add_theme_font_override("font", HudSkin.body())
	box.add_child(body)
	return box


# --- Input-aware words (ART-0 F, ported from art-pass W2 / W9F; ART_BIBLE v1 §6.8, §12) ------
## Mouse words a pad player never reads, lower case, whole words, and the pad words that
## stand in for them when a caller passes mouse wording by mistake.
const MOUSE_WORDS := {"click": "press", "clicks": "presses", "clicked": "pressed", "clicking": "pressing",
	"right-click": "press", "double-click": "press", "drag": "move", "drags": "moves", "dragged": "moved",
	"dragging": "moving", "hover": "focus", "hovering": "focusing"}


## The words for the device in use: `pad_text` while a pad is in use, else `mouse_text`. Pad
## players never read mouse wording: if `pad_text` still says "click" or "drag" (a caller's
## slip), those words are swapped for pad ones (and a debug warning).
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
	var out := ""
	var at := 0
	for m in _word_re().search_all(text):
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


static var _re: RegEx = null


static func _word_re() -> RegEx:
	if _re == null:
		_re = RegEx.create_from_string("[A-Za-z-]+")
	return _re


static func _words(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	for m in _word_re().search_all(text):
		out.append(m.get_string())
	return out
