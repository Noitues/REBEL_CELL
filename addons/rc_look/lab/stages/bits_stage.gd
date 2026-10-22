extends RcLookLabStage
## LOOK-TOOLBOX module 16 in the lab: the same bit plan through the four ways the game draws bits, side by side at fixed
## clocks. Columns: (1) BinaryBits on the GPU with today's binary_bits.gdshader, (2) the same plan on the module's
## drop-in shader (rc_bits_particles.gdshader, built on rc_bits.gdshaderinc), (3) BinaryBits' CPU fallback, (4) BitsSeam's
## glyph drawing (the combat streams' look) from a BitPath built out of the same plan. Rows: three clocks as shares of
## the last arrival that BinaryBits.burst returned. Columns 1 and 2 must match pixel for pixel; 3 and 4 differ where the
## game's two systems diverge (the rulings, see bits_rulings_stage.gd).
##
## `--bits_probe=<json>` (after the lab's `--`) also runs the probe in off-screen viewports and writes the answers there:
## the largest pixel difference between the current shader and the module's at three clocks, and whether the atlas frame
## channel (CUSTOM.z, risk R7) really flips 0 / 1 on the GPU. View only.

## Layout (px): margins, gap, label size, the columns' count.
const MARGIN := Vector2(150.0, 70.0)
const GAP := 14.0
const LABEL_SIZE := 14
## The clocks, as shares of the last arrival.
const CLOCK_SHARES: Array[float] = [0.2, 0.5, 0.8]
const COLUMN_TITLES: Array[String] = ["GPU: binary_bits.gdshader (today)", "GPU: module drop-in (rc_bits)",
	"CPU fallback (BinaryBits)", "BitsSeam (BitPath, streams)"]
## The scene in a cell (shares of the cell): the source rect, the wheel's centre and radius (of the cell's height).
const SOURCE_RECT := Rect2(0.08, 0.2, 0.26, 0.6)
const WHEEL_CENTRE := Vector2(0.7, 0.5)
const WHEEL_RADIUS := 0.3
const BITS := 36
const SEED := 7
const BIT_COLOR := Color(1.0, 0.24, 0.66)
const BACKDROP := Color(0.02, 0.025, 0.05)
const RING_COLOR := Color(1, 1, 1, 0.12)
## BitsSeam's lettering size for the lab (px) and the stream preset's name.
const SEAM_PX := 26.0
## The probe: viewport size, the clocks (single bit: frame 0, frame 0, frame 1), the single bit's long flight (s) and its
## tiny hot time, the flight check's clocks (shares of the last arrival), the pixel shown as a difference.
const PROBE_PX := 192
const PROBE_FLIP_CLOCKS: Array[float] = [0.01, 0.02, 0.07]
const PROBE_FLIGHT_S := 100.0
const PROBE_HOT_S := 0.001
const PROBE_FRAMES := 4
## The frame counts as flipped when the 0 -> 1 change moves this many times more pixels than the same-frame control
## (the control differs by a few anti-aliased edge pixels: the bit shrinks a hair over 100 s).
const PROBE_FLIP_RATIO := 10
const PROBE_SETTLE := 90
## How long a held GPU burst lives (s).
const HOLD_LIFETIME := 100.0
## Two arrival lists count as the same within this many seconds (cells sit at different global positions: float noise).
const ARRIVAL_TOLERANCE := 0.0001
const CURRENT_SHADER := preload("res://shaders/kit/binary_bits.gdshader")
const MODULE_SHADER := preload("res://addons/rc_look/shaders/rc_bits_particles.gdshader")

var _cells: Array = []  # [row][col] = {host, dyn: Array[Node]}
var _cell_size: Vector2 = Vector2.ZERO
var _probe_path: String = ""
var _status: Label


func _ready() -> void:
	var view := get_viewport_rect().size
	var cols := COLUMN_TITLES.size()
	var rows := CLOCK_SHARES.size()
	_cell_size = Vector2((view.x - MARGIN.x - 30.0 - GAP * (cols - 1)) / cols, (view.y - MARGIN.y - 66.0 - GAP * (rows - 1)) / rows)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--bits_probe="):
			_probe_path = a.trim_prefix("--bits_probe=")
	for c in cols:
		_label(COLUMN_TITLES[c], Vector2(MARGIN.x + c * (_cell_size.x + GAP), MARGIN.y - LABEL_SIZE - 10.0))
	for r in rows:
		var row: Array = []
		for c in cols:
			var host := _Backdrop.new()
			host.position = MARGIN + Vector2(c * (_cell_size.x + GAP), r * (_cell_size.y + GAP))
			host.size = _cell_size
			host.clip_contents = true
			host.bg = BACKDROP
			host.ring_centre = _cell_size * WHEEL_CENTRE
			host.ring_radius = _cell_size.y * WHEEL_RADIUS
			add_child(host)
			row.append({"host": host, "dyn": []})
		_cells.append(row)
	_status = _label("", Vector2(MARGIN.x, view.y - 54.0))
	apply(&"night", null)
	if _probe_path != "":
		_run_probe.call_deferred()


