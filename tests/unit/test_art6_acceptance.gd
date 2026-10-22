extends GutTest
## M14 ART-6 acceptance (docs/MILESTONES.md "ART-6 — Raid"; DECISIONS 2026-10-11 "M14 ART-6
## acceptance"). Two of its boxes as rules:
## - Reading holds are never shortened at 2x / 4x (R7 C4, STYLE_GUIDE 5.5): every raid reading
##   time in ui_motion.tres (the raid_* HOLD entries and the reading times their views keep on the
##   real clock) holds at least its 1x time with the raid playout's own 2x / 4x buttons pressed.
## - DOWN is the Site markers' white bolt over a greyed marker at every raid zoom, never the amber
##   dashed forecast socket (ruling 11): the raid map's DOWN node across its camera band.
## The looks themselves are captured windowed (tools/design_lab/raid_lab, sheet
## docs/art_review/ART-6/RAID_STATES.jpg).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CITY_CONFIG := preload("res://content/config/city_config.tres")
## The raid's reading times: the raid_* HOLD entries and the reading times kept on the real
## clock (the pencil words write on in real time; RAID INCOMING's stamp is read on the jack
## cover). Each maps to how its view reads it (see _reading_seconds).
const READING: Array[StringName] = [&"raid_mark_hold", &"raid_mark_write", &"raid_breached_write", &"raid_incoming_hold"]
## A pixel of a socket image counts when this opaque (0..1).
const OPAQUE := 0.3
## A greyed marker: at most this share of its opaque pixels is saturated (s > SAT, v > SAT_V).
const GREY_SHARE := 0.02
const SAT := 0.35
const SAT_V := 0.3
## Amber (Palette.WARN, the forecast's dashed DOWN ring): hue band, saturation and value floors.
const AMBER_HUE := Vector2(0.08, 0.16)
const AMBER_SV := 0.5

var cfg: CityConfig = CITY_CONFIG
var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	Motion.set_speed(1.0)
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art6_accept"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


# --- Reading holds at 2x / 4x (R7 C4) ------------------------------------------------------------

## The seconds reading time `id` stays on screen as its raid view reads it now.
func _reading_seconds(id: StringName) -> float:
	match id:
		&"raid_incoming_hold":
			return Fx.note_hold()
		_:
			return RaidFxLayer.mark_seconds(id)


## Presses the raid playout's own speed button for `speed` (RaidPlayoutPanel: 1x / 2x / 4x).
func _press_speed(panel: RaidPlayoutPanel, speed: float) -> void:
	for b in panel.speed_buttons():
		if b.name == "Speed%dx" % int(speed):
			b.pressed.emit()
			return
	fail_test("the raid playout has no %dx button" % int(speed))


func test_every_raid_reading_hold_is_never_shortened_at_2x_and_4x() -> void:
	# Every raid_* HOLD entry is a reading time this test reads.
	var holds := 0
	for e in Motion.config().entries:
		if e != null and String(e.id).begins_with("raid_") and e.kind == UiMotionEntryData.Kind.HOLD:
			holds += 1
			assert_has(READING, e.id, "%s is a raid HOLD: its reading time is checked here" % e.id)
	assert_gt(holds, 0, "the raid has HOLD entries")
	Motion.force_live = true  # the words write on as on a real display (headless writes at once)
	var panel := RaidPlayoutPanel.new()
	add_child_autofree(panel)
	assert_eq(panel.speed_buttons().size(), 3, "the playout offers 1x / 2x / 4x")
	var fx := RaidFxLayer.new()
	autofree(fx)
	var mark := {"kind": "down", "heavy": false, "stays": false}
	var breach := {"kind": "breached", "heavy": true, "stays": true}
	_press_speed(panel, 1.0)
	var at_1x := {}
	for id in READING:
		var e := Motion.entry(id)
		assert_not_null(e, "%s is in ui_motion.tres" % id)
		at_1x[id] = _reading_seconds(id)
		assert_gt(float(at_1x[id]), 0.0, "%s: read at 1x" % id)
	var mark_1x := fx.mark_length(mark)
	var breach_1x := fx.mark_length(breach)
	for speed in [2.0, 4.0]:
		_press_speed(panel, speed)
		assert_almost_eq(Motion.speed, speed, 0.0001, "%dx is the playout's speed" % int(speed))
		for id in READING:
			var s := _reading_seconds(id)
			assert_true(s >= float(at_1x[id]) - 0.0001, "%dx: %s stays %.2f s, its 1x reading time is %.2f s" % [int(speed), id, s, at_1x[id]])
			assert_true(s >= Motion.entry(id).duration - 0.0001, "%dx: %s never under its raw %.2f s" % [int(speed), id, Motion.entry(id).duration])
		assert_true(fx.mark_length(mark) >= mark_1x - 0.0001, "%dx: a DOWN / TAKEN / INCOMING word is on screen as long as at 1x" % int(speed))
		assert_true(fx.mark_length(breach) >= breach_1x - 0.0001, "%dx: BREACHED writes as slowly as at 1x" % int(speed))
	# Reduce effects: the words show at once, the holds still hold (a reading time).
	_press_speed(panel, 4.0)
	Settings.set_reduce_effects(true)
	assert_almost_eq(_reading_seconds(&"raid_mark_hold"), Motion.entry(&"raid_mark_hold").duration, 0.0001, "reduce effects at 4x: the mark's hold still reads")
	assert_true(Fx.note_hold() >= Motion.entry(&"raid_incoming_hold").duration - 0.0001, "reduce effects at 4x: RAID INCOMING still reads")
	_press_speed(panel, 1.0)


