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
## The first block is the flash itself: every bit at the instant it spawns (0.01 s of its 0.08 s hot phase), so the hot
## colour shows at near full strength; the others
## are shares of the last arrival.
const FIRST_CLOCK_S := 0.01
const CLOCK_SHARES: Array[float] = [0.0, 0.45, 0.8]
const BITS := 16
const GLYPH_PX := 22.0
const BAR_W := 6.0
## The crop: its size in px and the magnification.
const CROP_PX := 32
const ZOOM := 4
## The squint row: its height (px), how far it is shown down from full size, the blur radius (px each way: a 1/8-scale box),
## the gap between its images.
const SQUINT_H := 140.0
const SQUINT_SHOW := 2.0
const SQUINT_BLUR := 4
const SQUINT_GAP := 30.0
const DIFFERS := Color(1.0, 0.55, 0.1)
const SAME := Color(0.5, 0.5, 0.5)

## The groups: title, what differs, the old and the new preset.
const GROUPS: Array[Dictionary] = [
	{"title": "burst, GPU", "note": "DIFFERS: hot colour WHITE -> PAPER; outline same-colour -> NIGHT_SKY rim", "old": &"wheel", "new": &"burst", "differs": true},
	{"title": "burst, CPU fallback", "note": "DIFFERS: hot colour, outline, and spin phase (now matches the GPU)", "old": &"cpu", "new": &"burst", "differs": true},
	{"title": "stream", "note": "UNCHANGED (control): PAPER, NIGHT_SKY rim, steady glyph + trail already", "old": &"seam", "new": &"stream", "differs": false},
]

var _views: Array[Control] = []
var _block_w: float = 0.0
var _panel_w: float = 0.0
var _panel_h: float = 0.0


func _ready() -> void:
	var view := get_viewport_rect().size
	var blocks := CLOCK_SHARES.size() + 1  # the clocks, then the magnified crops
	_block_w = (view.x - MARGIN.x - 30.0 - BLOCK_GAP * (blocks - 1)) / blocks
	_panel_w = (_block_w - GAP) / 2.0
	_panel_h = (view.y - MARGIN.y - SQUINT_H - 40.0 - ROW_GAP * GROUPS.size()) / GROUPS.size()
	for g in GROUPS.size():
		var grp := GROUPS[g]
		var y := MARGIN.y + g * (_panel_h + ROW_GAP)
		var bar := ColorRect.new()
		bar.color = DIFFERS if grp["differs"] else SAME
		bar.position = Vector2(MARGIN.x - 20.0 - BAR_W, y)
		bar.size = Vector2(BAR_W, _panel_h)
		add_child(bar)
		_label(String(grp["title"]), Vector2(20.0, y), 15)
		_label("old: %s\nnew: %s" % [grp["old"], grp["new"]], Vector2(20.0, y + 24.0), 12)
		_label(String(grp["note"]), Vector2(MARGIN.x, y - LABEL_SIZE - 6.0), 12)
		for c in blocks:
			var x := MARGIN.x + c * (_block_w + BLOCK_GAP)
			if g == 0:
				_label("every bit at t = %.2f s (the hot flash)" % FIRST_CLOCK_S if c == 0 else "4x nearest crop of one bit, on light" if c == 3
						else "t = %.0f %% of the last arrival" % (CLOCK_SHARES[c] * 100.0), Vector2(x, MARGIN.y - 2.0 * LABEL_SIZE - 10.0))
			if c == blocks - 1:
				_zoom_pair(grp, Vector2(x, y))
			else:
				_clock_panels(self, grp, c, Vector2(x, y), true)
	_squint_row(view)


func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	for v in _views:
		v.queue_redraw()


