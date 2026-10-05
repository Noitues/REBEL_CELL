# REBEL_CELL — Art Bible v2

**Status:** v2.0 (2026-10-05), rewritten from the concept-art direction pass (rounds 1–43).
**Supersedes:** `docs/ART_BIBLE_v1.md` (v1.0, 2026-09-28). v1 stays as the record; where this
document is silent, v1 still applies (layout grid, component states, input widgets, definition
of done). Section 10 lists what changed; Appendix C lists contradictions between rounds.

**Sources of truth, in order:**
1. `docs/concepts/DIRECTION_REVIEW.md`: the decision log. Later entries override earlier ones.
   **LOCKED** items are binding. Its "Game to-do" lists are game-design proposals, not art rules.
2. The round folders under `docs/concepts/` (each has a `NOTES.md`). Appendix A names the latest
   locked image for every element.
3. `docs/GDD.md` for game rules and terms. Art never changes a rule. Where a locked concept needs a
   rule that does not exist yet, it is listed in Appendix B and must go through `DECISIONS.md`.
4. `docs/STYLE_GUIDE.md` §5.1–5.5: the motion and interaction rulings (ANIM-*) stay binding.
   Its icon tables (§4.1) stay binding until the glyph atlas (§3.6 below) replaces them.

**Words:** MUST / NEVER are hard rules. SHOULD is the default; deviate only with a reason logged in
`DECISIONS.md`. "Proposal" marks art that shows a mechanic the game does not have yet.

**Known conflict to resolve first:** GDD §9.1 (locked) still describes "Wireframe Cyberspace" for
the net and "Punk Zine (paper, tape, marker, spray paint)" for the Cell's voice, and GDD §9.4
describes corporate wireframe creeping over the zine layer. The direction pass replaced both (spray,
marker and wireframe are rejected). A `DECISIONS.md` entry and a GDD §9 update are needed before
reintegration (see `GDD_ART_COVERAGE.md` §3).

---

## 1. Pillars and the mixed-media rule

### 1.1 North star
> **A gritty low-poly city that watches you, with the Cell's hardware, stickers and wax pencil
> laid over it.**

1. **Readable first.** The slice under each needle and its value read instantly, at hero size, at
   r = 60 and in greyscale. Readability beats spectacle.
2. **Every medium has one job.** The material tells the player *what kind of information* it is
   before they read it (1.2).
3. **The city is alive and reacts.** Traffic, sky lanes, signs and Heat lights move; territory and
   Heat change the city, not a HUD tint.
4. **True to the rules.** Plans, previews, forecasts and pencil marks show only what the rules
   will do. Preview equals result.

Tone: scrappy, nocturnal, precise, funny under pressure. Anti-words: glossy chrome, sterile,
graffiti chaos, cute.

### 1.2 The media and their jobs (LOCKED)

| Medium | Job | Look | Never |
|---|---|---|---|
| **World** | The city, HQs, Sites, combat backdrops, event CAM feeds, busts | **Cv2** gritty triangulated low-poly (variable facet sizes, tone jitter per triangle) + **E** cel shading: 3 hard toon bands, wobbly ink lines from id/normal/depth edges, grime, bloom and **light spill** from glowing elements onto walls and streets, depth haze, rain at night | Flat blocks or placeholders; wireframe; painterly; labels baked into the world (only diegetic signage) |
| **Vinyl sticker** | Things that **never change**: cards, node-type and route-node stickers, buttons and verbs (SEND IT, JACK IN, START DEFENSE, CONTINUE), screen titles, name plates, the result stamp (CELL HOLDS), firmware drop, Exploit keycards, temporary effect words | Anton lettering, ink keyline, extrude, white die-cut border, gloss 0.22 at rest with one slow sweep on one sticker at a time; peel, slap and dissolve motion | A value that changes (HP, Heat, resources, live forecasts); portraits (they change state) |
| **Grease pencil** | **Plans and annotations that are true to the rules** | Opaque wax (alpha 0.96), thick, rough edge with dropouts and a sheen line, dark under-shadow so it reads day and night. Yellow `#FFE200` = our plan / valid; red `#FF1C2C` = threat / invalid / loss. Solid = what will happen; dashed = what-if. Writes on, wipes off with a cloth wipe (never fades alpha) | Jokes or claims that misstate the game state ("THEY WANT THE VAULT" unless true for that threat); live numbers; body text. **No UI ever covers grease pencil** (standing rule, round 40) |
| **CRT terminal** ("Screens & Data") | **The Cell's own systems**: slices, menus, resources, Heat strip, crew roster, YOUR NETWORK, tooltips, toggles, toasts, forecasts (IF CLEARED, IF PLACED), Speed/Skip, Daemon tiles, dialogue feed | Navy glass, cyan edge, Share Tech Mono, 3 px scanlines, faint scrolling hex-dump, edge glow, type-on text, `>` caret; accent per use (cyan Cell, lime firmware, gold Schematics, corp colour inside corp Terminals, red DISPATCH) | Paper, corp intel, sticker gloss |
| **Corp paper** | **Intercepted corp documents**: raid work order, after-action raid report, campaign audit dossier, seizure notices, operative dossier on the map, event memos from corp speakers | Courier Prime (fields, titles), IBM Plex Sans Condensed Medium letterheads, Anton stamps (CLASSIFIED, CASE CLOSED, PROCESSED), corp seal and letterhead per corp, redactions, paper clips, polaroids, auditor's blue ballpoint post-its | The Cell's own UI |
| **Decrypted holo** | **Hacked corp intel**: the selected Site file, THREAT INTEL, intercepted corp news toasts | Corp tint at about 78 %, 4 px scanlines, 3–4 slow bands, ±2 px RGB split on the edge only, near-opaque scrim (0.88) behind it, the corp seal cracked with a red fracture and a DECRYPTED stamp | Anything the Cell owns |
| **Binary bits** | **Digital transitions, dissolves and damage**: card dissolve, damage shards, heal inflow, status apply/tick, temporary-label dissolve, drone and enemy destruction, player defeat, jack-in rain | `0`/`1` glyphs (Share Tech Mono atlas with a same-colour outline) in the colour of the source; white-hot for the first 60–100 ms, flipping 0↔1, tumbling, then sucked along a curve into their target | Decoration with no cause; travelling across a wheel face (bits go round the rim) |
| **Bare Anton** | Live big numbers: HP, Heat value, damage numbers | Anton, 2 px dark rim, glow in its own colour | Sticker backing |

**The fiction behind it.** The world is the city. Stickers are the Cell's fixed objects. Pencil is
the Cell thinking. Terminals are the Cell's computers. Paper and holo are what the Cell stole from
the corps (paper = printed, holo = scanned and decrypted). Bits are data moving.

**Rejected (do not reintroduce):** spray paint and stencils, the dripping marker, ransom collage,
ink brush, light pen as an overlay, the wireframe net, painterly or neon-painting cities, the
round-1 directions A–E, round-2 A/B/D, Cv3, illustrated identity icons on slices (rounds 8–9).

### 1.3 Word over a system word
A verb sticker sits over a washed-out system word in the terminal font: SEND IT over `EXECUTE`
(with `> turn_resolve.exe [SPACE]`), BREACH over `CONNECT`. The sticker is the action; the system
word is the machine underneath (round 22 `send_it_sticker.png`).

---

## 2. Palette, tokens and typography

Code form: `scripts/ui/kit/palette.gd` (`Palette`) and `scripts/ui/kit/ui_theme.gd` (`UiTheme`).
Views never hard-code colours or sizes. A token changed below MUST be changed in `Palette` in the
same commit, with a `DECISIONS.md` line.

### 2.1 Brand and neutral tokens (kept from v1)

| Token | Hex | Role |
|---|---|---|
| `CELL_PINK` | #FF3DA8 | The Cell's brand; the committing verb sticker (SEND IT, BREACH, BURN IT); attack/crit slices |
| `CELL_ACID` / `FOCUS` | #D4FF00 | Focus brackets and aim; never an ON or selected colour |
| `CELL_TURF` | #D4FF00 | **Lime = the Cell's**: owned nodes and links, walked netrun path, claimed Sites, visited rings |
| `NET_CYAN` / `PROTECT` | #5CE1FF | Terminal edges, defend/shield slices, block and shield FX |
| `TERMINAL_BG` / `TERMINAL_EDGE` / `TERMINAL_TEXT` | rgba(5,13,28,.92–.95) / #5CE1FF @ 75–80 % / #CFF6FF | CRT panels |
| `INK` | #111111 (glyph outline `#0C0A16`) | Ink on paper and stickers; glyph outline |
| `PAPER` / `PAPER_ALT` | #F2EEE4 / #E9E4D6 | Corp paper stock |
| `CRT_AMBER` / `WARN` | #FFB000 | Caution, NOTICED band, low HP |
| `RESIST_GOLD` | #FFD24D | Spin resistance; tier III gold; Exploit gold |
| `NEON_VIOLET` | #B04DFF | City neon ink only |

### 2.2 Semantic tokens (kept from v1; MUST pair with a shape, glyph or word)

| Token | Hex | Meaning | Paired with |
|---|---|---|---|
| `HARM` | #FF4433 | Damage, cost, loss, refusal, LETHAL | ▼ / "−", the word |
| `GAIN` | #7BE07B | Heal, gain | ▲ / "+" |
| `HARM_INK` / `GAIN_INK` | #AB2E22 / #396739 | The same on paper (≥ 4.5:1) | |
| `DISABLED` | #6A7080 outline; label `TEXT_MID` | Unavailable | lock or reason; greyscale vinyl at 80 % for stickers |
| `TEXT_HI` / `TEXT_MID` / `TEXT_LO` | #F2F6FF / #AFC0D6 / #7A889C | Text on dark | |
| `SCRIM` | #02030A @ 55 % + 6 px blur | Behind panels over the city | |

