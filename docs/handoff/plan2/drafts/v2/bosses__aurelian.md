<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01VyfaEioaVujaomJg4hxWKS, custom_id v2__bosses__aurelian; status ok; tokens in 23278 cache-write 0 cache-read 32585 out 41782; cost $0.235. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, Lictor not budgeted / over the 3–4 turn limit):**
  - Buff 5 is now **one** Lictor, **P2 only**, docked on the first Gladius (6 ticks), 8 HP. Two Lictors on P3's single Gladius was impossible.
  - Thresholds are now 0.88 / **0.775** / 0.46 / 0.33.
  - The floor is ceil(0.775 × 380) = 295.
  - Phase HP is 45 / 40 (+8 Lictor = 48) / 120 / 49 / 126 = 380, with turns 3.4 / 3.2 / 3.9 / 3.7 / 3.5 = 17.7.
  - "Optional detour" is replaced by "a forced guard when the needle sits on that Gladius; budgeted in P2".
  - The Lictor's Rod intake is added to P2.
- **Issue 2 (BLOCKER, Praetorian shield):**
  - The percent shield is recomputed on the elite's own max HP (5 % × 58 = 2.9, × 5/30 = 0.48).
  - Sustain is now 1.81 / 2.31 / 2.99 / 3.88, P1 budgets are 25.2 / 30.4 / 38.5 / 49.4, and the sum is 56.7 / 68.9 / 87.5 / 112.4.
  - The authored 58 / 70 / 89 / 114 and threshold 0.55 are kept; both are in band.
- **Issue 3 (MAJOR, Gate Codes deletes P1 and P4):**
  - Gate Codes → TOLL GATE now makes the CALL **deferred**. The verdict is recorded at the landing and applied at your next End Turn, before the resolve.
  - The `verdict_map`, including P4's inversion, is unchanged, and you get one turn to Cleanse or Encrypt.
  - P1 and P4 keep their questions. The "counters degrade, never delete" claim now holds.
- **Issue 4 (MAJOR, Genome duplication):**
  - Murmillo is now "OVERFLOW 7, **×3 while the slice under your pointer is marked**" (NEW slice rider `multiplier_vs_status`, an N20 extension). It replaces `perfect_multiplier`.
  - The answers are Cleanse, Encrypt and steering, not a one-tick nudge.
  - P3's question is now "how many marks can I carry?".
  - P5's Pollice also MARKs (pierce plus mark), so its loop is mark → ×3, not "corrupt every hit".
  - The pairing tables for P3 and P5 are redone around enemy slice pairings.
  - The Praetorian's P2 becomes the elite that teaches the marked-×3 punish, and it now needs NEW-A.
- **Issue 5 (MAJOR, 8-tick slices):**
  - R11's default for 8 ticks is W W W G G W W W (no Perfect), now stated in §2.2.
  - The mini-boss P3 Thumbs 8 authors `tick_quality` = G×8, so its intake math holds.
  - Boss P1 Null 8 has no effect, so quality is moot.
  - The roster's other 8-tick slices (Dole Cart Dole, Lictor Gladius, Vestal Pyre) are re-cut to 7 or less, with the sums re-added.
  - Intake figures are stated as full-output upper bounds; the sim applies sub-tick tiers.
- **Issue 6 (NIT, Vestal):** the percent shield is not rescaled. Sustain is 1.12 / 1.36 / 1.76 / 2.24, budgets are 27.6 / 33.7 / 42.8 / 55.2, and the authored HP is unchanged (28 / 34 / 44 / 56).
- **Issue 7 (NIT, US spelling):** "defence" → "defense", "flavour" → "flavor", "centre" → "center", "judgement" → "judgment".
- **Issue 8 (NIT, contradictions):**
  - §1.2 now says VERDICT is a new status (NEW-A) built from existing parts.
  - The enrage steps are placed correctly (turn 12 in P4, turn 16 about two turns into P5, turn 20 later).
  - The "clear marks by landing WEAK" advice is removed (it trades the mark for CORRUPTED).
  - DECOY as a threat is replaced by a float threat with high integrity.
  - Intermission Debt judges under the **outgoing** phase's map, so entering P4 does not accidentally reward WEAK.
- **Triage BLOCKER rows:** both are covered by issues 1 and 2.
- **Critic Qs:**
  - The Dole gift is not a scaled enemy flat amount. RAM is not on R2's list (heal, block, shield, hits), so +3 stays flat (answered inline).
  - The loan valuation and the forced boss bodyguard move into Q:.
- **Kept, because strong:**
  - The read-tier table and the data-only inversion.
  - The uneven-needle pairing aid (rebuilt).
  - The teaching order of the roster.
  - The honesty that N6, N7 and N10 are not needed.
  - Mini-boss HP arithmetic, rechecked.
- **Rulings:** no conflict with a designer ruling.

---

# Aurelian Concord: corporation content draft

Working ids: corporation `aurelian_concord`; enemy files under `content/enemies/`. All names are placeholders and every number awaits the balance sim. Reference damage per turn is `reference_dpt_by_tier` = [9, 11, 14, 18] with 3.5 turns per phase, so one needle's phase budget is 31.5 / 38.5 / 49 / 63 HP at T1–T4. Enemy tier damage factors are [1.0, 1.3, 1.69, 2.2]. Flat amounts are written at T1 base and scale by that factor. Intake figures are full-output upper bounds (every landing at 1.0×); the sim applies sub-tick tiers.

---

## 1. Corporation identity summary

### 1.1 What they sell, in game terms
Aurelian sells bread and circus as a subscription: you are a *client*, and the House collects. The fight-facing idea is **consent**. Aurelian rarely hurts you directly. It *judges* you, and your own precision decides the verdict.

- Solace taxes RAM.
- Meridian locks and steers.
- Halcyon stacks statuses.
- Orbital moves the geometry.
- REBEL_CELL mirrors you.
- **Aurelian grades your landing.** Its signature stat is the landing tier, which no other corporation reads.

### 1.2 House rule: VERDICT (specified for the build)

VERDICT is a **new status on a player slice (NEW-A)**, built from existing parts: OVERCLOCKED, CORRUPTED, ENCRYPTED, CLEANSE, the landing tiers of GDD 2.4 and the R8/R9 status rules.

| Term | Rule |
|---|---|
| **MARK** | An Aurelian slice puts a VERDICT mark on one of your slices (under your pointer, or a deterministic neighbor). The mark waits. |
| **Judgment** | When a marked slice next resolves, the **read tier** decides (table below). |
| **CALL** | An immediate verdict: at the end of the resolve (statuses pass, GDD 2.2 step 3) the slice(s) under your pointer(s) are judged by *this turn's* landing. A GOOD call leaves a mark. |
| **Deferred CALL** | Under the TOLL GATE counter (boss buff 1) the CALL records the landing tier and applies the verdict at your next End Turn, before the resolve. You get a turn to Cleanse or Encrypt. Preview: the badge shows the pending verdict. |
| **Read tier** | The landing tier after TIER_DOWN stacks (R8). A netted GOOD reads WEAK. Sub-tick maps (R11) decide the landing. |
| **Cap** | `max_on_wheel` (default 2) per wheel. A mark beyond the cap is refused, so previews stay trivial. |
| **Defense** | ENCRYPTED absorbs the mark or the resulting status. CLEANSE removes a mark. SANDBOX (R13) negates the whole resolution, riders included (Q1). |
| **Preview** | A thumb badge on the marked slice. The chip on the pointer reads `VERDICT ▲ OVERCLOCK`, `▼ CORRUPT` or `= STAYS`, computed from the same landing, so preview = result. |

