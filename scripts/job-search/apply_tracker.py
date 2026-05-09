#!/usr/bin/env python3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
APPLIED_PATH = REPO_ROOT / "data" / "applied_jobs.json"

_state: dict = {"applied": []}


def load_applied_ids() -> set[str]:
    global _state
    if APPLIED_PATH.exists():
        try:
            _state = json.loads(APPLIED_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            log.warning("Could not load applied_jobs.json: %s", exc)
            _state = {"applied": []}
    return {entry["id"] for entry in _state.get("applied", [])}


def mark_applied(job: dict, *, method: str, ats: str | None, success: bool, form_data: dict | None = None) -> None:
    entry = {
        "id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "ats": ats,
        "success": success,
    }
    if form_data:
        entry["form_data"] = form_data
    _state.setdefault("applied", []).append(entry)
    log.info("Marked job '%s' at '%s' as applied (success=%s)", job["title"], job["company"], success)


def save_applied() -> None:
    APPLIED_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPLIED_PATH.write_text(json.dumps(_state, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Saved applied_jobs.json (%d entries)", len(_state.get("applied", [])))


def get_applied_map() -> dict[str, dict]:
    return {entry["id"]: entry for entry in _state.get("applied", [])}
