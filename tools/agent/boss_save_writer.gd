class_name BossSaveWriter
extends RefCounted
## Writes a campaign through the game's own save path (the RunManager.autosave() layout, via
## the SaveService autoload's save_dict) into any folder: campaign_<slot>.json plus a profile.json, so the title's
## CONTINUE and slot list load it. Tools only (change plan 1 V4).


## Writes `c` as slot `slot` under `out_dir`. `rng` is the RngService autoload (its state is saved
## so a resumed campaign draws the same numbers). Returns OK or the file error.
static func write(save_service: Node, rng: Node, c: CampaignState, out_dir: String, slot: String) -> Error:
	rng.seed_campaign(c.campaign_seed)
	var data := {
		"corporation_id": String(c.corporation_id),
		"campaign": c.to_dict(),
		"run": {},
		"rng": rng.to_dict(),
		"saved_at": Time.get_unix_time_from_system(),
	}
	var err: Error = save_service.save_dict(out_dir.path_join(save_service.CAMPAIGN_FILE_FORMAT % slot), data)
	if err != OK:
		return err
	var profile := ProfileState.new()
	profile.campaigns_started = 1
	return save_service.save_dict(out_dir.path_join(save_service.PROFILE_FILE), {"profile": profile.to_dict(), "slots": [slot]})


## The one-line summary: seed, run number, Heat, crew with Rank and HP, deck size, Firmware, Daemons, Schematics.
static func summary(c: CampaignState) -> String:
	var crew := PackedStringArray()
	var deck := 0
	var firmware := 0
	var daemons := 0
	for op in c.living_operatives():
		crew.append("%s R%d %d/%d HP" % [op.name, op.rank, op.hp, op.max_hp])
		deck += op.deck.size()
		firmware += op.slot_firmware_ids.size()
		daemons += op.daemon_ids.size()
	return "seed %d, run %d, Heat %d, crew [%s], deck %d, Firmware %d, Daemons %d, Schematics %d, Exploits %d" % [
		c.campaign_seed, c.runs_completed, c.heat, "; ".join(crew), deck, firmware, daemons, c.schematics, c.exploits.size()]