| Read tier | Standard verdict | Result |
|---|---|---|
| PERFECT | thumbs up | slice OVERCLOCKED (1.5× on its next trigger, then it burns into CORRUPTED) |
| GOOD | no verdict | mark stays (CALL: places a mark) |
| WEAK | thumbs down | slice CORRUPTED (R9: 2× RAM for cards and nudges acting there) |

- The verdict map is **data**: `verdict_map` = {PERFECT, GOOD, WEAK} → {status, MARK or NONE}. Inversion (boss P4) is a data change.
- **Why it is a real question and not a tax.**
  - Under R9, CORRUPTED deals no damage. Thumbs-up is a loan (1.5× once, then a 2× RAM tax until cleansed).
  - Thumbs-down is an immediate tax.
  - GOOD is the cheap, safe landing, but it leaves the mark in place, and the marked slice is a liability (Interest, and the Murmillo ×3 punish).
  - "Which offset do I land on?" is never free, and there is no always-right answer.
- **Levers the player has:** the free nudge; paid nudges (double cost on a CORRUPTED slice); steering the enemy needle off the Thumbs slice; Cleanse and Encrypt; SANDBOX; a "Calibrated" Firmware (R11).
- **The mark is skippable but not free.** You may never resolve a marked slice, but then it is dead weight on a 6-slice wheel, and it can still be the slice your pointer lands on at the start of a turn.
- **A GOOD landing never clears a mark.** Bite comes from Interest and the marked-×3 punish, not from GOOD punishing you.

### 1.3 Tone
Grand, paternal, legal. Intents read like corp paper: "Your patronage has been RENEWED." Latin tags are branding. The Dole slice says "FREE" and means "free, terms apply". Defeat verb: PACIFIED.

### 1.4 Exploit trio flavor
- **INTEL (the client rolls):** who is whose client; reveals the Arena seating plan and the Lictor roster.
- **BREACH (the gate codes):** triumph-gate and Grand Stand access, plus legion engineering.
- **VIRUS (the open dole):** the ration chips are freed, and debts are wiped.

The pool is eight named Exploits (§3.4), each tagged INTEL, BREACH or VIRUS. A Grid draws five (R7). Each Exploit sits at its own special building (D5), mapped to the art's Site types.

### 1.5 Raid flavor (LEVIES)
The Levy is a legion wedge in verdigris plus a gilded float. The raid summary is a **LEVY RECEIPT**. Threat roster sketch for the pending raid pass (existing threat fields):
- **Legion wedge:** slow, high integrity, SHORTEST_TO_HOME.
- **Collectors:** fast, low integrity, HIGHEST_VALUE (they hunt Vault Terminals).
- **Gilded float:** very slow, very high integrity, WEAKEST_NODE routing, placed to soak asset fire by being first in path.

The raid-pass hook is R1 EXPOSED: the Levy "calls a verdict" on one node, so an asset there is exposed. R4's ultimatum is naturally a "TRIBUTE" demand, the Schematics sink.

### 1.6 Story-path hooks (beats reveal in Exploit order; one path per campaign)

| Path | Hook |
|---|---|
| The Free Bread | The dole is the leash: the ration chips are the subscription. Beats follow VIRUS finds. |
| Fixed Games | Arena outcomes are rigged by a patron. The Games Master's wheel is "calibrated". |
| Census of Clients | The Censor's ledger lists every subbie's patron. |
| Bread Riot | The wards revolt. Story raids are mobs, not legions. |
| A Patron for DISPATCH | Foreshadows DISPATCH: the ledger shows a patron with impossible timestamps. |
| The Triumph | The Rostrum prepares a victory parade over the Cell. The finale. |

### 1.7 Where the art identity needs a game-side change

| # | Art identity says | Game-side change needed |
|---|---|---|
| 1 | VERDICT uses only existing statuses | Needs a new `Status.VERDICT` (a tier-conditional mark), the call effect and the deferred call. NEW-A in §5. |
| 2 | Art Q2: does GOOD keep the mark? | Decided: yes, the mark stays. |
| 3 | Seven Site types, eight buffs | An **eighth Exploit building** is needed. Proposed: CASTRA (legion camp) for the Lictor Roster. Flag to art. |
| 4 | Enemy list Lictor, Legionary, Tax Farmer, Lanista, Vestal | Lanista is **promoted to the mini-boss** ("Games Master"; Lanista Corvina stays the event speaker). The roster adds **Crier** and **Dole Cart** and gives the Legionary a net. |
| 5 | Phase 2 "arches turn gilt, Grand Stand lights" | In this design that moment is **boss P4** (the crowd turns, verdict inverts). The hub thumb flips to thumbs-up as the tell. Sync with the boss-wheel agent. |
| 6 | "PACIFIED" loss stamp | The campaign-lost verb needs a per-corporation string field. |
| 7 | REBEL_CELL unlocks after every other corporation | GDD 8.5 now means all six others. Flag to the profile ladder. |
| 8 | THE TURNING GATES HQ mechanic | Belongs to the HQ netrun pass (G12). Nothing here depends on it. |
| 9 | Verdigris is never used for a gain chip | The Dole's "+3 RAM" gift must use the standard GAIN chip with ▲, not the corp hue. |

---

## 2. Mini-boss: THE GAMES MASTER (`games_master.tres`)

### 2.1 Identity and the one question
**Question: "Where is my safe offset right now?"** The mini-boss is the house rule examined at depth. Each phase changes *what the safe landing is*:
- **P1:** GOOD is safe.
- **P2:** a net flips it, so PERFECT is the safe landing and GOOD hurts.
- **P3:** it judges you the same turn, and the only escape is steering.

It needs no listener, lock or ring, so it can ship early.

### 2.2 Phase plan

Three phases, thresholds 0.66 and 0.33. Every layout sums to 30. Amounts are T1 base.

| | **P1 Opening Bouts** (100 → 66 %) | **P2 The Net** (66 → 33 %) | **P3 Roar** (33 → 0 %) |
|---|---|---|---|
| Needles | 1, tick 0 | 1, tick 0 | 1, tick 0 |
| Layout (ticks) | Gladius 6 · Thumbs 4 · Testudo 5 · Trident 5 · Thumbs 4 · Null 6 = 30 | Gladius 6 · Net 5 · Trident 5 · Thumbs 4 · Testudo 4 · Gladius 6 = 30 | Gladius 5 · Thumbs 8 · Trident 5 · Gladius 5 · Testudo 4 · Null 3 = 30 |
| Gladius | SHIM 4 | SHIM 7 | SHIM 9 |
| Trident | OVERFLOW 8 | OVERFLOW 11 | OVERFLOW 13 |
| Testudo | BLOCK 6 FLAT | BLOCK 6 FLAT | BLOCK 6 FLAT |
| Thumbs | SHIM 2 + **MARK** (pointer slice, cap **1**) | SHIM 3 + **MARK** (cap **2**) | SHIM 4 + **CALL** (standard verdict, same resolve) |
| Net | n/a | SHIM 2 + **TIER_DOWN ×1** on your pointer slice (cap 2 slices) | n/a |
| Hub rule | None | **Purse:** HEAL PERCENT 1 % max HP per turn | None |
| Intake (T1 base) | 2.7 | 5.4 | 6.2 |
| Intake target | 2–4 | 4–6 | 6–9 |

