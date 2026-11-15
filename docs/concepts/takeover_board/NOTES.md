# Takeover board in the locked family (B-086), concept plates, 2026-11-15

Build's B-086 asked for one board plate and the prototype's five fight states. The brief:
- **Style:** the locked combat family's style system (ART CALL 53).
- **Layout:** the prototype's own fight screen (Campaign B v36).
- **Rules:** `ENGINE_ORDER.md` section A on `port-campaign-b`.
- **Names:** `NAME_MAP.md`, so the plan step is SURGE, not WAVE.

These are concept plates only, with no Godot work. The corp skin is Solace.

| File | State |
|---|---|
| `tk_board.png` | Board: turn 3, play phase, nothing hovered |
| `tk_play.png` | 1. Play phase, BREACH lifted: legal targets in FOCUS corners, the aimed take in grease pencil, the HUD forecast "with this play" |
| `tk_forecast.png` | 2. Forecast: wedge outcome marks at rest, your ICE hovered with its numbered arrows (B-088) |
| `tk_resolve.png` | 3. Resolution (the END TURN replay at step 13): the firing pointers lit, numbered arrows, the corp retakes your ICE |
| `tk_wallseal.png` | 4. A corp WALL pair around TURRET, your WALL, a corp SEAL on CORE and your SEAL on FIREWALL |
| `tk_win.png` | 5. Win at 12 / 12 |
| `tk_sheet.jpg` | All six on one sheet |

Source: `src/tk_render.py` (drawing) and `src/tk_states.py` (the state data). It imports the locked `rb_tokens` and
`card_render` from `../combat_redesign/locked/scratch_src/corp/src` (live copy: `D:/rc_scratch/combat_redesign/locked/corp/src`).
Render with `python tk_render.py board play forecast resolve wallseal win`, then `python tk_sheet.py`. It runs as one process,
with no Godot.

## How the locked style system maps onto the Takeover wheel
- **Ownership is material.**
  - Your segments are punk print: bone paper, pink Ben-Day dots, a linocut black key line with a block drop, a pink scissor-cut
    halo, and a misregistered pink glyph under the ink one.
  - Corp segments are enamel: slate glass cells, with the Solace teal glaze on the cell edge only, and engraved K-type glyphs
    and integrity.
  - The two read apart in grey (paper is light, slate is dark), so ownership never rests on hue alone.
- **The wheel belongs to the corp.**
  - The rim is the Solace teal rope.
  - The pointers and the spin hub are gunmetal: the clock material, the corp's time grammar.
  - A pointer that fires takes the SCHEDULE edge.
  - The hub shows this END TURN's spin and the next three.
- **Segment type** is one of eight vector glyphs (CACHE, CORE, FIREWALL, ICE, NODE, RELAY, SPAWNER, TURRET) plus the type word.
  Integrity is the big number. All three sit in one upright label group per segment.
- **Armed this END TURN** is the HOT mark: a HARM arc with its white-hot core on the outer edge of every corp segment whose type a
  pointer arms.
- **The exact forecast (system layer)** shows in three places:
  - cyan glass chips on the inner ring give each segment's integrity after END TURN. A teal fill means it becomes yours, a red
    fill means it is lost, and a SCHEDULE ring means it fires;
  - a HARM "−1 HP" tag sits on each segment the corp will retake;
  - the HUD forecast panel gives the totals, and itemises them in engine order when END TURN is hovered.
  Nothing is hidden.
- **Walls and seals** are physical pieces for both sides:
  - corp wall: an enamel steel bar with rivets and the teal edge, on the boundary;
  - your wall: a bone plank with the pink halo and the black key;
  - corp seal: a glaze lid outline with a SEALED tag;
  - your seal: a strip of pink tape across the segment's outer edge.
- **HUD** (cyan terminal glass):
  - the fight header and the wheel's rule in one line;
  - OWNED with its forecast, ENERGY as RAM coins, TURN and ESCALATION;
  - run health, as the YOU strip of punk paper taped on the terminal, with the forecast loss in the red loss hatch;
  - the corp plan as enamel tickets (NOW with the live SCHEDULE edge; T+1 and T+2 stepped down in value);
  - statuses as chips, and the DRAW / DISCARD counts.
- **Hand:** the locked WPAP cards at the locked hand scale (1.10x, rules cap height at least 16 px). An unusable card has a red
  frame and a red "CAN'T PLAY" tab that says why ("needs 4 energy"). END TURN is the pink punk button (Space), and UNDO is the
  paper tab (Z).

## Calls made (art-pass, within the locked system)
1. **Ownership** is the two locked materials (paper vs slate), not two hues.
2. **Pointers and the hub** are the clock material (gunmetal), because the spin is the corp's schedule.
3. **On-wheel forecast:** the exact forecast stays on the wheel as small system-layer chips, because the prototype shows it there
   and B-086 asks for "nothing hidden". The itemised version lives in the HUD.
