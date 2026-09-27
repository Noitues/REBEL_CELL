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
## The Heat band words, by band.
const BAND_WORDS: Array[String] = ["cool", "noticed", "flagged", "hunted"] # TR

## ANIM-5 (4.12): the Heat each campaign's posters last showed (view memory, not game
## state), so a threshold crossed anywhere (a run, a lost raid) plays once where the Heat
## shows next: Fx.heat_pulse per crossing up (with the corporate wireframe creeping in),
## the ransom letters shake once, and the band word stamps on. A crossing down (Heat
## bought off) only stamps the new band. A steady value plays nothing.
static var _seen_heat: Dictionary = {}
## The ransom letters' shake offset (px) and the band word's stamp scale (1 = at rest).
var shake_offset: Vector2 = Vector2.ZERO
var stamp_scale: float = 1.0
## Crossings up still to play (they wait until the poster shows and no jack runs), and
## whether the band word still has to stamp.
var pending_pulses: int = 0
var _pending_stamp: bool = false
## The ink box round the band word while it stamps (px).
const STAMP_BOX_PAD := 3.0


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
	if prev >= 0 and prev != value:
		pending_pulses += crossings(prev, value, marks)
		if band_of(prev, thresholds) != band:
			_pending_stamp = true
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
	if pending_pulses > 0:
		_pulse_chain(pending_pulses)
		pending_pulses = 0
		Motion.shake(self, &"heat_letters_shake", ^"shake_offset")
	if _pending_stamp:
		_pending_stamp = false
		stamp_scale = Motion.amplitude(&"poster_stamp")
		Motion.run(&"poster_stamp", self, ^"stamp_scale", 1.0)


func _pulse_chain(left: int) -> void:
	if left <= 0:
		return
	Fx.heat_pulse(-1.0, hot_color)
	if left > 1 and is_inside_tree():
		get_tree().create_timer(Motion.seconds(&"heat_pulse")).timeout.connect(_pulse_chain.bind(left - 1))


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
	var x := 8.0
	for i in letters.size():
		var strip := Rect2(Vector2(x, y + 4 + (i % 2) * 4) + shake_offset * (1.0 if i % 2 == 0 else -1.0), Vector2(24, 28))
		draw_rect(strip, Palette.PAPER if i % 2 == 0 else Palette.CELL_PINK)
		draw_rect(strip, Palette.INK, false, 1.0)
		draw_string(fonts[i % fonts.size()], strip.position + Vector2(5, 22), letters[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.INK)
		x += 28
	draw_string(Palette.display(), Vector2(x + 6, y + 30), "%d" % heat, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.CELL_PINK if band < 2 else hot_color)
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
