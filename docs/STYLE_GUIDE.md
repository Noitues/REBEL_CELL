# REBEL_CELL — Style Guide (Visual Baseline)

Approved mockups (private canvas; ask the project owner for access):
https://claude.ai/artifact/EyiLTRaqVVwdhSQox1yufP — see the "Blended direction: three
worlds" row (HQ, City Grid, Netrun combat).

## 1. Three Worlds
| World | Style | Used for |
|---|---|---|
| Physical | **Diegetic Cyberdeck**: rain-streaked window, neon, worn metal deck, CRT readouts | HQ, recruitment, stationing, loadout |
| The net | **Wireframe Cyberspace**: glowing line geometry, perspective grid floor, wireframe skyline | City Grid, netrun map, combat arena, raids |
| The Cell's voice | **Punk Zine**: paper, tape, marker, spray paint, drips, halftone | Cards, HUD, notes, menus, story beats, codex |

**The rule:** the room is a cyberdeck, the net is wireframe, and anything the Cell touches
gets zined. Only combat combines two worlds (wireframe arena + zine UI).

Punk energy reference: neon graffiti chaos (spray, drips, scrawled notes, hot pink).
Use original motifs only. Do not copy existing characters, doodles or logos from any IP.
The Cell mascot is an original grinning hexagon "cell".

### 1.1 Neon city pass (2026-09-25)
Reference: `docs/reference/ChatGPT Image Sep 24, 2026, 08_08_40 PM.png`. Every screen stands
over the isometric neon city: in the physical world it is seen through the Cell's window; in
the net it is re-inked with circuit lanes. Each corporation's district has its own building
mix, colour weighting and landmark HQ (Solace DNA double helix; with a culture theme,
the Chinese pagoda, the Egyptian terraced pyramid, the English clock tower). The Cell has
no tower: its roads etch a raised fist into ordinary city blocks. Buildings are painted
slate tinted strongly toward their line colour (`NeonCity.DEFAULT_TEXTURE`, "strong
tinted slate": lit from above, ledges, recessed panels, ribs, vents, amber light slots,
rimmed roofs), inked by hand in amber, purple, pink, cyan and green. Streets are bundles
of skinny full-neon marker strokes, wider where traffic is busy. System UI is terminal glass,
with a mono title and a pink rule. The Cell's voice stays paper (taped notes, Polaroids,
stamps, marker scrawls). CRT scanlines appear only on the city and terminal glass.

## 2. Colour Tokens
| Token | Hex | Use |
|---|---|---|
| `cell_pink` | #FF3DA8 | The Cell: player wheel, tags, primary actions |
| `cell_acid` | #D4FF00 | Secondary Cell highlight: previews, scribbles, emphasis |
| `cell_turf` | #D4FF00 | The Cell's territory: claimed Sites, its network links, the district tint, CLAIMED marks, the spray ring (ANIM-R3: never `cell_pink`, which is damage) |
| `paper` | #F2EEE4 | Zine paper |
| `paper_alt` | #E9E4D6 | Aged paper, posters |
| `ink` | #111111 | Zine ink |
| `net_cyan` | #5CE1FF | Neutral net geometry, grid, links |
| `net_bg` | #02030A → #0D1440 | Cyberspace background (radial) |
| `corp_solace` | #3DFF8B | Solace wheels, Sites, threats, holograms |
| `corp_meridian` | #FF8C1A | Meridian Freight Systems (M8) |
| `corp_halcyon` | #8C7BFF | Halcyon Civic (M9; moved off #4FFFB0, too close to Solace) |
| `corp_orbital` | #DDE3FF | Orbital Commons (M10; starlight, kept clear of resist_gold) |
| `corp_rebel_cell` | #E8141E | REBEL_CELL (M11; deep red since H20, #FF2A6D was nearly `cell_pink`) |
| `crt_amber` | #FFB000 | CRT readouts on the physical deck only |
| `resist_gold` | #FFD24D | Spin resistance, locks |
| `desk_dark` | #1B1D21 / #34383E | Deck metal |
| `night_*` | #060816 sky, #101832 / #1C2A55 blocks | City backdrop masses |
| `neon_violet` | #B04DFF | Fifth ink colour (with amber, pink, cyan, green) |
| `terminal_*` | navy glass rgba(5,13,28,.9), edge #5CE1FF @75% | Terminal panels |
| `note_*` | #E9DFC6 paper, #F4C3CF pink, #F2DC7A yellow | Taped notes |

