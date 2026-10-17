<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__tethys; status ok; tokens in 10217 cache-write 0 cache-read 32585 out 2084; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/tethys

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 node arithmetic / layer map.** The stated total is "3+3+1+3+4+4+3+3+3+2+1 = 30". The real sum is 30, but the table says L4 = 3, L5 = 4, L6 = 4, L7 = 3, L8–L9 = 3, 3, L10 = 2, L11 = 1. The act table lists layers 8–11 as "3, 3, 2, 1" (one slot for layers 8–11 missing), while the layer map and the Pressure text assume four layers below 7. Act IV sums to 9, not the 3+3+3+2+1 = 12 implied by the map. Pick one count.
2. **BLOCKER, §3.4 Pressure.** "Starting at 0 at layer 8", "11 at layer 10, 10 at layer 11 for a base of 12". Pressure of 2 at layer 10 gives −1, so 11; layer 11 gives Pressure 3, so −1 (also 11). The −1 per 2 Pressure rule does not produce 10. The text also says "below layer 7" but starts at layer 8. Max RAM 12 is also not the base for every class (Rigger gets +1).
3. **BLOCKER, §3.3 and §4, R1.** The Lockkeeper is "a 4-turn fight, 2 phases", yet R1 gives an elite 6–8 turns (2 phases × 3–4). A 4-turn limit contradicts 3–4 turns per phase. It is also tagged "mini-fight" while the elite count lists only two elites. No HP is given anywhere, with no R2 budget arithmetic.
4. **MAJOR, §3.1 Head.** Dry LOW removes "1 free nudge", which is a nonstandard stat change. It is also unclear whether HIGH closes nodes while the Exploit-free route has no opening. The soft-lock guard says "Nodes can never be closed at both HIGH and FALLING", but FALLING is shown open anyway, so the guard is redundant. The Surge "respin their first Needle" is a random-event respin that wipes the preview, and the hash derivation is unnecessary. The draft's own fallback ("combat stream") conflicts with the preview-equals-result claim.
5. **MAJOR, §5 HP budget.** The player takes 90–110 HP of loss against a pool of 55–65, with only about 55–65 HP of healing. That is 145–175 total supply against 90–110 loss. The text then says skipping rests leaves the player at 30–40 %, which doesn't follow. The Hub heal (12–15) is counted under both "Hub" and "pay Pressure for heal". Decompression is promised at 1–2 nodes but the heal budget assumes two.
6. **MAJOR, §3.2 and §2 Sluice.** "Layer 2 (two of the three nodes) and one node in layer 6" is two puzzles on the map, but §4 states "2 (layers 2 and 6)" while three exist. The Divert mark on "next layer" could target layer 3, which has no lower nodes.
7. **MAJOR, §4 Virus.** "The boss's first phase starts with its buff list down by one" duplicates R7 (an Exploit turns a buff off). Marking the Head step FALLING breaks the "pure function of count" determinism claim in §3.1.
8. **MAJOR, §6 Ballast and Dry run.** The Daemon has a one-sentence placeholder with no cap rule check. "Pressure under 4" is the maximum reachable value, so the condition is nearly always true.
9. **NIT, §3.1 and §3.2.** Tide tick vs Wait action costs "1 Heat" are inconsistent with "HQ run does not raise Heat from the Head".
10. **NIT, §2.** Some references use "AD rule (8.4)" and "2026-10-16 Q2 ruling", which do not exist in the supplied sources.

## Concrete fixes

- **Fix 1:** Act IV nodes: L8 = 3, L9 = 3, L10 = 2, L11 = 1 (9 nodes). Total = 3+3+1+3+4+4+3+9 = 30. Rewrite the act table as "IV: layers 8–11, 3 / 3 / 2 / 1" and add "Acts I–III = 21, Act IV = 9".
- **Fix 2:** "Pressure starts at 0 on layer 8 and gains 1 per layer. Max RAM −1 per Pressure above 1 (cap at −2): layers 8–9 = 0 or −0, layer 10 = −1, layer 11 = −2. Applies to the boss too."
- **Fix 3:** The Lockkeeper becomes a 2-phase elite, 6–8 turns, T4 HP 112–144 (R2 elite band). The clock is "the Head steps at the end of turn 4 and again at turn 8; winning by turn 6 picks the Head".
- **Fix 4:** Remove the LOW nudge penalty (replace it with "LOW: cleared nodes cost no tide tick"). Make Surge "enemy wheel starts the fight with its needle at a fixed tick shown on the node (no respin)."
- **Fix 5:** Re-state the budget: loss 70–85 HP, healing 2 rests × 18 + 10 event + 12 Hub = 58, with the remainder absorbed by class HP 55–65 (supply 113–123).
- **Fix 6:** Sluice count 3 (L2 ×2, L6 ×1). Divert may only target a LOWER node on layers 8–9.

## Keep

- The Head as a single legible run-wide clock tied to the art's gauge, with a clean per-frame art hook table.
- Descent with one-way links makes Act IV feel committed, with the Exploit payoffs themed per key.
- A data-only fallback for every new system.

## Q:

Q: Should Head advance be per completed node or per layer?
Q: Does Pressure still add value alongside R9 corruption RAM doubling?
Q: Should Exploit payoffs replace or sit on the Grid gates?
