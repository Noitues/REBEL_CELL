# C — STRENGTH DUEL, round 2 (current; replaces the SPEC.md rules)

## Rules (one function, `duel()` in `tools/raid_concepts/concept_c2_duel.py`)
- **Paths.** Each threat declares a target and a path. Every node it passes takes one strike (a small banner). Its target
  takes 3 strikes (a big banner).
- **The duel.**
  - ATK = strikes × damage.
  - DEF = integrity + bonus.
  - loss = max(0, ATK − bonus).

  | Loss | Result |
  |---|---|
  | 0 | HOLDS |
  | below integrity | SCUFFED |
  | at least integrity | DOWN |
  | at least 2 × integrity | TAKEN |

  Home loses the loss from its integrity; 0 = BREACHED.
- **The pieces:**
  - **Firewall gun** +3.
  - **Turret** +8 on its node.
  - **Crew** +3 on its node **and every neighbour**, so adjacency matters.
  - **ICE** cancels the biggest single strike at its node.
  - **Decoy** re-targets the Collector onto the Decoy node.

## Presentation
- **Each banner** shows:
  - the attacker silhouettes × strikes;
  - ATK in cobalt;
  - the bonus icons;
  - DEF in yellow;
  - a two-colour margin bar;
  - a verdict icon in the corner: check, bolt or flag.
- **The duel card** (planning) itemises every line and the delta of the piece being dragged.
- **The forecast** gives the clean payout and the **tightest margin** (which node, and by how much).
- **The duels play** biggest first and home last, 3 beats each.

## The shown example (computed)
- **Bare:** Proxy is TAKEN (30 vs 15) and home takes −15.
- **The turret alone** makes Proxy DOWN (30 : 23).
- **Turret + ICE on Proxy** makes it SCUFFED (21 : 23).
- **The full plan** (turret + ICE on Proxy, crew on the Safehouse, Decoy on the Firewall) is a **clean defense**, with
  Proxy at margin 5.

## Rule changes (each a designer decision)
1. Strikes along declared paths replace step travel.
2. Flat bonuses, with the crew aura.
3. ICE cancels a strike.
4. The playout is locked to duels instead of steps.