Each corporation gets its own `corp_*` glow colour. Never use colour as the only signal.

## 3. Typography
| Role | Font | Notes |
|---|---|---|
| Handwriting, tags, notes | Permanent Marker | Cell voice only |
| Zine display, numbers | Anton | Card titles, HP, Heat |
| System text | Share Tech Mono | Net labels, logs, CRT, DISPATCH |

All three are on Google Fonts under open licences; confirm each licence before release.
DISPATCH is always Share Tech Mono on clean surfaces, never handwritten or zine-styled.

## 4. Component Rules
- **Wheels:** neon gauge rings; translucent slices (attack/crit `cell_pink`,
  defend/shield `net_cyan`, evade/heal green, afflict/deploy violet) with a bright rim;
  a glyph on every slice drawn **bold**: solid black with a heavy white outline
  (`SliceIcon.style` 4), the same on Modem slice tiles; value outside the ring; white
  gauge-needle pointers; dashed outline for the Miss slice; resistance in `resist_gold`.
  A right nudge turns the wheel clockwise on screen (H20). Curved white nudge arrows sit
  at the top left (anticlockwise) and top right (clockwise) of every wheel, a second pair
  marked IN for an inner ring; the current target wears four `cell_acid` reticle brackets.
- **Zine elements never cover the wheels** (nor their values, satellites or HP arc:
  radius + 66 px).
- **Cards:** stickers (black/pink/paper), slight rotation (±4°), tape strips, hovered card
  lifts and glows; cost in marker. Cards are dragged onto what they aim at; legal drop
  zones glow `cell_acid` (thin), the aimed one thick.
- **HUD:** Polaroid portrait, ransom-note Heat, RAM chip bar with its count, Daemon sigils
  under the Polaroid, subtitles and the tutorial in the right column, RESPIN / UNDO
  stickers beside the drip-lettered SEND IT. No text log the player must read: the taped
  tag over each spinner shows what its needles land on and a row of result chips (HITS,
  HP, BLK, statuses, RAM, HEAT...), the HP arc shows the predicted loss in red.
- **Ghost preview:** dashed `cell_acid` arc from the arriving slice (its icon) to the
  needle, arrowhead the way the rim moves.
- **Grid:** isometric wireframe buildings; claimed Sites `cell_pink` with spray circles;
  corporate Sites `corp_*`; threat paths glowing `corp_*` arrows; zine sidebar "THE PLAN".
- **HQ:** graffiti tag with drips, wanted poster (Heat), Polaroid roster, pirate radio,
  deck CRT, "JACK IN" button (the Site card's launch button says JACK IN too).
- **Subtitles** have a band of their own (`SubtitleStrip`): under the top bar on the HQ
  and netrun screens, beside the tag on the title; nothing interactive and no stat tag
  sits in it. A fight docks its own in the right column.

### 4.1 Icon set (H21)
One line-drawn vector icon per resource and action (`StatIcon`, no font glyphs or emoji,
so it reads in every language and at every text size), drawn in ink on paper tags and in
the resource's colour on the dark screens. The same icon wherever the resource shows:
top-bar tags, CELL STATUS badges, Modem price tags and wallet, event choice outcomes, run
and profile tags.

| Resource / action | Icon | | Resource / action | Icon |
|---|---|---|---|---|
| Heat | flame | | Cycles (money) | coin (ring, inner ring, dot) |
| Schematics | blueprint sheet | | Cards | two stacked cards |
| Home server | house | | Rank | two chevrons |
| Exploits | diamond with a solid core | | Banked | vault door with dial |
| Raids | shield with "!" | | Armory / assets | crate |
| ICE | snowflake | | Crew / operative | two people / one person |
| HP | heart | | Firmware | chip with pins |
| Daemon | ghost | | Fights won / fight | crossed swords / crosshair |
| Elite | crown | | Shop (Modem) | bag |
| Terminal event | screen with a prompt | | Rack | server rack |
| Play / continue | triangle / bar + triangle | | Map / Grid | folded map |
| Codex | open book | | Settings | gear |
| Save | floppy | | Exit / back / next | door with arrow / arrows |
| Skip | double chevron | | More below | double chevron down |
| Heat reduction | small flame + down arrow | | Claim | spray ring with a drip |
| Sites a run opens | node, street, arrowhead | | | |

H24: every **map node kind** has its own silhouette *and* symbol, and never borrows a
resource's icon for another concept (the snowflake is ICE only; the diamond is Exploits
only). `CityMapOverlay.KIND_SHAPES` / `KIND_SYMBOLS`; the key rows, the HQ mini-map, the
route and Grid buttons and the tooltips all use the same painter.

