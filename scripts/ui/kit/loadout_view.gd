class_name LoadoutView
extends Control
## VIEW LOADOUT (top bar, a dossier's Loadout button): an operative's deck and spinner in
## one modal, switched by DECK / SPINNER tabs. The spinner shows the hub core and the inner
## ring too (H20). With more than one operative (`crew`) a NEXT OPERATIVE tab cycles
## through them and `operative_changed` tells the scene. Look-only; details on click.
## Modal for keys and the pad. Emits `closed`.

signal closed
signal operative_changed(operative_id: StringName)

var op: OperativeState
var lookup: ContentLookup
var upgrades: Array[SliceData] = []
## Operatives the NEXT OPERATIVE tab cycles through (empty = just `op`).
var crew: Array[OperativeState] = []
var tab: String = "DECK"
var _view: Control = null
## ANIM-4: drag and drop inside the view (the screen wires its check and its drops): at
## Rank 3 the ring segment swaps sit beside the wheel as chips to drag onto a segment.
var drops: DropLayer = null
## Plan 2 N12 (R11): the letter each precision tier shows in a slice's sub-tick map.
const QUALITY_LETTERS := {RC.PrecisionTier.WEAK: "W", RC.PrecisionTier.GOOD: "G", RC.PrecisionTier.PERFECT: "P"} # TR
## Sub-tick map cells (px at text 1.0): a tick's width and height, the gap, the slot-number column, the row's
## most width (a 30-tick slot shrinks its cells to fit), and the dim of an empty arc's row.
const MAP_CELL_W := 18.0
const MAP_CELL_H := 14.0
const MAP_CELL_GAP := 2.0
const MAP_NUM_W := 22.0
const MAP_ROW_W := 480.0
const MAP_EMPTY_ALPHA := 0.35


func _init(p_op: OperativeState, p_lookup: ContentLookup, p_upgrades: Array[SliceData] = [], p_crew: Array[OperativeState] = []) -> void:
	op = p_op
	lookup = p_lookup
	upgrades = p_upgrades
	crew = p_crew
	name = "LoadoutView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _init_drops() -> void:
	if drops == null:
		drops = DropLayer.new()
		add_child(drops)


func _ready() -> void:
	UiFocus.hold(self)
	_init_drops()
	show_deck()
	# ART-0 F (ported from art-pass W8a, §10): a modal: it opens with the modal motion and a
	# page change waits for it (PageTransition.after_modals). It closes at once (main's
	# UiFocus.release, so focus goes back the same frame).
	PageTransition.open_modal(self)


func show_deck() -> void:
	tab = "DECK"
	_swap(DeckView.new(op.deck, lookup, tr("LOADOUT // %s // DECK") % op.name.to_upper()))
	_add_tabs()


func show_spinner() -> void:
	tab = "SPINNER"
	var view := SpinnerView.new(op.slot_slice_ids, op.slot_firmware_ids, lookup, tr("LOADOUT // %s // SPINNER // %d SLICES") % [op.name.to_upper(), op.slot_slice_ids.size()], "", upgrades)
	# B5 (review section c: "the spinner tab should show the D4 wheel at r = 220 on a dimmed backdrop, not a mini
	# wheel"; round 44 `deck_viewer_spinner.png`): the combat's own wheel (WheelView), the slices as glyph rows.
	view.use_d4(display_combatant(op, lookup))
	_swap(view)
	var core := core_of(op, lookup)
	view.set_core(core["hub"], core["ring"])
	_add_tabs()
	_add_swaps(view, core["ring"])
	_add_subtick_map(view)


## Plan 2 N12 (R11): each slice's sub-tick map as a row of cells (one per tick, a letter on the tier's tag
## colour: PointerTag.tint, the disc's own WEAK / GOOD / PERFECT tags), led by the slot number, in the spinner's
## rows column. An empty arc gets a dim empty row. Read-only text from subtick_maps.
func _add_subtick_map(view: SpinnerView) -> void:
	var box := VBoxContainer.new()
	box.name = "SubtickMap"
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override(&"separation", UiTheme.SP_XS)
	var head := Label.new()
	head.text = tr("SUB-TICK MAP  //  W weak  G good  P perfect")
	head.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
	head.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	box.add_child(head)
	var maps := subtick_maps(op, lookup, RunManager.config())
	for i in maps.size():
		box.add_child(_map_row(i, maps[i].split(" ", false)))
	view.add_rows_section(box)


