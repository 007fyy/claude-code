from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class BrowseHistoryReq(BaseModel):
    spu_id: int


class BrowseHistoryItem(BaseModel):
    spu_id: int
    name: str
    cover_url: str = ""
    price_range: str = ""
    category: str = ""
    material: str = ""
    viewed_at: str


class BrowseHistoryGroup(BaseModel):
    date: str
    items: list[BrowseHistoryItem]
