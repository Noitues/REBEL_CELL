"""State-driven playtester: an LLM plays whole campaigns through the headless agent bridge (doc 05 §11).

    python tools/playtest/state_agent.py --name SA-001 --seed 1000 --tier intermediate --persona strategist
    python tools/playtest/state_agent.py --name SA-002 --seeds 1000-1004 --tier expert --parallel 3 --budget 5

No screen: tools/agent/agent_bridge.gd runs the deterministic campaign headless and, at each
decision, writes the state and a menu of options (whole-turn combat plans with their exact
previews, map nodes, rewards, events, launches, raid placements with projected outcomes). This
driver answers with an LLM, in the persona's style, and gets a one-line reason for every pick:
that reason is the qualitative balance signal ("never take X because..."). Option 0 is always the
built-in policy's pick (greedy CombatBot / CampaignSimulator), so `--builtin all` is the free
baseline the LLM is compared with.

It measures balance and difficulty under real play; it says nothing about clarity or feel (the
screen testers do that). Output per campaign: <out>/<name>/<seed>/report.json + decisions.jsonl,
and a summary at docs/playtest/claude/state/<name>.md.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as hz  # noqa: E402  (api_key, MODELS, PRICES)

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / ".playtest_sessions" / "state"
DOCS = ROOT / "docs" / "playtest" / "claude" / "state"
ROSTER = ROOT / "tools" / "playtest" / "personas.json"
KINDS = ["combat", "node", "reward", "event", "launch", "raid"]
# Per tier: model per decision kind ("" = built-in policy, no call).
TIER_MODELS = {
    "novice": {"combat": "haiku", "node": "haiku", "reward": "haiku", "event": "haiku", "launch": "haiku", "raid": "haiku"},
    "intermediate": {"combat": "haiku", "node": "haiku", "reward": "sonnet", "event": "haiku", "launch": "sonnet", "raid": "sonnet"},
    "expert": {"combat": "sonnet", "node": "sonnet", "reward": "sonnet", "event": "sonnet", "launch": "sonnet", "raid": "sonnet"},
}
SCHEMA = {"type": "object", "properties": {"choice": {"type": "integer"}, "reason": {"type": "string"}},
          "required": ["choice", "reason"], "additionalProperties": False}
RULES = """You are playing REBEL_CELL, a roguelite deckbuilder: an operative runs netruns (a map of fights,
events, shops and Server Racks) against a corporation; fights resolve through spinning wheels where
each pointer lands on a slice (Perfect = the centre of a slice, the strongest result). Between runs you
manage the campaign: Heat (raids fire at thresholds), Schematics, the home server, operatives (permadeath).
Win: breach the corporation's central server with enough Exploits. Lose: the home server falls in a raid.