**New tokens to add:** `PENCIL_PLAN` #FFE200, `PENCIL_THREAT` #FF1C2C, `PENCIL_SHADOW` #060308 @ 85 %,
`HEAT_B` #CE5412 (the world Heat tint on maps), `RING_AVAILABLE` (the run orange, drawn as
#FF8C1A), `RING_UNAVAILABLE` white #F2F6FF, `RING_CUT` dim grey. Every netrun concept was drawn on
the Meridian campaign, so it is open whether "available" stays orange or follows the target corp's
hue (Appendix C #22). Orange is the default.

### 2.3 Slice colours (kept)
Slice colour = **slice type on any wheel**, never ownership. Attack/crit `CELL_PINK`; defend/shield
`NET_CYAN`; evade/heal #7BE07B; afflict #C85AFF; deploy #B08CFF; miss #6A6A6A. Ownership reads from
the wheel's corp kit (3.11) and bezel. Damage shards take the **attacking slice's** colour in both
directions (round 18).

### 2.4 Corporation palettes (LOCKED kits, round 18 values)
Every corp owns **hue + material + crest + landmark**, never hue alone.

| Corp | Primary | Secondary (tier II) | Material | Crest | HQ landmark |
|---|---|---|---|---|---|
| Meridian Freight | orange #FF8C1A | red (hot #FF2E28) | container steel + barcodes, hazard rim | crane-A (castle crest to follow, Appendix B) | Container-wall fortress with moat and gantry-crane keep, rail yard |
| Solace Biosystems | lime / leaf green #96FF46 | pink #FF4696 | leaf-green glass, cells, bubbles | porcelain roundel / helix | Lit DNA double helix (no centre tower) |
| Halcyon Civic | violet #B06EFF | amber #FFAA28 | violet blueprint with amber notes | the **EYE** | Seven-tier Civic Core with scanning eye |
| Orbital Commons | ice white #CDF0FF | white | near-black space, white stars, steel-blue nebula, pale steel bezel | ringed planet | Silo crescent: dishes round an in-ground missile silo |
| REBEL_CELL (DISPATCH) | red #E8141E | pale pink | corrupted Cell PCB, broken black-red rim | raised **FIST** (thumb tucked on the map) | No tower: red-window fist district, Tokyo canyon backdrop |

Rules:
- Squint test: blurred, the five read as orange, lime, violet, pale white-grey and red
  (`round18_corp_wheels/corps_compare.jpg`).
- A corp hue MUST NOT be used for any UI role in 2.2.
- Vehicles carry the corp three ways (under-glow pool, roof livery plate, twin beacons). Solace
  vehicles use (0.42, 1, 0.16), deliberately greener than Cell lime. REBEL_CELL rings are paled to
  #FFAAAC so dashes read.
- **Palette debt:** `Palette.CORP_SOLACE`, `CORP_HALCYON` and `CORP_ORBITAL` still hold the v1
  values (#3DFF8B, #8C7BFF, #7FA8FF). They MUST move to the values above. Two risks to check when
  they do (Appendix C): Orbital #CDF0FF sits near `TEXT_HI`, the exact problem v1 fixed, so its
  material and crest MUST carry it; Solace #96FF46 sits near Cell lime #D4FF00, so Cell lime stays
  reserved for ownership and Solace never appears on a link or ring.
- City district tints on the map are still round 6 (Solace teal, Orbital blue). A territory-colour
  pass is owed.

### 2.5 Class accents (LOCKED, round 22 `class_colours_v2.png`, used by portraits and beacons)

| Class | Accent | Class | Accent |
|---|---|---|---|
| Breaker | #FF3DA8 pink | Wrecker | #FF6E32 orange |
| Ghost | #5BE0FF cyan | Phantom | #DBC1FF pale lilac (fallback #C9A6FF) |
| Rigger | #7AE07A green | Overclocker | #FFB040 amber |
| Botnet | #6072FF indigo | Hivemind | #C659FF violet |

These replace v1 §7.1. `Palette.class_accent` MUST follow. Accents live only on portraits, the hub
core glow, the station beacon and dossier stripes, never on UI roles.

### 2.6 Daemon trigger families (LOCKED, round 34)

| Family | Colour | Fires |
|---|---|---|
| PERFECT | yellow | on a Perfect |
| MISS | deep red #EC303A | on the Miss slice |
| TURN | cyan | combat/turn start, always-on |
| ACTION | lavender #BA92FF | on your nudge or card |
| RUN | lime | after a won fight / Server Rack capture |
| HEAT | orange | netrun or Heat |

Colour is the second cue; each Daemon has a unique sigil and the tooltip names the family.

### 2.7 Rarity
Common = cool white LED / gunmetal, 1 pip. Uncommon = cyan, 2 pips. Rare = gold, 3 pips. Shared by
firmware chips and Daemon tiles. Cards: rarity on the card is still undesigned (Appendix B).

### 2.8 Heat colours
Band words are always printed (never colour alone). COOL 0–24, NOTICED 25+ `WARN`, FLAGGED 50+
#FF7A1A, HUNTED 75+ `HARM`. Heat is never green. On maps the world Heat tint is `HEAT_B` #CE5412.

### 2.9 Typography

| Role | Face | Sizes (1080p px; ÷1.5 for the 720p `UiTheme` steps) | Floor | Licence |
|---|---|---|---|---|
| Sticker / display | **Anton** Regular, ink keyline 5 px, extrude 7 px, die-cut 12 px | 144 verbs, 96 titles, 66 stamps, 45 values | 36 sticker word, 30 bare number | SIL OFL 1.1, in repo |
| Terminal | **Share Tech Mono**; CAPS +8 % tracking | 33 / 27 / 22 / 18 | 18 | SIL OFL 1.1, in repo |
| Grease pencil | **Permanent Marker** rendered as wax, tracking 0.45 | 48 / 34 / 28 | 26 | Apache 2.0, in repo |
| Body / tooltip | **IBM Plex Sans Condensed** Regular + Medium (keywords in Medium, in their colour) | 22 body, 20 small, line 1.4, 36–60 chars a line | 20 | SIL OFL 1.1, in repo |
| Corp paper | **Courier Prime** Regular (fields) and Bold (titles); Plex Sans Condensed Medium letterheads; Anton stamps | 34 title, 30 letterhead, 20 fields, 15 meta | 20 for anything read | SIL OFL 1.1, **fetched** into `docs/concepts/round33_ui_chrome/fonts/`; MUST be copied to `assets/fonts/` with `OFL_CourierPrime.txt` and a README row |

- Every face imports as MSDF. Sizes come from `UiTheme` × `Settings.text_scale`; stickers scale as
  whole baked objects.
- Nothing the player reads is below the 720p caption floor (12 px), v1 §4.3 still applies.
- Bits use Share Tech Mono (its 0 and 1 stay distinct when rotated). Consolas and Courier New are
  concept-only and MUST NOT ship.
- DISPATCH text stays Share Tech Mono on clean surfaces.

### 2.10 Focus and state colours in chrome
- **Focus:** lime #D4FF00 corner brackets, 3 px thick, 7 px outside the element
  (`StyleBoxBrackets`). A focused sticker gets a lime die-cut halo instead. A focused menu line also
  gets a `>` caret. Lime is therefore never ON or selected; ON/selected are cyan fills plus a word.
- **Two-sticker choice:** yellow (#FFEE60 → #FFB60E) = the safe or back-out choice (CANCEL,
  default focus); pink = the committing verb. Grey vinyl is only the disabled state.
- **One sticker verb per screen.** Screen titles are yellow stickers so they never compete with
  the pink verb.

---

## 3. Combat

### 3.1 The screen (LOCKED layout, round 31 / round 43 HUD v4)
Reference: `round41_wheel_stack/combat_typical_v4.png`, `combat_worst_case_v4.png`.
- Player wheel at about (481, 490) r = 220; boss at about (1438, 520) r = 236 (1080p).
- **Backdrop** (3.14) fills the screen; each wheel's area is softened and darkened about 55 %, with
  darker bands under the hand and the top bar.
- **Nudge buttons** sit **above** each wheel on one line (y ≈ 216): CCW on the left, CW on the
  right. Player keys [Q] / [E]; boss keys [A] / [D] (proposal, check bindings).
- The **CELL-9 // CLASS** name sticker sits just above the RAM readout, bottom left.
- **No forecast tags, no NEXT plates.** Beside each HP value sits this turn's result if SEND IT is
  pressed now, in this order:
  `[final damage]` (red, boxed) `(N shield)` (blue, absorbed, no box) `+N shield` (green)
  `−N <icon>` (other losses, e.g. RAM) `<status icons ×N>`.
  Example: `−6 (4 shield) +4 shield −1 RAM`. Hovering the final-damage chip shows the breakdown
  tooltip (each wheel's slice, landing tier, guard and hub passive). Chips update when the wheel
  settles.
- **SEND IT** is the pink vinyl sticker over `EXECUTE` (bottom right); RESPIN and UNDO are terminal
  chips beside it. The undo block shows on the UNDO button (greys out, small lock tick), never as a
  word.
- **Daemon rack:** a narrow CRT plate on the left edge beside the player wheel (3.13).
- **RAM:** terminal pips; gain comes from the TURN banner (3.12).

### 3.2 Wheel frame: D4 "Lens & rail" (LOCKED for every wheel)
Reference: `round13_wheel_details/d4.png`, `combat_d4.png`.
- **Bezel:** a D3-lite machined profile with a glass channel, lip shadow on the disc, hub shadow and
  a glass crescent. One baked bezel sprite + one shadow sprite per corp.
- **Pointer (blade):** a cream notched blade rooted in the bezel, its tip biting the slice's outer
  bezel, with a dark **value window** showing the live value. Multi-needle wheels: every needle is a
  full blade with an index tab (1, 2, 3).
- **Active slice:** lifted 2.5 %, cream outline; other slices dimmed to 68 %.
- **Telemetry ring (V2):** the ring scrolls class/corp telemetry. Over the pointer, ±50° becomes
  the **readout rail**: static, tinted the program colour, bracketed, reading
  `OVERFLOW 12 // CRIT // PERFECT //`. The rail **splits around each needle** (a dark ±8° gap, no
  text), so text never runs under or over a needle (round 39). Rest-of-ring scrolls; the rail does
  not.
- **At r = 60:** the rail becomes a solid colour arc over the pointer, the blade is scaled ×1.6,
  the hub shows the HP number. All values move to the HP chips.
- **HP arc:** thick, segmented, under each wheel; HP number below. Boss phase pips sit on the HP
  arc (66 %, 33 %).
- **Boss extras:** nameplate banner as the blade mount with a crowned blade in the corp colour, a
  counter-rotating threat ring with crest lugs, phase pips. **No standing NEXT arrows** (they became
  the card-play preview).
- **Option (accessibility, proposal):** "hub shows slice value" (D2 readout) in Settings.

### 3.3 Hub cores
Reference: `round40_hub_inner_ring/hub_cores_v3.png`, `round39_hub_inner_ring/hub_cores_v2.png`,
`round38_hub_inner_ring/hub_cores.png`.
- **Player hub:** a dark CRT disc (class tint, scanlines, vignette) in a machined rim with an accent
  hairline; the emblem centred with an accent glow; core name and a short passive under it; sits
  inside the inner ring. At r = 60 the emblem only.
- **Class cores (LOCKED):**

  | Class | Core | Emblem |
  |---|---|---|
  | Breaker | `breaker_core` | crowbar claw striking a spiderweb of glass cracks (9 spokes, 3 broken rings) |
  | Wrecker | `wrecker_core` | sledgehammer, no speed lines |
  | Ghost | `ghost_core` | hood with mesh eyes |
  | Phantom | `phantom_core` | mask with a moving echo trail (after-images slide left and fade; static icon `CORE_phantom_echo`) |
  | Rigger | `rig_core` | firmware chip dropping into a socket |
  | Overclocker | `overclock_core` | RPM gauge, needle buried in the red zone, ×1000 window |
  | Botnet | `swarm_core` | three linked drones |
  | Hivemind | `hive_core` | hex cell holding 4 nodes |

- **Mk2** (Rank 2 "Upgraded Hub Core"): same emblem + a second notched rim + an `MK2` tab on the
  bottom rim.
- **Enemy hubs (LOCKED):** no inner ring; the hub fills the centre with a slow corp-colour chevron
  sweep. Compliance Lock = rubber stamp; Priority Routing = express arrow overtaking two lanes;
  Emergency Powers = siren dome; Station Keeping = satellite; Auto-Renew = renew loop round a plus;
  Root Access = terminal with `#_`.
- **Hub Breach = LOCKDOWN (LOCKED, round 40):** a **waterline of encrypted bits** (cyan hex and
  symbol characters, slowly churning, bright wavy surface) fills the hub and drains with the
  lockdown timer; the hub underneath dims; a LOCKDOWN plate with a padlock; turns left top right.
  Hub Breach starts at 1, Short Circuit at 2. Passive is off while any water remains. At r = 60 a
  thick `HARM` ring carries the state. The round 38 cracked-glass breach is superseded.
- **Player defeat (LOCKED, round 40):** the core breaks into 4 px bits, bottom rows first; they
  fall, tint toward the class accent and **vanish at the circle's edge** (no drain line, full alpha
  until they vanish); FLATLINED stamps in at the end.

### 3.4 Slices (LOCKED family C "Screens & Data")
Reference: `round34_slice_names/slice_system_final_v3.png`, `glyph_set_v3.png`;
`round17_slice_system/tiers_final.png`.
- Each slice is a **live CRT screen** in its own bezel. The animation fills the whole screen; the
  **read block** (white glyph + value on a darkened ellipse plate) stays **upright**
  (counter-rotated) at every angle. Corp animations are also composited upright (round 16).
- **Program names (LOCKED, round 34):**

  | Type | Program | Glyph | Screen |
  |---|---|---|---|
  | ATTACK | **SHIM** | dagger | (EXPLOIT screen) |
  | CRIT | **OVERFLOW** | 12-point burst | (ZERO-DAY screen) |
  | DEFEND | **DEFRAG** | brick wall with flame tongues | shots fall radially inward from the outer rim onto a crenellated wall on the hub side |
  | SHIELD | **SANDBOX** | sand pile with pail and shovel (option C) | |
  | EVADE | **DETOUR** | double chevron | road-sign hard 90° turn, packet with afterimages, "road closed" barrier |
  | HEAL | **HOTFIX** | crossed band-aids | |
  | AFFLICT | **INFECT** | biohazard | ooze slides down from the rim and pools |
  | DEPLOY | **TROJAN** | horse on a wheeled platform | |
  | MISS | **NULL** | "1/0" | static |

  The renames are a game to-do (strings and content); until then the code keeps the GDD type
  names. Corp specials: DOSE (capsule), CITATION (receipt), SOLAR FLARE (sun on the horizon line
  only), WEIGHT (anvil, was INERTIA), PRIORITY (rotating alarm beacon, Meridian RAM drain, was
  TARIFF / JUDGEMENT), GROWTH (Solace heal, true mitosis, pending rename), DRONE (quad-rotor).
- **Defend rule everywhere:** attacks come from the outer arc; the wall stands on the inner (hub)
  side of what it protects. Applies to card art, chips and hit FX.
- Drain variants (`atk_7_drain`) keep their type glyph plus a "−n RAM" chip.

### 3.5 Glyph set (LOCKED, round 17 package + round 18 PRIORITY)
Source of truth: `round17_slice_system/glyphs/*.png` (58 files, 256 px, white on transparent,
alpha = coverage) + `round18_corp_wheels/special_priority.png`.
- One flat white silhouette with few dark cut-outs; dark rounded outline added at render time
  (width 0.075 × size, `#0C0A16`).
- Strokes ≥ 40/512 of the box, cut-outs ≥ 24/512 (exceptions: SPOOF ridges, RECON rings).
- **16 px rule:** the outer silhouette alone identifies the glyph; soft IoU against every other
  glyph below about 0.68. Run the twin check for every new glyph.
- Attacks are pointed; defences blocky.
- **Status badges** say whether it helps: circle = helps; diamond = hurts; circle with a diamond
  notch = helps then hurts; rounded square = neutral; dashed outline = predicted.
- Pictograms carry an amount at the bottom right. **MOMENTUM is dynamic:** big/small numbers on the
  spin arrow, the big one is what will run (before a spin big 2 / small 5; after, small 2 / big 5).
- Aliases reuse files: FREEZE = `state_frozen`, RESIST = `special_weight`, DAMAGE = `slice_exploit`,
  SHIELD pts = `placeholder_shield`, EVADE = `slice_proxy`, HEAL = `slice_patch`.
- Placeholders (`placeholder_*`) are not in the game. VAULT, KEY and SPOOF are already raid node
  glyphs and would clash if they ever become slices.
- Hub, segment and Exploit glyphs join the same atlas (`hub_<core_id>`, `seg_<id>`).

### 3.6 Value and value read
- The value reads three times at hero size: blade window, read block, rail.
- **Read block is always on top** of every slice layer except the badge (3.10).

### 3.7 Upgrade tiers (LOCKED V2 "strong"; tiers are a game to-do)
The outer silhouette is identical at every tier; all flair sits inside the border; the read block
never changes; tier-tab pips (1/2/3) top centre.

| Tier | Bezel | Screen gain | Inside the border |
|---|---|---|---|
| I | matte | 60 % | — |
| II | brushed steel, type-colour trim | 100 % | 2.2 px bright inset line, 10 px gap |
| III | gold with holo lip | 142 %, holo sweep | solid 2.6 px gold strip + heavy gold cross-hatch filling the gap |

Corp tiers use the corp palette: I primary border, II secondary border, III the tier-III treatment
in the corp palette. Elite = tier II wheel, boss = tier III. The II line MUST stay ≥ 1.5 px on
screen.

### 3.8 State overlays (LOCKED, "ship it", round 15) and stacks
Reference: `round15_slice_system/states.png`, `states_fx.gif`; CORRUPTED port
`round23_combat_fx/fx_corrupted_storyboard.png`.

| State | Overlay | In game? |
|---|---|---|
| CORRUPTED | full-slice pink/green glitch: 5 tear bands ±6–20 px re-rolled every 83 ms, pink/green ghost split ±3–5 px, colour bands, 18 % scanline flicker, a tear line once a second | yes |
| ENCRYPTED | asterisks scrolling outward | yes |
| OVERCLOCKED | more translucent heat look, ×1.5 | yes |
| PARASITE | the large translucent bug only, legs crawling, body pumping (alpha ≈ 0.5), ×0.5 | yes |
| FROZEN | approved frost | placeholder (game Freeze is wheel-level) |
| LOCKED | padlocks scrolling left to right | placeholder |
| BURNING | approved flame | placeholder |
| EMPOWERED | huge translucent gold chevrons rising outward | placeholder |

- An overlay is its own layer under the read block; inside the read window it thins to 35 % or
  less (the wash stays ≤ 45 % overall).
- **Statuses are their overlay** (round 23). No standing rule chip.
- **Stacks (LOCKED, round 40):** a ×N ink tab, shown only when stacks > 1, rides a small flat corner
  badge in the **outer clockwise corner**; the ×1.5 / ×0.5 multiplier tags sit just under that
  badge (round 34). Hide ×N tabs at r < 150; the count also shows in the HP result chips. See
  Appendix C #1 for the conflict with round 23's "overlay only".

### 3.9 Firmware socket (LOCKED, rounds 33–34)
Reference: `round34_firmware_daemons/firmware_socket.png`, `firmware_set.png`, `firmware_trigger.gif`.
- **Chip:** the socketed die: a faceted octagonal die (3-tone facets), a gold pin comb on one edge,
  a DIP notch opposite, an LED in the rarity colour, 1–3 white rarity pips, the effect glyph upright
  on the dark top plate.
- **Placement:** on the slice midline in the hub-side band between the hub ring and the read
  block, rotated radially with **pins into the core**; master ρ ≈ 160 (R_IN 130, R_OUT 360), chip
  50 master px. Below r = 150: die, LED, pins and the rarity-coloured lip only, 0.9×. Enemy wheels
  use the same socket. Constants go in UI config.
- **18 effect glyphs** (never a slice glyph): Patch+ double plus; Hardened armoured hex with `***`;
  Burner gas ring; Leech fanged drop; Mirror ▶|◀; Shunt fork with two arrowheads; Overvolt bolt;
  Bulkhead blast door; Siphon pipe; Static Coat zig-zag shield; Barbed Wire; Recycler three-arrow
  triangle; Counterstrike ⇄; Nanite Mesh hex cluster; Power Cell battery; Tracer round; Skimmer
  coin stack; Coolant Loop radiator coil.
- **Socketing:** valid slots get lime focus brackets; invalid go greyscale 55 % dark and say "ATK
  ONLY"; an occupied slot asks an amber "REPLACE <chip>?" (destroy-on-replace is a proposal).
- **Trigger cue (one grammar):** LAND → FLARE (0.10 s: LED, lip and pins flash in rarity colour)
  → TRACE (0.18 s: a gold PCB trace runs **from the core outward** into the read block; for Mirror
  and Shunt it drops to a bus on the hub ring, runs along it, rises into the neighbour) → PAYOFF
  (a pip to the RAM bar, "+1 HEAT" in Heat orange, a heal or chip). Mirror shows a cyan phosphor
  ghost of the neighbour's read block; Shunt a lime outline + ×1.5; Hardened is passive (dashed link
  to the ENCRYPTED overlay); once/twice-per-combat chips go dark when spent.
- **Word:** "Firmware" everywhere (shop label too); "Microchip" is retired.

### 3.10 Inner ring
Reference: `round39_hub_inner_ring/inner_ring_v2.png`, `round40_hub_inner_ring/inner_ring_v3.png`.
- **Ring (LOCKED v2):** a machined annulus between hub and slices (master 100–127 on the D4 hub):
  outer and inner lips with accent hairlines, recessed gunmetal band, grooves with two bolts between
  three 120° segments, glass sheen; each segment has 10 ticks and its glyph on a small plate;
  the segment under the pointer gets an accent edge glow, others dim to 72 %.
- **Textures that extend into the outer slices (LOCKED):** each segment carries a texture across its
  band; when aligned under the pointer the texture extends into the outer slice it modifies, fading
  toward the rim and thinning under the read block. ×2 doubled gold hairlines; Pierce white chevrons
  streaming outward; Corrupt pink/green dead blocks climbing; Anchor steel chain links; Accelerator
  amber speed streaks; Echo cyan ripples; blank brushed steel (none). Under tier III the extension
  draws at reduced alpha under the inset line (tier wins at the screen edge).
- **Segment glyphs:** ×2, Pierce (arrow through a brick slab), Corrupt (glitched block), Anchor
  (anchor), Accelerator (gear + speed lines), Echo (block + two arcs), blank (dash).
- **Sub-needle (LOCKED as a direction; proposal mechanic):** the D4 cream blade at about 60 %,
  rooted on the ring's outer lip, pointing outward, turning with the inner ring; tip stops at the
  slice lip (r 152), clear of the firmware socket.
- **Hangar (LOCKED as a direction; proposal mechanic):** up to two drone pods dock on the slice rim
  side by side; beyond two show "+n".
- **At r = 60** the ring is lit/unlit colour bands only.

### 3.11 Satellites and drones
Reference: `round40_satellites/satellites_v3.png`, `replace.gif`; `round41_wheel_stack/drones_v2.png`.
- **Satellite = a docked mini-wheel:** the D4 frame scaled (0.22 of host since round 41), the
  owner's C slices, its own blade pointing **away** from the host, HP in its hub as a number + pips;
  values upright and large (glyph before centre, value after).
- **Dock (LOCKED):** centred on its slice's midline, outside the blade and HP arc. The slice's own
  outline swells out of the host rim in one smooth lobe (metaball of rim arc, waisted neck, collar).
  Two drones on one slice sit at ±14° so the blade passes between them.
- **Collapsed band (LOCKED, round 42):** by default each slice's drones collapse into one thin band
  (34 units deep), one tile per drone showing its current effect (glyph + value) and HP pips. No stem
  when a parasite is present, a short stem otherwise. **Hover bloom:** hovering the slice or aiming
  a card at a drone blooms the band into full mini-wheels with their needles. Bloom away from HUD
  controls.
- **Ownership tint:** each drone collar takes its owner's frame colour.
- **Rides spins and flips** with its slice (+12N° for a spin of N). Not nudgeable by default.
- **Bodyguard (LOCKED):** a pointer attack on a guarded slice bends to the drone: cyan guard arc,
  impact star, HP pips turn red. Pierce does not bypass.
- **Replace (LOCKED):** the new satellite hovers outside with a dashed amber "waiting" ring; the old
  one breaks into blocks and streams back to the host core as **green** bits; the core pulses green;
  the new one glides in. Red bits are kept for destruction only.
- **Destroyed (LOCKED, drone destroyed v3):** a shot bends to the drone; its own HP plate counts to
  0 (plate turns red, flashes); the hex splits with a shock ring and a binary-bit explosion; pieces
  pixelate and fall; no "DESTROYED" label.

### 3.12 Parasite ring (LOCKED option A + pop-up; boss mechanic is a proposal)
Reference: `round40_satellites/parasite_needle_options.png`, `round41_wheel_stack/parasite_popup.gif`.
- A thin partial third ring (about 90 master units deep) latched on **one** slice of **either**
  wheel, with 3 sub-slices that reuse real slice effects (e.g. SHIM 4 hits you, HOTFIX 6 heals the
  boss, DOSE corrupts). Violet fleshy rim with barbs, claws on the host rim, turn pips (3 turns).
- **Attached:** a thin band hugging the frame over its slice, glyphs only, while the needle is
  elsewhere and during any spin.
- **Popped (option A):** when the wheel settles with the needle on its slice it tweens out
  **beyond the needle tip** at full depth with glyphs and values; a beam links the blade to the
  in-line sub-slice, which fires. It drops back on the next spin. While a card is hovered, popped
  parasites on other slices drop back.
- It is never hit and never guards. Drones dock beyond it and move out with it.

### 3.13 Daemons (LOCKED, rounds 33–34)
Reference: `round34_firmware_daemons/daemon_set.png`, `daemon_row.png`, `daemon_trigger.gif`.
- A Daemon is a process the Cell keeps running: a unique **sigil** on a small CRT tile; phosphor
  colour = trigger family (2.6); rarity on the bezel (2.7). 24 unique sigils, none a slice glyph or
  card picto. Readable at 48 and 24 px; bare sigil at 16 px for tooltip rows.
- **Rack:** narrow CRT plate on the left edge beside the player wheel; 60 px tiles in install order;
  more than 6 → the 6th becomes "+N" and opens the tray.
- **Idle:** scan bar rolls (2.4 s, phase per slot), glow breathes ±12 %, heartbeat LED.
- **Fire (0.35 s):** white glass flash, sigil ×1.14 with RGB split, LED solid, a dashed packet line
  in the family colour to what it changes. Same-hook order: rack order, top-down, 0.12 s stagger.
- **Counters:** pips (Clean Signal 3, Cascade 2, Botnet Seed 2), a stack ("+N DMG"), READY/SPENT
  (spent = grey static).
- **Wheel-changing Daemons:** Twin Pointer = a second pointer in Daemon cyan at the bottom of the
  wheel; Botnet Seed = a 1-HP drone docked on the triggered slice. Zero Day, Stolen Intent, Linked
  Bus and the Mirror elite's "your Daemons" hub are not drawn yet (Appendix B).

### 3.14 Combat backdrop (LOCKED)
- **The backdrop is a close-up of the place being attacked,** authored in Blender with the Cv2 + E
  pipeline. Night is the reference; day is the **cool day** (round 11b grade) so orange targets
  separate from orange wheels.
- **Map = close-up rule:** the boss target **is** the corp HQ; the close-up uses the same HQ model
  and the same roads as the city map. Regular fights happen at smaller Sites that stand on the real
  road layout. A building that blocks the camera is removed from both the close-up and the map.
- **Framing:** zoomed in; the HQ fills the gap between the wheels and the wheels may overlap it.
  Blocks behind a wheel are kept low, dark and sparsely lit.
- **Per corp:**

  | Corp | Boss backdrop (HQ close-up) | Regular Site |
  |---|---|---|
  | Meridian | Camera faces the crane boom; crane centred between the wheels; a freight train runs left to right in front, takes a container and speeds off with streaks (20-frame loop) | container depot (DEPOT) |
  | Solace | Lit helix: underside down-lights, a centre up-spot, LED chasers spiralling up | SOLACE GENERAL hospital |
  | Halcyon | Civic Core; the eye sweeps ±55° with a translucent amber searchlight (dim it if it competes) | Halcyon Court with the Justice statue (eye blindfold, lit scales) |
  | Orbital | In-ground silo; doors slide sideways; rocket nose rises (combat uses the open state) | OC-TV broadcast station with dishes |
  | REBEL_CELL | **Tokyo street canyon**, darker so alley detail reads, detailed buildings, food/chip holograms, multilingual blade signs filled edge to edge, slow gentle animation (holds of 4 frames, 4 % dropout). **Home** lays low (no rebel signs); **DISPATCH** shows anti-human signage and the nearest right hologram is the red fist | the MAINFRAME shop (red sign) |

- **HQ-run nodes:** regular nodes (combat, event, shop) use their **dressed room backdrop**; the
  boss fight at the Central Server uses the HQ close-up.
- **Fight won:** the target building's lights recolour to the Cell (lime outlines, pink hazard
  stripes) while the district dims to about 62 %; a yellow pencil "OURS NOW" (round 32
  `reward_screen_v2.png`).

