class_name LoadoutView
extends Control
## VIEW LOADOUT (top bar): an operative's deck and spinner in one modal, switched by
## DECK / SPINNER tabs. Look-only; details on click. Emits `closed`.

signal closed

var op: OperativeState
var lookup: ContentLookup
var upgrades: Array[SliceData] = []
var _view: Control = null


func _init(p_op: OperativeState, p_lookup: ContentLookup, p_upgrades: Array[SliceData] = []) -> void:
	op = p_op
	lookup = p_lookup
	upgrades = p_upgrades
	name = "LoadoutView"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	show_deck()


func show_deck() -> void:
	_swap(DeckView.new(op.deck, lookup, "LOADOUT // %s // DECK" % op.name.to_upper()))
	_view.add_tab("DECK", show_deck, true)
	_view.add_tab("SPINNER", show_spinner)


func show_spinner() -> void:
	_swap(SpinnerView.new(op.slot_slice_ids, op.slot_firmware_ids, lookup, "LOADOUT // %s // SPINNER" % op.name.to_upper(), "", upgrades))
	_view.add_tab("DECK", show_deck)
	_view.add_tab("SPINNER", show_spinner, true)


func _swap(view: Control) -> void:
	if _view != null and is_instance_valid(_view):
		_view.closed.disconnect(_on_closed)
		_view.queue_free()
	_view = view
	_view.closed.connect(_on_closed)
	add_child(_view)


func _on_closed() -> void:
	closed.emit()
	queue_free()
