# D — AUTO-BATTLER LOADOUT, round 2 (current)

## What changed in round 2
- **On the real city map.**
  - The Solace lineup chips (two numbers, speed and route glyph) sit at their sites, with arrows to their targets.
  - Each target node has 2 slots on the map.
  - **Map adjacency is synergy.** A Breaker in a slot boosts the turret (+2 a tick) and the ICE (+1 tick) of its own node
    and of map-adjacent nodes. Teal links show each boost.
- **Lane sim** (`tools/raid_concepts/d2_lane_sim.py`, one rule). Each threat fights the lane of its target node.
  Per tick, 6 ticks:
  1. A frozen threat skips its tick.
  2. Our pieces fire. A turret hits 4 (+2 if boosted). A Breaker in a slot fights for 3.
  3. The threat strikes. A Decoy soaks hits while it has integrity left (12); otherwise the node takes the hit.

  At the end:
  - a threat still alive TAKES its node (home only loses integrity; 0 = BREACHED);
  - a node at 0 is DOWN.
- **Strips.**
  - Every diamond carries its number: yellow for our hits, cobalt for theirs, teal when frozen, grey when soaked; a red X
    marks the kill.
  - The lane result is an icon. Home shows −N.
- **Two plans compared:**
  - plan 1: turret + ICE on Proxy, Breaker on Vault, Decoy on home → home −15, nothing lost;
  - plan 2: turret + ICE on home, Decoy + Breaker on Vault → home 0, Proxy TAKEN.
- **The playout is on the map.** Units fire from their slots, and a playhead runs along the strips.
- **The aftermath is on the map**, with unit wear listed.

## Rule changes (each a designer decision)
1. The lane model: no damage in passing.
2. Slots per node.
3. Adjacency synergies.
4. A Breaker in a slot fights.
