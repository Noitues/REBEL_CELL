# Takeover fight screen: port spec for the Deface v3 look (2026-11-15)

**For:** build (port-campaign-b, S8 fight screen on the option A layout, B-089).
**From:** art-pass, after A-119.
**Reference plates:**
- `v3/` (the full B-086 state set in v3: board, play, forecast, resolve, wall/seal, win);
- `inspiration/rendered/df3_*` (aim, play sequence, hover, WORM, invalid target, statuses).

**Rules source:** `ENGINE_ORDER.md` section A. **Words:** NAME_MAP section E (B-090).

This look is a skin and an interaction layer on build's option A layout. Nothing in the rules or the layout changes. Most of
it is already LOCKED in `docs/ART_BIBLE.md`: v3 applies the bible's sticker-card lifecycle (3.18) and grease-pencil spec to the
Takeover wheel. Where this spec and the bible differ, the designer rulings in section 7 win.

## 1. Layers (what draws what)

| Layer | Medium (bible 1.2) | On the Takeover screen |
|---|---|---|
| Runner objects | vinyl sticker | programs (LOADED), your statuses on the wheel, SEND IT, temporary result words |
| Player markup | grease pencil (wax) | aim line, target loops, the forecast (wedge outcome marks, hover arrows), status values, can't-use reasons |
| Corp machinery | enamel | corp segments, rim, pointers, hub, corp walls and seals, corp statuses, the corp SCHEDULE board (right) |
| System | CRT terminal glass | HUD header, RAM, QUEUE / SPENT / DELETED counts, the totals line, the hover step list, tooltips, ROLLBACK |
| Live numbers | engraved (wheel) or bare Anton | segment integrity, health, RAM, damage pops |

Draw order, back to front: backdrop → wheel → corp statuses → your status stickers → pencil layer → held or flying sticker →
bits → HUD → temporary labels.

## 2. Program stickers (the LOADED programs)
- **Shape:** each program has its own die-cut silhouette in a deface / tag idiom, which reads as the action. For the sample
  hand: BREACH is a burst, GUARD a shield, TIME BOMB a bomb with a fuse, WORM a wriggle, NUDGE a spin tag.
  - **Asset ask:** one silhouette plus an icon per program. The sample glyphs are borrowed placeholders.
- **Face:**
  - Anton name with the sticker key line and extrude (bible 2.9 sticker spec: die-cut border 0.14 x the lettering size,
    12 px max);
  - the type word on its plate (CONTROL, VIRUS, FIRE, BLOCK, DELAY; teal for a program you aim at a segment, lilac for one
    you don't);
  - the yellow cost dot (RAM);
  - a key chip 1-5;
  - the gloss band.
- **Placement:** stuck on the glass on the runner side at loose angles (about ±8°). They may overlap, but never over the cost
  dot, the name or the type word. The left column of option A holds them, above the QUEUE / SPENT / DELETED counts.
- **States:**

| State | Look | Source |
|---|---|---|
| idle | 2 px bob, corner curl breathes | bible 3.18.1 |
| hover / focus | peel-back corner curl only (no brackets), lift, shadow grows; the RAM meter hatches the cost; the forecast preview plays | bible 2.10, 3.18.2 |
| can't use | greyscale vinyl at 80 %, grey cost dot, red pencil reason beside it ("needs 4") | bible `DISABLED`; v3 replaces the NEED tag with pencil |
| peeled / held | the fold sweeps, the sticker pops free, and a faint liner outline stays on the glass; it follows the cursor with spring lag and tilts by velocity | 3.18.3-4 |
| can't stick (illegal target) | stays curled and lifted over the wedge; a red pencil circle-and-slash on the wedge plus the reason in the rule's words | `df3_invalid` |
| slap | drop, squash 1.13 / 0.86, overshoot, settle; white contact ring and gloss sweep; RAM is paid here; the pencil wipes off stroke-first | 3.18.5 |
| dissolve | Dissolve A: a scan front runs top to bottom; 17 px cells decode to 0/1 glyphs (19-25 px, white-hot 80 ms) in the sticker's colour and run round the rim. The bible's version spirals into the hub; on Takeover, the bits run to the effect's target. | 3.18.6 |
| effect | resolves from the slap point (bible 3.18 rule) | 3.20 |

- **Input:**
  - click or drag to peel;
  - click a looped wedge or press Enter to slap;
  - Tab cycles the legal wedges;
  - Esc or right-click sticks it back;
  - keys 1-5 peel the program in that slot.
- **Multi-target (WORM), per B-091:** the player picks one target only. The card's selector in data adds the rest (WORM:
  `target_and_corp_nb`, the target and then its corp neighbours).
  - Hovering a legal wedge while WORM is held calls S8's preview (card + hovered segment → the ordered segments). Each one
    gets a numbered yellow loop (1 = the picked target), and one pencil line runs from the sticker through them in order.
  - Slapping on the hovered wedge plays it.
  - The numbers match the resolver's order and the S4 trace.
  - `df3_worm.png` predates B-091 and shows a manual 3-pick ("click a loop to drop it"). That is superseded by `v3_worm.png`.

