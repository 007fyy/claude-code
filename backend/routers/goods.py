from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
import models
import schemas

router = APIRouter()


@router.get("/list", response_model=schemas.GoodsListResp)
def list_goods(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(models.GoodsSpu).filter(models.GoodsSpu.status == 1)
    if category:
        q = q.filter(models.GoodsSpu.category == category)

    total = q.count()
    spus = (
        q.order_by(models.GoodsSpu.sort_weight.desc(), models.GoodsSpu.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for spu in spus:
        active_skus = [s for s in spu.skus if s.status == 1]
        price_min = min((float(s.price) for s in active_skus), default=0)
        price_max = max((float(s.price) for s in active_skus), default=0)
        default_sku = active_skus[0] if active_skus else None

        items.append(
            schemas.SpuListItem(
                spu_id=spu.id,
                name=spu.name,
                category=spu.category,
                material=spu.material or "",
                style_tags=spu.style_tags or [],
                cover_url=spu.cover_url or "",
                price_range=f"{price_min:.0f} - {price_max:.0f}",
                mount_type=spu.mount_type,
                default_sku_id=default_sku.id if default_sku else None,
                ar_available=bool(default_sku and default_sku.ar_asset_url),
                ar_asset_url=default_sku.ar_asset_url if default_sku else None,
            )
        )

    return schemas.GoodsListResp(
        total=total, page=page, page_size=page_size, items=items
    )


@router.get("/{spu_id}", response_model=schemas.SpuDetailResp)
def get_spu(spu_id: int, db: Session = Depends(get_db)):
    spu = db.query(models.GoodsSpu).filter(models.GoodsSpu.id == spu_id).first()
    if not spu:
        raise HTTPException(status_code=404, detail="商品不存在")

    skus = [
        schemas.SkuItem(
            sku_id=s.id,
            sku_name=s.sku_name,
            color=s.color or "",
            size=s.size or "",
            price=float(s.price),
            original_price=float(s.original_price) if s.original_price else None,
            stock=s.stock,
            ar_available=bool(s.ar_asset_url),
            ar_asset_url=s.ar_asset_url,
            ar_offset_x=float(s.ar_offset_x or 0),
            ar_offset_y=float(s.ar_offset_y or 0),
            ar_scale_base=float(s.ar_scale_base or 1),
            ar_rotation_offset=float(s.ar_rotation_offset or 0),
        )
        for s in spu.skus
        if s.status == 1
    ]

    return schemas.SpuDetailResp(
        data=schemas.SpuDetail(
            spu_id=spu.id,
            name=spu.name,
            category=spu.category,
            description=spu.description or "",
            style_tags=spu.style_tags or [],
            occasion_tags=spu.occasion_tags or [],
            material=spu.material or "",
            cover_url=spu.cover_url or "",
            detail_images=spu.detail_images or [],
            target_face_shapes=spu.target_face_shapes or [],
            mount_type=spu.mount_type,
            skus=skus,
        )
    )
