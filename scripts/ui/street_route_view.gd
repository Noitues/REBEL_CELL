class_name StreetRouteView
extends Control
## NA-23: the street netrun route page. The city seen at street level (`RouteRig`: the netrun camera, the route's rooms, the 7.1
## occlusion), the grease-pencil overlay (`StreetRouteOverlay`), the hover power cut (a 2D grade with a branch mask, 9.4) and the
## input: number keys select an option, Z flips OVERVIEW / DECISION, Enter confirms, Esc lets go of a hover / selection, then
## leaves OVERVIEW, then asks for the pause menu; the mouse hovers (HOVER lights the node's tag and cuts power to the rest) and a
## click selects, with an explicit confirm. Signal Up: it only emits what the player chose; the screen enters the node.
## Headless and under reduce effects every camera move and ease lands at once.

## The pointer is over node `id` ("" = none).
signal node_hovered(id: String)
## An option was selected (click or number key).
signal node_selected(id: String)
## The selected option was confirmed (Enter, the confirm button of the host, `confirm()`).
signal node_confirmed(id: String)
## Esc with nothing left to back out of: the host opens the pause menu.
signal pause_requested
## The base view (OVERVIEW / DECISION) or HOVER changed.
signal view_changed(view: int)
## The rig finished drawing the city.
signal ready_to_show

var rig: RouteRig = null
var overlay: StreetRouteOverlay = null
var data: StreetRouteData = null
## The Bloom look last put on the street ({} before the first call; strength 0 when off).
var bloom: Dictionary = {}
## OVERVIEW or DECISION (`StreetRouteRules.View`); HOVER is derived (`current_view`).
var base_view: int = StreetRouteRules.View.DECISION
## The node under the pointer ("" = none) and the selected option ("" = none).
var hover_id := ""
var selected_id := ""
## id -> the tag shown on hover (the screen fills it: kind word, Heat). Empty = the kind word.
var tag_text: Callable = Callable()

var _state: Dictionary = {"current": "", "visited": [], "options": []}
var _hit: Control = null
var _toggle_dec: Button = null
var _toggle_box: Control = null
var _toggle_ov: Button = null
var _mask_img: Image = null
var _mask_tex: ImageTexture = null
var _hover_k := 0.0
var _hover_to := 0.0
var _hover_from := 0.0
var _hover_t := 1.0
var _hover_dur := 0.0
var _branch: Array = []
var _last_focus := ""
var _dec_state: Dictionary = {}
var _lit_all := false
## NA-25: true while the entry sequence (`EntryCover`) drives the camera and the overlay; the view takes no input then.
var entry_active := false
var _entry_occ_on := true
## NA-25b: the rooms stay open through the entry (the Grid / Route zoom reuses the dive; only the REVEAL builds the rooms up).
var _entry_rooms_open := false


## The data of the run `session` on the game's city, or a data object with `error` set. The city model is the shared one (built on
## this thread when no scene has built it yet).
static func build_data(session: NetrunSession, corp: CorporationData) -> StreetRouteData:
	var cfg := CityView3D.CONFIG
	var model := CityModel.shared(cfg, CityPlan.current_seed())
	return StreetRouteData.build(session, model, cfg, CityLayout.site_points(corp))


## Builds the view for `p_data`; call once, after adding to the tree. `current` / `visited` / `options` are the run's position.
func setup(p_data: StreetRouteData, model: CityModel, current: String, visited: Array, options: Array) -> void:
	data = p_data
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	rig = RouteRig.new()
	rig.name = "Rig"
	add_child(rig)
	rig.setup(data, model)
	rig.prepared.connect(func() -> void: ready_to_show.emit())
	overlay = StreetRouteOverlay.new()
	overlay.name = "Overlay"
	add_child(overlay)
	overlay.bind(rig, data)
	_hit = Control.new()
	_hit.name = "Hit"
	_hit.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_hit.mouse_filter = Control.MOUSE_FILTER_STOP
	_hit.gui_input.connect(_on_hit_input)
	_hit.mouse_exited.connect(_on_mouse_exit)
	add_child(_hit)
	_build_toggle()
	var ms := float(StreetRouteConfigData.shipped().hover["mask_scale"])
	_mask_img = Image.create(maxi(2, int(size.x * ms)), maxi(2, int(size.y * ms)), false, Image.FORMAT_L8)
	_mask_tex = ImageTexture.create_from_image(_mask_img)
	_apply_grade_uniforms()
	resized.connect(_on_resized)
	set_run_state(current, visited, options, false)
	_on_resized()


func _cfg() -> StreetRouteConfigData:
	return StreetRouteConfigData.shipped()


