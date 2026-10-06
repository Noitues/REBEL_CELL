extends GutTest
## B5 (M14 integration review D8 / D9 / D10, section f top bar; designer rulings 5 and 6): the netrun's loot, event and
## Mainframe pages.
## - D8 / ruling 6: the loot's title sticker is FIGHT WON (PAYOUT only the terminal's word), the page sits on the
##   fought Site's close-up in its won state with OURS NOW in pencil, and ends on the pink CONTINUE sticker (the same
##   press as taking the lit sticker);
## - D9: the event page sits on the run's Site close-up dimmed with the corp tint; its CAM feed reads that close-up
##   (never an empty box) and at big text shrinks to a strip above the story (never hidden);
## - D10 / ruling 5: DISPATCH is voice only (the red voice trace and the red-accent CRT transcript), never paper;
## - section f: each page's top bar shows only what it is about.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_b5_netrun"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(1)


func _loot(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(4)


func _event(scene: Control, id: StringName) -> void:
	var run := RunManager.netrun.run
	run.event_id = id
	run.phase = RunState.Phase.EVENT
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(4)


func _bar_tags(scene: Control) -> PackedStringArray:
	var out := PackedStringArray()
	for i in scene.hud.stats.items.size():
		out.append(String(scene.hud.stats.items[i][0]))
	return out


# --- D8: loot ----------------------------------------------------------------------------------

func test_the_loot_page_sits_on_the_won_site_and_ends_on_continue() -> void:
	var scene := _netrun()
	await _frames(2)
	await _loot(scene)
	var sb: CombatBackdrop = scene.site_backdrop
	assert_true(sb.visible, "the run's Site close-up behind the loot")
	assert_almost_eq(sb.won, 1.0, 0.001, "in its won state (the district dims, the target's lights in Cell colours)")
	assert_not_null(sb.ours_now(), "OURS NOW in the kit's wax pencil")
	assert_true(sb.ours_now().is_visible_in_tree(), "written on over the won Site")
	assert_false(scene.site_dim.visible, "no event dim on the loot")
	var title := scene._panel.find_child("LootTitle", true, false) as HoloSticker
	assert_ne(title.sticker.text, "PAYOUT", "PAYOUT is the terminal's word, never the title sticker")
	assert_eq(String(scene.hud._title), "", "no bar title over the page's own sticker")
	var go := scene._panel.find_child("Continue", true, false) as HoloSticker
	assert_not_null(go, "the page ends on the CONTINUE sticker verb")
	assert_eq(go.sticker.fill, VinylSticker.Fill.PINK, "the pink verb")
	assert_true(go.sticker.sweep_primary, "the page's one sweep")
	var stickers := scene._panel.find_child("Stickers", true, false) as Control
	var deck_before := RunManager.netrun.run.operative.deck.size()
	(stickers.get_child(1) as Control).grab_focus()
	await _frames(1)
	go.pressed.emit()
	await _frames(2)
	assert_eq(RunManager.netrun.run.operative.deck.size(), deck_before + 1, "CONTINUE takes the lit sticker (the rules' own pick)")
	assert_true(RunManager.netrun.run.operative.deck.has(&"jam"), "the one that held the focus")
	await _close(scene)


func test_loot_words_never_put_payout_on_a_sticker() -> void:
	for w in NetrunScript.LOOT_SOURCES.values():
		assert_false(String(w).contains("PAYOUT"), "%s: a sticker word" % w)
	assert_false(NetrunScript.LOOT_PLAIN.contains("PAYOUT"))


# --- D9 / D10: events ----------------------------------------------------------------------------

func test_the_event_sits_on_the_dimmed_site_and_its_cam_feed_reads_it() -> void:
	var scene := _netrun()
	await _frames(2)
	await _event(scene, &"ev_leash_on_the_floor")
	assert_true(scene.site_backdrop.visible, "the run's Site close-up behind the event")
	assert_true(scene.site_dim.visible, "dimmed")
	var tint := Palette.corp_color(RunManager.campaign.corporation_id)
	var dim: Color = scene.site_dim.color
	assert_lt(maxf(dim.r, maxf(dim.g, dim.b)), 0.6, "to about 40 %")
	var dominant := 0 if tint.r >= tint.g and tint.r >= tint.b else (1 if tint.g >= tint.b else 2)
	assert_eq(dominant, 0 if dim.r >= dim.g and dim.r >= dim.b else (1 if dim.g >= dim.b else 2), "with the corp's tint")
	assert_true(scene.site_copy.visible, "the CAM feed's copy of the close-up (never an empty box)")
	assert_lt(scene.site_copy.get_index(), scene.site_dim.get_index(), "copied before the dim")
	assert_gt(scene.site_copy.get_index(), scene.site_backdrop.get_index(), "after the close-up")
	var feed := scene._panel.find_child("CamFeed", true, false) as CamFeed
	assert_not_null(feed, "the CAM feed")
	assert_false(feed.voice_only)
	assert_null(scene._panel.find_child("EventRun", true, false), "section f: the top bar carries what the choices change (no RUN terminal)")
	await _close(scene)


func test_at_big_text_the_cam_feed_is_a_strip_above_the_story_never_hidden() -> void:
	var scene := _netrun(1.6)
	await _frames(2)
	await _event(scene, &"ev_leash_on_the_floor")
	var feed := scene._panel.find_child("CamFeed", true, false) as CamFeed
	assert_not_null(feed, "never dropped")
	assert_true(feed.is_visible_in_tree(), "shown")
	var text := scene._panel.find_child("EventText", true, false) as Control
	assert_lt(feed.get_global_rect().end.y, text.get_global_rect().position.y + 1.0, "a strip above the story")
	assert_almost_eq(feed.custom_minimum_size.x, NetrunScript.EVENT_CAM_STRIP_W * minf(1.6, NetrunScript.EVENT_CAM_STRIP_GROW), 0.5, "about 160 px wide")
	await _close(scene)


func test_dispatch_is_voice_only_never_paper() -> void:
	var scene := _netrun()
	await _frames(2)
	await _event(scene, &"ev_dispatch_early_reply")
	assert_null(_find_class(scene._panel, "CorpMemo"), "no memo paper (D10)")
	var feed := scene._panel.find_child("CamFeed", true, false) as CamFeed
	assert_not_null(feed, "the voice panel")
	assert_true(feed.voice_only, "VOICE ONLY // NO FEED: the red voice trace")
	var holder := scene._panel.find_child("EventPanel", true, false) as CrtWindow
	assert_eq(holder.glass.accent_kind, CrtTerminalPanel.Accent.DISPATCH, "the transcript in the red-accent CRT")
	var text := scene._panel.find_child("EventText", true, false) as RichTextLabel
	assert_eq(text.get_theme_font(&"normal_font"), Palette.mono(), "typed on in the terminal's mono, never Courier on paper")
	await _close(scene)


func _find_class(root: Node, cls: String) -> Node:
	for n in root.find_children("*", "", true, false):
		if n.get_script() != null and (n.get_script() as Script).get_global_name() == cls:
			return n
	return null


# --- section f: the top bar per page ------------------------------------------------------------

func test_each_netrun_page_bar_shows_only_what_it_is_about() -> void:
	var scene := _netrun()
	await _frames(3)
	assert_eq(_bar_tags(scene), PackedStringArray(["HP", "CYCLES"]), "the route: HP and Cycles (with the Heat gauge)")
	assert_true(scene.hud.heat_gauge.visible, "the Heat gauge on every page (designer ruling Q1)")
	assert_true(scene.hud.loadout_button.visible, "the rest behind VIEW LOADOUT")
	await _loot(scene)
	assert_eq(_bar_tags(scene), PackedStringArray(["CARDS"]), "the loot: the deck (a card is on offer)")
	await _event(scene, &"ev_leash_on_the_floor")
	var want := NetrunScript.event_bar_keys(RunManager.netrun)
	assert_eq(Array(_bar_tags(scene)), want, "an event: what its choices change")
	assert_true(want.has("CYCLES"), "this one's choices pay Cycles")
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()
	await _frames(3)
	assert_eq(_bar_tags(scene), PackedStringArray(["CYCLES"]), "the Mainframe: Cycles")
	await _close(scene)
