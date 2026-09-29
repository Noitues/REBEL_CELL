class_name PadPrompts
extends HBoxContainer
## Button prompts for a pad player (H23 S11, ART_BIBLE §5.2 "prompt bar", §12): each
## prompt is the pad button's drawn glyph (PadGlyph, in the player's glyph set) beside its
## verb, "(A) Buy  (B) Leave  (≡) Settings", never letters in brackets. A row of its own at
## the foot of the screen, so it covers no control. Each prompt names the pad button bound
## to its action and is rebuilt when the device, the binds or the glyph set change
## (Settings.hints_changed / changed). Shown only while a pad is in use: mouse and keyboard
## players read the buttons' own words and key hints. View only; the screen sets the
## prompts.

## Gap between prompts at text scale 1.0 (px), and between a glyph and its verb.
const GAP := 22.0
const GLYPH_GAP := 6.0

## [[action, verb], ...] in the order shown.
var prompts: Array = []
## Art pass W9F: a compact bar (a fight's status row): verbs at `caption` and the gaps kept
## at their 1.0 size, so the row fits beside the turn line at 2.0.
var compact: bool = false
## What each shown prompt says ("A  Buy": the glyph's name, two spaces, the verb), in order.
var _texts := PackedStringArray()


func _init() -> void:
	name = "PadPrompts"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	alignment = BoxContainer.ALIGNMENT_CENTER
	visible = false


func _ready() -> void:
	Settings.hints_changed.connect(_relabel)
	Settings.changed.connect(_relabel)


## Sets the screen's prompts: [[action, verb], ...] ([] hides the row).
func set_prompts(p_prompts: Array) -> void:
	prompts = p_prompts
	_relabel()


## The prompts as shown, each "glyph name  verb" ("A  Buy"), for tests; [] while hidden.
func texts() -> PackedStringArray:
	return _texts if visible else PackedStringArray()


## The glyphs shown, in order (tests).
func glyphs() -> Array[PadGlyph]:
	var out: Array[PadGlyph] = []
	for pair in get_children():
		for c in pair.get_children():
			if c is PadGlyph:
				out.append(c)
	return out


## One prompt: the glyph for pad button `button` and the verb `verb` (translated) beside it,
## as separate elements (W8: a price with a button beside it uses the glyph on its own).
static func make_pair(button: int, verb: String, p_compact: bool = false) -> HBoxContainer:
	var pair := HBoxContainer.new()
	pair.name = "Prompt"
	pair.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pair.add_theme_constant_override("separation", roundi(GLYPH_GAP * (1.0 if p_compact else Settings.text_scale)))
	var g := PadGlyph.new(button)
	g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pair.add_child(g)
	if verb == "":
		return pair  # art pass W9F: a glyph that says it all (the Menu glyph's three lines)
	var l := Label.new()
	l.name = "Verb"
	# H24 S4: the verb is the key, translated by the caller once; shown as given here.
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.text = verb
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_color_override("font_color", Palette.TEXT_HI)
	if p_compact:
		l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pair.add_child(l)
	return pair


func _relabel() -> void:
	# ANIM-R3 B12: freed at once (plain Controls, nothing waits on them). Removed and queued,
	# each relabel left its old nodes as orphans until the frame ended.
	for child in get_children():
		remove_child(child)
		child.free()
	_texts = PackedStringArray()
	add_theme_constant_override("separation", roundi(GAP * (1.0 if compact else Settings.text_scale)))
	var any := false
	for p in prompts:
		var action := StringName(p[0])
		var button := PadGlyph.button_for_action(action)
		if button < 0:
			continue  # no pad button for this action: no prompt
		var verb := tr(String(p[1]))
		add_child(make_pair(button, verb, compact))
		_texts.append("%s  %s" % [PadGlyph.name_of(button), verb])
		any = true
	var was := visible
	visible = any and Settings.pad_active
	# Animation pass ANIM-6: a new set of prompts fades in (`pad_prompts_in`); a relabel of
	# the same set does not.
	var sig := str(prompts) + str(visible)
	if visible and (sig != _shown_sig or not was):
		modulate.a = 0.0
		Motion.fade(self, 1.0, &"pad_prompts_in")
	_shown_sig = sig


## The prompt set last shown (a relabel of the same set does not fade).
var _shown_sig: String = ""
