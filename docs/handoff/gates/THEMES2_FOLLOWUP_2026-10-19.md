# Theme follow-up questions (THEMES2, 2026-10-19)

These questions come from applying your theme-sheet answers. Revised drafts: `docs/handoff/plan2/drafts/themes/v2/<corp>.md`, where section 1 holds the
merged rules. Answer per code, e.g. "ME2 toll", "OR1 default", or "all defaults". The recommended default is in parentheses; unanswered
lines take it.

## Meridian
- **ME1** Does the free Grid clear order (rule 11) apply to all Meridian tiers, or only from T2 up, with T1 Sites still opened by the chain? (all tiers, with Rank still gating the tier you may launch)
- **ME2** When you hold nothing undeclared at a Checkpoint, should it be a free pass or still cost a flat toll? (free pass, so declaring in advance is rewarded)
- **ME3** May the Over resistance (up to 3) land on a boss fight at full strength, since M1 allows power loss? (yes; its cap is already config)
- **ME4** Should Express/Tariff change Heat as well as Cycles? (no, Cycles only, to avoid a second economy)
- **ME5** Should a Depot fight count as a normal fight for the Window and the Priority Meter? (yes, it is the intended tie-in)

## Orbital
- **OR1** Should the Relay's death be the escape from the blackout as designed (kill it and pay a Debris at P2+, or replace it free), or should DARK turns be unavoidable and only the strike cancellable? (Recommended: kill or replace both end DARK, since the player needs an answer.)
- **OR2** Do Orbital Exploits taken add raid strikes (a retaliation cost for progress), or should they instead weaken Orbital (e.g. Breach removes a Relay in HQ)? (Recommended: add strikes, because it follows Heat's retaliation logic and needs no new content.)
- **OR3** May a player remove Debris during a netrun (a Rest option for 10 % max HP), or is it permanent until the run ends? (Recommended: permanent until the run ends, capped at 3, per O5.)
- **OR4** Should `ice_steps` push a T1 site to P2 (ICE 10) or should phase follow site tier only? (Recommended: ICE pushes it, capped at P3, so high ICE feels different in early sites.)
- **OR5** May a DARK turn coincide with a strike turn (it can at cadence 3 only when offsets are changed)? (Recommended: never, with strike turns offset so a strike turn is always one where nudges work.)
- **OR6** Does the raid phase use the highest cleared Orbital Site tier, or the campaign's overall tier progress? (Recommended: the highest cleared Orbital Site tier, since it is already stored.)

## Solace
- **SO1** Should the infection decay on a held raid be a flat amount plus kills as drafted (a defended campaign trends to 0), or should it reset fully to 0 after each raid that CELL HOLDS with no TAKEN node? (Keep the partial decay.)
- **SO2** Should Heat objective sites and Proxy Relay completions also cure infection, or should only raids lower it? (Yes, both cure.)
- **SO3** Is stacking all three Exploits (pace 0.75, setback, half turn cost, free ACROSS) too strong, should a cap apply on the combined slowdown? (No cap for now; tune after the sim.)
- **SO4** Should Heat's pace multiplier reach 160 % at PURGE, or should it stop at HUNTED? (Keep 160 %; PURGE is a rare end state.)

## Halcyon
- **HA1** Do other actions that pass time on the Grid (a raid, a patrol) also count as campaign turns that move the Eye? (No: only ended netruns.)
- **HA2** Is Lockdown (beam ×2, Blade +1) the right shape for Alert, or should it summon a Warden fight? (Beam and Blade only.)
- **HA3** Should Stall cost something besides Alert and a step, such as Heat? (No.)
- **HA4** Should Annex rooms be exempt from SHUTTERED, since they are optional? (No, they follow H4.)
- **HA5** Should Cut the Power be once per run, or a Daemon or Exploit-linked reward? (Once per run, in the Power Room.)
- **HA6** Should a FIXED Eye give a stronger raid bonus than a moving one? (No, the same +25 %.)

## REBEL_CELL
- **RC1** When a replacement enters and the dead operative's lane was mid-fight, should the fight restart fresh (my default) or resume with the enemy's damage kept?
- **RC2** Should the backup roster also supply replacements for operatives that fall in the finale (my default: no, since the roster closes at THROW), or may a reserve step in?
- **RC3** Should the run-abandon case (no reserve) lose the run's unbanked gains (my default, as in Q24.1), or keep Cycles already earned?
- **RC4** Should the heal floor stay 20 % at every ICE of 5 and above (my default), or keep declining past ICE 7?
- **RC5** Should the backup roster be shown to the player on the launch screen as an explicit "reserve" choice (my default: all roster extras, in recruit order), or may the player pick the order?

## Aurelian
- **AU1** When a Grid has more than 3 Exploits owned (extra beats), should the extras do anything for the gates, or only for story beats? (Only story beats.)
- **AU2** Should a failed HQ run keep the Breach "once per gate" uses already spent? (No, they reset with the clock.)
- **AU3** Should the stored HQ layout be fixed per campaign or per HQ attempt chain, since A5 says same on retry? (Per campaign.)

## Tethys
- **TE1** Should the Head a netrun ends on be stored when the operative dies or abandons, or only on a win? (Store it on every end, since a failed netrun is still a campaign turn.)
- **TE2** Should Wait for the tide cost a flat 2 Heat or scale with layer? (Flat 2.)
- **TE3** Should a stored end Head expire after one raid? (No; it is overwritten by the next netrun's end.)
- **TE4** Should Divert cost something, such as one Sluice action, since it is now permanent? (It uses the sluice action it already spends, with no extra cost.)
