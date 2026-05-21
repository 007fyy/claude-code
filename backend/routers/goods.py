from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import json, os, uuid

from database import get_db
from core.deps import require_admin
import models
import schemas
from config import BizError
from schemas.goods_admin import CreateSpuReq, UpdateSpuReq, CreateSkuReq, UpdateSkuReq

router = APIRouter()

AR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "ar")
os.makedirs(AR_DIR, exist_ok=True)


@router.get("/admin/list")
def admin_list_goods(db: Session = Depends(get_db), _=Depends(require_admin)):
    spus = db.query(models.GoodsSpu).order_by(
        models.GoodsSpu.sort_weight.desc(), models.GoodsSpu.id.desc()
    ).all()
    data = []
    for spu in spus:
        data.append({
            "spu_id": spu.id,
            "name": spu.name,
            "category": spu.category,
            "cover_url": spu.cover_url or "",
            "mount_type": spu.mount_type,
            "skus": [
                {
                    "sku_id": s.id,
                    "sku_name": s.sku_name,
                    "price": float(s.price),
                    "stock": s.stock,
                    "ar_asset_url": s.ar_asset_url,
                    "ar_offset_x": float(s.ar_offset_x or 0),
                    "ar_offset_y": float(s.ar_offset_y or 0),
                    "ar_scale_base": float(s.ar_scale_base or 1),
                    "ar_rotation_offset": float(s.ar_rotation_offset or 0),
                }
                for s in spu.skus if s.status == 1
            ],
        })
    return {"code": 0, "message": "success", "data": data}


@router.get("/admin/ar-presets")
def get_ar_presets(_=Depends(require_admin)):
    path = os.path.join(AR_DIR, "manifest.json")
    if not os.path.exists(path):
        return {"code": 0, "message": "success", "data": []}
    with open(path, "r", encoding="utf-8") as f:
        return {"code": 0, "message": "success", "data": json.load(f)}


@router.post("/admin/sku/{sku_id}/ar-asset")
async def upload_ar_asset(
    sku_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    if file.content_type not in {"image/png", "image/webp"}:
        raise BizError(4001, "AR素材仅支持 PNG/WebP 格式（需透明背景）")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise BizError(4002, "文件大小不能超过 10MB")
    sku = db.get(models.GoodsSku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU不存在")
    ext = "png" if file.content_type == "image/png" else "webp"
    filename = f"sku_{sku_id}_{uuid.uuid4().hex[:8]}.{ext}"
    with open(os.path.join(AR_DIR, filename), "wb") as f:
        f.write(data)
    sku.ar_asset_url = f"/uploads/ar/{filename}"
    db.commit()
    return {"code": 0, "message": "上传成功", "data": {"ar_asset_url": sku.ar_asset_url}}


@router.put("/admin/sku/{sku_id}/ar-params")
def update_ar_params(
    sku_id: int,
    ar_asset_url: Optional[str] = None,
    ar_offset_x: float = 0,
    ar_offset_y: float = 0,
    ar_scale_base: float = 1.0,
    ar_rotation_offset: float = 0,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sku = db.get(models.GoodsSku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU不存在")
    if ar_asset_url is not None:
        sku.ar_asset_url = ar_asset_url
    sku.ar_offset_x = ar_offset_x
    sku.ar_offset_y = ar_offset_y
    sku.ar_scale_base = ar_scale_base
    sku.ar_rotation_offset = ar_rotation_offset
    db.commit()
    return {"code": 0, "message": "参数已保存", "data": None}


@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    from models.order import Order
    from models.user import User as UserModel
    return {"code": 0, "message": "success", "data": {
        "total_orders":   db.query(Order).count(),
        "pending_ship":   db.query(Order).filter(Order.status == "paid").count(),
        "total_products": db.query(models.GoodsSpu).filter(models.GoodsSpu.status == 1).count(),
        "total_users":    db.query(UserModel).filter(UserModel.role == "user").count(),
    }}


@router.post("/admin/spu")
def create_spu(req: CreateSpuReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    spu = models.GoodsSpu(
        name=req.name, category=req.category, material=req.material,
        description=req.description, mount_type=req.mount_type,
        cover_url=req.cover_url, style_tags=req.style_tags,
        occasion_tags=req.occasion_tags, target_face_shapes=req.target_face_shapes,
        sort_weight=req.sort_weight, status=1,
    )
    db.add(spu)
    db.flush()
    for s in req.skus:
        db.add(models.GoodsSku(
            spu_id=spu.id, sku_name=s.sku_name, price=s.price,
            original_price=s.original_price, stock=s.stock,
            color=s.color, size=s.size, status=1,
        ))
    db.commit()
    return {"code": 0, "message": "商品已创建", "data": {"spu_id": spu.id}}


@router.put("/admin/spu/{spu_id}")
def update_spu(spu_id: int, req: UpdateSpuReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    spu = db.get(models.GoodsSpu, spu_id)
    if not spu:
        raise HTTPException(status_code=404, detail="商品不存在")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(spu, k, v)
    db.commit()
    return {"code": 0, "message": "已更新", "data": None}


@router.patch("/admin/spu/{spu_id}/status")
def toggle_spu_status(spu_id: int, status: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    spu = db.get(models.GoodsSpu, spu_id)
    if not spu:
        raise HTTPException(status_code=404, detail="商品不存在")
    spu.status = status
    db.commit()
    return {"code": 0, "message": "状态已更新", "data": None}


@router.post("/admin/spu/{spu_id}/sku")
def create_sku(spu_id: int, req: CreateSkuReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    if not db.get(models.GoodsSpu, spu_id):
        raise HTTPException(status_code=404, detail="商品不存在")
    sku = models.GoodsSku(
        spu_id=spu_id, sku_name=req.sku_name, price=req.price,
        original_price=req.original_price, stock=req.stock,
        color=req.color, size=req.size, status=1,
    )
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return {"code": 0, "message": "SKU已添加", "data": {"sku_id": sku.id}}


@router.put("/admin/sku/{sku_id}")
def update_sku(sku_id: int, req: UpdateSkuReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    sku = db.get(models.GoodsSku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU不存在")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(sku, k, v)
    db.commit()
    return {"code": 0, "message": "已更新", "data": None}


@router.delete("/admin/sku/{sku_id}")
def delete_sku(sku_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    sku = db.get(models.GoodsSku, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU不存在")
    sku.status = 0
    db.commit()
    return {"code": 0, "message": "已删除", "data": None}


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
