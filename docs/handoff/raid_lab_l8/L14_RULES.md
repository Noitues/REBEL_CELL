# L14 rules (designer 2026-10-24: R9 dummy deck with wounds, R1 two sealed beams, R13 adapted to the deck, R14 hint for Heat)

Lab only (tools/). The GDD is NOT changed until this round shows a score movement. Applies to sweep_l8.py (oracle),
l8_golden.py, l8_rules.gd and parity_check.gd. Everything in L9–L13b stays unless changed here.

## R9: the raid is fed by a dummy run deck; lost districts wound the deck
- **Cards.** A card is `(id: str, type: str, verb: str)`. type in D/N/E, or "-" for a wound. verb in:
  - `GUARD`: sentry only;
  - `SHIFT`: a sentry, or spent at RESPONSE for REDEPLOY;
  - `JAM`: a sentry, or spent at RESPONSE for JAM;
  - `WOUND`: dead. It cannot be placed or spent.
- **START_DECK** (8 cards, ids sorted as strings): s0 D GUARD, s1 D GUARD, s2 N GUARD, s3 N GUARD, s4 E GUARD,
  s5 D SHIFT, s6 E SHIFT, s7 N JAM.
- **State:** `deck: tuple` of cards sorted by id. It replaces `pool`. The kit keeps `ghost` (2); `spoof` is removed.
  Responses are paid with cards instead.
- **DRAW** (new phase, after DECAY and CAPTURE, before PLAN): `hand(leg, raid, st) -> list[str]` of card ids.
  - Take the deck ids in id order and shuffle them with `random.Random(HAND_SEED + 13 * seed + raid)`, where
    HAND_SEED = 9300.
  - Return the first `hand_size(st.heat)` ids. Use the Heat at draw time, without the ghost.
  - `hand_size(heat) = HAND_BASE + (heat >= EXTRA_AT) + (heat >= STRONG_AT)`, with HAND_BASE = 4. See R13.
- **PLAN:**
  - **Sentries:** place at most MAX_PLACED = 2 non-wound hand cards, at most 1 per live cell. `place` is
    `(sentries {cell: card_id}, ghost)`.
  - **Sentry type:** a placed card's type is the sentry's type. `State.sentries` keeps `((cell, card_id), ...)`.
  - **Distinct placements:** placements are distinct by the `(type, verb)` signature of the card on each cell. With
    identical signatures, use the lowest id.
  - **Order:** cells in cell order; then cards in hand order by first appearance of a signature; then skip.
  - **Ghost order** is unchanged.
- **RESPONSE:** the response hand is the hand minus the placed cards. Response formats are unchanged. Each response
  except HOLD and SACRIFICE costs SPOOF_HEAT (+2), as before.
  - `REDEPLOY s -> c` needs a SHIFT card in the response hand.
  - `DEPLOY t -> c` needs a non-wound response-hand card of type t, of any verb; the lowest-id such card is used. It stays placed for the raid.
  - `JAM` needs a JAM card in the response hand.
  - SACRIFICE and HOLD need no card.
  - **Option order is unchanged:** HOLD, REDEPLOY…, DEPLOY…, SACRIFICE…, JAM.
- **Cards return.** The deck persists across the leg and the hand is redrawn every raid. No card is consumed.
- **WOUNDS** (the negative tie-in):
  - Every time an owned cell becomes TAKEN (a HIT on a DOWN cell, DECAY, or SACRIFICE), add one wound card
    `("w<k>", "-", "WOUND")` to the deck, where k is the number of wounds already in the deck.
  - Wounds dilute later hands.
  - **Score:** `-WOUND_COST * wounds` at leg end, with WOUND_COST = 5. This is the cost carried into the run deck.
  - Holding a district gives the deck nothing.
- **BETWEEN:**
  - The `build` option is now `None | "D" | "N" | "E" | "CLEAN"`.
  - **A type** adds `("b<k>", t, "GUARD")` for SENTRY_PRICE (3), where k is the number of built cards so far.
  - **CLEAN** removes the highest-id wound for CLEAN_PRICE (4). It is only an option when a wound exists.
  - Repair, intensity and perks are unchanged.