func _instant() -> bool:
	return DisplayServer.get_name() == "headless" or Settings.reduce_effects


func _build_toggle() -> void:
	var box := HBoxContainer.new()
	box.name = "ViewToggle"
	_toggle_box = box
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	box.offset_left = -300.0
	box.offset_top = -52.0
	box.offset_right = -24.0
	box.offset_bottom = -12.0
	add_child(box)
	_toggle_dec = Button.new()
	_toggle_dec.name = "ToggleDecision"
	_toggle_dec.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # the text is translated once, here
	_toggle_dec.text = tr("DECISION")
	_toggle_dec.toggle_mode = true
	_toggle_dec.pressed.connect(set_base_view.bind(StreetRouteRules.View.DECISION))
	box.add_child(_toggle_dec)
	_toggle_ov = Button.new()
	_toggle_ov.name = "ToggleOverview"
	_toggle_ov.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_toggle_ov.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_toggle_ov.text = tr("OVERVIEW")
	_toggle_ov.toggle_mode = true
	_toggle_ov.tooltip_text = tr("Z flips between OVERVIEW and DECISION.")
	_toggle_ov.pressed.connect(set_base_view.bind(StreetRouteRules.View.OVERVIEW))
	box.add_child(_toggle_ov)
	_sync_toggle()


func _sync_toggle() -> void:
	if _toggle_dec == null:
		return
	_toggle_dec.set_pressed_no_signal(base_view == StreetRouteRules.View.DECISION)
	_toggle_ov.set_pressed_no_signal(base_view == StreetRouteRules.View.OVERVIEW)


func _on_resized() -> void:
	if rig == null:
		return
	var kk := size.y / float(_cfg().frame["ref_h"])
	var f := _cfg().frame
	overlay.usable = Rect2(Vector2(float(f["left_px"]) * kk, float(f["top_px"]) * kk),
		Vector2(size.x - (float(f["left_px"]) + float(f["right_px"])) * kk, size.y - (float(f["top_px"]) + float(f["bottom_px"])) * kk))
	overlay.mark_dirty()
	var ms := float(_cfg().hover["mask_scale"])
	var want := Vector2i(maxi(2, int(size.x * ms)), maxi(2, int(size.y * ms)))
	if _mask_img != null and Vector2i(_mask_img.get_size()) != want:
		_mask_img = Image.create(want.x, want.y, false, Image.FORMAT_L8)
		_mask_tex = ImageTexture.create_from_image(_mask_img)
		_apply_grade_uniforms()


func _apply_grade_uniforms() -> void:
	var g := rig.grade()
	var h: Dictionary = _cfg().hover
	g.set_shader_parameter(&"mask", _mask_tex)
	g.set_shader_parameter(&"k", _hover_k)
	g.set_shader_parameter(&"cut_level", float(h["cut_level"]))
	g.set_shader_parameter(&"cut_desat", float(h["cut_desat"]))
	g.set_shader_parameter(&"branch_boost", float(h["branch_boost"]))
	if _mask_img != null:
		g.set_shader_parameter(&"mask_texel", Vector2(1.0 / float(_mask_img.get_width()), 1.0 / float(_mask_img.get_height())))
		var ms := float(h["mask_scale"])
		g.set_shader_parameter(&"blur", float(h["blur_px"]) * ms / 1.0)


# --- State ------------------------------------------------------------------------------------

## The run's position changed (a node was walked): the DECISION on the new current, a clean selection.
func set_run_state(current: String, visited: Array, options: Array, animate: bool = true) -> void:
	_state = {"current": current, "visited": visited.duplicate(), "options": options.duplicate()}
	overlay.state = _state
	selected_id = selected_id if options.has(selected_id) else ""
	hover_id = hover_id if hover_id == "" or data.rooms().has(hover_id) else ""
	_dec_state = data.decision_state(current, options)
	_refresh_tags()
	_refresh(animate, rig.t_step_seconds())


## LOOK Solace Bloom A (A-096; look only): the Bloom's look on the street, read from the run's `BloomState` `b` (a disabled Bloom, so any
## other corporation, gives the off look). Called after each node entry and fight end. Returns the look it set.
func set_bloom(b: BloomState, campaign_cfg: CampaignConfigData) -> Dictionary:
	bloom = BloomLook.from_state(b, BloomLook.street_layout(data.derive), campaign_cfg)
	if rig != null and rig.view != null:
		rig.view.set_bloom(bloom)
	return bloom


## The current run position `{current, visited, options}`.
func run_state() -> Dictionary:
	return _state


## The node the view shows in detail: the pointer's, else the selected option ("" = none).
func focus_id() -> String:
	return hover_id if hover_id != "" else selected_id


