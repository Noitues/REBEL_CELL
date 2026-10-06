class_name HeatPoster
extends Control
## Ransom-note Heat (STYLE_GUIDE 4): cut-out letters in mixed fonts on paper strips and
## the value in Anton. As a wanted poster in HQ (`poster = true`) it gains a border and a
## "WANTED" header. Heat bands follow the MAJOR and PURGE thresholds (GDD 4.3, 9.4): COOL,
## NOTICED, FLAGGED, HUNTED, PURGE.

## The most ransom-note strips the Heat word takes (a longer translation is cut).
const RANSOM_LETTERS_MAX := 6
## Colour of the number at high Heat: the campaign's corporation (set by the HQ).
var hot_color: Color = Palette.CORP_SOLACE
var heat: int = 0
var heat_max: int = 100
var poster: bool = false
var band: int = 0
## Threshold marks on the bar and the band starts (HeatRules.band_levels: the MAJOR levels and
## the PURGE level, passed by the scenes).
var marks: Array[int] = [25, 50, 75, 100]
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
const BAND_WORDS: Array[String] = ["cool", "noticed", "flagged", "hunted", "purge"] # TR

## ANIM-5 (4.12): the Heat each campaign's posters last showed (view memory, not game
## state), so a threshold crossed anywhere (a run, a lost raid) plays once where the Heat
## shows next. ANIM-R2 R8, in this order per threshold crossed going up: the number rolls
## up to the threshold, the "HEAT 30 · NOTICED (25+)" banner stamps, the poster distorts briefly
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
## rest; it grows and flashes white on a crossing) and the crossing's banner ("HEAT 30 ·
## NOTICED (25+)", stamped over the poster, then gone): 0 hidden, 1 shown; its stamp scale.
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
## ANIM-R2 R8 / ANIM-R3 B7: the banner's lettering follows the text size and shrinks (to
## BANNER_FONT_MIN, still readable) until the tilted banner fits the poster less
## BANNER_MARGIN a side; past that it wraps to two lines (at "-", else the middle space) and
## only then shrinks further (to BANNER_FONT_FLOOR). The 8 px floor on one line ran a French
## banner 168 px in 164.
const BANNER_FONT_MIN := 12
const BANNER_FONT_FLOOR := 8
const BANNER_MARGIN := 3.0
## Line height of the banner's lettering (x its size) and the gap between it and the poster's
## Heat block (px).
const BANNER_LINE := 1.15
const BANNER_GAP := 4.0
## ANIM-R3 B7: the band's consequence under the banner's words (mono, px at text scale 1.0)
## and the eye glyph before them (x the lettering: width, and the gap after it).
const SUB_FONT := 10
const EYE_W := 1.3
const EYE_GAP := 0.35
## ANIM-R3 B7: a crossing is a warning, never good news: amber (noticed), orange (flagged),
## red (hunted), by band (1-3), not the corporation's colour (Solace green read as good).
## PURGE (band 4) clamps to hunted's red until ART-1 gives it its own look.
const BAND_COLORS: Array[Color] = [Color("#FFB000"), Color("#FFB000"), Color("#FF8C1A"), Color("#FF2A3D")]
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
	# PASS: the scene's tooltip (what the thresholds do) shows on hover. ANIM-R3 B9: set here
	# (it sat after a return in band_label_rect and never ran).
	mouse_filter = Control.MOUSE_FILTER_PASS
	# ANIM-R6 C1: one press completes the Heat's motion with every other (MotionSkip).
	MotionSkip.register(self)


## Where the band word ("cool", "hunted") is drawn (local px).
func band_label_rect() -> Rect2:
	var top := POSTER_BLOCK_TOP if poster else 0.0
	var f := Palette.marker()
	var word := tr(BAND_WORDS[mini(shown_band(), BAND_WORDS.size() - 1)])
	var base := top + BAND_BASELINE
	return Rect2(8, base - f.get_ascent(BAND_FONT), f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT).x, f.get_height(BAND_FONT))


func _make_custom_tooltip(for_text: String) -> Object:
	return UiTip.make(tooltip_words(for_text), "Heat") if for_text != "" else null


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
## plays there (banner, local distortion, letters), then it rolls on to the Heat. ANIM-R6 C1:
## a chain of one-shot steps (it was an await loop no press could end): `_rise_ups` holds the
## thresholds still to reach, and `complete_motion` plays them out at once.
func _play_rise(from: int, ups: Array[int]) -> void:
	shown_heat = from
	_rise_ups.assign(ups)
	_rise_next()


## The thresholds the rise has still to reach (lowest first).
var _rise_ups: Array[int] = []


