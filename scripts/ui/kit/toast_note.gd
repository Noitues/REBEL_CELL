class_name ToastNote
extends Toast
## A toast at the foot of a screen for what the player must see once (H20: the system log
## is an optional record, so refusals, saves and unlocks can't live only there). Kept for
## its callers' API (`show_on`, `label`, `whole`, NODE_NAME), it is now the one sticky toast
## (ART_BIBLE §6.7, art pass W2): a refusal (`warn`) leads with the no-entry mark, news with
## "i". One per screen (a new one replaces it); ignores the mouse and focus; it keeps off
## every usable control and the prompt bar (Toast.spot) and goes after Toast.hold_seconds
## (at least `toast_hold`, read raw: reduce effects and a raid's speed never shorten it).
## View only.

var _warn := false


func _init(p_text: String = "", warn: bool = false) -> void:
	super()
	_warn = warn
	label.text = p_text
	refusal = warn


## Shows `text` on `host` (a full-screen scene), replacing a note already there; `anchor`
## places it beside the control it refers to.
static func show_on(host: Control, text: String, warn: bool = false, anchor: Control = null) -> ToastNote:
	var t := ToastNote.new(text, warn)
	Toast.replace_on(host, t)
	t.present(text, warn, anchor)
	return t


## True when every line of the note's words shows (tests).
func whole() -> bool:
	return label.get_line_count() <= label.get_visible_line_count() and size.y + 0.5 >= label.get_combined_minimum_size().y