At each decision you get the state and a numbered menu. Combat options are whole-turn plans with
their exact outcome (the game's preview is exact): damage dealt and taken, kills, RAM, and where
each pointer lands. Pick one option by its number, in your persona's style, and give a one-line
reason a designer would learn from (what you weighed, what you avoided and why)."""


class Agent:
    def __init__(self, a, seed: int, persona: dict, models: dict, cost: dict, lock: threading.Lock):
        import anthropic

        self.client = anthropic.Anthropic(api_key=hz.api_key(), base_url="https://api.anthropic.com", max_retries=5)
        self.a, self.seed, self.models, self.cost, self.lock = a, seed, models, cost, lock
        self.dir = OUT / a.name / str(seed)
        shutil.rmtree(self.dir, ignore_errors=True)
        self.dir.mkdir(parents=True)
        style = "\n".join("- %s: %s" % (k, persona[k]) for k in ("bio", "risk", "pace") if k in persona)
        self.system = [{"type": "text", "text": RULES + "\n\n# Your persona: %s\n%s" % (persona["label"], style),
                        "cache_control": {"type": "ephemeral"}}]
        self.memory: list[str] = []

    def answer(self, req: dict) -> dict:
        kind, options = req["kind"], req["options"]
        model = self.models.get(kind, "")
        with self.lock:
            over = self.cost["usd"] >= self.a.budget
        if not model or over:
            return {"choice": 0, "reason": "builtin" if not model else "budget reached: builtin"}
        menu = "\n".join("%d. %s" % (i, o) for i, o in enumerate(options))
        text = ("Decision: %s\nState: %s\nRecent decisions:\n%s\n\nOptions:\n%s\n\nPick one number." % (
            kind, json.dumps(req["state"]), "\n".join(self.memory[-8:]) or "(none)", menu))
        try:
            r = self.client.messages.create(model=hz.MODELS[model], max_tokens=2000, system=self.system,
                                            messages=[{"role": "user", "content": text}],
                                            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})
        except Exception as e:  # noqa: BLE001 - any API failure falls back to the built-in pick
            return {"choice": 0, "reason": "api error: %s" % type(e).__name__}
        pin, pout, pcr, pcw = hz.PRICES[hz.MODELS[model]]
        u = r.usage
        usd = ((u.input_tokens or 0) * pin + (u.output_tokens or 0) * pout + (getattr(u, "cache_read_input_tokens", 0) or 0) * pcr
               + (getattr(u, "cache_creation_input_tokens", 0) or 0) * pcw) / 1e6
        with self.lock:
            self.cost["usd"] += usd
            self.cost["calls"] = self.cost.get("calls", 0) + 1
        out = json.loads(next(b.text for b in r.content if b.type == "text"))
        out["choice"] = max(0, min(len(options) - 1, int(out["choice"])))
        self.memory.append("[%s] %s <- %s" % (kind, options[out["choice"]][:140], out["reason"][:140]))
        return out

    def play(self) -> dict:
        log = open(self.dir / "godot.log", "w", encoding="utf-8")
        cmd = [self.a.godot, "--headless", "--path", str(ROOT), "-s", "tools/agent/agent_bridge.gd", "--",
               "dir=%s" % self.dir.as_posix(), "seed=%d" % self.seed, "ice=%d" % self.a.ice, "class=%s" % self.a.cls,
               "corp=%s" % self.a.corp, "max_runs=%d" % self.a.max_runs,
               "builtin=%s" % ",".join(k for k in KINDS if not self.models.get(k))]
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
        seen = set()
        with open(self.dir / "decisions.jsonl", "a", encoding="utf-8") as dl:
            while p.poll() is None or any(self.dir.glob("req_*.json")):
                reqs = sorted(f for f in self.dir.glob("req_*.json") if f.name not in seen)
                if not reqs:
                    time.sleep(0.02)
                    continue
                for f in reqs:
                    seen.add(f.name)
                    req = json.loads(f.read_text(encoding="utf-8"))
                    ans = self.answer(req)
                    resp = f.with_name(f.name.replace("req_", "resp_"))
                    resp.with_suffix(".tmp").write_text(json.dumps(ans), encoding="utf-8")
                    resp.with_suffix(".tmp").replace(resp)
                    dl.write(json.dumps({"seq": req["seq"], "kind": req["kind"], "state": req["state"],
                                         "chosen": req["options"][ans["choice"]], "choice": ans["choice"],
                                         "n_options": len(req["options"]), "reason": ans["reason"]}) + "\n")
                    f.unlink()
        log.close()
        rep = self.dir / "report.json"
        return json.loads(rep.read_text(encoding="utf-8")) if rep.exists() else {"outcome": "CRASHED", "seed": self.seed}


def summarize(a, reports: list[dict], cost: dict, persona: dict) -> Path:
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = ["# State playtest %s — %s tier, persona %s, ICE %d, %s vs %s" % (a.name, a.tier, persona["id"], a.ice, a.cls, a.corp),
             "", "Cost: $%.2f (%d LLM calls). Option 0 of every menu = the built-in policy (greedy CombatBot)." % (cost["usd"], cost.get("calls", 0)),
             "", "| Seed | Outcome | Runs | Completed | Deaths | Raids (won) | Heat peak | Breach Heat | Fights | Decisions off-default |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in reports:
        dec = r.get("decisions", [])
        off = sum(1 for d in dec if int(d.get("choice", 0)) != 0)
        lines.append("| %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %d of %d |" % (
            r.get("seed"), r.get("outcome"), r.get("runs"), r.get("completed"), r.get("deaths"), r.get("raids"),
            r.get("raids_won"), r.get("heat_peak"), r.get("heat_at_breach"), r.get("fights"), off, len(dec)))
    lines += ["", "## Reasons by decision kind (sample)", ""]
    for seed_dir in sorted((OUT / a.name).iterdir()):
        dj = seed_dir / "decisions.jsonl"
        if not dj.exists():
            continue
        rows = [json.loads(l) for l in dj.read_text(encoding="utf-8").splitlines() if l.strip()]
        for kind in KINDS:
            picked = [r for r in rows if r["kind"] == kind and r["reason"] not in ("builtin",)][:4]
            for r in picked:
                lines.append("- seed %s [%s] %s — *%s*" % (seed_dir.name, kind, r["chosen"][:160], r["reason"][:200]))
    lines += ["", "## Run logs", ""]
    for r in reports:
        lines.append("### seed %s" % r.get("seed"))
        lines += ["    " + l for l in r.get("log", [])[-60:]]
    out = DOCS / ("%s.md" % a.name)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--seeds", default="", help="a range like 1000-1004 (overrides --seed)")
    ap.add_argument("--tier", choices=sorted(TIER_MODELS), default="intermediate")
    ap.add_argument("--persona", default="strategist")
    ap.add_argument("--builtin", default="", help="kinds left to the built-in policy, e.g. combat,node; 'all' = free baseline")
    ap.add_argument("--ice", type=int, default=0)
    ap.add_argument("--cls", default="breaker")
    ap.add_argument("--corp", default="solace")
    ap.add_argument("--max-runs", type=int, default=60)
    ap.add_argument("--budget", type=float, default=3.0, help="dollars for the whole command; then the built-in policy answers")
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--godot", default="godot")
    a = ap.parse_args()
    seeds = list(range(int(a.seeds.split("-")[0]), int(a.seeds.split("-")[1]) + 1)) if a.seeds else [a.seed]
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    persona = next(p for p in roster["personas"] if p["id"] == a.persona)
    models = dict(TIER_MODELS[a.tier])
    for k in (KINDS if a.builtin == "all" else [k for k in a.builtin.split(",") if k]):
        models[k] = ""
    cost, lock, reports = {"usd": 0.0}, threading.Lock(), []

    def run(seed: int) -> None:
        r = Agent(a, seed, persona, models, cost, lock).play()
        with lock:
            reports.append(r)
            print("seed %s: %s in %s runs (%s deaths), %s raids, Heat peak %s; $%.2f so far" % (
                r.get("seed"), r.get("outcome"), r.get("runs"), r.get("deaths"), r.get("raids"), r.get("heat_peak"), cost["usd"]), flush=True)

    threads: list[threading.Thread] = []
    for seed in seeds:
        while sum(t.is_alive() for t in threads) >= a.parallel:
            time.sleep(0.5)
        t = threading.Thread(target=run, args=(seed,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    reports.sort(key=lambda r: int(r.get("seed", 0)))
    print(summarize(a, reports, cost, persona))
    return 0


if __name__ == "__main__":
    sys.exit(main())
