from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.get_current_user import get_current_user_id
from app.schema.filter_schema import AddFilterSchema, FilterSchema, UpdateFilterSchema
from app.service.filter_service import FilterService

router = APIRouter(
    prefix="/filter",
    tags=["filter"],
)


@router.post(
    "/",
    response_model=FilterSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create filter for the current user (1 filter per user)"
)
async def create_user_filter(
    filter_data: AddFilterSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FilterService(db)
    return await service.add_filter(filter_data, user_id)


@router.get(
    "/",
    response_model=FilterSchema,
    summary="Get the current user's filter"
)
def get_user_filter(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FilterService(db)
    user_filter = service.get_filter_by_user_id(user_id)
    if not user_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No filter found for this user."
        )
    return user_filter


@router.patch(
    "/",
    response_model=FilterSchema,
    summary="Update filter properties (one, several, or all)"
)
async def update_user_filter(
    filter_data: UpdateFilterSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FilterService(db)
    return await service.update_filter(filter_data, user_id)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete the current user's filter"
)
async def delete_user_filter(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FilterService(db)
    await service.delete_filter(user_id)
    return None
