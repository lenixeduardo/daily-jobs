import logging
from pathlib import Path

from .base_filler import BaseFiller

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]


class WorkableFiller(BaseFiller):
    ats_name = "workable"

    def _fill(self, page, job: dict, applicant: dict, cover_letter: str, *, dry_run: bool) -> None:
        page.goto(job["url"], wait_until="domcontentloaded")
        self._human_delay()

        # First name
        self._safe_fill(page, [
            "[name='firstname']",
            "[aria-label='First Name']",
            "#firstname",
        ], applicant.get("first_name", ""))

        # Last name
        self._safe_fill(page, [
            "[name='lastname']",
            "[aria-label='Last Name']",
            "#lastname",
        ], applicant.get("last_name", ""))

        # Email
        self._safe_fill(page, [
            "[name='email']",
            "[aria-label='Email']",
            "#email",
        ], applicant.get("email", ""))

        # Phone
        self._safe_fill(page, [
            "[name='phone']",
            "[aria-label='Phone']",
            "#phone",
        ], applicant.get("phone", ""))

        # Resume upload
        resume_path = REPO_ROOT / applicant.get("resume_path", "assets/resume.pdf")
        if resume_path.exists():
            try:
                file_input = page.locator("input[type='file']").first
                if file_input.count():
                    file_input.set_input_files(str(resume_path))
                    self._human_delay()
            except Exception as exc:
                log.debug("Resume upload skipped: %s", exc)

        # Cover letter
        if cover_letter:
            self._safe_fill(page, [
                "[name='cover_letter']",
                "textarea[aria-label*='cover']",
                "textarea[aria-label*='Cover']",
                "textarea[placeholder*='cover']",
            ], cover_letter)

        # LinkedIn URL
        linkedin = applicant.get("linkedin_url", "")
        if linkedin:
            self._safe_fill(page, [
                "input[aria-label*='LinkedIn']",
                "input[placeholder*='linkedin']",
                "[name='linkedin']",
            ], linkedin)

        if dry_run:
            log.info("[workable] dry_run=True — form filled but NOT submitted for '%s'", job["title"])
            return

        # Workable may have a multi-step form — try to advance through steps
        for _ in range(3):
            next_btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if next_btn.count() and next_btn.is_visible():
                next_btn.click()
                self._human_delay()

        submit = page.locator("button[type='submit'], button:has-text('Submit')").first
        if submit.count() and submit.is_visible():
            submit.click()
            page.wait_for_load_state("networkidle", timeout=15_000)
            log.info("[workable] Submitted application for '%s' at '%s'", job["title"], job["company"])
        else:
            raise RuntimeError("Submit button not found")
