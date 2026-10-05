class_name UiWrap
extends RefCounted
## Keeps menu panels inside the fixed 1280-wide screen (H9/H12 width rule): long Labels and
## Buttons wrap instead of widening their panel. Views call fit() after a panel enters the tree.
## ART-0 F (ported from art-pass W8b / W9F, §4.3 rule 3): at word boundaries only, never mid-word.

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


## ART-0 F (ported from art-pass W9F; ART_BIBLE v1 §4.3 rule 3, kept by v2): wraps `l` at
## word boundaries only, never mid-word (AUTOWRAP_WORD; WORD_SMART split "BREAKE/R" at 2.0),
## and the label is never narrower than its longest word, so a word that can't fit grows the
## label (and its component) instead of breaking. Measured once the label is in the tree and
## again when its theme, text size or words change (never from its own size, so layout can't
## loop). A view that would rather shrink the text a step does so itself (it knows its room).
static func whole_words(l: Label) -> void:
	if l == null:
		return
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	if l.has_meta(WHOLE_WORDS_META):
		_fit_words.call_deferred(l)  # new words (a label reused)
		return
	l.set_meta(WHOLE_WORDS_META, [l.custom_minimum_size.x, -1.0])
	l.theme_changed.connect(_fit_words.bind(l), CONNECT_DEFERRED)
	l.ready.connect(_fit_words.bind(l), CONNECT_DEFERRED | CONNECT_ONE_SHOT)
	if l.is_inside_tree():
		_fit_words.call_deferred(l)


## The meta whole_words keeps on a label: [its own minimum width, the width whole_words last
## set] (px); a width the view sets later becomes its own.
const WHOLE_WORDS_META := &"whole_words_min"


## The width of the widest word of `text` in `font` at `px`.
static func longest_word_px(text: String, font: Font, px: int) -> float:
	var widest := 0.0
	if font == null:
		return widest
	for word in text.replace("\n", " ").split(" ", false):
		widest = maxf(widest, font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return widest


## The label's minimum width now: its own, or its longest word when that is wider.
## Untyped on purpose: a deferred call can land after the label was freed.
static func _fit_words(target) -> void:
	if not is_instance_valid(target) or not (target is Label) or not (target as Label).is_inside_tree():
		return
	var l := target as Label
	var m: Array = l.get_meta(WHOLE_WORDS_META, [0.0, -1.0])
	var own: float = m[0]
	if not is_equal_approx(l.custom_minimum_size.x, float(m[1])):
		own = l.custom_minimum_size.x  # the view set it since
	var need := ceilf(longest_word_px(l.text, l.get_theme_font(&"font"), l.get_theme_font_size(&"font_size")))
	var want := maxf(own, need)
	l.set_meta(WHOLE_WORDS_META, [own, want])
	if not is_equal_approx(l.custom_minimum_size.x, want):
		l.custom_minimum_size.x = want