**P3 Thumbs sub-tick map:** an 8-tick slice defaults to W W W G G W W W (no Perfect, R11). This Thumbs authors `tick_quality` = G×8: the judging slice always lands full strength and never has a Perfect. A 27 % slice that always bites is the P3 question.

**Intake arithmetic (tick share × amount):**
- P1: 6/30×4 + 5/30×8 + 8/30×2 = 0.8 + 1.33 + 0.53 = 2.67.
- P2: 12/30×7 + 5/30×11 + 5/30×2 + 4/30×3 = 2.8 + 1.83 + 0.33 + 0.4 = 5.37.
- P3: 10/30×9 + 5/30×13 + 8/30×4 = 3.0 + 2.17 + 1.07 = 6.23.

**Transitions:**
- `cleanse_on_enter` = NONE (R6), so marks and nets carry across phases.
- The P2 net and marks matter at once in P3, because a netted, marked slice is judged by the P3 CALL.
- Phase lines: "Games begin" / "The Net" / "Roar".

### 2.3 Sustain and HP by tier (R2 arithmetic)

Sustain per turn = expected BLOCK absorbed (tick share × 6 × tier factor) + hub HEAL PERCENT. Budget per phase = (dpt − sustain) × 3.5.

| | T1 (dpt 9) | T2 (dpt 11) | T3 (dpt 14) |
|---|---|---|---|
| P1 sustain: Testudo 5/30 × 6 × f | 1.00 | 1.30 | 1.69 |
| P1 budget | 8.00×3.5 = **28.0** | 9.70×3.5 = **33.95** | 12.31×3.5 = **43.1** |
| P2 sustain: Testudo 4/30×6×f + 1 % HP | 0.80+0.86 = 1.66 | 1.04+1.06 = 2.10 | 1.35+1.32 = 2.67 |
| P2 budget | 7.34×3.5 = **25.7** | 8.90×3.5 = **31.2** | 11.33×3.5 = **39.7** |
| P3 sustain: Testudo 4/30×6×f | 0.80 | 1.04 | 1.35 |
| P3 budget | 8.20×3.5 = **28.7** | 9.96×3.5 = **34.9** | 12.65×3.5 = **44.3** |
| Sum of budgets | 82.4 | 100.1 | 127.1 |
| R2 band (3-phase mini-boss) | 85–105 | 104–128 | 132–162 |
| **Authored `hp_by_tier`** | **86** | **106** | **132** |

The netted sum is just under the band floor, so I author the floor (86 and 106 are rounded a hair above it; 132 is the floor). Floors and phase HP:

| Tier | Floors (0.66 / 0.33) | Phase HP P1 / P2 / P3 | Turns P1 / P2 / P3 |
|---|---|---|---|
| T1 (86) | ceil(56.76) = 57 · ceil(28.38) = 29 | 29 / 28 / 29 | 29/8.00 = 3.6 · 28/7.34 = 3.8 · 29/8.20 = 3.5 |
| T2 (106) | ceil(69.96) = 70 · ceil(34.98) = 35 | 36 / 35 / 35 | 36/9.70 = 3.7 · 35/8.90 = 3.9 · 35/9.96 = 3.5 |
| T3 (132) | ceil(87.12) = 88 · ceil(43.56) = 44 | 44 / 44 / 44 | 44/12.31 = 3.6 · 44/11.33 = 3.9 · 44/12.65 = 3.5 |

All phases fall in the 3–4 turn target. The highest sustain is P2 at about 18–19 % of dpt, under the 30 % limit. Purse is PERCENT, read from max HP and never scaled again (R2).

### 2.4 Enrage
Mini-boss default (R4): start turn 10, every 5 turns, +25 % additive. Expected length is about 11 turns, so the first step usually lands late in P3, as intended.

### 2.5 Counterplay per phase

**P1 (read the exam):**
- Land the marked slice at GOOD and the mark just stays.
- Land PERFECT only for the loan: a marked OVERFLOW that resolves at 1.5× is a legitimate burst plan.
- Use the free nudge to lift a WEAK landing to GOOD.
- Encrypt or Cleanse the mark.
- Nudge the enemy wheel to keep the needle off the two 4-tick Thumbs.

**P2 (the safe offset flips).** A netted slice reads one tier lower:

| Your landing | Read tier (net ×1) | Verdict on a marked slice |
|---|---|---|
| PERFECT | GOOD | mark stays (safe) |
| GOOD | WEAK | **CORRUPTED** (and 0.5× output) |
| WEAK | WEAK | CORRUPTED |
| PERFECT (net ×2) | WEAK | CORRUPTED |

- The safe move on a netted marked slice is to land PERFECT, which costs nudges.
- Cleanse a net before you resolve the slice.
- Leave netted slices unresolved. A turn on an *unmarked* netted slice is only a 0.5× hit.
- Two nets and two marks can occupy four of your six slices.

**P3 (no skipping):**
- The Thumbs CALL judges whichever slice you play, the same turn.
- Your outs: steer its needle off the 8-tick Thumbs (the first enemy-wheel nudge is free); SANDBOX the Thumbs resolve; land GOOD (the CALL leaves only a mark); Encrypt the slice you intend to play.
- Perfect-hook classes must decide whether the 1.5× loan is worth the 2× RAM tax.
- The enrage step at turn 10 gives a reason to burst.

### 2.6 Systems
- NEW-A (VERDICT status, mark and call, `verdict_map`).
- N8 and N9 (TIER_DOWN stacks, CORRUPTED = RAM ×2).
- N3 (phases, parking) and N4 (enrage).
- N12 (the 4-, 5- and 8-tick slices, and the `tick_quality` override).

**Fallback without N12:** six 5-tick slots per phase.
- P1: Gladius · Thumbs · Testudo · Trident · Thumbs · Null.
- P2 and P3: the same template with Net or Thumbs substituted.

This keeps the exam intact, because the Games Master only needs to *place* marks and nets. Intake shifts and the sim retunes. **No data-only fallback** exists for the verdict itself.

### 2.7 Delta and notes
- It needs no N6, N7 or N10, so it can be built first.
- It deliberately avoids the other mini-bosses' hooks (Solace's Perfect counter, Halcyon's stack-and-lock, Meridian's latch ring, Orbital's gates, REBEL_CELL's mirror).
- The only overlap is Halcyon's status stacking. TIER_DOWN here is positional (it moves your *safe landing*), not a damage lever.