### 3.15 Heat on combat: H1 "the city reacts" (LOCKED, round 22)
Backdrop only, behind the wheels' darkened pools; never on the HUD or wheels.

| Band | Shows |
|---|---|
| NOTICED 25–49 | Three slowly turning red/amber alarm beacons on **side** buildings; nothing on the target |
| FLAGGED 50–74 | Two rooftop searchlights at the screen sides sweeping the sky **away** from the target, plus two alarm beacons **on** the target |
| HUNTED 75+ | Police light clusters (13) and two searchlights on the target. No helicopters, no siren wash |

- The full-screen **heat glitch** shader is an **Options extra only** (Settings › Accessibility
  `HEAT GLITCH`, off by default), with a protect mask so wheel discs get ≤ 35 % and the HUD is
  untouched. It needs a Settings field and a VfxTier exemption (Appendix B).
- A Heat crossing still pulses once on threshold events (GDD 9.4, STYLE_GUIDE 5.3).

### 3.16 Bosses and phases
- Boss = tier III corp wheel + banner-mounted crowned blade + threat ring + crest lugs + phase pips
  on the HP arc.
- **Phase change v3 (LOCKED):** HP crosses the pip → 120 ms hit-stop, white flash, the pip rings;
  the banner flips (scale-y through 0) to PHASE 2; orange bits stream **from the crossed phase pip**
  along under the arc to the bezel, and a crowned second needle extrudes with its value chip;
  `PHASE 2` and `2 NEEDLES` are temporary labels that dissolve to bits.
