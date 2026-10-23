class_name L7Fx
extends RefCounted
## The raid's animation cues, read off the resolver's events in the order they happen (STYLE_GUIDE 5.3: raids play from the
## resolver's events and are never recomputed). `consume(play)` is called after every advance of the playout (animated: a
## frame at a time; instant: once, after the whole skip) and appends the cues of everything new: a beam launching, each cell
## it touches (a flash), a decoy pulling it aside, the unseal beats, the spoof window and the pick, the hunter's turn, the
## impacts (DOWN: the wrench drops in; TAKEN: the ground flips; HOME: the drain), the stamp. The view draws from the events
## and these timestamps; the cue list is what flow_check compares against the resolver's touch order and against the
## instant run.

var cues: Array = []
var _n_events: int = 0
var _state: int = -1
var _beam: String = ""
var _spoof_seen: bool = false
var _stamped: bool = false
## play.clock when the unseal began, the spoof window opened, the pick was made, the sweep's end began (-1 = not yet).
var unseal_at: float = -1.0
var decide_at: float = -1.0
var pick_at: float = -1.0
var pick_cell: Vector2i = L5Rules.NONE
var end_at: float = -1.0


func reset() -> void:
	cues = []
	_n_events = 0
	_state = -1
	_beam = ""
	_spoof_seen = false
	_stamped = false
	unseal_at = -1.0
	decide_at = -1.0
	pick_at = -1.0
	pick_cell = L5Rules.NONE
	end_at = -1.0


func _cue(kind: String, p: L5Play, extra: Dictionary = {}) -> void:
	var c := {"kind": kind, "at": p.clock}
	c.merge(extra)
	cues.append(c)


## Read what the playout has done since the last call, in order.
func consume(p: L5Play) -> void:
	# The events first (they carry their own time), so a touch is always cued before the state change that follows it.
	while _n_events < p.events.size():
		var e: Dictionary = p.events[_n_events]
		_n_events += 1
		var step: String = e["kind"]
		cues.append({"kind": "touch", "at": e["at"], "beam": e["beam"], "cell": e["cell"], "step": step, "outcome": e["outcome"]})
		match String(e["outcome"]):
			"DECOY":
				cues.append({"kind": "decoy_pull", "at": e["at"], "beam": e["beam"], "cell": e["cell"]})
			"DOWN":
				cues.append({"kind": "impact_down", "at": e["at"], "beam": e["beam"], "cell": e["cell"]})
			"TAKEN":
				cues.append({"kind": "impact_taken", "at": e["at"], "beam": e["beam"], "cell": e["cell"]})
			"HOME":
				cues.append({"kind": "impact_home", "at": e["at"], "beam": e["beam"], "cell": e["cell"]})
		if step == "spoofed":
			cues.append({"kind": "bypass", "at": e["at"], "beam": e["beam"], "cell": e["cell"]})
	if p.spoof_used and not _spoof_seen:
		_spoof_seen = true
		pick_at = p.clock
		pick_cell = p.spoof
		_cue("pick_jam" if p.spoof == L5Rules.JAM else "pick_skip", p, {"cell": p.spoof})
	var id := p.beam_id()
	if p.state != _state or id != _beam:
		match p.state:
			L5Play.S.BEAM:
				_cue("launch", p, {"beam": id})
			L5Play.S.UNSEAL:
				unseal_at = p.clock
				_cue("unseal", p)
			L5Play.S.DECIDE:
				decide_at = p.clock
				_cue("spoof_window", p)
			L5Play.S.NOTE:
				_cue("no_spoof", p)
			L5Play.S.TURN:
				_cue("hunter_turn", p)
			L5Play.S.END:
				end_at = p.clock
		_state = p.state
		_beam = id
	if p.state in [L5Play.S.END, L5Play.S.DONE] and not _stamped:
		_stamped = true
		if end_at < 0.0:
			end_at = p.clock
		_cue("stamp", p)


## The touches in the order they were cued: [[x, y, kind]], the same shape as the resolver's touch list.
func touch_order() -> Array:
	var out: Array = []
	for c: Dictionary in cues:
		if c["kind"] == "touch" and String(c["outcome"]) != "":
			out.append([(c["cell"] as Vector2i).x, (c["cell"] as Vector2i).y, c["step"]])
	return out


## The kinds of the cues, in order (for the animated-versus-instant comparison).
func kinds() -> Array:
	var out: Array = []
	for c: Dictionary in cues:
		out.append(c["kind"])
	return out


## The cue's identity without its time (kind, beam, cell, outcome), in order: equal in an animated and an instant run.
func signature() -> Array:
	var out: Array = []
	for c: Dictionary in cues:
		out.append("%s|%s|%s|%s" % [c["kind"], c.get("beam", ""), str(c.get("cell", "")), c.get("outcome", "")])
	return out
