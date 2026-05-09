import logging
import random
import time
from abc import ABC, abstractmethod
from pathlib import Path

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
SCREENSHOTS_DIR = REPO_ROOT / "data" / "screenshots"


class BaseFiller(ABC):
    TIMEOUT_MS = 45_000

    def apply(self, job: dict, applicant: dict, cover_letter: str, *, dry_run: bool = True) -> dict:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        result = {"success": False, "ats": self.ats_name, "error": None}

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 900},
                )
                page = ctx.new_page()
                page.set_default_timeout(self.TIMEOUT_MS)

                self._fill(page, job, applicant, cover_letter, dry_run=dry_run)
                result["success"] = True
                browser.close()
        except PWTimeout as exc:
            log.warning("[%s] Timeout on '%s': %s", self.ats_name, job["title"], exc)
            result["error"] = f"timeout: {exc}"
            self._screenshot(job["id"])
        except Exception as exc:
            log.warning("[%s] Error on '%s': %s", self.ats_name, job["title"], exc)
            result["error"] = str(exc)
            self._screenshot(job["id"])

        return result

    @property
    @abstractmethod
    def ats_name(self) -> str: ...

    @abstractmethod
    def _fill(self, page, job: dict, applicant: dict, cover_letter: str, *, dry_run: bool) -> None: ...

    def _human_delay(self) -> None:
        time.sleep(random.uniform(1.0, 2.5))

    def _safe_fill(self, page, selectors: list[str], value: str) -> bool:
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if el.count() and el.is_visible():
                    el.fill(value)
                    self._human_delay()
                    return True
            except Exception:
                continue
        log.debug("No selector matched for value '%s...'", value[:30])
        return False

    def _screenshot(self, job_id: str) -> None:
        path = SCREENSHOTS_DIR / f"{job_id}.png"
        try:
            path.write_bytes(b"")
        except Exception:
            pass
        log.info("Screenshot placeholder saved: %s", path)
