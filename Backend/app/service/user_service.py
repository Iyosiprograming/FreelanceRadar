import uuid
from app.core.logger import logger
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.model.user_model import User
from app.schema.user_schema import AddUserSchema


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.scalars(select(User).where(User.id == user_id)).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.scalars(select(User).where(User.email == email)).first()

    def get_user_by_clerk_id(self, clerk_id: str) -> User | None:
        return self.db.scalars(select(User).where(User.clerk_id == clerk_id)).first()

    def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        return self.db.scalars(select(User).where(User.telegram_id == telegram_id)).first()

    def create_user(self, user_data: AddUserSchema) -> User:
        if self.get_user_by_clerk_id(user_data.clerk_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this clerk_id already exists."
            )

        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )

        try:
            new_user = User(**user_data.model_dump())
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            logger.info("User created successfully")
            return new_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise

    def link_telegram(self, user_id: uuid.UUID, telegram_id: int) -> User | None:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # If user is already linked
        if user.telegram_id is not None:
            return user if user.telegram_id == telegram_id else None

        # If this telegram_id is already used by another account, reject
        if self.get_user_by_telegram_id(telegram_id):
            return None

        user.telegram_id = telegram_id
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"User {user.id} linked to Telegram ID {telegram_id}")
        return user