| Kind | Silhouette | Symbol | | Kind | Silhouette | Symbol |
|---|---|---|---|---|---|---|
| Fight | circle | crossed blades | | Boss Site | star | small star |
| Elite fight | 8-point star | crossed blades | | Exploit Site | diamond | Exploits diamond |
| Shop (Modem) | price tag | bag | | Heat reduction Site | drop | flame + down arrow |
| Event | square | ? | | CORE | house | door |
| Rack | tall box | server blades | | Site (tier) | hexagon | its tier ("T2") |

Menu items carry their icon in place of the terminal chevron (`IconMark`, sized to the
button's font); a shop price hangs on a yellow price tag with the coin (pink when out of
reach), never in a card's RAM circle; an event choice shows its outcome as icons with
signed numbers (green helps, red costs) under its words.

H22: a button that stands for a map node (route choices, Grid RUNS OPEN NOW rows) draws
that node's **map icon** with the map's own painter and colour (not a StatIcon), and a
Site row adds the map's **tier pips** (lit pips of four: the harder, the more lit). The
HQ JACK IN stamp carries the plug over its word. A **forecast** (what happens if you act
now, e.g. the raid setup's "IF THE RAID RUNS NOW: HOME HIT") is drawn dashed like
combat's NEXT plate; solid stamps are results only (REPELLED, BREACHED after the raid).

## 5. Motion & Feedback
- Jack in: camera pushes into the deck CRT and dissolves to wireframe; jack out reverses.
- Precision: Perfect = latch + wheel-local inversion + 2-frame freeze; Good = clean click
  and a ring off the rim; Partial = stutter; Miss slice = static burst over that slice only
  (built in ANIM-2, 5.2).
- Heat: effects pulse on threshold events; they do not stay on. Physical world adds wanted
  posters and searchlights; the net shows corporate wireframe creeping over zine elements.
- REBEL_CELL campaign: the net itself renders in zine style.

### 5.1 Motion config (the Animation pass, ANIM-1)
- **One table.** Every UI animation's duration, delay, ease, transition, amplitude and
  on/off switch is an entry in `content/config/ui_motion.tres` (schema
  `UiMotionData` / `UiMotionEntryData`), looked up by id (`&"card_hover"`,
  `&"resolve_pass"`...). No motion number lives inline in a view. Every roadmap item in
  ANIMATION_HANDOFF 4 has at least one id, and content validation requires them all.
- **Build tweens with `Motion`** (`scripts/ui/kit/motion.gd`): `Motion.pop(node, id)`,
  `slide_in(node, from, id)`, `fade`, `shake`, `blink`, `loop_pulse`, `number_roll`,
  `run(id, node, property, to)` and `stop(node)`. Code that builds its own tween reads
  `Motion.seconds(id)`, `delay_of(id)`, `amplitude(id)` and `entry(id).ease/.trans`.
- **Reduce effects and headless** show the end state at once: the helpers return null
  and never leave a tween running, and a disabled entry does the same. Never `await` a
  motion in a rule path.
- **Speed.** `Motion.set_speed()` (0.25x-4x) divides the durations the kit hands out: the
  lab uses 0.25x-2x, raid playback 1x/2x/4x. Ambient loops (beacons) keep their own clock.
- **Tuning.** `tools/design_lab/motion_lab.tscn` loops any id on real pieces. It has
  sliders and pickers, and "copy values" gives paste-ready .tres lines. Frame strips for
  review: ANIMATION_HANDOFF 6.
- **Amplitude units** depend on the helper: px (slide, lift, shake), a scale (pop, bump),
  an alpha (fade, blink, pulse, flash), degrees (tilt, flip), frames (hit freeze), ticks
  per second (spin blur), tenths of a tick (spin overshoot), a seconds cap (a menu
  line's typing), a share 0..1 (a split of a motion's time), px per second (the drag
  ghost's full-tilt speed) or a count (pulses). Each entry's comment in the .tres says
  which (`UiMotionEntryData` lists them too).
- **One press rule (ANIM-R1, `MotionSkip`).** A press is a key going down (no auto-repeat),
  mouse button 1-3 going down (never the wheel) or a pad button going down. A press that
  completes a motion is consumed and does nothing else: the SEND IT replay, drops and
  landings, flights and stamps, typing words and subtitles, page entrances and the route
  move all end at once and nothing behind them sees the press. Exceptions (ANIM-R2): in a
  menu a press that works the menu — a focus move (arrows, D-pad, Tab), an accept (Enter,
  Space, A) or a click on one of its lines — completes the line's motion and passes on (a
  menu never drops a fast tap: Down then Enter activates the new line); a press that
  completes typing shows every word typing on screen at once (the page's text and the
  subtitle); while the jack covers the screen nothing is a press.
  ANIM-R3: outside menus too a press that works the screen (a focus move, the Settings key,
  accept on the focused button, a click on a button) completes the motion and passes on: the
  raid playout, ambient typing and subtitles consume only presses aimed at them; an open
  pause menu keeps its presses; a consumed pad press still switches the prompts to the pad.
  ANIM-R4: one rule in every helper (`MotionSkip.verdict`: the SEND IT replay, page
  entrances, flights, drops, the route move, typing, subtitles, the raid playout): while a
  pause menu is open the motion plays on and the press is the menu's; a press that works the
  screen completes the motion and passes on; any other press completes it and is consumed.
  "A click on a button" means the control under the pointer (a button covered by a panel is
  not clicked), with the clicking mouse button in its button mask (a right-click works no
  left-click button); the topmost button under the point counts only when nothing hovered
  holds it. The SEND IT replay keeps presses on the fight's own controls (SEND IT, RESPIN,
  UNDO, the hand): they end the replay and do nothing else, so a turn is never played blind.
  In a menu the Settings key passes too (Esc while a pause-menu line types closes it).

