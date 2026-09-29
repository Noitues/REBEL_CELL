class_name LoadoutView
extends Control
## VIEW LOADOUT (top bar, a dossier's Loadout button): an operative's deck and spinner in
## one modal, switched by DECK / SPINNER tabs. The spinner shows the hub core and the inner
## ring too (H20). With more than one operative (`crew`) a NEXT OPERATIVE tab cycles
## through them and `operative_changed` tells the scene. Look-only; details on click.
## Modal for keys and the pad. Emits `closed`.
##
## Art pass W8b (ART_BIBLE §5.3, §10.2; critique 11-13, 57/58, gifs/10):
## - one size on both tabs (MODAL, centred, as tall as the room under the subtitle band
##   allows): the frame never jumps when the tab changes; a full-screen SCRIM (#02030A 55% +
##   6 px blur, `glass_blur`) sits behind it, so nothing of the page behind pokes out;
## - the spinner tab scales its wheel up to fill the frame; the deck tab's card grid fills
##   the frame's height;
## - the Rank 3 swap chips wrap at word boundaries (AUTOWRAP_WORD: "Accelera/tor" broke
##   mid-word) a step smaller when a name needs it;
## - a ring swap is seen: the swapped segment fills, recolours and pulses (RingSwapMark).

signal closed
signal operative_changed(operative_id: StringName)

## The modal's size at every text scale (px; its height shrinks to the room under the
## subtitle band), the least top, the bottom margin, the scrim's blur.
const MODAL := Vector2(920, 600)
const TOP_MIN := 50.0
const BOTTOM_MARGIN := 8.0
const GLASS_BLUR := "res://shaders/glass_blur.gdshader"
## The spinner's wheel area at scale 1 (SpinnerView's), how far it may scale, and the room
## kept round it (px).
const WHEEL_AREA := Vector2(670, 440)
const WHEEL_SCALE_MIN := 0.7
const WHEEL_SCALE_MAX := 1.3
const WHEEL_MARGIN := 24.0
## The least height the deck tab's card grid keeps (px; it scrolls inside).
const DECK_SCROLL_MIN := 160.0
## The swap chips' type steps: `label` (the note's own), one step smaller for a long name.
const CHIP_STEPS: Array[int] = [UiTheme.BODY, UiTheme.CAPTION]
## A swap chip's room beside its words (the note's padding and the pictogram, px).
const CHIP_PAD := 40.0

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
## The full-screen scrim behind the modal.
var scrim: ColorRect
## The wheel's scale on the spinner tab (1 on the deck tab; tests).
var wheel_scale: float = 1.0


func _init(p_op: OperativeState, p_lookup: ContentLookup, p_upgrades: Array[SliceData] = [], p_crew: Array[OperativeState] = []) -> void:
	op = p_op
	lookup = p_lookup
	upgrades = p_upgrades
	crew = p_crew
	name = "LoadoutView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	scrim = ColorRect.new()
	scrim.name = "Scrim"
	scrim.color = Palette.SCRIM
	scrim.mouse_filter = Control.MOUSE_FILTER_STOP
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var sh := load(GLASS_BLUR) as Shader
	if sh != null and not Settings.high_contrast:
		var mat := ShaderMaterial.new()
		mat.shader = sh
		mat.set_shader_parameter(&"blur_px", float(Palette.SCRIM_BLUR_PX))
		mat.set_shader_parameter(&"tint", Color(Palette.SCRIM, 1.0))
		mat.set_shader_parameter(&"tint_alpha", Palette.SCRIM.a)
		scrim.material = mat
	elif Settings.high_contrast:
		scrim.color = Color(HighContrast.BG, 1.0)  # §12: opaque behind a modal
	add_child(scrim)


func _init_drops() -> void:
	if drops == null:
		drops = DropLayer.new()
		add_child(drops)


func _ready() -> void:
	UiFocus.hold(self)
	_init_drops()
	if _view == null:
		show_deck()
	# W8a (§10): the modal fades and grows in (<= 0.22 s, never a cut) and counts as open.
	PageTransition.open_modal(self)


