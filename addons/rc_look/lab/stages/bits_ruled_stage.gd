extends RcLookLabStage
## LOOK-TOOLBOX module 16: the ruled bits, old next to new. The designer's rulings (DIRECTION_REVIEW 2026-10-22): PAPER
## #F2EEE4 hot colour on every system, a NIGHT_SKY rim at 95 %, bursts that flip and tumble with a per-bit spin phase
## (the CPU fallback now matching the GPU), streams as a steady glyph with a trail copy, the turn staying 6.28.
## Three groups, each at three fixed clocks (shares of the last arrival), every panel split dark | light:
##   - burst on the GPU:         old "wheel" (today's GPU look) | new "burst"        DIFFERS: hot colour, outline
##   - burst on the CPU fallback: old "cpu"  (today's fallback)  | new "burst"        DIFFERS: hot colour, outline, spin phase
##   - stream:                   old "seam" (today's BitsSeam)  | new "stream"       UNCHANGED (the control)
## The rows that should differ carry an orange bar and the word DIFFERS; the control a grey bar. Lab only: nothing in the
## game uses the new presets. Run as `--module=bits_ruled`. View only.

const MARGIN := Vector2(190.0, 60.0)
const GAP := 6.0
const BLOCK_GAP := 22.0
const ROW_GAP := 36.0
const LABEL_SIZE := 13
## The first clock is in seconds, inside the hot phase (the first 0.08 s of a bit, where the hot colour shows); the others
## are shares of the last arrival.
const FIRST_CLOCK_S := 0.04
const CLOCK_SHARES: Array[float] = [0.0, 0.45, 0.8]
const BITS := 16
const GLYPH_PX := 22.0
const BAR_W := 6.0
const DIFFERS := Color(1.0, 0.55, 0.1)
const SAME := Color(0.5, 0.5, 0.5)

## The groups: title, what differs, the old and the new preset.
const GROUPS: Array[Dictionary] = [
	{"title": "burst, GPU", "note": "DIFFERS: hot colour WHITE -> PAPER; outline same-colour -> NIGHT_SKY rim", "old": &"wheel", "new": &"burst", "differs": true},
	{"title": "burst, CPU fallback", "note": "DIFFERS: hot colour, outline, and spin phase (now matches the GPU)", "old": &"cpu", "new": &"burst", "differs": true},
	{"title": "stream", "note": "UNCHANGED (control): PAPER, NIGHT_SKY rim, steady glyph + trail already", "old": &"seam", "new": &"stream", "differs": false},
]

var _views: Array[Control] = []


func _ready() -> void:
	var view := get_viewport_rect().size
	var blocks := CLOCK_SHARES.size()
	var block_w := (view.x - MARGIN.x - 30.0 - BLOCK_GAP * (blocks - 1)) / blocks
	var panel_w := (block_w - GAP) / 2.0
	var panel_h := (view.y - MARGIN.y - 30.0 - ROW_GAP * GROUPS.size()) / GROUPS.size()
	for g in GROUPS.size():
		var grp := GROUPS[g]
		var y := MARGIN.y + g * (panel_h + ROW_GAP)
		var bar := ColorRect.new()
		bar.color = DIFFERS if grp["differs"] else SAME
		bar.position = Vector2(MARGIN.x - 20.0 - BAR_W, y)
		bar.size = Vector2(BAR_W, panel_h)
		add_child(bar)
		_label(String(grp["title"]), Vector2(20.0, y), 15)
		_label("old: %s\nnew: %s" % [grp["old"], grp["new"]], Vector2(20.0, y + 24.0), 12)
		_label(String(grp["note"]), Vector2(MARGIN.x, y - LABEL_SIZE - 6.0), 12)
		for c in blocks:
			var x := MARGIN.x + c * (block_w + BLOCK_GAP)
			if g == 0:
				_label("t = %.2f s (the hot phase)" % FIRST_CLOCK_S if c == 0 else "t = %.0f %% of the last arrival" % (CLOCK_SHARES[c] * 100.0), Vector2(x, MARGIN.y - 2.0 * LABEL_SIZE - 10.0))
			for side in 2:
				var v := RcLookBitsView.new()
				v.position = Vector2(x + side * (panel_w + GAP), y)
				v.size = Vector2(panel_w, panel_h)
				v.preset = RcLookBits.preset(StringName(grp["old"] if side == 0 else grp["new"]))
				v.mode = &"flight"
				v.clock_s = FIRST_CLOCK_S if c == 0 else -1.0
				v.clock_share = CLOCK_SHARES[c]
				v.age_s = -1.0
				v.split = true
				v.bits = BITS
				v.glyph_px = GLYPH_PX
				add_child(v)
				_views.append(v)
				_label("old" if side == 0 else "NEW", Vector2(v.position.x, y + panel_h + 1.0), 11)


func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	for v in _views:
		v.queue_redraw()


func _label(text: String, at: Vector2, size: int = LABEL_SIZE) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", size)
	add_child(l)
