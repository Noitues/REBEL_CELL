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
## Pencil sizes (px at 1.0): the words, the stroke; the gap between marks (x a write).
const WORD_PX := 22
const STROKE := 3.5
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
	queue_redraw()


func _total() -> float:
	return (Motion.entry(WRITE).duration if Motion.entry(WRITE) != null else 0.4) * (1.0 + GAP_SHARE) * 5.0


## MotionSkip: marks still writing.
func motion_running() -> bool:
	return _t < _total()


## MotionSkip: every mark written.
func complete_motion() -> void:
	_t = INF
	queue_redraw()


## The report row value named `value_name` (local rect; empty when missing).
func _value_rect(value_name: String) -> Rect2:
	if report == null or not is_instance_valid(report):
		return Rect2()
	var l := report.find_child(value_name, true, false) as Control
	if l == null or not l.is_visible_in_tree():
		return Rect2()
	var r := l.get_global_rect()
	return Rect2(get_global_transform().affine_inverse() * r.position, r.size)


func _u(i: int) -> float:
	var w := Motion.entry(WRITE).duration if Motion.entry(WRITE) != null else 0.4
	return clampf((_t - i * w * (1.0 + GAP_SHARE)) / maxf(w, 0.001), 0.0, 1.0)


func _draw() -> void:
	var k := Settings.text_scale
	var px := roundi(WORD_PX * k)
	var w := STROKE * k
	var yellow := RaidSkin.pencil_plan()
	var red := RaidSkin.pencil_threat()
	var i := 0
	var destroyed := int(result.get("threats_destroyed", 0))
	var units := _value_rect("ReportUnits")
	if units.has_area() and destroyed > 0:
		var u := _u(i)
		RaidPencil.circle(self, units.get_center(), units.size.x * 0.62 + 6.0 * k, units.size.y * 0.75, yellow, w, 0.0, u, 11)
		_side_word(tr(THEY_LOST) % destroyed, units, px, yellow, u)
		i += 1
	var reward_r := _value_rect("ReportReward")
	if reward_r.has_area() and reward > 0:
		var u := _u(i)
		RaidPencil.circle(self, reward_r.get_center(), reward_r.size.x * 0.6 + 6.0 * k, reward_r.size.y * 0.75, yellow, w, 0.0, u, 23)
		_side_word(tr(OURS) % reward, reward_r, px, yellow, u)
		i += 1
	var rec := _value_rect("ReportReclaimed")
	if rec.has_area():
		RaidPencil.word(self, tr(RIP), rec.position + Vector2(-px * 1.4, rec.size.y * 0.5), px, red, _u(i), 0.0, -0.1, false, 0.0, 37)
		i += 1
	var home := _value_rect("ReportHome")
	if home.has_area() and int(result.get("home_after", 0)) >= int(result.get("home_before", 0)) and held:
		RaidPencil.tick(self, home.position + Vector2(-px * 0.9, home.size.y * 0.5), px * 0.9, yellow, w, _u(i), 41)


## A pencil note left of a circled value with an arrow toward it ("THEY LOST 6 ->").
func _side_word(text: String, at: Rect2, px: int, col: Color, u: float) -> void:
	if report == null:
		return
	var size := RaidPencil.word_size(text, px)
	var paper := Rect2(get_global_transform().affine_inverse() * report.get_global_rect().position, report.size)
	var c := Vector2(paper.position.x - size.x * 0.55 - px * 0.8, at.get_center().y)
	RaidPencil.word(self, text, c, px, col, u, 0.0, -0.05, false, 0.0, text.hash())
	var from := c + Vector2(size.x * 0.5 + px * 0.15, 0)
	var to := Vector2(at.position.x - px * 0.4, at.get_center().y)
	if to.x > from.x:
		RaidPencil.arrow(self, PackedVector2Array([from, (from + to) * 0.5 + Vector2(0, -px * 0.25), to]), col, STROKE * Settings.text_scale * 0.8, u, 5)
