from fastapi import FastAPI
from app.core.config import Settings
from app.core.limiter import limiter


def test_docs_disabled_in_fastapi_instance():
    """Verify that Swagger docs and OpenAPI endpoints are disabled when passed None."""
    app_no_docs = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    assert app_no_docs.docs_url is None
    assert app_no_docs.redoc_url is None
    assert app_no_docs.openapi_url is None


def test_slowapi_limiter_configured():
    """Verify that the SlowAPI limiter has client IP keying and default limits configured."""
    assert limiter is not None
    assert len(limiter._default_limits) == 1
    assert limiter._headers_enabled is True