## One slot's map row: its number, then a cell per tick letter (a dim outline when the arc is empty).
func _map_row(slot: int, letters: PackedStringArray) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", int(MAP_CELL_GAP))
	var num := Label.new()
	num.text = str(slot + 1)
	num.custom_minimum_size.x = MAP_NUM_W
	num.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
	row.add_child(num)
	if letters.is_empty():
		row.modulate = Color(Palette.NO_TINT, MAP_EMPTY_ALPHA)
		var empty := PanelContainer.new()
		empty.custom_minimum_size = Vector2(MAP_CELL_W, MAP_CELL_H)
		row.add_child(empty)
		return row
	var w := minf(MAP_CELL_W, (MAP_ROW_W - MAP_NUM_W) / float(letters.size()) - MAP_CELL_GAP)
	for letter in letters:
		var cell := ColorRect.new()
		cell.custom_minimum_size = Vector2(w, MAP_CELL_H)
		cell.color = map_cell_color(letter)
		var l := Label.new()
		l.text = letter
		l.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.add_theme_color_override(&"font_color", Palette.INK)
		l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
		cell.add_child(l)
		row.add_child(cell)
	return row


## The cell colour for a tier letter: the colour of that tier's pointer tag on the disc.
static func map_cell_color(letter: String) -> Color:
	for tier in QUALITY_LETTERS:
		if TranslationServer.translate(QUALITY_LETTERS[tier]) == letter:
			return PointerTag.tint({"tier": tier, "is_null": false})
	return Palette.TEXT_MID


## Plan 2 N12 (R11): the operative's sub-tick maps as the fight reads them (the slot sizes,
## authored maps and Calibrated steps; EffectInterpreter.tick_tiers), one string per slot of
## space-separated tier letters ("W G P G W"; "" for an empty arc).
static func subtick_maps(p_op: OperativeState, p_lookup: ContentLookup, config: CampaignConfigData) -> PackedStringArray:
	var out := PackedStringArray()
	var c := display_combatant(p_op, p_lookup)
	if c.wheel == null:
		return out
	var fx := EffectInterpreter.new(config, p_lookup)
	for i in c.wheel.slot_slice_ids.size():
		var letters := PackedStringArray()
		for t in fx.tick_tiers(c.wheel, i):
			letters.append(TranslationServer.translate(QUALITY_LETTERS[t]))
		out.append(" ".join(letters))
	return out


## ANIM-4: the Rank 3 ring segment swaps (GDD 6.4) as chips beside the wheel (the class
## default first): drag one onto an inner ring segment, or press it and pick the segment
## with the D-pad. The dossier's segment lists stay the button path. Nothing here changes
## the operative: the drop goes up to the screen.
func _add_swaps(view: SpinnerView, ring: Array) -> void:
	var cls := lookup.get_content(op.class_id) as ClassData
	var options: Array[StringName] = []
	if cls != null:
		options = CampaignRules.ring_segment_options(op, cls)
	if options.is_empty() or drops == null:
		return
	var ids: Array[StringName] = [&""]
	ids.append_array(options)
	for id in ids:
		var seg := lookup.get_content(id) as RingSegmentData if id != &"" else null
		var chip := Button.new()
		chip.name = "Swap_%s" % (String(id) if id != &"" else "default")
		chip.theme_type_variation = &"NoteButton"
		chip.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		chip.text = TextDb.t(seg, "display_name") if seg != null else tr("Class default")
		chip.autowrap_mode = TextServer.AUTOWRAP_WORD
		chip.custom_minimum_size.x = SpinnerView.SIDE_W
		chip.tooltip_text = UiTip.fold((Codex.describe(seg) + "\n" if seg != null else "") + UiTip.for_input(tr("Rank 3 swap: drag it onto an inner ring segment of the wheel (or press it, then pick the segment)."),
			tr("Rank 3 swap: pick it up and move it onto an inner ring segment of the wheel (or press it, then pick the segment).")))
		# ANIM-R3 A7: a ring pictogram on each chip (they were words only): the segment it
		# swaps in lit on a small ring, the class default with its hub lit.
		SegmentMark.attach(chip, seg == null)
		view.add_side(chip)
		drops.add_source(chip, {"kind": "segment", "op": op.id, "segment": id}, true)
	for k in ring.size():
		var pad := view.ring_pad(k)
		if pad != null:
			drops.add_target("ring:%d" % k, ["segment"], "ring", k, DropLayer.rect_of(pad))