---

## 3. Boss: THE ROSTRUM (`rostrum.tres`, Hub: THE GRAND STAND)

### 3.1 Identity and the one question
THE ROSTRUM stages a day at the Games in five acts. **The single rule, VERDICT, is re-read every act**, and each act asks a new question:

| Act | Question |
|---|---|
| P1 Processional | "How do I live under a judge?" |
| P2 Free Bread | "Is the gift worth the debt?" |
| P3 Gladiators | "How many marks can I carry?" |
| P4 The Crowd Turns | "What do I do when the safe landing flips?" |
| P5 Pollice Verso | "Can I stay unmarked while it pierces me?" |

The fight is one slow lesson in landing quality, ending in a race against marks and pierce.

### 3.2 Phase plan

All layouts sum to 30. Amounts are T1 base; the T4 effective value is ×2.2. **Murmillo ×3 vs marked** is the slice rider `multiplier_vs_status` (NEW, N20 extension): its damage is tripled while the slice under your pointer is marked (checked before the statuses pass). Pierce is N20.

| | **P1 Processional** | **P2 Free Bread** | **P3 Gladiators** | **P4 The Crowd Turns** | **P5 Pollice Verso** |
|---|---|---|---|---|---|
| Window | 100 → 88 % | 88 → 77.5 % | 77.5 → 46 % | 46 → 33 % | 33 → 0 % |
| Needles | 1 @ 0 | 1 @ 0 | **2 @ 0 / 11** (uneven, R10) | 1 @ 0 | **2 @ 0 / 13** |
| Layout | Gladius 7 · Testudo 4 · Gladius 6 · Trident 5 · Null 8 = 30 | Gladius 6 · Dole 5 · Trident 5 · Testudo 4 · Dole 4 · Gladius 6 = 30 | Murmillo 7 · Net 4 · Dole 4 · Gladius 5 · Testudo 4 · Null 6 = 30 | Gladius 6 · Net 4 · Trident 5 · Testudo 4 · Dole 5 · Gladius 6 = 30 | Murmillo 7 · Gladius 4 · Pollice 5 · Net 4 · Gladius 4 · Null 6 = 30 |
| Amounts | Gladius SHIM 3; Trident OVERFLOW 6; Testudo BLOCK 6 FLAT | Gladius 4; Trident 8; Testudo BLOCK 6 | Murmillo OVERFLOW 7 (**×3 vs marked**); Gladius 3; Net SHIM 2 + TIER_DOWN ×1; Testudo BLOCK 6 | Gladius 4; Trident 9; Net 2 + TIER_DOWN ×1; Testudo BLOCK 6 | Murmillo 7 (×3 vs marked); Gladius 3; **Pollice OVERFLOW 7, pierce, + MARK**; Net 2 + TIER_DOWN ×1 |
| Dole | n/a | Gift **+3 RAM** to you and **2 MARKS** (pointer slice + next clockwise) | same | same | n/a |
| Hub rule | **Grand Stand CALL** (standard) + Herald HEAL PERCENT 0.5 % | CALL + **Interest** | CALL + Interest | **CALL INVERTED** + Interest + Herald HEAL PERCENT 0.5 % | CALL (standard again) + Interest |
| Testudo Wall (buff) | + SHIELD PERCENT 2 % | same | same | same | no Testudo |
| Lictor (buff) | none | 1 Lictor on the first Gladius, 8 HP | none | none | none |
| Intake T4 (unmitigated) | 5.1 | 7.3 | 12.9 | 7.4 | 19.4 |
| Intake target T4 | 3–6 | 5–8 | 9–13 | 7–10 | 15–20 (before enrage) |

An 8-tick Null in P1 has no effect, so its sub-tick map is moot.

**What the hub rules do:**
- **CALL:** after each resolve, the slice(s) under your pointer(s) are judged by this turn's landing (§1.2), in the statuses pass.
- **Interest:** at the start of each of your turns, every marked slice gains OUTPUT_DOWN ×1 (cap ×3): −25 %, −50 %, −75 % of that slice's output. Marks are the cost of the Dole and of GOOD landings.
- **INVERTED (P4):** `verdict_map` becomes PERFECT → CORRUPTED, WEAK → OVERCLOCKED, GOOD → mark. Now the *stumble* is rewarded and precision is punished.
- **Intermission Debt (buff 7):** at each phase change, every mark on your wheel is judged as a WEAK landing under the **outgoing** phase's map, so it becomes CORRUPTED (the P3 → P4 change does not read the inverted map).
- **Murmillo punish:** the hit is tripled only if the slice under your pointer was already marked when the resolve began. A Dole mark made in the same resolve cannot be punished until next turn.

**Intake arithmetic (full output; tick share × amount × 2.2):**
- P1: (13/30×3 + 5/30×6) × 2.2 = (1.3 + 1.0) × 2.2 = 5.1.
- P2: (12/30×4 + 5/30×8) = 1.6 + 1.33 = 2.93; the Lictor's Rod (SHIM 2 when its host slice resolves) adds 6/30×2 = 0.4; (2.93 + 0.4) × 2.2 = 7.3.
- P3 (per needle), assuming on average 1 of your 6 slices is marked: Murmillo 7/30×7 = 1.63, marked bump 7/30 × 1/6 × 14 = 0.54, Net 4/30×2 = 0.27, Gladius 5/30×3 = 0.5, total 2.94. Two needles × 2.2 = 12.9. Range: no marks 2.40 per needle (10.6 total), two marks 3.49 (15.4 total).
- P4: (12/30×4 + 5/30×9 + 4/30×2) × 2.2 = (1.6 + 1.5 + 0.27) × 2.2 = 7.4.
- P5 (per needle), one mark average: Murmillo 1.63 + 0.54, Gladius 8/30×3 = 0.8, Pollice 5/30×7 = 1.17, Net 0.27, total 4.41. Two needles × 2.2 = 19.4.

**Needle pairing (uneven needles).** Rotation moves both needles; B = A + gap. Enemy WEAK edges deal 0.5×.

*P3, gap 11.* Murmillo [0–6] (W W G P G W W), Net [7–10], Dole [11–14] (W G G W), Gladius [15–19] (W G P G W), Testudo [20–23], Null [24–29].

| A tick | A reads | B tick | B reads | What the player faces |
|---|---|---|---|---|
| 0 | Murmillo WEAK (0.5×) | 11 | Dole WEAK edge | quiet turn; the Dole still marks |
| 2 | Murmillo GOOD (full) | 13 | Dole GOOD | **hit and re-mark:** a marked pointer slice takes ×3, and two new marks follow |
| 4 | Murmillo GOOD | 15 | Gladius WEAK | full Murmillo, half Gladius |
| 6 | Murmillo WEAK | 17 | Gladius GOOD | half Murmillo, full Gladius |
| 21 | Testudo GOOD (block) | 32 → 2 | Murmillo GOOD | the boss blocks while it hits: steer off Murmillo or pay the marked ×3 |

*P5, gap 13.* Murmillo [0–6], Gladius [7–10], Pollice [11–15] (W G P G W), Net [16–19], Gladius [20–23], Null [24–29].

