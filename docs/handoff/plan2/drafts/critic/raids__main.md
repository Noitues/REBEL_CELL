<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__raids__main; status ok; tokens in 12000 cache-write 0 cache-read 32585 out 1809; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: raids/main

**Verdict:** FIX

## Issues

1. **BLOCKER, §6 Example A, arithmetic and logic.** The 14 Schematics left after decrypt and move leaves no margin, and the net line is inconsistent. "Net +4 − 1 − 3 − 14" is not the income arithmetic: 18 + 18 reward − 1 − 3 − 14 = 18. The text also says the player "is behind", which contradicts that. The wave 1 numbers ignore the "+25 % rounding" the draft claims: base 12/5 would give 15/6 only for the collector, and the base stats are never stated. The step trace is unverifiable. "V takes 22 total and goes DOWN" contradicts "with the spotlight on S, V's damage was only ×1" and the earlier claim that V falls on step 2.
2. **BLOCKER, §2 vs §6, spotlight logic.** Moving the ring to S wastes the bonus, but S is not the node threats reach. The draft calls it "a node the routing never visits", yet V–S–H is a route to Home. Also, the Ghost is stationed on S, so S carries the free decrypt and station bonus. The worked example does not test the stated decision.
3. **BLOCKER, R2 vs "previews must equal results".** The interval preview breaks the preview = result guarantee. The rulings have no exemption. It is also open as a Q, but the design depends on it. A deterministic hidden-routing hash is fine, but the preview shows a range until paid. A fallback is needed that keeps exact preview for the unencrypted part.
4. **MAJOR, §5 "second wave", premise.** The draft says `raid_purge` already has two waves and that the wave 1–2 timing is "verify". Sequential waves with `spawn_step` are claimed as existing but flagged unverified. Raids are at "FLAGGED and HUNTED", yet §1 says wave 2 for FLAGGED is "reinforcements" and in §6 the HUNTED wave 2 preview shows 2 drones that are "cancellable". The order of the ultimatum against R2 decrypt spend is also unspecified.
5. **MAJOR, §4, systems and ids.** Tethys and Aurelian rosters are invented (`levy`, `bannerman`, `submersible`, `pressure_hull`, `gunship`, `drop_pod`), and so are "levy-lite grounds" and "gunship-lite (courier)", which are not ids. The retag table assigns threats to corporations by guess. The new entry table has an unlabeled `routing` column (1, 2, 0 are ints) and "other" and "rebel_mirror_*" entries that are not field lists.
6. **MAJOR, §5 price curve.** "Anchor: about 50 % repair cost of one DOWN node" is not computed. A repair price of node install costs is not given, so 8 / 14 is unjustified. At 18 income per raid and 14 to cancel, the sink is 78 % of the reward, which far exceeds the sim target of 15–25 %. The 1.5× refuse bonus at 21 contradicts "keeps Schematics scarce".
7. **MAJOR, §1.** The "PURGE" band row says R4 is "no deal", yet §9 has `no_deal`, while §1 says raid_purge wave 2 is mandatory. Heat cost payment "blocked if it would reach 100" is stated only for the spotlight, not for the R4 Heat cancel.
8. **NIT, §7.** The offers draw on the `rewards` RNG stream, but no checkpointed named stream is confirmed. Fallback: deterministic list. "Raid event" needs N16, which is only optional.
9. **NIT, §3.** Free decrypt rules are applied "automatically to the highest-damage threats", which removes a choice that the text elsewhere promises.

## Concrete fixes

- **#1:** Replace the net line with: "Schematics: 18 start + 18 reward − 1 − 3 − 14 = 18. V stays exposed-free, so it takes 11 per step (not 17) and holds on step 3." State base wave 1 stats (12/5, 8/3, 25/9, 18/6) before the ×1.25.
- **#2:** Move the Ghost to a Proxy node P off the route, and make the dead-end target P ("P–H only"), so the move costs 3 Schematics to waste the bonus.
- **#3:** "Encrypted routing is shown as the most likely rule (exact preview, with a ? badge). The preview equals the result when the guess holds. A wrong guess is flagged, so the interval is not shown."
- **#6:** Set FLAGGED 5 / HUNTED 8, fatigue ×1.25, refuse bonus 1.25× base, and add "payments ≈ 20 % of income".

## Keep

- Hash-based hidden routing, which is deterministic and a real question.
- The vehicle triangle (stall / fire / perimeter) with a Railgun exemption.
- The Heat-or-Schematics fork and the no-cascade rule for ultimatums.

## Q:

- Q: Is a fully exact preview required even while encrypted, or is "likely route + badge" allowed?
- Q: Should the Ghost's free decrypt be chosen by the player?
- Q: Is the 50 % repair cost the right anchor for the ultimatum price?
