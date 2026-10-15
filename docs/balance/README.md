# Balance sim (docs/handoff/plan2/BALANCE_SIM.md)

Logic-only combat and campaign simulation with data overrides. No scene, no window; Godot runs headless.

## Run
```
python tools/balance/balance.py run <campaign|fight|boss|netrun> --name NAME [--seeds 1000:1019] [-j 6] [--out-dir DIR] [options]
python tools/balance/balance.py report NAME.json
python tools/balance/balance.py compare A.json B.json --name NAME        # -> docs/balance/CMP_NAME.md
```
Options (passed to `balance_sim.gd`): `--policy builtin|heuristic [--lookahead 1|2]`, `--skill 0..1`, `--ice N`,
`--set <id>.<prop>=<json>` (also `*=` and `+=`; `config.` is the campaign config; repeatable), `--variant file.json`
(`{"set": ["a=b", ...]}`), `--fast` (no per-fight pools), `--no-quiet`; fight: `--enemy ID|all --tiers 1,2,3,4
--categories enemy,elite,mini_boss`; netrun: `--tier N`; boss: `--source campaign|fresh`.
Direct: `godot --headless --path . -s tools/balance/balance_sim.gd -- <mode> ... --out file.json`.

Seeds are sharded over `-j` Godot processes with work stealing (one seed per process for campaign / boss); the merged
records are sorted, so `-j` never changes the result. Same seeds + same overrides = byte-identical records.

## Reading the numbers
- `skill` 1.0 = the policy as is; lower = that share of combat turns played well, the rest are random legal actions.
- Policies: `builtin` is CombatBot (the Monte Carlo policy); `heuristic` is the playtest HeuristicStrategist (slower).
- Perfect rate counts the operative's first pointer. "RAM debt" has no rule in the code: the report shows RAM left
  unspent per turn instead. Raid causes: a threshold-raid is "flatline" when the Heat of the run's actions alone would
  not have crossed it (death Heat tipped it); raids fought inside a run count as actions.
- Boss `--source campaign` plays the campaign to its first breach launch (slow); `fresh` fights with a starter operative.
- Netrun and fight modes start from a fresh starter operative (the campaign mode's attrition tables are the realistic ones).

## Isolation
Branch `balance`: commits may touch only `content/`, `docs/balance/`, `tools/balance/` (`tools/balance/path_guard.py`,
called by `tools/precommit.sh`). The `BASELINE_<sha>.md/.json` here is the reference for `compare`.
