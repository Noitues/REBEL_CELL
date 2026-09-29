class_name Hologram
extends Control
## An enemy or boss as a hologram (ART_BIBLE 7.2, 6.1, 8): the PortraitArt subject drawn
## as projected light in its corporation's hue, its body filled with the corp pattern
## (CorpPattern), over a projector cone, with scanlines. The net's material (§7.1: "scan
## lines in the net"), through W6's `crt_overlay` shader (roll band, static scanlines).
##
## - BUST: the enemy portrait above its wheel (1:1; W3 places and sizes it).
## - BOSS: the large hologram behind the boss wheel, sized by `boss_size` to about 40% of
##   the screen height and dimmed (`dim`) so the wheel and its values stay readable. W3
##   places it so it never covers slice values.
##
## Motion: T0 idle (`hologram_idle`: the scanlines drift one pitch per `duration`, a slow
## shimmer of `amplitude` alpha) and the T4 intro reveal (`hologram_intro`, `play_intro`),
## which W3's boss intro sting plays under its name slam. Reduce effects: fully static
## (no drift, no shimmer, the shader's roll stops through the global `reduce_effects`
## uniform) and the intro is a plain cross-fade (`hologram_intro_fade`). Headless: the end
## state at once. View only: it never reads or changes game state, and it takes no input
## (W3's sting owns skipping: it calls `finish_intro`).

## Emitted when the intro reveal has ended (played out, cross-faded or finished early).
signal intro_finished

enum Mode { BUST, BOSS }

## Boss mode: the hologram's side is this share of the viewport height (§7.2 "≈ 40%").
const BOSS_HEIGHT_SHARE := 0.4
## Boss mode: the figure's alpha behind the wheel (the wheel stays readable).
const BOSS_DIM := 0.5
## Bust mode: the default side at text scale 1.0 (px); W3 may size it.
const BUST_SIDE := 96.0
## The reference viewport height (1280x720 base, ART_BIBLE 5.4) for the default boss size.
const REFERENCE_HEIGHT := 720.0
## Light levels of the projected figure (alphas of the subject's hue).
const BODY_ALPHA := 0.2
const PATTERN_ALPHA := 0.45
const EDGE_ALPHA := 0.9
const DETAIL_ALPHA := 0.6
const CONE_ALPHA := 0.1
const SCAN_ALPHA := 0.1
## Scanline pitch (px) and the projector base's height (share of the side).
const SCAN_PITCH := 3.0
const BASE_SHARE := 0.06
## The crt_overlay settings on the hologram (W6's shader; its roll is T0, ≥ 3 s).
const CRT_SHADER := "res://shaders/crt_overlay.gdshader"
const CRT_SCAN_STRENGTH := 0.18
const CRT_ROLL_STRENGTH := 0.12
const CRT_FLICKER := 0.02
## Motion table ids (content/config/ui_motion.tres).
const IDLE_ID := &"hologram_idle"
const INTRO_ID := &"hologram_intro"
const INTRO_FADE_ID := &"hologram_intro_fade"

## The PortraitArt subject shown (enemy_subject / enemy_data_subject).
var subject: Dictionary = {}
var mode: int = Mode.BUST
## The figure's alpha multiplier (BOSS_DIM for a boss, 1 for a bust).
var dim: float = 1.0
## Intro progress 0..1 (1 = fully projected).
var reveal: float = 1.0
## The idle clock (s); frozen at 0 under reduce effects and headless.
var phase: float = 0.0
var _intro: Tween = null
var _fading: bool = false


func _init(p_subject: Dictionary = {}, p_mode: int = Mode.BUST) -> void:
	subject = p_subject
	mode = p_mode
	dim = BOSS_DIM if mode == Mode.BOSS else 1.0
	name = "Hologram"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	custom_minimum_size = boss_size(REFERENCE_HEIGHT) if mode == Mode.BOSS else Vector2.ONE * BUST_SIDE * Settings.text_scale


## A hologram for an enemy's content (EnemyData): BOSS for a boss, BUST otherwise.
static func for_enemy(data: EnemyData) -> Hologram:
	return Hologram.new(PortraitArt.enemy_data_subject(data), Mode.BOSS if data.is_boss else Mode.BUST)


