# M10 sweep-raid lab: critic review

Verdict: **a readable raid puzzle that is not yet a raid. CHOICE mode 31/50, PRESS mode 30/50.** It places just below
Kingdom Rush (33) and level with Teamfight Tactics (31). The forecast and the aftermath ledger are good work. Nothing
else in the leg gives it stakes. Ship CHOICE and drop PRESS. It is not ready for the real build until the designer rules
on the five decisions below, and three of them contradict the GDD as written.

Method: I read shots_scrambled/ 00-13 first and took notes before I opened any readable capture. Then I read
shots_choice/ and shots_press/, then LAB_README.md, then GDD sections 1, 4.3-4.4, 7 and 9.3. I did not launch Godot.
References are in refs/: `refs/side_by_side.png` (lab scrambled forecast and beam 2 beside Into the Breach and
Invisible Inc. Steam screenshots). The source URLs are in `refs/urls.txt`:
- https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/590380/ss_1ac6f8ce8e81bc1b3fe9cb23f58c477cbda04a04.600x338.jpg
- https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/590380/ss_4b985c7747c1ff0b7fbbf3eaf8ca5a1272f0dadb.600x338.jpg
- https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/243970/ss_065423f51f4f35e9867ac6cec9598d32baf7c37b.600x338.jpg
- https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/243970/ss_33c9bdeb0dcbc64c6699e4375e591f7ab3c94ce3.600x338.jpg

## Score table

| | CHOICE | PRESS | One-line reason |
|---|---|---|---|
| W what/why/when | 7 | 7 | The contact chain (run nodes, Heat, notch, contact) is a good why. "What is at stake" stays vague: the key bar's /25 is never explained, and Heat has no visible effect at all. |
| P predictability | 8 | 7 | The on-grid forecast with shape markers, a loss bracket and evade checks is close to ITB quality. The bracket ignores the held spoof (0..-18 shown, -8 was the real worst case after the spoof). PRESS adds a timing miss the forecast cannot show. |
| N no-words | 5 | 5 | Without words I got beams, order badges, lever costs and the ledger arithmetic. I did not get the spoof, the hunter's origin rule, GO DARK's cost formula, EVADE +6, the wrench, or what the key is for. |
| D decision depth | 6 | 6 | A 4x3 grid, 3 sealed candidates, levers capped at 1/1/3: it is solved by inspection in under a minute. The spoof pick is nearly always "the biggest node on the lit line". PRESS adds dexterity, not decisions. |
| C consequences | 5 | 5 | The ledger reconciles and is legible. But every raid ends "CELL HOLDS, 1 DOWN, -11", Heat only climbs and does nothing, the wrench marks vanish when the next network loads, and there is no loss state (no TAKEN, no home integrity). |
| **Total /50** | **31** | **30** | |
| S suspense | 5 | 6 | One real unknown (which sealed line unseals) and one beat of agency (the spoof). Beam 1, beam 2 after the reveal, and the hunter are all foretold, so most of the 6-beat playout is confirmation. PRESS buys a small spike with the ring. |
| V visuals | 4 | 4 | Clean placeholder vector: readable but sterile. Cobalt beams on navy have no threat color. The 4x3 dot grid has no place, no city and no corp. |
| Fit | 6 | 4 | Ghost, decoy, go dark and spoof fit the cell-evasion fantasy well. A sweep over "run nodes as assets" is detached from the Grid, links and network territory in GDD 7. PRESS puts a precision/timing check into raids, against Pillar 4 ("wheel mechanics exist only in combat; raids are deterministic graph auto-battles"). |

**CHOICE is better.** PRESS changes no outcome in the delivered leg (both records are identical). It adds a second
timing indicator: the ring on the node and the slider in the panel split your eyes. It also breaks the pillar that
keeps skill-timing inside the wheels. Its only gain is one point of suspense, and an extra reveal beat would buy that
point more cheaply.

