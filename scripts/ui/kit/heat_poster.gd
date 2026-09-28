class_name HeatPoster
extends Control
## Ransom-note Heat (STYLE_GUIDE 4): cut-out letters in mixed fonts on paper strips and
## the value in Anton. As a wanted poster in HQ (`poster = true`) it gains a border and a
## "WANTED" header. Heat bands follow the thresholds 25/50/75 (GDD 9.4).

## The most ransom-note strips the Heat word takes (a longer translation is cut).
const RANSOM_LETTERS_MAX := 6
## Colour of the number at high Heat: the campaign's corporation (set by the HQ).
var hot_color: Color = Palette.CORP_SOLACE
var heat: int = 0
var heat_max: int = 100
var poster: bool = false
var band: int = 0
## Threshold marks on the bar (the config's MAJOR Heat levels, passed by the scenes).
var marks: Array[int] = [25, 50, 75]
## Who the wanted poster shows (a PortraitArt subject; the HQ names the crew's lead).
var wanted: Dictionary = PortraitArt.operative_subject(&"operative")
## The mugshot's side on the wanted poster (px).
const MUG_SIZE := 44.0


## The Heat block's top on a wanted poster (under the header and mugshot), the band
## word's baseline below that block's top, its lettering, and the paper kept under it (px).
const POSTER_BLOCK_TOP := 84.0
const BAND_BASELINE := 68.0
const BAND_FONT := 13
const BAND_PAD := 6.0
## ANIM-R1 M16: the ransom letters' layout for `count` letters on this poster's width:
## {"step", "strip" (a strip's width), "num_w" (the widest the number or "/max" is),
## "num_x" (where the number starts)}; the number's right end stays on the poster.
func letter_layout(count: int) -> Dictionary:
	var num_w := maxf(Palette.display().get_string_size("%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, NUMBER_FONT).x,
		Palette.mono().get_string_size("/%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x)
	var width := size.x if size.x > 0.0 else custom_minimum_size.x
	var room := width - 8.0 - 6.0 - num_w - 4.0
	var step := clampf(room / maxf(1.0, count), LETTER_STEP_MIN, LETTER_STEP)
	var num_x := minf(8.0 + step * count, width - 6.0 - num_w) + 6.0
	return {"step": step, "strip": step - (LETTER_STEP - LETTER_WIDTH), "num_w": num_w, "num_x": num_x}


## The Heat band words, by band.
const BAND_WORDS: Array[String] = ["cool", "noticed", "flagged", "hunted"] # TR

## ANIM-5 (4.12): the Heat each campaign's posters last showed (view memory, not game
## state), so a threshold crossed anywhere (a run, a lost raid) plays once where the Heat
## shows next. ANIM-R2 R8, in this order per threshold crossed going up: the number rolls
## up to the threshold, the "HEAT 25 - NOTICED" banner stamps, the poster distorts briefly
## (Fx.heat_pulse_at: local, `heat_pulse` <= 0.3 s; the full-screen corporate wireframe no
## longer creeps in: it lingered and read as a display fault), the letters shake; then the
## next threshold, one banner per band crossed; then the number rolls on to the Heat. A
## drop across a band (Heat bought off) re-stamps the band word only (no banner, no
## distortion). A steady value plays nothing.
static var _seen_heat: Dictionary = {}
## The ransom letters' shake offset (px) and the band word's stamp scale (1 = at rest).
var shake_offset: Vector2 = Vector2.ZERO
var stamp_scale: float = 1.0
## Crossings up still to play (they wait until the poster shows and no jack runs), and
## whether the band word still has to stamp.
var pending_pulses: int = 0
var _pending_stamp: bool = false
## ANIM-R2 R8: the thresholds crossed going up still to play, lowest first, and the one the
## banner names now.
var _crossings: Array[int] = []
var _banner_at: int = 0
var _banner_tween: Tween = null
## ANIM-R1 M6: the Heat number as shown (it rolls from the Heat last seen), its pop (1 = at
## rest; it grows and flashes white on a crossing) and the crossing's banner ("HEAT 30 -
## NOTICED", stamped over the poster, then gone): 0 hidden, 1 shown; its stamp scale.
var shown_heat: float = 0.0
var number_scale: float = 1.0
var banner_alpha: float = 0.0
var banner_scale: float = 1.0
var _roll_from: int = -1
## The number's lettering and the banner's (px), and the banner's tilt (degrees).
const NUMBER_FONT := 30
const BANNER_FONT := 18
const BANNER_PAD := 6.0
const BANNER_TILT := -7.0
## ANIM-R2 R8: the banner's lettering follows the text size and shrinks (to BANNER_FONT_MIN)
## until the tilted banner fits the poster less BANNER_MARGIN a side (at 18 px a French
## band word ran 8-9 px past it).
const BANNER_FONT_MIN := 8
const BANNER_MARGIN := 3.0
## The ink box round the band word while it stamps (px).
const STAMP_BOX_PAD := 3.0
## A ransom letter's strip and the step between strips at rest, and the closest the
## strips may close up (px; ANIM-R1 M16).
const LETTER_WIDTH := 24.0
const LETTER_STEP := 28.0
const LETTER_STEP_MIN := 14.0


func _init(p_poster: bool = false) -> void:
	poster = p_poster
	# H23 S6: the poster is tall enough for its band word ("cool" hung under the paper,
	# hidden by the Pirate Radio note).
	custom_minimum_size = Vector2(170, 96 if not p_poster else ceilf(band_label_rect().end.y + BAND_PAD))


## Where the band word ("cool", "hunted") is drawn (local px).
func band_label_rect() -> Rect2:
	var top := POSTER_BLOCK_TOP if poster else 0.0
	var f := Palette.marker()
	var word := BAND_WORDS[mini(band, 3)]
	var base := top + BAND_BASELINE
	return Rect2(8, base - f.get_ascent(BAND_FONT), f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT).x, f.get_height(BAND_FONT))
	# PASS: the scene's tooltip (what the thresholds do) shows on hover.
	mouse_filter = Control.MOUSE_FILTER_PASS


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(for_text, "Heat") if for_text != "" else null


func set_heat(value: int, maximum: int, thresholds: Array[int] = [] as Array[int]) -> void:
	heat = value
	heat_max = maximum
	if not thresholds.is_empty():
		marks = thresholds
	band = 0
	for t in thresholds:
		if heat >= t:
			band += 1
	# ANIM-5: what changed since this campaign's Heat last showed.
	var key := memory_key()
	var prev: int = _seen_heat.get(key, -1)
	_seen_heat[key] = value
	shown_heat = value
	if prev >= 0 and prev != value:
		pending_pulses += crossings(prev, value, marks)
		for t in marks:
			if prev < t and value >= t:
				_crossings.append(t)
		if band_of(prev, thresholds) != band:
			_pending_stamp = true
		_roll_from = prev
		_play_pending()
	queue_redraw()


## Thresholds in `at` crossed going up from Heat `from` to `to` (0 going down).
static func crossings(from: int, to: int, at: Array[int]) -> int:
	var n := 0
	for t in at:
		if from < t and to >= t:
			n += 1
	return n


## The band Heat `value` falls in for thresholds `at`.
static func band_of(value: int, at: Array[int]) -> int:
	var b := 0
	for t in at:
		if value >= t:
			b += 1
	return b


## The Heat memory's key: the current campaign ("-" when none).
static func memory_key() -> String:
	var c := RunManager.campaign
	return "%s|%d" % [c.corporation_id, c.campaign_seed] if c != null else "-"


## Plays what waits once the poster shows (not under a jack cover): one Heat pulse per
## crossing (Fx.heat_pulse, a pulse's length apart), the letters' shake, the band stamp.
func _play_pending() -> void:
	if pending_pulses <= 0 and not _pending_stamp:
		set_process(false)
		return
	if not is_inside_tree() or not is_visible_in_tree() or Fx.transitioning():
		set_process(true)
		return
	set_process(false)
	var ups: Array[int] = []
	ups.assign(_crossings)
	_crossings.clear()
	pending_pulses = 0
	var from := _roll_from if _roll_from >= 0 else heat
	_roll_from = -1
	if not Motion.live(&"number_roll") or ups.is_empty():
		# No roll plays (headless, reduce effects), or a drop / a rise inside a band: the
		# number at once (a rise still rolls), then the crossings a pulse apart.
		if ups.is_empty() and Motion.live(&"number_roll"):
			shown_heat = from
			Motion.run(&"number_roll", self, ^"shown_heat", float(heat))
		else:
			shown_heat = heat
		_cross_chain(ups)
		if _pending_stamp:
			_stamp_band()
		return
	_play_rise(from, ups)


## ANIM-R2 R8: the rise, threshold by threshold: the number rolls to each and its crossing
## plays there (banner, local distortion, letters), then it rolls on to the Heat.
func _play_rise(from: int, ups: Array[int]) -> void:
	shown_heat = from
	for t in ups:
		var tw := Motion.run(&"number_roll", self, ^"shown_heat", float(t))
		if tw != null:
			await tw.finished
		if not is_inside_tree():
			return
		_cross(t, t == ups[ups.size() - 1])
	Motion.run(&"number_roll", self, ^"shown_heat", float(heat))


## Crossings `ups` (thresholds) played a pulse apart, the first now (no roll plays).
func _cross_chain(ups: Array[int]) -> void:
	if ups.is_empty():
		return
	_cross(ups[0], ups.size() == 1)
	if ups.size() > 1 and is_inside_tree():
		var rest: Array[int] = []
		rest.assign(ups.slice(1))
		get_tree().create_timer(Motion.seconds(&"heat_pulse")).timeout.connect(_cross_chain.bind(rest))


## ANIM-R2 R8: threshold `t` crossed going up: its banner stamps, the poster distorts
## briefly round itself, the number pops, the letters shake; the band word stamps with the
## last one.
func _cross(t: int, last: bool) -> void:
	_banner_at = t
	_stamp_banner()
	number_scale = Motion.amplitude(&"heat_number_pop")
	if Motion.run(&"heat_number_pop", self, ^"number_scale", 1.0) == null:
		number_scale = 1.0
	Motion.shake(self, &"heat_letters_shake", ^"shake_offset")
	Fx.heat_pulse_at(get_global_rect() if is_inside_tree() else Rect2())
	if last and _pending_stamp:
		_stamp_band()


func _stamp_band() -> void:
	_pending_stamp = false
	stamp_scale = Motion.amplitude(&"poster_stamp")
	if Motion.run(&"poster_stamp", self, ^"stamp_scale", 1.0) == null:
		stamp_scale = 1.0


## The crossing's banner: stamps on (`poster_stamp`'s timing from `heat_banner`'s scale),
## holds (`heat_banner`'s delay) and fades out (its duration); nothing when it is off.
func _stamp_banner() -> void:
	if not Motion.live(&"heat_banner"):
		banner_alpha = 0.0
		return
	var e := Motion.entry(&"heat_banner")
	banner_alpha = 1.0
	banner_scale = Motion.amplitude(&"heat_banner")
	Motion.run(&"poster_stamp", self, ^"banner_scale", 1.0)
	# ANIM-R2 R8: the next crossing's banner replaces this one (its fade must not dim it).
	if _banner_tween != null and _banner_tween.is_valid():
		_banner_tween.kill()
	var tw := create_tween()
	_banner_tween = tw
	tw.tween_property(self, "banner_alpha", 0.0, Motion.seconds(&"heat_banner")).set_delay(Motion.delay_of(&"heat_banner")).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_method(func(_v: float) -> void: queue_redraw(), 0.0, 1.0, Motion.seconds(&"heat_banner") + Motion.delay_of(&"heat_banner"))


## The banner's words for the threshold crossed ("HEAT 25 - NOTICED").
func banner_text() -> String:
	var at := _banner_at if _banner_at > 0 else heat
	return tr("HEAT %d - %s") % [at, tr(BAND_WORDS[mini(band_of(at, marks), 3)]).to_upper()]


## ANIM-R2 R8: the banner's lettering (px): BANNER_FONT at the text size, shrunk until the
## tilted banner fits the poster.
func banner_font_size() -> int:
	var f := Palette.display()
	var text := banner_text()
	var room := (size.x if size.x > 0.0 else custom_minimum_size.x) - BANNER_MARGIN * 2.0
	var fs := maxi(BANNER_FONT_MIN, roundi(BANNER_FONT * Settings.text_scale))
	while fs > BANNER_FONT_MIN and banner_span(f, text, fs) > room:
		fs -= 1
	return fs


## The width the tilted banner at `fs` spans on the poster (px).
static func banner_span(f: Font, text: String, fs: int) -> float:
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + BANNER_PAD * 2.0
	var h := fs * 1.5
	var a := deg_to_rad(absf(BANNER_TILT))
	return w * cos(a) + h * sin(a)


func _process(_delta: float) -> void:
	_play_pending()


func _draw() -> void:
	var y := 0.0
	if poster:
		draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER_ALT)
		draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 3.0)
		draw_string(Palette.display(), Vector2(10, 30), tr("WANTED"), HORIZONTAL_ALIGNMENT_LEFT, size.x - 20, 26, Palette.INK)
		PortraitArt.draw(self, Rect2(size.x * 0.5 - MUG_SIZE * 0.5, 38, MUG_SIZE, MUG_SIZE), wanted)
		y = POSTER_BLOCK_TOP
	# The ransom-note word, cut into letters (translated; H24).
	var word := tr("HEAT")
	var letters: Array[String] = []
	for ch in word.left(RANSOM_LETTERS_MAX):
		letters.append(ch)
	var fonts := [Palette.display(), Palette.marker(), Palette.mono(), Palette.display()]
	# ANIM-R1 M16: the letters and the number fit the poster's width (a longer translated or
	# pseudolocalised word ran the number and "/100" off its right edge): the strips close up
	# to fit beside the widest the number and its maximum can be.
	var lay := letter_layout(letters.size())
	var step: float = lay["step"]
	var strip_w: float = lay["strip"]
	var num_w: float = lay["num_w"]
	var x := 8.0
	for i in letters.size():
		var strip := Rect2(Vector2(x, y + 4 + (i % 2) * 4) + shake_offset * (1.0 if i % 2 == 0 else -1.0), Vector2(strip_w, 28))
		draw_rect(strip, Palette.PAPER if i % 2 == 0 else Palette.CELL_PINK)
		draw_rect(strip, Palette.INK, false, 1.0)
		var lf: Font = fonts[i % fonts.size()]
		var lfs := 18
		while lfs > 8 and lf.get_string_size(letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x > strip_w - 4.0:
			lfs -= 1
		draw_string(lf, strip.position + Vector2(maxf(2.0, (strip_w - lf.get_string_size(letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, lfs).x) * 0.5), 22), letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, lfs, Palette.INK)
		x += step
	x = minf(x, size.x - 6.0 - num_w)
	# ANIM-R1 M6: the number rolls, grows and flashes white on a crossing.
	var num_col := Palette.CELL_PINK if band < 2 else hot_color
	if number_scale > 1.0:
		num_col = num_col.lerp(Palette.PAPER, clampf((number_scale - 1.0) / maxf(0.001, Motion.amplitude(&"heat_number_pop") - 1.0), 0.0, 1.0))
	var num_at := Vector2(x + 6, y + 30)
	draw_set_transform(num_at + Vector2(0, -NUMBER_FONT * 0.35), 0.0, Vector2.ONE * number_scale)
	draw_string(Palette.display(), Vector2(0, NUMBER_FONT * 0.35), "%d" % roundi(shown_heat), HORIZONTAL_ALIGNMENT_LEFT, -1, NUMBER_FONT, num_col)
	draw_set_transform(Vector2.ZERO)
	draw_string(Palette.mono(), Vector2(x + 6, y + 44), "/%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.INK if poster else Palette.PAPER)
	var bar := Rect2(8, y + 44, size.x - 16, 8)
	draw_rect(bar, Color(Palette.INK, 0.3) if poster else Color(Palette.PAPER, 0.15))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0), bar.size.y)), Palette.CELL_PINK)
	for t in marks:
		var tx: float = bar.position.x + bar.size.x * int(t) / float(heat_max)
		draw_line(Vector2(tx, bar.position.y - 3), Vector2(tx, bar.end.y + 3), Palette.INK if poster else Palette.PAPER, 1.0)
	var word_col := Palette.INK if poster else Palette.CELL_ACID
	if stamp_scale > 1.0:
		# ANIM-5: the new band stamps on (scaled down onto the paper, an ink box round it).
		var r := band_label_rect()
		var c := r.get_center()
		draw_set_transform(c, 0.0, Vector2.ONE * stamp_scale)
		var box := Rect2(r.position - c, r.size).grow(STAMP_BOX_PAD)
		draw_rect(box, Color(hot_color, clampf((stamp_scale - 1.0) * 4.0, 0.0, 1.0)), false, 2.0)
		draw_string(Palette.marker(), Vector2(8, y + BAND_BASELINE) - c, tr(BAND_WORDS[mini(band, 3)]), HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT, word_col)
		draw_set_transform(Vector2.ZERO)
	else:
		draw_string(Palette.marker(), Vector2(8, y + BAND_BASELINE), tr(BAND_WORDS[mini(band, 3)]), HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT, word_col)
	if banner_alpha > 0.0:
		_draw_banner(y)


## ANIM-R1 M6: the crossing's banner across the poster's Heat block ("HEAT 30 - NOTICED"),
## in the corporation's colour, tilted like a stamp.
func _draw_banner(y: float) -> void:
	var f := Palette.display()
	var text := banner_text()
	var fs := banner_font_size()
	var tw := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Rect2(Vector2(-tw * 0.5 - BANNER_PAD, -fs * 0.8), Vector2(tw + BANNER_PAD * 2.0, fs * 1.5))
	draw_set_transform(Vector2(size.x * 0.5, y + 34), deg_to_rad(BANNER_TILT), Vector2.ONE * banner_scale)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.92 * banner_alpha))
	draw_rect(box, Color(hot_color, banner_alpha), false, 3.0)
	draw_string(f, Vector2(-tw * 0.5, fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(hot_color.lerp(Palette.PAPER, 0.3), banner_alpha))
	draw_set_transform(Vector2.ZERO)
