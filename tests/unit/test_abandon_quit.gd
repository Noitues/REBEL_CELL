extends GutTest
## ABANDON-QUIT (designer ruling 2026-10-05, GDD 4.5): the three ways out.
## Abandon run = the operative's death on the run (the same consequences as `_die`, GDD 4.2);
## abandon campaign = the campaign ends ABANDONED (a lost campaign for the profile, the slot
## reads "abandoned"); quit = a save of the exact state, mid-run included, that the title's
## Continue resumes. Each dialog's costs are the rules' preview, and preview == result.

const SLOT := "gut_abandon"

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func before_each() -> void:
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = _cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _start(seed: int = 11, tier: int = 2, campaign: CampaignState = null) -> NetrunSession:
	if campaign == null:
		campaign = _campaign()
	return NetrunSession.start(_resolver, campaign, &"op_1", tier, &"t1_a", seed)


## A run with loot both sides of the bank: Cycles, an unbanked and a banked asset, banked
## Schematics, a card and a Daemon picked up on the run.
func _looted(seed: int = 11) -> NetrunSession:
	var s := _start(seed)
	s.run.cycles = 140
	s.run.unbanked_assets.append(&"turret")
	s.run.banked_assets.append(&"decoy")
	s.run.banked_schematics = 6
	s.run.operative.deck.append(s.run.operative.deck[0])
	var daemons := _resolver.lookup.ids_of_class(&"DaemonData")
	daemons.sort()
	s.run.operative.daemon_ids.append(StringName(daemons[0]))
	return s


# --- Abandon run: the death rule -----------------------------------------------------------------

func test_abandoning_the_run_has_exactly_the_deaths_consequences() -> void:
	var a := _looted()
	var b := _looted()
	var events := a.abandon()
	b._die()
	assert_eq(a.campaign.state_hash(), b.campaign.state_hash(), "the campaign after an abandon is the campaign after a death")
	assert_eq(a.run.outcome, RunState.Outcome.DIED, "the operative is killed (an operative death)")
	assert_true(a.run.is_over())
	assert_false(a.campaign.get_operative(&"op_1").alive, "lost for good")
	assert_eq(a.campaign.deaths, 1)
	assert_false(a.campaign.is_over(), "the campaign goes on")
	assert_eq(String(events[0]["type"]), "run_abandoned", "the run says it was abandoned")


func test_abandon_adds_the_death_heat_and_keeps_only_the_banked_loot() -> void:
	var s := _looted()
	var heat := s.campaign.heat
	var schematics := s.campaign.schematics
	s.abandon()
	assert_eq(s.campaign.heat - heat, _cfg.death_heat_base + s.run.tier, "Heat + %d + tier (GDD 4.2, no new number)" % _cfg.death_heat_base)
	assert_eq(s.campaign.schematics - schematics, 6, "banked Schematics stay; Cycles do not convert")
	assert_true(s.campaign.armory.has(&"decoy"), "a banked asset reaches the Armory")
	assert_false(s.campaign.armory.has(&"turret"), "an unbanked asset is lost")


func test_abandon_mid_fight_ends_the_fight_with_the_run() -> void:
	var s := _start()
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	s.abandon()
	assert_false(s.in_combat(), "the fight ends")
	assert_true(s.run.combat.is_empty(), "no fight is saved with the ended run")
	assert_eq(s.run.outcome, RunState.Outcome.DIED)


func test_an_ended_run_cannot_be_abandoned() -> void:
	var s := _start()
	s.abandon()
	var hash := s.campaign.state_hash()
	var events := s.abandon()
	assert_eq(String(events[-1]["type"]), "refused")
	assert_eq(s.campaign.state_hash(), hash, "nothing changes twice")
	assert_eq(s.abandon_preview(), {}, "no preview once the run is over")


