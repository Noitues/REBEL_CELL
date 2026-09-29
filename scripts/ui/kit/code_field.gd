class_name CodeField
extends HBoxContainer
## ART_BIBLE §6.5 text field (seeds, codes): a mono GLASS field with a copy button beside
## it, so a raw code never shows as body text (critique 18: the pause menu's code). The
## field is a themed LineEdit (focus brackets, the §6 states from UiTheme); the copy button
## is a Tertiary button with the COPY icon. `value` is the text; `text_changed` and
## `copied` are emitted; `read_only` shows a code to copy, not to type. A refused edit or
## copy flashes the refused state (RefusalMark). View only: the screen decides what a code
## does.

## The text changed (typed).
signal text_changed(value: String)
## The code went to the clipboard.
signal copied(value: String)
## A copy or an edit while disabled.
signal refused

## The field's least width in characters of the mono face (a seed or code fits).
const MIN_CHARS := 12

var field: LineEdit
var copy_button: Button

## The field's text.
var value: String:
	get:
		return field.text
	set(v):
		field.text = v
## A code to read and copy, not to type.
var read_only: bool = false:
	set(v):
		read_only = v
		field.editable = not v and not disabled
## Unavailable: no typing, no copying (both refused).
var disabled: bool = false:
	set(v):
		disabled = v
		field.editable = not v and not read_only
		copy_button.disabled = v


func _init(p_value: String = "", p_read_only: bool = false, copy_tip: String = "Copy") -> void: # TR
	add_theme_constant_override("separation", UiTheme.SP_XS)
	field = LineEdit.new()
	field.name = "Field"
	field.text = p_value
	field.add_theme_font_override(&"font", Palette.mono())
	field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	field.text_changed.connect(func(t: String) -> void: text_changed.emit(t))
	field.gui_input.connect(_field_input)
	add_child(field)
	copy_button = Button.new()
	copy_button.name = "Copy"
	copy_button.theme_type_variation = UiTheme.TERTIARY
	copy_button.tooltip_text = copy_tip
	copy_button.pressed.connect(copy)
	add_child(copy_button)
	IconMark.attach(copy_button, StatIcon.COPY)
	read_only = p_read_only


func _ready() -> void:
	field.custom_minimum_size.x = Palette.mono().get_string_size("0".repeat(MIN_CHARS), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x


func _field_input(event: InputEvent) -> void:
	if disabled and (event is InputEventKey and (event as InputEventKey).pressed or event is InputEventMouseButton and (event as InputEventMouseButton).pressed):
		refuse()


## Copies the code to the clipboard (refused while disabled or empty).
func copy() -> void:
	if disabled or field.text == "":
		refuse()
		return
	DisplayServer.clipboard_set(field.text)
	copied.emit(field.text)


## Shows the refused state (§6) on the field and emits `refused`.
func refuse() -> void:
	RefusalMark.flash(field)
	refused.emit()