func _rise_next() -> void:
	if _rise_ups.is_empty():
		Motion.run(&"number_roll", self, ^"shown_heat", float(heat))
		return
	var tw := Motion.run(&"number_roll", self, ^"shown_heat", float(_rise_ups[0]))
	if tw == null:
		_rise_reached()
	else:
		tw.finished.connect(_rise_reached, CONNECT_ONE_SHOT)


func _rise_reached() -> void:
	if _rise_ups.is_empty() or not is_inside_tree():
		return
	var t: int = _rise_ups.pop_front()
	_cross(t, _rise_ups.is_empty())
	_rise_next()


## Crossings `ups` (thresholds) played a pulse apart, the first now (no roll plays).
## ANIM-R6 C1: the ones still to play wait in `_chain_rest` (a press plays them at once).
func _cross_chain(ups: Array[int]) -> void:
	if ups.is_empty():
		return
	_cross(ups[0], ups.size() == 1)
	_chain_rest.assign(ups.slice(1))
	if not _chain_rest.is_empty() and is_inside_tree():
		get_tree().create_timer(Motion.seconds(&"heat_pulse")).timeout.connect(_chain_on)


## Crossings the chain has still to play, and the timer's step to the next one.
var _chain_rest: Array[int] = []


func _chain_on() -> void:
	if _chain_rest.is_empty():
		return
	var rest: Array[int] = []
	rest.assign(_chain_rest)
	_chain_rest.clear()
	_cross_chain(rest)


# --- ANIM-R6 C1: MotionSkip ------------------------------------------------------------------

## A press while the Heat's motion plays (the number's roll, a crossing's pop, shake and band
## stamp, the banner stamping on or fading) completes it with every other running motion
## (MotionSkip.handle; a press that drives the raid playout passes, MotionSkip notes). The
## banner's reading hold is not motion: once stamped, the banner and its consequence note stay
## their hold (`heat_banner`'s delay) whatever is pressed, then fade (STYLE_GUIDE 5.1).
func _input(event: InputEvent) -> void:
	if motion_running():
		MotionSkip.handle(event, self)


## MotionSkip: true while the Heat moves (a roll, a crossing still to play, a pop, the band
## stamp, the banner stamping on or fading out); false during the banner's reading hold.
func motion_running() -> bool:
	if not is_visible_in_tree():
		return false
	if not _rise_ups.is_empty() or not _chain_rest.is_empty() or _banner_phase == BannerPhase.FADE:
		return true
	for key in get_meta_list():
		if String(key).begins_with(Motion.META_PREFIX):
			return true
	return false


## MotionSkip: the Heat at its end state at once: the number on the Heat, every crossing
## still to play played (its banner, the last one's, stamped and held to be read), the pops,
## shake and band stamp at rest; a banner fading out is gone.
func complete_motion() -> void:
	var ups: Array[int] = []
	ups.assign(_rise_ups + _chain_rest)
	_rise_ups.clear()
	_chain_rest.clear()
	Motion.stop(self)
	shown_heat = heat
	number_scale = 1.0
	stamp_scale = 1.0
	shake_offset = Vector2.ZERO
	banner_scale = 1.0
	if not ups.is_empty():
		_banner_at = ups[ups.size() - 1]
		_stamp_banner()
		banner_scale = 1.0
		Motion.stop(self)
	elif _banner_phase == BannerPhase.FADE:
		_end_banner()
	_pending_stamp = false
	queue_redraw()


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
## ANIM-R6 C5: under reduce effects (no motion, the entry on) the banner and its consequence
## note show at once, static, for the hold (a reading time, like RAID INCOMING), then go.
## ANIM-R6 C1: its phases (`_banner_phase`): the hold is a reading time, the fade is motion.
func _stamp_banner() -> void:
	var e := Motion.entry(&"heat_banner")
	if e == null or not e.enabled or not is_inside_tree():
		banner_alpha = 0.0
		return
	banner_alpha = 1.0
	banner_scale = Motion.amplitude(&"heat_banner") if Motion.live(&"heat_banner") else 1.0
	Motion.run(&"poster_stamp", self, ^"banner_scale", 1.0)
	# ANIM-R2 R8: the next crossing's banner replaces this one (its fade must not dim it).
	if _banner_tween != null and _banner_tween.is_valid():
		_banner_tween.kill()
	_banner_phase = BannerPhase.HOLD
	var tw := create_tween()
	_banner_tween = tw
	tw.tween_method(_banner_frame, 0.0, 1.0, Motion.delay_of(&"heat_banner"))
	tw.tween_callback(_start_fade)
	if Motion.live(&"heat_banner"):
		tw.tween_property(self, "banner_alpha", 0.0, Motion.seconds(&"heat_banner")).set_ease(e.ease).set_trans(e.trans)
		tw.parallel().tween_method(_banner_frame, 0.0, 1.0, Motion.seconds(&"heat_banner"))
	tw.tween_callback(_end_banner)
	_note_at = Rect2()
	_banner_frame(0.0)


