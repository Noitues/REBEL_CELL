class_name SiteMarker
extends RefCounted
## ART-5 5d: the City Grid's Site marker v4 (ART_BIBLE v2 §4.5, round 42
## `site_markers_v4.png`, ported from `markers42.py` on tag art-concepts-r43). One marker,
## five layers, each answering one question:
##   pad (raid socket)  OWNERSHIP   corporate dark pad + corp pins; claimed lime; cleared grey;
##                                  TAKEN red pins (a raid entry point)
##   icon disc          KIND        corp crest; Exploit = gold key plate + type sub-badge (INTEL
##                                  magnifier, BREACH sledgehammer, VIRUS); Heat objective =
##                                  dark-orange flame; claimed = lime fist (thumb tucked); CORE
##                                  = lime heart. The disc is a vinyl node sticker
##                                  (SiteMarkerView) holding the concept's own disc art
## M14 asset parity: every part (disc art, pad, slip, check badge, bolt) is a texture exported
## by round 42's generator (`assets/city/grid_markers/manifest.json`); the ring and pips stay
## procedural (their width, glow and grey follow the zoom and state).
##   ring               AVAILABILITY white = not yet, orange = selectable, lime = yours/visited
##   pips (1-3 squares) TIER        gold on Exploit Sites; the boss (T4) has none
##   corner badge       STATUS      CLEARED grey check (PATROL on hover)
## DOWN (a claimed node at 0 integrity): the whole marker greys and a white bolt lies across
## it (ruling 11: the raid view uses the same bolt, `draw_bolt`). TAKEN: an intercepted corp
## SEIZURE NOTICE slip replaces the disc, its pips in violet. The boss is the HQ itself with
## the red pencil TARGET circle and the `CENTRAL SERVER // EXPLOITS n/3` chip.
##
## Pure maths and drawing on any CanvasItem; `spec_for` is a pure function of the campaign
## state (no Node), so the marker reads the same on the Grid, its key and the tests. A view:
## it never changes game state. Sizes are screen px at the Grid zoom (`k` scales them).

## Kinds (the disc).
const KIND_SITE := "site"
const KIND_EXPLOIT := "exploit"
const KIND_HEAT := "heat"
const KIND_CORE := "core"
const KIND_CENTRAL_SERVER := "central_server"
## Statuses (pad, badge, slip, bolt).
const ST_CORPORATE := "corporate"
const ST_CLEARED := "cleared"
const ST_CLAIMED := "claimed"
const ST_DOWN := "down"
const ST_TAKEN := "taken"
## Availability (the ring).
const AV_NOT_YET := "notyet"
const AV_NEXT := "next"
const AV_YOURS := "yours"

