# W3 QUESTIONS (Q-DESIGNER lines from RD-01 raid operative drafts, and ST-01 status audit)

Each line is a designer question with the recommended default. Source file in brackets. Round: W3, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp.

- [botnet.md] Should the exposed-node soak (rule 4) exist, or should the Botnet be only the free turret? | DEFAULT: keep it, 1 hit per raid, so the Botnet has a visible R1 role
- [botnet.md] Should rank scaling raise the free asset's damage or the number of free assets? | DEFAULT: damage only (1.0 / 1.25 / 1.5 / 2.0), one asset
- [botnet.md] Should the free asset count against the Armory cap of 6? | DEFAULT: no, it is a station bonus
- [botnet.md] Should the free asset always be a TURRET (halved by HEAVY), or may the player pick another type? | DEFAULT: always the existing turret asset, so the triangle stays "stall / shoot / cover"
- [breaker.md] Should the Breaker bonus apply to the Firewall Relay built-in turret, or only to placed Armory assets? | DEFAULT: yes, to both, since the built-in is a TURRET-type asset.
- [breaker.md] Should HEAVY halving apply after the Breaker multiplier, or should the Breaker's shots ignore it? | DEFAULT: halving applies after the multiplier, so stall and Railgun stay the HEAVY counters.
- [breaker.md] Should the rank 0 bonus be 1.5 with no rank scaling in raids? | DEFAULT: no, rank scales it as in `breaker.tres` (1.5 / 1.625 / 1.75 / 2.0).
- [ghost.md] Should the Ghost hold round up or down, given the class comment says 1 / 1 / 2 / 2 steps but the multipliers 1.0 / 1.25 / 1.5 / 2.0 do not give that with either rounding? | DEFAULT: use the authored per-rank steps 1 / 1 / 2 / 2 as direct config values instead of a multiplier
- [ghost.md] Does the unified draft's "Slip the Lock −%" damage reduction exist, or is the Ghost's raid role only the hold? | DEFAULT: hold only, and the −% line is dropped from the unified draft
- [ghost.md] Should the Ghost hold affect FLYING threats? | DEFAULT: no, FLYING ignores the Ghost hold like ICE Lock
- [ghost.md] Should the free decrypt need a Safehouse, or work anywhere the Ghost is stationed? | DEFAULT: Safehouse only, as in the unified draft
- [hivemind.md] Should drones persist across raids or reset each raid? | DEFAULT: reset each raid, since the Hub's persistence is a netrun rule
- [hivemind.md] Do swarm drones count as assets toward the Armory cap of 6? | DEFAULT: no, they are a station bonus, not Armory assets
- [hivemind.md] Should the swarm also absorb the spill damage from a neighboring node? | DEFAULT: no, they guard only hits on their own node
- [hivemind.md] Is the Hivemind's station bonus different enough from Botnet's, whose bonus is one free asset per raid? | DEFAULT: yes for now, with drones on the node instead of an asset, to be revisited at the station-bonus pass
- [overclocker.md] Is the station bonus amount 5 a Heat increase or a Heat reduction at raid start (the excerpt shows no sign)? | DEFAULT: a reduction of 5 Heat before bands are built, scaled by rank, clamped so it cannot cross a threshold downward in a way that cancels the raid
- [overclocker.md] Should the shift apply before the band (changing wave 2, encryption and ultimatum) or after band selection (a cosmetic Heat change only)? | DEFAULT: after the raid's band is chosen but before the ultimatum price is shown, so the band is stable and only the Heat-option legality and the end-of-raid Heat change
- [overclocker.md] Should the Overclocker have any playout role (for example a one-time RAM-style burst), or stay a setup-only Heat station? | DEFAULT: setup-only; no playout effect
- [overclocker.md] Does the shift stack with other classes' station Heat effects? | DEFAULT: no; only the largest single station effect applies
- [phantom.md] Should the Phantom's freeze scale with rank, or stay flat? | DEFAULT: scale with the existing rank station multiplier, giving 1 / 1 / 2 / 2 steps across the four ranks
- [phantom.md] Should the freeze target a specific threat type rather than the highest damage? | DEFAULT: highest scaled damage in the first wave, ties by lowest threat index
- [phantom.md] Should the dodge also scale with rank? | DEFAULT: no; flat at one hit per raid, scaling only the freeze
- [rigger.md] Should the Rigger heal also fire mid-wave (every N steps) so a long wave 1 is covered? | DEFAULT: No; wave end and raid end only, capped at 3 heals per raid
- [rigger.md] Should the Rigger heal apply to adjacent nodes at half strength? | DEFAULT: No; own node only, to keep shared-defense bookkeeping simple
- [rigger.md] Should the heal be allowed on a node that is exposed (R1)? | DEFAULT: Yes; it is applied after the ×1.5 hit and never alters the multiplier
- [rigger.md] Should the Rigger count toward the HEAVY or FLYING counters? | DEFAULT: No; the heal is neither turret nor asset damage
- [wrecker.md] Does the file's `multiplier = 1.5` mean the Rank 0 strike is ×1.5 of the base, or is it ×1.0 with the Rank scale applied on top? | DEFAULT: Rank 0 is ×1.0, Ranks 1-3 are ×1.25 / ×1.5 / ×2.0, and the 1.5 stays a netrun-only value
- [wrecker.md] Should the strike start at 4 damage, which is about half a T1 asset shot? | DEFAULT: 4, to be tuned by the sim so the Wrecker never replaces a Turret
- [wrecker.md] Should a stationed Wrecker's strike range grow with Rank? | DEFAULT: no, range stays 1 hop; only damage scales with Rank
- [wrecker.md] Should the Wrecker strike also hit a LANDER on arrival, before its first hold? | DEFAULT: yes, if it lands in range; it follows the normal range rule with no special case
- [status_audit/ST01.md] Do you want defender-side amplification ("vulnerable") at all, given Medicine ×4 and OVERCLOCKED already stack? | DEFAULT: No; if wanted later, ship it as a Parasite-ring anti-slice with `config: campaign_config.vulnerable_damage_pct` = 150, not a new Status value.
- [status_audit/ST01.md] Should enemy normals ever get a turn-based ramp like enrage (a "ritual" analogue)? | DEFAULT: No; R4 keeps normals' enrage off, and phase changes provide the ramp.
- [status_audit/ST01.md] Should GDD 2.9 be rewritten to the five live statuses, with CORRUPTED as a RAM debuff only? | DEFAULT: Yes; update 2.9 to the code (CORRUPTED, OVERCLOCKED, ENCRYPTED, OUTPUT_DOWN, TIER_DOWN) and note PARASITE as an alias for OUTPUT_DOWN x2.
- [status_audit/ST01.md] Should "frail" (reduced block gained) be covered only by OUTPUT_DOWN on defense slices? | DEFAULT: Yes; accept that block from cards is unaffected, and note it in the Codex status text.
