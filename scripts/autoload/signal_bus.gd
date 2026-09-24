extends Node
## SignalBus autoload: global event bridge only (TECH_SPEC §3). It holds no state.
## Views connect here to animate what the core reports; core code never touches it.

## Campaign Heat changed (CampaignState is the source of truth; this is a notification).
signal heat_changed(old_value: int, new_value: int)
## A Heat threshold was crossed for the first time (one-time events).
signal heat_threshold_crossed(threshold: HeatThresholdData)
## All content under res://content has been scanned and validated.
signal content_loaded(id_count: int, error_count: int)
## A campaign run started / ended. `result` is a plain dictionary (M2 defines its keys).
signal run_started(campaign_seed: int)
signal run_ended(result: Dictionary)
## Combat lifecycle (M1 defines the payloads).
signal combat_started
signal combat_ended(result: Dictionary)
## RunManager is about to switch scenes.
signal scene_change_requested(scene_path: String)
## SaveService wrote or failed to write a file.
signal save_completed(path: String)
signal save_failed(path: String, error: int)
