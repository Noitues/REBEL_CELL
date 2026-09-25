class_name ConfirmDialog
extends Control
## A zine confirm strip: a question, YES / NO. Emits confirmed or cancelled and frees
## itself. Used for quitting, deleting saves and abandoning campaigns.

signal confirmed
signal cancelled

var yes_button: Button
var no_button: Button


func _init(question: String, yes_text: String = "Yes", no_text: String = "No") -> void:
	custom_minimum_size = Vector2(420, 120)
	var panel := ZinePanel.new("ARE YOU SURE?", 0.0, true)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var box := VBoxContainer.new()
	panel.content.add_child(box)
	var l := Label.new()
	l.text = question
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(380, 0)
	l.add_theme_color_override("font_color", Palette.TERMINAL_TEXT)
	box.add_child(l)
	var row := HBoxContainer.new()
	box.add_child(row)
	yes_button = Button.new()
	yes_button.text = yes_text
	yes_button.pressed.connect(func() -> void: confirmed.emit(); queue_free())
	row.add_child(yes_button)
	no_button = Button.new()
	no_button.text = no_text
	no_button.pressed.connect(func() -> void: cancelled.emit(); queue_free())
	row.add_child(no_button)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		cancelled.emit()
		get_viewport().set_input_as_handled()
		queue_free()


## Who had focus before the dialog opened; it gets focus back when the dialog closes.
var _return_focus: Control = null


func _ready() -> void:
	_return_focus = UiFocus.owner_of(self)
	UiFocus.trap.call_deferred(self)  # Yes <-> No, and never out to the screen behind
	# Pad / keyboard: the safe answer takes focus.
	if no_button != null:
		no_button.grab_focus.call_deferred()


func _notification(what: int) -> void:
	if what == NOTIFICATION_EXIT_TREE and _return_focus != null and is_instance_valid(_return_focus) 			and _return_focus.is_inside_tree() and not _return_focus.is_queued_for_deletion():
		_return_focus.grab_focus.call_deferred()