func test_the_abandon_preview_is_the_result() -> void:
	var s := _looted()
	var deck := s.run.operative.deck.size()
	var run_hash := s.state_hash()
	var campaign_hash := s.campaign.state_hash()
	var p := s.abandon_preview()
	assert_eq(s.state_hash(), run_hash, "a preview changes nothing in the run")
	assert_eq(s.campaign.state_hash(), campaign_hash, "nor in the campaign")
	assert_eq(String(p["operative"]), "Vex")
	assert_eq(int(p["cycles"]), 140)
	assert_eq(int(p["assets"]), 1, "one unbanked asset")
	assert_eq(int(p["cards_added"]), 1, "the card picked up on the run")
	assert_eq(int(p["daemons"]), 1, "the Daemon picked up on the run")
	assert_eq(int(p["firmware"]), 0)
	assert_eq(int(p["tier"]), 2)
	var heat := s.campaign.heat
	var schematics := s.campaign.schematics
	var armory := s.campaign.armory.size()
	var raids := s.campaign.pending_raids.size()
	s.abandon()
	assert_eq(int(p["heat"]), s.campaign.heat - heat, "the dialog's Heat is the Heat the abandon adds")
	assert_eq(int(p["heat_after"]), s.campaign.heat)
	assert_eq(int(p["schematics_kept"]), s.campaign.schematics - schematics, "the Schematics kept are those banked")
	assert_eq(int(p["assets_kept"]), s.campaign.armory.size() - armory)
	assert_eq(int(p["raids"]), s.campaign.pending_raids.size() - raids)
	assert_eq(deck, s.run.operative.deck.size(), "the lost deck is the one previewed")


func test_the_preview_heat_follows_the_ice_modifiers_and_the_heat_cap() -> void:
	# Near the cap the death's Heat is what the meter takes, and the preview says so.
	var c := _campaign()
	c.heat = _cfg.heat_max - 3
	var s := _start(11, 2, c)
	var p := s.abandon_preview()
	s.abandon()
	assert_eq(int(p["heat"]), 3, "capped at the meter's top")
	assert_eq(int(p["heat_after"]), s.campaign.heat)
	assert_eq(int(p["raids"]), s.campaign.pending_raids.size(), "a threshold's raid is previewed too")


func test_a_preview_leaves_a_seeded_replay_unchanged() -> void:
	var a := _start(23)
	var b := _start(23)
	for k in 3:
		a.abandon_preview()
		for s in [a, b]:
			var run: NetrunSession = s
			if run.in_combat():
				run.combat_action(CombatAction.end_turn())
			elif run.run.phase == RunState.Phase.MAP and not run.available_nodes().is_empty():
				run.enter_node(run.available_nodes()[0])
	assert_eq(a.state_hash(), b.state_hash(), "the previewed run replays as the plain one")
	assert_eq(a.campaign.state_hash(), b.campaign.state_hash())
	a.abandon()
	b.abandon()
	assert_eq(a.campaign.state_hash(), b.campaign.state_hash(), "an abandon is deterministic")


# --- Abandon campaign ---------------------------------------------------------------------------

func test_abandoning_the_campaign_ends_it_abandoned() -> void:
	var c := _campaign()
	var p := ExitRules.abandon_campaign_preview(c)
	var events := ExitRules.abandon_campaign(c)
	assert_eq(c.outcome, CampaignState.Outcome.ABANDONED)
	assert_true(c.is_over(), "the campaign's own end")
	assert_eq(String(events[0]["type"]), "campaign_abandoned")
	assert_eq(int(p["outcome"]), c.outcome, "preview == result")
	assert_eq(int(p["runs"]), c.runs_completed)
	assert_eq(int(p["heat"]), c.heat)
	assert_eq(int(p["operatives"]), c.living_operatives().size())
	assert_eq(int(p["schematics"]), c.schematics)


func test_a_campaign_is_not_abandoned_twice_nor_under_a_running_netrun() -> void:
	var c := _campaign()
	var hash := c.state_hash()
	assert_eq(String(ExitRules.abandon_campaign(c, true)[0]["type"]), "refused", "a run is in progress")
	assert_eq(c.state_hash(), hash)
	assert_eq(ExitRules.abandon_campaign_preview(c, true), {})
	ExitRules.abandon_campaign(c)
	hash = c.state_hash()
	assert_eq(String(ExitRules.abandon_campaign(c)[0]["type"]), "refused", "already over")
	assert_eq(c.state_hash(), hash)


