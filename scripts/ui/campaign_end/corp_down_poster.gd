class_name CorpDownPoster
extends Control
## M14 parity END-03 (designer group ruling 2026-10-05: the campaign won keeps the M13 build's
## celebration beat, the CORP DOWN poster, reworked in the v2 language). Ported from
## art-m13-final `scripts/ui/kit/campaign_end_stage.gd` + `corp_fall_art.gd` (5c077bc1): the
## target corporation's billboard crossed out, CORP DOWN slammed across its foot. In v2 (ART_BIBLE
## v2 §1.2; spray paint is a rejected medium) the pieces are:
## - the corporation's own notice in its house style, the ransom notice's language turned on its
##   owner (CorpHouseStyle: house back, its motif `assets/campaign_end/motif_*.png`, the header bar
##   in the house hue, its seal `CorpSeal` with the round 20 emblem, the boss's name and division);
## - the Cell's red grease pencil X over it (GreasePencilMark, THREAT ink: the threat struck out,
##   true to the rules: the corporation's boss is offline), written on in writing order;
## - CORP DOWN as the Cell's vinyl sticker (VinylSticker, yellow: the Cell's own word) slapped
##   half over the poster's foot, clear of the pencil (no UI covers grease pencil, §1.2).
## The dossier drives the beat (`apply`, `slap_sticker`); at rest it is the end state. Look only.

## The poster's size at text scale 1.0 (px) and the most it grows with the text.
const SIZE := Vector2(288, 126)
const GROW_MAX := 1.3
## The header bar's height, the inner pad, the seal's radius share of the body's height, the
## pencil X's inset from the body's corners and the tape's size (px at 1.0).
const BAR_H := 18.0
const PAD := 10.0
const SEAL_SHARE := 0.4
const X_INSET := 8.0
const TAPE := Vector2(64, 16)
const TAPE_TILT := 32.0
## How far in from the corner a tape strip sits (share of its length).
const TAPE_IN := 0.35
## Room under the paper for the sticker's hang (px at 1.0).
const HANG_ROOM := 34.0
## The motif's strength under the seal (the ransom notice's `motif_strength`).
const MOTIF_ALPHA := 0.3
## The share of the body (from its top) the boss's words keep to: the sticker hangs over the rest.
const WORDS_SHARE := 0.66
## The sticker's lettering step, tilt (degrees) and how far its body hangs below the poster's
## foot (share of its height).
const STICKER_STEP := UiTheme.TITLE
const STICKER_TILT := -5.0
const STICKER_HANG := 0.5
## The sticker's jitter seed (the same poster, the same sticker).
const STICKER_SEED := 7

var style: CorpHouseStyle = null
## The house name and the boss as printed (translated).
var house_shown: String = ""
var boss_name: String = ""
var pencil: GreasePencilMark = null
var sticker: VinylSticker = null
## The beat (0..1): the poster's slap in, the pencil's written share.
var in_t: float = 1.0
var write_t: float = 1.0
var _motif_tex: Texture2D = null


func _init(corporation_id: StringName = &"", display_name: String = "", p_boss_name: String = "") -> void:
	name = "CorpDownPoster"
	style = CorpHouseStyle.of(corporation_id)
	house_shown = style.name_shown(display_name)
	boss_name = p_boss_name
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	# Its room in the layout: the paper and the sticker's hang under it (it never covers the
	# sheet below).
	custom_minimum_size = poster_size() + Vector2(0, HANG_ROOM * _k())
	size = custom_minimum_size
	_motif_tex = load(RansomLock.MOTIF_ART % RansomLock.MOTIF_NAMES[clampi(style.motif, 0, RansomLock.MOTIF_NAMES.size() - 1)]) as Texture2D
	pencil = GreasePencilMark.new()
	pencil.name = "PencilX"
	pencil.ink = GreasePencilMark.Ink.THREAT
	pencil.auto_write = false  # the file's beat drives its write (END-03); the wax is the kit's one width (B1b)
	add_child(pencil)
	sticker = VinylSticker.new()
	sticker.name = "CorpDown"
	sticker.text = tr("CORP DOWN")
	sticker.fill = VinylSticker.Fill.YELLOW
	# It grows with the text as far as the poster does (GROW_MAX).
	sticker.font_step = roundi(STICKER_STEP * minf(1.0, GROW_MAX / maxf(Settings.text_scale, 0.01)))
	sticker.tilt_deg = STICKER_TILT
	sticker.seed = STICKER_SEED
	sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sticker)
	resized.connect(_place)
	sticker.resized.connect(_place)
	_place()


## The poster's size at the player's text size (px).
static func poster_size() -> Vector2:
	return (SIZE * minf(Settings.text_scale, GROW_MAX)).round()


func _k() -> float:
	return minf(Settings.text_scale, GROW_MAX)


## The poster's paper (local px; the sticker's hang lies under it).
func paper_rect() -> Rect2:
	return Rect2(Vector2.ZERO, poster_size())


## The poster's body under the header bar (local px): the seal, the words and the pencil X.
func body_rect() -> Rect2:
	var bar := BAR_H * _k()
	var p := paper_rect()
	return Rect2(Vector2(0, bar), Vector2(p.size.x, p.size.y - bar))