func settle_frames() -> int:
	return PROBE_SETTLE if _probe_path != "" else 8


func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	for r in _cells.size():
		_fire_row(r)


## Fires one row: the GPU cell first (it makes the plan and its arrival times), then the others on the same plan.
func _fire_row(r: int) -> void:
	var row: Array = _cells[r]
	for cell: Dictionary in row:
		for n: Node in cell["dyn"]:
			if is_instance_valid(n):
				n.queue_free()
		cell["dyn"] = []
	var rect := Rect2(_cell_size * SOURCE_RECT.position, _cell_size * SOURCE_RECT.size)
	var starts := BitsPath.points_in_rect(rect, BITS)
	var target := _cell_size * WHEEL_CENTRE
	var radius := _cell_size.y * WHEEL_RADIUS
	var share := CLOCK_SHARES[r]
	var gpu := _bits_node(row[0], false)
	var arrivals := _burst_in(gpu, row[0], starts, target, radius)
	var live := not gpu._bursts.is_empty()
	var info := "t = %.0f %% of the last arrival" % (share * 100.0)
	if not live:
		_status.text = "bits are off (reduce effects): every arrival is 0, nothing flies"
		return
	var rec: Dictionary = gpu._bursts[0]
	var total := float(arrivals[arrivals.size() - 1])
	var clock := share * total
	_hold(gpu, rec, clock)
	info += " = %.3f s" % clock
	(row[0]["host"] as Control).set_meta(&"info", info)
	var plan: Array[Dictionary] = rec["plan"]
	var hot: float = rec["hot"]
	# column 2: the module's shader on the same plan
	var em := make_emitter(MODULE_SHADER, plan, target, BIT_COLOR, hot, clock)
	(row[1]["host"] as Control).add_child(em)
	row[1]["dyn"].append(em)
	# column 3: the CPU fallback
	var cpu := _bits_node(row[2], true)
	var carr := _burst_in(cpu, row[2], starts, target, radius)
	if not cpu._bursts.is_empty():
		_hold(cpu, cpu._bursts[0], clock)
	# column 4: BitsSeam on a BitPath made of the plan
	var seam := _Seam.new()
	seam.size = _cell_size
	seam.path = seam_path(plan, target)
	seam.clock = clock
	seam.color = BIT_COLOR
	seam.hot = hot
	(row[3]["host"] as Control).add_child(seam)
	row[3]["dyn"].append(seam)
	if r == 0:
		_status.text = "BinaryBits.burst arrivals: %d bits, %.3f .. %.3f s; the CPU fallback returns the same (within %s s): %s" % [
			arrivals.size(), arrivals[0], total, ARRIVAL_TOLERANCE, _same_times(arrivals, carr)]
	for c in row.size():
		var host := row[c]["host"] as Control
		host.queue_redraw()


## Fires `bb` (a node in `cell`) with cell-local `starts` and `target`: BinaryBits takes global points, so they are
## shifted by the cell's origin. Returns its arrival times.
func _burst_in(bb: BinaryBits, cell: Dictionary, starts: PackedVector2Array, target: Vector2, radius: float) -> PackedFloat32Array:
	var origin := (cell["host"] as Control).global_position
	var g := PackedVector2Array()
	for p in starts:
		g.append(p + origin)
	return bb.burst(g, target + origin, BIT_COLOR, target + origin, radius, SEED)


## A BinaryBits in a cell (at the cell's origin, so its local coordinates are the cell's).
func _bits_node(cell: Dictionary, cpu: bool) -> BinaryBits:
	var bb := BinaryBits.new()
	bb.use_cpu_fallback = cpu
	(cell["host"] as Control).add_child(bb)
	cell["dyn"].append(bb)
	return bb


## Freezes a burst at `clock` (the lab compares fixed clocks; BinaryBits' own _process would run it live).
static func _hold(bb: BinaryBits, rec: Dictionary, clock: float) -> void:
	bb.set_process(false)
	rec["clock"] = clock
	var g := rec.get("emitter") as GPUParticles2D
	if g != null:
		(g.process_material as ShaderMaterial).set_shader_parameter(&"clock", clock)
		g.lifetime = HOLD_LIFETIME  # the capture may come later than the burst's own lifetime
		g.restart()
	bb.queue_redraw()