### 5.2 Combat motion (the Animation pass, ANIM-2 / ANIM-3)
- **Replay, never re-run.** The state is final at once; motion replays the engine's own
  events on top (`ResolveBeats`, `CombatFxLayer`, `WheelView` overrides). Skips and
  reduce effects show the end state.
- **SEND IT** reads as a sequence of about 2 s (ANIM-R1): needles latch and the landed
  slices pulse in their colour (a MISS slice gets a big grey X) and hold 0.3 s; each hit
  pulses its needle and flies as a thick projectile in the attacker's colour from its
  landed slice to the victim's HP ring, one at a time (ANIM-R2: never two at once), acid
  for the operative's side and red for the enemies', its raw number riding with it (a hit
  soaked whole still flies and shows its guard's glyph and "0" where it struck; since ANIM-R4
  the equation sword 8 − shield 8 = 0); a partly blocked hit meets its guard where it struck
  (sword 14 − shield 5 = 9) and what got through pops fresh in the hub and travels into the
  HP counter, which rolls down with a white lag bar as
  the wheel flashes and shakes (every HP change has a number of exactly its size; a
  satellite's shows at its token); guard numbers sit under the hub's lines; statuses stamp on their slice; a wheel
  whose HP didn't change stamps NO DAMAGE (ALL BLOCKED when every hit was soaked); a
  dying enemy's HP is seen at 0 before it falls apart (a short white flash on its own wheel,
  never the screen) and leaves its empty spot marked DEFEATED; a fight ending on a break
  shows its result first and VICTORY lands over the enemies' side. The result waits for
  every HP roll, holds 0.5 s under THIS TURN with LAST TURN, then the wheels spin to the next
  landing and the forecast flips in, its tape reading IF YOU SEND IT; the TURN counter
  changes when the replay ends. A new fight's enemy enters from the edge (its forecast
  shows as it comes).
  Any press skips (and does nothing else).
