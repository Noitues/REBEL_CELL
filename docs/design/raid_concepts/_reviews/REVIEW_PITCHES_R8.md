# Raid pitches: fresh critic review

**Verdict: none of the 12 pitches is a 9 on its own. The strongest direction is evasion: Pursuit (2) or Ghost Protocol (11), or the two merged. Ring Pursuit (3) is the only strong pitch that uses the core verb, but it is the most expensive. Bastion (12) is a sound baseline with a generic look. The Offer (6) and Honeypot (8) are modifiers, not raid models.**

Sources: GDD sections 1–4 and 7 (read-only), and PITCHES.md. I opened no other review.
Scale: 7 means a good shipped game does this about this well. Axes: WWW = what / why / when, Pred = outcome predictability, NoW = no-words test, Dep = decision depth, Con = consequences. Total is out of 50.

## 1. Score table

| # | Pitch | WWW | Pred | NoW | Dep | Con | **Total** | Fit | Most likely failure |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ring Siege | 6 | 8 | 7 | 7 | 5 | **33** | 8 | The exact forecast turns setup into trial-and-error search. The fight is cut off from the network, so losses no longer land on territory. |
| 2 | Pursuit | 9 | 7 | 8 | 8 | 7 | **39** | 9 | It is a campaign clock, not a raid. The HQ siege is undefined, and the ambush is a hands-on fight. The front either never matters or forces the minimum path. |
| 3 | Ring Pursuit | 9 | 7 | 7 | 8 | 7 | **38** | 9 | Two new systems at once. The link from route to spoke is invisible across several netruns of delay. |
| 4 | Mirror Netrun | 6 | 5 | 6 | 6 | 6 | **29** | 8 | An auto-resolved wheel fight is a slot machine to watch. A chain of small fights blows the 30–60 s playout. |
| 5 | Deck Fortress | 4 | 6 | 5 | 7 | 4 | **26** | 5 | The run deck dies with the operative (GDD 4.2), so a death wipes the fortress. Dead draws in netrun combat feel bad. |
| 6 | The Offer | 7 | 8 | 3 | 5 | 7 | **30** | 7 | One arithmetic choice (pay the cheapest acceptable offer). Priced text offers fail the no-words test. It needs a base model. |
| 7 | Counterstrike | 6 | 5 | 4 | 8 | 7 | **30** | 8 | Two parallel auto-battles on a split screen is unreadable. The counter-hack is another wheel with no input. |
| 8 | Honeypot Farm | 8 | 6 | 6 | 7 | 6 | **33** | 6 | Once defense is solved, maximum lure dominates and Heat stops being pressure. Snowball. |
| 9 | Signal War | 5 | 5 | 7 | 6 | 5 | **28** | 5 | Overlapping influence fields cannot be read without numbers, which makes it a spreadsheet. Flips feel fuzzy, not fair. |
| 10 | The Rack | 4 | 8 | 8 | 8 | 6 | **34** | 3 | A different game bolted on. Three to five raids per campaign is too few to learn a packing-synergy system. |
| 11 | Ghost Protocol | 9 | 9 | 8 | 5 | 6 | **37** | 9 | Perfect information plus a binary found/lost result is a solved puzzle, and watching a solved sweep is dead air. |
| 12 | Bastion (H7) | 7 | 8 | 6 | 7 | 7 | **35** | 6 | Competent graph tower defense with no wheel and no evasion: generic. Corp adaptation can read as punishment for building well. |

### Notes per pitch (calibration)