- Phase 2/3 corp treatments (round 14): P2 re-skin and a hot threat ring; P3 armour plates bolt on,
  screens overdrive, drones dock. The designer has not picked every corp's phase-2 treatment; keep
  the round 14/17 kits until told otherwise.
- Not drawn yet: Migrate flicker and Orbit trail on D4 (GDD 9.2), enemy entering.

### 3.17 Card-play preview (LOCKED, animated, round 17)
Reference: `round17_corp_wheels/preview.gif`, `preview_storyboard.png`; in the sticker flow
`round19_combat_fx/card_play_v2.gif`.
- Shown only while a spin or nudge card is hovered or aimed (or a nudge button hovered).
- **One** directional set: large ghosted **chevrons** outside the rim chase from the top needle to
  its landing, lighting in turn in the direction of travel (9 chevrons, 46 px, 900–1500 ms).
- **Ghost blades:** every needle gets a full dashed ghost blade at its landing, with its value
  window and index tab; the landing slice gets a dashed outline in its program colour.
- **Ghost drones:** a dashed ghost where each docked drone/satellite ends up.
- Labels ("1 LANDS HERE", "DRONE ENDS HERE") only while the card waits; the preview holds at 50 %
  through peel, drag and slap. No white trace lines, no aim pips, no arrowheads, no gates.
- On commit the ghost is re-parented to the rotating slices, so it meets the blade exactly as the
  wheel lands (**LANDED = PREVIEW**).

### 3.18 Sticker cards (LOCKED)
- **Frame:** C-C sticker card: white die-cut, gloss band, yellow cost dot, holo border for Rare,
  peel curl on hover. A thinner border (~5 px) at hand size. Can't afford greys the dot and adds a
  NEED tag. (The WHEEL / HACK / SYSTEM type band is not in the GDD; Appendix B.)
- **Play lifecycle (LOCKED, rounds 18–19):**
  1. Idle bob 2 px; corner curl breathes.
  2. **Hover:** lift, scale ~1.36, straighten, peel corner lifts, shadow grows; neighbours shift;
     the RAM meter hatches the cost; the preview plays.
  3. **Peel:** on press the fold sweeps, the sticker pops free; a faint liner outline stays in the
     slot.
  4. **Drag/aim:** spring lag, tilt by velocity; a yellow pencil line writes on from the card to the
     target; a pencil loop writes round a valid wheel.
  5. **Slap:** drop, squash 1.13/0.86, overshoot, settle; white contact ring and gloss sweep; RAM is
     paid here; the pencil wipes off stroke-first.
  6. **Dissolve A, the bit stream:** a scan front runs top to bottom; each 17 px cell decodes to a
     0/1 glyph (19–25 px, white-hot 80 ms), holds, then spirals **clockwise** into the hub along a
     Bézier; one faint trail copy; absorbed over the last 30 %.
  7. **Effect** (e.g. the spin with blur and a yellow tick trail on the telemetry ring).
  8. The hand closes the gap.
- **Rule:** every card-caused effect stems from the card's **slap point on the target wheel**; its
  bits leave from there, never from the hand. Effects no card causes keep their own source (slice,
  hub, turn start, enemy).

### 3.19 Precision landings (LOCKED, round 39)
Reference: `round39_landing_exploits/landing_perfect.gif`, `landing_good.gif`, `landing_weak.gif`,
`landing_storyboard.png`. Landings differ in **shape**, not only colour.

| | PERFECT | GOOD | WEAK (GDD "Partial") |
|---|---|---|---|
| Wheel | dead centre | 1° overshoot and back (clean click) | stutter +3.5 / −2.5 / +1.5 / −0.6° at 40 ms each |
| Needle | latch: two jaws clamp the tip (80 ms) | one white tick ring at the tip | grey sparks off the tip |
| Freeze | 2 frames + wheel-local inversion | — | — |
| Rail | gold `… // PERFECT // …`, one white pulse | white `GOOD` | amber `WEAK x0.5` |
| Slice | gold flash, gold 0/1 crown, class core flares (Perfect hook) | soft white flash | amber flash, slice dims 20 % |
| Word | gold `PERFECT` vinyl, 650 ms, then bits | small white `GOOD`, then bits | amber `WEAK` + `x0.5`, then bits |
| Sound | latch clunk, 2-frame silence, bright chime | one clean ratchet click | stuttered 3-click ratchet, low |

The OVERFLOW banner sits off the needle. The Miss slice is a slice, not a tier: static burst.
Reduce effects: no freeze, inversion or particles; rail recolour only. The inversion counts as a
flash.

### 3.20 Damage shards and combat FX (LOCKED list)
All FX use bits in the source colour, vinyl stickers for words and objects, additive glow with
light spill, and are held to their VfxTier (5.3). Every effect has a reduce-effects end state.

| Effect | Locked version | Tier | Key beats |
|---|---|---|---|
| Hit | `round18_combat_fx/damage_shards.gif` | T2 | comet tracer from the blade; slice flash ≤ 55 %, impact disc, 3-frame pixel tear; 0/1 shards in the attacker's colour burst from the hit point and curve **round the rim** into the HP arc; the number pops, rises, flies into HP; when you are hit, the drained arc segments flash white and *become* the shards, spraying away from the HP number |
| Crit | same | T3 | 3-frame hit-stop, RGB split on the wheel rect only, 7 crack lines, 7 code streaks (`0110 1001`) that shatter into shards, 4 px shake |
| Blocked | same | T2 | the DEFRAG wall pops between hit and wheel (outer side), ripples; dim shards bounce off; a few pass through |
| Block / shield gain | `round19_combat_fx/fx_block_shield.gif` | T2 | bricks pop in course by course on the side facing the enemy; hex plates tile out with a ripple |
| Heal | `round19_combat_fx/fx_heal.gif` | T2 | green `+`/1/0 rise in **from outside**, segments relight white → green |
| Evade | `round23_combat_fx/fx_evade_v4.gif` | T2 | `>>` token on the rim lifts early and flies up then left; the attack bends off and chases it; both fade at the screen edge; the wheel never moves |
| Apply CORRUPTED | `round23_combat_fx/fx_corrupt_apply_v4.gif` | T2 | slap, dissolve A, pink bits into the slice; the glitch takes the slice left to right (320 ms), doubled tears 500 ms; result = overlay only |
| CORRUPTED tick | `round23_combat_fx/fx_corrupt_tick_v3.gif` | T2 | flash + tear spike; glitch wipes left to right into pink/green bits that run round the rim to HP; a bolt cracks a RAM pip; the glitch writes back on |
| Nudge + resistance | `round20_combat_fx/fx_nudge_resist.gif` | T1 | strain 3° and spring back; RESIST chip cracks to grey bits; paid step 12° with a yellow 1-tick notch |
| Respin | `round23_combat_fx/fx_respin_v3.gif` | T2 | RAM pips crack into cyan bits to the hub; 2+ turns of blur; landing ring; temporary `RESPIN` (never CHECKPOINT) |
| Drone deploy / attack | `round19_combat_fx/fx_drone.gif` | T2 | bits stream to the dock and pack into the drone; attack = lens charge, mini tracer, S-tier shards |
| Drone destroyed | `round22_combat_fx/fx_drone_destroyed_v3.gif` | T2 | 3.11 |
| Phase change | `round23_combat_fx/fx_phase_change_v3.gif` | T3 | 3.16 |
| RAM gain | `round21_combat_fx/fx_ram_gain_origins.gif` (option **B**) | T1 | the TURN banner ticks over (cyan sweep); bits fall down the centre gap into the meter, 4 per pip |
| Enemy defeated | `round23_combat_fx/fx_enemy_defeated_v2.gif` | T3 | lethal hit-stop; cracks along every seam; the wheel cuts into slices, hub, ring chunks and banner that fly apart, pixelate and shed bits; hub shockwave; `DELETED` dissolves to bits |
| Player defeat | `round40_hub_inner_ring/player_defeat_v2.gif` | T3 | 3.3 |
| SEND IT | `round22_combat_fx/send_it_sticker.png` | — | states: hover (lift, curl, full gloss), pressed (squash), disabled (greyscale vinyl 80 % + RESOLVING chip) |

- **Temporary labels (LOCKED):** every word sticker or result chip from an effect (EVADED, RESPIN,
  PHASE 2, DELETED, PERFECT/GOOD/WEAK, −4 RAM, 2 NEEDLES) pops in, holds ~0.75–0.9 s, then
  **dissolves left to right into 0/1 bits** that drift up and fade within 0.5 s. One `TempLabel`
  scene.
- Severity scales shard count, size and speed (S/M/L/XL table in `round18_combat_fx/NOTES.md`);
  numbers in content config.
- The rest of the inventory (block expires, shield broken, pierce, flip, freeze, encrypt/overclock/
  parasite apply, cleanse, migrate/orbit, draw/discard/exhaust, rewind, lethal) is listed with
  motion ideas in `round19_combat_fx/effects_list.md` and is **not designed yet**.

### 3.21 Worst-case clutter rules (LOCKED stack, round 41)
Per-slice z-order, bottom to top: 1 slice screen · 2 ring texture extension · 3 tier inset · 4 state
overlay wash · 5 firmware socket · 6 sub-needle · **7 read block** · 8 state badge + ×N tab +
multiplier tag · 9 frame + telemetry · 10 dock lobes · 11 parasite · 12 drones · 13 needle blades ·
14 card-preview ghosts.

Radial zones (master units, player wheel): hub + inner ring < 127; sub-needle 122–152; ring
extension 132–182; firmware 142–194; read block 230–306; badge 300–352; frame 360–414; needle
336–510; parasite attached 420–462, popped 526–616; drones beyond.

Rules:
1. Drones collapse to the band by default; bloom on hover or aim (3.11).
2. Parasites stay attached until the needle settles on them; ghosts draw on top of everything and
   popped parasites on other slices drop back while a card is hovered.
3. The read block is always re-stamped on top; overlay wash ≤ 45 %.
4. One corner badge per slice (highest stack); full list on hover and in the HP chips.
5. Values that do not fit at r ≤ 90 move to the HP result chips.
6. HUD controls (nudges, HP chips, sticker) stay clear of wheel extras; bloomed drones mirror away
   from HUD controls; forecast space above the top slice may need 30 px more margin.
7. Hard limits (proposal): ≤ 2 drones per slice, ≤ 6 drones and ≤ 2 parasites per wheel.

The worst case (2 drones + parasite + status on every slice of both wheels, inner ring populated)
fits at 0 % off-screen with no HUD covered (`combat_worst_case_v4.png`).

---

## 4. City and campaign

### 4.1 The unified city (LOCKED v3, round 42)
Reference: `round39_city_unified/city_grid.png`, `round40_city_unified/raid_view_v3.png`,
`three_views_v3.png`, `round38_city_unified/zoom_through.gif` (scale proof only, not a gameplay
transition).
- **One model, one camera.** The City Grid, the raid view and the netrun transit are cameras on
  **one** city model built from the game's own layout (every street tile and lane colour, about
  14 100 individual building extrusions, plazas, the five locked HQs, the Cell district). Buildings
  are individual, never merged blocks. One orthographic iso camera (yaw 135°, pitch 40°); only
  target and zoom change.