## A BitPath carrying a BitsPath plan (appearing and released at the spawn delay, travelling its flight), for BitsSeam.
static func seam_path(plan: Array[Dictionary], target: Vector2) -> BitPath:
	var bp := BitPath.new()
	for b in plan:
		bp.bits.append({"from": b["start"], "burst": Vector2.ZERO, "ctrl": b["ctrl"], "to": target, "appear": b["delay"],
			"release": b["delay"], "travel": b["flight"], "glyph": BitPath.ONE if float(b["phase"]) > 0.5 else BitPath.ZERO,
			"size": SEAM_PX, "fade": false, "end_scale": RcLookBits.default_config().end_scale})
	return bp


## A one-shot GPU emitter running `shader` on `plan` (cell-local coordinates), frozen at `clock`: BinaryBits' emitter
## with the plan's numbers set the way BinaryBits sets them. Returns a node to add where the plan's origin should be.
static func make_emitter(shader: Shader, plan: Array[Dictionary], target: Vector2, color: Color, hot: float, clock: float,
		lifetime: float = 100.0) -> GPUParticles2D:
	var cfg := RcLookBits.default_config()
	var g := GPUParticles2D.new()
	g.amount = cfg.max_bits
	g.one_shot = true
	g.explosiveness = 1.0
	g.local_coords = true
	g.interpolate = false
	g.fixed_fps = 0
	g.texture = BinaryBits.ATLAS
	g.visibility_rect = Rect2(-4096, -4096, 8192, 8192)
	g.lifetime = lifetime
	var cm := CanvasItemMaterial.new()
	cm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	cm.particles_animation = true
	cm.particles_anim_h_frames = cfg.frames
	cm.particles_anim_v_frames = 1
	cm.particles_anim_loop = false
	g.material = cm
	var pm := ShaderMaterial.new()
	pm.shader = shader
	var starts: Array[Vector4] = []
	var ctrls: Array[Vector4] = []
	for b in plan:
		var s: Vector2 = b["start"]
		var c: Vector2 = b["ctrl"]
		starts.append(Vector4(s.x, s.y, b["delay"], b["flight"]))
		ctrls.append(Vector4(c.x, c.y, b["phase"], b["spin"]))
	pm.set_shader_parameter(&"bit_start", starts)
	pm.set_shader_parameter(&"bit_ctrl", ctrls)
	pm.set_shader_parameter(&"count", starts.size())
	pm.set_shader_parameter(&"target", target)
	pm.set_shader_parameter(&"clock", clock)
	pm.set_shader_parameter(&"hot_seconds", hot)
	pm.set_shader_parameter(&"color", color)
	pm.set_shader_parameter(&"flip_seconds", cfg.flip_seconds)
	pm.set_shader_parameter(&"bit_scale", cfg.bit_scale)
	pm.set_shader_parameter(&"frames", float(cfg.frames))
	g.process_material = pm
	g.emitting = true
	return g


