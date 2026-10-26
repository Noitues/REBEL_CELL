extends GutTest
## Plan 2 EV-02 hosts (Solace vertical, Q6): the two venues EV-01 left without a host. RAID_WIN: a won raid
## offers one event from the `events` stream (mid-run at the raid interlude, or at the hub after a raid fought
## at HQ). HQ_VIEW: every hq_event_every_runs-th completed netrun owes the hub one event. A hub event is a
## session of kind "event": Cycles are bought from Schematics and convert back, the operative keeps its wounds,
## a fight there is never lethal, a pending event and its wheel survive a save.

const CRATE := &"ev_hq_dead_letter_crate"
const RUMOR := &"ev_rw_second_hand_rumor"
const OP := &"op_1"

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func before_each() -> void:
	RaidModelFixture.use_resolver()  # Phase 2b: Solace is the resolver's carrier here (raid views of the tide are Phase 3)
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RaidModelFixture.restore()
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _campaign(schematics: int = 50) -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _hub(venue: int, seed: int = 11, schematics: int = 50, c: CampaignState = null) -> NetrunSession:
	var camp := c if c != null else _campaign(schematics)
	camp.venue_event_due = venue
	return NetrunSession.start_venue_event(_resolver, camp, OP, venue, 1, seed)


func _event(id: StringName) -> TerminalEventData:
	return ContentRegistry.get_content(id) as TerminalEventData


## Puts hub session `s` on event `id` (the venue draw is tested apart).
func _open(s: NetrunSession, id: StringName) -> void:
	s.run.event_id = id
	s.run.phase = RunState.Phase.EVENT


func _events_stream_copy(s: NetrunSession) -> RandomNumberGenerator:
	return RngStreams.from_dict(s.streams.to_dict()).get_stream(EventRules.STREAM)


func _auto_fight(s: NetrunSession) -> void:
	var turns := 0
	while s.in_combat() and turns < 80:
		s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		for i in range(s.combat.state.hand.size() - 1, -1, -1):
			if i < s.combat.state.hand.size():
				s.combat_action(CombatAction.play_card(i, s.combat.state.target_id))
		s.combat_action(CombatAction.end_turn())
		turns += 1
	assert_false(s.in_combat(), "fight finished within %d turns" % turns)


# --- The event and the pools -----------------------------------------------------------------

func test_the_crate_is_authored_as_drafted() -> void:
	var ev := _event(CRATE)
	assert_not_null(ev)
	assert_eq(ev.validate(), PackedStringArray())
	assert_eq(ev.venue, TerminalEventData.Venue.HQ_VIEW)
	assert_eq(ev.choices.size(), 4)
	assert_eq(ev.choices[0].event_wheel.slices.size(), 3)
	assert_eq(ev.choices[1].hp_cost, 6)
	assert_true(ev.choices[1].common_firmware)
	assert_eq(ev.choices[3].cycle_cost, 15)
	assert_eq(ev.choices[3].starts_combat.enemy_id, &"tariff_collector")
	assert_true(ev.choices[3].starts_combat.win_daemon)


func test_venue_pools_never_cross_venues() -> void:
	var lookup := _resolver.lookup
	var rw := EventRules.venue_pool(lookup, TerminalEventData.Venue.RAID_WIN, &"solace", 1)
	var hq := EventRules.venue_pool(lookup, TerminalEventData.Venue.HQ_VIEW, &"solace", 1)
	assert_true(rw.has(RUMOR) and not rw.has(CRATE))
	assert_true(hq.has(CRATE) and not hq.has(RUMOR))
	assert_true(EventRules.venue_pool(lookup, TerminalEventData.Venue.HQ_VIEW, &"solace", 0).is_empty(), "min_tier gates the pool")
	var terminal: Array = _hub(TerminalEventData.Venue.HQ_VIEW).pools()["events"]
	assert_false(terminal.has(CRATE) or terminal.has(RUMOR), "the Terminal pool draws neither")