## Focus on inner ring segment `k`'s pad (after a swap dropped there).
func focus_ring(k: int) -> void:
	var view := _view as SpinnerView
	var pad := view.ring_pad(k) if view != null else null
	if pad != null:
		pad.grab_focus.call_deferred()


## Shows the next operative of `crew` on the same tab.
func next_operative() -> void:
	if crew.size() < 2:
		return
	var i := 0
	for k in crew.size():
		if crew[k].id == op.id:
			i = k
	op = crew[(i + 1) % crew.size()]
	operative_changed.emit(op.id)
	if tab == "SPINNER":
		show_spinner()
	else:
		show_deck()


func _add_tabs() -> void:
	_view.add_tab("DECK", show_deck, tab == "DECK") # TR
	_view.add_tab("SPINNER", show_spinner, tab == "SPINNER") # TR
	if crew.size() > 1:
		_view.add_tab("NEXT OPERATIVE >", next_operative) # TR


## The operative's hub core and inner ring segments as they fight (rank rewards and Rank 3
## segment swaps applied): {"hub": HubCoreData or null, "ring": Array[RingSegmentData]}.
static func core_of(p_op: OperativeState, p_lookup: ContentLookup) -> Dictionary:
	var ring: Array[RingSegmentData] = []
	var cls := p_lookup.get_content(p_op.class_id) as ClassData
	if cls == null or cls.starting_wheel == null:
		return {"hub": null, "ring": ring}
	var hub := cls.starting_wheel.hub
	var hub_id := p_op.hub_id(cls)
	if hub_id != &"":
		for reward in cls.rank_rewards:
			if reward != null and reward.hub_upgrade != null and reward.hub_upgrade.id == hub_id:
				hub = reward.hub_upgrade
	var inner := cls.starting_wheel.inner_ring
	var best := 0
	for reward in cls.rank_rewards:
		if reward != null and reward.inner_ring != null and reward.rank <= p_op.rank and reward.rank > best:
			best = reward.rank
			inner = reward.inner_ring
	if inner != null:
		for k in inner.segments.size():
			var seg := inner.segments[k]
			var swapped: StringName = p_op.ring_segment_ids[k] if k < p_op.ring_segment_ids.size() else &""
			if swapped != &"":
				var s := p_lookup.get_content(swapped) as RingSegmentData
				if s != null:
					seg = s
			ring.append(seg)
	return {"hub": hub, "ring": ring}


## B5: the operative's wheel as it fights (its slices, Firmware, hub core and inner ring with the Rank 3 swaps), as a
## display-only CombatantState for the combat's WheelView (no fight starts; nothing of the operative changes).
static func display_combatant(p_op: OperativeState, p_lookup: ContentLookup) -> CombatantState:
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	var cls := p_lookup.get_content(p_op.class_id) as ClassData
	if cls == null or cls.starting_wheel == null:
		return p
	p.source_id = cls.id
	p.display_name = cls.display_name
	p.max_hp = maxi(1, p_op.max_hp)
	p.hp = clampi(p_op.hp, 0, p.max_hp)
	var inner := cls.starting_wheel.inner_ring
	var best := 0
	for reward in cls.rank_rewards:
		if reward != null and reward.inner_ring != null and reward.rank <= p_op.rank and reward.rank > best:
			best = reward.rank
			inner = reward.inner_ring
	p.wheel = WheelState.from_wheel_data(cls.starting_wheel, inner, p_op.slot_slice_ids, p_op.slot_firmware_ids, p_op.ring_segment_ids)
	var hub_id := p_op.hub_id(cls)
	if hub_id != &"":
		p.wheel.hub_id = hub_id
	return p


func _swap(view: Control) -> void:
	if _view != null and is_instance_valid(_view):
		_view.closed.disconnect(_on_closed)
		_view.queue_free()
	_view = view
	_view.closed.connect(_on_closed)
	add_child(_view)
	# ANIM-4: the drop layer stays over the view; the old view's targets go with it.
	if drops != null:
		drops.reset()
		move_child(drops, -1)


func _on_closed() -> void:
	closed.emit()
	UiFocus.release(self)
