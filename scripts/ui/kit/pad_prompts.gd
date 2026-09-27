class_name PadPrompts
extends HBoxContainer
## Button prompts for a pad player (H23 S11: the Modem, loot, raid setup, route and HQ
## showed none): "A  Buy   B  Leave   Menu  Settings" in a row of its own at the foot of the
## screen, so it covers no control. Each prompt names the pad button bound to its action
## (Settings.key_text) and is relabelled when the device or the binds change
## (Settings.hints_changed). Shown only while a pad is in use: mouse and keyboard players
## read the buttons' own words and key hints. View only; the screen sets the prompts.

## Gap between prompts at text scale 1.0 (px).
const GAP := 22.0

## [[action, verb], ...] in the order shown.
var prompts: Array = []


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


## The prompts' words as shown ("A Buy"), for tests; [] while hidden.
func texts() -> PackedStringArray:
	var out := PackedStringArray()
	if not visible:
		return out
	for child in get_children():
		if child is Label and not child.is_queued_for_deletion():
			out.append((child as Label).text)
	return out


func _relabel() -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()
	add_theme_constant_override("separation", roundi(GAP * Settings.text_scale))
	var any := false
	for p in prompts:
		var key := Settings.key_text(StringName(p[0]))
		if key == "":
			continue
		var l := Label.new()
		# H24 S4: the verb is the key, translated here once; "A  Buy" is no key, so the label
		# shows it as given.
		l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		l.text = "%s  %s" % [key, tr(String(p[1]))]
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		l.add_theme_color_override("font_color", Palette.CELL_ACID)
		add_child(l)
		any = true
	visible = any and Settings.pad_active
