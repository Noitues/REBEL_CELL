class_name RouteHp
extends RefCounted
## W3-ROUTE (7A): what HP the operative carries along a netrun route. Moving between nodes
## never changes HP: only fights, event choices and Daemons do, and the run's end restores it
## fully at HQ (GDD: HP carries between fights, survivors heal fully at HQ). The route map
## shows this so the player sees what HP they arrive with and where they can heal. Pure reads
## of the run state; the map shows what the rules hold.


## The HP the operative arrives at the next node with: {"hp", "max_hp"}.
static func arrival(s: NetrunSession) -> Dictionary:
	if s == null or s.run == null or s.run.operative == null:
		return {"hp": 0, "max_hp": 0}
	return {"hp": s.run.operative.hp, "max_hp": s.run.operative.max_hp}


## True when node type `node_type` (RC.InfilNodeType) can heal the operative: Terminal events
## offer healing choices (e.g. the medbay).
static func heals_at(node_type: int) -> bool:
	return node_type == RC.InfilNodeType.TERMINAL or node_type == RC.InfilNodeType.REST