| A tick | A reads | B tick | B reads | What the player faces |
|---|---|---|---|---|
| 0 | Murmillo WEAK | 13 | **Pollice PERFECT** (full, pierce, mark) | the pierce is the threat; Murmillo is half |
| 1 | Murmillo WEAK | 14 | Pollice GOOD (full) | same |
| 2 | Murmillo GOOD (full) | 15 | Pollice WEAK (half) | Murmillo is the threat (×3 if marked) |
| 4 | Murmillo GOOD | 17 | Net GOOD | two full hits, but Net is a 2-damage slice |

**Pairing rule:** Murmillo and Pollice are never both at full power. The player picks which needle to deny, not whether both are safe.

**Transitions (R6):**
- `cleanse_on_enter` = NONE everywhere; statuses carry across phases with the standard remap.
- Each transition plays a line and reveals the new layout.
- P3 enters via MULTIPLY (a second needle at 0 / 11).
- P5 enters via MULTIPLY (0 / 13) and removes Testudo and the Herald.
- P4 changes `hub_override` to the inverted map. This is the only phase where the verdict flips.
- **Intermission Debt** fires at every transition (`on_enter_effects`, N3 extension). **Clear your marks before the floor** (Cleanse or Encrypt).

### 3.3 Sustain, intake and the HP budget (R2 arithmetic)

Boss budget per phase = (needles × 18 − sustain) × 3.5. Sustain per needle is expected BLOCK absorbed (4/30 × 6 × 2.2 = 1.76) plus Wall shield (4/30 × 2 % × 380 = 1.01) plus hub heal (0.5 % × 380 = 1.9). Authored at max HP 380.

| Phase | Needles | Sustain per turn | Budget |
|---|---|---|---|
| P1 | 1 | heal 1.9 + Testudo 1.76 + Wall 1.01 = **4.7** | (18 − 4.7) × 3.5 = **46.5** |
| P2 | 1 | Testudo 1.76 + Wall 1.01 = **2.8** | (18 − 2.8) × 3.5 = **53.2** |
| P3 | 2 | (1.76 + 1.01) × 2 = **5.5** | (36 − 5.5) × 3.5 = **106.8** |
| P4 | 1 | 1.9 + 1.76 + 1.01 = **4.7** | **46.5** |
| P5 | 2 | **0** | 36 × 3.5 = **126** |
| **Sum** | | | **379** |

- Sustain stays ≤ 30 % of each phase's reference damage: P1 and P4 are 4.7/18 = 26 %, P2 is 16 %, P3 is 15 %.
- **`hp_bands`** (ICE boss-strength zone ceiling → HP): **≤ 1.00 → 380 · ≤ 1.15 → 420 · ≤ 1.30 → 460 · > 1.30 → 510** (the same +10 / +21 / +34 % ladder as the Genome Core).
- **Thresholds:** 0.88 / 0.775 / 0.46 / 0.33. Floors at 380: ceil(334.4) = 335 · ceil(294.5) = 295 · ceil(174.8) = 175 · ceil(125.4) = 126.

| Phase | HP | Turns |
|---|---|---|
| P1 | 380 − 335 = 45 | 45/13.3 = 3.4 |
| P2 | 335 − 295 = 40 host + **8 Lictor** = 48 | 48/15.2 = 3.2 |
| P3 | 295 − 175 = 120 | 120/30.5 = 3.9 |
| P4 | 175 − 126 = 49 | 49/13.3 = 3.7 |
| P5 | 126 | 126/36 = 3.5 |
| **Total** | 380 (+8 Lictor) | **17.7** |

- 17.7 turns sits inside R1's 12–20, and every phase is in 3–4 turns (P3 at 3.9 is the edge; the sim retunes).
- P2's budget is 53.2 against 48 authored: the Lictor is a **forced guard** and is budgeted here. When the needle sits on the guarded Gladius (6/30 = 20 % of turns), your pointer hit lands on the Lictor (GDD 2.7) and the overkill is wasted, which accounts for the 5-HP gap.
- Percent amounts read the real max HP (higher bands run slightly longer; the sim retunes).
- Budgets assume **all buffs active**. Each Exploit makes the fight shorter, the intended reward.

### 3.4 Buffs and their Exploits (8; a Grid draws 5; `min_exploits_for_breach` = 3)

