class_name GridState
extends RefCounted
## Runtime state of the City Grid (GDD 3.1-3.3, 4.1): which Sites are cleared, claimed
## or Seized, the node installed on each claimed Site, its integrity and condition, the
## assets deployed there, the stationed operative, and links opened by Intel.
## Layout comes from CityGridData (content); this holds only what changes.

enum SiteStatus { CORPORATE, CLEARED, CLAIMED, SEIZED }
enum Condition { OK, DISABLED }

var home_site_id: StringName = &""
var home_integrity: int = 50
var home_max_integrity: int = 50
## site_id -> {"status": int, "node_type": String, "integrity": int, "max_integrity": int,
##             "condition": int, "assets": Array[String], "stationed": String}
var sites: Dictionary = {}
## Locked links opened by Intel, as "a|b" with a < b.
var opened_links: Array[String] = []


## Builds the opening state from a City Grid: home claimed with the home node, every
## other Site corporate.
static func from_grid(grid: CityGridData, home_node: NetworkNodeData) -> GridState:
	var g := GridState.new()
	g.home_site_id = grid.home_site_id
	g.home_max_integrity = home_node.integrity if home_node != null else 50
	g.home_integrity = g.home_max_integrity
	for site in grid.sites:
		if site == null:
			continue
		g.sites[site.id] = _blank()
	g.sites[grid.home_site_id]["status"] = SiteStatus.CLAIMED
	g.sites[grid.home_site_id]["node_type"] = "home_server"
	g.sites[grid.home_site_id]["integrity"] = g.home_max_integrity
	g.sites[grid.home_site_id]["max_integrity"] = g.home_max_integrity
	return g


static func _blank() -> Dictionary:
	return {"status": SiteStatus.CORPORATE, "node_type": "", "integrity": 0, "max_integrity": 0,
		"condition": Condition.OK, "assets": [], "stationed": ""}


func site(site_id: StringName) -> Dictionary:
	return sites.get(site_id, {})


func status_of(site_id: StringName) -> int:
	return int(site(site_id).get("status", SiteStatus.CORPORATE))


func is_home(site_id: StringName) -> bool:
	return site_id == home_site_id


func is_claimed(site_id: StringName) -> bool:
	return status_of(site_id) == SiteStatus.CLAIMED


func is_cleared(site_id: StringName) -> bool:
	return status_of(site_id) == SiteStatus.CLEARED


func is_seized(site_id: StringName) -> bool:
	return status_of(site_id) == SiteStatus.SEIZED


func is_corporate(site_id: StringName) -> bool:
	return status_of(site_id) == SiteStatus.CORPORATE


## Claimed Sites (home included) whose node is not Disabled.
func is_active_node(site_id: StringName) -> bool:
	return is_claimed(site_id) and int(site(site_id).get("condition", Condition.OK)) == Condition.OK


## Every claimed Site in id order (home first).
func claimed_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in _sorted_ids():
		if is_claimed(id) and id != home_site_id:
			out.append(id)
	out.push_front(home_site_id)
	return out


func node_type_of(site_id: StringName) -> StringName:
	return StringName(String(site(site_id).get("node_type", "")))


func assets_on(site_id: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for a in site(site_id).get("assets", []):
		out.append(StringName(String(a)))
	return out


func stationed_on(site_id: StringName) -> StringName:
	return StringName(String(site(site_id).get("stationed", "")))


## Neighbouring Site ids over open links plus opened locked links, sorted.
func neighbors(site_id: StringName, grid: CityGridData) -> Array[StringName]:
	var out := {}
	for s in grid.sites:
		if s == null:
			continue
		if s.id == site_id:
			for l in s.links:
				out[l] = true
			for l in s.locked_links:
				if is_link_open(s.id, l):
					out[l] = true
		elif s.links.has(site_id) or (s.locked_links.has(site_id) and is_link_open(s.id, site_id)):
			out[s.id] = true
	var ids: Array[StringName] = []
	for k in out.keys():
		ids.append(k)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return ids


static func link_key(a: StringName, b: StringName) -> String:
	return "%s|%s" % [a, b] if String(a) < String(b) else "%s|%s" % [b, a]


func is_link_open(a: StringName, b: StringName) -> bool:
	return opened_links.has(link_key(a, b))


func open_link(a: StringName, b: StringName) -> void:
	var key := link_key(a, b)
	if not opened_links.has(key):
		opened_links.append(key)


## Shortest hop distance between two Sites, or -1.
func distance(from: StringName, to: StringName, grid: CityGridData) -> int:
	if from == to:
		return 0
	var seen := {from: 0}
	var queue: Array[StringName] = [from]
	while not queue.is_empty():
		var cur: StringName = queue.pop_front()
		for n in neighbors(cur, grid):
			if seen.has(n):
				continue
			seen[n] = int(seen[cur]) + 1
			if n == to:
				return int(seen[n])
			queue.append(n)
	return -1


## Next Site on a shortest path from `from` to `to` (ties by site id), or `from`.
func next_hop(from: StringName, to: StringName, grid: CityGridData) -> StringName:
	if from == to:
		return from
	var best := from
	var best_d := distance(from, to, grid)
	if best_d < 0:
		return from
	for n in neighbors(from, grid):
		var d := distance(n, to, grid)
		if d >= 0 and d < best_d:
			best_d = d
			best = n
	return best


func _sorted_ids() -> Array[StringName]:
	var ids: Array[StringName] = []
	for k in sites.keys():
		ids.append(k)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return ids


func duplicate_state() -> GridState:
	return from_dict(to_dict())


func to_dict() -> Dictionary:
	var out := {}
	for id in _sorted_ids():
		out[String(id)] = sites[id].duplicate(true)
	return {"home_site_id": String(home_site_id), "home_integrity": home_integrity,
		"home_max_integrity": home_max_integrity, "sites": out, "opened_links": opened_links.duplicate()}


static func from_dict(d: Dictionary) -> GridState:
	var g := GridState.new()
	g.home_site_id = StringName(String(d.get("home_site_id", "")))
	g.home_integrity = int(d.get("home_integrity", 50))
	g.home_max_integrity = int(d.get("home_max_integrity", 50))
	for k in d.get("sites", {}):
		var s: Dictionary = d["sites"][k]
		var assets := []
		for a in s.get("assets", []):
			assets.append(String(a))
		g.sites[StringName(String(k))] = {"status": int(s.get("status", 0)), "node_type": String(s.get("node_type", "")),
			"integrity": int(s.get("integrity", 0)), "max_integrity": int(s.get("max_integrity", 0)),
			"condition": int(s.get("condition", 0)), "assets": assets, "stationed": String(s.get("stationed", ""))}
	for l in d.get("opened_links", []):
		g.opened_links.append(String(l))
	return g