## Disc diameter (an Exploit's is larger), the not-yet shrink, the ring's gap and widths.
const DISC_PX := 30.0
const DISC_EXPLOIT_PX := 34.0
const NOT_YET_SCALE := 0.85
const RING_GAP := 5.0
const RING_W := 4.0
const RING_W_NOT_YET := 3.0
## The ring's soft glow: its width over the ring's, and its alpha by availability.
const RING_GLOW_W := 3.0
const RING_GLOW_NEXT := 0.35
const RING_GLOW_YOURS := 0.22
## The pad (a diamond at the Site's street point) and how far under the disc it sits when
## a marker is drawn on its own (the key); on the map it sits on the Site's roof.
const PAD_R := 17.0
const PAD_R_NOT_YET := 14.0
const PAD_DROP := 15.0
## M14 asset parity: every marker part is the round 42 generator's own drawing
## (`tools/art_pipeline/parity/export_grid_markers.py`, manifest in ART_DIR), at 2x. The pad
## textures are square canvases with the pad's half-width this share of their side.
const ART_DIR := "res://assets/city/grid_markers/"
const ART_X := 2.0
const PAD_TEX_SHARE := 34.0 / 148.0
## The crests of the corps the round 42 sheet does not draw (it shows Meridian's crane-A):
## ART-2 2A's crest masks from the concept recipes (round 15 / round 40), and their size on a
## disc (share of its radius).
const CREST_DIR := "res://assets/wheel/glyphs_interim/crest_%s.png"
const CREST_SHARE := 1.1
## The SEIZURE NOTICE slip's letterhead mark (the concept draws Meridian's crane-A there):
## its centre (shares of the slip's size from its centre, before the slip's tilt), the patch
## that covers it for another corp's crest (shares of the slip's size), the crest's size (share
## of the slip's height) and the slip's own tilt (the concept's rotate_rgba(-8): 8 degrees
## clockwise on screen).
const SLIP_MARK_AT := Vector2(0.0, -0.38)
const SLIP_MARK_PATCH := Vector2(0.5, 0.2)
const SLIP_MARK_SIZE := 0.17
const SLIP_ART_TILT_DEG := 8.0
## Tier pips: square side, gap, and their top under the disc's edge.
const PIP_S := 5.0
const PIP_GAP := 3.0
const PIP_DROP := 9.0
## The corner badge's radius and inset from the disc's top-right.
const BADGE_R := 9.0
const BADGE_INSET := 2.0
## The DOWN bolt reaches this far past the disc's edge, and is this many times that across;
## its ink shadow's offset (the concept's (2, 3)).
const BOLT_REACH := 9.0
const BOLT_SPAN := 2.1
const BOLT_SHADOW := Vector2(2, 3)
## The SEIZURE NOTICE slip: its paper's size over 1.25 x the disc (the concept's
## seizure_memo(px * 1.25): 0.86 x 1.05 of that).
const SLIP_SCALE := 1.25
const SLIP_W := 0.86
const SLIP_H := 1.05
## Greying (DOWN, cleared disc): the share toward grey.
const GREY_SHARE := 0.75
## The disc fill: how much of its kind's colour tints the night ink.
const DISC_TINT := 0.18
## Fight won (D17): the share of a won Site's lit windows in lime (the rest Cell pink).
const WON_LIME_SHARE := 0.3

## What each kind and status is, in plain words (the Grid's key and the tooltips; v4 "WHAT
## EACH ICON MEANS IN THE GAME", written from the rules).
const MEANINGS := {
	"next": "Orange ring: a corporate Site you can run now. Clear it, then claim it to grow your network.", # TR
	"notyet": "White ring: not reachable yet. Clear a linked Site first.", # TR
	"cleared": "Grey + check: cleared, used up and not claimed. You can still patrol it for loot, Heat and Rank.", # TR
	"yours": "Lime fist: your node, a claimed Site. Raids attack these; runs start from them.", # TR
	"down": "White bolt: DOWN, your node hit 0 integrity. No bonus and no power to its links until you repair it.", # TR
	"taken": "Seizure notice: TAKEN, the corporation took the Site back. Run a Reclaim (one fight) to retake it; it is a raid entry point.", # TR
	"exploit": "Gold key: an Exploit Site (always T2). It holds one Exploit; you need 3 to breach the Central Server. Point at it for the Exploit.", # TR
	"heat": "Flame: a Heat objective Site. Clearing it lowers Heat.", # TR
	"core": "Heart: CORE, your home server. If its integrity reaches 0 you lose the campaign.", # TR
	"pips": "Pips: the Site's tier, 1 to 3 (harder runs, better rewards). Gold pips: an Exploit Site.", # TR
	"target": "TARGET: the Central Server, the boss fight. The chip counts your Exploits.", # TR
	"locked": "Padlock: a locked link. An Intel Exploit or an objective opens it.", # TR
	"depowered": "Grey broken link: no power flows to a TAKEN or DOWN node.", # TR
}
## The chip over the boss (TARGET).
const BOSS_CHIP := "CENTRAL SERVER // EXPLOITS %d/%d" # TR
## A cleared Site's hover word (v4 "PATROL on hover").
const PATROL_TIP := "PATROL: loot, Heat and Rank, no objective." # TR


# --- State (pure) -----------------------------------------------------------------------

