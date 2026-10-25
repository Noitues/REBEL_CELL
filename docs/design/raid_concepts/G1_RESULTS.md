# G1 results: four Solace merge concepts and three corp path rules, simulated as campaigns

Status: lab measurement for the designer (brief `docs/handoff/raid_integration/G1_SIM.md`, 2026-10-25). Nothing in
`scripts/`, `content/`, `scenes/`, GDD.md or DECISIONS.md changed.
Oracle: `tools/raid_concepts/sweep_g1.py` + `tools/raid_concepts/g1_geo.py` (stdlib, seeded; `--check` replays a
seed twice per variant and player and asserts the same record). Raw summary:
`D:/rc_tmp/raid_design_lab/g1/sweep_g1.json` (12 netruns) and `sweep_g1_n24.json` (24-netrun sensitivity run).
Print a table: `python tools/raid_concepts/sweep_g1.py --table <json>`.

**Runtime:** 211 s for the full sweep (11 variants x 3 claim policies x 200 campaigns x 2 raid players = 13,200
campaigns, 5 worker processes on this machine), plus 206 s for the 24-netrun run (100 campaigns per policy). No
campaign count was reduced.

---

## 1. Results table (12 netruns; all three claim policies pooled, 600 campaigns per cell)

Raid metrics are from the **greedy** raid player unless the column says N (naive). Lower is better for locked.

| Variant | G loss | N loss | G city lost | Win | Raids/run | Locked at plan | Live after resp. | Resp. decides | Late used | Place. gap | Between H (bits) | Path variety | Paths avail. | Relevance | HOME hit | Wounds | Timer at end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-open | 0.70 | 1.00 | 0.70 | 0.05 | 0.50 | 0.67 | 0.19 | 0.30 | – | 17.7 | 2.63 | 6.7 | 15.8 | 0.62 | 0.34 | 3.95 | 112 % |
| A-all | 0.44 | 1.00 | 0.44 | 0.25 | 0.50 | 0.80 | 0.13 | 0.29 | – | 20.4 | 2.77 | 7.0 | 29 | 0.54 | 0.39 | 2.92 | 98 % |
| A-target | 0.92 | 1.00 | 0.92 | 0.00 | 0.50 | 0.61 | 0.22 | 0.21 | – | 13.1 | 2.28 | 6.8 | 29 | 0.76 | 0.38 | 3.74 | 126 % |
| B-wards | 0.01 | 0.66 | 0.00 | 0.15 | 0.50 | 0.72 | 0.18 | 0.24 | 0.28 (QUAR.) | 9.7 | 2.65 | 5.9 | 3 | 0.69 | 0.43 | 5.47 | 62 % (worst ward) |
| C-open | 0.00 | 0.35 | 0.00 | 0.35 | 0.50 | 0.66 | 0.21 | 0.32 | 0.00 | 7.1 | 2.71 | 6.7 | 16.7 | 0.63 | 0.34 | 5.20 | 26 % |
| C-all | 0.00 | 0.22 | 0.00 | 0.52 | 0.50 | 0.79 | 0.14 | 0.29 | 0.00 | 7.2 | 2.89 | 7.0 | 29 | 0.53 | 0.39 | 3.87 | 26 % |
| **C-target** | **0.03** | **0.65** | 0.00 | 0.36 | 0.50 | **0.62** | 0.24 | 0.21 | 0.00 | 5.4 | 2.28 | 6.8 | 29 | **0.76** | 0.44 | 5.68 | 29 % |
| C-open-tongue | 0.00 | 0.31 | 0.00 | 0.34 | 0.50 | 0.71 | 0.19 | 0.30 | 0.01 | 7.2 | 2.72 | 6.7 | 16.7 | 0.60 | 0.33 | 4.81 | 26 % |
| C-all-tongue | 0.00 | 0.15 | 0.00 | 0.50 | 0.50 | 0.84 | 0.12 | 0.28 | 0.01 | 7.1 | 2.88 | 7.0 | 29 | 0.50 | 0.38 | 3.67 | 26 % |
| C-target-tongue | 0.03 | 0.62 | 0.00 | 0.39 | 0.50 | 0.61 | 0.23 | 0.21 | 0.03 | 5.5 | 2.35 | 6.8 | 29 | 0.75 | 0.43 | 5.31 | 28 % |
| D-lattice | 0.01 | 0.77 | 0.00 | 0.31 | 0.50 | 0.67 | **0.25** | 0.16 | 0.24 (CURE) | 5.5 | 2.44 | 5.9 | 3 | 0.70 | 0.49 | 3.00 | 2 % (INFECTED/healthy) |
| *lab L14 (ref.)* | *0.00* | *1.00* | | | | *~0.47–0.6* | | *0.53* | | | | | | | | *0.45/leg* | |

