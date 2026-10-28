# Combat concept polish pass 3: element iterations (art-pass, 2026-10-28)

The designer wants another polish pass on the two remaining combat concepts, **Code-base Tower** and **Shifting Waves**
(Packet Lanes is dropped). Each concept is broken into its unique elements. Each element gets its own design iteration
(several options). Art-pass judges and picks the best option per element, the picks are integrated into full plates,
and then a cohesion pass runs. You run ONE iteration cycle (your element group, below). You do not integrate.

## The concepts (rules are fixed; read them, look at every frame)
- **Code-base Tower**:
  - rules: `D:/rc_tmp/combat_concepts/D4_H1/rules.md` and `codebase.md`;
  - frames: `f1_start.png`–`f4_next.png`;
  - an H2 rules variant is pending in `D4_H2/` (Lock holds 2 turns OR a printed step schedule; broken slices lose their ability). Design so either can be shown.
  - Current plates (v2): `D:/rc_tmp/combat_critic/plates/tower_v2/`.
  - Critic review: `D:/rc_tmp/combat_critic/critic_pl2/REVIEW_PL2.md`. Read sections 4–5. Its biggest flaw: p1 shows nothing of what YOU deal (no outgoing fire), packet HP has no number, and the reach arc and next-turn facing are unlabeled.
- **Shifting Waves**, new rules E4 (designer 2026-10-28):
  - **3 rings, all rotating together on ONE printed rotation schedule shown 3 turns deep**;
  - brief: `D:/rc_tmp/combat_critic/brief_e4_rules.md`; base rules: `D:/rc_tmp/combat_concepts/D4_E3/rules.md`;
  - sim in progress at `D4_E4/`;
  - current plates (4-ring E2 view): `D:/rc_tmp/combat_critic/plates/waves/`; critic-refined low-fi view: `D:/rc_tmp/combat_critic/viewdev/spin/`;
  - critic review: `D:/rc_tmp/combat_critic/critic_pl1/REVIEW_PL1.md`.
  - **SPINNER ONLY:** everything is drawn on the wheel (code base in the middle, rings of units, landing band on the rim). There is no grid or table restating the wheel.
- Plate notes: `D:/rc_tmp/combat_critic/plates/PLATES.md`.

## Direction (what the judge favours, in order)
1. **Polish:** AAA finish, real materials and light, crisp type. Not flat stickers.
2. **Cohesion:** one game. Both concepts share the code base, the unit family, the cards and the HUD.
3. **Theme:** cyberpunk; you are a hacker crew defending/bending a corporation's code base. The designer wants something innovative; it must not read as Plants vs Zombies or a generic tower defence.
4. **Readability:** squint at 320 px, deutan/tritan safe, never colour alone (shape + glyph + number), 16 px glyph minimum at 1080p.
5. **Information parity:** every number and mark from the frames can still be shown.
- Art bible: `D:/rc_art/art-pass/docs/ART_BIBLE.md`.
  - §1.2 media jobs, §2 palette and type, §3 combat: slices family C "Screens & Data" CRT screens, the glyph set, state overlays, sticker cards, card-play preview, damage shards.
  - Your option A is the bible-faithful baseline. Options may challenge a lock if clearly better; say so plainly.
- Approved combat look ref: `D:/rc_art/art-pass/docs/concepts/round31_meridian_combat/` (NOTES.md, combat_meridian.jpg).
- Research first: 3+ real references per element group (games, real UI, real hardware or industrial design). Cite them in NOTES.md with what you took from each.

## Each element: deliver 3–4 options (A = baseline, B–D new and genuinely different, not tints of one idea)
Per option:
1. a large isolated hero render or drawing of the element;
2. an in-context mock: the option dropped into the current plate at 1080p crop size;
3. a 320 px squint;
4. a deutan sim for anything colour-coded.
- One sheet per element, `E_<group>_<element>.jpg`, laid out as options left to right, rows hero / context / squint.
- Then `NOTES.md`: per element, a one-line pitch per option, your own recommendation and why, and risks.
- Physical things (slices, units, board, gates, beams) are real 3D in Blender headless. HUD and cards may be 2D, at final quality.

## Output
`D:/rc_scratch/combat_polish/<your cycle id>/`. Make the folder; everything you write goes there.

## Hard rules (non-negotiable)
- D: drive only.
- **NEVER run `python -` or pipe/heredoc anything into python, in any form.** Write a .py file and run it by path.
- Kill only PIDs you started. Never `taskkill /IM`.
- Never touch the designer's running Blender (PID 73456) or its MCP. Only launch your own headless `blender --background`.
- GPU: wrap every render in the GPU lock (read `D:/rc_scratch/solace_v1/gpu_lock.py`). Other overnight jobs share the GPU (a Godot parity loop), so keep renders modest: EEVEE, about 1280 px heroes. Release the lock between renders.
- FILE SAFETY:
  - Delete only files you created, inside your own folder. NEVER use a wildcard or glob in rm / Remove-Item.
  - Never delete or overwrite anything under D:/rc_tmp, D:/rc_scratch or any worktree outside your own folder.
  - The concept folders and plates are read-only for you. If you touch anything not yours, stop and report it at once.
- No game design: do not change rules. If a visual needs a rule decision, list it as a question.
- Leave no background processes when you report.
- Report: the sheet paths, your recommendation per element, the risks, and any slips.
