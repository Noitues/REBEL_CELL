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

## Starts a fresh campaign against `corporation_id` (GDD 5.4 opening).
func new_campaign(campaign_seed: int, corporation_id: StringName = DEFAULT_CORPORATION) -> CampaignState:
	_ensure_resolver()
	corporation = lookup().get_content(corporation_id) as CorporationData
	var home := lookup().get_content(DEFAULT_HOME) as HomeServerVariantData
	campaign = CampaignRules.new_campaign(corporation, config(), lookup(), campaign_seed, class_data(), home.core if home != null else null)
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


func launch_error(operative_id: StringName, site_id: StringName) -> String:
	if campaign == null:
		return "No campaign."
	var site := CampaignRules.site_data(corporation, site_id)
	if site == null:
		return "No such Site."
	return CampaignRules.launch_error(campaign, corporation, config(), campaign.get_operative(operative_id), class_data(), site)


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
	if netrun.run.outcome == RunState.Outcome.COMPLETED:
		profile.runs_completed += 1
	elif netrun.run.outcome == RunState.Outcome.DIED:
		profile.operatives_lost += 1
	sync_profile_with_campaign()


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
	}
	return SaveService.save_dict(save_path(), data)


func resume() -> bool:
	_ensure_resolver()
	if not has_save():
		return false
	var data := SaveService.load_dict(save_path())
	if data.is_empty() or not data.has("campaign"):
		return false
	campaign = CampaignState.from_dict(data["campaign"])
	corporation = lookup().get_content(StringName(String(data.get("corporation_id", DEFAULT_CORPORATION)))) as CorporationData
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


func go_to_hq() -> void:
	change_scene(HQ_SCENE)


func go_to_netrun() -> void:
	change_scene(NETRUN_SCENE)


func _ensure_resolver() -> void:
	if resolver == null:
		resolver = CombatEngine.make_resolver()