4. **Statuses on segments** are small stamped tags on the inner edge. A pink keyline means you put it there; a teal one means it is
   the corp's own.
5. **Corp plan** uses the locked ticket value steps (100 / 72 / 52 %).

## Placeholders and limits
- The card icons and band art are borrowed from the locked Shifting Waves cards (NUDGE uses Nudge, WORM uses Hold, BREACH uses
  Strike, GUARD uses Brace, TIME BOMB uses Trigger). Takeover cards need their own icons.
- The card plate words (CONTROL, VIRUS, FIRE, BLOCK, DELAY) are the prototype's card groupings. The plate colour is the locked
  pair: teal for a card you aim at a segment, lilac for a card you don't. Takeover card types are not settled.
- The eight segment glyphs are a first vector pass.
- **No measured checks:** the locked checks a-e and the value order were not run on these plates. They are concept plates, and the
  checks belong to the polish pass.
- In the resolution plate, the arrows cross some segment labels.
- **The numbers are illustrative.** The states use plausible values in the prototype's rules, not a recorded seed.
- The backdrop is the locked bio room under a dark pool, not re-graded for this board.
- **Not done:** Meridian or other skins, motion, and effects.

## Revision 2026-11-15: B-088 (designer on A-116 question 2), the forecast lives on the wedges
The itemised END TURN forecast panel is gone. In its place:
- **At rest, every plate:** each wedge that END TURN will change carries its cumulative outcome as a system-layer mark on its
  inner edge, half on the wedge and half on the dark ring:
  - cyan glass "→ n" for the integrity after END TURN;
  - teal glass "TAKEN" for a segment that becomes yours;
  - red "LOST −1 HP" for a segment that is retaken, with its health cost.
  Unchanged wedges carry no mark. The segment status tags moved to the outer edge to make room. The run health strip keeps one
  cumulative mark ("27 → 26", with the red loss hatch).
- **Hover a wedge (`tk_forecast.png`, your ICE hovered):**
  - the wedge takes a cyan inspect outline;
  - every arrow and effect that feeds its outcome is drawn, each with a resolution number (ENGINE_ORDER A3 step, then the order
    inside the step), so it reads in sequence;
  - the run health mark takes the same cyan outline and the matching number.
  The example trace:
  - 11.1: the plan STRIKE from the hub, −2;
  - 11.2: your GUARD blocks 2, shown as a P-stock plate tied to the wedge;
  - 13.1: CORE's counterattack, −3;
  - 16.1: LOST, −1 HP, on the outcome mark and on the health mark.
- **Replay (`tk_resolve.png`):** the replay uses the same numbered arrows. The hub shows the step being played (13, COUNTER), and
  the steps played so far keep their numbered arrows (8.1 RELAY repairs CORE +2, 11.1, 11.2, 13.1), with the retake burst.
- **What is left in the HUD:** the one-line card hint while you aim a card (play), a one-line WALL / SEAL key, and the fight result
  (win). None of these is a forecast list.
- **Data:** build's forecast returns a per-segment trace (resolution number, source, target, kind, amount). The plates draw from
  that shape (`trace` in `src/tk_states.py`).
- **Limits:**
  - In the replay, the long RELAY → CORE arrow crosses two segment labels.
  - Label placement is hand-set per plate. In the game, labels need an auto-placer that keeps them off the wedge labels.

## Designer rulings, 2026-11-15 (on A-116, given to art-pass directly)
1. **Card type words stay** (CONTROL, VIRUS, FIRE, BLOCK, DELAY) on the type plate.
2. **The forecast is shown in two places:**
   - **At rest:** on the wedges (outcome marks) and in the HUD (one totals line: taken, lost, owned after, health after).
   - **Hovering a segment:** the numbered arrows on the wheel (B-088), and the same numbered steps listed in the HUD.
   - The plates are re-rendered to match: board, play and wall/seal carry the HUD totals line; forecast lists the hovered
     wedge's steps 11.1, 11.2, 13.1, 16.1 in the HUD. This replaces "What is left in the HUD" in the B-088 section.
3. **Direction (A-116 Q3) not approved as is.**
   - The space either side of the wheel is wasted.
   - The board is not strongly hacker / netrunner themed: playing cards is not on theme.
   - An agent is exploring alternative visual approaches that keep the mechanics. Its output goes in `alternatives/`.
4. **Direction in progress: Deface v3** (`inspiration/rendered/df3_*`). Actions are deface-shaped vinyl stickers on the glass,
   grease pencil does the aim and the forecast, and a play is peel → slap on the wedge → dissolve into bits → resolve. The
   alternatives, Packet Ladder and Deface v1 / v2 were not taken.
5. **Grease pencil may carry forecast numbers** (an exception to ART_BIBLE 1.2, which lists live numbers under pencil's Never).
   Live values (integrity, RAM, health) stay engraved or terminal. To fold into the bible when this direction locks.
