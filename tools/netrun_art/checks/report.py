"""Check records, markdown and JSON output, exit code (NA-04 acceptance 1).

A record is a plain dict `{id, status, value, threshold, note}`. Status is `pass`, `warn`, `fail` or `n/a`
(NA03_NA04_ANSWERS O-4: not applicable or no input; it never fails the run). Only `fail` makes the exit code 1.
Standard library only.
"""
import math
import os
from typing import Any, Dict, Iterable, List, Optional

from .. import io

PASS, WARN, FAIL, NA = "pass", "warn", "fail", "n/a"
STATUSES = (PASS, WARN, FAIL, NA)
Record = Dict[str, Any]


def clean(v: Any) -> Any:
    """JSON-safe copy of a value: NaN and Inf become None, tuples become lists, numpy scalars become Python."""
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    if hasattr(v, "item") and not isinstance(v, (list, tuple, dict)):
        v = v.item()
    if isinstance(v, float):
        return v if math.isfinite(v) else None
    if isinstance(v, int):
        return v
    if isinstance(v, (list, tuple)):
        return [clean(e) for e in v]
    if isinstance(v, dict):
        return {str(k): clean(e) for k, e in v.items()}
    return str(v)


def record(check_id: str, status: str, value: Any = None, threshold: Any = None, note: str = "") -> Record:
    """Build one record. `status` must be one of pass, warn, fail, n/a."""
    if status not in STATUSES:
        raise ValueError(f"bad status {status!r}")
    return {"id": check_id, "status": status, "value": clean(value), "threshold": clean(threshold), "note": note}


def exit_code(records: Iterable[Record]) -> int:
    """1 when any record failed, else 0 (warn and n/a never fail)."""
    return 1 if any(r["status"] == FAIL for r in records) else 0


def counts(records: Iterable[Record]) -> Dict[str, int]:
    """Number of records per status."""
    out = {s: 0 for s in STATUSES}
    for r in records:
        out[r["status"]] += 1
    return out


def _cell(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.4f}".rstrip("0").rstrip(".") if "." in f"{v:.4f}" else f"{v:.4f}"
    if isinstance(v, (list, dict)):
        return io.canonical_dumps(v).replace("\n", "").replace(" ", "")
    return str(v)


def to_markdown(records: List[Record], title: str = "NA-04 checks") -> str:
    """Markdown table of the records plus a one-line summary."""
    c = counts(records)
    lines = [f"# {title}", "", f"pass {c[PASS]}, warn {c[WARN]}, fail {c[FAIL]}, n/a {c[NA]}", "",
             "| id | status | value | threshold | note |", "|---|---|---|---|---|"]
    for r in records:
        note = r["note"].replace("|", "/")
        lines.append(f"| {r['id']} | {r['status'].upper()} | {_cell(r['value'])} | {_cell(r['threshold'])} | {note} |")
    return "\n".join(lines) + "\n"


def to_json_obj(records: List[Record], meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Report object: `{version, summary, records, meta}`; write it with `io.dump`."""
    return {"version": 1, "summary": counts(records), "records": [clean(r) for r in records], "meta": clean(meta or {})}


def write_reports(records: List[Record], out_dir: str, stem: str = "checks", meta: Optional[Dict[str, Any]] = None) -> None:
    """Write `<stem>.md` and `<stem>.json` (canonical JSON) into `out_dir`."""
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, stem + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(to_markdown(records, title=stem))
    io.dump(to_json_obj(records, meta), os.path.join(out_dir, stem + ".json"))