## ANIM-R6 C1: where the banner is: none, its reading hold, or its fade.
enum BannerPhase { NONE, HOLD, FADE }
var _banner_phase: BannerPhase = BannerPhase.NONE


func _start_fade() -> void:
	_banner_phase = BannerPhase.FADE


## The banner (and its note) gone.
func _end_banner() -> void:
	if _banner_tween != null and _banner_tween.is_valid():
		_banner_tween.kill()
	_banner_tween = null
	_banner_phase = BannerPhase.NONE
	banner_alpha = 0.0
	_update_note()
	queue_redraw()


## ANIM-R6 C1: true during the banner's reading hold (tests).
func banner_holding() -> bool:
	return _banner_phase == BannerPhase.HOLD


## A frame of the banner's hold and fade: the poster redraws, the note follows it.
func _banner_frame(_v: float) -> void:
	queue_redraw()
	_update_note()


# --- ANIM-R5 P9: the consequence note ---------------------------------------------------------

## The band's consequence as a flat note beside the poster while the banner shows (on the
## tilted sticker it was ~9 px for ~1.6 s and covered the WANTED title): mono lettering never
## under NOTE_FONT px, x the text size; NOTE_WIDTH wide (x the text size, never wider than
## the screen less NOTE_MARGIN a side); held as long as the banner (`heat_banner`'s delay, a
## reading time) and fading with it. It stands below the poster, else above, right, left:
## the first spot on the screen that covers no usable button, else the least covered.
const NOTE_FONT := 12
const NOTE_WIDTH := 260.0
const NOTE_PAD := 8.0
const NOTE_GAP := 6.0
const NOTE_MARGIN := 8.0
const NOTE_BORDER := 2.0
var _note: Control = null
var _note_at: Rect2 = Rect2()
var _note_from: Rect2 = Rect2()


## The note's lettering (px).
func note_font_size() -> int:
	return maxi(NOTE_FONT, roundi(NOTE_FONT * Settings.text_scale))


## The note's words: what the band the banner names brings ("" when nothing).
func note_text() -> String:
	return consequence(_banner_at if _banner_at > 0 else heat)


## The note's width (px).
func note_width() -> float:
	var w := NOTE_WIDTH * Settings.text_scale
	if is_inside_tree():
		w = minf(w, get_viewport_rect().size.x - NOTE_MARGIN * 2.0)
	return w


## The note's lines, wrapped to its width (`w`: another width to try; the width placed).
func note_lines(w: float = -1.0) -> PackedStringArray:
	if w <= 0.0:
		w = _note_w if _note_w > 0.0 else note_width()
	return wrap_words(Palette.mono(), note_text(), note_font_size(), w - NOTE_PAD * 2.0)


func note_size(w: float = -1.0) -> Vector2:
	if w <= 0.0:
		w = _note_w if _note_w > 0.0 else note_width()
	return Vector2(w, note_lines(w).size() * note_font_size() * BANNER_LINE + NOTE_PAD * 2.0)


## ANIM-R6 C5: the width the note was placed at (0: its full width), and the narrower shares
## of it it tries when no spot at its full width is free of words (at 1.6 the HQ has room for
## a narrow note under PIRATE RADIO only).
var _note_w: float = 0.0
const NOTE_SHARES: Array[float] = [1.0, 0.8, 0.65]


## Where the note stands (global px; see the notes above). ANIM-R6 C5: it covers no text
## either (at 1.0 and 1.6 it stood on the PIRATE RADIO card's title and words for its whole
## hold): from below the poster, above, right and left, each slid on by NOTE_SLIDE px a step
## (at most NOTE_SLIDE_STEPS), the nearest spot on the screen that covers no usable button and
## no words; else the least covered one.
func note_rect() -> Rect2:
	var avoid := note_avoid()
	var best := Rect2()
	var best_cover := INF
	var best_w := 0.0
	for share in NOTE_SHARES:
		var w := note_width() * share
		var found := _note_spot(note_size(w), avoid)
		if float(found[1]) <= 0.0:
			_note_w = w
			return found[0]
		if float(found[1]) < best_cover:
			best_cover = float(found[1])
			best = found[0]
			best_w = w
	_note_w = best_w
	return best


