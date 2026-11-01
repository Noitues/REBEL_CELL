# Hover plates, one per card effect type (Shifting Waves)

All plates are 1920x1080 on `combat_backdrop/v3_1/room_bio_bare.png`. `hover_overview.png` is the contact sheet. `hover_key.png` is the grammar key. Nowords variants: brace, spin3, trigger, twist.

Generator: `D:/rc_scratch/combat_redesign/hover/src`, a copy of the E10 final src. A copy of the new files is in `src/` here. `combat_e10_design/` and the sim were not edited.

## How the plates are made
- **Real sim, read only.** `hover_sim.py` imports the E10 sim and applies each card's real action to the approved turn-2 state (seed 49). The bill, the landing arcs, the guns and the HP numbers on every plate are the sim's plan values, not hand-drawn.
- **No showcase state edits were needed.** Every card has a legal target in the approved state. Only the hand display is swapped, because the state's hand is Brace, Spin3, Trigger, Twist. Plates for Spin2, Nudge, Strike, Shove, Pull, Hold and Firewall say so in their review slip. The Shove bump plate uses the real collision rule.
- **Stand-in board.** The board is the E10 generator, patched in the copy (`plan_patch.py`) toward VISUAL_PLAN: no dashes, neutral lane outlines with hot, cold and dotted time grammar, slate enemy units, cross-hatched HP lost at END TURN (red for the enemy, pink for ours), pink gun tracers. The tower, cards, wave arcs and HUD are still E10 art. They wait for the chosen player-style finalist.

## Hover grammar (adapted from r3 option B focus ghost)
- **Lit and dim.** What the card touches stays at full value. Everything else drops to value x 0.50 and chroma x 0.45. This is a whole-screen spotlight, not only dimmed units. The other cards in the hand drop to 70 percent.
- **Lifted card.** Grown 1.12x, with a hand-cut pink offset print behind it (P family: hard-edged, no glow).
- **Focus.** Thin lime corner brackets mark legal targets. Thick brackets mark the aimed target.
- **Ghost.** The thing at its new place, at 74 percent, with a grease-pencil yellow outline meaning "proposal". The origin is veiled with ink at 60 percent.
- **Motion.** L5 arrowed outline. The edge colour is the owner: pink for the tower, orange for rings and schedule, yellow pencil for a unit path.
- **Outcome.** Pink cross-hatch means lost at this END TURN and ours. Red hatch means the enemy takes it from you. The pink starburst is a hit landing.
- **Plan numbers.** The bill switches to plan values. A pencil underline marks LANDS or THROUGH when they change. A pencil ring marks the RAM coin spent. A pencil square marks the TRACE gained.
- **Note slip.** A paper review slip sits in the free room zone. It is plate chrome, not game UI, and is omitted from the nowords variants.

## Per card
| Plate | Highlighted (lit) | Dimmed | Ghost rule |
|---|---|---|---|
| `hover_brace` (h02) | All 6 slices, landing arcs, bill, RAM | Rings, queue, header, objectives | Thin lime brackets on the 5 other slices. On the aimed slice (sector 2, TURRET): a painted pink plate over the outer 40 percent, with an L10 double edge (pink and paper), rivets and a pencil outline. A pencil mark sits on the landing arc that now stops. THROUGH 6 to 4. |
| `hover_spin3` (h01) | Tower, ring NOW, gun target cells, arcs, bill, RAM | Rings +1 and +2, queue | The tower is drawn at the plan angle. A pencil rim on the tower marks the proposal. A pink L5 arc around the hub covers 3 sectors (180 deg). Tracers and arcs are at plan values. |
| `hover_spin2`, `hover_nudge` (h01) | Same | Same | The same plate with a 2-sector or 1-sector arc. The hand is swapped. |
| `hover_trigger` (h03) | Legal units (rings +1 and +2), the victim cell, slices 3 and 4, bill, RAM and TRACE | Everything else | The aimed Payload has thick brackets. Two pencil L5 paths run down sectors 3 and 4. The victim Packet is pink cross-hatched, with a pink burst at the kill. A refund coin sits in the cell. Pencil marks show the RAM and TRACE changes. |
| `hover_trigger_f2` | Same | Same | After Twist is played (best line f2). The hand shows the played liner and the refund is live (RAM returns). |
| `hover_twist` (h04) | Rings +1 and +2, the bezel and schedule, arcs, bill | Ring NOW, tower | An orange L5 sweep of one sector in the free ring +1 cell. The E10 twist pill sits on the ring tag. The two affected landing arcs are redrawn at their new sectors with a pencil underline. |
| `hover_strike` (h05) | Every unit in range, the Adjuster, arcs, bill | Tower, schedule | The aimed Packet (2 HP) is pink-hatched and gets a pink burst with speed lines. Its landing arc is removed. |
| `hover_shove`, `hover_shove_bump` (h06) | Rings NOW and +1, the Adjuster, arcs, bill | Ring +2, schedule | Clean slide: the ghost is at the new cell, an orange L5 arrow runs between the tokens, the origin is veiled and the arc is redrawn. Bump: an orange arrow, a pink burst at the shared edge and one pink-hatched HP tick on each unit. |
| `hover_pull` (h07) | The only legal unit, its destination, its two arcs | Everything else | Only one unit has a free inner cell, so only it gets brackets. The ghost is on ring +1, an orange inward L5 arrow, and the arc moves a turn nearer. |
| `hover_hold` (h08) | Bezel, all rings, arcs, bill | Tower interior, header | The schedule goes 2,0,0 to 0,2,0 (live HOLD cell). An orange L5 arrow outside the bezel shows the step sliding one slot. A pencil outline sits on the live cell. Arcs are recomputed. |
| `hover_firewall` (h09) | The aimed column (sector 0) across 3 rings, the 2 units that step in (Payload, 9-wide Packet), bill | Tower, other columns | A pink burn band: wash, 4 painted flame strokes and a pencil outline. Thin lime brackets on the other legal columns. Bursts on the 2 units. The Packet loses 1 pink-hatched HP. The Payload loses 0 (armour). |

## Open points and caveats
- Hover plates for the soak toggle and unit hover (h10, h11) were not asked for and are not made.
- The Firewall rule (burn the next 2 units that enter the column) is read from the sim code.
- The player style is not chosen yet. All P marks (clamp plate, offset print, tracers) use the pink painted-stroke helper so they can be re-skinned in the finalist style.
- The E10 future-wave arcs, orange W-tags and the card art are unchanged and are dimmed on every plate.
- Process slip: `python -` with an empty heredoc was run by mistake three times. Each of those stdin Python processes was stopped. The last one (PID 13080) was stopped with taskkill. No other PIDs were touched.
