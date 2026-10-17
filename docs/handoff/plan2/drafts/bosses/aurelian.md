<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_019oYme7HUgRhM17CyDWCCDt, custom_id corp__aurelian; status ok; tokens in 11518 cache-write 0 cache-read 32007 out 84668; cost $0.438. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Aurelian Concord: corporation content draft

Working ids: corporation `aurelian_concord`; enemy files under `content/enemies/`. All names are placeholders and every number awaits the balance sim. Reference damage per turn is `reference_dpt_by_tier` = [9, 11, 14, 18] with 3.5 turns per phase, so one needle's phase budget is 31.5 / 38.5 / 49 / 63 HP at T1–T4. Enemy tier damage factors are [1.0, 1.3, 1.69, 2.2]. Flat amounts below are written at T1 base and scale by that factor.

---

## 1. Corporation identity summary

### 1.1 What they sell, in game terms
Aurelian sells bread and circus as a subscription: you are a *client*, and the House collects. The fight-facing idea is **consent**. Aurelian rarely hurts you directly. It *judges* you, and your own precision decides the verdict.

Compared with the existing corporations:
- Solace taxes RAM.
- Meridian locks and steers.
- Halcyon stacks statuses.
- Orbital moves the geometry.
- REBEL_CELL mirrors you.
- **Aurelian grades your landing.**

Its signature stat is the *landing tier* itself, which no other corporation reads.

### 1.2 House rule: VERDICT (specified for the build)

VERDICT is a new status on a player slice, not a new system. It uses only OVERCLOCKED, CORRUPTED, ENCRYPTED, CLEANSE and the landing tiers of GDD 2.4.

| Term | Rule |
|---|---|
| **MARK** | An Aurelian slice puts a VERDICT mark on one of your slices (the one under your pointer, or a deterministic neighbour). The mark waits. |
| **Judgement** | When a marked slice next resolves, the **read tier** decides (table below). |
| **CALL** | An immediate verdict: at the end of the resolve (statuses pass, GDD 2.2 step 3) the slice(s) under your pointer(s) are judged by *this turn's* landing. A GOOD call leaves a mark. |
| **Read tier** | The landing tier after TIER_DOWN stacks (R8). A netted GOOD reads WEAK. Sub-tick maps (R11) decide the landing. |
| **Cap** | `max_on_wheel` (default 2) per wheel. A mark beyond the cap is refused, so previews stay trivial. |
| **Defence** | ENCRYPTED absorbs the mark or the call's resulting status. CLEANSE removes a mark. SANDBOX (R13) negates the whole resolution, riders included (see Q2). |
| **Preview** | A thumb badge on the marked slice. The chip on the pointer reads `VERDICT ▲ OVERCLOCK` or `▼ CORRUPT` or `= STAYS`. It is computed from the same landing, so preview = result. |

| Read tier | Standard verdict | Result |
|---|---|---|
| PERFECT | thumbs up | slice OVERCLOCKED (1.5× on its next trigger, then it burns into CORRUPTED) |
| GOOD | no verdict | mark stays (CALL: places a mark) |
| WEAK | thumbs down | slice CORRUPTED (R9: 2× RAM for cards and nudges acting there) |

- The verdict map is **data**: `verdict_map` = {PERFECT, GOOD, WEAK} → {status, MARK or NONE}. Inversion (boss P4) is therefore a data change.
- **Why it is a real question and not a tax.**
  - Under R9, CORRUPTED deals no damage. Thumbs-up is *not a reward*: it is a loan (1.5× once, then a 2× RAM tax until cleansed).
  - Thumbs-down is an immediate tax.
  - GOOD is the cheap, safe landing, but it leaves the mark in place, and Aurelian's *Interest* (OUTPUT_DOWN stacking on marked slices) makes a lingering mark expensive.
  - So "which offset do I land on?" is never free, and there is no always-right answer.
- **Levers the player has:**
  - the free nudge;
  - paid nudges (the cost doubles on a CORRUPTED slice);
  - steering the enemy needle off the Thumbs slice by nudging the enemy wheel;
  - Cleanse and Encrypt;
  - SANDBOX;
  - a "Calibrated" Firmware (R11), which makes weak sub-ticks read GOOD.
- **The mark is skippable but not free.** You may simply never resolve a marked slice, but then that slice is dead weight on a 6-slice wheel. Interest prevents "skip it forever".
- **A GOOD landing never clears a mark.** This answers the art doc's open question 2 as "the mark stays". Bite comes from Interest, not from GOOD punishing you.

### 1.3 Tone
Grand, paternal, legal. Intents read like the corp paper: "Your patronage has been RENEWED." Latin tags are branding. The Dole slice says "FREE" and means "free, terms apply". Defeat verb: PACIFIED.

### 1.4 Exploit trio flavour
- **INTEL (the client rolls):** who is whose client; reveals the Arena's seating plan and the Lictor roster.
- **BREACH (the gate codes):** triumph-gate and Grand Stand access, plus legion engineering.
- **VIRUS (the open dole):** the ration chips are freed, and debts are wiped.

The pool is eight named Exploits (§3.4), each tagged INTEL, BREACH or VIRUS. A Grid draws five (R7). Each Exploit sits at its own special building (D5), mapped to the art's Site types.

