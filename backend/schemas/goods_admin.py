from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class CreateSkuReq(BaseModel):
    sku_name: str
    price: float
    original_price: Optional[float] = None
    stock: int = 0
    color: Optional[str] = None
    size: Optional[str] = None


class UpdateSkuReq(BaseModel):
    sku_name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    stock: Optional[int] = None
    color: Optional[str] = None
    size: Optional[str] = None


class CreateSpuReq(BaseModel):
    name: str
    category: str
    material: Optional[str] = None
    description: Optional[str] = None
    mount_type: str
    cover_url: Optional[str] = None
    style_tags: list[str] = []
    occasion_tags: list[str] = []
    target_face_shapes: list[str] = []
    sort_weight: int = 0
    skus: list[CreateSkuReq] = []


class UpdateSpuReq(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    material: Optional[str] = None
    description: Optional[str] = None
    mount_type: Optional[str] = None
    cover_url: Optional[str] = None
    style_tags: Optional[list[str]] = None
    occasion_tags: Optional[list[str]] = None
    target_face_shapes: Optional[list[str]] = None
    sort_weight: Optional[int] = None