## The probe: current shader vs the module's, off-screen, answers written as JSON.
func _run_probe() -> void:
	var result := {}
	var cfg := RcLookBits.default_config()
	var cur_vp := _probe_viewport()
	var mod_vp := _probe_viewport()
	var mid := Vector2(PROBE_PX, PROBE_PX) * 0.5
	# R7: one bit that stays put (start = control = target) with no spin and phase 0: only the frame can change.
	var one: Array[Dictionary] = [{"start": Vector2.ZERO, "ctrl": Vector2.ZERO, "delay": 0.0, "flight": PROBE_FLIGHT_S,
		"arrive": PROBE_FLIGHT_S, "phase": 0.0, "spin": 0.0}]
	var flip_imgs: Array[Image] = []
	var flip_mod: Array[Image] = []
	for pair: Array in [[CURRENT_SHADER, cur_vp, flip_imgs], [MODULE_SHADER, mod_vp, flip_mod]]:
		var vp := pair[1] as SubViewport
		var em := make_emitter(pair[0], one, Vector2.ZERO, Color.WHITE, PROBE_HOT_S, PROBE_FLIP_CLOCKS[0])
		em.position = mid
		vp.add_child(em)
		var pm := em.process_material as ShaderMaterial
		pm.set_shader_parameter(&"bit_scale", 1.0)
		for k in PROBE_FLIP_CLOCKS:
			pm.set_shader_parameter(&"clock", k)
			(pair[2] as Array).append(await _grab(vp))
		em.queue_free()
	result["frame_channel_flips"] = _lit_diff(flip_imgs[0], flip_imgs[2]) > PROBE_FLIP_RATIO * maxi(1, _lit_diff(flip_imgs[0], flip_imgs[1]))
	result["frame0_vs_frame0_px"] = _lit_diff(flip_imgs[0], flip_imgs[1])
	result["frame0_vs_frame1_px"] = _lit_diff(flip_imgs[0], flip_imgs[2])
	result["flip_module_equals_current"] = _max_diff(flip_imgs[0], flip_mod[0]) == 0 and _max_diff(flip_imgs[2], flip_mod[2]) == 0
	# Whole plan: three clocks, current vs module, largest byte difference.
	var starts := BitsPath.points_in_rect(Rect2(8, 30, 60, 130), BITS)
	var target := Vector2(PROBE_PX * 0.7, PROBE_PX * 0.5)
	var plan := RcLookBits.plan(starts, target, 0.55, 0.12, SEED, target, PROBE_PX * 0.3)
	var total := float(RcLookBits.arrivals(plan)[plan.size() - 1])
	var diffs: Array[int] = []
	for share in CLOCK_SHARES:
		var imgs: Array[Image] = []
		for pair: Array in [[CURRENT_SHADER, cur_vp], [MODULE_SHADER, mod_vp]]:
			var vp := pair[1] as SubViewport
			var em := make_emitter(pair[0], plan, target, BIT_COLOR, 0.08, share * total)
			vp.add_child(em)
			imgs.append(await _grab(vp))
			em.queue_free()
		diffs.append(_max_diff(imgs[0], imgs[1]))
	result["max_pixel_diff_current_vs_module"] = diffs.max()
	result["pixel_diffs_per_clock"] = diffs
	var f := FileAccess.open(_probe_path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(result, "\t"))
	_status.text += "\nprobe: atlas frame channel flips = %s; largest pixel difference, current vs module shader = %s" % [
		result["frame_channel_flips"], result["max_pixel_diff_current_vs_module"]]
	cur_vp.queue_free()
	mod_vp.queue_free()


func _probe_viewport() -> SubViewport:
	var vp := SubViewport.new()
	vp.size = Vector2i(PROBE_PX, PROBE_PX)
	vp.transparent_bg = false
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	return vp


func _grab(vp: SubViewport) -> Image:
	for k in PROBE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	return vp.get_texture().get_image()


## The largest per-channel byte difference between two images.
static func _max_diff(a: Image, b: Image) -> int:
	var da := a.get_data()
	var db := b.get_data()
	var worst := 0
	for i in mini(da.size(), db.size()):
		worst = maxi(worst, absi(int(da[i]) - int(db[i])))
	return worst


## How many pixels differ at all between two images.
static func _lit_diff(a: Image, b: Image) -> int:
	var da := a.get_data()
	var db := b.get_data()
	var n := 0
	for i in range(0, mini(da.size(), db.size()), 4):
		if da[i] != db[i] or da[i + 1] != db[i + 1] or da[i + 2] != db[i + 2]:
			n += 1
	return n


func _label(text: String, at: Vector2) -> Label:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	add_child(l)
	return l


## A cell's backdrop: the dark ground and the wheel's rim ring, with the row's clock written beside the first cell.
class _Backdrop extends Control:
	var bg: Color = Color.BLACK
	var ring_centre: Vector2 = Vector2.ZERO
	var ring_radius: float = 0.0

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), bg)
		draw_arc(ring_centre, ring_radius, 0.0, TAU, 64, RING_COLOR, 2.0)
		if has_meta(&"info"):
			draw_string(ThemeDB.fallback_font, Vector2(6.0, size.y - 6.0), String(get_meta(&"info")), HORIZONTAL_ALIGNMENT_LEFT,
					-1.0, 12, Color(1, 1, 1, 0.5))


## BitsSeam's glyph drawing of a BitPath at a fixed clock.
class _Seam extends Control:
	var path: BitPath
	var clock: float = 0.0
	var color: Color = Color.WHITE
	var hot: float = 0.1

	func _draw() -> void:
		BitsSeam.draw(self, path, clock, color, Vector2.ZERO, hot)


static func _same_times(a: PackedFloat32Array, b: PackedFloat32Array) -> bool:
	if a.size() != b.size():
		return false
	for i in a.size():
		if absf(a[i] - b[i]) > ARRIVAL_TOLERANCE:
			return false
	return true
