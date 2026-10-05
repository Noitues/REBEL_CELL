class_name ConfirmDialog
extends Control
## A confirm: a question, the safe answer and the committing verb. Emits confirmed or
## cancelled and frees itself. Used for quitting and deleting saves.
## ART-0 F (ported from art-pass W8a, ART_BIBLE v1 §10 / v2 SCRIM): it is a modal: a
## GlassScrim backdrop behind it takes the clicks meant for the page, it opens and closes
## with PageTransition's modal motion (`open_modal` / `close_modal`), and a page change
## waits for it to close (`PageTransition.after_modals`).
## ART-10 4C (ART_BIBLE v2 §4.13 "Abandon dialog", §2.10 two-sticker choice; round 33
## `abandon_dialog.jpg`): a v2 terminal in HARM red (`> CONFIRM // WHAT`, a CANNOT UNDO chip
## when it destroys something), the question in Plex, its cost under it, then two vinyl
## stickers: yellow CANCEL (the safe choice, default focus) and the pink verb, each with a
## terminal caption. B / Esc cancels at once.

signal confirmed
signal cancelled

## The stickers' lettering size (px at 1.0) and their tilts.
const STICKER_PX := 34.0
const TILT_NO := -2.0
const TILT_YES := 2.0
## The dialog's least width (px at text scale 1.0) and the question's.
const WIDTH := 520.0
const QUESTION_W := 470.0
## Space between the two choices (px).
const CHOICE_GAP := 70
## The default answers (keys).
const ANSWERS := ["Yes", "Cancel", "CONFIRM", "CANNOT UNDO", "keep going [B]", "confirm"] # TR

var yes_button: VinylSticker
var no_button: VinylSticker
var window: CrtWindow


## `question` and `detail` come translated (H24 S4: the dialog shows its words as given);
## the answers and `what` are keys, translated here. `destructive` adds the CANNOT UNDO chip.
func _init(question: String, yes_text: String = "Yes", no_text: String = "Cancel", what: String = "", detail: String = "", destructive: bool = false) -> void:
	TextDb.shown_as_given(self)
	var title := tr("CONFIRM")
	if what != "":
		title += " // " + tr(what)
	window = CrtWindow.new(title, Palette.HARM)
	window.name = "ConfirmWindow"
	window.hex = false
	if destructive:
		window.tag_label.text = tr("CANNOT UNDO")
	add_child(window)
	var box := window.body
	box.add_theme_constant_override("separation", 8)
	var l := Label.new()
	l.name = "Question"
	l.text = question
	l.add_theme_font_override(&"font", Chrome.body_medium_font())
	l.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.TITLE))
	l.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	l.custom_minimum_size = Vector2(QUESTION_W, 0)
	box.add_child(l)
	if detail != "":
		var d := Chrome.body_label(detail, UiTheme.LABEL, Palette.TEXT_MID)
		d.name = "Detail"
		d.custom_minimum_size = Vector2(QUESTION_W, 0)
		box.add_child(d)
	var rule := ColorRect.new()
	rule.color = Color(Palette.HARM, 0.35)
	rule.custom_minimum_size = Vector2(0, 1)
	box.add_child(rule)
	var row := HBoxContainer.new()
	row.name = "Choices"
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", CHOICE_GAP)
	box.add_child(row)
	no_button = VinylSticker.new(tr(no_text).to_upper(), VinylSticker.Fill.YELLOW, STICKER_PX, TILT_NO)
	no_button.pre_translated = true
	no_button.name = "No"
	no_button.pressed.connect(func() -> void: cancelled.emit(); _close())
	row.add_child(_choice(no_button, tr("keep going [B]")))
	yes_button = VinylSticker.new(tr(yes_text).to_upper(), VinylSticker.Fill.PINK, STICKER_PX, TILT_YES)
	yes_button.pre_translated = true
	yes_button.name = "Yes"
	yes_button.pressed.connect(func() -> void: confirmed.emit(); _close())
	row.add_child(_choice(yes_button, tr(what).to_lower() if what != "" else tr("confirm")))
	custom_minimum_size = Vector2(WIDTH, 0)
	window.minimum_size_changed.connect(_fit)
	_fit()


## A sticker over its terminal caption.
func _choice(sticker: VinylSticker, caption: String) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 2)
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	sticker.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	col.add_child(sticker)
	var c := Chrome.caps_label(caption, UiTheme.CAPTION, Palette.TEXT_MID if sticker == no_button else Palette.HARM)
	c.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(c)
	return col


func _fit() -> void:
	var m := window.get_combined_minimum_size()
	custom_minimum_size = Vector2(maxf(WIDTH, m.x), m.y)
	size = custom_minimum_size
	window.size = size


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
	PageTransition.enter(window, PageTransition.Look.GLASS)
	UiFocus.trap.call_deferred(self)  # the two choices, never out to the screen behind
	# Pad / keyboard: the safe answer takes focus (§2.10: yellow = default focus).
	if no_button != null:
		no_button.grab_focus.call_deferred()


func _notification(what: int) -> void:
	if what == NOTIFICATION_EXIT_TREE and _return_focus != null and is_instance_valid(_return_focus) 			and _return_focus.is_inside_tree() and not _return_focus.is_queued_for_deletion():
		_return_focus.grab_focus.call_deferred()