## The boss hologram's size for a viewport `height` (px): a square of BOSS_HEIGHT_SHARE.
static func boss_size(height: float) -> Vector2:
	return Vector2.ONE * height * BOSS_HEIGHT_SHARE


func _ready() -> void:
	var sh := load(CRT_SHADER) as Shader
	if sh != null:
		var m := ShaderMaterial.new()
		m.shader = sh
		m.set_shader_parameter(&"scan_strength", CRT_SCAN_STRENGTH)
		m.set_shader_parameter(&"roll_strength", CRT_ROLL_STRENGTH)
		m.set_shader_parameter(&"flicker", CRT_FLICKER)
		m.set_shader_parameter(&"roll_period", maxf(VfxTier.T0_MIN_PERIOD, Motion.seconds(IDLE_ID)))
		material = m
	if not Settings.changed.is_connected(_sync_live):
		Settings.changed.connect(_sync_live)
	_sync_live()


func _exit_tree() -> void:
	if Settings.changed.is_connected(_sync_live):
		Settings.changed.disconnect(_sync_live)


## True when the idle drift and shimmer play (effects on, a real display, entry enabled).
func is_live() -> bool:
	return Motion.live(IDLE_ID)


## Starts or stops the idle clock with the settings (reduce effects: static at phase 0).
func _sync_live() -> void:
	var live := is_live()
	set_process(live)
	if not live:
		phase = 0.0
	queue_redraw()


func _process(delta: float) -> void:
	phase += delta
	queue_redraw()


## The T4 intro reveal (W3's boss intro sting): the figure projects up from its base
## with a bright scan edge (`hologram_intro`). Reduce effects: a cross-fade
## (`hologram_intro_fade`). Headless or switched off: the end state at once. Emits
## `intro_finished` when done.
func play_intro() -> void:
	_stop_intro()
	if not Fx.effects_enabled():
		reveal = 1.0
		var e := Motion.entry(INTRO_FADE_ID)
		if e != null and e.enabled and (Motion.force_live or DisplayServer.get_name() != "headless"):
			modulate.a = 0.0
			_fading = true
			_intro = create_tween()
			_intro.tween_property(self, "modulate:a", 1.0, Motion.seconds(INTRO_FADE_ID))
			_intro.finished.connect(_on_intro_done)
			return
		_on_intro_done()
		return
	if not Motion.live(INTRO_ID):
		reveal = 1.0
		_on_intro_done()
		return
	var e := Motion.entry(INTRO_ID)
	reveal = 0.0
	_intro = create_tween()
	_intro.tween_method(_set_reveal, 0.0, 1.0, Motion.seconds(INTRO_ID)).set_delay(Motion.delay_of(INTRO_ID)).set_ease(e.ease).set_trans(e.trans)
	_intro.finished.connect(_on_intro_done)


## Ends a running intro at once (its end state) and emits `intro_finished` (W3's skip).
func finish_intro() -> void:
	if not intro_running():
		return
	_stop_intro()
	_on_intro_done()


## True while the intro reveal or its cross-fade plays.
func intro_running() -> bool:
	return _intro != null and _intro.is_valid() and _intro.is_running()


func _stop_intro() -> void:
	if _intro != null and _intro.is_valid():
		_intro.kill()
	_intro = null


func _set_reveal(v: float) -> void:
	reveal = v
	queue_redraw()


func _on_intro_done() -> void:
	_intro = null
	_fading = false
	reveal = 1.0
	modulate.a = 1.0
	queue_redraw()
	intro_finished.emit()


## The shimmer's alpha factor now (1 when static).
func shimmer() -> float:
	if phase == 0.0:
		return 1.0
	var period := maxf(0.001, Motion.seconds(IDLE_ID))
	return 1.0 - Motion.amplitude(IDLE_ID) * (0.5 + 0.5 * sin(TAU * phase / period))


## The square the figure is drawn in (centred, bottom-aligned in the control).
func figure_rect() -> Rect2:
	var side := minf(size.x, size.y)
	return Rect2(Vector2((size.x - side) * 0.5, size.y - side), Vector2(side, side))