## The marker of Site `sd` in campaign `c` (corp `corp_id`): {kind, status, avail, tier,
## exploit (RC.ExploitType), corp, pinned, won}. `selectable` = a run can launch there now
## (CampaignRules.launchable_sites / patrol). Pure: the same state, the same marker.
static func spec_for(c: CampaignState, corp_id: StringName, sd: SiteData, selectable: bool) -> Dictionary:
	var kind := KIND_SITE
	if sd.id == c.grid.home_site_id:
		kind = KIND_CORE
	else:
		match CampaignRules.site_objective(c, sd):
			RC.SiteObjective.EXPLOIT:
				kind = KIND_EXPLOIT
			RC.SiteObjective.HEAT_REDUCTION:
				kind = KIND_HEAT
			RC.SiteObjective.CENTRAL_SERVER:
				kind = KIND_CENTRAL_SERVER
	var status := ST_CORPORATE
	match c.grid.status_of(sd.id):
		GridState.SiteStatus.CLEARED:
			status = ST_CLEARED
		GridState.SiteStatus.CLAIMED:
			status = ST_DOWN if int(c.grid.site(sd.id).get("condition", GridState.Condition.OK)) == GridState.Condition.DOWN else ST_CLAIMED
		GridState.SiteStatus.TAKEN:
			status = ST_TAKEN
	var avail := AV_NEXT if selectable else AV_NOT_YET
	if status == ST_CLEARED or status == ST_CLAIMED or status == ST_DOWN or kind == KIND_CORE:
		avail = AV_YOURS
	var pinned := kind != KIND_SITE or status != ST_CORPORATE or selectable
	return {"kind": kind, "status": status, "avail": avail, "tier": 0 if kind == KIND_CORE or kind == KIND_CENTRAL_SERVER else sd.tier,
		"exploit": int(sd.exploit_type) if kind == KIND_EXPLOIT else int(RC.ExploitType.NONE), "corp": corp_id,
		"pinned": pinned, "won": status == ST_CLEARED or status == ST_CLAIMED}


## The legend row key a marker reads as ("next", "notyet", "cleared", "yours", "down",
## "taken", "exploit", "heat", "core", "target").
static func meaning_key(spec: Dictionary) -> String:
	match String(spec.get("status", ST_CORPORATE)):
		ST_DOWN:
			return "down"
		ST_TAKEN:
			return "taken"
		ST_CLAIMED:
			return "core" if spec.get("kind") == KIND_CORE else "yours"
		ST_CLEARED:
			return "cleared"
	match String(spec.get("kind", KIND_SITE)):
		KIND_EXPLOIT:
			return "exploit"
		KIND_HEAT:
			return "heat"
		KIND_CORE:
			return "core"
		KIND_CENTRAL_SERVER:
			return "target"
	return "next" if spec.get("avail") == AV_NEXT else "notyet"


## What tells marker `spec` apart with no colour (greyscale, bible §5.1 "never colour
## alone"): its disc art, its status layer (check, bolt, slip), its size and its ring's tone.
static func grey_key(spec: Dictionary) -> String:
	var st := String(spec.get("status", ST_CORPORATE))
	var art := String(spec.get("kind", KIND_SITE))
	if (st == ST_CLAIMED or st == ST_DOWN) and art != KIND_CORE:
		art = "fist"
	var layer := String({ST_CLEARED: "check", ST_DOWN: "bolt", ST_TAKEN: "slip"}.get(st, "none"))
	var small: bool = spec.get("avail") == AV_NOT_YET
	var tone := -1.0 if st == ST_TAKEN or art == KIND_CENTRAL_SERVER else snappedf(ring_color(spec).get_luminance(), GREY_TONE_STEP)
	return "%s|%s|%s|%.2f" % [art, layer, "small" if small else "full", tone]

## Ring tones closer than this read the same in grey.
const GREY_TONE_STEP := 0.2


## The plain-language meaning of `key` (MEANINGS), translated once.
static func meaning(key: String) -> String:
	return CityMapOverlay.tr_word(String(MEANINGS.get(key, "")))


## The Exploit tag a T2 Site's hover shows: {category: "BREACH", name: "CUSTOMS OVERRIDE
## KEYS", effect: what it does at the breach} from corporation `corp`'s ExploitData of
## `type` (translated); empty when the corp has none of that type.
static func exploit_tag(corp: CorporationData, type: int) -> Dictionary:
	if corp == null or type == RC.ExploitType.NONE:
		return {}
	for e in corp.exploits:
		if e != null and int(e.exploit_type) == type:
			var full := TextDb.t(e, "display_name")
			var category := CityMapOverlay.tr_word(String(RC.ExploitType.keys()[type])).to_upper()
			var item := full.get_slice(": ", 1) if full.contains(": ") else full
			return {"category": category, "name": item.to_upper(), "effect": TextDb.t(e, "description")}
	return {}


# --- Geometry ---------------------------------------------------------------------------

