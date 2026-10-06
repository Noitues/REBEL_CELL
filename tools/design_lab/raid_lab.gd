extends Control
## ART-6 3A raid lab (dev tool, never exported): one windowed launch walks every raid state
## the presentation draws and writes a frame per state, for reading next to the references in
## docs/art_reference/raid/. Run only through tools/run_windowed.py (never a bare windowed
## Godot), with APPDATA pointed at a scratch folder (the HQ autosaves its demo campaign there):
##
##   python tools/run_windowed.py --log <file> -- res://tools/design_lab/raid_lab.tscn -- --out=<abs dir>
##       [--states=sheet,setup_solace,...] [--scale=1.0] [--raw] [--size=WxH]
##
## S-MAPVIEW: `--raw` also writes `<state>_raw.png`, the 3D city's own render (its viewport
## texture, before the page draws it), to check the page shows it as rendered (S-ARENA's
## linear-as-sRGB darkening); `--size=WxH` sizes the window (1920x1080 for the frame budget).
##
## States: `sheet` (the kit: sockets, vehicle icons v4, pencil, stickers, paper, holo,
## terminal), `setup_<corp>` (the raid setup against each corporation), `drag_valid`,
## `drag_invalid` (a defence carried over a node), `playout_mark` (a pencil mark in its hold),
## `playout_end`, `report`, `breached_bits` (mid bit burst), `breached`, `saved_stamp` (the autosave stamp on the setup), `uplink_close` (ART-3 6w: a node's uplink pad up close). Writes `<state>.png` (1280x720).

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const ALL := ["sheet", "setup_meridian", "setup_solace", "setup_halcyon", "setup_orbital", "setup_rebel_cell",
	"drag_valid", "drag_invalid", "playout_mark", "playout_end", "report", "breached_bits", "breached", "saved_stamp", "uplink_close"]
## `breached_bits` is caught this far into the bit burst (its share of raid_bits_burst).
const BITS_AT := 0.3
const NODE_TYPES: Array[StringName] = [&"firewall_relay", &"vault_terminal", &"relay", &"safehouse", &"proxy_relay"]
const SETTLE := 40
const WAIT := 900
## ART-3 6w: the `uplink_close` state's camera (ortho BU).
const UPLINK_CLOSE_ORTHO := 90.0

var out_dir := ""
var raw := false
var states: Array = ALL
var _hq: Node = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--states="):
			states = Array(a.trim_prefix("--states=").split(","))
		elif a.begins_with("--scale="):
			Settings.text_scale = float(a.trim_prefix("--scale="))
		elif a == "--raw":
			raw = true
		elif a.begins_with("--size="):
			var wh := a.trim_prefix("--size=").split("x")
			DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	DirAccess.make_dir_recursive_absolute(out_dir)
	_run.call_deferred()


func _run() -> void:
	for s: String in states:
		print("raid_lab: state %s" % s)
		if s == "sheet":
			await _sheet()
		else:
			await _screen(s)
		await _shot(s)
		_clear()
	print("raid_lab: done")
	get_tree().quit(0)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _until(cond: Callable, limit: int = WAIT) -> bool:
	for i in limit:
		if cond.call():
			return true
		await get_tree().process_frame
	print("raid_lab: waited %d frames" % limit)
	return false