## The spot for a note of size `s` covering the least of `avoid`: [rect, covered area].
func _note_spot(s: Vector2, avoid: Array[Rect2]) -> Array:
	var p := get_global_rect()
	var screen := get_viewport_rect().grow(-NOTE_MARGIN) if is_inside_tree() else Rect2(Vector2.ZERO, s)
	var starts: Array[Rect2] = [Rect2(Vector2(p.position.x, p.end.y + NOTE_GAP), s), Rect2(Vector2(p.position.x, p.position.y - NOTE_GAP - s.y), s),
		Rect2(Vector2(p.end.x + NOTE_GAP, p.position.y), s), Rect2(Vector2(p.position.x - NOTE_GAP - s.x, p.position.y), s)]
	var steps: Array[Vector2] = [Vector2(0, NOTE_SLIDE), Vector2(0, -NOTE_SLIDE), Vector2(NOTE_SLIDE, 0), Vector2(-NOTE_SLIDE, 0)]
	var best := Rect2()
	var best_cover := INF
	for i in NOTE_SLIDE_STEPS + 1:
		for d in starts.size():
			var r := starts[d]
			r.position += steps[d] * i
			# Kept on the screen (slid along its edge), never over the poster itself.
			r.position = r.position.clamp(screen.position, (screen.end - r.size).max(screen.position))
			if r.intersects(p.grow(-1.0)):
				continue
			var cover := 0.0
			for o in avoid:
				if o.intersects(r):
					cover += o.intersection(r).get_area()
			if cover <= 0.0:
				return [r, 0.0]
			if cover < best_cover:
				best_cover = cover
				best = r
	return [best, best_cover] if best_cover < INF else [starts[0], INF]


## ANIM-R6 C5: how far a note spot slides a step (px) and the most steps it slides.
const NOTE_SLIDE := 24.0
const NOTE_SLIDE_STEPS := 16


## ANIM-R6 C5: what the note keeps off (global px): every usable button and every shown line
## of words (a Label or RichTextLabel with text) on this poster's screen, but its own.
func note_avoid() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if not is_inside_tree():
		return out
	for n in get_tree().root.find_children("*", "Control", true, false):
		var c := n as Control
		if c.get_viewport() != get_viewport() or not c.is_visible_in_tree() or is_ancestor_of(c) or c == self:
			continue
		if c is BaseButton:
			if not (c as BaseButton).disabled:
				out.append(c.get_global_rect())
		elif (c is Label and (c as Label).text != "") or (c is RichTextLabel and (c as RichTextLabel).get_parsed_text() != "") \
				or c is HudStats or c is PadPrompts or c is SubtitleStrip:
			# Drawn words too: the top bar's tags, the pad prompts, the subtitles (at 1.6 the note
			# went up over the CREW tag).
			out.append(c.get_global_rect())
	return out


func _update_note() -> void:
	var show := banner_alpha > 0.0 and note_text() != "" and is_visible_in_tree()
	if not show:
		if _note != null:
			_note.visible = false
		return
	if _note == null:
		_note = Control.new()
		_note.name = "HeatNote"
		_note.top_level = true
		_note.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_note.z_index = NOTE_Z
		_note.draw.connect(_draw_note)
		add_child(_note, false, Node.INTERNAL_MODE_BACK)
	var at := get_global_rect()
	if _note_at == Rect2() or at != _note_from:
		_note_from = at
		_note_at = note_rect()
	_note.position = _note_at.position
	_note.size = _note_at.size
	_note.modulate.a = banner_alpha
	_note.visible = true
	_note.queue_redraw()


## The note's draw order over the page (it is read over whatever it passes).
const NOTE_Z := 50


func _draw_note() -> void:
	var r := Rect2(Vector2.ZERO, _note.size)
	var col := banner_color()
	_note.draw_rect(r.grow(NOTE_BORDER), Color(0, 0, 0, 0.8))
	_note.draw_rect(r, Palette.NIGHT_SKY)
	_note.draw_rect(r, col, false, NOTE_BORDER)
	var f := Palette.mono()
	var fs := note_font_size()
	var lines := note_lines()
	for i in lines.size():
		_note.draw_string(f, Vector2(NOTE_PAD, NOTE_PAD + fs * BANNER_LINE * i + f.get_ascent(fs)), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.PAPER)


## True while the consequence note shows (tests).
func note_showing() -> bool:
	return _note != null and _note.visible


## ANIM-R4 H6: the banner's words: the Heat now, the band it is in and the threshold that
## band starts at ("HEAT 30 · NOTICED (25+)"); the band is the one crossed while a crossing
## plays. "HEAT 5 · COOL" below the first threshold.
func banner_text() -> String:
	var at := _banner_at if _banner_at > 0 else _band_floor(heat)
	var word := tr(BAND_WORDS[mini(band_of(at, marks), BAND_WORDS.size() - 1)]).to_upper()
	if at <= 0:
		return tr("HEAT %d · %s") % [heat, word]
	return tr("HEAT %d · %s (%d+)") % [heat, word, at]


## The threshold the band of Heat `value` starts at (0 below the first).
func _band_floor(value: int) -> int:
	var best := 0
	for t in marks:
		if value >= t:
			best = maxi(best, t)
	return best