### 1.5 Raid flavour (LEVIES)
The Levy is a legion wedge in verdigris plus a gilded float. The raid summary is a **LEVY RECEIPT**. Threat roster sketch for the pending raid pass (data-only, existing threat fields):
- **Legion wedge:** slow, high integrity, SHORTEST_TO_HOME.
- **Collectors:** fast, low integrity, HIGHEST_VALUE (they hunt Vault Terminals, in the Tax Farmer's spirit).
- **Gilded float:** a decoy-type threat that soaks asset fire.

The raid-pass hook is R1 EXPOSED. The Levy "calls a verdict" on one node, so an asset on that node is exposed. R4's ultimatum is naturally a "TRIBUTE" demand, which makes it the Schematics sink.

### 1.6 Story-path hooks (beats reveal in Exploit order; one path chosen per campaign)

| Path | Hook |
|---|---|
| The Free Bread | The dole is the leash: the ration chips are the subscription. Beats follow VIRUS finds. |
| Fixed Games | The arena outcomes are rigged by a patron. The Games Master's wheel is "calibrated". |
| Census of Clients | The Censor's ledger lists every subbie's patron. |
| Bread Riot | The wards revolt. The story raids are mobs, not legions. |
| A Patron for DISPATCH | Foreshadows DISPATCH: the ledger shows a patron with impossible timestamps. |
| The Triumph | The Rostrum is preparing a victory parade over the Cell. The finale. |

### 1.7 Where the art identity needs a game-side change

| # | Art identity says | Game-side change needed |
|---|---|---|
| 1 | VERDICT uses only existing statuses | It needs a new `Status.VERDICT` (a tier-conditional mark) and the call effect. See "NEW-A" in §5. |
| 2 | Art Q2: does GOOD keep the mark? | Decided: yes, the mark stays. Interest gives it bite. |
| 3 | Seven Site types, eight buffs | An **eighth Exploit building** is needed. Proposed: CASTRA (legion camp) for the Lictor Roster. Flag to art. |
| 4 | Enemy list Lictor, Legionary, Tax Farmer, Lanista, Vestal | Lanista is **promoted to the mini-boss** ("Games Master"; Lanista Corvina stays the event speaker). The roster adds **Crier** and **Dole Cart** and gives the Legionary a net. |
| 5 | Phase 2 "arches turn gilt, Grand Stand lights" | In this design that moment is **boss P4** (the crowd turns, verdict inverts). The hub thumb flips to thumbs-up as the tell. Sync with the boss-wheel agent. |
| 6 | "PACIFIED" loss stamp | The campaign-lost verb needs a per-corporation field (string data). |
| 7 | REBEL_CELL unlocks after every other corporation | GDD 8.5 now means all six others. Flag to the profile ladder. |
| 8 | THE TURNING GATES HQ mechanic | Belongs to the HQ netrun pass (G12). Nothing in this draft depends on it. The seating rings stay boss-wheel art only. |
| 9 | Verdigris is never used for a gain chip | The Dole's "+3 RAM" gift is a gain chip and must use the standard GAIN chip with ▲, not the corp hue. |

---

## 2. Mini-boss: THE GAMES MASTER (`games_master.tres`)

### 2.1 Identity and the one question
**Question: "Where is my safe offset right now?"**

The mini-boss is the house rule examined at depth. Each phase changes *what the safe landing is*:
- **P1:** GOOD is safe.
- **P2:** a net flips it, so PERFECT is the safe landing and GOOD hurts.
- **P3:** it judges you the same turn, and the only escape is steering.

It needs no listener, lock or ring, so it can ship early (§5).

### 2.2 Phase plan

Three phases. HP thresholds 0.66 and 0.33. Every layout sums to 30. All amounts are T1 base values.

| | **P1 Opening Bouts** (100 → 66 %) | **P2 The Net** (66 → 33 %) | **P3 Roar** (33 → 0 %) |
|---|---|---|---|
| Needles | 1, tick 0 | 1, tick 0 | 1, tick 0 |
| Layout (slice ticks) | Gladius 6 · Thumbs 4 · Testudo 5 · Trident 5 · Thumbs 4 · Null 6 | Gladius 6 · Net 5 · Trident 5 · Thumbs 4 · Testudo 4 · Gladius 6 | Gladius 5 · Thumbs 8 · Trident 5 · Gladius 5 · Testudo 4 · Null 3 |
| Gladius | SHIM 4 | SHIM 7 | SHIM 9 |
| Trident | OVERFLOW 8 | OVERFLOW 11 | OVERFLOW 13 |
| Testudo | BLOCK 6 FLAT | BLOCK 6 FLAT | BLOCK 6 FLAT |
| Thumbs | SHIM 2 + **MARK** (slice under your pointer, cap **1**) | SHIM 3 + **MARK** (cap **2**) | SHIM 4 + **CALL** (standard verdict, same resolve) |
| Net | n/a | SHIM 2 + **TIER_DOWN ×1** on the slice under your pointer (cap 2 slices) | n/a |
| Hub rule | None | **Purse:** HEAL PERCENT 1 % max HP per turn | None |
| Intake (T1 base, unmitigated) | 2.7 | 5.4 | 6.2 |
| Intake target | 2–4 | 4–6 | 6–9 |

**Intake arithmetic (tick share × amount):**
- P1: 6/30×4 + 5/30×8 + 8/30×2 = 0.8 + 1.33 + 0.53 = 2.67.
- P2: 12/30×7 + 5/30×11 + 5/30×2 + 4/30×3 = 2.8 + 1.83 + 0.33 + 0.4 = 5.4.
- P3: 10/30×9 + 5/30×13 + 8/30×4 = 3.0 + 2.17 + 1.07 = 6.2.

The 8-tick Thumbs is 27 % of the wheel, so P3 is *felt* even when its damage is small.

**Transitions:**
- `cleanse_on_enter` = NONE at both (R6), so marks and nets carry across phases.
- The P2 net and the P2 marks matter at once in P3, because a netted, marked slice is judged by the P3 CALL.
- The phase line is "Games begin" / "The Net" / "Roar".

### 2.3 Sustain and HP by tier (R2 arithmetic)

Sustain per turn = expected BLOCK absorbed (tick share × amount × tier damage factor) + hub HEAL PERCENT. Budget per phase = (reference dpt − sustain) × 3.5.

| | T1 (dpt 9) | T2 (dpt 11) | T3 (dpt 14) |
|---|---|---|---|
| P1 sustain: Testudo 5/30 × 6 × factor | 1.00 | 1.30 | 1.69 |
| P1 budget | (9−1.00)×3.5 = **28.0** | (11−1.30)×3.5 = **33.95** | (14−1.69)×3.5 = **43.1** |
| P2 sustain: Testudo 4/30×6×f + 1 % max HP | 0.80+0.86 = 1.66 | 1.04+1.06 = 2.10 | 1.35+1.32 = 2.67 |
| P2 budget | (9−1.66)×3.5 = **25.7** | (11−2.10)×3.5 = **31.2** | (14−2.67)×3.5 = **39.7** |
| P3 sustain: Testudo 4/30 × 6 × f | 0.80 | 1.04 | 1.35 |
| P3 budget | (9−0.80)×3.5 = **28.7** | (11−1.04)×3.5 = **34.9** | (14−1.35)×3.5 = **44.3** |
| Sum of budgets | 82.4 | 100.1 | 127.1 |
| R2 band (3-phase mini-boss) | 85–105 | 104–128 | 132–162 |
| **Authored `hp_by_tier`** | **86** | **106** | **132** |

- Netting sustain out leaves the sum about 3–4 % under the band floor, so I author the **band floor**.
- Floors at T1: ceil(86×0.66) = 57 and ceil(86×0.33) = 29, so the phases hold 29 / 28 / 29 HP.
- Phase lengths at the authored HP:

| Tier | P1 | P2 | P3 |
|---|---|---|---|
| T1 | 29.2/8.0 = 3.65 | 28.4/7.34 = 3.87 | 28.4/8.2 = 3.46 |
| T2 | 36.0/9.70 = 3.7 | 35.0/8.9 = 3.9 | 35.0/9.96 = 3.5 |
| T3 | 44.9/12.3 = 3.65 | 43.6/11.3 = 3.85 | 43.6/12.65 = 3.45 |

All fall in the 3–4 turn target.

- **Sustain ≤ 30 % check:** the highest is P2 at about 19 % of dpt (T1: 1.66/9 = 18 %).
- **Fallback on percent heal:** Purse is PERCENT and read from max HP, so it is never tier-scaled again (R2).

### 2.4 Enrage
The mini-boss default (R4): start turn 10, every 5 turns, +25 % additive. Expected length is 11 turns, so the first step usually lands in P3, as intended.

### 2.5 Counterplay per phase

**P1 (read the exam):**
- Land the marked slice at an offset of ±1 (GOOD) and the mark just stays.
- Land PERFECT only if you want the loan: a marked OVERFLOW that resolves twice at 1.5× is a legitimate burst plan.
- Use the free nudge to move a WEAK landing to GOOD.
- Encrypt or Cleanse the mark.
- Nudge the enemy wheel to keep the needle off Thumbs (its two Thumbs slices are 8 of 30 ticks).

**P2 (the safe offset flips).** A netted slice reads one tier lower:

| Your landing | Read tier (net ×1) | Verdict on a marked slice |
|---|---|---|
| PERFECT | GOOD | mark stays (safe) |
| GOOD | WEAK | **CORRUPTED** (and 0.5× output) |
| WEAK | WEAK | CORRUPTED |
| PERFECT (net ×2) | WEAK | CORRUPTED |

- The safe move on a netted marked slice is to land PERFECT, which costs nudges.
- Cleanse a net before you resolve the slice.
- Leave netted slices unresolved. A turn spent on an *unmarked, netted* slice is only a 0.5× hit.
- Two nets and two marks can occupy four of your six slices. The wheel feels the pressure even if you never get hit hard.

**P3 (no skipping):**
- The Thumbs CALL judges whichever slice you play, the same turn.
- Your outs are:
  - steer its needle off the 8-tick Thumbs with enemy-wheel nudges (the first is free);
  - SANDBOX the Thumbs resolve;
  - land GOOD (the CALL leaves only a mark);
  - Encrypt the slice you intend to play.
- Perfect-hook classes are tempted to land PERFECT, so they must decide whether a 1.5× loan is worth the 2× RAM tax.
- The enrage step at turn 10 gives a reason to burst.

### 2.6 Systems
- NEW-A (VERDICT status, mark and call, `verdict_map`).
- N8 (TIER_DOWN stacks).
- N9 (TIER_DOWN, OUTPUT_DOWN, CORRUPTED = RAM ×2).
- N3 (phases and parking).
- N4 (enrage).
- N12 (the 4-, 5- and 8-tick slices).

**Fallback without N12:** six 5-tick slices per phase.
- P1: Gladius · Thumbs · Testudo · Trident · Thumbs · Null (all 5).
- P2 and P3: the same six-slot template with Net or Thumbs substituted.

This keeps the exam fully intact, because the Games Master only needs to *place* marks and nets. Intake shifts slightly and the sim retunes.

**No data-only fallback** exists for the verdict itself.

### 2.7 Delta and notes
- Nothing here needs N6 (listeners), N7 (locks) or N10 (parasite ring), so it can be built first.
- It deliberately avoids the other mini-bosses' hooks:
  - Solace's Perfect counter;
  - Halcyon's stack-and-lock;
  - Meridian's latch ring;
  - Orbital's gates;
  - REBEL_CELL's mirror.
- The only overlap is Halcyon's status stacking. TIER_DOWN here is positional (it changes your *safe landing*), not a damage lever.

---

## 3. Boss: THE ROSTRUM (`rostrum.tres`, Hub: THE GRAND STAND)

### 3.1 Identity and the one question
THE ROSTRUM stages a day at the Games in five acts. **The single rule, VERDICT, is re-read every act**, and each act asks a new question about it:

| Act | Question |
|---|---|
| P1 Processional | "How do I live under a judge?" |
| P2 Free Bread | "Is the gift worth the debt?" |
| P3 Gladiators | "Which needle gets to be Perfect?" |
| P4 The Crowd Turns | "What do I do when the safe landing flips?" |
| P5 Pollice Verso | "Can I survive sudden death before the sand runs out?" |

A fight against the Rostrum is one slow lesson in landing quality, ending in a tight race against its pierce.

### 3.2 Phase plan

All layouts sum to 30. T1 base amounts; the T4 effective value is ×2.2. Perfect ×3 is `perfect_multiplier` (N20); pierce is N20.

| | **P1 Processional** | **P2 Free Bread** | **P3 Gladiators** | **P4 The Crowd Turns** | **P5 Pollice Verso** |
|---|---|---|---|---|---|
| Window (threshold) | 100 → 88 % | 88 → 74 % | 74 → 46 % | 46 → 33 % | 33 → 0 % |
| Needles | 1 @ 0 | 1 @ 0 | **2 @ 0 / 11** (uneven, R10) | 1 @ 0 | **2 @ 0 / 13** |
| Layout | Gladius 7 · Testudo 4 · Gladius 6 · Trident 5 · Null 8 | Gladius 6 · Dole 5 · Trident 5 · Testudo 4 · Dole 4 · Gladius 6 | Murmillo 7 · Net 4 · Dole 4 · Gladius 5 · Testudo 4 · Null 6 | Gladius 6 · Net 4 · Trident 5 · Testudo 4 · Dole 5 · Gladius 6 | Murmillo 7 · Gladius 4 · Pollice 5 · Net 4 · Gladius 4 · Null 6 |
| Amounts | Gladius SHIM 3; Trident OVERFLOW 6; Testudo BLOCK 6 FLAT | Gladius 4; Trident 8; Testudo BLOCK 6 | Murmillo OVERFLOW 7 (**×3 on Perfect**); Gladius 3; Net SHIM 2 + TIER_DOWN ×1; Testudo BLOCK 6 | Gladius 4; Trident 9; Net 2 + TIER_DOWN ×1; Testudo BLOCK 6 | Murmillo 7 (×3 on Perfect); Gladius 3; **Pollice OVERFLOW 7, pierce**; Net 2 + TIER_DOWN ×1 |
| Dole (gift, debt) | n/a | Gift **+3 RAM** to you, and **2 MARKS** (pointer slice + next clockwise) | same | same | n/a |
| Hub rule | **Grand Stand CALL** (standard) + Herald HEAL PERCENT 0.5 % | CALL + **Interest** | CALL + Interest | **CALL INVERTED** + Interest + Herald HEAL PERCENT 0.5 % | CALL (standard again) |
| Testudo Wall (buff) | + SHIELD PERCENT 2 % | same | same | same | no Testudo |
| Intake T4 (unmitigated) | 5.1 | 6.4 | 12.6 | 7.4 | 19.1 |
| Intake target T4 | 3–6 | 5–8 | 9–13 | 7–10 | 15–20 (before enrage) |

**What the hub rules do:**
- **CALL:** after each resolve, the slice(s) under your pointer(s) are judged by this turn's landing (§1.2). It happens in the statuses pass.
- **Interest:** at the start of each of your turns, every VERDICT-marked slice gains OUTPUT_DOWN ×1 (cap ×3), so a mark becomes −25 %, −50 %, −75 % of that slice's output over time. This is the "bill that grows". Marks are the cost of the Dole and of GOOD landings.
- **INVERTED:** `verdict_map` becomes PERFECT → CORRUPTED, WEAK → OVERCLOCKED, GOOD → mark. The crowd turns: now the *stumble* is rewarded and precision is punished. A WEAK landing halves the output *now*, but arms 1.5× next time.
- **Intermission Debt (buff, §3.4):** each phase change judges every mark as a WEAK landing, so it becomes CORRUPTED.

**Intake arithmetic (tick share × amount × 2.2):**
- P1: (13/30×3 + 5/30×6) × 2.2 = (1.3+1.0) × 2.2 = 5.1.
- P2: (12/30×4 + 5/30×8) × 2.2 = (1.6+1.33) × 2.2 = 6.4.
- P3 (per needle): Murmillo 7/30×7 = 1.63, plus the Perfect bump 1/30×(21−7) = 0.47, plus Net 4/30×2 = 0.27, plus Gladius 5/30×3 = 0.5, which gives 2.87. Two needles × 2.2 = 12.6.
- P4: (12/30×4 + 5/30×9 + 4/30×2) × 2.2 = (1.6+1.5+0.27) × 2.2 = 7.4.
- P5 (per needle): Murmillo 1.63+0.47, Gladius 8/30×3 = 0.8, Pollice 5/30×7 = 1.17, Net 0.27, which gives 4.34. Two needles × 2.2 = 19.1.

**Needle pairing (uneven needles).** Rotation `r` moves both needles; positions are (r, r+gap).

P3, gap 11. Murmillo [0–6], Net [7–10], Dole [11–14], Gladius [15–19], Testudo [20–23], Null [24–29]. Murmillo is 7 ticks (WWGPGWW), so its Perfect tick is 3.

| r | Needle A | Needle B |
|---|---|---|
| 2 | tick 2: Murmillo GOOD | tick 13: Dole GOOD |
| 3 | tick 3: **Murmillo PERFECT (×3)** | tick 14: Dole WEAK edge |
| 4 | tick 4: Murmillo GOOD | tick 15: Gladius WEAK edge |

P5, gap 13. Murmillo [0–6], Gladius [7–10], Pollice [11–15] (P at 13), Net [16–19], Gladius [20–23], Null [24–29].

| r | Needle A | Needle B |
|---|---|---|
| 0 | tick 0: Murmillo WEAK (0.5×) | tick 13: **Pollice centre** |
| 3 | tick 3: **Murmillo PERFECT** | tick 16: Net WEAK edge |

The gaps are chosen so the worst slice at one needle always pairs with a half-power edge at the other. The player picks which needle to deny, not whether both are safe.

**Transitions (R6):**
- `cleanse_on_enter` = NONE everywhere. Statuses carry across phases and the status remap is the standard one.
- Each transition plays a line and reveals the new layout.
- P3 enters via MULTIPLY (a second needle at 0 / 11).
- P5 enters via MULTIPLY (0 / 13) and removes Testudo and Herald.
- P4 changes `hub_override` to the inverted map. This is the only phase where the verdict flips.
- If marks exist at P4 entry (Intermission Debt countered), they are judged by the *inverted* map. This is deliberate: clear your marks before the P3 floor.

### 3.3 Sustain, intake and the HP budget (R2 arithmetic)

Boss budget per phase = (needles × dpt_T4 − sustain) × 3.5, with dpt_T4 = 18 and 3.5 turns per phase. Sustain per needle is expected BLOCK absorbed (4/30 × 6 × 2.2 = 1.76) plus Wall shield (4/30 × 2 % max HP) plus hub heal. Authored at max HP = 380.

| Phase | Needles | Sustain per turn | Budget (needles×18 − sustain) × 3.5 |
|---|---|---|---|
| P1 | 1 | heal 0.5 % = 1.95; Testudo 1.76; Wall (2 % = 7.6, ×4/30) 1.01 → **4.7** | (18 − 4.7) × 3.5 = **46.5** |
| P2 | 1 | Testudo 1.76 + Wall 1.01 = **2.8** | (18 − 2.8) × 3.5 = **53.2** |
| P3 | 2 | (1.76 + 1.01) × 2 = **5.5** | (36 − 5.5) × 3.5 = **106.8** |
| P4 | 1 | heal 1.95 + Testudo 1.76 + Wall 1.01 = **4.7** | (18 − 4.7) × 3.5 = **46.5** |
| P5 | 2 | **0** (no defence, no heal) | 36 × 3.5 = **126** |
| **Sum** | | | **379** |

- Sustain stays ≤ 30 % of each phase's reference damage: P1 and P4 are 4.7/18 = 26 %, and P2 is 16 %.
- **`hp_bands`** (ICE boss-strength zone ceiling → HP): **≤ 1.00 → 380 · ≤ 1.15 → 420 · ≤ 1.30 → 460 · > 1.30 → 510** (the same +10 / +21 / +34 % ladder as the Genome Core's 300 / 330 / 360 / 400).
- **Thresholds:** 0.88 / 0.74 / 0.46 / 0.33.
- At 380 the floors are ceil(380×0.88) = 335, ceil(0.74×380) = 282, ceil(0.46×380) = 175 and ceil(0.33×380) = 126.
- Phase HP at 380 and phase length:

| Phase | HP | Turns |
|---|---|---|
| P1 | 380 − 335 = 45 | 45/13.3 = 3.4 |
| P2 | 335 − 282 = 53 | 53/15.2 = 3.5 |
| P3 | 282 − 175 = 107 | 107/30.5 = 3.5 |
| P4 | 175 − 126 = 49 | 49/13.3 = 3.7 |
| P5 | 126 | 126/36 = 3.5 |
| **Total** | 380 | **17.6** |

- 17.6 turns sits inside R1's 12–20.
- Percent amounts read the real max HP (higher bands run slightly longer; the sim retunes).
- Budgets assume **all buffs active**. Each Exploit makes the fight shorter, which is the intended reward.
- The Lictor satellites (buff 5) are **not** in the phase budget. They are an optional detour: killing one costs about 1.1 turns, and it is only paid by players who attack a guarded slice.
- A **guarded slice** is any Gladius when the Lictors are on, so the guarded attack is the cheap one.

### 3.4 Buffs and their Exploits (8; a Grid draws 5; `min_exploits_for_breach` = 3)

| # | Buff | Effect | Counter Exploit (type) → building | Signature |
|---|---|---|---|---|
| 1 | **Grand Stand** | The hub CALLs a verdict every turn (the house rule). | **Gate Codes** (BREACH) → TOLL GATE: the hub only MARKs (deferred judgement, no immediate call) | **yes** |
| 2 | **Interest** | Marks grow OUTPUT_DOWN each turn (P2+). | **Debt Relief** (VIRUS) → ANNONA: marks stay marks, no growth | **yes** |
| 3 | **Free Bread** | The Dole's gift comes with 2 marks. | **Open Dole** (VIRUS) → DOLE: the Dole gives RAM only | |
| 4 | **Twin Gladiators** | The second needle in P3 and P5. | **Arena Plan** (INTEL) → LUDUS: one needle | |
| 5 | **Lictors** | Two fixed fasces satellites on the Gladius slices (P2–P4) | **Lictor Roster** (INTEL) → CASTRA (new): no Lictors | |
| 6 | **Testudo Wall** | Testudo slices also gain SHIELD PERCENT 2 % (enemy percent shield; own cap, see Q4). | **Siege Wright** (BREACH) → AQUEDUCT: BLOCK only | |
| 7 | **Intermission Debt** | At every phase change, all your marks are judged as WEAK (CORRUPTED). | **Amnesty** (VIRUS) → ATRIUM: marks persist unjudged | **yes** |
| 8 | **Sudden Death** | Pollice (P5) pierces BLOCK and SHIELD. | **Appeal** (BREACH) → CURIA: Pollice is a plain OVERFLOW | |

**Distribution:** INTEL 2, BREACH 3, VIRUS 3.

**Counters degrade the fight, they never delete a phase.**
- If *Gate Codes* is used, P1 still marks, and P2 and P4's Interest still bites.
- If *Arena Plan* is used, P3 and P5 are one needle: shorter, with the same questions.
- If *Debt Relief* is used, P2 loses its bill but keeps the Dole and Net choices.

### 3.5 Enrage
**Authored**, not the boss default:
- Start turn 12, every 4 turns, +25 % additive (×1.25, ×1.5, …).
- It raises damage only. The HUD shows a falling-sand chip ("the Games are running long").

**Why not the default (10 / 5):** P1–P3 end at about turn 10.5, so the default's first step would hit at the P3 → P4 boundary for an average player. 12 / 4 puts the first step inside P4 and the second at the start of P5, so a typical 17.6-turn fight sees one or two steps. A slow route (turn 20) sees three.

### 3.6 Counterplay per phase

**P1 Processional**
- Land GOOD on slices you are not ready to pay for.
- Land PERFECT on a damage slice only if you will replay it for the 1.5× before the burn-out.
- Cleanse or Encrypt a slice you intend to reuse.
- Hub Breach (a card) turns the CALL off for one turn, so you can land PERFECT for free.
- P1 is short (45 HP). Burst through it.

**P2 Free Bread**
- Interest makes a mark a ticking bill, so the Dole is a decision:
  - Let the needle land on Dole and the boss does nothing, but you pay two marks and gain +3 RAM.
  - Or nudge the enemy wheel to move it off Dole at one RAM.
- Clear marks by landing PERFECT or WEAK, or by Cleanse.
- Avoid resolving marked slices unprepared.
- Lictors guard the cheap slice: steer rather than kill.

**P3 Gladiators**
- Two needles mean your hits land twice, so race.
- **Deny the Perfect.** Nudge the enemy wheel by 1 so that Murmillo reads GOOD (×1) instead of PERFECT (×3: 46 damage at T4). That nudge also moves needle B; check the pairing table.
- Nets plus marks recreate the mini-boss's P2 puzzle, doubled.
- **Clear your marks before the P3 floor.** Intermission Debt fires at the transition.

**P4 The Crowd Turns**
- The safe landing flips: a WEAK landing now OVERCLOCKS, PERFECT CORRUPTS.
- Pre-plan with the sub-tick map: a 4-tick slice (WGGW) now has a 2-tick "thumbs-up" edge and no Perfect to trip over.
- A Net helps: GOOD under a net reads WEAK, which is now thumbs-up.
- Perfect-hook classes should either avoid the hook or use Cleanse. Calibrated Firmware turns edge WEAKs into GOOD (the mark stays), so it protects but doesn't reward.
- Marks left from P3 are judged by the inverted map.

**P5 Pollice Verso**
- No boss defence, so every hit lands.
- Pierce skips BLOCK and SHIELD. Your answers are **SANDBOX** (negates the whole resolution), **steering** the needle off Pollice, or the Appeal Exploit.
- The gap-13 pairing means that when needle B sits on Pollice, needle A is on a WEAK Murmillo edge (0.5×).
- Finish before the second enrage step (turn 16–20).

### 3.7 Systems
- NEW-A (the VERDICT status, CALL, INVERTED map).
- NEW-B: SlicePick `NEXT_CW` and `ALL_MARKED`.
- NEW-C: opponent-targeted beneficial effects (the Dole gift, `GAIN_RAM` targeting the player).
- N1 (percent shield and heal).
- N3 (phases, parking, plus a small `on_enter_effects` extension for Intermission Debt).
- N4 (authored enrage chip).
- N5 (buffs and Exploits).
- N8, N9 (OUTPUT_DOWN, TIER_DOWN stacks).
- N11 (uneven needles).
- N12 (the 4-, 5- and 7-tick slices).
- N13 (Lictors).
- N14 (SANDBOX).
- N20 (`perfect_multiplier`, `pierce`).

**Fallbacks:**
- Without N12, use 5-tick slices:
  - P1 (6 slots): Gladius, Testudo, Gladius, Trident, Null, Null.
  - P3, P5 (6 slots): Murmillo, Net, Dole, Gladius, Testudo, Null (P5 swaps in Pollice, Net, Gladius).
  - Murmillo's Perfect is then the normal centre tick. Intake and pairing tables must be redone.
- Without N5, the buffs are always on, as an "all-countered" test configuration.
- No fallback exists for the CALL itself.

### 3.8 Delta and notes
- It shares a ramp skeleton with the Genome Core: a mild start, a second needle, no defence at the end.
- It differs in that the ramp is **one rule being re-read** (VERDICT), not a new slice set per phase. It needs no listeners.
- P5's pierce and no-defence finish echoes Genome P4, but the answer here is SANDBOX and steering, not cleansing.
- The Free Bread opponent-targeted gift is the only new effect-target class (NEW-C).

---

## 4. Enemy roster sketch (6 normals, 2 elites)

All normals are 1 phase, 1 needle, no threshold. Wheel sketches list slice name and ticks (sum 30); all amounts are T1 base. R2 bands: normal 28–36 / 34–44 / 44–56 / 56–70 for T1–T4; elite 56–72 / 68–88 / 88–112 / 112–144.

**Teaching order.** The roster teaches the house rule in this sequence:
1. **Crier (L1–2):** the mark and the "land GOOD" answer.
2. **Dole Cart (L1–2):** gift versus debt.
3. **Legionary Drone (L3):** TIER_DOWN shifts the safe offset.
4. **Tax Farmer (L3–4):** Interest on marks.
5. **Lictor (L4–5):** a fixed bodyguard.
6. **Vestal Firewall (L5–6):** the immediate CALL.
7. **Praetorian (elite, L4–6):** denying a Perfect.
8. **Censor (elite, L5–6):** a mark flips meaning at the phase floor.

Everything the Games Master uses (marks, nets, calls) has been seen by the time the final Rack arrives.

### 4.1 Normals

| Working name | Class | Layer role | The one question | Wheel sketch | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|---|
| **Crier** | Normal | Teach L1–2 | "What does a mark want from me?" Land GOOD, or keep that slice out of play. | Gladius 6 (3) · Thumbs 5 (1 + MARK, cap 1) · Gladius 6 (3) · Null 7 · Thumbs 6 | **30 / 37 / 47 / 60** | NEW-A, N12 (fallback: six 5-tick slices) |
| **Dole Cart** | Normal | Teach L1–2 | "Free turn now, debt later?" | Dole 8 (+2 RAM to you; MARK ×1 on pointer slice, cap 1) · Gladius 6 (4) · Testudo 5 (BLOCK 5) · Gladius 6 (4) · Null 5 | **29 / 35 / 44 / 57** | NEW-A, NEW-C |
| **Legionary Drone** | Normal | Teach L3 | "Under a net, which landing is actually safe?" | Gladius 6 (4) · Net 6 (1 + TIER_DOWN ×1, cap 2) · Gladius 5 (4) · Testudo 4 (BLOCK 6) · Trident 5 (7) · Null 4 | **29 / 35 / 44 / 57** | N8, N9, N12 |
| **Tax Farmer** | Normal | Teach L3–4 | "How long can I carry this mark?" | Hub: Interest (OUTPUT_DOWN ×1 per marked slice per turn, cap ×2). Thumbs 6 (1 + MARK, cap 2) · Gladius 7 (5) · Null 5 · Gladius 7 (5) · Thumbs 5 | **31 / 38 / 48 / 62** | NEW-A, NEW-B (`ALL_MARKED`), N8, N9 |
| **Lictor** | Normal | Teach L4–5 | "The guarded slice is the dangerous one. Kill the rod, or steer away?" | Host: Gladius 8 (3) · Trident 6 (6, **guarded**) · Testudo 5 (BLOCK 5) · Gladius 6 (3) · Thumbs 5 (1 + MARK) with a **fixed Fasces satellite** docked on the Trident (2 slices × 15 ticks: Rod SHIM 2, Bundle BLOCK 3) | **29 / 35 / 44 / 57** (host + satellite: **21+8 / 25+10 / 32+12 / 42+15**) | N13, NEW-A |
| **Vestal Firewall** | Normal | Pressure L5–6 | "Keep the needle off the Pyre, or land safe, because it judges you now." | Hub: Sacred Flame (SHIELD PERCENT 4 % max HP at turn start). Pyre 8 (3 + **CALL**) · Gladius 7 (4) · Trident 5 (7) · Null 5 · Gladius 5 (4) | **28 / 34 / 44 / 56** | NEW-A, N1 |

**Arithmetic and intake (T1 base).** Reference budget = dpt × 3.5 = 31.5 / 38.5 / 49 / 63; sustain is netted out.

- **Crier (intake 1.6, no sustain).**
  - Intake: 12/30×3 + 11/30×1 = 1.2 + 0.37.
  - HP is about 5 % under budget for a teach enemy: 30 / 37 / 47 / 60.
- **Dole Cart (intake 1.6).**
  - Sustain is Testudo 5/30 × 5 × f: 0.83 / 1.08 / 1.41 / 1.83.
  - HP = (dpt − sustain) × 3.5: 28.6 / 34.7 / 44.1 / 56.6, authored 29 / 35 / 44 / 57.
  - Dole is 8 ticks (27 % of turns), so about a quarter of its turns are free, which is why intake is low.
- **Legionary Drone (intake 2.8).**
  - Intake: 11/30×4 + 5/30×7 + 6/30×1 = 1.47 + 1.17 + 0.2.
  - Sustain is Testudo 4/30 × 6 × f: 0.8 / 1.04 / 1.35 / 1.76.
  - HP = 28.7 / 34.9 / 44.3 / 56.8, authored 29 / 35 / 44 / 57.
- **Tax Farmer (intake 2.7, no sustain).**
  - Intake: 14/30×5 + 11/30×1 = 2.33 + 0.37.
  - HP 31 / 38 / 48 / 62 against budget 31.5 / 38.5 / 49 / 63.
  - Interest cap ×2 means a mark costs at most −50 % output.
  - Distinct from Halcyon's Citation: Interest only grows on **marked** slices, so it is a clock on a decision, not a stack on your wheel.
- **Lictor (intake 3.8).**
  - Intake: host 14/30×3 + 6/30×6 + 5/30×1 = 1.4 + 1.2 + 0.17, plus the Rod's average 1.0.
  - Sustain is Testudo 5/30×5×f: 0.83 / 1.08 / 1.41 / 1.83.
  - Total budget host + satellite = (dpt − sustain) × 3.5 = 28.6 / 34.7 / 44.1 / 56.6.
  - Satellite HP 8 / 10 / 12 / 15, so host = 21 / 25 / 32 / 42.
  - The Trident is the 6-tick guarded slice: when the needle sits on it, your attack hits the rod instead of the host.
- **Vestal Firewall (intake 3.6).**
  - Intake: 8/30×3 + 12/30×4 + 5/30×7 = 0.8 + 1.6 + 1.17.
  - Sustain is the Flame shield: 4 % × ~31 HP = 1.2 per turn at T1, scaling 1.5 / 1.9 / 2.4. Budget = 27.3 / 33.3 / 42.4 / 54.6.
  - Authored at the band floor 28 / 34 / 44 / 56, which is 3.5–3.7 turns.
  - Percent shield reads own max HP, never rescaled (R2).

**Distinctness from the other corporations:**
- Not billing-based, so no overlap with Solace's Billing Daemon or Collections Agent.
- The Tax Farmer is not a RAM drain, unlike Meridian's Tariff Collector.
- The net and the mark are not Halcyon's Citation.
- The Lictor uses fixed satellites like Solace's mini-boss, but guards the *dangerous* slice.
- No enemy uses spin resistance, orbit or mirroring.

**Fallbacks without the new systems:**
- Without N8/N9 the Legionary can use today's PARASITE status, which is a halve rather than a tier shift. It would change the question, so it is not recommended.
- Everything with a mark or call needs NEW-A.

### 4.2 Elites

Both elites have 2 phases, 1 needle each, and use the elite enrage default (start turn 8, every 5, +25 %).

| Working name | Class | Layer role | The one question | Phase plan | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|---|
| **Praetorian** | Elite | Pressure L4–6 | P1 "Starve the wall" (steer off Testudo; block and shield refill only there). P2 "Deny the Perfect" (Murmillo ×3). | **P1 Shield Wall** (100 → 55 %): Testudo 5 (BLOCK 8 + SHIELD PERCENT 5 %) · Gladius 7 (4) · Trident 6 (8) · Null 6 · Gladius 6 (4). **P2 Charge** (55 → 0 %): Murmillo 7 (OVERFLOW 7, **×3 on Perfect**) · Gladius 5 (3) · Gladius 5 (3) · Null 7 · Trident 6 (7). Needle at 0 in both. | **58 / 70 / 89 / 114** | N1, N3, N12, N20 |
| **Censor** | Elite | Pressure L5–6 | P1 "Audit": marks and Interest, carry them or clear them? P2 "Redraw": marks you carried flip meaning (previews boss P4). | **P1 Audit** (100 → 48 %): hub Interest (OUTPUT_DOWN per mark per turn, cap ×3). Thumbs 6 (2 + MARK, cap 2) · Gladius 6 (4) · Null 5 · Gladius 6 (4) · Thumbs 7. **P2 Redraw** (48 → 0 %): `verdict_map` becomes INVERTED. Thumbs 5 (2 + MARK) · Gladius 6 (5) · Trident 6 (8) · Gladius 5 (5) · Testudo 4 (BLOCK 6) · Null 4. Needle at 0 in both. | **60 / 73 / 93 / 120** | NEW-A, NEW-B, N3, N8, N9, N12 |

**Praetorian arithmetic.**
- P1 sustain is expected BLOCK 5/30 × 8 × f plus shield 5 % × HP × 5/30:
  - T1 1.33 + 0.25 = 1.6; T2 1.73 + 0.29 = 2.0; T3 2.25 + 0.37 = 2.6; T4 2.9 + 0.46 = 3.4.
- P1 budget = (dpt − sustain) × 3.5 = 25.9 / 31.5 / 39.9 / 51.
- P2 has no sustain: 31.5 / 38.5 / 49 / 63.
- Sum = 57.4 / 70 / 88.9 / 114, authored **58 / 70 / 89 / 114**, in band (56–72, 68–88, 88–112, 112–144).
- P1 is about 45 % of the total, so the threshold is **0.55**.
- Intake P1: Gladius 13/30×4 + Trident 6/30×8 = 1.73 + 1.6 = 3.3. P2: Murmillo 1.63 + Perfect bump 0.47 + Gladius 10/30×3 + Trident 6/30×7 = 4.5.
- A single needle means the second phase is a pure Perfect-denial exam, with no double hit.

**Censor arithmetic.**
- P1 budget has no sustain: 31.5 / 38.5 / 49 / 63.
- P2 sustain is Testudo 4/30 × 6 × f: 0.8 / 1.04 / 1.35 / 1.76. Budget = 28.7 / 34.9 / 44.3 / 56.8.
- Sum = 60.2 / 73.4 / 93.3 / 119.8, authored **60 / 73 / 93 / 120**, in band.
- P1 is about 52 % of the total, so the threshold is **0.48**.
- Intake P1: Gladius 12/30×4 + Thumbs 13/30×2 = 1.6 + 0.87 = 2.5. P2: Gladius 11/30×5 + Trident 6/30×8 + Thumbs 5/30×2 = 1.83 + 1.6 + 0.33 = 3.8.

**Both elites are single-needle on purpose.** A second needle doubles the player's hits and breaks the R2 elite band (see Q3), so uneven needles are first taught by the boss.

---

## 5. Systems needed

| Id | System | Needed by | Data-only fallback? |
|---|---|---|---|
| **NEW-A** | **VERDICT status + effect**: `Status.VERDICT` appended (enum ints kept), `verdict_mode` MARK / CALL, `verdict_map`, `max_on_wheel`, preview chip and thumb badge. Extends N8/N9. | Everything Aurelian: Crier, Dole Cart, Tax Farmer, Lictor (mark slice), Vestal, Censor, mini-boss, boss | **No.** A reduced version is "immediate-only" through an N6 listener with a tier parameter. |
| **NEW-B** | `SlicePick.NEXT_CW` and `ALL_MARKED` (deterministic neighbour, per-turn Interest target) | Dole (boss), Tax Farmer, Censor, boss Interest | Partial: UNDER_POINTER only (Dole marks 1). |
| **NEW-C** | Opponent-targeted beneficial effects (Dole's `GAIN_RAM` on the player). To be verified in `effect_interpreter`. | Dole Cart, boss Dole | No. A fallback is to drop the gift (Dole becomes a pure NULL-with-debt). |
| **N1** | Amount modes (percent shield and heal) | Vestal, Praetorian, boss | Fixed values (loses the R2 fix) |
| **N3** | Phases, parking, plus a small `on_enter_effects` extension | Elites, mini-boss, boss | None |
| **N4** | Enrage (the authored boss values, HUD sand chip) | Mini-boss, boss, elites | None |
| **N5** | Boss buffs and Exploits | Boss | Always-on test config |
| **N8, N9** | ×N stacks; TIER_DOWN, OUTPUT_DOWN, corruption = RAM ×2 | Legionary, Tax Farmer, Censor, mini-boss, boss | PARASITE stand-in (poor) |
| **N11** | Pointers on any tick (uneven needles) | Boss P3 and P5 | Even needles lose the Perfect denial |
| **N12** | Variable slice sizes and sub-tick map | All layouts | Six 5-tick slices (see fallbacks) |
| **N13** | Fixed satellites | Lictor, boss buff 5 | Docking exists today; fixed behaviour needs N13 |
| **N14** | Defence trio (SANDBOX negates a resolution) | Boss P5 counter | None |
| **N20** | Slice riders (`perfect_multiplier`, `pierce`) | Praetorian, boss | None |
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

Q: **SANDBOX and riders.** Does SANDBOX (R13) negate status and verdict riders of the resolution, or only damage? This draft assumes it negates the whole resolution, riders included, which makes it the counter to the CALL. Confirm.

Q: **Perfect-hook classes under the inverted verdict (boss P4).** Breaker, Ghost and Rigger hooks all trigger on PERFECT, which P4 punishes. Is that acceptable, or should Calibrated Firmware / a Daemon be guaranteed in the Aurelian reward pool?

Q: **Two-needle phases against the R2 bands.** A phase with two needles doubles the budget (P3 and P5 here, roughly 2× 3.5 × dpt), which would blow an elite or mini-boss band. I kept elites and the mini-boss at one needle. Should the band tables grow a "+1 needle" column, or is two needles boss-only?

Q: **Enemy percent shields and caps.** Testudo Wall and Vestal grant SHIELD PERCENT of the enemy's own max HP. Does the enemy shield share the player's `shield_cap` = 15, or have its own cap? At 380 HP, 2 % is 7.6, so a small cap changes the sustain math.

Q: **Exploit pool versus the three typed gates.** This draft tags 8 Exploits as INTEL / BREACH / VIRUS and gives each a building, including a new CASTRA. With 5 drawn per Grid, does any 3 open the breach (R7), and may the art add an eighth Site type?

Q: **Dole gift and scaling.** The gift is unscaled RAM (+3 at every tier) so it needs no R2 treatment. Is a flat +3 right, or should the Dole gift also scale with ICE so it stays tempting at high tiers?
