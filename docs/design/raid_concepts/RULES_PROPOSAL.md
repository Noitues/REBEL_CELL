# Raid rules: changes and clarifications that lift the score ceiling

## Why this exists
Two fresh critics scored six concepts over two rounds. Even the best UI stalls at about 35/50. The second critic was
explicit: "the resolver is exact but not something the player can reason about". A perfect telegraph of an
unguessable rule set turns planning into "drag pieces until the numbers look good".

**Every item below is a designer decision.** Nothing here is implemented in `scripts/`.

## How it was measured
`tools/raid_concepts/sim.py` is a Python mirror of `scripts/core/raid_resolver.gd`. Each change is a toggle in its
`RULES`, measured with `tools/raid_concepts/rule_metrics.py`.

**Setup.**
- **Scenario:** the lab scenario, a Heat 50 Solace raid of three threats against six nodes.
- **Plans:** an Armory of **5** (Turret, ICE Lock, Decoy, Sentry, Railgun, with their stats from `content/assets/*.tres`),
  of which 3 are taken into the raid. Every placement on the 6 nodes is run, with the Breaker on any node: 12,960 plans
  per rule set.

**The metrics:**
- **clean %**: plans that end home untouched with no node DOWN or TAKEN.
- **retargets**: how often a threat changes target mid-raid; each change makes the warning telegraph wrong.
- **home surprises**: a threat that was going somewhere else ends up spent on the home server.
- **revisits**: a threat walks back through a node it already passed (zig-zag).
- **1-move changes %**: moving one piece one node changes some node's outcome tag. Below about 50 %, placements feel
  pointless (the round-1 "placement changes nothing" complaint). Near 100 %, the system is chaotic.

## Results

| Rule set | clean % | retargets / raid | home surprises / raid | revisits / raid | 1-move changes % |
|---|---|---|---|---|---|
| Today, with the 3-piece Armory (the R1/R2 scenario) | **0.00** | — | — | — | — |
| Today, with the 5-piece Armory (take 3) | 2.42 | 3.34 | 1.13 | 0.42 | 70.8 |
| + target lock | 2.42 | 2.42 | 1.21 | 0.60 | 65.2 |
| + target lock + home is not a corridor | 3.50 | 3.08 | 0.53 | 2.24 | 70.3 |
| + target lock + home not a corridor + weakest tie | 3.27 | 3.33 | 0.53 | 2.36 | 67.7 |
| **Fixed routes** | 2.42 | **0** | 0.23 | **0** | 63.1 |
| Fixed routes + home not a corridor + weakest tie | 3.27 | 0 | **0** | 0 | 62.0 |
| **Fixed routes + home not a corridor + weakest tie + ICE blocks the strike** | **4.83** | **0** | **0** | **0** | 57.6 |
| … + decoy radius | 2.55 | 0 | 0 | 0 | 56.5 |

**The winning package** is the bold row. With it:
- the warning telegraph is never wrong: 0 retargets, 0 revisits, 0 home surprises;
- a clean defense exists but is rare (about 1 plan in 20);
- a single move still changes an outcome more than half the time.

Target lock on its own does not help. Threats still re-pick whenever their target falls, which is why fixing the whole
route is the lever.

## Rule changes (in order of value)

### R1. Fixed routes: the telegraph IS the route
- **Today.** Every step, each threat re-picks its target (weakest node, highest value, or a Decoy) and its next hop.
  When a target falls, it re-picks: on average 3.3 times per raid, and each re-pick makes the warning telegraph wrong.
  Patching routing alone makes this worse. With "home is not a corridor" but no fixed routes, the bare raid's Enforcer
  zig-zags 12 hops (Proxy > Vault > Relay > Vault > Proxy > Safehouse …).
- **Proposed.**
  - When the raid starts, each threat picks its target and its whole route, on the pre-raid map **with the player's
    placements**. The Decoy acts here, at plan time.
  - The threat walks that route. It strikes each live node it stops on, and strikes its target until the target is
    TAKEN. Then it leaves.
  - Threats still standing at the step cap TAKE their node, as today.
- **Why it lifts the scores.**
  - **Predictability:** the warning arrows are the whole truth.
  - **No-words:** one arrow per threat, end to end.
  - **What / why / when:** the route can be drawn at the warning.
  - It is the Kingdom Rush / Into the Breach contract: a path is a promise.
- **Cost.** A resolver change in `_move_threats` and `_target_of`, and the tests that pin re-targeting.

### R2. Home is never a corridor
- **Today.** A threat bound for another node can route **through** the home server. It hits home, and is spent there.
  In the lab, a Decoy on the Firewall pulled two threats through home (critic R2, finding 1).
- **Proposed.** Only a threat whose target is home may enter home. Others route around it. If there is no other way,
  home becomes their target, and the arrow says so.
- **Why.** No player predicts "my decoy walked them through my house". Home surprises drop to 0.

