class_name TurnQueuePanel
extends Control
## W2-A2: the queue readout between the wheels: what is played this turn (and the hovered play
## after it), the running net per wheel and the RAM. A terminal panel of mono rows
## {left, right, color}; `TurnQueue` and the scene decide what the rows say. View only.

const FONT := 12
const PAD := 8.0
const ROW_GAP := 3.0
## The widest the panel gets (px at text scale 1.0); the scene narrows it to the room it has.
const MAX_W := 300.0

var rows: Array[Dictionary] = []
## The width the scene gives it (px; 0 = fit the words, at most MAX_W scaled).
var room_w: float = 0.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false


## Shows `p_rows` (an empty list hides the panel).
func set_rows(p_rows: Array[Dictionary], p_room_w: float = 0.0) -> void:
	rows = p_rows.duplicate(true)
	room_w = p_room_w
	visible = not rows.is_empty()
	_fit()
	queue_redraw()


## The panel's lettering grows with the text size only up to this share (the room between the wheels
## does not grow with it: at 2.0 the words stay 1.4 times their size and give way with "...").
const SCALE_MAX := 1.4


static func _ts() -> float:
	return minf(Settings.text_scale, SCALE_MAX)


static func _fs() -> int:
	return roundi(FONT * _ts())


func _line_h() -> float:
	var f := HudSkin.mono()
	return f.get_height(_fs()) + ROW_GAP * _ts()


## The row's words fitted to `w` (the left words give way: they end in "..." before the right
## words are touched).
func fitted_left(row: Dictionary, w: float) -> String:
	var f := HudSkin.mono()
	var fs := _fs()
	var left := String(row.get("left", ""))
	var right_w := f.get_string_size(String(row.get("right", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var room := w - right_w - fs
	if f.get_string_size(left, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room:
		return left
	var cut := left
	while cut.length() > 1 and f.get_string_size(cut + "…", HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		cut = cut.left(cut.length() - 1)
	return cut + "…"


func _want_w() -> float:
	var f := HudSkin.mono()
	var fs := _fs()
	var w := 0.0
	for r in rows:
		w = maxf(w, f.get_string_size(String(r.get("left", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			+ f.get_string_size(String(r.get("right", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * 1.5)
	var cap := MAX_W * _ts()
	if room_w > 0.0:
		cap = minf(cap, room_w)
	return minf(w + PAD * 2.0 * _ts(), cap)


func _fit() -> void:
	var s := _ts()
	custom_minimum_size = Vector2(_want_w(), rows.size() * _line_h() + PAD * 2.0 * s)
	size = custom_minimum_size


func _draw() -> void:
	if rows.is_empty():
		return
	var s := _ts()
	var f := HudSkin.mono()
	var fs := _fs()
	draw_rect(Rect2(Vector2.ZERO, size), Color(HudSkin.CHIP_INK, 0.82))
	HudSkin.draw_terminal_edge(self, Rect2(Vector2.ZERO, size), HudSkin.TERMINAL_EDGE)
	var y := PAD * s
	for r in rows:
		var base := y + f.get_ascent(fs)
		var col: Color = r.get("color", HudSkin.TERMINAL_TEXT)
		HighContrast.draw_text(self, f, Vector2(PAD * s, base), fitted_left(r, size.x - PAD * 2.0 * s), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		var right := String(r.get("right", ""))
		if right != "":
			var rw := f.get_string_size(right, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			HighContrast.draw_text(self, f, Vector2(size.x - PAD * s - rw, base), right, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, r.get("right_color", col))
		y += _line_h()