func show_deck() -> void:
	tab = "DECK"
	_swap(DeckView.new(op.deck, lookup, tr("LOADOUT // %s // DECK") % op.name.to_upper()))
	_add_tabs()


func show_spinner() -> void:
	tab = "SPINNER"
	var view := SpinnerView.new(op.slot_slice_ids, op.slot_firmware_ids, lookup, tr("LOADOUT // %s // SPINNER") % op.name.to_upper(), "", upgrades)
	_swap(view)
	var core := core_of(op, lookup)
	view.set_core(core["hub"], core["ring"])
	_add_tabs()
	_add_swaps(view, core["ring"])


## The modal's rect now (px): MODAL centred, from under the subtitle band to the foot.
func modal_rect() -> Rect2:
	var room := get_viewport_rect().size if is_inside_tree() else Vector2(1280, 720)
	var top := SubtitleStrip.top_below(TOP_MIN)
	var h := minf(MODAL.y, room.y - BOTTOM_MARGIN - top)
	return Rect2(Vector2(roundf((room.x - MODAL.x) * 0.5), top), Vector2(MODAL.x, h))


## Puts the tab's window in the one modal rect, hides its own dim (the scrim is ours) and
## fits its content: the wheel scaled to fill, the card grid as tall as the frame.
func _frame(view: Control) -> void:
	var w: TerminalWindow = view.get("window")
	if w == null:
		return
	for c in view.get_children():
		if c is ColorRect:
			(c as ColorRect).visible = false  # the modal's own scrim stands behind both tabs
			break
	var r := modal_rect()
	w.position = r.position
	# Measured with no size of its own: what the content needs besides the fitted part.
	w.custom_minimum_size = Vector2.ZERO
	if view is SpinnerView:
		_fit_wheel(view as SpinnerView, r)
	else:
		_fit_deck(w, r)
	w.custom_minimum_size = r.size
	w.size = Vector2(r.size.x, maxf(r.size.y, w.get_combined_minimum_size().y))


## The wheel area scaled to fill the frame's room (kept inside WHEEL_SCALE_MIN..MAX).
func _fit_wheel(view: SpinnerView, r: Rect2) -> void:
	var pad := view.slot_pad(0)
	if pad == null:
		return
	var wheel := pad.get_parent() as Control
	var holder := wheel.get_parent() as Control
	if not (holder is Control) or holder.name != &"WheelFit":
		var box := wheel.get_parent()
		var at := wheel.get_index()
		box.remove_child(wheel)
		holder = Control.new()
		holder.name = "WheelFit"
		holder.mouse_filter = Control.MOUSE_FILTER_PASS
		box.add_child(holder)
		box.move_child(holder, at)
		holder.add_child(wheel)
	var chrome := view.window.get_combined_minimum_size().y - holder.custom_minimum_size.y
	var k := minf((r.size.x - WHEEL_MARGIN * 2.0) / WHEEL_AREA.x, (r.size.y - chrome - WHEEL_MARGIN) / WHEEL_AREA.y)
	wheel_scale = clampf(k, WHEEL_SCALE_MIN, WHEEL_SCALE_MAX)
	wheel.scale = Vector2.ONE * wheel_scale
	wheel.position = Vector2(maxf(0.0, (r.size.x - WHEEL_MARGIN - WHEEL_AREA.x * wheel_scale) * 0.5), 0.0)
	holder.custom_minimum_size = WHEEL_AREA * wheel_scale
	for chip in view.find_children("Swap_*", "Button", true, false):
		_size_chip(chip as Button)


## The deck's card grid grows to the frame's height (its columns already fill the width).
func _fit_deck(w: TerminalWindow, r: Rect2) -> void:
	wheel_scale = 1.0
	var scrolls := w.find_children("*", "ScrollContainer", true, false)
	if scrolls.is_empty():
		return
	var sc := scrolls[0] as ScrollContainer
	var chrome := w.get_combined_minimum_size().y - sc.custom_minimum_size.y
	sc.custom_minimum_size.y = maxf(DECK_SCROLL_MIN, r.size.y - chrome)


