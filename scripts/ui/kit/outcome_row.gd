class_name OutcomeRow
extends Control
## What a Terminal event choice does, as icons with numbers (H21 #13: the outcome was in
## words only): each item is a StatIcon (the resource's own icon: coin for Cycles, flame
## for Heat, heart for HP, blueprint for Schematics, card / chip / daemon / crate /
## operative for what the choice gives) and a signed amount, green when it helps and red
## when it costs. `attach` puts the row under a choice button's words. `of_choice` reads
## the amounts from the choice's data the way NetrunSession applies them (Heat through
## HeatRules.scaled_delta). View only.

## Icon radius, gap after an icon and between items at text scale 1.0 (px).
const ICON_R := 8.0
const ICON_GAP := 3.0
const ITEM_GAP := 12.0
## Amount colours on the paper choice notes.
const GOOD := Color("#17702c")
const BAD := Color("#b3122f")

## [{kind: StringName, amount: int, text: String, good: bool, name: String}]
var items: Array[Dictionary] = []


func _init(p_items: Array[Dictionary] = []) -> void:
	name = "OutcomeRow"
	items = p_items
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## The outcome of `choice` for session `s`: costs first, then gains, then the reward.
static func of_choice(s: NetrunSession, choice: EventChoiceData) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if choice == null:
		return out
	if choice.cycle_cost > 0:
		out.append(_item(StatIcon.CYCLES, -choice.cycle_cost, false))
	var hp_loss := s.choice_hp_loss(choice)
	if hp_loss > 0:
		out.append(_item(StatIcon.HP, -hp_loss, false))
	for e in choice.effects:
		if e == null:
			continue
		match e.type:
			RC.EffectType.GAIN_CYCLES:
				if e.amount != 0:
					out.append(_item(StatIcon.CYCLES, e.amount, e.amount > 0))
			RC.EffectType.MODIFY_HEAT:
				var dh := HeatRules.scaled_delta(s.campaign, e.amount, s.config)
				out.append(_item(StatIcon.HEAT, dh, dh <= 0))
			RC.EffectType.HEAL:
				out.append(_item(StatIcon.HP, e.amount, true))
			RC.EffectType.GAIN_SCHEMATICS:
				out.append(_item(StatIcon.SCHEMATICS, e.amount, e.amount >= 0))
	if choice.reward != null:
		var kind := StatIcon.OPERATIVE
		if choice.reward is CardData:
			kind = StatIcon.CARDS
		elif choice.reward is FirmwareData:
			kind = StatIcon.FIRMWARE
		elif choice.reward is DaemonData:
			kind = StatIcon.DAEMON
		elif choice.reward is DefenseAssetData:
			kind = StatIcon.ARMORY
		var it := _item(kind, 1, true)
		it["name"] = TextDb.t(choice.reward, "display_name") if "display_name" in choice.reward else ""
		out.append(it)
	return out


static func _item(kind: StringName, amount: int, good: bool) -> Dictionary:
	return {"kind": kind, "amount": amount, "text": "%+d" % amount, "good": good, "name": ""}


## The row in words (a tooltip line): "Cycles -25, Heat +2, Card: Jam".
static func describe(p_items: Array[Dictionary]) -> String:
	var parts := PackedStringArray()
	for it in p_items:
		var what := String(StatIcon.NAMES.get(it["kind"], String(it["kind"])))
		parts.append(("%s: %s" % [what, it["name"]]) if String(it.get("name", "")) != "" else "%s %s" % [what, it["text"]])
	return ", ".join(parts)


## Puts `row` under the words of choice button `b`: the button's styles get room at the
## bottom (recomputed when the text size changes) and the row sits there.
static func attach(b: Button, row: OutcomeRow) -> void:
	b.add_child(row)
	row._fit_parent()


func _scale() -> float:
	return maxf(1.0, get_theme_font_size(&"font_size", &"Label") / float(UiTheme.BASE_SIZE))


func _font() -> Font:
	return get_theme_font(&"font", &"Label")


func _get_minimum_size() -> Vector2:
	var s := _scale()
	var fs := get_theme_font_size(&"font_size", &"Label")
	var w := 0.0
	for it in items:
		w += (ICON_R * 2.0 + ICON_GAP) * s + _font().get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + ITEM_GAP * s
	return Vector2(w, maxf(ICON_R * 2.0 * s, _font().get_height(fs)))


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		update_minimum_size()
		_fit_parent.call_deferred()
		queue_redraw()


## Room at the bottom of the parent button for the row; the row placed in it.
func _fit_parent() -> void:
	var b := get_parent() as Button
	if b == null or items.is_empty():
		return
	var h := get_combined_minimum_size().y
	var left := 0.0
	var bottom := 0.0
	for st in [&"normal", &"hover", &"pressed", &"hover_pressed", &"focus", &"disabled"]:
		b.remove_theme_stylebox_override(st)
		var sb := b.get_theme_stylebox(st)
		if sb == null:
			continue
		if st == &"normal":
			left = sb.get_margin(SIDE_LEFT)
			bottom = sb.get_margin(SIDE_BOTTOM)
		var room := sb.duplicate() as StyleBox
		room.content_margin_bottom = sb.get_margin(SIDE_BOTTOM) + h + 4.0
		b.add_theme_stylebox_override(st, room)
	set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	offset_left = left
	offset_right = -left
	offset_bottom = -bottom
	offset_top = -bottom - h


func _draw() -> void:
	var s := _scale()
	var fs := get_theme_font_size(&"font_size", &"Label")
	var font := _font()
	var x := 0.0
	var mid := size.y * 0.5
	for it in items:
		var col := GOOD if bool(it["good"]) else BAD
		StatIcon.draw(self, Vector2(x + ICON_R * s, mid), ICON_R * s, StringName(it["kind"]), Palette.INK)
		x += (ICON_R * 2.0 + ICON_GAP) * s
		var t := String(it["text"])
		draw_string(font, Vector2(x, mid + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.25), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		x += font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + ITEM_GAP * s