- **Zooms:** City Grid ≈ ortho 440 with panning (edge chevrons, minimap terminal, DRAG / WASD, a red
  pencil edge marker for an off-screen TARGET); raid **fitted to the network** (owned nodes + entry
  Sites + panel margin), clamped (Appendix C #13); netrun transit fitted to the run map (≈ 130–190).
- **The City Grid shows all city life:** sky lanes, holo billboards, fog patches, rain, blinking red
  aircraft lights, full-strength street lanes, at round 39 brightness (the global lightening was
  reverted).
- **Translucency rule (raid and netrun views):** buildings go see-through by **view band** (ramp
  over lod 1.45–1.75): opacity 0.68, darkened ×0.86, chroma ×1.35, window glow +15 %; a thin
  outline. Ground, lanes and cars render under them. The network (nodes, links, threat lanes,
  units) draws at full strength through buildings; street lane glow drops to 28 %; sky lanes to
  35 %. Cars and defences are excluded from the see-through material. At the City Grid zoom
  buildings are solid and a hidden link shows through as a solid x-ray.
- **Building LOD:** always mass, taper, roof neon trim, window grid, territory tint, red crest
  windows, HQ heroes; from raid zoom the facet grid (~1.7 m), ledges, blade signs, pipes, AC, tanks,
  antennas, roof billboards, uplink pads and risers; transit-only shopfront glow and awnings.
- **Network decal by zoom:** City = single bright trace (~3 px) + halo, node = glow disc + tier ring
  + billboard pin with tier badge; raid/transit = 3-trace bus with vias and packets, full socket.
  Border and not-yet links are dashed. Minimum socket 22 px on screen at management zooms.
- **Car LOD (LOCKED):** FAR (ortho > 400) head dot + lane-colour line; MEDIUM (150–400) a small box
  filled in its lane colour, ~35 % translucent, same colour outline and line; CLOSE (< 150) the
  low-poly flying-car model (wedge body, dark cabin, lane-colour stripes, under-glow, head/tail
  lights) + a thick speed line. In the netrun transit the sky-lane car layer is off.
- Label avoidance is required at the grid zoom (tags collide with pins).

### 4.2 City motion (LOCKED, rounds 24–26)
Reference: `round26_city_motion/city_ambient_night_v4.gif`, `city_ambient_day_v4.gif`,
`round24_city_motion/motion_layers.png`.
Layers bottom to top: baked city → occlusion mask → street traffic (night head/tail streaks, day
small coloured cars) → **sky lanes** → holo billboards (illegible panels cycling with a wipe,
dropout, jitter) → aviation lights → fog banks (patchy, drifting, thin round labels and HQs) → rain
and steam (night rain only) → Heat props → tilt-shift → UI (never blurred).
- **Sky lanes v4:** 16 road shapes (double deck, cloverleaf, four-level stack, spiral ramp,
  flyovers) as lanes with no deck surface: fast cars with a light streak, dark body and under-glow,
  faint lane-guide dots; 14–20 car gaps per 3.84 s loop; each car picks one of six lane colours
  (pink, cyan, amber, violet, mint, orange) from a seeded stream, day and night; the white headlight
  stays at the nose.
- Day has no fog at raid zoom; tilt-shift and haze stay.
- All counts, speeds and periods live in the city config `.tres`; randomness from a seeded
  `RngService` stream.

### 4.3 Heat on maps
- **City Grid / netrun (LOCKED Heat B, calm, rounds 35–37):** the number lives on the operative
  dossier stamp (`HEAT 52: HUNTED`); city-wide two slow searchlight sweeps; each node Heat has made
  harder gets one soft circling red/blue light on a thin dark-orange (`HEAT_B`) ring plus its
  effect chip (`HEAT: +1 ELITE`, `HEAT: +1 RESISTANCE`). Only selectable nodes carry markers.
- **Raid:** the band's rigs (choppers on circular orbits with wobbling spotlights, drones with mini
  spots, strobes) are set at raid start and **padlocked**; nothing escalates mid-raid. EXPOSED (a
  spotlit node takes extra damage) is a locked visual for a proposed rule.
- Round 24's map Heat (alarms → searchlights → police, choppers, drones) remains the language for
  the HUNTED city if the campaign map shows bands.

### 4.4 HQs and the REBEL_CELL district (LOCKED)
Reference: `round26_hq_targets/hq_*_close_*.jpg`, `round27_hq_targets/hq_meridian_*`,
`round31_meridian_combat/combat_meridian.jpg`, `round34_rebel_cell/*`.
- HQ landmarks per 2.4 and 3.14. Meridian keeps texture A (raw corrugated steel, Meridian orange),
  lower walls, a faceted moat, the gantry crane keep with the boom, rail yard and freight train;
  angular, no round shapes.
- **REBEL_CELL district (LOCKED, round 34):** a normal street grid; no fist roads, no painted roofs,
  no holograms on the map. The fist is drawn in **red windows**: a tucked-thumb fist (finger splits,
  thumb upper edge, thumb tip, a half palm line on the right, the vertical tucked-thumb line),
  toned down (home 70 % red-window density, DISPATCH 90 %); its detail lines are buildings with no
  windows. The label sits below the fist.
- **Blackout reveal:** the sector starts fully lit and washed out; then the blackout ring and the
  hand's lines go dark and the fist appears (`map_fist_reveal.gif`).
- **Home vs DISPATCH:** two versions of the district and the canyon (3.14). The Cell's HQ room is
  **dropped**; HQ actions need another representation (Appendix B).

### 4.5 Site markers v4 (City Grid)
Reference: `round42_site_markers/site_markers_v4.png`, `site_markers_on_map_v4.png`. One marker,
five layers:

| Layer | Answers | Look |
|---|---|---|
| Pad (raid socket) | ownership | corporate dark pad, orange pins; claimed = Cell lime node; cleared = grey |
| Icon disc (normal colours) | kind | regular = corp crest; **Exploit Site = gold keyring plate + type sub-badge** (INTEL magnifier, BREACH sledgehammer, VIRUS the INFECT glyph; badge radius 0.31 of the disc); Heat objective = dark-orange flame; claimed = **lime rebel fist, thumb tucked**; CORE = lime heart |
| Ring | availability | white = not yet, orange = selectable, lime = yours/visited |
| Pips (1–3 squares) | tier | gold on Exploit Sites; the boss (T4) has none |
| Corner badge | status | CLEARED grey check (PATROL on hover) |

- **DISABLED:** a white lightning bolt across the whole marker, everything greyed.
- **SEIZED:** an intercepted corp **SEIZURE NOTICE** slip (pale paper, violet hatch, violet
  letterhead with the corp mark, red SEIZED bar) replaces the node circle; tier pips stay, in violet.
  An orange ring shows while a Reclaim run is possible.
- **De-powered links:** every link to a seized or disabled node is a dim grey double trace with a
  break in the middle.
- **Locked cross-link:** grey dashes + a padlock disc at the midpoint.
- **Boss:** the HQ landmark with the red pencil **TARGET** circle and the
  `CENTRAL SERVER // EXPLOITS n/3` chip, placed clear of the pencil.
- **Pinned (always shown):** Exploit and Heat-objective Sites (at 90 %, white rings), your nodes,
  cleared and seized Sites, the boss. A plain-language legend says what each icon means.

### 4.6 Netrun (LOCKED hybrid D)
Reference: `round37_netrun/*`, `round38_netrun_transit/transit_v3.png`, `transit_step_v3.gif`.
- **Structure:** Site runs are a **transit** along the border link from an owned node; the HQ boss
  run is the overhead **compound** (4.7); raids stay on the city map. A run goes from any owned node
  to any unowned node across a border link; no planning UI; no cap on choices; nodes are never
  revisited.
- **Node states (option A, LOCKED):** node-type stickers keep full colour; one outline ring carries
  the state: **white** not yet available, **orange** selectable, **lime** visited/walked, dim grey
  cut off. On the transit, the next options are numbered.
- **Hidden nodes (LOCKED):** by default only owned/visited, selectable and the TARGET are drawn
  (plus the pinned Sites of 4.5); hovering the legend strip ("HOVER HERE: SHOW ALL NODES") shows all;
  hovering empty map reveals the node under the cursor (~40 px, 0.15 s fade); Options › Map "Always
  show all nodes".
- **Transit paths v3 (LOCKED):** network cable runs between the buildings of the adjacent blocks:
  straight segments with 45° or 90° turns only, crossing streets rather than riding them; the walked
  path is a **solid** lime line; available (orange) and not-yet (white) paths are dashed; crossings
  avoided, the rest bridged with a hop; ~7 layers, 15–20 nodes; the lighter city grade.
- **Panels:** the operative **dossier** is corp paper (AT LARGE stamp by the name, Heat stamp); the
  node info window shows only tier, type and rewards, and only when decrypted; the TARGET keeps its
  red pencil circle; DECK and MENU.
- **Transition (LOCKED, ~4.4 s, skippable):** JACK IN → the Cell's terminal types
  `jack --from RELAY_4 --to DEPOT_15`, routing, handshake → CONNECTED, binary rain along the chosen
  link only → the terminal window despawns as a CRT collapse (line, then dot) → the operative's wheel
  slaps onto the link and spins up → **wheel lens**: the hub opens onto the transit view and the ring
  flies past the camera. Beats 1–3 can shorten after the first runs (setting).
- **Node backdrops:** a dressed room per HQ node (desk/screen-wall Terminal room etc.).

### 4.7 HQ runs: the compound and unique mechanics (LOCKED "good for now", round 43)
Reference: `round43_hq_mechanics/hq_<corp>_compound.png`, `hq_<corp>_mechanic.gif`.
- Overhead compound at the city azimuth, 55°; nodes sit on real buildings and moving parts; the
  Central Server is a real place (THE MASTER MANIFEST, THE GENOME CORE, THE PANOPTICON, LAUNCH
  CONTROL; DISPATCH CORE). Red ring = danger/locked.
- **Link change grammar:** links that change **de-power** (dark red with sparks, 2 frames) and are
  **re-made** (drawn on from their source with a bright head, 2 frames), even when they reconnect
  to the same place.
- **Meridian:** 6-step crane/train cycle; the next container to move is telegraphed one step ahead
  with a yellow pencil ring ("NEXT: ONTO THE TRAIN"); the train stays one full turn; the crane moves
  containers both ways; paths run along the walls.
- **Solace:** two helix strands, each its own node chain (semi-random sets, not "all elites"); three
  crossover walkways are the only switches; the camera orbits to keep the player centred; goal is
  the top. No spinning.
- **Halcyon:** switchback pyramid (6, 5, 4, 3, 2, 1); gold shortcuts 4>9, 9>13, 13>17, 17>20, at most
  2 used; the eye watches one half plus the centre column each step; entering a watched node =
  SPOTTED.
- **Orbital:** a repeating loop cleared every lap; the missile bay prep bar fills; sabotage 3
  missiles (red X tally); lap 4 bypasses the platform and the 4th launch destroys the base.
- **DISPATCH:** **Sync Strike** finale (3 runners hit 3 locks on the same step) and **mirror
  combats** (your own slices and firmware) through that chapter.
- All mechanic rules are proposals for the GDD (Appendix B).

### 4.8 Raid (LOCKED, rounds 19–23, re-run on the unified city in round 40)
Reference: `round39_city_unified/raid_view.png`, `round40_city_unified/raid_view_v3.png`,
`round40_city_unified/raid_gifs/` (index.md), `round22_raid_ui/node_status_key.png`.
- **Network on the street = circuit inlay (C):** sockets with frame, pins, pin-1 notch, glyph and
  integrity; **lime links** (3-trace bus with vias and moving packets). Risers run from the socket
  into the node's building and up the facade to a **B uplink pad** on the roof (the pad face is the
  socket's twin; a lime beacon mast at its corner).
- **No node tags.** Type = socket glyph (Relay all-targets arrows, Firewall, Vault safe door,
  Proxy fingerprint, Safehouse key, CORE pink hex; seized = the corp citation glyph). Status = frame
  colour + pattern: holds solid green (owned sockets shift from map lime to "holds" green), disabled
  dashed amber with dark pins, seized violet hatch, TAKEN burnt. Forecast = a dashed outer ring in
  the projected outcome colour.
- **Node health v2:** the outline and icon stay lit; only the inner lit fill drains **north to
  south** with a faint hatch and a bright drain line; at 0 it switches to disabled amber dashed.
  Numbers float above the north point on hover (or Options "Always show node health"): numeral +
  10-segment bar, lime/amber/red. Repair raises the fill south to north with a count-up and rising
  "+" sparks.
- **Panels by fiction (option E):** YOUR NETWORK = CRT terminal with status chips; RAID INCOMING =
  intercepted work order (memo under glass, corp letterhead, redactions, INTERCEPTED); THREAT INTEL
  = decrypted holo with the corp seal cracked + DECRYPTED and scanned vehicle silhouettes
  (NOT-DECRYPTED variant is a proposal). Panels re-skin per raiding corp (one corp theme resource).
- **Speed/Skip:** the terminal strip **below START DEFENSE**; START peels away in playout and the
  strip stays.
- **Pencil rules:** red pencil routes along the real streets (solid = active route, dashed =
  what-if; A/B/C circles at entry Sites). DECOY preview: the abandoned part is scribbled through and
  the new route drawn dashed; on placement the old part is cloth-wiped and the new route drawn
  solid; no re-route during execution unless the decoy is destroyed (route reverts). State marks
  (INCOMING, DOWN, TAKEN, wave cleared) write ~0.4 s, hold ~1.5 s, wipe ~0.4 s. TAKEN is normal
  weight above the node, then wipes and the node is removed. **BREACHED** stays: one slow heavy
  wax pass with an underline, a red bit explosion at CORE, links de-powering segment by segment.
- **Card drag model:** the defence sticker peels and **parks** just above its hand slot (no outline);
  a yellow pencil arrow draws from it to the cursor; within ~95 px of a node the arrow stops just
  outside the node's circle and the circle draws (yellow = valid with the IF PLACED terminal; red
  circle + X = invalid with NO SLOT); leaving erases the circle and the arrow snaps back. Remove to
  hand = click the node; swap = one motion with a truthful cursor path.
- **ICE:** light-blue translucent fill, crisp blue rim, blue/white crystals growing inward from the
  border; on frozen links and units encased in ice.
- **Threat vehicles (LOCKED models + icons v4):** corp silhouette families (Meridian freight boxes,
  Solace white capsules, Halcyon police wedges with violet rim and amber bars, Orbital hover pods,
  REBEL_CELL scrap mirrors). **Icon:** SHAPE = type (FAST chevron badge `>>`, HEAVY block, SPECIAL
  hexagon with its verb glyph, FLYING diamond with four rotor circles and a 2×2 circle glyph; Orbital's
  special is the lander DROP); FILL = corp colour **= health**, draining top-down with a white line;
  RING = dashed corp circle ~1.8× the icon carrying status pips clockwise from top right (slowed,
  frozen, burning, exposed, corrupted) and, on hover/selection only, the yellow heading arrow;
  UPGRADED = two white chevrons + double rim. On the street a filled disc under the unit drains the
  same way. Models close, icons far (swap with hysteresis, hold [V] for models).
