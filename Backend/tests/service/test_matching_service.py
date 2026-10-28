import uuid
from unittest.mock import AsyncMock
import pytest

from app.model.user_model import User
from app.model.filter_model import Filter
from app.model.job_model import Job
from app.service.matching_service import MatchingService, make_description_snippet


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning a background loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.get_users_by_keywords = AsyncMock(return_value=set())
    return mock


@pytest.fixture
def matching_service(db_session, mock_redis):
    return MatchingService(db=db_session, redis=mock_redis)


@pytest.fixture
def sample_user(db_session):
    user = User(
        clerk_id="clerk_match_user",
        email="match@example.com",
        telegram_id=123456789,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_filter(db_session, sample_user):
    user_filter = Filter(
        user_id=sample_user.id,
        name="Python Backend",
        skills=["Python", "FastAPI"],
        project_type="fixed",
        min_budget=150.0,
    )
    db_session.add(user_filter)
    db_session.commit()
    db_session.refresh(user_filter)
    return user_filter


def make_job(
    skills: list[str] = None,
    project_type: str = "fixed",
    budget_min: float = 100.0,
    budget_max: float = 300.0,
    title: str = "Build Web Scraper API"
) -> Job:
    return Job(
        id=uuid.uuid4(),
        external_id="fl_test_job_1",
        title=title,
        description="We need an expert to build an API using Python and FastAPI framework.",
        url="https://www.freelancer.com/projects/1",
        project_type=project_type,
        budget_min=budget_min,
        budget_max=budget_max,
        currency="USD",
        skills=skills or ["Python", "FastAPI"],
    )


# ===========================================================================
# 1. Description Snippet Helper Tests
# ===========================================================================

def test_make_description_snippet_short():
    """Verify short descriptions are returned clean without truncation."""
    text = "Short job description."
    assert make_description_snippet(text) == "Short job description."


def test_make_description_snippet_long_truncates_cleanly():
    """Verify long descriptions are truncated at word boundaries with ellipsis."""
    text = "Word " * 50  # 250 characters
    snippet = make_description_snippet(text, max_length=100)
    assert len(snippet) <= 103  # 100 + "..."
    assert snippet.endswith("...")


def test_make_description_snippet_empty_or_none():
    """Verify empty/None descriptions return fallback text."""
    assert make_description_snippet(None) == "No description provided."
    assert make_description_snippet("") == "No description provided."


# ===========================================================================
# 2. Grade Job for Filter Tests (The Core Rules)
# ===========================================================================

def test_grade_100_percent_skill_match_success(matching_service, sample_filter, sample_user):
    """Verify job with 2/2 skills matches with 100% score."""
    job = make_job(skills=["Python", "FastAPI"])

    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)

    assert result is not None
    assert result.match_score == 100
    assert result.telegram_id == sample_user.telegram_id
    assert set(result.matched_skills) == {"python", "fastapi"}


def test_grade_50_percent_skill_match_success(matching_service, sample_filter, sample_user):
    """Verify job with 1/2 skills meets the 50% threshold."""
    job = make_job(skills=["Python", "Django"])  # Only Python matches (1 of 2 = 50%)

    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)

    assert result is not None
    assert result.match_score == 50
    assert result.matched_skills == ["python"]


def test_grade_under_50_percent_skill_match_rejected(matching_service, sample_user, db_session):
    """Verify job with < 50% skill match (e.g. 1/3 = 33%) is rejected."""
    # User filter has 3 skills
    user_filter = Filter(
        user_id=sample_user.id,
        name="Full Stack",
        skills=["Python", "React", "Docker"],
        project_type="any"
    )
    db_session.add(user_filter)
    db_session.commit()

    # Job only has Python (1 out of 3 = 33% < 50%)
    job = make_job(skills=["Python"])

    result = matching_service.grade_job_for_filter(job, user_filter, sample_user)
    assert result is None


def test_grade_project_type_mismatch_rejected(matching_service, sample_filter, sample_user):
    """Verify job with wrong project_type (hourly when user wants fixed) is rejected."""
    job = make_job(project_type="hourly")
    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)
    assert result is None


def test_grade_project_type_any_accepts_both(matching_service, sample_user, db_session):
    """Verify project_type='any' in filter accepts both fixed and hourly jobs."""
    user_filter = Filter(
        user_id=sample_user.id,
        name="Any Type",
        skills=["Python"],
        project_type="any"
    )
    db_session.add(user_filter)
    db_session.commit()

    fixed_job = make_job(project_type="fixed", skills=["Python"])
    hourly_job = make_job(project_type="hourly", skills=["Python"])

    assert matching_service.grade_job_for_filter(fixed_job, user_filter, sample_user) is not None
    assert matching_service.grade_job_for_filter(hourly_job, user_filter, sample_user) is not None


def test_grade_budget_below_min_rejected(matching_service, sample_filter, sample_user):
    """Verify job with max budget below user's min_budget is rejected."""
    # User min_budget is $150; job max is $100
    job = make_job(budget_min=50.0, budget_max=100.0)

    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)
    assert result is None


def test_grade_inactive_user_rejected(matching_service, sample_filter, sample_user, db_session):
    """Verify inactive users are rejected even if job matches filter."""
    sample_user.is_active = False
    db_session.commit()

    job = make_job(skills=["Python", "FastAPI"])
    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)
    assert result is None


def test_grade_missing_telegram_id_rejected(matching_service, sample_filter, sample_user, db_session):
    """Verify users without connected Telegram are rejected."""
    sample_user.telegram_id = None
    db_session.commit()

    job = make_job(skills=["Python", "FastAPI"])
    result = matching_service.grade_job_for_filter(job, sample_filter, sample_user)
    assert result is None


# ===========================================================================
# 3. Find Matches for Job (Integrated Redis + SQL Pipeline)
# ===========================================================================

def test_find_matches_for_job_success(matching_service, mock_redis, sample_filter, sample_user):
    """Verify find_matches_for_job finds candidates via Redis and grades them."""
    job = make_job(skills=["Python", "FastAPI"])

    # Redis returns candidate user ID
    mock_redis.get_users_by_keywords = AsyncMock(return_value={str(sample_user.id)})

    matches = run_sync(matching_service.find_matches_for_job(job))

    assert len(matches) == 1
    assert matches[0].user_id == sample_user.id
    assert matches[0].match_score == 100
    assert matches[0].telegram_id == 123456789


def test_find_matches_for_job_no_candidates_returns_empty(matching_service, mock_redis):
    """Verify find_matches_for_job returns empty list when Redis finds no users."""
    job = make_job(skills=["Ruby", "Rails"])

    # Redis returns empty set
    mock_redis.get_users_by_keywords = AsyncMock(return_value=set())

    matches = run_sync(matching_service.find_matches_for_job(job))
    assert matches == []