func _shot(state: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	if raw and _hq != null and is_instance_valid(_hq) and _hq.wireframe.city.view3d != null:
		var city: NeonCity = _hq.wireframe.city
		var r := city.cover_rect()
		print("raid_lab: RAW %s cover %s at %s view %s" % [state, r, city.get_global_transform_with_canvas() * r.position,
			city.view3d.size])
		img.save_png(out_dir.path_join(state + "_full.png"))
		city.view3d.get_texture().get_image().save_png(out_dir.path_join(state + "_raw.png"))
		# The city alone (the network decal off for a frame): what the map's marks sit on.
		var net := city.view3d.network
		city.view3d.set_network(null)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		city.view3d.get_texture().get_image().save_png(out_dir.path_join(state + "_city_raw.png"))
		city.view3d.set_network(net)
	if img.get_width() != 1280:
		img.resize(1280, 720, Image.INTERPOLATE_LANCZOS)
	img.save_png(out_dir.path_join(state + ".png"))


func _clear() -> void:
	if _hq != null and is_instance_valid(_hq):
		_hq.queue_free()
	_hq = null
	for c in get_children():
		c.queue_free()
	Motion.set_speed(1.0)


# --- Screens -----------------------------------------------------------------------------------

## A campaign against `corp` with five claimed nodes of every type (a turret, an ICE lock and
## an operative on them), weak spots so a raid takes and downs nodes, and a raid queued.
func _campaign(corp_id: StringName, home_integrity: int = -1, defended: bool = true, weak: bool = false) -> void:
	var p := RunManager.profile
	for u in [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital", &"unlock_rebel_cell"]:
		if not p.unlocks.has(u):
			p.unlocks.append(u)
	RunManager.new_campaign(7, corp_id)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 500
	var claimed := 0
	var guard := 0
	while claimed < NODE_TYPES.size() and guard < 20:
		guard += 1
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, NODE_TYPES[claimed])
		claimed += 1
	print("raid_lab: %s, %d nodes claimed" % [corp.id, c.grid.claimed_ids().size()])
	var ids := c.grid.claimed_ids()
	if defended and ids.size() > 1:
		c.armory = [&"turret", &"ice_lock", &"decoy", &"turret"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, ids[1])
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, ids[1])
	for id in ids:
		if id != c.grid.home_site_id and (c.grid.node_type_of(id) == &"vault_terminal" or weak):
			c.grid.sites[id]["integrity"] = 2  # weak nodes: DOWN, then TAKEN
		if id != c.grid.home_site_id and c.grid.node_type_of(id) == &"safehouse" and not c.living_operatives().is_empty():
			CampaignRules.station(c, RunManager.lookup(), c.living_operatives()[0].id, id)
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "raid lab")


func _open_raid(corp_id: StringName, home_integrity: int = -1, defended: bool = true, weak: bool = false) -> Node:
	_hq = HQ.instantiate()
	add_child(_hq)
	await _frames(2)
	_campaign(corp_id, home_integrity, defended, weak)
	_hq.show_raid()
	await _until(func() -> bool: return _hq.arrival_ready())
	# ART-3 6w: the raid is on the 3D city: its model built and every chunk placed.
	await _until(func() -> bool:
		var v: CityView3D = _hq.wireframe.city.view3d
		return v == null or (v.model != null and not v.is_processing()))
	await _frames(SETTLE)
	print("raid_lab: CAM ortho %.0f uplinks %d" % [RaidZoomFit.ortho_of(_hq.wireframe.city.scale.x, _hq.size.x),
		_hq.wireframe.city.view3d.uplink_count() if _hq.wireframe.city.view3d != null else -1])
	return _hq