Column notes:
- **Locked at plan**: share of raids where all 12 A x B x hunter outcomes of the chosen placement have one tier (under
  HOLD). **Live after resp.**: share where, on the real A with the chosen response (and late choice), the 4 (B, hunter)
  outcomes still differ in tier. **Resp. decides**: the chosen response (+ late) changes the real outcome's tier against
  HOLD. All three count tiers only; a response that only moves a timer (QUARANTINE, CURE) is in "Late used".
- **Late used**: C = the field dose, D = CURE (both after REVEAL B); B = QUARANTINE (a RESPONSE, shown here for
  comparison). The field dose and CURE never changed a tier (late_decides 0.000–0.003).
- **Place. gap**: EV of the best placement minus the median one (planner value points; a T2 Site is 8).
- **Between H**: entropy of the between choices (repair? / build or CLEAN / dose verb / PATCH).
- **Path variety**: distinct lines drawn per raid (3 known beams + 3 sealed + 2 hunter candidates; max 8).
  **Paths avail.**: route paths the corp could pick from (B and D: the 3 rows).
- **Relevance**: share of the lines that ran which touched owned live territory.
- **Timer decisive**: the share of campaigns lost to the timer equals the "G city lost" column (greedy) and was
  0.000–0.030 for every naive player outside A (A naive: 1.00).
- Raids per netrun is 0.50 everywhere (the base trigger). B's 50 % trigger and C's tide crossings almost always land
  on a netrun that already queued a raid; they add 0.00–0.03.

**Per claim policy (greedy raid player; loss / win):**

| Variant | greedy claims | keys first | random claims |
|---|---|---|---|
| A-all | 0.59 / 0.33 | 0.53 / 0.43 | 0.20 / 0.00 |
| B-wards | 0.00 / 0.00 | 0.04 / 0.45 | 0.01 / 0.00 |
| C-all | 0.00 / 0.74 | 0.00 / 0.82 | 0.00 / 0.01 |
| C-target | 0.00 / 0.60 | 0.09 / 0.48 | 0.01 / 0.00 |
| D-lattice | 0.00 / 0.32 | 0.02 / 0.49 | 0.00 / 0.11 |

Naive loss by policy for C-target: 0.70 / 0.91 / 0.35; for D: 0.54 / 0.98 / 0.79; for B: 0.42 / 0.95 / 0.62.

**24-netrun sensitivity run** (100 campaigns per policy; the real campaign is 24–45 runs, so 12 is short for a timer):

| Variant | G loss | N loss | G city lost | Win | Locked | Resp. decides | Late used | Wounds | Timer at end |
|---|---|---|---|---|---|---|---|---|---|
| A-all / A-open / A-target | 1.00 / 1.00 / 1.00 | 1.00 | 1.00 | 0.00 | 0.61–0.81 | 0.20–0.30 | – | 3.8–4.6 | 132–139 % |
| B-wards | 0.86 | 1.00 | 0.59 | 0.00 | 0.81 | 0.22 | QUAR. | 18.0 | 109 % |
| C-all | 0.00 | 0.66 | 0.00 | 0.01 | 0.86 | 0.28 | 0.00 | 19.1 | 64 % |
| C-open | 0.15 | 0.76 | 0.00 | 0.00 | 0.75 | 0.30 | 0.00 | 19.5 | 65 % |
| C-target | 0.43 | 0.92 | 0.00 | 0.00 | 0.73 | 0.19 | 0.00 | 18.2 | 62 % |
| C-target-tongue | 0.35 | 0.91 | 0.00 | 0.00 | 0.73 | 0.19 | 0.02 | 18.6 | 63 % |
| D-lattice | 0.07 | 1.00 | 0.01 | 0.32 | 0.75 | 0.18 | 0.29 | 9.6 | 14 % |