func test_venue_pick_reads_one_draw_and_an_empty_pool_reads_none() -> void:
	var lookup := _resolver.lookup
	var pool := EventRules.venue_pool(lookup, TerminalEventData.Venue.HQ_VIEW, &"solace", 1)
	var a := RandomNumberGenerator.new()
	a.seed = 5
	var b := RandomNumberGenerator.new()
	b.seed = 5
	assert_eq(EventRules.venue_pick(lookup, pool, a), EventRules.venue_pick(lookup, pool, b), "same stream, same pick")
	var one := RandomNumberGenerator.new()
	one.seed = 5
	one.randf()
	assert_eq(a.state, one.state, "exactly one randf is read")
	var c := RandomNumberGenerator.new()
	c.seed = 5
	var before := c.state
	assert_eq(EventRules.venue_pick(lookup, [] as Array[StringName], c), &"")
	assert_eq(c.state, before, "nothing is drawn from an empty pool")


func test_the_hq_cadence_comes_from_config() -> void:
	var cfg := _cfg.duplicate() as CampaignConfigData
	cfg.hq_event_every_runs = 3
	assert_false(EventRules.hq_event_due(cfg, 0))
	assert_false(EventRules.hq_event_due(cfg, 2))
	assert_true(EventRules.hq_event_due(cfg, 3))
	assert_false(EventRules.hq_event_due(cfg, 4))
	assert_true(EventRules.hq_event_due(cfg, 6))
	cfg.hq_event_every_runs = 0
	assert_false(EventRules.hq_event_due(cfg, 3), "0 = never")
	assert_true(_cfg.raid_win_event_enabled)
	assert_eq(_cfg.hq_event_every_runs, 3)


func test_purse_rounds_down_to_whole_schematics() -> void:
	assert_eq(EventRules.purse_for(7, 10), 70)
	assert_eq(EventRules.purse_schematics_delta(55, 70, 10), -2, "15 Cycles spent cost 2")
	assert_eq(EventRules.purse_schematics_delta(70, 70, 10), 0)
	assert_eq(EventRules.purse_schematics_delta(95, 70, 10), 2, "25 Cycles gained pay 2")
	assert_eq(EventRules.purse_schematics_delta(60, 70, 10), -1)


# --- The hub session ---------------------------------------------------------------------------

func test_a_hub_session_opens_a_venue_event_with_a_purse() -> void:
	var c := _campaign(50)
	var started := c.runs_started
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	assert_true(s.is_event_session())
	assert_eq(s.run.phase, RunState.Phase.EVENT)
	assert_eq(s.run.event_id, CRATE, "the HQ_VIEW pool holds the crate")
	assert_eq(s.run.cycles, 500, "Schematics bought at the config ratio")
	assert_eq(s.run.purse_cycles, 500)
	assert_eq(c.venue_event_due, -1, "the due mark is spent")
	assert_eq(c.runs_started, started, "a hub event is no netrun")
	var again := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, _campaign(50))
	assert_eq(again.run.event_id, s.run.event_id, "the same seed draws the same event")


func test_no_event_to_draw_returns_null_and_clears_the_mark() -> void:
	var c := _campaign()
	c.venue_event_due = TerminalEventData.Venue.HQ_VIEW
	var s := NetrunSession.start_venue_event(_resolver, c, OP, TerminalEventData.Venue.HQ_VIEW, 0, 5)
	assert_null(s)
	assert_eq(c.venue_event_due, -1)


func test_leaving_the_crate_closes_the_session_without_a_netrun_trace() -> void:
	var c := _campaign(50)
	c.heat = 10
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	var rank := c.get_operative(OP).rank
	assert_eq(s.choice_costs(s.current_event().choices[2]), "-1 Heat")
	s.choose_event_option(2)
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED)
	assert_eq(c.heat, 9)
	assert_eq(c.schematics, 50, "nothing spent, nothing gained")
	assert_eq(c.get_operative(OP).rank, rank, "no Rank for a hub event")
	assert_eq(c.runs_completed, 0)
	assert_eq(c.venue_event_due, -1)


