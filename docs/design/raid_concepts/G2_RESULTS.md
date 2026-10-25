# G2 results: the hybrid "Infected Tide" (H) against C-target and D-lattice

Status: lab measurement for the designer (brief `docs/handoff/raid_integration/G2_SIM.md`, 2026-10-25). Nothing in
`scripts/`, `content/`, `scenes/`, GDD.md or DECISIONS.md changed.
Oracle: `tools/raid_concepts/sweep_g1.py` (new variants `H`, `H-noB`, `H-nospread`, `H-brief`) + `g1_geo.py` (one new
optional argument, default unchanged) + `g2_tune.py` (grid helper over the `H_*` overrides). `--check` passes for all
15 variants; C-target, D-lattice, B-wards and A-all reproduce G1's records byte for byte (48 campaigns compared against
the HEAD 0f298f27 module). Raw summaries: `D:/rc_tmp/raid_design_lab/g2/sweep_g2_n12.json`, `sweep_g2_n24.json`
(extras: `h_k0_n12.json`, `h_k0_n24.json`, `h_esc_n24.json`, tuning grids in `g2/tune/`).

**Runtime:** 130 s (12 netruns) + 236 s (24 netruns) for 6 variants x 3 claim policies x 200 campaigns x 2 raid players
(14,400 campaigns, 5 workers); 112 s for the three extra H rows; about 15 min of tuning grids at 30 campaigns per policy.

---

## 1. Table (all three claim policies pooled, 600 campaigns per cell; raid metrics from the skilled player)

G = skilled (greedy) player, N = careless (naive) player. Targets: G loss <= 0.15 and N loss >= 0.50 at both lengths,
locked <= 0.5, resp. decides >= 0.4.

| Variant | Len | G loss | (breach / city) | N loss | Win | Purge | Locked | Live after resp. | Resp. decides | B flip | INFECTED / camp. | Front | HOME hit | Relevance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H** | 12 | **0.00** | 0 / 0 | **0.90** | 0.20 | 0.30 | **0.43** | 0.09 | 0.35 | 0.04 | 5.9 | 0.9 | 0.07 | 0.81 |
| **H** | 24 | **0.13** | 0.01 / 0.11 | **1.00** | 0.11 | 0.33 | **0.48** | 0.06 | **0.45** | 0.05 | 18.0 | 2.8 | 0.13 | 0.84 |
| H-noB | 12 | 0.00 | 0 / 0 | 0.89 | 0.18 | 0.29 | 0.38 | 0.36 | 0.37 | – | 6.2 | 1.0 | 0.18 | 0.81 |
| H-noB | 24 | 0.30 | 0.05 / 0.24 | 1.00 | 0.09 | 0.31 | 0.40 | 0.34 | 0.43 | – | 17.8 | 2.9 | 0.26 | 0.84 |
| H-nospread | 12 | 0.00 | 0 / 0 | 0.88 | 0.24 | 0.38 | 0.42 | 0.08 | 0.35 | 0.05 | 5.9 | 0.5 | 0.06 | 0.81 |
| H-nospread | 24 | 0.00 | 0 / 0 | 1.00 | 0.22 | 0.48 | 0.43 | 0.06 | 0.42 | 0.05 | 17.5 | 1.4 | 0.13 | 0.85 |
| H-brief (brief's literal numbers) | 12 | 0.11 | 0.09 / 0.02 | 0.98 | 0.07 | 0.10 | 0.93 | 0.05 | 0.26 | 0.13 | 6.3 | 1.5 | 0.43 | 0.76 |
| H-brief | 24 | 0.93 | 0.24 / 0.69 | 1.00 | 0.00 | 0.10 | 0.94 | 0.04 | 0.26 | 0.12 | 13.3 | 2.4 | 0.51 | 0.78 |
| H, known beams never routes | 12 | 0.00 | 0 / 0 | 0.89 | 0.18 | 0.29 | 0.38 | 0.08 | 0.39 | 0.04 | – | – | 0.01 | – |
| H, known beams never routes | 24 | 0.11 | 0 / 0.11 | 1.00 | 0.10 | 0.32 | 0.39 | 0.07 | 0.52 | 0.05 | – | – | 0.01 | – |
| C-target (G1 ref.) | 12 | 0.03 | 0.03 / 0 | 0.65 | 0.36 | – | 0.62 | 0.24 | 0.21 | – | 5.7 wounds | – | 0.44 | 0.76 |
| C-target | 24 | 0.42 | 0.42 / 0 | 0.91 | 0.00 | – | 0.73 | 0.17 | 0.19 | – | 18.1 wounds | – | 0.60 | 0.71 |
| D-lattice (G1 ref.) | 12 | 0.01 | 0.01 / 0 | 0.77 | 0.31 | – | 0.67 | 0.25 | 0.16 | – | 3.0 | – | 0.49 | 0.70 |
| D-lattice | 24 | 0.07 | 0.06 / 0.01 | 1.00 | 0.31 | – | 0.74 | 0.22 | 0.18 | – | 9.7 | – | 0.62 | 0.76 |

Column notes:
- **Win** for H = 3 Exploits held at the end **and** a PURGE during the campaign; **Purge** = campaigns with at least
  one raid survived with 0 INFECTED cards while holding the 3 Exploits. Hold-3 alone for H: 0.30 (12) / 0.18 (24).
  C and D: win = hold 3 Exploits (G1 proxy).
- **B flip** = share of raids where the corp's post-response B differs from the lean shown at REVEAL A (non-HOLD
  responses only: 0.08 for H, 0.22–0.25 for H-brief).