func test_a_campaign_preview_changes_nothing() -> void:
	var c := _campaign()
	var hash := c.state_hash()
	ExitRules.abandon_campaign_preview(c)
	assert_eq(c.state_hash(), hash)
	assert_false(c.is_over())


# --- Through RunManager (the save, the profile, the slot) ----------------------------------------

func test_run_manager_abandon_run_records_a_death_and_the_campaign_goes_on() -> void:
	RunManager.new_campaign(41)
	RunManager.start_run()
	var lost := RunManager.profile.operatives_lost
	var p := RunManager.abandon_run_preview()
	var heat := RunManager.campaign.heat
	RunManager.abandon_run()
	assert_false(RunManager.has_active_run(), "the run is over")
	assert_true(RunManager.has_campaign(), "the campaign goes on at HQ")
	assert_eq(RunManager.profile.operatives_lost, lost + 1, "an operative death for the profile")
	assert_eq(RunManager.campaign.heat - heat, int(p["heat"]), "preview == result")
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_null(RunManager.netrun, "the save holds no run")
	assert_false(RunManager.campaign.get_operative(StringName(String(p["operative_id"]))).alive, "the save holds the death")


func test_run_manager_abandon_campaign_counts_a_loss_and_marks_the_slot() -> void:
	RunManager.new_campaign(42)
	RunManager.start_run()
	var refused := RunManager.abandon_campaign()
	assert_eq(String(refused[0]["type"]), "refused", "not under a running netrun")
	assert_false(RunManager.campaign.is_over())
	RunManager.abandon_run()
	var losses := RunManager.profile.campaigns_lost
	var p := RunManager.abandon_campaign_preview()
	watch_signals(RunManager)
	RunManager.abandon_campaign()
	assert_signal_emitted(RunManager, "campaign_ended")
	assert_eq(RunManager.campaign.outcome, CampaignState.Outcome.ABANDONED)
	assert_eq(RunManager.profile.campaigns_lost, losses + 1, "an abandoned campaign is a lost one")
	var summary := RunManager.slot_summary(SLOT)
	assert_eq(String(summary["state"]), "abandoned", "the slot reads abandoned")
	assert_eq(int(summary["heat"]), int(p["heat"]))
	assert_eq(int(summary["runs"]), int(p["runs"]))
	RunManager.sync_profile_with_campaign()
	assert_eq(RunManager.profile.campaigns_lost, losses + 1, "counted once")