func _place() -> void:
	pivot_offset = size * 0.5
	var k := _k()
	var p := paper_rect()
	var b := body_rect()
	var inset := X_INSET * k
	# The X strikes the corporation out (its seal and its boss) above the sticker's hang: no UI
	# covers grease pencil.
	var x_box := Rect2(b.position, Vector2(b.size.x, b.size.y * WORDS_SHARE)).grow(-inset)
	pencil.clear()
	pencil.add_stroke(PackedVector2Array([x_box.position, x_box.end]))
	pencil.add_stroke(PackedVector2Array([Vector2(x_box.end.x, x_box.position.y), Vector2(x_box.position.x, x_box.end.y)]))
	pencil.progress = write_t
	# Half over the foot, centred: the X's legs are in the corners there.
	var body := sticker.body_rect.size
	sticker.pivot_offset = sticker.body_rect.position + body * 0.5
	sticker.place_center(Vector2(p.size.x * 0.5, p.size.y + body.y * (STICKER_HANG - 0.5)))
	queue_redraw()


## Sets the beat: the poster `p_in` of the way through its slap (scale from `amplitude`), the
## pencil `p_write` written. The sticker slaps on with `slap_sticker`.
func apply(p_in: float, p_write: float, amplitude: float) -> void:
	in_t = clampf(p_in, 0.0, 1.0)
	write_t = clampf(p_write, 0.0, 1.0)
	# Unseen (never hidden: the row keeps its room, the prints never shift) until it lands.
	modulate.a = minf(1.0, in_t * 2.0)
	scale = Vector2.ONE * (lerpf(amplitude, 1.0, ease(in_t, 0.4)) if amplitude > 0.0 else 1.0)
	pencil.progress = write_t


## The sticker before its slap (hidden) or slapped on (`sticker_slap`; at rest at once when that
## motion does not play). Returns the slap's seconds.
func slap_sticker() -> float:
	return sticker.slap()


## Hides the sticker until its slap.
func hold_sticker() -> void:
	sticker.visible = false


## The sticker at rest on the poster (a skip, reduce effects).
func sticker_at_rest() -> void:
	if sticker.motion_running():
		sticker.complete_motion()
	sticker.visible = true
	sticker.scale = Vector2.ONE
	sticker.rotation_degrees = sticker.tilt_deg
	sticker.modulate.a = 1.0


func _draw() -> void:
	var k := _k()
	var r := paper_rect()
	draw_rect(Rect2(r.position + DossierPhoto.SHADOW_OFFSET * k, r.size), Palette.SHADOW)
	draw_rect(r, style.back())
	var b := body_rect()
	if _motif_tex != null:
		draw_texture_rect(_motif_tex, b, false, Color(style.color(), MOTIF_ALPHA))
	# The header bar: the house, in its hue.
	var bar := Rect2(Vector2.ZERO, Vector2(r.size.x, b.position.y))
	draw_rect(bar, style.color())
	var mono := Palette.mono()
	var fs := UiTheme.font_px_at(UiTheme.CAPTION, k)  # it grows as far as the poster does
	draw_string(mono, Vector2(PAD * k, (bar.size.y + mono.get_ascent(fs) - mono.get_descent(fs)) * 0.5), house_shown.to_upper(),
		HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD * 2.0 * k, fs, style.back())
	# The seal on the left, the boss's name and the house's division beside it.
	var rad := b.size.y * SEAL_SHARE
	var c := Vector2(PAD * k + rad, b.position.y + b.size.y * 0.5)
	CorpSeal.draw_seal(self, c, rad, style.corp_id, style.color(), house_shown)
	var x := c.x + rad + PAD * k
	var room := r.size.x - x - PAD * k
	var head := style.head_font()
	var hs := UiTheme.font_px_at(UiTheme.LABEL, k)
	# The boss's name and the house's division, whole words, centred on the seal's line (above
	# the sticker's hang).
	var lines := HeatPoster.wrap_words(head, boss_name.to_upper(), hs, room)
	var div := HeatPoster.wrap_words(mono, tr(style.division), fs, room)
	var block := lines.size() * head.get_height(hs) + div.size() * mono.get_height(fs)
	var y := b.position.y + PAD * k + maxf(0.0, (b.size.y * WORDS_SHARE - PAD * k - block) * 0.5) + head.get_ascent(hs)
	for line in lines:
		draw_string(head, Vector2(x, y), line, HORIZONTAL_ALIGNMENT_LEFT, room, hs, Palette.END_HOUSE_TEXT)
		y += head.get_height(hs)
	y += mono.get_ascent(fs) - head.get_ascent(hs)
	for line in div:
		draw_string(mono, Vector2(x, y), line, HORIZONTAL_ALIGNMENT_LEFT, room, fs, style.color())
		y += mono.get_height(fs)
	draw_rect(r, style.color(), false, maxf(1.0, 2.0 * k))
	# Taped to the folder at its top corners.
	var t := TAPE * k
	for side in [-1.0, 1.0]:
		var at := Vector2(r.size.x * 0.5 + side * (r.size.x * 0.5 - t.x * TAPE_IN), 0.0)
		draw_set_transform(at, deg_to_rad(side * TAPE_TILT), Vector2.ONE)
		draw_rect(Rect2(-t * 0.5, t), PaperInk.opaque(Palette.TAPE, Palette.PAPER))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
