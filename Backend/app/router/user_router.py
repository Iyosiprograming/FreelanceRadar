from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.get_current_user import get_current_user_id
from app.schema.user_schema import UserSchema
from app.service.user_service import UserService

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user profile including Telegram status"
)
@router.get(
    "/me/",
    response_model=UserSchema,
    include_in_schema=False
)
def get_me(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.get_me(user_id)