## 3. Grease pencil layer
- **Spec:** Permanent Marker rendered as wax, tracking 0.45, sizes 28-36 px. Strokes are 7 px with an ink edge (bible 2.9,
  3.19 / 3.22 pencil). Strokes write on (stroke-first) and wipe off stroke-first.
- **Colours:**
  - yellow `#FFE200`: your plan, aim, legal loops, your results (→ n, TAKEN), your block;
  - red `#FF1C2C`: corp hits, LOST −1 HP, can't-use reasons, the illegal slash.
- **What it draws:**
  - **Aim:** a line from the held sticker to the target. It routes over the rim, never across the hub or another wedge's
    label.
  - **Legal targets:** loops round each legal wedge while a program is held.
  - **Forecast at rest (B-088):** each wedge that COMMIT changes carries its cumulative outcome mark: "→ n" (drawn as a short
    pencil arrow plus the number, because the font has no arrow glyph), TAKEN, or "LOST −1 HP". Unchanged wedges carry
    nothing.
  - **Forecast on hover:** the numbered arrows and effects feeding the hovered wedge, each with its resolution number (A3
    step.order) in a pencil circle. The same steps are listed in the HUD (system layer), per the designer ruling of
    2026-11-15.
  - **Status values:** the count or turns beside a status sticker (section 4).
  - **Replay:** the played steps keep their numbered pencil arrows while COMMIT resolves. The hub shows the step being
    played.
- **Layout:** label positions need an auto-placer that keeps pencil labels off the wedge labels and off each other. The plates
  are hand-placed.

## 4. Statuses on the wheel
- **Yours:** a small die-cut status sticker on the wedge's outer edge (BLOCK, VIRUS, SEAL, TIME BOMB, …), in the program's
  colour family. Its value (count or turns left) is in grease pencil beside it, never printed on the sticker. When the value
  changes, the pencil rewrites, and the sticker stays.
- **Corp's own:** enamel / teal, as on the locked board. A corp seal is the enamel lid marked SEALED.
- **TIME BOMB:** a bomb sticker on the target, with "2 turns, then −6" in pencil (the countdown is forecast).
- **Hover a status:** peel curl and lift, a numbered pencil arrow to the outcome it feeds, and a terminal tooltip with the rule.
- **Walls:** yours is a sticker plank on the boundary; the corp's is the enamel steel bar.

## 5. Right side and HUD
- **The corp SCHEDULE board** is enamel tickets: NOW with the live SCHEDULE edge, T+1 and T+2 stepped down, then the ARMED list.
- **HUD** (system glass):
  - the header with the wheel rule;
  - OWNED;
  - the totals line at rest ("+0 taken −1 lost → owned 2 · health 27 → 26");
  - the hover step list;
  - the aim line ("BREACH on FIREWALL 2: 3 damage, takes it", plus Enter / Tab / Esc hints).
- **SEND IT:** the pink vinyl sticker over the washed-out system word `COMMIT` with `> turn_resolve.exe [SPACE]`. Its states
  are in bible 3.20: hover (lift, curl, gloss), pressed (squash), disabled (greyscale vinyl 80 % + RESOLVING chip).
- **ROLLBACK [Z]:** a terminal chip.

## 6. Data the look needs
Already provided by S4: the B-088 per-segment trace (resolution number, source, target, kind, amount) and the exact forecast.

Asked in A-119, answered in B-091:
1. **Multi-target order:** S8's preview (card + hovered segment → the ordered segments), from the card's selector.
2. **Reasons:**
   - `why_not(card)` gives the program-level reason (energy, rule, no_target, …): the red pencil beside a can't-use sticker.
   - S8's `target_why(card, i)` gives the code plus the rule's words for one wedge (not corp, sealed, not next to yours, no
     virus, hp above the cap, the card's own rule): the red pencil at the wedge, under the circle-and-slash.
3. **Status values:** `TakeoverSegmentState.st` maps a status id to its value (stacks, or turns left for timed statuses). The
   id picks the sticker and the value is the pencil number. Runner-side statuses work the same way on the fight state.

## 7. Designer rulings this spec depends on (2026-11-15)
1. **Card type words stay.**
2. **The forecast is on the wedges and in the HUD.** At rest it shows as the totals line; on hover, as the numbered arrows plus
   the HUD list.
3. **Grease pencil may carry forecast numbers.** This is an exception to bible 1.2. Live values stay engraved or terminal.
4. **A status is a sticker, and its value is in grease pencil.**
5. **Words: NAME_MAP section E** (B-090). Art's call, open to build: SEND IT stays the commit sticker over the system word
   `COMMIT`.

## 8. Not covered yet
- **Assets:** a sticker silhouette and icon for each program, and a status sticker set.
- **Motion:** stills only so far, no GIFs for the Takeover dissolve. Bible 3.18 / 3.20 give the beats and timings.
- **Reduce effects:**
  - no squash or bits;
  - the sticker fades out at the slap point;
  - the pencil writes on instantly.
- **Other skins:** Meridian and the other corp skins.
- **Measured checks:** not run on the plates (they belong to the polish pass).
