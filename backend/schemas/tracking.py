from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Optional


class TrackEventReq(BaseModel):
    event_type: str
    target_type: str
    target_id: Optional[str] = None
    page_path: Optional[str] = None
    duration_ms: Optional[int] = None
    extra: Optional[dict[str, Any]] = None


class TrackBatchReq(BaseModel):
    events: list[TrackEventReq]
