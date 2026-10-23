# Raid lab L8: the city raid

A playable design demo (Godot 4.7, everything built in code). The raid takes place on the **city view** between two
HQs: ours (amber, left) and the corp's (cobalt, right). This lab has no critic. It exists to show that ownership, the
hunter and the beams read clearly on the city board.

- **Capture:** a CAPTURE phase stands in for the netruns. Each raid you claim one district.
- **Typed threats and sentries:** threats are DRONE `D`, NETRUNNER `N` and ENFORCER `E`. Typed sentries bring back
  minimal tower defense, because a sentry blocks only its own type.
- **The sealed beam:** one of the three routes is the real one. The candidates are shown before launch and revealed
  mid-launch.
- **Response:** after the reveal you choose HOLD, REDEPLOY a sentry, or JAM the hunter.
- **Hunter:** a hound that runs down the street of the raid's first touch.

The rules oracle is Python: `tools/raid_concepts/sweep_l8.py`. `l8_rules.gd` is a port of it, and the Python wins any
disagreement. The full spec is in `docs/handoff/raid_lab_l8/SPEC.md`, and the data shapes are in
`docs/handoff/raid_lab_l8/GD_CONTRACT.md`.

## Run

