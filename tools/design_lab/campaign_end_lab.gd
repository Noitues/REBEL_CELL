extends Control
## Art pass W8d: the campaign's end T4 in context, for Movie Maker frame strips. Opens the
## HQ on a demo campaign (its own save slot, deleted after), waits for the city's bake,
## then shows the end page so its sequence plays, and prints the frame it starts on
## ("campaign_end_lab: <won|lost> starts on frame N") for tools/design_lab/frame_strip.py.
## Windowed only (tools/run_windowed.py), e.g.:
##   python tools/run_windowed.py --log <log> -- --path . --write-movie <dir>/f.png
##     --fixed-fps 30 --quit-after 150 res://tools/design_lab/campaign_end_lab.tscn -- --end=won
## Args: --end=won|lost, --dead=N (operatives flatlined first), --seed=N, --reduce-effects.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SLOT := "w8d_lab"
## Frames the page waits to settle, and the most it waits for the bake.
const SETTLE_FRAMES := 20
const BAKE_FRAMES := 300


func _ready() -> void:
	var won := true
	var dead := 1
	var seed := 7
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--end="):
			won = a.trim_prefix("--end=") != "lost"
		elif a.begins_with("--dead="):
			dead = a.trim_prefix("--dead=").to_int()
		elif a.begins_with("--seed="):
			seed = a.trim_prefix("--seed=").to_int()
		elif a == "--reduce-effects":
			Settings.set_reduce_effects(true)
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	var hq: Control = load(HQ).instantiate()
	add_child(hq)
	await get_tree().process_frame
	hq.new_campaign(seed)
	for f in SETTLE_FRAMES:
		await get_tree().process_frame
	for f in BAKE_FRAMES:
		if CityBakeCache.busy() == 0:
			break
		await get_tree().process_frame
	var c := RunManager.campaign
	c.story_beats_revealed = 99
	for i in mini(dead, c.roster.size()):
		c.roster[i].alive = false
	c.outcome = CampaignState.Outcome.WON if won else CampaignState.Outcome.LOST
	print("campaign_end_lab: %s starts on frame %d" % ["won" if won else "lost", Engine.get_frames_drawn()])
	hq.show_end()


func _exit_tree() -> void:
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