## The disc's diameter (px at k = 1 and the given scale).
static func disc_px(spec: Dictionary) -> float:
	var d := DISC_EXPLOIT_PX if spec.get("kind") == KIND_EXPLOIT else DISC_PX
	return d * (NOT_YET_SCALE if spec.get("avail") == AV_NOT_YET else 1.0)


## The ring's radius round the disc (px x k).
static func ring_radius(spec: Dictionary, k: float = 1.0) -> float:
	return (disc_px(spec) * 0.5 + RING_GAP) * k


## How far from the disc's centre a pointer still picks the marker (px x k).
static func hit_radius(spec: Dictionary, k: float = 1.0) -> float:
	if spec.get("status") == ST_TAKEN:
		return disc_px(spec) * SLIP_SCALE * SLIP_H * 0.5 * k
	return ring_radius(spec, k) + RING_W * 0.5 * k


## The rect the marker covers round disc centre `c` (ring, badge, pips or slip), px x k.
static func box(spec: Dictionary, c: Vector2, k: float = 1.0) -> Rect2:
	var d := disc_px(spec) * k
	var r := ring_radius(spec, k) + RING_W * k
	var out := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	if spec.get("status") == ST_TAKEN:
		var slip := slip_size(spec) * k
		var half := maxf(slip.x, slip.y) * 0.5
		out = Rect2(c - Vector2(half, half), Vector2(half, half) * 2.0)
	if spec.get("status") == ST_CLEARED:
		var b := c + Vector2(d * 0.5 + BADGE_INSET * k, -d * 0.5 + BADGE_INSET * k)
		out = out.merge(Rect2(b - Vector2(BADGE_R, BADGE_R) * k, Vector2(BADGE_R, BADGE_R) * 2.0 * k))
	if spec.get("status") == ST_DOWN:
		var reach := (d * 0.5 + BOLT_REACH * k) * BOLT_SPAN * 0.5
		out = out.merge(Rect2(c - Vector2(reach, reach), Vector2(reach, reach) * 2.0))
	var n := pip_count(spec)
	if n > 0:
		out = out.merge(pips_rect(spec, c, k))
	return out


## The number of tier pips the marker shows (none on claimed, DOWN, CORE or the boss).
static func pip_count(spec: Dictionary) -> int:
	var st := String(spec.get("status", ST_CORPORATE))
	if st == ST_CLAIMED or st == ST_DOWN:
		return 0
	return clampi(int(spec.get("tier", 0)), 0, CityMapOverlay.TIER_PIPS_MAX)


## Where the pips sit under disc centre `c` (px x k).
static func pips_rect(spec: Dictionary, c: Vector2, k: float = 1.0) -> Rect2:
	var n := pip_count(spec)
	var w := (n * PIP_S + maxi(0, n - 1) * PIP_GAP) * k
	var top := c.y + disc_px(spec) * 0.5 * k + PIP_DROP * k
	if spec.get("status") == ST_TAKEN:
		top = c.y + slip_size(spec).y * 0.5 * k + PIP_GAP * k
	return Rect2(c.x - w * 0.5, top, w, PIP_S * k)


## The SEIZURE NOTICE slip's size (px at k = 1, before its tilt).
static func slip_size(spec: Dictionary) -> Vector2:
	var px := disc_px(spec) * SLIP_SCALE
	return Vector2(px * SLIP_W, px * SLIP_H)


# --- Colours ----------------------------------------------------------------------------

## The ring's colour (availability; lime once yours or visited).
static func ring_color(spec: Dictionary) -> Color:
	match String(spec.get("avail", AV_NOT_YET)):
		AV_NEXT:
			return Palette.RING_AVAILABLE
		AV_YOURS:
			return Palette.CELL_ACID
	return Palette.RING_UNAVAILABLE


## The pad's pin colour (ownership).
static func pad_color(spec: Dictionary) -> Color:
	match String(spec.get("status", ST_CORPORATE)):
		ST_CLAIMED, ST_DOWN:
			return Palette.CELL_ACID
		ST_CLEARED:
			return Palette.RING_CUT
		ST_TAKEN:
			return Palette.HARM
	return Palette.corp_color(StringName(spec.get("corp", &"")))


