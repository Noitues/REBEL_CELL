# Round 34: renaming the slice programs

The GDD art audit (`GDD_ART_COVERAGE.md` §3) found that six of the concept "program" names already mean something else in the game. The designer decided to rename the slice programs.

**This round changes names only.** Glyphs, screens, tiers and overlays stay as locked in round 17.

## How the names were checked
`scripts/name_check.py` builds a corpus of 496 files:
- `docs/GDD.md`;
- `docs/DECISIONS.md`;
- every `content/**/*.tres` file, including ids, display names, descriptions and event text.

A name counts as a **collision** if it appears in the corpus as a whole word, case-insensitive, also matching a snake_case id part (for example `spawn_drone`).

I also grepped `ART_BIBLE`, `GAP_ANALYSIS`, `VISUAL_CRITIQUE` and `DIRECTION_REVIEW` for the recommended names.

Hit counts for the current names:

| Current name | Hits | What it collides with |
|---|---|---|
| EXPLOIT | 70 | the Exploit resource / mainframe gate |
| VIRUS | 74 | the Virus Exploit kind |
| PATCH | 53 | Hot Patch, Patch Up and Stim Patch cards; Patch+ firmware; patch home |
| FIREWALL | 33 | the Firewall card, Firewall Relay node, Firewall turret, Internal Firewall |
| PROXY | 14 | Proxy Relay node, Handler Proxy enemy |
| ZERO-DAY | 12 | the Zero Day daemon |
| SANDBOX | 0 | — |
| TROJAN | 0 | — |
| NULL | 3 | code wording only, in DECISIONS (`GUARD_NULL`, "returns null"); not a game term |

## The table
**Bold** marks the recommendation. The number after each option is its hit count in the corpus.

| Type | Old | Options (hits) | Recommended | Collision checked against |
|---|---|---|---|---|
| ATTACK | EXPLOIT | **SHIM** (0), SHIV (0), SPIKE (0), STAB (0), PAYLOAD (3: Orbital event text) | **SHIM** (designer, v3) | GDD, DECISIONS, all content `.tres`. 0 hits, and none in the other docs either. A shim slipped into a gap fits the dagger glyph; 4 letters. |
| CRIT | ZERO-DAY | **OVERFLOW** (0), SEGFAULT (0), BLUESCREEN (0), KERNEL PANIC (0 as a phrase, but "Kernel Sync" exists) | **OVERFLOW** | Same corpus. Buffer overflow fits the burst glyph. "overflow" also appears in ART_BIBLE / VISUAL_CRITIQUE as UI wording ("+N MORE"), but it is not a displayed game term. |
| DEFEND | FIREWALL | **DEFRAG** (0), BURNWALL (0), IRONWALL (0), BLACKWALL (0) | **DEFRAG** (designer, v3) | Same corpus. 0 hits, and none in the other docs either. It also avoids the BURN / BURNING placeholder clash that BURNWALL had. The wall glyph and the screen stay as they are. Defrag (re-stacking blocks) fits the brick rows. BLACKWALL is avoided because it is a known Cyberpunk 2077 lore term. |
| SHIELD | SANDBOX | **SANDBOX** (0), BUBBLE (0), QUARANTINE (3: the Quarantine Ward event) | **SANDBOX (keep)** | Same corpus. No collision. Glyph locked (option C). |
| EVADE | PROXY | **DETOUR** (0), TUNNEL (0), REROUTE (11: Meridian `reroute_the_audit` Site and events) | **DETOUR** | Same corpus. Matches the locked road-sign detour screen. |
| HEAL | PATCH | **HOTFIX** (0), RESTORE (4: GDD, DECISIONS, event text), DEBUG (1, code) | **HOTFIX** | Same corpus. The cards "Hot Patch" and "Hot Swap" share only the word "hot", not the name. |
| AFFLICT | VIRUS | **INFECT** (0), CONTAGION (0), PATHOGEN (0), BLIGHT (0) | **INFECT** | Same corpus. The shortest clean option (6 letters), so it reads at small size; fits the biohazard glyph. Leech Worm and Malware Drop (cards) ruled out WORM and MALWARE. |
| DEPLOY | TROJAN | **TROJAN** (0), SPAWN (34: Spawn Drone card, classes), FORK (5: Tuning Fork daemon) | **TROJAN (keep)** | Same corpus. No collision; fits the horse glyph. |
| MISS | NULL | **NULL** (3, code wording only), NOP (0), VOID (4: event text "Void the invoices") | **NULL (keep)** | Same corpus. Keep with the 1/0 glyph. NOP is the fallback if the designer wants zero hits even in code docs. |

## The approved set (v3)

The designer changed SHIV to **SHIM** and BURNWALL to **DEFRAG**, and approved the rest.
| Type | Name |
|---|---|
| ATTACK | **SHIM** |
| CRIT | **OVERFLOW** |
| DEFEND | **DEFRAG** |
| SHIELD | **SANDBOX** |
| EVADE | **DETOUR** |
| HEAL | **HOTFIX** |
| AFFLICT | **INFECT** |
| DEPLOY | **TROJAN** |
| MISS | **NULL** |

Each recommended name has 0 hits in the corpus, apart from NULL's code-only hits. Each is one word of 4 to 8 letters and keeps the hacker flavour. None of them overlaps the placeholder glyph names (PHISHING, SHIELD, ENCRYPT, RECON, BURN, BOMB, VAULT, KEY, SPOOF, STORM) or the corporation specials.

Not covered here: the separate corporation-special renames (TARIFF → PRIORITY, INERTIA → WEIGHT, Solace HEAL → GROWTH) are tracked in the audit. **PRIORITY still collides with Priority Routing**, The Manifest's hub (DECISIONS M8).

## Files
| File | What it is |
|---|---|
| `slice_system_final_v3.png`, `glyph_set_v3.png` | The approved names: SHIM and DEFRAG. |
| `slice_system_final_v2.png`, `glyph_set_v2.png` | The first proposal (SHIV, BURNWALL), kept for history. |
| `scripts/name_check.py` | The collision check. Rerun it after content changes. |
| `scripts/glyph_catalog.py` | Holds the `RENAME` map. |

Everything else is carried over from round 17.
