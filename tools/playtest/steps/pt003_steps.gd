extends Node
## PT-003 scripted steps (dev tool, windowed only through tools/run_windowed.py):
## `-- --out=<abs dir>` drives the real game through the 19 steps of
## docs/playtest/PT-003_plan-1-waves-3-to-5-city-clarity.md section 2 in ONE run, saves screenshots per step to
## <out>/step_<n>/ and writes <out>/steps.json (step id, where, action, adjusted PASS sentence, shots, machine facts).
## Judged afterwards by tools/playtest/steps_judge.py (Message Batches API). Steps the script cannot drive are marked SKIP.
## Where a UI gesture has a public method that the gesture calls (select_card, open_reward, _on_dropped...), the method
## is used and the step's "action" says so. `--only=2,3` runs just those steps.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const FACT_TEXTS_CAP := 50

var out: String = ""
var holder: Control
var steps: Array = []
var cur: Dictionary = {}
var only: PackedStringArray = PackedStringArray()


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
		elif a.begins_with("--only="):
			only = a.substr(7).split(",")
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "pt003_steps"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	_skip("1", "Options", "Reduce effects OFF, text 1.0",
		"(setup) Options at text 1.0, reduce effects OFF.",
		"SKIP (setup step with nothing to look at; the script runs at the defaults: text 1.0, reduce effects off)")
	await _run("2", _s2)
	await _run("3", _s3)
	await _run("4", _s4)
	await _run("5", _s5)
	await _run("6", _s6)  # also records steps 7 and 8
	await _run("9", _s9)
	await _run("10", _s10)
	await _run("11", _s11)  # also records step 12
	await _run("13", _s13)
	await _run("14", _s14)
	await _run("15", _s15)
	await _run("16", _s16)
	await _run("17", _s17)
	await _run("18", _s18)
	await _run("19", _s19)
	if not only.is_empty() and FileAccess.file_exists(out.path_join("steps.json")):
		# A partial re-run replaces just its own steps in the existing file.
		var old: Variant = JSON.parse_string(FileAccess.get_file_as_string(out.path_join("steps.json")))
		var ran := {}
		for s in steps:
			ran[str(s["id"])] = true
		if old is Dictionary:
			for s in old["steps"]:
				if not ran.has(str(s["id"])):
					steps.append(s)
	steps.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return int(a["id"]) < int(b["id"]))
	var f := FileAccess.open(out.path_join("steps.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify({"steps": steps}, "  "))
	f.close()
	RunManager.delete_save()
	get_tree().quit()


func _run(id: String, fn: Callable) -> void:
	if not only.is_empty() and not only.has(id):
		return
	await fn.call()


# --- bookkeeping ---------------------------------------------------------------------------

func _begin(id: String, where: String, action: String, pass_when: String) -> void:
	cur = {"id": id, "where": where, "action": action, "pass_when": pass_when, "shots": [], "facts": {}, "status": "RAN"}
	DirAccess.make_dir_recursive_absolute(out.path_join("step_" + id))


func _end() -> void:
	steps.append(cur)
	cur = {}


func _skip(id: String, where: String, action: String, pass_when: String, why: String) -> void:
	steps.append({"id": id, "where": where, "action": action, "pass_when": pass_when, "shots": [], "facts": {}, "status": why})


func _fact(k: String, v: Variant) -> void:
	cur["facts"][k] = v


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	await _frames(3)
	var rel := "step_%s/%s.png" % [cur["id"], shot_name]
	get_viewport().get_texture().get_image().save_png(out.path_join(rel))
	cur["shots"].append(rel)


## `count` frames, one every `every` frames, composed into one contact sheet (4 columns of 640x360).
func _strip(shot_name: String, count: int, every: int) -> void:
	var imgs: Array[Image] = []
	for i in count:
		await _frames(every)
		var im := get_viewport().get_texture().get_image()
		im.resize(640, 360, Image.INTERPOLATE_BILINEAR)
		imgs.append(im)
	var cols := 4
	var rows := ceili(float(count) / cols)
	var sheet := Image.create(640 * cols, 360 * rows, false, imgs[0].get_format())
	for i in imgs.size():
		sheet.blit_rect(imgs[i], Rect2i(Vector2i.ZERO, Vector2i(640, 360)), Vector2i((i % cols) * 640, (i / cols) * 360))
	var rel := "step_%s/%s.png" % [cur["id"], shot_name]
	sheet.save_png(out.path_join(rel))
	cur["shots"].append(rel)
	_fact("strip_%s" % shot_name, "%d frames, one every %d game frames, left to right then down" % [count, every])


func _fresh(seed_value: int) -> void:
	if holder != null:
		holder.queue_free()
		holder = null
		await _frames(3)
	RunManager.reset()
	RunManager.new_campaign(seed_value)
	holder = Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)


func _mount(path: String) -> Control:
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _hover_at(p: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = p
	m.global_position = p
	Input.warp_mouse(p)
	get_viewport().push_input(m)


func _click_at(p: Vector2) -> void:
	_hover_at(p)
	for down in [true, false]:
		var e := InputEventMouseButton.new()
		e.position = p
		e.global_position = p
		e.button_index = MOUSE_BUTTON_LEFT
		e.pressed = down
		get_viewport().push_input(e)


func _action(action_name: String) -> void:
	for down in [true, false]:
		var e := InputEventAction.new()
		e.action = action_name
		e.pressed = down
		Input.parse_input_event(e)


## Visible Label / Button texts under `root` (optionally those containing one of `needles`, case-insensitive).
func _texts(root: Node, needles: PackedStringArray = PackedStringArray()) -> Array:
	var res: Array = []
	if root == null:
		return res
	var stack: Array[Node] = [root]
	while not stack.is_empty() and res.size() < FACT_TEXTS_CAP:
		var n: Node = stack.pop_back()
		for ch in n.get_children():
			stack.append(ch)
		if not (n is Label or n is BaseButton or n is RichTextLabel) or not (n as Control).is_visible_in_tree():
			continue
		var t := ""
		if n is RichTextLabel:
			t = (n as RichTextLabel).get_parsed_text()
		else:
			t = String(n.get("text"))
		t = t.strip_edges().replace("\n", " / ")
		if t == "":
			continue
		if not needles.is_empty():
			var hit := false
			for nd in needles:
				if t.to_lower().contains(nd.to_lower()):
					hit = true
			if not hit:
				continue
		if not res.has(t):
			res.append(t)
	return res


func _advance(steps_n: int) -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	for i in steps_n:
		var open := CampaignRules.launchable_sites(c, corp, cfg)
		if open.is_empty():
			return
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(c, open[0])
		CampaignRules.on_run_completed(c, corp, cfg, run, RunManager.lookup())


func _claim_some(n_max: int) -> void:
	var c := RunManager.campaign
	var n := 0
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.status_of(sid) == GridState.SiteStatus.CLEARED and n < n_max:
			c.grid.sites[sid]["status"] = GridState.SiteStatus.CLAIMED
			n += 1


func _tag_names(hq: Control) -> Array:
	var ids: Array = []
	for i in hq.city_overlay.tagged_ids():
		ids.append(String(i))
	return ids


func _strs(a: Array) -> Array:
	var r: Array = []
	for i in a:
		r.append(String(i))
	return r


func _alive(c: CampaignState) -> int:
	var n := 0
	for o in c.roster:
		if o.alive:
			n += 1
	return n


# --- steps ---------------------------------------------------------------------------------

func _s2() -> void:
	_begin("2", "Title -> NEW RUN -> HQ (seeded new campaign, HQ Grid)", "Look at the City Grid at rest; hover one Reachable Site; hover the map key",
		"At rest no Site carries a name tag; the Reachable Sites are ringed (orange) so you can tell where to go first; hovering a Reachable Site shows its name tag; hovering the map key shows every tag.")
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(90)
	await _shot("1_rest")
	_fact("tagged_ids_at_rest", _tag_names(hq))
	var reach: Array = []
	var target: StringName = &""
	for n in hq.city_overlay.nodes:
		if n.has("marker") and String(n["marker"].get("avail", "")) == "next":
			reach.append(String(n["id"]))
			if target == &"":
				target = n["id"]
	_fact("reachable_site_ids", reach)
	if target == &"":
		target = hq.city_overlay.nodes[1]["id"]
	var r: Rect2 = hq._map_node_rect(target)
	_hover_at(r.get_center())
	await _frames(40)
	_hover_at(r.get_center() + Vector2(1, 1))
	await _frames(40)
	await _shot("2_hover_site")
	_fact("hovered_site", String(target))
	_fact("tagged_ids_on_hover", _tag_names(hq))
	if hq.hq_legend != null and hq.hq_legend.fold_button != null:
		var kr: Rect2 = hq.hq_legend.fold_button.get_global_rect()
		_hover_at(kr.get_center())
		await _frames(40)
		_hover_at(kr.get_center() + Vector2(1, 1))
		await _frames(60)
	await _shot("3_hover_key")
	_fact("tagged_ids_on_key_hover", _tag_names(hq))
	_hover_at(Vector2(5, 5))
	_end()


func _locked_site(hq: Control) -> SiteData:
	var corp := RunManager.corporation
	for s in corp.city_grid.sites:
		if s != null and hq.lock_line(s) != "":
			return s
	return null


func _s3() -> void:
	_begin("3", "HQ Grid", "Hover a locked Site, then click it (select_site, what the click calls)",
		"Hover or select says what to clear first ('LOCKED: clear X first'); that prerequisite Site gets a double ring and CLEAR FIRST, and the view pans so it is on screen.")
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(90)
	var locked := _locked_site(hq)
	if locked == null:
		_fact("error", "no locked site found")
		_end()
		return
	_fact("locked_site", String(locked.id))
	_fact("lock_line", hq.lock_line(locked))
	var r: Rect2 = hq._map_node_rect(locked.id)
	_hover_at(r.get_center() if r.has_area() else Vector2(640, 360))
	await _frames(100)
	_hover_at(r.get_center() + Vector2(1, 1))
	await _frames(60)
	await _shot("1_hover_locked")
	_fact("tagged_ids_on_hover", _tag_names(hq))
	_fact("texts_on_hover", _texts(hq, PackedStringArray(["locked", "clear first"])))
	hq.select_site(locked.id)
	await _frames(70)
	await _shot("2_selected_locked")
	_fact("selected_site", String(hq.selected_site))
	_fact("texts_selected", _texts(hq, PackedStringArray(["locked", "clear first", "clear"])))
	_hover_at(Vector2(5, 5))
	_end()


func _s4() -> void:
	_begin("4", "HQ Grid", "Select a runnable Site (Heat 22); then one where clearing crosses a raid line",
		"The Site file's FLATLINE row shows 'HEAT +N -> T' on one line and the raid line it crosses sits under it.")
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(60)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var open: SiteData = CampaignRules.launchable_sites(c, corp, cfg)[0]
	c.heat = 22
	hq.select_site(open.id)
	await _frames(70)
	await _shot("1_runnable_heat22")
	_fact("site", String(open.id))
	_fact("texts_heat22", _texts(hq, PackedStringArray(["flatline", "heat", "raid"])))
	var found := false
	for h in range(15, 80):
		for s in CampaignRules.launchable_sites(c, corp, cfg):
			c.heat = h
			var pv := CampaignRules.clear_preview(c, corp, cfg, s, RunManager.lookup())
			if bool(pv.get("raid", false)):
				found = true
				hq.select_site(s.id)
				await _frames(70)
				await _shot("2_raid_line")
				_fact("raid_line_at_heat", h)
				_fact("raid_line_site", String(s.id))
				_fact("texts_raid_line", _texts(hq, PackedStringArray(["flatline", "heat", "raid"])))
				break
		if found:
			break
	_fact("raid_line_found", found)
	_end()


func _s5() -> void:
	_begin("5", "HQ -> CORE (HOME SERVER card) at 0 Schematics", "Select the home Site (the CORE card)",
		"Heat Scrub is disabled and a line gives the reason; the card's text does not clip.")
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(60)
	var c := RunManager.campaign
	c.heat = 0
	c.schematics = 0
	hq.select_site(c.grid.home_site_id)
	await _frames(70)
	await _shot("1_core_card")
	var scrub := hq.find_child("CoreHeatScrub", true, false) as BaseButton
	_fact("scrub_found", scrub != null)
	if scrub != null:
		_fact("scrub_disabled", scrub.disabled)
	var why := hq.find_child("CoreHeatScrubWhy", true, false) as Label
	_fact("scrub_why_text", why.text if why != null else "(none)")
	_end()


## Steps 6, 7 and 8 share the route map.
func _s6() -> void:
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(70)
	var s := RunManager.netrun
	s.run.operative.hp = maxi(1, s.run.operative.max_hp - 7)
	nr._show_map()
	await _frames(40)
	# --- 7: badges, key strip, a node file
	_begin("7", "Route map", "Read the badges and the key strip; open a node file (click a node)",
		"Each node type has its own sticker shape or icon (type reads from the node itself); the node file shows 'HP: n / max on arrival' and where you heal.")
	await _shot("1_route_badges")
	_fact("available_nodes", _strs(s.available_nodes()))
	var b := nr._panel.find_child("Node1", true, false) as Button
	_fact("node1_button_found", b != null)
	if b != null:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.pressed = true
		b.gui_input.emit(click)
		b.pressed.emit()
	await _frames(60)
	await _shot("2_node_file")
	_fact("texts_node_file", _texts(nr, PackedStringArray(["hp", "heal", "arrival"])))
	_fact("operative_hp", "%d/%d" % [s.run.operative.hp, s.run.operative.max_hp])
	_end()
	# --- 6: select only, CONFIRM travels
	_begin("6", "JACK IN -> route map", "Click a node (select), then CONFIRM (confirm_route_node)",
		"The click only selects (the node file shows, the run has not moved); CONFIRM travels.")
	_fact("current_node_before", String(s.run.current_node_id))
	_fact("route_selected_after_click", String(nr.route_selected()))
	_fact("texts_confirm_button", _texts(nr, PackedStringArray(["confirm"])))
	var sel_before: StringName = nr.route_selected()
	await _shot("1_selected_not_travelled")
	_fact("moved_after_click_only", s.run.current_node_id == sel_before and sel_before != &"")
	nr.confirm_route_node()
	await _frames(20)
	await _shot("2_confirm_mid_travel")
	await _frames(120)
	await _shot("3_after_confirm")
	_fact("selected_node", String(sel_before))
	_fact("current_node_after_confirm", String(s.run.current_node_id))
	_fact("travelled_on_confirm", s.run.current_node_id == sel_before and sel_before != &"")
	_end()
	# --- 6 (Enter): a fresh run, select then Enter
	await _fresh(1)
	nr = _mount(NETRUN)
	nr.start_run(1)
	await _frames(60)
	s = RunManager.netrun
	var av: Array = s.available_nodes()
	if not av.is_empty():
		nr.select_route_node(av[0])
		await _frames(30)
		_action("ui_accept")
		await _frames(120)
		steps[steps.size() - 1]["facts"]["enter_key_travelled"] = s.run.current_node_id == av[0]
		steps[steps.size() - 1]["facts"]["enter_key_current_node"] = String(s.run.current_node_id)
		get_viewport().get_texture().get_image().save_png(out.path_join("step_6/4_after_enter.png"))
		steps[steps.size() - 1]["shots"].append("step_6/4_after_enter.png")
	# --- 8: grid view on a fresh run
	_begin("8", "During a run -> GRID VIEW", "Open GRID VIEW (_grid_zoomed + _show_map, what its button does)",
		"The run path and its target are on screen; there are no node choices in GRID VIEW.")
	await _fresh(1)
	nr = _mount(NETRUN)
	nr.start_run(1)
	await _frames(40)
	nr._grid_zoomed = true
	nr._show_map()
	await _frames(300)
	await _shot("1_grid_view")
	var choice_buttons := 0
	for ch in nr._panel.find_children("Node*", "Button", true, false):
		if (ch as Control).is_visible_in_tree():
			choice_buttons += 1
	_fact("visible_node_choice_buttons", choice_buttons)
	_fact("run_target_site", String(RunManager.netrun.run.site_id) if RunManager.netrun != null else "")
	_end()


func _find_fine_tune_scene() -> Control:
	var scene: Control = null
	var idx := -1
	for sd in range(1, 80):
		scene = _mount(COMBAT)
		scene.auto_start = false
		scene.start_fight(&"collections_agent", sd)
		var hand: Array = scene.engine.state().hand
		for i in hand.size():
			if StringName(String(hand[i])) == &"fine_tune":
				idx = i
		if idx >= 0:
			break
		scene.queue_free()
		scene = null
		await _frames(2)
	if scene != null:
		scene.set_meta("idx", idx)
	return scene


func _s9() -> void:
	_begin("9", "Any fight", "Pick Fine Tune (select_card, a multi-play aim); press Q (nudge_left); pick again, press E (nudge_right); pick again, press Esc (ui_cancel); pick again, right-click",
		"Each aim ends cleanly: no aim arrow or aim hint stays and the RAM is unchanged. (Only the card aim could be driven; the free-nudge aim and a target switch were not.)")
	await _fresh(1)
	var scene := await _find_fine_tune_scene()
	scene.skip_motion()
	if scene.tutorial != null and is_instance_valid(scene.tutorial):
		scene.tutorial.queue_free()
		scene.tutorial = null
	await _frames(40)
	var idx: int = int(scene.get_meta("idx"))
	_fact("fine_tune_hand_index", idx)
	var ram0: int = scene.engine.state().ram
	scene.select_card(idx)
	await _frames(25)
	await _shot("1_aiming")
	_fact("aiming_selecting", scene.selecting)
	_fact("aim_options", scene.selection_options().size())
	var keys := {"Q": "nudge_left", "E": "nudge_right", "Esc": "ui_cancel"}
	var n := 2
	for k: String in keys.keys():
		_action(keys[k])
		await _frames(25)
		await _shot("%d_after_%s" % [n, k])
		n += 1
		_fact("after_%s_selecting" % k, scene.selecting)
		_fact("after_%s_ram_delta" % k, scene.engine.state().ram - ram0)
		scene.select_card(idx)
		await _frames(15)
	var rc := InputEventMouseButton.new()
	rc.button_index = MOUSE_BUTTON_RIGHT
	rc.pressed = true
	rc.position = Vector2(640, 360)
	get_viewport().push_input(rc)
	await _frames(25)
	await _shot("%d_after_rightclick" % n)
	_fact("after_rightclick_selecting", scene.selecting)
	_fact("after_rightclick_ram_delta", scene.engine.state().ram - ram0)
	_end()


func _s10() -> void:
	_begin("10", "A fight after a respin or random card", "Play Malware Drop (a random result), press UNDO (rewind, what Z calls)",
		"The message names the random event it stops at ('Nothing to undo since <card> rolled a random result').")
	await _fresh(1)
	var scene := _mount(COMBAT)
	scene.auto_start = false
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	if scene.tutorial != null and is_instance_valid(scene.tutorial):
		scene.tutorial.queue_free()
		scene.tutorial = null
	var st: CombatState = scene.engine.state()
	st.hand[0] = &"malware_drop"
	scene._refresh(st)
	await _frames(30)
	scene.play_card(0)
	scene.skip_motion()
	await _frames(20)
	scene.rewind()
	await _frames(25)
	await _shot("1_undo_blocked")
	_fact("undo_block_text", scene.undo_block_text())
	_fact("texts_on_screen", _texts(scene, PackedStringArray(["undo", "blocked", "random"])))
	_end()


func _s11() -> void:
	_begin("11", "Any fight", "Play Fine Tune; then SEND IT (end_turn); frame strips of the landing and the exchange",
		"The wheel turns as the card lands; damage numbers land on the HP counter; the beams do not overlap; the enemy strikes right after SEND IT.")
	var c12 := {"id": "12", "where": "A fight where you land a PERFECT", "action": "Force a PERFECT landing tag on the player's wheel (play_precision, as p1_combat_capture does) and take a frame strip",
		"pass_when": "The PERFECT tag flies into the hit.", "shots": [], "facts": {}, "status": "RAN"}
	await _fresh(1)
	var scene := await _find_fine_tune_scene()
	if scene.tutorial != null and is_instance_valid(scene.tutorial):
		scene.tutorial.queue_free()
		scene.tutorial = null
	await _frames(40)
	await _shot("1_before")
	scene.play_card(int(scene.get_meta("idx")))
	await _strip("2_card_lands", 8, 5)
	_fact("motion_animating_during_play", Motion.animating())
	# --- 12: forced PERFECT
	var cur11 := cur
	cur = c12
	DirAccess.make_dir_recursive_absolute(out.path_join("step_12"))
	var v: WheelView = scene._player_view
	if "payoff_to" in v:
		v.payoff_to = scene._payoff_point(scene.engine.state())
	v.play_precision(RC.PrecisionTier.PERFECT, 0, 0)
	await _strip("1_perfect_tag", 8, 5)
	_end()
	cur = cur11
	var st0: CombatState = scene.engine.state()
	var hp0: int = st0.enemies[0].hp if not st0.enemies.is_empty() else -1
	scene.end_turn()
	await _strip("3_send_it", 12, 10)
	var st: CombatState = scene.engine.state()
	_fact("enemy_hp_before_send", hp0)
	_fact("enemy_hp_after", st.enemies[0].hp if not st.enemies.is_empty() else -1)
	_fact("player_hp_after", st.player.hp)
	_end()


func _s13() -> void:
	_begin("13", "Win a fight with 2+ picks (rewards set up directly: three picks)", "Open a row and take it (open_reward + choose_reward); open the next and SKIP it (skip_reward); then PROCEED with one left (proceed_rewards)",
		"The list shows every pick; a taken row is marked TAKEN and a skipped row SKIPPED; SKIP skips only that pick; PROCEED with a pick left asks first (a confirm dialog).")
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(10)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.pending_rewards.append({"kind": "firmware", "options": ["leech", "overvolt"]})
	run.pending_rewards.append({"kind": "card", "options": ["twist", "cache"]})
	run.phase = RunState.Phase.REWARD
	nr._show_current()
	await _frames(60)
	await _shot("1_list")
	_fact("picks_at_start", run.pending_rewards.size())
	nr.open_reward(0)
	await _frames(60)
	await _shot("2_row_open")
	nr.choose_reward(0, -1)
	await _frames(60)
	await _shot("3_after_take")
	_fact("picks_after_take", run.pending_rewards.size())
	_fact("texts_after_take", _texts(nr, PackedStringArray(["taken", "skipped", "skip"])))
	nr.open_reward(0)
	await _frames(40)
	nr.skip_reward()
	await _frames(60)
	await _shot("4_after_skip")
	_fact("picks_after_skip", run.pending_rewards.size())
	_fact("texts_after_skip", _texts(nr, PackedStringArray(["taken", "skipped"])))
	nr.proceed_rewards()
	await _frames(40)
	await _shot("5_proceed_asks")
	var dlg := nr.find_child("ProceedConfirm", true, false)
	_fact("proceed_confirm_open", dlg != null)
	_fact("texts_confirm", _texts(dlg))
	_end()


func _s14() -> void:
	_begin("14", "HQ", "Click the Menu button (top left); then click outside the pause menu",
		"Menu opens the pause menu; an outside click closes it; every key prompt (chips) shares one chip look.")
	await _fresh(1)
	var hq := _mount(HQ)
	await _frames(80)
	await _shot("1_hq_menu_button")
	var mb := hq.hud.menu_button as Button
	_fact("menu_button_text", mb.text)
	_click_at(mb.get_global_rect().get_center())
	await _frames(40)
	var opened_by_click: bool = hq._settings_panel != null and is_instance_valid(hq._settings_panel)
	_fact("pause_menu_open_after_pointer_click", opened_by_click)
	if not opened_by_click:
		mb.pressed.emit()
		await _frames(40)
	await _shot("2_menu_open")
	_fact("pause_menu_open", hq._settings_panel != null and is_instance_valid(hq._settings_panel))
	_click_at(Vector2(30, 690))
	await _frames(40)
	await _shot("3_after_outside_click")
	_fact("pause_menu_open_after_outside_click", hq._settings_panel != null and is_instance_valid(hq._settings_panel))
	_end()


func _s15() -> void:
	_begin("15", "HQ with 0 crew alive", "Open CREW; hover JACK IN; press the first FREE HIRE card (recruit)",
		"A FREE HIRE card leads the crew hand; JACK IN is off and says why; hiring makes the crew deployable.")
	await _fresh(7)
	var c := RunManager.campaign
	for op in c.roster:
		op.alive = false
	c.schematics = 0
	var hq := _mount(HQ)
	await _frames(90)
	await _shot("1_hq")
	var tab := hq._panel.find_child("Tab_CREW", true, false) as BaseButton
	if tab != null:
		tab.pressed.emit()
		await _frames(40)
	await _shot("2_crew_tab")
	var cards := hq.find_children("Recover_*", "", true, false)
	_fact("free_hire_cards", cards.size())
	_fact("texts_crew", _texts(hq, PackedStringArray(["hire", "free", "crew"])))
	var jack := hq._panel.find_child("Launch", true, false) as BaseButton
	_fact("jack_in_found", jack != null)
	if jack != null:
		_fact("jack_in_disabled", jack.disabled)
		_fact("jack_in_tooltip", jack.tooltip_text)
		var jr := jack.get_global_rect()
		_hover_at(jr.get_center())
		await _frames(100)
		_hover_at(jr.get_center() + Vector2(1, 1))
		await _frames(60)
		await _shot("3_jack_in_hover")
		_hover_at(Vector2(5, 5))
	_fact("alive_before_hire", _alive(c))
	if not cards.is_empty():
		(cards[0] as BaseButton).pressed.emit()
		await _frames(60)
		await _shot("4_after_hire")
	_fact("alive_after_hire", _alive(c))
	var jack2 := hq._panel.find_child("Launch", true, false) as BaseButton
	_fact("jack_in_disabled_after_hire", jack2.disabled if jack2 != null else "(none)")
	_end()


func _raid_hq() -> Control:
	var c := RunManager.campaign
	_advance(3)
	_claim_some(3)
	c.heat = 30
	CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "capture")
	return _mount(HQ)


func _s16() -> void:
	_begin("16", "HQ -> a raid with nobody stationed -> START DEFENSE", "Open the raid setup (show_raid); press START DEFENSE (request_start_defense)",
		"A warning ('NO CREW STATIONED: N alive, 0 stationed') shows on the setup and START DEFENSE asks first (a confirm dialog) instead of starting.")
	await _fresh(7)
	var hq := _raid_hq()
	await _frames(40)
	var c := RunManager.campaign
	hq.show_raid()
	await _frames(100)
	await _shot("1_setup")
	_fact("raid_crew_warning", CampaignRules.raid_crew_warning(c))
	_fact("alive", _alive(c))
	_fact("stationed", CampaignRules.stationed_count(c))
	_fact("texts_setup", _texts(hq, PackedStringArray(["crew", "stationed", "defense"])))
	hq.request_start_defense()
	await _frames(40)
	await _shot("2_start_defense_asks")
	_fact("defense_confirm_open", hq._defense_confirm != null and is_instance_valid(hq._defense_confirm))
	_fact("raids_pending_after", RunManager.campaign.pending_raids.size())
	_end()


func _s17() -> void:
	_begin("17", "Raid setup", "Drop a defense asset on a claimed node (_on_dropped, the drop handler the drag calls)",
		"The node itself shows the defense (a ring and a pip on the node on the map).")
	await _fresh(7)
	var c := RunManager.campaign
	var hq := _raid_hq()
	await _frames(40)
	hq.show_raid()
	await _frames(100)
	await _shot("1_setup_before")
	var node_id: StringName = &""
	for sid in c.grid.sites.keys():
		if sid != c.grid.home_site_id and c.grid.is_active_node(sid):
			node_id = sid
			break
	node_id = c.grid.home_site_id  # a plain claimed node has no asset slot; the HOME SERVER does
	c.armory.append(&"turret")
	_fact("target_node", String(node_id))
	_fact("assets_on_node_before", c.grid.site(node_id)["assets"].size() if node_id != &"" else -1)
	hq._on_dropped({"kind": "asset", "index": c.armory.size() - 1}, {"kind": "node", "value": node_id})
	await _frames(90)
	await _shot("2_setup_after")
	_fact("assets_on_node_after", c.grid.site(node_id)["assets"].size() if node_id != &"" else -1)
	_end()


func _s18() -> void:
	_begin("18", "Raid report", "Run the raid with START DEFENSE's own call (fight_raid) and open the report (show_raid_summary)",
		"The outcome word matches the stamp; CELL HOLDS is a sticker (not pencil); there are no pencil circles or ticks.")
	await _fresh(3)
	var hq := _raid_hq()
	await _frames(40)
	hq.show_raid()
	await _frames(40)
	RunManager.fight_raid()
	hq.show_raid_summary()
	await _frames(30)
	await _shot("1_report_early")
	await _frames(200)
	await _shot("2_report")
	_fact("texts_report", _texts(hq, PackedStringArray(["holds", "falls", "breach", "fell", "held", "outcome", "raid", "lost"])))
	_end()


func _s19() -> void:
	_begin("19", "Tutorial, then a netrun fight", "Open the stand-alone tutorial (start_tutorial); then enter a fight from a netrun (first campaign, tutorial not done)",
		"The tutorial box shows in the stand-alone tutorial and does not appear in a real netrun fight.")
	var saved_done: bool = Settings.tutorial_done
	Settings.tutorial_done = false
	await _fresh(1)
	var scene := _mount(COMBAT)
	scene.auto_start = false
	scene.start_fight(&"collections_agent", 5)
	scene.start_tutorial()
	await _frames(60)
	await _shot("1_standalone_tutorial")
	_fact("tutorial_in_standalone", scene.tutorial != null and is_instance_valid(scene.tutorial))
	await _fresh(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(40)
	var s := RunManager.netrun
	var fight_id: StringName = &""
	if not s.available_nodes().is_empty():
		fight_id = s.available_nodes()[0]
	_fact("entered_node", String(fight_id))
	nr.enter_node(fight_id)
	await _frames(180)
	await _shot("2_netrun_fight")
	_fact("run_phase", int(s.run.phase))
	var cs: Node = null
	for ch in nr.find_children("*", "", true, false):
		if "tutorial" in ch and "engine" in ch:
			cs = ch
			break
	_fact("combat_scene_found", cs != null)
	if cs != null:
		_fact("tutorial_in_netrun_fight", cs.tutorial != null and is_instance_valid(cs.tutorial))
	Settings.tutorial_done = saved_done
	_end()
