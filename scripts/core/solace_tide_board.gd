class_name SolaceTideBoard
extends RefCounted
## The Solace raid's board (the Infected Tide, H5; docs/handoff/raid_integration/SOLACE_RAID_SPEC.md section 1): the
## City Grid seen as a graph of Sites, built once per campaign. Pure data, no randomness, no state.
##
## A raid line runs Genome Core -> HOME through the Sites ("routes") or across the spokes ("streets", never HOME).
## Route pool = every simple path from the core to HOME of at most `max_links` links, base and locked links alike
## (R-B). A spoke is the chain T1 -> T2 -> T3 that starts at one HOME link; objective (Heat) Sites are not on a chain.
## Every list is sorted by site id (text order), so the board is the same for the same grid.

## The Genome Core and HOME node ids (not in `sites`).
var core: StringName = &""
var home: StringName = &""
## The raid Sites (everything but HOME and the core), sorted by id.
var sites: Array[StringName] = []
## site -> tier (int), site -> Exploit Site (bool), objective Site -> its Heat change (int, negative).
var tier: Dictionary = {}
var exploit: Dictionary = {}
var objective_heat: Dictionary = {}
## Undirected adjacency, node -> sorted Array[StringName] (HOME and the core included): base links, and base plus locked.
var base_adj: Dictionary = {}
var all_adj: Dictionary = {}
## site -> spoke key (the spoke's T1 Site id); spoke key -> {tier (int) -> Site} for the main chain only.
var spoke_of: Dictionary = {}
var chain: Dictionary = {}
## Every core -> HOME route of at most the max links, each an Array[StringName] of Sites (core side first, no core,
## no HOME), sorted.
var route_pool: Array = []


## Builds the board from the golden's graph form (`graph` of solace_raid_golden.json): {"core", "home_links",
## "sites": {id: {"tier", "links", "locked", "exploit", "objective_heat"}}}. HOME is "home".
static func from_dict(g: Dictionary, max_links: int) -> SolaceTideBoard:
	var rows := {}
	var base_pairs: Array = []
	var locked_pairs: Array = []
	var home_id := &"home"
	var core_id := StringName(String(g.get("core", "core")))
	for k in (g["sites"] as Dictionary).keys():
		var s: Dictionary = g["sites"][k]
		var id := StringName(String(k))
		rows[id] = {"tier": int(s["tier"]), "exploit": bool(s["exploit"]), "heat": int(s["objective_heat"])}
		for l in s["links"]:
			base_pairs.append([id, StringName(String(l))])
		for l in s["locked"]:
			locked_pairs.append([id, StringName(String(l))])
	for l in g["home_links"]:
		base_pairs.append([home_id, StringName(String(l))])
	return _build(rows, base_pairs, locked_pairs, home_id, core_id, max_links)


## Builds the board from a corporation's City Grid (CityGridData): the boss Site is the Genome Core, HOME is the grid's
## home Site, an EXPLOIT objective is an Exploit Site and a HEAT_REDUCTION objective an objective Site.
static func from_grid(grid: CityGridData, max_links: int) -> SolaceTideBoard:
	var rows := {}
	var base_pairs: Array = []
	var locked_pairs: Array = []
	for s in grid.sites:
		if s == null:
			continue
		if s.id != grid.home_site_id and s.id != grid.boss_site_id:
			rows[s.id] = {"tier": s.tier, "exploit": s.objective == RC.SiteObjective.EXPLOIT,
				"heat": s.heat_change if s.objective == RC.SiteObjective.HEAT_REDUCTION else 0}
		for l in s.links:
			base_pairs.append([s.id, l])
		for l in s.locked_links:
			locked_pairs.append([s.id, l])
	return _build(rows, base_pairs, locked_pairs, grid.home_site_id, grid.boss_site_id, max_links)


static func _build(rows: Dictionary, base_pairs: Array, locked_pairs: Array, home_id: StringName, core_id: StringName,
		max_links: int) -> SolaceTideBoard:
	var b := SolaceTideBoard.new()
	b.home = home_id
	b.core = core_id
	var ids: Array = rows.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		b.sites.append(id)
		b.tier[id] = int(rows[id]["tier"])
		b.exploit[id] = bool(rows[id]["exploit"])
		if int(rows[id]["heat"]) != 0:
			b.objective_heat[id] = int(rows[id]["heat"])
	b.base_adj = _adjacency(base_pairs)
	b.all_adj = _adjacency(base_pairs + locked_pairs)
	b._build_spokes()
	b.route_pool = b._paths(max_links)
	return b


