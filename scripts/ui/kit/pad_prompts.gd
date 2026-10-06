class_name PadPrompts
extends HBoxContainer
## Button prompts for a pad player (H23 S11: the Mainframe, loot, raid setup, route and HQ
## showed none): "A  Buy   B  Leave   Menu  Settings" in a row of its own at the foot of the
## screen, so it covers no control. Each prompt names the pad button bound to its action
## (Settings.key_text) and is relabelled when the device or the binds change
## (Settings.hints_changed). Shown only while a pad is in use: mouse and keyboard players
## read the buttons' own words and key hints. View only; the screen sets the prompts.
## ART-0 F (ported from art-pass W2 / W9F, ART_BIBLE §12): each prompt is the pad button's
## drawn glyph (PadGlyph, in the player's glyph set) beside its verb, never letters in
## brackets; `texts()` still reads "A  Buy" (the glyph's name, two spaces, the verb).

## Gap between prompts at text scale 1.0 (px), and between a glyph and its verb.
const GAP := 22.0
const GLYPH_GAP := 6.0

## [[action, verb], ...] in the order shown.
var prompts: Array = []
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


## One prompt: the glyph for pad button `button` and the verb `verb` (translated by the
## caller) beside it, as separate elements.
static func make_pair(button: int, verb: String) -> HBoxContainer:
	var pair := HBoxContainer.new()
	pair.name = "Prompt"
	pair.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pair.add_theme_constant_override("separation", roundi(GLYPH_GAP * Settings.text_scale))
	var g := PadGlyph.new(button)
	g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pair.add_child(g)
	if verb == "":
		return pair
	var l := Label.new()
	l.name = "Verb"
	# H24 S4: the verb is the key, translated by the caller once; shown as given here.
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.text = verb
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_color_override("font_color", Palette.CELL_ACID)
	Chrome.keyline(l)  # B5 (B1a b Q2): prompts sit over the world: the ink keyline
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pair.add_child(l)
	return pair


func _relabel() -> void:
	# ANIM-R3 B12: freed at once (plain Labels, nothing waits on them). Removed and queued,
	# each relabel left its old Labels as orphans until the frame ended; a text size change
	# relabels twice (changed, hints_changed), so a screen torn down right after one leaked
	# them (6 per HQ page in test_anim_r2_city).
	for child in get_children():
		remove_child(child)
		child.free()
	_texts = PackedStringArray()
	add_theme_constant_override("separation", roundi(GAP * Settings.text_scale))
	var any := false
	for p in prompts:
		var button := PadGlyph.button_for_action(StringName(p[0]))
		if button < 0:
			continue  # no pad button for this action: no prompt
		# H24 S4: the verb is the key, translated here once (shown as given).
		var verb := tr(String(p[1]))
		add_child(make_pair(button, verb))
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