func _draw() -> void:
	if subject.is_empty():
		return
	var rect := figure_rect()
	if rect.size.x <= 0.0:
		return
	var tint: Color = subject["tint"]
	var a := dim * shimmer()
	var base_h := rect.size.y * BASE_SHARE
	var base_c := Vector2(rect.get_center().x, rect.end.y - base_h * 0.5)
	# The projector: a cone of light from the base, then the base's lit ellipse.
	var cone := PackedVector2Array([base_c + Vector2(-rect.size.x * 0.08, 0), base_c + Vector2(rect.size.x * 0.08, 0),
		Vector2(rect.end.x - rect.size.x * 0.06, rect.position.y + rect.size.y * 0.1), Vector2(rect.position.x + rect.size.x * 0.06, rect.position.y + rect.size.y * 0.1)])
	draw_colored_polygon(cone, Color(tint, CONE_ALPHA * a * reveal))
	# The figure projects up from its base during the intro.
	var fig := Rect2(rect.position, Vector2(rect.size.x, rect.size.y - base_h))
	draw_set_transform(Vector2(0, fig.end.y * (1.0 - reveal)), 0.0, Vector2(1.0, maxf(0.001, reveal)))
	var s := PortraitArt.shapes(fig, subject)
	var r: float = s["r"]
	var w := maxf(1.0, r * 0.05)
	if subject.get("kind", -1) == PortraitArt.Kind.BOSS:
		PortraitArt.boss_halo(self, fig, subject, s, Color(tint, PATTERN_ALPHA * a))
	for p in PortraitArt.silhouette_polygons(fig, subject):
		draw_colored_polygon(p, Color(tint, BODY_ALPHA * a))
	var body: PackedVector2Array = s["body"]
	var pattern := PortraitArt.pattern_of(subject)
	if pattern != CorpPattern.Kind.NONE and body.size() >= 3:
		CorpPattern.fill_polygon(self, body, pattern, Color(tint, PATTERN_ALPHA * a), clampf(fig.size.x / PortraitArt.PATTERN_REF, PortraitArt.PATTERN_SCALE_MIN, 1.0))
	for p in PortraitArt.silhouette_polygons(fig, subject):
		var closed := p.duplicate()
		closed.append(p[0])
		draw_polyline(closed, Color(tint, EDGE_ALPHA * a), w, true)
	for e in s["extras"]:
		draw_line(e[0], e[1], Color(tint, EDGE_ALPHA * a), w * 1.4, true)
	var c: Vector2 = s["c"]
	var lens: float = s["lens"]
	var hot := Palette.TEXT_HI
	if lens > 0.0:
		draw_circle(c, lens, Color(tint, DETAIL_ALPHA * a))
		draw_circle(c, lens * 0.45, Color(hot, a))
	for p in s["eyes"]:
		if (p as PackedVector2Array).size() >= 3:
			draw_colored_polygon(p, Color(hot, a))
	var tie: PackedVector2Array = s["tie"]
	if tie.size() >= 3:
		draw_colored_polygon(tie, Color(tint, DETAIL_ALPHA * a))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# The base disc.
	draw_set_transform(base_c, 0.0, Vector2(1.0, 0.25))
	draw_circle(Vector2.ZERO, rect.size.x * 0.22, Color(tint, CONE_ALPHA * 2.0 * a))
	draw_arc(Vector2.ZERO, rect.size.x * 0.22, 0.0, TAU, 32, Color(tint, EDGE_ALPHA * a), 2.0, true)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	# Scanlines drifting one pitch per idle period (static under reduce effects).
	var drift := 0.0
	if phase != 0.0:
		drift = fmod(phase / maxf(0.001, Motion.seconds(IDLE_ID)), 1.0) * SCAN_PITCH
	var top := fig.position.y + fig.size.y * (1.0 - reveal)
	var y := top + drift
	while y < fig.end.y:
		draw_line(Vector2(fig.position.x, y), Vector2(fig.end.x, y), Color(tint, SCAN_ALPHA * a), 1.0)
		y += SCAN_PITCH
	# The intro's bright scan edge at the top of the projected part.
	if reveal < 1.0 and not _fading:
		draw_line(Vector2(fig.position.x, top), Vector2(fig.end.x, top), Color(hot, a), 2.0)
