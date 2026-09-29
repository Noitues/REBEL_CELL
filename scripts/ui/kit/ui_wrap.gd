class_name UiWrap
extends RefCounted
## Keeps menu panels inside the fixed 1280-wide screen (H9/H12 width rule): long Labels and
## Buttons wrap instead of widening their panel. Views call fit() after a panel enters the tree.
## Art pass W8b (ART_BIBLE §4.3 rule 3): at word boundaries only (AUTOWRAP_WORD), never mid-word.

## Widest a single Label or Button in a row may grow before it wraps.
const MAX_ITEM_WIDTH := 560.0


## Wraps every Label stacked in a vertical box, and any Label or Button in a row that is
## wider than MAX_ITEM_WIDTH (text scale included).
static func fit(root: Node) -> void:
	if root == null:
		return
	for n in root.find_children("*", "Label", true, false):
		var l := n as Label
		if l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			continue
		if l.get_parent() is VBoxContainer:
			l.autowrap_mode = TextServer.AUTOWRAP_WORD
			l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		elif l.get_minimum_size().x > MAX_ITEM_WIDTH:
			l.autowrap_mode = TextServer.AUTOWRAP_WORD
			l.custom_minimum_size.x = MAX_ITEM_WIDTH
	for n in root.find_children("*", "Button", true, false):
		var b := n as Button
		if b.autowrap_mode == TextServer.AUTOWRAP_OFF and b.get_minimum_size().x > MAX_ITEM_WIDTH:
			b.autowrap_mode = TextServer.AUTOWRAP_WORD
			b.custom_minimum_size.x = MAX_ITEM_WIDTH


## Art pass W9F (ART_BIBLE §4.3 rule 3): wraps `l` at word boundaries only, never mid-word
## (AUTOWRAP_WORD; WORD_SMART split "BREAKE/R" at 2.0). When its longest word is wider than
## the label, the text steps down one type step at a time (never under `caption` x text
## scale); if the word still doesn't fit at `caption`, the label (and its component) grows
## to hold it. Call once after building the label; it follows later resizes.
static func whole_words(l: Label) -> void:
	if l == null:
		return
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	if l.has_meta(WHOLE_WORDS_META):
		return
	l.set_meta(WHOLE_WORDS_META, -1)
	l.resized.connect(_fit_words.bind(l))
	l.ready.connect(_fit_words.bind(l), CONNECT_ONE_SHOT)


## The meta whole_words keeps on a label: the font size it was built with (-1 until read).
const WHOLE_WORDS_META := &"whole_words_px"


## The width of the widest word of `text` in `font` at `px`.
static func longest_word_px(text: String, font: Font, px: int) -> float:
	var widest := 0.0
	if font == null:
		return widest
	for word in text.replace("\n", " ").split(" ", false):
		widest = maxf(widest, font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return widest


static func _fit_words(l: Label) -> void:
	if not is_instance_valid(l) or not l.is_inside_tree() or l.size.x < 1.0:
		return
	var base: int = int(l.get_meta(WHOLE_WORDS_META, -1))
	if base < 0:
		base = l.get_theme_font_size(&"font_size")
		l.set_meta(WHOLE_WORDS_META, base)
	var font := l.get_theme_font(&"font")
	var floor_px := UiTheme.font_px(UiTheme.CAPTION)
	var px := base
	# Step down the scale (sizes are step x text scale) until the longest word fits.
	var steps: Array[int] = []
	for st in UiTheme.STEPS:
		var sp := UiTheme.font_px(st)
		if sp < base and sp >= floor_px:
			steps.append(sp)
	steps.reverse()
	var i := 0
	while longest_word_px(l.text, font, px) > l.size.x + 0.5 and i < steps.size():
		px = steps[i]
		i += 1
	if px != l.get_theme_font_size(&"font_size"):
		l.add_theme_font_size_override(&"font_size", px)
	var need := ceilf(longest_word_px(l.text, font, px))
	if need > l.size.x + 0.5 and need > l.custom_minimum_size.x:
		l.custom_minimum_size.x = need
