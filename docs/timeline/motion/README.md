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
| `resolve_sequence` | a whole SEND IT: discard, latch, block number, hit line, HP drain, spins, deal-in, LAST TURN | 1.45 s budget, beat gap 0.18 s (squeezed to fit) | the most readable that still fits "under ~1.5 s"; 1.8 s dragged, 1.2 s crowded the beats |
| `number_float` | damage, crit (1.5x + burst) and block numbers in the enemy's hub | 0.6 s, 28 px rise (capped to the hub), CUBIC out | readable for a whole beat without stacking; the heavy one overlapped the next beat |
| `card_play` | a card flies to its zone, stamps and dissolves into the effect; the hand keeps its gap | fly 0.22 s, stamp 0.1 s (x1.2 down to 1) | "zine, tactile, 0.2-0.35 s": the effect starts 0.32 s after the click |
| `drag_ghost_follow` | the drag ghost trailing a fast cursor with tilt, zones pulsing | time constant 0.08 s, alpha 0.6, tilt up to 8° | "carried" without feeling late; 0.16 s trailed too far behind a flick |
| `drag_cancel_return` | a cancelled drag gliding back to its slot | 0.15 s, CUBIC out | a cancel should feel instant; 0.3 s read as a second action |
| `enemy_break` | the enemy wheel cracking along slice borders and falling, then its dim ghost | 0.75 s, 160 px fall, QUAD in | the kill is the climax of the fight; the netrun waits for it |

## Map, raid, jack and Heat (ANIM-5)

| Strip | Slice | Motion | Variants (top to bottom) | Picked | Captured with |
|---|---|---|---|---|---|
| `influence_spread.png` | ANIM-5 | Territory tint spreads from a newly claimed Site (HQ backdrop) | `influence_spread` 0.7 / 1.0 / 1.4 s | 1.0 s (the front reads, done inside a second) | hq `--demo-hq --demo-anim=influence_spread` |
| `raid_playout.png` | ANIM-5 | Threat travels the street route, turret trace, hit, damage number, HOLDS stamp | `raid_move` 0.35 / 0.5 / 0.7 s | 0.5 s | hq `--demo-raid --demo-anim=raid_playout` |
| `heat_pulse.png` | ANIM-5 | Heat crosses 25: distortion pulse, corporate wireframe creeps in from the edges, letters shake, band stamps | `heat_pulse` peak 0.85 / 0.5 / 0.3 | 0.5 (the UI keeps its shapes) | hq `--demo-hq --demo-anim=heat_pulse` |
| `jack_in.png` | ANIM-5 | Push into the JACK IN / deck CRT, dissolve to the wireframe city, scanlines roll, the net arrives | `jack_in` 0.6 / 0.8 / 0.9 s | 0.8 s (heavy, mid-range) | hq `--demo-grid --demo-anim=jack_in` |
| `route_pulse.png` | ANIM-5 | Netrun move: light pulse carries the marker along the link, new node pops, old one dims | `route_pulse` 0.3 / 0.4 / 0.6 s | 0.4 s | netrun `--demo-run --demo-anim=route_pulse` |
| `site_select.png` | ANIM-5 | Grid Site selected: roof outline draws on, ring eases in, camera leans and eases | `site_outline_draw` 0.25 / 0.4 / 0.6 s | 0.4 s | hq `--demo-grid --demo-anim=site_select` |
| `asset_drop.png` | ANIM-5 | Raid asset deployed: drops onto its node with a stamp ring (the map holds still) | one (`asset_drop` 0.25 s BOUNCE 24 px) | as is | hq `--demo-raid --demo-anim=asset_drop` |

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
| `loot_pick` | the picked card lifts and flies to CARDS as the route comes in (`--demo-loot --demo-pick`) | lift 12 px, 0.35 s CUBIC in-out | the lift says "taken"; 30 px / 0.5 s lingered over the next screen |
| `dispatch_type` | a DISPATCH subtitle typing in (lab) | 0.025 s a character (40 cps), bar in 0.2 s 40 px | ahead of reading speed so it never holds the reader; 0.045 s dragged on long lines |
| `drip_grow` | SEND IT's drips growing on first appearance, then holding (lab) | 0.6 s QUAD out | slow enough to notice, once; ELASTIC wobbled |
| `sticky_bump` | top bar: Cycles 85 → 140 counts up, CARDS 10 → 11 bumps and rolls (lab) | x1.08 0.12 s BACK; roll 0.3 s; count up 0.6 s | a nudge, not a shout; x1.15 over 0.2 s shouted on every purchase |
| `hq_idle` | the HQ on arrival: radio types in, the deck monitor hums, JACK IN breathes (`--demo-hq`, 0-2.8 s) | radio 0.03 s/char; hum 2 s band 0.06; breathe 1.04 over 2.4 s | alive but quiet; the strong hum (0.14) read as a fault |
| `city_traffic` | the city's live layer: dashes on the busiest streets only (lab city) | traffic ≥ 0.55, 2.8 s a lot, short bright dashes; 1 in 3 HQ signs flicker | "very sparse" per the handoff; frame time unchanged (DECISIONS ANIM-6) |