## The two panels (old | new) of group `grp` at clock block `c`, in `parent` at `at`.
func _clock_panels(parent: Node, grp: Dictionary, c: int, at: Vector2, labels: bool) -> void:
	for side in 2:
		var v := RcLookBitsView.new()
		v.position = at + Vector2(side * (_panel_w + GAP), 0.0)
		v.size = Vector2(_panel_w, _panel_h)
		v.preset = RcLookBits.preset(StringName(grp["old"] if side == 0 else grp["new"]))
		v.mode = &"grid" if c == 0 else &"flight"
		v.clock_s = FIRST_CLOCK_S if c == 0 else -1.0
		v.clock_share = CLOCK_SHARES[c]
		v.age_s = FIRST_CLOCK_S if c == 0 else -1.0
		v.split = true
		v.bits = BITS
		v.glyph_px = GLYPH_PX
		parent.add_child(v)
		_views.append(v)
		if labels:
			_label("old" if side == 0 else "NEW", Vector2(v.position.x, at.y + _panel_h + 1.0), 11)


## The squint row: per group, the flash and 45 % panels (old | new) drawn at full size in a viewport, box-blurred SQUINT_BLUR
## px each way (what a 1/8-scale view loses), and shown at 1/2 size.
func _squint_row(view: Vector2) -> void:
	var y := view.y - SQUINT_H - 24.0
	var src := Vector2(_block_w * 2.0 + BLOCK_GAP, _panel_h)
	var shown := src / SQUINT_SHOW
	_label("squint: flash and 45 % columns, old | new, blurred (1/8 scale) and shown at 1/2", Vector2(MARGIN.x, y - 2.0 * LABEL_SIZE - 6.0), 12)
	for g in GROUPS.size():
		var grp := GROUPS[g]
		var vp := SubViewport.new()
		vp.size = Vector2i(src)
		vp.transparent_bg = false
		vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		add_child(vp)
		for k in 2:
			_clock_panels(vp, grp, k, Vector2(k * (_block_w + BLOCK_GAP), 0.0), false)
		var tr := TextureRect.new()
		tr.texture = vp.get_texture()
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_SCALE
		tr.position = Vector2(MARGIN.x + g * (shown.x + SQUINT_GAP), y)
		tr.size = shown
		var m := ShaderMaterial.new()
		m.shader = _blur_shader()
		m.set_shader_parameter(&"radius", SQUINT_BLUR)
		tr.material = m
		add_child(tr)
		_label(String(grp["title"]), Vector2(tr.position.x, y + shown.y + 1.0), 11)


func _blur_shader() -> Shader:
	var s := Shader.new()
	s.code = """shader_type canvas_item;
uniform int radius = 4;
void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE;
	vec3 sum = vec3(0.0);
	float n = 0.0;
	for (int i = -8; i <= 8; i++) {
		for (int j = -8; j <= 8; j++) {
			if (abs(i) <= radius && abs(j) <= radius) {
				sum += texture(TEXTURE, UV + vec2(float(i), float(j)) * px).rgb;
				n += 1.0;
			}
		}
	}
	COLOR = vec4(sum / n, 1.0);
}
"""
	return s


## The magnified crops of one group: old | new, one bit each, drawn in a small viewport and shown ZOOM x with nearest filtering.
func _zoom_pair(grp: Dictionary, at: Vector2) -> void:
	for side in 2:
		var vp := SubViewport.new()
		vp.size = Vector2i(CROP_PX, CROP_PX)
		vp.transparent_bg = false
		vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		var v := RcLookBitsView.new()
		v.size = Vector2(CROP_PX, CROP_PX)
		v.preset = RcLookBits.preset(StringName(grp["old"] if side == 0 else grp["new"]))
		v.mode = &"zoom"
		v.glyph_px = GLYPH_PX
		vp.add_child(v)
		add_child(vp)
		var tr := TextureRect.new()
		tr.texture = vp.get_texture()
		tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_SCALE
		tr.position = at + Vector2(side * (_panel_w + GAP), 0.0)
		tr.size = Vector2(CROP_PX, CROP_PX) * ZOOM
		add_child(tr)
		_label("old" if side == 0 else "NEW", Vector2(tr.position.x, tr.position.y + tr.size.y + 1.0), 11)


func _label(text: String, at: Vector2, size: int = LABEL_SIZE) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", size)
	add_child(l)
