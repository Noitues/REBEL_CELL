class_name ConfirmDialog
extends Control
## A zine confirm strip: a question, YES / NO. Emits confirmed or cancelled and frees
## itself. Used for quitting, deleting saves and abandoning campaigns.
## ART-0 F (ported from art-pass W8a, ART_BIBLE v1 §10 / v2 SCRIM): it is a modal: a
## GlassScrim backdrop behind it takes the clicks meant for the page, it opens and closes
## with PageTransition's modal motion (`open_modal` / `close_modal`), and a page change
## waits for it to close (`PageTransition.after_modals`).

signal confirmed
signal cancelled

var yes_button: Button
var no_button: Button


## `question` comes translated (H24 S4: the dialog shows its words as given); the answers
## are keys, translated here.
func _init(question: String, yes_text: String = "Yes", no_text: String = "No") -> void: # TR
	custom_minimum_size = Vector2(420, 120)
	TextDb.shown_as_given(self)
	var panel := ZinePanel.new(tr("ARE YOU SURE?"), 0.0, true)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var box := VBoxContainer.new()
	panel.content.add_child(box)
	var l := Label.new()
	l.text = question
	UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	l.custom_minimum_size = Vector2(380, 0)
	l.add_theme_color_override("font_color", Palette.TERMINAL_TEXT)
	box.add_child(l)
	var row := HBoxContainer.new()
	box.add_child(row)
	yes_button = Button.new()
	yes_button.text = tr(yes_text)
	yes_button.pressed.connect(func() -> void: confirmed.emit(); _close())
	row.add_child(yes_button)
	no_button = Button.new()
	no_button.text = tr(no_text)
	no_button.pressed.connect(func() -> void: cancelled.emit(); _close())
	row.add_child(no_button)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		cancelled.emit()
		get_viewport().set_input_as_handled()
		_close()


## Closes the dialog: through PageTransition.close_modal (it fades out, then frees) unless it
## is already closing (a page change closed it first).
func _close() -> void:
	if bool(get_meta(PageTransition.META_MODAL_CLOSING, false)) or is_queued_for_deletion():
		return
	if is_in_group(PageTransition.MODAL_GROUP):
		PageTransition.close_modal(self)
	else:
		queue_free()


## Who had focus before the dialog opened; it gets focus back when the dialog closes.
var _return_focus: Control = null


func _ready() -> void:
	_return_focus = UiFocus.owner_of(self)
	# ART-0 F: a modal over a SCRIM (the page behind blurred and dimmed; it takes the clicks
	# meant for the page), opened with the modal motion.
	GlassScrim.backdrop_for(self, get_viewport_rect().size)
	PageTransition.open_modal(self)
	# The question drops in (Animation pass ANIM-6); a press during the drop completes it.
	var glass := get_child(0) as Control
	if glass is ZinePanel:
		PageTransition.enter(glass, PageTransition.Look.PAPER)
	UiFocus.trap.call_deferred(self)  # Yes <-> No, and never out to the screen behind
	# Pad / keyboard: the safe answer takes focus.
	if no_button != null:
		no_button.grab_focus.call_deferred()


func _notification(what: int) -> void:
	if what == NOTIFICATION_EXIT_TREE and _return_focus != null and is_instance_valid(_return_focus) 			and _return_focus.is_inside_tree() and not _return_focus.is_queued_for_deletion():
		_return_focus.grab_focus.call_deferred()