static func _adjacency(pairs: Array) -> Dictionary:
	var sets := {}
	for p in pairs:
		var a: StringName = p[0]
		var c: StringName = p[1]
		sets.get_or_add(a, {})[c] = true
		sets.get_or_add(c, {})[a] = true
	var out := {}
	for k in sets.keys():
		var arr: Array = (sets[k] as Dictionary).keys()
		IdSort.sort_ids(arr)
		out[k] = arr
	return out


## The spokes: each T1 Site next to HOME starts one; the chain follows the base link to the next tier's Site. An
## objective Site belongs to the spoke of its lowest-id chain neighbor.
func _build_spokes() -> void:
	for t1 in base_adj.get(home, []):
		if not tier.has(t1) or int(tier[t1]) != 1 or objective_heat.has(t1):
			continue
		var cur: StringName = t1
		chain[t1] = {1: t1}
		spoke_of[t1] = t1
		for t in [2, 3]:
			var nxt: StringName = &""
			for n in base_adj.get(cur, []):
				if tier.has(n) and int(tier[n]) == t and not objective_heat.has(n):
					nxt = n
					break
			if nxt == &"":
				break
			(chain[t1] as Dictionary)[t] = nxt
			spoke_of[nxt] = t1
			cur = nxt
	for o in objective_heat.keys():
		var best: StringName = &""
		for n in base_adj.get(o, []):
			if spoke_of.has(n) and (best == &"" or String(spoke_of[n]) < String(best)):
				best = spoke_of[n]
		if best != &"":
			spoke_of[o] = best


## Every simple path core -> HOME with at most `max_links` links over `all_adj`, as the Site list (core side first).
func _paths(max_links: int) -> Array:
	var out: Array = []
	var path: Array[StringName] = []
	var seen := {core: true}
	_walk(core, path, seen, max_links, out)
	out.sort_custom(path_less)
	return out


func _walk(node: StringName, path: Array[StringName], seen: Dictionary, max_links: int, out: Array) -> void:
	if path.size() > max_links:
		return
	for n in all_adj.get(node, []):
		if n == home:
			if not path.is_empty() and path.size() + 1 <= max_links:
				out.append(path.duplicate())
			continue
		if seen.has(n) or n == core:
			continue
		seen[n] = true
		path.append(n)
		_walk(n, path, seen, max_links, out)
		path.pop_back()
		seen.erase(n)


## Lexicographic order of two Site lists (text order, a prefix first).
static func path_less(a: Array, b: Array) -> bool:
	var n := mini(a.size(), b.size())
	for i in n:
		var x := String(a[i])
		var y := String(b[i])
		if x != y:
			return x < y
	return a.size() < b.size()


## The spoke keys of the Sites in `cells` (sorted, unique).
func spokes_of(cells: Array) -> Array:
	var seen := {}
	for s in cells:
		if spoke_of.has(s):
			seen[spoke_of[s]] = true
	var out: Array = seen.keys()
	IdSort.sort_ids(out)
	return out


## The tier-`t` ring of `spokes` (sorted): the main-chain Sites of tier t, spoke by spoke.
func ring_at(spokes: Array, t: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for sp in spokes:
		var ch: Dictionary = chain.get(sp, {})
		if ch.has(t):
			out.append(ch[t])
	return out


## The street pool of a raid: the T1, T2 and T3 rings over the spokes of the candidates' cells, then for every other
## spoke that holds a live owned Site its segment T3 -> T2 -> T1 (at least 2 Sites). `owned` = site -> condition
## (SolaceTideState.Cond; a TAKEN Site is not live). Duplicates are dropped, the order is kept. Returns Array of
## Array[StringName].
func street_pool(cand_cells: Array, owned: Dictionary) -> Array:
	var flat: Array = []
	for cells in cand_cells:
		flat.append_array(cells)
	var spokes := spokes_of(flat)
	var pool: Array = []
	for t in [1, 2, 3]:
		var ring := ring_at(spokes, t)
		if not ring.is_empty():
			pool.append(ring)
	var live := {}
	for s in owned.keys():
		if int(owned[s]) != SolaceTideState.Cond.TAKEN and spoke_of.has(s) and not spokes.has(spoke_of[s]):
			live[spoke_of[s]] = true
	var live_spokes: Array = live.keys()
	IdSort.sort_ids(live_spokes)
	for sp in live_spokes:
		var ch: Dictionary = chain.get(sp, {})
		var seg: Array[StringName] = []
		for t in [3, 2, 1]:
			if ch.has(t):
				seg.append(ch[t])
		if seg.size() >= 2:
			pool.append(seg)
	var out: Array = []
	for p in pool:
		var dup := false
		for q in out:
			if _same(p, q):
				dup = true
				break
		if not dup:
			out.append(p)
	return out


static func _same(a: Array, b: Array) -> bool:
	if a.size() != b.size():
		return false
	for i in a.size():
		if a[i] != b[i]:
			return false
	return true