## ANIM-R4 H6: the band the poster's number is in now (the band word follows the number
## as it rolls: it said NOTICED while the roll still showed 21).
func shown_band() -> int:
	return band_of(roundi(shown_heat), marks)


## ART-10 4C: the colour of the band the number shows (Palette.HEAT_BAND_COLORS), as ink on
## the paper poster (COOL = INK; the warm bands a step darker).
func band_color() -> Color:
	var b := mini(shown_band(), Palette.HEAT_BAND_COLORS.size() - 1)
	var col: Color = Palette.HEAT_BAND_COLORS[b]
	if poster:
		return Palette.INK if b == 0 else col.darkened(PAPER_DARKEN)
	return col


## How much darker a band colour is on the paper poster.
const PAPER_DARKEN := 0.25


## ANIM-R3 B7: the banner's colour: the band's warning colour (BAND_COLORS).
func banner_color() -> Color:
	var at := _banner_at if _banner_at > 0 else heat
	return BAND_COLORS[clampi(band_of(at, marks), 0, BAND_COLORS.size() - 1)]


## ANIM-R3 B7 / ANIM-R4 H5: what threshold `at` brings (its content text, translated through
## its TextDb key: "A raid is queued. While Heat stays at 25 or more, elites
## are more frequent."); "" when no campaign or no such threshold.
static func consequence(at: int) -> String:
	var cfg: CampaignConfigData = RunManager.config() if RunManager.campaign != null else null
	if cfg == null:
		return ""
	var best: HeatThresholdData = null
	for t in cfg.heat_thresholds:
		if t != null and t.kind == RC.ThresholdKind.MAJOR and t.heat <= at and (best == null or t.heat > best.heat):
			best = t
	return TextDb.t(best, "event_text") if best != null else ""


## ANIM-R4 H6: the banner laid out in the room it has (banner_room), worked out once per
## change (its inputs are the key): {"lines", "fs" (the words' lettering), "subs" (the
## consequence's lines, maybe none), "sfs" (their lettering), "rect" (the box, unrotated,
## local px)}. The words keep one line down to BANNER_FONT_MIN, then wrap (at " · ", then
## at spaces, a word too long for a line broken between letters) down to BANNER_FONT_FLOOR;
## the consequence shrinks with them and is left to the tooltip only when the box would not
## fit the room even at the floor. The whole tilted box, sub-lines included, stays inside
## the room ("room" in the result: banner_room, or on a short small poster whose room under
## the bar holds nothing at the floor, banner_room_wide, which takes the bar too).
## ANIM-R5 P9: the consequence is the flat note beside the poster now (note_lines); the
## banner carries the band line alone ("subs" stays empty).
func banner_layout() -> Dictionary:
	var room := banner_room()
	var text := banner_text()
	var key := "%s|%s|%.2f|%s" % [text, room, Settings.text_scale, TranslationServer.get_locale()]
	if key == _layout_key:
		return _layout
	_layout_key = key
	_layout = _fit_banner(text, "", room)
	if _layout.is_empty():
		var wide := banner_room_wide()
		_layout = _fit_banner(text, "", wide)
		if _layout.is_empty():
			_layout = _floor_banner(text, wide)
	return _layout


var _layout_key: String = ""
var _layout: Dictionary = {}


## The room the banner may cover (local px): the wanted poster's mugshot band, under its
## WANTED title (ANIM-R5 P9: it covered the title), above the Heat block; the small poster's
## paper under its Heat bar. Never the number.
func banner_room() -> Rect2:
	var width := size.x if size.x > 0.0 else custom_minimum_size.x
	var height := size.y if size.y > 0.0 else custom_minimum_size.y
	if poster:
		return Rect2(BANNER_MARGIN, TITLE_BOTTOM + BANNER_GAP, width - BANNER_MARGIN * 2.0, POSTER_BLOCK_TOP - TITLE_BOTTOM - BANNER_GAP * 2.0)
	var top := BAR_BOTTOM + BANNER_GAP
	return Rect2(BANNER_MARGIN, top, width - BANNER_MARGIN * 2.0, maxf(0.0, height - top - BANNER_GAP))


## The small poster's last resort (banner_layout): its paper from the top of the Heat bar
## down (the bar hides for the banner's hold; the number and "/max" stay clear). The wanted
## poster's room is its header either way.
func banner_room_wide() -> Rect2:
	if poster:
		# ANIM-R5 P9: a banner too long for the band under WANTED (a long translation) takes the
		# whole header, the title too, rather than lettering under the floor.
		var width := size.x if size.x > 0.0 else custom_minimum_size.x
		return Rect2(BANNER_MARGIN, BANNER_GAP, width - BANNER_MARGIN * 2.0, POSTER_BLOCK_TOP - BANNER_GAP * 2.0)
	var width := size.x if size.x > 0.0 else custom_minimum_size.x
	var height := size.y if size.y > 0.0 else custom_minimum_size.y
	return Rect2(BANNER_MARGIN, BAR_TOP, width - BANNER_MARGIN * 2.0, maxf(0.0, height - BAR_TOP - BANNER_GAP))


