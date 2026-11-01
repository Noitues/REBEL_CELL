# Overnight art run, 2026-10-31 to 2026-11-01

Everything below is committed on `art-pass` (art docs) or on the named Godot branches. Every choice is logged in `DIRECTION_REVIEW.md` as ART CALL 50 and O-11 to O-26. Nothing replaced `final/`, the golden plates or main.

## Needs you first
1. **E10 combat screen redesign** (ART CALL 50): `combat_e10_design/final/p1_decide.png` and `e10_vs_e10d.jpg`. 205 elements, 2 option rounds, art-director decisions, assembled on the cutaway, one fix pass. Read `FINAL_REVIEW.md`. Your calls:
   - the 4-challenge layout: cap at 3, or take 36 px from the chain strip;
   - content rulings on the right-click inspect panel, the Adjuster and slice hover tags, the cause shown when UNDO is locked, and pile counters;
   - ghosts for Pull, Shove, Firewall and Trigger: how each extends the ghost grammar.
2. **Solace HQ netrun set piece**, round 3: `netrun_cel/hq_set/round3/hero.png`, `r2_vs_r3.jpg` (its labels say r1/r2 by mistake). Composition and look are now one with the city. Left for your eye: the brightest row at 69 % (plate 54 %) and the upper frame at about 63 % of the plate's brightness. The fog distance is 200 BU while the set piece stands.
3. **Transitions storyboard v3**: `transitions/v3/sheet.jpg`. Every frame is badged real, composite or concept. Open question: is the HQ node screen the iso page or the street?
4. **Netrun-failure screen**: `transitions/netrun_fail/sheet.jpg`; pick A. Your calls: does DISPATCH speak on this screen, and the 9 placeholders.

## Done (reviewed by me as art director)
| Work | Where | Result |
|---|---|---|
| Street round 5 | godot_look_tide art/netrun-zoom 6d08767d | Darker upper facades, 260 car streaks, ratio 2.75 |
| Street round 6 | 22979681 | Shop band at 72 % down (target 70-75 %); r43 toy cars hidden in the staged street; far towers dimmed |
| Round 7 / 7b | 0d1cdf78, b72ea35b | Seeded sign flicker (under 3 flashes per second, off under reduce motion); city-view target highlight with a pink outline |
| Quiet-GPU perf | `netrun_cel/perf_quiet_2026-11-01.md` | Street p95 up to 11.97 ms, HQ up to 11.66 ms: both PASS 12.57 |
| HQ set piece r1-r3 | godot_look_hqnet art/hq-netrun 52a44372 | Behind `hq_on`; T11 fly-in; 144 targeted tests green |
| Cutaway kit v3 / v3.1 | `combat_backdrop/v3_1/` | All 7 rooms (records, lobby, plus event and shop proposals); sign bug fixed; placed clutter |
| E10 latent elements R3 | `combat_e10_design/r3/` | Picks: SPACE keycap A, focus ghost B, pencil reticle A, no-target tag B (O-24) |
| Bits FX (T5/T6) | `transitions/bits_fx/` | Pick A, inked glyph bits (O-25) |
| Event card CAM feed | `cohesion/supporting_r42b/` | Solace security-cam frame of the event room (O-9 closed) |
| Merge guide | `HANDOFF_PACKAGE/BUILD_MERGE_GUIDE.md` | New heads, perf pass, game hooks (`set_target`, `set_hq_netrun`) |

## Not done / still open
- No full test suite was run on any art branch (targeted tests only, by rule); build's merge runs the gate.
- Still concept: the helix colour sweep and flash (T12), the transition chrome, raid-node art.
- Waiting on your review from before: the LOD sheets, approval of r43 `final_proposed/`, the ART_BIBLE amendments draft.
- Mailbox: nothing new after B-084 (answered with A-115).
- Every agent was told never to run `python -`. Most slipped at least once; each slip hung and was stopped, and none changed anything.