- **Locked / Live after** for the post-response B variants: B is a function of the board, so the outcome set is
  A x hunter (6) instead of A x B x hunter (12), and live-after-response varies only the hunter. That makes "live after"
  structurally low for H (0.06–0.09 against 0.34–0.36 for H-noB); it is not a like-for-like column.
- **Front** = mean visible front size at the start of a raid (Sites tied to INFECTED cards plus their TAKEN neighbours).
- **Forecast rows:** 97–100 % of H forecast rows show a non-zero INFECTED change (mean 2.5 at 12 runs, 2.9 at 24),
  counting Sites lost now and Sites left DOWN that are lost at the next DECAY unless repaired. The planner scores it.
- Response mix, H 24 runs: HOLD 38 %, SACRIFICE 27 %, DEPLOY 23 %, JAM 5 %, REDEPLOY 4 %, JAM-the-pick 2 %.
- Per claim policy, H 24 runs (G loss / win): greedy claims 0.16 / 0.03, keys first 0.22 / 0.29, random 0.00 / 0.00.
- **Escalation probe** (`H_ESCALATE=6:1`, one extra known beam from raid 6): identical to H. Heat is already over 50 by
  then, so the extra beam fires anyway. No escalation was added: the careless player already loses 88–100 %.

**Verdict on the targets.** H (tuned) meets the skilled-loss, careless-loss and locked targets at both lengths, and
response_decides at 24 runs (0.45). It misses response_decides at 12 runs: **0.35 against 0.40** (0.39 with known beams
never routes). H as the brief literally wrote it (H-brief) fails badly: locked 0.93, and 93 % skilled loss at 24 runs.

---

## 2. Assumed numbers and rulings (G2 additions; everything else is G1_RESULTS section 2)

