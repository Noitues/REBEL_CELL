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

---

## Actions without cards (follow-up, 2026-11-14)

The designer's point: a card only performs an action against a target. So the hand can stop being
cards, and stop being card-shaped chips. Four options follow. All four use the direction A layout
(the rig on the left, the wheel in the centre, the corp on the right). The yellow text on the
wireframes is annotation.

**The mechanics stay the same in all four.** Each action shows its RAM cost, whether it takes a target
or not, its type word (CONTROL, VIRUS, FIRE, BLOCK, DELAY) and a hotkey (1-5). The STACK / SPENT /
PURGED counts stay. An action you can't use is red and gives the reason ("needs 4 RAM, you have 3").
The B-088 forecast is unchanged: an aimed action previews on the wedges. The colour of each type word
is a wireframe placeholder. The locked type-plate colours would replace it.

### A1. Command line
`alt_act_1_command_line.png`
- **Pitch:** each action is a command. The target is its argument.
- **Play and aim:** press 1-5 or click a command. Its argument slot (`<host>`, `<yours>`) waits for
  a target. Click a wedge to fill it. The prompt under the wheel shows the full line and its result
  ("$ breach FIREWALL#2 -> 5 becomes 2"). Enter runs it; Esc cancels. A no-target command (`nudge
  --spin +1|-1`) runs at once or takes an inline flag.
- **Cost and piles:** "1 RAM" at the end of each line. A command you have run greys out of the list
  into SPENT. A purged command is struck through.
- **Style layer:** system (cyan terminal). The runner's pink is used only for the command names.
- **Risks:** it is text-heavy and has no picture to recognise. It is close to direction B. The aim is
  less physical, though the argument slot does tell you the target rule.
- **Effort:** S.

### A2. Tool ring (target first)
`alt_act_2_tool_ring.png`
- **Pitch:** pick the segment first. A radial ring of the tools that can act on it opens beside it.
- **Play and aim:** click or Tab to a segment. Its tools fan out. A legal tool is bright; an illegal
  one is red and says why ("only on yours", "needs 4 RAM"). Press the tool's number or click it.
  No-target tools (NUDGE, WORM) sit on the hub ring. The tool belt on the left shows the whole hand
  as round icons with a cost badge and a key. You can still pick from the belt first and then the
  target.
- **Cost and piles:** a cost badge on each belt icon. A used tool leaves the belt for SPENT.
- **Style layer:** the belt icons are punk print; the radial menu is system glass.
- **Risks:** the radial covers neighbouring wedges and their forecast marks. Target-first is a
  second way to play, and it must agree with tool-first. The icons need art.
- **Effort:** M.

### A3. Daemons (recommended)
`alt_act_3_daemons.png`
- **Pitch:** each action is a small agent that you dispatch onto a segment. Agents whose effect
  lasts stay on the wheel where you can see them.
- **Play and aim:** pick a daemon in the bay (1-5 or click). Drag it, or click a wedge. It travels
  there with the "5 -> 2" preview, then acts. A no-target daemon (NUDGE) lands on the hub. WORM
  splits into three on its targets.
- **What stays on the board:** GUARD sits on your segment as "G3" until the turn's cleanup. A TIME
  BOMB stays parked with its countdown ("2"). A virus shows as "V1". These are the runner-made
  statuses and charges, drawn as the daemon that made them. They replace the small stamped tags.
- **Cost and piles:** the RAM cost is on each bay row. A daemon that has acted goes to SPENT; a
  parked one goes to SPENT when it expires. A purged one burns out.
- **Style layer:** the daemons are runner punk print (hex badges with the pink key line), so they
  read as yours against the corp's enamel.
- **Risks:** the tokens need room on each wedge. They would share the outer edge with the status tags
  (B-088 moved those there). Travel motion adds about 0.2 s per play, and it must be skippable. The
  hover trace must start at the daemon token (for example, 11.2 BLOCK starts at G3).
- **Effort:** M. Six small badges, plus a slot rule on the wedge.

### A4. Patch bay
`alt_act_4_patch_bay.png`
- **Pitch:** each action is a jack on the deck. You patch a cable from it into a segment's port.
- **Play and aim:** pick a jack (1-5) and every legal port on the rim lights up. Click a port and the
  cable runs from the jack to that segment. A no-target jack patches into the hub. A DELAY cable stays
  plugged in with its timer.
- **Cost and piles:** the cost sits by each jack. An unplugged jack goes to SPENT.
- **Style layer:** the cables are runner punk colour; the ports are corp gunmetal.
- **Risks:** cables cross the wheel and hide labels and forecast marks. With more than one live cable
  it gets messy. The ports add 12 small targets on the rim.
- **Effort:** M-L.

### Recommendation: A3, Daemons
- It makes "an action against a target" literal: something goes to the target and acts there.
- It shows on the wheel what lasts (block, a delayed charge, a virus) as the runner's own pieces. The
  B-088 trace then has a clear start point for those steps.
- It fits direction A without layout changes: the bay replaces the chip rack.
- It keeps the locked three layers. The runner's punk print is now on the wheel too.
- Borrow from A2: Tab to cycle through the legal target wedges for keyboard play, with the red reason
  shown on illegal ones.

Open question: should the runner's daemon tokens replace the runner's own status tags on the wedges
(one mark per effect), or sit beside them?

Files: `alt_act_1_command_line.png`, `alt_act_2_tool_ring.png`, `alt_act_3_daemons.png`,
`alt_act_4_patch_bay.png`, `alt_actions_sheet.jpg`. Source: `D:/rc_scratch/takeover/alternatives/alt_actions.py`
(it imports the helpers in `alt_wireframes.py`; run `python alt_actions.py`).
