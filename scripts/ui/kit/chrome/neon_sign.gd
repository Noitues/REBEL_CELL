class_name NeonSign
extends Control
## ART-10 4C: the REBEL_CELL neon tube sign on its circuit board (ART_BIBLE v2 §4.13 title
## option A; round 33 `title_screen.jpg` / `.gif`): pink tube letters with a hot core and a
## glow, a lime underscore, on a dark board with traces, pads, screws and a rig label, hung
## on two wires. Idle (`title_sign_flicker`, one 48-frame loop): the underscore blinks as a
## cursor, one E stutters, and the sign drops to "CELL" for two frames. Under reduce effects,
## headless or with the entry off it holds fully lit (the end state). The sign is diegetic
## signage, so its words are the brand mark and are never translated. View only.

const MOTION := &"title_sign_flicker"
const WORD_A := "REBEL"
const WORD_B := "CELL"
## The board's size (px at 1280x720; a world object: it never scales with the text).
const BOARD := Vector2(624, 168)
## Tube lettering size and the tube's width (px).
const LETTER_PX := 118
const TUBE := 9.0
## Glow passes: (outline px, alpha).
const GLOWS: Array[Vector2] = [Vector2(40, 0.07), Vector2(26, 0.12), Vector2(16, 0.22)]
## The underscore bar (share of a cap's width / px tall), and the gap round it.
const BAR := Vector2(0.62, 12.0)
## Board details: corner radius-ish inset, frame width, screw radius, traces and pads.
const FRAME_W := 3.0
const SCREW_R := 5.0
const TRACES := 26
const PAD_R := 2.6
## The loop's frames and its moments (round 33 GIF: 48 x 80 ms).
const LOOP_FRAMES := 48.0
const STUTTER_LETTER := 1
const STUTTER_FRAMES: Array[int] = [14, 16, 17, 31]
const DROP_FRAMES: Array[int] = [36, 37]
const CURSOR_PERIOD := 12
## Frames of each cursor period the underscore is lit (a terminal cursor: on longer than off).
const CURSOR_ON := 8
## The tube's light on the board inside each letter (share of the tube colour).
const INNER_GLOW := 0.16
## A dead tube's alpha.
const DEAD_ALPHA := 0.16
const RIG_LABEL := "RC-03 // NEON RIG REV.B"

var _clock: float = 0.0
var _frame: int = -1


func _init() -> void:
	name = "NeonSign"
	custom_minimum_size = BOARD
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


func _process(delta: float) -> void:
	if not Motion.live(MOTION):
		if _frame != -1:
			_frame = -1
			queue_redraw()
		return
	var loop := maxf(0.1, Motion.seconds(MOTION))
	_clock = fmod(_clock + delta, loop)
	var f := int(_clock / loop * LOOP_FRAMES)
	if f != _frame:
		_frame = f
		queue_redraw()


## The frame of the idle loop shown now (-1: held fully lit).
func frame() -> int:
	return _frame


## How lit letter `i` of "REBEL_CELL" is at loop frame `f` (1 lit, else the dead alpha);
## index 5 is the underscore. Frame -1 = all lit.
static func lit_at(i: int, f: int) -> float:
	if f < 0:
		return 1.0
	if DROP_FRAMES.has(f) and i <= WORD_A.length():
		return DEAD_ALPHA
	if i == STUTTER_LETTER and STUTTER_FRAMES.has(f):
		return DEAD_ALPHA
	if i == WORD_A.length() and f % CURSOR_PERIOD >= CURSOR_ON:
		return DEAD_ALPHA
	return 1.0


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, BOARD)
	# The wires it hangs on.
	for x in [BOARD.x * 0.12, BOARD.x * 0.88]:
		draw_line(Vector2(x, -BOARD.y), Vector2(x, 2.0), Palette.BOARD_FRAME, 2.0)
	draw_rect(r.grow(2.0), Palette.GLYPH_INK)
	draw_rect(r, Palette.BOARD_BG)
	_draw_traces(r.grow(-FRAME_W * 3.0))
	draw_rect(r.grow(-FRAME_W * 0.5), Palette.BOARD_FRAME, false, FRAME_W)
	for c in [Vector2(14, 14), Vector2(BOARD.x - 14, 14), Vector2(14, BOARD.y - 14), Vector2(BOARD.x - 14, BOARD.y - 14)]:
		draw_circle(c, SCREW_R, Palette.BOARD_FRAME)
		draw_line(c - Vector2(SCREW_R * 0.7, 0), c + Vector2(SCREW_R * 0.7, 0), Palette.GLYPH_INK, 1.5)
	var cap_f := Palette.mono()
	var cap_px := Chrome.px(UiTheme.CAPTION)
	draw_string(cap_f, Vector2(28, BOARD.y - 10), RIG_LABEL, HORIZONTAL_ALIGNMENT_LEFT, -1, cap_px, Palette.TEXT_LO)
	_draw_tubes()


## The board's copper: horizontal runs with a 45-degree jog and a pad at each end, laid out
## by a fixed hash (no RNG: the same board every time).
func _draw_traces(area: Rect2) -> void:
	for i in TRACES:
		var h := hash(i * 7919 + 13)
		var y := area.position.y + float(h % 1000) / 1000.0 * area.size.y
		var x0 := area.position.x + float((h >> 10) % 1000) / 1000.0 * area.size.x * 0.7
		var run := area.size.x * (0.12 + float((h >> 20) % 100) / 100.0 * 0.3)
		var jog := (12.0 if (h >> 4) % 2 == 0 else -12.0)
		var mid := x0 + run * 0.5
		var pts := PackedVector2Array([Vector2(x0, y), Vector2(mid, y), Vector2(mid + absf(jog), clampf(y + jog, area.position.y, area.end.y)),
			Vector2(minf(x0 + run, area.end.x), clampf(y + jog, area.position.y, area.end.y))])
		draw_polyline(pts, Palette.BOARD_TRACE, 1.5)
		draw_circle(pts[0], PAD_R, Palette.BOARD_PAD)
		draw_circle(pts[pts.size() - 1], PAD_R, Palette.BOARD_PAD)


func _draw_tubes() -> void:
	var f := Chrome.sticker_font()
	var px := LETTER_PX
	var w_a := f.get_string_size(WORD_A, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var w_b := f.get_string_size(WORD_B, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var cap_w := f.get_string_size("E", HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var gap := cap_w * (BAR.x + 0.3)
	var total := w_a + gap + w_b
	var cap_h := px * VinylSticker.CAP_SHARE
	var base := Vector2((BOARD.x - total) * 0.5, (BOARD.y + cap_h) * 0.5 - 2.0)
	var letters: Array = []  # [char, x, index]
	var x := base.x
	for i in WORD_A.length():
		letters.append([WORD_A[i], x, i])
		x += f.get_string_size(WORD_A[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var bar_x := x + cap_w * 0.15
	x += gap
	for i in WORD_B.length():
		letters.append([WORD_B[i], x, WORD_A.length() + 1 + i])
		x += f.get_string_size(WORD_B[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	for l in letters:
		_draw_tube_letter(f, String(l[0]), Vector2(float(l[1]), base.y), px, lit_at(int(l[2]), _frame))
	var bar := Rect2(Vector2(bar_x, base.y - BAR.y), Vector2(cap_w * BAR.x, BAR.y))
	var on := lit_at(WORD_A.length(), _frame)
	if on >= 1.0:
		for g in GLOWS:
			draw_rect(bar.grow(g.x * 0.3), Color(Palette.CELL_ACID, g.y))
	draw_rect(bar, Color(Palette.CELL_ACID, on))
	draw_rect(bar.grow(-3.0), Color(Palette.NEON_CORE, on * 0.8))


## One tube letter: its glow, the pink tube (the outline round the glyph), the hot core
## line, and the board showing inside (the glyph filled with the board colour).
func _draw_tube_letter(f: Font, ch: String, at: Vector2, px: int, lit: float) -> void:
	if lit >= 1.0:
		for g in GLOWS:
			draw_string_outline(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(g.x + TUBE), Color(Palette.NEON_TUBE, g.y))
	draw_string_outline(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(TUBE * 2.0), Color(Palette.NEON_TUBE, lit))
	draw_string_outline(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(TUBE * 1.2), Color(Palette.NEON_CORE, lit * 0.85))
	draw_string_outline(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(TUBE * 0.5), Color(Palette.NEON_TUBE, lit))
	draw_string(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.BOARD_BG.lerp(Palette.NEON_TUBE, INNER_GLOW * lit))
