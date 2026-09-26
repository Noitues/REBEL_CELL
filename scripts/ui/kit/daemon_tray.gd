class_name DaemonTray
extends Control
## The installed Daemons, opened from the top bar's DAEMONS icon: a row of unique sigils
## on a terminal strip under the bar. Hovering a sigil shows its card; clicking pins its
## detail. Click outside or Esc closes. View only.

signal closed

var ids: Array[StringName] = []
var lookup: ContentLookup
var _strip: PanelContainer
var _card: TerminalWindow = null
var _card_id: StringName = &""


func _init(p_ids: Array[StringName], p_lookup: ContentLookup, anchor_x: float) -> void:
	ids = p_ids
	lookup = p_lookup
	name = "DaemonTray"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_strip = PanelContainer.new()
	_strip.theme_type_variation = &"TerminalPanel"
	var w := maxf(200.0, ids.size() * 48.0 + 30.0)
	if anchor_x < 200.0:
		anchor_x = 1270.0  # the icon sits at the bar's right end
	_strip.position = Vector2(clampf(anchor_x - w, 10.0, 1270.0 - w), 60)
	add_child(_strip)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	_strip.add_child(row)
	if ids.is_empty():
		var none := Label.new()
		none.text = "No Daemons installed."
		row.add_child(none)
	for id in ids:
		var b := Button.new()
		b.flat = true
		b.name = "Daemon_" + String(id)
		b.custom_minimum_size = Vector2(40, 40)
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		var did := id
		b.draw.connect(func() -> void:
			var d := lookup.get_content(did) as DaemonData
			DaemonSigil.draw_sigil(b, b.size * 0.5, 17, did, d.rarity if d != null else RC.Rarity.UNCOMMON)
			if b.has_focus() or b.is_hovered():
				b.draw_arc(b.size * 0.5, 20, 0, TAU, 24, Palette.CELL_ACID, 1.5))
		b.mouse_entered.connect(func() -> void: show_card(did, false))
		b.focus_entered.connect(func() -> void: show_card(did, false))
		b.pressed.connect(func() -> void: show_card(did, true))
		row.add_child(b)


func _ready() -> void:
	UiFocus.focus_first.call_deferred(_strip)


## The Daemon's card under the strip (`pinned` from a click keeps it while hovering others).
func show_card(id: StringName, pinned: bool) -> void:
	if _card != null and is_instance_valid(_card):
		_card.queue_free()
	var d := lookup.get_content(id) as DaemonData
	_card_id = id
	_card = TerminalWindow.new("DAEMON" + (" // PINNED" if pinned else ""), DaemonSigil.color_of(id))
	_card.name = "DaemonCard"
	_card.custom_minimum_size.x = 320
	_card.position = Vector2(minf(_strip.position.x, 1270.0 - 340.0), _strip.position.y + 62)
	var head := Control.new()
	head.custom_minimum_size = Vector2(300, 56)
	head.draw.connect(func() -> void:
		DaemonSigil.draw_sigil(head, Vector2(28, 28), 24, id, d.rarity if d != null else RC.Rarity.UNCOMMON)
		head.draw_string(Palette.display(), Vector2(62, 36), (d.display_name if d != null else String(id)).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Palette.PAPER))
	_card.body.add_child(head)
	var desc := Label.new()
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc.custom_minimum_size.x = 300
	desc.text = Codex.describe(d) if d != null else String(id)
	_card.body.add_child(desc)
	add_child(_card)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		close()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()


func close() -> void:
	closed.emit()
	queue_free()