---

## 2. Assumed numbers and rulings made by the oracle (where the brief or the doc left them open)

Campaign:
- Start: bank 10, Heat 44, HOME 3, the L14 8-card deck, ghost kit 2 per campaign; no Site owned (the first raid comes
  after 2 claims, the lab's 2 start cells).
- 12 netruns; a netrun queues at most one raid; the base trigger is "2 netruns since the last raid", and a concept
  trigger resets it (so concept raids replace rather than add to the base cadence).
- Income per netrun: sum(value // 6) over OK Sites (the lab's sum(v // 3) per raid, at 2 runs per raid).
- Heat per claim: + tier (1/2/3), + 5 more for an Exploit (Solace SOLACE_BAL_r2); a Heat objective claimed the first
  time gives its sink (-5 / -5 / -8 / -8) instead; a re-claim or a patrol +1. EVADED -10, card responses +2, ghost +5
  (lab).
- A TAKEN Site can be claimed back by a netrun. Claims use base links only (locked links never help a claim).
- **PATCH HOME** (added; an existing HQ verb kept by INTEGRATION_PLAN): +1 HOME pip for 8 bank at the between step.
  Without it, HOME 3 over 6 raids breached almost every campaign (probe: naive 100 % by raid 3, greedy ~50 %). The
  naive player patches when it can, then repairs.
- Repair = value // 2 (no free repair; the intensity perks are gone). Build a GUARD card 3, CLEAN a wound 4 (lab).
- Netrun doses: every 3rd netrun banks one (B and D: a DOSE card into the deck; C: a held dose). This abstracts "an
  unused netrun dose banks one" / "is pushed into the tide".
- Win proxy: all 3 Exploits live at the end and HOME > 0.

Corp draws (graph concepts A and C):
- Path length for P-all: at most 5 links from the Core to HOME (tiers 3 + 2), which allows one sideways step. 29 paths.
  P-open: only base links plus locked links whose two ends the player has claimed (permanent once opened); length
  capped at 9 links. P-target: the P-all paths ranked by live owned Sites on them; the 3 sealed candidates are the top
  3, ties by seeded rng.
- Known beams: 50 % a route (uniform from the rule's pool; P-target uses the P-all pool), 50 % a street from the
  hunter pool. Extras at Heat 50 / 75 (lab).
- H-street pool: the three tier rings across the candidates' spokes (a ring is drawn by rule, north to south, as in
  SOLACE_MERGE_IDEAS A), plus the T3 -> T1 segment of every other spoke that holds a live Site. Two drawn.
- H-tongue: the tier rings across the candidates' spokes at the two columns first inward of the front (padded outward).
- A beam still scans its whole path in C (the doc's "beams start at the front" contradicts its own "shorter when
  pushed back", so it was left out).

Concept numbers (doc values unless marked *assumed*):
- A: +8 % per HIT, +15 % per HOME hit, +5 % per TAKEN (raid or DECAY), -10 % on EVADED, -15 % per Heat objective,
  CITY LOST at 100 %. No Proxy Relay in the model.
- B: Exploits on t2_intel / t2_e / t2_h; +2 % per netrun in every standing ward, +8 % per HIT in the ward, +15 % to the
  ward of a HOME-hitting row; -15 % for the ward's Heat objective; -5 % on EVADED; a ward at 100 % falls (its Sites
  TAKEN, a wound each, no more claims there); CITY LOST at 2 fallen wards; +1 raid the first time a ward reaches 50 %.
  2 DOSE cards in the start deck; QUARANTINE consumes the DOSE card (*assumed*: "spend") and costs no Heat. A HIT on a
  DOWN Site in a quarantined ward leaves it DOWN. The fallen ward's "beams one column deeper" is not modelled.
- C: front 4000; pace per netrun T1 100 / T2 130 / T3 160 (patrol 100) x the S2 table 100/110/125/140/160 % by Heat
  band (*assumed* band edges 25 / 50 / 75 / 90) x 75 % with the Virus key; Breach key +500 once; Heat objective +300;
  EVADED +200; HQ dose 300 (a held dose, or bought for 12 bank, +4 per purchase); field dose 150 (a held dose, one per
  raid, after REVEAL B); an owned Site at column >= front goes DOWN and comes back OK when pushed past (repairs cannot
  fix it while the front covers it); a Tide raid the first time the front crosses 3000 / 2000 / 1000; CITY LOST at 0.
  Not modelled: Proxy Relay, death pace, the netrun's street Bloom start cut.
- D: lattice 3 x 3 anchors (T1 6 / T2 8 / T3 10, Exploits on the three T2 anchors), 2 annexes per anchor at the
  anchor's tier value (*assumed*), 4 Heat objectives hung on A1 / C1 / C2 / B3 (each gives a DOSE card when first
  claimed). Annexes are lost (no wound) when their anchor goes TAKEN. Spread: +1 INFECTED at each DECAY when any is in
  the deck unless a DOSE card is spent (greedy always spends; naive never). A netrun draws 5 defense cards; each
  INFECTED drawn costs 2 bank (X = 2, *assumed*). CURE (late slot, a DOSE card in the response hand) removes one
  INFECTED. CITY LOST when INFECTED >= healthy cards.

Planner (greedy raid player):
- Value = the lab score (bank + Sites + 6 per Exploit - 15 per HOME pip - Heat terms - 5 per wound, + 2.5 per kit
  item) plus a timer term: A -0.003 per basis point, B -0.25 per ward %, C -0.01 per milli of tide, D -2 more per
  INFECTED; +3 per held dose / DOSE card. Raising A's weight to 0.008 or 0.02 did not lower A's loss rate (0.54 / 1.00
  for A-all / A-target at every weight), so A's losses come from its numbers, not from the planner.
- Placement: a HOLD screen of every placement (at most 2 hand cards, on live cells that lie on one of this raid's
  lines; ghost none or HOME), then the full response and late-slot search on the 3 best. Ghost on a Site is not
  offered. Response targets are restricted to cells on this raid's lines (plus the cheapest off-line cell for
  SACRIFICE).
