class_name SendItSticker
extends DripButton
## ART-2 2D (ART_BIBLE v2 §1.3, §2.10, §4.13; round 22 `send_it_sticker`): a verb as a vinyl
## sticker slapped over a washed-out system word in the terminal font: SEND IT over
## `EXECUTE`, with `> turn_resolve.exe [Space]` under it. Anton lettering in the sticker's
## colour (light top, keyline, extrude, white die-cut, rest gloss); hover lifts it (x1.05)
## and sweeps the gloss, a press squashes it, disabled greys it, focus gives it a lime
## die-cut halo. It keeps DripButton's API and motion entries (`send_it_press`, `drip_halo`,
## `drip_grow` = the slap as it first shows, `send_it_drips` = the shadow snapping in,
## `send_it_ready`): art restyles motion, never drops it. View only; the scene decides what
## a press means.
## ART-1 1B landed: the sticker's art is 1B's VinylSticker (`art`, Anton jitter, keyline,
## extrude, die-cut, rim, gloss, its own slap / hover / press / sweep entries) over the
## system word, with this button's states mapped onto it; the drawn sticker below stays only as
## the fallback when `use_kit_art` is off. The terminal line and the focus halo stay this
## button's.

## The system word under the sticker and the terminal line beside its key.
var system_word: String = "EXECUTE"
var system_line: String = "> turn_resolve.exe"
## The sticker's tilt (degrees).
var tilt: float = -4.0

## The system word's size as a share of the lettering's, and how far the sticker sits in
## from its left edge (share of the word's width) and down from its top (share of `fs`).
const SYSTEM_SHARE := 0.8
const STICKER_IN := 0.3
const STICKER_DOWN := 0.62
## The terminal line's size as a share of the key hint's, and the largest text scale that
## still shows its words (above it, the key alone).
const LINE_SHARE := 0.8
const LINE_FULL_UP_TO := 1.3
## Hover: lift (px at text scale 1.0) and scale.
const HOVER_LIFT := 3.0
const HOVER_SCALE := 1.05
## The first slap's overshoot (scale at grow 0).
const SLAP_FROM := 1.25
## The die-cut and keyline are stamped round the letters this many times.
const STAMPS := 16
## The shadow's offset (px at text scale 1.0) and alpha.
const SHADOW_OFFSET := Vector2(4.0, 6.0)
const SHADOW_ALPHA := 0.55
## The disabled sticker's RESOLVING chip lettering share of the key hint.
const RESOLVING_SHARE := 0.9
## 1B's sticker for SEND IT-sized lettering (HERO) and smaller verbs (DISPLAY): the font size
## from which the HERO step is used.
const HERO_FROM := 80
## Text scales up to which the kit sticker keeps its step, and up to which it takes HEADING
## (above: TITLE).
const ART_SCALE_SMALL := 1.3
const ART_SCALE_MID := 1.7
## The focus halo round the kit sticker (px) and its stroke.
const HALO_PAD := 6.0
const HALO_PX := 3.0
## The kit sticker sits right of and below the drawn lettering's place (shares of the system
## word's width and of the font size), so EXECUTE reads above-left of it (round 22).
const ART_SHIFT := Vector2(0.22, 0.18)

## 1B's vinyl sticker drawing this button's lettering (null = the drawn fallback).
var art: VinylSticker = null
## Draw with 1B's sticker (the kit material); off = the drawn fallback.
static var use_kit_art: bool = true
var _art_state: int = -1
var _slapped: bool = false


func _init(p_text: String = "SEND IT", p_hint: String = "", p_color: Color = HudSkin.VINYL_PINK, p_size: int = 56) -> void:
	super(p_text, p_hint, p_color, p_size, [])
	if use_kit_art:
		art = VinylSticker.new()
		art.name = "Art"
		art.mouse_filter = Control.MOUSE_FILTER_IGNORE
		art.font_step = art_step()
		art.tilt_deg = tilt
		add_child(art)
		_sync_art_words()
		resized.connect(_place_art)


## The kit sticker's fill for this button's paint: yellow for the safe choice, white for a
## lost fight's JACK OUT, else the Cell's pink.
func kit_fill() -> VinylSticker.Fill:
	if paint == HudSkin.VINYL_YELLOW:
		return VinylSticker.Fill.YELLOW
	if paint == Palette.PAPER:
		return VinylSticker.Fill.WHITE
	return VinylSticker.Fill.PINK


func _sync_art_words() -> void:
	if art == null:
		return
	var shown := String(shown_lettering()[0])
	if art.text != shown:
		art.text = shown
	if art.fill != kit_fill():
		art.fill = kit_fill()
	var step := art_step()
	if art.font_step != step:
		art.font_step = step
	_place_art()


## The kit sticker's type step: the sticker is a baked object, so at big text it takes a
## smaller step and keeps about its 1.0 size (§2.9).
func art_step() -> int:
	var base := UiTheme.HERO if font_size >= HERO_FROM else UiTheme.DISPLAY
	var ts := Settings.text_scale
	if ts <= ART_SCALE_SMALL:
		return base
	return UiTheme.HEADING if ts <= ART_SCALE_MID else UiTheme.TITLE


## The kit sticker's centre: where the drawn lettering's middle would be.
func _place_art() -> void:
	if art == null:
		return
	var tw := face().get_string_size(String(shown_lettering()[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	art.place_center(_base() + Vector2(tw * 0.5 + _system_w() * ART_SHIFT.x, -font_size * 0.35 + font_size * ART_SHIFT.y))
	# Kept inside the button on the right (the screen's edge is there).
	var over := art.position.x + art.body_rect.end.x - size.x
	if over > 0.0:
		art.position.x -= over


## This button's state on the kit sticker (rest, hover, pressed, disabled).
func _sync_art_state() -> void:
	if art == null:
		return
	var st := state()
	var want := VinylSticker.State.REST
	if disabled:
		want = VinylSticker.State.DISABLED
	elif st == KitState.PRESSED:
		want = VinylSticker.State.PRESSED
	elif st == KitState.HOVER or st == KitState.FOCUS or _hot:
		want = VinylSticker.State.HOVER
	if int(want) != _art_state:
		_art_state = int(want)
		art.set_state(want)


func set_tag_text(text: String) -> void:
	super(text)
	_sync_art_words()


## The first show slaps the kit sticker on (its `slap` entry) with DripButton's growth.
func grow_in() -> void:
	super()
	if art != null and not _slapped and is_visible_in_tree():
		_slapped = true
		art.slap()


func motion_running() -> bool:
	return super() or (art != null and art.motion_running())


func complete_motion() -> void:
	super()
	if art != null:
		art.complete_motion()


## The lettering face: Anton (display).
static func face() -> Font:
	return HudSkin.display()


func shown_lettering() -> Array:
	var shown := String(TranslationServer.translate(tag_text))
	var room := lettering_room()
	var fs := font_size
	var floor_size := maxi(1, roundi(font_size * FIT_MIN_SHARE))
	while fs > floor_size and face().get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	return [shown, fs]


func lettering_room() -> float:
	var shown := String(TranslationServer.translate(tag_text))
	var floor_size := maxi(1, roundi(font_size * FIT_MIN_SHARE))
	return maxf(face().get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x,
		face().get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, floor_size).x)


func drawn_width() -> float:
	var lettering := shown_lettering()
	return _sticker_x() + face().get_string_size(String(lettering[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, int(lettering[1])).x


func _system_px() -> int:
	return roundi(font_size * SYSTEM_SHARE)


func _system_w() -> float:
	return HudSkin.mono().get_string_size(String(TranslationServer.translate(system_word)), HORIZONTAL_ALIGNMENT_LEFT, -1, _system_px()).x


## Where the lettering starts (px from the left edge).
func _sticker_x() -> float:
	return HudSkin.VINYL_DIE_CUT_PX + _system_w() * STICKER_IN


## The system word's baseline (local y).
func _system_y() -> float:
	if system_word == "":
		# No system word: the sticker's top sits under its die-cut.
		return HudSkin.VINYL_DIE_CUT_PX + face().get_ascent(font_size) - font_size * STICKER_DOWN
	return HudSkin.mono().get_ascent(_system_px()) + 2.0


## The terminal line under the sticker ("> turn_resolve.exe [Space]") as drawn.
func _line_words() -> String:
	# At big text the line keeps the key only (the room is the hand's).
	var line := String(TranslationServer.translate(system_line)) if Settings.text_scale <= LINE_FULL_UP_TO else ""
	if disabled and system_line != "":
		line = String(TranslationServer.translate("RESOLVING..."))
	return ("%s %s" % [line, key_hint]).strip_edges()


func _line_w() -> float:
	return HudSkin.mono().get_string_size(_line_words(), HORIZONTAL_ALIGNMENT_LEFT, -1, _hint_px()).x + 12.0 + (_hint_px() * 2.0 + GLYPH_GAP if glyph else 0.0)


func _hint_px() -> int:
	return roundi(HINT_SIZE * LINE_SHARE * Settings.text_scale)


func _fit_size() -> void:
	var cut := HudSkin.VINYL_DIE_CUT_PX
	var w := maxf(maxf(_system_w(), _sticker_x() + lettering_room() + cut), _line_w())
	var h := _system_y() + font_size * STICKER_DOWN + face().get_descent(font_size) + cut + HudSkin.VINYL_EXTRUDE_PX
	if key_hint != "" or system_line != "":
		h += _hint_px() + 8.0
	custom_minimum_size = Vector2(w + cut, h)


## The lettering's baseline (local, before the hover / press transforms).
func _base() -> Vector2:
	return Vector2(_sticker_x(), _system_y() + font_size * STICKER_DOWN)


func _draw() -> void:
	if art != null:
		_draw_with_art()
		return
	var s := Settings.text_scale
	var lettering := shown_lettering()
	var shown: String = lettering[0]
	var fs: int = lettering[1]
	var f := face()
	var st := state()
	var off := disabled
	var base := _base()
	var tw := f.get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# The machine underneath: the system word, mono, scanlined, washed out.
	var sys := String(TranslationServer.translate(system_word))
	var sp := _system_px()
	var sys_base := Vector2(0.0, _system_y())
	_draw_plate(sys)
	if sys != "":
		draw_string(HudSkin.mono(), sys_base, sys, HORIZONTAL_ALIGNMENT_LEFT, -1, sp, Color(HudSkin.TERMINAL_TEXT, HudSkin.SYSTEM_WORD_ALPHA))
	# The sticker: hover lifts and grows it, a press squashes it, the first show slaps it on.
	var hot := (st == KitState.HOVER or st == KitState.FOCUS or _hot) and not off
	var k := (HOVER_SCALE if hot else 1.0) * lerpf(SLAP_FROM, 1.0, clampf(grow, 0.0, 1.0))
	var pivot := base + Vector2(tw * 0.5, -fs * 0.35)
	var lift := Vector2(0.0, -HOVER_LIFT * s if hot else KitState.lift(st))
	var sq := squash
	draw_set_transform(pivot + lift, deg_to_rad(tilt), Vector2(k / maxf(0.01, sq), k * sq))
	var at := base - pivot
	var paint_col := paint if not off else HudSkin.VINYL_DISABLED
	var light := paint_col.lightened(HudSkin.VINYL_LIGHT)
	var dark := paint_col.darkened(HudSkin.VINYL_DARK)
	var cut := HudSkin.VINYL_DIE_CUT_PX
	var key := HudSkin.VINYL_KEYLINE_PX
	var ext := HudSkin.VINYL_EXTRUDE_PX
	# Shadow (snaps in on a press: `send_it_drips` runs it in).
	var shadow := SHADOW_OFFSET * s * (1.0 - clampf(drip_run / maxf(1.0, Motion.amplitude(&"send_it_drips")), 0.0, 1.0) * 0.6)
	_stamp(f, at + shadow, shown, fs, cut, Color(Palette.NIGHT_SKY, SHADOW_ALPHA))
	# The die-cut: white (focus is the kit sticker's sheen and curl, never lime).
	var die := HudSkin.VINYL_DIE_CUT
	_stamp(f, at, shown, fs, cut, die)
	_stamp(f, at + Vector2(0.0, ext), shown, fs, cut, die)
	# Keyline round letters and extrude, then the extrude itself.
	_stamp(f, at, shown, fs, key, HudSkin.VINYL_KEYLINE)
	_stamp(f, at + Vector2(0.0, ext), shown, fs, key, HudSkin.VINYL_KEYLINE)
	var steps := maxi(1, roundi(ext))
	for i in steps:
		draw_string(f, at + Vector2(0.0, ext * float(steps - i) / steps), shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, dark)
	# The face: a light top, the colour below (the gradient), the gloss over it.
	draw_string(f, at, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, light)
	draw_string(f, at + Vector2(0.0, fs * 0.08), shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, paint_col)
	var swell := sin(PI * clampf(halo_pulse, 0.0, 1.0))
	var gloss := lerpf(HudSkin.VINYL_GLOSS_REST, HudSkin.VINYL_GLOSS_HOT, swell if hot else 0.0)
	draw_string(f, at + Vector2(-1.0, -fs * 0.02), shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(HudSkin.VINYL_DIE_CUT, gloss * 0.5))
	draw_set_transform(Vector2.ZERO)
	# The terminal line and its key: "> turn_resolve.exe [Space]"; RESOLVING while disabled.
	var hs := _hint_px()
	var words := _line_words()
	if words != "":
		var hw := HudSkin.mono().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, hs).x
		var hp := Vector2(6.0, size.y - 5.0)
		if sys == "":
			draw_rect(Rect2(hp + Vector2(-6, -hs), Vector2(hw + 12, hs + 5)), Color(PaletteSkins.chrome(HudSkin.TERMINAL_BG), 0.85))
		draw_string(HudSkin.mono(), hp, words, HORIZONTAL_ALIGNMENT_LEFT, -1, hs, HudSkin.TERMINAL_TEXT if not off else HudSkin.TERMINAL_DIM)
		if glyph:
			_draw_glyph(Vector2(hp.x + hw + 6.0 + GLYPH_GAP + hs * 2.0, hp.y - hs * 0.5 + 2.0), hs, paint_col)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), st, false)


## `text` stamped round itself at `radius` in `col` (die-cut, keyline, shadow).
func _stamp(f: Font, at: Vector2, text: String, fs: int, radius: float, col: Color) -> void:
	for i in STAMPS:
		var o := Vector2(cos(TAU * i / STAMPS), sin(TAU * i / STAMPS)) * radius
		draw_string(f, at + o, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


## S-COMBAT-HUD (parity CMB-06, combat_typical_v4): the machine under the sticker is a dark
## terminal plate (glass, its edge dim) holding the washed-out system word and the terminal
## line, so EXECUTE reads as a plate the sticker is slapped on, not a pale outline floating
## alone (it read like a rendering fault).
func _draw_plate(sys: String) -> void:
	if sys == "":
		return
	var sp := _system_px()
	var top := _system_y() - HudSkin.mono().get_ascent(sp) - PLATE_PAD
	var w := maxf(_system_w(), _line_w()) + PLATE_PAD * 2.0
	HudSkin.draw_terminal_panel(self, Rect2(Vector2(-PLATE_PAD, top), Vector2(w, size.y - top)),
		Color(PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), HudSkin.SYSTEM_WORD_ALPHA), Color(PaletteSkins.chrome(HudSkin.TERMINAL_BG), PLATE_ALPHA))


## The plate's padding round the system word (px) and its glass's alpha.
const PLATE_PAD := 4.0
const PLATE_ALPHA := 0.72


## With 1B's sticker: the system word and the terminal line here, the sticker is `art`; focus
## is the kit sticker's own rainbow sheen and curl (designer 2026-10-05: no halo, no brackets).
func _draw_with_art() -> void:
	_sync_art_words()
	_sync_art_state()
	var sys := String(TranslationServer.translate(system_word))
	var sp := _system_px()
	var sys_base := Vector2(0.0, _system_y())
	_draw_plate(sys)
	if sys != "":
		draw_string(HudSkin.mono(), sys_base, sys, HORIZONTAL_ALIGNMENT_LEFT, -1, sp, Color(HudSkin.TERMINAL_TEXT, HudSkin.SYSTEM_WORD_ALPHA))
	var hs := _hint_px()
	var words := _line_words()
	if words != "":
		var hw := HudSkin.mono().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, hs).x
		var hp := Vector2(6.0, size.y - 5.0)
		if sys == "":
			draw_rect(Rect2(hp + Vector2(-6, -hs), Vector2(hw + 12, hs + 5)), Color(PaletteSkins.chrome(HudSkin.TERMINAL_BG), 0.85))
		draw_string(HudSkin.mono(), hp, words, HORIZONTAL_ALIGNMENT_LEFT, -1, hs, HudSkin.TERMINAL_TEXT if not disabled else HudSkin.TERMINAL_DIM)
		if glyph:
			_draw_glyph(Vector2(hp.x + hw + 6.0 + GLYPH_GAP + hs * 2.0, hp.y - hs * 0.5 + 2.0), hs, paint if not disabled else HudSkin.VINYL_DISABLED)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state(), false)
