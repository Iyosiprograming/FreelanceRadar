import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, UUID, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    # 1-to-1 relationship: Each user can only have ONE filter
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True,
        nullable=False
    )

    # Label for this filter (e.g., "Python Web Scraping", "FastAPI Projects")
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # List of skills (stored as JSON: ["Python", "FastAPI", "Web Scraping"])
    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )

    # Project type: 'fixed', 'hourly', or 'any'
    project_type: Mapped[str] = mapped_column(
        String(50),
        default="any"
    )

    # Minimum budget thresholds (freelancers filter out low-ball jobs)
    min_budget: Mapped[float | None] = mapped_column(
        Float, 
        nullable=True, 
        default=None
    )
    
    min_hourly_rate: Mapped[float | None] = mapped_column(
        Float, 
        nullable=True, 
        default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )