# TETHYS DEEP: identity (exploratory, not content)

**Tagline:** *Breathe easy. We hold the air.*

Board: `identity_board.png`. Crest (TIDE WHIRL) and icons: `crest_icons.png`. Crest options: `crest_options.png`.

## What they sell, in Night-City terms
The air and the waterline.
- **The seawall and the pumps:** when the sea came up, Tethys Deep built them. The lower wards stay dry only while
  their district pays the **BREATHE PLAN**. A ward that lapses is flooded by switching the pumps off.
- **Cold storage:** below the waves, the **ATLANTIS** arcology holds the city's banks, backups and memories in pods
  chilled by the abyss.
- **The sea cables:** those pods are wired ashore through Tethys sea cables.

They also sell air leases in the flooded wards and fresh water by the litre.

A corporate deep-sea arcology, not a fairy tale. "Atlantis" is the arcology's product name, and Tethys is the
company that owns it.

## The slots it fills

| Slot | Tethys Deep |
|---|---|
| Central Server | **THE BLACK SMOKER**, the vent-powered core at the trench floor (its Hub: **THE VENT CAP**) |
| House rule | **TIDE** (proposal, below) |
| Boss rule | THE BLACK SMOKER OVERCLOCKS one of its own slices every turn, unless THE VENT CAP is breached |
| Enemies | Pump Warden, Diver drone, Kelp Crawler, Pressure Sentinel, Lamprey (parasite). Elites: Siphonophore (chained satellites), Angler |
| Exploits | INTEL: the tide tables. BREACH: the pump override. VIRUS: open air, which frees the air leases |
| Raids | **HIGH TIDES**: amphibious pods and flood barges. The after-action report is a FLOOD ADVISORY |
| Campaign lost | verb stamp **SUBMERGED** |
| Event speakers | The Harbourmaster, Dr. Selka Marr (pressure medicine), VOICE OF ATLANTIS (the arcology's concierge AI) |
| Story paths | The Breathe Plan, Ward Nine Floods, Cold Storage, The Cable Cut, Sunken Ghost (foreshadows DISPATCH), Salvage Rights |
| HQ landmark | **ATLANTIS STATION**: five pressure decks hung down a trench to the vent (`hq_overview.png`) |
| Site types | AIR LEASE (oxygen depot), PUMP HOUSE (seawall lock and pumps), BUOY RELAY (the sea-cable head's relay buoy), COLD VAULT (submerged data pod), TAP HOUSE (fresh water by the litre), DOCK LOCK (sub dock airlock) |

## House rule: TIDE (proposal)
Every Tethys fight runs on a four-step tide shown on the HUD: LOW, RISING, HIGH, FALLING. The tide moves one step per
turn, and the starting step is seeded at fight start.

| Tide | Effect on Tethys enemies |
|---|---|
| HIGH | Their SANDBOX slices give double shield |
| LOW | Their shield drains by 3 at turn start |

The tide is fixed and visible, so preview equals result. The HQ uses the same clock (the BALLAST TIDE), so one
mechanic reads in combat and on the map.

## Heat flavour

| Band | What the city does |
|---|---|
| NOTICED | Buoy beacons blink on the canals |
| FLAGGED | Sonar pings ripple across the map; two dive lights sweep |
| HUNTED | Seawall sirens; the flood gates shut and the ward goes under |

## Palette

| Token | Hex | Job |
|---|---|---|
| ABYSS BLUE | #2F6BFF | **The corp hue:** crest, pins, wheel kit, neon trims |
| LIGHTLESS RED | #C8264E | Tier II and the material. Deep-sea security wears red because red is invisible at depth (the water medium absorbs red first, so it really does vanish in the renders) |
| TRENCH | #06112A | Pads, the paper band, backs |
| PHOTOPHORE | #7CF2E4 | World light only (bioluminescence, kelp tips, dome strips) |
| DIVE-LIGHT | #FFE9B8 | World light only (warm interiors, sub headlights) |

**Clash check** (ΔE against abyss blue; values on the board):
- Meridian 151, Solace 184, Orbital 91, REBEL_CELL 137, Aurelian 132.
- **Halcyon violet is 27:** the "needs a second cue" pair. The two are never on the same map, and they differ in
  material (Halcyon violet blueprint + amber, Tethys wet hull + glass) and in crest. Halcyon's v1 code value #8C7BFF
  would be closer still: the bible's palette debt (2.4) must be paid first.
- NET_CYAN 88. Route states and pencils are all > 75.
- **Lightless red** sits near HARM. It is material and tier II only, never a UI signal. That is the same rule as
  Meridian's hot red.

## Typography accent
Lowercase IBM Plex Sans Condensed with a **waterline**: a 1 px cut through the x-height. Depth marks (-412 m) use
tabular figures, on paper only. In neon it is a single blue tube, with bubbles for the dots.

## Tone of voice
Calm, spa-soft, clinical about breath. Lowercase, short sentences, countdowns. It never raises its voice; it lowers the
water.

- **Corp paper:** *SERVICE ADVISORY // ward 9.* "your breathe plan has lapsed. pumps in your district will pause in
  00:30. please move to higher ground or renew. breathe easy." Stamp: LAPSED.
- **DISPATCH:** "Tide's up in Ward 9. They switched the pumps off at midnight. Go deep while they're busy bailing."