## Quit: the save is the live state at every page of a run (map, fight mid-turn, loot, event,
## shop); resuming it (the title's Continue) gives the same run and campaign back.
func test_quit_mid_run_saves_exactly_the_live_state_at_every_page() -> void:
	RunManager.new_campaign(43)
	RunManager.start_run()
	var seen := {}
	var steps := 0
	while RunManager.has_active_run() and steps < 200 and seen.size() < 5:
		steps += 1
		var s := RunManager.netrun
		var phase := s.run.phase
		if not seen.has(phase):
			seen[phase] = true
			if phase == RunState.Phase.COMBAT:
				s.combat_action(CombatAction.end_turn())  # mid-fight, a turn in
			var run_hash := s.state_hash()
			var campaign_hash := RunManager.campaign.state_hash()
			RunManager.quit_game()
			RunManager.reset()
			assert_true(RunManager.resume(), "Continue finds the save")
			assert_true(RunManager.has_active_run(), "with its run")
			assert_eq(RunManager.netrun.state_hash(), run_hash, "the run as it was (%s)" % RunState.Phase.keys()[phase])
			assert_eq(RunManager.campaign.state_hash(), campaign_hash, "the campaign as it was (%s)" % RunState.Phase.keys()[phase])
			s = RunManager.netrun
		match s.run.phase:
			RunState.Phase.MAP:
				s.enter_node(s.available_nodes()[0])
			RunState.Phase.COMBAT:
				s.combat.state.player.max_hp = 9999
				s.combat.state.player.hp = 9999
				CombatFixture.land(s.combat.state.player, 0)
				s.combat_action(CombatAction.end_turn())
			RunState.Phase.REWARD:
				s.skip_reward()
			RunState.Phase.EVENT:
				s.choose_event_option(s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				s.leave_shop()
			RunState.Phase.RAID:
				s.raid_fight()
		RunManager.after_step()
	assert_true(seen.has(RunState.Phase.MAP) and seen.has(RunState.Phase.COMBAT) and seen.has(RunState.Phase.REWARD),
		"the map, a fight and its loot were saved and resumed (%s)" % [seen.keys()])


func test_quit_at_hq_resumes_the_campaign() -> void:
	RunManager.new_campaign(44)
	var hash := RunManager.campaign.state_hash()
	RunManager.quit_game()
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_null(RunManager.netrun)
	assert_eq(RunManager.campaign.state_hash(), hash, "the campaign as it was")


# --- The dialogs (ExitDialogs on 4C's AbandonDialog / ConfirmDialog) -------------------------------

func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _accept(pressed: bool) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = &"ui_accept"
	e.pressed = pressed
	return e


func test_the_abandon_run_dialog_shows_the_preview_as_its_costs() -> void:
	var s := _looted()
	var p := s.abandon_preview()
	var d: AbandonDialog = add_child_autofree(ExitDialogs.abandon_run(p))
	await _frames(2)
	assert_true(d.panel.header_text().contains("ABANDON RUN"), "> CONFIRM // ABANDON RUN (%s)" % d.panel.header_text())
	assert_true(d.panel.destructive, "CANNOT UNDO")
	var words := d.cost_words()
	assert_eq(words.size(), 12, "six costs, name and value")
	for key in ["cycles", "cards_added", "firmware", "daemons", "assets", "rank"]:
		assert_true(words.has(str(int(p[key]))), "%s shows the preview's %d" % [key, int(p[key])])
	assert_true(d.heat_label.text.contains(TextDb.signed(int(p["heat"]))), "the Heat line is the preview's Heat (%s)" % d.heat_label.text)
	assert_eq(d.heat_label.get_theme_color(&"font_color"), Palette.HARM)
	assert_eq(d.kept_label.get_theme_color(&"font_color"), Palette.GAIN, "what stays reads in GAIN")
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "CANCEL has the default focus")
	assert_true(d.hold_to_confirm, "BURN IT is held on the pad")


func test_burn_it_needs_the_hold_on_the_pad_and_a_click_on_the_mouse() -> void:
	var d: AbandonDialog = add_child_autofree(ExitDialogs.abandon_run(_start().abandon_preview()))
	await _frames(2)
	watch_signals(d)
	d.yes_button.grab_focus()
	d._on_verb_input(_accept(true))
	assert_true(d.holding, "A down starts the hold")
	assert_signal_not_emitted(d, "confirmed", "a press alone never confirms")
	d.advance_hold(AbandonDialog.hold_seconds() * 0.5)
	assert_almost_eq(d.hold_ring.progress, 0.5, 0.01, "the ring is half full")
	d._on_verb_input(_accept(false))
	assert_eq(d.hold_progress, 0.0, "letting go early empties the ring")
	assert_signal_not_emitted(d, "confirmed")
	assert_almost_eq(AbandonDialog.hold_seconds(), 0.8, 0.001, "0.8 s (round 33)")
	d._on_verb_input(_accept(true))
	d.advance_hold(AbandonDialog.hold_seconds())
	assert_signal_emitted(d, "confirmed", "a full ring confirms")


func test_a_click_on_burn_it_confirms_at_once() -> void:
	var d: AbandonDialog = add_child_autofree(ExitDialogs.abandon_run(_start().abandon_preview()))
	await _frames(1)
	watch_signals(d)
	d.yes_button.pressed.emit()
	assert_signal_emitted(d, "confirmed")


func test_the_abandon_campaign_dialog_shows_its_costs() -> void:
	var c := _campaign()
	c.heat = 37
	var p := ExitRules.abandon_campaign_preview(c)
	var d: AbandonDialog = add_child_autofree(ExitDialogs.abandon_campaign(p, "Solace Biosystems"))
	await _frames(2)
	assert_true(d.panel.header_text().contains("ABANDON CAMPAIGN"), d.panel.header_text())
	assert_true(d.panel.destructive)
	assert_true(d.cost_words().has("37"), "the campaign's Heat")
	assert_true(d.hold_to_confirm)
	assert_eq(get_viewport().gui_get_focus_owner(), d.no_button)


