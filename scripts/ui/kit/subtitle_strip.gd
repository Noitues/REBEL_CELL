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


## Art pass W8b (ART_BIBLE §5.2): one line at text scale 1.0 and up to BIG_LINES lines
## above it, so a line at big text pages whole sentences instead of a clipped half line
## (critique 1.6/08, 1.6/15). The subtitle text itself is Dialogue's (`body` x the scale).
const BIG_LINES := 2


## The most lines the band grows to above 1.0 on the page shown now (a map page that needs
## its height sets 1: a long line then pages whole, never clipped).
var big_lines: int = BIG_LINES


## The lines the band holds at text scale `s`: `lines` at 1.0, up to `big_lines` above.
func lines_at(s: float) -> int:
	return maxi(lines, big_lines) if s > 1.0 + 0.001 else lines


## Sets `big_lines` and refits the band.
func set_big_lines(n: int) -> void:
	if n == big_lines:
		return
	big_lines = maxi(1, n)
	if is_inside_tree():
		_fit()


## Height for `lines_at` lines at the text size in force.
func _fit() -> void:
	var h := Dialogue.band_height(lines_at(Settings.text_scale))
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