## The top of the Heat bar below the block's top (px).
const BAR_TOP := 44.0
## ANIM-R5 P9: the wanted poster's WANTED title: its baseline, lettering and the bottom of
## its line (px); the banner keeps under it.
const TITLE_BASELINE := 30.0
const TITLE_FONT := 26
const TITLE_BOTTOM := 36.0


## ANIM-R5 P9: the WANTED title's box (local px; the wanted poster only).
func title_rect() -> Rect2:
	var f := Palette.display()
	return Rect2(10, TITLE_BASELINE - f.get_ascent(TITLE_FONT), f.get_string_size(tr("WANTED"), HORIZONTAL_ALIGNMENT_LEFT, size.x - 20, TITLE_FONT).x, f.get_height(TITLE_FONT))


func _fit_banner(text: String, sub: String, room: Rect2) -> Dictionary:
	var f := Palette.display()
	var top := maxi(BANNER_FONT_MIN, roundi(BANNER_FONT * Settings.text_scale))
	var sub_top := maxi(BANNER_FONT_FLOOR, roundi(SUB_FONT * Settings.text_scale))
	for with_sub in ([true, false] if sub != "" else [false]):
		for wrap in [false, true]:
			for fs in range(top, (BANNER_FONT_FLOOR if wrap else BANNER_FONT_MIN) - 1, -1):
				var inner := room.size.x - fs * (EYE_W + EYE_GAP) - BANNER_PAD * 2.0 - SUB_TILT_ROOM
				var lines := wrap_words(f, text, fs, inner, " · ") if wrap else PackedStringArray([text])
				if not wrap and banner_span(f, lines, fs) > room.size.x:
					continue
				var sfs := clampi(roundi(fs * float(SUB_FONT) / BANNER_FONT), BANNER_FONT_FLOOR, sub_top)
				var subs := wrap_words(Palette.mono(), sub, sfs, room.size.x - BANNER_PAD * 2.0 - SUB_TILT_ROOM) if with_sub else PackedStringArray()
				if subs.size() > SUB_LINES_MAX:
					continue
				var r := _banner_box(lines, fs, subs, sfs, room)
				var t := _tilted(r.size)
				if t.x <= room.size.x + 0.5 and t.y <= room.size.y + 0.5:
					return {"lines": lines, "fs": fs, "subs": subs, "sfs": sfs, "rect": r, "room": room}
	return {}


## The words alone at the floor in `room` (nothing fits it otherwise).
func _floor_banner(text: String, room: Rect2) -> Dictionary:
	var last := wrap_words(Palette.display(), text, BANNER_FONT_FLOOR, room.size.x - BANNER_FONT_FLOOR * (EYE_W + EYE_GAP) - BANNER_PAD * 2.0 - SUB_TILT_ROOM, " · ")
	return {"lines": last, "fs": BANNER_FONT_FLOOR, "subs": PackedStringArray(), "sfs": BANNER_FONT_FLOOR,
		"rect": _banner_box(last, BANNER_FONT_FLOOR, PackedStringArray(), BANNER_FONT_FLOOR, room), "room": room}


## The unrotated box of a banner (local px): as wide as its widest line, as tall as its
## lines; centred across the poster, and in the room: the wanted poster's header centres it,
## the small poster hangs it under the bar.
func _banner_box(lines: PackedStringArray, fs: int, subs: PackedStringArray, sfs: int, room: Rect2) -> Rect2:
	var w := 0.0
	for line in lines:
		w = maxf(w, Palette.display().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	w += fs * (EYE_W + EYE_GAP) + BANNER_PAD * 2.0
	for line in subs:
		w = maxf(w, Palette.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, sfs).x + BANNER_PAD * 2.0)
	var h := banner_height(lines.size(), fs) + subs.size() * sfs * BANNER_LINE
	var t := _tilted(Vector2(w, h))
	var cy := room.get_center().y if poster else room.position.y + t.y * 0.5
	return Rect2(Vector2(room.get_center().x - w * 0.5, cy - h * 0.5), Vector2(w, h))


## The span of a box `s` tilted by BANNER_TILT (px): its bounding box's size.
static func _tilted(s: Vector2) -> Vector2:
	var a := deg_to_rad(absf(BANNER_TILT))
	return Vector2(s.x * cos(a) + s.y * sin(a), s.x * sin(a) + s.y * cos(a))