func _screen(state: String) -> void:
	if state.begins_with("setup_"):
		await _open_raid(StringName(state.trim_prefix("setup_")))
		return
	match state:
		"drag_valid", "drag_invalid":
			var hq: Node = await _open_raid(&"halcyon")
			hq._demo_drag("drag_asset" if state == "drag_valid" else "drag_asset_refuse")
			await _until(func() -> bool: return hq.drops.mode == DropLayer.Mode.CARRY)
			await _frames(17)  # the pointer at the target, before the release
		"playout_mark":
			var hq: Node = await _open_raid(&"meridian", -1, false, true)
			hq.fight_raid()
			await _until(func() -> bool:
				var fx: RaidFxLayer = hq.playout.fx if hq.playout != null else null
				if fx == null:
					return false
				for m in fx._marks:
					var pr := fx.mark_progress(m)
					if m["kind"] in ["down", "taken"] and pr.x >= 1.0 and pr.y <= 0.0:
						return true
				return false, 3000)
		"playout_end":
			var hq: Node = await _open_raid(&"meridian", -1, false, true)
			hq.fight_raid()
			await _frames(4)
			hq.playout.skip_to_end()
			await _frames(30)
		"report":
			var hq: Node = await _open_raid(&"halcyon")
			hq.fight_raid()
			await _frames(4)
			hq.show_raid_summary()
			await _frames(90)
		"uplink_close":
			# ART-3 6w: a close look at the uplink pads (the concept's pad and risers) on the city.
			var hq: Node = await _open_raid(&"halcyon")
			var nodes: Array[Dictionary] = hq.raid_uplink_nodes()
			var view: CityView3D = hq.wireframe.city.view3d
			if not nodes.is_empty() and view != null:
				var pads := RaidUplinkPads.of(view.model, view.cfg, nodes)
				var big := 0
				for k in pads.size():
					if float(pads[k]["half"]) > float(pads[big]["half"]):
						big = k
				var at: Vector2 = Vector2(pads[big]["lot"]) + Vector2(0.5, 0.5) if not pads.is_empty() else Vector2(nodes[0]["lot"])
				hq._raid_passes = hq.RAID_PASSES_MAX  # the page's framing passes are over: the close-up stays
				hq._frame_city(RaidZoomFit.zoom_of(UPLINK_CLOSE_ORTHO, hq.size.x), at, Vector2(0.45, 0.8))
				await _frames(SETTLE)
				for p in pads:
					var px: Vector2 = view.project(p["centre"]) / Vector2(view.size) * hq.size
					print("raid_lab: PAD %s top %.1f half %.2f at %s" % [p["id"], p["top"], p["half"], px.round()])
		"saved_stamp":
			await _open_raid(&"solace")
			Fx.show_saved()
			await _frames(4)  # placed a frame after the save, then stamped down
		"breached_bits":
			var hq: Node = await _open_raid(&"solace", 2, false)
			hq.fight_raid()
			await _until(func() -> bool:
				var fx: RaidFxLayer = hq.playout.fx if hq.playout != null else null
				if fx == null or fx._breach_t0 == INF:
					return false
				return fx.clock >= fx._breach_t0 + RaidBeats.raw_seconds(RaidFxLayer.BREACH_BITS) * BITS_AT, 3000)
		"breached":
			var hq: Node = await _open_raid(&"solace", 2, false)
			hq.fight_raid()
			await _until(func() -> bool:
				var fx: RaidFxLayer = hq.playout.fx if hq.playout != null else null
				if fx == null:
					return false
				for m in fx._marks:
					if m["kind"] == "breached" and fx.mark_progress(m).x >= 1.0:
						return true
				return false, 3000)
			await _frames(10)


# --- The kit sheet -----------------------------------------------------------------------------

func _sheet() -> void:
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var canvas := Control.new()
	canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	canvas.draw.connect(_draw_sheet.bind(canvas))
	add_child(canvas)
	var paper := RaidPaper.new(&"meridian", "MANIFEST AUDIT", RaidPaper.STAMP_INTERCEPTED, "WO 52-MF-114")
	paper.set_sub("RAID INCOMING  //  WO 52-MF-114")
	paper.add_row("TARGET", "CORE (HOME)")
	paper.add_row("UNITS", "6 IN 1 WAVE")
	paper.add_row("IF IT RAN NOW", "HOME 50 > 41", Palette.HARM_INK)
	paper.position = Vector2(900, 20)
	paper.size = Vector2(360, 0)
	add_child(paper)
	var holo := RaidHolo.new(&"halcyon", "THREAT INTEL // SCAN", "7F-A2")
	holo.add_line("BAILIFF + INSPECTOR", Palette.AUTO, UiTheme.BODY)
	holo.add_line("> weakest node  //  Permit Queue Server")
	holo.body.add_child(RaidIntelStrip.new(&"halcyon", [{"type": RaidVehicle.HEAVY, "name": "BAILIFF", "letter": "A1"}, {"type": RaidVehicle.FAST, "name": "INSPECTOR", "letter": "A2"}]))
	holo.position = Vector2(900, 330)
	holo.size = Vector2(360, 0)
	add_child(holo)
	var term := RaidTerminal.new("YOUR NETWORK", Palette.NET_CYAN)
	term.position = Vector2(540, 470)
	term.size = Vector2(340, 120)
	for row in [["CORE (home)", "HOME -8", Palette.CELL_PINK], ["FIREWALL RELAY", "HOLDS", Palette.GAIN], ["VAULT TERMINAL", "DOWN", Palette.WARN]]:
		var h := HBoxContainer.new()
		var l := Label.new()
		l.text = String(row[0])
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		h.add_child(l)
		h.add_child(RaidChip.new(String(row[1]), row[2]))
		term.body.add_child(h)
	add_child(term)
	var start := RaidSticker.new("START DEFENSE", UiTheme.HEADING, RaidSticker.PINK)
	start.position = Vector2(560, 620)
	add_child(start)
	var holds := RaidSticker.new("CELL HOLDS", UiTheme.DISPLAY, RaidSticker.YELLOW, -6.0)
	holds.position = Vector2(860, 610)
	add_child(holds)
	var strip := RaidSpeedStrip.new(30)
	strip.position = Vector2(20, 670)
	add_child(strip)
	await _frames(20)


