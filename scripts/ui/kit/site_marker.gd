class_name SiteMarker
extends RefCounted
## ART-5 5d: the City Grid's Site marker v4 (ART_BIBLE v2 §4.5, round 42
## `site_markers_v4.png`, ported from `markers42.py` on tag art-concepts-r43). One marker,
## five layers, each answering one question:
##   pad (raid socket)  OWNERSHIP   corporate dark pad + corp pins; claimed lime; cleared grey;
##                                  TAKEN red pins (a raid entry point)
##   icon disc          KIND        corp crest; Exploit = gold keyring + type sub-badge (glyph
##                                  atlas); Heat objective = dark-orange flame; claimed = lime
##                                  fist (thumb tucked); CORE = lime heart. The disc is a vinyl
##                                  node sticker (SiteMarkerView)
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
## The pad diamond's flattening (iso) and its pins (dots on each corner).
const PAD_FLAT := 0.55
const PAD_PIN := 2.2
## Tier pips: square side, gap, and their top under the disc's edge.
const PIP_S := 5.0
const PIP_GAP := 3.0
const PIP_DROP := 9.0
## The corner badge's radius and inset from the disc's top-right.
const BADGE_R := 9.0
const BADGE_INSET := 2.0
## The Exploit type sub-badge: radius as a share of the disc's diameter (v4: 0.31), its
## centre's offset from the disc's centre (shares of the diameter).
const SUB_BADGE_SHARE := 0.31
const SUB_BADGE_AT := Vector2(0.22, 0.2)
## The DOWN bolt reaches this far past the disc's edge, and is this many times that across.
const BOLT_REACH := 9.0
const BOLT_SPAN := 2.1
## The bolt's outline (unit points of `bolt_mask`, 512 box) and its shadow's offset.
const BOLT_POINTS: Array[Vector2] = [Vector2(300, 40), Vector2(130, 290), Vector2(240, 290), Vector2(200, 470), Vector2(380, 200), Vector2(270, 200)]
const BOLT_SHADOW := Vector2(2, 3)
## The SEIZURE NOTICE slip: its size over 1.25 x the disc, its letterhead and bar shares, tilt.
const SLIP_SCALE := 1.25
const SLIP_W := 0.86
const SLIP_H := 1.05
const SLIP_HEAD := 0.24
const SLIP_BAR := Vector2(0.78, 0.94)
const SLIP_TILT_DEG := -8.0
const SLIP_LINES: Array[float] = [0.42, 0.56, 0.7]
const SLIP_HATCH_STEP := 3.0
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
	"exploit": "Gold keyring: an Exploit Site (always T2). It holds one Exploit; you need 3 to breach the Central Server. Point at it for the Exploit.", # TR
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


## The colour of the disc's art (crest, keyring, flame, fist, heart).
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

## The pad (raid socket) at street point `at`: a flat diamond, dark, with its pins.
static func draw_pad(ci: CanvasItem, spec: Dictionary, at: Vector2, k: float = 1.0) -> void:
	var r := (PAD_R_NOT_YET if spec.get("avail") == AV_NOT_YET else PAD_R) * k
	var col := pad_color(spec)
	if spec.get("status") == ST_DOWN:
		col = greyed(col)
	var q := PackedVector2Array([at + Vector2(0, -r * PAD_FLAT), at + Vector2(r, 0), at + Vector2(0, r * PAD_FLAT), at + Vector2(-r, 0)])
	ci.draw_colored_polygon(q, Color(Palette.NIGHT_SKY, 0.85))
	var closed := q.duplicate()
	closed.append(q[0])
	ci.draw_polyline(closed, Color(col, 0.75), maxf(1.0, 1.5 * k), true)
	for p in q:
		ci.draw_circle(p, PAD_PIN * k, col)


