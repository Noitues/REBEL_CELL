extends "res://tools/visual_qa/review_pack.gd"
## ART-12 12p: the windowed frame-time profile of every screen (dev tool, never exported). It
## walks the review pack's screens (the same drivers, so every screen is reached the way the QA
## matrix reaches it) plus the profile's own (the HQ run's page and gate, the worst-case combat
## fixture of `tools/design_lab/arena_lab.gd` with and without wheels + FX), once per city
## quality tier, in ONE launch. Per screen, once it is reached and its picture taken, it turns
## v-sync off, warms up, then times frames for `--perf` seconds and prints one PERF line:
## the frame time (mean, p95, max), the GPU time of the root viewport (the 2D layers: HUD, wheels,
## FX, the composited city), of the 3D city (every CityView3D) and of every live SubViewport,
## the render CPU, draw calls and primitives. Needs a renderer: windowed only,
## through tools/run_windowed.py:
##
##   python tools/run_windowed.py --log <f> --timeout 5400 -- --resolution 1920x1080
##     res://tools/visual_qa/perf_pack.tscn -- --out=<abs dir> [--tiers=2,1] [--perf=4]
##     [--warmup=60] [--size=1920x1080] [--screens=a,b] [--save-size=480x270]
##
## --tiers sets Settings.city_quality per pass (each screen builds its city fresh, so it reads
## the tier); <out>/tier<N>/ holds the pictures and <screen>.perf.json.

const ARENA_LAB := preload("res://tools/design_lab/arena_lab.gd")
## The profile's own screens (after the review pack's).
const PERF_SCREENS := [
	["hq_run", "_s_hq_run", "ART-8 8w: the HQ run's page on the corp's compound (boss run)."],
	["hq_run_gate", "_s_hq_run_gate", "ART-8 8w: the Central Server's gate over the HQ run's page."],
	["combat_worst", "_s_combat_worst", "arena_lab worst fixture: boss on the city backdrop, every slot docked, firmware, Daemons, bloom, a card hovered."],
	["combat_worst_fx", "_s_combat_worst_fx", "The worst fixture with FX firing all through the timing (Perfect bursts, precision landings, numbers)."],
	["combat_worst_send", "_s_combat_worst_send", "The worst fixture with SEND IT pressed as the timing starts (the real turn's replay and FX on every docked drone)."],
	["combat_worst_bare","_s_combat_worst_bare", "The worst fixture with the wheels and the FX layer hidden (the wheels + FX cost is the difference)."],
]
## Run only when named in --screens: the worst fixture with one part hidden at a time (a
## PROBE line per part: its frame time against the whole screen's), to find what costs.
const PROBE_SCREENS := [
	["combat_worst_probe", "_s_combat_worst_probe", "The worst fixture, each part of the combat scene hidden in turn."],
	["combat_worst_redraw", "_s_combat_worst_redraw", "The worst fixture, every wheel view redrawn every frame (its own drawing's cost)."],
	["combat_worst_fxlayer", "_s_combat_worst_fxlayer", "The worst fixture, the FX layer's volley alone (no precision landing on the wheels)."],
	["scrim_probe_hq", "_s_scrim_probe_hq", "B1a: the HQ page with and without its UiScrimPools layer (pools, shadows, spill)."],
	["scrim_probe_route", "_s_scrim_probe_route", "B1a: the route page with and without its UiScrimPools layer."],
	["scrim_probe_combat", "_s_scrim_probe_combat", "B1a b: a fight's frame with and without its UiScrimPools layer."],
	["scrim_luma_combat_start", "_s_scrim_luma_combat_start", "B1a b: the fight's world luma in the wheel pools vs between the wheels (+ fixture)."],
	["scrim_luma_combat_aiming", "_s_scrim_luma_combat_aiming", "B1a b: the same while a card is aimed."],
	["scrim_luma_hq", "_s_scrim_luma_hq", "B1a b: the HQ's city luma in the panels' pool margins and under the foot band vs open (+ fixture)."],
	["scrim_luma_raid_setup", "_s_scrim_luma_raid_setup", "B1a b: the same on the raid setup (+ fixture)."],
	["scrim_luma_route", "_s_scrim_luma_route", "B1a b: the same on the route page (+ fixture)."],
]
const ScrimLuma := preload("res://tools/visual_qa/scrim_luma.gd")
## B1a b: the luma probe's working size and fixture size (px).
const LUMA_SIZE := Vector2i(480, 270)
## Frames and seconds per probe part.
const PROBE_WARMUP := 20
const PROBE_S := 1.2
const PERF_DEFAULT_S := 4.0
## A frame longer than this (ms: the 60 fps frame, TECH_SPEC 10) is listed as a hitch, at most
## MAX_SPIKES of them per screen.
const SPIKE_MS := 16.7
const MAX_SPIKES := 40
const WARMUP_DEFAULT := 60
## Frames between two FX volleys in combat_worst_fx.
const FX_EVERY := 12

