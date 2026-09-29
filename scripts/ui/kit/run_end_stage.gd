class_name RunEndStage
extends Control
## Art pass W8c (ART_BIBLE §11 "Run failed (FLATLINED)", §8 T4, critique 51): the end of a
## netrun staged over the city, never a black void and never cut off. In order (T4,
## `run_end_flatline`, ≤ 2.5 s, skippable with any press):
## 1. the operative's Polaroid flatlines (W5 `PortraitArt.Expr.FLATLINED`);
## 2. the city behind grades to grey (a desaturating grade over the backdrop: the CITY
##    material has no grey context yet, see W7 request);
## 3. the verdict slams in centred at `hero` size (VerdictStamp);
## 4. the run in numbers on a taped receipt (W8a's RunReceipt) with what the end means for
##    the operative (Plex body), then Back to HQ (the one primary).
## The other verdicts use the same template: JACKED OUT (the Polaroid triumphant, the city
## in colour, GAIN ink) and HOME FELL (grey, HARM ink). Under reduce effects nothing moves:
## the end state shows at once and the page's own entrance (a cross-fade) brings it in.
## View only: the screen passes the words and numbers.

## The grey grade's shader (the backdrop drawn so far, desaturated and dimmed by `amount`).
const GRADE_CODE := """
shader_type canvas_item;
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float amount : hint_range(0.0, 1.0) = 0.0;
uniform float dim : hint_range(0.0, 1.0) = 0.0;
const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);
void fragment() {
	vec3 c = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;
	float l = dot(c, LUMA);
	COLOR = vec4(mix(c, vec3(l), amount) * (1.0 - dim * amount), 1.0);
}
"""
## The motion (T4) and the shares of it each beat starts at: the flatline, the grade, the
## stamp's slam, the receipt.
const MOTION := &"run_end_flatline"
const AT_FLATLINE := 0.2
const AT_GRADE := 0.25
const GRADE_SHARE := 0.3
const AT_STAMP := 0.55
const STAMP_SHARE := 0.12
const AT_RECEIPT := 0.72
const RECEIPT_SHARE := 0.2
## How grey and how dim the city ends (a flatline, the home server lost), and a clean exit.
const GREY_AMOUNT := 1.0
const GREY_DIM := 0.35
## The Polaroid's size at text scale 1.0 (px) and the gaps (§5.1).
const POLAROID := Vector2(132, 160)
const GAP := UiTheme.SP_M

var outcome: int = RunState.Outcome.DIED
var grade: ColorRect
var column: VBoxContainer
var polaroid: Polaroid
var stamp: VerdictStamp
var receipt: RunReceipt
var fate_label: Label
var back_button: Button
var _tween: Tween = null
var _grade_to: float = 0.0


## `verdict` (translated) in `color`; `died` / `lost` grade the city grey; `class_id` and
## `operative_id` picture the operative; `stats` = [[StatIcon, value], ...] for the receipt
## with `title` (translated) at its head; `fate` (translated) says what it means.
func _init(p_outcome: int = RunState.Outcome.DIED, verdict: String = "", color: Color = Palette.HARM,
		class_id: StringName = &"", operative_id: StringName = &"", op_name: String = "",
		title: String = "", stats: Array = [], fate: String = "") -> void:
	name = "RunEndStage"
	outcome = p_outcome
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	_grade_to = GREY_AMOUNT if outcome != RunState.Outcome.COMPLETED else 0.0
	grade = ColorRect.new()
	grade.name = "GreyGrade"
	grade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = GRADE_CODE
	var mat := ShaderMaterial.new()
	mat.shader = sh
	mat.set_shader_parameter(&"dim", GREY_DIM)
	grade.material = mat
	grade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(grade)
	var center := CenterContainer.new()
	center.name = "RunEndCenter"
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	column = VBoxContainer.new()
	column.name = "RunEndColumn"
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	column.add_theme_constant_override("separation", GAP)
	column.minimum_size_changed.connect(update_minimum_size)
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center.add_child(column)
	polaroid = Polaroid.new(op_name, "[PORTRAIT]", -3.0)
	polaroid.name = "RunEndPolaroid"
	polaroid.custom_minimum_size = POLAROID * minf(Settings.text_scale, POLAROID_GROW_MAX)
	polaroid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	polaroid.set_operative(class_id, operative_id)
	polaroid.set_expression(PortraitArt.Expr.TRIUMPHANT if outcome == RunState.Outcome.COMPLETED else PortraitArt.Expr.NEUTRAL)
	column.add_child(polaroid)
	stamp = VerdictStamp.new(verdict, color, STAMP_MAX_WIDTH)
	stamp.name = "ResultStamp"
	stamp.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	column.add_child(stamp)
	var foot := HBoxContainer.new()
	foot.name = "RunEndFoot"
	foot.alignment = BoxContainer.ALIGNMENT_CENTER
	foot.add_theme_constant_override("separation", GAP)
	column.add_child(foot)
	receipt = RunReceipt.new(RunReceipt.TILT_STEP)
	receipt.name = "RunReceipt"
	receipt.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	receipt.line(title.to_upper(), UiTheme.BODY, Palette.display())
	receipt.line("-")
	receipt.fields(stats)
	foot.add_child(receipt)
	var words := VBoxContainer.new()
	words.name = "RunEndWords"
	words.add_theme_constant_override("separation", GAP)
	words.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	foot.add_child(words)
	fate_label = Label.new()
	fate_label.name = "RunFate"
	fate_label.theme_type_variation = UiTheme.BODY_TEXT
	fate_label.text = fate
	UiWrap.whole_words(fate_label)  # art pass W9F §4.3.3: whole words, never mid-word
	fate_label.custom_minimum_size.x = words_width()
	words.add_child(fate_label)
	back_button = Button.new()
	back_button.name = "BackToHQ"
	back_button.theme_type_variation = UiTheme.PRIMARY
	back_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	words.add_child(back_button)