- **Spins** run the exact ticks with ease-out, a 0.2-tick overshoot and settle; slices blur
  when fast. **Nudges** are 0.08 s steps with a 2 px recoil, queued and never out of step.
- **Landings** differ in shape, not only colour: inversion (Perfect), ring (Good), stutter
  (Partial), static in the slice (Miss).
- **Cards** lift 12 px and straighten on hover; drag ghosts trail and tilt; zones pulse and
  a reticle glides to the aim; a play flies, stamps and dissolves (burns when exhausted);
  a cancel glides home; the hand never moves under the cursor.
- **Readability**: numbers stay inside the hub (sized to fit it at every text size), off
  the hub's words and never on each other, clear of every needle; tags and NEXT plates
  hide while a SEND IT replays and flip back in; nothing waits on motion when the player
  decides.
- **Refusals and SEND IT** (ANIM-R1): not enough RAM flashes the RAM chips red with "COST >
  RAM" beside them and pulses the card's cost (or the respin sticker); SEND IT carries a
  drawn ▶▶ that pulses gently when no RAM is left. Tag chips come in order of importance
  (damage to you, damage dealt, HP, then the rest), so "+N MORE" never hides damage; at big
  text they shrink to their 1.3 size before any folds (ANIM-R2). Spent RAM floats "-N RAM"
  off the count; a purchase short of Cycles flashes the CYCLES tag red (NEED N · HAVE M).
- **SEND IT reads to a newcomer (ANIM-R3)**: the forecast tag stays up through the replay and
  ticks each line as it happens, its tape then reads THIS TURN and it fades; a hit rides its aim
  (12 -> 6 ½ at half power, bigger on PERFECT) and waits until the last number has entered its
  HP (one roll per hit); a hit soaked or evaded whole shows its glyph and 0 where it struck, and
  ALL BLOCKED / NO DAMAGE carry a shield-over-empty-set mark (ALL BLOCKED on the last impact);
  guards are a glyph and a number from the blocker, never a word badge; an icon row beside
  each HP (sword 6 -> shield 5 = -1) stays with LAST TURN; a breaking wheel cracks with its own
  art and falls, a skull on the beaten side; a won fight swaps SEND IT, RESPIN and UNDO for the
  next step (LOOT / CONTINUE) at once; a played card is gone before its wheel spins; a status
  marks its slice as it lands; YOU PLAY X; NEXT and LAST TURN explain themselves on hover.
