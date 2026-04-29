from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models.tracking_event import TrackingEvent
from schemas.common import ApiResponse
from schemas.tracking import TrackEventReq, TrackBatchReq

router = APIRouter()


def _get_user_id(request: Request) -> int | None:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        from core.security import verify_token
        return verify_token(auth[7:])
    except Exception:
        return None


@router.post("/event", response_model=ApiResponse[None])
def track_event(
    req: TrackEventReq,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = _get_user_id(request)
    db.add(TrackingEvent(
        user_id=user_id,
        event_type=req.event_type,
        target_type=req.target_type,
        target_id=req.target_id,
        page_path=req.page_path,
        duration_ms=req.duration_ms,
        extra=req.extra,
    ))
    db.commit()
    return ApiResponse()


@router.post("/batch", response_model=ApiResponse[None])
def track_batch(
    req: TrackBatchReq,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = _get_user_id(request)
    for evt in req.events:
        db.add(TrackingEvent(
            user_id=user_id,
            event_type=evt.event_type,
            target_type=evt.target_type,
            target_id=evt.target_id,
            page_path=evt.page_path,
            duration_ms=evt.duration_ms,
            extra=evt.extra,
        ))
    db.commit()
    return ApiResponse()
