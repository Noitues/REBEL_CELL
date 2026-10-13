"""Unit tests for the playtest tooling's rules (slice T1): gate profiles, escalation, accounting, parity pairing.

    python tools/playtest/test_playtest_tools.py

No API calls, no game: dry runs and pure functions only. Run by tests/unit/test_playtest_tools.gd.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
import harness  # noqa: E402
import parity  # noqa: E402
import roll_testers  # noqa: E402
import run_batch  # noqa: E402


def args(**kw) -> argparse.Namespace:
    d = dict(at="route:to_netrun", llm_sweep=False, state_budget=12.0, combat_escalation=False, audit_all=False)
    d.update(kw)
    return argparse.Namespace(**d)


def tiers(plan: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in plan["testers"]:
        out[r["tier"]] = out.get(r["tier"], 0) + 1
    return out


class GateProfiles(unittest.TestCase):
    def test_testers_per_profile(self) -> None:
        want = {
            "flow": {"novice": 2, "intermediate": 1},
            "combat": {"novice": 2, "intermediate": 2},
            "access": {"novice": 1, "intermediate": 1},
            "city": {"novice": 3, "intermediate": 1},
            "balance": {"expert": 1},
            "milestone": {"novice": 2, "intermediate": 2, "expert": 1},
        }
        self.assertEqual(sorted(want), sorted(gate.PROFILES))
        for name, w in want.items():
            self.assertEqual(tiers(gate.make_plan(name, args())), w, name)

    def test_no_expert_at_ordinary_gates_and_no_motion_anywhere(self) -> None:
        for name in gate.PROFILES:
            plan = gate.make_plan(name, args())
            for r in plan["testers"]:
                self.assertNotEqual(r["kind"], "motion", name)
                self.assertNotEqual(r["focus"], "animation_feel", name)
                if name in ("flow", "combat", "access", "city"):
                    self.assertNotEqual(r["tier"], "expert", name)

    def test_starts(self) -> None:
        city = gate.make_plan("city", args())
        novices = [r for r in city["testers"] if r["tier"] == "novice"]
        self.assertTrue(all(r["start"] == "title" for r in novices))
        flow = gate.make_plan("flow", args(at="title"))
        self.assertTrue(all(r["start"] == "title" for r in flow["testers"]))
        flow = gate.make_plan("flow", args())
        self.assertTrue(all(r["start"] == "route to_netrun" for r in flow["testers"]))
        bal = gate.make_plan("balance", args())
        self.assertEqual(bal["testers"][0]["start"], "save heat>=25")

    def test_caps_and_budget(self) -> None:
        for name in gate.PROFILES:
            plan = gate.make_plan(name, args())
            self.assertAlmostEqual(plan["caps_total"], sum(r["cap"] for r in plan["testers"]), places=2)
            self.assertGreaterEqual(plan["screen_budget"], plan["caps_total"])  # every tester's cap fits
        self.assertEqual(gate.make_plan("balance", args())["testers"][0]["minutes"], 30)

    def test_llm_sweep_is_opt_in_in_every_profile(self) -> None:
        for name, prof in gate.PROFILES.items():
            off = gate.make_plan(name, args(llm_sweep=False))["state_runs"]
            on = gate.make_plan(name, args(llm_sweep=True))["state_runs"]
            if prof["state"] == "none":
                self.assertEqual((off, on), ([], []), name)
            else:
                self.assertEqual(off, ["heuristic"], name)
                self.assertEqual(on, ["heuristic", "llm"], name)
        flow_h = gate.make_plan("flow", args(llm_sweep=False))
        self.assertEqual(flow_h["state_est"]["heuristic"], 0.0)
        self.assertNotIn("llm", flow_h["state_est"])
        self.assertLess(flow_h["est_typical"], 4.0)
        milestone = gate.make_plan("milestone", args(llm_sweep=False))
        self.assertEqual(milestone["state_runs"], ["heuristic"])
        self.assertEqual(milestone["state_cap"].get("llm", 0.0), 0.0)

    def test_dry_run_prints_without_running(self) -> None:
        text = gate.print_plan(gate.make_plan("combat", args()))
        self.assertIn("keyboard_only", text)
        self.assertIn("Estimated spend", text)

    def test_llm_sweep_flag_exists_and_default_profile_is_milestone(self) -> None:
        self.assertEqual(gate.DEFAULT_PROFILE, "milestone")
        src = (Path(gate.__file__)).read_text(encoding="utf-8")
        self.assertIn('"--llm-sweep", action="store_true"', src)
        self.assertNotIn("--state-mode", src)

    def test_balance_sweep_uses_the_two_turn_lookahead(self) -> None:
        self.assertEqual(gate.state_cmd("heuristic", "x", "1000-1019", 0.0, gate.PROFILES["balance"].get("lookahead", 0))[-2:], ["--lookahead", "2"])
        self.assertNotIn("--lookahead", gate.state_cmd("heuristic", "x", "1000-1019", 0.0, gate.PROFILES["flow"].get("lookahead", 0)))

    def test_access_profile_pins_focus_and_keyboard_persona(self) -> None:
        roster = json.loads(roll_testers.ROSTER.read_text(encoding="utf-8"))
        plan = roll_testers.parse_mix(gate.PROFILES["access"]["mix"], roster)
        self.assertEqual(plan, [("novice", "", "readability_accessibility"),
                                ("intermediate", "keyboard_only", "readability_accessibility")])


class Escalation(unittest.TestCase):
    def d(self, kind: str, esc: bool = False) -> dict:
        return {"kind": kind, "escalate": esc}

    def test_combat_turn_start_does_not_escalate_by_default(self) -> None:
        self.assertFalse(harness.should_escalate(self.d("combat_turn_start"), True, False, False))
        self.assertFalse(harness.should_escalate(self.d("combat_turn_start", True), True, False, False))
        self.assertFalse(harness.should_escalate(self.d("combat_mid_turn", True), True, False, False))

    def test_non_combat_decisions_and_flags_escalate(self) -> None:
        for kind in ("reward_choice", "shop", "map_choice", "event_choice", "raid_setup", "hq_or_city"):
            self.assertTrue(harness.should_escalate(self.d(kind), True, False, False), kind)
        self.assertFalse(harness.should_escalate(self.d("reward_choice"), False, False, False))  # not a fresh screen
        self.assertTrue(harness.should_escalate(self.d("menu", True), False, False, False))  # the actor asked
        self.assertFalse(harness.should_escalate(self.d("menu"), True, False, False))

    def test_watchdog_always_escalates_and_flag_restores_combat(self) -> None:
        self.assertTrue(harness.should_escalate(self.d("combat_turn_start"), False, True, False))
        self.assertTrue(harness.should_escalate(self.d("combat_turn_start"), True, False, True))
        self.assertTrue(harness.should_escalate(self.d("combat_mid_turn", True), False, False, True))

    def test_rules_text_drops_the_combat_escalation_hint(self) -> None:
        self.assertIn(harness.COMBAT_ESCALATION_LINE, harness.RULES)
        self.assertNotIn(harness.COMBAT_ESCALATION_LINE, harness.RULES.replace(harness.COMBAT_ESCALATION_LINE, ""))


class Accounting(unittest.TestCase):
    def test_judge_cost_counted_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old = run_batch.SESSIONS
            run_batch.SESSIONS = Path(tmp)
            try:
                for name, usd in (("a", 1.0), ("b", 2.5), ("judge", 0.75)):
                    (Path(tmp) / "PB-T" / name).mkdir(parents=True)
                    (Path(tmp) / "PB-T" / name / "cost.json").write_text(json.dumps({"usd": usd}))
                self.assertAlmostEqual(run_batch.spent("PB-T"), 3.5)
                self.assertAlmostEqual(run_batch.judge_spent("PB-T"), 0.75)
                self.assertAlmostEqual(run_batch.batch_total("PB-T"), 4.25)
            finally:
                run_batch.SESSIONS = old


class ParityPairing(unittest.TestCase):
    def truth(self, replay: str, n: int) -> list[dict]:
        return [{"replay": replay, "turn": t} for t in range(1, n + 1)]

    def steps(self, fights: list[int], end_ms: list[int] | None = None, header: bool = True) -> list[dict]:
        rows, k = [], 0
        for f, turns in enumerate(fights):
            for t in range(1, turns + 1):
                rows.append({"kind": "combat_turn_start", "shot": "s%d.png" % k, "turn": t if header else 0, "sends": False,
                             "epoch_ms": (end_ms[f] - 1000) if end_ms else 0})
                rows.append({"kind": "combat_mid_turn", "shot": "m%d.png" % k, "turn": t if header else 0, "sends": True,
                             "epoch_ms": (end_ms[f] - 500) if end_ms else 0})
                k += 1
            rows.append({"kind": "combat_result", "shot": "r%d.png" % f, "turn": 0, "sends": False,
                         "epoch_ms": end_ms[f] if end_ms else 0})
        return rows

    def test_pairs_by_order_when_times_and_headers_are_useless(self) -> None:
        by = {"replay_100_1.json": self.truth("replay_100_1.json", 3), "replay_200_2.json": self.truth("replay_200_2.json", 2)}
        pairs, unpaired = parity.pair_turns(by, self.steps([3, 2], header=False))
        self.assertEqual(len(pairs), 5)
        self.assertEqual(unpaired, 0)
        self.assertEqual(pairs[0]["shot"], "s0.png")

    def test_extra_earlier_step_fight_falls_off_the_front(self) -> None:
        by = {"replay_100_1.json": self.truth("replay_100_1.json", 2)}
        pairs, _ = parity.pair_turns(by, self.steps([4, 2], header=False))
        self.assertEqual([p["shot"] for p in pairs], ["s4.png", "s5.png"])

    def test_end_time_picks_the_fight(self) -> None:
        by = {"replay_5000_1.json": self.truth("replay_5000_1.json", 2)}
        pairs, _ = parity.pair_turns(by, self.steps([2, 2], end_ms=[5000, 90000]))
        self.assertEqual([p["shot"] for p in pairs], ["s0.png", "s1.png"])

    def test_turn_header_pairs_when_counts_differ(self) -> None:
        by = {"replay_100_1.json": self.truth("replay_100_1.json", 3)}
        steps = [r for r in self.steps([3]) if not (r["shot"] == "s1.png")]  # one turn start was never screenshotted
        steps = [r for r in steps if r["shot"] != "m1.png"]
        pairs, _ = parity.pair_turns(by, steps)
        self.assertEqual(sorted(p["shot"] for p in pairs), ["s0.png", "s2.png"])

    def test_no_screenshots_pairs_nothing(self) -> None:
        by = {"replay_100_1.json": self.truth("replay_100_1.json", 3)}
        pairs, unpaired = parity.pair_turns(by, [])
        self.assertEqual((pairs, unpaired), ([], 1))


class MixAndStarts(unittest.TestCase):
    def test_start_specs(self) -> None:
        t = {"tier": "intermediate", "persona": "", "focus": "raids"}
        self.assertEqual(run_batch.start_for(t, None, {"intermediate": "title"}), ("", ""))
        self.assertEqual(run_batch.start_for(t, None, {"intermediate": "route:to_netrun"}), ("to_netrun", ""))
        self.assertEqual(run_batch.start_for(t, None, {"intermediate": "save:heat>=25"}), ("continue", "heat>=25"))
        self.assertEqual(run_batch.start_for(t, None, {"keyboard_only": "title", "default": "route:x"}), ("x", ""))

    def test_limits(self) -> None:
        self.assertEqual(run_batch.parse_limits("expert=30:3.0,novice=40:1"), {"expert": (30, 3.0), "novice": (40, 1.0)})


if __name__ == "__main__":
    unittest.main()