## OVERVIEW, DECISION or HOVER (`StreetRouteRules.View`).
func current_view() -> int:
	var f := focus_id()
	return StreetRouteRules.view_for(base_view, f != "" and (_state["options"] as Array).has(f))


## Sets the base view (the toggle, Z): moves the camera over `rig.t_zoom`.
func set_base_view(v: int) -> void:
	if v == base_view:
		_sync_toggle()
		return
	base_view = v
	_sync_toggle()
	_refresh(true, rig.t_zoom_seconds())
	view_changed.emit(current_view())


## Selects option `id` (a click, a number key); ignored for a node that is not an option.
func select(id: String) -> void:
	if not (_state["options"] as Array).has(id):
		return
	selected_id = id
	overlay.selected = id
	_refresh(true, rig.t_hover_in_seconds())
	node_selected.emit(id)


## Confirms the selected option (Enter, the host's confirm button).
func confirm() -> void:
	if selected_id != "" and (_state["options"] as Array).has(selected_id):
		node_confirmed.emit(selected_id)


## The legend hover lights the whole graph (D7).
func set_lit_all(on: bool) -> void:
	_lit_all = on
	overlay.lit_all = on
	overlay.mark_dirty()


# --- Camera and look --------------------------------------------------------------------------

func _refresh_tags() -> void:
	var t: Dictionary = {}
	for id: String in data.rooms().keys():
		if tag_text.is_valid():
			t[id] = String(tag_text.call(id))
		else:
			t[id] = CityMapOverlay.kind_word(overlay.kind_name(id))
	overlay.tags = t


func _target_state() -> Dictionary:
	var f := focus_id()
	if base_view == StreetRouteRules.View.OVERVIEW:
		return data.overview_state()
	if f != "" and (_state["options"] as Array).has(f):
		return data.hover_state(_dec_state, f)
	return _dec_state


## The camera pose, the occlusion and the grade for the current view.
func _refresh(animate: bool, seconds: float) -> void:
	var st := _target_state()
	var f := focus_id()
	rig.move_to(st["pose"], seconds if animate else 0.0)
	rig.set_occlusion(st["rec"])
	_branch = StreetRouteRules.branch_of(data.run_graph, f) if f != "" else []
	var cur := String(_state["current"])
	if cur != "" and f != "" and not _branch.has(cur):
		_branch.append(cur)
	overlay.focus = f
	overlay.branch = _branch
	overlay.selected = selected_id
	overlay.mark_dirty()
	_set_hover_target(1.0 if f != "" else 0.0)
	_sync_energies()
	if f != _last_focus:
		_last_focus = f
		node_hovered.emit(hover_id)


func _sync_energies() -> void:
	for id: String in rig.room_ids():
		rig.set_room_open(id, true)
		rig.set_room_energy(id, _room_energy(id))


## The energy room `id` rests at: lit for the options, the hovered branch and the current room, else idle.
func _room_energy(id: String) -> float:
	var rc: Dictionary = _cfg().rooms
	var options: Array = _state["options"]
	var on: bool = options.has(id) or _branch.has(id) or id == String(_state["current"])
	return float(rc["energy_lit"]) * float(_cfg().hover["type_glow"]) if on else float(rc["energy_idle"])


func _set_hover_target(to: float) -> void:
	if is_equal_approx(to, _hover_to) and _hover_t >= 1.0:
		return
	_hover_from = _hover_k
	_hover_to = to
	var rg := NetrunArtConfigData.shipped().rig
	_hover_dur = float(rg["t_hover_in"]) if to > _hover_k else float(rg["t_hover_out"])
	_hover_t = 0.0
	if _instant():
		_hover_k = to
		_hover_t = 1.0
		_push_grade()


func _process(delta: float) -> void:
	if rig == null:
		return
	if _hover_t < 1.0:
		_hover_t = minf(1.0, _hover_t + delta / maxf(_hover_dur, 0.001))
		_hover_k = lerpf(_hover_from, _hover_to, NetrunCameraRig.ease(_hover_t))
		_push_grade()
	elif _hover_k > 0.0 or _hover_to > 0.0:
		_update_mask()
	elif rig.moving():
		pass


func _push_grade() -> void:
	rig.grade().set_shader_parameter(&"k", _hover_k)
	_update_mask()


