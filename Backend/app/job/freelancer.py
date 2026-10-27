from datetime import datetime, timezone
from typing import Any
import httpx
from pydantic import ValidationError

from app.core.logger import logger
from app.schema.job_schema import AddJobSchema

# Official Freelancer.com API v0.1 endpoint for active projects
FREELANCER_ACTIVE_PROJECTS_URL = "https://www.freelancer.com/api/projects/0.1/projects/active/"


def _parse_non_negative_float(val: Any) -> float | None:
    """Safely converts a number or numeric string to a float >= 0, returning None on invalid input."""
    if val is None:
        return None
    try:
        num = float(val)
        return num if num >= 0 else None
    except (ValueError, TypeError):
        return None


def _parse_timestamp(val: Any) -> datetime | None:
    """Safely converts a Unix timestamp (int, float, or numeric string) to UTC datetime."""
    if val is None:
        return None
    try:
        ts = float(val)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, TypeError, OSError):
        return None


def normalize_freelancer_project(raw: dict) -> AddJobSchema | None:
    """
    Normalizes a single project dictionary from the Freelancer.com API
    into our system's validated AddJobSchema.
    """
    try:
        project_id = raw.get("id")
        title = raw.get("title")

        # Skip malformed or empty project records
        if not project_id or not title:
            return None

        # Build clean direct project URL
        seo_url = raw.get("seo_url")
        if seo_url:
            clean_seo = str(seo_url).strip().lstrip("/")
            url = f"https://www.freelancer.com/projects/{clean_seo}"
        else:
            url = f"https://www.freelancer.com/projects/{project_id}"

        # Map project type: 'fixed' or 'hourly'
        raw_type = str(raw.get("type", "fixed")).lower()
        project_type = "hourly" if "hourly" in raw_type else "fixed"

        # Safely parse budget thresholds (handles float, int, or numeric strings)
        budget = raw.get("budget") or {}
        budget_min = _parse_non_negative_float(budget.get("minimum"))
        budget_max = _parse_non_negative_float(budget.get("maximum"))

        # Extract currency (e.g. USD, EUR)
        currency_info = raw.get("currency") or {}
        currency = currency_info.get("code", "USD") if isinstance(currency_info, dict) else "USD"

        # Extract skills list from the 'jobs' array: [{"name": "Python"}, ...]
        skills = [
            skill["name"]
            for skill in raw.get("jobs", [])
            if isinstance(skill, dict) and "name" in skill
        ]

        # Convert Unix timestamp safely
        published_at = _parse_timestamp(raw.get("submitdate"))

        return AddJobSchema(
            external_id=str(project_id),
            title=str(title).strip(),
            description=raw.get("preview_description") or raw.get("description"),
            url=url,
            project_type=project_type,
            budget_min=budget_min,
            budget_max=budget_max,
            currency=currency,
            skills=skills,
            published_at=published_at,
        )

    except (ValidationError, ValueError, TypeError) as e:
        logger.warning(f"Skipping invalid Freelancer project {raw.get('id')}: {e}")
        return None


async def fetch_freelancer_jobs(limit: int = 50) -> list[AddJobSchema]:
    """
    Fetches the latest active projects from Freelancer.com API
    and returns a list of normalized AddJobSchema instances.
    """
    params = {
        "limit": limit,
        "sort_field": "time_updated",
        "reverse_sort": "true",
        "job_details": "true",  # Ensures skill tags are included
    }
    headers = {
        "User-Agent": "FreelancerRadar/1.0",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                FREELANCER_ACTIVE_PROJECTS_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            raw_projects = data.get("result", {}).get("projects", [])
            normalized_jobs: list[AddJobSchema] = []

            for raw in raw_projects:
                job = normalize_freelancer_project(raw)
                if job:
                    normalized_jobs.append(job)

            logger.info(f"Successfully fetched & normalized {len(normalized_jobs)} jobs from Freelancer.com")
            return normalized_jobs

    except httpx.HTTPStatusError as e:
        logger.error(f"Freelancer API returned HTTP {e.response.status_code}")
        return []
    except httpx.RequestError as e:
        logger.error(f"Network error connecting to Freelancer.com: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching Freelancer jobs: {e}")
        return []
