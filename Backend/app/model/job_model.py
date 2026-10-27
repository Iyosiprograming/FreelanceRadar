import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, UUID, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    # Freelancer.com project ID to prevent duplicate alerts
    external_id: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )

    url: Mapped[str] = mapped_column(
        String(1000), 
        nullable=False
    )

    # 'fixed' or 'hourly'
    project_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )

    budget_min: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    budget_max: Mapped[float | None] = mapped_column(
        Float, 
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(10), 
        default="USD"
    )

    
    # JSON list of skills: ["Python", "FastAPI", "Web Scraping"]
    skills: Mapped[list[str]] = mapped_column(
        JSON, 
        default=list
    )

    # Timestamp when posted on Freelancer.com
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Timestamp when ingested into FreelancerRadar
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )