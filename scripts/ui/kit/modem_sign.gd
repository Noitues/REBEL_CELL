class_name ModemSign
extends Control
## The Modem's vertical neon sign (left edge of the shop). Art pass W8c (ART_BIBLE §4.3
## rule 5, §11 Modem, critique 52 / §6 "Modem sign"): **baked art**, the original SVG
## `assets/art/netrun/modem_sign.svg` (a pink neon frame round a dark circuit board, MODEM
## stacked in angular pink tubes, CYBER SHOP in cyan tubes), never live text in a display
## face. When the player's language says the words differently, a translated subtitle sits
## at the sign's foot (§10.6). The BUY / SHRED sticky notes that overlapped its corner are
## gone: in the Modem a sticker is always a button (the items' BUY / SHRED stickers).
## Decoration.

const PINK := Palette.CELL_PINK
## The baked sign and its size in the SVG (px; the texture is imported at 2x).
const ART := preload("res://assets/art/netrun/modem_sign.svg")
const ART_SIZE := Vector2(210, 540)
## The sign's horizontal bands in ART_SIZE px (top edges; the last ends at the foot): the
## five MODEM letters, then CYBER SHOP. Each band is one "tube" in the warm-up.
const BANDS: Array[float] = [0.0, 105.0, 171.0, 237.0, 303.0, 382.0]
## Retired (art pass W8c): the sticky notes the drawn sign carried. Kept as the list of what
## the Modem does (it sells and removes cards; nothing is sold back, H20).
const NOTES: Array[String] = ["BUY", "SHRED"] # TR
## The sign's words (keys): the baked English, and the subtitle when translated.
const WORD_MODEM := "MODEM" # TR
const WORD_CYBER := "CYBER" # TR
const WORD_SHOP := "SHOP" # TR


## Animation pass ANIM-6 (ANIMATION_HANDOFF 4.19): on entering the Modem the neon tubes warm
## up (`modem_sign_warmup`: each tube flickers on at its own, hash-picked moments, then
## holds) and the circuit lights with CYBER SHOP last (`modem_trace`). 1 = lit (the rest
## state; reduce effects and headless stay there: T0, static).
var warm: float = 1.0
var trace: float = 1.0
var _tweens: Array[Tween] = []
## Flicker steps across the warm-up, and the brightness of an unlit tube.
const WARM_STEPS := 14
const TUBE_OFF_ALPHA := 0.12
## ANIM-R3 A7 / ANIM-R4 C5: every tube strikes within `modem_sign_strike` of the warm-up,
## flickers for `modem_sign_flicker` after it (lit at a flicker step with this chance: a
## drawing threshold, not motion), then holds.
const FLICKER_ON := 0.6
## Tube ids for the warm-up hash: the border, then each band.
const TUBE_BORDER := 0
## When CYBER SHOP lights along `trace` (it starts at this share and is lit by the next).
const TRACE_CYBER_FROM := 0.6
const TRACE_CYBER_SPAN := 0.4
## The translated subtitle's pill: its inset from the sign's foot and its padding (px).
const SUBTITLE_INSET := 18.0
const SUBTITLE_PAD := Vector2(6, 2)


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = ART_SIZE


## Warms the sign up from dark (entering the Modem).
func warm_up() -> void:
	settle()
	if Motion.live(&"modem_sign_warmup"):
		var e := Motion.entry(&"modem_sign_warmup")
		warm = 0.0
		var tw := create_tween()
		tw.tween_method(func(v: float) -> void:
			warm = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(&"modem_sign_warmup")).set_delay(Motion.delay_of(&"modem_sign_warmup")).set_ease(e.ease).set_trans(e.trans)
		_tweens.append(tw)
	if Motion.live(&"modem_trace"):
		var te := Motion.entry(&"modem_trace")
		trace = 0.0
		var tt := create_tween()
		tt.tween_method(func(v: float) -> void:
			trace = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(&"modem_trace")).set_delay(Motion.delay_of(&"modem_trace")).set_ease(te.ease).set_trans(te.trans)
		_tweens.append(tt)
	queue_redraw()


## Ends the warm-up at once (lit).
func settle() -> void:
	for tw in _tweens:
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	warm = 1.0
	trace = 1.0
	queue_redraw()


## True while the sign is still warming up.
func warming() -> bool:
	return warm < 1.0 or trace < 1.0


## A tube's brightness now: lit once warm, else flickering on at hash-picked steps.
## ANIM-R3 A7: each tube strikes at its own hash-picked moment in the first
## strike_share() of the warm-up, flickers for flicker_share(), then holds lit, so the sign is
## whole well before the warm-up ends (a still mid-way showed one lit letter: it read as
## broken).
func tube(id: int) -> float:
	if warm >= 1.0:
		return 1.0
	var strike := float(absi(hash([id, 41])) % 1000) / 1000.0 * strike_share()
	if warm < strike:
		return TUBE_OFF_ALPHA
	if warm >= strike + flicker_share():
		return 1.0
	var step := floori(warm * WARM_STEPS)
	var h := float(absi(hash([id, step, 43])) % 1000) / 1000.0
	return 1.0 if h < FLICKER_ON else TUBE_OFF_ALPHA


## `col` at brightness `k` (1 = lit; an unlit tube is the colour darkened).
static func _tube_color(col: Color, k: float) -> Color:
	return col if k >= 1.0 else col.darkened(1.0 - k)


## The rect the art is drawn in (its aspect kept, centred, as large as the control allows).
func art_rect() -> Rect2:
	var k := minf(size.x / ART_SIZE.x, size.y / ART_SIZE.y) if size.x > 0.0 and size.y > 0.0 else 1.0
	var sz := ART_SIZE * k
	return Rect2((size - sz) * 0.5, sz)


## Band `i`'s brightness now: its tube's warm-up, and CYBER SHOP (the last) waits for the
## circuit trace too. High contrast (§12) shows the sign lit and whole.
func band_light(i: int) -> float:
	if Settings.high_contrast:
		return 1.0
	var k := tube(i + 1)
	if i == BANDS.size() - 1 and trace < 1.0:
		k = minf(k, lerpf(TUBE_OFF_ALPHA, 1.0, clampf((trace - TRACE_CYBER_FROM) / TRACE_CYBER_SPAN, 0.0, 1.0)))
	return k


func _draw() -> void:
	var r := art_rect()
	var k := r.size.x / ART_SIZE.x
	var tex_scale := Vector2(ART.get_width(), ART.get_height()) / ART_SIZE
	for i in BANDS.size():
		var top := BANDS[i]
		var bottom := BANDS[i + 1] if i + 1 < BANDS.size() else ART_SIZE.y
		var src := Rect2(Vector2(0, top) * tex_scale, Vector2(ART_SIZE.x, bottom - top) * tex_scale)
		var dst := Rect2(r.position + Vector2(0, top * k), Vector2(r.size.x, (bottom - top) * k))
		var light := band_light(i)
		draw_texture_rect_region(ART, dst, src, _tube_color(Color.WHITE, light))
	var sub := subtitle()
	if sub != "":
		# §10.6: the baked words in the player's language, on a dark pill at the sign's foot.
		var f := Palette.mono()
		var fs := UiTheme.font_px(UiTheme.CAPTION)
		var w := minf(f.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, r.size.x - SUBTITLE_PAD.x * 4.0)
		var h := f.get_height(fs)
		var at := Vector2(r.position.x + (r.size.x - w) * 0.5, r.end.y - SUBTITLE_INSET * k - h)
		draw_rect(Rect2(at - SUBTITLE_PAD, Vector2(w, h) + SUBTITLE_PAD * 2.0), HighContrast.BG if Settings.high_contrast else Palette.TERMINAL_BG)
		draw_string(f, at + Vector2(0, f.get_ascent(fs)), sub, HORIZONTAL_ALIGNMENT_CENTER, w, fs, Palette.TEXT_HI)


## §10.6: the translated subtitle under the baked sign ("" when the player's language says
## MODEM / CYBER SHOP as the art does).
func subtitle() -> String:
	var m := tr(WORD_MODEM)
	var c := tr(WORD_CYBER)
	var s := tr(WORD_SHOP)
	if m == WORD_MODEM and c == WORD_CYBER and s == WORD_SHOP:
		return ""
	return "%s // %s %s" % [m, c, s]


## The sign's words as the player reads them (the translated subtitle's words; tests).
func shown_words() -> PackedStringArray:
	return PackedStringArray([tr(WORD_MODEM), tr(WORD_CYBER), tr(WORD_SHOP)])


## True: the sign's words are baked art, not live text (ART_BIBLE §4.3 rule 5; tests).
func is_baked() -> bool:
	return ART != null


## ANIM-R4 C5: each tube strikes within this share of the warm-up (`modem_sign_strike`).
static func strike_share() -> float:
	return clampf(Motion.amplitude(&"modem_sign_strike"), 0.0, 1.0)


## ANIM-R4 C5: a struck tube flickers for this share of the warm-up (`modem_sign_flicker`).
static func flicker_share() -> float:
	return clampf(Motion.amplitude(&"modem_sign_flicker"), 0.0, 1.0)
