import logging
from pathlib import Path

from .base_filler import BaseFiller

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]


class LeverFiller(BaseFiller):
    ats_name = "lever"

    def _fill(self, page, job: dict, applicant: dict, cover_letter: str, *, dry_run: bool) -> None:
        page.goto(job["url"], wait_until="domcontentloaded")
        self._human_delay()

        # Full name (Lever uses a single name field)
        full_name = f"{applicant.get('first_name', '')} {applicant.get('last_name', '')}".strip()
        self._safe_fill(page, [
            "[name='name']",
            "#name",
            "[aria-label='Full name']",
            "[placeholder*='Name']",
        ], full_name)

        # Email
        self._safe_fill(page, [
            "[name='email']",
            "#email",
            "[aria-label='Email']",
        ], applicant.get("email", ""))

        # Phone
        self._safe_fill(page, [
            "[name='phone']",
            "#phone",
            "[aria-label='Phone']",
        ], applicant.get("phone", ""))

        # Location
        self._safe_fill(page, [
            "[name='location']",
            "#location",
            "[aria-label='Location']",
        ], applicant.get("location", ""))

        # LinkedIn URL
        linkedin = applicant.get("linkedin_url", "")
        if linkedin:
            self._safe_fill(page, [
                "[name='urls[LinkedIn]']",
                "input[aria-label*='LinkedIn']",
                "input[placeholder*='linkedin']",
            ], linkedin)

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

        # Cover letter (Lever has a textarea for additional info)
        if cover_letter:
            self._safe_fill(page, [
                "[name='comments']",
                "textarea[aria-label*='cover']",
                "textarea[aria-label*='Cover']",
                "textarea[aria-label*='additional']",
                "textarea[aria-label*='Additional']",
            ], cover_letter)

        if dry_run:
            log.info("[lever] dry_run=True — form filled but NOT submitted for '%s'", job["title"])
            return

        submit = page.locator("button[type='submit'], input[type='submit']").first
        if submit.count() and submit.is_visible():
            submit.click()
            page.wait_for_load_state("networkidle", timeout=15_000)
            log.info("[lever] Submitted application for '%s' at '%s'", job["title"], job["company"])
        else:
            raise RuntimeError("Submit button not found")
