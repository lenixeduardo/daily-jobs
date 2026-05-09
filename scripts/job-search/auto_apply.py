#!/usr/bin/env python3
import logging

from ats.detector import detect_ats
from ats.greenhouse import GreenhouseFiller
from ats.lever import LeverFiller
from ats.workable import WorkableFiller

log = logging.getLogger(__name__)

_FILLERS = {
    "greenhouse": GreenhouseFiller(),
    "lever": LeverFiller(),
    "workable": WorkableFiller(),
}


def attempt_auto_apply(
    job: dict,
    applicant: dict,
    cover_letter: str,
    *,
    dry_run: bool = True,
    ats_allowlist: list[str] | None = None,
) -> dict:
    ats = detect_ats(job["url"])

    if ats is None:
        log.info("Skipping '%s' — unsupported or blocked ATS (url=%s)", job["title"], job["url"])
        return {"success": False, "ats": None, "error": "unsupported ATS"}

    if ats_allowlist and ats not in ats_allowlist:
        log.info("Skipping '%s' — ATS '%s' not in allowlist", job["title"], ats)
        return {"success": False, "ats": ats, "error": f"ATS '{ats}' not in allowlist"}

    filler = _FILLERS[ats]
    log.info("Auto-applying to '%s' at '%s' via %s (dry_run=%s)", job["title"], job["company"], ats, dry_run)
    return filler.apply(job, applicant, cover_letter, dry_run=dry_run)
