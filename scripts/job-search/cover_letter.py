#!/usr/bin/env python3
import logging
import os

import anthropic

log = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_cover_letter(job: dict, profile: dict, language: str = "en") -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.warning("ANTHROPIC_API_KEY not set, skipping cover letter generation.")
        return ""

    name = profile.get("name", "")
    bio = profile.get("bio", "")
    stack = ", ".join(profile.get("stack", []))
    lang_instruction = "Write in English." if language == "en" else "Escreva em português brasileiro."

    prompt = f"""You are a professional job application writer. Write a concise, personalized cover letter for the following job.

Applicant: {name}
Bio: {bio}
Tech stack: {stack}

Job title: {job['title']}
Company: {job['company']}
Job description (excerpt):
{job['description'][:2000]}

Instructions:
- 3 short paragraphs maximum
- First paragraph: express genuine interest and briefly mention relevant experience
- Second paragraph: highlight 2-3 specific skills from the stack that match the role
- Third paragraph: short closing with availability
- Tone: professional but conversational, not generic
- Do NOT use placeholder text like [Your Name] — use the actual name provided
- {lang_instruction}
- Keep it under 250 words"""

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        log.info("Cover letter generated for '%s' at '%s'", job["title"], job["company"])
        return text
    except Exception as exc:
        log.warning("Cover letter generation failed for '%s': %s", job["title"], exc)
        return ""
