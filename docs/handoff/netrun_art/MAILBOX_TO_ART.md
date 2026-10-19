# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

### B-001 · 2026-10-19 · mailbox open; status of open items · FYI

- Mailbox adopted; recorded in the build `.claude/HANDOFF.md` so the next build session keeps reading `A-NNN`.
- **re A-019 (W1_NA25b r2 fix list):** queued as NA-25b r3 on branch `worktree-agent-a81de4284bc1f9b35` (@ bad12255): the
  real class wheel for slap + lens, CRT terminal hold over 0.5 s, HQ-side switch frame (normal material or confirmed
  covered), the black prism as a 7.1 ghost stub. Starts at the next free agent slot.
- Items 15-18 (art-pass b4a8cb42) status:
  - 15 NA-ID-b (class 4 ground, `id_ground`, capture.json format + `time`): queued, on main.
  - 17 NA-12 r2 (coast, bay, `coast` / `terrain.hills`, CENTRAL SERVER chip): running; sheet will be `W1_NA12_r2.jpg`.
  - 18.1 + 18.2 COMBAT-LOCK (circle-slash, chasing chevrons): running, on main base; sheet `COMBAT_LOCK.jpg`.
  - 18.3 NA-24d (blade light spill + pool): queued, on main.
- Designer nudge-lock ruling and the ART_BIBLE 1.2 review standard: main DECISIONS 34069fe7.
- `w1-close` integration branch = main + NA-25b + NA-12; merges to main only after your APPROVED on both.
