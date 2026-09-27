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
  an alpha (fade, blink, pulse), degrees (tilt, flip) or frames (hit freeze). Each
  entry's comment in the .tres says which.

### 5.2 Combat motion (the Animation pass, ANIM-2 / ANIM-3)
- **Replay, never re-run.** The state is final at once; motion replays the engine's own
  events on top (`ResolveBeats`, `CombatFxLayer`, `WheelView` overrides). Skips and
  reduce effects show the end state.
- **SEND IT** reads as a sequence under 1.5 s: needles latch, each hit pulses its needle,
  draws a line to its victim and pops a number in the victim's hub (red loss, cyan guard,
  green heal, crits 1.5x with a burst), HP arcs drain with a white lag bar, statuses stamp
  on their slice, dead wheels fall apart, then both wheels spin to the next landing and
  LAST TURN slides up. Any press skips.
- **Spins** run the exact ticks with ease-out, a 0.2-tick overshoot and settle; slices blur
  when fast. **Nudges** are 0.08 s steps with a 2 px recoil, queued and never out of step.
- **Landings** differ in shape, not only colour: inversion (Perfect), ring (Good), stutter
  (Partial), static in the slice (Miss).
- **Cards** lift 12 px and straighten on hover; drag ghosts trail and tilt; zones pulse and
  a reticle glides to the aim; a play flies, stamps and dissolves (burns when exhausted);
  a cancel glides home; the hand never moves under the cursor.
- **Readability**: numbers stay inside the hub, clear of every needle; tags hide while a
  SEND IT replays and flip back in; nothing waits on motion when the player decides.

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
- **Heat**: one pulse per threshold crossed going up (distortion, the corporate
  wireframe creeping in from the edges, the ransom letters shaking, the band stamped);
  nothing stays on.
- **Netrun move**: a light pulse carries the "you are here" marker along the link, the
  new node pops, the old one dims; any input skips it.
- Values: `ui_motion.tres` (DECISIONS "Animation pass — ANIM-5"); strips:
  `docs/timeline/motion/`.

### 5.4 Drag and drop, HQ side (the Animation pass, ANIM-4)
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
- **Keys and pad**: X / Space picks up the focused item (A on items that only move), the
  D-pad walks a reticle through every target (the item follows), A drops, B puts it back;
  the pad prompts follow. The mouse can click an item, then its target.
- **Purchases by click fly**: a Black Market recruit or boost arcs from its button to
  where it went, which shows as it lands.
- Reduce effects and headless: no pulses, flights or marks, the end state at once. Values:
  `ui_motion.tres` (DECISIONS "Animation pass — ANIM-4"); strips `docs/timeline/motion/drag_*`.

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
