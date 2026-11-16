from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.logger import logger
from app.core.redis import redis_client
from app.model.job_model import Job
from app.model.filter_model import Filter
from app.model.user_model import User
from app.service.redis_service import RedisService


@dataclass
class MatchResult:
    user_id: UUID
    telegram_id: int | None
    job_id: UUID
    title: str
    url: str
    project_type: str
    budget_text: str
    description_snippet: str
    match_score: int
    matched_skills: list[str]
    published_at: str | None = None


def make_description_snippet(description: str | None, max_length: int = 160) -> str:
    """Cleans and shortens description to a sleek snippet with ellipsis."""
    if not description:
        return "No description provided."
    clean = " ".join(description.split())
    if len(clean) <= max_length:
        return clean
    return clean[:max_length].rsplit(" ", 1)[0] + "..."


CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "AUD": "A$",
    "CAD": "C$",
    "NZD": "NZ$",
    "SGD": "S$",
    "JPY": "¥",
    "CNY": "¥",
    "BRL": "R$",
    "HKD": "HK$",
    "CHF": "CHF ",
    "PHP": "₱",
    "PKR": "₨",
    "BDT": "৳",
    "NGN": "₦",
    "ZAR": "R ",
    "AED": "AED ",
}


def _format_amount(amount: float, symbol: str) -> str:
    """Formats amount cleanly: adds commas (e.g. 12,500), omits .00 if integer."""
    if amount == int(amount):
        formatted_num = f"{int(amount):,}"
    else:
        formatted_num = f"{amount:,.2f}"
    return f"{symbol}{formatted_num}"


def format_budget_display(
    budget_min: float | None,
    budget_max: float | None,
    currency_code: str | None = "USD",
    project_type: str = "fixed"
) -> str:
    """
    Formats the actual budget using the proper currency symbol (e.g. ₹1,500 - ₹12,500 or $50 - $100 / hr)
    without mismatched currency text like '$1500 INR'.
    """
    code = (currency_code or "USD").strip().upper()
    symbol = CURRENCY_SYMBOLS.get(code, f"{code} ")
    rate_suffix = " / hr" if project_type == "hourly" else ""

    if budget_min is not None and budget_max is not None:
        if budget_min == budget_max:
            return f"{_format_amount(budget_min, symbol)}{rate_suffix}"
        return f"{_format_amount(budget_min, symbol)} - {_format_amount(budget_max, symbol)}{rate_suffix}"
    elif budget_max is not None:
        return f"Up to {_format_amount(budget_max, symbol)}{rate_suffix}"
    elif budget_min is not None:
        return f"From {_format_amount(budget_min, symbol)}{rate_suffix}"
    else:
        return "Budget not specified"


class MatchingService:
    def __init__(self, db: Session, redis: RedisService | None = None):
        self.db = db
        self.redis = redis or RedisService(redis_client)

    def grade_job_for_filter(self, job: Job, user_filter: Filter, user: User) -> MatchResult | None:
        """
        Grades whether a job meets a user's filter:
        1. Checks user is active and has telegram_id
        2. Checks project type (fixed vs hourly vs any)
        3. Checks budget (job.budget_max >= filter.min_budget)
        4. Calculates skill match percentage (Must be >= 50%)
        """
        # Rule 1: User must be active with Telegram connected
        if not user.is_active or not user.telegram_id:
            return None

        # Rule 2: Project type match
        if user_filter.project_type != "any" and job.project_type != user_filter.project_type:
            return None

        # Rule 3: Budget match
        job_max_budget = job.budget_max or job.budget_min or 0.0

        if job.project_type == "fixed" and user_filter.min_budget is not None:
            if job_max_budget < user_filter.min_budget:
                return None

        if job.project_type == "hourly" and user_filter.min_hourly_rate is not None:
            if job_max_budget < user_filter.min_hourly_rate:
                return None

        # Rule 4: Skill Match (Must be >= 50%)
        user_skills = {s.strip().lower() for s in (user_filter.skills or []) if s.strip()}
        if not user_skills:
            return None

        job_skills = {s.strip().lower() for s in (job.skills or []) if s.strip()}
        matched_skills = user_skills & job_skills

        # Match percentage = (matched / total user skills) * 100
        score = int((len(matched_skills) / len(user_skills)) * 100)
        if score < 50:
            return None  # Discard if under 50%

        # Format actual budget display with proper symbol and commas
        budget_text = format_budget_display(
            budget_min=job.budget_min,
            budget_max=job.budget_max,
            currency_code=job.currency,
            project_type=job.project_type,
        )

        published_str = None
        if job.published_at:
            if isinstance(job.published_at, datetime):
                published_str = job.published_at.isoformat()
            else:
                published_str = str(job.published_at)

        return MatchResult(
            user_id=user.id,
            telegram_id=user.telegram_id,
            job_id=job.id,
            title=job.title,
            url=job.url,
            project_type=job.project_type,
            budget_text=budget_text,
            description_snippet=make_description_snippet(job.description),
            match_score=score,
            matched_skills=list(matched_skills),
            published_at=published_str,
        )

    async def find_matches_for_job(self, job: Job) -> list[MatchResult]:
        """
        Takes 1 new job and finds all matching users:
        1. Asks Redis for candidates matching job skills (1ms)
        2. Queries database for candidate filters and telegram_ids
        3. Grades them and returns qualified matches
        """
        # 1. Redis quick pre-filter
        candidate_user_ids = await self.redis.get_users_by_keywords(job.skills)
        if not candidate_user_ids:
            return []

        # 2. Fetch candidate filters & users in ONE single SQL query
        candidates = self.db.execute(
            select(Filter, User)
            .join(User, Filter.user_id == User.id)
            .where(
                Filter.user_id.in_([UUID(uid) for uid in candidate_user_ids]),
                User.is_active.is_(True),
                User.telegram_id.isnot(None),
            )
        ).all()

        # 3. Grade each candidate
        matches: list[MatchResult] = []
        for user_filter, user in candidates:
            match = self.grade_job_for_filter(job, user_filter, user)
            if match:
                matches.append(match)

        if matches:
            logger.info(f"Job [{job.external_id}] matched {len(matches)} user(s): '{job.title[:40]}'")
        return matches