# Playtest feedback — parallax · PB-PT-002 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** parallax
- **Persona / focus / quirks:** Keyboard-first player (intermediate, wrist injury) / First hour and onboarding / uses UNDO to experiment, visits Terminals (events)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 60 minutes (530 actions, 429 steps; the game was quit to the title and continued several times, and it restarted itself once after Quit)
- **Campaign setup:** corporation Solace Biosystems, ICE not shown, home server variant not shown, starting roster: 3 Breakers (classes not shown), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (out of time. INCOMPLETE: all 3 Breakers flatlined, Jack In blocked, raid incoming at Heat 33)
  - Netruns: 3 started, 0 completed, 3 operative deaths (Rack layer 4 vs Claims Adjuster; a later tutorial-overlay fight on Continuum Billing Farm; and a second Billing Farm fight, which I lost on turn 10 under the tutorial 4/7 box)
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: 0 survived, 0 nodes lost (one raid incoming at the end, not played)
  - Final Heat: 33 (raid threshold of 25 crossed) · Home server integrity: not shown
- **Overall enjoyment (1–10):** 3 — the first hour was mostly spent fighting the controls and a stuck aim, and I never reached a real campaign.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. The preview chips (for example 38→14 on the Dosage Dispenser) made planning readable. But Q/E never visibly moved the needle for me, so nudging felt mouse-only and out of my hands.
  - Did SEND IT ever give a different result from the preview chips? Not clearly seen.
  - Did UNDO / rewind behave as expected? No. UNDO was often blocked ("a random event/pick came since"). The block message only became clear late, around 34m. On the Rack turn 1 at 6 HP, UNDO flickered between live and blocked and Z often did nothing.
- **Card balance & utility:**
  - Overpowered / automatic picks: Mirror Flip (the preview showed a big swing on the enemy wheel) and Firewall seemed solid. Not enough data for more.
  - Useless / never worth picking: Overdrive plus Brute Spin pushed RAM into debt for little gain. Mirror Flip showed NEED 3 with 2 RAM and was dead in hand.
- **Synergies & archetypes:** No strategy came together. I skipped most loot to keep the deck lean, and with Breakers dying early I never saw a build form.
- **Card text & clarity:** No. The confusing parts were the RAM debt chip (e.g. -6), the WEAK/GOOD/NULL/PERFECT tags with no on-screen legend, the Jolt "-1" chip, and the "COOL" meter.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netrun: fights ran 3–12 turns. Whole campaign: not judgeable; I ended at about 60 min with all Breakers dead.
- **Netrun map & encounters:** I saw fights, a shop (Mainframe, only 40 Cycles so I bought nothing), an event node, and a forced Rack at layer 4. Several maps offered a single forced next node, with no heal available at 9/60 or 6/60 HP.
- **City Grid & HQ:** HQ showed Breakers, a Market recruit tab and Jack In. Schematics (20) sat unspent. I could not tell whether Heat mattered until the raid warning.
- **Heat:** Not predictable for me. It went 11 → 22 → 33 from flatlines. The raid warning at 25 appeared, with a good [R] key hint on Raid Setup.
- **Raids:** Not played.
- **RNG & fairness (1–5):** 4 — being forced into a Rack against a 112 HP Claims Adjuster at 9/60 and then 6/60 HP, with no healing node offered, felt unfair.
- **Permadeath & meta-progression:** Losing the first Breaker felt unearned: the forced path and a blocked undo set it up. I had no pull to start another campaign.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the LANDS HERE preview were visible. The tags, RAM debt and the Weak/Null meaning were not explained. A tutorial box obscured the board.
- **Information outside combat:** The map is busy and the nodes are small. Hovering a node explains its type and rewards, which is good.
- **Controls:** Many actions had no key or no shown key:
  - Route node picks, loot Continue/Skip and card pick, firmware choice.
  - Tutorial NEXT/FINISH/Skip (Space happens to work, but never shown on the button).
  - JACK IN, BACK TO HQ, Market tab, and Quit to Main Menu.
  - Nudge aiming (Q/E gave no visible effect; clicking the arrow worked).
  - Card aiming and cancelling an aim (Esc opens pause, right-click did nothing).
  - Pause menu: only Resume shows [Esc], and Abandon Run sits right beside Resume and Quit.
  - Quit confirm: it shows QUIT [A], but pressing A did nothing.
  - Shown and working: UNDO [Z], Space for SEND/LOOT/next_step.exe, Raid Setup [R], and Esc for Quit on the title.
