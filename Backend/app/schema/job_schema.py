import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class JobSchema(BaseModel):
    id: uuid.UUID
    external_id: str
    title: str
    description: str | None = None
    url: str
    project_type: Literal["fixed", "hourly"] = "fixed"
    budget_min: float | None = None
    budget_max: float | None = None
    currency: str | None = "USD"
    skills: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddJobSchema(BaseModel):
    external_id: str = Field(..., min_length=1, max_length=100, description="Freelancer.com project ID")
    title: str = Field(..., min_length=1, max_length=500, description="Job title")
    description: str | None = Field(default=None, description="Job description details")
    url: str = Field(..., min_length=1, max_length=1000, description="Link to project on Freelancer.com")
    project_type: Literal["fixed", "hourly"] = Field(default="fixed", description="Project contract type")
    budget_min: float | None = Field(default=None, ge=0, description="Minimum budget or rate")
    budget_max: float | None = Field(default=None, ge=0, description="Maximum budget or rate")
    currency: str | None = Field(default="USD", max_length=10, description="Currency code")
    skills: list[str] = Field(default_factory=list, description="List of required skills/tags")
    published_at: datetime | None = Field(default=None, description="Timestamp when posted on Freelancer.com")

