# G3 results: H3, the Infected Tide with the blind critic's four fixes

Status: lab measurement for the designer (G3 round of `docs/handoff/raid_integration/G2_SIM.md`, 2026-10-25; a blind
critic scored G2's H 36/50 (S 7, Fit 8) against D-lattice 34). Nothing in `scripts/`, `content/`, `scenes/`, GDD.md
or DECISIONS.md changed. No commits.
Oracle: `tools/raid_concepts/sweep_g1.py` (new variant `H3`; its numbers are the `H3` dict, overridable as `H3_<KEY>`),
`g1_geo.py` (one more optional argument, default unchanged), `g2_tune.py` (grid helper; `G2_TUNE_OUT` sets the folder).
`--check` passes for all 16 variants. **H is reproducible:** H, H-noB, H-nospread, H-brief, C-target and D-lattice match
the G2 commit a81f2fd4 byte for byte (72 campaigns compared). Raw: `D:/rc_tmp/raid_design_lab/g3/sweep_g3_n12.json`,
`sweep_g3_n24.json` (H, and H3 without DISCARD), `h3_discard_n12.json`, `h3_discard_n24.json` (H3 as shipped), grids in
`g3/tune*/`.

**Runtime:** 43 s + 97 s (H and H3-autodose, 12 / 24 netruns) + 21 s + 58 s (H3), 200 campaigns per claim policy x 3
policies x 2 players, 5 workers; about 25 min of tuning grids at 30–60 campaigns per policy.

---

## 1. Table (all claim policies pooled, 600 campaigns per cell)

G = skilled player, N = careless player.

| Variant | Len | G loss | N loss | Win | Purge | Locked | Resp. decides | HOME hit | SACRIFICE | B flip | INFECTED / camp. | Front |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H (G2) | 12 | 0.00 | 0.90 | 0.20 | 0.30 | 0.43 | 0.35 | 0.07 | 0.18 | 0.04 | 5.9 | 0.9 |
| H (G2) | 24 | 0.13 | 1.00 | 0.11 | 0.33 | 0.48 | 0.45 | 0.13 | 0.27 | 0.05 | 18.0 | 2.8 |
| **H3** | 12 | **0.00** | **0.71** | **0.30** | 0.49 | **0.47** | 0.31 | **0.17** | **0.11** | 0.05 | 5.7 | 0.3 |
| **H3** | 24 | **0.00** | 0.97 | **0.35** | 0.63 | **0.41** | 0.38 | **0.19** | **0.11** | 0.06 | 16.9 | 0.8 |
| H3 without DISCARD (auto-dose only) | 12 | 0.00 | 0.79 | 0.31 | 0.49 | 0.47 | 0.31 | 0.17 | 0.11 | 0.05 | 5.7 | 0.5 |
| H3 without DISCARD | 24 | 0.12 | 1.00 | 0.26 | 0.58 | 0.42 | 0.38 | 0.20 | 0.13 | 0.06 | 17.2 | 1.7 |

Notes:
- H3's losses are breaches for the careless player (0.71 / 0.97 all BREACHED). Its HOME is hit in 97 % of its raids,
  because it holds and never blocks the sealed routes.
- H3 discards an INFECTED card in 14 % of skilled raids at 12 netruns and 35 % at 24. DOSE cards spent per campaign:
  4.6 / 11.8. Per claim policy at 24 netruns, skilled win is 0.48 (greedy claims) / 0.56 (keys first) / 0.01 (random).
- Live after response: 0.07 / 0.06, the hunter alone, as in G2.

**Targets for H3:**

| Target | 12 netruns | 24 netruns |
|---|---|---|
| Win 0.3–0.5 | **met** (0.30) | **met** (0.35) |
| HOME hit 0.15–0.30 | **met** (0.17) | **met** (0.19) |
| SACRIFICE <= 15 % | **met** (0.11) | **met** (0.11) |
| Locked <= 0.5 | **met** (0.47) | **met** (0.41) |
| Skilled loss 5–15 % at 12 (<= 15 % at 24) | **missed** (0.00) | met (0.00) |
| Careless loss 0.55–0.80 | **met** (0.71) | **missed** (0.97) |
| Resp. decides >= 0.4 | **missed** (0.31) | **missed** (0.38) |

Five of the seven targets are met at 12 netruns and five at 24.

---

## 2. Assumed and tuned numbers (H3 = G2's tuned H plus these; G2 values in brackets)

| Number | H3 | Fix | Note |
|---|---|---|---|
| PURGE | a raid closed with <= 1 INFECTED card while the 3 Exploits are live, or 2 DOSE cards spent at that raid's DECAY (0 INFECTED) | 1 | Win = a PURGE, then 3 Exploits held at the end (unchanged). The Exploit condition stays on the PURGE; without it, raid 1 (0 INFECTED) would always count. |
| DOSE cards per DECAY | up to 2 (1) | 1 | Needed for the "2 DOSE in one raid" purge. Each one blocks the spread, or else removes 1 INFECTED. |
| Known beam route to HOME | 60 % in raids 1–3, then 10 % (10 % always) | 2 | 30 % for raids 1–2 gave a HOME hit rate of 0.08. Making the first 3 raids (all of a 12-run campaign's first half) threatening was needed to reach 0.15. |
| SACRIFICE | at most once per 2 raids (always) | 3 | A SACRIFICE already counted toward the spread trigger in G2: the sacrificed Site is a lost Site and adds an INFECTED card. |
| DOSE spending | automatic at DECAY, for every player (skilled only) | 4 | The critic's "doses to everyone" lever. Alone, careless loss is 0.79 / 1.00. |
| DISCARD | one INFECTED card in a raid hand may be discarded from the deck for +2 Heat (none) | 4 | Added for the win target at 24 netruns (0.26 -> 0.35) and careless 12 (0.79 -> 0.71). The skilled player discards when its value says so; the careless player always does. |
| Kept from G2 | B rule "any", spread on 2+ lost Sites, DOSE every 2nd netrun, CLEAN 2, PATCH 8, HOME 3 | | |

Tried and rejected (30–60 campaigns per policy, grids in `g3/tune*`):
- **HOME 4** or a **cheaper PATCH (4–6):** careless loss at 12 netruns falls to 0.02–0.47. At 24 it stays 0.81–0.99.
- **Starting at HOME 2:** no change to the skilled player. The careless player's 12-run loss stays 0.09–0.31.
- **More early or late known routes (up to 80 % for 4 raids; 20 % after):** HOME hit rises to 0.27–0.52, but locked
  rises to 0.56–0.76, response_decides falls to 0.16–0.29, and the skilled player still never loses at 12 netruns.
- **Escalation:** not used. The extra beams already fire once Heat passes 50.

---

## 3. Rule sheet (player-facing, as simulated; for a blind critic)

- Your Cell holds Sites in a city network. The enemy HQ is at the far end; your HQ (HOME, 3 integrity) at the near end.
- Each run you claim one Site linked to your territory; a lost Site can be claimed again. Every 2 runs, the corp raids.
- **Infection is in your defense deck.** Every Site you lose adds an INFECTED card tied to it. INFECTED cards are dead
  draws in raids, and each one you draw on a run costs 2 bank. If they ever outnumber your healthy cards, the city is lost.
- **Spread:** if you lost 2 or more Sites since the last raid, one more INFECTED card is added when the raid starts.
- **DOSE cards:** one every 2nd run. When a raid starts, up to 2 are used by themselves: each blocks the spread, or removes an INFECTED card.
- The map shows the infected front: the Sites your INFECTED cards are tied to, and lost Sites next to them.
- **A raid.** Sites left DOWN since the last raid are lost. You draw a hand (drones, netrunners, enforcers; some can
  SHIFT, one can JAM). You may throw one INFECTED card in your hand out of the deck for +2 Heat.
- Beams travel from the enemy HQ. You see the known beam (often a route to HOME in the first 3 raids, mostly a cross
  street after) and the 3 routes the corp may fire: those through the most of your Sites. Two fire, each with a type.
- PLAN: place up to 2 cards on your Sites. A card blocks a beam of its own type, and the beam stops there.
- An unblocked beam hits each of your Sites once per raid (OK -> DOWN, DOWN -> lost) and, at the end of a route, HOME
  (at most once per raid).
- The first route is revealed, with the corp's lean for the second. The corp takes the route with more of your Sites
  before the first card it can see. It sees your cards, but not their types. A tie keeps the lean.
- Then pick one RESPONSE: hold, move a card (SHIFT), add a card, JAM (stop the hunter, or scramble the corp's second
  pick onto the other route), or SACRIFICE a Site (it is lost now; HOME is safe this raid; once per 2 raids).
- Moving or adding a card can change the corp's second pick. Then both routes fire.
- Last, a hunter sweeps one of two cross streets (shown in advance) that never reach HOME.
- Each forecast row shows the result and the INFECTED cards it would add (Sites lost now, plus Sites left DOWN).
- Between raids: repair a DOWN Site (half its value), build a card (3) or clean an INFECTED card (2), patch HOME (8).
- A PURGE: survive a raid holding all three key Sites with at most 1 INFECTED card, or after 2 DOSE cards were used.
- You win by achieving a PURGE and holding all three key Sites at the end. You lose if HOME falls or the infection
  overwhelms your deck.

---

## 4. My read (separate from the sheet)

**H3 fixes what the critic asked for in the win, threat and SACRIFICE axes.** Wins are 0.30 / 0.35, against 0.20 /
0.11 for H. The HOME hit rate is 0.17 / 0.19, against 0.07 / 0.13. SACRIFICE falls from 18–27 % of raids to 11 %, and
locked stays under 0.5. The between step widens (entropy 1.9–2.0, against 1.7–1.8).

Three targets are out of reach with the levers given, and the data says why:
1. **The skilled player never loses a 12-run campaign** (0 in 600, in every grid cell I ran: HOME 2 to 4, PATCH 4 to 8,
   known routes up to 80 %). In 6 raids HOME takes at most one hit per raid, and the skilled player patches every
   hit. Losing at 12 runs needs a raid that can take 2 pips (for example a known route plus a sealed route both
   scoring), or a smaller bank. That is a rule change the critic did not list, so I flag it instead of adding it.
2. **Careless loss cannot sit in 0.55–0.80 at both lengths.** The careless player's HOME is hit in 97 % of raids, so
   its death is a slow drain on the bank: about 10–15 % per raid from raid 5 on, rising with Heat (3 known beams at
   75+). A cheap PATCH saves it at 12 runs and still loses it at 24. The infection levers (auto-dose, discard) work on
   city-lost, which is no longer what kills it. Hitting both needs a front-loaded hazard: an early raid that is
   deadlier, then a ceiling (Heat bands that stop adding beams, or a cheaper PATCH after raid 6).
3. **Response decides fell to 0.31 / 0.38** (H 0.35 / 0.45). The early known routes add the HOME hits but hit before
   the response, and the SACRIFICE cap removes the commonest deciding response. HOME hit rate and response_decides
   trade directly on this graph: every grid point with HOME hit >= 0.15 had response_decides <= 0.40.

**Recommendation:** take H3 to the blind critic. If the designer wants the skilled-12 and careless-24 targets, the
next round needs one of these rule changes (not tuning):
- a two-pip HOME hit for an unanswered known route;
- a Heat ceiling on extra beams.

response_decides needs a response that can stop a known beam, not only the sealed routes.