## The colour of the disc's art (crest, key, flame, fist, heart).
static func art_color(spec: Dictionary) -> Color:
	match String(spec.get("status", ST_CORPORATE)):
		ST_CLAIMED, ST_DOWN:
			return Palette.CELL_ACID
	match String(spec.get("kind", KIND_SITE)):
		KIND_EXPLOIT:
			return Palette.RESIST_GOLD
		KIND_HEAT:
			return Palette.HEAT_FLAGGED
		KIND_CORE:
			return Palette.CELL_ACID
	return Palette.corp_color(StringName(spec.get("corp", &"")))


## The disc's fill: night ink tinted by the kind's colour.
static func disc_fill(spec: Dictionary) -> Color:
	var tint := Palette.HEAT_B if spec.get("kind") == KIND_HEAT and spec.get("status") == ST_CORPORATE else art_color(spec)
	return Palette.NIGHT_SKY.lerp(tint, DISC_TINT)


## `col` greyed (DOWN: the whole marker; cleared: the disc).
static func greyed(col: Color) -> Color:
	var g := col.get_luminance()
	return col.lerp(Color(Palette.TEXT_MID, col.a).darkened(1.0 - g), GREY_SHARE)


# --- Drawing ----------------------------------------------------------------------------

## A marker part's texture (`name` without extension, ART_DIR), loaded once.
static func art(name: String) -> Texture2D:
	if not _art_cache.has(name):
		_art_cache[name] = load(ART_DIR + name + ".png") as Texture2D
	return _art_cache[name]


## Corp `corp_id`'s crest mask (white; CREST_DIR), loaded once; null for an unknown corp.
static func crest(corp_id: StringName) -> Texture2D:
	var path := CREST_DIR % String(corp_id)
	if not _art_cache.has(path):
		_art_cache[path] = load(path) as Texture2D if ResourceLoader.exists(path) else null
	return _art_cache[path]


static var _art_cache: Dictionary = {}


## The disc art `spec` shows (a texture name in ART_DIR), or "" for another corp's regular
## Site (the concept's plain disc with that corp's crest, `draw_art`).
static func disc_art(spec: Dictionary) -> String:
	var cleared := "_cleared" if spec.get("status") == ST_CLEARED else ""
	match String(spec.get("status", ST_CORPORATE)):
		ST_CLAIMED, ST_DOWN:
			return "disc_core" if spec.get("kind") == KIND_CORE else "disc_claimed"
	match String(spec.get("kind", KIND_SITE)):
		KIND_CORE:
			return "disc_core"
		KIND_EXPLOIT:
			var type := int(spec.get("exploit", RC.ExploitType.NONE))
			var sub := "" if type == RC.ExploitType.NONE else "_" + String(RC.ExploitType.keys()[type]).to_lower()
			return "disc_exploit" + sub + cleared
		KIND_HEAT:
			return "disc_heat" + cleared
	if StringName(spec.get("corp", &"")) == &"meridian":
		return "disc_site_meridian" + cleared
	return ""


## The pad texture's name for `spec` (OWNERSHIP).
static func pad_art(spec: Dictionary) -> String:
	match String(spec.get("status", ST_CORPORATE)):
		ST_CLAIMED:
			return "pad_claimed"
		ST_DOWN:
			return "pad_down"
		ST_CLEARED:
			return "pad_cleared"
		ST_TAKEN:
			return "pad_taken"
	var corp := String(spec.get("corp", &""))
	return "pad_corporate_" + (corp if ResourceLoader.exists(ART_DIR + "pad_corporate_" + corp + ".png") else "meridian")


## The pad (raid socket) at street point `at`: the concept's circuit-inlay diamond in its
## ownership colour (round 42 `pad`).
static func draw_pad(ci: CanvasItem, spec: Dictionary, at: Vector2, k: float = 1.0) -> void:
	var r := (PAD_R_NOT_YET if spec.get("avail") == AV_NOT_YET else PAD_R) * k
	var t := art(pad_art(spec))
	var side := r / PAD_TEX_SHARE
	ci.draw_texture_rect(t, Rect2(at - Vector2(side, side) * 0.5, Vector2(side, side)), false)


