extends Node
## RunManager autoload: owns the ProfileState, the CampaignState (with its corporation)
## and the active NetrunSession; saves and resumes them through SaveService; switches
## scenes (TECH_SPEC §3, §8).

signal campaign_changed(campaign: CampaignState)
signal run_changed(netrun: NetrunSession)
signal run_ended(netrun: NetrunSession)
signal campaign_ended(campaign: CampaignState)

const DEFAULT_SLOT := "current"
const HQ_SCENE := "res://scenes/hq/hq_scene.tscn"
const NETRUN_SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const TITLE_SCENE := "res://scenes/menu/title_scene.tscn"
const COMBAT_SCENE := "res://scenes/combat/combat_scene.tscn"
const DEFAULT_CORPORATION := &"solace"
const DEFAULT_CLASS := &"breaker"
const DEFAULT_HOME := &"home_standard"

var profile: ProfileState = ProfileState.new()
var campaign: CampaignState = null
var corporation: CorporationData = null
var netrun: NetrunSession = null
var resolver: CombatResolver = null
## Save slot name; tests use their own so they never touch a player's save.
var save_slot: String = DEFAULT_SLOT
## Tests switch this off so scene changes never replace the test runner.
var scene_switching_enabled: bool = true
## The next combat scene opened runs the guided tutorial (title "Tutorial" button).
var pending_tutorial: bool = false
## Achievement ids earned since the last check (the HUD announces them).
var new_achievements: Array[StringName] = []

var profile_state: RefCounted:
	get:
		return profile


func _ready() -> void:
	if resolver == null and ContentRegistry.config != null:
		resolver = CombatEngine.make_resolver()
	load_profile()


func has_active_run() -> bool:
	return netrun != null and not netrun.run.is_over()


func has_campaign() -> bool:
	return campaign != null and not campaign.is_over()


func save_path() -> String:
	return SaveService.campaign_path(save_slot)


func profile_path() -> String:
	return SaveService.profile_path() if save_slot == DEFAULT_SLOT else SaveService.SAVE_DIR.path_join("profile_%s.json" % save_slot)


func has_save() -> bool:
	return SaveService.has_save(save_path())


## Forgets the campaign and run in memory (files stay). The profile is reloaded.
func reset() -> void:
	campaign = null
	netrun = null
	load_profile()


func config() -> CampaignConfigData:
	_ensure_resolver()
	return resolver.config


func lookup() -> ContentLookup:
	_ensure_resolver()
	return resolver.lookup


func class_data() -> ClassData:
	return lookup().get_content(DEFAULT_CLASS) as ClassData


# --- Campaign ----------------------------------------------------------------------------

## Highest ICE the profile allows for `corporation_id` (GDD 3.4).
func ice_cap(corporation_id: StringName = DEFAULT_CORPORATION) -> int:
	return profile.ice_cap_for(corporation_id, config().new_corp_ice_offset)


## Home-server variants the profile may start on (the standard one always).
func available_home_variants() -> Array[HomeServerVariantData]:
	var out: Array[HomeServerVariantData] = []
	for id in lookup().ids_of_class(&"HomeServerVariantData"):
		var v := lookup().get_content(id) as HomeServerVariantData
		var u := CampaignRules.unlock_for(lookup(), v)
		if v != null and (u == null or profile.has_unlock(u.id)):
			out.append(v)
	return out


## Starts a fresh campaign against `corporation_id` (GDD 5.4 opening) at `ice_level`
## (clamped to the profile's cap) on `home_variant_id`.
## Classes the profile may recruit now (the Breaker plus unlocked classes).
## REBEL_CELL (GDD 8.5): builds the corporation from the template and a usage snapshot
## and registers it (and its generated elites, threats and raids) in the lookup.
func build_generated(corporation_id: StringName, snap: Dictionary) -> CorporationData:
	var template := ContentRegistry.get_content(corporation_id) as CorporationData
	var built := RebelCellBuilder.build(template, snap, lookup())
	lookup().add(built)
	return built


## Corporations the profile may start a campaign against (GDD 3.4).
func available_corporations() -> Array[CorporationData]:
	return CampaignRules.available_corporations(profile, lookup())


func available_classes() -> Array[ClassData]:
	return CampaignRules.available_classes(profile, lookup())


## Recruits a rookie of `class_id` (refused when the class is locked).
func recruit(class_id: StringName = DEFAULT_CLASS) -> Array[Dictionary]:
	var cls := lookup().get_content(class_id) as ClassData
	if not CampaignRules.class_available(profile, lookup(), cls):
		var refused: Array[Dictionary] = [{"type": "refused", "text": "%s is locked: buy the Profile unlock first." % class_id}]
		return refused
	return CampaignRules.recruit(campaign, config(), cls)