- **Visual feedback:** Previews were clear. The Rack stuck-aim state gave no feedback, and the FLATLINED/DEFEAT state gave no clear next step.

## 5. Focus questions (First hour and onboarding)

1. After the tutorial, what did you still not understand? — The nudge key (Q/E), the Weak/Good/Null/Perfect tags, the RAM debt chip, how to cancel a card aim, and when UNDO is blocked.
2. Which word, icon or number confused you longest? — The RAM debt chip (-2/-6) and the WEAK tag. Neither was ever explained, across about 40 minutes.
3. When did the game 'click', if it did? — It never fully clicked. The previews were readable, and the 3-turn Dispenser win at 10.8m was the best moment, but the stuck aim and blocked UNDO took over after that.

## 6. Open feedback

- **Favourite moment or build:** Mirror Flip on the Dosage Dispenser, with a 38→14 preview and a clean 3-turn win.
- **Biggest frustration / moment you wanted to quit:** The lethal Rack turn 1 at 6 HP, from about 21m to 52m. A Jolt or Brute Spin aim stuck for many minutes, UNDO flickered, and the pause menu looped. Only Quit to Main Menu got me out, and CONTINUE returned me to the same aim.
- **One thing to change or add right now:** Show a key hint on every button and make cancelling an aim a visible key (Esc or right-click). Say plainly on screen why UNDO is blocked.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Rack L4 fight turn 1 | 21–50m, Jolt/Brute Spin aimed | Aim cancels via Esc/right-click/Z/UNDO | Aim stuck for ~30 min; it cleared only intermittently or by itself | blocker | 0204.png, 0320.png |
| 2 | UNDO | 15.9m, 21.2m, 34.2m | Undo works, or says why not | Blocked after random events; it flickered live/blocked and Z often ignored | wrong | 0097.png, 0226.png |
| 3 | Quit/Continue | 33.5–33.7m | Fresh state after Continue | Returned straight to the same stuck aim | wrong | 0222.png |
| 4 | Nudge keys Q/E | 5.0–12m | Keys move the needle | No visible effect all tutorial; mouse arrow worked | wrong | 0025.png |
| 5 | Quit confirm | 54.0m | Pressing A quits | A did nothing; only a click worked; the game later restarted to the Godot splash | wrong | 0383.png |
| 6 | Tutorial 4/7 box | 57.7–59m | Box clears once the lesson is done | It covered turns 4–10; only Space moved it; it persisted after the Breaker flatlined | wrong | 0403.png |
| 7 | Rack turn 1 | 52.0m | Free nudge counter drops after use | The banner still read FREE NUDGE 1 | cosmetic | 0365.png |
| 8 | Respin | 31.8m | Respin opens | Spent RAM (to 2/12), no respin appeared | wrong | 0207.png |
| 9 | Title/loading | 55.3–55.5m | Clean screens | Blank transitions; the title then started a tutorial fight | cosmetic | 0397.png |

**Confusion log**:
- 2.0m — tutorial resistance/NEXT — NEXT looked greyed out — about 10s, Space worked.
- 3.3–5.3m — tutorial turn 7 — the needle was stuck on NULL and the Q/E keys did nothing — about 2 min, a click on the arrow fixed it.
- 11.6m — L3 fight — the Weak tag on my wheel was unexplained — never resolved.
- 21.2–52m — Rack turn 1 — a lethal preview with a stuck aim and blocked UNDO — about 30 min, unresolved.
- 34.2m — UNDO banner — it finally explained why UNDO was blocked — late.
- 56.2m — Breaker FLATLINED while the tutorial box continued — unclear how to leave — it ended only with the netrun failed screen.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: parallax
persona: PB-PT-002
focus: first-hour-onboarding
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 0
playtime_min: 60
enjoyment: 3
rng_fairness: 4
netrun_length: just right
campaign_length: too long
text_clear: no
op_picks: Mirror Flip, Firewall
weak_picks: Overdrive, Brute Spin
bugs: 9
top_frustration: Card aim stuck for ~30 minutes on a lethal Rack turn with UNDO blocked and no keyboard way to cancel
top_change: Show a key hint on every button and add a visible aim-cancel key, with a clear on-screen reason when UNDO is blocked
```