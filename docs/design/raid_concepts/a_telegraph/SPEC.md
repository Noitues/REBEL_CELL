# A — TELEGRAPH (exact whole-raid intents)

**One line.** Into the Breach's telegraph, stretched over the whole raid. Every threat's move and strike for every step is
drawn on the network before you commit. A step scrubber lets you look at any step, and every node wears its end-of-raid result.

## The decision
- You place up to the Armory's assets on nodes: a turret, an ICE Lock or a Decoy. You can also move the stationed operative.
- Each placement rewrites the telegraph at once: arrows reroute, strikes vanish, damage numbers change.
- The puzzle is ordering and coverage. A turret on the node where two routes meet thins both threats. An ICE Lock on the
  first heavy hit buys two steps for the turret to work. A Decoy bends a route off a fragile node onto a sturdy one.
- There is no budget beyond the Armory itself; the Armory is the budget.

## The information shown
- **On the board, for the scrubbed step:**
  - cobalt arrows for each threat's move;
  - a red pencil ring on each struck node, with an order badge (1, 2, 3) and a damage badge (−5);
  - the node's integrity pips, with the projected loss striped red.
- **Scrubber (top).** Six step cells. Each cell holds the tiny silhouettes of the threats that strike in that step, so you can
  see the raid's shape at a glance (a heavy front, then the Enforcer alone).
- **Attack order panel.** For the scrubbed step: numbered rows of silhouette → target node icon → damage. A held threat shows
  an ICE icon instead of damage.
- **Always on.** Every node carries a HOLDS / DOWN / TAKEN tag for the **end of the raid**. A forecast strip names the
  changed nodes (Relay 15 > 10, Vault 20 > 17, Proxy DOWN) and the verdict (CELL HOLDS · not clean: +0 Heat).
- **What-if.** While you drag a card, a yellow tag at the target states the delta (PROXY −9 → −0).

## Resolution
- **Commit** with START RAID. The board does not move; the camera is fixed.
- **Steps play in order.** Inside a step, strikes resolve in their badge order, so the board plays back exactly what the scrubber showed.
- **Effects are drawn on the units:**
  - shots are yellow tracer lines;
  - damage appears as floaters on the hit unit;
  - threat HP pips drain;
  - a killed threat cracks and greys out.
- **No text log and no input.** Only 1x / 2x / 4x and skip are available.
- **Timing (D26).** About 4 s per step, so 6 steps last about 25 s at 1x.

## Consequences
- **The verdict stamp** is large and centred over the map's empty side:
  - CELL HOLDS, with a cost line (HOME 50 > 45 · 1 DOWN);
  - CLEAN DEFENSE in teal, with +5 Heat and +12 Schematics;
  - BREACHED, as a full-screen red takeover with no CONTINUE, only "CAMPAIGN LOST → summary".
- **A "cost of this raid" card** lists each repair price, each spent asset and the clean bonus you missed.
- **Map marks persist** on the HQ map until repaired or reclaimed: the DOWN bolt, and the TAKEN flag with its pencil X. A
  TAKEN node also gets a dashed cobalt "new entry" arrow.

## Rule changes
None to the resolver's maths. It is the current step model with an exact telegraph.

One presentation rule needs a new spec: inside a step, the order in which strikes resolve must be fixed and shown.
Today it is fixed but hidden. **Designer decision: no** (it is already deterministic).

## Key frames
`r1/mockups/1_warning.png` … `5_aftermath.png`, scrambled under `r1/scrambled/`.