- **Operators:** stationed operatives show as **R3 class beacons**: a cone opening up from the
  Safehouse pad to a cap ring, the class emblem as a scanlined holo with no light behind it, one idle
  per class (Rigger blinks and sometimes scowls). Station-bonus FX: Breaker damage aura, Ghost slow
  field drawn **under** the units (dashed rings drifting inward; levelled = ice crystals), Rigger
  repair; alternates are proposals.
- **Raid report:** the raiding corp's own **after-action report** (paper, CLASSIFIED stamp) with
  the Cell's pencil on it (circles, RIP, ticks) and CELL HOLDS slapped on top; Heat settles here.
- **Campaign lost (option A, ransomware lock):** the winning corp's house style and verb
  (PROCESSED, RECLAIMED, TREATED, DE-ORBITED, OVERWRITTEN), every node padlocked, a countdown to the
  wipe; the Cell's stickers curl and drop off. **Campaign summary** = the corp's audit dossier
  (manila folder, typed AUDIT REPORT, CASE CLOSED, personnel sheet with DECEASED / AT LARGE,
  polaroids, auditor post-its in blue ballpoint); NEW CAMPAIGN / MAIN MENU are stickers.

### 4.9 Exploits and the Central Server breach
Reference: `round38_landing_exploits/exploit_items.png`, `central_server_gate.png`,
`central_server_breach.gif`; `round39_landing_exploits/exploits_v2.png`, `exploit_on_map_v3.png`.
- **Item = a vinyl keycard** (whole rounded rectangle, corp band across the top with a category chip,
  gold contact pad, kind word, item name, one-line effect). Kind = icon + backing shape (reads in
  greyscale); corp = tint band. HUD chip 56 px; top-bar `EXPLOITS n/3`.
- **Gate (LOCKED look):** boss wheel in front of its dimmed HQ; a CENTRAL SERVER panel with 3
  keycard sockets (+ 2 dashed extras); each Exploit slaps into its socket, the socket rings in the
  corp colour, then its bits stream from the socket to the wheel and the effect lands (INTEL: ghost
  needles and orbit arrows revealed; BREACH: the ghost needle is crossed out and shatters; VIRUS:
  slices taken by the CORRUPTED glitch). At 3/3 the grey BREACH vinyl over `CONNECT` turns pink.
  The gate preview equals the fight start.
- **Expanded set (LOCKED as options):** one Exploit per boss power-up, in categories INTEL, BREACH,
  VIRUS, ROOTKIT, HIJACK, CIPHER (e.g. CUT A HEAD, ORBIT LOCK, ROLLBACK, HUB DOWN, TURNCOAT,
  SCRAMBLE). Exploits sit on **T2** Sites.
- **On the map:** each T2 Exploit Site shows only a small badge (category icon on a gold-ringed node,
  T2 tab); the full tag is a hover tooltip; nothing covers pencil.

### 4.10 MAINFRAME shop
Reference: `round33_mainframe_sign/mainframe_blue_v4.png`, `mainframe_red_v4.png`,
`mainframe_sequence_v4.gif`, `iamai_sequence_v4.gif`, `iamnoman_sequence_v4.gif`;
`round12_modem_facade/f1b_*.png`; `round34_firmware_daemons/shop_v5.png`; `round33_shop/*`.
- **Exterior:** the **F1b Tenement** facade (one-point street view, alley stair, two wall-to-wall
  cables, front building with roll shutters) with the vertical sign.
- **Sign (LOCKED v4):** **MAINFRAME**, filled neon tubes (saturated body, thin hot centre line,
  unlit tubes as dark glass) on a circuit-board plate; three trace weights (3.4 / 2.4 / 1.3 px),
  6 px pitch, 45° bends, ring pads, vias, varied components; every trace belongs to a letter and
  lights with it (lit letters' traces carry pulses into the tube; dead letters' wiring is dark
  copper). Normal = blue with blue spill; REBEL_CELL = red, fully lit.
- **Takeover sequences (LOCKED):** NO → MoRE → MAN (`N3 A6(o)` / `M0 A1(o) R5 E8` / `M0 A1 N3`),
  I AM → AI, I AM → NO → MAN. An `A(o)` lights only the top half (shoulders, top bar, crossbar) and
  its legs go fully dark. Unused letters get snapped tubes and soot; spill drops to ~10 % during
  words.
- **Interior:** the clerk screen sits under the sign plate; a grease-pencil note ("ask about the
  back room") replaces the old MODEM sticker; pegboard with kraft price tags and label-maker tape
  sections; FIRMWARE chips pushed pins-first into pink anti-static foam; DAEMONS as tiles in
  cartridge housings on hooks; unaffordable tags print red with a pencil "can't afford"; a colourful
  holographic LEAVE sticker with a pink chevron arrow.
- **Slice wheel (LOCKED option B):** a 12-slice stock wheel mostly offscreen (hub ~170 px below the
  screen), spins once on entry (seeded, sets a checkpoint), eases out ~1.5 s; **no needle** — the top
  slice's price tag hangs where the needle would be; the 3 slices for sale are full brightness with
  yellow arcs and kraft tags tied to their rims; the rest greyscale, darkened 60 %, padlocked.
- **Removal (LOCKED): the RECYCLE BIN** on the sidewalk: drop a card or slice; the lid flaps open,
  the sticker crumples into a faceted toon-shaded ball, drops in, lime/pink bits fizz, the lid slams;
  a count badge; natural sound cues (clank, crunch, fizz, slam, tick).

### 4.11 Rewards, Server Rack, events, dialogue
- **Reward (LOCKED A):** offers peel from a **loot sheet** (sticker liner with kiss-cut slots); the
  taken slot stays as a shiny empty outline; entrance = bits assembling (dissolve A reversed); the
  pick flies to DECK. Firmware drops show a mini spinner with lit valid slots. PAYOUT on CRT.
  Reference `round31_reward_event/reward_screen.png`, `reward_reveal.gif`, `round32_shop_reward/reward_screen_v2.png`.
- **Server Rack:** `round31_reward_event/server_rack.png` is in progress; its "flash" upgrade/swap is
  not a GDD rule.
- **Events (LOCKED as drawn):** the story in a CRT Terminal tinted the corp colour, a CAM feed in the
  world style, choices as sticker buttons with outcome chips (green gain, red cost, grey no change);
  a corp-speaker event gets an intercepted memo taped over the Terminal; after the pick a CHOSEN
  stamp. At most one pencil slogan. Full design pass later.
- **Dialogue (LOCKED A):** a low-poly cel **bust on a CRT comm feed**; the speaker is live, the
  listener dimmed. **DISPATCH never gets a face:** a red voice trace on black, "VOICE ONLY // NO
  FEED".

### 4.12 Portraits (LOCKED v2)
Reference: `round39_portraits/portraits_classes_v2.png`, `round38_portraits/portrait_states.png`,
`portrait_contexts.png`.
- Cv2 facets + E toon + inverted-hull ink busts with a class-colour rim; procedural rookies from a
  seed (skin, hair, jaw, beard, one gear swap) stored on the operative.
- **Class gear:** Breaker hood + visor bar (no chin piece, no beard); Wrecker respirator + shoulder
  pads; Ghost ninja wrap with an open eye band and a cyan headband; Phantom full mask with
  downward-pointing triangle eyes and vents; Rigger goggles inline with a level band (up or down);
  Overclocker slot goggles + heat-sink fins; Botnet antenna + hovering ico-drones; Hivemind hex
  circlet + a square lens on an arm.
- **States:** idle (scanlines, slow blink), talking (mouth swap + voice bars), hurt (HP ≤ 25 %:
  grimace, red wash, torn bands, cracked glass), stationed (class-colour monochrome 12 fps, "ON
  <SITE>"), flatlined (static, NO SIGNAL, red pencil X, FLATLINED), recruit (greyscale, HIRE stamp).
  Triumphant is deferred.
- **Contexts:** crew roster CRT rows; corp dossier photo print (desaturated, paper-clipped, red pencil
  ring); audit polaroids; contacts (fixer cyan, street merc amber).

### 4.13 UI kit, title and settings
Reference: `round33_ui_chrome/ui_kit.png`, `typography.png`, `title_screen.png`/`.gif`,
`abandon_dialog.png`; `round31_ui_chrome/settings_menu.png`, `city_map_hud.png`.
- **Title (LOCKED option A, "the plan"):** the REBEL_CELL neon tube sign over the living night city;
  three numbered stickers with plain labels on terminal chips: **1. BREACH** (pink, default focus) =
  CONTINUE + slot summary; **2. SIMULATE** = TUTORIAL ("a practice run in a simulated net"),
  lettering with the CORRUPTED glitch inside the letters (bursts twice per loop); **3. OVERTHROW** =
  NEW CAMPAIGN, readable blue with the last O a red rebel fist. The rest in a terminal MORE panel
  (CAMPAIGN SLOTS, CODEX, STATS & ACHIEVEMENTS, OPTIONS, QUIT). Idle: cursor blink, E stutter, a
  two-frame drop to "CELL", ticker.
- **Abandon dialog:** terminal body with GDD costs; yellow CANCEL (default focus) and pink BURN IT
  (pad hold-to-confirm 0.8 s is a proposal).
- **Components:** terminal panel (chamfered corner, `> TITLE` header), terminal buttons (`>` caret
  on hover, no colour-only cue), holo panel, paper panel (9-patch), vinyl sticker buttons (baked per
  locale at 2×; hover scale 1.05 + gloss sweep, pressed squash, disabled greyscale 80 %, focus lime
  halo), 9-slice name plates. Tooltips: terminal header (name, value, type tag), glyph-tile rows
  (26 px) and Plex text, a key-hint row, 350 ms delay. Toasts: plain cyan terminal; refusal `HARM`
  edge + no-entry mark; corp news = holo strip; 2.4 s at the foot.
- **Settings:** terminal; every switch from `settings_panel.gd`, plus HEAT GLITCH (preview + LIMITED
  chip while flash limiter or reduce effects is on) and Map › "Always show all nodes"; text-scale
  slider with a live sample; colour-blind tiles; resolve-speed tiles.
- **City Grid HUD (in progress):** THE GRID title sticker, terminal resource strip, Heat, crew,
  map key, selected Site as holo, IF CLEARED terminal, RAID PENDING + RAID SETUP, JACK IN sticker.

### 4.14 Not designed yet (do not improvise; Appendix B)
Card illustrations (71), rarity on cards, event illustrations (124), enemy busts and mini-bosses,
new-campaign page, campaign slots, codex, stats/achievements, pause, run end (JACKED OUT /
FLATLINED / HOME FELL screens), campaign WON, tutorial overlay, HQ actions, home-server variants,
built-in defences, Tar Pit/Honeypot structures, node upgrade levels, RAID INCOMING warning, Armory,
netrun complications, Flip/Freeze/three-pass resolution FX, Bug card. Until designed, keep the
current game look and log the gap; never mix in rejected media.

---

## 5. Accessibility and motion

### 5.1 Never colour alone
- Every slice has a glyph; every status a badge shape; every tier a structure change (line, then
  filled band); every vehicle a shape per type; every node a glyph; every Heat band its word; Daemon
  families a sigil + tooltip; Exploit kinds a backing shape.
- **Greyscale check** for every screen and every new set (the round sheets show greyscale beside
  colour). **Colour-blind check** with Machado 2009 (protan, deutan, tritan) in linear RGB; report
  ΔE for any pair that carries meaning. Known close pairs: Daemon PERFECT/RUN and RUN/HEAT (shape cue
  per family is the next step if needed); Phantom/Botnet resolved by lilac vs indigo.
- `Settings.colorblind_mode` applies a daltonize correction (v1 §16 item 5 still open).

### 5.2 The 16 px glyph rule
Any glyph, sigil, emblem or icon MUST identify by outer silhouette at 16 px with soft IoU < ~0.68
against the whole atlas (slice glyphs, pictos, statuses, hub emblems, segment glyphs, firmware
glyphs, Daemon sigils, Exploit icons). Known borderline: STORM/HP and ESC/BLOCK 0.67, Phantom static
icon/CITATION 0.69 (animated hub unaffected), Corrupt segment/Ghost core 0.66.

### 5.3 VfxTier (kept; `scripts/ui/fx/vfx_tier.gd`)

| Tier | Examples | Coverage | Max duration | Flash | Shake / hit-stop |
|---|---|---|---|---|---|
| T0 ambient | city life, Heat lights, sign flicker, idle loops | backdrop | loop ≥ 3 s period | none | none |
| T1 feedback | hover, nudge, RAM gain, number bump | element + 16 px | 0.25 s | +20 % glow | none |
| T2 outcome | hit, block, heal, evade, status apply/tick, drone, respin, card play | element + 25 % region | 0.6 s | 60 % local | 2 px, 2 frames |
| T3 moment | crit, Perfect, phase change, enemy defeated, player defeat | region | 1.2 s | 70 % local, never full screen | 4 px, 3 frames |
| T4 cinematic | jack-in transition, Central Server breach, campaign end | full screen | 2.5 s (skippable) | 40 % white once | camera move |

- No full-screen colour flash below T4. Flash limiter ≤ 3 flashes/s globally; a denied flash skips
  the flash and keeps the particles. Batch per-frame segment flashes.
- The Perfect inversion, MAINFRAME stutters and title drops count as flashes.
- The heat glitch is full-screen but adds no light: register it as an exempt post layer, gated by
  its own setting (Appendix B).
- The netrun transition (~4.4 s) exceeds T4's 2.5 s: it is skippable by any press and its first
  beats shorten by setting (open question: exempt it or split it into beats).

### 5.4 Reduce effects and reduce motion
- **Reduce effects** (`Settings.reduce_effects`): no particles, streams, bursts, flashes, shake,
  hit-stop, tears, RGB split, scanline roll or flicker. End states at once: HP set, a static −n chip
  beside HP, walls/hexes/drones/badges appear with a 1-frame outline, the defeated wheel fades to
  grey in 300 ms with its sticker, wheels step to their end rotation in one 120 ms tween, card play
  slides 150 ms and fades. Static scanlines on CRT panels may stay.
- **Reduce motion** (`Settings.reduce_motion`): no camera moves or parallax; no hand bob, drag tilt
  or squash; no shake or hit-stop; numbers appear beside HP instead of flying. City: traffic at 40 %
  with no streaks, billboards hold one panel, fog static, rain becomes a static wet sheen, steam off,
  sky-lane markers without cars, steady aviation lights; Heat lights steady (no rotation or strobe,
  never above 3 Hz), searchlights fixed, choppers and drones parked.
- Every motion value lives in `content/config/ui_motion.tres` with its tier; STYLE_GUIDE 5.1 press
  and skip rules (ANIM-R1–R4) apply to every new motion, including the netrun transition, raid
  playout and shop wheel spin.

### 5.5 Heat glitch option
`HEAT GLITCH` (Settings › Accessibility) is off by default and only ever an extra. Off = static
corp edge tint at HUNTED only. Under reduce effects: tears only at NOTICED strength, at most one
burst per 3 s. Flash limiter on: the COOL luminance dip is skipped.

### 5.6 High contrast and text scale (kept)
- **HighContrast** (`scripts/ui/kit/high_contrast.gd`): opaque #000 panels (no glass, blur or holo
  transparency), `TEXT_HI` at 7:1, solid button and focus edges. Paper keeps its stock with `INK`
  at 7:1 (`PaperInk`). Holo panels become opaque corp-tinted terminals. Stickers keep their baked
  art; their labels must already meet 4.5:1.
- **Text scale** 1.0–2.0: nothing clips, overlaps or truncates; wheels stay ≥ 70 % of their 1.0
  size; baked sticker words scale as objects and shrink-to-fit their slot.
- Contrast minimums (v1 §3.7): 4.5:1 for anything read, 3:1 for large text and meaningful icons.
- Pad: every drag has a button path; focus visible from 3 m; glyph sets per controller.

---

## 6. Asset production notes (Godot 4.7)

### 6.1 World and city
- **Blender pipeline (offline):** Blender 5.2 headless, Eevee; triangulated facets with tone jitter;
  3-band toon ramp (separate day-cool and night palettes); post pass in the round scripts for ink
  (from id/normal/depth), grime, bloom, light spill, haze, rain. Bake HQ close-ups and Site
  backdrops per corp, day and night, plus loops (Meridian crane/train, Solace chaser, Halcyon eye,
  REBEL_CELL canyon signs).
- **`CityModel` resource:** baked from the layout table, seeded per campaign: one MultiMesh per
  building family (~6), street mesh with a lane-colour vertex attribute, prop MultiMeshes, HQ
  scenes. LOD0 within the raid frustum, LOD1 (mass + window emissive) elsewhere, LOD2 extrusion.
  Visibility by camera ortho `size`, not distance.
- **One orthographic `Camera3D`**, size tweened log-linearly; UI layers swap on `lod` thresholds
  with hysteresis; no scene change between grid, raid and netrun.
- **Building material:** a uniform `opacity` driven by view band; below 1 it switches to
  alpha-blended with the depth pre-pass off; `albedo *= mix(1.0, 0.86, 1 - opacity)` (v3 values).
- **Network = one ground decal shader:** node buffer (position, state enum, glyph index, tier,
  integrity, exposed), link polyline buffer (points, state, packet phase), `lod`. X-ray = a second
  pass with depth test GREATER (solid at city lod). Prototype `post36.Net36`, health
  `netdecal21.health_pad`.
- **Traffic and sky lanes:** a Path per lane with an elevation curve; cars in a MultiMesh moved in
  the vertex shader along a baked position texture; per-instance colour from a 6-colour config
  palette via a seeded `RngService` stream; car LOD = three MultiMeshes per lane colour.
- **Fog:** two scrolled noise samples × keep-mask × vertical gradient; `textureLod(screen, uv,
  density × max_lod)`. **Tilt-shift:** last post pass with a band mask. Bloom via 2D HDR glow on
  additive layers only. Half resolution on low settings.
- **Pause** every ambient layer when the map is covered or the window unfocused.

### 6.2 Wheels
- Wheel = `Node2D` with a rotating `Slices` node: one `Polygon2D` wedge per slice with a shared corp
  `ShaderMaterial` (batching), per-slice uniforms (`slice_color`, `span_deg`, `r_in`, `r_out`,
  `screen_tex` flipbook, `tier`, tier table from config, `bezel_material`, `hit_flash`,
  `tear_seed`, `tear_amount`, `invert`). Distance fields `e_scr`, `u`, `v` port from
  `slicekit.geom`.
- Overlay = a sibling `ColorRect` padded ~34 master px with its own shader (`state`, `read_center`,
  `read_radii`, `seed`, `wipe_x`, `spike`); CORRUPTED reads `hint_screen_texture`.
- Read block = glyph `TextureRect` + value `Label`, counter-rotated (`top_level` rotation 0).
  Corp scene flipbooks sample screen-aligned UV with the same counter-rotation.
- Glyph atlas: MSDF/SDF from `round17_slice_system/glyphs/` in 128 px cells (`index.txt` order),
  one CanvasItem shader (fill at smoothstep 0.5 ± aa, outline `#0C0A16` width 0.075). One atlas
  covers 16–64 px. Hub, segment, firmware, Daemon and Exploit glyphs join it.
- Frame nodes: baked `Bezel` + shadow per corp, `TelemetryRing` (scrolling text shader) + `Rail`
  (masked arc with `rail_half_angle`, `rail_colour`, split around needles), `Blade` ×n with index
  tabs, `EliteCollar`, `ThreatRing` (negative rotation), `ArmourPlates`, `Crest` ×2, `Banner`.
- Hub: `Control` with a CRT shader (`accent`, lockdown `level` + scrolling glyph-atlas mask),
  emblem, two labels, `MK2` tab. Inner ring: independent `Node2D`, annulus shader
  (`seg_type[3]`, `active`, `ring_rot`) + extension wedge under the read block.
- Satellites: `Satellite` scene under a `DockPoint` child of `Slices`; dock lobe = one shader shape
  tinted `type_color`; `SAT_K`, dock offsets in UI config. Parasite: `ArcSegment` on the dock point.
- `PreviewOverlay` fed by the forecast's landing ticks (same code path as the forecast, so preview =
  result); chevrons with staggered modulate; dashed ghost sprites re-parented on commit.
