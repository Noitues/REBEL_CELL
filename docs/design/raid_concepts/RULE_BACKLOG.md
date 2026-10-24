# Raid rules backlog: rule changes that raise the bar (tally)

These are rule changes the critics named as the way past the presentation ceiling. None are applied yet. Each needs a
designer call before a rules round. Estimated gains are the critics' own figures (±3 noise).

| # | Rule change | Axes and est. gain | Source (review) | Notes |
|---|---|---|---|---|
| R1 | **Two sealed beams per raid** (or a sealed beam plus a sealed hunter street), so more than one unknown is live at the reveal | S +2–3, D +1 | L11, L7 ("more simultaneous pressure") | The strongest suspense lever. The forecast table grows to 3×3 or uses ranges. |
| R2 | **The hunter's street is decided at the response step**, not by the first touch: one live unknown during the reveal | S +2, P −1 | L11 (optional 4th change) | Cheap to build; trades prediction for suspense. |
| R3 | **A response that trades a district for HOME** (e.g. SACRIFICE: a chosen owned cell absorbs the HOME hit and goes TAKEN) | D +1.5, S +1 | L11, L5 ("real trade-offs, not one obvious row") | Gives the post-reveal menu a costly option instead of a lookup. |
| R4 | **Heat charged in bands** (50 / 75 thresholds) instead of a flat −1 per point; **HOME pips priced well above Heat** | D +1, C +0.5 | L11 | Makes LOW/NORMAL/HOT a real trade. |
| R5 | **Each intensity buys something different** (HOT = an extra capture, LOW = a free sentry, NORMAL = a repair) | D +1, C +0.5 | L11, L5 ("LOW dominant"), L3 | LOW is chosen 36 of 40 times in every measurement since L3. |
| R6 | **Different costs for different responses** (SKIP/JAM/REDEPLOY/DEPLOY), and value for a leftover spoof at leg end | D +1, S +1 | L5, L7 | The spoof Heat cost is currently flat. |
| R7 | **Damage escalates if left** (done in L9: decay DOWN → TAKEN). Possible next step: **a TAKEN district becomes a corp staging point** that adds a beam origin | C +1, D +0.5 | L4, L9 | Builds on the decay that already exists. |
| R8 | **Look ahead over the whole leg:** warn when HOME first drops, with a projection two raids ahead | P +1, D +1 | L7, L5 | Partly done by `safe_next` (one raid ahead). |
| R9 | **Tie it to the deck:** sentries, kit or responses come from cards in the run deck | Fit +2, D +1 | L8, L9, L10, L11 ("the raid is a minigame beside the deckbuilder") | The largest Fit lever, and a GDD-level decision. |

**Ceiling statement (critics, L7–L11):** presentation alone tops out near 40–41. Past that needs R1–R3 (simultaneous
pressure and costly choices) and R9 (deck tie-in).

## Added from the L12 critic
| # | Rule change | Axes and est. gain | Source | Notes |
|---|---|---|---|---|
| R10 | **Captured districts change route geometry** (e.g. a district you hold forks or blocks a street) | D +1 | L12 | Choices that interact across raids. |
| R11 | **Exploits change which routes can be sealed** (holding an exploit removes one candidate, or reveals its type early) | D +1, S +0.5 | L12 | Gives the EXPLOIT key a raid role beyond score. |
| R12 | **The hunter's street depends on your placement** (the L8–L11 first-touch rule did this; L13 R2 replaces it with a sealed pair) | D +0.5 | L12 | Revisit if R2 measures badly. |

## Added from the L13 critic, plus the tally of what was applied
| # | Rule change | Axes and est. gain | Source | Notes |
|---|---|---|---|---|
| R13 | **Escalation adds options too** (each Heat band crossed grants one reserve sentry or spoof) | D +1.5, S +0.5 | L13 | Raid 3 stops being "pick the least-bad row". |
| R14 | **Don't print the best response** (show the per-route table, and sell the "best response" hint for Heat) | D +1, S +1, P −0.5 | L13, L12 | Partial information instead of a solved menu. |

**Applied so far:**
- R2, R3, R4 and R5 in L13. R5 was rebalanced as L13b: HOT ×0.5 income.
- R7's first step (decay) in L9.
- R8 in part (`safe_next`) in L11.

**Measured effect:** the response decides the outcome in 65% of raids (from 45%), and the critic's S rose from 4–5 to
6. The total did not move (34).

**Next calls need the designer:** R9 (deck tie-in), R1 (two sealed beams), R13 and R14.

## Added from the L15 critic
| # | Rule change | Axes and est. gain | Source | Notes |
|---|---|---|---|---|
| R15 | **One variable stays live through the response**: for example, the hunter cannot be fully pre-covered by 2 sentries plus the ghost, or the B pair is drawn so that one placement cannot cover both | S +2, D +1 | L15, L14 | Most raids are LOCKED at PLAN; S is capped near 5 otherwise. Needs a designer call. |

**Applied in L14 (designer 2026-10-24):** R9 (the dummy deck plus wounds; no reward for holding), R1 (a second sealed
beam), R13 (one more card drawn per Heat band) and R14 (a Heat-priced hint). R14's hidden results were reverted in the
L15 presentation after the L14 critic showed they misled players.