func new_campaign(campaign_seed: int, corporation_id: StringName = DEFAULT_CORPORATION, ice_level: int = 0, home_variant_id: StringName = DEFAULT_HOME, class_id: StringName = DEFAULT_CLASS) -> CampaignState:
	_ensure_resolver()
	corporation = lookup().get_content(corporation_id) as CorporationData
	if not CampaignRules.corporation_available(profile, lookup(), corporation):
		corporation = lookup().get_content(DEFAULT_CORPORATION) as CorporationData
		corporation_id = DEFAULT_CORPORATION
	var home := lookup().get_content(home_variant_id) as HomeServerVariantData
	if home == null or not available_home_variants().has(home):
		home = lookup().get_content(DEFAULT_HOME) as HomeServerVariantData
	var snap := {}
	if corporation.generated_from_profile:
		snap = RebelCellBuilder.snapshot(profile, DEFAULT_CLASS)
		corporation = build_generated(corporation_id, snap)
	var ice := clampi(ice_level, 0, ice_cap(corporation_id))
	var start_class := lookup().get_content(class_id) as ClassData
	if not CampaignRules.class_available(profile, lookup(), start_class):
		start_class = class_data()
	campaign = CampaignRules.new_campaign(corporation, config(), lookup(), campaign_seed, start_class, home.core if home != null else null, ice, home)
	campaign.generated = snap
	netrun = null
	RngService.seed_campaign(campaign_seed)
	_reset_profile_sync()
	profile.campaigns_started += 1
	save_profile()
	SignalBus.run_started.emit(campaign_seed)
	campaign_changed.emit(campaign)
	autosave()
	return campaign


## Sites the player may target now.
func launchable_sites() -> Array[SiteData]:
	return CampaignRules.launchable_sites(campaign, corporation, config()) if campaign != null else []


## Cleared or claimed Sites that can be patrolled again (Rank without objectives).
func patrol_sites() -> Array[SiteData]:
	return CampaignRules.patrol_sites(campaign, corporation) if campaign != null else []


func launch_error(operative_id: StringName, site_id: StringName) -> String:
	if campaign == null:
		return "No campaign."
	var site := CampaignRules.site_data(corporation, site_id)
	if site == null:
		return "No such Site."
	var op := campaign.get_operative(operative_id)
	var cls := lookup().get_content(op.class_id) as ClassData if op != null else class_data()
	return CampaignRules.launch_error(campaign, corporation, config(), op, cls, site)


## Launches a run at `site_id` with `operative_id` (default: the first living operative).
## Full netruns, the final breach and Reclaim runs are all NetrunSessions.
func start_run(operative_id: StringName = &"", site_id: StringName = &"") -> NetrunSession:
	_ensure_resolver()
	if campaign == null:
		push_error("RunManager: no campaign.")
		return null
	if operative_id == &"":
		var living := campaign.living_operatives()
		if living.is_empty():
			push_error("RunManager: no living operative.")
			return null
		operative_id = living[0].id
	if site_id == &"":
		var sites := launchable_sites()
		if sites.is_empty():
			push_error("RunManager: no launchable Site.")
			return null
		site_id = sites[0].id
	var err := launch_error(operative_id, site_id)
	if err != "":
		push_error("RunManager: " + err)
		return null
	var site := CampaignRules.site_data(corporation, site_id)
	var seed_rng := RngService.get_stream(&"map") if RngService.is_seeded() else RngStreams.make_stream(campaign.campaign_seed, &"map")
	var run_seed := seed_rng.randi()
	match CampaignRules.run_kind_for(campaign, site):
		"boss":
			netrun = NetrunSession.start_special(resolver, campaign, operative_id, "boss", site_id, site.tier, run_seed,
				corporation.final_boss.id, CampaignRules.boss_overrides(campaign, corporation), corporation)
		"reclaim":
			var pool: Array = []
			for e in corporation.enemies:
				if e != null:
					pool.append(e.id)
			var enemy: StringName = pool[seed_rng.randi_range(0, pool.size() - 1)] if not pool.is_empty() else &""
			netrun = NetrunSession.start_special(resolver, campaign, operative_id, "reclaim", site_id, site.tier, run_seed, enemy, {}, corporation)
		_:
			netrun = NetrunSession.start(resolver, campaign, operative_id, site.tier, site_id, run_seed, corporation)
	_history_recorded = false
	run_changed.emit(netrun)
	autosave()
	return netrun


## Called by the UI after any run step; saves, records outcomes, announces the end.
func after_step() -> void:
	if netrun != null and netrun.run.is_over():
		_record_run_outcome()
	else:
		sync_profile_with_campaign()
	autosave()
	if netrun != null and netrun.run.is_over():
		run_ended.emit(netrun)
	if campaign != null and campaign.is_over():
		campaign_ended.emit(campaign)
	run_changed.emit(netrun)


