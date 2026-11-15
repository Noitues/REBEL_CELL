# Takeover actions: PACKET LADDER and DEFACE rendered, 2026-11-15

Two of the inspiration concepts rendered as finished plates in the locked style, on the `BOARD` / `PLAY` state. Designer: "Try the packet ladder, but also want to see the deface rendered." The DEFACE definition comes first (it was written before the render), then the plates.

## DEFACE, defined
**Pitch.** Taking the corp's wheel is defacing it. Your actions are linocut stencils taped to your wall; you hold one over a
wedge, the cut-out shows where the paint lands, and confirming sprays the pink overprint. Effects that last stay on the wedge as
sprayed tags.

**The stencil (one action).**
- The sheet is cut to the shape of what it can touch: a **wedge-shaped sheet** for an action aimed at a segment (WORM, BREACH,
  GUARD, TIME BOMB), a **round sheet** for an action aimed at the hub (NUDGE). The shape is the target class at a glance.
- Material: bone paper, black linocut key line with the block drop, pink scissor halo (the locked runner layer). Old pink
  overspray rings every cut, so it reads as a used spray stencil.
- The cut-out is the action's glyph and its name in bridged stencil letters.
- The **type word** (CONTROL, VIRUS, FIRE, BLOCK, DELAY) is a label of tape across the narrow end, in the locked plate colours
  (teal for an aimed action, lilac for one you don't aim).
- The **hotkey** is a paper key cap on the sheet's top-left corner (1-5, left to right, top to bottom).
- **Cost and target rule** sit on a small cyan-glass payload tag pinned under the stencil (the system layer): RAM coins with the
  cost, then the rule in words ("3 damage next to yours").

**Piles.** Under the stencils: DRAW = the uncut roll (count), DISCARD = peeled stencils (count), EXHAUST = burnt (count).
The game words stay primary; roll / peeled / burnt are the picture.

**Can't use.** A strip of red HARM tape reading NO RAM goes across the stencil, its paper goes dull, and its payload tag turns red and says why ("CAN'T USE, needs 4 energy").
Its key does nothing; clicking it shakes the tag.

**One play.**
1. **Pick:** press 3 or click BREACH. The stencil comes off the wall (its place keeps a dashed ghost and the tape), its payload tag
   lights pink, and every legal wedge takes the FOCUS corners.
2. **Aim:** move to a wedge. The stencil is held over it, turned to the wedge, slightly off-true like a hand holds it. The cut-out
   shows the paint in pink on the wedge, and the B-088 outcome mark on the wedge updates (TAKEN). The HUD line says the play and
   the END TURN totals with it. Over an illegal wedge the stencil does not settle; it tilts away and the tag says why.
3. **Confirm:** click or Enter. The pink sprays through the cut-out; the stencil peels off to DISCARD.
4. **Result:** a taken wedge becomes punk print (already the locked owner material). A lasting effect (virus, guard, bomb timer)
   stays as a sprayed tag on the wedge's outer edge with its count (V1, G2); the corp's own statuses keep the teal stamped chips.

**Forecast.** Unchanged B-088: outcome marks on the wedges at rest, numbered arrows and the same steps in the HUD on hover.
**Flanks.** Left: your wall (health tape, energy, stencils, piles, UNDO). Right: the corp's compliance board in slate enamel
(site, wheel rule, turn, escalation, plan notices NOW / T+1 / T+2, armed types), then the cyan payload terminal (owned, forecast
totals) and END TURN.

## Plates
| File | What it shows |
|---|---|
| `pl_rest.png` | PACKET LADDER at rest (BOARD): five packet strips on your lifeline, the plan inbound on the corp lifeline, B-088 marks on the wedges, HUD totals. |
| `pl_aim.png` | PACKET LADDER aiming BREACH at the corp FIREWALL (PLAY): strip and port lit, dashed packet P1 along the rim groove into wedge 2, TAKEN, play line and totals in the HUD. |
| `df_rest.png` | DEFACE at rest (BOARD): five stencils taped on your wall with payload tags, V1 and G2 as sprayed tags, the corp compliance board, HUD totals. |
| `df_aim.png` | DEFACE aiming BREACH at wedge 2 (PLAY): the stencil held over FIREWALL with the pink paint in the cut-out, a dashed ghost on the wall, TAKEN, play line in the HUD. |
| `render_sheet.jpg` | The four plates, 2x2, with captions. |

All four share: the wheel moved to the screen centre (same wheel, pointers, hub, HOT arcs, outcome marks and FOCUS corners as
`tk_board.png`), the YOU health tape and energy row top left, UNDO (Z) bottom left, the cyan forecast panel and the pink END
TURN (Space) bottom right. Same sample state as `BOARD` / `PLAY`: NUDGE 0, WORM 1, BREACH 1, GUARD 1, TIME BOMB 4 (can't use).

## PACKET LADDER: how it reads
- One action = one thin header strip (no art) torn off a print run, pointing at its port on your lifeline. Fields in a single
  row, like a header diagram: **key** (ink key cap) | **name** | **len** = cost (RAM coin) | **flag** = type word on the locked
  plate | **dst** = target (HUB, 3 CORP, CORP·ADJ, YOURS, CORP). The rule sits under it as plain text, Wireshark's Info column.
  One column header names the fields once, so the strips stay thin.
- Can't use: the strip goes grey with a red outline, its port is a red ring, and a red **RST** tab says why ("RST · needs 4 energy").
- Piles at the lifeline's foot: DRAW / DISCARD / EXHAUST first, with queued / sent / dropped as the small word.
- Right flank: the corp host header (solace.sys, wheel kind and rule), INBOUND plan packets NOW / T+1 / T+2 on the corp lifeline
  (the locked ticket values), the ARMED legend for the HOT arcs.
- Aim: the picked strip slides into its port with the pink scissor halo; the others dim; legal wedges take FOCUS corners; the
  packet runs **along the rim groove** (the gunmetal channel between the wedges and the rope) and turns into the wedge with
  the B-088 arrow head, labelled `P1 BREACH −3`.

## Calls made
1. **Wheel to the centre**, both flanks used (brief allows it). Done by setting `tk_render.CX` and its polar helper at import
   time; `tk_render.py` and `tk_states.py` are not edited, and the wheel, segment, hub, pointer, outcome-mark and badge
   drawing are imported from them.
2. **Packet route along the rim groove**, not across the wheel. This solves the "long arrows cross the wheel" risk from the
   inspiration doc and keeps every label clear; it passes under the top pointer.
3. **Packets are strips with an arrow tip and an info line, not boxes**: one header row, no card art, torn left edge, hairline
   field rules. The fields are the card's data (cost, type word, target, rule), so nothing is lost.
4. **Game words first, network words second** (DRAW 7 / queued, END TURN / send, UNDO / rollback, RAM for energy only in the
   packet ladder's header). The net words are dress until the designer rules on them (inspiration open question 2).
5. **`P1` numbers your own play** (your first packet this turn), next to the engine-order numbers (11.1, 13.1) used on hover.
6. **DEFACE stencil shape = target class**: a wedge-shaped sheet for segment actions, a round sheet for the hub action (NUDGE).
7. **DEFACE cost and rule live on a cyan payload tag** under each stencil (system layer), so the stencil itself is all print.
8. **The held stencil covers the wedge's own label.** The result is carried by the cut-out paint, the B-088 TAKEN mark and the
   HUD play line. The stencil sits slightly off-true (1.2°, 4 px) so it reads as held, not placed.
9. **Sprayed tags replace the stamped status chips only for your effects** (V1, G2); the corp's own statuses would keep the teal
   chips (none in this state).
10. **Stencil letters are not bridged.** Bridged Anton read as wrong letters (B as D, N as H); the stencil reads from the cut,
    the key line and the overspray instead.

## Limits
- Concept plates: the locked measured checks (a-e, value order) were not run.
- Numbers are illustrative and copied from `BOARD` / `PLAY` (including PLAY's "on FIREWALL 2: 3 damage, takes it").
- Glyphs are borrowed from the locked Shifting Waves cards (NUDGE Nudge, WORM Hold, BREACH Strike, GUARD Brace, TIME BOMB
  Trigger), as on the current plates.
- The packet route and all label positions are hand-set. In the game both need an auto-placer (the B-088 one already owed).
- WORM (three targets) is drawn only at rest; its three-wedge aim (three packets / three sprays) is not shown.
- An illegal hover (stencil tilting away, "binds" reason) is described, not drawn.
- The left flank is fuller than the right; the space between the forecast panel and END TURN is open on rest plates.
- The backdrop is the locked bio room re-centred on the wheel, with a dark scrim on the flanks; not re-graded.

## Files
- `pl_rest.png`, `pl_aim.png`, `df_rest.png`, `df_aim.png` (1920x1080), `render_sheet.jpg`.
- Source: `D:/rc_scratch/takeover/inspiration/insp_render.py`. Run `python insp_render.py` (all four plates and the sheet,
  one process) or name plates: `python insp_render.py pl_aim sheet`. It imports `D:/rc_scratch/takeover/src/tk_render.py`
  and `tk_states.py`, and through them the locked `rb_tokens`, `card_render`, glyphs and fonts.

## Deface v2, 2026-11-15
Designer on v1: "Really it's just reshaped cards though, right." Correct: five stencils, each with its own name, cost tag, type
tape and key, were a hand of cards with a new outline. v2 keeps every mechanic and breaks the card shape.

| File | What it shows |
|---|---|
| `df2_rest.png` | Rest (BOARD): one cut sheet on your wall with five cuts and hand marks, the paint can at 3/3, the worn GUARD shield and the spreading virus tag on the wheel. |
| `df2_aim.png` | BREACH aimed at FIREWALL (PLAY): its cut lifted out of the sheet (an empty window marked "lifted") and laid on wedge 2, paint showing through; FOCUS corners on CORE and FIREWALL; the can previews 3 → 2; the rule in the HUD. |
| `df2_after.png` | After confirming BREACH: wet pink BREACH paint on wedge 2 (5 → 2, TAKEN), the cut back in the sheet but clogged with paint and marked "used", DISCARD 3 → 4, the can at 2/3, the HUD line "BREACH sprayed: FIREWALL 5 → 2, TAKEN" and the totals. |
| `df2_sheet.jpg` | The three in a row with captions. |

**What changed**
- **One sheet per turn, not five objects.** The hand is a single bone-paper stencil plate, torn off the roll and taped up.
  - Each action is a **cut** in it. The glyph and the name are the holes; the knife outline round the cut is the target class
    (wedge = a segment, round = the hub).
  - DRAW = the roll above the sheet (7 cuts left). DISCARD = clogged cuts (they peel off with the sheet at END TURN; the count
    goes up when you spray). EXHAUST = burnt cuts.
- **Hand marks, not tag boxes.** By each cut, written on the sheet:
  - the circled key (1-5);
  - the type word in the type plate's ink (teal; deep lilac for CONTROL);
  - cost as drips plus the number;
  - the target in pencil ("the hub", "3 corp", "next to yours").
  The full rule appears only in the HUD while you aim (hover).
- **Can't use:** red tape across the TIME BOMB cut, written "needs 4", with red drips.
- **Energy is paint.** A spray can with a fill gauge (one band per energy) replaces the coins. A pending cost shows as a hatched
  band and "3 → 2".
- **Playing is painting the wheel.**
  - Aim lifts the cut piece out of the sheet and lays it on the wedge at the wedge's angle. Confirm sprays it.
  - The paint stays on the wedge under its re-inked label, and the B-088 outcome mark sits on top.
  - Lasting effects are paint that wears: GUARD (G2) is a painted shield, patchy where it has been hit; the virus (V1) is a tag
    with small marks spreading toward the hub.
- **Unchanged:** the corp compliance board, the HUD panel (OWNED and END TURN totals), END TURN and UNDO.

**Why it no longer reads as cards.** There is one object, not five. The actions are holes in the same material, not things with
frames, so nothing can be "held in a hand". The data that made v1 look like a card face (cost, type and rule boxes) is now
marks on a working surface. Each play leaves its result on the wheel itself, so the wheel, not a panel, carries what you have
done this fight.

**Calls**
- A sprayed cut counts as discarded right away (DISCARD 4 in the after plate), matching the card rule. The clogged sheet peels at
  END TURN.
- The painted wedge's own label is re-cut in ink over the paint so its integrity stays readable.
- UNDO after a spray puts the paint back in the can.

**Limits**
- No new mechanics were added. The TIME BOMB countdown tag is described but not drawn (not in this state); WORM's three-wedge
  spray is not shown.
- Handwriting is Anton and Plex jittered per letter, not a real hand font.
- The left flank is denser than the right; the space between the HUD panel and END TURN is still open.
- The paint, sheet and cut positions are hand-set; locked checks not run; numbers from BOARD / PLAY.
- Source: `D:/rc_scratch/takeover/inspiration/insp_deface2.py` (`python insp_deface2.py`, or name plates). It imports
  `insp_render.py` (v1) and `tk_render.py` unchanged; the v1 plates are untouched.

## Deface v3, 2026-11-15
Designer on v2: "The original art bible had user using stickers as buttons and grease pen marking up the monitor for movement
and action. I think deface shaped stickers, grease pen for targeting sticker, and grease pen for forecast and such. Playing the
sticker lifts it off the screen, places it on the corp wheel, then it dissolves into bits and is played."

| File | What it shows |
|---|---|
| `df3_rest.png` | Rest (BOARD): five deface-shaped vinyl stickers slapped on the glass at varied angles. The B-088 forecast is grease pencil on the wedges (yellow "→9", "→4"; red "LOST −1 HP"). HUD totals, RAM pips, SEND IT over EXECUTE. |
| `df3_aim.png` | BREACH peeled and held (peel curl, long soft shadow, its liner outline left on the glass). A yellow pencil line runs from it over the rim to FIREWALL 2, with "−3"; pencil loops round the legal wedges (CORE, FIREWALL); TAKEN in pencil. RAM hatches the cost (3 → 2); the rule shows in the HUD. |
| `df3_play.png` | Three panels: place (slapped, squash, white contact ring), dissolve (scan front, 0/1 bits in the sticker's pink, a stream round the rim), resolve (bare Anton −3, FIREWALL 5 → 2, TAKEN in pencil). Plus a small full-screen copy of the result (sticker gone, liner left, RAM 2/3, DISCARD 4, HUD totals +1 taken). |
| `df3_hover.png` | Your ICE hovered: numbered pencil arrows 11.1 (−2 from the hub), 13.1 (−3 from CORE), 11.2 (BLOCK 2, a yellow bracket on the wedge), 16.1 on the LOST mark; the same steps listed in the HUD (designer ruling). |
| `df3_sheet.jpg` | The four plates, 2x2, with captions. |

**What changed from v2**
- The stencil sheet and the paint can are gone.
  - Actions are **die-cut vinyl stickers**, each in a street-sticker silhouette that reads as the action: an impact burst (BREACH),
    a shield (GUARD), a bomb with a fuse (TIME BOMB), a wriggle (WORM), a spin tag with an arrowhead (NUDGE).
  - Each sticker has an Anton name with an ink key line and extrude, the type word on its locked plate, the yellow cost dot, a key
    chip (1-5), a white die-cut border and gloss 0.22.
- **Energy is RAM again**: terminal pips (bible 3.1). The aim hatches the cost.
- **Piles** are one terminal line (DRAW 7, DISCARD 3, EXHAUST 0). **UNDO** is a terminal chip.
- **SEND IT** is the pink vinyl verb over the washed-out `EXECUTE` and `> turn_resolve.exe [SPACE]` (bible 1.3).
- **Grease pencil** (wax: opaque, dropouts, sheen line, ink edge, under-shadow) does all the marking up:
  - aim line and legal loops;
  - the B-088 outcome marks;
  - the numbered hover arrows and their badges.
  The HUD totals line and the hover step list stay as before.
- **Play** follows bible 3.18: peel (curl, liner outline) → slap onto the wedge → Dissolve A into 0/1 bits in the source colour
  → the effect from the slap point.

**Bible lines followed**
- 1.2: the media table.
  - Stickers are fixed objects.
  - Pencil is plans that are true to the rules: yellow for our plan, red for threat or loss, solid for what will happen.
  - Bits are 0/1 glyphs in the source colour, white-hot first, going round the rim.
  - The fiction: "Pencil is the Cell thinking".
- 1.3: SEND IT over a system word.
- 2.9: Anton sticker lettering; Permanent Marker as wax at 28-36 px (floor 26); Share Tech Mono bits.
- 2.10: a focused or hovered sticker shows only the peel-back corner curl, with no lime halo.
- 3.1: RAM terminal pips; UNDO as a terminal chip.
- 3.18: die-cut, gloss band, yellow cost dot, greyed dot when it can't be afforded; peel, then a pencil line from the card
  to the target and a pencil loop round the valid target, then slap (squash 1.13 / 0.86, contact ring, RAM paid, pencil
  wipes), then dissolve A; the effect comes from the slap point.
- 3.19: pencil 7 px with an ink edge.
- The sticker and wax code is the repo's own `cohesion/map_pages_r42/scripts/sticker_lib19.py`, imported read-only.

**Calls made**
1. **Red as well as yellow.** Bible 1.2 already gives the pencil red `#FF1C2C` for threat, invalid and loss; 3.19's
   "yellow only" is about the plan line. So the plan, the aim, the legal loops, our results (→ n, TAKEN) and our GUARD block
   are yellow; the corp's hits (11.1, 13.1), LOST −1 HP (16.1) and the can't-use reason are red.
2. **Forecast numbers in pencil.** Bible 1.2 lists "live numbers" under the pencil's Never column. These marks are the
   END TURN forecast, true to the rules (pillar 4), which is the pencil's job, and the designer asked for them. The live values
   (integrity, RAM, health) stay engraved or terminal. **Designer ruling, 2026-11-15: allowed.** Grease pencil may carry
   forecast numbers, as an exception to bible 1.2's Never column. Live values stay engraved or terminal.
3. **Deface silhouettes without spray texture.** Bible 1.2 rejects spray paint and stencils as a medium, so the deface reads
   from the die-cut shapes; the surface stays clean vinyl.
4. **Pencil is never covered.** The held sticker sits above the wheel's top-left, clear of every pencil mark; the TAKEN mark
   moved onto the dark ring to clear the wedge word.
5. **The can't-use state follows the designer's brief**: greyscale vinyl at 80 %, a grey cost dot, and a red pencil
   "needs 4" with an arrow. Bible 3.18's NEED tag is replaced by the pencil reason.
6. **The marker font has no arrow glyph**, so "→ n" is a short pencil arrow plus the number.
7. The `−3` result is bare Anton (bible: live big numbers).

**Limits**
- Statuses (V1, G2) still use the stamped chips from the locked plates; bible 1.2 would make temporary effect words stickers.
  Not changed here.
- The sticker art uses the borrowed card glyphs; the silhouettes are a first vector pass.
- The idle bob, the gloss sweep and all motion are stills only; the dissolve is one frame.
- WORM's three-target play and an illegal aim (the red pencil "invalid" mark) are not drawn.
- Pencil positions are hand-set (an auto-placer is owed). The locked checks were not run. Numbers come from BOARD / PLAY / FORECAST.
- The left flank is denser than the right, with open space above SEND IT.
- Source: `D:/rc_scratch/takeover/inspiration/insp_deface3.py`. Run `python insp_deface3.py`, or name plates. It imports
  `insp_render.py`, `tk_render.py` and `sticker_lib19` without changing them; the v1 and v2 plates are untouched.

## Deface v3: missing states, 2026-11-15
| File | What it shows |
|---|---|
| `df3_worm.png` | WORM peeled and held. Three yellow pencil loops round CACHE, TURRET and NODE, numbered 1-3 in pick order. One pencil line runs from the sticker over the rim into loop 1, then on to 2 and 3. "+V" (+1 virus) sits on each target. The HUD shows "WORM 1 virus on CACHE, TURRET, NODE" and "3 of 3 picked (click a loop to drop it)". RAM hatches 3 → 2. |
| `df3_invalid.png` | BREACH held over your own NODE. The sticker won't stick: it stays curled and lifted, with a long soft shadow. A red pencil circle-and-slash sits on the wedge (the bible's nudge-lock mark), with "it's yours: needs a corp seg next to yours" written beside it. CORE and FIREWALL stay looped in yellow. The HUD reads "BREACH can't go on your NODE" and names the legal wedges. |
| `df3_status.png` | Your statuses as small die-cut vinyl stickers (bible 1.2): BLOCK 2 on your ICE, SEAL on your FIREWALL, VIRUS 1 on corp NODE. The corp's own seal on SPAWNER stays the enamel glaze lid with SEALED. A TIME BOMB bomb-sticker sits on corp RELAY, with "2 turns, then −6" in pencil. VIRUS 1 is hovered: it lifts with a peel curl, its numbered pencil arrow 5.1 points at NODE's "→4" mark (with "−1"), and a CRT tooltip explains it. |
| `df3_states_sheet.jpg` | The three in a row, with captions. |

**State changes for these plates** (otherwise BOARD):
- **Worm:** no other change.
- **Invalid:** no other change. The legal wedges come from PLAY.
- **Status:**
  - your G2 and V1 chips are replaced by the stickers;
  - added your SEAL on FIREWALL (seg 1) and a corp seal on SPAWNER (seg 7);
  - a TIME BOMB, played on an earlier turn, on RELAY with 2 turns left.
  The END TURN totals are left as BOARD's, because the bomb does not fire this turn.

**Calls**
1. **WORM picks in order.** The numbered loops show the pick order, and one pencil line visits them. Clicking a loop drops it,
   and Enter is only live at 3 of 3. The virus outcome is "+V" by each loop. NODE's own "→4" moved aside to make room.
2. **The illegal mark reuses the bible's red circle-and-slash** (the nudge lock, 3.1). The reason is red pencil at the wedge
   in the rule's words. The sticker shows "can't stick" by staying curled and lifted, with no slap.
3. **Statuses are pill-shaped mini-stickers** in the action's colour family: BLOCK blue, VIRUS green, SEAL pink. The
   corp's own effects keep the enamel / teal material. A count (BLOCK 2, VIRUS 1) is printed on the sticker. Bible 1.2 says
   stickers never carry a changing value, so a count change is a new sticker swapped in, not an edit. **Open question for
   the designer:** confirm this.
4. **TIME BOMB:** a small bomb-sticker stays on the target. Its turn count and the coming 6 damage are pencil (forecast),
   below the rim where there is free space.
5. **Status hover** reuses the action hover: the peel curl and lift, the numbered pencil arrow to the outcome it feeds (A3
   step 5.1), and a CRT tooltip for the rule. No new medium is added.

**Limits**
- WORM with fewer than 3 legal targets, and a partial pick (1 of 3), are not drawn.
- In the invalid plate the held sticker sits over the ICE / NODE border and covers the G2 chip. The slash is on NODE.
- The status sticker positions and the pencil are hand-set. The VIRUS curl is small at this size.
- The source is `D:/rc_scratch/takeover/inspiration/insp_deface3b.py` (`python insp_deface3b.py`). It imports
  `insp_deface3.py` unchanged.
