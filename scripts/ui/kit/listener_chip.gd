class_name ListenerChip
extends RefCounted
## Plan 2 N6 (acceptance 10, ruling Q19): the enemy listener chip. While a play (or the End
## Turn forecast) is previewed, an enemy whose listeners would fire shows one Badge under its
## enrage badge: "REACTS: N DMG" (the HP its listeners take from the operative in that
## preview) or "REACTS xN" (fires, when they deal no damage). Reads only the preview's events
## ("listener" and "damage"); no motion; view only.

## The chip node's name on the wheel view.
const NODE_NAME := "ListenerChip"
## Gap under the enrage badge's slot (px at text scale 1.0).
const GAP := 4.0


## What the chip of enemy `enemy_id` shows for preview `events`: {visible, fires, damage,
## triggers (names, in fire order)}. Pure.
static func state_for(events: Array, enemy_id: StringName) -> Dictionary:
	var keys := {}
	var fires := 0
	var triggers := PackedStringArray()
	var damage := 0
	for e in events:
		var t := String(e.get("type", ""))
		if t == "listener" and StringName(e.get("owner", &"")) == enemy_id:
			fires += 1
			keys[String(e.get("listener", ""))] = true
			triggers.append(String(RC.Trigger.keys()[int(e.get("trigger", 0))]))
		elif t == "damage" and StringName(e.get("attacker", &"")) == enemy_id and keys.has(String(e.get("source_id", ""))):
			damage += int(e.get("hp_damage", 0))
	return {"visible": fires > 0, "fires": fires, "damage": damage, "triggers": triggers}


## The chip's words.
static func label(state: Dictionary) -> String:
	if int(state.get("damage", 0)) > 0:
		return TranslationServer.translate("REACTS: %d DMG") % int(state["damage"])
	return TranslationServer.translate("REACTS x%d") % int(state.get("fires", 0))


## The chip's tooltip: what the enemy reacts to in this preview.
static func tooltip(state: Dictionary) -> String:
	var words := PackedStringArray()
	for t in state.get("triggers", PackedStringArray()):
		words.append(String(t).to_lower().replace("_", " "))
	return TranslationServer.translate("Reacts to your play: %s.") % ", ".join(words)


## Adds, updates or removes the chip on `view` for `state` (a state_for result).
static func sync(view: Control, state: Dictionary) -> void:
	var chip := view.get_node_or_null(NODE_NAME) as Badge
	if not bool(state.get("visible", false)):
		if chip != null:
			chip.queue_free()
		return
	if chip == null:
		chip = Badge.new()
		chip.name = NODE_NAME
		chip.glyph = "~"
		chip.color = Palette.PENCIL_THREAT
		chip.mouse_filter = Control.MOUSE_FILTER_PASS
		chip.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		view.add_child(chip)
	chip.text = label(state)
	chip.tooltip_text = UiTip.fold(tooltip(state))
	chip.update_minimum_size()
	chip.size = chip.get_combined_minimum_size()
	var inset := EnrageBuff.INSET * Settings.text_scale
	var top := inset
	var enrage := view.get_node_or_null(EnrageBuff.NODE_NAME) as Control
	if enrage != null:
		top = enrage.position.y + enrage.size.y + GAP * Settings.text_scale
	chip.position = Vector2(view.size.x - chip.size.x - inset, top)
	if view is WheelView:
		var corner := (view as WheelView).badge_corner()
		chip.position.x = minf(corner.x, view.size.x - chip.size.x - inset)
		if enrage == null:
			chip.position.y = maxf(inset, corner.y - chip.size.y)
	chip.queue_redraw()