| # | Buff | Effect | Counter Exploit (type) → building | Signature |
|---|---|---|---|---|
| 1 | **Grand Stand** | The hub CALLs a verdict every turn (the house rule). | **Gate Codes** (BREACH) → TOLL GATE: the CALL is **deferred**: it records your landing and applies the verdict at your next End Turn, before the resolve. The `verdict_map` (including P4's inversion) is unchanged, and you get one turn to Cleanse or Encrypt. | **yes** |
| 2 | **Interest** | Marks grow OUTPUT_DOWN each turn (P2+). | **Debt Relief** (VIRUS) → ANNONA: marks stay marks, no growth | **yes** |
| 3 | **Free Bread** | The Dole's gift comes with 2 marks. | **Open Dole** (VIRUS) → DOLE: the Dole gives RAM only | |
| 4 | **Twin Gladiators** | The second needle in P3 and P5. | **Arena Plan** (INTEL) → LUDUS: one needle | |
| 5 | **Lictor** | One fixed fasces satellite on the first Gladius in P2 (8 HP; Rod SHIM 2; guards that slice) | **Lictor Roster** (INTEL) → CASTRA (new): no Lictor | |
| 6 | **Testudo Wall** | Testudo slices also gain SHIELD PERCENT 2 % (enemy percent shield; own cap, Q3). | **Siege Wright** (BREACH) → AQUEDUCT: BLOCK only | |
| 7 | **Intermission Debt** | At every phase change, all your marks are judged as WEAK under the outgoing map (CORRUPTED). | **Amnesty** (VIRUS) → ATRIUM: marks persist unjudged | **yes** |
| 8 | **Sudden Death** | Pollice (P5) pierces BLOCK and SHIELD. | **Appeal** (BREACH) → CURIA: Pollice is a plain OVERFLOW (it still marks) | |

**Distribution:** INTEL 2, BREACH 3, VIRUS 3.

**Counters degrade the fight, they never delete a phase.**
- With *Gate Codes* every phase keeps its question (a deferred CALL still marks, judges and inverts in P4).
- With *Arena Plan*, P3 and P5 are one needle: shorter, with the same questions.
- With *Debt Relief*, P2 loses its bill but keeps the Dole and Net choices.
- With *Lictor Roster*, P2 loses one guard turn and gains a straight race.

### 3.5 Enrage
**Authored**, not the boss default: start turn 12, every 4 turns, +25 % additive (×1.25, ×1.5, …). It raises damage only. The HUD shows a falling-sand chip ("the Games are running long").

**Why not the default (10 / 5):** P1–P3 end at about turn 10.5 (3.4 + 3.2 + 3.9), so the default's first step would land at the P3 → P4 boundary. With 12 / 4:
- Step 1 (turn 12) lands in P4, which ends at about turn 14.2.
- Step 2 (turn 16) lands about two turns into P5.
- Step 3 (turn 20) catches only slow routes.

A typical 17.7-turn fight sees two steps.

### 3.6 Counterplay per phase

**P1 Processional**
- Land GOOD on slices you are not ready to pay for.
- Land PERFECT on a damage slice only if you will replay it for the 1.5× before it burns out.
- Cleanse or Encrypt a slice you intend to reuse.
- Hub Breach (a card) turns the CALL off for one turn, so you can land PERFECT for free.
- P1 is short (45 HP). Burst through it.

**P2 Free Bread**
- Interest makes a mark a ticking bill, so the Dole is a decision:
  - Let the needle land on Dole and the boss does nothing, but you pay two marks and gain +3 RAM.
  - Or nudge the enemy wheel off Dole for 1 RAM.
- Clear marks with Cleanse, or accept a PERFECT loan on a slice you will replay.
- The Lictor guards the first Gladius: steer the needle off that slice, or spend a turn killing the 8-HP rod.

**P3 Gladiators**
- Two needles mean your hits land twice, so race.
- **Starve the ×3:** Murmillo is only dangerous to a marked slice under your pointer. Cleanse, Encrypt, or use your free nudge so an unmarked slice sits under the pointer (the preview shows the ×3 before you commit).
- Use the pairing table: when needle A is on Murmillo, B is on the Dole or a half-power edge.
- Nets plus marks recreate the mini-boss's P2 puzzle, doubled.
- **Clear your marks before the floor** (Intermission Debt fires at the transition).

**P4 The Crowd Turns**
- The safe landing flips: a WEAK landing now OVERCLOCKS, PERFECT CORRUPTS.
- A 4-tick slice (W G G W) now has two thumbs-up edges and no Perfect to trip over.
- A Net helps: GOOD under a net reads WEAK, which is now thumbs-up.
- Perfect-hook classes should avoid the hook or carry Cleanse. Calibrated Firmware turns edge WEAKs into GOOD (the mark stays), so it protects but does not reward.
- Marks left from P3 (with Amnesty) are judged by the inverted map.

**P5 Pollice Verso**
- No boss defense, so every hit lands.
- Pierce skips BLOCK and SHIELD. Your answers are **SANDBOX** (negates the whole resolution, riders included), **steering** the needle off Pollice, or the Appeal Exploit.
- Pollice also marks you, and Murmillo punishes marks next turn, so Cleanse and Encrypt are the economy of the phase.
- The gap-13 pairing means a full Pollice never pairs with a full Murmillo.
- Finish before the second enrage step (turn 16).

### 3.7 Systems
- NEW-A (VERDICT status, CALL, deferred CALL, INVERTED map).
- NEW-B: SlicePick `NEXT_CW` and `ALL_MARKED`.
- NEW-C: opponent-targeted beneficial effects (the Dole gift, `GAIN_RAM` targeting the player).
- N1 (percent shield and heal).
- N3 (phases, parking, plus a small `on_enter_effects` extension for Intermission Debt).
- N4 (authored enrage chip).
- N5 (buffs and Exploits).
- N8, N9 (OUTPUT_DOWN, TIER_DOWN stacks).
- N11 (uneven needles).
- N12 (4-, 5- and 7-tick slices).
- N13 (fixed Lictor).
- N14 (SANDBOX).
- N20 (`pierce`, plus the NEW rider `multiplier_vs_status`).

**Fallbacks:**
- Without N12, six 5-tick slots:
  - P1: Gladius, Testudo, Gladius, Trident, Null, Null.
  - P2: Gladius, Dole, Trident, Testudo, Dole, Gladius.
  - P3: Murmillo, Net, Dole, Gladius, Testudo, Null.
  - P4: Gladius, Net, Trident, Testudo, Dole, Gladius.
  - P5: Murmillo, Gladius, Pollice, Net, Gladius, Null.
  - Intake and the pairing tables must be redone.
- Without N5, the buffs are always on, as an "all-countered" test configuration.
- No fallback exists for the CALL itself.

### 3.8 Delta and notes
- Like the Genome Core it ramps: a mild start, a second needle, no defense at the end.
- It differs in that the ramp is **one rule re-read** (VERDICT), not a new slice set per phase, and it needs no listeners.
- The Genome's engine is "every hit corrupts you, and Perfect gets ×N". Here the engine is "marks make your wheel a liability": Murmillo is ×3 vs marked, Pollice marks, Interest bills, and the answers are Cleanse, Encrypt and SANDBOX, not a one-tick nudge.
- The Dole gift is unscaled +3 RAM. RAM is not one of R2's flat enemy amounts, so it is a buff-like flat gift.
- The opponent-targeted gift is the only new effect-target class (NEW-C).

---

## 4. Enemy roster sketch (6 normals, 2 elites)

All normals are 1 phase, 1 needle, no threshold. Wheel sketches list slice name and ticks (sum 30); all amounts are T1 base. R2 bands: normal 28–36 / 34–44 / 44–56 / 56–70 for T1–T4; elite 56–72 / 68–88 / 88–112 / 112–144.

**Teaching order.** The roster teaches the house rule in this sequence:
1. **Crier (L1–2):** the mark, and the "land GOOD" answer.
2. **Dole Cart (L1–2):** gift versus debt.
3. **Legionary Drone (L3):** TIER_DOWN shifts the safe offset.
4. **Tax Farmer (L3–4):** Interest on marks.
5. **Lictor (L4–5):** a fixed bodyguard.
6. **Vestal Firewall (L5–6):** the immediate CALL.
7. **Praetorian (elite, L4–6):** a marked slice is punished (×3).
8. **Censor (elite, L5–6):** marks flip meaning at the phase floor.

Everything the Games Master and the Rostrum use (marks, nets, calls, the marked ×3) has been seen by the time the final Rack arrives.

### 4.1 Normals

| Working name | Class | Layer role | The one question | Wheel sketch | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|---|
| **Crier** | Normal | Teach L1–2 | "What does a mark want from me?" Land GOOD, or keep that slice out of play. | Gladius 6 (3) · Thumbs 5 (1 + MARK, cap 1) · Gladius 6 (3) · Null 7 · Thumbs 6 = 30 | **30 / 37 / 47 / 60** | NEW-A, N12 (fallback: six 5-tick slices) |
| **Dole Cart** | Normal | Teach L1–2 | "Free turn now, debt later?" | Dole 7 (+2 RAM to you; MARK ×1 on pointer slice, cap 1) · Gladius 6 (4) · Testudo 5 (BLOCK 5) · Gladius 6 (4) · Null 6 = 30 | **29 / 35 / 44 / 57** | NEW-A, NEW-C |
| **Legionary Drone** | Normal | Teach L3 | "Under a net, which landing is actually safe?" | Gladius 6 (4) · Net 6 (1 + TIER_DOWN ×1, cap 2) · Gladius 5 (4) · Testudo 4 (BLOCK 6) · Trident 5 (7) · Null 4 = 30 | **29 / 35 / 44 / 57** | N8, N9, N12 |
| **Tax Farmer** | Normal | Teach L3–4 | "How long can I carry this mark?" | Hub: Interest (OUTPUT_DOWN ×1 per marked slice per turn, cap ×2). Thumbs 6 (1 + MARK, cap 2) · Gladius 7 (5) · Null 5 · Gladius 7 (5) · Thumbs 5 = 30 | **31 / 38 / 48 / 62** | NEW-A, NEW-B (`ALL_MARKED`), N8, N9 |
| **Lictor** | Normal | Teach L4–5 | "The guarded slice is the dangerous one. Kill the rod, or steer away?" | Host: Gladius 7 (3) · Trident 6 (6, **guarded**) · Testudo 5 (BLOCK 5) · Gladius 6 (3) · Thumbs 6 (1 + MARK) = 30, with a **fixed Fasces satellite** docked on the Trident (2 slices × 15 ticks: Rod SHIM 2, Bundle BLOCK 3) | **29 / 35 / 44 / 57** (host + satellite: **21+8 / 25+10 / 32+12 / 42+15**) | N13, NEW-A, N12 |
| **Vestal Firewall** | Normal | Pressure L5–6 | "Keep the needle off the Pyre, or land safe, because it judges you now." | Hub: Sacred Flame (SHIELD PERCENT 4 % max HP at turn start). Pyre 7 (3 + **CALL**) · Gladius 7 (4) · Trident 5 (7) · Null 6 · Gladius 5 (4) = 30 | **28 / 34 / 44 / 56** | NEW-A, N1, N12 |

**Arithmetic and intake (T1 base).** Reference budget = dpt × 3.5 = 31.5 / 38.5 / 49 / 63; sustain is netted out.

- **Crier (intake 1.6, no sustain).**
  - Intake: 12/30×3 + 11/30×1 = 1.2 + 0.37 = 1.57.
  - HP about 5 % under budget for a teach enemy: 30 / 37 / 47 / 60.
- **Dole Cart (intake 1.6).**
  - Sustain: Testudo 5/30 × 5 × f = 0.83 / 1.08 / 1.41 / 1.83.
  - HP = (dpt − sustain) × 3.5 = 28.6 / 34.7 / 44.1 / 56.6, authored 29 / 35 / 44 / 57.
  - The Dole is 7 ticks (23 % of turns), so about a quarter of its turns are free.
- **Legionary Drone (intake 2.8).**
  - Intake: 11/30×4 + 5/30×7 + 6/30×1 = 1.47 + 1.17 + 0.2 = 2.83.
  - Sustain: Testudo 4/30 × 6 × f = 0.80 / 1.04 / 1.35 / 1.76.
  - HP = 28.7 / 34.9 / 44.3 / 56.8, authored 29 / 35 / 44 / 57.
- **Tax Farmer (intake 2.7, no sustain).**
  - Intake: 14/30×5 + 11/30×1 = 2.33 + 0.37.
  - HP 31 / 38 / 48 / 62 against budget 31.5 / 38.5 / 49 / 63.
  - Interest caps at ×2, so a mark costs at most −50 % output.
  - Distinct from Halcyon's Citation: Interest grows only on **marked** slices, a clock on a decision, not a stack on your wheel.
- **Lictor (intake 3.7).**
  - Host intake: 13/30×3 + 6/30×6 + 6/30×1 = 1.3 + 1.2 + 0.2 = 2.7, plus the Rod's average 1.0.
  - Sustain: Testudo 5/30×5×f = 0.83 / 1.08 / 1.41 / 1.83.
  - Total budget host + satellite = 28.6 / 34.7 / 44.1 / 56.6.
  - Satellite HP 8 / 10 / 12 / 15, so host = 21 / 25 / 32 / 42.
  - The Trident is the 6-tick guarded slice (20 % of turns), so a guard turn sends your hit to the rod.
- **Vestal Firewall (intake 3.5).**
  - Intake: 7/30×3 + 12/30×4 + 5/30×7 = 0.7 + 1.6 + 1.17 = 3.47.
  - Sustain is the Flame shield, percent of own max HP and never rescaled (R2): 4 % × 28 / 34 / 44 / 56 = 1.12 / 1.36 / 1.76 / 2.24 per turn.
  - Budget = (dpt − sustain) × 3.5 = 27.6 / 33.7 / 42.8 / 55.2.
  - Authored 28 / 34 / 44 / 56 (the T3 value is the band floor, about 1 HP over budget). Turns 3.5–3.6.

**Distinctness from the other corporations:**
- Not billing-based, so no overlap with Solace's Billing Daemon or Collections Agent.
- The Tax Farmer is not a RAM drain, unlike Meridian's Tariff Collector.
- The net and the mark are not Halcyon's Citation.
- The Lictor uses fixed satellites like Solace's mini-boss, but guards the *dangerous* slice.
- No enemy uses spin resistance, orbit or mirroring.

**Fallbacks without the new systems:**
- Without N8/N9 the Legionary can use today's PARASITE status, which halves rather than shifts a tier. That changes the question, so it is not recommended.
- Everything with a mark or call needs NEW-A.

### 4.2 Elites

Both elites have 2 phases, 1 needle each, and use the elite enrage default (start turn 8, every 5, +25 %).

| Working name | Class | Layer role | The one question | Phase plan | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|---|
| **Praetorian** | Elite | Pressure L4–6 | P1 "Starve the wall" (steer off Testudo; block and shield refill only there). P2 "Don't carry marks into the charge" (Murmillo ×3 vs a marked pointer slice). | **P1 Shield Wall** (100 → 55 %): Testudo 5 (BLOCK 8 + SHIELD PERCENT 5 %) · Gladius 7 (4) · Trident 6 (8) · Null 6 · Gladius 6 (4) = 30. **P2 Charge** (55 → 0 %): Murmillo 7 (OVERFLOW 7, **×3 vs marked**) · Thumbs 5 (SHIM 2 + MARK, cap 1) · Gladius 5 (3) · Null 7 · Trident 6 (7) = 30. Needle at 0 in both. | **58 / 70 / 89 / 114** | NEW-A, N1, N3, N12, N20 (`multiplier_vs_status`) |
| **Censor** | Elite | Pressure L5–6 | P1 "Audit": marks and Interest, carry them or clear them? P2 "Redraw": marks you carried flip meaning (previews boss P4). | **P1 Audit** (100 → 48 %): hub Interest (OUTPUT_DOWN per mark per turn, cap ×3). Thumbs 6 (2 + MARK, cap 2) · Gladius 6 (4) · Null 5 · Gladius 6 (4) · Thumbs 7 = 30. **P2 Redraw** (48 → 0 %): `verdict_map` becomes INVERTED. Thumbs 5 (2 + MARK) · Gladius 6 (5) · Trident 6 (8) · Gladius 5 (5) · Testudo 4 (BLOCK 6) · Null 4 = 30. Needle at 0 in both. | **60 / 73 / 93 / 120** | NEW-A, NEW-B, N3, N8, N9, N12 |

**Praetorian arithmetic.**
- P1 sustain = expected BLOCK 5/30 × 8 × f plus shield 5 % of the elite's own max HP × 5/30:
  - T1: 1.33 + 0.5 % × ... computed exactly as 5 % × 58 = 2.9 × 5/30 = 0.48 → **1.81**.
  - T2: 1.73 + (5 % × 70 = 3.5 × 5/30 = 0.58) = **2.31**.
  - T3: 2.25 + (5 % × 89 = 4.45 × 5/30 = 0.74) = **2.99**.
  - T4: 2.93 + (5 % × 114 = 5.7 × 5/30 = 0.95) = **3.88**.
- P1 budget = (dpt − sustain) × 3.5 = 25.2 / 30.4 / 38.5 / 49.4.
- P2 has no sustain: 31.5 / 38.5 / 49 / 63.
- Sum = 56.7 / 68.9 / 87.5 / 112.4, authored **58 / 70 / 89 / 114**, in band (56–72, 68–88, 88–112, 112–144).
- P1 is about 45 % of the total, so the threshold is **0.55**. At T1 the floor is ceil(31.9) = 32, so P1 = 26 HP and P2 = 32 HP.
- Intake P1: Gladius 13/30×4 + Trident 6/30×8 = 1.73 + 1.6 = 3.3.
- Intake P2: Murmillo 7/30×7 = 1.63 + marked bump (one mark, 7/30 × 1/6 × 14 = 0.54) + Thumbs 5/30×2 = 0.33 + Gladius 5/30×3 = 0.5 + Trident 6/30×7 = 1.4 = 4.4.
- A single needle keeps P2 a clean "keep your pointer slice unmarked" exam, taught before the boss multiplies it.

**Censor arithmetic.**
- P1 budget has no sustain: 31.5 / 38.5 / 49 / 63.
- P2 sustain is Testudo 4/30 × 6 × f: 0.8 / 1.04 / 1.35 / 1.76. Budget = 28.7 / 34.9 / 44.3 / 56.8.
- Sum = 60.2 / 73.4 / 93.3 / 119.8, authored **60 / 73 / 93 / 120**, in band.
- P1 is about 52 % of the total, so the threshold is **0.48**.
- Intake P1: Gladius 12/30×4 + Thumbs 13/30×2 = 1.6 + 0.87 = 2.5. P2: Gladius 11/30×5 + Trident 6/30×8 + Thumbs 5/30×2 = 1.83 + 1.6 + 0.33 = 3.8.

**Both elites are single-needle on purpose.** A second needle doubles the player's hits and breaks the R2 elite band (Q2), so uneven needles are first taught by the boss.

---

## 5. Systems needed

| Id | System | Needed by | Data-only fallback? |
|---|---|---|---|
| **NEW-A** | **VERDICT status + effect**: `Status.VERDICT` appended (enum ints kept), `verdict_mode` MARK / CALL / deferred CALL, `verdict_map`, `max_on_wheel`, preview chip and thumb badge. Extends N8/N9. | Everything Aurelian: Crier, Dole Cart, Tax Farmer, Lictor, Vestal, Praetorian, Censor, mini-boss, boss | **No.** A reduced version is "immediate-only" through an N6 listener with a tier parameter. |
| **NEW-B** | `SlicePick.NEXT_CW` and `ALL_MARKED` (deterministic neighbor, per-turn Interest target) | Boss Dole and Interest, Tax Farmer, Censor | Partial: UNDER_POINTER only (Dole marks 1). |
| **NEW-C** | Opponent-targeted beneficial effects (Dole's `GAIN_RAM` on the player). To be verified in `effect_interpreter`. | Dole Cart, boss Dole | No. A fallback is to drop the gift (Dole becomes NULL-with-debt). |
| **N1** | Amount modes (percent shield and heal) | Vestal, Praetorian, boss | Fixed values (loses the R2 fix) |
| **N3** | Phases, parking, plus a small `on_enter_effects` extension | Elites, mini-boss, boss | None |
| **N4** | Enrage (authored boss values, HUD sand chip) | Mini-boss, boss, elites | None |
| **N5** | Boss buffs and Exploits | Boss | Always-on test config |
| **N8, N9** | ×N stacks; TIER_DOWN, OUTPUT_DOWN, corruption = RAM ×2 | Legionary, Tax Farmer, Censor, mini-boss, boss | PARASITE stand-in (poor) |
| **N11** | Pointers on any tick (uneven needles) | Boss P3 and P5 | Even needles lose the pairing rule |
| **N12** | Variable slice sizes, sub-tick map, `tick_quality` override | All layouts | Six 5-tick slots (see fallbacks) |
| **N13** | Fixed satellites | Lictor, boss buff 5 | Docking exists today; fixed behavior needs N13 |
| **N14** | Defense trio (SANDBOX negates a resolution) | Boss P5 counter | None |
| **N20** | Slice riders: `pierce`, plus NEW `multiplier_vs_status` | Praetorian P2, boss P3 and P5 | None (without it Murmillo is a plain OVERFLOW) |
| N19 | Sim metrics (turns per phase, enrage step, parked damage) | Verification | None |

**Not needed:** N6 (listeners), N7 (locks), N10 (parasite ring), N15 (rim gates). Aurelian is the cheapest of the new corporations to build because every phase is a data variation on VERDICT.

**Build order:**
1. Foundation (shared): N1 → N2 → N3 → N4 → N19, with N11, N13 and N14 in parallel.
2. NEW-A, NEW-B, NEW-C plus N8 and N9 (the verdict core).
3. The roster: Crier, Dole Cart, Legionary Drone, Tax Farmer. Test the sim at T1–T3.
4. The **Games Master** mini-boss (N12 optional).
5. Lictor (N13), Vestal, Praetorian (N20), Censor (N3).
6. N5, then the **Rostrum** (N11, N14, N20).

The Aurelian HQ netrun (G12) and the raid modifiers are separate passes.

---

## 6. Open questions

Q: **SANDBOX and riders.** Does SANDBOX (R13) negate status and verdict riders of the resolution, or only damage? This draft assumes the whole resolution, which makes it the counter to the CALL and to Pollice's mark.

Q: **Two-needle phases against the R2 bands.** A second needle doubles a phase budget, which would blow an elite or mini-boss band. Elites and the mini-boss are kept at one needle. Should the band tables grow a "+1 needle" column, or is two needles boss-only?

Q: **Enemy percent shields and caps.** Testudo Wall, Vestal and Praetorian grant SHIELD PERCENT of the enemy's own max HP. Does the enemy shield share the player's `shield_cap` = 15, or have its own cap? At 380 HP, 2 % is 7.6, so a small cap changes the sustain math.

Q: **Forced bodyguard on a boss, and the eighth building.** Is one Lictor satellite on a boss acceptable (it is budgeted in P2 and removable with Lictor Roster), or should Lictors stay mini-boss/normal-only? Does the art accept CASTRA as an eighth Exploit building, and does any 3 of the drawn five open the breach (R7)?

Q: **Perfect-hook classes and the loan.** Should the sim value the PERFECT → OVERCLOCKED loan before the Perfect-hook classes (Breaker, Ghost, Rigger) are judged under boss P4's inversion, and should Calibrated Firmware or a Daemon be guaranteed in the Aurelian reward pool?