- Between: the option with the best value after the next DECAY (so repairs count).
- Claims: greedy = the best value after one netrun; keys = the claim nearest to an unowned Exploit (then value, id);
  random = seeded.

---

## 3. Rule sheets (player-facing, as simulated; for a blind critic)

### Design 1
- Your Cell holds Sites in a city network. The enemy HQ sits at the far end; your HQ (HOME, 3 integrity) at the near end.
- Each run you claim one Site linked to your territory. Every 2 runs (sooner if the Bloom crosses a ring) the corp raids.
- **The Bloom.** A front of infection starts at the enemy HQ and creeps toward HOME a little every run (deeper runs and
  higher Heat make it faster). Your Sites behind the front are infected: DOWN, and repair cannot save them. If the front
  reaches HOME, the city is lost. Doses push it back: a Heat objective Site, an evaded raid, or a dose you hold or buy.
- **A raid.** You draw a hand from your defense deck (drones, netrunners, enforcers; some can SHIFT, one can JAM).
- Beams travel paths from the enemy HQ to HOME. You see the known beams and the 3 paths the corp might use: they are
  the paths through the most of your Sites. The corp fires two of them, each with its own type.
- PLAN: place up to 2 cards on your Sites. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits each of your Sites once per raid (OK -> DOWN, DOWN -> TAKEN) and, at the end of a path, HOME.
- The first sealed path is revealed. Then pick one RESPONSE: hold, move a card (SHIFT), add a card, JAM the hunter,
  or SACRIFICE a Site (it is lost now, HOME is safe this raid). Then the second path fires.
- After the second path, you may spend a held dose in the field: the Bloom steps back, and Sites it leaves are healed.
- Last, a hunter sweeps one of two cross streets (shown in advance) that never reach HOME.
- Every Site lost adds a dead card to your deck. A Site left DOWN falls at the next raid unless repaired.
- Between raids: repair a Site, build a card or clean a dead one, buy or use a dose, patch HOME.
- You win by holding all three key Sites; you lose if HOME falls or the Bloom reaches it.

### Design 2
- Your Cell holds Sites in a city network. The enemy HQ sits at the far end; your HQ (HOME, 3 integrity) at the near end.
- Each run you claim one Site linked to your territory. Every 2 runs the corp raids.
- **Infection.** The city has one infection figure. Every hit on your Sites raises it 8 %, a hit on HOME 15 %, every
  Site lost 5 %. An evaded raid lowers it 10 %; a Heat objective Site lowers it 15 %. At 100 % the city is lost.
