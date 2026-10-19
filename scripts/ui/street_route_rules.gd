class_name StreetRouteRules
extends RefCounted
## NA-23: the pure rules of the street netrun view: the key map, the view states and what Esc / Z do in them, the node and
## link states of a run, the hovered branch, and the TARGET edge-arrow switch (PIPELINE_SPEC 9.2, 9.4, 9.5b). No Nodes, no game
## state: the screen feeds it the run's graph and position and draws what it answers.

enum View { OVERVIEW, DECISION, HOVER }
enum Esc { NONE, CLEAR_FOCUS, BACK_TO_DECISION, PAUSE }

const STATE_WALKED := "walked"
const STATE_NEXT := "next"
const STATE_LATER := "later"
const STATE_CUT := "cut"
const LINK_WALKED := "walked"
const LINK_OPTION := "option"
const LINK_AHEAD := "ahead"
const LINK_PAST := "past"


## The option a number key selects: keys 1-9 (top row or keypad) pick the n-th option; "" for any other key or a number past the
## options.
static func option_for_key(keycode: int, options: Array) -> String:
	var n := -1
	if keycode >= KEY_1 and keycode <= KEY_9:
		n = keycode - KEY_1
	elif keycode >= KEY_KP_1 and keycode <= KEY_KP_9:
		n = keycode - KEY_KP_1
	if n < 0 or n >= options.size():
		return ""
	return String(options[n])


## Z flips OVERVIEW and DECISION (HOVER counts as DECISION: it returns to OVERVIEW).
static func toggled(view: int) -> int:
	return View.DECISION if view == View.OVERVIEW else View.OVERVIEW


## What Esc does: first it lets go of a hover / selection, then leaves OVERVIEW for DECISION, else opens the pause menu.
static func esc_action(view: int, has_focus: bool) -> int:
	if has_focus:
		return Esc.CLEAR_FOCUS
	if view == View.OVERVIEW:
		return Esc.BACK_TO_DECISION
	return Esc.PAUSE


## The view the screen shows: HOVER only in DECISION with a focused option.
static func view_for(base: int, hovered_option: bool) -> int:
	if base == View.DECISION and hovered_option:
		return View.HOVER
	return base


## The layer (1-based) of node `id` in `run_graph` (0 when unknown or "").
static func layer_of(run_graph: Dictionary, id: String) -> int:
	if id == "":
		return 0
	for n: Dictionary in run_graph["nodes"]:
		if String(n["id"]) == id:
			return int(n["layer"])
	return 0


## The walked set: the visited nodes plus the one the run stands on.
static func walked_set(current: String, visited: Array) -> Dictionary:
	var out: Dictionary = {}
	for v: Variant in visited:
		out[String(v)] = true
	if current != "":
		out[current] = true
	return out


## The state of a node's sticker: walked (visited or here), next (a choice), cut (behind the run and not walked: the run never goes
## back) or later.
static func node_state(run_graph: Dictionary, id: String, current: String, visited: Array, options: Array) -> String:
	var walked := walked_set(current, visited)
	if walked.has(id):
		return STATE_WALKED
	if options.has(id):
		return STATE_NEXT
	if layer_of(run_graph, id) <= layer_of(run_graph, current):
		return STATE_CUT
	return STATE_LATER


## The state of the link `a` -> `b` (9.2): walked (both walked), option (from here to a choice), past (behind the run) or ahead.
static func link_state(run_graph: Dictionary, a: String, b: String, current: String, visited: Array, options: Array) -> String:
	var walked := walked_set(current, visited)
	if walked.has(a) and walked.has(b):
		return LINK_WALKED
	if a == current and options.has(b):
		return LINK_OPTION
	if layer_of(run_graph, b) <= layer_of(run_graph, current):
		return LINK_PAST
	return LINK_AHEAD


## The hovered branch (9.4 rule 1): node `id` and every node reachable from it, sorted by id.
static func branch_of(run_graph: Dictionary, id: String) -> Array:
	var seen: Dictionary = {id: true}
	var todo: Array = [id]
	while not todo.is_empty():
		var n: String = todo.pop_back()
		for e: Dictionary in run_graph["edges"]:
			if String(e["a"]) == n and not seen.has(String(e["b"])):
				seen[String(e["b"])] = true
				todo.append(String(e["b"]))
	var out: Array = seen.keys()
	IdSort.sort_ids(out)
	return out


## The last node of the graph: the run's TARGET (the final Rack; the first node of the last layer).
static func target_of(run_graph: Dictionary) -> String:
	var last := int(run_graph["layers"])
	var best := ""
	for n: Dictionary in run_graph["nodes"]:
		if int(n["layer"]) == last and (best == "" or IdSort.less(String(n["id"]), best)):
			best = String(n["id"])
	return best


## The share of `box` (a screen rect) inside `area`, 0..1 (an empty box counts 0).
static func visible_share(box: Rect2, area: Rect2) -> float:
	if box.size.x <= 0.0 or box.size.y <= 0.0:
		return 0.0
	var inter := box.intersection(area)
	if inter.size.x <= 0.0 or inter.size.y <= 0.0:
		return 0.0
	return (inter.size.x * inter.size.y) / (box.size.x * box.size.y)


## Whether the TARGET edge arrow shows (9.5b rule 4): from `share` of the TARGET inside the usable area and whether the arrow
## showed in the last frame. More than `switch_share` visible: no arrow; at or below it: the arrow; the switch moves by
## `hysteresis` so the arrow never flickers while the camera moves.
static func arrow_on(share: float, was_on: bool, switch_share: float, hysteresis: float) -> bool:
	if was_on:
		return share <= switch_share + hysteresis
	return share <= switch_share - hysteresis
