# C — STRENGTH DUEL (Civilization-style siege per node)

**One line.** Each threat **declares a target node** when the raid is announced. Travel is abstracted away. Each target node
carries a siege banner: attacker strength against defense strength, a margin bar, and a verdict word. Defenses are moved
into banners, and every modifier is itemised.

## The decision
- **Triage across banners.**
  - Defense pieces add to a banner's DEF: turret +8 (two shots), ICE Lock "cancel one strike", Decoy "move a banner's attacker
    to the Decoy's node", operative +3 per adjacent node.
  - The Armory cannot cover every banner, so choose which nodes hold, which go DOWN and which are TAKEN.
  - Adjacency gives synergy: a Firewall next to a target lends its built-in +3.
- **Margins matter.**
  - DEF ≥ ATK → HOLDS.
  - ATK > DEF → DOWN.
  - ATK ≥ 2 × DEF (or a DOWN node hit again) → TAKEN.
  - Home: ATK − DEF comes off its integrity; 0 = BREACHED.

## The information shown
- **Siege banners** on each targeted node:
  - attacker silhouette and ATK (cobalt);
  - node icon and DEF (yellow);
  - a two-colour margin bar;
  - the verdict word, coloured by state.
- **The selected banner expands into a duel card** (Civ VI / VII combat preview):
  - big ATK vs DEF;
  - itemised lines (9 × 3 strikes = 27; node integrity 15; turret +8; crew +0);
  - the delta while dragging (TAKEN > DOWN).
- **The result panel**:
  - CLEAN DEFENSE / CELL HOLDS / BREACHED;
  - "3 / 3 hold";
  - the payout (+5 Heat, +12 Schematics);
  - the **tightest margin** ("Proxy margin 1").

## Resolution
- **The duels play one at a time**, in a fixed order: home last, for tension. Each plays centre-stage over its node.
  - Attack fills against defense, strike by strike (3 beats per duel).
  - The verdict word lands on the node.
- **About 6–8 s per duel**; 3 duels last about 25 s. No input.

## Consequences
As in the other concepts: a stamp with the cost or payout, persistent DOWN and TAKEN marks, and a list of worn and spent
defenses. Here the HOLDS ticks also stay on the map until the next raid, as a record.

## Rule changes (each is a designer decision)
1. **Routes stop mattering mid-raid.**
   - Threats choose a target at announcement, using today's routing rules, and strike it.
   - There is no travel and no damage in passing.
   - Entry points still decide which nodes are reachable.

   **Designer decision.**
2. **Outcomes come from strength totals and thresholds** (ATK vs DEF, the 2× TAKEN rule), not from step-by-step HP.
   **Designer decision.**
3. **Asset effects become flat DEF modifiers**, which replace reach and targeting priority. **Designer decision.**
4. **D26's step-locked playout becomes "duel-locked"**: three beats per duel. **Designer decision.**

## Key frames
`r1/mockups/`, `r1/scrambled/`.