- **A raid.** You draw a hand from your defense deck (drones, netrunners, enforcers; some can SHIFT, one can JAM).
- Beams travel paths from the enemy HQ to HOME, at most one sideways step. You see the known beams and 3 possible paths
  the corp picked; it fires two of them, each with its own type.
- PLAN: place up to 2 cards on your Sites. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits each of your Sites once per raid (OK -> DOWN, DOWN -> TAKEN) and, at the end of a path, HOME.
- The first sealed path is revealed. Then pick one RESPONSE: hold, move a card (SHIFT), add a card, JAM the hunter,
  or SACRIFICE a Site (it is lost now, HOME is safe this raid). Then the second path fires.
- Last, a hunter sweeps one of two cross streets (shown in advance) that never reach HOME.
- Every Site lost adds a dead card to your deck. A Site left DOWN falls at the next raid unless repaired.
- Each forecast row shows the tier and the infection change.
- Between raids: repair a Site, build a card or clean a dead one, patch HOME.
- You win by holding all three key Sites; you lose if HOME falls or infection reaches 100 %.

### Design 3
- The city is a 3 x 3 board: three routes from the enemy HQ to HOME (3 integrity), three districts deep, with streets
  joining neighbours. Each district has an anchor Site and two side Sites that are safe while the anchor stands.
- Each run you claim one Site: an anchor next to your board, or a side Site of an anchor you hold. Every 2 runs, a raid.
- **The infection is in your deck.** Every Site you lose adds an INFECTED card. At the start of each raid, if any
  INFECTED card is in your deck, one more is added unless you spend a DOSE card. INFECTED cards are dead draws in raids
  and cost you in runs. If INFECTED cards ever equal your healthy cards, the city is lost. DOSE cards come from runs and
  Heat objective Sites.
- **A raid.** You draw a hand (drones, netrunners, enforcers; some can SHIFT, one can JAM; DOSE cards).
- You see the known beams; the corp will fire two of the three routes, each with its own type.
- PLAN: place up to 2 cards on your anchors. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits each of your anchors once per raid (OK -> DOWN, DOWN -> TAKEN) and, at the end of a route, HOME.
- The first sealed route is revealed. Then pick one RESPONSE: hold, move a card, add a card, JAM the hunter, or
  SACRIFICE an anchor (it is lost now, HOME is safe this raid). Then the second route fires.
- After the second route, you may play a DOSE card to CURE: remove one INFECTED card.
- Last, a hunter sweeps one of two streets (shown in advance).
- A losing anchor takes its side Sites with it. An anchor left DOWN falls at the next raid unless repaired.
- Between raids: repair, build a card or clean an INFECTED card, patch HOME.
- You win by holding all three key anchors; you lose if HOME falls or the infection overwhelms your deck.

### Design 4
- The city is three wards (north, middle, south), each three rings deep, between the enemy HQ and HOME (3 integrity).
  A block is one ward at one ring; it may hold several of your Sites. Each ward holds one key Site.
- Each run you claim one Site linked to your territory. Every 2 runs (or the first time a ward reaches 50 %), a raid.
- **Three infection meters**, one per ward. Every run adds 2 % to each ward; a hit in a ward adds 8 %; a hit on HOME
  adds 15 % to the ward it came through. An evaded raid cures every ward 5 %; a Heat objective Site cures its ward 15 %.
  A ward at 100 % falls: all your Sites in it are lost. Two fallen wards lose the city.
- **A raid.** You draw a hand (drones, netrunners, enforcers; some can SHIFT, one can JAM; DOSE cards).
- Beams run a ward from the enemy HQ to HOME, or a ring across the wards. You see the known beams; the corp will fire
  two of the three wards, each with its own type.
- PLAN: place up to 2 cards on blocks. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits the most valuable of your Sites in each block it crosses, once per Site per raid
  (OK -> DOWN, DOWN -> TAKEN), and, at the end of a ward, HOME.
- The first sealed ward is revealed. Then pick one RESPONSE: hold, move a card, add a card, JAM the hunter, SACRIFICE a
  block (lost now, HOME is safe this raid), or QUARANTINE a ward with a DOSE card (its meter does not rise this raid and
  its Sites cannot be lost). Then the second ward fires.
