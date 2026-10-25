# G1 simulation: run the four Solace merge concepts and the corp path rules (designer 2026-10-25)

**Designer:**
- "Run a version of each option and decide which plays best."
- The corp's paths are our call. The goal is a high critic score.
- **Rule (designer):** every raid line starts at the corp HQ (the Genome Core), ends at our HQ, and takes its own
  path through the network, so the design must fit networks of any shape.

**Read first:**
- docs/design/raid_concepts/SOLACE_MERGE_IDEAS.md (concepts A–D, the numbers, section 1 on Solace today);
- docs/design/raid_concepts/INTEGRATION_PLAN.md;
- docs/handoff/raid_lab_l8/L14_RULES.md;
- tools/raid_concepts/sweep_l8.py (the lab oracle, L14: the deck, wounds, sealed A/B, hunter, responses, greedy and
  naive planners);
- D:/rc_tmp/raid_design_lab/integration/solace_geom.py (the Solace graph, copied from content/corporations/solace.tres:
  LINKS, LOCKED, tiers, exploits).

## What to build: tools/raid_concepts/sweep_g1.py (plus helper modules if needed, all in tools/raid_concepts/)

Python 3 stdlib only, deterministic and seeded. Reuse sweep_l8's raid machinery wherever it fits: the deck and hand,
wounds, the typed BLOCK and HIT scan, the HOME hit once per raid, the responses, tiers, the score, and the
greedy-over-outcomes planner. Generalize the board from a 4×3 grid to a **graph**:
- Owned Sites with statuses OK / DOWN / TAKEN.
- A **line** is an ordered list of Sites. Scanning works as in the lab, and a line that ends at HOME hits HOME.

### Campaign model (shared by every concept)
- **Netrun step:** the player claims one Site that is next to its territory (a claim = a netrun). Policies:
  - **greedy:** best value or exploit by a one-step lookahead;
  - **keys:** the exploit chains first;
  - **random.**
- **Raids** are queued by each concept's trigger, with one base trigger: one raid per 2 netruns.
- **A campaign** lasts 12 netruns, or ends at a loss.
- **Win proxy:** hold 3 exploits at the end with HOME above 0.
- Starting values follow the lab: bank, Heat, HOME 3, the L14 start deck.
- Site values: T1 6, T2 8, T3 10, exploit +6.

### Corp path rules (test all three inside concepts A and C)
- **P-open:** simple paths from the Genome Core to HOME using only links the player has opened. Locked cross-links
  open when the player claims both ends.
- **P-all:** any simple path from the Core to HOME, locked links included, of length at most (tiers + 2).
- **P-target:** P-all, but the candidates are the paths through the most owned Sites (top-k by owned count, ties
  broken by seeded rng). This is the "corp hunts you" rule.

**Per raid**, the corp draws:
- the known beams (beam 1, plus extras at the Heat bands);
- sealed A and B: the 3 candidates are distinct paths with distinct types, and B differs from A;
- the hunter (H-street): a candidate pair of cross paths that never reach HOME (a tier ring over cross-links, or a
  spoke segment).

Record the number of available paths per raid.

### The concepts (one version each, following SOLACE_MERGE_IDEAS.md; keep each as close to its doc as possible)
- **A, Contagion Sweep:**
  - path raids on the real Solace graph;
  - the infection figure is fed by HITs (+8 %), HOME hits (+15 %) and TAKEN (+5 %);
  - at 100 % the city is lost.
- **B, Three Wards:**
  - the ward board (3 wards × 3 tiers = 9 cells, the beam hits the best Site in a cell; lines are the ward rows,
    lab-style);
  - per-ward meters, with exploits moved to one per ward;
  - the QUARANTINE dose response.
- **C, Bloom Tide:**
  - path raids on the real graph;
  - the tide front advances per netrun by tier (100 / 130 / 160 thousandths of a column, times the Heat table, Virus
    ×0.75);
  - doses push it back (the sources and amounts in the doc);
  - Sites the front reaches go DOWN;
  - each column crossing queues a Tide raid;
  - the field dose response comes after reveal B (push 150, one per raid);
  - CITY LOST when the front reaches HOME.
  - **Also test the Tongue hunter (H-tongue):** the hunter runs the Sites on the front column instead of a street.
- **D, Carrier Deck:**
  - the 3×3 lattice board (lab-shaped);
  - infected cards in the defense deck spread by 1 per raid unless a DOSE card is spent;
  - drawing an infected card in a netrun is abstracted as −X to that netrun's claim value;
  - lost when infected cards outnumber healthy ones.

Where the doc leaves a number open, pick the simplest value and list it under "assumed" in the report.

## Measure (per concept and variant: 200 campaigns per claim policy; greedy raid play vs naive)
- **S proxy:**
  - **locked_at_plan:** the share of raids where every A×B×hunter outcome has the same tier for the chosen
    placement. Lower is better. The lab measured about 0.6–0.7.
  - **live_after_response:** the share of raids where the outcome still varies after the response is picked.
- **D proxies:**
  - **response_decides:** the best response differs from HOLD in tier on the real outcome.
  - **placement_gap:** the EV of the best placement minus the median one.
  - **between_diversity:** the entropy of between choices.
  - **path_variety:** distinct paths per raid.
- **C proxy:** wounds per campaign, Sites lost, and how often the timer was decisive.
- **Relevance:** the share of raid lines that touch owned territory, and the HOME hit rate.
- **Balance:**
  - greedy and naive loss rates (target: greedy ≤ 15 %, naive ≥ 50 %);
  - the win proxy;
  - campaign length;
  - raids per netrun (target about 0.33–0.5).
- **Runtime:** state it. Bound it so the whole sweep finishes in under 40 minutes; reduce campaigns if needed and
  say so.

## Outputs
- **tools/raid_concepts/sweep_g1.py,** plus a JSON summary at D:/rc_tmp/raid_design_lab/g1/sweep_g1.json.
- **docs/design/raid_concepts/G1_RESULTS.md:**
  - the table of every concept and variant against every metric;
  - the assumed numbers;
  - a short rule sheet per concept, at most 25 lines each, as it was simulated. A blind critic will score from these
    sheets, so write them as player-facing rules without concept names, labelled "Design 1–4".
  - your read of which plays best and why (keep it separate from the rule sheets).
- **Do not touch:** scripts/, content/, scenes/, GDD.md or DECISIONS.md.
