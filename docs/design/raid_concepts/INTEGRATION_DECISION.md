# Raid integration decision (2026-10-25)

**Designer direction (2026-10-25):** lean toward Solace option C, with raid lines that start at the corp HQ, end at
our HQ and take their own path through any network. "Up to you which paths the corps can use; keep the critic score
high. Run a version of each option and decide which plays best, then go ahead with the plan."

## Chosen design: the "Infected Tide" (H3)

C's board and paths, plus D's deck infection. Simulated in tools/raid_concepts/sweep_g1.py (variant H3).

| Part | Rule | Why |
|---|---|---|
| Board | The real corp network (the Solace graph as shipped; no content regroup) | Designer's path rule; fits networks of any shape |
| Corp paths | **P-target:** the sealed candidates are paths from the Genome Core to HOME through the most owned Sites | G1's strongest lever: locked-at-plan 0.61 vs 0.79 (any path), relevance 0.76, almost never EVADED |
| Raid sequence | L14 sweep: known beams, sealed A, response, sealed B picked **after** the response by a readable corp lean, hunter on a street | G2: the lean is a balance lever more than a decision (it flips 5 %) |
| Infection | Each lost Site adds an INFECTED card tied to it (dead draw in raids; costs bank in netruns). It spreads +1 when 2 or more Sites were lost since the last raid. CITY LOST when INFECTED cards outnumber healthy ones | D's deckbuilder fit, without D's flat-tax snowball |
| The map's front | Derived: the infected Sites and their TAKEN neighbors, drawn as the Bloom | C's readability; no separate timer (G1: never decisive) |
| Doses | A DOSE every 2nd netrun, spent automatically (≤ 2 per DECAY); one INFECTED card per raid hand can be discarded for +2 Heat | Softens the death spiral |
| Early threat | The known beam routes to HOME 60 % in raids 1–3, then 10 % | HOME hit rate 0.17–0.19 |
| SACRIFICE | At most once per 2 raids; the lost Site adds INFECTED | Was a crutch (27 %) |
| Win | 3 exploits held, plus a PURGE (a raid closed with ≤ 1 INFECTED card while holding them, or 2 DOSE spent at one DECAY) | Reachable: win 0.30–0.35 |

## Measured (600 campaigns per cell)

| | Skilled loss | Careless loss | Win | Locked at plan | Response decides | HOME hit |
|---|---|---|---|---|---|---|
| H3, 12 netruns | 0.00 | 0.71 | 0.30 | 0.47 | 0.31 | 0.17 |
| H3, 24 netruns | 0.00 | 0.97 | 0.35 | 0.41 | 0.38 | 0.19 |
| C Bloom Tide (G1) | 0.03 / 0.42 | 0.65 / 0.91 | 0.36 / 0.00 | 0.62 / 0.73 | 0.21 / 0.19 | 0.44 / 0.60 |
| D Carrier Deck (G1) | 0.01 / 0.07 | 0.77 / 1.00 | 0.31 | 0.67 / 0.74 | 0.16 / 0.18 | 0.49 / 0.62 |

**Blind critics (rule sheets plus metrics, no visuals):**
- G1: D 35, C 33, B 32, A 30.
- G2: the hybrid H 36 (S 7, Fit 8) vs D 34.
- These are not comparable with the lab's visual score of 39.

**Open misses (they need rule changes, not tuning):**
- **The skilled player never loses at 12 netruns.** HOME takes at most 1 pip per raid, and the player can always
  patch it.
- **Careless loss at 24 netruns is 0.97:** a slow Heat drain from three known beams past Heat 75.
- **Response decides is 0.31–0.38.** On this graph it trades directly against the HOME hit rate.
- **Note:** the real game's HOME integrity is 50 with `raid_home_hit_damage`, not 3 pips. These misses must be
  re-measured in the Phase 1 oracle against the real numbers before anything else is tuned.

## Rulings needed from the designer (defaults in brackets)

| # | Ruling | Default |
|---|---|---|
| R-A | Adopt the Infected Tide as the Solace raid. This replaces GDD §7.1–7.2 for Solace and keeps raid_resolver.gd for the other corps until they are ported (INTEGRATION_PLAN Q1) | yes |
| R-B | The corp hunts you: its sealed candidates are the paths through the most owned Sites (P-target), and corp beams may use locked links (S-M11) | yes |
| R-C | The defense deck is campaign-wide (the Armory as cards; stationed operatives add their class card), not the operative's run deck (plan Q2) | yes |
| R-D | Lost Sites add INFECTED cards: dead in raid hands, and −2 bank when drawn in a netrun. They are not added to netrun combat decks yet (plan Q4 deferred) | yes |
| R-E | CITY LOST (INFECTED cards outnumber healthy ones) is a campaign loss with its own verdict word, separate from BREACHED (S-M8) | yes |
| R-F | The Solace win needs a PURGE as well as 3 exploits held | yes |
| R-G | Drop Solace's step-based infection and the separate tide timer. The Bloom front on the map is drawn from the INFECTED Sites (supersedes S-M2–S-M4) | yes |
| R-H | DECAY: a Site still DOWN at the next raid goes TAKEN (GDD §3.3) | yes |

## Next (the INTEGRATION_PLAN phases, rescoped)

| Phase | Work | Status |
|---|---|---|
| 0 | Log the rulings in DECISIONS.md once approved. Merge this branch's tools and docs into main (one MAILBOX conflict) when the designer says so | Waiting on the designer |
| 1 | The graph oracle, done in G1–G3. Remaining: re-measure with the real HOME 50 / damage numbers and the real Solace values, then write the golden for parity | Next |
| 2+ | Core port, Solace wiring, the vertical-slice UI | Per the plan |

## Designer rulings (2026-10-25)

R-A, R-B, R-C, R-E, R-G and R-H are approved as written. Two are revised:
- **R-D:** INFECTED cards move the Solace netrun virus front one step closer each (no "bank" cost; netruns use Cycles,
  and the street Bloom already exists).
- **R-F:** there is no purge. The win is the existing one: breach the Genome Core and release the antidote code. Doses
  are stolen antidote samples that cure a district. The INFECTED count at the breach scales the final Genome Core
  netrun's strength.

The rulings are logged in docs/DECISIONS.md (2026-10-25).
