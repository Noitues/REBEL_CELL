class_name DemoSetup
extends RefCounted
## Dev flags and captures only (ANIM-R6 B2): the one place a screenshot or capture shortcut
## (`--demo-shop`, `--demo-loot`, `--demo-end=...`, the combat end demo, the HQ's loadout
## demo) sets up a run, a campaign or a fight. The views never write game state (Signal Up,
## Call Down): a dev flag asks this class, which works on the state objects it is handed,
## through the session's own steps where there is one. Never called by the game's own flow
## or its rules; the tests call it to reach a state quickly too. Pure: no Node, no scene.

## The Cycles `--demo-shop` opens the Modem with.
const SHOP_CYCLES := 120


## Opens the Modem on the run's node with `cycles` Cycles in hand (the session's own stock).
static func open_shop(s: NetrunSession, cycles: int = SHOP_CYCLES) -> void:
	if s == null:
		return
	s.run.cycles = cycles
	s.call(&"_open_shop")


## Sets the run's Cycles (a purchase or a refusal demo).
static func set_cycles(s: NetrunSession, cycles: int) -> void:
	if s != null:
		s.run.cycles = cycles


## Installs Daemons `ids` on the running operative (the tray demo).
static func add_daemons(s: NetrunSession, ids: Array[StringName]) -> void:
	if s != null:
		s.run.operative.daemon_ids.append_array(ids)


## Puts a loot offer of `kind` with `options` (content ids) on the run and opens it.
static func offer_loot(s: NetrunSession, options: Array, kind: String = "card") -> void:
	if s == null:
		return
	s.run.pending_rewards.append({"kind": kind, "options": options})
	s.run.phase = RunState.Phase.REWARD


## Opens Terminal event `event_id` on the run.
static func open_event(s: NetrunSession, event_id: StringName) -> void:
	if s == null:
		return
	s.run.event_id = event_id
	s.run.phase = RunState.Phase.EVENT


## Ends the run through the session's own ending: "completed" (the clean exit) or anything
## else (the flatline). The session's events are in `s.last_events`.
static func end_run(s: NetrunSession, kind: String) -> void:
	if s == null:
		return
	s.last_events.clear()
	s.call(&"_complete_run" if kind == "completed" else &"_die")


## Raises campaign Heat past the first major level and lets the session queue its raid
## interlude (a run that opens on a raid).
static func queue_raid_interlude(s: NetrunSession, config: CampaignConfigData) -> void:
	if s == null or config == null:
		return
	HeatRules.add_heat(s.campaign, config.major_heat_levels()[0] + 1, config, "demo")
	s.call(&"_maybe_raid_interlude")


## The campaign's roster becomes one operative of class `cls` (a screenshot of that class).
static func only_class(c: CampaignState, cls: ClassData) -> void:
	if c == null or cls == null:
		return
	c.roster.clear()
	c.recruit(cls)


## Sets an operative's Rank (the loadout demo's ring swaps).
static func set_rank(op: OperativeState, rank: int) -> void:
	if op != null:
		op.rank = rank


## The combat end demo: the side that should lose ("win": the first enemy, else the
## operative) is left one hit from 0 on the live fight state.
static func one_hit_from_end(st: CombatState, win: bool) -> void:
	if st == null:
		return
	if win:
		if not st.enemies.is_empty():
			st.enemies[0].hp = 1
	elif st.player != null:
		st.player.hp = 1


# --- ANIM-R6 C16 (the HQ's dev flags) ---------------------------------------------------------

## The campaign's roster becomes one operative of each of `classes` (`--demo-classes`).
static func roster_of(c: CampaignState, classes: Array[ClassData]) -> void:
	if c == null:
		return
	c.roster.clear()
	for cls in classes:
		if cls != null:
			c.recruit(cls)


## Sets the campaign's Schematics (the Grid and raid demos' budget).
static func set_schematics(c: CampaignState, amount: int) -> void:
	if c != null:
		c.schematics = amount


## Sets the campaign's Armory to `ids` (the raid demos' defences).
static func set_armory(c: CampaignState, ids: Array[StringName]) -> void:
	if c != null:
		c.armory.assign(ids)


## Sets the campaign's Heat (the Heat poster demo; the crossing plays where it shows).
static func set_heat(c: CampaignState, heat: int) -> void:
	if c != null:
		c.heat = heat


## Ends the campaign with `outcome` (`--demo-campaign-end=won|lost`); a lost one's home is at 0.
static func end_campaign(c: CampaignState, outcome: int) -> void:
	if c == null:
		return
	c.outcome = outcome
	if outcome == CampaignState.Outcome.LOST:
		c.grid.home_integrity = 0