- **Planner value:**
  - `score(mid=True)` adds KIT_VALUE per ghost and per built card.
  - It subtracts nothing extra for wounds, because WOUND_COST already counts them.
- **naive:**
  - Places the first min(2, live) non-wound hand cards in hand order, on live cells by descending value, then cell
    order.
  - Never responds.
  - Between: as before. It never builds or cleans.

## R1: two sealed beams per raid
- Each raid gains `real_b`: a second sealed route that differs from `real`.
  - Draw it with `random.Random(SEALB_SEED + 13 * seed + raid)`, where SEALB_SEED = 9200:
    `real_b = [k for k in range(3) if k != real][rng.randrange(2)]`.
  - All other leg data is unchanged.
- **Raid order:**
  1. beam 1 and the extras;
  2. REVEAL A (the sealed route `cand`);
  3. RESPONSE, chosen knowing A but not B or the hunter;
  4. sealed A;
  5. REVEAL B: B is one of the two other routes, and both are shown as candidates;
  6. sealed B;
  7. HUNTER REVEAL;
  8. the hunter.
- **Signatures:**
  - `resolve`, `trace` and `hunter_line` take `(leg, raid, st, cand, cand_b, hunt, place, response)`.
  - `cand_b != cand`, otherwise ValueError.
  - The trace beam name for B is `"sealed_b"`. HOME is still lost at most once per raid.
- **forecast(leg, raid, st, place):** per A, returns `{cand, outcomes: [[HOLD result for (b, hunt) ...]]}`.
  - b ranges over the two other routes in route order, and hunt over 0, 1. That is 2 × 2 entries per A, each
    `{state, touches, tier}`.
- **Planner:**
  - EV over 3 A × 2 B × 2 hunt.
  - The response is chosen per A to maximize the mean over the 4 (B, hunt) pairs.
  - Keep the SACRIFICE pruning.
  - Keep 20 legs under about 45 minutes. If that is impossible, `LEGS = int(os.environ.get("LEGS", 20))` and document
    it.

## R13 (adapted for R9): escalation also deals cards
- Each Heat band reached (Heat ≥ 50, Heat ≥ 75) draws **one more card** into the hand (`hand_size` above).
- It adds no state. The board's corp tower shows the band beams together with the extra card slot.

## R14: the best response is hidden; a scan is sold for Heat
- **Rules side:**
  - `HINT_HEAT = 3`.
  - `buy_hint(st) -> State` returns the state with Heat + 3. The lab applies it at RESPONSE before resolving.
  - `best_response(leg, raid, st, cand, place) -> response`, chosen by the planner rule: the mean over the 4
    (B, hunt) outcomes, with the earliest response kept on ties. It ignores the kit's mid value: `mid=False` in the
    final raid, `mid=True` otherwise, the same as the planner.
- **Planners:** greedy never buys a hint (it already sees the EV), and naive never does either.

## Golden and parity
- **Leg JSON:** add `real_b` per raid.
- **State JSON:**
  - `deck` as `[[id, type, verb], ...]`;
  - `sentries` as `[[x, y, card_id], ...]`;
  - `pool` and spoof are dropped from the kit.
- **Steps:** add `hand`, `cand_b` (the real B) and `place.sentries` as `[[x, y, card_id], ...]`.
- **Random raids:**
  - draw `hunt` and the B choice from the rng;
  - the placement is random among `placements`;
  - responses come from `response_options`.
- **Extra checks:**
  - `hand` / `hand_size` on random states;
  - `best_response` for every greedy step;
  - `buy_hint`.
- **parity_check:** checks every new field and function.

## Measurement (sweep_l14.json, OUT path updated)
- Keep all L13 metrics.
- **b_split:** the share of raids where the two B routes give different HOLD outcomes for the chosen placement and the
  real A.
- **wounds_end:** the mean.
- **dead_draws:** the mean number of wounds per hand.
- **clean_use:** how often CLEAN is used.
- **card_response_use:** REDEPLOY/DEPLOY/JAM counts.
- **response_decides** over the new 3 × 2 × 2 table.
- **Greedy and naive breach rate.**
