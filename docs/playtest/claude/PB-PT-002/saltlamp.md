# Playtest feedback — saltlamp · PB-PT-002 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** saltlamp
- **Persona / focus / quirks:** Roguelite newcomer / City Grid, HQ and Heat / uses UNDO to experiment with alternative plays most turns
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
- **Total playtime:** 40 minutes (425 actions, 1 session; I quit via the pause menu when time ran out)
- **Campaign setup:** corporation not shown in my notes, ICE not shown, home server not shown, starting roster: a Breaker (60 HP, later seen as 68 max on the map), campaign code not shown (the pause menu has a code box)
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, stuck on the Turn 4 free nudge aim in the third fight)
  - Netruns: 3 fights started, 2 completed, 0 operative deaths
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: 0 · Home server integrity: not encountered (Breaker 13/60 HP)
- **Overall enjoyment (1–10):** 3 — I spent most of the session confused by the wheel and nudge rules and never reached the campaign layer I was meant to judge.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? I never got that far. I couldn't tell what a free nudge gained me, and the tooltips only say "one tick counterclockwise". I worked out by spending that each nudge costs 1 RAM, because only the RAM ledger shows it.
  - Did SEND IT ever give a different result from the preview chips? Not noticed. The previews (Daemon 30→18, Breaker 60→48) were readable once I learned them.
  - Did UNDO / rewind behave as expected? Mostly. It restored RAM. Several early clicks on the button seemed to do nothing until I used the Z key. On Turn 4 of fight 3, UNDO was blocked by "a random event came since (a respin, a random pick)". The game never said what the event was. Afterwards UNDO showed 0 and stayed grey.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Fine Tune felt like a trap. It kept getting selected by accident and I couldn't read where its arrow landed. Overdrive was unplayable for me at 13 HP because of its Corrupted rule.
- **Synergies & archetypes:** I didn't see a strategy come together. I picked Nudge Driver (cards trigger twice), Sanitize (cleanse) and the Patch+ Firmware (+50% slice output). I never tested whether they work together.
- **Card text & clarity:** No. Confusing items:
  - Null ("unless a Daemon says otherwise")
  - Resistance
  - The GOOD, PERFECT and WEAK tags. I only found the PRECISION TAG tooltip at about 14.5m, and until then I thought GOOD over the Daemon's 12 might be a bonus.
  - The aim arrow and the "LANDS HERE" label
  - Q/E icons
  - Shunt's Perfect text
  - Overdrive text that is cut off on the card

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Fight 1 took about 19 minutes, mostly my confusion. Fight 2 took about 2 minutes. I didn't finish fight 3. Whole campaign length is not encountered.
- **Netrun map & encounters:** I saw the layer 1 route map, with fight nodes and a Rack. I did not get far enough to judge whether encounters repeat.
- **City Grid & HQ:** Not encountered. I only saw the route view and the Grid View button. I never recruited, stationed, or spent Schematics.
- **Heat:** Heat stayed at 0 the whole time. The tutorial said banking Schematics on each Rack adds Heat, and I took that to mean banking cools it off. I never saw it move.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 3 — the unnamed "random event" that blocked UNDO on Turn 4 felt unfair, and I couldn't see what it was.
- **Permadeath & meta-progression:** Not encountered.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and previews were readable once I found them. The RAM ledger in the top middle was the only place nudge costs showed. Threat tags weren't explained in the fight. The Turn counter seemed to run ahead of my notes.
- **Information outside combat:** On the map I wanted to find a Rack to heal at 13/60. The map showed only Fight L3, and I found "[1] Fight > Rack" in the route panel. The map showed 25/68 HP where I expected 25/60.
- **Controls:**
  - Esc during a card selection opened the pause menu instead of cancelling. Right-click worked only sometimes. Nothing on screen says which key cancels.
  - Clicks on the Fine Tune area (about 730–737,513) did nothing six times.
  - The free nudge aim felt broken. Clicks on the Breaker wheel and ring marker did nothing, and the arrow kept landing on the Triage ring.
  - The pause menu's "Abandon Run – No Going Back" scared me off touching anything.
- **Visual feedback:** I never saw impact clearly. I got 1 Perfect in fight 1. The preview numbers were the clearest feedback.

## 5. Focus questions (City Grid, HQ and Heat)

1. Could you predict how much Heat an action would add or remove before doing it? No. Heat was 0 throughout. At 23.0m I noted that I couldn't see any Heat number on the plan preview screen.
2. Did you ever feel stuck with no good Site to take? Not exactly. I felt stuck on the map: at 13/60 HP the map showed only Fight L3 until I found the Rack in the route list. I never saw the City Grid.
3. What did you spend Schematics on, and did it feel worth it? Not encountered. I never spent any.

## 6. Open feedback

- **Favourite moment or build:** The fight 2 win against the Dosage Dispenser in 4 turns with no damage taken, and being able to take plays back with UNDO.
- **Biggest frustration / moment you wanted to quit:** The Turn 4 free nudge in fight 3. I spent about 8 minutes unable to aim it at my own Breaker, with UNDO blocked and grey.
- **One thing to change or add right now:** Explain the aim arrow, the "LANDS HERE" label, nudge costs and the cancel key on screen. Also explain the GOOD/PERFECT/WEAK tags and name the random event that blocks UNDO.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Fight 1, Turn 2 | Clicked the Fine Tune area six times (17.5m) | A card selection or a response | No visible change | wrong | 0135.png |
| 2 | Fight 1, Turn 1 | Clicked UNDO (9.4–9.5m) | RAM reset | No visible change until I used Z | wrong | 0062.png |
| 3 | Fight 3, Turn 4 | Staged Fine Tune, then tried UNDO (28.7m) | UNDO works, or says what happened | Blocked by an unnamed "random event" | wrong | 0209.png |
| 4 | Fight 3, Turn 4 free nudge | Clicked the Breaker wheel and ring marker (34–39m) | Nudge aimed at the Breaker | Arrow stuck on the Triage ring, no response, UNDO at 0 | blocker | 0243.png |
| 5 | Card selection | Pressed Esc (7.1m) | Selection cancelled | Pause menu opened | cosmetic | 0041.png |

**Confusion log:**
- 3.0m–4.8m — Turn 1 free nudge — didn't know what a nudge gains — about 2 minutes; I found the RAM cost only by spending the nudges.
- 5.4m–11.5m — Jolt, and how to cancel a card selection — about 6 minutes, resolved by UNDO and trial.
- 12.1m–14.5m — GOOD tag on the Daemon wheel — about 2.5 minutes, resolved by the PRECISION TAG tooltip.
- 25.5m–28.2m — aim arrow — about 3 minutes, partly resolved by the "LANDS HERE" label.
- 28.7m–40.2m — Turn 4 free nudge and blocked UNDO — never resolved.

## 8. Summary

```
SUMMARY
handle: saltlamp
persona: PB-PT-002
focus: City Grid, HQ and Heat
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 2
operative_deaths: 0
raids_survived: 0
playtime_min: 40
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: not encountered
text_clear: no
op_picks: Nudge Driver, Sanitize, Patch+
weak_picks: Fine Tune, Overdrive
bugs: 5
top_frustration: Free nudge aiming was never explained, and the Turn 4 nudge could not be aimed or undone.
top_change: Explain the aim arrow, nudge cost, cancel key and threat tags on screen, and name the random event that blocks UNDO.
```