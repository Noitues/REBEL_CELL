class_name RaidReportPencil
extends Control
## ART-6 3A: the Cell's grease pencil on the intercepted after-action report (ART_BIBLE v2
## §4.8 "Raid report", round 21 `raid_report`): what we gained and they lost circled in our
## yellow ("THEY LOST 6", "OURS! +12"), RIP in red by the Sites they reclaimed, a tick by our
## home server when it held. Each mark writes on after the last (`raid_mark_write`, real time;
## one press ends them; all at once when motion doesn't play). A full-screen layer over the
## page (no UI ever covers grease pencil); it reads where the report's rows are and takes no
## input. View only.

const THEY_LOST := "THEY LOST %d" # TR
const OURS := "OURS! +%d" # TR
const RIP := "RIP" # TR
const WRITE := &"raid_mark_write"
## Pencil: the words' type step, the gap to the paper (px); the gap between
## marks (x a write).
const WORD_STEP := UiTheme.TITLE
const NOTE_GAP := 18.0
const GAP_SHARE := 0.6

var report: Control
var result: Dictionary = {}
var held: bool = true
var reward: int = -1
var _t: float = 0.0


func _init(p_report: Control = null, p_result: Dictionary = {}, p_held: bool = true, p_reward: int = -1) -> void:
	report = p_report
	result = p_result
	held = p_held
	reward = p_reward
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MotionSkip.register_passive(self)
	if not Motion.live(WRITE):
		_t = INF


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	if _t < _total():
		_t += delta
	_lay()


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


func _total() -> float:
	return (Motion.entry(WRITE).duration if Motion.entry(WRITE) != null else 0.4) * (1.0 + GAP_SHARE) * 5.0


## MotionSkip: marks still writing.
func motion_running() -> bool:
	return _t < _total()


## MotionSkip: every mark written.
func complete_motion() -> void:
	_t = INF


## The report row value named `value_name` (global rect; empty when missing).
func _value_rect(value_name: String) -> Rect2:
	if report == null or not is_instance_valid(report):
		return Rect2()
	var l := report.find_child(value_name, true, false) as Control
	if l == null or not l.is_visible_in_tree():
		return Rect2()
	return l.get_global_rect()


func _u(i: int) -> float:
	var w := Motion.entry(WRITE).duration if Motion.entry(WRITE) != null else 0.4
	return clampf((_t - i * w * (1.0 + GAP_SHARE)) / maxf(w, 0.001), 0.0, 1.0)


## Lays the Cell's marks on 1B's grease pencil (RaidPencilPool, above the paper and every panel).
func _lay() -> void:
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var plan := GreasePencilMark.Ink.PLAN
	var threat := GreasePencilMark.Ink.THREAT
	var i := 0
	var destroyed := int(result.get("threats_destroyed", 0))
	var units := _value_rect("ReportUnits")
	if units.has_area() and destroyed > 0:
		var u := _u(i)
		_pool.stroke("units", [PencilShapes.hand_circle(units.get_center(), Vector2(units.size.x * 0.62 + 6.0, units.size.y * 0.8), 11)], plan, u, 0.0, false, 11)
		_side_word("lost", tr(THEY_LOST) % destroyed, units, plan, u)
		i += 1
	var reward_r := _value_rect("ReportReward")
	if reward_r.has_area() and reward > 0:
		var u := _u(i)
		_pool.stroke("reward", [PencilShapes.hand_circle(reward_r.get_center(), Vector2(reward_r.size.x * 0.6 + 6.0, reward_r.size.y * 0.8), 23)], plan, u, 0.0, false, 23)
		_side_word("ours", tr(OURS) % reward, reward_r, plan, u)
		i += 1
	var rec := _value_rect("ReportReclaimed")
	if rec.has_area():
		var w := RaidPencilPool.word_size(tr(RIP), WORD_STEP)
		_pool.word("rip", tr(RIP), rec.position + Vector2(-w.x * 0.7, rec.size.y * 0.5), WORD_STEP, threat, 1.0, _u(i), 0.0, -0.1)
		i += 1
	var home := _value_rect("ReportHome")
	if home.has_area() and int(result.get("home_after", 0)) >= int(result.get("home_before", 0)) and held:
		var s := home.size.y * 0.9
		var tc := home.position + Vector2(-s, home.size.y * 0.5)
		_pool.stroke("tick", [PackedVector2Array([tc + Vector2(-s * 0.5, 0), tc + Vector2(-s * 0.1, s * 0.4), tc + Vector2(s * 0.6, -s * 0.55)])], plan, _u(i), 0.0, false, 41)
	_pool.end()


## A pencil note left of the report with an arrow to the circled value ("THEY LOST 6 ->").
func _side_word(key: String, text: String, at: Rect2, ink: GreasePencilMark.Ink, u: float) -> void:
	var size := RaidPencilPool.word_size(text, WORD_STEP)
	var paper := report.get_global_rect()
	var c := Vector2(paper.position.x - size.x * 0.55 - NOTE_GAP, at.get_center().y)
	_pool.word(key, text, c, WORD_STEP, ink, 1.0, u, 0.0, -0.05)
	var from := c + Vector2(size.x * 0.5 + NOTE_GAP * 0.2, 0)
	var to := Vector2(at.position.x - NOTE_GAP * 0.5, at.get_center().y)
	if to.x > from.x:
		var shaft := PencilShapes.bezier(from, (from + to) * 0.5 + Vector2(0, -NOTE_GAP * 0.4), to, 16)
		_pool.stroke(key + "_arrow", PencilShapes.arrow(shaft, GreasePencilMark.stroke_width() * 2.5, 5), ink, u, 0.0, false, 5)


var _pool: RaidPencilPool = null