## The branch's room boxes (and the current room's), grown by `hover.grow_px`, on the mask (white = lit).
func _update_mask() -> void:
	if _hover_k <= 0.0 and _hover_to <= 0.0:
		return
	_mask_img.fill(Palette.INK.darkened(1.0))
	var ms := float(_cfg().hover["mask_scale"])
	var grow := float(_cfg().hover["grow_px"]) * size.y / float(_cfg().frame["ref_h"])
	for id: Variant in _branch:
		var box := rig.room_box_px(String(id)).grow(grow)
		if box.size == Vector2.ZERO:
			continue
		var r := Rect2i(Vector2i((box.position * ms).floor()), Vector2i((box.size * ms).ceil()))
		_mask_img.fill_rect(r.intersection(Rect2i(Vector2i.ZERO, _mask_img.get_size())), Palette.NO_TINT)
	_mask_tex.update(_mask_img)


# --- Input ------------------------------------------------------------------------------------

func _on_hit_input(ev: InputEvent) -> void:
	if entry_active:
		return
	if ev is InputEventMouseMotion:
		var id := overlay.node_at((ev as InputEventMouseMotion).position)
		_set_hover(id)
	elif ev is InputEventMouseButton:
		var mb := ev as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			var id := overlay.node_at(mb.position)
			if id != "":
				if (_state["options"] as Array).has(id):
					select(id)
				accept_event()


func _on_mouse_exit() -> void:
	_set_hover("")


func _set_hover(id: String) -> void:
	if id == hover_id:
		return
	hover_id = id
	_refresh(true, rig.t_hover_in_seconds() if focus_id() != "" else rig.t_hover_out_seconds())


func _unhandled_key_input(event: InputEvent) -> void:
	if entry_active or not is_visible_in_tree() or not (event is InputEventKey):
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo:
		return
	var opt := StreetRouteRules.option_for_key(k.keycode, _state["options"])
	if opt != "":
		select(opt)
		get_viewport().set_input_as_handled()
		return
	match k.keycode:
		KEY_Z:
			set_base_view(StreetRouteRules.toggled(base_view))
			get_viewport().set_input_as_handled()
		KEY_ENTER, KEY_KP_ENTER:
			if selected_id != "":
				confirm()
				get_viewport().set_input_as_handled()
		KEY_ESCAPE:
			_escape(true)


## What Esc does (`StreetRouteRules.esc_action`); `consume` marks the key handled when the view used it.
func _escape(consume: bool = false) -> int:
	var act := StreetRouteRules.esc_action(base_view, focus_id() != "")
	match act:
		StreetRouteRules.Esc.CLEAR_FOCUS:
			selected_id = ""
			hover_id = ""
			_refresh(true, rig.t_hover_out_seconds())
		StreetRouteRules.Esc.BACK_TO_DECISION:
			set_base_view(StreetRouteRules.View.DECISION)
		StreetRouteRules.Esc.PAUSE:
			pause_requested.emit()
			return act
	if consume and is_inside_tree():
		get_viewport().set_input_as_handled()
	return act


## Test and host entry: the Esc rule without a key event.
func press_escape() -> int:
	return _escape(false)


# --- Entry sequence (NA-25) -------------------------------------------------------------------

## Starts the entry: the view locks its input, shows the OVERVIEW toggle state, and the rooms and overlay go dark (the dive's
## first frame is the HQ page). `EntryCover` drives the `entry_*` calls below and ends with `entry_end`.
func entry_begin(rooms_open: bool = false) -> void:
	entry_active = true
	_entry_rooms_open = rooms_open
	if _toggle_box != null:
		_toggle_box.visible = false
	if _hit != null:
		_hit.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_id = ""
	selected_id = ""
	base_view = StreetRouteRules.View.OVERVIEW
	_sync_toggle()
	overlay.intro = true
	overlay.reveal_s = -1.0
	overlay.mark_s = -1.0
	overlay.reveal_total = Motion.seconds(&"entry_reveal")
	overlay.focus = ""
	overlay.branch = []
	overlay.selected = ""
	_entry_occlusion(false)
	_entry_rooms(func(_layer: int) -> float: return 0.0)
	overlay.mark_dirty()


## The dive at `u` (0 = the HQ page, 1 = the street OVERVIEW; PIPELINE_SPEC 6.3). Without an HQ pose the camera holds the OVERVIEW.
func entry_dive(u: float) -> void:
	overlay.intro = true
	var ov: NetrunPose = data.overview_state()["pose"]
	var hq := data.hq_pose()
	rig.set_pose(NetrunCameraRig.dive_pose(u, hq, ov) if hq != null else ov)
	overlay.reveal_s = -1.0
	overlay.mark_s = -1.0
	_entry_occlusion(false)
	_entry_rooms(func(_layer: int) -> float: return 0.0)
	overlay.mark_dirty()