## `text` wrapped to lines no wider than `room` at `fs`: first at `first_break` (the
## banner's " · "), then at spaces; a word wider than a line on its own is broken between
## letters (a long compound in a translation never runs off the poster).
static func wrap_words(f: Font, text: String, fs: int, room: float, first_break: String = "") -> PackedStringArray:
	var out := PackedStringArray()
	if text == "":
		return out
	var parts := PackedStringArray([text])
	if first_break != "" and text.contains(first_break):
		parts = text.split(first_break, false)
	for part in parts:
		var line := ""
		for word in part.strip_edges().split(" ", false):
			var next := word if line == "" else line + " " + word
			if f.get_string_size(next, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room:
				line = next
				continue
			if line != "":
				out.append(line)
			line = ""
			# The word alone: whole when it fits, else in pieces.
			var piece := ""
			for ch in word:
				if piece != "" and f.get_string_size(piece + ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
					out.append(piece)
					piece = ""
				piece += ch
			line = piece
		if line != "":
			out.append(line)
	return out


## The banner's lines at its lettering size: {"lines": PackedStringArray, "fs": int}
## (banner_layout).
func banner_lines() -> Dictionary:
	var lay := banner_layout()
	return {"lines": lay["lines"], "fs": lay["fs"]}


## ANIM-R2 R8: the banner's lettering (px) (banner_lines).
func banner_font_size() -> int:
	return int(banner_layout()["fs"])


## `text` in two lines: after its " · " (or " - ") when it has one, else at the space
## nearest its middle (one line when it has no space).
static func split_banner(text: String) -> PackedStringArray:
	for mark in [" · ", " - "]:
		var at := text.find(mark)
		if at >= 0:
			return PackedStringArray([text.left(at + mark.length() - 1).strip_edges(), text.substr(at + mark.length()).strip_edges()])
	var best := -1
	for i in text.length():
		if text[i] == " " and (best < 0 or absi(i - text.length() / 2) < absi(best - text.length() / 2)):
			best = i
	if best < 0:
		return PackedStringArray([text])
	return PackedStringArray([text.left(best), text.substr(best + 1)])


## The width the tilted banner of `lines` at `fs` spans on the poster (px), its eye glyph
## included.
static func banner_span(f: Font, lines: Variant, fs: int) -> float:
	var list: PackedStringArray = PackedStringArray([lines]) if lines is String else lines
	var w := 0.0
	for line in list:
		w = maxf(w, f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	w += fs * (EYE_W + EYE_GAP) + BANNER_PAD * 2.0
	var h := banner_height(list.size(), fs)
	var a := deg_to_rad(absf(BANNER_TILT))
	return w * cos(a) + h * sin(a)


## The banner box's height for `count` lines at `fs` (px, sub-line not included).
static func banner_height(count: int, fs: int) -> float:
	return count * fs * BANNER_LINE + BANNER_PAD * 1.5


## ANIM-R3 B7 / ANIM-R4 H6: where the banner's box sits, unrotated (local px), sub-lines
## included (banner_layout): over the wanted poster's header, under the small poster's bar;
## never over the number, and (tilted) inside the poster.
func banner_rect() -> Rect2:
	return banner_layout()["rect"]


## The banner box's corners as drawn (tilted round its centre, local px).
func banner_corners() -> PackedVector2Array:
	var r := banner_rect()
	var c := r.get_center()
	var out := PackedVector2Array()
	for p in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		out.append(c + (p - c).rotated(deg_to_rad(BANNER_TILT)))
	return out


## The bottom of the Heat bar below the block's top (px; the small poster's banner hangs
## under it).
const BAR_BOTTOM := 52.0


func sub_font_size() -> int:
	return int(banner_layout()["sfs"])


## The consequence under the banner, wrapped to the poster (banner_layout; none when it
## would not fit even at the smallest lettering: the tooltip says it then).
func sub_lines() -> PackedStringArray:
	return banner_layout()["subs"]


const SUB_LINES_MAX := 4
## Width kept free beside the lines so the tilted, taller box still fits (px).
const SUB_TILT_ROOM := 12.0


## ANIM-R3 B7: the tooltip adds what the band in force does.
func tooltip_words(for_text: String) -> String:
	var band_line := consequence(heat)
	if band_line == "" or for_text.contains(band_line):
		return for_text
	return for_text + "\n" + tr(BAND_WORDS[mini(band, BAND_WORDS.size() - 1)]).to_upper() + ": " + band_line


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
	# ART-10 4C (audit P2, ART_BIBLE v2 §2.8): the number and the bar take the band's colour
	# (five bands; the band word says it too); on the paper poster COOL is ink and the warm
	# bands darken a step so they read on the stock.
	var num_col := band_color()
	if number_scale > 1.0:
		num_col = num_col.lerp(Palette.PAPER, clampf((number_scale - 1.0) / maxf(0.001, Motion.amplitude(&"heat_number_pop") - 1.0), 0.0, 1.0))
	var num_at := Vector2(x + 6, y + 30)
	draw_set_transform(num_at + Vector2(0, -NUMBER_FONT * 0.35), 0.0, Vector2.ONE * number_scale)
	draw_string(Palette.display(), Vector2(0, NUMBER_FONT * 0.35), "%d" % roundi(shown_heat), HORIZONTAL_ALIGNMENT_LEFT, -1, NUMBER_FONT, num_col)
	draw_set_transform(Vector2.ZERO)
	draw_string(Palette.mono(), Vector2(x + 6, y + 44), "/%d" % heat_max, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.INK if poster else Palette.PAPER)
	var bar := Rect2(8, y + 44, size.x - 16, 8)
	draw_rect(bar, Color(Palette.INK, 0.3) if poster else Color(Palette.PAPER, 0.15))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(float(heat) / maxf(1.0, heat_max), 0.0, 1.0), bar.size.y)), band_color())
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
		draw_string(Palette.marker(), Vector2(8, y + BAND_BASELINE) - c, tr(BAND_WORDS[mini(shown_band(), BAND_WORDS.size() - 1)]), HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT, word_col)
		draw_set_transform(Vector2.ZERO)
	else:
		draw_string(Palette.marker(), Vector2(8, y + BAND_BASELINE), tr(BAND_WORDS[mini(shown_band(), BAND_WORDS.size() - 1)]), HORIZONTAL_ALIGNMENT_LEFT, -1, BAND_FONT, word_col)
	if banner_alpha > 0.0:
		_draw_banner(y)


