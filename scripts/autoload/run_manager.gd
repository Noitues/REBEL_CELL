extends Node
## RunManager autoload: owns ProfileState, CampaignState and the active RunState and
## drives scene transitions (TECH_SPEC §3). M0 skeleton: the state classes arrive in
## M1–M3, so the holders are untyped for now.

var profile_state: RefCounted = null
var campaign_state: RefCounted = null
var run_state: RefCounted = null


## True while a netrun is in progress.
func has_active_run() -> bool:
	return run_state != null


## Seeds every RNG stream for a campaign and announces the start.
func start_campaign(campaign_seed: int) -> void:
	RngService.seed_campaign(campaign_seed)
	SignalBus.run_started.emit(campaign_seed)


## Switches to the scene at `scene_path`, announcing it on the SignalBus first.
func change_scene(scene_path: String) -> void:
	SignalBus.scene_change_requested.emit(scene_path)
	get_tree().change_scene_to_file(scene_path)
