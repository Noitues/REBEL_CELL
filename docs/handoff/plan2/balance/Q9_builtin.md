# Q9: why the builtin bot's campaign win fell from 50 % to 25-35 %

2026-10-20, branch `q9-builtin`, base main @ 976063b7. Policy: **builtin** (CombatBot), ICE 0, Solace, breaker, `--fast`,
20 seeds (1000..1019) per point unless noted. Raw reports: `D:/rc_tmp/q9/runs/pt_<sha>.md|json` (not committed).
With n = 20 one standard error is about 10 points, so only the 50 -> 30 step below is a signal.

## Bisect
| commit | what | win % | runs | deaths |
|---|---|---|---|---|
| e2e13918 | BASELINE_e2e13918 tooling (reproduces the committed 50 %) | 50 | 38.6 | 10.5 |
| 5929377f | last point before plan 2 W0 | 50 | 38.6 | 10.5 |
| a5f2bff0 | W0 N2 (tier tables), branched before N1 | 50 | 38.6 | 10.5 |
| **324c7751** | **W0 N1 (amount modes; enemy FLAT heal / block / shield x tier factor)** | **30** | 47.8 | 7.2 |
| 4bd16381 | N1 + follow-ups | 30 | 47.8 | 7.2 |
| 6fb2e8ed | N2 merged on top of N1 | 30 | 47.8 | 7.2 |
| a2a36ab3 | N1b (enemy DEAL_DAMAGE effects scale by tier) | 15 | 47.6 | 23.0 |
| 6856be0b | N9 | 30 | 48.2 | 16.9 |
| 6b3ec4f7 | N12 | 30 | 48.2 | 16.9 |
| 293dadf5 | WH-11 Bloom | 30 | 48.2 | 16.9 |
| 17189869 | Solace v2 slices 1-8 | 30 | 50.0 | 17.4 |
| 9f9f90c0 | w1-close | 30 | 48.2 | 16.9 |
| 163c5411 | Halcyon v2 | 30 | 50.0 | 17.4 |
| eea48259 | w2-int merge | 25 | 50.7 | 15.9 |
| 976063b7 | main head | 35 | 48.1 | 13.2 |

(Rows with identical figures are commits that change nothing this sim touches.) The drop is a single step at **324c7751
(N1)**. Run graph v2, EV-01 events, Halcyon, the route retire and CITY-A2 are all flat (30 % before and after). N1b
(a2a36ab3) adds a second, real dip (15 %, deaths 23); it recovers to 30 % by 6856be0b. That is more likely n = 20 noise after
a chaotic trajectory change than a stable effect; not pursued.

## Cause
N1 made an enemy's FLAT heal / block / shield effects multiply by the tier damage factor (`EffectInterpreter.effect_amount`,
DECISIONS "2026-10-18 Plan 2 W0 N1"). The Genome Core's (`renewal_engine`) Hub heal Auto-Renew is 10 at T1 and 22 at T4. The
breach is T4, so the boss now heals more than twice as much per turn.

Evidence (probe over seeds 1000 / 1002 / 1004 / 1006, `CampaignSimulator` log, builtin):
| | 5929377f | 324c7751 |
|---|---|---|
| fights that hit the 60-turn cap ("stuck") | 18, all vs renewal_engine | 161, all vs renewal_engine |
| boss HP left at the cap (max 1475, mean) | 279 | 852 |
| campaign outcome (4 seeds) | 2 WON, 2 NONE | 0 WON, 4 NONE |
| deaths | 35 | 20 |

Every stuck fight in both builds is the boss. Before N1 the bot usually got the boss close to dead inside 60 turns and won on a
retry; after N1 it cannot out-damage the heal, so it loops breach -> 60-turn stalemate -> breach until the 60-run cap. That also
explains the lower death count and the higher run count: the failure moved from dying to stalling. The normals, elites and
mini-bosses are not the cause (died-vs mix unchanged).

## Verdict
**A real, designer-ruled gameplay change (plan 2 R2 / R5), not a sim or bot gap, and not a bug.** The sim handles REST,
WORKSHOP, CACHE, events and Halcyon as before; nothing in `scripts/core/campaign_simulator.gd` or `tools/` regressed. The builtin
bot is a floor policy that cannot beat the post-N1 Genome Core; the reference policy (lookahead 2) does (boss ~52 % in
SOLACE_BAL_r1). No code changed in this branch.

## Open questions for the designer (no fix made; each is a balance call)
- Q: Re-baseline the builtin floor in `docs/balance/TARGETS.md` ("campaign win not below 50 %, BASELINE_e2e13918") to the
  post-N1 level (about 30 %, 20 seeds), since the 50 % pre-dates N1 and the boss is now tuned on the reference policy; or
- Q: keep 50 % and ease the boss for a weak player (for example Auto-Renew not scaled past T3, or a lower scale on
  `renewal_engine`'s heal). Note the boss is 360 HP x the legacy T4 HP scale 4.096 = 1475 in the campaign (BAL-05's 400 is
  1638 at head); a weak bot loses on sustain, not on raw HP.