## Everything of the marker but its disc (the vinyl sticker), round disc centre `c`: the
## ring, the pips, the corner badge, and the SEIZURE NOTICE slip in the disc's place.
static func draw_under(ci: CanvasItem, spec: Dictionary, c: Vector2, k: float = 1.0) -> void:
	if spec.get("kind") == KIND_CENTRAL_SERVER:
		return  # the boss is its HQ with the pencil TARGET (no disc, ring or pips)
	var down: bool = spec.get("status") == ST_DOWN
	if spec.get("status") == ST_TAKEN:
		draw_slip(ci, spec, c, k)
	else:
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
		var r := BADGE_R * k
		ci.draw_circle(b, r, Palette.DESK_DARK)
		ci.draw_arc(b, r, 0.0, TAU, 20, Palette.TEXT_MID, maxf(1.0, 2.0 * k), true)
		ci.draw_polyline(PackedVector2Array([b + Vector2(-r * 0.5, 0), b + Vector2(-r * 0.1, r * 0.45), b + Vector2(r * 0.55, -r * 0.45)]), Palette.TEXT_HI, maxf(1.5, 3.0 * k), true)


## The DOWN bolt across the whole marker (ruling 11; the raid view draws the same).
static func draw_bolt(ci: CanvasItem, c: Vector2, disc: float, k: float = 1.0) -> void:
	var span := (disc * 0.5 + BOLT_REACH * k) * BOLT_SPAN
	var pts := PackedVector2Array()
	var shadow := PackedVector2Array()
	for p in BOLT_POINTS:
		var q := c + (p / 512.0 - Vector2(0.5, 0.5)) * span
		pts.append(q)
		shadow.append(q + BOLT_SHADOW * k)
	ci.draw_colored_polygon(shadow, Palette.GLYPH_INK)
	ci.draw_colored_polygon(pts, Palette.TEXT_HI)