func test_a_cycle_price_is_a_schematic_price() -> void:
	var c := _campaign(50)
	c.venue_event_due = TerminalEventData.Venue.RAID_WIN
	var s := NetrunSession.start_venue_event(_resolver, c, OP, TerminalEventData.Venue.RAID_WIN, 1, 11)
	assert_eq(s.run.event_id, RUMOR)
	assert_eq(s.choice_costs(s.current_event().choices[0]), "-20 Cycles, next raid scouted")
	s.choose_event_option(0)
	assert_true(s.run.is_over())
	assert_eq(c.schematics, 48, "20 Cycles = 2 Schematics")
	assert_true(bool(c.next_raid_mods["scout"]), "the next raid is marked")
	var poor := _campaign(1)
	var p := _hub(TerminalEventData.Venue.RAID_WIN, 11, 1, poor)
	assert_ne(p.choice_error(p.current_event().choices[0]), "", "1 Schematic buys only 10 Cycles")


func test_the_inspected_crate_keeps_the_wound_and_offers_the_firmware() -> void:
	var c := _campaign(50)
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	var max_hp := c.get_operative(OP).max_hp
	var choice := s.current_event().choices[1]
	assert_eq(s.choice_costs(choice), "-6 HP, +20 Cycles, Firmware: ?", "? only where the stream is read")
	var predicted := _events_stream_copy(s)
	var pool: Array = s.pools()["common_firmware"]
	var expect: String = String(pool[predicted.randi_range(0, pool.size() - 1)])
	s.choose_event_option(1)
	assert_eq(s.run.phase, RunState.Phase.REWARD, "the Firmware is a pick")
	assert_eq(s.run.pending_rewards[0]["options"], [expect], "the pick is the next events draw")
	s.skip_reward()
	assert_true(s.run.is_over())
	assert_eq(c.get_operative(OP).hp, max_hp - 6, "the wound stays at HQ")
	assert_eq(c.schematics, 52, "20 Cycles = 2 Schematics")


func test_the_crate_wheel_pays_and_hands_the_tracker_to_the_next_run() -> void:
	var c := _campaign(50)
	c.heat = 10
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	var predicted_tick := _events_stream_copy(s).randi_range(0, RC.TICKS - 1)
	assert_eq(s.choice_costs(s.current_event().choices[0]), "+10 Schematics, +4 Heat, wheel (start ?)")
	s.choose_event_option(0)
	assert_eq(int(s.run.event_wheel["tick"]), predicted_tick, "the start tick is the next events draw")
	assert_eq(c.heat, 14)
	s.run.event_wheel["tick"] = 25  # the live tracker
	assert_eq(s.event_wheel_slice().size_ticks, 8)
	s.event_wheel_commit()
	assert_true(s.run.is_over())
	assert_eq(c.heat, 18, "+4 Heat more")
	assert_eq(c.schematics, 60, "the +10 banked Schematics")
	assert_eq(c.carried_combat_mods.size(), 1, "the modifier waits for the next netrun")
	var next := NetrunSession.start(_resolver, c, OP, 1, &"t1_a", 7)
	assert_eq(next.run.combat_mods.size(), 1)
	assert_eq(int(next.run.combat_mods[0]["res"]), 1)
	assert_true(c.carried_combat_mods.is_empty(), "taken by that run")
	# The salvage slice pays 30 Cycles = 3 Schematics.
	var c2 := _campaign(50)
	var s2 := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c2)
	s2.choose_event_option(0)
	s2.run.event_wheel["tick"] = 3
	s2.event_wheel_commit()
	assert_eq(c2.schematics, 63)
	assert_true(c2.carried_combat_mods.is_empty())


func test_the_traced_enforcer_pays_a_common_daemon_on_a_win() -> void:
	var c := _campaign(50)
	c.heat = 10
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	var choice := s.current_event().choices[3]
	assert_eq(s.choice_costs(choice), "-15 Cycles, fight: tariff_collector, win: Daemon ?")
	s.choose_event_option(3)
	assert_true(s.in_combat())
	assert_eq(s.combat.setup["enemy_ids"][0], "tariff_collector")
	assert_eq(s.run.normal_fights_started, 0, "an event fight is no node fight")
	_auto_fight(s)
	assert_eq(c.heat, 8, "-2 Heat for the win")
	assert_eq(s.run.phase, RunState.Phase.REWARD)
	var offer := s.run.pending_rewards[0]
	assert_eq(offer["kind"], "daemon")
	var id := StringName(String(offer["options"][0]))
	assert_eq((ContentRegistry.get_content(id) as DaemonData).rarity, RC.Rarity.COMMON, "the Daemon rarity pool")
	s.choose_reward(0)
	assert_true(s.run.is_over())
	assert_true(c.get_operative(OP).daemon_ids.has(id))
	assert_eq(c.schematics, 48, "15 Cycles = 2 Schematics")
	assert_eq(c.get_operative(OP).rank, 0)


