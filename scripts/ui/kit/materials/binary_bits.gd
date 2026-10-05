class_name BinaryBits
extends Node2D
## Binary bits (ART-1 1B; ART_BIBLE v2 §1.2 "Binary bits", §6.3 "Bits"): digital
## transitions, dissolves and damage. `0` / `1` glyphs (Share Tech Mono atlas with a
## same-colour outline, `shaders/kit/bits_atlas.png`, baked by
## `tools/design_lab/bits_atlas_bake.py`) in the source's colour, white-hot for the first
## `bits_flight` amplitude seconds, flipping 0 <-> 1, tumbling, then sucked along a curve into
## their target; round a wheel they go round the rim (BitsPath).
##
## A pool of GPUParticles2D (one per burst, additive, one pass) runs
## `shaders/kit/binary_bits.gdshader`, which lerps each bit along its Bezier from numbers the
## view computed (BitsPath.plan). `burst` returns every bit's arrival time (s from now) so a
## view schedules HP ticks, segment flashes and lag drains on them: particles are never read
## back and never change state. CPU fallback (`use_cpu_fallback`, at most CPU_MAX bits): the
## same plan drawn by this node (CPUParticles2D can't run a process shader, so the fallback
## draws the plan itself; DECISIONS "ART-1 1B").
##
## Reduce effects, headless or the entry switched off: no bits fly; every arrival is 0 (the
## end state at once). Tier: `bits_flight`'s (T2); the caller keeps it within its region.

signal burst_finished(index: int)

const SHADER := preload("res://shaders/kit/binary_bits.gdshader")
const ATLAS := preload("res://shaders/kit/bits_atlas.png")
const FLIGHT := &"bits_flight"
## Bits per GPU burst (the shader's uniform arrays) and the CPU fallback's cap.
const MAX_BITS := 64
const CPU_MAX := 44
## Emitters kept for reuse.
const POOL_SIZE := 4
## Atlas cells (0, 1, +, bit-rot) and how long a glyph shows before it flips (s).
const FRAMES := 4
const FLIP_SECONDS := 0.06
## Bits a rect source gives by default.
const RECT_BITS := 36
## A bit's drawn size share of the atlas cell.
const BIT_SCALE := 0.5
## Extra lifetime past the last arrival (s) before an emitter returns to the pool.
const LINGER := 0.1

@export var use_cpu_fallback: bool = false

var _pool: Array[GPUParticles2D] = []
var _bursts: Array[Dictionary] = []
var _next_index: int = 0


## Fires bits from `starts` (global positions) to `target` (global) in `color`; round a
## wheel when `rim_radius` > 0 (`rim_centre` global). Returns each bit's arrival time (s from
## now, sorted); all 0 when no bits fly (reduce effects, headless, switched off).
func burst(starts: PackedVector2Array, target: Vector2, color: Color, rim_centre: Vector2 = Vector2.ZERO,
		rim_radius: float = 0.0, seed: int = 0) -> PackedFloat32Array:
	var cap := CPU_MAX if use_cpu_fallback else MAX_BITS
	var local := PackedVector2Array()
	for i in mini(starts.size(), cap):
		local.append(to_local(starts[i]))
	var e := Motion.entry(FLIGHT)
	var plan := BitsPath.plan(local, to_local(target), e.duration if e != null else 0.0,
		e.delay if e != null else 0.0, seed, to_local(rim_centre), rim_radius)
	if not Motion.live(FLIGHT) or plan.is_empty():
		var none := PackedFloat32Array()
		none.resize(plan.size())
		return none
	var sp := maxf(Motion.speed, Motion.SPEED_MIN)
	for b in plan:
		b["delay"] = float(b["delay"]) / sp
		b["flight"] = float(b["flight"]) / sp
		b["arrive"] = float(b["arrive"]) / sp
	var total := 0.0
	for b in plan:
		total = maxf(total, float(b["arrive"]))
	var rec := {"index": _next_index, "plan": plan, "clock": 0.0, "total": total, "color": color, "target": to_local(target),
		"hot": Motion.amplitude(FLIGHT) / sp, "emitter": null}
	_next_index += 1
	if not use_cpu_fallback:
		rec["emitter"] = _start_gpu(rec)
	_bursts.append(rec)
	set_process(true)
	queue_redraw()
	return BitsPath.arrivals(plan)


## Bits from a rect's cells (a sticker, a card, a label: its opaque area), global coords.
func burst_from_rect(rect: Rect2, target: Vector2, color: Color, count: int = RECT_BITS, seed: int = 0) -> PackedFloat32Array:
	return burst(BitsPath.points_in_rect(rect, count), target, color, Vector2.ZERO, 0.0, seed)


## Bursts in flight now.
func active_bursts() -> int:
	return _bursts.size()


## Emitters made so far (pooled; reused after a burst ends).
func pool_size() -> int:
	return _pool.size()