- Firmware chip: children of the slice node after the overlay, before the read block; LED as an
  additive sprite; trigger via `firmware_triggered(slot, effect)` signal; trace = `Line2D` with a
  tweened gradient offset.

### 6.3 FX
- **Bits:** one pooled `GPUParticles2D` per burst in `CombatFxLayer`; 0/1 (+ `+`, blank, bit-rot)
  atlas from Share Tech Mono with a ~1/22 outline, `particles_animation`; additive blend, one pass
  only. Stock attractors are 3D, so a small **particle process shader** lerps each particle along a
  quadratic Bézier (control point on the rim-side bisector at 1.5 × R_out, so shards go round the
  wheel). `CPUParticles2D` fallback (≤ 44). The view **precomputes arrival times** to schedule HP
  ticks, segment flashes and lag drains; it never reads particles back and never changes state.
- Dissolve A, `TempLabel`, card dissolve, corrupt wipe and lockdown all share the emitter with
  `emission_points` baked from the source's opaque cells and spawn delay proportional to x or y.
- Card: one CanvasItem shader for peel and gloss (`fold`, `corner`, `gloss_t`, `backing_color`,
  `scan_y`); shadow child with blur; one `Tween` chain; follow phase per frame in `_process`.
- Grease pencil: `Line2D` round caps, width 8–10, wax-grain texture + `marker_stroke.gdshader`, a
  duplicate offset (2, 3) under-shadow; write-on/wipe by trimming points (never alpha); dashed =
  tiled dash texture; snapping to real edge polylines so marks stay true.
- Heat H1: a backdrop `HeatCity` `Node2D` (additive spill sprites, searchlight cones, beacons); band
  counts and periods in `campaign_config.tres`.

### 6.4 UI
- Theme type variations in `UiTheme.build()`: `TerminalPanel`, `TerminalButton` (focus =
  `StyleBoxBrackets` lime, grow 7 px), `HoloPanel` (`holo_panel.gdshader`), `PaperPanel` (9-patch).
  Shaders expose each effect as a uniform so reduce effects can zero it: `crt_panel.gdshader`
  (scanlines 3 px @ 10 %, hex-dump 6 %, edge glow), `holo_panel.gdshader`, `foil.gdshader` (gloss).
- **Sticker words** are baked offline per locale at 2× (keyline, extrude, die-cut, rest gloss) into
  an atlas; runtime `TextureButton`/`StickerButton` plays states.
- Live numbers: `LabelSettings` Anton, 2 px outline #06060A, shadow size 10 in own colour @ 50 %.
- Neon signs: one texture per sign with per-letter masks (filled tube + core mask + partial A-top
  mask), `uniform float lit[]`, a timeline per sequence; dead letters swap to a broken-tube sprite;
  spill = additive sprite modulated by mean `lit`.
- Portraits: pre-rendered bust sets per seed (idle, blink, talk, hurt, dead-eyes) or assembled in a
  SubViewport; feed = one CanvasItem shader (`mode`, `tint`, `split`, `tear`, `noise`, `fps_hold`);
  paper contexts via a "print" shader.
- Layer order, combat (back to front): city + spill → wheels → heat-glitch post (optional) → FX
  world layer (tracers, shards, dissolve, walls) → HUD → stickers → hand → moving card → damage
  numbers → grease pencil → cursor. Pencil is above all UI.

### 6.5 Data and determinism
- Every random look (city props, car colours, rookie busts, sign phases, corridor dressing) comes
  from a seeded `RngService` stream; tie-breaks by content id then node id.
- Every tuning number in the round NOTES (shard counts, Heat band counts, lane speeds, socket
  radii, dock offsets, run-path costs, camera clamps) goes into config `.tres`, never code.
- Views only read state (Signal Up, Call Down). HQ mechanics are pure functions in `scripts/core/`
  of `(hq_data, step)`; the view animates between two results.

---

## 7. Appendix A: locked reference images

Paths are relative to `docs/concepts/`. "v" = the latest locked version.

