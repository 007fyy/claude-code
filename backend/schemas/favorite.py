from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class FavoriteToggleReq(BaseModel):
    spu_id: int


class FavoriteOut(BaseModel):
    spu_id: int
    is_favorited: bool
    created_at: Optional[str] = None


class FavoriteListItem(BaseModel):
    spu_id: int
    name: str
    cover_url: Optional[str] = ""
    price_range: str = ""
    category: str = ""
    material: Optional[str] = ""
    created_at: Optional[str] = None
