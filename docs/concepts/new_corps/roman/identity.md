# AURELIAN CONCORD: identity (exploratory, not content)

**Tagline:** *Bread. Circus. Terms apply.*

Board: `identity_board.png`. Crest and icons: `crest_icons.png`.

## What they sell, in Night-City terms
The bread and the circus.
- **The DOLE:** free nutrient loaves for the lower wards, paid for in *patronage*: your vote, your data, your labour
  hours.
- **The CIRCUS:** arena bloodsport streamed to every leash, with the betting on the side.
- **The patron ledger:** underneath it all, every subbie is some House's *client*, and the House collects.

They also control the **aqueduct data conduits**, the old-stone backbone that carries the city's traffic over the
streets, and the **triumph-gate tolls** on the boulevards.

A corporate empire in neon: it congratulates you while it bills you. It is not a museum. The marble is a brand, and
the statues are billboard mounts.

## The slots it fills (same as the four corps)

| Slot | Aurelian Concord |
|---|---|
| Central Server | **THE ROSTRUM** (its Hub: **THE GRAND STAND**) |
| House rule (enemy signature) | **VERDICT** (proposal, below) |
| Boss rule | THE ROSTRUM calls a VERDICT on the slice under your pointer every turn, unless THE GRAND STAND is breached |
| Enemies | Lictor (fasces bodyguard satellites), Legionary drone, Tax Farmer, Lanista, Vestal Firewall. Elites: Praetorian, Censor |
| Exploits | INTEL: the client rolls. BREACH: the gate codes. VIRUS: the open dole, which frees the ration chips |
| Raids | **LEVIES**: legion wedges in verdigris and a gilded float. The after-action report is a LEVY RECEIPT |
| Campaign lost | verb stamp **PACIFIED** |
| Event speakers | The Patron (gilded mask bust), Lanista Corvina (arena promoter), the Tribune of Clients (debt collector) |
| Story paths | The Free Bread, Fixed Games, Census of Clients, Bread Riot, A Patron for DISPATCH (foreshadows DISPATCH), The Triumph |
| HQ landmark | **THE CIRCUS AURELIUS**: a colosseum of four turning seating rings (`hq_overview.png`) |
| Site types | DOLE (bread ration depot), ANNONA (granary and grain office), LUDUS (arena gym and stream studio), AQUEDUCT (data-conduit pump station), ATRIUM (patron's debt office), CURIA (the patrons' senate house), TOLL GATE (triumph-gate toll) |

## House rule: VERDICT (proposal)
Aurelian specials mark one of your slices with a VERDICT. When the marked slice next resolves, the landing decides:

| Landing | Verdict | Effect |
|---|---|---|
| PERFECT | thumbs up | the slice is OVERCLOCKED |
| WEAK | thumbs down | the slice is CORRUPTED |
| GOOD | no verdict | the mark stays |

It uses only existing statuses (GDD 2.9) and existing landing tiers (2.4). It is deterministic, so the preview shows the
verdict before SEND IT.

## Heat flavour (bible 3.15 bands)

| Band | What the city does |
|---|---|
| NOTICED | Lictor drones circle the side blocks |
| FLAGGED | The rooftop statues' eyes turn red; two arena searchlights sweep |
| HUNTED | The triumph gates seal, and the Legion marches the boulevard |

## Palette (checked against the existing five corps, the route states and the UI roles)

| Token | Hex | Job |
|---|---|---|
| VERDIGRIS | #29DBA6 | **The corp hue:** crest, pins, wheel kit, vehicle beacons, neon trims. Roman bronze gone green under acid rain |
| TRAVERTINE | #E9D5AA | Tier II and the material: stone, bezel, the paper band |
| PORPHYRY | #3A1426 | Pads, the paper letterhead band, sticker backs, slice screens |
| GILT | #C9A35A | World signage only, in small doses (it sits near Exploit gold #FFD24D) |
| MARBLE | #F3EFE6 | World material only |

**Clash check** (CIE76 ΔE against verdigris; values printed on the board):
- Every existing corp is at least 55: Orbital ice white is the nearest (55), then Solace lime (61).
- Route lime is 80, route orange 109, route white 61, route grey 69.
- Pencil yellow is 90 and pencil red 141.
- **NET_CYAN is 48:** fine, but verdigris must never sit on a Terminal edge.
- **GAIN is 27:** the one "needs a second cue" pair. Verdigris is never used for a heal or gain chip. GAIN always
  carries its ▲, and the corp hue always carries the crest or the material.

Squint test: the seven corp hues blur to seven separate blobs. In greyscale, verdigris is mid-light: it is set apart
from Orbital (lighter) and Halcyon (darker) by its material.

## Typography accent
Inscription capitals in IBM Plex Sans Condensed Medium:
- tracking +45 %;
- V for U, as in `AVRELIAN · CONCORD`;
- interpuncts between words;
- Roman numerals for lots and seats (LOT XXIV, SEAT CXII).

Carved lettering has an inset shadow on travertine. In neon it is a single tube line. No new font is needed: it is all
repo fonts.

## Tone of voice
Grand, paternal, legal. Latin tags are branding, never decoration. It congratulates you while it bills you.

- **Corp paper:** *CLIENT NOTICE // LOT XXIV.* "Citizen-client, your patronage has been RENEWED. Your ration is
  assured. Your attendance at the Games of the Ides is EXPECTED. Rejoice." Stamp: RENEWED.
- **DISPATCH:** "Aurelian's throwing games tonight. Whole ward's watching the arena. Nobody's watching the aqueduct."