var _perf_s := PERF_DEFAULT_S
var _warmup := WARMUP_DEFAULT
var _tiers: PackedInt32Array = []
var _size := Vector2i(1920, 1080)
## --census: also count every CanvasItem's redraws through the timing and print the busiest
## (CENSUS lines; the counting itself costs frame time, so read its frame times apart).
var _census := false
const CENSUS_TOP := 15
var _tier := -1
## Called every timed frame (combat_worst_fx fires its FX from it).
var _tick: Callable = Callable()
var _combat: Control = null
## combat_worst_fx's volley lands a precision landing on every wheel too (off: the FX layer alone).
var _fx_precision := true


func _ready() -> void:
	var only: PackedStringArray = []
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--screens="):
			only = a.trim_prefix("--screens=").split(",", false)
		elif a.begins_with("--perf="):
			_perf_s = float(a.trim_prefix("--perf="))
		elif a == "--census":
			_census = true
		elif a.begins_with("--warmup="):
			_warmup = int(a.trim_prefix("--warmup="))
		elif a.begins_with("--tiers="):
			for t in a.trim_prefix("--tiers=").split(",", false):
				_tiers.append(int(t))
		elif a.begins_with("--size="):
			var wh := a.trim_prefix("--size=").split("x")
			_size = Vector2i(int(wh[0]), int(wh[1]))
		elif a.begins_with("--save-size="):
			var wh := a.trim_prefix("--save-size=").split("x")
			save_size = Vector2i(int(wh[0]), int(wh[1]))
		elif a.begins_with("--screen-timeout="):
			screen_timeout = float(a.trim_prefix("--screen-timeout="))
	if out_dir == "":
		push_error("perf_pack: --out=<dir> is required")
		get_tree().quit(2)
		return
	if _tiers.is_empty():
		_tiers.append(-1)
	DirAccess.make_dir_recursive_absolute(out_dir)
	_log = ErrorLog.new()
	OS.add_logger(_log)
	_setup_settings()
	# The quiet window takes Settings' resolution (apply_display): the profile's size, no v-sync.
	Settings.resolution = _size
	Settings.vsync = false
	Settings.apply_display()
	for n in get_tree().root.get_children():
		_keep.append(n)
	await get_tree().process_frame
	var todo: Array = []
	for s in SCREENS + PERF_SCREENS + PROBE_SCREENS:
		if (only.is_empty() and not PROBE_SCREENS.has(s)) or only.has(s[0]):
			todo.append(s)
	var base := out_dir
	print("PERFPACK start screens=%d tiers=%s window=%s" % [todo.size(), str(_tiers), str(DisplayServer.window_get_size())])
	for tier in _tiers:
		_tier = tier
		Settings.city_quality = tier
		out_dir = base.path_join("tier%d" % tier)
		DirAccess.make_dir_recursive_absolute(out_dir)
		for s in todo:
			await _capture(s[0], s[1], s[2])
	out_dir = base
	_teardown()
	print("PERFPACK DONE %d screens x %d tiers in %s" % [todo.size(), _tiers.size(), out_dir])
	get_tree().quit()


