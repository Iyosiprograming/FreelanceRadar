import asyncio
from contextlib import asynccontextmanager
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.logger import logger
from app.core.redis import redis_client

# Import all models so SQLAlchemy Base knows about them before creating tables
from app.model.user_model import User
from app.model.filter_model import Filter
from app.model.job_model import Job

from app.router.clerk_webhook import router as clerk_router
from app.router.filter_router import router as filter_router
from app.router.telegram_router import router as telegram_router
from app.router.user_router import router as user_router
from app.service.redis_service import RedisService
from app.worker.job_radar_worker import start_radar_worker
from app.worker.cleanup_worker import start_cleanup_worker


# ---------------------------------------------------------------------------
# Lifespan: Handles Application Startup & Shutdown cleanly
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in [{settings.MODE}] mode...")
    
    # 1. Create database tables (temporary until Alembic migrations are added)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise e

    # 2. Rebuild Redis cache from database on boot
    try:
        with SessionLocal() as db:
            await RedisService().rebuild_cache_from_db(db)
        logger.info("Redis cache rebuilt successfully from database.")
    except Exception as e:
        logger.warning(f"Could not connect to Redis to rebuild cache: {e}")

    # 3. Start background workers (radar worker every 3m, cleanup worker every 24h)
    radar_task = None
    cleanup_task = None
    if settings.MODE != "testing":
        radar_task = asyncio.create_task(start_radar_worker(interval_seconds=180))
        cleanup_task = asyncio.create_task(start_cleanup_worker(interval_seconds=86400, older_than_hours=24))
        logger.info("Background job radar worker started (running every 3 minutes).")
        logger.info("Daily job cleanup worker started (running every 24 hours).")

    yield

    # --- Shutdown ---
    logger.info("Shutting down application...")
    for task in (radar_task, cleanup_task):
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    try:
        await redis_client.close()
        logger.info("Redis connection closed cleanly.")
    except Exception:
        pass

    engine.dispose()
    logger.info("Database connections closed cleanly.")


# ---------------------------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# ---------------------------------------------------------------------------
# CORS Middleware (Allows your Frontend to communicate with the Backend)
# ---------------------------------------------------------------------------
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
if settings.FRONTEND_URL:
    clean_frontend_url = settings.FRONTEND_URL.strip().rstrip("/")
    if clean_frontend_url and clean_frontend_url not in allowed_origins:
        allowed_origins.append(clean_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------
app.include_router(clerk_router)
app.include_router(filter_router)
app.include_router(telegram_router)
app.include_router(user_router)


# ---------------------------------------------------------------------------
# Root Health Check Endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": settings.MODE
    }


# ---------------------------------------------------------------------------
# Local Dev Server Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=(settings.MODE == "development")
    )