func _draw_sheet(ci: Control) -> void:
	var r := 15.0
	var states_row := [
		{"glyph": "relay"}, {"glyph": "firewall"}, {"glyph": "vault"}, {"glyph": "proxy"}, {"glyph": "safehouse"}, {"glyph": "core"},
		{"glyph": "relay", "health": 0.6}, {"glyph": "relay", "health": 0.25}, {"glyph": "relay", "state": "down", "health": 0.0},
		{"glyph": "relay", "state": "taken"}, {"glyph": "relay", "forecast": "down"}, {"glyph": "relay", "forecast": "taken"},
		{"glyph": "relay", "dock": "valid"}, {"glyph": "relay", "dock": "invalid"},
	]
	for i in states_row.size():
		var c := Vector2(40 + (i % 7) * 70, 40 + (i / 7) * 70)
		RaidSocket.draw(ci, c, r, states_row[i])
	var corps := RaidSkin.CORPS
	var types := [RaidVehicle.FAST, RaidVehicle.HEAVY, RaidVehicle.SPECIAL]
	for ci_i in corps.size():
		for t in types.size():
			RaidVehicle.draw(ci, Vector2(40 + ci_i * 58, 190 + t * 56), 12.0, types[t], corps[ci_i])
	for h in 5:
		RaidVehicle.draw(ci, Vector2(340 + h * 54, 190), 12.0, RaidVehicle.HEAVY, &"halcyon", 1.0 - h * 0.25)
	RaidVehicle.draw(ci, Vector2(340, 250), 12.0, RaidVehicle.FAST, &"meridian", 0.8, [RaidVehicle.STATUS_SLOWED])
	RaidVehicle.draw(ci, Vector2(400, 250), 12.0, RaidVehicle.FAST, &"meridian", 0.6, [RaidVehicle.STATUS_FROZEN])
	RaidVehicle.draw(ci, Vector2(460, 250), 12.0, RaidVehicle.FAST, &"meridian", 1.0, [], -PI * 0.25)
	var red := RaidSkin.pencil_threat()
	var yellow := RaidSkin.pencil_plan()
	RaidPencil.word(ci, "INCOMING", Vector2(110, 370), 26, red)
	RaidPencil.word(ci, "TAKEN", Vector2(280, 370), 26, red, 0.6)
	RaidPencil.word(ci, "DOWN", Vector2(420, 370), 26, red, 1.0, 0.5)
	RaidPencil.word(ci, "BREACHED", Vector2(200, 440), 48, red, 1.0, 0.0, -0.05, true, 1.0)
	RaidPencil.arrow(ci, PackedVector2Array([Vector2(30, 500), Vector2(200, 480), Vector2(320, 540)]), red, 4.5)
	RaidPencil.arrow(ci, PackedVector2Array([Vector2(30, 560), Vector2(200, 540), Vector2(320, 600)]), red, 4.5, 1.0, 3, true)
	RaidPencil.circle(ci, Vector2(400, 520), 32, 22, red, 4.5)
	RaidPencil.circle(ci, Vector2(480, 520), 32, 22, yellow, 4.5)
	RaidPencil.cross(ci, Vector2(400, 590), 14, red, 5.0)
	RaidPencil.tick(ci, Vector2(470, 590), 22, yellow, 4.0)