## Placement

ITB 45 > Slay intents 42 > Invisible Inc. 39 > FTL 35 > Kingdom Rush 33 > **lab CHOICE 31 = TFT 31** > lab PRESS 30.

The lab borrows ITB's best idea: numbered attack order plus the threat drawn on the target (ref sheet, ITB
ss_4b985c77). Its P is near ITB's. It loses to ITB on D, because ITB has several units and pushes that redirect the
threat, where the lab has three static stickers. It loses badly on C, because an ITB grid-power loss is permanent and
can end the run. It loses to Invisible Inc. on S and N. Invisible's red floor cones and alarm track give you a live
threat that is spatial and ticking (ref inv2). The lab's sealed lines are drawn identically in calm blue, so the unknown
does not feel dangerous.

## The 5 changes that would most raise it

1. **Give the loss somewhere to land (designer decision).** Tie the raid to GDD 7 outcomes: a found node goes DOWN on
   the Grid and stays DOWN into the next raid, a node found twice goes TAKEN, and the home server sits on the grid with
   integrity. Right now the "consequence" is a number moving on a bar whose purpose is unstated. Raises C by 2 and S
   by 1.
2. **Make Heat matter in the raid, or stop charging it (designer decision).** GHOST's +5 Heat currently buys nothing
   bad that the player can see. Wire raid strength to Heat bands (GDD 4.3: +25% at 75) as one more candidate line or
   one more beam at HUNTED. Then GHOST trades now against later, and the climb from 52 to 91 becomes a threat rather
   than decoration. Raises D and C.
3. **Fold the spoof into the forecast and make the spoof choice non-trivial.** Show the post-spoof worst case (for
   example "-18, -8 with spoof"). Then make the pick matter: the hunter should start from the first real find after the
   spoof, so spoofing the 8 that the hunter would turn on can beat spoofing the 10. Right now "pick the biggest" is
   dominant. Raises P and D.
4. **More unknown, fewer confirmations (designer decision).** Unseal beam 2 later (after the spoof is committed, or
   only when it reaches its first node), or seal the hunter's turn direction as a second reveal. Six beats with one
   surprise is a slideshow. Raises S by 2 and costs P by 1, a trade worth taking.
5. **Fix the no-words vocabulary.** Diamond is used for the decoy lever, for one sealed-line origin, and for a red
   forecast marker. Give each meaning one shape. Use the GDD's DOWN mark (white bolt on a greyed marker) instead of a
   red X plus a red wrench that reads as "tool". Draw threats in red grease pencil per GDD 9.3, not the cobalt that
   also colors the notch and the player's own badges. Drop the HAUL panel, which repeats the grid's numbers with no
   position. Raises N by 2.

Rejected as low value: tuning numbers, more lever types, and PRESS window tuning.

## What the scrambled captures failed to say

These are notes from before I read any words:
- **What the spoof is.** The teal "x1" card reads as a ticket or card. At 06 I could see teal dashed rings on three
  spots of the lit line, one of them an empty dot, but I could not tell that the click makes the beam skip the node. The
  empty node is offered as a target for no reason.
- **Why the hunter starts at the decoy.** 08 shows a red ring on my own decoy and a "GNSQZ" tag. I read it as "the
  decoy got destroyed", not "the third beam turns from the first find".
- **GO DARK's price.** The crossed-out icon reads "0" and then "3" after it is placed on a 4-node. The rule v // 2 + 1
  cannot be recovered, and the cost lands next raid on a line I could not connect to the lever.
- **EVADE +6.** It appears as a teal check with +6 by the key bar, never comes up in any aftermath, and does not match
  the 0 end of the bracket.
- **The key bar.** "19/25" with a hexagon: I could not tell whether 25 is a cap, a goal or a price. The bracket "0 ..
  -18" was readable as a loss range only because the numbers sit beside a hatched bar.
