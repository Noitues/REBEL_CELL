# BB_bible: ART_BIBLE-faithful Shifting Waves (E4 state, seed 4, turn 1)

Scope (designer change): Waves only. Tower dropped.
Plates: `D:/rc_tmp/combat_critic/plates/bible/waves/` — `p1_decide`, `p2_preview`, `p3_resolve` (strict) and `conflict_p1/p2/p3` (minimal deviation).
Sheets: `plates/bible/compare_sheet.jpg` (bible | pass-3/4, squint and deutan rows) and `plates/bible/strict_vs_conflict.jpg`.
Source: `BB_bible/src/` (`bb_lib.py` wheels, `bb_plates.py` cards/chips, `bb_build.py` plates, `sheet.py`). State: `state_bb.json` from `dump_bb.py` (the D4_E4 sim, read-only import; seed 4 = same state as waves_e4). Every number on the plates is read from it.
Reused (copied): round41 `scripts/` (slicelib/roster_wheel/combat_wheel = the real D4 "Lens & rail" wheel with family-C CRT slices), round31 backdrop gif, round17 glyphs. Type patched to the bible faces (Anton, Share Tech Mono, IBM Plex Sans Condensed).

## 1. Locked rules that apply to a combat screen (checklist, ✔ = obeyed on the strict plates)
- 1.2 media jobs: world = backdrop only ✔; vinyl = cards, name sticker, SEND IT ✔; grease pencil = plans only (yellow underline under the HP chips while aiming, p2) ✔; CRT = slices, RAM/Trace, top bar, range plate ✔; bare Anton = HP numbers ✔; bits = p3 shards ✔. Corp paper / holo: unused.
- 1.1 #4 preview equals result (this-turn chips = sim preview) ✔.
- 2.1/2.2 tokens: CELL_PINK, NET_CYAN, HARM #FF4433 (with "-" and boxed), GAIN, PENCIL_PLAN, TERMINAL_*; never colour alone (glyph + word + number on every mark) ✔.
- 2.3 slice colour = slice TYPE, never ownership; ownership = bezel/kit ✔ (this drives a finding, see 3.4).
- 2.9 type: Anton sticker/values, Share Tech Mono terminal (floor 18), Plex body (floor 20). Floors broken by the concept itself, see 3.2.
- 3.1 layout: player wheel (481,490) r220, enemy wheel (1438,520) r236, backdrop fills, top bar plate, name sticker bottom left, RAM terminal, SEND IT pink over EXECUTE, UNDO chip beside it, hand bottom centre, HP chips beside the HP value in order `[final] (absorbed) +shield -other` ✔; **no forecast tags, no NEXT plates** ✔ (strict); nudge buttons above wheels: NOT drawn (nudge is a card here, see conflicts); RESPIN: not in this concept.
- 3.2 Lens & rail: one wheel frame, cream blade, readout rail over the pointer ±50° split around the needle, telemetry ring ✔; HP arc under the wheel with predicted loss ✔.
- 3.3 hub cores: Breaker core on the code base ✔; enemy hub = corp chevron hub (Meridian emblem) ✔.
- 3.4 family C slices, upright read block (glyph + value), 3 ring depth cells drawn the same way ✔ (cells 50 px thick, see verdict).
- 3.5 glyph set: slice glyphs reused; unit glyphs, HP plate glyph, card glyphs are **EXTENSION** (white silhouette + ink outline, 16 px twin check not run).
- 3.8 overlays/badge in the outer clockwise corner ✔ (used for HP badges); broken slice = **EXTENSION** state.
- 3.14 backdrop: close-up of the attacked place, wheels softened ~55 % ✔ (round31 Meridian HQ close-up reused; the real regular fight would be the DEPOT lot).
- 3.17 card-play preview: ghost chevrons outside the rim, ghost cells, only while the card is hovered ✔; no arrows/gates ✔.
- 3.18 sticker cards: white die-cut, yellow cost dot, family band, peel curl on the hovered card ✔.
- 3.20 FX (p3): 0/1 shards in the attacker's colour across the gap, popped numbers, blocked label, no log strip ✔.
- 3.21 clutter: read block on top, one badge per slice, values that do not fit move to chips ✔ (stress-tested, see verdict).
- 5.1 never colour alone ✔; 5.2 16 px glyph rule: unit glyphs not twin-checked (EXTENSION).

