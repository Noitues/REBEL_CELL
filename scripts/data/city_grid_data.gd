class_name CityGridData
extends Resource
## A corporation's City Grid (4.4). Links are undirected.

@export var sites: Array[SiteData] = []
@export var home_site_id: StringName
@export var boss_site_id: StringName


func get_site(site_id: StringName) -> SiteData:
	for s in sites:
		if s and s.id == site_id:
			return s
	return null


func validate(min_exploits: int = 3) -> PackedStringArray:
	var errors := PackedStringArray()
	var by_id := {}
	for s in sites:
		if s == null:
			errors.append("Grid has an empty site entry.")
			continue
		if by_id.has(s.id):
			errors.append("Duplicate site id %s." % s.id)
		by_id[s.id] = s
		errors.append_array(s.validate())
	# Links point at real sites.
	for s in by_id.values():
		for l in s.links + s.locked_links:
			if not by_id.has(l):
				errors.append("Site %s links to missing site %s." % [s.id, l])
	if not by_id.has(home_site_id):
		errors.append("Home site %s not found." % home_site_id)
	if not by_id.has(boss_site_id):
		errors.append("Boss site %s not found." % boss_site_id)
	elif by_id[boss_site_id].objective != RC.SiteObjective.BOSS:
		errors.append("Boss site %s does not have objective BOSS." % boss_site_id)
	# Tier chains: each T1 opens at most one T2.
	for s in by_id.values():
		if s.tier == 1:
			var t2 := 0
			for l in s.links:
				if by_id.has(l) and by_id[l].tier == 2:
					t2 += 1
			if t2 > 1:
				errors.append("T1 site %s opens %d T2 sites (max 1)." % [s.id, t2])
	# Enough Exploits.
	var exploits := 0
	for s in by_id.values():
		if s.objective == RC.SiteObjective.EXPLOIT:
			exploits += 1
	if exploits < min_exploits:
		errors.append("Grid has %d Exploit sites, needs %d." % [exploits, min_exploits])
	# Boss reachable from home over open + locked links.
	if by_id.has(home_site_id) and by_id.has(boss_site_id):
		var adj := {}
		for s in by_id.values():
			for l in s.links + s.locked_links:
				if by_id.has(l):
					adj.get_or_add(s.id, []).append(l)
					adj.get_or_add(l, []).append(s.id)
		var seen := {home_site_id: true}
		var queue: Array = [home_site_id]
		while not queue.is_empty():
			var cur = queue.pop_front()
			for n in adj.get(cur, []):
				if not seen.has(n):
					seen[n] = true
					queue.append(n)
		if not seen.has(boss_site_id):
			errors.append("Boss site is unreachable from home.")
	return errors


func size_warnings() -> PackedStringArray:
	var w := PackedStringArray()
	if sites.size() < 30 or sites.size() > 40:
		w.append("Grid has %d sites; target is 30-40." % sites.size())
	return w
