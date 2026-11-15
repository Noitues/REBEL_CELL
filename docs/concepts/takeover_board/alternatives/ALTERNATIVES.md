# Takeover screen: alternative directions, 2026-11-14

Art-pass proposals answering the designer's critique of the B-086 / B-088 Takeover plates
(`../tk_*.png`, `../NOTES.md`). Concept documents and rough wireframes only. No Godot work.

## What every direction keeps
- **The rules do not change.** They follow `ENGINE_ORDER.md` section A and `NAME_MAP.md` section A on
  `port-campaign-b`. The screen keeps: 12 segments, segment 0 the start, owner, type and integrity,
  3-4 fixed pointers, the plan step, counterattack, escalation, walls, seals, health loss at A5.
- **The B-088 forecast stays.** At rest, each wedge carries its cumulative END TURN outcome ("-> n",
  TAKEN, "LOST -1 HP"). Hover a segment and every arrow that feeds it is drawn with its resolution
  number (A3 step, then the order inside the step). The run health mark takes the same number.
- **Type words stay as words:** CONTROL, VIRUS, FIRE, BLOCK, DELAY.
- **Nothing hidden:** statuses, energy, draw / discard counts, plan NOW and next, END TURN forecast.
- Mouse and keyboard, text scale 1.0. An unusable action is red and says why ("NO RAM: needs 4").
- The same sample state as the plates: Static Alley, Firewall wheel, turn 3, your ICE hovered.

## The critique, restated
1. The wheel sits left, the HUD is stacked right, the hand is squeezed bottom-right. The left and
   centre-bottom of the frame are empty.
2. Playing cards, a hand and "energy" read as a card game, not as netrunning.
3. Keep the B-088 forecast and the card type words.

## Shared re-framing (used by A, C, D and E; B goes further)
The deck mechanics stay. Only the words and the objects change.

