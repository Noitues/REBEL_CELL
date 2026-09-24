extends Node
## RunManager autoload: owns the CampaignState and the active NetrunSession, saves and
## resumes them through SaveService, and switches scenes (TECH_SPEC §3, §8).
## ProfileState arrives in M3.

signal campaign_changed(campaign: CampaignState)
signal run_changed(netrun: NetrunSession)
signal run_ended(netrun: NetrunSession)

const DEFAULT_SLOT := "current"

var profile_state: RefCounted = null
var campaign: CampaignState = null
var netrun: NetrunSession = null
var resolver: CombatResolver = null
## Save slot name; tests use their own so they never touch a player's save.
var save_slot: String = DEFAULT_SLOT


func _ready() -> void:
	if resolver == null and ContentRegistry.config != null:
		resolver = CombatEngine.make_resolver()


func has_active_run() -> bool:
	return netrun != null and not netrun.run.is_over()


func save_path() -> String:
	return SaveService.campaign_path(save_slot)


func has_save() -> bool:
	return SaveService.has_save(save_path())


## Forgets everything in memory (the save file stays).
func reset() -> void:
	campaign = null
	netrun = null


## Starts a fresh campaign with the GDD 5.4 opening: 2 rookies, starting Schematics.
func new_campaign(campaign_seed: int, class_id: StringName = &"breaker") -> CampaignState:
	_ensure_resolver()
	campaign = CampaignState.new()
	campaign.campaign_seed = campaign_seed
	campaign.schematics = resolver.config.starting_schematics
	var cls := resolver.lookup.get_content(class_id) as ClassData
	for i in resolver.config.starting_rookies:
		campaign.recruit(cls)
	netrun = null
	RngService.seed_campaign(campaign_seed)
	SignalBus.run_started.emit(campaign_seed)
	campaign_changed.emit(campaign)
	autosave()
	return campaign


## Launches a netrun for `operative_id` (default: the first living operative).
func start_run(operative_id: StringName = &"", tier: int = 1, site_id: StringName = &"t1_a") -> NetrunSession:
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
	var run_seed := RngService.get_stream(&"map").randi() if RngService.is_seeded() else campaign.campaign_seed + campaign.runs_started
	netrun = NetrunSession.start(resolver, campaign, operative_id, tier, site_id, run_seed)
	run_changed.emit(netrun)
	autosave()
	return netrun


## Called by the UI after any run step; saves and announces the end of a run.
func after_step() -> void:
	autosave()
	if netrun != null and netrun.run.is_over():
		run_ended.emit(netrun)
	run_changed.emit(netrun)


## Writes campaign + run (+ campaign RNG streams) to the save slot.
func autosave() -> Error:
	if campaign == null:
		return ERR_UNCONFIGURED
	var data := {
		"campaign": campaign.to_dict(),
		"run": netrun.to_dict() if netrun != null and not netrun.run.is_over() else {},
		"rng": RngService.to_dict(),
	}
	return SaveService.save_dict(save_path(), data)


## Loads the save slot. Returns false when there is nothing to resume.
func resume() -> bool:
	_ensure_resolver()
	if not has_save():
		return false
	var data := SaveService.load_dict(save_path())
	if data.is_empty() or not data.has("campaign"):
		return false
	campaign = CampaignState.from_dict(data["campaign"])
	if data.has("rng") and not data["rng"].is_empty():
		RngService.from_dict(data["rng"])
	var run_data: Dictionary = data.get("run", {})
	netrun = NetrunSession.from_dict(resolver, campaign, run_data) if not run_data.is_empty() else null
	campaign_changed.emit(campaign)
	run_changed.emit(netrun)
	return true


## Drops the finished run (the campaign stays).
func clear_run() -> void:
	netrun = null
	autosave()


func delete_save() -> void:
	SaveService.delete_save(save_path())


## Switches to the scene at `scene_path`, announcing it on the SignalBus first.
func change_scene(scene_path: String) -> void:
	SignalBus.scene_change_requested.emit(scene_path)
	get_tree().change_scene_to_file(scene_path)


func _ensure_resolver() -> void:
	if resolver == null:
		resolver = CombatEngine.make_resolver()
