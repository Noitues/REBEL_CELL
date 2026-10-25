# D — AUTO-BATTLER LOADOUT (lineup match per lane)

**One line.** The raid is a lineup match, in the manner of Super Auto Pets, Backpack Battles, The Bazaar and TFT.
- Solace reveals its lineup: unit cards, each pointing at the node it will attack.
- You slot defenses into each targeted node's slots.
- Defenses are units with triggers and adjacency synergies.
- A deterministic tick strip per lane shows every hit before you commit.
- Then the lanes fight side by side, with no input.

## The decision
- **Slotting.** Each node card has slots: the Firewall 3, the Home 2, other nodes 2. Armory pieces and the operative go into slots.
- **Synergies between neighbouring slots** (a teal link and a chip show each one):
  - an operative next to an ICE Lock makes it hold +1 tick;
  - an operative next to a turret makes it hit +2;
  - a Decoy next to anything draws the first hit.
- **Re-slotting is free until commit.** The fun is in finding the combo that flips a lane. A unit can also be moved across lanes
  if its node is adjacent to that lane's node.

## The information shown
- **Unit cards for threats.** Each card shows the silhouette, with an HP disc (cobalt, bottom left), a damage disc (red,
  bottom right) and speed chevrons. This is the auto-battler convention: two numbers and no words.
- **Node cards for the Cell.** The node icon and its integrity pips, with slot frames (empty frames show "+").
- **Sim strip per lane** (The Bazaar-style tick bar, six ticks):
  - yellow diamonds are our hits, cobalt diamonds are theirs;
  - a chip at the end gives the lane result (HOLDS / DOWN / TAKEN).

  The strip is the exact sim, not an estimate.
- **What-if.** While you drag, the lane's strip shows the new result, and a tag states the flip ("with ice: DOWN > HOLDS").
- **Sim result panel.** CLEAN DEFENSE / CELL HOLDS / BREACHED, with its payout.
- **The real map**, as an inset, so the player keeps their bearings.

## Resolution
- **The lanes fight at once.** A playhead runs along the tick strips.
- **Hits flash on the cards.** Tracers run from slot to unit, and floaters appear on the node card.
- **A killed unit card flips face-down.**
- **Timing.** About 4 s per tick, about 25 s in all. No input.

## Consequences
- **Stamp** with its payout or cost line.
- **"Lineup after" card** with each unit's wear: turret 10 > 6, ICE spent, operative XP +1, Decoy 12 > 12.
- **The HQ map** takes the DOWN and TAKEN marks, the same as in the other concepts.
- **Lane results are remembered.** A lane that went DOWN starts the next raid with a cracked slot (−1 slot) until repaired.

## Rule changes (each is a designer decision)
1. **Lane model.**
   - Each threat fights only its target node's lane; routes collapse into "who attacks whom".
   - Threats on the way do no damage in passing.

   **Designer decision.**
2. **Node slots** replace "assets on claimed nodes": a fixed slot count per node type. **Designer decision.**
3. **Adjacency synergies between slotted pieces** are a new mechanic. **Designer decision.**
4. **The cracked-slot persistence** is new. **Designer decision.**
5. **D26 is kept** (the playout is tick-locked).

## Key frames
`r1/mockups/`, `r1/scrambled/`.
