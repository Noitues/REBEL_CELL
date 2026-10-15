extends CampaignSimulator
## CampaignSimulator (the builtin CombatBot policy) that stops the campaign at the first moment its
## launch policy would send a crew to the Genome Core breach and keeps the campaign it stopped on.
## The builtin twin of tools/agent/boss_stop_simulator.gd (which stops the heuristic policy).

## The campaign at the stop (or at the run cap); read it after run_campaign().
var final_campaign: CampaignState = null
## True when the stop was the breach launch (false = the run cap or a loss came first).
var reached_breach: bool = false


func _pick_launch(c: CampaignState) -> Dictionary:
	var pick := super(c)
	if not pick.is_empty() and CampaignRules.run_kind_for(c, pick["site"]) == "boss":
		reached_breach = true
		return {}
	return pick


func _report(c: CampaignState, stats: Dictionary, campaign_seed: int, ice: int) -> Dictionary:
	final_campaign = c
	return super(c, stats, campaign_seed, ice)