## ANIM-R1 M6 / ANIM-R3 B7: the crossing's banner ("HEAT 30 · NOTICED (25+)"), tilted like
## a stamp, in the band's warning colour with an eye glyph; beside the Heat number, never
## over it (banner_rect), and it fades after its hold. ANIM-R5 P9: the band's consequence is
## no longer on the sticker (9 px, tilted): it is the flat note beside the poster
## (`note_lines`, `_draw_note`).
func _draw_banner(y: float) -> void:
	var f := Palette.display()
	var lay := banner_lines()
	var fs: int = lay["fs"]
	var lines: PackedStringArray = lay["lines"]
	var subs := sub_lines()
	var sfs := sub_font_size()
	var r := banner_rect()
	if not poster:
		r.position.y += y
	var col := banner_color()
	var a := banner_alpha
	draw_set_transform(r.get_center(), deg_to_rad(BANNER_TILT), Vector2.ONE * banner_scale)
	var box := Rect2(-r.size * 0.5, r.size)
	draw_rect(box.grow(2.0), Color(0, 0, 0, 0.8 * a))
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.94 * a))
	draw_rect(box, Color(col, a), false, 3.0)
	var x := box.position.x + BANNER_PAD
	var line_h := fs * BANNER_LINE
	var top := box.position.y + BANNER_PAD * 0.75
	_draw_eye(Vector2(x + fs * EYE_W * 0.5, top + line_h * lines.size() * 0.5), fs, Color(col, a))
	x += fs * (EYE_W + EYE_GAP)
	for i in lines.size():
		draw_string(f, Vector2(x, top + line_h * i + f.get_ascent(fs)), lines[i], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col.lerp(Palette.PAPER, 0.25), a))
	var sy := top + line_h * lines.size()
	for i in subs.size():
		draw_string(Palette.mono(), Vector2(box.position.x + BANNER_PAD, sy + sfs * BANNER_LINE * i + Palette.mono().get_ascent(sfs)), subs[i],
			HORIZONTAL_ALIGNMENT_LEFT, -1, sfs, Color(Palette.PAPER, a))
	draw_set_transform(Vector2.ZERO)


## ANIM-R3 B7: the watching eye before the banner's words (an almond outline and its pupil),
## `fs` px tall, centred on `c`.
func _draw_eye(c: Vector2, fs: int, col: Color) -> void:
	var w := fs * EYE_W * 0.5
	var h := fs * 0.42
	var pts := PackedVector2Array()
	for i in 17:
		var t := PI * i / 16.0
		pts.append(c + Vector2(-cos(t) * w, -sin(t) * h))
	for i in range(1, 16):
		var t := PI * i / 16.0
		pts.append(c + Vector2(cos(t) * w, sin(t) * h))
	pts.append(pts[0])
	draw_polyline(pts, col, 2.0)
	draw_circle(c, h * 0.62, col)
	draw_circle(c, h * 0.25, Palette.NIGHT_SKY)