- **Heat consequence.** I saw Heat already past the notch at raid 1 and still rising at raids 2 and 3. Nothing showed
  what Heat does or what happens at 100.
- **The ghost's near miss.** The white flash at 09 reads as "hit", not "missed because hidden".

What it did say well without words: the beam order (1, 2, 3 badges and the step track), the sealed lines as "one of
these three", lever costs as delta colors on the meters, what was lost (red X), and the ledger (19 -3 -8 = 8).

## Ledger and consistency errors

1. **The Heat trigger contradicts GDD 4.3.** Raids fire the first time a threshold is crossed, never again. The lab
   draws "Heat 69 > notch 50, contact" for raid 2 and "Heat 86 > notch 50" for raid 3. Raid 2 crosses no threshold.
   Raid 3 crossed 75, which is not the notch shown. The cause chain the lab is proudest of is false from raid 2 on.
2. **Heat direction contradicts GDD 7.2.** The GDD gives a clean defense +5 Heat and damage none. The lab gives GHOST
   +5 Heat and EVADED -10 Heat. That is the opposite incentive, so it needs a ruling and cannot be a silent port.
3. **The DOWN mark contradicts GDD 9.3** (white bolt over a greyed marker). The lab uses a red X plus a red wrench.
   The threat color contradicts GDD 9.3 too: red grease pencil, with the Cell in yellow. The lab draws threats cobalt.
4. **The forecast bracket does not equal the attainable result.** It shows 0..-18 while the spoof is held, the real
   result was -8, and the evade outcome is +6, not 0. "Preview must equal the real result" (CLAUDE.md rule 6) holds
   for the no-spoof sweep only.
5. **The leg record is an auto-play artifact presented as play.** All three raids read "ghost 1, decoy 1, dark 1,
   decoy -3, repair -8, 1 DOWN" on three different networks. Raids 2 and 3 are "spoof: not landed" in both modes,
   because the driver auto-plays raid 1 only. The CHOICE and PRESS records are byte-for-byte the same. The captures
   cannot show that PRESS changes anything, or that the leg has any variance.
6. **"DOWN nodes get a wrench and stay marked"** (README). They stay marked only until the next network replaces the
   grid, so the persistence claim is invisible in the leg.
7. **The key currency is undecided.** KEY_LABEL toggles Schematics, Scrap and Credits, and the /25 has no source in
   the GDD (Core Schematics have no cap of 25). The run income between raids is invented (+12/+12, as the README admits).
8. **EVADED on a decoy-only contact** (README finding). The screen says "a beam stopped on something" while the rules
   pay +6 and -10 Heat. A player will read that as a bug.
9. **Hunter arrow direction.** The plan view draws column 3 as a downward dashed arrow from the top. In the playout the
   lit segment runs from the decoy row upward. The plan and the playout disagree on direction.
10. **Sealed beam reveal vs GDD 7.1.** The GDD says "exact projected outcome per node" and Pillar 4 says
    "deterministic". The lab shows a range over hidden candidates. This is probably the right call, but it is a GDD
    change and needs a DECISIONS entry.

## Ready for the real build?

**No, not even after rulings, until items 1 and 2 of the changes are designed, not just ruled.** The sweep, levers,
forecast and ledger are portable as they stand (parity PASS, the rules are clean). The designer must rule first on:
(a) PRESS vs CHOICE (recommend CHOICE), (b) the Heat direction and the trigger model (GDD 4.3 and 7.2 vs the lab),
(c) where a "find" lands (DOWN/TAKEN on the Grid with home integrity, or key bleed only), (d) the hidden candidate vs
exact projection, and (e) decoy-only = EVADED. Without (c) the raid has no failure state, and a raid you cannot lose
will score C 5 or less however good the forecast looks. After (c), plus the forecast/spoof fix and the vocabulary fix,
I would expect roughly 36-38, in FTL to Invisible Inc. territory. That is the bar to clear before porting.