# --- DOWN at every zoom (ruling 11) --------------------------------------------------------------

## A campaign with three claimed nodes, the second one DOWN before the raid, and a raid pending.
## Returns the DOWN node's id.
func _down_campaign() -> StringName:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"vault_terminal", &"relay"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	var ids := c.grid.claimed_ids()
	var down: StringName = ids[1] if ids.size() > 1 else &""
	if down != &"":
		c.grid.sites[down]["condition"] = GridState.Condition.DOWN
		c.grid.sites[down]["integrity"] = 0
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")
	return down


## The share of `img`'s opaque pixels that are saturated, and its amber pixels.
static func _ink(img: Image) -> Vector2:
	var opaque := 0
	var sat := 0
	var amber := 0
	for y in img.get_height():
		for x in img.get_width():
			var p := img.get_pixel(x, y)
			if p.a < OPAQUE:
				continue
			opaque += 1
			if p.s > SAT and p.v > SAT_V:
				sat += 1
			if p.h >= AMBER_HUE.x and p.h <= AMBER_HUE.y and p.s > AMBER_SV and p.v > AMBER_SV:
				amber += 1
	return Vector2(float(sat) / maxf(1.0, opaque), amber)


static func _socket_image(spec: Dictionary) -> Image:
	return Image.load_from_file(ProjectSettings.globalize_path(RaidSocket.DIR + RaidSocket.image_of(spec) + ".png"))


func test_down_is_the_white_bolt_over_a_greyed_marker_at_every_raid_zoom() -> void:
	# The kit: a DOWN socket is the greyed image (every node type), never the amber dashed
	# forecast ring, even when the forecast also says DOWN; the bolt is the Site markers' white.
	assert_eq(Palette.TEXT_HI.s < 0.1 and Palette.TEXT_HI.v > 0.9, true, "the bolt is white")
	for glyph: String in [RaidSocket.GLYPH_RELAY, RaidSocket.GLYPH_FIREWALL, RaidSocket.GLYPH_VAULT, RaidSocket.GLYPH_PROXY,
			RaidSocket.GLYPH_SAFEHOUSE, RaidSocket.GLYPH_COMPILER, RaidSocket.GLYPH_CORE]:
		var down := {"glyph": glyph, "state": RaidSocket.STATE_DOWN, "health": 0.0, "forecast": RaidSocket.STATE_DOWN}
		assert_eq(RaidSocket.image_of(down), glyph + "_down", "%s: DOWN wins over the forecast ring" % glyph)
		var ink := _ink(_socket_image(down))
		assert_true(ink.x <= GREY_SHARE, "%s DOWN: the marker is greyed (%.3f saturated)" % [glyph, ink.x])
		assert_eq(int(ink.y), 0, "%s DOWN: no amber dashed socket" % glyph)
		# The check sees amber where it is: the forecast's dashed DOWN ring.
		var fc := _ink(_socket_image({"glyph": glyph, "forecast": RaidSocket.STATE_DOWN}))
		assert_gt(int(fc.y), 0, "%s: the forecast ring is the amber one" % glyph)
	# The raid map: the DOWN node across the raid camera band.
	var down_id := _down_campaign()
	assert_ne(down_id, &"", "a node is DOWN before the raid")
	var hq := _scene(HQ)
	await get_tree().process_frame
	hq.show_raid()
	await BoundedWait.until(get_tree(), func() -> bool: return hq.city_overlay != null and is_instance_valid(hq.city_overlay), 10.0)
	var ov: CityMapOverlay = hq.city_overlay
	assert_not_null(ov, "the raid map shows")
	if ov == null:
		return
	var n: Dictionary = {}
	for node in ov.nodes:
		if node["id"] == down_id:
			n = node
	assert_true(n.has("socket"), "the DOWN node is a socket on the raid map")
	if not n.has("socket"):
		return
	var city: NeonCity = hq.wireframe.city
	var w: float = hq.size.x
	# The setup's own framing done and its markers laid (they follow the node layer's draw).
	await BoundedWait.until(get_tree(), func() -> bool: return not n.has("marker") or not ov.marker_shown(n) or ov.marker_view(down_id) != null, 10.0)
	# The HQ's own fit (icons as drawn, a Site landmark's roof lifts the marker) settles first: it re-frames the camera
	# for a few frames after the page opens and would take the camera back from the band below.
	await BoundedWait.until(get_tree(), func() -> bool: return not hq._hq_fit_pending, 10.0)
	# The band: the raid's closest fit, its middle, its widest fit, and the widest the setup
	# frames at big text (zoom_ortho_max, HQ fit_hq_map's floor on the raid page).
	var orthos: Array[float] = [cfg.raid_fit_min, (cfg.raid_fit_min + cfg.raid_fit_max) * 0.5, cfg.raid_fit_max, cfg.zoom_ortho_max]
	var bolt_px: Array[float] = []
	for o in orthos:
		var z := RaidZoomFit.zoom_of(o, w)
		hq._frame_city(z, city.focus_grid, city.focus_anchor)
		await get_tree().process_frame
		await get_tree().process_frame
		assert_almost_eq(city.scale.x, z, 0.0001, "ortho %.0f: the camera is there" % o)
		var spec := ov.socket_spec(n)
		assert_eq(String(spec["state"]), RaidSocket.STATE_DOWN, "ortho %.0f: the node draws DOWN" % o)
		assert_eq(RaidSocket.image_of(spec), String(spec["glyph"]) + "_down", "ortho %.0f: the greyed DOWN socket, no forecast ring" % o)
		assert_eq(int(_ink(_socket_image(spec)).y), 0, "ortho %.0f: no amber on the DOWN node" % o)
		assert_true(n.has("marker"), "ortho %.0f: the setup shows the DOWN node's Site marker" % o)
		if n.has("marker"):
			# The setup draws the Site marker v4 over the socket (HQ-B): DOWN greys it whole
			# (its ring too) and its sticker is the DISABLED one under the white bolt.
			var mspec: Dictionary = n["marker"]
			assert_eq(String(mspec["status"]), SiteMarker.ST_DOWN, "ortho %.0f: the Site marker reads DOWN" % o)
			var ring := SiteMarker.greyed(SiteMarker.ring_color(mspec))
			assert_true(ring.s <= SAT, "ortho %.0f: the marker's ring is greyed (s %.2f)" % [o, ring.s])
			assert_false(ring.h >= AMBER_HUE.x and ring.h <= AMBER_HUE.y and ring.s > AMBER_SV, "ortho %.0f: the ring is not amber" % o)
			if ov.marker_shown(n):
				var view := ov.marker_view(down_id)
				assert_not_null(view, "ortho %.0f: the DOWN marker shows" % o)
				if view != null:
					assert_eq(view.sticker.state, VinylSticker.State.DISABLED, "ortho %.0f: the grey sticker under the white bolt" % o)
					assert_almost_eq(view.scale.x * city.scale.x, 1.0, 0.001, "ortho %.0f: the marker is its own size on screen" % o)
		var r := ov.icon_radius(n)
		var bolt := r * RaidSocket.BOLT
		# The bolt (0.62 x its size each way) lies on the socket (the baked image's box).
		assert_true(RaidSocket.rect(Vector2.ZERO, r).grow(-bolt * 0.62).has_area(), "ortho %.0f: the bolt lies on the marker" % o)
		bolt_px.append(bolt * city.scale.x)
	for i in bolt_px.size():
		assert_gt(bolt_px[i], 0.0, "ortho %.0f: the bolt shows" % orthos[i])
		assert_almost_eq(bolt_px[i], bolt_px[0], 0.01, "ortho %.0f: the marker and its bolt are the same size on screen at every zoom" % orthos[i])
