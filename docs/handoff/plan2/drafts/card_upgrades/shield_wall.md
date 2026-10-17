<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__shield_wall; status ok; tokens in 5107 cache-write 0 cache-read 32585 out 1139; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: shield_wall

**Level count:** one + version is enough. The card is a simple stat stick, so a second level would only be a bigger number.

## 1. Role
Cheap, neutral, lingering defense: it puts SHIELD up for later turns, which makes it the way to bank safety under the `shield_cap` of 15.

## 2. Upgraded card: Shield Wall+
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.3 (55 → ~72, rounded to 70).
- **Text:** "Gain 6 shield. If you have no shield, gain 8 instead." Both lines are replaced by the simpler version below.
- **Chosen version (decisive):** "Gain 7 shield." This is a plain bigger number. I rejected the conditional text because it adds tooltip and preview work for a 1 RAM card.
- **Effect list (one EffectData):**
  - type GAIN_SHIELD (value 2)
  - target SELF (0)
  - amount 7
  - amount_mode FLAT (the default; nothing is percent here)
  - ring_scope OUTER (ignored), status NONE, duration_turns 0
- **Exhaust:** false.
- **wheel_target:** OWN (0).

**Why 7 and not 8 or more:** the cap is 15. Two plays of the base card give 8; two plays of the + give 14, which is nearly a full cap. Three plays of the base give 12, so the + saves one card play per 14 shield without ever exceeding the cap. At 8 per play, two plays would reach 16 and waste 1 against the cap, so 7 keeps the numbers clean.

**Dominance:** the + version strictly dominates at the same RAM, but it costs more Cycles (~70 against 55). That is the trade: you pay in the shop. A sidegrade (cheaper, smaller) would only blur the "bigger number" role, so I don't offer one.

## 3. Interplay
- **Defense trio (R13):** SHIELD lingers, and Pierce ignores it. Against the Genome Core P4 (pierce Adrenaline), the extra shield is bypassed, so the + gains nothing there. It still matters in P2 against IV chip damage, where many small hits are absorbed.
- **Corruption (R9):** a card played while the pointer reads a CORRUPTED slice costs 2× RAM. The card's low cost of 1 makes the double cost (2) tolerable. This is a good card to play through corruption.

## 4. Data
Changes against the current .tres:
- `amount = 4` → `7`
- `ram_cost` stays 1
- `cycle_cost = 55` → `70`
- `description` = "Gain 7 shield."
- `id` = `shield_wall_plus`, `display_name` = "Shield Wall+"

No new effect or system is needed. The R13 rename (SHIELD) is display only (N14); the `SANDBOX` enum int stays. A `+` flag or upgrade link on `CardData` belongs to the card-upgrade pass, not to this card.

## 5. Questions
Q: Should the + version also raise `shield_cap` for the turn, or is the cap of 15 sacred, which would make the + a pure number bump?
Q: Does an upgrade multiply Cycle cost by a fixed ×1.3 for every card, or is it authored per card as here?