| Element | Locked reference |
|---|---|
| Base world style (Cv2 + E) | `round2/assets_compare/s1_cv2_cel`, `round2/r2_blend_EC_on_Cv2_day` |
| City restyle (day/night/suspicion) | `round6_city_restyle/views/restyle_*_full.png` |
| Overlay kit (sticker, pencil, spill) | `round3_overlay/combined_v2` |
| Opaque grease pencil | `round11_combat_target/combat_boss_night.png` |
| Combat backdrop day (cool) | `round11_combat_target/combat_boss_day_cool.png` |
| D4 wheel frame | `round13_wheel_details/d4.png`, `combat_d4.png` |
| Slice system, names, glyphs | `round34_slice_names/slice_system_final_v3.png`, `glyph_set_v3.png`; masters `round17_slice_system/glyphs/` |
| Tiers V2 | `round17_slice_system/tiers_final.png` |
| State overlays | `round15_slice_system/states.png`, `states_fx.gif` |
| DEFRAG (player defend) screen | `round16_slice_system/firewall_screen.png`, `firewall_fx.gif` |
| DETOUR / INFECT screens | `round11_combat_target/slices_r11.png` |
| Corp kits | `round17_corp_wheels/corp_{halcyon,orbital,rebel_cell}.png`, `round18_corp_wheels/corp_{meridian,solace}.png`, `round18_corp_wheels/corps_compare.jpg`, `motion_*.gif` |
| PRIORITY glyph | `round18_corp_wheels/special_priority.png` |
| Card-play preview | `round17_corp_wheels/preview.gif`, `preview_storyboard.png` |
| Card play (hover, slap, dissolve A) | `round19_combat_fx/card_play_v2.gif`, `dissolve_A_bitstream.gif` |
| Damage shards | `round18_combat_fx/damage_shards.gif`, `binary_damage/` |
| Combat FX | see 3.20 table (rounds 19–23) |
| SEND IT | `round22_combat_fx/send_it_sticker.png` |
| Heat on combat (H1) | `round22_combat_fx/heat_city_v4.gif`, `heat_city_v4_strip.png` |
| Precision landings | `round39_landing_exploits/landing_{perfect,good,weak}.gif` |
| Hub cores, lockdown, defeat | `round40_hub_inner_ring/hub_cores_v3.png`, `lockdown.gif`, `player_defeat_v2.gif`; `round39_hub_inner_ring/hub_cores_v2.png` (Rigger, Overclocker); `round38_hub_inner_ring/hub_cores.png` (Ghost, Swarm, Hive, enemy hubs) |
| Inner ring | `round39_hub_inner_ring/inner_ring_v2.png`, `round40_hub_inner_ring/inner_ring_v3.png` |
| Status stacks | `round40_hub_inner_ring/status_stacks.png` (style B) |
| Satellites, replace | `round40_satellites/satellites_v3.png`, `replace.gif` |
| Parasite ring | `round40_satellites/parasite_needle_options.png` (A), `round41_wheel_stack/parasite_popup.gif` |
| Wheel stack, clutter, HUD v4 | `round41_wheel_stack/wheel_stack_combined.png`, `drones_v2.png`, `combat_worst_case_v4.png`, `combat_typical_v4.png` |
| Firmware | `round34_firmware_daemons/firmware_socket.png`, `firmware_set.png`, `firmware_trigger.gif` |
| Daemons | `round34_firmware_daemons/daemon_set.png`, `daemon_row.png`, `daemon_trigger.gif`, `daemon_colours.png` |
| City motion | `round26_city_motion/city_ambient_{night,day}_v4.gif`, `round24_city_motion/motion_layers.png` |
| HQs + Sites | `round26_hq_targets/hq_{solace,halcyon,orbital}_close_*.jpg`, `site_{solace,orbital}_night.jpg`; `round27_hq_targets/site_halcyon_court_night.jpg`; `round31_meridian_combat/combat_meridian.jpg`, `combat_meridian_motion.gif`; `round11_combat_target/combat_regular_night.png` (Meridian depot) |
| Orbital silo open | `round26_hq_targets/hq_orbital_close_night_open.jpg` |
| REBEL_CELL map + canyon | `round34_rebel_cell/map_A_{home,dispatch}.jpg`, `map_fist_reveal.gif`, `canyon_dispatch.jpg`, `combat_rebel_cell_motion.gif` |
| MAINFRAME sign | `round33_mainframe_sign/mainframe_{blue,red}_v4.png`, `mainframe_sequence_v4.gif`, `iamai_sequence_v4.gif`, `iamnoman_sequence_v4.gif` |
| Shop facade | `round12_modem_facade/f1b_{night,day,rain}.png` |
| Shop interior, wheel, bin | `round34_firmware_daemons/shop_v5.png`, `round33_shop/slice_wheel_offscreen.gif`, `recycle_bin.gif` |
| Unified city | `round39_city_unified/city_grid.png`, `round40_city_unified/raid_view_v3.png`, `three_views_v3.png`, `cars_lod.png` |
| Raid UI and interactions | `round39_city_unified/raid_view.png`, `round40_city_unified/raid_gifs/index.md`; `round21_raid_ui/path_rules.png`, `node_health.png`, `raid_report.png`; `round22_raid_ui/node_status_key.png`; `round23_raid_ui/interactions_gifs/` |
| Raid world | `round20_raid_world/building_nodes_v2.png` (B), `round21_raid_world/operators_r3.png`, `round22_raid_world/vehicle_icons_v4.png`, `unit_health.gif`, `operator_rigger.gif`, `class_colours_v2.png`; `round23_raid_world/bonus_slow_v3.gif`, `bonus_repair_v3.gif` |
| Campaign lost / dossier | `round20_raid_world/campaign_lost.png` (A), `round21_raid_world/campaign_dossier.png` |
| Netrun | `round37_netrun/city_default.png`, `city_legend_hover.png`, `city_heat_calm.gif`, `transition_mix.gif`; `round36_netrun/city_states_a.png`, `node_backdrop.png`; `round38_netrun_transit/transit_v3.png`, `transit_step_v3.gif` |
| HQ compound + mechanics | `round35_netrun/hq_compound.png`; `round43_hq_mechanics/hq_*_compound.png`, `hq_*_mechanic.gif`, `dispatch_sync_strike.gif` |
| Site markers | `round42_site_markers/site_markers_v4.png`, `site_markers_on_map_v4.png` |
| Exploits + gate | `round38_landing_exploits/central_server_gate.png`, `central_server_breach.gif`; `round39_landing_exploits/exploits_v2.png`, `exploit_on_map_v3.png` |
| Reward, events, dialogue | `round31_reward_event/reward_screen.png`, `reward_reveal.gif`, `event_screen.png`, `event_screen_memo.png`, `dialogue.png`; `round32_shop_reward/reward_screen_v2.png` |
| Portraits | `round39_portraits/portraits_classes_v2.png`, `round38_portraits/portrait_states.png`, `portrait_contexts.png` |
| UI kit, type, title | `round33_ui_chrome/ui_kit.png`, `typography.png`, `title_screen.png`, `title_screen_alt_simulate.png`, `abandon_dialog.png`; `round31_ui_chrome/settings_menu.png` |

## 8. Appendix B: open game-design to-dos that affect art

The authoritative list is DIRECTION_REVIEW's "Game to-do list for reintegration" and the "Game
to-do" blocks under each round. These block or shape art reintegration:

1. **GDD §9.1 / §9.4 baseline** replaced by this bible (DECISIONS entry + GDD update).
2. **Renames:** slice programs (SHIM, OVERFLOW, DEFRAG, SANDBOX, DETOUR, HOTFIX, INFECT, TROJAN,
   NULL); WEIGHT, PRIORITY (still collides with Priority Routing), GROWTH, AIRMAIL; "Mainframe Gate"
   → **Central Server**; Microchip → **Firmware** (`strings.csv`); PARTIAL → **WEAK**; raid words
   TAKEN / CELL HOLDS vs GDD Seized / Holds.
3. **New data:** SliceData tier I–III; placeholder slice types and states (PHISHING, SHIELD,
   ENCRYPT, RECON, BURN/TORCH/DISSOLVE, FROZEN/LOCKED/BURNING/EMPOWERED, KILL PROCESS); status stack
   counts; MOMENTUM runtime picto; card type band (WHEEL/HACK/SYSTEM) or drop it; card rarity look.
4. **Settings:** `heat_glitch: bool = false` + VfxTier exemption; `always_show_nodes: bool = false`;
   "Always show node health"; optional "hub shows slice value"; netrun transition shortening.
5. **Combat proposals:** inner-ring sub-needle, hangar (damage with several drones), double status,
   splash/broadcast, blank start; parasite ring (either wheel, cleanse, aim conflict); satellite
   overwrite and no-nudge; drone/parasite hard limits; one-pointer boss and CUT A HEAD ("boss starts
   stunned"); Virus random picks; expanded Exploit set (ROOTKIT, HIJACK, CIPHER) and seeding; gates;
   Perfect latch release timing; boss nudge keys A/D.
6. **Firmware/Daemons:** replace-and-destroy on an occupied socket; Zero Day, Stolen Intent, Linked
   Bus and Mirror-elite hub visuals.
7. **Shop:** top slice cheaper (80 vs GDD flat 100); nudges on the shop wheel; recycle-bin undo until
   LEAVE.
8. **Campaign/raid:** EXPOSED rule; Heat raises waves/routes; intel NOT-decrypted at high Heat;
   decoy destruction; alternate-class station bonuses and levelling; raid zoom fitted to network
   size + sector split; Exploit Site pinning before decryption; claimed-Site icon losing its kind.
9. **Netrun/HQ:** start-node choice; long-link layer fit (pan vs spacing); HQ mechanic rules (WAIT
   cost, riding the train, SPOTTED cost, sabotage cost, Sync Strike decks); DISPATCH finale.
10. **HQ actions** without an HQ room (Heat, patching, repairs, recruiting, Black Market).
11. **Meridian follow-ups:** castle crest replacing crane-A on wheels, raid frames and threat
    stickers; re-run the city map for the round 31 boom-facing view corridor.
12. **Undesigned content** listed in 4.14 and `GDD_ART_COVERAGE.md` §2.

## 9. Appendix C: contradictions between rounds and how this bible resolves them

| # | Contradiction | Resolution here |
|---|---|---|
| 1 | Round 23 locks "statuses are only their overlay: no badge, no rule chip"; round 34 locks multiplier tags under the status badge and round 40 locks ×N tabs on badges; round 41's stack draws badge + tab + rule tag | Overlay is the status; a small flat corner badge appears only to carry a ×N tab (stacks > 1) and the ×1.5/×0.5 tag. **Designer to confirm.** |
| 2 | DIRECTION_REVIEW round 31: MAINFRAME "NO = N + top of the R"; round 33 v4 (locked) uses the second A's top | Round 33 v4: `N3 A6(o)` |
| 3 | Shop centre slice premium 120 (rounds 32–33) vs top slice cheapest 80 (round 34); GDD flat 100 | Round 34 (later); still a DECISIONS item |
| 4 | Class accents: v1 §7.1 / `Palette` (Rigger gold, Botnet green, Overclocker magenta, Ghost #9FE8FF…) vs round 22 `class_colours_v2` and round 38 portraits | Round 22 / 38 values (2.5); Palette debt |
| 5 | Corp hues: v1 / `Palette` (Solace #3DFF8B, Halcyon #8C7BFF, Orbital #7FA8FF) vs round 18 kits (#96FF46, #B06EFF, #CDF0FF); round 17 NOTES say #CDF0FF but its patch script used #AACDFF | Round 18 values; Orbital re-approaches UI-text white and Solace approaches Cell lime (2.4 risks) |
| 6 | Exploit kind icons: keycards use binoculars / key / CORRUPTED mark (round 38) vs Site sub-badges magnifier / sledgehammer / INFECT glyph (round 42 v4), where the key now means only "Exploit Site" | Unify on the round 42 icons for both; keycards need a re-render |
| 7 | Exploits on T3 key Sites (rounds 35–36 stills, round 36–38 unified NOTES text) vs T2 (GDD, round 36 decision, round 37) | T2 |
| 8 | HQ boss run as building climb (rounds 32–34, "locked D") vs overhead compound (round 35 lock) | Compound; climb rooms survive as node backdrops |
| 9 | Netrun paths: thin double dashes along streets (round 38 decision, round 39) vs single dashed meander (round 40) vs straight cable runs with solid walked path (round 41 lock) | Cable runs v3 |
| 10 | HQ mechanics round 42 (Solace rotates; Halcyon beam LOCKS nodes) vs round 43 (Solace no spinning; Halcyon SPOTTED) | Round 43 |
| 11 | Hub Breach: round 38–39 cracked-glass BREACHED (and "Breached stays as an enemy state") vs round 40 LOCKDOWN waterline | Lockdown waterline |
| 12 | Disabled: raid sockets dashed amber (rounds 19–21) vs Site markers "amber gone", white bolt over a greyed marker (round 42 v3) | Each view keeps its locked look; the semantic differs by zoom. Designer to confirm |
| 13 | Raid camera clamp: 140–320 (round 37), 150–320 / 150–420 (round 38), 220–380 (round 39) | Config value; dedicated pass owed |
| 14 | Heat glitch "on by default" (round 18) vs "Options extra, off by default" (round 19 lock) | Off by default |
| 15 | Focus brackets 2 px at 4 px offset (v1) vs 3 px at 7 px (round 31) | Round 31 |
| 16 | Respin label CHECKPOINT (rounds 19–20) vs RESPIN (round 23) | RESPIN |
| 17 | Forecast tags above wheels (v1, STYLE_GUIDE, rounds 10–31; GDD 9.2 "per-pointer intent labels") vs HP result chips, no forecast tags (round 43) | HP result chips; GDD 9.2 wording needs updating |
| 18 | Firmware socket at ρ 160 (round 34) vs "r = 168" / zone 142–194 in round 41's stack | ρ ≈ 160–168, config value |
| 19 | Station beacon: R1 rooftop figure recommended (round 20) vs R3 class beacon (round 21 lock) | R3 |
| 20 | Combat HUNTED: helicopters (round 19 H1) vs no helicopters (rounds 21–22) | No helicopters on combat; the city map keeps choppers at HUNTED (round 24) |
| 21 | Shop removal: PURGE rm -rf key (round 32 recommendation) vs recycle bin (round 33 lock); sign MARKET NEON (round 27–28 lock) vs MAINFRAME (round 31) | Recycle bin; MAINFRAME |
| 22 | Netrun "available" colour: corp-colour pads (round 34) vs fixed orange "run colour" (rounds 35–42); all drawn on Meridian, whose hue is orange | Orange until the designer says otherwise |

## 10. Changes from v1 (summary)

| Topic | v1 | v2 |
|---|---|---|
| Materials | CITY / GLASS / PAPER (Cell's zine voice: tape, marker, spray, drips) / DECK | World, vinyl sticker, grease pencil, CRT terminal, corp paper, decrypted holo, binary bits, bare Anton. Spray, drips and marker graffiti are gone; paper is now corp paper; DECK has no current use (HQ room dropped) |
| City | isometric neon slate city, marker-stroke streets, raised-fist roads | Cv2 + E low-poly city, one model at three zooms, sky lanes, red-window fist |
| Wheels | paper-stickered player bezel, gauge needle | D4 Lens & rail, C slices, V2 tiers, overlays, firmware, inner-ring textures, collapsed drones |
| Cards | paper stock by rarity, risograph illustrations | vinyl sticker cards, peel/slap/dissolve A; illustration style undecided |
| VFX | per-type hit shapes (slash, hex, smear…) | binary bits for all digital FX, temporary labels dissolve to bits; VfxTier table kept |
| Heat | posters, glitch, searchlights, grade shift | H1 city reacts on combat, calm Heat B on maps; glitch is an option |
| Forecast | paper tags above wheels | HP result chips |
| Corp and class colours | v1 table | 2.4 and 2.5 |
| Fonts | Anton, Share Tech Mono, Permanent Marker, Plex | + Courier Prime for corp paper |
| Focus | 2 px brackets | 3 px lime brackets at 7 px |

Still valid from v1 and not repeated here: the 8 px grid and spacing tokens (§5), the six component
states (§6), input widgets (§6.5), resolution and aspect rules (§5.4), the definition of done (§14).
