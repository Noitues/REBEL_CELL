class_name HqLadderWords
extends RefCounted
## Plan 2 W2 HQ-LADDER-UI: the words and marks the Solace HQ ladder (run kind "hq", SolaceHqGraph) shows in
## the netrun scene: a room's name (Clinic Gate, Rest, Mini-boss, Genome Core), its tower (WARD / BILLING),
## how it is entered (UP or ACROSS, in the hover tag and room file only), the exact Bloom gap entering it leaves (NetrunSession.bloom_preview,
## no "?"), and which links of the graph are ACROSS bridges. Read-only: every value comes from the session's
## rules, nothing is decided here.

const GATE_WORD := "Clinic Gate" # TR
const REST_WORD := "Rest" # TR
const MINI_BOSS_WORD := "Mini-boss" # TR
const CROWN_WORD := "Genome Core" # TR
const BOSS_FORMAT := "BOSS: %s" # TR
const MINI_BOSS_FORMAT := "MINI-BOSS: %s" # TR
const MOVE_UP := "UP" # TR
const MOVE_ACROSS := "ACROSS" # TR
const TOWER_WARD := "WARD" # TR
const TOWER_BILLING := "BILLING" # TR
const GAP_WORDS := "GAP %s" # TR
const CAUGHT_WORDS := "GAP %s CAUGHT" # TR
## The Bloom field of a room's file: the gap after entering, and what each fight turn there costs.
const PANEL_TOWER := "TOWER" # TR
const PANEL_MOVE := "MOVE" # TR
const PANEL_GAP := "BLOOM GAP" # TR
const PANEL_GAP_VALUE := "%s layers after entering" # TR
const PANEL_GAP_CAUGHT := "%s layers: the Bloom has you" # TR
const PANEL_TURN_COST := "Each fight turn there: -%s of gap per turn, Heat and Exploit cuts applied" # TR
const MOVE_ACROSS_TIP := "Bridge: the other tower's next rung; the front gains extra pace." # TR
const MOVE_ACROSS_FREE_TIP := "Bridge: the other tower's next rung; free with the Breach key." # TR
const MOVE_UP_TIP := "Same tower, next rung." # TR
## The link key the overlay and `across_keys` share: "<from>><to>".
const KEY_FORMAT := "%s>%s"
## The kind names the street overlay stickers use for the ladder's own rooms (D4 / elite shapes).
const KIND_REST := "rest"
const KIND_MINI_BOSS := "elite"


## True for the Solace HQ ladder's session.
static func is_ladder(s: NetrunSession) -> bool:
	return s != null and s.run != null and s.run.kind == NetrunSession.HQ_LADDER_KIND


## The ladder room kind of `node`: &"gate" (the first node), &"crown", &"mini_boss", &"rest" or &"" (a plain room).
static func room_kind(node: Dictionary) -> StringName:
	if bool(node.get("boss", false)):
		return &"crown"
	if bool(node.get("mini_boss", false)):
		return &"mini_boss"
	if bool(node.get("rest", false)):
		return &"rest"
	if int(node.get("layer", 0)) == 1:
		return &"gate"
	return &""


## The room's name when the ladder gives it its own ("" for a plain fight / shop / event / elite: the scene's word).
static func special_word(node: Dictionary) -> String:
	match room_kind(node):
		&"gate":
			return TranslationServer.translate(GATE_WORD)
		&"rest":
			return TranslationServer.translate(REST_WORD)
		&"mini_boss":
			return TranslationServer.translate(MINI_BOSS_WORD)
		&"crown":
			return TranslationServer.translate(CROWN_WORD)
	return ""


## The tower's name in caps ("" for the gate and the crown, which stand on neither).
static func tower_word(node: Dictionary) -> String:
	match String(node.get("tower", "")):
		SolaceHqGraph.TOWER_WARD:
			return TranslationServer.translate(TOWER_WARD) if room_kind(node) != &"crown" else ""
		SolaceHqGraph.TOWER_BILLING:
			return TranslationServer.translate(TOWER_BILLING)
	return ""


## How entering `node` from `from_id` is worded: ACROSS, UP, or "" (no room to enter from).
static func move_word(map: MapGraph, node: Dictionary, from_id: StringName) -> String:
	if NetrunSession.entered_across(node, from_id):
		return TranslationServer.translate(MOVE_ACROSS)
	if from_id == &"":
		return ""
	return TranslationServer.translate(MOVE_UP)


