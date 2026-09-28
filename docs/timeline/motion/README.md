# Motion frame strips (Animation pass)

Each PNG stacks 2-3 variants of one animation, captured with the motion lab
(`godot --path . --resolution 1280x720 --write-movie <dir>/f.png --fixed-fps 30
--quit-after N res://tools/design_lab/motion_lab.tscn -- --demo-anim=<id>
--demo-set=<id>.<field>=<value>,...`) and montaged with `tools/design_lab/frame_strip.py`.
Each frame is labelled with its ms from the start of the motion; the variant's values are
in its title, and the chosen one says CHOSEN. The chosen values are in
`content/config/ui_motion.tres`; the reasons are in `docs/DECISIONS.md` ("Animation pass").

## Combat (ANIM-2 / ANIM-3)

| id | what it shows | values chosen | why |
|---|---|---|---|
| `wheel_spin` | a card spin of 9 ticks on the operative's wheel: ease-out, overshoot, settle, slice blur | 0.35 s, CUBIC out, overshoot 0.2 tick | "mechanical, snappy": lands fast and exactly; heavy felt slow, bouncy's BACK overshoot grows with distance |
| `wheel_respin` | a 70-tick respin (the turn-start spin to the next landing; `enemy_turn_spin` is the same 0.15 s later) | 0.4 s, CUBIC out, overshoot 0.2 tick | keeps the SEND IT sequence under 1.5 s; bouncy showed a wrong slice mid-settle |
| `wheel_nudge` | three queued one-tick nudges with the recoil | 0.08 s per step, 2 px recoil | "crisp, under 0.12 s"; the queue catches up instead of lagging |
| `resolve_sequence` | ANIM-R4 recapture (lab `--demo-anim=resolve_side_gap`, the `send_both` fight; row 2 `--demo-anim=impact_mark`, the `send_block` fight): your hits land in full and their rolls end, a gap, then the enemy's (its drone staggered after); a hit leaves from the slice under its needle, its number shows when it arrives; a guarded hit shows sword 8 - shield 8 = 0 where it struck, the icon row under the HP says the same; the forecast is ticked and fades | `hit_line` 0.45 s (flight 60 %: 0.27 s), `resolve_side_gap` 0.35 s, `resolve_attacker_gap` 0.15 s; `impact_mark` 0.6 s | rows 1-2 CHOSEN; row 3 (`resolve_side_gap` 0.10 s): the enemy's shot left while your number still rolled |
| `number_float` | ANIM-R4 recapture (`--demo-anim=number_float`, now a real SEND IT, so the tag says what happens: the ANIM-R3 demo's made-up hits flew under a "MISS" tag): the enemy's raw 8 rides its projectile, meets your guard where it strikes (sword 8 - shield 2 = 6), then -6 pops fresh in your hub and travels into the HP; then its drone's 3 | `hit_absorb` 0.3 s (the equation reads before the number pops); `number_to_hp` hold 0.22 s, travel 0.22 s | top CHOSEN; at 0.15 s the equation was gone before it read |
| `card_play` | ANIM-R4 recapture: the card flies, stamps and dissolves, then its spin plays; the forecast tags stay hidden until the spin lands (no spoiler of where it lands) | fly 0.22 s, stamp 0.1 s, dissolve 0.3 s | top CHOSEN; at 0.35 s the flight dragged |
| `drag_ghost_follow` | ANIM-R2 recapture: the drag ghost trailing a fast cursor with tilt, zones pulsing | time constant 0.08 s, alpha 0.92 (was 0.6), tilt up to 8° | top CHOSEN; at 0.6 the carried card's words were too washed out to read |
| `drag_cancel_return` | a cancelled drag gliding back to its slot | 0.15 s, CUBIC out | a cancel should feel instant; 0.3 s read as a second action |
| `enemy_break` | ANIM-R4 recapture (`--demo-anim=enemy_break`): the real wheel cracks for `break_crack` of the break, then falls; VICTORY stands above the beaten disc (never over the crack); DEFEATED and the skull in the enemy's own colour | 0.75 s, 160 px fall, `break_crack` 0.22 | top CHOSEN; at 0.4 the pieces hung too long |

## Map, raid, jack and Heat (ANIM-5; captured again in ANIM-R1, R2 and R3)

Recaptured after the ANIM-R3 fixes (DECISIONS "Animation pass — ANIM-R3 city, raid, jack,
heat and route"): two variants each, the picked one on top titled CHOSEN, quantized to 128
colours, frames every 3-48 frames at 30 fps (the ms label says when). `site_select` is from
ANIM-R1.

| Strip | Slice | Motion | Variants (top to bottom) | Picked | Captured with |
|---|---|---|---|---|---|
| `influence_spread.png` | ANIM-5 / R1-R3 | Territory tint spreads from a newly claimed Site in the Cell's acid (`cell_turf`); the district keeps a 0.45 tint and a hatch; CLAIMED stamps over its Site, above the labels | `influence_tint` 0.45 / 0.3 | 0.45 (0.3 was nearly invisible over the lit city) | hq `--demo-grid --demo-anim=influence_spread` |
| `raid_playout.png` | ANIM-5 / R1-R3 | Framed steps, threat tokens with a trail, shot / hit / number (a node's number on its right, a threat's on its left), each node stamping its resolved outcome, home's verdict as its banner placed clear, the feed in sentences with names | `raid_outcome_stagger` 0.3 / 0.5 s | 0.3 s (0.5 s dragged the end out) | hq `--demo-raid --demo-anim=raid_playout` |
| `heat_pulse.png` | ANIM-5 / R1-R3 | Heat crosses 25: the number rolls to 25, the amber HEAT 25 - NOTICED banner with its eye and the band's consequence stamps over the WANTED header (never the number) and fades; the poster distorts briefly | `heat_banner` stamp x1.5 / x1.0 | x1.5 (x1.0 did not read as a stamp) | hq `--demo-hq --demo-anim=heat_pulse` |
| `jack_in.png` | ANIM-5 / R1-R3 | Push into JACK IN (no first-frame hitch: the run is built under the cover, the shaders warmed), a calm dissolve wave from the CRT, CONNECTING TO <SITE>, the arriving route lifts with it | `jack_dissolve` spread 0.9 feather 0.08 / spread 0.6 hard cells (ANIM-R2) | 0.9 / 0.08 (the hard scattered cells read as corruption) | hq `--demo-grid --demo-anim=jack_in` |
| `route_pulse.png` | ANIM-5 / R1-R3 | Netrun move on a route framed with a margin (you-are-here at the street before the first node), twins only for the same whole road, "then:" icons for what only one choice reaches, a thick acid trail, the target pulses and pops | `route_pulse` 0.4 / 0.6 s | 0.4 s | netrun `--demo-run --demo-anim=route_pulse` |
| `site_select.png` | ANIM-5 / R1 | Grid Site selected: roof outline draws on, ring eases in and breathes (`select_ring_pulse`), camera leans and eases | `site_outline_draw` 0.25 / 0.4 / 0.6 s | 0.4 s | hq `--demo-grid --demo-anim=site_select` |
| `asset_drop.png` | ANIM-5 / R1-R3 | Raid asset deployed: waits for the camera, falls 56 px from x2.2 its size, stamps a thick ring with a flash, keeps its name, and the forecast numbers it changed rise off their nodes ("25 > 30") | `asset_drop_grow` x2.2 / x1.0 | x2.2 (at its own size the landing was nearly invisible) | hq `--demo-raid --demo-anim=asset_drop` |

Variants: add `--demo-tune=<id>:<duration>[:<amplitude>]` (a duplicate of the table; the
file never changes). Command: `godot --path . --resolution 1280x720 --write-movie
<dir>/f.png --fixed-fps 30 --quit-after N <scene> -- <flags>`; the log prints "anim5: <id>
starts on frame N" for `tools/design_lab/frame_strip.py --start`.

## Drag and drop, HQ side (ANIM-4)

Each strip follows one item from the pick-up (0 ms: it pops and its slot dims; the
targets that take it pulse, the others stay dark) along a scripted pointer (the item
trails it with ANIM-3's ghost lag) to the let-go at about +700 ms, a little off the
target's centre so the snap shows.

| Strip | Motion | Variants (top to bottom) | Picked | Captured with |
|---|---|---|---|---|
| `drag_loadout.png` | Rank 3 ring swap: a swap chip carried onto an inner ring segment of the loadout view's wheel; it snaps in, dips and stamps, the ring shows the new segment | `drop_settle` 0.10 s / 4 px, **0.15 s / 6 px**, 0.25 s / 10 px | 0.15 s / 6 px: tactile without a bounce that reads as a second action | hq `--demo-hq --demo-anim=drag_loadout` |
| `drag_crew.png` | An operative's chip carried from the Site card onto JACK IN (who runs it): reticle, snap, stamp ring (the jack itself is ANIM-5's, switched off for the capture) | `drop_stamp` 0.18 s / +12 px, **0.25 s / +18 px**, 0.35 s / +26 px | 0.25 s / +18 px: reads as a stamp, gone before the jack | hq `--demo-grid --demo-anim=drag_crew` |
| `drag_asset.png` | A DECOY card carried from the Armory onto CORE on the map; the node's own asset drop (ANIM-5 `asset_drop`) is the landing | `drag_pickup` x1.00, **0.10 s x1.06**, 0.16 s x1.14 | x1.06: the card visibly lifts; x1.14 jumps out of its row | hq `--demo-raid --demo-anim=drag_asset` |
| `drag_refuse.png` | The same card onto a node with no free slot: the no-entry mark shakes on the node, the card glides home, the rules' reason shows | `drop_reject` 0.12 s / 3 px, **0.20 s / 6 px**, 0.35 s / 10 px | 0.20 s / 6 px: a clear "no" that doesn't hold the item up | hq `--demo-raid --demo-anim=drag_asset_refuse` |
| `drag_cancel.png` | Top: a crew chip let go over nothing glides home (`drag_cancel_return`, ANIM-3's 0.15 s). Bottom: a dossier carried to the mini-map's firewall relay (no station slot) is refused and glides home | one each (chosen values) | as is | hq `--demo-grid --demo-anim=drag_crew_cancel` and `--demo-anim=drag_crew_refuse` |

The log prints "anim4: <id> starts on frame N" (the pick-up) and "lets go on frame N";
the strips take 8 frames every 5 from the pick-up. `--demo-anim=drag_loadout_cancel` (a
swap let go beside the wheel) plays too.

## Drag and drop in the run (ANIM-4b)

Same scripted pointer as ANIM-4 (pick-up at 0 ms, let go at about +700 ms a little off the
target's centre); 10 frames every 4 from the pick-up. Strips are quantized (128 colours).

| Strip | Motion | Variants (top to bottom) | Picked | Captured with |
|---|---|---|---|---|
| `drag_buy_card.png` | ANIM-R3 recapture: the Modem card carried onto CARDS at the combat ghost's 0.92 alpha (the ANIM-4b strip was taken at 0.6: washed out), shrinking in with SOLD; Cycles roll down, CARDS bumps | `drag_ghost_follow` alpha **0.92**, 0.8 | 0.92: the carried card reads; at 0.8 it faded into the page | netrun `--demo-shop --demo-anim=drag_buy_card` |
| `drag_buy_chip.png` | A microchip carried onto a slot of the small spinner beside the wallet (the capture has 300 Cycles) | `drop_buy` as above | 0.22 s / x0.45 | netrun `--demo-shop --demo-anim=drag_buy_chip` |
| `drag_buy_refuse.png` | The same card with 5 Cycles: CARDS refuses, the no-entry mark shakes on it, the card glides home, "Not enough Cycles" | `drop_reject` 0.12 s / 3 px, **0.20 s / 6 px**, 0.35 s / 10 px | 0.20 s / 6 px (ANIM-4's) | netrun `--demo-shop --demo-anim=drag_buy_refuse` |
| `drag_shred.png` | A deck card carried onto the REMOVE viewer's SHRED tile: it squashes into the mouth as paper strips run out; the viewer closes once it has played | `shred_feed` 0.2 s / 18 px, **0.3 s / 28 px**, 0.45 s / 40 px | 0.3 s / 28 px: reads as shredded; 0.2 s was a vanish, 0.45 s waited | netrun `--demo-shop --demo-anim=drag_shred` |
| `drag_loot.png` | A loot card carried onto CARDS; the route comes in under the landing | `drop_buy` as above | 0.22 s / x0.45 | netrun `--demo-loot --demo-anim=drag_loot` |

The log prints "anim4b: <id> starts on frame N" and "lets go on frame N"; variants use
`--demo-set=<id>.<field>=<value>,...`.

## Screens, menus and ambience (ANIM-6)

Lab strips use `--demo-anim=<id>` ("screen" demos); in-context strips run the scene with
its demo flag (`--demo-shop`, `--demo-buy`, `--demo-loot`, `--demo-pick`, `--demo-hq`) and
`--demo-set` (MotionDemo), starting on the frame noted in each label.

| id | what it shows | values chosen | why |
|---|---|---|---|
| `panel_in` | a terminal glass page slides in with the one-frame CRT roll (lab) | 0.22 s, 48 px, CUBIC out; roll 6 px for one frame | reads as a page change without delaying input; 0.14 s looked like a cut, 96 px dragged |
| `panel_drop` | a paper page drops in and settles on its tape (lab) | 0.22 s, 24 px, BACK out | the small overshoot is the tape pressing down; BOUNCE made paper jelly |
| `menu_highlight` | two focus moves on the main menu: highlight slide, the line typing in, the caret (lab) | slide 0.12 s QUAD out; type 0.02 s/char, at most 0.18 s a line; caret 0.5 s | terminal feel with no wait; 0.4 s a line felt like waiting on the menu |
| `modem_sign_warmup` | entering the Modem: page slides in, tubes flicker on, traces light, CYBER SHOP last (netrun `--demo-shop`) | warm-up 0.8 s; traces 0.6 s from 0.35 s | the flicker reads; 0.45 s missed it, 1.2 s left the sign dark while shopping |
| `buy_fly` | a purchase: SOLD stamps, the card flies to CARDS, Cycles roll down (`--demo-shop --demo-buy`) | SOLD x1.5 0.14 s BACK; fly 0.4 s CUBIC in-out to x0.35 | says where it went; 0.25 s was lost, 0.6 s full size covered the top bar |
| `loot_fan` | the loot stickers fan in from the foot of their row (`--demo-loot`) | 0.3 s CUBIC out, 0.06 s stagger, 8° a card | a deal, not a wait; 0.45 s / 14° sprawled out of the window |
| `loot_pick` | ANIM-R4 recapture at 1.0 and 1.6 (`--demo-loot --demo-pick [--demo-scale=1.6]`): the picked card flies to CARDS as a fresh copy (its slot empties), the cards not taken fall inside the loot window, and the route comes in only once they have (they floated over it) | lift 12 px, 0.35 s; `loot_reject` 0.45 s | rows 1-2 CHOSEN (one per text size); row 3 `loot_reject` 0.3 s read as a cut |
| `dispatch_type` | a DISPATCH subtitle typing in (lab) | 0.025 s a character (40 cps), bar in 0.2 s 40 px | ahead of reading speed so it never holds the reader; 0.045 s dragged on long lines |
| `drip_grow` | SEND IT's drips growing on first appearance, then holding (lab) | 0.6 s QUAD out | slow enough to notice, once; ELASTIC wobbled |
| `sticky_bump` | top bar: Cycles 85 → 140 counts up, CARDS 10 → 11 bumps and rolls (lab) | x1.08 0.12 s BACK; roll 0.3 s; count up 0.6 s | a nudge, not a shout; x1.15 over 0.2 s shouted on every purchase |
| `hq_idle` | the HQ on arrival: radio types in, the deck monitor hums, JACK IN breathes (`--demo-hq`, 0-2.8 s) | radio 0.03 s/char; hum 2 s band 0.06; breathe 1.04 over 2.4 s | alive but quiet; the strong hum (0.14) read as a fault |
| `city_traffic` | the city's live layer: dashes on the busiest streets only (lab city) | traffic ≥ 0.55, 2.8 s a lot, short bright dashes; 1 in 3 HQ signs flicker | "very sparse" per the handoff; frame time unchanged (DECISIONS ANIM-6) |