| Mechanic | Current word | Netrun framing |
|---|---|---|
| Card | card | **program** (`breach.exe`), shown as a chip or cartridge |
| Hand | hand | **loaded programs** |
| Energy | energy | **RAM** (cyan memory blocks; the cost is "1 RAM") |
| Draw pile | draw | **STACK** (programs waiting to load) |
| Discard | discard | **SPENT** |
| Exhaust | exhaust | **PURGED** |
| Run health | run health | **NEURAL LINK** (still the runner's name and the number) |
| END TURN | END TURN | **EXECUTE** (the label keeps "END TURN [SPACE]" under it) |
| UNDO | UNDO | **ROLLBACK [Z]** |
| Corp plan | corp plan | **SCHEDULE** (the daemon's queue) |
| Pointers | pointers | **trace heads** (fixed scanners that arm what they read) |

Card names (NUDGE, WORM, BREACH...) are content and stay. The `.exe` suffix is dress only.
These words are a proposal. A `DECISIONS.md` entry is owed if the designer takes them.

---

## A. ICEBREAKER RIG
`alt_a_icebreaker_rig.png`

**Pitch:** the wheel moves to the centre; the runner's cyberdeck rig fills the left, the corp
daemon fills the right.

**Screen use.** A three-column layout. The left column (about 540 px) is the runner's rig. The
centre (about 800 px) is the wheel at the same size as the plates. The right column (about 540 px)
is the corp. A thin system strip runs across the top. A one-line command preview sits under the wheel.
No zone is empty, and the two sides mirror the fight: you on the left, them on the right.

**Mechanics.**
- *Wheel and segments:* as on the plates. Your segments are punk paper; corp segments are slate enamel
  with the Solace teal edge. Integrity is the big number and the type word sits under it.
- *Pointers and spin:* gunmetal trace heads on the rim. The hub shows this spin and the next three.
  The red armed arc stays on corp segments a head will arm.
- *Corp plan:* a vertical SCHEDULE of three enamel tickets (NOW, T+1, T+2), with the locked value
  steps. Under it, "ARMED ON END TURN" lists each armed type and what its protocol does in one line.
  Corp statuses and escalation follow.
- *Forecast and hover trace:* B-088 unchanged, on the wedges. The command line under the wheel echoes
  the aimed play ("run breach.exe --target 02").
- *Walls and seals:* as on the plates (steel bar and bone plank on boundaries; glaze lid and pink tape).
- *Hand, energy, draw, discard:* the hand is a vertical rack of five program chips. Each chip shows its
  RAM cost on a black pin strip, a hotkey (1-5), the name, the type word and one line of effect.
  RAM is three cyan blocks above the rack. STACK / SPENT / PURGED counts sit under it.
- *Run health:* the punk YOU strip at the top of the rig, "27 -> 26" with the red loss hatch.
- *END TURN:* a large pink EXECUTE button at the bottom right, with the forecast totals on it
  ("owned 3 -> 2, HP 27 -> 26"). ROLLBACK [Z] is a paper tab at the bottom left.

**Netrun read.** You run programs from a rig against a daemon's schedule. The chips, RAM blocks and
command line do the work; the wheel itself is unchanged.

**Locked style.** Keeps all three layers as they are. The runner layer moves from the WPAP card to a
punk-print chip (same paper, key line and pink halo; smaller art). The corp column is enamel. The
system strip and command line are cyan glass.

**Risks.**
- The chip rack is narrower than the card art. Card illustration shrinks to an icon or goes.
- Long effect lines must fit one line at text scale 1.0 (about 30 characters at 18 px).
- Drag-to-target travels further (left rack to centre wheel). Click-then-click and hotkeys fix it.

**Godot cost:** low. Containers and the existing wheel. **Motion:** chips slide out of the rack when
lifted; nothing new on the wheel. **Effort: S-M** (about 2-3 days of art and layout on top of the plates).

---

## B. SHELL
`alt_b_shell.png`

**Pitch:** the whole screen is a tiled terminal (tmux style); you act at a prompt.

**Screen use.** Six panes edge to edge: `whoami` (top left), `ls ~/rig/loaded` (left), `netstat
--ring` with the wheel (centre), `crontab -l solace` (top right), `ps --armed` (bottom right) and a
full-width prompt along the bottom. Every pixel is a pane.

**Mechanics.**
- *Wheel:* drawn as in A inside the centre pane.
- *Pointers and spin:* as in A.
- *Corp plan:* the crontab pane: NOW, T+1, T+2 as cron lines with a `#` comment.
- *Armed protocols:* the `ps --armed` pane lists them, with escalation and corp statuses.
- *Forecast and hover trace:* B-088 on the wedges. The prompt pane also prints a one-line diff of the
  aimed play and the END TURN totals.
- *Walls and seals:* as on the plates.
- *Hand:* numbered program lines (`3 breach  1R  FIRE  3 dmg next to yours`). Keys 1-5 pick; click or
  arrows pick a host; Enter runs. An unusable line is red with "! cannot run: needs 4 RAM".
- *Run health, RAM, piles:* text lines in `whoami`, health in a punk paper tape.
- *END TURN:* a pink `commit` button (Space). Rollback (Z).

**Netrun read.** The strongest: it looks like a hacker's desktop.

**Locked style.** **Bends it.** The system layer takes over most of the screen. The runner's punk
print survives only on the health tape, the selected program and the commit key. The corp keeps its
enamel only in the wheel and the cron tickets. Why bend: it is the most direct answer to critique 2.

**Risks.**
- The highest wall-of-text risk on the list. Monospace lines are slow to scan.
- Ownership on the wheel is fine, but the hand loses all images.
- Easy to look like a debug view instead of a game.

**Godot cost:** low (RichTextLabel and panels). **Motion:** typing and cursor effects are cheap.
**Effort: S** for the layout, **M** to make it feel like a game and not a log.

---

## C. TOKEN RING
`alt_c_token_ring.png`

**Pitch:** the 12 segments become a stadium-shaped network loop that fills the 16:9 frame; the
runner works from the infield.

**Screen use.** The best fit for 16:9. The loop runs round the whole screen: five segments along the
top, one at the right end, five along the bottom, one at the left end. The infield holds the plan,
the spin, the hand, health, RAM and EXECUTE.

**Mechanics.**
- *Segments:* upright rectangles. Labels are always upright, so no label auto-placer is needed for
  the segments themselves (an open problem in the current notes). Adjacency is plain: next on the track.
- *Spin:* the ring **shifts** round the track by n slots (the "CORP SHIFT" readout, -2 then +1 +1 -2).
  Pointers are fixed sentries outside the track (top middle, bottom left, bottom right, plus a fourth
  in phase 2).
- *Corp plan:* three tickets in a row at the top of the infield.
- *Forecast:* the outcome tags sit on the infield edge of each slot. The hover trace draws arrows
  along the track and across the infield from the plan.
- *Walls:* bars between two slots. *Seals:* lid or tape on the slot.
- *Hand:* a row of five program chips in the infield, EXECUTE beside them.
- *Run health:* the punk strip under the hand.

**Netrun read.** A network loop with packets (your programs) in the middle. Token ring is a real
network shape. It reads less "wheel of fortune" and more "network".

**Locked style.** Keeps the three materials. **Drops the wheel shape**, which the locked combat family
and the prototype both use. That is a big change to the game's identity; flag it.

**Risks.**
- Spin is harder to read than rotation: 12 cells sliding round a stadium can look like a conveyor
  belt. Cells on the curves must turn the corner cleanly.
- Distance is uneven: two neighbours at a corner sit farther apart than neighbours on a straight.
- The infield is tight (about 1460 x 500). The hand cards are smaller than now.
- Trace arrows across the infield cross the hand.

**Godot cost:** medium (Path2D and PathFollow2D for the shift, custom corner cells).
**Motion:** the shift animation is the hard part. **Effort: M-L.**

---

## D. VERSUS
`alt_d_versus.png`

**Pitch:** a fighting-game frame: the runner on the left, the corp sysop on the right, the wheel
between them, the hand fanned underneath.

**Screen use.** Two tall portrait columns (about 460 px each) frame a centred wheel. The hand fans
along the bottom under the wheel. END TURN sits bottom right.

**Mechanics.**
- *Wheel, pointers, forecast, walls and seals:* as on the plates, centred.
- *Corp plan:* stacked tickets in the corp column, with an escalation bar (turn 3 of 13).
- *Hand:* five program chips in a shallow fan. Hover lifts a chip.
- *Run health:* a tall vertical bar beside the runner portrait, "27 -> 26".
- *RAM, statuses, piles:* in the runner column.
- *END TURN:* "JACK OUT TURN" button (Space), UNDO (Z).

**Netrun read.** Medium. It reads as a duel. The netrun flavour comes from the portraits and words,
not from the objects.

**Locked style.** Keeps everything. Adds two portraits (a punk runner and an enamel sysop avatar).

**Risks.**
- Two portraits are new art (two per corp skin, one per runner).
- The portraits take space that could hold information; the plan column is narrower.
- Still uses card-like chips; the least answer to critique 2.

**Godot cost:** low. **Motion:** portrait reactions are optional. **Effort: M** (portrait art).

---

## E. PLATTER DECK
`alt_e_platter_deck.png`

**Pitch:** the screen is the runner's cyberdeck seen from above: the wheel is a disk platter, the
pointers are read heads, the programs are cartridges plugged into the deck.

**Screen use.** The whole frame is the device. The platter sits centre-left. The left edge holds
the vitals monitor and RAM sticks. The right holds the corp's incoming schedule as printer tape.
Cartridges plug in along the bottom. EXEC is a big hardware key.

**Mechanics.**
- *Wheel:* the platter. Corp sectors are enamel; sectors you own are overwritten in punk print.
- *Pointers and spin:* read-head arms on fixed pivots. The platter spins under them; a head that
  lands on a corp sector arms its type. This is the most literal fit for "fixed pointers on a
  spinning wheel" on the list.
- *Corp plan:* printer tape strips (NOW bright, T+1 and T+2 greyer).
- *Forecast and hover trace:* B-088 unchanged.
- *Hand:* cartridges with gold contacts, standing in slots. An unusable cartridge is red and says why.
- *RAM:* three DIMM sticks with LEDs. *Health:* an EKG vitals screen with "HP 27 -> 26".
- *END TURN:* the EXEC key (Space). UNDO is the BKSP key (Z).

**Netrun read.** Strong and physical: the deck is a machine, the runner's stickers are on it.

**Locked style.** **Bends it.** A fourth material appears: the runner's hardware (plastic, metal,
LEDs). The punk print moves to stickers and the overwritten sectors. Why: it makes the deck a cyberdeck.

**Risks.**
- The read-head arms cross the platter; they must not hide segment labels. The wireframe stops each
  head on the rim; any longer and it covers the number.
- More texture and more objects: harder to keep calm and readable.
- A 4-pointer phase needs a fourth arm.

**Godot cost:** medium (arm sprites, one hardware frame per runner rig).
**Motion:** satisfying (platter spin, head clicks) but more to animate. **Effort: L.**

---

## Comparison

| | A Icebreaker Rig | B Shell | C Token Ring | D Versus | E Platter Deck |
|---|---|---|---|---|---|
| Uses 16:9 | good | full | best | good | good |
| Netrun read | good | best | good | fair | strong |
| Fits locked style | yes | bends (system-heavy) | yes, but no wheel | yes | bends (hardware) |
| Readability risk | low | high (text) | medium (spin) | low | medium (clutter) |
| Godot cost | low | low | medium | low | medium |
| New art | chips | little | chips, track | 2+ portraits | deck, arms, carts |
| Effort | S-M | S / M | M-L | M | L |

## Recommendation: A, Icebreaker Rig

1. It solves critique 1 directly. The wheel goes to the centre and both flanks carry information.
   The plan and the armed list get room to be read in one line each.
2. It answers critique 2 with low risk. Programs, RAM, STACK / SPENT, SCHEDULE and EXECUTE make it a
   netrun without changing a rule or the wheel.
3. It keeps the locked three-layer style and all of B-088. The plates' wheel can be reused as is.
4. It is the cheapest in Godot.

Borrow two things from the others:
- From **E**, the read-head idea for the pointers (fixed heads that "read" a segment), drawn small on
  the rim so they never cross a label.
- From **B**, the one-line command preview under the wheel and the 1-5 hotkeys on the programs.

If the designer wants a bolder break, paper-test **C** next. It uses the frame best, but it drops the
wheel shape, and the shift animation must be proven before anything else.

## Open questions for the designer
1. Take the netrun words (program, RAM, STACK, SPENT, PURGED, EXECUTE, ROLLBACK, SCHEDULE)?
2. Do program chips keep a small illustration, or icon only?
3. Is the bend in B or E acceptable, or must the three locked layers hold?

## Files
- `alt_a_icebreaker_rig.png`, `alt_b_shell.png`, `alt_c_token_ring.png`, `alt_d_versus.png`,
  `alt_e_platter_deck.png`: 1920x1080 wireframes (flat blocks and labels; yellow text is annotation).
- `alternatives_sheet.jpg`: all five on one sheet.
- Source: `D:/rc_scratch/takeover/alternatives/alt_wireframes.py` (`python alt_wireframes.py`).
- No finished mock was made for A; the wireframe plus the existing plates' wheel cover it.
