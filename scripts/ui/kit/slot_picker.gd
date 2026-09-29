class_name SlotPicker
extends TilePicker
## Art pass W8c (ART_BIBLE §6.5 picker, §2: never a native dropdown): the spinner's slots as
## a row of small GLASS tiles, one per slot: the slot's number, its slice's icon in the
## slice colour and its short name ("CRIT 12"), and a chip mark when a Firmware chip is
## socketed. Replaces the Modem's socket list and the Firmware loot's slot list
## (OptionButtons). TilePicker's behaviour (one focus stop, arrows / D-pad move a cursor,
## accept or a click chooses, the six §6 states) is kept; only the tiles' size and face
## differ. The tile under the pointer tells the slot's whole name (slot_name) as its tip.
## View only.

## A slot tile at text scale 1.0 (px): room for "CRIT 12" at caption and the icon.
const SLOT_W := 72.0
const SLOT_H := 52.0
## The slice icon's radius, the chip mark's radius (px at 1.0).
const SLICE_R := 11.0
const CHIP_R := 6.0


## `slots`: one per slot: {name: "1", meta: "CRIT 12", slice_type: int, firmware: bool,
## tip: "Slot 1: CRIT 12 + Barbed Wire"} (words translated by the caller).
func _init(slots: Array[Dictionary] = [], p_columns: int = 0) -> void:
	super(slots, p_columns)
	name = "SlotPicker"
	tooltip_text = " "  # _get_tooltip names the slot under the pointer
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


## The tiles for operative `op`'s slots (their words from NetrunScene.slot_name's parts).
static func tiles_for(op: OperativeState) -> Array[Dictionary]:
	var lookup := RunManager.lookup()
	var out: Array[Dictionary] = []
	for k in op.slot_slice_ids.size():
		var sd := lookup.get_content(op.slot_slice_ids[k]) as SliceData
		var meta := "?"
		var type := -1
		if sd != null:
			type = sd.slice_type
			meta = TranslationServer.translate(String(Palette.SLICE_NAMES.get(sd.slice_type, "?"))) + ((" %d" % sd.base_output) if sd.base_output > 0 else "")
		var fw: StringName = op.slot_firmware_ids[k] if k < op.slot_firmware_ids.size() else &""
		out.append({"name": str(k + 1), "meta": meta, "slice_type": type, "firmware": fw != &"", "tip": ""})
	return out


## Lays the tiles in as many columns as `width` (px) holds (at least one).
func fit_columns(width: float) -> SlotPicker:
	var w := _tile_size().x + TILE_GAP
	columns = maxi(1, floori((width + TILE_GAP) / w))
	return self


func _tile_size() -> Vector2:
	return Vector2(SLOT_W, SLOT_H) * Settings.text_scale


func _get_tooltip(at_position: Vector2) -> String:
	var i := tile_at(at_position)
	if i < 0:
		i = cursor
	return String(tiles[i].get("tip", "")) if i >= 0 and i < tiles.size() else ""


func _draw() -> void:
	var mono := Palette.mono()
	var num_px := UiTheme.font_px(UiTheme.LABEL)
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var s := Settings.text_scale
	for i in tiles.size():
		var t: Dictionary = tiles[i]
		var st := tile_state(i)
		var r := tile_rect(i)
		r.position.y += KitState.lift(st)
		var chosen := i == selected() and not is_locked(i)
		var fill := Palette.TERMINAL_BG_HOT if chosen and st != KitState.DISABLED else Palette.TERMINAL_BG
		if Settings.high_contrast:
			fill = HighContrast.BG  # §12: opaque panels
		KitState.draw_box(self, r, st, fill)
		if chosen and st != KitState.DISABLED:
			draw_rect(r, Palette.CELL_PINK, false, CHOSEN_EDGE)
		var ink := KitState.label_color(st)
		# The slot's number, top left.
		draw_string(mono, Vector2(r.position.x + PAD, r.position.y + PAD + mono.get_ascent(num_px)), String(t.get("name", "")),
			HORIZONTAL_ALIGNMENT_LEFT, -1, num_px, ink)
		# The slice's icon, top right, in its colour.
		var type := int(t.get("slice_type", -1))
		if type >= 0:
			var ic := Vector2(r.end.x - PAD - SLICE_R * s, r.position.y + PAD + SLICE_R * s)
			SliceIcon.draw_icon(self, ic, SLICE_R * s, type, Palette.slice_color(type) if st != KitState.DISABLED else ink)
		# Its short name along the foot.
		draw_string(mono, Vector2(r.position.x + PAD, r.end.y - PAD - mono.get_descent(meta_px)), String(t.get("meta", "")),
			HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD * 2.0, meta_px, Palette.TEXT_MID if st != KitState.FOCUS else Palette.FOCUS)
		if bool(t.get("firmware", false)):
			StatIcon.draw(self, Vector2(r.position.x + PAD + num_px * 1.1 + CHIP_R * s, r.position.y + PAD + CHIP_R * s), CHIP_R * s,
				StatIcon.FIRMWARE, StatIcon.color_of(StatIcon.FIRMWARE))
		KitState.draw_frame(self, r, st)