func test_a_lost_hub_fight_is_never_lethal() -> void:
	var c := _campaign(50)
	c.heat = 10
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	s.choose_event_option(3)
	assert_true(s.in_combat())
	s.combat.state.player.hp = 0
	s.combat_action(CombatAction.end_turn())
	assert_false(s.in_combat())
	assert_true(s.run.is_over())
	assert_true(c.get_operative(OP).alive, "no death at HQ")
	assert_eq(c.get_operative(OP).hp, 1)
	assert_eq(c.deaths, 0)
	assert_eq(c.heat, 10, "no payout")
	assert_false(c.get_operative(OP).daemon_ids.has(&"") or s.run.pending_rewards.size() > 0)
	assert_eq(c.schematics, 48, "the 15 Cycles are spent")


func test_abandon_is_refused_at_hq() -> void:
	var c := _campaign()
	var s := _hub(TerminalEventData.Venue.HQ_VIEW, 11, 50, c)
	var events := s.abandon()
	assert_eq(events[0]["type"], "refused")
	assert_true(c.get_operative(OP).alive)
	assert_false(s.run.is_over())


# --- The owed marks --------------------------------------------------------------------------

func test_every_third_completed_netrun_owes_the_hub_an_event() -> void:
	var c := _campaign()
	var s := NetrunSession.start(_resolver, c, OP, 1, &"t1_a", 4)
	c.runs_completed = 1
	s._complete_run()
	assert_eq(c.venue_event_due, -1, "run 2 is not owed")
	c.runs_completed = 2
	var s3 := NetrunSession.start(_resolver, c, OP, 1, &"t1_a", 5)
	s3._complete_run()
	assert_eq(c.runs_completed, 3)
	assert_eq(c.venue_event_due, TerminalEventData.Venue.HQ_VIEW)
	var c2 := _campaign()
	c2.runs_completed = 5
	c2.venue_event_due = TerminalEventData.Venue.RAID_WIN
	NetrunSession.start(_resolver, c2, OP, 1, &"t1_a", 6)._complete_run()
	assert_eq(c2.venue_event_due, TerminalEventData.Venue.RAID_WIN, "an owed raid-win event is not replaced")


func test_the_owed_marks_save_and_default_to_nothing() -> void:
	var c := _campaign()
	assert_false(c.to_dict().has("venue_event_due"))
	assert_false(c.to_dict().has("carried_combat_mods"))
	c.venue_event_due = TerminalEventData.Venue.HQ_VIEW
	c.carried_combat_mods.append({"left": 1, "res": 1})
	var back := CampaignState.from_dict(c.to_dict())
	assert_eq(back.venue_event_due, TerminalEventData.Venue.HQ_VIEW)
	assert_eq(back.carried_combat_mods.size(), 1)
	assert_eq(int(back.carried_combat_mods[0]["res"]), 1)
	assert_eq(back.state_hash(), c.state_hash())
	assert_false(RunState.new().to_dict().has("purse_cycles"))


# --- Raid wins ---------------------------------------------------------------------------------

func _winnable_raid(c: CampaignState) -> void:
	RunManager.lookup().add(GridFixture.raid(&"ev02_empty_raid", [], 8))
	c.pending_raids.append({"raid_id": "ev02_empty_raid", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})


func test_a_raid_won_mid_run_opens_the_event_before_the_next_raid() -> void:
	RunManager.new_campaign(34)
	var c := RunManager.campaign
	var s := RunManager.start_run()
	_winnable_raid(c)
	s._maybe_raid_interlude()
	assert_eq(s.run.phase, RunState.Phase.RAID)
	var won := c.raids_won
	s.raid_fight()
	assert_eq(c.raids_won, won + 1)
	assert_eq(s.run.phase, RunState.Phase.EVENT, "CELL HOLDS: the event is offered after the result")
	assert_eq(s.run.event_id, RUMOR)
	s.run.cycles = 100
	s.choose_event_option(1)  # take the spoils
	assert_eq(s.run.cycles, 110)
	assert_eq(c.next_raid_mods["strength_pct"], 10, "the next raid is marked")
	assert_eq(s.run.phase, RunState.Phase.MAP, "back to the route")