Kept from G1: the Solace graph, P-target (3 sealed candidates = the P-all paths through the most live owned Sites, ties
by seeded rng), the street hunter, bank 10, Heat 44, HOME 3, the L14 8-card deck, ghost kit 2, a raid every 2 netruns,
income sum(value // 6), netrun draw 5 cards with each INFECTED drawn costing 2 bank, a build 3, repair value // 2,
the planner. No bloom-front timer (dropped as the brief says).

Tuned in G2 (H, H-noB, H-nospread; H-brief keeps the brief or G1 value shown in brackets):
| Number | H | Brief / G1 | Why |
|---|---|---|---|
| Corp's B rule | owned Sites before the first sentry of **any** type | before the first sentry **of the route's type** | The typed rule lets the corp see through types and dodge every block: under HOLD the B pick is always the unblocked route, so every A gives DAMAGED (locked 0.93) and 24-run loss 93 %. "Any" keeps the brief's readable rule (more of your Sites, sentries steer it) but the corp only sees that a card is there, so a mistyped card can bait it. |
| Known beam is a route to HOME | 10 % (else a street) | 50 % | A known route beam hits HOME before PLAN can answer; it was the main source of locked raids (DAMAGED in every outcome). 0 % also meets the targets (row above) but makes HOME almost unhittable (1 %). |
| Spread trigger | 2+ Sites lost since the last raid | 1+ Site | With 1, the spread fires almost every raid (a Site is lost nearly every raid on this graph): 24-run city lost 0.69–0.91 whatever the dose rate. |
| DOSE card | every 2nd netrun | every 3rd | Needed with the spread at 24 runs (every 3rd: city lost 0.67 even with a 2-Site trigger). |
| CLEAN an INFECTED card | 2 bank | 4 | Small effect alone (grid: a few points); kept low so the purge is reachable. |
| PATCH HOME | 8 bank, +1 pip, max 3 | 8 | Price grid 4–8 moved breach by at most 0.1; with the known route at 10 % breach is 0.01, so PATCH stays at 8. |
| Escalating raid tiers | none | (optional) | Not needed: careless loss 0.88–1.00. Hook: `H_ESCALATE="N:K"`. |

New H rules as simulated:
- A Site lost (DECAY of an unrepaired DOWN Site, or SACRIFICE) adds one INFECTED card tied to it. On this graph a raid
  never takes a Site directly (DECAY clears every DOWN Site first), so the infection always comes from DOWN Sites
  left unrepaired, or a sacrifice.
- One DOSE per DECAY at most. The skilled player spends it when the spread fires (blocks it), otherwise to remove 1
  INFECTED card. The careless player never spends.
- The corp's lean at REVEAL A uses the board before the response (ties: the first candidate in display order). After
  the response the same rule picks B; a tie keeps the lean.
- JAM now has two uses: stop the hunter, or scramble the corp's pick (B becomes the other route). A move or a new
  sentry can also flip the pick.
- CITY LOST when INFECTED > healthy cards (DOSE cards count as healthy). The spread card is tied to the most recently
  lost Site (lowest id on ties).
- PURGE: a raid closed with 0 INFECTED cards in the deck while the 3 Exploits are live. Win = a purge, then 3 Exploits
  held at the end.
- Planner: G1 value + D's -2 per INFECTED card, -2 per DOWN Site (it becomes INFECTED unless repaired), and the
  pending spread (-3 if a DOSE card can block it, else -7). INFECTED card ids are now monotonic (G1's `w%d` ids can
  collide after 10 wounds; the reference variants keep the old ids so they reproduce G1).

---

## 3. Rule sheet (player-facing, as simulated; for a blind critic)

- Your Cell holds Sites in a city network. The enemy HQ is at the far end; your HQ (HOME, 3 integrity) at the near end.
- Each run you claim one Site linked to your territory; a lost Site can be claimed again. Every 2 runs, the corp raids.
- **Infection is in your defense deck.** Every Site you lose adds an INFECTED card tied to it. INFECTED cards are dead
  draws in raids, and each one you draw on a run costs 2 bank. If they ever outnumber your healthy cards, the city is lost.
- **Spread:** if you lost 2 or more Sites since the last raid, one more INFECTED card is added when the raid starts.
- **DOSE cards:** one every 2nd run. When a raid starts, spend one to block the spread or remove an INFECTED card.
- The map shows the infected front: the Sites your INFECTED cards are tied to, and lost Sites next to them.
- **A raid.** Sites left DOWN since the last raid are lost. You draw a hand (drones, netrunners, enforcers; some can
  SHIFT, one can JAM).
- Beams travel from the enemy HQ. You see the known beam (usually a cross street, sometimes a route to HOME), and the 3
  routes the corp may fire: the routes through the most of your Sites. It fires two of them, each with its own type.
- PLAN: place up to 2 cards on your Sites. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits each of your Sites once per raid (OK -> DOWN, DOWN -> lost) and, at the end of a route, HOME
  (at most once per raid).
- The first route is revealed, with the corp's lean for the second: "next: route X". The corp takes the route with more
  of your Sites before the first card it can see. It sees your cards, but not their types. A tie keeps the lean.
- Then pick one RESPONSE: hold, move a card (SHIFT), add a card, JAM (stop the hunter, or scramble the corp's second
  pick onto the other route), or SACRIFICE a Site (it is lost now; HOME is safe this raid).
- Moving or adding a card can change the corp's second pick. Then both routes fire.
- Last, a hunter sweeps one of two cross streets (shown in advance) that never reach HOME.
- Each forecast row shows the result and the INFECTED cards it would add (Sites lost now, plus Sites left DOWN).
- Between raids: repair a DOWN Site (half its value), build a card (3) or clean an INFECTED card (2), patch HOME (8).
- You lose if HOME falls or the infection overwhelms your deck.
- You win by holding all three key Sites and surviving a raid with a clean deck (no INFECTED card) while holding them.

---

## 4. My read (separate from the sheet)

**H works once three of the brief's numbers move; as literally written it does not.** H-brief, with the typed B rule,
known routes at 50 %, a spread on any loss and a dose every 3rd run, has locked 0.93 and loses 93 % of skilled
24-run campaigns. Tuned H is the first G-series design inside the balance band at **both** lengths: skilled 0.00 /
0.13, careless 0.90 / 1.00. It also roughly halves locked (0.43–0.48, against 0.62–0.74 for C-target and D) and doubles
response_decides (0.35 / 0.45 against 0.16–0.21). The 12-run response_decides (0.35) is the one target it misses.

What carries it:
1. **Moving the HOME threat off the known beam.** The biggest single lever was not the B rule but the known route
   beam: at 50 % it settles the raid at DRAW. At 10 %, HOME is threatened by the sealed routes, which the response can
   answer.
2. **The deck infection is a real clock** (unlike C's tide). City-lost is the main way a skilled player loses at 24
   runs, and the spread is what makes it bite: H-nospread loses 0 % at 24 runs, against 13 % for H. Spread is worth
   keeping, but only with the 2-Site trigger: on this graph a Site is lost almost every raid, so "any loss" fires every
   time.
3. **The front grows the way it should:** 0.9 Sites at 12 runs, 2.8 at 24.

What the data says against it, honestly:
- **Fix 1 (B picked after the response) is not a decision lever.** The pick changes in 4–5 % of raids (8 % of
  non-HOLD responses), and JAM-the-pick is used in 2 %. Its real effect is balance: the corp becomes predictable, so
  the skilled player defends better (24-run loss 0.13 against 0.30 for H-noB). response_decides barely moves (0.45 vs
  0.43). It also removes the B uncertainty, so live-after-response falls to the hunter alone (0.06). If the designer
  wants a second-route mind game, the lean must be less informative, not more.
- **SACRIFICE dominates the response** (27 % of raids at 24 runs). With the infection as the cost, "lose a Site, save
  HOME" is the default skilled answer, and HOME is hit in only 7–13 % of raids. PATCH HOME is almost unused. This is
  the merge working (Sites are what you pay), but a critic may read it as one obvious move.
- **The win is hard:** the PURGE needs a clean deck, so wins are 0.20 / 0.11 (keys-first claims 0.49 / 0.29). If
  the PURGE is meant to be the goal, CLEAN or the dose may need a further push. If not, report Hold-3 instead.
- The between choice is narrower (entropy 1.7–1.8 against 2.3–2.5): CLEAN at 2 is almost always right.

**Recommendation:** take tuned H to the blind critic with the sheet above. Changes to log for the designer (as open
questions, not applied): the corp sees sentries, not their types; known beams are mostly streets; the spread needs 2
lost Sites; a DOSE every 2nd run; CLEAN 2. Next oracle round if wanted: a less informative lean (shown only after the
response, or as one of two), aimed at the 12-run response_decides gap.