## 2. Extensions I had to invent (marked EXTENSION)
1. Wave wheel = ONE enemy wheel with 3 concentric rings x 6 sectors (ring depth 0 innermost = lands now). Cells use the family-C screen; Meridian orange bezel = ownership, pink/violet screens = attack/afflict by slice type (rule 2.3).
2. Unit read block = unit glyph + arriving damage; unit HP = corner badge (plate glyph + number, `22>8` when this turn's fire changes it).
3. Unit glyph set: Packet, Worm, Jammer, Payload; card glyphs Shove/Stall/Twist; HP-plate glyph; trace eye.
4. Sector numbers 0-5 as ink chips on both rims (the only link between the two wheels; the needle = sector 0).
5. Slice HP as a corner badge on the code-base wheel with predicted loss (`6>0` red); broken slice overlay.
6. Wave schedule printed on the wave wheel's readout rail (WAVE TURNS | HOLD +1 +1), bible-size.
7. Adjuster HP as the enemy HP number + range plate; `-19` deal chip with the unit glyph (damage to units, not Adjuster).
8. Absorbed chip `(22 plate)` and slice-loss chip `-21 plate` as "other losses".
9. Trace as a second terminal row under RAM with hatched lockdown cell and "FIGHT ENDS NOW = N HEAT".
10. Family bands TOWER / WAVE on cards (bible Appendix B open item), LOUD eye + "+N".
Not drawn: the Adjuster drone (docked satellite) on the rim: left out of the strict plates for room (information lost: its position on the wave wheel; only HP/range remain) — a gap, listed as a slip below.

## 3. Conflicts (bible lock vs concept)
- C1 **No forecast tags / no NEXT plates (3.1)** vs a 3-turn forecast. Strict: rings 1-2 are visible units, but WHERE they will land (the ring turn) is only printed on the rail at ~9 px, and next-turn cost is absent. CONFLICT plate adds ghost cells for the next position, a `NEXT -51` chip, and the WAVE TURNS cells.
- C2 **Locked two-wheel layout (3.1)** vs one board where the wave sits around the code base. Strict: the sector link is by number chips only; the player must cross-read 0-5 between wheels 960 px apart. CONFLICT plate: wave wheel r300, code base r195 (still two wheels, layout positions moved).
- C3 **Preview = this turn only (3.17, 1.1 #4)** vs Twist, whose whole value is next turn. p2 strict: the HP chips are identical to p1 (-24 / 22 / -21). The only change is the dashed ghost cells and the rail. A new player sees a card that does nothing. CONFLICT plate adds `NEXT -51` (was -57).
- C4 **Nudge buttons above each wheel (3.1)** vs nudge/twist as cards. Buttons omitted; either the buttons go (cards only) or cards become the free-nudge shortcut. Needs a designer call.
- C5 **Readout rail text (3.2)** at wheel size r236 is ~9 px: unreadable at 1080p, below the 16 px bar. In the CONFLICT plate it is promoted to bezel cells.
- C6 **Colour = slice type, never ownership (2.3)**: enemy attack cells are pink like our BURST/TURRET. Hits vs guns are told apart by bezel hue (orange vs pink/teal) only; threat red is only on chips. Strict plate keeps it; this hurts the squint.
- C7 **Enemy wheel has HP (3.2)**: here the enemy wheel has none (Adjuster is a separate unit); the HP slot holds Adjuster HP.

## 4. Verdict per bible section
| § | verdict | evidence (sheet) |
|---|---|---|
| 1.2 media jobs | **HOLDS** | the table sorts every mark cleanly: cards vinyl, plan pencil, systems CRT, shards bits. Better than pass 3 in one respect: pass 3 uses glass chips and 3D enamel for things the bible says belong to CRT/vinyl |
| 2 palette/type | **EXTEND** | tokens hold; need a THREAT-on-slice rule (C6) and a rule for a "wave" family colour (orange is the Meridian bezel and the pass-3 wave colour) |
| 3.1 screen layout | **RETHINK** (for this concept) | two far-apart wheels need the sector links (C2); hand + HUD fit fine; p2 hover card hits the enemy wheel bottom |
| 3.1 no forecast / HP chips | **EXTEND** | HP chip row works well and is the cleanest bill in either version (p1/p3). But a forecast is the concept's core: add a bible-legal forecast surface (C1/C3), e.g. a "NEXT" chip row beside HP |
| 3.2 wheel frame | **HOLDS** (EXTEND for rings) | the frame reads instantly; rail text too small (C5): add a "schedule bezel cells" rule |
| 3.3 hubs | **HOLDS** | emblem hubs fine; the wave hub needs its own emblem (WAVE) |
| 3.4 slices family C | **EXTEND** | works as a unit cell, but a 50 px thick ring cell cannot take an upright block + HP badge: diagonal sectors overflow (p1 zoom). Needs "ring cell: stacked block, HP badge as pips" rule |
| 3.5 glyphs | **EXTEND** | 4 unit glyphs + HP plate + trace eye + Shove/Stall/Twist; twin check needed |
| 3.8 overlays | **EXTEND** | BROKEN state needed (black-out + red X is in p3); jam/lock stay |
| 3.14 backdrop | **HOLDS** | strongest cohesion: it IS the city/raid look; pass 3's tower-top cutaway is original but breaks "close-up of the place attacked" only mildly |
| 3.17 card-play preview | **EXTEND** | ghost chevrons + ghost cells work, but ghosts on a busy 3-ring wheel are clutter (p2); needs a "ghost cell shows number only" rule and a next-turn surface |
| 3.18 sticker cards | **HOLDS** | die-cut white vinyl cards read as the player's hand and pair with the city; family band (TOWER/WAVE) needs ratifying; pass-3 K cards are the same idea with stronger family colour |
| 3.20 FX | **HOLDS** | shards across the gap, pop numbers, blocked label: replaces the replay chip strip (a K pick) with the bible's own language at lower text load; but a still cannot show order (animation covers it) |
| 3.21 clutter | **EXTEND** | rules cope with slice-level stacks; a 3-ring field with 10 units + badges + ghosts exceeds them |
| 5 accessibility | **HOLDS** | glyph+number+word everywhere; deutan row: both versions keep value hierarchy; the bible version loses hue separation of hits vs guns |

## 5. Honest read of the comparison
- Bible strengths: unmistakably the same game as the city/raid/netrun (pink/teal CRT wheels, white vinyl cards, Anton HP, the real backdrop); the HP chip bill is the best parity read; type is on the project faces; FX language is native.
- Bible weaknesses for Waves: (1) the unit cells are small dark tiles — the squint row shows the threat cluster is barely visible against the navy field, where pass 3's red enamel units and cyan rings read as a place; (2) the wave rotation and next-turn landing, which is the concept, are invisible without a hover; (3) two distant wheels make the sector link a numbers exercise; (4) p2 preview shows no change this turn.
- Pass-3/4 strengths: structure is a board (concentric rings around the code base) that explains itself; threat red vs plan yellow separation; all schedule and lane info visible. Weaknesses: break several locks (3D enamel units on a wheel, glass chips as a second chip family, recoloured wheel, replay strip, forecast text blocks), and the screen is the busiest in the game.
- CONFLICT plates (strict_vs_conflict.jpg): a bigger wave wheel (r300), the WAVE TURNS bezel cells and the `NEXT` chip restore the schedule and the forecast in the bible's own language and stay readable; the cost is a moved layout and a new forecast chip.

## 6. Recommendation: AMEND the combat chapter (not rewrite, not keep as is)
Five most important changes:
1. Add a **forecast surface** rule: a NEXT chip row beside the HP chips (this turn | next turn), exempt from "no forecast tags", for modes with scheduled threats. (C1, C3)
2. Add **ring-wheel / multi-ring enemy wheels**: concentric ring cells on a family-C wheel, stacked upright block, HP as corner badge, sector numbers on the rim, and permission to scale the enemy wheel to r~300 when it carries the board. (C2, 3.4 verdict)
3. Add a **schedule bezel** (cells on the wheel's outer edge: arrow/step, HOLD bar, yellow twist cell) as the readable form of the readout rail whenever the rail text would fall below 16 px; make the rail rule "text >= 16 px or move to chips". (C5)
4. Add **threat colour on slices**: enemy attack cells keep type hue but get a HARM-red trim/LED and the corp bezel, so hits and guns separate at squint; define a wave/orange family token. (C6)
5. Add the **new states and glyphs**: BROKEN slice overlay, unit glyph set (16 px twin check), HP plate glyph, TOWER/WAVE card family bands, and decide whether nudge buttons survive when cards do the turning. (C4, 3.5, 3.8)

## Questions for the designer (no rules changed)
- Do nudge buttons exist when nudge is a card?
- Is a forecast allowed on the combat screen (it conflicts with a locked "no forecast tags")?
- Is Adjuster HP the "enemy HP" slot, and is the Adjuster a docked satellite on the wave wheel?
- Is slice HP a stat on the read block, a badge, or HP pips?

## Slips / gaps (honest)
- Two accidental empty `python -` invocations (stdin, no code) hung; stopped with TaskStop, nothing executed, nothing written. Three `python -c` one-liners were used for image crops and a dependency check.
- Strict plates omit the Adjuster drone on the wave rim and the deck/discard pile counts; no Blender render (the bible has no 3D objects on the wheels; the only 3D is the reused backdrop), so the "real 3D for physical things" bar applies only to the backdrop.
- Unit glyph 16 px twin check not run; fonts checked by eye (all text on strict plates >= 16 px except the bible-size rail and a few HP badges at 17 px).
- Dashed ghost cells overlap live cells on p2 by design (3.21 rule 2) and read as clutter; not tuned further.
- Nothing outside BB_bible and plates/bible was written. I read (never wrote) D4_E4 sim, I_waves/state.json, waves_e4 plates.
