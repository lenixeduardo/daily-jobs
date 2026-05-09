from urllib.parse import urlparse

_BLOCKED = {"linkedin.com", "www.linkedin.com", "indeed.com", "www.indeed.com", "br.indeed.com"}

_ATS_MAP = {
    "boards.greenhouse.io": "greenhouse",
    "job-boards.greenhouse.io": "greenhouse",
    "jobs.lever.co": "lever",
    "apply.workable.com": "workable",
}


def detect_ats(url: str) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return None

    if host in _BLOCKED:
        return None

    return _ATS_MAP.get(host)
