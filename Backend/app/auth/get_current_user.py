from uuid import UUID
from clerk_backend_api import Clerk
from clerk_backend_api.security import AuthenticateRequestOptions
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.logger import logger
from app.model.user_model import User
from app.service.user_service import UserService

clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db)
) -> UUID:
    """
    Extracts and verifies the user's identity, returning their internal UUID.
    In development mode without an Authorization header, falls back to a local dev user.
    """
    # -----------------------------------------------------------------------
    # 1. DEVELOPMENT BYPASS (For Swagger UI & Local Testing)
    # -----------------------------------------------------------------------
    auth_header = request.headers.get("Authorization")
    
    if settings.MODE == "development" and not auth_header:
        dev_user_id = db.scalar(select(User.id))
        
        if dev_user_id:
            logger.debug(f"[DEV MODE] Bypassing Clerk auth. Using test user ID: {dev_user_id}")
            return dev_user_id
        
        # If no user found in DB, create a temporary dev user
        logger.info("[DEV MODE] No user found in DB. Creating temporary dev user...")
        from app.schema.user_schema import AddUserSchema
        dev_user = UserService(db).create_user(
            AddUserSchema(clerk_id="dev_clerk_123", email="dev@example.com")
        )
        return dev_user.id

    # -----------------------------------------------------------------------
    # 2. PRODUCTION / REAL AUTHENTICATION
    # -----------------------------------------------------------------------
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required."
        )

    options = AuthenticateRequestOptions(
        secret_key=settings.CLERK_SECRET_KEY,
        jwt_key=settings.JWKS_PUBLIC_KEY if settings.JWKS_PUBLIC_KEY else None
    )
    request_state = clerk_client.authenticate_request(request, options)

    if not request_state.is_signed_in:
        error_msg = request_state.message or (str(request_state.reason) if request_state.reason else "Invalid session token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized: {error_msg}"
        )

    if not request_state.payload or not request_state.payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token does not contain a valid user identity."
        )

    clerk_id = request_state.payload.get("sub")
    
    user_id = db.scalar(select(User.id).where(User.clerk_id == clerk_id))

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in local database."
        )

    return user_id


# Alias so both get_current_user and get_current_user_id can be imported
get_current_user = get_current_user_id