## Ends every burst at once (MotionSkip passive: the arrivals were scheduled by the view).
func complete_motion() -> void:
	for rec in _bursts:
		_release(rec)
	_bursts.clear()
	queue_redraw()


func motion_running() -> bool:
	return not _bursts.is_empty()


func _ready() -> void:
	MotionSkip.register_passive(self)  # ANIM-R6 D7: flying bits end with any press that ends a motion
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	material = add  # the CPU fallback's bits; the GPU emitters carry their own
	set_process(false)


func _emitter() -> GPUParticles2D:
	for e in _pool:
		if not e.emitting and not e.has_meta(&"busy"):
			return e
	var g := GPUParticles2D.new()
	g.amount = MAX_BITS
	g.one_shot = true
	g.explosiveness = 1.0
	g.local_coords = true
	g.interpolate = false
	g.fixed_fps = 0
	g.texture = ATLAS
	g.visibility_rect = Rect2(-4096, -4096, 8192, 8192)
	var cm := CanvasItemMaterial.new()
	cm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	cm.particles_animation = true
	cm.particles_anim_h_frames = FRAMES
	cm.particles_anim_v_frames = 1
	cm.particles_anim_loop = false
	g.material = cm
	var pm := ShaderMaterial.new()
	pm.shader = SHADER
	g.process_material = pm
	if _pool.size() < POOL_SIZE:
		_pool.append(g)
	add_child(g)
	return g


func _start_gpu(rec: Dictionary) -> GPUParticles2D:
	var g := _emitter()
	g.set_meta(&"busy", true)
	var starts: Array[Vector4] = []
	var ctrls: Array[Vector4] = []
	for b in rec["plan"]:
		var s: Vector2 = b["start"]
		var c: Vector2 = b["ctrl"]
		starts.append(Vector4(s.x, s.y, b["delay"], b["flight"]))
		ctrls.append(Vector4(c.x, c.y, b["phase"], b["spin"]))
	var pm := g.process_material as ShaderMaterial
	pm.set_shader_parameter(&"bit_start", starts)
	pm.set_shader_parameter(&"bit_ctrl", ctrls)
	pm.set_shader_parameter(&"count", starts.size())
	pm.set_shader_parameter(&"target", rec["target"])
	pm.set_shader_parameter(&"clock", 0.0)
	pm.set_shader_parameter(&"hot_seconds", rec["hot"])
	pm.set_shader_parameter(&"color", rec["color"])
	pm.set_shader_parameter(&"flip_seconds", FLIP_SECONDS)
	pm.set_shader_parameter(&"bit_scale", BIT_SCALE)
	pm.set_shader_parameter(&"frames", float(FRAMES))
	g.lifetime = float(rec["total"]) + LINGER
	g.visible = true
	g.restart()
	g.emitting = true
	return g


func _release(rec: Dictionary) -> void:
	var g := rec.get("emitter") as GPUParticles2D
	if g != null and is_instance_valid(g):
		g.emitting = false
		g.visible = false
		g.remove_meta(&"busy")
		if not _pool.has(g):
			g.queue_free()
	burst_finished.emit(int(rec["index"]))


func _process(delta: float) -> void:
	var i := _bursts.size() - 1
	while i >= 0:
		var rec: Dictionary = _bursts[i]
		rec["clock"] = float(rec["clock"]) + delta
		var g := rec.get("emitter") as GPUParticles2D
		if g != null:
			(g.process_material as ShaderMaterial).set_shader_parameter(&"clock", rec["clock"])
		if float(rec["clock"]) > float(rec["total"]) + LINGER:
			_release(rec)
			_bursts.remove_at(i)
		i -= 1
	if use_cpu_fallback:
		queue_redraw()
	if _bursts.is_empty():
		set_process(false)


## The CPU fallback: the same plan drawn here (the GPU path draws nothing of its own).
func _draw() -> void:
	if not use_cpu_fallback:
		return
	var cell := Vector2(ATLAS.get_width() / float(FRAMES), ATLAS.get_height())
	for rec in _bursts:
		var clock: float = rec["clock"]
		var col: Color = rec["color"]
		var target: Vector2 = rec["target"]
		for b in rec["plan"]:
			var age := clock - float(b["delay"])
			var t := age / maxf(float(b["flight"]), 0.001)
			if age < 0.0 or t >= 1.0:
				continue
			var p := BitsPath.at(b["start"], b["ctrl"], target, BitsPath.eased(t))
			var hot := clampf(age / maxf(float(rec["hot"]), 0.001), 0.0, 1.0)
			var c := Palette.WHITE_HOT.lerp(col, hot)
			var frame := int(floor(age / FLIP_SECONDS + float(b["phase"]) * 7.0)) % 2
			var sz := cell * BIT_SCALE * lerpf(1.0, 0.55, t)
			draw_set_transform(p, clock * float(b["spin"]))
			draw_texture_rect_region(ATLAS, Rect2(-sz * 0.5, sz), Rect2(Vector2(cell.x * frame, 0), cell), c)
	draw_set_transform(Vector2.ZERO, 0.0)