func test_the_quit_confirm_is_not_destructive_and_says_its_keys() -> void:
	for in_run in [true, false]:
		var d: ConfirmDialog = add_child_autofree(ExitDialogs.quit(in_run))
		await _frames(2)
		assert_true(d.panel.header_text().contains("QUIT"), d.panel.header_text())
		assert_false(d.panel.destructive, "quitting loses nothing")
		assert_false(d is AbandonDialog)
		assert_eq(get_viewport().gui_get_focus_owner(), d.no_button, "CANCEL has the default focus")
		d.queue_free()
		await _frames(1)


# --- The pause menus' rows -------------------------------------------------------------------------

func _row_names(menu: PauseMenu) -> PackedStringArray:
	var out := PackedStringArray()
	for c in menu._rows.get_children():
		out.append(String(c.name))
	return out


func test_the_in_run_pause_abandons_the_run() -> void:
	RunManager.new_campaign(45)
	RunManager.start_run()
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	assert_eq(menu._menu.get_child(0), menu.resume_button, "Resume stays first")
	var rows := _row_names(menu)
	assert_true(rows.has("AbandonRun"), "the in-run pause has Abandon run (%s)" % [rows])
	assert_false(rows.has("AbandonCampaign"), "and not Abandon campaign")
	assert_true(rows.find("AbandonRun") < rows.find("Quit"), "Abandon run sits above Quit")
	assert_eq(menu.abandon_run_button.get_theme_color(&"font_color"), Palette.HARM, "the destructive row reads in HARM")
	menu.abandon_run_button.pressed.emit()
	await _frames(2)
	assert_true(menu.exit_dialog is AbandonDialog, "it asks with the abandon dialog")
	watch_signals(RunManager)
	menu.exit_dialog.yes_button.pressed.emit()
	assert_signal_emitted(RunManager, "run_abandoned")
	assert_false(RunManager.has_active_run(), "BURN IT abandoned the run")
	assert_eq(RunManager.netrun.run.outcome, RunState.Outcome.DIED)


func test_the_hq_pause_abandons_the_campaign() -> void:
	RunManager.new_campaign(46)
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	var rows := _row_names(menu)
	assert_true(rows.has("AbandonCampaign"), "the campaign's pause has Abandon campaign (%s)" % [rows])
	assert_false(rows.has("AbandonRun"))
	assert_eq(menu.abandon_campaign_button.get_theme_color(&"font_color"), Palette.HARM)
	menu.abandon_campaign_button.pressed.emit()
	await _frames(2)
	assert_true(menu.exit_dialog is AbandonDialog)
	watch_signals(RunManager)
	menu.exit_dialog.yes_button.pressed.emit()
	assert_eq(RunManager.campaign.outcome, CampaignState.Outcome.ABANDONED, "BURN IT abandoned the campaign")
	assert_signal_emitted(RunManager, "campaign_ended")


func test_the_pause_quit_asks_with_the_plain_quit_confirm() -> void:
	RunManager.new_campaign(47)
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	(menu._rows.get_node("Quit") as Button).pressed.emit()
	await _frames(2)
	assert_not_null(menu.exit_dialog)
	assert_false(menu.exit_dialog is AbandonDialog, "quitting loses nothing: the plain confirm")
	assert_false(menu.exit_dialog.panel.destructive)
	menu.exit_dialog.no_button.pressed.emit()
	assert_true(RunManager.has_campaign(), "CANCEL leaves everything as it was")


func test_the_quit_confirm_keeps_its_key_hints_at_big_text() -> void:
	var was := Settings.text_scale
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.text_scale = scale
		var d: ConfirmDialog = add_child_autofree(ExitDialogs.quit(false))
		await _frames(1)
		assert_eq((d.no_button as SendItSticker)._line_words().right(3), "[B]", "CANCEL says [B] at %.1f" % scale)
		assert_eq((d.yes_button as SendItSticker)._line_words().right(3), "[A]", "QUIT says [A] at %.1f" % scale)
		d.queue_free()
		await _frames(1)
	Settings.text_scale = was