## Everything of the marker but its disc (the vinyl sticker), round disc centre `c`: the
## ring, the pips, the corner badge, and the SEIZURE NOTICE slip in the disc's place.
static func draw_under(ci: CanvasItem, spec: Dictionary, c: Vector2, k: float = 1.0) -> void:
	if spec.get("kind") == KIND_CENTRAL_SERVER:
		return  # the boss is its HQ with the pencil TARGET (no disc, ring or pips)
	var down: bool = spec.get("status") == ST_DOWN
	if spec.get("status") == ST_TAKEN:
		draw_slip(ci, spec, c, k)
	else:
		# The ring stays procedural: its width, glow and greying follow the availability and the
		# zoom (the concept's `ring` is a plain glowing outline in these colours).
		var rc := ring_color(spec)
		if down:
			rc = greyed(rc)
		var rr := ring_radius(spec, k)
		var w := (RING_W_NOT_YET if spec.get("avail") == AV_NOT_YET else RING_W) * k
		var glow := RING_GLOW_NEXT if spec.get("avail") == AV_NEXT else (RING_GLOW_YOURS if spec.get("avail") == AV_YOURS else 0.0)
		if glow > 0.0 and not down:
			ci.draw_arc(c, rr, 0.0, TAU, 40, Color(rc, glow), w * RING_GLOW_W, true)
		ci.draw_arc(c + Vector2(1, 2) * k, rr, 0.0, TAU, 40, Color(Palette.GLYPH_INK, 0.9), w, true)
		ci.draw_arc(c, rr, 0.0, TAU, 40, rc, w, true)
	var n := pip_count(spec)
	if n > 0:
		var pr := pips_rect(spec, c, k)
		var pc := ring_color(spec)
		if spec.get("kind") == KIND_EXPLOIT:
			pc = Palette.RESIST_GOLD
		elif spec.get("status") == ST_TAKEN:
			pc = Palette.NEON_VIOLET
		elif spec.get("avail") == AV_NOT_YET:
			pc = Palette.TEXT_MID
		for i in n:
			var p := Vector2(pr.position.x + i * (PIP_S + PIP_GAP) * k, pr.position.y)
			ci.draw_rect(Rect2(p - Vector2(k, k), Vector2(PIP_S + 2.0, PIP_S + 2.0) * k), Palette.GLYPH_INK)
			ci.draw_rect(Rect2(p, Vector2(PIP_S, PIP_S) * k), pc)
	if spec.get("status") == ST_CLEARED:
		var d := disc_px(spec) * k
		var b := c + Vector2(d * 0.5 + BADGE_INSET * k, -d * 0.5 + BADGE_INSET * k)
		var t := art("badge_cleared")
		var side := t.get_width() / ART_X * k
		ci.draw_texture_rect(t, Rect2(b - Vector2(side, side) * 0.5, Vector2(side, side)), false)


## The DOWN bolt across the whole marker (ruling 11; the raid view draws the same): the
## concept's `bolt_mask` in white over its ink shadow.
static func draw_bolt(ci: CanvasItem, c: Vector2, disc: float, k: float = 1.0) -> void:
	var span := (disc * 0.5 + BOLT_REACH * k) * BOLT_SPAN
	var t := art("bolt_down")
	var rect := Rect2(c - Vector2(span, span) * 0.5, Vector2(span, span))
	ci.draw_texture_rect(t, Rect2(rect.position + BOLT_SHADOW * k, rect.size), false, Palette.GLYPH_INK)
	ci.draw_texture_rect(t, rect, false)


## The SEIZURE NOTICE slip (TAKEN) round `c`: the concept's slip (pale paper, violet hatch,
## violet letterhead, typed lines, the red bar; tilted). Its letterhead carries Meridian's
## crane-A; another corp's slip gets its own crest on a letterhead patch.
static func draw_slip(ci: CanvasItem, spec: Dictionary, c: Vector2, k: float = 1.0) -> void:
	var t := art("slip_taken")
	var sz := Vector2(t.get_width(), t.get_height()) / ART_X * k
	ci.draw_texture_rect(t, Rect2(c - sz * 0.5, sz), false)
	var corp := StringName(spec.get("corp", &""))
	var ct := crest(corp)
	if corp == &"meridian" or ct == null:
		return
	var paper := slip_size(spec) * k
	ci.draw_set_transform(c, deg_to_rad(SLIP_ART_TILT_DEG))
	var at := SLIP_MARK_AT * paper.y
	var patch := paper * SLIP_MARK_PATCH
	ci.draw_rect(Rect2(at - patch * 0.5, patch), _letterhead())
	var s := paper.y * SLIP_MARK_SIZE
	ci.draw_texture_rect(ct, Rect2(at - Vector2(s, s), Vector2(s, s) * 2.0), false, Palette.corp_color(corp))
	ci.draw_set_transform(Vector2.ZERO, 0.0)