## The SEIZURE NOTICE slip (TAKEN) round `c`: pale paper, violet hatch, a violet letterhead
## with the corp's crest, typed lines and the red TAKEN bar, tilted.
static func draw_slip(ci: CanvasItem, spec: Dictionary, c: Vector2, k: float = 1.0) -> void:
	var sz := slip_size(spec) * k
	var xf := Transform2D(deg_to_rad(SLIP_TILT_DEG), c)
	var half := sz * 0.5
	var rect := func(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
		return xf * PackedVector2Array([Vector2(x0, y0) - half, Vector2(x1, y0) - half, Vector2(x1, y1) - half, Vector2(x0, y1) - half])
	ci.draw_colored_polygon(xf * PackedVector2Array([-half + Vector2(2, 3) * k, Vector2(half.x, -half.y) + Vector2(2, 3) * k, half + Vector2(2, 3) * k, Vector2(-half.x, half.y) + Vector2(2, 3) * k]), Palette.SHADOW)
	ci.draw_colored_polygon(rect.call(0.0, 0.0, sz.x, sz.y), Palette.PAPER)
	var y := 0.0
	while y < sz.y:
		var a := xf * (Vector2(0, y) - half)
		var b := xf * (Vector2(sz.x, minf(sz.y, y + sz.x * 0.35)) - half)
		ci.draw_line(a, b, Color(Palette.NEON_VIOLET, 0.35), maxf(1.0, k))
		y += SLIP_HATCH_STEP * k
	ci.draw_colored_polygon(rect.call(0.0, 0.0, sz.x, sz.y * SLIP_HEAD), Palette.NEON_VIOLET.darkened(0.55))
	draw_crest(ci, StringName(spec.get("corp", &"")), xf * (Vector2(sz.x * 0.5, sz.y * SLIP_HEAD * 0.5) - half), sz.y * SLIP_HEAD * 0.42,
		Palette.corp_color(StringName(spec.get("corp", &""))), maxf(1.0, 1.5 * k))
	for t in SLIP_LINES:
		ci.draw_line(xf * (Vector2(sz.x * 0.14, sz.y * t) - half), xf * (Vector2(sz.x * 0.86, sz.y * t) - half), Palette.TEXT_LO, maxf(1.0, 1.5 * k))
	ci.draw_colored_polygon(rect.call(sz.x * 0.08, sz.y * SLIP_BAR.x, sz.x * 0.92, sz.y * SLIP_BAR.y), Palette.HARM)
	var edge: PackedVector2Array = rect.call(0.0, 0.0, sz.x, sz.y)
	edge.append(edge[0])
	ci.draw_polyline(edge, Palette.VINYL_INK, maxf(1.0, 1.5 * k), true)


## The disc's art (inside the node sticker): the kind's symbol round `c`, radius `r`
## (the disc's), in `col`. The Exploit's type sub-badge is a glyph (SiteMarkerView).
static func draw_art(ci: CanvasItem, spec: Dictionary, c: Vector2, r: float) -> void:
	var col := art_color(spec)
	var w := maxf(1.5, r * 0.14)
	match String(spec.get("status", ST_CORPORATE)):
		ST_CLAIMED, ST_DOWN:
			if spec.get("kind") == KIND_CORE:
				draw_heart(ci, c, r * 0.55, col)
			else:
				draw_fist(ci, c, r * 0.8, col)
			return
	match String(spec.get("kind", KIND_SITE)):
		KIND_CORE:
			draw_heart(ci, c, r * 0.55, col)
		KIND_EXPLOIT:
			draw_keyring(ci, c + Vector2(-r * 0.12, -r * 0.05), r * 0.62, col, w)
		KIND_HEAT:
			draw_flame(ci, c, r * 0.62, col)
		_:
			draw_crest(ci, StringName(spec.get("corp", &"")), c, r * 0.55, col, w)


## A corp's crest (bible §2.4): Meridian crane-A, Solace helix, Halcyon eye, Orbital ringed
## planet, REBEL_CELL fist.
static func draw_crest(ci: CanvasItem, corp_id: StringName, c: Vector2, r: float, col: Color, w: float) -> void:
	match String(corp_id):
		"solace":
			for s in [1.0, -1.0]:
				var pts := PackedVector2Array()
				for i in 13:
					var t := float(i) / 12.0
					pts.append(c + Vector2(sin(t * TAU) * r * 0.55 * s, (t - 0.5) * r * 2.0))
				ci.draw_polyline(pts, col, w, true)
			for i in 3:
				var y := c.y + (float(i) - 1.0) * r * 0.6
				ci.draw_line(Vector2(c.x - r * 0.3, y), Vector2(c.x + r * 0.3, y), col, maxf(1.0, w * 0.6))
		"halcyon":
			var lid := PackedVector2Array()
			for i in 25:
				var a := PI + PI * float(i) / 24.0
				lid.append(c + Vector2(cos(a) * r, sin(a) * r * 0.55))
			for i in 25:
				var a := PI * float(i) / 24.0
				lid.append(c + Vector2(cos(a) * r, sin(a) * r * 0.55))
			ci.draw_polyline(lid, col, w, true)
			ci.draw_circle(c, r * 0.32, col)
		"orbital":
			ci.draw_circle(c, r * 0.5, col)
			ci.draw_arc(c, r * 0.5, 0.0, TAU, 20, Palette.GLYPH_INK, maxf(1.0, w * 0.5), true)
			var ring := PackedVector2Array()
			for i in 33:
				var a := TAU * float(i) / 32.0
				ring.append(c + Vector2(cos(a) * r * 1.05, sin(a) * r * 0.32).rotated(-0.35))
			ci.draw_polyline(ring, col, maxf(1.0, w * 0.8), true)
		"rebel_cell":
			draw_fist(ci, c, r * 1.4, col)
		_:
			# Meridian: the crane-A (the A and the boom over it).
			var s := r
			var cc := c + Vector2(0, s * 0.15)
			ci.draw_polyline(PackedVector2Array([cc + Vector2(-s * 0.8, s * 0.7), cc + Vector2(0, -s), cc + Vector2(s * 0.8, s * 0.7)]), col, w * 1.3, true)
			ci.draw_line(cc + Vector2(-s * 0.45, s * 0.1), cc + Vector2(s * 0.45, s * 0.1), col, w)
			ci.draw_line(cc + Vector2(-s * 1.1, -s * 0.55), cc + Vector2(s * 1.2, -s * 0.75), col, w)


## The Exploit Site's keyring: a ring with three keys dangling (round 42 v2 keyring).
static func draw_keyring(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float) -> void:
	var ring_c := c + Vector2(0, -r * 0.55)
	ci.draw_arc(ring_c, r * 0.32, 0.0, TAU, 24, col, w, true)
	for ang in [-28.0, 0.0, 28.0]:
		var a := deg_to_rad(90.0 + ang)
		var dir := Vector2(cos(a), sin(a))
		var bow := ring_c + dir * r * 0.5
		var tip := ring_c + dir * r * 1.45
		ci.draw_circle(bow, r * 0.2, col)
		ci.draw_line(bow, tip, col, w)
		var nrm := Vector2(-dir.y, dir.x)
		for t in [0.8, 0.95]:
			var q := bow.lerp(tip, t)
			ci.draw_line(q, q + nrm * r * 0.22, col, w * 0.8)


## The Heat objective's flame (dark-orange outer, lighter heart).
static func draw_flame(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	var outer := PackedVector2Array()
	var inner := PackedVector2Array()
	for i in 25:
		var t := float(i) / 24.0 * TAU
		var bulge := 1.0 - 0.45 * maxf(0.0, -sin(t))
		var p := Vector2(sin(t) * r * 0.75 * bulge, -cos(t) * r)
		if i == 0 or i == 24:
			p = Vector2(0, -r * 1.25)
		outer.append(c + p + Vector2(0, r * 0.15))
		inner.append(c + p * 0.5 + Vector2(0, r * 0.45))
	ci.draw_colored_polygon(outer, Palette.HEAT_B)
	ci.draw_polyline(outer, col, maxf(1.0, r * 0.12), true)
	ci.draw_colored_polygon(inner, col)


## CORE's heart.
static func draw_heart(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 41:
		var t := TAU * float(i) / 40.0
		var x := 16.0 * pow(sin(t), 3.0)
		var y := 13.0 * cos(t) - 5.0 * cos(2.0 * t) - 2.0 * cos(3.0 * t) - cos(4.0 * t)
		pts.append(c + Vector2(x, -y) * r / 16.0)
	ci.draw_colored_polygon(pts, col)


## The rebel fist, thumb tucked (round 34 map crest, `fist_mask`): four fingers, the thumb
## folded across, the tucked-thumb line, the wrist; the detail lines cut in night ink.
static func draw_fist(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	var s := r * 2.0 / 15.6
	var at := func(u: float, v: float) -> Vector2: return c + Vector2(u, 7.1 - v) * s
	var cut := Palette.NIGHT_SKY.lerp(col, DISC_TINT)
	var lw := maxf(1.0, 0.95 * s)
	ci.draw_colored_polygon(PackedVector2Array([at.call(-3.6, 0.0), at.call(3.6, 0.0), at.call(3.6, 5.2), at.call(5.6, 5.2),
		at.call(5.6, 13.3), at.call(-5.4, 13.3), at.call(-5.4, 5.2), at.call(-3.6, 5.2)]), col)
	for f: Vector2 in [Vector2(-5.4, -2.75), Vector2(-2.75, -0.05), Vector2(-0.05, 2.75), Vector2(2.75, 5.6)]:
		var mid := (f.x + f.y) * 0.5
		var rad := (f.y - f.x) * 0.5
		ci.draw_circle(at.call(mid, 13.3), rad * s, col)
	for f: Vector2 in [Vector2(-5.4, -2.75), Vector2(-2.75, -0.05), Vector2(-0.05, 2.75)]:
		ci.draw_line(at.call(f.y + 0.12, 8.3), at.call(f.y + 0.12, 14.0), cut, lw)
	ci.draw_line(at.call(-5.4, 8.25), at.call(4.4, 8.25), cut, lw)
	ci.draw_line(at.call(4.4, 8.25), at.call(5.6, 6.33), cut, lw)
	ci.draw_line(at.call(0.4, 5.2), at.call(5.0, 5.2), cut, lw)
	ci.draw_line(at.call(0.4, 5.2), at.call(0.4, 8.25), cut, lw)


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
