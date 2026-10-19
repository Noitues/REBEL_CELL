class_name SaveMigration
extends RefCounted
## Save format steps and checks (TECH_SPEC §8), pure: SaveService registers the steps and
## runs the check on every load. Plan 2 N8 (save v3): a wheel's slot statuses carry ×N
## stacks. v2 stored one RC.Status int per slot ("slice_statuses"); v3 stores one
## {"<status int>": stacks} per slot ("slice_stacks"), keys in RC.Status order.

## Load refusals, each a stable code (SaveService.last_error).
const ERR_TOO_NEW := "save_version_too_new"
const ERR_STACK_COUNT := "invalid_stack_count"
const ERR_UNKNOWN_STATUS := "unknown_status"
const ERR_STACKS_SHAPE := "invalid_stacks_shape"
const ERR_NO_STEP := "no_migration_step"
## Plan 2 N12 (save v4): a wheel's "slot_sizes" that is not one 0-30 int per slot summing to 30.
const ERR_SLOT_SIZES := "invalid_slot_sizes"
## Plan 2 N12: the v4 wheel key (absent for an equal layout).
const V4_SIZES_KEY := "slot_sizes"
## The v2 and v3 wheel keys.
const V2_KEY := "slice_statuses"
const V3_KEY := "slice_stacks"


## v2 -> v3: every wheel dictionary anywhere in `data` (operative, enemies, satellites,
## drones, the rewind checkpoint, a run's saved fight) trades its "slice_statuses" for
## "slice_stacks": NONE -> no stacks, PARASITE -> OUTPUT_DOWN x `parasite_stacks` (R8;
## CampaignConfigData.parasite_output_down_stacks), any other status -> one stack. A status
## int v2 never had is kept as one stack of it, for validate_v3 to refuse. Pure: returns a
## new dictionary; data without "slice_statuses" (v3 already) comes back equal.
static func v2_to_v3(data: Dictionary, parasite_stacks: int) -> Dictionary:
	return _walk(data.duplicate(true), parasite_stacks)


static func _walk(v: Variant, parasite_stacks: int) -> Variant:
	if v is Dictionary:
		var d: Dictionary = v
		if d.has(V2_KEY) and d[V2_KEY] is Array:
			var stacks := []
			for s in d[V2_KEY]:
				stacks.append(_slot_v3(int(s), parasite_stacks))
			d.erase(V2_KEY)
			d[V3_KEY] = stacks
		for k in d.keys():
			d[k] = _walk(d[k], parasite_stacks)
		return d
	if v is Array:
		var a: Array = v
		for i in a.size():
			a[i] = _walk(a[i], parasite_stacks)
		return a
	return v


static func _slot_v3(status: int, parasite_stacks: int) -> Dictionary:
	if status == RC.Status.NONE:
		return {}
	if status == RC.Status.PARASITE:
		return {str(RC.Status.OUTPUT_DOWN): parasite_stacks}
	return {str(status): 1}


## v3 -> v4 (plan 2 N12): wheels gain an optional "slot_sizes" (written only for an uneven
## layout). A v3 wheel has equal slots, which v4 reads from its absence, so the step changes
## nothing. Pure: returns a copy.
static func v3_to_v4(data: Dictionary) -> Dictionary:
	return data.duplicate(true)


## Checks v4 `data`: validate_v3's stack checks, then every wheel's "slot_sizes" (an Array of
## whole numbers 0-30, one per slot of "slot_slice_ids", summing to 30; ERR_SLOT_SIZES).
static func validate_v4(data: Variant) -> String:
	var err := validate_v3(data)
	return err if err != "" else _check_sizes(data)


static func _check_sizes(data: Variant) -> String:
	if data is Array:
		for item in data:
			var err := _check_sizes(item)
			if err != "":
				return err
		return ""
	if not (data is Dictionary):
		return ""
	var d: Dictionary = data
	if d.has(V4_SIZES_KEY):
		var sizes: Variant = d[V4_SIZES_KEY]
		if not (sizes is Array) or (sizes as Array).size() != (d.get("slot_slice_ids", []) as Array).size():
			return ERR_SLOT_SIZES
		var total := 0
		for n in sizes:
			if not (n is int or n is float) or float(n) != floorf(float(n)) or float(n) < 0.0 or float(n) > RC.TICKS:
				return ERR_SLOT_SIZES
			total += int(n)
		if total != RC.TICKS:
			return ERR_SLOT_SIZES
	for k in d.keys():
		var err := _check_sizes(d[k])
		if err != "":
			return err
	return ""


## Checks every "slice_stacks" in v3 `data`. Returns "" when sound, else a code: a slot that
## is not a dictionary (ERR_STACKS_SHAPE), a key that is not a stored status
## (ERR_UNKNOWN_STATUS: RC.STORED_STATUSES; NONE and the retired PARASITE are refused) or a
## count that is not a whole number of at least 1 (ERR_STACK_COUNT). A leftover v2
## "slice_statuses" is ERR_STACKS_SHAPE too.
static func validate_v3(data: Variant) -> String:
	if data is Array:
		for item in data:
			var err := validate_v3(item)
			if err != "":
				return err
		return ""
	if not (data is Dictionary):
		return ""
	var d: Dictionary = data
	if d.has(V2_KEY):
		return ERR_STACKS_SHAPE
	if d.has(V3_KEY):
		if not (d[V3_KEY] is Array):
			return ERR_STACKS_SHAPE
		for slot in d[V3_KEY]:
			var err := _check_slot(slot)
			if err != "":
				return err
	for k in d.keys():
		if k == V3_KEY:
			continue
		var err := validate_v3(d[k])
		if err != "":
			return err
	return ""


static func _check_slot(slot: Variant) -> String:
	if not (slot is Dictionary):
		return ERR_STACKS_SHAPE
	for k in (slot as Dictionary).keys():
		var key := str(k)
		if not key.is_valid_int() or not (key.to_int() in RC.STORED_STATUSES):
			return ERR_UNKNOWN_STATUS
		var n: Variant = slot[k]
		if not (n is int or n is float) or float(n) != floorf(float(n)) or float(n) < 1.0:
			return ERR_STACK_COUNT
	return ""