- Last, a hunter sweeps one of two rings (shown in advance).
- Every Site lost adds a dead card to your deck. A Site left DOWN falls at the next raid unless repaired.
- Between raids: repair, build a card or clean a dead one, patch HOME.
- You win by holding all three key Sites; you lose if HOME falls or two wards fall.

---

## 4. My read (separate from the sheets)

Sheet key: Design 1 = C Bloom Tide (P-target, street hunter), Design 2 = A Contagion Sweep (P-all), Design 3 = D Carrier
Deck, Design 4 = B Three Wards.

**Pick: C, Bloom Tide, with the P-target path rule and the street hunter (C-target).** Reasons, in order:
1. **It is the only concept that both fits the designer's path rule and is balanced.** The designer's rule (every line
   leaves the Genome Core, ends at HOME, and takes its own path through any network) rules out B and D as simulated:
   both need a fixed 3-row board (B by regrouping and moving the Exploits, D by rewriting the grid). Of the two graph
   concepts, A fails balance badly: greedy loses the city 44–92 % at 12 runs and 100 % at 24, and a heavier planner
   weight does not help. C-target sits on the brief's balance targets: greedy loss 3 % (target ≤ 15 %), naive 65 %
   (target ≥ 50 %).
2. **P-target is the strongest lever measured, more than the timer.** Ranking the corp's paths by owned Sites gives
   the lowest locked-at-plan of any variant (0.61–0.62, against 0.79–0.84 for P-all and 0.66–0.71 for P-open), the
   highest relevance (0.76: three of four lines touch the player, against 0.50–0.63), and it removes the free EVADED
   raid (2 in 3,400 raids against ~300). It does the same for A. "The corp hunts you" is the rule to keep whichever
   timer is chosen.
3. **It keeps the doc's graph features working.** The tide costs the player Sites over time (0.6 front-infected Sites per
   12-run campaign, 6–9 per 24-run one), which is the designer's "too slow and the city is infected".

What the data says against C, honestly:
- **The tide is never decisive.** At 12 runs it ends near 28 %, at 24 runs near 63 %, and no campaign was lost to it.
  Its bite is indirect: infected T3 / T2 Sites decay into wounds (C wounds 5.7 per 12 runs against 3.0 for D). To make
  it a real clock, raise the pace (about x1.6 puts the 24-run front near HOME) or start it nearer, then re-measure.
- **The field dose (C's R15 fix) is not used:** 0–3 % of raids, and it never changed a tier. A held dose is worth 300
  of tide at the HQ against 150 in the field, and the tongue shift only matters right after a crossing, which is rare.
  It needs to be cheaper than the HQ use or stronger (e.g. heal plus stop the hunter) before it can lift S.
- **The tongue adds nothing measurable** over the street hunter (locked 0.61 vs 0.62, late use 0.03). Keep the street
  hunter; the tongue is a presentation idea, not a rule gain.
- **Longer campaigns break HOME 3:** C-target greedy loses 43 % at 24 runs (BREACHED, 12 raids). The real campaign
  needs HOME 50 with patching tuned, or fewer raids per run, before the port.
- Response decides 0.21 (lab 0.53): on the real graph, with 3 sealed paths ranked by ownership and HOME hit 44 % of
  raids, more raids are settled before the response. This is the S axis, and no concept here reaches the lab: the best
  live-after-response is D at 0.25.

**Second choice: D (Carrier Deck)** if the designer accepts a fixed board. It is the most robust at 24 runs (greedy loss
7 %, naive 100 %, win 32 %), has the highest live-after-response (0.25) and the only late slot that gets used (CURE
24–29 % of raids, though it never changes a tier). It breaks the path rule and costs the content rewrite.
**B** has a real non-tier decision (QUARANTINE in 28 % of raids), but its per-ward clocks collapse in long campaigns
(86 % greedy loss at 24 runs, 59 % to fallen wards). **A** should be dropped as written: its infection is a second HOME
bar that hits 100 % in about five raids.

Suggested next round (oracle only): C-target with the tide pace x1.6, a field dose at 300 (equal to the HQ use) that
also heals the Sites it passes, HOME patch tuned for 24 runs, then the brief's gates again.
