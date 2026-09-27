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


func _init(p_op: OperativeState, p_lookup: ContentLookup, p_upgrades: Array[SliceData] = [], p_crew: Array[OperativeState] = []) -> void:
	op = p_op
	lookup = p_lookup
	upgrades = p_upgrades
	crew = p_crew
	name = "LoadoutView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	UiFocus.hold(self)
	show_deck()


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


func _on_closed() -> void:
	closed.emit()
	UiFocus.release(self)