## Art pass W8c: the fate words' width (≤ 44 characters of the body face: beside the
## receipt, inside the screen at 2.0).
static func words_width() -> float:
	return ceilf(Palette.body().get_string_size(UiTip.COLUMN_SAMPLE.repeat(FATE_COLUMNS), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x)


## The fate line's columns, the stamp's widest (px; 140% slack is kept inside it) and the
## most the Polaroid grows with the text.
const FATE_COLUMNS := 44
const STAMP_MAX_WIDTH := 1100.0
const POLAROID_GROW_MAX := 1.3


## Plays the T4 sequence (or shows its end at once when the motion doesn't play).
func play() -> void:
	finish_now()
	if not Motion.live(MOTION):
		return
	var d := Motion.seconds(MOTION)
	var e := Motion.entry(MOTION)
	_set_grade(0.0)
	polaroid.set_expression(PortraitArt.Expr.NEUTRAL if outcome != RunState.Outcome.COMPLETED else PortraitArt.Expr.TRIUMPHANT)
	stamp.modulate.a = 0.0
	receipt.modulate.a = 0.0
	fate_label.modulate.a = 0.0
	back_button.modulate.a = 0.0
	_tween = create_tween()
	_tween.tween_interval(d * AT_FLATLINE)
	_tween.tween_callback(_flatline)
	_tween.tween_interval(maxf(0.0, d * (AT_GRADE - AT_FLATLINE)))
	_tween.tween_method(_set_grade, 0.0, _grade_to, d * GRADE_SHARE).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_interval(maxf(0.0, d * (AT_STAMP - AT_GRADE - GRADE_SHARE)))
	_tween.tween_callback(func() -> void:
		stamp.pivot_offset = stamp.size * 0.5
		stamp.scale = Vector2.ONE * Motion.amplitude(MOTION))
	_tween.tween_property(stamp, ^"modulate:a", 1.0, d * STAMP_SHARE * 0.5)
	_tween.parallel().tween_property(stamp, ^"scale", Vector2.ONE, d * STAMP_SHARE).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	_tween.tween_interval(maxf(0.0, d * (AT_RECEIPT - AT_STAMP - STAMP_SHARE)))
	_tween.tween_property(receipt, ^"modulate:a", 1.0, d * RECEIPT_SHARE)
	_tween.parallel().tween_property(fate_label, ^"modulate:a", 1.0, d * RECEIPT_SHARE)
	_tween.parallel().tween_property(back_button, ^"modulate:a", 1.0, d * RECEIPT_SHARE)
	_tween.tween_callback(finish_now)
	# PageTransition.settle / Typing.finish_all end a page's motions through this meta (the
	# stage holds its tween there, as a typing label does): the stage then shows its end.
	set_meta(Typing.META, _tween)


## True while the sequence plays.
func running() -> bool:
	return _tween != null and _tween.is_valid()


## Shows the end state now (a press, a settle, reduce effects).
func finish_now() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null
	if has_meta(Typing.META):
		remove_meta(Typing.META)
	_flatline()
	_set_grade(_grade_to)
	stamp.scale = Vector2.ONE
	for c: CanvasItem in [stamp, receipt, fate_label, back_button]:
		c.modulate.a = 1.0


func _flatline() -> void:
	if outcome != RunState.Outcome.COMPLETED:
		polaroid.set_expression(PortraitArt.Expr.FLATLINED)


func _set_grade(v: float) -> void:
	(grade.material as ShaderMaterial).set_shader_parameter(&"amount", v)
	grade.visible = v > 0.0


## The grade's amount now (0 colour, 1 grey; tests).
func grade_amount() -> float:
	return float((grade.material as ShaderMaterial).get_shader_parameter(&"amount"))


func _process(_delta: float) -> void:
	# A settle took the meta (PageTransition.settle, Typing.finish_all): end now.
	if _tween != null and not has_meta(Typing.META):
		finish_now()


func _input(event: InputEvent) -> void:
	# §8 T4: skippable: a press shows the end at once (and does nothing else).
	if not running():
		return
	var pressed := (event is InputEventKey and (event as InputEventKey).pressed and not (event as InputEventKey).echo) \
		or (event is InputEventMouseButton and (event as InputEventMouseButton).pressed) \
		or (event is InputEventJoypadButton and (event as InputEventJoypadButton).pressed)
	if pressed:
		finish_now()
		get_viewport().set_input_as_handled()


## The verdict's words for a run outcome (keys; the same words as ANIM-R5 B3's stamp).
static func verdict_of(p_outcome: int) -> String:
	match p_outcome:
		RunState.Outcome.COMPLETED:
			return "JACKED OUT" # TR
		RunState.Outcome.ABORTED:
			return "HOME FELL" # TR
	return "FLATLINED" # TR


## The verdict's ink (§3.3: harm for a loss, gain for a clean exit; never colour alone: the
## word and the grey city say it too).
static func color_of(p_outcome: int) -> Color:
	return Palette.GAIN if p_outcome == RunState.Outcome.COMPLETED else Palette.HARM


## At least as tall as its column (so a page taller than the screen scrolls, never centres
## its top off the screen).
func _get_minimum_size() -> Vector2:
	return column.get_combined_minimum_size() if column != null else Vector2.ZERO