func _capture(screen: String, method: String, what: String) -> void:
	_tick = Callable()
	_combat = null
	_fx_precision = true
	await super(screen, method, what)
	var status: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(out_dir.path_join(screen + ".status.json")))
	if status == null or String(status.get("status", "")) != "ok":
		print("PERF tier=%d screen=%s status=%s" % [_tier, screen, "?" if status == null else String(status.get("status", ""))])
		return
	await _measure(screen)


## Every SubViewport drawn each frame (a viewport drawn once or never keeps its last measured
## time: it is left out).
func _live_viewports() -> Array[SubViewport]:
	var out: Array[SubViewport] = []
	for n in get_tree().root.find_children("*", "SubViewport", true, false):
		var v := n as SubViewport
		if v != null and v.render_target_update_mode != SubViewport.UPDATE_DISABLED and v.render_target_update_mode != SubViewport.UPDATE_ONCE:
			out.append(v)
	return out


func _measure(screen: String) -> void:
	var root_rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(root_rid, true)
	var gen := _gen
	for i in _warmup:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
		for v in _live_viewports():
			RenderingServer.viewport_set_measure_render_time(v.get_viewport_rid(), true)
		if _tick.is_valid():
			_tick.call(i)
		await get_tree().process_frame
		if gen != _gen:
			return
	var times: Array[float] = []
	var root_gpu := 0.0
	var city_gpu := 0.0
	var sub_gpu := 0.0
	var cpu := 0.0
	var draws := 0.0
	var prims := 0.0
	var subs := 0
	var counts := {}
	var items: Array[Node] = []
	var hooks: Array[Callable] = []
	if _census:
		items = get_tree().root.find_children("*", "CanvasItem", true, false)
		for ci in items:
			var cb := _count_draw.bind(counts, ci.get_instance_id())
			hooks.append(cb)
			(ci as CanvasItem).draw.connect(cb)
	var started := Time.get_ticks_usec()
	var last := started
	var n := 0
	while Time.get_ticks_usec() - started < int(_perf_s * 1000000.0):
		if _tick.is_valid():
			_tick.call(_warmup + n)
		await get_tree().process_frame
		if gen != _gen:
			return
		var now := Time.get_ticks_usec()
		times.append((now - last) / 1000.0)
		last = now
		n += 1
		root_gpu += RenderingServer.viewport_get_measured_render_time_gpu(root_rid)
		var c := RenderingServer.viewport_get_measured_render_time_cpu(root_rid) + RenderingServer.get_frame_setup_time_cpu()
		var vps := _live_viewports()
		subs = maxi(subs, vps.size())
		for v in vps:
			var rid := v.get_viewport_rid()
			RenderingServer.viewport_set_measure_render_time(rid, true)
			var g := RenderingServer.viewport_get_measured_render_time_gpu(rid)
			sub_gpu += g
			if v is CityView3D:
				city_gpu += g
			c += RenderingServer.viewport_get_measured_render_time_cpu(rid)
		cpu += c
		draws += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
		prims += Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	if _census:
		var rows: Array = []
		for i in items.size():
			if is_instance_valid(items[i]):
				(items[i] as CanvasItem).draw.disconnect(hooks[i])
				var k: int = counts.get(items[i].get_instance_id(), 0)
				if k > 0:
					rows.append([k, items[i]])
		rows.sort_custom(func(x: Array, y: Array) -> bool: return x[0] > y[0])
		for r in rows.slice(0, CENSUS_TOP):
			var nd: Node = r[1]
			print("CENSUS tier=%d screen=%s draws=%d of %d frames: %s (%s)" % [_tier, screen, r[0], n, String(nd.get_path()).right(90), _cls(nd) if _cls(nd) != "" else nd.get_class()])
	var fn := float(maxi(1, n))
	var total := 0.0
	var worst := 0.0
	for t in times:
		total += t
		worst = maxf(worst, t)
	var sorted := times.duplicate()
	sorted.sort()
	var p95: float = sorted[mini(sorted.size() - 1, int(sorted.size() * 0.95))] if not sorted.is_empty() else 0.0
	var rec := {
		"screen": screen, "tier": _tier, "window": [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
		"frames": n, "frame_mean_ms": total / fn, "frame_p95_ms": p95, "frame_max_ms": worst,
		"gpu_total_ms": (root_gpu + sub_gpu) / fn, "gpu_root_ms": root_gpu / fn, "gpu_city3d_ms": city_gpu / fn,
		"gpu_sub_ms": sub_gpu / fn, "subviewports": subs, "render_cpu_ms": cpu / fn,
		"draws": draws / fn, "prims": prims / fn,
		"vmem_mb": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0,
		"tex_mb": Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0,
	}
	# The hitches: frames over the 60 fps frame (when, in s from the timing's start, and how long).
	var spikes := PackedStringArray()
	var at := 0.0
	for t in times:
		at += t / 1000.0
		if t > SPIKE_MS and spikes.size() < MAX_SPIKES:
			spikes.append("%.2fs:%.0f" % [at, t])
	rec["spikes"] = spikes
	_write_json(out_dir.path_join(screen + ".perf.json"), rec)
	if not spikes.is_empty():
		print("SPIKES tier=%d screen=%s %s" % [_tier, screen, " ".join(spikes)])
	print("PERF tier=%d screen=%s frames=%d frame_mean_ms=%.2f frame_p95_ms=%.2f frame_max_ms=%.1f gpu_total_ms=%.2f gpu_root_ms=%.2f gpu_city3d_ms=%.2f gpu_sub_ms=%.2f subs=%d cpu_ms=%.2f draws=%.0f prims=%.0f vmem_mb=%.0f window=%s" % [
		_tier, screen, n, rec["frame_mean_ms"], p95, worst, rec["gpu_total_ms"], rec["gpu_root_ms"], rec["gpu_city3d_ms"],
		rec["gpu_sub_ms"], subs, rec["render_cpu_ms"], rec["draws"], rec["prims"], rec["vmem_mb"],
		str(DisplayServer.window_get_size())])


# --- The profile's own screens ---------------------------------------------------------

## A boss run's netrun scene on its HQ-run page (not entered).
func _boss_route() -> Node:
	RunManager.new_campaign(5)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	for e in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
		if not c.exploits.has(e):
			c.exploits.append(e)
	var boss_site: SiteData = null
	for sd in corp.city_grid.sites:
		if CampaignRules.run_kind_for(c, sd) == "boss":
			boss_site = sd
			break
	if boss_site == null:
		push_error("perf_pack: no boss site")
		return null
	RunManager._ensure_resolver()
	RunManager.netrun = NetrunSession.start_special(RunManager.resolver, c, c.living_operatives()[0].id, "boss", boss_site.id,
		boss_site.tier, c.campaign_seed, corp.final_boss.id, CampaignRules.boss_overrides(c, corp), corp)
	RunManager.run_changed.emit(RunManager.netrun)
	var net: Node = _open(NETRUN)
	await _frames(2)
	await _until(func() -> bool: return net.arrival_ready(), "the HQ run page")
	await _until(func() -> bool:
		var v: HqRunView = net.hq_run_view
		return v != null and v.city != null and v.city.model != null, "the compound's city")
	await _settle(net)
	return net


func _s_hq_run() -> void:
	await _boss_route()


func _s_hq_run_gate() -> void:
	var net: Node = await _boss_route()
	if net == null:
		return
	net.open_gate(RunManager.netrun.available_nodes()[0])
	await _settle(net)


## The boss fight dressed as arena_lab's worst fixture (every slot docked on both wheels,
## firmware in every slot, every Daemon, the dock bloomed, a card hovered).
func _worst() -> Control:
	var combat := await _boss_fight()
	if combat == null:
		return null
	var engine = combat.engine
	var st: CombatState = engine.state()
	var lookup: ContentLookup = engine.resolver.lookup
	var boss := st.enemies[0]
	for i in st.player.wheel.slice_count:
		if st.satellite_at(st.player.id, i) == null:
			_dock(st, st.player, lookup.get_content(ARENA_LAB.DRONE) as EnemyData, i)
	for i in boss.wheel.slice_count:
		if st.satellite_at(boss.id, i) == null:
			_dock(st, boss, lookup.get_content(ARENA_LAB.SAT_TEMPLATES[i % ARENA_LAB.SAT_TEMPLATES.size()]) as EnemyData, i)
	for i in st.player.wheel.slice_count:
		st.player.wheel.slot_firmware_ids[i] = ARENA_LAB.FIRMWARE[i % ARENA_LAB.FIRMWARE.size()]
	for i in boss.wheel.slice_count:
		boss.wheel.slot_firmware_ids[i] = ARENA_LAB.FIRMWARE[(i + 2) % ARENA_LAB.FIRMWARE.size()]
	st.daemon_ids.clear()
	for d in ARENA_LAB.DAEMONS:
		st.daemon_ids.append(d)
	st.hand[0] = ARENA_LAB.SPIN_CARD
	combat._refresh(st)
	for v in combat._views():
		v.attachments.dock.force_bloom = true
	combat._preview_card(0)
	await _settle(combat.get_parent())
	_combat = combat
	return combat


## arena_lab's `_dock` (a satellite docked on `owner`'s slot `slot`).
func _dock(st: CombatState, owner: CombatantState, data: EnemyData, slot: int) -> void:
	if data == null:
		return
	var d := EffectInterpreter.make_combatant(data, StringName("%s_lab_%d" % [owner.id, slot]), true)
	d.is_player = owner.is_player
	d.host_id = owner.id
	d.dock_slot = slot
	d.hp = maxi(1, d.max_hp - slot % 3)
	if d.wheel != null:
		d.wheel.rotation = (slot * 7) % RC.TICKS
	if owner.is_player:
		st.drones.append(d)
	else:
		st.enemies.append(d)


func _s_combat_worst() -> void:
	await _worst()


func _s_combat_worst_fx() -> void:
	var combat := await _worst()
	if combat == null:
		return
	_tick = _fx_volley


## Every FX_EVERY frames: a Perfect burst and a precision landing on every wheel, a damage
## number and a hit line from the player's wheel to the boss's.
func _fx_volley(frame: int) -> void:
	if _combat == null or not is_instance_valid(_combat) or frame % FX_EVERY != 0:
		return
	var fx: CombatFxLayer = _combat.fx_layer
	var views: Array = _combat._views()
	var k := frame / FX_EVERY
	for v: WheelView in views:
		if _fx_precision:
			v.play_precision(k % 3, k % 6, 0)
		if fx != null:
			fx.wheel_burst(v.global_center(), v.disc_radius(), CombatFxLayer.BURST_PERFECT)
	if fx != null and views.size() >= 2:
		var a: Vector2 = (views[0] as WheelView).global_center()
		var b: Vector2 = (views[1] as WheelView).global_center()
		fx.hit_line(a, b, Palette.HARM, "12", "")
		fx.number(b, "-12", Palette.HARM, &"number_float", Vector2.UP, k % 2 == 0)


func _s_combat_worst_bare() -> void:
	var combat := await _worst()
	if combat == null:
		return
	for v: WheelView in combat._views():
		v.visible = false
	if combat.fx_layer != null:
		combat.fx_layer.visible = false
	await _frames(4)


func _s_combat_worst_probe() -> void:
	var combat := await _worst()
	if combat == null:
		return
	var parts: Array[CanvasItem] = []
	for n in combat.get_children():
		if n is CanvasItem:
			parts.append(n)
	for v: WheelView in combat._views():
		for n in v.find_children("*", "CanvasItem", true, false):
			if n.get_parent() == v or n.get_parent().get_parent() == v:
				parts.append(n)
	# What redraws: every CanvasItem's draw count over one probe window.
	var counts := {}
	var items: Array[Node] = combat.find_children("*", "CanvasItem", true, false)
	var hooks: Array[Callable] = []
	for ci in items:
		var cb := _count_draw.bind(counts, ci.get_instance_id())
		hooks.append(cb)
		(ci as CanvasItem).draw.connect(cb)
	var whole := await _probe_ms()
	for i in items.size():
		if is_instance_valid(items[i]):
			(items[i] as CanvasItem).draw.disconnect(hooks[i])
	var frames := int(PROBE_S * 1000.0 / maxf(0.1, whole))
	for ci in items:
		var k: int = counts.get(ci.get_instance_id(), 0)
		if is_instance_valid(ci) and k > frames / 4:
			print("PROBE redraws=%d of ~%d frames: %s class=%s" % [k, frames, combat.get_path_to(ci), _cls(ci) if _cls(ci) != "" else ci.get_class()])
	print("PROBE whole frame_ms=%.2f" % whole)
	for p in parts:
		if not is_instance_valid(p) or not p.visible:
			continue
		p.visible = false
		var ms := await _probe_ms()
		p.visible = true
		print("PROBE hidden=%s class=%s frame_ms=%.2f saves_ms=%.2f" % [combat.get_path_to(p), _cls(p) if _cls(p) != "" else p.get_class(), ms, whole - ms])


## B1a: the HQ page's frame with its UiScrimPools layer shown and hidden (one PROBE line each).
func _s_scrim_probe_hq() -> void:
	var hq: Node = await _hq_with_campaign()
	await _settle(hq)
	await _scrim_probe(hq)


## B1a: the route page's frame with its UiScrimPools layer shown and hidden.
func _s_scrim_probe_route() -> void:
	await _s_route()
	await _scrim_probe(get_tree().current_scene if get_tree().current_scene != null else self)


## B1a b: a fight's frame with its UiScrimPools layer shown and hidden.
func _s_scrim_probe_combat() -> void:
	await _s_combat_start()
	await _scrim_probe(get_tree().root)


func _scrim_probe(root: Node) -> void:
	var scrims: Array[Node] = root.find_children("*", "UiScrimPools", true, false)
	if scrims.is_empty():
		scrims = get_tree().root.find_children("*", "UiScrimPools", true, false)
	# Shown, hidden, shown again (the mean of the two shown windows: less drift).
	var whole := await _probe_ms()
	for s in scrims:
		(s as CanvasItem).visible = false
	var bare := await _probe_ms()
	for s in scrims:
		(s as CanvasItem).visible = true
	whole = (whole + await _probe_ms()) * 0.5
	for s in scrims:
		(s as UiScrimPools).keep_enabled = false
	var no_keep := await _probe_ms()
	for s in scrims:
		(s as UiScrimPools).keep_enabled = true
	print("PROBE scrim layers=%d frame_ms=%.2f without=%.2f costs_ms=%.2f no_keep=%.2f keep_costs_ms=%.2f" % [scrims.size(), whole, bare,
		whole - bare, no_keep, whole - no_keep])


func _s_scrim_luma_combat_start() -> void:
	await _s_combat_start()
	await _scrim_luma("combat_start")


func _s_scrim_luma_combat_aiming() -> void:
	await _s_combat_aiming()
	await _scrim_luma("combat_aiming")


func _s_scrim_luma_hq() -> void:
	await _s_hq()
	await _scrim_luma("hq")


func _s_scrim_luma_raid_setup() -> void:
	await _s_raid_setup()
	await _scrim_luma("raid_setup")


func _s_scrim_luma_route() -> void:
	await _s_route()
	await _scrim_luma("route")


## B1a b: the world under the screen's scrim with its pools and bands hidden (raw) and shown (on),
## the UI and the lifted map hidden; prints the measured ratios (and the scrim maths' on the raw
## frame), and writes the raw frame and the scrim's sources as a fixture (<out>/fixtures/).
func _scrim_luma(screen: String) -> void:
	var scrim: UiScrimPools = null
	var best := -1
	for n in get_tree().root.find_children("*", "UiScrimPools", true, false):
		var s := n as UiScrimPools
		if s == null or not s.is_visible_in_tree():
			continue
		s.refresh()
		if s.shapes.size() > best:
			best = s.shapes.size()
			scrim = s
	if scrim == null:
		push_error("perf_pack: no scrim on %s" % screen)
		return
	for i in 6:
		await get_tree().process_frame
	scrim.refresh()
	var src := scrim.sources()
	scrim.hold_shapes = true
	var hidden: Array[CanvasItem] = []
	for sib in scrim.get_parent().get_children():
		var ci := sib as CanvasItem
		if ci != null and ci.get_index() > scrim.get_index() and ci.visible:
			hidden.append(ci)
	for ci in scrim.lifted:
		if is_instance_valid(ci) and ci.visible:
			hidden.append(ci)
	for ci in hidden:
		ci.visible = false
	scrim.spill.visible = false
	scrim.visible = false
	var raw := await _grab_luma()
	scrim.visible = true
	var on := await _grab_luma()
	scrim.hold_shapes = false
	scrim.spill.visible = true
	for ci in hidden:
		if is_instance_valid(ci):
			ci.visible = true
	var real := ScrimLuma.measure(raw, on, src)
	var model := ScrimLuma.measure(raw, null, src)
	print("PROBE scrim_luma tier=%d screen=%s real: %s" % [_tier, screen, ScrimLuma.line(real)])
	print("PROBE scrim_luma tier=%d screen=%s model: %s" % [_tier, screen, ScrimLuma.line(model)])
	var dir := out_dir.path_join("fixtures")
	DirAccess.make_dir_recursive_absolute(dir)
	raw.save_png(dir.path_join(screen + ".png"))
	on.save_png(dir.path_join(screen + "_on.png"))
	var f := FileAccess.open(dir.path_join(screen + ".json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(ScrimLuma.to_json(src), "\t"))
	f.close()


func _grab_luma() -> Image:
	for i in 3:
		await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.resize(LUMA_SIZE.x, LUMA_SIZE.y, Image.INTERPOLATE_NEAREST)
	return img


## The mean frame time (ms) over PROBE_S seconds after PROBE_WARMUP frames, v-sync off.
func _probe_ms() -> float:
	for i in PROBE_WARMUP:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
		await get_tree().process_frame
	var started := Time.get_ticks_usec()
	var n := 0
	while Time.get_ticks_usec() - started < int(PROBE_S * 1000000.0):
		await get_tree().process_frame
		n += 1
	return (Time.get_ticks_usec() - started) / 1000.0 / maxf(1.0, n)


func _cls(n: Node) -> String:
	var sc: Script = n.get_script()
	return String(sc.get_global_name()) if sc != null else ""


func _count_draw(counts: Dictionary, id: int) -> void:
	counts[id] = int(counts.get(id, 0)) + 1


func _s_combat_worst_redraw() -> void:
	if await _worst() == null:
		return
	_tick = _redraw_views


func _redraw_views(_frame: int) -> void:
	if _combat != null and is_instance_valid(_combat):
		for v: WheelView in _combat._views():
			v.queue_redraw()


func _s_combat_worst_fxlayer() -> void:
	if await _worst() == null:
		return
	_fx_precision = false
	_tick = _fx_volley


func _s_combat_worst_send() -> void:
	if await _worst() == null:
		return
	_tick = _send_once


## SEND IT on the timing's first frame (its warm-up): the replay plays through the timing.
func _send_once(frame: int) -> void:
	if frame == 0 and _combat != null and is_instance_valid(_combat):
		_combat.end_turn()
