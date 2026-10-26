from pydantic import BaseModel, EmailStr,ConfigDict
from datetime import datetime
from uuid import UUID
class UserSchema(BaseModel):
    id: UUID
    clerk_id: str
    email: EmailStr
    telegram_id: int | None
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AddUserSchema(BaseModel):
    clerk_id: str
    email: EmailStr
    telegram_id: int | None = None



