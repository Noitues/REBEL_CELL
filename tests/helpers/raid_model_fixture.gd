class_name RaidModelFixture
extends RefCounted
## Phase 2b: Solace plays the Infected Tide (CorporationData.raid_model "tide"), whose raid views arrive in Phase 3. The tests of the
## RESOLVER's raids and raid screens that use Solace content as their carrier (its Grid ids, its Sites) switch Solace to the
## resolver for the length of the test: `use_resolver()` in before_each, `restore()` in after_each. Only the test process sees it.

static var _saved: Dictionary = {}


## Switches `corp_id` (Solace by default) to the resolver model; `restore` undoes it.
static func use_resolver(corp_id: StringName = &"solace") -> void:
	var corp := ContentRegistry.get_content(corp_id) as CorporationData
	if corp == null:
		return
	if not _saved.has(corp_id):
		_saved[corp_id] = corp.raid_model
	corp.raid_model = CorporationData.RAID_MODEL_RESOLVER


## Puts every corporation switched by `use_resolver` back to the model it shipped with.
static func restore() -> void:
	for id in _saved.keys():
		var corp := ContentRegistry.get_content(id) as CorporationData
		if corp != null:
			corp.raid_model = _saved[id]
	_saved.clear()