## The slip's letterhead colour, read off the concept's own slip (its band's left end).
static func _letterhead() -> Color:
	if not _art_cache.has("letterhead"):
		# Headless has no texture data: the band's violet ink then (the 5d slip's letterhead).
		var col := Palette.NEON_VIOLET.darkened(0.55)
		var img := art("slip_taken").get_image()
		if img != null and not img.is_empty():
			if img.is_compressed():
				img.decompress()
			col = img.get_pixelv(Vector2i(roundi(img.get_width() * 0.3), roundi(img.get_height() * 0.13)))
		_art_cache["letterhead"] = col
	return _art_cache["letterhead"]


## The disc's art (inside the node sticker) round `c`, radius `r` (the disc's): the concept's
## disc for its kind and status (crest, key plate with its type sub-badge, flame, fist,
## heart); another corp's regular Site is the plain disc with that corp's crest.
static func draw_art(ci: CanvasItem, spec: Dictionary, c: Vector2, r: float) -> void:
	var name := disc_art(spec)
	if name != "":
		ci.draw_texture_rect(art(name), Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0), false)
		return
	ci.draw_circle(c, r, disc_fill(spec))
	var ct := crest(StringName(spec.get("corp", &"")))
	if ct != null:
		var s := r * CREST_SHARE * 0.5
		ci.draw_texture_rect(ct, Rect2(c - Vector2(s, s), Vector2(s, s) * 2.0), false, art_color(spec))


## A locked cross-link's padlock disc at `at` (the padlock is the atlas's `state_locked`,
## drawn by the caller's glyph layer); the disc here.
static func draw_lock_disc(ci: CanvasItem, at: Vector2, r: float) -> void:
	ci.draw_circle(at, r, Palette.DESK_DARK)
	ci.draw_arc(at, r, 0.0, TAU, 24, Palette.TEXT_MID, maxf(1.0, r * 0.15), true)


## A de-powered link (to a TAKEN or DOWN node): a dim grey double trace with a break in the
## middle and two bent loose ends.
static func draw_depowered(ci: CanvasItem, pts: PackedVector2Array, k: float = 1.0) -> void:
	if pts.size() < 2:
		return
	var total := PencilShapes.length_of(pts)
	var gap := minf(total * 0.25, 12.0 * k)
	var halves: Array[PackedVector2Array] = [PencilShapes.trim(pts, 0.0, total * 0.5 - gap), PencilShapes.trim(pts, total * 0.5 + gap, total)]
	for h in halves:
		if h.size() < 2:
			continue
		for o in [-2.5, 2.5]:
			var moved := PackedVector2Array()
			for i in h.size():
				var a := h[maxi(0, i - 1)]
				var b := h[mini(h.size() - 1, i + 1)]
				var nrm := (b - a).normalized().orthogonal()
				moved.append(h[i] + nrm * o * k)
			ci.draw_polyline(moved, Color(Palette.TEXT_LO, 0.85), maxf(1.0, 2.0 * k), true)
	var a0 := halves[0][-1] if halves[0].size() > 0 else pts[0]
	var b0 := halves[1][0] if halves[1].size() > 0 else pts[-1]
	var dir := (b0 - a0).normalized()
	var nrm := dir.orthogonal()
	ci.draw_line(a0, a0 + (nrm * 9.0 + dir * 3.0) * k, Palette.TEXT_MID, maxf(1.0, 2.0 * k))
	ci.draw_line(b0, b0 - (nrm * 9.0 + dir * 3.0) * k, Palette.TEXT_MID, maxf(1.0, 2.0 * k))


## Fight won (D17): the colour of a won Site building's lit window `i` (Cell pink, some
## lime), deterministic by the Site id.
static func won_light(site_id: StringName, i: int) -> Color:
	var h := absi(hash("%s:%d" % [site_id, i]))
	return Palette.CELL_ACID if float(h % 100) / 100.0 < WON_LIME_SHARE else Palette.CELL_PINK
