# Quiet-GPU frame time re-measure, 2026-11-01

Limit: gpu_city p95 <= 12.57 ms. Raw logs: `perf_quiet_logs/` (`log_street_r1..5.log`, `log_hq_r1..5.log`, `run_times.txt`).

## Verdict
- **art/netrun-zoom (street band), b72ea35b: PASS.** All 5 p95 values are under 12.57 (max 11.97).
- **art/hq-netrun (HQ band), 52a44372: PASS.** All 5 p95 values are under 12.57 (max 11.66).

Note: p99 and max go over 12.57 in several runs on both branches. The limit is on p95, so these do not change the verdict, but they are listed in the table.

## Results (gpu_city, 500 frames, 1920x1080, Vulkan, AMD RX 6700 XT)
Median is the p50 value from the same PERF line.

| # | Band | Start (local) | mean | median | p95 | p99 | max | p95 <= 12.57 |
|---|---|---|---|---|---|---|---|---|
| 1 | street | 03:57:26 | 10.27 | 10.33 | 10.96 | 12.16 | 12.61 | yes |
| 2 | HQ | 03:58:28 | 10.56 | 10.53 | 11.61 | 12.38 | 12.89 | yes |
| 3 | street | 03:59:30 | 10.30 | 10.35 | 10.99 | 12.57 | 12.73 | yes |
| 4 | HQ | 04:00:30 | 10.46 | 10.39 | 11.66 | 12.53 | 13.56 | yes |
| 5 | street | 04:01:32 | 10.44 | 10.52 | 11.10 | 12.73 | 13.01 | yes |
| 6 | HQ | 04:02:33 | 10.00 | 10.26 | 11.28 | 13.97 | 15.03 | yes |
| 7 | street | 04:03:39 | 10.37 | 10.31 | 11.97 | 13.32 | 14.16 | yes |
| 8 | HQ | 04:04:41 | 10.41 | 10.46 | 11.12 | 12.16 | 12.63 | yes |
| 9 | street | 04:05:45 | 10.15 | 10.21 | 10.82 | 12.39 | 12.85 | yes |
| 10 | HQ | 04:06:47 | 10.60 | 10.61 | 11.53 | 12.43 | 12.59 | yes |

Street summary (runs 1,3,5,7,9): p95 min 10.82, max 11.97. HQ summary (runs 2,4,6,8,10): p95 min 11.12, max 11.66.

## Commands
Both wrappers take the shared GPU lock (`D:/rc_scratch/GPU_LOCK`, agent name `art_nrzoom` / `art_hqnet`), run Godot through `tools/run_windowed.py`, and write Godot output to the `--log` file, not to a pipe. Driver: `scratchpad/run_quiet.sh` (in the session scratchpad).

Street (worktree `D:/rc_art/godot_look_tide`, `art/netrun-zoom`, HEAD b72ea35b):
```
bash D:/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh D:/rc_art/art-pass/docs/concepts/netrun_cel/perf_quiet_logs street_rN --zr --target --stages=5 --layers=1 --perf --frames=500
```

HQ (worktree `D:/rc_art/godot_look_hqnet`, `art/hq-netrun`, HEAD 52a44372):
```
bash D:/rc_art/godot_look_hqnet/tools/look_parity/hq_net.sh D:/rc_art/art-pass/docs/concepts/netrun_cel/perf_quiet_logs hq_rN --hq --perf --frames=500 --poses=hero
```

Order: street 1, HQ 1, street 2, ... HQ 5. Each run took about 62 s including the lock and the Godot start.

## Notes on method
- **Command choice.** The brief named `tools/city_perf_probe.gd` as the round 6 command. Round 6's logs (`zoom_rules/round6/logs/perf1-6.log`) do not come from that script. Their `PERF stage=5 layers=1 gpu_city ...` lines come from `tools/look_parity/nr_zoom.gd` (`--perf`), and the city probe prints `PROBE` lines with no median. So the runs above use nr_zoom for the street and hq_net for the HQ band, which are the scripts that wrote the round 6 and round 3 PERF lines. Flags were taken from the script's argument parser; the exact round 6 flag set is not recorded in its notes. `--zr --target --stages=5 --layers=1` is the stage/layers setup named in round 6, and `--hq --poses=hero` is the set-piece and pose used in round 3.
- **Quiet GPU.** Before the first run, two other Godot processes were running (PID 12732, a headless gut test in the rebel_cell worktree, and PID 13828, a windowed `click_coverage` playtest in another rebel_cell worktree). I did not stop them. I waited until both had exited (about 03:57:22) and then started run 1 at 03:57:26. During the series, a headless gut test (PID 5164, rebel_cell worktree) was still running. Headless runs do not use the render GPU, but I did not verify that it caused no contention. The lock was held only by these runs.
- **Failures.** No run failed. All ten exited with code 0. The logs contain no "error" lines. Godot printed the same device line in every run (AMD Radeon RX 6700 XT, Vulkan Forward+).
- **Cleanup.** `run_windowed.py` removed its `override.cfg` and `.quiet_runs` from both worktrees. No code was changed and nothing was committed.