func _record_run_outcome() -> void:
	var r := netrun.run
	if r.outcome == RunState.Outcome.COMPLETED:
		profile.runs_completed += 1
	elif r.outcome == RunState.Outcome.DIED:
		profile.operatives_lost += 1
	if not _history_recorded:
		_history_recorded = true
		profile.add_stat("cycles", r.cycles)
		profile.add_stat("racks", r.banked_schematics / maxi(1, config().rack_schematics_by_tier[clampi(r.tier - 1, 0, 3)]) if r.kind == "netrun" else 0)
		profile.add_stat("runs_t%d" % r.tier, 1)
		_record_usage(r)
		profile.record_run({"corporation": String(campaign.corporation_id), "tier": r.tier, "site": String(r.site_id),
			"outcome": RunState.Outcome.keys()[r.outcome].to_lower(), "cycles": r.cycles, "banked": r.banked_schematics})
	sync_profile_with_campaign()


var _history_recorded: bool = false


## What the Cell used this run, for REBEL_CELL (GDD 8.5): the class, its Daemons, and the
## node types and defense assets standing on the Grid.
func _record_usage(r: RunState) -> void:
	profile.record_usage("class", r.operative.class_id)
	for d in r.operative.daemon_ids:
		profile.record_usage("daemon", d)
	for site in campaign.grid.claimed_ids():
		if site != campaign.grid.home_site_id:
			profile.record_usage("node", campaign.grid.node_type_of(site))
		for a in campaign.grid.assets_on(site):
			profile.record_usage("asset", a)


## Counts a Perfect landing for the stats (combat scenes report them).
func record_perfect() -> void:
	profile.add_stat("perfects", 1)


## Mirrors campaign raid counters and the campaign outcome into the profile exactly once
## (mid-run raid interludes and HQ raids both end up here).
var _profile_raids_won_seen: int = 0
var _profile_raids_lost_seen: int = 0
var _profile_outcome_seen: int = CampaignState.Outcome.NONE


func sync_profile_with_campaign() -> void:
	if campaign == null:
		return
	profile.raids_won += maxi(0, campaign.raids_won - _profile_raids_won_seen)
	profile.raids_lost += maxi(0, campaign.raids_lost - _profile_raids_lost_seen)
	_profile_raids_won_seen = campaign.raids_won
	_profile_raids_lost_seen = campaign.raids_lost
	if campaign.outcome != _profile_outcome_seen:
		_profile_outcome_seen = campaign.outcome
		if campaign.outcome == CampaignState.Outcome.WON:
			profile.record_win(campaign.corporation_id, campaign.ice_level)
		elif campaign.outcome == CampaignState.Outcome.LOST:
			profile.record_loss()
	var corp_ids := []
	for id in lookup().ids_of_class(&"CorporationData"):
		var c := lookup().get_content(id) as CorporationData
		if c != null and not c.generated_from_profile:
			corp_ids.append(id)
	for id in Achievements.check(profile, campaign, corp_ids):
		profile.add_achievement(id)
		new_achievements.append(id)
		var d := Achievements.definition(id)
		if has_node("/root/Dialogue"):
			get_node("/root/Dialogue").say(RC.Voice.NARRATOR, "Achievement: %s. %s" % [d.get("title", id), d.get("text", "")])
	save_profile()


func _reset_profile_sync() -> void:
	_profile_raids_won_seen = campaign.raids_won if campaign != null else 0
	_profile_raids_lost_seen = campaign.raids_lost if campaign != null else 0
	_profile_outcome_seen = campaign.outcome if campaign != null else CampaignState.Outcome.NONE


# --- Raids ---------------------------------------------------------------------------------

func pending_raid() -> Dictionary:
	return CampaignRules.pending_raid(campaign) if campaign != null else {}


func project_raid() -> RaidResolver.RaidResult:
	var pending := pending_raid()
	return CampaignRules.project_raid(campaign, corporation, config(), lookup(), pending) if not pending.is_empty() else null


## Plays out the first pending raid and applies it. Returns the events.
func fight_raid() -> Array[Dictionary]:
	var pending := pending_raid()
	if pending.is_empty():
		return []
	var events := CampaignRules.fight_raid(campaign, corporation, config(), lookup(), pending)
	sync_profile_with_campaign()
	if campaign.outcome == CampaignState.Outcome.LOST:
		campaign_ended.emit(campaign)
	autosave()
	campaign_changed.emit(campaign)
	return events


# --- Save / load ------------------------------------------------------------------------------