## "1.2" style gap text and whether the preview says entering is caught: {"text", "caught", "turn"} for node `id`
## from the session's `bloom_preview()`, or {} when the preview holds nothing for it.
static func gap_of(preview: Dictionary, id: StringName) -> Dictionary:
	if not preview.has(id):
		return {}
	var p: Dictionary = preview[id]
	return {"text": NetrunSession.bloom_gap_text(int(p["gap_milli"])), "caught": bool(p["caught"]), "across_milli": int(p.get("across_milli", 0)),
		"turn": NetrunSession.bloom_gap_text(int(p["turn_cost_milli"])) if int(p["turn_cost_milli"]) > 0 else ""}


## The hover tag of room `id`: "WARD · Rest · ACROSS · GAP 1.2", the crown "Genome Core · UP" (parts that do not apply are left out).
static func tag(s: NetrunSession, id: StringName, base_word: String) -> String:
	var node := s.run.map.get_node(id)
	var parts := PackedStringArray()
	var tw := tower_word(node)
	if tw != "":
		parts.append(tw)
	parts.append(base_word)
	var mv := move_word(s.run.map, node, s.run.current_node_id)
	if mv != "" and s.available_nodes().has(id):
		parts.append(mv)
	var gap := gap_of(s.bloom_preview(), id)
	if not gap.is_empty():
		parts.append(TranslationServer.translate(CAUGHT_WORDS if bool(gap["caught"]) else GAP_WORDS) % String(gap["text"]))
	return " · ".join(parts)


## The extra rows of room `id`'s file: [[label, value], ...] for TOWER, MOVE and BLOOM GAP.
static func panel_rows(s: NetrunSession, id: StringName) -> Array:
	var node := s.run.map.get_node(id)
	var rows: Array = []
	var tw := tower_word(node)
	if tw != "":
		rows.append([TranslationServer.translate(PANEL_TOWER), tw])
	var mv := move_word(s.run.map, node, s.run.current_node_id)
	if mv != "" and s.available_nodes().has(id):
		var tip := MOVE_UP_TIP
		if NetrunSession.entered_across(node, s.run.current_node_id):
			tip = MOVE_ACROSS_TIP if int(gap_of(s.bloom_preview(), id).get("across_milli", 1)) > 0 else MOVE_ACROSS_FREE_TIP
		rows.append([TranslationServer.translate(PANEL_MOVE), "%s: %s" % [mv, TranslationServer.translate(tip)]])
	var gap := gap_of(s.bloom_preview(), id)
	if not gap.is_empty():
		var key := PANEL_GAP_CAUGHT if bool(gap["caught"]) else PANEL_GAP_VALUE
		rows.append([TranslationServer.translate(PANEL_GAP), TranslationServer.translate(key) % String(gap["text"])])
		if String(gap["turn"]) != "":
			rows.append(["", TranslationServer.translate(PANEL_TURN_COST) % String(gap["turn"])])
	return rows


## The keys ("<from>><to>") of every ACROSS link of `map`, for the overlay to draw as bridges.
static func across_keys(map: MapGraph) -> Dictionary:
	var out := {}
	for n in map.all_nodes():
		for from_id in n.get("across_from", []):
			out[KEY_FORMAT % [from_id, n["id"]]] = true
	return out


## id -> the overlay kind of the rooms the ladder gives their own sticker (rest, mini-boss).
static func kind_overrides(map: MapGraph) -> Dictionary:
	var out := {}
	for n in map.all_nodes():
		match room_kind(n):
			&"rest":
				out[String(n["id"])] = KIND_REST
			&"mini_boss":
				out[String(n["id"])] = KIND_MINI_BOSS
	return out


## The format the combat address line gives the enemy of this fight: "BOSS: %s" for the crown, "MINI-BOSS: %s" for a
## mini-boss room, "" otherwise (and for other run kinds).
static func fight_label(run: RunState) -> String:
	if run == null or run.kind != NetrunSession.HQ_LADDER_KIND or run.map == null:
		return ""
	match room_kind(run.current_node()):
		&"crown":
			return TranslationServer.translate(BOSS_FORMAT)
		&"mini_boss":
			return TranslationServer.translate(MINI_BOSS_FORMAT)
	return ""
