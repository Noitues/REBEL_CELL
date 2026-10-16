# HQ others (Meridian, Solace, Orbital, Rebel Cell): status

- 12:55  Design phase done for all four (Eevee previews). GPU: queued 3rd (lock held by storyboard since 12:11; Halcyon
  waiting). One locked batch of Cycles TEST frames (1280 x 720) is queued: Meridian overview + decision (with the
  landmark lighting rig from the designer audit), the REDESIGNED Solace (twin twisting towers, a bow-tie bridge per
  floor, the ladder route) overview + decision, Orbital overview, Rebel Cell overview. When it runs they land in
  `hq_<corp>/scratch/test/` (`H_overview.png`, `H_overview_plate.png`, `H_overview_thumb.png` = the 320 px
  silhouette check) with the value checks (frame median / under 0.10 / over 0.85, landmark vs local background ratio)
  in `hq_<corp>/scratch/test_run.log`. Final renders wait for approval of those test frames.
- 14:10  Solace REDESIGNED per review (twin twisting towers of stacked floors, a bow-tie skybridge per floor, ladder
  route up/across; v1 archived in D:\rc_scratch\hq_solace\v1_helix). Orbital REVISED per review (front-and-centre
  orbiting camera, truss antenna tower with two elite vaults, rocket + RETARGET n/3 story, the override shortcut in
  red pencil, H_rocket, the launch storyboard H_launch_board + H_launch_strike as Eevee previews so far; the HQ
  explosion cutscene noted only). Meridian lit per audit. The combined Cycles TEST batch was re-queued with:
  Meridian overview + decision, Solace overview + decision, Orbital decision + rocket, Rebel Cell overview
  (-> hq_<corp>/scratch/test/, values in hq_<corp>/scratch/test_run.log). Still waiting for the GPU lock (storyboard).
- 14:30  Still queued. The storyboard re-acquires the lock after every batch and keeps GPU_WAITING_storyboard up, so by
  the protocol (an earlier-ordered waiting agent goes first) hq_others never gets a turn; Halcyon got one at 14:15.
  Coordinator: please tell the storyboard to leave a gap, or tell me to take the next free slot.
  Meanwhile Meridian / Solace decision cameras are now front and centre on the active room (the review's pattern).
- 15:10  TEST frames rendered (Cycles, 1280 x 720) in `hq_<corp>/scratch/test/`: Meridian overview + decision, Solace
  overview + decision (v2 boxes: superseded by the tube redesign below), Orbital decision + rocket, Rebel Cell overview.
  Values in `hq_<corp>/scratch/test_run.log`. Fixes since: Meridian's back fog bank was a second volume (346 s a test
  frame) -> folded into the main fog, fills toned down (its background read brighter than the castle: ratio 1.0 / 0.47);
  Solace was 6x its background -> dimmed; Rebel Cell too dark (median 0.045) -> plain windows up, the fist district
  counted as the landmark. Orbital decision / rocket landed at ratio 2.0 / 2.4 (median 0.25: floods trimmed).
  Solace v3 per the designer: two smooth swept TUBES (shared-vertex, smooth shaded), oval portholes in rows with frame
  rings, skinnier (tube r 9) and taller (19 floors x 12.5), bow-tie bridges per floor kept; Eevee preview in
  hq_solace/H_overview.png; its Cycles test overview is next in the queue.
- 15:45  Rebel Cell reworked per review: no tower (v1 archived), the fist in red windows with the SEQ shader (before /
  blackout / spreading / full) + PULSE; option A built (three stacked lanes in a section cut along a real street line
  of the block grid, lane buildings on the real lots, the earth + service tunnel); B/C skipped (C's scripts kept,
  unused). Test batch queued: Meridian overview+decision (cheaper fog), Solace v3 tubes overview+decision, Rebel A
  option frames (-> hq_rebel_cell/scratch/OPTION_SHOTS/) and the red sequence (-> hq_rebel_cell/scratch/RED_SHOTS/).
- 17:10  Test batch 2 done. Meridian (fog bank folded into the main fog): 32 s a test frame now, landmark / background
  1.28 overview, 0.89 decision (work lights + seams raised a notch for the finals). Solace v3 tubes: reads as a
  DNA pair, ratio 3.2 / 4.3 (window bands, bridge walls and ground spots lowered; the halo fills that made white blobs
  on the ground cut). Rebel Cell option A frames and the red sequence (before / blackout / spreading / full) in
  hq_rebel_cell/scratch/OPTION_SHOTS and RED_SHOTS: the fist reads clearly at full; earth made darker and deeper.
  Starting the final batches in task order (Meridian first) unless told otherwise.
- 17:30  MERIDIAN DONE: hq_meridian/ H_overview, H_decision, H_hover, H_mechanic_states, H_reveal.mp4/.gif, plates/, NOTES.md (first reveal frames being re-rendered in the next batch). Next batch queued: Solace finals + Orbital stills/sheet/launch board.
- 18:15  SOLACE DONE (v3 tubes): hq_solace/ H_overview, H_decision, H_hover, H_mechanic_states, H_reveal.mp4/.gif, plates, NOTES. ORBITAL stills done (H_overview, H_decision, H_hover, H_rocket, H_mechanic_states, H_launch_board, H_launch_strike); its reveal + all Rebel Cell finals in the running batch.