func test_the_config_can_turn_the_raid_win_event_off() -> void:
	RunManager.new_campaign(35)
	var c := RunManager.campaign
	var s := RunManager.start_run()
	_winnable_raid(c)
	s._maybe_raid_interlude()
	_cfg_toggle(false)
	s.raid_fight()
	_cfg_toggle(true)
	assert_eq(c.raids_won, 1)
	assert_eq(s.run.phase, RunState.Phase.MAP, "disabled in config: no event")
	assert_eq(s.run.event_id, &"")
	RunManager.new_campaign(36)
	c = RunManager.campaign
	_winnable_raid(c)
	_cfg_toggle(false)
	RunManager.fight_raid()
	_cfg_toggle(true)
	assert_eq(c.venue_event_due, -1, "nor is one owed at the hub")


func test_a_lost_raid_offers_nothing() -> void:
	RunManager.new_campaign(39)
	var c := RunManager.campaign
	var s := RunManager.start_run()
	RunManager.lookup().add(GridFixture.raid(&"ev02_lost_raid", [&"enforcer"], 8, 1))
	c.pending_raids.append({"raid_id": "ev02_lost_raid", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	s._maybe_raid_interlude()
	s.raid_fight()
	assert_eq(c.raids_won, 0, "the raid was not a clean defense")
	assert_ne(s.run.phase, RunState.Phase.EVENT, "only a win offers the event")
	assert_eq(c.venue_event_due, -1)


func _cfg_toggle(on: bool) -> void:
	RunManager.config().raid_win_event_enabled = on


func test_a_raid_won_at_hq_owes_the_hub_one_event() -> void:
	RunManager.new_campaign(37)
	var c := RunManager.campaign
	_winnable_raid(c)
	RunManager.fight_raid()
	assert_eq(c.venue_event_due, TerminalEventData.Venue.RAID_WIN)
	assert_eq(RunManager.venue_event_due(), TerminalEventData.Venue.RAID_WIN)
	var s := RunManager.start_venue_event()
	assert_not_null(s)
	assert_eq(s.run.event_id, RUMOR)
	assert_eq(c.venue_event_due, -1)
	assert_eq(RunManager.venue_event_due(), -1, "a run under way owes nothing")
	var before := c.schematics
	s.choose_event_option(0)  # pay for the details
	assert_true(s.run.is_over())
	assert_eq(c.schematics, before - 2)
	assert_true(bool(c.next_raid_mods["scout"]))
	RunManager.after_step()
	assert_eq(RunManager.profile.runs_completed, 0, "a hub event is no netrun in the profile")


func test_a_pending_hub_event_and_its_wheel_survive_a_save() -> void:
	RunManager.new_campaign(38)
	var c := RunManager.campaign
	c.venue_event_due = TerminalEventData.Venue.HQ_VIEW
	var s := RunManager.start_venue_event()
	assert_eq(s.run.event_id, CRATE)
	var hash_open := s.state_hash()
	RunManager.reset()
	assert_true(RunManager.resume())
	s = RunManager.netrun
	assert_true(s.is_event_session())
	assert_eq(s.state_hash(), hash_open, "the open event survives the save")
	s.choose_event_option(0)
	var tick := int(s.run.event_wheel["tick"])
	RunManager.after_step()
	var hash_wheel := s.state_hash()
	RunManager.reset()
	assert_true(RunManager.resume())
	s = RunManager.netrun
	assert_eq(s.state_hash(), hash_wheel, "the wheel survives at its checkpoint")
	assert_eq(int(s.run.event_wheel["tick"]), tick, "a reload cannot reroll the start")
	s.event_wheel_commit()
	assert_true(s.run.is_over())
	RunManager.after_step()
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_null(RunManager.netrun, "a closed hub event leaves no run to resume")
	RunManager.campaign.venue_event_due = TerminalEventData.Venue.RAID_WIN
	RunManager.autosave()
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_eq(RunManager.venue_event_due(), TerminalEventData.Venue.RAID_WIN, "an owed event survives the save")
