import uuid
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.service.user_service import UserService
from app.service.telegram_service import send_telegram_message

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", summary="Telegram Bot Webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    # Verify secret token if configured
    if settings.TELEGRAM_WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram webhook secret token"
            )

    try:
        body = await request.json()
    except Exception:
        return {"ok": True}

    message = body.get("message")
    if not message:
        return {"ok": True}

    raw_chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()

    if raw_chat_id is None or not text:
        return {"ok": True}

    try:
        chat_id = int(raw_chat_id)
    except (ValueError, TypeError):
        chat_id = raw_chat_id

    # Handle /start
    if text.startswith("/start"):
        user_service = UserService(db)
        existing_user = user_service.get_user_by_telegram_id(chat_id)
        parts = text.split()
        token = parts[1] if len(parts) > 1 else None

        # Case A: This Telegram account is ALREADY linked to a user in the database
        if existing_user:
            # If a token was provided, check if it's their own account or someone else's
            if token:
                try:
                    token_uuid = uuid.UUID(token)
                    if existing_user.id != token_uuid:
                        await send_telegram_message(
                            chat_id=chat_id,
                            text=f"⚠️ This Telegram account is already linked to <b>{existing_user.email}</b>."
                        )
                        return {"ok": True, "status": "already_linked_different_user"}
                except ValueError:
                    pass

            await send_telegram_message(
                chat_id=chat_id,
                text="👋 <b>Welcome back!</b>\n\nYour Telegram is already connected to FreelancerRadar. Your job alerts are active and running."
            )
            return {"ok": True, "status": "already_linked", "user_id": str(existing_user.id)}

        # Case B: This Telegram account is NOT yet linked
        if token:
            try:
                user_id = uuid.UUID(token)
                user = user_service.link_telegram(user_id, chat_id)
                if user:
                    await send_telegram_message(
                        chat_id=chat_id,
                        text="Account linked successfully! You will now receive job alerts here."
                    )
                    return {"ok": True, "status": "linked", "user_id": str(user.id)}
            except ValueError:
                pass
            return {"ok": True}

        # Case C: Not linked and bare /start (no token provided)
        await send_telegram_message(
            chat_id=chat_id,
            text="👋 <b>Welcome to FreelancerRadar!</b>\n\nTo link your account and receive real-time job alerts, please log in to your dashboard and click <b>Connect Telegram</b>."
        )
        return {"ok": True, "status": "unlinked"}

    return {"ok": True}