func autosave() -> Error:
	if campaign == null:
		return ERR_UNCONFIGURED
	var data := {
		"corporation_id": String(campaign.corporation_id),
		"campaign": campaign.to_dict(),
		"run": netrun.to_dict() if netrun != null and not netrun.run.is_over() else {},
		"rng": RngService.to_dict(),
		"saved_at": Time.get_unix_time_from_system(),
	}
	return SaveService.save_dict(save_path(), data)


## Summary of a campaign slot for the title screen ({} when empty): corporation, heat,
## ice, runs, state, in_run, saved_at.
func slot_summary(slot: String) -> Dictionary:
	var path := SaveService.campaign_path(slot)
	if not SaveService.has_save(path):
		return {}
	var data := SaveService.load_dict(path)
	var c: Dictionary = data.get("campaign", {})
	if c.is_empty():
		return {}
	var outcome := int(c.get("outcome", 0))
	return {"corporation": String(data.get("corporation_id", "")), "heat": int(c.get("heat", 0)), "ice": int(c.get("ice_level", 0)),
		"runs": int(c.get("runs_completed", 0)), "state": "won" if outcome == CampaignState.Outcome.WON else ("lost" if outcome == CampaignState.Outcome.LOST else "active"),
		"in_run": not data.get("run", {}).is_empty(), "saved_at": float(data.get("saved_at", 0.0))}


## The slot saved most recently ("" when none), among the numbered slots.
func latest_slot() -> String:
	var best := ""
	var best_time := -1.0
	for slot in SaveService.list_campaign_slots():
		if slot == "gut_test" or slot == "demo":
			continue
		var s := slot_summary(slot)
		if not s.is_empty() and float(s["saved_at"]) > best_time:
			best_time = float(s["saved_at"])
			best = slot
	return best


func delete_slot(slot: String) -> void:
	SaveService.delete_save(SaveService.campaign_path(slot))
	if slot == save_slot:
		campaign = null
		netrun = null


func quit_game() -> void:
	if campaign != null and not campaign.is_over():
		autosave()
	save_profile()
	if scene_switching_enabled:
		get_tree().quit()


func resume() -> bool:
	_ensure_resolver()
	if not has_save():
		return false
	var data := SaveService.load_dict(save_path())
	if data.is_empty() or not data.has("campaign"):
		return false
	campaign = CampaignState.from_dict(data["campaign"])
	corporation = lookup().get_content(StringName(String(data.get("corporation_id", DEFAULT_CORPORATION)))) as CorporationData
	if corporation != null and corporation.generated_from_profile and not campaign.generated.is_empty():
		corporation = build_generated(corporation.id, campaign.generated)
	if data.has("rng") and not data["rng"].is_empty():
		RngService.from_dict(data["rng"])
	var run_data: Dictionary = data.get("run", {})
	netrun = NetrunSession.from_dict(resolver, campaign, run_data, corporation) if not run_data.is_empty() else null
	_reset_profile_sync()
	campaign_changed.emit(campaign)
	run_changed.emit(netrun)
	return true


func save_profile() -> Error:
	return SaveService.save_dict(profile_path(), {"profile": profile.to_dict()})


func load_profile() -> void:
	if SaveService.has_save(profile_path()):
		var data := SaveService.load_dict(profile_path())
		profile = ProfileState.from_dict(data.get("profile", {}))
	else:
		profile = ProfileState.new()


func clear_run() -> void:
	netrun = null
	autosave()


func delete_save() -> void:
	SaveService.delete_save(save_path())
	SaveService.delete_save(profile_path())


# --- Scenes ----------------------------------------------------------------------------------

func change_scene(scene_path: String) -> void:
	SignalBus.scene_change_requested.emit(scene_path)
	if scene_switching_enabled:
		get_tree().change_scene_to_file(scene_path)


func go_to_title() -> void:
	if has_node("/root/Dialogue"):
		get_node("/root/Dialogue").clear()
	change_scene(TITLE_SCENE)


## Jack out (STYLE_GUIDE 5): wireframe dissolves back to the deck CRT.
func go_to_hq() -> void:
	if scene_switching_enabled:
		Fx.jack_out(func() -> void: change_scene(HQ_SCENE))
	else:
		change_scene(HQ_SCENE)


## Jack in: the camera pushes into the deck CRT and dissolves to wireframe.
func go_to_netrun() -> void:
	AudioDirector.play_sfx("jack_in")
	if scene_switching_enabled:
		Fx.jack_in(func() -> void: change_scene(NETRUN_SCENE))
	else:
		change_scene(NETRUN_SCENE)


func _ensure_resolver() -> void:
	if resolver == null:
		resolver = CombatEngine.make_resolver()
