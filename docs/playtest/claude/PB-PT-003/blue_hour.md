# Playtest feedback — blue_hour · PB-PT-003 · build 52ba1e942fc6205fa97a705cb4c3171aafbbeae9 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** blue_hour
- **Persona / focus / quirks:** Impatient skimmer / Raids and cell defense / never reads tooltips unless stuck; tries a different class each netrun when possible (could not: only Breaker was unlocked)
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52ba1e94
- **Total playtime:** 40 minutes (334 actions, 202 steps; the game was quit and restarted several times, the last quit via the pause menu)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker ×2, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time. INCOMPLETE. I also abandoned several earlier runs after both Breakers died.)
  - Netruns: roughly 14 fights started across several campaigns; about 7 won and 7 lost. Operative deaths: 7 Breakers, mostly at fight nodes on L2/L3 (Dosage Dispenser, Collections Agent, Triage Unit, Compliance Officer). No Elite Router or Server Rack deaths.
  - Highest Site tier reached: T1 (map showed L3 at best) · Exploits held: 0 · Sites claimed at the end: not encountered
  - Raids: not encountered (0 survived, 0 nodes lost)
  - Final Heat: 13 · Home server integrity: not shown
- **Overall enjoyment (1–10):** 3 — fights were long slogs and permadeath hit with no warning.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? No. I mashed SEND IT and never understood the wheels or RAM. I still won some fights that way.
  - Did SEND IT ever give a different result from the preview chips? Can't say, I never read the chips.
  - Did UNDO / rewind behave as expected? Not used.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. I took Nudge Driver, Firewall and Patch+ without reading.
  - Useless / never worth picking: can't judge.
- **Synergies & archetypes:** Only Breaker was available (Hivemind locked, "UNLOCKS 60"). The deck felt like a random pile because I never read it.
- **Card text & clarity:** No. Keywords and RAM -1 were never explained to me, and I skipped the tutorial box. A first fight lasting 15 turns made it worse.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long (fights ran 5–18 turns, roughly 2–4 min each); whole campaign: could not finish in 40 min.
- **Netrun map & encounters:** I saw fights, one wellness-kiosk event and an elite (Recall Unit) at the end. Fights repeated the same Billing Farm and Dosage Dispenser nodes a lot.
- **City Grid & HQ:** After both Breakers died, the map said to "recruit at HQ" but I never found an HQ route. The MARKET panel did show a Breaker recruit at 15 schematics, and I had 5. This was a dead end.
- **Heat:** Heat jumped by 11 per death (11, 22). I could not predict or manage it.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 3 — going into a fight at 7/60 HP and dying was my own fault, but the game gave little warning of permadeath.
- **Permadeath & meta-progression:** Permadeath felt unearned the first times, since the LETHAL tag was the only warning. Later I admitted some deaths were my fault. It did not make me want another run.

## 4. UI, controls & audio

- **Information in combat:** Wheels, RAM and enemy pointers were unreadable to me. HP numbers were fine.
- **Information outside combat:** I could not find HQ. The Map Key panel covers the site card (0055.png), the dossier HP max is hidden (0130.png), and JACK IN looks active when no operative can run.
- **Controls:** Responsive. Esc opened the pause menu unexpectedly. My first click on the title loaded the wrong thing.
- **Visual feedback:** Not much impact registered for me.

## 5. Focus questions (Raids and cell defense)

1. Did the projected outcome in setup match the result? — Not encountered. I never saw a raid warning, setup or projection.
2. Did you understand why a node went DOWN or TAKEN? — Not encountered. The map key lists DOWN and TAKEN icons, but I never saw one on the map.
3. Did raids feel like a puzzle you could solve, or a tax? — Can't say. Fights and permadeath ate the whole session before any raid.

## 6. Open feedback

- **Favourite moment or build:** The win screen with the loot pick was the first thing that felt like progress.
- **Biggest frustration / moment you wanted to quit:** Both Breakers dead (9.0m, again at 27m) with "recruit at HQ" and no HQ to be found.
- **One thing to change or add right now:** Add a clear HQ button and a permadeath warning, and shorten the slog fights.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Map after both Breakers flatlined | 9.0–11.0m, 27.1–29.5m | A route to HQ to recruit or rest | No HQ route; CREW click did nothing | blocker | 0055.png |
| 2 | Map key over site card | 9.6m | Panels not overlapping | Key covers the card's top | cosmetic | 0055.png |
| 3 | Dossier card | 25.2m | Full HP shown | Max HP hidden behind the stamp | cosmetic | 0130.png |
| 4 | Site card / JACK IN | 10.1m | JACK IN disabled with no operative | Looks active | wrong | 0058.png |
| 5 | Market recruit card | 10.1m | Clear cost | Shows 0 schematics but costs 15 | wrong | 0058.png |

**Confusion log:**
- 1.2m — title — wrong screen loaded after my click — brief.
- 2.1m — first netrun — tutorial wall of text, skipped; never resolved.
- 9.0–11.0m — map — where is HQ — never resolved; gave up.
- 27.1–29.5m — map — same HQ problem — never resolved; quit and restarted.
- 30.0m — new campaign — Hivemind locked — resolved, only Breaker is pickable.

## 8. Summary

```
SUMMARY
handle: blue_hour
persona: PB-PT-003
focus: raids
build: 52ba1e942fc6205fa97a705cb4c3171aafbbeae9
outcome: INCOMPLETE
netruns_completed: 7
operative_deaths: 7
raids_survived: 0
playtime_min: 40
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: none
bugs: 5
top_frustration: Both Breakers died and the map said recruit at HQ but showed no way to get there.
top_change: Add a clear HQ route and a permadeath warning, and shorten fights.
```