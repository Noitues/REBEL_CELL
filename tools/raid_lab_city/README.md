# Raid lab L8: the city raid

A playable design demo (Godot 4.7, everything built in code). The raid takes place on the **city view** between two
HQs: ours (amber, left) and the corp's (cobalt, right). This lab has no critic. It exists to show that ownership, the
hunter, the beams and now the run deck read clearly on the city board.

- **Capture:** a CAPTURE phase stands in for the netruns. Each raid you claim one district, or two after a HOT turn.
- **Typed threats and sentries:** threats are DRONE `D` (triangle), NETRUNNER `N` (square) and ENFORCER `E`
  (circle). A sentry blocks only its own type.
- **The run deck:** your sentries are cards. Each raid you draw a hand. Losing districts puts wounds in the deck.
- **Two sealed beams:** two of the three routes are real. The first is revealed before you respond. The second is
  revealed only after that.
- **Hunter:** a hound that runs down one of two sealed streets. Its street is revealed last.

The rules oracle is Python: `tools/raid_concepts/sweep_l8.py`. `l8_rules.gd` is a port of it, and the Python wins any
disagreement. The full spec is in `docs/handoff/raid_lab_l8/SPEC.md`, and the round changes are in `L13_RULES.md`
and `L14_RULES.md`. The data shapes are in `docs/handoff/raid_lab_l8/GD_CONTRACT.md`.

## How a raid plays

A leg is 3 raids.

1. **DECAY** (raids 2 and 3): every district still DOWN becomes TAKEN (cobalt). Each one adds a wound to your deck.
2. **CAPTURE:** legal districts glow. Click one ("Claim 2 of 2" after a HOT turn).
3. **DRAW:** the deck deals a hand into the card row at the bottom of the screen.
   - The hand holds 4 cards, plus 1 at Heat 50 and plus 1 at Heat 75. Extra cards have a gold edge.
   - The "+1 card" tags on the corp tower's heat ghosts show the thresholds.
4. **PLAN:**
   - Pick a card, then a district. Place at most 2 cards, at most 1 per district.
   - **G** places the ghost on HOME or a district (+5 Heat). **Z** undoes, and **Enter** goes to the forecast.
5. **FORECAST:** for each possible first sealed route (A), a 2 × 2 table of tier icons: second route (B) × hunter
   street, assuming HOLD. **Enter** launches.
   - The launch asks for a confirm when HOME drops on every outcome, or when HOME is at 1.
6. **LAUNCH:**
   1. beam 1, plus the extra beams at Heat ≥ 50 and ≥ 75;
   2. **REVEAL A**;
   3. your **RESPONSE**;
   4. sealed A fires;
   5. **REVEAL B** (one of the two other routes);
   6. sealed B fires;
   7. **HUNTER REVEAL**;
   8. the hunter runs its street.
7. **AFTERMATH:** the raid's tier: BREACHED, DAMAGED, EVADED, BATTERED or HOLDS.
8. **BETWEEN** (not after raid 3):
   - repair one DOWN district;
   - add a D/N/E guard card (3), or CLEAN to remove a wound (4);
   - pick an intensity card.
9. **RECORD:** per-raid tiers, districts and exploits kept, and the score breakdown.

## Cards

| Card | Glyph | As a sentry | At RESPONSE |
|---|---|---|---|
| GUARD | shield | blocks its type | DEPLOY: place it on a free district |
| SHIFT | curved arrow | blocks its type | REDEPLOY a placed sentry, or DEPLOY |
| JAM | zigzag | blocks its type | JAM: the hunter does not run, or DEPLOY |
| WOUND | cracked gray | dead | dead |

- **The response hand:** unplaced cards stay in the row as your response hand. SHIFT and JAM cards are highlighted
  as "held for response".
- **Cards return:** no card is used up. The whole deck is reshuffled into a new hand every raid.
- **Wounds:** whenever a district turns TAKEN (hit, decay or sacrifice), a cracked card flies into the deck strip at
  the left edge. Wounds clog later hands and cost **5 points each** at the end of the leg. Hover over the strip to
  see the counts.

## Responses and SCAN

- **The response rows:**
  - **HOLD:** free.
  - **SACRIFICE:** give up a district to shield HOME for this raid.
  - **REDEPLOY, DEPLOY or JAM:** each needs the card shown on its row and costs +2 Heat. Rows you have no card for
    are hidden.
- **Results on hover:** a row's result appears only when you hover over it. It shows a range over the unknown
  B route and hunter street.
- **SCAN (+3 Heat):** marks the best response with a gold edge. You can buy it once per raid.
- **Keys:** **H** = HOLD, **J** = JAM.

## Between raids

| Intensity | Heat | Income | Perk |
|---|---|---|---|
| LOW | +6 | ×0.5 | none |
| NORMAL | +12 | ×1.0 | free repair this step |
| HOT | +18 | ×0.5 | 2 captures next raid |

**Score:** bank, plus districts kept (DOWN at half value), plus 6 per exploit kept. Then subtract:
- 15 per HOME lost;
- the Heat term (above 44, plus a penalty at the 50 and 75 bands);
- 5 per wound.

A breach loses the campaign.

## Run

From the project root:

