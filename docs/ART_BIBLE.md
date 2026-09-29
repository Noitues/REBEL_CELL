# REBEL_CELL — Art Bible

**Status:** v1.0 (2026-09-28). **Owner:** project art direction.
**This document is the visual source of truth.** Any change to how the game looks must follow it. When it conflicts with another doc, it wins, except where it defers to one explicitly.

| Document | Role |
|---|---|
| `ART_BIBLE.md` (this) | *What* the game looks like: pillars, layers, tokens, type, layout, components, VFX tiers, motion principles, accessibility, asset specs, screen blueprints, definition of done. |
| `STYLE_GUIDE.md` | Historical baseline and the detailed **motion and interaction rulings** (5.1–5.5, ANIM-*). They stay binding unless a section below overrides them (listed in §15). The icon tables (4.1) stay binding. |
| `content/config/ui_motion.tres` | The **numbers** for every motion (durations, eases, amplitudes). This bible gives budgets and principles; the .tres holds values. |
| `scripts/ui/kit/palette.gd` | The **code form** of §3. Every colour in this bible exists there under the listed name; views never hard-code colours. |
| `scripts/ui/kit/ui_theme.gd` | The **code form** of §4 and §6 (type scale, component styles). |

How an implementing agent uses this document:
1. Find the rule for the screen or component you are touching (§6 components, §11 screens).
2. Use only the tokens in §3–§5. If you need a new one, add it to this bible *and* `Palette`/`UiTheme` in the same change.
3. Check the result against the definition of done (§14) at text scale 1.0 and 1.6, with mouse and pad, with and without reduce effects.
4. If a rule here seems wrong for a case, don't improvise. Leave the old look, and note the case under §16 "Open questions".

Words: **MUST** and **NEVER** are hard rules. **SHOULD** is the default; deviate only with a written reason in DECISIONS.md.

---

## 1. North star

> **A punk zine taped to a hacker's cyberdeck, over a neon city that is watching you.**

Three feelings, in priority order:
1. **Readable.** A player understands any screen in 2 seconds, and the combat outcome before SEND IT. *Readability beats spectacle, every time.*
2. **Handmade defiance.** Everything the Cell touches looks cut, taped, sprayed and stamped by people, against a cold, precise corporate machine.
3. **A living city.** The world behind the UI is lit, moving and reacting to what the player does (Heat, territory, the corp at war).

What REBEL_CELL is **not**:
- Not chrome-and-hologram "generic cyberpunk".
- Not a spreadsheet with neon borders.
- Not graffiti chaos that buries information.

The zine is loud in a **few** places, so it stays special.

Tone words: *scrappy, warm, urgent, precise, nocturnal, funny under pressure.*
Anti-words: *glossy, sterile, grimdark, cluttered, cute.*