- **1 Ring Siege.**
  - Strengths: the core verb transfers. Rotating rings with an exact forecast is the readable kind of determinism (compare Into the Breach's telegraphs). Defense layers on rings are a strong image.
  - Problems:
    - Ring speed and phase are continuous-feeling knobs. With an exact forecast the player nudges until everything is green. That is Opus Magnum without the authorship, and solving it is not deciding.
    - Consequences are weak: what does a broken slice on ring 2 cost the campaign? Territory loss (GDD 3.3) disappears from the fight.
- **2 Pursuit.**
  - Strengths: the best what / why / when in the set. FTL's rebel fleet is the reference for always-on-screen, Heat-driven pressure, and the cobalt fill passes the no-words test outright.
  - Problems:
    - It only specifies the pressure. The raid itself ("any defense model") is undefined, and the ambush is hands-on wheel combat, which breaks the hands-off raid rule.
    - FTL works because a sector is about 20 minutes of jumps. Here the clock ticks once per 15-minute netrun over about 8 runs, which is a much coarser clock. Pacing risk is high.
- **3 Ring Pursuit.**
  - Strengths: the best structural idea in the set. The campaign route writes the siege's threat queue, so the map decision has a delayed, visible cost.
  - Problems: legibility across time. Players must remember which swallowed node produced which spoke threat. Slay the Spire's map works because the payoff is the next node, not four runs later.
- **4 Mirror Netrun.**
  - Strengths: a good premise mirror.
  - Problems: an auto-played wheel fight hides the reason it went the way it did. The player never sees the alignment decisions, because there are none. Compare Dungeon Keeper or Legend of Keepers: those work because fights are stat checks that read at a glance.
- **5 Deck Fortress.**
  - Strengths: the offense-now versus safety-later tension is real. Compare Inscryption's sacrifice economy and Monster Train's floor defense from one deck.
  - Problems: it collides with progression. The deck dies with the operative and the roster has several operatives. "Stack the deck" is fiddly admin, not a decision.
- **6 The Offer.**
  - Strengths: thematically sharp. A subscription-bricking corp extorting you fits the fiction. Compare Frostpunk's demands and Banner Saga's trades.
  - Problems: as a raid it is a dialog box.
- **7 Counterstrike.**
  - Strengths: the best incentive design in the set ("defending perfectly is not always right").
  - Problems: the worst readability. Even Into the Breach shows one board.
- **8 Honeypot Farm.**
  - Strengths: Balatro and Hades heat-style greed dials work because the player picks the risk. That gives a strong why / when.
  - Problems: it inverts the pillar "Heat is the threat", and the existing inverted clean-defense Heat rule (GDD 7.2) already pushes this way.
- **9 Signal War.**
  - Problems: Go is no-words in principle, but nobody reads territory at a glance without years of play, and digital influence games (Plague Inc. spread, Civ culture borders) need tooltips to predict flips.
- **10 The Rack.**
  - Strengths: Backpack Battles and Super Auto Pets prove the format reads well and plays deep.
  - Problems: they work over about 15–20 rounds per run. Five times a campaign is not enough reps. Fit is the lowest in the set: no network, no wheel, no evasion.
- **11 Ghost Protocol.**
  - Strengths: the cleanest fiction-mechanic join ("Heat is how visible you are"). Invisible Inc.'s alarm level and vision cones and Mark of the Ninja's sight lines prove that telegraphed detection reads without words.
  - Problems:
    - Depth is low as pitched: three levers, and found means lost.
    - Invisible Inc. gets depth because the player acts during the sweep. Here they cannot.
- **12 Bastion.**
  - Strengths: the GDD's exact projection gives the predictability. The measured result (planning the leg beats one-raid play) is real depth. Footholds and survivors rejoining give persistence.
  - Problems:
    - It reads as Bad North or Thronefall: competent and placeable anywhere. Nothing in it is REBEL_CELL.
    - Node jobs and adaptation add rules text that hurts the no-words test.

## 2. Top 3

### Top 1: Pursuit (2)

**What must be true for 9+ on every axis:**
- **WWW:** the front shows its next-netrun position as a ghost fill before the Site pick. The Heat-to-speed link is drawn on the Heat meter itself.
- **Pred:** the advance is deterministic and fully previewed: "this route, the front ends here."
- **NoW:** fill, ghost fill and swallowed-node state read without labels.
- **Dep:** every pick offers at least two real options (push for value, detour to cover tracks, sacrifice a node to slow the front), each with a visible cost. The minimum winning path must not dominate.
- **Con:** swallowed nodes reuse the TAKEN state with a Reclaim path. The HQ siege is a defined hands-off model, Bastion or a ring siege, not "any".
- **Frequency:** catch events land at about 3–5 per campaign by tuning, not by luck.

**Biggest design risk:** clock granularity. The front moves once per 15-minute netrun over about 8 runs, so there are only about 8 clock ticks per campaign. Either it is too slow to feel or one bad tick is fatal. FTL has about 50 or more jumps over which to spread the pressure.

**Cheapest experiment:** extend the existing Bastion campaign planner. Add a front that advances N nodes per netrun as a function of Heat, over 50 seeded City Grids, and measure:
- the distribution of catch events per campaign (target 3–5, low variance);
- the share of seeds where the minimum path is optimal (kill the pitch if it is above 70 %);
- the number of distinct near-optimal routes per seed (target at least 3).

Running the planner needs no new art. Then make a one-frame City Grid mockup with fill and ghost fill for the no-words test.

### Top 2: Ghost Protocol (11)

**What must be true for 9+:**
- **Dep:**
  - The levers must carry real costs. A node gone dark gives no bonus next netrun. Decoys cost Schematics and each one draws a specific sweep. Ghost-node capacity is small.
  - Sweeps need corp-specific patterns that interact: two beams, one reroutes on a decoy.
  - The best placement must change with the network, not be "hide the two biggest assets".
- **Con:** found must be graded, not binary. Found assets go DOWN, an operative found starts an ambush the next netrun, and an evaded sweep lowers Heat. Each loss is stamped on the node.
- **Pred:** the playout must have its own beat, a near miss that the forecast showed but the player feels. Mark of the Ninja's sound rings show how.

**Biggest design risk:** solved-puzzle dead air. Full information, no input during play and binary results give one correct answer and a 30-second replay of it. Depth must come from scarcity of hiding resources, not from reading the sweep.

**Cheapest experiment:** a headless enumerator on a 12-node network with a 3-sweep pattern. Enumerate every legal hide, decoy and go-dark allocation, then measure:
- the regret spread between the best allocation and the median allocation;
- the count of allocations within 5 % of the best.

If the best allocation is unique and obvious (for example, it always matches a greedy rule) on most seeds, kill the pitch or add levers. In parallel, run a 3-frame paper mockup of the sweep (before, mid, near miss) for the no-words test.

### Top 3: Ring Pursuit (3)

**What must be true for 9+:**
- **NoW:** the siege is capped at 3 rings and 4 spokes.
- **WWW and Con:** each spoke's threat wears the icon of the node it was swallowed from, and that node is highlighted on the map when the threat appears. The route-to-siege causality is shown at both ends.
- **Pred:** the forecast lists each contact as "spoke, ring, tick, outcome".
- **Dep:** ring speed and phase are discrete and costly, for example a few preset speeds bought with Schematics. Exact tuning must not be free, or it becomes search.
- **Con:** a broken ring maps back to network nodes losing integrity, so the siege result lands on the campaign.

**Biggest design risk:** scope plus search. It needs two new systems. The siege's exact forecast invites slider-until-green play, so the depth must come from the route (which threats you let the front collect), not from tuning the rings.

**Cheapest experiment:** a headless ring-siege sim using the locked resolution math (GDD 2.3). For random threat queues, enumerate the stockings, then measure:
- the fraction of stockings that hold;
- how far a naive stocking falls from the best one.

Kill the pitch if the naive stocking is within 5 % of the best (no depth) or if fewer than 1 % of stockings hold (pure puzzle). Then rerun with two different collected queues from different routes. If the best stocking does not change, the merge's core claim (the route shapes the siege) is false.

## 3. Merges and refinements

1. **Manhunt = Pursuit (2) + Ghost Protocol (11). My recommended direction.**
   - The front is where the corp is looking, and Heat is visibility in both halves.
   - When the front reaches your nodes at a threshold, the raid is a sweep across what it touches. You hide, decoy and go dark, and the result is graded (Ghost Protocol).
   - The two fix each other: Pursuit lacks a defined raid, and Ghost lacks depth, which the route choice supplies. Ghost also gives the front's arrival a hands-off, short, readable playout.
   - It is the closest fit to the premise ("hackers evading a corporation while hacking toward its core").
2. **Bastion (12) + The Offer (6).**
   - The demand appears after setup, priced against Bastion's exact projection: "refuse: Vault DOWN, home -8 · pay: 20 Schematics."
   - Bastion's preview makes the Offer a real decision. The Offer gives Bastion a third outcome and a fiction beat.
   - Cheapest valuable add in the set. Icon-price the offers to pass the no-words test.
3. **Honeypot (8) folded into Ghost or Bastion as the decoy reward.** A decoy that is found traps the sweep or threat and pays salvage. Greed then lives inside a pressure model instead of replacing it. Do not ship the lure dial on its own.
4. **Ring Siege (1) only as the home-server last stand.** Keep the graph or sweep raid for the network. When a threat reaches HQ, the home server's defense is a single-ring, hands-off wheel: one ring, stocked from the Armory. This puts the core verb at the dramatic moment without a second puzzle system every raid. It also fits the PURGE raid at Heat 100.
5. **Counterstrike's incentive (7) without its split screen.** After a raid, surviving pieces can be spent on a counter-hack that lowers Heat or opens a cross-link. This is a post-raid choice, not a parallel playout.
6. **Drop:** Deck Fortress (5), Signal War (9) and The Rack (10). Their failure modes are structural, not tuning problems.

## 4. Barriers (every item is a designer decision)

### Pursuit / Manhunt
- **[DESIGNER] GDD 4.3 and 4.4:** raids fire once at fixed Heat thresholds. A continuous front replaces or reframes this (the pitch also cites D27 and D28).
- **[DESIGNER] Brief: 3–5 raids per campaign.** A front makes pressure continuous. Do catch events count as raids?
- **[DESIGNER] Hands-off raids versus the ambush.** The ambush is a hands-on wheel fight. Either call it a netrun complication, not a raid, or make it hands-off.
- **[DESIGNER] GDD 3.3:** is a swallowed node TAKEN, or a new state? A new state adds a rules word.
- **[DESIGNER] GDD 7.1:** the about 4-minute setup is spread across the campaign instead of a raid screen.
- **[DESIGNER] For Manhunt:** pillar 4 says raids are "deterministic graph auto-battles", but a sweep is not a battle.

### Ghost Protocol
- **[DESIGNER] Pillar 4:** raids are graph auto-battles. Stealth replaces combat.
- **[DESIGNER] GDD 7.2 inverted Heat:** a clean defense gains +5 Heat, but "Heat is visibility" implies an evaded sweep should lower Heat. These directly contradict each other.
- **[DESIGNER] GDD 3.2 and 3.3:** integrity, DOWN and TAKEN become found / lost. Firewall Relay turrets and integrity values lose meaning.
- **[DESIGNER] GDD 7.3 Armory:** defense assets become hide, decoy and dark tools. Locked persistence rules need re-reading.
- **[DESIGNER] Loss condition (GDD 1.3, 3.2):** home integrity reaching 0 needs a sweep equivalent, for example HQ found twice.

### Ring Pursuit
- **[DESIGNER] Pillar 4:** "Wheel mechanics exist only in combat." This is the single biggest barrier, and it applies to Ring Siege too.
- **[DESIGNER] GDD 7.1 and 7.2:** the graph raid on the City Grid is replaced by a wheel fight. D26 pacing becomes ticks.
- **[DESIGNER] GDD 2.1 locked anatomy reused outside combat:** confirm that "locked" covers raid wheels, and that concentric rings beyond the single inner ring of 6.4 are allowed.
- **[DESIGNER] Node integrity (3.2) to ring mapping:** how siege damage maps back to network nodes.
- **[DESIGNER]** All of Pursuit's barriers above.
