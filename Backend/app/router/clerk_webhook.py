import json
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError

from app.core.config import settings
from app.core.database import get_db
from app.core.logger import logger
from app.schema.user_schema import AddUserSchema
from app.service.user_service import UserService

router = APIRouter(
    prefix="/clerk",
    tags=["clerk"],
)

@router.post("/webhook")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing svix headers"
        )

    payload = await request.body()
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing payload"
        )

    headers = {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }

    wh = Webhook(settings.WEBHOOK_SECRET)

    # 1. Verify cryptographic Svix signature
    try:
        wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid svix signature"
        )

    # 2. Parse the verified payload
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

    event_type = event.get("type")
    data = event.get("data", {})

    if event_type == "user.created":
        clerk_id = data.get("id")
        if not clerk_id:
            logger.warning("Clerk user ID is missing from webhook data. Skipping.")
            return {"status": "ignored", "detail": "Missing clerk ID"}

        # Extract primary email
        primary_id = data.get("primary_email_address_id")
        email = None
        for item in data.get("email_addresses", []):
            if item.get("id") == primary_id:
                email = item.get("email_address")
                break
        if not email and data.get("email_addresses"):
            email = data["email_addresses"][0].get("email_address")

        if not email:
            logger.warning(f"User {clerk_id} has no email address. Skipping.")
            return {"status": "ignored", "detail": "No email address found"}

        user_service = UserService(db)
        user_input = AddUserSchema(clerk_id=clerk_id, email=email)

        try:
            user = user_service.create_user(user_input)
            logger.info(f"User created from Clerk webhook: {user.id}")
            return {"status": "success", "user_id": str(user.id)}
        except HTTPException as e:
            # Handle duplicate gracefully to prevent Svix from retrying continuously
            if e.status_code == status.HTTP_409_CONFLICT:
                logger.warning(f"User {clerk_id} already exists. Acknowledging webhook.")
                return {"status": "ignored", "detail": "User already exists"}
            raise e

    return {"status": "received", "event": event_type}
