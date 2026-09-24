class_name SiteData
extends Resource
## A Site on the City Grid. Used up once cleared, then claimable.

@export var id: StringName
@export var display_name: String
@export_range(1, 4) var tier: int = 1
## Open links to other Site ids.
@export var links: Array[StringName] = []
## Links opened by Intel Exploits or objectives. Raids can use them too once open.
@export var locked_links: Array[StringName] = []
@export var objective: RC.SiteObjective = RC.SiteObjective.NONE
@export var exploit_type: RC.ExploitType = RC.ExploitType.NONE
## Negative for Heat-reduction objectives (e.g. Scrub Records = -5).
@export var heat_change: int = 0
@export var claimable: bool = true
@export var map_position: Vector2


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if objective == RC.SiteObjective.EXPLOIT and exploit_type == RC.ExploitType.NONE:
		errors.append("Site %s is an EXPLOIT objective with no exploit_type." % id)
	if objective == RC.SiteObjective.HEAT_REDUCTION and heat_change >= 0:
		errors.append("Site %s reduces Heat but heat_change is not negative." % id)
	if id in links or id in locked_links:
		errors.append("Site %s links to itself." % id)
	return errors