## ANIM-4: the Rank 3 ring segment swaps (GDD 6.4) as chips beside the wheel (the class
## default first): drag one onto an inner ring segment, or press it and pick the segment
## with the D-pad. Nothing here changes the operative: the drop goes up to the screen.
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
		# W8b (§4.3.3): whole words only; a name wider than the chip steps down one size.
		chip.autowrap_mode = TextServer.AUTOWRAP_WORD
		_size_chip(chip)
		chip.tooltip_text = UiTip.fold((Codex.describe(seg) + "\n" if seg != null else "") + tr("Rank 3 swap: drag it onto an inner ring segment of the wheel (or press it, then pick the segment)."))
		# ANIM-R3 A7: a ring pictogram on each chip (they were words only): the segment it
		# swaps in lit on a small ring, the class default with its hub lit.
		SegmentMark.attach(chip, seg == null)
		view.add_side(chip)
		drops.add_source(chip, {"kind": "segment", "op": op.id, "segment": id}, true)
	for k in ring.size():
		var pad := view.ring_pad(k)
		if pad != null:
			drops.add_target("ring:%d" % k, ["segment"], "ring", k, DropLayer.rect_of(pad))


## Sizes a swap chip for the wheel's scale: the chips sit in the scaled wheel area, so
## their type is set at the step's size divided by `wheel_scale` and reads on screen at
## that step, never under the caption floor (W8b lint, 1.6 and 2.0).
func _size_chip(chip: Button) -> void:
	var k := maxf(0.01, wheel_scale)
	var screen_px := chip_font_px(chip.text, SpinnerView.SIDE_W * k)
	var px := ceili(screen_px / k)
	chip.add_theme_font_size_override("font_size", px)
	# §4.3.3: a word that still doesn't fit grows the chip (never cut, never broken).
	chip.custom_minimum_size.x = maxf(SpinnerView.SIDE_W, longest_word(chip.text, px) + CHIP_PAD)


## The swap chip's font size for `text` in a chip `width` px wide: the first step whose
## longest word fits (§4.3.3: a word never breaks; the text shrinks a step instead).
static func chip_font_px(text: String, width: float) -> int:
	var f := Palette.marker()
	var px := UiTheme.font_px(CHIP_STEPS[CHIP_STEPS.size() - 1])
	for step in CHIP_STEPS:
		px = UiTheme.font_px(step)
		var fits := true
		for word in text.split(" ", false):
			if f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > width - CHIP_PAD:
				fits = false
		if fits:
			break
	return px


## The widest word of `text` in the chips' marker at `px` (px).
static func longest_word(text: String, px: int) -> float:
	var w := 0.0
	for word in text.split(" ", false):
		w = maxf(w, Palette.marker().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return w


## Focus on inner ring segment `k`'s pad (after a swap dropped there), and (W8b §10.2)
## the swapped segment fills, recolours and pulses.
func focus_ring(k: int) -> void:
	var view := _view as SpinnerView
	var pad := view.ring_pad(k) if view != null else null
	if pad != null:
		pad.grab_focus.call_deferred()
		RingSwapMark.play_on(view, k)


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


func _swap(view: Control) -> void:
	if _view != null and is_instance_valid(_view):
		_view.closed.disconnect(_on_closed)
		_view.queue_free()
	_view = view
	_view.closed.connect(_on_closed)
	add_child(_view)
	_frame(_view)
	_frame.call_deferred(_view)  # again once its content is laid out
	# ANIM-4: the drop layer stays over the view; the old view's targets go with it.
	if drops != null:
		drops.reset()
		move_child(drops, -1)


func _on_closed() -> void:
	closed.emit()
	# W8a (§10): it fades out (never a cut), then frees itself.
	PageTransition.close_modal(self)
