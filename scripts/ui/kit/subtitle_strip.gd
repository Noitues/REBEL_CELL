class_name SubtitleStrip
extends Control
## The subtitles' own band on a screen (H21 #11): an empty, click-through strip the screen
## lays out like any row (under the top bar on the HQ and netrun screens, beside the title
## on the main menu), so no control and no stat tag can sit under it. It sizes itself to
## `lines` subtitle lines at the current text size and hands its rect to
## Dialogue.set_default_rect; Dialogue.dock_default (and a fight's exit) put the bar there.
## Hidden (a fight docks its own subtitles) or freed, it gives the dock back. View only.

## Gap between the strip's ends and the bar (px).
const SIDE_GAP := 8.0

## Gap between the subtitle band and a modal window placed under it (px).
const MODAL_GAP := 6.0

var lines: int = 1


## The first y under the subtitle band in use, at least `min_y`: modal viewers (deck,
## spinner, Daemons) open there so a subtitle never covers their tabs.
static func top_below(min_y: float) -> float:
	return maxf(min_y, Dialogue.default_rect.end.y + MODAL_GAP)


func _init(p_lines: int = 1) -> void:
	name = "SubtitleStrip"
	lines = maxi(1, p_lines)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	size_flags_horizontal = Control.SIZE_EXPAND_FILL


func _ready() -> void:
	item_rect_changed.connect(_on_moved)  # moved (the top bar grew) or resized
	visibility_changed.connect(_register)
	Settings.changed.connect(_fit)
	_fit()
	_register.call_deferred()


## ANIM-R5 B2: a screen whose lines run long (an event's story, the run's end) gives its
## band `n` lines; the dock pages the line on screen again for them.
func set_lines(n: int) -> void:
	lines = maxi(1, n)
	_fit()


## Height for `lines` lines at the text size in force.
func _fit() -> void:
	var h := Dialogue.band_height(lines)
	if not is_equal_approx(custom_minimum_size.y, h):
		custom_minimum_size.y = h


## The rect the subtitle bar takes (screen coordinates).
func dock_rect() -> Rect2:
	var r := get_global_rect()
	return Rect2(r.position.x + SIDE_GAP, r.position.y, maxf(0.0, r.size.x - SIDE_GAP * 2.0), r.size.y)


## A strip that moved keeps the dock only if it holds it (H22: a screen left behind under
## a newer one, e.g. its header re-laid out, must not take the subtitles back).
func _on_moved() -> void:
	var holder := Dialogue.default_owner()
	if holder == null or holder == self:
		_register()


func _register() -> void:
	if not is_inside_tree():
		return
	if is_visible_in_tree():
		Dialogue.set_default_rect(dock_rect(), self)
	else:
		Dialogue.release_default_rect(self)


func _exit_tree() -> void:
	Dialogue.release_default_rect(self)