- **SEND IT for a beginner (ANIM-R4)**: the operative's hits (then its drones', staggered)
  land in full, their HP rolls done, then a gap (`resolve_side_gap`), then the enemies' (then
  their satellites'); a hit leaves from the slice right under the needle that resolves it, and
  its number shows only when it arrives; one notation for a hit and its guard everywhere, the
  mark where it struck and the icon row under the HP alike: sword and the raw hit, minus the
  shield (or the evade mark) and what it took, = what got through (no arrow formula; each
  hit's HP number pops fresh, never morphing in the hub); the operative's projectiles are
  always acid, the enemies' always red, with a big paper-ringed head flying 0.27 s; after a
  card or a respin the forecast waits (hidden) until the spin lands; a status lands as its
  glyph in green (good for you) or red (bad for you), on its slice's mark too, and a random
  status says which and whose ("☠ CORRUPTED · RANDOM SLICE", red on your wheel); DEFEATED
  and its skull wear the beaten wheel's own colour, and VICTORY stands in the room above its
  disc, never over the crack; RAM floats "-N RAM" above its count when spent (never on a
  refusal, which says NEED / HAVE) and "+N RAM" when the turn refills it.

### 5.3 Map, raid, jack and Heat motion (the Animation pass, ANIM-5)
- **Territory tint never jumps.** The city bakes the new look once; the new image shows
  through the old one as the tint spreads from the Site that changed owner, block by
  block along the streets (a light band in the new owner's colour on the front), and the
  rest of the change cross-fades behind it. It plays where the change is first seen.
- **Raids play from the resolver's events**, never recomputed: threats travel the street
  routes, traces fire, ICE LOCK rings close, decoys pull aside, numbers rise off nodes,
  outcome stamps flip on, home drains with a white lag bar, the forecast resolves. 1x /
  2x / 4x scale the raid layer only; the city's own lights keep their clock.
- **Map cameras ease, frames stay honest.** A camera change moves a rig under the city
  from the old frame to the new; fits and labels always read the real frame. A lean
  toward the selected Site stays inside the fitted map.
- **Jack in / out**: push into the deck CRT, dissolve cell by cell to the wireframe city
  with rolling scanlines; the scene changes under the opaque cover (never both scenes).
- **Heat**: one pulse per threshold crossed going up (a short distortion round the poster,
  the ransom letters shaking, the band stamped); nothing stays on (the corporate wireframe
  creep is gone since ANIM-R2 / ANIM-R3).
- **Netrun move**: a light pulse carries the "you are here" marker along the link, the
  new node pops, the old one dims; any input skips it.
- **Readable at fight scale (ANIM-R1)**: a raid step is framed before it plays (the camera
  eases to its entries, moves, guns and targets); a shot reads shot, hit, number; big tokens,
  stamps and numbers; enemy routes carry chevrons, the Cell's links stay solid; placed
  defences stay on their nodes as markers; a hit on home flies its number into HOME, which
  rolls down. A territory change ends in a lasting outline and a CLAIMED / SEIZED stamp on the
  Site, and the SITES counter bumps. A Heat crossing lives on the number (it rolls, grows,
  flashes) and a HEAT n - BAND banner; the screen distortion is small and short. The jack
  lifts only onto a built screen. Visited route nodes carry a tick.
- **No frame freezes for a bake**: the city is baked off the main thread, a chunk a frame,
  and the raid's areas ahead of time.
- **A map is never empty (ANIM-R2)**: a map's nodes and labels draw on its first frame (the
  city's placement is known at once); the city's image fades in over the night sky when its
  bake lands, never a strip of city over part of the screen. The jack says CONNECTING TO
  <place> while the arriving screen builds and lifts onto the page, not the image.
- **Raids, Heat and routes read at a glance (ANIM-R2)**: threats are big white diamonds ringed
  in red with a trail; the end's outcomes stamp one after another and a HOME -N / HOME HOLDS
  banner stays; a defence lands after the camera pans and keeps its name. A Heat crossing plays
  in order: the number reaches the threshold, the banner stamps, the poster alone distorts
  briefly (one banner per band crossed; a drop re-stamps the band word). A claimed district
  keeps a lasting tint. A route move draws a thick trail and its target pulses; equal choices
  say "(same as 1)".
- **Verdicts, numbers and places that agree (ANIM-R3)**: every raided node stamps its resolved
  outcome, the word its label says; home's one verdict is its banner (HOME -5 - HOLDS, HOME
  BREACHED), placed clear of stamps, labels and icons. One number per hit, adding up to the
  node's change; a node's rises on its right, a threat's on its left. The feed names places
  and threats, never ids. A dropped defence falls large, stamps and shows the forecast numbers
  it changed ("25 > 30"). Territory is the Cell's acid (`cell_turf`), hatched, its stamp over
  the labels. A Heat banner warns (amber, orange, red, an eye), says what the band brings and
  never covers the number. A map baking shows the city's silhouette, never the empty sky; the
  image fades in from it. The route frames where you are (a marker at the street before the
  first node) and the next choices; "(same as N)" means the same whole road, and other
  choices show the icons of what only they reach. The jack dissolves in a calm wave from the
  CRT and names the run (and a raid that interrupts it).
- **One verdict, one notation (ANIM-R4)**: a raid has one verdict everywhere (the forecast
  stamps, the playout's result, the report): ALL HOLD only when nothing is lost, else its
  losses one per line (HOME -5, 1 DISABLED, 1 SEIZED), CAMPAIGN LOST when home falls; never
  "HOME HIT". Home's banner uses the same words (HOME -5 · HOLDS). Every change of a number
  reads `a → b` (forecast floats add ▲ green for a gain, ▼ pink for a loss); the feed says a
  hit's HP before and after, Heat's from and to, and the top bar's Heat and RAIDS move only
  with the line that moves them. A threat token stands on an opaque dark halo with a paper rim
  (never its glow over a pink node). A dropped defence sends a pulse along the threat road to
  CORE before the numbers it changed rise. A raid that interrupts a jack is a large amber
  stamp naming the corporation, held at least a second. The Heat banner says the Heat, the band
  and its threshold (HEAT 30 · NOTICED (25+)); the band word follows the number shown; the
  whole tilted banner stays on its poster. A route move shows the new choices (map labels and
  ROUTE window) as it starts; the walked route stays as a faint solid trail. A CLAIMED /
  SEIZED stamp takes the first spot round its Site that covers no label.
- Values: `ui_motion.tres` (DECISIONS "Animation pass — ANIM-5", "— ANIM-R1 campaign and
  screens", "— ANIM-R3 city, raid, jack, heat and route", "— ANIM-R4 city, raid, heat, route
  and HQ"); strips: `docs/timeline/motion/`.

### 5.4 Drag and drop, HQ side and in the run (the Animation pass, ANIM-4 / ANIM-4b)
- **Anything that moves between places drags**, with the same feel as a combat card
  (ANIM-3): it pops as it lifts, its slot dims, the ghost trails the pointer with a lag
  and a tilt. Every drag has its button, and the button stays.
- **Targets say yes or no before the drop**: the ones that take the item pulse acid corner
  brackets, the hovered one lights fully; a target that refuses shows the drawn no-entry
  mark (the refusal toast's circle and slash) when the item is over it.
- **A drop snaps and stamps**: the item snaps onto the target, dips a few px and springs
  back, a ring stamps out as it fades, an operative's dossier pops. A raid asset lands
  with the node's own drop (5.3). A refusal shakes the no-entry mark and the item glides
  home; the rules' reason shows as a toast. A drop on nothing glides home.
- **Drops pick; presses start** (designer ruling 2026-09-27, ANIM-R1): a crew chip dropped
  on a Site card's JACK IN picks that operative for the run; only pressing JACK IN (click,
  A) launches it.
- **Keys and pad**: X / Space picks up the focused item (A on items that only move), the
  D-pad walks a reticle through every target (the item follows), A drops, B puts it back;
  the pad prompts follow. The mouse can click an item, then its target.
- **Purchases by click fly**: a Black Market recruit or boost arcs from its button to
  where it went, which shows as it lands.
- Reduce effects and headless: no pulses, flights or marks, the end state at once. Values:
  `ui_motion.tres` (DECISIONS "Animation pass — ANIM-4"); strips `docs/timeline/motion/drag_*`.
- **In the run too (ANIM-4b)**: Modem purchases drag onto where they go (cards onto the
  CARDS tag, Daemons onto the DAEMONS icon, microchips and slice upgrades onto a slot of
  the small spinner in the REMOVE A CARD window, or of the UPGRADE viewer's wheel); deck
  cards drag onto the REMOVE viewer's SHRED tile; loot and an event's card or Daemon drag
  onto theirs; raid interlude assets onto a node's row. A purchase's copy shrinks into its
  small target with SOLD stamping on it (`drop_buy`, `sold_stamp`), then settles and
  stamps; a shredded card squashes into the shredder's mouth as paper strips run out
  (`shred_feed`). BUY, the socket list, UPGRADE / REMOVE and the loot's press stay (DECISIONS
  "Animation pass — ANIM-4b"; strips `drag_buy_*`, `drag_shred`, `drag_loot`).
### 5.5 Screens, menus and ambience (the Animation pass, ANIM-6)
- **Pages enter in their world's way** (`PageTransition`): glass slides in from an edge
  with a one-frame CRT roll, paper drops in and settles on its tape; under 0.25 s. Only a
  new screen enters (a page rebuilt after an action just shows). Focus lands when it ends;
  any press completes it and does nothing else.
- **Menus**: the highlight slides between lines, the new line types in (at most 0.18 s),
  a block caret blinks after the focused line's words.
- **Things you get fly to where they live** (`FlightFx`): a bought item stamps SOLD and
  flies to its top bar icon, a picked loot card lifts and flies to CARDS, the chosen event
  outcome stamps over the next screen. The state is already final; the flight replays it.
- **Numbers**: a top bar tag whose value changed bumps (x1.08) and rolls to it; Cycles and
  Schematics count up when they rise; CAMPAIGN / THIS RUN cross-fade.
- **Words type in**: subtitles (the page's time starts once it is all shown), the event's
  DISPATCH text, the pirate radio. Options can make them instant; the words are always
  whole underneath, and any press shows them.
- **Once, then hold**: drips grow the first time a tag appears; the Modem's tubes warm up
  and its traces light on entry; hover gives one halo pulse. Idle loops are few and slow:
  the deck monitor's hum, JACK IN breathing, the caret, a third of the HQ signs, sparse
  traffic dashes on the busiest streets. All stop under reduce effects.
- **Settings changes animate nothing** (text size, language): the page just re-lays out.
- **Words before choices, places kept (ANIM-R1)**: an event's choices wait for its typed
  words (ANIM-R2: readable and focusable on their paper with a typing mark; a press shows
  the words, the first choice then has focus); shop and loot cards show their whole text; a bought Modem item stays as a SOLD
  stub in its place; loot not taken falls away; tips keep off buttons and titles.
- **ANIM-R3 screens**: the Modem's first focus is an item; its sign is whole within 0.3 s; a
  flying card is a fresh copy of itself; loot not taken falls within its window; swap chips
  wear a ring pictogram; every event choice shows icons; discards keep off RESPIN / UNDO.
- **ANIM-R4 screens**: the loot page stays (inert) until the offers not taken have fallen
  inside its window, then leaves; drawn words are translated once (LOOT / CONTINUE, the loot's
  graffiti tag and scrawls) and measured as drawn, the tag shrinking to fit its window; a
  focus tip never folds under 26 columns and goes beside (off the MODEM sign); a flapping BUY
  keeps off its card's text; a price refusal under a narrow tag wraps at its dot; an event's
  story types within 0.8 s on paper as tall as its words.
- **ANIM-R5 netrun screens**: typing never changes a layout (words are shaped whole while
  they type; paper is at least as tall as its content); a subtitle page types within 0.8 s,
  is paged again when its band changes shape, never shrinks under 12 px x the text size, and
  the event's and the run end's bands hold two lines; a page's focus lands once its words
  are whole (a press completes them). The run's end is a window over the city with a verdict
  stamp (FLATLINED / JACKED OUT / HOME FELL), the operative's fate (a flatline is for good)
  and why Heat rose. Flights take 0.7 s, arrive at x0.55 and pulse the tag they land on. A
  route move keeps its page's presses (they end the move, nothing else); "then:" icons carry
  their words; the Modem's socket list says "Chips go into:".

## 6. Accessibility
Reduce-effects toggle, flash limiter (≤ 3 flashes/s, on by default), glyphs for every
slice and status, text scaling, subtitles with speaker names.

## 7. Placeholder Art Policy
- Use simple shapes in the correct colour tokens and fonts until final art lands.
- Portraits are drawn by `PortraitArt` (no grey boxes since the visual pass): one subject
  model (operative, corporate agent, machine, boss, corporation face) in four looks
  (NEON BUST default, XEROX ZINE, WIRE SCAN, MUGSHOT; `--demo-portrait=N`), at the final
  1:1 aspect ratio inside the Polaroid frame. Every operative has its own face: the class
  sets the kind, a hash of the operative id varies hair, visor and tint
  (`PortraitArt.operative_subject` / `draw_operative`, `Polaroid.set_operative`;
  deterministic, no RNG), so the dossier, the wanted poster and the combat Polaroid show
  the same face for the same operative. Enemies come from
  `enemy_subject` (machine / agent / boss by name).
- The `[CLASS PORTRAIT]` label on a Polaroid only picks the class's default face when no
  operative is named.
- Keep art behind a thin view layer so final art swaps in without code changes
  (`Polaroid.portrait` texture, `ClassData.portrait`).
- Portrait pipeline (final): painted in full colour with strong value contrast, shown
  through a shader matching the screen's world; glitch variants at low HP and death.
