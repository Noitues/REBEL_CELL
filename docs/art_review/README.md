# Art pass: review folders

Each workstream in `docs/ART_PLAN.md` writes its results to its own folder here. Review them in
any order while the work goes on.

| Folder | Workstream | Contents |
|---|---|---|
| `W1/` | Foundation: tokens, type, spacing | Token swatches, the type scale at 1.0/1.6/2.0, MSDF before/after |
| `W10/` | Visual QA harness | The **baseline ("before") pack** of every screen, plus lint reports |
| `W2/` | Component library | The components lab in every state |
| `W3/` | Wheels and combat | Combat before/after, frame strips |
| `W4/` | Cards | Card frames, rarity stock, stand-in illustrations, `concepts/` |
| `W5/` | Characters | Class portraits, expressions, holograms, `concepts/` |
| `W6/` | VFX and shaders | Tier strips, hit VFX per slice, reduce-effects end states |
| `W7/` | City | Lighting, Heat states, territory, grade |
| `W8a`–`W8d/` | Screens | Per-screen before/after |
| `W9/` | Accessibility | 2.0 text, colour-blind remaps, high contrast, pad |
| `W9F/` | Final accessibility sweep | Every screen at 2.0 mouse and pad, grey, deutan, high contrast, reduce effects, reduce motion; the final runtime lint; the §12/§14 table |

Each folder has a `README.md` with:
- what changed (files);
- the ART_BIBLE §14 checklist;
- the decisions made (also logged in `docs/DECISIONS.md`);
- anything not done, and why.

Concept images (`concepts/`) are script-drawn pixel or vector art for the painted-art briefs.
They aren't game assets and ship only with the designer's approval.
