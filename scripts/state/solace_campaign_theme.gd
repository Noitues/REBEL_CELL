class_name SolaceCampaignTheme
extends CorpThemeBlock
## Solace's campaign block (Phase 2b): the Infected Tide's state (SOLACE_RAID_SPEC.md sections 1 and 9). It replaces the
## v2 population figure `infection_bp` (R-G). `tide` is null until a campaign of a `raid_model` "tide" corporation
## starts it (CampaignRules.new_campaign), so every other corporation's block stays default and is left out of the save.
## Only the tide block is saved (`SolaceTideState.block_dict`); the campaign fields the tide reads are the campaign's.

var tide: SolaceTideState = null


## The tide block, or {} for no tide. Overrides the field walk: the state is not a CorpThemeBlock.
func to_dict() -> Dictionary:
	if tide == null:
		return {}
	return {"tide": tide.block_dict()}


func is_default() -> bool:
	return tide == null


func load_dict(d: Dictionary) -> void:
	var raw: Variant = d.get("tide", null)
	tide = SolaceTideState.from_block(raw) if raw is Dictionary else null


## A deep copy (the tide's block only: the working view is rebuilt from the campaign).
func copy() -> CorpThemeBlock:
	var c := SolaceCampaignTheme.new()
	if tide != null:
		c.tide = SolaceTideState.from_block(tide.block_dict())
	return c
