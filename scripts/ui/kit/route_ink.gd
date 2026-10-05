class_name RouteInk
extends RefCounted
## ART-7 3B: the netrun route's colours and faces in one place (ART_BIBLE v2 §2.2 tokens,
## §4.6 option A, §1.2 media), every one a Palette token (1A) or face (Courier Prime paper,
## Permanent Marker pencil). No literal colours (the static lint).
## Draw-only; no game state.

## Option A rings (§4.6): one outline ring carries a route node's state.
## Lime: walked / visited (the Cell's lime line). §2.2: drawn as #D4FF00.
const RING_WALKED := Palette.CELL_ACID
## Orange: selectable now (the run orange, §2.2 RING_AVAILABLE #FF8C1A; Appendix C #22 keeps
## orange for every corporation).
const RING_AVAILABLE := Palette.RING_AVAILABLE
## White: not available yet (§2.2 RING_UNAVAILABLE #F2F6FF).
const RING_UNAVAILABLE := Palette.RING_UNAVAILABLE
## Dim grey: cut off, the run never goes back (§2.2 RING_CUT).
const RING_CUT := Palette.RING_CUT
## Grease pencil (§1.2): red = threat / the TARGET circle; yellow = our plan.
const PENCIL_THREAT := Palette.PENCIL_THREAT
const PENCIL_PLAN := Palette.PENCIL_PLAN
## The pencil's dark under-shadow (§1.2: it reads day and night).
const PENCIL_SHADOW := Palette.PENCIL_SHADOW
const PENCIL_SHADOW_ALPHA := 1.0
## The pencil's wax opacity (§1.2: alpha 0.96).
const PENCIL_ALPHA := 0.96
## The police lights circling a node Heat has made harder (§4.3: red / blue).
const HEAT_LIGHT_RED := Palette.HARM
const HEAT_LIGHT_BLUE := Palette.NET_CYAN
## Sticker die-cut border and the ink keyline under every ring (§1.2 vinyl sticker).
const DIE_CUT := Palette.PAPER
const KEYLINE := Palette.INK
const KEYLINE_ALPHA := 0.9
## Node-type sticker fills (§4.6: stickers keep full colour; state lives in the ring):
## combat steel navy, elite hot red, event terminal green, shop blue, rack amber-brown.
const STICKER_FIGHT := Palette.NIGHT_BLOCK_LIT
const STICKER_ELITE := Palette.HARM_INK
const STICKER_EVENT := Palette.GAIN_INK
const STICKER_SHOP := Palette.NET_BG_INNER
const STICKER_RACK := Palette.CRT_AMBER
## How far the rack's amber is darkened into its brown sticker.
const RACK_DARKEN := 0.55
## The shop sticker's blue lightening (its navy reads as black otherwise).
const SHOP_LIGHTEN := 0.25
## Corp paper (§1.2): the intercepted document's stock, ink and stamps.
const PAPER_STOCK := Palette.PAPER
const PAPER_RULE := Palette.PAPER_ALT
const PAPER_INK := Palette.INK
const PAPER_STAMP := Palette.HARM_INK
const PAPER_FIELD := Palette.TEXT_LO
## Decrypted holo (§1.2): corp tint at about 78 %, the cracked seal's red fracture.
const HOLO_ALPHA := 0.78
const HOLO_SCRIM := Palette.NIGHT_SKY
const HOLO_SCRIM_ALPHA := 0.88
const HOLO_FRACTURE := Palette.HARM
const HOLO_TEXT := Palette.TEXT_HI
const HOLO_FIELD := Palette.TEXT_MID
const HOLO_STAMP := Palette.CELL_ACID


## The world Heat tint on maps (§2.2 HEAT_B).
static func heat_b() -> Color:
	return Palette.HEAT_B


## The sticker fill of route node kind `kind` (CityMapOverlay.KIND_*).
static func sticker_of(kind: String) -> Color:
	match kind:
		CityMapOverlay.KIND_ELITE:
			return STICKER_ELITE
		CityMapOverlay.KIND_EVENT:
			return STICKER_EVENT
		CityMapOverlay.KIND_SHOP:
			return STICKER_SHOP.lightened(SHOP_LIGHTEN)
		CityMapOverlay.KIND_RACK:
			return STICKER_RACK.darkened(RACK_DARKEN)
	return STICKER_FIGHT


## The state ring colour of a route node in state `state` (RouteOverlay.STATE_*).
static func ring_of(state: String) -> Color:
	match state:
		"walked":
			return RING_WALKED
		"next":
			return RING_AVAILABLE
		"cut":
			return RING_CUT
	return RING_UNAVAILABLE


## The corp paper's typewriter face (§2.9 Courier Prime).
static func paper_font() -> Font:
	return Palette.paper()


## The paper's letterhead face (§2.9: IBM Plex Sans Condensed Medium).
static func letterhead_font() -> Font:
	return Palette.body_medium()


## The stamp face (§2.9: Anton).
static func stamp_font() -> Font:
	return Palette.display()


## The grease pencil's face (§2.9: Permanent Marker as wax).
static func pencil_font() -> Font:
	return Palette.pencil()