### R3. A stated tie-break: "they probe the weaker node"
- **Today.** Equal-length routes are broken alphabetically by site id. That is invisible and arbitrary.
- **Proposed.** On equal length, the route goes through the node with lower integrity, then by id. Draw a small
  cracked-shield glyph where a route forks.
- **Why.** It can be guessed from the map. It is thematic, and it ties damage you left unpatched (SCUFFED) to the next
  raid's route.

### R4. A held threat does not strike
- **Today.** An ICE Lock holds a threat for 2 steps, but the held threat still damages the node it stands on (except at
  home).
- **Proposed.** A held threat does nothing: no move and no strike.
- **Why.** The snowflake then means one thing: "this one is frozen". Clean % goes up from 3.27 to 4.83 without making
  it common. ICE becomes a timing tool for the turrets.

### R5. The Armory becomes a draft: bring 3 of what you own
- **Today.** The Armory holds up to 6 pieces, and every owned piece can deploy. The lab scenario's 3-piece Armory had **no**
  clean defense in 2,058 placements, so the +5 Heat / +12 Schematics reward was decoration.
- **Proposed.** Each raid deploys up to N pieces (config; N = 3 here) chosen from the Armory, so the choice starts at the
  draft. This also relies on content giving at least one high-damage piece (the Railgun). With only Turret, ICE and Decoy,
  no clean defense exists.
- **Why.** Decision depth was 6 in both rounds ("brute force over four pieces"). A draft adds a choice before placement,
  and makes a clean defense a real but hard target. Both critics asked for this.

## Clarifications (no maths change; the rule becomes stated and shown)

| # | Topic | Today | Proposed wording / display |
|---|---|---|---|
| C1 | **Clean defense** | Three definitions in circulation: D27's "no damage", the resolver's "home undamaged and no DOWN/TAKEN", and C's own. | Use the resolver's: **home untouched, no node DOWN or TAKEN**. A SCUFFED node (it held but lost integrity) is still clean. Record that D27's "no damage" means this. **Designer decision** (the other reading is stricter and makes clean rarer still). |
| C2 | **SCUFFED** (held, integrity lost) | Not named. Integrity stays low after the raid at no cost. A node at 3/15 then becomes the next "weakest" target. | Name it and mark it (teal check with a red corner and −N). It persists until patched, **1 Schematic per point**, like home. **Designer decision.** With R3 the link becomes visible: a scuffed node draws the next raid. |
| C3 | **Cascade** | 50 % of the excess damage when a node goes DOWN spreads to live neighbours, and it is drawn nowhere. | Draw it as a dashed red spill arrow with −N, in the telegraph and in the playout. Alternatively cut it for clarity. **Designer decision**; the lab recommends drawing it. |
| C4 | **Speed** | A live node stops the advance, so speed 2 only matters through empty or neutral sites. | State it: "fast threats cross empty sites in one step". Draw the Auditor's two-link hop as one arrow. |
| C5 | **Damage in passing** | A threat strikes every live node it stops on, not just its target. | State it, and draw a small strike badge at each stop on the route. |
| C6 | **Strike order inside a step** | Fixed by content id, and hidden. | Show it with numbered badges. It is already deterministic. |
| C7 | **When** | GDD 4.4: a raid can land mid-netrun (as an interlude) or between netruns. | Either always land on the return to HQ, with a countdown of netrun map nodes left on the netrun map, or show the interlude point on the netrun map. **Designer decision**; the lab recommends always on return. |
| C8 | **What a lost raid costs** | Losses are listed after the raid. | Before committing, show the plan's price in the same units as the report: coins to repair and patch, netruns to reclaim, and new entry points. |

## Expected effect on the rubric (lab estimate, to be confirmed by a critic)

| Axis | R2 best | With R1–R5 and C1–C8 | Driver |
|---|---|---|---|
| What / why / when | 8 | 9 | C7 countdown, and R1 routes drawn at the warning |
| Predictability | 8 | 9 | R1 to R4: the telegraph never lies, and the rules are guessable |
| No-words | 7 | 8 | one arrow per threat; one meaning per icon (R4) |
| Decision depth | 6 | 8 | R5 draft; a reachable clean target; R3 makes unpatched damage matter next raid |
| Consequences | 8 | 9 | C2 SCUFFED priced and persistent; C8 the price before commit; TAKEN gives new entries |

Round 3 mockups (the merged A+B concept) use this package, so the next critic can confirm or refute the estimate.

## Migration notes for the build session
- **R1 and R2** are the main work: `RaidResolver._move_threats` and `_target_of`, plus a precomputed route per threat
  (the setup forecast already calls the same resolve). The forecast data can then expose `route` per threat for the view.
- **R3** touches `GridState.next_hop` (the tie-break key).
- **R4** is one guard in `_damage_nodes`.
- **R5** needs a config key `raid_deploy_cap`, and a draft step in Raid Setup.
- **C2** needs patching for non-home nodes (the home patch exists, 2026-09-24).
- **The rest** is view work.
- **Every change** needs its rule test (CLAUDE.md rule 6). The existing resolver tests that pin re-targeting will change.