## REVEAL, `s` seconds in (of `total`): links write on and the rooms come up layer by layer.
func entry_reveal(s: float, total: float) -> void:
	overlay.intro = true
	rig.set_pose(data.overview_state()["pose"])
	_entry_occlusion(true)
	overlay.reveal_s = s
	overlay.reveal_total = total
	overlay.mark_s = -1.0
	var layers := int(data.run_graph["layers"])
	_entry_rooms(func(layer: int) -> float: return EntryBeats.up_k(layer, layers, total, s))
	overlay.mark_dirty()


## MARK, `s` seconds in: the route is drawn whole, the markers come in.
func entry_mark(s: float) -> void:
	overlay.intro = true
	rig.set_pose(data.overview_state()["pose"])
	_entry_occlusion(true)
	overlay.reveal_s = overlay.reveal_total
	overlay.mark_s = s
	_entry_rooms(func(_layer: int) -> float: return 1.0)
	overlay.mark_dirty()


## ZOOM at `u` (0 = OVERVIEW, 1 = DECISION): the camera eases between the two; the toggle flips at the midpoint.
func entry_zoom(u: float) -> void:
	var ov: NetrunPose = data.overview_state()["pose"]
	var dec: Dictionary = _dec_state
	overlay.intro = false
	overlay.reveal_s = overlay.reveal_total
	overlay.mark_s = Motion.seconds(&"entry_mark")
	_entry_occlusion(true)
	rig.set_pose(ov.mix(dec["pose"], NetrunCameraRig.ease(u)))
	var to_dec := u >= 0.5
	var want := StreetRouteRules.View.DECISION if to_dec else StreetRouteRules.View.OVERVIEW
	if want != base_view:
		base_view = want
		_sync_toggle()
		rig.set_occlusion(dec["rec"] if to_dec else data.overview_state()["rec"])
	_entry_rooms(func(_layer: int) -> float: return 1.0)
	overlay.mark_dirty()


## NA-25b: the Grid / Route toggle's one camera ease at `u` (0 = the Grid's framing, the HQ page pose, 1 = the street DECISION): rooms
## open, the street's occlusion on, the overlay whole. Without an HQ pose the camera holds the DECISION.
func entry_toggle(u: float) -> void:
	var dec: Dictionary = _dec_state
	var hq := data.hq_pose()
	overlay.intro = false
	overlay.reveal_s = overlay.reveal_total
	overlay.mark_s = Motion.seconds(&"entry_mark")
	_entry_occlusion(true)
	rig.set_pose(hq.mix(dec["pose"], NetrunCameraRig.ease(u)) if hq != null else dec["pose"])
	var want := StreetRouteRules.View.DECISION
	if want != base_view:
		base_view = want
		_sync_toggle()
		rig.set_occlusion(dec["rec"])
	_entry_rooms(func(_layer: int) -> float: return 1.0)
	overlay.mark_dirty()


## The end state of beat 7 (CHOOSE): DECISION on the current room, input back, the overlay whole. The same whether the beats played
## or were skipped.
func entry_end() -> void:
	entry_active = false
	_entry_rooms_open = false
	if _toggle_box != null:
		_toggle_box.visible = true
	if _hit != null:
		_hit.mouse_filter = Control.MOUSE_FILTER_STOP
	_entry_occ_on = true
	overlay.intro = false
	overlay.reveal_s = -1.0
	overlay.mark_s = -1.0
	base_view = StreetRouteRules.View.DECISION
	_sync_toggle()
	_refresh(false, 0.0)
	overlay.mark_dirty()


## The street's occlusion on (the OVERVIEW's cones, from REVEAL on) or off (the HQ page's full-height city, during the dive).
func _entry_occlusion(on: bool) -> void:
	if on == _entry_occ_on:
		return
	_entry_occ_on = on
	rig.set_occlusion(data.overview_state()["rec"] if on else {"occlusion": {"buildings": []}})


## Rooms at `up_of(layer)` of their resting energy. A room at 0 is closed: its building shows the closed facade (windows and wash),
## never a black box; between 0 and 1 the facade dissolves into the cutaway room (NA-25b; the timeline's `k`, so a skip, a scrub and the
## jack-out reverse land on the same state); under reduce effects it is open or closed, never between.
func _entry_rooms(up_of: Callable) -> void:
	for id: String in rig.room_ids():
		var k := 1.0 if _entry_rooms_open else float(up_of.call(StreetRouteRules.layer_of(data.run_graph, id)))
		if Settings.reduce_effects:
			rig.set_room_open(id, k > 0.0)
		else:
			rig.set_room_dissolve(id, k)
		rig.set_room_energy(id, _room_energy(id) * k)
