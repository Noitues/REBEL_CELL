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
