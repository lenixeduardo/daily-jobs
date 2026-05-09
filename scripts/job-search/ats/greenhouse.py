import logging
from pathlib import Path

from .base_filler import BaseFiller

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]


class GreenhouseFiller(BaseFiller):
    ats_name = "greenhouse"

    def _fill(self, page, job: dict, applicant: dict, cover_letter: str, *, dry_run: bool) -> None:
        page.goto(job["url"], wait_until="domcontentloaded")
        self._human_delay()

        # First name
        self._safe_fill(page, [
            "[name='job_application[first_name]']",
            "#first_name",
            "[aria-label='First Name']",
        ], applicant.get("first_name", ""))

        # Last name
        self._safe_fill(page, [
            "[name='job_application[last_name]']",
            "#last_name",
            "[aria-label='Last Name']",
        ], applicant.get("last_name", ""))

        # Email
        self._safe_fill(page, [
            "[name='job_application[email]']",
            "#email",
            "[aria-label='Email']",
        ], applicant.get("email", ""))

        # Phone
        self._safe_fill(page, [
            "[name='job_application[phone]']",
            "#phone",
            "[aria-label='Phone']",
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
                "[name='job_application[cover_letter]']",
                "#cover_letter",
                "textarea[aria-label*='cover']",
                "textarea[aria-label*='Cover']",
            ], cover_letter)

        # LinkedIn URL
        linkedin = applicant.get("linkedin_url", "")
        if linkedin:
            self._safe_fill(page, [
                "[name='job_application[answers_attributes][0][text_value]']",
                "input[aria-label*='LinkedIn']",
                "input[placeholder*='linkedin']",
            ], linkedin)

        if dry_run:
            log.info("[greenhouse] dry_run=True — form filled but NOT submitted for '%s'", job["title"])
            return

        submit = page.locator("input[type='submit'], button[type='submit']").first
        if submit.count() and submit.is_visible():
            submit.click()
            page.wait_for_load_state("networkidle", timeout=15_000)
            log.info("[greenhouse] Submitted application for '%s' at '%s'", job["title"], job["company"])
        else:
            raise RuntimeError("Submit button not found")
