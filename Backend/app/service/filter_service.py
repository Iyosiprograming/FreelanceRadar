import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.logger import logger
from app.model.filter_model import Filter
from app.schema.filter_schema import AddFilterSchema, UpdateFilterSchema


class FilterService:
    def __init__(self, db: Session):
        self.db = db

    def get_filter_by_user_id(self, user_id: uuid.UUID) -> Filter | None:
        """Fetch the single filter belonging to a user."""
        return self.db.scalars(select(Filter).where(Filter.user_id == user_id)).first()

    def add_filter(self, filter_data: AddFilterSchema, user_id: uuid.UUID) -> Filter:
        """Create a new filter for a user. Rejects if user already has one."""
        existing_filter = self.get_filter_by_user_id(user_id)
        if existing_filter:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Filter already exists for this user."
            )

        try:
            new_filter = Filter(
                **filter_data.model_dump(),
                user_id=user_id
            )
            self.db.add(new_filter)
            self.db.commit()
            self.db.refresh(new_filter)
            logger.info(f"Filter created successfully: {new_filter.id} for user: {user_id}")
            return new_filter
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Filter already exists for this user."
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating filter: {e}")
            raise

    def update_filter(self, filter_data: UpdateFilterSchema, user_id: uuid.UUID) -> Filter:
        """Update one or more fields of the existing filter for a user."""
        existing_filter = self.get_filter_by_user_id(user_id)
        if not existing_filter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No filter found for this user."
            )

        # Only extract fields that were explicitly sent in the request
        update_dict = filter_data.model_dump(exclude_unset=True)
        if not update_dict:
            return existing_filter

        try:
            for key, value in update_dict.items():
                setattr(existing_filter, key, value)
            self.db.commit()
            self.db.refresh(existing_filter)
            logger.info(f"Filter updated successfully for user: {user_id} with fields: {list(update_dict.keys())}")
            return existing_filter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating filter: {e}")
            raise

    def delete_filter(self, user_id: uuid.UUID) -> None:
        """Delete the single filter belonging to a user."""
        existing_filter = self.get_filter_by_user_id(user_id)
        if not existing_filter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No filter found for this user."
            )

        try:
            self.db.delete(existing_filter)
            self.db.commit()
            logger.info(f"Filter deleted successfully for user: {user_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting filter: {e}")
            raise