Benchmarks for presentation quality (study, don't copy): *Hades* (hierarchy, VFX restraint), *Balatro* / *Slay the Spire 2* (card and number juice), *Persona 5* (graphic-design identity in UI), *Citizen Sleeper* (designed text screens), *Ghostrunner* (neon UI legibility). Use original motifs only; never copy characters, doodles or logos from any IP (STYLE_GUIDE 1).

---

## 2. The four materials (layer rules)

Every pixel belongs to exactly one material. Materials **NEVER** mix inside one component. A glass panel never contains paper cards, and a paper note never contains a native dropdown. A paper element may be *taped onto* glass (it sits on top, with a shadow), but it is its own component.

| Material | Look | Used for | Must | Never |
|---|---|---|---|---|
| **CITY** (backdrop) | Isometric neon city: tinted-slate buildings hand-inked in the five neon inks, marker-stroke streets, haze. In the net it is re-inked with circuit lanes (STYLE_GUIDE 1.1). | Every screen's backdrop; Grid, Route and Raid maps. | Be alive (§8 T0) and react to state (§9). Sit behind a dim/blur scrim wherever UI panels sit over it. | Compete with UI: no saturated light or motion directly behind text. Never show a flat placeholder (§9.4). |
| **GLASS** (terminal system UI) | Navy glass `terminal_bg`, 1 px `terminal_edge` rule, `cell_pink` title rule, Share Tech Mono, faint scanlines. | Data: lists, settings, feeds, legends, logs, map windows, DISPATCH. | Be precise: aligned to the grid, mono labels, icons from `StatIcon`. Size to content. | Stickers, paper, drips, rotation, marker font. Native OS-looking widgets. |
| **PAPER** (the Cell's voice) | Paper stock, ink, tape, marker, spray, drips, halftone, stamps, Polaroids. | Player intent and emotion: cards, forecasts, stamps and verdicts, loot, crew, notes, the top-bar tags, verbs (SEND IT, LOOT, JACK IN), story beats. | Carry slight rotation (±4°), tape, and a hard shadow. Be used **sparingly**: a screen SHOULD have no more than 3 paper focal points. | Carry dense data tables. Cover a wheel, its values, satellites or HP arc (radius + 66 px, STYLE_GUIDE 4). |
| **DECK** (physical hardware) | Worn metal `desk_dark`/`desk_metal`, CRT glass with curvature, amber readouts `crt_amber`, cables, a rain-streaked window. | HQ frame and the physical world: the deck monitor, radio, window. | Frame the HQ as a place (§11 HQ). Use amber for CRT text only. | Appear inside the net (Grid, Route, combat) except through the jack transition. |

The STYLE_GUIDE's "three worlds" map onto these materials: Physical = DECK (with CITY through the window), the net = CITY re-inked + GLASS, the Cell's voice = PAPER.

**Combat** is the only place CITY (net arena), GLASS and PAPER all meet. There, PAPER is reserved for forecasts, stamps, cards, the Polaroid, the Heat poster and the verbs. Everything else is GLASS or wheel hardware (§6.1).

---

## 3. Colour

### 3.1 Principles
- **Colour carries meaning (semantic roles).** A hue that means "harm" never also decorates a button.
- **Never colour alone.** Every semantic colour is paired with a shape, glyph, pattern or word (§12).
- **Corporations own a hue *and* a pattern *and* a landmark.** The pattern is what separates them for colour-blind players and in crowded palettes.
- The screen's **brightest, most saturated element is its most important one.** Anything else that is bright is competing with it.

### 3.2 Brand and neutral tokens (existing, unchanged)

| Token (`Palette`) | Hex | Role |
|---|---|---|
| `CELL_PINK` | #FF3DA8 | **The Cell's brand**: primary actions (one per screen), the player's identity, attack/crit slice colour, the logo. |
| `CELL_ACID` | #D4FF00 | **Focus and aim**: previews, reticles, legal drop zones, the operative's projectiles, keyboard/pad focus. |
| `CELL_TURF` | #D4FF00 | **The Cell's territory**: claimed Sites, its links, the district tint, CLAIMED marks. Always paired with a hatch and spray ring. |
| `PAPER` / `PAPER_ALT` | #F2EEE4 / #E9E4D6 | Paper stock. |
| `NOTE_PAPER`, `NOTE_PINK`, `NOTE_YELLOW`, `STICKER_PINK` | #E9DFC6, #F4C3CF, #F2DC7A, #F5AFCB | Taped notes and stickers. |
| `INK` | #111111 | Ink on paper; outlines of slice glyphs. |
| `NET_CYAN` | #5CE1FF | Neutral net geometry, glass edges, defend/shield slices. |
| `TERMINAL_BG` / `TERMINAL_EDGE` / `TERMINAL_TEXT` | rgba(5,13,28,.95) / #5CE1FF @75% / #CFF6FF | Glass panels. |
| `NIGHT_*`, `NET_BG_*` | see palette.gd | City and net backdrop masses. |
| `NEON_VIOLET` | #B04DFF | Fifth city ink only. |
| `CRT_AMBER` | #FFB000 | CRT readouts on the DECK only, and the Heat NOTICED band. |
| `RESIST_GOLD` | #FFD24D | Spin resistance, locks. |
| `DESK_DARK` / `DESK_METAL` | #1B1D21 / #34383E | Deck hardware. |

### 3.3 Semantic tokens (new; add to `Palette`)

| Token | Hex | Meaning | Always paired with |
|---|---|---|---|
| `HARM` | #FF4433 | Damage taken, losses, costs, LETHAL, enemy projectiles, refusals. | ▼ or "−", the sword/skull glyph, the word. |
| `GAIN` | #7BE07B | Healing, gains, a positive outcome, "good for you" status. | ▲ or "+", the heart glyph. |
| `HARM_INK` / `GAIN_INK` | #AB2E22 / #396739 | `HARM` and `GAIN` as **ink on paper** (PAPER, PAPER_ALT, NOTE_PAPER, NOTE_YELLOW, all ≥ 4.5:1). Paper surfaces use these; they never darken the screen hues locally. | As `HARM` / `GAIN`. |
| `PROTECT` | = `NET_CYAN` | Block, shield, evade, guards. | Shield glyph. |
| `WARN` | = `CRT_AMBER` | Caution: low HP (<50%), NOTICED Heat, a pending raid. | An eye or "!" glyph. |
| `FOCUS` | = `CELL_ACID` | Keyboard/pad focus, aim, legal drop zones, current target. | Corner brackets (4 marks). |
| `DISABLED` | #6A7080 at 100% (text), outline only | Unavailable controls. | A lock glyph or a reason on hover/focus. **NEVER** a faded version of an active colour. |
| `TEXT_HI` / `TEXT_MID` / `TEXT_LO` | #F2F6FF / #AFC0D6 / #7A889C | Text on dark: primary, secondary, tertiary (tertiary is never used for information the player needs). | – |
| `SCRIM` | #02030A @ 55% + 6 px blur | Behind every glass panel and modal that overlays the city. | – |

`HARM` replaces all ad-hoc reds and pinks used for damage (the STYLE_GUIDE's "pink is damage" ruling is superseded; see §15). `CELL_PINK` is **never** used to mean harm.

### 3.4 Slice colours (existing `Palette.slice_color`, kept)
Attack/crit `CELL_PINK`, defend/shield `NET_CYAN`, evade/heal #7BE07B, afflict #C85AFF, deploy #B08CFF, miss #6A6A6A (dashed). Slice colour means **slice type on any wheel**, not whose wheel it is. Ownership comes from wheel hardware (§6.1).

### 3.5 HP and Heat scales
- **HP** (ring, bar, number): ≥50% `GAIN`, 25–49% `WARN`, <25% `HARM` plus a heartbeat pulse (T1). A forecast loss shows as a hatched ghost segment in `HARM`. At 0, the wheel's own colour dims to 30% under its DEFEATED/DEFEAT stamp.
- **Heat** (poster, number, banner): COOL 0–24 `TEXT_MID` on paper; NOTICED 25+ `WARN`; FLAGGED 50+ #FF7A1A; HUNTED 75+ `HARM`. Heat is **never** green.

### 3.6 Corporations

Each corporation has **hue + pattern + landmark glyph**, used together on Sites, districts, threat routes, enemy wheel hardware and corp UI.

| Corp | Hue (token) | Pattern (district hatch, wheel bezel, threat line) | Landmark glyph | Change |
|---|---|---|---|---|
| Solace Biosystems | #3DFF8B `CORP_SOLACE` | Double-helix dots | DNA helix | kept |
| Meridian Freight Systems | #FF8C1A `CORP_MERIDIAN` | Shipping-container stripes (45°) | Container crane | kept |
| Halcyon Civic | #8C7BFF `CORP_HALCYON` | Concentric civic rings | Clock tower | kept |
| Orbital Commons | **#7FA8FF** `CORP_ORBITAL` | Star-dot grid | Satellite dish | **changed** from #DDE3FF, which was indistinguishable from UI text |
| REBEL_CELL (handler AI) | #E8141E `CORP_REBEL_CELL` | Scan-glitch bars (horizontal broken lines) | Inverted Cell hexagon | kept; the pattern is **mandatory** because the hue sits near `HARM` |

Rules:
- A corp hue MUST NOT be used for any UI role in §3.3.
- In a campaign against a corp, that corp's hue may tint the city grade (§9.3), but UI tokens don't change.
- Threat routes always carry chevrons (STYLE_GUIDE 5.3) in the corp pattern. The Cell's links are solid `CELL_TURF`.

### 3.7 Contrast minimums
- Body text and any number the player needs: **4.5:1** against its actual background (measured over the city through the scrim).
- Large text (≥ 24 px) and icons that carry meaning: **3:1**.
- Unaffordable, disabled or locked items MUST still meet 4.5:1 for their label. Show unavailability with `DISABLED` outline plus a lock or reason, not by fading text.

---

## 4. Typography

### 4.1 Faces (licences: STYLE_GUIDE 3; confirm before release)

| Role | Face | Case | Used for | Never |
|---|---|---|---|---|
| **Verb display** | Permanent Marker, drawn as drip graffiti (`GraffitiTag`) | CAPS | SEND IT, LOOT, CONTINUE, JACK OUT, VICTORY, DEFEAT, page scrawls. **Verbs and outcomes only.** At most 2 per screen. | Labels, headings, body text, anything with a number. |
| **Zine display** | Anton | CAPS | Card titles, HP, Heat, big numbers, stamp words, top-bar values, panel titles on paper. | Paragraphs. |
| **Handwriting** | Permanent Marker (plain) | Mixed | Notes, marker annotations, costs in marker, crew names on Polaroids. | Anything under 16 px. |
| **System** | Share Tech Mono | Mixed / CAPS for labels | Glass labels, lists, logs, DISPATCH, map labels, legends, tooltips (≤ 3 lines). | Text blocks over 3 lines. |
| **Body (new)** | IBM Plex Sans Condensed (OFL) | Mixed | Any text block over 3 lines: Codex, event story, card detail, long tooltips, end-screen story beats. | Headings or labels. |

DISPATCH stays Share Tech Mono on clean surfaces (STYLE_GUIDE 3) regardless of length. Wrap it at ≤ 64 columns.

All faces MUST be imported with MSDF rendering so they stay crisp at every text scale and resolution.

### 4.2 Type scale
Sizes are in reference pixels of the 1280×720 base viewport, **before** `Settings.text_scale`. Every size is multiplied by `text_scale`; there are **no exceptions** (§4.3).

| Step | Size | Line height | Use |
|---|---|---|---|
| `caption` | **12** | 1.3 | Legend rows, keybind hints, tertiary meta. **The floor: nothing the player reads is smaller.** |
| `body` | 15 (`UiTheme.BASE_SIZE`) | 1.4 | Default glass text, list rows, card rules text. |
| `label` | 18 | 1.25 | Emphasised rows, chip text, button labels, forecast lines. |
| `title` | 22 | 1.2 | Panel titles, section headings. |
| `heading` | 30 | 1.1 | Screen titles, stamp words, HP numbers. |
| `display` | 44 | 1.0 | Big numbers (Heat on the poster), verdict banners. |
| `hero` | 64–96 | 1.0 | Verb graffiti (SEND IT), VICTORY, FLATLINED, campaign verdicts. |

- Numbers in the combat hub fit the hub at every text scale (STYLE_GUIDE 5.2); use `heading` and shrink to `label` before overlapping anything.
- Line length: ≤ 70 characters for body text; wider panels use two columns.
- Tracking: Anton +2%, Share Tech Mono labels in CAPS +8%, everything else default.

### 4.3 Hard type rules
1. **Every** font size comes from the scale via `UiTheme` and is multiplied by `text_scale`. A literal size in a view is a bug. Example: `ui_theme.gd` sets a fixed 22 on one button variant; that must become `roundi(22 * text_scale)`.
2. No text below `caption` (12) at text scale 1.0. That includes map labels, tier pips labels, legend rows, microchip text, LAST TURN rows and the subtitle band.
3. No mid-word breaks ("Accelera/tor"). Wrap at word boundaries; if a word can't fit, the component grows or the text shrinks one step. Never hyphenate automatically.
4. Text never overlaps text. Numbers never sit on top of other numbers, needles, or the words they describe.
5. Live text in a display face must fit its container at 140% of its English width (localisation slack). The logo, MODEM / CYBER SHOP sign and NEVER SLEEP / TRUST NO ONE scrawls are **baked art** with translated subtitles where needed (§10.6).

---

## 5. Layout

### 5.1 Grid and spacing
- **8 px grid** (4 px half-step for tight UI). Margins, gutters, paddings and component sizes are multiples of 4.
- Screen safe margin: **24 px** at 1280×720 (scales with the viewport; TV-safe mode 5%).
- Panel padding: 16 px horizontal, 12 px vertical. Gutter between panels: 16 px.
- Spacing tokens: `xs 4`, `s 8`, `m 16`, `l 24`, `xl 32`, `xxl 48`.

### 5.2 Structure of every page
1. **Top bar** (existing sticky-note stat tags, `HudBar`): fixed height, never scrolls, never wraps. It fills its width evenly; tags don't grow with long values.
2. **Subtitle band** (`SubtitleStrip`) directly under it when present (STYLE_GUIDE 4). One line at 1.0; up to two lines at larger scales, never clipped mid-sentence.
3. **Content**: one primary region plus at most two secondary regions.
4. **Prompt bar** (`PadPrompts`) at the bottom on **every** page when a pad is active, including title, slots and options.

### 5.3 Panel rules
- Panels **size to their content** up to a maximum; they never leave more than 25% of their area empty. When content is short, the panel shrinks (pause menus, event panels, the crew roster, loot).
- Content that exceeds a panel scrolls **inside** the panel with a visible scroll hint. It never clips mid-row.
- A modal is centred with a `SCRIM` behind it, and **keeps one size across its tabs** (e.g. the loadout's DECK / SPINNER).
- One **primary** action per state (`CELL_PINK` filled). Everything else is secondary or tertiary.
- Grid layouts (dossiers, cards, market items) fill their columns: 3 columns at 1.0, reflowing to 2 then 1 as text scale grows.

### 5.4 Resolution and aspect
- Base design 1280×720, with 1920×1080 and 3840×2160 verified. UI scales with the viewport; the city renders at native resolution.
- 16:10 and 21:9: content stays in the 16:9 safe column; the city extends to fill.
- Steam Deck (1280×800) is a target: text scale default 1.2 on that device.

---

## 6. Components

Every component lives in `scripts/ui/kit/`, is styled from `UiTheme` and `Palette`, and defines **all** states:

| State | Treatment |
|---|---|
| Idle | – |
| Hover | Lift 2 px, glow +20%, cursor change |
| Focus (pad/keys) | `FOCUS` 4-corner brackets 2 px thick, offset 4 px, plus a 1.03 scale (T1). Visible from 3 m on a TV. |
| Pressed | Down 1 px, glow −20% |
| Disabled | `DISABLED` outline, label at 4.5:1, lock or reason |
| Error / refused | `HARM` flash, no-entry mark (STYLE_GUIDE 5.4) |

### 6.1 Wheels (combat hero)
- **Physical hardware.** Each wheel has a bezel (outer ring), slice inlays (translucent, bright rim, bold glyph per STYLE_GUIDE 4), a hub screen, and a gauge needle with counterweight.
- **Ownership by bezel, not position.**
  - Operative: a scratched `PAPER`-stickered bezel with a `CELL_PINK` rim, and the operative's Polaroid mini-portrait inset at the hub's top.
  - Enemy: a machined bezel in its corp hue with the corp pattern (§3.6), a notched "hostile" edge, and the enemy portrait or hologram above (§7.2).
  - `FOCUS` brackets mean "targeted" only.
- **Class identity** (operative): each class has a unique bezel ornament, hub pattern and hub glyph (§7.1). No two classes share a bezel. Portrait tints are unique per class.
- **HP** lives on a thick segmented arc under each wheel (≥ 10 px), coloured per §3.5, with a ghost segment for forecast loss and a two-stage drain (white lag, then fill). The HP number sits below the arc in `heading`. It is never under a needle's sweep; for multi-needle bosses, HP moves outside the bezel.
- **Boss wheels** are 120% of normal size, with a nameplate banner (PAPER, taped) and phase pips on the HP arc.
- The hub shows the name, then status words. Only one stamp at a time is allowed in the hub: PHASE, NO DAMAGE and similar queue, they don't stack.

### 6.2 Forecast tags (PAPER)
- One tag per wheel, above it, titled with that wheel's own outcome ("DEFEND · PERFECT AIM").
- Chips describe **what this wheel does**. What the player *receives* is summarised once, as a net line under the operative's HP ("−3 ♥ (7 − 4)"), not repeated on the operative's own tag.
- Chip order follows STYLE_GUIDE 5.2 (damage to you first). At most one row at 1.0; overflow shows as "+N MORE" and never hides damage.
- A tag never covers the nudge arrows or their prompts. It sits at radius + 66 px or wider.

### 6.3 Cards (PAPER)
- **Frame:**
  - Cost gem top-left (marker numeral in a circle).
  - Title in Anton `label`.
  - Illustration window, 60% of the card height.
  - Effect band at the bottom: glyph plus key number in `heading`.
  - Rules text in Plex `body`.
- **Rarity is shown by stock:** common = photocopy paper, uncommon = glossy sticker, rare = holographic foil (shader, tilts with pointer or stick).
- Card colour (paper / black / pink) means **card type**, and the codex and tooltip say which.
- **Hover:** lift 12 px, scale 1.12, straighten (STYLE_GUIDE 5.2). The preview on the tags stays **through the whole drag** until drop or cancel.
- Text never truncates with "…" on a card at any text scale. The card detail view shows the full art and rules text and **never repeats** the card face's text in a second block.

### 6.4 Buttons
| Variant | Material | Look |
|---|---|---|
| Primary (1 per state) | GLASS or PAPER sticker | Filled `CELL_PINK`, `INK` or `TEXT_HI` label, icon left |
| Secondary | GLASS | 1 px `TERMINAL_EDGE` outline, `TEXT_HI` label |
| Tertiary | GLASS | Text plus icon, no box |
| Danger (delete, abandon) | GLASS | 1 px `HARM` outline, trash/X glyph (**never** the power glyph), confirm dialog |
| Verb | PAPER graffiti | SEND IT / LOOT / JACK IN stamp; one per screen |

Full-width bar buttons are only for list rows; a standalone action button is sized to its label plus 32 px.

### 6.5 Inputs (replace every native-looking control)
- **Picker:** a row of tiles (icon + name + meta) or a radial, never an OS-style dropdown. Locked options appear greyed with a lock and their unlock condition.
- **Stepper:** [−] value [+] chips with the value in `label`.
- **Toggle:** a pill switch placed **next to** its label (label left, switch 16 px right of the label's longest line in the group), with both states drawn as pills.
- **Slider:** track + handle + **value readout** ("1.6×").
- **Text field** (seeds, codes): mono, with a copy button for codes. Raw codes never appear as body text.

### 6.6 Stamps, stickers, banners (PAPER)
- **Stamps** are results (solid ink, rotated ±6°). **Forecasts** are dashed (STYLE_GUIDE 4.1). A stamp says one thing in ≤ 3 words.
- Stamps are held long enough to read: at least 0.6 s plus 0.05 s per character.
- Only one banner per region at a time; others queue.

### 6.7 Toasts and refusals
**One** toast style: a `NOTE_YELLOW` sticky with tape, a glyph (no-entry for a refusal, info "i" otherwise), the text in `label`, positioned near what it refers to, or bottom-centre when global. The terminal-line toast is retired. Refusal feedback follows GIF 13's model (Modem buy refused): flash the resource tag in `HARM`, show NEED n · HAVE m, glide the item home.

### 6.8 Tooltips
GLASS, max width 36 columns, never narrower than 26 columns (STYLE_GUIDE 5.5), never covering the element it explains or its title. Input-aware wording: pad users never read "click" or "drag".

### 6.9 Top bar tags (PAPER)
Keep the sticky-note tags (a signature piece). Rules:
- One icon + label + value per tag, value in Anton `title`.
- Tags bump and roll on change (STYLE_GUIDE 5.5).
- A tag that is a drop target (CARDS, DAEMONS) shows `FOCUS` brackets while a matching item is dragged.

### 6.10 Map elements
- Node silhouettes and symbols per STYLE_GUIDE 4.1 (H24). Minimum node size 28 px, minimum placed-asset marker 24 px.
- Labels: `caption` or larger on a GLASS pill, with a leader line to the node. The layout MUST resolve collisions (no label over another label, node or number).
- "You are here" sits **on** the current node (or the street stub before the first node), never in empty space.
- Legends are GLASS panels that fold to a MAP KEY button at text scale > 1.3 (existing pattern). They never move or jump when the page rebuilds.

---

## 7. Characters and art assets

### 7.1 Operatives (eight classes)
Each class has a unique **silhouette** (head and shoulders), **accent colour** and **prop**:

| Class | Accent | Silhouette / prop cue | Bezel ornament |
|---|---|---|---|
| Breaker | `CELL_PINK` | Heavy jacket, crowbar-antenna | Riveted plates |
| Wrecker | #FF7A1A | Welding visor, scars | Welded, dented rim |
| Ghost | #9FE8FF | Hood, face-mesh | Flickering translucent rim |
| Phantom | #C8B6FF | Mask, long coat collar | Afterimage double rim |
| Rigger | #FFD24D | Goggles, cable harness | Cable-wrapped rim |
| Overclocker | #FF4FD8 | Heat-sink crown, LEDs | Vented heat-sink fins |
| Botnet | #7BE07B | Drone halo | Orbiting dot ring |
| Hivemind | #B04DFF | Linked-node headset | Hex-cell lattice |

Accent colours sit **only** on the class's portrait, bezel ornament and dossier stripe, never on UI roles.

**Portraits** (final pipeline, STYLE_GUIDE 7):
- Painted, 1:1, 1024 px master, strong value contrast.
- Four expressions: neutral, hurt, triumphant, flatlined.
- Per-operative variation from the id hash (existing `PortraitArt` pattern) applies to hair, visor and tint **within** the class accent.
- Shown through the screen's material shader (Polaroid print on PAPER, scan lines in the net).

### 7.2 Enemies and bosses
- Every enemy has a bust or hologram portrait (1:1, 768 px) in its corp hue and pattern, shown above its wheel.
- Bosses get a large hologram (≈ 40% screen height) behind their wheel, plus an intro sting: name slam in Anton `display` on a taped banner.

### 7.3 Card illustrations
- Style: **two-colour risograph/halftone** with slight misregistration, on photocopy texture, fitting the PAPER material. Ink colours: `INK` plus one of the card-type colours.
- Master size 768×512 (3:2), shown in the card's illustration window.
- Minimum set: one illustration per card. A budget pass may share about 30 base illustrations tinted per type; rares and class cards are unique.

### 7.4 Icons
- `StatIcon` / `SliceIcon` / map painters stay the single source (STYLE_GUIDE 4.1).
- New icons follow the same grammar: 24 px grid, 2 px stroke, round caps, filled when active, drawn in `INK` on paper and in the role colour on dark.
- No font glyphs or emoji as icons (the status glyphs ☠ ⚡ ⌗ ✺ are to be redrawn as `StatIcon`s).

---

## 8. VFX tiers

Spectacle scales with importance. Every effect declares its tier in `ui_motion.tres` (the `tier` field), and the effects layer enforces the tier's limits.

| Tier | Examples | Max screen coverage | Max duration | Brightness / flash | Shake / hit-stop |
|---|---|---|---|---|---|
| **T0 ambient** | City traffic, signs, idle wheel shimmer, caret | Whole backdrop (behind scrim) | Looping, slow (≥ 3 s period) | No flashes | None |
| **T1 feedback** | Hover, tick, nudge, focus, number bump | Element + 16 px | 0.25 s | +20% glow | None |
| **T2 outcome** | Hit, block, buy, drop, stamp | Element + 25% of its region | 0.6 s | Local flash ≤ 60% alpha, element only | 1–2 px shake, 2-frame hit-stop |
| **T3 moment** | Perfect, kill, phase change, Heat band, claim | The region (a wheel, a panel, a district) | 1.2 s | Local flash ≤ 70% alpha, **never full screen** | 3–4 px, 3 frames |
| **T4 cinematic** | Boss intro, VICTORY on a boss, campaign end, FLATLINED, jack in/out | Full screen | 2.5 s (skippable) | Full-screen grade change allowed; a white flash ≤ 40% alpha, once | Camera move instead of shake |

Rules:
- **No full-screen colour flash below T4.** This retires the magenta Perfect flash and the green phase-3 flash; they become T3 wheel-local effects (STYLE_GUIDE 5's "wheel-local inversion" is the intent).
- Flash limiter: ≤ 3 flashes/s globally, enforced by the effects layer, not per effect.
- Reduce effects: T0 loops stop; T1–T3 show end states; T4 becomes a cross-fade; no shake, chromatic aberration, scanline roll or flicker (STYLE_GUIDE 5.1).
- Each slice type has its own hit VFX shape (so outcomes read without colour): crit = shattered-glass burst, attack = slash streak, shield = hex plates, evade = afterimage smear, afflict = glitch crawl, heal = rising plus-signs, miss = static.

---

## 9. The city (CITY material)

### 9.1 Look
STYLE_GUIDE 1.1 stands: tinted-slate buildings, five neon inks, marker-stroke streets, district landmarks, the Cell's raised-fist roads.

Additions:
- **Lighting:** emissive neon with HDR glow tuned per ink; two to three haze bands in depth; wet-street reflections on the ground plane; rim light from the brightest signs.
- **Grade:** per-context LUT. HQ is warm and dirty (window view); the net is cool and high-contrast; combat raises contrast and dims the city 35% behind wheels.

### 9.2 Life (T0)
Traffic dashes on busy streets (existing), aircraft blinkers, occasional drone patrols, billboard loops in corp hue and pattern, window lights toggling slowly. Density follows Heat (§9.3). Everything stops under reduce effects.

### 9.3 State reactivity
| State | City response |
|---|---|
| Heat COOL | Calm, baseline traffic |
| Heat NOTICED (25+) | Slow searchlight sweeps over the target corp's district |
| Heat FLAGGED (50+) | Patrol drones, red/blue rim flicker on corp buildings (≤ 1 Hz, off under reduce effects) |
| Heat HUNTED (75+) | Desaturated grade (−25%), heavier haze, sirens (audio) |
| Territory claimed | Spray tags projected on the district's buildings, `CELL_TURF` hatch and light leaking into haze (replacing the flat khaki tint) |
| Campaign progress | Grade shifts 0 → 20% toward the target corp's hue |

### 9.4 No placeholders
The city never shows flat blocks. The next district bakes during the transition; if it isn't ready, show the district's silhouette pre-render (STYLE_GUIDE 5.3 ANIM-R3) and fade to the bake.

### 9.5 Maps over the city
On Grid, Route and Raid, the city behind the map is dimmed 40% and slightly blurred so nodes, links and labels sit forward. Nodes, links and labels are never dimmed.

---

## 10. Motion principles

Values live in `ui_motion.tres`; helpers in `Motion` (STYLE_GUIDE 5.1). This section sets the principles and budgets those values must satisfy.

1. **Acknowledge within 50 ms.** Every input gets a visible response (a T1 effect) at once, even if the full motion follows.
2. **Anticipation → action → follow-through → settle** for every drag, drop, buy, stamp and card play. A result that is only a label change (e.g. the rank-3 ring swap, crew → JACK IN) is **not done**: the target must visibly change (fill, recolour, stamp).
3. **Budgets:**

| Motion | Budget |
|---|---|
| Page transition | ≤ 0.35 s, one direction per material (glass slides from the right, paper drops from above) |
| Modal open/close | ≤ 0.22 s (never a cut) |
| Stamp | 0.12 s in, held per §6.6 |
| Number roll | ≤ 0.4 s |
| Toast | 0.18 s in, 2.5 s hold, 0.2 s out |
| Typing | ≥ 45 characters/s (subtitle and story), always skippable |
| SEND IT resolve | ≈ 2 s at 1×; speed option 1× / 2× / instant; hold to fast-forward |

4. **One thing moves at a time per region.** Sequence, don't stack. For example, the forecast clears, *then* wheels respin, *then* the hand redeals.
5. **Nothing reflows under the pointer.** A grid keeps a ghost gap until the drop (shred, remove). A panel never changes height when its selection changes (site card).
6. **Continuous space.** Moving between CITY screens (HQ → Grid → Route → combat) travels the camera through one city rather than cutting. A modal never outlives a page change: the page changes after the modal closes.
7. **Skip rules** are STYLE_GUIDE 5.1 ANIM-R1…R4, unchanged.

---

## 11. Screen blueprints

Each blueprint gives the **focal order** (what the eye hits first to last), the **materials**, and **must/never**. Implementers MUST match the focal order.

### Title
- Focal order: logo → Continue → city.
- DECK frame optional; menu on GLASS with `SCRIM`; one PAPER note plus one scrawl anchored to the menu panel (not floating).
- Logo is baked art with an idle drip (T0). Prompt bar present with a pad.

### Campaign slots
- Each slot is a **case-file card** (PAPER folder on GLASS): corp hue stripe and landmark glyph, Heat bar, run count, last played, crew Polaroids.
- Actions: Load (primary), Delete (danger, confirm).
- Never plain text rows.

### New campaign
- A **planning table**: target corp as dossier tiles (locked corps visible and greyed with their unlock), ICE as a stepper, home server as tiles, crew as Polaroids, seed and codes in a folded GLASS drawer.
- One primary: START.

### HQ
- DECK frame around the room.
- Focal order: JACK IN stamp → Grid monitor (CRT, curvature, amber readouts) → WANTED poster → crew.
- Crew in 3 columns. Black Market grouped under headers (Recruit / Boosts / Unlocks) with an icon per item, price tags per §6.4, locked items per §3.7.
- Pause menu sized to content.

### City Grid
- Focal order: selected Site → its card's primary → map → runs list.
- **One primary per state** (JACK IN when a Site is selected; RAID SETUP only when a raid is pending, and then it is the primary and JACK IN is secondary).
- Site card keeps a fixed height. Runs rows contain their chips.

### Raid setup and playout
- Forecast stamp (dashed) → map → armory.
- During playout the stamp reads **LIVE**, and **RESULT** after; it never keeps the "IF THE RAID RUNS NOW" wording.
- Continue disabled per §6 (never faded magenta).
- The end camera frames the verdict banner and home.

### Route
- Map first, route list second (compact). "You are here" on a node. Route key folds like the MAP KEY.

### Combat
- Focal order: the two forecast tags → the wheels → the hand → SEND IT.
- Wheels per §6.1. The top-right Polaroid and Heat poster are compact (≤ 12% of the screen).
- LAST TURN row in `caption` or larger. The NEXT plate explains itself with a word ("NEXT TURN −56"), not just a number.

### Loot
- Modal at 70% of screen width, cards at hover size. The graffiti title fits inside the modal.
- The chosen card flies to CARDS **before** the page leaves.

### Modem
- Keep the sign (baked), panel colour-coding and BUY stickers.
- Microchip text at `body`. Replace the socket dropdown with slot tiles. One Cycles readout (the top bar).

### Events
- Story on PAPER sized to its text (Plex `body`). Speaker plate once (no repeats). Choices with outcome icons (existing).
- The subtitle band never repeats the on-page text.

### Codex
- An illustrated zine spread: section tabs, two columns, glyphs at 24 px beside each entry, Plex body text.

### Options
- GLASS. Toggles beside their labels (§6.5). Slider with value. Tabs for Accessibility / Display / Audio / Controls / Language. A live preview of text scale.

### Stats and achievements
- Achievements as sticker badges (earned: full colour; unearned: outline + lock). Stats in a 3-column grid. Run history as taped receipts.

### Run failed (FLATLINED)
- T4: the portrait flatlines, the city grades to grey, then the FLATLINED stamp at `hero` size centred. Stats on a receipt below. Never a black void.

### Campaign end (WON / LOST)
- Distinct templates. WON: the corp landmark falling, the corp's hue and pattern crossed out in spray, a CORP DOWN stamp, crew Polaroid wall. LOST: the Cell's hexagon cracked, a CELL BURNED stamp, a grey grade.
- Story beats in Plex body. Actions as §6.4.

---

## 12. Accessibility (part of the look, not an add-on)

- **Text scale** 1.0–2.0. At every step nothing clips, overlaps or truncates; panels scroll; wheels stay at least 70% of their 1.0 size (text yields before the wheels do).
- **Colour-blind modes** (deutan, protan, tritan) remap corp and semantic hues. Patterns and glyphs (§3.6, §8) make every state readable in greyscale. Test every screen in greyscale.
- **Reduce effects** and **flash limiter** per §8. Plus a separate **reduce motion** toggle (no camera moves, no parallax, cross-fades only).
- **High-contrast mode:** opaque panels (no blur), `TEXT_HI` on #000, 7:1 minimum.
  - **PAPER in high contrast:** PAPER keeps its stock colour, but text goes `INK` at 7:1 and edges 2 px `INK`; nothing on paper is translucent (tape, fills). `PaperInk` in the kit applies it.
- **Pad:** face-button glyph sets for Xbox, PlayStation, Switch and Steam Deck, switched automatically. Prompts use glyphs, never letters in brackets. The focus treatment per §6. Every drag has its button path (STYLE_GUIDE 5.4).
- **Localisation:** see §4.3 rule 5. Glyphs and numbers stand alone from words (never embed a number inside a translatable sentence where it can't be read without the words).

---

## 13. Technical art (Godot 4.7)

- **Canvas layers:** CITY (SubViewport, own grade/blur) → map overlays → GLASS → PAPER → FX → modals → toasts → subtitles → prompts. A component never draws above its layer.
- **Shader library** (one folder, shared uniforms): `glass_blur`, `crt_overlay` (city and glass only, STYLE_GUIDE 1.1), `foil`, `paper_burn`, `glitch_dissolve` (jack), `marker_stroke` (stamps, circles), `halftone`. Each exposes a `reduce_effects` uniform.
- **Fonts:** MSDF for all faces; sizes only via `UiTheme` (§4.3).
- **Performance:** 60 fps locked at 1080p on Steam Deck; post stack and particles budgeted per tier.
- **Automated visual checks** (extend the review-pack harness):
  - Render every screen at 1.0 / 1.6 / 2.0, mouse and pad, reduce effects on and off, plus greyscale.
  - Lint: fixed font sizes, overlapping Control rects, clipped text, contrast < 4.5:1, text < 12 px.
  - Diff against the previous build.

---

## 14. Definition of done (every screen or component change)

- [ ] Uses only §3 tokens, §4 type steps and §5 spacing. No literal colours or sizes in the view.
- [ ] Materials are not mixed inside a component (§2).
- [ ] Focal order matches the blueprint (§11); one primary action per state.
- [ ] All six component states exist (§6).
- [ ] At text scale 1.0, 1.6 and 2.0: no clipping, overlap, truncation, mid-word break, or text < 12 px.
- [ ] Contrast meets §3.7, including disabled and locked items.
- [ ] Readable in greyscale (colour-blind check) and with the scrambled-text pass (icons and numbers carry meaning).
- [ ] Pad: prompt bar present, glyphs correct, focus visible, no mouse wording.
- [ ] Motion within §10 budgets; VFX within its tier (§8); reduce effects shows end states, no full-screen flash below T4.
- [ ] No placeholder city, no empty panel over 25%, no leftover elements after transitions.
- [ ] Review stills and frame strips captured and added to `docs/timeline/`.

---

## 15. Changes from STYLE_GUIDE.md

These rulings override the STYLE_GUIDE. Update it to point here.

| Topic | STYLE_GUIDE said | Art bible says | Why |
|---|---|---|---|
| Damage colour | Pink is damage on maps and in fights; enemy projectiles red | All harm is `HARM` #FF4433; `CELL_PINK` is brand and primary only | Pink meant both "the Cell" and "you got hurt" |
| Orbital Commons | #DDE3FF starlight | #7FA8FF + star-dot pattern | Indistinguishable from UI text |
| REBEL_CELL corp | #E8141E | Kept, but its scan-glitch pattern is mandatory | Near `HARM` |
| Fonts | Three faces | Adds IBM Plex Sans Condensed for body text over 3 lines | Share Tech Mono is tiring in long text |
| Precision Perfect | "wheel-local inversion" | Kept; explicitly **no full-screen flash** below T4 | The shipped build flashes the whole screen |
| Ownership | Implied by slice colour and position | Bezel hardware per §6.1 | Both wheels looked alike |
| Class look | Portrait by class kind | Unique accent, silhouette, bezel per class (§7.1) | Classes read as identical pairs |
| Toasts | Two styles in use | One sticky style (§6.7) | Consistency |
| HP colour | Green arc | Green / amber / red scale (§3.5) | 1/60 was still green |
| Heat colour | Not specified | Never green; COOL/NOTICED/FLAGGED/HUNTED scale | Heat 62 read as "good" |

---

## 16. Open questions (owner to decide; do not implement until resolved)

**Resolved 2026-09-28** (DECISIONS "Art pass (branch `art-pass`)"): 1 = ~30 tinted bases + unique rares and class cards; 2 = §7.1 accents accepted; 3 = IBM Plex Sans Condensed; 4 = full DECK frame. Items below stay for the record.

1. Final card illustration budget: unique per card or the ~30-base tinted set (§7.3)?
2. Class accents in §7.1 are proposals; confirm them against the portrait painter's concepts.
3. Body face: IBM Plex Sans Condensed vs keeping Share Tech Mono with better line length. Plex is the recommendation.
4. Whether HQ gets the full DECK frame (monitor bezel, keyboard edge) or keeps the current window-over-city composition.

Add new questions here rather than improvising.
