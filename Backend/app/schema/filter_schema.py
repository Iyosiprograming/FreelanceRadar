import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class FilterSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    skills: list[str]
    project_type: Literal["fixed", "hourly", "any"] = "any"
    min_budget: float | None = None
    min_hourly_rate: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddFilterSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Filter display name")
    skills: list[str] = Field(default_factory=list, description="List of required skills")
    project_type: Literal["fixed", "hourly", "any"] = Field(default="any", description="Project contract type")
    min_budget: float | None = Field(default=None, ge=0, description="Minimum fixed budget threshold")
    min_hourly_rate: float | None = Field(default=None, ge=0, description="Minimum hourly rate threshold")


class UpdateFilterSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255, description="Filter display name")
    skills: list[str] | None = Field(default=None, description="List of required skills")
    project_type: Literal["fixed", "hourly", "any"] | None = Field(default=None, description="Project contract type")
    min_budget: float | None = Field(default=None, ge=0, description="Minimum fixed budget threshold")
    min_hourly_rate: float | None = Field(default=None, ge=0, description="Minimum hourly rate threshold")
